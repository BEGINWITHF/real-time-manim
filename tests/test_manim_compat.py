"""Regression test: the Manim compatibility shims in real_time_manim.compat.

Each test reproduces an UPSTREAM Manim defect (0.20/0.21) that plain Manim hits
too, then asserts the RTM-side workaround makes the class usable.  Importing
`real_time_manim` applies every shim.

Pure Python: no window, no GPU (LabeledArrow aside, these all fail at
construction/begin time).
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import pytest
from manim import Circle, FadeIn, Square

import real_time_manim                                   # noqa: F401  (applies shims)
from real_time_manim.compat import apply_manim_shims


def test_shims_are_idempotent():
    assert apply_manim_shims() == {"already applied": True}


def test_apply_pointwise_function_to_center_runs():
    """Upstream: super().__init__(mobject.move_to, **kwargs) drops `mobject`.

    Construction *and* interpolation, because a shim that only fixes construction
    (leaving ``method = mobject.apply_function``) makes ``begin()`` hand that bound
    method a bare coordinate -> "numpy.ndarray object is not callable".
    """
    from manim import Square
    from manim.animation.transform import ApplyPointwiseFunctionToCenter

    mob = Square()
    anim = ApplyPointwiseFunctionToCenter(lambda p: p, mob)
    anim.begin()
    anim.interpolate(0.5)
    # begin() supplies the centre as the single argument, so the method the
    # animation applies has to be the bound `move_to`
    assert anim.method.__name__ == "move_to"
    assert anim.method.__self__ is mob


def test_movement_module_has_vmobject():
    """Upstream: SmoothedVectorizedHomotopy uses VMobject without importing it."""
    from manim.animation import movement
    from manim.mobject.types.vectorized_mobject import VMobject

    assert movement.VMobject is VMobject


def test_smoothed_vectorized_homotopy_interpolates():
    import numpy as np
    from manim.animation.movement import SmoothedVectorizedHomotopy

    # a Homotopy function takes a point plus the animation time
    anim = SmoothedVectorizedHomotopy(lambda x, y, z, t: np.array([x, y, z]), Square())
    anim.begin()
    anim.interpolate(0.5)               # used to raise NameError: VMobject


def test_transform_animations_shim_populates_subanim_state():
    """Upstream: sub-animations without `target_copy` blow up in begin().

    Both of the class's upstream defects are covered: the missing `target_copy`
    and (in manim >= 0.21) the strict family zip.
    """
    from manim.animation.transform import TransformAnimations

    anim = TransformAnimations(FadeIn(Square()), FadeIn(Square()))
    anim.begin()                            # used to raise AttributeError
    anim.interpolate(0.5)                   # used to raise ValueError (strict zip)
    assert anim.start_anim.target_copy is not None
    assert anim.end_anim.target_copy is not None


def test_show_partial_has_default_bounds():
    """Upstream: ShowPartial._get_bounds always raises NotImplementedError."""
    from manim.animation.creation import ShowPartial

    anim = ShowPartial(Square())
    assert anim._get_bounds(0.25) == (0.0, 0.25)
    anim.begin()
    anim.interpolate(0.5)


def test_split_screen_camera_constructs():
    """Upstream: Camera.__init__ -> init_background needs `shifted_cameras`."""
    from manim import Camera, SplitScreenCamera

    cam = SplitScreenCamera(Camera(), Camera())
    assert cam.left_camera is not None and cam.right_camera is not None
    assert cam.shifted_cameras              # now populated by MappingCamera


def test_labeled_arrow_interpolates_without_broadcast_error():
    """Upstream: nested families reach bezier.interpolate with (16,3) vs (12,3)."""
    from manim import FadeIn, LabeledArrow

    anim = FadeIn(LabeledArrow("x", start=[-2, 0, 0], end=[2, 0, 0]))
    anim.begin()                            # used to raise ValueError
    anim.interpolate(0.5)


def test_normal_transform_still_interpolates():
    """The alignment shim must not change well-formed transforms."""
    from manim import Circle, Square, Transform

    anim = Transform(Square(), Circle())
    anim.begin()
    anim.interpolate(0.5)
    assert anim.mobject.get_num_points() > 0


def test_env_switch_disables_shims(monkeypatch):
    """RTM_NO_MANIM_SHIMS=1 keeps Manim untouched."""
    monkeypatch.setenv("RTM_NO_MANIM_SHIMS", "1")
    assert apply_manim_shims() == {"disabled": "RTM_NO_MANIM_SHIMS is set"}
    monkeypatch.delenv("RTM_NO_MANIM_SHIMS")
    assert apply_manim_shims() == {"already applied": True}


def test_import_applies_shims_without_the_switch():
    """A plain import (no env var) leaves the shims in place."""
    from manim import Camera, SplitScreenCamera, Square
    from manim.animation import movement
    from manim.animation.creation import ShowPartial

    assert hasattr(movement, "VMobject")
    assert ShowPartial(Square())._get_bounds(0.3) == (0.0, 0.3)
    assert SplitScreenCamera(Camera(), Camera()).shifted_cameras
