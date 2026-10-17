# -*- coding: utf-8 -*-
"""``Axes.plot_surface`` must build, project and fill its faces exactly as CE.

Regression for the wiki 07 sample
``05-坐标系与图表/assets/RTM output/07-极坐标与三维坐标系-surface.mp4`` -- the
worst A/B diff anywhere in the wiki (mean|diff| 25.04, 125 frames over the 4.0
threshold).  The archived RTM clip was a strict subset of its ManimCE twin
(every bright pixel of one was bright in the other, IoU 0.63) and carried only
45 % of the surface ink on the top-down view: the per-face fills were being
truncated by the per-frame vertex budget in ``native/draw/draw_bezier.c`` --
exactly the bug already pinned by ``tests/test_focuson_screen_fill.py``.
Re-rendered with the fix (and the sample's real parameters: ``sin(u)*cos(v)``,
``resolution=(12, 12)``) the pair measures mean|diff| 0.79 with 0 frames over.

These tests are **window-free and GPU-free**: they build the real
``ThreeDAxes`` / ``Surface`` mobjects, compare the numbers RTM's senders derive
against manim's own, and drive the native tessellator through its headless
``RtmTest_*`` probes (no window, no Vulkan surface, no image).

Run with::

    python -X utf8 -m pytest tests/test_plot_surface.py -q
"""

from __future__ import annotations

import ctypes
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
import pytest

from manim import ThreeDAxes, ThreeDScene

import real_time_manim.camera_state as cs

DLL_PATH = os.path.join(REPO, "real_time_manim", "vulkan_core.dll")
MAX_VERTICES = 4194304            # native/draw_common.h
PIXEL_W, PIXEL_H = 1920, 1080

# the 07 sample's scene parameters, recovered from the archived CE twin
U_RANGE = (-3, 3)
V_RANGE = (-3, 3)
RESOLUTION = (12, 12)
TOP_DOWN = (0.0, -np.pi / 2)      # ThreeDCamera defaults
SAMPLE_CAMERA = (1.1, -0.6)       # move_camera(theta=-0.6, phi=1.1)


def surface_fn(u, v):
    return np.sin(u) * np.cos(v)


def build(phi, theta, resolution=RESOLUTION):
    """The sample's ThreeDAxes + plot_surface at one camera orientation."""
    scene = ThreeDScene()
    scene.camera.set_phi(phi)
    scene.camera.set_theta(theta)
    scene.camera.reset_rotation_matrix()
    axes = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1),
                      z_range=(-2, 2, 1))
    surf = axes.plot_surface(surface_fn, u_range=U_RANGE, v_range=V_RANGE,
                             resolution=resolution)
    return scene, axes, surf


def c2p_corners(axes, face):
    """The four data-space corners of one uv cell, mapped through c2p."""
    return np.array([
        axes.c2p(face.u1, face.v1, surface_fn(face.u1, face.v1)),
        axes.c2p(face.u2, face.v1, surface_fn(face.u2, face.v1)),
        axes.c2p(face.u2, face.v2, surface_fn(face.u2, face.v2)),
        axes.c2p(face.u1, face.v2, surface_fn(face.u1, face.v2)),
    ])


# --------------------------------------------------------------------------- #
# geometry: the Surface is a u/v grid of c2p-mapped quads
# --------------------------------------------------------------------------- #

def test_plot_surface_builds_the_uv_face_grid():
    """``resolution=(12, 12)`` is 12*12 faces, each one uv cell of the range."""
    _scene, _axes, surf = build(*TOP_DOWN)

    assert len(surf.list_of_faces) == RESOLUTION[0] * RESOLUTION[1]

    u_step = (U_RANGE[1] - U_RANGE[0]) / RESOLUTION[0]
    v_step = (V_RANGE[1] - V_RANGE[0]) / RESOLUTION[1]
    seen = set()
    for face in surf.list_of_faces:
        assert 0 <= face.u_index < RESOLUTION[0]
        assert 0 <= face.v_index < RESOLUTION[1]
        assert face.u2 - face.u1 == pytest.approx(u_step)
        assert face.v2 - face.v1 == pytest.approx(v_step)
        seen.add((face.u_index, face.v_index))
    assert len(seen) == RESOLUTION[0] * RESOLUTION[1], "duplicate uv cells"


def test_every_face_quad_passes_through_its_c2p_corners():
    """Each face's path must contain all four ``c2p(u, v, f(u, v))`` corners.

    This is the sender's contract: a face of the plotted surface lands on the
    axes' own mapping, not on a raw uv rectangle.
    """
    _scene, axes, surf = build(*TOP_DOWN)
    missing = 0
    for face in surf.list_of_faces:
        pts = np.asarray(face.points, dtype=float)
        for corner in c2p_corners(axes, face):
            if np.abs(pts - corner).max(axis=1).min() > 1e-6:
                missing += 1
    assert missing == 0, "%d face corners are not on the axes c2p mapping" % missing


