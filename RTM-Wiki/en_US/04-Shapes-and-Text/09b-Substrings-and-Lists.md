# MathTex part methods, lists and titles

Following on from [LaTeX](09-LaTeX.md): the colouring / fetching / opacity methods for formula parts, plus the LaTeX bulleted list and the page-header title. One sample per method, each changing every **fillable parameter** of that method once.

> **How parts are split**: the `{{ }}` marker only takes effect **within a single string argument**; `MathTex("{{x}}^2+{{y}}^2={{z}}^2")` actually splits into just two parts, `x` and `^2+{{y}}^2={{z}}^2` (consistent across both engines in testing). To colour or fetch by part, write each part as a **separate argument**: `MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2")`. Every sample below uses the latter form.

## Parameters

### `MathTex.set_color_by_tex`

```python
def set_color_by_tex(self, tex: str, color: ParsableManimColor, **kwargs) -> Self:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `tex` | `str` | required | the part text (must be **exactly equal** to that part's `tex_string`, e.g. `"x"`); the sample colours `x`/`y`/`z` in turn |
| `color` | `ManimColor` | required | the target colour; the same part can be coloured differently in different formulas (the sample's last formula chains `x→ORANGE`, `z→PURPLE` twice) |

#### Sample: colouring x / y / z in turn + chaining twice

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, MathTex, BulletedList, Title, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write, MED_LARGE_BUFF,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class ColorByTexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09b-set_color_by_tex", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— the same formula, each of the three coloured once (one "tex / color" pair each time) ——
        pairs = [("x", RED), ("y", GREEN), ("z", BLUE)]   # the "tex / color" parameters
        for i, (tex, col) in enumerate(pairs):
            eq = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=52)
            eq.set_color_by_tex(tex, col)   # the "tex = part text / color = target colour" parameters
            eq.move_to([-4.2 + i * 4.2, 0.9, 0])
            cap = Text('set_color_by_tex("%s")' % tex, font_size=18, color=GREY_B).next_to(eq, DOWN, buff=0.4)
            win.play(Write(eq), FadeIn(cap), run_time=0.6)   # colour x red, y green, z blue in turn

        # —— one part can be coloured differently in different formulas ——
        eq2 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=52)
        eq2.set_color_by_tex("x", ORANGE)   # the same "x", this time orange
        eq2.set_color_by_tex("z", PURPLE)   # once more, purple
        eq2.move_to([-1.6, -1.7, 0])
        cap2 = Text('x->ORANGE  z->PURPLE', font_size=18, color=GREY_B).next_to(eq2, DOWN, buff=0.35)
        win.play(Write(eq2), FadeIn(cap2), run_time=0.6)   # chained twice
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: set_color_by_tex_to_color_map —— colour many parts at once
```

What this code does: the same set of formulas is drawn three times, each colouring exactly one part (red `x`, green `y`, blue `z`), with the caption naming the `tex` used that time. The last formula calls `set_color_by_tex` twice in a row on **the same object**, turning `x` orange and `z` purple while `y` stays white—so it recolours in place and can be chained.

<video src="assets/RTM output/09b-Substrings-and-Lists-colorbytex.mp4" controls width="560"></video>

> Note: `tex` must be **exactly equal** to the part's `tex_string` (no substring matching and no tolerance for whitespace differences); colouring changes colour only, not geometry, so it does not affect `get_part_by_tex` lookups.

### `MathTex.set_color_by_tex_to_color_map`

```python
def set_color_by_tex_to_color_map(self, texs_to_color_map: dict[str, ParsableManimColor], **kwargs) -> Self:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `texs_to_color_map` | `dict[str, color]` | required | a part → colour dictionary, colouring many parts at once; equivalent to calling `set_color_by_tex` repeatedly. It can also be given as a construction argument `MathTex(..., tex_to_color_map={...})` (the sample demonstrates both) |

#### Sample: the method form + the construction-argument form

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, MathTex, BulletedList, Title, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write, MED_LARGE_BUFF,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class ColorMapDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09b-set_color_by_tex_to_color_map", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— method form: pass one dictionary at once ——
        eq = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=72)
        eq.set_color_by_tex_to_color_map({"x": RED, "y": GREEN, "z": BLUE})   # the "texs_to_color_map" parameter
        eq.move_to([0, 0.9, 0])
        cap = Text("set_color_by_tex_to_color_map({...})", font_size=18, color=GREY_B).next_to(eq, DOWN, buff=0.4)
        win.play(Write(eq), FadeIn(cap), run_time=0.6)   # colour three parts at once

        # —— construction-argument form: fully equivalent, just write it into MathTex(...) ——
        eq2 = MathTex("{{a}}^2", "+", "{{b}}^2", "=", "{{c}}^2", font_size=72,
                      tex_to_color_map={"a": ORANGE, "b": TEAL, "c": PURPLE})   # the "tex_to_color_map" parameter
        eq2.move_to([0, -1.7, 0])
        cap2 = Text("MathTex(..., tex_to_color_map={...})", font_size=18, color=GREY_B).next_to(eq2, DOWN, buff=0.35)
        win.play(Write(eq2), FadeIn(cap2), run_time=0.6)   # coloured as it is constructed
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: get_part_by_tex —— fetching one part =====================
```

