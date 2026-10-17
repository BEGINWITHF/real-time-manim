"""Coordinate conversion (manim -> screen) plus fill/stroke colour, shading
and opacity extraction."""

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


def shaded_fill_gradient(mob, w, h):
    """``(c1, c2, p1, p2)`` for a fill CE paints as a LINEAR GRADIENT, else ``None``.

    Two callers, one contract: **both stops as 0-255 ints plus their two
    projected endpoints in screen pixels**, exactly what ``_send_vmobject``
    hands native's ``AddBezierPath(..., fr2, fg2, fb2, gx1, gy1, gx2, gy2)``
    (``render/text/vmobject.py``).

    * A ``shade_in_3d`` face: manim shades it with two stops -- its start- and
      end-corner colours -- and Cairo interpolates across the path.
      ``shaded_fill_rgb`` averages them for callers that take a single colour;
      this returns both stops plus the projected corner positions so the native
      bezier fill can interpolate the same way.  Without it the peak of a
      curved surface is clipped: CE's Sphere limb reaches luma 249 where the
      averaged colour tops out near 195.
    * Any other multi-stop fill (NEW branch below): CE does the same thing for
      them, so RTM must too -- see :func:`_multi_stop_fill_gradient`.
    """
    grad = _shaded_face_gradient(mob, w, h)
    if grad is not None:
        return grad
    return _multi_stop_fill_gradient(mob, w, h)


def _shaded_face_gradient(mob, w, h):
    """The original ``shade_in_3d`` branch of :func:`shaded_fill_gradient`."""
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
    last_rgb = rgbas[min(1, len(rgbas) - 1)][:3]
    first = np.clip(_shade_one(rgbas[0][:3], points[start],
                               _corner_normal(points, start), light_source),
                    0.0, 1.0) * 255.0
    second = np.clip(_shade_one(last_rgb, points[end],
                                _corner_normal(points, end), light_source),
                     0.0, 1.0) * 255.0
    sx1, sy1 = manim_to_screen(points[start][0], points[start][1], w, h,
                               points[start][2])
    sx2, sy2 = manim_to_screen(points[end][0], points[end][1], w, h,
                               points[end][2])
    return ((int(first[0]), int(first[1]), int(first[2])),
            (int(second[0]), int(second[1]), int(second[2])),
            (sx1, sy1), (sx2, sy2))


def fill_gradient_stops(mob):
    """``fill_rgbas`` when ``mob``'s fill is a MULTI-STOP ramp, else ``None``.

    CE turns any ``fill_rgbas`` carrying more than one DISTINCT row into a
    ``cairo.LinearGradient`` over ``get_gradient_start_and_end_points()`` --
    one ``add_color_stop_rgba`` per row (``Camera.set_cairo_context_color``,
    quoted in :func:`_multi_stop_fill_gradient`).  "More than one distinct row"
    is therefore exactly the test for "this fill is a ramp, not a flat
    colour"; a fill whose rows are all identical is flat and answers
    ``None``, so every already-correct shape keeps the code path it was
    measured on.

    Two callers, one truth: :func:`_multi_stop_fill_gradient` decides *what
    colour* to hand native, and the window's polygon dispatch decides *which
    sender* may paint the shape at all (native's ``AddPolygon`` has no
    gradient channel, so a ramping polygon has to go down the bezier path --
    ``window/paint.py``).
    """
    try:
        rgbas = np.asarray(mob.get_fill_rgbas(), dtype=float)
    except Exception:
        return None
    if rgbas.ndim != 2 or len(rgbas) < 2:
        return None
    if np.allclose(rgbas[:, :3], rgbas[0][:3], atol=1e-6, rtol=0.0):
        return None                          # every stop identical: flat
    return rgbas


def _multi_stop_fill_gradient(mob, w, h):
    """``(c1, c2, p1, p2)`` for a flat-free multi-stop fill, else ``None``.

    CE's own rule for a fill's colour, verbatim from
    ``camera/camera.py:731-746`` (``Camera.set_cairo_context_color``)::

        if len(rgbas) == 1:
            ctx.set_source_rgba(*rgbas[0]...)          # flat
        else:
            points = vmobject.get_gradient_start_and_end_points()
            pat = cairo.LinearGradient(*chain(*(p[:2] for p in points)))
            offsets = np.linspace(0, 1, len(rgbas))
            ...add_color_stop_rgba(offset, ...)        # one stop per row

    so **any** ``fill_rgbas`` with more than one row is a ramp across
    ``get_gradient_start_and_end_points()`` -- which is what
    ``Polygon(...).set_color((C1, C2))`` (what ``Axes.get_area`` builds) and
    ``set_sheen`` both produce.  RTM's generic filler averaged those rows
    instead (``render/text/vmobject.py``: "Average the stops"), painting the
    whole shape ONE flat mid colour.

    Measured on wiki ``05-坐标系与图表/06-面积与黎曼矩形``
    ``06-面积与黎曼矩形-area.mp4`` "有渐变色没有正确生效" at f220 (960x540 →
    1920x1080 video), the filled band along one scan line:

        x       RTM (before)   CE
        0.40    (65,116,95)    (70,114,79)   <- CE near the GREEN stop
        0.55    (65,116,95)    (61,114,104)
        0.70    (65,116,95)    (61,114,104)  -> rising to the BLUE_C stop

    and ``(65,116,95)`` is exactly the mean of the two stops blended at the
    polygon's 0.6 opacity over black: 0.6 * mean(BLUE_C, GREEN) =
    0.6 * (110,195,162) = (66,117,97).  The gradient was replaced by its own
    average -- peak pixel error 80/255, 350 px off per frame, mean|diff| 1.025.

    Only two stops can be handed to native (``AddBezierPath`` takes
    ``fr2/fg2/fb2`` + one axis), so first/last rows become the ramp's ends.
    That is EXACT for a 2-row fill (manim's normal case) and for the N-row
    arrays ``update_rgbas_array`` stretches linearly; a fill whose rows are all
    equal is flat and returns None, so every already-correct shape keeps taking
    the code path it was measured on.

    The axis is ``get_gradient_start_and_end_points()`` itself -- the method CE
    calls -- projected through the same ``manim_to_screen`` that draws the
    shape, so a zooming/panning camera keeps the ramp pinned to the geometry.
    """
    rgbas = fill_gradient_stops(mob)
    if rgbas is None:
        return None
    first = rgbas[0][:3]
    last = rgbas[-1][:3]
    try:
        p1, p2 = mob.get_gradient_start_and_end_points()
    except Exception:
        return None
    p1 = np.asarray(p1, dtype=float).ravel()
    p2 = np.asarray(p2, dtype=float).ravel()
    s1 = manim_to_screen(float(p1[0]), float(p1[1]), w, h,
                         float(p1[2]) if p1.size > 2 else 0.0)
    s2 = manim_to_screen(float(p2[0]), float(p2[1]), w, h,
                         float(p2[2]) if p2.size > 2 else 0.0)
    if abs(s2[0] - s1[0]) < 1e-6 and abs(s2[1] - s1[1]) < 1e-6:
        # Degenerate axis (a sheen direction the projection collapses): cairo
        # would draw a constant, and native's gradient maths would divide by
        # |g|^2 == 0 -- keep the old single-colour path instead of a NaN fill.
        return None
    c1 = tuple(int(round(float(v) * 255)) for v in first)
    c2 = tuple(int(round(float(v) * 255)) for v in last)
    return c1, c2, (float(s1[0]), float(s1[1])), (float(s2[0]), float(s2[1]))


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
