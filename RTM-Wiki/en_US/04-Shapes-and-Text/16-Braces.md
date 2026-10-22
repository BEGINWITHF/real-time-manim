# Brace annotations

The annotation family for "draw a brace next to an object + a caption": defined in `mobject/svg/brace.py`; the manual entry is `BraceText` (there is no `BraceWithText`). One sample per class, and each sample changes each of that class's **fillable parameters** once.

> **The kwargs of `get_text` / `get_tex` go only to `put_at_tip`**: inside `Brace.get_text(*text, **kwargs)` the `**kwargs` are all fed to `put_at_tip(mob, **kwargs)` (which ends up as `mob.next_to(..., **kwargs)`), so `get_text("x", font_size=20)` / `get_tex("x", font_size=20)` raise `TypeError: Mobject.next_to got an unexpected keyword argument 'font_size'`.
> The font size/colour must be set **after getting the object back**: `lbl = br.get_text("x"); lbl.scale(0.6).set_color(GREY)`; only `next_to` parameters such as `buff` and `aligned_edge` can be passed directly.

## Parameters

### `Brace`

```python
def __init__(self, mobject: Mobject, direction: Vector3DLike = DOWN, buff: float = 0.2, sharpness: float = 2, stroke_width: float = 0, fill_opacity: float = 1.0, background_stroke_width: float = 0, background_stroke_color: ParsableManimColor = BLACK, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | required | the annotated object (the brace automatically takes its position and length) |
| `direction` | `array-like` | `DOWN` | the brace's orientation; the sample draws all four directions `DOWN`/`UP`/`LEFT`/`RIGHT` |
| `buff` | `float` | `0.2` | spacing from the object; the sample compares `0.9` against the default |
| `sharpness` | `float` | `2` | how sharp the corner is; the sample uses `6` (sharper tip, steeper transition) |
| `stroke_width` | `float` | `0` | stroke width; the sample uses `2` |
| `fill_opacity` | `float` | `1.0` | fill opacity; the sample uses `0.5` |
| `background_stroke_width` | `float` | `0` | background stroke width; the sample uses `10` (a thicker outer ring) |
| `background_stroke_color` | `ManimColor` | `BLACK` | background stroke colour; the sample uses `RED` |

Methods: `get_text(*text, **kwargs)` (puts a `Tex` at the tip and returns it), `get_tex(*tex, **kwargs)` (the same but with `MathTex`), `put_at_tip(mob, use_next_to=True, **kwargs)`, `get_tip()` (the tip coordinates), `get_direction()` (the orientation vector).

#### Sample: the four directions / `buff` + `sharpness` / stroke and fill / five methods

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Brace, BraceText, BraceLabel, BraceBetweenPoints, ArcBrace,
    Square, Line, Dot, Text, Arc, VGroup, MathTex, DEGREES,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, GrowFromCenter, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class BraceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("16-Brace", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— direction: which side of the object the brace is on ——
        group = VGroup()
        for i, (d, name) in enumerate([(DOWN, "DOWN"), (UP, "UP"), (LEFT, "LEFT"), (RIGHT, "RIGHT")]):   # the "direction" parameter
            sq = Square(side_length=1.2, color=BLUE).move_to([-4.8 + i * 3.2, 1.1, 0])
            br = Brace(sq, direction=d, color=GREEN)   # the "mobject / direction" parameters
            lbl = br.get_text(name, buff=0.06)   # the "get_text" method: the kwargs only go to put_at_tip (i.e. next_to's buff)
            lbl.scale(0.55).set_color(GREY_B)   # a Tex's font size/colour must be set afterwards (get_text does not take those kwargs)
            group.add(sq, br, lbl)
            win.play(Create(sq), GrowFromCenter(br), FadeIn(lbl), run_time=0.45)   # the four directions appear one after another
        win.play(FadeOut(group), run_time=0.3)

        # —— buff / sharpness: spacing from the object, corner sharpness ——
        sq2 = Square(side_length=1.4, color=BLUE).move_to([-2.0, 0.6, 0])
        br2 = Brace(sq2, direction=DOWN, buff=0.9, sharpness=6, color=ORANGE)   # the "buff / sharpness" parameters
        lbl2 = br2.get_text("buff=0.9  sharpness=6")   # the "get_text" method
        lbl2.scale(0.6).set_color(GREY_B)
        win.play(Create(sq2), GrowFromCenter(br2), FadeIn(lbl2), run_time=0.6)
        win.play(FadeOut(sq2), FadeOut(br2), FadeOut(lbl2), run_time=0.25)

        # —— stroke_width / fill_opacity / background_stroke_width / background_stroke_color ——
        ln = Line(LEFT * 2.2, RIGHT * 2.2, color=BLUE)
        br3 = Brace(ln, direction=DOWN, stroke_width=2, fill_opacity=0.5,
                    background_stroke_width=10, background_stroke_color=RED)   # the "stroke_width / fill_opacity / background_*" parameters
        lbl3 = br3.get_text("stroke 2 - fill 0.5 - bg 10 - RED")   # the "get_text" method (Tex is math mode: do not put underscores in the string)
        lbl3.scale(0.5).set_color(GREY_B)
        win.play(Create(ln), GrowFromCenter(br3), FadeIn(lbl3), run_time=0.7)
        win.play(FadeOut(ln), FadeOut(lbl3), run_time=0.25)

        # —— methods: get_tex / put_at_tip / get_tip / get_direction ——
        lbl4 = br3.get_tex(r"x^2+y^2=r^2")   # the "get_tex" method: switch to a MathTex label
        lbl4.scale(0.7).set_color(TEAL)
        win.play(FadeIn(lbl4), run_time=0.4)
        tip = br3.get_tip()   # the "get_tip()" method: get the tip coordinates
        dot = Dot(tip, color=YELLOW, radius=0.07)
        dirn = br3.get_direction()   # the "get_direction()" method: get the orientation vector
        cap = Text("tip + direction = (%d, %d)" % (round(dirn[0]), round(dirn[1])),
                   font_size=20, color=GREY_B).next_to(lbl4, DOWN, buff=0.25)
        win.play(FadeIn(dot), FadeIn(cap), run_time=0.4)
        win.play(FadeOut(lbl4), run_time=0.25)   # the tip label and the get_tex label share a position; take the old one away first
        tag = Text("put_at_tip", font_size=22, color=PURPLE)
        br3.put_at_tip(tag)   # the "put_at_tip(mob)" method: put the object at the tip
        win.play(FadeIn(tag), run_time=0.4)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: BraceText —— brace + ordinary text in one step ==========
```

