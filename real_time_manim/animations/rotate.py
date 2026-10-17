# This might not cause a bug or issue, check for other place first --TT Noted
"""One-shot rotation: RTM's own ``Rotate`` (manim CE semantics).

Time semantics are RTM's: ``begin(t)`` / ``interpolate(t)`` with ``t`` in
seconds.  The class honours the full CE signature
``Rotate(mobject, angle=PI, axis=OUT, about_point=None, about_edge=None)``:

* ``axis`` parallel to ``OUT``/``IN`` keeps the cheap draw-time channel
  (``state.set_anim_rotation`` + ``_rotation_about_point``); a negative z
  axis (``IN``) simply flips the sign of the angle.
* ``axis`` with an in-plane component (``UP``, ``RIGHT``, anything tilted)
  cannot be expressed as a screen-plane angle, so the rotation is a real 3D
  Rodrigues rotation applied to the point arrays every frame -- exactly what
  manim's ``Mobject.rotate`` does, so the final state matches CE point for
  point.  RTM's renderer projects with ``z`` dropped in a 2D scene (that is
  also what manim's Cairo renderer does), so an in-plane axis shows up as
  the expected foreshortening (``axis=UP`` squashes x by ``cos(angle)``),
  and in a ``ThreeDScene`` the viewport projection picks up the resulting
  ``z`` for free.
* ``about_point`` wins; when it is ``None`` and ``about_edge`` is given the
  pivot is ``mobject.get_critical_point(about_edge)``; when both are ``None``
  the renderer's own default (the mobject's centre) is left in place.
"""

from real_time_manim.animations.base import (
    Animation,
    set_anim_opacity,
    get_anim_opacity,
    get_anim_rotation,
    set_anim_rotation,
)
import numpy as np
import math
from real_time_manim.rate_functions import _smooth
from real_time_manim.utils.paths import rotation_matrix

OUT = np.array([0.0, 0.0, 1.0])


def _unit_axis(axis):
    """``axis`` normalised; the zero vector falls back to ``OUT`` (manim's rule)."""
    if axis is None:
        return OUT.copy()
    vec = np.array(axis, dtype=float).reshape(3)
    norm = np.linalg.norm(vec)
    if norm < 1e-12:
        return OUT.copy()
    return vec / norm


def _axis_is_parallel_to_z(axis):
    vec = _unit_axis(axis)
    return abs(vec[0]) < 1e-9 and abs(vec[1]) < 1e-9


