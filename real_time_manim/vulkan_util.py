import math

import numpy as np


def manim_to_screen(x, y, w=800, h=600, z=0.0):
    # Phase 5: when the scene's camera exposes a frame (MovingCamera /
    # MovingCameraScene) that viewport is published per frame and every sender
    # funnels through here, so the camera finally affects what is drawn.
    try:
        from real_time_manim.camera_state import get_viewport, screen_scale
        _vp = get_viewport()
        s = screen_scale(w, h)
    except Exception:                            # pragma: no cover
        _vp = None
        s = float(h) / 8.0
    if _vp is not None:
        return _vp.project(x, y, w, h, z)
    cx, cy = w / 2.0, h / 2.0
    return float(cx + x * s), float(cy - y * s)


def rotate_point(x, y, cx, cy, angle):
    if angle == 0:
        return x, y
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    dx = x - cx
    dy = y - cy
    nx = dx * cos_a - dy * sin_a + cx
    ny = dx * sin_a + dy * cos_a + cy
    return nx, ny


def point_path_bounds(mob):
    """The ``(lower, upper)`` a *point-path* sender should draw from ``mob``.

    Point-path senders (``_send_vmobject``, ``_send_polygon``, ``_send_arc``)
    tessellate ``mob.get_points()`` and then walk a fraction of **that** path.
    Two things can already have shortened those points:

    * manim's own ``ShowPartial.interpolate_submobject`` calls
      ``pointwise_become_partial`` with the eased bound, so for a native
      ``Create``/``Uncreate`` the geometry *is* the animation -- walking a
      further ``_vulkan_progress`` fraction of it drew
      ``progress * geometry`` instead of ``geometry`` (measured: ``Uncreate``
      rises to a mid-animation peak and returns to 0, which only a product can
      produce, and frame 25 of AnimationCreationBasics drew 0 px where CE drew
      589).  ``render_hooks._write_progress`` marks those mobjects
      ``_vulkan_points_partial`` and the whole cut path is drawn.
    * an explicit bounds window (``ShowPassingFlash``) -- an intentional clip,
      so it wins over a stale tag.

    Untagged mobjects keep the plain channel: RTM's own animations never
    truncate the points and carry their partial state in the channel alone
    (``animations/create.py``), so they must keep composing as before.
    """
    if hasattr(mob, "_vulkan_progress_upper"):
        return (float(getattr(mob, "_vulkan_progress_lower", 0.0)),
                float(getattr(mob, "_vulkan_progress_upper", 1.0)))
    if getattr(mob, "_vulkan_points_partial", False):
        return 0.0, 1.0
    return 0.0, float(getattr(mob, "_vulkan_progress", 1.0))


def get_fill_rgb(mob, alpha=1.0):
    try:
        rgbas = mob.get_fill_rgbas()
        if len(rgbas) > 0:
            r, g, b, a = rgbas[0]
            fo = float(a)
            return int(r * 255 * alpha * fo), int(g * 255 * alpha * fo), int(b * 255 * alpha * fo)
    except Exception:
        pass
    try:
        rgbas = mob.get_stroke_rgbas()
        if len(rgbas) > 0:
            r, g, b, a = rgbas[0]
            return int(r * 255 * alpha), int(g * 255 * alpha), int(b * 255 * alpha)
    except Exception:
        pass
    # No rgba arrays at all (ImageMobject and friends): at least honour the
    # mobject's own fill opacity instead of falling back to an opaque white quad.
    fo = get_opacity(mob, 'fill', 1.0)
    if fo <= 0:
        return 0, 0, 0
    return int(255 * alpha * fo), int(255 * alpha * fo), int(255 * alpha * fo)


def get_fill_rgb_raw(mob):
    try:
        rgbas = mob.get_fill_rgbas()
        if len(rgbas) > 0:
            r, g, b, _ = rgbas[0]
            return int(r * 255), int(g * 255), int(b * 255)
    except Exception:
        pass
    try:
        rgbas = mob.get_stroke_rgbas()
        if len(rgbas) > 0:
            r, g, b, _ = rgbas[0]
            return int(r * 255), int(g * 255), int(b * 255)
    except Exception:
        pass
    fo = get_opacity(mob, 'fill', 1.0)
    if fo <= 0:
        return 0, 0, 0
    return 255, 255, 255


def _shade_one(rgb, point, unit_normal, light_source):
    """manim's ``get_shaded_rgb`` -- ``rgb + 0.5*(normal . to_light)**3``.

    A negative dot means the face points away, and manim halves the (already
    negative) term, so a face turned from the light darkens rather than glowing.
    """
    to_light = np.asarray(light_source, dtype=float) - np.asarray(point, dtype=float)
    norm = float(np.linalg.norm(to_light))
    if norm <= 1e-12:
        return np.asarray(rgb, dtype=float)
    light = 0.5 * float(np.dot(unit_normal, to_light / norm)) ** 3
    if light < 0.0:
        light *= 0.5
    return np.asarray(rgb, dtype=float) + light


