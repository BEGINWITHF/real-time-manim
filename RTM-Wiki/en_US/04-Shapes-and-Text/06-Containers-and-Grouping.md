# Containers: VGroup and grouping

These classes are all defined in `mobject/types/vectorized_mobject.py`. Each of the five classes gets one sample, and each sample changes all of that class's **fillable parameters** once.

Among them, `VDict` / `DashedVMobject` / `VectorizedPoint` / `CurvesAsSubmobjects` had "no clip of their own" before, and this time they are covered.

> **`VGroup` only holds vector objects**: `VGroup(Circle, ImageMobject("x.png"))` raises `TypeError: Only values of type VMobject can be added as submobjects of ...`. To hold non-vector objects such as images together with shapes, use the general-purpose container `Group` (it does not restrict the type; see the sample comparison below).
> **`VDict` is indexed by key, not by position**: `vd["c"]` works, while `vd[2]` raises `KeyError: 2` — it is a dictionary, not a list.

## Parameters

### `VGroup`

```python
def __init__(self, *vmobjects: VMobject, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*vmobjects` | `VMobject...` | can be empty | the vector objects to pack (can be empty, and you can `add` later); a non-`VMobject` (such as `ImageMobject`) raises `TypeError`, in which case use `Group` |

Frequently used methods: `add(*vmobjects)`, `remove(*vmobjects)`, `arrange(direction, buff)`, `shift(...)`, positional indexing `vg[i]` (`-1` is the last one), and whole-group styling (`set_color_by_gradient` and the like act on all submobjects).

