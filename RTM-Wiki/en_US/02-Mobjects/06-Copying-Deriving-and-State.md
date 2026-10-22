# Copying, Deriving and State

This section covers copying objects, turning one object into another, saving and restoring state, and the interpolation and alignment interfaces behind `Transform`.

Of these methods, apart from `copy` (which returns a new object) and `generate_target` (which returns `self.target`), all return self and can be chained.

## Parameters

### copy

```python
def copy() -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| (no parameters) | — | — | a deep copy (including all submobjects and styles) |

> **Returns**: a new, independent object. The new copy **does not appear in the scene automatically** — `self.add(...)` it by hand or hand it to an animation; later changes to the original do not affect the copy.

#### Sample: a deep copy leaves the two independent

A blue square is copied into a red twin and the original then turns green — the twin stays red, proving the two are completely independent.

```python
from real_time_manim import Scene, Square, \
    BLUE, RED, GREEN, LEFT, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class CopyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.4, fill_opacity=0.6).shift(LEFT * 3.5)   #the original
        self.add(sq)   #add to the scene
        twin = sq.copy()   #deep copy: an independent copy that does not enter the scene automatically
        twin.set_color(RED).shift(RIGHT * 2.0)   #recolor the copy and move it away: independent of the original
        self.add(twin)   #add the copy to the scene
        win.play(FadeIn(twin), run_time=0.5)   #fade the copy in
        win.play(sq.animate.set_color(GREEN), run_time=0.5)   #recolor the original: the copy does not move at all
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: the blue square on the left first `copy()`s a twin, which is immediately recolored red and moved to the right before entering the scene (`copy` itself does not enter the scene).

Then the **original** plays a turn-green animation — the copy on the right does not move at all and stays red. That is what "deep copy" means: vertices, colors and submobjects are all independent, so changing one never affects the other.

<video src="assets/RTM output/06-Copying-Deriving-and-State-copy.mp4" controls width="560"></video>

> Note: `copy` is a **deep** copy, so the copy also clones any updaters, so remember to `clear_updaters` before using it.
>
> For "two identical copies that change in sync" use a reference / `VGroup`; use `copy` only when you need independent changes.

### become

```python
def become(mobject: Mobject, match_height: bool = False, match_width: bool = False,
           match_depth: bool = False, match_center: bool = False,
           stretch: bool = False) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | target shape |
| `match_height` / `match_width` / `match_depth` | `bool` | `False` | keep **its own** height/width/depth (scaling the target proportionally) |
| `match_center` | `bool` | `False` | keep its own centre position (otherwise it takes the target's position too) |
| `stretch` | `bool` | `False` | ignores the three `match_*` and **stretches the target along each of the three dimensions** to its own height/width/depth (distorts) |

> **Returns**: self. `become` changes the shape **instantly** — calling it directly gives no transition; only with `.animate` do you get an animation.

#### Sample: `become`'s position and `stretch`

A circle first `become`s the rectangle on the right directly (shape and position both move over); then it `become`s the small circle on the left with `match_center=True, stretch=True` — the small circle is stretched into a 3.0×1.4 ellipse while the position stays put.

```python
from real_time_manim import Scene, Circle, Rectangle, \
    ORANGE, PURPLE, TEAL, RIGHT, LEFT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class BecomeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        circ = Circle(radius=0.9, color=ORANGE, fill_opacity=0.7)   #circle
        self.add(circ)   #add to the scene
        rect = Rectangle(width=3.0, height=1.4, color=PURPLE, fill_opacity=0.7).shift(RIGHT * 3.2)   #the target rectangle is on the right
        win.play(circ.animate.become(rect), run_time=0.6)   #shape and position both turn into the target's
        print("after become: width =", round(circ.width, 2), "position =", circ.get_center().round(2))   #3.0, it has moved to the right
        dot = Circle(radius=0.3, color=TEAL).shift(LEFT * 3.2)   #the target small circle is on the left
        win.play(circ.animate.become(dot, match_center=True, stretch=True),
                 run_time=0.5)   #stretch pulls the target to its own 3.0×1.4 (small circle → ellipse), match_center keeps the position put
        print("after stretch+center:", round(circ.width, 2), round(circ.height, 2), circ.get_center().round(2))   #3.0 1.4, position unchanged
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: the orange circle's first `become(rect)` — vertices and color are all swapped for the purple rectangle on the right, and even the **position** moves over (console `width=3.0`, the centre has moved to the right).

The second call combines `match_center=True, stretch=True`: `stretch` stretches the target small circle into an ellipse along **its own current 3.0×1.4**, while `match_center` pins the position in place — so the small circle target on the left becomes a teal ellipse sitting in the upper right.

