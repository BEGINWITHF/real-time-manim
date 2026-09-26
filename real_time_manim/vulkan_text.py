import ctypes
import math
from real_time_manim.vulkan_util import manim_to_screen, get_fill_rgb
from real_time_manim.animations import get_anim_opacity


class TextMixin:
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
                        vx, vy = manim_to_screen(p[0], p[1], w, h)
                        flat.append(vx)
                        flat.append(vy)
                        flat.append(0.0)
                arr = (ctypes.c_float * len(flat))(*flat)
                self.dll.AddBezierPath(
                    arr, num_segs * 4,
                    sr, sg, sb, 3.0,
                    sr, sg, sb, 1.0,
                    1.0, 1, 1, alpha,
                )
            except Exception as e:
                import traceback
                print('[ERROR] _send_transformed_text: ' + str(e))
                traceback.print_exc()

    def _send_text_write(self, mob, letter_alphas, w, h, alpha=1.0):
        try:
            c = mob.get_color()
            base_r, base_g, base_b = round(float(c[0]) * 255), round(float(c[1]) * 255), round(float(c[2]) * 255)
        except Exception:
            base_r, base_g, base_b = 255, 255, 255
        if base_r == 0 and base_g == 0 and base_b == 0:
            base_r, base_g, base_b = 255, 255, 255
        for i, sub in enumerate(mob.submobjects):
            sub_alpha = letter_alphas.get(i, 0.0)
            if sub_alpha <= 0.001:
                continue

            pts = sub.get_points()
            if len(pts) < 8:
                continue

            flat = []
            for p in pts:
                sx, sy = manim_to_screen(p[0], p[1], w, h)
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
            sr, sg, sb = base_r, base_g, base_b
            stroke_width = 2.0 * stroke_fade
            show_stroke = 1 if stroke_width > 0.001 else 0

            self.dll.AddBezierPath(
                arr, n,
                sr, sg, sb, stroke_width,
                base_r, base_g, base_b, fill_alpha,
                stroke_progress, show_stroke, 1 if fill_alpha > 0 else 0, alpha,
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

    def _send_vmobject(self, mob, a, w, h, parent_offset=None, rot=0.0, is_text=False):
        try:
            pts = mob.get_points()
        except Exception:
            return

        if len(pts) == 0 and hasattr(mob, 'submobjects') and mob.submobjects:
            # Propagate _grow_scale/_grow_point to submobjects so animations
            # like Indicate that set them on a VGroup/Text parent correctly
            # scale individual child pieces.
            pg_gs = getattr(mob, '_grow_scale', None)
            pg_gp = getattr(mob, '_grow_point', None)
            for sub in mob.submobjects:
                need_gs = pg_gs is not None and not hasattr(sub, '_grow_scale')
                need_gp = pg_gp is not None and not hasattr(sub, '_grow_point')
                if need_gs:
                    sub._grow_scale = pg_gs
                if need_gp:
                    sub._grow_point = pg_gp
                self._send_vmobject(sub, a, w, h, parent_offset, rot, is_text=is_text)
                if need_gs:
                    del sub._grow_scale
                if need_gp:
                    del sub._grow_point
            return

        from manim.animation.changing import TracedPath
        is_polyline = isinstance(mob, TracedPath)

        if is_polyline and len(pts) >= 2:
            about = getattr(mob, '_rotation_about_point', None)
            if about is not None:
                cx, cy = float(about[0]), float(about[1])
            else:
                cx, cy, _ = mob.get_center()
            sr, sg, sb, sa = 1, 1, 1, 1
            try:
                srgbas = mob.get_stroke_rgbas()
                if len(srgbas) > 0:
                    sr, sg, sb, sa = float(srgbas[0][0]), float(srgbas[0][1]), float(srgbas[0][2]), float(srgbas[0][3])
            except Exception:
                sr, sg, sb = 1, 1, 1
                sa = 1.0
            so = mob.get_stroke_opacity() if hasattr(mob, 'get_stroke_opacity') else 1.0
            sw_manim = 2.0
            try:
                raw = mob.get_stroke_width()
                if isinstance(raw, (int, float)):
                    sw_manim = float(raw)
                elif hasattr(raw, '__len__') and len(raw) > 0:
                    sw_manim = float(raw[0])
            except Exception:
                pass
            sw = max(1, int(round(sw_manim * 0.01 * (h / 8.0))))

            raw_pts = []
            cos_a = math.cos(rot)
            sin_a = math.sin(rot)
            grow_scale = getattr(mob, '_grow_scale', 1.0)
            grow_pt = getattr(mob, '_grow_point', None)
            for i in range(len(pts)):
                px, py = float(pts[i][0]), float(pts[i][1])
                if grow_scale != 1.0 and grow_pt is not None:
                    px = grow_pt[0] + (px - grow_pt[0]) * grow_scale
                    py = grow_pt[1] + (py - grow_pt[1]) * grow_scale
                dx, dy = px - cx, py - cy
                rx = dx * cos_a - dy * sin_a + cx
                ry = dx * sin_a + dy * cos_a + cy
                raw_pts.append((rx, ry))

            so_attr = getattr(mob, 'stroke_opacity', 1.0)
            if isinstance(so_attr, (list, tuple)) and len(so_attr) == 2:
                sri = round(sr * 255 * a)
                sgi = round(sg * 255 * a)
                sbi = round(sb * 255 * a)
                so_start, so_end = float(so_attr[0]), float(so_attr[1])
                so_arr = []
                n_raw = len(raw_pts)
                for i in range(n_raw):
                    t = i / max(1, n_raw - 1)
                    so_arr.append(so_start + (so_end - so_start) * t)
            else:
                sri = round(sr * 255 * sa * a)
                sgi = round(sg * 255 * sa * a)
                sbi = round(sb * 255 * sa * a)
                so_arr = None

            if len(raw_pts) >= 2:
                smooth_pts = [raw_pts[0]]
                smooth_so = [so_arr[0]] if so_arr else None
                for i in range(len(raw_pts) - 1):
                    x0, y0 = raw_pts[i]
                    x1, y1 = raw_pts[i + 1]
                    dist = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
                    steps = max(1, int(dist / 0.15))
                    for j in range(1, steps + 1):
                        t = j / steps
                        smooth_pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
                        if smooth_so is not None:
                            so0 = so_arr[i]
                            so1 = so_arr[i + 1]
                            smooth_so.append(so0 + (so1 - so0) * t)
                raw_pts = smooth_pts
                so_arr = smooth_so

            coords = (ctypes.c_float * (len(raw_pts) * 2))()
            for i in range(len(raw_pts)):
                x0, y0 = raw_pts[i]
                if parent_offset is not None:
                    x0 += parent_offset[0]; y0 += parent_offset[1]
                sx, sy = manim_to_screen(x0, y0, w, h)
                coords[i * 2] = sx
                coords[i * 2 + 1] = sy

            alphas = (ctypes.c_float * len(raw_pts))()
            if so_arr is not None:
                for i in range(len(raw_pts)):
                    alphas[i] = max(0.0, min(1.0, so_arr[i] * a))
            else:
                for i in range(len(raw_pts)):
                    alphas[i] = a
            self.dll.AddLineStrip(coords, alphas, len(raw_pts), sw, sri, sgi, sbi, 1.0)
            return
        else:
            if len(pts) < 2:
                return
            if len(pts) < 4:
                sr, sg, sb = 1, 1, 1
                try:
                    srgbas = mob.get_stroke_rgbas()
                    if len(srgbas) > 0:
                        sr, sg, sb = float(srgbas[0][0]), float(srgbas[0][1]), float(srgbas[0][2])
                except Exception:
                    pass
                sw = self._stroke_width(mob)
                sri = int(sr * 255 * a)
                sgi = int(sg * 255 * a)
                sbi = int(sb * 255 * a)
                for i in range(len(pts) - 1):
                    px0, py0 = float(pts[i][0]), float(pts[i][1])
                    px1, py1 = float(pts[i+1][0]), float(pts[i+1][1])
                    if parent_offset is not None:
                        px0 += parent_offset[0]; py0 += parent_offset[1]
                        px1 += parent_offset[0]; py1 += parent_offset[1]
                    sx0, sy0 = manim_to_screen(px0, py0, w, h)
                    sx1, sy1 = manim_to_screen(px1, py1, w, h)
                    self.dll.AddLine(sx0, sy0, sx1, sy1, max(1, round(sw)), sri, sgi, sbi, a)
                return
            cx, cy, _ = mob.get_center()
            cos_a = math.cos(rot)
            sin_a = math.sin(rot)
            flat = []
            grow_scale = getattr(mob, '_grow_scale', 1.0)
            grow_pt = getattr(mob, '_grow_point', None)
            # Approach-A baseline shift, set on text characters at draw time so
            # a descender-heavy word is lowered onto its shared baseline without
            # ever mutating the mobject's points (no positional jitter).
            b_dy = float(getattr(mob, '_baseline_dy', 0.0) or 0.0)
            for p in pts:
                px, py = p[0], p[1]
                if grow_scale != 1.0 and grow_pt is not None:
                    px = grow_pt[0] + (px - grow_pt[0]) * grow_scale
                    py = grow_pt[1] + (py - grow_pt[1]) * grow_scale
                dx, dy = px - cx, py - cy
                px = dx * cos_a - dy * sin_a + cx
                py = dx * sin_a + dy * cos_a + cy
                if parent_offset is not None:
                    px += parent_offset[0]
                    py += parent_offset[1]
                py += b_dy
                sx, sy = manim_to_screen(px, py, w, h)
                flat.append(sx)
                flat.append(sy)
                flat.append(0.0)

        n = len(flat) // 3
        if n < 8:
            # Fill: render as a convex polygon when the mobject has fill opacity
            fo = 0.0
            try:
                frgbas = mob.get_fill_rgbas()
                if len(frgbas) > 0:
                    fo = float(frgbas[0][3])
            except Exception:
                fo = mob.get_fill_opacity() if hasattr(mob, 'get_fill_opacity') else 0.0
            if fo > 0.01 and n >= 3:
                fr, fg, fb = 0, 0, 0
                try:
                    frgbas = mob.get_fill_rgbas()
                    if len(frgbas) > 0:
                        fr = float(frgbas[0][0])
                        fg = float(frgbas[0][1])
                        fb = float(frgbas[0][2])
                except Exception:
                    pass
                if fr == 0 and fg == 0 and fb == 0:
                    try:
                        c = mob.get_color()
                        fr, fg, fb = float(c[0]), float(c[1]), float(c[2])
                    except Exception:
                        fr, fg, fb = 1.0, 1.0, 1.0
                fri = round(fr * 255)
                fgi = round(fg * 255)
                fbi = round(fb * 255)
                fill_alpha = min(1.0, fo * a)
                fverts = (ctypes.c_float * (n * 2))()
                for i in range(n):
                    fverts[i * 2] = flat[i * 3]
                    fverts[i * 2 + 1] = flat[i * 3 + 1]
                self.dll.AddPolygon(
                    flat[0], flat[1], fri, fgi, fbi, fri, fgi, fbi, 0,
                    n, fverts, 1.0, fill_alpha, 1,
                )
            if n >= 2:
                sr, sg, sb = 1, 1, 1
                try:
                    srgbas = mob.get_stroke_rgbas()
                    if len(srgbas) > 0:
                        sr, sg, sb = float(srgbas[0][0]), float(srgbas[0][1]), float(srgbas[0][2])
                except Exception:
                    pass
                sw = self._stroke_width(mob)
                sri = int(sr * 255 * a)
                sgi = int(sg * 255 * a)
                sbi = int(sb * 255 * a)
                for i in range(n - 1):
                    x0, y0 = flat[i * 3], flat[i * 3 + 1]
                    x1, y1 = flat[(i + 1) * 3], flat[(i + 1) * 3 + 1]
                    self.dll.AddLine(x0, y0, x1, y1, max(1, round(sw)), sri, sgi, sbi, a)
            return

        fr, fg, fb, fa = 0, 0, 0, 0
        try:
            frgbas = mob.get_fill_rgbas()
            if len(frgbas) > 0:
                fr, fg, fb, fa = float(frgbas[0][0]), float(frgbas[0][1]), float(frgbas[0][2]), float(frgbas[0][3])
        except Exception:
            pass
        if fr == 0 and fg == 0 and fb == 0:
            try:
                c = mob.get_color()
                fr, fg, fb = float(c[0]), float(c[1]), float(c[2])
                fa = 1.0
            except Exception:
                fr, fg, fb = 1.0, 1.0, 1.0
                fa = 1.0
            if is_text and fr == 0 and fg == 0 and fb == 0:
                fr, fg, fb = 1.0, 1.0, 1.0

        sr, sg, sb, sa = 1, 1, 1, 1
        try:
            srgbas = mob.get_stroke_rgbas()
            if len(srgbas) > 0:
                sr, sg, sb, sa = float(srgbas[0][0]), float(srgbas[0][1]), float(srgbas[0][2]), float(srgbas[0][3])
        except Exception:
            sr, sg, sb = fr, fg, fb
            sa = 1.0
        if sr == 0 and sg == 0 and sb == 0:
            sr, sg, sb = fr, fg, fb
            if is_text and sr == 0 and sg == 0 and sb == 0:
                sr, sg, sb = 1.0, 1.0, 1.0
        if sa <= 0:
            try:
                for fm in mob.family_members_with_points():
                    srgba = fm.stroke_rgbas
                    if len(srgba) > 0:
                        s = float(srgba[0][3])
                        if s > sa:
                            sa = s
            except Exception:
                pass
        if sa <= 0:
            sa = 1.0

        try:
            so = float(mob.stroke_rgbas[:, 3].max())
        except Exception:
            so = mob.get_stroke_opacity() if hasattr(mob, 'get_stroke_opacity') else 1.0
        if so <= 0:
            try:
                for fm in mob.family_members_with_points():
                    s = float(fm.stroke_rgbas[:, 3].max())
                    if s > so:
                        so = s
            except Exception:
                pass
        sw = self._stroke_width(mob)
        fill_alpha = min(1.0, fa * a)
        # stroke_alpha uses so (max stroke-rgba alpha) — consistent
        # with how fill_alpha uses fa (fill-rgba alpha from first element)
        stroke_alpha = min(1.0, so * a)
        stroke_w = max(1.0, sw) if sw > 0 else 0
        # Default per-vertex stroke alpha; the latex write-stroke synthesis
        # overrides this to fade the outline out as the fill comes in.
        stroke_point_alpha = a

        progress = getattr(mob, '_vulkan_progress', 1.0)
        has_bounds = hasattr(mob, '_vulkan_progress_upper')
        if has_bounds:
            progress_lower = getattr(mob, '_vulkan_progress_lower', 0.0)
            progress_upper = getattr(mob, '_vulkan_progress_upper', 1.0)
        else:
            progress_lower = 0.0
            progress_upper = progress
        sri = round(sr * 255 * stroke_alpha)
        sgi = round(sg * 255 * stroke_alpha)
        sbi = round(sb * 255 * stroke_alpha)
        fri = round(fr * 255)
        fgi = round(fg * 255)
        fbi = round(fb * 255)

        show_fill = 1 if fill_alpha > 0.01 and progress_lower == 0.0 else 0
        do_stroke = stroke_alpha > 0.01 and stroke_w > 0

        if is_text and fill_alpha > 0.01:
            do_stroke = False

        if not do_stroke and getattr(mob, '_transforming', False) and sw > 0 and not is_text:
            sr, sg, sb = fr, fg, fb
            stroke_alpha = max(stroke_alpha, a)
            sri = round(sr * 255 * stroke_alpha)
            sgi = round(sg * 255 * stroke_alpha)
            sbi = round(sb * 255 * stroke_alpha)
            do_stroke = True

        # LaTeX glyphs (VMobjectFromSVGPath) carry no stroke (sw == 0), and the
        # native tessellate_fill pops the whole fill in at once.  During a
        # Write/Create the DrawBorderThenFill tags the glyph with _write_active;
        # while that is set we synthesize a stroke from the fill color so the
        # hand-writing outline reveal is visible.  The stroke fades out via its
        # per-vertex alpha as the fill fades in (color stays the glyph color),
        # giving a smooth write-then-fill with no dip in between.
        if (not do_stroke and not is_text and sw == 0
                and getattr(mob, '_write_active', False)):
            stroke_point_alpha = max(0.0, 1.0 - fill_alpha * 1.2) * a
            sr, sg, sb = fr, fg, fb
            sri = round(sr * 255)
            sgi = round(sg * 255)
            sbi = round(sb * 255)
            stroke_w = 2.0
            do_stroke = True

        arr = (ctypes.c_float * len(flat))(*flat)
        n = (n // 4) * 4
        self.dll.AddBezierPath(
            arr, n,
            sri, sgi, sbi, stroke_w,
            fri, fgi, fbi, fill_alpha,
            progress, 0, show_fill, a,
        )

        if do_stroke:
            seg_count = n // 4
            vis_start = int(seg_count * progress_lower)
            vis_end = int(seg_count * progress_upper)
            stroke_pts = []
            for si in range(vis_start, min(seg_count, vis_end + 1)):
                idx = si * 4
                p0x, p0y = flat[idx*3], flat[idx*3+1]
                p1x, p1y = flat[(idx+1)*3], flat[(idx+1)*3+1]
                p2x, p2y = flat[(idx+2)*3], flat[(idx+2)*3+1]
                p3x, p3y = flat[(idx+3)*3], flat[(idx+3)*3+1]
                # flat holds screen-space control points.  Subdivide each cubic
                # to roughly STEP_PX screen pixels per straight run so strongly
                # curved outlines (e.g. a Square warped by exp -> a wide arc,
                # test 63) don't come out faceted.  8 fixed samples/seg was too
                # coarse there; native tessellation uses 64.  Length-aware
                # sampling keeps gentle/low-curvature segments cheap too.
                STEP_PX = 3.0
                cpoly = (math.hypot(p1x-p0x, p1y-p0y) + math.hypot(p2x-p1x, p2y-p1y)
                         + math.hypot(p3x-p2x, p3y-p2y))
                chord = math.hypot(p3x-p0x, p3y-p0y)
                est = (cpoly + chord) * 0.5
                seg_samples = int(max(8.0, min(256.0, math.ceil(est / STEP_PX))))
                for s in range(seg_samples + 1):
                    t = s / seg_samples
                    u = 1.0 - t
                    bx = u*u*u*p0x + 3*u*u*t*p1x + 3*u*t*t*p2x + t*t*t*p3x
                    by = u*u*u*p0y + 3*u*u*t*p1y + 3*u*t*t*p2y + t*t*t*p3y
                    stroke_pts.append((bx, by))
            if len(stroke_pts) >= 2:
                coords = (ctypes.c_float * (len(stroke_pts) * 2))()
                alphas = (ctypes.c_float * len(stroke_pts))()
                for i, (px, py) in enumerate(stroke_pts):
                    coords[i * 2] = px
                    coords[i * 2 + 1] = py
                    alphas[i] = stroke_point_alpha
                self.dll.AddLineStrip(coords, alphas, len(stroke_pts), int(stroke_w), sri, sgi, sbi, 1.0)

    def _send_text_stroke(self, mob, a, w, h, parent_offset=None):
        if not hasattr(mob, 'family_members_with_points'):
            return
        for fm in mob.family_members_with_points():
            sw_attr = fm.get_stroke_width() if hasattr(fm, 'get_stroke_width') else 0
            if sw_attr <= 0:
                continue
            self._send_vmobject(fm, a, w, h, parent_offset)
