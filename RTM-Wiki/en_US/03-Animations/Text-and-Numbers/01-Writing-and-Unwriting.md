# Letter-by-letter writing and unwriting: AddTextLetterByLetter and friends

Three animation classes that show/hide a `Text` one character at a time. `AddTextLetterByLetter` and `RemoveTextLetterByLetter` have been render-verified (frame-for-frame aligned across both engines); `AddTextWordByWord` is a broken upstream implementation and is not recommended (see below).

For the typewriter effect with a cursor see [01b-Typing-with-a-Cursor](01b-Typing-with-a-Cursor.md). `Write`/`Unwrite` are "write/erase in one stroke" and belong to the creation-and-removal chapter, see [Create and the drawing family](../Creation-and-Removal/01-Create-and-the-Drawing-Family.md) and [Reverse removal](../Creation-and-Removal/02-Reverse-Removal.md); this page does not cover them.

## Parameters

### `AddTextLetterByLetter` 

```python
AddTextLetterByLetter(text, suspend_mobject_updating=False, int_func=np.ceil,
                      rate_func=linear, time_per_char=0.1, run_time=None,
                      reverse_rate_function=False, introducer=True, **kwargs)
```

Makes a `Text` **pop out one letter at a time** (showing it character by character rather than fading it in smoothly); `time_per_char` controls the typing speed. When `run_time` is not passed it is computed automatically as `max(1/frame rate, time_per_char) * number of characters`. **Only supports `Text`, not `MathTex`**; empty text raises `ValueError`. **Inherits** `AddTextLetterByLetter(ShowIncreasingSubsets)` ← `Animation`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `text` | `Text` | — | the text to reveal letter by letter (must be non-empty) |
| `suspend_mobject_updating` | `bool` | `False` | whether to suspend updaters |
| `int_func` | `Callable` | `np.ceil` | the progress rounding function (`ceil` = show as soon as it is reached) |
| `rate_func` | `Callable` | `linear` | uniform typing speed |
| `time_per_char` | `float` | `0.1` | the minimum display interval per character (seconds) |
| `run_time` | `float \| None` | `None` | if not passed, automatically = `max(1/frame_rate, time_per_char) * len(text)` |
| `reverse_rate_function` | `bool` | `False` | if `True`, it collects in reverse |
| `introducer` | `bool` | `True` | add to the scene before playing |
| `**kwargs` | — | — | `ShowIncreasingSubsets`/`Animation` common parameters |

> **Returns**: an `AddTextLetterByLetter` instance.

One-liner:

```python
t = Text("Typing...", font_size=48)
win.play(AddTextLetterByLetter(t, time_per_char=0.15))
```

### `RemoveTextLetterByLetter` 

```python
RemoveTextLetterByLetter(text, suspend_mobject_updating=False, int_func=np.ceil,
                         rate_func=linear, time_per_char=0.1, run_time=None,
                         reverse_rate_function=True, introducer=False, remover=True, **kwargs)
```

The reverse playback of the parent — **disappears one letter at a time** and is removed from the scene when done. The only difference from the parent is the defaults, which the signature already shows. **Inherits** `RemoveTextLetterByLetter(AddTextLetterByLetter)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `text` | `Text` | — | the text being removed letter by letter |
| `suspend_mobject_updating` | `bool` | `False` | whether to suspend updaters |
| `int_func` | `Callable` | `np.ceil` | the progress rounding function |
| `rate_func` | `Callable` | `linear` | uniform |
| `time_per_char` | `float` | `0.1` | the interval per character (seconds) |
| `run_time` | `float \| None` | `None` | computed automatically like the parent |
| `reverse_rate_function` | `bool` | `True` | play in reverse (unlike the parent's `False`) |
| `introducer` | `bool` | `False` | not added to the scene before playing (unlike the parent's `True`) |
| `remover` | `bool` | `True` | remove from the scene when done |
| `**kwargs` | — | — | `ShowIncreasingSubsets`/`Animation` common parameters |

> **Returns**: a `RemoveTextLetterByLetter` instance.

One-liner:

```python
t = Text("Vanishing")
self.add(t)
win.play(RemoveTextLetterByLetter(t))
```

### `AddTextWordByWord` (broken upstream implementation, not recommended)

```python
AddTextWordByWord(text_mobject, run_time=None, time_per_char=0.06, **kwargs)
```

It is meant to appear "one word at a time", but the upstream source is annotated `# TODO, this is broken...` and its docstring also says *currently broken*: word-splitting a plain `Text` yields nothing, so it renders a static frame — the same result; this is an upstream bug, not a gap in RTM. **Not recommended in new scripts**; for a word-by-word effect use `Text`'s line-level slicing plus `LaggedStart(FadeIn)`. **Inherits** `AddTextWordByWord(Succession)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `text_mobject` | `Text` | — | the text being revealed word by word |
| `run_time` | `float \| None` | `None` | the total duration (computed from the internal sequence if not passed) |
| `time_per_char` | `float` | `0.06` | the interval per word |
| `**kwargs` | — | — | `Succession`/`AnimationGroup` common parameters |

