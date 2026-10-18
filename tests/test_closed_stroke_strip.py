"""A tessellated closed shape must be stroked as ONE line strip, not N quads.

Background
----------
Native's line primitive extends every quad ``half_thick`` past BOTH endpoints
(native/draw/draw_line.c:24-27, ``ex1 = x1 - ux*half_thick``), so when
``_send_ellipse``/``_send_circle`` stroked their outline one ``AddLine`` per
segment, neighbouring segments overlapped in a ``2 * half_thick`` band at
every joint.  Opaque ink hides the overlap; a fading stroke does not: at
alpha < 1 each joint composites twice and paints a brighter seam every 1/48 of
a turn.

Measured on ``BooleanOperations``' ``FadeIn(Ellipse(width=4, height=5,
stroke_width=10))`` (FFT of ring-sampled stroke intensity, analyse5.py):

    fade frame (alpha~0.4)  RTM 48 cyc/rev rel amp 124.9  vs  CE 11.6
    opaque frame            RTM 48 cyc/rev rel amp  10.0

The reported artifact ("circular mobjects render as segmented/dashed pieces
during fade in/out") is exactly that 48-cycle signal.

``_emit_stroke_strip`` now submits the whole outline through ``AddLineStrip``.
That first traded the overlap for its mirror image: the strip builder ended
every quad with a plain perpendicular cap, so the OUTSIDE of each 7.5 deg
turn lost a wedge (~1 px base at half_w = 7) and the border grew a dark tick
at every joint (the follow-up report: "现在圆形的边框出现了一些空隙").
Native mitres joints instead -- both quads of a joint are cut along one
shared line through ``n_in + n_out`` (draw_line.c, ``JointCutCorners``), and
a strip whose last point returns to its first mitres its seam too -- so the
quads tile exactly: no notch, no double blend.

Pure Python -- captures the DLL calls, no GPU work, no ffmpeg.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

try:
    import real_time_manim.vulkan_bind as vb
    from manim import Circle, Ellipse
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


class Recorder(object):
    """Stands in for the native DLL and keeps every submitted call."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


@pytest.fixture(scope="module")
def renderer():
    try:
        r = vb.MLWindow(1920, 1080, hidden=True)
    except Exception as e:  # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield r
    try:
        r.close()
    except Exception:
        pass


def _capture(renderer, send, *args):
    """Run `send` against a recording DLL; return (counts, calls)."""
    rec = Recorder()
    real = renderer.dll
    renderer.dll = rec
    try:
        send(*args)
    finally:
        renderer.dll = real
    counts = {}
    for name, _a in rec.calls:
        counts[name] = counts.get(name, 0) + 1
    return counts, rec.calls


def _strips(calls):
    out = []
    for name, a in calls:
        if name != "AddLineStrip":
            continue
        coords, alphas, n, width, r, g, b, alpha = a
        pts = [(float(coords[i * 2]), float(coords[i * 2 + 1]))
               for i in range(int(n))]
        out.append({"pts": pts, "alphas": alphas, "n": int(n),
                    "width": int(width), "rgb": (int(r), int(g), int(b)),
                    "alpha": float(alpha)})
    return out


def _fading(mob, alpha):
    """A fading-in mobject at the fast path (progress 1.0, flat camera)."""
    mob.set_fill(opacity=0.0)
    mob.set_stroke(opacity=1.0, width=10.0)
    mob._vulkan_progress = 1.0
    return mob, alpha


# --------------------------------------------------------------------------- #
# no per-segment AddLine for a closed outline
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("factory,method", [
    (lambda: Ellipse(width=4.0, height=5.0), "_send_ellipse"),
    (lambda: Circle(radius=1.5), "_send_circle"),
], ids=["Ellipse", "Circle"])
def test_fading_closed_shape_emits_no_per_segment_addline(renderer, factory, method):
    """The headline defect: 48 overlapping AddLine quads per outline.

    Red before the fix: the capture showed `AddLine` == 48 x layers and no
    `AddLineStrip` at all -- the exact 48 seams the FFT measures.
    """
    mob, alpha = _fading(factory(), 0.4)
    counts, calls = _capture(
        renderer, getattr(renderer, method), mob, alpha, 1920, 1080, 0.0, None)
    assert counts.get("AddLine", 0) == 0, (
        "%s still strokes per segment: %d AddLine calls -- each overlapping "
        "neighbour by 2*half_thick, which double-blends into visible seams "
        "while the shape fades" % (method, counts.get("AddLine", 0)))
    assert counts.get("AddLineStrip", 0) > 0, (
        "%s emitted no line strip: %r" % (method, counts))


