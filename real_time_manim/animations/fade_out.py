# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import (Animation, release_hidden_channels,
                                             set_anim_opacity, get_anim_opacity)
import numpy as np


class FadeOut(Animation):
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
        if not mobjects and "mobject" in kwargs:
            mobjects = (kwargs.pop("mobject"),)
        elif mobjects and "mobject" in kwargs:
            raise TypeError("FadeOut() got multiple values for argument 'mobject'")
        super().__init__(mobjects[0] if mobjects else None, run_time=run_time, **kwargs)
        self.mobjects = list(mobjects)
        self.remover = True
        self._start_positions = []

    def begin(self, t):
        super().begin(t)
        self._start_positions = []
        self._orig_points = {}
        for mob in self.mobjects:
            self._park_opacity(mob, 1.0)
            self._start_positions.append(mob.get_center().copy())
            if self.fade_scale != 1.0:
                # Same rule as ``FadeIn.begin`` -- see the long comment there.
                # manim CE's ``FadeOut`` fades to ``mobject.copy().scale(scale)``
                # (``fading.py``), so the WHOLE family shrinks, including a
                # plain shape's own points.  The old ``if fm is not mob`` filter
                # dropped the mobject itself, so a leaf VMobject (Circle,
                # Square, Dot, ...) captured an empty list and ``scale=`` was
                # silently ignored -- measured: ``FadeOut(Circle(r=0.68),
                # scale=0.5)`` kept width 1.3600 end to end, while CE goes
                # 1.3600 -> 1.1900 -> 1.0200 -> 0.8500 -> 0.6800.
                # Containers (Text/VGroup) have no points of their own, so
                # dropping the filter leaves them unchanged.
                self._orig_points[id(mob)] = [
                    (fm, fm.get_points().copy())
                    for fm in mob.family_members_with_points()
                    if len(getattr(fm, "points", ())) > 0
                ]

    def _park_opacity(self, mob, value):
        """Record ``value`` as ``mob``'s animated opacity.

        The paint walk multiplies opacity top-down the scene tree, so the
        value has to land on a node that walk actually visits.  Parking on
        ``mob`` itself is right whenever ``mob`` is (or sits inside) the
        scene tree; subclasses that fade a DETACHED wrapper override this to
        also cover the nodes the tree reaches through the wrapper's real
        parents.
        """
        set_anim_opacity(mob, value)

    def interpolate(self, t):
        if getattr(self, '_use_alpha', False):
            alpha = float(t)
        else:
            alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
            alpha = max(0.0, min(1.0, alpha))
            if self.reverse_rate_function:
                alpha = 1.0 - alpha
            alpha = self.rate_func(alpha)
        opacity = 1.0 - alpha

        for i, mob in enumerate(self.mobjects):
            self._park_opacity(mob, opacity)

            if self.fade_scale != 1.0:
                target_scale = 1.0 + (self.fade_scale - 1.0) * alpha
                if id(mob) in self._orig_points:
                    cx, cy = self._start_positions[i][0], self._start_positions[i][1]
                    for fm, orig in self._orig_points[id(mob)]:
                        scaled = orig.copy()
                        scaled[:, 0] = cx + (orig[:, 0] - cx) * target_scale
                        scaled[:, 1] = cy + (orig[:, 1] - cy) * target_scale
                        fm.points = scaled

            if self.fade_shift is not None and alpha > 0.0:
                mob.move_to(self._start_positions[i] + self.fade_shift * alpha)

            if self.target_position is not None and i < len(self._start_positions):
                if hasattr(self.target_position, 'get_center'):
                    target = self.target_position.get_center()
                else:
                    target = np.array(self.target_position, dtype=float)
                original = self._start_positions[i]
                mob.move_to(original + (target - original) * alpha)

    def finish(self):
        super().finish()
        for mob in self.mobjects:
            for fm, orig in self._orig_points.get(id(mob), []):
                fm.points = orig.copy()
            # A fade-out is a remover: CE leaves the mobject itself untouched
            # and only takes it out of the scene, so a later `add`/`FadeIn` of
            # the same mobject shows it whole.  Parking the opacity registry at
            # 0.0 (which outlives the animation) made every later draw of it
            # invisible.
            release_hidden_channels(mob)
