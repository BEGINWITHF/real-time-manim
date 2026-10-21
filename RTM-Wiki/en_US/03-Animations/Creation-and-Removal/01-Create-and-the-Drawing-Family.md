# Create and the drawing family: Create / Write / DrawBorderThenFill / ShowPartial

This section covers the classes filed under "draw it stroke by stroke": they all trace the vector path and bring an object into existence from nothing.

- `Create`: the most standard drawing animation.
- `Write`: the most commonly used entrance animation.
- `DrawBorderThenFill`: good for shapes that have a fill.
- `ShowPartial`: their shared abstract base class.

## Parameters

### `Create`

```python
Create(mobject, run_time=1.0, lag_ratio=1.0, **kwargs)
```

Inherits `Create(Animation)` (RTM's own implementation, `real_time_manim/animations/create.py`; **not** a subclass of `ShowPartial`). It gradually draws **from start to finish** along the vector path — the most standard "drawing" animation. The RTM version does **no type checking**; the default `lag_ratio=1.0` makes multiple sub-strokes finish **one after another**.

> **2026-10-17 update · import**: the signature on this page describes **RTM's own** `Create`, which must be imported with `from real_time_manim.vulkan_bind import Create` (or `real_time_manim.animations`).
>
> The sample code imports from the **top level** of `real_time_manim`, so it gets the **built-in ManimCE 0.21 version**:
>
> - `Create(ShowPartial)`
> - `introducer` is fixed at `True`
> - non-vector objects raise `TypeError`
>
> The two versions share the same name, the same parameters and the same usage; the samples do not depend on this difference.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `VMobject` | —(required) | the object to draw. **accepts** any `VMobject`: `Square`/`Circle`/`Text`/`MathTex`/`Arrow`…; RTM's own version does no type checking, so a plain `Mobject` also constructs (the picture still advances stroke by stroke) |
| `run_time` | `float` | `1.0` | seconds needed to finish drawing; **accepts** any positive number |
| `lag_ratio` | `float` | `1.0` | stagger ratio of the sub-strokes; **accepts** `0`~`1`, `1.0` = draw one after another, `0` = all strokes grow at the same time |
| `introducer` | `bool` | `False` | add the object to the scene before playing. RTM's own `Create` **does not fix** this parameter (it goes through `Animation`'s default `False`; passing `True` explicitly takes effect). The sample passes `True` explicitly, so both versions are equivalent |
| rest | — | — | inherits `Animation`'s `rate_func`/`remover`/`name`/`suspend_mobject_updating`/`reverse_rate_function`/`use_override` (see [Lifecycle and Common Parameters](../Common/01-Lifecycle-and-Common-Parameters.md)) |

> **Returns**: a `Create` instance.

#### Sample: every common parameter, letters drawn one after another by lag_ratio

A single Text takes the whole set of `Animation` common parameters: `lag_ratio=0.3` makes the letters stagger and appear one after another, and the rest are named one by one.

```python
from real_time_manim import Scene, Text, VGroup, BLUE, YELLOW, GREY_B, UP, DOWN, \
    smooth, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class CreateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Create", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l1 = Text("Create(mobject, lag_ratio=0.3, introducer=True,",
                  font_size=30, color=GREY_B)
        l2 = Text("         run_time=1.3, rate_func=smooth, remover=False, ...)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line "Create" signature label
        obj1 = Text("Create", font_size=52, color=BLUE).next_to(lab1, DOWN, buff=0.7)   # the letters drawn stroke by stroke
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(
            Create(obj1,                               # parameter "mobject"
                   lag_ratio=0.3,                      # parameter "lag_ratio": letters are drawn one after another
                   introducer=True,                    # parameter "introducer"
                   run_time=1.3,                       # parameter "run_time"
                   rate_func=smooth,                   # parameter "rate_func"
                   remover=False,                      # parameter "remover": kept after drawing
                   name="Create(Text)",                # parameter "name"
                   suspend_mobject_updating=True,      # parameter "suspend_mobject_updating"
                   reverse_rate_function=False,        # parameter "reverse_rate_function"
                   use_override=True),                 # parameter "use_override"
            run_time=1.3,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: it passes the whole set of `Animation` common parameters to `Create` in one go; watch `lag_ratio=0.3` in particular.

- `lag_ratio=0.3`: each letter of the Text is drawn with a 30% stagger in turn (the default `1.0` is one after another, and `0` grows all strokes at the same time).
- `rate_func=smooth`: the finish has easing.
- `remover=False`: the letters stay on screen after being drawn.
- `introducer=True`: the object does not need to be added to the scene by hand before playing.

<video src="assets/RTM output/01-Create-and-the-Drawing-Family-create.mp4" controls width="560"></video>

### `Write`

```python
Write(mobject, rate_func=linear, reverse=False, run_time=None, lag_ratio=None, **kwargs)
```

Inherits `Write(DrawBorderThenFill) ← DrawBorderThenFill(Animation)`. It simulates "handwriting / hand drawing": stroke the outline first, then fill, appearing stroke by stroke — the most commonly used entrance animation; `Text`, `Tex`, `MathTex` and any `VMobject` all work.

The default rate is `linear`. `run_time` and `lag_ratio` both default to `None` and are chosen automatically from the object's complexity (`run_time=1` when `length < 15`, otherwise `2`; `lag_ratio = min(4/length, 0.2)`); pass them explicitly and your values win. `reverse=True` turns it into "writing backwards" and automatically sets `remover=True`, `introducer=False`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vmobject` | `VMobject` | —(required) | the object to write out |
| `rate_func` | `Callable` | `linear` | **not advisable to change**: constant speed is what matches the intuition of handwriting |
| `reverse` | `bool` | `False` | `True` writes in reverse order and defaults to `remover=True` (removed once written) |
| `run_time` | `float \| None` | `None` | **accepts** any positive number; if not passed it is chosen from the length as `1` or `2` |
| `lag_ratio` | `float \| None` | `None` | **accepts** `0`~`1`; if not passed it is `min(4/max(1,length), 0.2)` |
| rest | — | — | `Animation` common parameters + `DrawBorderThenFill`'s `stroke_width=2`/`stroke_color=None` |

