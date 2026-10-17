"""Regression test: ``win.play`` must validate run_time like manim's Scene.play.

Report: wiki ``01-场景与相机/场景/03-播放与等待`` -- ``win.play(..., run_time=0)``
silently produced nothing where CE raises a clear ``ValueError``.  RTM replaced
``Scene.play`` and never called ``Scene.validate_run_time``, so the friendly
diagnostic was lost.

manim's rule (``Scene.validate_run_time``):

    run_time <= 0                 -> ValueError (cannot render)
    0 < run_time < 1/frame_rate   -> warning + clamp up to one frame

Pure Python: a stub window carrying a real manim ``Scene`` (which owns the
classmethod validator), no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest
from manim import FadeIn, Square, Scene

from real_time_manim.window.play import PlayMixin


class StubWindow:
    """Just enough of MLWindow for ``_validate_play_run_time``."""

    def __init__(self, scene):
        self.scene = scene

    def play(self, *a, **k):   # referenced only for its __name__ in the message
        pass


def _validate(scene, anims):
    return PlayMixin._validate_play_run_time(StubWindow(scene), anims)


def test_zero_run_time_raises():
    """The reported case: run_time=0 must raise CE's ValueError, not vanish."""
    scene = Scene()
    anim = FadeIn(Square(), run_time=0)
    with pytest.raises(ValueError):
        _validate(scene, [anim])


def test_negative_run_time_raises():
    """A non-manim animation (RTM-native / third-party) that does not self-guard.

    manim's ``Animation.run_time`` setter rejects negatives outright, so the
    only way a negative reaches play() is an animation outside manim's base --
    exactly what RTM's own animation classes are.  The validator must still
    raise for them.
    """

    class PlainAnim:
        run_time = -2

    with pytest.raises(ValueError):
        _validate(Scene(), [PlainAnim()])


def test_normal_run_time_passes_silently():
    scene = Scene()
    anim = FadeIn(Square(), run_time=1.5)
    _validate(scene, [anim])   # no raise is the assertion


def test_sub_frame_run_time_does_not_raise():
    """A tiny-but-positive run_time clamps with a warning -- it must not raise."""
    scene = Scene()
    anim = FadeIn(Square(), run_time=0.001)
    _validate(scene, [anim])   # warning + clamp, not an error


def test_aggregate_uses_max_run_time():
    """Like ``Scene.get_run_time``: the max across the play is validated."""
    scene = Scene()
    bad = FadeIn(Square(), run_time=0)      # zero on its own...
    good = FadeIn(Square(), run_time=2.0)   # ...but the play totals 2.0
    _validate(scene, [bad, good])           # max == 2.0 -> no raise


def test_empty_play_is_a_noop():
    _validate(Scene(), [])


def test_stub_scene_without_validator_is_a_noop():
    """A bare scene with no ``validate_run_time`` degrades to a no-op."""

    class Bare:
        pass

    w = StubWindow(Bare())
    PlayMixin._validate_play_run_time(w, [FadeIn(Square(), run_time=0)])
