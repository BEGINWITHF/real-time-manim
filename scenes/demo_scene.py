import time
import numpy as np
from manim import *
from manim.animation.transform import Transform as _ManimTransform
from real_time_manim.vulkan_bind import (
    MLWindow, Write, Wait, Add,
    Create, Uncreate, Unwrite,
    FadeIn, FadeOut, FadeTransform, FadeTransformPieces,
    Transform, ReplacementTransform,
    Rotating, Rotate,
    TransformMatchingShapes, TransformMatchingTex,
    Animation, AnimationGroup, Succession, DrawBorderThenFill,
    ShowIncreasingSubsets, SpiralIn, GrowFromCenter, GrowArrow, GrowFromEdge, GrowFromPoint,
    SpinInFromNothing, ApplyWave, Circumscribe,
    Blink, TypeWithCursor, UntypeWithCursor, Indicate, ShowPassingFlash, Homotopy, MoveAlongPath,
    TextDecimalNumber,
)


def _title(render, text):
    t = Write(Text(text, font_size=32).shift(UP * 3.2), run_time=0.8)
    render.play(t)


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


class DemoApplyingWaves(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "ApplyWave")

        tex = Text("WaveWaveWaveWaveWave", font_size=36).scale(2)
        self.add(tex)

        render.play(ApplyWave(tex))
        render.play(ApplyWave(tex, direction=RIGHT, time_width=0.5, amplitude=0.3))
        render.play(ApplyWave(tex, rate_func=linear, ripples=4))
        render.play(Wait(1.5))
        render.close()


