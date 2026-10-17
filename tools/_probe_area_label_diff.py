# -*- coding: utf-8 -*-
"""Item (c): is the area page's axis-number paint order visible in the pixels?

The batch-C handoff flagged "area 页坐标轴数字的 paint order" as a suspected
difference, without a measurement.  This probe turns it into numbers:

* where the residual RTM-vs-CE diff actually lives, split into "inside the
  coordinate labels' screen boxes" and "outside" (item c is about the labels);
* how much INK each side puts inside each label box -- a paint-order bug would
  show up as RTM lighting fewer pixels there (a label covered by something
  painted later) or more (a label painted over something CE keeps on top).

Numbers only; nothing is ever opened as an image.

    python tools/_probe_area_label_diff.py "<RTM mp4>" "<CE mp4>"
"""
import argparse
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools.wiki_diff import decode  # noqa: E402

SCALE = (480, 270)
FULL = (1920, 1080)


def Axes_stub():
    """The page's own Axes, built without a window (geometry only)."""
    from manim import Axes
    ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 6, 1], x_length=9, y_length=5.5)
    return ax.add_coordinates()


def label_boxes():
    """Screen boxes (480x270 space) of the wiki area page's axis numbers."""
    from manim import DecimalNumber
    from real_time_manim.render.util import manim_to_screen

    ax = Axes_stub()
    boxes = []
    for mob in ax.get_family():
        if not isinstance(mob, DecimalNumber):
            continue
        pts = np.vstack([np.asarray(sub.get_points(), dtype=float).reshape(-1, 3)
                         for sub in mob.get_family()
                         if len(np.asarray(sub.get_points()))])
        xy = np.array([manim_to_screen(p[0], p[1], FULL[0], FULL[1], p[2])
                       for p in pts])
        boxes.append((type(mob).__name__,
                      xy[:, 0].min() * SCALE[0] / FULL[0],
                      xy[:, 0].max() * SCALE[0] / FULL[0],
                      xy[:, 1].min() * SCALE[1] / FULL[1],
                      xy[:, 1].max() * SCALE[1] / FULL[1]))
    return boxes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rtm")
    ap.add_argument("ce")
    ap.add_argument("--frame", type=int, default=221)
    args = ap.parse_args()

    boxes = label_boxes()
    print("coordinate labels: %d boxes" % len(boxes))

    fa = decode(args.rtm, scale=SCALE)
    fb = decode(args.ce, scale=SCALE)
    n = min(len(fa), len(fb))
    h, w = SCALE[1], SCALE[0]

    mask = np.zeros((h, w), dtype=bool)
    for _name, x0, x1, y0, y1 in boxes:
        mask[max(0, int(y0) - 1):int(y1) + 2,
             max(0, int(x0) - 1):int(x1) + 2] = True
    print("mask covers %d of %d pixels (%.2f%% of frame)"
          % (int(mask.sum()), h * w, 100.0 * mask.sum() / (h * w)))

    tot_in, tot_out = 0.0, 0.0
    worst_in = 0.0
    per_frame = []
    for i in range(n):
        d = np.abs(fa[i].astype(int) - fb[i].astype(int)).max(axis=2)
        per_frame.append(d.mean())
        tot_in += float(d[mask].sum())
        tot_out += float(d[~mask].sum())
        worst_in = max(worst_in, float(d[mask].max()))
    print("frames=%d  mean|diff|=%.4f (max %.4f)" % (
        n, float(np.mean(per_frame)), float(np.max(per_frame))))
    print("diff energy inside the label boxes: %.0f of %.0f (%.2f%%)"
          % (tot_in, tot_in + tot_out,
             100.0 * tot_in / max(1.0, tot_in + tot_out)))
    px_in, px_out = float(mask.sum()) * n, float((~mask).sum()) * n
    print("mean |diff| per pixel: inside=%.4f  outside=%.4f  ratio=%.2fx"
          % (tot_in / px_in, tot_out / px_out,
             (tot_in / px_in) / max(1e-9, tot_out / px_out)))
    big = 0
    for i in range(n):
        d = np.abs(fa[i].astype(int) - fb[i].astype(int)).max(axis=2)
        big += int((d[mask] >= 64).sum())
    print("in-box pixels with |diff|>=64: %d of %d (%.3f%%) -- sparse edge"
          " pixels, not whole labels" % (big, px_in, 100.0 * big / px_in))
    print("worst per-pixel diff inside a label box: %.0f/255" % worst_in)

    # ink inside each box on a settled frame: a covered label loses ink
    i = max(0, min(args.frame, n - 1))
    print("ink inside each box at f%d (pixels differing from black):" % i)
    for name, x0, x1, y0, y1 in boxes:
        xi0, xi1 = max(0, int(x0) - 1), int(x1) + 2
        yi0, yi1 = max(0, int(y0) - 1), int(y1) + 2
        ink_a = int((fa[i, yi0:yi1, xi0:xi1].max(axis=2) > 16).sum())
        ink_b = int((fb[i, yi0:yi1, xi0:xi1].max(axis=2) > 16).sum())
        d = np.abs(fa[i, yi0:yi1, xi0:xi1].astype(int)
                   - fb[i, yi0:yi1, xi0:xi1].astype(int)).max()
        print("  %-14s box x[%3d..%3d] y[%3d..%3d]  RTM ink=%4d  CE ink=%4d"
              "  max|d|=%3d" % (name, xi0, xi1, yi0, yi1, ink_a, ink_b, d))


if __name__ == "__main__":
    main()
