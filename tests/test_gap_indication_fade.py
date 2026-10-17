"""Gap tests: A20 Circumscribe.time_width / A21 ShowPassingFlash.remover /
A22 FadeIn inside AnimationGroup / A23 FadeTransformPieces residuals.

Pure Python: a stub scene + direct ``begin``/``interpolate``/``clean_up_from_scene``
calls -- no window, no GPU, no ffmpeg.

* **A20** ``real_time_manim/animations/circumscribe.py`` -- ``time_width`` was
  never wired in: the frame was always drawn with ``Create`` and the beam width
  parameter did nothing ("传入后画面无差别").  CE draws the non-fade branch as
  ``ShowPassingFlash(frame, time_width)`` -- a ``time_width``-wide sliver, the
  rest of the outline transparent.  The default render must stay byte-identical,
  so the sliver is selected by *passing* ``time_width`` (the sentinel default is
  numerically CE's ``0.3``).
* **A21** ``real_time_manim/animations/show_passing_flash.py`` -- ``remover``
  was hard-wired to ``True``; it is now a constructor parameter (default
  unchanged) and ``remover=False`` must leave the mobject in the scene *and*
  fully stroked.
* **A22** ``real_time_manim/animations/fade_in.py`` -- regression net for the
  reported "AnimationGroup 里 FadeIn 新对象整段不显示": the fade-in half must
  carry every target and ramp it 0 -> 1.  (Whether the targets ENTER the scene
  is decided by ``window/play.py::_ensure_animated_present``, which presents
  ``child.mobject``/``child.mobjects`` of a group -- see the report.)
* **A23** ``real_time_manim/animations/fade_transform.py`` -- a finished
  ``FadeTransformPieces`` left a copy of the target on screen that a later
  ``FadeOut`` could not dim (the morph ``_ghost`` presented as a scene root,
  plus the piece targets parked as detached roots).
"""

import inspect
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import Circle, LEFT, RIGHT, Square, Triangle, UP, VGroup

from real_time_manim.animations.animation_group import AnimationGroup
from real_time_manim.animations.circumscribe import Circumscribe
from real_time_manim.animations.create import Create
from real_time_manim.animations.fade_in import FadeIn
from real_time_manim.animations.fade_out import FadeOut
from real_time_manim.animations.fade_transform import FadeTransform, FadeTransformPieces
from real_time_manim.animations.show_passing_flash import ShowPassingFlash
from real_time_manim.state import get_anim_opacity


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

class StubScene:
    """Bare scene: a list of roots with manim's ``add``/``remove`` shape."""

    def __init__(self):
        self.mobjects = []

    def add(self, mob):
        if mob in self.mobjects:
            return
        # Scene.add absorbs family members that are roots before appending
        family = set(id(m) for m in mob.get_family())
        self.mobjects = [m for m in self.mobjects if id(m) not in family]
        self.mobjects.append(mob)

    def remove(self, mob):
        self.mobjects = [m for m in self.mobjects if m is not mob]


def effective_alpha(scene, mob):
    """Paint alpha of ``mob`` when reached through its root (parent x child)."""

    def walk(node, acc):
        a = acc * float(get_anim_opacity(node) or 0.0)
        if node is mob:
            return a
        for sub in getattr(node, "submobjects", ()):
            found = walk(sub, a)
            if found is not None:
                return found
        return None

    for root in scene.mobjects:
        if root is mob:
            return float(get_anim_opacity(root) or 0.0)
        found = walk(root, 1.0)
        if found is not None:
            return found
    return None                      # not in the scene at all


def sweep_window(mob):
    """``(lower, upper)`` of a sliding flash window, or ``None``."""
    if not hasattr(mob, "_vulkan_progress_upper"):
        return None
    return (float(mob._vulkan_progress_lower),
            float(mob._vulkan_progress_upper))


def drive(anim, end_fraction=1.0, steps=4):
    """Run ``anim`` from its start to ``end_fraction * run_time``."""
    anim.begin(0.0)
    for i in range(1, steps + 1):
        anim.interpolate(end_fraction * anim.run_time * i / steps)


# --------------------------------------------------------------------------- #
# A20 -- Circumscribe.time_width
# --------------------------------------------------------------------------- #

def _mid_frame(**kwargs):
    """The frame half way through a fresh ``Circumscribe``."""
    cs = Circumscribe(Square(), **kwargs)
    # a real play evaluates frame 0 first, which is where Succession activates
    # its child; jumping straight in would begin the child at that timestamp.
    cs.begin(0.0)
    cs.interpolate(0.0)
    cs.interpolate(0.5 * cs.run_time)
    return cs, cs._frame


