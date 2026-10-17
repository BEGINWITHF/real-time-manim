"""Gap tests A15-A19: transform / rotation / homotopy motion semantics.

Wiki evidence:

* A15 ``Rotate`` swallowed ``axis`` -- ``03-动画/移动与旋转/01-旋转.md`` (19, 58, 144)
* A16 ``Rotate`` swallowed ``about_edge`` -- same page (21, 58, 144)
* A17 RTM ``Homotopy`` did not accept ``apply_function_kwargs`` --
  ``03-动画/移动与旋转/02-沿路径与同态变换.md`` (70, 112)
* A18 ``SmoothedVectorizedHomotopy`` / ``ComplexHomotopy`` /
  ``PhaseFlow`` ``apply_function_kwargs`` --
  ``03-动画/移动与旋转/02b-同态变换其余类.md`` (20, 164)
* A19 RTM ``Transform`` stored ``path_arc_centers`` but never used it --
  ``03-动画/变换/01-Transform核心.md`` (134, 191)

Everything here is GPU-free (pure point math) except the one sender-routing
smoke test at the bottom, which builds a *hidden* window and skips when the
Vulkan runtime is unavailable.

Run with::

    python -X utf8 -m pytest tests/test_gap_transform_motion.py -q
"""
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
import pytest

import real_time_manim  # noqa: F401  -- installs bundled manim + compat shims

from manim import (
    DOWN,
    IN,
    LEFT,
    ORIGIN,
    OUT,
    PI,
    RIGHT,
    UP,
    Circle,
    Square,
    Triangle,
    VGroup,
)
from real_time_manim.animations.homotopy import Homotopy
from real_time_manim.animations.rotate import Rotate
from real_time_manim.animations.rotating import Rotating
from real_time_manim.animations.transform import Transform as RtmTransform
from real_time_manim.rate_functions import _linear
from real_time_manim.state import get_anim_rotation
from real_time_manim.utils.paths import path_along_arc, rotation_matrix


def _drive(anim, alpha):
    """Begin at t=0 and interpolate to ``alpha`` (run_time is 1 s in these tests)."""
    anim.begin(0.0)
    anim.interpolate(alpha * anim.run_time)


# ---------------------------------------------------------------------------
# A15: Rotate honours `axis`
# ---------------------------------------------------------------------------

def test_rotate_axis_in_flips_the_screen_direction():
    """z-parallel axis: ``IN`` must turn the other way (the Rotating demo case)."""
    sq_out = Square(side_length=2)
    anim = Rotate(sq_out, angle=PI / 2, axis=OUT)
    _drive(anim, 1.0)
    assert get_anim_rotation(sq_out) == pytest.approx(PI / 2)

    sq_in = Square(side_length=2)
    anim = Rotate(sq_in, angle=PI / 2, axis=IN)
    _drive(anim, 1.0)
    assert get_anim_rotation(sq_in) == pytest.approx(-PI / 2)


def test_rotate_about_up_axis_foreshortens_x_and_lifts_z():
    """In-plane axis: a real 3D Rodrigues rotation, CE point for point.

    manim's ``Rotate`` interpolates start -> rotated target, and for a
    rotation that relation makes CE's arc path exactly
    ``R(alpha * angle) @ (start - pivot) + pivot`` -- so that is what the
    mid-frame must equal, and the end frame must equal
    ``mobject.rotate(angle, axis, about_point)``.
    """
    sq = Square(side_length=2).shift(RIGHT + UP * 0.5)
    start = sq.points.copy()
    anim = Rotate(sq, angle=PI / 2, axis=UP, about_point=ORIGIN)
    anim.begin(0.0)

    anim.interpolate(0.5 * anim.run_time)
    mid = (start - ORIGIN) @ rotation_matrix(PI / 4, UP).T + ORIGIN
    assert np.allclose(sq.points, mid, atol=1e-9)

    anim.interpolate(anim.run_time)
    end = (start - ORIGIN) @ rotation_matrix(PI / 2, UP).T + ORIGIN
    assert np.allclose(sq.points, end, atol=1e-9)

    # rotation about UP: x -> x*cos(t), y untouched, z = -x*sin(t)
    assert sq.get_width() == pytest.approx(0.0, abs=1e-9)
    assert sq.get_height() == pytest.approx(2.0, abs=1e-6)
    assert np.abs(sq.points[:, 2]).max() == pytest.approx(2.0, abs=1e-6)

    anim.finish()
    assert not hasattr(sq, "_rotation_3d")
    assert getattr(sq, "_transforming", False) is True   # points carry the final state
    assert get_anim_rotation(sq) == 0.0
    assert np.allclose(sq.points, end, atol=1e-9)


