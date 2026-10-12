"""Render demo videos covering every newly-verified feature domain.

Each scene is recorded through a real (hidden) Vulkan window with
`fast_record_scene` and written to `demo_out/`.  Open the mp4s to eyeball the
result.  Run:  python -X utf8 tools/render_demo_videos.py
"""
import os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
from manim import (
    Scene, Square, Circle, Triangle, Dot, Line, DashedLine, Arrow, Polygon, Star,
    VGroup, Text, MathTex, Tex, MarkupText, Paragraph, Matrix, Table, Code,
    DecimalNumber, Integer, Variable, Brace, Angle, SurroundingRectangle,
    Label, LabeledArrow, LabeledLine, LabeledPolygram, Title, BulletedList,
    Union, Difference, Intersection, Exclusion,
    NumberLine, Axes, NumberPlane, ComplexPlane, PolarPlane, ThreeDAxes,
    BarChart, SampleSpace, LogBase, LinearBase,
    Graph, DiGraph, ArrowVectorField, StreamLines,
    AnimatedBoundary, TracedPath,
    LaggedStart, LaggedStartMap, ComplexHomotopy, SmoothedVectorizedHomotopy,
    PhaseFlow, Broadcast, AddTextLetterByLetter, RemoveTextLetterByLetter,
    AddTextWordByWord, UpdateFromFunc, UpdateFromAlphaFunc,
    MaintainPositionRelativeTo, Succession, Wait,
    Create, Uncreate, Write, FadeIn, FadeOut, Rotate, Transform, Indicate,
    UP, DOWN, LEFT, RIGHT, ORIGIN, UL, UR, DL, DR, PI, RIGHT as R,
    RED, GREEN, BLUE, YELLOW, WHITE, BLACK, PURPLE, PURPLE_B, ORANGE, GREY_BROWN,
)

from real_time_manim.vulkan_bind import MLWindow
from real_time_manim.record import fast_record_scene

OUT_DIR = os.path.join(REPO, "demo_out")
os.makedirs(OUT_DIR, exist_ok=True)


def record(scene_cls, name, fps=60):
    out = os.path.join(OUT_DIR, name + ".mp4")
    res = fast_record_scene(scene_cls, out, fps=fps, hidden=True,
                            verbose=False, overwrite=True, cleanup=True)
    p = res.get("out_path")
    size = os.path.getsize(p) if p and os.path.exists(p) else 0
    print(f"  [{name}] -> {p}  ({size/1024:.0f} KB)")
    return p, size


# --------------------------------------------------------------------------
# 1. Animations (the ⚠️ list, now verified)
# --------------------------------------------------------------------------
class AnimationsDemo(Scene):
    def construct(self):
        win = MLWindow(1920, 1080); win.scene = self
        title = Title("RTM Animations -- now verified").scale(0.6)
        win.play(Write(title), run_time=0.5)

        # LaggedStart / LaggedStartMap
        g = VGroup(Square(), Circle(), Triangle()).arrange(RIGHT, buff=0.7)
        win.play(LaggedStart(*[FadeIn(m, shift=UP) for m in g], lag_ratio=0.4),
                 run_time=0.8)
        win.play(LaggedStartMap(lambda m: FadeOut(m), g, lag_ratio=0.3), run_time=0.6)

        # ComplexHomotopy
        sq = Square().set_fill(BLUE, 0.6)
        win.play(Create(sq), run_time=0.3)
        win.play(ComplexHomotopy(lambda z, t: z * np.exp(1j * np.pi * t * 0.5), sq),
                 run_time=0.8)
        win.play(FadeOut(sq), run_time=0.3)

        # PhaseFlow
        d = Dot(color=RED).shift(LEFT * 3)
        self.add(d)
        win.play(PhaseFlow(lambda p: np.array([-p[1], p[0], 0.0]) * 0.4, d),
                 run_time=0.8)
        self.remove(d)

        # Broadcast
        sq2 = Square().set_fill(YELLOW, 0.6)
        win.play(Broadcast(sq2, focal_point=ORIGIN, n_mobs=5,
                           initial_opacity=1.0, final_opacity=0.0), run_time=0.8)

        # AddTextLetterByLetter
        t = Text("Letter by letter", color=GREEN)
        win.play(AddTextLetterByLetter(t), run_time=0.8)
        win.play(RemoveTextLetterByLetter(t), run_time=0.6)

        # TracedPath
        dot = Dot(color=BLUE).shift(LEFT * 3)
        tp = TracedPath(dot.get_center, stroke_width=6, stroke_color=YELLOW)
        self.add(tp, dot)
        win.play(dot.animate(path_arc=PI / 2).shift(RIGHT * 6), run_time=1.0)
        self.remove(tp, dot)

        # AnimatedBoundary (VGroup + updater, add + wait)
        sq3 = Square().set_fill(ORANGE, 0.5)
        ab = AnimatedBoundary(sq3, colors=[RED, GREEN, BLUE], cycle_rate=3)
        self.add(sq3, ab)
        win.play(Wait(1.0))
        self.remove(sq3, ab)

        win.play(FadeOut(title), run_time=0.4)
        win.close()


