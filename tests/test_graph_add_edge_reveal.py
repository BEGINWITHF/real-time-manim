"""A Graph edge added by ``add_edges`` must be REVEALED, never snapped on.

Report: wiki ``07-图论与向量场/01b-图的增删与布局``
``01b-图的增删与布局-add.mp4`` -- "四号点发生错误位移".

Root cause (measured, then fixed in the animation pipeline)
----------------------------------------------------------
``g.animate.add_edges((1, 4), positions=...)`` builds, through manim's
``_AnimationBuilder`` override path, an
``AnimationGroup(Create(LabeledDot), Create(Line), lag_ratio=0)``.  The two
children are manim's own ``Create``, which CUTS the geometry every frame
(``pointwise_become_partial``) and which RTM's hook tags
``_vulkan_points_partial`` -- so the sender must draw the cut path it is
handed and nothing more (``point_path_bounds`` then returns ``(0, 1)``).

In the video the pipeline did not do that: the new edge was submitted
FULL LENGTH on the animation's very first frame (``f84``) and stayed full
while vertex 4's disc was still growing, so the edge pointed at empty
space -- "四号点发生错误位移".  Measured with
``tools/_probe_idx20_edge.py`` (40 samples along the free stretch of the
segment, '#' = ink):

    f84  RTM ..#.####################################   CE .......................................#
    f98  RTM ########...............................   CE ########...............................#
    f114 RTM ########################################   CE ########################################

and with ``tools/_probe_idx20_timeline.py`` (first frame with ink):

    element                 RTM before   CE    RTM after
    vertex 4 dot (v4)            84      90       90
    edge (4,5) (e45)            168     182      182

The window files that own that pipeline (``window/play.py``,
``render/hooks.py``, ``render/hook_channels.py``) were reworked after the
baseline video was rendered (video mtime 2026-10-15 14:00, those files
2026-10-16 13:30-14:19); a re-render of the page now matches CE frame for
frame on both counters and mean|diff| went 0.867 -> 0.842 (the residue is
the page's label text, a different report).

What this test pins
-------------------
The mechanism the render depends on, so a regression in any of it fails
here without a GPU or a window:

* the child ``Create`` really cuts the edge (``get_end()`` walks from
  vertex 1 to vertex 4 as alpha grows, and sits on vertex 1 at alpha 0);
* the hook tags the path and ``point_path_bounds`` hands the sender
  ``(0, 1)`` -- i.e. the sender draws the cut geometry and does NOT window
  it a second time;
* the geometry ``_send_line`` submits is that cut edge: it grows
  monotonically and never reaches full length before the animation ends.

Run with::

    python -X utf8 -m pytest tests/test_graph_add_edge_reveal.py -q
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
import pytest

import real_time_manim  # noqa: F401  -- the bundled manim must win

from manim import BLACK, Graph

from real_time_manim import camera_state
from real_time_manim.render.hooks import clear_hooks, install_hooks
from real_time_manim.render.shapes import ShapeMixin
from real_time_manim.render.util import point_path_bounds

V4 = np.array([3.2, 1.2, 0.0])
ALPHAS = (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0)


class _Recorder(object):
    """Stands in for the native DLL and keeps every submitted call."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


class _Sender(ShapeMixin):
    """A ShapeMixin host with no window behind it (pure geometry)."""

    win_w, win_h = 1920, 1080

    def __init__(self):
        self.dll = _Recorder()

    @staticmethod
    def _dbg_emit(*args, **kwargs):                     # pragma: no cover
        pass


@pytest.fixture(autouse=True)
def _flat_camera():
    prev = camera_state.get_viewport()
    camera_state.set_viewport(None)
    yield
    camera_state.set_viewport(prev)


def _edge_animation():
    """The wiki sample's ``g.animate.add_edges((1, 4), ...)`` as RTM plays it."""
    g = Graph([1, 2, 3], [(1, 2), (2, 3)], layout="circular", layout_scale=2.0,
              labels=True, label_fill_color=BLACK)
    anim = g.animate.add_edges((1, 4), positions={4: [3.2, 1.2, 0]},
                               labels=True).build()
    subs = list(getattr(anim, "animations", []) or [])
    assert len(subs) == 2, [type(s).__name__ for s in subs]
    edge = next(s.mobject for s in subs
                if abs(np.asarray(s.mobject.get_end())[0]
                       - np.asarray(s.mobject.get_start())[0]) > 0.1)
    return anim, edge


def _drawn_fraction(edge):
    """0..1 of the edge that exists, measured along vertex1 -> vertex4."""
    start = np.asarray(edge.get_start(), dtype=float)
    end = np.asarray(edge.get_end(), dtype=float)
    full = V4 - start
    t = float(np.dot(end - start, full) / np.dot(full, full))
    return t