What this code does: four sections.

- The first section draws one brace on the same square for each of the four `direction`s, and writes the direction name on each brace with `get_text`.
- The second pulls `buff` up to 0.9 and `sharpness` up to 6; the brace is clearly further away and the tip is sharper.
- The third adds a brace to a horizontal line and changes `stroke_width` (2), `fill_opacity` (0.5), `background_stroke_width` (10) and `background_stroke_color` (RED) at the same time.
- The last section demonstrates the methods: `get_tex` for a formula label, `get_tip()` to take the tip coordinates and draw a yellow dot, `get_direction()` to print the orientation vector as a reading, and `put_at_tip()` to place another object at the tip.

<video src="assets/RTM output/16-Braces-brace.mp4" controls width="560"></video>

> Note: when `sharpness` is too small (e.g. 1) the tip gets blunt and looks like an arc; `background_stroke_*` draws a thick border on the brace's **outer** ring (`stroke_width` is the inner ring), so the two layers can be different colours.

### `BraceText`

```python
def __init__(self, obj: Mobject, text: str, label_constructor: type[SingleStringMathTex | Text] = Text, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `obj` | `Mobject` | required | the annotated object |
| `text` | `str \| Mobject` | required | the annotation text |
| `label_constructor` | `class` | `Text` | the text rendering class; the sample switches it to `MathTex` for comparison (`MathTex` goes through LaTeX, so formulas look neater) |
| `brace_direction` | `array-like` | `DOWN` | the brace's orientation; the sample uses `RIGHT` / `UP` |
| `font_size` | `float` | `DEFAULT_FONT_SIZE` | label font size; the sample uses `24` / `60` |
| `buff` | `float` | `0.2` | spacing between the brace and the object; the sample uses `0.7` |
| `brace_config` | `dict \| None` | `None` | the style passed to the internal `Brace`; the sample uses `{"color": ORANGE}` |

It is the `Text` version of `BraceLabel`: it constructs "brace + ordinary text" in one go, with the text automatically placed just outside the tip.

#### Sample: default / switching to `MathTex` / direction + spacing + style / a large font

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Brace, BraceText, BraceLabel, BraceBetweenPoints, ArcBrace,
    Square, Line, Dot, Text, Arc, VGroup, MathTex, DEGREES,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, GrowFromCenter, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class BraceTextDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("16-BraceText", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— default: label_constructor=Text, the brace below ——
        sq = Square(side_length=1.6, color=BLUE).move_to([-3.4, 0.9, 0])
        bt = BraceText(sq, "square", font_size=28)   # the "obj / text" parameters
        win.play(Create(sq), GrowFromCenter(bt), run_time=0.6)   # the text is automatically placed just outside the tip

        # —— label_constructor: switch the label to MathTex ——
        sq2 = Square(side_length=1.6, color=TEAL).move_to([0.6, 0.9, 0])
        bt2 = BraceText(sq2, r"a^2", label_constructor=MathTex, font_size=40)   # the "label_constructor" parameter
        win.play(Create(sq2), GrowFromCenter(bt2), run_time=0.6)

        # —— brace_direction / buff / brace_config: direction, spacing, brace style ——
        sq3 = Square(side_length=1.6, color=GOLD).move_to([-3.4, -1.6, 0])
        bt3 = BraceText(sq3, "buff & config", brace_direction=RIGHT, font_size=24,
                        buff=0.7, brace_config={"color": ORANGE})   # the "brace_direction / buff / brace_config" parameters
        win.play(Create(sq3), GrowFromCenter(bt3), run_time=0.7)

        # —— the brace above, with a larger font ——
        sq4 = Square(side_length=1.6, color=PURPLE).move_to([2.8, -2.2, 0])
        bt4 = BraceText(sq4, "font_size=32", brace_direction=UP, font_size=32)   # the "font_size" parameter
        win.play(Create(sq4), GrowFromCenter(bt4), run_time=0.7)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: BraceLabel —— default MathTex label + four methods =======
```

