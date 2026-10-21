# .animate syntax and generate_target() / MoveToTarget

`Mobject.animate` is the syntactic sugar for "change a property and it animates"; RTM's `win.play` / `AnimationGroup` / `Succession` all explicitly recognise an `.animate` builder and convert it automatically, and `MoveToTarget` is supported too.

## Parameters

### `Mobject.animate` (`_AnimationBuilder`)

```python
@property
def animate(self) -> _AnimationBuilder: ...

win.play(sq.animate.shift(RIGHT))                    # shift
win.play(sq.animate.set_fill(RED).set_opacity(0.5))  # chaining: several methods make one animation
win.play(sq.animate(run_time=2).rotate(PI / 2))      # animation parameters go right after .animate(...), passed only once
win.play(sq.animate(rate_func=there_and_back).shift(RIGHT))
```

`Mobject.animate` is a property that returns `_AnimationBuilder`: internally it calls `generate_target()` first, records each method on the chain into a list, and `win.play` composes them into **one** animation.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `**kwargs` (right after `.animate(...)`) | `Any` | — | **what can be passed**: attributes that can be `setattr`'d onto the animation object: `run_time`, `rate_func`, `reverse_rate_function`, … **Can only be passed once, before accessing any method**; writing them after a chained method or passing them twice raises `ValueError`. `lag_ratio=...` is not dropped: it is `setattr`'d onto the animation object at build time — with submobjects it staggers by family and RTM renders normally; for a single animation with no children the parameter has no effect, but it now raises a `UserWarning` explicitly instead of staying silent |
| chained method calls | — | — | e.g. `.shift(RIGHT)`, `.set_fill(RED)`, `.rotate(PI/2)`: not parameters themselves; all are recorded into the list and composed into one animation by `win.play` |

> **Returns**: `_AnimationBuilder`; `win.play(...)` converts it into an animation automatically.

### `generate_target` / `MoveToTarget`

```python
def generate_target(self) -> None: ...
MoveToTarget(mobject, **kwargs)
```

`.animate` is sugar for `generate_target()` + `MoveToTarget`; when the **target state needs complex computation** (lay out and align `target` first, then play), use the explicit form: `c.generate_target()` copies one into `c.target`, change `c.target` freely, and finally `win.play(MoveToTarget(c))`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the object that runs toward its own `target`; you must call `generate_target()` first for it to have a `target`. Playing without that call: the ManimCE version raises `ValueError` at construction, and RTM's own version raises `AttributeError: 'NoneType' object has no attribute 'copy'` in `begin()` (`Mobject`'s built-in `.target` is `None`) |
| `**kwargs` | `Any` | — | common `Animation` parameters (`run_time`, `rate_func`, `lag_ratio`, …), no extra parameters |

> **Returns**: `generate_target()` returns nothing (it attaches the copy to `mobject.target`); `MoveToTarget(...)` returns an animation instance to hand to `win.play(...)`.

#### Sample: three .animate forms + generate_target / MoveToTarget

The sample demonstrates three `.animate` forms, plus the explicit `generate_target()` + `MoveToTarget`:

- the chained `.animate.shift(...)`;
- `.animate(run_time=1.3).set_color(RED).rotate(PI/5)` (kwargs right after `.animate(...)`, several methods composed into one animation);
- the `.animate(rate_func=there_and_back).scale(0.55)`;
- the explicit `ci.generate_target()` + `MoveToTarget(ci, run_time=1.2)`.

