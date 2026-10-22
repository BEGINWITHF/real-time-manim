# Colors (1): the ManimColor object and color transforms

`ManimColor` is Manim's unified color object; almost every `color=` / `fill_color=` parameter takes it directly. It is quite lenient about how a color is written: color-name strings, hex, integers and tuples all work.

It lives in `utils/color/core.py` and everything is available via `from manim import ...`. For hand-written colors prefer the predefined constants (`RED`, `BLUE_C`, …) and only work with it directly when you need computation, gradients or programmatic generation.

All three samples on this page have been rendered in RTM (RTM has no dedicated color module; colors ride along with vector geometry through generic rendering).

## Parameters

### `ManimColor(value, alpha)`

```python
ManimColor(value: ParsableManimColor | None, alpha: float = 1.0)
```

Internally it is four 0-1 floats `[r, g, b, a]`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `value` | `ParsableManimColor \| None` | required (`None` = pure black) | What can be passed is in the table below: a `ManimColor` itself, a predefined color-name string, a hex string, an int, an int/float tuple… |
| `alpha` | `float` | `1.0` | Opacity 0-1; when `value` already carries an 8-digit hex or a 4-tuple, alpha is included — **passing `alpha` again overrides it** |

> **Returns**: a `ManimColor` instance.

**Supported `value` forms (`ParsableManimColor`)**:

| Form | Example | Description |
| --- | --- | --- |
| `ManimColor` | `ManimColor(RED)` | reuses the internal value directly |
| predefined color-name string | `"RED"`, `"blue_e"` | case-insensitive; an unknown name raises `ValueError` |
| hex string | `"#FF8800"`, `"0xFF8800"`, `"#F80"`, `"#FF880080"` | 3/4-digit forms are auto-expanded; the last two of 8 digits are alpha |
| int | `0xFF8800`, `16744448` | interpreted as `0xRRGGBB` |
| int tuple/array | `(255, 0, 0)`, `np.array([255,0,0])` | interpreted as 0-255 |
| float tuple/array | `(1.0, 0.0, 0.0)`, `(1.0, 0.0, 0.0, 0.5)` | interpreted as 0-1; a 4-tuple includes alpha |
| object with `get_hex()` | — | calls it, then parses as hex |

**Static / class methods for construction**:

| Signature | Meaning |
| --- | --- |
| `ManimColor.parse(color, alpha=1.0) -> ManimColor \| list[ManimColor]` | one color → one `ManimColor`; a sequence → `list` (**a tuple is treated as a sequence** and parsed element-by-element) |
| `ManimColor.from_rgb(rgb, alpha=1.0)` | build from a 3-element RGB (int or float auto-detected) |
| `ManimColor.from_rgba(rgba)` | build from a 4-element RGBA |
| `ManimColor.from_hex(hex_str, alpha=1.0)` | build from `"#XXXXXX"` |
| `ManimColor.from_hsv(hsv, alpha=1.0)` | build from `[h, s, v]` (each 0-1); RTM-tested: **pass a tuple** — a `list` is misparsed as an int RGB array and yields a wrong color |
| `ManimColor.from_hsl(hsl, alpha=1.0)` | build from `[h, l, s]` (each 0-1) |

#### Sample: five `value` forms and `to_hex`

Five blocks in a row, each built with a different `value` form; above each block is the source form and below it the `to_hex()` output. The last block also demonstrates the translucent effect of the `alpha` parameter.

```python
from real_time_manim import Scene, Square, Text, VGroup, ManimColor, YELLOW, WHITE, \
    GREY_B, UP, DOWN, RIGHT, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class ColorParseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01-ManimColor", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        vals = [ManimColor("#FF8800"), ManimColor((255, 0, 0)), ManimColor(0x00FF00),   #hex string / 0-255 int tuple / int
                ManimColor("RED"), ManimColor("BLUE", alpha=0.4)]   #predefined color name / color name + "alpha" param
        labs = ["'#FF8800'", "(255, 0, 0)", "0x00FF00", "'RED'", "alpha=0.4"]   #how each color is written in source
        sw = VGroup(*[Square(side_length=1.0, stroke_width=2).set_fill(c, 1) for c in vals])   #five color blocks, filled 0.9 opaque
        sw.arrange(RIGHT, buff=0.5).move_to(UP * 0.55)   #arrange left to right in a row
        src = VGroup(*[Text(s, font_size=15, color=GREY_B).next_to(m, UP, buff=0.18)
                       for s, m in zip(labs, sw)])   #above each block: how the value is written
        hx = VGroup(*[Text(c.to_hex(), font_size=16, color=WHITE).next_to(m, DOWN, buff=0.18)
                      for c, m in zip(vals, sw)])   #below each block: the to_hex() result
        hint = Text("to_hex() -> '#RRGGBB'", font_size=22, color=YELLOW).to_edge(DOWN)   #note that the bottom row comes from to_hex
        self.add(sw, src, hx, hint)   #add the blocks, both label rows and the hint to the scene
        win.play(FadeIn(sw), run_time=0.6)   #the whole row of blocks fades in
        win.play(FadeIn(src), FadeIn(hx), run_time=0.6)   #source-form and hex-result rows fade in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: five blocks are built from a hex string, a `0-255` int tuple, an int, a color-name string, and a color name + `alpha=0.4`, laid out in a row.

The upper row is how each block is written in source; the lower row is the `#RRGGBB` printed back by `to_hex()` — the two representations of the same color line up.

