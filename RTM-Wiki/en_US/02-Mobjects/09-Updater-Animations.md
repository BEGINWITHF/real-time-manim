# Updater animation classes (played directly by `Scene.play`)

Three updater animations you can hand to `Scene.play`: callback-style animations with a beginning and an end.

## Parameters

### UpdateFromFunc

```python
def UpdateFromFunc(mobject: Mobject, update_function: Callable[[Mobject], Any],
                   suspend_mobject_updating: bool = False, **kwargs: Any) -> Animation
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the driven object (it appears in the scene during the animation) |
| `update_function` | `Callable[[Mobject], Any]` | — | the function `f(mob)` that receives `mobject` every frame |
| `suspend_mobject_updating` | `bool` | `False` | whether to pause the object's **existing** updater during the animation |
| `**kwargs` | `Any` | — | passed through to `Animation` (`run_time=`, `rate_func=`, …) |

> **Returns**: `Animation`. It repeatedly calls `update_function(mobject)` for the **whole duration** of the `play`. The difference from `add_updater`: it is a **finite animation** (it stops when `run_time` ends), while an updater stays mounted permanently.

#### Sample: a readout that follows the dot

A yellow dot crosses the screen. In the second play the dot moves back and `UpdateFromFunc(lab, follow)` keeps the label **right above the dot**, showing its x coordinate in real time — the callback stops as soon as the animation ends.

```python
from real_time_manim import Scene, Dot, DecimalNumber, \
    WHITE, YELLOW, UP, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim import UpdateFromFunc

class UpdateFromFuncDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        dot = Dot(color=YELLOW, radius=0.12).shift(LEFT * 4.0)   # yellow dot
        lab = DecimalNumber(0, num_decimal_places=2, color=WHITE).scale(0.7)   # readout label
        lab.to_edge(UP, buff=0.5)   # put it at the top first
        self.add(dot, lab)   # add to the scene

        def follow(m):   # called every frame during the animation: pin the label above the dot and show the dot's x coordinate
            m.move_to(dot.get_center() + UP * 1.2)
            m.set_value(round(float(dot.get_x()), 2))

        win.play(dot.animate.shift(RIGHT * 8.0), run_time=1.2)   # the dot crosses the screen (label not attached yet)
        win.play(UpdateFromFunc(lab, follow), dot.animate.shift(LEFT * 8.0), run_time=1.2)   # drive the label every frame for the whole animation
        win.play(Wait(0.3))   # pause 0.3s
        win.close()   # close the RTM window
```

What this code does: the yellow dot first crosses the screen on its own (the label is still pinned to the top and does not move).

The second `play` runs two animations at once — the dot moves back while `UpdateFromFunc(lab, follow)` calls `follow` every frame for the **whole 1.2 seconds**, moving the label above the dot and writing out its x coordinate (the number scrolls in real time).

As soon as `run_time` is up the callback stops automatically and the label stays where the last frame left it.

<video src="assets/RTM output/09-Updater-Animations-update_func.mp4" controls width="560"></video>

> Note: pick one of the two with `add_updater` — for "follow forever" use an updater, for "follow only during one animation" use `UpdateFromFunc`.
>
> The driven object is added to the scene automatically (no need to `add` it first); `suspend_mobject_updating=True` suppresses its own updater during the callback so they don't fight.

### UpdateFromAlphaFunc

```python
def UpdateFromAlphaFunc(mobject: Mobject, update_function: Callable[[Mobject, Any], Any],
                        suspend_mobject_updating: bool = False, **kwargs: Any) -> Animation
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the driven object |
| `update_function` | `Callable[[Mobject, Any], Any]` | — | signature is `func(mobject, alpha)`, where `alpha` is the 0→1 progress after `rate_func` |
| `suspend_mobject_updating` | `bool` | `False` | whether to pause the object's existing updater during the animation |
| `**kwargs` | `Any` | — | passed through to `Animation` |

> **Returns**: `Animation`. A subclass of `UpdateFromFunc` for custom animations that **interpolate exactly by progress** — the callback gets an extra `alpha`, so it can do **deterministic** transforms such as colour gradients and position mapping.

#### Sample: interpolating by progress

