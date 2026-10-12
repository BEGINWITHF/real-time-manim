"""A `Dot` that carries a submobject must still draw at its own circle.

Reported: ``videos_rtm_hq/05_mobject_classes/VectorizedContainers.mp4`` -- the
yellow dot sits in the wrong place (它压在 "dot" 标签上, to the LEFT of where
CE puts it).

Mechanism, measured on the two renders at 1080p (yellow blob bounding box):

    CE    cx 517.5  cy 485.5  44 x 44 px
    RTM   cx 456.7  cy 484.6  47 x 46 px     <- 61 px left, 7 % fat

Why: the scene builds ``VDict({...}, show_keys=True)``, and manim's
``VDict.add_key_value_pair`` appends the key label to the VALUE --
``mob.add(key_text)`` -- so ``registry["dot"]`` is a ``Dot`` with a
``Tex("dot")`` submobject.  ``_send_dot`` took both its centre and its radius
from the family-wide bbox:

    get_center()                 = (-3.736, 0.4)   includes the label
    circle's own points centre   = (-3.274, 0.4)   <- CE draws here
    min(width, height) / 2       = 0.1756          label height 0.351 / 2
    true radius                  = 0.16

so the disc was dragged 0.462 units (62 px) towards the label and drawn 10 %
fat.  A Dot's bezier control points sit exactly on the circle, so its OWN
point box is both the drawn centre and the drawn radius.

This file pins that rule: a labelled Dot emits CE's centre and CE's radius, an
unlabelled one is unchanged, and a point-less mobject (Text -- what a FocusOn
target usually is) still falls back to the family bbox.  Pure Python, no
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
    from manim import BLUE, LEFT, UP, YELLOW, Dot, RoundedRectangle, VDict
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)

W, H = 1920, 1080
PX_PER_UNIT = H / 8.0           # 135 px per manim unit at the default frame
TOL = 0.05                      # px; a rasteriser may quantise, 62 px may not


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
    prev = camera_state._viewport
    yield
    camera_state._viewport = prev


@pytest.fixture
def labelled_dot():
    """Exactly the entry VectorizedContainers renders."""
    registry = VDict(
        {
            "frame": RoundedRectangle(width=3.0, height=2.0, corner_radius=0.3,
                                      color=BLUE),
            "dot": Dot(radius=0.16, color=YELLOW),
        },
        show_keys=True,
    )
    registry.move_to(4.0 * LEFT + 0.4 * UP)
    return registry["dot"]


def emitted_circle(renderer, mob):
    """(x, y, radius) handed to native's AddCircle, or None if it never ran."""
    orig = renderer.dll.AddCircle
    rec = []

    def _cap(*a):
        rec.append((float(a[0]), float(a[1]), float(a[2])))
        return 0

    renderer.dll.AddCircle = _cap
    try:
        renderer._send_dot(mob, 1.0, W, H)
    finally:
        renderer.dll.AddCircle = orig
    return rec[0] if rec else None


def own_points_box(mob):
    """CE's ground truth: the bbox of the mobject's OWN points."""
    pts = mob.points
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    return (lo + hi) / 2.0, float(min(hi[0] - lo[0], hi[1] - lo[1])) / 2.0


def to_screen(p):
    manim_x, manim_y = p[0], p[1]
    return (W / 2.0 + manim_x * PX_PER_UNIT, H / 2.0 - manim_y * PX_PER_UNIT)


