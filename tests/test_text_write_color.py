"""A glyph drawn through the Write path keeps ITS OWN colour.

Report: ``06_text.PlainTextAndMarkup`` rendered the whole ``styled`` line pure
white -- the ``t2c`` teal of "colourful" was gone from the first frame, and the
closing ``styled.animate.set_color(YELLOW)`` never showed (CE ends yellow).

`Write` sets ``_letter_alphas`` on the Text, and that flag is still set
afterwards, so `_send_impl` keeps routing the mobject through
`_send_text_write` for the rest of the scene.  That writer took its colour from
``mob.get_color()`` -- the container's own ``color`` attribute, which manim
leaves at ``#000000`` for a ``Text`` and only updates when ``set_color`` is
called *on the container* (``_MethodAnimation.finish``).  A colour that manim
animates lives in the glyphs' ``fill_rgbas`` instead, so reading the container
painted every glyph white.  Measured on the rendered clip, 1920x1080, the
``Manim is colourful`` row:

    RTM: 0 saturated pixels   CE: 5295 saturated pixels (teal), 13457 (yellow)

`_glyph_rgb` reads the glyph's own rgba stops, falling back to the container
colour only when the glyph carries none.

Pure Python: captures the DLL calls, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

try:
    import real_time_manim.vulkan_bind as vb
    from manim import TEAL, YELLOW, Text, Write
    from real_time_manim.render_hooks import install_hooks
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


class _Recorder(object):
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


def _capture(mob):
    renderer = vb.MLWindow(854, 480)
    rec = _Recorder()
    real_dll = renderer.dll
    renderer.dll = rec
    try:
        renderer._send(mob)
    finally:
        renderer.dll = real_dll
        renderer.close()
    return rec.calls


def _written(text):
    """Pose ``text`` exactly as the scene leaves it after ``Write(text)``."""
    anim = Write(text, run_time=1.0)
    anim.begin()
    install_hooks(anim)
    anim.interpolate(1.0)
    assert getattr(text, "_letter_alphas", None) is not None, (
        "the Write hook did not arm _letter_alphas; the test is not "
        " exercising the writer it claims to")
    return text


def _expected_rgb(glyph, default=(255, 255, 255)):
    """The glyph colour the writer is contracted to emit (independent calc)."""
    for getter in ("get_fill_rgbas", "get_stroke_rgbas"):
        stops = list(getattr(glyph, getter)())
        if not stops:
            continue
        n = float(len(stops))
        rgb = [sum(float(s[k]) for s in stops) / n for k in range(3)]
        if any(v != 0.0 for v in rgb):
            return tuple(int(round(v * 255)) for v in rgb)
    return default


def _fill_args(calls):
    return [a for n, a in calls if n == "AddBezierPath"]


def _scene_text():
    """The scene's styled line: one bold word, one teal sub-string."""
    return Text("Manim is colourful", font_size=42, t2c={"colourful": TEAL})


def test_written_glyphs_are_painted_with_their_own_colour():
    """t2c survives the Write: the coloured glyphs must not come out white."""
    text = _written(_scene_text())
    glyphs = list(text.submobjects)
    calls = _capture(text)
    bez = _fill_args(calls)
    assert len(bez) == len(glyphs), (
        "%d glyph paths for %d glyphs" % (len(bez), len(glyphs)))

    painted_teal = 0
    for i, args in enumerate(bez):
        want = _expected_rgb(glyphs[i])
        got = (int(args[6]), int(args[7]), int(args[8]))
        assert got == want, (
            "glyph %d: emitted fill rgb %r but its own fill_rgbas say %r -- "
            "the Write writer takes the colour from `mob.get_color()`, which "
            "is #000000 for a Text and falls back to white" % (i, got, want))
        if want != (255, 255, 255):
            painted_teal += 1
    assert painted_teal > 0, (
        "the t2c sub-string produced no differently-coloured glyph: the "
        "scene text lost its markup colour")


def test_written_glyphs_follow_an_animated_colour():
    """The closing ``.animate.set_color`` must reach a written Text.

    manim writes the interpolated colour into the glyphs' ``fill_rgbas`` only;
    the container's own ``color`` attribute stays ``#000000`` until
    ``_MethodAnimation.finish``, so a writer keyed on ``get_color()`` renders
    white for the whole animation.
    """
    text = _scene_text()
    _written(text)
    anim = text.animate.set_color(YELLOW).build()
    anim.begin()
    anim.interpolate(0.5)

    glyphs = list(text.submobjects)
    bez = _fill_args(_capture(text))
    assert len(bez) == len(glyphs), (
        "%d glyph paths for %d glyphs" % (len(bez), len(glyphs)))

    for i, args in enumerate(bez):
        want = _expected_rgb(glyphs[i])
        got = (int(args[6]), int(args[7]), int(args[8]))
        assert got == want, (
            "glyph %d at alpha 0.5: emitted %r, its fill_rgbas say %r"
            % (i, got, want))
    # ...and the line really is tinted, i.e. not the old all-white fallback.
    blues = [int(a[8]) for a in bez]
    assert max(blues) < 255, (
        "every glyph is still pure white after set_color(YELLOW) at alpha 0.5: %r"
        % (blues,))
