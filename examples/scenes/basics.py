# ruff: noqa: F403, F405 -- manim-style star imports (from .common import *)
"""Demo scenes: the core animation vocabulary -- Create / Write, Transform, Fade,
Rotate, VGroup and Succession.

Split out of the original single-file ``demo_scene.py``; the class
bodies are unchanged.  Re-exported by ``examples.scenes``.
"""
from .common import *  # noqa: F401,F403
from .common import _title  # noqa: F401

__all__ = [
    "DemoCreate", "DemoWriteUnwrite", "DemoTransform",
    "DemoReplacementTransform", "DemoFadeInFadeOut", "DemoFadeTransform",
    "DemoRotating", "DemoTransformMatchingShapes", "DemoVGroup", "DemoAllShapes",
    "DemoSuccession", "DemoFadeInShift"
]


class DemoCreate(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Create - draw shapes")

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.6)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4)

        circ = Circle(radius=0.8, color=RED)
        circ.set_fill(RED, opacity=0.6)
        circ.set_stroke(width=4)

        tri = Triangle(color=GREEN)
        tri.set_fill(GREEN, opacity=0.6)
        tri.set_stroke(width=4)
        tri.scale(0.9)
        tri.shift(RIGHT * 4)

        render.play(Create(sq), Create(circ), Create(tri), run_time=2.0)
        render.play(Wait(1.5))
        render.close()


class DemoWriteUnwrite(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Write / Unwrite - text")

        t1 = Text("Hello World", font_size=60).shift(UP * 1)
        t2 = Text("Vulkan Render", font_size=48).shift(DOWN * 1)

        render.play(Write(t1, run_time=2.0))
        render.play(Wait(0.5))
        render.play(Write(t2, run_time=1.5))
        render.play(Wait(0.5))
        render.play(Unwrite(t1, run_time=1.5))
        render.play(Wait(0.5))
        render.close()


class DemoTransform(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Transform - morph shapes")

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4)

        circ = Circle(radius=0.8, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 4)

        render.play(Add(sq), Add(circ), run_time=0.5)
        render.play(Wait(0.5))

        render.play(Transform(sq, circ, run_time=1.5))
        render.play(Wait(1.0))
        render.close()


class DemoReplacementTransform(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "ReplacementTransform - replace in scene")

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)

        tri = Triangle(color=RED)
        tri.set_fill(RED, opacity=0.7)
        tri.set_stroke(width=4)
        tri.scale(0.9)

        render.play(Add(sq), run_time=0.5)
        render.play(Wait(0.5))

        render.play(ReplacementTransform(sq, tri, run_time=1.5))
        render.play(Wait(1.0))
        render.close()