What this code does: four squares each with a `BraceText`.

- The first is the default: a `Text` label, brace below.
- The second switches `label_constructor` to `MathTex` and gives it `a^2`.
- The third switches to `brace_direction=RIGHT`, `buff=0.7`, `brace_config={"color": ORANGE}`.
- The fourth raises `font_size` to 60 and points the brace upwards.

<video src="assets/RTM output/16-Braces-bracetext.mp4" controls width="560"></video>

> Note: `BraceText`'s `**kwargs` are passed on to `BraceLabel`, so all of `BraceLabel`'s parameters (`brace_direction`, `font_size`, `buff`, `brace_config`) are available here.

### `BraceLabel`

```python
def __init__(self, obj: Mobject, text: str, brace_direction: Vector3DLike = DOWN, label_constructor: type[SingleStringMathTex | Text] = MathTex, font_size: float = DEFAULT_FONT_SIZE, buff: float = 0.2, brace_config: dict | None = None, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `obj` | `Mobject` | required | the annotated object |
| `text` | `str \| Mobject` | required | the label content (the string goes through LaTeX, so by default formulas can be written directly) |
| `brace_direction` | `array-like` | `DOWN` | the brace's orientation; the sample uses `LEFT` |
| `label_constructor` | `class` | `MathTex` | the label rendering class (`BraceText` is just this switched to `Text`) |
| `font_size` | `float` | `DEFAULT_FONT_SIZE` | label font size; the sample uses `30` |
| `buff` | `float` | `0.2` | spacing |
| `brace_config` | `dict \| None` | `None` | brace style; the sample uses `{"color": TEAL}` |

Methods: `creation_anim(label_anim=FadeIn, brace_anim=GrowFromCenter)` (an animation group that brings the brace and the label in together), `change_label(*text)` (change only the label), `change_brace_label(obj, *text)` (change the object + the label), `shift_brace(obj)` (re-attach the brace to the object).

#### Sample: default / `creation_anim` / `change_label` / `shift_brace` / `change_brace_label`

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Brace, BraceText, BraceLabel, BraceBetweenPoints, ArcBrace,
    Square, Line, Dot, Text, Arc, VGroup, MathTex, DEGREES,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, GrowFromCenter, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class BraceLabelDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("16-BraceLabel", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— default: label_constructor=MathTex ——
        sq = Square(side_length=2.0, color=BLUE).move_to([0, 0.6, 0])
        bl = BraceLabel(sq, r"2 \times 2")   # the "obj / text" parameters
        win.play(Create(sq), bl.creation_anim(), run_time=0.6)   # the "creation_anim" method

        # —— change_label: swap out the label text ——
        old_label = bl.label   # the entrance animation adds the old label to the scene separately: take it away too when changing the label
        bl.change_label(r"\sqrt{2}")   # the "change_label(*text)" method
        win.play(FadeOut(old_label), FadeIn(bl.label), run_time=0.5)

        # —— shift_brace: move the brace to the other side (the text follows) ——
        bl2 = BraceLabel(sq, "LEFT", brace_direction=LEFT, font_size=30,
                         brace_config={"color": TEAL})   # the "brace_direction / font_size / brace_config" parameters
        bl.shift_brace(sq)   # the "shift_brace(obj)" method: re-attach to the object
        win.play(GrowFromCenter(bl2), run_time=0.6)   # one more on the left for comparison

        # —— change_brace_label: change the object + the label ——
        sq2 = Square(side_length=1.4, color=GREEN).move_to([-4.4, -2.0, 0])
        bl2.change_brace_label(sq2, "moved")   # the "change_brace_label(obj, *text)" method
        win.play(Create(sq2), run_time=0.5)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: BraceBetweenPoints —— marking the distance between two points
```

