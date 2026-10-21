# Angles and callout boxes (2): labeled annotations

The labeled line/polygon classes are defined in `mobject/geometry/labeled.py` and are all based on `Label` (a three-layer combination of "text + background box + frame"). Each class has one sample, and every sample changes each of that class's **fillable parameters** once.

> **The config dictionaries only take effect when the label is a string**: `label_config` / `box_config` / `frame_config` are only used when `label` is a `str` (a string is rendered with `MathTex`); when you pass a ready-made `Text`/`MathTex` object directly, the three dictionaries are ignored and the object's own style wins (the sample's first block demonstrates this).

## Parameters

### `Label`

```python
def __init__(self, label: str | ManimTextLabel, label_config: dict | None = None, box_config: dict | None = None, frame_config: dict | None = None, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `label` | `str \| MathTex \| Text \| Typst` | required | label content; a **string** is rendered with `MathTex` (and only then do the three dictionaries below take effect), or you can pass a ready-made object directly |
| `label_config` | `dict \| None` | `None` | config passed to the label (only effective for strings; the defaults are `color=WHITE`, `font_size=48`), e.g. `{"color": RED, "font_size": 72}` |
| `box_config` | `dict \| None` | `None` | config passed to the background box, e.g. `{"color": TEAL, "fill_opacity": 0.8}` |
| `frame_config` | `dict \| None` | `None` | config passed to the frame, e.g. `{"color": ORANGE, "stroke_width": 6}` |

Returns a `VGroup` (frame + background box + text, three layers), which you can `.scale()` and `.move_to()` as a whole.

#### Sample: the default / each of the three dictionaries changed once / passing a ready-made object

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Label, LabeledLine, LabeledArrow, LabeledPolygram,
    Line, Arrow, Polygon, Triangle, Square, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class LabelDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04b-Label", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— default: white text + the default background box ——
        l1 = Label("x")   # the "label" parameter: a string is rendered with MathTex
        l1.move_to([-4.2, 1.2, 0])
        cap1 = Text('Label("x")', font_size=18, color=GREY_B).next_to(l1, DOWN, buff=0.3)
        win.play(FadeIn(l1), FadeIn(cap1), run_time=0.5)

        # —— label_config: only effective for string labels (colour / font size) ——
        l2 = Label("y", label_config={"color": RED, "font_size": 72})   # the "label_config" parameter
        l2.move_to([-0.6, 1.2, 0])
        cap2 = Text('label_config={"color": RED, "font_size": 72}', font_size=18, color=GREY_B).next_to(l2, DOWN, buff=0.3)
        win.play(FadeIn(l2), FadeIn(cap2), run_time=0.5)

        # —— box_config: colour and opacity of the background box ——
        l3 = Label("z", box_config={"color": TEAL, "fill_opacity": 0.8})   # the "box_config" parameter
        l3.move_to([3.0, 1.2, 0])
        cap3 = Text('box_config={"color": TEAL, "fill_opacity": 0.8}', font_size=18, color=GREY_B).next_to(l3, DOWN, buff=0.3)
        win.play(FadeIn(l3), FadeIn(cap3), run_time=0.5)

        # —— frame_config: colour and stroke width of the frame ——
        l4 = Label("w", frame_config={"color": ORANGE, "stroke_width": 6})   # the "frame_config" parameter
        l4.move_to([-4.2, -1.0, 0])
        cap4 = Text('frame_config={"color": ORANGE, "stroke_width": 6}', font_size=18, color=GREY_B).next_to(l4, DOWN, buff=0.3)
        win.play(FadeIn(l4), FadeIn(cap4), run_time=0.5)

        # —— when label is not a string, *_config is not read: use a ready-made mobject as the label ——
        l5 = Label(Text("hi", color=YELLOW, font_size=40),
                   label_config={"color": RED})   # the "label" parameter given a Mobject: config is ignored
        l5.move_to([-0.6, -1.0, 0])
        cap5 = Text("Label(Text(...))  config ignored", font_size=18, color=GREY_B).next_to(l5, DOWN, buff=0.3)
        win.play(FadeIn(l5), FadeIn(cap5), run_time=0.5)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: LabeledLine —— a label on a line ===========================
```