@pytest.mark.parametrize("factory,method", [
    (lambda: Ellipse(width=4.0, height=5.0), "_send_ellipse"),
    (lambda: Circle(radius=1.5), "_send_circle"),
], ids=["Ellipse", "Circle"])
def test_strip_carries_the_full_outline_at_the_adaptive_count(renderer, factory, method):
    """One closed strip per width layer, tessellated for its on-screen size.

    The count used to be a hard-coded 48 and this test pinned it.  That is what
    made a zoomed-in circle faceted -- the fiddly-bit-of-geometry fix is the
    opposite problem -- so what matters now is that the outline is closed, that
    the count comes from the `curve_segments` rule for the outline's own
    on-screen radius, and that the sagitta it implies stays sub-pixel.
    """
    import math

    from real_time_manim.render.util import curve_segments

    mob, alpha = _fading(factory(), 0.4)
    _counts, calls = _capture(
        renderer, getattr(renderer, method), mob, alpha, 1920, 1080, 0.0, None)
    strips = _strips(calls)
    assert strips, "%s submitted no AddLineStrip" % method
    for s in strips:
        pts = s["pts"]
        assert pts[0] == pytest.approx(pts[-1], abs=1e-3), (
            "%s: the outline strip is not closed (first %r != last %r)"
            % (method, pts[0], pts[-1]))
        cx = sum(p[0] for p in pts[:-1]) / (len(pts) - 1)
        cy = sum(p[1] for p in pts[:-1]) / (len(pts) - 1)
        r_px = max(math.hypot(p[0] - cx, p[1] - cy) for p in pts[:-1])
        segs = s["n"] - 1
        assert segs == curve_segments(r_px), (
            "%s: %d segments for a %.1f px outline, the rule asks for %d"
            % (method, segs, r_px, curve_segments(r_px)))
        sagitta = r_px * (1.0 - math.cos(math.pi / segs))
        assert sagitta < 0.5, (
            "%s: a %.1f px outline drawn with %d segments is faceted "
            "(%.2f px sagitta)" % (method, r_px, segs, sagitta))


# --------------------------------------------------------------------------- #
# the fade alpha still rides the strip
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("factory,method", [
    (lambda: Ellipse(width=4.0, height=5.0), "_send_ellipse"),
    (lambda: Circle(radius=1.5), "_send_circle"),
], ids=["Ellipse", "Circle"])
def test_strip_alpha_carries_the_fade(renderer, factory, method):
    """Straight alpha, same as `_emit_stroke`: colour full, opacity in alpha."""
    mob, alpha = _fading(factory(), 0.4)
    _counts, calls = _capture(
        renderer, getattr(renderer, method), mob, alpha, 1920, 1080, 0.0, None)
    strips = _strips(calls)
    assert strips, "%s submitted no AddLineStrip" % method
    # `_stroke_layers` splits a stroke into a narrow core laid over a wider
    # fractional band, and both cover the core pixels -- so the fade has to
    # come out of the PAIR, never a single layer.  The core's alpha is solved
    # for 1-(1-core)(1-band) == alpha, which is what keeps a translucent
    # stroke at CE's brightness: with the core at the full alpha the two
    # stacked, and a Square/Circle posed statically at stroke_opacity 0.345
    # peaked at 117/255 and 118/255 against CE's 93/255 and 91/255.
    inner = min(strips, key=lambda s: s["width"])
    band = max(strips, key=lambda s: s["width"])
    composite = 1.0 - (1.0 - inner["alpha"]) * (1.0 - band["alpha"])
    assert composite == pytest.approx(0.4, abs=0.02), (
        "%s: the strip layers composite to %.4f, they must carry the 0.4 "
        "fade: %r" % (method, composite, [s["alpha"] for s in strips]))
    expected_rgb = tuple(
        round(float(v) * 255) for v in mob.get_stroke_rgbas()[0][:3])
    assert all(s["rgb"] == expected_rgb for s in strips), (
        "%s: stroke colour must stay full-strength, got %r want %r"
        % (method, [s["rgb"] for s in strips], expected_rgb))


