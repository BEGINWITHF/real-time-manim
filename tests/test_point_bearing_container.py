"""A container that carries geometry of its OWN must paint that path.

Reported: ``videos_rtm_hq/90_gallery_official/HeatDiagramPlot.mp4`` rendered the
axes, the labels and the four vertex dots -- but no yellow line.  CE draws it.

``Axes.plot_line_graph`` builds the polyline like this::

    graph = VGroup(color=line_color, **kwargs)
    graph.set_points_as_corners(vertices)     # <- the polyline IS the VGroup
    line_graph["line_graph"] = graph          # a VDict of two VGroups

so the line is a point-bearing VGroup with ZERO children (probed: 12 points,
``family_members_with_points() == [itself]``), while the dots live in a second,
point-less VGroup.  ``_send_impl``'s container branch only *dispatches*
``submobjects`` -- ``container_subs`` -- so ``subs`` was empty and the branch
painted nothing at all: one member of the VDict drew, the other silently did
not.

Manim CE keeps every family member that has points, the container included:
``extract_mobject_family_members(..., only_those_with_points=True)`` runs over
``get_family()``, whose first entry is ``self``.  This file pins that rule at
three levels -- the whole ``VDict`` as the scene adds it, the collection pass
that defers a frame's paint into ``_PaintQueue``, and the negative case (a
point-less container must still paint nothing of its own) -- plus the two
coordinates that matter: the path is drawn from its OWN points (never from the
family bbox, see ``test_dot_with_label``) in pure yellow.

Pure Python: a stub DLL records the native calls, no GPU, no ffmpeg.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

try:
    import real_time_manim.vulkan_bind as vb
    from real_time_manim.vulkan_util import manim_to_screen
    from manim import Axes, Dot, VGroup
except Exception as e:                                  # pragma: no cover
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)

W, H = 1920, 1080
PX_TOL = 2.0                       # px; the emitter walks the exact anchors

# The scene's own data (scenes/90_gallery_official.py::HeatDiagramPlot).
X_VALS = [0, 8, 38, 39]
Y_VALS = [20, 0, 0, -5]


class _Recorder(object):
    """Records every DLL call by name; returns 0 like the real stub."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call

    def counts(self):
        out = {}
        for name, _args in self.calls:
            out[name] = out.get(name, 0) + 1
        return out


def _window():
    """An MLWindow that never touches the device (see test_send_containers)."""
    win = vb.MLWindow.__new__(vb.MLWindow)
    win.win_w, win.win_h = W, H
    win.dll = _Recorder()
    return win


def _graph():
    """The scene's ``plot_line_graph`` result, freshly built."""
    # No labels/numbers: the polyline's geometry does not depend on them.
    ax = Axes(x_range=[0, 40, 5], y_range=[-8, 32, 5],
              x_length=9, y_length=6, tips=False)
    return ax.plot_line_graph(x_values=X_VALS, y_values=Y_VALS)


def _path_points(calls):
    """Vertices the fill/stroke path emitted, in screen pixels."""
    pts = []
    for name, args in calls:
        if name == "AddBezierPath":
            flat, n = list(args[0]), int(args[1])
            stride = len(flat) // n if n else 0
            pts += [(float(flat[stride * i]), float(flat[stride * i + 1]))
                    for i in range(n)]
        elif name == "AddLineStrip":
            flat, n = list(args[0]), int(args[2])
            stride = len(flat) // n if n else 0
            pts += [(float(flat[stride * i]), float(flat[stride * i + 1]))
                    for i in range(n)]
    return pts


def _expected_bbox(mob):
    """Screen bbox of the mobject's OWN points -- where CE draws it."""
    xs, ys = [], []
    for p in mob.points:
        sx, sy = manim_to_screen(float(p[0]), float(p[1]), W, H)
        xs.append(sx)
        ys.append(sy)
    return min(xs), max(xs), min(ys), max(ys)


def _bbox(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), max(xs), min(ys), max(ys)


