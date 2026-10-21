# Saving state / in-place style (Restore, ScaleInPlace)

The `save_state()` + `Restore` pair for "mess it up, then put it back", plus `ScaleInPlace`, the in-place scaling animation whose meaning reads most plainly.

## Parameters

### Restore

```python
Restore(mobject, **kwargs)
```

Restores the object to **the state saved by the most recent `save_state()`** (position, size, colour, opacity…), often combined with `.animate` for "mess it up, then put it back".

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | you **must have called** `mobject.save_state()` first, otherwise it restores to the default state |
| `**kwargs` | … | — | common `Transform`/`Animation` parameters |

> **Returns**: a `Restore` instance (subclass of `Restore(ApplyMethod)` ← `Transform`).

### ScaleInPlace

```python
ScaleInPlace(mobject, scale_factor, **kwargs)
```

An animation wrapper for in-place scaling (equivalent to `ApplyMethod(m.scale, factor)`); its meaning reads more plainly than `.animate.scale()`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the object being scaled |
| `scale_factor` | `float` | — (required) | the scale factor |
| `**kwargs` | … | — | common `Transform`/`Animation` parameters |

> **Returns**: a `ScaleInPlace` instance (subclass of `ScaleInPlace(ApplyMethod)` ← `Transform`).

## Examples

#### Sample: Restore / ScaleInPlace

Page-specific sample (`assets/RTM code/03-Saving-State-and-Style-Transform.py`): first `sq.save_state()`, then use `.animate` to turn the square purple and enlarge it, and `Restore` with `run_time` / `rate_func` puts it back; `ScaleInPlace` uses the two non-default factors 1.8 / 0.6 to show in-place enlargement and shrinking.

```python
import os

from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    PURPLE,
    DOWN,
    LEFT,
    UP,
    Scene,
    Square,
    Text,
    VGroup,
    smooth,
)
# Restore / ScaleInPlace are not in RTM's export list; import them from real_time_manim with the bundled ManimCE; tested and working
from real_time_manim import Restore, ScaleInPlace
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_03_Saving_State_and_Style_Transform(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("Saving state / in-place style", font_size=44, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # --- 1. save_state() + .animate to mess it up ---
        lab1 = VGroup(
            Text("sq.save_state()", font_size=30, color=GREY_B),
            Text("sq.animate.set_color(PURPLE).scale(1.8)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        sq = Square(side_length=1.4, color=BLUE).set_fill(BLUE, 0.6).move_to(LEFT * 3.2 + DOWN * 1.2)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Create(sq), run_time=0.5)
        sq.save_state()                            # param save_state() ✓ (the prerequisite for Restore)
        win.play(sq.animate.set_color(PURPLE).scale(1.8), run_time=1.1)   # param .animate ✓
        win.play(FadeOut(lab1), run_time=0.45)

        # --- 2. Restore: go back to the most recent save_state() ---
        lab2 = Text("Restore(sq, run_time=1.2, rate_func=smooth)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Restore(sq, run_time=1.2, rate_func=smooth), run_time=1.2)   # param Restore(mobject) ✓
        win.play(FadeOut(VGroup(lab2, sq)), run_time=0.5)

        # --- 3. ScaleInPlace: in-place scaling, the factor reads plainly ---
        lab3 = VGroup(
            Text("ScaleInPlace(txt, 1.8, run_time=1.0)", font_size=30, color=GREY_B),
            Text("ScaleInPlace(txt, 0.6, run_time=1.0)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        txt = Text("ScaleInPlace", font_size=40, color=GREEN).move_to(DOWN * 1.3)
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(Write(txt), run_time=0.6)
        win.play(ScaleInPlace(txt, 1.8, run_time=1.0, rate_func=smooth), run_time=1.0)   # param scale_factor=1.8 ✓
        win.play(ScaleInPlace(txt, 0.6, run_time=1.0, rate_func=smooth), run_time=1.0)   # param scale_factor=0.6 ✓

        win.play(Wait(0.5))
        win.play(FadeOut(VGroup(title, lab3, txt)), run_time=0.6)
        win.close()                                 # param win.close()
```

What this code does: it first builds a blue square and calls `save_state()` while it is still "normal"; then uses `.animate` to turn it purple and enlarge it 1.8x (the messing-up phase); then a single `Restore(sq)` brings the square back to its archived size, colour and position. The third segment uses `ScaleInPlace` on green text, first enlarging it 1.8x and then shrinking it to 0.6x — the factor is written straight into the argument, so you never compute the target size yourself.

<video src="assets/RTM output/03-Saving-State-and-Style-Transform.mp4" controls width="560"></video>

> Note: `Restore` brings back **the most recent** `save_state()` snapshot — `save_state()` can be called many times, each overwriting the last; if you forget to call `save_state()` and call `Restore` directly, it restores the object's default state, which looks like "nothing happened".
>
> `Restore` / `ScaleInPlace` are not in RTM's export list; just import them from `real_time_manim` — they play fine in testing.

Not demonstrated: none — every visible parameter of the two classes on this page is shown explicitly.

See also: [Shrink and recolour](03b-Shrink-and-Recolor.md) · [Method- and function-driven transforms](02-Method-and-Function-Driven.md) · [Core Transform](01-Transform-Core.md)
