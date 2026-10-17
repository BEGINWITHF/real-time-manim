"""Regression test: an explicitly BLACK glyph must be painted black.

Report: wiki ``02-Mobject通用/05-样式与颜色`` (``get_match``) -- "「color」消失
被错误显示成了变白".  The sample does::

    w = Text("color", color=WHITE); w[0:2].set_color(RED)
    ...
    w.to_original_color()      # every glyph -> set_color(Text.color) == #000000

so CE paints the word black, i.e. it vanishes off the black stage.  RTM
turned it white: the shape sender's "an all-zero fill is probably just unset"
fallback replaced the measured black with ``get_color()``, and the text
writers then had their own "still black? -> white" rule on top.

Pure-python checks of the two decisions, plus one end-to-end submission check
through a stub DLL.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import RED, WHITE, Text

import real_time_manim.vulkan_bind as vb
from real_time_manim.render.text.vmobject import _black_fill_is_real


class _Recorder:
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


def _fill_colours(calls):
    out = []
    for name, args in calls:
        if name == "AddBezierPath":
            out.append(tuple(round(float(v)) for v in args[6:9]))
        elif name == "AddPolygon":
            out.append(tuple(round(float(v)) for v in args[2:5]))
    return out


def test_white_text_still_paints_white():
    w = Text("color", font_size=38, color=WHITE)
    colours = _fill_colours(_paint([w]))
    assert colours, "nothing submitted for the word"
    assert (255, 255, 255) in colours, colours


def test_to_original_color_paints_black_not_white():
    w = Text("color", font_size=38, color=WHITE)
    w[0:2].set_color(RED)
    w.to_original_color()
    colours = _fill_colours(_paint([w]))
    assert colours, "nothing submitted for the word"
    assert (255, 255, 255) not in colours, (
        "the word was painted white after to_original_color(); CE paints it "
        "black (Text.color is #000000) so it disappears")
    assert (0, 0, 0) in colours, colours


def test_partially_coloured_word_keeps_its_two_red_glyphs():
    w = Text("color", font_size=38, color=WHITE)
    w[0:2].set_color(RED)
    colours = _fill_colours(_paint([w]))
    assert (255, 255, 255) in colours and (252, 98, 85) in colours, colours


def test_black_fill_is_not_treated_as_unset():
    """A measured black fill is real; only "no rgba data" is unset."""
    assert _black_fill_is_real(Text("x")) is False   # glyph data is white
    from manim import BackgroundRectangle
    t = Text("x")
    t.add_background_rectangle()
    assert _black_fill_is_real(t.background_rectangle) is True
    assert isinstance(t.background_rectangle, BackgroundRectangle)
