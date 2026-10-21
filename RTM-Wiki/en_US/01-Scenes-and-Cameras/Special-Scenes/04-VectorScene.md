# VectorScene

A linear-algebra teaching scene for drawing vectors, writing coordinates and labeling basis vectors on a number-line plane; for grid-transformation play see [LinearTransformationScene](05-LinearTransformationScene.md). In RTM testing every method with a playable animation works.

First, one general precondition: the plane returned by `add_plane()` is **not** automatically hung on `self.plane`, while `get_vector` / `add_vector` need to read `self.plane`.

So every `add_plane` in the samples is followed immediately by `self.plane = plane` to hang it on by hand, and your own code should do the same.

## Parameters

### class VectorScene

```python
def __init__(self, basis_vector_stroke_width: float = 6.0, **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `basis_vector_stroke_width` | `float` | `6.0` | stroke width of the basis vectors (the `i_hat` / `j_hat` built by `get_basis_vectors`); **accepts** positive numbers, the samples contrast `6.0` and `2.0`, smaller is thinner |
| `**kwargs` | `Any` | — | forwarded to `Scene.__init__` (`random_seed` and so on, see [Scene Basics](../Scenes/01-Scene-Basics.md)) |

> **Returns**: none (constructs an instance).

### add_plane / add_axes

```python
def add_plane(self, animate: bool = False, **kwargs: Any) -> NumberPlane:
def add_axes(self, animate: bool = False, color: ParsableManimColor | Iterable[ParsableManimColor] = WHITE) -> Axes:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `animate` | `bool` | `False` | with `True` it plays the grid-drawing / axes-drawing entrance with `Create` (internally `self.play`, so under RTM set `self.play = win.play` first) |
| `color` | `ParsableManimColor \| Iterable[...]` | `WHITE` | `add_axes` only: axis color, **accepts** any color |
| `**kwargs` | `Any` | — | `add_plane` only: forwarded to `NumberPlane` (e.g. `x_range`, `y_range`) |

> **Returns**: `add_plane` returns a `NumberPlane` (remember to `self.plane = ...` by hand), `add_axes` returns `Axes`.

#### Sample: changing the constructor parameters and `add_plane`

The same scene run twice with only the `basis_vector_stroke_width` constructor parameter swapped: `Create` the grid first, then switch to drawing axes, and finally put the basis vectors on screen to see the stroke-width difference.

```python
from real_time_manim import VectorScene, Text, \
    UP, YELLOW
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   # instantly swap the top caption text without spending animation time
    cap.become(Text(text, font_size=28, color=YELLOW).to_edge(UP))

class PlaneAxesBase(VectorScene):
    STROKE = 6.0   # subclasses lower it to see the basis vectors get thinner
    TAG = ""       # subclasses fill in the stroke-width number for the title

    def __init__(self, **kwargs):
        super().__init__(basis_vector_stroke_width=self.STROKE, **kwargs)   # pass "basis_vector_stroke_width" to VectorScene.__init__

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # add_plane / add_axes call self.play internally, so wire it to the window first
        cap = Text("", font_size=28, color=YELLOW)   # top caption text (content swapped later)
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene

        say(cap, "add_plane(animate=True)")
        plane = self.add_plane(animate=True)   # draw the grid plane with Create
        self.plane = plane   # get_vector / add_vector both read self.plane, so hang it on by hand
        win.play(Wait(0.6))   # pause 0.6s

        say(cap, "add_axes(animate=True, color=WHITE)")
        self.remove(plane)   # take the grid away
        self.add_axes(animate=True, color=WHITE)   # draw the axes with Create
        win.play(Wait(0.4))   # pause 0.4s

        say(cap, "get_basis_vectors() stroke=%.1f" % self.STROKE)
        self.add(self.get_basis_vectors())   # put i_hat / j_hat on screen, at the constructor's stroke width
        win.play(Wait(0.8))   # pause 0.8s and finish
        win.close()   # close the RTM window


class PlaneAxesWide(PlaneAxesBase):
    STROKE = 6.0   # default stroke width
    TAG = "6.0"


class PlaneAxesThin(PlaneAxesBase):
    STROKE = 2.0   # one step thinner
    TAG = "2.0"
```

