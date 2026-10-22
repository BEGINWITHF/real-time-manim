# Revealing submobjects one by one: ShowIncreasingSubsets / ShowSubmobjectsOneByOne / SpiralIn

This section covers the three classes filed under "reveal submobjects one by one"; they all act on each submobject of a container:

- `ShowIncreasingSubsets`: pops out one after another, and the previous ones stay.
- `ShowSubmobjectsOneByOne`: shows only one at a time.
- `SpiralIn`: flies in along a spiral trajectory.

## Parameters

### `ShowIncreasingSubsets`

```python
ShowIncreasingSubsets(group, suspend_mobject_updating=False, int_func=np.floor,
                      reverse_rate_function=False, **kwargs)
```

Inherits `ShowIncreasingSubsets(Animation)`. It reveals submobjects **one after another to the beat, and the ones already revealed stay on screen** (the opacity jumps from 0 to 1, so it "pops out" rather than fades in).

**Note**: at construction it immediately sets all submobjects to `set_opacity(0)`, so either `self.add(group)` first and then construct it, or make sure it only enters the scene at `play` time.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `group` | `Mobject` | —(required) | the container revealed one by one (`VGroup`, etc.) |
| `suspend_mobject_updating` | `bool` | `False` | **not advisable to change**: by default the updater is not suspended (opacity is controlled externally) |
| `int_func` | `Callable` | `np.floor` | the function that rounds the continuous progress into a "number revealed". **accepts** `np.floor`/`np.ceil`/a custom callable |
| `reverse_rate_function` | `bool` | `False` | `True` collects in reverse (from all revealed to disappearing one by one) |
| rest | — | — | `Animation` common parameters (`lag_ratio` is replaced by `int_func` in this class) |

> **Returns**: a `ShowIncreasingSubsets` instance.

#### Sample: four shapes pop out to the beat, the previous ones stay

A row of four shapes is added to the scene with `self.add` first, then the five parameters are named one by one — `int_func=np.floor` rounds the progress into a "number revealed", and the shapes pop out one after another and all stay on screen.

