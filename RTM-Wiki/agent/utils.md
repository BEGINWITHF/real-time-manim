# utils

> scope: Colors (`ManimColor` construction/parse/from_*/to_hex/darker/lighter/invert/opacity/contrasting, `color_gradient`, `interpolate_color`/`average_color`/`random_color`/`random_bright_color`, `color_to_*`/`rgb_to_*`/`hex_to_rgb`/`get_shaded_rgb`/`HSV`/`RandomColorGenerator`, predefined palette constants); rate functions (RTM `rate_functions` module, 12 common + 5 special/factory at top level, 30 `ease_*`, decorators + `RateFunction`); direction/math/size constants (`UP`/`DOWN`/`LEFT`/`RIGHT`/`ORIGIN`/`IN`/`OUT`/`UL`…, `PI`/`TAU`/`DEGREES`, `compass_directions`); vector & geometry utilities (`space_ops`: `rotate_vector`/`angle_*`/`center_of_mass`/`regular_vertices`/`shoelace`/…); path & sequence utilities (`paths`, `iterables`, `simple_functions`).
> src: `real_time_manim/manim/utils/{color/core.py,color/manim_colors.py,rate_functions.py,space_ops.py,paths.py,iterables.py,simple_functions.py}`, `real_time_manim/manim/constants.py`, `real_time_manim/rate_functions.py`, `real_time_manim/__init__.py`; human wiki `../zh_CN/08-工具/`.
> Import: every symbol here is reachable from `real_time_manim` (top level) unless marked otherwise. RTM re-exports the whole bundled ManimCE 0.21.0 namespace, so `from manim import ...` also works (import `real_time_manim` first, see README §2). RTM does **not** have a dedicated color/geometry module — colors ride generic vector rendering; `space_ops`/`paths`/`iterables` are the bundled ManimCE implementations, bit-for-bit.

---

## 1. Colors

### `ManimColor`
```python
ManimColor(value: ParsableManimColor | None, alpha: float = 1.0)
```
- `ret`: `ManimColor` instance; internally `[r, g, b, a]` floats in 0..1 (`ManimColorDType`).
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `value` | `ParsableManimColor \| None` | required (`None` → pure black) | see accepted forms below |
| `alpha` | `float` | `1.0` | opacity 0..1; **overrides** any alpha already inside `value` (8-digit hex / 4-tuple) |

- `notes`:
  - Accepted `value` forms (`ParsableManimColor`): `ManimColor`; predefined color-name `str` (`"RED"`, `"blue_e"`, case-insensitive); hex `str` (`"#FF8800"`, `"0xFF8800"`, `"#F80"`, `"#FF880080"` — 3/4-digit auto-expanded, last 2 of 8 = alpha); `int` (`0xFF8800` = `0xRRGGBB`); int tuple/array (`(255,0,0)`, `np.array([255,0,0])` → 0..255); float tuple/array (`(1.0,0.0,0.0)`, `(1.0,0.0,0.0,0.5)` → 0..1, 4 = with alpha); any object with `get_hex()`.
  - Supports operators `+ - * / // % **`, `~color`, `int()`, `color[i]`, `==`.
  - `alpha` and a `value`-embedded alpha conflict: `ManimColor("#FF880080", alpha=0.9)` → `alpha` wins.
- `errs`:
  - `ValueError` — unknown color name (e.g. `"REDD"`).
- `see`: ../zh_CN/08-工具/01-颜色.md
- `eg`:
```python
c1 = ManimColor("#FF8800"); c2 = ManimColor((255, 0, 0))
c3 = ManimColor(0x00FF00); c4 = ManimColor("RED"); c5 = ManimColor("BLUE", alpha=0.4)
```

### `ManimColor.parse`
```python
ManimColor.parse(color: ParsableManimColor | Sequence[ParsableManimColor] | None,
                 alpha: float = 1.0) -> ManimColor | list[ManimColor]
```
- `ret`: one `ManimColor` for a single color, `list[ManimColor]` for a sequence.
- `args`: `color` — single color or sequence; `alpha: float = 1.0`.
- `notes`: **treats a tuple as a sequence** and parses element-by-element — do not pass an RGB tuple expecting one color (use `ManimColor(...)` / `from_rgb`).
- `see`: ../zh_CN/08-工具/01-颜色.md

### `ManimColor.from_rgb` / `from_rgba` / `from_hex` / `from_hsv` / `from_hsl`
```python
ManimColor.from_rgb(rgb: FloatRGBLike | IntRGBLike, alpha: float = 1.0) -> Self
ManimColor.from_rgba(rgba: FloatRGBALike | IntRGBALike) -> Self
ManimColor.from_hex(hex_str: str, alpha: float = 1.0) -> Self
ManimColor.from_hsv(hsv: FloatHSVLike, alpha: float = 1.0) -> Self
ManimColor.from_hsl(hsl: FloatHSLLike, alpha: float = 1.0) -> Self
```
- `ret`: `ManimColor`.
- `notes`:
  - `from_rgb` auto-detects int (0..255) vs float (0..1); beware `5.0` is read as float RGB.
  - `from_hsv` / `from_hsl` expect `[h, s, v]` / `[h, l, s]`, each 0..1. **RTM-tested: pass a tuple** — a `list` is misparsed as an int RGB array and yields a wrong color.
  - All five are construction shortcuts; output is bit-identical to `ManimColor(value)`.
