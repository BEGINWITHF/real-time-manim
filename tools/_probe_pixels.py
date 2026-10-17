"""Read pixel values from the first/last frames of a pair -- text only.

    python tools/_probe_pixels.py <rtm.mp4> <ce.mp4> [--frames 0,100,-1]

Prints RGB at a grid of points plus frame-wide mean/min/max, so a suspected
background/global-colour mismatch can be confirmed without ever looking at an
image.
"""
import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.wiki_diff import decode  # noqa: E402


def stats(img):
    f = img.astype("int16")
    return (f.mean(axis=(0, 1)), f.min(), f.max())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rtm")
    ap.add_argument("ce")
    ap.add_argument("--frames", default="0,-1")
    ap.add_argument("--scale", default="480x270")
    args = ap.parse_args()
    w, h = (int(x) for x in args.scale.lower().split("x"))
    a, b = decode(args.rtm, (w, h)), decode(args.ce, (w, h))
    n = min(len(a), len(b))
    print(f"frames rtm={len(a)} ce={len(b)}  compared={n}")

    want = [int(x) for x in args.frames.split(",") if x.strip()]
    pts = [(x, y) for y in (2, h // 4, h // 2, 3 * h // 4, h - 3)
           for x in (2, w // 4, w // 2, 3 * w // 4, w - 3)]
    for wi in want:
        i = wi % n
        sa, sb = stats(a[i]), stats(b[i])
        print(f"\nframe {i}:  rtm mean={sa[0].round(2)} min={sa[1]} max={sa[2]}   "
              f"ce mean={sb[0].round(2)} min={sb[1]} max={sb[2]}")
        print(f"  delta(mean) = {(sa[0] - sb[0]).round(2)}")
        print("      point        rtm            ce          delta")
        for x, y in pts:
            pa, pb = a[i][y, x], b[i][y, x]
            d = pa.astype("int16") - pb.astype("int16")
            print(f"  ({x:3},{y:3})  {tuple(int(v) for v in pa)!s:16} "
                  f"{tuple(int(v) for v in pb)!s:16} {tuple(int(v) for v in d)!s}")

    # per-frame whole-image mean delta: constant offset or content dependent?
    da = a[:n].astype("int16").mean(axis=(1, 2, 3))
    db = b[:n].astype("int16").mean(axis=(1, 2, 3))
    delta = da - db
    print("\nper-frame mean delta: "
          f"min={delta.min():.2f} max={delta.max():.2f} mean={delta.mean():.2f} "
          f"std={delta.std():.2f}")
    step = max(1, n // 12)
    print("  samples: " + ", ".join(f"f{i}:{delta[i]:+.2f}" for i in range(0, n, step)))


if __name__ == "__main__":
    main()
