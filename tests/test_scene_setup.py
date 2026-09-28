"""Regression test: the scene lifecycle calls setup() before construct().

Manim's own Scene.render() runs setup() then construct(); RTM used to call
construct() alone, so everything a scene prepared in setup() was missing --
LinearTransformationScene.moving_vectors, ZoomedScene.zoomed_display,
MovingCameraScene.camera.frame and any user setup() hook.

Pure Python: no window, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from manim import Scene

from real_time_manim.record import scene_lifecycle, _as_runner


class Recording(Scene):
    """Records the order in which the lifecycle hooks are called."""

    def setup(self):
        self.calls = getattr(self, 'calls', [])
        self.calls.append("setup")

    def construct(self):
        self.calls.append("construct")


def test_lifecycle_calls_setup_before_construct():
    scene = Recording()
    scene_lifecycle(scene)
    assert scene.calls == ["setup", "construct"], scene.calls


def test_runner_from_class_uses_the_lifecycle():
    ran = {}

    class Tracked(Recording):
        def construct(self):
            Recording.construct(self)
            ran["calls"] = list(self.calls)

    _as_runner(Tracked)()
    assert ran["calls"] == ["setup", "construct"], ran


def test_runner_from_instance_uses_the_lifecycle():
    scene = Recording()
    _as_runner(scene)()
    assert scene.calls == ["setup", "construct"], scene.calls


def test_runner_still_rejects_non_scenes():
    try:
        _as_runner(object() if not hasattr(object, "construct") else object)
    except TypeError:
        return
    raise AssertionError("expected TypeError for a non-scene")
