# Animation lifecycle and common constructor parameters

Every animation class (`Create`/`FadeIn`/…) inherits `Animation`'s four-phase lifecycle and shares one set of common constructor parameters; RTM's `win.play(...)` accepts these keyword arguments. Understand these two and many a "why" answers itself.

## Parameters

### `Animation` (animation base class: lifecycle + common constructor parameters)

```python
Animation(mobject, lag_ratio=0.0, run_time=1.0, rate_func=smooth,
          reverse_rate_function=False, name=None, remover=False,
          suspend_mobject_updating=True, introducer=False, use_override=True)
```

Every animation object goes through four phases in one `win.play(...)`; **you don't need to override them**, but understanding them explains a lot of "why"s:

| Phase | When | What it does |
| --- | --- | --- |
| `begin()` | one-time initialisation before playback | saves `starting_mobject = mobject.copy()`, builds the target, and suspends the updater if needed (when `suspend_mobject_updating=True`) |
| `interpolate(alpha)` | called once per frame, `alpha` 0 → 1 | the actual interpolation; `rate_func` and `lag_ratio` both take effect here (`get_sub_alpha()` computes each submobject's own progress) |
| `finish()` | when playback ends | forces `interpolate(1)` and restores the updater |
| `_setup_scene()` / `clean_up_from_scene(scene)` | before start / after end | adds the **introducer**'s mobject to the scene before starting; removes the **remover**'s mobject from the scene after ending |

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject \| None` | `None` | the object animated; **what can be passed**: any `Mobject`. With `None` an empty `Mobject` is used (you normally pass one for anything other than `Wait`/`Add`) |
| `run_time` | `float` | `1.0` | total animation duration (seconds). **What can be passed**: any positive number. **RTM's own classes do not validate at construction time** (the value is stored directly; negative/0 doesn't error); the **ManimCE version** raises `ValueError("The run_time of Animation cannot be negative...")` at construction time (`0` does not error). RTM's fallback lives in `win.play`: it raises `ValueError` for **a whole play whose total `run_time <= 0`** (`window/play.py:_validate_play_run_time`, matching CE's `Scene.validate_run_time`), and a positive value smaller than one frame is raised to one frame with a warning |
| `lag_ratio` | `float` | `0.0` | submobject lag ratio: submobject `i`'s progress = `rate_func` applied to `alpha*full_length - i*lag_ratio`, where `full_length = (n-1)*lag_ratio + 1`; it does not change the total duration, only redistributes it among the `n` submobjects |
| `rate_func` | `Callable` | `smooth` | rate function, which decides the "progress ↔ time" mapping. **What can be passed**: `linear`, `smooth`, `there_and_back`, `rush_into`, `rush_from`, `double_smooth`, `exponential_decay`, … (see [Rate functions](../../08-Utilities/02-Rate-Functions.md)) |
| `reverse_rate_function` | `bool` | `False` | `True` reverses the rate function (a "rewind" feel). **Not recommended** as `remover`/`introducer`: it does not change those two flags |
| `name` | `str \| None` | `None` | the name shown in the render log, defaulting to `<class name>(<Mobject name>)`. **Not recommended to change**: it only affects the log, the image is unchanged |
| `remover` | `bool` | `False` | `True` removes the mobject from the scene when playback finishes |
| `introducer` | `bool` | `False` | `True` adds the mobject to the scene before playback |
| `suspend_mobject_updating` | `bool` | `True` | suspends the mobject's own updater during the animation (so the updater does not overwrite the interpolation). **Not recommended to change**: with a mobject that has no updater, both values give an identical image |
| `use_override` | `bool` | `True` | whether to use the overridden version if the mobject's type overrode this animation class with `override_animation`. The override mechanism is wired up (`Animation.__new__` consults the override registry, `animation_override_for` supports same-name fallback across namespaces, and `False` keeps the original animation class). **Not recommended to change**: you won't need it day to day |

> **Returns**: an `Animation` instance; hand it straight to `win.play(...)`.

### `Animation.set_default`

```python
@classmethod
def set_default(cls, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `**kwargs` | `Any` | — | the defaults to override in bulk (e.g. `run_time=2, rate_func=linear`); **what can be passed**: any constructor parameter from the table above. It applies globally and is **not recommended** to change in library code; calling it with no arguments `set_default()` restores the original defaults |

> **Returns**: none (it modifies that animation class's constructor defaults in place).

### `set_rate_func` (chained method)

```python
def set_rate_func(self, func: Callable[[float], float]) -> "Animation":
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `func` | `Callable[[float], float]` | — | the new rate function (e.g. `linear`). It returns `self`, so chaining continues |

> **Returns**: `self` (it changes `rate_func` in place and returns itself). Chained methods such as `set_run_time` / `get_run_time` / `get_rate_func` / `set_name` / `is_introducer` / `is_remover` / `copy` are all implemented on RTM's own `Animation` (test `tests/test_gap_wait_timeline.py`).

#### Sample: Animation common constructor parameters one by one

It passes the constructor parameters explicitly one by one: `run_time` / `lag_ratio` / `rate_func` / `reverse_rate_function` / `introducer` / `remover`, plus the `set_default` bulk defaults and the `set_rate_func` chained method.

```python
import os
from real_time_manim import (
    BLUE,
    DOWN,
    GREEN,
    GREY_B,
    LEFT,
    ORANGE,
    RIGHT,
    UP,
    YELLOW,
    PI,
    Circle,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
    linear,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    Rotate,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401

class Page_01_Lifecycle_and_Common_Parameters(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("01-Animation lifecycle and common parameters", font_size=42, color=YELLOW).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # —— signature on screen: the constructor parameters all animations share ——
        s1 = Text("Animation(mobject, lag_ratio=0.0, run_time=1.0, rate_func=smooth,", font_size=28, color=GREY_B)
        s2 = Text("           reverse_rate_function=False, name=None, remover=False,", font_size=28, color=GREY_B)
        s3 = Text("           introducer=False, use_override=True)", font_size=28, color=GREY_B)
        sig = VGroup(s1, s2, s3).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.0)
        win.play(FadeIn(sig, shift=DOWN), run_time=0.5)

        # —— Step 1: run_time + rate_func ——
        l1 = Text("Create(sq, run_time=1.4, rate_func=linear)", font_size=30, color=GREY_B)
        l1.next_to(sig, DOWN, buff=0.35)
        sq = Square(side_length=1.2, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 3.4 + DOWN * 2.4)
        ci = Circle(radius=0.62, color=GREEN).set_fill(GREEN, 0.5).shift(DOWN * 2.4)
        tri = Triangle(color=ORANGE).scale(0.75).set_fill(ORANGE, 0.5).shift(RIGHT * 3.4 + DOWN * 2.4)
        win.play(FadeIn(l1, shift=DOWN), run_time=0.4)
        win.play(Create(sq, run_time=1.4, rate_func=linear))    # params run_time / rate_func

        # —— Step 2: lag_ratio: Write staggered by glyph ——
        win.play(FadeOut(l1), run_time=0.3)
        l2 = Text("Write(txt, lag_ratio=0.5, run_time=1.6)", font_size=30, color=GREY_B)
        l2.next_to(sig, DOWN, buff=0.35)
        txt = Text("lag_ratio", font_size=40, color=YELLOW).shift(DOWN * 2.4)
        win.play(FadeIn(l2, shift=DOWN), run_time=0.4)
        win.play(Write(txt, lag_ratio=0.5, run_time=1.6))       # param lag_ratio (glyphs written one by one)
        win.play(FadeOut(VGroup(l2, txt)), run_time=0.3)

        # —— Step 3: introducer / remover: the two lifecycle hooks for entering/leaving the scene ——
        l3 = Text("FadeIn(sq2, introducer=True) / FadeOut(sq2, remover=True)",
                  font_size=30, color=GREY_B).next_to(sig, DOWN, buff=0.35)
        sq2 = Square(side_length=1.2, color=YELLOW).set_fill(YELLOW, 0.5).shift(DOWN * 2.4)
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)
        win.play(FadeIn(sq2, introducer=True, shift=UP, run_time=0.9))   # param introducer
        win.play(Wait(0.3))
        win.play(FadeOut(sq2, remover=True, run_time=0.9))               # param remover

        # —— Step 4: reverse_rate_function: rewind ——
        win.play(FadeOut(l3), run_time=0.3)
        l4 = Text("Rotate(tri, PI/2, reverse_rate_function=True)", font_size=30, color=GREY_B)
        l4.next_to(sig, DOWN, buff=0.35)
        win.play(FadeIn(l4, shift=DOWN), run_time=0.4)
        win.play(Rotate(tri, PI / 2, reverse_rate_function=True,
                        run_time=1.2, rate_func=linear))        # param reverse_rate_function (rewinds from PI/2 back to 0)
        win.play(FadeOut(l4), run_time=0.3)

        # —— Step 5: set_default bulk defaults + set_rate_func chained method ——
        l5 = Text("Rotate.set_default(run_time=1.2, rate_func=linear)", font_size=30, color=GREY_B)
        l6 = Text("  ->  win.play(Rotate(ci, PI/2))   # 1.2s linear from the defaults", font_size=28, color=GREY_B)
        l7 = Text("rot.set_rate_func(linear)  # chained method on RTM's Animation", font_size=28, color=GREY_B)
        sig5 = VGroup(l5, l6, l7).arrange(DOWN, buff=0.06).next_to(sig, DOWN, buff=0.35)
        win.play(FadeIn(sig5, shift=DOWN), run_time=0.4)
        Rotate.set_default(run_time=1.2, rate_func=linear)      # Animation.set_default(**kwargs)
        win.play(Rotate(ci, PI / 2))                            # params run_time=1.2 / rate_func=linear (from the defaults)
        Rotate.set_default()                                    # called with no arguments to restore the defaults
        rot = Rotate(ci, -PI / 2, run_time=0.8)
        rot.set_rate_func(linear)                               # method set_rate_func
        win.play(rot)

        win.play(FadeOut(VGroup(title, sig, sq, ci, tri, sig5)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_01_Lifecycle_and_Common_Parameters,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "01-Lifecycle-and-Common-Parameters.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
```

What this code does: it opens by writing the title and the whole `Animation(...)` signature, then demonstrates in five steps —

- ① `Create(sq, run_time=1.4, rate_func=linear)` — a non-default duration plus constant speed;
- ② `Write(txt, lag_ratio=0.5, run_time=1.6)` — staggered by glyph, written out character by character;
- ③ `FadeIn(sq2, introducer=True)` / `FadeOut(sq2, remover=True)` — walks through the two hooks for entering and leaving the scene;
- ④ `Rotate(tri, PI/2, reverse_rate_function=True)` — rotates back from the end point;
- ⑤ `Rotate.set_default(run_time=1.2, rate_func=linear)` makes the later `Rotate(ci, PI/2)` run linearly for 1.2 seconds without any arguments; at the end `set_default()` restores the defaults and `set_rate_func(linear)` changes the rate function by hand for comparison.

<video src="assets/RTM output/01-Lifecycle-and-Common-Parameters.mp4" controls width="560"></video>

> Note:
>
> - `FadeOut` fixes `remover=True` internally (passing it or not makes no difference).
> - `FadeIn`'s `introducer` is **not fixed** in RTM: it defaults to `False`, and an explicit `introducer=True` is accepted. To demonstrate "introducer/remover on any animation", passing it to `Create` / a custom animation is more reliable.
> - `set_default` is a class-level global switch; remember to restore it after use.

Not demonstrated:

- `name` — only affects repr/the render log, the image is unchanged;
- `suspend_mobject_updating` — no video: with a mobject that has no updater, True/False give an identical image;
- `use_override` — the override mechanism is wired up (`override_animation` registry + `animation_override_for` same-name fallback across namespaces, `use_override=False` keeps the original class), still not demonstrated: it needs a custom Mobject subclass, and there is no visible parameter difference;
- `set_run_time` / `set_name` / `get_run_time` / `get_rate_func` / `is_introducer` / `is_remover` / `copy` — implemented (test `tests/test_gap_wait_timeline.py`), still not demonstrated: pure attribute access, no image difference.

---

See also: [play and wait parameters](02-play-and-wait-Parameters.md) · [.animate syntax](03-animate-Syntax.md) · [The Fade family](../Fades/01-The-Fade-Family.md)
