# Updater utility functions and auto-changing objects: 12.1 + changing.py

This page covers two things: the 12.1 updater utility functions (module-level functions, not animation classes), and the objects that change automatically over time (`changing.py`).

The former returns a **mobject with an updater attached**; the latter is a **Mobject that carries its own updater (not an Animation)**. Both are used the same way: call first, then `self.add(...)`; no `play` needed.

All rendered and verified (`override_animation` is wired up but has no visible parameter difference; see the end of the page). For the animation classes see [01-Updater-Animations](01-Updater-Animations.md).

## Parameters

### 12.1 Updater utility functions (module-level functions, not animation classes)

**Purpose**: convenient ways to attach an updater to an object. **Returns**: the mobject that got the updater (just `self.add(...)` it).

| Function (source `mobject_update_utils.py`) | Signature | Purpose |
| --- | --- | --- |
| `always_redraw` | `always_redraw(func) -> Mobject` | **regenerates** the object every frame with `func()` (`mob.become(func())`); pairing it with `ValueTracker` to draw "a tangent / auxiliary circle that changes with a parameter" is the classic use |
| `always` | `always(method, *args, **kwargs) -> Mobject` | calls `method(*args, **kwargs)` every frame (`method` must be a mobject's bound method), e.g. `always(sq.set_color, RED)` |
| `f_always` | `f_always(method, *arg_generators, **kwargs) -> Mobject` | same as `always`, but the arguments are **generator functions** re-evaluated every frame, e.g. `f_always(label.next_to, mob.get_center, UP)` |
| `always_shift` | `always_shift(mobject, direction=RIGHT, rate=0.1) -> Mobject` | shifts `rate` units along `direction` per second at constant speed |
| `always_rotate` | `always_rotate(mobject, rate=20*DEGREES, **kwargs) -> Mobject` | rotates `rate` radians per second (`**kwargs` go to `rotate`, e.g. `about_point`) |
| `turn_animation_into_updater` | `turn_animation_into_updater(animation, cycle=False, delay=0, **kwargs) -> Mobject` | turns any animation **into an updater on that mobject**: no `play`; it advances automatically with scene time; `delay` is the delay in seconds |
| `cycle_animation` | `cycle_animation(animation, **kwargs) -> Mobject` | `turn_animation_into_updater(animation, cycle=True)`, an infinite loop |
| `override_animation` | `override_animation(animation_class) -> decorator` | decorates a method of a `Mobject` subclass so that a given animation class is **overridden** on that mobject (source `animation/animation.py`). Now wired up: RTM's `Animation.__new__` consults the override registry, `animation_override_for` supports same-name fallback across namespaces, `use_override=False` keeps the original class, and it works both ways; no visible parameter difference, so it is not demonstrated |

Quick start:

```python
alpha = ValueTracker(0)
dot = always_redraw(lambda: Dot(
    [np.cos(alpha.get_value()) * 2, np.sin(alpha.get_value()) * 2, 0], color=BLUE))
self.add(dot)
win.play(alpha.animate.set_value(PI), run_time=2, rate_func=linear)
```

```python
words = Text("Welcome").scale(0.8)
turn_animation_into_updater(Write(words, run_time=0.9))   # no play; writes automatically with time
self.add(words)
```

### `TracedPath`

```python
TracedPath(traced_point_func, stroke_width=2, stroke_color=WHITE, dissipating_time=None, **kwargs)
```

**Records the path traced by a point function and draws it as a line**: every frame it calls `traced_point_func()` (a no-argument function, usually `dot.get_center`) and appends the new point to itself. When `dissipating_time` is given, the trace **dissipates segment by segment** after that many seconds, producing a trailing effect. **Inherits** `TracedPath(VMobject)` (`metaclass=ConvertToOpenGL`).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `traced_point_func` | `Callable[[], point]` | — | a no-argument function returning the tracked point (e.g. `circ.get_start`, `dot.get_center`) |
| `stroke_width` | `float` | `2` | trace line width |
| `stroke_color` | `ParsableManimColor \| None` | `WHITE` | trace colour |
| `dissipating_time` | `float \| None` | `None` | dissipation duration; `None` = kept forever |
| `**kwargs` | … | — | other `VMobject` parameters (`stroke_opacity=[0,1]` gives a translucent trail, `fill_opacity`, …) |

> **Returns**: a `TracedPath` instance (it is a `VMobject`; just `self.add(...)` it).

Quick start:

```python
circ = Circle(color=RED).shift(4 * LEFT)
dot = Dot(color=RED).move_to(circ.get_start())
group = VGroup(circ, dot)
trace = TracedPath(circ.get_start, dissipating_time=0.5, stroke_opacity=[0, 1])
group.add_updater(lambda m: m.rotate(-0.3))
self.add(trace, group)
win.play(group.animate.shift(8 * RIGHT), run_time=4, rate_func=linear)
```

### `AnimatedBoundary`

```python
AnimatedBoundary(vmobject, colors=[BLUE_D, BLUE_B, BLUE_E, GREY_BROWN], max_stroke_width=3,
                 cycle_rate=0.5, back_and_forth=True, draw_rate_func=smooth,
                 fade_rate_func=smooth, **kwargs)
```

Wraps an object in a **border that keeps changing colour and drawing back and forth**, cycling automatically; good for keeping a piece of text continuously eye-catching. The border is made of two outline copies, one "drawing" and one "fading out". **Inherits** `AnimatedBoundary(VGroup)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vmobject` | `VMobject` | — | the object the border is drawn around |
| `colors` | `Sequence` | `[BLUE_D, BLUE_B, BLUE_E, GREY_BROWN]` | colour sequence used cyclically |
| `max_stroke_width` | `float` | `3` | maximum stroke width |
| `cycle_rate` | `float` | `0.5` | cycle speed multiplier |
| `back_and_forth` | `bool` | `True` | `True` draws back and forth, `False` cycles one way |
| `draw_rate_func` / `fade_rate_func` | `RateFunction` | `smooth` | rate function for drawing / fading out |
| `**kwargs` | … | — | `VGroup` parameters |

> **Returns**: an `AnimatedBoundary` instance (a `VGroup`; just `self.add(...)` it).

Quick start:

```python
text = Text("So shiny!")
boundary = AnimatedBoundary(text, colors=[RED, GREEN, BLUE], cycle_rate=3)
self.add(text, boundary)
win.play(Wait(2))
```

#### Sample: 12.1 utilities / TracedPath / AnimatedBoundary item by item

The finished clip for this page demonstrates one segment each in the order always_redraw → always/f_always → always_shift/always_rotate → turn_animation_into_updater/cycle_animation → TracedPath → AnimatedBoundary, with every parameter labelled on screen.

```python
import os

import numpy as np
from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    PI,
    RED,
    YELLOW,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    AnimatedBoundary,
    ApplyWave,
    Circle,
    Dot,
    Scene,
    Square,
    Text,
    TracedPath,
    Triangle,
    ValueTracker,
    VGroup,
    Write,
    always,
    always_redraw,
    always_rotate,
    always_shift,
    cycle_animation,
    f_always,
    linear,
    smooth,
    turn_animation_into_updater,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    Wait,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  used by __main__ at the end of the file


class Page_01b_Updater_Tools(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w=1280 / h=720 / hidden=True
        win.scene = self                          # param win.scene

        title = Text("Update utils 12.1 / TracedPath / AnimatedBoundary",
                     font_size=34, color=GREEN).to_edge(UP)   #title uses ASCII only: two-engine font fallback is more stable
        win.play(Write(title), run_time=0.8)

        # —— Step 1: always_redraw(func) —— regenerate the object from func() every frame ——
        s1a = Text("alpha = ValueTracker(0)", font_size=28, color=GREY_B)
        s1b = Text("dot = always_redraw(lambda: Dot([2cos t, 2sin t-1, 0], BLUE))",
                   font_size=26, color=GREY_B)
        s1c = Text("win.play(alpha.animate.set_value(PI), run_time=1.6, rate_func=linear)",
                   font_size=24, color=GREY_B)
        sig1 = VGroup(s1a, s1b, s1c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        alpha = ValueTracker(0)
        dot = always_redraw(lambda: Dot(                    # param func: regenerated every frame ✓
            [np.cos(alpha.get_value()) * 2,
             np.sin(alpha.get_value()) * 2 - 1.2, 0], color=BLUE))
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.4)
        self.add(dot)
        win.play(alpha.animate.set_value(PI), run_time=1.6, rate_func=linear)
        win.play(FadeOut(sig1), FadeOut(dot), run_time=0.4)

        # —— Step 2: always / f_always —— call a bound method every frame / re-evaluate arguments every frame ——
        s2a = Text("always(sq.next_to, dot2, DOWN)", font_size=30, color=GREY_B)
        s2b = Text("f_always(lbl.next_to, dot2.get_center, direction=UP)", font_size=28, color=GREY_B)
        s2c = Text("win.play(dot2.animate.shift(RIGHT * 5), run_time=1.5, rate_func=linear)",
                   font_size=24, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        dot2 = Dot(radius=0.1, color=RED).next_to(sig2, DOWN, buff=0.9).shift(LEFT * 2.5)
        sq = Square(side_length=0.9, color=ORANGE).set_fill(ORANGE, 0.7)
        lbl = Text("f_always", font_size=30, color=ORANGE)
        always(sq.next_to, dot2, DOWN)                      # param method(*args): fixed arguments, called every frame ✓
        f_always(lbl.next_to, dot2.get_center, direction=UP)  # param method(*generator functions): re-evaluated every frame ✓
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.4)
        self.add(dot2, sq, lbl)
        win.play(dot2.animate.shift(RIGHT * 5), run_time=1.5, rate_func=linear)
        sq.clear_updaters()
        lbl.clear_updaters()
        win.play(FadeOut(sig2), FadeOut(dot2), FadeOut(sq), FadeOut(lbl), run_time=0.4)

        # —— Step 3: always_shift / always_rotate —— no play, changes automatically with time ——
        s3a = Text("always_shift(tri, direction=UP, rate=0.9)", font_size=30, color=GREY_B)
        s3b = Text("always_rotate(tri, rate=PI)", font_size=30, color=GREY_B)
        sig3 = VGroup(s3a, s3b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        tri = Triangle().set_fill(GREEN, 0.7).set_stroke(GREEN, width=4)
        tri.next_to(sig3, DOWN, buff=0.8).shift(LEFT * 3 + DOWN * 0.8)
        always_shift(tri, direction=UP, rate=0.9)           # param direction=UP / rate=0.9 ✓
        always_rotate(tri, rate=PI)                         # param rate=PI ✓ (default 20*DEGREES)
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.4)
        self.add(tri)
        win.play(Wait(1.5))
        tri.clear_updaters()
        win.play(FadeOut(sig3), FadeOut(tri), run_time=0.4)

        # —— Step 4: turn_animation_into_updater / cycle_animation ——
        s4a = Text("turn_animation_into_updater(Write(words), cycle=False, delay=0.3)",
                   font_size=24, color=GREY_B)
        s4b = Text("cycle_animation(ApplyWave(wave, amplitude=0.3, ripples=2))",
                   font_size=26, color=GREY_B)
        s4c = Text("win.play(Wait(2.0))", font_size=26, color=GREY_B)
        sig4 = VGroup(s4a, s4b, s4c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        words = Text("Welcome", font_size=46, color=YELLOW).next_to(sig4, DOWN, buff=0.9).shift(LEFT * 3)
        wave = Text("wave", font_size=46, color=BLUE).next_to(sig4, DOWN, buff=0.9).shift(RIGHT * 3)
        turn_animation_into_updater(                        # param animation ✓
            Write(words, run_time=1.2), cycle=False, delay=0.3)   # param cycle=False / delay=0.3 ✓
        cycle_animation(                                    # param animation ✓ (= turn_animation_into_updater(cycle=True))
            ApplyWave(wave, amplitude=0.3, ripples=2, run_time=1.0))
        win.play(FadeIn(sig4, shift=DOWN), run_time=0.4)
        self.add(words, wave)
        win.play(Wait(2.0))                                 # the animation itself is not played; the updater advances with time
        wave.clear_updaters()
        win.play(FadeOut(sig4), FadeOut(words), FadeOut(wave), run_time=0.4)

        # —— Step 5: TracedPath(traced_point_func, stroke_width, stroke_color,
        #                      dissipating_time) —— record a point's path and draw it as a line ——
        s5a = Text("trace = TracedPath(circ.get_start, stroke_width=5,", font_size=26, color=GREY_B)
        s5b = Text("                     stroke_color=YELLOW, dissipating_time=0.6)", font_size=24, color=GREY_B)
        s5c = Text("group.add_updater(lambda m: m.rotate(-0.3))", font_size=28, color=GREY_B)
        s5d = Text("win.play(group.animate.shift(RIGHT * 6), run_time=2, rate_func=linear)",
                   font_size=24, color=GREY_B)
        sig5 = VGroup(s5a, s5b, s5c, s5d).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        circ = Circle(radius=0.7, color=RED, stroke_width=4).next_to(sig5, DOWN, buff=0.5)
        dot5 = Dot(radius=0.08, color=RED).move_to(circ.get_start())
        group = VGroup(circ, dot5)
        group.add_updater(lambda m: m.rotate(-0.3))
        trace = TracedPath(                                 # param traced_point_func ✓
            circ.get_start,
            stroke_width=5,                                 # param stroke_width=5 ✓ (default 2)
            stroke_color=YELLOW,                            # param stroke_color=YELLOW ✓ (default WHITE)
            dissipating_time=0.6,                           # param dissipating_time=0.6 ✓ (trail dissipates)
        )
        win.play(FadeIn(sig5, shift=DOWN), run_time=0.4)
        self.add(trace, group)
        win.play(group.animate.shift(RIGHT * 6), run_time=2.0, rate_func=linear)
        group.clear_updaters()
        win.play(FadeOut(sig5), FadeOut(trace), FadeOut(group), run_time=0.4)

        # —— Step 6: AnimatedBoundary(vmobject, colors, max_stroke_width, cycle_rate,
        #                             back_and_forth, draw/fade_rate_func) ——
        s6a = Text("AnimatedBoundary(txt, colors=[RED, GREEN, BLUE],", font_size=28, color=GREY_B)
        s6b = Text("    max_stroke_width=4, cycle_rate=3, back_and_forth=True,",
                   font_size=26, color=GREY_B)
        s6c = Text("    draw_rate_func=smooth, fade_rate_func=smooth)",
                   font_size=26, color=GREY_B)
        sig6 = VGroup(s6a, s6b, s6c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        txt = Text("So shiny!", font_size=46, color=GREEN).next_to(sig6, DOWN, buff=1.0)
        boundary = AnimatedBoundary(                        # param vmobject ✓
            txt,
            colors=[RED, GREEN, BLUE],                      # param colors ✓ (default [BLUE_D, BLUE_B, BLUE_E, GREY_BROWN])
            max_stroke_width=4,                             # param max_stroke_width=4 ✓ (default 3)
            cycle_rate=3,                                   # param cycle_rate=3 ✓ (default 0.5)
            back_and_forth=True,                            # param back_and_forth=True ✓ (draws back and forth)
            draw_rate_func=smooth,                          # param draw_rate_func=smooth ✓
            fade_rate_func=smooth,                          # param fade_rate_func=smooth ✓
        )
        win.play(FadeIn(sig6, shift=DOWN), run_time=0.4)
        self.add(txt, boundary)
        win.play(Wait(1.5))
        win.play(FadeOut(sig6), FadeOut(txt), FadeOut(boundary), run_time=0.45)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()
```

What this code does: six segments of "it moves without play".

- Segment 1: `always_redraw` regenerates a blue dot every frame from the `ValueTracker` angle; push `alpha` from 0 to π and you see the dot run along an arc.
- Segment 2: `always` makes an orange square run `next_to(the red dot, DOWN)` every frame; `f_always` makes the label stick to the red dot using a **re-evaluated** `dot2.get_center`. The red dot moves 5 units right.
- Segment 3: `always_shift` + `always_rotate` make a triangle rise and spin at the same time; you only `Wait(1.5)` and time moves on its own.
- Segment 4: `turn_animation_into_updater(Write(...))` auto-writes "Welcome" after a 0.3 s delay, and `cycle_animation(ApplyWave(...))` loops a wave forever; during `Wait(2.0)` only the updaters move.
- Segment 5: `TracedPath` draws the trajectory of the rotating circle's start point as a yellow trail (`dissipating_time=0.6`; it dissipates as it is drawn).
- Segment 6: `AnimatedBoundary` wraps "So shiny!" in a back-and-forth border that cycles red/green/blue.

Each segment ends with `clear_updaters()` before clearing the stage, so an updater does not survive into the next segment.

<video src="assets/RTM output/01b-Updater-Tools.mp4" controls width="560"></video>

> Note:
>
> - These "auto-changing" objects only move because **scene time advances**. In RTM you need `win.play(Wait(...))` (or some other play) to let time flow; just `self.add` and waiting does nothing.
> - `turn_animation_into_updater` / `cycle_animation` are now bridged to RTM's own animation classes (`t = origin + alpha*run_time` normalized driving, removed at the end; manim animations still go through their original functions), and both sources can be fed in; the samples on this page stay with manim's native classes (the demo was not re-rendered).
> - `always`/`f_always`'s `method` must be a mobject's **bound method**.
> - Remember `clear_updaters()` before switching segments, otherwise the object keeps being dragged along by the old updater.

See also: [Updater animations](01-Updater-Animations.md) · [Updaters (Mobject methods)](../../02-Mobjects/08-Updaters.md) · [Updater utility functions (Mobject)](../../02-Mobjects/08b-Updater-Utilities.md)
