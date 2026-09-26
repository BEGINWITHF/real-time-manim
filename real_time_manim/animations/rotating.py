from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity, get_anim_rotation, set_anim_rotation
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

    def _is_3d_axis(self):
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
        if self._is_3d_axis():
            self.mobject._rotation_3d = True
            self._start_points = {}
            for sub in self.mobject.family_members_with_points():
                if hasattr(sub, 'points') and len(sub.points) > 0:
                    self._start_points[id(sub)] = sub.points.copy()
                    set_anim_rotation(sub, 0.0)
        else:
            self.mobject._rotation_3d = False

    def finish(self):
        super().finish()
        if not self._is_3d_axis() and self._rotation_about_point is not None:
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

        if self._is_3d_axis():
            axis = np.array(self._axis, dtype=float)
            axis_norm = np.linalg.norm(axis)
            if axis_norm < 1e-12:
                return
            axis = axis / axis_norm
            about = self._rotation_about_point
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
