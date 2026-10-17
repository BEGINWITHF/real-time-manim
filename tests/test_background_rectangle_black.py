"""Regression test: ``add_background_rectangle`` must paint a BLACK plate.

Report: wiki ``02-Mobject通用/05-样式与颜色`` -- "lable应为黑底".  The label's
backing plate came out WHITE-ish (RTM (223,238,217) against CE (32,47,23)),
so the "READABLE" caption sat on a bright block instead of the dark one the
coloured bars need.

Both shape senders treat an all-zero ``fill_rgbas`` as ambiguous -- manim
leaves it at zeros for a ``VMobject`` whose fill colour was never set -- and
resolve it through ``get_color()``.  ``BackgroundRectangle`` is the exception:
its black IS the colour (``set_style`` hard-codes ``fill_color=BLACK`` and the
caller's ``opacity`` rides ``fill_opacity``), while ``get_color()`` hands back
the colour of the mobject it backs -- here the white ``Text``.

Drives a real hidden ``MLWindow`` against a stub DLL and checks the colour
that reaches the native side, exactly like the render probes do.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import BLACK, BLUE, UP, WHITE, Text

import real_time_manim.vulkan_bind as vb


class _Recorder:
    """Stands in for the native DLL and keeps every submitted call."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


def _paint(mobjects):
    from manim import Scene
    scene = Scene()
    scene.mobjects = list(mobjects)
    win = vb.MLWindow(320, 180, hidden=True)
    rec = _Recorder()
    real = win.dll
    win.dll = rec
    try:
        win.sync(scene)
    finally:
        win.dll = real
    return rec.calls


def _fills(calls):
    """(colour, alpha) of every filled AddBezierPath submission.

    Native ``AddBezierPath(coords, n, r, g, b, a, fr, fg, fb, fa)``: the first
    colour pair is the STROKE (white at alpha 0 for a fill-only shape), the
    second one is the FILL.
    """
    out = []
    for name, args in calls:
        if name != "AddBezierPath":
            continue
        out.append((tuple(round(float(v)) for v in args[6:9]),
                    float(args[9])))
    return out


def test_background_rectangle_reaches_native_as_black():
    txt = Text("READABLE", font_size=44, color=WHITE).shift(UP * 1.6)
    txt.add_background_rectangle(color=BLACK, opacity=0.75)
    fills = _fills(_paint([txt]))
    assert fills, "nothing was submitted for the label"
    colours = {c for c, _alpha in fills}
    assert (0, 0, 0) in colours, (
        f"the backing plate was painted {colours} -- an all-black fill_rgbas "
        "was mistaken for 'unset' and replaced by get_color() (the text's own "
        "colour)")
    plate = [(c, a) for c, a in fills if c == (0, 0, 0)]
    assert all(0.7 < a <= 1.0 for _c, a in plate), plate


def test_background_rectangle_of_a_coloured_mobject_stays_black():
    """Same, with a non-white owner: the plate must not take ITS colour."""
    txt = Text("READABLE", font_size=44, color=BLUE)
    txt.add_background_rectangle(color=BLACK, opacity=0.7)
    fills = _fills(_paint([txt]))
    colours = {c for c, _a in fills}
    assert (0, 0, 0) in colours, colours


def test_the_black_fill_helper_only_excepts_background_rectangles():
    """Non-regression: a genuinely unset fill still uses the fallback."""
    from real_time_manim.render.text.vmobject import _black_fill_is_real
    txt = Text("x")
    txt.add_background_rectangle()
    assert _black_fill_is_real(txt.background_rectangle) is True
    from manim import Circle
    assert _black_fill_is_real(Circle()) is False
