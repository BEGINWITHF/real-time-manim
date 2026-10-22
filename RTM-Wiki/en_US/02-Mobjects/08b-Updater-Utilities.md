# Updater utilities (module level)

Module-level convenience functions provided by `manim.animation.updaters`: redraw in one line, steady translation/rotation, and turning an animation into an updater.

## Parameters

### always_redraw

```python
def always_redraw(func: Callable[[], M]) -> M
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `func` | callable with no parameters | — | a factory function returning a new `Mobject` |

> **Returns**: the `Mobject` with its updater already attached (that is, the first result of `func()`); just `self.add(...)` it. The standard way to have a `ValueTracker` drive "a shape that depends on the current value" — each frame the factory is re-run and its result `become`d.

#### Sample: a dot on a track

A `ValueTracker` moves along a track and `always_redraw` redraws a dot from the current value each frame — the dot's position follows the number in real time.

```python
from real_time_manim import Scene, Line, Dot, ValueTracker, \
    RED, GREY, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim import always_redraw

class AlwaysRedrawDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        alpha = ValueTracker(0.0)   #value tracker
        track = Line(LEFT * 3.0, RIGHT * 3.0, color=GREY)   #a piece of track
        self.add(track)   #add to the scene
        bead = always_redraw(lambda: Dot(color=RED, radius=0.12).move_to(LEFT * 3.0 + alpha.get_value() * RIGHT))   #redraw the dot from the current value every frame
        self.add(bead)   #add to the scene (the return value is the object with its updater attached)
        win.play(alpha.animate.set_value(6.0), run_time=1.0)   #drive the tracker: the dot travels steadily along the track
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: the grey track runs from `x=-3` to `x=+3`; while the `ValueTracker` animates from 0 to 6, `always_redraw(lambda: Dot(...))` builds a brand-new dot **every frame** — its position is computed from `alpha.get_value()` and `become`d onto the old dot.

The effect is a red dot sliding steadily along the track: the number changes and the shape is always computed and drawn on the spot. This is the standard posture for "a shape that depends on some changing value".

<video src="assets/RTM output/08b-Updater-Utilities-always_redraw.mp4" controls width="560"></video>

> Note: the factory function must return a **new object** and runs every frame — so do not put heavy work in it (such as constructing a `Text` each time).
>
> The object from `always_redraw` can also go straight into a `play` animation (such as `TransformFromCopy`); internally it is just `add_updater` + `become`.

### always / f_always (module-level functions)

```python
def always(method: Callable, *args, **kwargs) -> Mobject
def f_always(method: Callable[[M], None], *arg_generators, **kwargs) -> M
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `method` | bound method | — | must be a method on a `Mobject` instance, otherwise the assertion fails |
| `*args` | any | — | fixed parameters, evaluated once at attach time (`always` only) |
| `*arg_generators` | callables with no parameters | — | argument generators called once per frame and then passed to the target method (`f_always` only) |

> **Returns**: the `Mobject` the method belongs to. Same name as the `Mobject.always` property but **a different thing**; `always`'s parameters are evaluated once at attach time while `f_always`'s are evaluated every frame — the only difference between the two.

#### Sample: one following label per line

`always(tag.next_to, sq, UP, ...)` keeps the yellow label permanently above the square; `f_always(tag2.next_to, lambda: sq, lambda: DOWN, ...)` uses argument generators to keep the green label below.

```python
from real_time_manim import Scene, Square, Text, \
    BLUE, YELLOW, GREEN, UP, DOWN, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim import always, f_always

class AlwaysFnDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.2).shift(LEFT * 3.0)   #blue square
        self.add(sq)   #add to the scene
        tag = Text("always", font_size=24, color=YELLOW)   #the upper label
        always(tag.next_to, sq, UP, buff=0.3)   #always: parameters evaluated once at attach time (the reference keeps working)
        self.add(tag)   #add to the scene
        tag2 = Text("f_always", font_size=24, color=GREEN)   #the lower label
        f_always(tag2.next_to, lambda: sq, lambda: DOWN, buff=0.3)   #f_always: the argument generators are re-evaluated every frame
        self.add(tag2)   #add to the scene
        win.play(sq.animate.shift(RIGHT * 2.5), run_time=0.8)   #the two labels, one above and one below, follow the whole time
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: the yellow label above the blue square is attached with `always(tag.next_to, sq, UP, buff=0.3)` — the parameter `sq` is a reference, so evaluating it once at attach time is enough (its position is read afresh on every run).

The green label below uses `f_always`, with the reference written as `lambda: sq` and the direction as `lambda: DOWN`, each called once per frame before being passed.

During the 0.8 s the square moves right, the two labels follow above and below the whole way — either works day to day, but when you need "a different reference / direction every frame" only `f_always` can do it.

<video src="assets/RTM output/08b-Updater-Utilities-always_fn.mp4" controls width="560"></video>

> Note:
>
> - What `always` takes must be a **bound method** (`tag.next_to`, not `Tag.next_to`); passing it wrongly makes `assert_is_mobject_method` raise `AssertionError`.
> - The parameters hold the value from the moment of attaching — use `f_always` for values that change.
> - It and the `Mobject.always` property (see [Updaters](08-Updaters.md)) are two separate implementations with almost identical behaviour.

### always_shift / always_rotate

