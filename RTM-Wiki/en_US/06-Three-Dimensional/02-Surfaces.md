# 3D Surfaces: Surface, Sphere, Torus

`Surface` is the general entry point for parametric surfaces; `Sphere` / `Torus` (and [Cone / Cylinder](01b-Basic-3D-Objects-Advanced.md)) are all its subclasses. Recoloring every `Surface` subclass on this page requires calling **`.set_color(...)` after construction** — the `color=` constructor parameter is swallowed upstream and has no effect (see the note in each section).

## Surface

```python
Surface(func: Callable[[float, float], np.ndarray], u_range: tuple[float, float] = (0, 1), v_range: tuple[float, float] = (0, 1), resolution: int | Sequence[int] = 32, surface_piece_config: dict = {}, fill_color: ParsableManimColor = BLUE_D, fill_opacity: float = 1.0, checkerboard_colors: Iterable[ParsableManimColor] | Literal[False] = [BLUE_D, BLUE_E], stroke_color: ParsableManimColor = LIGHT_GREY, stroke_width: float = 0.5, should_make_jagged: bool = False, pre_function_handle_to_anchor_scale_factor: float = 0.00001, **kwargs)
```

Define a surface with `func(u, v) -> (x, y, z)`; it is cut into `resolution` checkerboard cells. With axes you usually write `lambda u, v: axes.c2p(...)`.

Two methods are commonly used for coloring: `set_fill_by_checkerboard(*colors, opacity=None)` cycles colors by `(u_index + v_index) % n`, and `set_fill_by_value` applies a gradient by coordinate value.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `func` | `Callable[[float,float], np.ndarray]` | required | parametric equation returning a 3D coordinate |
| `u_range` | `tuple[float,float]` | `(0, 1)` | interval for u |
| `v_range` | `tuple[float,float]` | `(0, 1)` | interval for v |
| `resolution` | `int \| Sequence[int]` | `32` | int sets both u and v; passing `(u_res, v_res)` sets them separately; **not recommended** to set large — the face count grows as `u_res × v_res` and so does render time |
| `surface_piece_config` | `dict` | `{}` | extra config for each face |
| `fill_color` | `ParsableManimColor` | `BLUE_D` | face fill color (overridden by `checkerboard_colors`; to use it, turn the checkerboard off first) |
| `fill_opacity` | `float` | `1.0` | opacity |
| `checkerboard_colors` | `Iterable[...] \| False` | `[BLUE_D, BLUE_E]` | alternating checkerboard colors; pass `False` to disable the checkerboard |
| `stroke_color` | `ParsableManimColor` | `LIGHT_GREY` | stroke color of each face |
| `stroke_width` | `float` | `0.5` | stroke width |
| `should_make_jagged` | `bool` | `False` | switch Bézier anchors from smooth to polyline (jagged look) |
| `pre_function_handle_to_anchor_scale_factor` | `float` | `0.00001` | sample-anchor scale factor (leave alone) |
| `**kwargs` | `Any` | — | forwarded to `VGroup`; `color=` is swallowed here (see the note) |

#### Sample: `Surface` variations

A spiral-ramp parametric surface, blue checkerboard by default; midway `set_fill_by_checkerboard` recolors it to a green/yellow scheme in place, then it orbits 90°.

