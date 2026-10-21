# The .animate syntax

Turning "any method you call on an object" into a transition animation is the most common pattern in live preview.

## Parameters

### .animate (property)

```python
def animate(**play_kwargs) -> _AnimationBuilder
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `**play_kwargs` | `Any` | — | the keywords right after `.animate(...)` are **not parameters of `Scene.play`**; they are `setattr`'d onto the animation object after it is built (`run_time=`, `rate_func=`, `lag_ratio=`…); they **must come right after `.animate`, before the method call** |

> **Returns**: an `_AnimationBuilder`, which `Scene.play` finally turns into an animation. `mob.set_fill(RED)` changes instantly, `mob.animate.set_fill(RED)` plays a transition animation; several methods can be chained into **one** animation.

**Three common pitfalls**

1. The same object may appear only once in a single `play`: write `m.animate.shift(RIGHT).rotate(PI)` rather than splitting it into two animations.
2. `.animate` is **linear interpolation between points**, not path animation; to move along a path or rotate continuously by angle, use `MoveAlongPath` / `Rotate` / `Rotating`.
3. To follow a `ValueTracker`'s continuous changes, use an updater rather than `.animate`.

#### Sample: shifting, chaining, play parameters and `set`

A red square does a plain shift, chains "scale + rotate" into one two-step animation, then passes play parameters via `animate(run_time=..., rate_func=there_and_back)`.

An orange rectangle demonstrates `set` with `animate`.

```python
from real_time_manim import Scene, Square, Rectangle, \
    RED, ORANGE, DOWN, LEFT, RIGHT, PI, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class AnimateBasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        s = Square(color=RED, side_length=1.2, fill_opacity=0.6).shift(LEFT * 3.5)   #red square
        self.add(s)   #add to the scene
        win.play(s.animate.shift(RIGHT * 1.6), run_time=0.5)   #the plainest ".animate": a shift
        win.play(s.animate.scale(1.5).rotate(PI / 6), run_time=0.6)   #chained: one animation in two steps
        win.play(s.animate(run_time=0.8, rate_func=there_and_back).shift(DOWN), run_time=0.8)   #play parameters right after ".animate"
        rect = Rectangle(width=2.0, height=1.0, color=ORANGE, fill_opacity=0.6).shift(RIGHT * 3.5)   #orange rectangle
        self.add(rect)   #add to the scene
        win.play(rect.animate.set(width=5.0), run_time=0.5)   #set with animate: size to the target dimensions
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: the red square takes three steps.

- `animate.shift`: the plainest usage, a shift.
- `animate.scale(1.5).rotate(PI / 6)`: chains scaling and rotation **together** so a single animation does both smoothly (splitting it into two plays rotates first and scales second — a completely different look).
- `animate(run_time=0.8, rate_func=there_and_back).shift(DOWN)`: play parameters right after `.animate`, so the square goes down and comes back.

The orange rectangle on the right demonstrates `rect.animate.set(width=5.0)`: a transition animation that sizes to **target dimensions** (rather than by a factor).

<video src="assets/RTM output/07-animate-Syntax-animate.mp4" controls width="560"></video>

> Note:
>
> - The parenthesised parameters of `.animate(...)` **only accept** attributes that are valid to `setattr` on the animation object (`run_time` / `rate_func` / `lag_ratio` / `reverse_rate_function`…); put them in the method's argument position and they become method arguments — `animate.shift(2)` and `animate(run_time=2)` are two entirely different things.
> - Chained methods execute in order, and `run_time` is the total duration of the **whole chain**.
> - `lag_ratio=0.3` has no effect on an object with **no submobjects**; RTM now emits a `UserWarning` to say so explicitly instead of staying silent.

### override_animate (module-level decorator)

```python
def override_animate(method: types.MethodType) -> Callable[[types.MethodType], types.MethodType]
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `method` | unbound method | — | the method being overridden (defined on a `Mobject` subclass) |

> **Returns**: a decorator. It specifies, for a custom method, "which animation to play when called through `.animate`": the decorated method returns an `Animation`, and `.animate.method(...)` plays it instead of "execute directly, then interpolate". **Limitation**: the overridden method **cannot** appear chained with other methods in the same `.animate`.

#### Sample: a plain call vs. an `.animate` call

`PulseSquare` defines a plain method `pulse` (scales directly, instantly) and pairs it with a `Transform` animation via `@override_animate(pulse)`.

The left block is called directly and grows instantly; the right block is called through `.animate` and grows smoothly.

```python
from real_time_manim import Scene, Square, \
    PURPLE, LEFT, RIGHT, Transform, override_animate
from real_time_manim.vulkan_bind import MLWindow, Wait