def test_the_child_create_cuts_the_edge_geometry():
    """manim's Create must trim the Line every frame -- the reveal itself."""
    anim, edge = _edge_animation()
    install_hooks(anim)
    try:
        anim.begin()
        fractions = []
        for a in ALPHAS:
            anim.interpolate(a)
            fractions.append(_drawn_fraction(edge))
    finally:
        clear_hooks(anim)

    assert fractions[0] == pytest.approx(0.0, abs=1e-9), (
        "at alpha 0 the edge already spans %s of its length -- the animation "
        "would pop on fully drawn" % fractions[0])
    assert fractions[-1] == pytest.approx(1.0, abs=1e-6), fractions
    assert all(b - 1e-9 <= c for b, c in zip(fractions, fractions[1:])), (
        "the reveal is not monotonic: %s" % fractions)
    for a, f in zip(ALPHAS[1:-1], fractions[1:-1]):
        assert f < 1.0, (
            "alpha %.2f already draws the whole edge (%.3f) -- that is the "
            "'四号点发生错误位移' snap-on" % (a, f))


def test_the_path_is_tagged_and_windowed_only_by_the_cut():
    """``point_path_bounds`` must be (0, 1): the points ARE the drawn prefix."""
    anim, edge = _edge_animation()
    install_hooks(anim)
    try:
        anim.begin()
        anim.interpolate(0.5)
        assert getattr(edge, "_vulkan_points_partial", False) is True, (
            "the hook did not tag the cut path; the sender would then window "
            "the already-cut geometry a second time")
        assert point_path_bounds(edge) == (0.0, 1.0), point_path_bounds(edge)
        # ... and the channel still records the animation's own progress
        assert 0.0 < float(getattr(edge, "_vulkan_progress", -1.0)) < 1.0
    finally:
        clear_hooks(anim)


def test_the_submitted_edge_grows_and_never_snaps_on():
    """End to end through `_send_line`: what native receives, frame by frame."""
    sender = _Sender()
    anim, edge = _edge_animation()
    install_hooks(anim)
    try:
        anim.begin()
        lengths = []
        for a in ALPHAS:
            anim.interpolate(a)
            sender.dll.calls = []
            sender._send_line(edge, 1.0, 1920, 1080, 0.0, None)
            segs = [c for c in sender.dll.calls if c[0] in ("AddLine", "AddLineStrip")]
            if not segs:
                lengths.append(0.0)
                continue
            if a == 0.0:
                # a degenerate submit is fine (zero length), anything visible
                # is not
                pass
            coords = np.asarray(segs[0][1][0], dtype=float)
            if segs[0][0] == "AddLine":
                p0 = (float(segs[0][1][0]), float(segs[0][1][1]))
                p1 = (float(segs[0][1][2]), float(segs[0][1][3]))
                length = float(np.hypot(p1[0] - p0[0], p1[1] - p0[1]))
            else:
                n = int(segs[0][1][2])
                pts = coords[: n * 2].reshape(-1, 2)
                length = float(np.hypot(*(pts[-1] - pts[0]))) if n >= 2 else 0.0
            lengths.append(length)
    finally:
        clear_hooks(anim)

    full = None
    # the fully drawn edge, in pixels, at this window size
    sender2 = _Sender()
    anim2, edge2 = _edge_animation()
    anim2.begin()
    anim2.interpolate(1.0)
    sender2.dll.calls = []
    sender2._send_line(edge2, 1.0, 1920, 1080, 0.0, None)
    for name, args in sender2.dll.calls:
        if name == "AddLine":
            full = float(np.hypot(args[2] - args[0], args[3] - args[1]))
            break
        if name == "AddLineStrip":
            n = int(args[2])
            pts = np.asarray(args[0], dtype=float)[: n * 2].reshape(-1, 2)
            full = float(np.hypot(*(pts[-1] - pts[0])))
            break
    assert full and full > 100.0, full

    for a, length in zip(ALPHAS, lengths):
        assert length <= full * 1.02, (
            "alpha %.2f: submitted edge %.1f px > full length %.1f px"
            % (a, length, full))
    assert lengths[0] < full * 0.05, (
        "the first frame already submits %.1f px of a %.1f px edge -- the new "
        "edge snaps on full length instead of being drawn" % (lengths[0], full))
    assert all(b - 1.0 <= c for b, c in zip(lengths, lengths[1:])), (
        "the drawn edge shrank between frames: %s" % lengths)
    assert lengths[-1] == pytest.approx(full, rel=0.02), (lengths[-1], full)
