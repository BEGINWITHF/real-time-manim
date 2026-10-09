"""Paint order: RTM must paint in the order Manim CE paints.

CE's rule, from manim 0.20.1 itself:

* ``Camera.get_mobjects_to_display`` flattens every root's family
  (``extract_mobject_family_members(..., use_z_index=True,
  only_those_with_points=True)``) and STABLE-sorts that list by
  ``m.z_index`` -- so ``z_index`` reorders the *whole scene*, not just the
  mobject's own siblings, and a member shared by two roots is painted once,
  at its first occurrence;
* ``ThreeDCamera.get_mobjects_to_display`` then stable-sorts *that* list by
  its camera-space depth, so in 3D the precedence is
  ``(depth, z_index, family pre-order)``;
* ``CairoRenderer.update_frame`` captures ``scene.mobjects`` followed by any
  ``foreground_mobjects`` that are not in it, and ``Scene.add`` re-appends
  ``foreground_mobjects`` last on every add.

RTM used to paint ``scene.mobjects`` top to bottom and ignore ``z_index``
entirely, so every ``Graph`` drew its edges *over* its vertices
(``manim/mobject/graph.py`` hard-codes ``z_index=-1`` on every edge), the
`SetZIndex` example in manim's own docs came out inverted, and a foreground
overlay could end up behind what it was supposed to cover.

The probes in this file drive a real ``MLWindow.sync`` against a stub DLL and
compare the order the leaf senders fire in with CE's own order, computed here
from manim's own functions.

Run with::

    python -X utf8 -m pytest tests/test_paint_order.py -q
"""

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
if os.path.join(REPO, "tools") not in sys.path:
    sys.path.insert(0, os.path.join(REPO, "tools"))

import pytest

try:
    import real_time_manim.vulkan_bind as vb
    from paint_order_probe import (
        _Recorder,
        ce_index,
        ce_order,
        rtm_order,
    )
    from manim import (
        BLUE,
        GREEN,
        RED,
        WHITE,
        Circle,
        Dot,
        Graph,
        Scene,
        Square,
        Text,
        ThreeDScene,
        VGroup,
    )
except Exception as e:                                  # pragma: no cover
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


# --------------------------------------------------------------------------- #
# fixture / helpers
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def window():
    try:
        w = vb.MLWindow(1920, 1080, hidden=True)
    except Exception as e:                              # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield w
    try:
        w.close()
    except Exception:
        pass


def painted(window, scene, three_d=False):
    """The mobjects RTM paints, plus the index CE paints each of them at."""
    expected = ce_order(scene, three_d=three_d)
    index = {}
    for i, mob in enumerate(expected):
        index.setdefault(id(mob), i)
    return rtm_order(window, scene), expected, index


def assert_same_as_ce(window, scene, three_d=False, what=""):
    order, expected, index = painted(window, scene, three_d=three_d)
    last, seen = -1, set()
    for mob in order:
        i = ce_index(mob, index)
        assert i is not None, "%s: RTM painted a mobject CE never would: %r" % (
            what, mob)
        assert i >= last, (
            "%s: RTM painted %r at CE index %d after CE index %d -- CE paints "
            "the flattened family stable-sorted by (depth, z_index, family "
            "order), so the indices can only rise" % (what, mob, i, last))
        last = i
        seen.add(id(mob))
        for sub in getattr(mob, "family_members_with_points", lambda: [])():
            seen.add(id(sub))
    missing = [m for m in expected if id(m) not in seen]
    assert not missing, "%s: never painted by RTM: %r" % (what, missing[:4])


def _shape(kind, color, scale=1.0):
    cls = Square if kind == "square" else Circle
    return cls(fill_color=color, fill_opacity=1, stroke_width=0).scale(scale)


# --------------------------------------------------------------------------- #
# z_index
# --------------------------------------------------------------------------- #

def test_z_index_reorders_across_roots(window):
    """CE's sort is global: z=-1 sinks below roots added before AND after it.

    Red before the fix: the Square painted last (it is added last) instead of
    first, i.e. RTM ignored ``z_index`` and painted the green square on top of
    the circle and the red square.
    """
    scene = Scene()
    red = _shape("square", RED).shift(2.0)
    blue = Circle(radius=1.4, fill_color=BLUE, fill_opacity=1, stroke_width=0)
    sunken = _shape("square", GREEN, 0.6)
    sunken.set_z_index(-1)
    scene.add(red, blue, sunken)
    assert_same_as_ce(window, scene, what="z_index across roots")


