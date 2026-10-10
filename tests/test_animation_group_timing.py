"""``AnimationGroup`` must run on the timeline's clock, and draw its children.

`real_time_manim.animations.animation_group` had two defects, both visible
without any GPU work:

1. **Children never advanced.** The group began each RTM child with
   ``time.time()`` and then handed it manim's *normalised* alpha, but RTM's
   animations read ``alpha = (t - start_time) / run_time`` -- so the value was
   always negative and clamped to 0:

       RTM Create alone             AddLine=684  progress=1.0
       AnimationGroup(RTM Create)   AddLine=0    progress=0.0   <- nothing

   ``Succession`` has always done it the right way (absolute time), which is
   why it was fine.

2. **The group finished early.** ``timeline.evaluate_animation`` passes
   *elapsed seconds*, but ``interpolate`` treated any ``t < 100`` as a
   normalised alpha (``group_time = rate_func(t) * total``), so a 1.5 s group
   ran its whole schedule in 1.0 s and the rest of the play was frozen frames.

Plus the group's default ``rate_func`` was the shared Animation's ``smooth``
where manim's ``AnimationGroup`` defaults to ``linear`` -- easing the group on
top of every child's own easing, so even a correctly clocked group ran at a
different pace from CE.  ``Succession`` had the same wrong default (CE's
``Succession`` is ``rate_func=linear`` too).

Run with::

    python -X utf8 -m pytest tests/test_animation_group_timing.py -q
"""

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

try:
    import real_time_manim.vulkan_bind as vb
    from manim import RIGHT, Circle, Create as ManimCreate, Scene, Square, VGroup
    from real_time_manim.animations.succession import Succession
    from real_time_manim.vulkan_bind import AnimationGroup, Create, FadeIn
except Exception as e:                                  # pragma: no cover
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


class Recorder(object):
    """Stands in for the native DLL and keeps every submitted call."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


# --------------------------------------------------------------------------- #
# the clock
# --------------------------------------------------------------------------- #

def _group_of_two(lag=0.5):
    a, b = Square(), Square()
    group = AnimationGroup(Create(a, run_time=1.0),
                           Create(b, run_time=1.0), lag_ratio=lag)
    group.begin(0.0)
    return group, a, b


def test_group_runs_on_elapsed_seconds_not_on_normalised_alpha():
    """1.5 s of schedule must still be running at t = 1.0 s.

    The old code mapped ``t`` straight into ``rate_func(t) * total``, so at
    t = 1.0 ``rate_func(1.0) == 1`` handed the group its *end* and child b --
    which manim starts at 0.5 s -- was already finished.
    """
    group, a, b = _group_of_two()
    assert group.run_time == pytest.approx(1.5)
    group.interpolate(1.0)
    assert b._vulkan_progress < 1.0 - 1e-6, (
        "child b was still due until t=1.5 s but finished at t=1.0 s -- the "
        "group read elapsed seconds as a normalised alpha")
    assert a._vulkan_progress == pytest.approx(1.0)


def test_second_child_starts_at_its_own_lag_time():
    group, a, b = _group_of_two(lag=0.5)
    group.interpolate(0.4)                     # before b's start (0.5 s)
    assert '_vulkan_progress' not in b.__dict__, (
        "b was interpolated before its start time: %r" % b._vulkan_progress)
    group.interpolate(1.0)
    # b has run 0.5 s of its 1.0 s, through its own smooth rate function
    assert b._vulkan_progress == pytest.approx(0.5, abs=0.05)


def test_group_reaches_the_final_state_at_the_end_of_its_run_time():
    group, a, b = _group_of_two()
    group.interpolate(1.5)
    assert a._vulkan_progress == pytest.approx(1.0)
    assert b._vulkan_progress == pytest.approx(1.0)


def test_default_rate_function_is_linear_like_manims():
    """manim's AnimationGroup: ``rate_func: ... = linear`` (composition.py)."""
    group = AnimationGroup(Create(Square(), run_time=1.0))
    assert group.rate_func(0.25) == pytest.approx(0.25)
    assert group.rate_func(0.5) == pytest.approx(0.5)


def test_children_begin_on_the_groups_clock():
    """``begin()`` must stamp the child's own start, not the wall clock."""
    group, _a, _b = _group_of_two(lag=0.5)
    group.interpolate(0.6)                     # b began at 0.5 s
    start = group.animations[1].start_time
    assert start == pytest.approx(0.5), (
        "b's start_time is %r -- (t - start_time)/run_time can never leave 0 "
        "on a later absolute-time step" % start)


def test_manim_children_still_get_normalised_alpha():
    """manim's animations take alpha, not seconds -- keep both conventions."""
    sq = Square()
    child = ManimCreate(sq, run_time=1.0)
    group = AnimationGroup(child)
    group.begin(0.0)
    seen = []
    real = child.interpolate
    child.interpolate = lambda alpha, _r=real: (seen.append(alpha), _r(alpha))[1]
    group.interpolate(0.25)
    assert seen and seen[-1] == pytest.approx(0.25), seen


