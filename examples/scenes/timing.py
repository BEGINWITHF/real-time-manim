# ruff: noqa: F403, F405 -- manim-style star imports (from .common import *)
"""Demo scenes: text styles and animation timing -- add, run_time, LagRatios,
TracedPath, LaggedStart and Succession patterns.

Split out of the original single-file ``demo_scene.py``; the class
bodies are unchanged.  Re-exported by ``examples.scenes``.
"""
from .common import *  # noqa: F401,F403
from .common import _title  # noqa: F401

__all__ = [
    "DemoTextFeatures", "DemoCombined", "DemoDefaultAdd",
    "DemoAddWithRunTime", "DemoLagRatios", "DemoChangeDefaultAnimation",
    "DemoAnimatedBoundary", "DemoTracedPath", "DemoDissipatingPath",
    "DemoLaggedStartMap", "DemoLaggedStart", "DemoSuccessionDots"
]


class DemoTextFeatures(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Text rendering")

        render.play(Write(Text("Hello World", font_size=60).shift(UP * 1.5)), run_time=2.0)
        render.play(Wait(0.5))
        render.play(Write(Text("Bold Text", font_size=48, weight=BOLD).shift(UP * 0.0)), run_time=1.5)
        render.play(Wait(0.5))
        render.play(Write(Text("Vulkan Renderer", font_size=48).shift(DOWN * 1.5)), run_time=1.5)
        render.play(Wait(1.5))
        render.close()


class DemoCombined(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Combined demo")

        sq = Square(side_length=1.2, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4 + UP * 1)

        circ = Circle(radius=0.7, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 4 + UP * 1)

        label = Write(Text("Combined Demo", font_size=28).shift(DOWN * 2.5))

        render.play(Add(sq), Add(circ), label, run_time=1.5)
        render.play(Wait(0.3))

        render.play(Transform(sq, circ, run_time=1.5))
        render.play(Wait(0.5))

        render.play(FadeOut(sq), FadeOut(circ), run_time=1.0)
        render.play(Wait(0.5))
        render.close()


class DemoDefaultAdd(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        text_1 = Text("I was added with Add!")
        text_2 = Text("Me too!")
        text_3 = Text("And me!")
        texts = VGroup(text_1, text_2, text_3).arrange(DOWN)
        rect = SurroundingRectangle(texts, buff=0.5)

        render.play(
            Create(rect, run_time=3.0),
            Succession(
                Wait(1.0),
                Add(text_1),
                Wait(1.0),
                Add(text_2, text_3),
            ),
        )
        render.play(Wait(2.0))
        render.close()


class DemoAddWithRunTime(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        circles = VGroup(
            *[Circle(radius=0.5) for _ in range(25)]
        ).arrange_in_grid(5, 5)

        render.play(
            Succession(
                *[Add(circle, run_time=0.2) for circle in circles],
                rate_func=smooth,
            ),
        )
        render.play(Wait(2.0))
        render.close()


class DemoLagRatios(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        ratios = [0, 0.1, 0.5, 1, 2]

        group = VGroup(*[Dot() for _ in range(4)]).arrange_submobjects()
        groups = VGroup(*[group.copy() for _ in ratios]).arrange_submobjects(buff=1)
        self.add(groups)

        self.add(Text("lag_ratio = ", font_size=36).next_to(groups, UP, buff=1.5))
        for grp, ratio in zip(groups, ratios):
            self.add(Text(str(ratio), font_size=36).next_to(grp, UP))

        render.play(AnimationGroup(*[
            grp.animate(lag_ratio=ratio, run_time=1.5).shift(DOWN * 2)
            for grp, ratio in zip(groups, ratios)
        ]))

        render.play(groups.animate(run_time=1, lag_ratio=0.1).shift(UP * 2))
        render.play(Wait(1.0))
        render.close()


class DemoChangeDefaultAnimation(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        Rotate.set_default(run_time=2, rate_func=rate_functions.linear)
        Indicate.set_default(color=None)

        S = Square(color=BLUE, fill_color=BLUE, fill_opacity=0.25)
        self.add(S)
        render.play(Rotate(S, PI))
        render.play(Indicate(S))

        Rotate.set_default()
        Indicate.set_default()
        render.play(Wait(0.5))
        render.close()


class DemoAnimatedBoundary(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        text = Text("So shiny!")
        boundary = AnimatedBoundary(text, colors=[RED, GREEN, BLUE],
                                    cycle_rate=3)
        self.add(text, boundary)
        render.play(Wait(2.0))
        render.close()


# you are not allowed to change any code here --TT Noted
class DemoTracedPath(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        circ = Circle(color=RED).shift(4 * LEFT)
        dot = Dot(color=RED).move_to(circ.get_start())
        rolling_circle = VGroup(circ, dot)
        trace = TracedPath(circ.get_start)
        rolling_circle.add_updater(lambda m: m.rotate(-0.3))
        self.add(trace, rolling_circle)
        render.play(rolling_circle.animate.shift(8 * RIGHT), run_time=4, rate_func=linear)


class DemoDissipatingPath(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        a = Dot(RIGHT * 2)
        b = TracedPath(a.get_center, dissipating_time=0.5, stroke_opacity=[0, 1])
        self.add(a, b)
        render.play(a.animate(path_arc=PI / 4).shift(LEFT * 2))
        render.play(a.animate(path_arc=-PI / 4).shift(LEFT * 2))
        render.play(Wait(1.0))
        render.close()


class DemoLaggedStartMap(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        title = Text("LaggedStartMap").to_edge(UP, buff=LARGE_BUFF)
        dots = VGroup(
            *[Dot(radius=0.16) for _ in range(35)]
            ).arrange_in_grid(rows=5, cols=7, buff=MED_LARGE_BUFF)
        self.add(dots, title)

        for mob in dots, title:
            render.play(LaggedStartMap(
                ApplyMethod, mob,
                lambda m: (m.set_color, YELLOW),
                lag_ratio=0.1,
                rate_func=there_and_back,
                run_time=2
            ))
        render.play(Wait(0.5))
        render.close()


class DemoLaggedStart(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        title = Text("lag_ratio = 0.25").to_edge(UP)

        dot1 = Dot(point=LEFT * 2 + UP, radius=0.16)
        dot2 = Dot(point=LEFT * 2, radius=0.16)
        dot3 = Dot(point=LEFT * 2 + DOWN, radius=0.16)
        line_25 = DashedLine(
            start=LEFT + UP * 2,
            end=LEFT + DOWN * 2,
            color=RED
        )
        label = Text("25%", font_size=24).next_to(line_25, UP)
        self.add(title, dot1, dot2, dot3, line_25, label)

        render.play(LaggedStart(
            dot1.animate.shift(RIGHT * 4),
            dot2.animate.shift(RIGHT * 4),
            dot3.animate.shift(RIGHT * 4),
            lag_ratio=0.25,
            run_time=4
        ))
        render.play(Wait(1.0))
        render.close()


class DemoSuccessionDots(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        dot1 = Dot(point=LEFT * 2 + UP * 2, radius=0.16, color=BLUE)
        dot2 = Dot(point=LEFT * 2 + DOWN * 2, radius=0.16, color=MAROON)
        dot3 = Dot(point=RIGHT * 2 + DOWN * 2, radius=0.16, color=GREEN)
        dot4 = Dot(point=RIGHT * 2 + UP * 2, radius=0.16, color=YELLOW)
        self.add(dot1, dot2, dot3, dot4)

        render.play(Succession(
            dot1.animate.move_to(dot2),
            dot2.animate.move_to(dot3),
            dot3.animate.move_to(dot4),
            dot4.animate.move_to(dot1)
        ))
        render.play(Wait(0.5))
        render.close()
