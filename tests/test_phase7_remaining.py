"""Phase 7 -- the last remaining ⚠️ pages (minor features not yet exercised).

Covers the leftovers flagged in the wiki after Phases 1-5:
  14b  Table methods        (add_highlighted_cell / get_cell / create)
  05-01b  NumberLine methods (n2p / p2n / add_numbers / add_ticks / get_center_point)
  05-02b  guide lines & line graph (get_horizontal_line / get_vertical_line / plot_line_graph)
  05-05b  curve annotation    (get_graph_label / get_T_label / get_vertical_lines_to_graph /
                               get_secant_slope_group / plot_implicit_curve)
  05-05c  derivative/antiderivative (plot_derivative_graph / plot_antiderivative_graph /
                                     input_to_graph_point / slope_of_tangent)
  05-06   area & Riemann       (get_area / get_riemann_rectangles)
  05-10   scaling              (LogBase / LinearBase)
  07-01b  graph edit           (g[k] / add_edges / remove_edges / change_layout)
  04-04b  Label / LabeledPolygram

Run standalone:  python -X utf8 tests/test_phase7_remaining.py
Or with pytest:  pytest tests/test_phase7_remaining.py -q
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
    Scene, Square, Circle, Dot, Line, DashedLine, VGroup, Table, Matrix,
    NumberLine, Axes, NumberPlane, ComplexPlane,
    LogBase, LinearBase, DecimalNumber, Integer, Tex, MathTex,
    Graph, DiGraph, Label, LabeledPolygram, LabeledLine,
    Create, FadeIn, Write, Wait, UP, DOWN, LEFT, RIGHT, ORIGIN, PI, UR, DL,
    RED, GREEN, BLUE, YELLOW, WHITE, PURPLE_B, PURE_YELLOW,
)


def _run(name, build, expect_anim=False):
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            build(self, win)
            win.close()
    info = verify(S, name)
    assert info["render"] == "OK", info
    assert not info["all_blank"], info
    if expect_anim:
        assert not info["static"], info
    return info


# --------------------------------------------------------------------------
# 14b  Table methods
# --------------------------------------------------------------------------

def test_table_add_highlighted_cell():
    def build(sc, win):
        t = Table([["1", "2"], ["3", "4"]], include_outer_lines=True)
        t.add_highlighted_cell((2, 1), color=RED)
        win.play(FadeIn(t), run_time=0.6)
    _run("t_table_highlight", build, expect_anim=True)


def test_table_get_cell():
    def build(sc, win):
        t = Table([["a", "b"], ["c", "d"]])
        cell = t.get_cell(pos=(1, 2))
        hcell = t.get_highlighted_cell(pos=(2, 2), color=BLUE)
        win.play(FadeIn(t), run_time=0.3)
        win.play(FadeIn(cell), FadeIn(hcell), run_time=0.3)
    _run("t_table_get_cell", build, expect_anim=True)


def test_table_create():
    def build(sc, win):
        t = Table([["1", "2"], ["3", "4"]], include_outer_lines=True)
        win.play(t.create(lag_ratio=0.5), run_time=1.0)
    _run("t_table_create", build, expect_anim=True)


# --------------------------------------------------------------------------
# 05-01b  NumberLine methods
# --------------------------------------------------------------------------

def test_numberline_methods():
    def build(sc, win):
        nl = NumberLine(x_range=[-3, 3, 1], length=8)
        pt = nl.n2p(2)                       # number -> scene point
        assert np.allclose(nl.p2n(pt), 2)    # scene point -> number
        nl.add_numbers()
        nl.add_ticks()
        d = Dot(point=pt)
        self_group = VGroup(nl, d)
        win.play(Create(nl), run_time=0.4)
        win.play(FadeIn(d), run_time=0.2)
    _run("c_nl_methods", build, expect_anim=True)


# --------------------------------------------------------------------------
# 05-02b  guide lines & line graph
# --------------------------------------------------------------------------

def test_axes_guide_lines_and_line_graph():
    def build(sc, win):
        ax = Axes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], x_length=6, y_length=6)
        h = ax.get_horizontal_line(ax.c2p(0, 1), color=BLUE)
        v = ax.get_vertical_line(ax.c2p(1, 0), color=GREEN)
        lg = ax.plot_line_graph(x_values=[-2, -1, 0, 1, 2],
                                y_values=[1, -1, 2, 0, -1])
        win.play(Create(ax), run_time=0.3)
        win.play(Create(h), Create(v), run_time=0.3)
        win.play(Create(lg), run_time=0.4)
    _run("c_guide_lines", build, expect_anim=True)


# --------------------------------------------------------------------------
# 05-05b  curve annotation helpers
# --------------------------------------------------------------------------

def test_graph_label():
    def build(sc, win):
        ax = Axes(x_range=[-3, 3, 1], y_range=[-1, 5], x_length=6, y_length=5)
        curve = ax.plot(lambda x: x ** 2, x_range=[-2, 2], color=PURPLE_B)
        lbl = ax.get_graph_label(curve, "x^2", x_val=-2, direction=DL)
        win.play(Create(ax), run_time=0.2)
        win.play(Create(curve), run_time=0.3)
        win.play(FadeIn(lbl), run_time=0.3)
    _run("c_graph_label", build, expect_anim=True)


def test_graph_T_label():
    def build(sc, win):
        ax = Axes(x_range=[-3, 5, 1], y_range=[-1, 7], x_length=7, y_length=5)
        curve = ax.plot(lambda x: x ** 2, x_range=[-2, 2], color=PURPLE_B)
        t_lbl = ax.get_T_label(x_val=2, graph=curve, label=Tex("x-value"))
        win.play(Create(ax), run_time=0.2)
        win.play(Create(curve), run_time=0.3)
        win.play(FadeIn(t_lbl), run_time=0.3)
    _run("c_graph_T_label", build, expect_anim=True)


def test_vertical_lines_to_graph():
    def build(sc, win):
        ax = Axes(x_range=[-3, 3, 1], y_range=[-1, 5], x_length=6, y_length=5)
        curve = ax.plot(lambda x: x ** 2, x_range=[-2, 2])
        lines = ax.get_vertical_lines_to_graph(curve, x_range=[-2, 2], num_lines=8)
        win.play(Create(ax), run_time=0.2)
        win.play(Create(curve), run_time=0.3)
        win.play(Create(lines), run_time=0.4)
    _run("c_vertical_lines", build, expect_anim=True)


def test_secant_slope_group():
    def build(sc, win):
        ax = Axes(x_range=[-3, 5, 1], y_range=[-1, 7], x_length=7, y_length=5)
        curve = ax.plot(lambda x: x ** 2, x_range=[-2, 2])
        grp = ax.get_secant_slope_group(x=2.0, graph=curve, dx=1.0,
                                        dx_label="dx", dy_label="dy",
                                        secant_line_length=4)
        win.play(Create(ax), run_time=0.2)
        win.play(Create(curve), run_time=0.3)
        win.play(Create(grp), run_time=0.4)
    _run("c_secant_group", build, expect_anim=True)


def test_implicit_curve():
    def build(sc, win):
        ax = Axes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], x_length=6, y_length=6)
        ic = ax.plot_implicit_curve(lambda x, y: x ** 2 + y ** 2 - 4)
        win.play(Create(ax), run_time=0.2)
        win.play(Create(ic), run_time=0.6)
    _run("c_implicit_curve", build, expect_anim=True)


# --------------------------------------------------------------------------
# 05-05c  derivative / antiderivative / tangent
# --------------------------------------------------------------------------

def test_derivative_graph():
    def build(sc, win):
        ax = NumberPlane(x_range=[-3, 3], y_range=[-3, 3],
                         background_line_style={"stroke_opacity": 0.3})
        c1 = ax.plot(lambda x: x ** 2, color=PURPLE_B, x_range=[-2, 2])
        c2 = ax.plot_derivative_graph(c1, color=GREEN)
        pos = ax.input_to_graph_point(x=PI / 2, graph=c1)
        sq = Square(side_length=0.5, color=YELLOW).move_to(pos)
        win.play(Create(c1), run_time=0.3)
        win.play(Create(c2), run_time=0.3)
        win.play(FadeIn(sq), run_time=0.2)
    _run("c_derivative", build, expect_anim=True)


def test_antiderivative_graph():
    def build(sc, win):
        ax = Axes(x_range=[-3, 3, 1], y_range=[-3, 3], x_length=6, y_length=5)
        c1 = ax.plot(lambda x: x ** 2, x_range=[-2, 2])
        c2 = ax.plot_antiderivative_graph(c1, y_intercept=0, samples=50)
        win.play(Create(ax), run_time=0.2)
        win.play(Create(c1), run_time=0.3)
        win.play(Create(c2), run_time=0.3)
    _run("c_antiderivative", build, expect_anim=True)


def test_slope_of_tangent():
    def build(sc, win):
        ax = Axes(x_range=[-3, 3, 1], y_range=[-3, 3], x_length=6, y_length=5)
        g = ax.plot(lambda x: x ** 2, x_range=[-2, 2])
        slope = ax.slope_of_tangent(x=-2, graph=g)
        assert abs(slope - (-4.0)) < 0.1, slope
        win.play(Create(ax), run_time=0.2)
        win.play(Create(g), run_time=0.3)
    _run("c_slope_tangent", build, expect_anim=True)


# --------------------------------------------------------------------------
# 05-06  area & Riemann rectangles
# --------------------------------------------------------------------------

def test_get_area():
    def build(sc, win):
        ax = Axes(x_range=[-3, 3, 1], y_range=[-1, 5], x_length=6, y_length=5)
        graph = ax.plot(lambda x: x ** 2, x_range=[-2, 2])
        area = ax.get_area(graph, x_range=[-2, 2], color=(BLUE, GREEN), opacity=0.4)
        win.play(Create(ax), run_time=0.2)
        win.play(Create(graph), run_time=0.3)
        win.play(FadeIn(area), run_time=0.3)
    _run("c_get_area", build, expect_anim=True)


def test_get_riemann_rectangles():
    def build(sc, win):
        ax = Axes(x_range=[-3, 3, 1], y_range=[-1, 5], x_length=6, y_length=5)
        graph = ax.plot(lambda x: x ** 2, x_range=[-2, 2])
        rects = ax.get_riemann_rectangles(graph, x_range=[-2, 2], dx=0.4,
                                          stroke_width=0.5)
        win.play(Create(ax), run_time=0.2)
        win.play(Create(graph), run_time=0.3)
        win.play(FadeIn(rects), run_time=0.3)
    _run("c_riemann", build, expect_anim=True)


# --------------------------------------------------------------------------
# 05-10  LogBase / LinearBase scaling
# --------------------------------------------------------------------------

def test_log_base_scaling():
    def build(sc, win):
        nl = NumberLine(x_range=[0, 3, 1], length=8, scaling=LogBase(base=10))
        nl.add_numbers()
        win.play(Create(nl), run_time=0.5)
    _run("c_log_base", build, expect_anim=True)


def test_linear_base_scaling():
    def build(sc, win):
        nl = NumberLine(x_range=[-2, 2, 1], length=8, scaling=LinearBase(scale_factor=1.0))
        win.play(Create(nl), run_time=0.4)
    _run("c_linear_base", build, expect_anim=True)


# --------------------------------------------------------------------------
# 07-01b  graph edit: index / add_edges / remove_edges / change_layout
# --------------------------------------------------------------------------

def test_graph_index_and_edges():
    def build(sc, win):
        g = Graph([1, 2, 3], [(1, 2), (2, 3)], layout="circular", labels=True)
        v = g[1]           # vertex mobject
        e = g[(1, 2)]      # edge mobject
        assert v is not None and e is not None
        self_group = VGroup(g)
        win.play(FadeIn(g), run_time=0.4)
    _run("g_graph_index", build, expect_anim=True)


def test_graph_add_remove_change_layout():
    def build(sc, win):
        g = Graph([1, 2, 3], [(1, 2), (2, 3)], layout="circular")
        win.play(FadeIn(g), run_time=0.3)
        win.play(g.animate.add_edges((1, 4), positions={4: [2, 0.5, 0]}),
                 run_time=0.4)
        win.play(g.animate.remove_edges((2, 3)), run_time=0.3)
        win.play(g.animate.change_layout("spring"), run_time=0.4)
    _run("g_graph_edit", build, expect_anim=True)


# --------------------------------------------------------------------------
# 04-04b  Label & LabeledPolygram (the two not covered in Phase 2)
# --------------------------------------------------------------------------

def test_label():
    def build(sc, win):
        lb = Label("hi", label_config={"color": WHITE})
        win.play(FadeIn(lb), run_time=0.5)
    _run("g_label", build, expect_anim=True)


def test_labeled_polygram():
    def build(sc, win):
        lp = LabeledPolygram(
            [[-2, -1, 0], [2, -1, 0], [2, 1, 0], [-2, 1, 0]],
            label="inside", precision=0.01)
        win.play(FadeIn(lp), run_time=0.5)
    _run("g_labeled_polygram", build, expect_anim=True)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for fn in fns:
        try:
            fn(); print("PASS", fn.__name__); passed += 1
        except Exception as e:
            print("FAIL", fn.__name__, "->", str(e)[:250]); failed += 1
    print(f"\n{passed} passed, {failed} failed")
