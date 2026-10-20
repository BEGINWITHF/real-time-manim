# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity, color_to_rgb
import numpy as np


class GrowArrow(Animation):
    def __init__(self, arrow, point_color=None, run_time=1.0, **kwargs):
        self.point_color = point_color
        self._orig_fill = None
        self._orig_stroke = None
        self._orig_stroke_width = None
        super().__init__(arrow, run_time=run_time, **kwargs)

    @staticmethod
    def _members(mob):
        try:
            return list(mob.get_family())
        except Exception:
            return [mob]

    def begin(self, t):
        super().begin(t)
        mob = self.mobject
        # A VGroup (or any container without its own points) has no
        # ``get_start``: manim raises "Cannot call Mobject.get_start for a
        # Mobject with no points".  CE's GrowFromCenter/VGroup works because
        # manim's GrowFromPoint only measures the mobject's centre; grow from
        # the centre for those, which is what GrowFromCenter overrides to
        # anyway (and GrowFromEdge/GrowFromPoint override explicitly).
        try:
            self._grow_point = mob.get_start()
        except Exception:
            self._grow_point = mob.get_center()
        self._orig_fill = {}
        self._orig_stroke = {}
        # The arrowHEAD is a submobject (`Arrow.tip`).  Only `mob`'s own rgbas
        # were stored/lerped, and `set_color` on a Line does not reach the tip,
        # so `GrowArrow(arrow, point_color=RED)` left the head GOLD while the
        # shaft went red -> gold (wiki 03-动画/生长出现/01b-箭头与旋入: the
        # last frame still had a red tip where CE has the whole arrow gold).
        # Keep every family member's colours and lerp them all.
        for sub in self._members(mob):
            try:
                frgbas = sub.get_fill_rgbas()
                if len(frgbas) > 0:
                    self._orig_fill[id(sub)] = np.array(frgbas, dtype=float)
            except Exception:
                pass
            try:
                srgbas = sub.get_stroke_rgbas()
                if len(srgbas) > 0:
                    self._orig_stroke[id(sub)] = np.array(srgbas, dtype=float)
            except Exception:
                pass
        if hasattr(mob, 'stroke_width'):
            self._orig_stroke_width = mob.stroke_width

        mob._grow_scale = 0.0
        mob._grow_point = self._grow_point
        if self.point_color:
            self._pc = color_to_rgb(self.point_color)
            for sub in self._members(mob):
                self._set_rgb(sub, self._pc)

    @staticmethod
    def _set_rgb(sub, pc):
        try:
            if hasattr(sub, 'fill_rgbas') and len(sub.fill_rgbas) > 0:
                sub.fill_rgbas[:, 0] = pc[0]
                sub.fill_rgbas[:, 1] = pc[1]
                sub.fill_rgbas[:, 2] = pc[2]
        except Exception:
            pass
        try:
            if hasattr(sub, 'stroke_rgbas') and len(sub.stroke_rgbas) > 0:
                sub.stroke_rgbas[:, 0] = pc[0]
                sub.stroke_rgbas[:, 1] = pc[1]
                sub.stroke_rgbas[:, 2] = pc[2]
        except Exception:
            pass

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        mob = self.mobject
        mob._grow_scale = alpha
        if not self.point_color:
            return
        for sub in self._members(mob):
            self._lerp_to_orig(sub, self._orig_fill.get(id(sub)),
                               self._orig_stroke.get(id(sub)), alpha)

    def _lerp_to_orig(self, sub, orig_fill, orig_stroke, alpha):
        pc = self._pc
        if orig_fill is not None and hasattr(sub, 'fill_rgbas') and len(sub.fill_rgbas) > 0:
            for k in range(3):
                sub.fill_rgbas[:, k] = pc[k] + (orig_fill[:, k] - pc[k]) * alpha
        if orig_stroke is not None and hasattr(sub, 'stroke_rgbas') and len(sub.stroke_rgbas) > 0:
            for k in range(3):
                sub.stroke_rgbas[:, k] = pc[k] + (orig_stroke[:, k] - pc[k]) * alpha

    def finish(self):
        super().finish()
        mob = self.mobject
        if hasattr(mob, '_grow_scale'):
            del mob._grow_scale
        if hasattr(mob, '_grow_point'):
            del mob._grow_point
        for sub in self._members(mob):
            of = self._orig_fill.get(id(sub)) if self._orig_fill else None
            os_ = self._orig_stroke.get(id(sub)) if self._orig_stroke else None
            try:
                if of is not None and hasattr(sub, 'fill_rgbas') and len(sub.fill_rgbas) > 0:
                    sub.fill_rgbas[:, 0] = of[:, 0]
                    sub.fill_rgbas[:, 1] = of[:, 1]
                    sub.fill_rgbas[:, 2] = of[:, 2]
            except Exception:
                pass
            try:
                if os_ is not None and hasattr(sub, 'stroke_rgbas') and len(sub.stroke_rgbas) > 0:
                    sub.stroke_rgbas[:, 0] = os_[:, 0]
                    sub.stroke_rgbas[:, 1] = os_[:, 1]
                    sub.stroke_rgbas[:, 2] = os_[:, 2]
            except Exception:
                pass
        if self._orig_stroke_width is not None:
            try:
                mob.stroke_width = self._orig_stroke_width
            except Exception:
                pass