> **Returns**: a `Write` instance.

#### Sample: constant-speed linear handwriting overriding the automatic run_time / lag_ratio

"Hello Manim" is written out with `Write`, with `run_time=1.5` / `lag_ratio=0.2` overriding the length-based default.

```python
from real_time_manim import Scene, Text, VGroup, GREEN, YELLOW, GREY_B, UP, DOWN, \
    linear, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class WriteDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Write", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l3 = Text("Write(vmobject, rate_func=linear, reverse=False,",
                  font_size=30, color=GREY_B)
        l4 = Text("        run_time=1.5, lag_ratio=0.2, stroke_width=2, ...)",
                  font_size=30, color=GREY_B)
        lab2 = VGroup(l3, l4).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line "Write" signature label
        obj2 = Text("Hello Manim", font_size=48, color=GREEN).next_to(lab2, DOWN, buff=0.7)   # the text being written
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(
            Write(obj2,                                # parameter "vmobject"
                  rate_func=linear,                    # parameter "rate_func": constant-speed handwriting
                  reverse=False,                       # parameter "reverse": write in forward order
                  run_time=1.5,                        # parameter "run_time": overrides the automatic value
                  lag_ratio=0.2,                       # parameter "lag_ratio": overrides the automatic value
                  stroke_width=2,                      # parameter "stroke_width"
                  stroke_color=None),                  # parameter "stroke_color"
            run_time=1.5,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: `Write(obj2, rate_func=linear, run_time=1.5, lag_ratio=0.2, ...)` strokes the outline first, then fills, writing "Hello Manim" stroke by stroke. Only `linear`'s constant speed looks like handwriting; passing `run_time` / `lag_ratio` explicitly overrides the length-based default logic (see the note).

<video src="assets/RTM output/01-Create-and-the-Drawing-Family-write.mp4" controls width="560"></video>

> Note: when `run_time` / `lag_ratio` are not passed, `Write` chooses them from the letter count (`length<15` → `run_time=1`, otherwise `2`; `lag_ratio=min(4/max(1,length), 0.2)`) — pass them explicitly to control it precisely; the sample does exactly that.

### `DrawBorderThenFill`

```python
DrawBorderThenFill(mobject, run_time=2.0, stroke_width=2, stroke_color=None,
                   rate_func=double_smooth, introducer=True, **kwargs)
