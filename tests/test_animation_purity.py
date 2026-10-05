"""Regression test for the 2.0.0 assumption: manim's animations are pure
functions of alpha, so they can be evaluated out of order for random-access seek.

GPU-free: it only inspects mobject points/fill state.
See docs/2.0.0-time-addressable.md.
"""
import numpy as np
import pytest

from manim import Square, Circle, Text, BLUE, YELLOW, WHITE
from manim.animation.fading import FadeIn, FadeOut
from manim.animation.transform import Transform, ReplacementTransform, FadeTransform
from manim.animation.creation import Create, DrawBorderThenFill, Write
from manim.animation.growing import GrowFromCenter, SpinInFromNothing
from manim.animation.rotation import Rotate, Rotating


def _points(mobs):
    return [m.points.copy() for mob in mobs for m in mob.family_members_with_points()]


def _fills(mobs):
    out = []
    for mob in mobs:
        for m in mob.family_members_with_points():
            try:
                out.append(np.array(m.fill_rgbas, dtype=float).copy())
            except Exception:
                pass
    return out


def _same(xs, ys, tol=1e-9):
    if len(xs) != len(ys):
        return False
    for a, b in zip(xs, ys):
        if a.shape != b.shape or not np.allclose(a, b, atol=tol):
            return False
    return True


CASES = {
    "FadeIn": lambda: (FadeIn(Square(side_length=2)),),
    "FadeOut": lambda: (FadeOut(Square(side_length=2)),),
    "Transform": lambda: (Transform(Square(side_length=2, color=BLUE), Circle(radius=1)),),
    "ReplacementTransform": lambda: (ReplacementTransform(Square(side_length=2), Circle(radius=1)),),
    "Create": lambda: (Create(Square(side_length=2)),),
    "DrawBorderThenFill": lambda: (DrawBorderThenFill(Square(side_length=2)),),
    "Write": lambda: (Write(Text("hi", color=WHITE)),),
    "GrowFromCenter": lambda: (GrowFromCenter(Square(side_length=2)),),
    "SpinInFromNothing": lambda: (SpinInFromNothing(Square(side_length=2)),),
    "Rotate": lambda: (Rotate(Square(side_length=2), 1.0),),
    "Rotating": lambda: (Rotating(Square(side_length=2), 1.0),),
    "FadeTransform": lambda: (FadeTransform(Square(side_length=2, color=BLUE), Circle(radius=1, color=YELLOW)),),
}


@pytest.mark.parametrize("name", sorted(CASES))
def test_animation_is_pure_function_of_alpha(name):
    (anim,) = CASES[name]()
    anim.begin()  # capture start/target copies first
    mobs = list(anim.get_all_mobjects()) if hasattr(anim, "get_all_mobjects") else [anim.mobject]

    anim.interpolate(0.30)
    ref_pts, ref_fills = _points(mobs), _fills(mobs)

    # jump far, then return: must reproduce the same state
    anim.interpolate(0.70)
    anim.interpolate(0.30)
    assert _same(ref_pts, _points(mobs)), f"{name}: not stable when returning to alpha"
    assert _same(ref_fills, _fills(mobs)), f"{name}: fill state not stable"

    # approach the same alpha in a different order: must still match
    anim.interpolate(0.95)
    anim.interpolate(0.05)
    anim.interpolate(0.30)
    assert _same(ref_pts, _points(mobs)), f"{name}: order-dependent (not a pure function of alpha)"
