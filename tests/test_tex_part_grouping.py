"""Tests that a multi-string `Tex` splits its glyphs per tex_string.

The core bug this guards against: manim wraps every tex_string in
``\\special{dvisvgm:raw <g id='uniqueNNN'>}`` so dvisvgm emits one named SVG
group per string, and MathTex hands each group to its own MathTexPart.  RTM used
to strip those tags and split the glyph list by *character weight* instead,
which cannot know how many glyphs a string really produced (spaces and ``\\\\``
contribute nothing, ``fi`` is a single ligature glyph, ...).

For BulletedList's four items the weights 19/15/14/18 over 53 glyphs put the
first boundary at 15 instead of 16, so the trailing "s" of "changelog entries"
landed in the next part: the dot for that part was placed left of the stray "s"
and the first bullet wrapped onto a line of its own.

These tests need LaTeX (they skip when it is missing).
"""
import shutil
import sys
from pathlib import Path

import pytest

# Ensure project root is importable so `real_time_manim.*` resolves.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import real_time_manim.vulkan_bind  # noqa: F401  (registers the MathTex monkeypatch)
from manim import Tex

pytestmark = pytest.mark.skipif(
    shutil.which("latex") is None, reason="LaTeX is not installed"
)

# The items of the demo scene's BulletedList: "entries" ends in a letter that
# used to be the glyph handed to the next part.
ITEMS = [
    "changelog entries\\\\",
    "caching fixes\\\\",
    "Typst markup\\\\",
    "plugin discovery\\\\",
]


def glyphs(mobj):
    """Every point-bearing leaf glyph under `mobj` (a Tex or one of its parts)."""
    out = []
    for sub in mobj.submobjects:
        if sub.submobjects:
            out.extend(glyphs(sub))
        elif sub.has_points():
            out.append(sub)
    return out


def test_tex_keeps_one_svg_group_per_tex_string():
    """The dvisvgm group tags that carry the exact glyph -> string mapping.

    The group has to come from the SVG.  A fallback that cannot find it
    synthesises a MathTexPart per string instead -- which is exactly the thing
    that has to be told apart here, because a synthesised part only knows a
    proportional guess of where the string ended.
    """
    from manim import VGroup

    tex = Tex(*ITEMS, tex_environment=None)
    ids = [tex_string_id for _, tex_string_id in tex._main_matches]
    assert len(ids) == len(ITEMS)
    for tex_string_id in ids:
        group = tex.id_to_vgroup_dict.get(tex_string_id)
        assert group is not None, f"no SVG group for {tex_string_id}"
        assert group.submobjects, f"SVG group {tex_string_id} is empty"
        # Not a synthesised MathTexPart: without the SVG's named group a
        # fallback builds one per string from a proportional guess of where
        # the string ended -- the guess this bug came from.
        assert isinstance(group, VGroup), (
            f"{tex_string_id} is a synthesised part, not the SVG's named group"
        )


def test_each_part_gets_exactly_its_own_glyphs():
    """A part must hold the glyphs its own string produced -- no more, no less.

    Each string is also rendered on its own as the oracle, which is immune to
    the grouping: a lone string has a single part holding every glyph.
    """
    tex = Tex(*ITEMS, tex_environment=None)
    expected = [
        len(glyphs(Tex(item, tex_environment=None))) for item in ITEMS
    ]

    parts = list(tex.submobjects)
    assert len(parts) == len(ITEMS)
    assert [len(glyphs(part)) for part in parts] == expected


def test_no_glyph_of_a_later_row_is_left_in_an_earlier_part():
    """The lost-glyph symptom, checked geometrically.

    Every row of this list is its own baseline, so the glyphs a part collected
    must sit within one line-height of each other; the old split left the last
    letter of row one in row two's part, a whole line below the rest.
    """
    tex = Tex(*ITEMS, tex_environment=None)
    for part in tex.submobjects:
        ys = [float(g.get_center()[1]) for g in glyphs(part)]
        assert max(ys) - min(ys) < 0.35, (
            f"part {part.tex_string!r} spans lines: y {min(ys):.3f}..{max(ys):.3f}"
        )
