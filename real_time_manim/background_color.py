"""Stroke colour for a mobject that carries a `background_image`.

manim keeps stroke colour **per point**, and the `VectorField` family
(`StreamLines`, `ArrowVectorField`, ...) only ever sets a *background image* on
each line (`VMobject.color_using_background_image`); the stroke rgba itself is
left WHITE and the Cairo renderer does the tinting
(`Camera.display_multiple_background_colored_vmobjects` ->
`BackgroundColoredVMobjectDisplayer.display`, which renders the strokes into a
coverage mask and multiplies it by that image).

RTM therefore drew an entire vector field white where CE renders reds
(measured `VectorFieldsAndTrackers`: CE's `trails` half is (160,96,96) /
(192,96,96), RTM's is (224,224,224) / (96,96,96), 4832 white pixels against
CE's 768 -- which are only the caption).

Per-pixel colour is out of reach for the vector path, so this takes the mean
colour of the image itself (the field's own gradient), cached per image, and
uses it as the line's stroke colour.
"""

from __future__ import annotations

import weakref

import numpy as np

# id(image) -> (weakref to that image, (r, g, b) in 0..1 or None).
#
# The key is `id(image)` only because PIL's ``Image`` is UNHASHABLE (verified:
# ``hash(Image.new(...))`` raises TypeError), so a ``WeakKeyDictionary`` keyed
# on the image itself is not available.  ids are recycled the instant an object
# is collected, though, so the bare-id cache this replaced could resolve a
# freshly built background image to a DEAD one's colour.  The weakref beside
# each value detects exactly that: a recycled id means the original object is
# gone and ``ref()`` has been cleared, so the entry is dropped and recomputed.
# Nothing is ever evicted by size and nothing survives its image.
_cache: dict[int, tuple[weakref.ref, tuple | None]] = {}


def background_image_rgb(mob):
    """Mean colour of ``mob``'s background image, or ``None`` if it has none."""
    getter = getattr(mob, "get_background_image", None)
    if getter is None:
        return None
    try:
        image = getter()
    except Exception:
        return None
    if not image:
        return None
    return image_mean_rgb(image)


def image_mean_rgb(image):
    """Average colour of an image's non-transparent pixels (0..1 floats)."""
    key = id(image)
    hit = _cache.get(key)
    if hit is not None:
        ref, value = hit
        if ref() is image:          # same object, id not recycled
            return value
        # id was recycled (or the ref was cleared): fall through and recompute.
    out = None
    try:
        arr = np.asarray(image.convert("RGBA"), dtype=float)
        alpha = arr[..., 3]
        mask = alpha > 8.0
        if mask.any():
            rgb = arr[..., :3][mask].mean(axis=0) / 255.0
            out = (float(rgb[0]), float(rgb[1]), float(rgb[2]))
    except Exception:
        out = None

    def _drop(_ref, _key=key):
        _cache.pop(_key, None)

    try:
        ref = weakref.ref(image, _drop)
    except TypeError:               # not weak-referenceable: keep it uncached
        return out
    _cache[key] = (ref, out)
    return out
