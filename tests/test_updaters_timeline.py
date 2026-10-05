"""Regression test: updaters run on the Timeline path too (2.0.0 seek policy).

2.0.0 routes `MLWindow.play` through `Timeline`, which only evaluated animations
and never drove mobject updaters -- so `mobject.add_updater` / `ValueTracker`
scenes stopped updating (they worked on the legacy tick loop).

Policy under test: updaters accumulate on forward playback (dt = timeline delta)
and re-anchor on a seek (dt = 0), so animation state stays a pure function of t
and random access is not sacrificed.

Pure Python: stub window (sync/tick are no-ops), stub scene, no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import pytest
from manim import Square, ValueTracker

from real_time_manim.timeline import Timeline
from real_time_manim.vulkan_bind import Create, _drive_mobject_updaters


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


def _scene_with(updater):
    """A scene holding one mobject carrying `updater`."""
    scene = StubScene()
    mob = Square()
    mob.add_updater(updater)
    scene.mobjects.append(mob)
    return scene, mob


def test_two_arg_updater_receives_dt():
    seen = []
    scene, _ = _scene_with(lambda m, dt: seen.append(dt))
    _drive_mobject_updaters(scene, 0.05)
    assert seen == [0.05], seen


def test_one_and_zero_arg_updaters_are_called():
    calls = []
    scene = StubScene()
    mob = Square()
    mob.add_updater(lambda m: calls.append("one"))
    scene.mobjects.append(mob)
    scene.mobjects.append(mob)
    _drive_mobject_updaters(scene, 0.1)
    assert calls.count("one") == 2, calls          # two mobject slots -> two calls


def test_suspended_updaters_are_skipped():
    seen = []
    scene, mob = _scene_with(lambda m, dt: seen.append(dt))
    mob.updating_suspended = True
    _drive_mobject_updaters(scene, 0.05)
    assert seen == []


def _prepared_timeline(scene):
    tl = Timeline(StubWindow(), scene)
    tl.add(Create(Square(), run_time=1.0), 0.0)
    tl.finalize()
    return tl


def test_forward_playback_drives_updaters():
    deltas = []
    scene, _ = _scene_with(lambda m, dt: deltas.append(dt))
    tl = _prepared_timeline(scene)
    for t in (0.1, 0.2, 0.3):
        tl.render_at(t)
    # the first frame re-anchors (dt unknown), then every forward step advances
    assert len(deltas) == 2, deltas
    assert deltas == [pytest.approx(0.1)] * 2, deltas


def test_seek_re_anchors_without_accumulating():
    deltas = []
    scene, _ = _scene_with(lambda m, dt: deltas.append(dt))
    tl = _prepared_timeline(scene)
    tl.render_at(0.5)          # first frame        -> re-anchor, no updater run
    tl.render_at(0.6)          # forward            -> dt 0.1
    tl.render_at(0.2)          # BACKWARD seek      -> dt 0.0 (no history replay)
    tl.render_at(0.2)          # same t             -> dt 0.0
    tl.render_at(0.3)          # forward again      -> dt 0.1
    assert deltas == [pytest.approx(0.1)] * 2, deltas


def test_valuetracker_advances_during_playback():
    """The reported case: a ValueTracker driven by an updater."""
    scene = StubScene()
    tracker = ValueTracker(0.0)
    tracker.add_updater(lambda m, dt: m.increment_value(dt))
    scene.mobjects.append(tracker)
    tl = _prepared_timeline(scene)
    for t in (0.1, 0.2, 0.35):
        tl.render_at(t)
    # 0.1 re-anchors; then +0.1 and +0.15 accumulate
    assert tracker.get_value() == pytest.approx(0.25), tracker.get_value()
