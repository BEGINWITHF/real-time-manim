# Text

The three text classes `Text` / `MarkupText` / `Paragraph`, plus `register_font` (temporarily register a font file). One sample for each of the four.

> **`remove_invisible_chars` is not available**: the current version does not export this function from `real_time_manim` (`from real_time_manim import remove_invisible_chars` raises `ImportError` outright); if you need to strip invisible characters, filter by glyph yourself.

## Parameters

### `Text`

```python
def __init__(self, text: str, fill_opacity: float = 1, stroke_width: float = 0, color: ParsableManimColor | None = None, font_size: float = 48, line_spacing: float = -1, font: str = "", slant: str = "NORMAL", weight: str = "NORMAL", t2c: dict | None = None, t2f: dict | None = None, t2w: dict | None = None, t2s: dict | None = None, disable_ligatures: bool = False, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `text` | `str` | required | the text content; `\n` for a line break |
| `font` | `str` | `""` (default font) | font family name; the sample uses `"Arial"` |
| `font_size` | `float` | `48` | font size; the sample uses 40 / 34 |
| `weight` | `str` | `"NORMAL"` | font weight; the sample uses `"BOLD"` |
| `slant` | `str` | `"NORMAL"` | slant (italic); the sample uses `"ITALIC"` |
| `color` | `ManimColor \| None` | `None` | overall colour; the sample uses `TEAL` |
| `line_spacing` | `float` | `-1` (automatic) | line spacing; the sample uses `1.2` |
| `t2c` | `dict \| None` | `None` | substring → colour (`{"red": RED}`) |
| `t2f` / `t2w` / `t2s` | `dict \| None` | `None` | substring → font / weight / slant |
| `fill_opacity` / `stroke_width` | `float` | `1` / `0` | fill and stroke |

#### Sample: font / font size / weight / slant / line spacing / per-substring colour

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Text, MarkupText, Paragraph, register_font,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class TextDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("08-Text", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— default: a single line of text ——
        t1 = Text("Hello RTM").move_to([0, 1.6, 0])   # the "text" parameter
        win.play(Write(t1), FadeIn(cap('Text("Hello RTM")', t1)), run_time=0.6)

        # —— font / font_size / weight / slant ——
        t2 = Text("Arial 40 bold italic", font="Arial", font_size=40,
                  weight="BOLD", slant="ITALIC").move_to([0, 0.5, 0])   # the "font / font_size / weight / slant" parameters
        win.play(Write(t2), FadeIn(cap('font="Arial" weight=BOLD slant=ITALIC', t2)), run_time=0.7)

        # —— color / line_spacing: overall colour and line spacing of two lines ——
        t3 = Text("first line\nsecond line", font_size=34, color=TEAL,
                  line_spacing=1.2).move_to([0, -1.0, 0])   # the "color / line_spacing" parameters
        win.play(Write(t3), FadeIn(cap("color=TEAL, line_spacing=1.2", t3)), run_time=0.7)

        # —— t2c: colour a given substring on its own ——
        t4 = Text("red green blue", font_size=34,
                  t2c={"red": RED, "green": GREEN, "blue": BLUE}).move_to([0, -2.3, 0])   # the "t2c" parameter
        win.play(Write(t4), FadeIn(cap('t2c={"red": RED, …}', t4)), run_time=0.7)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: MarkupText —— Pango markup text ==========================
```

What this code does: each of the four lines of text demonstrates one group of parameters.

- The first line is the default text.
- The second gives `font="Arial"`, `font_size=40`, `weight="BOLD"` and `slant="ITALIC"` all at once.
- The third is two lines of text, using `color=TEAL` and `line_spacing=1.2` to show the line spacing.
- The fourth uses `t2c` to colour the words `red`/`green`/`blue` red, green and blue respectively.

<video src="assets/RTM output/08-Text-text.mp4" controls width="560"></video>

> Note: the keys of `t2c`/`t2f`/`t2w`/`t2s` are **substrings** and are matched in order of appearance; `line_spacing=-1` means "automatic", so only an explicit positive number is treated as a multiplier.

### `MarkupText`

```python
def __init__(self, text: str, fill_opacity: float = 1, stroke_width: float = 0, color: ParsableManimColor | None = None, font_size: float = 48, line_spacing: float = -1, font: str = "", slant: str = "NORMAL", weight: str = "NORMAL", justify: str = "left", indent: float = 0, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `text` | `str` | required | Pango markup text; the sample only uses `<b>` / `<i>` |
| `font_size` | `float` | `48` | font size; the sample uses 36 / 32 / 30 |
| `color` | `ManimColor \| None` | `None` | overall colour; the sample uses `TEAL` |
| `line_spacing` | `float` | `-1` | line spacing; the sample uses `1.4` |
| `font` / `weight` / `slant` | `str` | default / `NORMAL` | same as `Text` |
| `justify` | `str` | `"left"` | multi-line alignment (`left`/`center`/`right`) |
| `indent` | `float` | `0` | first-line indent |

#### Sample: `<b>`/`<i>` / overall colour / line spacing

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Text, MarkupText, Paragraph, register_font,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class MarkupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("08-MarkupText", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— markup syntax: <b> / <i> / <span foreground=…> ——
        m1 = MarkupText('<b>bold</b> and <i>italic</i>',
                        font_size=36).move_to([0, 1.3, 0])   # the "text" parameter (Pango markup)
        win.play(Write(m1), FadeIn(cap('MarkupText("<b>…</b> <i>…</i>")', m1)), run_time=0.8)

        # —— color / font_size: the overall colour and font size (colours in the markup win) ——
        m2 = MarkupText('colored markup text',
                        font_size=32, color=TEAL).move_to([0, 0.0, 0])   # the "color / font_size" parameters
        win.play(Write(m2), FadeIn(cap("color=TEAL", m2)), run_time=0.8)

        # —— line_spacing / justify: multiple lines and alignment ——
        m3 = MarkupText("line one\nline two is longer", font_size=30,
                        line_spacing=1.4).move_to([0, -1.5, 0])   # the "line_spacing" parameter
        win.play(Write(m3), FadeIn(cap("line_spacing=1.4", m3)), run_time=0.8)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 3: Paragraph —— multiple text blocks, aligned line by line ===
```