> **Returns**: an `AddTextWordByWord` instance (not recommended to construct).

#### Sample: AddTextLetterByLetter / RemoveTextLetterByLetter demonstrated item by item

The page clip demonstrates AddTextLetterByLetter → RemoveTextLetterByLetter in that order, one segment each, with every parameter labelled on screen.

```python
import os

import numpy as np
from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    RED,
    DOWN,
    UP,
    AddTextLetterByLetter,
    RemoveTextLetterByLetter,
    Scene,
    Text,
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


class Page_01_Writing_and_Unwriting(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameters w=1280 / h=720 / hidden=True
        win.scene = self                          # parameter win.scene

        title = Text("AddTextLetterByLetter / RemoveTextLetterByLetter",
                     font_size=34, color=GREEN).to_edge(UP)   #title uses ASCII only: font fallback stays reliable in both engines
        win.play(Write(title), run_time=0.85)

        # —— step 1: AddTextLetterByLetter(...) ——
        s1a = Text("AddTextLetterByLetter(txt, suspend_mobject_updating=False,",
                   font_size=28, color=GREY_B)
        s1b = Text("    int_func=np.ceil, rate_func=linear, time_per_char=0.25,",
                   font_size=28, color=GREY_B)
        s1c = Text("    run_time=2.4, reverse_rate_function=False, introducer=True)",
                   font_size=28, color=GREY_B)
        sig1 = VGroup(s1a, s1b, s1c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        a01 = Text("Typing...", font_size=50, color=BLUE).next_to(sig1, DOWN, buff=0.9)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        win.play(
            AddTextLetterByLetter(
                a01,                                   # parameter text ✓ (only Text is supported)
                suspend_mobject_updating=False,        # parameter suspend_mobject_updating=False ✓
                int_func=np.ceil,                      # parameter int_func=np.ceil ✓ (shown as soon as reached)
                rate_func=linear,                      # parameter rate_func=linear ✓ (uniform typing speed)
                time_per_char=0.25,                    # parameter time_per_char=0.25 ✓ (default 0.1)
                run_time=2.4,                          # parameter run_time=2.4 ✓ (if not passed it is computed from the character count)
                reverse_rate_function=False,           # parameter reverse_rate_function=False ✓
                introducer=True,                       # parameter introducer=True ✓ (added to the scene before playing)
            ),
        )
        win.play(Wait(0.3))
        win.play(FadeOut(sig1), FadeOut(a01), run_time=0.45)

        # —— step 2: RemoveTextLetterByLetter(...) ——
        s2a = Text("RemoveTextLetterByLetter(txt, suspend_mobject_updating=False,",
                   font_size=28, color=GREY_B)
        s2b = Text("    int_func=np.ceil, rate_func=linear, time_per_char=0.2,",
                   font_size=28, color=GREY_B)
        s2c = Text("    run_time=2.0, reverse_rate_function=True, introducer=False,",
                   font_size=28, color=GREY_B)
        s2d = Text("    remover=True)", font_size=28, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c, s2d).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        b01 = Text("Vanishing", font_size=50, color=RED).next_to(sig2, DOWN, buff=0.7)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        self.add(b01)                                  # parameter introducer=False → added to the scene by hand first
        win.play(
            RemoveTextLetterByLetter(
                b01,                                   # parameter text ✓
                suspend_mobject_updating=False,        # parameter suspend_mobject_updating=False ✓
                int_func=np.ceil,                      # parameter int_func=np.ceil ✓
                rate_func=linear,                      # parameter rate_func=linear ✓
                time_per_char=0.2,                     # parameter time_per_char=0.2 ✓
                run_time=2.0,                          # parameter run_time=2.0 ✓
                reverse_rate_function=True,            # parameter reverse_rate_function=True ✓ (unlike the parent's False)
                introducer=False,                      # parameter introducer=False ✓ (unlike the parent's True)
                remover=True,                          # parameter remover=True ✓ (removed from the scene when done)
            ),
        )
        win.play(FadeOut(sig2), run_time=0.45)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()
```

What this code does: it writes the title first, then demonstrates two typing segments.

- Segment 1: the blue "Typing..." pops out one character at a time with `time_per_char=0.25` (`run_time=2.4` overrides the automatic duration).
- Segment 2: the red "Vanishing" is first `self.add`ed to the scene (`introducer=False` does not introduce it automatically), then disappears one character at a time from the end with `reverse_rate_function=True`; `remover=True` removes the whole text from the scene once it finishes.

Once it has run in the console you can count it out: the character count of each segment × `time_per_char` gives its rhythm.

<video src="assets/RTM output/01-Writing-and-Unwriting.mp4" controls width="560"></video>

> Note:
>
> - `RemoveTextLetterByLetter` defaults to `introducer=False`: **without a `self.add(...)` first the object is not in the scene at all** and the animation spins on nothing; the parent `AddTextLetterByLetter` is the opposite (`introducer=True` introduces it automatically).
> - Both classes **only support `Text`**; feeding them a `MathTex` goes wrong.
> - For `run_time`, if you want "uniform typing", give it enough per `time_per_char * number of characters`; give it too little and the characters pop out bunched together.
