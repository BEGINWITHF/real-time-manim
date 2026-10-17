"""Regression test: ``wait_until``'s ``stop_condition`` must end the wait early.

Report: wiki ``01-场景与相机/场景/03-播放与等待`` -- ``self.wait_until(cond,
max_time=0.3)`` always ran the full ``max_time`` even when ``cond`` was already
true, where manim ends the wait on the frame the condition first fires.

manim's ``CairoRenderer`` loop does, per frame::

    update_frame(scene)      # updaters run
    write_frame(scene)       # the frame is emitted
    if stop_condition is not None and stop_condition():
        break                # ...so the wait ends on that frame

``_run_timeline`` was missing the trailing check, so the wait never stopped
early.  The fix evaluates the ``Wait``'s ``stop_condition`` once per frame AFTER
the frame is drawn and breaks, reporting the real elapsed time so the audio
playhead advances by what actually played.

This is forward-only by nature: ``stop_condition`` is a stateful, side-effecting
callable, so the resolved end time is only known while stepping forward (a
random-access ``render_at`` still follows the full schedule).

Pure Python: stub window + timeline, a real manim ``Wait``, no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import Wait

from real_time_manim.window.play import PlayMixin, TARGET_FPS
from real_time_manim.timeline import ce_frame_count


class StubScene:
    def __init__(self):
        self.mobjects = []
        self.updaters = []

    def add(self, mob):
        self.mobjects.append(mob)

    def get_mobject_family_members(self):
        members = []
        for root in self.mobjects:
            members.extend(root.get_family())
        return members


class StubTimeline:
    def __init__(self, duration):
        self.duration = duration
        self._entries = []
        self.render_calls = 0

    def render_at(self, t, **kwargs):
        self.render_calls += 1
        return True


class StubWindow:
    def __init__(self):
        self._fast_record = False
        self.scene = StubScene()

    def _capture_frame(self):
        pass


def _run(wait, duration):
    tl = StubTimeline(duration=duration)
    win = StubWindow()
    elapsed = PlayMixin._run_timeline(win, tl, [wait])
    return tl, elapsed


def test_wait_until_stops_on_the_frame_the_condition_fires():
    """The reported case: cond true on the 3rd frame -> only 3 frames render."""
    calls = {"n": 0}

    def cond():
        calls["n"] += 1
        return calls["n"] >= 3

    wait = Wait(0.5, stop_condition=cond)
    tl, elapsed = _run(wait, duration=0.5)
    # frames 0,1,2 each draw then check; the check after frame 2 fires -> break.
    assert tl.render_calls == 3, tl.render_calls
    assert abs(elapsed - 3.0 / TARGET_FPS) < 1e-9, elapsed


def test_wait_until_runs_full_duration_when_condition_never_true():
    """A condition that never fires renders the whole wait, unchanged."""
    wait = Wait(0.5, stop_condition=lambda: False)
    tl, elapsed = _run(wait, duration=0.5)
    full = ce_frame_count([wait], 0.5, TARGET_FPS)
    assert tl.render_calls == full, (tl.render_calls, full)
    assert elapsed is None   # not truncated -> caller keeps tl.duration


def test_condition_false_until_last_possible_frame():
    """Fires on the final frame: every frame still renders, elapsed reported."""
    calls = {"n": 0}

    def cond():
        calls["n"] += 1
        return calls["n"] >= 2

    wait = Wait(0.5, stop_condition=cond)
    tl, elapsed = _run(wait, duration=0.5)
    assert tl.render_calls == 2, tl.render_calls
    assert abs(elapsed - 2.0 / TARGET_FPS) < 1e-9, elapsed


def test_plain_wait_without_condition_is_unaffected():
    """A wait with no stop_condition renders its full length (no regression)."""
    wait = Wait(0.5)
    tl, elapsed = _run(wait, duration=0.5)
    full = ce_frame_count([wait], 0.5, TARGET_FPS)
    assert tl.render_calls == full, (tl.render_calls, full)
    assert elapsed is None


def test_raising_condition_stops_the_wait_not_the_play():
    """A condition that raises ends the wait gracefully instead of crashing."""

    def cond():
        raise RuntimeError("boom")

    wait = Wait(0.5, stop_condition=cond)
    tl, elapsed = _run(wait, duration=0.5)   # must not raise
    assert tl.render_calls == 1, tl.render_calls   # first frame drew, then check raised -> stop
    assert abs(elapsed - 1.0 / TARGET_FPS) < 1e-9, elapsed