What this code does: the first clip (stroke width 6.0) uses `add_plane(animate=True)` to `Create` the grid and hangs it on `self.plane` by hand, then after taking the grid away draws the axes with `add_axes(animate=True, color=WHITE)`, and finally puts the default `i_hat`/`j_hat` on screen — the thickness of the basis vectors is the constructor parameter. The second clip is word for word the same apart from the stroke width being `2.0`, and the two clips are stitched into one video for comparison.

<video src="assets/RTM output/04-VectorScene-plane.mp4" controls width="560"></video>

> Note: don't forget `self.plane = plane` (`get_vector` / `add_vector` / `label_vector` all read it). After `add_axes` draws the axes, the sample deliberately does `self.remove(plane)` before drawing them, so that the two steps do not overlap in the frame. `basis_vector_stroke_width` only affects `get_basis_vectors()` (and the basis vectors automatically put on screen when the scene starts), not the axis stroke width.

### add_vector / get_vector

```python
def add_vector(self, vector: Arrow | Vector3DLike, color: ParsableManimColor | Iterable[ParsableManimColor] = PURE_YELLOW, animate: bool = True, **kwargs: Any) -> Arrow:
def get_vector(self, numerical_vector: Vector3DLike, **kwargs: Any) -> Arrow:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vector` | `Arrow \| Vector3DLike` | — | the vector: a coordinate list `[2, 1]` or a ready-made `Arrow` object |
| `color` | `ParsableManimColor \| Iterable[...]` | `PURE_YELLOW` | vector color, **accepts** any color |
| `animate` | `bool` | `True` | whether it enters with `GrowArrow` (internally `self.play`, so under RTM set `self.play = win.play` first) |
| `numerical_vector` | `Vector3DLike` | — | `get_vector` only: build an `Arrow` from coordinates |
| `**kwargs` | `Any` | — | forwarded to `Arrow` / the animation |

> **Returns**: both return an `Arrow`; `add_vector` adds it to the scene and registers it in `moving_vectors`, while `get_vector` **only builds it and does not add it** — when to `self.add` is up to you.

#### Sample: changing `add_vector` / `get_vector`

On one grid: `add_vector` adds a yellow vector that enters automatically, while `get_vector` builds another one that you `self.add` by hand.

```python
from real_time_manim import VectorScene, Text, \
    UP, YELLOW
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   # instantly swap the top caption text without spending animation time
    cap.become(Text(text, font_size=28, color=YELLOW).to_edge(UP))

class VectorAddDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # add_vector calls self.play internally, so wire it to the window first
        cap = Text("", font_size=28, color=YELLOW)   # top caption text (content swapped later)
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene
        plane = self.add_plane(animate=False)   # put the grid on screen directly
        self.plane = plane   # get_vector / add_vector both read self.plane, so hang it on by hand

        say(cap, "add_vector([2, 1], color=YELLOW, animate=True)")
        self.add_vector([2, 1], color=YELLOW, animate=True)   # build the vector from coordinates, entering with GrowArrow
        win.play(Wait(0.8))   # pause 0.8s

        say(cap, "get_vector([-2, 1]) -> self.add(arrow)")
        arrow = self.get_vector([-2, 1])   # only build the Arrow: not added to the scene, not registered
        self.add(arrow)   # decide for yourself when to add it
        win.play(Wait(0.8))   # pause 0.8s and finish
        win.close()   # close the RTM window
```

What this code does: after putting the grid on screen and hanging it on `self.plane`, it first calls `add_vector([2, 1], animate=True)` — building a yellow arrow from the coordinates and growing it out with `GrowArrow`; then `get_vector([-2, 1])` only builds a white arrow object, and nothing changes in the scene until `self.add(arrow)` is called by hand, when it appears. In the end two vectors sit side by side in one frame, showing directly the "does it add, does it play" difference between the two methods.

<video src="assets/RTM output/04-VectorScene-addvec.mp4" controls width="560"></video>

> Note: `add_vector`'s `animate` defaults to `True` (`get_vector` plays no animation at all); for "build first, put on screen later" use `get_vector` + your own `self.add`. `color` only takes effect when you pass coordinates (rather than a ready-made `Arrow`). Both methods read `self.plane`, so don't forget to hang it on by hand.

### write_vector_coordinates, label_vector, get_vector_label

