# Rate functions

A rate function maps animation progress `t ∈ [0, 1]` to actual progress `f(t)`; pass it via `play(..., rate_func=...)` — the same shift with a different curve feels completely different.

The common functions are exported at the top level (`rate_func=smooth`); the standard easings `ease_*` are **not exported**, so you must write `rate_func=rate_functions.ease_out_bounce`. Close relatives like `smoothstep` / `smootherstep` and the `ease_*` family go through the generic fallback, rendered by RTM with per-point evaluation (`use_vectorized=False`; the scalar implementation is equally safe).

The three samples draw "four common curves", "four decorated curves" and "one movement × four rates", respectively; all have been rendered in RTM.

> **2026-10-17 update (unified counting)**: in manim 0.21 the `manim.utils.rate_functions` module **defines 50 names** = **47 rate functions** (`__all__` lists 17 explicitly + the full `ease_*` family of 30 taken as module attributes) + 2 decorators (`unit_interval` / `zero`) + 1 `Protocol` (`RateFunction`) — matching this page's four sections 12 + 5 + 30 + 3 = 50 item by item. `real_time_manim` exports **17** of them at the top level (12 common + 5 special/factory); the 30 `ease_*` and the decorators/`Protocol` are not at the top level and need the `rate_functions.` prefix.

