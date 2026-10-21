# Updaters: methods on Mobject

Attach a "runs every frame" function to an object: following, accumulating motion, live readouts.

## Parameters

### add_updater

```python
def add_updater(update_function: _Updater, index: int | None = None,
                call_updater: bool = False) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `update_function` | callable | — | `f(mob)` is the non-time-based form, once per frame; `f(mob, dt)` is the time-based form, where `dt` is the seconds since the previous frame |
| `index` | `int` or `None` | `None` | insertion position; `None` appends to the end (this decides the execution order) |
| `call_updater` | `bool` | `False` | with `True` it runs once immediately after being attached (`dt=0`) |

> **Returns**: self. **An object with an updater must be `self.add(...)`ed into the scene to be driven** (`ValueTracker` is no different, see [ValueTracker](10-ValueTracker.md)). Updaters keep running during animations.

#### Sample: time-based vs. non-time-based

A rotating square carries one time-based updater (`f(mob, dt)`); a label carries two non-time-based ones — one reads the width every frame to write the number, the other uses `index=0, call_updater=True` to snap to the square's underside immediately and follow it all the way.

```python
from real_time_manim import Scene, Square, DecimalNumber, \
    BLUE, YELLOW, UP, DOWN, LEFT, RIGHT, DEGREES, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class AddUpdaterDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.0, fill_opacity=0.6).shift(LEFT * 3.5)   #blue square
        self.add(sq)   #add to the scene (an object with an updater must be in the scene to be driven)
        spin = lambda m, dt: m.rotate(dt * 90 * DEGREES)   #time-based f(mob, dt): rotate 90° per second
        sq.add_updater(spin)   #attach the updater
        lbl = DecimalNumber(0, num_decimal_places=2, color=YELLOW).scale(0.7).shift(LEFT * 3.5 + DOWN * 1.6)   #readout label
        val = lambda d: d.set_value(round(float(sq.get_width()), 2))   #non-time-based f(mob): read the square's bounding-box width every frame
        pos = lambda d: d.next_to(sq, DOWN, buff=0.3)   #non-time-based: the label follows the square
        lbl.add_updater(val)   #appended to the end of the list by default
        lbl.add_updater(pos, index=0, call_updater=True)   #insert at the head and run once immediately on attach
        self.add(lbl)   #add the label to the scene
        win.play(Wait(1.0))   #hold for 1 second: the square keeps rotating and the number keeps refreshing
        win.play(sq.animate.shift(RIGHT * 2.0), run_time=0.5)   #updaters keep driving during the animation
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: the blue square carries a **time-based** updater — `f(mob, dt)` rotating by `dt × 90°` each frame (exactly 90° in a second) — and rotates at a visibly steady rate during the 1-second `Wait`.

As it rotates, its bounding-box width keeps changing; the yellow numeric label below (two **non-time-based** updaters) shows that width in real time and follows along attached to the square's bottom. `index=0` inserts the position updater at the head of the execution list, and `call_updater=True` puts it in place the instant it is attached.

During the final `animate.shift` animation the rotation and the readout carry on as usual.

<video src="assets/RTM output/08-Updaters-add_updater.mp4" controls width="560"></video>

> Note: **do not cache values in the parameters** of a non-time-based updater — writing `d.next_to(sq, UP, buff=0.3)` so that `sq`'s position is read afresh each time is what keeps up; the same goes for the `always.next_to` sugar.
>
> Forgetting `self.add` on the object is the most common reason "the updater does nothing".

### remove_updater / clear_updaters

