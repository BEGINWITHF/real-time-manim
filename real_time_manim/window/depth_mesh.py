"""Experimental automatic depth-tested mesh for flat-shaded ``Surface`` roots.

The legacy painter draws every face as an independent polygon in a sorted
order.  That is correct for separated, convex shapes but cannot resolve a
surface that overlaps itself: neighbouring cells, a rim crossing the surface,
or a folded sheet end up painted in list order.

``MeshBatch`` (``real_time_manim.mesh``) already sends an explicit triangle
batch through the native depth buffer.  This module builds the same batch
automatically from ordinary ``Surface`` mobjects, so scene code keeps the
normal manim spelling::

    surf = Surface(...)
    surf.set_fill_by_checkerboard(...)
    self.add(surf)

Opt in with ``RTM_AUTO_DEPTH=1``.  Default off: the painter path is untouched.

Scope of this first prototype -- deliberately narrow, so the opt-in cannot
change scenes it does not understand:

* only top-level ``Surface`` roots (``Surface``/``Sphere``/``Torus``/
  ``Cylinder``/... -- anything with ``list_of_faces``);
* every face must be opaque (``fill_opacity`` >= 0.999) and flat-shaded
  (``shade_in_3d`` false);
* the stroke must be invisible or the same colour as the fill, because the
  depth batch carries fills only;
* no other lit 3D geometry anywhere in the frame; a scene that mixes a
  ``Surface`` with a ``Cube`` would need both on the depth path, so it falls
  back to the painter as a whole.

Everything else -- text, images, fixed-in-frame captions, the rim ``Circle``
of a membrane -- stays on the painter and is drawn after the mesh, i.e. on
top.  That is the intended layering: 3D world first, 2D overlay second.

The depth written per vertex is the camera-space z, normalised over the batch
so the nearest corner maps to 0.01 and the farthest to 0.99.  x/y come from
the same projection the painter uses (``Viewport.project`` maths, vectorised),
so mesh and painter agree pixel for pixel.
"""
from __future__ import annotations

import os

import numpy as np

from real_time_manim.camera_state import screen_scale

_TRUTHY = {"1", "true", "yes", "on"}


def enabled() -> bool:
    """True when the opt-in environment variable is set."""
    return os.environ.get("RTM_AUTO_DEPTH", "").strip().lower() in _TRUTHY


def _is_surface(root) -> bool:
    return hasattr(root, "list_of_faces") and hasattr(root, "func")


def _corners(face):
    """World-space corners of a face as a convex ring, or ``None``.

    ``Surface`` builds each cell with ``set_points_as_corners`` over its four
    UV corners.  The *start* anchors are those corners; a cell touching the
    disc centre can repeat its first corner, so consecutive duplicates are
    dropped and the result is a triangle instead of a degenerate quad.
    """
    anchors = np.asarray(face.get_start_anchors(), dtype=np.float64)
    if anchors.ndim != 2 or anchors.shape[1] != 3 or len(anchors) < 3:
        return None
    if not np.all(np.isfinite(anchors)):
        return None

    ring = [anchors[0]]
    for point in anchors[1:]:
        if not np.allclose(point, ring[-1], atol=1e-9):
            ring.append(point)
    while len(ring) > 1 and np.allclose(ring[0], ring[-1], atol=1e-9):
        ring.pop()
    return np.asarray(ring, dtype=np.float64) if len(ring) >= 3 else None


def _stroke_matches_fill(face) -> bool:
    opacity = float(face.get_stroke_opacity())
    width = float(face.get_stroke_width())
    if opacity <= 0.01 or width <= 0.01:
        return True
    fill = np.asarray(face.get_fill_color().to_rgb(), dtype=np.float64)
    stroke = np.asarray(face.get_stroke_color().to_rgb(), dtype=np.float64)
    return float(np.max(np.abs(fill - stroke))) <= 2.0 / 255.0


