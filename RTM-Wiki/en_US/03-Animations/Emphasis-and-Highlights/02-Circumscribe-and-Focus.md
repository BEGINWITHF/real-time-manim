# Circumscribe and Focus (Circumscribe, FocusOn, Wiggle)

Three attention animations: a temporary frame drawn around an object, a glow shrinking to a focus, and a quick "shake" of an object.

## Parameters

### `Circumscribe` 

```python
Circumscribe(mobject, shape=Rectangle, fade_in=False, fade_out=False, time_width=0.3,
             buff=SMALL_BUFF, color=PURE_YELLOW, run_time=1, stroke_width=DEFAULT_STROKE_WIDTH, **kwargs)
```

**Draws a temporary frame around the object and then erases it**; **note that `shape` takes a class, not an instance**.

The two versions validate `shape` differently:

- The **CE version** accepts only `Rectangle` / `Circle` and raises `ValueError("shape should be either Rectangle or Circle.")` for anything else.
- **RTM's own version does not raise**: `shape is Rectangle` goes through `SurroundingRectangle`, and **everything else is treated as a `Circle`** (passing a `Dot` or the like silently draws a circle).

**Inherits** `Circumscribe(Succession)` ← `AnimationGroup` ← `Animation` (RTM's own chain is isomorphic to CE's).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the object being circled |
| `shape` | `type[Rectangle] \| type[Circle]` | `Rectangle` | the frame shape **class** (`Rectangle` or `Circle`) |
| `fade_in` | `bool` | `False` | the frame fades in (and the drawing direction is reversed) |
| `fade_out` | `bool` | `False` | the frame fades out |
| `time_width` | `float` | `0.3` (sentinel default) | now wired up (2026-10-16, test `tests/test_gap_indication_fade.py`): when passed **explicitly** (including an explicit `0.3`) the non-fade branch switches to `ShowPassingFlash` beam semantics (only a short stretch of width `time_width` is lit each frame); **when not passed it keeps the old `Create` progressive drawing** (existing renders are frame-for-frame unchanged; the default is identified by a sentinel object and `signature` still prints `0.3`); the `fade_in`/`fade_out=True` branch **ignores** this parameter (both samples on this page take the fade branch) |
| `buff` | `float` | `SMALL_BUFF` | the gap between the frame and the object |
| `color` | `ParsableManimColor` | `PURE_YELLOW` | the frame colour. RTM's own version writes `None` as the default and falls back internally to manim's **`YELLOW`** (on the creamy side) |
| `run_time` | `float` | `1` | the overall duration (in fade mode it is split evenly between the two halves) |
| `stroke_width` | `float` | `DEFAULT_STROKE_WIDTH (=4)` | the frame line width |
| `**kwargs` | … | — | forwarded to the internal `Succession` and its sub-animations |

> **Returns**: a `Circumscribe` instance.

One-liner:

```python
lbl = Tex("Circumscribe").scale(2)
win.play(Circumscribe(lbl, Circle, fade_out=True))
```

### `FocusOn` 

```python
FocusOn(focus_point, opacity=0.2, color=GREY, run_time=2, **kwargs)
```

A "focus" effect where **a large glow shrinks down to the target point** and leaves a small bright dot (internally it first builds a big `Dot` with radius = screen radius, then transforms it into a small dot attached to the target); it is removed automatically when it finishes (`remover=True`). **Inherits** `FocusOn(Transform)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `focus_point` | `Point3DLike \| Mobject` | — (required) | the focus point; when a mobject is given, its centre is used |
| `opacity` | `float` | `0.2` | the opacity of the glow after focusing |
| `color` | `ParsableManimColor` | `GREY` | the glow colour |
| `run_time` | `float` | `2` | the duration |
| `**kwargs` | … | — | `Transform`/`Animation` common parameters |

> **Returns**: a `FocusOn` instance.

One-liner:

```python
win.play(FocusOn(Dot(color=PURE_YELLOW).shift(DOWN)))
```

### `Wiggle` 

```python
Wiggle(mobject, scale_value=1.1, rotation_angle=0.01 * TAU, n_wiggles=6,
       scale_about_point=None, rotate_about_point=None, run_time=2, **kwargs)
