# Polygons and stars (1): the Polygram family

The classes in this section are defined in `mobject/geometry/polygram.py` and all inherit `Polygram` → `VMobject`: hand-drawn polygons, regular polygons, stars, and the all-purpose corner-rounding method.

`Polygram` / `Polygon` / `Triangle` use the native path. `Star(Polygon)` (`polygram.py:465`) is a polygon too and uses the **native** `_send_polygon` (`paint.py:1036`), with a dedicated assertion in `tests/test_polygram_groups.py:195` ("a `Star` is one group of 10 vertices"), no longer a "generic bezier fallback"; `RegularPolygram` / `RegularPolygon` / `round_corners` render with this page's samples.

The two samples on this page (`polygons` / `stars_round`) rendered on 2026-10-17 and (`frames>4.0` all 0).

## Parameters

### Polygram, Polygon, RegularPolygon (in this page's samples), Triangle

```python
def __init__(self, *vertex_groups: ArrayLike, color: ManimColor = BLUE,
             **kwargs: Any) -> None:  # Polygram

def __init__(self, *vertices: ArrayLike, **kwargs: Any) -> None:  # Polygon

def __init__(self, n: int = 6, **kwargs: Any) -> None:  # RegularPolygon

def __init__(self, **kwargs: Any) -> None:  # Triangle
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*vertex_groups` | `array-like...` | required | (`Polygram`) **every positional argument = one group of vertices**, and each group is itself a list of points: write `Polygram([p1, p2, p3, p4])`; passing single points straight in (`Polygram(p1, p2, ...)`) raises `IndexError` (verified) |
| `color` | `ManimColor` | `BLUE` | colour (blue by default; the samples all change it explicitly) |
| `*vertices` | `array-like...` | required | (`Polygon`) vertex coordinates; after joining them in order it **closes automatically**; `[x, y]` omits z, which is filled in as 0 |
| `n` | `int` | `6` | (`RegularPolygon`) number of sides; **accepts** an integer ≥3 |
| `radius` | `float` | `1` | (inherited) circumradius, shared by `RegularPolygon` / `Triangle` |
| `start_angle` | `float \| None` | `None` | (inherited) start angle; `None` picks it automatically per shape |

> **Returns**: a closed polygon object. Common methods: `get_vertices()` returns the array of all vertices (sample 2 uses it to place the vertex dots); for `round_corners(...)` see the second subsection. `Triangle` ≡ a specialization of `RegularPolygon(n=3)` that only saves you writing `n`.

#### Sample: a scrambled bow tie, an irregular quadrilateral, an equilateral triangle, and changing n

The top row has three shapes: `Polygram` interleaves its four vertices deliberately as "top-left → bottom-right → top-right → bottom-left" and its edges **self-intersect** into a bow tie (the order decides the shape); `Polygon` takes four vertices in the usual order for a filled quadrilateral; `Triangle()` gives an equilateral triangle. The bottom row changes only `n` on `RegularPolygon`, drawing a set of n=4 / 6 / 8.

