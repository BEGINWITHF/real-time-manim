"""Phase 2 -- graphics & text mobjects the wiki marked ⚠️.

These mostly fall through to RTM's generic bezier/tessellation sender. The
question per class is simply: does it render non-blank through the real Vulkan
pipeline (not crash, not invisible)?  A few are asserted to actually animate.

Run standalone:  python -X utf8 tests/test_phase2_graphics.py
Or with pytest:  pytest tests/test_phase2_graphics.py -q
"""
import os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest
from tools.rtm_verify import window_available, verify

if not window_available():                              # pragma: no cover
    pytest.skip("Vulkan window unavailable", allow_module_level=True)

import numpy as np
from manim import (
    Scene, VGroup, Square, Circle, Triangle, Dot, Line, Arrow, Polygon,
    Angle, SurroundingRectangle, LabeledArrow, LabeledLine,
    Brace, BraceLabel, Matrix, Table, DecimalNumber, Integer, Variable,
    Code, MarkupText, Paragraph, Star, Title, BulletedList,
    Union, Difference, Intersection, Exclusion,
    NumberLine, Axes, NumberPlane, ComplexPlane, PolarPlane, ThreeDAxes,
    BarChart, SampleSpace, Graph, DiGraph, ArrowVectorField, StreamLines,
    LogBase, LinearBase,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI, BLUE, RED, GREEN, YELLOW, WHITE, BLACK,
    Text, MathTex, Tex, Create, FadeIn, Write, Wait,
)


def _mk(build):
    """Wrap a build(scene, win) callable into a Scene and verify-render it."""
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            build(self, win)
            win.close()
    return S


def _run(name, build, expect_anim=False):
    S = _mk(build)
    info = verify(S, name)
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    if expect_anim:
        assert not info["static"], info
    return info


# --------------------------------------------------------------------------
# 04-图形与文本 : angles / labels / braces / matrix / table / numbers
# --------------------------------------------------------------------------

def test_angle():
    def build(sc, win):
        l1 = Line(ORIGIN, RIGHT * 2)
        l2 = Line(ORIGIN, 2 * (np.cos(PI / 3) * RIGHT + np.sin(PI / 3) * UP))
        a = Angle(l1, l2, radius=0.6)
        win.play(Create(a), run_time=0.6)
    _run("g_angle", build, expect_anim=True)


def test_surrounding_rectangle():
    def build(sc, win):
        sq = Square().set_fill(BLUE, 0.5)
        sr = SurroundingRectangle(sq, color=RED, buff=0.2)
        win.play(Create(sq), run_time=0.3)
        win.play(Create(sr), run_time=0.3)
    _run("g_surrounding_rectangle", build, expect_anim=True)


def test_labeled_arrow():
    # NB: passing points positionally after the label trips an upstream manim
    # 0.21 bug (labeled.py:93 `label_config or {}` on a numpy array) before RTM
    # is involved; the start=/end= kwargs form constructs fine.
    def build(sc, win):
        la = LabeledArrow("label", start=ORIGIN, end=RIGHT * 2)
        win.play(FadeIn(la), run_time=0.5)
    _run("g_labeled_arrow", build, expect_anim=True)


def test_labeled_line():
    def build(sc, win):
        ll = LabeledLine("a", start=ORIGIN, end=RIGHT * 2, buff=0.2)
        win.play(FadeIn(ll), run_time=0.5)
    _run("g_labeled_line", build, expect_anim=True)


def test_brace():
    def build(sc, win):
        sq = Square()
        b = Brace(sq, direction=DOWN)
        bl = b.get_text("x")
        win.play(FadeIn(sq), run_time=0.2)
        win.play(Create(b), run_time=0.3)
        win.play(FadeIn(bl), run_time=0.2)
    _run("g_brace", build, expect_anim=True)


def test_matrix():
    def build(sc, win):
        m = Matrix([[1, 2], [3, 4]])
        win.play(Create(m), run_time=0.6)
    _run("g_matrix", build, expect_anim=True)