@pytest.mark.parametrize("time_width", [0.2, 0.8, 1.5])
def test_circumscribe_time_width_is_the_sweep_width(time_width):
    """The lit sliver is exactly ``time_width`` wide (CE semantics)."""
    cs, frame = _mid_frame(time_width=time_width)
    window = sweep_window(frame)
    assert window is not None, (
        "time_width=%s did not reach the stroke: the frame carries no sweep "
        "window, so the parameter is still ignored" % time_width)
    lower, upper = window
    assert upper - lower == pytest.approx(min(time_width, 1.0), abs=1e-9)


def test_circumscribe_time_width_leaves_the_rest_transparent():
    """Only the beam is drawn; the rest of the outline is transparent."""
    _cs, frame = _mid_frame(time_width=0.8)
    lower, upper = sweep_window(frame)
    assert lower > 0.0 and upper < 1.0, (
        "a 0.8-wide beam at mid-sweep must sit inside the outline, got "
        "(%s, %s) -- the whole frame is being lit" % (lower, upper))


def test_circumscribe_different_time_widths_draw_different_amounts():
    _small, small = _mid_frame(time_width=0.2)
    _big, big = _mid_frame(time_width=0.9)
    w_small = sweep_window(small)[1] - sweep_window(small)[0]
    w_big = sweep_window(big)[1] - sweep_window(big)[0]
    assert w_big > w_small, (
        "time_width had no effect on the mid-frame stroke width "
        "(0.2 -> %s, 0.9 -> %s)" % (w_small, w_big))


def test_circumscribe_default_render_is_unchanged():
    """Not passing ``time_width`` must keep the legacy progressive ``Create``."""
    cs, frame = _mid_frame()
    assert sweep_window(frame) is None, (
        "the default Circumscribe now draws a beam -- the existing default "
        "render (a progressive Create) must stay byte-identical")
    assert frame._vulkan_progress == pytest.approx(0.5, abs=1e-9), (
        "the default draw is no longer the plain Create progress sweep")
    assert isinstance(cs.animations[0], Create)


def test_circumscribe_time_width_signature_matches_ce_default():
    """``inspect.signature`` must still advertise CE's documented ``0.3``."""
    default = inspect.signature(Circumscribe).parameters["time_width"].default
    assert float(default) == pytest.approx(0.3)
    assert repr(default) == "0.3"


def test_circumscribe_ignores_time_width_in_fade_branches():
    """CE ignores ``time_width`` when ``fade_in``/``fade_out`` is set."""
    for kwargs in ({"fade_out": True}, {"fade_in": True},
                   {"fade_in": True, "fade_out": True}):
        cs = Circumscribe(Square(), time_width=0.9, **kwargs)
        cs.begin(0.0)
        cs.interpolate(0.0)
        cs.interpolate(0.5 * cs.run_time)
        assert sweep_window(cs._frame) is None, (
            "fade branch %s drew a beam; time_width must stay ignored there"
            % kwargs)


# --------------------------------------------------------------------------- #
# A21 -- ShowPassingFlash.remover
# --------------------------------------------------------------------------- #

def test_show_passing_flash_defaults_to_remover():
    assert ShowPassingFlash(Square()).remover is True, (
        "the default must keep the historic hard-wired value")


def test_show_passing_flash_remover_true_takes_the_mobject_out():
    scene = StubScene()
    mob = Square()
    scene.add(mob)
    flash = ShowPassingFlash(mob, time_width=0.3)
    drive(flash)
    flash.clean_up_from_scene(scene)
    assert mob not in scene.mobjects, (
        "the default remover=True must still remove the flashed mobject")


def test_show_passing_flash_remover_false_keeps_the_mobject():
    scene = StubScene()
    mob = Square()
    scene.add(mob)
    flash = ShowPassingFlash(mob, time_width=0.3, remover=False)
    drive(flash)
    assert sweep_window(mob) is not None, "the sweep never ran"
    flash.clean_up_from_scene(scene)
    assert mob in scene.mobjects, (
        "remover=False still took the mobject out of the scene")