```python
def remove_updater(update_function: _Updater) -> Self
def clear_updaters(recursive: bool = True) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `update_function` | callable | — | what is passed must be **the same function object** (keep it in a variable) |
| `recursive` | `bool` | `True` | `clear_updaters` only: whether to clear submobjects as well |

> **Returns**: self. `remove_updater` removes **one** by reference; `clear_updaters` empties them all (if the same function was attached several times, all are removed).

#### Sample: attaching, removing, re-attaching, clearing

A named `spin` is attached and rotates; `remove_updater(spin)` takes it off by the same function object; an anonymous function is swapped in to make it fall, and finally `clear_updaters()` wipes everything in one go — each step verified by printing the count.

```python
from real_time_manim import Scene, Square, \
    GREEN, DOWN, LEFT, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class RemoveClearDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=GREEN, side_length=1.0, fill_opacity=0.6).shift(LEFT * 3.0)   #green square
        spin = lambda m, dt: m.rotate(dt * 120 * DEGREES)   #keep it named: removal needs the same function object
        sq.add_updater(spin)   #attach
        self.add(sq)   #add to the scene
        print("updaters after attach =", len(sq.get_updaters()))   #1
        win.play(Wait(0.6))   #it starts rotating
        sq.remove_updater(spin)   #remove by the same function object
        print("updaters after remove =", len(sq.get_updaters()))   #0
        sq.add_updater(lambda m, dt: m.shift(DOWN * dt))   #attach another anonymous function: fall 1 per second
        win.play(Wait(0.5))   #it falls
        sq.clear_updaters()   #clear every updater (recursive)
        print("updaters after clear =", len(sq.get_updaters()))   #0
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: the green square first attaches the named `spin` and rotates for 0.6 s (console `updaters after attach = 1`); `remove_updater(spin)` passes **the same function object** to take it off and the square stops at once (`0`); then an anonymous function is attached to make it fall steadily for 0.5 s; finally `clear_updaters()` empties everything and the fall stops too (`0`).

<video src="assets/RTM output/08-Updaters-remove_clear.mp4" controls width="560"></video>

> Note: `remove_updater` needs the same function by **reference equality** — an anonymous `lambda m, dt: ...` cannot be pointed at again, so store it in a variable if you want to remove it.
>
> `clear_updaters(recursive=True)` clears submobjects recursively; pass `recursive=False` to clear only its own.

### suspend_updating / resume_updating / update

```python
def suspend_updating(recursive: bool = True) -> Self
def resume_updating(recursive: bool = True) -> Self
def update(dt: float = 0, recursive: bool = True) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `recursive` | `bool` | `True` | whether to act recursively on submobjects |
| `dt` | `float` | `0` | `update` only: the seconds passed to time-based updaters |

> **Returns**: self. `suspend_updating` pauses execution but **the function stays in the list**; `resume_updating` runs once immediately with `dt=0` when it resumes; `update(dt)` triggers it once by hand — normally the render loop calls it, and you only need it outside a `Scene` (interactive scripts, unit tests); while suspended, `update` skips it entirely.

#### Sample: spin → stop → spin again → trigger by hand

A rotating square plays for 0.5 s and then pauses (stopped for 0.5 s), spins again after resuming, and finally is triggered once by hand with `update(dt=0)`.

```python
from real_time_manim import Scene, Square, \
    RED, UP, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class SuspendDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=RED, side_length=1.0, fill_opacity=0.6).shift(UP * 1.5)   #red square
        sq.add_updater(lambda m, dt: m.rotate(dt * 120 * DEGREES))   #rotate 120° per second
        self.add(sq)   #add to the scene
        win.play(Wait(0.5))   #it starts rotating
        sq.suspend_updating(recursive=True)   #pause: the function is still in the list, it just does not run
        win.play(Wait(0.5))   #it stops spinning
        sq.resume_updating(recursive=True)   #resume: run once immediately with dt=0
        win.play(Wait(0.3))   #it spins again
        sq.update(dt=0, recursive=True)   #trigger once by hand (only needed outside the render loop)
        win.play(Wait(0.3))   #wait 0.3s
        win.close()   #close the RTM window
