"""The four convex primitives: square, rectangle, ellipse and circle."""

import math
import numpy as np
from real_time_manim.render.util import manim_to_screen, get_stroke_w, get_opacity, point_path_bounds, curve_segments


class PrimitiveMixin:


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
        # A size written in manim units converts with the frame height that is
        # actually on screen (see `_visible_frame_height`): `h / 8.0` pinned the
        # quad to the default 8-unit frame, so under a zooming camera the
        # square's POSITION followed the camera while its SIZE did not.
        scale = h / self._visible_frame_height()
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
        scale = h / self._visible_frame_height()
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
        scale = h / self._visible_frame_height()
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
            # Same rule as the circle's stroke (see curve_segments); an
            # elongated ellipse is sized by its major radius, where its
            # curvature is highest and it would facet first.
            segs = curve_segments(max(rx, ry))
            circumference = math.pi * (3 * (rx + ry) - math.sqrt((3 * rx + ry) * (rx + 3 * ry)))
            drawn = circumference * progress
            accumulated = 0.0
            prev_angle_rad = rot
            pts = [
                sx + math.cos(prev_angle_rad) * rx,
                sy - math.sin(prev_angle_rad) * ry,
            ]
            for j in range(1, segs + 1):
                if accumulated >= drawn:
                    break
                cur_angle_rad = rot + 2.0 * math.pi * j / segs
                px = sx + math.cos(cur_angle_rad) * rx
                py = sy - math.sin(cur_angle_rad) * ry
                seg_len = math.sqrt((px - pts[-2]) ** 2 + (py - pts[-1]) ** 2)
                if accumulated + seg_len <= drawn:
                    pts.append(px); pts.append(py)
                    accumulated += seg_len
                else:
                    frac = (drawn - accumulated) / seg_len if seg_len > 0 else 0
                    pts.append(pts[-2] + (px - pts[-2]) * frac)
                    pts.append(pts[-1] + (py - pts[-1]) * frac)
                    accumulated = drawn
            # One strip, not segs separate quads: see _emit_stroke_strip.
            self._emit_stroke_strip(pts, sw, cr, cg, cb, a)

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

    @staticmethod
    def _circle_round_radius(mob):
        """The shared anchor radius while the path still IS one circle, else None.

        `_send_circle` strokes a native disc from ONE radius, which is only
        correct while every anchor sits at that radius.  A `Circle` that was
        `stretch`ed, `apply_matrix`ed or had its points generated anisotropically
        keeps class `Circle` but its path is an ELLIPSE -- measured on
        `Circle(radius=0.9).stretch(1.6, 0)`: anchor distances 1.44 / 1.201 /
        0.9 / 1.201 / ... while CE strokes a 2.88x1.8 ellipse and RTM drew a
        uniform disc of radius 1.44 (`_oncurve_radius` reads `get_start()`,
        which is the x-extreme anchor on such a path).

        manim stores a cubic as 4 control points with the anchor at the stride
        (`points[0::4]`; the handles of an r=0.9 circle sit at 0.9311), so the
        check samples exactly the anchors.  The centre is the anchors' own bbox
        centre -- `get_center()` is family-wide and drifts when the circle
        carries submobjects.  A rotating circle stays round: its anchors keep a
        constant distance while the handles sweep.

        Returns the shared radius, or None when the anchors disagree; the
        caller then routes the shape through the point path, which tessellates
        the bezier that is actually there.
        """
        try:
            pts = getattr(mob, "points", None)
            if pts is None or len(pts) < 4:
                return None
            anchors = np.asarray(pts[0::4], dtype=float)
            lo = anchors.min(axis=0)
            hi = anchors.max(axis=0)
            c = (lo + hi) / 2.0
            d = np.linalg.norm(anchors[:, :2] - c[:2], axis=1)
            d = d[np.isfinite(d)]
            if len(d) == 0:
                return None
            r = float(d.min())
            if r <= 0.0:
                return None
            if float(d.max()) > r * 1.001:
                return None
            return r
        except Exception:
            return None

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
        scale_y = h / self._visible_frame_height()
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
            # Segments for the on-screen radius (see render/util.curve_segments):
            # a fixed 48 collapsed as the camera zoomed in -- at 8x the outline
            # was a 48-gon with a 4.6 px sagitta.  48 at the default zoom, so an
            # unzoomed frame is unchanged.
            segs = curve_segments(sr)
            circumference = 2.0 * math.pi * sr
            drawn = circumference * progress
            accumulated = 0.0
            prev_angle_rad = rot
            pts = [
                sx + math.cos(prev_angle_rad) * sr,
                sy - math.sin(prev_angle_rad) * sr,
            ]
            for j in range(1, segs + 1):
                if accumulated >= drawn:
                    break
                cur_angle_rad = rot + 2.0 * math.pi * j / segs
                px = sx + math.cos(cur_angle_rad) * sr
                py = sy - math.sin(cur_angle_rad) * sr
                seg_len = math.sqrt((px - pts[-2]) ** 2 + (py - pts[-1]) ** 2)
                if accumulated + seg_len <= drawn:
                    pts.append(px); pts.append(py)
                    accumulated += seg_len
                else:
                    frac = (drawn - accumulated) / seg_len if seg_len > 0 else 0
                    pts.append(pts[-2] + (px - pts[-2]) * frac)
                    pts.append(pts[-1] + (py - pts[-1]) * frac)
                    accumulated = drawn
            # One strip, not segs separate quads: see _emit_stroke_strip.
            self._emit_stroke_strip(pts, sw, cr, cg, cb, a)
