# patterns & recipes

> scope: idiomatic, copy-pasteable RTM recipes for bots — scene skeletons, value/updater-driven motion, camera moves, coordinate plots, 3D, graphs/fields/streamlines, tables/matrices, text & number animations, composition, boolean ops. Every recipe is a full, runnable `construct()` body.
> src: agent files `runtime.md`, `scene-camera.md`, `mobject.md`, `animation-transform.md`, `animation-motion.md`, `geometry.md`, `text.md`, `coords-charts.md`, `three-d.md`, `graph-vector.md`, `utils.md`; snippets condensed from the tested samples in `../zh_CN/`. On conflict the source tree wins.

Conventions (true for every recipe): `MLWindow` size is forced to **1920×1080 @ 60 fps**; `win.scene = self` and `win.close()` are both **required**; one window per process; RTM-own animation classes come from `real_time_manim.vulkan_bind`, everything else from `real_time_manim` (bundled ManimCE). Never `import manim` first.

---

## live-preview scene skeleton

use: watch the animation on screen in real time; no file output.

```python
from real_time_manim import Scene, Square, Text, BLUE, YELLOW, UP
from real_time_manim.vulkan_bind import MLWindow, Create, Wait

class LiveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)          # forced to 1920x1080 (prints a notice)
        win.scene = self                  # REQUIRED: bind the Scene to the window
        win.play(Text("live", color=YELLOW).to_edge(UP), run_time=0.4)
        win.play(Create(Square(color=BLUE).set_fill(BLUE, 0.6)), run_time=1.0)
        win.play(Wait(0.5))
        win.close()                       # REQUIRED: else nothing flushes / run may not exit

if __name__ == "__main__":
    LiveDemo().construct()                # visible window, real-time playback
```

