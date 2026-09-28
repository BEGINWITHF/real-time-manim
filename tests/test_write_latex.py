"""Tests for Write/DrawBorderThenFill on LaTeX mobjects.

The core bug this guards against: for a LaTeX mobject (MathTex) the actual
fill/stroke geometry lives on nested point-bearing descendants (the
VMobjectFromSVGPath glyph leaves inside MathTexPart), NOT on the MathTexPart
container.  DrawBorderThenFill used to set fill/stroke opacity only on the
container, so the glyphs stayed fully filled for the whole animation and the
"outline then fill" hand-writing reveal never happened.

These tests assert the animation state transitions (pure Python, no GPU/DLL):
  - during the border phase (alpha < 0.5) every glyph's fill is suppressed to 0
    while progress ramps through the stroke reveal;
  - during the fill phase (alpha >= 0.5) glyph fill fades back in;
  - finish() restores every glyph's original fill opacity.
"""
import sys
from pathlib import Path

import pytest

# Ensure project root is importable so `core.animations.*` resolves.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import real_time_manim.vulkan_bind  # noqa: F401  (registers the MathTex monkeypatch)
from manim import Circle, MathTex, Text
from real_time_manim.animations.write import Write


def glyph_fills(mathtex):
    """Collect get_fill_opacity() across every point-bearing leaf glyph."""
    out = []
    for part in mathtex.submobjects:
        for glyph in part.submobjects:
            out.append(float(glyph.get_fill_opacity()))
    return out


def run_write(mob, alpha):
    """Drive a Write animation on `mob` to the given alpha and return it."""
    w = Write(mob)
    w.begin(0)
    mob._vulkan_progress = 0.0
    w.interpolate(alpha)
    return w


def test_write_latex_border_phase_suppresses_glyph_fill():
    mt = MathTex("x^2 + y^2", font_size=48)
    assert len(mt.submobjects) >= 1
    assert all(g.get_fill_opacity() == pytest.approx(1.0) for g in mt.submobjects[0].submobjects)

    run_write(mt, 0.3)  # alpha 0.3 < border_frac 0.5 -> border phase

    # Every leaf glyph's fill must be hidden during the border phase so the
    # stroke reveal is visible as a hand-writing effect.
    for fill in glyph_fills(mt):
        assert fill == pytest.approx(0.0)


def test_write_latex_fill_phase_fades_fill_back_in():
    mt = MathTex("x^2 + y^2", font_size=48)
    run_write(mt, 0.75)  # alpha 0.75 >= 0.5 -> fill phase

    # Fill should be partially faded in (between 0 and 1), not fully 0.
    fills = glyph_fills(mt)
    assert all(0.0 < f <= 1.0 for f in fills)


def test_write_latex_finish_restores_fill():
    mt = MathTex("x^2 + y^2", font_size=48)
    w = run_write(mt, 1.0)
    w.finish()

    assert all(f == pytest.approx(1.0) for f in glyph_fills(mt))


def test_write_latex_glyphs_receive_progress_during_border():
    mt = MathTex("x^2 + y^2", font_size=48)
    run_write(mt, 0.15)

    # During the border phase the MathTexPart container carries a partial
    # progress value (the renderer's _send VGroup branch distributes that to
    # the individual glyph leaves). It must not be full at a partial alpha.
    progresses = [
        getattr(part, "_vulkan_progress", None)
        for part in mt.submobjects
        if hasattr(part, "_vulkan_progress")
    ]
    assert progresses, "expected MathTexPart(s) to receive _vulkan_progress"
    assert all(p is not None and 0.0 < p < 1.0 for p in progresses)


def test_write_plain_vmobject_unchanged():
    """Non-LaTeX VMobjects must keep their original behaviour (fill=0 Circle)."""
    c = Circle(radius=1.0)
    assert c.get_fill_opacity() == pytest.approx(0.0)

    w = run_write(c, 0.3)  # border phase
    assert c.get_fill_opacity() == pytest.approx(0.0)

    w.interpolate(1.0)
    w.finish()
    assert c.get_fill_opacity() == pytest.approx(0.0)


def test_write_text_unchanged():
    """Write on plain Text must still produce per-letter fill progression."""
    t = Text("Hello", font_size=48)
    run_write(t, 0.5)

    alphas = getattr(t, "_letter_alphas", None)
    assert alphas is not None
    assert len(alphas) == len(t.submobjects)
    # Letters reveal in order: first letter ahead of the last.
    assert alphas[0] >= alphas[len(t.submobjects) - 1]


def _render_dll_call_counts(mathtex, alpha):
    """Render a MathTex at the given Write alpha and capture DLL draw calls.

    Returns (bezier, linestrip, max_stroke_vertex_alpha).  This needs the
    Vulkan DLL, so it is skipped automatically if the renderer can't be
    constructed (CI/headless fallback).
    """
    import real_time_manim.vulkan_bind as vb

    renderer = vb.MLWindow(400, 200)
    counters = {"bezier": 0, "linestrip": 0, "max_vertex_alpha": 0.0}

    def _bez(*_a):
        counters["bezier"] += 1
        return 0

    def _ls(*args):
        counters["linestrip"] += 1
        # args: points, per-vertex alphas, num, width, r, g, b, alpha
        alphas = args[1]
        for v in alphas:
            if v > counters["max_vertex_alpha"]:
                counters["max_vertex_alpha"] = v
        return 0

    renderer.dll.AddBezierPath = _bez
    renderer.dll.AddLineStrip = _ls
    try:
        run_write(mathtex, alpha)
        renderer._send(mathtex)
    finally:
        renderer.close()
    return (counters["bezier"], counters["linestrip"], counters["max_vertex_alpha"])


def test_write_latex_draws_progressive_stroke_during_border():
    """During the border phase a latex glyph must draw a progressive stroke.

    LaTeX glyphs are filled shapes with no stroke; without a synthesized stroke
    the native fill pops in whole -> Write looks like a fade-in.  This test
    asserts the renderer emits AddLineStrip (progressive outline) calls during
    the border phase with a fully-opaque stroke, and that the stroke then fades
    out (via per-vertex alpha, staying the glyph color) as the fill fades in —
    never leaving a dip where neither stroke nor fill is shown.
    """
    try:
        import real_time_manim.vulkan_bind as vb  # noqa: F401 (import guard)
    except Exception as e:
        pytest.skip(f"Vulkan DLL unavailable: {e}")

    border_bez, border_ls, border_sa = _render_dll_call_counts(
        MathTex("x^2 + y^2", font_size=48), 0.3)
    mid_bez, mid_ls, mid_sa = _render_dll_call_counts(
        MathTex("x^2 + y^2", font_size=48), 0.65)
    end_bez, end_ls, end_sa = _render_dll_call_counts(
        MathTex("x^2 + y^2", font_size=48), 1.0)

    # Border phase (alpha 0.3 < 0.5): progressive outline stroke, fully opaque.
    assert border_ls > 0, f"expected progressive stroke calls during border, got {border_ls}"
    assert border_sa >= 0.99, f"expected full-opacity stroke during border, got {border_sa}"

    # Mid fill phase (alpha 0.65): stroke still present but fading out.
    assert mid_ls > 0, "expected fading stroke calls during fill phase"
    assert 0.0 < mid_sa < 1.0, f"expected partially-faded stroke, got {mid_sa}"

    # End (alpha 1.0): stroke fully faded (alpha 0), fill complete.
    assert end_sa <= 0.01, f"expected stroke fully faded at end, got {end_sa}"

    # Both phases still draw the glyph fills/beziers.
    assert border_bez > 0 and mid_bez > 0 and end_bez > 0
