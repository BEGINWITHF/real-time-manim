# Indicate and Flash (Indicate, Flash, Blink)

Three animations that briefly pull the viewer's eye onto an object: scale-and-tint emphasis (`Indicate`), a radiating spark (`Flash`), and on/off blinking (`Blink`).

## Parameters

### `Indicate` 

```python
Indicate(mobject, scale_factor=1.2, color=PURE_YELLOW, rate_func=there_and_back, **kwargs)
```

Briefly **scales the object up, tints it a highlight colour, then returns it to normal** (`rate_func=there_and_back` guarantees the "go there and come back" motion); it is the most commonly used "draw attention here" animation. **Inherits** `Indicate(Animation)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the object being emphasised |
| `scale_factor` | `float` | `1.2` | the scale factor during emphasis |
| `color` | `ParsableManimColor` | `PURE_YELLOW` | the colour during emphasis (restored to the original colour once it finishes). RTM's own version defaults to manim's **`YELLOW`** (`#F7D96F`, creamy rather than pure yellow) — the two versions have different default colours; pass a value explicitly to make them agree |
| `rate_func` | `RateFunction` | `there_and_back` | the there-and-back progress curve |
| `run_time` | `float` | `1.0` (fixed) | the constructor's `kwargs.pop('run_time')` **is discarded outright**: `Indicate(sq, run_time=3)` has no effect and is always `1.0`; to change the duration you can only pass it **at the play level** (`win.play(Indicate(...), run_time=1.4)` setattrs over it) |
| `**kwargs` | … | — | `Animation` common parameters (`reverse_rate_function`, `name`, …). RTM's own `Indicate` **is not a `Transform` subclass**, so passing something like `path_arc` has no effect (it is swallowed by `**kwargs`) |

> **Returns**: an `Indicate` instance.

One-liner:

```python
win.play(Indicate(Tex("Indicate").scale(3)))
```

### `Flash`

```python
Flash(point, line_length=0.2, num_lines=12, flash_radius=0.1, line_stroke_width=3,
      color=PURE_YELLOW, time_width=1, run_time=1.0, **kwargs)
```

