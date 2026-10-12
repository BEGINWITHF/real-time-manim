"""Turning mobjects into native draw calls.

`_send_impl` is the dispatcher: it picks a sender per mobject kind,
handles transform/fade channels and recurses through the family."""

import math
import numpy as np
from manim import (
    Square, Circle, Line, Rectangle, Polygon, Polygram,
    Arrow, Dot, DashedLine,
    Arc, Ellipse, Point, Text, VGroup, Group, VMobject
)
from manim.mobject.types.image_mobject import AbstractImageMobject
from manim.mobject.types.point_cloud_mobject import PMobject

from real_time_manim.animations import (
    get_anim_opacity,
    get_anim_rotation,
)
from manim.mobject.text.tex_mobject import MathTexPart

from real_time_manim.window.paint_order import (
    NATIVE_MAX_POLYGON_VERTS,
    container_subs,
    depth_key,
    depth_order,
    lend_grow,
    release_grow,
    split_mixed_depth,
    split_mixed_z,
)


class PaintMixin:

    def _root_paint(self, cam, roots, idx, mob, angle, fixed_ids, cam_images):
        """The whole-root paint as one deferred unit (see ``_PaintQueue``)."""
        from real_time_manim.camera_state import (
            set_viewport, get_viewport, Viewport, DEFAULT_FRAME_HEIGHT)

        def paint():
            if idx in cam_images:
                # An image that reads the camera's array only shows what was
                # already drawn into it (report R10-5).
                self._rasterise_camera_prefix(cam, roots, idx)
            if id(mob) in fixed_ids:
                saved = get_viewport()
                set_viewport(Viewport((0.0, 0.0), DEFAULT_FRAME_HEIGHT))
                try:
                    self._send(mob, angle, parent_alpha=1.0)
                finally:
                    set_viewport(saved)
            else:
                self._send(mob, angle, parent_alpha=1.0)

        return paint

    def _paint_order(self, items):
        """Sibling paint order; the collection pass skips the depth sort.

        While a queue is open every leaf is re-sorted against every other leaf
        of the frame anyway, so sorting the siblings here would only repeat
        that work -- and the collection index (what the queue tie-breaks on)
        must stay the original one either way.
        """
        if getattr(self, "_paint_queue", None) is not None:
            return list(enumerate(items))
        return depth_order(items)

    @staticmethod
    def _camera_image_prefixes(cam, roots):
        """Indices of the roots that display the camera's own pixel array.

        ``ImageMobjectFromCamera.get_pixel_array()`` returns
        ``scene.camera.pixel_array`` **live** (manim
        ``image_mobject.py:336``), and manim's renderer walks
        ``camera.capture_mobjects(list(scene.mobjects))`` in list order, so by
        the time it reaches such an image the array already holds the
        background plus everything drawn before it: the image is a copy of the
        scene as drawn so far.

        RTM draws vectors on the GPU and never writes that array
        (``_rasterise_custom_camera`` explicitly exempts a plain ``Camera``),
        so ``send_image`` uploaded the cleared background -- black, invisible.
        Measured on ImagesAndSvg (report R10-5): 2172 px of CE content missing,
        three blobs whose bboxes map back onto the swatch / badge / quad
        through ``from_camera``'s box, and one unchanged texture key for all 19
        visible frames under ``RTM_TEX_DEBUG``.
        """
        if cam is None:
            return {}
        live = getattr(cam, "pixel_array", None)
        if live is None:
            return {}
        out = set()
        for i, mob in enumerate(roots):
            if not isinstance(mob, AbstractImageMobject):
                continue
            getter = getattr(mob, "get_pixel_array", None)
            if getter is None:
                continue
            try:
                if getter() is live:
                    out.add(i)
            except Exception:
                continue
        return out

    def _dbg_arrow(self, mob, where, parent_transforming):
        """Env-gated trace of which Arrow branch ran (R10-6 diagnosis only).

        Set ``RTM_ARROW_DEBUG=<path>`` to append one line per Arrow dispatch:
        which branch took it, the transform/progress flags, and whether it is a
        double-headed arrow.  No-op when the variable is absent.
        """
        try:
            import os
            path = os.environ.get("RTM_ARROW_DEBUG")
            if not path:
                return
            st = getattr(mob, "start_tip", None)
            has_start = bool(st is not None and st in mob)
            subs = [type(s).__name__ for s in getattr(mob, "submobjects", [])]
            try:
                from real_time_manim.state import get_anim_opacity as _gao
                ao = _gao(mob)
            except Exception:
                ao = "<n/a>"
            fo = getattr(mob, "fill_opacity", "<n/a>")
            try:
                fra = float(mob.fill_rgbas[:, 3].max())
            except Exception:
                fra = "<n/a>"
            hb = hasattr(mob, "_vulkan_progress_upper")
            with open(path, "a", encoding="utf-8") as fh:
                fh.write(
                    "%s where=%s transforming=%s parent=%s progress=%s "
                    "has_start_tip=%s subs=%s anim_op=%s fill_op=%s "
                    "fo_rgbas=%s has_bounds=%s\n"
                    % (type(mob).__name__, where,
                       getattr(mob, "_transforming", None), parent_transforming,
                       getattr(mob, "_vulkan_progress", 1.0), has_start, subs,
                       ao, fo, fra, hb))
        except Exception:
            pass

    @staticmethod
    def _dbg_emit(tag, text):
        """Env-gated free-form emission log (R10-6 diagnosis)."""
        try:
            import os
            path = os.environ.get("RTM_ARROW_DEBUG")
            if not path:
                return
            with open(path, "a", encoding="utf-8") as fh:
                fh.write("%s %s\n" % (tag, text))
        except Exception:
            pass

    @staticmethod
    def _rasterise_camera_prefix(cam, roots, upto):
        """Replay ``roots[:upto]`` into the camera array, exactly as CE had it.

        CE reaches that array mid-``capture_mobjects``; this reproduces the
        state it saw: clear to the background, then draw only the roots that
        precede the image.  A root that comes *after* it must stay out -- that
        is what makes the copy a prefix and not the whole frame.
        """
        try:
            reset = getattr(cam, "reset", None)
            if callable(reset):
                reset()
            cam.capture_mobjects(list(roots[:upto]))
            return True
        except Exception:
            return False

    def _glyph_baseline(self, mob):
        """Approximate the x-height baseline of a Text from its glyph bottoms.

        Descender glyphs (g/p/j/y/q...) are the minority of deepest bottoms;
        the shallow half of letter bottoms cluster on the typographic baseline.

        Returns ``None`` for a multi-line Text -- the whole baseline heuristic
        assumes ONE visual line of words ("same-font words sharing a center
        after arrange() fall onto one baseline"), and applying it to a tall
        block moves the entire block: measured on ``FlagMappingScene``'s
        20-line body it produced dy = -2.55 units (-153 px), so most of the
        block was drawn below the frame (glyph first points out to y=600 in a
        480 px window, d(last) -1.59).  A tall block is detected by comparing
        its height with its tallest glyph, which is scale-free.
        """
        bottoms = []
        glyph_heights = []
        stack = list(getattr(mob, 'submobjects', []))
        while stack:
            s = stack.pop()
            pts = getattr(s, 'points', None)
            if pts is not None and len(pts):
                bottoms.append(float(pts[:, 1].min()))
                glyph_heights.append(float(pts[:, 1].max() - pts[:, 1].min()))
            if getattr(s, 'submobjects', None):
                stack.extend(s.submobjects)
        if not bottoms:
            return None
        tallest = max(glyph_heights) if glyph_heights else 0.0
        if tallest > 0.0:
            try:
                if float(mob.height) > 2.2 * tallest:
                    return None
            except Exception:
                pass
        bottoms.sort()
        n = len(bottoms)
        shallow = bottoms[max(0, int(n * 0.5)):]
        return float(np.median(shallow))

    def _text_baseline_dy(self, mob):
        """Approach A: the vertical (manim-unit) offset that moves this Text's
        typographic baseline to ``center_y - ascent/2``, independent of its
        bounding box (which manim pads downward by descender depth).

        Clean words (no descenders) return ~0 and stay put; descender-heavy
        words are lowered, so same-font words sharing a center after arrange()
        fall onto one baseline.  Applied as a draw-time offset — the mobject's
        points are never mutated, so it cannot cause positional jitter.
        """
        base = self._glyph_baseline(mob)
        if base is None:
            return 0.0
        try:
            center = mob.get_center()[1]
        except Exception:
            return 0.0
        try:
            top = float(np.max([
                s.points[:, 1].max()
                for s in mob.family_members_with_points()
                if s.points is not None and len(s.points)
            ]))
        except Exception:
            return 0.0
        if top - base <= 1e-6:
            return 0.0
        dy = (center - (top - base) / 2.0) - base
        return dy if abs(dy) > 1e-9 else 0.0

    def _text_row_ids(self, scene, skip_ids=None):
        """Return ids of visible, same-font Text roots that sit on one visual
        line (vertical spans overlap) with at least one other such word.

        Only multi-word lines need baseline alignment — isolated words and
        titles are deliberately excluded so the offset never moves them.
        """
        roots = []
        for mob in scene.mobjects:
            if skip_ids and id(mob) in skip_ids:
                continue
            if not isinstance(mob, Text) or not getattr(mob, 'submobjects', None):
                continue
            if get_anim_opacity(mob) < 0.5:
                continue
            try:
                font_size = mob._font_size
            except Exception:
                continue
            try:
                bottom = mob.get_bottom()[1]
                top = mob.get_top()[1]
            except Exception:
                continue
            roots.append({'id': id(mob), 'font': font_size,
                          'b': bottom, 't': top})
        ids = set()
        for i in range(len(roots)):
            for j in range(i + 1, len(roots)):
                a, b = roots[i], roots[j]
                if a['font'] == b['font'] and a['b'] < b['t'] and b['b'] < a['t']:
                    ids.add(a['id'])
                    ids.add(b['id'])
        return ids

    def _text_baseline_for(self, mob):
        """The draw-time baseline offset for this Text -- decided ONCE.

        ``_text_row_ids`` rebuilds the "same-font words on one visual line"
        set from ``scene.mobjects`` every frame, and a row-mate enters that
        list whenever ITS animation starts.  So row membership is not a
        property of the word, it is a property of the clock: re-reading it
        moves words that are already standing still.

        Measured on ``MatchersAndBooleanOps``: only ``highlight me`` is a Text
        root for frames 1-36, so its row is empty and it is drawn unshifted;
        the frame ``cross me out`` joins ``scene.mobjects`` the two overlap on
        one line, the row forms, and the offset landed in that same frame --
        the word jumped 6 px (0.0451 units) mid-scene and then sat 7 px away
        from where CE draws it (CE applies no such shift at all, so the
        unshifted pose was the correct one).  A word may never move after it
        has been drawn, hence the verdict -- a zero included -- is cached on
        the first frame the word is drawn at rest.

        * at rest (``opacity >= 0.95``): decide from the row as it exists
          right now, cache it, and never look again.  Words animated together
          therefore still line up, and the isolated-text / single-line case
          caches ``0.0`` so a title is never disturbed.
        * mid-fade / mid-scale: the geometry is transient, so ``0.0`` is
          returned WITHOUT caching -- retry on a later frame instead of
          locking in a verdict taken from a pose that never repeats.
        """
        dy = getattr(mob, '_baseline_dy', None)
        if dy is not None:
            return dy
        if get_anim_opacity(mob) < 0.95:
            return 0.0
        in_row = id(mob) in getattr(self, '_row_text_ids', ())
        dy = self._text_baseline_dy(mob) if in_row else 0.0
        mob._baseline_dy = dy
        return dy

    @staticmethod
    def _edges_are_straight(pts):
        """True when every closed cubic-bezier edge keeps its two control
        points collinear with the chord between its anchors (i.e. the edges
        are straight segments, as for an axis-aligned or merely rotated quad).
        Any non-affine warp (e.g. Homotopy y += A*sin(x)) bends a control point
        off the chord, giving a non-zero perpendicular deviation, so the edge
        is a curve and must be rendered as a bezier path."""
        n = len(pts)
        if n < 4:
            return True
        # Straight segments have control points exactly collinear (dev ~ 0.0);
        # even a faint Homotopy warp yields dev >= ~1e-3.  1e-4 cleanly splits.
        TOL = 1e-4
        for i in range(0, n, 4):
            if i + 3 >= n:
                break
            p0 = pts[i][:2]
            p3 = pts[i + 3][:2]
            cx = p3[0] - p0[0]
            cy = p3[1] - p0[1]
            L2 = cx * cx + cy * cy
            if L2 <= 0.0:
                continue
            for c in (pts[i + 1][:2], pts[i + 2][:2]):
                vx = c[0] - p0[0]
                vy = c[1] - p0[1]
                cross = vx * cy - vy * cx
                dist = abs(cross) / (L2 ** 0.5)
                if dist > TOL:
                    return False
        return True

    def _send(self, *args, **kwargs):
        """Entry point: guard against a container that iterates itself.

        The real fix is ``container_subs`` (iterate ``submobjects``); this keeps a
        future mistake from turning into a RecursionError.
        """
        stack = getattr(self, '_send_stack', None)
        if stack is None:
            stack = self._send_stack = set()
        key = id(args[0]) if args else None
        if key in stack:
            return
        stack.add(key)
        try:
            return self._send_impl(*args, **kwargs)
        finally:
            stack.discard(key)

    @staticmethod
    def _paint_as_unit(mob):
        """Does ``_send_impl`` paint ``mob`` in one go instead of recursing?

        Three cases, matching the dispatch below exactly:

        * at most one point-bearing member in the *whole* subtree -- the
          paint is that member, so grouping cannot differ from CE's sort;
        * a non-``VGroup`` parent that carries points of its own (``Arrow``,
          a ``Rectangle`` holding its SampleSpace dividers, ...): it paints
          itself first and walks its children afterwards, so splitting it
          would leave the parent in front of its own children, out of depth
          order -- the subtree stays one unit.  ``Text`` lands here too: it
          has no points itself but paints its glyphs from ``_letter_alphas``
          in a single call, so its characters must stay inside that path;
        * ``VGroup`` / ``Group`` / ``MathTexPart`` only *dispatch* their
          children -- and so does a container with no points of its own
          (``Graph``, ``MathTex``, both reached via the dispatcher walk in
          ``_send_impl``).  Walking them lets every leaf take its own place
          in the frame-wide depth sort.

        The "lone member" test must scan the WHOLE family, not the direct
        children: PolyhedraShowcase's ``solids`` VGroup holds six Polyhedrons
        -- VGroups with no points of their own -- so
        ``any(sub.has_points() for sub in subs)`` was False, the whole scene
        became ONE unit painted in document order, and over 35 members came
        out inverted against CE (two ConvexHull3D faces blending with the
        wrong one in front).  The same gap kept each polyhedron's ``Graph`` a unit,
        painting all of its cells and edges at the graph's centre key.
        """
        if len(mob.family_members_with_points()) <= 1:
            return True
        if isinstance(mob, (VGroup, Group, MathTexPart)):
            return False
        if isinstance(mob, Text) or getattr(mob, '_is_text', False):
            return True
        return bool(mob.has_points())

    def _send_impl(self, mob, angle=0.0, parent_alpha=1.0, parent_offset=None, parent_transforming=False, parent_is_text=False, _skip_children=False):
        w, h = self.win_w, self.win_h
        own_alpha = get_anim_opacity(mob)
        a = parent_alpha * own_alpha
        if a <= 0:
            return

        # Collection pass (see _PaintQueue): record what this subtree would
        # paint, in its own depth order, instead of painting it now.  Only the
        # nodes that paint themselves as a unit land here; a VGroup container
        # falls through to its branch below and is walked, so its leaves are
        # queued individually and can interleave with the other roots'.
        collect = getattr(self, '_paint_queue', None)
        if collect is not None and self._paint_as_unit(mob):
            if (mob.submobjects
                    and not isinstance(mob, (Arrow, DashedLine, Text))
                    and not getattr(mob, '_is_text', False)
                    and (split_mixed_z(mob)
                         or split_mixed_depth(mob, collect.viewport))):
                # CE flattens the family and stable-sorts every member by its
                # OWN z_index, so a subtree that disagrees (a DiGraph edge:
                # Line z=-1 with a z=0 arrow tip) cannot be one unit -- one z
                # slot would paint the tip with the edge instead of in the z=0
                # block, where a vertex it overlaps covers it.  The same holds
                # for depth under a ThreeDCamera: it sorts every member by its
                # own camera-space depth, so a container whose centre key is
                # nowhere near its children's keys (ThreeDAxes' NumberLine:
                # centre 0.0, cells -2.60..+2.48) cannot be one block either --
                # one key pins the whole axis to 0.0, on top of the sphere and
                # under the torus, both backwards from CE.  Queue the parent's
                # own paint at the unit key (children suppressed) and walk each
                # child so it reaches the queue at its own z and depth.  Arrow
                # / DashedLine / Text draw their children inside a single
                # specialised sender, so splitting them would double-draw the
                # tip or drop glyphs; they stay one unit regardless.
                collect.add(
                    depth_key(mob, collect.viewport),
                    lambda: self._send(mob, angle, parent_alpha=parent_alpha,
                                       parent_offset=parent_offset,
                                       parent_transforming=parent_transforming,
                                       parent_is_text=parent_is_text,
                                       _skip_children=True),
                    mob,
                )
                for sub in mob.submobjects:
                    # The parent paints itself at its own z and the children
                    # are queued separately, so the grow state has to travel
                    # with them -- the loan is only dropped once the queue has
                    # flushed (see release_grow).
                    need_gs, need_gp = lend_grow(mob, sub)
                    self._send(sub, angle, parent_alpha=parent_alpha,
                               parent_offset=parent_offset,
                               parent_transforming=parent_transforming,
                               parent_is_text=parent_is_text)
                    release_grow(collect, sub, need_gs, need_gp)
                return
            _k = depth_key(mob, collect.viewport)
            collect.add(
                _k,
                lambda: self._send(mob, angle, parent_alpha=parent_alpha,
                                   parent_offset=parent_offset,
                                   parent_transforming=parent_transforming,
                                   parent_is_text=parent_is_text),
                mob,
            )
            return

        rot = get_anim_rotation(mob) + angle
        grow_rot = getattr(mob, '_grow_rot', 0.0)
        rot += grow_rot

        is_text = isinstance(mob, Text) or getattr(mob, '_is_text', False) or parent_is_text

        if isinstance(mob, Text) and hasattr(mob, 'submobjects') and mob.submobjects:
            # Tag all text characters so they're recognized as text even
            # when rendered through an intermediate Group (e.g. LaggedStartMap).
            # This prevents the _transforming stroke logic in _send_vmobject
            # from adding unwanted borders to text characters during animation.
            # The baseline verdict comes from _text_baseline_for, which settles
            # it on the first drawn frame -- see that method for the
            # MatchersAndBooleanOps "highlight me" teleport it exists to stop.
            dy = self._text_baseline_for(mob)
            for sub in mob.submobjects:
                sub._is_text = True
                if dy != 0.0:
                    sub._baseline_dy = dy
                elif hasattr(sub, '_baseline_dy'):
                    del sub._baseline_dy
            if getattr(mob, '_letter_alphas', None) is not None:
                # `parent_offset` used to be dropped here while the
                # `_send_vmobject` branch below it honoured it, so a Text that
                # had been `Write`-animated and was later carried inside a
                # shifted VGroup / LaggedStartMap drew at the group's ORIGIN
                # (its glyphs were projected from unshifted manim coords).
                self._send_text_write(mob, mob._letter_alphas, w, h, a,
                                      parent_offset)
            else:
                self._send_vmobject(mob, a, w, h, parent_offset, 0.0, is_text=is_text)
            return

        # MathTexPart is a VMobject (not VGroup) but holds Text submobjects
        # added by _build_math_part; its children carry the actual glyph data.
        elif isinstance(mob, (VGroup, Group, MathTexPart)):
            effective_alpha = parent_alpha * own_alpha
            if effective_alpha <= 0:
                return
            # DELETED: a block that tried to push the VGroup's stroke_width
            # down onto descendants that carry a stroke colour but no
            # stroke_width of their own ("e.g. AnimatedBoundary's text chars").
            # It has never once executed: the guard read
            #
            #     sc = desc.get_stroke_color()
            #     if sc is not None and sc != '#000000' ...
            #
            # and ManimColor.__eq__ RAISES TypeError against a str (verified:
            # "Cannot compare ManimColor with str"), so the exception was
            # swallowed by the surrounding `except Exception: pass` and
            # `desc.stroke_width` was never written.  It could not be switched
            # on by fixing the comparison either: it mutated the descendant
            # IN PLACE with no restore path, and `stroke_propagated` -- the set
            # that was supposed to remember what to put back -- was written and
            # never read.  Turning it on would leave every descendant of a
            # stroked VGroup permanently wider after the VGroup is gone (the
            # same stale-state trap as the old _grow_scale leak).  Removing it
            # restores the measured baseline: no propagation, no leak.
            vgroup_progress = getattr(mob, '_vulkan_progress', 1.0)
            subs = container_subs(mob)
            num_subs = len(subs)
            about = getattr(mob, '_rotation_about_point', None)
            is_3d = getattr(mob, '_rotation_3d', False)
            vgroup_center = np.array(mob.get_center(), dtype=float)
            try:
                pts = mob.get_points()
                original_center = np.array(pts.mean(axis=0) if len(pts) > 0 else mob.get_center(), dtype=float)
            except Exception:
                original_center = vgroup_center.copy()
            offset = vgroup_center - original_center
            if parent_offset is not None:
                offset = offset + parent_offset
            if is_3d:
                for _i, sub in self._paint_order(mob.family_members_with_points()):
                    if hasattr(sub, 'points') and len(sub.points) > 0:
                        need_gs, need_gp = lend_grow(mob, sub)
                        if getattr(self, '_paint_queue', None) is not None:
                            # Collection pass: this cell has to reach the
                            # queue like every other leaf, or a mobject being
                            # rotated in 3D would paint ahead of its depth.
                            self._send(sub, 0.0, parent_alpha=effective_alpha,
                                       parent_offset=offset,
                                       parent_transforming=getattr(mob, '_transforming', False) or parent_transforming,
                                       parent_is_text=is_text)
                        else:
                            self._send_vmobject(sub, effective_alpha, w, h, offset, 0.0, is_text=is_text)
                        release_grow(getattr(self, '_paint_queue', None), sub,
                                     need_gs, need_gp)
                return
            # A container may carry geometry of its OWN.  ``Axes.plot_line_graph``
            # builds its polyline with ``VGroup.set_points_as_corners`` and adds no
            # children at all, so ``subs`` is empty and the walk below painted
            # NOTHING: HeatDiagramPlot lost its yellow line while its vertex dots
            # (a child VGroup) drew fine.  CE keeps every family member that has
            # points -- ``extract_mobject_family_members(...,
            # only_those_with_points=True)`` runs over ``get_family()``, which
            # starts with the container itself -- so paint the container's own path
            # here, in that same pre-order slot, and only then walk the children.
            #
            # It must not take ``offset``: that is the family bbox centre minus the
            # MEAN of the own points, a shape statistic rather than a coordinate
            # difference, and it measures (-0.525, +0.75) units on HeatDiagramPlot's
            # line -- 71 px left and 101 px up from CE at 1080p.  Same rule as
            # ``test_dot_with_label``: a member's geometry comes from its OWN
            # points.  Children keep the offset they were given; only a pivot
            # rotation (``_rotation_about_point``) displaces this path, exactly as
            # it displaces every child below.
            if isinstance(mob, VMobject) and mob.has_points():
                own_offset = parent_offset
                if about is not None and rot != 0.0:
                    own_center = np.array(mob.get_center(), dtype=float)
                    rel = own_center - np.array(about, dtype=float)
                    _cos, _sin = math.cos(rot), math.sin(rot)
                    _pivot = np.array(about, dtype=float)
                    new_center = _pivot + np.array([rel[0] * _cos - rel[1] * _sin,
                                                    rel[0] * _sin + rel[1] * _cos,
                                                    0.0])
                    _delta = new_center - own_center
                    own_offset = (_delta if parent_offset is None
                                  else _delta + parent_offset)
                if collect is not None:
                    # Collection pass: the own path has to reach the queue like
                    # every other leaf, or it would paint out of frame order.
                    collect.add(
                        depth_key(mob, collect.viewport),
                        lambda: self._send_vmobject(mob, effective_alpha, w, h,
                                                    own_offset, rot,
                                                    is_text=is_text),
                        mob,
                    )
                else:
                    self._send_vmobject(mob, effective_alpha, w, h, own_offset,
                                        rot, is_text=is_text)
            for i, sub in self._paint_order(subs):
                sub_offset = offset
                if about is not None and rot != 0.0:
                    sub_center = np.array(sub.get_center(), dtype=float)
                    rel = sub_center - np.array(about, dtype=float)
                    cos_a = math.cos(rot)
                    sin_a = math.sin(rot)
                    rx = rel[0] * cos_a - rel[1] * sin_a
                    ry = rel[0] * sin_a + rel[1] * cos_a
                    new_center = np.array(about, dtype=float) + np.array([rx, ry, 0.0])
                    sub_offset = sub_offset + (new_center - sub_center)
                if vgroup_progress < 1.0 and num_subs > 1:
                    full_length = (num_subs - 1) * 1.0 + 1
                    value = vgroup_progress * full_length
                    lower = i * 1.0
                    sub_progress = max(0.0, min(1.0, value - lower))
                    sub._vulkan_progress = sub_progress
                    # What *we* put there, so release_split() can take it back
                    # once the container's own animation finishes.
                    sub._vsplit_progress = sub_progress
                sub_rot = rot
                sub_is_text = isinstance(sub, Text) or getattr(sub, '_is_text', False)
                effective_sub_offset = None if sub_is_text else sub_offset
                # Propagate _grow_scale/_grow_point from parent VGroup to submobjects
                # so animations like Indicate that set these on the VGroup correctly
                # scale individual characters/text pieces.
                need_gs, need_gp = lend_grow(mob, sub)
                self._send(sub, sub_rot, parent_alpha=effective_alpha, parent_offset=effective_sub_offset, parent_transforming=getattr(mob, '_transforming', False) or parent_transforming, parent_is_text=is_text)
                release_grow(getattr(self, '_paint_queue', None), sub,
                             need_gs, need_gp)
            return

        # A non-VGroup, non-text container with no points of its own (a
        # ``Graph``, a ``MathTex``) reaches here only while the collection
        # pass is open: it paints none of its own pixels, it merely
        # dispatches to its children (see ``_paint_as_unit``).  Take each
        # child onto the queue individually so every leaf is sorted against
        # the whole frame -- painting the subtree at this node's key grouped
        # all of a polyhedron's cells and edges at the graph's centre, which
        # inverted over 35 members against CE.
        if collect is not None:
            for _i, sub in self._paint_order(container_subs(mob)):
                # This container paints no pixels of its own, but a grow
                # animation still targets it: its children are queued here
                # one by one and must inherit the state (the loan is dropped
                # when the queue flushes).
                need_gs, need_gp = lend_grow(mob, sub)
                self._send(sub, rot, parent_alpha=a, parent_offset=parent_offset,
                           parent_transforming=parent_transforming,
                           parent_is_text=is_text)
                release_grow(collect, sub, need_gs, need_gp)
            return

        # During generic VMobject transforms we default to bezier path rendering.
        # However, axis-aligned quads (Square/Rectangle) render more robustly
        # via the polygon path — unless they're morphing into a curved shape
        # (e.g. square→circle) which produces many vertices and needs bezier
        # smoothing.  Use vertex count to distinguish: 4-vert quad = rotating
        # (test 72, polygon path); >4 verts = morphing (test 3, bezier path).
        if getattr(mob, '_transforming', False) or parent_transforming:
            try:
                vert_count = len(mob.get_vertices()) if hasattr(mob, 'get_vertices') else 0
            except AttributeError:
                vert_count = 0
            # A transforming Square/Rectangle with <=4 anchors is only a true
            # quad — safe to render through the straight-edged _send_polygon —
            # when its edges are genuinely straight (an affine/rotational warp
            # keeps each edge's two bezier control points collinear with the
            # chord between its anchors).  A non-affine point warp such as
            # Homotopy (y += A*sin(x)) bends the control points off the chord,
            # so the top/bottom edges become curves and must be rendered as a
            # bezier path (_send_vmobject).  Collapsing them to the 4 straight
            # corner-to-corner chords makes the square a rigid parallelogram —
            # the "moving top/bottom edges should be flexible" complaint.
            quad_edges_straight = True
            if isinstance(mob, (Square, Rectangle)):
                try:
                    quad_edges_straight = self._edges_are_straight(mob.get_points())
                except Exception:
                    quad_edges_straight = True
            is_quad_morph = (isinstance(mob, (Square, Rectangle)) and vert_count <= 4
                             and not getattr(mob, '_apply_method', False)
                             and quad_edges_straight)
            if not is_quad_morph:
                # FocusOn: route through _send_dot so the dot renders
                # as a proper circle instead of bezier path
                if getattr(mob, '_focus_on_dot', False):
                    self._send_dot(mob, a, w, h)
                    return
                # Arrow: during Rotating/transforms, _send_vmobject only
                # renders the shaft bezier — the tip polygon is a submobject
                # that never gets drawn. Route through _send_arrow instead.
                if isinstance(mob, Arrow):
                    screen_rot = -rot
                    self._dbg_arrow(mob, "transforming", parent_transforming)
                    self._send_arrow(mob, a, w, h, screen_rot, None if is_text else parent_offset)
                    return
                self._send_vmobject(mob, a, w, h, None if is_text else parent_offset, 0.0, is_text=is_text)
                return

        screen_rot = -rot

        # Images have no rgba arrays and four corner points, so the shape
        # senders below cannot express them (they used to fall through to
        # _send_vmobject as an opaque white quad).  Plan 4.4B routes them to the
        # native texture pipeline instead.
        if isinstance(mob, AbstractImageMobject) and not is_text:
            from real_time_manim.render.image import send_image
            if send_image(self, mob, a):
                return

        # For squares/rectangles whose points are already rotated (e.g. by
        # .animate.rotate()), the native rect dispatcher computes from the
        # axis-aligned width/height and would lose the true corner geometry.
        # Route those through the polygon path rather than _send_vmobject so
        # the fill stays a full convex quad instead of going through Bezier
        # tessellation.
        # A RoundedRectangle -- `SurroundingRectangle(corner_radius=...)` is one
        # -- IS a Rectangle subclass, but `get_vertices()` returns the arc
        # *anchors*, not the curved path, so drawing chords between them chamfers
        # every corner (measured: a bright 45-degree cut across the corner where
        # CE's arc leaves the frame background).  Take the polygon path only when
        # the edges really are straight; a rounded one falls through to the point
        # path, which tessellates the arcs.
        _quad_flat = True
        if isinstance(mob, (Square, Rectangle)) and not is_text:
            try:
                _quad_flat = self._edges_are_straight(mob.get_points())
            except Exception:
                _quad_flat = True
            if _quad_flat:
                # An OPEN quad reached here without a tracked-reveal tag must
                # not use the quad senders: `_send_polygon` closes the vertex
                # ring and `_send_square` rebuilds a full quad from
                # `side_length`, so both draw a spurious chord back to the
                # start.  manim's `pointwise_become_partial` run OUTSIDE a
                # ShowPartial -- `AnimatedBoundary`'s per-frame updater -- cuts
                # the anchors so they no longer return to the first, and the
                # closing chord is the diagonal that slashed across it.  A
                # tracked Create/Write cut carries `_vulkan_progress` and keeps
                # the polygon path (which rebuilds the cut prefix OPEN via
                # `_vulkan_points_partial`); only an untracked open path is
                # rerouted to the point path, which strokes the points that are
                # actually there.
                _p = mob.get_points()
                if (len(_p) >= 2
                        and getattr(mob, '_vulkan_progress', None) is None
                        and not (abs(_p[0][0] - _p[-1][0]) < 1e-4
                                 and abs(_p[0][1] - _p[-1][1]) < 1e-4)):
                    _quad_flat = False
        if isinstance(mob, (Square, Rectangle)) and not is_text and _quad_flat:
            drawn = False
            try:
                # Always route axis-aligned quads through the polygon path.
                # This keeps fills solid both for .animate.rotate() (points already
                # rotated) and for Rotating/Rotate (rotation supplied in screen_rot).
                self._send_polygon(
                    mob,
                    mob.get_vertices(),
                    a,
                    rot_override=screen_rot,
                    parent_offset=parent_offset,
                )
                drawn = True
            except Exception:
                drawn = False
            if drawn:
                # A Rectangle may carry submobjects -- manim's SampleSpace turns
                # its divided parts into children -- and manim's family walk
                # paints parent first, then children on top.  Returning here
                # without walking them dropped the divisions entirely (the
                # SampleSpace showed only its base fill; charts d(last) -6.33).
                # A split mixed-z parent (split_mixed_z) painted only itself
                # and had its children queued separately at their own z.
                if not _skip_children:
                    for _i, sub in depth_order(getattr(mob, 'submobjects', ()) or ()):
                        # The quad sender just drew the BORDER with this
                        # mobject's `_grow_scale`; the children (a Rectangle's
                        # `grid_lines`, a SampleSpace's dividers) are drawn by
                        # their own senders, which read the channels off
                        # themselves -- without the loan a channel-only grow
                        # (an RTM animation, Flash, Circumscribe) leaves the
                        # contents at full size inside a scaled border.
                        # manim's own grows need no loan: they scale the points
                        # instead of writing a channel (see `_write_grow`).
                        need_gs, need_gp = lend_grow(mob, sub)
                        self._send(sub, rot, parent_alpha=a, parent_offset=parent_offset,
                                   parent_transforming=parent_transforming,
                                   parent_is_text=is_text)
                        release_grow(getattr(self, '_paint_queue', None), sub,
                                     need_gs, need_gp)
                return

        if isinstance(mob, Square):
            if not _quad_flat:
                # _quad_flat is False when the points are genuinely curved, and
                # the comment above promises those "fall through to the point
                # path, which tessellates the arcs".  They did not: the dispatch
                # below is class-based, so _send_square rebuilt an axis-aligned
                # quad from side_length.  A Square that became a circle
                # (MobjectPositioningAndStyling's ghost) has class Square but
                # 32 bezier points -- it was drawn as the wrong shape and the
                # scene's A collapsed 0.859 -> 0.001.  Send them to the generic
                # renderer instead, which is what the comment promised.
                self._send_vmobject(mob, a, w, h,
                                    None if is_text else parent_offset, rot,
                                    is_text=is_text)
            else:
                self._send_square(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Rectangle):
            if not _quad_flat:
                # same: a RoundedRectangle must reach the bezier tessellator,
                # not _send_rectangle's axis-aligned width/height quad.
                self._send_vmobject(mob, a, w, h,
                                    None if is_text else parent_offset, rot,
                                    is_text=is_text)
            else:
                self._send_rectangle(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Ellipse):
            # `_send_ellipse` rebuilds rx/ry from `mob.width/height`, i.e. from
            # the bounding box of the points that exist, and then windows that
            # by `_vulkan_progress`.  On a path manim's ShowPartial has already
            # cut, that box is the DRAWN PART's -- half way through a Create the
            # true ry is used at half value -- and the window cuts the result a
            # second time.  Measured on CutEllipse: CE a full-height dome, RTM a
            # flat one, mean|d| 2.38 against a 0.75 baseline.  Same rule as the
            # Circle branch below: a shape that is being drawn comes off the
            # point path, which renders the points that are actually there.
            _e_progress = getattr(mob, '_vulkan_progress', 1.0)
            if 0.0 < _e_progress < 1.0:
                self._send_vmobject(mob, a, w, h,
                                    None if is_text else parent_offset, rot,
                                    is_text=is_text)
            else:
                self._send_ellipse(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Dot):
            self._send_dot(mob, a, w, h, parent_offset)
        elif isinstance(mob, Circle):
            # same reasoning as the Arc branch: a partially drawn circle keeps the
            # real radius on the point path (native progress counts segments of a
            # full-radius circle, and on a cut arc `mob.get_center()` is the arc's
            # own bbox centre, not the circle's, so `|get_start() - get_center()|`
            # is not the radius -- `_send_circle` now derives the radius from the
            # on-curve start instead of `mob.width`, which also measured the
            # off-curve handles and inflated a rotating circle by 3.46 %).
            _c_progress = getattr(mob, '_vulkan_progress', 1.0)
            # A Circle inside a 3D scene is not a circle on screen.  At phi=70 a
            # horizontal cap projects to a 60x21 px ELLIPSE, while `_send_circle`
            # draws a full-radius disc from `mob.width` -- measured on
            # SolidPrimitives3D: the Cylinder's two end caps bulged ~21 px past
            # the body at BOTH ends (957 + 883 px of excess fill).  When the
            # camera carries a rotation, hand the mobject to the point path,
            # which projects every point (and its z) individually.
            _vp3d = False
            try:
                from real_time_manim.camera_state import get_viewport
                _vp = get_viewport()
                _vp3d = _vp is not None and _vp.rotation is not None
            except Exception:
                _vp3d = False
            if _vp3d or 0.0 < _c_progress < 1.0:
                self._send_vmobject(mob, a, w, h, None if is_text else parent_offset,
                                    rot, is_text=is_text)
            else:
                self._send_circle(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Arrow):
            self._dbg_arrow(mob, "main", parent_transforming)
            self._send_arrow(mob, a, w, h, screen_rot, parent_offset)
            # `_send_arrow` draws the shaft AND `mob.tip`, which is why Arrow
            # is left out of the family walk below ("Arrow is already fully
            # handled by _send_arrow").  True for `tip`, false for anything
            # else: a LabeledArrow carries a SECOND submobject, its `Label`,
            # that nothing drew at all (report R10-2 -- BracesAndLabels' last
            # row, `flow`: CE 329 px of glyphs, RTM 0; label_probe.py shows
            # `_send(flow)` emitting AddLine x2 + AddBezierPath x1 only).  Walk
            # every submobject except the tip, so report #9's tip stays drawn
            # exactly once.
            _arrow_tip = getattr(mob, "tip", None)
            for _i, _sub in depth_order(mob.submobjects):
                if _sub is _arrow_tip:
                    continue
                self._dbg_arrow(_sub, "walk", parent_transforming)
                # `_send_arrow` lends the grow state to the tip itself; a
                # Label drawn here needs the same loan or it stays full size
                # while the shaft grows.
                need_gs, need_gp = lend_grow(mob, _sub)
                self._send(_sub, rot, parent_alpha=a,
                           parent_offset=parent_offset,
                           parent_transforming=parent_transforming,
                           parent_is_text=is_text)
                release_grow(getattr(self, '_paint_queue', None), _sub,
                             need_gs, need_gp)
        elif isinstance(mob, DashedLine):
            self._send_dashed_line(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Line):
            self._send_line(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, Arc):
            # `_send_arc` reads mob.radius / start_angle -- construction-time
            # attributes that a partial draw (`Create`) or a scale does not
            # update, so an arc that is being drawn or morphed has to go through
            # the point path, which tessellates the actual points and honours
            # `_vulkan_progress` (plan 4.2).
            #
            # A fill-bearing arc has to take that road too: `_send_arc` has only
            # a stroke branch -- it never reads `fill_rgbas` -- and
            # `_stroke_width` turns manim's `stroke_width=0` into 0.0 px, so a
            # fill-only arc submitted NOTHING at all and the element never
            # appeared (report #8: ArcsAndCurves' Sector CE 2626 px vs RTM 0,
            # AnnularSector CE 2124 px vs RTM 0; the missing area equals the
            # shoelace of the points we dropped).  manim builds both with
            # fill_opacity=1 and stroke_width=0, which is the normal way to
            # make a filled wedge.
            _arc_progress = getattr(mob, '_vulkan_progress', 1.0)
            try:
                _arc_fill = float(mob.fill_rgbas[:, 3].max())
            except Exception:
                _arc_fill = 0.0
            if (0.0 < _arc_progress < 1.0 or _arc_fill > 0.0
                    or getattr(mob, '_transforming', False)):
                self._send_vmobject(mob, a, w, h, None if is_text else parent_offset,
                                    rot, is_text=is_text)
            else:
                # `screen_rot`/`parent_offset`: `_send_arc` has always taken
                # both (it projects each control point itself) but the dispatch
                # never passed them, so a rotating or grouped Arc rendered
                # unrotated and untranslated.
                self._send_arc(mob, a, w, h, screen_rot, parent_offset)
        elif isinstance(mob, (Polygon, Polygram)):
            # native AddPolygon *silently drops* any polygon with more than
            # MAX_POLYGON_VERTS (64) vertices (platform.c: `vert_count <=
            # MAX_POLYGON_VERTS`), and its fill loop also indexes edge_lens[64].
            # Axes.get_area() returns an 84-vertex Polygon, so the whole filled
            # area disappeared (GraphAreaPlot lit 8782 vs CE 27905).  Route the
            # big ones through the bezier path, which tessellates and fills up
            # to 1024 segments.
            _verts = mob.get_vertices()
            if _verts is not None and len(_verts) > NATIVE_MAX_POLYGON_VERTS:
                self._send_vmobject(mob, a, w, h, None if is_text else parent_offset,
                                    rot, is_text=is_text)
            else:
                # `parent_offset` / `screen_rot` belong here too: `_send_polygon`
                # reads them off its arguments and the dispatch used to drop
                # both, so a Polygon inside a translated/rotated group was drawn
                # at the group's origin, unrotated.
                self._send_polygon(mob, _verts, a, rot_override=screen_rot,
                                   parent_offset=parent_offset)
        elif isinstance(mob, PMobject):
            # 点云/PMobject：逐点画，别走贝塞尔填充（实测会糊成实心，ink 差 4 倍）
            # `screen_rot`, not `rot`: `_send_point_cloud` rotates in SCREEN
            # space about the projected centre, exactly like `_send_line` /
            # `_send_arc`, so handing it the manim-space angle spun every
            # rotating point cloud the wrong way.
            self._send_point_cloud(mob, a, w, h, rot=screen_rot, parent_offset=parent_offset)
        elif isinstance(mob, Point):
            self._send_point(mob, a, w, h, parent_offset)
        else:
            try:
                pts = mob.get_points()
                if len(pts) >= 2:
                    self._send_vmobject(mob, a, w, h, parent_offset, rot, is_text=is_text)
            except Exception:
                pass

        # Some non-VGroup types (e.g. NumberLine) hold submobjects
        # (tick marks, etc.) that must be rendered separately. Arrow is
        # already fully handled by _send_arrow.  A split mixed-z parent (see
        # split_mixed_z) arrives with _skip_children: its children were queued
        # separately at their own z, so it must paint only itself here.
        if (not _skip_children
                and not isinstance(mob, (Text, VGroup, Group, MathTexPart, Arrow, DashedLine))
                and hasattr(mob, 'submobjects') and mob.submobjects):
            for _i, sub in depth_order(mob.submobjects):
                # The sender above drew `mob` with its `_grow_scale`; the
                # children are drawn by their own senders, so hand the state
                # down (and take it back once painted) or a grow leaves the
                # contents unscaled inside a scaled parent.
                need_gs, need_gp = lend_grow(mob, sub)
                self._send(sub, rot, parent_alpha=a, parent_offset=parent_offset,
                           parent_transforming=parent_transforming, parent_is_text=is_text)
                release_grow(getattr(self, '_paint_queue', None), sub,
                             need_gs, need_gp)

