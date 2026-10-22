# LinearTransformationScene

A teaching scene with its own grids (a grey background grid plus a teal foreground grid that gets transformed), basis vectors `î`/`ĵ` and a label system, using the `apply_*` family of methods to play matrix/function transform animations; if you only want to draw vectors without transforming the grid, use [VectorScene](04-VectorScene.md).

Under RTM all of it is verified to work (the constructor switches, the four kinds of `apply_*`, and the auto-rewriting transform labels).

## Parameters

### class LinearTransformationScene

```python
def __init__(self, include_background_plane: bool = True, include_foreground_plane: bool = True, background_plane_kwargs: dict[str, Any] | None = None, foreground_plane_kwargs: dict[str, Any] | None = None, show_coordinates: bool = False, show_basis_vectors: bool = True, basis_vector_stroke_width: float = 6, i_hat_color: ParsableManimColor = X_COLOR, j_hat_color: ParsableManimColor = Y_COLOR, leave_ghost_vectors: bool = False, **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `include_background_plane` | `bool` | `True` | whether to add the grey background grid; switching only this off still leaves **a grid in the frame** (the foreground plane has its own), and to clear it you must switch off the next row too (sample 1, third clip) |
| `include_foreground_plane` | `bool` | `True` | whether to add the teal foreground grid that gets transformed; switch it off and `self.plane` is `None`, so `apply_*` only transforms the basis vectors |
| `background_plane_kwargs` | `dict \| None` | `None` (built-in grey thin-line style) | override the background `NumberPlane` parameters; normally leave empty |
| `foreground_plane_kwargs` | `dict \| None` | `None` (built-in `x/y_range=±frame_width`, `faded_line_ratio=1`) | override the foreground `NumberPlane` parameters; normally leave empty |
| `show_coordinates` | `bool` | `False` | the background grid shows tick numbers; **accepts** `True` (sample 1, second clip) |
| `show_basis_vectors` | `bool` | `True` | whether to show `î`/`ĵ`; **accepts** `False` to hide the basis vectors |
| `basis_vector_stroke_width` | `float` | `6` | basis-vector stroke width, the same parameter as in [VectorScene](04-VectorScene.md) |
| `i_hat_color` | `ParsableManimColor` | `X_COLOR` (`GREEN_C`) | the color of `î`; **accepts** any color |
| `j_hat_color` | `ParsableManimColor` | `Y_COLOR` (`RED_C`) | the color of `ĵ`; **accepts** any color |
| `leave_ghost_vectors` | `bool` | `False` | keep the "ghost" of the basis vectors' old position after the transform; **accepts** `True` (sample 1, fourth clip) |
| `**kwargs` | `Any` | — | forwarded to `VectorScene.__init__` → `Scene.__init__` (see [Scene Basics](../Scenes/01-Scene-Basics.md)) |

> **Returns**: none (constructs an instance). The grids and basis vectors are added automatically by `setup()` when the scene starts and are ready to use in `construct`.

#### Sample: changing the constructor parameters

Four clips, each changing one step of the constructor parameters: the default staging, `show_coordinates=True`, both planes off (only the basis vectors left), and `leave_ghost_vectors=True` (with one shear to see the ghost).

```python
from real_time_manim import LinearTransformationScene, Text, \
    Wait
from real_time_manim.vulkan_bind import MLWindow, Wait

class CtorBase(LinearTransformationScene):
    KW = {}            # subclasses fill in the constructor parameters to pass to LinearTransformationScene.__init__
    LABEL = ""         # subclasses fill in this clip's title text
    TRANSFORM = False  # subclasses with True play one shear at the end

    def __init__(self, **kwargs):
        super().__init__(**self.KW, **kwargs)   # pass the keys in "KW" to LinearTransformationScene.__init__

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # apply_* calls self.play internally, so wire it to the window first
        cap = Text(self.LABEL, font_size=26, color=YELLOW)   # top title shows the current constructor parameters
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene (setup adds the grids and basis vectors automatically)
        win.play(Wait(1.3))   # pause 1.3s to see the default staging
        if self.TRANSFORM:
            self.apply_matrix([[1, 1], [0, 1]], run_time=1.2)   # one horizontal shear: only then is the ghost switch visible
            win.play(Wait(0.6))   # pause 0.6s to see the ghost
        win.close()   # close the RTM window


class LtsPlain(CtorBase):
    LABEL = "defaults (bg+fg plane, i_hat/j_hat)"   # default staging
    KW = {}                                          # an empty dict = manim's defaults


