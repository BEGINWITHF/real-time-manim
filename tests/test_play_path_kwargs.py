# -*- coding: utf-8 -*-
"""Play-level ``path_arc`` must reach the animation (manim parity).

``LinearTransformationScene.apply_transposed_matrix`` computes the net rotation
of its matrix and hands it to ``play`` -- it never touches an animation
constructor (``vector_space_scene.py:1211-1217``)::

    func = self.get_transposed_matrix_transformation(transposed_matrix)
    if "path_arc" not in kwargs:
        net_rotation = np.mean(
            [angle_of_vector(func(RIGHT)), angle_of_vector(func(UP)) - np.pi / 2]
        )
        kwargs["path_arc"] = net_rotation
    self.apply_function(func, **kwargs)      # -> self.play(*anims, **kwargs)

manim's ``Scene.compile_animations`` ends with::

    for animation in animations:
        for k, v in kwargs.items():
            setattr(animation, k, v)

so ``path_arc`` lands on every animation and ``Transform``'s property setter
rebuilds ``path_func`` -- every animated point then travels a circular arc
instead of a straight line (``utils.paths.path_along_arc``).  RTM forwarded only
``run_time`` / ``rate_func``, so the number plane interpolated in a straight
line:

    measured on wiki 01-场景与相机/专用场景 ``05-线性变换场景-apply.mp4`` f40,
    the grid line that starts at y = 3 sits at y = 3.144 in CE (the arc lifts
    |y| by 4.8 %, exactly ``path_along_arc(net_rotation)`` at that frame's
    eased alpha) and stayed at 3.000 in RTM.  mean|diff| 4.08 with 172 frames
    over 4.0, every one of them inside an ``apply_*`` segment.

Stubs only: no DLL, no GPU, no images.  The one live-branch test draws nothing
(``sync``/``_capture_frame`` are stubs) and runs 0.5 s of a 60 fps play.
"""
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

from manim import (
    RIGHT,
    UP,
    ApplyPointwiseFunction,
    FadeIn,
    LinearTransformationScene,
    Scene,
    Square,
)
from manim.utils.paths import path_along_arc, straight_path
from manim.utils.rate_functions import smooth
from manim.utils.space_ops import angle_of_vector

from real_time_manim.animations import Transform as RtmTransform
from real_time_manim.record import scene_lifecycle
from real_time_manim.window.play import (
    PATH_PLAY_KWARGS,
    PlayMixin,
    _forward_path_kwargs,
)

SHEAR = [[1, 1], [0, 1]]


# ---------------------------------------------------------------------------
# window stubs -- no DLL, no GPU
# ---------------------------------------------------------------------------

class TimelineStub(PlayMixin):
    """The LIVE branch of ``play()`` with every drawing call nulled out."""

    _schedule_mode = False

    def __init__(self, scene, sample=None):
        self.scene = scene
        self._fast_record = False
        self._cursor = 0.0
        self._sched = []
        self._sample = sample
        self.samples = []

    def sync(self, scene):
        pass

    def tick(self):
        return True

    def _capture_frame(self):
        if self._sample is not None:
            self.samples.append(self._sample())


class ScheduleStub(TimelineStub):
    """The ``FrameServer`` branch: ``play()`` records, never renders."""

    _schedule_mode = True


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _y_extent(mob):
    """Largest |y| over a mobject's family -- the plane's own height."""
    pts = np.vstack([np.asarray(m.points, dtype=float)
                     for m in mob.family_members_with_points()])
    return float(np.abs(pts[:, 1]).max())


def _net_rotation(scene, matrix):
    """The arc ``apply_transposed_matrix`` computes for ``matrix``."""
    func = scene.get_transposed_matrix_transformation(np.array(matrix).T)
    return float(np.mean([angle_of_vector(func(RIGHT)),
                          angle_of_vector(func(UP)) - np.pi / 2]))


def _arc_factor(arc, ymax, alpha):
    """``|y|`` growth of a sheared point after ``path_along_arc`` at ``alpha``.

    The plane point ``(x, y)`` goes to ``(x + y, y)``; the arc's y-displacement
    is linear in ``y``, so one point gives the whole plane's factor.
    """
    start = np.array([[0.0, ymax, 0.0]])
    end = np.array([[ymax, ymax, 0.0]])
    return float(arc(start, end, alpha)[0][1]) / ymax


def _straight_factor(ymax, alpha):
    start = np.array([[0.0, ymax, 0.0]])
    end = np.array([[ymax, ymax, 0.0]])
    return float(straight_path()(start, end, alpha)[0][1]) / ymax


class _Demo(LinearTransformationScene):
    """A ``LinearTransformationScene`` that does nothing of its own."""

    def construct(self):
        pass


# ---------------------------------------------------------------------------
# the forwarding rule itself
# ---------------------------------------------------------------------------

