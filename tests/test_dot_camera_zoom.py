"""A `Dot` must change size with the camera frame, not keep its pre-zoom size.

Reported (user): "FollowingGraphCamera.mp4 里橘色点的大小在整段视频里不一致" --
the orange dot of ``FollowingGraphCamera`` is a different size depending on
which part of the video you look at.

Mechanism, measured on the two renders at 1080p (``videos_{ce,rtm}_hq`` ->
orange blob bounding box, 10 samples/s):

    t=     0.0  0.1  0.2 ... 0.5  0.6 ... 0.9  1.0 .. 1.9  2.0  2.5 .. 2.9
    CE    22   22   22      31   36      43   44   44..44   44   26   22
    RTM   21   22   22      22   22      21   44   44..44   21   21   21

CE grows the disc smoothly over ``camera.frame.animate.scale(0.5)`` (frame height
8 -> 4, so every manim unit is twice as many pixels) and shrinks it again over
``Restore``; RTM held one constant size during both camera plays and snapped to
the other size at each play boundary -- a dot whose size depends on where in the
video you pause.

Why: ``_send_dot`` converted its radius with ``h / 8.0``, the DEFAULT frame
height, while ``manim_to_screen`` (its centre) already followed the visible one.
Only the follow segment looked right by accident: ``MoveAlongPath`` marks the dot
``_transforming``, so that play routes it through the point path, which projects
every point and therefore does scale.

This file pins the rule: the emitted radius is the manim radius times the same
pixels-per-unit ``Viewport.project`` places the dot with.  Pure Python, no
ffmpeg, no video comparison.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import real_time_manim.camera_state as camera_state
    import real_time_manim.vulkan_bind as vb
    from real_time_manim.camera_state import Viewport
    from manim import ORANGE, Dot
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)

W, H = 1920, 1080          # the only format MLWindow supports (qh gallery)
ZOOMED_HEIGHT = 4.0        # frame height after `frame.animate.scale(0.5)`
TOL = 0.05                 # px; a rasteriser may quantise, a 2x error may not


@pytest.fixture(scope="module")
def renderer():
    try:
        r = vb.MLWindow(W, H)
    except Exception as e:  # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield r
    try:
        r.close()
    except Exception:
        pass


@pytest.fixture
def viewport():
    """Publish a viewport for one test and put the global state back."""
    prev = camera_state._viewport
    yield
    camera_state._viewport = prev


def frame_height():
    """The helper both `_stroke_width` and `_send_dot` derive their scale from."""
    from real_time_manim.vulkan_shapes import ShapeMixin
    return ShapeMixin._visible_frame_height()


def emitted_radius(renderer, dot, h=H, w=W):
    """The radius `_send_dot` hands to native's AddCircle, or None if no call."""
    orig = renderer.dll.AddCircle
    rec = []

    def _cap(*a):
        rec.append(float(a[2]))              # AddCircle(x, y, r, ...)
        return 0

    renderer.dll.AddCircle = _cap
    try:
        renderer._send_dot(dot, 1.0, w, h)
    finally:
        renderer.dll.AddCircle = orig
    return rec[0] if rec else None


def projected_px_per_unit(height):
    """The scale `Viewport.project` places positions with, for the same frame."""
    vp = Viewport(center=(0.0, 0.0), height=height)
    sx, _sy = vp.project(1.0, 0.0, W, H)
    return sx - W / 2.0


def test_no_camera_keeps_the_old_mapping(renderer, viewport):
    """A plain Scene has no viewport: `h / 8.0`, exactly as before this fix."""
    camera_state._viewport = None
    dot = Dot(color=ORANGE)
    rad = emitted_radius(renderer, dot)
    assert rad is not None, "_send_dot emitted no AddCircle"
    expected = (min(dot.width, dot.height) / 2.0) * (H / 8.0)
    assert rad == pytest.approx(expected, abs=TOL), (
        "unzoomed Dot radius moved: got %.4f px, expected %.4f px (manim radius "
        "%.4f * %d/8)" % (rad, expected, min(dot.width, dot.height) / 2.0, H))


def test_zoomed_camera_doubles_the_dot(renderer, viewport):
    """The reported bug: the dot must grow with the frame it is seen through."""
    dot = Dot(color=ORANGE)
    camera_state._viewport = None
    base = emitted_radius(renderer, dot)
    camera_state._viewport = Viewport(center=(0.0, 0.0), height=ZOOMED_HEIGHT)
    zoomed = emitted_radius(renderer, dot)

    assert base is not None and zoomed is not None
    factor = 8.0 / ZOOMED_HEIGHT
    assert zoomed == pytest.approx(base * factor, abs=TOL), (
        "Dot did not follow the camera zoom: %.4f px at frame height 8 and "
        "%.4f px at frame height %.1f, manim CE gives %.4f px (a factor of %.1f). "
        "The disc would keep its pre-zoom size while its centre moves with the "
        "camera, which is what made FollowingGraphCamera's orange dot a "
        "different size depending on where you pause."
        % (base, zoomed, ZOOMED_HEIGHT, base * factor, factor))


def test_dot_size_uses_the_same_scale_as_its_position(renderer, viewport):
    """Radius and centre must come out of one mapping, or the disc lags behind."""
    dot = Dot(color=ORANGE)
    camera_state._viewport = Viewport(center=(0.0, 0.0), height=ZOOMED_HEIGHT)
    rad = emitted_radius(renderer, dot)
    manim_radius = min(dot.width, dot.height) / 2.0
    assert rad == pytest.approx(manim_radius * projected_px_per_unit(ZOOMED_HEIGHT),
                                abs=TOL), (
        "Dot radius %.4f px != manim radius %.4f x projected %.4f px/unit"
        % (rad, manim_radius, projected_px_per_unit(ZOOMED_HEIGHT)))


def test_frame_height_scales_inverse_to_the_zoom(viewport):
    """Mechanism pin for the helper both the stroke and the dot derive from."""
    camera_state._viewport = None
    assert frame_height() == pytest.approx(8.0)
    for height in (8.0, 6.0, 4.0, 2.0):
        camera_state._viewport = Viewport(center=(0.0, 0.0), height=height)
        assert frame_height() == pytest.approx(height)