What this code does: the formula above passes `{"x": RED, "y": GREEN, "z": BLUE}` in the method form, colouring three parts at once; the one below writes the same dictionary into the construction argument `tex_to_color_map=`, with exactly the same effect—the only difference is whether it is given when the object is built or afterwards.

<video src="assets/RTM output/09b-Substrings-and-Lists-colormap.mp4" controls width="560"></video>

> Note: parts named in the dictionary that do not exist in the formula are **silently ignored** (no error), so a typo'd key will not crash but also will not colour anything—glancing at the frame afterwards is the safest check.

### `MathTex.get_part_by_tex`

```python
def get_part_by_tex(self, tex: str, **kwargs) -> Mobject:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `tex` | `str` | required | the part text; **returns `None` when nothing matches** (it does not error—an `AttributeError` only comes when `part.width` is used next, consistent across both engines in testing) |

Returns the sub-object of the matching part.

#### Sample: fetching a part to box it / move it on its own

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, MathTex, BulletedList, Title, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write, MED_LARGE_BUFF,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class GetPartDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09b-get_part_by_tex", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— the fetched sub-object can be animated on its own (here boxed) ——
        eq = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=72).move_to([0, 0.9, 0])
        part = eq.get_part_by_tex("y")   # the "tex = part text" parameter
        box = Rectangle(width=part.width + 0.3, height=part.height + 0.3,
                        color=YELLOW).move_to(part.get_center())   # box the "y" only
        win.play(Write(eq), run_time=0.6)   # write the formula first
        win.play(Create(box), run_time=0.5)   # box the part that was fetched

        # —— the fetched part can also be moved on its own ——
        eq2 = MathTex("{{a}}", "+", "{{b}}", "=", "{{c}}", font_size=72).move_to([0, -1.7, 0])
        part2 = eq2.get_part_by_tex("b")
        win.play(Write(eq2), run_time=0.6)
        win.play(part2.animate.shift(UP * 1.2), run_time=0.6)   # lift the "b" on its own
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: set_opacity_by_tex —— highlight one, dim the rest =========
```

What this code does: the first formula fetches the `y` part and builds a yellow box from its width and height to fit it exactly; the second fetches the `b` part and uses `.animate.shift(UP * 1.2)` to lift it **on its own**—both show that what you get is a real sub-object you can measure and animate separately.

<video src="assets/RTM output/09b-Substrings-and-Lists-getpart.mp4" controls width="560"></video>

> Note: what is returned is **the sub-object itself in the scene** (not a copy), so transforming it changes the formula on screen directly; when nothing matches you get `None`, so check for null before using it.

### `MathTex.set_opacity_by_tex`

```python
def set_opacity_by_tex(self, tex: str, opacity: float = 0.5, remaining_opacity: float | None = None, **kwargs) -> Self:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `tex` | `str` | required | the part whose opacity to set |
| `opacity` | `float` | `0.5` | the opacity of that part; the sample uses the default 0.5 first, then gives `1.0` explicitly |
| `remaining_opacity` | `float \| None` | `None` | the opacity of the remaining parts; leave it out to "change this one only", fill it in to "highlight one and dim the rest" (the sample uses `0.25` / `0.3`) |

#### Sample: the default / explicit highlighting / changing the focus

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, MathTex, BulletedList, Title, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write, MED_LARGE_BUFF,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class OpacityByTexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09b-set_opacity_by_tex", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— opacity defaults to 0.5; without remaining_opacity nothing else moves ——
        eq = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=72)
        eq.set_opacity_by_tex("y")   # only the "tex" parameter: opacity=0.5 by default
        eq.move_to([-2.2, 0.9, 0])
        cap = Text("set_opacity_by_tex('y')", font_size=18, color=GREY_B).next_to(eq, DOWN, buff=0.4)
        win.play(Write(eq), FadeIn(cap), run_time=0.6)

        # —— opacity explicit + remaining_opacity: the focus bright, the rest darker ——
        eq2 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=72)
        eq2.set_opacity_by_tex("y", opacity=1.0, remaining_opacity=0.25)   # the "opacity / remaining_opacity" parameters
        eq2.move_to([2.2, 0.9, 0])
        cap2 = Text("opacity=1.0 remaining=0.25", font_size=18, color=GREY_B).next_to(eq2, DOWN, buff=0.4)
        win.play(Write(eq2), FadeIn(cap2), run_time=0.6)

        # —— two calls on the same formula: highlight different parts in turn ——
        eq3 = MathTex("{{a}}", "+", "{{b}}", "=", "{{c}}", font_size=72)
        eq3.set_opacity_by_tex("b", opacity=1.0, remaining_opacity=0.3)
        eq3.move_to([0, -1.7, 0])
        cap3 = Text("highlight 'b'", font_size=18, color=GREY_B).next_to(eq3, DOWN, buff=0.35)
        win.play(Write(eq3), FadeIn(cap3), run_time=0.6)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 5: MathTexPart —— iterating parts and reading tex_string =====
```

