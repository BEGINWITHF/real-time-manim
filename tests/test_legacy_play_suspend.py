# -*- coding: utf-8 -*-
"""``_play_legacy`` must suspend the animated mobject's own updaters (CE rule).

Item (d) of the batch-C render handoff: "_play_legacy() 的 suspend 语义未同步".

Root cause
----------
``manim.Animation.begin()`` calls ``mobject.suspend_updating()`` whenever the
animation's own ``suspend_mobject_updating`` flag is True -- its default -- so
during a ``Scene.play`` the animated mobject's updaters do NOT run and only the
copies ``begin()`` took are advanced (``animation.py:197-214``); ``finish()``
resumes them (``animation.py:216-227``).

``_play_legacy`` used to FORCE ``anim_args['suspend_mobject_updating'] = False``
on every ``.animate`` builder it resolved, so ``begin()`` never suspended the
mobject and the legacy frame loop -- which drives scene updaters through
``_drive_mobject_updaters`` -- kept running the animated mobject's own updater
ON TOP of the animation: the animation rendered one frame AHEAD of CE (the same
measurement ``play()``'s comment quotes: RTM[k] == CE[k+1], max |Δ| 0.198 scene
units on the wiki TracedPath sample, |Δ| == 0 once the default is kept).

Fix
---
The builder is now built exactly as ``play()`` builds it -- no override -- so
``begin()`` suspends and ``finish()`` resumes.  Nothing else changes: the
legacy loop already honours ``updating_suspended`` inside
``_run_mobject_updaters`` (``window/scene.py``).  One companion fix in the same
block: the legacy loop's one-shot "run the target copy's updaters" pass called
``updater(target)`` for every arity, which raised ``TypeError`` for the common
two-argument form; it now uses ``_run_mobject_updaters``'s own 0/1/2-argument
rule.

Run with::

    python -X utf8 -m pytest tests/test_legacy_play_suspend.py -q
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest  # noqa: E402
from manim import RIGHT, Square  # noqa: E402

from real_time_manim.animations import AnimationGroup  # noqa: E402
from real_time_manim.window.play import PlayMixin  # noqa: E402


class StubScene(object):
    """Only what ``_play_legacy`` / ``_ensure_animated_present`` read."""

    def __init__(self, *mobjects):
        self.mobjects = list(mobjects)
        self.foreground_mobjects = []
        self.updaters = []

    def add(self, *mobjects):
        for mob in mobjects:
            if mob not in self.mobjects:
                self.mobjects.append(mob)

    def get_mobject_family_members(self):
        out = []
        for mob in self.mobjects:
            out.extend(mob.get_family())
        return out


class _LegacyHost(PlayMixin):
    """``PlayMixin`` with the fast-record, count-only frame loop.

    Count-only skips ``sync``/``tick`` entirely, so no DLL and no GPU are
    needed; the loop still runs ``begin`` / ``interpolate`` / ``finish`` and
    the per-frame ``_drive_mobject_updaters`` pass, which is all this test
    observes.
    """

    win_w, win_h = 480, 360

    def __init__(self, scene):
        self.scene = scene
        self._fast_record = True
        self._fast_record_fps = 30
        self._fast_record_count_only = True
        self._fast_record_pipe_mode = True
        self._fast_record_segment = None
        self._fast_record_frame_idx = 0
        self._fast_record_sim_time = 0.0
        self._last_frame_time = -1.0


def _scene_with_updater():
    """A scene holding one square whose own updater counts its calls."""
    seen = []
    mob = Square()
    mob.add_updater(lambda m, dt: seen.append(dt))
    scene = StubScene(mob)
    return scene, mob, seen


def _positive(seen):
    return [dt for dt in seen if dt > 0]


def test_builder_play_does_not_run_the_animated_mobjects_own_updater():
    """The ``.animate`` case: suspended for the whole play, resumed after.

    The play runs 30 frames (run_time 1.0 at 30 fps).  ``_play_legacy`` may
    drive the updater exactly ONCE with dt > 0 -- on the finishing frame, after
    ``Animation.finish()`` resumed the mobject and before the loop breaks --
    which is the legacy twin of CE's trailing ``update_mobjects(0)`` pass (CE
    evaluates it at dt 0, this loop at its last frame's dt).  While the
    animation itself was running the updater must not fire AT ALL: that is the
    suspend rule, and breaking it puts the animation one frame ahead of CE.
    """
    scene, mob, seen = _scene_with_updater()
    host = _LegacyHost(scene)
    host._play_legacy(mob.animate.shift(RIGHT))
    assert len(_positive(seen)) <= 1, (
        "the animated mobject's own updater ran DURING the play (%d positive-dt "
        "calls over 30 frames): CE suspends it in Animation.begin() exactly so "
        "the animation cannot render one frame ahead (RTM[k] == CE[k+1])"
        % len(_positive(seen)))
    assert mob.updating_suspended is False, (
        "Animation.finish() must resume the mobject it suspended")
    assert mob.get_center() == pytest.approx([1.0, 0.0, 0.0]), (
        "the animation itself must still have been applied")


def test_the_removed_override_would_run_the_updater_every_frame(monkeypatch):
    """Documents the bug this file's fix removed, so the test can feel it.

    Re-applying the old ``suspend_mobject_updating = False`` override to the
    builder turns the single finishing-frame call into one call PER FRAME --
    that is the "one frame ahead of CE" divergence (RTM[k] == CE[k+1]).
    """
    from manim.mobject.mobject import _AnimationBuilder

    orig = _AnimationBuilder.build

    def forced_build(self):
        self.anim_args['suspend_mobject_updating'] = False
        return orig(self)

    monkeypatch.setattr(_AnimationBuilder, "build", forced_build)
    scene, mob, seen = _scene_with_updater()
    host = _LegacyHost(scene)
    host._play_legacy(mob.animate.shift(RIGHT))
    assert len(_positive(seen)) > 5, (
        "the old override should fire the updater on every frame, got %d"
        % len(_positive(seen)))


def test_animationgroup_sub_builders_keep_the_same_rule():
    """The nested-builder branch of the same resolution walk."""
    scene, mob, seen = _scene_with_updater()
    host = _LegacyHost(scene)
    host._play_legacy(AnimationGroup(mob.animate.shift(RIGHT), run_time=0.3))
    assert len(_positive(seen)) <= 1, (
        "a builder nested in an AnimationGroup was resolved with "
        "suspend_mobject_updating forced off -- same one-frame-ahead bug "
        "(%d positive-dt calls)" % len(_positive(seen)))
    assert mob.updating_suspended is False


def test_an_updater_on_another_mobject_still_runs():
    """Non-regression: suspension is per mobject, not a global mute."""
    scene, mob, _seen = _scene_with_updater()
    other_seen = []
    other = Square()
    other.add_updater(lambda m, dt: other_seen.append(dt))
    scene.add(other)
    host = _LegacyHost(scene)
    host._play_legacy(mob.animate.shift(RIGHT))
    assert _positive(other_seen), (
        "a mobject the animation does not touch must keep updating "
        "(%d calls)" % len(other_seen))