The last block is visibly darker on the black background because of `alpha=0.4` — proof that opacity took effect.

<video src="assets/RTM output/01-Colors-parse.mp4" controls width="560"></video>

> Note:
>
> - The `alpha` parameter clashes with any alpha inside `value`: in `ManimColor("#FF880080")` the `80` is already alpha, so writing `alpha=0.9` overrides it.
> - Color names are case-insensitive (`"RED"`, `"blue_e"` both work); a wrong name raises `ValueError` directly.

### `ManimColor.to_hex(with_alpha)`

```python
ManimColor.to_hex(with_alpha: bool = False) -> str
```

Outputs uppercase `"#RRGGBB"`; the most common conversion when printing / writing configs / logging. **Returns** `str`. Its visual effect is folded into the previous sample — the row below each block is its output.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `with_alpha` | `bool` | `False` | `False` outputs the 6-digit `#RRGGBB`; `True` outputs the 8-digit `#RRGGBBAA` |

### `ManimColor.darker` / `ManimColor.lighter`

```python
ManimColor.darker(blend: float = 0.2) -> Self
ManimColor.lighter(blend: float = 0.2) -> Self
```

`darker` interpolates toward `BLACK` for a deeper color; `lighter` interpolates toward `WHITE` for a brighter color (fully symmetric usage). **Returns a new object, leaves the original unchanged**, with opacity preserved. The easiest way to build shades within one hue (headers / cells / shadows).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `blend` | `float` | `0.2` | `darker`: 0 = unchanged, 1 = pure black; `lighter`: 0 = unchanged, 1 = pure white. Any float 0-1 works |

> **Returns**: a new `ManimColor` (the original is untouched).

#### Sample: shades within one hue

Starting from `RED`, two steps brighter and two steps darker, with the original kept in the middle — the gradient toward white / toward black is obvious at a glance.

