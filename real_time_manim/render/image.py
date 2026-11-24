"""Textured quads: one stable token per mobject owning a GPU texture slot,
refreshed only when the pixel digest changes."""

"""ImageMobject pixels on the native texture pipeline (plan 4.4B).

The renderer draws solid triangles; an ``ImageMobject`` has four points and no
rgba arrays, so before this module existed it came out as an opaque white quad
whose brightness never changed (probe: constant 10.4 against CE's 0.0 -> 6.0
ramp).  Here the pixels are handed to the native texture slot instead.

Two details drive the interface:

* ``ImageMobject.reset_points`` lays the four corners out as
  ``[UL, UR, DL, DR]`` -- *not* a triangle-strip order -- so they are reordered
  to TL, TR, BR, BL before upload.
* A fade does not set an opacity attribute: ``set_opacity`` writes straight into
  the alpha channel of ``pixel_array``.  When that alpha is uniform it becomes the
  quad's opacity (so the digest stays stable and the texture is uploaded once);
  a per-pixel alpha falls back to uploading the bytes and leaving opacity at 1.

Per-frame work is cached on the mobject (``_rtm_tex_cache``): the opaque RGBA
buffer, its digest and its ctypes copy survive until ``_rtm_tex_rev`` /
``_rtm_alpha_rev`` change.  ``ImageMobject.set_color`` / ``set_opacity`` /
``interpolate_color`` bump those counters, ``mark_texture_dirty()`` covers raw
``pixel_array`` writes, and ``ImageMobjectFromCamera.get_pixel_array`` bumps
them because the camera array changes behind the same object.  A static image
or a uniform ``set_opacity`` fade therefore does no hash/RGBA work, and a fully
transparent image returns after one alpha check.

A uniform ``set_opacity`` is a scalar on the mobject (``_rtm_tex_opacity``):
the alpha channel is not rewritten and the value rides the quad opacity, so a
fade costs no per-pixel write.  Per-pixel masks still write/re-upload the
channel, and ``interpolate_color`` carries the scalar for Transform/Fade.
"""

import ctypes
import hashlib
import itertools
import os

import numpy as np

from real_time_manim.render.util import manim_to_screen

_tokens = itertools.count(1)

# Set RTM_TEX_DEBUG=<path> to append every submitted quad (corners, opacity,
# window size) to that file -- the fastest way to tell "Python sent the wrong
# geometry" apart from "native drew it wrong".
_DEBUG = os.environ.get("RTM_TEX_DEBUG") or None


def _pixel_array(mob):
    """The mobject's RGBA array, or None when it has no pixels yet."""
    arr = None
    getter = getattr(mob, 'get_pixel_array', None)
    if getter is not None:
        try:
            arr = getter()
        except Exception:
            arr = None
    if arr is None:
        arr = getattr(mob, 'pixel_array', None)
    try:
        arr = np.asarray(arr)
    except Exception:
        return None
    if arr.ndim != 3 or arr.shape[0] < 1 or arr.shape[1] < 1 or arr.shape[2] < 3:
        return None
    return arr


def _token(mob):
    """Stable per-mobject token, so one mobject owns one GPU texture slot."""
    tok = getattr(mob, '_rtm_tex_token', None)
    if tok is None:
        tok = next(_tokens)
        try:
            mob._rtm_tex_token = tok
        except Exception:                      # slots/immutable types
            pass
    return tok


def _corners(mob, w, h):
    """Screen-space corners in TL, TR, BR, BL order (the shader's uv order)."""
    try:
        pts = mob.get_points()
    except Exception:
        return None
    if pts is None or len(pts) < 4:
        return None
    out = []
    for i in (0, 1, 3, 2):                     # UL, UR, DR, DL
        p = pts[i]
        sx, sy = manim_to_screen(p[0], p[1], w, h, p[2] if len(p) > 2 else 0.0)
        out.append(sx)
        out.append(sy)
    return out


def _digest(*parts):
    d = hashlib.blake2b(digest_size=8)
    for part in parts:
        d.update(part)
    return int.from_bytes(d.digest(), 'little')