- `see`: ../zh_CN/08-工具/01-颜色.md

### `ManimColor.to_hex`
```python
ManimColor.to_hex(with_alpha: bool = False) -> str
```
- `ret`: `str` — uppercase `"#RRGGBB"`, or `"#RRGGBBAA"` when `with_alpha=True`.
- `args`: `with_alpha: bool = False`.
- `see`: ../zh_CN/08-工具/01-颜色.md

### `ManimColor.darker` / `ManimColor.lighter`
```python
ManimColor.darker(blend: float = 0.2) -> Self
ManimColor.lighter(blend: float = 0.2) -> Self
```
- `ret`: **new** `ManimColor` (original unchanged); alpha preserved.
- `args`: `blend: float = 0.2` — `darker` interpolates toward `BLACK` (0 = unchanged, 1 = black); `lighter` toward `WHITE` (0 = unchanged, 1 = white). Values outside 0..1 are clamped (no error).
- `see`: ../zh_CN/08-工具/01-颜色.md

### `ManimColor.interpolate`
```python
ManimColor.interpolate(other: Self, alpha: float) -> Self
```
- `ret`: new `ManimColor`.
- `args`: `other: ManimColor` (any parsable); `alpha: float` required — 0 = self, 1 = other.
- `notes`: interpolates in **RGBA** — differing opacities make intermediate `alpha` shift linearly; use `opacity(...)` to pin alpha.
- `see`: ../zh_CN/08-工具/01b-颜色进阶.md

### `ManimColor.invert` / `opacity` / `contrasting`
```python
ManimColor.invert(with_alpha: bool = False) -> Self
ManimColor.opacity(opacity: float) -> Self
ManimColor.contrasting(threshold: float = 0.5, light: Self | None = None,
                       dark: Self | None = None) -> Self
```
- `ret`: new `ManimColor`.
- `args`:
  - `invert`: `with_alpha: bool = False` — per-channel linear inversion; `with_alpha=True` also inverts alpha.
  - `opacity`: `opacity: float` — replaces alpha only, keeps RGB.
  - `contrasting`: `threshold: float = 0.5` (luminance cutoff); `light: Self | None = None` (default `WHITE`); `dark: Self | None = None` (default `BLACK`) → returns `light` or `dark` per luminance (dark-bg→white text, light-bg→black text).
- `see`: ../zh_CN/08-工具/01b-颜色进阶.md
- `eg`:
```python
src = ManimColor("RED")
src.invert()               # cyan-ish complement
src.opacity(0.35)          # half-transparent red
ManimColor("#333333").contrasting()   # -> WHITE
```

### `ManimColor` other methods (quick table)
| signature | meaning |
| --- | --- |
| `to_rgb() -> FloatRGB` | 3 floats 0..1 |
| `to_int_rgb() -> IntRGB` | 3 ints 0..255 |
| `to_rgba() -> FloatRGBA` | 4 floats 0..1 (with alpha) |
| `to_int_rgba() -> IntRGBA` | 4 ints 0..255 |
| `to_rgba_with_alpha(alpha) -> FloatRGBA` | RGBA with a different alpha |
| `to_int_rgba_with_alpha(alpha) -> IntRGBA` | same, int form |
| `to_integer() -> int` | `0xRRGGBB` int (drops alpha) |
| `to_hsv() -> FloatHSV` | `[h, s, v]`, each 0..1 |
| `to_hsl() -> FloatHSL` | `[h, l, s]`, each 0..1 |
| `into(class_type) -> Self` | convert to another color-space class (e.g. `HSV`), internal value unchanged |
| `gradient(colors, length)` | **raises `NotImplementedError`** — use module-level `color_gradient` |
| `ManimColorDType` | internal float dtype (numpy-level work only) |
- `notes`: `RGBA` is an alias of `ManimColor`; `HSV([h, s, v], alpha=1.0)` has read/write attrs `hue/saturation/value` (aliases `h/s/v`).
- `see`: ../zh_CN/08-工具/01b-颜色进阶.md

### `color_gradient`
```python
color_gradient(reference_colors: Iterable[ParsableManimColor],
               length_of_output: int) -> list[ManimColor]
```
- `ret`: `list[ManimColor]` of length `length_of_output`.
- `args`: `reference_colors` — ≥1 parsable colors (single color → replicated); `length_of_output: int` — any non-negative int (`0` → empty list).
- `notes`: **module-level function**, not `ManimColor.gradient` (which raises `NotImplementedError`).
- `see`: ../zh_CN/08-工具/01-颜色.md
- `eg`:
```python
ramp = color_gradient([RED, YELLOW, BLUE], 6)
```

### `interpolate_color` / `average_color` / `random_color` / `random_bright_color`
```python
interpolate_color(color1: ManimColorT, color2: ManimColorT, alpha: float) -> ManimColorT
average_color(*colors: ParsableManimColor) -> ManimColor
random_color() -> ManimColor
random_bright_color() -> ManimColor
```
- `ret`: `ManimColor`.
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `color1` / `color2` | `ManimColor` | required | interpolation ends (any parsable) |
| `alpha` | `float` | required | 0 = `color1`, 1 = `color2` |
| `*colors` | `ParsableManimColor` | required | colors to average (≥1) |

