import ctypes
import math
from real_time_manim.vulkan_util import manim_to_screen, get_fill_rgb, get_opacity, point_path_bounds, shaded_fill_rgb
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
                sx, sy = manim_to_screen(p[0], p[1], w, h, p[2])
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

    def _small_path_chords(self, flat, n):
        """Straight runs to stroke for a path carrying fewer than 8 points.

        ``flat`` is screen-space control points as x,y,z triples.  A VMobject
        stores its path as runs of four control points per cubic -- or
        ``1 + 3k`` when it was built curve by curve -- so a FOUR-point path is
        ONE cubic segment, not a polygon.  Chords straight between the raw
        control points are only right when the segment really is straight:
        ``ArcsAndCurves``' ``CubicBezier(-1L, -0.4L+0.9U, 0.4R-0.9U, 1R)`` has
        4 points and was stroked as the 36 x 108 px triangle through its
        handles while CE draws the 27 x 31 px curve (report R10-1; probe
        bezier_probe.py, three AddLine exactly along p0->p1->p2->p3).

        Curved segments are sampled with the same length-aware rule the
        8-plus-point path uses (STEP_PX = 3, 8..256 samples), so both branches
        agree on where a cubic lies; a segment whose handles sit on its chord
        stays one chord, which keeps a straight glyph or Line costing a single
        primitive instead of `samples`.
        """
        straight_px = 0.75   # handles this close to the chord are invisible
        step_px = 3.0        # same rule as the tessellation below (vulkan_text)
        stride = None
        n_seg = 0
        if n % 4 == 0:
            stride, n_seg = 4, n // 4
        elif (n - 1) % 3 == 0:
            stride, n_seg = 3, (n - 1) // 3
        if stride is None:
            # Not a cubic layout (5 or 6 anchors): the raw points ARE the path.
            return [(flat[i * 3], flat[i * 3 + 1],
                     flat[(i + 1) * 3], flat[(i + 1) * 3 + 1])
                    for i in range(n - 1)]
        runs = []
        for si in range(n_seg):
            idx = si * stride
            if idx + 3 >= n:
                break
            p0x, p0y = flat[idx * 3], flat[idx * 3 + 1]
            p1x, p1y = flat[(idx + 1) * 3], flat[(idx + 1) * 3 + 1]
            p2x, p2y = flat[(idx + 2) * 3], flat[(idx + 2) * 3 + 1]
            p3x, p3y = flat[(idx + 3) * 3], flat[(idx + 3) * 3 + 1]
            dx, dy = p3x - p0x, p3y - p0y
            chord = math.hypot(dx, dy)
            if chord > 1e-9:
                # distance of a handle from the chord LINE: the curve lies in
                # the convex hull of its control points, so it cannot leave it.
                off1 = abs(dx * (p0y - p1y) - (p0x - p1x) * dy) / chord
                off2 = abs(dx * (p0y - p2y) - (p0x - p2x) * dy) / chord
            else:
                off1 = math.hypot(p1x - p0x, p1y - p0y)
                off2 = math.hypot(p2x - p0x, p2y - p0y)
            if max(off1, off2) <= straight_px:
                seg = [(p0x, p0y), (p3x, p3y)]
            else:
                cpoly = (math.hypot(p1x - p0x, p1y - p0y)
                         + math.hypot(p2x - p1x, p2y - p1y)
                         + math.hypot(p3x - p2x, p3y - p2y))
                est = (cpoly + chord) * 0.5
                samples = int(max(8.0, min(256.0, math.ceil(est / step_px))))
                seg = []
                for s in range(samples + 1):
                    t = s / samples
                    u = 1.0 - t
                    seg.append((u * u * u * p0x + 3 * u * u * t * p1x
                                + 3 * u * t * t * p2x + t * t * t * p3x,
                                u * u * u * p0y + 3 * u * u * t * p1y
                                + 3 * u * t * t * p2y + t * t * t * p3y))
            # Stitch onto the previous run only when the anchor really is the
            # same point; a `1 + 3k` path shares it, a run of independent
            # 4-point segments does not and must not get a chord between them.
            if runs and (abs(runs[-1][-1][0] - seg[0][0]) < 1e-6
                         and abs(runs[-1][-1][1] - seg[0][1]) < 1e-6):
                runs[-1].extend(seg[1:])
            else:
                runs.append(seg)
        chords = []
        for run in runs:
            for i in range(len(run) - 1):
                chords.append((run[i][0], run[i][1],
                               run[i + 1][0], run[i + 1][1]))
        return chords

    def _send_vmobject(self, mob, a, w, h, parent_offset=None, rot=0.0, is_text=False, exact_width=False):
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
            so = get_opacity(mob, 'stroke', 1.0)
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
                    self._emit_stroke(sx0, sy0, sx1, sy1, sw, sri, sgi, sbi, a)
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
                pz = float(p[2]) if len(p) > 2 else 0.0
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
                # z must reach the viewport: a ThreeDCamera rotates the point
                # before the screen mapping, so dropping it flattens every 3D
                # VMobject (a Surface collapsed into thin stray strips).  native
                # AddBezierPath reads stride-3 points but only x,y, so the third
                # slot stays 0 here.
                sx, sy = manim_to_screen(px, py, w, h, pz)
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
                fo = get_opacity(mob, 'fill', 0.0)
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
                # `a` is RTM's own animation registry (`state.py`), which
                # manim's FadeIn never writes -- a fade travels through
                # stroke_rgbas instead (report R10-3).  This branch used `a`
                # alone, so ArcsAndCurves' 4-point CubicBezier -- one cubic
                # segment, i.e. exactly this path -- was stroked at full
                # brightness on frame 0 of FadeIn(top) and never ramped, while
                # CE is empty for 5 frames and only then fades in (report
                # R10-4).  The >=8 branch already uses
                # `stroke_alpha = min(1, so * a)`; do the same here, and skip
                # the stroke when none of it is visible.
                try:
                    so = float(mob.stroke_rgbas[:, 3].max())
                except Exception:
                    so = get_opacity(mob, 'stroke', 1.0)
                stroke_alpha = min(1.0, so * a)
                sw = self._stroke_width(mob)
                sri = int(sr * 255 * a)
                sgi = int(sg * 255 * a)
                sbi = int(sb * 255 * a)
                # `_small_path_chords`, not raw points: below 8 points the
                # path may still be a cubic (4 points = ONE segment), and
                # chords through its handles drew the control hull instead of
                # the curve (report R10-1).
                if stroke_alpha > 0.004:
                    for x0, y0, x1, y1 in self._small_path_chords(flat, n):
                        self._emit_stroke(x0, y0, x1, y1, sw, sri, sgi, sbi,
                                          stroke_alpha)
            return

        fr, fg, fb, fa = 0, 0, 0, 0
        _fa_measured = False
        try:
            frgbas = mob.get_fill_rgbas()
            if len(frgbas) > 0:
                _fa_measured = True
                # manim keeps a *gradient* fill as several stops -- e.g.
                # `set_sheen(0.4, RIGHT)` leaves [dim, bright].  Reading only
                # stop 0 painted every gradient/sheen fill at its darkest stop
                # (~25% dim): measured on VobjectManagerPathOperations the same
                # region read '.' (52-78) in RTM against ':' (78-104) in CE,
                # which straddles the lit threshold (luma>55) and cost 60% of
                # the lit count.  Average the stops; a flat fill has all stops
                # equal, so nothing else moves.
                _stops = list(frgbas)
                fr = sum(float(s[0]) for s in _stops) / len(_stops)
                fg = sum(float(s[1]) for s in _stops) / len(_stops)
                fb = sum(float(s[2]) for s in _stops) / len(_stops)
                fa = max(float(s[3]) for s in _stops)
        except Exception:
            pass
        if fr == 0 and fg == 0 and fb == 0:
            # The fill colour is literally black, which is ambiguous: it may be
            # the real colour or just "unset".  Take the colour from
            # `get_color()`, but do NOT touch `fa` when the rgba data was read
            # -- `fa` is the mobject's own fill opacity and the only thing that
            # carries a fade.  Forcing it to 1.0 made a faded-out glyph fill at
            # full strength: GraphMobjects' six vertex labels flashed for one
            # frame before each FadeIn (report R10-3, fill_alpha 1.0 with
            # fa 0.0).  Only a mobject with no fill rgba data at all falls back
            # to "paint it".
            try:
                c = mob.get_color()
                fr, fg, fb = float(c[0]), float(c[1]), float(c[2])
                if not _fa_measured:
                    fa = 1.0
            except Exception:
                fr, fg, fb = 1.0, 1.0, 1.0
                if not _fa_measured:
                    fa = 1.0
            if is_text and fr == 0 and fg == 0 and fb == 0:
                fr, fg, fb = 1.0, 1.0, 1.0

        # A `shade_in_3d` face is lit by the ThreeDCamera's light source;
        # without this every face of a 3D solid takes its flat colour (see
        # vulkan_util.shaded_fill_rgb).  No-op outside a rotated 3D viewport.
        _lit = shaded_fill_rgb(mob)
        if _lit is not None:
            fr, fg, fb = _lit[0] / 255.0, _lit[1] / 255.0, _lit[2] / 255.0

        sr, sg, sb, sa = 1, 1, 1, 1
        try:
            srgbas = mob.get_stroke_rgbas()
            if len(srgbas) > 0:
                sr, sg, sb, sa = float(srgbas[0][0]), float(srgbas[0][1]), float(srgbas[0][2]), float(srgbas[0][3])
        except Exception:
            sr, sg, sb = fr, fg, fb
            sa = 1.0
        from real_time_manim.background_color import background_image_rgb
        if getattr(mob, 'get_background_image', None) is not None:
            # The VectorField family carries a background image and leaves its
            # stroke rgba WHITE; CE tints those strokes from that image.  Use the
            # image's mean colour so the field is not drawn white (measured
            # VectorFieldsAndTrackers, +2.58, 4832 white px vs CE's 768).
            try:
                _bg = background_image_rgb(mob)
            except Exception:
                _bg = None
            if _bg is not None:
                sr, sg, sb = _bg
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
            so = get_opacity(mob, 'stroke', 1.0)
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
        if exact_width and sw > 0:
            # Warped lines arrive here from `_send_line`; give them the exact
            # sub-pixel width (native's strip is `width+1` px, so use the next
            # integer up plus a compensating alpha -- see _send_line).  NOT
            # applied in general: dimming the outline of a filled shape measured
            # worse than leaving it over-thick (ThreeDSurfaceLab -0.56 -> -2.08
            # with it on).
            stroke_w = max(1.0, float(int(math.ceil(sw - 1e-6)) - 1))
            stroke_width_alpha = min(1.0, sw / (stroke_w + 1.0))
        elif sw > 0 and getattr(mob, 'shade_in_3d', False):
            # A 3D face's own outline is thin and usually a light grey.  manim
            # draws a Surface's quad borders at `stroke_width` (0.5 by default),
            # i.e. 0.3 px at 480p, but `max(1.0, sw)` turned that into a 2 px
            # quad (native's strip is `width + 1` px) -- so every quad border of
            # a Sphere/Cone came out as a fat white mesh.  Measured on
            # SolidPrimitives3D: 57 % of the sphere's lit pixels were the stroke
            # grey (187,187,187) against CE's 1 %, and the fills were buried
            # under it.  Give it the exact sub-pixel width, the same rule
            # `_send_line` uses; `stroke_width_alpha` rides the per-vertex alpha
            # at the AddLineStrip below.
            stroke_w = max(0.0, float(int(math.ceil(sw - 1e-6)) - 1))
            stroke_width_alpha = min(1.0, sw / (stroke_w + 1.0))
        else:
            stroke_w = max(1.0, sw) if sw > 0 else 0
            stroke_width_alpha = 1.0
        # Default per-vertex stroke alpha; the latex write-stroke synthesis
        # overrides this to fade the outline out as the fill comes in.
        stroke_point_alpha = a

        # The native fill window and the stroke walk below must agree, and both
        # are fractions OF mob's points -- which manim's ShowPartial has already
        # cut when render_hooks tagged the mobject (see point_path_bounds).
        progress_lower, progress_upper = point_path_bounds(mob)
        progress = progress_upper
        # Straight alpha.  native blends `colour * alpha + dst * (1 - alpha)`
        # (vulkan_init.c:633), so the colour must stay full-strength and the
        # mobject's stroke opacity rides in the alpha -- exactly the rule the
        # bezier fill code already documents (native/draw/draw_bezier.c:234:
        # "Baking opacity into the colour ... made low-opacity fills render as
        # BLACK instead of transparent -- the colour approached 0 while alpha
        # stayed ~1").  Folding `stroke_alpha` into the colour here, with the
        # blend alpha left at `a`, submits an OPAQUE dark stroke that REPLACES
        # whatever it lands on.  Measured on ApplyTransformAnimations: at frame
        # 83 FadeTransform's source ring is at stroke opacity 0.154 and is
        # drawn after the target square (native builds every AddLineStrip after
        # every AddLine, vulkan_draw.c:89-90), so it erased the middle of all
        # four edges -- 269 ink against CE's 442.
        sri = round(sr * 255)
        sgi = round(sg * 255)
        sbi = round(sb * 255)
        fri = round(fr * 255)
        fgi = round(fg * 255)
        fbi = round(fb * 255)

        show_fill = 1 if fill_alpha > 0.01 and progress_lower == 0.0 else 0
        # Gate on the ORIGINAL `sw`, never the rounded `stroke_w`: the sub-pixel
        # rule above legitimately yields stroke_w == 0 for a thin outline, and
        # gating on it would drop the stroke entirely -- the width lives in
        # `stroke_width_alpha` instead.
        do_stroke = stroke_alpha > 0.01 and sw > 0

        if is_text and fill_alpha > 0.01:
            do_stroke = False

        if not do_stroke and getattr(mob, '_transforming', False) and sw > 0 and not is_text:
            # Silhouette for a morphing shape that has no stroke of its own.
            # It must NOT fire when manim has faded the whole mobject away:
            # `a` is the animation-registry value, which deliberately stays 1.0
            # for a container animation (see `_is_container`), so the old
            # `max(stroke_alpha, a)` resurrected FadeTransform's vanishing
            # source as a fully opaque ring painted over the finished square
            # (measured frame 85: 573 ink against CE's 360).  Only a mobject
            # that is still visible -- through its fill -- earns the outline.
            if max(stroke_alpha, fill_alpha) > 0.01:
                sr, sg, sb = fr, fg, fb
                stroke_alpha = 1.0
                sri = round(sr * 255)
                sgi = round(sg * 255)
                sbi = round(sb * 255)
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
            # colour is the glyph's fill colour, full strength: the fade-out is
            # carried entirely by `stroke_point_alpha`, so `stroke_alpha` (the
            # glyph's own stroke opacity, i.e. 0 here) must not multiply it.
            stroke_alpha = 1.0
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
                    # `stroke_alpha` is the mobject's own stroke opacity and is
                    # NOT in the colour any more (straight alpha above), so it
                    # belongs here: total = opacity * animation * width.
                    alphas[i] = min(1.0, stroke_alpha * stroke_point_alpha
                                    * stroke_width_alpha)
                self.dll.AddLineStrip(coords, alphas, len(stroke_pts), int(stroke_w), sri, sgi, sbi, 1.0)

    def _send_text_stroke(self, mob, a, w, h, parent_offset=None):
        if not hasattr(mob, 'family_members_with_points'):
            return
        for fm in mob.family_members_with_points():
            sw_attr = fm.get_stroke_width() if hasattr(fm, 'get_stroke_width') else 0
            if sw_attr <= 0:
                continue
            self._send_vmobject(fm, a, w, h, parent_offset)