```python
from real_time_manim import Scene, Polygram, Polygon, RegularPolygon, Triangle, Text, \
    TEAL, GREEN, PURPLE, ORANGE, BLUE, YELLOW, GREY_B, UP, DOWN, \
    Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class PolygonsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03-Polygram / Polygon / RegularPolygon / Triangle", font_size=26, color=YELLOW)
        title.to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— Polygram: one group of vertices = one positional argument, a scrambled order can self-intersect ——
        pb = Polygram([[-5.6, 2.0, 0], [-2.6, 0.8, 0], [-3.6, 2.0, 0], [-4.6, 0.8, 0]],
                      color=TEAL, stroke_width=5)   # vertices interleaved "top-left → bottom-right → top-right → bottom-left"
        cap1 = Text("Polygram (crossed order)", font_size=20, color=GREY_B).move_to([-4.6, 0.4, 0])
        win.play(Create(pb), FadeIn(cap1), run_time=0.7)   # draw the bow tie + caption

        # —— Polygon: joins in vertex order, closes, and can be filled ——
        pg = Polygon([-1.6, 2.0, 0], [1.6, 2.0, 0], [0.9, 0.7, 0], [-0.7, 0.7, 0],
                     color=GREEN, fill_opacity=0.55, stroke_width=5)   # an irregular quadrilateral with four vertices
        cap2 = Text("Polygon(*vertices)", font_size=20, color=GREY_B).move_to([0, 0.4, 0])
        win.play(Create(pg), FadeIn(cap2), run_time=0.7)   # draw the quadrilateral + caption

        # —— Triangle: an equilateral triangle (the n=3 specialization) ——
        tri = Triangle(radius=1.2, color=BLUE, fill_opacity=0.55).shift([4.6, 1.5, 0])   # equilateral triangle
        cap3 = Text("Triangle()", font_size=20, color=GREY_B).move_to([4.6, 0.4, 0])
        win.play(Create(tri), FadeIn(cap3), run_time=0.6)   # draw the triangle + caption

        # —— RegularPolygon: the shape changes as soon as n does ——
        r4 = RegularPolygon(n=4, radius=1.1, color=PURPLE, fill_opacity=0.55).shift([-4.6, -1.5, 0])   # n=4
        r6 = RegularPolygon(n=6, radius=1.1, color=ORANGE, fill_opacity=0.55).shift([0, -1.5, 0])   # n=6
        r8 = RegularPolygon(n=8, radius=1.1, color=BLUE, fill_opacity=0.55).shift([4.6, -1.5, 0])   # n=8
        cap4 = Text("RegularPolygon(n=4 / 6 / 8)", font_size=22, color=GREY_B).move_to([0, -2.8, 0])
        win.play(Create(r4), run_time=0.45)   # draw n=4
        win.play(Create(r6), run_time=0.45)   # draw n=6
        win.play(Create(r8), FadeIn(cap4), run_time=0.45)   # draw n=8 + caption
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the top row has three shapes side by side.

- The upper left is a bow-tie `Polygram` — "the same four points self-intersect once you change the order they are written in".
- The green `Polygon` in the middle joins four points in order, closes, and fills.
- `Triangle()` at the upper right gives an equilateral triangle straight away.

The three regular polygons in the bottom row **differ only in `n`** (4 purple / 6 orange / 8 blue), directly showing that "the shape changes as soon as the side count does".

<video src="assets/RTM output/03-Polygons-and-Stars-polygons.mp4" controls width="560"></video>

> Note:
>
> - `Polygram`'s vertex group **must be put into one positional argument as a whole** (a list of point lists); passing single points straight in raises `IndexError` — `Polygon` is the one that takes one positional argument per vertex.
> - The vertex order decides how the edges are joined, so give the points in whatever order produces the edges you want.
> - `radius` defaults to 1, which is very small; remember to scale it up as needed when composing.

### RegularPolygram (in this page's samples), Star (native `_send_polygon`), Polygram.round_corners (in this page's samples)

```python
def __init__(self, num_vertices: int, *, density: int = 2, radius: float = 1,
             start_angle: float | None = None, **kwargs: Any) -> None:  # RegularPolygram

def __init__(self, n: int = 5, *, outer_radius: float = 1,
             inner_radius: float | None = None, density: int = 2,
             start_angle: float = TAU / 4, **kwargs: Any) -> None:  # Star

def round_corners(self, radius: float = 0.5,
                  evenly_distribute_anchors: bool = False,
                  components_per_rounded_corner: int = 2) -> Self:  # Polygram.round_corners
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `num_vertices` / `n` | `int` | required / `5` | total number of vertices (corners); **accepts** an integer ≥3 |
| `density` | `int` | `2` | connection density — join a line every so many points: `1` = regular polygon, `2` = a two-pointed star / pentagram wireframe; on `Star` it only applies when `inner_radius=None` |
| `radius` | `float` | `1` | (`RegularPolygram`) circumradius |
| `outer_radius` | `float` | `1` | (`Star`) outer vertex radius |
| `inner_radius` | `float \| None` | `None` | (`Star`) inner vertex radius; `None` derives it from `density` (leave it `None` for standard proportions) |
| `start_angle` | `float \| None` | `None` / `TAU/4` | start angle / rotation; `Star` defaults to `TAU/4` so one point faces up |
| `radius` | `float` | `0.5` | (`round_corners`) corner radius; **accepts** 0 ~ half the shortest edge |
| `evenly_distribute_anchors` | `bool` | `False` | distribute the anchors evenly; **do not change** |
| `components_per_rounded_corner` | `int` | `2` | number of segments per rounded corner; **do not change** |

> **Returns**: a star / rounded polygon object (`round_corners` returns **itself** and is chainable — the sample calls it right at the end of the construction chain). `RegularPolygram` is the shared generator behind `RegularPolygon` and `Star`; `get_vertices()` works on them too.

#### Sample: three stars, the same trapezoid with two corner radii, and vertex dots

The top row has three stars: a gold pentagram with a hand-given inner radius, the pentagram **wireframe** from `RegularPolygram(density=2)` (with its own crossing lines built in), and a seven-pointed star with `inner_radius=None` left to `density=3` to derive. The bottom row has one pair of identical trapezoids changing only the `round_corners` radius (0.15 vs 0.55), and the hexagon on the far right places a yellow dot at each vertex using `get_vertices()`.

