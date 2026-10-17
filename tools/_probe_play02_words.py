"""Probe: where does the constant (font-size independent) width delta between
`win.` and `self` come from?  Dumps the cached Pango SVGs and the resulting
mobject geometry for the two words at several font sizes."""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import real_time_manim  # noqa: E402,F401
from manim import Text  # noqa: E402
from manim.mobject.text.text_mobject import (  # noqa: E402
    TEXT2SVG_ADJUSTMENT_FACTOR, TEXT_MOB_SCALE_FACTOR)

SCREEN_PX_PER_SVG_PX = TEXT_MOB_SCALE_FACTOR * (1080 / 8.0)
print(f"TEXT2SVG_ADJUSTMENT_FACTOR={TEXT2SVG_ADJUSTMENT_FACTOR}  "
      f"TEXT_MOB_SCALE_FACTOR={TEXT_MOB_SCALE_FACTOR}  "
      f"screen px per svg px = {SCREEN_PX_PER_SVG_PX}")

WORDS = ["win.", "self", "w", "i", "n", ".", "s", "e", "l", "f",
         "win.play", "self.play"]
for size in (30, 42, 60, 96, 144):
    print(f"\n=== font_size {size} (svg em = {size/TEXT2SVG_ADJUSTMENT_FACTOR:.4f} px) ===")
    widths = {}
    for wd in WORDS:
        t = Text(wd, font_size=size)
        w_units = float(t.get_right()[0] - t.get_left()[0])
        widths[wd] = w_units * 135.0     # ink extent in screen px
    base = None
    for wd in WORDS:
        w = widths[wd]
        if base is None:
            base = w
        print(f"  {wd!r:12s} ink {w:9.4f} screen px = "
              f"{w/SCREEN_PX_PER_SVG_PX:9.4f} svg px")
    print(f"  [win.] - [self]        = {widths['win.']-widths['self']:+9.4f} screen px "
          f"= {(widths['win.']-widths['self'])/SCREEN_PX_PER_SVG_PX:+9.4f} svg px")
    print(f"  [win.play] - [self.play] = {widths['win.play']-widths['self.play']:+9.4f} screen px "
          f"= {(widths['win.play']-widths['self.play'])/SCREEN_PX_PER_SVG_PX:+9.4f} svg px")