def test_a_long_polygon_is_split_into_native_sized_polygons(renderer):
    """A ring with more than `MAX_POLYGON_VERTS` must still be filled.

    Native's `AddPolygon` returns without emitting anything when handed more
    than 64 vertices, so `RegularPolygon(n=100)` (or any many-point `Polygon`)
    used to have NO fill at all -- silently.  A complete fill is fanned from the
    centroid of the vertices it is given, so consecutive runs sharing their two
    boundary vertices tile the ring; the split is what this pins.
    """
    from manim import RegularPolygon

    mob = RegularPolygon(n=100, radius=2.0, fill_opacity=0.5)
    mob._vulkan_progress = 1.0
    verts = mob.get_vertices()
    assert len(verts) > 64
    _counts, calls = _capture(renderer, renderer._send_polygon, mob, verts, 1.0)
    polys = [a for name, a in calls if name == "AddPolygon"]
    assert len(polys) >= 2, (
        "a %d-vertex ring emitted %d AddPolygon calls; native drops any single "
        "call above 64 vertices" % (len(verts), len(polys)))
    for a in polys:
        n_verts = int(a[9])            # (x, y, r, g, b, ..., vert_count, verts, ...)
        assert 3 <= n_verts <= 64, (n_verts, len(verts))


def test_curve_segments_keeps_the_on_screen_sagitta_constant():
    """The rule behind the fix: identity below the calibration radius, then ∝√r.

    A fixed count is what made a zoomed-in circle faceted; the sagitta (how far
    the polygon's edge falls inside the true arc) is what you actually see, so
    that is what has to stay put as the radius grows.  Keeping the base radius
    at 135 px also means an unzoomed outline draws exactly what it used to.
    """
    import math

    from real_time_manim.render.util import curve_segments

    assert curve_segments(135.0) == 48                 # the old fixed count
    assert curve_segments(1.0) == 48
    assert curve_segments(135.0, base=36) == 36        # native's calibration
    assert curve_segments(540.0, turns=0.25) < curve_segments(540.0)

    for r_px in (270.0, 540.0, 1080.0, 2160.0, 8000.0):
        segs = curve_segments(r_px)
        assert segs > 48, (r_px, segs)
        sagitta = r_px * (1.0 - math.cos(math.pi / segs))
        assert sagitta < 0.4, (r_px, segs, sagitta)


def test_stroke_layers_composite_onto_the_requested_alpha(renderer):
    """The band quad covers the core as well, so the PAIR lands on `alpha`.

    Pure geometry, no mobject.  At alpha == 1 this is the old behaviour
    exactly (the core saturates, which is why every width calibration was
    done opaque and never saw the stacking); below it the core's alpha is
    solved for 1-(1-core)(1-band) == alpha.
    """
    for px in (0.6, 1.0, 2.4, 5.0, 5.7, 12.0, 12.33, 30.5):
        for alpha in (1.0, 0.75, 0.345, 0.05):
            layers = renderer._stroke_layers(px, alpha)
            assert layers, "px=%s produced no layer" % px
            if px < 1.0:
                # one sub-pixel quad: its alpha IS the ink it lays down
                assert layers == [(0, pytest.approx(alpha * px, abs=1e-9))]
                continue
            if len(layers) == 1:
                got = layers[0][1]
            else:
                wide = max(layers, key=lambda l: l[0])
                narrow = min(layers, key=lambda l: l[0])
                got = 1.0 - (1.0 - narrow[1]) * (1.0 - wide[1])
            assert got == pytest.approx(alpha, abs=1e-6), (px, alpha, layers)


def test_alpha_one_outline_is_still_fully_drawn(renderer):
    """Non-regression: at full opacity the whole ring is there, once.

    Guards against a strip fix that dropped the closing segment or truncated
    the point list.
    """
    mob, alpha = _fading(Circle(radius=1.5), 1.0)
    _counts, calls = _capture(
        renderer, renderer._send_circle, mob, alpha, 1920, 1080, 0.0, None)
    strips = _strips(calls)
    assert strips, "a fully opaque circle emitted no strip"
    total = 0.0
    for s in strips:
        pts = s["pts"]
        total = max(total, sum(
            ((pts[i + 1][0] - pts[i][0]) ** 2
             + (pts[i + 1][1] - pts[i][1]) ** 2) ** 0.5
            for i in range(len(pts) - 1)))
    import math
    expect = 2.0 * math.pi * 1.5 * (1080 / 8.0)
    assert total == pytest.approx(expect, rel=0.02), (
        "the closed ring's perimeter is %.1f px, expected ~%.1f px"
        % (total, expect))
