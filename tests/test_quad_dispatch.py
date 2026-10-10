"""A Square/Rectangle with curved points must reach the generic renderer.

Background (measured, `compare_auto --mode scenes` on
`04_mobject_base.MobjectPositioningAndStyling`):

    A_med_min   0.8593 (before 5fe6775)  ->  0.0012 (after 5fe6775)
    severity    4.69                    ->  33.29
    RTM ink     2419 px against CE's 8476 at frame 0

Why: the scene's `ghost` is built as

    ghost = square.copy()          # class Square, 16 straight points
    ghost.become(morph.copy())     # class stays Square, points become a circle

`become` copies the data but not the class, so `ghost` is still a `Square`
while holding 32 bezier points.  `5fe6775` added

    _quad_flat = _edges_are_straight(mob.get_points())
    if isinstance(mob, (Square, Rectangle)) and not is_text and _quad_flat:
        ... _send_polygon ...

whose comment promises that a non-flat one "falls through to the point path,
which tessellates the arcs".  It does not: the next branches are class-based,

    if isinstance(mob, Square):      self._send_square(...)
    elif isinstance(mob, Rectangle): self._send_rectangle(...)

so `_send_square` rebuilt an axis-aligned quad from `side_length` and painted
the wrong shape.  Reverting just the guard recovered A to 0.9020; routing the
curved case to `_send_vmobject` -- what the comment promised -- reached 0.9555,
better than the pre-5fe6775 0.8593.

These tests pin all three halves:

  * a genuinely straight quad still takes the class fast path,
  * a Square that became a circle goes to `_send_vmobject`,
  * a RoundedRectangle (the case 5fe6775 was written for) goes to
    `_send_vmobject` rather than `_send_rectangle`.

Run with::

    python -X utf8 -m pytest tests/test_quad_dispatch.py -q
"""

import inspect

import pytest

from manim import Circle, Rectangle, RoundedRectangle, Square

import real_time_manim.vulkan_bind as vb


# --------------------------------------------------------------------------- #
# fixture / capture
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def renderer():
    try:
        r = vb.MLWindow(854, 480)
    except Exception as e:  # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield r
    try:
        r.close()
    except Exception:
        pass


def dispatch_routes(renderer, mob):
    """Run `_send` and return the set of class-specific branches it took.

    Every branch whose name starts with ``_send_`` and takes ``mob`` as its
    first parameter is stubbed out, so nothing actually touches the DLL and
    the test only observes *which* branch ran.
    """
    tried = []
    stubs = {}

    def _make(name):
        def _stub(*a, **k):
            tried.append(name)
            return None
        return _stub

    for name in dir(renderer):
        if not name.startswith("_send_") or name.startswith("_send_stack"):
            continue
        if name in ("_send_impl", "_send_image"):
            continue
        fn = getattr(renderer, name)
        if not callable(fn):
            continue
        try:
            params = list(inspect.signature(fn).parameters)
        except (TypeError, ValueError):  # pragma: no cover
            continue
        if not params or params[0] != "mob":
            continue
        stubs[name] = fn
        setattr(renderer, name, _make(name))

    try:
        renderer._send(mob)
    finally:
        for name, fn in stubs.items():
            setattr(renderer, name, fn)
    return tried


def curved_square():
    """The scene's `ghost`: class Square, but the points of a circle."""
    square = Square(side_length=2)
    ghost = square.copy()
    ghost.become(Circle(radius=0.8))
    return ghost


# --------------------------------------------------------------------------- #
# tests
# --------------------------------------------------------------------------- #

def test_curved_square_keeps_its_class(renderer):
    """Precondition of the whole bug: become() swaps data, not the class."""
    ghost = curved_square()
    assert isinstance(ghost, Square), (
        "manim changed become(); the class/geometry split this test relies on "
        "no longer holds (got %s)" % type(ghost).__name__)
    assert len(ghost.get_points()) != 16, (
        "the ghost no longer carries circle geometry")
    assert vb.MLWindow._edges_are_straight(ghost.get_points()) is False, (
        "the ghost's points are straight, so it would legitimately take the "
        "quad path and this test would prove nothing")


def test_straight_square_still_takes_the_polygon_path(renderer):
    """Control: the flat-quad fast path must stay in use.

    `_send_impl` sends a flat Square/Rectangle through `_send_polygon` and
    returns at the `drawn:` block, so `_send_square` is not involved at all
    here -- that is the path this fix must not disturb.
    """
    tried = dispatch_routes(renderer, Square(side_length=2))
    assert "_send_polygon" in tried, (
        "a plain Square no longer reaches the polygon fast path "
        "(routes: %s)" % tried)
    assert "_send_vmobject" not in tried, (
        "a plain Square is being rendered through the generic bezier path, "
        "which is slower and was not intended (routes: %s)" % tried)


def test_square_that_became_a_circle_reaches_generic_renderer(renderer):
    """The MobjectPositioningAndStyling regression, pinned.

    Red before the fix: `_send_square` is called (routes == ['_send_square']).
    Green after:        `_send_vmobject` is called instead.
    """
    ghost = curved_square()
    tried = dispatch_routes(renderer, ghost)
    assert "_send_polygon" not in tried, (
        "a curved Square still went through the flat-quad block "
        "(routes: %s)" % tried)
    assert "_send_square" not in tried, (
        "a Square holding circle geometry was handed to _send_square, which "
        "rebuilds an axis-aligned quad from side_length -- this is the "
        "dispatch bug that collapsed MobjectPositioningAndStyling's A_med "
        "from 0.8593 to 0.0012")
    assert "_send_vmobject" in tried, (
        "the curved Square reached no renderer at all (routes: %s)" % tried)


def test_rounded_rectangle_reaches_generic_renderer(renderer):
    """The case 5fe6775 was written for must tessellate, not chamfer.

    Drawing chords between a RoundedRectangle's arc anchors chamfers every
    corner (a bright 45-degree cut across it); drawing it with
    `_send_rectangle` collapses it to an axis-aligned width/height quad.
    """
    rounded = RoundedRectangle(width=3.0, height=2.0, corner_radius=0.3)
    assert vb.MLWindow._edges_are_straight(rounded.get_points()) is False

    tried = dispatch_routes(renderer, rounded)
    assert "_send_rectangle" not in tried, (
        "a RoundedRectangle was rebuilt as an axis-aligned rectangle "
        "(routes: %s)" % tried)
    assert "_send_vmobject" in tried, (
        "a RoundedRectangle must be tessellated by the generic renderer, or "
        "its corners are chamfered (routes: %s)" % tried)


def test_straight_rectangle_still_takes_the_polygon_path(renderer):
    """Control: the rectangle fast path is untouched by the fix."""
    tried = dispatch_routes(renderer, Rectangle(width=3, height=2))
    assert "_send_polygon" in tried, (
        "a plain Rectangle no longer reaches the polygon fast path "
        "(routes: %s)" % tried)
    assert "_send_vmobject" not in tried, (
        "a plain Rectangle is going through the generic renderer "
        "(routes: %s)" % tried)
