# ruff: noqa: F403, F405 -- manim-style star imports (from .common import *)
"""Demo scenes: attention effects -- waves, Blink, Circumscribe, Flash, Homotopy,
decimal numbers, rotation and the SpeedModifier demos.

Split out of the original single-file ``demo_scene.py``; the class
bodies are unchanged.  Re-exported by ``examples.scenes``.
"""
from .common import *  # noqa: F401,F403
from .common import _title  # noqa: F401

__all__ = [
    "DemoApplyingWaves", "DemoBlinking", "DemoCircumscribe",
    "DemoUsingIndicate", "DemoUsingFlash", "DemoFlashOnCircle", "DemoFocusOn",
    "DemoTimeWidthValues", "DemoHomotopy", "DemoMoveAlongPath", "DemoWiggle",
    "DemoChangeDecimalToValue", "DemoUsingRotate", "DemoRotatingAbout",
    "DemoChangingDecimal", "BroadcastExample", "SpeedModifierExample",
    "SpeedModifierUpdaterExample", "SpeedModifierUpdaterExample2"
]


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
