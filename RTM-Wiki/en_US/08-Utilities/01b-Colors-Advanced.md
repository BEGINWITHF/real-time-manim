# Colors (2): interpolation and module-level tools

Continuing from [Colors](01-Colors.md): two-color interpolation for `ManimColor`, a quick table of per-channel methods, and interpolation / averaging / random color picking plus a batch of color↔float conversion functions, all available via `from manim import ...`. Both samples on this page have been rendered in RTM (the random-color sample uses a fixed seed so both engines draw the same colors).

## Parameters

### `ManimColor.interpolate`

```python
ManimColor.interpolate(other: Self, alpha: float) -> Self
```

Linear interpolation in RGBA space: `alpha=0` is self, `alpha=1` is `other`; gradients, value-driven coloring and animated color transitions all rely on it.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `other` | `ManimColor` | required | target color; any parsable color works |
| `alpha` | `float` | required | interpolation position 0-1; 0 = self, 1 = target, linear in between |

> **Returns**: a new `ManimColor` (the original is unchanged).

#### Sample: a nine-step `RED → BLUE` interpolation band

`alpha` is evenly divided into 9 steps from 0 to 1 and lit block by block; the middle block switches to the module-level `interpolate_color(...)` form — its color is bit-identical to `interpolate`.

```python
from real_time_manim import Scene, Square, Text, VGroup, ManimColor, interpolate_color, \
    RED, BLUE, YELLOW, WHITE, GREY_B, UP, DOWN, RIGHT, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class ColorInterpolateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01b-interpolate", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        cols = [RED.interpolate(BLUE, i / 8) for i in range(9)]   #alpha evenly divided into 9 steps from 0 to 1
        sq = VGroup(*[Square(side_length=0.85, stroke_width=1).set_fill(c, 1) for c in cols])   #9 color blocks
        sq.arrange(RIGHT, buff=0.12).move_to(UP * 0.55)   #arrange into an interpolation band, left to right
        sq[4].set_fill(interpolate_color(RED, BLUE, 0.5), 1)   #the middle block switches to the function form; the color is bit-identical to interpolate
        lab = Text("RED.interpolate(BLUE, i / 8)", font_size=18, color=GREY_B)
        lab.next_to(sq, UP, buff=0.3)   #label the call above the band
        l0 = Text("alpha=0  RED", font_size=16, color=GREY_B).next_to(sq[0], DOWN, buff=0.22)   #left end = self
        l1 = Text("alpha=1  BLUE", font_size=16, color=GREY_B).next_to(sq[-1], DOWN, buff=0.22)   #right end = target color
        lm = Text("interpolate_color(RED, BLUE, 0.5)", font_size=16, color=WHITE)
        lm.next_to(sq[4], DOWN, buff=0.55)   #the middle block = the same result as the function form
        self.add(lab, l0, l1, lm)   #add the labels to the scene first (the blocks fade in one by one later)
        for m in sq:   #fade in block by block in increasing alpha so the color change is visible
            win.play(FadeIn(m), run_time=0.12)
        win.play(FadeIn(lab), FadeIn(l0), FadeIn(l1), FadeIn(lm), run_time=0.5)   #the three labels fade in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: nine blocks light up one by one from red to blue at `alpha = 0, 1/8, …, 1`; the middle block is deliberately rewritten as `interpolate_color(RED, BLUE, 0.5)` — no color difference is visible, proving the two forms give the same result. The left end is labeled `alpha=0` (original) and the right end `alpha=1` (target), showing interpolation stepping across one notch at a time.

<video src="assets/RTM output/01b-Colors-Advanced-interpolate.mp4" controls width="560"></video>

> Note: `interpolate` interpolates in **RGBA** space — when the two ends have different opacity, the intermediate `alpha` shifts linearly too; to change only the color and not opacity, pair it with `opacity(...)`.

### Other frequently used `ManimColor` methods (quick table)

Supports the operators `+ - * / // % **`, `~color`, `int()`, `color[i]` and `==` (indexing and comparison); the entries marked as covered appear in the two samples below.

