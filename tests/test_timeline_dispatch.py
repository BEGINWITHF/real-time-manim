"""Phase 1.1 regression: the timeline must dispatch by *type*, not module name.

`_is_manim_animation` matched on `type(anim).__module__.startswith("manim")`, so a
user's own subclass (`class MyFade(FadeIn)`, defined in their module) was treated
as an RTM animation and got the RTM `begin(t)` signature:
"TypeError: X.begin() takes 1 positional argument but 2 were given" -- four demo
scenes crashed on this.

Pure Python: stub window/scene, no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from manim import Animation, Square

from real_time_manim.animations.create import Create as RtmCreate
from real_time_manim.timeline import Timeline, _is_manim_animation


class StubWindow:
    win_w, win_h = 480, 360

    def sync(self, scene):
        pass

    def tick(self):
        return True

    def request_readback(self):
        pass


class StubScene:
    def __init__(self):
        self.mobjects = []

    def add(self, mob):
        self.mobjects.append(mob)

    def get_mobject_family_members(self):
        return list(self.mobjects)


class Local(Animation):
    """A user-side animation: manim's class, defined in *this* module."""

    def begin(self):
        super().begin()

    def interpolate(self, alpha):
        pass


def test_user_subclass_counts_as_a_manim_animation():
    assert _is_manim_animation(Local(Square())) is True


def test_rtm_own_animation_does_not_count_as_manim():
    assert _is_manim_animation(RtmCreate(Square())) is False


def test_finalize_dispatches_user_subclass_without_typeerror():
    scene = StubScene()
    mob = Square()
    scene.mobjects.append(mob)
    tl = Timeline(StubWindow(), scene)
    tl.add(Local(mob, run_time=0.5), 0.0)
    tl.finalize()                      # used to raise the begin() signature TypeError
    assert tl.duration == 0.5
    assert getattr(tl._entries[0]["anim"], "scene", None) is scene


def test_finalize_still_uses_the_rtm_signature_for_rtm_animations():
    scene = StubScene()
    mob = Square()
    scene.mobjects.append(mob)
    tl = Timeline(StubWindow(), scene)
    tl.add(RtmCreate(mob, run_time=0.25), 0.0)
    tl.finalize()
    assert tl.duration == 0.25
