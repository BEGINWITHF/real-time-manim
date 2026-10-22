# Swapping / copy transforms

This page covers three kinds of transform:

- the "copy" transform, which leaves the original intact (`TransformFromCopy`)
- `ClockwiseTransform` / `CounterclockwiseTransform`, which swap two objects along an arc
- `CyclicReplace` / `Swap`, which rotate several objects into each other's slots

## Parameters

### TransformFromCopy

```python
TransformFromCopy(mobject, target_mobject, **kwargs)
```

**Leaves the original unmoved** and makes `target_mobject` first align to the original's shape, then interpolate back to its own shape and position; visually it looks like "a copy evolves out of the original". A target object that is not in the scene is added automatically.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the source object, **left unchanged** |
| `target_mobject` | `Mobject` | — (required) | the target object; it is added to the scene and morphed |
| `**kwargs` | … | — | common `Transform`/`Animation` parameters |

> **Returns**: a `TransformFromCopy` instance (subclass of `TransformFromCopy(Transform)`).

### ClockwiseTransform / CounterclockwiseTransform

```python
ClockwiseTransform(mobject, target_mobject, path_arc=-np.pi, **kwargs)
CounterclockwiseTransform(mobject, target_mobject, path_arc=np.pi, **kwargs)
```

Forces the points to move to the target position along a **clockwise / counterclockwise half-arc** (default arc angles `-π` / `+π`), so two objects "swap around" instead of crossing in a straight line. Both take exactly the same parameters; only the `path_arc` default differs.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the source object |
| `target_mobject` | `Mobject` | — (required) | the target object |
| `path_arc` | `float` | Clockwise `-np.pi` / Counterclockwise `+np.pi` | the arc angle; changeable |
| `**kwargs` | … | — | `Transform` (`path_func`, `path_arc_axis`, `path_arc_centers`, `replace_mobject_with_target_in_scene`) and the common `Animation` parameters |

> **Returns**: an instance of the corresponding class (both are `Transform` subclasses).

### CyclicReplace / Swap

```python
CyclicReplace(*mobjects, path_arc=90 * DEGREES, **kwargs)
Swap(*mobjects, path_arc=90 * DEGREES, **kwargs)
```

Makes several objects **rotate through each other's slots**: the first moves to the second's position, the second to the third's … and the last back to the first's, following a 90° arc by default; with two objects it is simply a "swap". `Swap` has no constructor of its own — it is the same thing under a plainer name.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*mobjects` | `Group`/`VGroup` or several `Mobject`s | — (required) | if a single `Group` is passed it is used directly, otherwise the code builds `Group(*mobjects)` internally |
| `path_arc` | `float` | `90 * DEGREES` | the arc angle the rotation follows |
| `**kwargs` | … | — | common `Transform`/`Animation` parameters |

> **Returns**: an instance of the corresponding class (`CyclicReplace(Transform)`, `Swap(CyclicReplace)`).

## Examples

#### Sample: TransformFromCopy / ClockwiseTransform / CounterclockwiseTransform / CyclicReplace / Swap

Page-specific sample (`assets/RTM code/04-Swapping-and-Copy-Transforms.py`):

- `Swap` swaps two letters using the non-default `path_arc=180 * DEGREES`;
- `TransformFromCopy` uses MathTex formulas to show the original staying put;
- `Clockwise` / `Counterclockwise` swap two points along ±π half-arcs;
- `CyclicReplace` rotates three numbers through each other's slots.

```python
import os

