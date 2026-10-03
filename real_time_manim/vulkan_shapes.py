import ctypes
import math
import numpy as np
from real_time_manim.vulkan_util import manim_to_screen, rotate_point, get_fill_rgb, get_fill_rgb_raw, get_stroke_rgb, get_stroke_w, get_opacity
from real_time_manim.animations import get_anim_rotation


class ShapeMixin:
    def _color(self, mob, alpha=1.0):
        return get_fill_rgb(mob, alpha)

    def _fill_color(self, mob):
        return get_fill_rgb_raw(mob)

    def _stroke_color(self, mob):
        return get_stroke_rgb(mob)

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
        frame_height = 8.0
        try:
            from real_time_manim.camera_state import get_viewport
            viewport = get_viewport()
            if viewport is not None:
                frame_height = float(viewport.height) or 8.0
        except Exception:
            pass
        return sw_manim * 0.01 * (h / frame_height)

    def _rotate_point(self, x, y, cx, cy, angle):
        return rotate_point(x, y, cx, cy, angle)

    def _send_square(self, mob, a, w, h, rot, parent_offset=None):
        cx, cy, _ = mob.get_center()
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
        sx, sy = manim_to_screen(cx, cy, w, h)
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
        if so > 0:
            cr, cg, cb = self._stroke_color(mob)
            cr = int(cr * so)
            cg = int(cg * so)
            cb = int(cb * so)
            sw = max(1, round(self._stroke_width(mob)))
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
                    self.dll.AddLine(x0, y0, x1, y1, sw, cr, cg, cb, a)
                    remaining -= length
                else:
                    frac = remaining / length
                    ex = x0 + (x1 - x0) * frac
                    ey = y0 + (y1 - y0) * frac
                    self.dll.AddLine(x0, y0, ex, ey, sw, cr, cg, cb, a)
                    remaining = 0

    def _send_rectangle(self, mob, a, w, h, rot, parent_offset=None):
        cx, cy, _ = mob.get_center()
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
        sx, sy = manim_to_screen(cx, cy, w, h)
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
        progress = getattr(mob, '_vulkan_progress', 1.0)
        if fo <= 0 and so <= 0:
            return
        if progress <= 0:
            return
        fr, fg, fb = self._fill_color(mob)
        self.dll.AddRect(sx, sy, hw, hh, rot, fr, fg, fb, 0, 0, 0, 0.0, progress, a * fo)
        if so > 0:
            cr, cg, cb = self._stroke_color(mob)
            cr = int(cr * so)
            cg = int(cg * so)
            cb = int(cb * so)
            sw = max(1, round(self._stroke_width(mob)))
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
                    self.dll.AddLine(x0, y0, x1, y1, sw, cr, cg, cb, a)
                    remaining -= length
                else:
                    frac = remaining / length
                    ex = x0 + (x1 - x0) * frac
                    ey = y0 + (y1 - y0) * frac
                    self.dll.AddLine(x0, y0, ex, ey, sw, cr, cg, cb, a)
                    remaining = 0

    def _send_ellipse(self, mob, a, w, h, rot, parent_offset=None):
        cx, cy, _ = mob.get_center()
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
        sx, sy = manim_to_screen(cx, cy, w, h)
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
        if so > 0:
            cr, cg, cb = self._stroke_color(mob)
            cr = int(cr * so)
            cg = int(cg * so)
            cb = int(cb * so)
            sw = max(1, round(self._stroke_width(mob)))
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
                    self.dll.AddLine(prev_px, prev_py, px, py, sw, cr, cg, cb, a)
                    accumulated += seg_len
                else:
                    frac = (drawn - accumulated) / seg_len if seg_len > 0 else 0
                    ex = prev_px + (px - prev_px) * frac
                    ey = prev_py + (py - prev_py) * frac
                    self.dll.AddLine(prev_px, prev_py, ex, ey, sw, cr, cg, cb, a)
                    accumulated = drawn
                prev_px, prev_py = px, py

    def _send_circle(self, mob, a, w, h, rot, parent_offset=None):
        cx, cy, _ = mob.get_center()
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
        sx, sy = manim_to_screen(cx, cy, w, h)
        scale_y = h / 8.0
        sr = (mob.width / 2.0) * scale_y * grow_scale
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
            cr = int(cr * so)
            cg = int(cg * so)
            cb = int(cb * so)
            sw = max(1, round(self._stroke_width(mob)))
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
                    self.dll.AddLine(prev_px, prev_py, px, py, sw, cr, cg, cb, a)
                    accumulated += seg_len
                else:
                    frac = (drawn - accumulated) / seg_len if seg_len > 0 else 0
                    ex = prev_px + (px - prev_px) * frac
                    ey = prev_py + (py - prev_py) * frac
                    self.dll.AddLine(prev_px, prev_py, ex, ey, sw, cr, cg, cb, a)
                    accumulated = drawn
                prev_px, prev_py = px, py

    def _send_arrow(self, mob, a, w, h, rot, parent_offset=None):
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
            cx, cy, _ = mob.get_center()
            if parent_offset is not None:
                cx += parent_offset[0]; cy += parent_offset[1]
            scx, scy = manim_to_screen(cx, cy, w, h)
            sx1, sy1 = self._rotate_point(sx1, sy1, scx, scy, rot)
            sx2, sy2 = self._rotate_point(sx2, sy2, scx, scy, rot)
        r, g, b = self._stroke_color(mob)
        sw = max(1, round(self._stroke_width(mob)))
        progress = getattr(mob, '_vulkan_progress', 1.0)
        if progress <= 0:
            return
        dx = sx2 - sx1
        dy = sy2 - sy1
        length = math.hypot(dx, dy)
        if length <= 0:
            return
        ux = dx / length
        uy = dy / length
        arrow_len_manim = math.hypot(e[0] - s[0], e[1] - s[1])
        max_tip_ratio = getattr(mob, 'max_tip_length_to_length_ratio', 0.25)
        default_tip_length = getattr(mob, 'tip_length', 0.35)
        tip_manim = min(default_tip_length, max_tip_ratio * arrow_len_manim)
        scale_y = h / 8.0
        head_len = tip_manim * scale_y
        head_w = head_len * 0.5
        base_x = sx2 - ux * head_len
        base_y = sy2 - uy * head_len
        if progress >= 1.0:
            self.dll.AddLine(sx1, sy1, base_x, base_y, sw, r, g, b, a)
        else:
            ex = sx1 + (base_x - sx1) * progress
            ey = sy1 + (base_y - sy1) * progress
            self.dll.AddLine(sx1, sy1, ex, ey, sw, r, g, b, a)
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

    def _send_line(self, mob, a, w, h, rot, parent_offset=None):
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
            cx, cy, _ = mob.get_center()
            if parent_offset is not None:
                cx += parent_offset[0]; cy += parent_offset[1]
            scx, scy = manim_to_screen(cx, cy, w, h)
        sx1, sy1 = self._rotate_point(sx1, sy1, scx, scy, rot)
        sx2, sy2 = self._rotate_point(sx2, sy2, scx, scy, rot)
        r, g, b = self._stroke_color(mob)
        sw = max(1, round(self._stroke_width(mob)))
        progress = getattr(mob, '_vulkan_progress', 1.0)
        if progress <= 0:
            return
        if progress >= 1.0:
            self.dll.AddLine(sx1, sy1, sx2, sy2, sw, r, g, b, a)
        else:
            ex = sx1 + (sx2 - sx1) * progress
            ey = sy1 + (sy2 - sy1) * progress
            self.dll.AddLine(sx1, sy1, ex, ey, sw, r, g, b, a)

    def _send_dot(self, mob, a, w, h):
        cx, cy, _ = mob.get_center()
        sx, sy = manim_to_screen(cx, cy, w, h)
        scale_y = h / 8.0
        rad = (mob.width / 2.0) * scale_y
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
        cx, cy, _ = mob.get_center()
        if parent_offset is not None:
            cx += parent_offset[0]
            cy += parent_offset[1]
        scx, scy = manim_to_screen(cx, cy, w, h)
        sx1, sy1 = self._rotate_point(sx1, sy1, scx, scy, rot)
        sx2, sy2 = self._rotate_point(sx2, sy2, scx, scy, rot)
        so = get_opacity(mob, 'stroke', 1.0)
        if so <= 0:
            return
        r, g, b = self._stroke_color(mob)
        r, g, b = int(r * so), int(g * so), int(b * so)
        scale = h / 8.0
        sw = max(1, round(self._stroke_width(mob)))
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
            self.dll.AddDashedLine(sx1, sy1, sx2, sy2, sw, r, g, b, dl, gl, a)
        else:
            ex = sx1 + (sx2 - sx1) * progress
            ey = sy1 + (sy2 - sy1) * progress
            self.dll.AddDashedLine(sx1, sy1, ex, ey, sw, r, g, b, dl, gl, a)

    def _stroke_polyline_with_progress(self, flat, closed, lower, upper,
                                       r, g, b, width, alpha):
        """Stroke the [lower, upper] stretch of a screen-space polyline.

        ``flat`` is x0,y0,x1,y1,... in screen pixels; ``lower``/``upper`` are
        fractions of the total length.  Shared by the polygon and arc senders so
        a partially drawn shape (Create / ShowPartial / ShowPassingFlash) is
        stroked the same way whichever sender handles it (plan 4.2).
        """
        n = len(flat) // 2
        if n < 2:
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
                self.dll.AddLine(x0, y0, x1, y1, width, r, g, b, alpha)
                remaining -= el
            else:
                frac = remaining / el if el > 0 else 0.0
                ex = x0 + (x1 - x0) * frac
                ey = y0 + (y1 - y0) * frac
                self.dll.AddLine(x0, y0, ex, ey, width, r, g, b, alpha)
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
        cx, cy, _ = mob.get_center()
        if parent_offset is not None:
            cx += parent_offset[0]
            cy += parent_offset[1]
        sx, sy = manim_to_screen(cx, cy, w, h)
        flat = self._stroke_points_polyline(points, w, h, parent_offset, rot, sx, sy)
        if len(flat) < 4:
            return
        r, g, b = self._stroke_color(mob)
        sw = max(1, round(self._stroke_width(mob)))
        lower = getattr(mob, '_vulkan_progress_lower', 0.0)
        upper = getattr(mob, '_vulkan_progress_upper', progress)
        self._stroke_polyline_with_progress(flat, False, lower, upper,
                                            int(r * so), int(g * so), int(b * so),
                                            sw, a)

    def _send_polygon(self, mob, verts, alpha=1.0, rot_override=None, parent_offset=None):
        w, h = self.win_w, self.win_h
        cx, cy, _ = mob.get_center()
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

        sx, sy = manim_to_screen(cx, cy, w, h)
        br, bg, bb = self._stroke_color(mob)
        bw = self._stroke_width(mob)
        rot = -get_anim_rotation(mob) if rot_override is None else rot_override
        progress = getattr(mob, '_vulkan_progress', 1.0)
        has_bounds = hasattr(mob, '_vulkan_progress_upper')
        if has_bounds:
            progress_lower = getattr(mob, '_vulkan_progress_lower', 0.0)
            progress_upper = getattr(mob, '_vulkan_progress_upper', 1.0)
        else:
            progress_lower = 0.0
            progress_upper = progress
        try:
            fo = float(mob.fill_rgbas[:, 3].max())
        except Exception:
            fo = get_opacity(mob, 'fill', 1.0)
        if progress <= 0 and not has_bounds:
            return
        if fo <= 0:
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
            so = get_opacity(mob, 'stroke', 1.0)
            if so <= 0:
                return
            self._stroke_polyline_with_progress(
                flat, True, progress_lower, progress_upper,
                int(br * so), int(bg * so), int(bb * so),
                max(1, round(bw)), alpha)
        else:
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
            fr, fg, fb = self._fill_color(mob)
            arr = (ctypes.c_float * len(flat))(*flat)
            self.dll.AddPolygon(
                sx, sy, fr, fg, fb, 0, 0, 0, 0.0,
                len(verts), arr, 0 if has_bounds else progress, alpha * fo, 1
            )
            so = get_opacity(mob, 'stroke', 1.0)
            if so > 0:
                self._stroke_polyline_with_progress(
                    flat, True, progress_lower, progress_upper,
                    int(br * so), int(bg * so), int(bb * so),
                    max(1, round(bw)), alpha)

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
        cx, cy, _ = mob.get_center()
        sx, sy = manim_to_screen(cx, cy, w, h)
        try:
            points = mob.get_points()
        except Exception:
            return
        for p in points:
            vx, vy = float(p[0]), float(p[1])
            if parent_offset is not None:
                vx += parent_offset[0]
                vy += parent_offset[1]
            vz = float(p[2]) if len(p) > 2 else 0.0
            px, py = manim_to_screen(vx, vy, w, h, vz)
            px, py = self._rotate_point(px, py, sx, sy, rot)
            self.dll.AddPoint(px, py, r, g, b, a * so)

    def _send_point(self, mob, a, w, h):
        pos = mob.get_location()
        sx, sy = manim_to_screen(pos[0], pos[1], w, h)
        r, g, b = self._color(mob, a)
        self.dll.AddPoint(sx, sy, r, g, b, a)