#### Sample: construction / a whole-group transform / `add`+`remove` / colouring by index / a whole-group gradient

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, VGroup, VDict, DashedVMobject, VectorizedPoint, CurvesAsSubmobjects,
    Circle, Square, Triangle, Dot, Line, Rectangle, Text, Arc, Star,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class VGroupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("06-VGroup", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— construction: pack three shapes together ——
        vg = VGroup(Circle(radius=0.5, color=BLUE),
                    Square(side_length=0.9, color=GREEN),
                    Triangle(color=ORANGE).scale(0.5))   # the "*vmobjects" parameter
        vg.arrange(RIGHT, buff=0.4).move_to([-3.4, 1.2, 0])   # the "arrange(direction, buff)" method
        cap = Text("VGroup(circle, square, triangle)", font_size=18, color=GREY_B).next_to(vg, DOWN, buff=0.35)
        win.play(Create(vg), FadeIn(cap), run_time=0.6)

        # —— a whole-group transform: the whole set moves together ——
        win.play(vg.animate.shift(RIGHT * 1.2).scale(1.15), run_time=0.7)   # shift the whole group right and scale it up

        # —— add / remove: add and remove submobjects at any time (the caption updates in place, no overlapping text) ——
        vg.add(Dot([1.6, 0, 0], color=RED, radius=0.14))   # the "add(*vmobjects)" method
        cap.become(Text("add(Dot)", font_size=18, color=GREY_B).next_to(vg, DOWN, buff=0.35))
        win.play(FadeIn(vg[-1]), run_time=0.5)
        vg.remove(vg[1])   # the "remove(*vmobjects)" method: take the square out
        cap.become(Text("remove(square)", font_size=18, color=GREY_B).next_to(vg, DOWN, buff=0.35))
        win.play(FadeOut(vg[1].copy().move_to(vg[1])), run_time=0.5)

        # —— indexing and colouring one by one: vg[i] is a submobject ——
        vg2 = VGroup(*[Dot(point=[-4.0 + i * 0.9, -1.4, 0], radius=0.16) for i in range(7)])
        vg2[0].set_color(RED)   # positional indexing
        vg2[3].set_color(TEAL)
        vg2[-1].set_color(GOLD)
        cap2 = Text("vg2[0] / vg2[3] / vg2[-1] coloured individually", font_size=18, color=GREY_B).next_to(vg2, DOWN, buff=0.4)
        win.play(FadeIn(vg2), FadeIn(cap2), run_time=0.6)

        # —— whole-group style: acts on all submobjects at once ——
        win.play(vg2.animate.set_color_by_gradient(BLUE, PURPLE), run_time=0.7)
        cap2.become(Text("set_color_by_gradient applies to all", font_size=18, color=GREY_B).next_to(vg2, DOWN, buff=0.4))
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: VDict —— the container with names ==========================
```

What this code does: first the circle, square and triangle are packed into a `VGroup` and lined up horizontally with `arrange(RIGHT)`.

- Then the whole group is `shift`+`scale`d together, showing that "a group acts as one thing".
- Then `add(Dot)` adds a dot and `remove(vg[1])` takes the square out, so the container's contents can change at any time.
- The second group is seven dots, coloured red/teal/gold via `vg2[0]`, `vg2[3]` and `vg2[-1]` respectively, and finally the whole group gets `set_color_by_gradient` to show the overall effect.

<video src="assets/RTM output/06-Containers-and-Grouping-vgroup.mp4" controls width="560"></video>

> Note: `arrange` **re-lays out** the whole group, not just the one you have added, so after `add` you usually need to `arrange` once more. A whole-group style changes only the style, not the relative positions.

### `VDict`

```python
def __init__(self, mapping_or_iterable: Mapping[Hashable, VMobject] | Iterable[tuple[Hashable, VMobject]] = {}, show_keys: bool = False, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mapping_or_iterable` | `dict \| iterable` | `{}` | the initial key-value pairs: a dictionary or a `[("key", mob), ...]` list (the sample uses both) |
| `show_keys` | `bool` | `False` | whether to show each key as text next to its submobject; the sample compares `True`/`False` |

Frequently used methods: `add(mapping)`, `remove(key)`, `add_key_value_pair(key, value)`, `get_all_submobjects`; fetch submobjects with a **key** (`vd["c"]`) — using a positional index raises `KeyError: 2`.

#### Sample: dictionary form / list form / fetching by key / the three add-and-remove methods

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, VGroup, VDict, DashedVMobject, VectorizedPoint, CurvesAsSubmobjects,
    Circle, Square, Triangle, Dot, Line, Rectangle, Text, Arc, Star,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class VDictDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("06-VDict", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— dictionary form + show_keys=True: the key is shown next to each submobject ——
        vd = VDict({"c": Circle(radius=0.55, color=BLUE),
                    "s": Square(side_length=0.9, color=GREEN)},
                   show_keys=True)   # the "mapping_or_iterable / show_keys" parameters
        vd.arrange(RIGHT, buff=1.1).move_to([-3.2, 1.2, 0])
        cap = Text('VDict({"c":…, "s":…}, show_keys=True)', font_size=18, color=GREY_B).next_to(vd, DOWN, buff=0.4)
        win.play(FadeIn(vd), FadeIn(cap), run_time=0.6)

        # —— key-value list form + show_keys=False ——
        vd2 = VDict([("tri", Triangle(color=ORANGE).scale(0.55)),
                     ("dot", Dot([0.5, 0, 0], color=RED, radius=0.16))],
                    show_keys=False)   # the "mapping_or_iterable" parameter given an iterable
        vd2.arrange(RIGHT, buff=1.0).move_to([1.6, 1.2, 0])
        win.play(FadeIn(vd2), FadeIn(Text('[("tri",…), ("dot",…)] show_keys=False', font_size=18, color=GREY_B).next_to(vd2, DOWN, buff=0.4)), run_time=0.6)

        # —— fetching by key: vd["c"] gets that submobject ——
        vd["c"].set_color(YELLOW)   # fetch a submobject by index/key
        cap.become(Text('vd["c"].set_color(YELLOW)', font_size=18, color=GREY_B).next_to(vd, DOWN, buff=0.4))
        win.play(Wait(0.4), run_time=0.4)

        # —— add / add_key_value_pair / remove: add and remove at any time (note it is by key, not by index) ——
        vd3 = VDict({"t": Triangle(color=TEAL).scale(0.5),
                     "d": Dot([0.6, 0, 0], color=PURPLE, radius=0.14)})
        vd3.arrange(RIGHT, buff=0.9).move_to([-3.2, -1.6, 0])
        win.play(FadeIn(vd3), run_time=0.5)
        vd3.add({"s2": Square(side_length=0.6, color=GREEN)})   # the "add(mapping)" method
        vd3.add_key_value_pair("c2", Circle(radius=0.32, color=BLUE))   # the "add_key_value_pair(key, value)" method
        vd3.arrange(RIGHT, buff=0.7).move_to([-3.2, -1.6, 0])
        cap3 = Text('add + add_key_value_pair + remove("t")', font_size=18, color=GREY_B).next_to(vd3, DOWN, buff=0.4)
        win.play(FadeIn(vd3["s2"]), FadeIn(vd3["c2"]), FadeIn(cap3), run_time=0.5)   # fetching by key: vd3["s2"]
        vd3.remove("t")   # the "remove(key)" method
        vd3.arrange(RIGHT, buff=0.7).move_to([-3.2, -1.6, 0])

        # —— get_all_submobjects: list the submobjects and move them all together ——
        subs = vd3.get_all_submobjects()   # the "get_all_submobjects()" method
        win.play(vd3.animate.shift(RIGHT * 0.8), run_time=0.6)
        cap3.become(Text("get_all_submobjects() -> %d items" % len(subs), font_size=18, color=GREY_B).next_to(vd3, DOWN, buff=0.4))
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: DashedVMobject —— dashing =================================
```

What this code does: this group of samples shows several ways to use `VDict`.

- The first uses the dictionary `{"c": circle, "s": square}` with `show_keys=True`, and each shape's key appears next to it on screen.
- The second uses `[("tri", …), ("dot", …)]` with `show_keys=False`.
- Then `vd["c"].set_color(YELLOW)` fetches that submobject by key and recolours it.
- Finally `add({"s2": …})`, `add_key_value_pair("c2", …)` and `remove("t")` demonstrate adding and removing, and the count from `get_all_submobjects()` is printed as a readout.

<video src="assets/RTM output/06-Containers-and-Grouping-vdict.mp4" controls width="560"></video>

> Note: the key-name text added by `show_keys=True` is also a submobject and is `arrange`d / `shift`ed along with the rest, so remember when animating that they are in the group too. `get_all_submobjects()` counts the key-name text as well, so the count can be larger than the "number of shapes".

### `DashedVMobject`

```python
def __init__(self, vmobject: VMobject, num_dashes: int = 15, dashed_ratio: float = 0.5, dash_offset: float = 0, color: ManimColor = WHITE, equal_lengths: bool = True, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vmobject` | `VMobject` | required | the object to dash (not limited to straight lines; circles, rectangles and curves all work) |
| `num_dashes` | `int` | `15` | number of dash segments; the sample compares 10 / 40 |
| `dashed_ratio` | `float` | `0.5` | fraction taken by the solid part; `0.1` turns it into a dotted line |
| `dash_offset` | `float` | `0` | start offset (where on the path the dashes begin) |
| `color` | `ManimColor` | `WHITE` | colour |
| `equal_lengths` | `bool` | `True` | whether the segments are equal in length; `False` splits by arc-length proportion (longer segments get longer) |

#### Sample: `num_dashes` / `dashed_ratio` / `dash_offset` / `equal_lengths` / a different shape

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, VGroup, VDict, DashedVMobject, VectorizedPoint, CurvesAsSubmobjects,
    Circle, Square, Triangle, Dot, Line, Rectangle, Text, Arc, Star,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class DashedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("06-DashedVMobject", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— num_dashes: the number of dash segments (10 versus 40) ——
        base = Circle(radius=0.85, color=BLUE)
        d10 = DashedVMobject(base, num_dashes=10, color=BLUE).move_to([-4.6, 1.3, 0])   # the "vmobject / num_dashes" parameters
        d40 = DashedVMobject(base, num_dashes=40, color=TEAL).move_to([-1.8, 1.3, 0])
        win.play(FadeIn(d10), FadeIn(Text("num_dashes=10", font_size=18, color=GREY_B).next_to(d10, DOWN, buff=0.25)), run_time=0.5)
        win.play(FadeIn(d40), FadeIn(Text("num_dashes=40", font_size=18, color=GREY_B).next_to(d40, DOWN, buff=0.25)), run_time=0.5)

        # —— dashed_ratio: the solid fraction (0.5 versus 0.1) ——
        d50 = DashedVMobject(base, num_dashes=20, dashed_ratio=0.5, color=ORANGE).move_to([1.2, 1.3, 0])   # the "dashed_ratio" parameter
        ddot = DashedVMobject(base, num_dashes=20, dashed_ratio=0.1, color=YELLOW).move_to([4.0, 1.3, 0])
        win.play(FadeIn(d50), FadeIn(Text("dashed_ratio=0.5", font_size=18, color=GREY_B).next_to(d50, DOWN, buff=0.25)), run_time=0.5)
        win.play(FadeIn(ddot), FadeIn(Text("dashed_ratio=0.1 (dotted)", font_size=18, color=GREY_B).next_to(ddot, DOWN, buff=0.25)), run_time=0.5)

        # —— dash_offset: the start offset (where on the path the dashes begin) ——
        off0 = DashedVMobject(base, num_dashes=12, color=GREEN).move_to([-4.6, -1.6, 0])   # the "dash_offset" parameter, 0 by default
        off5 = DashedVMobject(base, num_dashes=12, dash_offset=0.5, color=PURPLE).move_to([-1.8, -1.6, 0])
        win.play(FadeIn(off0), FadeIn(Text("dash_offset=0", font_size=18, color=GREY_B).next_to(off0, DOWN, buff=0.25)), run_time=0.5)
        win.play(FadeIn(off5), FadeIn(Text("dash_offset=0.5", font_size=18, color=GREY_B).next_to(off5, DOWN, buff=0.25)), run_time=0.5)

        # —— equal_lengths=False: the segments are unequal (the long ones still follow arc-length proportion) ——
        circle = Circle(radius=0.85, color=BLUE).move_to([1.2, -1.6, 0])
        eq = DashedVMobject(circle, num_dashes=12, equal_lengths=False, color=GOLD).move_to([1.2, -1.6, 0])   # the "equal_lengths" parameter
        win.play(FadeIn(eq), FadeIn(Text("equal_lengths=False", font_size=18, color=GREY_B).next_to(eq, DOWN, buff=0.25)), run_time=0.5)

        # —— not limited to circles: any vector object can be dashed ——
        rr = DashedVMobject(Rectangle(width=2.4, height=1.2, color=RED), num_dashes=24,
                            dashed_ratio=0.6, color=RED).move_to([4.0, -1.6, 0])
        win.play(FadeIn(rr), FadeIn(Text("a rectangle can be dashed too", font_size=18, color=GREY_B).next_to(rr, DOWN, buff=0.25)), run_time=0.5)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: VectorizedPoint —— the invisible anchor ====================
```

What this code does: the same arc is used to demonstrate several parameter comparisons in a row.

- `num_dashes` is 10 and 40, to show the number of dash segments.
- `dashed_ratio` is 0.5 and 0.1, and the latter is a dotted line.
- `dash_offset` is 0 and 0.5, shifting the dashes as a whole along the path.
- `equal_lengths=False` splits by arc-length proportion, so longer segments get longer.
- Finally a rectangle is dashed too, proving it does not depend on the shape type.

<video src="assets/RTM output/06-Containers-and-Grouping-dashed.mp4" controls width="560"></video>

> Note: `dashed_ratio` is "the fraction of one segment that is solid", so `num_dashes=20, dashed_ratio=0.5` looks denser. `equal_lengths=False` shows no difference on an object with equal arc lengths such as a circle, and only becomes visible on an ellipse or a curved path.

### `VectorizedPoint`

```python
def __init__(self, location: Point3DLike = ORIGIN, color: ManimColor = BLACK, fill_opacity: float = 0, stroke_width: float = 0, artificial_width: float = 0.01, artificial_height: float = 0.01, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `location` | `array-like` | `ORIGIN` | the point's position |
| `color` | `ManimColor` | `BLACK` | colour (black by default, so it is almost invisible) |
| `fill_opacity` | `float` | `0` | fill opacity; the sample gives `1.0` to turn it into a small visible dot |
| `stroke_width` | `float` | `0` | stroke width; the sample gives `0` (fill only) |
| `artificial_width` | `float` | `0.01` | the **reported width** (it affects `p.width` and the alignment maths, not the size actually drawn); the sample uses `0.8` |
| `artificial_height` | `float` | `0.01` | the reported height; the sample uses `0.5` |

Methods: `get_location()`, `set_location(new_loc)`. It is often used as a positioning anchor or an alignment reference.

#### Sample: invisible by default / inflating the reported size / becoming a visible dot / moving it as an anchor

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, VGroup, VDict, DashedVMobject, VectorizedPoint, CurvesAsSubmobjects,
    Circle, Square, Triangle, Dot, Line, Rectangle, Text, Arc, Star,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class VectorizedPointDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("06-VectorizedPoint", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: completely invisible, but it occupies a very small "reported size" ——
        p = VectorizedPoint(location=[-4.6, 1.5, 0])   # the "location" parameter
        box = Rectangle(width=p.width + 0.4, height=p.height + 0.4,
                        color=GREY_B).move_to(p.get_location())
        cap = Text("default 0.01 x 0.01", font_size=16, color=GREY_B).next_to(box, DOWN, buff=0.3)
        win.play(Create(box), FadeIn(cap), run_time=0.6)

        # —— artificial_width / artificial_height: inflate the "reported size" ——
        p2 = VectorizedPoint(location=[-1.6, 1.5, 0], artificial_width=0.8,
                             artificial_height=0.5)   # the "artificial_width / artificial_height" parameters
        box2 = Rectangle(width=p2.width + 0.2, height=p2.height + 0.2,
                         color=GREY_B).move_to(p2.get_location())
        cap2 = Text("artificial 0.8 x 0.5", font_size=16, color=GREY_B).next_to(box2, DOWN, buff=0.3)
        win.play(Create(box2), FadeIn(cap2), run_time=0.6)

        # —— color / fill_opacity / stroke_width: it can also be drawn as a small visible dot ——
        p3 = VectorizedPoint(location=[1.6, 1.5, 0], color=RED, fill_opacity=1.0,
                             stroke_width=0, artificial_width=0.06,
                             artificial_height=0.06)   # the "color / fill_opacity / stroke_width" parameters
        dot = Dot(p3.get_location(), color=YELLOW, radius=0.05)
        cap3 = Text("visible (fill_opacity=1)", font_size=16, color=GREY_B).next_to(p3.get_location(), DOWN, buff=0.35)
        win.play(FadeIn(dot), FadeIn(cap3), run_time=0.6)

        # —— get_location / set_location: move it around as an anchor ——
        target = Dot([-3.0, -1.9, 0], color=TEAL, radius=0.1)
        p.set_location([-3.0, -1.9, 0])   # the "set_location(new_loc)" method
        win.play(FadeIn(target), run_time=0.4)

        # —— use the anchor to position another object: move the box to where it now is ——
        win.play(box.animate.move_to(p.get_location()), run_time=0.8)   # the "get_location()" method
        cap.become(Text("set_location + get_location: the box follows the anchor", font_size=16, color=GREY_B).next_to(target, DOWN, buff=0.4))
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 5: CurvesAsSubmobjects —— splitting into segments ============
```

What this code does:

- The first point uses the default parameters and nothing appears on screen, but the grey box drawn from its `p.width`/`p.height` marks its "reported size" (0.01×0.01).
- The second point inflates `artificial_width`/`artificial_height` to 0.8×0.5 and the grey box is clearly bigger — showing that these two parameters change only the **reported size**, not the visuals.
- Only when the third point switches on `color=RED, fill_opacity=1` is it drawn as a small visible dot.
- Finally `p.set_location(...)` moves the first point to the bottom left, and `box.animate.move_to(p.get_location())` makes the grey box follow it, demonstrating "anchor + `get_location()` positioning".

<video src="assets/RTM output/06-Containers-and-Grouping-vpoint.mp4" controls width="560"></video>

> Note: by default it is both invisible and only 0.01 in size, so when you add it to a `VGroup` and `arrange`, do not expect it to open up any spacing — to get spacing, raise `artificial_width/height`.

### `CurvesAsSubmobjects`

```python
def __init__(self, vmobject: VMobject, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vmobject` | `VMobject` | required | the object to split; the number of resulting submobjects = its number of sub-curve segments (the sample prints the segment count) |

Splits each sub-curve segment of a compound path object into a separate submobject, which is handy for per-segment handling (per-segment animation, per-segment colouring).

#### Sample: splitting a circle + colouring per segment + moving per segment + per-segment colour on a `Star`

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, VGroup, VDict, DashedVMobject, VectorizedPoint, CurvesAsSubmobjects,
    Circle, Square, Triangle, Dot, Line, Rectangle, Text, Arc, Star,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class CurvesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("06-CurvesAsSubmobjects", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— a circle is made of several Bézier curve segments: once split you can count them one by one ——
        cs = CurvesAsSubmobjects(Circle(radius=1.1, color=BLUE))   # the "vmobject" parameter
        cs.move_to([-3.4, 0.4, 0])
        cap = Text("circle -> %d segments" % len(cs), font_size=18, color=GREY_B).next_to(cs, DOWN, buff=0.8)
        win.play(Create(cs), FadeIn(cap), run_time=0.7)

        # —— colouring per segment: each segment is a separate submobject ——
        colors = [RED, ORANGE, YELLOW, GREEN, TEAL, BLUE, PURPLE, GOLD]
        for i, part in enumerate(cs):
            part.set_color(colors[i % len(colors)])
        cap.become(Text("per-segment set_color", font_size=18, color=GREY_B).next_to(cs, DOWN, buff=0.8))
        win.play(Wait(0.4), run_time=0.4)

        # —— per-segment animation: move each segment apart a little, proving they are independent ——
        for i, part in enumerate(cs):
            part.shift(DR * 0.22 * (i % 3))

        # —— split a more complex object: the multi-segment straight lines of a `Star` can be coloured per segment too ——
        star = Star(outer_radius=1.2, color=TEAL)
        cs2 = CurvesAsSubmobjects(star)   # the "vmobject" parameter
        cs2.scale(0.85).move_to([2.6, 0.4, 0])
        cap2 = Text("Star -> %d segments" % len(cs2), font_size=18, color=GREY_B).next_to(cs2, DOWN, buff=0.4)
        win.play(Create(cs2), FadeIn(cap2), run_time=0.8)

        # —— gradient on the split segments: colouring per segment is handier ——
        win.play(cs2.animate.set_color_by_gradient(ORANGE, PURPLE), run_time=0.8)
        win.play(Wait(0.4))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does:

- A circle is handed to `CurvesAsSubmobjects` and the caption prints the number of segments (a circle's 8 Bézier curve segments).
- Then `cs[i].set_color(...)` colours each segment differently and `cs[i].shift(...)` moves each one apart a little, proving they are independent.
- The second group splits a `Star` (10 straight segments), the caption prints the segment count the same way, and finally the split segments get a whole-group gradient.

<video src="assets/RTM output/06-Containers-and-Grouping-curves.mp4" controls width="560"></video>

> Note: the split submobjects **are still the original curve segments** (just as separate objects), so `shift`ing them as a whole makes them fall apart — which is also its most common use (for "segments flying apart / per-segment highlighting").

---

See also: [Basic shapes](01-Basic-Shapes.md) · [Polygons and stars](03-Polygons-and-Stars.md) · [VMobject styles](07-VMobject-Styles.md)
