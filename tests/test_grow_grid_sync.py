"""A grown ``Rectangle`` must draw its border and its grid at ONE size.

``08_geometry.PolygramFamily`` plays ``GrowFromCenter`` over a ``Rectangle``
built with ``grid_xstep``/``grid_ystep``.  manim's grows are Transforms: their
``interpolate`` has already scaled every point of the family by
``smooth(alpha)`` about the grow point, and CE draws exactly those points.

RTM's ``_write_grow`` additionally stamped ``_grow_scale = alpha`` on the
animated mobject.  ``_send_polygon`` (the border) re-applies that channel to
the vertices it reads off the points, so the border came out at
``alpha * smooth(alpha)`` while the grid lines -- drawn from the same scaled
points by ``_send_line``, and carrying no channel of their own -- stayed at
``smooth(alpha)``.  Measured on the rendered scene: at t=0.8 s the border was
144 px wide where CE has 212, while the grid measured 212 in both.

The probes in this file drive a real ``MLWindow`` against a stub DLL and
compare the geometry that is actually submitted, tagged with the sender that
submitted it: the border's extents and the grid's line lengths have to agree
at every point of the grow.

Run with::

    python -X utf8 -m pytest tests/test_grow_grid_sync.py -q
"""

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

try:
    import real_time_manim.vulkan_bind as vb
    from manim import (GrowFromCenter, Polygon, Rectangle, Scene, Square,
                       VGroup)
    from real_time_manim.render_hooks import install_hooks
except Exception as e:                                  # pragma: no cover
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


# --------------------------------------------------------------------------- #
# fixture / helpers
# --------------------------------------------------------------------------- #

class _Recorder(object):
    """Stands in for the native DLL and keeps every submitted call.

    ``sender`` names the leaf sender that is running, so a border stroke
    (``_send_polygon``) can be told apart from a grid line (``_send_line``)
    even though both end up in the same ``AddLine``.
    """

    def __init__(self):
        self.calls = []
        self.sender = None

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((self.sender, name, args))
            return 0
        return _call


# Every branch of `_send_impl` that emits geometry (same list as
# tools/paint_order_probe.py).
LEAF_SENDERS = (
    "_send_vmobject", "_send_polygon", "_send_square", "_send_rectangle",
    "_send_ellipse", "_send_dot", "_send_circle", "_send_arrow",
    "_send_dashed_line", "_send_line", "_send_arc", "_send_point",
    "_send_point_cloud", "_send_text_write",
)


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


def submitted(window, mobject):
    """Sync a one-mobject scene against a stub DLL; return the tagged calls."""
    scene = Scene()
    scene.add(mobject)
    rec = _Recorder()
    real_dll = window.dll
    window.dll = rec
    wrapped = []
    for name in LEAF_SENDERS:
        fn = getattr(window, name, None)
        if not callable(fn):
            continue

        def make(fn, name):
            def wrapper(*args, **kwargs):
                prev = rec.sender
                rec.sender = name
                try:
                    return fn(*args, **kwargs)
                finally:
                    rec.sender = prev
            return wrapper

        setattr(window, name, make(fn, name))
        wrapped.append(name)
    try:
        window.sync(scene)
    finally:
        window.dll = real_dll
        for name in wrapped:
            try:
                delattr(window, name)
            except AttributeError:
                pass
    return rec.calls


def _pairs(arr, n):
    vals = list(arr)[: 2 * int(n)]
    return vals[0::2], vals[1::2]


def extents(calls, sender):
    """(width, height) in px of everything ``sender`` submitted.

    ``_send_polygon`` strokes its border as ``AddLine``/``AddLineStrip`` and
    fills it as ``AddPolygon``; ``_send_line`` submits one ``AddLine`` per
    grid line.
    """
    xs, ys = [], []
    for who, name, args in calls:
        if who != sender:
            continue
        if name == "AddLine":
            xs.extend([float(args[0]), float(args[2])])
            ys.extend([float(args[1]), float(args[3])])
        elif name == "AddLineStrip":
            px, py = _pairs(args[0], args[2])
            xs.extend(px)
            ys.extend(py)
        elif name == "AddPolygon":
            px, py = _pairs(args[10], args[9])
            xs.extend(px)
            ys.extend(py)
    assert xs, "the %s sender submitted no geometry" % sender
    return max(xs) - min(xs), max(ys) - min(ys)


def border_extents(calls):
    return extents(calls, "_send_polygon")


def grid_extents(calls):
    """The grid of a ``Rectangle`` is vertical + horizontal ``Line`` children."""
    return extents(calls, "_send_line")


def grided_rect(**kwargs):
    """The figure PolygramFamily grows: a Rectangle with a grid inside it."""
    params = dict(width=1.8, height=1.1, grid_xstep=0.45, grid_ystep=0.55,
                  stroke_width=2)
    params.update(kwargs)
    return Rectangle(**params)