## `rate_func` (the animation parameter of `play`)

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `rate_func` | `Callable[[float], float]` | `smooth` | Can be: a top-level common function (`linear`, `smooth`, `rush_into`, …), a factory product (`squish_rate_func(smooth, 0.2, 0.8)`), or a `rate_functions.ease_*` standard easing; input `t ∈ [0, 1]`, output actual progress (**may exceed 0-1** — fine for movement, but don't use overshooting functions for `set_opacity`-type properties) |

#### Sample: one movement × four rates

Four lanes draw the exact same movement track; in a small box to the left of each track is a thumbnail of that lane's rate curve, and four same-colored dots start together — only `rate_func` differs, and their positions separate immediately; the `there_and_back` dot even runs back to the start at the end.

```python
from real_time_manim import Scene, Text, VGroup, Line, Dot, Arrow, Rectangle, \
    FunctionGraph, BLUE, GREEN, RED, YELLOW, GREY_B, UP, DOWN, LEFT, \
    FadeIn, Write, Create
from real_time_manim import linear, rush_into, smooth, \
    there_and_back
from real_time_manim.vulkan_bind import MLWindow, Wait

class RateMotionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("02-rate_func on a shift", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        names = ["linear", "smooth", "rush_into", "there_and_back"]   #one rate per lane
        funcs = [linear, smooth, rush_into, there_and_back]
        cols = [GREY_B, BLUE, GREEN, RED]
        xs0, xs1 = -2.4, 6.0   #start and end of the movement track (identical for all four)
        mx0, mx1 = -5.0, -3.0   #horizontal extent of the small curve box on the left
        lanes, dots = [], []
        for i, (nm, f, c) in enumerate(zip(names, funcs, cols)):
            y = 1.9 - i * 1.2   #y coordinate of each lane
            box = Rectangle(width=mx1 - mx0, height=1.0, stroke_width=1)
            box.set_stroke(GREY_B, 1, opacity=0.5).set_fill(opacity=0)   #hollow little box as the plot area
            box.move_to([(mx0 + mx1) / 2, y, 0])
            lab = Text(nm, font_size=15, color=c).next_to(box, LEFT, buff=0.25)   #lane name to the left of the curve box

            def g(u, f=f):   #draw this lane's rate function into the box (x 0→1, y 0→1)
                t = (u - mx0) / (mx1 - mx0)
                v = f(t)
                v = 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)   #clamp out-of-range values to the box edge
                return y + (v - 0.5) * 0.8   #f=0 → box bottom, f=1 → box top

            curve = FunctionGraph(g, x_range=[mx0, mx1, (mx1 - mx0) / 40],
                                  color=c, stroke_width=3)   #thumbnail of this lane's rate curve
            trk = Line([xs0, y, 0], [xs1, y, 0], color=GREY_B, stroke_width=2)
            trk.set_stroke(opacity=0.4)   #movement track (translucent grey line)
            dot = Dot([xs0, y, 0], radius=0.13, color=c)   #starting dot, same color as the curve
            lanes += [box, lab, curve, trk]
            dots.append((dot, y, f))
        note = Text("same shift, only rate_func differs", font_size=19, color=YELLOW).to_edge(DOWN)   #bottom note
        win.play(FadeIn(VGroup(*lanes)), FadeIn(note), run_time=0.5)   #the four lanes and the note settle into place
        self.add(*[d for d, _, _ in dots])   #add the four dots to the scene (all start at the left end of the track)
        win.play(*[d.animate(run_time=1.6, rate_func=f).move_to([xs1, y, 0])
                   for d, y, f in dots])   #the "rate_func" parameter: one movement × four rates starting together
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: the four lanes have identical tracks, start points and durations; the only variable is the `rate_func` passed to `animate`:

- `linear` covers it at constant speed;
- `smooth` is slow at both ends, fast in the middle;
- `rush_into` starts extremely slow and sprints at the end;
- `there_and_back` goes to the end and returns to the start.

The same-colored curve in each small box is that lane's `f(t)` shape; the dot's live position matches the curve height frame by frame.

<video src="assets/RTM output/02-Rate-Functions-motion.mp4" controls width="560"></video>

> Note:
>
> - `rate_func` takes a **progress→progress** function, not an easing timestamp.
> - Functions like `there_and_back` / `wiggle` return to zero at the end of the animation, which shows up as "back to the start" for a movement; using them to drive strict-0-1 properties such as `set_fill(opacity=...)` misbehaves.

## Common rate functions (directly usable at top level) (12)

| Function | RTM | Frequency | Curve shape |
| --- | --- | --- | --- |
| `linear` | — | 🔴 | identity line `y = t`, constant speed |
| `smooth` | — | 🔴 | S-shaped sigmoid (`inflection=10`), smooth start and finish — **Manim's default for most animations** |
| `smoothstep` | — | 🟡 | `3t²−2t³`, first derivative 0 at the endpoints, the classic SmoothStep |
| `smootherstep` | — | 🟡 | `6t⁵−15t⁴+10t³`, first and second derivatives 0 at the endpoints, softer than smoothstep |
| `smoothererstep` | — | ⚪ | third-order smooth version (up to third derivative zero), the softest S shape |
| `there_and_back` | — | 🔴 | out and back: 0→1→0, fastest at the midpoint, good for "bounce then reset" |
| `there_and_back_with_pause` | — | 🟡 | as above but holds at the far end for `pause_ratio=1/3` of the time before returning |
| `exponential_decay` | — | 🔴 | `1−e^(−t/0.1)`: rushes near the end instantly, then a long tail converges; good for "fly in and settle" |
| `rush_into` | — | 🟡 | accelerating curve: very slow start, hard charge to the end (abrupt stop) |
| `rush_from` | — | 🟡 | decelerating curve: hard start, gentle settle |
| `slow_into` | — | ⚪ | quarter circle `sqrt(1−(1−t)²)`: starts at full speed, decays to 0 (no ease-in) |
| `double_smooth` | — | ⚪ | a `smooth` over each half; a brief "pause" near the midpoint |

#### Sample: curves of four common rate functions

In a coordinate system with progress `t` on the x-axis and actual progress `f(t)` on the y-axis, draw the four curves `linear`, `smooth`, `rush_into`, `rush_from` one by one, with a same-colored legend on the right — when `f(t)` is above the diagonal the animation runs ahead, below it lags.

```python
from real_time_manim import Scene, Text, VGroup, Arrow, FunctionGraph, BLUE, \
    GREEN, RED, YELLOW, GREY_B, UP, DOWN, LEFT, FadeIn, Write, Create
from real_time_manim import linear, rush_from, rush_into, smooth
from real_time_manim.vulkan_bind import MLWindow, Wait

class RateCurveCommonDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("02-common rate_funcs", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        x0, x1, y0, y1 = -6.0, 2.6, -2.4, 1.8   #plot area: t left to right, f(t) bottom to top
        lo, hi = -0.05, 1.05   #vertical display range (5% margin at each end)

        def plot(f, color):   #draw a rate function as a curve: map screen x back to t, then map f(t) into the plot area
            def g(u):
                t = (u - x0) / (x1 - x0)   #screen x → progress t
                y = f(t)   #actual progress given by the rate function
                if y < lo:
                    y = lo   #clamp out-of-range values (wiggle in sample 2 overshoots 0-1)
                elif y > hi:
                    y = hi
                return y0 + (y - lo) / (hi - lo) * (y1 - y0)   #map to a scene y coordinate
            return FunctionGraph(g, x_range=[x0, x1, (x1 - x0) / 96], color=color, stroke_width=5)

        xax = Arrow([x0 - 0.3, y0, 0], [x1 + 0.4, y0, 0], color=GREY_B, stroke_width=4, buff=0)   #x-axis: progress t
        yax = Arrow([x0, y0 - 0.3, 0], [x0, y1 + 0.35, 0], color=GREY_B, stroke_width=4, buff=0)   #y-axis: actual progress f(t)
        lt = Text("t", font_size=22, color=GREY_B).next_to(xax, DOWN, buff=0.12)   #x-axis name
        lf = Text("f(t)", font_size=22, color=GREY_B).next_to(yax, UP, buff=0.12)   #y-axis name
        l0 = Text("0", font_size=18, color=GREY_B).next_to([x0, y0, 0], DOWN, buff=0.15)   #origin tick
        l1t = Text("1", font_size=18, color=GREY_B).next_to([x1, y0, 0], DOWN, buff=0.15)   #t=1 tick
        l1f = Text("1", font_size=18, color=GREY_B).next_to([x0, y1, 0], LEFT, buff=0.15)   #f(t)=1 tick
        win.play(FadeIn(VGroup(xax, yax, lt, lf, l0, l1t, l1f)), run_time=0.4)   #axes position first

        names = ["linear", "smooth", "rush_into", "rush_from"]   #four common rate functions
        funcs = [linear, smooth, rush_into, rush_from]
        cols = [GREY_B, BLUE, GREEN, RED]
        for i, (nm, f, c) in enumerate(zip(names, funcs, cols)):
            g = plot(f, c)   #the i-th curve
            lab = Text(nm, font_size=17, color=c).move_to([3.2, 1.2 - i * 0.8, 0])   #same-color legend on the right
            win.play(Create(g), run_time=0.6)   #draw each curve in turn
            win.play(FadeIn(lab), run_time=0.2)   #then add its name
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: it first sets up the "t across, f(t) up" coordinate system, then draws the four common rate functions one by one:

- grey `linear` is the diagonal (constant speed);
- blue `smooth` is the S shape, gentle at the ends and steep in the middle;
- green `rush_into` stays below the diagonal throughout (slow start, catches up later);
- red `rush_from` is the opposite (fast start, trailing end).

The four curves share one `plot` wrapper: the screen x coordinate is mapped back to `t`, and `f(t)` is then mapped linearly into the plot area.

<video src="assets/RTM output/02-Rate-Functions-curves_common.mp4" controls width="560"></video>

> Note:
>
> - The 12 common functions such as `linear` / `smooth` are exported directly at the `manim` top level; `from manim import linear` or `from manim.utils.rate_functions import linear` both work.
> - The `smoothstep` family, when not listed separately, goes through the generic fallback with per-point evaluation (`use_vectorized=False`); the curve shape is identical, but it does not take the vectorized fast path.

## Special-purpose and factory functions (5)

| Function | RTM | Frequency | Curve shape and use |
| --- | --- | --- | --- |
| `running_start(t, pull_factor=-0.5)` | — | 🟡 | pulls **backwards** a bit first, then rushes to the end — a springy "anticipation" feel |
| `wiggle(t, wiggles=2)` | — | 🟡 | `there_and_back × sin(wiggles·π·t)`, oscillating between 0 and 1 `wiggles` times |
| `lingering` | — | ⚪ | linear over `[0, 0.8]`, then holds still for the last 20% (lingering finish) |
| `not_quite_there(func=smooth, proportion=0.7)` | — | 🟡 | **factory**: reaches only `proportion` × the `func` result, always "not quite there" |
| `squish_rate_func(func, a=0.4, b=0.6)` | — | 🔴 | **factory**: squishes `func` into the time interval `[a, b]`, holding 0 before and 1 after |

#### Sample: factory / back-and-forth / standard easing curves

Four "decorated" rate functions in the same coordinate system:

- `squish_rate_func(smooth, 0.2, 0.8)` squeezes the S curve into 0.2-0.8;
- `wiggle(t, 3)` oscillates three times;
- `lingering` lingers at the end;
- `rate_functions.ease_out_bounce` is a ball bouncing on landing.

This group overshoots 0-1, so the y-axis range is widened to −1.1-1.4.

```python
from real_time_manim import Scene, Text, VGroup, Arrow, FunctionGraph, RED, \
    YELLOW, TEAL, PURPLE, GREY_B, UP, DOWN, LEFT, FadeIn, Write, Create
from real_time_manim import rate_functions
from real_time_manim import lingering, smooth, squish_rate_func, \
    wiggle
from real_time_manim.vulkan_bind import MLWindow, Wait

class RateCurveFactoryDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("02-squish / wiggle / ease", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        x0, x1, y0, y1 = -6.0, 2.6, -2.4, 1.8   #plot area
        lo, hi = -1.1, 1.4   #this group overshoots 0-1 (wiggle oscillates, ease pulls back), so widen the range

        def ypos(v):   #convert an f value to a scene y coordinate (for tick labels)
            return y0 + (v - lo) / (hi - lo) * (y1 - y0)

        def plot(f, color):   #likewise draw a rate function as a curve
            def g(u):
                t = (u - x0) / (x1 - x0)   #screen x → progress t
                y = f(t)   #actual progress given by the rate function
                if y < lo:
                    y = lo   #clamp to the display bounds
                elif y > hi:
                    y = hi
                return ypos(y)
            return FunctionGraph(g, x_range=[x0, x1, (x1 - x0) / 96], color=color, stroke_width=5)

        xax = Arrow([x0 - 0.3, y0, 0], [x1 + 0.4, y0, 0], color=GREY_B, stroke_width=4, buff=0)   #x-axis: progress t
        yax = Arrow([x0, y0 - 0.3, 0], [x0, y1 + 0.35, 0], color=GREY_B, stroke_width=4, buff=0)   #y-axis: actual progress f(t)
        lt = Text("t", font_size=22, color=GREY_B).next_to(xax, DOWN, buff=0.12)   #x-axis name
        lf = Text("f(t)", font_size=22, color=GREY_B).next_to(yax, UP, buff=0.12)   #y-axis name
        ticks = VGroup(*[Text(v, font_size=17, color=GREY_B).next_to([x0, ypos(float(v)), 0], LEFT, buff=0.15)
                         for v in ("1", "0", "-1")])   #three y-axis ticks: 1 top, 0 middle, -1 bottom
        l1t = Text("1", font_size=18, color=GREY_B).next_to([x1, y0, 0], DOWN, buff=0.15)   #t=1 tick
        win.play(FadeIn(VGroup(xax, yax, lt, lf, ticks, l1t)), run_time=0.4)   #axes position first

        names = ["squish(smooth, .2, .8)", "wiggle(t, 3)", "lingering", "ease_out_bounce"]   #four "decorated" rate functions
        funcs = [squish_rate_func(smooth, 0.2, 0.8), lambda t: wiggle(t, 3),
                 lingering, rate_functions.ease_out_bounce]
        cols = [PURPLE, RED, YELLOW, TEAL]
        for i, (nm, f, c) in enumerate(zip(names, funcs, cols)):
            g = plot(f, c)   #the i-th curve
            lab = Text(nm, font_size=16, color=c).move_to([3.4, 1.2 - i * 0.8, 0])   #same-color legend on the right
            win.play(Create(g), run_time=0.6)   #draw each curve in turn
            win.play(FadeIn(lab), run_time=0.2)   #then add its name
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: each of the four curves is one "decoration".

- purple is the product of the factory `squish_rate_func(smooth, 0.2, 0.8)` — the S curve that used to span the whole range is squeezed into 0.2-0.8 (horizontal at both ends);
- red `wiggle(t, 3)` swings back and forth three times between 0 and 1;
- yellow `lingering` completes 80% and then stays put;
- teal `ease_out_bounce` is the landing bounce among the standard easings: it overshoots past 1 and bounces back.

Together the four show that a rate function need not be a predefined name: you can machine one on the spot with a factory, and it may even overshoot 0-1.

<video src="assets/RTM output/02-Rate-Functions-curves_factory.mp4" controls width="560"></video>

> Note:
>
> - `squish_rate_func` is a **factory** — you must call it (`squish_rate_func(smooth, 0.2, 0.8)` returns a new function); writing `rate_func=squish_rate_func` passes the factory itself and blows up only at runtime.
> - `ease_out_bounce` is not exported at the top level; write the full `rate_functions.ease_out_bounce`.

## Standard easings `rate_functions.ease_*` (30, from easings.net)

> 10 families × 3 kinds (`_in` ease-in / `_out` ease-out / `_in_out` both ends), **all must be prefixed with `rate_functions.`**; sample 2 already features `ease_out_bounce` (landing bounce), and the rest of that family are drawn exactly the same way.

| Family | Ease-in `ease_in_*` | Ease-out `ease_out_*` | Ease-in-out `ease_in_out_*` | Family character |
| --- | --- | --- | --- | --- |
| `_sine` | slow-start sine acceleration | slow-finish sine deceleration | slow at both ends, fast in the middle | softest, no overshoot |
| `_quad` | quadratic acceleration start | quadratic deceleration to the end | quadratic, slow at both ends | basic sense of acceleration |
| `_cubic` | cubic start (barely moves at first) | cubic finish | cubic, slow at both ends | the higher the power, the sharper the middle |
| `_quart` | quartic start | quartic finish | quartic, slow at both ends | as above, more extreme |
| `_quint` | quintic start | quintic finish | quintic, slow at both ends | the polynomial with the dullest start among the 10 families |
| `_expo` | exponential: barely moves for the first 90% | exponential: arrives instantly, then fine-tunes | almost still at both ends | strongest contrast |
| `_circ` | circular-arc ease-in | circular-arc ease-out | circular, slow at both ends | a distinct right-angle feel at the boundary |
| `_back` | pulls back, overshoots, then returns | overshoots the target, then rebounds once | pulls back once at each end | **has pull-back/overshoot** |
| `_elastic` | spring-stretch oscillation at the start (can be negative) | spring-rebound oscillation at the end | oscillates at both ends | most pronounced oscillation, can exceed [0,1] |
| `_bounce` | reverse bounce (like a replayed landing) | a ball bouncing several times on landing | bounces at both ends | stepped bouncing |

> Note: the intermediate values of `_back`, `_elastic` and `_bounce` exceed `[0, 1]`; fine for movement animations, but don't use them to drive strict-0-1 properties like `set_opacity`.

## Decorators and protocol (rarely used, 3)

> These 3 names are **not** exported at the `manim` top level and need the `rate_functions.` prefix; none are built into RTM (generic fallback).

| Name | Kind | Meaning |
| --- | --- | --- |
| `unit_interval(func)` | decorator | guarantees `t<0 → 0`, `t>1 → 1`, calling the original only inside the interval; applied to all "normal progress" rate functions |
| `zero(func)` | decorator | guarantees `t` outside `[0,1]` returns 0; used by `there_and_back`, `wiggle` for "reset at end" |
| `RateFunction` | Protocol class | for type annotations: `def __call__(self, t: float, *args, **kwargs) -> float` |

Not demonstrated: `unit_interval` / `zero` / `RateFunction` — the decorators wrap other functions and the Protocol is type-only, so a separate clip would be frame-identical to the original function (the curves in sample 1 are already the final form after `unit_interval` is applied).

`smoothstep` / `smootherstep` / `smoothererstep` / `double_smooth` / `slow_into` / `exponential_decay` / `there_and_back_with_pause` and other S-shaped variants, plus the remaining 29 `ease_*` — drawn exactly like samples 1/2 (using the same `plot`); the shape differences are in the table above.

`running_start` / `not_quite_there` and other unlisted ones go through the generic fallback; see the table for their shapes.

---

See also: [Colors](01-Colors.md) | [Directions and Constants](03-Directions-and-Constants.md)
