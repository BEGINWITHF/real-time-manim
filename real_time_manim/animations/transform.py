from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np
from real_time_manim.utils.paths import path_along_arc, straight_path


class Transform(Animation):
    def __init__(self, mobject, target_mobject, replace_mobject_with_target_in_scene=False,
                 run_time=1.0, path_func=None, path_arc=0.0, path_arc_axis=None,
                 path_arc_centers=None, **kwargs):
        self.target_mobject = target_mobject
        self.replace_mobject_with_target_in_scene = replace_mobject_with_target_in_scene
        self._path_arc = path_arc
        self._path_arc_axis = np.array(path_arc_axis) if path_arc_axis is not None else np.array([0.0, 0.0, 1.0])
        self._path_arc_centers = path_arc_centers
        self._path_func = path_func
        super().__init__(mobject, run_time=run_time, **kwargs)

    @property
    def path_func(self):
        if self._path_func is not None:
            return self._path_func
        if abs(self._path_arc) < 1e-9:
            return straight_path
        return path_along_arc(self._path_arc, self._path_arc_axis)

    def begin(self, t):
        super().begin(t)
        self._starting_mobject = self.mobject.copy()
        self._target_copy = self.target_mobject.copy()
        try:
            self._starting_mobject.align_data(self._target_copy)
            self.mobject.align_data(self._target_copy)
        except Exception:
            pass
        set_anim_opacity(self.mobject, 1.0)
        self._set_transforming(self.mobject, True)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        pf = self.path_func
        try:
            mob_fam = self.mobject.family_members_with_points()
            start_fam = self._starting_mobject.family_members_with_points()
            target_fam = self._target_copy.family_members_with_points()
            for m, s, tgt in zip(mob_fam, start_fam, target_fam):
                m.interpolate(s, tgt, alpha, pf)
        except Exception:
            pass

    def finish(self):
        super().finish()
        set_anim_opacity(self.mobject, 1.0)
        try:
            mob_fam = self.mobject.family_members_with_points()
            target_fam = self.target_mobject.family_members_with_points()
            for m, tgt in zip(mob_fam, target_fam):
                m.set_points(tgt.get_points().copy())
        except Exception:
            try:
                self.mobject.set_points(self.target_mobject.get_points().copy())
            except Exception:
                pass
        if not self.replace_mobject_with_target_in_scene:
            set_anim_opacity(self.target_mobject, 0.0)
        self._set_transforming(self.mobject, True)
        self._set_transforming(self.target_mobject, False)

    @staticmethod
    def _set_transforming(mob, val):
        Transform._set_transforming_impl(mob, val, set())

    @staticmethod
    def _set_transforming_impl(mob, val, seen):
        mid = id(mob)
        if mid in seen:
            return
        seen.add(mid)
        mob._transforming = val
        if hasattr(mob, 'family_members_with_points'):
            for sub in mob.family_members_with_points():
                Transform._set_transforming_impl(sub, val, seen)
        elif hasattr(mob, 'submobjects'):
            for sub in mob.submobjects:
                Transform._set_transforming_impl(sub, val, seen)

    def clean_up_from_scene(self, scene):
        if self.replace_mobject_with_target_in_scene:
            if self.mobject in scene.mobjects:
                scene.remove(self.mobject)
            if self.target_mobject not in scene.mobjects:
                scene.add(self.target_mobject)
            set_anim_opacity(self.target_mobject, 1.0)
            self._set_transforming(self.target_mobject, False)
        else:
            self._set_transforming(self.mobject, True)
            self._set_transforming(self.target_mobject, False)