# --------------------------------------------------------------------------
# 2. Graphics & text
# --------------------------------------------------------------------------
class GraphicsTextDemo(Scene):
    def construct(self):
        win = MLWindow(1920, 1080); win.scene = self
        win.play(Write(Title("Graphics and Text").scale(0.7)), run_time=0.5)

        # Angle
        l1 = Line(ORIGIN, RIGHT * 2)
        l2 = Line(ORIGIN, 2 * (np.cos(PI / 3) * RIGHT + np.sin(PI / 3) * UP))
        ang = Angle(l1, l2, radius=0.6)
        win.play(Create(l1), Create(l2), run_time=0.3)
        win.play(Create(ang), run_time=0.4)
        win.play(FadeOut(VGroup(l1, l2, ang)), run_time=0.3)

        # SurroundingRectangle
        txt = Text("highlight").scale(0.8)
        sr = SurroundingRectangle(txt, color=RED, buff=0.2)
        win.play(Write(txt), run_time=0.4)
        wiggle = SurroundingRectangle(txt, color=YELLOW, buff=0.2)
        win.play(Create(sr), run_time=0.3)
        win.play(Transform(sr, wiggle), run_time=0.4)
        win.play(FadeOut(VGroup(txt, sr)), run_time=0.3)

        # Matrix
        m = Matrix([[1, 2], [3, 4]])
        win.play(Create(m), run_time=0.6)
        win.play(FadeOut(m), run_time=0.3)

        # Table + highlight
        tbl = Table([["1", "2"], ["3", "4"]], include_outer_lines=True)
        tbl.add_highlighted_cell((2, 1), color=RED)
        win.play(FadeIn(tbl), run_time=0.5)
        win.play(tbl.create(lag_ratio=0.5), run_time=0.8)
        win.play(FadeOut(tbl), run_time=0.3)

        # DecimalNumber / Integer / Variable
        dec = DecimalNumber(3.14, num_decimal_places=2).shift(UP * 1.5)
        integ = Integer(42).shift(ORIGIN)
        var = Variable(3, "x", num_decimal_places=0).shift(DOWN * 1.5)
        win.play(FadeIn(dec), FadeIn(integ), FadeIn(var), run_time=0.6)
        win.play(FadeOut(VGroup(dec, integ, var)), run_time=0.3)

        # Brace
        sq = Square()
        br = Brace(sq, direction=DOWN)
        lbl = br.get_text("x")
        win.play(FadeIn(sq), run_time=0.2)
        win.play(Create(br), run_time=0.3)
        win.play(FadeIn(lbl), run_time=0.2)
        win.play(FadeOut(VGroup(sq, br, lbl)), run_time=0.3)

        # Star, Boolean Union, MarkupText, Code, BulletedList
        star = Star(n=5, outer_radius=0.9, inner_radius=0.4).set_fill(YELLOW, 0.8)
        star.shift(LEFT * 4)
        a = Circle(radius=0.7).set_fill(RED, 0.5).shift(ORIGIN + LEFT * 0.4)
        b = Square(side_length=1.2).set_fill(BLUE, 0.5).shift(ORIGIN + RIGHT * 0.4)
        u = Union(a, b)
        mk = MarkupText('markup <i>text</i>').shift(RIGHT * 4).scale(0.6)
        win.play(Create(star), run_time=0.4)
        win.play(FadeIn(a), FadeIn(b), run_time=0.2)
        win.play(FadeIn(u), run_time=0.4)
        win.play(Write(mk), run_time=0.4)
        win.play(FadeOut(VGroup(star, a, b, u, mk)), run_time=0.3)

        # Label / LabeledPolygram
        lb = Label("label box", label_config={"color": WHITE}).shift(UP * 1)
        lp = LabeledPolygram(
            [[-2, -2, 0], [2, -2, 0], [2, -0.5, 0], [-2, -0.5, 0]],
            label="poly", precision=0.01).shift(DOWN * 0.5)
        win.play(FadeIn(lb), run_time=0.3)
        win.play(FadeIn(lp), run_time=0.4)
        win.play(FadeOut(VGroup(lb, lp)), run_time=0.3)

        win.close()


