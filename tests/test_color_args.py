"""Regression test: colour arguments accept every form manim accepts.

`point_color` used to be indexed blindly (`color[0]`, `float(color[0])`), so a
hex string either set garbage colours (characters of the string) or raised
`ValueError: could not convert string to float: '#'`.  GrowFromCenter,
GrowFromPoint, GrowFromEdge, SpinInFromNothing and GrowArrow all shared it.

Pure Python: no window, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import pytest
from manim import BLUE, ManimColor, Square, UP, ORIGIN

from real_time_manim.animations import base as anim_base
from real_time_manim.vulkan_bind import (
    GrowArrow, GrowFromCenter, GrowFromEdge, GrowFromPoint, SpinInFromNothing,
)

# Every spelling manim's ParsableManimColor allows *as an animation argument*:
# ManimColor and str (hex / name).  A bare tuple is NOT here on purpose -- manim
# itself rejects it ("ManimColor only accepts int, str, list[...]", verified
# against manim's own GrowFromCenter), so it is not RTM's contract to fix.
SPECS = [BLUE, "#33AADD", "blue"]


def expected_rgb(spec):
    return tuple(float(c) for c in ManimColor(spec).to_rgb())


def make(cls, spec):
    """Build the animation with `point_color=spec` (each class has its own args)."""
    mob = Square()
    if cls is GrowFromEdge:
        return cls(mob, edge=UP, point_color=spec)
    if cls is GrowFromPoint:
        return cls(mob, point=ORIGIN, point_color=spec)
    if cls is GrowArrow:
        return cls(mob, point_color=spec)
    return cls(mob, point_color=spec)


@pytest.mark.parametrize("cls", [GrowArrow, GrowFromCenter, GrowFromEdge,
                                 GrowFromPoint, SpinInFromNothing])
@pytest.mark.parametrize("spec", SPECS, ids=lambda s: str(s))
def test_point_color_accepts_every_spec(cls, spec):
    anim = make(cls, spec)
    anim.begin(0.0)
    got = tuple(round(float(c), 6) for c in anim._pc)
    want = tuple(round(c, 6) for c in expected_rgb(spec))
    assert got == want, f"{cls.__name__} point_color={spec!r}: {got} != {want}"


def test_hex_string_no_longer_crashes():
    """The exact crash from the test log: float('#')."""
    anim = GrowFromCenter(Square(), point_color="#33AADD")
    anim.begin(0.0)
    assert anim._pc == pytest.approx((0x33 / 255, 0xAA / 255, 0xDD / 255), abs=1e-6)


def test_color_to_rgb_helper_matches_manim():
    # ManimColor / str (RTM's contract) ...
    for spec in SPECS:
        assert anim_base.color_to_rgb(spec) == pytest.approx(expected_rgb(spec))
    # ... and list/tuple, which ManimColor itself normalizes even though manim's
    # set_color path rejects a tuple (see SPECS note above).
    for spec in ((1.0, 0.0, 0.0), [0.2, 0.4, 0.6]):
        assert anim_base.color_to_rgb(spec) == pytest.approx(tuple(spec))