def test_rotate_3d_axis_is_a_pure_function_of_alpha():
    sq = Square(side_length=2).shift(LEFT)
    anim = Rotate(sq, angle=2 * PI / 3, axis=RIGHT + UP, about_point=DOWN)
    anim.begin(0.0)
    anim.interpolate(0.3 * anim.run_time)
    first = sq.points.copy()
    anim.interpolate(0.9 * anim.run_time)
    anim.interpolate(0.3 * anim.run_time)
    assert np.allclose(sq.points, first, atol=1e-9)


def test_rotate_3d_folds_a_carried_channel_rotation_into_the_points():
    """``Rotate`` persists through the draw-time channel -- a later 3D axis
    rotation must not throw that state away."""
    sq = Square(side_length=2)
    first = Rotate(sq, angle=PI / 4)
    _drive(first, 1.0)
    assert get_anim_rotation(sq) == pytest.approx(PI / 4)

    second = Rotate(sq, angle=PI / 2, axis=UP, about_point=ORIGIN)
    _drive(second, 1.0)

    ref = Square(side_length=2)
    ref.rotate(PI / 4, axis=OUT, about_point=ref.get_center())
    ref.rotate(PI / 2, axis=UP, about_point=ORIGIN)
    assert np.allclose(sq.points, ref.points, atol=1e-9)
    assert get_anim_rotation(sq) == 0.0


def test_rotate_3d_folds_a_carried_vgroup_channel_rotation():
    """The container's channel rotation reaches its children at draw time --
    a 3D-axis rotation must fold it in, not drop it."""
    sq = Square(side_length=2)
    vg = VGroup(sq)
    first = Rotate(vg, angle=PI / 3)
    _drive(first, 1.0)
    assert get_anim_rotation(vg) == pytest.approx(PI / 3)

    second = Rotate(vg, angle=PI / 2, axis=UP, about_point=ORIGIN)
    _drive(second, 1.0)

    ref = Square(side_length=2)
    ref.rotate(PI / 3, axis=OUT, about_point=ref.get_center())
    ref.rotate(PI / 2, axis=UP, about_point=ORIGIN)
    assert np.allclose(sq.points, ref.points, atol=1e-9)
    assert get_anim_rotation(vg) == 0.0


def test_rotating_3d_axis_rides_the_point_path_too():
    """A15 companion check: ``Rotating`` already implements ``axis`` (unlike
    ``Rotate``), but its non-z branch only shows on primitives when the
    mobject rides the point path."""
    sq = Square(side_length=2)
    anim = Rotating(sq, angle=PI / 2, axis=UP, run_time=1.0, rate_func=_linear)
    anim.begin(0.0)
    anim.interpolate(0.5)
    assert getattr(sq, "_transforming", False) is True
    # x squashed by cos(angle/2), y untouched, z projected away
    # (Rotating's orthographic rule for a non-z axis)
    assert sq.get_width() == pytest.approx(2.0 * math.cos(PI / 4), abs=1e-6)
    assert sq.get_height() == pytest.approx(2.0, abs=1e-6)
    assert np.abs(sq.points[:, 2]).max() == pytest.approx(0.0, abs=1e-9)


def test_rotate_3d_axis_honours_about_edge_pivot():
    tri = Triangle().shift(UP * 1.5)
    start = tri.points.copy()
    pivot = tri.get_critical_point(UP)
    anim = Rotate(tri, angle=PI / 3, axis=RIGHT, about_edge=UP)
    _drive(anim, 1.0)
    expected = (start - pivot) @ rotation_matrix(PI / 3, RIGHT).T + pivot
    assert np.allclose(tri.points, expected, atol=1e-9)


# ---------------------------------------------------------------------------
# A16: Rotate honours `about_edge`
# ---------------------------------------------------------------------------

