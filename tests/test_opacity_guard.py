"""Regression test: opacity lookup must not trust `hasattr(mob, 'get_*_opacity')`.

manim defines `Mobject.get_fill_opacity` / `get_stroke_opacity` for every
mobject, but they just forward to `fill_opacity` / `stroke_opacity` -- which
PMobject (PointCloudDot) and parts of the ImageMobject family do not have. So the
old guard `mob.get_fill_opacity() if hasattr(mob, 'get_fill_opacity') else 1.0`
passed the check and then raised AttributeError halfway through a render, which
is exactly the F5 crash (0 frames, no output).

Pure Python: no window, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import pytest
from manim import PointCloudDot, Square

from real_time_manim.vulkan_util import get_opacity


def test_old_guard_is_indeed_broken():
    """Document the false assumption the fix removes."""
    mob = PointCloudDot()
    assert hasattr(mob, "get_stroke_opacity") is True      # the old guard passed ...
    assert hasattr(mob, "stroke_opacity") is False         # ... yet there is no value
    with pytest.raises(AttributeError):
        mob.get_stroke_opacity()                           # -> the F5 crash


def test_point_cloud_dot_has_no_stroke_opacity():
    mob = PointCloudDot()
    assert get_opacity(mob, "stroke", 1.0) == 1.0
    assert get_opacity(mob, "fill", 0.0) == 0.0
    assert get_opacity(mob, "fill") == 1.0                 # default default


def test_normal_mobject_keeps_its_real_opacity():
    sq = Square()
    sq.set_fill(opacity=0.4)
    sq.set_stroke(opacity=0.25)
    assert get_opacity(sq, "fill") == pytest.approx(0.4)
    assert get_opacity(sq, "stroke") == pytest.approx(0.25)


def test_image_mobject_family_missing_fill_opacity():
    """The exact class from the report: no fill_opacity, must not raise."""
    from manim import ImageMobjectFromCamera, MovingCamera
    mob = ImageMobjectFromCamera(MovingCamera())
    assert hasattr(mob, "fill_opacity") is False
    assert get_opacity(mob, "fill", 0.3) == 0.3
    assert isinstance(get_opacity(mob, "stroke", 0.3), float)


def test_getter_that_raises_falls_back():
    class Broken:
        """Has the getter (like manim's Mobject) but it raises (like PMobject)."""
        def get_fill_opacity(self):
            raise AttributeError("no fill_opacity")

    assert get_opacity(Broken(), "fill", 0.7) == 0.7


def test_value_that_cannot_be_float_falls_back():
    class Weird:
        fill_opacity = "opaque"

    assert get_opacity(Weird(), "fill", 0.2) == 0.2
