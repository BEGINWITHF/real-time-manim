"""Probe: sub-pixel horizontal shift of the SHARED text between the RTM and CE
renders of wiki page 02-play与wait参数, measured from the videos themselves at
native 1920x1080.

For a horizontal band containing one text line, the column ink profile
p(x) = sum_y luma(x, y) of the two videos must be identical wherever the two
sources show the SAME characters, up to a rigid x shift (the lines are
centred, and the sources differ by `win.` vs `self`).  We cross-correlate the
profile over the shared x window and refine to sub-pixel accuracy.

Windows are chosen manually per line (the differing part is known from the
two sources).  Control windows (identical text) should read ~0 shift.

Measured result (checked-in wiki artifacts, 1920x1080)
------------------------------------------------------
The four lines whose demo strings differ (`win.` vs `self`) are all
centred, so each carries a RIGID shift of the shared text:

    frame 310  title shared prefix  -3.79 px   (74% of residual explained)
               title shared suffix  +3.88 px   (44%)
               l4 shared tail       +3.83 px   (86%)
    frame 130  title shared prefix  -3.80 px   (76%)
               l1  shared tail      +3.82 px   (83%)
    frame 225  l3  shared tail      +3.81 px   (89%)

And the control -- the one line whose text is IDENTICAL in both sources
(l2, `run_time=1.6, rate_func=linear)   # 逐个 setattr`) -- reads
**-0.001 px**.  So wherever the two sources agree on characters, RTM and CE
place the text at the same x to a thousandth of a pixel; the whole residual
is the centring consequence of the 4 intentional string differences plus a
Cyan-vs-Vulkan rasteriser floor (measured ~0.38 mean|diff|).
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402

RTM = "C:/Users/begin/Desktop/RTM-Wiki/03-动画/通用/assets/RTM output/02-play与wait参数.mp4"
CE = "C:/Users/begin/Desktop/RTM-Wiki/03-动画/通用/assets/ManimCE output/02-play与wait参数-manimce.mp4"


def frame(path, idx):
    """Decode one frame at native resolution as (H, W, 3) uint8."""
    cmd = ["ffmpeg", "-v", "error", "-i", path,
           "-vf", f"select=eq(n\\,{idx})", "-vsync", "0",
           "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(1080, 1920, 3).copy()


def profile(img, y0, y1):
    """Column ink profile of a band, normalised to 0..1 float."""
    p = img[y0:y1].astype(np.float64).mean(axis=2).sum(axis=0)
    return p


def best_shift(pa, pb, x0, x1, max_lag=14):
    """Sub-pixel shift s such that pa(x) ~ pb(x - s) inside [x0, x1).

    Returns (s, residual_without_shift, residual_at_best_s).
    """
    win_a = pa[x0:x1]
    lags = np.arange(-max_lag, max_lag + 1)
    res = []
    for lag in lags:
        win_b = pb[x0 - lag:x1 - lag]
        res.append(np.abs(win_a - win_b).mean())
    res = np.asarray(res)
    k = int(res.argmin())
    s = float(lags[k])
    if 0 < k < len(lags) - 1:            # parabolic refinement
        y0_, y1_, y2_ = res[k - 1], res[k], res[k + 1]
        denom = (y0_ - 2 * y1_ + y2_)
        if denom > 0:
            s += 0.5 * (y0_ - y2_) / denom
    r0 = float(np.abs(win_a - pb[x0:x1]).mean())
    return s, r0, float(res[k])


def main():
    # frozen frame inside Wait(1.2): title + l4 + triangle + txt on screen
    fa = frame(RTM, 310)
    fb = frame(CE, 310)
    print("=== frozen frame 310 (t=5.17s, Wait(1.2)) ===")

    # locate text rows: row ink = mean luma over full width
    ra = fa.mean(axis=(1, 2))
    rb = fb.mean(axis=(1, 2))
    rows = [(i, float(ra[i]), float(rb[i])) for i in range(0, 400)]
    # print a coarse row profile to locate bands
    print("row ink (every 8 rows, first 400):")
    for i in range(0, 400, 8):
        print(f"  y={i:4d}  rtm {ra[i]:6.2f}  ce {rb[i]:6.2f}")

    CASES = [
        # (name, y0, y1, x0, x1, note)
        ("title shared prefix '02-Scene.play / wait (C' ", 60, 150, 150, 1150,
         "left part; same chars in both"),
        ("title shared suffix 'dengjia)'                ", 60, 150, 1250, 1700,
         "right part after the win/self difference"),
        ("l4  shared tail 'play(Wait(1.2)) ... 1.2)'    ", 210, 280, 350, 1700,
         "right >90% of the line, same chars"),
        ("l4  first chars 'win./self'                   ", 210, 280, 180, 420,
         "the differing word itself"),
    ]
    pa, pb = profile(fa, 0, 1080), profile(fb, 0, 1080)
    for name, y0, y1, x0, x1, note in CASES:
        pa = profile(fa, y0, y1)
        pb = profile(fb, y0, y1)
        s, r0, rb_ = best_shift(pa, pb, x0, x1)
        print(f"\n{name}  [{note}]")
        print(f"  band y[{y0}..{y1}] x[{x0}..{x1}]")
        print(f"  best shift of CE relative to RTM: {s:+.3f} px")
        print(f"  residual no-shift {r0:.3f}   residual at best shift {rb_:.3f} "
              f"  ({100*(1-rb_/r0) if r0 else 0:.1f}% of it explained by the shift)")

    # control: frame 130 (t=2.17s): title + l1 + l2 visible; l2 is identical text
    print("\n=== frozen frame 130 (t=2.17s, after Create) ===")
    fa = frame(RTM, 130)
    fb = frame(CE, 130)
    ra = fa.mean(axis=(1, 2))
    for i in range(0, 400, 8):
        print(f"  y={i:4d}  rtm {ra[i]:6.2f}  ce {fb.mean(axis=(1,2))[i]:6.2f}")
    CASES2 = [
        ("title shared prefix                ", 60, 150, 150, 1150),
        ("l2  IDENTICAL control line         ", 284, 322, 250, 1750),
        ("l1  shared tail 'play(Create(sq)...'", 210, 262, 400, 1700),
    ]
    for name, y0, y1, x0, x1 in CASES2:
        pa = profile(fa, y0, y1)
        pb = profile(fb, y0, y1)
        s, r0, rb_ = best_shift(pa, pb, x0, x1)
        print(f"\n{name}")
        print(f"  best shift of CE relative to RTM: {s:+.3f} px "
              f"(positive = CE left of RTM)")
        print(f"  residual no-shift {r0:.3f}   residual at best shift {rb_:.3f}")

    # l3 line during the frozen Wait(0.4) (frame 225, t=3.75s): l3 + dots
    print("\n=== frozen frame 225 (t=3.75s, Wait(0.4) with l3) ===")
    fa = frame(RTM, 225)
    fb = frame(CE, 225)
    CASES3 = [
        ("l3  shared tail 'play(*[FadeIn...'  ", 210, 262, 400, 1700),
        ("title shared prefix                 ", 60, 150, 150, 1150),
    ]
    for name, y0, y1, x0, x1 in CASES3:
        pa = profile(fa, y0, y1)
        pb = profile(fb, y0, y1)
        s, r0, rb_ = best_shift(pa, pb, x0, x1)
        print(f"\n{name}")
        print(f"  best shift of CE relative to RTM: {s:+.3f} px "
              f"(positive = CE left of RTM)")
        print(f"  residual no-shift {r0:.3f}   residual at best shift {rb_:.3f}")


if __name__ == "__main__":
    main()
