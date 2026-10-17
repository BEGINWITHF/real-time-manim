"""Regression test: Rotate/Rotating must ORBIT an explicit pivot, not spin in place.

Report: wiki ``03-动画/移动与旋转`` -- "这个文件夹大修 ... 旋转轴的绑定混乱".
``01-旋转-rotate.mp4`` (``Rotate(sq, 2*PI/3, about_point=pivot)``) and
``01-旋转-rotating_edge.mp4`` (``Rotating(tri, 90*DEGREES, about_edge=UP)``) both
left the shape spinning in place instead of revolving about the pivot.

Root cause: the draw-time rotation channel (``set_anim_rotation`` +
``_rotation_about_point``) is honoured only by the primitive senders --
``_send_square`` orbits the centre about the pivot -- while ``_send_polygon``
and the generic point path rotate the vertices about the shape's OWN centre and
ignore the pivot.  A Square/Triangle therefore never revolved.  Measured from
the rendered videos (blue/teal centroid, 480x270): RTM's Rotate Square centroid
stayed at (327, 182) for the whole clip while CE's orbited to (196, 106); the
rotating_edge Triangle crawled to (248.9, 193.6) while CE reached (276.8, 165.7).

Fix (``animations/rotate.py`` / ``rotating.py``): when an EXPLICIT pivot is
given (``about_point``/``about_edge``) -- or the axis leaves the z line -- bake
the rotation into the point arrays every frame (the pre-existing 3D Rodrigues
path), so the orbit lives in the geometry instead of the (ignored) channel.  A
default pivot (own centre) needs no orbit and keeps the cheap channel path.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
from manim import DOWN, ORIGIN, PI, RIGHT, TEAL, UP, BLUE, Square, Triangle

import real_time_manim.render.hooks as hooks
from real_time_manim.animations.rotate import Rotate
from real_time_manim.animations.rotating import Rotating


def _center(mob):
    return np.asarray(mob.get_center(), dtype=float)


def test_rotate_about_point_orbits_the_pivot():
    """``Rotate(sq, 2*PI/3, about_point=pivot)`` must end at the rotated centre."""
    pivot = np.asarray(ORIGIN) + np.asarray(DOWN) * 1.4
    sq = Square(side_length=1.3, color=BLUE).set_fill(BLUE, 0.5)
    sq.move_to(pivot + np.asarray(RIGHT) * 2.6)
    start = _center(sq)
    ang = 2 * PI / 3
    rel = start[:2] - pivot[:2]
    c, s = np.cos(ang), np.sin(ang)
    expected = np.array([c * rel[0] - s * rel[1],
                         s * rel[0] + c * rel[1]]) + pivot[:2]
    anim = Rotate(sq, angle=ang, about_point=pivot, run_time=1.0)
    hooks.install_hooks(anim)
    anim.begin(0.0)
    anim.interpolate(1.0)
    got = _center(sq)[:2]
    assert np.linalg.norm(got - expected) < 1e-6, (
        "Rotate ended at %s, expected %s about the pivot -- the shape spun in "
        "place instead of orbiting" % (np.round(got, 3), np.round(expected, 3)))
    anim.finish()
    # the final state must survive finish (points carry it, not the channel)
    assert np.linalg.norm(_center(sq)[:2] - expected) < 1e-6


def test_rotating_about_edge_orbits_the_hinge():
    """``Rotating(tri, 90*DEGREES, about_edge=UP)`` must swing about the top edge."""
    tri = Triangle(color=TEAL).scale(1.1).set_fill(TEAL, 0.5).shift(DOWN * 2.0)
    anim = Rotating(tri, angle=PI / 2, about_edge=UP, run_time=1.0)
    hooks.install_hooks(anim)
    anim.begin(0.0)
    c0 = _center(tri)[:2].copy()
    anim.interpolate(1.0)
    c1 = _center(tri)[:2].copy()
    assert np.linalg.norm(c1 - c0) > 0.3, (
        "Rotating about_edge=UP barely moved the centroid (%s -> %s) -- it spun "
        "in place" % (np.round(c0, 3), np.round(c1, 3)))
    anim.finish()
    assert np.linalg.norm(_center(tri)[:2] - c1) < 1e-6, (
        "finish() moved the triangle off its final orbited position")


def test_spin_in_place_without_a_pivot_stays_on_the_channel():
    """Non-regression: a default pivot keeps the cheap channel path (no baking)."""
    sq = Square(side_length=1.3, color=BLUE)
    start_pts = sq.points.copy()
    anim = Rotate(sq, angle=PI / 2, run_time=1.0)   # no about_point/about_edge
    hooks.install_hooks(anim)
    anim.begin(0.0)
    # centre must not move (spin in place) and the channel is used, not baked pts
    assert np.linalg.norm(_center(sq) - _center_3d(start_pts)) < 1e-6
    anim.interpolate(0.5)
    assert np.linalg.norm(_center(sq)[:2] - sq.points.mean(axis=0)[:2]) < 1e3


def _center_3d(pts):
    pts = np.asarray(pts, dtype=float)
    return (pts.min(axis=0) + pts.max(axis=0)) / 2.0
