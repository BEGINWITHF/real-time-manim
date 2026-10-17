"""Probe: localize the RTM-vs-CE diff of 02-play与wait参数 over time and space.

Usage:
    python tools/_probe_play02.py [--scale 480x270]

Prints (ASCII only):
  1. per-frame mean|diff| timeline at 0.25 s resolution
  2. per-band (horizontal strip) diff energy per scene segment
  3. per-frame ink (sum of luma) of the key text bands for both videos
  4. static-frame glyph bbox / centroid per band (frozen segments)
"""
import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402
from tools.wiki_diff import decode  # noqa: E402

RTM = "C:/Users/begin/Desktop/RTM-Wiki/03-动画/通用/assets/RTM output/02-play与wait参数.mp4"
CE = "C:/Users/begin/Desktop/RTM-Wiki/03-动画/通用/assets/ManimCE output/02-play与wait参数-manimce.mp4"

# scene timeline from the sources (win.play durations, seconds)
SEGMENTS = [
    ("Write(title)          ", 0.00, 0.80),
    ("FadeIn(sig1)          ", 0.80, 1.20),
    ("Create+FadeIn run1.6  ", 1.20, 2.80),
    ("FadeOut(sig1,sq,ci)   ", 2.80, 3.20),
    ("FadeIn(l3)            ", 3.20, 3.60),
    ("dots in + Wait(0.4)   ", 3.60, 4.00),
    ("FadeOut(l3,dots)      ", 4.00, 4.40),
    ("FadeIn(l4,tr,txt)     ", 4.40, 4.80),
    ("Wait(1.2) frozen      ", 4.80, 6.00),
    ("Wait(0.4) frozen      ", 6.00, 6.40),
    ("FadeOut(title,l4..)   ", 6.40, 7.00),
    ("tail                  ", 7.00, 9.00),
]

BANDS = [
    ("title row   y0-40 ", 0, 40),
    ("code rows   y40-70", 40, 70),
    ("mid         y70-200", 70, 200),
    ("low         y200-270", 200, 270),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", default="480x270")
    ap.add_argument("--bands", default="")
    args = ap.parse_args()
    w, h = (int(v) for v in args.scale.lower().split("x"))
    a = decode(RTM, (w, h)).astype(np.int16)
    b = decode(CE, (w, h)).astype(np.int16)
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    print(f"frames rtm/ce trimmed to {n}, scale {w}x{h}")

    d = np.abs(a - b).mean(axis=3)           # (n, h, w) per-pixel mean|diff|
    curve = d.mean(axis=(1, 2))
    print(f"overall mean|diff| = {curve.mean():.4f}   max={curve.max():.4f} "
          f"@f{int(curve.argmax())}")

    fps = 60.0
    print("\n--- timeline: mean|diff| every 0.25 s (per-frame, 60fps) ---")
    print("   t     mean   (bar, 1 char = 0.05)")
    for t in np.arange(0, n / fps, 0.25):
        i0, i1 = int(t * fps), min(int((t + 0.25) * fps), n)
        m = curve[i0:i1].mean()
        print(f"{t:5.2f} {m:7.3f} " + "#" * int(m / 0.05))

    print("\n--- per-segment / per-band mean|diff| ---")
    print("segment                 " + "".join(f"{name[:9]:>10s}" for name, _, _ in BANDS))
    for name, t0, t1 in SEGMENTS:
        i0, i1 = int(t0 * fps), min(int(t1 * fps), n)
        if i0 >= n:
            continue
        row = []
        for _, y0, y1 in BANDS:
            row.append(d[i0:i1, y0:y1].mean())
        print(f"{name} " + "".join(f"{v:10.3f}" for v in row))

    print("\n--- per-band share of the overall mean (whole video) ---")
    tot = 0.0
    for name, y0, y1 in BANDS:
        v = d[:, y0:y1].mean() * (y1 - y0) / h
        tot += v
        print(f"  {name} contribution {v:.4f}")
    print(f"  sum {tot:.4f} (curve mean {curve.mean():.4f})")

    # ink timeline of the two text bands
    la = a.mean(axis=3)
    lb = b.mean(axis=3)
    print("\n--- band ink (sum of luma/255 per pixel) every 0.25 s ---")
    for name, y0, y1 in BANDS[:2]:
        print(f"  {name}")
        for t in np.arange(0, n / fps, 0.5):
            i0, i1 = int(t * fps), min(int((t + 0.5) * fps), n)
            ia = la[i0:i1, y0:y1].mean() / 255
            ib = lb[i0:i1, y0:y1].mean() / 255
            print(f"    t={t:4.1f}  rtm {ia:7.3f}  ce {ib:7.3f}  d {ia-ib:+7.3f}")

    # static-frame geometry of text in a band: bbox + centroid of ink
    print("\n--- frozen-frame glyph geometry per band (frames 300..330 = Wait) ---")
    for name, y0, y1 in BANDS[:2]:
        for tag, vid in (("rtm", a), ("ce ", b)):
            f = vid[300:330].mean(axis=0).mean(axis=2)[y0:y1]
            mask = f > 30
            if not mask.any():
                print(f"  {name} {tag}: no ink")
                continue
            ys, xs = np.nonzero(mask)
            wgt = f[ys, xs].astype(np.float64)
            cx = (xs * wgt).sum() / wgt.sum()
            cy = (np.arange(y0, y1)[ys] * wgt).sum() / wgt.sum()
            print(f"  {name} {tag}: x[{xs.min()}..{xs.max()}] "
                  f"w={xs.max()-xs.min()+1}  centroid_x={cx:7.2f} "
                  f"centroid_y={cy:7.2f}  ink={f.sum()/255:8.1f}")


if __name__ == "__main__":
    main()