class DemoBlinking(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Blink")

        text = Text("Blinking", font_size=36).scale(1.5)
        self.add(text)

        render.play(Blink(text, blinks=3))
        render.play(Wait(1.5))
        render.close()


class DemoCircumscribe(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Circumscribe")

        lbl = Text("Circum-\nscribe", font_size=36).scale(2)
        self.add(lbl)

        render.play(Circumscribe(lbl))
        render.play(Circumscribe(lbl, Circle))
        render.play(Circumscribe(lbl, fade_out=True))
        render.play(Circumscribe(lbl, time_width=2))
        render.play(Circumscribe(lbl, Circle, True))
        render.play(Wait(1.5))
        render.close()


class DemoUsingIndicate(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Indicate")

        tex = Text("Indicate", font_size=36).scale(3)
        self.add(tex)

        render.play(Indicate(tex))
        render.play(Wait(1.5))
        render.close()


class DemoUsingFlash(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Flash")

        dot = Dot(color=PURE_YELLOW).shift(DOWN)
        self.add(Text("Flash the dot below:"), dot)
        render.play(Flash(dot))
        render.play(Wait(1.5))
        render.close()


class DemoFlashOnCircle(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Flash on Circle")
        radius = 2
        circle = Circle(radius)
        self.add(circle)
        render.play(Flash(
            circle, line_length=1,
            num_lines=30, color=RED,
            flash_radius=radius + SMALL_BUFF,
            time_width=0.3, run_time=2,
            rate_func=rush_from,
        ))
        render.play(Wait(1.5))
        render.close()


class DemoFocusOn(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FocusOn")
        dot = Dot(color=PURE_YELLOW).shift(DOWN)
        self.add(Text("Focusing on the dot below:"), dot)
        anim = FocusOn(dot, run_time=1, opacity=3.0)
        anim.mobject.move_to(dot.get_center())
        render.play(anim)
        render.play(Wait(1.5))
        render.close()


class DemoTimeWidthValues(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        p = RegularPolygon(5, color=DARK_GRAY, stroke_width=6).scale(3)
        self.add(p)

        p = p.copy().set_color(BLUE)

        for time_width in [0.2, 0.5, 1, 2]:
            lbl = Text(f"time_width={time_width:.1f}", font_size=36)
            self.add(lbl)
            render.play(ShowPassingFlash(p.copy().set_color(BLUE), run_time=2, time_width=time_width))
            self.remove(lbl)

        render.play(Wait(1.5))
        render.close()


class DemoHomotopy(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        square = Square()
        self.add(square)

        def homotopy(x, y, z, t):
            if t <= 0.25:
                progress = t / 0.25
                return (x, y + progress * 0.2 * np.sin(x), z)
            else:
                wave_progress = (t - 0.25) / 0.75
                return (x, y + 0.2 * np.sin(x + 10 * wave_progress), z)

        render.play(Homotopy(homotopy, square, rate_func=linear, run_time=2))
        render.play(Wait(1.5))
        render.close()

class DemoMoveAlongPath(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))

        d1 = Dot().set_color(ORANGE)
        l1 = Line(LEFT, RIGHT)
        l2 = Line(LEFT, LEFT + UP * 0.001).set_color(ORANGE).set_stroke(width=6)
        l2.add_updater(lambda m: m.put_start_and_end_on(LEFT, d1.get_center()))
        self.add(d1, l1, l2)

        render.play(MoveAlongPath(d1, l1), rate_func=linear)
        render.play(Wait(1.5))
        render.close()


class DemoWiggle(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Wiggle")
        tex = Text("Wiggle").scale(3)
        self.add(tex)
        render.play(Wiggle(tex))
        render.play(Wait(1.5))
        render.close()


class DemoChangeDecimalToValue(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "ChangeDecimalToValue")
        number = TextDecimalNumber(0, font_size=48)
        self.add(number)
        render.play(ChangeDecimalToValue(number, 10, run_time=3))
        render.play(Wait(1))
        render.close()


class DemoUsingRotate(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Rotate")
        top_sq = Square(side_length=0.5).shift(UP * 2)
        bot_sq = Square(side_length=0.5)
        self.add(top_sq, bot_sq)
        render.play(
            Rotate(
                VGroup(top_sq, bot_sq),
                angle=2*PI,
                about_point=ORIGIN,
                rate_func=linear,
            ),
        )
        render.play(Wait(1))
        render.close()


class DemoRotatingAbout(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        circle = Circle(radius=1, color=BLUE)
        line = Line(start=ORIGIN, end=RIGHT)
        arrow = Arrow(start=ORIGIN, end=RIGHT, buff=0, color=GOLD)
        vg = VGroup(circle, line, arrow)
        self.add(vg)
        anim_kw = {"about_point": arrow.get_start(), "run_time": 1}
        render.play(Rotating(arrow, 180 * DEGREES, **anim_kw))
        render.play(Rotating(arrow, PI, **anim_kw))
        render.play(Rotating(vg, PI, about_point=RIGHT))
        render.play(Rotating(vg, PI, axis=UP, about_point=ORIGIN))
        render.play(Rotating(vg, PI, axis=RIGHT, about_edge=UP))
        render.play(vg.animate.move_to(ORIGIN))
        render.close()


class DemoChangingDecimal(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "ChangingDecimal")
        number = TextDecimalNumber(0, font_size=48)
        self.add(number)
        render.play(ChangingDecimal(number, lambda a: 5 * a, run_time=3))
        render.play(Wait(1))
        render.close()


class BroadcastExample(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(1))
        mob = Circle(radius=4, color=TEAL_A)
        render.play(Broadcast(mob))
        render.play(Wait(1))
        render.close()


class SpeedModifierExample(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        a = Dot().shift(LEFT * 4)
        b = Dot().shift(RIGHT * 4)
        self.add(a, b)
        render.play(Wait(0.5))
        render.play(
            ChangeSpeed(
                AnimationGroup(
                    a.animate(run_time=1).shift(RIGHT * 8),
                    b.animate(run_time=1).shift(LEFT * 8),
                ),
                speedinfo={0.3: 1, 0.4: 0.1, 0.6: 0.1, 1: 1},
                rate_func=linear,
            )
        )
        render.play(Wait(1))
        render.close()


class SpeedModifierUpdaterExample(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        a = Dot().shift(LEFT * 4)
        self.add(a)

        ChangeSpeed.add_updater(a, lambda x, dt: x.shift(RIGHT * 4 * dt))
        render.play(
            ChangeSpeed(
                Wait(2),
                speedinfo={0.4: 1, 0.5: 0.2, 0.8: 0.2, 1: 1},
                affects_speed_updaters=True,
            )
        )
        render.close()


class SpeedModifierUpdaterExample2(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        a = Dot().shift(LEFT * 4)
        self.add(a)

        ChangeSpeed.add_updater(a, lambda x, dt: x.shift(RIGHT * 4 * dt))
        render.play(Wait(1.0))
        render.play(
            ChangeSpeed(
                Wait(),
                speedinfo={1: 0},
                affects_speed_updaters=True,
            )
        )
        render.close()


class ApplyMatrixExample(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        matrix = [[1, 1], [0, 2/3]]
        render.play(ApplyMatrix(matrix, Text("Hello World!")), ApplyMatrix(matrix, NumberPlane()))
        render.play(Wait(1))
        render.close()


class WarpSquare(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        square = Square()
        render.play(
            ApplyPointwiseFunction(
                lambda point: complex_to_R3(np.exp(R3_to_complex(point))), square
            )
        )
        render.play(Wait(1))
        render.close()


class ClockwiseExample(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        dl, dr = Dot(), Dot()
        sl, sr = Square(), Square()

        VGroup(dl, sl).arrange(DOWN).shift(2*LEFT)
        VGroup(dr, sr).arrange(DOWN).shift(2*RIGHT)

        self.add(dl, dr)
        render.play(Wait(1.0))
        render.play(
            ClockwiseTransform(dl, sl),
            Transform(dr, sr)
        )
        render.play(Wait(1.0))
        render.close()

# do not change the code here
class CounterclockwiseTransform_vs_Transform(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        c_transform = VGroup(
            TextDecimalNumber(number=3.141, num_decimal_places=3),
            TextDecimalNumber(number=1.618, num_decimal_places=3)
        )
        text_1 = Text("CounterclockwiseTransform", color=RED)
        c_transform.add(text_1)

        transform = VGroup(
            TextDecimalNumber(number=1.618, num_decimal_places=3),
            TextDecimalNumber(number=3.141, num_decimal_places=3)
        )
        text_2 = Text("Transform", color=BLUE)
        transform.add(text_2)

        ints = VGroup(c_transform, transform)
        texts = VGroup(text_1, text_2).scale(0.75)
        c_transform.arrange(direction=UP, buff=1)
        transform.arrange(direction=UP, buff=1)

        ints.arrange(buff=2)
        self.add(ints, texts)

        render.play(CounterclockwiseTransform(c_transform[0], c_transform[1]))
        render.play(_ManimTransform(transform[0], transform[1]))
        render.play(Wait(1.0))
        render.close()


class DemoCyclicReplace(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "CyclicReplace")
        group = VGroup(Square(), Circle(), Triangle(), Star())
        group.arrange(RIGHT)
        self.add(group)
        for _ in range(4):
            render.play(CyclicReplace(*group))
            render.play(Wait(0.5))
        render.play(Wait(1))
        render.close()


class DemoFadeToColor(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FadeToColor")
        render.play(FadeToColor(Text("Hello World!"), color=RED))
        render.play(Wait(1))
        render.close()


class DemoDifferentFadeTransforms(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FadeTransform")
        starts = [Rectangle(width=4, height=1) for _ in range(3)]
        VGroup(*starts).arrange(DOWN, buff=1).shift(3*LEFT)
        targets = [Circle(fill_opacity=1).scale(0.25) for _ in range(3)]
        VGroup(*targets).arrange(DOWN, buff=1).shift(3*RIGHT)
        self.add(*starts)
        render.play(Wait(0.5))
        render.play(
            FadeTransform(starts[0], targets[0], stretch=True),
            FadeTransform(starts[1], targets[1], stretch=False, dim_to_match=0),
            FadeTransform(starts[2], targets[2], stretch=False, dim_to_match=1),
        )
        render.play(Wait(1))
        render.close()


class DemoFadeTransformPieces(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "FadeTransformPieces")
        src = VGroup(Square(), Circle().shift(LEFT + UP))
        src.shift(3*LEFT + 2*UP)
        src_copy = src.copy().shift(4*DOWN)
        target = VGroup(Circle(), Triangle().shift(RIGHT + DOWN))
        target.shift(3*RIGHT + 2*UP)
        target_copy = target.copy().shift(4*DOWN)
        self.add(src, src_copy)
        render.play(Wait(0.5))
        render.play(
            FadeTransform(src, target),
            FadeTransformPieces(src_copy, target_copy),
        )
        render.play(Wait(1))
        render.close()


class DemoMoveToTarget(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "MoveToTarget")

        c = Circle()
        self.add(c)

        c.generate_target()
        c.target.set_fill(color=GREEN, opacity=0.5)
        c.target.shift(2 * RIGHT + UP).scale(0.5)

        render.play(MoveToTarget(c))
        render.play(Wait(1.5))
        render.close()


class DemoReplacementTransformOrTransform(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self

        r_transform = VGroup(*[TextDecimalNumber(number=i, num_decimal_places=0) for i in range(1,4)])
        text_1 = Text("ReplacementTransform", color=RED)
        r_transform.add(text_1)

        transform = VGroup(*[TextDecimalNumber(number=i, num_decimal_places=0) for i in range(4,7)])
        text_2 = Text("Transform", color=BLUE)
        transform.add(text_2)

        ints = VGroup(r_transform, transform)
        texts = VGroup(text_1, text_2).scale(0.75)
        r_transform.arrange(direction=UP, buff=1)
        transform.arrange(direction=UP, buff=1)

        ints.arrange(buff=2)
        self.add(ints, texts)

        render.play(ReplacementTransform(r_transform[0], r_transform[1]))
        render.play(ReplacementTransform(r_transform[2], texts[0]))

        render.play(Transform(transform[0], transform[1]))
        render.play(Transform(transform[1], transform[2]))
        render.play(Wait(1.0))
        render.close()


class DemoRestore(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Restore")

        s = Square()
        s.save_state()
        self.add(s)
        render.play(FadeIn(s))
        render.play(s.animate.set_color(PURPLE).set_opacity(0.5).shift(2 * LEFT).scale(3))
        render.play(s.animate.shift(5 * DOWN).rotate(PI / 4))
        render.play(Wait(0.5))
        render.play(Restore(s), run_time=2)
        render.play(Wait(1.0))
        render.close()


class DemoScaleInPlace(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "ScaleInPlace")

        t = Text("Hello World!")
        self.add(t)
        render.play(ScaleInPlace(t, 2))
        render.play(Wait(1.0))
        render.close()


class DemoShrinkToCenter(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "ShrinkToCenter")

        t = Text("Hello World!")
        self.add(t)
        render.play(ShrinkToCenter(t))
        render.play(Wait(1.0))
        render.close()


class DemoTransformPathArc(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "TransformPathArc")

        def make_arc_path(start, end, arc_angle):
            points = []
            p_fn = path_along_arc(arc_angle)
            for alpha in range(0, 11):
                points.append(p_fn(start, end, alpha / 10.0))
            path = VMobject(stroke_color=YELLOW)
            path.set_points_smoothly(points)
            return path

        left = Circle(stroke_color=BLUE_E, fill_opacity=1.0, radius=0.5).move_to(LEFT * 2)
        colors = [TEAL_A, TEAL_B, TEAL_C, TEAL_D, TEAL_E, GREEN_A]
        examples = [-90, 0, 30, 90, 180, 270]
        anims = []
        for idx, angle in enumerate(examples):
            left_c = left.copy().shift((3 - idx) * UP)
            left_c.fill_color = colors[idx]
            right_c = left_c.copy().shift(4 * RIGHT)
            path_arc = make_arc_path(left_c.get_center(), right_c.get_center(),
                                     arc_angle=angle * DEGREES)
            desc = Text('%d°' % examples[idx]).next_to(left_c, LEFT)
            self.add(
                path_arc.set_z_index(1),
                desc.set_z_index(2),
                left_c.set_z_index(3),
            )
            anims.append(Transform(left_c, right_c, path_arc=angle * DEGREES))

        render.play(*anims, run_time=2)
        render.play(Wait(1.0))
        render.close()


class DemoAnagram(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "TransformMatchingShapes Anagram")

        src = Text("the morse code")
        tar = Text("here come dots")
        self.add(src)
        render.play(Write(src))
        render.play(Wait(0.5))
        render.play(TransformMatchingShapes(src, tar, path_arc=PI / 2))
        render.play(Wait(0.5))
        render.close()


class DemoMatchingEquationParts(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "TransformMatchingTex")

        variables = VGroup(MathTex("a"), MathTex("b"), MathTex("c")).arrange(RIGHT).shift(UP)

        eq1 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2")
        eq2 = MathTex("{{a}}^2", "+", "{{b}}^2", "=", "{{c}}^2")
        eq3 = MathTex("{{a}}^2", "=", "{{b}}^2", "-", "{{c}}^2")

        self.add(eq1)
        render.play(Wait(0.5))
        render.play(TransformMatchingTex(Group(eq1, variables), eq2))
        render.play(Wait(0.5))
        render.play(TransformMatchingTex(eq2, eq3))
        render.play(Wait(0.5))
        render.close()

class DemoTangentAnimation(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "TangentLine - sliding tangent")

        ax = Axes(
            x_range=[-7, 7, 1],
            y_range=[-4, 4, 1],
            x_length=8,
            y_length=5,
            axis_config={"include_tip": True, "font_size": 24},
        )
        sine = ax.plot(np.sin, color=RED)
        alpha = ValueTracker(0)
        point = always_redraw(
            lambda: Dot(
                sine.point_from_proportion(alpha.get_value()),
                color=BLUE
            )
        )
        tangent = always_redraw(
            lambda: TangentLine(
                sine,
                alpha=alpha.get_value(),
                color=YELLOW,
                length=4,
            )
        )
        self.add(ax, sine, point, tangent)
        render.play(alpha.animate.set_value(1), rate_func=linear, run_time=3)
        render.play(Wait(1.0))
        render.close()


class DemoLatexWithoutLatex(Scene):
    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "All LaTeX commands")

        FS = 28

        def sym(s):
            return MathTex(s, font_size=FS)

        def vg(*strings):
            return VGroup(*[sym(t) for t in strings]).arrange(RIGHT, buff=0.3)

        def stacked(*rows):
            return VGroup(*rows).arrange(DOWN, buff=0.35)

        _R = chr(92)
        _ra = _R + "rangle"
        _rf = _R + "rfloor"
        _rc = _R + "rceil"
        _ri = _R + "right"
        _rar = _R + "rightarrow"
        _rrp = _R + "rightleftharpoons"

        # Each pair: (group_A, group_B) where each symbol is its own MathTex
        # TransformMatchingTex will morph symbol-by-symbol

        pairs = []
        W = max  # width placeholder — ignore

        # 1. Greek lowercase → uppercase
        greek_low = ["\\alpha","\\beta","\\gamma","\\delta","\\epsilon","\\zeta","\\eta","\\theta"]
        greek_low2 = ["\\iota","\\kappa","\\lambda","\\mu","\\nu","\\xi","\\pi","\\rho"]
        greek_low3 = ["\\sigma","\\tau","\\upsilon","\\phi","\\chi","\\psi","\\omega",
                      "\\varepsilon"]
        greek_up = ["\\Gamma","\\Delta","\\Theta","\\Lambda","\\Xi","\\Pi","\\Sigma",
                    "\\Upsilon"]
        greek_up2 = ["\\Phi","\\Psi","\\Omega","\\aleph","\\beth","\\daleth","\\gimel",
                     "\\digamma"]
        g1 = stacked(vg(*greek_low), vg(*greek_low2), vg(*greek_low3))
        g2 = stacked(vg(*greek_up), vg(*greek_up2)).move_to(g1)
        pairs.append((g1, g2))

        # 2. Structures: frac→sqrt→overbrace→binom→int
        s1 = stacked(
            vg(r"\frac{a}{b}", r"\sqrt{x}", r"\sqrt[n]{x}"),
            vg(r"\overline{AB}", r"\underline{CD}"),
            vg(r"\overrightarrow{EF}", r"\hat{x}", r"\tilde{y}"),
        )
        s2 = stacked(
            vg(r"\overbrace{a+b+c}", r"\underbrace{x+y+z}"),
            vg(r"\frac{\partial f}{\partial x}", r"\frac{d}{dx}"),
            vg(r"\binom{n}{k}", r"\int_a^b f(x)\,dx"),
        ).move_to(s1)
        pairs.append((s1, s2))

        # 3. Delimiters
        d1 = stacked(
            vg("|x|", r"\Vert x\Vert", "\\langle x" + _ra),
            vg("\\{x\\}", "\\lfloor x" + _rf, "\\lceil x" + _rc),
            vg(r"\backslash", r"\uparrow", r"\downarrow"),
        )
        d2 = stacked(
            vg("\\left(\\frac{a}{b}" + _ri + ")", "\\left[\\frac{a}{b}" + _ri + "]"),
            vg("\\left\\{\\frac{a}{b}" + _ri + "\\}", "\\left|\\frac{a}{b}" + _ri + "|"),
            vg(r"\Uparrow", r"\Downarrow", r"\Updownarrow"),
        ).move_to(d1)
        pairs.append((d1, d2))

        # 4. Large operators
        o1 = stacked(
            vg(r"\sum_{i=1}^n i", r"\prod_{i=1}^n i"),
            vg(r"\int_0^\infty", r"\oint", r"\iint", r"\iiint"),
            vg(r"\bigcap", r"\bigcup", r"\bigsqcup", r"\bigvee", r"\bigwedge"),
        )
        o2 = stacked(
            vg(r"\coprod", r"\biguplus", r"\bigoplus", r"\bigotimes", r"\bigodot"),
            vg(r"\sum\nolimits_{i=1}^n", r"\int\nolimits_0^1"),
            vg(r"\displaystyle\sum_{i=1}^\infty \frac{1}{i^2} = \frac{\pi^2}{6}"),
        ).move_to(o1)
        pairs.append((o1, o2))

        # 5. Functions
        f1 = stacked(
            vg(r"\sin x", r"\cos x", r"\tan x"),
            vg(r"\arcsin x", r"\arccos x", r"\arctan x"),
            vg(r"\sinh x", r"\cosh x", r"\tanh x"),
        )
        f2 = stacked(
            vg(r"\lim_{x\to 0}\frac{\sin x}{x}=1", r"\limsup", r"\liminf"),
            vg(r"\log x", r"\ln x", r"\lg x", r"\exp x"),
            vg(r"\max", r"\min", r"\sup", r"\inf", r"\gcd", r"\det", r"\dim", r"\ker",
               r"\arg", r"\deg", r"\Pr"),
        ).move_to(f1)
        pairs.append((f1, f2))

        # 6. Binary ops → relations
        b1 = stacked(
            vg(r"\pm", r"\mp", r"\times", r"\div", r"\ast", r"\star", r"\cdot"),
            vg(r"\circ", r"\bullet", r"\oplus", r"\ominus", r"\otimes", r"\odot"),
            vg(r"\cap", r"\cup", r"\sqcap", r"\sqcup", r"\wedge", r"\vee"),
        )
        b2 = stacked(
            vg(r"\leq", r"\geq", r"\ll", r"\gg", r"\equiv", r"\sim", r"\simeq"),
            vg(r"\approx", r"\cong", r"\neq", r"\doteq", r"\propto", r"\prec", r"\succ"),
            vg(r"\subset", r"\supset", r"\subseteq", r"\supseteq", r"\in", r"\ni", r"\notin"),
        ).move_to(b1)
        pairs.append((b1, b2))

        # 7. More relations → negations
        r1 = stacked(
            vg(r"\mid", r"\parallel", r"\nmid", r"\nparallel", r"\perp", r"\bowtie", r"\Join"),
            vg(r"\vdash", r"\dashv", r"\models", r"\Vdash", r"\vDash", r"\Vvdash"),
            vg(r"\lll", r"\ggg", r"\preceq", r"\succeq", r"\precsim", r"\succsim"),
        )
        r2 = stacked(
            vg(r"\nsim", r"\ncong", r"\nleq", r"\ngeq", r"\nprec", r"\nsucc", r"\nsupseteq"),
            vg(r"\lneqq", r"\gneqq", r"\lnsim", r"\gnsim", r"\lvertneqq", r"\gvertneqq"),
            vg(r"\ntriangleleft", r"\ntriangleright", r"\nVDash", r"\nvDash", r"\nvdash"),
        ).move_to(r1)
        pairs.append((r1, r2))

        # 8. Arrows
        a1 = stacked(
            vg("\\leftarrow" + _rar, "\\leftrightarrow"),
            vg(r"\Leftarrow", r"\Rightarrow", r"\Leftrightarrow"),
            vg(r"\longleftarrow", r"\longrightarrow", r"\longleftrightarrow"),
        )
        a2 = stacked(
            vg(r"\mapsto", r"\longmapsto", r"\hookrightarrow", r"\hookleftarrow"),
            vg(r"\uparrow", r"\downarrow", r"\updownarrow", r"\Uparrow", r"\Downarrow", r"\Updownarrow"),
            vg("\\nLeftarrow", "\\nRightarrow", "\\nLeftrightarrow" + _rrp),
        ).move_to(a1)
        pairs.append((a1, a2))

        # 9. Misc symbols
        m1 = stacked(
            vg(r"\infty", r"\forall", r"\exists", r"\nexists", r"\emptyset", r"\varnothing"),
            vg(r"\nabla", r"\partial", r"\eth", r"\angle", r"\measuredangle"),
            vg(r"\triangle", r"\triangledown", r"\vartriangle", r"\lozenge", r"\blacklozenge"),
        )
        m2 = stacked(
            vg(r"\cdots", r"\vdots", r"\ddots", r"\ldots", r"\prime", r"\sharp", r"\flat"),
            vg(r"\natural", r"\surd", r"\hbar", r"\ell", r"\wp", r"\imath", r"\jmath"),
            vg(r"\clubsuit", r"\diamondsuit", r"\heartsuit", r"\spadesuit", r"\bigstar"),
        ).move_to(m1)
        pairs.append((m1, m2))

        # 10. More misc → blackboard
        mm1 = stacked(
            vg(r"\Game", r"\Finv", r"\Bbbk", r"\circledS", r"\complement"),
            vg(r"\blacksquare", r"\square", r"\blacktriangle", r"\blacktriangledown"),
            vg(r"\Re", r"\Im", r"\mho", r"\hslash", r"\backprime"),
        )
        mm2 = stacked(
            vg(r"\mathbb{R}", r"\mathbb{C}", r"\mathbb{N}", r"\mathbb{Z}", r"\mathbb{Q}"),
            vg(r"\mathcal{A}", r"\mathcal{B}", r"\mathcal{C}", r"\mathcal{D}", r"\mathcal{E}"),
            vg(r"\mathfrak{A}", r"\mathfrak{B}", r"\mathfrak{C}", r"\mathfrak{D}", r"\mathfrak{E}"),
        ).move_to(mm1)
        pairs.append((mm1, mm2))

        # 11. Accents
        ac1 = stacked(
            vg(r"\hat{x}", r"\tilde{x}", r"\bar{x}", r"\vec{x}", r"\dot{x}", r"\ddot{x}"),
            vg(r"\acute{x}", r"\grave{x}", r"\check{x}", r"\breve{x}"),
        )
        ac2 = stacked(
            vg(r"\widehat{abc}", r"\widetilde{abc}", r"\overline{abc}"),
            vg(r"\Hat{x}", r"\Tilde{x}", r"\Bar{x}", r"\Vec{x}", r"\Dot{x}", r"\Ddot{x}"),
            vg(r"\Acute{x}", r"\Grave{x}", r"\Check{x}", r"\Breve{x}", r"\underrightarrow{abc}"),
        ).move_to(ac1)
        pairs.append((ac1, ac2))

        # 12. Arrays + matrices
        arr1 = stacked(
            vg(r"\begin{array}{cc} a & b \\ c & d \end{array}"),
            vg(r"\begin{array}{|c|c|} x & y \\ z & w \end{array}"),
        )
        arr2 = stacked(
            vg(r"\begin{pmatrix} a & b \\ c & d \end{pmatrix}"),
            vg(r"\begin{bmatrix} x & y \\ z & w \end{bmatrix}"),
        ).move_to(arr1)
        pairs.append((arr1, arr2))

        # 13. Fonts
        ft1 = stacked(
            vg(r"\mathbf{A}", r"\mathbf{B}", r"\mathbf{C}"),
            vg(r"\mathsf{A}", r"\mathsf{B}", r"\mathsf{C}"),
        )
        ft2 = stacked(
            vg(r"\textbf{ABC}", r"\textit{ABC}", r"\texttt{ABC}"),
            vg(r"\underline{ABC}", r"\overline{ABC}"),
        ).move_to(ft1)
        pairs.append((ft1, ft2))

        center = ORIGIN + UP * 0.3
        for sa, sb in pairs:
            sa.move_to(center)
            sb.move_to(center)

        page_names = [
            "1/13 Greek & Hebrew", "2/13 Structures", "3/13 Delimiters",
            "4/13 Large operators", "5/13 Functions", "6/13 Binary ops → Relations",
            "7/13 Relations → Negations", "8/13 Arrows", "9/13 Misc symbols",
            "10/13 Misc → Blackboard", "11/13 Accents", "12/13 Arrays & matrices",
            "13/13 Fonts",
        ]
        page_label = Text(page_names[0], font_size=20, fill_color=GREY).to_edge(DOWN, buff=0.3)
        self.add(page_label)

        self.add(pairs[0][0])
        render.play(Wait(0.5))

        for i, ((sa, sb), (na, _)) in enumerate(zip(pairs, pairs[1:] + pairs[:1])):
            next_label = Text(page_names[(i + 1) % 13], font_size=20, fill_color=GREY).to_edge(DOWN, buff=0.3)
            render.play(TransformMatchingTex(sa, sb, run_time=0.8))
            render.play(Wait(0.1))
            render.play(TransformMatchingTex(sb, na, run_time=0.8))
            self.remove(page_label)
            self.add(next_label)
            page_label = next_label
            render.play(Wait(0.1))

        render.play(Wait(1.5))
        render.close()


class DemoFourierTransform(Scene):
    """Epicycles tracing a heart via Fourier series — 20 harmonics."""

    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Fourier Transform — Epicycles")

        # ── 1. Heart path DFT ─────────────────────────────────────
        N = 256
        t = np.linspace(0, 2 * np.pi, N, endpoint=False)
        x = 16 * np.sin(t) ** 3
        y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
        pts = (x + 1j * y) / 22  # scale to ~2-unit span

        coeffs = np.fft.fft(pts) / N
        order = np.argsort(-np.abs(coeffs))
        coeffs, freqs = coeffs[order], order - N // 2

        K = 20
        coeffs, freqs = coeffs[:K], freqs[:K]
        span = float(np.sum(np.abs(coeffs))) * 2.2
        coeffs = (coeffs / span) * 3.5  # normalize visual span

        # ── 2. Build epicycle components ──────────────────────────
        colors = color_gradient([BLUE_E, PURPLE_E, RED_E, ORANGE, YELLOW], K)
        circles, arms = [], []
        for i in range(K):
            c = Circle(radius=0.08, color=colors[i], stroke_width=1.0)
            c.set_fill(colors[i], opacity=0.08)
            circles.append(c)
            arms.append(Line(ORIGIN, RIGHT * 0.1, color=colors[i], stroke_width=1.5))

        pen = Dot(radius=0.06, color=WHITE)
        trace = TracedPath(pen.get_center, stroke_color=YELLOW, stroke_width=2.5)

        epi = VGroup(*circles, *arms, pen)
        self.add(epi, trace)

        # ── 3. Updater ────────────────────────────────────────────
        start_t = time.time()
        period = 8.0

        def updater(g, dt):
            elapsed = time.time() - start_t
            pos = np.array([0.0, 0.0, 0.0])
            for i in range(K):
                mag = float(np.abs(coeffs[i]))
                phi = (2 * np.pi * float(freqs[i]) * elapsed / period
                       + float(np.angle(coeffs[i])))
                tip = pos + np.array([mag * np.cos(phi), mag * np.sin(phi), 0.0])
                circles[i].move_to(pos)
                arms[i].set_points_as_corners([pos, tip])
                pos = tip
            pen.move_to(pos)

        epi.add_updater(updater)

        # ── 4. Animate ────────────────────────────────────────────
        render.play(Wait(period + 1))
        epi.clear_updaters()
        render.play(Wait(1.0))
        render.close()


class DemoLorenzButterfly(Scene):
    """Lorenz attractor — 5 particles, rotating view, dissipating trails."""

    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Lorenz Attractor")

        # ── Lorenz params ──────────────────────────────────────────
        sigma, rho, beta = 10.0, 28.0, 8 / 3
        dt, N = 0.0015, 40000
        num_parts = 5
        run_time = 20.0

        # ── Seeds (butterfly effect!) ──────────────────────────────
        base = np.array([-8.0, 8.0, 27.0])
        rng = np.random.RandomState(42)
        seeds = [base + rng.normal(0, 0.25, 3) for _ in range(num_parts)]

        # ── Pre-compute trajectories ───────────────────────────────
        all_3d = []
        for start in seeds:
            path = [start.copy()]
            p = start.copy()
            for _ in range(N - 1):
                dx = sigma * (p[1] - p[0])
                dy = p[0] * (rho - p[2]) - p[1]
                dz = p[0] * p[1] - beta * p[2]
                p = p + np.array([dx, dy, dz]) * dt
                path.append(p.copy())
            all_3d.append(np.array(path))

        # ── Color palette ──────────────────────────────────────────
        colors = [BLUE_D, TEAL_D, PURPLE_D, MAROON_D, GOLD_D]

        # ── Dots, glows & trails ───────────────────────────────────
        dots, glows, traces = [], [], []
        for i in range(num_parts):
            d = Dot(radius=0.05, color=colors[i])
            g = Circle(radius=0.18, color=colors[i],
                       fill_opacity=0.06, stroke_width=0)
            t = TracedPath(d.get_center, stroke_color=colors[i],
                           stroke_width=1.6, dissipating_time=4.0)
            dots.append(d)
            glows.append(g)
            traces.append(t)
            self.add(d, g, t)

        # ── Updaters ───────────────────────────────────────────────
        start_t = time.time()

        for i in range(num_parts):
            _traj = all_3d[i]
            _glow = glows[i]

            def updater(d, _i=i):
                elapsed = time.time() - start_t
                frac = min(elapsed / run_time, 1.0)
                ang = frac * np.pi * 2
                fidx = frac * (N - 1)
                lo = int(fidx)
                hi = min(lo + 1, N - 1)
                t = fidx - lo
                p = _traj[lo] * (1 - t) + _traj[hi] * t
                c, s = np.cos(ang), np.sin(ang)
                rx = p[0] * c - p[1] * s
                ry = p[0] * s + p[1] * c
                sx = rx * 0.11
                sy = (ry * 0.3 + p[2] * 0.8) * 0.09
                pos = np.array([sx, sy, 0.0])
                d.move_to(pos)
                _glow.move_to(pos)

            dots[i].add_updater(updater)

        # ── Animate ────────────────────────────────────────────────
        render.play(Wait(run_time + 1))
        for d in dots:
            d.clear_updaters()
        render.play(Wait(1.0))
        render.close()


class DemoWriteLatex(Scene):
    """Write on LaTeX mobjects — exercises the progressive glyph reveal.

    Previously Write on a MathTex popped the whole equation in fully filled
    (the container fill was set, but the actual fill lives on the nested SVG
    glyph leaves).  This scene verifies the outline-then-fill reveal works.
    """

    def construct(self):
        render = MLWindow(1920, 1080)
        render.scene = self
        render.play(Wait(2.0))
        _title(render, "Write on LaTeX")

        # Single-part equation (one MathTexPart, several glyph leaves)
        eq1 = MathTex("x^2 + y^2", font_size=56).shift(UP * 1.5)
        render.play(Write(eq1, run_time=0.8))
        render.play(Wait(1.0))

        # Multi-part equation — Write staggers across the parts
        eq2 = MathTex(r"\frac{a}{b} + \sqrt{c}", font_size=56).shift(DOWN * 1.5)
        render.play(Write(eq2, run_time=0.8))
        render.play(Wait(1.5))
        render.close()


# ====================================================================
# Download all demo scenes to MP4 (mss screen capture)
# Run: python scenes/demo_scene.py
# ====================================================================
if __name__ == "__main__":
    import os, time, subprocess, tempfile, threading, shutil, ctypes, ctypes.wintypes as wt
    import mss
    from PIL import Image

    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(os.path.dirname(PROJECT_DIR), "downloaded_videos")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    user32 = ctypes.windll.user32
    _rec_state = [None, None, None, 0, None, None, ""]  # stop, thread, dir, count, mon, sct, path

    def find_win():
        h = user32.FindWindowW(None, "Real Time Manim")
        if not h: return None
        r = wt.RECT(); user32.GetClientRect(h, ctypes.byref(r))
        pt = wt.POINT(0, 0); user32.ClientToScreen(h, ctypes.byref(pt))
        return {"left": pt.x, "top": pt.y, "width": r.right, "height": r.bottom}

    _orig_init = MLWindow.__init__
    _orig_close = MLWindow.close
    _scene_name, _scene_num = "", 0

    def _rec_init(self, w=1920, h=1080):
        global _scene_name, _scene_num
        _orig_init(self, w, h)
        safe = "".join(c if c.isalnum() or c in "._" else "_" for c in _scene_name)
        _rec_state[6] = os.path.join(OUTPUT_DIR, f"{_scene_num:02d}_{safe}.mp4")
        print(f"[{_scene_num:02d}] {_scene_name}  →  {os.path.basename(_rec_state[6])}")
        time.sleep(0.3)
        mon = find_win()
        if not mon: print("     ⚠ window not found"); return
        _rec_state[4], _rec_state[5] = mon, mss.MSS()
        _rec_state[2] = tempfile.mkdtemp(prefix="mb_rec_")
        _rec_state[3] = 0
        _rec_state[0] = threading.Event()
        def worker():
            idx, iv = 0, 1.0 / 30.0
            while not _rec_state[0].is_set():
                t0 = time.time()
                try:
                    f = _rec_state[5].grab(_rec_state[4])
                    img = Image.frombytes("RGB", f.size, f.bgra, "raw", "BGRX")
                    img.save(os.path.join(_rec_state[2], f"f_{idx:06d}.bmp"))
                    idx += 1
                except: pass
                rem = iv - (time.time() - t0)
                if rem > 0: _rec_state[0].wait(rem)
            _rec_state[3] = idx
        _rec_state[1] = threading.Thread(target=worker, daemon=True)
        _rec_state[1].start()

    def _rec_close(self):
        if _rec_state[0] is not None:
            _rec_state[0].set()
            if _rec_state[1]: _rec_state[1].join(timeout=5)
            total = _rec_state[3]
            if total > 0 and _rec_state[2] and _rec_state[6]:
                p = os.path.join(_rec_state[2], "f_%06d.bmp")
                cmd = ["ffmpeg", "-y", "-framerate", "30", "-i", p,
                       "-c:v", "libx264", "-pix_fmt", "yuv420p",
                       "-crf", "18", "-preset", "fast", _rec_state[6]]
                try:
                    subprocess.run(cmd, check=True, capture_output=True)
                    sz = os.path.getsize(_rec_state[6]) / 1024
                    print(f"     ✓ saved ({total} frames, {sz:.0f} KB)")
                except FileNotFoundError:
                    print("     ✗ ffmpeg not found")
                except subprocess.CalledProcessError as e:
                    print(f"     ✗ ffmpeg: {(e.stderr or b'')[:200]}")
            elif total == 0: print("     ⚠ 0 frames")
            _rec_state[0], _rec_state[1] = None, None
            if _rec_state[5]: _rec_state[5].close(); _rec_state[5] = None
            if _rec_state[2]: shutil.rmtree(_rec_state[2], ignore_errors=True)
            _rec_state[2], _rec_state[3], _rec_state[4], _rec_state[6] = None, 0, None, ""
        _orig_close(self)

    MLWindow.__init__ = _rec_init
    MLWindow.close = _rec_close

    # -- cache helpers --
    TEX_CACHE = os.path.join(os.path.dirname(PROJECT_DIR), "tex_cache")
    media_tex = os.path.join(os.path.dirname(PROJECT_DIR), "media", "Tex")

    def restore_tex():
        if not os.path.exists(TEX_CACHE): return
        os.makedirs(media_tex, exist_ok=True)
        for fn in os.listdir(TEX_CACHE):
            s, d = os.path.join(TEX_CACHE, fn), os.path.join(media_tex, fn)
            if not os.path.exists(d): shutil.copy2(s, d)

    def save_tex():
        if not os.path.exists(media_tex): return
        os.makedirs(TEX_CACHE, exist_ok=True)
        for fn in os.listdir(media_tex):
            s, d = os.path.join(media_tex, fn), os.path.join(TEX_CACHE, fn)
            if not os.path.exists(d): shutil.copy2(s, d)

    def clean_media():
        d = os.path.join(os.path.dirname(PROJECT_DIR), "media")
        if os.path.exists(d):
            for _ in range(3):
                try: shutil.rmtree(d); break
                except: time.sleep(0.5)

    ALL_SCENES = [
        (1, "Create", DemoCreate),
        (2, "Write_Unwrite", DemoWriteUnwrite),
        (3, "Transform", DemoTransform),
        (4, "ReplacementTransform", DemoReplacementTransform),
        (5, "FadeIn_FadeOut", DemoFadeInFadeOut),
        (6, "FadeTransform", DemoFadeTransform),
        (7, "Rotating", DemoRotating),
        (8, "TransformMatchingShapes", DemoTransformMatchingShapes),
        (9, "VGroup", DemoVGroup),
        (10, "AllShapes", DemoAllShapes),
        (11, "Succession", DemoSuccession),
        (12, "FadeInShift", DemoFadeInShift),
        (13, "TextFeatures", DemoTextFeatures),
        (14, "Combined", DemoCombined),
        (15, "DefaultAdd", DemoDefaultAdd),
        (16, "AddWithRunTime", DemoAddWithRunTime),
        (17, "LagRatios", DemoLagRatios),
        (18, "ChangeDefaultAnimation", DemoChangeDefaultAnimation),
        (19, "AnimatedBoundary", DemoAnimatedBoundary),
        (20, "TracedPath", DemoTracedPath),
        (21, "DissipatingPath", DemoDissipatingPath),
        (22, "LaggedStart", DemoLaggedStart),
        (23, "LaggedStartMap", DemoLaggedStartMap),
        (24, "SuccessionDots", DemoSuccessionDots),
        (25, "CreateSquare", DemoCreateSquare),
        (26, "DrawBorderThenFill", DemoDrawBorderThenFill),
        (27, "ShowIncreasingSubsets", DemoShowIncreasingSubsets),
        (28, "SpiralIn", DemoSpiralIn),
        (29, "TypeWithCursor", DemoTypeWithCursor),
        (30, "UntypeWithCursor", DemoUntypeWithCursor),
        (31, "Uncreate", DemoUncreate),
        (32, "Unwrite_RevTrue", DemoUnwriteReverseTrue),
        (33, "Unwrite_RevFalse", DemoUnwriteReverseFalse),
        (34, "ShowWrite", DemoShowWrite),
        (35, "ShowWriteReversed", DemoShowWriteReversed),
        (36, "FadeInExample", DemoFadeInExample),
        (37, "FadeOutExample", DemoFadeOutExample),
        (38, "GrowFromCenter", DemoGrowFromCenter),
        (39, "GrowArrow", DemoGrowArrow),
        (40, "GrowFromEdge", DemoGrowFromEdge),
        (41, "GrowFromPoint", DemoGrowFromPoint),
        (42, "SpinInFromNothing", DemoSpinInFromNothing),
        (43, "ApplyingWaves", DemoApplyingWaves),
        (44, "Blinking", DemoBlinking),
        (45, "Circumscribe", DemoCircumscribe),
        (46, "UsingFlash", DemoUsingFlash),
        (47, "FlashOnCircle", DemoFlashOnCircle),
        (48, "FocusOn", DemoFocusOn),
        (49, "UsingIndicate", DemoUsingIndicate),
        (50, "TimeWidthValues", DemoTimeWidthValues),
        (51, "Wiggle", DemoWiggle),
        (52, "Homotopy", DemoHomotopy),
        (53, "MoveAlongPath", DemoMoveAlongPath),
        (54, "ChangeDecimalToValue", DemoChangeDecimalToValue),
        (55, "ChangingDecimal", DemoChangingDecimal),
        (56, "UsingRotate", DemoUsingRotate),
        (57, "RotatingAbout", DemoRotatingAbout),
        (58, "Broadcast", BroadcastExample),
        (59, "SpeedModifier", SpeedModifierExample),
        (60, "SpeedModifierUpdater", SpeedModifierUpdaterExample),
        (61, "SpeedModifierUpdater2", SpeedModifierUpdaterExample2),
        (62, "ApplyMatrix", ApplyMatrixExample),
        (63, "WarpSquare", WarpSquare),
        (64, "ClockwiseTransform", ClockwiseExample),
        (65, "Counterclockwise", CounterclockwiseTransform_vs_Transform),
        (66, "CyclicReplace", DemoCyclicReplace),
        (67, "FadeToColor", DemoFadeToColor),
        (68, "DifferentFadeTransforms", DemoDifferentFadeTransforms),
        (69, "FadeTransformPieces", DemoFadeTransformPieces),
        (70, "MoveToTarget", DemoMoveToTarget),
        (71, "ReplacementTransformOr", DemoReplacementTransformOrTransform),
        (72, "Restore", DemoRestore),
        (73, "ScaleInPlace", DemoScaleInPlace),
        (74, "ShrinkToCenter", DemoShrinkToCenter),
        (75, "TransformPathArc", DemoTransformPathArc),
        (76, "Anagram", DemoAnagram),
        (77, "MatchingEquationParts", DemoMatchingEquationParts),
        (78, "TangentAnimation", DemoTangentAnimation),
        (79, "LatexWithoutLatex", DemoLatexWithoutLatex),
        (80, "FourierTransform", DemoFourierTransform),
        (81, "LorenzButterfly", DemoLorenzButterfly),
    ]

    print("=" * 55)
    print("  Real Time Manim — Download All Demo Scenes")
    print("=" * 55)
    ok, fail = [], []
    for num, name, cls in ALL_SCENES:
        _scene_name, _scene_num = name, num
        restore_tex()
        try:
            s = cls(); s.construct(); ok.append(name)
        except Exception as e:
            fail.append((name, str(e)))
            print(f"     ✗ ERROR: {e}")
        save_tex(); clean_media(); time.sleep(2.0)
    print(); print(f"  Done: {len(ok)}/{len(ALL_SCENES)}")
    for n, e in fail: print(f"    ✗ {n}: {e[:120]}")
