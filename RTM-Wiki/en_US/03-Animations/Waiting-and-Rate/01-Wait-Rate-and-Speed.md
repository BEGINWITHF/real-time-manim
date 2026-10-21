# Waiting, rate and speed: Wait / ChangeSpeed / Animation

The classes filed under "wait and rate":

- `Wait`: a pure wait.
- `ChangeSpeed`: assigns a speed multiplier to any animation by time percentage.
- `Animation`: the base class, instantiated directly as a placeholder.

All three have been measured to render (`Wait` uses RTM's own implementation; `ChangeSpeed` is bridged by `window/patches.py`'s `_sm.prepare_animation = _patched_prepare_animation` + `_RtmAnimationAdapter` (not in `compat.py`); `Animation` is the manim base class rendered through the timeline). A same-scene comparison of 8 `rate_func`s is also included.

## Parameters

### `Wait`

```python
Wait(run_time=1, stop_condition=None, frozen_frame=None, rate_func=linear, **kwargs)
```

Inherits `Wait(Animation)`. It is the "do nothing" animation: a pure wait of `run_time` seconds.

`stop_condition` is a no-argument function evaluated every frame; returning a truthy value ends it early; `frozen_frame` controls whether it renders as a still frame (`None` lets the scene decide automatically, while `False` still runs updaters). You only need to construct `Wait` explicitly when you want to **put it on a `Succession`/`AnimationGroup` timeline**.

Related API: `Scene.wait(duration=1.0, stop_condition=None, frozen_frame=None)`, `Scene.pause(duration)`, `Scene.wait_until(stop_condition, max_time=60)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `run_time` | `float` | `1` | wait seconds |
| `stop_condition` | `Callable[[], bool] \| None` | `None` | the end condition evaluated every frame; ends early when true; **giving it together with `frozen_frame=True` raises `ValueError`** (the same error as manim). RTM's own `Wait` supports it too, see [Play and Wait (Scene chapter)](../../01-Scenes-and-Cameras/Scenes/03-Play-and-Wait.md) |
| `frozen_frame` | `bool \| None` | `None` | whether to freeze the frame; `None` decides automatically (freezes when the scene has no updater at all, otherwise steps); during `True` updaters are never driven and the picture is frozen |
| `rate_func` | `Callable` | `linear` | the progress function during the wait (usually no need to change — there is nothing interpolatable on screen during a wait) |
| `**kwargs` | `Any` | — | `Animation` common parameters |

> **Returns**: an `Animation` (hand it to `play`, or put it on a `Succession`/`AnimationGroup` timeline).

#### Sample: run_time pure wait of 1 second

A blue square with `Wait(run_time=1.0)` just stops for 1 second, entering and leaving the scene with `FadeIn`/`FadeOut` around it.

```python
from real_time_manim import Scene, Text, VGroup, Square, BLUE, GREY_B, YELLOW, UP, DOWN, \
    FadeIn, FadeOut, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class WaitDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Wait", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        lab = Text("win.play(Wait(1.0))   # run_time=1.0s",
                   font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        sq = Square(side_length=1.1, color=BLUE).set_fill(BLUE, 0.5).next_to(lab, DOWN, buff=0.6)   # the blue square during the wait
        txt = Text("waiting...", font_size=30, color=GREY_B).next_to(sq, DOWN, buff=0.4)   # the waiting hint text
        win.play(FadeIn(lab, shift=DOWN), FadeIn(sq), FadeIn(txt), run_time=0.4)   # the label and square fade in
        win.play(Wait(1.0))   # parameter "run_time": wait 1 second doing nothing
        win.play(FadeOut(VGroup(lab, sq, txt)), run_time=0.4)   # the whole group fades out to close
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: after the label fades in, `win.play(Wait(1.0))` stops for 1 second — `run_time` is the number of seconds it stops, the picture freezes and nothing happens, then the whole group fades out to close.

0.6 seconds are left before and after the wait so the result settles.

<video src="assets/RTM output/01-Wait-Rate-and-Speed-wait.mp4" controls width="560"></video>

### `ChangeSpeed`

```python
ChangeSpeed(anim, speedinfo, rate_func=None, affects_speed_updaters=True, **kwargs)
```

Inherits `ChangeSpeed(Animation)`, from `animation/speedmodifier.py`; on the RTM side it is wired up by **`window/patches.py`** (`_sm.prepare_animation = _patched_prepare_animation` + `_RtmAnimationAdapter` bridges RTM's own sub-animations into manim's `ChangeSpeed` — **not in `compat.py`**).

**Adding speed changes to another animation**: specify different speed multipliers at nodes given as percentages of `run_time` (`1` = normal, `0.1` = slow motion, `0` = stopped), with smooth transitions between nodes. Internally it rewrites the sub-animations' `rate_func` and recomputes the total duration on the new timeline.