```python
from real_time_manim import Scene, Square, Text, VGroup, ManimColor, YELLOW, GREY_B, \
    UP, DOWN, RIGHT, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class ColorDepthDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01-darker-lighter", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        base = ManimColor("RED")   #base color: predefined name "RED"
        cols = [base.lighter(0.6), base.lighter(0.3), base,   #two steps toward white + original
                base.darker(0.3), base.darker(0.6)]   #two steps toward black
        labs = ["lighter(0.6)", "lighter(0.3)", "'RED'", "darker(0.3)", "darker(0.6)"]   #where each block comes from
        sw = VGroup(*[Square(side_length=1.1, stroke_width=2).set_fill(c, 1) for c in cols])   #five color blocks
        sw.arrange(RIGHT, buff=0.45).move_to(UP * 0.55)   #arrange left to right in a row
        src = VGroup(*[Text(s, font_size=15, color=GREY_B).next_to(m, UP, buff=0.2)
                       for s, m in zip(labs, sw)])   #label the blend call above each block
        note = Text("new object, original unchanged", font_size=20, color=YELLOW).to_edge(DOWN)   #emphasize "returns a new object"
        self.add(sw, src, note)   #add the blocks, labels and note to the scene
        win.play(FadeIn(sw), run_time=0.6)   #the whole row of blocks fades in
        win.play(FadeIn(src), FadeIn(note), run_time=0.6)   #labels and note fade in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: with `ManimColor("RED")` as the base, the two left blocks are `lighter(0.6)` / `lighter(0.3)` (further left is closer to pale pink), the middle is the original itself, and the two right blocks are `darker(0.3)` / `darker(0.6)` (further right is closer to dark red). The middle block stays pure red, showing these methods **return a new object** and never modify `base` itself.

<video src="assets/RTM output/01-Colors-depth.mp4" controls width="560"></video>

> Note:
>
> - A `blend` above 1 or below 0 does not error, but is clamped to the 0/1 endpoint effects.
> - `darker` / `lighter` only touch the color, not opacity: a color with alpha still changes shade, with its opacity kept as-is.

### `color_gradient(reference_colors, length_of_output)`

```python
color_gradient(reference_colors: Iterable[ParsableManimColor], length_of_output: int) -> list[ManimColor]
```

Uniformly expands a list of reference colors into `length_of_output` colors (linear interpolation between adjacent stops); use it for heat bars, color scales and coloring a `VGroup` one by one. **Returns** `list[ManimColor]`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `reference_colors` | `Iterable[ParsableManimColor]` | required | reference colors (≥1; a single one is replicated to fill the output); any parsable color works |
| `length_of_output` | `int` | required | number of output colors (`0` returns an empty list); any non-negative int works |

#### Sample: same reference colors, two `length_of_output`

Three reference colors `RED → YELLOW → BLUE` expand into two ramps of 6 and 14 colors; only the count differs.

```python
from real_time_manim import Scene, Square, Text, VGroup, color_gradient, RED, YELLOW, \
    BLUE, GREY_B, UP, DOWN, RIGHT, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class ColorGradientDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01-color_gradient", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        ramp6 = color_gradient([RED, YELLOW, BLUE], 6)   #expand three reference colors into 6
        sq6 = VGroup(*[Square(side_length=0.7, stroke_width=1).set_fill(c, 1) for c in ramp6])   #6 large color blocks
        sq6.arrange(RIGHT, buff=0.08).move_to(UP * 1.0)   #arrange into a thick ramp
        lab6 = Text("color_gradient([RED, YELLOW, BLUE], 6)", font_size=17, color=GREY_B)
        lab6.next_to(sq6, UP, buff=0.25)   #label the call above the thick ramp

        ramp14 = color_gradient([RED, YELLOW, BLUE], 14)   #same reference colors expanded into 14
        sq14 = VGroup(*[Square(side_length=0.45, stroke_width=1).set_fill(c, 1) for c in ramp14])   #14 small color blocks
        sq14.arrange(RIGHT, buff=0.05).move_to(DOWN * 0.7)   #arrange into a thin ramp
        lab14 = Text("color_gradient([RED, YELLOW, BLUE], 14)", font_size=17, color=GREY_B)
        lab14.next_to(sq14, UP, buff=0.22)   #label the call above the thin ramp
        note = Text("same reference colors, different length_of_output", font_size=19,
                    color=YELLOW).to_edge(DOWN)   #the two rows differ only in count
        self.add(sq6, lab6, sq14, lab14, note)   #add both ramps and the note to the scene
        win.play(FadeIn(sq6), FadeIn(lab6), run_time=0.6)   #thick ramp first
        win.play(FadeIn(sq14), FadeIn(lab14), FadeIn(note), run_time=0.6)   #then the thin ramp and the note
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: the same reference colors `[RED, YELLOW, BLUE]` go through `color_gradient` twice — a 6-cell row on top and a 14-cell row below, both running red through yellow to blue. The reference colors are unchanged and only `length_of_output` varies, so the only thing that changes is the sampling density: more cells means finer color steps, so for a heat bar pick as large a number as the smoothness you want.

<video src="assets/RTM output/01-Colors-gradient.mp4" controls width="560"></video>

> Note: `color_gradient` is a **module-level function** (`from manim import color_gradient`); the same-named method `ManimColor.gradient(...)` raises `NotImplementedError` directly — don't mix them up.

Not demonstrated: `ManimColor.parse` / `from_rgb` / `from_rgba` / `from_hex` / `from_hsv` / `from_hsl` — all six are construction shortcuts whose colors are bit-identical to calling `ManimColor(...)` directly (sample 1 already covers the end result), so a separate clip carries no extra information.

`to_hex(with_alpha=True)` just prints two more alpha digits and likewise has no standalone visual; which of `alpha` and an 8-digit hex wins is only visible in the numbers, and the translucent block in sample 1 already gives the visual conclusion.

---

See also: [Colors Advanced](01b-Colors-Advanced.md) | [Rate Functions](02-Rate-Functions.md)