class PulseSquare(Square):   #a custom subclass: pair a plain method with a dedicated animation
    def pulse(self, scale_factor):   #plain call: scale directly (instantly)
        self.scale(scale_factor)

    @override_animate(pulse)   #tell "pulse" which animation to play on an ".animate" call
    def _pulse_animation(self, scale_factor, anim_args=None):   #parameters match the original method, plus anim_args
        if anim_args is None:
            anim_args = {}
        target = self.copy().scale(scale_factor)   #target shape
        return Transform(self, target, **anim_args)   #return the animation: morph over smoothly


class OverrideDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        ds = PulseSquare(color=PURPLE, side_length=1.2, fill_opacity=0.6).shift(LEFT * 3.5)   #left: called directly
        ds2 = PulseSquare(color=PURPLE, side_length=1.2, fill_opacity=0.6).shift(RIGHT * 3.5)   #right: called through animate
        self.add(ds, ds2)   #add to the scene
        ds.pulse(1.4)   #a direct call → goes through the plain method (grows instantly)
        win.play(Wait(0.5))   #see the instant change
        win.play(ds2.animate.pulse(1.4), run_time=0.6)   #an ".animate" call → replaced by the returned animation (smooth)
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: `PulseSquare.pulse(1.4)` is normally just "a direct `scale`" — the left block is called directly and grows within a frame.

On the same class, the method decorated with `@override_animate(pulse)` defines "what to play on an `.animate` call": the right block's `ds2.animate.pulse(1.4)` triggers it, it returns a `Transform` (a snapshot after scaling), and the right block grows **smoothly**. One method, two call styles, two behaviours — that is the point of override.

<video src="assets/RTM output/07-animate-Syntax-override.mp4" controls width="560"></video>

> Note:
>
> - The decorator method (the `_xxx_animation` starting with an underscore) has a signature of the original method's parameters plus `anim_args` (the play parameters inside `.animate(...)`); its return value must be an `Animation`.
> - The overridden method **cannot** be mixed with other methods on the same `.animate` chain (it errors or bypasses the override).
> - A direct call always goes through the original implementation; keep both behaviours by telling them apart with this decorator.

### add_animation_override / animation_override_for (class methods)

```python
def add_animation_override(animation_class: type[Animation],
                           override_func: FunctionOverride) -> None
def animation_override_for(animation_class: type[Animation]) -> FunctionOverride | None
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `animation_class` | `type[Animation]` | — | the animation class being replaced, such as `FadeIn` |
| `override_func` | callable | — | a function returning the new animation, taking the constructor's parameters |

> **Returns**: `None` for the former; the registered function or `None` for the latter. Programmatically register/query "the replacement implementation of an animation class for this subclass" — the layer under `@override_animate`. It **only applies to the current class** (not to subclasses); registering the same animation class twice raises `MultiAnimationOverrideException`.

#### Sample: registering FadeIn → FadeOut

Register "`FadeIn` becomes `FadeOut`" for `FlashSquare`: print the registry lookup, and playing `FadeIn(sq)` actually performs a fade-out — the visible square vanishes on the spot.

```python
from real_time_manim import Scene, Square, \
    TEAL, FadeIn, FadeOut, Transform
from real_time_manim.vulkan_bind import MLWindow, Wait

class FlashSquare(Square):   #just a carrier class for the registry
    pass


class AddOverrideDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        FlashSquare.add_animation_override(FadeIn, lambda mobject, **kwargs: FadeOut(mobject))   #register: FadeIn becomes FadeOut
        print("override_for(FadeIn) =", FlashSquare.animation_override_for(FadeIn))   #lookup: fetch the registered function
        print("override_for(Transform) =", FlashSquare.animation_override_for(Transform))   #never registered: None
        sq = FlashSquare(color=TEAL, side_length=1.4, fill_opacity=0.7)   #teal square
        self.add(sq)   #add to the scene
        win.play(FadeIn(sq), run_time=0.6)   #the code says FadeIn; the registry swaps in FadeOut (the visible object fades out on the spot)
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: three steps in all.

- First register a rule on the `FlashSquare` class — "when this class meets `FadeIn`, swap in a function that returns `FadeOut`".
- `animation_override_for(FadeIn)` looks up the function just registered, while `animation_override_for(Transform)` finds nothing and returns `None`.
- Then a teal square **already on screen** is played with `win.play(FadeIn(sq))` — the registry takes effect, `FadeOut` actually runs, and the square fades out and disappears on the spot.

<video src="assets/RTM output/07-animate-Syntax-add_override.mp4" controls width="560"></video>

> Note: registration is **class-level** and **does not inherit to subclasses**; registering the same animation class twice raises `MultiAnimationOverrideException` (remove the old one before changing it).
>
> This API is lower-level than `@override_animate` — it replaces **by animation class**, while `@override_animate` replaces **by method**; prefer the latter for everyday custom animations.

---

See also: [Copying, Deriving and State](06-Copying-Deriving-and-State.md) | [Updater Animations](09-Updater-Animations.md)
