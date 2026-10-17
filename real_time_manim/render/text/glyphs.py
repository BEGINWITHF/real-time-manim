"""Per-glyph text senders.

`Text`/`MathTex` glyphs are drawn from their bitmap or from their bezier
outline, with the write/type animation channels applied."""

import ctypes
from real_time_manim.render.util import manim_to_screen
from real_time_manim.animations import get_anim_opacity


class GlyphMixin:

    def _stroke_rgb_with_background(self, mob, sr, sg, sb):
        """Stroke colour of ``mob``, honouring a VectorField background image.

        The `VectorField` family (`StreamLines`, `ArrowVectorField`, ...) keeps
        its stroke rgba **WHITE** and lets the Cairo renderer tint every stroke
        pixel from the mobject's background image
        (`VMobject.color_using_background_image` ->
        `BackgroundColoredVMobjectDisplayer.display`).  RTM cannot do per-pixel
        tinting, so it substitutes the image's mean colour (see
        `real_time_manim.background_color`).

        Every stroke-reading branch of `_send_vmobject` has to ask for the
        colour through here: the SHORT-PATH branch (`n < 8`, one or two cubic
        segments) read `get_stroke_rgbas()` on its own and painted those lines
        white.  Measured on `VectorFieldsAndTrackers`: the two stream lines
        that happen to be a single cubic segment -- lines 0 and 34, the short
        ticks at the field's lower-left and upper-right -- came out pure white
        (253,255,253) against CE's red (~255,129,122), while every longer line
        was already correct.
        """
        if getattr(mob, 'get_background_image', None) is None:
            return sr, sg, sb
        try:
            from real_time_manim.background_color import background_image_rgb
            _bg = background_image_rgb(mob)
        except Exception:
            _bg = None
        if _bg is None:
            return sr, sg, sb
        return _bg

    def _send_transformed_text(self, mob, w, h, alpha=1.0):
        try:
            c = mob.get_color()
            base_r, base_g, base_b = round(float(c[0]) * 255), round(float(c[1]) * 255), round(float(c[2]) * 255)
        except Exception:
            base_r, base_g, base_b = 255, 255, 255
        if base_r == 0 and base_g == 0 and base_b == 0:
            base_r, base_g, base_b = 255, 255, 255

        for sub in mob.submobjects:
            sub_a = get_anim_opacity(sub)
            if sub_a <= 0:
                continue
            try:
                pts = sub.get_points() if hasattr(sub, 'get_points') else sub.points
                if len(pts) < 4:
                    continue
                num_segs = len(pts) // 4
                if num_segs == 0:
                    continue
                sr = int(base_r * sub_a * alpha)
                sg = int(base_g * sub_a * alpha)
                sb = int(base_b * sub_a * alpha)
                flat = []
                for seg_i in range(num_segs):
                    for pt_i in range(4):
                        p = pts[seg_i * 4 + pt_i]
                        vx, vy = manim_to_screen(p[0], p[1], w, h, p[2])
                        flat.append(vx)
                        flat.append(vy)
                        flat.append(0.0)
                arr = (ctypes.c_float * len(flat))(*flat)
                self.dll.AddBezierPath(
                    arr, num_segs * 4,
                    sr, sg, sb, 3.0,
                    sr, sg, sb, 1.0,
                    1.0, 1, 1, alpha,
                    sr, sg, sb, 0.0, 0.0, 0.0, 0.0,
                )
            except Exception as e:
                import traceback
                print('[ERROR] _send_transformed_text: ' + str(e))
                traceback.print_exc()

    def _glyph_rgb(self, sub, default):
        """A glyph's own colour, or ``default`` when it carries none.

        manim writes a glyph's colour into its rgba arrays: that is where
        ``t2c`` puts a markup colour and where an animation writes the colour
        it interpolates towards (``.animate.set_color`` runs through
        ``Mobject.interpolate_color``).  ``Text.get_color()`` is a different
        thing entirely -- the container's own ``color`` attribute, which manim
        leaves at ``#000000`` for a ``Text`` until somebody calls
        ``set_color`` on it.  Painting every glyph from that turned a *written*
        Text pure white: ``Write`` leaves ``_letter_alphas`` set, so the whole
        line stayed on this writer afterwards and lost both its ``t2c`` colour
        and its final ``set_color(YELLOW)`` (PlainTextAndMarkup: 0 saturated
        pixels in the line where CE has 5295, still white where CE is yellow).
        """
        for getter in ("get_fill_rgbas", "get_stroke_rgbas"):
            try:
                stops = list(getattr(sub, getter)())
            except Exception:
                continue
            if not stops:
                continue
            n = float(len(stops))
            r = sum(float(s[0]) for s in stops) / n
            g = sum(float(s[1]) for s in stops) / n
            b = sum(float(s[2]) for s in stops) / n
            if r != 0.0 or g != 0.0 or b != 0.0:
                return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))
            # Data that is there and is BLACK is an EXPLICIT black, not
            # "unset": `Text.to_original_color()` resets every glyph through
            # `set_color(Text.color)` and `Text.color` is `#000000`, so CE
            # paints the word black -- i.e. it disappears.  Falling through to
            # `default` repainted it with the container's colour, which for a
            # Text is white (the wiki report "「color」消失被错误显示成了变白",
            # 02-Mobject通用/05-样式与颜色).  Only a glyph with no rgba data at
            # all reaches `default`.
            return 0, 0, 0
        return default

    def _send_text_write(self, mob, letter_alphas, w, h, alpha=1.0,
                         parent_offset=None):
        try:
            c = mob.get_color()
            base_r, base_g, base_b = round(float(c[0]) * 255), round(float(c[1]) * 255), round(float(c[2]) * 255)
        except Exception:
            base_r, base_g, base_b = 255, 255, 255
        if base_r == 0 and base_g == 0 and base_b == 0:
            base_r, base_g, base_b = 255, 255, 255
        base = (base_r, base_g, base_b)
        # `Write` leaves `_letter_alphas` on the mobject for good (see
        # `_glyph_rgb`), so every later frame of that Text comes through this
        # writer -- which has to carry the channels `_send_vmobject` applies to
        # a glyph (vulkan_text.py:537/542), or a Written word disagrees with an
        # unwritten row-mate by the whole baseline shift and refuses to grow.
        # A `Transform`'s `align_data` also pads the shorter Text with copies of
        # its LAST glyph, giving extra submobjects no entry of their own: the
        # old 0.0 default drew them invisible where CE draws the line in full.
        default_alpha = letter_alphas.get(len(letter_alphas) - 1, 1.0)
        grow_scale = getattr(mob, '_grow_scale', 1.0)
        grow_pt = getattr(mob, '_grow_point', None)
        for i, sub in enumerate(mob.submobjects):
            sub_alpha = letter_alphas.get(i, default_alpha)
            if sub_alpha <= 0.001:
                continue

            pts = sub.get_points()
            # A glyph is a stack of 4-point bezier segments, and native
            # `AddBezierPath` reads them four at a time (`n = (n // 4) * 4`
            # below), so anything with fewer than four points contributes no
            # segment at all.  The old `< 8` test also threw away every
            # 4-point glyph -- a period, a bare apostrophe, the dot of an
            # `i` -- which `Write` then drew as nothing where CE inks the
            # full stop.
            if len(pts) < 4:
                continue

            # Approach-A baseline shift, tagged on the characters at draw time
            # by `vulkan_bind._send_impl` -- same rule, same source as the
            # `_send_vmobject` glyph branch.
            b_dy = float(getattr(sub, '_baseline_dy', 0.0) or 0.0)
            # The parent's shift is in manim units and applies to the whole
            # glyph, so it lands before the projection (see the note at the
            # call site).
            if parent_offset is not None:
                off_x = float(parent_offset[0])
                off_y = float(parent_offset[1])
            else:
                off_x = off_y = 0.0
            flat = []
            for p in pts:
                px, py = float(p[0]) + off_x, float(p[1]) + off_y
                if grow_scale != 1.0 and grow_pt is not None:
                    px = grow_pt[0] + (px - grow_pt[0]) * grow_scale
                    py = grow_pt[1] + (py - grow_pt[1]) * grow_scale
                sx, sy = manim_to_screen(px, py + b_dy, w, h, p[2])
                flat.append(sx)
                flat.append(sy)
                flat.append(0.0)

            n = len(flat) // 3
            n = (n // 4) * 4
            arr = (ctypes.c_float * len(flat))(*flat)

            stroke_progress = min(1.0, sub_alpha * 2.5)
            stroke_fade = max(0.0, 1.0 - max(0.0, (sub_alpha - 0.4) * 2.5))
            fill_alpha = max(0.0, (sub_alpha - 0.3) * 2.0)

            # Handwriting outline keeps the text's own colour; as the fill
            # completes it recedes INWARD (width shrinks 2px -> 0) instead of
            # popping off, so the letter ends with no sudden border
            # disappearance and no residual ring.
            sr, sg, sb = self._glyph_rgb(sub, base)
            stroke_width = 2.0 * stroke_fade
            show_stroke = 1 if stroke_width > 0.001 else 0

            self.dll.AddBezierPath(
                arr, n,
                sr, sg, sb, stroke_width,
                sr, sg, sb, fill_alpha,
                stroke_progress, show_stroke, 1 if fill_alpha > 0 else 0, alpha,
                sr, sg, sb, 0.0, 0.0, 0.0, 0.0,
            )

    def _send_text_bitmap(self, mob, w, h, alpha=1.0):
        base_r, base_g, base_b = 255, 255, 255
        fade_scale = getattr(mob, '_fade_scale', 1.0)
        cx, cy = mob.get_center()[0], mob.get_center()[1]
        try:
            c = mob.get_color()
            r, g, b = int(c[0] * 255), int(c[1] * 255), int(c[2] * 255)
            if r > 0 or g > 0 or b > 0:
                base_r, base_g, base_b = r, g, b
        except Exception:
            pass
        if base_r == 255 and base_g == 255 and base_b == 255:
            try:
                for fm in mob.family_members_with_points():
                    srgba = fm.stroke_rgbas
                    if len(srgba) > 0:
                        sr, sg, sb = float(srgba[0][0]), float(srgba[0][1]), float(srgba[0][2])
                        if sr > 0 or sg > 0 or sb > 0:
                            base_r, base_g, base_b = int(sr * 255), int(sg * 255), int(sb * 255)
                            break
            except Exception:
                pass
        if base_r == 0 and base_g == 0 and base_b == 0:
            try:
                srgbas = mob.get_stroke_rgbas()
                if len(srgbas) > 0:
                    sr, sg, sb = float(srgbas[0][0]), float(srgbas[0][1]), float(srgbas[0][2])
                    base_r, base_g, base_b = int(sr * 255), int(sg * 255), int(sb * 255)
            except Exception:
                pass
        if base_r == 0 and base_g == 0 and base_b == 0:
            try:
                frgbas = mob.get_fill_rgbas()
                if len(frgbas) > 0:
                    fr, fg, fb = float(frgbas[0][0]), float(frgbas[0][1]), float(frgbas[0][2])
                    base_r, base_g, base_b = int(fr * 255), int(fg * 255), int(fb * 255)
            except Exception:
                pass
        if base_r == 0 and base_g == 0 and base_b == 0:
            base_r, base_g, base_b = 255, 255, 255

        text_str = mob.text if hasattr(mob, 'text') else str(mob)
        font_size = mob._font_size if hasattr(mob, '_font_size') else 48.0
        font_px = font_size * (h / 480.0)
        try:
            bottom_y = mob.get_bottom()[1]
            cy = bottom_y
        except Exception:
            cy = mob.get_center()[1]
        sx, sy = manim_to_screen(cx, cy, w, h)
        self.dll.AddText(sx, sy, base_r, base_g, base_b, font_px, 1.0, text_str.encode('utf-8'), alpha)


    def _send_text_stroke(self, mob, a, w, h, parent_offset=None):
        if not hasattr(mob, 'family_members_with_points'):
            return
        for fm in mob.family_members_with_points():
            sw_attr = fm.get_stroke_width() if hasattr(fm, 'get_stroke_width') else 0
            if sw_attr <= 0:
                continue
            self._send_vmobject(fm, a, w, h, parent_offset)
