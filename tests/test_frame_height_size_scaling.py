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


def test_affine_store_is_bit_identical_to_manim_to_screen():
    """The numpy fast path must land on exactly the same pixels.

    `_send_vmobject`/`_send_text_write` now map a whole path with
    `store_screen_points` when the frame map is affine (the common case) instead
    of looping per point.  Same operations, same order, then the same
    double->float32 narrowing: bit-identical, including the rounding.
    """
    import ctypes

    import numpy as np

    from real_time_manim.render.util import (affine_frame_map, manim_to_screen,
                                             store_screen_points)

    pts = [(0.0, 0.0), (1.25, -0.5), (-7.111111, 3.9), (0.1, 0.2),
           (-0.0009765625, 7.999999)]

    def check(w, h):
        affine = affine_frame_map(w, h)
        assert affine is not None                # affine: no camera viewport
        out = (ctypes.c_float * (len(pts) * 3))()
        xs = np.asarray([p[0] for p in pts], dtype=np.float64)
        ys = np.asarray([p[1] for p in pts], dtype=np.float64)
        store_screen_points(out, xs, ys, affine[0], affine[1], affine[2])
        for i, (x, y) in enumerate(pts):
            sx, sy = manim_to_screen(x, y, w, h, 0.0)
            assert out[i * 3] == ctypes.c_float(sx).value, (x, y, w, h)
            assert out[i * 3 + 1] == ctypes.c_float(sy).value, (x, y, w, h)
            assert out[i * 3 + 2] == 0.0

    orig_w, orig_h = config.frame_width, config.frame_height
    try:
        camera_state.set_viewport(None)
        for w, h in ((1920, 1080), (1280, 720), (854, 480)):
            check(w, h)
        config.frame_height = 4.0
        config.frame_width = 4.0 * 16 / 9
        check(1920, 1080)
        # A camera viewport is not affine: the senders must fall back to
        # projecting point by point rather than mis-using the affine map.
        config.frame_height, config.frame_width = orig_h, orig_w
        camera_state.set_viewport(Viewport((0.3, -0.2), 5.0))
        assert affine_frame_map(1920, 1080) is None
    finally:
        config.frame_width, config.frame_height = orig_w, orig_h
        camera_state.set_viewport(None)


def test_screen_projector_is_bit_identical_to_manim_to_screen():
    """The senders' fast path must not move a single pixel.

    `_send_vmobject`/`_send_text_write` used to call `manim_to_screen` once per
    POINT (cProfile: 342k calls per 150 frames of a three-Text scene, ~30 % of
    the frame) and now build one `screen_projector` per mobject instead.  The
    whole point of that trade is that it changes nothing: same viewport, same
    scale, same expression order, so the mapped coordinates are identical bit
    for bit -- in the affine case, and under a camera viewport too.
    """
    from real_time_manim.render.util import manim_to_screen, screen_projector

    pts = [(0.0, 0.0, 0.0), (1.25, -0.5, 0.0), (-7.111111, 3.9, 0.0),
           (0.1, 0.2, 0.0), (-0.0009765625, 7.999999, 0.0)]

    def compare(w, h):
        project = screen_projector(w, h)
        for x, y, z in pts:
            assert project(x, y, z) == manim_to_screen(x, y, w, h, z), (x, y, z)

    orig_w, orig_h = config.frame_width, config.frame_height
    try:
        camera_state.set_viewport(None)
        for w, h in ((1920, 1080), (1280, 720), (854, 480)):
            compare(w, h)
        # A frame override must reach the projector too (it is read once).
        config.frame_height = 4.0
        config.frame_width = 4.0 * 16 / 9
        compare(1920, 1080)
        # ... and so must a camera viewport, which projects per point.
        config.frame_height, config.frame_width = orig_h, orig_w
        camera_state.set_viewport(Viewport((0.3, -0.2), 5.0))
        compare(1920, 1080)
    finally:
        config.frame_width, config.frame_height = orig_w, orig_h
        camera_state.set_viewport(None)