def test_labelled_dot_centre_ignores_the_label(renderer, viewport, labelled_dot):
    """The reported bug: the disc must not be dragged towards its key label."""
    camera_state._viewport = None
    mob = labelled_dot
    centre, _rad = own_points_box(mob)

    # the label is really there, and really does move the family centre
    assert len(mob.submobjects) == 1, "VDict(show_keys=True) lost the key label"
    assert mob.get_center()[0] < centre[0] - 0.1, (
        "fixture stopped reproducing: the family centre should sit left of the "
        "circle (label is added to the LEFT)")

    got = emitted_circle(renderer, mob)
    assert got is not None, "_send_dot emitted no AddCircle"
    want_x, want_y = to_screen(centre)
    assert got[0] == pytest.approx(want_x, abs=TOL), (
        "labelled Dot drawn at x=%.1f px, CE draws it at %.1f px (a %.1f px / "
        "%.2f unit error). get_center() includes the Tex key label that "
        "VDict.show_keys adds as a SUBMOBJECT; the disc is drawn from the "
        "circle's own points." % (got[0], want_x, got[0] - want_x,
                                  (got[0] - want_x) / PX_PER_UNIT))
    assert got[1] == pytest.approx(want_y, abs=TOL), (
        "labelled Dot drawn at y=%.1f px, CE draws it at %.1f px"
        % (got[1], want_y))


def test_labelled_dot_radius_is_the_circle_not_the_label(renderer, viewport,
                                                         labelled_dot):
    """min(width, height) measures the label's height: 10 % fat."""
    camera_state._viewport = None
    mob = labelled_dot
    _centre, rad = own_points_box(mob)

    got = emitted_circle(renderer, mob)
    assert got is not None
    assert got[2] == pytest.approx(rad * PX_PER_UNIT, abs=TOL), (
        "labelled Dot radius %.2f px, CE's is %.2f px (manim radius %.4f). "
        "min(width, height)/2 measures the LABEL (height %.4f), not the circle "
        "(%.4f)." % (got[2], rad * PX_PER_UNIT, rad, mob.height, 2 * rad))


def test_unlabelled_dot_is_unchanged(renderer, viewport):
    """The plain case must not move: own points and family bbox agree."""
    camera_state._viewport = None
    dot = Dot(radius=0.16, color=YELLOW)
    got = emitted_circle(renderer, dot)
    assert got is not None
    want_x, want_y = to_screen(dot.get_center())
    assert got[0] == pytest.approx(want_x, abs=TOL)
    assert got[1] == pytest.approx(want_y, abs=TOL)
    assert got[2] == pytest.approx(0.16 * PX_PER_UNIT, abs=TOL)


def test_scaled_labelled_dot_tracks_its_points(renderer, viewport, labelled_dot):
    """A transform moves the points; the disc must follow them."""
    camera_state._viewport = None
    mob = labelled_dot
    mob.scale(2.0)
    centre, rad = own_points_box(mob)
    got = emitted_circle(renderer, mob)
    want_x, want_y = to_screen(centre)
    assert got[0] == pytest.approx(want_x, abs=TOL)
    assert got[1] == pytest.approx(want_y, abs=TOL)
    assert got[2] == pytest.approx(rad * PX_PER_UNIT, abs=TOL)


def test_pointless_mobject_falls_back_to_the_family_bbox(renderer, viewport):
    """FocusOn tags its target `_focus_on_dot`; that target is often a Text,
    which carries no points of its own (the glyphs are submobjects)."""
    camera_state._viewport = None
    from manim import Text
    t = Text("target")
    assert len(t.points) == 0, "fixture: Text is expected to have no own points"
    got = emitted_circle(renderer, t)
    assert got is not None, "a point-less target must still fall back, not vanish"
    want_x, want_y = to_screen(t.get_center())
    assert got[0] == pytest.approx(want_x, abs=TOL)
    assert got[1] == pytest.approx(want_y, abs=TOL)
    assert got[2] == pytest.approx(min(t.width, t.height) / 2.0 * PX_PER_UNIT,
                                   abs=TOL)


def test_own_point_box_helper_is_the_circle_geometry(labelled_dot):
    """Mechanism pin for the helper, with no window needed."""
    from real_time_manim.vulkan_shapes import ShapeMixin
    mob = labelled_dot
    own = ShapeMixin._dot_own_points_box(None, mob)
    centre, rad = own_points_box(mob)
    assert own is not None
    assert list(own[0]) == pytest.approx(list(centre))
    assert own[1] == pytest.approx(rad)

    assert ShapeMixin._dot_own_points_box(None, Dot()) is not None
    from manim import Text
    assert ShapeMixin._dot_own_points_box(None, Text("x")) is None
