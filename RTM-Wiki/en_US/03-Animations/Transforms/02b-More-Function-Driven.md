# More function-driven transforms (centre / complex / matrix)

The advanced entries in the function-driven family: repositioning by moving the centre point only, a conformal map by a complex function, and a linear transform by a matrix.

## Parameters

### ApplyPointwiseFunctionToCenter

```python
ApplyPointwiseFunctionToCenter(function, mobject, **kwargs)
```

Applies a `center -> center` function to the **centre point** only, then `move_to`s the whole object to the result — good for animations that "reposition by a rule" without changing the shape.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `function` | `Callable[[np.ndarray], np.ndarray]` | — (required) | centre -> new centre |
| `mobject` | `Mobject` | — (required) | the object being transformed |
| `**kwargs` | … | — | includes `run_time=3.0` and the common `Transform`/`Animation` parameters |

> **Returns**: an `ApplyPointwiseFunctionToCenter` instance (subclass of `ApplyPointwiseFunctionToCenter(ApplyPointwiseFunction)`).

### ApplyComplexFunction

```python
ApplyComplexFunction(function, mobject, **kwargs)
```

Applies the complex function `z -> f(z)` to every point of the object (internally calls `mobject.apply_complex_function`); good for conformal maps such as `exp`, rotation and scaling. It also sets the rotation path arc automatically from `log(f(1)).imag`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `function` | `Callable[[complex], complex]` | — (required) | a map from the complex plane to the complex plane |
| `mobject` | `Mobject` | — (required) | the object being transformed |
| `**kwargs` | … | — | common `Transform`/`Animation` parameters |

> **Returns**: an `ApplyComplexFunction` instance (subclass of `ApplyComplexFunction(ApplyMethod)` ← `Transform`).

### ApplyMatrix

```python
ApplyMatrix(matrix, mobject, about_point=ORIGIN, **kwargs)
```

Applies a linear transform matrix to the object (`2x2` or `3x3`; `2x2` is padded to `3x3` automatically, other sizes raise `ValueError("Matrix has bad dimensions")`); good for shear, stretch and mirror. The formula is `p' = (p - about_point) @ matrix.T + about_point`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `matrix` | `np.ndarray \| list` | — (required) | a 2x2 or 3x3 linear transform matrix |
| `mobject` | `Mobject` | — (required) | the object being transformed |
| `about_point` | `np.ndarray` | `ORIGIN` | the transform origin |
| `**kwargs` | … | — | includes `run_time=3.0` and the common `Transform`/`Animation` parameters |

> **Returns**: an `ApplyMatrix` instance (subclass of `ApplyMatrix(ApplyPointwiseFunction)`).

## Examples

#### Sample: ApplyPointwiseFunctionToCenter / ApplyComplexFunction / ApplyMatrix

Page-specific sample (`assets/RTM code/02b-More-Function-Driven.py`): one segment per class, with `run_time` always passed explicitly:

- centre repositioning: `lambda c: c + UP * 2.2`, the shape stays put.
- a conformal map by a complex function: `lambda z: np.exp(z)`.
- a 2x2 shear matrix: `[[1, 1], [0, 2 / 3]]` plus the non-default anchor `about_point=DOWN * 2.6`.