Only one `ChangeSpeed` with `affects_speed_updaters=True` may be playing at a time, otherwise `AssertionError`.

Static method `ChangeSpeed.add_updater(mobject, update_function, index=None, call_updater=False)`: only updaters added with it respond to the speed change (when the function signature takes `dt`, the speed-changed `dt` is fed in).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `anim` | `Animation \| _AnimationBuilder` | — | the animation being speed-changed (`AnimationGroup` is processed per sub-animation and rebuilt as-is) |
| `speedinfo` | `dict[float, float]` | — | `{time percentage: speed multiplier}`. **accepts** e.g. `{0.3:1, 0.6:0.1, 1:1}`; a missing `0` is filled with `1`, a missing `1` with the last multiplier |
| `rate_func` | `Callable \| None` | `None` | overrides the wrapped animation's rate function (`None` uses its own) |
| `affects_speed_updaters` | `bool` | `True` | whether updaters added with `ChangeSpeed.add_updater` also follow the speed change |
| `**kwargs` | `Any` | — | `Animation` common parameters (`run_time` is computed internally on the new timeline) |

> **Returns**: an `Animation` (hand it to `play`).

#### Sample: speedinfo by percentage, two colliding dots

Two colliding dots each run a 1-second translation (`AnimationGroup` starts them together), wrapped in `ChangeSpeed` to pace them by progress percentage: normal speed for the first 30%, 0.25× slow motion in the middle, 2× fast-forward at the end.

```python
from real_time_manim import Scene, Text, VGroup, Dot, Line, BLUE, RED, YELLOW, GREY_B, \
    UP, DOWN, LEFT, RIGHT, AnimationGroup, ChangeSpeed, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class ChangeSpeedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-ChangeSpeed", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        lab3 = Text("ChangeSpeed(AnimationGroup(a.shift, b.shift),",
                    font_size=30, color=GREY_B)
        lab4 = Text("  speedinfo={0.3:1, 0.5:0.25, 1:2}, rate_func=linear)",
                    font_size=30, color=GREY_B)
        lab = VGroup(lab3, lab4).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line signature label
        a = Dot(radius=0.14, color=RED).move_to(LEFT * 3.2 + DOWN * 1.2)
        b = Dot(radius=0.14, color=BLUE).move_to(RIGHT * 3.2 + DOWN * 1.2)
        trk = Line(LEFT * 3.2 + DOWN * 1.2, RIGHT * 3.2 + DOWN * 1.2, stroke_width=2, color=GREY_B)
        trk.set_stroke(opacity=0.4)
        win.play(FadeIn(lab, shift=DOWN), FadeIn(VGroup(a, b, trk)), run_time=0.4)   # the label and the two colliding dots fade in
        win.play(ChangeSpeed(
            AnimationGroup(a.animate(run_time=1).shift(RIGHT * 6.4),
                           b.animate(run_time=1).shift(LEFT * 6.4)),
            speedinfo={0.3: 1, 0.5: 0.25, 1: 2},   # parameter "speedinfo": normal speed for the first 30%, 0.25x in the middle, 2x at the end
            rate_func=linear,                      # parameter "rate_func"
            affects_speed_updaters=True))          # parameter "affects_speed_updaters"
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the red and blue dots translate toward each other, and `speedinfo={0.3: 1, 0.5: 0.25, 1: 2}` paces them by progress percentage — normal speed for the first 30%, dropping to 0.25× slow motion from 30% to 50% (a visible pause), then 2× fast-forward past 50% to the end.

`rate_func=linear` keeps the speed constant within each segment without easing.

<video src="assets/RTM output/01-Wait-Rate-and-Speed-changespeed.mp4" controls width="560"></video>

#### Sample: an updater attached with add_updater follows the speed change

The yellow dot's displacement is not played as an animation but accumulated by an updater attached with `ChangeSpeed.add_updater` according to `dt`; wrapped in `ChangeSpeed(Wait(1.6), ...)`, **even the updater follows the speed change** — during the 0.15× middle segment the yellow dot almost stops.

```python
from real_time_manim import Scene, Text, VGroup, Dot, Line, YELLOW, GREY_B, UP, DOWN, \
    LEFT, RIGHT, ChangeSpeed, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class ChangeSpeedUpdaterDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-ChangeSpeed-updater", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        lab5 = Text("ChangeSpeed.add_updater(m, fn)  +  ChangeSpeed(",
                    font_size=30, color=GREY_B)
        lab6 = Text("    Wait(1.6), speedinfo={0.3:1, 0.55:0.15, 1:1})",
                    font_size=30, color=GREY_B)
        lab = VGroup(lab5, lab6).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line signature label
        m = Dot(radius=0.14, color=YELLOW).move_to(LEFT * 3.2 + DOWN * 1.2)
        trk = Line(LEFT * 3.2 + DOWN * 1.2, RIGHT * 3.2 + DOWN * 1.2, stroke_width=2, color=GREY_B)
        trk.set_stroke(opacity=0.4)
        win.play(FadeIn(lab, shift=DOWN), FadeIn(VGroup(m, trk)), run_time=0.4)   # the label and track fade in
        ChangeSpeed.add_updater(m, lambda mob, dt: mob.shift(RIGHT * 3.4 * dt))   # parameter "ChangeSpeed.add_updater": attach a speed-changing updater
        win.play(ChangeSpeed(Wait(1.6), speedinfo={0.3: 1, 0.55: 0.15, 1: 1},   # parameter "speedinfo": 0.15x slow motion in the middle
                             affects_speed_updaters=True))
        m.clear_updaters()   # detach the updater
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the yellow dot's displacement is accumulated by the updater attached with `ChangeSpeed.add_updater(m, lambda mob, dt: mob.shift(RIGHT * 3.4 * dt))` according to `dt`, wrapped in `ChangeSpeed(Wait(1.6), speedinfo={0.3: 1, 0.55: 0.15, 1: 1})` — normal-speed glide for the first 30%, almost stopping at 0.15× in the middle, then back to normal speed to finish.

