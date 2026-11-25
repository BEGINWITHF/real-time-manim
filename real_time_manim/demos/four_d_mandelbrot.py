#!/usr/bin/env python3
"""Mandelbrot in four dimensions — the RTM reference short.

A finished 38.8 s film, kept in the package as the executable quality bar:
every rule in ``RTM-Wiki/agent/filmcraft.md`` is applied here, and the whole
timeline is a single pure function of absolute time so ``jobs=N`` and frame
seeking agree.

What it shows
-------------
1. The usual Mandelbrot set in the complex plane, rendered as an escape-time
   image.
2. c is lifted into the quaternions ℍ.  Because quaternion squaring commutes
   with every rotation of (i, j, k), the 4D Mandelbrot set is exactly the
   complex one spun around the real axis.  The animation lathes the 2D outline
   into that solid of revolution, with a gold meridian riding the sweep.
3. A hyperplane w = const cuts the 4D solid; its 3D slice is the same vase
   with every radius r replaced by sqrt(r^2 - w^2), so the thin filaments
   disappear first.
4. Outro card with the definition in ℍ.

Usage
-----
    python -m real_time_manim.demos.four_d_mandelbrot                 # -> out/four_d_mandelbrot.mp4
    python -m real_time_manim.demos.four_d_mandelbrot --jobs 4
    python -m real_time_manim.demos.four_d_mandelbrot --still 2,12,26 # PNG stills instead
    python -m real_time_manim.demos.four_d_mandelbrot --preview        # scrub GUI + progress bar
    python -m real_time_manim.demos.four_d_mandelbrot --preview slider # slider instead of text box

Measured on a 16-core / Intel iGPU laptop: 2,328 frames at 1920x1080@60 in
~118 s with ``--jobs 4``; the 38,024-quad surface costs ~10.5 ms perframe to
rebuild and shade in pure numpy.
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import time

import numpy as np
from PIL import Image, ImageFilter

import real_time_manim  # noqa: F401  (must come before any `manim` import)
from real_time_manim import (
    DEGREES,
    DOWN,
    LEFT,
    ORIGIN,
    UP,
    Animation,
    ImageMobject,
    ManimColor,
    MathTex,
    Rectangle,
    RoundedRectangle,
    Text,
    ThreeDScene,
    VMobject,
    linear,
)
from real_time_manim.mesh import MeshBatch
from real_time_manim.record import fast_record_scene
from real_time_manim.vulkan_bind import MLWindow

# --------------------------------------------------------------------------
# look
# --------------------------------------------------------------------------
BG = "#070b14"
BG_RGB = np.array([0.0275, 0.0431, 0.0784])
INK = "#efe9dc"
DIM = "#7b93a6"
FAINT = "#3d5468"
GOLD = "#f2c66d"
CYAN = "#6fd6cd"
WHITE = "#fff6e8"

# --------------------------------------------------------------------------
# maths / geometry
# --------------------------------------------------------------------------
CX, CY = -0.765, 0.0           # complex window centre
SPAN_X = 1.295                # half width of the window  -> re in [-2.06, 0.53]
IM_HALF = 1.18                # imaginary half height
IMG_PX_W = 1000
IMG_PX_H = int(round(IMG_PX_W * 2.0 * IM_HALF / (2.0 * SPAN_X)))
MAXIT = 300

IMG_WORLD_W = 8.00
S = IMG_WORLD_W / (2.0 * SPAN_X)                # world units per complex unit
A_MID = -0.765                                  # real axis is centred in the frame

N_PROFILE = 680
N_AZ = 56

# palette for the surface / image (low -> high escape time)
PALETTE = np.array(
    [
        [0.030, 0.070, 0.140],
        [0.055, 0.220, 0.360],
        [0.100, 0.550, 0.600],
        [0.450, 0.880, 0.720],
        [0.980, 0.800, 0.420],
        [1.000, 0.970, 0.900],
    ]
)

SURFACE_PALETTE = np.array(
    [
        [0.020, 0.055, 0.115],
        [0.040, 0.180, 0.280],
        [0.050, 0.420, 0.520],
        [0.220, 0.720, 0.720],
        [0.950, 0.760, 0.380],
        [1.000, 0.940, 0.820],
    ]
)

# light in world space, well off the view axis so the lathe reads as a solid
LIGHT = np.array([-0.72, -0.28, 0.63])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def smoothstep(a):
    a = np.clip(a, 0.0, 1.0)
    return a * a * (3.0 - 2.0 * a)


def ramp(t, t0, t1):
    return float(smoothstep((t - t0) / max(t1 - t0, 1e-9)))


def palette(t, stops=PALETTE):
    t = np.clip(np.asarray(t, dtype=np.float64), 0.0, 1.0) * (len(stops) - 1)
    i = np.clip(t.astype(int), 0, len(stops) - 2)
    f = (t - i)[..., None]
    return stops[i] * (1.0 - f) + stops[i + 1] * f


# --------------------------------------------------------------------------
# escape-time field
# --------------------------------------------------------------------------
def mandel_field(re0, re1, im0, im1, nw, nh, maxit=MAXIT):
    xs = np.linspace(re0, re1, nw)
    ys = np.linspace(im0, im1, nh)
    re, im = np.meshgrid(xs, ys)
    zr = np.zeros_like(re)
    zi = np.zeros_like(im)
    esc = np.full(re.shape, float(maxit))
    alive = np.ones(re.shape, dtype=bool)
    with np.errstate(over="ignore", invalid="ignore"):
        for n in range(1, maxit + 1):
            zr, zi = zr * zr - zi * zi + re, 2.0 * zr * zi + im
            m2 = zr * zr + zi * zi
            newly = alive & (m2 > 256.0)
            if newly.any():
                esc[newly] = n + 1.0 - np.log2(np.log2(m2[newly]) * 0.5)
                alive &= ~newly
            if not alive.any():
                break
    return xs, ys, esc


def hero_image(esc, maxit=MAXIT):
    """Escape-time colours, dark set, soft rim bloom.  RGBA uint8, row 0 = top."""
    inside = esc >= maxit
    t = (esc / (esc + 6.5)) ** 2.1
    rgb = palette(t)
    halo = np.exp(-np.clip(maxit - esc, 0.0, None) / 16.0) * (~inside)
    halo_img = Image.fromarray((np.clip(halo, 0.0, 1.0) * 255).astype(np.uint8))
    bloom = np.asarray(
        halo_img.filter(ImageFilter.GaussianBlur(9)), dtype=np.float32
    ) / 255.0
    warm = np.array([0.95, 0.72, 0.30])
    cool = np.array([0.30, 0.85, 0.82])
    rgb = np.clip(
        rgb + bloom[..., None] * (0.55 * warm) + (bloom**2)[..., None] * (0.30 * cool),
        0.0,
        1.0,
    )
    rgb[inside] = np.array([0.012, 0.017, 0.034])
    # let the far exterior fall away into the scene background
    far = smoothstep((esc - 2.0) / 12.0)
    rgb = BG_RGB + (rgb - BG_RGB) * far[..., None]
    # fade the texture's edges into the scene background: no visible rectangle
    h, w = esc.shape
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)).astype(np.float64)
    edge = smoothstep(d / 46.0)
    rgb = BG_RGB + (rgb - BG_RGB) * edge[..., None]
    out = np.empty(esc.shape + (4,), dtype=np.uint8)
    out[..., :3] = (rgb * 255.0 + 0.5).astype(np.uint8)
    out[..., 3] = 255
    return np.ascontiguousarray(out)


# --------------------------------------------------------------------------
# marching squares -> boundary loops of the filled set
# --------------------------------------------------------------------------
def _segments(mask):
    """Boundary segments of a boolean mask, in grid index space (x=i, y=j)."""
    m = mask
    ny, nx = m.shape
    a = m[:-1, :-1]
    b = m[:-1, 1:]
    c = m[1:, 1:]
    d = m[1:, :-1]
    case = (
        a.astype(np.uint8)
        + (b.astype(np.uint8) << 1)
        + (c.astype(np.uint8) << 2)
        + (d.astype(np.uint8) << 3)
    )
    js, ix = np.nonzero((case != 0) & (case != 15))
    table = {
        1: [(3, 0)],
        2: [(0, 1)],
        3: [(3, 1)],
        4: [(1, 2)],
        5: [(3, 0), (1, 2)],
        6: [(0, 2)],
        7: [(3, 2)],
        8: [(2, 3)],
        9: [(2, 0)],
        10: [(0, 1), (2, 3)],
        11: [(1, 2)],
        12: [(3, 1)],
        13: [(0, 1)],
        14: [(3, 0)],
    }
    segs = []
    for j, i in zip(js.tolist(), ix.tolist()):
        vals = (int(m[j, i]), int(m[j, i + 1]), int(m[j + 1, i + 1]), int(m[j + 1, i]))
        cbits = sum(v << k for k, v in enumerate(vals))
        for e0, e1 in table.get(cbits, ()):
            p0 = _edge_point(e0, i, j)
            p1 = _edge_point(e1, i, j)
            segs.append((p0, p1))
    return segs


def _edge_point(edge, i, j):
    if edge == 0:
        return (i + 0.5, j)
    if edge == 1:
        return (i + 1.0, j + 0.5)
    if edge == 2:
        return (i + 0.5, j + 1.0)
    return (i, j + 0.5)


def boundary_loops(mask, xs, ys):
    from collections import defaultdict

    segs = _segments(mask)
    key = lambda p: (round(p[0] * 8.0), round(p[1] * 8.0))
    adj = defaultdict(list)
    for p0, p1 in segs:
        adj[key(p0)].append((p0, p1))
        adj[key(p1)].append((p1, p0))
    used = set()
    loops = []
    for s0, e0 in segs:
        if (key(s0), key(e0)) in used:
            continue
        pts = [s0]
        prev, cur = s0, e0
        used.add((key(s0), key(e0)))
        for _ in range(400000):
            pts.append(cur)
            nxt = None
            for p, q in adj[key(cur)]:
                if (key(p), key(q)) in used or key(q) == key(prev):
                    continue
                nxt = q
                used.add((key(p), key(q)))
                used.add((key(q), key(p)))
                break
            if nxt is None or key(nxt) == key(pts[0]):
                break
            prev, cur = cur, nxt
        if len(pts) > 40:
            loops.append(np.asarray(pts, dtype=np.float64))
    # index space -> complex plane
    out = []
    for loop in loops:
        ix = np.clip(loop[:, 0].astype(int), 0, len(xs) - 2)
        iy = np.clip(loop[:, 1].astype(int), 0, len(ys) - 2)
        fx = loop[:, 0] - ix
        fy = loop[:, 1] - iy
        out.append(
            np.stack(
                [
                    xs[ix] * (1 - fx) + xs[ix + 1] * fx,
                    ys[iy] * (1 - fy) + ys[iy + 1] * fy,
                ],
                axis=1,
            )
        )
    out.sort(key=len, reverse=True)
    return out


def upper_arc(loop, tol=0.0):
    """Upper half (r >= 0) of a closed boundary loop as one polyline.

    The boundary dips onto the real axis at every real-axis bulb, so the upper
    half is a set of arcs; they are joined along the axis (where the lathe
    radius is zero anyway).
    """
    n = len(loop)
    pts = []
    for i in range(n):
        p = loop[i]
        q = loop[(i + 1) % n]
        if p[1] >= tol:
            pts.append(p)
        if (p[1] >= tol) != (q[1] >= tol):
            t = p[1] / (p[1] - q[1]) if abs(p[1] - q[1]) > 1e-12 else 0.0
            pts.append(p + t * (q - p))
    arc = np.asarray(pts, dtype=np.float64)
    # rotate so the path starts at the left-most axis crossing (the antenna tip)
    at_axis = np.abs(arc[:, 1]) < 1e-9
    if at_axis.any():
        idx = np.where(at_axis)[0]
        start = idx[np.argmin(arc[idx, 0])]
        arc = np.vstack([arc[start:], arc[:start]])
    # and, if it still starts on the upper curve, flip to the antenna side
    if arc[0, 0] > arc[-1, 0]:
        arc = arc[::-1]
    return arc


def resample_arc(arc, k):
    d = np.hypot(np.diff(arc[:, 0]), np.diff(arc[:, 1]))
    s = np.concatenate([[0.0], np.cumsum(d)])
    t = np.linspace(0.0, s[-1], k)
    x = np.interp(t, s, arc[:, 0])
    y = np.interp(t, s, arc[:, 1])
    return np.stack([x, y], axis=1)


def smooth_profile(p, passes=3):
    k = np.array([1.0, 4.0, 6.0, 4.0, 1.0])
    k /= k.sum()
    for _ in range(passes):
        q = p.copy()
        for c in range(p.shape[1]):
            col = p[:, c]
            q[2:-2, c] = (
                k[0] * col[:-4] + k[1] * col[1:-3] + k[2] * col[2:-2]
                + k[3] * col[3:-1] + k[4] * col[4:]
            )
        p = q
    return p


# --------------------------------------------------------------------------
# the solid of revolution (one mesh, rebuilt per frame)
# --------------------------------------------------------------------------
class Vase:
    """Quaternion Mandelbrot slice as a lathe mesh.

    ``xs``/``rs`` are profile samples in world units: xs runs along the real
    axis (world x, the revolution axis), rs >= 0 is the imaginary radius.
    """

    def __init__(self, xs, rs, mesh, n_az=N_AZ):
        self.x = np.asarray(xs, dtype=np.float64)
        self.r = np.asarray(rs, dtype=np.float64)
        self.mesh = mesh
        self.n_az = n_az
        self.phi = np.linspace(np.pi, 3.0 * np.pi, n_az + 1)
        self.cos = np.cos(self.phi)
        self.sin = np.sin(self.phi)
        self.dx = np.gradient(self.x)
        self.dr = np.gradient(self.r)
        # colour along the profile: cool at the antenna, warm at the cusp
        frac = np.linspace(0.0, 1.0, len(self.x))
        self.base = palette(0.06 + 0.88 * frac**0.95, SURFACE_PALETTE)

    def geometry(self, w, reveal, cam_dir, dx=0.0):
        """Vertex grid, normals and shaded colours for slice ``w``."""
        rb = self.r
        rs = np.sqrt(np.maximum(rb * rb - w * w, 0.0))
        drs = np.where(rs > 1e-7, rb * self.dr / np.maximum(rs, 1e-9), 0.0)
        drs = np.clip(drs, -40.0, 40.0)

        cos = self.cos[None, :]
        sin = self.sin[None, :]
        px = np.broadcast_to(self.x[:, None] + dx, (len(self.x), self.n_az + 1))
        py = rs[:, None] * cos
        pz = rs[:, None] * sin

        nx = np.broadcast_to(-drs[:, None], px.shape)
        ny = self.dx[:, None] * cos
        nz = self.dx[:, None] * sin
        nlen = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
        nx, ny, nz = nx / nlen, ny / nlen, nz / nlen

        ndl = np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0.0, 1.0)
        ndv = np.clip(nx * cam_dir[0] + ny * cam_dir[1] + nz * cam_dir[2], 0.0, 1.0)
        h = LIGHT + cam_dir
        h = h / (np.linalg.norm(h) + 1e-9)
        ndh = np.clip(nx * h[0] + ny * h[1] + nz * h[2], 0.0, 1.0)

        base = self.base
        col = base[:, None, :] * (0.20 + 0.95 * ndl[..., None] ** 0.85)
        col = col + (ndh**38)[..., None] * np.array([1.0, 0.94, 0.82]) * 0.30
        rim = (1.0 - ndv) ** 4.0
        col = col + rim[..., None] * np.array([0.32, 0.80, 0.78]) * 0.30
        col = np.clip(col, 0.0, 1.0)

        n_vis = int(round(np.clip(reveal, 0.0, 1.0) * self.n_az))
        if n_vis <= 0:
            return None, None
        p = np.stack([px, py, pz], axis=-1)[:, : n_vis + 1]
        c = col[:, : n_vis + 1]
        quads = np.stack(
            [p[:-1, :-1], p[:-1, 1:], p[1:, 1:], p[1:, :-1]],
            axis=2,
        ).reshape(-1, 4, 3)
        cols = np.stack(
            [c[:-1, :-1], c[:-1, 1:], c[1:, 1:], c[1:, :-1]],
            axis=2,
        ).reshape(-1, 4, 3)
        cols = np.concatenate([cols, np.ones((len(cols), 4, 1))], axis=2)
        return quads, cols.astype(np.float32)

    def meridian(self, w, angle, dx=0.0):
        """Profile curve rotated to ``angle``; the gold lathe blade."""
        rs = np.sqrt(np.maximum(self.r * self.r - w * w, 0.0))
        ca, sa = math.cos(angle), math.sin(angle)
        return np.stack([self.x + dx, rs * ca, rs * sa], axis=1)


# --------------------------------------------------------------------------
# animations
# --------------------------------------------------------------------------
class Story(Animation):
    """The whole short: one pure function of absolute time."""

    def __init__(self, scene, vase, image, outline, blade, image_mobj,
                 hud, slice_hud, t0, run_time, total, outline_base):
        super().__init__(VMobject(), run_time=run_time, rate_func=linear)
        self.scene = scene
        self.camera = scene.camera
        self.vase = vase
        self.image = image
        self.outline = outline
        self.blade = blade
        self.image_mobj = image_mobj
        self.hud = hud                # dict of caption mobjects
        self.slice_hud = slice_hud    # (bar, marker, label)
        self.outline_base = outline_base
        self.t0 = float(t0)
        self.total = float(total)

    # -- state at absolute time t -----------------------------------------
    def state(self, t):
        fade = ramp(t, 36.6, 38.2)
        keep = 1.0 - fade

        # act 1: the complex set
        img_op = ramp(t, 1.1, 2.4) * (1.0 - ramp(t, 9.0, 9.9))
        if self.image_mobj is not None:
            self.image_mobj.set_opacity(img_op)

        phi = np.radians(38.0) * smoothstep(ramp(t, 9.4, 12.2))
        zoom = (
            1.0
            + 0.04 * ramp(t, 4.6, 8.8)
            - 0.16 * ramp(t, 9.4, 12.6)
            + 0.04 * ramp(t, 12.6, 20.0)
        )
        self.camera.set_phi(phi)
        self.camera.set_theta(
            np.radians(-90.0 + 16.0 * ramp(t, 9.4, 14.0))
        )
        self.camera.set_zoom(zoom)

        # lathe reveal, then a slow spin of the gold blade
        reveal = ramp(t, 9.7, 14.6)
        spin = 2.0 * np.pi * (0.06 * max(0.0, t - 13.0))
        dx = 1.55 * ramp(t, 31.0, 33.4)

        # 4D slicing
        wmax = float(self.vase.r.max())
        w = 0.0
        if 21.0 < t < 31.0:
            u = (t - 21.0) / 10.0
            w = wmax * 0.52 * math.sin(math.pi * u) ** 1.35

        # camera direction for the rim light
        rot = np.asarray(self.camera.generate_rotation_matrix(), dtype=float)
        cam_dir = rot.T @ np.array([0.0, 0.0, 1.0])

        quads, cols = self.vase.geometry(w, reveal, cam_dir, dx)
        if quads is not None:
            if fade > 0.0:
                cols[..., :3] = cols[..., :3] * keep + BG_RGB * fade
            self.vase.mesh.quads = quads
            self.vase.mesh.colors = cols
        else:
            self.vase.mesh.quads = np.empty((0, 4, 3))
            self.vase.mesh.colors = np.empty((0, 4, 4))

        # gold cross-section + lathe blade (stroke only: set_opacity fills)
        self.outline.set_points_as_corners(
            self.outline_base + np.array([dx, 0.0, 0.0])
        )
        self.outline.set_stroke(
            color=ManimColor(GOLD), width=2.4,
            opacity=0.95 * ramp(t, 8.0, 9.2) * (1.0 - 0.6 * ramp(t, 31.5, 33.0))
            * (1.0 - 0.45 * (w / max(wmax, 1e-9))) * keep,
        )
        self.blade.set_points_as_corners(self.vase.meridian(w, np.pi + spin, dx))
        self.blade.set_stroke(
            color=ManimColor(GOLD), width=2.0,
            opacity=0.9 * ramp(t, 9.7, 10.4) * (1.0 - ramp(t, 14.8, 16.2)) * keep,
        )

        # HUD
        caps = self.hud
        caps["title"].set_opacity(ramp(t, 0.0, 1.1) * keep)
        caps["subtitle"].set_opacity(ramp(t, 0.0, 1.1) * keep)
        caps["cap1"].set_opacity(ramp(t, 3.2, 4.0) * (1.0 - ramp(t, 8.1, 8.7)) * keep)
        caps["quat"].set_opacity(ramp(t, 10.3, 11.2) * (1.0 - ramp(t, 12.0, 12.8)) * keep)
        caps["spin"].set_opacity(ramp(t, 12.9, 13.8) * (1.0 - ramp(t, 18.4, 19.4)) * keep)
        caps["slice"].set_opacity(ramp(t, 21.4, 22.2) * (1.0 - ramp(t, 30.4, 31.2)) * keep)
        caps["end"].set_opacity(ramp(t, 32.6, 34.0) * keep)
        caps["end2"].set_opacity(ramp(t, 33.4, 34.8) * keep)
        caps["formula"].set_opacity(
            (ramp(t, 2.4, 3.2) * (1.0 - ramp(t, 9.0, 9.8)) + ramp(t, 32.8, 33.6)) * keep
        )

        bar, marker, label = self.slice_hud
        vis = ramp(t, 21.2, 22.0) * (1.0 - ramp(t, 30.6, 31.4)) * keep
        bar.set_opacity(0.85 * vis)
        marker.set_opacity(vis)
        label.set_opacity(0.9 * vis)
        if vis > 0.001:
            marker.set_y(-1.15 + 2.30 * (w / max(wmax, 1e-9)))

    def interpolate_mobject(self, alpha):
        self.state(self.t0 + alpha * self.run_time)


# --------------------------------------------------------------------------
# scene
# --------------------------------------------------------------------------
class FourDMandelbrot(ThreeDScene):
    def construct(self):
        win = MLWindow(1920, 1080)
        win.scene = self
        self.camera.background_color = BG
        self.set_camera_orientation(phi=0.0, theta=-90.0 * DEGREES, zoom=1.0)

        # ---------- assets ----------
        re0, re1 = CX - SPAN_X, CX + SPAN_X
        im0, im1 = CY - IM_HALF, CY + IM_HALF
        xs, ys, esc = mandel_field(re0, re1, im0, im1, IMG_PX_W, IMG_PX_H)

        arr = hero_image(esc)
        image = ImageMobject(arr)
        image.scale_to_fit_width(IMG_WORLD_W)
        image.move_to(ORIGIN)
        image.set_z_index(-5)

        mask = esc >= MAXIT * 0.998
        loops = boundary_loops(mask, xs, ys)
        loop = loops[0]
        arc = upper_arc(loop)
        prof = smooth_profile(resample_arc(arc, N_PROFILE), passes=6)
        prof[:, 1] = np.clip(prof[:, 1], 0.0, None)

        prof_x = (prof[:, 0] - A_MID) * S
        prof_r = prof[:, 1] * S
        mesh = MeshBatch()
        vase = Vase(prof_x, prof_r, mesh)
        win.set_mesh(mesh)

        # full 2D boundary, closed, as a gold outline in the plane
        outline = VMobject(stroke_color=ManimColor(GOLD), stroke_width=2.4)
        full = loop.copy()
        if np.hypot(*(full[0] - full[-1])) > 1e-9:
            full = np.vstack([full, full[0]])
        outline.set_points_as_corners(
            np.column_stack(
                [
                    (full[:, 0] - A_MID) * S,
                    (full[:, 1] - CY) * S,
                    np.zeros(len(full)),
                ]
            )
        )
        outline.set_fill(opacity=0.0)
        outline.set_opacity(0.0)

        blade = VMobject(stroke_color=ManimColor(GOLD), stroke_width=2.0)
        blade.set_points_as_corners(vase.meridian(0.0, 0.0))
        blade.set_fill(opacity=0.0)
        blade.set_opacity(0.0)

        # ---------- HUD ----------
        title = Text("The Mandelbrot set", font="Cambria", font_size=46, color=INK)
        title.to_corner([-1, 1, 0], buff=0.62)
        subtitle = Text(
            "in four dimensions", font="Cambria", font_size=26, color=DIM
        )
        subtitle.next_to(title, DOWN, buff=0.12, aligned_edge=LEFT)

        formula = MathTex(
            r"z_{n+1} = z_n^2 + c", font_size=40, color=GOLD
        )
        formula.to_corner([1, -1, 0], buff=0.62)

        cap1 = Text(
            "c ∈ ℂ — keep the orbit of 0 bounded",
            font="Cambria", font_size=25, color=DIM,
        )
        cap1.to_corner([-1, -1, 0], buff=0.62)

        cap_quat = MathTex(
            r"c = a + b\,i + c\,j + d\,k \in \mathbb{H}",
            font_size=38, color=CYAN,
        )
        cap_quat.to_corner([-1, -1, 0], buff=0.62)

        cap_spin = Text(
            "squaring commutes with rotations of (i, j, k) — so spin the plane",
            font="Cambria", font_size=25, color=DIM,
        )
        cap_spin.to_corner([-1, -1, 0], buff=0.62)

        cap_slice = Text(
            "cut the 4D solid: the thin filaments go first",
            font="Cambria", font_size=25, color=DIM,
        )
        cap_slice.to_corner([-1, -1, 0], buff=0.62)

        cap_end = MathTex(r"\mathcal{M}_4 \subset \mathbb{H}", font_size=54, color=WHITE)
        cap_end.move_to([-4.0, 0.75, 0.0])
        cap_end2 = Text(
            "the quaternion Mandelbrot set\none Mandelbrot, spun through four dimensions",
            font="Cambria", font_size=22, color=DIM, line_spacing=0.85,
        )
        cap_end2.next_to(cap_end, DOWN, buff=0.34)

        # w slider
        bar = RoundedRectangle(
            corner_radius=0.04, width=0.07, height=2.4,
            fill_color=FAINT, fill_opacity=1.0, stroke_width=0,
        )
        bar.move_to([5.9, 0.0, 0.0])
        marker = Rectangle(
            width=0.52, height=0.055, fill_color=GOLD, fill_opacity=1.0, stroke_width=0
        )
        marker.next_to(bar, LEFT, buff=0.10)
        wlabel = MathTex(r"w", font_size=30, color=GOLD)
        wlabel.next_to(bar, UP, buff=0.18)

        for m in (title, subtitle, formula, cap1, cap_quat, cap_spin,
                  cap_slice, cap_end, cap_end2, bar, marker, wlabel):
            m.set_opacity(0.0)
            self.add_fixed_in_frame_mobjects(m)

        self.add(image, outline, blade)

        # one pure timeline: every frame is a function of t, so any worker or
        # seek reproduces it exactly
        hud = {
            "title": title, "subtitle": subtitle, "formula": formula,
            "cap1": cap1, "quat": cap_quat, "spin": cap_spin,
            "slice": cap_slice, "end": cap_end, "end2": cap_end2,
        }
        story = Story(
            self, vase, None, outline, blade, image, hud,
            (bar, marker, wlabel), t0=0.0, run_time=38.8, total=38.8,
            outline_base=outline.points.copy(),
        )
        win.play(story, run_time=38.8)
        win.close()


# --------------------------------------------------------------------------
# entry
# --------------------------------------------------------------------------
def render(out_path="out/four_d_mandelbrot.mp4", jobs=None):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    t0 = time.time()
    res = fast_record_scene(
        FourDMandelbrot, out_path, overwrite=True, jobs=jobs, cleanup=False
    )
    print("[render] %.1f s -> %s" % (time.time() - t0, res.get("files")))
    return res


def stills(times, out_dir="frames"):
    from real_time_manim import FrameServer

    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    fs = FrameServer(FourDMandelbrot)
    print("[prepare] %.1f s, duration %.2f s" % (time.time() - t0, fs.duration))
    try:
        for t in times:
            p = os.path.join(out_dir, "m4_t%05.2f.png" % t)
            fs.save_frame(t, p)
            print(p)
    finally:
        fs.close()


def preview(controls="input", start_frame=0, out_dir="frames"):
    """Scrub GUI with a native progress bar (FramePreview)."""
    from real_time_manim import FramePreview

    t0 = time.time()
    fp = FramePreview(
        FourDMandelbrot, out_dir=out_dir, controls=controls, use_bar=True
    )
    print(
        "[preview] ready in %.1f s -- %.1f s / %d frames"
        % (time.time() - t0, fp.duration, fp.n_frames)
    )
    print(
        "[preview] type 120 or 2.5s to jump, +10/-1 to step, s to save a PNG, "
        "p to play from here, q to quit"
    )
    return fp.run(start_frame=start_frame)


def main(argv=None):
    ap = argparse.ArgumentParser(description="4D Mandelbrot, 3b1b style (RTM)")
    ap.add_argument("--out", default="out/four_d_mandelbrot.mp4")
    ap.add_argument("--jobs", type=int, default=None)
    ap.add_argument("--still", default=None,
                    help="comma separated seconds; write PNGs instead of a video")
    ap.add_argument("--still-dir", default="frames")
    ap.add_argument(
        "--preview", nargs="?", const="input", choices=("input", "slider"),
        default=None,
        help="open the scrub GUI with a native progress bar "
             "(controls: input or slider)",
    )
    ap.add_argument("--preview-frame", type=int, default=0,
                    help="frame to start the preview at")
    args = ap.parse_args(argv)
    if args.preview:
        return preview(args.preview, args.preview_frame)
    if args.still:
        times = [float(x) for x in args.still.split(",") if x.strip()]
        stills(times, args.still_dir)
        return 0
    render(args.out, jobs=args.jobs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
