# -*- coding: utf-8 -*-
"""Where does CE put the tip label vs where does RTM project it? (idx 18)

Pure geometry -- no rendering, no GPU.
"""
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import real_time_manim  # noqa: F401  -- bundled manim

from manim import Text, UR, DEGREES, ThreeDScene
from manim import Arrow3D

from real_time_manim.camera_state import viewport_from_scene, screen_scale

W, H = 1920, 1080

a = Arrow3D(start=[-2, -1, 0], end=[1.5, 0.5, 1.5])
tip = Text("tip=(%.1f, %.1f, %.1f)" % tuple(a.get_end()),
           font_size=24, color="#aaaaaa").next_to(a.get_end(), UR, buff=0.2)


class S(ThreeDScene):
    def construct(self):
        pass


scene = S()
scene.set_camera_orientation(phi=65 * DEGREES, theta=-60 * DEGREES)
scene.add_fixed_orientation_mobjects(tip)

vp = viewport_from_scene(scene)
print("viewport:", vp, "rotation:", None if vp is None else vp.rotation is not None)
cam = scene.camera
func = cam.fixed_orientation_mobjects.get(tip) or cam.fixed_orientation_mobjects.get(
    tip.submobjects[0])
print("center func:", func)
c = np.asarray(func(), dtype=float)
print("raw center:", np.round(c, 4))

_members = list(tip.family_members_with_points())
pts = np.vstack([np.asarray(m.points, dtype=float) for m in _members
                 if len(m.points)])
print("points:", pts.shape)
s = screen_scale(W, H, vp.height)

# --- RTM today: every point through the rotating viewport
cur = np.array([vp.project(p[0], p[1], W, H, p[2]) for p in pts])

# --- CE rule: points + (project_point(center) - center), then the plain
#     2D mapping (pixel = W/2 + s*x)
pc = vp.project(c[0], c[1], W, H, c[2])
world = np.array([(pc[0] - W / 2) / s, (H / 2 - pc[1]) / s])   # projected centre
ce = np.stack([W / 2 + s * (pts[:, 0] + world[0] - c[0]),
               H / 2 - s * (pts[:, 1] + world[1] - c[1])], axis=1)


def bb(xy):
    return (round(float(xy[:, 0].min())), round(float(xy[:, 0].max())),
            round(float(xy[:, 1].min())), round(float(xy[:, 1].max())))


print("RTM today   bbox x[%d..%d] y[%d..%d]" % bb(cur))
print("CE rule     bbox x[%d..%d] y[%d..%d]" % bb(ce))
print("CE video    ink x[1140..1580] y[364..408]  (from the twin at f0)")
print("RTM video   ink x[1120..1580] y[352..428]  (smeared, from the twin at f0)")

# how far does each candidate travel over the clip?  the camera orbits
for theta in (-60, -90, -120, -150):
    scene.set_camera_orientation(phi=65 * DEGREES, theta=theta * DEGREES)
    vp2 = viewport_from_scene(scene)
    c2 = np.asarray(func(), dtype=float)
    pc2 = vp2.project(c2[0], c2[1], W, H, c2[2])
    cur2 = np.array([vp2.project(p[0], p[1], W, H, p[2]) for p in pts])
    w2 = np.array([(pc2[0] - W / 2) / s, (H / 2 - pc2[1]) / s])
    ce2 = np.stack([W / 2 + s * (pts[:, 0] + w2[0] - c2[0]),
                    H / 2 - s * (pts[:, 1] + w2[1] - c2[1])], axis=1)
    print("theta=%4d  RTM centre %s   CE centre %s" % (
        theta, tuple(round(v) for v in cur2.mean(axis=0)),
        tuple(round(v) for v in ce2.mean(axis=0))))
