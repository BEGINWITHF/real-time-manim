# Number animations: ChangingDecimal / ChangeDecimalToValue

Two animation classes that drive a change in a `DecimalNumber`'s displayed value — one takes its value from an arbitrary function, one jumps linearly from the current value to a target value.

## Parameters

### `ChangingDecimal` 

```python
ChangingDecimal(decimal_mob, number_update_func, suspend_mobject_updating=False, **kwargs)
```

Continuously changes the number a `DecimalNumber` displays according to the function `f(alpha) -> value` you provide (each frame `set_value(f(rate_func(alpha)))`), so it can do any time-to-value mapping. A non-`DecimalNumber` input raises `TypeError`. **Inherits** `ChangingDecimal(Animation)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `decimal_mob` | `DecimalNumber` | — | the number object being animated (must be a `DecimalNumber`) |
| `number_update_func` | `Callable[[float], float]` | — | takes the progress `alpha` and returns the value to display |
| `suspend_mobject_updating` | `bool` | `False` | whether to suspend updaters (by default it is not suspended, so it can coexist with a `ValueTracker`) |
| `**kwargs` | … | — | `Animation` common parameters (`run_time`, `rate_func`, …) |

> **Returns**: a `ChangingDecimal` instance.

One-liner:

```python
number = DecimalNumber(0)
self.add(number)
win.play(ChangingDecimal(number, lambda a: 5 * a, run_time=3))
win.play(Wait(1))
```

### `ChangeDecimalToValue` 

```python
ChangeDecimalToValue(decimal_mob, target_number, **kwargs)
```

**Linearly interpolates a `DecimalNumber` from the current value to a target value** (internally `lambda a: interpolate(start, target, a)`); this is the most common "counter jumps to X" idiom. **Inherits** `ChangeDecimalToValue(ChangingDecimal)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `decimal_mob` | `DecimalNumber` | — | the number object being animated |
| `target_number` | `int` | — | the target value; the source annotates `int`, but it actually goes through `interpolate`, so passing a float works just as well |
| `**kwargs` | … | — | `ChangingDecimal`'s `suspend_mobject_updating=False` and `Animation` common parameters (e.g. `run_time=3`) |

> **Returns**: a `ChangeDecimalToValue` instance.

One-liner:

```python
number = DecimalNumber(0)
self.add(number)
win.play(ChangeDecimalToValue(number, 10, run_time=3))
```

> Tip: to **follow a `ValueTracker`** displaying a value over the **long term**, an updater is more appropriate: `number.add_updater(lambda n: n.set_value(tracker.get_value()))` — that is exactly the third segment of this page's clip.
>
> This section of the manual covers only the two classes above. RTM also exports `TextDecimalNumber` (already supported, `real_time_manim.animations.text`), but the manual does not document its signature, so this page does not go into it.

#### Sample: ChangingDecimal / ChangeDecimalToValue / ValueTracker follow

The page clip demonstrates ChangingDecimal → ChangeDecimalToValue → ValueTracker+updater in that order, one segment each, with every parameter labelled on screen.

