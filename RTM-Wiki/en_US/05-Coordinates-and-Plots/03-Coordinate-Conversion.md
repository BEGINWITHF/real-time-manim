# Coordinate conversion (c2p / p2c / @ / add_coordinates)

The **most error-prone** topic in coordinate systems: data coordinates ⇄ screen coordinates. Placing any element (`Dot`, `Text`, `next_to`, `move_to`) relies on this set of conversions, and computing the scale by hand is a source of errors.

## The semantics of x_range and x_length

| Form | Meaning |
| --- | --- |
| `x_range=[a, b, s]` | **data range** `[x_min, x_max]` and **tick step** `s`; the step only decides how many ticks/labels are drawn, it does not change the scale |
| `x_length=L` | the axis's **physical length** on screen (Manim units) |
| scale | `x_length / (b - a)`, the number of Manim units per 1 data unit |
| defaults | `Axes()` → `x_range=[-7,7,1]`, `x_length≈12`, `y_range=[-4,4,1]`, `y_length≈6`; `NumberPlane()` → `x_length=None` (1 data unit = 1 Manim unit) |
| two-element tuple | `x_range=[0, 5]` is equivalent to `[0, 5, 1]` |
| range without 0 | moves 0 (or the nearest endpoint) to the centre automatically, and `c2p` still computes from data coordinates |

## coords_to_point / c2p (data → screen)

```python
def coords_to_point(self, *coords: float | Sequence[float] | np.ndarray) -> np.ndarray
```

Alias `c2p(*coords)`, and it can also be written `ax @ (x, y)`. The only correct way to place any element.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*coords` | `float \| Sequence[float] \| np.ndarray` | required | single point `ax.c2p(1, 2)` / `ax.c2p([1, 2])`; batch `ax.c2p([x0,x1,...], [y0,y1,...])`; add a third argument for 3D |

> **Returns**: an `np.ndarray` whose shape matches the input (a single point is a `(3,)` scene coordinate).

## point_to_coords / p2c (screen → data)

```python
def point_to_coords(self, point: Point3DLike) -> np.ndarray
```

The inverse of `c2p`, often used to work out "what is this point on the graph".

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `point` | `Point3DLike` | required | a scene point; you can also pass a list of points `[RIGHT, [0,1,0]]` |

> **Returns**: an `np.ndarray` (e.g. `[4.0, 7.0]`); passing a list of points returns a 2D array.

## Quick syntax reference (the @ operator, table only)

```python
ax.c2p(2, 1.5)          # recommended
ax @ (2, 1.5)           # same thing (__matmul__)
ax.p2c(point)           # reverse, recommended
[1.0, 0.5, 0.0] @ ax    # reverse; only a plain list/tuple is allowed,
                        # np.ndarray is grabbed by numpy first and raises -- use p2c
NumberLine() @ 3        # number-line version: value -> point (i.e. n2p)
```

Polar version: `CoordinateSystem.polar_to_point(radius, azimuth)` (alias `pr2pt`), `point_to_polar(point)` (alias `pt2pr`); internally they are the trigonometric transform of `c2p`/`p2c`, see [Polar and 3D coordinates](07-Polar-and-3D-Coordinates.md) for details.

#### Sample: `c2p`/`p2c`/`@`/batch conversion

This sample demonstrates three sets of usage:

- the green dot lands via `c2p`, and the `p2c` read-back result is shown next to it.
- the yellow dot demonstrates the `@` form and uses an `assert` for a round-trip self-check.
- three blue dots demonstrate "pass two arrays to convert a batch at once".

```python
import numpy as np

