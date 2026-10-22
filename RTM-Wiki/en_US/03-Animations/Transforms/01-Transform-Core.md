# Transform Core: Turn A into B

There are three core ways to interpolate one object into another:

- the whole-object morph `Transform`
- the hand-over `ReplacementTransform`
- the "change the target first, then play" `MoveToTarget`

For the ways that do not write a target by hand, see [Method- and function-driven transforms](02-Method-and-Function-Driven.md).

## Parameters

### Transform

```python
Transform(mobject, target_mobject, path_func=None, path_arc=0, path_arc_axis=None,
          path_arc_centers=None, replace_mobject_with_target_in_scene=False, **kwargs)
```

**Interpolates** the point set of `mobject` into `target_mobject` (padding the point count / submobjects automatically when needed). When it finishes, `mobject` stays in the scene and already looks like the target; `target_mobject` is not added to the scene by default.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the source object being morphed (changed in place) |
| `target_mobject` | `Mobject` | — (**required, no default**) | the morph target. RTM's own `Transform` **must be passed explicitly** (there is no `=None` default) |
| `path_func` | `Callable \| None` | `None` | a custom path function `(start_pts, end_pts, alpha) -> pts`, see `manim.utils.paths` |
| `path_arc` | `float` | `0` | arc angle (radians); `>0` is counterclockwise |
| `path_arc_axis` | `np.ndarray \| None` | `None` (→ `OUT`) | arc rotation axis (used in 3D); when `None` it is treated internally as `[0,0,1]` |
| `path_arc_centers` | `Point3DLike \| None` | `None` | arc centres; when given and `path_func` is not, a `path_along_circles` path is generated automatically |
| `replace_mobject_with_target_in_scene` | `bool` | `False` | `True`: when done, swap `mobject` for `target_mobject` (the target stays in the scene) |
| `**kwargs` | … | — | common `Animation` parameters (`run_time`, `rate_func`…) |

> **Returns**: a `Transform` instance (subclass of `Transform(Animation)`).

### ReplacementTransform

```python
ReplacementTransform(mobject, target_mobject, **kwargs)
```

The same morph as `Transform`, but with `replace_mobject_with_target_in_scene` pinned to `True`: **when it finishes the source object disappears and the target takes over the scene**. The first choice for formula derivations / concept replacement.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the morph source object |
| `target_mobject` | `Mobject` | — (required) | the morph target; it stays in the scene when done |
| `**kwargs` | … | — | all forwarded to `Transform` (`path_arc`, `path_func`, `path_arc_centers`, `replace_mobject_with_target_in_scene` — passing it explicitly overrides the default `True` — and the common `Animation` parameters) |

> **Returns**: a `ReplacementTransform` instance (subclass of `ReplacementTransform(Transform)`).

### MoveToTarget

```python
MoveToTarget(mobject, **kwargs)
```

Morphs `mobject` into `mobject.target` — the copy you modified by hand after `generate_target`; the `.animate` syntax is sugar for it.

**Both versions fail when `target` is missing, but they fail differently**:

- The ManimCE version raises `ValueError` during construction.
- RTM's own version tests `hasattr(mobject, "target")`, and `Mobject` **ships with a `.target` attribute whose value is `None`**. When you have not called `generate_target`, it reads back `None`, so construction does not raise — but `begin` raises `AttributeError: 'NoneType' object has no attribute 'copy'`.

**Call `generate_target` before playing** and both versions are stable.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | you must call `generate_target()` first and set up `mobject.target` |
| `**kwargs` | … | — | forwards the common `Transform` / `Animation` parameters |

> **Returns**: a `MoveToTarget` instance (subclass of `MoveToTarget(Transform)`).

## Examples

#### Sample: Transform / ReplacementTransform / MoveToTarget

Page-specific sample (`assets/RTM code/01-Transform-Core.py`): one segment each for `Transform`'s `path_arc` arc path and a custom `path_func`, `ReplacementTransform`'s "source disappears, target takes over", and the `MoveToTarget` `generate_target()` flow. Source and target differ in shape / position / colour, so you can see exactly what changes at each step.

