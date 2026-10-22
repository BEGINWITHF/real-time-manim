# The rest of the API: low-frequency but public

Closing odds and ends: bitmap export, submobject reordering, family-wide operations and taking points along a path. The three renderable groups each have sample videos; the two that **cannot be rendered** have their reason written out in the section, with no empty video slot.

## Parameters

### get_image / show / save_image — cannot be rendered

```python
def get_image(camera: Camera | None = None) -> Image.Image
def show(camera: Camera | None = None) -> None
def save_image(name: str | None = None) -> None
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `camera` | `Camera` or `None` | `None` | custom camera |
| `name` | `str` or `None` | `None` | file name (without extension); defaults to the object's name |

> **Returns**: `get_image` returns a PIL `Image`; `show` pops up an image viewer; `save_image(name)` saves to `name.png` under the current `video_dir`. As designed in the docs, these suit debugging "what does this thing actually look like".

**Why there is no video**: in manim 0.21's implementation these three methods reference `Camera` internally **without importing it** (an upstream bug), so calling them directly raises `NameError: name 'Camera' is not defined` — RTM and the stock engine **crash identically** in testing, there is no picture to render, so this section has no video.

Workaround: for a bitmap, use the render pipeline's output directly (an RTM recorded frame / `manim`'s `-s` saved frame), or draw from the point array yourself.

```python
from real_time_manim import Square
Square().get_image()   #NameError: name 'Camera' is not defined (identical on both engines)
```

### sort / shuffle / invert

```python
def sort(point_to_num_func: Callable[[Point3DLike], float] = lambda p: p[0],
         submob_func: Callable[[Mobject], Any] | None = None) -> Self
def shuffle(recursive: bool = False) -> Self
def invert(recursive: bool = False) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `point_to_num_func` | callable | `lambda p: p[0]` | compute the sort key from a point (`sort`) |
| `submob_func` | callable or `None` | `None` | compute the sort key directly from a submobject, **takes priority** |
| `recursive` | `bool` | `False` | whether to recurse into submobjects |

> **Returns**: the object itself. It reorders the `submobjects` list, which directly affects draw order and the order `arrange` uses: `sort` sorts by centre x by default, `shuffle` randomises, `invert` reverses.

#### Sample: four reorderings in a row

Five scattered coloured squares: `sort` (by position) → `invert` (reverse) → seeded `shuffle` (random) → `sort(submob_func=...)` (by colour name), with `arrange` showing the new order after each step.

```python
import random

from real_time_manim import Scene, VGroup, Square, \
    RED, BLUE, GREEN, YELLOW, PURPLE, UP, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class SortShuffleInvertDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        colors = (RED, BLUE, GREEN, YELLOW, PURPLE)   # five colours
        spots = (LEFT * 3.5 + UP * 1.4, RIGHT * 2.0 + UP * 0.6, LEFT * 1.0 + DOWN * 1.2, RIGHT * 3.2 + DOWN * 1.6, LEFT * 2.4)   # five distinct scattered positions
        v = VGroup(*[Square(color=c, side_length=0.8).shift(p) for c, p in zip(colors, spots)])   # scatter them first
        self.add(v)   # add to the scene
        win.play(Wait(0.4))   # pause to see the initial scattered positions
        v.sort()   #sort: reorder the list left-to-right by current centre x
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   # line them up in list order: colours ordered by position
        v.invert(recursive=False)   #invert: reverse the list order
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   # the order is entirely reversed
        random.seed(7)   # fix the random seed for reproducibility
        v.shuffle(recursive=False)   #shuffle: randomise
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   # random order
        v.sort(submob_func=lambda m: str(m.color))   #submob_func takes priority: sort by colour name
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   # colour names A to Z
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: five coloured squares are first scattered over the grid, then the list order changes four times in a row.

- `sort()` reorders the list by current **centre x**, so after `arrange` the colours left-to-right match the positions left-to-right.
- `invert()` turns the whole list around; after re-lining-up the order is mirrored.
- `shuffle()` randomises (the sample fixes the random sequence with `random.seed(7)` first, so two engines / two runs agree).
- Finally `sort(submob_func=lambda m: str(m.color))` uses the **higher-priority** submobject key — sorting by colour name alphabetically into BLUE→GREEN→PURPLE→RED→YELLOW.

<video src="assets/RTM output/11b-Misc-APIs-sort_shuffle_invert.mp4" controls width="560"></video>

> Note: the three methods change the **list order** (which affects both draw order and `arrange`) and never touch coordinates; `shuffle` without a seed gives a different result every time.
>
> `recursive=True` also reorders the lists inside submobjects.

### apply_to_family

```python
def apply_to_family(func: Callable[[Mobject], None]) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `func` | `Callable[[Mobject], None]` | — | called once for every descendant **with points** |

> **Returns**: the object itself. It calls `func` on itself and on every descendant with points, which is handier than writing a loop.

#### Sample: restyling in bulk

Three squares and two circles each restyle their strokes in bulk with one `apply_to_family` line — three lines fewer than a `for m in ...` loop.

