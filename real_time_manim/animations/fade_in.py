# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np


class FadeIn(Animation):
    def __init__(
        self,
        *mobjects,
        shift=None,
        target_position=None,
        scale=1.0,
        run_time=1.0,
        **kwargs,
    ):
        self.fade_shift = shift
        self.target_position = target_position
        self.fade_scale = scale
        self._start_positions = []
        # CE accepts the single-mobject spelling; ``*mobjects`` holds the
        # positional form.  RTM used to feed ``mobject=`` into ``**kwargs``,
        # together with ``mobjects[0] if mobjects else None``, producing
        # "got multiple values for argument 'mobject'".
        if not mobjects and "mobject" in kwargs:
            mobjects = (kwargs.pop("mobject"),)
        elif mobjects and "mobject" in kwargs:
            raise TypeError("FadeIn() got multiple values for argument 'mobject'")
        super().__init__(mobjects[0] if mobjects else None, run_time=run_time, **kwargs)
        self.mobjects = list(mobjects)

    def begin(self, t):
        super().begin(t)
        self._start_positions = []
        self._orig_points = {}
        for mob in self.mobjects:
            set_anim_opacity(mob, 0.0)
            self._start_positions.append(mob.get_center().copy())
            if self.fade_scale != 1.0:
                # manim CE fades in from ``mobject.copy().scale(scale_factor)``
                # (``fading.py::_Fade._create_faded_mobject``), i.e. the whole
                # family INCLUDING a plain shape's own points, then pointwise
                # interpolates back to full size.  The old filter
                # ``if fm is not mob`` captured only the *descendants*, so a
                # leaf VMobject -- Circle/Square/Dot/Triangle, whose
                # ``family_members_with_points()`` is just ``[mob]`` -- got an
                # EMPTY list and ``scale=`` was silently ignored.
                #
                # Measured (no GPU): ``FadeIn(Circle(radius=0.68), scale=0.5)``
                # kept width == 1.3600 for the whole run in RTM, while CE went
                # 0.6800 -> 0.8500 -> 1.0200 -> 1.1900 -> 1.3600 at alpha
                # 0/0.25/0.5/0.75/1.  On the wiki page
                # 03-动画/通用/02-play与wait参数 ("shift down被展示成了up",
                # idx15) that alone accounts for the whole residual: the
                # circle region's mean luma tracked alpha exactly (0.101 vs
                # 0.104 linear at alpha 0.10) instead of CE's
                # opacity*area curve alpha*(0.5+0.5*alpha)^2 (0.283 measured
                # vs 0.28 predicted at alpha 0.5).
                #
                # Containers (Text/VGroup) have no points of their own, so
                # ``family_members_with_points()`` returns their glyph/shape
                # leaves and their behaviour is unchanged by dropping the
                # filter; members without points are skipped so an empty
                # assignment never happens.
                self._orig_points[id(mob)] = [
                    (fm, fm.get_points().copy())
                    for fm in mob.family_members_with_points()
                    if len(getattr(fm, "points", ())) > 0
                ]

    def interpolate(self, t):
        if getattr(self, '_use_alpha', False):
            alpha = float(t)
        else:
            alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
            alpha = max(0.0, min(1.0, alpha))
            if self.reverse_rate_function:
                alpha = 1.0 - alpha
            alpha = self.rate_func(alpha)

        for i, mob in enumerate(self.mobjects):
            set_anim_opacity(mob, alpha)

            if self.fade_scale != 1.0:
                target_scale = self.fade_scale + (1.0 - self.fade_scale) * alpha
                if id(mob) in self._orig_points:
                    cx, cy = self._start_positions[i][0], self._start_positions[i][1]
                    for fm, orig in self._orig_points[id(mob)]:
                        scaled = orig.copy()
                        scaled[:, 0] = cx + (orig[:, 0] - cx) * target_scale
                        scaled[:, 1] = cy + (orig[:, 1] - cy) * target_scale
                        fm.points = scaled

            if self.fade_shift is not None:
                # manim: `_Fade._create_faded_mobject(fadeIn=True)` shifts the
                # STARTING copy by ``-shift`` (``direction_modifier = -1``), so
                # the mobject begins at ``final - shift`` and travels BY ``shift``
                # into place.  ``FadeIn(m, shift=DOWN)`` therefore slides DOWN
                # into view.  Adding ``+shift`` here started it BELOW and moved
                # it up -- the wiki report "shift=DOWN 被展示成了 up"
                # (03-动画/通用/02-play与wait参数).  At alpha == 1 the term is
                # exactly 0, so the guard that used to skip the final frame also
                # stopped leaving a residual offset behind.
                mob.move_to(self._start_positions[i] - self.fade_shift * (1.0 - alpha))

            if self.target_position is not None and i < len(self._start_positions):
                if hasattr(self.target_position, 'get_center'):
                    target = self.target_position.get_center()
                else:
                    target = np.array(self.target_position, dtype=float)
                original = self._start_positions[i]
                mob.move_to(target + (original - target) * alpha)

    def finish(self):
        super().finish()
        for mob in self.mobjects:
            set_anim_opacity(mob, 1.0)
            for fm, orig in self._orig_points.get(id(mob), []):
                fm.points = orig.copy()

    def get_all_mobjects(self):
        return list(self.mobjects)
