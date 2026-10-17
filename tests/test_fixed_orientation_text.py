"""A fixed-orientation 3D label must be drawn unrotated, anchored on its centre.

Report: wiki ``06-三维/01b-三维基本体进阶``
``01b-三维基本体进阶-arrow3d.mp4`` -- "文字动画错误".

Root cause
----------
``Arrow3DDemo`` pins its tip label with
``self.add_fixed_orientation_mobjects(tip)``.  CE honours that in
``ThreeDCamera.transform_points_pre_display``
(``manim/camera/three_d_camera.py:356-370``)::

    center = center_func()
    return points + (self.project_point(center) - center)

i.e. the glyph points are NEVER rotated -- only translated so their centre
lands where the 3D camera projects that centre.  RTM had no such path:
every point went through ``Viewport.project`` with the camera rotation, so
the label was skewed along with the scene.

Fix
---
``camera_state.fixed_orientation_viewport`` derives the *unrotated* viewport
whose centre makes ``center`` project exactly where the rotated viewport
puts it, and ``window/paint.py::_send_in_fixed_orientation`` swaps it in for
the duration of the send (restoring the frame's viewport afterwards).  The
swap is gated on a viewport that really carries a 3D rotation and on the
camera's own registration table, so every other mobject takes the exact code
path it did before.

Measurement
-----------
Frame 0 of the wiki pair (the first 48 frames are static), label block at
1920x1080, from ``tools/_probe_idx18_project.py`` + the twin videos:

    block                       x span        y span      height
    CE twin (ink)               ~1240..1580   364..408    44 px
    RTM video before the fix    ~1120..1580   352..428    76 px
    CE rule predicted           1222..1556    366..410    44 px
    old projection predicted    1226..1565    351..427    76 px

Each prediction lands within ~2 px of the video that produced it, so the
rule above is the whole difference (mean|diff| 1.005, 458 px off per frame).

Run with::

    python -X utf8 -m pytest tests/test_fixed_orientation_text.py -q
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
import pytest

import real_time_manim  # noqa: F401  -- the bundled manim must win

from manim import Arrow3D, DEGREES, Text, ThreeDScene, UR

from real_time_manim import camera_state
from real_time_manim.camera_state import (fixed_orientation_viewport,
                                          get_viewport, screen_scale,
                                          set_viewport, viewport_from_scene)
from real_time_manim.window.paint import PaintMixin

W, H = 1920, 1080


# --------------------------------------------------------------------------- #
# the exact geometry CE asks for
# --------------------------------------------------------------------------- #

def _tip_scene(theta=-60.0, phi=65.0):
    """The wiki's Arrow3DDemo setup: tip label fixed in orientation.

    Built by hand (no ``construct()`` call): manim only runs that from
    ``render()``, and everything the rule needs -- the registered center
    function and the camera orientation -- is available immediately.
    """
    scene = ThreeDScene()
    arrow = Arrow3D(start=[-2, -1, 0], end=[1.5, 0.5, 1.5])
    tip = Text("tip=(%.1f, %.1f, %.1f)" % tuple(arrow.get_end()),
               font_size=24, color="#aaaaaa").next_to(arrow.get_end(), UR,
                                                       buff=0.2)
    scene.add_fixed_orientation_mobjects(tip)
    scene.set_camera_orientation(phi=phi * DEGREES, theta=theta * DEGREES)
    scene.tip = tip
    return scene


def _family_points(mob):
    return np.vstack([np.asarray(m.points, dtype=float)
                      for m in mob.family_members_with_points() if len(m.points)])


def _ce_rule(viewport, points, center):
    """CE's answer, written straight from ``transform_points_pre_display``.

    The raw points are shifted by ``project_point(center) - center`` and then
    mapped by the plain 2D camera transform ``w/2 + scale * x``.
    """
    scale = screen_scale(W, H, viewport.height)
    pcx, pcy = viewport.project(float(center[0]), float(center[1]), W, H,
                                float(center[2]))
    wx = (pcx - 0.5 * W) / scale            # projected centre, camera units
    wy = (0.5 * H - pcy) / scale
    out = np.empty((len(points), 2), dtype=float)
    out[:, 0] = 0.5 * W + scale * (points[:, 0] + wx - center[0])
    out[:, 1] = 0.5 * H - scale * (points[:, 1] + wy - center[1])
    return out


def _spans(xy):
    return (float(xy[:, 0].min()), float(xy[:, 0].max()),
            float(xy[:, 1].min()), float(xy[:, 1].max()))


def test_fixed_orientation_viewport_reproduces_the_ce_rule():
    """The derived viewport and CE's own formula must agree bit for bit."""
    for theta in (-60, -90, -120, -150):
        scene = _tip_scene(theta=theta)
        vp = viewport_from_scene(scene)
        assert vp is not None and vp.rotation is not None
        tip = scene.tip
        func = vp.fixed_orientation[id(tip)]
        center = np.asarray(func(), dtype=float)
        points = _family_points(tip)

        derived = fixed_orientation_viewport(vp, W, H, center, func)
        assert derived is not None
        assert derived.rotation is None, (
            "the derived viewport must be unrotated -- the glyphs are drawn "
            "at their 2D shape")
        got = np.array([derived.project(float(p[0]), float(p[1]), W, H,
                                        float(p[2])) for p in points])
        want = _ce_rule(vp, points, center)
        err = float(np.abs(got - want).max())
        assert err < 1e-6, (
            "theta=%s: derived viewport differs from CE's rule by %.3g px"
            % (theta, err))
        # and the anchor really is CE's projected centre
        pc = vp.project(float(center[0]), float(center[1]), W, H,
                        float(center[2]))
        anchor = derived.project(float(center[0]), float(center[1]), W, H,
                                 float(center[2]))
        assert abs(anchor[0] - pc[0]) < 1e-6 and abs(anchor[1] - pc[1]) < 1e-6