def test_show_passing_flash_remover_false_restores_the_full_stroke():
    """CE restores the whole path; a lingering (1, 1) window is empty."""
    from real_time_manim.vulkan_util import point_path_bounds

    scene = StubScene()
    mob = Square()
    scene.add(mob)
    flash = ShowPassingFlash(mob, time_width=0.3, remover=False)
    drive(flash)
    flash.clean_up_from_scene(scene)
    assert sweep_window(mob) is None, (
        "the sliding window is still parked on the mobject after clean-up")
    assert point_path_bounds(mob) == (0.0, 1.0), (
        "the mobject is kept but not drawn whole: %s" % (point_path_bounds(mob),))


# --------------------------------------------------------------------------- #
# A22 -- FadeIn inside AnimationGroup (the fade_in.py half)
# --------------------------------------------------------------------------- #

def test_fade_in_carries_every_mobject_it_was_given():
    """Presentation reads ``.mobject``/``.mobjects``/``get_all_mobjects()``."""
    a, b = Square(), Circle()
    fi = FadeIn(a, b, shift=UP)
    assert fi.mobject is a, "FadeIn only reports its first mobject"
    assert list(fi.mobjects) == [a, b]
    assert set(fi.get_all_mobjects()) >= {a, b}


def test_animation_group_ramps_its_fade_in_targets_from_zero_to_one():
    """The reported symptom: new objects must appear during the group."""
    old = Square().shift(LEFT * 2)
    new_a = Circle().shift(RIGHT)
    new_b = Triangle().shift(RIGHT * 2)
    group = AnimationGroup(FadeOut(old, shift=UP),
                           FadeIn(new_a, new_b, shift=UP), lag_ratio=0.0)
    samples = []
    group.begin(0.0)
    for i in range(0, 5):
        group.interpolate(i / 4.0 * group.run_time)
        samples.append((float(get_anim_opacity(old)),
                        float(get_anim_opacity(new_a)),
                        float(get_anim_opacity(new_b))))
    start, end = samples[0], samples[-1]
    assert start[0] == pytest.approx(1.0), "the fade-out source starts visible"
    assert start[1] == pytest.approx(0.0) and start[2] == pytest.approx(0.0), (
        "the fade-in targets start visible (never parked at 0)")
    assert end[1] == pytest.approx(1.0) and end[2] == pytest.approx(1.0), (
        "the fade-in targets never reach full opacity inside the group: %s"
        % (samples,))
    assert end[0] == pytest.approx(0.0), "the fade-out source must end hidden"
    # both targets move together, and the fade actually progresses
    for _old, a, b in samples:
        assert a == pytest.approx(b)
    assert samples[1][1] > start[1] and samples[-2][1] < end[1], (
        "the fade-in is not a ramp: %s" % (samples,))


def test_animation_group_reports_the_fade_in_targets_of_its_children():
    """``get_all_mobjects`` is the generic contract any presenter relies on."""
    new_a, new_b = Circle(), Triangle()
    group = AnimationGroup(FadeIn(new_a, new_b))
    assert set(group.get_all_mobjects()) >= {new_a, new_b}


# --------------------------------------------------------------------------- #
# A23 -- FadeTransformPieces residuals
# --------------------------------------------------------------------------- #

def _pieces_scenario():
    """Source group + target group, ghost copies presented as the play does."""
    scene = StubScene()
    src = VGroup(Square(), Circle()).shift(LEFT * 2)
    tgt = VGroup(Circle(), Triangle()).shift(RIGHT * 2)
    scene.add(src)
    pieces = FadeTransformPieces(src, tgt)
    pieces.begin(0.0)
    # PlayMixin._present_detached_animated adds every piece's morph ghost as a
    # scene root (RTM paints only the scene tree).
    for sub in pieces.animations:
        ghost = getattr(sub, "_ghost", None)
        if ghost is not None:
            scene.add(ghost)
    assert any(g is not None for g in (s._ghost for s in pieces.animations)), (
        "test premise: FadeTransformPieces builds no ghosts")
    # run to the end the way play() does (evaluate to run_time, then clean up)
    pieces.interpolate(pieces.run_time)
    return scene, src, tgt, pieces


def _ghosts_of(pieces):
    return [s._ghost for s in pieces.animations if s._ghost is not None]


def test_pieces_cleanup_removes_every_ghost_copy():
    scene, src, tgt, pieces = _pieces_scenario()
    ghosts = _ghosts_of(pieces)
    assert all(g in scene.mobjects for g in ghosts), (
        "the test premise failed: the ghosts were never presented")
    pieces.clean_up_from_scene(scene)
    left = [g for g in ghosts if g in scene.mobjects]
    assert not left, (
        "FadeTransformPieces left %d ghost copy(ies) of the target in the "
        "scene -- a later FadeOut cannot dim them (wiki 05-淡出淡入式变换)"
        % len(left))