# --------------------------------------------------------------------------- #
# projection: the RTM sender must land on manim's own pixels
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("camera", [TOP_DOWN, SAMPLE_CAMERA])
def test_surface_points_project_to_manims_own_pixels(camera):
    """RTM's viewport must reproduce ``Camera.points_to_pixel_coords``.

    Every sender converts manim units to pixels through
    ``camera_state.Viewport.project``; manim's ``ThreeDCamera`` does it through
    ``points_to_pixel_coords``.  A systematic mismatch here would place the
    whole plotted surface off the axes.
    """
    scene, _axes, surf = build(*camera)
    viewport = cs.viewport_from_scene(scene)
    assert viewport is not None and viewport.rotation is not None, (
        "a ThreeDScene must publish a rotated viewport")

    cam = scene.camera
    worst = 0.0
    for face in surf.list_of_faces:
        pts = np.asarray(face.points, dtype=float)
        reference = cam.points_to_pixel_coords(face, pts)   # int pixels
        got = np.array([viewport.project(x, y, PIXEL_W, PIXEL_H, z)
                        for x, y, z in pts])
        worst = max(worst, float(np.abs(reference - got).max()))
    # ``points_to_pixel_coords`` truncates to integer pixels, so 1 px is exact
    assert worst <= 1.0, (
        "RTM's projection is %.2f px away from manim's own points_to_pixel_coords"
        % worst)


# --------------------------------------------------------------------------- #
# fill budget: a plotted surface must not lose its faces
# --------------------------------------------------------------------------- #

def _load_dll():
    if not os.path.exists(DLL_PATH):
        pytest.skip("vulkan_core.dll not built")
    try:
        dll = ctypes.CDLL(DLL_PATH)
    except OSError as exc:                              # pragma: no cover
        pytest.skip("vulkan_core.dll cannot be loaded: %s" % exc)
    if not hasattr(dll, "RtmTest_VertexCount"):
        pytest.skip("the DLL predates the headless RtmTest_* probes -- rebuild "
                    "the native side (native/build.ps1)")
    dll.RtmTest_VertexCount.restype = ctypes.c_uint
    dll.RtmTest_ReadVertex.restype = ctypes.c_int
    return dll


def _add_quad(dll, corners):
    """One filled bezier quad; the four cubics share their endpoints."""
    flat = []
    for i in range(4):
        a = corners[i]
        b = corners[(i + 1) % 4]
        flat.extend([a[0], a[1], 0.0,
                     a[0] + (b[0] - a[0]) / 3.0,
                     a[1] + (b[1] - a[1]) / 3.0, 0.0,
                     a[0] + 2.0 * (b[0] - a[0]) / 3.0,
                     a[1] + 2.0 * (b[1] - a[1]) / 3.0, 0.0,
                     b[0], b[1], 0.0])
    arr = (ctypes.c_float * len(flat))(*flat)
    dll.AddBezierPath(
        arr, ctypes.c_int(len(flat) // 3),
        ctypes.c_int(41), ctypes.c_int(53), ctypes.c_int(147), ctypes.c_float(0.5),
        ctypes.c_int(41), ctypes.c_int(53), ctypes.c_int(147), ctypes.c_float(1.0),
        ctypes.c_float(1.0), ctypes.c_int(1), ctypes.c_int(1), ctypes.c_float(1.0),
        ctypes.c_int(41), ctypes.c_int(53), ctypes.c_int(147),
        ctypes.c_float(0.0), ctypes.c_float(0.0),
        ctypes.c_float(0.0), ctypes.c_float(0.0))


def test_a_plotted_surface_fills_the_whole_frame_without_capping_out():
    """144 screen-covering faces must cost O(rows), not 6 vertices per pixel.

    The top-down view makes every face a screen-filling quad.  Before the
    ``native/draw/draw_bezier.c`` span-quad fix the aggregate cost was
    ~6 * covered area = several times ``MAX_VERTICES``, so the scanline ran out
    of budget part-way down the frame and the rest of the surface was never
    filled -- the archived RTM clip carried 45 % of its twin's surface ink with
    the missing part a strict subset of it.
    """
    scene, axes, surf = build(*TOP_DOWN)
    viewport = cs.viewport_from_scene(scene)

    dll = _load_dll()
    dll.RtmTest_SetSurfaceSize(ctypes.c_uint(PIXEL_W), ctypes.c_uint(PIXEL_H))
    dll.RtmTest_ResetFrame()

    for face in surf.list_of_faces:
        corners = [viewport.project(x, y, PIXEL_W, PIXEL_H, z)
                   for x, y, z in c2p_corners(axes, face)]
        _add_quad(dll, corners)
    dll.BuildVerticesFromBezierPaths()

    count = int(dll.RtmTest_VertexCount())
    assert count < MAX_VERTICES // 4, (
        "%d vertices for a plotted surface: the per-pixel fill emitter would "
        "need ~%d against a budget of %d, so the fill was abandoned mid-frame"
        % (count, 144 * 20000 * 6, MAX_VERTICES))

    out = (ctypes.c_float * 6)()
    xs, ys = [], []
    for i in range(count):
        assert dll.RtmTest_ReadVertex(ctypes.c_int(i), out)
        xs.append((out[0] + 1.0) / 2.0 * PIXEL_W)
        ys.append((out[1] + 1.0) / 2.0 * PIXEL_H)
    xs, ys = np.array(xs), np.array(ys)
    assert ys.min() <= 1.0 and ys.max() >= PIXEL_H - 1.0, (
        "the surface's fill stops at y=[%.1f..%.1f]: it was truncated before "
        "the bottom of the %d-row frame" % (ys.min(), ys.max(), PIXEL_H))
    assert xs.min() <= PIXEL_W * 0.2 and xs.max() >= PIXEL_W * 0.8, (
        "the surface's fill spans only x=[%.1f..%.1f]" % (xs.min(), xs.max()))