What this code does:

- The one on the left gives only `tex="y"`, so `y` fades to the default 0.5 and the rest stays put.
- The one on the right gives both `opacity=1.0` and `remaining_opacity=0.25`, so `y` is brightest and everything else is dimmed ("highlighting the focus").
- The one below repeats the same usage on a different formula.

<video src="assets/RTM output/09b-Substrings-and-Lists-opacitybytex.mp4" controls width="560"></video>

> Note: `remaining_opacity` and `opacity` are **two independent** values—leave the former out and the other parts stay as they are; fill it in and they move; successive calls overwrite the values set on those parts last time.

### `MathTexPart`

```python
# not constructed directly: an internal class representing a single part after MathTex splits
```

| Member | Type | Description |
| --- | --- | --- |
| `.tex_string` | `str` | the LaTeX text of that part, usable for matching / display |
| (not constructed directly) | — | instances are generated inside `MathTex`; you meet them when iterating `MathTex.submobjects` or `.family_members_with_points()` |

#### Sample: iterating the parts and listing each one's `tex_string`

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, MathTex, BulletedList, Title, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write, MED_LARGE_BUFF,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class PartsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09b-MathTexPart", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— iterating sub-objects: every MathTexPart carries its own .tex_string ——
        eq = MathTex(r"{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=64)
        eq.move_to([0, 1.4, 0])
        win.play(Write(eq), run_time=0.8)   # write the formula first

        labels = VGroup()   # print each part's tex_string below in turn
        for i, part in enumerate(eq.submobjects):
            txt = getattr(part, "tex_string", "(no tex_string)")   # the "tex_string" attribute
            labels.add(Text("%d: %s" % (i, txt), font_size=18, color=GREY_B))
        labels.arrange(DOWN, buff=0.08).next_to(eq, DOWN, buff=0.35)
        win.play(FadeIn(labels), run_time=0.6)   # list the part texts one by one
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 6: BulletedList —— a bulleted list =========================
```

What this code does: it iterates the formula's `submobjects` one by one, reads each `MathTexPart`'s `tex_string` and lays them out as a label list below—on screen you can see pairs like `0: x`, `1: ^2`, `2: +`… and this is the text the methods above use to match parts.

<video src="assets/RTM output/09b-Substrings-and-Lists-parts.mp4" controls width="560"></video>

> Note: the **order of `submobjects` is LaTeX's writing order** (including non-letter parts such as `^2` and `+`), so count in that order when doing index-based lookups.

### `BulletedList`

```python
def __init__(self, *items: str, buff: float = MED_LARGE_BUFF, dot_scale_factor: float = 2, tex_environment: str | None = None, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*items` | `str...` | required | one string per item; the sample uses three / three items |
| `buff` | `float` | `MED_LARGE_BUFF` (0.5) | item spacing; the sample tightens it to `0.3 ×` for comparison |
| `dot_scale_factor` | `float` | `2` | scaling of the bullet dot; the sample enlarges it to 4 |
| `tex_environment` | `str \| None` | `None` | **do not change**: the outer LaTeX environment; usually just leave it at the default (changing it swaps the typesetting environment of the whole list) |
| `fade_all_but(index_or_string, opacity=0.5)` | method | — | only **indices** are supported: passing a string raises `Exception: Could not locate part by provided tex string '…'` (a `BulletedList` item's `tex_string` carries a trailing `\\` line break, so neither plain text nor `\item x` matches; **consistent across both engines**). The sample uses indices only |

#### Sample: default spacing / tightened spacing + enlarged dot / `fade_all_but` changing the focus

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, MathTex, BulletedList, Title, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write, MED_LARGE_BUFF,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class BulletedListDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("09b-BulletedList", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— buff at its default, dot_scale_factor at its default 2 ——
        bl = BulletedList("first item", "second item", "third item",
                          font_size=40)   # the "*items" parameter
        bl.move_to([-3.2, 0.9, 0])
        win.play(Write(bl), run_time=0.7)   # default spacing and dot size

        # —— buff tightened + dot_scale_factor enlarged ——
        bl2 = BulletedList("tight", "spacing", "list", font_size=40,
                           buff=MED_LARGE_BUFF * 0.3,   # the "buff" parameter: item spacing
                           dot_scale_factor=4)   # the "dot_scale_factor" parameter: dot enlargement
        bl2.move_to([2.6, 0.9, 0])
        cap2 = Text("buff=0.3x  dot_scale_factor=4", font_size=18, color=GREY_B).next_to(bl2, DOWN, buff=0.4)
        win.play(Write(bl2), FadeIn(cap2), run_time=0.7)

        # —— fade_all_but: dim every item except one, by "index" ——
        bl3 = BulletedList("alpha", "beta", "gamma", font_size=40).move_to([-1.6, -1.6, 0])
        win.play(Write(bl3), run_time=0.6)
        bl3.fade_all_but(1, opacity=0.25)   # the "index_or_string=1" parameter: only item 1 stays as it is
        win.play(FadeIn(Text("fade_all_but(1, opacity=0.25)",
                             font_size=18, color=GREY_B).next_to(bl3, DOWN, buff=0.3)),
                 run_time=0.4)
        bl3.fade_all_but(2, opacity=0.25)   # switch the parameter to 2: now dim items 0 and 1
        win.play(FadeIn(Text("fade_all_but(2, opacity=0.25)",
                             font_size=18, color=GREY_B).next_to(bl3, DOWN, buff=0.05)),
                 run_time=0.4)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 7: Title —— the page-header title and its underline ==========
```

What this code does:

- On the left is a list with default parameters.
- On the right `buff` is tightened to 0.3× and `dot_scale_factor` enlarged to 4, so the items are tighter and the dots bigger.
- The one below demonstrates the two indices of `fade_all_but`—first `1` (only `beta` bright), then `2` (both `alpha` and `beta` dimmed, leaving only `gamma`).

<video src="assets/RTM output/09b-Substrings-and-Lists-bulletedlist.mp4" controls width="560"></video>

> Note: `fade_all_but` only changes the **dimmed** items to the given `opacity`; items dimmed before and not part of this call's "rest" **are not restored automatically** (after the sample's second call `beta` is still dim); to restore them one by one, call `set_opacity` on each item yourself.

### `Title`

```python
def __init__(self, *text_parts: str, include_underline: bool = True, match_underline_width_to_text: bool = False, underline_buff: float = MED_SMALL_BUFF, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*text_parts` | `str...` | required | the title text; it can be split into several parts (so they can be coloured separately); the sample gives four variants with a single part |
| `include_underline` | `bool` | `True` | whether to draw the underline; `False` means the line is not there at all |
| `match_underline_width_to_text` | `bool` | `False` | underline width: `False` spans the screen width, `True` matches the text width |
| `underline_buff` | `float` | `MED_SMALL_BUFF` (0.25) | the gap between the underline and the text; the sample uses `0.55` for a visibly wider gap |

#### Sample: four combinations (default / text-width band / no underline / wide gap)

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, MathTex, BulletedList, Title, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write, MED_LARGE_BUFF,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class TitleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"

        # —— default: comes with an underline as wide as the screen ——
        t1 = Title("Chapter 1")   # the "*text_parts" parameter
        win.play(Write(t1), run_time=0.6)   # the default underline spans the screen width
        win.play(FadeOut(t1), run_time=0.3)

        # —— match_underline_width_to_text: the underline is only as wide as the text ——
        t2 = Title("Chapter 2", match_underline_width_to_text=True)   # the "match_underline_width_to_text=True" parameter
        win.play(Write(t2), run_time=0.6)
        win.play(FadeOut(t2), run_time=0.3)

        # —— include_underline=False: no underline at all ——
        t3 = Title("Chapter 3", include_underline=False)   # the "include_underline=False" parameter
        win.play(Write(t3), run_time=0.6)
        win.play(FadeOut(t3), run_time=0.3)

        # —— underline_buff: the gap between the underline and the text ——
        t4 = Title("Chapter 4", match_underline_width_to_text=True,
                   underline_buff=0.55)   # the "underline_buff=0.55" parameter (MED_SMALL_BUFF by default)
        win.play(Write(t4), run_time=0.8)   # the underline sits visibly further from the text
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: four titles appear in turn and fade out.

- The first passes nothing, so the underline spans the screen width.
- The second uses `match_underline_width_to_text=True`, so the underline matches the text width.
- The third uses `include_underline=False`, so there is no underline.
- The fourth raises `underline_buff` to 0.55, visibly widening the gap from the text.

<video src="assets/RTM output/09b-Substrings-and-Lists-title.mp4" controls width="560"></video>

> Note: by default `Title` hugs the **top edge** of the screen and spans the full width, so it works as a page header; several text parts (`Title("A", "B")`) are joined into one line and can be coloured separately.

---

See also: [LaTeX](09-LaTeX.md) · [Text](08-Text.md) · [Braces](16-Braces.md)