def test_pieces_cleanup_does_not_depend_on_the_group_recursion():
    """AnimationGroup.clean_up_from_scene lives in another module: self-sufficient."""
    scene, src, tgt, pieces = _pieces_scenario()
    ghosts = _ghosts_of(pieces)
    original = AnimationGroup.clean_up_from_scene
    AnimationGroup.clean_up_from_scene = lambda self, scene_: None
    try:
        pieces.clean_up_from_scene(scene)
    finally:
        AnimationGroup.clean_up_from_scene = original
    assert not any(g in scene.mobjects for g in ghosts), (
        "with the group's recursion disabled the ghosts still stayed: the "
        "Pieces clean-up must remove them itself")
    assert tgt in scene.mobjects, (
        "with the group's recursion disabled the target never entered the "
        "scene, so nothing of the crossfade would be visible")


def test_pieces_cleanup_presents_the_target_as_one_root():
    scene, src, tgt, pieces = _pieces_scenario()
    piece_targets = [s.target_mobject for s in pieces.animations]
    pieces.clean_up_from_scene(scene)
    assert tgt in scene.mobjects, "the target group never entered the scene"
    detached = [tm for tm in piece_targets if tm in scene.mobjects]
    assert not detached, (
        "the piece targets are still detached roots (%d) -- FadeOut(target) "
        "cannot dim them as one object" % len(detached))
    for tm in piece_targets:
        assert effective_alpha(scene, tm) == pytest.approx(1.0), (
            "a piece target is not visible after the crossfade")


def test_a_later_fade_out_dims_the_whole_target():
    """The reported symptom: 'target copy stays, FadeOut cannot remove it'."""
    scene, src, tgt, pieces = _pieces_scenario()
    pieces.clean_up_from_scene(scene)

    fade = FadeOut(tgt)
    fade.begin(0.0)
    fade.interpolate(0.0)
    fade.interpolate(fade.run_time)

    for sub in tgt.submobjects:
        alpha = effective_alpha(scene, sub)
        assert alpha is not None and alpha == pytest.approx(0.0, abs=1e-9), (
            "FadeOut could not dim the transformed target: submobject alpha "
            "is still %s (it was a detached root, not part of the group)"
            % alpha)


def test_pieces_cleanup_leaves_no_stale_root_copy():
    """After clean-up the scene holds exactly the source + the target."""
    scene, src, tgt, pieces = _pieces_scenario()
    ghosts = _ghosts_of(pieces)
    pieces.clean_up_from_scene(scene)
    roots = scene.mobjects
    assert len(roots) == 2, (
        "expected the source and the target as the only roots, got %s"
        % [type(m).__name__ for m in roots])
    assert src in roots and tgt in roots
    assert not any(g in roots for g in ghosts)
    assert effective_alpha(scene, src) == pytest.approx(0.0), (
        "the transformed source must not stay visible")


def test_pieces_keeps_its_source_reference():
    """docs/BUG_REPORT.md H3: ``AnimationGroup.__init__`` clobbered it."""
    src = VGroup(Square(), Circle())
    tgt = VGroup(Circle(), Triangle())
    pieces = FadeTransformPieces(src, tgt)
    assert pieces.mobject is src, (
        "FadeTransformPieces.mobject is %r -- the source group is lost"
        % (pieces.mobject,))
    assert src in pieces.get_all_mobjects()


def test_whole_fade_transform_has_no_cleanup_residual():
    """Same-family check for the un-grouped form (wiki 05, same page)."""
    scene = StubScene()
    src = Square().shift(LEFT * 2)
    tgt = Circle().shift(RIGHT * 2)
    scene.add(src)
    ft = FadeTransform(src, tgt)
    ft.begin(0.0)
    if ft._ghost is not None:
        scene.add(ft._ghost)
    ft.interpolate(ft.run_time)
    ft.clean_up_from_scene(scene)

    assert src not in scene.mobjects, "the source was not removed"
    assert ft._ghost is None or ft._ghost not in scene.mobjects, (
        "FadeTransform left its morph ghost in the scene")
    assert tgt in scene.mobjects, "the target never entered the scene"
    assert get_anim_opacity(tgt) == pytest.approx(1.0)