<video src="assets/RTM output/06-Copying-Deriving-and-State-become.mp4" controls width="560"></video>

> Note: with `stretch=True` **all three dimensions** are pulled to match its own, and the three `match_*` no longer take effect (in the source the `stretch` branch overwrites them outright); without `stretch`, `match_*` scales the target **proportionally**.
>
> Calling `become` directly is an instant jump; for a transition write `animate.become(...)` or `Transform`.

### save_state / restore

```python
def save_state() -> Self
def restore() -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| (neither takes parameters) | — | — | the former saves position/size/color/structure into `self.saved_state`; the latter restores with `become(saved_state)` |

> **Returns**: self. Calling `restore` without a prior save raises; you can `save_state` repeatedly to overwrite the snapshot.

#### Sample: saving and restoring

The square in the upper left first `save_state`s, then is scaled up, turned green and moved right, and `animate.restore()` takes it all the way back to the saved state.

```python
from real_time_manim import Scene, Square, \
    BLUE, GREEN, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class SaveRestoreDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.4, fill_opacity=0.7).shift(LEFT * 3.0)   #blue square
        self.add(sq)   #add to the scene
        sq.save_state()   #save position/size/color/structure into saved_state
        win.play(sq.animate.scale(1.8).set_color(GREEN).shift(RIGHT * 3.0), run_time=0.7)   #scale up, turn green, move right
        win.play(sq.animate.restore(), run_time=0.6)   #restore to the state at save time
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: the blue square on the left first `save_state()`s the whole set — "position, size, color, vertex structure"; then in one go it is scaled 1.8×, turned green and moved right by 3 (three changes stacked on the same `animate` chain); finally `sq.animate.restore()` plays the restore animation — size, color and position all return to the instant it was saved. This is the standard "go out and play, then come home in one click" pattern.

<video src="assets/RTM output/06-Copying-Deriving-and-State-save_restore.mp4" controls width="560"></video>

> Note: `save_state` is a **reference-style snapshot** (`become` semantics), so structural changes are restored too; `restore()` with no snapshot raises outright, so don't gamble on it inside a conditional branch. Multiple `save_state` calls overwrite the old snapshot; for multiple slots, keep several copies yourself.

### generate_target

```python
def generate_target(use_deepcopy: bool = False) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `use_deepcopy` | `bool` | `False` | `True` uses `deepcopy`; the default uses `copy()` |

> **Returns**: the `self.target` snapshot itself (not self!). Combine it with a `MoveToTarget` animation to "turn the object into it" — the target state can change anything: position, size, color, submobjects.

#### Sample: `generate_target` + `MoveToTarget`

A yellow square generates a target snapshot; the snapshot is moved right, scaled up and recolored, and `MoveToTarget` plays the animation of the object turning into it.

```python
from real_time_manim import Scene, Square, \
    YELLOW, TEAL, LEFT, RIGHT, MoveToTarget
from real_time_manim.vulkan_bind import MLWindow, Wait

class TargetDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=YELLOW, side_length=1.2).shift(LEFT * 3.5)   #yellow square
        self.add(sq)   #add to the scene
        sq.generate_target(use_deepcopy=False)   #generate the self.target snapshot (the object itself does not disappear)
        sq.target.shift(RIGHT * 3.0).scale(1.6).set_color(TEAL)   #arrange the target shape on the snapshot
        win.play(MoveToTarget(sq), run_time=0.7)   #animate the object to the target shape
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: after `generate_target()` the yellow square holds an extra `self.target` snapshot (the object itself is still on screen); make any changes you like directly on the **snapshot** — move it right by 3, scale it 1.6×, recolor it teal; finally `MoveToTarget(sq)` plays the animation of the object "transitioning toward the target state". It is more intuitive than `Transform(object, copy)`: the target state is just a snapshot you edit freely.

<video src="assets/RTM output/06-Copying-Deriving-and-State-target.mp4" controls width="560"></video>

> Note: `generate_target` returns `self.target`, not self (assigning it directly would swap out your object), so be careful with chained writes. `use_deepcopy=True` goes further (including immutable attributes); the default `copy()` is usually enough.

### interpolate

```python
def interpolate(mobject1: Mobject, mobject2: Mobject, alpha: float,
                path_func: PathFuncType = straight_path()) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject1` / `mobject2` | `Mobject` | — | start state / end state |
| `alpha` | `float` | — | 0 = start, 1 = end |
| `path_func` | callable | `straight_path()` | the interpolation path; for an arc use the `arc_path` family |

> **Returns**: self. The layer under `Transform`: it turns the object **instantly** into the interpolated state of the two states at `alpha`. All three **must have the same point count** (usually produce the states with `copy`).

#### Sample: taking an interpolated state by hand

