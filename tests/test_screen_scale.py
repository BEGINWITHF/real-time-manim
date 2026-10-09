"""RTM's world->pixel scale must be manim's, not the video's pixel aspect.

Measured on VectorBasicsScene (compare_auto frame 6, 854x480 CE):

    CE  centre = 426.9998 + 60.0461 * wx   max|resid| = 0.028
    RTM centre = 427.0028 + 60.0003 * wx   max|resid| = 0.009

Both agree exactly at the frame centre and diverge linearly to +-0.31 px at the
edges -- a 0.076 % scale error.  Stroke half-widths match (h = 0.600 both, so
``_stroke_layers`` is fine); only the mapping is wrong.

Cause: ``manim_to_screen`` derived its frame width from the *pixel* aspect
(``w * 8.0 / h`` = 14.2333 at 854x480) while manim declares
``config.frame_width = 14.222222`` (128/9, the 16:9 default), and scales
uniformly by ``pixel_width / frame_width``:

    854 / (128/9)            = 60.046875   <- measured CE 60.0461 (err 0.0008)
    480 / 8                  = 60.000000   <- measured RTM 60.0003

Because a 1.2 px stroke straddles pixel boundaries differently at those offsets,
RTM lit a second column where CE lit one: 3641 extra pixels, 100 % of them
within 1 px of CE's ink, 84 % in runs >= 6 px -- which tripped compare_auto's
detector C (C_extra 0.1355 > 0.10) and kept VectorBasicsScene at CONTENT.

At an exact 16:9 resolution the two scales coincide
(``1920 / (128/9) == 1080 / 8 == 135``), so this only ever bit the 854x480
renders.
"""
import pytest

from real_time_manim import camera_state
from real_time_manim.vulkan_util import manim_to_screen

W, H = 854, 480


def _expected_scale():
    from manim import config
    return W / float(config.frame_width)


@pytest.fixture(autouse=True)
def no_viewport():
    """``manim_to_screen`` prefers a published viewport; pin the fallback path."""
    prev = camera_state._viewport
    camera_state._viewport = None
    yield
    camera_state._viewport = prev


def test_fallback_x_scale_matches_manim():
    s = _expected_scale()
    for wx in (-7.0, -3.5, 0.0, 3.5, 7.0):
        sx, _sy = manim_to_screen(wx, 0.0, W, H)
        got = sx - W / 2.0
        assert abs(got - wx * s) < 0.02, (
            "x scale wrong at wx=%.1f: got %.4f px/unit, manim gives %.4f "
            "(%.4f px error)" % (wx, got / wx if wx else float("nan"), s,
                                 abs(got - wx * s)))


def test_fallback_y_scale_matches_manim():
    """y must use the SAME uniform scale as x, not h/8.

    CE's horizontal rules sit at 59.860 for wy=3: 240 - 3*60.046875 = 59.859,
    whereas h/8 would put them at exactly 60.0.
    """
    s = _expected_scale()
    for wy in (-4.0, -1.0, 0.0, 1.0, 4.0):
        _sx, sy = manim_to_screen(0.0, wy, W, H)
        got = H / 2.0 - sy
        assert abs(got - wy * s) < 0.02, (
            "y scale wrong at wy=%.1f: got %.4f, manim gives %.4f"
            % (wy, got, wy * s))


def test_viewport_scale_matches_manim():
    """The live path: MLWindow.sync publishes a viewport every frame, so
    ``Viewport.project`` -- not the fallback -- is what actually renders."""
    from manim import config
    s = _expected_scale()
    vp = camera_state.Viewport(center=(0.0, 0.0),
                               height=float(config.frame_height))
    for wx in (-7.0, -3.0, 0.0, 3.0, 7.0):
        sx, _sy = vp.project(wx, 0.0, W, H)
        assert abs((sx - W / 2.0) - wx * s) < 0.02, (
            "viewport x scale wrong at wx=%.1f: %.4f px/unit expected %.4f"
            % (wx, (sx - W / 2.0) / wx if wx else float("nan"), s))
    for wy in (-4.0, 0.0, 4.0):
        _sx, sy = vp.project(0.0, wy, W, H)
        assert abs((H / 2.0 - sy) - wy * s) < 0.02, (
            "viewport y scale wrong at wy=%.1f: %.4f expected %.4f"
            % (wy, H / 2.0 - sy, wy * s))


def test_scales_agree_at_frame_centre():
    """Both paths must still pin the origin at the surface centre."""
    sx, sy = manim_to_screen(0.0, 0.0, W, H)
    assert abs(sx - W / 2.0) < 1e-6
    assert abs(sy - H / 2.0) < 1e-6


def test_sixteen_nine_render_is_unchanged():
    """At an exact 16:9 size the two formulas coincide, so this fix must not
    move the 1920x1080 renders at all."""
    from manim import config
    w16, h16 = 1920, 1080
    from_pixel_aspect = (w16 * 8.0 / h16)
    assert abs(w16 / float(config.frame_width) - h16 / 8.0) < 1e-9, (
        "16:9 scales diverged (%.9f vs %.9f)" % (w16 / from_pixel_aspect,
                                                 h16 / 8.0))
