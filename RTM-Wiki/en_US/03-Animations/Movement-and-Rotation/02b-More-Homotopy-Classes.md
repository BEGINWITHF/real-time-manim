# The remaining homotopy classes: Smoothed / Complex / PhaseFlow

The three classes from the manual's "7.3 Homotopy" besides `Homotopy`: a smoothed pointwise remap, a complex-function drive, and a vector field that accumulates displacement.

All three classes are verified renderable (signatures copied from the manual, source `animation/movement.py`), and the three samples each have their own clip. `SmoothedVectorizedHomotopy` needs an upstream-bug workaround under plain command-line rendering (see the sample and the note).

## Parameters

### SmoothedVectorizedHomotopy

```python
SmoothedVectorizedHomotopy(homotopy, mobject, run_time=3, apply_function_kwargs=None, **kwargs)
```

Inherits `SmoothedVectorizedHomotopy(Homotopy)` (**no `__init__` of its own**, the signature is inherited entirely from `Homotopy`), from `animation/movement.py` (no docstring; organised from the source). Used like `Homotopy`, but it calls `make_smooth()` on the result every frame to keep the curve smooth (only valid for `VMobject`, otherwise an `assert` fails).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `homotopy` | `Callable[[float, float, float, float], tuple]` | — | inputs the old coordinates and the time, outputs the new coordinates (same as `Homotopy`). **accepts** any four-argument function |
| `mobject` | `Mobject` | — | the object being deformed, **must be a `VMobject`** (a vector object) |
| `run_time` | `float` | `3` | duration (seconds) |
| `apply_function_kwargs` | `dict \| None` | `None` | parameters forwarded to `Mobject.apply_function`. Fixed (2026-10-16, test `tests/test_gap_transform_motion.py`): the real cause was upstream `VMobject.apply_function` declaring `about_point` / `about_edge` without passing them on to the parent class (true throughout 0.19-0.21), and RTM fixes it with a one-line change in the embedded copy plus an idempotent runtime patch (which also takes effect for an already-imported external manim) |
| `**kwargs` | `Any` | — | `Animation` common parameters (`rate_func`…) |

> **Returns**: `Animation` (hand it to `play` to play it).

#### Sample: a circle smoothly squashed and then stretched

A blue circle is mapped point by point by `squash(x, y, z, t)`: it stretches along x and squashes along y as `t` goes on, and its outline stays smooth throughout.

```python
from real_time_manim import Scene, Text, VGroup, Circle, BLUE, GREY_B, YELLOW, UP, DOWN, \
    FadeIn, SmoothedVectorizedHomotopy, Write, linear
from real_time_manim.vulkan_bind import MLWindow, Wait

class SmoothedHomotopyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("02b-SmoothedVectorizedHomotopy", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("SmoothedVectorizedHomotopy(squash, c, run_time=1.8,", font_size=30, color=GREY_B)
        l2 = Text("                            rate_func=linear)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        c = Circle(radius=1.0, color=BLUE).set_fill(BLUE, 0.4).shift(DOWN * 1.5)   # blue circle
        win.play(FadeIn(sig, shift=DOWN), FadeIn(c), run_time=0.4)   # fade in the label and the circle

        def squash(x, y, z, t):   # parameter "homotopy": stretch x, squash y
            return (x * (1.0 + 0.9 * t), y * (1.0 - 0.45 * t), z)

        win.play(SmoothedVectorizedHomotopy(squash, c, run_time=1.8, rate_func=linear))
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: `squash(x, y, z, t)` maps every point to `(x*(1+0.9t), y*(1-0.45t))` — over 1.8 seconds the blue circle stretches sideways to 1.9 times while being squashed to half its height.

`SmoothedVectorizedHomotopy` calls `make_smooth()` on the result every frame, so the outline stays a smooth curve while stretching and never develops corners.

<video src="assets/RTM output/02b-More-Homotopy-Classes-smoothed.mp4" controls width="560"></video>

> Note: upstream manim 0.21's `SmoothedVectorizedHomotopy.interpolate_submobject` uses `VMobject` without importing it, so under plain manim the first interpolation raises `NameError`; adding `movement.VMobject = VMobject` fixes it (RTM's `compat.py` already ships this fix, and the sample renders fine).

### ComplexHomotopy

```python
ComplexHomotopy(complex_homotopy, mobject, **kwargs)
```

Inherits `ComplexHomotopy(Homotopy)`, from `animation/movement.py`. It describes the deformation with a complex function `C × [0,1] -> C`: internally it treats `(x, y)` as the complex number `z`, computes `complex_homotopy(complex(x, y), t)` and then takes the real and imaginary parts (the `z` coordinate is unchanged).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `complex_homotopy` | `Callable[[complex, float], complex]` | — | inputs a complex number and the time, outputs a new complex number. **accepts** e.g. `lambda z, t: z * np.exp(1j * t * PI / 2)` (a rotation in the complex plane) |
| `mobject` | `Mobject` | — | the object being deformed |
| `**kwargs` | `Any` | — | `Homotopy`'s `run_time=3`, `apply_function_kwargs`, and `Animation` common parameters |

> **Returns**: `Animation` (hand it to `play` to play it).

#### Sample: multiplying by e^(i*t*PI/2) turns it 90° in place in the complex plane

Every point of the red square is treated as a complex number; after multiplying by the rotation factor it turns 90° in place.

```python
import numpy as np