```python
import numpy as np

from real_time_manim import ThreeDScene, Surface, Text, \
    GREEN, GREY_B, YELLOW, TAU, UP, DOWN, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class SurfaceDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("02-surface", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        surf = Surface(lambda u, v: [v * np.cos(u), v * np.sin(u), u * 0.5],   # parametric equation of a spiral ramp
                       u_range=(0, TAU), v_range=(0.3, 1.8),   # u makes a full turn, v spans the inner/outer radius
                       resolution=(16, 8))   # low resolution: keeps render time down while the faces stay readable
        self.add(surf)   # add the surface to the scene
        self.set_camera_orientation(phi=60 * DEGREES, theta=-60 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the default blue checkerboard
        surf.set_fill_by_checkerboard([GREEN, YELLOW], opacity=0.85)   # method: recolor the checkerboard in place
        win.play(Wait(0.6))   # pause 0.6s to see the new colors
        self.move_camera(theta=-150 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: it defines a spiral ramp with `lambda u, v` — `u` makes a full turn setting the azimuth while the height rises as `u * 0.5`, and `v` sets the "spoke" length from inner radius 0.3 to outer radius 1.8. With `resolution=(16, 8)` it is cut into low-resolution cells, so the cells read clearly and the render stays fast.

It pauses 0.8s to show the default blue checkerboard, then `set_fill_by_checkerboard([GREEN, YELLOW], opacity=0.85)` recolors it to a green/yellow alternating scheme in place, and finally orbits 90° to show the ramp's 3D shape.

<video src="assets/RTM output/02-Surfaces-surface.mp4" controls width="560"></video>

> Note:
>
> - `resolution` is the first lever on render time: face count = `u_res × v_res`, each cell an independent polygon. An illustrative surface at `(16, 8)` (128 cells) is enough to read the structure; the default `32` (1024 cells) is noticeably slower.
> - **Do not** rely on `Surface(..., color=...)` for recoloring: `Mobject.__init__` applies `color=` first and the checkerboard faces are generated after, so the color is overwritten (upstream behaviour, identical in both engines); recolor with `set_fill_by_checkerboard(...)` or `.set_fill(...)`.

### set_fill_by_value parameters

Colors the surface by coordinate value (a gradient); not demoed in the samples (it needs a `ThreeDAxes` to invert back to data coordinates — advanced usage):

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `axes` | `ThreeDAxes` | required | used to map point coordinates back to data coordinates |
| `colorscale` | `Iterable[color] \| Iterable[(color, pivot value)] \| None` | `None` | color scheme; the tuple form lets you customize the pivots |
| `axis` | `int` | `2` | which axis's value colors the surface: 0=x, 1=y, 2=z |
| `colors` | (`**kwargs` alias) | - | equivalent to `colorscale`; you may pass only one of the two |

## Sphere

```python
Sphere(center: Point3DLike = ORIGIN, radius: float = 1, resolution: int | Sequence[int] | None = None, u_range: tuple[float, float] = (0, TAU), v_range: tuple[float, float] = (0, PI), **kwargs)
```

A standard sphere; change `u_range` (azimuth) / `v_range` (polar angle) to cut out a spherical cap, hemisphere, etc.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `center` | `Point3DLike` | `ORIGIN` | center |
| `radius` | `float` | `1` | radius |
| `resolution` | `int \| Sequence[int] \| None` | `None` → cairo `(24, 12)` | sample resolution; same as `Surface`, **not recommended** to set large |
| `u_range` | `tuple[float,float]` | `(0, TAU)` | azimuth range |
| `v_range` | `tuple[float,float]` | `(0, PI)` | polar-angle range (0 = north-pole direction); `v_range=(0, PI/2)` cuts out the upper hemisphere |
| `**kwargs` | `Any` | — | forwarded to `Surface`; `color=` has no effect, recolor with `.set_color(...)` (`Dot3D` does exactly this internally) |

#### Sample: `Sphere` variations

A full sphere vs the upper hemisphere (spherical cap) cut by `v_range=(0, PI/2)`, orbiting 90° to show the cut boundary.

```python
from real_time_manim import ThreeDScene, Sphere, Text, \
    GREY_B, RED, YELLOW, PI, UP, DOWN, LEFT, RIGHT, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class SphereDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("02-sphere", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        full = Sphere(radius=1, resolution=(24, 12))   # full sphere: u a full turn, v from north to south pole
        full.shift(LEFT * 2.5)   # place it on the left
        half = Sphere(radius=1, resolution=(24, 12), v_range=(0, PI / 2))   # v_range cuts out the upper hemisphere
        half.set_color(RED)   # recolor: the "color=" parameter of a Surface subclass has no effect; call set_color after construction
        half.shift(RIGHT * 2.5)   # place it on the right
        tag1 = Text("v_range=(0,PI)", font_size=24, color=GREY_B).next_to(full, DOWN)   # bottom-left label
        tag2 = Text("v_range=(0,PI/2)", font_size=24, color=GREY_B).next_to(half, DOWN)   # bottom-right label
        self.add(full, half, tag1, tag2)   # add the two spheres and labels to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the spherical-cap shape
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: on the left a full sphere (`v_range` defaults to `(0, PI)`, north pole to south pole in one sweep); the right one narrows `v_range` to `(0, PI/2)` — the polar angle only reaches the equator, producing the red upper hemisphere (a spherical cap) whose open bottom faintly shows the interior. As it orbits 90° the cut boundary (the equator circle) is clearly visible.

<video src="assets/RTM output/02-Surfaces-sphere.mp4" controls width="560"></video>

> Note: `v_range`'s 0 is the **north-pole** direction; `(0, PI/2)` is the upper hemisphere and `(PI/2, PI)` the lower one. `Sphere(..., color=RED)` has no effect (`color=` is swallowed upstream, identical in both engines) — call `.set_color(RED)` after construction, which is exactly what `Dot3D` does internally.

## Torus

```python
Torus(major_radius: float = 3, minor_radius: float = 1, u_range: tuple[float, float] = (0, TAU), v_range: tuple[float, float] = (0, TAU), resolution: int | tuple[int, int] | None = None, **kwargs)
```

A ring/torus shaped like a lifebuoy; `major_radius` is the ring radius and `minor_radius` the tube radius.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `major_radius` | `float` | `3` | major radius (ring radius) |
| `minor_radius` | `float` | `1` | minor radius (tube radius) |
| `u_range` | `tuple[float,float]` | `(0, TAU)` | angle range around the ring (trim a segment to get a "bent tube") |
| `v_range` | `tuple[float,float]` | `(0, TAU)` | angle range around the tube (cut in half to get a half-tube) |
| `resolution` | `int \| tuple[int,int] \| None` | `None` → cairo `(24, 24)` | sample resolution; same as `Surface`, **not recommended** to set large |
| `**kwargs` | `Any` | — | forwarded to `Surface`; `color=` has no effect, recolor with `.set_color(...)` |

#### Sample: `Torus` variations

A full ring vs the half-tube cut by `v_range=(0, PI)` (sliced in half across the tube cross-section), orbiting 90° to show the cross-section.

```python
from real_time_manim import ThreeDScene, Torus, Text, \
    GREEN, GREY_B, YELLOW, PI, UP, DOWN, LEFT, RIGHT, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class TorusDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("02-torus", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        full = Torus(major_radius=1.6, minor_radius=0.5)   # default full ring: ring radius 1.6, tube radius 0.5
        full.shift(LEFT * 2.5)   # place it on the left
        half = Torus(major_radius=1.6, minor_radius=0.5, v_range=(0, PI))   # v_range cuts out half the tube
        half.set_color(GREEN)   # recolor: the "color=" parameter of a Surface subclass has no effect; call set_color after construction
        half.shift(RIGHT * 2.5)   # place it on the right
        tag1 = Text("full ring", font_size=24, color=GREY_B).next_to(full, DOWN)   # bottom-left label
        tag2 = Text("v_range=(0,PI)", font_size=24, color=GREY_B).next_to(half, DOWN)   # bottom-right label
        self.add(full, half, tag1, tag2)   # add the two tori and labels to the scene
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the half-tube cross-section
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: on the left a shrunk full torus (ring radius 1.6, tube radius 0.5); the right one uses `v_range=(0, PI)` to halve the angle around the tube, opening the green tube along its longitudinal cross-section so the tube-wall section is visible. Orbiting 90° to the side makes the difference between the two shapes obvious.

<video src="assets/RTM output/02-Surfaces-torus.mp4" controls width="560"></video>

> Note:
>
> - For `Torus`, `u` runs around the ring and `v` around the tube: trimming `u_range` gives a "bent segment of tube", trimming `v_range` gives a "tube cut open" — don't swap them.
> - The default `major_radius=3` is wider than the frame; shrink it to your scene when you actually use it.
> - Recoloring is the same as `Sphere`: only `.set_color(...)` works.

## Depth mesh: `MeshBatch` (advanced)

`Surface` faces are painted in painter order by default. That order cannot resolve a surface crossing itself or a rim passing through a face. `MeshBatch` sends quads through the GPU depth buffer instead.

```python
import numpy as np

from real_time_manim import DEGREES, MeshBatch, ThreeDScene
from real_time_manim.vulkan_bind import MLWindow, Wait

class MeshDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # open an RTM window
        win.scene = self
        self.set_camera_orientation(phi=58 * DEGREES, theta=0)

        quads = np.array([
            [[-1.5, -1.5, -0.6], [1.5, -1.5, -0.6],
             [1.5, 1.5, -0.6], [-1.5, 1.5, -0.6]],
            [[-0.8, -0.8, 0.6], [0.8, -0.8, 0.6],
             [0.8, 0.8, 0.6], [-0.8, 0.8, 0.6]],
        ], dtype=float)                              # (Q, 4, 3), world coords
        colors = np.array([
            [[0.2, 0.4, 1.0, 1.0]] * 4,
            [[1.0, 0.5, 0.1, 1.0]] * 4,
        ], dtype=np.float32)                         # (Q, 4, 4), RGBA

        mesh = MeshBatch()
        mesh.append(quads, colors)
        win.set_mesh(mesh)                           # submitted every frame
        win.play(Wait(0.8))
        win.close()
```

The orange quad sits at `z = 0.6` and the blue one at `z = -0.6`; depth testing makes orange occlude blue. To use this with a `Surface`, put each face's four corners into `quads`.

### `MeshBatch`

| Member | Meaning |
| --- | --- |
| `MeshBatch()` | empty batch |
| `append(quads, colors)` | append quads; returns self |
| `quads` | `(Q, 4, 3)` float, four corners in world coordinates |
| `colors` | `(Q, 4, 4)` float, RGBA per corner in 0–1 |
| `build_vertices(viewport, width, height)` | called by the window each frame; projects to NDC + depth (rarely called by hand) |

Attach it to the window:

| Method | Meaning |
| --- | --- |
| `win.set_mesh(mesh)` | submit this frame's mesh; `None` is the same as `clear_mesh()` |
| `win.clear_mesh()` | detach the mesh and return to the painter |

### Limits

- Quads only; split triangles yourself or use the automatic `Surface` path.
- One batch holds at most `MAX_MESH_VERTS = 262144` vertices, about 43690 quads.
- `append` appends; `win.set_mesh` submits the current batch each frame and does not stack calls.
- The mesh is drawn first and 2D afterwards, so text, formulas and images always sit on top.
- Overlapping translucent quads remain an approximation; there is no per-pixel sort.
- Every camera move re-projects the batch on the CPU, which costs time on large meshes.

### Automatic depth (experimental)

Since RTM 2.0.3 an eligible `Surface` can use the depth buffer without writing `MeshBatch` by hand:

```powershell
$env:RTM_AUTO_DEPTH = "1"
```

Eligibility: a 3D camera, a top-level `Surface`, opaque faces, `shade_in_3d=False`, stroke colour equal to fill, and no other lit 3D geometry in the frame.

It fixes occlusion; it does not remove the Python cost of per-face `set_fill` / `set_stroke`. For many faces, update colours in one array write instead, or use `MeshBatch`.

---

See also: [Basic 3D Objects (1)](01-Basic-3D-Objects.md) · [Polyhedra](03-Polyhedra.md)
