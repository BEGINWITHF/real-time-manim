"""Regression tests for the 2026-10-19 wiki clip fixes.

Five clips from the RTM-Wiki re-render sweep each had a concrete cause:

1. ``03-动画/移动与旋转/01-旋转-rotating_axis`` -- "转轴绑错了".
   ``Rotating(arrow, 180*DEGREES, axis=IN)`` has no explicit pivot, and manim's
   ``Mobject.rotate`` then uses the mobject's **centre**.  RTM's bake path used
   ORIGIN, so the arrow swung around the frame centre and left the screen while
   CE spun it in place (measured: RTM centroid cx 179 -> 60 px, CE 179 -> 167).

2. ``03-动画/文字与数字/01b-带光标打字`` -- "光标 delete 在最后一个 D 消失后
   没有移动".  manim's ``TypeWithCursor.update_submobject_list`` has an
   ``index == 0`` branch that moves the cursor onto the FIRST glyph; RTM had
   ``if index > 0`` only, so the caret stayed parked right of the deleted "D".

3. ``03-动画/生长出现/01b-箭头与旋入`` -- "箭头头的颜色没变".  The arrowHEAD is a
   submobject; only the shaft's rgbas were stored/lerped, so
   ``GrowArrow(arrow, point_color=RED)`` left the head red on the last frame
   where CE has the whole arrow back to gold.

4. ``03-动画/强调与提示/01b-扫光与波纹`` -- the flash was windowed TWICE (manim's
   ``ShowPartial`` already cut the points to ``_get_bounds(alpha)``) and with a
   phase-shifted window (``[alpha, alpha + tw]`` instead of
   ``[alpha*(1+tw) - tw, alpha*(1+tw)]``).

5. ``03-动画/变换/02b-更多函数驱动`` -- "黄点出现的动画没播放": ``Dot`` has its
   own sender, which always submitted ``stroke_progress = 1.0`` (and native's
   fill ignores that channel), so ``Create(Dot)`` popped the disc in whole.

6. ``04-图形与文本/03-多边形与星形-stars_round`` -- "弧形角画成尖角":
   ``round_corners()`` keeps the ``Polygon`` class but replaces the corners with
   arcs, and ``get_vertices()`` then returns the arc anchors, so the polygon
   fast path chordered them into sharp corners.

Run with::

    python -X utf8 -m pytest tests/test_wiki_clip_fixes.py -q
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
import pytest

try:
    from manim import (Arrow, Dot, DOWN, IN, LEFT, PI, Polygon, RIGHT, Scene,
                       Square, Text, UP, YELLOW, Line)
    from real_time_manim.animations.grow_arrow import GrowArrow
    from real_time_manim.animations.rotating import Rotating
    from real_time_manim.animations.type_with_cursor import TypeWithCursor
    from real_time_manim.animations.untype_with_cursor import UntypeWithCursor
    from real_time_manim.animations.base import get_anim_opacity
    from real_time_manim.render.hook_channels import _write_passing_flash
    from real_time_manim.render.hooks import install_hooks
    from real_time_manim.vulkan_bind import MLWindow
except Exception as e:                                  # pragma: no cover
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


@pytest.fixture(scope="module")
def window():
    try:
        w = MLWindow(1920, 1080, hidden=True)
    except Exception as e:                              # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield w
    try:
        w.close()
    except Exception:
        pass


class Recorder(object):
    """Stands in for the native DLL and keeps every submitted call."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


def _record(window, mob, **attrs):
    for key, value in attrs.items():
        setattr(mob, key, value)
    rec = Recorder()
    real = window.dll
    window.dll = rec
    try:
        window._send(mob)
    finally:
        window.dll = real
    return [name for name, _ in rec.calls]


# --------------------------------------------------------------------------- #
# 1. Rotating without a pivot spins in place
# --------------------------------------------------------------------------- #

def test_rotating_without_a_pivot_spins_about_the_mobjects_centre():
    sq = Square(side_length=1.0).move_to(LEFT * 3.0 + DOWN * 1.0)
    anim = Rotating(sq, angle=PI, axis=IN, run_time=1.0)
    anim.begin(0.0)
    centre = np.array(sq.get_center(), dtype=float)

    anim.interpolate(0.5)
    mid = np.array(sq.get_center(), dtype=float)
    assert np.allclose(mid, centre, atol=0.05), (
        "an in-plane rotation with no pivot must keep the centre; it orbited "
        "to %s from %s" % (mid, centre))

    anim.interpolate(1.0)
    end = np.array(sq.get_center(), dtype=float)
    assert np.allclose(end, centre, atol=0.05)