from real_time_manim import Scene, Text, VGroup, Square, RED, GREY_B, YELLOW, UP, DOWN, \
    ComplexHomotopy, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class ComplexHomotopyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("02b-ComplexHomotopy", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("ComplexHomotopy(lambda z, t: z*e^(i*t*PI/2), sq,", font_size=30, color=GREY_B)
        l2 = Text("                run_time=1.8)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        sq = Square(side_length=1.6, color=RED).set_fill(RED, 0.4).shift(DOWN * 1.5)   # red square
        win.play(FadeIn(sig, shift=DOWN), FadeIn(sq), run_time=0.4)   # fade in the label and the square
        win.play(ComplexHomotopy(lambda z, t: z * np.exp(1j * t * np.pi / 2), sq,   # parameter "complex_homotopy" (rotation in the complex plane)
                                 run_time=1.8))
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: `lambda z, t: z * np.exp(1j * t * np.pi / 2)` is "multiplying a complex number by one of modulus 1 whose argument grows from 0 to PI/2 with `t`", which geometrically equals turning every point 90° counter-clockwise about the origin.

Over 1.8 seconds the red square completes its 90° turn in place, and the `z` coordinate (perpendicular to the page) is unaffected.

<video src="assets/RTM output/02b-More-Homotopy-Classes-complex.mp4" controls width="560"></video>

### PhaseFlow

```python
PhaseFlow(function, mobject, virtual_time=1, suspend_mobject_updating=False,
          rate_func=linear, **kwargs)
```

Inherits `PhaseFlow(Animation)`, from `animation/movement.py` (no docstring; organised from the source). It **accumulates displacement frame by frame** along the vector field `function(point) -> velocity` (per-frame displacement `Δ = virtual_time * (rate_func(a2) - rate_func(a1)) * function(p)`), making a shape move along the phase flow.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `function` | `Callable[[np.ndarray], np.ndarray]` | — | the vector field: inputs a point, outputs a velocity. **accepts** e.g. `lambda p: np.array([-p[1], p[0], 0])` (a field rotating about the origin) |
| `mobject` | `Mobject` | — | the object being pushed |
| `virtual_time` | `float` | `1` | displacement multiplier |
| `suspend_mobject_updating` | `bool` | `False` | whether to suspend updaters (in a scene with no updaters `True`/`False` look the same) |
| `rate_func` | `Callable` | `linear` | progress function |
| `**kwargs` | `Any` | — | `Animation` common parameters |

> **Returns**: `Animation` (hand it to `play` to play it).

#### Sample: a dot pushed by a vector field to trace an arc about a centre

A grey dot is pushed by a rotating vector field to trace an arc about a centre point at the lower left.

```python
import numpy as np

from real_time_manim import Scene, Text, VGroup, Dot, GREY_B, YELLOW, LEFT, UP, DOWN, \
    FadeIn, PhaseFlow, Write, linear
from real_time_manim.vulkan_bind import MLWindow, Wait

class PhaseFlowDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("02b-PhaseFlow", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("PhaseFlow(lambda p: [-p[1]-1.3, p[0], 0], dot,", font_size=30, color=GREY_B)
        l2 = Text("          virtual_time=1.2, run_time=2.0, rate_func=linear)", font_size=28, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        dot = Dot(radius=0.13, color=GREY_B).shift(LEFT * 1.9 + DOWN * 1.3)   # the dot pushed by the vector field
        center = Dot(radius=0.06, color=GREY_B).shift(DOWN * 1.3)   # the centre of rotation of the vector field
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(dot, center)), run_time=0.4)   # fade in the label and the dots
        win.play(PhaseFlow(lambda p: np.array([-p[1] - 1.3, p[0], 0.0]), dot,   # parameter "function" (the vector field)
                           virtual_time=1.2, run_time=2.0, rate_func=linear))   # parameter "virtual_time / run_time / rate_func"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: the vector field `lambda p: [-p[1]-1.3, p[0], 0]` is the "counter-clockwise rotation about the point `(-1.3, 0)`" field — `PhaseFlow` integrates one small step at the current velocity each frame, and the grey dot is pushed along to trace an arc about the grey dot centre below.

`virtual_time=1.2` is the step multiplier (bigger runs faster), and `rate_func=linear` keeps the whole run at a constant rate.

<video src="assets/RTM output/02b-More-Homotopy-Classes-phaseflow.mp4" controls width="560"></video>

Not demonstrated:

- `SmoothedVectorizedHomotopy`'s `apply_function_kwargs` — fixed and usable (2026-10-16, test `tests/test_gap_transform_motion.py`); with the default `None` the picture matches the old version, so this page has no separate clip for it.
- `PhaseFlow`'s `suspend_mobject_updating` — no video: in a scene with no updaters, passing `True`/`False` looks exactly the same (`PhaseFlow` has no `apply_function_kwargs` parameter at all, see its `**kwargs` row).

---

See also: [Along Path and Homotopy](02-Along-Path-and-Homotopy.md) · [Rotation animations](01-Rotation.md)
