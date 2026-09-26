# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np
from real_time_manim.rate_functions import _smooth


class UntypeWithCursor(Animation):
    def __init__(self, text, cursor, buff=0.1, keep_cursor_y=True,
                 leave_cursor_on=True, time_per_char=0.1, run_time=None, **kwargs):
        self.cursor = cursor
        self.buff = buff
        self.keep_cursor_y = keep_cursor_y
        self.leave_cursor_on = leave_cursor_on
        self.time_per_char = time_per_char
        if run_time is None:
            n_chars = len(text.submobjects) if hasattr(text, 'submobjects') else max(1, len(str(text)))
            run_time = max(0.1, time_per_char) * n_chars
        self.all_submobs = list(text.submobjects) if hasattr(text, 'submobjects') else []
        self._orig_fo = {}
        self._orig_so = {}
        for mobj in self.all_submobs:
            try:
                self._orig_fo[id(mobj)] = mobj.fill_rgbas[:, 3].copy()
            except Exception:
                self._orig_fo[id(mobj)] = 1.0
            try:
                self._orig_so[id(mobj)] = mobj.stroke_rgbas[:, 3].copy()
            except Exception:
                self._orig_so[id(mobj)] = 1.0
        Animation.__init__(self, text, run_time=run_time, **kwargs)

    def begin(self, t):
        self.y_cursor = self.cursor.get_center()[1]
        self.initial_cursor_y = self.y_cursor
        for mobj in self.all_submobs:
            set_anim_opacity(mobj, 1.0)
            if hasattr(mobj, 'family_members_with_points'):
                for fm in mobj.family_members_with_points():
                    set_anim_opacity(fm, 1.0)
            try:
                orig = self._orig_fo.get(id(mobj))
                if orig is not None:
                    mobj.fill_rgbas[:, 3] = orig
                else:
                    mobj.fill_rgbas[:, 3] = 1.0
            except Exception:
                pass
            try:
                orig = self._orig_so.get(id(mobj))
                if orig is not None:
                    mobj.stroke_rgbas[:, 3] = orig
                else:
                    mobj.stroke_rgbas[:, 3] = 1.0
            except Exception:
                pass
        if self.all_submobs:
            last = self.all_submobs[-1]
            self.cursor.move_to(last.get_center())
            self.cursor.shift(np.array([1, 0, 0]) * (last.get_width() / 2 + self.buff * 4))
            if self.keep_cursor_y:
                self.cursor.move_to([
                    self.cursor.get_center()[0],
                    self.initial_cursor_y,
                    0
                ])
        set_anim_opacity(self.cursor, 1.0)
        try:
            self.cursor.fill_rgbas[:, 3] = 1.0
        except Exception:
            pass
        try:
            self.cursor.stroke_rgbas[:, 3] = 1.0
        except Exception:
            pass
        Animation.begin(self, t)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        alpha = self.rate_func(alpha)
        n = len(self.all_submobs)
        index = n - int(np.floor(alpha * n))
        index = max(0, min(index, n))
        self.update_submobject_list(index)

    def update_submobject_list(self, index):
        for i, mobj in enumerate(self.all_submobs):
            if i < index:
                set_anim_opacity(mobj, 1.0)
                if hasattr(mobj, 'family_members_with_points'):
                    for fm in mobj.family_members_with_points():
                        set_anim_opacity(fm, 1.0)
                try:
                    orig = self._orig_fo.get(id(mobj))
                    if orig is not None:
                        mobj.fill_rgbas[:, 3] = orig
                    else:
                        mobj.fill_rgbas[:, 3] = 1.0
                except Exception:
                    pass
                try:
                    orig = self._orig_so.get(id(mobj))
                    if orig is not None:
                        mobj.stroke_rgbas[:, 3] = orig
                    else:
                        mobj.stroke_rgbas[:, 3] = 1.0
                except Exception:
                    pass
            else:
                set_anim_opacity(mobj, 0.0)
                if hasattr(mobj, 'family_members_with_points'):
                    for fm in mobj.family_members_with_points():
                        set_anim_opacity(fm, 0.0)
                try:
                    mobj.fill_rgbas[:, 3] = 0.0
                except Exception:
                    pass
                try:
                    mobj.stroke_rgbas[:, 3] = 0.0
                except Exception:
                    pass

        if index > 0:
            last_visible = self.all_submobs[index - 1]
            last_center = last_visible.get_center()
            self.cursor.move_to(last_center)
            self.cursor.shift(np.array([1, 0, 0]) * (last_visible.get_width() / 2 + self.buff * 4))

        if self.keep_cursor_y:
            self.cursor.move_to([
                self.cursor.get_center()[0],
                self.initial_cursor_y,
                0
            ])
        set_anim_opacity(self.cursor, 1.0)
        try:
            self.cursor.fill_rgbas[:, 3] = 1.0
        except Exception:
            pass
        try:
            self.cursor.stroke_rgbas[:, 3] = 1.0
        except Exception:
            pass

    def finish(self):
        Animation.finish(self)
        for mobj in self.all_submobs:
            set_anim_opacity(mobj, 0.0)
            if hasattr(mobj, 'family_members_with_points'):
                for fm in mobj.family_members_with_points():
                    set_anim_opacity(fm, 0.0)
            try:
                mobj.fill_rgbas[:, 3] = 0.0
            except Exception:
                pass
            try:
                mobj.stroke_rgbas[:, 3] = 0.0
            except Exception:
                pass
        if self.all_submobs:
            first = self.all_submobs[0]
            self.cursor.move_to(first.get_center())
        if self.keep_cursor_y:
            self.cursor.move_to([
                self.cursor.get_center()[0],
                self.initial_cursor_y,
                0
            ])
        if self.leave_cursor_on:
            set_anim_opacity(self.cursor, 1.0)
            try:
                self.cursor.fill_rgbas[:, 3] = 1.0
            except Exception:
                pass
            try:
                self.cursor.stroke_rgbas[:, 3] = 1.0
            except Exception:
                pass
        else:
            set_anim_opacity(self.cursor, 0.0)
            try:
                self.cursor.fill_rgbas[:, 3] = 0.0
            except Exception:
                pass
            try:
                self.cursor.stroke_rgbas[:, 3] = 0.0
            except Exception:
                pass
