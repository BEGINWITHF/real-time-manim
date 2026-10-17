"""Regression test: a screen-filling bezier path must finish its fill.

Report: wiki ``03-动画/强调与提示`` ``assets/RTM output/02-圈注与聚焦.mp4``
-- "圆形uncreate方向错误，聚焦动画播放错误".

``FocusOn``'s starting mobject is
``Dot(radius=frame_x_radius + frame_y_radius)`` -- 11.11 manim units, i.e.
LARGER than the frame -- so during the first half of the animation its fill
covers every pixel of the stage.  ``tessellate_fill`` used to emit six
vertices (two triangles) per covered pixel, which costs 6 * area: at
1920x1080 that path is 2 073 600 px = 12.4 M vertices against
``MAX_VERTICES = 4 194 304``.  The scanline therefore ran out of budget
part-way down the frame and ``return``ed, leaving everything below the cut
unfilled.  Measured on that clip (frame 401): ManimCE carries the purple
spotlight over the whole frame (row luma ~19.8 top to bottom) while RTM
matches it down to y=395 and is then PURE BLACK (row luma 0.000) to the
bottom -- a straight horizontal cut that walks down as the disc shrinks
(y=761 at f410, y=604 at f430), the signature of a shared per-frame budget
rather than of any geometry.

Fix (``native/draw/draw_bezier.c``): only the first and last pixel of a span
are partially covered, so the fully covered run in between collapses into a
single quad.  The fill now costs O(rows + columns) instead of O(area) -- at
most 18 vertices per row -- and every emitted pixel is bit-for-bit the one
the old per-pixel loop produced (interior coverage is exactly 1.0, edge
pixels keep their own partial quad).

These tests drive the real DLL headlessly through the ``RtmTest_*`` probe
entry points: no GPU, no window, no image, no rendering -- just
``AddBezierPath`` -> tessellate -> read the vertices back.  They need the
DLL to have been rebuilt after the fix (``native/build.ps1``, or
``native/build_msvc.bat`` on this machine).
"""

import ctypes
import math
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

DLL_PATH = os.path.join(REPO, "real_time_manim", "vulkan_core.dll")
MAX_VERTICES = 4194304            # native/draw_common.h

SURFACE = (1920, 1080)


def _load():
    if not os.path.exists(DLL_PATH):
        pytest.skip("vulkan_core.dll not built")
    try:
        d = ctypes.CDLL(DLL_PATH)
    except OSError as exc:          # pragma: no cover - non-Windows CI
        pytest.skip("vulkan_core.dll cannot be loaded: %s" % exc)
    # default restype is c_int; these probes return unsigned/count values
    if hasattr(d, "RtmTest_VertexCount"):
        d.RtmTest_VertexCount.restype = ctypes.c_uint
    if hasattr(d, "RtmTest_ReadVertex"):
        d.RtmTest_ReadVertex.restype = ctypes.c_int
    return d


def _call(dll, name, *args):
    fn = getattr(dll, name, None)
    if fn is None:
        raise AssertionError(
            "%s is missing from the built DLL -- rebuild the native side "
            "(native/build.ps1, or native/build_msvc.bat on Windows) so the "
            "tessellator fix and its probe entry points are in it" % name)
    return fn(*args)


@pytest.fixture(scope="module")
def dll():
    return _load()


def _begin(d, w=SURFACE[0], h=SURFACE[1]):
    """Fresh per-frame state: surface size, zeroed budget, empty path list."""
    _call(d, "RtmTest_SetSurfaceSize", ctypes.c_uint(w), ctypes.c_uint(h))
    _call(d, "RtmTest_ResetFrame")