class DemoFadeInFadeOut(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FadeIn / FadeOut")

        sq = Square(side_length=1.2, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 3)

        circ = Circle(radius=0.7, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)

        tri = Triangle(color=GREEN)
        tri.set_fill(GREEN, opacity=0.7)
        tri.set_stroke(width=4)
        tri.scale(0.8)
        tri.shift(RIGHT * 3)

        render.play(FadeIn(sq), FadeIn(circ), FadeIn(tri), run_time=1.5)
        render.play(Wait(0.5))
        render.play(FadeOut(sq), FadeOut(circ), FadeOut(tri), run_time=1.5)
        render.play(Wait(0.5))
        render.close()


class DemoFadeTransform(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FadeTransform - crossfade shapes")

        sq = Square(side_length=1.5, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 3)

        circ = Circle(radius=0.8, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 3)

        render.play(Add(sq), Add(circ), run_time=0.5)
        render.play(Wait(0.5))

        render.play(FadeTransform(sq, circ, run_time=2.0))
        render.play(Wait(1.0))
        render.close()


class DemoRotating(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Rotating / Rotate")

        sq = Square(side_length=1.2, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4)

        tri = Triangle(color=RED)
        tri.set_fill(RED, opacity=0.7)
        tri.set_stroke(width=4)
        tri.scale(0.8)

        circ = Circle(radius=0.6, color=GREEN)
        circ.set_fill(GREEN, opacity=0.7)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 4)

        render.play(Add(sq), Add(tri), Add(circ), run_time=0.5)
        render.play(Wait(0.3))

        render.play(Rotating(sq, run_time=3.0))
        render.play(Rotate(tri, angle=PI, run_time=1.5))
        render.play(Rotate(circ, angle=PI / 2, run_time=1.0))
        render.play(Wait(0.5))
        render.close()


class DemoTransformMatchingShapes(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "TransformMatchingShapes")

        src = Text("abc", font_size=72)
        src.shift(LEFT * 3.5)

        tar = Text("xyz", font_size=72)
        tar.shift(RIGHT * 3.5)

        render.play(Write(src, run_time=1.5))
        render.play(Add(tar), run_time=0.5)
        render.play(Wait(0.5))

        render.play(TransformMatchingShapes(src, tar, run_time=2.0))
        render.play(Wait(1.5))
        render.close()


class DemoVGroup(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "VGroup - grouped animations")

        squares = VGroup()
        for i in range(5):
            sq = Square(side_length=0.8, color=[BLUE, GREEN, YELLOW, ORANGE, RED][i])
            sq.set_fill(opacity=0.7)
            sq.set_stroke(width=4)
            sq.shift(LEFT * 4 + RIGHT * 2 * i)
            squares.add(sq)

        render.play(Create(squares, run_time=2.0, lag_ratio=0.3))
        render.play(Wait(0.5))
        render.play(FadeOut(squares, run_time=1.5))
        render.play(Wait(0.5))
        render.close()


class DemoAllShapes(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "All supported shapes")

        sq = Square(side_length=1.0, color=BLUE)
        sq.set_fill(BLUE, opacity=0.6)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 5 + UP * 1.5)

        rect = Rectangle(width=1.6, height=0.9, color=GREEN)
        rect.set_fill(GREEN, opacity=0.6)
        rect.set_stroke(width=4)
        rect.shift(LEFT * 2 + UP * 1.5)

        circ = Circle(radius=0.5, color=RED)
        circ.set_fill(RED, opacity=0.6)
        circ.set_stroke(width=4)
        circ.shift(RIGHT * 1 + UP * 1.5)

        tri = Triangle(color=YELLOW)
        tri.set_fill(YELLOW, opacity=0.6)
        tri.set_stroke(width=4)
        tri.scale(0.6)
        tri.shift(RIGHT * 4 + UP * 1.5)

        line = Line(LEFT * 5, RIGHT * 1, color=ORANGE)
        line.set_stroke(width=4)
        line.shift(DOWN * 1)

        arrow = Arrow(LEFT * 1, RIGHT * 4, color=PURPLE)
        arrow.set_stroke(width=4)
        arrow.shift(DOWN * 1)

        dash = DashedLine(LEFT * 5 + DOWN * 2.5, RIGHT * 4 + DOWN * 2.5, color=TEAL)
        dash.set_stroke(width=4)

        render.play(
            Create(sq), Create(rect), Create(circ), Create(tri),
            Create(line), Create(arrow), Create(dash),
            run_time=2.5,
        )
        render.play(Wait(2.0))
        render.close()


class DemoSuccession(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Succession - chained animations")

        sq = Square(side_length=1.0, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)

        circ = Circle(radius=0.6, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)

        tri = Triangle(color=GREEN)
        tri.set_fill(GREEN, opacity=0.7)
        tri.set_stroke(width=4)
        tri.scale(0.6)

        render.play(Add(sq), run_time=0.5)
        render.play(Wait(0.3))

        render.play(
            Succession(
                Transform(sq, circ, run_time=1.0),
                Transform(sq, tri, run_time=1.0),
            )
        )
        render.play(Wait(1.0))
        render.close()


class DemoFadeInShift(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FadeIn with shift/scale")

        sq = Square(side_length=1.0, color=BLUE)
        sq.set_fill(BLUE, opacity=0.7)
        sq.set_stroke(width=4)
        sq.shift(LEFT * 4)

        circ = Circle(radius=0.6, color=RED)
        circ.set_fill(RED, opacity=0.7)
        circ.set_stroke(width=4)

        tri = Triangle(color=GREEN)
        tri.set_fill(GREEN, opacity=0.7)
        tri.set_stroke(width=4)
        tri.scale(0.6)
        tri.shift(RIGHT * 4)

        render.play(
            FadeIn(sq, shift=UP * 2),
            FadeIn(circ, scale=2.0),
            FadeIn(tri, target_position=sq.get_center()),
            run_time=2.0,
        )
        render.play(Wait(1.5))
        render.play(
            FadeOut(sq, shift=DOWN * 2),
            FadeOut(circ, scale=0.0),
            FadeOut(tri, shift=UP * 2),
            run_time=2.0,
        )
        render.play(Wait(0.5))
        render.close()
