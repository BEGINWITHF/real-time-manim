# Updater animations and updater tools: UpdateFromFunc and friends

All three animation classes drive object state during playback with a per-frame callback.

They come from manim's own `animation/updaters/update.py` — they are not in RTM's `vulkan_bind` export list, but RTM's render hooks take over as usual. Rendered and verified; the two engines align frame by frame.

For the 12.1 updater utility functions and the objects that change automatically, see [01b-Updater-Tools](01b-Updater-Tools.md).

## Parameters

### `UpdateFromFunc` 

```python
UpdateFromFunc(mobject, update_function, suspend_mobject_updating=False, **kwargs)
```

During playback it **calls `update_function(mobject)` every frame** to drive the object's state; suited to "one object's state depends on another object that is moving" (for example, a line that always connects two moving dots).

Its `rate_func` is not passed to the function; what it does is up to the function itself. **Inherits** `UpdateFromFunc(Animation)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the object being driven |
| `update_function` | `Callable[[Mobject], Any]` | — | called every frame; the argument is that mobject |
| `suspend_mobject_updating` | `bool` | `False` | whether to suspend its own updater (**keep `False`** so it can coexist with this animation) |
| `**kwargs` | … | — | common `Animation` parameters (`run_time` must be given explicitly, otherwise it stops calling after 1 second) |

> **Returns**: an `UpdateFromFunc` instance.

Quick start:

```python
dot = Dot()
label = Text("hi").next_to(dot, UP)
self.add(dot, label)
win.play(dot.animate.shift(RIGHT * 3),
          UpdateFromFunc(label, lambda l: l.next_to(dot, UP), run_time=3),
          rate_func=linear)
```

### `UpdateFromAlphaFunc` 

```python
UpdateFromAlphaFunc(mobject, update_function, suspend_mobject_updating=False, **kwargs)
```

Same as above, but the callback receives one extra **progress argument**: `update_function(mobject, rate_func(alpha))`. `alpha` advances monotonically from 0 to 1, suited to "interpolate to some state by progress". **Inherits** `UpdateFromAlphaFunc(UpdateFromFunc)` — **it has no `__init__` of its own**; it only overrides how interpolation is done.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the object being driven |
| `update_function` | `Callable[[Mobject, float], Any]` | — | the second argument is the progress after `rate_func` |
| `suspend_mobject_updating` | `bool` | `False` | whether to suspend the built-in updater |
| `**kwargs` | … | — | common `Animation` parameters |

> **Returns**: an `UpdateFromAlphaFunc` instance.

Quick start:

```python
sq = Square()
self.add(sq)
win.play(UpdateFromAlphaFunc(sq, lambda m, a: m.set_fill(RED, opacity=a), run_time=2))
```

### `MaintainPositionRelativeTo` 

```python
MaintainPositionRelativeTo(mobject, tracked_mobject, **kwargs)
```

During playback it keeps the **relative displacement at the start** between `mobject` and `tracked_mobject` unchanged: when the latter moves, the former follows. No docstring; compiled from the source. **Inherits** `MaintainPositionRelativeTo(Animation)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the follower |
| `tracked_mobject` | `Mobject` | — | the one being followed |
| `**kwargs` | … | — | common `Animation` parameters |

> **Returns**: a `MaintainPositionRelativeTo` instance.

Quick start:

```python
a, b = Dot(LEFT * 2), Dot(RIGHT * 2)
self.add(a, b)
win.play(a.animate.shift(UP * 2), MaintainPositionRelativeTo(b, a, run_time=2))
```

#### Sample: UpdateFromFunc / UpdateFromAlphaFunc / MaintainPositionRelativeTo item by item

The finished clip for this page demonstrates one segment each in the order UpdateFromFunc → UpdateFromAlphaFunc → MaintainPositionRelativeTo, with every parameter labelled on screen.

