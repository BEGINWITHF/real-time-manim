# ruff: noqa: F401, F403, F405 -- this module is a re-export hub: the demo
# modules do ``from .common import *`` (manim style), so nothing here is unused.
"""Imports and helpers shared by every demo scene module.

The demo modules do ``from .common import *``, so every name the scenes
use at module scope has to live here.
"""
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

