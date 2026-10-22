# Typing with a cursor: TypeWithCursor / UntypeWithCursor

The typewriter effect where a cursor mobject follows the end as each character is typed, and its reverse-playback version.

## Parameters

### `TypeWithCursor`

```python
TypeWithCursor(text, cursor, buff=0.1, keep_cursor_y=True, leave_cursor_on=True,
               time_per_char=0.1, run_time=None, **kwargs)
```

Types character by character while **a cursor follows the end**, moving right as characters are typed out (`buff` controls the gap); when it finishes you can choose to leave or hide the cursor. Often combined with `Blink` for a complete input effect (see [01-Indicate-and-Flash](../Emphasis-and-Highlights/01-Indicate-and-Flash.md)).

**Inherits** `TypeWithCursor(ShowIncreasingSubsets) ← Animation`. With `run_time=None` it is computed automatically as `time_per_char × number of characters` (the 0.14×9=1.26 s in the sample comments is exactly this).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `text` | `Text` | — | the text being typed |
| `cursor` | `Mobject` | — (required, no default) | the cursor (e.g. a thin rectangle / underscore); it is temporarily repositioned during the animation |
| `buff` | `float` | `0.1` | the gap between the cursor and the last character |
| `keep_cursor_y` | `bool` | `True` | `True` keeps the cursor's y at the centre of the whole text, otherwise it follows the current character's centre |
| `leave_cursor_on` | `bool` | `True` | whether to keep the cursor after the animation ends (`False` hides it) |
| `time_per_char` | `float` | `0.1` | the interval per character (it also determines the automatic duration when `run_time=None`) |
| `run_time` | `float \| None` | `None` (→ `time_per_char × number of characters`) | passing it explicitly overrides the automatic value |
| `rate_func` | `Callable` | `smooth` (`Animation` default) | RTM's own version **does not** have the `linear` default of CE's `AddTextLetterByLetter` |
| `reverse_rate_function` | `bool` | `False` | reverse (forwarded to `Animation` via `**kwargs`, **not an explicit parameter**) |
| `introducer` | `bool` | `False` (`Animation` default) | RTM's own version **does not pin it** (it goes through `Animation`'s default `False` and can be passed `True` explicitly, as the sample does) |
| `**kwargs` | — | — | `Animation` common parameters (`suspend_mobject_updating`, …). The RTM version does not have the `int_func` / `suspend_mobject_updating=False` defaults from CE's `AddTextLetterByLetter` |

> **Returns**: a `TypeWithCursor` instance.

One-liner:

```python
text = Text("Inserting", color=PURPLE).scale(1.5).to_edge(LEFT)
cursor = Rectangle(color=GREY_A, fill_color=GREY_A, fill_opacity=1,
                   height=1.1, width=0.5).move_to(text[0])
win.play(TypeWithCursor(text, cursor))
win.play(Blink(cursor, blinks=2))
```

### `UntypeWithCursor` 

```python
UntypeWithCursor(text, cursor, buff=0.1, keep_cursor_y=True, leave_cursor_on=True,
                 time_per_char=0.1, run_time=None, **kwargs)
```

**Reverse typing** with a cursor (characters disappear from the end one by one, the cursor following along), removed from the scene when done — for the shot where "this input gets deleted". **Inherits** `UntypeWithCursor(Animation)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `text` | `Text` | — | the text being deleted character by character |
| `cursor` | `VMobject` | — (**required, no default**) | in RTM's own version `cursor` is the **second positional required parameter**, with no `None` default |
| `buff` | `float` | `0.1` | the gap between the cursor and the last character |
| `keep_cursor_y` | `bool` | `True` | locks the cursor's y |
| `leave_cursor_on` | `bool` | `True` | whether to keep the cursor when done |
| `time_per_char` | `float` | `0.1` | the interval per character |
| `run_time` | `float \| None` | `None` (→ `time_per_char × number of characters`) | passing it explicitly overrides the automatic value |
| `reverse_rate_function` / `remover` | — | — | RTM's own version **has neither of these parameters** (nor `introducer`); the reverse direction is hard-coded in the class (`index = n - floor(alpha*n)`), so `remover`/`introducer` can only be passed through `**kwargs` to `Animation`, and `clean_up_from_scene` is the base class's `pass`, so it does not actually remove anything from the scene when done. Only ManimCE's version has these two explicit parameters |
| `**kwargs` | — | — | `Animation` common parameters (`rate_func`, etc.) |

> **Returns**: an `UntypeWithCursor` instance.

One-liner:

```python
text = Text("Deleting", color=PURPLE).scale(1.5).to_edge(LEFT)
cursor = Rectangle(color=GREY_A, fill_color=GREY_A, fill_opacity=1,
                   height=1.1, width=0.5).move_to(text[0])
