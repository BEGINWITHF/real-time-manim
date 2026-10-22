# Vector and geometry utilities (1): space_ops

`utils/space_ops.py` provides geometry utilities for vector rotation, angles, normalization, centroids, complex-number interchange and more; all available via `from manim import ...`. RTM reuses the manim implementation directly, with bit-identical numpy computation.

The three samples on this page demonstrate rotating a vector about an axis, angle and centroid, and shoelace area with regular-polygon vertices; all have been rendered in RTM. The remaining functions are in the quick table in the second half of the page.

## Naming traps (read this first)

The source does **not** have the following names, which are common in other Manim forks/tutorials — don't call them directly:

| May appear in tutorials | Correct form in this version (0.21.0) |
| --- | --- |
| `rotation_between_vectors(v1, v2)` | combine it yourself: `rotation_matrix(angle_between_vectors(v1, v2), np.cross(v1, v2))` |
| `angle_between(v1, v2)` | **`angle_between_vectors(v1, v2)`** |
| `get_unit_vector(v)` | `normalize(v)` (`space_ops.normalize`); `Line.get_unit_vector()` is a 2D `Line` method |
| `complex_to_vec3(z)` | **`complex_to_R3(z)`** |

## `rotate_vector` — rotate a vector about an axis

```python
rotate_vector(vector: Vector3DLike, angle: float, axis: Vector3DLike = OUT) -> Vector3D
```

Rotates a vector by `angle` radians about `axis`, returning a new vector (the original is unchanged); the most common tool for "computing a new position by angle", e.g. `rotate_vector(RIGHT, TAU/8)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vector` | `Vector3DLike` | required | vector to rotate (2D auto-pads z=0; >3 dims raises `ValueError`) |
| `angle` | `float` | required | rotation angle (radians, CCW positive) |
| `axis` | `Vector3DLike` | `OUT` | rotation axis |

> **Returns**: `Vector3D` (`np.ndarray`).

#### Sample: the same vector rotated 45° and 90°

Starting from `RIGHT` a grey arrow is drawn; `rotate_vector(RIGHT, PI / 4)` gives a yellow 45° arrow and `rotate_vector(RIGHT, PI / 2)` a green 90° arrow (landing exactly on `UP`), with two arcs marking the rotated angles.

