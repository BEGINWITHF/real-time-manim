# In-place style: ShrinkToCenter / FadeToColor

Two "in-place style" animation wrappers: `ShrinkToCenter`, which shrinks an object into its centre until it disappears, and `FadeToColor`, which fades the colour to a given colour.

## Parameters

### ShrinkToCenter

```python
ShrinkToCenter(mobject, **kwargs)
```

Shrinks the object to 0 (collapsing into the centre until it disappears). **Note**: it is not a remover — when it finishes the object is still in the scene (just invisible); to truly remove it, call `self.remove(m)` afterward, or switch to `FadeOut` / `Uncreate`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the object being shrunk |
| `**kwargs` | … | — | internally fixes `scale_factor=0`; the rest are the common `Transform`/`Animation` parameters |

> **Returns**: a `ShrinkToCenter` instance (subclass of `ShrinkToCenter(ScaleInPlace)` ← `ApplyMethod` ← `Transform`).

### FadeToColor

```python
FadeToColor(mobject, color, **kwargs)
```

**Fades** the object's colour to the given colour (equivalent to `ApplyMethod(m.set_color, color)`).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the object being recoloured |
| `color` | `str \| ManimColor` | — (required) | the target colour |
| `**kwargs` | … | — | common `Transform`/`Animation` parameters |

> **Returns**: a `FadeToColor` instance (subclass of `FadeToColor(ApplyMethod)` ← `Transform`).

## Examples

#### Sample: ShrinkToCenter / FadeToColor

Page-specific sample (`assets/RTM code/03b-Shrink-and-Recolor.py`): after `ShrinkToCenter` collapses the object into the centre, a `self.remove(word)` line follows immediately (showing it is not a remover); `FadeToColor` fades the same piece of text to two different target colours (white → red → yellow).

```python
import os

from real_time_manim import (
    GREY_B,
    ORANGE,
    RED,
    WHITE,
    YELLOW,
    DOWN,
    LEFT,
    UP,
    Scene,
    Text,
    VGroup,
    smooth,
)
# ShrinkToCenter / FadeToColor are not in RTM's export list; import them from real_time_manim with the bundled ManimCE; tested and working
from real_time_manim import FadeToColor, ShrinkToCenter
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_03b_Shrink_and_Recolor(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("ShrinkToCenter / FadeToColor", font_size=40, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # --- 1. ShrinkToCenter: shrink to 0, collapsing into the centre ---
        lab1 = Text("ShrinkToCenter(word, run_time=1.4, rate_func=smooth)",
                    font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)
        word = Text("Bye", font_size=48, color=YELLOW).move_to(LEFT * 2.0 + DOWN * 1.4)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Write(word), run_time=0.8)
        win.play(ShrinkToCenter(word, run_time=1.4, rate_func=smooth), run_time=1.4)   # param ShrinkToCenter ✓
        self.remove(word)      # note: ShrinkToCenter is not a remover; when done the object is still in the scene (just invisible)
        win.play(FadeOut(lab1), run_time=0.45)

        # --- 2. FadeToColor: fade the colour to a given colour (showing two different target colours) ---
        lab2 = VGroup(
            Text("FadeToColor(msg, RED, run_time=1.2)", font_size=30, color=GREY_B),
            Text("FadeToColor(msg, YELLOW, run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        msg = Text("Hello World!", font_size=44, color=WHITE).move_to(DOWN * 1.6)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Write(msg), run_time=0.8)
        win.play(FadeToColor(msg, RED, run_time=1.2, rate_func=smooth), run_time=1.2)      # param color=RED ✓
        win.play(FadeToColor(msg, YELLOW, run_time=1.2, rate_func=smooth), run_time=1.2)   # param color=YELLOW ✓

        win.play(Wait(0.4))
        win.play(FadeOut(VGroup(title, lab2, msg)), run_time=0.6)
        win.close()                                 # param win.close()
```

What this code does: the first segment writes `Bye`, then plays `ShrinkToCenter` — the text shrinks to 0 about its own centre and vanishes; the following `self.remove(word)` line demonstrates "it is not a remover": without that line the object would still sit in the scene taking up room.

The second segment takes `Hello World!` and fades it to red with `FadeToColor`, then to yellow — both are smooth colour transitions (not an instant colour swap), with the target colour written straight into the argument.

<video src="assets/RTM output/03b-Shrink-and-Recolor.mp4" controls width="560"></video>

> Note: when `ShrinkToCenter` finishes the object is **still in the scene** (`points` shrunk to 0, invisible). If you later want to animate it or fade the whole scene out, remember to `self.remove` first, or switch to a real remover (`FadeOut` / `Uncreate`).
>
> Neither of these two classes is in RTM's export list; just import them from `real_time_manim`.

Not demonstrated: none — every visible parameter of the two classes on this page is shown explicitly.

See also: [Saving state / in-place scaling](03-Saving-State-and-Style-Transform.md) · [Fade-out / fade-in transforms](05-Fade-Through-Transforms.md) · [Core Transform](01-Transform-Core.md)
