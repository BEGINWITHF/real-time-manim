from real_time_manim.animations.base import Animation, get_anim_rotation, set_anim_rotation
import numpy as np
import math
from manim import OUT
from real_time_manim.rate_functions import _linear


def _rotate_vectors(vectors, angle, axis):
    axis = np.array(axis, dtype=float)
    norm = np.linalg.norm(axis)
    if norm < 1e-12:
        return vectors.copy()
    axis = axis / norm
    c = math.cos(angle)
    s = math.sin(angle)
    dot = vectors[:, 0] * axis[0] + vectors[:, 1] * axis[1] + vectors[:, 2] * axis[2]
    cross_x = axis[1] * vectors[:, 2] - axis[2] * vectors[:, 1]
    cross_y = axis[2] * vectors[:, 0] - axis[0] * vectors[:, 2]
    cross_z = axis[0] * vectors[:, 1] - axis[1] * vectors[:, 0]
    result = np.zeros_like(vectors)
    result[:, 0] = vectors[:, 0] * c + cross_x * s + axis[0] * dot * (1 - c)
    result[:, 1] = vectors[:, 1] * c + cross_y * s + axis[1] * dot * (1 - c)
    result[:, 2] = vectors[:, 2] * c + cross_z * s + axis[2] * dot * (1 - c)
    return result


class Rotating(Animation):
    def __init__(
        self,
        mobject,
        angle=2 * math.pi,
        axis=None,
        about_point=None,
        about_edge=None,
        run_time=5.0,
        rate_func=None,
        **kwargs,
    ):
        self.rot_angle = angle
        self._axis = axis
        self._about_point = about_point
        self._about_edge = about_edge
        super().__init__(mobject, run_time=run_time, rate_func=rate_func or _linear, **kwargs)

    def _should_bake(self):
        """Bake the rotation into the point arrays, per frame.

        True for a non-z axis (a real 3D rotation) AND for any rotation about
        an EXPLICIT pivot (``about_point``/``about_edge``).  The draw-time
        channel (``set_anim_rotation`` + ``_rotation_about_point``) is only
        honoured by the primitive senders (``_send_square`` orbits the centre
        about the pivot); ``_send_polygon`` and the generic point path rotate
        the vertices about the shape's OWN centre and ignore the pivot, so an
        explicit pivot came out as a spin-in-place.  Measured on wiki
        ``03-动画/移动与旋转/01-旋转-rotating_edge.mp4``
        (``Rotating(tri, 90*DEGREES, about_edge=UP)``): RTM's teal-Triangle
        centroid crawled to (248.9, 193.6) while CE's orbited the top-edge
        hinge to (276.8, 165.7) -- mean|d| 1.21.  A default pivot (own centre)
        needs no orbit and keeps the cheap channel path.
        """
        if self._rotation_about_point is not None:
            return True
        if self._axis is None:
            return False
        return not np.allclose(np.array(self._axis, dtype=float), OUT)

    def begin(self, t):
        super().begin(t)
        self._start_rotation = get_anim_rotation(self.mobject)
        pt = self._about_point
        if pt is None and self._about_edge is not None:
            pt = self.mobject.get_critical_point(self._about_edge)
        if pt is not None:
            self._rotation_about_point = np.array(pt, dtype=float)
            self.mobject._rotation_about_point = self._rotation_about_point.copy()
        else:
            self._rotation_about_point = None
            # manim's own Rotating has no default pivot: `interpolate_mobject`
            # calls `mobject.rotate(...)` with about_point=None, and
            # `Mobject.rotate` then uses `get_center()`.  The bake path used
            # ORIGIN instead, so `Rotating(arrow, 180*DEGREES, axis=IN)` swung
            # the arrow around the frame centre (off-screen) where CE spins it
            # in place -- wiki 03-动画/移动与旋转/01-旋转-rotating_axis.
            self._bake_about = np.array(self.mobject.get_center(), dtype=float)
        if self._should_bake():
            self.mobject._rotation_3d = True
            # The bake rewrites the point arrays every frame, and the primitive
            # senders (`_send_square` / `_send_circle` / ...) rebuild the shape
            # from class attributes and would ignore the baked geometry --
            # exactly the rule `animations.rotate` follows.  The final rotation
            # stays in the points, so the flag stays on.
            self.mobject._transforming = True
            self._start_points = {}
            for sub in self.mobject.family_members_with_points():
                if hasattr(sub, 'points') and len(sub.points) > 0:
                    self._start_points[id(sub)] = sub.points.copy()
                    set_anim_rotation(sub, 0.0)
            # A container's own channel rotation is not in the family walk;
            # zero it so the sender does not re-apply it over the baked points.
            set_anim_rotation(self.mobject, 0.0)
        else:
            self.mobject._rotation_3d = False

    def finish(self):
        super().finish()
        # The per-frame bake already leaves the points at the final rotation, so
        # the fallback bake below must be skipped whenever `_should_bake()` held
        # -- otherwise it would rotate the finished points a SECOND time.
        if not self._should_bake() and self._rotation_about_point is not None:
            pivot = np.array(self._rotation_about_point, dtype=float)
            rot = get_anim_rotation(self.mobject)
            if abs(rot) > 1e-12:
                c = math.cos(rot)
                s = math.sin(rot)
                rot_matrix = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
                for sub in self.mobject.family_members_with_points():
                    if hasattr(sub, 'points') and len(sub.points) > 0:
                        sub.points = (sub.points - pivot) @ rot_matrix.T + pivot
            set_anim_rotation(self.mobject, 0.0)
        if hasattr(self.mobject, '_rotation_about_point'):
            del self.mobject._rotation_about_point
        if hasattr(self.mobject, '_rotation_3d'):
            del self.mobject._rotation_3d

    def _project_3d_to_2d(self, points):
        proj = np.zeros_like(points)
        proj[:, 0] = points[:, 0]
        proj[:, 1] = points[:, 1]
        proj[:, 2] = 0.0
        return proj

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        angle = self.rot_angle * alpha

        if self._should_bake():
            # `axis` defaults to OUT for a pivot-only rotation (Rotating's
            # `axis=None`), which is the in-plane hinge CE rotates about.
            axis_raw = self._axis if self._axis is not None else OUT
            axis = np.array(axis_raw, dtype=float)
            axis_norm = np.linalg.norm(axis)
            if axis_norm < 1e-12:
                return
            axis = axis / axis_norm
            about = self._rotation_about_point
            if about is None:
                about = getattr(self, '_bake_about', None)
            if about is None:
                about = np.zeros(3)
            for sub in self.mobject.family_members_with_points():
                sid = id(sub)
                if sid not in self._start_points:
                    continue
                if not hasattr(sub, 'points'):
                    continue
                pts = self._start_points[sid]
                rotated = _rotate_vectors(pts - about, angle, axis)
                projected = self._project_3d_to_2d(rotated)
                sub.points = projected + about
        else:
            current = self._start_rotation + angle
            set_anim_rotation(self.mobject, current)