What this code does: the first block is the default style. The next three blocks each change just one dictionary, and the caption under each says which parameter this block changes:

- `label_config` (red text, size 72);
- `box_config` (a teal semi-transparent backdrop);
- `frame_config` (a thick orange frame).

The last block passes a `Text` directly as the label and still gives `label_config={"color": RED}`, but the text on screen is still the `Text`'s own small yellow text — showing that the dictionary only takes effect for string labels.

<video src="assets/RTM output/04b-Labeled-Annotations-label.mp4" controls width="560"></video>

> Note: to restyle a ready-made `Text`/`MathTex`, set it on that object (`Text("hi", color=YELLOW)`) and do not expect `label_config` to do it.

### `LabeledLine`

```python
def __init__(self, label: str | ManimTextLabel, label_position: float = 0.5, label_config: dict | None = None, box_config: dict | None = None, frame_config: dict | None = None, *args, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `label` | `str \| MathTex \| Text \| Typst` | required | the label on the line (a string is rendered with `MathTex`) |
| `label_position` | `float` | `0.5` | ratio of the label's position along the line (0 start to 1 end); the sample compares 0.2 / 0.5 / 0.8 in turn |
| `label_config` | `dict \| None` | `None` | label config (only effective for string labels) |
| `box_config` | `dict \| None` | `None` | background-box config |
| `frame_config` | `dict \| None` | `None` | frame config |
| `*args` / `**kwargs` | — | — | **`start`/`end` must be written as keywords** (`LabeledLine("3cm", start=..., end=...)`): the first 5 positional parameters of the signature are taken by `label` / `label_position` / `label_config` / `box_config` / `frame_config`, so passing the 2nd to 6th parameters positionally shifts them all (it hits a manim upstream bug, noted in 98-Feature-List §5.2) |

#### Sample: three `label_position` values + the config trio + a ready-made object as the label

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Label, LabeledLine, LabeledArrow, LabeledPolygram,
    Line, Arrow, Polygon, Triangle, Square, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class LabeledLineDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04b-LabeledLine", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— label_position: ratio of the label's position along the line (0 start to 1 end) ——
        for i, pos in enumerate([0.2, 0.5, 0.8]):   # the "label_position" parameter
            ln = LabeledLine("3cm", start=[-4.4, 1.5 - i * 1.5, 0], end=[-0.4, 1.5 - i * 1.5, 0],
                             label_position=pos)   # the "start / end must be keywords" parameters
            cap = Text("label_position=%.1f" % pos, font_size=18, color=GREY_B).next_to(ln, RIGHT, buff=0.4)
            win.play(Create(ln), FadeIn(cap), run_time=0.5)   # the label slides along the line

        # —— the label_config / box_config / frame_config trio ——
        ln2 = LabeledLine("L", start=[1.6, 0.4, 0], end=[5.4, 0.4, 0],
                          label_config={"color": RED, "font_size": 64},
                          box_config={"color": TEAL, "fill_opacity": 0.8},
                          frame_config={"color": ORANGE, "stroke_width": 5})
        cap2 = Text("label/box/frame_config", font_size=18, color=GREY_B).next_to(ln2, DOWN, buff=0.4)
        win.play(Create(ln2), FadeIn(cap2), run_time=0.6)

        # —— the same line can also take a ready-made mobject as the label ——
        ln3 = LabeledLine(Text("Tetra", color=YELLOW, font_size=32),
                          start=[1.6, -1.4, 0], end=[5.4, -1.4, 0], label_position=0.35)
        cap3 = Text("label=Text(...)  label_position=0.35", font_size=18, color=GREY_B).next_to(ln3, DOWN, buff=0.4)
        win.play(Create(ln3), FadeIn(cap3), run_time=0.6)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: LabeledArrow —— the arrow version ==========================
```

What this code does: the picture splits into a left and a right block.

