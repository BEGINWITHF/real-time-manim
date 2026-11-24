"""Depth-tested triangle meshes for the native renderer.

The legacy RTM/manim path paints 2D primitives in document/depth order.  That
cannot give per-pixel occlusion for a mesh (intersecting quads, a rim crossing a
surface, coplanar cells).  ``MeshBatch`` bypasses the painter for geometry:
``MLWindow.sync`` hands its projected vertices to the native depth-tested mesh
pipeline, and the ordinary 2D sender path still paints afterwards.

Coordinates are world (manim) coordinates.  Two storage forms are supported:

* ``append(quads, colors)`` -- the original explicit-quad form;
* ``append_indexed(vertices, quads, colors)`` -- unique vertices plus a
  ``(Q, 4)`` index per face.  ``build_vertices`` projects each unique vertex
  once and gathers the triangles, so a 9,800-face shell does not project the
  same shared corner six times.  The gathered triangle buffer and (for indexed
  batches) the projected coordinates are reused across frames; call
  ``mark_geometry_dirty()`` after editing ``vertices`` in place.
"""
from __future__ import annotations

import ctypes
import warnings

import numpy as np

from real_time_manim.camera_state import screen_scale

#: Native depth-tested mesh capacity (``native/shared_types.h``).  Each quad
#: becomes two triangles, i.e. six vertices, so the last usable quad index is
#: ``MAX_QUADS - 1``.  Kept as a module constant as well as class attributes so
#: callers can size a batch without importing the native limit.
MAX_MESH_VERTS = 262_144
MAX_QUADS = MAX_MESH_VERTS // 6          # 43,690 quads = 262,140 vertices


