# ruff: noqa: F403, F405 -- manim-style star imports (from .common / sibling modules)
"""Demo scenes: advanced transforms -- ApplyMatrix, Warp, direction and path-arc
variants, MoveToTarget, Restore and matching shapes.

Split out of the original single-file ``demo_scene.py``; the class
bodies are unchanged.  Re-exported by ``examples.scenes``.
"""
from .common import *  # noqa: F401,F403
from .common import _title, _ManimTransform  # noqa: F401

__all__ = [
    "ApplyMatrixExample", "WarpSquare", "ClockwiseExample",
    "CounterclockwiseTransform_vs_Transform", "DemoCyclicReplace", "DemoFadeToColor",
    "DemoDifferentFadeTransforms", "DemoFadeTransformPieces", "DemoMoveToTarget",
    "DemoReplacementTransformOrTransform", "DemoRestore", "DemoScaleInPlace",
    "DemoShrinkToCenter", "DemoTransformPathArc", "DemoAnagram",
    "DemoMatchingEquationParts", "DemoTangentAnimation"
]


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
