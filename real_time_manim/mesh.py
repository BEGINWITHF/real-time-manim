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
import warnings

import numpy as np

from real_time_manim.camera_state import screen_scale

#: Native depth-tested mesh capacity (``native/shared_types.h``).  The legacy
#: path expands every quad to six vertices; the indexed path uses four
#: vertices plus six indices, so it fits 1.5x as many quads.
MAX_MESH_VERTS = 524_288
MAX_QUADS_LEGACY = MAX_MESH_VERTS // 6    # 87,381 quads, six vertices each
MAX_QUADS_INDEXED = MAX_MESH_VERTS // 4   # 131,072 quads, four vertices each
MAX_QUADS = MAX_QUADS_INDEXED


class MeshBatch:
    """A batch of coloured quads rendered with a GPU depth buffer.

    ``quads`` is ``(Q, 4, 3)`` float, ``colors`` is ``(Q, 4, 4)`` float in
    ``[0, 1]``.  The arrays are public so an animation can update Z/colour
    slices in place without rebuilding the Python object.

    The native mesh pipeline holds :data:`MAX_MESH_VERTS` vertices
    (:attr:`MAX_QUADS_INDEXED` quads through the indexed path,
    :attr:`MAX_QUADS_LEGACY` through the old six-vertex path).  ``append``
    raises before a batch can cross the indexed limit; both builders
    additionally truncate to whole quads (one warning) if the public arrays
    were grown directly, so a partial triangle/quad can never reach native.
    """

    MAX_MESH_VERTS = MAX_MESH_VERTS
    MAX_QUADS = MAX_QUADS
    MAX_QUADS_INDEXED = MAX_QUADS_INDEXED
    MAX_QUADS_LEGACY = MAX_QUADS_LEGACY

    def __init__(self):
        self.quads = np.empty((0, 4, 3), dtype=np.float64)
        self.colors = np.empty((0, 4, 4), dtype=np.float32)
        self._capacity_warned = False

    def append(self, quads, colors):
        quads = np.asarray(quads, dtype=np.float64)
        colors = np.asarray(colors, dtype=np.float32)
        if quads.ndim != 3 or quads.shape[1:] != (4, 3):
            raise ValueError("quads must have shape (Q, 4, 3)")
        if colors.shape != (quads.shape[0], 4, 4):
            raise ValueError("colors must have shape (Q, 4, 4)")
        total = len(self.quads) + len(quads)
        if total > self.MAX_QUADS:
            raise ValueError(
                "MeshBatch capacity exceeded: %d + %d = %d quads "
                "(%d indexed vertices), but MAX_QUADS is %d (%d vertices). "
                "Reduce the quad count, or drop whole quads before appending."
                % (len(self.quads), len(quads), total, total * 4,
                   self.MAX_QUADS, self.MAX_QUADS * 4)
            )
        self.quads = np.concatenate([self.quads, quads], axis=0)
        self.colors = np.concatenate([self.colors, colors], axis=0)
        return self

    @staticmethod
    def _project(pts, cols, viewport, width, height):
        """Project world points+corners to native ``(ndc, rgba)`` rows."""
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
        return n, out

    def build_vertices(self, viewport, width, height):
        """Legacy non-indexed path: six vertices per quad."""
        if len(self.quads) == 0:
            return None

        quads = self.quads
        colors = self.colors
        cap = self.MAX_QUADS_LEGACY
        if len(quads) > cap:
            if not self._capacity_warned:
                warnings.warn(
                    "MeshBatch has %d quads (%d vertices), over the legacy "
                    "MAX_QUADS_LEGACY=%d (%d vertices); dropping the last %d "
                    "quads so the native mesh stays whole."
                    % (len(quads), len(quads) * 6, cap, cap * 6,
                       len(quads) - cap),
                    RuntimeWarning, stacklevel=2)
                self._capacity_warned = True
            quads = quads[:cap]
            colors = colors[:cap]

        # Two triangles per quad, preserving the quad's vertex colours.
        tri = np.concatenate(
            [
                quads[:, [0, 1, 2], :],
                quads[:, [0, 2, 3], :],
            ],
            axis=0,
        )
        cols = np.concatenate(
            [
                colors[:, [0, 1, 2], :],
                colors[:, [0, 2, 3], :],
            ],
            axis=0,
        )
        n, out = self._project(tri.reshape(-1, 3), cols.reshape(-1, 4),
                               viewport, width, height)
        return n, out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

    def build_indexed_vertices(self, viewport, width, height):
        """Indexed path: four vertices per quad + six uint32 indices."""
        if len(self.quads) == 0:
            return None

        quads = self.quads
        colors = self.colors
        cap = self.MAX_QUADS_INDEXED
        if len(quads) > cap:
            if not self._capacity_warned:
                warnings.warn(
                    "MeshBatch has %d quads (%d vertices), over "
                    "MAX_QUADS_INDEXED=%d (%d vertices); dropping the last "
                    "%d quads so the native mesh stays whole."
                    % (len(quads), len(quads) * 4, cap, cap * 4,
                       len(quads) - cap),
                    RuntimeWarning, stacklevel=2)
                self._capacity_warned = True
            quads = quads[:cap]
            colors = colors[:cap]

        n, out = self._project(quads.reshape(-1, 3),
                               colors.reshape(-1, 4),
                               viewport, width, height)
        base = (np.arange(len(quads), dtype=np.uint32) * 4)[:, None]
        idx = base + np.array([[0, 1, 2, 0, 2, 3]], dtype=np.uint32)
        idx = idx.reshape(-1)
        return n, out, len(idx), idx