```python
def write_vector_coordinates(self, vector: Vector, **kwargs: Any) -> Matrix:
def label_vector(self, vector: Vector, label: ManimTextLabel | str, animate: bool = True, **kwargs: Any) -> ManimTextLabel:
def get_vector_label(self, vector: Vector, label: ManimTextLabel | str, at_tip: bool = False, direction: str = "left", rotate: bool = False, color: ParsableManimColor | None = None, label_scale_factor: float = LARGE_BUFF - 0.2) -> ManimTextLabel:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vector` | `Vector` | — | the vector to label / write coordinates for (an `Arrow` already in the scene) |
| `label` | `ManimTextLabel \| str` | — | label content; **a single character is typeset as a letter with an arrow** (the `v` in the sample), several characters are laid out horizontally as usual |
| `animate` | `bool` | `True` | `label_vector` only: whether it enters with `Write` (internally `self.play`, so under RTM set `self.play = win.play` first) |
| `at_tip` | `bool` | `False` | `get_vector_label` only: put the label at the arrow tip |
| `direction` | `str` | `"left"` | `get_vector_label` only: which side of the vector to put it on, `"left"` / `"right"` |
| `rotate` | `bool` | `False` | `get_vector_label` only: whether to tilt it along the vector's direction |
| `color` | `ParsableManimColor \| None` | `None` (follows the vector) | `get_vector_label` only: label color |
| `label_scale_factor` | `float` | `LARGE_BUFF - 0.2` | `get_vector_label` only: label scale, the sample uses `1.0` |
| `**kwargs` | `Any` | — | forwarded to `Matrix` / label creation / the animation |

> **Returns**: `write_vector_coordinates` returns a `Matrix` (a column matrix, also added to the foreground layer); `label_vector` / `get_vector_label` return a label mobject — the former plays an animation and registers it, the latter **only builds it**, so `self.add` it yourself.

#### Sample: changing `write_vector_coordinates` / `label_vector`

One vector does three things in turn: write the column matrix `[2, 1]`, put on a label with `label_vector` (a single character typeset as a letter with an arrow), and build another label at the tip with `get_vector_label` and add it by hand.

```python
from real_time_manim import VectorScene, Text, \
    UP, YELLOW, GREEN
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   # instantly swap the top caption text without spending animation time
    cap.become(Text(text, font_size=28, color=YELLOW).to_edge(UP))

class VectorLabelDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # several methods below call self.play internally, so wire it to the window first
        cap = Text("", font_size=28, color=YELLOW)   # top caption text (content swapped later)
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene
        plane = self.add_plane(animate=False)   # put the grid on screen directly
        self.plane = plane   # add_vector reads self.plane, so hang it on by hand
        v = self.add_vector([2, 1], color=YELLOW, animate=True)   # you need a vector object first

        say(cap, "write_vector_coordinates(v)")
        self.write_vector_coordinates(v)   # write the column matrix [2, 1] and register it in the foreground layer
        win.play(Wait(0.8))   # pause 0.8s

        say(cap, "label_vector(v, 'v')")
        self.label_vector(v, "v")   # Write a label next to the vector; a single character is typeset as the arrow letter v
        win.play(Wait(0.8))   # pause 0.8s

        say(cap, "get_vector_label(v, 'w', at_tip=True, ...)")
        lab = self.get_vector_label(   # only builds the label, plays no animation; all the parameters are here
            v, "w", at_tip=True, direction="right",
            rotate=False, color=GREEN, label_scale_factor=1.0)
        self.add(lab)   # add it to the scene yourself
        win.play(Wait(0.8))   # pause 0.8s and finish
        win.close()   # close the RTM window
```

What this code does: it first adds a `[2, 1]` yellow vector, then brings on three annotations in turn.

- (1) `write_vector_coordinates(v)` writes the column matrix `★[2, 1]` next to the vector
- (2) `label_vector(v, "v")` uses `Write` to write a label next to the vector, and the single character `v` is typeset as a letter with an arrow
- (3) `get_vector_label(v, "w", at_tip=True, ...)` only builds a green `w` at the arrow tip, which appears once you `self.add` it by hand

The three annotations end up sharing the screen.

<video src="assets/RTM output/04-VectorScene-labels.mp4" controls width="560"></video>

> Note: `label_vector` plays an animation (`animate=True` by default), so under RTM write `self.play = win.play` first; `get_vector_label` plays no animation and is a "builder", so don't forget `self.add`. The arrow-letter typesetting of a single-character `label` is an upstream typesetting rule, not a rendering problem.
>
> `at_tip=True` puts the label at the arrow tip — if there is also a matrix nearby the two end up rather close, so to space them out use the default `at_tip=False` + `direction="left"`.