from real_time_manim import Scene, Axes, Dot, Text, VGroup, \
    YELLOW, GREEN, BLUE, GREY_B, UP, DOWN, UR, DL, \
    Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class C2PDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03-c2p-p2c", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        ax = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1],
                  x_length=8, y_length=5, tips=False)   # coordinate system without arrows
        ax.add_coordinates()   # tick numbers
        labels = ax.get_axis_labels("x", "y")   # axis names
        lab = Text("p = ax.c2p(2, 1.5)   coords = ax.p2c(p)",
                   font_size=26, color=GREY_B).to_edge(DOWN)   # method description label
        win.play(Create(ax), FadeIn(labels), FadeIn(lab), run_time=0.8)   # the coordinate system and the labels appear together

        p = ax.c2p(2, 1.5)   # "c2p": data coordinates -> screen coordinates, the only correct way to place elements
        dot = Dot(p, color=GREEN)   # a green dot at the c2p result
        coords = ax.p2c(p)   # "p2c": screen coordinates -> data coordinates (the inverse of c2p)
        readout = Text("p2c=(%.1f, %.1f)" % (coords[0], coords[1]),   # show the read-back result on screen
                       font_size=28, color=GREEN).next_to(dot, UR, buff=0.2)
        win.play(FadeIn(dot), FadeIn(readout), run_time=0.5)   # the green dot and the read-back text fade in
        win.play(Wait(0.6))   # pause 0.6s to see the read-back result

        q = ax @ (1, -2)   # the "@" form: equivalent to ax.c2p(1, -2)
        assert np.allclose(ax.p2c(q), [1, -2], atol=1e-6)   # round-trip self-check: p2c(c2p(x)) == x
        dot2 = Dot(q, color=YELLOW)   # a yellow dot at the @ result
        tag2 = Text("ax @ (1,-2)", font_size=26, color=YELLOW).next_to(dot2, DL, buff=0.2)
        win.play(FadeIn(dot2), FadeIn(tag2), run_time=0.5)   # the yellow dot and label fade in

        batch = ax.c2p([-3, 0, 3], [-2, 0, 2])   # batch conversion: pass two equal-length arrays to compute 3 points at once
        dots3 = VGroup(*[Dot(pt, color=BLUE) for pt in batch])   # three blue dots placed on the diagonal
        win.play(FadeIn(dots3), run_time=0.4)   # the three blue dots fade in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: the green dot is positioned by `ax.c2p(2, 1.5)` — whatever the scale of the coordinate system, `c2p` gives the correct screen coordinate. `ax.p2c(p)` then reverses the screen coordinate back into `(2.0, 1.5)` and displays it, proving the two are inverses. The yellow dot is placed with `ax @ (1, -2)`, and `assert np.allclose(ax.p2c(q), [1, -2])` performs a round-trip self-check. Finally `ax.c2p([-3, 0, 3], [-2, 0, 2])` passes two equal-length arrays and converts the three points on the diagonal in one go — far faster than a loop when placing a batch of points.

<video src="assets/RTM output/03-Coordinate-Conversion-c2p_p2c.mp4" controls width="560"></video>

> Note:
>
> - The reverse `@` (`point @ ax`) only takes a plain `list`/`tuple` — an `np.ndarray` is grabbed by numpy and interpreted as matrix multiplication, raising an error; always use `p2c` for the reverse direction.
> - The return value of `c2p` is an `np.ndarray`; do not expect it to be a `Point` mobject.

## add_coordinates in detail (table only)

Quick syntax reference for `CoordinateSystem.add_coordinates(*axes_numbers, **kwargs)` (for full parameter details and samples see [02-Axes](02-Axes.md)):

| Form | Effect |
| --- | --- |
| `ax.add_coordinates()` | every axis uses the default tick numbers |
| `ax.add_coordinates(None, [0, 0.5, 1])` | the x axis keeps its default, the y axis shows only the given values |
| `ax.add_coordinates(range(0, 9, 2), None)` | changes only the x axis, the y axis is untouched |
| `ax.add_coordinates({1: "Mon", 2: "Tue"}, None)` | dict mapping: value → arbitrary label (a `str` automatically becomes `MathTex`) |
| `ax.add_coordinates(..., font_size=24)` | `**kwargs` are forwarded to `add_numbers`/`add_labels` |

Three-axis (`ThreeDAxes`) form: `ax.add_coordinates(x_labels, None, z_labels)`; retrieve the labels with `ax.coordinate_labels`.

---

See also: [Two-dimensional coordinate system](02-Axes.md) · [Number line methods](01b-NumberLine-Methods.md) · [Polar and 3D coordinates](07-Polar-and-3D-Coordinates.md)
