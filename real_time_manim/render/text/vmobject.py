"""The bezier-path sender for `VMobject`-shaped geometry.

`_send_vmobject` is the generic stroker/filler every text glyph and every
vector path ends up in; `_mitre_room_filter` trims the mitre overhang
before the points reach native."""

import ctypes
import math
from real_time_manim.render.util import manim_to_screen, get_opacity, point_path_bounds, shaded_fill_rgb, shaded_fill_gradient

def _mitre_room_filter(pts, half_w):
    """Drop the vertices that leave a corner's mitre cut without room.

    native ends every strip quad on the shared cut line of its joint
    (draw_line.c, `JointCutCorners`), which needs axial room
    ``half_w * tan(deflection / 2)`` on BOTH runs of the corner.  A run
    shorter than the two cuts it has to hold makes the quad bow-tie, and
    the guard reverts the whole segment to plain perpendicular caps --
    the corner loses its point.  The bezier sampler in `_send_vmobject`
    leaves ~3 px runs, so a sharp corner (the Intersection cusp in
    BooleanOperations deflects ~74 deg: 0.75 * half_w, i.e. 2.25 px at
    half_w=3 against 2.35 px runs) already sits on that edge, and a
    slightly sharper tip renders blunt where CE mitres to a point.

    Merge the too-short runs into their neighbours until every corner has
    its room.  The runs being merged are ~3 px chords of a smooth outline,
    so the merged chord deviates from the curve by well under 0.1 px --
    far below one screen pixel -- while the corner keeps its mitre.

    ``pts`` is a list of (x, y) screen-space points; a closed outline
    (first == last) is treated cyclically and re-closed on return.
    """
    if len(pts) < 3:
        return pts
    pts = list(pts)
    closed = (abs(pts[0][0] - pts[-1][0]) < 1e-3 and
              abs(pts[0][1] - pts[-1][1]) < 1e-3)
    if closed:
        pts = pts[:-1]
    m = len(pts)
    if m < 3:
        return pts + ([pts[0]] if closed else [])

    def run_len(i, j):
        return math.hypot(pts[j][0] - pts[i][0], pts[j][1] - pts[i][1])

    def room(i):
        """Axial mitre room the corner at vertex i demands of its runs."""
        if not closed and (i == 0 or i == m - 1):
            return 0.0                    # open end: plain cap, no room
        ip = (i - 1) % m
        iN = (i + 1) % m
        ax = pts[i][0] - pts[ip][0]
        ay = pts[i][1] - pts[ip][1]
        bx = pts[iN][0] - pts[i][0]
        by = pts[iN][1] - pts[i][1]
        la = math.hypot(ax, ay)
        lb = math.hypot(bx, by)
        if la < 1e-9 or lb < 1e-9:
            return 0.0
        c = (ax * bx + ay * by) / (la * lb)
        if c < -0.875:
            # Past ~151 deg native shares a plain cap line instead of a
            # mitre (its own documented fallback); no room is demanded.
            return 0.0
        return half_w * math.sqrt(max(0.0, (1.0 - c) / (1.0 + c)))

    turns = 0
    while turns < 64 and m > 3:
        turns += 1
        did = False
        for i in range(m if closed else m - 1):
            j = (i + 1) % m
            need = room(i) + room(j)
            if need <= 0.0 or run_len(i, j) >= need:
                continue
            # Run (i, j) is too short for its two cuts: merge it into the
            # neighbouring run whose own corner demands less, i.e. delete
            # the vertex between the two runs -- never an open end.
            if not (closed or i > 0):
                drop = j
            elif not (closed or j < m - 1):
                drop = i
            else:
                # Delete the FLATTER of the two endpoints -- the vertex
                # whose own corner demands less room.  Choosing by run
                # length alone (the old `drop = i if li <= lj else j`)
                # deleted the sharp corner itself whenever the run beyond
                # it happened to be the shorter one, replacing a mitre-
                # able 66 deg chart peak with a 5 px chamfer -- the
                # corner rendered blunt where CE mitres to a point.
                drop = j if room(j) < room(i) else i
            pts.pop(drop)
            m -= 1
            did = True
            break                    # lengths and rooms changed; rescan
        if not did:
            break
    if closed and m >= 2:
        pts.append(pts[0])
    return pts


