from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np
from manim import Rectangle, YELLOW
from real_time_manim.animations.succession import Succession
from real_time_manim.animations.wait import Wait
from real_time_manim.animations.fade_in import FadeIn
from real_time_manim.animations.fade_out import FadeOut
from real_time_manim.animations.create import Create
from real_time_manim.animations.uncreate import Uncreate
from real_time_manim.animations.show_passing_flash import ShowPassingFlash


class _LegacyTimeWidth(float):
    """Sentinel default for ``Circumscribe.time_width`` (A20).

    Two requirements meet here:

    * CE parity -- ``manim/animation/indication.py`` draws the frame with
      ``ShowPassingFlash(frame, time_width, run_time)``, i.e. only a
      ``time_width``-wide sliver is lit at any instant and the rest of the
      outline is transparent ("传入 time_width 后画面必须有差别");
    * backward compatibility -- RTM's default render draws the frame
      progressively with ``Create`` and that render must stay byte-identical
      for callers that never pass ``time_width``
      ("保持默认参数下现有渲染结果不变").

    The sentinel is numerically CE's documented default ``0.3`` (so
    ``signature(...).default == 0.3`` and ``repr`` prints ``0.3``) but is
    recognisable by identity: left at its default the legacy ``Create`` draw is
    kept, while any explicitly passed number -- including an explicit ``0.3``,
    the value the wiki sample passes -- takes the CE sliver path.
    """

    def __new__(cls):
        return float.__new__(cls, 0.3)

    def __repr__(self):
        # inspect.signature() prints ``time_width=0.3`` for the sentinel default
        return "0.3"


_LEGACY_TIME_WIDTH = _LegacyTimeWidth()


class Circumscribe(Succession):
    def __init__(self, mobject, shape=Rectangle, fade_in=False, fade_out=False,
                 time_width=_LEGACY_TIME_WIDTH, buff=0.1, color=None, run_time=1.0,
                 stroke_width=4, **kwargs):

        # Kept for introspection/tests; ``None``/the sentinel mean "no sliver".
        self.time_width = time_width

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
            # manim CE parity -- ``manim/animation/indication.py``
            # ``Circumscribe.__init__`` does exactly this, in this order:
            #
            #     elif fade_in:
            #         frame.reverse_direction()
            #         super().__init__(FadeIn(frame, run_time=run_time / 2),
            #                          Uncreate(frame, run_time=run_time / 2))
            #
            # ``reverse_direction()`` (``VMobject``: ``self.points =
            # self.points[::-1]``) flips the contour so the closing ``Uncreate``
            # -- which erases from the END of the point list backwards -- eats
            # the circle back the way it came, from the arc where the FadeIn
            # stopped, instead of from the opposite end.
            #
            # Measured (wiki ``03-动画/强调与提示/assets/RTM output/
            # 02-圈注与聚焦.mp4``, f300, Uncreate at ~0.69 of its window): the
            # signed (RTM - CE) luma map put RTM-only ink on the top /
            # upper-right arc (3 o'clock -> 12 o'clock, the PREFIX of a
            # non-reversed path) and CE-only ink on the lower right (3 o'clock
            # -> ~5:47), i.e. the two rings were mirror images about the 3
            # o'clock radius while agreeing on how much of the circle was left.
            # Only the point order decides that, so it must be fixed here.
            #
            # ``fade_out``/plain branches are deliberately NOT reversed: CE
            # only reverses in this branch.
            frame.reverse_direction()
            animations = [
                FadeIn(frame, run_time=run_time / 2),
                Uncreate(frame, run_time=run_time / 2),
            ]
        elif fade_out:
            animations = [
                Create(frame, run_time=run_time / 2),
                FadeOut(frame, run_time=run_time / 2),
            ]
        elif time_width is None or isinstance(time_width, _LegacyTimeWidth):
            # Legacy render, unchanged: nothing was wired to ``time_width``
            # before, so a caller that does not pass it keeps drawing the frame
            # progressively with ``Create``.
            animations = [
                Create(frame, run_time=run_time),
            ]
        else:
            # CE semantics (indication.py Circumscribe, non-fade branch):
            # Succession(ShowPassingFlash(frame, time_width, run_time)) -- a
            # ``time_width``-wide sliver travels the outline and everything
            # else stays transparent.  Ignored in the fade branches, exactly
            # like CE.
            animations = [
                ShowPassingFlash(frame, float(time_width), run_time=run_time),
            ]

        self._frame = frame
        kwargs.pop('run_time', None)
        total_time = sum(a.run_time for a in animations)
        super().__init__(*animations, run_time=total_time, **kwargs)

    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        if hasattr(self, '_frame') and self._frame in scene.mobjects:
            scene.remove(self._frame)
