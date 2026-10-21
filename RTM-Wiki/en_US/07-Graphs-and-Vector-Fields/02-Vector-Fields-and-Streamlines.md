# Vector fields: ArrowVectorField and VectorField

All three inherit from `VectorField`: give it a `func(point) -> vector` and it handles the coloring, generates the visible elements, and pushes mobjects along the field.

The module constant `DEFAULT_SCALAR_FIELD_COLORS = [BLUE_E, GREEN, YELLOW, RED]` is the default "gradient by magnitude" palette; it is not exported at the top level, so import it with `from manim.mobject.vector_field import ...`.

RTM has no dedicated vector-field renderer; it goes through the generic vector fallback. In testing, the arrow grid, one RK4 step, continuous updater flow and submobject group drift all work (see the samples below).

## ArrowVectorField — representing a vector field with an arrow grid

### class ArrowVectorField (RTM generic vector fallback rendering)

```python
ArrowVectorField(func: Callable[[np.ndarray], np.ndarray], color: ParsableManimColor | None = None, color_scheme: Callable[[np.ndarray], float] | None = None, min_color_scheme_value: float = 0, max_color_scheme_value: float = 2, colors: Sequence[ParsableManimColor] = DEFAULT_SCALAR_FIELD_COLORS, x_range: Sequence[float] = None, y_range: Sequence[float] = None, z_range: Sequence[float] = None, three_dimensions: bool = False, length_func: Callable[[float], float] = lambda norm: 0.45 * sigmoid(norm), opacity: float = 1.0, vector_config: dict | None = None, **kwargs)
```

Samples `func` on a regular grid and draws a whole field of `Vector` arrows; by default the **arrow color gradients across `colors` by magnitude** (if `color` is given, the whole field is single-colored), and lengths are compressed with `length_func` to keep them from getting too long. **Returns** an `ArrowVectorField` (a `VGroup`, directly `self.add`-able).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `func` | `Callable[[ndarray], ndarray]` | required | field function: position → vector |
| `color` | `ParsableManimColor \| None` | `None` | if set, the whole field is single-colored and position-based coloring is off |
| `color_scheme` | `Callable[[ndarray], float] \| None` | `None` | vector → scalar mapping; defaults to `np.linalg.norm` (magnitude) |
| `min_color_scheme_value` / `max_color_scheme_value` | `float` | `0` / `2` | range of scalars mapped to the first/last gradient color |
| `colors` | `Sequence[ParsableManimColor]` | `[BLUE_E, GREEN, YELLOW, RED]` | gradient color list |
| `x_range` / `y_range` / `z_range` | `Sequence[float] \| None` | `None` | `[min, max, step]`; defaults to the frame span, with step defaulting to 0.5 |
| `three_dimensions` | `bool` | `False` | 3D sampling; automatically becomes `True` if `z_range` is given |
| `length_func` | `Callable[[float], float]` | `0.45 * sigmoid(norm)` | actual magnitude → displayed length (default saturating compression) |
| `opacity` | `float` | `1.0` | arrow opacity |
| `vector_config` | `dict \| None` | `None` | passed to the `Vector` constructor (`stroke_width`, `tip_shape`, …) |
| `**kwargs` | - | - | forwarded to `VectorField` |

Other public method ⚪: `get_vector(point)` — builds a single arrow from the field function and coloring (usually called automatically).

#### Sample: ArrowVectorField constructor parameters

The same field rendered twice. The first segment uses the default coloring and default length function, gradienting blue→green→yellow→red by magnitude; the second uses `color=RED` for a single color, `length_func=lambda x: x/3` for a constant linear length, and `vector_config={"stroke_width": 2}` for thinner shafts.

