"""Regression test: a closed MLWindow leaves the class registry.

MLWindow hands its class registry to FrameServer (which looks up the window a
scene created for itself), but nothing ever removed an entry, so a process that
opens many windows -- a batch run, a test harness -- kept every window object
alive.  The F1 churn check (tests/verify_window_churn.py) opens 15.

Pure Python: MLWindow.__new__ skips __init__, so no DLL and no GPU are needed.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from real_time_manim.vulkan_bind import MLWindow


def _bare_window():
    """An MLWindow instance without running __init__ (no DLL, no window)."""
    return MLWindow.__new__(MLWindow)


def test_unregister_removes_the_window():
    win = _bare_window()
    MLWindow._registry.append(win)
    assert win in MLWindow._registry
    win._unregister()
    assert win not in MLWindow._registry


def test_unregister_is_idempotent():
    win = _bare_window()
    win._unregister()          # never registered: must not raise
    MLWindow._registry.append(win)
    win._unregister()
    win._unregister()
    assert win not in MLWindow._registry


def test_many_windows_do_not_accumulate():
    before = len(MLWindow._registry)
    for _ in range(15):
        win = _bare_window()
        MLWindow._registry.append(win)
        win._unregister()
    assert len(MLWindow._registry) == before
