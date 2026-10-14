"""A windowed reveal must neither pop its fill in whole nor lose its lower edge.

Two bugs of one family: a *partial* mobject was rendered as if it were whole.

**1. The fill arrived on frame one.**  Native's ``tessellate_fill`` samples
every cubic of the submitted array and never reads ``progress``
(draw_bezier.c:268-284), so a fill revealed by ``_vulkan_progress`` (RTM's own
``Create``) was submitted WHOLE on the first frame.  Measured on
``Create(Circle(fill_opacity=1))``: 95.0 % of the finished ink on frame one
against ManimCE's 0.0 %, while only the outline swept.  ``Square``/``Rectangle``
never showed it because they go through ``_send_polygon``, and manim's own
``Create`` never showed it because ``pointwise_become_partial`` cuts the POINTS
first.  Only the point-path shapes drawn from a bare ``_vulkan_progress`` were
affected -- Circle 95.0, Ellipse 94.6, Arc 90.5, Sector 100.0, AnnularSector
100.0.

**2. The window lost its lower edge.**  ``paint.py`` branched on the PLAIN
``_vulkan_progress``.  The flash publishes a lower/upper PAIR, and
``_write_passing_flash`` also sets ``_vulkan_progress = upper`` -- so once
``upper`` clamps to 1.0 the test ``0.0 < progress < 1.0`` goes FALSE and the
shape falls to ``_send_circle``/``_send_ellipse``/``_send_arc``, which read only
``_vulkan_progress`` (1.0) and never ``point_path_bounds``: the tail of the
sweep drew the WHOLE shape.  RTM's OWN ``ShowPassingFlash`` never wrote
``_vulkan_progress`` at all (it stays at the 0.0 that ``begin()`` set), so the
test failed at EVERY frame and those senders bailed at ``progress <= 0`` -- a
flash over a Circle emitted ZERO shape calls for the whole animation while Line
and Square, whose senders read ``point_path_bounds``, drew fine.  ``_send_line``
had the same drop in miniature: it read ``point_path_bounds(mob)[1]`` and always
started at the line's own start, so a Line's flash grew from the start and
peaked at 1980 px = 100 % of the full line where a 0.3-wide window should hold
~30 %.

Pure Python -- captures the DLL calls, no GPU work, no ffmpeg.

Run with::

    python -X utf8 -m pytest tests/test_passing_flash_and_fill.py -q
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import math

import pytest

try:
    import real_time_manim.vulkan_bind as vb
    from manim import Arc, Arrow, Circle, Ellipse, Line, Scene
    from real_time_manim.vulkan_bind import ShowPassingFlash
except Exception as e:                                  # pragma: no cover
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


WIN_W, WIN_H = 1920, 1080
UNITS_TALL = 8.0                  # manim's default frame height
SCALE = WIN_H / UNITS_TALL        # screen px per manim unit


@pytest.fixture(scope="module")
def window():
    try:
        w = vb.MLWindow(WIN_W, WIN_H, hidden=True)
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


def _stroke_length(name, args):
    """Arc length one native stroke call contributes, 0.0 for anything else."""
    if name == 'AddLine':
        return math.hypot(float(args[2]) - float(args[0]),
                          float(args[3]) - float(args[1]))
    if name == 'AddLineStrip':
        pts = list(args[0])
        m = int(args[2])
        return sum(math.hypot(float(pts[2 * i + 2]) - float(pts[2 * i]),
                              float(pts[2 * i + 3]) - float(pts[2 * i + 1]))
                   for i in range(m - 1))
    return 0.0


def _frame_lengths(rec):
    """Stroked length of each frame the recorder saw, frame = a ClearShapes."""
    out, cur = [], None
    for name, args in rec.calls:
        if name == 'ClearShapes':
            if cur is not None:
                out.append(cur)
            cur = 0.0
            continue
        if cur is None:
            continue
        cur += _stroke_length(name, args)
    if cur is not None:
        out.append(cur)
    return out


def _send(mobject, window, **attrs):
    """Run one ``_send_vmobject`` on ``mobject``; return the recorder."""
    for key, value in attrs.items():
        setattr(mobject, key, value)
    rec = Recorder()
    real = window.dll
    window.dll = rec
    try:
        window._send_vmobject(mobject, 1.0, WIN_W, WIN_H)
    finally:
        window.dll = real
    return rec


def _bezier_paths(rec):
    """Every ``(num_points, progress, show_fill)`` the fill path was sent with."""
    return [(int(args[1]), float(args[10]), int(args[12]))
            for name, args in rec.calls if name == 'AddBezierPath']


# --------------------------------------------------------------------------- #
# 1. the fill must grow with the outline, not arrive whole
# --------------------------------------------------------------------------- #

def test_fill_array_is_cut_to_the_drawn_prefix(window):
    """Halfway through, the fill array must be half the circle's cubics."""
    full_n = 32                      # manim builds a Circle from 8 cubics
    paths = _bezier_paths(_send(Circle(radius=0.6, fill_opacity=1.0), window,
                                _vulkan_progress=0.5))
    assert paths, "the fill was never submitted at all"
    n, progress, show_fill = paths[0]
    assert show_fill == 1
    assert n < full_n, (
        "a Circle filled halfway was submitted with %d points, the WHOLE "
        "outline's %d -- native's tessellate_fill ignores `progress`, so this "
        "paints the finished disc on the first frame" % (n, full_n))
    # The array now ENDS at the pen tip, so native must not window it twice.
    assert progress == 1.0


