"""Regression test: RTM hands a manim animation its scene before begin().

manim's Scene.play() calls Animation._setup_scene(scene) first; that stores
anim.scene (AddTextWordByWord reads it) and registers introducers' mobjects with
the scene.  RTM drives manim's classes directly and skipped this, so
AddTextWordByWord died with "'AddTextWordByWord' object has no attribute 'scene'".

Pure Python: no window, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from manim import Circle, Square

from real_time_manim.vulkan_bind import _setup_anim_scene


class FakeScene:
    """Just enough Scene for manim's introducer path."""

    def __init__(self):
        self.mobjects = []

    def add(self, mob):
        self.mobjects.append(mob)

    def get_mobject_family_members(self):
        return list(self.mobjects)


def test_uses_manims_own_setup_hook():
    """manim's hook does more than set .scene (introducers register mobjects)."""
    seen = {}

    class Anim:
        def _setup_scene(self, scene):
            seen["scene"] = scene

    scene = FakeScene()
    assert _setup_anim_scene(Anim(), scene) is True
    assert seen["scene"] is scene


def test_falls_back_to_assigning_scene():
    class Anim:
        pass

    anim, scene = Anim(), FakeScene()
    assert _setup_anim_scene(anim, scene) is True
    assert anim.scene is scene


def test_broken_hook_does_not_raise():
    class Anim:
        def _setup_scene(self, scene):
            raise RuntimeError("boom")

    anim, scene = Anim(), FakeScene()
    assert _setup_anim_scene(anim, scene) is True      # falls back to .scene
    assert anim.scene is scene


def test_real_manim_animation_gets_the_scene():
    """A plain manim animation uses Animation._setup_scene from manim itself."""
    from manim.animation.creation import ShowIncreasingSubsets
    anim = ShowIncreasingSubsets(Circle())
    scene = FakeScene()
    assert _setup_anim_scene(anim, scene) is True
    assert getattr(anim, "scene", None) is scene


def test_introducer_registers_its_mobject_with_the_scene():
    """manim's hook also adds introducers' mobjects -- RTM must not skip that."""
    from manim import Create
    mob = Square()
    anim = Create(mob)
    scene = FakeScene()
    _setup_anim_scene(anim, scene)
    assert anim.scene is scene
    assert mob in scene.mobjects


def test_addtextwordbyword_like_chain_no_longer_missing_scene():
    """The reported class: Succession of manim animations, needs .scene."""
    from manim.animation.creation import AddTextWordByWord
    from manim import Text
    anim = AddTextWordByWord(Text("hi there"))
    scene = FakeScene()
    _setup_anim_scene(anim, scene)
    assert getattr(anim, "scene", None) is scene