- `notes`:
  - `interpolate_color` = function form of `c1.interpolate(c2, alpha)` (lambda-friendly).
  - `average_color` averages per channel and **ignores alpha** (result alpha 1.0).
  - `random_color()` draws from the whole Manim palette; `random_bright_color()` = half-blend with `WHITE` (**expensive** — do not call in tight loops).
  - Both random funcs use Python's global random state → different every run; set `random.seed(...)` for reproducibility.
- `see`: ../zh_CN/08-工具/01b-颜色进阶.md

### Color module other tools
| signature | meaning |
| --- | --- |
| `color_to_rgb(color) -> FloatRGB` | any parsable → 3 floats 0..1 |
| `color_to_rgba(color, alpha=1.0) -> FloatRGBA` | → 4 floats 0..1 |
| `color_to_int_rgb(color) -> IntRGB` | → 3 ints 0..255 |
| `color_to_int_rgba(color, alpha=1.0) -> IntRGBA` | → 4 ints 0..255 |
| `rgb_to_color(rgb) -> ManimColor` | 3-array → color |
| `rgba_to_color(rgba) -> ManimColor` | 4-array → color |
| `rgb_to_hex(rgb) -> str` | 3-array → `"#RRGGBB"` |
| `hex_to_rgb(hex_code) -> FloatRGB` | `"#RRGGBB"` → 3 floats |
| `invert_color(color) -> ManimColor` | function form of `color.invert()` |
| `get_shaded_rgb(rgb: FloatRGB, point: Point3D, unit_normal_vect: Vector3D, light_source: Point3D) -> FloatRGB` | surface shading by orientation vs light source (custom 3D shading) |
| `HSV` | `HSV([h, s, v], alpha=1.0)`, attrs `hue/saturation/value` (`h/s/v`) |
| `RandomColorGenerator(seed=None, sample_colors=None)` + `.next() -> ManimColor` | seedable color generator; `sample_colors` restricts the palette (controlled `random_color()`) |
- `notes`: `RGBA` is a `ManimColor` alias.
- `see`: ../zh_CN/08-工具/01b-颜色进阶.md

### Predefined color constants
- `notes`:
  - Bare hue families (each with `_A` (lightest) … `_E` (darkest); bare name = `_C`): `BLUE`, `TEAL`, `GREEN`, `YELLOW`, `GOLD`, `RED`, `MAROON`, `PURPLE`.
  - Greys: `WHITE`, `GRAY_A`/`GREY_A` (`#DDDDDD`) … `GRAY_E`/`GREY_E` (`#222222`), `BLACK`; aliases `LIGHT_GRAY`=`GRAY_B`, `GRAY`/`GREY`=`#888888`, `DARK_GRAY`=`GRAY_D`. `GRAY_*` and `GREY_*` are both valid.
  - Pure + misc: `PURE_RED` `#FF0000`, `PURE_GREEN` `#00FF00`, `PURE_BLUE` `#0000FF`, `PINK`, `LIGHT_PINK`, `ORANGE`, `LIGHT_BROWN`, `DARK_BROWN`, `GRAY_BROWN`/`GREY_BROWN`, `LOGO_*`.
  - Names are `ManimColor` instances usable anywhere a color is accepted; a string form (`"BLUE_E"`) also parses case-insensitively.
- `see`: ../zh_CN/08-工具/01-颜色.md

---

## 2. Rate functions

### RTM override — `real_time_manim.rate_functions` (read first)
- `real_time_manim/rate_functions.py` defines its own local `_`-prefixed rate funcs (`_linear`, `_smooth`, `_rush_into`, `_rush_from`, `_there_and_back`, `_slow_into`, `_double_smooth`, `_wiggle`, `_lingering`, `_exponential_decay`, `_squish_rate_func`) which **RTM's internal animations import** (`real_time_manim.animations.*`).
- The module then does `from manim.utils.rate_functions import *`, so it is a **superset**: `rate_functions.smooth`, `rate_functions.ease_out_bounce`, … all resolve.
- `real_time_manim/__init__.py` binds the name `rate_functions` to **this RTM module** (not the ManimCE module): `from real_time_manim import rate_functions` → RTM's module. `__all__` = every non-underscore name in the bundled ManimCE `rate_functions` module dict.
- Consequence: `from real_time_manim import rate_functions` is safe and gives access to all 50 names (17 + 30 `ease_*` + 3); RTM never collides with the ManimCE copy.
- Top level exports **17** rate functions (`__all__` of the ManimCE module): 12 common + 5 special/factory. The 30 `ease_*`, the 2 decorators and `RateFunction` are **not** at top level — prefix with `rate_functions.`.
- `import` all rate funcs from `real_time_manim` (top level), e.g. `from real_time_manim import linear, smooth, rush_into, there_and_back`.
- `rate_func` is a **progress→progress** map `f: [0,1] → float`; output **may exceed 0..1**. Fine for movement; do **not** drive strict-0..1 properties (`set_opacity`) with overshooting funcs (`_back`/`_elastic`/`_bounce`, `wiggle`, `there_and_back`).
- `smoothstep` / `smootherstep` / `smoothererstep` / variants and all `ease_*` go through RTM's generic per-point fallback (`use_vectorized=False`), same shape, no vectorized fast path.

### `rate_func` (the `play` / `Animation` parameter)
| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `rate_func` | `Callable[[float], float]` | `smooth` | any top-level rate func, a factory product (`squish_rate_func(smooth, 0.2, 0.8)`), or `rate_functions.ease_*` |

- `see`: ../zh_CN/08-工具/02-速率函数.md

