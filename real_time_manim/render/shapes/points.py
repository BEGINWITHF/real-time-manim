"""Point-like senders: dots, points, dashed lines and point clouds."""

import math
import numpy as np
from real_time_manim.render.util import manim_to_screen, get_opacity


class PointMixin:


    def _dot_own_points_box(self, mob):
        """Centre and half-min-extent of the mobject's OWN points.

        `get_center()`/`width`/`height` are family-wide: they span the mobject
        and every submobject.  A `VDict(show_keys=True)` appends the key label
        to the value (`mob.add(key_text)`), so `registry["dot"]` is a Dot
        carrying a `Tex("dot")` submobject, and `get_center()` lands 0.462
        units (62 px at 1080p) LEFT of the disc while CE draws the disc from
        the circle's own points.  Measured on VectorizedContainers: RTM's dot
        sat at cx 457 against CE's 517, overlapping the "dot" label, and was
        also 10 % oversized because `min(width, height)` measures the label's
        0.351 height rather than the circle's 0.32.

        A Dot's bezier control points sit exactly on the circle, so the own
        point box is both the drawn centre and the drawn radius.  Text/Tex
        carry no points of their own (the glyphs are submobjects) -- which is
        what a FocusOn target often is -- so a point-less mobject falls back to
        the family bbox.
        """
        pts = getattr(mob, "points", None)
        try:
            if pts is None or len(pts) == 0:
                return None
            lo = pts.min(axis=0)
            hi = pts.max(axis=0)
        except Exception:
            return None
        c = (lo + hi) / 2.0
        return np.array([float(c[0]), float(c[1]), float(c[2])]), \
            float(min(hi[0] - lo[0], hi[1] - lo[1])) / 2.0

    def _send_dot(self, mob, a, w, h, parent_offset=None):
        own = self._dot_own_points_box(mob)
        if own is not None:
            (cx, cy, cz), own_rad = own
        else:
            cx, cy, cz = mob.get_center()
            own_rad = None
        # A Dot is a position, so a group's translation applies to it exactly
        # like it does to a Line's endpoints: dropping it drew every Dot of a
        # VGroup at the group's ORIGIN offset.
        if parent_offset is not None:
            cx += parent_offset[0]
            cy += parent_offset[1]
        # GrowFromPoint: the disc has to scale like every other sender
        # (`_send_circle` already multiplies its radius by `grow_scale`).
        grow_scale = getattr(mob, '_grow_scale', 1.0)
        grow_pt = getattr(mob, '_grow_point', None)
        if grow_scale != 1.0 and grow_pt is not None:
            cx = grow_pt[0] + (cx - grow_pt[0]) * grow_scale
            cy = grow_pt[1] + (cy - grow_pt[1]) * grow_scale
        sx, sy = manim_to_screen(cx, cy, w, h, cz)
        # The radius is in manim units, so it converts with the frame height that
        # is on screen -- the same rule as `_stroke_width`.  `h / 8.0` ignored the
        # camera: its centre already moved with the zoom (manim_to_screen) while
        # the disc stayed the size it had before the camera moved, so a zooming
        # scene showed a dot that never grew over `frame.animate.scale(...)` and
        # then snapped to the right size once the play ended
        # (FollowingGraphCamera: CE 22 -> 44 px smoothly, RTM 22, 22, ..., 44).
        scale_y = h / self._visible_frame_height()
        # Radius: the mobject's OWN point box when it has points -- a Dot's
        # bezier handles sit exactly on the circle, so that box is the drawn
        # disc (see `_dot_own_points_box`).  Falling back on `min(width,
        # height) / 2`: a VDict with show_keys=True stretches each entry to
        # line up with its key label (measured: width 1.244 against height
        # 0.351 for a radius-0.16 Dot), and taking the radius from `width`
        # drew a disc 3.9x too big (emitted AddCircle radius 37px where CE's
        # dot is 9.6px, 3882 yellow pixels against 226).  The smaller axis is
        # the un-stretched one -- but it still measures the LABEL for a
        # labelled dot, which is 10 % fat; the own-point box removes that.
        rad = (own_rad if own_rad is not None
               else min(mob.width, mob.height) / 2.0) * scale_y * grow_scale
        try:
            fo = float(mob.fill_rgbas[:, 3].max())
        except Exception:
            fo = get_opacity(mob, 'fill', 1.0)
        if fo <= 0:
            return
        # `_color(mob, a)` bakes BOTH `a` and the fill opacity into the RGB
        # (get_fill_rgb does `int(r * 255 * alpha * fo)`), and the alpha
        # argument below multiplies them in again -> (a*fo)^2.  Straight-alpha
        # wants full-strength colour and the opacity in the alpha only.
        r, g, b = self._fill_color(mob)
        fo = min(fo, getattr(mob, '_dot_max_opacity', 1.0))
        self.dll.AddCircle(sx, sy, rad, r, g, b, 0, 0, 0, 0.0, 1.0, a * fo)

    def _send_dashed_line(self, mob, a, w, h, rot=0.0, parent_offset=None):
        # same grow/offset/rotation treatment as _send_line, so a dashed line
        # inside a group follows that group's transform and rotation
        s = np.array(mob.get_start(), dtype=float)
        e = np.array(mob.get_end(), dtype=float)
        # The dash PATTERN is fixed by the line's own length (CE counts the
        # dashes once, from the un-animated line), so it has to be computed
        # before `_grow_scale` stretches the endpoints: a GrowFromPoint only
        # scales the existing dashes, it must not re-count them every frame.
        base_len = float(np.linalg.norm(e - s))
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
        about = getattr(mob, '_rotation_about_point', None)
        # Same rule as `_send_line`: when `_write_rotate` registered a pivot the
        # manim-space turn below already IS the whole rotation, so the
        # screen-space `_rotate_point` tail must not also run.  This sender
        # never consulted `_rotation_about_point` at all, so a dashed line in a
        # pivot-rotating group swung around the group's CENTRE instead of the
        # pivot `_write_rotate` recorded -- visually a different arc.
        pivoted = about is not None
        if pivoted:
            pivot = np.array(about, dtype=float)
            neg_rot = -rot
            c, sn = math.cos(neg_rot), math.sin(neg_rot)
            dx, dy = s[0] - pivot[0], s[1] - pivot[1]
            s = np.array([pivot[0] + dx * c - dy * sn,
                          pivot[1] + dx * sn + dy * c, s[2]])
            dx, dy = e[0] - pivot[0], e[1] - pivot[1]
            e = np.array([pivot[0] + dx * c - dy * sn,
                          pivot[1] + dx * sn + dy * c, e[2]])
            sx1, sy1 = manim_to_screen(s[0], s[1], w, h, s[2])
            sx2, sy2 = manim_to_screen(e[0], e[1], w, h, e[2])
        else:
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
        # The stroke opacity rides the ALPHA, not the colour (straight-alpha
        # blend, vulkan_init.c:633) -- same rule as `_send_square`.  Baking
        # `so` into the colour made a fading DashedLine replace the background
        # with a darkening solid instead of fading out over it.
        a = a * so
        # Manim CE does NOT tile `dash_length` along the line.  It first
        # picks (DashedLine._calculate_num_dashes):
        #     num_dashes = max(2, ceil(length / dash_length * dashed_ratio))
        # and then splits the whole line so that `num_dashes` dashes and
        # `num_dashes - 1` gaps EXACTLY fill it, dash first, gap between,
        # full dash flush at the end (DashedVMobject, open curve):
        #     dash = dashed_ratio / num_dashes * length
        #     gap  = (1 - dashed_ratio) / (num_dashes - 1) * length
        # The old flat tiling (`dash = dash_length`, gap = dash*(1-r)/r)
        # drifted against that pattern and ran off the end of the line:
        # LinesAnglesAndVectors' DashedLine (length 2.2, dash_length 0.18,
        # ratio 0.5) drew six 0.18-long dashes plus a 0.04 stub where CE
        # draws seven equal 0.157 dashes with 0.183 gaps, flush at both
        # ends (num_dashes = ceil(2.2 / 0.18 * 0.5) = 7).
        try:
            dl_manim = float(mob.dash_length)
        except Exception:
            dl_manim = 0.05                      # manim DEFAULT_DASH_LENGTH
        if dl_manim <= 0.0:
            # CE itself divides by dash_length when counting the dashes, and
            # the native tile loop would spin forever on a zero-length step.
            dl_manim = 0.05
        try:
            ratio = float(mob.dashed_ratio)
        except Exception:
            ratio = 0.5
        if not 0.0 < ratio < 1.0:
            ratio = 0.5
        if base_len > 1e-9 and dl_manim > 0.0:
            num_dashes = max(2, int(math.ceil(base_len / dl_manim * ratio)))
            dl_manim = ratio / num_dashes * base_len
            gl_manim = (1.0 - ratio) / (num_dashes - 1) * base_len
        else:
            gl_manim = dl_manim
        # Dash lengths are manim-unit sizes, so they convert with the frame
        # height that is actually on screen -- the same rule as
        # `_stroke_width` (a zoomed camera scales CE's dashes with everything
        # else).  Default frame == the old `h / 8.0`.
        scale = h / self._visible_frame_height()
        sw = self._stroke_width(mob)
        # ...and they scale with the mobject under GrowFromPoint instead of
        # re-counting dashes at every intermediate size.
        dl = dl_manim * scale * grow_scale
        gl = gl_manim * scale * grow_scale
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
        # `_color(mob, a)` bakes `a * fill_opacity` into the RGB; the alpha
        # arguments below multiply them in again -> squared.  Full-strength
        # colour, opacity in the alpha only (straight-alpha blend).
        r, g, b = self._fill_color(mob)
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
        # The rotation centre must include the group's offset, exactly like the
        # per-point loop below: without it a PointCloud inside a rotated group
        # swung around a point offset by the group's translation (wrong arc).
        if parent_offset is not None:
            cx += parent_offset[0]
            cy += parent_offset[1]
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

    def _send_point(self, mob, a, w, h, parent_offset=None):
        pos = mob.get_location()
        # A Point IS a position: a group's translation applies to it exactly
        # like it does to a Line's endpoints (the dispatch used to drop it).
        if parent_offset is not None:
            pos = np.array(pos, dtype=float)
            pos[0] += parent_offset[0]
            pos[1] += parent_offset[1]
        sx, sy = manim_to_screen(pos[0], pos[1], w, h, pos[2])
        # Same squared-alpha trap as `_send_dot`: `_color(mob, a)` already
        # folded `a * fill_opacity` into the RGB and the alpha argument then
        # multiplied `a` in a second time.
        try:
            fo = float(mob.fill_rgbas[:, 3].max())
        except Exception:
            fo = get_opacity(mob, 'fill', 1.0)
        r, g, b = self._fill_color(mob)
        self.dll.AddPoint(sx, sy, r, g, b, a * fo, self._dot_radius(mob, h))