```python
from real_time_manim import Scene, Text, Vector, Arc, Dot, GREY_B, YELLOW, GREEN, \
    WHITE, UP, DOWN, RIGHT, ORIGIN, PI, rotate_vector, FadeIn, Write, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class RotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("04-rotate_vector", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        o = Dot(ORIGIN, radius=0.06, color=WHITE)   #coordinate origin
        v0 = Vector(2.4 * RIGHT, color=GREY_B)   #base vector: RIGHT itself
        l0 = Text("RIGHT", font_size=18, color=GREY_B).next_to(v0.get_end(), DOWN, buff=0.2)
        win.play(FadeIn(o), Create(v0), FadeIn(l0), run_time=0.7)   #draw the base arrow first

        v45 = Vector(2.4 * rotate_vector(RIGHT, PI / 4), color=YELLOW)   #rotate 45° CCW about the default axis OUT
        a45 = Arc(radius=1.2, start_angle=0, angle=PI / 4, arc_center=ORIGIN,
                  color=YELLOW, stroke_width=5)   #arc from 0 → 45°
        l45 = Text("rotate(PI/4)", font_size=17, color=YELLOW).move_to([1.3, 1.9, 0])   #45° label (placed outside the arc)
        win.play(Create(a45), Create(v45), FadeIn(l45), run_time=0.7)   #the result of rotating 45°

        v90 = Vector(2.4 * rotate_vector(RIGHT, PI / 2), color=GREEN)   #rotate 90°: RIGHT becomes exactly UP
        a90 = Arc(radius=1.7, start_angle=0, angle=PI / 2, arc_center=ORIGIN,
                  color=GREEN, stroke_width=4)   #arc from 0 → 90° (a bigger sweep)
        l90 = Text("rotate(PI/2)", font_size=17, color=GREEN).move_to([2.1, 0.8, 0])   #90° label
        win.play(Create(a90), Create(v90), FadeIn(l90), run_time=0.7)   #the result of rotating 90°
        note = Text("rotate_vector(v, angle, axis=OUT) returns a new vector",
                    font_size=18, color=YELLOW).to_edge(DOWN)   #bottom note: the original vector is unchanged
        win.play(FadeIn(note), run_time=0.35)   #note fades in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: the grey `RIGHT` arrow is the unrotated vector, yellow is the 45° result and green the 90° result (`RIGHT` rotated 90° becomes exactly `UP`, pointing straight up). The two arcs have different radii and don't overlap, making it clear that `angle` is measured CCW about the screen-normal `OUT` axis; after rotation the original `RIGHT` is untouched — the function returns a **new** vector.

<video src="assets/RTM output/04-Vector-and-Geometry-Utilities-rotate.mp4" controls width="560"></video>

> Note:
>
> - `angle` is **radians**, not degrees (`45°` is `PI / 4` or `45 * DEGREES`).
> - To rotate "about any axis", pass the third argument `axis`; in 3D you'll most often use `X_AXIS` / `Y_AXIS`.
> - For the matrix form, use `rotation_matrix(angle, axis)`.

## Angle, polar angle and center: `angle_between_vectors` / `angle_of_vector` / `center_of_mass` / `midpoint`

| Signature | Meaning |
| --- | --- |
| `angle_between_vectors(v1: np.ndarray, v2: np.ndarray) -> float` | angle between two vectors, **always in `[0, π]`** (arctan2 half-angle formula, numerically stable) |
| `angle_of_vector(vector) -> float` | polar angle of the vector projected onto the xy plane (`atan2`, `(-π, π]`); also accepts a `(2, n)` point set and returns a per-point angle array |
| `center_of_mass(points: PointNDLike_Array) -> PointND` | arithmetic mean of the points (equal-weight centroid) |
| `midpoint(point1, point2)` | midpoint of two points (sugar for `center_of_mass([p1, p2])`) |

#### Sample: angle between two vectors and the centroid of an irregular quadrilateral

On the right two red and blue vectors are drawn and `angle_between_vectors` measures the angle between them, marked with an arc (the value is shown next to it); on the lower left four points are joined in order into an irregular quadrilateral, `center_of_mass` drops a gold centroid dot, and the bottom edge's `midpoint` drops a green midpoint.

```python
import numpy as np
from real_time_manim import Scene, Text, VGroup, Dot, Vector, Arc, Polygon, RED, \
    BLUE, YELLOW, GREEN, GREY_B, GOLD, UP, DOWN, RIGHT, ORIGIN, \
    angle_between_vectors, angle_of_vector, center_of_mass, midpoint, \
    FadeIn, Write, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class AngleCentroidDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("04-angle_centroid", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        a = Vector([2.6, 0.9, 0], color=RED)   #vector 1
        b = Vector([1.1, 2.4, 0], color=BLUE)   #vector 2
        la = Text("v1", font_size=18, color=RED).next_to(a.get_end(), RIGHT, buff=0.15)
        lb = Text("v2", font_size=18, color=BLUE).next_to(b.get_end(), UP, buff=0.15)
        ang = angle_between_vectors(a.get_end(), b.get_end())   #angle between the two vectors, always in [0, PI]
        aa, ab = angle_of_vector(a.get_end()), angle_of_vector(b.get_end())   #their polar angles, used to place the arc
        arc = Arc(radius=1.15, start_angle=aa, angle=ab - aa, arc_center=ORIGIN,
                  color=YELLOW, stroke_width=6)   #arc between the two arrows
        lt = Text("%.3f rad" % ang, font_size=17, color=YELLOW).move_to([1.05, 0.45, 0])   #angle value
        win.play(Create(a), FadeIn(la), run_time=0.5)   #draw v1 first
        win.play(Create(b), FadeIn(lb), run_time=0.5)   #then draw v2
        win.play(Create(arc), FadeIn(lt), run_time=0.5)   #measure the angle

        pts = [np.array([-3.1, -1.0, 0]), np.array([-1.2, -2.0, 0]),   #four lower-left points (an irregular quadrilateral)
               np.array([-0.7, 0.5, 0]), np.array([-2.9, 1.3, 0])]
        quad = Polygon(*pts, color=GREY_B, stroke_width=3)   #join the points in order into a quadrilateral
        pdots = VGroup(*[Dot(p, radius=0.09, color=RED) for p in pts])   #four vertices
        com = center_of_mass(pts)   #centroid = arithmetic mean of the points
        star = Dot(com, radius=0.12, color=GOLD)   #centroid dot
        lc = Text("center_of_mass", font_size=16, color=GOLD).next_to(star, DOWN, buff=0.18)
        mid = midpoint(pts[0], pts[1])   #midpoint of the bottom edge
        mdot = Dot(mid, radius=0.09, color=GREEN)
        lm = Text("midpoint", font_size=15, color=GREEN).next_to(mdot, DOWN, buff=0.15)
        win.play(Create(quad), FadeIn(pdots), run_time=0.7)   #the irregular quadrilateral
        win.play(FadeIn(star), FadeIn(lc), run_time=0.4)   #centroid marker
        win.play(FadeIn(mdot), FadeIn(lm), run_time=0.4)   #midpoint marker
        note = Text("angle_between_vectors -> [0, PI]", font_size=18, color=YELLOW).to_edge(DOWN)
        win.play(FadeIn(note), run_time=0.35)   #bottom note fades in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: after the two vectors on the right are drawn, `angle_between_vectors` gives a radian value (`0.643 rad` on screen), and the arc's start and end angles are placed using `angle_of_vector` to measure each vector's polar angle — the angle can be at most `[0, π]`, so order does not matter. The four red points on the lower left join into an irregular quadrilateral; the gold `center_of_mass` lands at the "center of gravity" (the arithmetic mean of the four points) and the green `midpoint` sits exactly at the middle of the bottom edge — the centroid works for irregular shapes too.

<video src="assets/RTM output/04-Vector-and-Geometry-Utilities-angle_centroid.mp4" controls width="560"></video>

> Note:
>
> - These functions all take **numpy arrays** — for a mobject like `Vector`, call `.get_end()` first to get the coordinates.
> - `angle_of_vector` only looks at the xy plane (the z component is ignored); for a 3D angle always use `angle_between_vectors`.

## Polygons: `regular_vertices` / `shoelace` / `shoelace_direction`

| Signature | Meaning |
| --- | --- |
| `regular_vertices(n: int, *, radius: float = 1, start_angle: float \| None = None) -> tuple` | generate `n` evenly spaced vertices on a circle of radius `radius`, returning `(vertex array, start angle)`; when `start_angle=None`, even `n` starts at 0 and odd `n` at 90° |
| `shoelace(x_y) -> float` | shoelace formula for the **signed** area; must be fed `np.array`, and the implementation is `np.trapezoid(y, x)` — it **does not auto-append the closing edge**, so for a closed polygon append the first point again yourself |
| `shoelace_direction(x_y) -> str` | whether the winding is `"CW"` or `"CCW"` (upstream convention: positive area → `"CW"`) |

#### Sample: the area of a regular pentagon and a clockwise square

On the left, `regular_vertices(5, radius=1.4, start_angle=PI / 2)` gets the pentagon's vertices and joins them; after manually closing the loop, `shoelace` gives the signed area (`-4.660` shown) and `shoelace_direction` gives `CCW`. On the right a square ordered clockwise "lower-left → upper-left → upper-right → lower-right" yields `4.0` and `CW` the same way — flip the vertex order and the sign of the area flips with it.

```python
import numpy as np
from real_time_manim import Scene, Text, VGroup, Dot, Polygon, PURPLE, GREEN, \
    TEAL, YELLOW, GREY_B, GOLD, UP, DOWN, PI, regular_vertices, shoelace, \
    shoelace_direction, FadeIn, Write, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class PolygonDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("04-shoelace_regular_vertices", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        verts, sa = regular_vertices(5, radius=1.4, start_angle=PI / 2)   #vertices of a radius-1.4 regular pentagon + start angle
        poly = Polygon(*verts, color=PURPLE, fill_opacity=0.3, stroke_width=5).shift([-2.3, -0.4, 0])   #left half: regular pentagon
        vdots = VGroup(*[Dot(v + np.array([-2.3, -0.4, 0]), radius=0.08, color=GOLD)
                         for v in verts])   #dots on the five vertices
        lv = Text("regular_vertices(n=5, radius=1.4)", font_size=15, color=GREY_B)
        lv.move_to([-2.3, 2.4, 0])   #left figure title
        area = shoelace(np.array(list(verts) + [verts[0]]))   #shoelace formula: signed area (feed np.array, append the first point to close)
        dire = shoelace_direction(np.array(verts))   #winding direction: "CW" or "CCW"
        la = Text("shoelace = %.3f" % area, font_size=16, color=PURPLE).move_to([-2.3, -2.75, 0])   #area value
        ld = Text("shoelace_direction = " + dire, font_size=16, color=YELLOW).move_to([-2.3, -3.2, 0])   #direction
        win.play(FadeIn(lv), Create(poly), FadeIn(vdots), run_time=0.9)   #the whole pentagon appears
        win.play(FadeIn(la), FadeIn(ld), run_time=0.5)   #the area and direction lines

        sq = [np.array([1.0, -1.0, 0]), np.array([1.0, 1.0, 0]),   #right half: a clockwise-ordered square
              np.array([3.0, 1.0, 0]), np.array([3.0, -1.0, 0])]   #(lower-left → upper-left → upper-right → lower-right)
        sqp = Polygon(*sq, color=TEAL, fill_opacity=0.3, stroke_width=5)
        sqdots = VGroup(*[Dot(p, radius=0.08, color=GREEN) for p in sq])
        ls = Text("clockwise order (4 pts)", font_size=15, color=GREY_B).move_to([2.0, 2.4, 0])   #right figure title
        sarea = shoelace(np.array(sq + [sq[0]]))   #clockwise order + closed first point → signed area is positive
        sdir = shoelace_direction(np.array(sq))
        lsa = Text("shoelace = %.1f" % sarea, font_size=16, color=TEAL).move_to([2.0, -1.6, 0])
        lsd = Text("shoelace_direction = " + sdir, font_size=16, color=YELLOW).move_to([2.0, -2.05, 0])
        win.play(Create(sqp), FadeIn(sqdots), FadeIn(ls), run_time=0.7)   #the clockwise square
        win.play(FadeIn(lsa), FadeIn(lsd), run_time=0.5)   #its area and direction
        note = Text("shoelace(np.array) + close the loop", font_size=18, color=YELLOW).to_edge(DOWN)   #bottom note: must be closed, must be np.array
        win.play(FadeIn(note), run_time=0.35)   #bottom note: must be closed, must be np.array
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: on the left `regular_vertices` spits out the pentagon's five vertices; after joining them, appending the first point again lets `shoelace` compute the full area (`-4.660`, exactly the negative of `½·n·r²·sin(2π/n)`). On the right the square deliberately gets its vertices in clockwise order, so the area becomes the positive `4.0` and `shoelace_direction` is marked `CW`. Together the two examples give the conclusion: the **absolute value** of the area is the polygon's size and the **sign** is decided by the winding direction.

<video src="assets/RTM output/04-Vector-and-Geometry-Utilities-polygon.mp4" controls width="560"></video>

> Note: both pitfalls are stepped on in the sample.
>
> - Feeding `shoelace` a plain Python `list` raises `TypeError` (it must be `np.array`), and it **does not auto-close** (the first point must be appended to the end manually, otherwise the last edge's contribution is missing).
> - `shoelace_direction` only looks at the sign, so it does not matter whether the closing point is fed.

## Other `space_ops` functions (quick table)

Including rotation matrices, Z-axis alignment, complex-number interchange and low-frequency tools (parameters and defaults are folded into the signatures and descriptions):

| Signature | Meaning |
| --- | --- |
| `rotation_matrix(angle: float, axis: Vector3DLike, homogeneous: bool = False) -> np.ndarray` | 3×3 rotation matrix about any axis (uses scipy `Rotation.from_rotvec`); `homogeneous=True` returns a 4×4 homogeneous form, `axis` is normalized first |
| `z_to_vector(vector: np.ndarray) -> np.ndarray` | returns an SO(3) matrix `M` with `M @ [0,0,1] = normalize(vector)`; orients "Z-default" faces/circles/cones anywhere, used inside `Cube.generate_points` to place its 6 faces |
| `normalize(vect, fall_back: np.ndarray \| None = None) -> np.ndarray` | normalize to a unit vector; for a zero vector returns `fall_back` (default all-zero) |
| `compass_directions(n: int = 4, start_vect: np.ndarray = RIGHT) -> np.ndarray` | rotate `start_vect` by `TAU/n` each time for `n` evenly spaced directions (default 4 = up, right, down, left) |
| `complex_to_R3(complex_num: complex) -> np.ndarray` | complex → 3D point: `complex_to_R3(1+1j)` → `[1, 1, 0]` |
| `R3_to_complex(point: Sequence[float]) -> np.ndarray` | 3D point → complex (first two components only) |
| `complex_func_to_R3_func(complex_func) -> Callable` | wrap a complex function into a 3D function directly feedable to `ParametricFunction`/`Surface` (handy for plotting `e^z`, `z²`) |
| `norm_squared(v) -> float` | squared vector length (no square root) |
| `cross(v1, v2) -> Vector3D` | 3D cross product (hand-written `np.cross`) |
| `rotation_about_z(angle) -> np.ndarray` | 3×3 rotation matrix about Z |
| `rotation_matrix_transpose(angle, axis) -> np.ndarray` | transpose (inverse rotation) of a rotation matrix |
| `rotation_matrix_from_quaternion(quat) -> np.ndarray` | quaternion → rotation matrix |
| `rotation_matrix_transpose_from_quaternion(quat) -> list[np.ndarray]` | quaternion → transposed rotation matrix |
| `normalize_along_axis(array, axis) -> np.ndarray` | in-place normalization along a given axis |
| `quaternion_mult(*quats)` | Hamilton product of quaternions; no args returns the identity `[1,0,0,0]` |
| `quaternion_from_angle_axis(angle, axis, axis_normalized=False)` | angle + axis → quaternion |
| `angle_axis_from_quaternion(quaternion)` | quaternion → `(angle, axis)` |
| `quaternion_conjugate(quaternion)` | quaternion conjugate (negate the imaginary part) |
| `get_unit_normal(v1, v2, tol=1e-6) -> Vector3D` | unit normal of the plane of two vectors; `DOWN` when degenerate |
| `line_intersection(line1, line2) -> np.ndarray` | intersection of two **xy-plane** lines (each defined by two points); parallel lines or a z component raise |
| `find_intersection(p0s, v0s, p1s, v1s, threshold=1e-5) -> list[Point3D]` | closest points of two space lines (or rays); supports batch arrays |
| `perpendicular_bisector(line, norm_vector=OUT) -> Sequence[np.ndarray]` | the two endpoints of the perpendicular bisector of a two-point line (normal can be specified) |
| `cartesian_to_spherical(vec) -> np.ndarray` | `[x,y,z]` → `[r, theta, phi]` (`theta` azimuth, `phi` polar) |
| `spherical_to_cartesian(spherical) -> np.ndarray` | `[r, theta, phi]` → `[x,y,z]` |
| `get_winding_number(points) -> float` | winding number of a polygon about the origin (1 = contains the origin) |
| `cross2d(a, b)` | 2D cross/determinant; supports `(n,2)` batches |
| `thick_diagonal(dim, thickness=2) -> MatrixMN` | generate a banded 0/1 matrix (1 near the diagonal) |
| `earclip_triangulation(verts, ring_ends) -> list` | ear-clip triangulation indices for polygons with holes (internal algorithm, for fills/meshes) |

Not demonstrated: `rotation_matrix` / `rotation_about_z` / `z_to_vector` / the quaternion family / `normalize` / `norm_squared` / `cross` / `cross2d` and other pure-numpy matrix functions — their output is numbers or arrays, corresponding bit-for-bit to the rotation sample and the trig table, with no standalone visual.

`line_intersection` / `find_intersection` / `perpendicular_bisector` — visually identical to "two lines, one intersection point", with values read directly from the coordinates.

`complex_to_R3` / `R3_to_complex` / `complex_func_to_R3_func` / `cartesian_to_spherical` / `spherical_to_cartesian` — coordinate-system interchanges; visually equivalent to "the point stays put".

`quaternion_*` / `earclip_triangulation` / `thick_diagonal` — internal algorithms or low-frequency tools with no standalone visual semantics.

---

See also: [Path and Sequence Utilities](04b-Path-and-Sequence-Utilities.md) | [Directions and Constants](03-Directions-and-Constants.md)
