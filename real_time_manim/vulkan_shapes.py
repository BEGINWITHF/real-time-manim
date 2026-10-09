import ctypes
import math
import numpy as np
from real_time_manim.vulkan_util import manim_to_screen, rotate_point, get_fill_rgb, get_fill_rgb_raw, get_stroke_rgb, get_stroke_w, get_opacity, point_path_bounds, shaded_fill_rgb
from real_time_manim.animations import get_anim_rotation


class ShapeMixin:
    def _color(self, mob, alpha=1.0):
        return get_fill_rgb(mob, alpha)

    def _fill_color(self, mob):
        return get_fill_rgb_raw(mob)

    def _fill_color_lit(self, mob):
        """`_fill_color` with manim's per-face 3D light shading (see vulkan_util)."""
        lit = shaded_fill_rgb(mob)
        return self._fill_color(mob) if lit is None else lit

    def _stroke_color(self, mob):
        return get_stroke_rgb(mob)

    @staticmethod
    def _visible_frame_height():
        """How many manim units the camera is currently showing vertically.

        Any *size* written in manim units (a stroke width, a Dot's radius) has to
        be converted with the pixels-per-unit of the frame that is actually on
        screen.  Positions already take that route -- ``manim_to_screen`` ->
        ``Viewport.project`` scales by the visible frame height -- so a size that
        assumed the default 8-unit frame drew a mobject that did not follow a
        zooming camera while its own position did.

        Measured on ``FollowingGraphCamera`` (``camera.frame.animate.scale(0.5)``,
        frame height 8 -> 4): manim CE doubles every dot on screen, 22 px ->
        44 px at 1080p, growing over the whole zoom-in and shrinking again over
        ``Restore``; with the default 8 RTM kept the disc at a constant 22 px for
        the entire zoom-in and the whole restore and snapped between the two
        sizes at the play boundaries.

        No published viewport means a plain ``Scene`` with the default fixed
        frame, so non-camera scenes render exactly as before.
        """
        try:
            from real_time_manim.camera_state import get_viewport, DEFAULT_FRAME_HEIGHT
        except Exception:                          # pragma: no cover - no camera_state
            return 8.0
        try:
            viewport = get_viewport()
            if viewport is not None:
                return float(viewport.height) or 8.0
        except Exception:                          # pragma: no cover - defensive
            pass
        return DEFAULT_FRAME_HEIGHT

    def _stroke_width(self, mob):
        sw_manim = get_stroke_w(mob)
        # Convert manim stroke_width to pixels
        # Manim shader: v_stroke_width = 0.01 * stroke_width * frame_scale
        # Geometry shader offsets curve by v_stroke_width in world space
        # World space to pixels: multiply by (pixel_height / frame_height).
        # The frame height is the *visible* one: a moving/zoomed camera narrows the
        # view (MovingCameraScene zoomed to height 4.1 measured here), and manim
        # scales strokes with it -- using the default 8 drew them half as thick
        # (CameraFamilyScene luma 1.12 vs CE 1.82).
        h = getattr(self, 'win_h', 800)
        return sw_manim * 0.01 * (h / self._visible_frame_height())

    @staticmethod
    def _stroke_layers(px, alpha):
        """(native width, alpha) pairs that composite to exactly `px` of ink.

        Native renders a quad of ``width + 1`` px (draw_line.c:
        ``half_thick = thick * 0.5f + 0.5f``) and native widths are integers,
        so an exact sub-pixel width needs an integer core plus symmetric
        fractional edges: a ``core``-wide quad at full alpha laid over a
        ``core + 1``-wide quad at alpha ``frac`` composites to
        ``floor(px) + frac = px``.

        Passing ``round(px)`` straight through instead drew
        ``round(px) + 1`` px -- 2 px where manim draws 1.2 px for the default
        stroke_width=2 at 480p, a 67% overdraw.  Measured with an independent
        probe (tests/test_stroke_width.py is the fast version, stroke_probe.py
        the on-video one):

            BracesAndLabels            ink x1.27  lit>55 x1.63  missing  87 px
            ApplyTransformAnimations   ink x1.23  lit>55 x1.68  missing   0 px

        ``missing = 0`` means CE's ink is a strict subset of RTM's: the same
        strokes, drawn wider, never in the wrong place -- which is compare_auto's
        ``width`` bucket.  ``de309df`` had already moved ``_send_line`` and
        ``_send_arrow`` over to this rule; the closed-shape senders had not.

        A single quad at a compensating alpha is NOT equivalent: it covers the
        next integer width up and every one of those pixels crosses an ink
        threshold (measured: ``ThreeDRotationProbe``'s excess coverage jumping
        0.054 -> 0.192, all of it within 2 px of CE's strokes).
        """
        px = float(px)
        if px <= 0:
            return []
        core = int(math.floor(px + 1e-6))
        frac = px - core
        if core < 1:
            # thinner than one pixel: a single 1 px quad at the exact alpha
            return [(0, alpha * min(1.0, px))]
        layers = []
        if frac > 0.01:
            layers.append((core, alpha * min(1.0, frac)))
        layers.append((core - 1, alpha))
        return layers

    def _emit_stroke(self, x1, y1, x2, y2, px, r, g, b, alpha):
        """Draw one straight stroke of exactly ``px`` pixels of ink.

        Layers are pushed in the order ``_stroke_layers`` returns them, so the
        opaque core lands on top of the fractional edge (the order the coverage
        above assumes).
        """
        for _w, _a in self._stroke_layers(px, alpha):
            self.dll.AddLine(x1, y1, x2, y2, _w, r, g, b, _a)

    def _rotate_point(self, x, y, cx, cy, angle):
        return rotate_point(x, y, cx, cy, angle)

    def _send_square(self, mob, a, w, h, rot, parent_offset=None):
        cx, cy, cz = mob.get_center()
        if parent_offset is not None:
            cx += parent_offset[0]; cy += parent_offset[1]
        about = getattr(mob, '_rotation_about_point', None)
        if about is not None:
            neg_rot = -rot
            dx, dy = cx - about[0], cy - about[1]
            c, sn = math.cos(neg_rot), math.sin(neg_rot)
            cx = about[0] + dx * c - dy * sn
            cy = about[1] + dx * sn + dy * c
        grow_scale = getattr(mob, '_grow_scale', 1.0)
        grow_pt = getattr(mob, '_grow_point', None)
        if grow_scale != 1.0 and grow_pt is not None:
            cx = grow_pt[0] + (cx - grow_pt[0]) * grow_scale
            cy = grow_pt[1] + (cy - grow_pt[1]) * grow_scale
        sx, sy = manim_to_screen(cx, cy, w, h, cz)
        scale = h / 8.0
        half = mob.side_length / 2.0 * scale * grow_scale
        try:
            fo = float(mob.fill_rgbas[:, 3].max())
        except Exception:
            fo = get_opacity(mob, 'fill', 1.0)
        try:
            so = float(mob.stroke_rgbas[:, 3].max())
        except Exception:
            so = get_opacity(mob, 'stroke', 1.0)
        progress = getattr(mob, '_vulkan_progress', 1.0)
        if fo <= 0 and so <= 0:
            return
        if progress <= 0:
            return
        fr, fg, fb = self._fill_color(mob)
        self.dll.AddRect(sx, sy, half, half, rot, fr, fg, fb, 0, 0, 0, 0.0, progress, a * fo)
        if so > 0 and self._stroke_width(mob) > 0:
            # `stroke_width = 0` means no stroke even though the rgba alpha is
            # 1.0 (same trap as `_send_polygon`'s fill-only shapes).
            cr, cg, cb = self._stroke_color(mob)
            # The stroke opacity rides the ALPHA, not the colour: native blends
            # straight-alpha (colour*alpha + dst*(1-alpha)), so baking `so` in
            # hard-replaced the background and a stroke over a non-black backdrop
            # stayed black while it faded in (same trap _send_polygon documents).
            a = a * so
            sw = self._stroke_width(mob)
            tl = self._rotate_point(sx - half, sy - half, sx, sy, rot)
            tr = self._rotate_point(sx + half, sy - half, sx, sy, rot)
            brc = self._rotate_point(sx + half, sy + half, sx, sy, rot)
            bl = self._rotate_point(sx - half, sy + half, sx, sy, rot)
            perimeter = 8.0 * half
            drawn = perimeter * progress
            edges = [
                (tr, tl, 2.0 * half),
                (tl, bl, 2.0 * half),
                (bl, brc, 2.0 * half),
                (brc, tr, 2.0 * half),
            ]
            remaining = drawn
            for (x0, y0), (x1, y1), length in edges:
                if remaining <= 0:
                    break
                if remaining >= length:
                    self._emit_stroke(x0, y0, x1, y1, sw, cr, cg, cb, a)
                    remaining -= length
                else:
                    frac = remaining / length
                    ex = x0 + (x1 - x0) * frac
                    ey = y0 + (y1 - y0) * frac
                    self._emit_stroke(x0, y0, ex, ey, sw, cr, cg, cb, a)
                    remaining = 0

    def _send_rectangle(self, mob, a, w, h, rot, parent_offset=None):
        cx, cy, cz = mob.get_center()
        if parent_offset is not None:
            cx += parent_offset[0]; cy += parent_offset[1]
        about = getattr(mob, '_rotation_about_point', None)
        if about is not None:
            neg_rot = -rot
            dx, dy = cx - about[0], cy - about[1]
            c, sn = math.cos(neg_rot), math.sin(neg_rot)
            cx = about[0] + dx * c - dy * sn
            cy = about[1] + dx * sn + dy * c
        grow_scale = getattr(mob, '_grow_scale', 1.0)
        grow_pt = getattr(mob, '_grow_point', None)
        if grow_scale != 1.0 and grow_pt is not None:
            cx = grow_pt[0] + (cx - grow_pt[0]) * grow_scale
            cy = grow_pt[1] + (cy - grow_pt[1]) * grow_scale
        sx, sy = manim_to_screen(cx, cy, w, h, cz)
        scale = h / 8.0
        hw = mob.width / 2.0 * scale * grow_scale
        hh = mob.height / 2.0 * scale * grow_scale
        try:
            fo = float(mob.fill_rgbas[:, 3].max())
        except Exception:
            fo = get_opacity(mob, 'fill', 1.0)
        try:
            so = float(mob.stroke_rgbas[:, 3].max())
        except Exception:
            so = get_opacity(mob, 'stroke', 1.0)
        # `mob.width`/`mob.height` come from the points, which manim's ShowPartial
        # has already cut -- so the native window must be 1.0 once tagged,
        # otherwise the fill is cut twice (render_hooks._write_progress).
        progress = point_path_bounds(mob)[1]
        if fo <= 0 and so <= 0:
            return
        if progress <= 0:
            return
        fr, fg, fb = self._fill_color(mob)
        self.dll.AddRect(sx, sy, hw, hh, rot, fr, fg, fb, 0, 0, 0, 0.0, progress, a * fo)
        if so > 0 and self._stroke_width(mob) > 0:
            # see _send_square: stroke_width 0 must not draw a border
            cr, cg, cb = self._stroke_color(mob)
            # The stroke opacity rides the ALPHA, not the colour: native blends
            # straight-alpha (colour*alpha + dst*(1-alpha)), so baking `so` in
            # hard-replaced the background and a stroke over a non-black backdrop
            # stayed black while it faded in (same trap _send_polygon documents).
            a = a * so
            sw = self._stroke_width(mob)
            tl = self._rotate_point(sx - hw, sy - hh, sx, sy, rot)
            tr = self._rotate_point(sx + hw, sy - hh, sx, sy, rot)
            brc = self._rotate_point(sx + hw, sy + hh, sx, sy, rot)
            bl = self._rotate_point(sx - hw, sy + hh, sx, sy, rot)
            edges = [
                (tr, tl, 2.0 * hw),
                (tl, bl, 2.0 * hh),
                (bl, brc, 2.0 * hw),
                (brc, tr, 2.0 * hh),
            ]
            perimeter = 2.0 * (2.0 * hw + 2.0 * hh)
            drawn = perimeter * progress
            remaining = drawn
            for (x0, y0), (x1, y1), length in edges:
                if remaining <= 0:
                    break
                if remaining >= length:
                    self._emit_stroke(x0, y0, x1, y1, sw, cr, cg, cb, a)
                    remaining -= length
                else:
                    frac = remaining / length
                    ex = x0 + (x1 - x0) * frac
                    ey = y0 + (y1 - y0) * frac
                    self._emit_stroke(x0, y0, ex, ey, sw, cr, cg, cb, a)
                    remaining = 0

    def _send_ellipse(self, mob, a, w, h, rot, parent_offset=None):
        cx, cy, cz = mob.get_center()
        if parent_offset is not None:
            cx += parent_offset[0]; cy += parent_offset[1]
        about = getattr(mob, '_rotation_about_point', None)
        if about is not None:
            neg_rot = -rot
            dx, dy = cx - about[0], cy - about[1]
            c, sn = math.cos(neg_rot), math.sin(neg_rot)
            cx = about[0] + dx * c - dy * sn
            cy = about[1] + dx * sn + dy * c
        grow_scale = getattr(mob, '_grow_scale', 1.0)
        grow_pt = getattr(mob, '_grow_point', None)
        if grow_scale != 1.0 and grow_pt is not None:
            cx = grow_pt[0] + (cx - grow_pt[0]) * grow_scale
            cy = grow_pt[1] + (cy - grow_pt[1]) * grow_scale
        sx, sy = manim_to_screen(cx, cy, w, h, cz)
        scale = h / 8.0
        rx = mob.width / 2.0 * scale * grow_scale
        ry = mob.height / 2.0 * scale * grow_scale
        try:
            fo = float(mob.fill_rgbas[:, 3].max())
        except Exception:
            fo = get_opacity(mob, 'fill', 1.0)
        try:
            so = float(mob.stroke_rgbas[:, 3].max())
        except Exception:
            so = get_opacity(mob, 'stroke', 1.0)
        progress = getattr(mob, '_vulkan_progress', 1.0)
        if fo <= 0 and so <= 0:
            return
        if progress <= 0:
            return
        fr, fg, fb = self._fill_color(mob)
        self.dll.AddEllipse(float(sx), float(sy), float(rx), float(ry), fr, fg, fb, 0, 0, 0, 0.0, progress, a * fo)
        if so > 0 and self._stroke_width(mob) > 0:
            # see _send_square: stroke_width 0 must not draw a border
            cr, cg, cb = self._stroke_color(mob)
            # The stroke opacity rides the ALPHA, not the colour: native blends
            # straight-alpha (colour*alpha + dst*(1-alpha)), so baking `so` in
            # hard-replaced the background and a stroke over a non-black backdrop
            # stayed black while it faded in (same trap _send_polygon documents).
            a = a * so
            sw = self._stroke_width(mob)
            # Match legacy behavior: fixed segment tessellation (segs=48)
            segs = 48
            circumference = math.pi * (3 * (rx + ry) - math.sqrt((3 * rx + ry) * (rx + 3 * ry)))
            drawn = circumference * progress
            accumulated = 0.0
            prev_angle_rad = rot
            prev_px = sx + math.cos(prev_angle_rad) * rx
            prev_py = sy - math.sin(prev_angle_rad) * ry
            for j in range(1, segs + 1):
                if accumulated >= drawn:
                    break
                cur_angle_rad = rot + 2.0 * math.pi * j / segs
                px = sx + math.cos(cur_angle_rad) * rx
                py = sy - math.sin(cur_angle_rad) * ry
                seg_len = math.sqrt((px - prev_px) ** 2 + (py - prev_py) ** 2)
                if accumulated + seg_len <= drawn:
                    self._emit_stroke(prev_px, prev_py, px, py, sw, cr, cg, cb, a)
                    accumulated += seg_len
                else:
                    frac = (drawn - accumulated) / seg_len if seg_len > 0 else 0
                    ex = prev_px + (px - prev_px) * frac
                    ey = prev_py + (py - prev_py) * frac
                    self._emit_stroke(prev_px, prev_py, ex, ey, sw, cr, cg, cb, a)
                    accumulated = drawn
                prev_px, prev_py = px, py

    @staticmethod
    def _oncurve_radius(mob):
        """The radius of the curve a `Circle` actually strokes, in manim units.

        `mob.width` is the bounding box of the **whole** bezier control polygon
        -- anchors *and* off-curve handles.  For a manim circle of r = 0.550000
        the handles sit at 0.569015, so `width` is `2 * 0.55` only while the
        control polygon happens to be axis-aligned.  `Rotate` (a `Transform`)
        sweeps that polygon, and once every 45 deg a handle lines up with the
        x axis:

            width = 1.100000 -> 1.137870   (+3.46 %)

        ...while the curve manim strokes never moves (`d_min`/`d_max` are
        constant at 0.550000/0.569015 on every frame, and CE's rendered ring is
        a flat 68 px).  Driving `sr` from `mob.width` therefore inflated the
        drawn circle for exactly the frames where a handle crosses the axis --
        reported as "在fade out之前有一瞬间非正常的膨胀" on
        `AnimationCompositionGroups`, and measured as RTM bbox h
        68,68,68,69,**72,72**,68,69,68 against CE's flat 68.

        `get_start()` is `points[0]`, the on-curve start of the path, so its
        distance from the centre is the true radius; it also tracks any scaling
        the mobject underwent, which the `radius` attribute does not.
        """
        try:
            c = np.asarray(mob.get_center(), dtype=float)
            s = np.asarray(mob.get_start(), dtype=float)
            r = float(np.linalg.norm(s[:2] - c[:2]))
            if r > 0.0 and np.isfinite(r):
                return r
        except Exception:
            pass
        return mob.width / 2.0

    def _send_circle(self, mob, a, w, h, rot, parent_offset=None):
        cx, cy, cz = mob.get_center()
        if parent_offset is not None:
            cx += parent_offset[0]; cy += parent_offset[1]
        about = getattr(mob, '_rotation_about_point', None)
        if about is not None:
            neg_rot = -rot
            dx, dy = cx - about[0], cy - about[1]
            c, sn = math.cos(neg_rot), math.sin(neg_rot)
            cx = about[0] + dx * c - dy * sn
            cy = about[1] + dx * sn + dy * c
        grow_scale = getattr(mob, '_grow_scale', 1.0)
        grow_pt = getattr(mob, '_grow_point', None)
        if grow_scale != 1.0 and grow_pt is not None:
            cx = grow_pt[0] + (cx - grow_pt[0]) * grow_scale
            cy = grow_pt[1] + (cy - grow_pt[1]) * grow_scale
        sx, sy = manim_to_screen(cx, cy, w, h, cz)
        scale_y = h / 8.0
        # NOT `mob.width / 2`: see `_oncurve_radius` -- `width` also measures the
        # off-curve bezier handles, so a rotating control polygon inflated the
        # drawn radius by up to 3.46 % while the stroked curve never moved.
        sr = self._oncurve_radius(mob) * scale_y * grow_scale
        try:
            fo = float(mob.fill_rgbas[:, 3].max())
        except Exception:
            fo = get_opacity(mob, 'fill', 1.0)
        try:
            so = float(mob.stroke_rgbas[:, 3].max())
        except Exception:
            so = get_opacity(mob, 'stroke', 1.0)
        progress = getattr(mob, '_vulkan_progress', 1.0)
        if fo <= 0 and so <= 0:
            return
        if progress <= 0:
            return
        fr, fg, fb = self._fill_color(mob)
        self.dll.AddCircle(float(sx), float(sy), float(sr), fr, fg, fb, 0, 0, 0, 0.0, progress, a * fo)
        sw_manim = get_stroke_w(mob)
        if so > 0 and sw_manim > 0:
            cr, cg, cb = self._stroke_color(mob)
            # The stroke opacity rides the ALPHA, not the colour: native blends
            # straight-alpha (colour*alpha + dst*(1-alpha)), so baking `so` in
            # hard-replaced the background and a stroke over a non-black backdrop
            # stayed black while it faded in (same trap _send_polygon documents).
            a = a * so
            sw = self._stroke_width(mob)
            # Match legacy behavior: fixed segment tessellation (segs=48)
            segs = 48
            circumference = 2.0 * math.pi * sr
            drawn = circumference * progress
            accumulated = 0.0
            prev_angle_rad = rot
            prev_px = sx + math.cos(prev_angle_rad) * sr
            prev_py = sy - math.sin(prev_angle_rad) * sr
            for j in range(1, segs + 1):
                if accumulated >= drawn:
                    break
                cur_angle_rad = rot + 2.0 * math.pi * j / segs
                px = sx + math.cos(cur_angle_rad) * sr
                py = sy - math.sin(cur_angle_rad) * sr
                seg_len = math.sqrt((px - prev_px) ** 2 + (py - prev_py) ** 2)
                if accumulated + seg_len <= drawn:
                    self._emit_stroke(prev_px, prev_py, px, py, sw, cr, cg, cb, a)
                    accumulated += seg_len
                else:
                    frac = (drawn - accumulated) / seg_len if seg_len > 0 else 0
                    ex = prev_px + (px - prev_px) * frac
                    ey = prev_py + (py - prev_py) * frac
                    self._emit_stroke(prev_px, prev_py, ex, ey, sw, cr, cg, cb, a)
                    accumulated = drawn
                prev_px, prev_py = px, py

    def _send_arrow(self, mob, a, w, h, rot, parent_offset=None):
        s = np.array(mob.get_start(), dtype=float)
        e = np.array(mob.get_end(), dtype=float)
        # `Arrow.get_end()` is the TIP's tip, not where the shaft stops: manim's
        # `add_tip` appends the tip as a submobject and shortens the line, so the
        # line's own last point is the real head base (2.00 for a triangle,
        # circle or stealth tip, 1.855 for a square one) while `get_end()` is
        # 2.35 for all of them.  The head base must come from the line itself:
        # the old `get_end() - tip_length` is only right when the tip happens to
        # be exactly `tip_length` long, and overshot a square tip's line by
        # 0.145 units = 8.7 px (report #9).
        #
        # The mirror image of that rule holds at the START end: for a
        # `DoubleArrow` manim adds a second tip (`start_tip`) at the beginning
        # of the line, and `get_start()` then reports THAT tip's apex, not the
        # shaft's first point (DoubleArrow([3.8, ...], [5.8, ...]): get_start()
        # = 3.80, the line's own points start at 4.15).  Drawing the shaft from
        # `get_start()` made it poke ~0.35 units out past the left arrowhead --
        # the shaft's stroke sticks out of the triangle's narrow apex as a stub
        # a few pixels left of it (LinesAnglesAndVectors' DoubleArrow: ink from
        # x=1469 where CE starts at x=1473).  So the shaft start must come from
        # the line itself, exactly like `e_line`; for an ordinary `Arrow` (no
        # tip at its start end) it is `get_start()`, so nothing else changes.
        try:
            _own = np.asarray(mob.get_points(), dtype=float)
            _d = np.linalg.norm(_own - s, axis=1)
            e_line = np.array(_own[int(np.argmax(_d))], dtype=float)
            _d0 = np.linalg.norm(_own - e_line, axis=1)
            s_line = np.array(_own[int(np.argmax(_d0))], dtype=float)
        except Exception:
            e_line = e.copy()
            s_line = s.copy()
        grow_scale = getattr(mob, '_grow_scale', 1.0)
        grow_pt = getattr(mob, '_grow_point', None)
        if grow_scale != 1.0 and grow_pt is not None:
            gp = np.array(grow_pt, dtype=float)
            s = gp + (s - gp) * grow_scale
            e = gp + (e - gp) * grow_scale
            e_line = gp + (e_line - gp) * grow_scale
            s_line = gp + (s_line - gp) * grow_scale
        if parent_offset is not None:
            off = np.array(parent_offset, dtype=float)
            s = s + off; e = e + off; e_line = e_line + off
            s_line = s_line + off
        about = getattr(mob, '_rotation_about_point', None)
        if about is not None:
            pivot = np.array(about, dtype=float)
            neg_rot = -rot
            c, sn = math.cos(neg_rot), math.sin(neg_rot)

            def _rot_about(pt):
                dx, dy = pt[0] - pivot[0], pt[1] - pivot[1]
                return np.array([pivot[0] + dx * c - dy * sn,
                                 pivot[1] + dx * sn + dy * c, 0.0])

            s = _rot_about(s)
            e = _rot_about(e)
            e_line = _rot_about(e_line)
            s_line = _rot_about(s_line)
            sx1, sy1 = manim_to_screen(s_line[0], s_line[1], w, h, s_line[2])
            sx2, sy2 = manim_to_screen(e[0], e[1], w, h, e[2])
            sxl, syl = manim_to_screen(e_line[0], e_line[1], w, h, e_line[2])
        else:
            sx1, sy1 = manim_to_screen(s_line[0], s_line[1], w, h, s_line[2])
            sx2, sy2 = manim_to_screen(e[0], e[1], w, h, e[2])
            sxl, syl = manim_to_screen(e_line[0], e_line[1], w, h, e_line[2])
            cx, cy, cz = mob.get_center()
            if parent_offset is not None:
                cx += parent_offset[0]; cy += parent_offset[1]
            scx, scy = manim_to_screen(cx, cy, w, h, cz)
            sx1, sy1 = self._rotate_point(sx1, sy1, scx, scy, rot)
            sx2, sy2 = self._rotate_point(sx2, sy2, scx, scy, rot)
            sxl, syl = self._rotate_point(sxl, syl, scx, scy, rot)
        # The shaft's own points (`s_line`/`e_line`) are what ShowPartial cuts
        # on a Create, so they already end at the pen: windowing them again by
        # `_vulkan_progress` drew `progress * cut` of the shaft.  A tagged path
        # therefore yields 1.0, which also flips `use_real_tip` below and hands
        # the head to `_send_arrow_tip` -- that reads the TIP submobject's
        # points, which manim cut with its own sub_alpha, exactly as CE draws
        # it.  Untagged (a flash, a stagger driver) keeps the plain progress.
        progress = point_path_bounds(mob)[1]
        if progress <= 0:
            return
        # The real tip is a submobject with its own geometry -- shape, size and
        # hollow-vs-filled all live there (manim builds seven different ones).
        # It is drawn instead of the synthesised triangle below, except during a
        # partial draw, where today's progress-aware head is kept rather than
        # revealing a whole tip at once.
        tip = getattr(mob, 'tip', None)
        tip_pts = None
        if tip is not None:
            try:
                tip_pts = tip.get_points()
            except Exception:
                tip_pts = None
        use_real_tip = (tip_pts is not None and len(tip_pts) >= 3
                        and progress >= 1.0)
        r, g, b = self._stroke_color(mob)
        so = get_opacity(mob, 'stroke', 1.0)
        r, g, b = int(r * so), int(g * so), int(b * so)
        # Same integer-core-plus-fractional-edge rule as _send_line: a single
        # widened quad makes every covered pixel cross an ink threshold, which
        # is what the coverage detector saw on the arrow scenes.
        px = self._stroke_width(mob)
        dx = sx2 - sx1
        dy = sy2 - sy1
        length = math.hypot(dx, dy)
        ux = dx / length if length > 0 else 0.0
        uy = dy / length if length > 0 else 0.0
        arrow_len_manim = math.hypot(e[0] - s[0], e[1] - s[1])
        max_tip_ratio = getattr(mob, 'max_tip_length_to_length_ratio', 0.25)
        default_tip_length = getattr(mob, 'tip_length', 0.35)
        tip_manim = min(default_tip_length, max_tip_ratio * arrow_len_manim)
        scale_y = h / 8.0
        head_len = tip_manim * scale_y
        head_w = head_len * 0.5
        if use_real_tip:
            base_x, base_y = sxl, syl
        else:
            base_x = sx2 - ux * head_len
            base_y = sy2 - uy * head_len
        # A shaft can legitimately be invisible (stroke_width=0 or
        # stroke_opacity=0) while the head is not, so the head is gated by its
        # own condition instead of riding the shaft's early returns.
        can_stroke = so > 0 and px > 0 and length > 0
        if can_stroke:
            if progress >= 1.0:
                ex, ey = base_x, base_y
            else:
                ex = sx1 + (base_x - sx1) * progress
                ey = sy1 + (base_y - sy1) * progress
            # `length` above measures to the TIP's apex, which stays out at the
            # arrowhead even while ShowPartial has collapsed the shaft's own
            # points to nothing -- so the shaft can still be a single point when
            # `can_stroke` says otherwise.  A collapsed path inks nothing in
            # manim either; native has no direction for the quad.
            if abs(ex - sx1) >= 1e-6 or abs(ey - sy1) >= 1e-6:
                # NB: `px` is reassigned to the head's perpendicular below
                # (px = -uy), so the shaft is emitted while it still holds the
                # stroke width.
                self._emit_stroke(sx1, sy1, ex, ey, px, r, g, b, a)
        if use_real_tip:
            self._send_arrow_tip(mob, tip, a, w, h, rot, parent_offset)
            return
        if not can_stroke:
            return
        px = -uy
        py = ux
        hx1 = base_x + px * head_w
        hy1 = base_y + py * head_w
        hx2 = base_x - px * head_w
        hy2 = base_y - py * head_w
        head_verts = (ctypes.c_float * 6)(sx2, sy2, hx2, hy2, hx1, hy1)
        self.dll.AddPolygon(
            sx2, sy2, r, g, b, r, g, b, 0,
            3, head_verts, progress, a, 1,
        )

    def _send_arrow_tip(self, mob, tip, a, w, h, rot, parent_offset=None):
        """Draw the arrow's own `ArrowTip` submobject (report #9).

        `_send_arrow` used to synthesise a fixed 3-vertex triangle whose only
        inputs were `tip_length` and a hard-coded `0.5` taper, so every arrow
        rendered as `ArrowTriangleFilledTip` whatever `tip_shape` said: on
        `ArrowTips` RTM's seven tip zones measured 238-249 px each while CE drew
        137/141/158/191/220/277/322 -- the head shape never varied.  The tip is a
        submobject, so it goes down the generic point path, which reads its fill,
        stroke and bezier points.

        `rot` here is the screen-space `-rot` the shaft uses (the dispatch passes
        `screen_rot`), and `_send_vmobject` rotates in manim space about the
        mobject's *own* centre -- so `-rot` restores manim's angle, and the tip's
        centre is displaced by however far that centre itself travels when the
        arrow rotates.  That centre-displacement decomposition is the same one
        the VGroup walk uses for its children.
        """
        rot_orig = -rot
        offset = None if parent_offset is None else np.array(parent_offset,
                                                             dtype=float)
        pg_gs = getattr(mob, '_grow_scale', None)
        pg_gp = getattr(mob, '_grow_point', None)
        # GrowArrow sets _grow_scale/_grow_point on the ARROW; the tip has to
        # scale with the shaft or the head appears at full size while the shaft
        # is still growing (the idiom used by the VGroup and Text walks).
        need_gs = pg_gs is not None and not hasattr(tip, '_grow_scale')
        need_gp = pg_gp is not None and not hasattr(tip, '_grow_point')
        if need_gs:
            tip._grow_scale = pg_gs
        if need_gp:
            tip._grow_point = pg_gp
        try:
            if rot_orig != 0.0:
                about = getattr(mob, '_rotation_about_point', None)
                centre = np.array(
                    about if about is not None else mob.get_center(),
                    dtype=float)
                tc = np.array(tip.get_center(), dtype=float)
                d = tc - centre
                ca, sa = math.cos(rot_orig), math.sin(rot_orig)
                moved = centre + np.array([d[0] * ca - d[1] * sa,
                                           d[0] * sa + d[1] * ca])
                delta = moved - tc
                if offset is None:
                    offset = np.zeros(3)
                offset = offset + delta
            self._send_vmobject(tip, a, w, h, offset, rot_orig)
        finally:
            if need_gs:
                del tip._grow_scale
            if need_gp:
                del tip._grow_point

    def _send_line(self, mob, a, w, h, rot, parent_offset=None):
        # The endpoints must come from the path itself.  `TipableVMobject`
        # (Line, NumberLine, anything with an arrowhead) overrides `get_end()`
        # to answer with the *tip submobject's* start -- a point that stays out
        # at the arrowhead while ShowPartial has collapsed this mob's own
        # points to nothing, so a Create inked the whole line from its very
        # first frame (CoordinateSystemBasics' y-spine was full 30 frames
        # before CE draws any of it, since `get_start()` correctly read the
        # collapsed `points[0]` and the tip still answered 0.3 units up).
        # CE strokes the path, and the cut wrote the path, so the path wins;
        # only a mobject with no points of its own falls back to the accessors.
        own = None
        try:
            own = np.asarray(mob.get_points(), dtype=float)
        except Exception:
            own = None
        if own is not None and len(own) > 0:
            s = np.array(own[0], dtype=float)
            e = np.array(own[-1], dtype=float)
        else:
            s = np.array(mob.get_start(), dtype=float)
            e = np.array(mob.get_end(), dtype=float)
        grow_scale = getattr(mob, '_grow_scale', 1.0)
        grow_pt = getattr(mob, '_grow_point', None)
        if grow_scale != 1.0 and grow_pt is not None:
            gp = np.array(grow_pt, dtype=float)
            s = gp + (s - gp) * grow_scale
            e = gp + (e - gp) * grow_scale
        if parent_offset is not None:
            off = np.array(parent_offset, dtype=float)
            s = s + off; e = e + off
        about = getattr(mob, '_rotation_about_point', None)
        if about is not None:
            pivot = np.array(about, dtype=float)
            neg_rot = -rot
            c, sn = math.cos(neg_rot), math.sin(neg_rot)
            dx, dy = s[0] - pivot[0], s[1] - pivot[1]
            s = np.array([pivot[0] + dx * c - dy * sn, pivot[1] + dx * sn + dy * c, 0.0])
            dx, dy = e[0] - pivot[0], e[1] - pivot[1]
            e = np.array([pivot[0] + dx * c - dy * sn, pivot[1] + dx * sn + dy * c, 0.0])
            sx1, sy1 = manim_to_screen(s[0], s[1], w, h, s[2])
            sx2, sy2 = manim_to_screen(e[0], e[1], w, h, e[2])
        else:
            sx1, sy1 = manim_to_screen(s[0], s[1], w, h, s[2])
            sx2, sy2 = manim_to_screen(e[0], e[1], w, h, e[2])
            cx, cy, cz = mob.get_center()
            if parent_offset is not None:
                cx += parent_offset[0]; cy += parent_offset[1]
            scx, scy = manim_to_screen(cx, cy, w, h, cz)
        sx1, sy1 = self._rotate_point(sx1, sy1, scx, scy, rot)
        sx2, sy2 = self._rotate_point(sx2, sy2, scx, scy, rot)
        r, g, b = self._stroke_color(mob)
        so = get_opacity(mob, 'stroke', 1.0)
        if so <= 0:
            return
        r, g, b = int(r * so), int(g * so), int(b * so)
        # A Line whose points were warped by `apply_function` (OpeningManim's
        # `grid.animate.apply_function(sin ...)`) is no longer straight, and
        # drawing the start->end chord loses the curve -- CE draws the whole
        # point path.  Hand those to the point path when a control point leaves
        # the chord by more than ~0.02 manim units (1.2 px at 480p).
        try:
            _pts = mob.get_points()
            if len(_pts) > 2:
                _dx, _dy = float(e[0] - s[0]), float(e[1] - s[1])
                _ln = math.hypot(_dx, _dy)
                if _ln > 1e-6:
                    _ux, _uy = _dx / _ln, _dy / _ln
                    _dev = 0.0
                    for _p in _pts:
                        _d = -(_p[1] - s[1]) * _ux + (_p[0] - s[0]) * _uy
                        if abs(_d) > _dev:
                            _dev = abs(_d)
                    if _dev > 0.02:
                        self._send_vmobject(mob, a, w, h, parent_offset, rot,
                                            exact_width=True)
                        return
        except Exception:
            pass
        # manim draws a line of `0.01 * stroke_width * (pixel_height /
        # frame_height)` pixels -- 1.2 px at 480p for the default stroke_width=2
        # -- and native's rasteriser makes a quad of ``width + 1`` pixels
        # (draw_line.c: half_thick = thick*0.5 + 0.5).  Native widths are
        # integers, so an exact sub-pixel width needs the nearest integer quad
        # ABOVE the target plus a compensating alpha: ink = (width+1) * alpha.
        # Rounding to nearest with alpha 1 (the previous `round(px) - 1`) left
        # every thin line short -- 1.2 px drawn as a 1 px quad is 17% less ink
        # than CE, which is exactly the VectorBasicsScene / VectorArrow /
        # OpeningManim signature (uniform ~12-22% dim, lit counts comparable).
        px = self._stroke_width(mob)
        if px <= 0:
            return
        # Exact sub-pixel width: integer core + symmetric fractional edges, NOT
        # one widened quad at a compensating alpha -- a single quad covers the
        # next integer up and every one of those pixels crosses an ink
        # threshold (measured: `ThreeDRotationProbe`'s excess coverage jumping
        # 0.054 -> 0.192, all of it within 2 px of CE's strokes).  The rule now
        # lives in _stroke_layers so every stroke sender shares it.
        # `s`/`e` are read from the path itself (see the top of this method),
        # and ShowPartial has already cut that path on a Create: the pen's end
        # IS the drawn end, so windowing it again by `_vulkan_progress` drew
        # `progress * cut` of the line.  `point_path_bounds` returns 1.0 for a
        # tagged path and the plain progress otherwise (same rule as
        # `_send_rectangle`, plan 4.2).
        progress = point_path_bounds(mob)[1]
        if progress <= 0:
            return
        if progress >= 1.0:
            ex, ey = sx2, sy2
        else:
            ex = sx1 + (sx2 - sx1) * progress
            ey = sy1 + (sy2 - sy1) * progress
        # A path the cut collapsed to a point has nothing to stroke: manim's
        # butt cap inks nothing, and native would have no direction to build
        # the quad from (ShowPartial at sub_alpha 0 is the common case).
        if abs(ex - sx1) < 1e-6 and abs(ey - sy1) < 1e-6:
            return
        self._emit_stroke(sx1, sy1, ex, ey, px, r, g, b, a)

    def _send_dot(self, mob, a, w, h):
        cx, cy, cz = mob.get_center()
        sx, sy = manim_to_screen(cx, cy, w, h, cz)
        # The radius is in manim units, so it converts with the frame height that
        # is on screen -- the same rule as `_stroke_width`.  `h / 8.0` ignored the
        # camera: its centre already moved with the zoom (manim_to_screen) while
        # the disc stayed the size it had before the camera moved, so a zooming
        # scene showed a dot that never grew over `frame.animate.scale(...)` and
        # then snapped to the right size once the play ended
        # (FollowingGraphCamera: CE 22 -> 44 px smoothly, RTM 22, 22, ..., 44).
        scale_y = h / self._visible_frame_height()
        # A Dot is a circle, but its bounding box need not be square: a VDict
        # with show_keys=True stretches each entry to line up with its key label
        # (measured: width 1.244 against height 0.351 for a radius-0.16 Dot), and
        # taking the radius from `width` drew a disc 3.9x too big (emitted
        # AddCircle radius 37px where CE's dot is 9.6px, 3882 yellow pixels
        # against 226).  The smaller axis is the un-stretched one.
        rad = (min(mob.width, mob.height) / 2.0) * scale_y
        try:
            fo = float(mob.fill_rgbas[:, 3].max())
        except Exception:
            fo = get_opacity(mob, 'fill', 1.0)
        if fo <= 0:
            return
        r, g, b = self._color(mob, a)
        fo = min(fo, getattr(mob, '_dot_max_opacity', 1.0))
        self.dll.AddCircle(sx, sy, rad, r, g, b, 0, 0, 0, 0.0, 1.0, a * fo)

    def _send_dashed_line(self, mob, a, w, h, rot=0.0, parent_offset=None):
        # same grow/offset/rotation treatment as _send_line, so a dashed line
        # inside a group follows that group's transform and rotation
        s = np.array(mob.get_start(), dtype=float)
        e = np.array(mob.get_end(), dtype=float)
        grow_scale = getattr(mob, '_grow_scale', 1.0)
        grow_pt = getattr(mob, '_grow_point', None)
        if grow_scale != 1.0 and grow_pt is not None:
            gp = np.array(grow_pt, dtype=float)
            s = gp + (s - gp) * grow_scale
            e = gp + (e - gp) * grow_scale
        if parent_offset is not None:
            off = np.array(parent_offset, dtype=float)
            s = s + off
            e = e + off
        sx1, sy1 = manim_to_screen(s[0], s[1], w, h, s[2])
        sx2, sy2 = manim_to_screen(e[0], e[1], w, h, e[2])
        cx, cy, cz = mob.get_center()
        if parent_offset is not None:
            cx += parent_offset[0]
            cy += parent_offset[1]
        scx, scy = manim_to_screen(cx, cy, w, h, cz)
        sx1, sy1 = self._rotate_point(sx1, sy1, scx, scy, rot)
        sx2, sy2 = self._rotate_point(sx2, sy2, scx, scy, rot)
        so = get_opacity(mob, 'stroke', 1.0)
        if so <= 0:
            return
        r, g, b = self._stroke_color(mob)
        r, g, b = int(r * so), int(g * so), int(b * so)
        scale = h / 8.0
        sw = self._stroke_width(mob)
        dl_manim = getattr(mob, 'dash_length', 0.05)
        ratio = getattr(mob, 'dashed_ratio', 0.5)
        if ratio <= 0 or ratio >= 1:
            ratio = 0.5
        gl_manim = dl_manim * (1.0 - ratio) / ratio
        dl = max(1.0, dl_manim * scale)
        gl = max(1.0, gl_manim * scale)
        progress = getattr(mob, '_vulkan_progress', 1.0)
        if progress <= 0:
            return
        if progress >= 1.0:
            ex, ey = sx2, sy2
        else:
            ex = sx1 + (sx2 - sx1) * progress
            ey = sy1 + (sy2 - sy1) * progress
        # `sw` is manim's target width in pixels, not a native quad width: the
        # native quad is `width + 1` px (draw_line.c), so a dashed line needs
        # the same core/fractional-edge split as every other stroke.  Each
        # layer becomes its own AddDashedLine because that entry point takes a
        # single width.
        for _w, _a in self._stroke_layers(sw, a):
            self.dll.AddDashedLine(sx1, sy1, ex, ey, _w, r, g, b, dl, gl, _a)

    def _stroke_polyline_with_progress(self, flat, closed, lower, upper,
                                       r, g, b, px, alpha):
        """Stroke the [lower, upper] stretch of a screen-space polyline.

        ``flat`` is x0,y0,x1,y1,... in screen pixels; ``lower``/``upper`` are
        fractions of the total length.  Shared by the polygon and arc senders so
        a partially drawn shape (Create / ShowPartial / ShowPassingFlash) is
        stroked the same way whichever sender handles it (plan 4.2).

        ``px`` is manim's target width in pixels, NOT a native quad width: the
        core/fractional decomposition of :meth:`_stroke_layers` happens here so
        every polyline sender inherits the exact-width rule instead of the old
        ``max(1, round(px))`` that drew ``round(px) + 1`` px.
        """
        n = len(flat) // 2
        if n < 2:
            return
        layers = self._stroke_layers(px, alpha)
        if not layers:
            return
        last = n if closed else n - 1
        edge_lens = []
        perimeter = 0.0
        for j in range(last):
            j2 = (j + 1) % n
            el = math.hypot(flat[j2 * 2] - flat[j * 2],
                            flat[j2 * 2 + 1] - flat[j * 2 + 1])
            edge_lens.append(el)
            perimeter += el
        if perimeter <= 0.0:
            return
        try:
            lower = max(0.0, min(1.0, float(lower)))
            upper = max(0.0, min(1.0, float(upper)))
        except (TypeError, ValueError):
            lower, upper = 0.0, 1.0
        skip = perimeter * lower
        remaining = perimeter * upper - skip
        if remaining <= 0.0:
            return
        for j in range(last):
            if remaining <= 0.0:
                break
            j2 = (j + 1) % n
            el = edge_lens[j]
            x0, y0 = flat[j * 2], flat[j * 2 + 1]
            x1, y1 = flat[j2 * 2], flat[j2 * 2 + 1]
            if skip >= el:
                skip -= el
                continue
            seg_start = el - skip
            if seg_start > 0:
                frac_start = (el - seg_start) / el if el > 0 else 0.0
                x0 = x0 + (x1 - x0) * frac_start
                y0 = y0 + (y1 - y0) * frac_start
                skip = 0.0
                el = seg_start
            if remaining >= el:
                for _w, _a in layers:
                    self.dll.AddLine(x0, y0, x1, y1, _w, r, g, b, _a)
                remaining -= el
            else:
                frac = remaining / el if el > 0 else 0.0
                ex = x0 + (x1 - x0) * frac
                ey = y0 + (y1 - y0) * frac
                for _w, _a in layers:
                    self.dll.AddLine(x0, y0, ex, ey, _w, r, g, b, _a)
                remaining = 0.0

    def _stroke_points_polyline(self, points, w, h, parent_offset, rot, sx, sy):
        """Screen-space polyline for a VMobject's points (groups of 4 control points).

        Cubic segments are subdivided so that roughly every 3 screen pixels is a
        straight run (the same length-aware rule the text stroke uses): the
        caller's points are the *real* geometry, so a partially drawn or scaled
        arc is already encoded in them (plan 4.2).
        """
        flat = []
        n = len(points)
        # manim stores a shape's cubics as runs of 4 control points -- Arc, Sector
        # and Annulus all come out as a multiple of 4 (measured: Arc(180°) = 32,
        # Annulus = 64, Sector = 72) -- while a shape built curve-by-curve carries
        # 1 + 3k points.  Pick the stride that fits and never index past the end:
        # a wrong count here raised IndexError in the middle of a frame.
        if n % 4 == 0:
            stride, n_seg = 4, n // 4
        elif (n - 1) % 3 == 0:
            stride, n_seg = 3, (n - 1) // 3
        else:
            stride, n_seg = 4, max(0, (n - 3) // 4)
        for si in range(n_seg):
            idx = si * stride
            if idx + 3 >= n:
                break
            ctrl = []
            for k in range(4):
                p = points[idx + k]
                vx, vy = float(p[0]), float(p[1])
                vz = float(p[2]) if len(p) > 2 else 0.0
                if parent_offset is not None:
                    vx += parent_offset[0]
                    vy += parent_offset[1]
                vx, vy = manim_to_screen(vx, vy, w, h, vz)
                vx, vy = self._rotate_point(vx, vy, sx, sy, rot)
                ctrl.append((vx, vy))
            (p0x, p0y), (p1x, p1y), (p2x, p2y), (p3x, p3y) = ctrl
            cpoly = (math.hypot(p1x - p0x, p1y - p0y)
                     + math.hypot(p2x - p1x, p2y - p1y)
                     + math.hypot(p3x - p2x, p3y - p2y))
            chord = math.hypot(p3x - p0x, p3y - p0y)
            est = (cpoly + chord) * 0.5
            samples = int(max(8.0, min(256.0, math.ceil(est / 3.0))))
            start = 0 if si == 0 else 1        # the shared endpoint is not repeated
            for s in range(start, samples + 1):
                t = s / samples
                u = 1.0 - t
                bx = u * u * u * p0x + 3 * u * u * t * p1x + 3 * u * t * t * p2x + t * t * t * p3x
                by = u * u * u * p0y + 3 * u * u * t * p1y + 3 * u * t * t * p2y + t * t * t * p3y
                flat.append(bx)
                flat.append(by)
        return flat

    def _send_arc(self, mob, a, w, h, rot=0.0, parent_offset=None):
        """Arc drawn from its own points (plan 4.2).

        The previous version read ``mob.radius`` / ``start_angle`` / ``angle`` --
        construction-time attributes that neither a partial draw (``Create``) nor
        ``.animate.scale()`` updates -- so an animating arc rendered as a full,
        unscaled arc (ArcScaleProbe FLAT, CreateArcProbe SKIP-INTRO).
        Tessellating the points fixes both and picks up stroke opacity on the way;
        the shared progress walk keeps a partial stroke exact.
        """
        so = get_opacity(mob, 'stroke', 1.0)
        if so <= 0:
            return
        progress = getattr(mob, '_vulkan_progress', 1.0)
        if progress <= 0:
            return
        try:
            points = mob.get_points()
        except Exception:
            points = None
        if points is None or len(points) < 4:
            return
        cx, cy, cz = mob.get_center()
        if parent_offset is not None:
            cx += parent_offset[0]
            cy += parent_offset[1]
        sx, sy = manim_to_screen(cx, cy, w, h, cz)
        flat = self._stroke_points_polyline(points, w, h, parent_offset, rot, sx, sy)
        if len(flat) < 4:
            return
        r, g, b = self._stroke_color(mob)
        sw = self._stroke_width(mob)
        lower, upper = point_path_bounds(mob)
        self._stroke_polyline_with_progress(flat, False, lower, upper,
                                            int(r * so), int(g * so), int(b * so),
                                            sw, a)

    @staticmethod
    def _polygram_groups(mob, verts):
        """Split a Polygram's flattened vertices into its closed subpaths.

        manim's ``Polygram`` is "a generalized Polygon, allowing for
        **disconnected** sets of edges": each vertex group is its own closed
        subpath, but ``get_vertices()`` returns them flattened into ONE list.
        Joining that list end to end draws edges the shape does not own --
        measured on ``08_geometry.PolygramFamily`` (last frame, region mean
        diff against CE, ink px CE vs RTM):

            Polygram         5.93   6977 vs 6122
            RegularPolygram  10.25  8133 vs 7583

        both are hexagrams built from TWO triangles, while Polygon, Star and
        ConvexHull are a single group and already rendered correctly.

        Returns ``[verts]`` -- one closed polyline, exactly the old behaviour --
        unless the split is unambiguous: every group must be closed and hold at
        least three vertices, so a path a partial draw has cut (an unclosed
        tail) is never guessed into extra subpaths.
        """
        try:
            starts = mob.get_start_anchors()
            ends = mob.get_end_anchors()
        except Exception:
            return [verts]
        if starts is None or ends is None:
            return [verts]
        if len(starts) != len(verts) or len(ends) != len(verts) or len(starts) < 3:
            return [verts]
        try:
            consider_equal = mob.consider_points_equals
        except Exception:                                   # pragma: no cover
            consider_equal = None

        def _same(a, b):
            if consider_equal is not None:
                try:
                    return bool(consider_equal(a, b))
                except Exception:                           # pragma: no cover
                    pass
            return bool(np.allclose(a, b))

        bounds = []                       # (first, one past last) per group
        begin = 0
        for i in range(len(starts)):
            if not _same(ends[i], starts[begin]):
                continue
            if i + 1 - begin < 3:
                return [verts]            # degenerate group: do not guess
            bounds.append((begin, i + 1))
            begin = i + 1
        if begin != len(starts) or len(bounds) < 2:
            return [verts]                # unclosed path, or a plain Polygon
        return [verts[a:b] for a, b in bounds]

    def _polygon_flat(self, verts, w, h, parent_offset, rot, sx, sy):
        """Screen-space ``x0,y0,x1,y1,...`` for one vertex group."""
        flat = []
        for v in verts:
            vx = float(v[0])
            vy = float(v[1])
            vz = float(v[2]) if len(v) > 2 else 0.0
            if parent_offset is not None:
                vx += parent_offset[0]
                vy += parent_offset[1]
            vx, vy = manim_to_screen(vx, vy, w, h, vz)
            vx, vy = self._rotate_point(vx, vy, sx, sy, rot)
            flat.append(vx)
            flat.append(vy)
        return flat

    @staticmethod
    def _flat_perimeter(flat):
        n = len(flat) // 2
        perimeter = 0.0
        for j in range(n):
            j2 = (j + 1) % n
            perimeter += math.hypot(flat[j2 * 2] - flat[j * 2],
                                    flat[j2 * 2 + 1] - flat[j * 2 + 1])
        return perimeter

    @staticmethod
    def _group_windows(flat_groups, lower, upper):
        """Cut one global ``[lower, upper]`` path window at each group's share.

        A partial draw walks the outline ONCE, group after group, so every
        group drawing the same fraction would show two half-drawn triangles at
        once instead of one triangle and then the next.  Each group gets the
        slice of the window that falls inside its own share of the perimeter; a
        group the window misses collapses to a zero-length slice -- ``(1, 1)``
        or ``(0, 0)`` -- so the stroke sender submits nothing for it.
        """
        if len(flat_groups) == 1:
            return [(lower, upper)]
        try:
            lower = max(0.0, min(1.0, float(lower)))
            upper = max(0.0, min(1.0, float(upper)))
        except (TypeError, ValueError):
            lower, upper = 0.0, 1.0
        perims = [ShapeMixin._flat_perimeter(f) for f in flat_groups]
        total = sum(perims)
        if total <= 0.0:
            return [(lower, upper)] * len(flat_groups)
        windows = []
        cum = 0.0
        for p in perims:
            c0 = cum / total
            c1 = (cum + p) / total
            cum += p
            span = c1 - c0
            lo = (lower - c0) / span if span > 0.0 else 0.0
            hi = (upper - c0) / span if span > 0.0 else 0.0
            windows.append((max(0.0, min(1.0, lo)),
                            max(0.0, min(1.0, hi))))
        return windows

    def _send_polygon(self, mob, verts, alpha=1.0, rot_override=None, parent_offset=None):
        w, h = self.win_w, self.win_h
        self._dbg_emit("POLY-IN", "%s nverts=%s alpha=%s" % (
            type(mob).__name__,
            (len(verts) if verts is not None else None), alpha))
        cx, cy, cz = mob.get_center()
        if parent_offset is not None:
            cx += parent_offset[0]
            cy += parent_offset[1]

        # GrowFromCenter / GrowArrow / GrowFromEdge / GrowFromPoint support
        grow_scale = getattr(mob, '_grow_scale', 1.0)
        grow_pt = getattr(mob, '_grow_point', None)
        if grow_scale != 1.0 and grow_pt is not None:
            new_verts = []
            for v in verts:
                vx = float(v[0]); vy = float(v[1])
                vx = grow_pt[0] + (vx - grow_pt[0]) * grow_scale
                vy = grow_pt[1] + (vy - grow_pt[1]) * grow_scale
                new_verts.append([vx, vy, float(v[2])])
            verts = new_verts
            cx = grow_pt[0] + (cx - grow_pt[0]) * grow_scale
            cy = grow_pt[1] + (cy - grow_pt[1]) * grow_scale

        sx, sy = manim_to_screen(cx, cy, w, h, cz)
        br, bg, bb = self._stroke_color(mob)
        bw = self._stroke_width(mob)
        rot = -get_anim_rotation(mob) if rot_override is None else rot_override
        progress = getattr(mob, '_vulkan_progress', 1.0)
        has_bounds = hasattr(mob, '_vulkan_progress_upper')
        # `verts` come from mob's points, which manim's ShowPartial has already
        # cut -- point_path_bounds draws the cut path whole once tagged.
        progress_lower, progress_upper = point_path_bounds(mob)
        try:
            fo = float(mob.fill_rgbas[:, 3].max())
        except Exception:
            fo = get_opacity(mob, 'fill', 1.0)
        if progress <= 0 and not has_bounds:
            return

        # A Polygram may hold SEVERAL disjoint vertex groups; drawing them as
        # one closed polyline invents the edges that join the groups (the
        # hexagrams in 08_geometry.PolygramFamily came out as a zigzag).  Every
        # group becomes its own closed subpath -- one group, i.e. every other
        # shape, takes exactly the code path it took before.
        groups = self._polygram_groups(mob, verts)
        flats = [self._polygon_flat(g, w, h, parent_offset, rot, sx, sy)
                 for g in groups]
        windows = self._group_windows(flats, progress_lower, progress_upper)

        # `Create` hands us a CUT path: manim's ShowPartial has already replaced
        # `mob.points` with the drawn prefix, so the stroke must be rebuilt from
        # that prefix instead of from `get_vertices()`:
        #
        # * `get_vertices()` keeps only whole-curve corners, so the pen's
        #   trailing partial curve was dropped -- early in the draw fewer than
        #   two corners were left, `_stroke_polyline_with_progress` bailed out
        #   and NOTHING was stroked (MovingFrameBox: CE 994 yellow px where RTM
        #   still had 0, i.e. the border sat invisible for a third of its own
        #   Create and then appeared at once).
        # * it has to run OPEN: `closed=True` appends the chord from the pen's
        #   last point back to the path's first one, which drew a diagonal
        #   across the framebox instead of tracing its perimeter (measured: the
        #   drawn set was top edge + left edge + hypotenuse, xor 4304 px).
        #
        # The group split still runs on the cut corners, so a multi-group
        # Polygram keeps its subpaths, and the finish is re-appended as the
        # last corner (a manim polygon repeats its first point there) so a
        # completed Create keeps its closing edge.  The FILL is rebuilt from
        # the same cut groups below: native fans it along the perimeter up to
        # `stroke_progress`, so windowing the already-cut vertices by
        # `progress` again cut it a second time.
        stroke_closed = True
        stroke_flats = flats
        stroke_windows = windows
        cut_path = bool(getattr(mob, "_vulkan_points_partial", False))
        if cut_path:
            try:
                cut = np.asarray(mob.get_points())
            except Exception:
                cut = None
            if cut is not None and len(cut) >= 4:
                nppc = int(getattr(mob, "n_points_per_curve", 4) or 4)
                corners = cut[::nppc]
                cut_groups = self._polygram_groups(mob, corners)
                if cut_groups:
                    last = cut[-1]
                    if not np.allclose(np.asarray(cut_groups[-1][-1]), last):
                        cut_groups[-1] = list(cut_groups[-1]) + [last]
                    stroke_flats = [
                        self._polygon_flat(g, w, h, parent_offset, rot, sx, sy)
                        for g in cut_groups]
                    stroke_windows = self._group_windows(
                        stroke_flats, progress_lower, progress_upper)
                    stroke_closed = False

        if fo <= 0:
            so = get_opacity(mob, 'stroke', 1.0)
            if so <= 0 or bw <= 0:
                # `stroke_width=0` means NO stroke, but `so` (the rgba alpha)
                # stays 1.0 -- `max(1, round(bw))` then drew a 2 px border on
                # every fill-only shape (manim's ConfigDrivenScene `plate` is a
                # GREY_E fill with stroke_width=0; measured +4755 excess ink px
                # against a 3128 px deficit, d(last) +1.02).
                return
            for flat, (flat_lower, flat_upper) in zip(stroke_flats,
                                                       stroke_windows):
                self._stroke_polyline_with_progress(
                    flat, stroke_closed, flat_lower, flat_upper,
                    br, bg, bb,
                    bw, alpha * so)
        else:
            fr, fg, fb = self._fill_color_lit(mob)
            # native fills a polygon with a triangle fan (draw_polygon.c), and
            # fanning two triangles from ONE origin fills the gap between them
            # -- each group is its own AddPolygon.
            #
            # On a CUT path the fan gets the cut outline and the whole window:
            # `flats` is built from `get_vertices()`, which keeps only whole
            # corners (the pen's trailing partial curve is missing, so a
            # quadrilateral came out a triangle) and `fill_windows` then
            # re-applied `progress` to vertices manim had already cut.  Measured
            # on CutPolygonFill / CutQuadFill: mean|d| 3.33 / 2.65 against a
            # 0.75 baseline.  A window of (0, 1) makes native fan from the
            # CENTROID (drawn >= perimeter), the origin the static shape takes
            # too, so there is no jump when the Create completes.
            fill_flats = stroke_flats if cut_path else flats
            fill_windows = self._group_windows(
                fill_flats, 0.0, 1.0 if cut_path else progress)
            for i, flat in enumerate(fill_flats):
                arr = (ctypes.c_float * len(flat))(*flat)
                emitted = 0 if has_bounds else fill_windows[i][1]
                self.dll.AddPolygon(
                    sx, sy, fr, fg, fb, 0, 0, 0, 0.0,
                    len(flat) // 2, arr, emitted, alpha * fo, 1
                )
                _xs, _ys = flat[0::2], flat[1::2]
                self._dbg_emit(
                    "POLY", "%s n=%d group=%d/%d prog=%s has_bounds=%s "
                            "emitted_prog=%s alpha=%s fo=%s "
                            "bbox=[%.1f..%.1f, %.1f..%.1f]"
                    % (type(mob).__name__, len(flat) // 2, i + 1,
                       len(fill_flats),
                       progress, has_bounds, emitted, alpha * fo, fo,
                       min(_xs), max(_xs), min(_ys), max(_ys)))
            so = get_opacity(mob, 'stroke', 1.0)
            if so > 0 and bw > 0:
                # `bw <= 0` means `stroke_width=0`: no stroke at all, even though
                # the rgba alpha reads 1.0 (see the fill-only branch above).
                for flat, (flat_lower, flat_upper) in zip(stroke_flats,
                                                           stroke_windows):
                    self._stroke_polyline_with_progress(
                        flat, stroke_closed, flat_lower, flat_upper,
                        br, bg, bb,
                        bw, alpha * so)

    def _dot_radius(self, mob, h):
        """PMobject / Point 的点半径（像素）。

        manim 把点画成直径约 4px 的圆盘（实测 logs/point_size_probe.py：亮段长度
        众数 4px），native 过去是固定半径 4px（面积 4 倍）。这里给 480p/默认视口下
        2px，并按可见高度等比缩放——与描边同一套规则，所以相机 zoom 时点一起放大。
        """
        # manim draws a PMobject point as a FIXED ~4 px disc -- measured: the
        # modal lit run is 4 px at BOTH 854x480 and 1920x1080 -- so the radius
        # must NOT scale with the surface height.  The old `h / 30` term made it
        # grow with the window: at 1080p that drew 19 px dots against CE's 4 px
        # and gave PointCloudMobjects 2.2x CE's ink (lit 31272 vs 13992).  Only
        # the *visible frame height* may scale it, which is what a zooming
        # camera changes; 16.0 is the 480p-calibrated 2 px radius re-expressed
        # against the default frame height of 8.
        frame_height = 8.0
        try:
            from real_time_manim.camera_state import get_viewport
            viewport = get_viewport()
            if viewport is not None:
                frame_height = float(viewport.height) or 8.0
        except Exception:
            pass
        return max(0.5, (16.0 / frame_height) * self._point_width_scale(mob))

    @staticmethod
    def _point_width_scale(mob):
        """Scale for a point cloud whose points are not the default 4px wide.

        The radius above is calibrated for manim's default point `stroke_width`
        of 4.  `PointCloudDot` builds its points with `stroke_width = 2`
        (measured), i.e. half the diameter -- drawing those at the default merged
        its 216 spiral points into a solid disc where CE shows a separated
        lattice (measured PointCloudMobjects: 2103 px of excess ink, all of it
        inside the cloud's own box, against CE's dotted spiral).
        """
        width = 4.0
        try:
            raw = mob.get_stroke_width()
            if isinstance(raw, (int, float)) and raw > 0:
                width = float(raw)
            elif hasattr(raw, "__len__") and len(raw) > 0 and float(raw[0]) > 0:
                width = float(raw[0])
        except Exception:
            pass
        return width / 4.0

    def _send_point_cloud(self, mob, a, w, h, rot=0.0, parent_offset=None):
        """PMobject 家族：每个点画成一个点，而不是一条填充路径。

        manim 把这些 mobject 画成一个个小圆点（``PMobject.radius``）；送给贝塞尔
        填充路径会把点之间的间隙糊成实心（实测 PointCloudMobjects：RTM ink 24232
        vs CE 5797，4 倍，且 RTM 在 CE 画点阵处画成整块）。
        """
        so = get_opacity(mob, 'fill', 1.0)
        if so <= 0:
            return
        r, g, b = self._color(mob, a)
        # The PMobject family (Mobject1D/Mobject2D/PMobject/PGroup/PointCloudDot)
        # keeps its per-point colour in `mob.rgbas` -- `fill_rgbas` and
        # `stroke_rgbas` both raise AttributeError on it, so `_color` fell back
        # to its white default and every point cloud was drawn grey where CE
        # renders the colours `add_line(..., color=...)` set (measured
        # PointCloudMobjects: CE (144,160,128)/(128,176,112) against RTM's
        # (240,240,240)/(112,112,112), d(last) +1.79).
        rgbas = getattr(mob, 'rgbas', None)
        try:
            n_rgbas = len(rgbas) if rgbas is not None else 0
        except Exception:
            n_rgbas = 0
        cx, cy, cz = mob.get_center()
        sx, sy = manim_to_screen(cx, cy, w, h, cz)
        radius = self._dot_radius(mob, h)
        try:
            points = mob.get_points()
        except Exception:
            return

        for i, p in enumerate(points):
            vx, vy = float(p[0]), float(p[1])
            if parent_offset is not None:
                vx += parent_offset[0]
                vy += parent_offset[1]
            vz = float(p[2]) if len(p) > 2 else 0.0
            px, py = manim_to_screen(vx, vy, w, h, vz)
            px, py = self._rotate_point(px, py, sx, sy, rot)
            if i < n_rgbas:
                pr, pg, pb, pa = rgbas[i]
                self.dll.AddPoint(px, py, int(float(pr) * 255), int(float(pg) * 255),
                                  int(float(pb) * 255), float(pa) * a, radius)
            else:
                self.dll.AddPoint(px, py, r, g, b, a * so, radius)

    def _send_point(self, mob, a, w, h):
        pos = mob.get_location()
        sx, sy = manim_to_screen(pos[0], pos[1], w, h, pos[2])
        r, g, b = self._color(mob, a)
        self.dll.AddPoint(sx, sy, r, g, b, a, self._dot_radius(mob, h))
