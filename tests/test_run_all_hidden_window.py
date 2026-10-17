"""Regression test: the batch renderer must build its window HIDDEN, not flash it.

Report: "选择不弹窗保存视频的时候，仍然会弹出一个窗口然后快速消失" -- every scene of a
``run_all.py`` batch run popped a bright window up for a moment and then hid it.

Root cause: ``run_all.py`` patched ``MLWindow.__init__`` to call the REAL init
first (which creates the window VISIBLE, because ``MLWindow._hidden_default`` was
still False) and only THEN call ``enable_fast_record(hidden=True)``.  That
``hidden`` flag merely does ``ShowWindow(SW_HIDE)`` on the already-visible window
-- the hide is always too late, so the window flashes on-screen during
``__init__`` (measured: visible for ~0.2 s / thousands of poll samples per scene).
``fast_record_scene`` and ``FrameServer`` never flash because they set
``MLWindow._hidden_default = True`` BEFORE the scene constructs its window, so it
is born invisible.

The fix sets ``vb.MLWindow._hidden_default = True`` in the generated runner just
before ``scene_lifecycle(...)``.  Test 1 is a pure string check on that generated
code (safe, no DLL).  Test 2 builds a real hidden window and polls the actual
``IsWindowVisible`` to prove it is never shown.
"""
import os
import sys
import threading
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

import run_all


def _runner_source():
    return run_all._runner_script("01", "probe", "SomeScene")


def test_runner_creates_window_hidden_before_scene_lifecycle():
    """The generated runner must set ``_hidden_default = True`` before the scene.

    Ordering matters: the flag has to be True by the time the patched
    ``__init__`` builds the window, which happens inside ``scene_lifecycle``.
    """
    src = _runner_source()
    assert "vb.MLWindow._hidden_default = True" in src, (
        "run_all's runner no longer builds the window hidden -- scenes will pop "
        "a visible window then hide it (the reported flash)")
    assert src.index("_hidden_default = True") < src.index("scene_lifecycle("), (
        "_hidden_default must be set BEFORE scene_lifecycle constructs the window")


def test_hidden_window_is_never_visible():
    """Behavioural proof: a window built with ``_hidden_default=True`` never shows."""
    ctypes = __import__("ctypes")
    user32 = ctypes.windll.user32
    from real_time_manim.window import MLWindow

    prev = MLWindow._hidden_default
    MLWindow._hidden_default = True
    samples = [0]
    stop = False

    def poll():
        while not stop:
            hwnd = user32.FindWindowW(None, "Real Time Manim")
            if hwnd and user32.IsWindowVisible(hwnd):
                samples[0] += 1

    thread = threading.Thread(target=poll, daemon=True)
    thread.start()
    try:
        win = MLWindow(960, 540)   # built hidden via _hidden_default
    except Exception as exc:       # pragma: no cover - no display / no DLL
        stop = True
        thread.join(timeout=1)
        MLWindow._hidden_default = prev
        pytest.skip(f"could not build a window here: {exc}")
    time.sleep(0.1)
    stop = True
    thread.join(timeout=1)
    try:
        win.close()
    except Exception:
        pass
    MLWindow._hidden_default = prev
    assert samples[0] == 0, (
        f"the hidden window became visible {samples[0]} time(s) -- it flashed")
