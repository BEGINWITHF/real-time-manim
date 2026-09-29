"""Regression test: the Timeline path gives manim animations their scene too.

2.0.0 routes `MLWindow.play` through `Timeline`, whose `finalize()` calls
`anim.begin()` for the animations it schedules.  It did not do what manim's
`Scene.play` does first -- hand the animation its scene -- so manim-native
classes that read `animation.scene` (AddTextWordByWord) still failed even after
the legacy loop was fixed.

`finalize()` never touches the window, so a stub window is enough: no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from manim import Create, Square, Text
from manim.animation.creation import AddTextWordByWord

from real_time_manim.timeline import Timeline


class StubWindow:
    """Timeline only needs a window for render_at(); finalize() ignores it."""

    win_w, win_h = 480, 360


class StubScene:
    def __init__(self):
        self.mobjects = []

    def add(self, mob):
        self.mobjects.append(mob)

    def get_mobject_family_members(self):
        return list(self.mobjects)


def _timeline(anim, scene):
    tl = Timeline(StubWindow(), scene)
    tl.add(anim, 0.0)
    tl.finalize()
    return tl


def test_finalize_sets_scene_on_manim_animation():
    scene = StubScene()
    anim = AddTextWordByWord(Text("hi there"))
    _timeline(anim, scene)
    assert getattr(anim, "scene", None) is scene


def test_finalize_registers_introducer_mobject():
    scene = StubScene()
    mob = Square()
    _timeline(Create(mob), scene)
    assert mob in scene.mobjects


def test_finalize_still_begins_and_reports_duration():
    scene = StubScene()
    anim = Create(Square(), run_time=0.5)
    tl = _timeline(anim, scene)
    assert tl.duration == 0.5
    assert anim.scene is scene
