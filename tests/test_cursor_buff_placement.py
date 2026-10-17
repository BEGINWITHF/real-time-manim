"""Regression test: the typing caret must sit ``buff`` from the last glyph.

Report: wiki ``03-动画/文字与数字/01b-带光标打字`` -- "光标过于偏右" (the caret
drifted too far right).

manim positions it with ``cursor.next_to(last_glyph, RIGHT, buff=self.buff)``,
which puts the caret's LEFT edge ``buff`` to the right of the glyph's right
edge.  RTM did ``move_to(glyph_center).shift(glyph_width / 2 + buff * 4)``,
whose ``* 4`` pushed the caret ``0.48`` right of the glyph (instead of 0.12)
and ignored the caret's own width.

Pure Python: no window, no GPU.
"""
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import RIGHT, Rectangle, Text

from real_time_manim.animations.base import place_cursor_after
from real_time_manim.animations.type_with_cursor import TypeWithCursor
from real_time_manim.animations.untype_with_cursor import UntypeWithCursor


def _manim_position(glyph, width, buff):
    """Where manim would park the caret (its own next_to, computed on a twin)."""
    ref = Rectangle(width=width, height=1.0).move_to(glyph)
    ref.next_to(glyph, RIGHT, buff=buff)
    return ref.get_center()


@pytest.mark.parametrize("buff,width", [(0.1, 0.5), (0.12, 0.14), (0.0, 0.3)])
def test_place_cursor_after_matches_manim_next_to(buff, width):
    text = Text("Inserting")
    glyph = text[3]
    cursor = Rectangle(width=width, height=1.0).move_to(glyph)
    place_cursor_after(cursor, glyph, buff)
    assert cursor.get_center() == pytest.approx(_manim_position(glyph, width, buff))


def test_place_cursor_after_is_not_the_old_fours_times_buff():
    """The old formula put the caret 0.29 further right than manim does."""
    text = Text("Inserting")
    glyph = text[3]
    cursor = Rectangle(width=0.14, height=1.0).move_to(glyph)
    place_cursor_after(cursor, glyph, 0.12)
    old = glyph.get_center().copy()
    old[0] += glyph.get_width() / 2 + 0.12 * 4
    assert cursor.get_center()[0] < old[0]


@pytest.mark.parametrize("cls", [TypeWithCursor, UntypeWithCursor])
def test_animation_caret_lands_on_the_manim_spot(cls):
    """``update_submobject_list``/``begin`` must leave the caret where CE does."""
    text = Text("Inserting")
    glyph = text[3]
    cursor = Rectangle(width=0.14, height=1.0).move_to(text[0])
    anim = cls(text, cursor, buff=0.12, keep_cursor_y=False)
    if cls is TypeWithCursor:
        anim.begin(0.0)
        anim.update_submobject_list(4)
        last = text[3]
    else:
        # Untype starts with the whole word typed, so its caret begins after
        # the LAST letter (manim's RemoveTextLetterByLetter does the same).
        anim.begin(0.0)
        last = text[-1]
    assert cursor.get_center()[0] == pytest.approx(
        _manim_position(last, 0.14, 0.12)[0])