def test_fixture_is_the_reported_shape():
    """The regression needs a point-bearing VGroup with no children."""
    line = _graph()["line_graph"]
    assert line.has_points(), "fixture: the polyline must have points"
    assert not line.submobjects, "fixture: the polyline has no children"
    assert len(line.family_members_with_points()) == 1, (
        "fixture: only the container itself bears points")


def test_line_graph_paints_its_polyline():
    """Red before the fix: `_send(vdict)` emitted the dots and no path."""
    graph = _graph()
    win = _window()
    win._send(graph)
    calls = win.dll.calls
    assert win.dll.counts().get("AddBezierPath", 0) + \
        win.dll.counts().get("AddLineStrip", 0) > 0, (
        "the line graph submitted no path at all: %r" % win.dll.counts())


def test_polyline_is_drawn_from_its_own_points():
    """Not from the family bbox: that delta is (-0.525, +0.75) units here.

    ``_send_impl`` shifts a container's children by
    ``get_center() - points.mean()`` -- a bbox-vs-mean shape statistic, not a
    coordinate difference.  Applying it to the container's own path would put
    the line 71 px left and 101 px up of CE at 1080p.
    """
    graph = _graph()
    line = graph["line_graph"]
    win = _window()
    win._send(graph)

    pts = _path_points(win.dll.calls)
    assert len(pts) >= 2, "no path vertices emitted"
    got = _bbox(pts)
    want = _expected_bbox(line)
    for i, (g, w) in enumerate(zip(got, want)):
        assert abs(g - w) <= PX_TOL, (
            "the polyline's bbox edge %d is at %.1f px, CE draws it at %.1f px "
            "(%.1f px off).  Emitted %d vertices; the path must come from the "
            "container's OWN points, with no family-bbox offset."
            % (i, g, w, abs(g - w), len(pts)))


def test_polyline_is_pure_yellow():
    """The scene's line is `PURE_YELLOW`; it must reach the native path."""
    graph = _graph()
    win = _window()
    win._send(graph)
    stroked = [a for n, a in win.dll.calls
               if n == "AddLineStrip" and int(a[2]) >= 2]
    assert stroked, "the polyline emitted no stroke strip"
    _coords, _n, _count, _sw, r, g, b, _a = stroked[0][:8]
    assert (int(r), int(g), int(b)) == (255, 255, 0), (
        "stroke colour is (%d, %d, %d), expected PURE_YELLOW"
        % (int(r), int(g), int(b)))


def test_vertex_dots_still_paint():
    """Non-regression: the other VDict member is a child VGroup, not own points."""
    graph = _graph()
    win = _window()
    win._send(graph)
    circles = win.dll.counts().get("AddCircle", 0)
    assert circles == 4, "expected the four vertex dots, got %d AddCircle" % circles


def test_collection_pass_defers_then_paints_the_path_once():
    """The queue path must not drop it (it is queued as ONE unit) or paint twice."""
    graph = _graph()
    win = _window()
    queue = vb._PaintQueue(None, {}, False)
    win._paint_queue = queue
    try:
        win._send(graph)
        assert win.dll.calls == [], (
            "collection must not paint: %r" % win.dll.counts())
    finally:
        # sync() closes the queue before flushing it: the deferred units are
        # painted with the collection pass over (see MLWindow.sync).
        win._paint_queue = None
    queue.flush()
    counts = win.dll.counts()
    assert counts.get("AddBezierPath", 0) == 1, (
        "the container's own path painted %d times, expected exactly 1: %r"
        % (counts.get("AddBezierPath", 0), counts))
    assert counts.get("AddCircle", 0) == 4, (
        "the vertex dots did not survive the deferred paint: %r" % counts)


def test_pointless_container_still_paints_nothing_of_its_own():
    """Negative case: the fix must not paint a plain VGroup as a shape."""
    container = VGroup(Dot(), Dot())
    assert not container.has_points()
    win = _window()
    win._send(container)
    counts = win.dll.counts()
    assert counts.get("AddBezierPath", 0) == 0, (
        "a point-less VGroup must not emit a path: %r" % counts)
    assert counts.get("AddCircle", 0) == 2, (
        "its children must still paint: %r" % counts)
