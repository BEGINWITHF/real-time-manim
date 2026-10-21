# Succession: sequential playback

The second half of the handbook's "8. Composing animations": a serial composition in which one animation finishes before the next plays, with only one child animation running at a time. It uses RTM's own implementation and is verified to render; `Wait` can be used directly as a child animation to leave a blank.

## Parameters

### Succession

```python
Succession(*animations, lag_ratio=1, **kwargs)
```

Inherits `Succession(AnimationGroup)`, source `animation/composition.py`. **One finishes before the next plays** (`lag_ratio` defaults fixed at `1`, i.e. 100% succession), used to arrange a narrative order: wait → add → wait → transform… collecting several pieces of action into a single `play`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*animations` | `Animation \| Iterable[Animation]` | — | child animations (lists/generators are flattened automatically; each goes through `prepare_animation`). **What can be passed**: any animation, an `.animate` builder and `Wait` |
| `lag_ratio` | `float` | `1` | fixed default of 100% succession; set it below 1 to let adjacent animations overlap. RTM's own `Succession` now inherits RTM's `AnimationGroup`, so this parameter takes effect |
| `**kwargs` | `Any` | — | same as `AnimationGroup`: `group`, `run_time=None`, `rate_func=linear` and the common `Animation` parameters; `run_time` is now accepted: when non-`None` it stretches the whole serial axis proportionally (`None` = the sum of the child animations' `run_time`) |

> **Returns**: an `Animation` (hand it to `play`).

> `Wait` (already supported) can go straight into the `Succession` timeline as a child animation to leave a blank between two pieces of action; the `Animation` base class can also be instantiated directly as a filler (see [Wait, rate and speed](../Waiting-and-Rate/01-Wait-Rate-and-Speed.md)).
>
> For the measured conclusions on `AnimationGroup` and `LaggedStart`/`LaggedStartMap`, see [01-AnimationGroup-and-Lag-Ratios](01-AnimationGroup-and-Lag-Ratios.md).

#### Sample: move → move → blank → recolour, four segments scheduled in one play

Three squares line up, and a single `play` schedules all four segments "move → move → `Wait` blank → recolour" into the serial timeline.

```python
from real_time_manim import Scene, Text, VGroup, Square, BLUE, GREEN, GREY_B, RED, YELLOW, \
    UP, DOWN, LEFT, RIGHT, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Succession, Wait

class SuccessionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("02-Succession", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        l1 = Text("Succession(sq1.animate.move_to(sq2),", font_size=30, color=GREY_B)
        l2 = Text("           sq2.animate.move_to(sq3), Wait(0.6),", font_size=30, color=GREY_B)
        l3 = Text("           sq3.animate(run_time=0.8).set_color(RED))", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #signature labels
        sq1 = Square(side_length=1.1, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 3.6 + DOWN * 2.1)   #blue square
        sq2 = Square(side_length=1.1, color=GREEN).set_fill(GREEN, 0.5).shift(DOWN * 2.1)   #green square
        sq3 = Square(side_length=1.1, color=GREY_B).shift(RIGHT * 3.6 + DOWN * 2.1)   #grey square
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(sq1, sq2, sq3)), run_time=0.4)   #labels and squares fade in
        win.play(Succession(                                      #param "*animations" (4 child animations)
            sq1.animate(run_time=1.0).move_to(sq2.get_center()),
            sq2.animate(run_time=1.0).move_to(sq3.get_center()),
            Wait(0.6),                                            #param "*animations" (Wait used directly as an empty segment)
            sq3.animate(run_time=0.8).set_color(RED),
        ))
        win.play(Wait(0.6))   #hold to see the result
        win.close()   #close the RTM window
```

What this code does: the blue square moves to the green square's position (1 second), then the green square moves to the grey square's position (1 second), then `Wait(0.6)` leaves a blank for 0.6 seconds, and finally the grey square turns red over 0.8 seconds.

The four segments are collected into a single `play`; only one small segment moves at a time, so the order is absolutely reliable (contrast with `AnimationGroup`'s parallel/staggered behaviour). When no group-level `run_time` is passed, the total duration is the sum of the child animations' `run_time`.

<video src="assets/RTM output/02-Succession-succession.mp4" controls width="560"></video>

> Note: when `Succession` is not given a group-level `run_time`, the total duration = the **sum** of the child animations' `run_time`; passing `run_time` stretches the whole serial axis proportionally. `Wait` can simply be passed as a child animation. If you want child animations to **overlap**, set `lag_ratio` below 1, or switch to `AnimationGroup(lag_ratio=0.5)` / `LaggedStart`.

#### Sample: rate_func=smooth applied to the whole serial timeline

Two circles move up one after the other; the group-level `rate_func=smooth` applies to the whole serial timeline.

```python
from real_time_manim import Scene, Text, VGroup, Circle, RED, BLUE, GREY_B, YELLOW, UP, \
    DOWN, LEFT, RIGHT, FadeIn, Write, smooth
from real_time_manim.vulkan_bind import MLWindow, Succession, Wait

class SuccessionRateFuncDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("02-SuccessionRateFunc", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        l1 = Text("Succession(a.animate.shift(UP), b.animate.shift(UP),", font_size=30, color=GREY_B)
        l2 = Text("           rate_func=smooth)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #signature labels
        a = Circle(radius=0.55, color=RED).set_fill(RED, 0.5).shift(LEFT * 2.2 + DOWN * 2.3)   #red circle
        b = Circle(radius=0.55, color=BLUE).set_fill(BLUE, 0.5).shift(RIGHT * 2.2 + DOWN * 2.3)   #blue circle
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(a, b)), run_time=0.4)   #labels and circles fade in
        win.play(Succession(                                      #param "rate_func" (applied to the whole serial timeline)
            a.animate(run_time=1.0).shift(UP * 1.6),
            b.animate(run_time=1.0).shift(UP * 1.6),
            rate_func=smooth,
        ))
        win.play(Wait(0.6))   #hold to see the result
        win.close()   #close the RTM window
```

What this code does: two circles move up one after the other, and `smooth` acts as the **group-level** `rate_func` over the whole serial timeline — the start and end of the whole thing ease in and out and the junction in the middle is smooth too, rather than each child animation easing once on its own.

<video src="assets/RTM output/02-Succession-ratefunc.mp4" controls width="560"></video>

> Note: the group-level `rate_func` acts on the **whole serial timeline** (easing at the start/end, smooth at the seams); to tune one child animation's rhythm, write `rate_func` into that child animation's own constructor.

### Difference from lag ratios

| | `Succession` | `AnimationGroup(lag_ratio=...)` | `LaggedStart` |
| --- | --- | --- | --- |
| Default rhythm | `lag_ratio=1`, fully serial | `lag_ratio=0`, fully parallel | `lag_ratio=0.05`, slight stagger |
| At any instant | only one child animation | all / overlapping by ratio | mostly overlapping |
| Typical use | narrative order, step-by-step explanation | side-by-side actions, overall composition | streaming appearance one by one |

Not demonstrated: `lag_ratio` — supported, not demonstrated here; `run_time` — supported (when non-`None` it stretches the whole serial axis proportionally), not demonstrated here (the samples don't pass it, so the default is the sum of the child animations' `run_time`).

---

See also: [AnimationGroup and lag ratios](01-AnimationGroup-and-Lag-Ratios.md) · [Wait, rate and speed](../Waiting-and-Rate/01-Wait-Rate-and-Speed.md) · [Updater animations](../Updater-Animations/01-Updater-Animations.md)