import numpy as np
from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    PURPLE,
    RED,
    YELLOW,
    DEGREES,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Dot,
    MathTex,
    Scene,
    Text,
    VGroup,
    smooth,
)
# The five classes below are not in RTM's export list; import them from real_time_manim with the bundled ManimCE; tested and working
from real_time_manim import (
    ClockwiseTransform,
    CounterclockwiseTransform,
    CyclicReplace,
    Swap,
    TransformFromCopy,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    Wait,  # noqa: F401
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_04_Swapping_and_Copy_Transforms(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("Swapping / copy transforms", font_size=42, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # --- 1. Swap: two objects swap places along an arc ---
        lab1 = VGroup(
            Text("Swap(a, b, path_arc=180 * DEGREES,", font_size=30, color=GREY_B),
            Text("     run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        a = Text("A", font_size=52, color=BLUE).move_to(LEFT * 3.5 + DOWN * 1.3)
        b = Text("B", font_size=52, color=GREEN).move_to(RIGHT * 3.5 + DOWN * 1.3)
        self.add(a, b)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Swap(a, b, path_arc=180 * DEGREES, run_time=1.2), run_time=1.2)   # params *mobjects / path_arc ✓
        # note: in RTM, objects added to the scene with self.add must each be FadeOut-ed
        #     separately (a VGroup fade only affects members added by a win.play animation), so here they are faded out one by one.
        win.play(FadeOut(lab1), FadeOut(a), FadeOut(b), run_time=0.5)

        # --- 2. TransformFromCopy: the original stays, the target evolves out ---
        lab2 = Text("TransformFromCopy(eq1, eq2, run_time=1.2, rate_func=smooth)",
                    font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)
        eq1 = MathTex("x = 1").move_to(LEFT * 3.2 + DOWN * 1.3)
        eq2 = MathTex("x^2 = 1").move_to(RIGHT * 3.2 + DOWN * 1.3)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Write(eq1), run_time=0.6)
        win.play(TransformFromCopy(eq1, eq2, run_time=1.2, rate_func=smooth), run_time=1.2)   # param ✓ (the original stays)
        win.play(FadeOut(lab2), FadeOut(eq1), FadeOut(eq2), run_time=0.5)

        # --- 3. ClockwiseTransform: the point swaps along a clockwise half-arc ---
        lab3 = Text("ClockwiseTransform(p, q.copy(), path_arc=-np.pi)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        p = Dot(radius=0.16, color=YELLOW).move_to(LEFT * 3.2 + DOWN * 1.3)
        q = Dot(radius=0.16, color=ORANGE).move_to(RIGHT * 3.2 + DOWN * 1.3)
        self.add(p, q)
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(ClockwiseTransform(p, q.copy(), path_arc=-np.pi, run_time=1.2), run_time=1.2)   # param path_arc ✓
        win.play(FadeOut(lab3), FadeOut(p), FadeOut(q), run_time=0.5)

        # --- 4. CounterclockwiseTransform: swap along a counterclockwise half-arc (opposite direction to (3)) ---
        lab4 = VGroup(
            Text("CounterclockwiseTransform(p2, q2.copy(),", font_size=30, color=GREY_B),
            Text("                           path_arc=np.pi)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        p2 = Dot(radius=0.16, color=RED).move_to(LEFT * 3.2 + DOWN * 1.3)
        q2 = Dot(radius=0.16, color=PURPLE).move_to(RIGHT * 3.2 + DOWN * 1.3)
        self.add(p2, q2)
        win.play(FadeIn(lab4, shift=DOWN), run_time=0.4)
        win.play(CounterclockwiseTransform(p2, q2.copy(), path_arc=np.pi, run_time=1.2), run_time=1.2)   # param ✓
        win.play(FadeOut(lab4), FadeOut(p2), FadeOut(q2), run_time=0.5)

        # --- 5. CyclicReplace: three objects rotate into each other's slots ---
        lab5 = VGroup(
            Text("CyclicReplace(c1, c2, c3,", font_size=30, color=GREY_B),
            Text("              path_arc=90 * DEGREES, run_time=1.4)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        c1 = Text("1", font_size=48, color=BLUE).move_to(LEFT * 3.5 + DOWN * 1.3)
        c2 = Text("2", font_size=48, color=GREEN).move_to(DOWN * 1.3)
        c3 = Text("3", font_size=48, color=ORANGE).move_to(RIGHT * 3.5 + DOWN * 1.3)
        self.add(c1, c2, c3)
        win.play(FadeIn(lab5, shift=DOWN), run_time=0.4)
        win.play(CyclicReplace(c1, c2, c3, path_arc=90 * DEGREES, run_time=1.4), run_time=1.4)   # param ✓

        win.play(FadeOut(title), FadeOut(lab5),
                 FadeOut(c1), FadeOut(c2), FadeOut(c3), run_time=0.6)
        win.close()                                 # param win.close()
```

What this code does: five segments showing five kinds of "swap / copy".

- (1) `Swap(a, b, path_arc=180°)` has A and B swap places along a half-arc.
- (2) `TransformFromCopy` "copies" from the original `x = 1` and evolves `x^2 = 1` out of it, with the original staying put on the left.
- (3) (4) two points fly along a clockwise / counterclockwise half-arc to each other's positions (opposite directions, symmetric paths).
- (5) `CyclicReplace` sends 1 -> 2's position, 2 -> 3's position and 3 back to 1's position, all three rotating along a 90° arc at once.

<video src="assets/RTM output/04-Swapping-and-Copy-Transforms.mp4" controls width="560"></video>

> Note: none of these five classes is in RTM's export list; just import them from `real_time_manim` — they play fine in testing.
>
> The sample also has two RTM-side caveats:
>
> - objects added to the scene with `self.add` must **each be `FadeOut`-ed separately** (a VGroup fade only affects members added by a `win.play` animation; objects added directly with `self.add` will not fade even if you wrap them in one).
> - to flip the arc direction of `Clockwise` / `CounterclockwiseTransform`, just change `path_arc`; the sample passes the documented default ±π explicitly so the arc is visible to the eye.

See also: [Core Transform](01-Transform-Core.md) · [Copy vs. fade-through trade-offs, see the fade-through page](05-Fade-Through-Transforms.md) · [The Grow family](../Growth/01-The-Grow-Family.md)