def collect_roots(roots, fixed_ids):
    """Eligible ``Surface`` roots for this frame, or ``None`` to stay painter.

    ``None`` means "do not switch this frame": one ineligible surface, or any
    other lit 3D geometry, would break cross-object ordering if only part of
    the frame moved to the depth buffer.
    """
    surfaces = []
    for root in roots:
        if id(root) in fixed_ids:
            continue
        if _is_surface(root):
            faces = list(getattr(root, "list_of_faces", ()) or ())
            if not faces:
                continue
            for face in faces:
                if _corners(face) is None:
                    return None
                if float(face.get_fill_opacity()) < 0.999:
                    return None
                if getattr(face, "shade_in_3d", False):
                    return None
                if not _stroke_matches_fill(face):
                    return None
                rgbas = np.asarray(face.fill_rgbas, dtype=np.float64)
                if rgbas.ndim != 2 or rgbas.shape[1] != 4 or len(rgbas) == 0:
                    return None
                if len(rgbas) > 1 and float(
                        np.ptp(rgbas, axis=0).max()) > 1.0 / 255.0:
                    return None
            surfaces.append(root)
            continue

        # Any other lit, visible face would also need the depth path.  Text,
        # images and stroke-only overlays have shade_in_3d false and pass.
        stack = list(getattr(root, "submobjects", ()) or ())
        while stack:
            member = stack.pop()
            if (getattr(member, "shade_in_3d", False)
                    and float(getattr(member, "fill_opacity", 0.0)) > 0.01):
                return None
            stack.extend(getattr(member, "submobjects", ()) or ())

    return surfaces or None


def build_vertices(surfaces, viewport, width, height):
    """Project every face to ``(x_ndc, y_ndc, depth, rgba)`` triangle vertices."""
    triangles = []
    colours = []
    for root in surfaces:
        for face in root.list_of_faces:
            corners = _corners(face)
            if corners is None:
                return None
            rgbas = np.asarray(face.fill_rgbas, dtype=np.float64)
            if rgbas.ndim != 2 or rgbas.shape[1] != 4 or len(rgbas) == 0:
                return None
            rgba = rgbas.mean(axis=0)
            # Fan from the first corner: two triangles for a quad, one for a
            # centre wedge whose first corner repeats.
            for k in range(1, len(corners) - 1):
                triangles.append(np.stack(
                    [corners[0], corners[k], corners[k + 1]]))
                colours.append(np.tile(rgba, (3, 1)))

    if not triangles:
        return None

    tri = np.asarray(triangles, dtype=np.float64)        # (T, 3, 3)
    tri_colours = np.asarray(colours, dtype=np.float64)  # (T, 3, 4)

    pts = tri.reshape(-1, 3)
    rot = np.asarray(viewport.rotation, dtype=np.float64)
    centre = np.asarray(getattr(viewport, "frame_center", (0.0, 0.0, 0.0)),
                        dtype=np.float64)
    q = (pts - centre) @ rot.T

    qx, qy = q[:, 0], q[:, 1]
    focal = getattr(viewport, "focal_distance", None)
    if focal and abs(focal) > 1e-6:
        denom = focal - q[:, 2]
        factor = np.where(np.abs(denom) > 1e-6, focal / denom, 1.0)
        if getattr(viewport, "exponential", False):
            factor = np.where(q[:, 2] < 0.0, factor,
                              np.exp(q[:, 2] / focal))
        qx = qx * factor
        qy = qy * factor

    scale = screen_scale(width, height, viewport.height)
    x = width * 0.5 + qx * scale
    y = height * 0.5 - qy * scale

    # Larger camera-space z is nearer; the native pipeline keeps smaller
    # depth, so the nearest corner must map to the small end.
    z = q[:, 2]
    lo, hi = float(z.min()), float(z.max())
    if hi - lo < 1e-9:
        depth = np.full(len(z), 0.5, dtype=np.float64)
    else:
        depth = 0.01 + 0.98 * (hi - z) / (hi - lo)

    out = np.empty((len(pts), 7), dtype=np.float32)
    out[:, 0] = (x / width) * 2.0 - 1.0
    out[:, 1] = (y / height) * 2.0 - 1.0
    out[:, 2] = depth
    out[:, 3:7] = tri_colours.reshape(-1, 4)
    return len(out), out
