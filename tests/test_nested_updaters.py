"""Regression test: an updater on a *nested* mobject must run too.

Report: ``06_text.CodeAndNumericDisplay`` never counted up -- the ``Integer``
that lives inside the scene's ``VGroup`` row stayed at ``0`` for the whole
clip, where CE ends on ``3``.

``_drive_mobject_updaters`` walked ``scene.mobjects`` and read each entry's
``updaters``, i.e. it only ever ran the updaters of *top-level* mobjects.
manim drives that very list through ``Scene.update_mobjects`` ->
``Mobject.update(dt)``, which recurses into ``submobjects`` -- so an updater on
a nested mobject fired in CE and was silently skipped by RTM (probe with both
cases side by side in one scene: the top-level ``Integer`` reached 2.99, the
identical nested one stayed at 0).

Pure Python: stub scene, no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest
from manim import Integer, Square, ValueTracker, VGroup

from real_time_manim.vulkan_bind import _drive_mobject_updaters


class StubScene:
    def __init__(self):
        self.mobjects = []

    def add(self, mob):
        self.mobjects.append(mob)


def test_updater_on_mobject_inside_a_vgroup_runs():
    """The reported case: ``counter`` nested in the row, driven by a tracker."""
    scene = StubScene()
    tracker = ValueTracker(0.0)
    counter = Integer(0)
    counter.add_updater(lambda m: m.set_value(tracker.get_value()))
    scene.add(VGroup(counter))          # top-level is the GROUP, not the Integer

    tracker.set_value(3)
    _drive_mobject_updaters(scene, 0.1)

    assert counter.number == 3, (
        "the nested counter never ticked: its updater did not run")


def test_nested_updater_receives_dt():
    """A two-argument updater on a grandchild gets the frame's dt."""
    seen = []
    scene = StubScene()
    leaf = Square()
    leaf.add_updater(lambda m, dt: seen.append(dt))
    scene.add(VGroup(VGroup(leaf)))      # two levels of nesting
    _drive_mobject_updaters(scene, 0.05)
    assert seen == [0.05], seen


def test_top_level_updater_still_runs_once():
    """Non-regression: the top-level path keeps working and runs exactly once."""
    calls = []
    scene = StubScene()
    mob = Square()
    mob.add_updater(lambda m: calls.append(1))
    scene.add(mob)
    _drive_mobject_updaters(scene, 0.1)
    assert calls == [1], calls


def test_suspended_container_prunes_its_whole_subtree():
    """manim's ``Mobject.update`` returns before recursing when suspended."""
    seen = []
    scene = StubScene()
    leaf = Square()
    leaf.add_updater(lambda m, dt: seen.append(dt))
    container = VGroup(leaf)
    container.updating_suspended = True
    scene.add(container)
    _drive_mobject_updaters(scene, 0.05)
    assert seen == [], seen


def test_updater_may_rebuild_its_own_children():
    """``DecimalNumber.set_value`` replaces the digit submobjects in place.

    The walk snapshots ``submobjects`` after running the mobject's own
    updaters, so a rebuilding updater cannot mutate the list under it.
    """
    scene = StubScene()
    tracker = ValueTracker(0.0)
    counter = Integer(0)
    counter.add_updater(lambda m: m.set_value(tracker.get_value()))
    scene.add(VGroup(counter))

    for value in (1, 2, 3):
        tracker.set_value(value)
        _drive_mobject_updaters(scene, 1 / 60)
        assert counter.number == value
