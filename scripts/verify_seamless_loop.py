#!/usr/bin/env python3
"""Assert that a rendered clip is a closed loop (first frame == last frame).

Usage:
    python verify_seamless_loop.py out.mp4 [--period 12] [--fps 60]

Checks
  1. frame count == round(period * fps) + 1   (the closure frame IS written)
  2. |frame(0) - frame(N-1)| within codec noise
  3. the wrap step is no larger than an ordinary consecutive-frame step,
     i.e. the repeat does not visibly jump

Exit code 0 only when all three hold. See the parent SKILL.md section
"Seamless loops" for how the scene side is built (run_time = T + 0.5/fps,
state driven from absolute time, snap at t >= T).
"""
import argparse
import subprocess
import sys

import numpy as np

W, H = 480, 270          # comparison resolution; full res is not needed


def count_frames(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
         "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", path],
        capture_output=True, text=True).stdout
    return int(out.strip())


def decode_all(path):
    """Decode the whole clip to (N, H, W) float grey in one pass."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={W}:{H}",
         "-pix_fmt", "gray", "-f", "rawvideo", "-"],
        capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8)
    n = a.size // (W * H)
    if n == 0:
        sys.exit("decode produced no frames: " + path)
    return a[: n * W * H].reshape(n, H, W).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mp4")
    ap.add_argument("--period", type=float, default=12.0, help="loop period in seconds")
    ap.add_argument("--fps", type=float, default=60.0)
    ap.add_argument("--noise", type=float, default=0.35,
                    help="max mean |f0 - fN| accepted as codec noise")
    a = ap.parse_args()

    expected = int(round(a.period * a.fps)) + 1
    n = count_frames(a.mp4)
    frames = decode_all(a.mp4)
    n = min(n, frames.shape[0])

    ok_count = n == expected
    d_wrap = float(np.abs(frames[0] - frames[-1]).mean())
    steps = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))
    ok_close = d_wrap < a.noise
    ok_step = d_wrap <= float(steps.max()) * 1.15

    print(f"frames: {n}  (expected {expected})  -> {'OK' if ok_count else 'MISMATCH'}")
    print(f"ordinary step: mean {steps.mean():.3f}  p50 {np.median(steps):.3f}  max {steps.max():.3f}")
    print(f"wrap step    : {d_wrap:.3f}  -> {'OK' if ok_close and ok_step else 'JUMP'}")
    print("LOOP:", "SEAMLESS" if (ok_count and ok_close and ok_step) else "PROBLEM")
    return 0 if (ok_count and ok_close and ok_step) else 1


if __name__ == "__main__":
    sys.exit(main())
