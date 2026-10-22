# StreamLines

Scatters "test particles" on a grid, integrates their trajectories along the field with Euler's method and draws them as smooth curves that show the flow direction at a glance; colors are by default sampled from the gradient according to field strength. **Construction simulates each complete trace**, so a larger `virtual_time` makes construction slower. RTM has no dedicated stream-line renderer; it goes through the generic vector fallback. In testing, line-by-line creation, continuous flow and smooth wind-down all work (see the samples below).

## class StreamLines (RTM generic vector fallback rendering)

```python
StreamLines(func: Callable[[np.ndarray], np.ndarray], color: ParsableManimColor | None = None, color_scheme: Callable[[np.ndarray], float] | None = None, min_color_scheme_value: float = 0, max_color_scheme_value: float = 2, colors: Sequence[ParsableManimColor] = DEFAULT_SCALAR_FIELD_COLORS, x_range: Sequence[float] = None, y_range: Sequence[float] = None, z_range: Sequence[float] = None, three_dimensions: bool = False, noise_factor: float | None = None, n_repeats = 1, dt = 0.05, virtual_time = 3, max_anchors_per_line = 100, padding = 3, stroke_width = 1, opacity = 1, **kwargs)
```

### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `func` | `Callable` | required | field function |
| `color` / `color_scheme` / `min_color_scheme_value` / `max_color_scheme_value` / `colors` | same as `ArrowVectorField` | same as above | coloring-related |
| `x_range` / `y_range` / `z_range` | `Sequence[float] \| None` | `None` | the **spawn area** for the particles (`[min, max, step]`) |
| `three_dimensions` | `bool` | `False` | 3D stream lines |
| `noise_factor` | `float \| None` | `None` → `step_y / 2` | random jitter amplitude per spawn point (to avoid a perfectly regular look) |
| `n_repeats` | `int` | `1` | how many particles to spawn per spawn point |
| `dt` | `float` | `0.05` | integration step; smaller = more accurate trajectories |
| `virtual_time` | `float` | `3` | the simulated "duration" of each stream line; larger = longer lines and slower construction |
| `max_anchors_per_line` | `int` | `100` | max anchors per line; excess is decimated (lowers complexity, not length) |
| `padding` | `float` | `3` | how far a particle may leave the spawn box before termination |
| `stroke_width` | `float` | `1` | line width |
| `opacity` | `float` | `1` | opacity |
| `**kwargs` | - | - | forwarded to `VectorField` |

**Returns** a `StreamLines`; every stream line is stored in the `stream_lines` attribute.

### Animation methods

| Signature | Frequency | Effect |
| --- | --- | --- |
| `create(lag_ratio=None, run_time=None, **kwargs) -> AnimationGroup` | 🔴 | draws the stream lines one by one in **random order**; `run_time` defaults to `virtual_time`, `lag_ratio` defaults to `run_time/2/line count` |
| `start_animation(warm_up=True, flow_speed=1, time_width=0.3, rate_func=linear, line_animation_class=ShowPassingFlash, **kwargs) -> None` | 🔴 | starts the **continuous-flow** animation (attaches an updater, no return value); `warm_up=True` first lights the lines up one by one, and `time_width` is the proportion of each line visible at once |
| `end_animation() -> AnimationGroup` | 🔴 | smoothly winds down the continuous animation (raises `ValueError` if `start_animation` was not called); returns a playable animation |

#### Sample: create draws the lines one by one in random order

An `sx*sin + sy*cos` field with a spawn grid `x∈[-4,4]`, `y∈[-2.5,2.5]`, step 1. Blue, line width 3, anchors decimated to 15, and `virtual_time=1` to keep construction cheap; `sl.create(run_time=1.4)` draws the lines one by one in random order.