def _cut_cubics_at(flat, n, progress):
    """Truncate a bezier control-point array to the first ``progress`` of it.

    ``flat`` is the stride-3 screen-space array ``_send_vmobject`` builds and
    hands to native ``AddBezierPath``: four control points per cubic, the
    groups NOT overlapping (the layout native reads at ``draw_bezier.c:79-85``
    and the stroke walk indexes with ``si * 4``).

    native's ``tessellate_fill`` (``draw_bezier.c:268-282``) samples EVERY
    cubic and never reads ``bp->progress``, so a filled shape arriving mid-
    ``Create`` painted its WHOLE fill on the first frame while only the
    outline swept -- measured at 90-100 % of the finished ink on frame one
    against ManimCE's 0 %.  Cutting the ARRAY instead makes the fill follow
    the pen: the trailing cubic is split with De Casteljau at the exact
    parameter, so the cut lands mid-segment just as the stroke window does (a
    Circle's cubic is 45 degrees of arc, so a whole-segment cut would
    staircase again -- the very bug the stroke walk was fixed for).

    Returns ``(cut_flat, cut_n)``.  ``cut_n`` can drop below native's
    ``num_points < 8`` floor for a short prefix; the caller skips the
    submission then, which is correct -- a wedge shorter than two cubics has
    no area worth drawing, and manim's own Create has already cut the points
    in that case anyway.
    """
    seg_count = n // 4
    if seg_count < 1 or progress <= 0.0:
        return flat, 0
    if progress >= 1.0:
        return flat, n
    target = seg_count * progress
    vis_end = int(math.floor(target))
    t_end = target - vis_end
    if t_end <= 1e-9:
        # An exact boundary cuts at the END of the previous cubic, not the
        # start of this one (progress 0 would otherwise draw a dot).
        vis_end -= 1
        t_end = 1.0
    if vis_end < 0:
        return flat, 0
    keep = vis_end + 1
    # NO `keep >= seg_count` shortcut here.  `progress < 1.0` already bounds
    # `target` below `seg_count`, so `vis_end <= seg_count - 1` and the 12
    # floats read below always sit inside the array -- but bailing out to the
    # whole path for `keep == seg_count` (i.e. every progress in
    # [7/8, 1.0) on an 8-cubic Circle) drew the COMPLETE fill for the last
    # eighth of the animation.  Measured on Create(Arc().set_fill): RTM
    # tracked CE within 2 % for 33 frames, then stepped +2485 px in one frame
    # against CE's +417.
    # De Casteljau: splitting (p0..p3) at t yields the first half
    # (p0, a, d, f) -- an exact reparameterisation, not an approximation.
    b = vis_end * 4 * 3
    p0x, p0y = flat[b], flat[b + 1]
    p1x, p1y = flat[b + 3], flat[b + 4]
    p2x, p2y = flat[b + 6], flat[b + 7]
    p3x, p3y = flat[b + 9], flat[b + 10]
    t = t_end
    ax = p0x + (p1x - p0x) * t
    ay = p0y + (p1y - p0y) * t
    bx = p1x + (p2x - p1x) * t
    by = p1y + (p2y - p1y) * t
    cx = p2x + (p3x - p2x) * t
    cy = p2y + (p3y - p2y) * t
    dx = ax + (bx - ax) * t
    dy = ay + (by - ay) * t
    ex = bx + (cx - bx) * t
    ey = by + (cy - by) * t
    fx = dx + (ex - dx) * t
    fy = dy + (ey - dy) * t
    cut = list(flat[:b])
    cut.extend((p0x, p0y, 0.0, ax, ay, 0.0, dx, dy, 0.0, fx, fy, 0.0))
    if keep < 2:
        # native refuses a path shorter than two cubics (`num_points < 8`),
        # and the fallback would be the WHOLE array -- the pop again.  Pad
        # with a degenerate cubic sitting on the cut point instead: every
        # control point is the same pixel, so it adds no area (the scanline
        # skips its zero-length edges) and its winding term is zero, but the
        # path clears the floor and the wedge can start as small as the pen
        # likes instead of jumping from nothing to a full 45-degree slice.
        cut.extend((fx, fy, 0.0, fx, fy, 0.0, fx, fy, 0.0, fx, fy, 0.0))
        keep = 2
    return cut, keep * 4