self.add(text)
win.play(UntypeWithCursor(text, cursor))
```

#### Sample: TypeWithCursor / UntypeWithCursor demonstrated item by item

The page clip demonstrates TypeWithCursor (including the cursor blinking twice after it finishes) → UntypeWithCursor in that order, one segment each, with every parameter labelled on screen.

```python
import os

from real_time_manim import (
    GREEN,
    GREY_B,
    PURPLE,
    RED,
    DOWN,
    UP,
    Rectangle,
    Scene,
    Text,
    VGroup,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Blink,
    FadeIn,
    FadeOut,
    TypeWithCursor,
    UntypeWithCursor,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  used by __main__ at the end of the file


class Page_01b_Typing_with_a_Cursor(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameters w=1280 / h=720 / hidden=True
        win.scene = self                          # parameter win.scene

        title = Text("TypeWithCursor / UntypeWithCursor",
                     font_size=34, color=GREEN).to_edge(UP)   #title uses ASCII only: font fallback stays reliable in both engines
        win.play(Write(title), run_time=0.85)

        # —— step 1: TypeWithCursor(text, cursor, buff, keep_cursor_y,
        #                           leave_cursor_on, time_per_char, ...) ——
        s1a = Text("TypeWithCursor(txt, cursor,", font_size=28, color=GREY_B)
        s1b = Text("    buff=0.12, keep_cursor_y=True, leave_cursor_on=True,",
                   font_size=28, color=GREY_B)
        s1c = Text("    time_per_char=0.14, reverse_rate_function=False,",
                   font_size=28, color=GREY_B)
        s1d = Text("    introducer=True)", font_size=28, color=GREY_B)
        sig1 = VGroup(s1a, s1b, s1c, s1d).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.3)
        txt01 = Text("Inserting", color=PURPLE, font_size=52).next_to(sig1, DOWN, buff=0.6)
        cur01 = Rectangle(color=RED, fill_color=RED, fill_opacity=1,   # cursor colour: set when the cursor is created
                          height=1.0, width=0.14).move_to(txt01[0])
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        win.play(
            TypeWithCursor(
                txt01,                                # parameter text ✓
                cur01,                                # parameter cursor ✓ (a thin rectangular cursor, RED)
                buff=0.12,                            # parameter buff=0.12 ✓ (default 0.1: the gap between the cursor and the last character)
                keep_cursor_y=True,                   # parameter keep_cursor_y=True ✓ (y locked to the centre of the whole text)
                leave_cursor_on=True,                 # parameter leave_cursor_on=True ✓ (the cursor stays when done)
                time_per_char=0.14,                   # parameter time_per_char=0.14 ✓ (default 0.1)
                reverse_rate_function=False,          # parameter reverse_rate_function=False ✓
                introducer=True,                      # parameter introducer=True ✓ (added to the scene before playing)
            ),
            Wait(1.6),                                # slightly longer than the automatic run_time (=0.14*9=1.26s) so the last frame reaches alpha 1
        )
        win.play(                                     # page example: blink the cursor twice after typing
            Blink(
                cur01,                                # parameter mobject ✓
                time_on=0.3,                          # parameter time_on=0.3 ✓
                time_off=0.3,                         # parameter time_off=0.3 ✓
                blinks=2,                             # parameter blinks=2 ✓
            ),
            run_time=1.2,
        )
        win.play(FadeOut(sig1), FadeOut(txt01), FadeOut(cur01), run_time=0.5)

        # —— step 2: UntypeWithCursor(text, cursor, ..., reverse_rate_function=True,
        #                             introducer=False, remover=True) ——
        s2a = Text("UntypeWithCursor(txt, cursor,", font_size=28, color=GREY_B)
        s2b = Text("    buff=0.12, keep_cursor_y=True, leave_cursor_on=True,",
                   font_size=28, color=GREY_B)
        s2c = Text("    time_per_char=0.14, reverse_rate_function=True,",
                   font_size=28, color=GREY_B)
        s2d = Text("    introducer=False, remover=True)", font_size=28, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c, s2d).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.3)
        txt02 = Text("Deleting", color=PURPLE, font_size=52).next_to(sig2, DOWN, buff=0.6)
        cur02 = Rectangle(color=RED, fill_color=RED, fill_opacity=1,
                          height=1.0, width=0.14).move_to(txt02[0])
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        self.add(txt02, cur02)                        # parameter introducer=False → added to the scene by hand first
        win.play(
            UntypeWithCursor(
                txt02,                                # parameter text ✓
                cur02,                                # parameter cursor ✓
                buff=0.12,                            # parameter buff ✓ (inherited from TypeWithCursor)
                keep_cursor_y=True,                   # parameter keep_cursor_y ✓
                leave_cursor_on=True,                 # parameter leave_cursor_on ✓
                time_per_char=0.14,                   # parameter time_per_char=0.14 ✓
                reverse_rate_function=True,           # parameter reverse_rate_function=True ✓ (unlike the parent's False)
                introducer=False,                     # parameter introducer=False ✓ (unlike the parent's True)
                remover=True,                         # parameter remover=True ✓ (removed from the scene when done)
            ),
            Wait(1.6),                                # as above: stretch the duration so the last frame reaches alpha 1
        )
        win.play(FadeOut(sig2), run_time=0.5)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()
