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

import math

import numpy as np

# The frame's default height in manim units -- what manim's own Camera uses and
# what the pre-Phase-5 conversion hard-coded.
DEFAULT_FRAME_HEIGHT = 8.0

# Published for the current frame; None means "use the default fixed frame".
_viewport = None


def screen_scale(w, h, frame_height=None):
    """Uniform pixels-per-manim-unit for a ``w``x``h`` surface.

    manim declares its frame as ``config.frame_width`` x ``config.frame_height``
    (14.222222 x 8.0, the 16:9 defaults) and scales a surface uniformly by
    ``pixel_width / frame_width``.  Deriving the frame width from the surface's
    own aspect instead -- ``w * 8.0 / h``, which is what this conversion did --
    gives 14.2333 at 854x480, i.e. 0.076 % too wide:

        854 / (128/9) = 60.046875   <- manim CE (measured 60.0461, err 0.0008)
        480 / 8       = 60.000000   <- what RTM used    (measured 60.0003)

    Both mappings agree exactly at the frame centre and diverge linearly to
    +-0.31 px at the edges.  A 1.2 px stroke straddles pixel boundaries
    differently at those offsets: RTM put every grid rule on an integer pixel
    (a 0.5/0.5 split, both halves above the 55-gray threshold) where manim left
    them at x.72 (an 0.875/0.325 split, one half below it).  Measured on
    VectorBasicsScene that was 3641 extra pixels -- 100 % of them within 1 px of
    CE's ink, 84 % in runs >= 6 px -- which tripped compare_auto's detector C
    (C_extra 0.1355 > 0.10).

    At an exact 16:9 size the two formulas coincide (``1920/(128/9) == 1080/8 ==
    135``), so this never moved the 1920x1080 renders.

    ``frame_height`` is how many manim units are currently visible; ``None``
    means the default full frame.  A zoomed viewport therefore scales up by
    ``config.frame_height / frame_height``, matching manim's MovingCamera.
    """
    try:
        from manim import config
        fw = float(config.frame_width)
        fh = float(config.frame_height)
        if fw > 0.0:
            s = float(w) / fw
            if frame_height is not None and fh > 0.0:
                s *= fh / float(frame_height)
            return s
    except Exception:                              # pragma: no cover - no manim
        pass
    # manim unavailable: keep the pre-existing pixel-aspect derivation.
    return float(h) / (float(frame_height) if frame_height else DEFAULT_FRAME_HEIGHT)


class Viewport:
    """The visible rectangle of manim space, in manim units."""

    __slots__ = ("center", "height", "rotation", "frame_center",
                 "focal_distance", "exponential", "light_source")

    def __init__(self, center=(0.0, 0.0), height=DEFAULT_FRAME_HEIGHT, rotation=None,
                 frame_center=(0.0, 0.0, 0.0), focal_distance=None,
                 exponential=False, light_source=None):
        self.center = (float(center[0]), float(center[1]))
        self.height = float(height) or DEFAULT_FRAME_HEIGHT
        # 3x3 camera rotation for the ThreeDCamera family (None for 2D).  Taken
        # from manim's own `generate_rotation_matrix()` so both agree.
        self.rotation = rotation
        # manim's `project_points` subtracts `frame_center` *before* rotating and
        # then scales each point by focal_distance/(focal_distance - z); doing the
        # subtraction after the rotation (or skipping the perspective term) put the
        # 3D content in the wrong place (measured IoU vs CE: 0.28-0.51).
        self.frame_center = (float(frame_center[0]), float(frame_center[1]),
                            float(frame_center[2]))
        self.focal_distance = None if focal_distance is None else float(focal_distance)
        self.exponential = bool(exponential)
        # The ThreeDCamera's light, in world units.  Its shading model sets each
        # `shade_in_3d` face's colour from this, so the renderer needs it too.
        self.light_source = None if light_source is None else tuple(
            float(v) for v in light_source)

    def project(self, x, y, w, h, z=0.0):
        """Map a manim point to screen pixels for a ``w``x``h`` surface.

        Rotates first when the scene has a 3D camera (manim does the same), then
        applies the uniform scale (frame aspect is fixed) and flips y.
        """
        s = screen_scale(w, h, self.height)
        if self.rotation is not None:
            r = self.rotation
            ox, oy, oz = self.frame_center
            px, py, pz = x - ox, y - oy, z - oz
            rx = r[0][0] * px + r[0][1] * py + r[0][2] * pz
            ry = r[1][0] * px + r[1][1] * py + r[1][2] * pz
            rz = r[2][0] * px + r[2][1] * py + r[2][2] * pz
            distance = self.focal_distance
            if distance and abs(distance) > 1e-6:
                if self.exponential:
                    factor = math.exp(rz / distance)
                    if rz < 0.0:
                        factor = distance / (distance - rz) if abs(distance - rz) > 1e-6 else 1.0
                else:
                    denominator = distance - rz
                    factor = distance / denominator if abs(denominator) > 1e-6 else 1.0
                rx *= factor
                ry *= factor
            return float(w / 2.0 + rx * s), float(h / 2.0 - ry * s)
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
            try:
                frame_center = np.asarray(cam.frame_center, dtype=float).reshape(-1)[:3]
            except Exception:
                frame_center = (0.0, 0.0, 0.0)
            get_focal = getattr(cam, "get_focal_distance", None)
            try:
                focal_distance = float(get_focal()) if callable(get_focal) else None
            except Exception:
                focal_distance = None
            # manim keeps the light as a Point mobject (default
            # 9*DOWN + 7*LEFT + 10*OUT); the shader reads its first point.
            light_source = None
            _light = getattr(cam, "light_source", None)
            if _light is not None:
                try:
                    light_source = np.asarray(_light.points[0], dtype=float).reshape(-1)[:3]
                except Exception:
                    light_source = None
            return Viewport(center, height, rotation=rot,
                            frame_center=frame_center,
                            focal_distance=focal_distance,
                            exponential=bool(getattr(cam, "exponential_projection", False)),
                            light_source=light_source)

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
