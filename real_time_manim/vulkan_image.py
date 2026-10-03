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
"""

import ctypes
import hashlib
import itertools
import os

import numpy as np

from real_time_manim.vulkan_util import manim_to_screen

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

    corners = _corners(mob, window.win_w, window.win_h)
    if corners is None:
        return False

    height, width = arr.shape[0], arr.shape[1]
    rgb = np.ascontiguousarray(arr[:, :, :3], dtype=np.uint8)

    if arr.shape[2] >= 4:
        a_ch = arr[:, :, 3]
        a_min = int(a_ch.min())
        a_max = int(a_ch.max())
    else:
        a_min = a_max = 255

    if a_min == a_max:
        # Uniform alpha: it is the animation's fade, so pass it as the quad's
        # opacity and keep the uploaded bytes identical across frames.  The
        # texture format is R8G8B8A8, so the RGB pixels still need an explicit
        # opaque alpha channel -- uploading three bytes per pixel would shift
        # every sample.
        opacity = float(alpha) * (a_max / 255.0)
        if opacity <= 0.0:
            return True                        # fully faded out: nothing to draw
        key = _digest(str(rgb.shape).encode(), rgb.tobytes())
        data = np.empty((height, width, 4), dtype=np.uint8)
        data[:, :, :3] = rgb
        data[:, :, 3] = 255
    else:
        # Per-pixel alpha (e.g. an ImageMobjectFromCamera with a mask): upload the
        # alpha too and leave the quad opaque.  Costs one upload per changed frame.
        opacity = float(alpha)
        rgba = np.ascontiguousarray(arr[:, :, :4], dtype=np.uint8)
        key = _digest(str(rgba.shape).encode(), rgba.tobytes())
        data = rgba

    if opacity <= 0.0:
        return True

    buf = (ctypes.c_ubyte * data.nbytes).from_buffer_copy(data.tobytes())
    quad = (ctypes.c_float * 8)(*corners)
    window.dll.AddImageQuad(_token(mob), key, buf, int(width), int(height), quad,
                            float(opacity))
    if _DEBUG:
        with open(_DEBUG, "a", encoding="utf-8") as fh:
            fh.write(f"{_token(mob)} key={key} {width}x{height} "
                     f"corners={[round(v, 1) for v in corners]} opacity={opacity:.3f} "
                     f"win={window.win_w}x{window.win_h}\n")
    return True
