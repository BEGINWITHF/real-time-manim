"""Red/green test: does `t.animate.set_value()` actually advance a ValueTracker?

The suite's `PolygonOnAxes` freezes for 47 frames: `rtm_one.py` renders 60
frames whose SHA256 matches the committed `videos_rtm` output byte for byte,
but frames 13..59 never change while CE keeps animating.

    ax = Axes(...)
    t = ValueTracker(5)
    polygon = always_redraw(lambda: Polygon(*(0,0) -> (t, k/t)))
    self.add(ax, graph, dot)
    self.play(Create(polygon))            # frames  0..14
    self.play(t.animate.set_value(10))    # frames 15..29   <-- nothing moves
    self.play(t.animate.set_value(k/10))  # frames 30..44   <-- nothing moves
    self.play(t.animate.set_value(5))     # frames 45..59   <-- nothing moves

`tests/test_updaters_timeline.py` covers the *other* way to move a tracker --
`tracker.add_updater(lambda m, dt: ...)` -- which works.  This file covers the
animation route, `t.animate.set_value()`, which the freeze says does not.

Pure Python: stub window (sync/tick are no-ops), stub scene, no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import pytest
from manim import ValueTracker

from real_time_manim.timeline import Timeline
from real_time_manim.vulkan_bind import _drive_mobject_updaters


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


def _build_anim(tracker, target):
    """`tracker.animate.set_value(target)` -> the Animation `Scene.play` gets."""
    builder = tracker.animate.set_value(target)
    return builder.build() if hasattr(builder, "build") else builder


def test_valuetracker_animate_set_value_reaches_target():
    """After the animation's full run_time, the tracker must hold the target."""
    scene = StubScene()
    tracker = ValueTracker(5.0)
    scene.mobjects.append(tracker)

    tl = Timeline(StubWindow(), scene)
    tl.add(_build_anim(tracker, 10.0), 0.0)
    tl.finalize()

    tl.render_at(1.0)                       # run_time defaults to 1s
    assert tracker.get_value() == pytest.approx(10.0), tracker.get_value()


def test_valuetracker_animate_set_value_interpolates_midway():
    """Half-way through, the tracker must be half-way (it is a pure function of t)."""
    scene = StubScene()
    tracker = ValueTracker(5.0)
    scene.mobjects.append(tracker)

    tl = Timeline(StubWindow(), scene)
    tl.add(_build_anim(tracker, 10.0), 0.0)
    tl.finalize()

    tl.render_at(0.5)
    assert tracker.get_value() == pytest.approx(7.5), tracker.get_value()


def test_later_animation_starts_from_where_its_predecessor_finished():
    """The PolygonOnAxes shape on the FrameServer path.

    `frames.FrameServer` sets `_schedule_mode`, records every play on ONE
    timeline with staggered starts, and `build_timeline()` renders it -- so the
    ValueTracker must read 7.0 half-way through the second play (10 -> 2.5),
    not the initial 5.0 it reads today.
    """
    scene = StubScene()
    tracker = ValueTracker(5.0)
    scene.mobjects.append(tracker)

    tl = Timeline(StubWindow(), scene)
    tl.add(_build_anim(tracker, 10.0), 0.0)   # runs 0.0 .. 1.0, ends at 10
    tl.add(_build_anim(tracker, 2.5), 1.0)    # runs 1.0 .. 2.0, from 10 -> 2.5
    tl.finalize()

    tl.render_at(1.5)                          # half-way through the second play
    assert tracker.get_value() == pytest.approx(6.25), (
        "second play interpolated from the initial state instead of 10: %s"
        % tracker.get_value())


def test_start_at_zero_still_interpolates_correctly():
    """The path MLWindow.play actually uses: everything scheduled at t=0."""
    scene = StubScene()
    tracker = ValueTracker(5.0)
    scene.mobjects.append(tracker)

    tl = Timeline(StubWindow(), scene)
    tl.add(_build_anim(tracker, 10.0), 0.0)
    tl.finalize()

    tl.render_at(0.5)
    assert tracker.get_value() == pytest.approx(7.5), tracker.get_value()
    tl.render_at(1.0)
    assert tracker.get_value() == pytest.approx(10.0), tracker.get_value()


def test_always_redraw_follows_an_animated_valuetracker():
    """The drawn shape must follow t; a frozen tracker freezes the picture."""
    from manim import Polygon, always_redraw

    scene = StubScene()
    tracker = ValueTracker(5.0)

    def rect():
        v = tracker.get_value()
        p = Polygon((0.0, 0.0, 0.0), (v, 0.0, 0.0),
                    (v, v, 0.0), (0.0, v, 0.0))
        return p

    shape = always_redraw(rect)
    scene.mobjects.append(shape)

    tl = Timeline(StubWindow(), scene)
    tl.add(_build_anim(tracker, 10.0), 0.0)
    tl.finalize()

    tl.render_at(0.0)
    w0 = shape.get_width()
    tl.render_at(1.0)
    w1 = shape.get_width()

    assert w1 != w0, "always_redraw never re-ran: width stayed %s" % w0
    assert w1 == pytest.approx(w0 * 2.0, rel=0.05), (w0, w1)
