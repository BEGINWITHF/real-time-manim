# Lines and arrows (2): the tip base class and seven arrowhead shapes

Picking up from [Lines and arrows (1)](02-Lines-and-Arrows.md): `TipableVMobject` is the base class of every object that "can take an arrow tip" (`Line` / `Arrow` / `Arc` / `Circle` all inherit it). This page first covers its three constructor parameters and the two methods `add_tip` / `get_tip`, then gives the seven swappable tip shapes (`mobject/geometry/tips.py`).

Tips are custom curves and go through the generic bezier fallback — the tip base class and the seven arrowhead shapes have been render-verified (2026-10-11), and both samples on this page have been rendered and verified.

## Parameters

### TipableVMobject: tip_length / add_tip / get_tip

```python
def __init__(self, tip_length: float = 0.35,
             normal_vector: Vector3DLike = [0, 0, 1],
             tip_style: dict | None = None, **kwargs: Any) -> None:  # TipableVMobject

def add_tip(self, tip: ArrowTip | None = None,
            tip_shape: type[ArrowTip] | None = None,
            tip_length: float | None = None,
            tip_width: float | None = None,
            at_start: bool = False) -> Self:  # TipableVMobject.add_tip

def get_tip(self) -> VMobject:  # TipableVMobject.get_tip
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `tip_length` | `float` | `0.35` | tip length (given at construction; `add_tip(tip_length=)` can override it) |
| `normal_vector` | `array-like` | `OUT` (`[0,0,1]`) | normal vector of the plane the tip lies in; **do not change** |
| `tip_style` | `dict \| None` | `None` | a dict of tip-style overrides, normally left `None` |
| `tip` | `ArrowTip \| None` | `None` | (`add_tip`) hand in a **ready-made tip instance** directly — pick one of this and `tip_shape` |
| `tip_shape` | `type[ArrowTip] \| None` | `None` | (`add_tip`) pass the **class itself** (no parentheses), e.g. `ArrowSquareTip` |
| `tip_length` | `float \| None` | `None` | (`add_tip`) override the tip length given at construction |
| `tip_width` | `float \| None` | `None` | (`add_tip`) override the tip width |
| `at_start` | `bool` | `False` | `True` = install the tip at the **start** end (by default it goes at the far end) |

> **Returns**: `add_tip(...)` returns the object itself (chainable, works with `.animate`); `get_tip()` returns the tip object — note it takes **no arguments** (it is not `get_tip(0)`), and with two tips it returns the far-end one; to get all of them at once use `get_tips()` (returned in the order they were installed). `TipableVMobject` is normally not instantiated directly; instead you call its methods on a ready object such as `Line` / `Arc`.

#### Sample: installing, fetching, and swapping tips on lines and arcs

Five rows:

- the first is a bare **tip-less** line;
- the second is given `tip_length=0.6` at construction, then `add_tip()` installs a tip and `get_tip()` fetches it back and colours it yellow (proving it was fetched);
- the third installs the tip at the left end with `at_start=True`;
- the fourth hands in a ready-made square tip with `tip=`;
- on the right an arc also has a tip installed at its tail.

```python
from real_time_manim import Scene, Line, Arc, Text, \
    BLUE, RED, GREEN, TEAL, YELLOW, GREY_B, UP, DOWN, PI, \
    ArrowSquareTip, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class TipsBaseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02b-add_tip / get_tip / tip_length", font_size=30, color=YELLOW)
        title.to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— lines have no tip by default, add_tip() installs one on the spot ——
        ln1 = Line([-5.5, 2.0, 0], [0.5, 2.0, 0], color=BLUE, stroke_width=7)   # Line has no tip by default
        c1 = Text("Line (no tip yet)", font_size=22, color=GREY_B).next_to(ln1, DOWN, buff=0.15)
        win.play(Create(ln1), FadeIn(c1), run_time=0.6)   # draw the bare line + caption

        # —— tip_length is given at construction; get_tip() fetches the tip object back ——
        ln2 = Line([-5.5, 0.75, 0], [0.5, 0.75, 0], color=RED, stroke_width=7, tip_length=0.6)   # give tip_length at construction
        c2 = Text("tip_length=0.6 + add_tip() + get_tip()", font_size=20, color=GREY_B)
        c2.next_to(ln2, DOWN, buff=0.15)   # the caption is below
        win.play(Create(ln2), run_time=0.5)   # draw the bare line first
        win.play(ln2.animate.add_tip(), run_time=0.5)   # install the tip with tip_length=0.6
        tip = ln2.get_tip()   # fetch back the tip just installed (get_tip takes no arguments)
        win.play(tip.animate.set_color(YELLOW), FadeIn(c2), run_time=0.4)   # colour the tip yellow to prove it was fetched

        # —— at_start: install the tip at the start end ——
        ln3 = Line([-5.5, -0.5, 0], [0.5, -0.5, 0], color=GREEN, stroke_width=7)   # the start is on the left
        c3 = Text("add_tip(at_start=True)", font_size=22, color=GREY_B).next_to(ln3, DOWN, buff=0.15)
        win.play(Create(ln3), run_time=0.4)   # draw the bare line first
        win.play(ln3.animate.add_tip(at_start=True), FadeIn(c3), run_time=0.5)   # install the tip at the left end

        # —— tip=: hand in a ready-made tip instance directly ——
        ln4 = Line([-5.5, -1.75, 0], [0.5, -1.75, 0], color=TEAL, stroke_width=7)   # about to install a square tip
        c4 = Text("add_tip(tip=ArrowSquareTip(...))", font_size=18, color=GREY_B)
        c4.next_to(ln4, DOWN, buff=0.15)   # the caption is below
        win.play(Create(ln4), run_time=0.4)   # draw the bare line first
        win.play(ln4.animate.add_tip(tip=ArrowSquareTip(length=0.42)), FadeIn(c4), run_time=0.5)   # install the ready-made square tip instance

        # —— any arc can take a tip too (an arrowhead at the arc's tail) ——
        arc = Arc(radius=1.1, start_angle=-PI / 4, angle=PI / 2, color=YELLOW, stroke_width=7)
        arc.shift([4.6, 1.0, 0])   # an arc in the top right
        c5 = Text("arc.add_tip(tip_length=0.3)", font_size=22, color=GREY_B).move_to([4.6, -0.6, 0])
        win.play(Create(arc), run_time=0.5)   # draw the arc first
        win.play(arc.animate.add_tip(tip_length=0.3), FadeIn(c5), run_time=0.5)   # install a tip at the arc's tail + caption
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the first four lines walk through the four ways to use `add_tip`.

