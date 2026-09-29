"""Compatibility shims for bugs in Manim 0.20/0.21 that RTM can work around.

RTM drives Manim's own animation and mobject classes, so a handful of upstream
defects surface as RTM failures even though plain Manim hits them too.  Each shim
below is the minimal fix for one such defect, applied **at import time** and only
in this process -- Manim's installed files are never modified.

Every shim is idempotent and cheap; importing this module twice changes nothing.
See wiki/Known-Issues.md for the user-facing list.

The shims
---------
1. ``ApplyPointwiseFunctionToCenter.__init__`` forgets to forward ``mobject`` to
   ``ApplyPointwiseFunction``, so the class cannot be constructed at all.
2. ``manim.animation.movement`` uses ``VMobject`` in
   ``SmoothedVectorizedHomotopy.interpolate_submobject`` without importing it.
3. ``TransformAnimations`` interpolates its two sub-animations immediately, but a
   sub-animation that is not itself a ``Transform`` (e.g. ``FadeIn``) has no
   ``target_copy`` yet -> AttributeError.
4. ``ShowPartial`` is an abstract base whose ``_get_bounds`` always raises; used
   directly it cannot render.  A default (the whole path up to alpha) makes it
   behave like ``Create``.
5. ``SplitScreenCamera.__init__`` calls ``Camera.__init__`` first, which runs
   ``init_background`` -> reads ``self.shifted_cameras`` before it exists.
"""
from __future__ import annotations

import math
import os

_APPLIED = False


def _shim_apply_pointwise_function_to_center() -> bool:
    """1. Missing ``mobject`` argument in the super() call.

    Upstream calls ``super().__init__(mobject.move_to, **kwargs)``, which drops
    ``mobject`` entirely -- so it cannot even construct.  The fix is *not* to pass
    ``function``/``mobject`` on to ``ApplyPointwiseFunction`` (that leaves
    ``method = mobject.apply_function``, and ``begin()`` then hands that bound
    method a bare coordinate, giving "numpy.ndarray object is not callable").
    What the class actually needs is ``ApplyMethod`` with the bound ``move_to``:
    ``begin()`` supplies the centre as its single argument, so ``create_target``
    ends up calling ``mobject.move_to(centre)``.
    """
    from manim.animation.transform import (
        DEFAULT_POINTWISE_FUNCTION_RUN_TIME, ApplyMethod, ApplyPointwiseFunctionToCenter,
    )

    def _init(self, function, mobject,
              run_time=DEFAULT_POINTWISE_FUNCTION_RUN_TIME, **kwargs):
        self.function = function
        ApplyMethod.__init__(self, mobject.move_to, run_time=run_time, **kwargs)

    ApplyPointwiseFunctionToCenter.__init__ = _init
    return True


def _shim_movement_vmobject() -> bool:
    """2. ``VMobject`` is used but never imported in ``movement.py``."""
    from manim.animation import movement
    from manim.mobject.types.vectorized_mobject import VMobject

    if not hasattr(movement, "VMobject"):
        movement.VMobject = VMobject
        return True
    return False


def _shim_transform_animations_target_copy() -> bool:
    """3. Give sub-animations a ``target_copy`` before they are interpolated."""
    from manim.animation.transform import TransformAnimations

    original_begin = TransformAnimations.begin

    def _begin(self):
        for anim in (self.start_anim, self.end_anim):
            if getattr(anim, "target_copy", None) is None:
                target = getattr(anim, "target_mobject", None)
                if target is not None:
                    anim.target_copy = target.copy()
            # A sub-animation that is interpolated directly also needs a starting
            # copy; without one it fails before drawing anything.
            if getattr(anim, "starting_mobject", None) is None:
                mob = getattr(anim, "mobject", None)
                if mob is not None:
                    anim.starting_mobject = mob.copy()
        return original_begin(self)

    TransformAnimations.begin = _begin
    return True


def _shim_show_partial_bounds() -> bool:
    """4. ``ShowPartial`` used directly: default to the Create-style bounds."""
    from manim.animation.creation import ShowPartial

    def _get_bounds(self, alpha):
        return 0.0, alpha

    ShowPartial._get_bounds = _get_bounds
    return True


