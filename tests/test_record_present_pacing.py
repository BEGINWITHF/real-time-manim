# -*- coding: utf-8 -*-
"""Present pacing: offline work must never wait for the display.

A record used to run at the refresh rate (an empty scene spent 6.9 ms of its
8.3 ms frame in the present path), so a hidden window -- or one that is
recording -- has to present unpaced, while a window a human is watching keeps
vsync.  The rule lives in `RecordingMixin`; the DLL side is a no-op stand-in
here, so this pins the *decisions*, not the driver.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from real_time_manim.window.recording import RecordingMixin  # noqa: E402


class _Fn:
    """A ctypes-like callable: it records calls and accepts restype/argtypes."""

    def __init__(self, log):
        self._log = log
        self.restype = None
        self.argtypes = None

    def __call__(self, *args):
        self._log.append(int(args[0]) if args else None)


class _FakeDLL:
    def __init__(self):
        self.unpaced = []
        self.visible = []
        self.Vulkan_SetUnpaced = _Fn(self.unpaced)
        self.Vulkan_SetWindowVisible = _Fn(self.visible)


class _Window(RecordingMixin):
    def __init__(self):
        self.dll = _FakeDLL()
        self.hidden = False


def test_a_visible_window_is_paced_and_hiding_it_is_not():
    win = _Window()
    win.set_visible(False)
    assert win.dll.unpaced[-1] == 1          # hidden: nothing to pace for
    win.set_visible(True)
    assert win.dll.unpaced[-1] == 0          # watched: keep vsync
    assert win.dll.visible == [0, 1]


def test_a_dll_without_the_export_is_left_alone():
    class Old(RecordingMixin):
        def __init__(self):
            class NoUnpaced:
                pass
            self.dll = NoUnpaced()
            self.hidden = False

    win = Old()
    win._set_unpaced(True)                   # must not raise
    win._set_unpaced(False)


def test_minguided_state_is_restored_when_a_record_ends():
    win = _Window()
    win._fast_record = True                  # a record is running
    win._fast_record_count_only = True
    win._fast_record_frame_idx = 7
    win.hidden = True                        # hidden window stays unpaced
    win._finish_fast_record()
    assert win.dll.unpaced[-1] == 1
    assert win._fast_record is False