```

Inherits `DrawBorderThenFill(Animation)` (RTM's own implementation). It is a **two-stage animation that draws the outline first, then shows the fill**, and is also the direct parent of `Write`; but it has no automatic `lag_ratio` logic of its own and does not subdivide stroke by stroke, so it suits making a "shape with a fill" appear as a whole. RTM's own version does **no type checking**.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `VMobject` | —(required) | the vector object being animated; RTM's own version does no type checking |
| `run_time` | `float` | `2` | total duration (shared by the two stages). **accepts** any positive number |
| `rate_func` | `Callable` | `double_smooth` | each of the two stages gets one smoothing pass, giving the "pause, then fill" feel; **not advisable to change** |
| `stroke_width` | `float` | `2` | outline width in the first stage. **accepts** any positive number |
| `stroke_color` | `str \| None` | `None` | outline color; when `None` it takes the object's own stroke color (or its fill color if there is no stroke) |
| `introducer` | `bool` | `True` | add to the scene before playing (RTM's own version makes it an explicit parameter, default `True`, and `False` can be passed) |
| rest | — | — | `Animation` common parameters |

> **Returns**: a `DrawBorderThenFill` instance.

#### Sample: a blue stroke_width=6 outline + double_smooth stuttering fill

An orange solid square goes through both stages: a thick outline is stroked first with `stroke_width=6`, `stroke_color=BLUE`, then it pauses before filling orange.

```python
from real_time_manim import Scene, Text, Square, VGroup, BLUE, ORANGE, YELLOW, GREY_B, \
    UP, DOWN, double_smooth, DrawBorderThenFill, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class BorderFillDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-DrawBorderThenFill", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l5 = Text("DrawBorderThenFill(vmobject, run_time=1.8,",
                  font_size=30, color=GREY_B)
        l6 = Text("    rate_func=double_smooth, stroke_width=6,",
                  font_size=30, color=GREY_B)
        l7 = Text("    stroke_color=BLUE, introducer=True)",
                  font_size=30, color=GREY_B)
        lab3 = VGroup(l5, l6, l7).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # three-line signature label
        obj3 = (Square(side_length=1.8, color=ORANGE)
                .set_fill(ORANGE, 1.0).next_to(lab3, DOWN, buff=0.6))   # the filled orange square
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(
            DrawBorderThenFill(                        # parameter "vmobject"
                obj3,
                run_time=1.8,                          # parameter "run_time"
                rate_func=double_smooth,               # parameter "rate_func": one smoothing pass per stage
                stroke_width=6,                        # parameter "stroke_width": a thicker outline
                stroke_color=BLUE,                     # parameter "stroke_color": a blue outline
                introducer=True),                      # parameter "introducer"
            run_time=1.8,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: two stages — `DrawBorderThenFill` first strokes the square's outline with a `stroke_width=6` blue line (`stroke_color=BLUE`), `double_smooth` makes it pause between the two stages, then the orange fill comes in. Unlike `Write`, it does not subdivide stroke by stroke; the whole outline appears in one go.

<video src="assets/RTM output/01-Create-and-the-Drawing-Family-border_fill.mp4" controls width="560"></video>

### `ShowPartial` (abstract base class, not advisable to use directly)

```python
ShowPartial(mobject, **kwargs)
```

Inherits `ShowPartial(Animation)` (**this is a ManimCE class**: `ShowPartial` is not on RTM's export list of its own 39 animations, so it comes with the built-in ManimCE imported from the top level of `real_time_manim`).

It is an **abstract base class**, and in CE it is the parent of animations that "show only a part of the stroke each frame" (`Create`, `ShowPassingFlash`). At construction it checks whether the object has a `pointwise_become_partial` method, and raises `TypeError` if it does not.

Instantiating it directly reports `NotImplementedError("Please use Create or ShowPassingFlash")` when played, so **users should not use it directly**; it is listed here only to explain the inheritance chain on the CE side.

RTM's **own** `Create` / `ShowPassingFlash` are **not** its subclasses (each inherits `Animation` directly). Under RTM it can actually be played by passing it straight in: `real_time_manim/compat.py` patches `_get_bounds`, rendering with Create-style bounds.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `VMobject \| OpenGLVMobject \| OpenGLSurface` | —(required) | the object being animated |
| rest | — | — | `Animation` common parameters (this class has no extra parameters) |

> **Returns**: a `ShowPartial` instance (**do not play it directly**, use `Create` / `ShowPassingFlash`).

#### Sample: the abstract base class played straight, a circle drawn along its path

`ShowPartial(obj4, run_time=1.3, introducer=True)` is constructed and played once to see the "draw a part" effect it shares with `Create` (playable under RTM thanks to the compat patch).

```python
from real_time_manim import Scene, Text, Circle, YELLOW, GREY_B, UP, DOWN, \
    FadeIn, ShowPartial, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class ShowPartialDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-ShowPartial", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l8 = Text("ShowPartial(mobject, run_time=1.3, introducer=True)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        obj4 = Circle(radius=0.7, color=GREEN).next_to(l8, DOWN, buff=0.7)   # the circle drawn frame by frame
        win.play(FadeIn(l8, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(
            ShowPartial(obj4,                          # parameter "mobject"
                        run_time=1.3,                  # parameter "run_time"
                        introducer=True),              # parameter "introducer"
            run_time=1.3,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the abstract base class `ShowPartial(obj4, run_time=1.3)` is played straight — a green circle is drawn along its path from the start point to the end point, the same family as `Create`; its value is being the parent of `Create` / `ShowPassingFlash`, so normal code should not use it directly.

<video src="assets/RTM output/01-Create-and-the-Drawing-Family-showpartial.mp4" controls width="560"></video>

---

See also: [Lifecycle and Common Parameters](../Common/01-Lifecycle-and-Common-Parameters.md) · [Reverse Removal](02-Reverse-Removal.md) · [Revealing Subsets](03-Revealing-Subsets.md)
