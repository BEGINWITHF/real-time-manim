# -*- coding: utf-8 -*-
"""A ``ThreeDCamera`` zoom must reach the viewport (it used to be dropped).

``ThreeDScene.move_camera`` / ``set_camera_orientation`` / ``set_zoom`` all
animate (or set) ``camera.zoom_tracker``::

    value_tracker_pairs = [..., (zoom, self.camera.zoom_tracker)]   # move_camera
    anims.append(tracker.animate.set_value(value))
    ...
    def set_zoom(self, value): self.zoom_tracker.set_value(value)
    def get_zoom(self):        return self.zoom_tracker.get_value()

``camera.zoom`` is a *different*, dead attribute -- ``ThreeDCamera.__init__``
writes it once from the constructor argument (three_d_camera.py:67) and nothing
ever touches it again.  ``camera_state.viewport_from_scene`` read that dead
attribute, so every 3D camera stayed at zoom 1 while CE multiplied its projected
x/y by ``get_zoom()`` (three_d_camera.py:321,339):

    measured on wiki 01-场景与相机/专用场景 ``02-ThreeDScene-camera.mp4`` f270
    (after ``move_camera(zoom=1.8)``), the row through the cube's face:
        CE   one teal run,  672..1241 px   (569 px wide)
        RTM  two teal runs, 800..1116 px   (316 px = 569 / 1.8, plus a seam)

    frames 223-353 were over 4.0 the whole time the camera was zoomed, and went
    back to ~0 the moment ``set_camera_orientation(..., zoom=1)`` reset it.

The stroke-width half of the same rule is pinned here too: CE applies the zoom
INSIDE ``project_points`` while its cairo matrix keeps the fixed
``frame_width``/``frame_height`` attributes, so a stroke keeps its width as you
zoom ("This ensures lines have constant width as you zoom in on them." --
camera.py ``apply_stroke``).  A ``MovingCamera`` is the opposite: its frame
really shrinks and the matrix scales with it, so its strokes scale.

Pure Python: a ``Scene`` object, no window, no GPU, no images.
"""
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

try:
    import real_time_manim.camera_state as camera_state
    from real_time_manim.camera_state import screen_scale
    from real_time_manim.render.shapes import ShapeMixin
    from manim import Line, MovingCameraScene, ThreeDScene
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)

W, H = 1920, 1080
FRAME_HEIGHT = 8.0
ZOOM = 1.8


@pytest.fixture(autouse=True)
def restore_viewport():
    """``camera_state`` publishes one global viewport: put it back."""
    prev = camera_state._viewport
    yield
    camera_state._viewport = prev


class _Renderer(ShapeMixin):
    """Enough of a sender for ``_stroke_width``: only ``win_h`` is read."""

    win_h = H


def _zoom_3d_scene(zoom):
    """A ``ThreeDScene`` whose camera was zoomed the way the wiki does it.

    ``set_zoom`` is what ``ThreeDScene.set_camera_orientation`` calls, and it
    writes the tracker -- never ``camera.zoom``.
    """
    scene = ThreeDScene()
    scene.camera.set_zoom(zoom)
    return scene


def test_dead_zoom_attribute_is_not_what_we_read():
    """Guard the mechanism: ``camera.zoom`` does NOT follow ``set_zoom``."""
    scene = _zoom_3d_scene(ZOOM)
    assert scene.camera.zoom == pytest.approx(1.0), (
        "ThreeDCamera.zoom unexpectedly tracks set_zoom(); the live value is "
        "zoom_tracker/get_zoom")
    assert scene.camera.get_zoom() == pytest.approx(ZOOM)


def test_three_d_camera_zoom_narrows_the_viewport():
    """The reported bug: the viewport must shrink with the camera zoom."""
    plain = camera_state.viewport_from_scene(ThreeDScene())
    zoomed = camera_state.viewport_from_scene(_zoom_3d_scene(ZOOM))
    assert plain is not None and zoomed is not None
    assert plain.height == pytest.approx(FRAME_HEIGHT)
    assert zoomed.height == pytest.approx(FRAME_HEIGHT / ZOOM), (
        "ThreeDCamera zoom dropped: visible height %.4f, expected %.4f -- the "
        "cube would keep its unzoomed size (569 px -> 316 px measured on "
        "02-ThreeDScene-camera f270)"
        % (zoomed.height, FRAME_HEIGHT / ZOOM))


def test_three_d_zoom_scales_positions():
    """A zoomed 3D point far from the centre must land ``zoom`` times further."""
    plain = camera_state.viewport_from_scene(ThreeDScene())
    zoomed = camera_state.viewport_from_scene(_zoom_3d_scene(ZOOM))
    x0, y0 = plain.project(1.0, 0.5, W, H)
    x1, y1 = zoomed.project(1.0, 0.5, W, H)
    # the scale is uniform about the frame centre
    k_plain = screen_scale(W, H, plain.height)
    k_zoomed = screen_scale(W, H, zoomed.height)
    assert k_zoomed == pytest.approx(k_plain * ZOOM, rel=1e-9)
    assert x1 - W / 2.0 == pytest.approx((x0 - W / 2.0) * ZOOM, rel=1e-6)
    assert H / 2.0 - y1 == pytest.approx((H / 2.0 - y0) * ZOOM, rel=1e-6)


def test_move_camera_zoom_tracker_is_live():
    """``move_camera(zoom=...)`` animates the tracker: the viewport must follow.

    A mid-animation frame is simulated by setting the tracker to an
    intermediate value -- exactly the state ``ValueTracker.animate.set_value``
    leaves behind on that frame.
    """
    scene = ThreeDScene()
    scene.camera.zoom_tracker.set_value(1.5)
    vp = camera_state.viewport_from_scene(scene)
    assert vp.height == pytest.approx(FRAME_HEIGHT / 1.5)


def test_three_d_zoom_keeps_stroke_width_constant():
    """CE keeps a 3D stroke's width while zooming; so must RTM."""
    camera_state.set_viewport(camera_state.viewport_from_scene(
        _zoom_3d_scene(ZOOM)))
    line = Line(stroke_width=2)
    expected = 2 * 0.01 * (H / FRAME_HEIGHT)          # unchanged by the zoom
    got = _Renderer()._stroke_width(line)
    assert got == pytest.approx(expected, rel=1e-9), (
        "a 3D-zoomed stroke came out %.4f px, expected the unzoomed %.4f px"
        % (got, expected))
    # ... while the frame height the *geometry* sizes use does shrink
    assert ShapeMixin._visible_frame_height() == pytest.approx(FRAME_HEIGHT / ZOOM)
    assert ShapeMixin._unit_frame_height() == pytest.approx(FRAME_HEIGHT)


def test_moving_camera_zoom_does_scale_stroke_width():
    """The other half of the rule: a shrinkable frame scales its strokes."""
    scene = MovingCameraScene()
    scene.camera.frame.scale(0.5)                     # frame height 8 -> 4
    vp = camera_state.viewport_from_scene(scene)
    assert vp.height == pytest.approx(4.0)
    assert vp.unit_height == pytest.approx(4.0), (
        "MovingCamera's cairo matrix uses the shrunk frame, so its strokes "
        "scale with the zoom")
    camera_state.set_viewport(vp)
    assert _Renderer()._stroke_width(Line(stroke_width=2)) == pytest.approx(
        2 * 0.01 * (H / 4.0), rel=1e-9)
