# Fade-out / fade-in transforms

The "swap things out" transform where the source fades out and the target fades in — good when the shapes differ a lot and a `Transform` would smear into a mess. This page also covers `TransformAnimations`, which interpolates **two animations themselves** into each other.

## Parameters

### FadeTransform

```python
FadeTransform(mobject, target_mobject, stretch=True, dim_to_match=1, **kwargs)
```

**The source fades out while the target fades in**, and the target is stretched / scaled to the source's size and then restored; when it finishes, the source returns to its original shape and is removed, and the target joins the scene.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the source (restored and removed from the scene when done) |
| `target_mobject` | `Mobject` | — (required) | the target (added to the scene when done) |
| `stretch` | `bool` | `True` | whether to stretch the target to the source's size |
| `dim_to_match` | `int` | `1` | used when `stretch=False`: `0/1/2` match length along x/y/z respectively |
| `**kwargs` | … | — | common `Transform`/`Animation` parameters |

> **Returns**: a `FadeTransform` instance (subclass of `FadeTransform(Transform)`).

### FadeTransformPieces

```python
FadeTransformPieces(mobject, target_mobject, stretch=True, dim_to_match=1, **kwargs)
```

Same as `FadeTransform`, but it **cross-fades submobject by submobject** (submobjects on the two sides are paired one-to-one), rather than replacing the whole thing — for cases where "the overall structure stays, only each piece is swapped". At construction it calls `align_submobjects` first to line up the counts on both sides.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the source (restored and removed from the scene when done) |
| `target_mobject` | `Mobject` | — (required) | the target (added to the scene when done) |
| `stretch` | `bool` | `True` | whether to stretch the target to the source's size |
| `dim_to_match` | `int` | `1` | used when `stretch=False`: `0/1/2` match length along x/y/z respectively |
| `**kwargs` | … | — | common `Transform`/`Animation` parameters |

> **Returns**: a `FadeTransformPieces` instance. **Since 2026-10-16 the constructor supports `run_time=`** (`AnimationGroup` gained `run_time=` / `group=` parameters), so `run_time` / `rate_func` can go in the **constructor** or at **play level**. This page's sample keeps the play-level form (the rendered clips match this version), and the comments in the code record that history.

### TransformAnimations

```python
TransformAnimations(start_anim, end_anim, rate_func=squish_rate_func(smooth), **kwargs)
```

Interpolates **two animations themselves** into each other (it runs `start_anim` and `end_anim` at the same time and transforms the point sets of their two mobjects into each other). The source is marked `TODO, this may be deprecated`; when you need a "transition between animations", usually switch to `AnimationGroup` + `lag_ratio` or `Succession`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `start_anim` | `Animation` | — (required) | the starting animation |
| `end_anim` | `Animation` | — (required) | the ending animation |
| `rate_func` | `Callable` | `squish_rate_func(smooth)` | a rate curve that squeezes progress into the middle |
| `run_time` | `float` | `max(start.run_time, end.run_time)` | when omitted, takes the larger of the two animations' durations |
| `**kwargs` | … | — | common `Transform`/`Animation` parameters |

> **Returns**: a `TransformAnimations` instance (subclass of `TransformAnimations(Transform)`).

## Examples

#### Sample: FadeTransform / FadeTransformPieces / TransformAnimations

Page-specific sample (`assets/RTM code/05-Fade-Through-Transforms.py`):