def _shim_split_screen_camera() -> bool:
    """5. ``shifted_cameras`` must exist before ``Camera.__init__`` runs."""
    from manim.camera.mapping_camera import MappingCamera, SplitScreenCamera

    original_init = SplitScreenCamera.__init__

    def _init(self, left_camera, right_camera, **kwargs):
        # Camera.__init__ -> init_background() iterates self.shifted_cameras
        self.shifted_cameras = []
        try:
            original_init(self, left_camera, right_camera, **kwargs)
        except TypeError:
            # upstream body: Camera.__init__ first, then MappingCamera.__init__
            # with the (camera, offset) pairs -- keep the half-width maths.
            from manim.camera.camera import Camera

            Camera.__init__(self, **kwargs)
            self.left_camera = left_camera
            self.right_camera = right_camera
            half_width = math.ceil(self.pixel_width / 2)
            for camera in (left_camera, right_camera):
                camera.reset_pixel_shape(camera.pixel_height, half_width)
            MappingCamera.__init__(
                self, (left_camera, (0, 0)), (right_camera, (0, half_width))
            )

    SplitScreenCamera.__init__ = _init
    return True


def _shim_transform_align_nested_families() -> bool:
    """6. Point-count mismatch reaches ``bezier.interpolate`` and blows up.

    ``Transform.begin`` aligns the *top level* of a mobject against its target,
    but nested families can still hand ``Mobject.interpolate`` two mobjects with
    different point counts (a ``LabeledArrow``'s label vs its stroke geometry),
    where the broadcast fails with
    "operands could not be broadcast together with shapes (16,3) (12,3)".

    So equalise the two operands at the call that requires it -- and only when
    their counts differ, i.e. exactly the case that used to crash.
    """
    from manim.mobject.mobject import Mobject

    original_interpolate = Mobject.interpolate

    def _interpolate(self, starting_mobject, target_mobject, alpha, *args, **kwargs):
        try:
            if starting_mobject.get_num_points() != target_mobject.get_num_points():
                target_mobject.align_points(starting_mobject)
        except Exception:
            pass                                  # never break a render over this
        return original_interpolate(self, starting_mobject, target_mobject, alpha,
                                    *args, **kwargs)

    Mobject.interpolate = _interpolate
    return True


def _shim_transform_strict_zip() -> bool:
    """6b. ``Transform.get_all_families_zipped`` zips three families strictly.

    Manim's own ``Animation`` base zips non-strictly, but ``Transform`` asks for
    ``strict=True`` -- and ``TransformAnimations`` rewires its sub-animations'
    mobjects, leaving the three families with different lengths, so the strict
    zip raises "zip() argument 2 is shorter than argument 1".

    Behaviour is left untouched whenever the families agree (still strict), and
    degenerate cases pair what exists instead of crashing, exactly like the base
    class.  Requires manim >= 0.21, where the strict zip was introduced.
    """
    from manim.animation.transform import Transform

    original = Transform.get_all_families_zipped

    def _get_all_families_zipped(self):
        mobs = [m for m in (self.mobject,
                            getattr(self, "starting_mobject", None),
                            getattr(self, "target_copy", None)) if m is not None]
        fams = [list(m.family_members_with_points()) for m in mobs]
        if len({len(f) for f in fams}) > 1:
            shortest = min(len(f) for f in fams)
            return iter(zip(*(f[:shortest] for f in fams)))
        return original(self)

    Transform.get_all_families_zipped = _get_all_families_zipped
    return True


def apply_manim_shims(force: bool = False) -> dict:
    """Apply every shim once.  Returns {name: applied_or_already_present}.

    Set ``RTM_NO_MANIM_SHIMS=1`` before importing real-time-manim to keep Manim
    untouched (useful when debugging whether a problem is really RTM's).
    """
    global _APPLIED
    if not force and os.environ.get("RTM_NO_MANIM_SHIMS"):
        return {"disabled": "RTM_NO_MANIM_SHIMS is set"}
    if _APPLIED:
        return {"already applied": True}
    results = {}
    for fn in (
        _shim_apply_pointwise_function_to_center,
        _shim_movement_vmobject,
        _shim_transform_animations_target_copy,
        _shim_show_partial_bounds,
        _shim_split_screen_camera,
        _shim_transform_align_nested_families,
        _shim_transform_strict_zip,
    ):
        name = fn.__name__.removeprefix("_shim_")
        try:
            results[name] = fn()
        except Exception as exc:            # never block importing RTM
            results[name] = f"skipped: {type(exc).__name__}: {exc}"
    _APPLIED = True
    return results
