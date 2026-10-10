"""Red/green test: play() cleanup must call animation.finish(), manim's order.

A fresh render of `PolygonOnAxes` (SHA256-identical to the committed output)
freezes for frames 13..59 while CE keeps animating.  A production-path probe
pinpoints why:

    PROBE per-mobject updater outcome:
      Dot      steps=56  suspended=0   points_changed=42     # runs fine
      Polygon  steps=56  suspended=56  points_changed=0      # never runs

`Polygon` is the `always_redraw` rectangle; it stays `updating_suspended`
forever, so `_drive_mobject_updaters` skips it on every frame.

manim's `Scene.play_internal` finishes each animation before cleaning up:

    for animation in self.animations:
        animation.finish()                  # <- resume_updating() lives here
        animation.clean_up_from_scene(self)

`Animation.clean_up_from_scene` calls `_on_finish`, NOT `finish`, and RTM's
`_run_timeline` only ever calls `clean_up_from_scene` -- so the suspend that
`begin()` applied is never undone.

Also, `finish()` does `interpolate(1)`; `ce_frame_count` uses arange's
exclusive end, so without it the last frame never reaches alpha=1.

Pure Python: stub window (sync/tick/_capture_frame are no-ops), no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import pytest
from manim import Create, Square

from real_time_manim.timeline import Timeline
from real_time_manim.vulkan_bind import MLWindow, _drive_mobject_updaters


class StubWindow:
    """Enough of MLWindow for `_run_timeline` to walk a short play."""

    win_w, win_h = 480, 360
    _fast_record = False          # -> non-record branch: _capture_frame + pacing
    _fast_record_fps = 30

    def sync(self, scene):
        pass

    def tick(self):
        return True

    def request_readback(self):
        pass

    def _capture_frame(self):
        pass


class StubScene:
    def __init__(self):
        self.mobjects = []

    def add(self, mob):
        self.mobjects.append(mob)

    def remove(self, mob):
        if mob in self.mobjects:
            self.mobjects.remove(mob)


def _play_through_rtm(scene, anim, run_time=0.1):
    """Mirror MLWindow.play's Timeline setup, then run RTM's real cleanup path."""
    win = StubWindow()
    win.scene = scene          # _run_timeline does anim.clean_up_from_scene(self.scene)
    tl = Timeline(win, scene)
    tl.add(anim, 0.0)
    tl.finalize()                        # begin() -> suspend_updating()
    MLWindow._run_timeline(win, tl)      # RTM's own loop + cleanup
    return win


def test_create_suspends_updating_at_begin():
    """Baseline: manim's begin() must suspend, or there is nothing to restore."""
    scene = StubScene()
    mob = Square()
    mob.add_updater(lambda m: None)
    scene.mobjects.append(mob)

    tl = Timeline(StubWindow(), scene)
    tl.add(Create(mob, run_time=0.1), 0.0)
    tl.finalize()
    assert mob.updating_suspended is True, "begin() should have suspended it"


def test_run_timeline_resumes_updating_after_cleanup():
    """The regression: after a play finishes, the mobject must accept updaters again."""
    scene = StubScene()
    mob = Square()
    mob.add_updater(lambda m: None)
    scene.mobjects.append(mob)

    _play_through_rtm(scene, Create(mob, run_time=0.1))

    assert mob.updating_suspended is False, (
        "RTM's cleanup left the mobject suspended forever -- manim calls "
        "animation.finish() before clean_up_from_scene(); finish() is where "
        "resume_updating() happens")


def test_updaters_run_after_a_play_has_finished():
    """What the scene-level probe measured: points must actually change again."""
    scene = StubScene()
    mob = Square()
    shifts = []
    mob.add_updater(lambda m: shifts.append(1))
    scene.mobjects.append(mob)

    _play_through_rtm(scene, Create(mob, run_time=0.1))

    shifts.clear()
    _drive_mobject_updaters(scene, 0.1)
    assert shifts, "updater skipped: mobject still suspended after the play"


def test_cleanup_runs_finish_before_clean_up_from_scene():
    """Pins manim's documented order in scene.play_internal:

        for animation in self.animations:
            animation.finish()
            animation.clean_up_from_scene(self)
    """
    scene = StubScene()
    mob = Square()
    scene.mobjects.append(mob)
    anim = Create(mob, run_time=0.1)

    order = []
    real_finish = anim.finish
    real_clean = anim.clean_up_from_scene
    anim.finish = lambda *a, **k: (order.append("finish"),
                                   real_finish(*a, **k))[1]
    anim.clean_up_from_scene = lambda *a, **k: (order.append("clean_up"),
                                                real_clean(*a, **k))[1]

    _play_through_rtm(scene, anim)

    assert order[:2] == ["finish", "clean_up"], (
        "manim calls finish() then clean_up_from_scene(); RTM produced %r" % order)
