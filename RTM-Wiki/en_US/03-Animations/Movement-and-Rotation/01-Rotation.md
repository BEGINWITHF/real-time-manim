# Rotation animations: Rotate and Rotating

The manual's "7.1 Rotation" has two classes: `Rotate` turns an object by `angle` **in one shot** (the RTM-native version bakes a real per-frame rotation when an explicit pivot or a non-z axis is given); `Rotating` is a continuous turn that "actually rotates frame by frame".

Both classes are verified renderable (`Rotate`/`Rotating` go through the RTM-native implementation), and the three samples each have their own clip.

## Parameters

### Rotate

```python
Rotate(mobject, angle=PI, axis=OUT, about_point=None, about_edge=None, **kwargs)
```

Inherits `Rotate(Animation)` (RTM-native implementation, `real_time_manim/animations/rotate.py`; **not** a `Transform` subclass). It rotates the object by `angle` radians **in one shot** (default `PI`).

RTM uses **per-frame baking** — when an explicit `about_point`/`about_edge` (or a non-z axis) is given, each frame applies a real rotation of the point set / an orbit about the pivot, and the final state matches CE point for point; when it only turns about the object's own centre with the axis parallel to z, it falls back to the renderer's scalar drawing channel (the cheapest).

When `about_point` is not given the object's centre is used; `about_edge` lets a bounding-box edge act as the rotation centre (e.g. `about_edge=UP`).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the object being rotated |
| `angle` | `float` | `PI` | rotation angle (radians). **accepts** radian values such as `PI`, `2*PI/3`, `90 * DEGREES` |
| `axis` | `Vector3DLike` | `OUT` | rotation axis (in 2D that is the z axis). Already wired (completed 2026-10-16, test `tests/test_gap_transform_motion.py`): with the axis parallel to ±z it uses the scalar drawing channel and flips the angle by the axis sign (`axis=IN` rotates the other way, which previously did nothing at all); other axes take a per-frame 3D Rodrigues rotation (in a 2D scene this shows up as perspective compression, in a 3D scene as a full rotation). **Usage note**: `axis` is fundamentally a 3D parameter, so changing it in 2D usually has no visible effect (parallel to z it is equivalent to a mirror/reversal) |
| `about_point` | `Point3DLike \| None` | `None` | rotation centre; `None` uses `mobject.get_center()`; **accepts** a coordinate point |
| `about_edge` | `Vector3DLike \| None` | `None` | when `about_point` is `None`, a bounding-box edge can replace the centre (e.g. `UP`). Already wired (completed 2026-10-16): precedence `about_point` > `about_edge` (takes `get_critical_point(about_edge)`) > if neither is given, the default own-centre is kept |
| `**kwargs` | `Any` | — | `Animation` common parameters (`run_time`, `rate_func`…). The RTM-native `Rotate` is not a `Transform` subclass, so the two kwargs `path_arc`/`path_func` are still swallowed on `Rotate` — an arc path requires going through `Transform` (see [Transform Core](../Transforms/01-Transform-Core.md)) |

> **Returns**: `Animation` (hand it to `play` to play it).

#### Sample: rotate 120° about an orange fixed point

The orange dot is the rotation centre; the blue square orbits it by 120°; `rate_func=smooth` eases in and out.

```python
from real_time_manim import Scene, Text, VGroup, Square, Dot, BLUE, GREY_B, ORANGE, YELLOW, \
    UP, DOWN, RIGHT, ORIGIN, PI, FadeIn, Write, smooth
from real_time_manim.vulkan_bind import MLWindow, Rotate, Wait

class RotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("01-Rotate", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("Rotate(sq, angle=2*PI/3, about_point=PIVOT,", font_size=30, color=GREY_B)
        l2 = Text("         run_time=1.6, rate_func=smooth)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        pivot = Dot(point=ORIGIN + DOWN * 1.4, radius=0.09, color=ORANGE)   # rotation centre
        sq = Square(side_length=1.3, color=BLUE).set_fill(BLUE, 0.5).move_to(pivot.get_center() + RIGHT * 2.6)   # blue square
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(pivot, sq)), run_time=0.4)   # fade in the label and the shapes
        win.play(Rotate(sq, angle=2 * PI / 3, about_point=pivot.get_center(),   # parameter "angle / about_point"
                        run_time=1.6, rate_func=smooth))                        # parameter "run_time / rate_func"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: the RTM-native `Rotate`, when given an explicit `about_point`, **bakes a real rotation per frame** — every point of the blue square orbits the orange dot by 120°; only when `about_point` is not given does it fall back to turning about the object's own centre.

The 120° turn takes 1.6 seconds, and `rate_func=smooth` eases in and out.

<video src="assets/RTM output/01-Rotation-rotate.mp4" controls width="560"></video>

> Note:
>
> - `Rotate` turns to an **interpolated final state**; but the RTM-native version, when given an explicit `about_point`/`about_edge` (as the sample does), **bakes the real rotation/orbit per frame**, so the final state matches CE point for point. Only when it turns about its own centre with the axis parallel to z does it use the renderer's scalar channel.
> - `axis`/`about_edge` are already wired on the RTM side (marked in the parameter table, test `tests/test_gap_transform_motion.py`). In 2D, `axis` only has a visible effect when parallel to ±z (`axis=IN` rotates the other way); for a continuous turn that "really rotates every frame", see the two `Rotating` samples below.

### Rotating

```python
Rotating(mobject, angle=TAU, axis=None, about_point=None, about_edge=None,
         run_time=5, rate_func=linear, **kwargs)