def test_table():
    def build(sc, win):
        t = Table([["a", "b"], ["c", "d"]])
        win.play(FadeIn(t), run_time=0.5)
    _run("g_table", build, expect_anim=True)


def test_decimal_number():
    def build(sc, win):
        d = DecimalNumber(3.14, num_decimal_places=2)
        win.play(FadeIn(d), run_time=0.4)
    _run("g_decimal_number", build, expect_anim=True)


def test_integer():
    def build(sc, win):
        i = Integer(42)
        win.play(FadeIn(i), run_time=0.4)
    _run("g_integer", build, expect_anim=True)


def test_variable():
    def build(sc, win):
        v = Variable(3, "x", num_decimal_places=0)
        win.play(FadeIn(v), run_time=0.4)
    _run("g_variable", build, expect_anim=True)


def test_code_block():
    def build(sc, win):
        c = Code(code_string="x = 1\ny = 2", language="python")
        win.play(FadeIn(c), run_time=0.4)
    _run("g_code", build, expect_anim=True)


def test_markup_text():
    def build(sc, win):
        mt = MarkupText('hello <i>world</i>')
        win.play(Write(mt), run_time=0.5)
    _run("g_markup_text", build, expect_anim=True)


def test_paragraph():
    def build(sc, win):
        p = Paragraph("line one", "line two", "line three", alignment="center")
        win.play(FadeIn(p), run_time=0.4)
    _run("g_paragraph", build, expect_anim=True)


def test_star():
    def build(sc, win):
        s = Star(n=5, outer_radius=1.0, inner_radius=0.5).set_fill(YELLOW, 0.8)
        win.play(Create(s), run_time=0.5)
    _run("g_star", build, expect_anim=True)


def test_title():
    def build(sc, win):
        t = Title("My Title")
        win.play(FadeIn(t), run_time=0.4)
    _run("g_title", build, expect_anim=True)


def test_bulleted_list():
    def build(sc, win):
        bl = BulletedList("item a", "item b", "item c")
        win.play(FadeIn(bl), run_time=0.5)
    _run("g_bulleted_list", build, expect_anim=True)


def test_boolean_ops():
    def build(sc, win):
        a = Circle(radius=1.0).set_fill(RED, 0.5).shift(LEFT * 0.5)
        b = Square(side_length=1.6).set_fill(BLUE, 0.5).shift(RIGHT * 0.5)
        u = Union(a, b)
        win.play(FadeIn(a), FadeIn(b), run_time=0.2)
        win.play(FadeIn(u), run_time=0.4)
    _run("g_boolean_union", build, expect_anim=True)


# --------------------------------------------------------------------------
# 05-坐标系与图表 : numberline / axes / planes / charts
# --------------------------------------------------------------------------

def test_number_line():
    def build(sc, win):
        nl = NumberLine(x_range=[-3, 3, 1], length=6)
        win.play(Create(nl), run_time=0.6)
    _run("c_number_line", build, expect_anim=True)


def test_axes():
    def build(sc, win):
        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 2, 1], x_length=6, y_length=4)
        win.play(Create(ax), run_time=0.6)
    _run("c_axes", build, expect_anim=True)


def test_axes_plot():
    def build(sc, win):
        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 2, 1], x_length=6, y_length=4)
        graph = ax.plot(lambda x: x ** 2, x_range=[-2, 2], color=GREEN)
        win.play(Create(ax), run_time=0.3)
        win.play(Create(graph), run_time=0.5)
    _run("c_axes_plot", build, expect_anim=True)


def test_number_plane():
    def build(sc, win):
        np_ = NumberPlane(x_range=[-4, 4], y_range=[-3, 3])
        win.play(Create(np_), run_time=0.6)
    _run("c_number_plane", build, expect_anim=True)


def test_complex_plane():
    def build(sc, win):
        cp = ComplexPlane(x_range=[-3, 3], y_range=[-3, 3])
        win.play(Create(cp), run_time=0.6)
    _run("c_complex_plane", build, expect_anim=True)