### Common rate functions (top level, 12)
| function | shape / use |
| --- | --- |
| `linear(t)` | identity `y = t`, constant speed |
| `smooth(t, inflection=10.0)` | S-shaped sigmoid; smooth start+end — **Manim's default for most animations** |
| `smoothstep(t)` | `3t²−2t³`; zero first derivative at endpoints |
| `smootherstep(t)` | `6t⁵−15t⁴+10t³`; first+second derivative zero |
| `smoothererstep(t)` | third-order smoothstep (up to third derivative zero) |
| `there_and_back(t, inflection=10.0)` | 0→1→0, fastest at midpoint; "bounce and reset" |
| `there_and_back_with_pause(t, pause_ratio=1.0/3)` | as above, pauses at the far end |
| `exponential_decay(t, half_life=0.1)` | `1−e^(−t/0.1)`: near-instant then long tail; "fly in and settle" |
| `rush_into(t, inflection=10.0)` | slow start, hard finish |
| `rush_from(t, inflection=10.0)` | hard start, gentle finish |
| `slow_into(t)` | `sqrt(1−(1−t)²)`: full-speed start decaying to 0 (no ease-in) |
| `double_smooth(t)` | two half-`smooth`s; brief pause near midpoint |

- `see`: ../zh_CN/08-工具/02-速率函数.md

### Special-purpose & factory functions (top level, 5)
```python
running_start(t: float, pull_factor: float = -0.5) -> float
not_quite_there(func: RateFunction = smooth, proportion: float = 0.7) -> RateFunction
wiggle(t: float, wiggles: float = 2) -> float
squish_rate_func(func: RateFunction, a: float = 0.4, b: float = 0.6) -> RateFunction
lingering(t: float) -> float
```
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `pull_factor` | `float` | `-0.5` | `running_start`: backward pull before rushing forward |
| `func` | `RateFunction` | `smooth` (for `not_quite_there`) | wrapped function |
| `proportion` | `float` | `0.7` | `not_quite_there`: only reaches `proportion × func(t)` |
| `wiggles` | `float` | `2` | `wiggle`: number of oscillations between 0 and 1 |
| `a` / `b` | `float` | `0.4` / `0.6` | `squish_rate_func`: time interval `[a, b]`; before → 0, after → 1 |

- `notes`:
  - `not_quite_there` and `squish_rate_func` are **factories** — you must call them (`squish_rate_func(smooth, 0.2, 0.8)` returns a new function). Passing the factory itself (`rate_func=squish_rate_func`) blows up at runtime.
  - `lingering` is linear over `[0, 0.8]`, then holds still for the last 20%.
  - `wiggle` = `there_and_back × sin(wiggles·π·t)`; wrapped in `@zero` → output is 0 outside `[0,1]`.
- `errs`:
  - runtime `TypeError`/`ValueError` — factory passed uncalled as `rate_func`.
- `see`: ../zh_CN/08-工具/02-速率函数.md

### Standard easings `rate_functions.ease_*` (30)
- `notes`:
  - 10 families × 3 (`_in` / `_out` / `_in_out`): `sine`, `quad`, `cubic`, `quart`, `quint`, `expo`, `circ`, `back`, `elastic`, `bounce`. **All must be prefixed** `rate_functions.ease_out_bounce`.
  - `_back`, `_elastic`, `_bounce` overshoot `[0,1]` — fine for movement, avoid for strict-0..1 properties.
- `eg`:
```python
from real_time_manim import rate_functions
win.play(dot.animate(rate_func=rate_functions.ease_out_bounce).shift(RIGHT))
```
- `see`: ../zh_CN/08-工具/02-速率函数.md

### Decorators & protocol (not top-level, 3)
| name | kind | meaning |
| --- | --- | --- |
| `unit_interval(func)` | decorator | `t<0 → 0`, `t>1 → 1`, otherwise `func(t)`; applied to all "normal progress" rate funcs |
| `zero(func)` | decorator | returns 0 outside `[0,1]`; used by `there_and_back`/`wiggle` for "reset at end" |
| `RateFunction` | `Protocol` | typing only: `def __call__(self, t: float, *args, **kwargs) -> float` |
- `notes`: prefix with `rate_functions.`; not built into RTM (generic fallback).
- `see`: ../zh_CN/08-工具/02-速率函数.md

---

## 3. Directions & constants

### Direction / axis vectors (14)
| constant | value | meaning |
| --- | --- | --- |
| `ORIGIN` | `[0, 0, 0]` | origin |
| `UP` | `[0, 1, 0]` | +Y |
| `DOWN` | `[0, -1, 0]` | −Y |
| `RIGHT` | `[1, 0, 0]` | +X |
| `LEFT` | `[-1, 0, 0]` | −X |
| `IN` | `[0, 0, -1]` | −Z (into the screen) |
| `OUT` | `[0, 0, 1]` | +Z (out of the screen; 3D default axis) |
| `X_AXIS` | `[1, 0, 0]` | X basis |
| `Y_AXIS` | `[0, 1, 0]` | Y basis |
| `Z_AXIS` | `[0, 0, 1]` | Z basis |
| `UL` | `UP + LEFT` = `[-1, 1, 0]` | upper-left diagonal |
| `UR` | `UP + RIGHT` = `[1, 1, 0]` | upper-right diagonal |
| `DL` | `DOWN + LEFT` = `[-1, -1, 0]` | lower-left diagonal |
| `DR` | `DOWN + RIGHT` = `[1, -1, 0]` | lower-right diagonal |

