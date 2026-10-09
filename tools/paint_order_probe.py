"""Compare RTM's actual paint order with the order Manim CE paints in.

CE's rule (manim 0.20.1, camera/camera.py + utils/family.py):

    Camera.get_mobjects_to_display
      -> extract_mobject_family_members(scene.mobjects,
                                         use_z_index=True,
                                         only_those_with_points=True)
         = flatten every root's family in pre-order, drop duplicates
           (first occurrence wins), then STABLE-sort by ``m.z_index``.

`ThreeDCamera.get_mobjects_to_display` then stable-sorts that list by its own
camera-space depth key, so in a 3D scene the order is

    (depth, z_index, family pre-order)

and in 2D it is just

    (z_index, family pre-order)

The probe instruments RTM's leaf senders (``_send_*``) so it sees the order
mobjects actually reach the GPU, maps each onto the index CE would paint it
at, and reports every index that goes backwards.

Run::

    python -X utf8 tools/paint_order_probe.py                 # built-in battery
    python -X utf8 tools/paint_order_probe.py --scene Graph   # one case
"""

from __future__ import annotations

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np

from manim import (
    BLUE,
    DOWN,
    GREEN,
    RED,
    UP,
    WHITE,
    YELLOW,
    Circle,
    Dot,
    Graph,
    MathTex,
    Scene,
    Square,
    Text,
    ThreeDScene,
    VGroup,
)
from manim.utils.family import extract_mobject_family_members

import real_time_manim.vulkan_bind as vb


class _Recorder(object):
    """Stands in for the native DLL and keeps every submitted call."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


# Leaf senders: every branch of _send_impl that actually emits geometry.
LEAF_SENDERS = (
    "_send_vmobject", "_send_polygon", "_send_square", "_send_rectangle",
    "_send_ellipse", "_send_dot", "_send_circle", "_send_arrow",
    "_send_dashed_line", "_send_line", "_send_arc", "_send_point",
    "_send_point_cloud", "_send_text_write",
)


def ce_order(scene, three_d=False):
    """The mobjects CE paints, in CE's order.

    The render list is ``list_update(scene.mobjects,
    scene.foreground_mobjects)`` -- exactly what ``CairoRenderer.update_frame``
    hands to ``camera.capture_mobjects``.
    """
    render = list(scene.mobjects)
    known = {id(m) for m in render}
    for fg in getattr(scene, "foreground_mobjects", None) or ():
        if id(fg) not in known:
            render.append(fg)
            known.add(id(fg))
    members = extract_mobject_family_members(
        render, use_z_index=True, only_those_with_points=True)
    if not three_d:
        return members
    from manim.camera.three_d_camera import ThreeDCamera
    cam = getattr(scene, "camera", None)
    if not isinstance(cam, ThreeDCamera):
        return members
    rot = np.asarray(cam.get_rotation_matrix(), dtype=float)

    def z_key(mob):
        if not getattr(mob, "shade_in_3d", False):
            return np.inf
        return float(np.dot(mob.get_z_index_reference_point(), rot.T)[2])

    # stable: depth first, then z_index, then the family order from above
    by_depth = sorted(range(len(members)), key=lambda i: z_key(members[i]))
    return [members[i] for i in by_depth]


def rtm_order(window, scene, recorder=None):
    """The mobjects RTM paints, in submission order."""
    rec = recorder if recorder is not None else _Recorder()
    real_dll = window.dll
    painted = []
    wrapped = []
    window.dll = rec
    for name in LEAF_SENDERS:
        fn = getattr(window, name, None)
        if fn is None or not callable(fn):
            continue

        def make(fn):
            def wrapper(*args, **kwargs):
                mob = args[0] if args else None
                if mob is not None and (not painted or painted[-1] is not mob):
                    painted.append(mob)
                return fn(*args, **kwargs)
            return wrapper

        setattr(window, name, make(fn))
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
    return painted


def _name(mob):
    try:
        pos = np.round(np.asarray(mob.get_center(), dtype=float), 2)
    except Exception:
        pos = "?"
    return "%s@%s z=%s" % (type(mob).__name__, pos, getattr(mob, "z_index", "?"))


def ce_index(mob, index):
    """CE's paint index for ``mob``, or for its first painted family member.

    RTM paints some containers as ONE unit (a ``Text`` emits all of its glyphs
    in a single ``_send_text_write`` call), while CE's list holds the glyphs.
    A container therefore resolves through its own family; ``None`` means CE
    would not paint it at all.
    """
    i = index.get(id(mob))
    if i is not None:
        return i
    best = None
    for sub in getattr(mob, "family_members_with_points", lambda: [])():
        j = index.get(id(sub))
        if j is not None and (best is None or j < best):
            best = j
    return best


def report(label, scene, window, three_d=False, verbose=True):
    expected = ce_order(scene, three_d=three_d)
    index = {}
    for i, m in enumerate(expected):
        index.setdefault(id(m), i)
    painted = rtm_order(window, scene)

    unknowns, drops = [], []
    counts = {}
    by_id = {}
    last = -1
    for mob in painted:
        i = ce_index(mob, index)
        if i is None:
            unknowns.append(mob)
            continue
        counts[id(mob)] = counts.get(id(mob), 0) + 1
        by_id[id(mob)] = mob
        if i < last:
            drops.append((last, i, mob))
        last = max(last, i)
    covered = set()
    for p in painted:
        covered.add(id(p))
        for sub in getattr(p, "family_members_with_points", lambda: [])():
            covered.add(id(sub))
    missing = [m for m in expected if id(m) not in covered]
    ok = not drops and not unknowns
    twice = [by_id[k] for k, n in sorted(counts.items()) if n > 1]
    print("%-42s %s  (CE members=%d, painted=%d, unknown=%d, missing=%d, "
          "twice=%d)" % (label, "OK  " if ok else "ORDER", len(expected),
                         len(painted), len(unknowns), len(missing), len(twice)))
    if verbose and twice:
        for mob in twice[:6]:
            print("      painted more than once: %s" % _name(mob))
    if verbose and not ok:
        for a, b, mob in drops[:8]:
            print("      back-step: CE idx %d -> %d  (%s)" % (a, b, _name(mob)))
        for mob in unknowns[:6]:
            print("      painted by RTM but not by CE: %s" % _name(mob))
        for mob in missing[:8]:
            print("      never painted by RTM: %s" % _name(mob))
    return ok, drops


# --------------------------------------------------------------------------- #
# battery
# --------------------------------------------------------------------------- #

def scene_set_z_index():
    """manim's own SetZIndex doc example (mobject.py:3346)."""
    scene = Scene()
    text = Text("z_index = 3", color=RED).shift(UP).set_z_index(3)
    square = Square(2, fill_opacity=1).set_z_index(2)
    tex = MathTex(r"zIndex = 1", color=BLUE).shift(DOWN).set_z_index(1)
    circle = Circle(radius=1.7, color=GREEN, fill_opacity=1)
    scene.add(text, square, tex, circle)
    return scene