```python
import os

from real_time_manim import (
    GREEN,
    GREY_B,
    PURPLE,
    RED,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Dot,
    Scene,
    Square,
    Text,
    UpdateFromAlphaFunc,
    UpdateFromFunc,
    MaintainPositionRelativeTo,
    VGroup,
    linear,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  used by __main__ at the end of the file


class Page_01_Updater_Animations(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w=1280 / h=720 / hidden=True
        win.scene = self                          # param win.scene

        title = Text("UpdateFromFunc / UpdateFromAlphaFunc / MaintainPositionRelativeTo",
                     font_size=24, color=GREEN).to_edge(UP)   #title uses ASCII only: two-engine font fallback is more stable
        win.play(Write(title), run_time=0.85)

        # —— Step 1: UpdateFromFunc(mobject, update_function, suspend..., run_time) ——
        s1a = Text("UpdateFromFunc(label, lambda l: l.next_to(dot, UP),",
                   font_size=28, color=GREY_B)
        s1b = Text("    suspend_mobject_updating=False, run_time=2.4)",
                   font_size=28, color=GREY_B)
        sig1 = VGroup(s1a, s1b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        dot = Dot(radius=0.12, color=RED).next_to(sig1, DOWN, buff=1.1).shift(LEFT * 3.5)
        label = Text("hi", font_size=40, color=RED).next_to(dot, UP, buff=0.3)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        self.add(dot, label)
        win.play(                                    # params mobject=dot + drives label every frame
            dot.animate.shift(RIGHT * 7),
            UpdateFromFunc(
                label,                               # param mobject ✓
                lambda l: l.next_to(dot, UP),        # param update_function ✓ (called every frame)
                suspend_mobject_updating=False,      # param suspend_mobject_updating=False ✓
                run_time=2.4,                        # param **kwargs: run_time=2.4 ✓ (must be given explicitly)
            ),
            rate_func=linear,
        )
        win.play(FadeOut(sig1), FadeOut(dot), FadeOut(label), run_time=0.45)

        # —— Step 2: UpdateFromAlphaFunc(mobject, update_function, ...) ——
        s2a = Text("UpdateFromAlphaFunc(sq, lambda m, a: m.set_fill(RED, opacity=a),",
                   font_size=26, color=GREY_B)
        s2b = Text("    suspend_mobject_updating=False, run_time=2.0)",
                   font_size=26, color=GREY_B)
        sig2 = VGroup(s2a, s2b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        sq = Square(side_length=2.0, color=GREEN).next_to(sig2, DOWN, buff=0.6)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        self.add(sq)
        win.play(
            UpdateFromAlphaFunc(
                sq,                                   # param mobject ✓
                lambda m, a: m.set_fill(RED, opacity=a),   # param update_function ✓ (receives one extra progress argument)
                suspend_mobject_updating=False,       # param suspend_mobject_updating=False ✓
                run_time=2.0,                         # param **kwargs: run_time=2.0 ✓
            ),
        )
        win.play(FadeOut(sig2), FadeOut(sq), run_time=0.45)

        # —— Step 3: MaintainPositionRelativeTo(mobject, tracked_mobject, **kwargs) ——
        s3a = Text("MaintainPositionRelativeTo(b, a, run_time=2.2)",
                   font_size=30, color=GREY_B)
        sig3 = s3a.next_to(title, DOWN, buff=0.4)
        a = Dot(radius=0.14, color=GREEN).next_to(sig3, DOWN, buff=1.1).shift(LEFT * 2)
        b = Dot(radius=0.14, color=PURPLE).next_to(a, RIGHT, buff=1.2)
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.45)
        self.add(a, b)
        win.play(                                    # params mobject=b / tracked_mobject=a
            a.animate.shift(RIGHT * 2.5 + DOWN * 0.9),
            MaintainPositionRelativeTo(
                b,                                   # param mobject (the follower) ✓
                a,                                   # param tracked_mobject (the one followed) ✓
                run_time=2.2,                        # param **kwargs: run_time=2.2 ✓
            ),
            rate_func=linear,
        )
        win.play(FadeOut(sig3), FadeOut(a), FadeOut(b), run_time=0.5)

        win.play(FadeOut(title), run_time=0.5)
        win.close()
```

What this code does: all three segments are "per-frame callbacks".

- Segment 1: a red dot travels 7 units from left to right, and `UpdateFromFunc` makes the "hi" label re-run `next_to(dot, UP)` every frame so it sticks to the dot — the callback only receives the object; what it does is up to it.
- Segment 2: a green square uses `UpdateFromAlphaFunc` to turn its fill red by progress `a` (`opacity=a` fades in from transparent to solid).
- Segment 3: a green dot moves, and a purple dot follows it with `MaintainPositionRelativeTo`, keeping the initial relative displacement.

All three callbacks use `suspend_mobject_updating=False`, coexisting with the objects' built-in updaters.

<video src="assets/RTM output/01-Updater-Animations.mp4" controls width="560"></video>

> Note:
>
> - `UpdateFromFunc`'s `run_time` **must be given explicitly**. If you don't, the internal default of 1 second stops calling the callback and your object stalls halfway.
> - Keep `suspend_mobject_updating` at `False`. Passing `True` suspends the object's own updater too, which breaks "per-frame driving".
> - `UpdateFromAlphaFunc`'s callback receives one extra progress argument (already processed by `rate_func`); a wrong signature throws on the first frame.

See also: [Updater utility functions and auto-changing objects](01b-Updater-Tools.md) · [Updaters (Mobject methods)](../../02-Mobjects/08-Updaters.md) · [ValueTracker](../../02-Mobjects/10-ValueTracker.md)