def test_polar_plane():
    def build(sc, win):
        pp = PolarPlane()
        win.play(Create(pp), run_time=0.6)
    _run("c_polar_plane", build, expect_anim=True)


def test_three_d_axes():
    def build(sc, win):
        ax = ThreeDAxes(x_range=[-3, 3], y_range=[-3, 3], z_range=[-3, 3])
        win.play(Create(ax), run_time=0.6)
    _run("c_three_d_axes", build, expect_anim=True)


def test_bar_chart():
    def build(sc, win):
        bc = BarChart(values=[3, 5, 2, 7], y_range=[0, 8], x_length=5, y_length=3)
        win.play(Create(bc), run_time=0.6)
    _run("c_bar_chart", build, expect_anim=True)


def test_sample_space():
    def build(sc, win):
        ss = SampleSpace(0.6)
        win.play(FadeIn(ss), run_time=0.5)
    _run("c_sample_space", build, expect_anim=True)


def test_graph():
    def build(sc, win):
        g = Graph([1, 2, 3, 4], [(1, 2), (2, 3), (3, 4), (4, 1)], layout="circular")
        win.play(FadeIn(g), run_time=0.6)
    _run("g_graph", build, expect_anim=True)


def test_digraph():
    def build(sc, win):
        g = DiGraph([1, 2, 3], [(1, 2), (2, 3), (3, 1)], layout="circular")
        win.play(FadeIn(g), run_time=0.6)
    _run("g_digraph", build, expect_anim=True)


def test_arrow_vector_field():
    def build(sc, win):
        vf = ArrowVectorField(lambda p: np.array([-p[1], p[0], 0.0]))
        win.play(FadeIn(vf), run_time=0.6)
    _run("g_vector_field", build, expect_anim=True)


def test_stream_lines():
    def build(sc, win):
        sl = StreamLines(lambda p: np.array([-p[1], p[0], 0.0]),
                         x_range=[-3, 3], y_range=[-2, 2])
        win.play(FadeIn(sl), run_time=0.6)
    _run("g_stream_lines", build, expect_anim=True)


# --------------------------------------------------------------------------
# 09b / 15 : tex fragments, image/svg
# --------------------------------------------------------------------------

def test_math_tex_fragments():
    def build(sc, win):
        mt = MathTex(r"x^2", r"+", r"y^2", r"=", r"r^2")
        win.play(Write(mt), run_time=0.6)
    _run("g_math_tex_fragments", build, expect_anim=True)


def test_svg_mobject():
    def build(sc, win):
        import tempfile
        from manim import SVGMobject
        svg_path = os.path.join(tempfile.gettempdir(), "rtm_probe.svg")
        with open(svg_path, "w", encoding="utf-8") as fh:
            fh.write('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
                     '<circle cx="50" cy="50" r="40" fill="red"/></svg>')
        svg = SVGMobject(svg_path)
        win.play(FadeIn(svg), run_time=0.4)
    _run("g_svg_mobject", build, expect_anim=True)


def test_image_mobject():
    # manim 0.21 exposes AbstractImageMobject/Image via a raster path; render a
    # generated image so no external file is needed.
    def build(sc, win):
        from PIL import Image as PILImage
        import tempfile
        arr = (np.linspace(0, 255, 64 * 64 * 3).reshape(64, 64, 3)).astype("uint8")
        path = os.path.join(tempfile.gettempdir(), "rtm_probe_img.png")
        PILImage.fromarray(arr).save(path)
        from manim import ImageMobject
        im = ImageMobject(path).scale(2)
        win.play(FadeIn(im), run_time=0.4)
    _run("g_image_mobject", build, expect_anim=True)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for fn in fns:
        try:
            fn(); print("PASS", fn.__name__); passed += 1
        except Exception as e:
            print("FAIL", fn.__name__, "->", str(e)[:200]); failed += 1
    print(f"\n{passed} passed, {failed} failed")