class Rotate(Animation):
    def __init__(
        self,
        mobject,
        angle=math.pi,
        axis=OUT,
        about_point=None,
        about_edge=None,
        run_time=1.0,
        rate_func=None,
        **kwargs,
    ):
        self.rot_angle = angle
        self.axis = axis
        self.about_point = about_point
        self.about_edge = about_edge
        self._is_3d = not _axis_is_parallel_to_z(axis)
        self._axis_sign = 1.0 if _unit_axis(axis)[2] > 0 else -1.0
        super().__init__(mobject, run_time=run_time, rate_func=rate_func or _smooth, **kwargs)

    # -- pivot / axis helpers -------------------------------------------------

    def _resolve_pivot(self):
        """CE rule: ``about_point`` > ``about_edge`` critical point > ``None``.

        ``None`` means "let the renderer use the mobject's own centre", which
        is what ``Mobject.rotate``/CE's ``Rotate`` fall back to.
        """
        if self.about_point is not None:
            return np.array(self.about_point, dtype=float)
        if self.about_edge is not None:
            return np.array(
                self.mobject.get_critical_point(self.about_edge), dtype=float
            )
        return None

    def _begin_3d(self):
        """Non-z axis: snapshot start points and prepare the per-frame 3D bake.

        Any rotation the mobject still carries in the draw-time channel (a
        previous ``Rotate`` persists through ``set_anim_rotation``) is folded
        into the points first, otherwise zeroing the channel would throw that
        rotation away.
        """
        mob = self.mobject
        if self._pivot is None:
            self._pivot = np.array(mob.get_center(), dtype=float)
        # Primitive senders (``_send_square`` / ``_send_circle`` / ...) rebuild
        # the shape from class attributes and ignore the baked geometry, so the
        # mobject has to ride the point path while the points are being
        # rewritten.  It stays on it after ``finish``: the final rotation lives
        # in the points for good (same convention as ``Transform``).
        mob._transforming = True
        mob._rotation_3d = True
        entries = []
        for sub in mob.family_members_with_points():
            pts = getattr(sub, "points", None)
            if pts is None or len(pts) == 0:
                continue
            start = np.array(pts, dtype=float, copy=True)
            carried = get_anim_rotation(sub)
            if abs(carried) > 1e-12:
                about = getattr(sub, "_rotation_about_point", None)
                about = sub.get_center() if about is None else np.array(about, dtype=float)
                start = (start - about) @ rotation_matrix(carried, OUT).T + about
            set_anim_rotation(sub, 0.0)
            entries.append([sub, start])
        # A container's own channel rotation reaches the children at draw time
        # (paint passes it down as ``sub_rot``); fold it in about the container
        # pivot so zeroing the channel does not make it disappear.  The
        # container's OWN points (when it has any) were folded above with the
        # same pivot, so they must not be folded twice.
        root_carried = get_anim_rotation(mob)
        if abs(root_carried) > 1e-12:
            root_about = getattr(mob, "_rotation_about_point", None)
            root_about = (mob.get_center() if root_about is None
                          else np.array(root_about, dtype=float))
            rz = rotation_matrix(root_carried, OUT)
            for entry in entries:
                if entry[0] is mob:
                    continue
                entry[1] = (entry[1] - root_about) @ rz.T + root_about
        set_anim_rotation(mob, 0.0)
        self._start_points = entries

    def _interpolate_3d(self, alpha):
        rot = rotation_matrix(self.rot_angle * alpha, self.axis)
        about = self._pivot
        for sub, start in self._start_points:
            pts = getattr(sub, "points", None)
            if pts is None or len(pts) == 0:
                continue
            sub.points = (start - about) @ rot.T + about

    # -- animation API --------------------------------------------------------

    def begin(self, t):
        super().begin(t)
        self._start_rotation = get_anim_rotation(self.mobject)
        self._pivot = self._resolve_pivot()
        self._wrote_pivot = False
        # Bake the rotation into the point arrays when the axis leaves the z
        # line OR when an EXPLICIT pivot was given.  The draw-time channel
        # (`set_anim_rotation` + `_rotation_about_point`) is only honoured by
        # the primitive senders (`_send_square` orbits the centre about the
        # pivot); `_send_polygon` and the generic point path rotate the
        # vertices about the shape's OWN centre and ignore the pivot, so an
        # explicit `about_point`/`about_edge` came out as a spin-in-place.
        # Measured on wiki ``03-动画/移动与旋转/01-旋转-rotate.mp4``
        # (``Rotate(sq, 2*PI/3, about_point=pivot)``): RTM's blue-Square
        # centroid stayed at (327, 182) for the WHOLE clip while CE's orbited
        # the pivot and settled at (196, 106) -- mean|d| 1.87.  A default
        # pivot (the mobject's own centre) needs no orbit, so it keeps the
        # cheap channel path.
        self._bake = self._is_3d or self._pivot is not None
        if self._bake:
            self._begin_3d()
        else:
            if self._pivot is not None:
                self.mobject._rotation_about_point = self._pivot.copy()
                self._wrote_pivot = True

    def finish(self):
        super().finish()
        if hasattr(self.mobject, "_rotation_3d"):
            del self.mobject._rotation_3d
        if self._wrote_pivot and hasattr(self.mobject, "_rotation_about_point"):
            del self.mobject._rotation_about_point

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        if self._bake:
            self._interpolate_3d(alpha)
        else:
            # ``IN`` (negative z) reverses the on-screen turning direction.
            current = self._start_rotation + self.rot_angle * self._axis_sign * alpha
            set_anim_rotation(self.mobject, current)