def scene_graph_edges():
    """manim's Graph draws its edges with z_index=-1 (graph.py:1057)."""
    scene = Scene()
    graph = Graph(
        [1, 2, 3, 4],
        [(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)],
        layout="circular",
        vertex_config={"radius": 0.25, "fill_color": YELLOW},
        edge_config={"stroke_width": 6, "stroke_color": BLUE},
    )
    scene.add(graph)
    return scene


def scene_child_root_first():
    """A child is a scene root, then a group containing it is added."""
    scene = Scene()
    dot = Dot(point=[0, 0, 0], color=RED, radius=0.5)
    scene.add(dot)
    square = Square(fill_color=WHITE, fill_opacity=1,
                    stroke_width=0).scale(1.4)
    scene.add(VGroup(square, dot))
    return scene


def scene_z_index_across_roots():
    """z_index must reorder ACROSS roots, not just inside one."""
    scene = Scene()
    a = Square(fill_color=RED, fill_opacity=1, stroke_width=0).shift(2.0)
    b = Circle(radius=1.4, fill_color=BLUE, fill_opacity=1, stroke_width=0)
    c = Square(fill_color=GREEN, fill_opacity=1, stroke_width=0).scale(0.6)
    c.set_z_index(-1)
    scene.add(a, b, c)
    return scene


def scene_nested_z_index():
    """One root whose children disagree about z_index (the Graph shape)."""
    scene = Scene()
    back = Square(fill_color=RED, fill_opacity=1, stroke_width=0).scale(2.0)
    front = Circle(radius=0.7, fill_color=YELLOW, fill_opacity=1,
                   stroke_width=0)
    front.set_z_index(1)
    scene.add(VGroup(back, front))
    other = Square(fill_color=BLUE, fill_opacity=1, stroke_width=0).scale(0.4)
    scene.add(other)
    return scene


def scene_three_d_overlay():
    """A 2D overlay over 3D content in a ThreeDScene."""
    scene = ThreeDScene()
    sq = Square(fill_color=WHITE, fill_opacity=1, stroke_width=0).scale(1.5)
    sq.set_z_index(1)
    scene.add(sq)
    return scene


