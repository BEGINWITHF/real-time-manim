"""Regression tests for the TransformMatching*/FadeTransform engine fixes.

The paint pipeline walks the SCENE tree only, which gave (2026-10-14, found
while re-recording the wiki's matching-transform demo) four related failures:

1. ``_WrappedFadeOut`` parked the fade opacity only on the detached wrapper
   group -- the tree reaches the parts through their real parents, never
   through the wrapper -- so unmatched source parts never dimmed.  Fixed by
   parking on the wrapper AND its direct children.
2. ``FadeTransform`` had both halves of the same disease: the source fade
   parked on a detached wrapper (source never faded), and its morph ghost
   was never IN the scene (the target half of the crossfade never showed,
   leaving the source glyphs to "morph" into nothing).  On top of that the
   ghost's points never morphed: the morph called ``VMobject.interpolate``
   on the direct children only, which is NOT recursive, and a
   ``MathTexPart`` carries no points of its own -- they sit on its glyph
   child.  Result: the ghost kept the source's stretched bounding box (a
   bright square) for the whole crossfade.
3. TMA's fade-in target copy (``_fade_target_copy``) was never presented
   either, so unmatched target parts stayed invisible until
   ``clean_up_from_scene`` popped them in.
4. ``clean_up_from_scene`` must remove the presented ghost: TMA drives its
   sub-anims itself and never calls their clean_up.

These tests assert the state the paint walk consumes: parked opacities on
tree-visited nodes, ghost geometry over time, and scene membership.
"""
import pytest
from manim import MathTex, Circle, RIGHT, Scene, Square, Text, VGroup

from real_time_manim.animations.base import get_anim_opacity
from real_time_manim.animations.fade_transform import FadeTransform
from real_time_manim.animations.transform_matching_shapes import (
    TransformMatchingShapes,
)
from real_time_manim.animations.transform_matching_tex import (
    TransformMatchingTex,
)
from real_time_manim.vulkan_bind import MLWindow


@pytest.fixture(scope="module")
def window():
    try:
        w = MLWindow(1920, 1080, hidden=True)
    except Exception as e:                              # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield w
    try:
        w.close()
    except Exception:
        pass


def _family_ids(scene):
    return {id(m) for m in scene.get_mobject_family_members()}


def _tmt(scene, **kw):
    eq1 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2")
    eq2 = MathTex("{{x}}^2", "=", "{{z}}^2", "-", "{{y}}^2").move_to(eq1)
    scene.add(eq1)
    return TransformMatchingTex(eq1, eq2, **kw)


def _sub(anim, cls):
    return next(a for a in anim._anims if isinstance(a, cls))


def _piece_transform(anim):
    """The per-piece FadeTransform inside the mismatch crossfade (CE parity).

    ``fade_transform_mismatches=True`` builds CE's ``FadeTransformPieces`` -- an
    AnimationGroup of one FadeTransform per matched pair -- so its ghosts live
    on the children, not on a single whole-group FadeTransform.  Returns the
    piece whose source and target boxes DIFFER, i.e. one whose ghost has a
    stretch to measure.
    """
    from real_time_manim.animations.fade_transform import FadeTransformPieces
    group = _sub(anim, FadeTransformPieces)
    pieces = [a for a in group.animations if isinstance(a, FadeTransform)]
    for piece in pieces:
        if abs(piece.mobject.height - piece.target_mobject.height) > 0.1:
            return group, piece
    return group, pieces[0]


# --------------------------------------------------------------------------- #
# 1/2. FadeTransform: source fade + ghost presentation + morph
# --------------------------------------------------------------------------- #

