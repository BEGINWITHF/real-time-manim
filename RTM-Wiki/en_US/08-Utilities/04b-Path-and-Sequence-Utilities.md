# Transform paths and sequence utilities: paths, simple_functions, iterables

Three small utility modules: transform trajectories, small math functions and sequence handling; all available via `from manim import ...` unless marked otherwise. RTM reuses the manim implementation directly — `Transform`'s `path_func` hook and numpy sequence operations are bit-identical. The two samples on this page demonstrate `path_along_arc`'s three trajectories and `adjacent_pairs` closed edges + three small-math-function values; all have been rendered in RTM.

## `path_along_arc` — transform along an arc (`utils/paths.py`)

```python
path_along_arc(arc_angle: float, axis: Vector3DLike = OUT) -> PathFuncType
```

For `Transform(m1, m2, path_func=...)`: makes each point travel along an arc, rotating `arc_angle` radians to reach the end (about `axis`). `arc_angle=TAU/2` is a half turn, `-TAU/2` the reverse; `|arc_angle| < 0.01` auto-degenerates to a straight path.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `arc_angle` | `float` | required | angle each point sweeps (radians, may be negative) |
| `axis` | `Vector3DLike` | `OUT` | rotation axis |

> **Returns**: `PathFuncType` with signature `(start_points, end_points, alpha) -> points`; pass it straight to `Transform(..., path_func=...)`.

#### Sample: three transform trajectories of the same chord

Three lanes have identical start and end points (the same chord) and depart together: the top lane `path_along_arc(-TAU / 2)` bulges above the chord, the middle lane is a straight default, and the bottom lane `path_along_arc(TAU / 2)` bulges below — the half-turn arc is exactly a semicircle with the chord as diameter.

