"""P0 regressions: CE paint order and single-window lifecycle.

`tests/` is git-ignored in this repo; this file is a local regression aid.
"""
from types import SimpleNamespace

import pytest

from real_time_manim import Circle, Square, VGroup
from real_time_manim.vulkan_bind import MLWindow
from real_time_manim.window.paint_order import family_index, foreground_mobjects_of


def test_foreground_helper_returns_every_foreground_member():
    a, b = object(), object()
    scene = SimpleNamespace(mobjects=[a], foreground_mobjects=[a, b])
    assert list(foreground_mobjects_of(scene)) == [a, b]


def test_family_index_keeps_last_occurrence():
    first = Square()
    group = VGroup(Circle(), first)
    index = family_index([first, group])
    assert index[id(group)] == 0
    assert index[id(group.submobjects[0])] == 1
    assert index[id(first)] == 2


def test_second_window_is_rejected(monkeypatch):
    class Existing:
        _closed = False

    monkeypatch.setattr(MLWindow, "_registry", [Existing()])
    with pytest.raises(RuntimeError, match="one MLWindow per process"):
        MLWindow(1920, 1080)


def test_close_is_idempotent_and_stops_recording_first(monkeypatch):
    calls = []

    class FakeDLL:
        def Vulkan_Shutdown(self):
            calls.append("shutdown")

    win = object.__new__(MLWindow)
    win._closed = False
    win._defer_close = False
    win._recording = True
    win._fast_record = False
    win.dll = FakeDLL()
    win._unregister = lambda: calls.append("unregister")
    win.stop_record = lambda: calls.append("stop_record")

    win.close()
    win.close()

    assert calls == ["stop_record", "unregister", "shutdown"]
    assert win._closed is True
