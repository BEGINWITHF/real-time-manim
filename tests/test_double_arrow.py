"""A `DoubleArrow`'s shaft must start at its OWN first point, not at the
start tip's apex.

`LinesAnglesAndVectors` (scenes/08_geometry.py:196), frame comparison of
`videos_rtm_hq/08_geometry/LinesAnglesAndVectors.mp4` against the CE render:

    CE : arrow ink from x=1473 to x=1742   (the two apexes)
    RTM: arrow ink from x=1469 to x=1741   (4 px of ink CE never draws)

The extra ink is a stub of shaft sticking out to the LEFT of the left
arrowhead, at the shaft's own height (y 212..219), i.e. the shaft starts
before the head instead of at its base.

Why: `_send_arrow` used `mob.get_start()` as the shaft's first point, and on a
`DoubleArrow` that is not the shaft at all.  manim adds a SECOND tip at the
beginning of the line (`start_tip`), so the endpoints report the *tips'* apexes:

    DoubleArrow([3.8, 2.4, 0], [5.8, 2.4, 0], buff=0)
        get_start()          -> [3.80, 2.4, 0]   start tip's apex
        line's own points[0] -> [4.15, 2.4, 0]   where the shaft begins
        line's own points[-1]-> [5.45, 2.4, 0]   where the shaft ends
        get_end()            -> [5.80, 2.4, 0]   end tip's apex

That is the exact mirror of the `get_end()` rule `_send_arrow` already follows
at the far end (report #9: the head base had to come from the line, not from
`get_end() - tip_length`), and the shaft was drawn 0.35 units = 47 px too long
to the left.  It only shows where the head is narrow -- near the apex the
triangle no longer covers the shaft, so the stroke pokes out as a stub.

Pure Python: captures the DLL calls, no GPU work beyond opening the window.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import real_time_manim.vulkan_bind as vb
    from manim import Arrow, DoubleArrow
    from real_time_manim.vulkan_util import manim_to_screen
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)

W, H = 1920, 1080
START, END = (3.8, 2.4, 0.0), (5.8, 2.4, 0.0)


class Recorder(object):
    """Records every DLL call by name; returns 0 like the real stub."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


@pytest.fixture(scope="module")
def renderer():
    try:
        r = vb.MLWindow(W, H)
    except Exception as e:  # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield r
    try:
        r.close()
    except Exception:
        pass


def capture(renderer, mob):
    """Send `mob` through the real dispatch; return [(dll_name, args), ...]."""
    rec = Recorder()
    real = renderer.dll
    renderer.dll = rec
    try:
        renderer._send(mob)
    finally:
        renderer.dll = real
    return rec.calls


def shaft(calls):
    """(x1, y1, x2, y2) of the first `AddLine` -- the shaft, in screen px."""
    for name, args in calls:
        if name == "AddLine":
            return tuple(float(args[i]) for i in range(4))
    return None


def screen(pt):
    return manim_to_screen(pt[0], pt[1], W, H, pt[2])


def test_double_arrow_shaft_runs_from_head_base_to_head_base(renderer):
    """Both ends of the shaft are the line's own endpoints, not the apexes."""
    mob = DoubleArrow(np.array(START), np.array(END), buff=0)
    own = np.asarray(mob.get_points(), dtype=float)
    x1, y1, x2, y2 = shaft(capture(renderer, mob))
    assert (x1, y1) == pytest.approx(screen(own[0]), abs=0.5), (
        "shaft starts at %s, manim's line starts at %s"
        % ((x1, y1), screen(own[0])))
    assert (x2, y2) == pytest.approx(screen(own[-1]), abs=0.5), (
        "shaft ends at %s, manim's line ends at %s"
        % ((x2, y2), screen(own[-1])))


def test_double_arrow_shaft_does_not_start_at_the_start_tip_apex(renderer):
    """The defect itself: `get_start()` is 0.35 units (47 px) further left.

    A regression puts the shaft back on the apex, which is where it used to
    start, so this pins the difference rather than only the right answer.
    """
    mob = DoubleArrow(np.array(START), np.array(END), buff=0)
    x1, _, _, _ = shaft(capture(renderer, mob))
    apex_x = screen(mob.get_start())[0]
    base_x = screen(np.asarray(mob.get_points(), dtype=float)[0])[0]
    assert base_x - apex_x > 30, "test setup: tip is %s px long" % (
        base_x - apex_x,)
    assert x1 >= apex_x + 0.9 * (base_x - apex_x), (
        "shaft starts %.1f px from the apex, expected the head base "
        "(%.1f px from it)" % (x1 - apex_x, base_x - apex_x))


def test_plain_arrow_is_unchanged(renderer):
    """An ordinary `Arrow` has no tip at its start end: `get_start()` IS the
    shaft's first point, so it must still be drawn exactly there."""
    mob = Arrow(np.array([-1.0, 0.1, 0.0]), np.array([1.0, 0.1, 0.0]), buff=0)
    own = np.asarray(mob.get_points(), dtype=float)
    x1, y1, x2, y2 = shaft(capture(renderer, mob))
    assert (x1, y1) == pytest.approx(screen(mob.get_start()), abs=0.5)
    assert (x2, y2) == pytest.approx(screen(own[-1]), abs=0.5)


def head_points(name, args):
    """Vertices of a head primitive, honouring each primitive's layout."""
    def verts(flat, n):
        flat = list(flat)
        stride = len(flat) // int(n)
        return [(float(flat[stride * i]), float(flat[stride * i + 1]))
                for i in range(int(n))]
    try:
        if name == "AddBezierPath":
            return verts(args[0], args[1])
        if name == "AddLineStrip":
            return verts(args[0], args[2])
        if name == "AddPolygon":
            return verts(args[10], args[9])
    except Exception:
        return []
    return []


def test_both_heads_are_still_drawn(renderer):
    """Fixing the shaft must not cost a head: `_send_arrow` draws `mob.tip`,
    and the family walk in `vulkan_bind` draws the other submobject --
    `start_tip` -- on top of it."""
    mob = DoubleArrow(np.array(START), np.array(END), buff=0)
    calls = capture(renderer, mob)
    heads = [head_points(n, a) for n, a in calls if n != "AddLine"]
    heads = [h for h in heads if h]
    assert len(heads) == 2, "expected two heads, got %d" % len(heads)
    mid = (screen(START)[0] + screen(END)[0]) / 2.0
    sides = set()
    for pts in heads:
        cx = sum(p[0] for p in pts) / len(pts)
        sides.add("left" if cx < mid else "right")
    assert sides == {"left", "right"}, "heads on sides %s" % (sides,)