def scene_three_d_depth():
    """Two shaded discs at different depths plus an unshaded overlay."""
    from manim import IN, OUT, Text as T
    scene = ThreeDScene()
    near = Circle(radius=1.6, fill_color=RED, fill_opacity=1, stroke_width=0)
    near.set_shade_in_3d(True).shift(2.0 * OUT)
    far = Circle(radius=1.1, fill_color=BLUE, fill_opacity=1, stroke_width=0)
    far.set_shade_in_3d(True).shift(2.0 * IN)
    overlay = Circle(radius=0.5, fill_color=GREEN, fill_opacity=1,
                     stroke_width=0)
    scene.add(near, far, overlay)
    return scene


def scene_fixed_in_frame():
    """A fixed caption over 3D content (ThreeDScene.add_fixed_in_frame_mobjects)."""
    from manim import OUT, Text as T
    scene = ThreeDScene()
    body = Square(fill_color=WHITE, fill_opacity=1, stroke_width=0).scale(2.0)
    body.set_shade_in_3d(True).shift(1.5 * OUT)
    caption = T("caption", font_size=48).shift(2.5 * -1)
    scene.add(body)
    scene.add_fixed_in_frame_mobjects(caption)
    return scene


def scene_axes_labels():
    """Axes: ticks/numbers/labels are children of a point-less container."""
    from manim import Axes as Ax
    scene = Scene()
    axes = Ax(x_range=[-3, 3, 1], y_range=[-2, 2, 1])
    dot = Dot(point=[1, 1, 0], color=RED, radius=0.2)
    scene.add(axes, dot)
    return scene


def scene_table_cells():
    """manim's Table cells are drawn over their grid lines."""
    from manim import Table
    scene = Scene()
    table = Table([["a", "b"], ["c", "d"]],
                  row_labels=[Text("r1"), Text("r2")],
                  col_labels=[Text("c1"), Text("c2")])
    scene.add(table)
    return scene


def scene_readd_moves_front():
    """``scene.add`` of an existing root moves it to the front (CE)."""
    scene = Scene()
    a = Square(fill_color=RED, fill_opacity=1, stroke_width=0).scale(1.5)
    b = Circle(radius=1.4, fill_color=BLUE, fill_opacity=1, stroke_width=0)
    scene.add(a, b)
    scene.add(a)                      # CE: remove then append -> on top
    return scene


def scene_bring_to_front():
    from manim import Scene as S
    scene = S()
    a = Square(fill_color=RED, fill_opacity=1, stroke_width=0).scale(1.5)
    b = Circle(radius=1.4, fill_color=BLUE, fill_opacity=1, stroke_width=0)
    scene.add(a, b)
    scene.bring_to_back(a)
    return scene


def scene_text_over_shapes():
    """A VGroup of glyphs over an overlapping shape (the everyday case)."""
    scene = Scene()
    shape = Circle(radius=1.6, fill_color=BLUE, fill_opacity=1,
                   stroke_width=0)
    words = Text("label").scale(1.6)
    scene.add(shape, words)
    return scene


def scene_labeled_arrow():
    from manim import LabeledArrow, ORIGIN, RIGHT as R
    scene = Scene()
    ar = LabeledArrow("flow", start=ORIGIN, end=3 * R)
    scene.add(ar)
    return scene


BATTERY = {
    "set_z_index (doc example)": (scene_set_z_index, False),
    "Graph edges z_index=-1": (scene_graph_edges, False),
    "child root before parent": (scene_child_root_first, False),
    "z_index across roots": (scene_z_index_across_roots, False),
    "nested roots disagree on z": (scene_nested_z_index, False),
    "ThreeDScene + 2D overlay": (scene_three_d_overlay, True),
    "ThreeD depth vs overlay": (scene_three_d_depth, True),
    "ThreeD fixed-in-frame": (scene_fixed_in_frame, True),
    "Axes children": (scene_axes_labels, False),
    "Table cells": (scene_table_cells, False),
    "re-add moves to front": (scene_readd_moves_front, False),
    "bring_to_back": (scene_bring_to_front, False),
    "Text over a shape": (scene_text_over_shapes, False),
    "LabeledArrow": (scene_labeled_arrow, False),
}


def main(argv):
    only = None
    if "--scene" in argv:
        only = argv[argv.index("--scene") + 1]
    window = None
    failures = 0
    for label, (factory, three_d) in BATTERY.items():
        if only and only.lower() not in label.lower():
            continue
        if window is None:
            window = vb.MLWindow(1920, 1080, hidden=True)
        try:
            scene = factory()
            ok, _ = report(label, scene, window, three_d=three_d)
            if not ok:
                failures += 1
        except Exception as exc:                      # noqa: BLE001
            import traceback
            traceback.print_exc()
            print("%-42s ERROR %s" % (label, exc))
            failures += 1
    if window is not None:
        try:
            window.close()
        except Exception:
            pass
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
