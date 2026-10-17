"""Regression test: ``FadeIn(..., shift=V)`` must travel BY ``V``, not against it.

Report: wiki ``03-动画/通用/02-play与wait参数`` -- "shift down 被展示成了 up".
Every ``FadeIn(m, shift=DOWN)`` in that page slid its mobject UP into place.

manim builds FadeIn's starting state in ``_Fade._create_faded_mobject``::

    direction_modifier = -1 if fadeIn and not self.point_target else 1
    faded_mobject.shift(self.shift_vector * direction_modifier)

so the mobject starts at ``final - shift`` and moves BY ``shift``: with
``shift=DOWN`` it enters from ABOVE and travels downwards.  RTM added
``+shift * (1 - alpha)`` -- the exact opposite direction.  ``FadeOut`` is
correct as it stands (manim uses ``direction_modifier = +1`` there, i.e. the
mobject leaves BY ``shift``).

Also checks the end state: at ``alpha == 1`` the offset must be exactly zero
(the old ``alpha < 1.0`` guard skipped the last frame and left a residual).

Pure Python: no window, no GPU.
"""
import os
import sys

import numpy as np
import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import DOWN, LEFT, Square, UP

from real_time_manim.animations.fade_in import FadeIn
from real_time_manim.animations.fade_out import FadeOut


def _samples(anim, alphas):
    """Begin once, then read the mobject's centre at each alpha."""
    anim.begin(0.0)
    out = []
    for alpha in alphas:
        anim.interpolate(alpha)
        out.append(anim.mobject.get_center().copy())
    return out


def _alpha_state(anim, alpha):
    return _samples(anim, [alpha])[0]


def test_fade_in_starts_against_the_shift():
    mob = Square()
    final = mob.get_center().copy()
    anim = FadeIn(mob, shift=DOWN)
    start = _alpha_state(anim, 0.0)
    assert start == pytest.approx(final - DOWN), (
        "FadeIn(shift=DOWN) must start ABOVE the final spot (manim shifts the "
        "starting copy by -shift); it started below it")


def test_fade_in_moves_in_the_shift_direction():
    mob = Square()
    final = mob.get_center().copy()
    anim = FadeIn(mob, shift=DOWN)
    start, mid = _samples(anim, [0.0, 0.5])
    # halfway between the start (final - DOWN) and the final spot, and moving
    # DOWN (y decreasing) towards it
    assert start[1] > mid[1] > final[1], (start, mid, final)


def test_fade_in_ends_exactly_on_the_final_spot():
    mob = Square()
    final = mob.get_center().copy()
    anim = FadeIn(mob, shift=LEFT * 2)
    end = _alpha_state(anim, 1.0)
    assert end == pytest.approx(final), (
        "FadeIn must land exactly on the authored position at alpha 1")


def test_fade_in_matches_manims_starting_mobject():
    """Cross-check against manim's own FadeIn of the same mobject."""
    from manim import FadeIn as ManimFadeIn

    mob = Square()
    final = mob.get_center().copy()
    ours = _alpha_state(FadeIn(mob, shift=UP * 0.8 + LEFT * 0.4), 0.0)
    theirs = final - (UP * 0.8 + LEFT * 0.4)
    assert ours == pytest.approx(theirs)


def test_fade_out_still_leaves_by_the_shift():
    """Non-regression: FadeOut moves BY ``shift`` (manim uses +1 there)."""
    mob = Square()
    final = mob.get_center().copy()
    anim = FadeOut(mob, shift=UP)
    end = _alpha_state(anim, 1.0)
    assert end == pytest.approx(final + UP)


def test_target_position_still_overrides():
    """A ``target_position`` fade still starts AT the target (unchanged)."""
    mob = Square()
    target = np.array([2.0, -1.0, 0.0])
    anim = FadeIn(mob, target_position=target)
    assert _alpha_state(anim, 0.0) == pytest.approx(target)