def test_a_manim_wrapper_passing_alpha_still_drives_the_group():
    """``ChangeSpeed`` calls ``self.anim.interpolate(alpha)`` -- manim's alpha.

    It also drives ``begin()`` with no argument, so our own ``start_time`` is
    a wall-clock stamp while ``t`` is a 0..1 alpha.  Reading that as elapsed
    time (the naive fix for the seconds bug) would make the group time travel
    backwards and freeze -- which is exactly what scene 59 would have done.
    """
    import time

    from manim import ChangeSpeed, linear

    a, b = Square(), Square()
    inner = AnimationGroup(Create(a, run_time=1.0),
                           Create(b, run_time=1.0), lag_ratio=0.5)
    wrapper = ChangeSpeed(inner, speedinfo={0.0: 1.0, 1.0: 1.0},
                          rate_func=linear)
    wrapper.begin()                        # -> inner.begin() -> wall clock
    assert inner.start_time > 1e6, "test setup: expected a wall-clock origin"

    wrapper.interpolate(0.5)               # manim's normalised alpha
    assert a._vulkan_progress > 0.0, "the group never left t=0"
    assert b._vulkan_progress > 0.0, (
        "child b (starts at 0.5 s of a 1.5 s group) was never begun")
    assert a._vulkan_progress > b._vulkan_progress

    wrapper.interpolate(1.0)
    assert a._vulkan_progress == pytest.approx(1.0)
    assert b._vulkan_progress == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# Succession: same wrong default rate_func as the group had
# --------------------------------------------------------------------------- #

def test_succession_default_rate_function_is_linear_like_manims():
    """manim's Succession: ``rate_func: ... = linear`` (composition.py)."""
    succ = Succession(Create(Square(), run_time=1.0))
    assert succ.rate_func(0.25) == pytest.approx(0.25)
    assert succ.rate_func(0.5) == pytest.approx(0.5)


def test_succession_paces_its_children_linearly():
    """The default must actually change the clock, not just the attribute.

    Two 1.0 s children (2.0 s total) stepped at t = 0.6: with ``linear`` the
    schedule has run 0.6 s, so child 0 -- manim's, which receives a
    normalised alpha -- is at 0.6 of itself.  With the old ``smooth``
    default it would be at smooth(0.3) ~= 0.24: every child eased twice,
    once by the Succession and once by itself.
    """
    a, b = Square(), Square()
    succ = Succession(ManimCreate(a, run_time=1.0),
                      ManimCreate(b, run_time=1.0))
    succ.begin(0.0)
    seen = []
    child = succ.animations[0]
    real = child.interpolate
    child.interpolate = lambda alpha, _r=real: (seen.append(alpha), _r(alpha))[1]
    succ.interpolate(0.6)
    assert seen, "child 0 was never interpolated"
    assert seen[-1] == pytest.approx(0.6), (
        "child 0 got alpha=%r; a linear 2.0 s Succession stepped at t=0.6 "
        "must put its active child at 0.6 (smooth would give ~0.24)" % seen[-1])


# --------------------------------------------------------------------------- #
# what reaches the GPU
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def window():
    try:
        w = vb.MLWindow(1920, 1080, hidden=True)
    except Exception as e:                              # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield w
    try:
        w.close()
    except Exception:
        pass


def test_create_inside_an_animation_group_is_actually_drawn(window):
    """The headline defect: `AnimationGroup(Create(...))` drew nothing."""
    vg = VGroup(*[Square().shift(i * 3.0 * RIGHT) for i in range(3)])
    scene = Scene()
    scene.setup()
    scene.add(vg)
    rec = Recorder()
    real = window.dll
    window.dll = rec
    try:
        window.scene = scene
        window.play(AnimationGroup(Create(vg, run_time=1.0)), run_time=1.0)
        strokes = [a for n, a in rec.calls if n == 'AddLine']
    finally:
        window.dll = real
    assert strokes, (
        "AnimationGroup(Create) emitted no geometry at all -- the group "
        "handed its child a normalised alpha against a wall-clock start_time")
    assert vg._vulkan_progress == pytest.approx(1.0)


def test_group_play_backed_by_the_timeline_ends_finished(window):
    """Through `play()`: nothing may be left mid-draw when the play ends."""
    vg = VGroup(*[Square().shift(i * 3.0 * RIGHT) for i in range(3)])
    scene = Scene()
    scene.setup()
    scene.add(vg)
    real = window.dll
    window.dll = Recorder()
    try:
        window.scene = scene
        window.play(AnimationGroup(Create(vg, run_time=1.0),
                                   FadeIn(Circle(), run_time=1.0),
                                   lag_ratio=0.5), run_time=1.5)
    finally:
        window.dll = real
    assert vg._vulkan_progress == pytest.approx(1.0), (
        "the group stopped at %r: the timeline's exclusive frame end still "
        "has to be resolved to the group's final state"
        % getattr(vg, '_vulkan_progress', None))
