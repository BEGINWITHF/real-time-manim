"""Phase 1.2 regression: containers must be traversed via ``submobjects``.

manim's ``Mobject.__iter__`` yields *self first* when the mobject has points:

    return it.chain([self] if self.has_points() else [], self.submobjects)

so ``enumerate(mob)`` / ``len(list(mob))`` on a point-bearing VGroup handed the
container back to itself -- HeatDiagramPlot died with a 978-frame RecursionError,
and the progress segmentation was off by one.

Pure Python: no DLL, no GPU (the guard short-circuits before touching the device).
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from manim import LEFT, RIGHT, Circle, Square, VGroup

from real_time_manim.vulkan_bind import MLWindow, container_subs


class FakeContainer:
    """A container whose __iter__ yields itself first, like manim's."""

    def __init__(self):
        self.children = [object(), object()]
        self.submobjects = self.children

    def has_points(self):
        return True

    def __iter__(self):
        import itertools
        return itertools.chain([self] if self.has_points() else [], self.submobjects)


def test_container_subs_returns_children_not_self():
    fake = FakeContainer()
    subs = container_subs(fake)
    assert list(subs) == fake.children
    assert fake not in list(subs)


def test_manim_iter_includes_self_but_container_subs_does_not():
    """Documents the trap: len(list(vg)) == len(vg.submobjects) + 1 when it has points."""
    vg = VGroup(Square(), Circle())
    vg.set_points_as_corners([LEFT, RIGHT])            # give the container points
    assert len(list(vg)) == len(vg.submobjects) + 1     # manim's __iter__ yields self
    assert len(container_subs(vg)) == len(vg.submobjects)


def test_container_subs_tolerates_plain_mobjects():
    assert list(container_subs(Square())) == []
    assert list(container_subs(object())) == []


def test_send_guard_stops_a_reentrant_mobject():
    """Second entry with the same id returns immediately (no device access)."""
    win = MLWindow.__new__(MLWindow)                   # no __init__ -> no DLL
    mob = Square()
    win._send_stack = {id(mob)}
    assert win._send(mob) is None                      # would recurse before the guard
    assert win._send_stack == {id(mob)}                # untouched: the guard did not run
