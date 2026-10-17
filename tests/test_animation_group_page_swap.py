"""Regression test: a page-swap ``AnimationGroup`` must present EVERY fade-in mobject.

Report: wiki ``03-动画/淡入淡出/01-Fade家族`` "手册「换页组合」" -- the classic
page-swap

    AnimationGroup(FadeOut(old, shift=UP), FadeIn(new1, new2, shift=UP),
                   lag_ratio=0.0)

in RTM's OWN ``AnimationGroup`` faded the old one out but the "换上" half was
missing: only the FIRST fade-in mobject appeared.

manim's ``FadeIn(*mobjects)`` wraps every mobject in one ``VGroup`` as
``self.mobject``.  RTM's ``FadeIn`` instead keeps ``self.mobject = mobjects[0]``
and the rest in ``self.mobjects``.  The group-presentation walk in
``PlayMixin._ensure_animated_present`` matched a ``FadeIn`` sub against the
``(Create, Write, ..., FadeIn, ...)`` branch and appended only ``sub.mobject`` --
i.e. ``new1`` -- dropping ``new2``.  The fix appends every mobject the ``FadeIn``
carries.

Pure Python: stub scene + window, no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import Square, UP

from real_time_manim.animations.animation_group import AnimationGroup
from real_time_manim.animations.fade_in import FadeIn
from real_time_manim.animations.fade_out import FadeOut
from real_time_manim.window.play import PlayMixin


class StubScene:
    def __init__(self):
        self.mobjects = []

    def add(self, mob):
        if mob not in self.mobjects:
            self.mobjects.append(mob)

    def get_mobject_family_members(self):
        members = []
        for root in self.mobjects:
            members.extend(root.get_family())
        return members


class StubWindow:
    def __init__(self, scene):
        self.scene = scene
        self._skip_mob_ids = set()


def _present(anims):
    win = StubWindow(StubScene())
    PlayMixin._ensure_animated_present(win, anims)
    return win.scene


def test_page_swap_presents_both_fade_in_mobjects():
    """The reported case: ``FadeIn(new1, new2)`` in a group shows BOTH."""
    old = Square()
    new1 = Square()
    new2 = Square()
    group = AnimationGroup(
        FadeOut(old, shift=UP),
        FadeIn(new1, new2, shift=UP),
        lag_ratio=0.0,
    )
    scene = _present([group])
    assert new1 in scene.mobjects, "first fade-in mobject missing"
    assert new2 in scene.mobjects, (
        "the second fade-in mobject was dropped -- AnimationGroup presented "
        "only FadeIn.mobject (mobjects[0]) instead of every mobject")


def test_single_fade_in_in_group_still_works():
    """Non-regression: the one-mobject FadeIn keeps being presented."""
    old = Square()
    new = Square()
    group = AnimationGroup(
        FadeOut(old, shift=UP),
        FadeIn(new, shift=UP),
        lag_ratio=0.0,
    )
    scene = _present([group])
    assert new in scene.mobjects


def test_fade_in_begin_parks_every_mobject_at_zero():
    """``FadeIn.begin`` (run at Timeline.finalize) hides ALL its mobjects.

    ``_ensure_animated_present`` only ADDS the mobjects to the scene (at their
    current opacity); the fade-in's starting opacity of 0 comes from
    ``FadeIn.begin``, which the timeline calls before the first frame.  RTM's
    FadeIn iterates ``self.mobjects`` there, so every fade-in target -- not
    just ``mobjects[0]`` -- starts invisible.
    """
    new1 = Square()
    new2 = Square()
    fin = FadeIn(new1, new2)
    fin.begin(0.0)
    from real_time_manim.animations.base import get_anim_opacity
    assert get_anim_opacity(new1) == 0.0
    assert get_anim_opacity(new2) == 0.0
