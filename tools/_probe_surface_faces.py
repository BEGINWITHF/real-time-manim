# -*- coding: utf-8 -*-
"""Compare RTM's surface-face geometry against ManimCE's, window-free.

Builds the 07 `plot_surface` mobject at the sample's final camera orientation
and, for every face:

  * counts the native fill calls RTM's senders actually issue (stub DLL), and
  * projects the face's points through RTM's own viewport
    (``camera_state.Viewport.project``) and through manim's own
    ``ThreeDCamera.project_point`` -> pixel coords, then compares them.

The point is to separate "faces dropped by dispatch" from "faces at the wrong
place".

    python tools/_probe_surface_faces.py --phi 1.1 --theta -0.6
"""
from __future__ import annotations

import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np

from manim import ThreeDAxes, ThreeDScene
from manim._config import config as _config
import real_time_manim.camera_state as cs
import real_time_manim.vulkan_bind as vb
from tools.paint_order_probe import _Recorder

W, H = 1920, 1080


def ce_pixel(cam, point):
    p = np.asarray(cam.project_point(np.asarray(point, dtype=float)), dtype=float)
    fw = float(_config.frame_width)
    fh = float(_config.frame_height)
    return ((p[0] + fw / 2) / fw * W, (fh / 2 - p[1]) / fh * H)


def build(phi, theta):
    scene = ThreeDScene()
    scene.camera.set_phi(phi)
    scene.camera.set_theta(theta)
    ax = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-2, 2, 1))
    surf = ax.plot_surface(
        lambda u, v: 0.6 * (np.sin(u) * np.cos(v)),
        u_range=(-3, 3), v_range=(-3, 3), resolution=(8, 8))
    scene.add(ax)
    scene.add(surf)
    return scene, surf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phi", type=float, default=1.1)
    ap.add_argument("--theta", type=float, default=-0.6)
    args = ap.parse_args()

    scene, surf = build(args.phi, args.theta)
    cam = scene.camera
    print("faces: %d   resolution=%s" % (len(surf.list_of_faces), surf.resolution))

    window = vb.MLWindow(1920, 1080, hidden=True)
    rec = _Recorder()
    real = window.dll
    window.dll = rec
    # publish the same viewport the window would for this scene
    cs.set_viewport_from_scene(scene)
    try:
        window.sync(scene)
    finally:
        window.dll = real
        try:
            window.close()
        except Exception:
            pass
    counts = {}
    for name, _a in rec.calls:
        counts[name] = counts.get(name, 0) + 1
    print("native calls:", counts)

    vp = cs.get_viewport()
    print("viewport rotation set:", vp is not None and vp.rotation is not None)
    cam.reset_rotation_matrix()

    # per-face geometry comparison (corner points only)
    worst = []
    for face in surf.list_of_faces:
        pts = np.asarray(face.get_points(), dtype=float)
        anchors = pts[::3]                      # corner anchors of the quad
        rtm = np.array([vp.project(p[0], p[1], W, H, p[2]) for p in anchors])
        ce = np.array([ce_pixel(cam, p) for p in anchors])
        d = np.abs(rtm - ce).max()
        worst.append((d, face.u_index, face.v_index, rtm.mean(axis=0),
                      ce.mean(axis=0)))
    worst.sort(reverse=True)
    print("\nworst faces (max px deviation of any corner):")
    for d, ui, vi, rm, cm in worst[:10]:
        print("  face(%d,%d)  d=%7.2f  rtm_centre=(%7.1f,%7.1f) "
              "ce_centre=(%7.1f,%7.1f)"
              % (ui, vi, d, rm[0], rm[1], cm[0], cm[1]))
    print("  ... %d faces within 2 px" % sum(1 for d, *_ in worst if d <= 2.0))
    print("  median d=%.2f" % float(np.median([d for d, *_ in worst])))


if __name__ == "__main__":
    main()
