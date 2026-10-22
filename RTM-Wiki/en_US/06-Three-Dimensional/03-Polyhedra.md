# Polyhedra: the Polyhedron family and convex hulls

All polyhedra subclass `Polyhedron` (`VGroup`): internally `.faces` are the face polygons, plus a `.graph` whose vertices are `Dot3D`; the two are linked by an updater — drag `polyhedron.graph[v]` and the whole solid deforms with it.

This page covers the custom polyhedron `Polyhedron`, the four Platonic solids `Tetrahedron` / `Octahedron` / `Icosahedron` / `Dodecahedron`, and the automatic convex hull `ConvexHull3D`.

## Polyhedron

```python
Polyhedron(vertex_coords: Point3DLike_Array, faces_list: list[list[int]], faces_config: dict[str, str | int | float | bool] = {}, graph_config: dict[str, Any] = {})
```

A convex polyhedron defined by a "vertex-coordinate table + face-index table" (the idea behind OFF files): each face's vertices are closed automatically from first to last in list order.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vertex_coords` | `Point3DLike_Array` | required | list of vertex coordinates; the index is the vertex number |
| `faces_list` | `list[list[int]]` | required | which vertex indices make up each face |
| `faces_config` | `dict` | `{}` | construction params for the face `Polygon`s; `{"fill_opacity": 0.5, "shade_in_3d": True}` is injected by default |
| `graph_config` | `dict` | `{}` | construction params for the vertex `Graph`; `{"vertex_type": Dot3D, "edge_config": {"stroke_opacity": 0}}` is injected by default |

> **Returns**: none (constructs an instance). You can access `.faces` (a `VGroup` of faces) and `.graph` (a `Graph`) directly, plus `.layout` and `.edges`.

#### Sample: `Polyhedron` variations

A hand-written 5-vertex square pyramid (4 side faces + 1 base); the 3rd side face is colored yellow and the apex red, then `graph[4].animate` drags the apex — the updater carries the whole solid's deformation.

