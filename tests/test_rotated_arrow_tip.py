"""A rotated Arrow's head must be drawn where the rotation puts it -- not crash.

`scenes/57_...` (Rotating with about_point) is the only demo that *turns* an
Arrow, and it died on every frame of it:

    vulkan_shapes.py, _send_arrow_tip:
        moved = centre + np.array([d[0] * ca - d[1] * sa,
                                   d[0] * sa + d[1] * ca])
    ValueError: operands could not be broadcast together with shapes (3,) (2,)

`centre` and `d = tip.get_center() - centre` are 3D points and only the xy
part of the rotated vector was built, so *any* arrow with a non-zero rotation
raised.  Rotating about z leaves z alone, so the rotated offset keeps the
third component and the whole tip rides around the rotation centre.

Pure Python: captures the DLL calls, no GPU work beyond opening the window.

Run with::

    python -X utf8 -m pytest tests/test_rotated_arrow_tip.py -q
"""

import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import real_time_manim.vulkan_bind as vb
    from manim import Arrow
    from real_time_manim.vulkan_util import manim_to_screen
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)

W, H = 1920, 1080
START, END = np.array([-2.0, -1.0, 0.0]), np.array([2.0, 1.0, 0.0])
CENTRE = np.array([0.0, 0.0, 0.0])       # where scene 57 rotates about


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


def capture(renderer, mob, rot=0.0):
    """Send `mob` through the real dispatch at a screen rotation."""
    rec = Recorder()
    real = renderer.dll
    renderer.dll = rec
    try:
        renderer._send(mob, rot)
    finally:
        renderer.dll = real
    return rec.calls


def _verts(flat, n):
    flat = list(flat)
    stride = len(flat) // int(n)
    return [(float(flat[stride * i]), float(flat[stride * i + 1]))
            for i in range(int(n))]


def head_centroid(calls):
    """Screen centroid of every recorded head primitive, or None."""
    pts = []
    for name, args in calls:
        try:
            if name == "AddBezierPath":
                pts += _verts(args[0], args[1])
            elif name == "AddLineStrip":
                pts += _verts(args[0], args[2])
            elif name == "AddPolygon":
                pts += _verts(args[10], args[9])
        except Exception:
            continue
    if not pts:
        return None
    return np.array([sum(p[0] for p in pts) / len(pts),
                     sum(p[1] for p in pts) / len(pts)])


def _arrow():
    mob = Arrow(START, END, buff=0)
    mob._rotation_about_point = CENTRE.copy()
    return mob


def test_rotated_arrow_does_not_raise(renderer):
    """The crash itself: scene 57 rendered zero frames."""
    calls = capture(renderer, _arrow(), rot=0.7)
    assert calls, "the rotated arrow emitted nothing"


def test_unrotated_arrow_still_draws_a_head(renderer):
    """Control, so the next test cannot pass by drawing nothing."""
    assert head_centroid(capture(renderer, _arrow(), rot=0.0)) is not None


def test_head_rides_around_the_rotation_centre(renderer):
    """The tip must land where a z-rotation about `centre` puts it.

    ``_send_vmobject`` rotates the tip about its *own* centre, so the offset
    this function adds is what carries it around the arrow's rotation centre:
    ``centre + Rz(theta) @ (tip_centre - centre)``.  Building only the xy part
    of that vector raised instead -- and dropping the rotation altogether
    (the tempting way to silence the broadcast) would leave the head stuck at
    its unrotated spot while the shaft turned.
    """
    mob = _arrow()
    theta = math.pi / 2.0
    tc = np.asarray(mob.tip.get_center(), dtype=float)
    expected = CENTRE + np.array([
        math.cos(theta) * (tc[0] - CENTRE[0]) - math.sin(theta) * (tc[1] - CENTRE[1]),
        math.sin(theta) * (tc[0] - CENTRE[0]) + math.cos(theta) * (tc[1] - CENTRE[1]),
        tc[2],
    ])
    want = manim_to_screen(expected[0], expected[1], W, H, expected[2])

    got = head_centroid(capture(renderer, mob, rot=theta))
    assert got is not None, "the arrow head was not drawn"
    # the recorded primitive is the head's outline, so its centroid is a
    # couple of px off the mobject's own centre -- 12 px still catches a
    # head that never moved (hundreds of px away for this arrow)
    assert np.hypot(got[0] - want[0], got[1] - want[1]) < 12.0, (
        "head drawn at (%.1f, %.1f), the rotation puts it at (%.1f, %.1f)"
        % (got[0], got[1], want[0], want[1]))
