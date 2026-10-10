"""Regression test: after ``finish()``/``clean_up_from_scene`` the timeline must
run one more updater pass, exactly like manim's ``play_internal`` does.

Report: ``90_gallery_official.FollowingGraphCamera`` -- at the boundary between
``MoveAlongPath`` and the next ``Restore`` the camera lagged manim CE by one pan
step (the axes row/col jumped 44 px at frame 120 and eased back over ~48 frames;
``mean|CE-RTM|`` over frames 120-160 was 3.8 against 0.2 elsewhere).

manim CE ends ``Scene.play_internal`` with::

    for animation in self.animations:
        animation.finish()
        animation.clean_up_from_scene(self)
    ...
    self.update_mobjects(0)

``finish()`` applies ``interpolate(1)`` only *after* RTM's render loop has ended,
so the camera frame's ``update_curve`` updater never sees the dot at alpha == 1 --
and the scene removes that updater before the next play.  ``Restore.begin()`` then
captures a camera one step behind.

Pure Python: stub scene / stub timeline / stub window, no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import Animation, Dot, RIGHT

from real_time_manim import vulkan_bind
from real_time_manim.vulkan_bind import MLWindow, _drive_mobject_updaters


class StubScene:
    def __init__(self):
        self.mobjects = []


class StubTimeline:
    """Only the three attributes ``_run_timeline`` touches."""

    def __init__(self, anim, duration):
        self._entries = [{"anim": anim}]
        self.duration = duration
        self.render_calls = []

    def render_at(self, t):
        self.render_calls.append(t)


class StubWindow:
    def __init__(self, scene):
        self.scene = scene
        self._fast_record = False
        self._fast_record_fps = 30
        self._capture_frame = lambda: None


def _run(anim, duration, monkeypatch, events):
    """Drive ``MLWindow._run_timeline`` unbound, spying on the updater pass."""
    window = StubWindow(scene := StubScene())
    tl = StubTimeline(anim, duration)

    original = vulkan_bind._drive_mobject_updaters

    def spy(mob_scene, dt, *args, **kwargs):
        events.append(("drive", mob_scene, dt))
        return original(mob_scene, dt, *args, **kwargs)

    monkeypatch.setattr(vulkan_bind, "_drive_mobject_updaters", spy)
    MLWindow._run_timeline(window, tl)
    return scene, tl


def test_updater_pass_runs_after_finish(monkeypatch):
    """``_drive_mobject_updaters(scene, 0.0)`` must follow the finish loop."""
    leader, follower = Dot(), Dot()
    events = []

    class MoveLeader(Animation):
        def __init__(self, target, **kwargs):
            super().__init__(leader, **kwargs)
            self._target = target

        def finish(self):
            super().finish()
            leader.move_to(self._target)
            events.append(("finish",))

    scene, tl = _run(MoveLeader(4 * RIGHT), 0.04, monkeypatch, events)

    assert ("finish",) in events, "the animation never finished"
    drives = [e for e in events if e[0] == "drive"]
    assert drives, "no updater pass after finish/clean_up_from_scene"
    assert drives[0][1] is scene and drives[0][2] == 0.0, drives[0]
    assert events.index(drives[0]) > events.index(("finish",)), (
        "the updater pass ran before finish(), so it still saw the pre-final "
        "state -- that is exactly the stale-camera bug")


def test_follower_settles_on_the_finished_position(monkeypatch):
    """A camera-like follower updater must see the leader at alpha == 1."""
    leader, follower = Dot(), Dot()
    follower.add_updater(lambda m: m.move_to(leader.get_center()))

    class MoveLeader(Animation):
        def finish(self):
            super().finish()
            leader.move_to(4 * RIGHT)

    scene = StubScene()
    scene.mobjects.extend([leader, follower])
    window = StubWindow(scene)
    tl = StubTimeline(MoveLeader(leader), 0.04)

    MLWindow._run_timeline(window, tl)

    assert (follower.get_center() == leader.get_center()).all(), (
        "the follower never caught up with the finished leader: the updater "
        "pass after finish() is missing")


def test_pass_costs_no_time(monkeypatch):
    """dt must be 0 -- a re-anchor, not a replay of accumulated time."""
    events = []
    leader = Dot()

    class MoveLeader(Animation):
        def finish(self):
            super().finish()
            leader.move_to(4 * RIGHT)

    _run(MoveLeader(leader), 0.04, monkeypatch, events)
    assert all(e[2] == 0.0 for e in events if e[0] == "drive"), events
