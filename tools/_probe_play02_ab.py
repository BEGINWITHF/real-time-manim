"""Probe: A/B check of the controlled variant render (part 2).

variant.mp4 = RTM render of page 02-play与wait参数 with the four
intentionally-different demo strings swapped for the ManimCE ones.

Part 1 found that the variant is 348 frames where the checked-in RTM output
is 480 -- the current workspace renders the explicit `win.play(Wait(...))`
segments shorter.  So the A/B numbers are taken on the time-aligned prefix
(frames both renders share) and on content-matched frozen frames.
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402
from tools.wiki_diff import decode  # noqa: E402

CE = "C:/Users/begin/Desktop/RTM-Wiki/03-动画/通用/assets/ManimCE output/02-play与wait参数-manimce.mp4"
RTM = "C:/Users/begin/Desktop/RTM-Wiki/03-动画/通用/assets/RTM output/02-play与wait参数.mp4"
VAR = "C:/Users/begin/AppData/Local/Temp/opencode/play02_ab/02-play与wait参数.mp4"


def frame(path, idx):
    cmd = ["ffmpeg", "-v", "error", "-i", path,
           "-vf", f"select=eq(n\\,{idx})", "-vsync", "0",
           "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(1080, 1920, 3).copy()


def profile(img, y0, y1):
    return img[y0:y1].astype(np.float64).mean(axis=2).sum(axis=0)


def best_shift(pa, pb, x0, x1, max_lag=14):
    win_a = pa[x0:x1]
    lags = np.arange(-max_lag, max_lag + 1)
    res = np.array([np.abs(win_a - pb[x0 - l:x1 - l]).mean() for l in lags])
    k = int(res.argmin())
    s = float(lags[k])
    if 0 < k < len(lags) - 1:
        y0_, y1_, y2_ = res[k - 1], res[k], res[k + 1]
        den = y0_ - 2 * y1_ + y2_
        if den > 0:
            s += 0.5 * (y0_ - y2_) / den
    r0 = float(np.abs(win_a - pb[x0:x1]).mean())
    return s, r0, float(res[k])


def main():
    a = decode(VAR, (480, 270)).astype(np.int16)
    r = decode(RTM, (480, 270)).astype(np.int16)
    c = decode(CE, (480, 270)).astype(np.int16)

    print("--- per-frame brightness (0.25s) : rtm / var / ce ---")
    n = min(len(a), len(r), len(c))
    for t in np.arange(0, n / 60.0, 0.25):
        i = int(t * 60)
        print(f"  f{i:3d} t={t:4.2f}  rtm {r[i].mean():6.3f}  "
              f"var {a[i].mean():6.3f}  ce {c[i].mean():6.3f}")

    # exact divergence frame of var vs rtm (same source but the 4 strings)
    da = np.abs(a[:min(len(a), len(r))] - r[:min(len(a), len(r))]).mean(axis=(1, 2, 3))
    same = np.nonzero(da < 0.02)[0]
    print(f"\nvar-vs-rtm diff < 0.02 for frames up to {same.max()} "
          f"(then timing diverges)")

    for cut in (180, 200, 215):
        n2 = min(cut, len(a), len(r), len(c))
        dv = np.abs(a[:n2] - c[:n2]).mean()
        dr = np.abs(r[:n2] - c[:n2]).mean()
        print(f"mean|diff| vs CE on frames 0..{n2}:  rtm {dr:.4f}   "
              f"variant {dv:.4f}   -> content difference accounts for "
              f"{dr - dv:.4f}")

    print("\n--- rigid shifts on frozen frames (positive = CE left of other) ---")
    CASES = [
        # (video, frame, y0, y1, x0, x1, label) -- frames where content static
        (VAR, 190, 60, 150, 150, 1150, "var title prefix"),
        (VAR, 190, 60, 150, 1250, 1700, "var title suffix"),
        (VAR, 150, 284, 322, 250, 1750, "var l2 control   "),
        (VAR, 150, 210, 262, 400, 1700, "var l1 tail      "),
        (CE, 190, 60, 150, 150, 1150, "ce  title prefix"),
        (CE, 150, 284, 322, 250, 1750, "ce  l2 control   "),
        (CE, 150, 210, 262, 400, 1700, "ce  l1 tail      "),
    ]
    cache = {}
    for path, idx, y0, y1, x0, x1, label in CASES:
        for p in (path, CE):
            if (p, idx) not in cache:
                cache[(p, idx)] = frame(p, idx)
        pa = profile(cache[(path, idx)], y0, y1)
        pb = profile(cache[(CE, idx)], y0, y1)
        s, r0, rb_ = best_shift(pa, pb, x0, x1)
        print(f"{label} f{idx}: shift {s:+.3f} px   residual no-shift "
              f"{r0:.2f} -> at best {rb_:.2f}")


if __name__ == "__main__":
    main()
