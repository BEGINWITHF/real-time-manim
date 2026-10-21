"""Arrows, arrow tips and lines (an arrow is a line plus a tip)."""

import ctypes
import math
import numpy as np
from real_time_manim.render.util import manim_to_screen, get_opacity, point_path_bounds

# Distinguishes "this attribute was absent" from "present but None" when a
# temporary window is put back the way it was found.
_MISSING = object()


class ArrowMixin:


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
        # It returns a PAIR and only the upper end was read: the shaft ran from
        # its own start to `upper`, so an explicit window (ShowPassingFlash)
        # lost its `lower` edge and the sweep GREW from the start instead of
        # sliding.  Measured against ManimCE on
        # ShowPassingFlash(time_width=0.3) over Arrow(LEFT*3, RIGHT*3): CE's
        # ink rises to 28 % of the finished arrow and returns to 0 as the
        # window slides off, while RTM ramped to 100 % and stuck there (mean
        # |CE-RTM| 44.3 points, worst 99.9).  An untagged mobject reports
        # lower == 0.0, so a plain Create/Uncreate is untouched by this.
        progress_lower, progress_upper = point_path_bounds(mob)
        if progress_upper <= 0:
            return
        progress = progress_upper
        # An explicit window is what a ShowPassingFlash publishes, and CE applies
        # it to EVERY member of the family separately
        # (ShowPartial.interpolate_submobject -> pointwise_become_partial on
        # each submobject, manim/animation/creation.py:126-134), so the tip gets
        # the SAME lower/upper over its OWN contour.  Handing the tip the window
        # is what makes the head light up only as the sweep reaches it -- CE's
        # tip band measures 0 px through frames 5-20, 93 % at frame 40, back to
        # 5 % at 55, where a head pinned whole to the apex never leaves the
        # screen.  Without a window the synthesised head below is kept, so a
        # Create still reveals its tip at full size as it arrives (the behaviour
        # `_send_arrow` was measured with).
        _windowed = hasattr(mob, "_vulkan_progress_upper")
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
                        and (progress >= 1.0 or _windowed))
        r, g, b = self._stroke_color(mob)
        so = get_opacity(mob, 'stroke', 1.0)
        # The incoming alpha belongs to the HEAD; the shaft additionally folds
        # in the stroke opacity (see below).  In CE the head is the arrow's own
        # filled `ArrowTip` submobject -- `ArrowTriangleFilledTip` ships
        # fill_opacity=1, stroke_width=0 (manim tips.py) -- so hiding the
        # shaft's *stroke* never hides the head: `Arrow().set_stroke(opacity=0)`
        # or `.set_stroke(width=0)` draws a bare triangle in CE.
        alpha_in = a
        # The stroke opacity rides the ALPHA, not the colour: native blends
        # straight-alpha (colour*alpha + dst*(1-alpha)), so `int(r * so)` made a
        # fading arrow REPLACE the background with a darkening solid instead of
        # fading out over it -- the exact trap `_send_polygon`/`_send_square`
        # were already fixed for (commits da91860 / 8a4414e).  `r,g,b` are
        # shared by the shaft AND the head below, so the fold belongs in `a`.
        a = a * so
        # The head is NOT a stroke in CE, so it keeps the incoming alpha: only
        # the shaft folds in `so`.  This is why the head is emitted with
        # `head_a` below and the shaft with `a`.
        head_a = alpha_in
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
        # The tip length is a manim-unit size, so it converts with the visible
        # frame height like every other size (see `_visible_frame_height`);
        # `h / 8.0` kept the arrowhead a fixed pixel size while the camera zoomed.
        scale_y = h / self._visible_frame_height()
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
            # The END is measured from the shaft's own start, so it is computed
            # BEFORE the start is moved to `lower` -- otherwise `ex` would be
            # `upper` of a segment that already began at `lower`.
            if progress >= 1.0:
                ex, ey = base_x, base_y
            else:
                ex = sx1 + (base_x - sx1) * progress
                ey = sy1 + (base_y - sy1) * progress
            # A plain Create reports lower == 0.0 and is untouched; only an
            # explicit window moves the start.
            if progress_lower > 0.0:
                stx = sx1 + (base_x - sx1) * progress_lower
                sty = sy1 + (base_y - sy1) * progress_lower
            else:
                stx, sty = sx1, sy1
            # `length` above measures to the TIP's apex, which stays out at the
            # arrowhead even while ShowPartial has collapsed the shaft's own
            # points to nothing -- so the shaft can still be a single point when
            # `can_stroke` says otherwise.  A collapsed path inks nothing in
            # manim either; native has no direction for the quad.
            if abs(ex - stx) >= 1e-6 or abs(ey - sty) >= 1e-6:
                # NB: `px` is reassigned to the head's perpendicular below
                # (px = -uy), so the shaft is emitted while it still holds the
                # stroke width.
                self._emit_stroke(stx, sty, ex, ey, px, r, g, b, a)
        if use_real_tip:
            self._send_arrow_tip(mob, tip, head_a, w, h, rot, parent_offset,
                                 window=(progress_lower, progress_upper)
                                 if _windowed else None)
            return
        # The head is its own filled triangle, so the shaft's invisibility does
        # not take it with it (comment at `can_stroke`).  Only the shaft's
        # GEOMETRY is load-bearing: native needs a direction to orient the
        # head's perpendicular with, and a zero-length shaft has none -- a
        # collapsed path inks nothing in manim either.
        if length <= 0 or head_a <= 0:
            return
        px = -uy
        py = ux
        hx1 = base_x + px * head_w
        hy1 = base_y + py * head_w
        hx2 = base_x - px * head_w
        hy2 = base_y - py * head_w
        head_verts = (ctypes.c_float * 6)(sx2, sy2, hx2, hy2, hx1, hy1)
        # `head_a`, not `a`: `a` has the shaft's stroke opacity folded in, and
        # the head is a filled tip whose own opacity is independent of it.
        self.dll.AddPolygon(
            sx2, sy2, r, g, b, r, g, b, 0,
            3, head_verts, progress, head_a, 1,
        )

    def _send_arrow_tip(self, mob, tip, a, w, h, rot, parent_offset=None,
                        window=None):
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

        `window` is the flash's ``(lower, upper)`` pair, applied to the TIP's own
        contour the way CE applies it: `ShowPartial.interpolate_submobject` walks
        `get_all_families_zipped` and calls `pointwise_become_partial` on every
        member with the SAME bounds (manim/animation/creation.py:126-134), so the
        head lights up only as the sweep reaches it rather than sitting whole on
        the apex.  It is stamped on the tip for the duration of the call and
        removed after, so the next animation cannot inherit a stale window.
        """
        rot_orig = -rot
        _saved = None
        if window is not None:
            # Remember whatever the tip already carried so it can be put back:
            # a nested arrow may own a window of its own, and overwriting it
            # (or leaving mine behind) would clip the NEXT animation.
            _saved = {a: getattr(tip, a, _MISSING)
                      for a in ("_vulkan_progress_lower",
                                "_vulkan_progress_upper",
                                "_vulkan_points_partial")}
            tip._vulkan_progress_lower = float(window[0])
            tip._vulkan_progress_upper = float(window[1])
            # The window is a clip over the tip's COMPLETE contour, so a cut-path
            # tag from an earlier Create would describe the wrong points (same
            # rule `_write_passing_flash` applies to the whole family).
            tip._vulkan_points_partial = False
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
                # Rotate about z, so the z component is unchanged.  Building
                # only the xy part here was (3,) + (2,): every Arrow that
                # turned -- scene 57's Rotating(about_point) -- raised a
                # broadcast ValueError and killed the render.
                rot_d = np.array([d[0] * ca - d[1] * sa,
                                  d[0] * sa + d[1] * ca,
                                  d[2] if d.size > 2 else 0.0])
                moved = centre + rot_d
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
            if _saved is not None:
                for _attr, _value in _saved.items():
                    if _value is _MISSING:
                        if hasattr(tip, _attr):
                            delattr(tip, _attr)
                    else:
                        setattr(tip, _attr, _value)

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
        # True in the pivot branch: the manim-space turn below already IS the
        # whole rotation, so the shared screen-space `_rotate_point` tail must
        # not run again on top of it.  `_send_arrow` has always stopped at the
        # pivot turn; `_send_line` applied the tail unconditionally and turned
        # the line through 2*theta for RTM's own rotation channel.
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
            # `_write_rotate` registers the pivot for EVERY pivot rotation, so
            # this branch is reached with `rot == 0` too (manim's own Rotate,
            # whose points are already turned).  Nothing else to do here.
        else:
            sx1, sy1 = manim_to_screen(s[0], s[1], w, h, s[2])
            sx2, sy2 = manim_to_screen(e[0], e[1], w, h, e[2])
            cx, cy, cz = mob.get_center()
            if parent_offset is not None:
                cx += parent_offset[0]; cy += parent_offset[1]
            scx, scy = manim_to_screen(cx, cy, w, h, cz)
        if not pivoted:
            sx1, sy1 = self._rotate_point(sx1, sy1, scx, scy, rot)
            sx2, sy2 = self._rotate_point(sx2, sy2, scx, scy, rot)
        r, g, b = self._stroke_color(mob)
        so = get_opacity(mob, 'stroke', 1.0)
        if so <= 0:
            return
        # The stroke opacity rides the ALPHA, not the colour (straight-alpha
        # blend, vulkan_init.c:633) -- same rule as `_send_square`/`_send_arrow`
        # below.  Baking `so` into the colour made a fading line replace the
        # background with a darkening solid instead of fading out over it.
        a = a * so
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
                        # `_send_vmobject` rotates in MANIM space, but `rot`
                        # here is the screen-space angle the dispatch handed
                        # down (screen_rot == -manim_rot) -- the same inversion
                        # `_send_arrow_tip` does with `rot_orig = -rot`.  Passing
                        # it straight through spun the warped line the wrong way.
                        # Wrap the call so a raise inside it cannot silently
                        # fall through to the chord draw below, which would
                        # paint the straight start->end segment CE never draws.
                        try:
                            self._send_vmobject(mob, a, w, h, parent_offset,
                                                -rot, exact_width=True)
                        except Exception:
                            return
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
        #
        # It returns a PAIR and only the upper end was read: the stroke ran from
        # the line's own start to `upper`, so an explicit window
        # (ShowPassingFlash) lost its `lower` edge and the sweep GREW from the
        # start instead of sliding -- measured on
        # ShowPassingFlash(time_width=0.3) over a Line, the lit count reached
        # 1980 px = 100 % of the full line, where Square (which does honour the
        # window) held 30 %.  An untagged mobject reports lower == 0.0, so a
        # plain Create/Uncreate is untouched by this.
        progress_lower, progress_upper = point_path_bounds(mob)
        if progress_upper <= 0:
            return
        # the END is measured from the line's own start, so it is computed
        # BEFORE the start is moved to `lower` -- otherwise `ex` would be
        # `upper` of a segment that already began at `lower`.
        progress = progress_upper
        if progress >= 1.0:
            ex, ey = sx2, sy2
        else:
            ex = sx1 + (sx2 - sx1) * progress
            ey = sy1 + (sy2 - sy1) * progress
        if progress_lower > 0.0:
            sx1 = sx1 + (sx2 - sx1) * progress_lower
            sy1 = sy1 + (sy2 - sy1) * progress_lower
        # A path the cut collapsed to a point has nothing to stroke: manim's
        # butt cap inks nothing, and native would have no direction to build
        # the quad from (ShowPartial at sub_alpha 0 is the common case).
        if abs(ex - sx1) < 1e-6 and abs(ey - sy1) < 1e-6:
            return
        cap = getattr(mob, 'cap_style', None)
        cap_name = getattr(cap, 'name', '')
        if not cap_name and isinstance(cap, int):
            cap_name = {1: 'ROUND', 3: 'SQUARE'}.get(cap, '')
        if not cap_name and cap is not None:
            cap_name = str(cap)
        cap_name = str(cap_name).upper()
        half = float(px) * 0.5
        dx, dy = ex - sx1, ey - sy1
        ln = math.hypot(dx, dy)
        line_start = (sx1, sy1)
        line_end = (ex, ey)
        if ln > 1e-6 and cap_name in ('ROUND', 'BUTT'):
            # Native's line quad extends `half_thick` past BOTH endpoints
            # (draw_line.c), i.e. it already paints a square cap.  A round cap
            # therefore has to shorten the shaft by half a width and put a disc
            # on each end; a butt cap has to shorten it and stop.  AUTO/default
            # keeps the historical behaviour for every calibrated scene.
            ux, uy = dx / ln, dy / ln
            if ln > 2.0 * half:
                line_start = (sx1 + ux * half, sy1 + uy * half)
                line_end = (ex - ux * half, ey - uy * half)
            else:
                line_start = line_end = ((sx1 + ex) * 0.5, (sy1 + ey) * 0.5)
        self._emit_stroke(line_start[0], line_start[1],
                          line_end[0], line_end[1], px, r, g, b, a)
        if cap_name == 'ROUND':
            try:
                for cx, cy in ((sx1, sy1), (ex, ey)):
                    self.dll.AddCircle(float(cx), float(cy), half,
                                       int(r), int(g), int(b),
                                       0, 0, 0, 0.0, 1.0, a)
            except Exception:
                pass
