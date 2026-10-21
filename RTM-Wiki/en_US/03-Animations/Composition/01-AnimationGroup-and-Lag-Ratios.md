# AnimationGroup and lag ratios: LaggedStart / LaggedStartMap

The first half of the handbook's "8. Composing animations": the basic composition tool that plays several animations as one, plus its two streaming staggered variants.

`AnimationGroup` uses RTM's own implementation. `LaggedStart` / `LaggedStartMap` are not in RTM's own export list; they use manim's native classes rendered through RTM's timeline, and both the streaming stagger and the batch animation effects measured identical.

## Parameters

### AnimationGroup

```python
AnimationGroup(*animations, group=None, run_time=None, rate_func=linear, lag_ratio=0, **kwargs)
```

Inherits `AnimationGroup(Animation)`, source `animation/composition.py`. It plays several animations **as one animation**: with `run_time=None` the total duration is automatically the maximum end time of the timeline laid out by `lag_ratio`; if `run_time` is given, the whole thing is stretched/compressed to that duration. `lag_ratio` decides **at what fraction of the previous animation the next one starts** (`start[i+1] = start[i] + run_time[i] * lag_ratio`).

The children can be any animation or an `.animate` builder, and `AnimationGroup`s can be **nested**.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*animations` | `Animation \| Iterable[Animation]` | — | child animations (lists/generators are flattened automatically; each goes through `prepare_animation`). **What can be passed**: any animation and an `.animate` builder |
| `group` | `Group \| None` | `None` | manually specify the container for the whole group; by default the mobjects of all non-introducer child animations are collected into one `Group`. Accepted with CE semantics (container mobjects are collected into the group and returned by `get_all_mobjects()`) |
| `run_time` | `float \| None` | `None` | total duration; `None` = computed automatically from the child timeline. Constructor passing is now supported: when non-`None`, the child timeline is stretched/compressed as a whole with CE semantics; attribute assignment `ag.run_time = 1.8` still works (the sample uses it) |
| `rate_func` | `Callable` | `linear` | **group-level** rate function (applied to the whole timeline; child animations still have their own `rate_func`). **What can be passed**: `linear`, `smooth`, … |
| `lag_ratio` | `float` | `0` | `0` all start together; `0.5` the next starts when the previous is half done; `1` fully in succession |
| `**kwargs` | `Any` | — | common `Animation` parameters (`name`, `remover`, `introducer`, `suspend_mobject_updating`, …); `synchronize_with_wall_clock` is unsupported and **explicitly rejected**: `True` raises `ValueError` |

> **Returns**: an `Animation` (hand it to `play`).

Composition tips (same handbook section):

- passing `run_time=1.5` at the `play` level flattens several animations uniformly;
- `lag_ratio=0.3` gives a "start in turn" effect;
- when nesting, the outer level shapes the large rhythm and the inner level the small moves;
- an outer `lag_ratio=1` means "the previous group finishes completely before the next one plays".

#### Sample: three .animate builders start in turn, the whole axis stretched to 1.8 seconds

A red square, a blue circle and a green triangle each get an `.animate.shift` packed into an `AnimationGroup`; `lag_ratio=0.5` makes the three actions start in turn; the attribute assignment `ag.run_time = 1.8` stretches the whole timeline to 1.8 seconds.

```python
from real_time_manim import Scene, Text, VGroup, Square, Circle, Triangle, RED, BLUE, GREEN, \
    GREY_B, YELLOW, UP, DOWN, LEFT, RIGHT, FadeIn, Write, linear
from real_time_manim.vulkan_bind import MLWindow, AnimationGroup, Wait

class AnimationGroupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01-AnimationGroup", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        l1 = Text("AnimationGroup(sq.animate.shift(UP),", font_size=30, color=GREY_B)
        l2 = Text("              ci.animate.shift(DOWN), tr.animate.shift(UP),", font_size=28, color=GREY_B)
        l3 = Text("              lag_ratio=0.5, rate_func=linear);  ag.run_time = 1.8", font_size=28, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #signature labels
        sq = Square(side_length=1.2, color=RED).set_fill(RED, 0.5).shift(LEFT * 3.4 + DOWN * 2.1)   #red square
        ci = Circle(radius=0.65, color=BLUE).set_fill(BLUE, 0.5).shift(DOWN * 2.1)   #blue circle
        tr = Triangle(color=GREEN).scale(0.8).set_fill(GREEN, 0.5).shift(RIGHT * 3.4 + DOWN * 2.1)   #green triangle
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(sq, ci, tr)), run_time=0.4)   #labels and shapes fade in
        ag = AnimationGroup(                                      #param "*animations" (3 .animate builders)
            sq.animate.shift(UP * 1.4),
            ci.animate.shift(DOWN * 1.4),
            tr.animate.shift(UP * 1.4),
            lag_ratio=0.5,                                        #param "lag_ratio" (red → blue → green start in turn)
            rate_func=linear,                                     #param "rate_func" (group-level)
        )
        ag.run_time = 1.8                                         #param "run_time" (attribute assignment stretches the whole axis to 1.8s)
        win.play(ag)   #the three actions start in turn
        win.play(Wait(0.6))   #hold to see the result
        win.close()   #close the RTM window
