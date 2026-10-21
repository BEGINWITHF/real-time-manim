# ValueTracker: animatable numbers

`ValueTracker` is an **invisible** "number container" that encodes a value in vertex coordinates, so it can be animated with `.animate` and read by an updater.

It is the hub that plugs changing parameters into animations.

## Parameters

### ValueTracker constructor

```python
def ValueTracker(value: float = 0, **kwargs: Any) -> None
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `value` | `float` | `0` | initial value |
| `**kwargs` | `Any` | — | passed through to `Mobject.__init__` |

> **Returns**: a new `ValueTracker` instance.
>
> **Usage notes**: to drive it with an updater you **must `self.add(tracker)`** (otherwise the scene won't advance it); to change the value through playback use `win.play(tracker.animate.set_value(...))`; you can also change it instantly with `tracker += 1.5` (no animation). It does not display anything itself — to draw the number use `DecimalNumber` + an updater or `always_redraw`.

### get_value / set_value / increment_value

```python
def get_value() -> float
def set_value(value: float) -> Self
def increment_value(d_value: float) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `value` | `float` | — | target value (`set_value` only) |
| `d_value` | `float` | — | increment, may be negative (`increment_value` only) |

> **Returns**: `get_value` returns a `float`; the other two return the object itself and can be chained. Read / set / add to the current value.

#### Sample: setting values, arithmetic and the `+=` trap

A readout at the top shows the tracker's value in real time: animate 0→5, animate -2, `+= 2` to change instantly; then various arithmetic results are printed (all of them **new objects**).

```python
from real_time_manim import Scene, DecimalNumber, ValueTracker, \
    YELLOW, UP
from real_time_manim.vulkan_bind import MLWindow, Wait

class BasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        tracker = ValueTracker(0.0)   # initial value 0
        lbl = DecimalNumber(0, num_decimal_places=2, color=YELLOW).scale(0.8).to_edge(UP, buff=0.5)   # readout label
        lbl.add_updater(lambda d: d.set_value(round(float(tracker.get_value()), 2)))   # read the value every frame and display it
        self.add(lbl, tracker)   # tracker must be added to the scene to be driven
        win.play(tracker.animate.set_value(5.0), run_time=0.8)   # animated value change: 0 → 5
        win.play(tracker.animate.increment_value(-2.0), run_time=0.6)   # animated increment: -2
        tracker += 2.0   # change the value in place instantly (the += in-place version)
        print("after += :", tracker.get_value())   #5.0
        print("(tracker * 3).get_value() =", (tracker * 3).get_value())   #* → a new object, the original is unchanged
        print("- / / / // / % / ** =", (tracker - 1).get_value(), (tracker / 2).get_value(), (tracker // 2).get_value(), (tracker % 2).get_value(), (tracker ** 2).get_value())   #each arithmetic operator → a new ValueTracker
        print("bool(tracker) =", bool(tracker))   #bool is equivalent to bool(get_value())
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: the readout label calls `get_value()` every frame to show the current value, so the two animations (0→5, then -2) appear as a scrolling number; then `tracker += 2.0` changes the value **in place** instantly — the number jumps from 3.0 to 5.0 within one frame. The console prints verify the arithmetic: `tracker * 3`, `tracker - 1`, `/ // % **` all return a **new** `ValueTracker` (the original still holds 5.0), and `bool(tracker)` is equivalent to `bool(get_value())`.

<video src="assets/RTM output/10-ValueTracker-basic.mp4" controls width="560"></video>

> Note: `tracker += 1.5` and `tracker = tracker + 1.5` mean completely different things: the former modifies the original object **in place** (the attached updater still references it), the latter swaps in a new object — old references keep reading the old value, which is the most common "the number won't move" accident.
>
> The most common idiom is `tracker += dt` inside a time-based updater.

### interpolate

```python
def interpolate(mobject1: Mobject, mobject2: Mobject, alpha: float,
                path_func: PathFuncType = straight_path()) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject1` / `mobject2` | `Mobject` | — | start / end state (usually temporary `ValueTracker`s) |
| `alpha` | `float` | — | 0 = start, 1 = end |
| `path_func` | callable | `straight_path()` | interpolation path |

> **Returns**: the object itself. It overrides `Mobject.interpolate` and only interpolates the **point array** (`ValueTracker` has no notion of colour).

#### Sample: taking the interpolated state instantly

After animating to 4, `interpolate(ValueTracker(0), ValueTracker(2), 0.5)` instantly sets the value to 1.0 (the midpoint of 0 and 2) — the readout jumps in a single frame.

