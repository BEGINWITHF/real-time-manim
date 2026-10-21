# Code blocks

`Code` renders a piece of source into a **syntax-highlighted** code block (based on Pygments, 50 colour schemes), for showing code on screen. One sample for each of the two functions.

> **Two ways to construct it**: `code_string=` takes the source string directly (every sample uses it), while `code_file=` takes a file path (and reads the file); pick one of the two. If `language` is omitted it is inferred from the file extension, so with string construction it is best to write it explicitly.

## Parameters

### `Code`

```python
def __init__(self, code_file: StrPath | None = None, code_string: str | None = None, language: str | None = None, formatter_style: str | Style = "vim", tab_width: int = 4, add_line_numbers: bool = True, line_numbers_from: int = 1, background: Literal["rectangle", "window"] = "rectangle", background_config: dict | None = None, paragraph_config: dict | None = None) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `code_file` | `str \| Path \| None` | `None` | read a file as the source; an alternative to `code_string` |
| `code_string` | `str \| None` | `None` | give the source string directly (the sample uses it; `\n` for a line break, `\t` for an indent) |
| `language` | `str \| None` | `None` | the language name for syntax highlighting (`"python"`, `"javascript"`…); if omitted it is inferred from the file extension |
| `formatter_style` | `str \| Style` | `"vim"` | the colour scheme; the sample uses `"vim"` / `"monokai"`; see `Code.get_styles_list()` for the options |
| `tab_width` | `int` | `4` | tab width (how many characters wide one `\t` is); the sample uses `8` |
| `add_line_numbers` | `bool` | `True` | whether to show line numbers |
| `line_numbers_from` | `int` | `1` | the first line number; the sample starts at `10` |
| `background` | `"rectangle" \| "window"` | `"rectangle"` | the background style: `rectangle` is a flat colour block, `window` looks like a window with a title bar |
| `background_config` | `dict \| None` | `None` | style passed through to the background rectangle (e.g. `{"stroke_color": TEAL, "fill_opacity": 0.3}`) |
| `paragraph_config` | `dict \| None` | `None` | configuration passed through to the internal `Paragraph` (e.g. the font) |

Returns a `Code` (a `VGroup`: the background plus each line of text), which you can `scale`/`move_to` as a whole, or fetch sub-objects by line to colour individually.

#### Sample: language / line numbers / tabs / background style / colour scheme / both configs

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Code, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class CodeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("11-Code", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        # —— code_string + language: default tab_width=4, line numbers on, rectangle background ——
        c1 = Code(code_string="def f(x):\n    return x ** 2\n\nprint(f(3))",
                  language="python")   # the "code_string / language" parameters
        c1.scale(0.75).move_to([0, 0.9, 0])
        win.play(Write(c1), FadeIn(cap('language="python"', c1)), run_time=0.8)

        # —— tab_width / add_line_numbers / line_numbers_from ——
        c2 = Code(code_string="a = 1\nif a:\n\tprint(a)",
                  language="python", tab_width=8,   # the "tab_width" parameter
                  add_line_numbers=True, line_numbers_from=10)   # the "add_line_numbers / line_numbers_from" parameters
        c2.scale(0.75).move_to([-3.6, -1.9, 0])
        win.play(Write(c2), FadeIn(cap("tab_width=8, line numbers from 10", c2)), run_time=0.7)

        # —— background="window" + formatter_style: a window-style background and colour scheme ——
        c3 = Code(code_string="x = [1, 2, 3]\nprint(sum(x))",
                  language="python", background="window",   # the "background" parameter
                  formatter_style="monokai")   # the "formatter_style" parameter
        c3.scale(0.75).move_to([3.4, -1.9, 0])
        win.play(Write(c3), FadeIn(cap('background="window", style="monokai"', c3)), run_time=0.7)

        # —— background_config / paragraph_config: passing styles through ——
        c4 = Code(code_string="s = 'hi'",
                  language="python",
                  background_config={"stroke_color": TEAL, "fill_opacity": 0.3},   # the "background_config" parameter
                  paragraph_config={"font": "monospace"})   # the "paragraph_config" parameter
        c4.scale(0.75).move_to([0, -3.2, 0])
        win.play(Write(c4), run_time=0.6)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window


# ===== Sample 2: Code.get_styles_list —— the available colour schemes =====
```

What this code does: each of the four code blocks demonstrates one group of parameters.

- The first is the plainest `language="python"` (4-wide tabs by default, line numbers on, rectangle background).
- The lower left sets `tab_width` to 8 and starts line numbers at 10.
- The lower right pairs `background="window"` with `formatter_style="monokai"`, clearly showing the window-style base and dark scheme.
- The last block passes in both `background_config` (teal stroke, 0.3 fill) and `paragraph_config` (monospace font).

<video src="assets/RTM output/11-Code-Blocks-code.mp4" controls width="560"></video>

> Note: indent the lines inside `code_string` either with spaces or with `\t`—mixing them makes `tab_width` look like it is "not working"; `background="window"` adds a title bar and takes more height than `rectangle`, so leave a little extra room when laying out.

### `Code.get_styles_list`

```python
def get_styles_list() -> list[str]:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| (no parameters) | — | — | returns every available colour-scheme name (currently 50, such as `vim`, `monokai`, `friendly`…) |

This is a **classmethod**: call it directly as `Code.get_styles_list()`; it returns a list of strings, telling you what `formatter_style` accepts.

#### Sample: listing the first 6 + the same code in three colour schemes

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Code, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class StylesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("11-Code.get_styles_list", font_size=30, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.4)   # write the title

        styles = Code.get_styles_list()   # the "get_styles_list()" method: returns every available colour-scheme name
        # —— the first six names go on screen one by one (which also shows there are far more than the usual few) ——
        names = VGroup(*[Text(s, font_size=22, color=GREY_B) for s in styles[:6]])
        names.arrange(DOWN, buff=0.18).move_to([-4.2, 0.4, 0])
        cnt = Text("%d styles" % len(styles), font_size=24, color=TEAL).next_to(names, DOWN, buff=0.4)
        win.play(FadeIn(names), FadeIn(cnt), run_time=0.7)

        # —— the same code block in three styles, to see the difference at a glance ——
        for i, style in enumerate(("vim", "monokai", "friendly")):
            code = Code(code_string="def f(x):\n    return x ** 2",
                        language="python", formatter_style=style)   # the "formatter_style" parameter
            code.scale(0.6).move_to([0.6 + (i % 2) * 3.2, 0.9 - i * 1.9, 0])
            win.play(Write(code), FadeIn(cap(style, code, buff=0.2, size=16)), run_time=0.6)
        win.play(Wait(0.5))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: on the left the first 6 names from `get_styles_list()` are laid out in a column with the total (currently 50) below; on the right the same piece of Python is rendered in three `formatter_style`s, `vim`, `monokai` and `friendly`, so the difference in colour scheme is obvious at a glance.

<video src="assets/RTM output/11-Code-Blocks-styles.mp4" controls width="560"></video>

> Note: the list `get_styles_list()` returns changes with the Pygments version, so run the method once to confirm a name exists before hard-coding it; the sample shows only the first 6 to avoid filling the whole screen.

---

See also: [Text](08-Text.md) · [LaTeX](09-LaTeX.md) · [Tables](14-Tables.md)