- A bare line has no tip.
- A tip with a length of `0.6` fixed at construction (`get_tip()` fetches it and colours it yellow, so you can visibly see it "was fetched").
- `at_start=True` installs the tip at the other end.
- `tip=ArrowSquareTip(...)` installs a ready-made instance.

The right side shows that "tips do not belong to lines only": an `Arc` gets a tip at its tail, with the caption marking out `tip_length=0.3`.

<video src="assets/RTM output/02b-Arrow-Tips-tips_base.mp4" controls width="560"></video>

> Note:
>
> - `get_tip()` takes **no arguments** (any old reference showing `get_tip(0)` is wrong); for all the tips use `get_tips()`.
> - `tip=` takes an **instance** while `tip_shape=` takes a **class** — write `tip_shape=ArrowSquareTip` with no parentheses, and `tip=ArrowSquareTip(length=0.42)` with them.
> - When a construction-time `tip_length` and `add_tip(tip_length=)` both appear, the latter wins.
> - `Line` is bare with no tip by default; `Arrow` is the one that ships with a tip — do not wait for a tip to show up on a `Line` by itself.

### The seven tip shapes: valid values for tip_shape

```python
StealthTip(fill_opacity=1, stroke_width=3, length=0.175, start_angle=PI, **kwargs)
ArrowTriangleTip(fill_opacity=0, stroke_width=3, length=0.35, width=0.35, start_angle=PI, **kwargs)
ArrowTriangleFilledTip(fill_opacity=1, stroke_width=0, **kwargs)
ArrowCircleTip(fill_opacity=0, stroke_width=3, length=0.35, start_angle=PI, **kwargs)
ArrowCircleFilledTip(fill_opacity=1, stroke_width=0, **kwargs)
ArrowSquareTip(fill_opacity=0, stroke_width=3, length=0.35, start_angle=PI, **kwargs)
ArrowSquareFilledTip(fill_opacity=1, stroke_width=0, **kwargs)
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `fill_opacity` | `float` | hollow `0` / filled `1` | whether it is filled; note `StealthTip` is **filled** by default (`1`) |
| `stroke_width` | `float` | hollow `3` / filled `0` | stroke width, complementary to the fill |
| `length` | `float` | `0.35` (`0.175` for `StealthTip`) | tip length; on the filled versions it forwards through `**kwargs` (verified: `ArrowTriangleFilledTip(length=0.5)` takes effect) |
| `width` | `float` | `0.35` | tip width; only `ArrowTriangleTip` lists it explicitly, the other shapes are "length equals width" or take it through `**kwargs` |
| `start_angle` | `float` | `PI` | tip orientation (radians); **do not change** |

> **Returns**: the tip class itself (an `ArrowTip` subclass; `ArrowTip` inherits `VMobject`). The seven come in pairs — hollow versions are `fill_opacity=0 + stroke_width=3` and filled versions are `fill_opacity=1 + stroke_width=0`; the only exception is `StealthTip`, which has no paired hollow version, ships filled and is shorter and smaller.

#### Sample: seven tips compared row by row

Seven blue arrows with the same parameters (`buff=0`, `stroke_width=6`), each changing only `tip_shape=`, with the class names listed down the right side. Note that `tip_shape` takes a **class** (no parentheses); `StealthTip` is a short filled tip, and the three `Arrow*Tip` groups each pair a hollow and a filled version.

```python
from real_time_manim import Scene, Arrow, Text, \
    StealthTip, ArrowTriangleTip, ArrowTriangleFilledTip, \
    ArrowCircleTip, ArrowCircleFilledTip, ArrowSquareTip, ArrowSquareFilledTip, \
    YELLOW, GREY_B, UP, RIGHT, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class TipShapesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02b-7 tip shapes (tip_shape=...)", font_size=30, color=YELLOW)
        title.to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        names = ["StealthTip", "ArrowTriangleTip", "ArrowTriangleFilledTip",
                 "ArrowCircleTip", "ArrowCircleFilledTip",
                 "ArrowSquareTip", "ArrowSquareFilledTip"]   # the seven tip class names
        shapes = [StealthTip, ArrowTriangleTip, ArrowTriangleFilledTip,
                  ArrowCircleTip, ArrowCircleFilledTip,
                  ArrowSquareTip, ArrowSquareFilledTip]   # the seven classes themselves (pass classes, not instances)
        ys = [2.6, 1.7, 0.8, -0.1, -1.0, -1.9, -2.8]   # y coordinates of the seven rows
        for name, shape, y in zip(names, shapes, ys):   # draw row by row: arrow + class name on the right
            a = Arrow([-5.2, y, 0], [2.2, y, 0], buff=0, stroke_width=6,
                      tip_shape=shape)   # tip_shape takes a "class", with no parentheses
            lab = Text(name, font_size=22, color=GREY_B).next_to(a, RIGHT, buff=0.3)
            win.play(Create(a), FadeIn(lab), run_time=0.45)   # draw the arrow + the class-name caption
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: `zip` lines up three lists — class names, classes, and y coordinates — and loops over seven rows; each row is a blue arrow with the same parameters whose only variable is `tip_shape=`, with the class name pinned on the right. They compare at a glance: `StealthTip` is filled and has the shortest tip; the triangle / circle / square groups each put the hollow version (thin stroke) above and the filled version (solid) below.

<video src="assets/RTM output/02b-Arrow-Tips-tip_shapes.mp4" controls width="560"></video>

> Note: `tip_shape=` takes a **class, not an instance** — if you write `tip_shape=ArrowSquareTip()` (with parentheses) you should switch to `tip=ArrowSquareTip(...)`. To change an `Arrow`'s default tip to some shape, just `Arrow(..., tip_shape=...)` (which is exactly what this sample does); when switching styles in bulk, storing `tip_shape` in a variable and passing it is the least trouble.

---

See also: [Lines and arrows](02-Lines-and-Arrows.md) · [Angles and callout boxes](04-Angles-and-Callout-Boxes.md) · [VMobject styles](07-VMobject-Styles.md)
