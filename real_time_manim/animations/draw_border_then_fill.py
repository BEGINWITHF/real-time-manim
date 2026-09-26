# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation
from real_time_manim.rate_functions import _double_smooth


class DrawBorderThenFill(Animation):
    def __init__(self, mobject, run_time=2.0, stroke_width=2, stroke_color=None,
                 rate_func=_double_smooth, introducer=True, **kwargs):
        super().__init__(mobject, run_time=run_time, rate_func=rate_func,
                         introducer=introducer, **kwargs)
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color

    def _point_targets(self, mob):
        """Return the mobjects that actually carry fill/stroke geometry.

        For plain VMobjects this is just the mobject itself.  For LaTeX
        (MathTexPart -> VMobjectFromSVGPath glyph leaves) the fill lives on the
        nested point-bearing descendants, so we must style those too —
        otherwise Write's "outline then fill" reveal never happens (the glyphs
        stay fully filled for the whole animation).
        """
        if hasattr(mob, 'family_members_with_points'):
            fam = list(mob.family_members_with_points())
            if fam:
                return fam
        return [mob]

    def begin(self, t):
        super().begin(t)
        self._starting_mobject = self.mobject.copy() if hasattr(self.mobject, 'copy') else self.mobject
        # Capture original fill/stroke opacity for every point-bearing target
        # (container + LaTeX glyph leaves) so the two-phase reveal can restore
        # them correctly.
        self._orig_fill = {}
        self._orig_stroke = {}
        for tm in self._point_targets(self.mobject):
            self._orig_fill[id(tm)] = tm.get_fill_opacity() if hasattr(tm, 'get_fill_opacity') else 1.0
            self._orig_stroke[id(tm)] = tm.get_stroke_opacity() if hasattr(tm, 'get_stroke_opacity') else 1.0

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        self._apply_two_phase(alpha)

    def _apply_two_phase(self, alpha):
        mob = self.mobject
        has_subs = hasattr(mob, 'submobjects') and mob.submobjects
        if has_subs:
            num_subs = len(mob.submobjects)
            for i in range(num_subs):
                sub = mob.submobjects[i]
                sub_alpha = self.get_sub_alpha(alpha, i, num_subs)
                self._apply_single_two_phase(sub, sub_alpha)
            mob._letter_alphas = {i: self.get_sub_alpha(alpha, i, num_subs) for i in range(num_subs)}
        else:
            self._apply_single_two_phase(mob, alpha)

    def _set_fo(self, mob, value):
        if hasattr(mob, 'fill_rgbas') and mob.fill_rgbas is not None and len(mob.fill_rgbas) > 0:
            mob.fill_rgbas[:, 3] = value
        elif hasattr(mob, 'set'):
            mob.set(fill_opacity=value)

    def _set_so(self, mob, value):
        if hasattr(mob, 'stroke_rgbas') and mob.stroke_rgbas is not None and len(mob.stroke_rgbas) > 0:
            mob.stroke_rgbas[:, 3] = value
        elif hasattr(mob, 'set'):
            mob.set(stroke_opacity=value)

    def _apply_single_two_phase(self, mob, alpha):
        border_frac = 0.5
        targets = self._point_targets(mob)
        # Tag the point-bearing leaves so the renderer knows a Write is in
        # progress: it keeps the synthesized outline stroke visible (fading out)
        # while the fill fades in, avoiding a dip where neither is shown.
        for tm in targets:
            tm._write_active = True
        # Fill fades in at the SAME rate as the title's text-write
        # (_send_text_write): fill_alpha = max(0, (x - 0.3) * 2.0), i.e. it
        # starts fading in at 30% of the glyph's animation and is fully opaque
        # by 80% — not lagging until the very end.
        fill_alpha = max(0.0, min(1.0, (alpha - 0.3) * 2.0))
        if alpha < border_frac:
            # Border phase: stroke draws progressively, fill still ramping in
            # from 30% (overlaps with the tail of the stroke, like the title).
            stroke_alpha = self.rate_func(alpha / border_frac)
            mob._vulkan_progress = stroke_alpha
        else:
            # Fill phase: stroke fully drawn (renderer fades it out), fill
            # continues to full opacity by 80%.
            mob._vulkan_progress = 1.0
        for tm in targets:
            self._set_fo(tm, self._orig_fill.get(id(tm), 1.0) * fill_alpha)
            self._set_so(tm, self._orig_stroke.get(id(tm), 1.0))

    def finish(self):
        super().finish()
        mob = self.mobject
        if hasattr(mob, 'submobjects') and mob.submobjects:
            mob._letter_alphas = {i: 1.0 for i in range(len(mob.submobjects))}
        else:
            mob._vulkan_progress = 1.0
        # Restore original fill/stroke opacity on every point-bearing target.
        for tm in self._point_targets(mob):
            self._set_fo(tm, self._orig_fill.get(id(tm), 1.0))
            self._set_so(tm, self._orig_stroke.get(id(tm), 1.0))
            if hasattr(tm, '_write_active'):
                del tm._write_active