**Radiates a ring of short flashing lines** outward from a point (each line is one `ShowPassingFlash`, combined by an `AnimationGroup`); `point` can be a coordinate point or a mobject (its centre is taken automatically). **Inherits** `Flash(AnimationGroup)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `point` | `Point3DLike \| Mobject` | — (required) | the centre of the flash |
| `line_length` | `float` | `0.2` | the length of each line |
| `num_lines` | `int` | `12` | the number of lines |
| `flash_radius` | `float` | `0.1` | the distance from the centre to the start of the lines |
| `line_stroke_width` | `int` | `3` | the line width |
| `color` | `ParsableManimColor` | `PURE_YELLOW` | the line colour |
| `time_width` | `float` | `1` | the beam width passed to `ShowPassingFlash` |
| `run_time` | `float` | `1.0` | the duration |
| `**kwargs` | … | — | stored as `animation_config` and passed through to each line's `ShowPassingFlash` (e.g. `rate_func=rush_from`) |

> **Returns**: a `Flash` instance.

One-liner:

```python
win.play(Flash(Dot(color=PURE_YELLOW).shift(DOWN), num_lines=30, color=RED))
```

### `Blink`

```python
Blink(mobject, time_on=0.5, time_off=0.5, blinks=1, hide_at_end=False, **kwargs)
```

Makes the object **blink**: repeatedly shown for `time_on` seconds / hidden for `time_off` seconds, `blinks` times; often combined with `TypeWithCursor` for a blinking cursor (see [01b-Typing-with-a-Cursor](../Text-and-Numbers/01b-Typing-with-a-Cursor.md)). **Inherits** `Blink(Succession)` ← `AnimationGroup` ← `Animation`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the object being blinked |
| `time_on` | `float` | `0.5` | the visible duration each time |
| `time_off` | `float` | `0.5` | the hidden duration each time |
| `blinks` | `int` | `1` | the number of blinks |
| `hide_at_end` | `bool` | `False` | if `True`, it stays hidden at the end |
| `run_time` | `float` | computed from `time_on`/`time_off`/`blinks` | `kwargs.pop('run_time')` **is discarded outright**: the actual duration is always `blinks × (time_on + time_off)` (`hide_at_end=False` adds one more `time_on`); passing `run_time=` in the constructor has no effect |
| `**kwargs` | … | — | forwarded to the internal `Succession` (except `run_time`, see the row above) |

> **Returns**: a `Blink` instance.

One-liner:

```python
win.play(Blink(Text("Blinking").scale(1.5), blinks=3))
```

#### Sample: Indicate / Flash / Blink demonstrated item by item

The page clip demonstrates Indicate → Flash → Blink in that order, one segment each, with every parameter labelled on screen.

```python
from real_time_manim import (
    BLUE,
    DARK_GRAY,
    GREEN,
    GREY_B,
    RED,
    DOWN,
    UP,
    Dot,
    Flash,
    Scene,
    Square,
    Text,
    VGroup,
    rush_from,
    there_and_back,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Blink,
    FadeIn,
    FadeOut,
    Indicate,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  used by __main__ at the end of the file


class Page_01_Indicate_and_Flash(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameters w=1280 / h=720 / hidden=True
        win.scene = self                          # parameter win.scene

        title = Text("Indicate / Flash / Blink",
                     font_size=38, color=GREEN).to_edge(UP)   #title uses ASCII only: font fallback stays reliable in both engines
        win.play(Write(title), run_time=0.8)

        # —— step 1: Indicate(mobject, scale_factor, color, rate_func, **kwargs) ——
        s1a = Text("Indicate(sq, scale_factor=1.6,", font_size=32, color=GREY_B)
        s1b = Text("          color=RED, rate_func=there_and_back)", font_size=32, color=GREY_B)
        sig1 = VGroup(s1a, s1b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        sq = Square(side_length=1.6, color=BLUE).set_fill(BLUE, 0.5).next_to(sig1, DOWN, buff=0.7)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        win.play(
            Indicate(
                sq,                                      # parameter mobject ✓
                scale_factor=1.6,                        # parameter scale_factor=1.6 ✓ (default 1.2)
                color=RED,                               # parameter color=RED ✓ (default PURE_YELLOW)
                rate_func=there_and_back,                # parameter rate_func ✓ (explicit: goes there then comes back)
            ),
            run_time=1.4,                                # parameter **kwargs(run_time): overridden at the play level ✓
        )
        win.play(FadeOut(sig1), FadeOut(sq), run_time=0.45)

        # —— step 2: Flash(point, line_length, num_lines, flash_radius,
        #                   line_stroke_width, color, time_width, run_time, **kwargs) ——
        s2a = Text("Flash(dot, line_length=0.3, num_lines=30,", font_size=30, color=GREY_B)
        s2b = Text("        flash_radius=0.18, line_stroke_width=5,", font_size=30, color=GREY_B)
        s2c = Text("        color=RED, time_width=1.5, rate_func=rush_from)", font_size=30, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        dot = Dot(radius=0.12, color=DARK_GRAY).next_to(sig2, DOWN, buff=1.0)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        win.play(
            Flash(
                dot,                                     # parameter point (passing a mobject → its centre) ✓
                line_length=0.3,                         # parameter line_length=0.3 ✓ (default 0.2)
                num_lines=30,                            # parameter num_lines=30 ✓ (default 12)
                flash_radius=0.18,                       # parameter flash_radius=0.18 ✓ (default 0.1)
                line_stroke_width=5,                     # parameter line_stroke_width=5 ✓ (default 3)
                color=RED,                               # parameter color=RED ✓ (default PURE_YELLOW)
                time_width=1.5,                          # parameter time_width=1.5 ✓ (default 1)
                run_time=1.2,                            # parameter run_time=1.2 ✓ (default 1.0)
                rate_func=rush_from,                     # parameter **kwargs → passed through to each line's ShowPassingFlash ✓
            ),
            run_time=1.2,
        )
        win.play(FadeOut(sig2), FadeOut(dot), run_time=0.45)

        # —— step 3: Blink(mobject, time_on, time_off, blinks, hide_at_end, **kwargs) ——
        s3a = Text("Blink(txt, time_on=0.35, time_off=0.25,", font_size=32, color=GREY_B)
        s3b = Text("        blinks=3, hide_at_end=True)", font_size=32, color=GREY_B)
        sig3 = VGroup(s3a, s3b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        txt = Text("Blinking", font_size=48, color=GREEN).next_to(sig3, DOWN, buff=0.9)
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.45)
        self.add(txt)                                  #Blink does not introduce the object: add it to the scene first or it cannot blink
        win.play(
            Blink(
                txt,                                     # parameter mobject ✓
                time_on=0.35,                            # parameter time_on=0.35 ✓ (default 0.5)
                time_off=0.25,                           # parameter time_off=0.25 ✓ (default 0.5)
                blinks=3,                                # parameter blinks=3 ✓ (default 1)
                hide_at_end=True,                        # parameter hide_at_end=True ✓ (default False: stays hidden at the end)
            ),
        )
        win.play(FadeOut(sig3), run_time=0.45)

        win.play(FadeOut(title), run_time=0.5)
        win.close()
```

What this code does: it opens an RTM window, binds the scene to it, writes the title out first, then demonstrates three segments.

- Segment 1: a parameter caption and a blue square fade in, then `Indicate` scales the square up 1.6×, tints it red, and returns it to normal.
- Segment 2: a dark-grey dot, from whose centre `Flash` radiates 30 short lines (`rate_func=rush_from` makes the rays shoot outward).
- Segment 3: the green text "Blinking" is first `self.add`ed to the scene, then blinks 3 times with `time_on=0.35` / `time_off=0.25`; `hide_at_end=True` keeps it hidden once done.

Each segment fades its caption and object out when it finishes; at the end the title is removed and the window closed.

<video src="assets/RTM output/01-Indicate-and-Flash.mp4" controls width="560"></video>

> Note:
>
> - `Blink` **does not bring the object into the scene** — forget the `self.add(txt)` first and you get a black screen with nothing blinking (the sample is saved by exactly that line).
> - Remember to leave a **round-trip** curve such as `there_and_back` on `Indicate`'s `rate_func`: the "coming back" half is its job; switch to a one-way curve and the object stops in the scaled, tinted state.
> - `Flash`'s `**kwargs` are passed straight through to each line's `ShowPassingFlash`; to change the rhythm of the rays, put `rate_func` inside `Flash(...)`.
> - `Blink` defaults to `hide_at_end=False`, so the object is still there after blinking; pass `True` to "disappear once done".

See also: [Circumscribe and Focus](02-Circumscribe-and-Focus.md), [Sweeps and Waves](01b-Sweeps-and-Waves.md), [The Grow Family](../Growth/01-The-Grow-Family.md)
