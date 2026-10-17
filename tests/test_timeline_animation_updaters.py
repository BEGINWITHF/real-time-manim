"""Regression test: a manim animation's own updater pass must run every frame.

Report: wiki ``03-动画/更新器动画/01b-更新工具与自动变化`` -- "welcome的write动画不对，
tracepath画出的时直线".  The TracedPath half is what this file pins down.

Root cause (``real_time_manim/timeline.py``): manim's ``Scene.update_to_time``
does three things per frame, in this order::

    for animation in self.animations:
        animation.update_mobjects(dt)   # (1) advances the COPIES begin() took
        animation.interpolate(alpha)    # (2)
    self.update_mobjects(dt)            # (3) the scene's mobject updaters

``Timeline.evaluate`` only ever did (2), and ``render_at`` only ever did (3).
Step (1) is not redundant: ``Animation.get_all_mobjects_to_update()`` is
``get_all_mobjects()`` minus ``self.mobject``, i.e. ``starting_mobject`` /
``target_mobject`` / ``target_copy`` -- and those copies keep the updaters they
were copied with.  The sample drives ``group.animate.shift(RIGHT * 6)`` while
``group`` carries ``add_updater(lambda m: m.rotate(-0.3))`` and a ``TracedPath``
records ``circ.get_start``: without (1) the copies never rotate, ``interpolate``
re-derives ``group`` from that unrotated pair every frame, and the fresh
``rotate(-0.3)`` the scene pass applies is wiped on the next frame.  The traced
point therefore sits at ONE offset forever -- a perfectly straight horizontal
line (measured: y spread 0.0000 for RTM vs 1.3664 for manim's own loop, on a
0.66-unit orbit radius).

The fix adds ``timeline.drive_animation_updaters`` and calls it from
``Timeline.evaluate`` under the SAME forward-only gate ``render_at`` already
uses for ``_drive_mobject_updaters`` -- a seek must not replay a stateful pass.

Pure Python: stub window, no GPU, no images.
"""
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import RIGHT, Circle, Dot, Scene, VGroup  # noqa: E402

from real_time_manim.timeline import Timeline, drive_animation_updaters  # noqa: E402


class _StubWindow:
    """The three calls ``Timeline.render_at`` makes on its window."""

    dll = None

    def sync(self, scene):
        return None

    def tick(self):
        return True

    def request_readback(self):
        return None


def _build_group(suspend):
    """The wiki sample's TracedPath setup, verbatim but window-free."""
    scene = Scene()
    circ = Circle(radius=0.7, color="RED", stroke_width=4)
    dot = Dot(radius=0.08, color="RED").move_to(circ.get_start())
    group = VGroup(circ, dot)
    group.add_updater(lambda m: m.rotate(-0.3))
    scene.add(group)
    builder = group.animate.shift(RIGHT * 6)
    if suspend is False:
        # ``MLWindow.play`` used to force this; it no longer does, because manim
        # leaves the default (True) alone.  Kept as a knob so the test still
        # documents what the override cost.
        builder.anim_args["suspend_mobject_updating"] = False
    return scene, circ, group, builder.build()


def _manim_loop(suspend, frames=120):
    """manim's own frame loop: `Scene.update_to_time`, start to finish."""
    scene, circ, _group, anim = _build_group(suspend)
    scene.animations = [anim]
    anim._setup_scene(scene)
    anim.begin()
    scene.last_t = 0
    pts = []
    for k in range(frames):
        scene.update_to_time(k / 60.0)
        pts.append(np.array(circ.get_start(), dtype=float))
    return np.array(pts)


def _rtm_loop(suspend, frames=120):
    """RTM's frame loop: the Timeline `play()` builds."""
    scene, circ, _group, anim = _build_group(suspend)
    tl = Timeline(_StubWindow(), scene)
    tl.add(anim, 0.0)
    tl.finalize()
    pts = []
    for k in range(frames):
        tl.render_at(k / 60.0)
        pts.append(np.array(circ.get_start(), dtype=float))
    return np.array(pts)


def test_traced_point_accumulates_rotation():
    """The reported bug: a straight horizontal line instead of an orbit."""
    pts = _rtm_loop(suspend=False)
    y_spread = float(pts[:, 1].max() - pts[:, 1].min())
    assert y_spread > 0.5, (
        "the traced point never left one height -- the group's rotate updater "
        "is not accumulating (this is the 'tracepath画出的时直线' report)")


def test_timeline_matches_manims_own_frame_loop():
    """Frame for frame, for the default RTM plays with (suspend=False)."""
    ce = _manim_loop(suspend=False)
    rtm = _rtm_loop(suspend=False)
    assert rtm.shape == ce.shape
    assert np.abs(ce - rtm).max() < 1e-9, (
        "RTM's Timeline and manim's Scene.update_to_time disagree about where "
        "the animated mobject is at some frame")


def test_timeline_matches_manim_when_suspension_is_on():
    """The same with manim's DEFAULT suspension (no ``anim_args`` override)."""
    ce = _manim_loop(suspend=True)
    rtm = _rtm_loop(suspend=True)
    assert np.abs(ce - rtm).max() < 1e-9


def test_animation_updater_pass_only_runs_for_manim_animations():
    """RTM's own classes write their channels themselves -- leave them alone.

    They also expose a ``get_all_mobjects()`` whose entries are the real scene
    mobjects, so driving them here would double-run their updaters against
    ``_drive_mobject_updaters``.
    """
    from manim import Square
    from manim.animation.animation import Animation as ManimAnimation

    from real_time_manim.animations.fade_in import FadeIn

    seen = []

    # RTM class: must be skipped even if it happens to define the method
    ours = FadeIn(Square())
    ours.begin(0.0)
    ours.update_mobjects = lambda dt: seen.append(("rtm", dt))
    drive_animation_updaters(ours, 1 / 60)
    assert seen == []

    # manim class: must be driven with the frame's dt
    theirs = ManimAnimation(Square())
    theirs.begin()
    theirs.update_mobjects = lambda dt: seen.append(("manim", dt))
    drive_animation_updaters(theirs, 1 / 60)
    assert seen == [("manim", 1 / 60)]


def test_a_seek_does_not_run_the_updater_pass():
    """``drive=False`` is what a seek passes: a stateful pass is never replayed.

    Both passes -- manim's per-animation one and ``_drive_mobject_updaters`` --
    are gated by the same forward-only decision in ``render_at``, so counting
    updater calls is the precise check.
    """
    scene, _circ, group, anim = _build_group(suspend=False)
    calls = {"n": 0}
    original = group.updaters[0]

    def spy(m):
        calls["n"] += 1
        return original(m)

    group.updaters[0] = spy          # `Mobject.copy` shares the function object

    tl = Timeline(_StubWindow(), scene)
    tl.add(anim, 0.0)
    tl.finalize()                    # begin() -> the copies carry `spy` too

    for k in range(10):
        tl.render_at(k / 60.0)
    forward = calls["n"]
    assert forward > 0

    tl.render_at(5 / 60.0)           # backwards: must not fire
    assert calls["n"] == forward
    tl.render_at(5 / 60.0)           # the same t twice: must not fire twice
    assert calls["n"] == forward
    tl.render_at(6 / 60.0)           # genuinely forward: must fire again
    assert calls["n"] > forward
