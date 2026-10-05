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

import numpy as np

# id(image) -> (r, g, b) in 0..1, or None when the image is unusable
_cache: dict[int, tuple | None] = {}


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
    if key in _cache:
        return _cache[key]
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
    _cache[key] = out
    return out