```

The object **scales slightly and sways left-right `n_wiggles` times** in place, then returns to normal (using the `wiggle` rate function), as if it were "given a shake"; the difference from `ApplyWave` is that `Wiggle` sways the whole object while `ApplyWave` propagates a wave through its interior. **Inherits** `Wiggle(Animation)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the object being shaken |
| `scale_value` | `float` | `1.1` | the temporary scale-up amount |
| `rotation_angle` | `float` | `0.01*TAU (=3.6°)` | the angle of a single sway |
| `n_wiggles` | `int` | `6` | the number of sways |
| `scale_about_point` | `Point3DLike \| None` | `None` | the scaling centre; `None` uses the object's centre |
| `rotate_about_point` | `Point3DLike \| None` | `None` | the rotation centre; `None` uses the object's centre |
| `run_time` | `float` | `2` | the duration |
| `**kwargs` | … | — | `Animation` common parameters |

> **Returns**: a `Wiggle` instance.

One-liner:

```python
win.play(Wiggle(Tex("Wiggle").scale(3)))
```

#### Sample: both Circumscribe frames / FocusOn / Wiggle demonstrated item by item

The page clip demonstrates Circumscribe (rectangle) → Circumscribe (circle) → FocusOn → Wiggle in that order, one segment each, with every parameter labelled on screen.

```python
from real_time_manim import (
    GREEN,
    GREY_B,
    PURE_YELLOW,
    PURPLE,
    SMALL_BUFF,
    TEAL,
    TAU,
    DOWN,
    UP,
    Circle,
    Dot,
    FocusOn,
    Rectangle,
    Scene,
    Text,
    VGroup,
    Wiggle,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Circumscribe,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  used by __main__ at the end of the file


class Page_02_Circumscribe_and_Focus(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameters w=1280 / h=720 / hidden=True
        win.scene = self                          # parameter win.scene

        title = Text("Circumscribe / FocusOn / Wiggle",
                     font_size=36, color=GREEN).to_edge(UP)   #title uses ASCII only: font fallback stays reliable in both engines
        win.play(Write(title), run_time=0.8)

        lbl = Text("Circumscribe", font_size=46, color=GREEN).shift(DOWN * 1.6)

        # —— step 1: Circumscribe(shape=Rectangle, fade_out=True) ——
        s1a = Text("Circumscribe(lbl, shape=Rectangle, fade_in=False,", font_size=28, color=GREY_B)
        s1b = Text("    fade_out=True, time_width=0.3, buff=SMALL_BUFF,", font_size=28, color=GREY_B)
        s1c = Text("    color=PURE_YELLOW, run_time=1.6, stroke_width=6)", font_size=28, color=GREY_B)
        sig1 = VGroup(s1a, s1b, s1c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        cs1 = Circumscribe(
            lbl,                                     # parameter mobject ✓
            shape=Rectangle,                         # parameter shape=Rectangle (a class, not an instance) ✓
            fade_in=False,                           # parameter fade_in=False ✓
            fade_out=True,                           # parameter fade_out=True ✓ (default False: the frame fades out)
            time_width=0.3,                          # parameter time_width=0.3 (here fade_out=True: the fade branch ignores this parameter)
            buff=SMALL_BUFF,                         # parameter buff=SMALL_BUFF ✓
            color=PURE_YELLOW,                       # parameter color=PURE_YELLOW ✓
            run_time=1.6,                            # parameter run_time=1.6 ✓ (fade mode splits it evenly between the two halves)
            stroke_width=6,                          # parameter stroke_width=6 ✓ (default 4)
        )
        # add the label lbl to the scene by hand (Circumscribe's .mobject is None and carries no text);
        # since 2026-10-16 the frame _frame is also brought into the scene automatically by the play layer's "grouped sub-animation presentation",
        # so the self.add here becomes an idempotent fallback; clean_up_from_scene still removes _frame when it finishes.
        self.add(lbl, cs1._frame)
        win.play(cs1)
        win.play(FadeOut(sig1), run_time=0.4)

        # —— step 2: Circumscribe(shape=Circle, fade_in=True) ——
        s2a = Text("Circumscribe(lbl, shape=Circle, fade_in=True,", font_size=30, color=GREY_B)
        s2b = Text("    buff=0.18, color=TEAL, stroke_width=6, run_time=1.6)", font_size=30, color=GREY_B)
        sig2 = VGroup(s2a, s2b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.4)
        cs2 = Circumscribe(
            lbl,                                     # parameter mobject ✓
            shape=Circle,                            # parameter shape=Circle ✓ (default Rectangle)
            fade_in=True,                            # parameter fade_in=True ✓ (default False: the frame fades in)
            buff=0.18,                               # parameter buff=0.18 ✓ (default SMALL_BUFF)
            color=TEAL,                              # parameter color=TEAL ✓ (default PURE_YELLOW)
            stroke_width=6,                          # parameter stroke_width=6 ✓
            run_time=1.6,                            # parameter run_time=1.6 ✓
        )
        self.add(cs2._frame)
        win.play(cs2)
        win.play(FadeOut(sig2), FadeOut(lbl), run_time=0.4)

        # —— step 3: FocusOn(focus_point, opacity, color, run_time) ——
        s3a = Text("FocusOn(dot, opacity=0.4,", font_size=32, color=GREY_B)
        s3b = Text("         color=PURPLE, run_time=1.4)", font_size=32, color=GREY_B)
        sig3 = VGroup(s3a, s3b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        dot = Dot(radius=0.1, color=PURPLE).next_to(sig3, DOWN, buff=1.2)
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.4)
        self.add(dot)
        win.play(
            FocusOn(
                dot,                                   # parameter focus_point (passing a mobject → its centre) ✓
                opacity=0.4,                           # parameter opacity=0.4 ✓ (default 0.2)
                color=PURPLE,                          # parameter color=PURPLE ✓ (default GREY)
                run_time=1.4,                          # parameter run_time=1.4 ✓ (default 2)
            ),
        )
        win.play(FadeOut(sig3), FadeOut(dot), run_time=0.4)

        # —— step 4: Wiggle(mobject, scale_value, rotation_angle, n_wiggles,
        #                   scale_about_point, rotate_about_point, run_time) ——
        s4a = Text("Wiggle(wig, scale_value=1.35, rotation_angle=0.03*TAU,", font_size=28, color=GREY_B)
        s4b = Text("        n_wiggles=4, scale_about_point=None,", font_size=28, color=GREY_B)
        s4c = Text("        rotate_about_point=None, run_time=1.6)", font_size=28, color=GREY_B)
        sig4 = VGroup(s4a, s4b, s4c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        wig = Text("Wiggle", font_size=52, color=GREEN).next_to(sig4, DOWN, buff=0.9)
        win.play(FadeIn(sig4, shift=DOWN), run_time=0.4)
        self.add(wig)
        win.play(
            Wiggle(
                wig,                                   # parameter mobject ✓
                scale_value=1.35,                      # parameter scale_value=1.35 ✓ (default 1.1)
                rotation_angle=0.03 * TAU,             # parameter rotation_angle=0.03*TAU ✓ (default 0.01*TAU)
                n_wiggles=4,                           # parameter n_wiggles=4 ✓ (default 6)
                scale_about_point=None,                # parameter scale_about_point=None ✓ (uses the object's centre)
                rotate_about_point=None,               # parameter rotate_about_point=None ✓ (uses the object's centre)
                run_time=1.6,                          # parameter run_time=1.6 ✓ (default 2)
            ),
        )
        win.play(FadeOut(sig4), FadeOut(wig), run_time=0.45)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()
```

