"""A scene mobject drawn through the native depth-tested mesh.

``MeshBatch`` is frame geometry handed to ``win.set_mesh``: it is not part of
the scene, so a ``shift`` / ``rotate`` / ``.animate`` on the original
``Surface`` never reaches it.  ``MeshMobject`` is the scene-side wrapper: its
``points`` ARE the unique mesh vertices, so every ordinary manim transform
edits the mesh, and ``MLWindow.sync`` submits it automatically.

Build one from a flat ``Surface``::

    surf = Surface(...)
    surf.set_shade_in_3d(False)
    surf.set_stroke(width=0)
    mesh = MeshMobject.from_surface(surf)
    self.add(mesh)
    mesh.animate.shift(RIGHT)

or from explicit geometry::

    MeshMobject(vertices, quads, colors=None)

Only one native mesh is drawn per frame, so every ``MeshMobject`` in the scene
(and an explicit ``win.set_mesh`` batch) is merged into that frame's batch;
quads keep their per-corner colours and the depth buffer resolves them.
"""
from __future__ import annotations

import numpy as np

from manim.mobject.mobject import Mobject

from real_time_manim.mesh import MeshBatch


class MeshMobject(Mobject):
    """Mesh vertices as a mobject, so manim transforms move the mesh.

    ``points`` holds the unique ``(N, 3)`` world vertices; ``_indices`` /
    ``_colors`` hold the ``(Q, 4)`` quads and their per-corner RGBA.  Opaque
    quads are resolved per pixel by the native depth buffer, so a ``Surface``
    that crosses itself no longer depends on painter order.

    The mobject paints nothing itself (``window/paint.py`` skips it); its
    geometry goes through the mesh before the painter, which means 2D overlays
    still paint on top.  Merging several ``MeshMobject`` objects is automatic;
    the one-batch capacity (``MeshBatch.MAX_QUADS``) applies to the merged
    total.
    """

    #: Recognised by ``window/paint.py::_send_impl`` -- never painted as a path.
    _rtm_mesh_skip = True

    def __init__(self, vertices, quads, colors=None, normals=None, shade=False,
                 **kwargs):
        super().__init__(**kwargs)
        batch = MeshBatch(shade=shade).append_indexed(
            vertices, quads, colors, normals=normals)
        self.points = np.array(batch._vertices, dtype=np.float64, copy=True)
        self._indices = np.array(batch._indices, dtype=np.int64, copy=True)
        self._colors = np.array(batch._index_colors, dtype=np.float32,
                                copy=True)
        self._shade = bool(batch.shade)
        self._normals = (np.array(batch._index_normals, dtype=np.float64,
                                  copy=True) if self._shade else None)
        self._batch = None
        self._points_sig = None

    @classmethod
    def from_surface(cls, surface, *, ignore_strokes=False, shade=False,
                     **kwargs):
        """Bake a ``Surface``; ``shade=True`` carries face normals."""
        batch = MeshBatch.from_surface(surface, ignore_strokes=ignore_strokes,
                                       shade=shade)
        return cls(batch._vertices, batch._indices, batch._index_colors,
                   normals=batch._index_normals if shade else None,
                   shade=shade, **kwargs)

    @property
    def quad_count(self):
        """Number of quads (``Mobject.__len__`` is the submobject count)."""
        return len(self._indices)

    def to_mesh_batch(self):
        """This frame's :class:`MeshBatch`, refreshed after a transform.

        Transforms either mutate ``points`` in place (``shift``) or rebind it
        (``scale`` / ``rotate``), so the batch is pointed at the current array
        and its projection invalidated whenever the vertex bytes changed.
        """
        points = self.points
        sig = points.tobytes()
        batch = self.__dict__.get('_batch')
        if batch is None:
            batch = MeshBatch(shade=self._shade)
            batch.append_indexed(points, self._indices, self._colors)
            self._batch = batch
        elif sig != self._points_sig:
            batch._vertices = points
            if self._shade:
                from real_time_manim.mesh import _face_normals
                batch._index_normals = np.repeat(
                    _face_normals(points[self._indices])[:, None, :], 4,
                    axis=1)
            batch.mark_geometry_dirty()
        self._points_sig = sig
        return batch

    def build_indexed_lit_vertices(self, viewport, width, height):
        """Lit submission path; ``None`` for an unshaded mesh."""
        if not self._shade:
            return None
        return self.to_mesh_batch().build_indexed_lit_vertices(
            viewport, width, height)

    def build_indexed_vertices(self, viewport, width, height):
        """Let ``win.set_mesh(mesh_mobject)`` submit it like a batch."""
        return self.to_mesh_batch().build_indexed_vertices(
            viewport, width, height)

    def interpolate_color(self, mobject1, mobject2, alpha):
        """Interpolate the per-quad corner colours during a ``Transform``.

        ``Mobject.interpolate`` calls this for every animation; the base class
        raises ``NotImplementedError``, which made ``mesh.animate.shift(...)``
        fail before the mesh moved at all.  A geometry-only transform has equal
        colours before and after, so this is a no-op and the projection cache
        stays warm.
        """
        c1 = getattr(mobject1, '_colors', None)
        c2 = getattr(mobject2, '_colors', None)
        if c1 is None or c2 is None or c1.shape != c2.shape:
            return
        if np.array_equal(c1, c2):
            return
        if alpha <= 0.0:
            colors = c1
        elif alpha >= 1.0:
            colors = c2
        else:
            colors = (1.0 - alpha) * c1 + alpha * c2
        self._colors = np.asarray(colors, dtype=np.float32)
        self.__dict__['_batch'] = None       # rebuilt with the new colours

    def __deepcopy__(self, memo):
        # A Transform copies its target; the batch is a per-frame cache and its
        # projected buffers would only be copied to be thrown away.
        batch = self.__dict__.pop('_batch', None)
        try:
            clone = super().__deepcopy__(memo)
        finally:
            if batch is not None:
                self.__dict__['_batch'] = batch
        clone.__dict__['_batch'] = None
        clone.__dict__['_points_sig'] = None
        return clone