```

Inherits `Rotating(Animation)` (**not** a subclass of `Rotate`, nor of `Transform`), from `real_time_manim/animations/rotating.py`. It is a **continuous rotation** animation: every frame it resets the object to its starting state, then turns it by `rate_func(alpha)*angle` (with an explicit `about_point`/`about_edge` or a non-z axis it bakes a real 3D / pivot-centred rotation per frame).

So it "actually rotates" and does not distort through interpolation. By default it turns a full circle in 5 seconds at constant rate, good for gears, clock hands and 3D objects.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the object being rotated |
| `angle` | `float` | `TAU` | total rotation angle (radians). **accepts** `TAU`, `180 * DEGREES`, `PI`… |
| `axis` | `Vector3DLike \| None` | **`None`** | the RTM-native signature's default is **`None`** (semantically equivalent to `OUT`: `_is_3d_axis()` treats `None` as a non-3D axis, and `interpolate` handles it as `OUT`); **the ManimCE signature's default is written as `OUT`** — the two behave the same, only the default's spelling differs. **accepts** `OUT` (forward) and `IN` (reverse turn in a 2D frame) |
| `about_point` | `Point3DLike \| None` | `None` | rotation centre; `None` uses the object's centre. Passing an explicit value bakes a real orbit per frame |
| `about_edge` | `Vector3DLike \| None` | `None` | when `about_point` is `None`, a bounding-box edge acts as the pivot (e.g. `UP` = the top edge as a hinge) |
| `run_time` | `float` | `5` | total duration (seconds) |
| `rate_func` | `Callable` | `linear` | progress function. **accepts** `linear` (constant rate), `rush_into`, `smooth`… |
| `**kwargs` | `Any` | — | `Animation` common parameters. Not a `Transform` subclass, so `path_arc`/`path_func` are swallowed and do nothing |

> **Returns**: `Animation` (hand it to `play` to play it).

#### Sample: axis=IN reverses the turn in a 2D frame

A gold arrow continuously turns 180° with `Rotating`, and `axis=IN` reverses the direction of turn in the 2D frame.

```python
from real_time_manim import Scene, Text, VGroup, Arrow, GOLD, GREY_B, YELLOW, UP, DOWN, \
    RIGHT, ORIGIN, IN, DEGREES, FadeIn, Write, linear
from real_time_manim.vulkan_bind import MLWindow, Rotating, Wait

class RotatingAxisDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("01-RotatingAxis", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("Rotating(arrow, angle=180*DEGREES, axis=IN,", font_size=30, color=GREY_B)
        l2 = Text("          run_time=1.4, rate_func=linear)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        arrow = Arrow(ORIGIN, RIGHT * 2.0, buff=0, color=GOLD).shift(DOWN * 1.6)   # gold arrow
        win.play(FadeIn(sig, shift=DOWN), FadeIn(arrow), run_time=0.4)   # fade in the label and the arrow
        win.play(Rotating(arrow, angle=180 * DEGREES, axis=IN,   # parameter "angle / axis=IN" (reverse turn in the 2D frame)
                          run_time=1.4, rate_func=linear))       # parameter "run_time / rate_func"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: `Rotating` resets the object to its starting state each frame, then turns it by `rate_func(alpha)*angle`, so it "actually rotates" and does not distort through interpolation; `linear` is constant rate. With the same `angle=180*DEGREES`, switching `axis` from the default `OUT` to `IN` reverses the direction of turn in the 2D frame.

<video src="assets/RTM output/01-Rotation-rotating_axis.mp4" controls width="560"></video>

#### Sample: about_edge flips 90° with the top edge as a hinge

A teal triangle flips 90° about its top edge as a hinge.

```python
from real_time_manim import Scene, Text, VGroup, Triangle, TEAL, GREY_B, YELLOW, UP, DOWN, \
    DEGREES, FadeIn, Write, rush_into
from real_time_manim.vulkan_bind import MLWindow, Rotating, Wait

class RotatingEdgeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("01-RotatingEdge", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("Rotating(tri, angle=90*DEGREES, about_edge=UP,", font_size=30, color=GREY_B)
        l2 = Text("           run_time=1.6, rate_func=rush_into)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        tri = Triangle(color=TEAL).scale(1.1).set_fill(TEAL, 0.5).shift(DOWN * 2.0)   # teal triangle
        win.play(FadeIn(sig, shift=DOWN), FadeIn(tri), run_time=0.4)   # fade in the label and the triangle
        win.play(Rotating(tri, angle=90 * DEGREES, about_edge=UP,   # parameter "about_edge=UP" (the top edge as a hinge)
                          run_time=1.6, rate_func=rush_into))       # parameter "run_time / rate_func"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: `about_edge=UP`, with `about_point` not given, uses the bounding box's top edge as the pivot — the triangle swings over like a hinge hung on its top edge; `rate_func=rush_into` is slow first and fast after, finishing crisply.

<video src="assets/RTM output/01-Rotation-rotating_edge.mp4" controls width="560"></video>

Not demonstrated: `Rotate`'s `axis` / `about_edge` — already wired (completed 2026-10-16, test `tests/test_gap_transform_motion.py` covers the `axis=IN` reverse turn, the `about_edge` pivot precedence and the non-z 3D Rodrigues path), but this page has no dedicated clip yet. `Rotating`'s same-named parameters are demonstrated by the two samples above.

---

See also: [Along Path and Homotopy](02-Along-Path-and-Homotopy.md) · [Wait, Rate and Speed](../Waiting-and-Rate/01-Wait-Rate-and-Speed.md) · [Scaling, Rotation and Stretching (Mobject methods)](../../02-Mobjects/04-Scaling-Rotation-and-Stretching.md)
