# Method- and function-driven transforms

Instead of writing a target by hand, you turn "call some method / function" straight into an animation: it copies the object, runs the call on the copy, then interpolates the original over to it. One step fewer than `Transform` ("set up the target first").

## Parameters

### ApplyMethod

```python
ApplyMethod(method, *args, **kwargs)
```

Turns "call a mobject method" into an animation: internally it copies the object, runs `method(*args)` on the copy to get the target, then interpolates the original over to it. **You must pass a bound method, and the method must return a mobject**; writing `sq.shift(RIGHT)` (already called) raises `ValueError`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `method` | `Callable` (a bound method) | — (required) | e.g. `sq.shift`, `sq.set_color`, `sq.rotate` |
| `*args` | any | — | positional arguments passed to the method; **the last slot may hold a dict**, which is treated as the method's keyword arguments |
| `**kwargs` | … | — | forwarded to `Transform`/`Animation` (`run_time`, `rate_func`, `path_arc`…) |

> **Returns**: an `ApplyMethod` instance (subclass of `ApplyMethod(Transform)`).

### ApplyFunction

```python
ApplyFunction(function, mobject, **kwargs)
```

Turns any **pure function** `mobject copy -> mobject` into an animation (more freedom than `ApplyMethod`); if the return value is not a `Mobject` it raises `TypeError`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `function` | `Callable[[Mobject], Mobject]` | — (required) | takes a copy of the mobject and returns a new mobject |
| `mobject` | `Mobject` | — (required) | the object being transformed |
| `**kwargs` | … | — | common `Transform`/`Animation` parameters |

> **Returns**: an `ApplyFunction` instance (subclass of `ApplyFunction(Transform)`).

### ApplyPointwiseFunction

```python
ApplyPointwiseFunction(function, mobject, run_time=3.0, **kwargs)
```

Applies a `point -> point` function to **every point** (internally calls `mobject.apply_function`), for warping / bending shapes.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `function` | `Callable[[np.ndarray], np.ndarray]` | — (required) | coordinate -> coordinate |
| `mobject` | `Mobject` | — (required) | the object being transformed |
| `run_time` | `float` | `3.0` | duration (constant `DEFAULT_POINTWISE_FUNCTION_RUN_TIME`) |
| `**kwargs` | … | — | common `Transform`/`Animation` parameters |

> **Returns**: an `ApplyPointwiseFunction` instance (subclass of `ApplyPointwiseFunction(ApplyMethod)` ← `Transform`).

## Examples

#### Sample: ApplyMethod / ApplyFunction / ApplyPointwiseFunction

Page-specific sample (`assets/RTM code/02-Method-and-Function-Driven.py`) covers four usages:

- `ApplyMethod`, two segments: a bound method + a positional argument + `run_time` / `path_arc` / `rate_func` forwarding; a dict in the last `*args` slot as the method's keyword argument `{'about_edge': UP}`.
- `ApplyPointwiseFunction`, one segment: point-by-point warping into a wave, `run_time=1.5` overriding the default 3.0.
- `ApplyFunction`, one segment: a pure function, copy -> new object.

