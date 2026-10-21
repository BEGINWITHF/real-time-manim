# Grow: GrowArrow / SpinInFromNothing

The Grow family's two specialisations: `GrowArrow` grows an arrow from its start towards its tip, and `SpinInFromNothing` grows an object while it rotates.

## Parameters

### `GrowArrow`

```python
GrowArrow(arrow, point_color=None, **kwargs)
```

The arrow **grows from its start towards its tip**; this is the standard way to bring in arrows and vectors. The start state does `scale(0)` and `move_to(arrow.get_start)`, carried out by the renderer's `_grow_scale` / `_grow_point` channels, so the tip always grows towards the target direction. Inherits `GrowArrow(Animation)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `arrow` | `Arrow` | — (required) | the arrow object that appears |
| `point_color` | `ParsableManimColor \| None` | `None` | starting colour; `None` keeps the object's own colour. **accepts** any colour |
| `**kwargs` | `Any` | — | `Animation` common parameters (`run_time=1.0`, `rate_func`…). Not a `Transform` subclass, so `path_arc`/`path_func` are swallowed and do nothing |

> **Returns**: a `GrowArrow` instance.

### `SpinInFromNothing`

```python
SpinInFromNothing(mobject, angle=PI / 2, point_color=None, **kwargs)
```

Grows **from the centre while rotating**: RTM's implementation writes `_grow_rot = angle * alpha` to the renderer and does not go through a path function. `angle` is the total extra rotation during the growth (`2*PI` = a full turn). Inherits `SpinInFromNothing(GrowFromCenter) ← GrowArrow(Animation)` (the RTM-native chain).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the object that appears |
| `angle` | `float` | `PI / 2` | total extra rotation during the growth. **accepts** any radian value (`2*PI` a full turn, `PI/2` only 90°) |
| `point_color` | `ParsableManimColor \| None` | `None` | starting colour; `None` keeps the object's own colour |
| `**kwargs` | `Any` | — | `Animation` common parameters. The RTM-native version **has no `path_func` parameter at all** (the rotation is done by the `_grow_rot` channel, not by path interpolation), so passing `path_func=` is merely swallowed by `**kwargs` and does nothing |

> **Returns**: a `SpinInFromNothing` instance.

#### Sample: an arrow growing from its start / spin-in at two angles

`GrowArrow` (`point_color=RED`, the arrow grows from its start towards its tip) and `SpinInFromNothing` (`angle=2*PI` an extra full turn + `point_color=BLUE`, contrasted against the small turn at the default `angle=PI/2`).

```python
import os
from real_time_manim import (
    BLUE,
    GOLD,
    GREY_B,
    PURPLE,
    RED,
    YELLOW,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    PI,
    Arrow,
    Circle,
    Scene,
    Star,
    Text,
    VGroup,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    GrowArrow,
    SpinInFromNothing,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401

class Page_01b_Arrows_and_Spin_In(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameter w=1280 / h=720 / hidden=True
        win.scene = self

        title = Text("Grow: GrowArrow / SpinInFromNothing", font_size=42, color=YELLOW).to_edge(UP)
        win.play(Write(title, run_time=0.8), run_time=0.8)

        # --- 1. GrowArrow: the arrow grows from its start towards its tip ---
        l1 = Text("GrowArrow(arrow, point_color=RED, run_time=1.7)",
                  font_size=32, color=GREY_B).next_to(title, DOWN, buff=0.5)
        arr = Arrow(ORIGIN + LEFT * 3.2 + DOWN * 1.0, ORIGIN + RIGHT * 1.2 + DOWN * 1.0,
                    buff=0, color=GOLD, stroke_width=6).next_to(l1, DOWN, buff=0.9).shift(LEFT * 1.0)
        win.play(FadeIn(l1, shift=DOWN), run_time=0.4)
        win.play(
            GrowArrow(arr,                          # parameter arrow
                      point_color=RED,              # parameter point_color=RED (reddish at the start, back to gold as it grows)
                      run_time=1.7),                # parameter **kwargs(run_time)
            run_time=1.7,
        )
        win.play(FadeOut(VGroup(l1, arr)), run_time=0.5)

        # --- 2. SpinInFromNothing: grow while rotating (angle not the default: an extra full turn) ---
        l2 = Text("SpinInFromNothing(mobject, angle=2*PI, point_color=BLUE)",
                  font_size=32, color=GREY_B).next_to(title, DOWN, buff=0.5)
        star = Star(n=5, outer_radius=1.0, color=PURPLE).next_to(l2, DOWN, buff=0.8).shift(LEFT * 2.2)
        win.play(FadeIn(l2, shift=DOWN), run_time=0.4)
        win.play(
            SpinInFromNothing(                      # parameter mobject
                star,
                angle=2 * PI,                       # parameter angle=2*PI (an extra full turn while growing)
                point_color=BLUE,                   # parameter point_color=BLUE
                run_time=1.9),                      # parameter **kwargs(run_time)
            run_time=1.9,
        )
        # contrast: the small turn at the default angle PI/2
        l3 = Text("SpinInFromNothing(mobject, angle=PI/2)   # default angle for comparison",
                  font_size=32, color=GREY_B).next_to(l2, DOWN, buff=1.9).shift(RIGHT * 2.4)
        ci = Circle(radius=0.6, color=GREY_B).next_to(l3, DOWN, buff=0.6)
        win.play(FadeIn(VGroup(l3, ci), shift=DOWN), run_time=0.4)
        win.play(
            SpinInFromNothing(                      # parameter mobject
                ci,
                angle=PI / 2,                       # parameter angle=PI/2 (= the default, only 90°)
                run_time=1.5),                      # parameter **kwargs(run_time)
            run_time=1.5,
        )

        win.play(Wait(0.5))
        win.play(FadeOut(VGroup(title, star, l3, ci)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_01b_Arrows_and_Spin_In,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "01b-Arrows-and-Spin-In.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
```

What this code does: three segments in turn.

- (1) `GrowArrow(arr, point_color=RED, run_time=1.7)` grows the gold arrow from its left start towards the right tip, with a touch of red at the start.
- (2) `SpinInFromNothing(star, angle=2*PI, point_color=BLUE, run_time=1.9)` grows the purple star while it turns a full extra circle, starting bluish.
- (3) The control group `SpinInFromNothing(ci, angle=PI/2, run_time=1.5)` uses the default angle and turns only 90°; the difference in the number of turns is obvious at a glance.

<video src="assets/RTM output/01b-Arrows-and-Spin-In.mp4" controls width="560"></video>

> Note:
>
> - `angle` only affects "how much it turns while growing" and not the final pose (the end state is always the object's own angle).
> - To customise the **entrance path** (flying in along a curve, etc.), note that RTM's own `SpinInFromNothing` / `GrowArrow` **have no `path_func`** (not `Transform` subclasses, so it is swallowed); use `Transform(path_func=...)` or `MoveAlongPath` instead.

Not demonstrated:

- `point_color=None`: no separate clip (the default = keeps the object's own colour).
- A custom `path_func` path: RTM's own `SpinInFromNothing` **has no such parameter** (the rotation is done by `_grow_rot`, not path interpolation), so passing it does nothing; only the CE version uses `spiral_path(angle)` to occupy `path_func`.

The old wording in the samples' docstring follows the CE line; this page's parameter table is authoritative.

---

See also: [The Grow Family (Point / Center / Edge)](01-The-Grow-Family.md) · [Emphasis and Flashing](../Emphasis-and-Highlights/01-Indicate-and-Flash.md) · [Transform Core](../Transforms/01-Transform-Core.md)