```python
import numpy as np
from real_time_manim import Scene, Text, StreamLines, \
    BLUE, YELLOW, GREY_B, UP, DOWN, LEFT, \
    Write, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class StreamLinesCreateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02b-StreamLines-create", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text("sl.create(run_time=..., lag_ratio=...)",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.3)   # signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        func = lambda pos: np.sin(pos[0] / 2) * UP + np.cos(pos[1] / 2) * LEFT   # field function
        sl = StreamLines(
            func,                                   # parameter "func"
            x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],   # spawn grid
            color=BLUE,                             # parameter "color": whole field blue
            stroke_width=3,                         # parameter "stroke_width"
            max_anchors_per_line=15,                # decimate anchors: faster construction, smoother lines
            virtual_time=1,                         # parameter "virtual_time": simulated trace duration
        )
        win.play(sl.create(run_time=1.4), run_time=1.4)   # draw the lines one by one in random order
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: at construction time every stream line's full trajectory is already integrated. `virtual_time=1` simulates only 1 virtual second, and together with the `max_anchors_per_line=15` decimation, construction is fast.

Then `sl.create(run_time=1.4)` draws these curves one by one in **random order** — the default `lag_ratio` spreads them out automatically as `run_time/2/line count`, giving the whole segment a staggered growth rhythm.

<video src="assets/RTM output/02b-StreamLines-create.mp4" controls width="560"></video>

> Note:
>
> - `create()`'s `run_time` **defaults to `virtual_time`** — leave it out and the draw looks like a 3-second wait.
> - A larger `virtual_time` makes construction slower (the whole trace is integrated at creation); for big fields, turn it down first, or turn down `max_anchors_per_line`.

#### Sample: start_animation / end_animation continuous flow

The same stream lines are first drawn with `create`, then `start_animation(warm_up=False, flow_speed=1.5, time_width=0.5)` attaches the continuous flow, and after 2 seconds `win.play(sl.end_animation(), ...)` winds it down smoothly.

```python
import numpy as np
from real_time_manim import Scene, Text, StreamLines, \
    BLUE, YELLOW, GREY_B, UP, DOWN, LEFT, \
    Write, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class StreamLinesFlowDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("02b-StreamLines-flow", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text("start_animation(flow_speed=1.5, time_width=0.5) ... end_animation()",
                   font_size=24, color=GREY_B).next_to(title, DOWN, buff=0.3)   # signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        func = lambda pos: np.sin(pos[0] / 2) * UP + np.cos(pos[1] / 2) * LEFT   # field function
        sl = StreamLines(
            func,                                   # parameter "func"
            x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],   # spawn grid
            color=BLUE,                             # parameter "color": whole field blue
            stroke_width=3,                         # parameter "stroke_width"
            max_anchors_per_line=15,                # decimate anchors
            virtual_time=1,                         # parameter "virtual_time"
        )
        win.play(sl.create(run_time=0.8), run_time=0.8)   # draw the stream lines first
        self.add(sl)   # put "sl" itself into the scene: the updater lives on it, and without add the whole field is black
        sl.start_animation(warm_up=False, flow_speed=1.5, time_width=0.5)   # parameters "flow_speed" / "time_width"
        win.play(Wait(2.0))   # the light point keeps flowing along the lines for 2 seconds
        win.play(sl.end_animation(), run_time=0.6)   # smoothly wind down the continuous animation
        win.close()   # close the RTM window
```

What this code does: `start_animation` **attaches an updater directly** (it has no return value and cannot be `play`ed on its own), so just call it before `win.play(Wait(2.0))`.

Each of the three parameters handles one thing:

- `flow_speed=1.5` decides how fast the light point travels;
- `time_width=0.5` decides what fraction of each line is lit at once;
- `warm_up=False` skips the "line-by-line warm-up" and flows right away.

Finally `end_animation()` returns a playable animation that eases the continuous effect out smoothly.

The `self.add(sl)` line in the middle cannot be omitted: `create` only puts **each individual line** into the scene; the `sl` group itself is not in the scene, yet the updater lives on `sl`. Without adding it, `begin()` has already trimmed the lines to empty and the updater never runs, so the frame is all black (measured the same on both engines).

<video src="assets/RTM output/02b-StreamLines-flow.mp4" controls width="560"></video>

> Note:
>
> - `end_animation()` raises `ValueError` when `start_animation` has **never been called**; conversely, `start_animation` alone without winding down also renders fine (the frame just stays in the flowing state), but the pair should appear together to explain this API pair properly.
> - During the continuous animation the light points keep moving through `Wait`, so frame content differs from frame to frame; the light-point phase may differ slightly between the two engines — this is normal.
> - **The deadliest pitfall is forgetting `self.add(sl)`** — the symptom is that the whole stream-line field disappears once the flow starts, with no error.

---

See also: [Vector Fields and Streamlines](02-Vector-Fields-and-Streamlines.md) · [Graph and DiGraph](01-Graph-and-DiGraph.md) · [Graph Editing and Layout](01b-Graph-Editing-and-Layout.md)