| Signature | Frequency | Meaning |
| --- | --- | --- |
| `to_rgb() -> FloatRGB` | 🟡 | 3 floats 0-1 |
| `to_int_rgb() -> IntRGB` | ⚪ | 3 ints 0-255 |
| `to_rgba() -> FloatRGBA` | 🟡 | 4 floats 0-1 (with alpha) |
| `to_int_rgba() -> IntRGBA` | ⚪ | 4 ints 0-255 |
| `to_rgba_with_alpha(alpha) -> FloatRGBA` | ⚪ | RGBA array with a different alpha |
| `to_int_rgba_with_alpha(alpha) -> IntRGBA` | ⚪ | same, int form |
| `to_integer() -> int` | ⚪ | `0xRRGGBB` int (drops alpha) |
| `to_hsv() -> FloatHSV` | 🟡 | `[h, s, v]`, each 0-1 |
| `to_hsl() -> FloatHSL` | ⚪ | `[h, l, s]`, each 0-1 |
| `invert(with_alpha=False) -> Self` | 🟡 | per-channel linear inversion (returns a new object) — **shown in sample 2** |
| `opacity(opacity) -> Self` | 🟡 | replaces alpha only, keeps the color — **shown in sample 2** |
| `contrasting(threshold=0.5, light=None, dark=None) -> Self` | 🟡 | returns the more readable of a pair by luminance (white/black by default) — dark-bg white text, light-bg black text — **shown in sample 2** |
| `into(class_type) -> Self` | ⚪ | convert to another color-space class (e.g. `HSV`), internal value unchanged |
| `gradient(colors, length)` | ⚪ | **raises `NotImplementedError`** — use module-level `color_gradient` instead |
| `ManimColorDType` | ⚪ | internal float dtype, only for numpy-level work |

### `interpolate_color` / `average_color` / `random_color` / `random_bright_color`

```python
interpolate_color(color1: ManimColorT, color2: ManimColorT, alpha: float) -> ManimColorT
average_color(*colors: ParsableManimColor) -> ManimColor
random_color() -> ManimColor
random_bright_color() -> ManimColor
```

The color-picking functions each do their own thing:

