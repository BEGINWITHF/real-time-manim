# Boolean operations

These classes are defined in `mobject/geometry/boolean_ops.py`; both input and output are `VMobject` — the shapes' paths are required to be closed and fillable.

Each of the four functions gets one sample, and each draws "input shapes → result" side by side and changes the style `**kwargs` once along the way.

> **The result is a new object**: all four functions return a **brand-new** `VMobject`, i.e. the outline of the union / difference / intersection / symmetric difference. The original objects you pass in are not modified — every sample lays the original `a`/`b` back on screen untouched, for comparison.
>
> The style `**kwargs` (`color`, `stroke_width`, `.set_fill(...)` etc.) act directly on the return value.

## Parameters

### `Union`

```python
def __init__(self, *vmobjects: VMobject, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*vmobjects` | `VMobject...` | required | the shapes taking part in the merge (at least 2); the sample gives both the 2-shape and the 3-shape case |
| `**kwargs` | — | — | style passed to the result `VMobject`; the sample uses `color=GOLD, stroke_width=6` plus `.set_fill(GOLD, 0.85)` |

Union: merge several shapes into one outline, keeping only one layer where they overlap.

#### Sample: 2 shapes / 3 shapes / style kwargs / the originals are unmodified

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Union, Difference, Intersection, Exclusion,
    Circle, Square, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class UnionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05-Union", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— the union of two shapes: the overlap keeps only one outline layer ——
        a = Circle(radius=0.9, color=BLUE).shift(LEFT * 0.55 + UP * 1.2)
        b = Square(side_length=1.5, color=RED).shift(RIGHT * 0.55 + UP * 1.2)
        src = inputs(a, b).move_to([-4.4, 1.2, 0])
        merged = Union(a, b, color=GREEN).set_fill(GREEN, 0.5).move_to([-1.0, 1.2, 0])   # the "*vmobjects" parameter
        win.play(FadeIn(src), FadeIn(Text("a + b", font_size=18, color=GREY_B).next_to(src, DOWN, buff=0.25)), run_time=0.5)
        win.play(FadeIn(merged), FadeIn(Text("Union(a, b, color=GREEN)", font_size=18, color=GREY_B).next_to(merged, DOWN, buff=0.25)), run_time=0.6)

        # —— the union of three shapes: still only one outline ——
        c = Circle(radius=0.7, color=TEAL).move_to([2.2, 1.9, 0])
        d = Square(side_length=1.1, color=ORANGE).move_to([3.3, 0.9, 0])
        e = Triangle(color=PURPLE).scale(0.65).move_to([2.0, 0.7, 0])
        three = Union(c, d, e).set_fill(PURPLE, 0.35).move_to([2.7, 1.2, 0])
        win.play(FadeIn(three), FadeIn(Text("Union(c, d, e)", font_size=18, color=GREY_B).next_to(three, DOWN, buff=0.25)), run_time=0.6)

        # —— style kwargs: the union is also an ordinary VMobject ——
        a2 = Circle(radius=0.9, color=BLUE).shift(LEFT * 0.5 + DOWN * 1.6)
        b2 = Square(side_length=1.4, color=RED).shift(RIGHT * 0.5 + DOWN * 1.6)
        src2 = inputs(a2, b2).move_to([-4.4, -1.7, 0])
        styled = Union(a2, b2, color=GOLD, stroke_width=6).set_fill(GOLD, 0.85).move_to([-1.0, -1.7, 0])   # the "**kwargs" parameter
        win.play(FadeIn(src2), run_time=0.4)
        win.play(FadeIn(styled), FadeIn(Text("color=GOLD stroke_width=6 fill=0.85", font_size=18, color=GREY_B).next_to(styled, DOWN, buff=0.25)), run_time=0.6)

        # —— the originals are unaffected: lay a / b back out as they were, for comparison ——
        originals = VGroup(a.copy(), b.copy()).move_to([2.7, -1.7, 0])
        win.play(FadeIn(originals), FadeIn(Text("originals a / b unchanged", font_size=18, color=GREY_B).next_to(originals, DOWN, buff=0.25)), run_time=0.6)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: Difference —— the difference ===============================
