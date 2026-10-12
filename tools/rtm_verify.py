"""Shared verification harness for RTM feature work.

Renders a Scene through `fast_record_scene` into a BMP frame directory and
reports simple objective facts about the result: frame count, whether any frame
is non-blank, and whether the frames actually *change* over time (i.e. the
animation did something instead of painting a static final state).

Pure-python + numpy; no GPU assertion of its own -- if the Vulkan window is
unavailable the render raises and the caller decides whether to skip.
"""
import os, sys, shutil, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np

try:
    from PIL import Image
except Exception:                                     # pragma: no cover
    Image = None

from real_time_manim.record import fast_record_scene


def _read_bmp(path):
    if Image is not None:
        return np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)
    # minimal BMP reader (24-bit BI_RGB, bottom-up) -- PIL fallback
    with open(path, "rb") as fh:
        data = fh.read()
    off = int.from_bytes(data[10:14], "little")
    w = int.from_bytes(data[18:22], "little", signed=True)
    h = int.from_bytes(data[22:26], "little", signed=True)
    bpp = int.from_bytes(data[28:30], "little")
    if bpp != 24:
        raise RuntimeError("unsupported BMP bpp=%s" % bpp)
    abs_h = abs(h)
    stride = (w * 3 + 3) & ~3
    out = np.zeros((abs_h, w, 3), dtype=np.int16)
    for y in range(abs_h):
        src = off + y * stride
        row = data[src:src + w * 3]
        for x in range(w):
            b, g, r = row[x * 3], row[x * 3 + 1], row[x * 3 + 2]
            out[abs_h - 1 - y if h > 0 else y, x] = (r, g, b)
    return out


def render_frames(scene_cls, tmp_name, fps=30, duration=1.0, bg=(0, 0, 0)):
    """Render `scene_cls` and return a list of HxWx3 int16 numpy frames."""
    base = os.path.join(REPO, "media", "_verify", tmp_name)
    if os.path.isdir(base):
        shutil.rmtree(base, ignore_errors=True)
    os.makedirs(base, exist_ok=True)
    n = max(2, int(round(duration * fps)))
    fast_record_scene(scene_cls, os.path.join(base, "ignore.mp4"),
                      fps=fps, hidden=True, verbose=False,
                      segment=(0, n), cleanup=False, overwrite=True)
    # BMP frames land in a subdirectory named after the output file.
    files = sorted(glob.glob(os.path.join(base, "**", "*.bmp"), recursive=True))
    if not files:
        raise RuntimeError("no BMP frames produced in %s" % base)
    return [_read_bmp(f) for f in files]


def analyse(frames, bg=None, blank_tol=2.0, change_tol=8.0):
    """Return a dict of objective facts about a rendered frame sequence.

    ``static`` is decided on the *max* per-pixel diff between consecutive frames
    (a hard threshold near zero), which is robust to a small shape moving across
    a mostly-black frame -- a mean-over-all-pixels metric would wash out to ~0.1
    and misreport a live animation as static.
    """
    arr = np.stack(frames)
    n = arr.shape[0]
    flat = arr.reshape(n, -1, 3)
    per_frame_std = flat.std(axis=(1, 2))
    nonblank = int((per_frame_std > blank_tol).sum())
    diffs = np.abs(np.diff(arr.astype(np.int32), axis=0))
    per_step_mean = diffs.mean(axis=(1, 2, 3))
    per_step_max = diffs.max(axis=(1, 2, 3))
    changing = int((per_step_max > change_tol).sum())
    return {
        "frames": n,
        "size": (int(arr.shape[1]), int(arr.shape[2])),
        "nonblank_frames": nonblank,
        "max_frame_diff": float(per_step_max.max()) if n > 1 else 0.0,
        "mean_frame_diff": float(per_step_mean.max()) if n > 1 else 0.0,
        "changing_steps": changing,
        "all_blank": nonblank == 0,
        "static": n > 1 and changing == 0,
    }


def verify(scene_cls, name, duration=1.0, fps=60):
    """Render + analyse + print one-line JSON-ish verdict."""
    import json
    try:
        frames = render_frames(scene_cls, name, fps=fps, duration=duration)
    except Exception as e:
        return {"name": name, "render": "FAILED", "error": "%s: %s" % (type(e).__name__, e)}
    info = analyse(frames)
    info["name"] = name
    info["render"] = "OK"
    print(json.dumps(info, ensure_ascii=False))
    return info


def window_available():
    """True if a hidden Vulkan window can be created on this machine."""
    try:
        from real_time_manim.vulkan_bind import MLWindow
        w = MLWindow(320, 180, hidden=True)
        try:
            w.close()
        except Exception:
            pass
        return True
    except Exception:
        return False