class MeshGroup:
    """Several :class:`MeshBatch` objects drawn as one indexed mesh.

    Use it when independent parts of the scene each own their geometry: the
    group concatenates them into the frame's single native batch in list
    order, so no part has to append into another part's arrays.  List order is
    also draw order, which is what transparency sorts against; opaque quads
    are resolved per pixel by the depth buffer either way.

    ``win.set_mesh([a, b])`` is shorthand for ``MeshGroup(a, b)``.
    """

    MAX_MESH_VERTS = MAX_MESH_VERTS
    MAX_QUADS = MAX_QUADS_INDEXED
    MAX_QUADS_LEGACY = MAX_QUADS_LEGACY

    def __init__(self, *batches):
        if len(batches) == 1 and isinstance(batches[0], (list, tuple)):
            batches = tuple(batches[0])
        self.batches = list(batches)
        self._capacity_warned = False

    def append(self, batch):
        self.batches.append(batch)
        return self

    def __len__(self):
        return len(self.batches)

    def __iter__(self):
        return iter(self.batches)

    def __repr__(self):
        return "MeshGroup(%d batches)" % len(self.batches)

    def _gather(self, cap):
        """Concatenate quads/colours up to ``cap`` quads.

        Returns ``(quads, colors, dropped)``.  Slicing whole quads keeps the
        index/vertex prefixes consistent, so neither builder can send a
        partial quad to native.
        """
        parts = [b for b in self.batches if b is not None and len(b.quads)]
        total = sum(len(b.quads) for b in parts)
        quads, colors, used = [], [], 0
        for batch in parts:
            take = min(len(batch.quads), cap - used)
            if take <= 0:
                break
            quads.append(np.asarray(batch.quads[:take], dtype=np.float64))
            colors.append(np.asarray(batch.colors[:take], dtype=np.float32))
            used += take
            if used >= cap:
                break
        if not quads:
            return None
        return (np.concatenate(quads, axis=0),
                np.concatenate(colors, axis=0),
                total - used)

    def _warn_capacity(self, total, cap, where):
        if not self._capacity_warned:
            warnings.warn(
                "MeshGroup has %d quads over %s=%d; dropping the last %d "
                "quads so the native mesh stays whole."
                % (total, where, cap, total - cap),
                RuntimeWarning, stacklevel=3)
            self._capacity_warned = True

    def build_vertices(self, viewport, width, height):
        """Legacy non-indexed path: six vertices per quad."""
        cap = self.MAX_QUADS_LEGACY
        gathered = self._gather(cap)
        if gathered is None:
            return None
        quads, colors, dropped = gathered
        if dropped:
            self._warn_capacity(len(quads) + dropped, cap, "MAX_QUADS_LEGACY")
        tri = np.concatenate(
            [quads[:, [0, 1, 2], :], quads[:, [0, 2, 3], :]], axis=0)
        cols = np.concatenate(
            [colors[:, [0, 1, 2], :], colors[:, [0, 2, 3], :]], axis=0)
        n, out = MeshBatch._project(tri.reshape(-1, 3), cols.reshape(-1, 4),
                                    viewport, width, height)
        return n, out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

    def build_indexed_vertices(self, viewport, width, height):
        """Indexed path: four vertices per quad + six uint32 indices."""
        cap = self.MAX_QUADS
        gathered = self._gather(cap)
        if gathered is None:
            return None
        quads, colors, dropped = gathered
        if dropped:
            self._warn_capacity(len(quads) + dropped, cap,
                                "MAX_QUADS_INDEXED")
        n, out = MeshBatch._project(quads.reshape(-1, 3),
                                    colors.reshape(-1, 4),
                                    viewport, width, height)
        base = (np.arange(len(quads), dtype=np.uint32) * 4)[:, None]
        idx = (base + np.array([[0, 1, 2, 0, 2, 3]], dtype=np.uint32))
        idx = idx.reshape(-1)
        return n, out, len(idx), idx