class MeshBatch:
    """A batch of coloured quads rendered with a GPU depth buffer.

    ``quads``/``colors`` are the explicit form (``(Q, 4, 3)`` and
    ``(Q, 4, 4)``); ``append_indexed`` stores unique ``vertices`` plus
    ``(Q, 4)`` indices and per-corner colours instead.  The two forms cannot be
    mixed in one batch.

    The native mesh pipeline holds :data:`MAX_MESH_VERTS` triangulated
    vertices (:attr:`MAX_QUADS` quads).  ``append``/``append_indexed`` raise
    before a batch can cross that limit; ``build_vertices`` additionally
    truncates to whole quads (one warning) if the public arrays were grown
    directly, so a partial triangle/quad can never reach native.
    """

    MAX_MESH_VERTS = MAX_MESH_VERTS
    MAX_QUADS = MAX_QUADS

    def __init__(self):
        self.quads = np.empty((0, 4, 3), dtype=np.float64)
        self.colors = np.empty((0, 4, 4), dtype=np.float32)
        self._capacity_warned = False
        # Indexed form.  Mutually exclusive with ``quads``.
        self._vertices = np.empty((0, 3), dtype=np.float64)
        self._indices = np.empty((0, 4), dtype=np.int64)
        self._index_colors = np.empty((0, 4, 4), dtype=np.float32)
        self._indexed = False
        # Output/projection reuse.  ``_built_key`` covers the whole static
        # indexed batch; append-mode batches are rebuilt every call because
        # their public ``quads`` array may be edited in place.
        self._out = None
        self._built_key = None
        self._built_n = 0
        self._geometry_rev = 0
        self._project_key = None
        self._projected = None

    @property
    def quad_count(self):
        return len(self._indices) if self._indexed else len(self.quads)

    def __len__(self):
        return self.quad_count

    def append(self, quads, colors):
        quads = np.asarray(quads, dtype=np.float64)
        colors = np.asarray(colors, dtype=np.float32)
        if self._indexed:
            raise ValueError(
                "MeshBatch cannot mix append() with append_indexed(); "
                "use one representation per batch."
            )
        if quads.ndim != 3 or quads.shape[1:] != (4, 3):
            raise ValueError("quads must have shape (Q, 4, 3)")
        if colors.shape != (quads.shape[0], 4, 4):
            raise ValueError("colors must have shape (Q, 4, 4)")
        total = len(self.quads) + len(quads)
        if total > self.MAX_QUADS:
            raise ValueError(
                "MeshBatch capacity exceeded: %d + %d = %d quads "
                "(%d vertices), but MAX_QUADS is %d (%d vertices). "
                "Reduce the quad count, or drop whole quads before appending."
                % (len(self.quads), len(quads), total, total * 6,
                   self.MAX_QUADS, self.MAX_QUADS * 6)
            )
        self.quads = np.concatenate([self.quads, quads], axis=0)
        self.colors = np.concatenate([self.colors, colors], axis=0)
        self._geometry_rev += 1
        self._built_key = None
        return self

    def append_indexed(self, vertices, quads, colors=None):
        """Append unique ``vertices`` plus ``(Q, 4)`` index quads.

        ``vertices`` is ``(N, 3)``; ``quads`` indexes it, one quad per row.
        ``colors`` is ``(Q, 4, 4)`` per-corner RGBA (white when omitted).  The
        same vertex may be referenced by many quads, so projection happens
        once per unique vertex instead of once per triangle corner.
        """
        vertices = np.asarray(vertices, dtype=np.float64)
        quads = np.asarray(quads)
        if vertices.ndim != 2 or vertices.shape[1] != 3 or len(vertices) == 0:
            raise ValueError("vertices must have shape (N, 3) with N > 0")
        if quads.ndim != 2 or quads.shape[1] != 4:
            raise ValueError("quads must have shape (Q, 4) with Q > 0")
        if len(quads) == 0:
            return self
        if not np.issubdtype(quads.dtype, np.integer):
            rounded = np.rint(quads)
            if not np.allclose(quads, rounded):
                raise ValueError("quads must contain integer vertex indices")
            quads = rounded.astype(np.int64)
        else:
            quads = quads.astype(np.int64, copy=False)
        if int(quads.min()) < 0 or int(quads.max()) >= len(vertices):
            raise ValueError("quads index outside vertices")
        if colors is None:
            colors = np.ones((len(quads), 4, 4), dtype=np.float32)
        else:
            colors = np.asarray(colors, dtype=np.float32)
            if colors.shape != (len(quads), 4, 4):
                raise ValueError("colors must have shape (Q, 4, 4)")
        if len(self.quads):
            raise ValueError(
                "MeshBatch cannot mix append_indexed() with append(); "
                "use one representation per batch."
            )
        total = len(self._indices) + len(quads)
        if total > self.MAX_QUADS:
            raise ValueError(
                "MeshBatch capacity exceeded: %d + %d = %d quads "
                "(%d vertices), but MAX_QUADS is %d (%d vertices). "
                "Reduce the quad count, or drop whole quads before appending."
                % (len(self._indices), len(quads), total, total * 6,
                   self.MAX_QUADS, self.MAX_QUADS * 6)
            )
        offset = len(self._vertices)
        if self._indexed:
            self._vertices = np.concatenate([self._vertices, vertices], axis=0)
            self._indices = np.concatenate([self._indices, quads + offset],
                                           axis=0)
            self._index_colors = np.concatenate(
                [self._index_colors, colors], axis=0)
        else:
            self._vertices = vertices
            self._indices = quads
            self._index_colors = colors
            self._indexed = True
        self._geometry_rev += 1
        self._built_key = None
        return self

    def mark_geometry_dirty(self):
        """Invalidate the indexed projection/output cache after an edit.

        ``build_vertices`` caches the gathered triangles for an indexed batch
        when the geometry revision and view are unchanged.  Editing
        ``vertices`` (or other private arrays) in place must call this; calls
        to ``append``/``append_indexed`` do it automatically.
        """
        self._geometry_rev += 1
        self._built_key = None
        return self

    def _ensure_out(self, n):
        if self._out is None or self._out.shape[0] < n:
            self._out = np.empty((n, 7), dtype=np.float32)
        return self._out[:n]

    @staticmethod
    def _project(pts, viewport, width, height):
        """Project world points to pixel ``x, y`` and native ``depth``."""
        if viewport is None:
            s = screen_scale(width, height)
            x = width * 0.5 + pts[:, 0] * s
            y = height * 0.5 - pts[:, 1] * s
            depth = np.full(len(pts), 0.5, dtype=np.float32)
            return x, y, depth

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
                factor = np.where(np.abs(denom) > 1e-6, focal / denom, 1.0)
                q[:, 0] *= factor
                q[:, 1] *= factor
            p = q
        x = width * 0.5 + p[:, 0] * s
        y = height * 0.5 - p[:, 1] * s

        if rot is not None:
            rz = p[:, 2]
            focal = viewport.focal_distance
            scale = (abs(focal) if focal and abs(focal) > 1e-6
                     else max(viewport.height, 1.0))
            # Smaller depth is nearer.  Linear camera-space depth is enough
            # for the small cells here and matches the painter's depth key.
            depth = np.clip(0.5 - 0.5 * rz / scale, 0.0, 1.0)
        else:
            depth = np.full(len(pts), 0.5, dtype=np.float32)
        return x, y, depth

    @staticmethod
    def _view_key(viewport, width, height):
        if viewport is None:
            return (width, height, None)
        rot = viewport.rotation
        light = viewport.light_source
        return (
            width, height, viewport.center, viewport.height,
            viewport.unit_height,
            None if rot is None else np.asarray(rot, dtype=float).tobytes(),
            viewport.frame_center, viewport.focal_distance,
            viewport.exponential,
            None if light is None else np.asarray(light, dtype=float).tobytes(),
        )

    def _build_indexed(self, viewport, width, height):
        q = len(self._indices)
        if q == 0:
            return None
        indices = self._indices
        index_colors = self._index_colors
        if q > self.MAX_QUADS:
            if not self._capacity_warned:
                warnings.warn(
                    "MeshBatch has %d quads (%d vertices), over MAX_QUADS=%d "
                    "(%d vertices); dropping the last %d quads so the native "
                    "mesh stays whole."
                    % (q, q * 6, self.MAX_QUADS, self.MAX_QUADS * 6,
                       q - self.MAX_QUADS),
                    RuntimeWarning, stacklevel=2)
                self._capacity_warned = True
            q = self.MAX_QUADS
            indices = indices[:q]
            index_colors = index_colors[:q]
        view = self._view_key(viewport, width, height)
        key = (self._geometry_rev, view, q)
        if self._built_key == key:
            return self._built_n, self._out.ctypes.data_as(
                ctypes.POINTER(ctypes.c_float))

        # Two triangles per quad, gathering the shared unique vertices.
        tri_idx = np.concatenate(
            [indices[:, [0, 1, 2]], indices[:, [0, 2, 3]]],
            axis=0,
        ).reshape(-1)
        cols = np.concatenate(
            [index_colors[:, [0, 1, 2]], index_colors[:, [0, 2, 3]]],
            axis=0,
        ).reshape(-1, 4)
        n = len(tri_idx)
        if self._project_key != (self._geometry_rev, view):
            x, y, depth = self._project(self._vertices, viewport, width, height)
            self._projected = (
                (x / width) * 2.0 - 1.0,
                (y / height) * 2.0 - 1.0,
                depth,
            )
            self._project_key = (self._geometry_rev, view)
        ndc_x, ndc_y, depth = self._projected
        out = self._ensure_out(n)
        out[:, 0] = ndc_x[tri_idx]
        out[:, 1] = ndc_y[tri_idx]
        out[:, 2] = depth[tri_idx]
        out[:, 3:7] = cols
        self._built_key = key
        self._built_n = n
        return n, out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

    def build_vertices(self, viewport, width, height):
        """Project to native ``(x_ndc, y_ndc, depth, rgba)`` triangle vertices."""
        if self._indexed:
            return self._build_indexed(viewport, width, height)
        if len(self.quads) == 0:
            return None

        quads = self.quads
        colors = self.colors
        if len(quads) > self.MAX_QUADS:
            if not self._capacity_warned:
                warnings.warn(
                    "MeshBatch has %d quads (%d vertices), over MAX_QUADS=%d "
                    "(%d vertices); dropping the last %d quads so the native "
                    "mesh stays whole."
                    % (len(quads), len(quads) * 6, self.MAX_QUADS,
                       self.MAX_QUADS * 6, len(quads) - self.MAX_QUADS),
                    RuntimeWarning, stacklevel=2)
                self._capacity_warned = True
            quads = quads[:self.MAX_QUADS]
            colors = colors[:self.MAX_QUADS]

        # Two triangles per quad, preserving the quad's vertex colours.
        tri = np.concatenate(
            [quads[:, [0, 1, 2], :], quads[:, [0, 2, 3], :]], axis=0)
        cols = np.concatenate(
            [colors[:, [0, 1, 2], :], colors[:, [0, 2, 3], :]], axis=0)
        pts = tri.reshape(-1, 3)
        x, y, depth = self._project(pts, viewport, width, height)

        n = len(pts)
        out = self._ensure_out(n)
        out[:, 0] = (x / width) * 2.0 - 1.0
        out[:, 1] = (y / height) * 2.0 - 1.0
        out[:, 2] = depth
        out[:, 3:7] = cols.reshape(-1, 4)
        return n, out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