What this code does: it gives a square a default `BraceLabel` (a `MathTex` label `2 \times 2`) and brings it in directly with `creation_anim()`, then demonstrates three methods in turn.

- `change_label(r"\sqrt{2}")` swaps the text out.
- Another instance pointing left with a teal brace is built for comparison, and in between `shift_brace(sq)` is called once to demonstrate "re-attaching to the object".
- Finally the label instance is moved onto another green square with `change_brace_label(sq2, "moved")`.

<video src="assets/RTM output/16-Braces-bracelabel.mp4" controls width="560"></video>

> Note: `change_label` / `change_brace_label` / `shift_brace` all **change the object immediately** (they are not animations); to see the process, follow up with `win.play(bl.creation_anim())` or do `Write`/`Transform` on `bl.label` separately.

### `BraceBetweenPoints`

```python
def __init__(self, point_1: Point3DLike, point_2: Point3DLike, direction: Vector3DLike = ORIGIN, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `point_1` | `array-like` | required | end point 1 |
| `point_2` | `array-like` | required | end point 2 |
| `direction` | `array-like` | `ORIGIN` | orientation (with `ORIGIN` it automatically takes the direction perpendicular to the connecting line); the sample uses `DOWN` / `UP` / `LEFT` |

It does not depend on a Mobject and draws a brace straight between two points, good for annotating "the distance between two points / some interval"; it can likewise be labelled with `get_text` / `get_tex`.

#### Sample: horizontal `DOWN`/`UP` + a formula label + vertical `LEFT`

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Brace, BraceText, BraceLabel, BraceBetweenPoints, ArcBrace,
    Square, Line, Dot, Text, Arc, VGroup, MathTex, DEGREES,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, GrowFromCenter, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class BraceBetweenDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("16-BraceBetweenPoints", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— direction=DOWN: below two horizontal points ——
        a, b = LEFT * 4.0 + UP * 1.4, RIGHT * 1.0 + UP * 1.4
        d1 = Dot(a, color=BLUE)
        d2 = Dot(b, color=BLUE)
        bb = BraceBetweenPoints(a, b, direction=DOWN, color=GREEN)   # the "point_1 / point_2 / direction" parameters
        lbl = bb.get_text("distance")   # the "get_text" method
        lbl.scale(0.6).set_color(GREY_B)
        win.play(FadeIn(d1), FadeIn(d2), GrowFromCenter(bb), FadeIn(lbl), run_time=0.7)

        # —— direction=UP: above the same pair of points ——
        bb2 = BraceBetweenPoints(a, b, direction=UP, color=ORANGE)   # the parameter switched to UP
        win.play(GrowFromCenter(bb2), run_time=0.5)

        # —— get_tex: use a formula as the label; the same object can just get a label ——
        lbl2 = bb2.get_tex(r"\Delta x")   # the "get_tex" method
        lbl2.scale(0.7).set_color(TEAL)
        win.play(FadeIn(lbl2), run_time=0.5)

        # —— two vertical points + a LEFT direction ——
        c, d = LEFT * 1.0 + DOWN * 2.4, LEFT * 1.0 + UP * 0.4
        bb3 = BraceBetweenPoints(c, d, direction=LEFT, color=PURPLE)
        lbl3 = bb3.get_text("dy")
        lbl3.scale(0.6).set_color(GREY_B)
        win.play(FadeIn(Dot(c, color=YELLOW)), FadeIn(Dot(d, color=YELLOW)),
                 GrowFromCenter(bb3), FadeIn(lbl3), run_time=0.7)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 5: ArcBrace —— a curved brace ===============================
```

