import math


def manim_to_screen(x, y, w=800, h=600):
    frame_width = w * 8.0 / h
    sx = w / frame_width
    sy = h / 8.0
    cx, cy = w / 2.0, h / 2.0
    return float(cx + x * sx), float(cy - y * sy)


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

    ``hasattr(mob, 'get_fill_opacity')`` is **not** a usable guard: manim defines
    that getter on every ``Mobject``, but it only forwards to
    ``self.fill_opacity`` -- which ``PMobject`` and parts of the ``ImageMobject``
    family do not have.  So the check passes and the call raises AttributeError
    halfway through rendering (PointCloudDot: no ``stroke_opacity``,
    ImageMobjectFromCamera: no ``fill_opacity``).  Ask for the attribute itself,
    and fall back to the default if it (or the getter) is missing or unusable.
    """
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
