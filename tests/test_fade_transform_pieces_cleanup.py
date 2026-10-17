"""Regression test: ``FadeTransformPieces`` must not leave a target copy behind.

Report: wiki ``03-动画/变换/05-淡出淡入式变换`` -- after a ``FadeTransformPieces``
finished, a copy of the target stayed on screen and a later ``FadeOut`` could not
remove it (the red circle + yellow triangle lingering at the clip's end).

Two facts combine into the bug:

1. ``PlayMixin._present_detached_animated`` walks into a group and adds every
   piece's ``_ghost`` (``target.copy()``) to the scene, because RTM paints only
   the scene tree and the crossfade copy is otherwise unreachable.
2. Each ``FadeTransform.clean_up_from_scene`` is what removes that ghost again
   -- but ``AnimationGroup`` inherited the base ``Animation.clean_up_from_scene``
   (a no-op ``pass``) and never recursed into its children, so for the grouped
   ``...Pieces`` form the ghosts were never removed.

manim's ``AnimationGroup.clean_up_from_scene`` loops over
``self.animations`` calling each child's clean-up; restoring that recursion is
the fix.

Pure Python: stub scene, no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import Circle, LEFT, RIGHT, Square, VGroup

from real_time_manim.animations.animation_group import AnimationGroup
from real_time_manim.animations.fade_transform import FadeTransformPieces


class StubScene:
    def __init__(self):
        self.mobjects = []

    def add(self, mob):
        if mob not in self.mobjects:
            self.mobjects.append(mob)

    def remove(self, mob):
        self.mobjects = [m for m in self.mobjects if m is not mob]


def _present_piece_ghosts(group, scene):
    """Mirror ``_present_detached_animated``: add every piece's ``_ghost``."""

    def visit(anim):
        ghost = getattr(anim, "_ghost", None)
        if ghost is not None:
            scene.add(ghost)
        for sub in (getattr(anim, "animations", None) or ()):
            visit(sub)

    visit(group)


def _make_pieces():
    src = VGroup(Square(), Circle()).shift(LEFT * 2)
    tgt = VGroup(Square(), Circle()).shift(RIGHT * 2)
    return FadeTransformPieces(src, tgt)


def test_piece_ghosts_are_added_then_removed():
    """The reported residual: presented ghosts must be gone after clean-up."""
    scene = StubScene()
    pieces = _make_pieces()
    pieces.begin(0.0)

    _present_piece_ghosts(pieces, scene)
    ghosts = [sub._ghost for sub in pieces.animations]
    assert all(g is not None for g in ghosts)
    assert all(g in scene.mobjects for g in ghosts), (
        "the test premise failed: the piece ghosts were not presented")

    # A group's children begin lazily inside interpolate(); drive it to the end
    # so each piece reaches its finished state before clean-up (as the timeline
    # does: finalize -> interpolate over time -> finish -> clean_up_from_scene).
    run_time = float(pieces.run_time or 1.0)
    pieces.interpolate(pieces.start_time + run_time)
    pieces.finish()
    pieces.clean_up_from_scene(scene)

    assert not any(g in scene.mobjects for g in ghosts), (
        "FadeTransformPieces left a ghost (target copy) in the scene -- "
        "AnimationGroup did not recurse clean_up_from_scene into its children")


def test_animation_group_recurse_clean_up_into_children():
    """Generic contract: a group runs each child's clean_up_from_scene."""

    calls = []

    class RecordingChild:
        def clean_up_from_scene(self, scene):
            calls.append(id(scene))

    class PlainChild:
        pass

    scene = StubScene()
    group = AnimationGroup.__new__(AnimationGroup)   # skip __init__ wiring
    group.animations = [RecordingChild(), PlainChild()]
    group.clean_up_from_scene(scene)
    assert calls == [id(scene)], calls


def test_whole_fade_transform_still_cleans_its_ghost():
    """Non-regression: a lone (ungrouped) FadeTransform keeps removing its ghost."""
    from real_time_manim.animations.fade_transform import FadeTransform

    scene = StubScene()
    src = Square().shift(LEFT * 2)
    tgt = Square().shift(RIGHT * 2)
    ft = FadeTransform(src, tgt)
    ft.begin(0.0)
    if ft._ghost is not None:
        scene.add(ft._ghost)
    ft.finish()
    ft.clean_up_from_scene(scene)
    assert ft._ghost is None or ft._ghost not in scene.mobjects
