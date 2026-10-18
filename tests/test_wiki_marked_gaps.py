# -*- coding: utf-8 -*-
"""Two gaps the wiki marked with ❌/⚠️, now wired.

1. ``Scene.add_subcaption(...)`` -- manim stamps the cue at ``Scene.time`` (a
   clock that never advances under RTM) and appends it to a file writer RTM does
   not drive, so every direct call landed at t=0 and the ``.srt`` did not line
   up with the video.  ``compat`` shims it onto the same store
   ``play(..., subcaption=...)`` uses, stamped at the recorded cursor.

2. ``camera.background_opacity`` -- CE paints the background with that alpha
   over black; RTM handed native the colour alone, so the property changed
   nothing (measured: white at opacity 0.5 still rendered 255 instead of 128).

Pure Python: no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

from manim import Scene

import real_time_manim.compat as compat          # noqa: E402  (installs shims)
from real_time_manim import audio_track          # noqa: E402
from real_time_manim.window.core import CoreMixin  # noqa: E402
from real_time_manim.window import play as play_mod  # noqa: E402


@pytest.fixture(autouse=True)
def clean_store():
    play_mod.clear_subcaptions()
    yield
    play_mod.clear_subcaptions()


# ---------------------------------------------------------------------------
# Scene.add_subcaption
# ---------------------------------------------------------------------------

class _Window:
    """Stands in for an MLWindow: only the cursor and the store matter."""

    def __init__(self, cursor=0.0):
        self._cursor = float(cursor)


def test_the_shim_is_installed():
    assert getattr(Scene.add_subcaption, "_rtm_shimmed", False), (
        "compat must install the add_subcaption shim (apply_manim_shims)")


def test_add_subcaption_stamps_the_cursor_not_zero(monkeypatch):
    scene, window = Scene(), _Window(cursor=0.7)
    monkeypatch.setattr(audio_track, "_scene_window", lambda s: window)

    scene.add_subcaption("hello", duration=0.4)

    entries = play_mod.collect_subcaptions()
    assert len(entries) == 1, entries
    assert entries[0]["content"] == "hello"
    assert entries[0]["start"] == pytest.approx(0.7)    # the cursor, not t=0
    assert entries[0]["duration"] == pytest.approx(0.4)


def test_add_subcaption_honours_offset_and_default_duration(monkeypatch):
    scene, window = Scene(), _Window(cursor=1.0)
    monkeypatch.setattr(audio_track, "_scene_window", lambda s: window)

    scene.add_subcaption("offset", offset=0.25)         # manim's default: 1 s

    entry = play_mod.collect_subcaptions()[0]
    assert entry["start"] == pytest.approx(1.25)
    assert entry["duration"] == pytest.approx(1.0)


def test_add_subcaption_without_a_window_says_so(monkeypatch):
    monkeypatch.setattr(audio_track, "_scene_window", lambda s: None)
    with pytest.raises(RuntimeError, match="needs an MLWindow"):
        Scene().add_subcaption("nowhere")


# ---------------------------------------------------------------------------
# camera.background_opacity
# ---------------------------------------------------------------------------

class _Stub(CoreMixin):
    """Just enough of the window to run `_publish_background_color`."""

    def __init__(self):
        self.published = []

    def _set_background(self, r, g, b):
        self.published.append((r, g, b))


class _Camera:
    def __init__(self, colour, opacity):
        self.background_color = colour
        self.background_opacity = opacity


class _Scene:
    def __init__(self, camera):
        self.camera = camera


def _published(colour, opacity, monkeypatch):
    win = _Stub()
    win._publish_background_color(_Scene(_Camera(colour, opacity)))
    return win.published[-1]


def test_background_opacity_scales_the_clear_colour(monkeypatch):
    from manim import WHITE

    assert _published(WHITE, 1.0, monkeypatch) == pytest.approx((1.0, 1.0, 1.0))
    assert _published(WHITE, 0.5, monkeypatch) == pytest.approx((0.5, 0.5, 0.5))
    assert _published(WHITE, 0.0, monkeypatch) == pytest.approx((0.0, 0.0, 0.0))


def test_background_opacity_is_clamped(monkeypatch):
    from manim import WHITE

    assert _published(WHITE, 2.0, monkeypatch) == pytest.approx((1.0, 1.0, 1.0))
    assert _published(WHITE, -1.0, monkeypatch) == pytest.approx((0.0, 0.0, 0.0))
