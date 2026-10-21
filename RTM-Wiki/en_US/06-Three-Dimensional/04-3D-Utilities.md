# 3D utility functions (three_d_utils)

`mobject/three_d/three_d_utils.py` is a set of module-level utility functions that extract a `VMobject`'s start/end corner coordinates, its gradient start/end points, and the unit normal at any anchor; all are importable directly via `from manim import ...`.

These functions are only meaningful for a **single 3D face** (one `VMobject`): passing a `VGroup` shell such as `Cube` or `Sphere` degenerates (corners fall back to `ORIGIN`, normals to `UP`), so take a sub-face like `cube[i]` first and then query it.

## Start/end corners and gradient start/end points

```python
get_3d_vmob_start_corner(vmob: VMobject) -> Point3D
get_3d_vmob_end_corner(vmob: VMobject) -> Point3D
get_3d_vmob_gradient_start_and_end_points(vmob: VMobject) -> tuple[Point3D, Point3D]
get_3d_vmob_end_corner_index(vmob: VMobject) -> int
```

Four corner/endpoint query functions: the coordinates of the start corner (`points` index always 0) and the end corner (index `((len(points)-1)//6)*3`), that index itself, and the gradient start/end points (which equal the start/end corners, for `set_stroke`/`set_fill` gradients).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vmob` | `VMobject` | required | the 3D vector face to query (a single face, not a `VGroup` shell) |

> **Returns**: the coordinate-returning functions return `Point3D` (`np.ndarray`); `get_3d_vmob_end_corner_index` returns an `int` index; for an empty `vmob` the corner functions return `ORIGIN`. There is also `get_3d_vmob_start_corner_index(vmob) -> Literal[0]`, which always returns 0 — see "Not demonstrated" at the end of the page.

#### Sample: start/end corners and normal markers

Takes one face of a translucent cube, marks its start corner (red sphere) and end corner (yellow sphere), and prints the gradient endpoints and start/end normals to the console.

```python
from real_time_manim import ThreeDScene, Cube, Dot3D, Arrow3D, Text, \
    GREEN, GREY_B, RED, YELLOW, UP, DOWN, DEGREES, \
    get_3d_vmob_start_corner, get_3d_vmob_end_corner, \
    get_3d_vmob_end_corner_index, \
    get_3d_vmob_gradient_start_and_end_points, \
    get_3d_vmob_start_corner_unit_normal, get_3d_vmob_end_corner_unit_normal
from real_time_manim.vulkan_bind import MLWindow, Wait

class CornersDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("04-corners", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        cube = Cube(side_length=2, fill_opacity=0.35, stroke_width=3)   # translucent cube
        face = cube[0]   # take one face (a single VMobject; these functions are only meaningful for it)
        p0 = get_3d_vmob_start_corner(face)   # start-corner coordinates (index is always 0)
        p1 = get_3d_vmob_end_corner(face)   # end-corner coordinates
        g0, g1 = get_3d_vmob_gradient_start_and_end_points(face)   # gradient start/end points = start/end corners
        n0 = get_3d_vmob_start_corner_unit_normal(face)   # unit normal at the start corner
        n1 = get_3d_vmob_end_corner_unit_normal(face)   # unit normal at the end corner
        print("start:", p0, " end idx:", get_3d_vmob_end_corner_index(face), "->", p1)   # print the query results to the console
        print("gradient:", g0, g1)   # the gradient start/end points are just the start/end corners
        print("normals:", n0, n1)   # unit normals at the start/end corners
        d0 = Dot3D(p0, radius=0.09, color=RED)   # red sphere marks the start corner
        d1 = Dot3D(p1, radius=0.09, color=YELLOW)   # yellow sphere marks the end corner
        a0 = Arrow3D(p0, p0 + 0.8 * n0, color=GREEN, thickness=0.05)   # normal arrow at the start corner
        a1 = Arrow3D(p1, p1 + 0.8 * n1, color=GREEN, thickness=0.05)   # normal arrow at the end corner
        tag = Text("corners(red/yellow) normals(green)", font_size=24, color=GREY_B).to_edge(DOWN)
        self.add(cube, d0, d1, a0, a1, tag)   # add the cube, corner markers and normal arrows to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the markers
        self.move_camera(theta=-135 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: it builds a translucent cube, takes its first face with `cube[0]` (a single `VMobject`), looks up the start corner `p0`, end corner `p1`, the gradient start/end points and the start/end unit normals, and prints them to the console.

On screen a red sphere marks the start corner and a yellow one the end corner, and a green arrow is drawn from each corner along its normal. Orbiting 90° shows the two normal arrows always pointing perpendicular out of the face — the intuitive meaning of a "face-local normal".

<video src="assets/RTM output/04-3D-Utilities-corners.mp4" controls width="560"></video>

> Note:
>
> - In the console output `end idx: 6` — the end-corner index is computed against the `points` array (`((len-1)//6)*3`), not a face/vertex number, so don't use it as `faces[6]`.
> - The two coordinates returned by the gradient start/end points are exactly the start/end corners (`g0 == p0`); it is a convenience entry prepared for interfaces like "gradient shading along the start→end direction".

## Unit-normal queries

```python
get_3d_vmob_unit_normal(vmob: VMobject, point_index: int) -> Vector3D
get_3d_vmob_start_corner_unit_normal(vmob: VMobject) -> Vector3D
get_3d_vmob_end_corner_unit_normal(vmob: VMobject) -> Vector3D
```

Looks up the unit normal at any position by anchor index; the two start/end wrappers are equivalent to always passing 0 / the end-corner index. The normal comes from the face's 3D shading normal at that point, and falls back to `UP` when `vmob` is empty.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vmob` | `VMobject` | required | the single 3D face to query |
| `point_index` | `int` | required (only `get_3d_vmob_unit_normal`) | the index of the anchor in the `points` array |

> **Returns**: `Vector3D` (a unit direction vector, `np.ndarray`).

#### Sample: `get_3d_vmob_unit_normal` at an anchor index

Takes the start / middle / end anchors of a cube's side face and draws a green normal arrow perpendicular to the face at each.

```python
from real_time_manim import ThreeDScene, Cube, VGroup, Arrow3D, Text, \
    GREEN, GREY_B, YELLOW, UP, DOWN, DEGREES, \
    get_3d_vmob_end_corner_index, get_3d_vmob_unit_normal
from real_time_manim.vulkan_bind import MLWindow, Wait

class FaceNormalsDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("04-face_normals", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        face = Cube(side_length=2)[1]   # use a different face (a side) to sample several anchors
        end_idx = get_3d_vmob_end_corner_index(face)   # index of the end corner in points
        idxs = [0, end_idx // 2, end_idx]   # the three anchors: start / middle / end
        arrows = VGroup()
        for i in idxs:   # draw a normal arrow at each anchor
            p = face.points[i]   # anchor coordinates
            n = get_3d_vmob_unit_normal(face, i)   # look up the unit normal by anchor index
            arrows.add(Arrow3D(p, p + 0.7 * n, color=GREEN, thickness=0.05))
        tag = Text("normals at idx 0 / %d / %d" % (end_idx // 2, end_idx),   # put the three indices into the label
                   font_size=24, color=GREY_B).to_edge(DOWN)
        self.add(face, arrows, tag)   # add this face and the three arrows to the scene (no need for the whole cube)
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the three normal arrows
        self.move_camera(theta=-120 * DEGREES, run_time=1.2)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: it takes only one side face of the cube (without the whole cube), uses `get_3d_vmob_end_corner_index` to compute the end-corner index, then takes the start / middle / end anchors, looks up the unit normal at each and draws a green arrow, with the three indices printed in the label. The three arrows are all perpendicular to the same plane and point the same way; orbiting 90° to the side confirms they really are "attached to the face" and turn with it.

<video src="assets/RTM output/04-3D-Utilities-face_normals.mp4" controls width="560"></video>

> Note:
>
> - The index for `face.points[i]` and the `point_index` of `get_3d_vmob_unit_normal` are the same `points`-array index; out-of-range or odd indices (Bézier control points) may give a geometrically meaningless normal.
> - On one planar face the start/middle/end normals are nearly identical (a plane's normal is constant); to see the normal vary you need a curved surface face.

Not demonstrated:

- `get_3d_vmob_start_corner_index(vmob) -> Literal[0]` — it always returns `0`, with no parameter to vary and no frame that changes; even on the console it is just a single 0, so a video is not worth it.
- This group of functions is pure computation (input a `VMobject`, return an `ndarray`); the red/yellow spheres and green arrows in the frame are the drawn result of their return values — the functions themselves take no part in rendering.
- Calling them directly on a `VGroup` shell such as a whole `Cube` or `Sphere` degenerates: a `VGroup` has no `points` of its own, so corners fall back to `ORIGIN` and normals to `UP` — you must take a single face like `cube[i]` first, as the samples do.

---

See also: [Polyhedra](03-Polyhedra.md) · [Surfaces](02-Surfaces.md)
