"""Regression: a dead mobject's animation verdict must not reach a new one.

``state._anim_opacity`` / ``_anim_rotation`` / ``_anim_rotation_delta`` were
keyed by ``id(mobject)`` and never cleaned.  CPython reuses ids, so once the
mobject that earned a verdict is freed the NEXT mobject allocated at that
address inherits it -- rendered invisible or rotated for the rest of its life.
Freed ``Transform`` targets are exactly such owners: ``vulkan_bind`` parks
``set_anim_opacity(target, 0.0)`` on every one of them.

Measured before the fix: park ``set_anim_opacity(t, 0.0)`` on a ``Text``,
delete it, then allocate fresh ``Text``s -- the id came back after ~123
allocations, and 24 of 400 allocations inherited the stale verdict.
"""
import gc
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from manim import Text  # noqa: E402

from real_time_manim import state  # noqa: E402


def test_a_dead_mobjects_verdict_does_not_reach_a_new_one():
    victim = Text("doomed")
    state.set_anim_opacity(victim, 0.0)
    state.set_anim_rotation(victim, 1.234)
    del victim
    gc.collect()

    leaked = []
    for i in range(400):
        mob = Text("fresh%d" % i)
        op, rot = state.get_anim_opacity(mob), state.get_anim_rotation(mob)
        if op != 1.0 or rot != 0.0:
            leaked.append((i, op, rot))
        if i % 50 == 0:
            del mob
            gc.collect()
    assert not leaked, "stale verdict(s) landed on a new mobject: %s" % (leaked[:3],)


def test_a_live_mobject_still_reads_its_own_verdict():
    """Weak keys must not cost the registry its live values."""
    mob = Text("alive")
    state.set_anim_opacity(mob, 0.25)
    state.set_anim_rotation(mob, 0.5)
    state.set_anim_rotation_delta(mob, 0.125)
    try:
        assert state.get_anim_opacity(mob) == 0.25
        assert state.get_anim_rotation(mob) == 0.5
        assert state.get_anim_rotation_delta(mob) == 0.125
    finally:
        state.set_anim_opacity(mob, 1.0)
        state.set_anim_rotation(mob, 0.0)
        state.set_anim_rotation_delta(mob, 0.0)
    assert state.get_anim_rotation_delta(mob) == 0.0


def test_the_entry_dies_with_its_owner():
    """No unbounded growth: dropping the mobject drops the entry."""
    before = len(state._anim_opacity)
    mob = Text("ephemeral")
    state.set_anim_opacity(mob, 0.0)
    assert len(state._anim_opacity) == before + 1
    del mob
    gc.collect()
    assert len(state._anim_opacity) == before


def test_the_default_verdicts_survive():
    """An object that was never animated reads the documented defaults."""
    mob = Text("untouched")
    assert state.get_anim_opacity(mob) == 1.0
    assert state.get_anim_rotation(mob) == 0.0
    assert state.get_anim_rotation_delta(mob) == 0.0
