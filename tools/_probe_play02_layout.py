"""Probe: layout-level A/B of the text strings on wiki page 02-play与wait参数.

The page's two demo sources differ ON PURPOSE in four strings
(`win.play` vs `self.play`).  Both renderers lay text out with the same
manimpango pipeline (RTM vendors ManimCE 0.21.0 and reuses its `Text`), so
any horizontal drift between the two videos must come from these string
differences (they are centred -> a width delta `d` shifts the shared prefix
by -d/2 and the shared tail by +d/2) or from rasterisation.

Prints, per line: string widths, the induced half-width shift in screen
pixels (1 unit = h/8 = 135 px at 1080p), and the per-glyph x drift of the
shared prefix / shared suffix.

Measured result (current workspace, bundled manimpango layout)
--------------------------------------------------------------
For all four differing lines the shared affix drift is a PERFECTLY RIGID
block (min == max == mean to 3 decimals), equal to half the width delta:

    title f42  width delta -7.42 px -> shared prefix +3.711 px
    l1    f30  width delta -7.43 px -> shared prefix +3.714 px
    l2    f30  IDENTICAL -> delta 0.000, drift 0.000 (control)
    l3    f30  width delta -7.43 px -> shared prefix +3.714 px
    l4    f30  width delta -7.43 px -> shared prefix +3.714 px
    txt   f30  IDENTICAL -> delta 0.000, drift 0.000 (control)

The videos read 3.79-3.88 px vs the layout's 3.71-3.74 px.  The ~0.1 px
gap is not an RTM bug: `self` renders marginally wider in the build that
produced the checked-in CE video than in the current workspace's
manimpango, which is the expected signature of a font-metric/hinting delta
between two Pango versions -- not a placement error.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import real_time_manim  # noqa: E402,F401  (installs the vendored manim)
from manim import Text  # noqa: E402

SCALE = 1080 / 8.0  # px per manim unit at 1920x1080

PAIRS = [
    ("title f42",
     "02-Scene.play / wait 参数（win.play 等价）",
     "02-Scene.play / wait 参数（self.play 等价）"),
    ("l1    f30",
     "win.play(Create(sq), FadeIn(ci, scale=0.5),",
     "self.play(Create(sq), FadeIn(ci, scale=0.5),"),
    ("l2    f30 (identical control)",
     "         run_time=1.6, rate_func=linear)   # 逐个 setattr",
     "         run_time=1.6, rate_func=linear)   # 逐个 setattr"),
    ("l3    f30",
     "win.play(*[FadeIn(m, shift=DOWN) for m in dots])",
     "self.play(*[FadeIn(m, shift=DOWN) for m in dots])"),
    ("l4    f30",
     "win.play(Wait(1.2))   #  ≡  self.wait(1.2)",
     "self.play(Wait(1.2))   #  ≡  self.wait(1.2)"),
    ("txt   f30 (identical control)",
     "静止 1.2 秒",
     "静止 1.2 秒"),
]


def common_affix(a, b):
    """(prefix_len, suffix_len) of the longest common prefix / suffix."""
    k = 0
    while k < len(a) and k < len(b) and a[k] == b[k]:
        k += 1
    m = 0
    while m < len(a) - k and m < len(b) - k and a[-1 - m] == b[-1 - m]:
        m += 1
    return k, m


def glyph_xs(text, font_size):
    """x centre of each glyph submobject, in manim units."""
    t = Text(text, font_size=font_size)
    xs = [float(sub.get_center()[0]) for sub in t.submobjects]
    return float(t.get_left()[0]), float(t.get_right()[0]), xs


def glyph_index_for_char(text, char_idx):
    """Glyph (submobject) index of character `char_idx`, skipping spaces the
    way manim's Text does (a space consumes no submobject)."""
    return sum(1 for ch in text[:char_idx] if not ch.isspace())


def main():
    print(f"scale = {SCALE} px/unit (1920x1080)")
    for name, a, b in PAIRS:
        size = 42 if "f42" in name else 30
        la, ra, xa = glyph_xs(a, size)
        lb, rb, xb = glyph_xs(b, size)
        wa, wb = ra - la, rb - lb
        d_px = (wb - wa) * SCALE
        k, m = common_affix(a, b)
        print(f"\n=== {name} ===")
        print(f"  rtm width {wa*SCALE:8.3f} px   ce width {wb*SCALE:8.3f} px   "
              f"delta(ce-rtm) = {d_px:+.3f} px")
        print(f"  centred: shared prefix shift {-d_px/2:+.3f} px, "
              f"shared suffix shift {+d_px/2:+.3f} px")
        print(f"  common prefix {k} chars, common suffix {m} chars")
        # head drift: first k chars (prefix), for both strings
        ia = glyph_index_for_char(a, k)
        ib = glyph_index_for_char(b, k)
        nhead = min(ia, ib)
        if nhead:
            dr = [(xb[i] - xa[i]) * SCALE for i in range(nhead)]
            print(f"  head drift px (n={nhead}): min {min(dr):+.3f} "
                  f"max {max(dr):+.3f}  mean {sum(dr)/len(dr):+.3f}")
        # tail drift: last m chars (suffix)
        ja = glyph_index_for_char(a, len(a) - m) if m else len(xa)
        jb = glyph_index_for_char(b, len(b) - m) if m else len(xb)
        ntail = min(len(xa) - ja, len(xb) - jb)
        if ntail:
            dr = [(xb[len(xb) - ntail + i] - xa[len(xa) - ntail + i]) * SCALE
                  for i in range(ntail)]
            print(f"  tail drift px (n={ntail}): min {min(dr):+.3f} "
                  f"max {max(dr):+.3f}  mean {sum(dr)/len(dr):+.3f}")


if __name__ == "__main__":
    main()