- `notes`:
  - All are `numpy.ndarray`; add/multiply freely (`2 * UP + 3 * RIGHT`).
  - No aliases other than `IN`/`OUT`; diagonals can be written `UP + RIGHT` directly (`UR` is the ready-made alias).
  - `DR` value is taken from source (`DOWN + RIGHT` = `[1, -1, 0]`); the zh_CN 03 table prints `[1, 1, 0]` — **source wins**.
- `see`: ../zh_CN/08-工具/03-方向与常量.md

### Math constants `PI` / `TAU` / `DEGREES`
| constant | value | meaning |
| --- | --- | --- |
| `PI` | `3.14159265…` | π |
| `TAU` | `2 * PI = 6.28318530…` | full turn in radians |
| `DEGREES` | `TAU / 360 = 0.01745329…` | degree→radian factor: `30 * DEGREES` |
- `notes`: `Arc(angle=...)` etc. take **radians** — write `45 * DEGREES`, not `45`.
- `see`: ../zh_CN/08-工具/03-方向与常量.md

### `compass_directions`
```python
compass_directions(n: int = 4, start_vect: np.ndarray = RIGHT) -> np.ndarray
```
- `ret`: `np.ndarray` of `n` unit direction vectors evenly spaced by `TAU / n`; `result[0]` is `start_vect`.
- `args`: `n: int = 4` (count); `start_vect: np.ndarray = RIGHT` (first direction).
- `notes`:
  - Returns **unit direction vectors**, not points — multiply by a radius and add a center to place dots (`1.6 * p + c`).
  - **Discrepancy:** zh_CN 03 documents `compass_directions(n, start_vect=RIGHT, clockwise=False)`; source (and zh_CN 04) has **no `clockwise` parameter**. To rotate the other way, pass a different `start_vect` or negate the angle yourself.
- `see`: ../zh_CN/08-工具/03-方向与常量.md · ../zh_CN/08-工具/04-向量与几何工具.md
- `eg`:
```python
pts = compass_directions(8, start_vect=RIGHT)   # 8 evenly spaced unit vectors
```

### Sizes, buffers, timing (19)
| constant | value | meaning |
| --- | --- | --- |
| `START_X` | `30` | initial canvas width (px, internal) |
| `START_Y` | `20` | initial canvas height (px, internal) |
| `DEFAULT_DOT_RADIUS` | `0.08` | default `Dot`/`Dot3D` radius |
| `DEFAULT_SMALL_DOT_RADIUS` | `0.04` | smaller default dot radius |
| `DEFAULT_DASH_LENGTH` | `0.05` | `DashedLine` default segment length |
| `DEFAULT_ARROW_TIP_LENGTH` | `0.35` | default arrow-tip length |
| `SMALL_BUFF` | `0.1` | smallest spacing unit |
| `MED_SMALL_BUFF` | `0.25` | small-medium spacing |
| `MED_LARGE_BUFF` | `0.5` | medium-large spacing |
| `LARGE_BUFF` | `1` | large spacing |
| `DEFAULT_MOBJECT_TO_EDGE_BUFFER` | `MED_LARGE_BUFF` (`0.5`) | default mobject→frame-edge padding |
| `DEFAULT_MOBJECT_TO_MOBJECT_BUFFER` | `MED_SMALL_BUFF` (`0.25`) | default mobject→mobject padding |
| `DEFAULT_POINTWISE_FUNCTION_RUN_TIME` | `3.0` | default duration (s) for `apply_points_function`-type animations |
| `DEFAULT_WAIT_TIME` | `1.0` | default `self.wait()` duration (s) |
| `DEFAULT_POINT_DENSITY_2D` | `25` | 2D curve sampling density |
| `DEFAULT_POINT_DENSITY_1D` | `10` | 1D curve sampling density |
| `DEFAULT_STROKE_WIDTH` | `4` | default stroke width |
| `DEFAULT_FONT_SIZE` | `48` | default font size |
| `SCALE_FACTOR_PER_FONT_POINT` | `1/960` | font-point → scale factor |

### Renderer / misc constants (10)
| constant | value/type | meaning |
| --- | --- | --- |
| `QUALITIES` | `dict[str, QualityDict]` | `fourk_quality`(3840×2160@60,`k`), `production_quality`(2560×1440@60,`p`), `high_quality`(1920×1080@60,`h`), `medium_quality`(1280×720@30,`m`), `low_quality`(854×480@15,`l`), `example_quality`(854×480@30, no flag) |
| `DEFAULT_QUALITY` | `"high_quality"` | default quality (`-ql/-qm/-qh` override) |
| `EPILOG` | `str` | end-of-render credits text |
| `CONTEXT_SETTINGS` | `cloup.Context.settings` | CLI param grouping/constraint display |
| `SHIFT_VALUE` | `65505` | Shift keycode (keybind) |
| `CTRL_VALUE` | `65507` | Ctrl keycode |
| `RESAMPLING_ALGORITHMS` | `dict` | image resize map: `nearest/none→NEAREST`, `bilinear/linear→BILINEAR`, `bicubic/cubic→BICUBIC` |
| `RendererType` | `Enum` | `RendererType.CAIRO` (default 2D/vector), `RendererType.OPENGL`; `config.renderer = "cairo"/"opengl"` converts to it |
| `LineJointType` | `Enum` | line-joint style: `AUTO=0`, `ROUND=1`, `BEVEL=2`, `MITER=3` (used by `joint_type=`) |
| `CapStyleType` | `Enum` | line-cap style: `AUTO=0`, `ROUND=1`, `BUTT=2`, `SQUARE=3` (used by `cap_style=`) |