```python
import os

import numpy as np
from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    RED,
    YELLOW,
    DOWN,
    LEFT,
    OUT,
    RIGHT,
    UP,
    PI,
    Circle,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
    smooth,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    MoveToTarget,
    ReplacementTransform,
    Transform,
    Wait,  # noqa: F401
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


def arc_up(start_pts, end_pts, alpha):
    """Custom path_func: (start_pts, end_pts, alpha) -> pts; the points arc upward while interpolating."""
    pts = start_pts + (end_pts - start_pts) * alpha
    return pts + np.array([0.0, 1.1 * np.sin(np.pi * alpha), 0.0])


class Page_01_Transform_Core(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("Transform core · turn A into B", font_size=44, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # --- 1. Transform: every documented parameter passed explicitly; source and target differ in shape / position / colour ---
        lab1 = VGroup(
            Text("Transform(sq, circ, path_arc=PI / 2,", font_size=30, color=GREY_B),
            Text("  path_func=None, path_arc_axis=OUT,", font_size=30, color=GREY_B),
            Text("  replace_mobject_with_target_in_scene=False)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.3)
        sq = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6).move_to(LEFT * 3.6 + DOWN * 1.2)
        circ = Circle(radius=0.8, color=GREEN).set_fill(GREEN, 0.6).move_to(RIGHT * 2.8 + DOWN * 0.4)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Create(sq), run_time=0.5)
        win.play(                                                    # point-set interpolation plus an arc path
            Transform(sq, circ,                                     # params mobject / target_mobject ✓
                      path_func=None,                               # param path_func=None ✓ (the next step swaps in a custom function)
                      path_arc=PI / 2,                              # param path_arc ✓ (non-default 0: follows a 90° arc)
                      path_arc_axis=OUT,                            # param path_arc_axis ✓ (always the z-axis in 2D)
                      path_arc_centers=None,                        # param path_arc_centers ✓ (see "Not demonstrated")
                      replace_mobject_with_target_in_scene=False,   # param ✓ (default; when done the source stays in the scene)
                      run_time=1.5),                                # param run_time / **kwargs ✓
            run_time=1.5,
        )
        win.play(FadeOut(VGroup(lab1, sq)), run_time=0.5)

        # --- 2. Transform's path_func: a custom interpolation path ---
        lab2 = VGroup(
            Text("Transform(sq2, tri, path_func=arc_up,", font_size=30, color=GREY_B),
            Text("                      run_time=1.3)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        sq2 = Square(side_length=1.2, color=YELLOW).set_fill(YELLOW, 0.6).move_to(LEFT * 3.6 + DOWN * 1.2)
        tri = Triangle(color=RED).scale(0.8).set_fill(RED, 0.6).move_to(RIGHT * 3.2 + DOWN * 1.2)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Create(sq2), run_time=0.5)
        win.play(                                     # the interpolated points arc up along the custom path, then come back down
            Transform(sq2, tri, path_func=arc_up, run_time=1.3),
            run_time=1.3,
        )
        win.play(FadeOut(VGroup(lab2, sq2)), run_time=0.5)

        # --- 3. ReplacementTransform: when done the source disappears and the target takes over the scene ---
        lab3 = VGroup(
            Text("ReplacementTransform(left, right,", font_size=30, color=GREY_B),
            Text("                     run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        left = Text("left", font_size=44, color=BLUE).move_to(LEFT * 3.2 + DOWN * 1.2)
        right = Text("right", font_size=44, color=GREEN).move_to(RIGHT * 3.2 + DOWN * 1.2)
        self.add(left)                              # put the source object into the scene first
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(ReplacementTransform(left, right, run_time=1.2), run_time=1.2)
        win.play(FadeOut(VGroup(lab3, right)), run_time=0.5)

        # --- 4. MoveToTarget: call generate_target() to set up .target first, then play ---
        lab4 = VGroup(
            Text("sq3.generate_target(); sq3.target.shift(", font_size=30, color=GREY_B),
            Text("  RIGHT * 3).scale(1.6).set_fill(GREEN, 0.6)", font_size=30, color=GREY_B),
            Text("MoveToTarget(sq3, run_time=1.3)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.3)
        sq3 = Square(side_length=0.9, color=YELLOW).set_fill(YELLOW, 0.6).move_to(LEFT * 3.4 + DOWN * 1.4)
        win.play(FadeIn(lab4, shift=DOWN), run_time=0.4)
        win.play(Create(sq3), run_time=0.5)
        sq3.generate_target()                       # param mobject.target ✓ (set up the target state first)
        sq3.target.shift(RIGHT * 3).scale(1.6).set_fill(GREEN, 0.6)
        win.play(MoveToTarget(sq3, run_time=1.3), run_time=1.3)

        win.play(FadeOut(VGroup(title, lab4, sq3)), run_time=0.6)
        win.close()                                 # param win.close()
```

What this code does: four segments.

- The first segment morphs a blue square along a 90° arc into a green circle (`path_arc=PI/2`; shape / position / colour all change, and when it finishes the square stays in place shaped like the circle).
- The second segment swaps in the custom `path_func=arc_up`: as the square turns into a triangle, every interpolated point arcs up and then back down.
- The third segment uses `ReplacementTransform` to turn the `left` text on the left into the `right` text on the right — the source simply disappears and the target takes over.
- The fourth segment calls `generate_target()` to set up the target state (shift three units right, scale 1.6x, fill green), then plays `MoveToTarget` in one go.

<video src="assets/RTM output/01-Transform-Core.mp4" controls width="560"></video>

> Note: in the sample, `Transform` / `ReplacementTransform` / `MoveToTarget` / `Write` are imported from `real_time_manim.vulkan_bind` — RTM has its own implementation of this core transform group; `FadeIn` / `FadeOut` / `Create` and `Wait` (the RTM version) also come from `vulkan_bind`, while ordinary animation classes come from `real_time_manim`.
>
> - when `Transform` finishes the source object is still in the scene, only now it looks like the target.
> - to get the "swap it out" effect, either pass `replace_mobject_with_target_in_scene=True` explicitly or just use `ReplacementTransform` directly.

See also: [Method- and function-driven transforms](02-Method-and-Function-Driven.md) · [Swapping / copy transforms](04-Swapping-and-Copy-Transforms.md) · [Fade-out / fade-in transforms](05-Fade-Through-Transforms.md)
