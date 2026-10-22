# Directions and math constants

The constants live in `constants.py` and are all available via `from manim import ...`; the tables below cover all 64 exported names. Direction constants are `numpy.ndarray`s, so you can add them and multiply them by scalars directly (`2 * UP + 3 * RIGHT`).

RTM reuses manim's constants module directly; the values are bit-identical to upstream.

Both samples — direction construction and circle division — have been rendered in RTM; pure-value constants like sizes, quality and font weights have no standalone visual and are collected in the tables in the second half of the page.

## Direction and axis vectors (14)

| Constant | Value | Meaning |
| --- | --- | --- |
| `ORIGIN` | `[0, 0, 0]` | origin |
| `UP` | `[0, 1, 0]` | +Y one unit |
| `DOWN` | `[0, -1, 0]` | −Y one unit |
| `RIGHT` | `[1, 0, 0]` | +X one unit |
| `LEFT` | `[-1, 0, 0]` | −X one unit |
| `IN` | `[0, 0, -1]` | −Z one unit (**into the screen**) |
| `OUT` | `[0, 0, 1]` | +Z one unit (**out of the screen**, the 3D default axis) |
| `X_AXIS` | `[1, 0, 0]` | X basis vector |
| `Y_AXIS` | `[0, 1, 0]` | Y basis vector |
| `Z_AXIS` | `[0, 0, 1]` | Z basis vector |
| `UL` | `UP + LEFT` = `[-1, 1, 0]` | upper-left diagonal |
| `UR` | `UP + RIGHT` = `[1, 1, 0]` | upper-right diagonal |
| `DL` | `DOWN + LEFT` = `[-1, -1, 0]` | lower-left diagonal |
| `DR` | `DOWN + RIGHT` = `[1, 1, 0]` | lower-right diagonal |

#### Sample: eight directions and diagonal construction

A dot marks the origin; the four cardinal arrows are drawn right → up → left → down in turn, then the four diagonal arrows fade in all at once; the bottom note explains how diagonals are built and the Z-axis meaning of `IN` / `OUT`.