def test_graph_edges_painted_before_vertices(window):
    """``Graph`` sets ``z_index=-1`` on every edge (manim graph.py:1057).

    Red before the fix: edges are appended after the vertices, so RTM drew
    every edge across the vertex dots.
    """
    scene = Scene()
    graph = Graph(
        [1, 2, 3, 4],
        [(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)],
        layout="circular",
        vertex_config={"radius": 0.25, "fill_color": "#ffff00"},
        edge_config={"stroke_width": 6, "stroke_color": BLUE},
    )
    scene.add(graph)
    assert_same_as_ce(window, scene, what="Graph")


def test_children_of_one_root_can_disagree(window):
    """One root, children with different z_index (the Graph shape, minimal).

    Red before the fix: RTM walked the VGroup's children in list order, so
    the z=1 Circle painted over the ``other`` root that CE puts between them.
    """
    scene = Scene()
    back = _shape("square", RED, 2.0)
    front = Circle(radius=0.7, fill_color="#ffff00", fill_opacity=1,
                   stroke_width=0)
    front.set_z_index(1)
    scene.add(VGroup(back, front))
    scene.add(_shape("square", BLUE, 0.4))
    assert_same_as_ce(window, scene, what="nested z_index")


def test_no_z_index_keeps_document_order(window):
    """The fast path: a scene that uses no z_index paints as it always did."""
    scene = Scene()
    first = _shape("square", RED, 1.5)
    second = Circle(radius=1.2, fill_color=BLUE, fill_opacity=1,
                    stroke_width=0)
    third = Dot(radius=0.3, color=WHITE)
    scene.add(first, second, third)
    order, _expected, _ = painted(window, scene)
    assert [id(m) for m in order] == [id(m) for m in (first, second, third)]


def test_use_z_index_false_is_honoured(window):
    """``Camera(use_z_index=False)`` switches CE's z sort off too.

    The assertion is on RTM's own order: CE's helper hard-codes the sort, so
    with the flag off CE paints document order -- which is exactly what RTM
    must do here (a b would otherwise swap, because b asks for z=5).
    """
    scene = Scene()
    # a Camera *subclass* would be rasterised instead of drawn as vectors, so
    # flip the flag on the plain camera CE hands the scene
    scene.camera.use_z_index = False
    a = _shape("square", RED, 1.5)
    b = Circle(radius=1.2, fill_color=BLUE, fill_opacity=1, stroke_width=0)
    b.set_z_index(5)
    scene.add(a, b)
    order, _expected, _ = painted(window, scene)
    assert [id(m) for m in order] == [id(m) for m in (a, b)]


def test_set_z_index_doc_example(window):
    """manim's own ``SetZIndex`` example (mobject.py:3346), order for order."""
    from manim import DOWN, UP, MathTex
    scene = Scene()
    text = Text("z_index = 3", color=RED).shift(UP).set_z_index(3)
    square = Square(2, fill_opacity=1).set_z_index(2)
    tex = MathTex(r"zIndex = 1", color=BLUE).shift(DOWN).set_z_index(1)
    circle = Circle(radius=1.7, color=GREEN, fill_opacity=1)
    scene.add(text, square, tex, circle)
    assert_same_as_ce(window, scene, what="SetZIndex example")


# --------------------------------------------------------------------------- #
# family order / list order
# --------------------------------------------------------------------------- #

def test_a_member_shared_by_two_roots_is_painted_once(window):
    """CE keeps the first occurrence; a duplicate root must not vanish.

    Red before the fix: ``extra_skip`` found "other is r" for both entries of
    a duplicated root and dropped it from *both* positions -- nothing painted.
    """
    scene = Scene()
    square = _shape("square", RED, 1.2)
    scene.mobjects = [square, square]
    order, _expected, _ = painted(window, scene)
    assert len(order) == 1 and order[0] is square


def test_foreground_mobject_paints_last(window):
    """CE's render list is ``list_update(mobjects, foreground_mobjects)``."""
    scene = Scene()
    back = _shape("square", RED, 1.5)
    front = Circle(radius=1.2, fill_color=BLUE, fill_opacity=1,
                   stroke_width=0)
    scene.mobjects = [back]
    scene.foreground_mobjects = [front]        # not in scene.mobjects
    order, _expected, _ = painted(window, scene)
    assert [id(m) for m in order] == [id(back), id(front)]


