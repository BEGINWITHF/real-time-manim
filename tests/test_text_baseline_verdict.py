"""Regression: a word's baseline verdict is decided once, never re-decided.

``sync`` rebuilds ``_row_text_ids`` from ``scene.mobjects`` every frame, and a
row-mate enters that list whenever ITS animation starts.  The draw-time offset
used to be recomputed on any frame where ``_baseline_dy`` was still unset, so
the row could form *under a word that was already standing still* and push it.

Measured on ``MatchersAndBooleanOps``: ``highlight me`` is the only Text root
for frames 1-36 (row empty -> drawn unshifted), ``cross me out`` enters the
scene at frame 37, the two overlap on one line, the row forms -- and the offset
landed that same frame.  The word jumped 6 px (0.0451 units) after 0.6 s of
being still, and then sat 7 px away from where CE draws it, because CE applies
no such shift at all.

Pure Python: ``MLWindow.__new__`` skips ``__init__``, so no DLL and no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import pytest
from manim import Text

from real_time_manim.state import get_anim_opacity, set_anim_opacity
from real_time_manim.vulkan_bind import MLWindow

# Measured values of the demo suite (font_size=30 @1080p: 135 px per unit).
HIGHLIGHT_DY = -0.0451172


def _bare_window():
    """An MLWindow instance without running __init__ (no DLL, no window)."""
    win = MLWindow.__new__(MLWindow)
    win._row_text_ids = set()
    return win


def _word(text):
    """A Text at rest -- 1.0 so a recycled id can't leak another test's fade."""
    mob = Text(text, font_size=30)
    set_anim_opacity(mob, 1.0)
    return mob


def test_word_drawn_off_a_row_is_pinned_to_zero():
    win, word = _bare_window(), _word("highlight me")
    assert win._text_baseline_for(word) == 0.0
    assert word._baseline_dy == 0.0          # a zero is a verdict too


def test_row_forming_later_does_not_move_a_drawn_word():
    """The bug: 'cross me out' joins the scene long after 'highlight me'."""
    win, word = _bare_window(), _word("highlight me")
    assert win._text_baseline_for(word) == 0.0      # frames 1-36, no row yet

    win._row_text_ids = {id(word), id(_word("cross me out"))}   # frame 37
    assert win._text_baseline_for(word) == 0.0      # verdict already in
    assert word._baseline_dy == 0.0


def test_word_first_drawn_on_a_row_keeps_its_offset():
    win, word = _bare_window(), _word("highlight me")
    win._row_text_ids = {id(word), id(_word("cross me out"))}
    dy = win._text_baseline_for(word)
    assert dy == pytest.approx(HIGHLIGHT_DY, abs=1e-4)

    win._row_text_ids = set()               # row dissolves: still no movement
    assert win._text_baseline_for(word) == dy
    assert word._baseline_dy == pytest.approx(HIGHLIGHT_DY, abs=1e-4)


def test_each_word_of_a_row_gets_its_own_offset():
    """'highlight me' carries a descender, 'cross me out' barely: the offset
    is per word (that is the whole point of aligning the baselines)."""
    win, a, b = _bare_window(), _word("highlight me"), _word("cross me out")
    win._row_text_ids = {id(a), id(b)}
    assert win._text_baseline_for(a) == pytest.approx(HIGHLIGHT_DY, abs=1e-4)
    assert win._text_baseline_for(b) == pytest.approx(-0.000879, abs=1e-4)
    assert a._baseline_dy != b._baseline_dy


def test_mid_fade_does_not_lock_a_verdict():
    """A fading word's geometry is transient: return 0.0 but do NOT cache it,
    so the row is still evaluated once the word is at rest."""
    win, word = _bare_window(), _word("highlight me")
    mate = _word("cross me out")
    win._row_text_ids = {id(word), id(mate)}

    set_anim_opacity(word, 0.5)
    try:
        assert get_anim_opacity(word) == 0.5
        assert win._text_baseline_for(word) == 0.0
        assert not hasattr(word, "_baseline_dy")    # nothing decided yet
    finally:
        set_anim_opacity(word, 1.0)

    assert win._text_baseline_for(word) == pytest.approx(HIGHLIGHT_DY, abs=1e-4)
