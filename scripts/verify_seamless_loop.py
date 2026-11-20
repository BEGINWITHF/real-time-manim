#!/usr/bin/env python3
"""Assert that a rendered clip is a closed loop (frame 0 == frame N-1).

This is a VISUAL smoke test on the decoded mp4, not a bit-exact check: the
comparison happens after lossy decode and a 480x270 downscale, so codec noise
is expected.  It catches a wrong frame count and a seam large enough to be
visible (e.g. the missing-outline replay regression on a 3D pose); it does not
prove that two frames are bit-identical, and a subtle seam can pass.

Usage:
    python scripts/verify_seamless_loop.py out.mp4 [--period 12] [--fps 60]

Checks
  1. frame count == round(period * fps) + 1   (the closure frame IS written)
  2. mean |frame(0) - frame(N-1)| within --noise
  3. the wrap step is no larger than an ordinary consecutive-frame step,
     with a small floor so a perfectly static loop (ordinary step 0) still
     passes on codec noise alone.

Exit code 0 only when all three hold.  For the scene-side recipe see
``RTM-Wiki/agent/patterns.md``, section "Seamless loops".
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

import numpy as np

W, H = 480, 270          # comparison resolution; full res is not needed
FRAME_BYTES = W * H


def iter_frames(path):
    """Yield (H, W) uint8 frames from ONE ffmpeg decode pass.

    The clip is streamed, so a long loop costs O(1) memory instead of
    ``frames * 480 * 270 * 4`` bytes.  ffmpeg's stderr is surfaced on failure
    instead of being swallowed by ``capture_output``.
    """
    proc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-i", path, "-an", "-sn",
         "-vf", f"scale={W}:{H}", "-pix_fmt", "gray",
         "-f", "rawvideo", "-"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        while True:
            buf = proc.stdout.read(FRAME_BYTES)
            if len(buf) < FRAME_BYTES:
                break
            yield np.frombuffer(buf, np.uint8).reshape(H, W)
    finally:
        err = proc.stderr.read().decode("utf-8", "replace")
        code = proc.wait()
    if code != 0:
        raise RuntimeError("ffmpeg failed (exit %s): %s" % (code, err.strip()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mp4")
    ap.add_argument("--period", type=float, default=12.0,
                    help="loop period in seconds")
    ap.add_argument("--fps", type=float, default=60.0)
    ap.add_argument("--noise", type=float, default=0.35,
                    help="max mean |f0 - fN| accepted as codec noise")
    a = ap.parse_args()

    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg was not found on PATH")

    expected = int(round(a.period * a.fps)) + 1
    first = prev = None
    steps = []
    n = 0
    try:
        for frame in iter_frames(a.mp4):
            n += 1
            cur = frame.astype(np.int16)
            if first is None:
                first = cur
            elif prev is not None:
                steps.append(float(np.abs(cur - prev).mean()))
            prev = cur
    except RuntimeError as exc:
        sys.exit(str(exc))

    if n == 0:
        sys.exit("no frames decoded: " + a.mp4)
    if n < 2:
        print(f"frames: {n}  (expected {expected})  -> too short")
        print("LOOP: PROBLEM")
        return 1

    # A one-frame clip has no ordinary step; `prev` is the last frame.
    d_wrap = float(np.abs(first - prev).mean())
    max_step = max(steps) if steps else 0.0
    ok_count = n == expected
    ok_close = d_wrap <= a.noise
    # The floor keeps a static loop (ordinary step exactly 0) from failing on
    # codec noise alone while still rejecting a real seam.
    ok_step = d_wrap <= max(max_step, 0.01) * 1.15

    print(f"frames: {n}  (expected {expected})  -> {'OK' if ok_count else 'MISMATCH'}")
    print(f"ordinary step: mean {np.mean(steps):.3f}  p50 {np.median(steps):.3f}  "
          f"max {max_step:.3f}")
    print(f"wrap step    : {d_wrap:.3f}  -> {'OK' if ok_close and ok_step else 'JUMP'}")
    print("LOOP:", "SEAMLESS" if (ok_count and ok_close and ok_step) else "PROBLEM")
    return 0 if (ok_count and ok_close and ok_step) else 1


if __name__ == "__main__":
    sys.exit(main())