# --------------------------------------------------------------------------
# 3. Coordinate systems & charts
# --------------------------------------------------------------------------
class CoordinatesDemo(Scene):
    def construct(self):
        win = MLWindow(1920, 1080); win.scene = self
        win.play(Write(Title("Coordinate Systems and Charts").scale(0.6)), run_time=0.5)

        # NumberLine with numbers + LogBase
        nl = NumberLine(x_range=[-3, 3, 1], length=8).shift(UP * 2.5)
        nl.add_numbers()
        win.play(Create(nl), run_time=0.6)
        win.play(FadeOut(nl), run_time=0.3)

        # Axes + plot + derivative + area
        ax = Axes(x_range=[-3, 3, 1], y_range=[-1, 5], x_length=7, y_length=5)
        curve = ax.plot(lambda x: x ** 2, x_range=[-2, 2], color=PURPLE_B)
        deriv = ax.plot_derivative_graph(curve, color=GREEN)
        area = ax.get_area(curve, x_range=[-2, 2], color=(BLUE, GREEN), opacity=0.35)
        win.play(Create(ax), run_time=0.4)
        win.play(Create(curve), run_time=0.5)
        lbl = ax.get_graph_label(curve, "x^2", x_val=-2, direction=DL)
        t_lbl = ax.get_T_label(x_val=2, graph=curve, label=Tex("x-val"))
        win.play(FadeIn(lbl), FadeIn(t_lbl), run_time=0.4)
        win.play(Create(deriv), run_time=0.5)
        win.play(FadeIn(area), run_time=0.4)
        win.play(FadeOut(VGroup(ax, curve, deriv, area, lbl, t_lbl)), run_time=0.3)

        # NumberPlane + ComplexPlane
        nplane = NumberPlane(x_range=[-4, 4], y_range=[-3, 3]).scale(0.6).shift(LEFT * 4)
        cplane = ComplexPlane(x_range=[-3, 3], y_range=[-3, 3]).scale(0.6).shift(RIGHT * 4)
        win.play(Create(nplane), run_time=0.5)
        win.play(Create(cplane), run_time=0.5)
        win.play(FadeOut(VGroup(nplane, cplane)), run_time=0.3)

        # BarChart
        bc = BarChart(values=[3, 5, 2, 7], y_range=[0, 8], x_length=5, y_length=3)
        win.play(Create(bc), run_time=0.7)
        win.play(FadeOut(bc), run_time=0.3)

        # PolarPlane + LogBase axis
        pp = PolarPlane().scale(0.6).shift(LEFT * 3.5)
        lognl = NumberLine(x_range=[0, 3, 1], length=6, scaling=LogBase(base=10)).shift(RIGHT * 3.5 + DOWN * 1)
        lognl.add_numbers()
        win.play(Create(pp), run_time=0.5)
        win.play(Create(lognl), run_time=0.5)
        win.play(FadeOut(VGroup(pp, lognl)), run_time=0.3)

        win.close()