def grown(mobject, alpha):
    """Run manim's own grow over ``mobject`` up to ``alpha``."""
    anim = GrowFromCenter(mobject, run_time=1.0)
    anim.begin()
    install_hooks(anim)
    anim.interpolate(alpha)
    return mobject


def point_extent(mobject, axis=0):
    pts = mobject.points
    return float(pts[:, axis].max() - pts[:, axis].min())


# --------------------------------------------------------------------------- #
# the reported bug: the border against the grid inside it
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("alpha", [0.05, 0.25, 0.5, 0.75, 0.95, 1.0])
def test_border_and_grid_grow_as_one(window, alpha):
    """The border and the grid lines it encloses must be the same size.

    That is what CE draws: one family, one set of scaled points.  A mismatch
    here is the PolygramFamily bug -- grid lines running outside (or short of)
    their own border for the whole 0.35 s grow.
    """
    bw, bh = border_extents(submitted(window, grown(grided_rect(), alpha)))
    gw, gh = grid_extents(submitted(window, grown(grided_rect(), alpha)))

    assert abs(gw - bw) <= 2.0, (
        "alpha %.2f: the border is %.1f px wide but the grid it encloses is "
        "%.1f px -- one of the two is scaled a second time"
        % (alpha, bw, gw))
    assert abs(gh - bh) <= 2.0, (
        "alpha %.2f: the border is %.1f px tall but the grid it encloses is "
        "%.1f px" % (alpha, bh, gh))

    # Part-way through, or the two bugs would cancel (both at full size) and
    # the assertions above would pass vacuously.
    if alpha < 1.0:
        full_w, _ = border_extents(submitted(window, grided_rect()))
        assert bw < full_w, "alpha %.2f: nothing shrank at all" % alpha


# --------------------------------------------------------------------------- #
# the same double scale, on shapes with no children
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("alpha", [0.25, 0.5, 0.75])
@pytest.mark.parametrize("factory", [
    lambda: Square(stroke_width=2),
    lambda: Polygon([-1, -0.5, 0], [1, -0.5, 0], [1, 0.5, 0], [-1, 0.5, 0],
                    stroke_width=2),
    lambda: grided_rect(),
], ids=["square", "polygon", "rectangle"])
def test_border_follows_the_points(window, alpha, factory):
    """The border must sit where manim's own scaled points put it.

    Calibrated against the same shape at full size, so the screen scale is
    measured rather than assumed.  Before the fix the border was at
    ``alpha * smooth(alpha)`` of CE's size instead of ``smooth(alpha)``.
    """
    grown_obj, full_obj = factory(), factory()
    bw, _ = border_extents(submitted(window, grown(grown_obj, alpha)))
    full_w, _ = border_extents(submitted(window, full_obj))
    expect = full_w * point_extent(grown_obj) / point_extent(full_obj)
    assert abs(bw - expect) <= 2.0, (
        "%s at alpha %.2f: border %.1f px, manim's own points give %.1f px"
        % (type(grown_obj).__name__, alpha, bw, expect))


# --------------------------------------------------------------------------- #
# the loan is still needed for the animations that carry a channel only
# --------------------------------------------------------------------------- #

def test_channel_only_grow_scales_the_children(window):
    """``Flash``/``Circumscribe``/RTM's own grows stamp the channel, not the points.

    manim's grows need no loan (they scale the points), but a channel-only
    animation still has to carry its children: a ``Rectangle`` whose border is
    scaled by ``_grow_scale`` must not keep its grid lines at full size.
    """
    rect = grided_rect()
    full_w, full_h = border_extents(submitted(window, grided_rect()))

    rect._grow_scale = 0.5
    rect._grow_point = tuple(rect.get_center())
    calls = submitted(window, rect)
    bw, bh = border_extents(calls)
    gw, gh = grid_extents(calls)
    assert abs(bw - full_w / 2.0) <= 2.0, "the border ignored the channel"
    assert abs(bh - full_h / 2.0) <= 2.0, "the border ignored the channel"
    assert abs(gw - bw) <= 2.0, (
        "channel grow: the border is %.1f px wide, the grid %.1f px"
        % (bw, gw))
    assert abs(gh - bh) <= 2.0, (
        "channel grow: the border is %.1f px tall, the grid %.1f px"
        % (bh, gh))


def test_vgroup_grow_still_reaches_every_member(window):
    """The pre-existing loan (a VGroup has no points of its own) must keep working."""
    def group():
        return VGroup(Square(side_length=1.0, stroke_width=2),
                      Square(side_length=1.0, stroke_width=2).shift([2, 0, 0]))

    full_w, _ = border_extents(submitted(window, group()))
    grown_group = group()
    grown_group._grow_scale = 0.5
    grown_group._grow_point = tuple(grown_group.get_center())
    bw, _ = border_extents(submitted(window, grown_group))
    assert abs(bw - full_w / 2.0) <= 2.0, (
        "a VGroup's grow did not reach its members: %.1f px against %.1f"
        % (bw, full_w / 2.0))