After playing, `clear_updaters` detaches it.

<video src="assets/RTM output/01-Wait-Rate-and-Speed-changespeed_updater.mp4" controls width="560"></video>

> Note:
>
> - `ChangeSpeed.speedinfo`'s keys are **progress percentages** (0~1), not seconds.
> - Only one `affects_speed_updaters=True` may be playing at a time; stacking several raises `AssertionError`.
> - For your own updater to respond to the speed change it must be attached with `ChangeSpeed.add_updater`; an ordinary `add_updater`'s `dt` is unaffected by the speed change.

### `Animation` (the base class used directly)

```python
Animation(mobject, lag_ratio=0.0, run_time=1.0, rate_func=smooth, reverse_rate_function=False,
          name=None, remover=False, suspend_mobject_updating=True, introducer=False, use_override=True)
```

The base class of all animations, from `animation/animation.py`. When instantiated directly it "**takes up `run_time` seconds without changing anything**" (it interpolates the mobject back to itself every frame), commonly used as a placeholder in `Succession`/`LaggedStartMap`.

It is also the starting point for custom animations: subclass it and override `interpolate_mobject()` to write your own animation.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the object acted on |
| `lag_ratio` | `float` | `0.0` | the stagger ratio when combined with other animations |
| `run_time` | `float` | `1.0` | duration (seconds) |
| `rate_func` | `Callable` | `smooth` | progress function |
| `reverse_rate_function` | `bool` | `False` | whether to reverse the progress function |
| `name` | `str \| None` | `None` | animation name |
| `remover` | `bool` | `False` | whether to remove from the scene when finished |
| `suspend_mobject_updating` | `bool` | `True` | whether to suspend the mobject's own updater during playback |
| `introducer` | `bool` | `False` | whether to add to the scene before playing |
| `use_override` | `bool` | `True` | whether to use the `override_animation` rewrite |

> **Returns**: an `Animation`. A bare `Animation` does not change the picture; `name` / `lag_ratio` / `suspend_mobject_updating` / `introducer` / `use_override` / `reverse_rate_function` have no visible effect (see "Not demonstrable").

#### Sample: base-class placeholder for 1.2 seconds

A bare `Animation` takes up 1.2 seconds without changing anything — the green square does not move at all, which is exactly how it is used as a placeholder on a timeline.

```python
from real_time_manim import Scene, Text, Square, GREEN, YELLOW, GREY_B, UP, DOWN, \
    Animation, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class AnimationDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Animation", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        lab = Text("Animation(sq, run_time=1.2, rate_func=linear)  # placeholder",
                   font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        sq = Square(side_length=1.3, color=GREEN).set_fill(GREEN, 0.5).next_to(lab, DOWN, buff=0.6)   # the green square that stays put as a placeholder
        win.play(FadeIn(lab, shift=DOWN), FadeIn(sq), run_time=0.4)   # the label and square fade in
        win.play(Animation(sq, run_time=1.2, rate_func=linear))   # parameter "mobject" / "run_time" / "rate_func": takes up 1.2 seconds
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: `Animation(sq, run_time=1.2, rate_func=linear)` interpolates the green square back to itself every frame — nothing happens on screen, and the timeline really does elapse 1.2 seconds.

<video src="assets/RTM output/01-Wait-Rate-and-Speed-animation.mp4" controls width="560"></video>

## Rate functions at a glance

`rate_func` is a common parameter of all animations (see [Common Parameters](../Common/01-Lifecycle-and-Common-Parameters.md) for the syntax and defaults).

The same translation animation is compared against the 8 most commonly used rate functions at once: the 4 smoothing/impulse family run first, then the same dots are reset and the 4 round-trip/overshoot family run.

#### Sample: the same translation animation × 8 rate functions

Four colored dots run the same `dot.animate(run_time=1.8, rate_func=F).shift(RIGHT*6.4)`, changing only `rate_func`: the first batch `linear` / `smooth` / `rush_into` / `rush_from`, and after the reset the second batch `there_and_back` / `exponential_decay` / `squish(.35,.65)` / `wiggle`.

```python
from real_time_manim import Scene, Text, VGroup, Dot, Line, BLUE, GREEN, GREY_B, ORANGE, \
    RED, YELLOW, UP, DOWN, LEFT, RIGHT, FadeIn, FadeOut, Write