```python
from real_time_manim import Scene, Text, VGroup, Dot, Arrow, BLUE, GREEN, RED, \
    ORANGE, PURPLE, YELLOW, GREY_B, WHITE, UP, DOWN, LEFT, RIGHT, ORIGIN, \
    UL, UR, DL, DR, FadeIn, Write, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class DirectionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("03-direction constants", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        origin = Dot(ORIGIN, radius=0.07, color=WHITE)   #origin ORIGIN
        win.play(FadeIn(origin), run_time=0.3)   #show the origin first
        lab0 = Text("ORIGIN", font_size=16, color=WHITE).next_to(origin, DOWN, buff=0.2)
        win.play(FadeIn(lab0), run_time=0.25)   #origin label

        mains = [("RIGHT", RIGHT, BLUE), ("UP", UP, GREEN),   #four cardinal directions
                 ("LEFT", LEFT, RED), ("DOWN", DOWN, ORANGE)]
        for nm, d, c in mains:   #draw arrows right → up → left → down in turn
            ar = Arrow(ORIGIN, 2.0 * d, buff=0, color=c, stroke_width=6)   #direction arrow of length one unit
            lb = Text(nm, font_size=20, color=c).next_to(ar.get_end(), d, buff=0.2)   #write the constant name outside the arrow
            win.play(Create(ar), run_time=0.45)   #draw the arrow
            win.play(FadeIn(lb), run_time=0.2)   #then add its name

        diags = [("UR", UR), ("UL", UL), ("DL", DL), ("DR", DR)]   #four diagonal directions
        dgrp = VGroup()
        for nm, d in diags:   #diagonal = sum of two cardinal directions, all at once
            ar = Arrow(ORIGIN, 1.7 * d, buff=0, color=PURPLE, stroke_width=5)
            lb = Text(nm, font_size=18, color=PURPLE).next_to(ar.get_end(), d, buff=0.18)
            dgrp.add(ar, lb)
        win.play(FadeIn(dgrp), run_time=0.5)   #the whole group of diagonal arrows fades in
        note = Text("UR = UP + RIGHT   |   IN / OUT = Z axis", font_size=18,
                    color=GREY_B).to_edge(DOWN)   #note on how diagonals are built and the Z axis
        win.play(FadeIn(note), run_time=0.35)   #note fades in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: it puts a white dot at the origin labeled "ORIGIN", then draws one twice-as-long arrow right → up → left → down each, with the constant name in matching color outside the arrow; the four diagonals (`UR` / `UL` / `DL` / `DR`) are grouped and fade in all at once, and the bottom note explains "diagonal = sum of two cardinal directions" and that `IN` / `OUT` run along the Z axis.

<video src="assets/RTM output/03-Directions-and-Constants-directions.mp4" controls width="560"></video>

> Note: direction constants are `numpy.ndarray`s with **no** aliases beyond `IN` / `OUT` — `IN = [0, 0, -1]` points into the screen, `OUT = [0, 0, 1]` out of it; you can also just write `UP + RIGHT` for a diagonal, since `UR` is only its ready-made alias.

## Math constants `PI` / `TAU` / `DEGREES` and `compass_directions`

| Constant | Value | Meaning |
| --- | --- | --- |
| `PI` | `3.14159265…` | π |
| `TAU` | `2 * PI = 6.28318530…` | circumference/radius (radians in one full turn) |
| `DEGREES` | `TAU / 360 = 0.01745329…` | degree→radian factor: `30 * DEGREES` |

`compass_directions(n, start_vect=RIGHT, clockwise=False)` rotates `start_vect` by `TAU / n` ` n ` times, returning `n` direction vectors evenly spaced around a circle (`dot[0]` is the starting direction); use it for compasses, divisions and equally angled arrows.

#### Sample: dividing a circle into 8 and three arc lengths

The left half uses `compass_directions(8, start_vect=RIGHT)` to place 8 evenly spaced direction dots on a helper circle (the 0th is marked as the starting direction); the right half overlays three arcs at the same center — `TAU` (full turn), `PI` (half turn) and `45 * DEGREES` (a 45° arc) — and lists the three values below.

```python
from real_time_manim import Scene, Text, VGroup, Dot, Circle, Arc, BLUE, GREEN, \
    RED, YELLOW, GREY_B, UP, DOWN, LEFT, RIGHT, PI, TAU, DEGREES, \
    compass_directions, FadeIn, Write, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class CompassMathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        title = Text("03-compass_directions", font_size=34, color=YELLOW).to_edge(UP)   #page title
        win.play(Write(title), run_time=0.5)   #write out the title

        # —— left half: compass_directions rotates start_vect n times ——
        c = [-3.6, -0.4, 0]   #center of the left figure
        ring = Circle(radius=1.6, color=GREY_B, stroke_width=3).move_to(c)   #helper circle
        pts = compass_directions(8, start_vect=RIGHT)   #start from the right and rotate TAU/8 each time for 8 directions
        dots = VGroup(*[Dot(1.6 * p + c, radius=0.07,
                            color=BLUE if i == 0 else YELLOW) for i, p in enumerate(pts)])   #index 0 is start_vect
        lab_l = Text("compass_directions(8, start_vect=RIGHT)", font_size=15, color=GREY_B)
        lab_l.move_to([-3.6, 1.7, 0])   #left figure title
        lab_r = Text("dot[0] = start_vect", font_size=15, color=BLUE)
        lab_r.next_to(ring, DOWN, buff=0.35)   #the blue dot is the starting direction
        win.play(Create(ring), FadeIn(lab_l), run_time=0.5)   #helper circle and title
        win.play(FadeIn(dots), FadeIn(lab_r), run_time=0.5)   #8 evenly spaced direction dots
        # —— right half: the three math constants TAU / PI / DEGREES ——
        cc = [3.0, 0.2, 0]   #center of the right figure
        full = Arc(radius=1.5, start_angle=0, angle=TAU, arc_center=cc,
                   color=BLUE, stroke_width=4)   #one full turn = TAU
        half = Arc(radius=1.5, start_angle=0, angle=PI, arc_center=cc,
                   color=GREEN, stroke_width=7)   #half turn = PI
        wedge = Arc(radius=1.5, start_angle=0, angle=45 * DEGREES, arc_center=cc,
                    color=RED, stroke_width=12)   #45° = 45 * DEGREES
        vals = VGroup(
            Text("TAU = 6.28319", font_size=17, color=BLUE),
            Text("PI = 3.14159", font_size=17, color=GREEN),
            Text("45 * DEGREES = 0.78540", font_size=17, color=RED),
        ).arrange(DOWN, buff=0.18, aligned_edge=LEFT)   #three value lines, same colors as the three arcs
        vals.move_to([3.0, -2.4, 0])   #placed below the right figure
        win.play(Create(full), run_time=0.7)   #draw the full turn first
        win.play(Create(half), run_time=0.45)   #then overlay the half turn
        win.play(Create(wedge), run_time=0.3)   #finally the 45° arc
        win.play(FadeIn(vals), run_time=0.45)   #the three value lines fade in
        win.play(Wait(0.6))   #wait 0.6s
        win.close()   #close the RTM window