A green square keeps one copy each of its start and end states; `interpolate(s1, s2, 0.5)` takes the mid state instantly, then `become(s2)` compares against the end.

```python
from real_time_manim import Scene, Square, \
    GREEN, RIGHT, PI, straight_path
from real_time_manim.vulkan_bind import MLWindow, Wait

class InterpolateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=GREEN, side_length=1.2)   #green square
        self.add(sq)   #add to the scene
        win.play(Wait(0.4))   #see the start state
        s1 = sq.copy()   #start state
        s2 = sq.copy().shift(RIGHT * 2.5).scale(1.5).rotate(PI / 4)   #end state
        sq.interpolate(s1, s2, 0.5, path_func=straight_path())   #take the interpolated state at alpha=0.5 directly (instantly)
        win.play(Wait(0.5))   #see the mid state
        win.play(sq.animate.become(s2), run_time=0.4)   #then animate to the end state for comparison
        win.play(Wait(0.3))   #wait 0.3s
        win.close()   #close the RTM window
```

What this code does: the green square in the middle of the canvas first pauses for 0.4 s (the start), then two `copy`s define the start and end states (moved right 2.5, scaled 1.5×, rotated 45°); `interpolate(s1, s2, 0.5, straight_path())` **instantly** places it exactly halfway — position/size/angle all right at the midpoint; finally `animate.become(s2)` animates it to the end, making the positional difference between the "mid state" and the "end state" easy to compare.

<video src="assets/RTM output/06-Copying-Deriving-and-State-interpolate.mp4" controls width="560"></video>

> Note:
>
> - `interpolate` is an **instant** function (it lands in a single frame); for a continuous transition hand it to `Transform` / `MoveToTarget`, which call it once per frame.
> - A point-count mismatch between the three raises an error — call `align_points` before interpolating across shapes (see below).
> - `alpha` may go beyond 0–1 (extrapolation), but that is generally not recommended.

### match_dim_size / match_width / match_height / match_depth

```python
def match_dim_size(mobject: Mobject, dim: int, **kwargs: Any) -> Self
def match_width(mobject: Mobject, **kwargs: Any) -> Self
def match_height(mobject: Mobject, **kwargs: Any) -> Self
def match_depth(mobject: Mobject, **kwargs: Any) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the reference object |
| `dim` | `int` | — | `match_dim_size` only: `0` width, `1` height, `2` depth |
| `**kwargs` | `Any` | — | passed through to `rescale_to_fit`, such as `stretch=True` |

> **Returns**: self. By default it scales **proportionally** to the same size as the reference (`match_width` changes width and height together); `stretch=True` adjusts only that dimension.

#### Sample: proportional vs. stretched matching

A grey rectangle acts as the ruler: the blue square's `match_width` scales proportionally to the same width (the height follows to 2.6); the red square's `match_dim_size(ref, 1, stretch=True)` squashes only the height to match.

```python
from real_time_manim import Scene, Rectangle, Square, \
    BLUE, RED, GREY, UP, LEFT
from real_time_manim.vulkan_bind import MLWindow, Wait

class MatchSizeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        ref = Rectangle(width=2.6, height=1.0, color=GREY, fill_opacity=0.5).shift(UP * 1.6)   #the reference rectangle
        m1 = Square(color=BLUE, side_length=1.0).shift(LEFT * 3.0)   #the proportional comparison
        m2 = Square(color=RED, side_length=1.8).shift(LEFT * 1.0)   #the stretched comparison
        self.add(ref, m1, m2)   #add to the scene
        win.play(m1.animate.match_width(ref), run_time=0.5)   #scale proportionally to the reference's width
        print("after match_width:", round(m1.width, 2), round(m1.height, 2))   #2.6 2.6
        win.play(m2.animate.match_dim_size(ref, 1, stretch=True), run_time=0.5)   #match_dim_size: dim=1, squash only this dimension
        print("after match_dim_size:", round(m2.width, 2), round(m2.height, 2))   #1.8 1.0
        m2.match_depth(ref)   #match_depth: a safe no-op for flat objects (all dimension lengths are 0)
        print("after match_depth:", round(m2.width, 2), round(m2.height, 2))   #unchanged
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: a grey rectangle (2.6×1.0) acts as the ruler.

- The blue square's `match_width(ref)` scales **proportionally** to width 2.6, so the height becomes 2.6 too (console `2.6 2.6`).
- The red square's `match_dim_size(ref, 1, stretch=True)` — `dim=1` means height and `stretch=True` squashes only that dimension, turning the 1.8 square into a flat 1.8×1.0 bar.
- Finally `match_depth` is a safe no-op for flat objects (the width is unchanged).

