# ruff: noqa: F403, F405 -- manim-style star imports (from .common import *)
"""Demo scenes: creating, writing and growing mobjects -- Create / Uncreate,
Unwrite, DrawBorderThenFill, Fade and Grow variants.

Split out of the original single-file ``demo_scene.py``; the class
bodies are unchanged.  Re-exported by ``examples.scenes``.
"""
from .common import *  # noqa: F401,F403
from .common import _title  # noqa: F401

__all__ = [
    "DemoCreateSquare", "DemoDrawBorderThenFill",
    "DemoShowIncreasingSubsets", "DemoSpiralIn", "DemoTypeWithCursor",
    "DemoUntypeWithCursor", "DemoUnwriteReverseTrue", "DemoUnwriteReverseFalse",
    "DemoUncreate", "DemoShowWrite", "DemoShowWriteReversed", "DemoFadeInExample",
    "DemoFadeOutExample", "DemoGrowFromCenter", "DemoGrowArrow", "DemoGrowFromEdge",
    "DemoGrowFromPoint", "DemoSpinInFromNothing"
]


class DemoCreateSquare(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        sq = Square()
        self.add(sq)
        render.play(Create(sq))
        render.play(Wait(1.0))
        render.close()

# you are not allowed to change any code here --TT Noted
class DemoDrawBorderThenFill(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "DrawBorderThenFill")

        sq = Square(fill_opacity=1, fill_color=ORANGE)
        sq.set_stroke(width=4)

        render.play(DrawBorderThenFill(sq, run_time=2.0))
        render.play(Wait(1.5))
        render.close()


class DemoShowIncreasingSubsets(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "ShowIncreasingSubsets")

        p = VGroup(Dot(), Square(), Triangle())
        self.add(p)
        render.play(ShowIncreasingSubsets(p, run_time=2.0))
        render.play(Wait(1.5))
        render.close()


class DemoSpiralIn(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "SpiralIn")

        circle = Circle(color=GREEN_C, fill_opacity=1).shift(LEFT)
        square = Square(color=BLUE_D, fill_opacity=1).shift(UP)
        shapes = VGroup(circle, square)
        self.add(shapes)
        render.play(SpiralIn(shapes))
        render.play(Wait(1.5))
        render.close()


class DemoTypeWithCursor(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "TypeWithCursor + Blink")

        text = Text("Inserting", color=PURPLE).scale(1.5).to_edge(LEFT)
        cursor = Rectangle(
            color=GREY_A,
            fill_color=GREY_A,
            fill_opacity=1.0,
            height=1.1,
            width=0.5,
        ).move_to(text[0])

        render.play(TypeWithCursor(text, cursor, time_per_char=0.15, run_time=2.5))
        render.play(Blink(cursor, blinks=2, time_on=0.4, time_off=0.4, run_time=2.0))
        render.play(Wait(0.5))
        render.close()


class DemoUntypeWithCursor(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "UntypeWithCursor + Blink")
        text = Text("Deleting", color=PURPLE).scale(1.5).to_edge(LEFT)
        cursor = Rectangle(
            color=GREY_A,
            fill_color=GREY_A,
            fill_opacity=1.0,
            height=1.1,
            width=0.5,
        ).move_to(text[0])

        render.play(UntypeWithCursor(text, cursor))
        render.play(Blink(cursor, blinks=2))
        render.close()


class DemoUnwriteReverseTrue(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Unwrite reverse=True")

        text = Text("Alice and Bob").scale(3)
        render.play(Write(text))
        render.play(Wait(1.0))
        render.play(Unwrite(text, reverse=True))
        render.play(Wait(1.0))
        render.close()


class DemoUnwriteReverseFalse(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Unwrite reverse=False")

        text = Text("Alice and Bob").scale(3)
        render.play(Write(text))
        render.play(Wait(1.0))
        render.play(Unwrite(text, reverse=False))
        render.play(Wait(1.0))
        render.close()


class DemoUncreate(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Uncreate - reverse of Create")

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)

        render.play(Create(sq, run_time=1.0))
        render.play(Wait(0.5))
        render.play(Uncreate(sq, run_time=1.5))
        render.play(Wait(0.5))
        render.close()


class DemoShowWrite(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Write - font_size=144")

        text = Text("Hello", font_size=144)
        render.play(Write(text))
        render.play(Wait(1.5))
        render.close()


class DemoShowWriteReversed(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Write reversed - font_size=144")

        text = Text("Hello", font_size=144)
        render.play(Write(text, reverse=True, remover=False))
        render.play(Wait(1.5))
        render.close()


class DemoFadeInExample(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FadeIn with shift/target_position/scale")

        dot = Dot(UP * 2 + LEFT)
        self.add(dot)

        w0 = Text("FadeIn with", font_size=36)
        w1 = Text("shift", font_size=36)
        w2 = Text("target_position", font_size=36)
        w3 = Text("and scale", font_size=36)
        words = VGroup(w0, w1, w2, w3).arrange(RIGHT, buff=0.3)

        animations = [
            FadeIn(w0),
            FadeIn(w1, shift=DOWN),
            FadeIn(w2, target_position=dot),
            FadeIn(w3, scale=1.5),
        ]
        render.play(AnimationGroup(*animations, lag_ratio=0.5))
        render.play(Wait(1.5))
        render.close()


class DemoFadeOutExample(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FadeOut with shift/target_position/scale")

        dot = Dot(UP * 2 + LEFT)
        self.add(dot)

        t0 = Text("FadeOut with", font_size=36)
        t1 = Text("shift", font_size=36)
        t2 = Text("target_position", font_size=36)
        t3 = Text("and scale", font_size=36)
        tex = VGroup(t0, t1, t2, t3).arrange(RIGHT, buff=0.3)
        self.add(t0, t1, t2, t3)

        animations = [
            FadeOut(t0),
            FadeOut(t1, shift=DOWN),
            FadeOut(t2, target_position=dot),
            FadeOut(t3, scale=0.5),
        ]
        render.play(AnimationGroup(*animations, lag_ratio=0.5))
        render.play(Wait(1.5))
        render.close()


class DemoGrowFromCenter(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "GrowFromCenter")

        squares = [Square() for _ in range(2)]
        VGroup(*squares).set_x(0).arrange(buff=2)

        render.play(GrowFromCenter(squares[0]))
        render.play(GrowFromCenter(squares[1], point_color=RED))
        render.play(Wait(1.5))
        render.close()


class DemoGrowArrow(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "GrowArrow")

        arrows = [Arrow(2 * LEFT, 2 * RIGHT), Arrow(2 * DR, 2 * UL)]
        VGroup(*arrows).set_x(0).arrange(buff=2)

        render.play(GrowArrow(arrows[0]))
        render.play(GrowArrow(arrows[1], point_color=RED))
        render.play(Wait(1.5))
        render.close()


class DemoGrowFromEdge(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "GrowFromEdge")

        squares = [Square() for _ in range(4)]
        VGroup(*squares).set_x(0).arrange(buff=1)

        render.play(GrowFromEdge(squares[0], DOWN))
        render.play(GrowFromEdge(squares[1], RIGHT))
        render.play(GrowFromEdge(squares[2], UR))
        render.play(GrowFromEdge(squares[3], UP, point_color=RED))
        render.play(Wait(1.5))
        render.close()


class DemoGrowFromPoint(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "GrowFromPoint")

        dot = Dot(3 * UR, color=GREEN)
        squares = [Square() for _ in range(4)]
        VGroup(*squares).set_x(0).arrange(buff=1)
        self.add(dot)

        render.play(GrowFromPoint(squares[0], ORIGIN))
        render.play(GrowFromPoint(squares[1], [-2, 2, 0]))
        render.play(GrowFromPoint(squares[2], [3, -2, 0], RED))
        render.play(GrowFromPoint(squares[3], dot, dot.get_color()))
        render.play(Wait(1.5))
        render.close()


class DemoSpinInFromNothing(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "SpinInFromNothing")

        squares = [Square() for _ in range(3)]
        VGroup(*squares).set_x(0).arrange(buff=2)

        render.play(SpinInFromNothing(squares[0]))
        render.play(SpinInFromNothing(squares[1], angle=2 * PI))
        render.play(SpinInFromNothing(squares[2], point_color=RED))
        render.play(Wait(1.5))
        render.close()
