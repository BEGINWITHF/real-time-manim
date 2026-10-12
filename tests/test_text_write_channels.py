"""Regression: a Written Text must still carry every channel of the glyph path.

``Write`` leaves ``_letter_alphas`` on the mobject -- ``_glyph_rgb`` relies on
that, and ``vulkan_bind._send_impl`` routes any mobject carrying it through
``vulkan_text._send_text_write`` instead of ``_send_vmobject``.  That writer
used to send raw screen coordinates only, so a Written word

  * dropped the Approach-A baseline shift (``_baseline_dy``, applied by
    ``_send_vmobject`` at vulkan_text.py:542) and sat a whole row-shift away
    from its unwritten row-mates;
  * dropped the grow pair (``_grow_scale`` / ``_grow_point``, applied at
    vulkan_text.py:537), so GrowFromCenter did nothing to it;
  * read ``letter_alphas.get(i, 0.0)``, so the extra submobjects a
    ``Transform``'s ``align_data`` pads into the shorter Text were drawn
    INVISIBLE, where CE draws the target line in full.

Pure Python: ``MLWindow.__new__`` skips ``__init__``, and a recording ``dll``
catches the calls instead of the GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import numpy as np  # noqa: E402
from manim import Text  # noqa: E402

from real_time_manim.vulkan_bind import MLWindow  # noqa: E402

W, H = 1920, 1080
PX_PER_UNIT = H / 8.0          # manim_to_screen's scale at 1080p: 135 px
HIGHLIGHT_DY = -0.0451172      # measured on 'highlight me' @ font_size=30


class _RecordingDLL:
    """Stands in for vulkan_core: keeps the screen-space glyphs it is sent."""

    def __init__(self):
        self.paths = []

    def AddBezierPath(self, arr, n, *rest):
        pts = [(arr[3 * i], arr[3 * i + 1]) for i in range(n)]
        self.paths.append(pts)


def _window():
    win = MLWindow.__new__(MLWindow)
    win.dll = _RecordingDLL()
    return win


def _write(win, mob, alphas=None):
    """Send ``mob`` through the Write path; return one (x, y) list per glyph."""
    if alphas is None:
        alphas = {i: 1.0 for i in range(len(mob.submobjects))}
    win.dll.paths = []
    win._send_text_write(mob, alphas, W, H, 1.0)
    return list(win.dll.paths)


def _widths(paths):
    return [max(p[0] for p in pts) - min(p[0] for p in pts) for pts in paths]


def test_the_baseline_shift_reaches_a_written_word():
    word = Text("highlight me", font_size=30)
    win = _window()
    before = _write(win, word)
    assert before, "no glyph reached the writer: the test proves nothing"

    for sub in word.submobjects:
        sub._baseline_dy = HIGHLIGHT_DY
    after = _write(win, word)

    # screen y = cy - (y + dy) * s, so a negative dy lifts the glyph by |dy| * s
    expect = -HIGHLIGHT_DY * PX_PER_UNIT
    for old, new in zip(before, after):
        assert len(old) == len(new)
        old, new = np.array(old), np.array(new)
        assert np.allclose(new[:, 1] - old[:, 1], expect, atol=1e-3)
        assert np.allclose(new[:, 0] - old[:, 0], 0.0, atol=1e-3)


def test_the_grow_pair_reaches_a_written_word():
    word = Text("grow me", font_size=30)
    win = _window()
    before = _widths(_write(win, word))
    assert before and before[0] > 0

    word._grow_scale = 0.5
    word._grow_point = np.array(word.get_center())
    during = _widths(_write(win, word))

    assert np.allclose(np.array(during), np.array(before) * 0.5, atol=1e-3)


def test_glyphs_padded_in_by_a_transform_are_drawn():
    """`Transform(Text("ab"), Text("abcd"))` pads the short Text with copies of
    its last glyph; they have no entry in the map and used to vanish."""
    word = Text("ab", font_size=30)
    n = len(word.submobjects)
    assert n >= 2

    drawn = _write(_window(), word, alphas={0: 1.0})
    assert len(drawn) == n, "a glyph with no letter alpha was dropped"


def test_a_mid_write_prefix_still_hides_the_unwritten_letters():
    """The new default must not defeat the reveal: a partial map still gates."""
    word = Text("abcd", font_size=30)
    n = len(word.submobjects)
    drawn = _write(_window(), word, alphas={0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0})
    assert len(drawn) == n
    drawn_partial = _write(_window(), word,
                           alphas={i: (1.0 if i == 0 else 0.0) for i in range(n)})
    assert len(drawn_partial) == 1, "letters with alpha 0 must stay hidden"