A blue square moves from the centre to the right over 1 second while its colour interpolates from blue to red by `alpha` — the progress itself comes from the `alpha` argument and is a definite value on every frame.

```python
from real_time_manim import Scene, Square, \
    BLUE, RED, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim import UpdateFromAlphaFunc, interpolate_color

class UpdateAlphaDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.2, fill_opacity=0.7)   # blue square
        self.add(sq)   # add to the scene
        start = sq.get_center().copy()   # remember the start point

        def morph(m, alpha):   # interpolate by progress: colour blue→red, move right
            m.set_color(interpolate_color(BLUE, RED, alpha))
            m.move_to(start + alpha * RIGHT * 3.0)

        win.play(UpdateFromAlphaFunc(sq, morph, suspend_mobject_updating=False), run_time=1.0)   # alpha goes 0→1 after rate_func
        win.play(Wait(0.3))   # pause 0.3s
        win.close()   # close the RTM window
```

What this code does: the `alpha` that the square's `morph(m, alpha)` receives is the **progress after `rate_func`** (by default ease-in-out, 0→1) — the colour interpolates linearly via `interpolate_color(BLUE, RED, alpha)` and the position maps linearly via `start + alpha * RIGHT * 3.0`.

During the 1-second animation the two stay strictly in step: halfway through, the colour is exactly half-way to purple. This is the shortest route to "driving several attributes from one callback".

<video src="assets/RTM output/09-Updater-Animations-update_alpha.mp4" controls width="560"></video>

> Note:
>
> - `alpha` has already gone through `rate_func` — pass `rate_func=linear` for constant speed.
> - What the callback does **must be a pure function of alpha** (the same alpha gives the same state), otherwise playback will jump between repeated frames.
> - Incremental transforms (such as rotating 5° per frame) should use `UpdateFromFunc` + `dt` or an updater.

### MaintainPositionRelativeTo

```python
def MaintainPositionRelativeTo(mobject: Mobject, tracked_mobject: Mobject,
                               **kwargs: Any) -> Animation
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the object whose relative position is kept |
| `tracked_mobject` | `Mobject` | — | the reference object being tracked |
| `**kwargs` | `Any` | — | passed through to `Animation` |

> **Returns**: `Animation`. Keeps `mobject`'s position relative to `tracked_mobject` during the animation (the initial offset is recorded and followed every frame).

#### Sample: a satellite and its reference

A small purple circle first sits above a green square; playing `MaintainPositionRelativeTo(sat, ref)` together with a rightward shift of the square keeps the offset, so the circle travels along like a satellite.

```python
from real_time_manim import Scene, Square, Circle, \
    GREEN, PURPLE, UP, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim import MaintainPositionRelativeTo

class MaintainDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        ref = Square(color=GREEN, side_length=1.0, fill_opacity=0.6).shift(LEFT * 3.5)   # reference square
        sat = Circle(color=PURPLE, radius=0.35)   # satellite
        sat.next_to(ref, UP, buff=0.25)   # snap it above the reference first: this is the relative position to keep
        self.add(ref, sat)   # add to the scene
        win.play(MaintainPositionRelativeTo(sat, ref), ref.animate.shift(RIGHT * 7.0), run_time=1.2)   # the relative position stays: they move together
        win.play(Wait(0.3))   # pause 0.3s
        win.close()   # close the RTM window
```

What this code does: the purple circle first uses `next_to` to sit right above the green square — that initial offset is the "relative position" that gets remembered.

In the same `play` the square moves 7 units to the right and `MaintainPositionRelativeTo(sat, ref)` keeps the purple circle in sync with that offset every frame, so it looks like a satellite flying along with the square. When `run_time` ends the binding is released and the circle stays where it is.

<video src="assets/RTM output/09-Updater-Animations-maintain.mp4" controls width="560"></video>

> Note: the relative position is recorded **when the animation starts** — set the positions up before playing.
>
> After the animation ends the binding is released automatically (it is not a permanent follow); for a permanent follow use `add_updater(lambda m: m.move_to(ref.get_center() + offset))` or `always`.

---

See also: [Updaters](08-Updaters.md) | [Updater Utilities](08b-Updater-Utilities.md) | [ValueTracker](10-ValueTracker.md)