### get_basis_vectors / get_basis_vector_labels

```python
def get_basis_vectors(self, i_hat_color: ParsableManimColor | Iterable[ParsableManimColor] = X_COLOR, j_hat_color: ParsableManimColor | Iterable[ParsableManimColor] = Y_COLOR) -> VGroup:
def get_basis_vector_labels(self, **kwargs: Any) -> VGroup:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `i_hat_color` | `ParsableManimColor \| Iterable[...]` | `X_COLOR` (that is `GREEN_C`) | the color of `î`; **accepts** any color, the sample swaps in the standard `GREEN` (just one shade deeper, a subtle difference in the frame) |
| `j_hat_color` | `ParsableManimColor \| Iterable[...]` | `Y_COLOR` (that is `RED_C`) | the color of `ĵ`; the sample swaps in `RED` |
| `**kwargs` | `Any` | — | `get_basis_vector_labels` only: forwarded to label creation |

> **Returns**: both return a `VGroup` (they only build it and do not add it to the scene, so `self.add` it yourself); the stroke width is decided by the constructor parameter `basis_vector_stroke_width`.

#### Sample: changing `get_basis_vectors`

On one screen, first the basis vectors + labels in the default colors (`X_COLOR` / `Y_COLOR`), then swapped to `GREEN` / `RED` for comparison.

```python
from real_time_manim import VectorScene, Text, \
    UP, YELLOW, GREEN, RED
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   # instantly swap the top caption text without spending animation time
    cap.become(Text(text, font_size=28, color=YELLOW).to_edge(UP))

class BasisDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        cap = Text("", font_size=28, color=YELLOW)   # top caption text (content swapped later)
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene
        plane = self.add_plane(animate=False)   # put the grid on screen directly
        self.plane = plane   # nothing to do with the vectors, just a backdrop

        say(cap, "get_basis_vectors() default X_COLOR / Y_COLOR")
        basis = self.get_basis_vectors()   # default: i_hat green (X_COLOR), j_hat red (Y_COLOR)
        labels = self.get_basis_vector_labels()   # the MathTex labels for i_hat / j_hat
        self.add(basis, labels)   # add them to the scene together
        win.play(Wait(0.9))   # pause 0.9s

        self.remove(basis, labels)   # take the default-colour basis vectors away
        say(cap, "get_basis_vectors(i_hat_color=GREEN, j_hat_color=RED)")
        basis2 = self.get_basis_vectors(   # swap in manim's standard GREEN / RED (different from the defaults)
            i_hat_color=GREEN, j_hat_color=RED)
        self.add(basis2, labels)   # reuse the labels, only the colors changed
        win.play(Wait(0.9))   # pause 0.9s and finish
        win.close()   # close the RTM window
```

What this code does: it first calls `get_basis_vectors()` for the default-colored `î`/`ĵ` (`GREEN_C`/`RED_C` respectively) and puts them on screen together with the `MathTex` labels from `get_basis_vector_labels()`; 0.9 seconds later it takes them away and swaps in the version with `GREEN`/`RED` passed explicitly (reusing the labels), then watches for another 0.9 seconds.

The two color steps differ by one shade only, so the comparison is subtle to the eye — for a clearly visible difference just pass your own colors (such as `BLUE`/`ORANGE`).

<video src="assets/RTM output/04-VectorScene-basis.mp4" controls width="560"></video>

> Note: the defaults are `X_COLOR = GREEN_C` and `Y_COLOR = RED_C`, only one shade away from `GREEN`/`RED`, so the two clips look almost the same — swap in strongly contrasting colors for an obvious difference. Both methods only build and do not add to the scene. The labels are `MathTex` (rendered through RTM's Typst conversion path), and the stroke width is governed solely by `basis_vector_stroke_width`.

### vector_to_coords

```python
def vector_to_coords(self, vector: Vector3DLike, integer_labels: bool = True, clean_up: bool = True) -> tuple[Matrix, Line, Line]:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vector` | `Vector3DLike` | — | the coordinates to decompose, such as `[-1, 2]`, `[1.5, -1]` |
| `integer_labels` | `bool` | `True` | show the labels rounded to integers (`-1` instead of `-1.0`); **accepts** `False` to see decimal labels |
| `clean_up` | `bool` | `True` | restore the scene afterwards (the decomposition lines and the matrix leave automatically) |

> **Returns**: the `(matrix, x line, y line)` triple (the method plays the animation itself, so under RTM set `self.play = win.play` first; this method takes no `run_time`, its pacing is fixed at roughly 6 seconds per call).

#### Sample: changing `vector_to_coords`

One scene decomposing twice in a row: the integer vector `[-1, 2]` (`integer_labels=True`) and the decimal vector `[1.5, -1]` (`integer_labels=False`).

```python
from real_time_manim import VectorScene, Text, \
    UP, YELLOW
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   # instantly swap the top caption text without spending animation time
    cap.become(Text(text, font_size=28, color=YELLOW).to_edge(UP))

class CoordsDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # vector_to_coords calls self.play internally, so wire it to the window first
        cap = Text("", font_size=28, color=YELLOW)   # top caption text (content swapped later)
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene
        plane = self.add_plane(animate=False)   # put the grid on screen directly
        self.plane = plane   # nothing to do with the vectors, just a backdrop

        say(cap, "vector_to_coords([-1, 2], integer_labels=True)")
        self.vector_to_coords([-1, 2], integer_labels=True, clean_up=True)   # vector-to-coordinates decomposition, restored at the end
        win.play(Wait(0.5))   # pause 0.5s

        say(cap, "vector_to_coords([1.5, -1], integer_labels=False)")
        self.vector_to_coords([1.5, -1], integer_labels=False, clean_up=True)   # decimals get decimal labels
        win.play(Wait(0.5))   # pause 0.5s and finish
        win.close()   # close the RTM window
```

What this code does: the first time it decomposes `[-1, 2]` — a white vector grows out, then the green x-component line (labeled `-1`) and the red y-component line (labeled `2`) are drawn, then the column matrix `[-1, 2]` is written, and `clean_up=True` lets all of it leave automatically.

The second time it swaps in the decimal vector `[1.5, -1]` and turns `integer_labels` off, so the labels show `1.5` and `-1.0` (rather than the rounded `2` and `-1`). The two runs show the same decomposition animation under two label rules.

<video src="assets/RTM output/04-VectorScene-coords.mp4" controls width="560"></video>

> Note: `vector_to_coords` plays two animations in a row and **has no `run_time` parameter** (the signature is fixed), roughly 6 seconds per call, which is where the whole 13-second video comes from.
>
> `clean_up=True` takes the decomposition lines and the matrix away at the end; pass `False` to keep the process on screen.
>
> The reverse direction, `coords_to_vector` (coordinate matrix → vector), has a bug in upstream `manim` 0.21, see the next section.

### lock_in_faded_grid / coords_to_vector / show_ghost_movement

```python
def lock_in_faded_grid(self, dimness: float = 0.7, axes_dimness: float = 0.5) -> None:
def coords_to_vector(self, vector: Vector2DLike, coords_start: Point3DLike = 2 * RIGHT + 2 * UP, clean_up: bool = True) -> None:
def show_ghost_movement(self, vector: Arrow | Vector2DLike | Vector3DLike) -> None:
```

The three methods have bugs of their own in upstream `manim` 0.21, and **plain command-line rendering crashes just the same**; it is not an RTM problem, so they get no video:

| Method | Upstream problem | Status |
| --- | --- | --- |
| `lock_in_faded_grid` | internally calls `renderer.update_frame()` without the `scene` argument, with a TODO comment right there in the source | unusable |
| `coords_to_vector` | `Matrix(vector)` raises `TypeError: 'numpy.float64' object is not iterable` | unusable |
| `show_ghost_movement` | constructing `VMobject(*Dots)` raises `ValueError` (in 0.20.1 it was `Dot object has no attribute 'hex'`) | unusable |

If you just want the "faded grid" look, use `add_plane(animate=False)` and then `plane.set_opacity(0.3)` or similar instead; for the "moving ghost" look, see the path-arc idea of the `apply_*` animations (see [LinearTransformationScene](05-LinearTransformationScene.md)).

---

See also: [LinearTransformationScene](05-LinearTransformationScene.md), [ThreeDScene](02-ThreeDScene.md), [Scene Basics](../Scenes/01-Scene-Basics.md)
