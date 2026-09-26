"""Compatibility surface for real-time-manim 2.0.0.

Re-exports **manim's own** animations under the names the renderer and demos
use, so the hand-written ``real_time_manim.animations`` fork can be retired.
Only a handful of names have no manim equivalent and get tiny shims here
(``Wait``, ``Add`` and ``TextDecimalNumber``).

Shared renderer state (mobject opacity/rotation) is re-exported from
``real_time_manim.state`` so a single set of dicts is used everywhere.
"""
from manim import (
    Animation, Group, Text, DecimalNumber,
    Create, Uncreate, DrawBorderThenFill, Write, Unwrite,
    ShowIncreasingSubsets, SpiralIn,
    Blink, TypeWithCursor, UntypeWithCursor,
    Succession, AnimationGroup, MoveToTarget, Indicate,
    FadeIn, FadeOut, FadeTransform, FadeTransformPieces,
    Rotating, Rotate, Transform, ReplacementTransform,
    TransformMatchingShapes, TransformMatchingTex,
    GrowFromCenter, GrowArrow, GrowFromEdge, GrowFromPoint, SpinInFromNothing,
    ApplyWave, Circumscribe, ShowPassingFlash, Homotopy, MoveAlongPath,
)

from real_time_manim.state import (  # noqa: F401  (re-exported on purpose)
    set_anim_opacity, get_anim_opacity,
    set_anim_rotation, get_anim_rotation,
    set_anim_rotation_delta, get_anim_rotation_delta, clear_anim_rotation_delta,
    TARGET_FPS, FRAME_DURATION,
)

try:  # not exported at manim's top level
    from manim.animation.transform_matching_abstract_base import (
        TransformMatchingAbstractBase,
    )
except Exception:  # pragma: no cover - fallback keeps isinstance() working
    class TransformMatchingAbstractBase(Animation):
        pass


class Wait(Animation):
    """A timed hold: an animation with no visual effect.

    manim models a hold as ``Scene.wait``; the renderer's ``play`` takes
    animations, so we provide the same name as a no-op animation.
    """

    def __init__(self, run_time=1.0, **kwargs):
        super().__init__(Group(), run_time=run_time, **kwargs)

    def interpolate_mobject(self, alpha):
        pass


class Add:
    """Makes mobjects visible immediately (not a timed animation).

    ``MLWindow.play`` pulls these out and simply shows their mobjects, matching
    manim's ``add`` semantics.
    """

    def __init__(self, *mobjects, run_time=0.0, **kwargs):
        self.mobjects = list(mobjects)
        self.mobject = mobjects[0] if mobjects else None
        self.run_time = run_time


class TextDecimalNumber(Text):
    """A Text that can swap its digits without re-laying-out the whole line.

    manim's ``DecimalNumber`` renders via ``MathTex`` (needs LaTeX); this uses
    plain ``Text`` glyphs, which the Vulkan renderer draws directly.
    """

    def __init__(self, number=0, font_size=48, font="Times New Roman",
                 num_decimal_places=2, **kwargs):
        self.number = number
        self.num_decimal_places = num_decimal_places
        self._font_size = font_size
        self._font = font
        super().__init__(f"{number:.{num_decimal_places}f}",
                         font_size=font_size, font=font, **kwargs)

    def set_value(self, number):
        self.number = number
        center = self.get_center()
        new = Text(f"{number:.{self.num_decimal_places}f}",
                   font_size=self._font_size, font=self._font)
        self.submobjects = new.submobjects
        self.move_to(center)
        return self