def _add_path(d, pts, *, fill_opacity, alpha=1.0, show_fill=1, progress=1.0):
    """pts: list of (x, y) screen pixels, 4 per cubic, non-overlapping."""
    flat = []
    for (x, y) in pts:
        flat.extend((float(x), float(y), 0.0))
    arr = (ctypes.c_float * len(flat))(*flat)
    _call(d, "AddBezierPath",
          arr, ctypes.c_int(len(flat) // 3),
          ctypes.c_int(255), ctypes.c_int(255), ctypes.c_int(255), ctypes.c_float(0.0),
          ctypes.c_int(160), ctypes.c_int(32), ctypes.c_int(240), ctypes.c_float(fill_opacity),
          ctypes.c_float(progress), ctypes.c_int(0), ctypes.c_int(show_fill), ctypes.c_float(alpha),
          ctypes.c_int(160), ctypes.c_int(32), ctypes.c_int(240),
          ctypes.c_float(0.0), ctypes.c_float(0.0), ctypes.c_float(0.0), ctypes.c_float(0.0))


def _build(d):
    _call(d, "BuildVerticesFromBezierPaths")
    return int(_call(d, "RtmTest_VertexCount"))


def _vertex(d, i):
    out = (ctypes.c_float * 6)()
    ok = _call(d, "RtmTest_ReadVertex", ctypes.c_int(i), out)
    assert ok, "vertex %d out of range" % i
    return list(out)


def _to_px(v, w=SURFACE[0], h=SURFACE[1]):
    """Undo ``ToNDC`` (draw_common.h): pixel space, y down."""
    return ((v[0] + 1.0) / 2.0 * w, (v[1] + 1.0) / 2.0 * h)


def _circle_path(cx, cy, radius, n_cubics=8):
    """Manim's own circle layout: n cubics, non-overlapping 4-point groups."""
    k = 4.0 / 3.0 * math.tan(math.pi / (2 * n_cubics))
    pts = []
    for i in range(n_cubics):
        a0 = 2 * math.pi * i / n_cubics
        a1 = 2 * math.pi * (i + 1) / n_cubics
        p0 = (cx + radius * math.cos(a0), cy + radius * math.sin(a0))
        p3 = (cx + radius * math.cos(a1), cy + radius * math.sin(a1))
        t0 = (-math.sin(a0), math.cos(a0))
        t1 = (-math.sin(a1), math.cos(a1))
        p1 = (p0[0] + k * radius * t0[0], p0[1] + k * radius * t0[1])
        p2 = (p3[0] - k * radius * t1[0], p3[1] - k * radius * t1[1])
        pts.extend([p0, p1, p2, p3])
    return pts


def _rect_path(x0, y0, x1, y1):
    """Axis-aligned rectangle as four straight cubics."""
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    pts = []
    for i in range(4):
        a = corners[i]
        b = corners[(i + 1) % 4]
        pts.extend([a,
                    (a[0] + (b[0] - a[0]) / 3.0, a[1] + (b[1] - a[1]) / 3.0),
                    (a[0] + 2.0 * (b[0] - a[0]) / 3.0, a[1] + 2.0 * (b[1] - a[1]) / 3.0),
                    b])
    return pts


def test_screen_filling_focuson_path_completes(dll):
    """The FocusOn veil covers the frame: the fill must reach the bottom.

    Before the fix this submitted 6 vertices per pixel, hit MAX_VERTICES
    after ~364 rows and stopped -- the clip shows RTM black from y=395 down.
    """
    _begin(dll)
    # 11.11 units * 135 px/unit at 1080p -- FocusOn's starting Dot, centred
    # on the dot's position; big enough to cover every pixel of the stage.
    _add_path(dll, _circle_path(960.0, 796.0, 1500.0),
              fill_opacity=0.4, alpha=1.0)
    count = _build(dll)

    rows = SURFACE[1]
    # One quad per row, six vertices each; the loop allows at most two
    # partial edge pixels on top of that (18/row).  Anything in this window
    # means the scanline ran to the bottom of the surface.
    assert rows * 6 <= count <= rows * 18, (
        "%d vertices for a screen-filling path: the fill did not run to the "
        "bottom of the %d-row surface (the old 6-vertices-per-pixel emitter "
        "capped out at %d)" % (count, rows, MAX_VERTICES))

    ys = [_to_px(_vertex(dll, i))[1] for i in range(count)]
    xs = [_to_px(_vertex(dll, i))[0] for i in range(count)]
    assert max(ys) >= SURFACE[1] - 1.0, (
        "the lowest filled row is y=%.1f, i.e. the fill was abandoned "
        "mid-frame (this is the horizontal cut reported for "
        "02-圈注与聚焦.mp4)" % max(ys))
    assert min(ys) <= 1.0
    assert min(xs) <= 1.0 and max(xs) >= SURFACE[0] - 1.0


def test_partial_edge_pixels_keep_their_own_coverage(dll):
    """The merged run must not change the anti-aliased edges.

    Rectangle spanning x=10.3..50.7, y=10..50: pixel 10 and pixel 50 are 70 %
    covered and keep their own quad at 0.7 * fill_alpha; the 39 pixels
    between them (11..49) are fully covered and become ONE quad at
    fill_alpha.  40 rows * 3 quads = 720 vertices.
    """
    _begin(dll, w=100, h=100)
    _add_path(dll, _rect_path(10.3, 10.0, 50.7, 50.0), fill_opacity=0.5)
    count = _build(dll)

    assert count == 40 * 18, count

    # first row: [left partial][merged run][right partial]
    left = _to_px(_vertex(dll, 0), 100, 100)
    mid = _to_px(_vertex(dll, 6), 100, 100)
    right = _to_px(_vertex(dll, 12), 100, 100)
    assert abs(left[0] - 10.0) < 1e-3, left          # pixel 10 starts at 10
    assert abs(mid[0] - 11.0) < 1e-3, mid            # run starts at ceil(10.3)
    assert abs(right[0] - 50.0) < 1e-3, right        # pixel 50 starts at 50

    fill_a = _vertex(dll, 6)[5]
    edge_a = _vertex(dll, 0)[5]
    assert abs(fill_a - 0.5) < 1e-4, fill_a          # coverage == 1.0
    assert abs(edge_a - 0.5 * 0.7) < 2e-3, edge_a    # coverage == 0.7


def test_a_small_fill_is_unaffected_by_the_run_merge(dll):
    """Non-regression: a fully on-screen, pixel-aligned path costs 6/row."""
    _begin(dll, w=100, h=100)
    _add_path(dll, _rect_path(20.0, 30.0, 60.0, 70.0), fill_opacity=1.0)
    count = _build(dll)
    assert count == 40 * 6, count
    xs = [_to_px(_vertex(dll, i), 100, 100)[0] for i in range(count)]
    assert abs(min(xs) - 20.0) < 1e-3
    assert abs(max(xs) - 60.0) < 1e-3
