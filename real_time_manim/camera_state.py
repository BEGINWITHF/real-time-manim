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

# The frame's default height in manim units -- what manim's own Camera uses and
# what the pre-Phase-5 conversion hard-coded.
DEFAULT_FRAME_HEIGHT = 8.0

# Published for the current frame; None means "use the default fixed frame".
_viewport = None


class Viewport:
    """The visible rectangle of manim space, in manim units."""

    __slots__ = ("center", "height")

    def __init__(self, center=(0.0, 0.0), height=DEFAULT_FRAME_HEIGHT):
        self.center = (float(center[0]), float(center[1]))
        self.height = float(height) or DEFAULT_FRAME_HEIGHT

    def project(self, x, y, w, h):
        """Map a manim point to screen pixels for a ``w``x``h`` surface.

        Uniform scale (manim keeps the frame's aspect), y flipped.
        """
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
    set_viewport(viewport_from_scene(scene))