```python
from real_time_manim import Scene, Polygon, RegularPolygon, Star, RegularPolygram, \
    Dot, VGroup, Text, GOLD, TEAL, ORANGE, PURPLE, BLUE, YELLOW, GREY_B, \
    UP, DOWN, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class StarsRoundDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("03-Star / RegularPolygram / round_corners / get_vertices",
                     font_size=24, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        # —— First row: three stars ——
        s5 = Star(n=5, outer_radius=1.5, inner_radius=0.6, color=GOLD, fill_opacity=0.9)
        s5.shift([-4.7, 1.5, 0])   # a pentagram with a hand-given inner radius
        cap1 = Text("Star(inner_radius=0.6)", font_size=19, color=GREY_B).move_to([-4.7, 0.4, 0])
        win.play(Create(s5), FadeIn(cap1), run_time=0.6)   # draw the gold pentagram + caption

        rp = RegularPolygram(5, density=2, radius=1.4, color=TEAL, stroke_width=5)
        rp.shift([-0.6, 1.5, 0])   # the pentagram base class: join every other point (crossing lines built in)
        cap2 = Text("RegularPolygram(density=2)", font_size=19, color=GREY_B).move_to([-0.6, 0.4, 0])
        win.play(Create(rp), FadeIn(cap2), run_time=0.6)   # draw the pentagram wireframe + caption

        s7 = Star(n=7, outer_radius=1.4, density=3, color=BLUE, fill_opacity=0.6)
        s7.shift([4.6, 1.5, 0])   # seven-pointed star: inner_radius left to density to derive
        cap3 = Text("Star(n=7, density=3)", font_size=19, color=GREY_B).move_to([4.6, 0.4, 0])
        win.play(Create(s7), FadeIn(cap3), run_time=0.6)   # draw the seven-pointed star + caption

        # —— Second row: identical trapezoids, differing only in the corner radius ——
        t1 = Polygon([-5.9, -0.7, 0], [-3.3, -0.7, 0], [-3.7, -2.5, 0], [-5.5, -2.5, 0],
                     color=ORANGE, fill_opacity=0.55).round_corners(0.15)   # slight rounding
        cap4 = Text("round_corners(0.15)", font_size=19, color=GREY_B).move_to([-4.6, -2.85, 0])
        win.play(Create(t1), FadeIn(cap4), run_time=0.6)   # draw the slightly rounded trapezoid + caption

        t2 = Polygon([-2.7, -0.7, 0], [-0.1, -0.7, 0], [-0.5, -2.5, 0], [-2.3, -2.5, 0],
                     color=PURPLE, fill_opacity=0.55).round_corners(0.55)   # heavy rounding
        cap5 = Text("round_corners(0.55)", font_size=19, color=GREY_B).move_to([-1.4, -2.85, 0])
        win.play(Create(t2), FadeIn(cap5), run_time=0.6)   # draw the heavily rounded trapezoid + caption

        # —— get_vertices(): mark every vertex ——
        hexa = RegularPolygon(n=6, radius=1.1, color=BLUE, fill_opacity=0.3).shift([4.6, -1.6, 0])   # a blank hexagon
        dots = VGroup(*[Dot(p, radius=0.07, color=YELLOW) for p in hexa.get_vertices()])   # place yellow dots at the vertices
        cap6 = Text("get_vertices() -> dots", font_size=19, color=GREY_B).move_to([4.6, -2.85, 0])
        win.play(Create(hexa), run_time=0.5)   # draw the hexagon first
        win.play(FadeIn(dots), FadeIn(cap6), run_time=0.5)   # the yellow vertex dots + caption
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the three stars in the top row each demonstrate one way to fix the size.

- The gold star is given `inner_radius=0.6` by hand (sharper points).
- The teal `RegularPolygram(5, density=2)` shows the generator itself (a wireframe whose five edges cross each other).
- The blue star has seven points and leaves its inner radius to `density=3` to derive.

The two trapezoids in the bottom row have **identical shapes** and differ only in the `round_corners` radius, 0.15 rounding only slightly and 0.55 rounding noticeably. The hexagon on the far right draws the blank first, then places a yellow dot at each of the six vertices `get_vertices()` returns, verifying "vertex count = 6".

<video src="assets/RTM output/03-Polygons-and-Stars-stars_round.mp4" controls width="560"></video>

> Note:
>
> - With `density=1`, `RegularPolygram` degenerates into a regular polygon (the same shape as `RegularPolygon`).
> - `Star`'s `density` only takes effect when `inner_radius=None` — when both are given, `inner_radius` wins.
> - `round_corners` is a **chainable method** (it returns itself); a radius larger than half the shortest edge eats the edge entirely and deforms the shape, and the sample trapezoid 1.8 tall giving 0.55 is already a demonstration close to the limit.
> - When `RegularPolygram` / `Star` are drawn with `Create`, the stroke follows the vertex order, so a crossing star shows a "threading" process — that is normal.

---

See also: [Rectangles and special polygons](03b-Rectangles-and-Special-Polygons.md) · [Boolean operations](05-Boolean-Operations.md) · [VMobject styles](07-VMobject-Styles.md)