### Text weight/slant (Pango; pass to `Text(weight=, slant=)`) (14)
| constant | meaning | constant | meaning |
| --- | --- | --- | --- |
| `NORMAL` | normal | `BOLD` | bold |
| `ITALIC` | italic (font-native) | `THIN` | 100 |
| `OBLIQUE` | oblique | `ULTRALIGHT` | 200 |
| `MEDIUM` | 500 | `LIGHT` | 300 |
| `SEMIBOLD` | 600 | `SEMILIGHT` | 250 |
| `ULTRABOLD` | 800 | `BOOK` | 400 |
| `HEAVY` | 900 | `ULTRAHEAVY` | 950 |

### CLI message constants (4)
| constant | meaning |
| --- | --- |
| `SCENE_NOT_FOUND_MESSAGE` | `"{} is not in the script"` — scene lookup failure |
| `CHOOSE_NUMBER_MESSAGE` | prompt when choosing a scene/param interactively |
| `INVALID_NUMBER_MESSAGE` | prompt for an invalid scene number |
| `NO_SCENE_MESSAGE` | prompt when the script has no scenes |
- `notes`: these 4 (and `START_X`, `DEFAULT_*`, `QUALITIES`, `EPILOG`, `SHIFT_VALUE`, `NORMAL`, … 47 names total) are pure values/text — no independent visual; RTM reuses the same manim source bit-for-bit.
- `see`: ../zh_CN/08-工具/03-方向与常量.md

---

## 4. Vector & geometry utilities (`space_ops`)

### Naming traps (do not call these — they do not exist)
| not in this version (0.21.0) | correct form |
| --- | --- |
| `rotation_between_vectors(v1, v2)` | `rotation_matrix(angle_between_vectors(v1, v2), np.cross(v1, v2))` |
| `angle_between(v1, v2)` | `angle_between_vectors(v1, v2)` |
| `get_unit_vector(v)` | `normalize(v)`; `Line.get_unit_vector()` is a 2D `Line` method |
| `complex_to_vec3(z)` | `complex_to_R3(z)` |

### `rotate_vector`
```python
rotate_vector(vector: Vector3DLike, angle: float, axis: Vector3DLike = OUT) -> Vector3D
```
- `ret`: `Vector3D` (`np.ndarray`), a **new** vector (input unchanged).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `vector` | `Vector3DLike` | required | vector to rotate (2D auto-padded z=0; >3 dims raises) |
| `angle` | `float` | required | rotation angle in **radians**, CCW positive |
| `axis` | `Vector3DLike` | `OUT` | rotation axis |

- `notes`: `angle` is radians (`45°` = `PI/4` or `45 * DEGREES`); use `rotation_matrix(angle, axis)` for the matrix form.
- `errs`:
  - `ValueError: "Vector must have the correct dimensions."` — `vector` has more than 3 components.
- `see`: ../zh_CN/08-工具/04-向量与几何工具.md
- `eg`:
```python
v45 = rotate_vector(RIGHT, PI / 4)      # axis defaults to OUT
v90 = rotate_vector(RIGHT, PI / 2)      # == UP
```

### `angle_between_vectors` / `angle_of_vector` / `center_of_mass` / `midpoint`
```python
angle_between_vectors(v1: np.ndarray, v2: np.ndarray) -> float
angle_of_vector(vector: Sequence[float] | np.ndarray) -> float
center_of_mass(points: PointNDLike_Array) -> PointND
midpoint(point1: PointNDLike, point2: PointNDLike) -> PointND
```
- `ret`:
  - `angle_between_vectors` → `float` in `[0, π]` (arctan2 half-angle, numerically stable).
  - `angle_of_vector` → polar angle of the xy-projected vector via `atan2`, in `(-π, π]`; also accepts a `(2, n)` point set and returns per-point angles.
  - `center_of_mass` → arithmetic mean of the points (equal-weight centroid).
  - `midpoint` → midpoint of two points (`center_of_mass([p1, p2])` sugar).
- `notes`: all take **numpy arrays** — call `.get_end()` first for mobjects like `Vector`; `angle_of_vector` ignores z (use `angle_between_vectors` for 3D).
- `see`: ../zh_CN/08-工具/04-向量与几何工具.md
- `eg`:
```python
ang = angle_between_vectors(a.get_end(), b.get_end())   # in [0, PI]
com = center_of_mass(pts)                               # polygon centroid (vertices)
mid = midpoint(pts[0], pts[1])
```

