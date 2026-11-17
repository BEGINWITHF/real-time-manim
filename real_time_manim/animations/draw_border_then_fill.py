# This might not cause a bug or issue, check for other place first --TT Noted
from manim import Text as _Text

from real_time_manim.animations.base import Animation, resolve_mobject
from real_time_manim.animations.grow_arrow import color_to_rgb
from real_time_manim.rate_functions import _double_smooth


class DrawBorderThenFill(Animation):
    def __init__(self, mobject=None, run_time=2.0, stroke_width=2, stroke_color=None,
                 rate_func=_double_smooth, introducer=True, **kwargs):
        mobject = resolve_mobject(mobject, kwargs, "DrawBorderThenFill")
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
        # ``stroke_width`` / ``stroke_color`` used to be stored and never read:
        # the reveal drew with the mobject's own stroke, so
        # ``DrawBorderThenFill(circle, stroke_width=24)`` looked exactly like
        # the default.  CE builds an ``outline`` copy with
        # ``set_stroke(color=self.get_stroke_color(sm), width=self.stroke_width)``
        # and reveals the fill over it; keep the original width/colour here and
        # apply/restore the requested ones around the animation.
        self._orig_style = {}
        self._stroke_rgb = (color_to_rgb(self.stroke_color)
                            if self.stroke_color is not None else None)
        for tm in self._point_targets(self.mobject):
            self._orig_fill[id(tm)] = tm.get_fill_opacity() if hasattr(tm, 'get_fill_opacity') else 1.0
            self._orig_stroke[id(tm)] = tm.get_stroke_opacity() if hasattr(tm, 'get_stroke_opacity') else 1.0
            try:
                rgbas = tm.stroke_rgbas
                rgb = rgbas[:, :3].copy() if (rgbas is not None and len(rgbas) > 0) else None
            except Exception:
                rgb = None
            self._orig_style[id(tm)] = (getattr(tm, 'stroke_width', None), rgb)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        self._apply_two_phase(alpha)

    def _apply_two_phase(self, alpha):
        mob = self.mobject
        # CE staggers ``Write`` over every point-bearing member of the family
        # (`Animation.interpolate_mobject` -> `get_all_families_zipped`), not
        # over the top-level submobjects.  For a Text those two lists are the
        # same (one member per letter), but a MathTex's glyphs live one level
        # deeper inside its MathTexPart: staggering only the part (and setting
        # ``_letter_alphas`` on the MathTex, which routes it through the TEXT
        # writer) made every glyph of a formula draw at the same instant while
        # CE writes them one after another.
        targets = self._point_targets(mob)
        num_targets = len(targets)
        alpha_by_id = {}
        if not targets:
            self._apply_single_two_phase(mob, alpha)
        else:
            for i, target in enumerate(targets):
                sub_alpha = self.get_sub_alpha(alpha, i, num_targets)
                alpha_by_id[id(target)] = sub_alpha
                self._apply_single_two_phase(target, sub_alpha)
        # Text's fast sender (`_send_text_write`) fades each glyph from this
        # map, and only a Text root may carry it: setting it on a MathTex sends
        # the whole formula down the text writer, which loses the per-glyph
        # progress set above.  Arm every Text in the subtree, not only a Text
        # that happens to be the animation's own mobject: inside a VGroup a
        # Text sent without the map falls back to `_send_vmobject`, whose
        # `_is_text` branch skips the synthesized write outline, so the line
        # only faded its fill in and never showed the hand-writing stroke.
        for text_root in self._text_roots(mob):
            letters = getattr(text_root, 'submobjects', None) or ()
            text_root._letter_alphas = {
                i: alpha_by_id.get(id(letter), 0.0)
                for i, letter in enumerate(letters)}

    @staticmethod
    def _text_roots(mob):
        """Every ``Text`` root in the subtree, in family order."""
        getter = getattr(mob, 'get_family', None)
        nodes = getter() if callable(getter) else [mob]
        return [node for node in nodes if isinstance(node, _Text)]

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

    def _apply_stroke_style(self, mob):
        """Apply the animation's ``stroke_width`` / ``stroke_color`` override."""
        # Text/LaTeX glyphs carry no stroke of their own; the renderer builds a
        # synthesized outline from `_write_active` and fades it through
        # `stroke_point_alpha`.  Overriding the width here would give the glyph
        # a real, fully opaque stroke that never fades (tests/test_write_latex.py
        # caught exactly that), so leave the synthesized path alone.
        if (getattr(mob, '_write_active', False)
                and float(getattr(mob, 'stroke_width', 0) or 0) <= 0):
            return
        if self.stroke_width is not None:
            try:
                mob.stroke_width = float(self.stroke_width)
            except Exception:
                pass
        if self._stroke_rgb is not None:
            try:
                rgbas = mob.stroke_rgbas
                if rgbas is not None and len(rgbas) > 0:
                    rgbas[:, 0] = self._stroke_rgb[0]
                    rgbas[:, 1] = self._stroke_rgb[1]
                    rgbas[:, 2] = self._stroke_rgb[2]
            except Exception:
                pass

    def _restore_stroke_style(self, mob):
        orig = self._orig_style.get(id(mob))
        if not orig:
            return
        width, rgb = orig
        try:
            if width is not None:
                mob.stroke_width = width
        except Exception:
            pass
        if rgb is not None:
            try:
                rgbas = mob.stroke_rgbas
                if rgbas is not None and len(rgbas) > 0:
                    rgbas[:, :3] = rgb
            except Exception:
                pass

    def _apply_single_two_phase(self, mob, alpha):
        border_frac = 0.5
        targets = self._point_targets(mob)
        # Tag the point-bearing leaves so the renderer knows a Write is in
        # progress: it keeps the synthesized outline stroke visible (fading out)
        # while the fill fades in, avoiding a dip where neither is shown.
        for tm in targets:
            tm._write_active = True
            self._apply_stroke_style(tm)
        # CE's two phases (`ShowPartial.interpolate_submobject`): the whole
        # first half draws the outline at full opacity with NO fill, and the
        # second half ramps the fill 0 -> 1 while the outline recedes.  Starting
        # the fill at 30 % of the glyph (the old behaviour) dimmed the outline
        # while a third of it was still being drawn, which read as a grey,
        # softer stroke than CE's crisp white one.
        if alpha < border_frac:
            # Border phase: stroke draws progressively, fill stays off.
            stroke_alpha = self.rate_func(alpha / border_frac)
            mob._vulkan_progress = stroke_alpha
            fill_alpha = 0.0
        else:
            # Fill phase: outline complete, fill fades in over the whole half.
            mob._vulkan_progress = 1.0
            fill_alpha = min(1.0, (alpha - border_frac) / (1.0 - border_frac))
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
            self._restore_stroke_style(tm)
            self._set_fo(tm, self._orig_fill.get(id(tm), 1.0))
            self._set_so(tm, self._orig_stroke.get(id(tm), 1.0))
            if hasattr(tm, '_write_active'):
                del tm._write_active