```python
from real_time_manim import Scene, Text, VGroup, Dot, Line, Circle, BLUE, GREEN, \
    RED, YELLOW, GREY_B, UP, DOWN, TAU, path_along_arc, Transform, \
    FadeIn, Write, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class PathArcDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("04b-path_along_arc", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        xs0, xs1 = -1.8, 1.8   #shared start and end x of the three lanes (same chord length)
        lanes = [
            (1.1, GREEN, "path_along_arc(-TAU/2)", -TAU / 2),   #top: half turn in reverse (arc bulges upward)
            (-0.2, BLUE, "straight (default)", None),   #middle: default straight path
            (-1.4, RED, "path_along_arc(TAU/2)", TAU / 2),   #bottom: half turn forward (arc bulges downward)
        ]
        movers = []
        for y, c, nm, arc in lanes:
            track = Line([xs0, y, 0], [xs1, y, 0], color=GREY_B, stroke_width=2)
            track.set_stroke(opacity=0.3)   #chord (reference straight line, translucent)
            lab = Text(nm, font_size=16, color=c).next_to(track, UP, buff=0.15)   #lane name above the track
            s0 = Circle(radius=0.12, color=GREY_B, stroke_width=2).move_to([xs0, y, 0])   #start ring
            s1 = Circle(radius=0.12, color=GREY_B, stroke_width=2).move_to([xs1, y, 0])   #end ring
            dot = Dot([xs0, y, 0], radius=0.14, color=c)   #departing dot
            target = Dot([xs1, y, 0], radius=0.14, color=c)   #target dot at the end
            win.play(FadeIn(VGroup(track, lab, s0, s1)), run_time=0.4)   #lane positions first
            movers.append((dot, target, arc))
        win.play(FadeIn(VGroup(*[m for m, _, _ in movers])), run_time=0.3)   #the three dots take position
        win.play(*[Transform(m, t, path_func=path_along_arc(a) if a else None,
                             run_time=1.6)
                   for m, t, a in movers])   #one chord × three path_funcs starting together
        note = Text("Transform(..., path_func=path_along_arc(arc))",
                    font_size=18, color=YELLOW).to_edge(DOWN)   #bottom note
        win.play(FadeIn(note), run_time=0.35)   #note fades in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: the grey translucent chord in each lane is the "straight-line distance" reference, and three colored dots simultaneously perform a `Transform` to the same endpoint — only `path_func` differs. The green and red dots bulge as semicircles on opposite sides of the chord (`±TAU/2` are exactly semicircles with diameter equal to the chord), while the blue dot goes straight by default. Grab any frame midway and you see the three dots on completely different trajectories.

<video src="assets/RTM output/04b-Path-and-Sequence-Utilities-paths.mp4" controls width="560"></video>

> Note:
>
> - `path_along_arc`'s arc is **an arc swept about the midpoint of start—end**; at `±π` it is a semicircle with the chord as diameter, and the arc's "bulge height" equals half the chord length — a chord that is too long sends the arc off-screen, so leave enough room when framing.
> - At small angles (`< 0.01`) it auto-degenerates to a straight line and will not jitter from numerical issues.

## Other path functions (`utils/paths.py`)

| Signature | Meaning |
| --- | --- |
| `straight_path() -> PathFuncType` | straight path (`Transform`'s default behavior) |
| `clockwise_path() -> PathFuncType` | clockwise half-circle (= `path_along_arc(-π)`) |
| `counterclockwise_path() -> PathFuncType` | counterclockwise half-circle (= `path_along_arc(π)`) |
| `path_along_circles(arc_angle, circles_centers, axis=OUT)` | each point circles its **own** center (not top-level; needs `real_time_manim.manim.utils.paths.path_along_circles`) |
| `spiral_path(angle, axis=OUT)` | spiral path rotating while converging to the endpoint (not top-level; needs `real_time_manim.manim.utils.paths.spiral_path`) |
| `STRAIGHT_PATH_THRESHOLD = 0.01` | angles below this auto-degenerate to a straight path (not top-level) |

## `iterables` — sequence helpers

> Entries marked ⚙ need `from real_time_manim.manim.utils.iterables import ...` (deep path; RTM's aliases resolve to the same bundled module); the rest are available via `from real_time_manim import ...`.

| Signature | Frequency | Meaning |
| --- | --- | --- |
| `listify(obj) -> list` | 🟡 | smart to-list: a string becomes `[str]`, an iterable becomes `list(...)`, anything else becomes `[obj]` |
| `tuplify(obj) -> tuple` | ⚪ | same, to tuple |
| `adjacent_pairs(objects)` | 🟡 | circular adjacent pairs: `[1,2,3,4] → (1,2),(2,3),(3,4),(4,1)` (common for drawing polygon edges) |
| `adjacent_n_tuples(objects, n)` | ⚪ | circular tuples of length `n` (generalization of `adjacent_pairs`) |
| `remove_nones(sequence) -> list` | 🟡 | drop all "falsy" elements (`None`, `""`, `0`, `False`, …) |
| `list_update(l1, l2) -> list` | 🟡 | dedup-merge, **preserving l2 order** |
| `list_difference_update(l1, l2) -> list` | 🟡 | elements of `l1` not in `l2` |
| `concatenate_lists(*list_of_lists) -> list` | 🟡 | flatten several lists into one |
| `remove_list_redundancies(lst) -> list` | 🟡 | dedup keeping the **last** occurrence (ordered by last position); replaces `list(set(...))` |
| `make_even(i1, i2) -> tuple[list, list]` | ⚪ | pad the shorter by **repeating earlier elements** to equal length |
| `make_even_by_cycling(i1, i2) -> tuple[list, list]` | ⚪ | same, but padded by **cycling** |
| `all_elements_are_instances(iterable, Class) -> bool` | ⚪ | whether all elements are of a type |
| `stretch_array_to_length(nparray, length)` | ⚪ | index-resample an array to a target length |
| ⚙ `batch_by_property(items, property_func)` | ⚪ | split a sequence into contiguous same-property batches |
| ⚙ `resize_array(nparray, length)` | ⚪ | cyclic pad/truncate to a length |
| ⚙ `resize_preserving_order(nparray, length)` | ⚪ | resize by duplicating elements (order-preserving) |
| ⚙ `resize_with_interpolation(nparray, length)` | ⚪ | resize by linear interpolation |
| ⚙ `uniq_chain(*args)` | ⚪ | generator: yield all deduped elements in given order |
| ⚙ `hash_obj(obj) -> int` | ⚪ | hash for mutable containers (dict/set/list) |

#### Sample: `adjacent_pairs` closed edges and three small math functions

On the left, four points have their edges drawn one by one with `adjacent_pairs` — note the fourth edge automatically goes from the last point **back to the first**, closing the quadrilateral; on the right, three lines give the actual values of `choose(5, 2)`, `clip(3.7, 0, 1)` and `sigmoid(0)`, and the bottom line is the dedup result of `remove_list_redundancies`.

```python
from real_time_manim import Scene, Text, VGroup, Dot, Line, BLUE, GREEN, RED, \
    YELLOW, GREY_B, TEAL, WHITE, UP, DOWN, LEFT, adjacent_pairs, choose, \
    clip, sigmoid, FadeIn, Write, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class SequenceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("04b-iterables_functions", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        pts = [(-3.2, -0.9, 0), (-1.5, -2.0, 0),   #four points on the left (an irregular quadrilateral)
               (-0.9, 0.5, 0), (-2.9, 1.4, 0)]
        head = Text("adjacent_pairs: 4 pts -> 4 edges", font_size=15, color=GREY_B)
        head.move_to([-2.1, 2.1, 0])   #left figure title
        dots = VGroup(*[Dot(p, radius=0.09, color=RED) for p in pts])   #four vertices
        win.play(FadeIn(head), FadeIn(dots), run_time=0.5)   #title and vertices position first
        edges = [Line(a, b, color=BLUE, stroke_width=4)   #adjacent pairs: (1,2)(2,3)(3,4)(4,1)
                 for a, b in adjacent_pairs(pts)]   #the last pair (4,1) is added automatically, closing the quadrilateral
        for e in edges:
            win.play(Create(e), run_time=0.35)   #draw the four edges one by one (the fourth returns to the start)

        vals = VGroup(
            Text("choose(5, 2) = %d" % choose(5, 2), font_size=18, color=WHITE),
            Text("clip(3.7, 0, 1) = %.1f" % clip(3.7, 0, 1), font_size=18, color=GREEN),
            Text("sigmoid(0) = %.3f" % sigmoid(0), font_size=18, color=TEAL),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)   #three value lines on the right
        vals.move_to([1.9, 0.3, 0])
        win.play(FadeIn(vals), run_time=0.6)   #the three value lines fade in
        note = Text("remove_list_redundancies: [1,2,1,3,2] -> [1,3,2]",
                    font_size=17, color=YELLOW).to_edge(DOWN)   #dedup keeping the last occurrence
        win.play(FadeIn(note), run_time=0.35)   #bottom note fades in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: four red points fed in order to `adjacent_pairs` produce the four pairs `(1,2)(2,3)(3,4)(4,1)`. The four blue edges are drawn one by one and the last one naturally **caps** the shape — that is the point of "circular adjacent pairs" (drawing an arbitrary polygon's border in one line).

The three lines on the right are the live values of three small math functions: binomial `C(5,2)=10`, clamp `clip(3.7,0,1)=1.0`, `sigmoid(0)=0.500`.

The bottom line explains that the dedup function "keeps the last occurrence" — the last `2` is at the end, so it comes after `3`.

<video src="assets/RTM output/04b-Path-and-Sequence-Utilities-iterables.mp4" controls width="560"></video>

> Note:
>
> - `adjacent_pairs` returns a **zip iterator**, not a list (wrap in `list(...)` to re-iterate or take `len`).
> - `remove_list_redundancies` keeps the **last** occurrence, so `[1,2,1,3,2]` gives `[1,3,2]`, not `[1,2,3]` — for first-occurrence order use `dict.fromkeys` yourself.

## `simple_functions` — small math helpers (`utils/simple_functions.py`)

| Signature | Frequency | Meaning |
| --- | --- | --- |
| `sigmoid(x) -> float` | 🟡 | logistic `1/(1+e^-x)`; used by `ArrowVectorField`'s default `length_func` for saturation; sample 2's right side already features `sigmoid(0) = 0.500` |
| `clip(a, min_a, max_a)` | 🟡 | clamp `a` to `[min_a, max_a]`; works on any comparable objects; sample 2 features `clip(3.7, 0, 1) = 1.0` |
| `choose(n, k) -> int` | ⚪ | binomial `C(n,k)` (with `lru_cache`); sample 2 features `choose(5, 2) = 10` |
| `binary_search(function, target, lower_bound, upper_bound, tolerance=1e-4) -> float \| None` | ⚪ | numeric bisection: find `x` in the interval with `function(x) == target`, or `None` if not found |

Not demonstrated: `listify` / `tuplify` / `adjacent_n_tuples` / `remove_nones` / `list_update` / `list_difference_update` / `concatenate_lists` / `make_even` / `resize_*` / `batch_by_property` / `uniq_chain` / `hash_obj` / `binary_search` / `straight_path` / `clockwise_path` / `counterclockwise_path` / `path_along_circles` / `spiral_path` — the first three groups are pure data functions with list/tuple/number inputs and outputs, so the screen can only restate their results as text (sample 2 already gives representatives of the same families).

`clockwise_path` / `counterclockwise_path` are bit-identical to `path_along_arc(±π)` in sample 1, and `straight_path` is the middle lane's default behavior in sample 1.

---

See also: [Vector and Geometry Utilities](04-Vector-and-Geometry-Utilities.md) | [Directions and Constants](03-Directions-and-Constants.md)