def _unit_normal(v1, v2, tol=1e-6):
    """manim's ``utils.space_ops.get_unit_normal``.

    The non-obvious branch is the aligned one: on a `Surface` cell the two
    tangent vectors are frequently *parallel* (adjacent control points along a
    single edge), and manim then rotates the shared direction 90 degrees toward
    +Z instead of giving up.  Returning a constant up-vector there made the
    first corner of every cell shade from a fixed direction, so the cell lost
    its highlight -- measured on SolidPrimitives3D's Sphere, manim shades one
    cell (88,218,249) -> (28,158,189) while the up-vector version gave
    (29,159,190) -> (28,158,189), flattening the whole surface.
    """
    u1 = np.asarray(v1, dtype=float)
    u2 = np.asarray(v2, dtype=float)
    div1 = float(np.max(np.abs(u1))) if u1.size else 0.0
    div2 = float(np.max(np.abs(u2))) if u2.size else 0.0
    if div1 == 0.0:
        if div2 == 0.0:
            return np.array([0.0, -1.0, 0.0])          # manim: DOWN
        u = u2 / div2
    elif div2 == 0.0:
        u = u1 / div1
    else:
        u1, u2 = u1 / div1, u2 / div2
        cp = np.cross(u1, u2)
        cp_norm = float(np.sqrt(np.sum(cp * cp)))
        if cp_norm > tol:
            return cp / cp_norm
        u = u1
    if abs(u[0]) < tol and abs(u[1]) < tol:
        return np.array([0.0, -1.0, 0.0])              # manim: DOWN
    # Rotate u 90 degrees toward the Z axis: (u x [0,0,1]) x u.
    cp = np.array([-u[0] * u[2], -u[1] * u[2], u[0] * u[0] + u[1] * u[1]])
    return cp / float(np.sqrt(np.sum(cp * cp)))


def _corner_normal(points, index):
    """manim's ``get_3d_vmob_unit_normal`` for one corner of a face."""
    n = len(points)
    if n <= 4:
        return np.array([0.0, 1.0, 0.0])
    im3 = index - 3 if index > 2 else (n - 4)
    ip3 = index + 3 if index < (n - 3) else 3
    a = points[ip3] - points[index]
    b = points[im3] - points[index]
    return _unit_normal(a, b)


def shaded_fill_rgb(mob):
    """A ``shade_in_3d`` face's lit fill colour, or ``None`` when it does not apply.

    ``ThreeDCamera.modified_rgbas`` shades a face's start- and end-corner colours
    from the face's own unit normal and the camera's light source.  Without it
    every face of a Cube / Polyhedron / Prism takes the same colour -- measured
    on SolidPrimitives3D, CE's three cube faces read luma 68 / 82 / 90 where RTM
    drew a flat 80, i.e. the solids had no visible 3D form at all.

    The two corner colours are averaged because the native fill is a single
    colour here; manim's own two stops are nearly equal on a planar face, so the
    average reproduces its constant per-face shade.
    """
    try:
        from real_time_manim.camera_state import get_viewport
        viewport = get_viewport()
    except Exception:
        return None
    if viewport is None or getattr(viewport, "rotation", None) is None:
        return None
    if not getattr(mob, "shade_in_3d", False):
        return None
    light_source = getattr(viewport, "light_source", None)
    if light_source is None:
        return None
    try:
        rgbas = np.asarray(mob.get_fill_rgbas(), dtype=float)
        points = np.asarray(mob.get_points(), dtype=float)
    except Exception:
        return None
    if len(rgbas) == 0 or len(points) < 4:
        return None
    start = 0
    end = ((len(points) - 1) // 6) * 3
    first = _shade_one(rgbas[0][:3], points[start],
                       _corner_normal(points, start), light_source)
    last = _shade_one(rgbas[min(1, len(rgbas) - 1)][:3], points[end],
                      _corner_normal(points, end), light_source)
    lit = np.clip((first + last) / 2.0, 0.0, 1.0) * 255.0
    return int(lit[0]), int(lit[1]), int(lit[2])


def get_stroke_rgb(mob):
    try:
        rgbas = mob.get_stroke_rgbas()
        if len(rgbas) > 0:
            r, g, b, a = rgbas[0]
            return int(r * 255), int(g * 255), int(b * 255)
    except Exception:
        pass
    return 255, 255, 255


def get_stroke_w(mob):
    try:
        sw = mob.get_stroke_width()
        if isinstance(sw, (int, float)):
            return float(sw)
        elif hasattr(sw, '__len__') and len(sw) > 0:
            return float(sw[0])
    except Exception:
        pass
    return 0.0


def get_opacity(mob, kind="stroke", default=1.0):
    """Return a mobject's stroke/fill opacity, or ``default`` when it has none.

    **The animated value lives in the rgba arrays.**  manim interpolates
    ``fill_rgbas`` / ``stroke_rgbas`` per frame; the stored ``*_opacity``
    attributes are not updated (measured: after ``FadeIn(Square())`` at alpha 0.5
    the array holds 0.5 while ``stroke_opacity`` still reads 1.0 -- and for many
    shapes the attribute is 0 while the strokes are perfectly visible, so reading
    it made whole strokes vanish).  So: arrays first, attributes as a fallback.

    The attribute fallback exists because ``hasattr(mob, 'get_fill_opacity')`` is
    **not** a usable guard either: manim defines that getter on every ``Mobject``,
    but it only forwards to ``self.fill_opacity`` -- which ``PMobject`` and parts
    of the ``ImageMobject`` family do not have, so the check passes and the call
    raises AttributeError halfway through rendering.  Ask for the attribute
    itself, and fall back to ``default`` if it (or the getter) is unusable.
    """
    arrays = getattr(mob, "%s_rgbas" % kind, None)
    try:
        if arrays is not None and len(arrays):
            return float(np.asarray(arrays)[:, 3].max())
    except Exception:
        pass
    value = getattr(mob, "%s_opacity" % kind, None)
    if value is None:
        getter = getattr(mob, "get_%s_opacity" % kind, None)
        if getter is not None:
            try:
                value = getter()
            except Exception:
                value = None
    try:
        return default if value is None else float(value)
    except (TypeError, ValueError):
        return default
