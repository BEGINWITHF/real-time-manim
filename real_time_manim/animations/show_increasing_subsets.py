# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np


class ShowIncreasingSubsets(Animation):
    def __init__(self, group, int_func=None, run_time=2.0, **kwargs):
        self.all_submobs = list(group.submobjects)
        self.int_func = int_func
        for mobj in self.all_submobs:
            set_anim_opacity(mobj, 0.0)
            try:
                mobj.fill_rgbas[:, 3] = 0.0
            except Exception:
                pass
            try:
                mobj.stroke_rgbas[:, 3] = 0.0
            except Exception:
                pass
        super().__init__(group, run_time=run_time, **kwargs)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        n_submobs = len(self.all_submobs)
        if self.int_func is not None:
            index = int(self.int_func(alpha * n_submobs))
        else:
            index = int(np.floor(alpha * n_submobs))
        self.update_submobject_list(index)

    def _set_mobj_visible(self, mobj):
        set_anim_opacity(mobj, 1.0)
        try:
            mobj.fill_rgbas[:, 3] = 1.0
        except Exception:
            pass
        try:
            mobj.stroke_rgbas[:, 3] = 1.0
        except Exception:
            pass

    def _set_mobj_hidden(self, mobj):
        set_anim_opacity(mobj, 0.0)
        try:
            mobj.fill_rgbas[:, 3] = 0.0
        except Exception:
            pass
        try:
            mobj.stroke_rgbas[:, 3] = 0.0
        except Exception:
            pass

    def update_submobject_list(self, index):
        for mobj in self.all_submobs[:index]:
            self._set_mobj_visible(mobj)
        for mobj in self.all_submobs[index:]:
            self._set_mobj_hidden(mobj)

    def finish(self):
        super().finish()
        for mobj in self.all_submobs:
            self._set_mobj_visible(mobj)