class LtsCoords(CtorBase):
    LABEL = "show_coordinates=True"                 # the background grid shows tick numbers
    KW = {"show_coordinates": True}


class LtsBgOff(CtorBase):
    LABEL = "include_background/foreground_plane=False"   # both grid planes gone
    KW = {"include_background_plane": False,              # switch off the background plane
          "include_foreground_plane": False}              # switch off the foreground plane: only the basis vectors remain


class LtsGhost(CtorBase):
    LABEL = "leave_ghost_vectors=True"              # keep the basis vectors' ghost after the transform
    KW = {"leave_ghost_vectors": True}
    TRANSFORM = True                                # this clip plays one transform
```

What this code does: the base class collects the constructor parameters into a `KW` dict and passes them to `LinearTransformationScene.__init__`, and the four subclasses each change one step.

- The first passes nothing, showing the default staging (grey background grid + teal foreground grid + green `î`/red `ĵ`)
- The second is `show_coordinates=True`, and the background grid gains tick numbers
- The third switches both planes off, leaving only the two basis vectors in the frame (the starkest contrast)
- The fourth is `leave_ghost_vectors=True`: after one horizontal shear at the end, the basis vectors leave a ghost at their old position

<video src="assets/RTM output/05-LinearTransformationScene-ctor.mp4" controls width="560"></video>

> Note: **switching off only the background plane still leaves a grid in the frame** (the teal foreground plane has its own grid lines), and to clear it completely you must switch off both parameters — which is why the third clip exists. The ghost only applies to the **basis vectors** (the grid leaves no ghost), and it only appears when "a transform happens", so a static setup shows nothing. The `show_coordinates` numbers are drawn on the background plane, so switching that plane off naturally removes them too.

### apply_matrix / apply_inverse / apply_transposed_matrix / apply_inverse_transpose

The four linear-transform entry points, all of which act on the foreground grid, the basis vectors and `moving_vectors` (including the unit square):

- `apply_matrix` applies the matrix M
- `apply_inverse` applies the inverse of M (undoes it)
- `apply_transposed_matrix` takes M and actually applies its transpose
- `apply_inverse_transpose` applies the inverse of the transpose

```python
def apply_matrix(self, matrix: np.ndarray | list | tuple, **kwargs: Any) -> None:
def apply_inverse(self, matrix: np.ndarray | list | tuple, **kwargs: Any) -> None:
def apply_transposed_matrix(self, transposed_matrix: np.ndarray | list | tuple, **kwargs: Any) -> None:
def apply_inverse_transpose(self, t_matrix: np.ndarray | list | tuple, **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `matrix` | `np.ndarray \| list \| tuple` | — | a 2×2 matrix (a list is fine); **accepts** any invertible matrix; `apply_inverse` requires the matrix to be invertible (a singular matrix raises) |
| `transposed_matrix` / `t_matrix` | `np.ndarray \| list \| tuple` | — | same as above; what you pass is the "pre-transpose" original matrix — what is actually applied is its transpose (in the sample, passing `[[1,1],[0,1]]` is actually a vertical shear) |
| `**kwargs` | `Any` | — | forwarded to `self.play`: `run_time` (the sample uses `1.2`), `path_arc` and so on. `path_arc` travels via **play-level** propagation (that is how manim's `apply_transposed_matrix` is written); before 2026-10-17 RTM's `win.play()` only forwarded `run_time`/`rate_func` and swallowed it, which is now fixed (`Transform.path_arc`'s setter rebuilds `path_func`) |

> **Returns**: none (it plays the animation via `self.play` internally, so under RTM you must first set `self.play = win.play`).

#### Sample: changing the apply family

One shear matrix walks through four steps: apply (horizontal shear) → invert to undo → transpose (becoming a vertical shear) → inverse transpose to undo. Four plays in a row, and the direction the grid changes is visible to the eye.

```python
from real_time_manim import LinearTransformationScene, Text, \
    UP, YELLOW, Wait
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   # instantly swap the top caption text without spending animation time
    cap.become(Text(text, font_size=26, color=YELLOW).to_edge(UP))

class ApplyDemo(LinearTransformationScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # every apply_* calls self.play internally, so wire it to the window first
        cap = Text("", font_size=26, color=YELLOW)   # top caption text (content swapped later)
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene

        say(cap, "apply_matrix([[1, 1], [0, 1]])")
        self.apply_matrix([[1, 1], [0, 1]], run_time=1.2)   # horizontal shear: the whole grid leans up and to the right
        win.play(Wait(0.5))   # pause 0.5s

        say(cap, "apply_inverse([[1, 1], [0, 1]])")
        self.apply_inverse([[1, 1], [0, 1]], run_time=1.2)   # invert M and apply it, undoing the previous step
        win.play(Wait(0.5))   # pause 0.5s

        say(cap, "apply_transposed_matrix([[1, 1], [0, 1]])")
        self.apply_transposed_matrix([[1, 1], [0, 1]], run_time=1.2)   # pass M, apply its transpose (a vertical shear)
        win.play(Wait(0.5))   # pause 0.5s

        say(cap, "apply_inverse_transpose([[1, 1], [0, 1]])")
        self.apply_inverse_transpose([[1, 1], [0, 1]], run_time=1.2)   # apply the inverse transpose, back to the original grid
        win.play(Wait(0.6))   # pause 0.6s and finish
        win.close()   # close the RTM window
```

What this code does: it walks the full loop with one matrix, `[[1, 1], [0, 1]]`.

- (1) `apply_matrix` shears the grid horizontally (leans the x direction)
- (2) `apply_inverse` inverts it back to an orthogonal grid
- (3) `apply_transposed_matrix` applies the transpose, turning the grid into a vertical shear (visibly different from (1))
- (4) `apply_inverse_transpose` applies the inverse transpose and returns to the original grid once more

The "direction of action" of the four methods can be compared one after another on one screen.

<video src="assets/RTM output/05-LinearTransformationScene-apply.mp4" controls width="560"></video>

> Note: the parameters of `apply_transposed_matrix` / `apply_inverse_transpose` are the **original matrix** (the method transposes it internally), so don't pass an already-transposed matrix. `apply_inverse` raises `LinAlgError` outright for a singular matrix (determinant 0). `run_time` is forwarded to `self.play` and can be passed to all four methods.

### apply_nonlinear_transformation / apply_function

Two nonlinear entry points: the former subdivides the foreground grid first (`prepare_for_nonlinear_transform`) and then applies the function (smooth lines where it curves), the latter applies the function point by point (good for a simple stretch).

```python
def apply_nonlinear_transformation(self, function: Callable[[np.ndarray], np.ndarray], **kwargs: Any) -> None:
def apply_function(self, function: MappingFunction, added_anims: list[Animation] = [], **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `function` | `Callable[[np.ndarray], np.ndarray]` | — | the point transform function: it takes `[x, y, z]` and **must return three components** `np.array([x', y', z'])` (don't drop `p[2]`); **accepts** any point-by-point function |
| `added_anims` | `list[Animation]` | `[]` | `apply_function` only: other animations played at the same time as the transform |
| `**kwargs` | `Any` | — | forwarded to `self.play`: `run_time` (the sample uses `1.6`) and so on |

> **Returns**: none (it plays the animation via `self.play` internally).

#### Sample: changing the nonlinear transformations

Two point-by-point functions played in a row: `swirl` (the further from the origin, the more it turns) and `squash` (flattening vertically with `tanh`, which keeps it bounded).

```python
import math
import numpy as np

from real_time_manim import LinearTransformationScene, Text, \
    UP, YELLOW, Wait
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   # instantly swap the top caption text without spending animation time
    cap.become(Text(text, font_size=26, color=YELLOW).to_edge(UP))

class NonlinearDemo(LinearTransformationScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # every apply_* calls self.play internally, so wire it to the window first
        cap = Text("", font_size=26, color=YELLOW)   # top caption text (content swapped later)
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(cap)   # add it to the scene
        self.add_unit_square(animate=False)   # add a unit square to make the bending more obvious

        def swirl(p):   # rotate by distance from the origin: the further out, the more it turns
            x, y = p[0], p[1]
            a = 0.5 * math.hypot(x, y)   # turn 0.5 radians more per unit of radius
            c, s = math.cos(a), math.sin(a)
            return np.array([x * c - y * s, x * s + y * c, p[2]])

        def squash(p):   # flatten vertically: the further from the x axis, the harder the squeeze
            return np.array([p[0], 3.0 * math.tanh(p[1] / 3.0), p[2]])   # tanh keeps it bounded

        say(cap, "apply_nonlinear_transformation(swirl)")
        self.apply_nonlinear_transformation(swirl, run_time=1.6)   # subdivide the plane first, then apply the function
        win.play(Wait(0.6))   # pause 0.6s

        say(cap, "apply_function(squash)")
        self.apply_function(squash, run_time=1.6)   # apply the function to every point directly
        win.play(Wait(0.6))   # pause 0.6s and finish
        win.close()   # close the RTM window
```

What this code does: it first puts a unit square on screen as a reference, then (1) `apply_nonlinear_transformation(swirl)` — every point turns `0.5 × radius` radians about the origin, so the whole grid spins into a whirlpool and the square is twisted into curved edges; (2) `apply_function(squash)` — the y coordinate passes through `3·tanh(y/3)`, so the further from the x axis the harder the squeeze (distant grid lines crowd into dense stripes while the centre stays as it was), and the square is flattened sideways.

<video src="assets/RTM output/05-LinearTransformationScene-nonlinear.mp4" controls width="560"></video>

> Note: the function signature is `p -> np.array([x', y', z'])`, and the return value **must have three components** (`p[2]` is the z component; just copy it across), returning two raises a shape error.
>
> `apply_nonlinear_transformation` subdivides the grid first (smoother lines, heavier frames), while `apply_function` goes point by point (good for gentle transforms like `squash`). Both act on the foreground grid, the basis vectors, the unit square and `moving_vectors` at the same time.

### add_title / get_unit_square / add_unit_square

```python
def add_title(self, title: str | MathTex | Tex, scale_factor: float = 1.5, animate: bool = False) -> Self:
def get_unit_square(self, color: ParsableManimColor | Iterable[ParsableManimColor] = PURE_YELLOW, opacity: float = 0.3, stroke_width: float = 3) -> Rectangle:
def add_unit_square(self, animate: bool = False, **kwargs: Any) -> Self:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `title` | `str \| MathTex \| Tex` | — | title content; a `str` goes through `Tex` typesetting and automatically gets a background bar and joins the foreground layer |
| `scale_factor` | `float` | `1.5` | scale for a `str` title only (ignored if it is already a `Mobject`); the title is fixed with `to_edge(UP)` to the **top of the frame** and presses on top content (which is why the caption text in sample 4 goes at the bottom) |
| `animate` | `bool` | `False` | with `True` it plays `Write` internally (under RTM set `self.play = win.play` first) |
| `color` | `ParsableManimColor \| Iterable[...]` | `PURE_YELLOW` | `get_unit_square` only: the square's color |
| `opacity` | `float` | `0.3` | `get_unit_square` only: fill opacity |
| `stroke_width` | `float` | `3` | `get_unit_square` only: stroke width |
| `**kwargs` | `Any` | — | `add_unit_square` only: forwarded to the animation (`run_time` and so on) |

> **Returns**: `add_title` / `add_unit_square` return `Self` (already in the scene and registered as transformable); `get_unit_square` only builds a `Rectangle`.

### add_vector / write_vector_coordinates / add_transformable_label

```python
def add_vector(self, vector: Arrow | Vector3DLike, color: ParsableManimColor | Iterable[ParsableManimColor] = PURE_YELLOW, animate: bool = False, **kwargs: Any) -> Arrow:
def write_vector_coordinates(self, vector: Vector, **kwargs: Any) -> Matrix:
def add_transformable_label(self, vector: Vector, label: MathTex | str, transformation_name: str | MathTex = "L", new_label: str | MathTex | None = None, **kwargs: Any) -> MathTex:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vector` | `Arrow \| Vector3DLike` | — | a coordinate list (such as `[2, 1]`) or a ready-made `Arrow`; registered in `moving_vectors` so `apply_*` transforms it along |
| `color` | `ParsableManimColor \| Iterable[...]` | `PURE_YELLOW` | `add_vector` only: vector color |
| `animate` | `bool` | `False` | `add_vector` only: unlike `VectorScene`, **no animation plays by default**; pass `True` for a `GrowArrow` entrance (sample 4) |
| `label` | `MathTex \| str` | — | `add_transformable_label` only: the label rewritten automatically on a transform (the `w` in the sample) |
| `transformation_name` | `str \| MathTex` | `"L"` | `add_transformable_label` only: the prefix after the rewrite, `w` → `L(w)` |
| `new_label` | `str \| MathTex \| None` | `None` (auto-builds `L(...)`) | `add_transformable_label` only: fully custom rewritten label |
| `label_scale_factor` | `float` | `0.8` | `add_transformable_label` only: label scale |
| `**kwargs` | `Any` | — | forwarded to `Arrow` / the animation / label creation |

> **Returns**: `add_vector` returns an `Arrow`; `write_vector_coordinates` returns a `Matrix` (a column matrix, also added to the foreground layer); `add_transformable_label` returns a `MathTex`.

#### Sample: changing the composition

The methods above are chained into one complete "linear algebra class": title → unit square → vector → coordinate matrix → rewritable label → rotate 90°, all linked together.

```python
from real_time_manim import LinearTransformationScene, Text, \
    UP, DOWN, YELLOW, Wait
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   # instantly swap the top caption text without spending animation time
    cap.become(Text(text, font_size=26, color=YELLOW).to_edge(UP))

def say_low(cap, text):   # for ComposeDemo only: put the caption at the bottom to make room for add_title at the top
    cap.become(Text(text, font_size=26, color=YELLOW).to_edge(DOWN))

class ComposeDemo(LinearTransformationScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # add_title / add_unit_square / add_vector call self.play internally, so wire it to the window first
        cap = Text("", font_size=26, color=YELLOW)   # put the caption at the bottom to make room for the title at the top
        cap.to_edge(DOWN)   # move the title to the bottom of the frame
        self.add(cap)   # add it to the scene

        say_low(cap, "add_title('Linear Transformation', animate=True)")
        self.add_title("Linear Transformation",   # the big top title (automatically gets a background bar and joins the foreground layer)
                       scale_factor=0.9, animate=True)   # with animate=True it plays Write internally
        win.play(Wait(0.7))   # pause 0.7s

        say_low(cap, "add_unit_square(animate=True)")
        self.add_unit_square(animate=True)   # draw the unit square (DrawBorderThenFill)
        win.play(Wait(0.5))   # pause 0.5s

        say_low(cap, "add_vector([2, 1], color=YELLOW, animate=True)")
        v = self.add_vector([2, 1], color=YELLOW, animate=True)   # add a vector and register it in moving_vectors
        win.play(Wait(0.6))   # pause 0.6s

        say_low(cap, "write_vector_coordinates(v)")
        self.write_vector_coordinates(v)   # write the column-matrix coordinates
        win.play(Wait(0.6))   # pause 0.6s

        say_low(cap, "add_transformable_label(v, 'w', ...)")
        self.add_transformable_label(v, "w",   # a label rewritten automatically on a transform
                                     transformation_name="L",
                                     label_scale_factor=0.8)
        win.play(Wait(0.6))   # pause 0.6s

        say_low(cap, "apply_matrix([[0, -1], [1, 0]])  rotate 90°")
        self.apply_matrix([[0, -1], [1, 0]], run_time=1.4)   # rotate 90°: the square turns vertical, the label is rewritten with the matrix
        win.play(Wait(0.7))   # pause 0.7s and finish
        win.close()   # close the RTM window
```

What this code does: the whole clip demonstrates "how one set of teaching elements links together".

- (1) `add_title(..., animate=True)` `Write`s the big title at the top (with a background bar automatically)
- (2) `add_unit_square(animate=True)` draws the unit square
- (3) `add_vector([2, 1], animate=True)` grows the yellow vector out with `GrowArrow` and registers it in `moving_vectors`
- (4) `write_vector_coordinates(v)` writes the column matrix `★[2, 1]` beside it
- (5) `add_transformable_label(v, "w", ...)` adds a label that is rewritten with the transform
- (6) `apply_matrix` rotates 90° — the square turns vertical, the vector points up and to the left, the `w` label is rewritten to `L(w)`, and the coordinate matrix stays put (the foreground layer does not take part in the transform)

<video src="assets/RTM output/05-LinearTransformationScene-compose.mp4" controls width="560"></video>

> Note: `add_title` is fixed to the **top** of the frame, so this sample puts its caption text at the bottom (`say_low`) — make room for the title the same way in your own scenes.
>
> In `LinearTransformationScene`, `add_vector` **defaults to `animate=False`** (the opposite of `VectorScene`'s `True`), so pass it explicitly for an entrance animation.
>
> The label rewrite happens while `apply_*` plays (at the end of the video `w` → `L(w)`); the column matrix is on the foreground layer and **does not move with the transform**, which is deliberate (the coordinate values are the pre-transform ones).

---

See also: [VectorScene](04-VectorScene.md), [ThreeDScene](02-ThreeDScene.md), [Scene Basics](../Scenes/01-Scene-Basics.md)
