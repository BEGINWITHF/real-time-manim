# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np
from real_time_manim.rate_functions import _smooth, _double_smooth
from real_time_manim.animations.succession import Succession
from real_time_manim.animations.wait import Wait


class Blink(Succession):
    def __init__(self, mobject, time_on=0.5, time_off=0.5, blinks=1,
                 hide_at_end=False, **kwargs):
        self.blink_mobject = mobject
        self.hide_at_end = hide_at_end

        animations = []
        for _ in range(blinks):
            animations.append(Wait(time_on))
            animations.append(Wait(time_off))

        if not hide_at_end:
            animations.append(Wait(time_on))

        total_time = sum(a.run_time for a in animations)
        kwargs.pop('run_time', None)
        super().__init__(*animations, run_time=total_time, **kwargs)
        self._blink_mobject = mobject
        self._blink_time_on = time_on
        self._blink_time_off = time_off
        self._blink_blinks = blinks

    def _set_visible(self):
        set_anim_opacity(self._blink_mobject, 1.0)
        try:
            self._blink_mobject.fill_rgbas[:, 3] = 1.0
        except Exception:
            pass
        try:
            self._blink_mobject.stroke_rgbas[:, 3] = 1.0
        except Exception:
            pass

    def _set_hidden(self):
        set_anim_opacity(self._blink_mobject, 0.0)
        try:
            self._blink_mobject.fill_rgbas[:, 3] = 0.0
        except Exception:
            pass
        try:
            self._blink_mobject.stroke_rgbas[:, 3] = 0.0
        except Exception:
            pass

    def begin(self, t):
        super().begin(t)
        self._set_visible()

    def interpolate(self, t):
        elapsed = t - self.start_time
        total = self.run_time
        if total <= 0:
            return

        time_on = self._blink_time_on
        time_off = self._blink_time_off
        cycle = time_on + time_off
        pos_in_cycle = elapsed % cycle

        if pos_in_cycle < time_on:
            self._set_visible()
        else:
            self._set_hidden()

    def finish(self):
        super().finish()
        if self.hide_at_end:
            self._set_hidden()
        else:
            self._set_visible()