# --------------------------------------------------------------------------- #
# 2. the caret returns to the first glyph
# --------------------------------------------------------------------------- #

def test_untype_with_cursor_moves_onto_the_first_glyph_when_empty():
    scene = Scene()
    text = Text("Deleting", font_size=40)
    cursor = Square(side_length=0.4).move_to(text[0])
    scene.add(text, cursor)
    anim = UntypeWithCursor(text, cursor, run_time=1.0)
    anim.begin(0.0)
    anim.interpolate(1.0)                    # everything deleted
    assert get_anim_opacity(text[0]) == pytest.approx(0.0, abs=0.02)
    assert cursor.get_center()[0] == pytest.approx(text[0].get_center()[0],
                                                   abs=0.06)


def test_type_with_cursor_starts_on_the_first_glyph():
    scene = Scene()
    text = Text("Inserting", font_size=40)
    cursor = Square(side_length=0.4).move_to(text[0])
    anim = TypeWithCursor(text, cursor, run_time=1.0)
    anim.begin(0.0)
    anim.interpolate(0.0)                    # nothing typed yet
    assert cursor.get_center()[0] == pytest.approx(text[0].get_center()[0],
                                                   abs=0.06)


# --------------------------------------------------------------------------- #
# 3. GrowArrow's point colour reaches the head
# --------------------------------------------------------------------------- #

def test_grow_arrow_point_color_reaches_the_head_and_restores():
    from manim import GOLD, RED
    from real_time_manim.animations.base import color_to_rgb
    arrow = Arrow(LEFT * 2 + DOWN, RIGHT * 2 + DOWN, buff=0, color=GOLD)
    tip = arrow.tip
    orig_tip = np.array(tip.get_stroke_rgbas()[0][:3], dtype=float)
    anim = GrowArrow(arrow, point_color=RED, run_time=1.0)
    anim.begin(0.0)
    red = np.array(color_to_rgb(RED), dtype=float)

    start = np.array(tip.get_stroke_rgbas()[0][:3], dtype=float)
    assert np.allclose(start, red, atol=0.02), (
        "the head must start at point_color, got %s" % start)

    anim.interpolate(1.0)
    end = np.array(tip.get_stroke_rgbas()[0][:3], dtype=float)
    assert np.allclose(end, orig_tip, atol=0.02), (
        "the head must be back to its own colour, got %s want %s"
        % (end, orig_tip))

    anim.finish()
    restored = np.array(tip.get_stroke_rgbas()[0][:3], dtype=float)
    assert np.allclose(restored, orig_tip, atol=0.02)


# --------------------------------------------------------------------------- #
# 4. the flash window is manim's own, over the whole contour
# --------------------------------------------------------------------------- #

def test_passing_flash_window_is_manims_own():
    from manim import ShowPassingFlash
    line = Line([-3, 0, 0], [3, 0, 0], stroke_width=6)
    anim = ShowPassingFlash(line, time_width=0.5, run_time=1.0)
    anim.begin()
    install_hooks(anim)
    full = np.array(line.points, dtype=float)

    anim.interpolate(0.5)
    lower, upper = anim._get_bounds(0.5)
    assert getattr(line, "_vulkan_progress_lower") == pytest.approx(lower)
    assert getattr(line, "_vulkan_progress_upper") == pytest.approx(upper)
    # the window is a fraction of the WHOLE line, so the points must be back
    assert np.allclose(np.array(line.points, dtype=float), full, atol=1e-9), (
        "the hook must restore the pristine contour; the window is applied by "
        "the sender, not baked into the points")