```python
import numpy as np
from real_time_manim import Scene, Text, \
    RED, YELLOW, GREY_B, UP, DOWN, RIGHT, \
    Write, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class ArrowVectorFieldDemo(Scene):
    TUNED = False   # False uses the default coloring and length func; True switches to a single color + linear length

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-ArrowVectorField", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text(
            "color=RED, length_func=lambda x: x/3, vector_config={stroke_width:2}"
            if self.TUNED else "default: color=norm gradient, length_func=0.45*sigmoid",
            font_size=24, color=GREY_B,
        ).next_to(title, DOWN, buff=0.3)   # show the current constructor parameters
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        func = lambda pos: np.sin(pos[1] / 2) * RIGHT + np.cos(pos[0] / 2) * UP   # field function: position -> vector
        if self.TUNED:
            vf = ArrowVectorField(
                func,                                   # parameter "func"
                x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],   # sampling grid
                color=RED,                              # parameter "color": whole field single-colored
                length_func=lambda x: x / 3,            # parameter "length_func": constant linear length
                vector_config={"stroke_width": 2},      # parameter "vector_config"
            )
        else:
            vf = ArrowVectorField(
                func,                                   # parameter "func"
                x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],   # sampling grid
            )
        win.play(FadeIn(vf), run_time=0.8)   # the whole arrow field fades in
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: it builds a position→vector field function with `sin/cos` and samples one arrow every 1 unit on a grid over `x∈[-4,4]`, `y∈[-2.5,2.5]`.

The first segment uses the constructor's default behavior: arrows gradient blue-green-yellow-red by magnitude, with lengths compressed by sigmoid.

The second segment swaps three parameters at once:

- the whole field is red;
- length becomes the linear `x/3`, so higher-magnitude arrows are clearly longer;
- shafts thin to width 2.

<video src="assets/RTM output/02-Vector-Fields-and-Streamlines-field.mp4" controls width="560"></video>

> Note:
>
> - `color` and `colors` / `color_scheme` are mutually exclusive in effect: once `color` is set the whole field is one color; to get position-based gradient back, leave `color` as `None`.
> - `length_func` receives the **normalized magnitude**, and its return value is used directly as the arrow length; give it a constant function to draw equal-length arrows.

## VectorField — vector field base class (draws nothing, only supplies motion rules)

### class VectorField (RTM generic vector fallback rendering)

```python
VectorField(func: Callable[[Point3D], Vector3D], color: ParsableManimColor | None = None, color_scheme: Callable[[Vector3D], float] | None = None, min_color_scheme_value: float = 0, max_color_scheme_value: float = 2, colors: Sequence[ParsableManimColor] = DEFAULT_SCALAR_FIELD_COLORS, **kwargs)
```

The shared base class of `ArrowVectorField` and `StreamLines`; it produces no visible elements itself. It provides the whole set of methods for "making a mobject move along the field" plus the position-based coloring mechanism; the parameters are the same as the table above (no grid-related parameters).

### Public methods

| Signature | Frequency | Effect |
| --- | --- | --- |
| `nudge(mob, dt=1, substeps=1, pointwise=False) -> VectorField` | 🔴 | pushes `mob` one step along the field with RK4; a larger `dt` moves farther, a larger `substeps` is more accurate; `pointwise=True` pushes point by point (which distorts) |
| `get_nudge_updater(speed=1, pointwise=False) -> Callable` | 🔴 | returns an updater; hand it to `mob.add_updater(...)` to keep the mobject flowing along the field |
| `nudge_submobjects(dt=1, substeps=1, pointwise=False) -> VectorField` | 🟡 | pushes each of its own submobjects one step |
| `start_submobject_movement(speed=1, pointwise=False) -> VectorField` | 🟡 | attaches an updater to keep all submobjects flowing; calling it again replaces the old updater |
| `stop_submobject_movement() -> VectorField` | 🟡 | stops the previous updater |
| `shift_func(func, shift_vector) -> Callable` | 🟡 | static helper: returns `lambda p: func(p - shift_vector)`, translating the domain of the field function |
| `scale_func(func, scalar) -> Callable` | 🟡 | static helper: returns `lambda p: func(p * scalar)`, scaling the domain of the field function |
| `fit_to_coordinate_system(coordinate_system) -> None` | ⚪ | converts the field's anchor points into the given coordinate system (**call only once**; transforms in place) |
| `get_colored_background_image(sampling_rate=5) -> Image` | ⚪ | builds a position-colored bitmap (`StreamLines` uses it internally for coloring); a single-colored field raises an error |
| `get_vectorized_rgba_gradient_function(start, end, colors) -> Callable` | ⚪ | a vectorized "scalar array → RGBA array" gradient function (used by the OpenGL renderer) |

### nudge / get_nudge_updater — one-step pushing and continuous flow

`vf.nudge(dot, dt=1, substeps=20)` pushes the red dot one big step along the field with RK4 (**it lands in place immediately**, producing no animation — pair it with a `Line` annotation to make the displacement visible); after `dot.add_updater(vf.get_nudge_updater(speed=1))` switches it to a continuous updater, the red dot keeps flowing along the field lines.

#### Sample: nudge one step and continuous updater

A semi-transparent field as the background; the red dot is first pushed to a new position with one RK4 step (an orange line marks this step's displacement), then `get_nudge_updater` is attached to flow along the field for 2 seconds, and finally `clear_updaters` stops it.

```python
import numpy as np
from real_time_manim import Scene, Text, VGroup, Dot, Line, ArrowVectorField, \
    RED, ORANGE, YELLOW, GREY_B, UP, DOWN, RIGHT, \
    Write, FadeIn, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class NudgeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-VectorField-nudge", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = VGroup(
            Text("vf.nudge(dot, dt=1, substeps=20)   # one RK4 step",
                 font_size=26, color=GREY_B),
            Text("dot.add_updater(vf.get_nudge_updater(speed=1))",
                 font_size=26, color=GREY_B),
        ).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.3)   # two-line signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        func = lambda pos: np.sin(pos[1] / 2) * RIGHT + np.cos(pos[0] / 2) * UP   # field function
        vf = ArrowVectorField(func, x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],
                              opacity=0.4)   # a semi-transparent field as the background
        dot = Dot(radius=0.12, color=RED).move_to([-3.5, -1.4, 0])   # starting point
        win.play(FadeIn(vf), FadeIn(dot), run_time=0.5)   # the field and the red dot fade in
        start = dot.get_center().copy()   # remember the start point
        vf.nudge(dot, dt=1, substeps=20)   # parameters "dt" / "substeps": one big RK4 step (instant, no animation)
        step = Line(start, dot.get_center(), stroke_width=4, color=ORANGE)   # draw this step's displacement
        win.play(Create(step), run_time=0.4)   # the orange segment marks the one-step displacement
        win.play(Wait(0.3))   # wait for 0.3 s
        dot.add_updater(vf.get_nudge_updater(speed=1))   # parameter "speed": switch to continuous flow along the field
        win.play(Wait(2.0))   # the red dot flows along the field for 2 seconds
        dot.clear_updaters()   # detach the updater; the dot stops
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: an `opacity=0.4` arrow grid as the backdrop, with a red dot in the lower-left corner.