def test_wrapped_fade_transform_parks_source_parts_down_and_restores():
    """The key-mapped source part (reached via its real parent) must dim.

    CE pairs the key_map parts with ``FadeTransformPieces`` -- a per-piece
    crossfade: each source part fades out where it stands while a COPY of its
    partner fades in at the partner's place.  RTM used one whole-group
    ``FadeTransform``, whose single ghost is stretched to the source's
    bounding box: during the transition the source stayed at full strength
    and that (wrongly sized) ghost was painted over it, so the wiki clip
    ``03-动画/匹配变换/01-匹配变换-shapes_keymap`` showed "c" and "h" at
    once instead of a clean crossfade into "hat".
    """
    scene = Scene()
    src = Text("cat", font_size=52)
    tar = Text("hat", font_size=52).move_to(src)
    scene.add(src)
    key_map = {
        TransformMatchingShapes.get_mobject_key(src[0]):   # "c"
        TransformMatchingShapes.get_mobject_key(tar[0]),   # "h"
    }
    anim = TransformMatchingShapes(src, tar, key_map=key_map, run_time=2.0)
    anim.begin(0.0)

    # per-piece crossfade, not a whole-group FadeTransform
    assert not any(isinstance(a, FadeTransform) for a in anim._anims)
    copies = anim._key_mapped_copies
    assert len(copies.submobjects) == 1

    # mid-crossfade: the source "c" sits at ~0.5 and its partner's copy too
    anim.interpolate(1.0)
    assert get_anim_opacity(src[0]) == pytest.approx(0.5, abs=0.05)
    assert get_anim_opacity(copies.submobjects[0]) == pytest.approx(0.5, abs=0.05)

    # near the end the source must be gone and the target copy fully in
    anim.interpolate(1.99)
    assert get_anim_opacity(src[0]) < 0.02
    assert get_anim_opacity(copies.submobjects[0]) > 0.98

    # and the reset pass must restore it (CE resets before the source leaves)
    anim.interpolate(0.0)
    assert get_anim_opacity(src[0]) == pytest.approx(1.0)


def _mismatch_scene():
    """Two same-count groups with a shape that exists on ONE side only.

    The shared Square is matched by shape key, so only the Triangle/Circle pair
    reaches the mismatch branch -- which is exactly the branch under test.
    """
    from manim import Triangle
    src = VGroup(Square(side_length=1.0),
                 Triangle(radius=0.4).shift(RIGHT * 2))
    tar = VGroup(Square(side_length=1.0).shift(RIGHT * 2),
                 Circle(radius=1.0))
    return Scene(), src, tar


def test_fade_transform_ghost_morphs_to_target_shape(window):
    """Each per-piece ghost must be presented and morph to its own target.

    ``fade_transform_mismatches=True`` is CE's ``FadeTransformPieces``: one
    FadeTransform per pair, so each ghost is stretched to ITS part's box and
    then morphs to that part's target.  (The old whole-group FadeTransform
    stretched one ghost to the whole group's box: measured 0.332 against a
    0.020 target part.)
    """
    scene, src, tar = _mismatch_scene()
    scene.add(src)
    anim = TransformMatchingShapes(src, tar, fade_transform_mismatches=True,
                                   run_time=2.0)
    anim.begin(0.0)
    window.scene = scene
    try:
        group, ft = _piece_transform(anim)
        ghost, target = ft._ghost, ft.target_mobject
        window._present_detached_animated([anim])
        anim.interpolate(0.0)      # the group begins its children lazily

        assert id(ghost) in _family_ids(scene), (
            "each piece's FadeTransform ghost must be presented to the paint "
            "walk")

        start_h = ghost.height            # stretched to this pair's source box
        assert abs(start_h - target.height) > 1e-6, (
            "the ghost should start at the source part's box, not the "
            "target's (%s vs %s)" % (start_h, target.height))

        anim.interpolate(1.0)                          # mid-crossfade
        assert abs(ghost.height - target.height) < abs(start_h - target.height), (
            "ghost should be partway between the source box and the target")

        anim.interpolate(1.99)                         # near the end
        assert ghost.height == pytest.approx(target.height, abs=0.02)
        assert get_anim_opacity(ghost) > 0.98
    finally:
        window.scene = None


def test_tma_cleanup_removes_the_presented_ghost(window):
    """TMA never calls its sub-anims' clean_up, so it must remove ghosts.

    Before the fix the ghost -- presented above -- would have lingered in
    the scene tree at parked opacity 0 forever.
    """
    scene, src, tar = _mismatch_scene()
    scene.add(src)
    anim = TransformMatchingShapes(src, tar, fade_transform_mismatches=True,
                                   run_time=1.0)
    anim.begin(0.0)
    window.scene = scene
    try:
        window._present_detached_animated([anim])
        group, ft = _piece_transform(anim)
        ghost = ft._ghost
        assert ghost in scene.mobjects

        anim.interpolate(0.5)          # the group begins its children lazily
        anim.finish()
        anim.clean_up_from_scene(scene)
        assert all(m is not ghost for m in scene.mobjects)
        # the target takes over and is fully opaque again
        assert anim.target_mobject in scene.mobjects
        for part in anim.target_mobject.submobjects:
            assert get_anim_opacity(part) == pytest.approx(1.0)
    finally:
        window.scene = None