```

What this code does: the red square moves first, the blue circle only starts once the red square is half done, and the green triangle waits one more round — `lag_ratio=0.5` is "the next starts when the previous is 50% done".

After the three actions are collected into a single `play`, the attribute assignment `ag.run_time = 1.8` stretches the whole timeline to 1.8 seconds.

<video src="assets/RTM output/01-AnimationGroup-and-Lag-Ratios-animationgroup.mp4" controls width="560"></video>

> Note: `lag_ratio` is "**at what fraction of the previous animation** the next starts", not a gap in seconds.
>
> - `0.5` = half done
> - `1` = fully in succession
> - `0` = all together
>
> Both passing `run_time` to the constructor and the attribute assignment `ag.run_time = 1.8` work.

### LaggedStart

```python
LaggedStart(*animations, lag_ratio=0.05, **kwargs)
```

Inherits `LaggedStart(AnimationGroup)`, source `animation/composition.py`. It is a convenience version of `AnimationGroup`: `lag_ratio` defaults to **0.05**, i.e. "the next starts after the previous has played 5%", used to create a **streaming stagger**. The semantics are exactly the same as `AnimationGroup`; only the default is staggered rather than simultaneous.

The sample uses manim's own `LaggedStart` rendered through RTM's timeline; the stagger works normally.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*animations` | `Animation \| Iterable[Animation]` | — | child animations, as in `AnimationGroup`. **What can be passed**: e.g. `*[FadeIn(d, shift=DOWN) for d in dots]` |
| `lag_ratio` | `float` | `0.05` | lag ratio (different from `AnimationGroup`'s `0`). **What can be passed**: 0~1 |
| `**kwargs` | `Any` | — | same as `AnimationGroup`: `group`, `run_time=None`, `rate_func=linear` and the common `Animation` parameters |

> **Returns**: an `Animation` (hand it to `play`).

#### Sample: 5 coloured dots fade in with a streaming stagger

Five `FadeIn`s in different colours go to `LaggedStart`, with the lag ratio raised to 0.3; the dots fade in one after another like a stream.

```python
from real_time_manim import Scene, Text, VGroup, Dot, RED, YELLOW, GREEN, BLUE, PURPLE, \
    GREY_B, UP, DOWN, LEFT, RIGHT, FadeIn, LaggedStart, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class LaggedStartDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01-LaggedStart", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        l1 = Text("LaggedStart(*[FadeIn(d, shift=DOWN) for d in dots],", font_size=30, color=GREY_B)
        l2 = Text("            lag_ratio=0.3, run_time=1.6)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #signature labels
        cols = [RED, YELLOW, GREEN, BLUE, PURPLE]   #colours of the 5 lanes
        dots = VGroup(*[Dot(radius=0.18, color=c).shift(LEFT * 4.4 + RIGHT * 2.2 * i + DOWN * 1.8)   #5 coloured dots
                        for i, c in enumerate(cols)])
        win.play(FadeIn(sig, shift=DOWN), run_time=0.4)   #labels fade in
        win.play(LaggedStart(                                    #param "*animations" (5 FadeIns in different colours)
            *[FadeIn(d, shift=DOWN) for d in dots],
            lag_ratio=0.3,                                       #param "lag_ratio" (streaming stagger)
            run_time=1.6,                                        #param "run_time"
        ))
        win.play(Wait(0.6))   #hold to see the result
        win.close()   #close the RTM window
```

What this code does: the only difference from `AnimationGroup` is the default — `LaggedStart` sets `lag_ratio` to 0.05 by default, and here it is raised to 0.3. The five dots fade in one after another like a stream, and `run_time=1.6` controls the group's total duration.

<video src="assets/RTM output/01-AnimationGroup-and-Lag-Ratios-laggedstart.mp4" controls width="560"></video>

> Note: `LaggedStart` / `LaggedStartMap` are not in RTM's own export list of 39 classes. The sample (see the code block) can just `from real_time_manim import LaggedStart`; what you get is the **built-in ManimCE version** (the top level = `from manim import *`, so `from manim import LaggedStart` is the same class). The timeline drives it as usual, frame-for-frame identical to CE.

### LaggedStartMap

```python
LaggedStartMap(animation_class, mobject, arg_creator=None, run_time=2, lag_ratio=0.05, **kwargs)
```

Inherits `LaggedStartMap(LaggedStart)`, source `animation/composition.py`. For **each submobject** of `mobject` it builds one `animation_class` and plays them staggered — the shortest way to "apply an animation to a whole family by class". `arg_creator(submob)` turns a submobject into that animation's argument list; when it is not given, the submobject itself is passed by default.

The sample likewise uses manim's own class and was rendered for real.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `animation_class` | `type[Animation]` | — | the animation class to instantiate in bulk. **What can be passed**: `FadeIn`, `ApplyMethod`, … |
| `mobject` | `Mobject` | — | the container walked, **submobject** by submobject |
| `arg_creator` | `Callable \| None` | `None` | `submob -> (animation argument tuple)`; with `None`, `submob` is passed as the only argument. **What can be passed**: e.g. `lambda m: (m.set_color, YELLOW)` |
| `run_time` | `float` | `2` | group total duration |
| `lag_ratio` | `float` | `0.05` | lag ratio (if passed again in `**kwargs` it is stripped; this parameter wins) |
| `**kwargs` | `Any` | — | parameters passed to **each** `animation_class` instance (e.g. `rate_func=there_and_back`) |

> **Returns**: an `Animation` (hand it to `play`).

#### Sample: arg_creator tints each letter yellow in turn, then back

`arg_creator` turns each letter of "manim" into `ApplyMethod(set_color)`; each letter is tinted yellow and then, via `there_and_back`, returns to its own colour.

```python
from real_time_manim import Scene, Text, GREY_B, YELLOW, UP, DOWN, FadeIn, LaggedStartMap, \
    ApplyMethod, Write, there_and_back
from real_time_manim.vulkan_bind import MLWindow, Wait

class LaggedStartMapDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01-LaggedStartMap", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        l1 = Text("LaggedStartMap(ApplyMethod, words,", font_size=30, color=GREY_B)
        l2 = Text("   lambda m: (m.set_color, YELLOW),", font_size=30, color=GREY_B)
        l3 = Text("   lag_ratio=0.15, run_time=2.0, rate_func=there_and_back)", font_size=28, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #signature labels
        words = Text("manim", font_size=64, color=GREY_B).shift(DOWN * 1.9)   #the word tinted letter by letter
        win.play(FadeIn(sig, shift=DOWN), FadeIn(words), run_time=0.4)   #labels and word fade in
        win.play(LaggedStartMap(                                 #param "animation_class / mobject / arg_creator"
            ApplyMethod, words,
            lambda m: (m.set_color, YELLOW),                     #param "arg_creator" (submob -> argument tuple)
            lag_ratio=0.15,                                      #param "lag_ratio"
            run_time=2.0,                                        #param "run_time"
            rate_func=there_and_back,                            #param "**kwargs" (passed through to each child animation)
        ))
        win.play(Wait(0.6))   #hold to see the result
        win.close()   #close the RTM window
```

What this code does: no need to hand-write 5 `ApplyMethod`s — `LaggedStartMap` walks each letter of "manim" and `arg_creator` turns a submobject into animation arguments (here, tinting it yellow). `there_and_back` is passed to each child animation through `**kwargs`, so a letter returns to its original colour after being tinted.

<video src="assets/RTM output/01-AnimationGroup-and-Lag-Ratios-laggedstartmap.mp4" controls width="560"></video>

> Note: `LaggedStartMap`'s `**kwargs` are passed to **each child animation** (like `rate_func=there_and_back` here), not group-level parameters; when `arg_creator` is not given, the submobject itself is used as the only argument.

---

See also: [Succession](02-Succession.md) · [Special entrances](../Movement-and-Rotation/03-Special-Entrances.md) · [play and wait parameters](../Common/02-play-and-wait-Parameters.md)