def test_fill_prefix_grows_with_the_progress(window):
    """The submitted array must track the outline, not jump to whole."""
    sizes = [_bezier_paths(_send(Circle(radius=0.6, fill_opacity=1.0), window,
                                 _vulkan_progress=p))[0][0]
             for p in (0.25, 0.5, 0.75)]
    assert sizes == sorted(sizes), (
        "the fill array did not grow with progress: %s" % (sizes,))
    assert len(set(sizes)) == 3, (
        "the fill array jumped between frames: %s -- it is still quantized to "
        "whole cubic segments" % (sizes,))


def test_full_progress_keeps_the_whole_fill(window):
    """The cut must not lose the tail at ``progress == 1.0``."""
    paths = _bezier_paths(_send(Circle(radius=0.6, fill_opacity=1.0), window,
                                _vulkan_progress=1.0))
    assert paths[0][0] == 32


def test_a_flash_that_has_not_reached_the_end_fills_nothing(window):
    """A sliding window is a stroke, not a shape: no fill until it closes."""
    mobject = Circle(radius=0.6, fill_opacity=1.0)
    paths = _bezier_paths(_send(mobject, window,
                                _vulkan_progress=0.6,
                                _vulkan_progress_lower=0.3,
                                _vulkan_progress_upper=0.6))
    assert paths, "the flash never submitted a path"
    assert paths[0][2] == 0, (
        "a window at [%.2f, %.2f] submitted the fill (show_fill=%d) -- the "
        "native tessellator ignores the window and paints the whole disc"
        % (0.3, 0.6, paths[0][2]))


# --------------------------------------------------------------------------- #
# 2. a flash must draw something, and only its window
# --------------------------------------------------------------------------- #

def _flash_frames(mobject, window, time_width=0.3):
    """Stroked length of each frame a ``ShowPassingFlash`` produced."""
    scene = Scene()
    scene.setup()
    scene.add(mobject)
    rec = Recorder()
    real = window.dll
    window.dll = rec
    try:
        window.scene = scene
        window.play(ShowPassingFlash(mobject, time_width=time_width,
                                     run_time=1.0))
    finally:
        window.dll = real
    return _frame_lengths(rec)


@pytest.mark.parametrize("factory", [
    lambda: Circle(radius=0.6),
    lambda: Ellipse(width=1.4, height=0.8),
    lambda: Arc(angle=math.pi, radius=0.6),
], ids=["Circle", "Ellipse", "Arc"])
def test_a_flash_draws_every_frame(factory, window):
    """``ShowPassingFlash`` must not fall through to a sender that bails.

    RTM's own flash never wrote `_vulkan_progress`, so the `0.0 < p < 1.0`
    dispatch test failed on every frame and the Circle/Ellipse/Arc senders
    returned at `progress <= 0` -- the animation emitted zero shape calls.
    """
    mobject = factory()
    lens = [L for L in _flash_frames(mobject, window) if L > 0.0]
    assert len(lens) >= 20, (
        "a 60-frame flash painted only %d frames -- the shape is falling to a "
        "sender that reads the bare `_vulkan_progress` and bails" % len(lens))


