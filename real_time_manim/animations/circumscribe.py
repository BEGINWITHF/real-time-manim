from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np
from manim import Rectangle, YELLOW
from real_time_manim.animations.succession import Succession
from real_time_manim.animations.wait import Wait
from real_time_manim.animations.fade_in import FadeIn
from real_time_manim.animations.fade_out import FadeOut
from real_time_manim.animations.create import Create
from real_time_manim.animations.uncreate import Uncreate


class Circumscribe(Succession):
    def __init__(self, mobject, shape=Rectangle, fade_in=False, fade_out=False,
                 time_width=0.3, buff=0.1, color=None, run_time=1.0,
                 stroke_width=4, **kwargs):

        if shape is Rectangle:
            from manim import SurroundingRectangle
            frame = SurroundingRectangle(mobject, color=color or YELLOW, buff=buff,
                                         stroke_width=stroke_width)
        else:
            from manim import Circle
            frame = Circle(color=color or YELLOW, stroke_width=stroke_width)
            frame.surround(mobject, buffer_factor=1)
            radius = frame.width / 2
            frame.scale((radius + buff) / radius)

        if fade_in and fade_out:
            animations = [
                FadeIn(frame, run_time=run_time / 2),
                FadeOut(frame, run_time=run_time / 2),
            ]
        elif fade_in:
            animations = [
                FadeIn(frame, run_time=run_time / 2),
                Uncreate(frame, run_time=run_time / 2),
            ]
        elif fade_out:
            animations = [
                Create(frame, run_time=run_time / 2),
                FadeOut(frame, run_time=run_time / 2),
            ]
        else:
            animations = [
                Create(frame, run_time=run_time),
            ]

        self._frame = frame
        kwargs.pop('run_time', None)
        total_time = sum(a.run_time for a in animations)
        super().__init__(*animations, run_time=total_time, **kwargs)

    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        if hasattr(self, '_frame') and self._frame in scene.mobjects:
            scene.remove(self._frame)