```

What this code does: four comparison blocks are laid out on screen.

- Top left first lays out the circle and square taking part (with a faint fill, for comparison), and to the right sits the result of `Union(a, b, color=GREEN)`.
- Then `Union(c, d, e)` is applied to three shapes and the result still has only one outer outline.
- Bottom left applies both `color=GOLD, stroke_width=6` and `.set_fill(GOLD, 0.85)`, proving the return value is an ordinary `VMobject`.
- Finally the original `a`/`b` are put back on screen and their shapes are completely unchanged.

<video src="assets/RTM output/05-Boolean-Operations-union.mp4" controls width="560"></video>

> Note:
>
> - The shapes taking part must be **closed**; `Circle`/`Square`/`Polygon` all work; with a non-closed object such as `Line` the result is unreliable.
> - The number of outline paths in the union equals the number of "visible boundaries", so it is not a simple "layering" of shapes.

### `Difference`

```python
def __init__(self, subject: VMobject, clip: VMobject, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `subject` | `VMobject` | required | the main shape being subtracted from |
| `clip` | `VMobject` | required | the shape used to subtract (cut it out of the main shape) |
| `**kwargs` | — | — | result style; the sample uses `color=PURPLE, stroke_width=6` |

Difference: subtract from `subject` the part that overlaps `clip`. **The subtraction has a direction**, so swapping the two parameters gives a different result.

#### Sample: circle minus square / square minus circle / style kwargs / cutting a hole to make a ring

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Union, Difference, Intersection, Exclusion,
    Circle, Square, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class DifferenceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05-Difference", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— subject minus clip: the square bites a piece out of the circle ——
        subj = Circle(radius=1.0, color=BLUE).move_to([-4.4, 1.3, 0])
        clip = Square(side_length=1.4, color=RED).move_to([-3.8, 0.9, 0])
        diff = Difference(subj, clip, color=GREEN).set_fill(GREEN, 0.5).move_to([-1.0, 1.3, 0])   # the "subject / clip" parameters
        win.play(FadeIn(inputs(subj, clip)), FadeIn(diff),
                 FadeIn(Text("Difference(circle, square)", font_size=18, color=GREY_B).next_to(diff, DOWN, buff=0.25)), run_time=0.7)

        # —— swapped: square minus circle (the subtraction has a direction) ——
        subj2 = Square(side_length=1.6, color=ORANGE).move_to([2.2, 1.3, 0])
        clip2 = Circle(radius=0.85, color=TEAL).move_to([2.9, 1.3, 0])
        diff2 = Difference(subj2, clip2, color=ORANGE).set_fill(ORANGE, 0.5).move_to([4.7, 1.3, 0])
        win.play(FadeIn(inputs(subj2, clip2)), FadeIn(diff2),
                 FadeIn(Text("Difference(square, circle)", font_size=18, color=GREY_B).next_to(diff2, DOWN, buff=0.25)), run_time=0.7)

        # —— style kwargs ——
        subj3 = Circle(radius=0.95, color=PURPLE).move_to([-4.4, -1.7, 0])
        clip3 = Triangle(color=GOLD).scale(0.9).move_to([-3.9, -1.9, 0])
        diff3 = Difference(subj3, clip3, color=PURPLE, stroke_width=6).set_fill(PURPLE, 0.8).move_to([-1.0, -1.7, 0])   # the "**kwargs" parameter
        win.play(FadeIn(inputs(subj3, clip3)), FadeIn(diff3),
                 FadeIn(Text("color=PURPLE stroke_width=6 fill=0.8", font_size=18, color=GREY_B).next_to(diff3, DOWN, buff=0.25)), run_time=0.7)

        # —— cut-out: when clip is entirely inside subject the result is a "hole" ——
        ring = Difference(Circle(radius=0.95, color=RED).move_to([2.7, -1.7, 0]),
                          Circle(radius=0.5, color=RED).move_to([2.7, -1.7, 0]),
                          color=RED).set_fill(RED, 0.7)   # the inner circle stays empty = a ring
        win.play(FadeIn(ring), FadeIn(Text("cut out inside (ring)", font_size=18, color=GREY_B).next_to(ring, DOWN, buff=0.25)), run_time=0.7)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: Intersection —— the intersection ===========================
```

What this code does: the four samples take the key points of the difference in turn.

- The first is "the square bites a piece out of the circle".
- The second swaps the parameters (square minus circle) and the resulting shape is clearly different, showing that the order matters.
- The third applies `color`/`stroke_width`/`.set_fill`.
- The fourth puts `clip` entirely inside `subject`, punching out a hole the size of the inner circle — which draws a ring exactly.

<video src="assets/RTM output/05-Boolean-Operations-difference.mp4" controls width="560"></video>

> Note:
>
> - `Difference` performs a single boolean subtraction and does not automatically "punch a hole into a ring"; the ring is the natural result of "the inner circle being cut out entirely".
> - To punch several holes, subtract repeatedly, or switch to `Exclusion` for the symmetric difference.

### `Intersection`

```python
def __init__(self, *vmobjects: VMobject, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*vmobjects` | `VMobject...` | required | the shapes taking part in the intersection (at least 2); the sample uses 2 and 3 |
| `**kwargs` | — | — | result style; the sample uses `color=ORANGE, stroke_width=6` |

Intersection: keep only the common region where all the shapes overlap.

#### Sample: two circles / three circles / style kwargs / a completely separated empty result

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Union, Difference, Intersection, Exclusion,
    Circle, Square, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class IntersectionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05-Intersection", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— two shapes: keep only the common region ——
        a = Circle(radius=0.9, color=BLUE).move_to([-4.6, 1.2, 0])
        b = Circle(radius=0.9, color=RED).move_to([-3.4, 1.2, 0])
        inter = Intersection(a, b, color=YELLOW).set_fill(YELLOW, 0.8).move_to([-1.4, 1.2, 0])   # the "*vmobjects" parameter
        win.play(FadeIn(inputs(a, b)), FadeIn(inter),
                 FadeIn(Text("Intersection(a, b)", font_size=18, color=GREY_B).next_to(inter, DOWN, buff=0.25)), run_time=0.7)

        # —— three shapes: the common region is smaller ——
        c = Circle(radius=0.85, color=TEAL).move_to([2.1, 1.4, 0])
        d = Circle(radius=0.85, color=GREEN).move_to([3.3, 1.4, 0])
        e = Circle(radius=0.85, color=PURPLE).move_to([2.7, 0.4, 0])
        three = Intersection(c, d, e, color=WHITE).set_fill(WHITE, 0.8).move_to([2.7, 1.3, 0])
        win.play(FadeIn(three), FadeIn(Text("Intersection(c, d, e)", font_size=18, color=GREY_B).next_to(three, DOWN, buff=0.25)), run_time=0.7)

        # —— style kwargs ——
        a2 = Square(side_length=1.5, color=BLUE).move_to([-4.6, -1.8, 0])
        b2 = Circle(radius=0.95, color=RED).move_to([-3.9, -1.4, 0])
        styled = Intersection(a2, b2, color=ORANGE, stroke_width=6).set_fill(ORANGE, 0.9).move_to([-1.4, -1.8, 0])   # the "**kwargs" parameter
        win.play(FadeIn(inputs(a2, b2)), FadeIn(styled),
                 FadeIn(Text("color=ORANGE stroke_width=6", font_size=18, color=GREY_B).next_to(styled, DOWN, buff=0.25)), run_time=0.7)

        # —— when there is no overlap the intersection is empty: give a small hint (an empty result draws nothing) ——
        far = Intersection(Circle(radius=0.6, color=GOLD).move_to([2.0, -1.8, 0]),
                           Circle(radius=0.6, color=GOLD).move_to([4.4, -1.8, 0]), color=GOLD)
        win.play(FadeIn(Text("fully separated -> empty result", font_size=18, color=GREY_B).move_to([3.2, -2.6, 0])), run_time=0.5)
        win.play(FadeIn(far.set_fill(GOLD, 0.8)), run_time=0.5)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: Exclusion —— the symmetric difference ======================
```

What this code does: the four samples draw one case each.

- The two circles on the left produce the "lens" region in the middle.
- The three circles at the top right are intersected and the common region is smaller.
- The bottom left switches to a square and a circle and applies a style.
- The bottom right places two circles completely apart; there is nothing in the intersection, so only a line of explanation is left on screen — so seeing no new shape in the picture is a **normal result**, not a render failure.

<video src="assets/RTM output/05-Boolean-Operations-intersection.mp4" controls width="560"></video>

> Note:
>
> - When the shapes do not intersect at all the result is an empty object: it still returns a `VMobject`, it just has no visible points.
> - When writing an animation, do not wait until you have run `Create`/`Write` on it to discover that there is "nothing" — first confirm that the two figures really do overlap.

### `Exclusion`

```python
def __init__(self, subject: VMobject, clip: VMobject, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `subject` | `VMobject` | required | the main shape |
| `clip` | `VMobject` | required | the shape to take the symmetric difference with the main shape |
| `**kwargs` | — | — | result style; the sample uses `color=PURPLE, stroke_width=6` |

Symmetric difference (XOR): keep the parts of `subject` and `clip` that do **not** overlap, and cut out the overlap.

#### Sample: circle and square / circle and circle (two crescents) / style kwargs

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Union, Difference, Intersection, Exclusion,
    Circle, Square, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class ExclusionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("05-Exclusion", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— circle and square: keep only the non-overlapping parts (cut out the overlap) ——
        a = Circle(radius=0.95, color=BLUE).move_to([-4.5, 1.2, 0])
        b = Square(side_length=1.5, color=RED).move_to([-3.7, 1.2, 0])
        ex = Exclusion(a, b, color=GREEN).set_fill(GREEN, 0.5).move_to([-1.3, 1.2, 0])   # the "subject / clip" parameters
        win.play(FadeIn(inputs(a, b)), FadeIn(ex),
                 FadeIn(Text("Exclusion(circle, square)", font_size=18, color=GREY_B).next_to(ex, DOWN, buff=0.25)), run_time=0.7)

        # —— two circles: you get two crescents (XOR) ——
        c = Circle(radius=0.85, color=ORANGE).move_to([2.2, 1.2, 0])
        d = Circle(radius=0.85, color=TEAL).move_to([3.2, 1.2, 0])
        ex2 = Exclusion(c, d, color=YELLOW).set_fill(YELLOW, 0.7).move_to([4.6, 1.2, 0])
        win.play(FadeIn(inputs(c, d)), FadeIn(ex2),
                 FadeIn(Text("Exclusion(circle, circle) = two crescents", font_size=18, color=GREY_B).next_to(ex2, DOWN, buff=0.25)), run_time=0.7)

        # —— style kwargs ——
        a2 = Circle(radius=0.9, color=PURPLE).move_to([-4.5, -1.7, 0])
        b2 = Triangle(color=GOLD).scale(0.95).move_to([-3.6, -1.8, 0])
        ex3 = Exclusion(a2, b2, color=PURPLE, stroke_width=6).set_fill(PURPLE, 0.8).move_to([-1.3, -1.7, 0])   # the "**kwargs" parameter
        win.play(FadeIn(inputs(a2, b2)), FadeIn(ex3),
                 FadeIn(Text("color=PURPLE stroke_width=6", font_size=18, color=GREY_B).next_to(ex3, DOWN, buff=0.25)), run_time=0.7)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: three samples.

- The first takes the symmetric difference of a circle and a square, and the overlapping region is cut out.
- The second takes the symmetric difference of two intersecting circles and gives two crescents, left and right — this is what XOR looks like in practice.
- The third applies `color`/`stroke_width`/`.set_fill`, showing that the return value is an ordinary `VMobject` just like the other three functions.

<video src="assets/RTM output/05-Boolean-Operations-exclusion.mp4" controls width="560"></video>

> Note: `Exclusion(a, b)` and `Union(a, b)` are exact complements — one keeps only the non-overlapping parts, the other keeps only the union's outline.
>
> This pair is often used together for "cut-out highlighting": draw `Union` first, then overlay `Exclusion`, and visually you get "overall outline + the intersection cut out".

---

See also: [Polygons and stars](03-Polygons-and-Stars.md) · [Rectangles and special polygons](03b-Rectangles-and-Special-Polygons.md) · [VMobject styles](07-VMobject-Styles.md)