def test_rotate_about_edge_uses_the_critical_point():
    sq = Square(side_length=2).shift(RIGHT)
    anim = Rotate(sq, angle=PI / 2, about_edge=UP)
    anim.begin(0.0)
    expected = sq.get_critical_point(UP)
    # The pivot is resolved from `about_edge` and stored on the animation.  It
    # is baked into the point arrays (not published as the draw-time
    # `_rotation_about_point` channel): the channel is honoured only by the
    # primitive senders, while `_send_polygon` and the generic point path spin
    # the shape in place, so an explicit pivot must live in the geometry.
    assert np.allclose(anim._pivot, expected)
    assert expected[1] == pytest.approx(sq.get_top()[1])
    assert expected[0] == pytest.approx(sq.get_center()[0])
    # ... and the quarter turn really orbits the square about that pivot.
    start = sq.points.copy()
    anim.interpolate(anim.run_time)
    assert not np.allclose(sq.points, start, atol=1e-6)
    anim.finish()
    assert not hasattr(sq, "_rotation_about_point")


def test_rotate_about_point_wins_over_about_edge():
    sq = Square(side_length=2)
    anim = Rotate(sq, angle=PI / 2, about_point=ORIGIN, about_edge=UP)
    anim.begin(0.0)
    assert np.allclose(anim._pivot, ORIGIN)


def test_rotate_without_pivot_keeps_the_renderer_default():
    """``about_point``/``about_edge`` both None: the draw-time channel keeps
    rotating about the mobject's own centre (CE's ``about_point=None`` rule).
    """
    sq = Square(side_length=2)
    anim = Rotate(sq, angle=PI / 2)
    anim.begin(0.0)
    assert getattr(sq, "_rotation_about_point", None) is None
    anim.interpolate(anim.run_time)
    assert get_anim_rotation(sq) == pytest.approx(PI / 2)


# ---------------------------------------------------------------------------
# A17: RTM Homotopy accepts apply_function_kwargs
# ---------------------------------------------------------------------------

def _scale_twice(x, y, z, t):
    return (2.0 * x, 2.0 * y, z)


def test_homotopy_still_maps_absolute_coordinates_by_default():
    """No kwargs: ``apply_function`` defaults to ``about_point=ORIGIN``, i.e.
    the plain absolute-coordinate mapping RTM always did."""
    sq = Square(side_length=2)
    start = sq.points.copy()
    anim = Homotopy(lambda x, y, z, t: (x + 1.0, y, z), sq,
                    run_time=1.0, rate_func=_linear)
    anim.begin(0.0)
    anim.interpolate(0.5)
    assert np.allclose(sq.points, start + np.array([1.0, 0.0, 0.0]), atol=1e-9)
    anim.finish()
    assert np.allclose(sq.points, start, atol=1e-9)   # RTM restores the start state


def test_homotopy_empty_kwargs_match_the_default():
    sq_a = Square(side_length=2)
    sq_b = Square(side_length=2)
    anim_a = Homotopy(_scale_twice, sq_a, run_time=1.0, rate_func=_linear)
    anim_b = Homotopy(_scale_twice, sq_b, run_time=1.0, rate_func=_linear,
                      apply_function_kwargs={})
    _drive(anim_a, 0.5)
    _drive(anim_b, 0.5)
    assert np.allclose(sq_a.points, sq_b.points, atol=1e-12)


def test_homotopy_apply_function_kwargs_about_point():
    sq = Square(side_length=2)
    start = sq.points.copy()
    pivot = np.array([1.0, 0.25, 0.0])
    anim = Homotopy(_scale_twice, sq, run_time=1.0, rate_func=_linear,
                    apply_function_kwargs={"about_point": pivot})
    _drive(anim, 0.5)
    shifted = start - pivot
    expected = np.column_stack(
        [shifted[:, 0] * 2.0, shifted[:, 1] * 2.0, shifted[:, 2]]) + pivot
    assert np.allclose(sq.points, expected, atol=1e-9)