<video src="assets/RTM output/06-Copying-Deriving-and-State-match_size.mp4" controls width="560"></video>

> Note: this family is the "use someone else as the ruler" version of `rescale_to_fit` — `match_width` is equivalent to `rescale_to_fit(reference.width, 0)`. `match_width` / `match_height` are proportional by default; to force a single dimension you must pass `stretch=True` explicitly.

### match_coord / match_x / match_y / match_z / match_points / align_points

```python
def match_coord(mobject: Mobject, dim: int, direction: Vector3DLike = ORIGIN) -> Self
def match_x(mobject: Mobject, direction: Vector3DLike = ORIGIN) -> Self
def match_y(mobject: Mobject, direction: Vector3DLike = ORIGIN) -> Self
def match_z(mobject: Mobject, direction: Vector3DLike = ORIGIN) -> Self
def match_points(mobject: Mobject, copy_submobjects: bool = True) -> Self
def align_points(mobject: Mobject) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the reference object |
| `dim` | `int` | — | `match_coord` only: `0`/`1`/`2` |
| `direction` | vector | `ORIGIN` | which key point of its own to align by (`DOWN` = align the bottom edge) |
| `copy_submobjects` | `bool` | `True` | a parameter kept for signature compatibility |

> **Returns**: self. `match_coord` sets its own key point coordinate along one dimension to the reference's (`match_x` and friends are sugar for it); `match_points` **copies the vertices outright** (shape and size both take on the reference's); `align_points` only aligns the **vertex count** (a prerequisite of `Transform` interpolation) without changing the visible appearance.

#### Sample: coordinate matching, vertex copying and point-count alignment

A grey circle acts as the reference: the blue square's `match_x` (align x), the red square's `match_coord(ref, 1, direction=DOWN)` (align the bottom edge); the small circle's `match_points(ref)` turns it into the same circle as the reference, then `align_points` prints both point counts.

```python
from real_time_manim import Scene, Circle, Square, \
    BLUE, RED, TEAL, GREY, UP, DOWN, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class MatchPosDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        ref = Circle(radius=0.8, color=GREY, fill_opacity=0.5).shift(UP * 1.5 + RIGHT * 2.0)   #the reference circle
        m1 = Square(color=BLUE, side_length=1.0).shift(LEFT * 3.5 + DOWN * 1.5)   #the x-alignment comparison
        m2 = Square(color=RED, side_length=1.0).shift(LEFT * 1.5 + DOWN * 1.5)   #the y-edge-alignment comparison
        self.add(ref, m1, m2)   #add to the scene
        win.play(m1.animate.match_x(ref), run_time=0.5)   #match_x: align x to the reference's centre
        win.play(m2.animate.match_coord(ref, 1, direction=DOWN), run_time=0.5)   #match_coord: dim=1, align by the bottom edge
        print("ref centre =", ref.get_center().round(2), "| m1 centre =", m1.get_center().round(2))   #x is the same
        mp = Circle(color=TEAL, radius=0.4).shift(LEFT * 3.5 + UP * 1.5)   #the circle to be reshaped
        self.add(mp)   #add to the scene
        win.play(mp.animate.match_points(ref), run_time=0.5)   #match_points: copy the reference's vertices outright (shape and size both change)
        print("after match_points width =", round(mp.width, 2))   #1.6, matching the reference
        mp.align_points(ref)   #align_points: align the vertex counts (a prerequisite of interpolation)
        print("points after align_points =", mp.get_num_points(), ref.get_num_points())   #both the same
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: the grey circle in the upper right acts as the reference.

- The blue square's `match_x(ref)` moves x only to match the circle's centre (y does not move).
- The red square's `match_coord(ref, 1, direction=DOWN)` aligns y using the `DOWN` key point — its **bottom edge** lines up with the circle's lower rim (the console prints both centres' x/y for checking).
- The small circle in the upper left has only half the reference's radius, and `match_points(ref)` copies the reference's **vertex array** over wholesale, so the small circle instantly becomes the same circle as the reference (width 1.6).
- `align_points(ref)` aligns the vertex counts on both sides, printing 32 points each — exactly what `Transform` does before interpolating across shapes.

<video src="assets/RTM output/06-Copying-Deriving-and-State-match_pos.mp4" controls width="560"></video>

> Note:
>
> - `match_coord` aligns the coordinate of **one dimension**, not the whole position.
> - `match_points` copies **all vertices** (everything outside the color structure), so a circle takes on the other's circle exactly.
> - `align_points` only guarantees matching point counts; the appearance may flash a fill mismatch in between, so it is generally only used as a pre-step for animations.

---

See also: [animate Syntax](07-animate-Syntax.md) | [Updaters](08-Updaters.md)