def test_the_label_block_matches_the_measured_video_spans():
    """Pin the numbers the wiki videos actually show at frame 0.

    CE's twin keeps the label in a 44 px tall horizontal band (ink y 364..408);
    the old rotating projection produced a 76 px tall smear (RTM ink y
    352..428).  The fix must land in CE's band.
    """
    scene = _tip_scene()
    vp = viewport_from_scene(scene)
    tip = scene.tip
    func = vp.fixed_orientation[id(tip)]
    center = np.asarray(func(), dtype=float)
    points = _family_points(tip)

    old = np.array([vp.project(float(p[0]), float(p[1]), W, H, float(p[2]))
                    for p in points])
    derived = fixed_orientation_viewport(vp, W, H, center, func)
    new = np.array([derived.project(float(p[0]), float(p[1]), W, H, float(p[2]))
                    for p in points])

    _ox0, _ox1, oy0, oy1 = _spans(old)
    nx0, nx1, ny0, ny1 = _spans(new)
    old_h, new_h = oy1 - oy0, ny1 - ny0

    assert new_h < 52.0, (
        "the fixed-orientation label block is %.1f px tall; CE's band is 44 px"
        % new_h)
    assert old_h > 65.0, (
        "the un-fixed projection was expected to smear the label to ~76 px, "
        "got %.1f -- the measured premise no longer holds" % old_h)
    # CE's ink sits at y 364..408 (measured on the twin at f0)
    assert 360.0 <= ny0 <= 372.0, ny0
    assert 404.0 <= ny1 <= 416.0, ny1
    assert new_h < old_h * 0.75, (new_h, old_h)
    assert nx1 - nx0 > 300.0, (nx0, nx1)


# --------------------------------------------------------------------------- #
# the sender hook: swap in, draw, restore
# --------------------------------------------------------------------------- #

class _Host(PaintMixin):
    """PaintMixin with a recording stub in place of the real dispatcher."""

    win_w, win_h = W, H

    def __init__(self):
        self.seen = []

    def _send_impl(self, *args, **kwargs):
        self.seen.append(get_viewport())
        return "painted"


def _scene_viewport():
    scene = _tip_scene()
    vp = viewport_from_scene(scene)
    return scene, vp


