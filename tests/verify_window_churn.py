"""F1 check: many MLWindows in ONE process.

Reported in 1.0.1: the 13th window always died with
    RuntimeError: Failed to load any font   (vulkan_bind.py:709)
which matches native/draw/draw_text.c's font pool:

    #define MAX_FONTS 12
    static unsigned char font_data[MAX_FONTS][1 << 25];   // 12 x 32 MiB
    ...
    if (font_count >= MAX_FONTS) return 0;

If a build loads the same font blob once per window, window 13 exhausts the pool
and every font load fails.  The dev tree dedupes identical blobs, so it should
survive -- this script says which one you are running.

Usage: python tests/verify_window_churn.py [count]     (default 15)
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from real_time_manim.vulkan_bind import MLWindow

COUNT = int(sys.argv[1]) if len(sys.argv) > 1 else 15


def main():
    ok = 0
    for i in range(1, COUNT + 1):
        try:
            win = MLWindow(320, 240, hidden=True)
            win._defer_close = False
            win.close()
            ok += 1
        except Exception as e:
            print(f"WINDOW {i:2d}: FAIL {type(e).__name__}: {str(e)[:90]}")
            print(f"\nFAIL: {ok}/{COUNT} windows created; window {i} failed")
            return 1
        print(f"WINDOW {i:2d}: OK")
    print(f"\nPASS: {ok}/{COUNT} sequential windows in one process")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