def test_homotopy_apply_function_kwargs_about_edge():
    sq = Square(side_length=2).shift(RIGHT * 3)
    start = sq.points.copy()
    pivot = sq.get_critical_point(LEFT)          # left edge, x == 2
    assert pivot[0] == pytest.approx(2.0)
    anim = Homotopy(lambda x, y, z, t: (2.0 * x, y, z), sq,
                    run_time=1.0, rate_func=_linear,
                    apply_function_kwargs={"about_edge": LEFT})
    _drive(anim, 0.5)
    expected = (start - pivot) * np.array([2.0, 1.0, 1.0]) + pivot
    assert np.allclose(sq.points, expected, atol=1e-9)
    assert sq.get_left()[0] == pytest.approx(2.0)    # the edge is pinned
    assert sq.get_right()[0] == pytest.approx(6.0)   # the far side doubles away


def test_homotopy_apply_function_kwargs_are_t_independent():
    """The pivot only shifts the coordinate frame; ``t`` still drives the map."""
    sq = Square(side_length=2)
    start = sq.points.copy()
    anim = Homotopy(lambda x, y, z, t: (x + t, y, z), sq,
                    run_time=1.0, rate_func=_linear,
                    apply_function_kwargs={"about_point": np.array([5.0, 0.0, 0.0])})
    anim.begin(0.0)
    anim.interpolate(0.25)
    assert np.allclose(sq.points, start + np.array([0.25, 0.0, 0.0]), atol=1e-9)
    anim.interpolate(0.75)
    assert np.allclose(sq.points, start + np.array([0.75, 0.0, 0.0]), atol=1e-9)


def test_homotopy_rejects_unknown_apply_function_kwargs():
    with pytest.raises(TypeError):
        Homotopy(_scale_twice, Square(), apply_function_kwargs={"about_pooint": ORIGIN})


# ---------------------------------------------------------------------------
# A18: the manim-native homotopy classes (Smoothed / Complex / PhaseFlow)
# ---------------------------------------------------------------------------

def test_vmobject_apply_function_forwards_its_pivot_kwargs():
    """The mechanism behind A18: ``VMobject.apply_function`` must honour
    ``about_point``/``about_edge`` (upstream drops them; RTM patches that at
    runtime for whichever manim copy is active)."""
    from manim.mobject.types.vectorized_mobject import VMobject

    assert getattr(VMobject.apply_function, "_rtm_forwards_pivot", False) is True
    sq = Square(side_length=2)
    sq.apply_function(lambda p: 2.0 * p, about_point=np.array([1.0, 0.0, 0.0]))
    assert sq.get_right()[0] == pytest.approx(1.0, abs=1e-9)     # pivot pinned
    assert sq.get_left()[0] == pytest.approx(-3.0, abs=1e-9)     # far side doubles


def test_smoothed_vectorized_homotopy_forwards_apply_function_kwargs():
    """CE class via RTM: the dict must reach ``Mobject.apply_function``.

    manim's own ``interpolate_submobject`` already forwards it -- the pivot
    used to be dropped one level below, by ``VMobject.apply_function``
    (upstream defect, fixed at runtime by ``animations.homotopy``).
    """
    from manim.animation.movement import SmoothedVectorizedHomotopy

    c = Circle(radius=1.0)
    pivot = np.array([1.0, 0.0, 0.0])
    anim = SmoothedVectorizedHomotopy(
        lambda x, y, z, t: (2.0 * x, y, z), c,
        apply_function_kwargs={"about_point": pivot},
    )
    anim.begin()
    anim.interpolate(0.5)
    # scaled twice about the RIGHT edge: x = 1 stays, x = -1 maps to -3
    assert c.get_right()[0] == pytest.approx(1.0, abs=1e-6)
    assert c.get_left()[0] == pytest.approx(-3.0, abs=1e-6)

    # control: without kwargs the map is about ORIGIN
    c2 = Circle(radius=1.0)
    ctrl = SmoothedVectorizedHomotopy(lambda x, y, z, t: (2.0 * x, y, z), c2)
    ctrl.begin()
    ctrl.interpolate(0.5)
    assert c2.get_left()[0] == pytest.approx(-2.0, abs=1e-6)


def test_smoothed_homotopy_kwargs_survive_the_render_hook_wrapper():
    """The wiki claims the RTM side drops the passthrough -- through the real
    hook path (`install_hooks` wraps `interpolate`) it must still work."""
    from manim.animation.movement import SmoothedVectorizedHomotopy
    from real_time_manim.render_hooks import clear_hooks, install_hooks

    c = Circle(radius=1.0)
    anim = SmoothedVectorizedHomotopy(
        lambda x, y, z, t: (2.0 * x, y, z), c,
        apply_function_kwargs={"about_point": np.array([1.0, 0.0, 0.0])},
    )
    anim.begin()
    install_hooks(anim)
    try:
        anim.interpolate(0.5)
    finally:
        clear_hooks(anim)
    assert c.get_left()[0] == pytest.approx(-3.0, abs=1e-6)


