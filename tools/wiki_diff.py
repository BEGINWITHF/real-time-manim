"""Frame-by-frame A/B comparison of an RTM render against its ManimCE twin.

This is the acceptance harness for the RTM-Wiki issue list.  Every sample in
the wiki exists twice: `assets/RTM output/<name>.mp4` and
`assets/ManimCE output/<name>-manimce.mp4`, rendered from the same source and
frame-aligned (the wiki's own README quotes mean per-frame `blend=difference`
numbers this way).  This tool reproduces that metric and additionally says
*where* the two disagree, so a fix can be checked objectively instead of by
eyeballing.

Usage
-----
    # compare two existing mp4s
    python tools/wiki_diff.py A.mp4 B.mp4 [--out DIR] [--threshold 4.0]

    # work at a smaller decode size (much faster; enough to locate a bug)
    python tools/wiki_diff.py A.mp4 B.mp4 --scale 480x270

Output: the mean absolute per-frame difference, the worst frames listed with
their diff score, and (with --out) side-by-side PNGs of the worst frames plus
a heat map of where they differ.

Pure python + numpy + ffmpeg; no GPU needed.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)


def _tool(name):
    return shutil.which(name) or name


def _dims(path):
    info = json.loads(subprocess.run(
        [_tool("ffprobe"), "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "json", path],
        capture_output=True, text=True, check=True).stdout)
    st = info["streams"][0]
    return int(st["width"]), int(st["height"])


def decode(path, scale=None):
    """Decode the whole video into an (N, H, W, 3) uint8 array.

    `scale` is an (w, h) tuple; ffmpeg resamples on the way out, which makes
    whole-wiki sweeps an order of magnitude cheaper.
    """
    w, h = _dims(path)
    cmd = [_tool("ffmpeg"), "-v", "error", "-i", path]
    if scale:
        w, h = scale
        # Convert to RGB at the NATIVE resolution first, then downscale in RGB
        # space.  Doing it the other way round (`scale=W:H` on the YUV planes)
        # routes yuvj420p -- RTM's encoder tags its output full-range / pc --
        # through swscale's fixed-point rounding, which lifts pure black by
        # ~0.66/255 (measured on 03-动画\创建与擦除\01-Create与画线族-
        # border_fill.mp4 frame 0: RTM mean=0.664 max=2, while the ManimCE
        # twin -- yuv420p, limited range -- stays mean=0.000 max=0).  That
        # constant offset alone accounted for 73-95% of the apparent diff on
        # several issues.txt entries.  `format=rgb24` first decodes each file
        # in its own native color range (full-range yuvj420p -> exact 0,
        # limited-range yuv420p -> exact 0), and a downscale on RGB planes
        # preserves those exact values, so self-comparison of any file is
        # exactly 0.000 and RTM-vs-CE carries no constant bias.
        cmd += ["-vf", f"format=rgb24,scale={w}:{h}"]
    cmd += ["-f", "rawvideo", "-pix_fmt", "rgb24", "-vsync", "0", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    frame_size = w * h * 3
    n = len(raw) // frame_size
    return (np.frombuffer(raw[: n * frame_size], dtype=np.uint8)
            .reshape(n, h, w, 3).copy())


def _ascii(heat, cols=96):
    """Render a HxW float heat map as ASCII so results stay readable in a
    terminal (the whole tool chain is deliberately image-free)."""
    h, w = heat.shape
    rows = max(1, int(cols * h / w / 2.1))
    ys = (np.linspace(0, h - 1, rows)).astype(int)
    xs = (np.linspace(0, w - 1, cols)).astype(int)
    block = heat[ys][:, xs]
    ramp = " .:-=+*#%@"
    peak = float(block.max()) or 1.0
    idx = np.clip((block / peak * (len(ramp) - 1)).astype(int), 0, len(ramp) - 1)
    return "\n".join("".join(ramp[v] for v in row) for row in idx)


def _bbox(mask, shape):
    """Bounding box of a boolean mask in (x0, y0, x1, y1) pixel coords."""
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return None
    h, w = shape
    return (int(xs.min()) * w // 1, int(ys.min()), int(xs.max()), int(ys.max()))


def report(a, b, diff, idx, cols=96, pixel_threshold=24):
    """Text-only diagnosis of one differing frame: where the two disagree,
    how strongly, and a coarse picture of the disagreement."""
    d = np.abs(a[idx].astype(np.int16) - b[idx].astype(np.int16)).mean(axis=2)
    mask = d > pixel_threshold
    print(f"  --- frame {idx}  (mean {diff[idx]:.3f}) ---")
    if not mask.any():
        print("      no pixel differs by > %d" % pixel_threshold)
        return
    ys, xs = np.nonzero(mask)
    print(f"      differing pixels: {mask.sum()} ({100*mask.mean():.2f}%)  "
          f"bbox x[{xs.min()}..{xs.max()}] y[{ys.min()}..{ys.max()}]  "
          f"peak {d.max():.0f}")
    # where is the energy: split the frame into a coarse grid
    gh, gw = 6, 10
    cell = np.zeros((gh, gw))
    for r in range(gh):
        for c in range(gw):
            cell[r, c] = d[r * d.shape[0] // gh:(r + 1) * d.shape[0] // gh,
                          c * d.shape[1] // gw:(c + 1) * d.shape[1] // gw].mean()
    print("      energy grid (rows=top->bottom):")
    for r in range(gh):
        print("        |" + "".join(
            "%5.1f" % cell[r, c] for c in range(gw)) + "|")
    print("      ascii heat:")
    for line in _ascii(d, cols).splitlines():
        print("        " + line)


def compare(rtm_path, ce_path, out=None, threshold=4.0, top=8, scale=None,
            quiet=False, ascii_frames=0, pixel_threshold=24):
    a = decode(rtm_path, scale)
    b = decode(ce_path, scale)
    n = min(len(a), len(b))
    if len(a) != len(b):
        print(f"  !! frame count differs: rtm={len(a)} ce={len(b)} (first {n})")
    a, b = a[:n], b[:n]
    diff = np.abs(a.astype(np.int16) - b.astype(np.int16)).mean(axis=(1, 2, 3))
    overall = float(diff.mean())
    if not quiet:
        order = np.argsort(diff)[::-1][:top]
        print(f"  frames={n}  mean|diff|={overall:.4f}  "
              f"max={float(diff.max()):.4f}@f{int(diff.argmax())}  "
              f"frames>{threshold}: {int((diff > threshold).sum())}")
        print("  worst: " + ", ".join(f"f{int(i)}:{diff[i]:.2f}" for i in order))
        for k in range(min(ascii_frames, len(order))):
            report(a, b, diff, int(order[k]), pixel_threshold=pixel_threshold)

    if out:
        os.makedirs(out, exist_ok=True)
        np.save(os.path.join(out, "curve.npy"), diff)
    return overall, diff


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rtm")
    ap.add_argument("ce")
    ap.add_argument("--out", help="directory for worst-frame PNGs")
    ap.add_argument("--threshold", type=float, default=4.0,
                    help="mean per-frame |diff| above which a frame counts as broken")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--scale", default="", help="WxH decode size, e.g. 480x270")
    ap.add_argument("--ascii", type=int, default=0, dest="ascii_frames",
                    help="print a text diagnosis of the N worst frames")
    ap.add_argument("--pixel-threshold", type=int, default=24)
    args = ap.parse_args()
    scale = None
    if args.scale and "x" in args.scale:
        w, h = args.scale.lower().split("x")
        scale = (int(w), int(h))
    print(f"{os.path.basename(args.rtm)}\n  vs {os.path.basename(args.ce)}")
    compare(args.rtm, args.ce, out=args.out, threshold=args.threshold,
            top=args.top, scale=scale, ascii_frames=args.ascii_frames,
            pixel_threshold=args.pixel_threshold)


if __name__ == "__main__":
    main()