- `interpolate_color(c1, c2, alpha)` is the function form of `c1.interpolate(c2, alpha)`, handy for `lambda`s;
- `average_color(*colors)` averages per channel for the middle color (**ignores alpha**; result opacity 1.0);
- `random_color()` picks one color at random from the whole Manim palette;
- `random_bright_color()` is a random color half-blended with `WHITE` (**expensive** — don't call it in bulk inside a loop).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `color1` / `color2` | `ManimColor` | required | the two interpolation ends; any parsable color works |
| `alpha` | `float` | required | `0` = color1, `1` = color2 |
| `*colors` | `ParsableManimColor` | required | colors to average (≥1) |

> **Returns**: a `ManimColor`.

#### Sample: color-picking functions and three instance methods together

Three rows, each demonstrating one group:

- The first row is three color-picking functions (average / random / bright random, with the random part pinned by `random.seed(7)`);
- The second row is `invert()` / `opacity(0.35)`;
- The third row is the text color `contrasting()` automatically picks on dark and light panels.

```python
import random

from real_time_manim import Scene, Square, Rectangle, Text, VGroup, ManimColor, \
    average_color, random_color, random_bright_color, RED, BLUE, YELLOW, \
    WHITE, GREY_B, UP, DOWN, LEFT, RIGHT, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class ColorHelpersDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("01b-ColorHelpers", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        random.seed(7)   #pin the random seed so every run (on either engine) draws the same colors
        # —— row 1: three color-picking functions ——
        gen = [average_color(RED, BLUE), random_color(), random_bright_color()]   #average / random / bright random
        glab = ["average_color(RED, BLUE)", "random_color()", "random_bright_color()"]
        gsw = VGroup(*[Square(side_length=1.3, stroke_width=2).set_fill(c, 1) for c in gen])
        gsw.arrange(RIGHT, buff=1.2).move_to(UP * 1.7)   #three blocks in a row, spaced for the labels
        gt = VGroup(*[Text(s, font_size=15, color=GREY_B).next_to(m, DOWN, buff=0.18)
                      for s, m in zip(glab, gsw)])   #function name below each block
        gh = VGroup(*[Text(c.to_hex(), font_size=15, color=WHITE).next_to(m, UP, buff=0.18)
                      for c, m in zip(gen, gsw)])   #hex result above each block
        # —— row 2: three instance methods ——
        src = ManimColor("RED")
        meth = [src, src.invert(), src.opacity(0.35)]   #original / per-channel inversion / alpha-only swap
        mlab = ["'RED'", "invert()", "opacity(0.35)"]
        msw = VGroup(*[Square(side_length=1.3, stroke_width=2).set_fill(c, 1) for c in meth])
        msw.arrange(RIGHT, buff=1.2).move_to(DOWN * 0.35)   #three blocks in a row
        mt = VGroup(*[Text(s, font_size=15, color=GREY_B).next_to(m, DOWN, buff=0.18)
                      for s, m in zip(mlab, msw)])   #method name below each block
        # —— row 3: contrasting picks a readable text color ——
        dark = Rectangle(width=3.6, height=1.0, stroke_width=2).set_fill("#333333", 1)
        dark.set_stroke(GREY_B, 1).move_to(LEFT * 2.1 + DOWN * 2.5)   #dark backing panel
        dtx = Text("dark bg -> white text", font_size=20,
                   color=ManimColor("#333333").contrasting()).move_to(dark)   #picks white text on the dark panel
        lite = Rectangle(width=3.6, height=1.0, stroke_width=2).set_fill("#DDDDDD", 1)
        lite.set_stroke(GREY_B, 1).move_to(RIGHT * 2.1 + DOWN * 2.5)   #light backing panel
        ltx = Text("light bg -> black text", font_size=20,
                   color=ManimColor("#DDDDDD").contrasting()).move_to(lite)   #picks black text on the light panel
        self.add(gt, gh, mt)   #labels go in first
        win.play(FadeIn(gsw), FadeIn(gt), FadeIn(gh), run_time=0.6)   #row 1 blocks and labels
        win.play(FadeIn(msw), FadeIn(mt), run_time=0.6)   #row 2 blocks and labels
        win.play(FadeIn(VGroup(dark, dtx, lite, ltx)), run_time=0.6)   #row 3 contrast panels
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: three rows, each demonstrating one group.

- The first row's three blocks are the "red-blue average" (a pinkish-purple), the color drawn by `random_color()`, and the pale color `random_bright_color()` makes by half-blending it with white; above each block is its `to_hex()`.
- The second row starts from pure red: `invert()` gives the cyan-blue complement, `opacity(0.35)` gives a translucent red (dark red on the black background).
- The third row's two panels are dark and light, and `contrasting()` picks white and black text for them — a one-line solution for "dark background, white text; light background, black text".

<video src="assets/RTM output/01b-Colors-Advanced-helpers.mp4" controls width="560"></video>

> Note:
>
> - `random_color()` / `random_bright_color()` use Python's global random state, so **the colors differ every run** — the `random.seed(7)` at the start of the sample is there so both engines and every render draw the same colors; in real projects remember to control the seed yourself.
> - `random_bright_color()` is officially marked "expensive" — don't put it in a large loop.

### Other color module tools

| Signature | Meaning |
| --- | --- |
| `color_to_rgb(color) -> FloatRGB` | any parsable color → 3 floats 0-1 |
| `color_to_rgba(color, alpha=1.0) -> FloatRGBA` | → 4 floats 0-1 |
| `color_to_int_rgb(color) -> IntRGB` | → 3 ints 0-255 |
| `color_to_int_rgba(color, alpha=1.0) -> IntRGBA` | → 4 ints 0-255 |
| `rgb_to_color(rgb) -> ManimColor` | 3-array → color |
| `rgba_to_color(rgba) -> ManimColor` | 4-array → color |
| `rgb_to_hex(rgb) -> str` | 3-array → `"#RRGGBB"` |
| `hex_to_rgb(hex_code) -> FloatRGB` | `"#RRGGBB"` → 3 floats |
| `invert_color(color) -> ManimColor` | function form of `color.invert()` |
| `get_shaded_rgb(rgb, point, unit_normal_vect, light_source) -> FloatRGB` | shade by surface orientation vs light source (custom 3D shading) |
| `HSV` | `HSV([h, s, v], alpha=1.0)` with read/write attrs `hue/saturation/value` (aliases `h/s/v`); `RGBA` is a `ManimColor` alias |
| `RandomColorGenerator(seed=None, sample_colors=None)` + `.next() -> ManimColor` | seedable color generator; `sample_colors` restricts the candidate palette |

Not demonstrated: `to_rgb` / `to_int_rgb` / `to_rgba` / `to_int_rgba` / `to_rgba_with_alpha` / `to_integer` / `to_hsv` / `to_hsl` / `into` — all are value reads / representation changes that return numbers and produce no visual.

`ManimColor.gradient` — always raises `NotImplementedError`; use `color_gradient` instead.

`color_to_*` / `rgb_to_*` / `hex_to_rgb` / `invert_color` / `get_shaded_rgb` / `HSV` / `RGBA` / `RandomColorGenerator` — bit-for-bit equivalent to the corresponding methods already shown in the samples (`RandomColorGenerator(seed=...)` is just a controllable `random_color()`), so a separate clip has no new information.

---

See also: [Colors](01-Colors.md) | [Rate Functions](02-Rate-Functions.md)