- On the left, three identical lines get `label_position` 0.2 / 0.5 / 0.8 in turn, and the label slides from left to right along the line.
- On the right, the upper line gives `label_config` / `box_config` / `frame_config` together (red text, teal backdrop, orange frame).
- The lower one passes a `Text` as the label and sets `label_position` to 0.35.

<video src="assets/RTM output/04b-Labeled-Annotations-labeledline.mp4" controls width="560"></video>

> Note: with `label_position=0` / `1` the label sits exactly on an endpoint (leave room at the endpoints when drawing the line); parameters other than `start`/`end`, such as colour and stroke width, are still passed to the underlying `Line` as keywords.

### `LabeledArrow`

```python
def __init__(self, *args, **kwargs) -> None:   # forwards to LabeledLine / Arrow; signature is the same as LabeledLine
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `label` / `label_position` / `label_config` / `box_config` / `frame_config` | — | same as `LabeledLine` | exactly the same set of parameters as `LabeledLine` |
| `start` / `end` | `array-like` | required | likewise **must be keywords** |
| `**kwargs` | — | — | everything else keeps forwarding to `Arrow` (the sample gives `color=GOLD`) |

#### Sample: two `label_position` values + the config trio

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Label, LabeledLine, LabeledArrow, LabeledPolygram,
    Line, Arrow, Polygon, Triangle, Square, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class LabeledArrowDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04b-LabeledArrow", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— the same set of parameters as LabeledLine, only the shape is an arrow ——
        for i, pos in enumerate([0.2, 0.6]):   # the "label_position" parameter
            arr = LabeledArrow("5m", start=[-4.4, 1.2 - i * 1.9, 0], end=[0.4, 1.2 - i * 1.9, 0],
                               label_position=pos, color=GOLD)   # colour and the like keep forwarding to Arrow
            cap = Text("label_position=%.1f" % pos, font_size=18, color=GREY_B).next_to(arr, DOWN, buff=0.35)
            win.play(Create(arr), FadeIn(cap), run_time=0.6)

        # —— the config trio works here too ——
        arr2 = LabeledArrow("A", start=[2.0, 0.2, 0], end=[5.6, 0.2, 0],
                            label_config={"color": RED, "font_size": 60},
                            box_config={"color": PURPLE, "fill_opacity": 0.8},
                            frame_config={"color": YELLOW, "stroke_width": 5})
        cap2 = Text("label/box/frame_config", font_size=18, color=GREY_B).next_to(arr2, DOWN, buff=0.4)
        win.play(Create(arr2), FadeIn(cap2), run_time=0.6)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: LabeledPolygram —— it finds the position inside the polygon ===
```

What this code does: the two golden arrows above differ only in `label_position` (0.2 / 0.6); the one below gives the whole config trio — red text, purple backdrop, yellow frame — proving it is the same configuration interface as `LabeledLine`, only the shape is an arrow.

<video src="assets/RTM output/04b-Labeled-Annotations-labeledarrow.mp4" controls width="560"></video>

> Note: the width of the arrow head eats into the line's length, so at the same `label_position` the label looks slightly further forward than in the line version; for precise control, read `label_position` as a "ratio", not as a percentage scale.

### `LabeledPolygram`

```python
def __init__(self, *vertex_groups: Point3DLike_Array, label: str | ManimTextLabel, precision: float = 0.01, label_config: dict | None = None, box_config: dict | None = None, frame_config: dict | None = None, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*vertex_groups` | `array-like...` | required | **every vertex group must be one whole ring of vertices**: `LabeledPolygram([v1, v2, v3], label=...)`. Passing the three points as three positional parameters (`LabeledPolygram(v1, v2, v3, ...)`) raises `IndexError: too many indices for array: array is 1-dimensional, but 2 were indexed` (measured identical on both engines); an open ring is closed automatically |
| `label` | `str \| Mobject` | required | the label placed at the polygon's "innermost point" (pole of inaccessibility) |
| `precision` | `float` | `0.01` | PolyLabel algorithm precision, and it **must match the figure's scale**: the default is enough when the figure spans a few units, but a figure spanning tens of thousands of units needs 1 to 10 (the sample compares with 0.5) |
| `label_config` | `dict \| None` | `None` | label config |
| `box_config` | `dict \| None` | `None` | background-box config |
| `frame_config` | `dict \| None` | `None` | frame config |

