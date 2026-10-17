"""Regression test: scene-level updaters (``Scene.add_updater``) must run.

Report: wiki ``01-场景与相机/场景/03-播放与等待`` "场景级 vs mobject 级 updater"
-- the red square driven by ``self.add_updater(scene_updater)`` sat still for
the whole clip while the identical blue square (``mobject.add_updater``)
climbed.  RTM's single updater walk (``_drive_mobject_updaters``) only ever
ran *mobject* updaters; it never touched ``scene.updaters``.

manim splits the pass in two and runs them in a fixed order:

    Scene.update_mobjects(dt)  ->  for mobj in self.mobjects: mobj.update(dt)
    Scene.update_self(dt)      ->  for func in self.updaters: func(dt)

and ``update_self``'s own docstring says scene updaters run *last*.  So the
fix appends a ``scene.updaters`` walk after the mobject walk, passing each
function the frame's ``dt``.

Pure Python: stub scene, no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from real_time_manim.vulkan_bind import _drive_mobject_updaters


class StubScene:
    """Minimal stand-in: manim's Scene always carries ``mobjects`` + ``updaters``."""

    def __init__(self):
        self.mobjects = []
        self.updaters = []

    def add(self, mob):
        self.mobjects.append(mob)

    def add_updater(self, func):
        self.updaters.append(func)

    def remove_updater(self, func):
        self.updaters = [f for f in self.updaters if f is not func]


def test_scene_updater_runs_and_gets_dt():
    """The reported case: a scene updater is called once per pass with ``dt``."""
    scene = StubScene()
    seen = []
    scene.add_updater(lambda dt: seen.append(dt))
    _drive_mobject_updaters(scene, 0.1)
    assert seen == [0.1], seen


def test_scene_updater_runs_after_mobject_updaters():
    """CE order: every mobject updater fires before any scene updater."""
    order = []
    scene = StubScene()

    from manim import Square
    mob = Square()
    mob.add_updater(lambda m: order.append("mobject"))
    scene.add(mob)
    scene.add_updater(lambda dt: order.append("scene"))

    _drive_mobject_updaters(scene, 0.05)
    assert order == ["mobject", "scene"], order


def test_removed_scene_updater_no_longer_runs():
    """``Scene.remove_updater`` takes the function back off the list."""
    scene = StubScene()
    seen = []
    updater = lambda dt: seen.append(dt)
    scene.add_updater(updater)
    _drive_mobject_updaters(scene, 0.1)
    scene.remove_updater(updater)
    _drive_mobject_updaters(scene, 0.1)
    assert seen == [0.1], seen


def test_scene_updater_drives_visible_state():
    """End-to-end shape of the wiki clip: the scene-driven square moves.

    A ``shift``-ing scene updater advances a mobject's centre once per pass,
    exactly like the red square that was frozen before the fix.
    """
    from manim import RIGHT, Square
    scene = StubScene()
    sq = Square().shift(RIGHT * 3)
    scene.add(sq)
    start = sq.get_center()[0]
    scene.add_updater(lambda dt: sq.shift(RIGHT * 0.5))
    for _ in range(4):
        _drive_mobject_updaters(scene, 1 / 60)
    assert sq.get_center()[0] == start + 2.0, sq.get_center()


def test_scene_without_updaters_attribute_is_fine():
    """A bare stub carrying no ``updaters`` at all must not crash the walk."""
    class Bare:
        mobjects = []
    _drive_mobject_updaters(Bare(), 0.1)   # no assertion: not raising is the pass