`vf.nudge(dot, dt=1, substeps=20)` is **one-shot**: the dot jumps straight to the new position, so it manually draws an orange segment from the start to mark this step's displacement.

Then `add_updater(vf.get_nudge_updater(speed=1))` switches to continuous mode; the red dot winds along the field lines over 2 seconds, and a single `clear_updaters()` call freezes it.

<video src="assets/RTM output/02-Vector-Fields-and-Streamlines-nudge.mp4" controls width="560"></video>

> Note:
>
> - `nudge` itself **produces no animation** (the dot teleports); if you want the process to be visible, add your own `Line` annotation or switch to an updater.
> - At `substeps=1` RK4 degenerates to a single sample; a large `dt` easily overshoots, so animations commonly use `dt=1, substeps=20`, a "big quick push".
> - Once the continuous updater is attached, **the dot moves for as long as the frame keeps rendering** — always remember `clear_updaters()`.

### start_submobject_movement / stop_submobject_movement — group drift

Call `start_submobject_movement(speed=1.5)` on an `ArrowVectorField` as a whole (`StreamLines` behaves the same) and each of its arrows drifts along the field individually; `stop_submobject_movement()` freezes them at their current positions.

#### Sample: submobject group drift

A slightly sparser green arrow grid: after `start_submobject_movement(speed=1.5)` all arrows drift along the field together for 2 seconds, then `stop_submobject_movement()` freezes them.

```python
import numpy as np
from real_time_manim import Scene, Text, ArrowVectorField, \
    GREEN, YELLOW, GREY_B, UP, DOWN, RIGHT, \
    Write, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class SubmobjectMoveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02-VectorField-submobjects", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text("vf.start_submobject_movement(speed=1.5) ... stop_...()",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.3)   # signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        func = lambda pos: np.sin(pos[1] / 2) * RIGHT + np.cos(pos[0] / 2) * UP   # field function
        vf = ArrowVectorField(func, x_range=[-4, 4, 1.5], y_range=[-2.25, 2.25, 1.5],
                              color=GREEN)   # a slightly sparser green arrow grid
        win.play(FadeIn(vf), run_time=0.5)   # the whole arrow field fades in
        vf.start_submobject_movement(speed=1.5)   # parameter "speed": all arrows drift along the field together
        win.play(Wait(2.0))   # drift for 2 seconds
        vf.stop_submobject_movement()   # stop at the current position
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: it widens the grid step to 1.5 and colors the whole field green, giving a sparse array of arrows. `start_submobject_movement(speed=1.5)` attaches an along-field updater to **each arrow**, so over 2 seconds the whole field drifts in unison as if blown by wind, and a single `stop_submobject_movement()` call freezes them all.

<video src="assets/RTM output/02-Vector-Fields-and-Streamlines-submobject.mp4" controls width="560"></video>

> Note:
>
> - This method moves the field object's own submobjects (each `Vector`); it does **not** make an arbitrary mobject follow along — to push something else, use `nudge` / `get_nudge_updater`.
> - Calling it again replaces the old updater; it can only be stopped with `stop_submobject_movement()`, and `clear_updaters()` has no effect on it.

---

See also: [StreamLines](02b-StreamLines.md) · [Graph and DiGraph](01-Graph-and-DiGraph.md) · [Graph Editing and Layout](01b-Graph-Editing-and-Layout.md)
