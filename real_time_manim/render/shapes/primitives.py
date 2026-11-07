"""The four convex primitives: square, rectangle, ellipse and circle."""

import ctypes
import math

import numpy as np
from real_time_manim.camera_state import get_viewport
from real_time_manim.render.util import (manim_to_screen, get_stroke_w,
                                         get_opacity, point_path_bounds,
                                         path_center, curve_segments)


_UNIT_CIRCLE = {}


def _unit_circle(segs):
    """Cached ``(cos, sin)`` for the segs+1 points of a full ring.

    Built with ``math.cos`` so the values are bit-identical to the per-point
    loop it replaces.
    """
    cached = _UNIT_CIRCLE.get(segs)
    if cached is None:
        angles = [2.0 * math.pi * j / segs for j in range(segs + 1)]
        cached = (np.array([math.cos(a) for a in angles], dtype=np.float64),
                  np.array([math.sin(a) for a in angles], dtype=np.float64))
        _UNIT_CIRCLE[segs] = cached
    return cached


class PrimitiveMixin:


    def _send_square(self, mob, a, w, h, rot, parent_offset=None):
        cx, cy, cz = path_center(mob)
        if parent_offset is not None:
            cx += parent_offset[0]; cy += parent_offset[1]
        about = mob.__dict__.get('_rotation_about_point')
        if about is not None:
            neg_rot = -rot
            dx, dy = cx - about[0], cy - about[1]
            c, sn = math.cos(neg_rot), math.sin(neg_rot)
            cx = about[0] + dx * c - dy * sn
            cy = about[1] + dx * sn + dy * c
        _ch = mob.__dict__
        grow_scale = _ch.get('_grow_scale', 1.0)
        grow_pt = _ch.get('_grow_point')
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
        cx, cy, cz = path_center(mob)
        if parent_offset is not None:
            cx += parent_offset[0]; cy += parent_offset[1]
        about = mob.__dict__.get('_rotation_about_point')
        if about is not None:
            neg_rot = -rot
            dx, dy = cx - about[0], cy - about[1]
            c, sn = math.cos(neg_rot), math.sin(neg_rot)
            cx = about[0] + dx * c - dy * sn
            cy = about[1] + dx * sn + dy * c
        _ch = mob.__dict__
        grow_scale = _ch.get('_grow_scale', 1.0)
        grow_pt = _ch.get('_grow_point')
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
        cx, cy, cz = path_center(mob)
        if parent_offset is not None:
            cx += parent_offset[0]; cy += parent_offset[1]
        about = mob.__dict__.get('_rotation_about_point')
        if about is not None:
            neg_rot = -rot
            dx, dy = cx - about[0], cy - about[1]
            c, sn = math.cos(neg_rot), math.sin(neg_rot)
            cx = about[0] + dx * c - dy * sn
            cy = about[1] + dx * sn + dy * c
        _ch = mob.__dict__
        grow_scale = _ch.get('_grow_scale', 1.0)
        grow_pt = _ch.get('_grow_point')
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
            c = np.asarray(path_center(mob), dtype=float)
            s = np.asarray(mob.get_start(), dtype=float)
            r = float(np.linalg.norm(s[:2] - c[:2]))
            if r > 0.0 and np.isfinite(r):
                return r
        except Exception:
            pass
        return mob.width / 2.0

    @staticmethod
    def _points_hug_circle(pts, centre, radius, tol=0.01):
        """True when every point sampled along the path sits on that circle.

        A cubic bezier's control polygon hugs its circle to within 0.03 %; a
        straight edge's midpoint sits at cos(45 deg) = 0.707 r, so a 1 % window
        cleanly splits a real circle from a quad -- or from any other closed
        path whose anchors merely happen to be equidistant.
        """
        pts = np.asarray(pts, dtype=float)
        if len(pts) < 4 or radius <= 0.0:
            return False
        centre = np.asarray(centre, dtype=float)[:2]
        # Evaluate every cubic at t = .25/.5/.75 in one pass.  The scalar
        # version ran 24 tiny numpy expressions per Circle; a 2000-circle scene
        # spent ~120 us per shape here.
        cubics = pts.reshape(-1, 4, 3)[:, :, :2]
        t = np.array([0.25, 0.5, 0.75], dtype=float)[:, None]
        u = 1.0 - t
        b = (u ** 3 * cubics[:, 0][:, None, :]
             + 3.0 * u ** 2 * t * cubics[:, 1][:, None, :]
             + 3.0 * u * t ** 2 * cubics[:, 2][:, None, :]
             + t ** 3 * cubics[:, 3][:, None, :])
        dist = np.linalg.norm(b - centre, axis=2)
        return bool(np.all(np.abs(dist - radius) <= radius * tol))

    @staticmethod
    def _circle_round_radius(mob):
        """Cached :meth:`_circle_round_radius_uncached` for one mobject.

        The roundness test samples every cubic, which is pure waste for the
        same static Circle on every frame.  Compare the full point array (a
        few hundred bytes) before recomputing; any in-place or reassigned
        transform invalidates it.
        """
        try:
            pts = getattr(mob, "points", None)
            if pts is None or len(pts) < 4:
                return None
            cached = getattr(mob, "_rtm_round_cache", None)
            if cached is not None and np.array_equal(cached[0], pts):
                return cached[1]
            r = PrimitiveMixin._circle_round_radius_uncached(pts)
            mob._rtm_round_cache = (np.array(pts, copy=True), r)
            return r
        except Exception:
            return None

    @staticmethod
    def _circle_round_radius_uncached(pts):
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

        The sender also strokes a **complete** disc, so a path that is not
        closed must never reach it -- and neither check below was here before
        2.0.0's `pointwise_become_partial` support landed:

        * two anchors are ALWAYS equidistant from their own bbox centre (it is
          their midpoint), so an open single-quadrant arc passed the distance
          test and `_send_circle` drew a full disc of radius
          ``|get_start() - get_center()|``.  Measured on the wiki's
          `07b-VMobject样式进阶` `partial` sample, panel `[0.75, 1.0]`: an 86 px
          ring where CE strokes a 122 px quarter arc (RTM/CE mean|diff| 0.40 on
          that clip against a 0.13-0.24 baseline).
        * a >=3-anchor arc can also be equidistant by accident: `[0, 0.75]` of
          the same circle returns 0.9, the *right* radius, and still drew the
          whole circle instead of three quarters of it.

        Requiring the path to close fixes both; a real `Circle` has
        ``points[0] == points[-1]`` (`[0, 1]` above: 8 anchors, closed).
        """
        try:
            if pts is None or len(pts) < 4:
                return None
            anchors = np.asarray(pts[0::4], dtype=float)
            if len(anchors) < 3:
                return None
            first = np.asarray(pts[0], dtype=float)
            last = np.asarray(pts[-1], dtype=float)
            if not (abs(first[0] - last[0]) < 1e-3 and abs(first[1] - last[1]) < 1e-3):
                return None
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
            # ...and equidistant anchors are still not enough: a `Circle` that
            # `become`-ed a Square keeps four corners whose bbox centre is the
            # square's own centre, so every anchor sits at the same distance and
            # the closed+round test above passes while the shape is a quad.
            # Sample the cubics instead (see `_points_hug_circle`).
            if not PrimitiveMixin._points_hug_circle(pts, c[:2], r):
                return None
            return r
        except Exception:
            return None

    @staticmethod
    def _circle_state(mob, a, w, h, rot, parent_offset):
        """Everything that can change `_send_circle`'s native calls."""
        pts = mob.points
        frgbas = mob.__dict__.get('fill_rgbas')
        srgbas = mob.__dict__.get('stroke_rgbas')
        sw = mob.__dict__.get('stroke_width')
        if isinstance(sw, (int, float)):
            swk = float(sw)
        else:
            try:
                swk = np.asarray(sw).tobytes()
            except Exception:
                swk = repr(sw)
        vp = get_viewport()
        gp = mob.__dict__.get('_grow_point')
        return (
            pts.shape, pts.tobytes(),
            None if frgbas is None else (frgbas.shape, frgbas.tobytes()),
            None if srgbas is None else (srgbas.shape, srgbas.tobytes()),
            swk, float(a), float(rot),
            None if parent_offset is None
            else tuple(float(v) for v in parent_offset),
            w, h,
            None if vp is None
            else (vp.center, vp.height, vp.unit_height,
                  None if vp.rotation is None
                  else np.asarray(vp.rotation, dtype=float).tobytes(),
                  vp.frame_center, vp.focal_distance, vp.exponential),
            mob.__dict__.get('_grow_scale', 1.0),
            None if gp is None else tuple(float(v) for v in gp),
            mob.__dict__.get('_rotation_about_point') is not None,
            mob.__dict__.get('_vulkan_progress', 1.0),
            mob.__dict__.get('_vulkan_progress_upper'),
            mob.__dict__.get('_vulkan_progress_lower'),
            mob.__dict__.get('_vulkan_points_partial', False),
        )

    def _replay_circle(self, payload):
        (sx, sy, sr, fr, fg, fb, fill_alpha, progress,
         layers, coords, n, cr, cg, cb) = payload
        dll = self.dll
        dll.AddCircle(sx, sy, sr, fr, fg, fb, 0, 0, 0, 0.0, progress,
                      fill_alpha)
        for _w, _al in layers:
            dll.AddLineStrip(coords, None, n, _w, cr, cg, cb, _al)

    def _send_circle(self, mob, a, w, h, rot, parent_offset=None):
        sig = None
        try:
            sig = self._circle_state(mob, a, w, h, rot, parent_offset) + (
                id(self.dll),)
            cached = mob.__dict__.get('_rtm_circle_cache')
            if cached is not None and cached[0] == sig:
                self._replay_circle(cached[1])
                return
        except Exception:
            sig = None
        cx, cy, cz = path_center(mob)
        if parent_offset is not None:
            cx += parent_offset[0]; cy += parent_offset[1]
        about = mob.__dict__.get('_rotation_about_point')
        if about is not None:
            neg_rot = -rot
            dx, dy = cx - about[0], cy - about[1]
            c, sn = math.cos(neg_rot), math.sin(neg_rot)
            cx = about[0] + dx * c - dy * sn
            cy = about[1] + dx * sn + dy * c
        _ch = mob.__dict__
        grow_scale = _ch.get('_grow_scale', 1.0)
        grow_pt = _ch.get('_grow_point')
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
        fill_alpha = a * fo
        self.dll.AddCircle(float(sx), float(sy), float(sr), fr, fg, fb, 0, 0, 0, 0.0, progress, fill_alpha)
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
            if progress >= 1.0 - 1e-12 and rot == 0.0:
                # Full, unrotated ring: use the cached unit circle instead of
                # 2*segs trig calls and a Python list per frame.
                c, s = _unit_circle(segs)
                xy = np.empty((segs + 1, 2), dtype=np.float32)
                xy[:, 0] = sx + c * sr
                xy[:, 1] = sy - s * sr
                coords = (ctypes.c_float * (len(xy) * 2)).from_buffer_copy(
                    np.ascontiguousarray(xy, dtype=np.float32))
                layers = list(self._stroke_layers(sw, a))
                for _w, _al in layers:
                    self.dll.AddLineStrip(coords, None, len(xy), _w,
                                          cr, cg, cb, _al)
                if sig is not None:
                    try:
                        mob._rtm_circle_cache = (
                            sig,
                            (float(sx), float(sy), float(sr), fr, fg, fb,
                             float(fill_alpha), float(progress), layers,
                             coords, len(xy), cr, cg, cb),
                        )
                    except Exception:
                        pass
            else:
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