```python
from real_time_manim import ThreeDScene, Polyhedron, Text, \
    BLUE, GREY_B, RED, YELLOW, UP, DOWN, LEFT, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class PolyhedronDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # safety wiring: animate is played directly by win.play (only scene methods like move_camera really call self.play)
        title = Text("03-polyhedron", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        pyramid = Polyhedron(
            vertex_coords=[[1, 1, 0], [1, -1, 0], [-1, -1, 0], [-1, 1, 0], [0, 0, 2]],   # 4 base vertices + 1 apex
            faces_list=[[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4], [0, 1, 2, 3]],   # 4 side faces + 1 base
            faces_config={"fill_opacity": 0.6, "fill_color": BLUE},   # face config: translucent blue
        )
        pyramid.shift(LEFT * 2)   # shift left as a whole to leave room for the deformation
        pyramid.faces[2].set_color(YELLOW)   # recolor the 3rd face (a side face)
        pyramid.graph[4].set_color(RED)   # color the apex vertex
        print("faces:", len(pyramid.faces), "vertices:", len(pyramid.graph))   # confirm the structure on the console
        tag = Text("faces[2] / graph[4]", font_size=24, color=GREY_B).next_to(pyramid, DOWN)
        self.add(pyramid, tag)   # add the pyramid and the label to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the colored face and vertex
        win.play(pyramid.graph[4].animate.shift(DOWN + RIGHT * 0.5), run_time=1.0)   # drag the apex: the updater deforms the whole solid
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: it first builds a translucent blue square pyramid from the vertex and face tables and shifts it left to leave room for the deformation; it colors `faces[2]` yellow and `graph[4]` (the apex) red and prints the face/vertex counts to confirm the structure. After the oblique view pauses 0.8s, `graph[4].animate.shift(...)` drags the apex down-right for 1s — because the faces follow the vertices via the updater, the whole pyramid slumps in real time into a skew cone.

<video src="assets/RTM output/03-Polyhedra-polyhedron.mp4" controls width="560"></video>

> Note:
>
> - **Tested 2026-10-17**: a `.animate` animation such as `graph[4].animate.shift(...)` is built by `_AnimationBuilder` and played directly with `win.play(builder)`; it does **not** call back into `self.play` — the `self.play = win.play` on the first line is safety wiring (what really calls `self.play` is a scene method like `move_camera`, which this sample does not use).
> - The indices in `faces_list` refer to the order of `vertex_coords`; get them wrong and you get self-intersecting broken faces.
> - `fill_color` goes through `faces_config` (a `Polygon` parameter), not the `set_color` pitfall of a Surface.

## Tetrahedron / Octahedron / Icosahedron / Dodecahedron

```python
Tetrahedron(edge_length: float = 1, **kwargs)
Octahedron(edge_length: float = 1, **kwargs)
Icosahedron(edge_length: float = 1, **kwargs)
Dodecahedron(edge_length: float = 1, **kwargs)
```

The four Platonic solids (4 / 8 / 20 / 12 faces), all `Polyhedron` presets; they likewise support `.graph` / `.faces` access and vertex deformation.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `edge_length` | `float` | `1` | edge length |
| `**kwargs` | `Any` | — | forwarded to `Polyhedron` (`faces_config`, `graph_config`, …) |

#### Sample: the four Platonic solids

Tetrahedron / octahedron / icosahedron / dodecahedron in a row, with one vertex of the octahedron colored red and one face yellow, orbiting 90° to show the four shapes.

```python
from real_time_manim import ThreeDScene, VGroup, Tetrahedron, Octahedron, \
    Icosahedron, Dodecahedron, Text, \
    GREY_B, RED, YELLOW, UP, DOWN, RIGHT, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class PlatonicDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("03-platonic", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        solids = VGroup(
            Tetrahedron(edge_length=1),      # 4-face tetrahedron
            Octahedron(edge_length=1),       # 8-face octahedron
            Icosahedron(edge_length=0.9),    # 20-face icosahedron
            Dodecahedron(edge_length=0.7),   # 12-face dodecahedron
        ).arrange(RIGHT, buff=1.2)   # arrange left to right in a row
        solids.to_edge(DOWN, buff=1.4)   # lower it a bit to leave room for the title
        octa = solids[1]   # take the octahedron to demo attribute access
        octa.graph[0].set_color(RED)   # color one vertex (graph is the vertex Graph)
        octa.faces[2].set_color(YELLOW)   # color one face (faces is the face VGroup)
        tag = Text("tetra / octa / icosa / dodeca", font_size=24, color=GREY_B).next_to(solids, DOWN)
        self.add(solids, tag)   # add the four solids and the label to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-30 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the four solids
        self.move_camera(theta=-120 * DEGREES, run_time=1.4)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: it lays the four Platonic solids in a row along the bottom of the frame with decreasing edge length and adds a ground label; then it takes the second (the octahedron) to demo structure access — `graph[0]` is colored red and `faces[2]` yellow. After the oblique view pauses 0.8s it orbits 90°, showing the icosahedron's near-spherical form and the shading shift of the dodecahedron's large pentagonal faces as it turns.

<video src="assets/RTM output/03-Polyhedra-platonic.mp4" controls width="560"></video>

> Note: at equal `edge_length` the four solids differ a lot in visual size (different vertex counts), so the sample decreases it to keep them balanced. `graph` is a `Graph` and `faces` is a `VGroup`, accessed by integer index; vertices default to `Dot3D` and edges have no stroke by default (`stroke_opacity: 0`), so coloring only shows on points and faces.

## ConvexHull3D

```python
ConvexHull3D(*points: Point3D, tolerance: float = 1e-5, **kwargs)
```

Given a set of 3D points, automatically computes the convex hull as a `Polyhedron` (vertices + faces + edges all worked out), for visualising the "shape enclosed by scattered points".

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*points` | `Point3D` | required | the points that take part in the hull (positional args, not a list) |
| `tolerance` | `float` | `1e-5` | quickhull numeric tolerance |
| `**kwargs` | `Any` | — | forwarded to `Polyhedron` (`faces_config`, `graph_config`, …) |

#### Sample: `ConvexHull3D` computes a convex hull

6 scattered points (marked with small red spheres), automatically enclosed in a translucent green convex hull, orbiting 90° to show the envelope.

```python
from real_time_manim import ThreeDScene, ConvexHull3D, VGroup, Dot3D, Text, \
    GREEN, GREY_B, RED, YELLOW, UP, DOWN, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class HullDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        title = Text("03-hull", font_size=34, color=YELLOW).to_edge(UP)   # sample title
        self.add_fixed_in_frame_mobjects(title)   # pin the title to the screen
        pts = [[1.9, 0.4, -1.5], [-0.9, 1.2, 0.6], [0.4, 0.4, -1.8],   # 6 3D points
               [-1.5, -0.8, -0.5], [0.8, -1.4, 0.9], [-0.2, 0.1, 2.0]]
        hull = ConvexHull3D(*pts, faces_config={"fill_opacity": 0.4, "fill_color": GREEN})   # automatically compute the convex hull as a polyhedron
        dots = VGroup(*[Dot3D(p, radius=0.08, color=RED) for p in pts])   # mark the original points with small red spheres
        tag = Text("ConvexHull3D(*points)", font_size=24, color=GREY_B).to_edge(DOWN)
        self.add(hull, dots, tag)   # add the hull, points and label to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the hull envelope
        self.move_camera(theta=-135 * DEGREES, run_time=1.4)   # animate a 90° orbit
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: it scatters 6 points in space and marks them with small red spheres; `ConvexHull3D(*pts)` computes in one step the hull enclosing all of them (translucent green, with the interior red points visible), plus a ground label. After the oblique view pauses 0.8s it orbits 90°, and from the side you can see the hull "hug" the outermost points and bulge out, while points inside are wrapped behind the translucent faces.

<video src="assets/RTM output/03-Polyhedra-hull.mp4" controls width="560"></video>

> Note:
>
> - `ConvexHull3D` takes positional arguments (`ConvexHull3D(*pts)`); do not pass a single list.
> - With fewer than 4 points, or all points coplanar, no solid hull can be computed and it degenerates; leave `tolerance` at its default unless the point set is numerically ill-conditioned.

---

See also: [Surfaces](02-Surfaces.md) · [3D Utilities](04-3D-Utilities.md)