```

What this code does: after the red square attaches its rotation updater, it goes through four stages.

- During the first `Wait` it spins at a steady rate.
- During the second `Wait`, after `suspend_updating(recursive=True)`, it stops completely (the updater is still attached to the list, it just does not run).
- `resume_updating` resumes it and it spins again in the third stage.
- Finally `sq.update(dt=0, recursive=True)` triggers once by hand (`dt=0`, so there is no visible effect — this API is for use outside the render loop, and what the video shows is that it does not break the normal rhythm).

<video src="assets/RTM output/08-Updaters-suspend.mp4" controls width="560"></video>

> Note:
>
> - The typical use is to `suspend_updating` **during an animation** so the updater does not interfere with the interpolation, then `resume_updating` when it ends.
> - On resume it runs the non-time-based updaters once with `dt=0`, so following labels snap back into place at once.
> - `update` is rarely needed — RTM drives every frame automatically.

### always (property)

```python
def always.method(*args, **kwargs) -> _UpdaterBuilder
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*args`, `**kwargs` | `Any` | — | parameters passed straight to the target method |

> **Returns**: an `_UpdaterBuilder` (effective as soon as it is attached). `t.always.next_to(sq, UP)` is equivalent to `t.add_updater(lambda m: m.next_to(sq, UP), call_updater=True)`; each method in the chain is its **own independent** updater. Do not write read-only methods such as `mob.always.get_value(...)` — parameters are evaluated once at attach time, so use `add_updater` for values that need recomputing every frame.

#### Sample: a following label

One line, `tag.always.next_to(sq, UP, buff=0.3)`, sets up the following — as the square moves, the label stays glued above it the whole time.

```python
from real_time_manim import Scene, Square, Text, \
    BLUE, YELLOW, UP, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class AlwaysDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.2, fill_opacity=0.6).shift(LEFT * 3.0)   #blue square
        self.add(sq)   #add to the scene
        tag = Text("tag", font_size=28, color=YELLOW)   #the following label
        tag.always.next_to(sq, UP, buff=0.3)   #sugar: equivalent to add_updater(..., call_updater=True)
        self.add(tag)   #add to the scene
        win.play(sq.animate.shift(RIGHT * 2.5), run_time=0.8)   #the label follows the whole time
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: one line, `tag.always.next_to(sq, UP, buff=0.3)`, attaches "the label always 0.3 directly above the square" as an updater (it runs once at attach time, so it is in the right place from the start); during the 0.8 s the square moves right, the yellow `tag` stays stuck to it the whole way. This is sugar for `add_updater(lambda m: m.next_to(...), call_updater=True)`.

<video src="assets/RTM output/08-Updaters-always.mp4" controls width="560"></video>

> Note: the parameters of `.always.method(...)` are **evaluated once at attach time** — writing `t.always.next_to(sq, UP)` is fine (`sq` is a reference, so its position is read afresh on every run), but do not expect it to recompute the parameter expressions every frame; for per-frame dynamic parameters use `add_updater(lambda m: m.next_to(target(), UP))` honestly.
>
> It is a different thing from the module-level `always` function (see [Updater Utilities](08b-Updater-Utilities.md)).

### get_updaters / get_time_based_updaters / has_time_based_updater / match_updaters

```python
def get_updaters() -> list[_Updater]
def get_time_based_updaters() -> list[_TimeBasedUpdater]
def has_time_based_updater() -> bool
def match_updaters(mobject: Mobject) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | `match_updaters` only: copies its updater list (only that object's own) |

> **Returns**: the first three return lists / a `bool` (a debugging godsend); `match_updaters` returns self.

#### Sample: querying and copying

After the square attaches a rotation, three query results are printed; after the red dot's `match_updaters(square)` copies them, it spins too.

```python
from real_time_manim import Scene, Square, Dot, \
    GREEN, RED, RIGHT, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class QueryMatchDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=GREEN, side_length=1.0, fill_opacity=0.6).shift(LEFT * 3.0)   #green square
        spin = lambda m, dt: m.rotate(dt * 90 * DEGREES)   #keep it named
        sq.add_updater(spin)   #attach
        self.add(sq)   #add to the scene
        print("get_updaters =", len(sq.get_updaters()))   #1
        print("get_time_based_updaters =", len(sq.get_time_based_updaters()))   #1
        print("has_time_based_updater =", sq.has_time_based_updater())   #True
        d2 = Dot(color=RED, radius=0.1).shift(RIGHT * 3.0)   #red dot
        d2.match_updaters(sq)   #copy sq's updater list (only sq's own)
        self.add(d2)   #add to the scene
        print("d2 updaters =", len(d2.get_updaters()))   #1
        win.play(Wait(0.8))   #both of them are spinning
        win.close()   #close the RTM window
```

What this code does: after the green square attaches the time-based `spin`, all three queries pass — `get_updaters` has length 1, `get_time_based_updaters` has length 1, and `has_time_based_updater` is `True`.

A single `match_updaters(sq)` on the red dot on the right copies the square's updater list (`d2 updaters = 1`), so it rotates steadily as well — the two objects share the same function object and both spin correctly.

<video src="assets/RTM output/08-Updaters-query_match.mp4" controls width="560"></video>

> Note: `match_updaters` copies only the other's **own** list (it does not recurse into submobjects); what is copied is a function reference — when the same function runs on two objects each receives its own `mob`, with no cross-talk.
>
> To debug "is the updater actually attached", these three siblings' prints are all you need.

---

See also: [Updater Utilities](08b-Updater-Utilities.md) | [ValueTracker](10-ValueTracker.md)