```python
from real_time_manim import Scene, VGroup, Group, Square, Circle, \
    BLUE, RED, UP, DOWN, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class ApplyFamilyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        v = VGroup(*[Square(color=BLUE, side_length=0.9) for _ in range(3)])   # three squares
        v.arrange(RIGHT, buff=0.3).shift(UP * 1.5)
        self.add(v)   # add to the scene
        v.apply_to_family(lambda m: m.set_stroke(width=6))   # called once for every member with points
        win.play(FadeIn(v), run_time=0.4)   # squares with thick strokes fade in
        g = Group(Circle(radius=0.45), Circle(radius=0.45)).arrange(RIGHT, buff=0.4).shift(DOWN * 1.5)   # two circles
        self.add(g)   # add to the scene
        g.apply_to_family(lambda m: m.set_stroke(color=RED, width=6))   # works for the circles too
        win.play(FadeIn(g), run_time=0.4)   # circles with red thick strokes fade in
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: a row of three squares gets thickened strokes all at once with `apply_to_family(lambda m: m.set_stroke(width=6))`; the two circles below get red thick strokes from a single line too. The callback is **only sent to members with points** (containers themselves do not receive it), equivalent to the hand-written loop `for m in v.family_members_with_points(): f(m)`.

<video src="assets/RTM output/11b-Misc-APIs-apply_family.mp4" controls width="560"></video>

> Note: the callback receives **every member of the family that has points** — including itself (when it has points). It does not return a new object; it modifies state in place.
>
> For "bulk changes every frame" use an updater instead.

### get_start / get_end / get_start_and_end / get_pieces / point_from_proportion / proportion_from_point

```python
def get_start() -> Point3D    def get_end() -> Point3D    def get_start_and_end() -> tuple
def get_pieces(n_pieces: float) -> Group
def point_from_proportion(alpha: float) -> Point3D
def proportion_from_point(point: Point3DLike) -> float
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `n_pieces` | `float` | — | number of segments to cut into (`get_pieces` only) |
| `alpha` | `float` | — | path proportion 0~1 (`point_from_proportion` only) |
| `point` | point | — | the target point to invert back to a proportion (`proportion_from_point` only) |

> **Returns**: `get_start` / `get_end` return the **first / last vertex**; `point_from_proportion` / `proportion_from_point` are the general entry points for "taking a point along a curve", and the **base class raises `NotImplementedError`**, with `Line` / `Arc` / `VMobject` and friends implementing them; `get_pieces(n)` cuts the object into a group of n segments. The first few no-argument methods return `np.ndarray` / `tuple`.

#### Sample: taking points along a line and cutting segments

The line's first and last vertices, a red dot at 25%, `get_pieces(4)` cut into four gradient-coloured segments; on the circle, take the 25% point and invert it back to a proportion with `proportion_from_point` (`0.25`).

```python
from real_time_manim import Scene, Line, Circle, Dot, \
    BLUE, RED, YELLOW, ORANGE, UP, DOWN, LEFT, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class PathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        line = Line(LEFT * 3.5, RIGHT * 0.5, color=YELLOW).shift(UP * 1.5)   # a line segment
        self.add(line)   # add to the scene
        print("get_start =", line.get_start().round(2))   # first vertex
        print("get_end =", line.get_end().round(2))   # last vertex
        p = line.point_from_proportion(0.25)   # 25% along the path
        self.add(Dot(color=RED, radius=0.09).move_to(p))   # mark it with a dot
        print("point_from_proportion(0.25) =", p.round(2))
        pieces = line.get_pieces(4)   # cut into 4 segments
        pieces.set_color_by_gradient(RED, BLUE)
        self.add(pieces)   # add to the scene
        win.play(FadeIn(pieces), run_time=0.5)   # the four gradient segments appear
        c = Circle(radius=0.9, color=ORANGE).shift(RIGHT * 3.0 + DOWN * 1.2)   # circle: taking a point on a curve is more intuitive
        self.add(c)   # add to the scene
        q = c.point_from_proportion(0.25)
        print("circle 25% =", q.round(2))
        print("proportion_from_point =", round(c.proportion_from_point(q), 4))   # invert back to a proportion
        win.play(FadeIn(c), run_time=0.4)   # the circle fades in
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: the yellow line's `get_start` / `get_end` print the first and last vertex coordinates; `point_from_proportion(0.25)` takes the point 25% along the path and marks it with a red dot (a quarter of the way in from the left of the line); `get_pieces(4)` cuts the line into four segments, colours them with a gradient and fades them in — the four segments are all different colours.

The circle at the lower right demonstrates taking a point on a curve and **inverting** it: `point_from_proportion(0.25)` takes a point and `proportion_from_point(q)` computes the proportion `0.25` back exactly.

<video src="assets/RTM output/11b-Misc-APIs-path.mp4" controls width="560"></video>

> Note: `get_start` / `get_end` raise on objects without points (an empty `Group`); check `has_points()` first.
>
> `point_from_proportion` takes the point by **cumulative arc length**, which matches intuition for uniform paths like `Line` / `Arc` / `Circle`; `proportion_from_point` requires the point to **actually lie on the path** (on a `Circle` it returns 0.25 as measured, but even slightly off it raises `ValueError: does not lie on this curve`).

### mobject/utils.py renderer base-class factories — no visual

```python
def get_mobject_class() -> type           # the current renderer's Mobject base class
def get_vectorized_mobject_class() -> type  # VMobject
def get_point_mobject_class() -> type     # PMobject
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| (no parameters) | — | — | returns the corresponding base class for the current renderer |

**Why there is no video**: these three functions return **class objects** (`Mobject` / `VMobject` / `PMobject`) and produce no picture themselves; they are only good for printing. They exist for Manim's own code and plugin authors, and **ordinary animation scripts neither need nor should call them**:

```python
from real_time_manim import get_mobject_class, get_vectorized_mobject_class, get_point_mobject_class
print(get_mobject_class(), get_vectorized_mobject_class(), get_point_mobject_class())
#<class 'manim.mobject.mobject.Mobject'> <class '...VMobject'> <class '...PMobject'>
```

---

See also: [Measurement](03-Measurement.md) | [Screen Frame and Banners](11-Screen-Frame-and-Banners.md)
