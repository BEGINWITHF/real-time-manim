# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np
from manim import Text, VGroup
from real_time_manim.rate_functions import _smooth


class TextDecimalNumber(Text):
    _value_cache = {}

    def __init__(self, number=0, font_size=48, font="Times New Roman", num_decimal_places=2, **kwargs):
        self.number = number
        self.num_decimal_places = num_decimal_places
        self._font_size = font_size
        self._font = font
        cache_key = (font_size, font)
        TextDecimalNumber._ensure_cache(cache_key)
        fmt = f"{{:.{num_decimal_places}f}}"
        super().__init__(fmt.format(number), font_size=font_size, font=font, **kwargs)

    @classmethod
    def _ensure_cache(cls, cache_key):
        if cache_key not in cls._value_cache:
            cls._value_cache[cache_key] = {}

    def set_value(self, number):
        self.number = number
        center = self.get_center()
        fmt = f"{{:.{self.num_decimal_places}f}}"
        s = fmt.format(number)
        cache_key = (self._font_size, self._font)
        cache = TextDecimalNumber._value_cache.get(cache_key)
        if cache is None:
            TextDecimalNumber._ensure_cache(cache_key)
            cache = TextDecimalNumber._value_cache[cache_key]
        cached = cache.get(s)
        if cached is None:
            cached = Text(s, font_size=self._font_size, font=self._font)
            cache[s] = cached
        clone = cached.copy()
        self.submobjects = clone.submobjects
        self.move_to(center)
        return self

    def update_submobject_list(self, index):
        pass

    @classmethod
    def _build_cache(cls, font_size):
        cache = {}
        for ch in "0123456789.-+":
            cache[ch] = Text(ch, font_size=font_size)
        cls._digit_cache[font_size] = cache

    def update_submobject_list(self, index):
        for mobj in self.all_submobs[:index]:
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
        for mobj in self.all_submobs[index:]:
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
        else:
            self.cursor.move_to(self.all_submobs[0].get_center())

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
            try:
                self.cursor.stroke_rgbas[:, 3] = 0.0
            except Exception:
                pass
