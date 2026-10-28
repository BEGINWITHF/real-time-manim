"""Depth-tested triangle meshes for the native renderer.

The legacy RTM/manim path paints 2D primitives in document/depth order.  That
cannot give per-pixel occlusion for a mesh (intersecting quads, a rim crossing a
surface, coplanar cells).  ``MeshBatch`` bypasses the painter for geometry:
``MLWindow.sync`` hands its projected vertices to the native depth-tested mesh
pipeline, and the ordinary 2D sender path still paints afterwards.

Coordinates are world (manim) coordinates.  Each quad is four points and four
RGBA colours; ``build_vertices`` triangulates and applies the current viewport.
"""
from __future__ import annotations

import ctypes

import numpy as np

from real_time_manim.camera_state import screen_scale


class MeshBatch:
    """A batch of coloured quads rendered with a GPU depth buffer.

    ``quads`` is ``(Q, 4, 3)`` float, ``colors`` is ``(Q, 4, 4)`` float in
    ``[0, 1]``.  The arrays are public so an animation can update Z/colour
    slices in place without rebuilding the Python object.
    """

    def __init__(self):
        self.quads = np.empty((0, 4, 3), dtype=np.float64)
        self.colors = np.empty((0, 4, 4), dtype=np.float32)

    def append(self, quads, colors):
        quads = np.asarray(quads, dtype=np.float64)
        colors = np.asarray(colors, dtype=np.float32)
        if quads.ndim != 3 or quads.shape[1:] != (4, 3):
            raise ValueError("quads must have shape (Q, 4, 3)")
        if colors.shape != (quads.shape[0], 4, 4):
            raise ValueError("colors must have shape (Q, 4, 4)")
        self.quads = np.concatenate([self.quads, quads], axis=0)
        self.colors = np.concatenate([self.colors, colors], axis=0)
        return self

    def build_vertices(self, viewport, width, height):
        """Project to native ``(x_ndc, y_ndc, depth, rgba)`` triangle vertices."""
        if len(self.quads) == 0:
            return None

        # Two triangles per quad, preserving the quad's vertex colours.
        tri = np.concatenate(
            [
                self.quads[:, [0, 1, 2], :],
                self.quads[:, [0, 2, 3], :],
            ],
            axis=0,
        )
        cols = np.concatenate(
            [
                self.colors[:, [0, 1, 2], :],
                self.colors[:, [0, 2, 3], :],
            ],
            axis=0,
        )
        pts = tri.reshape(-1, 3)

        if viewport is None:
            s = screen_scale(width, height)
            x = width * 0.5 + pts[:, 0] * s
            y = height * 0.5 - pts[:, 1] * s
            depth = np.full(len(pts), 0.5, dtype=np.float32)
        else:
            s = screen_scale(width, height, viewport.height)
            cx, cy, cz = viewport.frame_center
            p = pts - np.array([cx, cy, cz], dtype=np.float64)
            rot = getattr(viewport, "rotation", None)
            if rot is not None:
                r = np.asarray(rot, dtype=np.float64)
                q = p @ r.T
                focal = viewport.focal_distance
                if focal and abs(focal) > 1e-6:
                    denom = focal - q[:, 2]
                    factor = np.where(
                        np.abs(denom) > 1e-6, focal / denom, 1.0
                    )
                    q[:, 0] *= factor
                    q[:, 1] *= factor
                p = q
            x = width * 0.5 + p[:, 0] * s
            y = height * 0.5 - p[:, 1] * s

            if rot is not None:
                rz = p[:, 2]
                focal = viewport.focal_distance
                scale = abs(focal) if focal and abs(focal) > 1e-6 else max(viewport.height, 1.0)
                # Smaller depth is nearer.  Linear camera-space depth is enough
                # for the small cells here and matches the painter's depth key.
                depth = np.clip(0.5 - 0.5 * rz / scale, 0.0, 1.0)
            else:
                depth = np.full(len(pts), 0.5, dtype=np.float32)

        ndc_x = (x / width) * 2.0 - 1.0
        ndc_y = (y / height) * 2.0 - 1.0

        n = len(pts)
        out = np.empty((n, 7), dtype=np.float32)
        out[:, 0] = ndc_x
        out[:, 1] = ndc_y
        out[:, 2] = depth
        out[:, 3:7] = cols.reshape(-1, 4)
        return n, out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
