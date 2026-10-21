# Reverse removal: Uncreate / Unwrite / Add

This section covers the classes filed under "reverse removal":

- `Uncreate`: `Create` played backwards.
- `Unwrite`: simulates erasing text by hand.
- `Add`: the animated version of "put into the scene" — it erases nothing, but like the two above it controls objects entering and leaving the scene through an animation, and it can be sequenced on a timeline.

## Parameters

### `Uncreate`

```python
Uncreate(mobject, run_time=1.0, lag_ratio=1.0, remover=True,
         rate_func=None, reverse_rate_function=True, **kwargs)
```

Inherits `Uncreate(Create)`. It is `Create` played backwards: it **erases along the path in reverse** an object that has already been drawn, and removes the object from the scene when it finishes by default. The difference from `FadeOut`: it is a "reverse redraw" that exposes the stroke path, whereas `FadeOut` fades the whole thing's opacity out.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `VMobject` | —(required) | the vector object to erase |
| `reverse_rate_function` | `bool` | `True` | play backwards. Since 2026-10-16 it defaults to CE's `smooth(1-t)` curve (this parameter can be passed explicitly); it is no longer a linear reverse |
| `remover` | `bool` | `True` | remove from the scene when finished; **not advisable** to change it to `False` (after erasing, staying in the scene is usually not what you want) |
| `introducer` | `bool` | `False` | the RTM version **accepts** it (it goes through `Animation`'s default `False`; passing `True` explicitly takes effect)
| `run_time` / `lag_ratio` | `float` | `1.0` / `1.0` | same defaults as `Create` |
| rest | — | — | `Create`/`Animation` common parameters (`rate_func=smooth`, etc.) |

> **Returns**: an `Uncreate` instance.

#### Sample: draw first, then erase backwards along the path

First `Create` draws a blue square, then the five `Uncreate` parameters are named one by one to play it back and erase it, removing it from the scene when finished.

```python
from real_time_manim import Scene, Text, Square, VGroup, BLUE, YELLOW, GREY_B, UP, DOWN, \
    smooth, Create, FadeIn, Uncreate, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class UncreateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-Uncreate", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l1 = Text("Uncreate(mobject, reverse_rate_function=True, remover=True,",
                  font_size=30, color=GREY_B)
        l2 = Text("         lag_ratio=1.0, run_time=1.2, rate_func=smooth)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line "Uncreate" signature label
        sq = Square(side_length=1.6, color=BLUE).next_to(lab1, DOWN, buff=0.6)   # the blue square to draw first and erase later
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(Create(sq, run_time=1.0), run_time=1.0)   # draw the square first
        win.play(
            Uncreate(sq,                            # parameter "mobject"
                     reverse_rate_function=True,    # parameter "reverse_rate_function": play backwards
                     remover=True,                  # parameter "remover": removed from the scene once erased
                     lag_ratio=1.0,                 # parameter "lag_ratio"
                     run_time=1.2,                  # parameter "run_time"
                     rate_func=smooth),             # parameter "rate_func"
            run_time=1.2,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: first `Create(sq, run_time=1.0)` draws the blue square completely, then `Uncreate(sq, reverse_rate_function=True, remover=True, lag_ratio=1.0, run_time=1.2, rate_func=smooth)` erases back along the same path — on screen it "disappears stroke by stroke", and the whole square leaves the scene once erased. The reverse playback comes from `reverse_rate_function=True` (it is the default; it is named one by one here just to make it clear).

<video src="assets/RTM output/02-Reverse-Removal-uncreate.mp4" controls width="560"></video>

### `Unwrite`

```python
Unwrite(mobject, rate_func=linear, reverse=True, run_time=1.0, **kwargs)
```

Inherits `Unwrite(Write) ← DrawBorderThenFill(Animation)`. It simulates erasing text/shapes by hand: the picture goes **from complete → gone** (`_apply_two_phase` computes `rate_func(1 - sub_alpha)` by hand).

`reverse` only decides **which end to erase from** — `True` (default) erases the last submobject first, `False` starts from the first submobject. `run_time` **explicitly defaults to `1.0`** (the RTM version does not take `Write`'s "choose from the length"), and `lag_ratio` is still chosen automatically as `min(4/length, 0.2)` when not passed.

The inherited `DrawBorderThenFill.interpolate` **reads `reverse_rate_function`** (it flips `alpha` first, then hands it to the reverse computation above), so passing `True` flips the picture once more.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `VMobject` | —(required) | the object to erase |
| `rate_func` | `Callable` | `linear` | **not advisable to change**: constant-speed erasing best matches the intuition of "erasing by hand" |
| `reverse` | `bool` | `True` | `True`: erase from the last submobject; `False`: from the first. In the RTM version `reverse` **no longer drags `remover` along** (`remover` is on the next line) |
| `run_time` | `float` | `1.0` | **accepts** any positive number. The RTM version **hard-codes the default to `1.0`** and does not choose from the length |
| `lag_ratio` | `float \| None` | `None` (→ automatic) | **accepts** `0`~`1`; when not passed it is `min(4/max(1,length), 0.2)` |
| `remover` | `bool` | `False` | In the RTM version it is **always `False`** by default and **no longer linked to `reverse`**. On the RTM side the stroke/submobject progress is set to 0 so it becomes invisible, but `Unwrite` has no `clean_up_from_scene` of its own (the base class is `pass`), so **it is not detached from the scene when finished** — even passing `remover=True` explicitly cannot detach it, only the attribute value changes |
| `reverse_rate_function` | `bool` | `False` | measured to **work** (the inherited `DrawBorderThenFill.interpolate` flips `alpha` by it first and then hands it to the reverse computation): the default `False` = erase from complete to gone; passing `True` flips once more so the picture goes back to "from nothing to complete". The RTM version defaults to `False`, the ManimCE version to `True` (the two defaults are opposite); the finished `unwrite` on this page uses the **CE version imported at the top level** (see the "import" note above), so it aligns with CE frame by frame and does not imply that the RTM version's intermediate frames match frame by frame too |
| rest | — | — | `Write`/`DrawBorderThenFill`/`Animation` common parameters |

> **Returns**: an `Unwrite` instance.

#### Sample: constant-speed linear erasing by hand, reverse=False erasing from the start

Write out "Goodbye Manim" first, then use the non-default `reverse=False` to erase by hand from the first letter, with `run_time`/`lag_ratio` explicitly overriding the automatic values.

```python
from real_time_manim import Scene, Text, VGroup, GREEN, YELLOW, GREY_B, UP, DOWN, \
    linear, FadeIn, Unwrite, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class UnwriteDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-Unwrite", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l3 = Text("Unwrite(vmobject, rate_func=linear, reverse=False,",
                  font_size=30, color=GREY_B)
        l4 = Text("        run_time=1.4, lag_ratio=0.2)",
                  font_size=30, color=GREY_B)
        lab2 = VGroup(l3, l4).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line "Unwrite" signature label
        txt = Text("Goodbye Manim", font_size=44, color=GREEN).next_to(lab2, DOWN, buff=0.6)   # the text to write first and erase later
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(Write(txt, rate_func=linear, run_time=1.0), run_time=1.0)   # write the text first
        win.play(
            Unwrite(txt,                            # parameter "vmobject"
                    rate_func=linear,               # parameter "rate_func": constant-speed erasing by hand
                    reverse=False,                  # parameter "reverse": non-default, erase from the start
                    run_time=1.4,                   # parameter "run_time"
                    lag_ratio=0.2),                 # parameter "lag_ratio"
            run_time=1.4,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: first `Write(txt, rate_func=linear, run_time=1.0)` writes out "Goodbye Manim", then `Unwrite(txt, rate_func=linear, reverse=False, run_time=1.4, lag_ratio=0.2)` erases by hand; `reverse=False` is the non-default direction — erase from the **first** submobject (the default `True` erases from the last). The RTM version does **not** remove it from the scene automatically when finished (`remover` is always `False`, it only sets the progress to 0), so the text stays on screen after being erased.

<video src="assets/RTM output/02-Reverse-Removal-unwrite.mp4" controls width="560"></video>

> Note: `Unwrite`'s reversal is computed by hand inside the class as `rate_func(1-alpha)`. Although `reverse_rate_function` is not a parameter of `Unwrite` itself, the inheritance chain reads it: the default `False` erases from complete to gone, and passing `True` flips once more (see the parameter table). In the RTM version `run_time` **defaults to a hard-coded `1.0`** and is not chosen from the length; `lag_ratio` is still automatic when not passed.
>
> The demo's `Uncreate` / `Unwrite` / `Create` / `Write` on this page are imported from the **top level** of `real_time_manim`; the **RTM version must use `from real_time_manim.vulkan_bind import`**, and the two versions have several opposite defaults. The sample explicitly passes `run_time=1.4, lag_ratio=0.2` and `reverse=False`, so the picture direction is the same.

### `Add`

```python
Add(*mobjects, run_time=0.0, **kwargs)
```

Inherits `Add(Animation)`. It is the animation version of putting one or more mobjects **instantly into the scene**, equivalent to `Scene.add`, but because it is an animation it can be combined by `Succession`/`AnimationGroup` and sequenced on a timeline. Multiple mobjects are combined into one `Group`; the default `run_time=0.0` means "insertion is completion", and `run_time>0` turns it into "stay this long after putting it in".

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | —(required) | one or more; more than 1 is wrapped into a `Group` internally |
| `run_time` | `float` | `0.0` | how long to stay after being added (the insertion itself is instantaneous). **accepts** `0` or any positive number |
| `introducer` | `bool` | `False` | RTM's own `Add` **does not fix** this parameter (it goes through `Animation`'s default `False`; passing `True` explicitly takes effect) |
| rest | — | — | `Animation` common parameters |

> **Returns**: an `Add` instance.

#### Sample: Add sequenced on a Succession timeline, instant add vs half-second hold

Three dots in a yellow box enter the scene in two batches: the green dot `run_time=0.0` is added instantly, and after 0.4 seconds the red and blue dots are wrapped into a `Group`, added together and held for half a second — all sequenced on one `Succession` timeline.

```python
from real_time_manim import Scene, Text, Rectangle, Circle, BLUE, GREEN, RED, YELLOW, \
    GREY_B, UP, DOWN, LEFT, RIGHT, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait, Succession, Add

class AddDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-Add", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l5 = Text("Add(*mobjects, run_time=0.0 instant / 0.5 hold) in Succession",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        rect = (Rectangle(width=3.4, height=1.4, color=YELLOW)
                .next_to(l5, DOWN, buff=0.6))   # the yellow box holding the dots
        dot_a = Circle(radius=0.16, color=GREEN).move_to(rect.get_left() + RIGHT * 0.7)   # the first dot to be added
        dot_b = Circle(radius=0.16, color=RED).move_to(rect.get_center() + RIGHT * 0.7)   # the second dot to be added
        dot_c = Circle(radius=0.16, color=BLUE).move_to(rect.get_right() + LEFT * 0.7)   # added in the same group as "dot_b"
        win.play(FadeIn(l5, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(Create(rect, run_time=0.8), run_time=0.8)   # draw the yellow box
        win.play(
            Succession(
                Add(dot_a, run_time=0.0),           # parameter "run_time=0.0": added instantly
                Wait(0.4),                          # 0.4s gap
                Add(dot_b, dot_c, run_time=0.5),    # more than 1 is wrapped into a Group; run_time=0.5 holds for half a second
            ),
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: after the yellow box is drawn, one `Succession` lines up three steps — `Add(dot_a, run_time=0.0)` brings the green dot into the scene instantly (insertion is completion), `Wait(0.4)` waits 0.4 seconds, and `Add(dot_b, dot_c, run_time=0.5)` wraps the red and blue dots into a `Group`, adds them together and holds for half a second. The three dots only appear once each reaches its own slot, neatly contrasting `run_time=0` (instant) with `run_time>0` (hold after adding).

<video src="assets/RTM output/02-Reverse-Removal-add.mp4" controls width="560"></video>

> Note: two or more mobjects are wrapped by `Add` into a `Group` and played as one animation (in the sample, `dot_b` and `dot_c`).
>
> The demo on this page keeps the style of importing `Add` / `Succession` from `real_time_manim.vulkan_bind`. The earlier interop problem — "manim `Succession` holding an RTM `Wait` raised `TypeError`, and manim `Add` was not registered into the scene" — **has been fixed** (`window/patches.py`: `prepare_animation` rebinding in the composition/scene modules + `_RtmAnimationAdapter` semantics bridging + manim `Add` recognition, test `tests/test_gap_interop.py`), and importing both from `manim` now works too. Playing `win.play(Add(x))` directly is equivalent to `self.add(x)`, but it can take `run_time`.

---

See also: [Create and the drawing family](01-Create-and-the-Drawing-Family.md) · [Revealing Subsets](03-Revealing-Subsets.md) · [The Fade family](../Fades/01-The-Fade-Family.md)
