"""A ``Create`` on a Circle must grow smoothly, not jump a cubic at a time.

Report: "圆形出现不平滑" -- the 01-安装 demo video draws its Circle by snapping
forward and standing still, instead of sweeping continuously.

manim builds a ``Circle`` from only EIGHT cubic segments (32 points), and
``_send_vmobject``'s stroke walk cut its reveal window at WHOLE segments::

    vis_end = int(seg_count * progress_upper)

so the drawn arc could only ever be 0/8, 1/8, ... 8/8 of the outline: each
cubic is 45 degrees of arc, so the tip froze for several frames and then
jumped 45 degrees.  Measured on the recorded video (60 fps, crop of the
circle), the lit-pixel count held at one value for 18 frames and then stepped
in ~475 px jumps; a recorder probe reproduced it exactly -- the drawn length
took the values 0.1250, 0.2500, ... 1.0000 of the perimeter and NOTHING in
between.

Native's own stroke tessellator never had this: it cuts at a fractional
``partial_t`` (native/draw/draw_bezier.c:144-170).  The Python walk now
matches it -- the window's ends land inside a segment and the cubic is
evaluated there, so the pen tip moves every frame.

Pure Python -- captures the DLL calls, no GPU work, no ffmpeg.

Run with::

    python -X utf8 -m pytest tests/test_create_circle_smooth.py -q
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
    from manim import Arc, Circle, Scene
    from real_time_manim.vulkan_bind import Create
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


def _frame_lengths(rec):
    """Total stroked length of each frame the recorder saw.

    A frame starts at its ``ClearShapes``; strokes arrive as ``AddLine``
    (one quad per edge) or ``AddLineStrip`` (a whole polyline) -- both
    contribute their true arc length.
    """
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


def _total_stroke(rec):
    """Stroked length across every call, ignoring frame boundaries."""
    return sum(_stroke_length(name, args) for name, args in rec.calls)


def _create_frames(mobject, window, run_time=0.9):
    """Run ``Create(mobject)``; return the stroked length of each frame."""
    scene = Scene()
    scene.setup()
    scene.add(mobject)
    rec = Recorder()
    real = window.dll
    window.dll = rec
    try:
        window.scene = scene
        window.play(Create(mobject), run_time=run_time)
    finally:
        window.dll = real
    return [L for L in _frame_lengths(rec) if L > 0.0]


# --------------------------------------------------------------------------- #
# the reveal must advance every frame
# --------------------------------------------------------------------------- #

def test_circle_reveal_advances_every_frame(window):
    """No plateau: a cubic segment is 45 degrees, far too coarse to see."""
    lens = _create_frames(Circle(radius=0.6), window)
    assert len(lens) >= 8, "expected many painted frames, got %d" % len(lens)
    full = lens[-1]
    assert full > 0.0
    steps = [b - a for a, b in zip(lens, lens[1:])]
    assert min(steps) > 0.0, (
        "the reveal froze for a frame (lengths %s) -- the stroke window is "
        "still quantized to whole cubic segments"
        % (["%.1f" % L for L in lens],))
    # A cubic is 1/8 of this circle; the old code stepped by exactly that.
    assert max(steps) < full / 8.0, (
        "the biggest step was %.1f px, a whole 1/8 (%.1f px) of the outline "
        "-- the tip is still jumping segment to segment"
        % (max(steps), full / 8.0))


def test_circle_reveal_follows_the_requested_progress(window):
    """The drawn arc tracks ``_vulkan_progress`` continuously, whatever the
    rate function and frame timing behind it."""
    mobject = Circle(radius=0.6)
    perimeter = 2.0 * math.pi * 0.6 * SCALE
    seen = []
    scene = Scene()
    scene.setup()
    scene.add(mobject)
    rec = Recorder()

    class _Recorder(Recorder):
        def ClearShapes(self, *a, **kw):
            seen.append(float(getattr(mobject, "_vulkan_progress", 1.0)))
            return Recorder.__getattr__(self, "ClearShapes")(*a, **kw)

    real = window.dll
    rec = _Recorder()
    window.dll = rec
    try:
        window.scene = scene
        window.play(Create(mobject), run_time=0.9)
    finally:
        window.dll = real

    lens = [L for L in _frame_lengths(rec) if L > 0.0]
    progress = seen[-len(lens):]
    assert len(lens) >= 8
    worst = 0.0
    for L, p in zip(lens, progress):
        # The tip may lead the requested progress by at most one sampler step
        # (STEP_PX = 3 px), and must never fall a whole cubic segment short.
        worst = max(worst, abs(L - p * perimeter))
    assert worst < 3.0, (
        "the drawn arc wandered %.2f px from the requested progress -- a "
        "cubic segment here is %.1f px, so this is the staircase again"
        % (worst, perimeter / 8.0))


def test_arc_reveal_is_smooth_too(window):
    """The same walk draws every ``Arc``; a half circle must not jump 90 deg."""
    lens = _create_frames(Arc(angle=math.pi, radius=0.6), window)
    full = lens[-1]
    steps = [b - a for a, b in zip(lens, lens[1:])]
    assert min(steps) > 0.0, "the Arc reveal froze (lengths %s)" % (
        ["%.1f" % L for L in lens],)
    # manim builds Arc from the same 8 cubics over its own angle, so the old
    # window stepped by a quarter of the drawn arc.
    assert max(steps) < full / 4.0, (
        "the Arc's biggest step was %.1f px, a whole quarter (%.1f px) of "
        "its outline" % (max(steps), full / 4.0))


# --------------------------------------------------------------------------- #
# the reveal must still be exact at both ends
# --------------------------------------------------------------------------- #

def test_full_progress_strokes_the_whole_outline(window):
    """The fractional cut must not lose the tail at ``progress == 1.0``."""
    expected = 2.0 * math.pi * 0.6 * SCALE
    assert _send_circle_stroke(window, 1.0) == pytest.approx(expected, rel=0.02)


def test_exact_segment_boundary_keeps_the_previous_segment(window):
    """``progress == 2/8`` is the END of segment 1, not the start of segment 2."""
    expected = 2.0 * math.pi * 0.6 * SCALE
    got = _send_circle_stroke(window, 2.0 / 8.0)
    assert got == pytest.approx(expected * 0.25, rel=0.05), (
        "an exact segment boundary drew %.1f px, expected a quarter of the "
        "%.1f px outline" % (got, expected))


def test_zero_progress_strokes_nothing(window):
    """``progress == 0`` must not draw a dot at the path's start."""
    assert _send_circle_stroke(window, 0.0) == 0.0


def _send_circle_stroke(window, progress):
    """Stroked length ``_send_vmobject`` produces for that progress alone."""
    mobject = Circle(radius=0.6)
    mobject._vulkan_progress = progress
    rec = Recorder()
    real = window.dll
    window.dll = rec
    try:
        window._send_vmobject(mobject, 1.0, WIN_W, WIN_H)
    finally:
        window.dll = real
    return _total_stroke(rec)