```python
import os
from real_time_manim import (
    BLUE,
    DOWN,
    GREEN,
    GREY_B,
    LEFT,
    RED,
    RIGHT,
    UP,
    YELLOW,
    PI,
    Circle,
    Scene,
    Square,
    Text,
    VGroup,
    there_and_back,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    MoveToTarget,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401

class Page_03_animate_Syntax(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("03-.animate syntax and MoveToTarget", font_size=44, color=YELLOW).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        sq = Square(side_length=1.4, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 3.2 + DOWN * 1.9)
        ci = Circle(radius=0.7, color=GREEN).set_fill(GREEN, 0.5).shift(RIGHT * 3.2 + DOWN * 1.9)

        # —— Step 1: sq.animate.shift(...) ——
        l1 = Text("win.play(sq.animate.shift(RIGHT * 1.6))", font_size=30, color=GREY_B)
        l1.to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(l1, shift=DOWN), FadeIn(sq), FadeIn(ci), run_time=0.4)
        win.play(sq.animate.shift(RIGHT * 1.6))                  # param .animate + chained method shift
        win.play(Wait(0.2))

        # —— Step 2: kwargs right after .animate(...), several chained methods ——
        win.play(FadeOut(l1), run_time=0.3)
        l2 = Text("win.play(sq.animate(run_time=1.3)", font_size=30, color=GREY_B)
        l3 = Text("              .set_color(RED).rotate(PI/5))", font_size=30, color=GREY_B)
        sig2 = VGroup(l2, l3).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.4)
        win.play(sq.animate(run_time=1.3)                         # param .animate(run_time=…) (can only be passed once)
                 .set_color(RED)                                  # chained method 1
                 .rotate(PI / 5))                                 # chained method 2 (composed into one animation)
        win.play(Wait(0.2))

        # —— Step 3: rate_func written into .animate(...) ——
        win.play(FadeOut(sig2), run_time=0.3)
        l4 = Text("win.play(sq.animate(rate_func=there_and_back).scale(0.55))",
                  font_size=30, color=GREY_B).to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(l4, shift=DOWN), run_time=0.4)
        win.play(sq.animate(rate_func=there_and_back).scale(0.55))   # param rate_func (goes out and comes back)
        win.play(Wait(0.2))

        # —— Step 4: explicit generate_target() + MoveToTarget ——
        win.play(FadeOut(l4), run_time=0.3)
        l5 = Text("ci.generate_target();  ci.target.set_fill(RED, 0.4)", font_size=28, color=GREY_B)
        l6 = Text("                 .shift(2 * RIGHT + UP).scale(0.5)", font_size=28, color=GREY_B)
        l7 = Text("win.play(MoveToTarget(ci, run_time=1.2))", font_size=28, color=GREY_B)
        sig4 = VGroup(l5, l6, l7).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(sig4, shift=DOWN), run_time=0.4)
        ci.generate_target()                                      # param generate_target()
        ci.target.set_fill(RED, 0.4).shift(2 * RIGHT + UP).scale(0.5)
        win.play(MoveToTarget(ci, run_time=1.2))                  # param MoveToTarget(mobject, run_time)
        win.play(Wait(0.3))

        win.play(FadeOut(VGroup(title, sq, ci, sig4)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_03_animate_Syntax,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "03-animate-Syntax.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
```

What this code does: four steps —

- ① `sq.animate.shift(RIGHT * 1.6)`, the plainest "change a property and it animates";
- ② `sq.animate(run_time=1.3).set_color(RED).rotate(PI / 5)`, with the animation parameters right after `.animate(...)` and two more chained methods, composed into one 1.3-second recolour + rotation animation;
- ③ `sq.animate(rate_func=there_and_back).scale(0.55)`, writing the rate function into `.animate(...)`, so the scale goes "out and back";
- ④ `ci.generate_target()` builds a target copy for the circle; after changing `ci.target`'s colour/position/size, `MoveToTarget(ci, run_time=1.2)` moves it there in one go.

<video src="assets/RTM output/03-animate-Syntax.mp4" controls width="560"></video>

> Note: the same mobject can only have one `.animate` in a single `play`; for several steps, chain them. `.animate` interpolates between "the point set before the change ↔ the point set after the change", so a rotation along a complex path or the long way round travels in a straight line rather than an arc — for those needs use `Rotate`, `MoveAlongPath` or `ValueTracker + updater`. When the target state must be computed before playing, `generate_target()` + `MoveToTarget` is more intuitive.

Not demonstrated: .animate(lag_ratio=...) — no video: the conclusion of the investigation — the parameter is not dropped (it is `setattr`'d onto the animation object at build time), with submobjects it staggers by family and RTM renders normally; it has no effect for a single animation with no children, but it now raises a `UserWarning` explicitly instead of staying silent; `@override_animate` / `@override_animation` — wired up (`Animation.__new__` consults the override registry + `animation_override_for` same-name fallback across namespaces, `use_override=False` keeps the original class, `.animate` goes through the `@override_animate` regression lock), still not demonstrated: it needs a custom Mobject subclass.

---

See also: [Lifecycle and common parameters](01-Lifecycle-and-Common-Parameters.md) · [play and wait parameters](02-play-and-wait-Parameters.md) · [Create and the drawing family](../Creation-and-Removal/01-Create-and-the-Drawing-Family.md)