def test_registered_mobject_is_drawn_on_the_derived_viewport():
    scene, vp = _scene_viewport()
    tip = scene.tip
    func = vp.fixed_orientation[id(tip)]
    center = np.asarray(func(), dtype=float)
    host = _Host()

    saved = get_viewport()
    set_viewport(vp)
    try:
        assert host._send(tip, 0.0) == "painted"
        during = host.seen[0]
        after = get_viewport()
    finally:
        set_viewport(saved)

    assert during is not vp, "the dispatcher never saw a swapped viewport"
    assert during.rotation is None, "the label was still rotated while drawn"
    pc = vp.project(float(center[0]), float(center[1]), W, H, float(center[2]))
    ac = during.project(float(center[0]), float(center[1]), W, H,
                        float(center[2]))
    assert abs(ac[0] - pc[0]) < 1e-6 and abs(ac[1] - pc[1]) < 1e-6, (
        "the derived viewport moved the anchor off the projected centre")
    assert after is vp, "the frame viewport was not restored after the send"


def test_unregistered_and_unrotated_mobjects_keep_the_frame_viewport():
    scene, vp = _scene_viewport()
    other = _tip_scene(theta=-120.0).tip            # registered on ANOTHER scene
    host = _Host()

    saved = get_viewport()
    set_viewport(vp)
    try:
        host._send(other, 0.0)
        assert host.seen[0] is vp, (
            "an mobject the camera did not register must keep the frame")
        # no 3D rotation at all: CE's own rule is the identity, so no swap
        set_viewport(None)
        host.seen = []
        host._send(scene.tip, 0.0)
        assert host.seen[0] is None
    finally:
        set_viewport(saved)


def test_a_family_is_anchored_once_not_per_member():
    """Every member shares ONE center function; re-deriving would compound."""
    scene, vp = _scene_viewport()
    tip = scene.tip
    host = _Host()
    seen = []

    saved = get_viewport()
    set_viewport(vp)
    try:
        # simulate the root's send: swap in, then walk a registered member
        derived = fixed_orientation_viewport(
            vp, W, H, np.asarray(vp.fixed_orientation[id(tip)](), dtype=float),
            vp.fixed_orientation[id(tip)])
        set_viewport(derived)
        host._send(tip.submobjects[0], 0.0)
        seen.append(host.seen[-1])
        assert seen[0] is derived, (
            "a nested family member re-derived the viewport instead of "
            "reusing its root's anchor")
    finally:
        set_viewport(saved)


def test_a_different_anchor_re_derives_from_the_frame():
    """Two fixed-orientation mobjects with different centres must not stack.

    A member anchored by ANOTHER center function, reached while one anchor is
    already active, has to be derived from the FRAME viewport -- reusing the
    outer anchor would drag it to the wrong place.
    """
    from real_time_manim.camera_state import Viewport

    scene, vp = _scene_viewport()
    tip = scene.tip
    other_scene = _tip_scene(theta=-120.0)
    other = other_scene.tip

    table = dict(vp.fixed_orientation or {})
    table[id(other)] = other_scene.camera.fixed_orientation_mobjects[other]
    frame = Viewport(vp.center, vp.height, rotation=vp.rotation,
                     frame_center=vp.frame_center,
                     focal_distance=vp.focal_distance,
                     exponential=vp.exponential,
                     light_source=vp.light_source,
                     fixed_orientation=table)

    host = _Host()
    saved = get_viewport()
    set_viewport(frame)
    try:
        host._send(tip, 0.0)                     # anchor #1 goes active
        outer = host.seen[-1]
        set_viewport(outer)
        host._send(other, 0.0)                   # anchor #2, different centre
        inner = host.seen[-1]
    finally:
        set_viewport(saved)

    assert inner is not outer, (
        "the second mobject reused the first one's anchor")
    assert inner.rotation is None
    for mob, view in ((tip, outer), (other, inner)):
        func = table[id(mob)]
        c = np.asarray(func(), dtype=float)
        want = frame.project(float(c[0]), float(c[1]), W, H, float(c[2]))
        got = view.project(float(c[0]), float(c[1]), W, H, float(c[2]))
        assert abs(got[0] - want[0]) < 1e-6 and abs(got[1] - want[1]) < 1e-6, (
            "anchor of %s drifted: %s vs %s" % (type(mob).__name__, got, want))