notes: running `.construct()` directly skips `setup()` — pass a class/instance to `fast_record_scene` if the scene relies on `setup()` (e.g. `MovingCameraScene`'s `camera.frame`). `MLWindow(960, 540)` is corrected to 1080p with a notice; that is normal. Use `record_scene(...)` instead if you want a visible window **and** an mp4.

## offline-render skeleton

use: batch / CI / scripted output, fastest route, no window.

```python
from real_time_manim import Scene, Square, BLUE
from real_time_manim.vulkan_bind import MLWindow, Create, Wait
from real_time_manim.record import fast_record_scene

class OfflineDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        win.play(Create(Square(color=BLUE).set_fill(BLUE, 0.6)), run_time=1.0)
        win.play(Wait(0.5))
        win.close()

if __name__ == "__main__":
    fast_record_scene(OfflineDemo, "out.mp4", jobs="auto")
```

notes: `fast_record_scene` = hidden window, Vulkan framebuffer readback → ffmpeg (fastest); `record_scene` = visible window + background capture thread. Default `out_path` is `~/Downloads/output.mp4`. `jobs="auto"` splits long (≥ 240 frame) importable single-window scenes across processes; instances/lambdas fall back to one pass. `ffmpeg` must be on `PATH`. `win.close()` is still required — the installed `_AutoRecord` finishes the encoder before it. Multi-window scenes get `_partN`.

## title + body + outro (sections)

use: lecture-style scene: header, body content, closing slide; mark sections.

```python
from real_time_manim import Scene, Text, Square, VGroup, YELLOW, BLUE, GREY_B, UP, DOWN
from real_time_manim.vulkan_bind import MLWindow, Create, FadeIn, FadeOut, Wait, Write

class Talk(Scene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self

        self.next_section("intro")                        # in-memory mark only in RTM
        title = Text("My Topic", font_size=54, color=YELLOW).to_edge(UP)
        win.play(Write(title), run_time=0.6)

        self.next_section("body")
        body = VGroup(Text("point 1", font_size=32, color=GREY_B),
                      Text("point 2", font_size=32, color=GREY_B)).arrange(DOWN, buff=0.3)
        win.play(FadeIn(body, shift=DOWN), run_time=0.6)
        win.play(Create(Square(color=BLUE).set_fill(BLUE, 0.5)), run_time=0.6)

        self.next_section("outro")
        win.play(FadeOut(body), FadeOut(title), run_time=0.4)
        win.play(Write(Text("Thanks!", font_size=48, color=YELLOW)), run_time=0.6)
        win.play(Wait(0.5))
        win.close()
```

notes: `next_section` is callable but produces **no artifact** in RTM (no `manim` CLI, no file writer) — to split a long video, write one scene per section and `fast_record_scene` each, then join/cut with ffmpeg. `Title(*parts)` (bundled CE) gives a top-edge header with a full-width underline. `Write` reveals text stroke-by-stroke; `Create` draws shapes; `FadeIn`/`FadeOut` swap content.

## animate a value (ValueTracker + always_redraw / DecimalNumber)

use: drive a shape and a readout from one animated number.

```python
from real_time_manim import (Scene, Dot, Line, DecimalNumber, ValueTracker, always_redraw,
                             RED, GREY, YELLOW, LEFT, RIGHT, UP)
from real_time_manim.vulkan_bind import MLWindow, Wait

class ValueDriven(Scene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        t = ValueTracker(0.0)
        self.add(Line(LEFT * 3, RIGHT * 3, color=GREY))          # a track
        bead = always_redraw(lambda: Dot(color=RED, radius=0.12)
                             .move_to(LEFT * 3 + t.get_value() * RIGHT))
        lbl = DecimalNumber(0, num_decimal_places=2, color=YELLOW).to_edge(UP)
        lbl.add_updater(lambda d: d.set_value(round(float(t.get_value()), 2)))
        self.add(bead, lbl, t)                                   # tracker must be added
        win.play(t.animate.set_value(6.0), run_time=1.0)
        win.play(Wait(0.4))
        win.close()
```

notes: `always_redraw(func)` re-runs the factory each frame and `become`s its result — keep the factory cheap (never build `Text` inside). A tracker driven by an updater must be `self.add`-ed; animate it with `t.animate.set_value(...)`. `t += 1.5` mutates in place (updaters keep reading it); `t = t + 1.5` replaces the object — the classic "number won't move" bug. `DecimalNumber` renders via `MathTex` by default (Typst/LaTeX); pass `mob_class=Text` for a LaTeX-free counter.

## updater-driven motion + MaintainPositionRelativeTo

use: continuous per-frame motion that no `play` drives, and a label that keeps a fixed offset while its target moves.

```python
from real_time_manim import (Scene, Square, Circle, GREEN, PURPLE, UP, LEFT, RIGHT,
                             MaintainPositionRelativeTo)
from real_time_manim.vulkan_bind import MLWindow, Wait

class Followers(Scene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        ref = Square(color=GREEN, side_length=1.0, fill_opacity=0.6).shift(LEFT * 3.5)
        sat = Circle(color=PURPLE, radius=0.35).next_to(ref, UP, buff=0.25)
        self.add(ref, sat)
        win.play(MaintainPositionRelativeTo(sat, ref),
                 ref.animate.shift(RIGHT * 7.0), run_time=1.2)   # satellite keeps its offset
        win.play(Wait(0.3))
        win.close()
```

notes: the offset is recorded at animation start — position first, then play; the binding releases at the end (permanent tracking = `add_updater` / `always`). Free-running updaters (`always_rotate`, `always_shift`, `mob.add_updater(...)`) advance **only while the scene plays**, so wrap them in `win.play(Wait(...))`; stop them with `clear_updaters()`. Spin example: `sq.add_updater(lambda m, dt: m.rotate(dt * 90 * DEGREES))`. For a follower only during a bounded animation use `UpdateFromFunc(label, lambda m: m.next_to(dot, UP))`.

## camera move / zoom (MovingCameraScene)

use: pan/zoom a `MovingCameraScene` by animating `self.camera.frame`.

```python
from real_time_manim import (MovingCameraScene, Square, BLUE, RED, Restore, LEFT, RIGHT)
from real_time_manim.vulkan_bind import MLWindow, Wait

class CameraDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        a = Square(color=BLUE, side_length=1.5).shift(LEFT * 1.5)
        b = Square(color=RED, side_length=1.5).shift(RIGHT * 1.5)
        self.add(a, b)
        self.camera.frame.save_state()                                  # remember full view
        win.play(self.camera.frame.animate.set(width=4.0).move_to(a), run_time=0.8)  # zoom + pan
        win.play(Restore(self.camera.frame), run_time=0.8)              # back to full view
        win.play(Wait(0.5))
        win.close()
```

notes: `self.camera.frame` (a `ScreenRectangle`) exists only with `camera_class=MovingCamera` (the default); plain `Camera` → `AttributeError`. `set(width=...)` changes zoom only (height auto-follows 16:9 — do **not** set it directly); `move_to(...)` changes center only; `save_state()` + `Restore(frame)` restores both. Too-small width → all-black. While the frame moves the whole scene is redrawn per frame. `to_edge`/`to_corner` reference the fixed frame, not `camera.frame`.

## coordinate plot with Axes (function, labels, tangent)

use: plot `y=f(x)` on `Axes`, label it, and draw the tangent at a point.

```python
from real_time_manim import (Scene, Axes, Line, PURPLE_B, GREEN, UR)
from real_time_manim.vulkan_bind import MLWindow, Create, FadeIn, Wait

class PlotDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        ax = Axes(x_range=[-3, 3, 1], y_range=[-1, 7, 1],
                  x_length=9, y_length=5.5).add_coordinates()
        f = lambda x: 0.25 * x**2 + 1
        curve = ax.plot(f, color=PURPLE_B)                       # only entry point (no get_graph)
        win.play(Create(ax), run_time=0.6)
        win.play(Create(curve), run_time=0.8)

        label = ax.get_graph_label(curve, "f(x)", x_val=2, direction=UR, dot=True)
        win.play(FadeIn(label), run_time=0.4)

        x0 = 2.0
        s = ax.slope_of_tangent(x=x0, graph=curve)               # DATA slope dy/dx
        tline = Line(ax.c2p(x0 - 1.5, f(x0) - 1.5 * s),
                     ax.c2p(x0 + 1.5, f(x0) + 1.5 * s), color=GREEN)
        win.play(Create(tline), run_time=0.5)
        win.play(Wait(0.5))
        win.close()
```

notes: `ax.plot` is the only entry point; `x_range`'s third element is the **sampling** step, not ticks. `get_graph_label(label=...)` renders via `MathTex` (write `x^2`, not `x²`). `slope_of_tangent` returns a data slope — extrapolate in data coords, then `ax.c2p` to screen (never use it as a screen slope). Clamp y for vertical asymptotes (`max(-60, min(60, ...))`) and declare `discontinuities=[...], dt=0.1`. `ax.input_to_graph_point(x, graph)` → screen point; `ax.input_to_graph_coords(x, graph)` → data coords.

## area under a curve / Riemann rectangles

use: fill the area under a curve, and approximate it with Riemann rectangles.

```python
from real_time_manim import (Scene, Axes, BLUE, GREEN_B, GREEN_D, YELLOW)
from real_time_manim.vulkan_bind import MLWindow, Create, FadeIn, FadeOut, Wait

class AreaDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 6, 1],
                  x_length=9, y_length=5.5).add_coordinates()
        quad = ax.plot(lambda x: 0.5 * x**2 - 0.5, color=BLUE)   # graph = ax.plot return value
        win.play(Create(ax), run_time=0.6)
        win.play(Create(quad), run_time=0.7)

        area = ax.get_area(quad, x_range=(0, 2), color=(GREEN_B, GREEN_D), opacity=1)
        win.play(FadeIn(area), run_time=0.6)
        win.play(FadeOut(area), run_time=0.3)

        rects = ax.get_riemann_rectangles(quad, x_range=[-2.5, 2.5], dx=0.25,
                                          input_sample_type="left", color=YELLOW)
        win.play(FadeIn(rects), run_time=0.6)
        win.play(Wait(0.6))
        win.close()
```

notes: both methods require `graph` = the `ax.plot` return value (they read its sampler and `t_min`/`t_max`). `get_area(bounded_graph=...)` gives the area **between** two curves; `bounded_graph` must be above `graph` or the area flips sign. `input_sample_type` is the full word `"left"`/`"right"`/`"center"`. Negative-area inversion is controlled by `show_signed_area` (default `True`). Smaller `dx` = better approximation, slower. A single color or a color list (x-gradient) is accepted by `color`.

## 3D scene skeleton (ThreeDScene)

use: a `ThreeDScene` with an oblique camera, an animated camera move, and a pinned title.

```python
from real_time_manim import (ThreeDScene, ThreeDAxes, Cube, Text, BLUE, YELLOW, UP, DEGREES)
from real_time_manim.vulkan_bind import MLWindow, FadeIn, Wait

class CubeDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        self.play = win.play                     # move_camera calls self.play internally
        axes = ThreeDAxes()
        cube = Cube(side_length=1.5).set_color(BLUE)
        title = Text("3D", font_size=34, color=YELLOW)
        self.add_fixed_in_frame_mobjects(title)  # pins position + orientation, and adds it
        title.to_edge(UP)
        self.add(axes, cube)
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # instant, 1 frame
        win.play(FadeIn(cube), run_time=0.5)
        self.move_camera(phi=70 * DEGREES, theta=-135 * DEGREES, run_time=1.4)  # animated
        win.play(Wait(0.5))
        win.close()
```

notes: with nothing set the initial view is **head-on** (`phi=0`, `theta=0`); the classic oblique view is not automatic — use `set_camera_orientation` (jump) or `move_camera` (animated). `move_camera` calls `self.play`, so write `self.play = win.play`. Angles are always radians. Reset with all of `phi`/`theta`/`gamma`/`zoom`/`frame_center` (omitting `frame_center` keeps a previously moved center). `add_fixed_in_frame_mobjects` also adds to the scene; `add_fixed_orientation_mobjects` locks orientation only. `Surface` subclasses (`Sphere`/`Cone`/`Cylinder`/`Torus`) swallow `color=` → use `.set_color(...)` after construction. Ambient rotation only advances while playing (`begin_ambient_camera_rotation(...)` + `win.play(Wait(...))`).

## graph + layout

use: build a networkx-backed `Graph`, animate its layout, add an edge, recolor a vertex.

```python
from real_time_manim import (Scene, Graph, YELLOW, BLUE, RED, BLACK)
from real_time_manim.vulkan_bind import MLWindow, Create, Wait

class GraphDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        g = Graph([1, 2, 3, 4, 5], [(1, 2), (2, 3), (3, 4), (4, 5), (1, 5)],
                  layout="circular", layout_scale=2.4, labels=True, label_fill_color=BLACK,
                  vertex_config={"radius": 0.16, "color": YELLOW, 3: {"color": RED}},
                  edge_config={"stroke_width": 5, "color": BLUE})
        win.play(Create(g), run_time=1.0)
        win.play(g.animate.change_layout("spring", layout_config={"seed": 7}), run_time=1.0)
        win.play(g.animate.add_edges((1, 4)), run_time=0.6)
        win.play(g[3].animate.set_color(RED), run_time=0.4)
        win.play(Wait(0.5))
        win.close()
```

notes: `layout="spring"` must pin `seed` for reproducibility; `"circular"` is deterministic and does **not** accept `seed` (passing it → `TypeError`). Per-vertex / per-edge override entries are whole replacements, not merges. `edge_type` must be a `Line` subclass (`CurvedArrow` → `TypeError`). Edges follow vertices via an auto-installed updater; `g[v]` / `g[(u, v)]` return the live mobject. `.animate` graph mutations (`add_vertices`, `add_edges`, `remove_*`, `change_layout`) are played directly by `win.play`. `DiGraph` adds tips via `edge_config["tip_config"]` and rebuilds them every frame.

## vector field

use: an arrow grid for a `func(point) -> vector` field, plus a dot that flows along it.

```python
import numpy as np
from real_time_manim import (Scene, ArrowVectorField, Dot, RED, ORANGE, UP, DOWN, LEFT, RIGHT)
from real_time_manim.vulkan_bind import MLWindow, FadeIn, Wait

class FieldDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        func = lambda pos: np.sin(pos[1] / 2) * RIGHT + np.cos(pos[0] / 2) * UP
        vf = ArrowVectorField(func, x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],
                              color=RED, length_func=lambda x: x / 3,
                              vector_config={"stroke_width": 2})
        win.play(FadeIn(vf), run_time=0.8)
        dot = Dot(color=ORANGE, radius=0.12)
        self.add(dot)
        dot.add_updater(vf.get_nudge_updater(speed=1))   # flow along the field
        win.play(Wait(2.0))
        dot.clear_updaters()
        win.close()
```

notes: `color=` makes the whole field single-colored and disables position coloring — leave `None` for the magnitude gradient (`colors` / `color_scheme`, default `np.linalg.norm`). `length_func` receives the actual norm; a constant function gives equal-length arrows. `nudge(mob, dt=1, substeps=1)` jumps instantly (no animation); `get_nudge_updater(speed=1)` keeps moving while frames render — always `clear_updaters()` to stop. `DEFAULT_SCALAR_FIELD_COLORS = [BLUE_E, GREEN, YELLOW, RED]` is not top-level exported (import from `manim.mobject.vector_field`).

## streamlines

use: integrate a field into stream lines, then animate them flowing.

```python
import numpy as np
from real_time_manim import (Scene, StreamLines, BLUE, UP, DOWN, LEFT)
from real_time_manim.vulkan_bind import MLWindow, Wait

class StreamDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        func = lambda pos: np.sin(pos[0] / 2) * UP + np.cos(pos[1] / 2) * LEFT
        sl = StreamLines(func, x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],
                         color=BLUE, stroke_width=3,
                         max_anchors_per_line=15, virtual_time=1)
        win.play(sl.create(run_time=0.8), run_time=0.8)   # draws lines in random order
        self.add(sl)                                      # REQUIRED: flow updater lives on sl
        sl.start_animation(warm_up=False, flow_speed=1.5, time_width=0.5)
        win.play(Wait(2.0))
        win.play(sl.end_animation(), run_time=0.6)
        win.close()
```

notes: the full trajectory is integrated at construction — `virtual_time` dominates build cost (lower it or `max_anchors_per_line`). `create()`'s `run_time` defaults to `virtual_time`; forgetting it looks like a 3-second wait. `start_animation(...)` only attaches an updater (not playable on its own); `end_animation()` returns a playable animation and raises `ValueError` if `start_animation` was never called. **`self.add(sl)` is mandatory** — without it the flow updater never runs and the field renders black with no error. RTM cannot tint per pixel; pass `color=` explicitly for deterministic output.

## table / matrix with highlighted cell

use: a grid with a highlighted cell — `Table` background block, or a `Matrix` entry boxed.

```python
from real_time_manim import (Scene, Table, Matrix, Text, SurroundingRectangle,
                             YELLOW, TEAL, RED)
from real_time_manim.vulkan_bind import MLWindow, FadeIn, Wait, Write

class TableDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        t = Table([["a", "b"], ["c", "d"]], include_outer_lines=True,
                  element_to_mobject=Text, element_to_mobject_config={"font_size": 34})
        win.play(Write(t), run_time=0.7)
        t.add_highlighted_cell((1, 2), color=YELLOW)                 # pos = (row, col), 1-based
        win.play(Write(t), run_time=0.5)
        hl = t.get_highlighted_cell((2, 1), color=TEAL, fill_opacity=0.4)
        win.play(FadeIn(hl), run_time=0.5)

        m = Matrix([["1", "2"], ["3", "4"]]).scale(0.8).move_to([0, -2, 0])
        box = SurroundingRectangle(m.get_entries()[2], color=RED, buff=0.1)
        win.play(Write(m), FadeIn(box), run_time=0.7)
        win.play(Wait(0.4))
        win.close()
```

notes: `add_highlighted_cell` / `get_cell` / `get_highlighted_cell` take `pos = (row, col)` **1-based** (`(1, 1)` = top-left); repeated calls on one cell stack new blocks (no replacement). The highlight is a child of the table, so it follows `scale`/`shift`/`set_row_colors`. The cell renderer decides what a cell may hold (`Table`→`Paragraph`, `MathTable`→`MathTex`, numeric tables→`Integer`/`DecimalNumber`). `font_size` is **not** a `Table`/`Matrix` parameter — pass `element_to_mobject_config={"font_size": ...}`. `Matrix` has no highlight API: index `get_entries()` and wrap the entry in a `SurroundingRectangle` (or use `get_cell` on a `Table`). `t.create()` returns an `AnimationGroup` for a staged entrance; do not `self.add` the table before playing it.

## text reveal / typewriter / number counting

use: letter-by-letter reveal, a cursor typewriter, and an animated counter.

```python
from real_time_manim import (Scene, Text, Rectangle, DecimalNumber,
                             AddTextLetterByLetter, ChangeDecimalToValue,
                             PURPLE, GREY_A, BLUE, GREEN, UP, DOWN, LEFT)
from real_time_manim.vulkan_bind import MLWindow, TypeWithCursor, Blink, Wait

class TextDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        t = Text("Typing...", font_size=50, color=BLUE).shift(UP)
        win.play(AddTextLetterByLetter(t, time_per_char=0.15), run_time=1.6)

        body = Text("Inserting", color=PURPLE).scale(1.2).to_edge(LEFT)
        cursor = Rectangle(color=GREY_A, fill_color=GREY_A, fill_opacity=1,
                           height=1.1, width=0.5).move_to(body[0])
        win.play(TypeWithCursor(body, cursor))
        win.play(Blink(cursor, blinks=2))

        n = DecimalNumber(0, num_decimal_places=1, color=GREEN).shift(DOWN)
        self.add(n)
        win.play(ChangeDecimalToValue(n, 10, run_time=2.0))
        win.play(Wait(0.4))
        win.close()
```

notes: `AddTextLetterByLetter` / `RemoveTextLetterByLetter` support `Text` **only** (not `MathTex`); `run_time=None` → `max(1/fps, time_per_char) * len(text)`. `RemoveTextLetterByLetter` defaults `introducer=False` → `self.add(text)` first. `TypeWithCursor` / `UntypeWithCursor` require an explicit cursor mobject; `Blink` does not introduce its object either (`self.add` first). `ChangeDecimalToValue` / `ChangingDecimal` are **one-shot** and require a `DecimalNumber`; for long-term following use `n.add_updater(lambda d: d.set_value(tracker.get_value()))` then `clear_updaters()`. `AddTextWordByWord` is broken upstream — use `LaggedStart(FadeIn)` per word instead.

## grouping + LaggedStart / Succession

use: one `play` for several animations — parallel, staggered, or strictly serial.

```python
from real_time_manim import (Scene, Dot, Square, VGroup, LaggedStart,
                             RED, YELLOW, GREEN, BLUE, PURPLE, UP, DOWN, LEFT, RIGHT)
from real_time_manim.vulkan_bind import MLWindow, Succession, FadeIn, Wait

class ComposeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        cols = [RED, YELLOW, GREEN, BLUE, PURPLE]
        dots = VGroup(*[Dot(radius=0.18, color=c).shift(LEFT * 4.4 + RIGHT * 2.2 * i + DOWN * 1.8)
                        for i, c in enumerate(cols)])
        win.play(LaggedStart(*[FadeIn(d, shift=DOWN) for d in dots],
                             lag_ratio=0.3, run_time=1.6))

        sq1 = Square(side_length=1.1, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 3.6 + UP * 1.6)
        sq2 = Square(side_length=1.1, color=GREEN).set_fill(GREEN, 0.5).shift(UP * 1.6)
        win.play(FadeIn(VGroup(sq1, sq2)), run_time=0.4)
        win.play(Succession(sq1.animate(run_time=1.0).move_to(sq2.get_center()),
                            Wait(0.6),
                            sq2.animate(run_time=0.8).set_color(RED)))
        win.play(Wait(0.5))
        win.close()
```

notes: `AnimationGroup(lag_ratio=0)` = fully parallel; `LaggedStart(lag_ratio=0.05)` = light stagger; `Succession(lag_ratio=1)` = one sub-animation at a time. `lag_ratio` is "how far the previous has played when the next starts", **not** a seconds gap (`start[i+1] = start[i] + run_time[i] * lag_ratio`). `run_time` on the group stretches the whole timeline; a group-level `rate_func` applies to the whole timeline, not per sub-animation. `Wait` can be a `Succession` child. `LaggedStart` / `LaggedStartMap` come from bundled ManimCE (top-level import) but render through the RTM timeline; `AnimationGroup`/`Succession` are RTM-own. One `play` = parallel; different durations → separate `play` calls.

## boolean op + fill styling

use: union / difference / intersection / XOR, styled via `**kwargs` + fill/stroke.

```python
from real_time_manim import (Scene, Union, Difference, Exclusion,
                             Circle, Square, GOLD, GREEN, RED, BLUE, PURPLE, TEAL,
                             UP, DOWN, LEFT, RIGHT)
from real_time_manim.vulkan_bind import MLWindow, FadeIn, Wait

class BoolDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)
        win.scene = self
        a = Circle(radius=0.9, color=BLUE).shift(LEFT * 0.55 + UP * 1.2)
        b = Square(side_length=1.5, color=RED).shift(RIGHT * 0.55 + UP * 1.2)
        merged = Union(a, b, color=GOLD, stroke_width=6).set_fill(GOLD, 0.85)
        win.play(FadeIn(merged), run_time=0.6)

        ring = Difference(Circle(radius=0.95, color=RED),
                          Circle(radius=0.5, color=RED), color=RED)
        win.play(FadeIn(ring.set_fill(RED, 0.7).shift(DOWN * 2)), run_time=0.6)

        xor = Exclusion(Circle(radius=0.85, color=PURPLE).shift(LEFT * 2.0),
                        Circle(radius=0.85, color=TEAL).shift(LEFT * 1.0), color=GREEN)
        win.play(FadeIn(xor), run_time=0.6)
        win.play(Wait(0.4))
        win.close()
```

notes: all four return a **new** `VMobject` (inputs unchanged). Inputs must be closed / fillable (`Circle`/`Square`/`Polygon`, not `Line`). Style the result with `**kwargs` (`color=`, `stroke_width=`) plus `VMobject` methods: `.set_fill(color, opacity)`, `.set_stroke(color, width, opacity)`, `.set_opacity(x)`, `.set_style(...)`. `Difference(subject, clip)` is directional — swap the args to flip the result; a ring appears when `clip` sits fully inside `subject`. Disjoint `Intersection` returns an empty (point-less) `VMobject` — that is a correct result, not a render failure. `Union` keeps a single merged contour; `Exclusion` is its complement (XOR). `Cutout(main, *holes)` is the cheaper alternative for a hollow shape.