```python
import os

import numpy as np
from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    YELLOW,
    DOWN,
    LEFT,
    ORIGIN,
    UP,
    Dot,
    Scene,
    Square,
    Text,
    VGroup,
    Write,
)
# The three classes below are not in RTM's export list; import them from real_time_manim with the bundled ManimCE; tested and working
# (ApplyPointwiseFunctionToCenter's __init__ is fixed up by real_time_manim.compat at import time)
from real_time_manim import ApplyComplexFunction, ApplyMatrix, ApplyPointwiseFunctionToCenter
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    Wait,  # noqa: F401
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_02b_More_Function_Driven(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("More function-driven transforms: centre / complex / matrix", font_size=42, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # --- 1. ApplyPointwiseFunctionToCenter: only the centre point changes, the shape stays put ---
        lab1 = VGroup(
            Text("ApplyPointwiseFunctionToCenter(", font_size=30, color=GREY_B),
            Text("  lambda c: c + UP * 2.2, d, run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        d = Dot(radius=0.16, color=YELLOW).move_to(LEFT * 3.0 + DOWN * 1.5)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Create(d), run_time=0.4)
        win.play(                                   # the centre is repositioned by the given rule
            ApplyPointwiseFunctionToCenter(lambda c: c + UP * 2.2, d,
                                           run_time=1.2),   # param run_time ✓ (default 3.0)
            run_time=1.2,
        )
        win.play(FadeOut(VGroup(lab1, d)), run_time=0.5)

        # --- 2. ApplyComplexFunction: a conformal map by a complex function (relative to ORIGIN) ---
        lab2 = VGroup(
            Text("ApplyComplexFunction(lambda z: np.exp(z),", font_size=30, color=GREY_B),
            Text("                     sq, run_time=1.5)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        sq = Square(side_length=2.2, color=GREEN).set_fill(GREEN, 0.5).move_to(ORIGIN + DOWN * 0.6)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Create(sq), run_time=0.5)
        win.play(ApplyComplexFunction(lambda z: np.exp(z), sq,   # params function + mobject ✓
                                      run_time=1.5), run_time=1.5)
        win.play(FadeOut(VGroup(lab2, sq)), run_time=0.5)

        # --- 3. ApplyMatrix: a 2x2 linear transform about a custom anchor ---
        lab3 = VGroup(
            Text("ApplyMatrix([[1, 1], [0, 2 / 3]], txt,", font_size=30, color=GREY_B),
            Text("  about_point=DOWN * 2.6, run_time=1.4)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        txt = Text("Hello", font_size=48, color=BLUE).move_to(LEFT * 1.6 + DOWN * 1.0)
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(Write(txt), run_time=0.6)
        win.play(                                   # p' = (p - about_point) @ matrix.T + about_point
            ApplyMatrix([[1, 1], [0, 2 / 3]], txt,   # param matrix ✓ (2x2 is padded to 3x3 automatically)
                        about_point=DOWN * 2.6,      # param about_point ✓ (non-default ORIGIN)
                        run_time=1.4),               # param run_time ✓ (default 3.0)
            run_time=1.4,
        )

        win.play(FadeOut(VGroup(title, lab3, txt)), run_time=0.6)
        win.close()                                 # param win.close()
```

What this code does: three segments, one kind of "function-driven" transform each.

- (1) the yellow dot's centre is repositioned by the rule `c + UP * 2.2` — the dot itself is not scaled or warped, it just translates upward as a whole.
- (2) the green square undergoes an `exp(z)` conformal map relative to ORIGIN: straight edges bend into arcs and the whole thing spreads up and to the right.
- (3) the `Hello` text is transformed by the shear matrix `[[1, 1], [0, 2/3]]` — sheared right horizontally, compressed vertically — with the anchor at the bottom of the frame (`about_point=DOWN * 2.6`), so the text shears about its bottom rather than its centre.

<video src="assets/RTM output/02b-More-Function-Driven.mp4" controls width="560"></video>

> Note: none of these three classes is in RTM's export list; just import them from `real_time_manim`.
>
> **`ApplyPointwiseFunctionToCenter` has an upstream bug in its constructor in ManimCE 0.21** (`super().__init__` fails to pass `mobject`, so using it directly raises `TypeError`); RTM fixes it automatically when `real_time_manim.compat` is imported — which is why the sample comment says "fixed up by real_time_manim.compat at import time".
>
> `ApplyMatrix` only accepts 2x2 / 3x3; any other size raises `ValueError("Matrix has bad dimensions")`.

Not demonstrated: none — every visible parameter of the three classes on this page is shown explicitly.

See also: [Method- and function-driven transforms](02-Method-and-Function-Driven.md) · [Core Transform](01-Transform-Core.md) · [Saving state / in-place style](03-Saving-State-and-Style-Transform.md)