def test_foreground_to_front_restores_ce_order():
    """``Scene.add`` re-appends foreground mobjects on every add."""
    scene = Scene()
    overlay = Circle(radius=1.0)
    late = Square()
    scene.mobjects = [overlay, late]
    scene.foreground_mobjects = [overlay]
    vb.foreground_to_front(scene)
    assert [id(m) for m in scene.mobjects] == [id(late), id(overlay)]


# --------------------------------------------------------------------------- #
# queue mechanics
# --------------------------------------------------------------------------- #

def test_queue_orders_by_depth_then_z_then_family():
    """The key CE actually sorts on (ThreeDCamera over Camera)."""
    q = vb._PaintQueue(None, {})
    painted_now = []
    q.add(float("inf"), lambda: painted_now.append("far"), None)
    q.add(1.0, lambda: painted_now.append("near"), None)
    q.flush()
    assert painted_now == ["near", "far"]      # smaller depth paints first


def test_queue_puts_a_negative_z_before_a_later_root():
    """``z_index`` is the second key, ahead of the family/document position."""
    q = vb._PaintQueue(None, {}, True)          # z_mode: the scene uses z
    painted_now = []
    first = Square()
    second = Square()
    second.z_index = -1
    # recorded in document order: `first` first, `second` second
    q.add(0.0, lambda: painted_now.append("first"), first)
    q.add(0.0, lambda: painted_now.append("second"), second)
    q.flush()
    assert painted_now == ["second", "first"]


def test_inherited_grow_state_survives_a_queued_paint():
    """A lent ``_grow_scale`` must still be there when the paint runs.

    ``_send_impl`` lends the animated VGroup's ``_grow_scale`` to each child
    for the duration of one ``_send`` call, but with a queue open that call
    only *records* the paint -- dropping the attribute right away made every
    queued frame (all of 3D, plus any 2D scene with a ``z_index``) ignore the
    grow and draw the mobject at full size.
    """
    q = vb._PaintQueue(None, {})
    child = Square()
    child._grow_scale = 0.4
    seen = []
    q.add(0.0, lambda: seen.append(getattr(child, "_grow_scale", None)), child)
    vb.release_grow(q, child, True, False)
    assert hasattr(child, "_grow_scale"), "dropped before the paint ran"
    q.flush()
    assert seen == [0.4], "the queued paint did not see the lent grow state"
    assert not hasattr(child, "_grow_scale"), "leaked into the next frame"


def test_release_grow_without_a_queue_drops_immediately():
    child = Square()
    child._grow_scale = 0.4
    vb.release_grow(None, child, True, False)
    assert not hasattr(child, "_grow_scale")
    # a value the mobject owned itself is not the parent's to drop
    child._grow_scale = 0.4
    vb.release_grow(None, child, False, False)
    assert child._grow_scale == 0.4


def test_family_index_keeps_the_first_occurrence():
    first = Square()
    group = VGroup(Circle(), first)
    index = vb.family_index([first, group])
    assert index[id(first)] == 0, "the standalone listing must win"
    assert index[id(group)] == 1
    assert index[id(group.submobjects[0])] == 2


def test_scan_z_index_walks_the_whole_family():
    inner = Square()
    inner.z_index = -1
    outer = VGroup(Circle(), VGroup(inner))
    assert vb.scan_z_index([outer]) is True
    assert vb.scan_z_index([VGroup(Square(), Circle())]) is False


# --------------------------------------------------------------------------- #
# 3D precedence: depth beats z_index (CE stable-sorts depth LAST)
# --------------------------------------------------------------------------- #

def test_three_d_depth_and_z_index(window):
    from manim import IN, OUT
    scene = ThreeDScene()
    near = Circle(radius=1.6, fill_color=RED, fill_opacity=1, stroke_width=0)
    near.set_shade_in_3d(True).shift(2.0 * OUT)
    far = Circle(radius=1.1, fill_color=BLUE, fill_opacity=1, stroke_width=0)
    far.set_shade_in_3d(True).shift(2.0 * IN)
    overlay = Circle(radius=0.5, fill_color=GREEN, fill_opacity=1,
                     stroke_width=0)          # shade_in_3d False -> inf
    scene.add(near, far, overlay)
    assert_same_as_ce(window, scene, three_d=True, what="3D depth + overlay")
