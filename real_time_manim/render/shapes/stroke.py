"""Colour and stroke helpers shared by every shape sender.

Fill/stroke colour extraction, the stroke-width ladder and the two
`_emit_stroke*` primitives every sender builds its quads from."""

import ctypes
import math
from real_time_manim.render.util import rotate_point, get_fill_rgb, get_fill_rgb_raw, get_stroke_rgb, get_stroke_w, shaded_fill_rgb


class StrokeMixin:

    def _color(self, mob, alpha=1.0):
        return get_fill_rgb(mob, alpha)

    def _fill_color(self, mob):
        return get_fill_rgb_raw(mob)

    def _fill_color_lit(self, mob):
        """`_fill_color` with manim's per-face 3D light shading (see vulkan_util)."""
        lit = shaded_fill_rgb(mob)
        return self._fill_color(mob) if lit is None else lit

    def _stroke_color(self, mob):
        return get_stroke_rgb(mob)

    @staticmethod
    def _visible_frame_height():
        """How many manim units the camera is currently showing vertically.

        Any *size* written in manim units (a stroke width, a Dot's radius) has to
        be converted with the pixels-per-unit of the frame that is actually on
        screen.  Positions already take that route -- ``manim_to_screen`` ->
        ``Viewport.project`` scales by the visible frame height -- so a size that
        assumed the default 8-unit frame drew a mobject that did not follow a
        zooming camera while its own position did.

        Measured on ``FollowingGraphCamera`` (``camera.frame.animate.scale(0.5)``,
        frame height 8 -> 4): manim CE doubles every dot on screen, 22 px ->
        44 px at 1080p, growing over the whole zoom-in and shrinking again over
        ``Restore``; with the default 8 RTM kept the disc at a constant 22 px for
        the entire zoom-in and the whole restore and snapped between the two
        sizes at the play boundaries.

        No published viewport means a plain ``Scene`` with the default fixed
        frame, so non-camera scenes render exactly as before.
        """
        try:
            from real_time_manim.camera_state import get_viewport, DEFAULT_FRAME_HEIGHT
        except Exception:                          # pragma: no cover - no camera_state
            return 8.0
        try:
            viewport = get_viewport()
            if viewport is not None:
                return float(viewport.height) or 8.0
        except Exception:                          # pragma: no cover - defensive
            pass
        return DEFAULT_FRAME_HEIGHT

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
        return sw_manim * 0.01 * (h / self._visible_frame_height())

    @staticmethod
    def _stroke_layers(px, alpha):
        """(native width, alpha) pairs that composite to exactly `px` of ink.

        Native renders a quad of ``width + 1`` px (draw_line.c:
        ``half_thick = thick * 0.5f + 0.5f``) and native widths are integers,
        so an exact sub-pixel width needs an integer core plus symmetric
        fractional edges: a ``core``-wide quad at full alpha laid over a
        ``core + 1``-wide quad at alpha ``frac`` composites to
        ``floor(px) + frac = px``.

        Passing ``round(px)`` straight through instead drew
        ``round(px) + 1`` px -- 2 px where manim draws 1.2 px for the default
        stroke_width=2 at 480p, a 67% overdraw.  Measured with an independent
        probe (tests/test_stroke_width.py is the fast version, stroke_probe.py
        the on-video one):

            BracesAndLabels            ink x1.27  lit>55 x1.63  missing  87 px
            ApplyTransformAnimations   ink x1.23  lit>55 x1.68  missing   0 px

        ``missing = 0`` means CE's ink is a strict subset of RTM's: the same
        strokes, drawn wider, never in the wrong place -- which is compare_auto's
        ``width`` bucket.  ``de309df`` had already moved ``_send_line`` and
        ``_send_arrow`` over to this rule; the closed-shape senders had not.

        A single quad at a compensating alpha is NOT equivalent: it covers the
        next integer width up and every one of those pixels crosses an ink
        threshold (measured: ``ThreeDRotationProbe``'s excess coverage jumping
        0.054 -> 0.192, all of it within 2 px of CE's strokes).
        """
        px = float(px)
        if px <= 0:
            return []
        core = int(math.floor(px + 1e-6))
        frac = px - core
        if core < 1:
            # thinner than one pixel: a single 1 px quad at the exact alpha
            return [(0, alpha * min(1.0, px))]
        layers = []
        if frac > 0.01:
            # The band quad is `core` native px, which renders `core + 1` -- so
            # it covers the inner core as well, and at alpha < 1 the two stack:
            # an inner pixel comes out 1-(1-a)(1-a*frac), i.e. `frac * a` above
            # the target.  Opaque strokes never showed it (the inner layer is
            # 1.0 and saturates), which is why every width calibration above was
            # done without it.  Measured once the fades stopped doubling: a
            # Square and a Circle posed statically at stroke_opacity 0.345 peak
            # at 117/255 and 118/255 where CE has 93/255 and 91/255 (x1.26,
            # x1.29), and a fading DashedLine at 0.363 against CE's 0.266.
            # Solving the inner layer for the composite to land on `alpha`
            # leaves alpha == 1 exactly as it was: 1 - 0/(1-frac) == 1.
            band = alpha * min(1.0, frac)
            inner = 1.0 - (1.0 - alpha) / max(1e-6, 1.0 - band)
            layers.append((core, band))
            layers.append((core - 1, max(0.0, min(1.0, inner))))
            return layers
        layers.append((core - 1, alpha))
        return layers

    def _emit_stroke(self, x1, y1, x2, y2, px, r, g, b, alpha):
        """Draw one straight stroke of exactly ``px`` pixels of ink.

        Layers are pushed in the order ``_stroke_layers`` returns them, so the
        opaque core lands on top of the fractional edge (the order the coverage
        above assumes).
        """
        for _w, _a in self._stroke_layers(px, alpha):
            self.dll.AddLine(x1, y1, x2, y2, _w, r, g, b, _a)

    def _emit_stroke_strip(self, pts, px, r, g, b, alpha):
        """Stroke the screen-space polyline ``pts`` (x0,y0,x1,y1,...) as ONE
        native line strip per width layer.

        A tessellated curve must not be stroked as a run of ``_emit_stroke``
        segments: native extends every line quad ``half_thick`` past BOTH
        endpoints (draw_line.c:24-27, ``ex1 = x1 - ux*half_thick``), so
        neighbouring segments overlap in a ``2 * half_thick`` band at every
        joint.  Where the ink is opaque that overlap is invisible -- but while
        a mobject fades, alpha < 1 makes each joint composite twice, painting
        a brighter seam every 1/N of a turn.  Measured on ``BooleanOperations``'
        fading ``Ellipse(width=4, height=5, stroke_width=10)`` (FFT of the
        stroke intensity sampled around the ring, analyse5.py):

            fade frame (alpha~0.4)  RTM 48 cyc/rev rel amp 124.9  vs CE 11.6
            opaque frame            RTM 48 cyc/rev rel amp  10.0

        -- exactly the 48 segments of the fixed tessellation, and gone at full
        opacity because ``a + a*(1-a) == a`` only when ``a == 1``.

        ``AddLineStrip`` mitres every joint: native cuts both quads of a
        joint along ONE shared line (draw_line.c, ``JointCutCorners``), so
        consecutive quads tile exactly -- no double-composited wedge while
        fading and, unlike the plain perpendicular cap this used to leave,
        no wedge notch on the outside of the turn either (that notch showed
        up as a dark tick at each of the 48 joints; a closed strip's seam is
        mitred the same way).  The strip is still pushed at its submission
        position (draw_line.c:93), so paint order against the fill and
        neighbouring mobjects is unchanged.

        ``px`` is manim's target width in pixels; the core/fractional layer
        decomposition of :meth:`_stroke_layers` is applied per strip, in the
        same order :meth:`_emit_stroke` pushes its layers.
        """
        if len(pts) < 4:
            return
        n = len(pts) // 2
        coords = (ctypes.c_float * len(pts))(*[float(v) for v in pts])
        for _w, _a in self._stroke_layers(px, alpha):
            self.dll.AddLineStrip(coords, None, n, _w, r, g, b, _a)

    def _rotate_point(self, x, y, cx, cy, angle):
        return rotate_point(x, y, cx, cy, angle)
