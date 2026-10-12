"""A tessellated closed shape must be stroked as ONE line strip, not N quads.

Background
----------
Native's line primitive extends every quad ``half_thick`` past BOTH endpoints
(native/draw/draw_line.c:24-27, ``ex1 = x1 - ux*half_thick``), so when
``_send_ellipse``/``_send_circle`` stroked their 48-gon one ``AddLine`` per
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
def test_strip_carries_the_full_48_segment_outline(renderer, factory, method):
    """One strip per width layer, 48 segments (49 points), closed loop."""
    mob, alpha = _fading(factory(), 0.4)
    _counts, calls = _capture(
        renderer, getattr(renderer, method), mob, alpha, 1920, 1080, 0.0, None)
    strips = _strips(calls)
    assert strips, "%s submitted no AddLineStrip" % method
    for s in strips:
        assert s["n"] == 49, (
            "%s: strip has %d points, expected 49 (48 segments + close)"
            % (method, s["n"]))
        assert s["pts"][0] == pytest.approx(s["pts"][-1], abs=1e-3), (
            "%s: the outline strip is not closed (first %r != last %r)"
            % (method, s["pts"][0], s["pts"][-1]))


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