```python
from real_time_manim import Scene, DecimalNumber, ValueTracker, \
    YELLOW, UP, straight_path
from real_time_manim.vulkan_bind import MLWindow, Wait

class InterpolateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        tracker = ValueTracker(0.0)   # number tracker
        lbl = DecimalNumber(0, num_decimal_places=2, color=YELLOW).scale(0.8).to_edge(UP, buff=0.5)   # readout label
        lbl.add_updater(lambda d: d.set_value(round(float(tracker.get_value()), 2)))   # read the value every frame and display it
        self.add(lbl, tracker)   # add to the scene
        win.play(tracker.animate.set_value(4.0), run_time=0.6)   # animate to 4.0 first
        tracker.interpolate(ValueTracker(0.0), ValueTracker(2.0), 0.5, path_func=straight_path())   # take the interpolation of 0 and 2 at 0.5 directly (instant)
        print("after interpolate =", tracker.get_value())   #1.0
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: the readout first scrolls from 0 to 4.0 along with the animation.

Then `interpolate` uses two temporary `ValueTracker`s (0 and 2) to compute the midpoint at `alpha=0.5` and **instantly** sets this object's value to 1.0 — the number jumps from 4.0 to 1.0 within one frame.

This is exactly what `Transform` does internally when transforming two `ValueTracker`s; calling it manually suits the case of "just set an intermediate value directly".

<video src="assets/RTM output/10-ValueTracker-interpolate.mp4" controls width="560"></video>

> Note: `interpolate` is an instant function; for a continuous transition hand the `animate` to `Transform`.
>
> The two temporary objects `ValueTracker(0)` / `ValueTracker(2)` are thrown away after creation; only their point arrays are used.

### ComplexValueTracker

```python
def ComplexValueTracker(value: float = 0, **kwargs: Any) -> None
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `value` | `complex` / `float` | `0` | initial complex value |

> **Returns**: a new `ComplexValueTracker`. It tracks a **complex** parameter, storing the value internally as `[real, imaginary, 0]`, so `dot.move_to(ct.points)` can use it as a geometric position. It overrides `get_value -> complex` and `set_value(value) -> Self`.
>
> The inherited arithmetic operators are **verified unusable** on 0.21 (`tracker * 1j` / `tracker + 1` both raise `TypeError: float argument must be a string or a real number, not 'complex'`), consistent upstream behaviour on both engines.

#### Sample: a complex number as a coordinate

Starting from `ComplexValueTracker(-2 + 1j)`, a blue dot follows `ct.points` directly with an updater; `animate.set_value(3 + 2j)` moves the dot smoothly from (-2, 1) to (3, 2).

```python
from real_time_manim import Scene, Dot, ComplexValueTracker, \
    BLUE
from real_time_manim.vulkan_bind import MLWindow, Wait

class ComplexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        ct = ComplexValueTracker(-2 + 1j)   # complex tracker: the value is stored internally as [real, imaginary, 0]
        cdot = Dot(color=BLUE, radius=0.12)   # blue dot
        cdot.add_updater(lambda x: x.move_to(ct.points))   # the dot follows the internal coordinate directly
        self.add(cdot, ct)   # add to the scene
        win.play(ct.animate.set_value(3 + 2j), run_time=1.0)   # animated value change: the dot moves from (-2, 1) to (3, 2)
        cdot.clear_updaters()   # stop following
        print("ct.get_value() =", ct.get_value())   #3+2j
        #cannot be demonstrated: arithmetic like ct * 1j / ct + 1
        #    TypeError: float() argument must be a string or a real number, not 'complex'
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: `ComplexValueTracker(-2 + 1j)` stores its value in point coordinates as `[real, imaginary, 0]`, and the blue dot's updater calls `move_to(ct.points)` directly — the complex number is literally the screen coordinate.

`ct.animate.set_value(3 + 2j)` drags the real part from -2 to 3 and the imaginary part from 1 to 2 over 1 second, and the blue dot flies smoothly up and to the right along a straight line; once the value change is done the follow is stopped and `ct.get_value()` (`3+2j`) is printed.

<video src="assets/RTM output/10-ValueTracker-complex.mp4" controls width="560"></video>

> Not demonstrable: `ComplexValueTracker`'s arithmetic `ct * 1j` / `ct + 1` / `ct * 2` — **upstream behaviour**: `TypeError: float argument must be a string or a real number, not 'complex'` (a complex scalar stored in real point coordinates is read back as a float).
>
> `set_value` / `get_value` / `.animate` all work fine and every other parameter on this page has been rendered; if you need complex arithmetic, take `get_value`, do the math yourself and `set_value` it back.

---

See also: [Updaters](08-Updaters.md) | [Updater Utilities](08b-Updater-Utilities.md)