What this code does: the first line uses the `<b>` and `<i>` tags for bold and italic; the second colours the whole string `TEAL`; the third is two lines of text with `line_spacing=1.4` spreading them out.

<video src="assets/RTM output/08-Text-markup.mp4" controls width="560"></video>

> Note: RTM parses markup through the Pango→SVG path, and **attributes such as `<span foreground=…>` fail to parse** (`ElementTree.ParseError: no element found`, which is why the sample only uses `<b>`/`<i>`); to colour one thing on its own, give the whole string a `color`, or use `t2c` on `Text`.

### `Paragraph`

```python
def __init__(self, *text: str, line_spacing: float = -1, alignment: str | None = None, **kwargs) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*text` | `str...` | required | each positional argument is one block; the sample uses 3 blocks / 2 blocks |
| `line_spacing` | `float` | `-1` | block spacing; the sample uses `0.6` |
| `alignment` | `str \| None` | `None` | whole-block alignment (`left`/`center`/`right`); the sample uses `"left"` / `"center"` |
| `**kwargs` | `Any` | — | passed to the text (`font_size` / `color` / `font`); the sample uses `color=ORANGE, font="Arial"` |

#### Sample: three blocks left-aligned / block spacing 0.6 / colour and font passed through

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Text, MarkupText, Paragraph, register_font,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class ParagraphDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("08-Paragraph", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— each positional argument is one block; alignment controls the whole block ——
        p1 = Paragraph("first paragraph", "second paragraph", "third",
                       alignment="left", font_size=32).move_to([-0.6, 0.9, 0])   # the "*text / alignment" parameters
        win.play(Write(p1), FadeIn(cap('alignment="left"', p1)), run_time=0.8)

        # —— line_spacing: spacing between blocks ——
        p2 = Paragraph("tight", "spacing", line_spacing=0.6,
                       alignment="center", font_size=32).move_to([-0.6, -1.4, 0])   # the "line_spacing" parameter
        win.play(Write(p2), FadeIn(cap("line_spacing=0.6", p2)), run_time=0.8)

        # —— **kwargs passed through: colour / font ——
        p3 = Paragraph("colored", "paragraph", font_size=32, color=ORANGE,
                       font="Arial").move_to([2.6, -1.4, 0])   # the "**kwargs (color / font)" parameters
        win.play(Write(p3), FadeIn(cap("color=ORANGE, font=Arial", p3)), run_time=0.8)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 4: register_font —— temporarily register a font file ========
```

What this code does: on the upper left are three text blocks with `alignment="left"`; the two below tighten `line_spacing` to 0.6 and switch to centred; the second block on the right passes `color=ORANGE` and `font="Arial"` through to the whole block with `**kwargs`.

<video src="assets/RTM output/08-Text-paragraph.mp4" controls width="560"></video>

> Note: `alignment` aligns the **whole block**, not each block independently; the spacing between blocks is controlled with `line_spacing`, not `\n` (`\n` becomes a line break inside the same block).

### `register_font` ✅

```python
@contextmanager
def register_font(font_file: str | Path) -> Iterator[None]:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `font_file` | `str \| Path` | required | path to the font file; the sample uses `C:\Windows\Fonts\arial.ttf` |

**Context manager**: registering inside a `with register_font(path):` block means a `Text` built inside the block can use the font by its family name.

#### Sample: registering inside a `with` block + reusing it outside + fallback when unregistered

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Text, MarkupText, Paragraph, register_font,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class RegisterFontDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("08-register_font", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— usage: register a font file inside a with block; a Text built in the block can use that family name ——
        font_file = r"C:\Windows\Fonts\arial.ttf"   # the "font_file" parameter: path to the font file
        with register_font(font_file):   # the "font_file" parameter
            t1 = Text("Registered: Arial", font="Arial", font_size=44).move_to([0, 0.9, 0])
            win.play(Write(t1), FadeIn(cap("with register_font(arial.ttf): Text(..., font=\"Arial\")", t1)), run_time=0.8)

        # —— same family name outside the block: already in the font cache, so it still lays out ——
        t2 = Text("outside the with-block", font="Arial", font_size=36,
                  color=TEAL).move_to([0, -0.8, 0])
        win.play(Write(t2), FadeIn(cap("same family name outside the block", t2)), run_time=0.8)

        # —— control case without registering: a family name the system lacks warns and falls back ——
        t3 = Text("fallback family", font_size=36, color=GREY_B).move_to([0, -2.2, 0])
        win.play(Write(t3), FadeIn(cap("an unregistered family falls back to the default font", t3)), run_time=0.8)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: inside `with register_font(r"C:\Windows\Fonts\arial.ttf"):` a line is laid out with `font="Arial"`; after leaving the `with` block the same family name still lays out (the font cache already knows it); the last line omits `font`, using the default font as a control—which shows that what gets registered is the mapping from family name to file.

<video src="assets/RTM output/08-Text-registerfont.mp4" controls width="560"></video>

> Note: registration takes effect by the **family name inside the font file** (not the file name); the `with` block only affects when registration happens, not later use (it is cached within the same process), so a different process must register again.

---

See also: [LaTeX](09-LaTeX.md) · [Typst](10-Typst.md) · [Containers and grouping](06-Containers-and-Grouping.md)