```

What this code does: two segments, one typing forward and one deleting in reverse.

- The first segment is a typewriter: a thin red rectangular cursor is attached to the start of "Inserting"; `TypeWithCursor` types it out character by character with `time_per_char=0.14` while the cursor moves right behind it (`buff=0.12` leaves a gap); when typing finishes the cursor stays (`leave_cursor_on=True`) and `Blink` flashes it twice; `Wait(1.6)` stretches this beat past the automatic duration (0.14×9=1.26 s) so the last frame reaches progress 1.
- The second segment plays in reverse: "Deleting" and the cursor are first `self.add`ed to the scene (`introducer=False`); `UntypeWithCursor` deletes characters from the end one by one while the cursor is pulled back along with them, and the whole text is removed from the scene when it finishes.

<video src="assets/RTM output/01b-Typing-with-a-Cursor.mp4" controls width="560"></video>

> Note:
>
> - The cursor is just an ordinary mobject, so **its colour/thickness are set when it is created** (the sample uses a thin red rectangle); the animation signature has no colour parameter.
> - `UntypeWithCursor`'s `introducer` is **not an explicit parameter** in RTM's own version (it reaches `Animation` via `**kwargs`, defaulting to `False`) — without a `self.add(text, cursor)` first the object is not in the scene and the animation spins on nothing.
> - If you want the typing rhythm to be deterministic, do not compress an animation that carries its own total duration, such as `Blink`, with a play-level `run_time`: the two handle "shortened semantics" differently and the blink phase drifts (the sample's `Blink(..., run_time=1.2)` is exactly this case, see the comparison note).

Not demonstrated:

- the cursor's "colour" is not in the animation signature — `cursor` is just a mobject, and its colour is set when the rectangle is created (the sample uses RED, the page example uses GREY_A).
- `UntypeWithCursor(reverse_rate_function=...)` / `(remover=...)` — RTM's own version **has neither of these parameters** (the reverse direction is hard-coded in the class, and `remover` does not remove it from the scene even if passed).
- the remaining common parameters in `**kwargs` have no visual effect.

See also: [Writing and Unwriting](01-Writing-and-Unwriting.md) · [Number Animations](02-Number-Animations.md)
