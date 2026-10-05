"""Regression test: a frame depends only on ``t``, not on access order.

The whole point of RTM is random access — asking for frame ``t`` must give the
same pixels whether it is the first frame you ask for or the twentieth, whether
you scrub forwards, backwards, or at random.  This test reads the same times in
several orders, twice each, in two separate windows, and requires identical
results.

What it guards (all three were real bugs):
  * the window was drawn *before* the new state was queued, so every read
    returned the previous call's frame;
  * the readback copied a swapchain image the presentation engine already owned,
    which the spec leaves undefined (stale/black pixels, order-dependent);
  * closing one window left a WM_QUIT in the thread queue that killed the next
    window's first tick (first frame of a second window came back black).

Run standalone: python tests/test_frame_access.py
Or with pytest:  pytest tests/test_frame_access.py
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import numpy as np

TIMES = (0.0, 1.0, 3.0, 4.5, 6.0)
ORDERS = (
    TIMES,
    tuple(reversed(TIMES)),
    (3.0, 0.0, 6.0, 1.0, 4.5),
)


def frame_mean(fs, t):
    """Mean brightness of the frame at ``t`` (raw BGR readback, no encoding)."""
    pixels, w, h, row_bytes = fs.grab(t)
    return round(float(np.frombuffer(pixels, dtype=np.uint8).mean()), 4)


def collect(times):
    """Read every t twice inside one window (a fresh window per call)."""
    from real_time_manim.frames import FrameServer
    from scenes.demo_scene import DemoCreate

    fs = FrameServer(DemoCreate)
    try:
        return {t: [frame_mean(fs, t) for _ in range(2)] for t in times}
    finally:
        fs.close()


def main():
    results = []
    for order in ORDERS:
        got = collect(order)
        results.append(got)
        print(f"order {order} -> {got}")

    failures = []
    for t in TIMES:
        values = [r[t][0] for r in results] + [v for r in results for v in r[t]]
        if len(set(values)) != 1:
            failures.append(f"t={t}: frame changed with access order -> {values}")
    if results[0][0.0][0] > 0.05:
        failures.append(f"t=0.0 should be (near) black, got {results[0][0.0][0]}")
    if results[0][6.0][0] < 1.0:
        failures.append(f"t=6.0 should be bright, got {results[0][6.0][0]}")

    if failures:
        print("\nFAIL")
        for f in failures:
            print("  -", f)
        return 1
    print("\nPASS: every t read back the same frame in all orders and both reads")
    return 0


def test_frame_is_order_independent():
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
