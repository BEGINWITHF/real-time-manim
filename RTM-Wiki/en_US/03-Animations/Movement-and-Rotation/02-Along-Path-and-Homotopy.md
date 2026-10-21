# Moving along a path and homotopy (MoveAlongPath / Homotopy)

The two main classes from the manual's "7.2 Move along a path" and "7.3 Homotopy (pointwise function driven)": one advances an object proportionally along a vector path, the other remaps the whole shape point by point with `(x, y, z, t) -> (x', y', z')`.

Both classes are verified renderable (they go through the RTM-native implementation), and the two samples each have their own clip. The other three classes in the same section are in [More Homotopy Classes](02b-More-Homotopy-Classes.md).

## Parameters

### MoveAlongPath

```python
MoveAlongPath(mobject, path, suspend_mobject_updating=False, **kwargs)
```

Inherits `MoveAlongPath(Animation)`, from `animation/movement.py`. It advances an object **proportionally along another VMobject's path** (each frame it takes `path.point_from_proportion(rate_func(alpha))` and does `move_to`); this is the standard answer for "a point tracing a trajectory" and "an object moving along a curve".

Note: it only moves the position, it does not change the orientation.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the object being moved |
| `path` | `VMobject` | — | the path. **accepts** only vector objects: `Line`, `Arc`, `Circle`, a custom `VMobject`… |
| `suspend_mobject_updating` | `bool` | `False` | whether to suspend updaters (keep `False` when the path needs updaters; with a path that has none, `True`/`False` look the same) |
| `**kwargs` | `Any` | — | `Animation` common parameters (`run_time`, `rate_func`, `lag_ratio`…) |

> **Returns**: `Animation` (hand it to `play` to play it).

#### Sample: an orange dot laps a drawn circular path once

A grey circular path is drawn first (so the trajectory is visible), and an orange dot walks a full lap along it at constant rate.

```python
from real_time_manim import Scene, Text, Circle, Dot, GREY_B, ORANGE, YELLOW, UP, DOWN, \
    Create, FadeIn, Write, linear
from real_time_manim.vulkan_bind import MLWindow, MoveAlongPath, Wait

class MoveAlongPathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("02-MoveAlongPath", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        sig = Text("MoveAlongPath(dot, path, run_time=2.0, rate_func=linear)",
                   font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        path = Circle(radius=1.9, color=GREY_B).shift(DOWN * 0.9)   # grey circular path
        dot = Dot(radius=0.14, color=ORANGE).move_to(path.point_from_proportion(0.0))   # orange dot at the start point
        win.play(FadeIn(sig, shift=DOWN), FadeIn(dot), run_time=0.4)   # fade in the label and the dot
        win.play(Create(path, run_time=0.8, rate_func=linear))   # draw the path (so the trajectory is visible)
        win.play(MoveAlongPath(dot, path, run_time=2.0, rate_func=linear))   # parameter "path / run_time / rate_func"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: it first uses `Create` to draw the grey circular path itself, then `MoveAlongPath(dot, path, run_time=2.0, rate_func=linear)` moves the orange dot onto the trajectory each frame by taking `path.point_from_proportion(alpha)` — only the position moves, the orientation does not change. `rate_func=linear` makes the whole lap even.

<video src="assets/RTM output/02-Along-Path-and-Homotopy-movealongpath.mp4" controls width="560"></video>

> Note:
>
> - `rate_func` directly decides the speed curve along the path: `linear` is constant rate, `smooth` is slow at both ends and fast in the middle.
> - Change the path's shape and the next point sampled changes with it, which is why a path makes sense as a visible trajectory line.

### Homotopy

```python
Homotopy(homotopy, mobject, run_time=3, apply_function_kwargs=None, **kwargs)
```

Inherits `Homotopy(Animation)`, from `animation/movement.py`. It **remaps the whole shape point by point** through the function you give, `(x, y, z, t) -> (x', y', z')`, with `t` going from 0 to 1.

It can produce whole-body continuous deformations such as "a block pushed into a wave" or "slime flowing".

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `homotopy` | `Callable[[float, float, float, float], tuple]` | — | inputs the old coordinates and the time, outputs the new coordinates. **accepts** any four-argument function (e.g. `lambda x, y, z, t: (x, y + .3*np.sin(x+2*PI*t), z)`) |
| `mobject` | `Mobject` | — | the object being deformed (recomputed each frame from a copy of the start state) |
| `run_time` | `float` | `3` | duration (seconds) |
| `apply_function_kwargs` | `dict \| None` | `None` | parameters forwarded to `Mobject.apply_function` (e.g. `about_point` / `about_edge`). Already accepted and forwarded (completed 2026-10-16, test `tests/test_gap_transform_motion.py`): an illegal key raises `TypeError` at construction time; when not passed the behaviour is bit-for-bit identical to before |
| `**kwargs` | `Any` | — | `Animation` common parameters (`rate_func`…) |

> **Returns**: `Animation` (hand it to `play` to play it).

#### Sample: a rectangle remapped point by point into a wavy band

A yellow rectangle is remapped frame by frame by `wave(x, y, z, t)` over 2 seconds into an undulating wavy band.

```python
import numpy as np

from real_time_manim import Scene, Text, Rectangle, GREY_B, YELLOW, UP, DOWN, \
    FadeIn, Write, linear
from real_time_manim.vulkan_bind import MLWindow, Homotopy, Wait

class HomotopyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("02-Homotopy", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        sig = Text("Homotopy(wave, rect, run_time=2.0, rate_func=linear)",
                   font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        rect = Rectangle(width=4.4, height=1.6, color=YELLOW).set_fill(YELLOW, 0.35).shift(DOWN * 1.2)   # yellow rectangle
        win.play(FadeIn(sig, shift=DOWN), FadeIn(rect), run_time=0.4)   # fade in the label and the rectangle

        def wave(x, y, z, t):   # parameter "homotopy": (x, y, z, t) -> (x', y', z')
            return (x, y + 0.45 * np.sin(2.2 * x + 2.0 * np.pi * t), z)

        win.play(Homotopy(wave, rect, run_time=2.0, rate_func=linear))   # parameter "homotopy / run_time / rate_func"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: `Homotopy(wave, rect, run_time=2.0, rate_func=linear)` remaps each vertex of the rectangle frame by frame through `wave(x, y, z, t)` over 2 seconds — a sine that varies with `x` and the time is added along `y`, so the rectangle becomes a wavy band undulating back and forth.

`t` goes from 0 to 1 and the function leaves no residual displacement, so it returns to its original shape at the end.

<video src="assets/RTM output/02-Along-Path-and-Homotopy-homotopy.mp4" controls width="560"></video>

> Note: `Homotopy` recomputes each frame from a **copy of the start state**, so do not expect it to "stop in an intermediate state" when it ends; for the smoothed version (which calls `make_smooth()` every frame) see `SmoothedVectorizedHomotopy` in [More Homotopy Classes](02b-More-Homotopy-Classes.md).

---

See also: [Rotation animations](01-Rotation.md) · [More Homotopy Classes](02b-More-Homotopy-Classes.md) · [Updater Animations](../Updater-Animations/01-Updater-Animations.md)