from real_time_manim import exponential_decay, linear, rush_from, \
    rush_into, smooth, squish_rate_func, there_and_back, wiggle
from real_time_manim.vulkan_bind import MLWindow, Wait

class RateFuncDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-rate_func", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        cols = [RED, BLUE, GREEN, ORANGE]
        names1 = ["linear", "smooth", "rush_into", "rush_from"]
        funcs1 = [linear, smooth, rush_into, rush_from]
        lab1 = Text("dot.animate(run_time=1.8, rate_func=F).shift(RIGHT*6.4)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   # label fades in from below
        tracks = VGroup()
        labels1 = VGroup()
        dots1 = []
        for i, nm in enumerate(names1):
            y = 0.55 - i * 1.15
            labels1.add(Text(nm, font_size=26, color=cols[i]).move_to(LEFT * 5.6 + UP * y))
            trk = Line(LEFT * 3.2 + UP * y, RIGHT * 3.2 + UP * y, stroke_width=2, color=GREY_B)
            trk.set_stroke(opacity=0.4)
            tracks.add(trk)
            dots1.append(Dot(radius=0.12, color=cols[i]).move_to(trk.get_start()))
        win.play(FadeIn(labels1), FadeIn(tracks), FadeIn(VGroup(*dots1)), run_time=0.4)   # the four tracks get in place
        win.play(*[d.animate(run_time=1.8, rate_func=f).shift(RIGHT * 6.4)
                   for d, f in zip(dots1, funcs1)])   # parameter "rate_func" x4: running together to pull the positions apart
        win.play(Wait(0.4))   # pause to see the result
        win.play(FadeOut(lab1), FadeOut(labels1), run_time=0.3)   # swap the label
        for d in dots1:   # put them back at the start with no animation: change the attributes directly
            d.move_to(LEFT * 3.2 + UP * d.get_center()[1])
        names2 = ["there_and_back", "exponential_decay", "squish(.35,.65)", "wiggle"]
        funcs2 = [there_and_back, exponential_decay, squish_rate_func(linear, 0.35, 0.65), wiggle]
        labels2 = VGroup()
        for i, nm in enumerate(names2):
            labels2.add(Text(nm, font_size=26, color=cols[i]).move_to(LEFT * 5.6 + UP * (0.55 - i * 1.15)))
        lab2 = Text("reset: 4 more rate_funcs (round-trip / overshoot)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # second batch signature label
        win.play(FadeIn(lab2, shift=DOWN), FadeIn(labels2), run_time=0.3)   # the second batch's label fades in
        win.play(*[d.animate(run_time=1.8, rate_func=f).shift(RIGHT * 6.4)
                   for d, f in zip(dots1, funcs2)])   # parameter "rate_func" x4: round-trip / decay / squish / wobble
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: four colored dots on four tracks run **the same** translation animation, changing only `rate_func` and starting at once, so the positions immediately pull apart:

- `linear` constant speed in the middle;
- `smooth` slow at both ends;
- `rush_into` slow in, fast out;
- `rush_from` fast in, slow out.

Then the same dots are put back at the start with no animation and the second batch runs:

- `there_and_back` returns to the start;
- `exponential_decay` shoots all the way to the end in one step;
- `squish_rate_func(linear, .35, .65)` fast in the middle, slow at both ends;
- `wiggle` wobbles back and forth with an overshoot.

<video src="assets/RTM output/01-Wait-Rate-and-Speed-ratefunc.mp4" controls width="560"></video>

> Note:
>
> - `squish_rate_func(linear, 0.35, 0.65)` is the "call returns a function" idiom — call it first to get the wrapped function, then pass that in.
> - `rate_func` is for **animations with displacement**; using it on `Wait` has no visible effect.

---

See also: [play and wait parameters](../Common/02-play-and-wait-Parameters.md) · [Succession](../Composition/02-Succession.md) · [Updater Animations](../Updater-Animations/01-Updater-Animations.md)