def send_image(window, mob, alpha=1.0):
    """Draw ``mob`` through the native texture path.  False when unsupported."""
    arr = _pixel_array(mob)
    if arr is None:
        return False

    alpha = float(alpha)
    if alpha <= 0.0:
        return True

    # `ImageMobject.set_opacity(0)` records the fade in ``stroke_opacity`` and
    # (for now) the pixel alpha.  Either way the image cannot ink anything, so
    # return before reading/copying the pixel array.  The caller still paints
    # the family (an ImageMobjectFromCamera may have a visible frame child).
    try:
        if float(getattr(mob, "stroke_opacity", 1.0) or 0.0) <= 0.0:
            return True
    except Exception:
        pass

    height, width = arr.shape[0], arr.shape[1]
    tex_rev = int(getattr(mob, "_rtm_tex_rev", 0) or 0)
    alpha_rev = int(getattr(mob, "_rtm_alpha_rev", 0) or 0)
    state = getattr(mob, "_rtm_tex_cache", None)
    prev_key = state.get("key") if isinstance(state, dict) else None
    same_array = bool(
        state is not None
        and state.get("tex_rev") == tex_rev
        and state.get("arr_id") == id(arr)
        and state.get("shape") == arr.shape
    )
    if (same_array and state.get("transparent")
            and state.get("alpha_rev") == alpha_rev):
        return True

    # Alpha first: a fully transparent image costs one scan and nothing else.
    # The scan is skipped entirely on a static image (alpha_rev unchanged).
    if same_array and not state.get("transparent") and \
            state.get("alpha_rev") == alpha_rev:
        a_min = state["a_min"]
        a_max = state["a_max"]
    elif arr.shape[2] >= 4:
        a_ch = arr[:, :, 3]
        a_min = int(a_ch.min())
        a_max = int(a_ch.max())
    else:
        a_min = a_max = 255
    if a_max == 0:
        try:
            mob._rtm_tex_cache = {
                "tex_rev": tex_rev, "alpha_rev": alpha_rev,
                "arr_id": id(arr), "shape": arr.shape,
                "a_min": 0, "a_max": 0, "transparent": True,
            }
        except Exception:
            pass
        return True

    uniform = a_min == a_max
    key = None
    buf = None
    if uniform:
        # Uniform alpha: pass it as the quad's opacity and keep the uploaded
        # bytes identical across frames.  An alpha-only change (set_opacity)
        # reuses the opaque RGB buffer; only a texture revision rebuilds it.
        opacity = alpha * (a_max / 255.0) * float(
            getattr(mob, "_rtm_tex_opacity", 1.0) or 1.0)
        if opacity <= 0.0:
            return True
        if same_array and state.get("uniform") and "buf" in state:
            key = state["key"]
            buf = state["buf"]
        else:
            rgb = np.ascontiguousarray(arr[:, :, :3], dtype=np.uint8)
            key = _digest(str(rgb.shape).encode(), rgb.tobytes())
            data = np.empty((height, width, 4), dtype=np.uint8)
            data[:, :, :3] = rgb
            data[:, :, 3] = 255
            buf = (ctypes.c_ubyte * data.nbytes).from_buffer_copy(data)
    else:
        # Per-pixel alpha (e.g. an ImageMobjectFromCamera with a mask): upload
        # the alpha too and leave the quad opaque.  Cache it by both revisions
        # so a still mask is uploaded once, while a camera frame (its getter
        # bumps the revisions) refreshes every call.
        opacity = alpha
        if (same_array and not state.get("uniform", True)
                and state.get("alpha_rev") == alpha_rev and "buf" in state):
            key = state["key"]
            buf = state["buf"]
        else:
            rgba = np.ascontiguousarray(arr[:, :, :4], dtype=np.uint8)
            key = _digest(str(rgba.shape).encode(), rgba.tobytes())
            buf = (ctypes.c_ubyte * rgba.nbytes).from_buffer_copy(rgba)

    if key != prev_key:
        window._diag_tex_uploads = getattr(
            window, "_diag_tex_uploads", 0) + 1

    try:
        mob._rtm_tex_cache = {
            "tex_rev": tex_rev, "alpha_rev": alpha_rev,
            "arr_id": id(arr), "shape": arr.shape,
            "a_min": a_min, "a_max": a_max, "uniform": uniform,
            "key": key, "buf": buf, "transparent": False,
        }
    except Exception:
        pass

    corners = _corners(mob, window.win_w, window.win_h)
    if corners is None:
        return False

    quad = (ctypes.c_float * 8)(*corners)
    window.dll.AddImageQuad(_token(mob), key, buf, int(width), int(height), quad,
                            float(opacity))
    if _DEBUG:
        with open(_DEBUG, "a", encoding="utf-8") as fh:
            fh.write(f"{_token(mob)} key={key} {width}x{height} "
                     f"corners={[round(v, 1) for v in corners]} opacity={opacity:.3f} "
                     f"win={window.win_w}x{window.win_h}\n")
    return True
