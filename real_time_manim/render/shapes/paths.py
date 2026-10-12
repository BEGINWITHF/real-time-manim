"""Open and closed paths: polylines, arcs and polygons."""

import ctypes
import math
import numpy as np
from real_time_manim.render.util import manim_to_screen, get_opacity, point_path_bounds
from real_time_manim.animations import get_anim_rotation


class PathMixin:


    def _stroke_polyline_with_progress(self, flat, closed, lower, upper,
                                       r, g, b, px, alpha):
        """Stroke the [lower, upper] stretch of a screen-space polyline.

        ``flat`` is x0,y0,x1,y1,... in screen pixels; ``lower``/``upper`` are
        fractions of the total length.  Shared by the polygon and arc senders so
        a partially drawn shape (Create / ShowPartial / ShowPassingFlash) is
        stroked the same way whichever sender handles it (plan 4.2).

        The window is cut into ONE point list and submitted as a single
        ``AddLineStrip`` per width layer (:meth:`_emit_stroke_strip`), NOT one
        ``AddLine`` per edge: native's line quad is extended a fixed
        ``half_thick`` past its endpoints (draw_line.c:24-27), which only
        reaches the mitre point of a 90 degree turn.  At a SHARPER corner the
        extension falls short of the joint's mitre point
        ``half_w / sin(interior/2)`` -- the stroke loses its point and the
        shape's tip renders blunt/notched against CE's clean spike (measured:
        the green Intersection lens of ``BooleanOperations``: its apex stopped
        ~1 half-width short while CE comes to a point).  Over-extending the
        segments from Python instead would overshoot native's own half-thick
        cap and double-cover the joint diamond while fading; the strip's
        shared mitre cut (draw_line.c, ``JointCutCorners``) tiles exactly --
        no notch at a tip, no double blend at any corner, and a closed window
        mitres its seam too.  Window ends keep native's plain butt cap at the
        cut point, which is the cap CE's pen draws.

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
        pts = []

        def _push(x, y):
            # Drop zero-length steps (a polygon that already repeats its
            # first point leaves one behind): the native strip skips them
            # anyway, which would break the joint pairing of its neighbours.
            if pts and abs(x - pts[-2]) < 1e-4 and abs(y - pts[-1]) < 1e-4:
                return
            pts.append(x)
            pts.append(y)

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
            if skip > 0.0:
                frac = skip / el
                x0 = x0 + (x1 - x0) * frac
                y0 = y0 + (y1 - y0) * frac
                el = el - skip
                skip = 0.0
            if not pts:
                _push(x0, y0)
            if remaining >= el:
                _push(x1, y1)
                remaining -= el
            else:
                frac = remaining / el
                _push(x0 + (x1 - x0) * frac, y0 + (y1 - y0) * frac)
                remaining = 0.0
        if len(pts) < 4:
            return
        self._emit_stroke_strip(pts, px, r, g, b, alpha)

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
        # GrowFromPoint / GrowFromEdge: the arc has to scale like every other
        # sender (`_send_line`, `_send_dashed_line`, `_send_polygon` all honour
        # `_grow_scale`), otherwise a GrowFromPoint(Arc) left the arc at its
        # final size while its position followed the animation.
        grow_scale = getattr(mob, '_grow_scale', 1.0)
        grow_pt = getattr(mob, '_grow_point', None)
        if grow_scale != 1.0 and grow_pt is not None:
            gp = np.array(grow_pt, dtype=float)
            pts = np.asarray(points, dtype=float).copy()
            pts[:, 0] = gp[0] + (pts[:, 0] - gp[0]) * grow_scale
            pts[:, 1] = gp[1] + (pts[:, 1] - gp[1]) * grow_scale
            points = pts
            cx = gp[0] + (cx - gp[0]) * grow_scale
            cy = gp[1] + (cy - gp[1]) * grow_scale
        sx, sy = manim_to_screen(cx, cy, w, h, cz)
        flat = self._stroke_points_polyline(points, w, h, parent_offset, rot, sx, sy)
        if len(flat) < 4:
            return
        r, g, b = self._stroke_color(mob)
        sw = self._stroke_width(mob)
        lower, upper = point_path_bounds(mob)
        # The stroke opacity rides the ALPHA, not the colour (straight-alpha
        # blend, vulkan_init.c:633) -- same rule as `_send_square`.  Baking `so`
        # into the colour made a fading arc REPLACE the background with a
        # darkening solid instead of fading out over it.
        self._stroke_polyline_with_progress(flat, False, lower, upper,
                                            r, g, b, sw, a * so)

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
        perims = [PathMixin._flat_perimeter(f) for f in flat_groups]
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