```python
def always_shift(mobject: M, direction: Vector3DLike = RIGHT, rate: float = 0.1) -> M
def always_rotate(mobject: M, rate: float = 20 * DEGREES, **kwargs) -> M
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the object being moved / rotated |
| `direction` | vector | `RIGHT` | the direction of translation (it is normalised, so the magnitude does not matter) |
| `rate` | `float` | `0.1` / `20 * DEGREES` | the distance moved per second / the angle turned per second |
| `**kwargs` | `Any` | — | `always_rotate` only: passed through to `Mobject.rotate` (such as `about_point=`) |

> **Returns**: that object. Each attaches a time-based updater — the object moves/rotates steadily **without knowing it**, is not `play`ed, and advances with the scene time; stop it with `clear_updaters()`. The sample also demonstrates `assert_is_mobject_method` (an argument-checking helper that confirms what was passed is a bound `Mobject` method; it returns `None`).

#### Sample: moving and rotating at once

A green triangle attaches both `always_shift` (move right 1 per second) and `always_rotate` (90° per second), moving and rotating at once for 1.2 s, and `clear_updaters()` stops both together.

```python
from real_time_manim import Scene, Triangle, \
    GREEN, UP, DOWN, LEFT, RIGHT, PI
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim import always_shift, always_rotate, assert_is_mobject_method

class AlwaysShiftRotateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        tri = Triangle(color=GREEN).set_fill(GREEN, opacity=1).scale(0.8).shift(DOWN * 1.5 + LEFT * 3.0)   #green triangle
        self.add(tri)   #add to the scene
        assert_is_mobject_method(tri.shift)   #argument-checking helper: confirm it is a bound method on a Mobject (returns None)
        print("assert_is_mobject_method -> None")
        always_shift(tri, direction=RIGHT, rate=1.0)   #steady translation right: 1.0 unit per second
        always_rotate(tri, rate=PI / 2)   #steady self-rotation: 90° per second
        win.play(Wait(1.2))   #moving and rotating at once
        tri.clear_updaters()   #stop both updaters together
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: the solid green triangle attaches `always_shift(direction=RIGHT, rate=1.0)` and `always_rotate(rate=PI / 2)` — two **independent** time-based updaters driving it at once, so during the 1.2-second `Wait` it slides 1.2 units to the right while turning clockwise by about 108°.

No `play`, no animation classes — everything is driven by the render loop each frame; `clear_updaters()` stops both. `assert_is_mobject_method(tri.shift)` demonstrates the argument checking these functions use internally (it returns `None`).

<video src="assets/RTM output/08b-Updater-Utilities-always_shift_rotate.mp4" controls width="560"></video>

> Note: several `always_*` calls stack (each is its own updater); `always_rotate` rotates about its own centre by default — add `about_point=` to rotate about somewhere else.
>
> For "go for a while, stop for a while" you have to attach/clear updaters yourself, or switch to an `animate` animation.

### turn_animation_into_updater / cycle_animation

```python
def turn_animation_into_updater(animation: Animation, cycle: bool = False,
                                delay: float = 0, **kwargs) -> Mobject
def cycle_animation(animation: Animation, **kwargs) -> Mobject
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `animation` | `Animation` | — | the animation to turn into an updater (**it does not go through `play`**) |
| `cycle` | `bool` | `False` | whether to loop forever (`cycle_animation` is shorthand for `cycle=True`) |
| `delay` | `float` | `0` | the seconds of delay before it starts |

> **Returns**: the `Mobject` the animation belongs to. It does not go through `play` and advances automatically with the scene time, removing its updater when it finishes (with `cycle=True` it keeps going forever until you `clear_updaters()` it by hand).

#### Sample: one full turn vs. turning forever

The left block's `turn_animation_into_updater(Rotate(..., angle=TAU), cycle=False)` stops by itself after one full turn; the right block's `cycle_animation(...)` keeps turning until it is stopped by hand.

```python
from real_time_manim import Scene, Square, \
    BLUE, ORANGE, UP, LEFT, RIGHT, TAU, Rotate
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim import turn_animation_into_updater, cycle_animation

class AnimUpdaterDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.0).shift(LEFT * 3.5 + UP * 1.5)   #left: ends after one full turn
        self.add(sq)   #add to the scene
        turn_animation_into_updater(Rotate(sq, angle=TAU), cycle=False, delay=0)   #turn the animation into an updater: it advances with the scene time
        win.play(Wait(0.9))   #watch it complete a full turn on its own
        sq2 = Square(color=ORANGE, side_length=1.0).shift(RIGHT * 3.5 + UP * 1.5)   #right: loops forever
        self.add(sq2)   #add to the scene
        cycle_animation(Rotate(sq2, angle=TAU))   #shorthand for cycle=True: it keeps turning forever
        win.play(Wait(0.9))   #watch it keep turning
        sq2.clear_updaters()   #stop it
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: the two squares each get one form of "turn an animation into an updater".

The left block's `Rotate` animation is **not** handed to `play`; instead `turn_animation_into_updater(...)` turns it into an updater — it rotates on its own with the scene time and ends automatically after one full turn (`TAU`). The right block uses `cycle_animation(...)` (i.e. `cycle=True`) to loop forever, so during the same 0.9 s it gets as far as it gets, and `clear_updaters()` finally stops it by hand.

Good for effects like "keep spinning/flashing in the background" that you do not want to occupy `play`.

<video src="assets/RTM output/08b-Updater-Utilities-anim_updater.mp4" controls width="560"></video>

> Note: once the animation object has been passed in, **do not `play` it yourself** (that would drive it twice); an animation with `cycle=True` must be stopped by hand.
>
> `delay=` staggers the start of several animation updaters.

---

See also: [Updaters](08-Updaters.md) | [Updater Animations](09-Updater-Animations.md) | [ValueTracker](10-ValueTracker.md)