What this code does: it writes the title, places a green "Circumscribe" text, then demonstrates four segments.

- Segment 1: a yellow rectangular frame is drawn and then fades out (`fade_out=True`), circling the text.
- Segment 2: a teal circular frame fades in and is then erased (`fade_in=True` + `shape=Circle`).
- Segment 3: a large purple glow shrinks down onto a small dot (`FocusOn`, `opacity=0.4`).
- Segment 4: the text "Wiggle" scales up 1.35× as a whole and sways 4 times before returning to normal.

`self.add(lbl, cs1._frame)` is what brings the **label** into the scene (`Circumscribe`'s `.mobject` is `None` and carries no text), while the internal frame is presented automatically by the play layer (the code comment notes why).

<video src="assets/RTM output/02-Circumscribe-and-Focus.mp4" controls width="560"></video>

> Note:
>
> - `shape` takes a **class** (`Rectangle` / `Circle`), not an instance; when you pass **any other class**, the **CE version raises `ValueError`** while **RTM's own version does not raise** (anything that is not `Rectangle` draws a circle as a `Circle`, see the parameter table).
> - `Circumscribe`'s `.mobject` is `None` and **does not carry the text being circled**, so the sample adds the label to the scene by hand with `self.add(lbl, ...)`; since the 2026-10-16 "grouped sub-animation presentation" (where `_ensure_animated_present` walks one layer of the `animations`' mobjects) the internal frame `_frame` is also brought into the scene automatically, so `self.add(cs1._frame)` has become an **idempotent fallback** — it looks the same whether or not you add it, and `clean_up_from_scene` clears `_frame` when it finishes.
> - `FocusOn` removes itself when it finishes (`remover=True`), so there is no need to `FadeOut` it.

See also: [Indicate and Flash](01-Indicate-and-Flash.md), [Sweeps and Waves](01b-Sweeps-and-Waves.md), [The Grow Family](../Growth/01-The-Grow-Family.md)