def test_path_play_kwargs_are_declared_supported():
    """The A34 warning must not name the keywords now applied."""
    assert "path_arc" in PATH_PLAY_KWARGS
    assert set(PATH_PLAY_KWARGS) <= set(
        __import__("real_time_manim.window.play", fromlist=["x"])
        .SUPPORTED_PLAY_KWARGS)


def test_play_forwards_path_arc_to_a_manim_animation():
    """The mechanism: manim's ``Transform.path_arc`` property is set by play."""
    win = ScheduleStub(Scene())
    anim = ApplyPointwiseFunction(lambda p: p, Square(), run_time=1.0)
    assert anim.path_arc == pytest.approx(0.0, abs=1e-12)

    win.play(anim, run_time=1.0, path_arc=-np.pi / 8)

    assert anim.path_arc == pytest.approx(-np.pi / 8)
    assert anim.path_func is not straight_path, (
        "path_arc reached the attribute but never rebuilt path_func -- the "
        "points would still interpolate in a straight line")


def test_play_forwards_path_arc_to_rtms_own_transform():
    """RTM's own ``Transform`` stores the arc privately and derives lazily."""
    anim = RtmTransform(Square(), Square().shift(RIGHT), run_time=1.0)
    _forward_path_kwargs([anim], {"path_arc": np.pi / 3})
    assert anim._path_arc == pytest.approx(np.pi / 3)
    # its path_func must now bend (the private value is what the property reads)
    assert anim.path_func is not straight_path


def test_play_forwards_path_arc_axis_and_centers():
    anim = RtmTransform(Square(), Square().shift(RIGHT), run_time=1.0)
    _forward_path_kwargs([anim], {"path_arc": np.pi / 4,
                                  "path_arc_axis": np.array([0.0, 1.0, 0.0]),
                                  "path_arc_centers": np.zeros(3)})
    assert anim._path_arc == pytest.approx(np.pi / 4)
    assert list(anim._path_arc_axis) == [0.0, 1.0, 0.0]
    assert anim._path_arc_centers is not None


def test_play_forwards_an_explicit_path_func():
    """``path_func`` wins over ``path_arc`` in both implementations."""
    calls = []

    def custom(start, end, alpha):
        calls.append(alpha)
        return start

    anim = ApplyPointwiseFunction(lambda p: p, Square(), run_time=1.0)
    _forward_path_kwargs([anim], {"path_func": custom})
    assert anim.path_func is custom, "explicit path_func not forwarded"

    rtm = RtmTransform(Square(), Square().shift(RIGHT), run_time=1.0)
    _forward_path_kwargs([rtm], {"path_func": custom})
    assert rtm.path_func is custom, "explicit path_func not forwarded (RTM)"


def test_path_play_kwargs_print_no_warning(capsys):
    win = ScheduleStub(Scene())
    win.play(FadeIn(Square()), run_time=0.2, path_arc=0.3)
    out = capsys.readouterr().out
    assert "unsupported keyword" not in out, out


def test_unknown_play_kwargs_still_warn_and_stay_inert(capsys):
    """A34 is unchanged: only the ``path_*`` family became honoured."""
    win = ScheduleStub(Scene())
    anim = FadeIn(Square())
    win.play(anim, lag_ratio=0.7, run_time=0.3)
    out = capsys.readouterr().out
    assert "unsupported keyword" in out and "'lag_ratio'" in out, out
    assert anim.lag_ratio == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# end to end: a real LinearTransformationScene's plane follows the arc
# ---------------------------------------------------------------------------

def test_sheared_number_plane_follows_the_arc_end_to_end():
    """The reported clip, in-process: ``apply_matrix`` must bend the plane.

    ``run_time=0.5`` is exactly 30 frames at 60 fps, so frame 15 sits at raw
    alpha 0.5 -- where manim's ``smooth`` rate function returns 0.5 too, i.e.
    the arc's own maximum (``path_along_arc`` peaks at half the arc angle).
    """
    run_time = 0.5
    scene = _Demo()
    scene_lifecycle(scene)                # setup(): background + foreground plane
    win = TimelineStub(scene, sample=lambda: _y_extent(scene.plane))
    scene.play = win.play

    base = _y_extent(scene.plane)
    assert base > 1.0, "scene setup produced no foreground plane"
    scene.apply_matrix(SHEAR, run_time=run_time)
    assert len(win.samples) >= 16, win.samples

    net_rotation = _net_rotation(scene, SHEAR)
    arc = path_along_arc(net_rotation)
    expected = _arc_factor(arc, base, smooth(0.5))
    straight = _straight_factor(base, smooth(0.5))

    peak = max(win.samples) / base
    assert abs(expected - straight) > 0.02, (expected, straight)   # the test bites
    assert peak == pytest.approx(expected, rel=2e-3), (
        "the sheared plane did not follow the play's path_arc: |y| grew by a "
        "factor of %.4f (straight line would be %.4f, the arc is %.4f) -- "
        "path_arc is being dropped by win.play" % (peak, straight, expected))
