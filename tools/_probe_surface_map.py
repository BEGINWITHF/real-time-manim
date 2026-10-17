# -*- coding: utf-8 -*-
"""ASCII brightness map of a clip's frames (numeric only, never an image).

Renders each frame as a coarse luminance ASCII picture so a layout/geometry
difference can be inspected from the terminal.

    python tools/_probe_surface_map.py A.mp4 [B.mp4] --frames 190 --cols 96
"""
import argparse
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
from tools.wiki_diff import decode  # noqa: E402

RAMP = " .:-=+*#%@"


def pic(img, cols):
    h, w = img.shape[:2]
    rows = max(1, int(cols * h / w / 2.1))
    ys = np.linspace(0, h - 1, rows).astype(int)
    xs = np.linspace(0, w - 1, cols).astype(int)
    lum = img[:, :, :3].max(axis=2).astype(float)
    # gamma-ish stretch so dim surfaces are visible
    block = np.sqrt(np.clip(lum[ys][:, xs] / 255.0, 0, 1))
    idx = np.clip((block * (len(RAMP) - 1)).astype(int), 0, len(RAMP) - 1)
    return ["".join(RAMP[v] for v in row) for row in idx]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b", nargs="?")
    ap.add_argument("--frames", default="190")
    ap.add_argument("--scale", default="480x270")
    ap.add_argument("--cols", type=int, default=96)
    args = ap.parse_args()
    w, h = (int(v) for v in args.scale.lower().split("x"))
    clips = {"A": decode(args.a, (w, h))}
    if args.b:
        clips["B"] = decode(args.b, (w, h))
    want = [int(x) for x in args.frames.split(",") if x.strip()]
    for name, frames in clips.items():
        print("=" * 20, name, args.a if name == "A" else args.b)
        for fi in want:
            i = fi % len(frames)
            print(f"--- {name} frame {i} ---")
            for line in pic(frames[i], args.cols):
                print("  " + line)


if __name__ == "__main__":
    main()