```python
import os

import numpy as np
from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    RED,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Scene,
    Square,
    Text,
    VGroup,
    smooth,
)
# ApplyMethod / ApplyFunction / ApplyPointwiseFunction are not in RTM's export list;
# import them from real_time_manim (= the bundled native ManimCE version); tested and win.play plays them fine
from real_time_manim import ApplyFunction, ApplyMethod, ApplyPointwiseFunction
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    Wait,  # noqa: F401
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_02_Method_and_Function_Driven(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("Method / function-driven transforms", font_size=44, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        m = Square(side_length=1.6, color=BLUE).set_fill(BLUE, 0.6).move_to(LEFT * 4.0 + DOWN * 1.2)

        # --- 1. ApplyMethod: a bound method + a positional argument + **kwargs ---
        lab1 = VGroup(
            Text("ApplyMethod(m.shift, RIGHT * 4.5,", font_size=30, color=GREY_B),
            Text("            run_time=1.1, path_arc=0.6)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Create(m), run_time=0.5)
        win.play(                                   # "calling a method" turned into an animation
            ApplyMethod(m.shift, RIGHT * 4.5,       # params method + *args ✓ (bound method + positional argument)
                        run_time=1.1,               # param run_time ✓
                        path_arc=0.6,               # param path_arc ✓ (**kwargs forwarded to Transform)
                        rate_func=smooth),          # param rate_func ✓
            run_time=1.1,
        )
        win.play(FadeOut(lab1), run_time=0.45)

        # --- 2. ApplyMethod: a dict in the last *args slot is treated as the method's keyword arguments ---
        lab2 = Text("ApplyMethod(m.scale, 1.5, {'about_edge': UP})",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(                                   # scale with the top edge fixed (about_edge=UP applies only to the copy)
            ApplyMethod(m.scale, 1.5, {'about_edge': UP}, run_time=1.0),
            run_time=1.0,
        )
        win.play(FadeOut(lab2), run_time=0.45)

        # --- 3. ApplyPointwiseFunction: every point goes its own way ---
        lab3 = VGroup(
            Text("ApplyPointwiseFunction(lambda p: p +", font_size=30, color=GREY_B),
            Text("  0.5 * np.sin(p[1] * 2) * RIGHT, m,", font_size=30, color=GREY_B),
            Text("  run_time=1.5)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.3)
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(                                   # each point shifts horizontally by its own y coordinate -> the square turns into a wave
            ApplyPointwiseFunction(lambda p: p + 0.5 * np.sin(p[1] * 2) * RIGHT, m,
                                   run_time=1.5),    # param run_time ✓ (default 3.0)
            run_time=1.5,
        )
        win.play(FadeOut(lab3), run_time=0.45)

        # --- 4. ApplyFunction: any pure function (copy -> new object) ---
        lab4 = VGroup(
            Text("ApplyFunction(lambda m: m.scale(0.6)", font_size=30, color=GREY_B),
            Text("  .set_color(GREEN), m, run_time=1.1)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        win.play(FadeIn(lab4, shift=DOWN), run_time=0.4)
        win.play(                                   # pure function: takes the copy and returns a new object
            ApplyFunction(lambda m: m.scale(0.6).set_color(GREEN), m, run_time=1.1),
            run_time=1.1,
        )

        win.play(FadeOut(VGroup(title, lab4, m)), run_time=0.6)
        win.close()                                 # param win.close()
```

What this code does: the same blue square is "turned into another shape" four different ways.

- (1) `ApplyMethod(m.shift, RIGHT * 4.5)` translates it to the right along a 0.6-radian arc.
- (2) then `ApplyMethod(m.scale, 1.5, {'about_edge': UP})` scales it with the top edge fixed (the last dict is fed to `scale` as-is).
- (3) `ApplyPointwiseFunction` shifts every point horizontally by its own y coordinate, twisting the square into a wave.
- (4) finally, `ApplyFunction`'s pure function scales the copy to 0.6x and turns it green.

<video src="assets/RTM output/02-Method-and-Function-Driven.mp4" controls width="560"></video>

> Note: `ApplyMethod` / `ApplyFunction` / `ApplyPointwiseFunction` are **not in RTM's export list**; import them directly from `real_time_manim`, and `win.play(...)` plays them fine in testing.
>
> - don't write the `ApplyMethod` argument as `sq.shift(RIGHT)` — that is an already-called return value, not a bound method, and raises `ValueError`; `m.shift` (without parentheses) is the right form.
> - `ApplyPointwiseFunction`'s default `run_time` is 3.0 (`DEFAULT_POINTWISE_FUNCTION_RUN_TIME`), noticeably longer than other animations; the sample overrides it to 1.5 explicitly.

See also: [Core Transform](01-Transform-Core.md) · [More function-driven transforms](02b-More-Function-Driven.md) · [Saving state / in-place style](03-Saving-State-and-Style-Transform.md)