class VMobjectMixin:


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
            # manim units -> pixels uses the *visible* frame height, the same
            # rule as `ShapeMixin._stroke_width`; `h / 8.0` pinned the outline
            # to the default frame under a zooming camera.
            sw = max(1, int(round(sw_manim * 0.01 * (h / self._visible_frame_height()))))

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
                # Straight alpha (vulkan_init.c:633): the colour stays full
                # strength and every bit of opacity rides the per-vertex alpha.
                # Baking `a` into the colour AND multiplying it into alphas
                # below squared it, so FadeOut(TracedPath) darkened the trace
                # towards black instead of fading it out.
                sri = round(sr * 255)
                sgi = round(sg * 255)
                sbi = round(sb * 255)
                so_start, so_end = float(so_attr[0]), float(so_attr[1])
                so_arr = []
                n_raw = len(raw_pts)
                for i in range(n_raw):
                    t = i / max(1, n_raw - 1)
                    so_arr.append(so_start + (so_end - so_start) * t)
            else:
                sri = round(sr * 255)
                sgi = round(sg * 255)
                sbi = round(sb * 255)
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
                    # `sa` used to live in the colour (see above); it belongs
                    # here, multiplied in exactly once alongside the animation.
                    alphas[i] = max(0.0, min(1.0, sa * a))
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
                sr, sg, sb = self._stroke_rgb_with_background(mob, sr, sg, sb)
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
                # A VectorField line keeps its stroke rgba WHITE and carries a
                # background image instead -- the same short-path tint the
                # n >= 8 branch applies (see _stroke_rgb_with_background).
                # Stream lines that happen to be ONE cubic segment (4 anchors,
                # n == 4) land here and came out white against CE's red.
                sr, sg, sb = self._stroke_rgb_with_background(mob, sr, sg, sb)
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
        # The VectorField family carries a background image and leaves its
        # stroke rgba WHITE; CE tints those strokes from that image.  Use the
        # image's mean colour so the field is not drawn white (measured
        # VectorFieldsAndTrackers, +2.58, 4832 white px vs CE's 768).
        sr, sg, sb = self._stroke_rgb_with_background(mob, sr, sg, sb)
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
        # These are the mobject's OWN opacities -- the animation's `a` is NOT
        # folded in, because the native side folds it in itself: the fill path
        # computes `fill_alpha = fo * bp->alpha` (draw_bezier.c:249) with
        # bp->alpha == `a`, and the stroke strip below reaches the same `a`
        # through stroke_point_alpha.  Multiplying `a` in HERE as well squared
        # it -- measured on RTM's own fades (animations/fade_in.py writes a
        # per-frame registry alpha != 1.0): a shape at a == 0.5 came out at
        # 0.25, and a nested container cubed it.  The ADDPOLYGON path
        # (_send_polygon -> AddPolygon) already passed the single `a`, which is
        # why it never showed this.
        fill_alpha = min(1.0, fa)
        # stroke_alpha uses so (max stroke-rgba alpha) — consistent
        # with how fill_alpha uses fa (fill-rgba alpha from first element)
        stroke_alpha = min(1.0, so)
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

        # Visibility gates keep the ANIMATED value (opacity * animation alpha):
        # `a` is what decides whether this mobject is on screen at all.  The
        # alpha actually submitted must stay free of `a` (native multiplies it
        # in), so the two are tracked separately from here on.
        vis_fill = min(1.0, fa * a)
        vis_stroke = min(1.0, so * a)

        # A windowed reveal (ShowPassingFlash's sliding lower/upper pair) that
        # has not yet reached the end of the path has nothing to fill, but the
        # native tessellator fills the WHOLE shape -- `show_fill` was the only
        # thing holding it back, and it only looked at `progress_lower`, so the
        # flash's first frame painted the entire filled shape.  Scoped to the
        # explicit-window branch of point_path_bounds: an animation that carries
        # its partial state in `_vulkan_progress` alone (RTM's own Create) keeps
        # the behaviour it was measured with.
        in_bounds_window = hasattr(mob, "_vulkan_progress_upper")
        show_fill = 1 if (vis_fill > 0.01 and progress_lower == 0.0
                          and (not in_bounds_window
                               or progress_upper >= 1.0)) else 0
        # Gate on the ORIGINAL `sw`, never the rounded `stroke_w`: the sub-pixel
        # rule above legitimately yields stroke_w == 0 for a thin outline, and
        # gating on it would drop the stroke entirely -- the width lives in
        # `stroke_width_alpha` instead.
        do_stroke = vis_stroke > 0.01 and sw > 0

        if is_text and vis_fill > 0.01:
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
            if max(vis_stroke, vis_fill) > 0.01:
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
            # `vis_fill`, not `fill_alpha`: the fade-out ramp must track how
            # visible the fill actually is (opacity * animation alpha), which is
            # what `fill_alpha` meant before the alpha-baking was untangled.
            stroke_point_alpha = max(0.0, 1.0 - vis_fill * 1.2) * a
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
        _grad = shaded_fill_gradient(mob, w, h)
        if _grad is not None:
            # manim's two shaded stops, interpolated across the path: use the
            # FIRST stop as the fill colour and hand the native the second one
            # plus the projected corner axis (see shaded_fill_gradient).
            _c1, _c2, _p1, _p2 = _grad
            fri, fgi, fbi = _c1
            _fr2, _fg2, _fb2 = _c2
            _gx1, _gy1 = _p1
            _gx2, _gy2 = _p2
        else:
            _fr2, _fg2, _fb2 = fri, fgi, fbi
            _gx1 = _gy1 = _gx2 = _gy2 = 0.0
        # native's tessellate_fill samples every cubic and never reads
        # `progress`, so a fill revealed by `_vulkan_progress` (RTM's own
        # Create) arrived WHOLE on the first frame -- measured at 90-100 % of
        # the finished ink on frame one against ManimCE's 0 %, while only the
        # outline swept.  Cut the ARRAY to the drawn prefix instead.  Skipped
        # when manim itself already cut the points (`_vulkan_points_partial`,
        # which makes point_path_bounds return 1.0) and for a bounds window
        # (ShowPassingFlash), where show_fill is already 0.
        #
        # A prefix shorter than native's `num_points < 8` floor cannot be
        # submitted at all -- and falling back to the WHOLE array there would
        # put the pop straight back on the first frames, which are exactly the
        # ones under the floor.  Hold the fill back instead: it is a sliver of
        # a sliver, and the stroke already marks where the pen is.
        _fill_arr, _fill_n, _fill_progress = arr, n, progress
        if show_fill and progress < 1.0:
            _cut_flat, _cut_n = _cut_cubics_at(flat, n, progress)
            if _cut_n >= 8:
                _fill_arr = (ctypes.c_float * len(_cut_flat))(*_cut_flat)
                _fill_n = _cut_n
                # The array now ENDS at the pen tip, so native must not also
                # window it: pass a complete path.
                _fill_progress = 1.0
            else:
                show_fill = 0
        self.dll.AddBezierPath(
            _fill_arr, _fill_n,
            sri, sgi, sbi, stroke_w,
            fri, fgi, fbi, fill_alpha,
            _fill_progress, 0, show_fill, a,
            _fr2, _fg2, _fb2, _gx1, _gy1, _gx2, _gy2,
        )

        if do_stroke:
            seg_count = n // 4
            # Cut the window at an EXACT fraction of a segment, never at whole
            # segments.  `int(seg_count * progress)` advanced the reveal one
            # cubic at a time, and manim builds a Circle from only EIGHT cubics
            # -- so `Create(Circle)` jumped 45 degrees at a time, standing
            # still for several frames and then snapping forward a whole
            # eighth of the outline (measured on the 01-安装 demo video and
            # reproduced with a recorder probe: the drawn length took the
            # values 0.125, 0.250, ... 1.000 of the perimeter and nothing in
            # between).  native's own stroke tessellator already cuts at a
            # fractional `partial_t` (draw_bezier.c:144-170); this walk, which
            # is what a stroke-only path actually takes, has to match it.
            f_start = seg_count * progress_lower
            f_end = seg_count * progress_upper
            vis_start = int(math.floor(f_start))
            t_start = f_start - vis_start        # fraction in at segment vis_start
            vis_end = int(math.floor(f_end))
            t_end = f_end - vis_end               # fraction in at segment vis_end
            if t_end <= 1e-9:
                # An exact segment boundary cuts at the END of the previous
                # segment, not at the start of this one (progress 1.0 would
                # otherwise lose the last segment, progress 0.0 draw a dot).
                vis_end -= 1
                t_end = 1.0
            stroke_pts = []
            # One strip per contour: several disjoint contours live in the same
            # point list (`VMobject.start_new_path`), and walking them as a
            # single polyline bridges them with one straight line -- measured on
            # BooleanOperations/MatchersAndBooleanOps, where the Exclusion
            # result grew a diagonal across its own hole.  native splits on the
            # very same rule when it tessellates a bezier stroke
            # (draw_bezier.c:91: squared jump > 40).
            runs = []
            prev_pt = None
            for si in range(vis_start, min(seg_count, vis_end + 1)):
                idx = si * 4
                p0x, p0y = flat[idx*3], flat[idx*3+1]
                p1x, p1y = flat[(idx+1)*3], flat[(idx+1)*3+1]
                p2x, p2y = flat[(idx+2)*3], flat[(idx+2)*3+1]
                p3x, p3y = flat[(idx+3)*3], flat[(idx+3)*3+1]
                if prev_pt is not None and (
                        (p0x - prev_pt[0]) ** 2 + (p0y - prev_pt[1]) ** 2) > 40.0:
                    if len(stroke_pts) >= 2:
                        runs.append(stroke_pts)
                    stroke_pts = []
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
                # The window's ends land INSIDE a segment: the first visible
                # segment starts at t_start, the last one stops at t_end.
                # Evaluating the cubic there makes the pen tip move
                # continuously instead of snapping forward a whole segment at
                # a time (a Circle is only 8 cubics, so a whole segment is 45
                # degrees of arc -- see the vis_start/vis_end block above).
                lo_t = t_start if si == vis_start else 0.0
                hi_t = t_end if si == vis_end else 1.0
                if hi_t <= lo_t:
                    prev_pt = (p3x, p3y)
                    continue
                span = hi_t - lo_t
                seg_samples = max(1, int(math.ceil(seg_samples * span)))
                for s in range(seg_samples + 1):
                    t = lo_t + span * (s / seg_samples)
                    u = 1.0 - t
                    bx = u*u*u*p0x + 3*u*u*t*p1x + 3*u*t*t*p2x + t*t*t*p3x
                    by = u*u*u*p0y + 3*u*u*t*p1y + 3*u*t*t*p2y + t*t*t*p3y
                    # Consecutive cubics share an endpoint, so t=1 of one
                    # segment and t=0 of the next append the same point
                    # twice.  native skips that zero-length run, which
                    # leaves each neighbour without the other's direction
                    # at the joint -- `JointCutCorners` gets a missing
                    # side, fills it from its own and draws a plain
                    # perpendicular cap.  At a sharp corner that cap is a
                    # wedge notch: the Intersection cusp rendered blunt
                    # where CE mitres to a point (report: "line joints
                    # still not sharp").  Keep one copy so the joint stays
                    # a real corner and native mitres it.
                    if (stroke_pts and abs(bx - stroke_pts[-1][0]) < 1e-3
                            and abs(by - stroke_pts[-1][1]) < 1e-3):
                        continue
                    stroke_pts.append((bx, by))
                prev_pt = (p3x, p3y)
            if len(stroke_pts) >= 2:
                runs.append(stroke_pts)
            half_w = int(stroke_w) * 0.5 + 0.5
            for stroke_pts in runs:
                # Guarantee every corner the axial room its mitre cut
                # needs (see _mitre_room_filter); without it native's
                # bow-tie guard silently reverts sharp corners to blunt
                # plain caps whenever the sampler left a run too short.
                stroke_pts = _mitre_room_filter(stroke_pts, half_w)
                if len(stroke_pts) < 2:
                    continue
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