```

What this code does: on the left a helper circle is drawn and `compass_directions(8, start_vect=RIGHT)` places 8 evenly spaced direction dots, with the 0th deliberately colored blue to show "it is the starting direction".

On the right, three arcs of different thicknesses are drawn at the same center in the order "full turn → half turn → 45°", and three same-colored value lines below spell out the actual sizes of `TAU`, `PI` and `45 * DEGREES` — to turn degrees into radians, just multiply by `DEGREES`.

<video src="assets/RTM output/03-Directions-and-Constants-compass_math.mp4" controls width="560"></video>

> Note:
>
> - `compass_directions` returns **direction vectors** (length 1); to place dots you still multiply by a radius yourself (in the sample, `1.6 * p + c`); `clockwise=True` rotates the other way.
> - `Arc(angle=...)` takes **radians** — write `45 * DEGREES`, not `45`.

## Default sizes, buffers and timing (19)

| Constant | Value | Meaning | Constant | Value | Meaning |
| --- | --- | --- | --- | --- | --- |
| `START_X` | `30` | initial canvas width (px, internal) | `START_Y` | `20` | initial canvas height (px, internal) |
| `DEFAULT_DOT_RADIUS` | `0.08` | default `Dot` / `Dot3D` radius | `DEFAULT_SMALL_DOT_RADIUS` | `0.04` | smaller default dot radius |
| `DEFAULT_DASH_LENGTH` | `0.05` | `DashedLine` default segment length | `DEFAULT_ARROW_TIP_LENGTH` | `0.35` | default arrow-tip length |
| `SMALL_BUFF` | `0.1` | smallest spacing unit | `MED_SMALL_BUFF` | `0.25` | small-medium spacing unit |
| `MED_LARGE_BUFF` | `0.5` | medium-large spacing unit | `LARGE_BUFF` | `1` | large spacing unit |
| `DEFAULT_MOBJECT_TO_EDGE_BUFFER` | `0.5` (= `MED_LARGE_BUFF`) | default mobject→frame-edge padding | `DEFAULT_MOBJECT_TO_MOBJECT_BUFFER` | `0.25` (= `MED_SMALL_BUFF`) | default padding between two mobjects |
| `DEFAULT_POINTWISE_FUNCTION_RUN_TIME` | `3.0` | default duration (s) for `apply_points_function`-type animations | `DEFAULT_WAIT_TIME` | `1.0` | default `self.wait()` duration (s) |
| `DEFAULT_POINT_DENSITY_2D` | `25` | 2D curve sampling density | `DEFAULT_POINT_DENSITY_1D` | `10` | 1D curve sampling density |
| `DEFAULT_STROKE_WIDTH` | `4` | default stroke width | `DEFAULT_FONT_SIZE` | `48` | default font size |
| `SCALE_FACTOR_PER_FONT_POINT` | `1/960` | font-point → scale factor | | | |

## Render quality, renderer and misc (10)

| Constant | Value/Type | Meaning | Constant | Value/Type | Meaning |
| --- | --- | --- | --- | --- | --- |
| `QUALITIES` | `dict[str, QualityDict]` | quality table: `fourk_quality(3840×2160@60, k)`, `production_quality(2560×1440@60, p)`, `high_quality(1920×1080@60, h)`, `medium_quality(1280×720@30, m)`, `low_quality(854×480@15, l)`, `example_quality(854×480@30, no flag)` | `DEFAULT_QUALITY` | `"high_quality"` | default quality (`-ql/-qm/-qh` override) |
| `EPILOG` | `str` | end-of-render credits text | `CONTEXT_SETTINGS` | `cloup.Context.settings` | CLI param grouping/constraint display settings |
| `SHIFT_VALUE` | `65505` | keyboard Shift keycode (for keybinds) | `CTRL_VALUE` | `65507` | keyboard Ctrl keycode |
| `RESAMPLING_ALGORITHMS` | `dict` | image resize algorithm name map: `nearest/none→NEAREST`, `bilinear/linear→BILINEAR`, `bicubic/cubic→BICUBIC` | `RendererType` | `Enum` | `RendererType.CAIRO` (default 2D/vector) and `RendererType.OPENGL`; `config.renderer = "cairo"/"opengl"` converts to it |
| `LineJointType` | `Enum` | polyline joint style: `AUTO=0`, `ROUND=1`, `BEVEL=2`, `MITER=3` (used via `joint_type=`) | `CapStyleType` | `Enum` | line-cap style: `AUTO=0`, `ROUND=1`, `BUTT=2`, `SQUARE=3` (used via `cap_style=`) |

## Text weight/slant (Pango constants; pass to `Text(weight=, slant=)`) (14)

| Constant | Meaning | Constant | Meaning |
| --- | --- | --- | --- |
| `NORMAL` | normal | `BOLD` | bold |
| `ITALIC` | italic (font-native) | `THIN` | extra thin (100) |
| `OBLIQUE` | oblique | `ULTRALIGHT` | ultra light (200) |
| `MEDIUM` | medium (500) | `LIGHT` | light (300) |
| `SEMIBOLD` | semibold (600) | `SEMILIGHT` | semilight (250) |
| `ULTRABOLD` | ultrabold (800) | `BOOK` | book body weight (400) |
| `HEAVY` | heavy (900) | `ULTRAHEAVY` | ultra heavy (950) |

## CLI message constants (4)

| Constant | Meaning | Constant | Meaning |
| --- | --- | --- | --- |
| `SCENE_NOT_FOUND_MESSAGE` | `"{} is not in the script"` — scene lookup failure prompt | `CHOOSE_NUMBER_MESSAGE` | prompt when choosing a scene/param interactively |
| `INVALID_NUMBER_MESSAGE` | prompt for an invalid scene number | `NO_SCENE_MESSAGE` | prompt when the script has no scenes |

Not demonstrated: `START_X` / `DEFAULT_DOT_RADIUS` / `SMALL_BUFF` / `QUALITIES` / `EPILOG` / `SHIFT_VALUE` / `NORMAL` / `SCENE_NOT_FOUND_MESSAGE` and the other 47 pure-value or pure-text constants — all are defaults and prompts that can only be "incidentally used" on screen and cannot show a difference on their own; the values come from the same manim source and RTM reuses them bit-for-bit, so they are collected in the tables above. The visible parts of the direction and math constants are already covered by the two samples.

---

See also: [Rate Functions](02-Rate-Functions.md) | [Vector and Geometry Utilities](04-Vector-and-Geometry-Utilities.md)