def test_complex_homotopy_forwards_apply_function_kwargs():
    from manim.animation.movement import ComplexHomotopy

    sq = Square(side_length=2)
    start = sq.points.copy()
    pivot = np.array([1.0, 0.0, 0.0])
    anim = ComplexHomotopy(lambda z, t: 2.0 * z, sq,
                           apply_function_kwargs={"about_point": pivot})
    anim.begin()
    anim.interpolate(0.5)
    shifted = start - pivot
    expected = np.column_stack(
        [shifted[:, 0] * 2.0, shifted[:, 1] * 2.0, shifted[:, 2]]) + pivot
    assert np.allclose(sq.points, expected, atol=1e-9)


def test_phaseflow_has_no_apply_function_kwargs_upstream():
    """CE parity, not an RTM gap: manim's ``PhaseFlow`` never had the
    parameter (``movement.py:145``) and rejects it exactly like CE does."""
    from manim.animation.movement import PhaseFlow

    with pytest.raises(TypeError):
        PhaseFlow(lambda p: np.array([-p[1], p[0], 0.0]), Square(),
                  apply_function_kwargs={"about_point": ORIGIN})
    # and the supported signature still works
    sq = Square(side_length=2)
    orig = sq.points.copy()
    anim = PhaseFlow(lambda p: np.array([-p[1], p[0], 0.0]), sq, run_time=1.0)
    anim.begin()          # seeds last_alpha at alpha 0
    assert np.allclose(sq.points, orig, atol=1e-9)
    anim.interpolate(0.25)
    expected = orig.copy()
    expected[:, 0] += -0.25 * orig[:, 1]      # dt * (-y, x)
    expected[:, 1] += 0.25 * orig[:, 0]
    assert np.allclose(sq.points, expected, atol=1e-9)


# ---------------------------------------------------------------------------
# A19: Transform.path_arc_centers actually bends the path
# ---------------------------------------------------------------------------

def _transform_pair():
    sq = Square(side_length=1).shift(LEFT * 2)
    target = sq.copy().shift(RIGHT * 4)
    return sq, target


def test_transform_path_arc_centers_bends_the_path_like_ce():
    from manim.utils.paths import path_along_circles as ce_path_along_circles

    sq, target = _transform_pair()
    anim = RtmTransform(sq, target, path_arc=PI / 2, path_arc_centers=ORIGIN,
                        run_time=1.0, rate_func=_linear)
    anim.begin(0.0)
    anim.interpolate(0.5)
    expected = ce_path_along_circles(PI / 2, np.zeros(3), OUT)(
        anim._starting_mobject.points, anim._target_copy.points, 0.5)
    assert np.allclose(sq.points, expected, atol=1e-9)


def test_transform_path_arc_centers_changes_the_midframe():
    """The reported gap: a non-None ``path_arc_centers`` used to be stored
    and ignored -- same scene, the mid-frame must now differ."""
    sq1, target1 = _transform_pair()
    sq2, target2 = _transform_pair()
    plain = RtmTransform(sq1, target1, path_arc=PI / 2,
                         run_time=1.0, rate_func=_linear)
    bent = RtmTransform(sq2, target2, path_arc=PI / 2, path_arc_centers=ORIGIN,
                        run_time=1.0, rate_func=_linear)
    _drive(plain, 0.5)
    _drive(bent, 0.5)
    assert not np.allclose(sq1.points, sq2.points, atol=1e-6)
    # ... and it bent onto the arc, not near the straight chord
    straight_mid = sq1.points.mean(axis=0)
    bent_mid = sq2.points.mean(axis=0)
    assert np.linalg.norm(bent_mid - straight_mid) > 0.5