```python
import numpy as np
from real_time_manim import Scene, Text, VGroup, Circle, Square, Triangle, BLUE, \
    GREEN, GREY_B, ORANGE, RED, YELLOW, UP, DOWN, RIGHT, FadeIn, \
    ShowIncreasingSubsets, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class IncreasingSubsetsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03-ShowIncreasingSubsets", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l1 = Text("ShowIncreasingSubsets(group, suspend_mobject_updating=False,",
                  font_size=30, color=GREY_B)
        l2 = Text("    int_func=np.floor, reverse_rate_function=False)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line signature label
        g1 = VGroup(Circle(radius=0.35, color=BLUE),
                    Square(side_length=0.9, color=GREEN),
                    Triangle(color=ORANGE).scale(0.6),
                    Circle(radius=0.35, color=RED),
                    ).arrange(RIGHT, buff=0.7).next_to(lab1, DOWN, buff=0.6)   # the four shapes revealed one by one
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   # label fades in from below
        self.add(g1)   # the submobjects are set_opacity(0) at construction, so add to the scene first
        win.play(
            ShowIncreasingSubsets(                  # parameter "group"
                g1,
                suspend_mobject_updating=False,     # parameter "suspend_mobject_updating"
                int_func=np.floor,                  # parameter "int_func": round the number revealed
                reverse_rate_function=False,        # parameter "reverse_rate_function"
                run_time=2.0,                       # parameter "run_time"
            ),
            run_time=2.0,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the four shapes are arranged in a row, `self.add(g1)` puts them into the scene first (constructing `ShowIncreasingSubsets` already set the submobjects to `set_opacity(0)`), then `ShowIncreasingSubsets(g1, suspend_mobject_updating=False, int_func=np.floor, reverse_rate_function=False, run_time=2.0)` plays to the beat. `int_func=np.floor` rounds the continuous progress into a "number revealed"; the shapes pop out one after another and the ones that popped out earlier all stay on screen.

<video src="assets/RTM output/03-Revealing-Subsets-increasing_subsets.mp4" controls width="560"></video>

> Note: `ShowIncreasingSubsets` sets all submobjects to `set_opacity(0)` at construction — the `self.add(g1)` line in the sample is there to "add to the scene first, then play the animation"; skip that line and the objects are invisible when they go on screen.

### `ShowSubmobjectsOneByOne`

```python
ShowSubmobjectsOneByOne(group, int_func=np.ceil, **kwargs)
```

Inherits `ShowSubmobjectsOneByOne(ShowIncreasingSubsets) ← Animation`. It is the opposite of `ShowIncreasingSubsets` — **it shows only one** submobject at a time and hides the previous ones automatically ("flashing in turn"). At construction it wraps the passed iterable into a `Group`. This class is not on RTM's export list; it comes with the bundled ManimCE imported from `real_time_manim` and has been measured to play.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `group` | `Iterable[Mobject]` | —(required) | an iterable container of submobjects (converted into a `Group` internally) |
| `int_func` | `Callable` | `np.ceil` | the progress-rounding function. **accepts** the same as above |
| rest | — | — | inherits `ShowIncreasingSubsets`'s `suspend_mobject_updating=False`, `reverse_rate_function=False` and the `Animation` common parameters |

> **Returns**: a `ShowSubmobjectsOneByOne` instance.

#### Sample: only one lights up at a time, four shapes flash in turn

The same batch of shapes is switched to `ShowSubmobjectsOneByOne(g2, int_func=np.ceil, run_time=2.0)` — `int_func=np.ceil` is exactly the opposite of the previous one; only one lights up at a time and the previous ones are hidden automatically. Again add with `self.add` first, then play.

```python
import numpy as np
from real_time_manim import Scene, Text, VGroup, Circle, Square, Triangle, BLUE, \
    RED, YELLOW, GREEN, GREY_B, UP, DOWN, RIGHT, FadeIn, \
    ShowSubmobjectsOneByOne, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class OneByOneDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03-ShowSubmobjectsOneByOne", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l3 = Text("ShowSubmobjectsOneByOne(group, int_func=np.ceil, run_time=2.0)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        g2 = VGroup(Circle(radius=0.35, color=YELLOW),
                    Square(side_length=0.9, color=RED),
                    Triangle(color=BLUE).scale(0.6),
                    Circle(radius=0.35, color=GREEN),
                    ).arrange(RIGHT, buff=0.7).next_to(l3, DOWN, buff=0.6)   # the four shapes flashing in turn
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)   # label fades in from below
        self.add(g2)   # set to 0 at construction, so add to the scene first
        win.play(
            ShowSubmobjectsOneByOne(                # parameter "group"
                g2,
                int_func=np.ceil,                   # parameter "int_func": the rounding function
                run_time=2.0,                       # parameter "run_time"
            ),
            run_time=2.0,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the same batch of shapes is switched to `ShowSubmobjectsOneByOne(g2, int_func=np.ceil, run_time=2.0)`. `int_func=np.ceil` rounds the progress into "which one should be lit right now"; only one submobject lights up at a time and the previous ones are hidden automatically, so the four shapes flash in turn. It inherits `ShowIncreasingSubsets` and likewise sets the submobjects to 0 at construction, so `self.add(g2)` is needed first too.

<video src="assets/RTM output/03-Revealing-Subsets-one_by_one.mp4" controls width="560"></video>

> Note: `ShowSubmobjectsOneByOne` is not on RTM's export list; import it from `real_time_manim` (see the code block), and it has been measured to play; switch `int_func` to another callable and the rounding rule changes with it.

### `SpiralIn`

```python
SpiralIn(shapes, scale_factor=8, fade_in_fraction=0.3, **kwargs)
```

Inherits `SpiralIn(Animation)`. **Each submobject** of `shapes` flies into place along a **spiral trajectory** from "a position scaled `scale_factor` times about the whole group's center", fading in during the first `fade_in_fraction` of the progress; good as a fancy entrance for a group of shapes.

**Gotcha**: the constructor **moves the submobjects immediately** (moving them to the spiral's start), so do not `self.add(shapes)` ahead of time. The demo on this page imports from the top level of `real_time_manim`, so it enters the scene as an introducer at play time.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `shapes` | `Mobject` | —(required) | the container being animated; **each submobject flies in separately** |
| `scale_factor` | `float` | `8` | how many times the start position is expanded outward relative to the whole group's center. **accepts** any positive number (larger = flies in from farther away) |
| `fade_in_fraction` | `float` | `0.3` | how much of the progress is used for fading in. **accepts** `0`~`1` |
| `introducer` | `bool` | `False` | RTM's own version **accepts** it (it goes through `Animation`'s default `False`; passing `True` explicitly takes effect) |
| rest | — | — | `Animation` common parameters |

> **Returns**: a `SpiralIn` instance.

#### Sample: four shapes fly in along a spiral trajectory

In `samples`, `scale_factor=6` is non-default (default 8), and `fade_in_fraction=0.3` fades in during the first 30%; this segment does **not** `self.add` ahead of time.

```python
from real_time_manim import Scene, Text, VGroup, Circle, Square, Triangle, BLUE, \
    GREEN, GREY_B, ORANGE, RED, YELLOW, UP, DOWN, RIGHT, FadeIn, SpiralIn, \
    Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class SpiralInDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03-SpiralIn", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l5 = Text("SpiralIn(shapes, scale_factor=6, fade_in_fraction=0.3,",
                  font_size=30, color=GREY_B)
        l6 = Text("        run_time=1.8)",
                  font_size=30, color=GREY_B)
        lab3 = VGroup(l5, l6).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line signature label
        g3 = VGroup(Circle(radius=0.4, color=GREEN),
                    Square(side_length=1.0, color=BLUE),
                    Triangle(color=RED).scale(0.7),
                    Circle(radius=0.4, color=ORANGE),
                    ).arrange(RIGHT, buff=0.7).next_to(lab3, DOWN, buff=0.6)   # the four shapes flying in along a spiral
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)   # label fades in from below
        # do not add ahead of time: SpiralIn moves the submobjects to the spiral start at construction and enters the scene as an introducer
        win.play(
            SpiralIn(g3,                            # parameter "shapes"
                     scale_factor=6,                # parameter "scale_factor": non-default 8
                     fade_in_fraction=0.3,          # parameter "fade_in_fraction"
                     run_time=1.8),                 # parameter "run_time"
            run_time=1.8,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: `SpiralIn(g3, scale_factor=6, fade_in_fraction=0.3, run_time=1.8)` makes the four shapes each fly into place along a spiral trajectory from a position "expanded 6 times about the whole group's center", fading in during the first 30% of the progress. Note that this segment does not `self.add` ahead of time — `SpiralIn` moves the submobjects to the spiral start at construction, letting it enter the scene as an introducer at play time.

<video src="assets/RTM output/03-Revealing-Subsets-spiral_in.mp4" controls width="560"></video>

> Note: `SpiralIn` is the opposite of the first two — do **not** `self.add` ahead of time (at construction it moves the submobjects to the spiral start; adding early would put that start position on screen directly).

Not demonstrable:

- `introducer`: RTM's own `SpiralIn` **accepts** it; `ShowIncreasingSubsets` has no such parameter, and the two versions agree.
- mobject type checking: RTM's own version does no type checking.

---

See also: [Create and the drawing family](01-Create-and-the-Drawing-Family.md) · [Reverse Removal](02-Reverse-Removal.md) · [Lifecycle and Common Parameters](../Common/01-Lifecycle-and-Common-Parameters.md)