def _complete_stroke(mobject, window, run_time=0.1):
    """Stroked length of the shape's LAST frame, i.e. its finished outline.

    Measured through the very same sender the flash uses, so anything the
    emitter does to a stroke (native's sub-pixel rule submits an integer core
    plus two symmetric fractional EDGE quads for one segment, which makes an
    arc-length proxy count that segment three times) cancels in the ratio.
    """
    scene = Scene()
    scene.setup()
    scene.add(mobject)
    rec = Recorder()
    real = window.dll
    window.dll = rec
    try:
        window.scene = scene
        from real_time_manim.vulkan_bind import Create
        window.play(Create(mobject), run_time=run_time)
    finally:
        window.dll = real
    lens = [L for L in _frame_lengths(rec) if L > 0.0]
    assert lens, "the complete outline drew nothing"
    return lens[-1]


@pytest.mark.parametrize("factory", [
    lambda: Circle(radius=0.6),
    lambda: Ellipse(width=1.4, height=0.8),
    lambda: Arc(angle=math.pi, radius=0.6),
    lambda: Line([-2.0, 0.0, 0.0], [2.0, 0.0, 0.0]),
    lambda: Arrow([-3.0, 0.0, 0.0], [3.0, 0.0, 0.0], buff=0),
], ids=["Circle", "Ellipse", "Arc", "Line", "Arrow"])
def test_a_flash_holds_its_window(factory, window):
    """The sweep must slide, never grow to the whole outline.

    A window of width 0.3 may ink about a third of the outline at its peak.  It
    used to reach 100 %: `_send_line` read only `point_path_bounds(mob)[1]` and
    always started at the line's own start, so its flash grew from the start
    (measured 1980 px = 100 % of the full line), and the Circle/Ellipse/Arc
    tail dropped `lower` once `upper` clamped to 1.0.
    """
    full = _complete_stroke(factory(), window)
    lens = _flash_frames(factory(), window)
    peak = max(lens)
    assert peak > 0.0, "the flash drew nothing at all"
    assert peak <= 0.55 * full, (
        "the flash peaked at %.0f px, %.0f %% of the %.0f px finished outline "
        "-- a 0.3-wide window must not reach the whole shape"
        % (peak, 100.0 * peak / full, full))
    assert peak >= 0.15 * full, (
        "the flash peaked at only %.0f px (%.0f %% of %.0f px) -- the window "
        "collapsed to almost nothing"
        % (peak, 100.0 * peak / full, full))


def test_a_line_flash_slides_instead_of_growing(window):
    """The lower edge of a Line's window must be honoured, frame by frame."""
    line = Line([-2.0, 0.0, 0.0], [2.0, 0.0, 0.0])
    full = _complete_stroke(Line([-2.0, 0.0, 0.0], [2.0, 0.0, 0.0]), window)
    lens = _flash_frames(line, window)
    # Every frame of a 0.3-wide window inks ~30 %; a growing line ramps 0 -> 100.
    over = [L for L in lens if L > 0.60 * full]
    assert not over, (
        "%d frames inked more than 60 %% of the %.0f px line (worst %.0f px) "
        "-- the window's `lower` edge is being dropped, so the sweep grows "
        "from the start instead of sliding" % (len(over), full, max(lens)))


def test_a_flash_arrow_head_follows_the_sweep(window):
    """The head must not be pinned whole to the apex during a flash.

    `_send_arrow` synthesises the head as a filled triangle at the apex and
    only routes the real tip down the point path when `progress >= 1.0` -- so
    during a flash (`progress = upper`, usually < 1.0) the whole head sat on
    the screen from the first frame.  CE instead applies the window to every
    member of the family separately (ShowPartial.interpolate_submobject ->
    pointwise_become_partial on each submobject, manim/animation/creation.py:
    126-134), so the head lights up only as the sweep reaches it.

    A synthesised head arrives as `AddPolygon`; the real tip goes through
    `AddBezierPath`.  Measured against CE on Arrow(LEFT*3, RIGHT*3):
    CE's ink rises to 28 % of the finished arrow and falls back to 0, while
    RTM ramped to 100 % and stuck there.
    """
    arrow = Arrow([-3.0, 0.0, 0.0], [3.0, 0.0, 0.0], buff=0)
    scene = Scene()
    scene.setup()
    scene.add(arrow)
    rec = Recorder()
    real = window.dll
    window.dll = rec
    try:
        window.scene = scene
        window.play(ShowPassingFlash(arrow, time_width=0.3, run_time=1.0))
    finally:
        window.dll = real

    names = [n for n, _a in rec.calls]
    assert "AddBezierPath" in names, (
        "a flash over an Arrow drew no tip at all -- the head never reached "
        "the point path")
    assert "AddPolygon" not in names, (
        "a flash over an Arrow submitted a synthesised `AddPolygon` head -- "
        "the head is pinned whole to the apex instead of following the sweep, "
        "so it is on screen from the first frame")