def test_passing_flash_window_is_eased_like_manim():
    """manim cuts with ``get_sub_alpha`` = ``rate_func(clip(alpha))``.

    The hook is handed the RAW progress, so windowing it directly swept the
    comet LINEARLY: measured on the wiki 01b-扫光与波纹 ring, CE's arc head
    ran 0, 2, 3, 6, 10, 16, 23, 33, 48, 67, 91, 120 deg while RTM's ran
    3, 19, 33, 49, 63, 78, 94, 110 (a constant 3.8 deg/frame).
    """
    from manim import ShowPassingFlash
    line = Line([-3, 0, 0], [3, 0, 0], stroke_width=6)
    # default rate_func is smooth, so 0.25 eases to 0.156 -- a plain
    # difference between the eased and the raw window
    anim = ShowPassingFlash(line, time_width=0.5, run_time=1.0)
    anim.begin()
    install_hooks(anim)
    raw = 0.25
    eased = float(anim.rate_func(raw))
    assert abs(eased - raw) > 1e-3, "test needs a non-linear rate function"

    anim.interpolate(raw)
    lower, upper = anim._get_bounds(eased)
    assert getattr(line, "_vulkan_progress_lower") == pytest.approx(lower, abs=1e-9)
    assert getattr(line, "_vulkan_progress_upper") == pytest.approx(upper, abs=1e-9)


# --------------------------------------------------------------------------- #
# 5/6. dispatch: partial Dot and rounded Polygon
# --------------------------------------------------------------------------- #

def test_polygram_stroke_width_survives_the_end_of_a_create():
    """A closed strip's seam cap must not taper the first quad.

    ``JointCutCorners`` falls back to a plain cap when a joint turns past
    ~151 deg.  At a CLOSED strip's seam the incoming direction is the LAST
    segment's, so using it for the first segment's start cap skewed that quad
    into a taper: the bow-tie ``Polygram`` of wiki
    04-图形与文本/03-多边形与星形-polygons drew its first edge 5 px wide in
    the steady state while CE draws 7 -- and it snapped from the Create's
    correct 7 px the moment the animation ended ("线条粗细瞬间变窄").
    """
    import numpy as np
    from manim import Polygram, TEAL, Create, Scene
    from real_time_manim.frames import FrameServer
    from real_time_manim.vulkan_bind import MLWindow

    verts = [[-5.6, 2.0, 0], [-2.6, 0.8, 0], [-3.6, 2.0, 0], [-4.6, 0.8, 0]]

    def scene(animated):
        class _S(Scene):
            def construct(self):
                win = MLWindow(1920, 1080)
                win.scene = self
                poly = Polygram(verts, color=TEAL, stroke_width=5)
                if animated:
                    win.play(Create(poly), run_time=1.0)
                else:
                    self.add(poly)
                win.close()
        return _S

    def first_edge_width(cls, t):
        fs = FrameServer(cls)
        try:
            px = fs.grab_pixels(t)
            w, h = fs.frame_size
            img = np.frombuffer(bytes(px), dtype=np.uint8).reshape(h, w, 4)
            luma = img[:, :, :3].mean(axis=2)
            col = luma[240:470, 300]
            lit = np.nonzero(col > 60)[0]
            runs = []
            for i in lit:
                if runs and runs[-1][1] + 1 == i:
                    runs[-1][1] = i
                else:
                    runs.append([i, i])
            return runs[0][1] - runs[0][0] + 1 if runs else 0
        finally:
            fs.close()

    steady = first_edge_width(scene(False), 0.1)
    after_create = first_edge_width(scene(True), 1.3)
    assert steady == after_create, (
        "the stroke must not change width when the Create ends: %d px steady "
        "vs %d px right after the play" % (steady, after_create))
    assert steady >= 6, "CE draws this edge 7 px wide, got %d" % steady


def test_create_dot_does_not_pop_the_disc_in(window):
    dot = Dot(radius=0.16, color=YELLOW)
    partial = _record(window, dot, _vulkan_progress=0.3)
    assert "AddCircle" not in partial, (
        "a partially drawn Dot must not submit a full disc: %s" % partial)
    assert "AddBezierPath" in partial

    whole = _record(window, dot, _vulkan_progress=1.0)
    assert "AddCircle" in whole


def test_rounded_polygon_takes_the_point_path(window):
    poly = Polygon([-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0],
                   color=YELLOW).round_corners(0.4)
    calls = _record(window, poly)
    assert "AddBezierPath" in calls, (
        "rounded corners must be tessellated, not chordered: %s" % calls)

    sharp = Polygon([-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0],
                    color=YELLOW)
    calls = _record(window, sharp)
    assert "AddBezierPath" not in calls, (
        "a straight-edged polygon keeps the cheap sender: %s" % calls)
    assert {"AddPolygon", "AddLineStrip"} & set(calls)
