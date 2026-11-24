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

import warnings

import numpy as np

from manim.mobject.mobject import Mobject

from real_time_manim.camera_state import get_viewport
from real_time_manim.mesh import MeshBatch, _batch_unit_normal, bake_surface


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

    def __init__(self, vertices, quads, colors=None, *, shade_data=None,
                 **kwargs):
        super().__init__(**kwargs)
        batch = MeshBatch().append_indexed(vertices, quads, colors)
        self.points = np.array(batch._vertices, dtype=np.float64, copy=True)
        self._indices = np.array(batch._indices, dtype=np.int64, copy=True)
        self._colors = np.array(batch._index_colors, dtype=np.float32,
                                copy=True)
        self._batch = None
        self._points_sig = None
        self._shade_data = shade_data
        self._shaded_light = None

    @classmethod
    def from_surface(cls, surface, *, ignore_strokes=False, shade=False,
                     **kwargs):
        """Bake a ``Surface``; ``shade=True`` bakes its 3D face lighting too.

        Without ``shade`` the Surface must be flat (``set_shade_in_3d(False)``,
        ``set_stroke(width=0)``), exactly like :meth:`MeshBatch.from_surface`.
        With ``shade=True`` a shaded Surface is accepted: manim's two-stop
        per-face lighting is baked from the world light on the first frame that
        has a 3D camera, and the four mesh corners interpolate between those
        stops.  The lighting is then frozen with the geometry, like every other
        baked colour.
        """
        if not shade:
            batch = MeshBatch.from_surface(surface,
                                           ignore_strokes=ignore_strokes)
            return cls(batch._vertices, batch._indices, batch._index_colors,
                       **kwargs)
        corners, colors, shade_data, dropped = bake_surface(
            surface, ignore_strokes=ignore_strokes, allow_shaded=True,
            shading=True)
        if dropped:
            warnings.warn(
                "MeshMobject.from_surface: visible Surface strokes were "
                "ignored; the depth mesh draws fills only.", RuntimeWarning,
                stacklevel=2)
        vertices, inverse = np.unique(corners.reshape(-1, 3), axis=0,
                                      return_inverse=True)
        return cls(vertices, inverse.reshape(-1, 4), colors,
                   shade_data=shade_data, **kwargs)

    @property
    def quad_count(self):
        """Number of quads (``Mobject.__len__`` is the submobject count)."""
        return len(self._indices)

    def _apply_baked_shading(self, light_source):
        """Compute the lit colours for ``shade=True`` surfaces."""
        data = self.__dict__["_shade_data"]
        light = np.asarray(light_source, dtype=np.float64)
        corners = self.points[self._indices]              # (F, 4, 3)
        # Recover the affine map from the baked corners to the current ones,
        # so rotate/scale/shear move the shading tangents with the mesh.
        source = data["bake_corners"].reshape(-1, 3)
        target = corners.reshape(-1, 3)
        design = np.column_stack([source, np.ones(len(source))])
        try:
            affine, *_ = np.linalg.lstsq(design, target, rcond=None)
            vec = data["rel"] @ affine[:3]                # (F, 5, 3)
        except np.linalg.LinAlgError:                     # pragma: no cover
            vec = data["rel"]
        normals = np.stack([
            _batch_unit_normal(vec[:, 0], vec[:, 1]),
            _batch_unit_normal(vec[:, 2], vec[:, 3]),
        ], axis=1)
        points = np.stack([corners[:, 0], corners[:, 0] + vec[:, 4]], axis=1)
        axis = points[:, 1] - points[:, 0]
        den = (axis * axis).sum(axis=1)
        offsets = corners - corners[:, None, 0]
        t = np.where(den[:, None] > 1e-18,
                     np.clip((offsets * axis[:, None, :]).sum(axis=2)
                             / np.where(den > 1e-18, den, 1.0)[:, None],
                             0.0, 1.0),
                     0.5)
        self._shade_t = t
        to_light = light[None, None, :] - points
        norm = np.linalg.norm(to_light, axis=2)
        good = norm > 1e-12
        unit = np.zeros_like(to_light)
        unit[good] = to_light[good] / norm[good, None]
        dot = (normals * unit).sum(axis=2)
        term = 0.5 * dot ** 3
        term = np.where(term < 0.0, term * 0.5, term)
        lit = np.clip(data["base"][..., :3] + term[..., None], 0.0, 1.0)
        t = self._shade_t[..., None]
        cols = lit[:, 0][:, None, :] * (1.0 - t) + lit[:, 1][:, None, :] * t
        alpha = np.repeat(data["base"][:, 0, 3][:, None], 4, axis=1)
        colors = np.concatenate([cols, alpha[..., None]], axis=2)
        mask = data["mask"]
        self._colors[mask] = colors[mask].astype(np.float32)
        self.__dict__["_batch"] = None

    def _shade_once(self):
        """Apply the baked lighting on the first frame that has a 3D light.

        The light source is published with the frame's viewport, so a
        ``from_surface(shade=True)`` called in ``construct()`` cannot see it
        yet.  Once applied the result stays frozen: it belongs to the baked
        geometry, and later camera moves (which do not change the shading) must
        not redo it.
        """
        if self.__dict__.get("_shade_data") is None:
            return
        if self.__dict__.get("_shaded_light") is not None:
            return
        try:
            viewport = get_viewport()
        except Exception:
            return
        if viewport is None or getattr(viewport, "rotation", None) is None:
            return
        light = getattr(viewport, "light_source", None)
        if light is None:
            return
        self._apply_baked_shading(light)
        self._shaded_light = np.asarray(light, dtype=np.float64).tobytes()

    def to_mesh_batch(self):
        """This frame's :class:`MeshBatch`, refreshed after a transform.

        Transforms either mutate ``points`` in place (``shift``) or rebind it
        (``scale`` / ``rotate``), so the batch is pointed at the current array
        and its projection invalidated whenever the vertex bytes changed.
        """
        self._shade_once()
        points = self.points
        sig = points.tobytes()
        batch = self.__dict__.get('_batch')
        if batch is None:
            batch = MeshBatch()
            batch.append_indexed(points, self._indices, self._colors)
            self._batch = batch
        elif sig != self._points_sig:
            batch._vertices = points
            batch.mark_geometry_dirty()
        self._points_sig = sig
        return batch

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
        # projected buffers would only be copied to be thrown away.  The baked
        # shading inputs are read-only, so the copy shares them.
        batch = self.__dict__.pop('_batch', None)
        shade = self.__dict__.get('_shade_data')
        try:
            clone = super().__deepcopy__(memo)
        finally:
            if batch is not None:
                self.__dict__['_batch'] = batch
        clone.__dict__['_batch'] = None
        clone.__dict__['_points_sig'] = None
        clone.__dict__['_shade_data'] = shade
        return clone