def test_transform_explicit_path_func_beats_path_arc_centers():
    def bump_up(start_points, end_points, alpha):
        pts = (1.0 - alpha) * start_points + alpha * end_points
        return pts + np.array([0.0, 1.5, 0.0])

    sq, target = _transform_pair()
    anim = RtmTransform(sq, target, path_arc=PI / 2, path_arc_centers=ORIGIN,
                        path_func=bump_up, run_time=1.0, rate_func=_linear)
    anim.begin(0.0)
    anim.interpolate(0.5)
    s, e = anim._starting_mobject.points, anim._target_copy.points
    expected = 0.5 * s + 0.5 * e + np.array([0.0, 1.5, 0.0])
    assert np.allclose(sq.points, expected, atol=1e-9)


def test_transform_default_path_is_unchanged():
    sq, target = _transform_pair()
    anim = RtmTransform(sq, target, run_time=1.0, rate_func=_linear)
    anim.begin(0.0)
    anim.interpolate(0.5)
    s, e = anim._starting_mobject.points, anim._target_copy.points
    assert np.allclose(sq.points, 0.5 * s + 0.5 * e, atol=1e-9)


def test_transform_path_arc_only_still_uses_path_along_arc():
    sq, target = _transform_pair()
    anim = RtmTransform(sq, target, path_arc=PI / 2,
                        run_time=1.0, rate_func=_linear)
    anim.begin(0.0)
    anim.interpolate(0.5)
    pf = path_along_arc(PI / 2, anim._path_arc_axis)
    expected = pf(anim._starting_mobject.points, anim._target_copy.points, 0.5)
    assert np.allclose(sq.points, expected, atol=1e-9)


def test_transform_path_arc_centers_accepts_a_per_point_array():
    from manim.utils.paths import path_along_circles as ce_path_along_circles

    sq, target = _transform_pair()
    anim = RtmTransform(sq, target, path_arc=PI / 2,
                        run_time=1.0, rate_func=_linear)
    anim.begin(0.0)
    # one centre per point; assigned after begin() because align_data may
    # change the point count the array has to match
    n = len(anim._starting_mobject.points)
    centers = np.zeros((n, 3))
    centers[:, 0] = np.linspace(-1.0, 1.0, n)
    anim._path_arc_centers = centers
    anim.interpolate(0.5)
    expected = ce_path_along_circles(PI / 2, centers, OUT)(
        anim._starting_mobject.points, anim._target_copy.points, 0.5)
    assert np.allclose(sq.points, expected, atol=1e-9)


# ---------------------------------------------------------------------------
# sender routing smoke test (hidden window; skipped without the Vulkan runtime)
# ---------------------------------------------------------------------------

class _Recorder(object):
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


@pytest.fixture(scope="module")
def renderer():
    import real_time_manim.vulkan_bind as vb
    try:
        r = vb.MLWindow(1920, 1080, hidden=True)
    except Exception as e:                          # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield r
    try:
        r.close()
    except Exception:
        pass


def _capture(renderer, mob):
    rec = _Recorder()
    real = renderer.dll
    renderer.dll = rec
    try:
        renderer._send(mob)
    finally:
        renderer.dll = real
    return rec.calls


def test_rotate_3d_square_reaches_the_point_path(renderer):
    """A 3D-rotated ``Square`` must not be rebuilt by ``_send_square`` from its
    ``side_length``: the emitted width has to be the foreshortened one."""
    from manim import config

    sq = Square(side_length=2, fill_opacity=1.0).shift(RIGHT)
    anim = Rotate(sq, angle=PI / 3, axis=UP, about_point=ORIGIN)
    _drive(anim, 0.5)

    calls = _capture(renderer, sq)
    names = [n for n, _ in calls]
    assert "AddRect" not in names, (
        "the 3D-rotated Square fell back to the axis-aligned rect sender")
    polys = [a for n, a in calls if n == "AddPolygon"]
    assert polys, "the 3D-rotated Square submitted no polygon"

    xs = []
    for args in polys:
        xs.extend(list(args[10])[0::2])       # AddPolygon(..., n, arr, ...)
    scale = 1920.0 / float(config.frame_width)
    manim_xs = [(x - 960.0) / scale for x in xs]
    width_units = max(manim_xs) - min(manim_xs)
    # x spans [0, 2] before the rotation and is foreshortened by cos(angle/2)
    assert width_units == pytest.approx(2.0 * math.cos(PI / 6), rel=0.02)
