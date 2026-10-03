"""Camera / viewport state for the renderer (plan Phase 5.0-5.1).

Every sender converts manim units to screen pixels through
``vulkan_util.manim_to_screen`` -- 30 call sites, all funnel through it.  That
function assumed the fixed default frame (8 manim units tall, centred on the
origin), which is why a moving/zooming camera had no effect on RTM's output
(``MovingCameraProbe`` diverged by 32.24: lit 4791 vs 9579).

Rather than thread a viewport through 30 call sites, the current frame's viewport
is published here and consulted by ``manim_to_screen``:

    set_viewport_from_scene(scene)      # once per frame, from MLWindow.sync
    manim_to_screen(x, y, w, h)         # picks it up automatically

With no camera frame (a plain ``Scene``) the viewport is ``None`` and the mapping
is exactly what it was before, so nothing changes for non-camera scenes.
"""

from __future__ import annotations

import numpy as np

# The frame's default height in manim units -- what manim's own Camera uses and
# what the pre-Phase-5 conversion hard-coded.
DEFAULT_FRAME_HEIGHT = 8.0

# Published for the current frame; None means "use the default fixed frame".
_viewport = None


class Viewport:
    """The visible rectangle of manim space, in manim units."""

    __slots__ = ("center", "height", "rotation")

    def __init__(self, center=(0.0, 0.0), height=DEFAULT_FRAME_HEIGHT, rotation=None):
        self.center = (float(center[0]), float(center[1]))
        self.height = float(height) or DEFAULT_FRAME_HEIGHT
        # 3x3 camera rotation for the ThreeDCamera family (None for 2D).  Taken
        # from manim's own `generate_rotation_matrix()` so both agree.
        self.rotation = rotation

    def project(self, x, y, w, h, z=0.0):
        """Map a manim point to screen pixels for a ``w``x``h`` surface.

        Rotates first when the scene has a 3D camera (manim does the same), then
        applies the uniform scale (frame aspect is fixed) and flips y.
        """
        if self.rotation is not None:
            r = self.rotation
            x, y = (r[0][0] * x + r[0][1] * y + r[0][2] * z,
                    r[1][0] * x + r[1][1] * y + r[1][2] * z)
        s = float(h) / self.height
        cx, cy = self.center
        return float(w / 2.0 + (x - cx) * s), float(h / 2.0 - (y - cy) * s)

    def __repr__(self):                          # pragma: no cover - debugging aid
        return f"Viewport(center={self.center}, height={self.height})"


def set_viewport(viewport):
    """Publish (or clear, with ``None``) the viewport for the current frame."""
    global _viewport
    _viewport = viewport


def get_viewport():
    return _viewport


def viewport_from_scene(scene):
    """The viewport a scene's camera asks for, or ``None`` for the default frame.

    ``MovingCamera`` (and therefore ``MovingCameraScene``) exposes its view as the
    ``frame`` mobject: centre = where the camera looks, height = how many manim
    units are visible.  Plain ``Camera`` has no ``frame``, so ``None``.
    """
    cam = getattr(scene, "camera", None)
    if cam is None:
        return None

    # ThreeDCamera (and its subclasses): orientation comes from manim's own
    # rotation matrix, height from the frame height scaled by the camera zoom.
    gen = getattr(cam, "generate_rotation_matrix", None)
    if callable(gen):
        try:
            rot = np.asarray(gen(), dtype=float)
            if rot.shape != (3, 3):
                rot = None
        except Exception:
            rot = None
        if rot is not None:
            try:
                center = np.asarray(cam.frame_center, dtype=float)[:2]
            except Exception:
                center = (0.0, 0.0)
            try:
                zoom = float(getattr(cam, "zoom", 1.0) or 1.0)
            except Exception:
                zoom = 1.0
            height = float(getattr(cam, "frame_height", DEFAULT_FRAME_HEIGHT) or
                           DEFAULT_FRAME_HEIGHT) / (zoom if zoom > 1e-6 else 1.0)
            return Viewport(center, height, rotation=rot)

    frame = getattr(cam, "frame", None)
    if frame is None or not hasattr(frame, "get_center"):
        return None
    try:
        center = frame.get_center()
        height = float(getattr(frame, "height", None) or DEFAULT_FRAME_HEIGHT)
    except Exception:
        return None
    if not (height > 0.0):
        height = DEFAULT_FRAME_HEIGHT
    return Viewport((float(center[0]), float(center[1])), height)


def set_viewport_from_scene(scene):
    """Publish the scene's camera viewport (or clear it).  Called once per frame."""
    viewport = viewport_from_scene(scene)
    import os
    path = os.environ.get("RTM_VIEWPORT_DEBUG")
    if path:
        try:
            cam = getattr(scene, "camera", None)
            frame = getattr(cam, "frame", None)
            centre = None if frame is None else tuple(
                round(float(v), 3) for v in frame.get_center())
            height = None if frame is None else round(float(frame.height), 3)
            shown = None if viewport is None else (
                round(viewport.center[0], 3), round(viewport.center[1], 3),
                round(viewport.height, 3), viewport.rotation is not None)
            with open(path, "a", encoding="utf-8") as handle:
                handle.write(f"{type(cam).__name__} frame_centre={centre} "
                             f"frame_height={height} viewport={shown}\n")
        except Exception:
            pass
    set_viewport(viewport)