# --------------------------------------------------------------------------
# 4. Graph theory & vector fields
# --------------------------------------------------------------------------
class GraphVectorDemo(Scene):
    def construct(self):
        win = MLWindow(1920, 1080); win.scene = self
        win.play(Write(Title("Graphs and Vector Fields").scale(0.65)), run_time=0.5)

        # Graph + add/remove/change_layout
        g = Graph([1, 2, 3], [(1, 2), (2, 3)], layout="circular", labels=True)
        win.play(FadeIn(g), run_time=0.5)
        win.play(g.animate.add_edges((1, 4), positions={4: [2, 0.5, 0]}), run_time=0.5)
        win.play(g.animate.remove_edges((2, 3)), run_time=0.4)
        win.play(g.animate.change_layout("spring"), run_time=0.6)
        win.play(FadeOut(g), run_time=0.3)

        # DiGraph
        dg = DiGraph([1, 2, 3], [(1, 2), (2, 3), (3, 1)], layout="circular")
        win.play(FadeIn(dg), run_time=0.5)
        win.play(FadeOut(dg), run_time=0.3)

        # ArrowVectorField + StreamLines
        vf = ArrowVectorField(lambda p: np.array([-p[1], p[0], 0.0])).scale(0.7)
        sl = StreamLines(lambda p: np.array([-p[1], p[0], 0.0]),
                         x_range=[-3, 3], y_range=[-2, 2]).scale(0.7)
        win.play(FadeIn(vf), run_time=0.6)
        win.play(FadeOut(vf), run_time=0.3)
        win.play(FadeIn(sl), run_time=0.6)
        win.play(FadeOut(sl), run_time=0.3)

        win.close()


# --------------------------------------------------------------------------
# 5. Tools: rate functions & colors
# --------------------------------------------------------------------------
class ToolsDemo(Scene):
    def construct(self):
        import manim
        win = MLWindow(1920, 1080); win.scene = self
        win.play(Write(Title("Rate Functions and Colors").scale(0.65)), run_time=0.5)

        # A row of squares each animated with a different manim rate function
        names = ["smooth", "linear", "rush_into", "there_and_back",
                 "ease_out_bounce", "ease_in_out_elastic"]
        sqs = VGroup(*[Square(side_length=0.8).set_fill(BLUE, 0.6)
                       for _ in names]).arrange(RIGHT, buff=0.5).shift(UP * 1.5)
        self.add(sqs)
        for sq, nm in zip(sqs, names):
            rf = getattr(manim.rate_functions, nm)
            win.play(sq.animate.set_fill(RED, 0.6).scale(1.3), rate_func=rf,
                     run_time=0.5)
            win.play(sq.animate.set_fill(BLUE, 0.6).scale(1 / 1.3), rate_func=rf,
                     run_time=0.4)
        self.remove(sqs)

        # Color interpolation sweep
        swatch = Square(side_length=2.0).set_fill(RED, 0.9)
        win.play(FadeIn(swatch), run_time=0.3)
        for col in (GREEN, BLUE, YELLOW, PURPLE, RED):
            win.play(swatch.animate.set_fill(col, 0.9), run_time=0.4)
        win.play(FadeOut(swatch), run_time=0.3)

        # Indicate colour tint
        tgt = Circle(radius=0.8).set_fill(GREY_BROWN, 0.8)
        win.play(FadeIn(tgt), run_time=0.3)
        win.play(Indicate(tgt, color=YELLOW, scale_factor=1.4), run_time=0.8)
        win.play(FadeOut(tgt), run_time=0.3)

        win.close()


SCENES = [
    (AnimationsDemo, "demo_animations"),
    (GraphicsTextDemo, "demo_graphics_text"),
    (CoordinatesDemo, "demo_coordinates"),
    (GraphVectorDemo, "demo_graph_vector"),
    (ToolsDemo, "demo_tools"),
]


if __name__ == "__main__":
    print(f"Rendering {len(SCENES)} demo videos -> {OUT_DIR}")
    ok = 0
    for cls, name in SCENES:
        try:
            p, size = record(cls, name)
            if size > 5000:
                ok += 1
            else:
                print(f"    !! suspiciously small")
        except Exception as e:
            print(f"  [{name}] FAILED: {type(e).__name__}: {e}")
    print(f"\n{ok}/{len(SCENES)} videos rendered to {OUT_DIR}")