It places only **one** label: when several vertex groups are passed together, PolyLabel finds the largest ring by area among all of them and puts the label there, not one label per ring.

#### Sample: a single ring / `precision` / two rings / the config trio

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Label, LabeledLine, LabeledArrow, LabeledPolygram,
    Line, Arrow, Polygon, Triangle, Square, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class LabeledPolygramDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("04b-LabeledPolygram", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— one vertex group (one closed ring): the label lands automatically at the "roomiest" spot inside the polygon ——
        ring = [[-5.4, -0.4, 0], [-3.4, -0.4, 0], [-4.4, 1.6, 0]]   # the "*vertex_groups" parameter: each group is one ring of vertices
        tri = LabeledPolygram(ring, label="A", color=TEAL)   # the "label" parameter
        win.play(Create(tri), FadeIn(Text("one ring, label=\"A\"", font_size=18, color=GREY_B).next_to(tri, DOWN, buff=0.35)),
                 run_time=0.6)

        # —— precision: the search precision of the PolyLabel algorithm, which must match the figure's scale ——
        square = [[-1.8, -0.6, 0], [1.4, -0.6, 0], [1.4, 1.6, 0], [-1.8, 1.6, 0]]
        big = LabeledPolygram(square, label="B", precision=0.5, color=GREEN)   # the "precision=0.5" parameter
        win.play(Create(big), FadeIn(Text("precision=0.5", font_size=18, color=GREY_B).next_to(big, DOWN, buff=0.35)),
                 run_time=0.6)

        # —— several vertex groups: each ring closes on its own and the label lands in the largest one ——
        two = LabeledPolygram([[3.2, 0.2, 0], [5.6, 0.2, 0], [4.4, 1.8, 0]],   # first ring: the large triangle
                              [[6.0, 0.2, 0], [6.8, 0.2, 0], [6.4, 0.8, 0]],   # second ring: the small triangle
                              label="2x", color=ORANGE)   # the "*vertex_groups" parameter: two rings
        win.play(Create(two), FadeIn(Text("two rings, label=\"2x\"", font_size=18, color=GREY_B).next_to(two, DOWN, buff=0.35)),
                 run_time=0.6)

        # —— the label config trio: label_config / box_config / frame_config ——
        poly = LabeledPolygram([[-5.4, -2.6, 0], [-3.4, -2.6, 0], [-4.4, -1.0, 0]],
                               label="C",
                               label_config={"color": RED, "font_size": 60},
                               box_config={"color": TEAL, "fill_opacity": 0.8},
                               frame_config={"color": ORANGE, "stroke_width": 5})
        win.play(Create(poly), FadeIn(Text("label/box/frame_config", font_size=18, color=GREY_B).next_to(poly, DOWN, buff=0.35)),
                 run_time=0.6)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: four blocks are compared.

- On the left, a triangle is given only one ring of vertices (the label lands automatically at the roomiest interior spot).
- The square at the top centre sets `precision` to 0.5.
- The top right passes **two whole rings** of vertices together (a large triangle + a small triangle) and the label lands in the larger one.
- The fourth triangle at the bottom left gives the whole config trio — red text, teal backdrop, orange frame.

<video src="assets/RTM output/04b-Labeled-Annotations-labeledpoly.mp4" controls width="560"></video>

> Note: give each vertex group as "one ring" and do not mix coordinates from different rings in the same list; when `precision` is larger than the figure's scale the search becomes coarse and the label position can drift, so the hint "precision matches scale" is the safest choice.

---

See also: [Angles and callout boxes](04-Angles-and-Callout-Boxes.md) · [Polygons and stars](03-Polygons-and-Stars.md) · [VMobject styles](07-VMobject-Styles.md)