# --------------------------------------------------------------------------- #
# 3. TMA default branch: fade-in target copy presentation
# --------------------------------------------------------------------------- #

def test_key_map_crossfade_copies_are_presented_and_removed(window):
    """The key-mapped partner copies must be presented DURING the play.

    The per-piece crossfade parks its incoming copies in a detached VGroup,
    which the scene tree cannot reach -- without presenting them the source
    faded out into nothing and the target popped in at clean_up.
    """
    scene = Scene()
    src = Text("cat", font_size=52)
    tar = Text("hat", font_size=52).move_to(src)
    scene.add(src)
    key_map = {
        TransformMatchingShapes.get_mobject_key(src[0]):
        TransformMatchingShapes.get_mobject_key(tar[0]),
    }
    anim = TransformMatchingShapes(src, tar, key_map=key_map, run_time=1.0)
    anim.begin(0.0)
    window.scene = scene
    try:
        copies = anim._key_mapped_copies
        window._present_detached_animated([anim])
        assert id(copies) in _family_ids(scene), (
            "the key-mapped crossfade copies must be presented")
        anim.interpolate(0.5)
        assert get_anim_opacity(copies.submobjects[0]) == pytest.approx(
            0.5, abs=0.06)
        anim.finish()
        anim.clean_up_from_scene(scene)
        assert all(m is not copies for m in scene.mobjects), (
            "clean_up must remove the presented copies again")
        assert anim.target_mobject in scene.mobjects
    finally:
        window.scene = None


def test_tma_fade_in_target_copy_is_presented_and_removed(window):
    """The unmatched target parts must fade in DURING the play.

    Before the fix the copy was never in the scene, so `−` (etc.) stayed
    invisible for the whole flight and popped in at clean_up.
    """
    scene = Scene()
    anim = _tmt(scene, run_time=1.0)
    scene.add(anim.mobject)
    anim.begin(0.0)
    window.scene = scene
    try:
        ftc = anim._fade_target_copy
        assert ftc is not None and len(ftc.submobjects) == 1  # the "−" part

        window._present_detached_animated([anim])
        assert id(ftc) in _family_ids(scene), (
            "the fade-in target copy must be presented to the paint walk")

        anim.interpolate(0.5)
        # FadeIn parks the copy's wrapper (which the paint walk reaches as a
        # presented scene root); its parts inherit via parent x child alpha.
        assert get_anim_opacity(ftc) == pytest.approx(0.5, abs=0.06), (
            "the unmatched target parts must fade in with the animation")

        anim.finish()
        anim.clean_up_from_scene(scene)
        assert all(m is not ftc for m in scene.mobjects), (
            "clean_up must remove the presented copy again")
        assert anim.target_mobject in scene.mobjects
    finally:
        window.scene = None


# --------------------------------------------------------------------------- #
# 4. end state after a full begin -> interpolate -> clean_up cycle
# --------------------------------------------------------------------------- #

def test_key_map_end_state_is_the_target_with_pristine_source():
    scene = Scene()
    src = Text("cat", font_size=52)
    tar = Text("hat", font_size=52).move_to(src)
    scene.add(src)
    key_map = {
        TransformMatchingShapes.get_mobject_key(src[0]):
        TransformMatchingShapes.get_mobject_key(tar[0]),
    }
    anim = TransformMatchingShapes(src, tar, key_map=key_map, run_time=1.0)
    anim.begin(0.0)
    anim.interpolate(1.0)
    anim.finish()
    anim.clean_up_from_scene(scene)

    assert all(m is not src for m in scene.mobjects), "source must leave"
    assert tar in scene.mobjects, "target must take over"
    for letter in src.submobjects:                     # pristine for reuse
        assert get_anim_opacity(letter) == pytest.approx(1.0)


def test_transform_mismatches_end_state():
    scene = Scene()
    src = Text("cat", font_size=52)
    tar = Text("hat", font_size=52).move_to(src)
    scene.add(src)
    anim = TransformMatchingShapes(src, tar, transform_mismatches=True,
                                   run_time=1.0)
    anim.begin(0.0)
    anim.interpolate(1.0)
    anim.finish()
    anim.clean_up_from_scene(scene)

    assert all(m is not src for m in scene.mobjects)
    assert tar in scene.mobjects
    for part in tar.submobjects:
        assert get_anim_opacity(part) == pytest.approx(1.0)