```python
import os

from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    RED,
    DOWN,
    UP,
    ChangeDecimalToValue,
    ChangingDecimal,
    DecimalNumber,
    Scene,
    Text,
    ValueTracker,
    VGroup,
    linear,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  used by __main__ at the end of the file


class Page_02_Number_Animations(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameters w=1280 / h=720 / hidden=True
        win.scene = self                          # parameter win.scene

        title = Text("ChangingDecimal / ChangeDecimalToValue",
                     font_size=34, color=GREEN).to_edge(UP)   #title uses ASCII only: font fallback stays reliable in both engines
        win.play(Write(title), run_time=0.85)

        # —— step 1: ChangingDecimal(decimal_mob, number_update_func, ...) ——
        s1a = Text("ChangingDecimal(num, lambda a: 5 * a,", font_size=30, color=GREY_B)
        s1b = Text("    suspend_mobject_updating=False, run_time=2.4,", font_size=30, color=GREY_B)
        s1c = Text("    rate_func=linear)", font_size=30, color=GREY_B)
        sig1 = VGroup(s1a, s1b, s1c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        n01 = DecimalNumber(0, num_decimal_places=2, color=BLUE).next_to(sig1, DOWN, buff=0.9)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        self.add(n01)
        win.play(
            ChangingDecimal(
                n01,                                  # parameter decimal_mob ✓ (must be a DecimalNumber)
                lambda a: 5 * a,                      # parameter number_update_func ✓: f(alpha) -> value
                suspend_mobject_updating=False,       # parameter suspend_mobject_updating=False ✓ (can coexist with a ValueTracker)
                run_time=2.4,                         # parameter **kwargs: run_time=2.4 ✓
                rate_func=linear,                     # parameter **kwargs: rate_func=linear ✓
            ),
        )
        win.play(Wait(0.4))
        win.play(FadeOut(sig1), FadeOut(n01), run_time=0.45)

        # —— step 2: ChangeDecimalToValue(decimal_mob, target_number, ...) ——
        s2a = Text("ChangeDecimalToValue(num, target_number=10,",
                   font_size=30, color=GREY_B)
        s2b = Text("    run_time=2.4, rate_func=linear,", font_size=30, color=GREY_B)
        s2c = Text("    suspend_mobject_updating=False)", font_size=30, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        n02 = DecimalNumber(0, num_decimal_places=2, color=RED).next_to(sig2, DOWN, buff=0.9)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        self.add(n02)
        win.play(
            ChangeDecimalToValue(
                n02,                                  # parameter decimal_mob ✓
                10,                                   # parameter target_number=10 ✓ (the source annotates int; a float works just as well)
                run_time=2.4,                         # parameter **kwargs: run_time=2.4 ✓
                rate_func=linear,                     # parameter **kwargs: rate_func=linear ✓
                suspend_mobject_updating=False,       # parameter **kwargs: inherited from ChangingDecimal ✓
            ),
        )
        win.play(Wait(0.3))
        win.play(FadeOut(sig2), FadeOut(n02), run_time=0.45)

        # —— step 3: the page's "tip" — use ValueTracker + updater for long-term following ——
        s3a = Text("tracker = ValueTracker(0)", font_size=30, color=GREY_B)
        s3b = Text("num.add_updater(lambda n: n.set_value(tracker.get_value()))",
                   font_size=30, color=GREY_B)
        s3c = Text("win.play(tracker.animate.set_value(7.5), run_time=2)",
                   font_size=30, color=GREY_B)
        sig3 = VGroup(s3a, s3b, s3c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        tracker = ValueTracker(0)
        n03 = DecimalNumber(0, num_decimal_places=1, color=GREEN).next_to(sig3, DOWN, buff=0.9)
        n03.add_updater(lambda n: n.set_value(tracker.get_value()))
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.45)
        self.add(n03)
        win.play(tracker.animate.set_value(7.5), run_time=2, rate_func=linear)
        n03.clear_updaters()
        win.play(FadeOut(sig3), FadeOut(n03), run_time=0.5)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()
```

What this code does: all three segments are "a number changing".

- Segment 1: the blue `DecimalNumber` uses `ChangingDecimal` with `lambda a: 5 * a` to climb uniformly from 0.00 to 5.00 (`rate_func=linear`, 2.4 s).
- Segment 2: the red number uses `ChangeDecimalToValue` to jump straight from the current value to 10.00.
- Segment 3 demonstrates the long-term-follow idiom — a `ValueTracker` is pushed from 0 to 7.5 and `num.add_updater(...)` makes the green number read its value every frame (when done, `clear_updaters()` unbinds it).

The first two segments are "one-shot" animations while the third is a "binding", and that is the most useful lesson on this page.

<video src="assets/RTM output/02-Number-Animations.mp4" controls width="560"></video>

> Note:
>
> - `ChangingDecimal`/`ChangeDecimalToValue` only accept a `DecimalNumber`; feeding them another type raises `TypeError`.
> - They are **one-shot** animations: when they finish the number stops at the end point; do not expect it to keep following.
> - For "a number that always follows some quantity", use the `add_updater` idiom from the third segment, and remember `clear_updaters()` before unbinding; otherwise later operations such as `FadeOut` will still be pulled back to the old value by the updater.

See also: [Updater Animations](../Updater-Animations/01-Updater-Animations.md) · [Writing and Unwriting](01-Writing-and-Unwriting.md) · [ValueTracker](../../02-Mobjects/10-ValueTracker.md)