### `regular_vertices` / `shoelace` / `shoelace_direction`
```python
regular_vertices(n: int, *, radius: float = 1,
                 start_angle: float | None = None) -> tuple[np.ndarray, float]
shoelace(x_y: Point2D_Array) -> float
shoelace_direction(x_y: Point2D_Array) -> str
```
- `ret`:
  - `regular_vertices` → `(vertices, start_angle)`; `vertices` is the `n` evenly spaced points on a radius-`radius` circle.
  - `shoelace` → signed area (`np.trapezoid(y, x)`).
  - `shoelace_direction` → `"CW"` or `"CCW"` (upstream convention: positive area → `"CW"`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `n` | `int` | required | number of vertices |
| `radius` | `float` | `1` | circle radius (keyword-only) |
| `start_angle` | `float \| None` | `None` | start angle; `None` → 0 for even `n`, 90° for odd `n` |

- `notes`:
  - `shoelace` needs an `np.array` and does **not** auto-close the polygon — append the first point again (`np.array(list(verts) + [verts[0]])`), otherwise the last edge is missing.
  - `shoelace_direction` only inspects the sign; closed or open input gives the same direction.
  - Area absolute value = polygon size; sign = winding direction.
- `errs`:
  - `TypeError` — `shoelace` given a plain Python `list` instead of `np.array`.
- `see`: ../zh_CN/08-工具/04-向量与几何工具.md
- `eg`:
```python
verts, sa = regular_vertices(5, radius=1.4, start_angle=PI / 2)
area = shoelace(np.array(list(verts) + [verts[0]]))   # -4.660
dirn = shoelace_direction(np.array(verts))            # "CCW"
```

### Other `space_ops` functions (quick table)
| signature | meaning |
| --- | --- |
| `rotation_matrix(angle: float, axis: Vector3DLike, homogeneous: bool = False) -> np.ndarray` | 3×3 rotation matrix (scipy `Rotation.from_rotvec`); `homogeneous=True` → 4×4; `axis` normalized |
| `z_to_vector(vector: np.ndarray) -> np.ndarray` | SO(3) `M` with `M @ [0,0,1] = normalize(vector)` (orients Z-default faces/cones; used by `Cube.generate_points`) |
| `normalize(vect, fall_back: np.ndarray \| None = None) -> np.ndarray` | unit vector; zero vector → `fall_back` (default all-zero) |
| `complex_to_R3(complex_num: complex) -> np.ndarray` | complex → 3D point: `complex_to_R3(1+1j)` → `[1, 1, 0]` |
| `R3_to_complex(point: Sequence[float]) -> np.ndarray` | 3D point → complex (first two components) |
| `complex_func_to_R3_func(complex_func) -> Callable` | wrap a complex function for `ParametricFunction`/`Surface` |
| `norm_squared(v) -> float` | squared length |
| `cross(v1, v2) -> Vector3D` | 3D cross product |
| `rotation_about_z(angle) -> np.ndarray` | 3×3 rotation about Z |
| `rotation_matrix_transpose(angle, axis) -> np.ndarray` | transpose (inverse) rotation matrix |
| `rotation_matrix_from_quaternion(quat) -> np.ndarray` | quaternion → rotation matrix |
| `rotation_matrix_transpose_from_quaternion(quat) -> list[np.ndarray]` | quaternion → transposed rotation matrix |
| `normalize_along_axis(array, axis) -> np.ndarray` | in-place normalization along an axis |
| `quaternion_mult(*quats)` | Hamilton product; no args → identity `[1,0,0,0]` |
| `quaternion_from_angle_axis(angle, axis, axis_normalized=False)` | angle+axis → quaternion |
| `angle_axis_from_quaternion(quaternion)` | quaternion → `(angle, axis)` |
| `quaternion_conjugate(quaternion)` | quaternion conjugate (negate imaginary part) |
| `get_unit_normal(v1, v2, tol=1e-6) -> Vector3D` | unit normal of the plane of two vectors; degenerate → `DOWN` |
| `line_intersection(line1, line2) -> np.ndarray` | intersection of two **xy-plane** lines (each by two points); parallel or z≠0 raises |
| `find_intersection(p0s, v0s, p1s, v1s, threshold=1e-5) -> list[Point3D]` | closest points of two space lines/rays; batch-array capable |
| `perpendicular_bisector(line, norm_vector=OUT) -> Sequence[np.ndarray]` | two endpoints of a perpendicular bisector of a 2-point line |
| `cartesian_to_spherical(vec) -> np.ndarray` | `[x,y,z]` → `[r, theta, phi]` |
| `spherical_to_cartesian(spherical) -> np.ndarray` | `[r, theta, phi]` → `[x,y,z]` |
| `get_winding_number(points) -> float` | winding number about the origin (1 = contains origin) |
| `cross2d(a, b)` | 2D cross/determinant; supports `(n,2)` batches |
| `thick_diagonal(dim, thickness=2) -> MatrixMN` | banded 0/1 matrix (1 near the diagonal) |
| `earclip_triangulation(verts, ring_ends) -> list` | ear-clip triangulation indices (internal; fills/meshes) |
- `notes`: these output numbers/arrays only — no standalone visual; visualization equals the rotate/angle samples.
- `see`: ../zh_CN/08-工具/04-向量与几何工具.md

---

## 5. Path & sequence utilities

### `path_along_arc`
```python
path_along_arc(arc_angle: float, axis: Vector3DLike = OUT) -> PathFuncType
```
- `ret`: `PathFuncType` with signature `(start_points, end_points, alpha) -> points`; pass to `Transform(..., path_func=...)`.
- `args`: `arc_angle: float` — radians each point rotates around `axis` (may be negative); `axis: Vector3DLike = OUT`.
- `notes`:
  - The arc turns about the midpoint of start—end; `±π` gives a semicircle with the chord as diameter, "bulge" = half the chord length (leave room in frame).
  - `|arc_angle| < 0.01` auto-degenerates to a straight path.
  - `arc_angle=TAU/2` = half turn, `-TAU/2` = reverse.
- `see`: ../zh_CN/08-工具/04b-路径与序列工具.md
- `eg`:
```python
win.play(Transform(dot, target, path_func=path_along_arc(TAU / 2), run_time=1.6))
```

### Other path functions (`utils/paths.py`)
| signature | meaning |
| --- | --- |
| `straight_path() -> PathFuncType` | straight path (`Transform` default) |
| `clockwise_path() -> PathFuncType` | clockwise half-circle (= `path_along_arc(-π)`) |
| `counterclockwise_path() -> PathFuncType` | counterclockwise half-circle (= `path_along_arc(π)`) |
| `path_along_circles(arc_angle, circles_centers, axis=OUT)` | each point circles its **own** center (**not top-level**; `real_time_manim.manim.utils.paths.path_along_circles`) |
| `spiral_path(angle, axis=OUT)` | spiral converging to the endpoint (**not top-level**; `real_time_manim.manim.utils.paths.spiral_path`) |
| `STRAIGHT_PATH_THRESHOLD = 0.01` | angles below this auto-degenerate to a straight path (**not top-level**) |
- `notes`:
  - `path_along_line` **does not exist** in RTM / ManimCE 0.21.0 — use `straight_path()` or a plain `Transform` (no `path_func`).
  - Path funcs hook into `Transform`; RTM reuses ManimCE's `path_func` handling bit-for-bit.
- `see`: ../zh_CN/08-工具/04b-路径与序列工具.md

### `iterables` — sequence helpers
- `notes`: entries marked ⚙ need `from real_time_manim.manim.utils.iterables import ...` (deep path; RTM aliases resolve to the same bundled module). The rest are `from real_time_manim import ...`.

| signature | meaning |
| --- | --- |
| `listify(obj) -> list` | smart to-list: `str → [str]`, iterable → `list(...)`, else `[obj]` |
| `tuplify(obj) -> tuple` | same, to tuple |
| `adjacent_pairs(objects)` | circular adjacent pairs: `[1,2,3,4] → (1,2),(2,3),(3,4),(4,1)` |
| `adjacent_n_tuples(objects, n)` | circular tuples of length `n` (generalization of `adjacent_pairs`) |
| `remove_nones(sequence) -> list` | drop all falsy elements (`None`, `""`, `0`, `False`, …) |
| `list_update(l1, l2) -> list` | dedup-merge, **preserving l2 order** |
| `list_difference_update(l1, l2) -> list` | elements of `l1` not in `l2` |
| `concatenate_lists(*list_of_lists) -> list` | flatten several lists into one |
| `remove_list_redundancies(lst) -> list` | dedup keeping **last** occurrence (ordered by last position); replaces `list(set(...))` |
| `make_even(i1, i2) -> tuple[list, list]` | pad the shorter by **repeating earlier elements** |
| `make_even_by_cycling(i1, i2) -> tuple[list, list]` | same, padded by **cycling** |
| `all_elements_are_instances(iterable, Class) -> bool` | all elements of a type? |
| `stretch_array_to_length(nparray, length)` | index-resample an array to a target length |
| ⚙ `batch_by_property(items, property_func)` | split a sequence into contiguous same-property batches |
| ⚙ `resize_array(nparray, length)` | cyclic pad/truncate to a length |
| ⚙ `resize_preserving_order(nparray, length)` | resize by duplicating elements (order-preserving) |
| ⚙ `resize_with_interpolation(nparray, length)` | resize by linear interpolation |
| ⚙ `uniq_chain(*args)` | generator yielding all deduped elements in given order |
| ⚙ `hash_obj(obj) -> int` | hash for mutable containers (dict/set/list) |

- `notes`:
  - `adjacent_pairs` returns a **zip iterator**, not a list — wrap in `list(...)` to re-iterate or take `len`.
  - `remove_list_redundancies([1,2,1,3,2])` → `[1,3,2]` (keeps last occurrence), **not** `[1,2,3]`; for first-occurrence order use `dict.fromkeys`.
- `see`: ../zh_CN/08-工具/04b-路径与序列工具.md
- `eg`:
```python
edges = [Line(a, b) for a, b in adjacent_pairs(pts)]   # closed loop: last pair returns to start
```

### `simple_functions` — math helpers
| signature | meaning |
| --- | --- |
| `sigmoid(x) -> float` | logistic `1/(1+e^-x)`; `ArrowVectorField` default `length_func`; `sigmoid(0) = 0.500` |
| `clip(a, min_a, max_a)` | clamp `a` to `[min_a, max_a]`; works on any comparable objects; `clip(3.7, 0, 1) = 1.0` |
| `choose(n, k) -> int` | binomial `C(n,k)` (with `lru_cache`); `choose(5, 2) = 10` |
| `binary_search(function, target, lower_bound, upper_bound, tolerance=1e-4) -> float \| None` | numeric bisection for `function(x) == target`; `None` if not found |
- `notes`: `binary_search` signature is verbatim from source; the rest are pure data functions (no independent visual).
- `see`: ../zh_CN/08-工具/04b-路径与序列工具.md
- `eg`:
```python
from real_time_manim import adjacent_pairs, choose, clip, sigmoid
print(choose(5, 2), clip(3.7, 0, 1), sigmoid(0))   # 10 1.0 0.5
```
