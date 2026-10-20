"""F1 check: many MLWindows in ONE process.

This guards the churn itself: creating and closing windows repeatedly used to
leave the GPU device, the swapchain or a static pool behind, so window N+1
failed where window 1 worked.

The original failure was reported in 1.0.1 -- the 13th window died with
``RuntimeError: Failed to load any font`` -- because ``MLWindow.__init__``
loaded a TrueType blob into native ``draw_text.c``'s font pool
(``MAX_FONTS 12``) for the ``AddText`` bitmap fallback.  That whole path was
dead (nothing ever called ``AddText``), so it has been removed: windows no
longer read a font at all, and that particular failure cannot come back.  What
this script still verifies is that N sequential windows survive.

Usage: python tests/verify_window_churn.py [count]              # dev tree
       venv21/Scripts/python.exe <this file> --installed        # installed package
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if "--installed" not in sys.argv:
    sys.path.insert(0, REPO)      # dev tree; --installed tests whatever is installed
else:
    sys.argv.remove("--installed")

from real_time_manim.vulkan_bind import MLWindow   # noqa: E402

COUNT = int(sys.argv[1]) if len(sys.argv) > 1 else 15
print("RTM from:", __import__("real_time_manim").__file__, flush=True)


def main():
    ok = 0
    import inspect
    supports_hidden = "hidden" in inspect.signature(MLWindow.__init__).parameters
    for i in range(1, COUNT + 1):
        try:
            win = MLWindow(320, 240, **({"hidden": True} if supports_hidden else {}))
            if not supports_hidden:
                # Pre-2.0 builds cannot create a hidden window; ask for the
                # count-only fast-record probe, which hides it after the fact.
                try:
                    win.enable_fast_record("", count_only=True, hidden=True)
                except Exception:
                    pass
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
