"""Regression test: a plain Scene's size scaling must follow ``config.frame_height``.

Report: wiki ``01-场景与相机/配置/02-画幅坐标`` "曲线/直线缩放不一致" -- halving the
frame (``config.frame_y_radius``/``frame_x_radius``) doubled the Square but left
the Circle/Dot at half the size ("曲线图形走了带 frame_height 修正的另一条坐标换算，
实测圆只有方块一半大").

Root cause: two different notions of "how many manim units tall is the frame":

* POSITIONS (a Square's points, a Dot's centre) go through
  ``manim_to_screen`` -> ``screen_scale(w, h)``, which reads ``config.frame_width``
  -- so they DO follow a ``config`` override.
* SIZES (a Dot's radius, a stroke width) go through ``h / _visible_frame_height()``,
  which for a plain Scene returned the HARDCODED ``8.0`` -- so they ignored the
  override and stayed the default size.

The fix makes ``_visible_frame_height`` fall back to ``config.frame_height`` (still
8.0 by default, so nothing changes for existing scenes; only an override is
affected), which puts sizes on the same config-derived scale as positions.

Pure Python: no DLL, no GPU.  Restores the global ``config.frame_height`` and the
published viewport after every test so nothing leaks into the rest of the suite.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import config

from real_time_manim import camera_state
from real_time_manim.render.shapes.stroke import StrokeMixin
from real_time_manim.camera_state import Viewport, screen_scale


def _with_config_frame_height(value, fn):
    """Run ``fn`` with ``config.frame_height`` set, then restore everything."""
    orig = config.frame_height
    camera_state.set_viewport(None)
    try:
        config.frame_height = value
        return fn()
    finally:
        config.frame_height = orig
        camera_state.set_viewport(None)


def test_default_frame_height_stays_eight():
    """No override: the default is 8.0, identical to the old hardcoded value."""
    assert _with_config_frame_height(8.0, StrokeMixin._visible_frame_height) == 8.0


def test_config_override_is_returned():
    """A plain Scene honors a ``config.frame_height`` override for SIZE scaling."""
    assert _with_config_frame_height(4.0, StrokeMixin._visible_frame_height) == 4.0


def test_viewport_wins_over_config():
    """A MovingCamera viewport still reports its own height, config ignored."""
    orig = config.frame_height
    try:
        config.frame_height = 8.0
        camera_state.set_viewport(Viewport((0.0, 0.0), 5.0))
        assert StrokeMixin._visible_frame_height() == 5.0
    finally:
        config.frame_height = orig
        camera_state.set_viewport(None)


def test_positions_and_sizes_scale_together_under_override():
    """The consistency the bug violated: a halved frame doubles BOTH scales.

    Positions use ``screen_scale(w, h)`` = ``w / config.frame_width``; sizes use
    ``h / _visible_frame_height()``.  With a 16:9 override halved on both axes
    the two must stay equal (uniform zoom) and 2x the default -- which is what
    puts the Square and the Dot/Circle back in agreement.
    """
    orig_w, orig_h = config.frame_width, config.frame_height
    camera_state.set_viewport(None)
    try:
        # exact 16:9 pairs so position and size scales agree to the bit
        config.frame_height = 8.0
        config.frame_width = 8.0 * 16 / 9
        base_pos = screen_scale(1920, 1080)
        base_size = 1080.0 / StrokeMixin._visible_frame_height()
        config.frame_height = 4.0
        config.frame_width = 4.0 * 16 / 9
        new_pos = screen_scale(1920, 1080)
        new_size = 1080.0 / StrokeMixin._visible_frame_height()
        assert abs(new_pos - 2 * base_pos) < 1e-6, (new_pos, base_pos)
        assert abs(new_size - 2 * base_size) < 1e-6, (new_size, base_size)
        assert abs(new_pos - new_size) < 1e-6, (new_pos, new_size)
    finally:
        config.frame_width, config.frame_height = orig_w, orig_h
        camera_state.set_viewport(None)
