# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.grow_arrow import GrowArrow
from real_time_manim.animations.base import Animation


class GrowFromEdge(GrowArrow):
    def __init__(self, mobject, edge, point_color=None, run_time=1.0, **kwargs):
        self.edge = edge
        super().__init__(mobject, point_color=point_color, run_time=run_time, **kwargs)

    def begin(self, t):
        Animation.begin(self, t)
        mob = self.mobject
        self._grow_point = mob.get_critical_point(self.edge)

        if hasattr(mob, 'get_fill_rgbas'):
            try:
                frgbas = mob.get_fill_rgbas()
                if len(frgbas) > 0:
                    self._orig_fill = [float(frgbas[0][i]) for i in range(4)]
            except Exception:
                pass
        if hasattr(mob, 'get_stroke_rgbas'):
            try:
                srgbas = mob.get_stroke_rgbas()
                if len(srgbas) > 0:
                    self._orig_stroke = [float(srgbas[0][i]) for i in range(4)]
            except Exception:
                pass
        if hasattr(mob, 'stroke_width'):
            self._orig_stroke_width = mob.stroke_width

        mob._grow_scale = 0.0
        mob._grow_point = self._grow_point
        if self.point_color:
            self._pc = (float(self.point_color[0]), float(self.point_color[1]), float(self.point_color[2]))
            if hasattr(mob, 'fill_rgbas') and len(mob.fill_rgbas) > 0:
                mob.fill_rgbas[:, 0] = self._pc[0]
                mob.fill_rgbas[:, 1] = self._pc[1]
                mob.fill_rgbas[:, 2] = self._pc[2]
            if hasattr(mob, 'stroke_rgbas') and len(mob.stroke_rgbas) > 0:
                mob.stroke_rgbas[:, 0] = self._pc[0]
                mob.stroke_rgbas[:, 1] = self._pc[1]
                mob.stroke_rgbas[:, 2] = self._pc[2]