- two `FadeTransform` combinations: the `stretch=True` default; and `stretch=False + dim_to_match=0` to match length along x only.
- `FadeTransformPieces` pairs submobjects piece by piece (the sample passes `run_time` / `rate_func` at play level — after 2026-10-16 the constructor's `run_time=` is also supported, so the two forms are equivalent).
- `TransformAnimations` interpolates the two native sub-animations `MCreate` / `MFadeOut` into each other (`rate_func=squish_rate_func(smooth)`, `run_time=1.5`).

```python
import os

from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    RED,
    YELLOW,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Circle,
    Rectangle,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
    smooth,
    squish_rate_func,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    FadeTransform,
    FadeTransformPieces,
    Wait,
    Write,
)
# TransformAnimations is a native ManimCE animation (RTM has not rewritten it; it is exported along with RTM);
# and it needs native sub-animations (it calls set_run_time / starting_mobject), so the sub-animations are imported under native aliases too
from real_time_manim import Create as MCreate, FadeOut as MFadeOut, TransformAnimations
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_05_Fade_Through_Transforms(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("Fade-out / fade-in transforms", font_size=44, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # --- 1. FadeTransform: the source fades out while the target fades in (and is stretched to the source's size) ---
        lab1 = VGroup(
            Text("FadeTransform(rect, circ, stretch=True,", font_size=30, color=GREY_B),
            Text("              dim_to_match=1, run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        rect = Rectangle(width=4.0, height=1.0, color=BLUE).set_fill(BLUE, 0.5).move_to(LEFT * 2.4 + DOWN * 1.4)
        circ = Circle(radius=1.1, color=GREEN).set_fill(GREEN, 0.5).move_to(RIGHT * 3.0 + DOWN * 1.4)
        self.add(rect)                             # put the source object into the scene first
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(
            FadeTransform(rect, circ, stretch=True, dim_to_match=1,   # params stretch / dim_to_match ✓
                          run_time=1.2),                               # param run_time ✓
            run_time=1.2,
        )
        win.play(FadeOut(VGroup(lab1, circ)), run_time=0.5)

        # --- 2. FadeTransform: dim_to_match only takes effect when stretch=False (0 = match along x) ---
        lab2 = VGroup(
            Text("FadeTransform(rect2, tri, stretch=False,", font_size=30, color=GREY_B),
            Text("              dim_to_match=0, run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        rect2 = Rectangle(width=4.5, height=0.8, color=RED).set_fill(RED, 0.5).move_to(LEFT * 2.4 + DOWN * 1.4)
        tri = Triangle(color=YELLOW).scale(1.1).set_fill(YELLOW, 0.5).move_to(RIGHT * 3.0 + DOWN * 1.4)
        self.add(rect2)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(
            FadeTransform(rect2, tri, stretch=False, dim_to_match=0,  # params stretch=False / dim_to_match=0 ✓
                          run_time=1.2),
            run_time=1.2,
        )
        win.play(FadeOut(VGroup(lab2, tri)), run_time=0.5)

        # --- 3. FadeTransformPieces: submobjects are paired one by one and cross-faded ---
        lab3 = VGroup(
            Text("FadeTransformPieces(grp, grp2,", font_size=30, color=GREY_B),
            Text("  stretch=True, dim_to_match=1)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        grp = VGroup(Square(side_length=1.0, color=BLUE),
                     Circle(radius=0.5, color=GREEN).shift(RIGHT * 1.6)).move_to(LEFT * 2.6 + DOWN * 1.4)
        grp2 = VGroup(Circle(radius=0.5, color=RED),
                      Triangle(color=YELLOW).scale(0.55).shift(RIGHT * 1.6)).move_to(RIGHT * 3.0 + DOWN * 1.4)
        self.add(grp)
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        # note: the sample keeps the older form - RTM's FadeTransformPieces is an AnimationGroup,
        #     so run_time / rate_func go at play level (since 2026-10-16 the constructor also takes run_time; both work).
        win.play(FadeTransformPieces(grp, grp2, stretch=True, dim_to_match=1),   # params stretch / dim_to_match ✓
                 run_time=1.5,                                                    # param run_time ✓ (play level)
                 rate_func=smooth)                                               # param rate_func ✓
        win.play(FadeOut(VGroup(lab3, grp2)), run_time=0.5)

        # --- 4. TransformAnimations: the two animations themselves interpolate into each other ---
        lab4 = VGroup(
            Text("TransformAnimations(MCreate(sq),", font_size=30, color=GREY_B),
            Text("  MFadeOut(sq), run_time=1.5,", font_size=30, color=GREY_B),
            Text("  rate_func=squish_rate_func(smooth))", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.3)
        sq = Square(side_length=1.8, color=GREEN).set_fill(GREEN, 0.5).move_to(LEFT * 2.8 + DOWN * 1.4)
        win.play(FadeIn(lab4, shift=DOWN), run_time=0.4)
        win.play(Create(sq), run_time=0.6)
        win.play(                                   # the two animations themselves interpolate into each other
            TransformAnimations(MCreate(sq), MFadeOut(sq),          # params start_anim / end_anim ✓
                                rate_func=squish_rate_func(smooth), # param rate_func ✓ (non-default)
                                run_time=1.5),                      # param run_time ✓ (non-default)
            run_time=1.5,
        )

        win.play(Wait(0.4))
        win.play(FadeOut(VGroup(title, lab4)), run_time=0.6)
        win.close()                                 # param win.close()
```

What this code does: four segments.

- (1) a blue rectangle cross-fades into a green circle — source fading out and target fading in happen at the same time, and the target is first stretched to the source's size and then restored (`stretch=True`).
- (2) switching to `stretch=False + dim_to_match=0`, the target triangle matches length along x only and keeps its own height proportions.
- (3) `FadeTransformPieces` swaps "square + circle" for "circle + triangle" piece by piece — each submobject is paired and cross-faded individually rather than replacing the whole group (`run_time` / `rate_func` go at `play` level, see the sample comments).
- (4) `TransformAnimations` interpolates the `Create` and `FadeOut` animations themselves into each other: the square is drawn out while it fades away, with progress squeezed into the middle by `squish_rate_func`.

<video src="assets/RTM output/05-Fade-Through-Transforms.mp4" controls width="560"></video>

> Note: `FadeTransform` / `FadeTransformPieces` are imported from `real_time_manim.vulkan_bind` (RTM's own implementation; the cross-fade works fine in testing).
>
> `TransformAnimations` is a native ManimCE animation (RTM has not rewritten it; it is exported along with `real_time_manim`), and its sub-animations must use the native version (they need `set_run_time` / `starting_mobject`), so the sample imports `MCreate` / `MFadeOut` under aliases.

See also: [Core Transform](01-Transform-Core.md) · [Swapping / copy transforms](04-Swapping-and-Copy-Transforms.md) · [In-place style: ShrinkToCenter / FadeToColor](03b-Shrink-and-Recolor.md)