What this code does: it draws braces between two blue points left and right, once for each of three directions.

- First below (`direction=DOWN`), labelled with `get_text("distance")`.
- Then one above the same pair of points (`direction=UP`), switching to `get_tex(r"\Delta x")`.
- Finally one on the left of two vertically arranged points with `direction=LEFT`, labelled `dy`.

<video src="assets/RTM output/16-Braces-bracebetween.mp4" controls width="560"></video>

> Note: when `direction` is `ORIGIN` (the default) the brace finds the "perpendicular to the connecting line" direction by itself; but when the line itself is slanted the result may be less intuitive than specifying the direction, so for slanted lines it is better to give `UP`/`DOWN` explicitly.

### `ArcBrace`

```python
def __init__(self, arc: Arc | None = None, direction: Vector3DLike = RIGHT, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `arc` | `Arc \| None` | `None` | the annotated arc; with `None` it uses the **unit circle** (the sample's last section demonstrates this) |
| `direction` | `array-like` | `RIGHT` | the brace's orientation (the outside/inside of the arc); the sample uses `RIGHT` / `LEFT` |

A curved brace drawn along an arc, used to annotate an angle/arc segment; it can likewise be labelled with `get_text`.

#### Sample: the two directions `RIGHT`/`LEFT` + a custom arc + `arc=None`

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Brace, BraceText, BraceLabel, BraceBetweenPoints, ArcBrace,
    Square, Line, Dot, Text, Arc, VGroup, MathTex, DEGREES,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, GrowFromCenter, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class ArcBraceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("16-ArcBrace", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— add a brace to an arc: direction=RIGHT ——
        arc = Arc(radius=1.4, start_angle=0, angle=90 * DEGREES, color=BLUE).move_to([-3.2, 0.4, 0])
        ab = ArcBrace(arc, direction=RIGHT, color=ORANGE)   # the "arc / direction" parameters
        win.play(Create(arc), GrowFromCenter(ab), run_time=0.7)

        # —— direction=LEFT: swings to the other side of the arc ——
        ab2 = ArcBrace(arc, direction=LEFT, color=TEAL)   # the parameter switched to LEFT
        win.play(GrowFromCenter(ab2), run_time=0.5)

        # —— with its own arc: a larger arc + a label ——
        arc2 = Arc(radius=1.4, start_angle=90 * DEGREES, angle=90 * DEGREES, color=GREEN).move_to([3.2, 0.4, 0])
        ab3 = ArcBrace(arc2, direction=RIGHT, color=PURPLE)
        lbl = ab3.get_text("90 deg")   # the "get_text" method
        lbl.scale(0.6).set_color(GREY_B)
        win.play(Create(arc2), GrowFromCenter(ab3), FadeIn(lbl), run_time=0.7)

        # —— arc=None: the unit circle by default ——
        ab4 = ArcBrace(direction=RIGHT, color=RED).move_to([0, -2.2, 0])   # the "arc=None" parameter
        cap = Text("arc=None (unit circle)", font_size=20, color=GREY_B).next_to(ab4, DOWN, buff=0.35)
        win.play(GrowFromCenter(ab4), FadeIn(cap), run_time=0.7)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: three blocks.

- A brace is added to a 90° arc on the left (`direction=RIGHT`), then another with `direction=LEFT` is added on the same arc for comparison.
- On the right another 90° arc is drawn with a brace, and the angle is labelled with `get_text("90 deg")`.
- Finally nothing is passed to `arc`, giving a brace hugging the unit circle, labelled `arc=None (unit circle)`.

<video src="assets/RTM output/16-Braces-arcbrace.mp4" controls width="560"></video>

> Note: `ArcBrace`'s brace radius follows the arc, so the shorter the arc the flatter the brace; when annotating an angle you usually put `direction` on the outside of the arc (the default `RIGHT` is the outward one).

---

See also: [Angles and callout boxes](04-Angles-and-Callout-Boxes.md) · [Labeled annotations](04b-Labeled-Annotations.md) · [Images and SVG](15-Images-and-SVG.md)
