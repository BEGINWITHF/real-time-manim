# text, math & tabular

> scope: `Text`/`MarkupText`/`Paragraph`/`register_font`; `Tex`/`MathTex`/`SingleStringMathTex` + fragment & list APIs; Typst (`Typst`/`TypstMath`/`MathTypst` + LaTeX→Typst auto-route); `Code`; numbers (`DecimalNumber`/`Integer`/`Variable`/`TextDecimalNumber`); matrices (`Matrix`/`DecimalMatrix`/`IntegerMatrix`/`MobjectMatrix` + helpers); tables (`Table`/`MathTable`/`MobjectTable`/`IntegerTable`/`DecimalTable` + cell methods); images/SVG (`ImageMobject`/`ImageMobjectFromCamera`/`AbstractImageMobject`/`SVGMobject`/`VMobjectFromSVGPath`); braces (`Brace`/`BraceText`/`BraceLabel`/`BraceBetweenPoints`/`ArcBrace`).
> src: ../zh_CN/04-图形与文本/{08-文本Text,09-LaTeX公式,09b-片段方法与列表,10-Typst,11-代码块,12-数字与变量,13-矩阵,14-表格,14b-表格方法,15-图片与SVG,16-花括号标注}.md

Cross-cutting: signatures below are verbatim from zh_CN unless marked "src". `48` == `DEFAULT_FONT_SIZE`. All classes construct via `__init__`; no factory CLI.

---

## Text

### `Text`
```python
def __init__(self, text: str, fill_opacity: float = 1, stroke_width: float = 0, color: ParsableManimColor | None = None, font_size: float = 48, line_spacing: float = -1, font: str = "", slant: str = "NORMAL", weight: str = "NORMAL", t2c: dict | None = None, t2f: dict | None = None, t2w: dict | None = None, t2s: dict | None = None, disable_ligatures: bool = False, **kwargs) -> None:
```
- `ret`: `Text` (subclass of `SVGMobject`; glyph leaves are `VMobjectFromSVGPath`).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `text` | `str` | required | content; `\n` = newline within one paragraph |
| `font` | `str` | `""` (default family) | font family name; eg `"Arial"` |
| `font_size` | `float` | `48` | font size |
| `weight` | `str` | `"NORMAL"` | eg `"BOLD"` |
| `slant` | `str` | `"NORMAL"` | eg `"ITALIC"` |
| `color` | `ManimColor \| None` | `None` | whole-string color |
| `line_spacing` | `float` | `-1` (auto) | line spacing; positive = multiplier |
| `t2c` | `dict \| None` | `None` | substring→color, eg `{"red": RED}` |
| `t2f`/`t2w`/`t2s` | `dict \| None` | `None` | substring→font / weight / slant |
| `fill_opacity`/`stroke_width` | `float` | `1` / `0` | fill & stroke |

- `notes`:
  - `t2c`/`t2f`/`t2w`/`t2s` keys are **substrings**, matched in order of appearance.
  - Source signature (RTM, `manim/mobject/text/text_mobject.py`) additionally accepts `t2g`, `gradient`, `tab_width=4`, `warn_missing_font=True`, `height`, `width`, `should_center=True`, `use_svg_cache=False` (not documented in zh_CN).
- `errs`:
  - `ImportError` on `from real_time_manim import remove_invisible_chars` — RTM does **not** export it; filter invisible chars yourself.
- `see`: ../zh_CN/04-图形与文本/08-文本Text.md
- `eg`:
```python
Text("Hello RTM")
Text("first line\nsecond line", font_size=34, color=TEAL, line_spacing=1.2)
Text("red green blue", t2c={"red": RED, "green": GREEN, "blue": BLUE})
```

### `Text.from_string`
- `notes`: **TODO / absent** — no `from_string` classmethod/method exists in the RTM source tree or zh_CN (grep: 0 matches). Do not use. To build text from a string use `Text(...)` directly.
- `see`: ../zh_CN/04-图形与文本/08-文本Text.md

### `MarkupText`
```python
def __init__(self, text: str, fill_opacity: float = 1, stroke_width: float = 0, color: ParsableManimColor | None = None, font_size: float = 48, line_spacing: float = -1, font: str = "", slant: str = "NORMAL", weight: str = "NORMAL", justify: str = "left", indent: float = 0, **kwargs) -> None:
```
- `ret`: `MarkupText` (subclass of `SVGMobject`).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `text` | `str` | required | Pango markup (only `<b>`/`<i>` verified) |
| `font_size` | `float` | `48` | font size |
| `color` | `ManimColor \| None` | `None` | whole-string color |
| `line_spacing` | `float` | `-1` | line spacing |
| `font`/`weight`/`slant` | `str` | default / `NORMAL` | same as `Text` |
| `justify` | `str` | `"left"` | multi-line alignment: `left`/`center`/`right` |
| `indent` | `float` | `0` | first-line indent |

- `notes`:
  - Markup parse path is Pango→SVG; attributes like `<span foreground=…>` **fail to parse** (see errs).
- `errs`:
  - `ElementTree.ParseError: no element found` — using `<span foreground=…>`-style attributes → give the whole string a `color`, or use `Text` with `t2c`.
- `see`: ../zh_CN/04-图形与文本/08-文本Text.md

### `Paragraph`
```python
def __init__(self, *text: str, line_spacing: float = -1, alignment: str | None = None, **kwargs) -> None:
```
- `ret`: `Paragraph` (`VGroup` of `MarkupText`).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `*text` | `str...` | required | each positional arg = one paragraph |
| `line_spacing` | `float` | `-1` | paragraph spacing (eg `0.6`) |
| `alignment` | `str \| None` | `None` | block alignment: `left`/`center`/`right` |
| `**kwargs` | `Any` | — | forwarded to text (`font_size`/`color`/`font`) |

- `notes`:
  - `alignment` aligns the **whole block**, not each paragraph. Separate paragraphs with `line_spacing`, not `\n` (`\n` becomes a newline inside one paragraph).
- `see`: ../zh_CN/04-图形与文本/08-文本Text.md

### `register_font`
```python
@contextmanager
def register_font(font_file: str | Path) -> Iterator[None]:
```
- `ret`: context manager (`with` block).
- `args`:
  - `font_file: str | Path` — font file path (eg `C:\Windows\Fonts\arial.ttf`).
- `notes`:
  - Registers by the **family name inside the font file** (not the filename). `Text(..., font="Arial")` inside the `with` block resolves it.
  - Search order (src): absolute path → `assets/fonts` → `fonts/` → same directory.
  - The `with` block only controls registration timing; the mapping is cached for the process, so the same family name keeps working after the block. A new process must re-register.
- `see`: ../zh_CN/04-图形与文本/08-文本Text.md
- `eg`:
```python
with register_font(r"C:\Windows\Fonts\arial.ttf"):
    t = Text("Registered: Arial", font="Arial", font_size=44)
```

---

## LaTeX

### `Tex`
```python
def __init__(self, *tex_strings: str, font_size: float = 48, color: ParsableManimColor | None = None, tex_environment: str = "document", **kwargs) -> None:
```
- `ret`: `Tex`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `*tex_strings` | `str...` | required | body+math mixed; math inside `$...$` |
| `font_size` | `float` | `48` | font size |
| `color` | `ManimColor \| None` | `None` | whole-string color (body + math) |
| `tex_environment` | `str` | `"document"` | outer LaTeX environment (eg `"align*"`) |

- `notes`:
  - **RTM deviation**: `Tex` is **excluded** from the Typst auto-route (`isinstance(self, _OrigTex)` check in `window/mathtex.py`). `Tex` always goes through the LaTeX toolchain; a usable LaTeX distribution is required.
  - Do **not** use `\\` manual line breaks under `tex_environment="document"` (compile failure); split into multiple `Tex` or use `align*`/`gather*`.
- `see`: ../zh_CN/04-图形与文本/09-LaTeX公式.md

### `MathTex`
```python
def __init__(self, *tex_strings: str, font_size: float = 48, color: ParsableManimColor | None = None, **kwargs) -> None:
```
- `ret`: `MathTex` (a `VGroup` of `MathTexPart`).
- `args`:
  - `*tex_strings: str...` — each positional arg is one part; `{{ }}` splits one part further.
  - `font_size: float = 48` — font size.
  - `color: ManimColor | None = None` — whole color.
  - `tex_to_color_map: dict[str, color]` — accepted as a constructor kwarg (equivalent to `set_color_by_tex_to_color_map`).
- `notes`:
  - **RTM deviation — Typst auto-route**: `MathTex.__init__` is monkey-patched (`window/mathtex.py`). Unless `self` is a `Tex`, if `RTM_TYPST != "0"` and every segment is inside the Typst-convertible subset (`typst_support.latex_to_typst_math` returns non-None), the formula is rendered by the in-process Typst backend — **no LaTeX needed**. Otherwise it silently falls back to the real LaTeX path. Compile errors inside Typst also fall back to LaTeX.
  - **RTM deviation — native layout**: an optional path `_USE_NATIVE_MATHTEX = True` (`window/mathtex.py`) bypasses LaTeX entirely and renders simple math via `Text`, laying out super/subscripts manually (`_layout_math_parts`). It is **off by default** because it renders many commands literally (`\frac`, `\sqrt`, `\mathbb`, matrices, accents).
  - No `$` inside `MathTex` (already math mode). A single string's `{{ }}` only splits the first part; write parts as **separate args** to index/color them.
  - Env vars: `RTM_TYPST=0` disables the Typst layer; `RTM_TYPST_DEBUG=1` prints routing reasons.
  - Fragment API (`set_color_by_tex` / `get_part_by_tex` / `set_opacity_by_tex` / `tex_to_color_map`) works on both the Typst and LaTeX paths.
  - **First render blocks the caller**: the compile is synchronous in `__init__` (~1–2 s LaTeX / ~0.4 s Typst cold). With a **visible** window RTM shows a "compiling formula" popup so it is not mistaken for a freeze (`runtime.md` → *Compile-wait popup*); the output is unaffected, and a cache hit (~30 ms) shows nothing. `RTM_WAIT_POPUP=0` disables it.
- `see`: ../zh_CN/04-图形与文本/09-LaTeX公式.md
- `eg`:
```python
MathTex(r"x^2 + y^2 = z^2")
MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2")
```

### `SingleStringMathTex`
```python
def __init__(self, tex_string: str, font_size: float = 48, color: ParsableManimColor | None = None, **kwargs) -> None:
```
- `ret`: `SingleStringMathTex`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `tex_string` | `str` | required | one string, **not** split into parts |
| `font_size` | `float` | `48` | font size |
| `color` | `ManimColor \| None` | `None` | whole color |

- `notes`:
  - Lightest of the three (single glyph-leaf layer). It is the glyph leaf class used by `Text`/`MathTex`. Only one part → cannot index fragments; use `MathTex` with explicit parts to color by item.
- `see`: ../zh_CN/04-图形与文本/09-LaTeX公式.md

### `MathTex.set_color_by_tex`
```python
def set_color_by_tex(self, tex: str, color: ParsableManimColor, **kwargs) -> Self:
```
- `ret`: `Self` (in-place, chainable).
- `args`:
  - `tex: str` — must **exactly equal** the part's `tex_string` (eg `"x"`); no substring/fuzzy match.
  - `color: ManimColor` — target color.
- `notes`:
  - Changes color only, not geometry, so `get_part_by_tex` lookups are unaffected. Same part can be recolored differently across formulas; repeated calls overwrite.
- `see`: ../zh_CN/04-图形与文本/09b-片段方法与列表.md

### `MathTex.set_color_by_tex_to_color_map`
```python
def set_color_by_tex_to_color_map(self, texs_to_color_map: dict[str, ParsableManimColor], **kwargs) -> Self:
```
- `ret`: `Self`.
- `args`:
  - `texs_to_color_map: dict[str, color]` — part→color; equivalent to repeated `set_color_by_tex`. Also writable as constructor kwarg `MathTex(..., tex_to_color_map={...})`.
- `notes`:
  - Keys present in the dict but absent from the formula are **silently ignored** (no error) — a typo will not crash but will not color.
- `see`: ../zh_CN/04-图形与文本/09b-片段方法与列表.md

### `MathTex.get_part_by_tex`
```python
def get_part_by_tex(self, tex: str, **kwargs) -> Mobject:
```
- `ret`: the matching sub-mobject (the **live** scene sub-object, not a copy; transforming it changes the formula).
- `args`:
  - `tex: str` — part text; **no match returns `None`** (not an error).
- `errs`:
  - `AttributeError` — chaining onto the `None` result (eg `part.width`) when the part was not found; test for `None` first.
- `see`: ../zh_CN/04-图形与文本/09b-片段方法与列表.md

### `MathTex.set_opacity_by_tex`
```python
def set_opacity_by_tex(self, tex: str, opacity: float = 0.5, remaining_opacity: float | None = None, **kwargs) -> Self:
```
- `ret`: `Self`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `tex` | `str` | required | part to adjust |
| `opacity` | `float` | `0.5` | opacity of that part |
| `remaining_opacity` | `float \| None` | `None` | opacity of all other parts; `None` leaves them untouched |

- `notes`:
  - `opacity` and `remaining_opacity` are independent. Successive calls overwrite previous values for the parts they touch.
- `see`: ../zh_CN/04-图形与文本/09b-片段方法与列表.md

### `MathTexPart`
```python
# not constructed directly: internal class representing one MathTex fragment
```
- `ret`: n/a.
- `args`:
  - (internal) instance created by `MathTex`; encountered when iterating `MathTex.submobjects` / `.family_members_with_points()`.
- `notes`:
  - Attribute `.tex_string: str` — the fragment's LaTeX text, used for matching/display.
  - `submobjects` order == LaTeX write order, including non-letter parts (`^2`, `+`); index-based lookup must follow that order.
- `see`: ../zh_CN/04-图形与文本/09b-片段方法与列表.md

### `BulletedList`
```python
def __init__(self, *items: str, buff: float = MED_LARGE_BUFF, dot_scale_factor: float = 2, tex_environment: str | None = None, **kwargs) -> None:
```
- `ret`: `BulletedList`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `*items` | `str...` | required | one string per item |
| `buff` | `float` | `MED_LARGE_BUFF` (0.5) | item spacing |
| `dot_scale_factor` | `float` | `2` | bullet dot scale |
| `tex_environment` | `str \| None` | `None` | **discouraged**: outer LaTeX env; leave default |

- `ret`/method: `fade_all_but(index_or_string, opacity=0.5)`.
- `notes`:
  - `fade_all_but` supports **index only**: passing a string raises (see errs). Items' `tex_string` carry a trailing `\\` newline, so plain text or `\item x` will not match.
  - `fade_all_but` only dims the items in "the rest"; previously dimmed items that are no longer in "the rest" are **not restored** — reset them yourself with `set_opacity`.
- `errs`:
  - `Exception: Could not locate part by provided tex string '…'` — string passed to `fade_all_but` → use an integer index.
- `see`: ../zh_CN/04-图形与文本/09b-片段方法与列表.md

### `Title`
```python
def __init__(self, *text_parts: str, include_underline: bool = True, match_underline_width_to_text: bool = False, underline_buff: float = MED_SMALL_BUFF, **kwargs) -> None:
```
- `ret`: `Title`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `*text_parts` | `str...` | required | title text; multiple parts join on one line, individually colorable |
| `include_underline` | `bool` | `True` | draw the underline |
| `match_underline_width_to_text` | `bool` | `False` | `False` = full screen width; `True` = text width |
| `underline_buff` | `float` | `MED_SMALL_BUFF` (0.25) | gap between underline and text |

- `notes`:
  - Defaults to the **top edge** with full-width underline → use as a page header.
- `see`: ../zh_CN/04-图形与文本/09b-片段方法与列表.md

---

## Typst

### `Typst`
```python
def __init__(self, typst_code: str, *, font_size: float = 48, typst_preamble: str = "", color: ParsableManimColor | None = None, stroke_width: float | None = None, font_paths: list[str | Path] | None = None, track_baselines: bool = False, should_center: bool = True, height: float | None = None) -> None:
```
- `ret`: `Typst` (subclass of `SVGMobject`).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `typst_code` | `str` | required | Typst source; math inside `$...$` |
| `font_size` | `float` | `48` | font size |
| `typst_preamble` | `str` | `""` | prepended definitions (`#set`, `#let`, …) |
| `color` | `ManimColor \| None` | `None` | whole color |
| `stroke_width` | `float \| None` | `None` | stroke width |
| `font_paths` | `list[str \| Path] \| None` | `None` | extra font directories |
| `track_baselines` | `bool` | `False` | baseline tracking (multi-line mixing) |
| `should_center` | `bool` | `True` | move result to origin |
| `height` | `float \| None` | `None` | scale to height (wins over `font_size`) |

- `notes`:
  - **RTM-provided**: Typst typesetting backend; upstream ManimCE 0.21 lacks `TypstMath` (re-exported from the bundled manim).
  - Typst math uses `$...$` (not LaTeX `$` pairing). `#let` definitions must precede their use (`typst_preamble` or top of `typst_code`).
  - When both `height` and `font_size` are given, `height` wins.
  - **First render blocks the caller**: compilation is synchronous in `__init__` (~0.4 s cold, ~30 ms cached). A **visible** window shows a "compiling formula" popup (`runtime.md` → *Compile-wait popup*); output is unaffected.
- `see`: ../zh_CN/04-图形与文本/10-Typst.md

### `Typst.select`
```python
def select(self, key: str | int) -> VGroup:
```
- `ret`: `VGroup` — submobjects of the selected group.
- `args`:
  - `key: str | int` — a label name matching a `data-typst-label` in the SVG, or an integer index into auto-numbered `{{ }}` groups (`_grp-0`, `_grp-1`, …).
- `notes`:
  - Labels come from the `manimgrp` helper, or auto from `{{ }}` in `MathTypst`. (src)
- `errs`:
  - `KeyError` — no group with that label.
  - `IndexError` — integer index out of range.
- `see`: ../zh_CN/04-图形与文本/10-Typst.md

### `TypstMath` / `MathTypst`
```python
def __init__(self, math_expression: str, **kwargs) -> None:
```
- `ret`: `MathTypst`; **`TypstMath` is an alias of `MathTypst`** (`typst_support.py: TypstMath = MathTypst`).
- `args`:
  - `math_expression: str` — math expression only (auto-wrapped in `$ ... $`); supports `{{ ... }}` groups, optionally `{{ content : label }}`.
  - `**kwargs` — forwarded to `Typst` (`font_size`/`color`/`stroke_width`/…).
- `notes`:
  - Do **not** add your own `$` (would nest twice).
  - Typst math syntax differs from LaTeX: `sqrt(x)`, `a/b`, `mat(1, 2; 3, 4)`, `integral_0^1`, `approx`.
  - `{{ }}` groups are selectable via `Typst.select`.
- `see`: ../zh_CN/04-图形与文本/10-Typst.md
- `eg`:
```python
TypstMath("sum_(i=1)^n i = (n(n+1))/2", font_size=44)
TypstMath("mat(1, 2; 3, 4)", font_size=40)
MathTypst("{{ a^2 + b^2 : lhs }} = {{ c^2 }}").select("lhs").set_color(RED)
```

### auto-route: `MathTex` (LaTeX → Typst)
```python
MathTex(r"\frac{a}{b} + \sqrt{x}")   # RTM internally renders via Typst
```
- `notes`:
  - `MathTex` keeps LaTeX syntax (`\frac`, `\sqrt`, …); RTM converts to Typst internally, so **no local LaTeX needed** for the convertible subset.
  - Fragment API (`set_color_by_tex`, `get_part_by_tex`, `mt2[0].set_color(...)`, `tex_to_color_map`) works unchanged.
  - A few macros (custom `\newcommand`, complex `tikz`-like) have no implementation → if it fails to typeset, write `TypstMath` directly.
  - Disable with `RTM_TYPST=0`; debug with `RTM_TYPST_DEBUG=1`. `Tex` never auto-routes.
- `see`: ../zh_CN/04-图形与文本/10-Typst.md

---

## Code

### `Code`
```python
def __init__(self, code_file: StrPath | None = None, code_string: str | None = None, language: str | None = None, formatter_style: str | Style = "vim", tab_width: int = 4, add_line_numbers: bool = True, line_numbers_from: int = 1, background: Literal["rectangle", "window"] = "rectangle", background_config: dict | None = None, paragraph_config: dict | None = None) -> None:
```
- `ret`: `Code` (`VGroup`: background + one text mobject per line). `scale`/`move_to` as a whole, or index per-line submobjects.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `code_file` | `str \| Path \| None` | `None` | read source from file; mutually exclusive with `code_string` |
| `code_string` | `str \| None` | `None` | source string (`\n` newline, `\t` indent) |
| `language` | `str \| None` | `None` | syntax-highlight language; else inferred from file extension |
| `formatter_style` | `str \| Style` | `"vim"` | color scheme; see `Code.get_styles_list()` |
| `tab_width` | `int` | `4` | tab width |
| `add_line_numbers` | `bool` | `True` | show line numbers |
| `line_numbers_from` | `int` | `1` | first line number |
| `background` | `"rectangle" \| "window"` | `"rectangle"` | background style |
| `background_config` | `dict \| None` | `None` | forwarded to the background rectangle |
| `paragraph_config` | `dict \| None` | `None` | forwarded to the internal `Paragraph` |

- `notes`:
  - Mixed space/`\t` indentation makes `tab_width` appear ineffective.
  - `background="window"` adds a title bar → taller than `rectangle`; reserve more space.
  - With `code_string` and no `language`, Pygments guesses the lexer.
- `errs`:
  - `ValueError: Either a code file or a code string must be specified.` — neither `code_file` nor `code_string` given.
- `see`: ../zh_CN/04-图形与文本/11-代码块.md

### `Code.get_styles_list`
```python
def get_styles_list() -> list[str]:
```
- `ret`: `list[str]` — all available formatter style names (currently 50, eg `vim`, `monokai`, `friendly`).
- `args`: none.
- `notes`:
  - **classmethod**: call as `Code.get_styles_list()`. The list follows the Pygments version; verify a hard-coded name first.
- `see`: ../zh_CN/04-图形与文本/11-代码块.md

---

## Numbers

### `DecimalNumber`
```python
def __init__(self, number: float = 0, num_decimal_places: int = 2, mob_class: type[SingleStringMathTex] = MathTex, include_sign: bool = False, group_with_commas: bool = True, digit_buff_per_font_unit: float = 0.001, show_ellipsis: bool = False, unit: str | None = None, unit_buff_per_font_unit: float = 0, include_background_rectangle: bool = False, edge_to_fix: Vector3DLike = LEFT, font_size: float = 48, stroke_width: float = 0, fill_opacity: float = 1.0, **kwargs) -> None:
```
- `ret`: `DecimalNumber`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `number` | `int \| float` | `0` | initial value |
| `num_decimal_places` | `int` | `2` | decimal places |
| `mob_class` | class | `MathTex` | renderer class (can be `Text`, LaTeX-free) |
| `include_sign` | `bool` | `False` | show `+` on positives |
| `group_with_commas` | `bool` | `True` | thousands separators |
| `digit_buff_per_font_unit` | `float` | `0.001` | digit spacing coefficient (scales with font size) |
| `show_ellipsis` | `bool` | `False` | append `...` when rounded/truncated |
| `unit` | `str \| None` | `None` | unit suffix (string goes through LaTeX, eg `r"\pi"`) |
| `unit_buff_per_font_unit` | `float` | `0` | unit spacing |
| `include_background_rectangle` | `bool` | `False` | attach a background rectangle |
| `edge_to_fix` | array-like | `LEFT` | which edge stays fixed on value change |
| `font_size` | `float` | `48` | font size |
| `stroke_width` | `float` | `0` | stroke width |
| `fill_opacity` | `float` | `1.0` | fill opacity |

- `ret`/methods: `set_value(number)`, `get_value()`, `increment_value(delta_t=1)`; `font_size` is a read/write property.
- `notes`:
  - `edge_to_fix` is only visible when the value length changes (`9.99 → 100.0`).
  - `set_value`/`increment_value` mutate immediately; animate via `ValueTracker` + updater.
  - `digit_to_depth` and `show_tractable_zeros` **do not exist** in the current source.
- `see`: ../zh_CN/04-图形与文本/12-数字与变量.md

### `Integer`
```python
def __init__(self, number: int = 0, num_decimal_places: int = 0, **kwargs) -> None:
```
- `ret`: `Integer` (`DecimalNumber` with `num_decimal_places=0`).
- `args`:
  - `number: int = 0` — initial integer.
  - `num_decimal_places: int = 0` — fixed 0 for the integer form.
  - `**kwargs` — all `DecimalNumber` params (`font_size`, `color`, `include_sign`, …).
- `ret`/methods: `get_value()` (overridden → returns `int`).
- `notes`:
  - `set_value` expects a numeric value; round in updaters (`int(...)`) for display. Updaters run every frame — do not create mobjects inside them.
- `see`: ../zh_CN/04-图形与文本/12-数字与变量.md

### `Variable`
```python
def __init__(self, var: float, label: str | Tex | MathTex | Text | SingleStringMathTex, var_type: type[DecimalNumber | Integer] = DecimalNumber, num_decimal_places: int = 2, **kwargs) -> None:
```
- `ret`: `Variable` (`VGroup`); attributes `variable.label`, `variable.value`, `variable.tracker` (`ValueTracker`).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `var` | `int \| float` | required | initial value |
| `label` | `str \| Tex \| Text \| MathTex` | required | name; a `str` becomes `MathTex` (so LaTeX like `"{a}_{i}"` works) |
| `var_type` | class | `DecimalNumber` | value renderer class (can be `Integer`) |
| `num_decimal_places` | `int` | `2` | decimal places |

- `notes`:
  - Animate the **`tracker`**: `v.tracker.animate.set_value(x)`. `v.value.set_value(...)` changes instantly (no transition).
- `see`: ../zh_CN/04-图形与文本/12-数字与变量.md

### `TextDecimalNumber` (RTM-only)
```python
def __init__(self, number: float = 0, font_size: float = 48, font: str = "Times New Roman", num_decimal_places: int = 2, **kwargs) -> None:
```
- `ret`: `TextDecimalNumber` (subclass of `Text`).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `number` | `float` | `0` | initial value (formatted `f"{number:.{places}f}"` then given to `Text`) |
| `font_size` | `float` | `48` | font size (part of the cache key) |
| `font` | `str` | `"Times New Roman"` | font name (via Pango) |
| `num_decimal_places` | `int` | `2` | decimal places |
| `**kwargs` | — | — | forwarded to `Text` (eg `color`) |

- `notes`:
  - **RTM deviation**: ManimCE 0.21 has no such class; it lives in `real_time_manim.animations.text`. Import: `from real_time_manim.animations.text import TextDecimalNumber`.
  - Method `set_value(number)` reuses cached glyphs (`_value_cache`) → no re-typeset. No `unit`/`edge_to_fix`/`include_sign` (it only takes a number).
  - Not a `DecimalNumber` replacement: `DecimalNumber` uses LaTeX (math font, `unit`, `edge_to_fix`); this uses plain text typesetting.
- `see`: ../zh_CN/04-图形与文本/12-数字与变量.md

---

## Matrix

### `Matrix`
```python
def __init__(self, matrix: Iterable[Iterable[Any] | Vector2DLike], v_buff: float = 0.8, h_buff: float = 1.3, bracket_h_buff: float = MED_SMALL_BUFF, bracket_v_buff: float = MED_SMALL_BUFF, add_background_rectangles_to_entries: bool = False, include_background_rectangle: bool = False, element_to_mobject: type[VMobject] | Callable[..., VMobject] = MathTex, element_to_mobject_config: dict = {}, element_alignment_corner: Vector3DLike = DR, left_bracket: str = "[", right_bracket: str = "]", stretch_brackets: bool = True, bracket_config: dict = {}, **kwargs) -> None:
```
- `ret`: `Matrix`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `matrix` | `list \| np.ndarray` | required | 2D data (strings via `MathTex`, or numbers) |
| `v_buff` | `float` | `0.8` | row spacing |
| `h_buff` | `float` | `1.3` | column spacing |
| `bracket_h_buff` | `float` | `MED_SMALL_BUFF` (0.25) | bracket↔content horizontal gap |
| `bracket_v_buff` | `float` | `MED_SMALL_BUFF` | bracket↔content vertical gap |
| `add_background_rectangles_to_entries` | `bool` | `False` | background block per element |
| `include_background_rectangle` | `bool` | `False` | background block for whole matrix |
| `element_to_mobject` | class/callable | `MathTex` | element renderer; numeric elements need a number class |
| `element_to_mobject_config` | `dict` | `{}` | config for the element renderer (eg `{"font_size": 40}`) |
| `element_alignment_corner` | array-like | `DR` | cell alignment corner |
| `left_bracket` | `str` | `"["` | left bracket shape |
| `right_bracket` | `str` | `"]"` | right bracket shape |
| `stretch_brackets` | `bool` | `True` | stretch brackets with matrix height |
| `bracket_config` | `dict` | `{}` | bracket style |

- `ret`/methods: `get_rows()`, `get_columns()`, `get_entries()`, `get_brackets()`, `get_mob_matrix()`; `set_row_colors(*colors)`, `set_column_colors(*colors)`, `add_background_to_entries()`.
- `notes`:
  - `font_size` is **not** a Matrix param — `**kwargs` falls through to `Mobject.__init__` (see errs). Use `element_to_mobject_config={"font_size": …}`.
  - Brackets are drawn via LaTeX; `stretch_brackets=False` only stops stretching (shape still LaTeX), so `bracket_config` still recolors them.
- `errs`:
  - `TypeError: Mobject.__init__() got an unexpected keyword argument 'font_size'` — passing `font_size=` → use `element_to_mobject_config`.
  - `AttributeError: 'int' object has no attribute 'find'` — `element_to_mobject=Text`/`MathTex` with numeric elements → use `DecimalNumber`/`Integer` for numbers.
- `see`: ../zh_CN/04-图形与文本/13-矩阵.md

### `DecimalMatrix`
```python
def __init__(self, matrix: Iterable[Iterable[Any]], element_to_mobject: type[VMobject] | Callable[..., VMobject] = DecimalNumber, element_to_mobject_config: dict = {"num_decimal_places": 1}, **kwargs) -> None:
```
- `ret`: `DecimalMatrix`.
- `args`:
  - `matrix: list | np.ndarray` — float data.
  - `element_to_mobject: class/callable = DecimalNumber` — element renderer; **allowed**: `DecimalNumber` or another number class (`Integer`). Do **not** use `Text`/`MathTex` (see errs).
  - `element_to_mobject_config: dict = {"num_decimal_places": 1}` — element config.
- `notes`:
  - `element_to_mobject_config` **replaces** the default dict (no merge); include `font_size` when changing decimal places.
- `errs`:
  - `AttributeError` — `Text(1.2)`/`MathTex(1.2)` as element renderer with float elements.
- `see`: ../zh_CN/04-图形与文本/13-矩阵.md

### `IntegerMatrix`
```python
def __init__(self, matrix: Iterable[Iterable[Any]], element_to_mobject: type[VMobject] | Callable[..., VMobject] = Integer, **kwargs) -> None:
```
- `ret`: `IntegerMatrix`.
- `args`:
  - `matrix: list | np.ndarray` — numeric data.
  - `element_to_mobject: class/callable = Integer` — element renderer (can be `DecimalNumber` for decimals; `Text`/`MathTex` error on numeric elements).
  - `**kwargs` — all `Matrix` params (`v_buff`/`h_buff`/…).
- `notes`:
  - Default renderer is `Integer`; for decimals prefer `DecimalMatrix`.
- `see`: ../zh_CN/04-图形与文本/13-矩阵.md

### `MobjectMatrix`
```python
def __init__(self, matrix: Iterable[Iterable[Any]], element_to_mobject: type[VMobject] | Callable[..., VMobject] = <identity>, **kwargs) -> None:
```
- `ret`: `MobjectMatrix`.
- `args`:
  - `matrix: list[list[Mobject]]` — a ready Mobject per cell.
  - `element_to_mobject: callable = <identity>` (`lambda m: m`) — element transform (eg `lambda m: m.copy().scale(0.5)`).
  - `**kwargs` — all `Matrix` params.
- `notes`:
  - Inside the transform call `m.copy()` before mutating, otherwise the caller's object is changed too.
- `see`: ../zh_CN/04-图形与文本/13-矩阵.md

### `get_det_text`
```python
def get_det_text(matrix: Matrix, determinant: int | str | None = None, background_rect: bool = False, initial_scale_factor: float = 2) -> VGroup:
```
- `ret`: `VGroup` (text + optional background rect).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `matrix` | `Matrix` | required | a constructed matrix (for symbols & size) |
| `determinant` | `int \| str \| None` | `None` | `None` → only `det(...)`; else `det(A) = value` |
| `background_rect` | `bool` | `False` | add a background rect |
| `initial_scale_factor` | `float` | `2` | initial scale |

- `notes`:
  - Returns a `VGroup` → place with `next_to(matrix, DOWN)` and animate as a whole.
- `see`: ../zh_CN/04-图形与文本/13-矩阵.md

### `matrix_to_tex_string`
```python
def matrix_to_tex_string(matrix: np.ndarray) -> str:
```
- `ret`: `str` — bare array LaTeX string, **without brackets**.
- `args`:
  - `matrix: list | np.ndarray` — 2D data.
- `notes`:
  - No brackets; add `\left[`/`\right]` yourself, or use `Matrix`.
- `see`: ../zh_CN/04-图形与文本/13-矩阵.md

### `matrix_to_mobject`
```python
def matrix_to_mobject(matrix: np.ndarray) -> MathTex:
```
- `ret`: `MathTex` — ready to add/animate, **without brackets**.
- `args`:
  - `matrix: list | np.ndarray` — 2D data.
- `notes`:
  - Differs from `matrix_to_tex_string` only in returning a mobject; still no brackets.
- `see`: ../zh_CN/04-图形与文本/13-矩阵.md

### Matrix methods
- `get_rows()`, `get_columns()`, `get_entries()`, `get_brackets()`, `get_mob_matrix()` — return the corresponding structures.
- `set_row_colors(*colors)` / `set_column_colors(*colors)` — color by row/column.
- `add_background_to_entries()` — add a background per cell after construction.
- `see`: ../zh_CN/04-图形与文本/13-矩阵.md

---

## Table

### `Table`
```python
def __init__(self, table: Iterable[Iterable[Any]], row_labels: Iterable[VMobject] | None = None, col_labels: Iterable[VMobject] | None = None, top_left_entry: VMobject | None = None, v_buff: float = 0.8, h_buff: float = 1.3, include_outer_lines: bool = False, include_inner_lines: bool = True, add_background_rectangles_to_entries: bool = False, entries_background_color: ManimColor = BLACK, include_background_rectangle: bool = False, background_rectangle_color: ManimColor = BLACK, element_to_mobject: type[VMobject] | Callable[..., VMobject] = Paragraph, element_to_mobject_config: dict = {}, arrange_in_grid_config: dict = {}, line_config: dict = {}, **kwargs) -> None:
```
- `ret`: `Table` (subclass of `VGroup`).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `table` | `list[list]` | required | 2D content (must be accepted by `element_to_mobject`) |
| `row_labels` | `list[Mobject] \| None` | `None` | row labels |
| `col_labels` | `list[Mobject] \| None` | `None` | column labels |
| `top_left_entry` | `Mobject \| None` | `None` | top-left cell; only usable when **both** label sets are given |
| `v_buff` | `float` | `0.8` | row spacing |
| `h_buff` | `float` | `1.3` | column spacing |
| `include_outer_lines` | `bool` | `False` | draw the outer frame |
| `include_inner_lines` | `bool` | `True` | draw the inner grid |
| `add_background_rectangles_to_entries` | `bool` | `False` | background per cell |
| `entries_background_color` | `ManimColor` | `BLACK` | per-cell background color |
| `include_background_rectangle` | `bool` | `False` | background for whole table |
| `background_rectangle_color` | `ManimColor` | `BLACK` | whole-table background color |
| `element_to_mobject` | class/callable | `Paragraph` | cell renderer |
| `element_to_mobject_config` | `dict` | `{}` | config for the renderer |
| `arrange_in_grid_config` | `dict` | `{}` | grid arrangement config |
| `line_config` | `dict` | `{}` | line style |

- `ret`/methods: `get_rows()`, `get_columns()`, `get_entries()`, `get_horizontal_lines()`, `get_vertical_lines()`, `set_row_colors(*colors)`, `set_column_colors(*colors)`, `add_background_to_entries(color)`; plus `add_highlighted_cell`/`get_cell`/`get_highlighted_cell`/`create` (below).
- `notes`:
  - Cell renderer decides what may go in a cell: `Table`→`Paragraph`, `MathTable`→`MathTex`, `MobjectTable`→identity, `IntegerTable`/`DecimalTable`→`Integer`/`DecimalNumber`. Type mismatch errors (numeric element → `Text`/`MathTex` → `AttributeError`).
  - `Table` is a `VGroup`, so generic VGroup ops (`arrange`, `scale`, whole-color, indexing) apply.
  - `set_row_colors`/`set_column_colors` repaint by row/column; a later call overwrites the earlier color for the same cells.
- `see`: ../zh_CN/04-图形与文本/14-表格.md

### `MathTable`
```python
def __init__(self, table: Iterable[Iterable[str]], element_to_mobject: type[SingleStringMathTex] = MathTex, **kwargs) -> None:
```
- `ret`: `MathTable`.
- `args`:
  - `table: list[list[str]]` — cell text in LaTeX math mode (eg `r"\frac{a}{b}"`).
  - `element_to_mobject: class = MathTex` — cell renderer (can be `Text`).
  - `**kwargs` — identical to `Table`.
- `notes`:
  - Cell strings **must be valid LaTeX** (unescaped `_`, `%` fail to compile). For plain text use `Text` or `element_to_mobject=Text`.
- `see`: ../zh_CN/04-图形与文本/14-表格.md

### `MobjectTable`
```python
def __init__(self, table: Iterable[Iterable[Mobject]], element_to_mobject: Callable = <identity>, **kwargs) -> None:
```
- `ret`: `MobjectTable`.
- `args`:
  - `table: list[list[Mobject]]` — a ready Mobject per cell.
  - `element_to_mobject: callable = <identity>` — element transform (eg `lambda m: m.copy().scale(0.5)`).
  - `**kwargs` — identical to `Table`.
- `notes`:
  - Use `m.copy()` before mutating inside the transform. Table lines are **separate objects** and do not scale with cells.
- `see`: ../zh_CN/04-图形与文本/14-表格.md

### `IntegerTable`
```python
def __init__(self, table: Iterable[Iterable[int]], element_to_mobject: type[Integer] = Integer, **kwargs) -> None:
```
- `ret`: `IntegerTable`.
- `args`:
  - `table: list[list[int]]` — integer data.
  - `element_to_mobject: class = Integer` — cell renderer (can be `DecimalNumber` with `num_decimal_places=0`).
  - `**kwargs` — identical to `Table`.
- `notes`:
  - Do not swap numeric elements to `Text`/`MathTex`. `color` colors both cells and grid lines.
- `see`: ../zh_CN/04-图形与文本/14-表格.md

### `DecimalTable`
```python
def __init__(self, table: Iterable[Iterable[float]], element_to_mobject: type[DecimalNumber] = DecimalNumber, element_to_mobject_config: dict = {"num_decimal_places": 1}, **kwargs) -> None:
```
- `ret`: `DecimalTable`.
- `args`:
  - `table: list[list[float]]` — decimal data.
  - `element_to_mobject: class = DecimalNumber` — cell renderer (can be `Integer`).
  - `element_to_mobject_config: dict = {"num_decimal_places": 1}` — cell config.
  - `**kwargs` — identical to `Table`.
- `notes`:
  - `element_to_mobject_config` **replaces** the default (no merge); include `font_size` when changing places.
- `see`: ../zh_CN/04-图形与文本/14-表格.md

### `Table.add_highlighted_cell`
```python
def add_highlighted_cell(self, pos: Sequence[int] = (1, 1), color: ParsableManimColor = YELLOW, **kwargs) -> Self:
```
- `ret`: `Self` (in-place, chainable); the highlight block then follows the table's transforms.
- `args`:
  - `pos: Sequence[int] = (1, 1)` — cell `(row, col)`, **1-based**.
  - `color: ManimColor = YELLOW` — highlight color.
  - `**kwargs: Any` — forwarded to the background block (`BackgroundRectangle`), eg `fill_opacity=0.4`.
- `notes`:
  - Position is `(row, col)` **1-based** — `(1, 1)` is top-left (differs from Python 0-based indexing). Repeated calls on the same cell stack new blocks (no replacement).
- `see`: ../zh_CN/04-图形与文本/14b-表格方法.md

### `Table.get_cell`
```python
def get_cell(self, pos: Sequence[int] = (1, 1), **kwargs) -> Polygon:
```
- `ret`: `Polygon` — the cell polygon (stroke visible).
- `args`:
  - `pos: Sequence[int] = (1, 1)` — cell `(row, col)`, 1-based.
  - `**kwargs: Any` — forwarded to the `Polygon` (eg `color=`, `fill_opacity=`).
- `notes`:
  - Distinct from `get_highlighted_cell` (a background rectangle). For a filled cell, the latter is easier.
- `see`: ../zh_CN/04-图形与文本/14b-表格方法.md

### `Table.get_highlighted_cell`
```python
def get_highlighted_cell(self, pos: Sequence[int] = (1, 1), color: ParsableManimColor = YELLOW, **kwargs) -> BackgroundRectangle:
```
- `ret`: `BackgroundRectangle` — **not** auto-added to the table.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `pos` | `Sequence[int]` | `(1, 1)` | cell `(row, col)`, 1-based |
| `color` | `ManimColor` | `YELLOW` | background color |
| `**kwargs` | `Any` | — | forwarded to `BackgroundRectangle` (`fill_opacity=`, `buff=`) |

- `notes`:
  - To make the highlight follow the table, `t.add(hl)`; for a one-off, just `FadeIn(hl)`.
- `see`: ../zh_CN/04-图形与文本/14b-表格方法.md

### `Table.create`
```python
def create(self, lag_ratio: float = 1, line_animation: Callable[[VMobject | VGroup], Animation] = Create, label_animation: Callable[[VMobject | VGroup], Animation] = Write, element_animation: Callable[[VMobject | VGroup], Animation] = Create, entry_animation: Callable[[VMobject | VGroup], Animation] = FadeIn, **kwargs) -> AnimationGroup:
```
- `ret`: `AnimationGroup` — pass to `win.play(...)`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `lag_ratio` | `float` | `1` | stagger between groups (lines / labels / cells) |
| `line_animation` | class | `Create` | grid-line entrance |
| `label_animation` | class | `Write` | row/col label entrance |
| `element_animation` | class | `Create` | cell content entrance |
| `entry_animation` | class | `FadeIn` | whole-entry animation |
| `**kwargs` | `Any` | — | forwarded to the internal `AnimationGroup` (eg `run_time=`) |

- `notes`:
  - Returns an **animation group**, not the table. Build the table first; do not `add` it to the scene before `win.play` or it will appear twice.
- `see`: ../zh_CN/04-图形与文本/14b-表格方法.md

---

## Image & SVG

### `ImageMobject`
```python
def __init__(self, filename_or_array: StrPath | np.ndarray, scale_to_resolution: int = 1080, invert: bool = False, image_mode: str = "RGBA", **kwargs) -> None:
```
- `ret`: `ImageMobject`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `filename_or_array` | `str \| Path \| np.ndarray` | required | image path (png/jpg…) or pixel array |
| `scale_to_resolution` | `int` | `1080` | target height to downscale to on load |
| `invert` | `bool` | `False` | invert colors |
| `image_mode` | `str` | `"RGBA"` | pixel mode (`"RGBA"` has alpha, `"RGB"` not) |

- `ret`/methods: `set_opacity(alpha)`, `get_pixel_array()` (returns `(H, W, 4)` `uint8`), `set_resampling_algorithm(algo)`.
- `notes`:
  - **Naming**: class is `ImageMobject` (lowercase `m`), not `ImageMObject`. `real_time_manim` top level exports `ImageMobject`, `ImageMobjectFromCamera`, `SVGMobject`, `VMobjectFromSVGPath`, `Camera`.
  - `scale_to_resolution` sets the load-time pixel count; on-screen size is set by `.scale()`/`.set(height=…)`.
- `see`: ../zh_CN/04-图形与文本/15-图片与SVG.md

### `ImageMobjectFromCamera`
```python
def __init__(self, camera: MovingCamera, default_display_frame_config: dict | None = None, **kwargs) -> None:
```
- `ret`: `ImageMobjectFromCamera`.
- `args`:
  - `camera: Camera` — source camera (in a scene, `self.camera`); call `capture_mobject(...)` first so `pixel_array` has content.
  - `default_display_frame_config: dict | None = {"stroke_width": 3, "stroke_color": WHITE, "buff": 0}` — default outer-frame style.
- `ret`/methods: `add_display_frame(**kwargs)` (add/replace the frame; kwargs override the config), `get_pixel_array()`.
- `notes`:
  - Captures the camera's **current** `pixel_array`: order is place objects → `capture_mobject` → construct the image. It is a static snapshot; later scene changes do not update it.
- `see`: ../zh_CN/04-图形与文本/15-图片与SVG.md

### `AbstractImageMobject`
```python
def __init__(self, scale_to_resolution: int, pixel_array_dtype: str = "uint8", resampling_algorithm: Resampling = Resampling.BICUBIC, **kwargs) -> None:
```
- `ret`: n/a (abstract base; **not** exported at top level; import from `manim.mobject.types.image_mobject`).
- `args`:
  - `scale_to_resolution: int` — target height (concrete `ImageMobject` fills in `1080`).
  - `pixel_array_dtype: str = "uint8"` — pixel array dtype.
  - `resampling_algorithm: Resampling = BICUBIC` — rescale resampling algorithm.
- `notes`:
  - Do not construct directly; use a concrete instance's methods: `get_pixel_array()`, `set_resampling_algorithm(...)`, `set_color(...)`.
  - `set_color()` multiplies a color over the whole image (not a palette swap); use `set_opacity()` for fading.
- `see`: ../zh_CN/04-图形与文本/15-图片与SVG.md

### `SVGMobject`
```python
def __init__(self, file_name: str | Path | None = None, should_center: bool = True, height: float | None = 2, width: float | None = None, color: ManimColor | None = None, opacity: float | None = None, fill_color: ManimColor | None = None, fill_opacity: float | None = None, stroke_color: ManimColor | None = None, stroke_opacity: float | None = None, stroke_width: float | None = None, svg_default: dict | None = None, path_string_config: dict | None = None, use_svg_cache: bool = True, **kwargs) -> None:
```
- `ret`: `SVGMobject` (submobjects are the paths; `Text` is a subclass).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `file_name` | `str \| Path \| None` | `None` | SVG file path |
| `should_center` | `bool` | `True` | move to origin |
| `height` | `float \| None` | `2` | loaded height |
| `width` | `float \| None` | `None` | scale by width (alternative to `height`) |
| `color` | `ManimColor \| None` | `None` | unified color (fill+stroke) |
| `opacity` | `float \| None` | `None` | overall opacity |
| `fill_color`/`fill_opacity` | `ManimColor`/`float \| None` | `None` | fill color/opacity |
| `stroke_color`/`stroke_opacity`/`stroke_width` | `ManimColor`/`float \| None` | `None` | stroke color/opacity/width |
| `svg_default` | `dict \| None` | `None` | **whole** default style table (all keys required) |
| `path_string_config` | `dict \| None` | `None` | per-path parse config (eg `{"long_lines": True}`) |
| `use_svg_cache` | `bool` | `True` | reuse same-file parse cache |

- `notes`:
  - `color` overrides both fill and stroke; for different fill/stroke colors use `fill_color` + `stroke_color`.
  - `svg_default` **replaces** the whole default style (no merge); all keys required.
- `errs`:
  - `KeyError: 'color'` — `svg_default` missing a key. Required keys: `color` / `fill_color` / `fill_opacity` / `stroke_color` / `stroke_opacity` / `stroke_width` / `opacity`.
- `see`: ../zh_CN/04-图形与文本/15-图片与SVG.md

### `VMobjectFromSVGPath`
```python
def __init__(self, path_obj: svgelements.Path, long_lines: bool = False, should_subdivide_sharp_curves: bool = False, should_remove_null_curves: bool = False, **kwargs) -> None:
```
- `ret`: `VMobjectFromSVGPath` (the glyph-leaf class of `Text`/`MathTex`).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `path_obj` | `svgelements.Path` | required | **parsed** path: `se.Path("M 0 0 L 2 0 L 2 2 Z")`; a `str` raises (see errs) |
| `long_lines` | `bool` | `False` | long straight-segment splitting |
| `should_subdivide_sharp_curves` | `bool` | `False` | subdivide at sharp corners |
| `should_remove_null_curves` | `bool` | `False` | drop zero-length segments |

- `notes`:
  - The three toggles are documented "only effective under the OpenGL renderer"; under non-OpenGL they do not error, just no shape change.
- `errs`:
  - `AttributeError: 'str' object has no attribute 'approximate_arcs_with_quads'` — passing a `d` string → wrap with `se.Path("…")` first.
- `see`: ../zh_CN/04-图形与文本/15-图片与SVG.md

---

## Braces

### `Brace`
```python
def __init__(self, mobject: Mobject, direction: Vector3DLike = DOWN, buff: float = 0.2, sharpness: float = 2, stroke_width: float = 0, fill_opacity: float = 1.0, background_stroke_width: float = 0, background_stroke_color: ParsableManimColor = BLACK, **kwargs) -> None:
```
- `ret`: `Brace` (subclass of `VMobjectFromSVGPath`).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | required | annotated object (brace takes its position & length) |
| `direction` | array-like | `DOWN` | brace orientation |
| `buff` | `float` | `0.2` | gap to the object |
| `sharpness` | `float` | `2` | corner sharpness (tip acuity) |
| `stroke_width` | `float` | `0` | stroke width (inner) |
| `fill_opacity` | `float` | `1.0` | fill opacity |
| `background_stroke_width` | `float` | `0` | background stroke width (outer) |
| `background_stroke_color` | `ManimColor` | `BLACK` | background stroke color |

- `ret`/methods: `get_text`, `get_tex`, `put_at_tip`, `get_tip`, `get_direction` (below).
- `notes`:
  - `sharpness` too small (eg 1) blunts the tip into an arc.
  - `background_stroke_*` draws an outer layer, `stroke_width` an inner one — the two can differ in color.
- `see`: ../zh_CN/04-图形与文本/16-花括号标注.md

### `Brace.get_text`
```python
def get_text(self, *text: str, **kwargs) -> Tex:
```
- `ret`: `Tex` — placed at the brace tip.
- `args`:
  - `*text: str` — text placed at the tip.
  - `**kwargs: Any` — **all forwarded to `put_at_tip`** (ultimately `mob.next_to(...)`), eg `buff`, `aligned_edge`.
- `notes`:
  - **RTM/CE gotcha**: kwargs only reach `put_at_tip`, so `font_size`/`color` are **not** accepted here. Set them on the returned object: `lbl = br.get_text("x"); lbl.scale(0.6).set_color(GREY)`.
- `errs`:
  - `TypeError: Mobject.next_to got an unexpected keyword argument 'font_size'` — `get_text("x", font_size=20)`.
- `see`: ../zh_CN/04-图形与文本/16-花括号标注.md

### `Brace.get_tex`
```python
def get_tex(self, *tex: str, **kwargs) -> MathTex:
```
- `ret`: `MathTex` — placed at the brace tip.
- `args`:
  - `*tex: str` — math placed at the tip.
  - `**kwargs: Any` — forwarded to `put_at_tip` only (same restriction as `get_text`).
- `notes`:
  - `Tex` is math mode: avoid underscores in the string. Font size/color set after retrieval.
- `errs`:
  - `TypeError: Mobject.next_to got an unexpected keyword argument 'font_size'`.
- `see`: ../zh_CN/04-图形与文本/16-花括号标注.md

### `Brace.put_at_tip`
```python
def put_at_tip(self, mob: Mobject, use_next_to: bool = True, **kwargs) -> Self:
```
- `ret`: `Self` (the brace).
- `args`:
  - `mob: Mobject` — object placed at the tip.
  - `use_next_to: bool = True` — if `True`, place via `next_to`; else `move_to` + directional shift.
  - `**kwargs: Any` — forwarded to `next_to` (when `use_next_to`) or used for `buff`.
- `see`: ../zh_CN/04-图形与文本/16-花括号标注.md

### `Brace.get_tip`
```python
def get_tip(self) -> Point3D:
```
- `ret`: `Point3D` — tip coordinates.
- `args`: none.
- `see`: ../zh_CN/04-图形与文本/16-花括号标注.md

### `Brace.get_direction`
```python
def get_direction(self) -> Vector3D:
```
- `ret`: `Vector3D` — unit vector from center to tip.
- `args`: none.
- `see`: ../zh_CN/04-图形与文本/16-花括号标注.md

### `BraceText`
```python
def __init__(self, obj: Mobject, text: str, label_constructor: type[SingleStringMathTex | Text] = Text, **kwargs) -> None:
```
- `ret`: `BraceText` (subclass of `BraceLabel`; the manual entry is `BraceText`, there is no `BraceWithText`).
- `args`:
  - `obj: Mobject` — annotated object.
  - `text: str | Mobject` — label content.
  - `label_constructor: class = Text` — label renderer (can be `MathTex`).
  - `**kwargs` — forwarded to `BraceLabel` (`brace_direction`, `font_size`, `buff`, `brace_config`).
- `notes`:
  - Constructs "brace + plain text" in one step; text sits outside the tip.
- `see`: ../zh_CN/04-图形与文本/16-花括号标注.md

### `BraceLabel`
```python
def __init__(self, obj: Mobject, text: str, brace_direction: Vector3DLike = DOWN, label_constructor: type[SingleStringMathTex | Text] = MathTex, font_size: float = DEFAULT_FONT_SIZE, buff: float = 0.2, brace_config: dict | None = None, **kwargs) -> None:
```
- `ret`: `BraceLabel` (subclass of `VMobject`).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `obj` | `Mobject` | required | annotated object |
| `text` | `str \| Mobject` | required | label (string goes through LaTeX) |
| `brace_direction` | array-like | `DOWN` | brace orientation |
| `label_constructor` | class | `MathTex` | label renderer (`BraceText` swaps in `Text`) |
| `font_size` | `float` | `DEFAULT_FONT_SIZE` | label font size |
| `buff` | `float` | `0.2` | gap |
| `brace_config` | `dict \| None` | `None` | brace style |

- `ret`/methods: `creation_anim`, `change_label`, `change_brace_label`, `shift_brace` (below).
- `notes`:
  - `change_label`/`change_brace_label`/`shift_brace` mutate **immediately** (not animated); animate afterwards (`win.play(bl.creation_anim())`, or `Write`/`Transform` on `bl.label`).
- `see`: ../zh_CN/04-图形与文本/16-花括号标注.md

### `BraceLabel.creation_anim`
```python
def creation_anim(self, label_anim: type[Animation] = FadeIn, brace_anim: type[Animation] = GrowFromCenter) -> AnimationGroup:
```
- `ret`: `AnimationGroup` (brace + label together).
- `args`:
  - `label_anim: class = FadeIn` — label entrance.
  - `brace_anim: class = GrowFromCenter` — brace entrance.
- `see`: ../zh_CN/04-图形与文本/16-花括号标注.md

### `BraceLabel.change_label`
```python
def change_label(self, *text: str, **kwargs) -> Self:
```
- `ret`: `Self`.
- `args`:
  - `*text: str` — new label text.
  - `**kwargs` — forwarded to `label_constructor`.
- `notes`:
  - Mutates immediately. `creation_anim` adds the old label separately to the scene, so `FadeOut(old_label)` alongside `FadeIn(bl.label)` when swapping.
- `see`: ../zh_CN/04-图形与文本/16-花括号标注.md

### `BraceLabel.change_brace_label`
```python
def change_brace_label(self, obj: Mobject, *text: str, **kwargs) -> Self:
```
- `ret`: `Self`.
- `args`:
  - `obj: Mobject` — new annotated object.
  - `*text: str` — new label text.
  - `**kwargs` — forwarded.
- `notes`: Equivalent to `shift_brace(obj)` then `change_label(*text)`. Mutates immediately.
- `see`: ../zh_CN/04-图形与文本/16-花括号标注.md

### `BraceLabel.shift_brace`
```python
def shift_brace(self, obj: Mobject, **kwargs) -> Self:
```
- `ret`: `Self`.
- `args`:
  - `obj: Mobject` (or `list`) — object to re-fit the brace onto.
  - `**kwargs` — forwarded to `Brace`.
- `notes`: Mutates immediately.
- `see`: ../zh_CN/04-图形与文本/16-花括号标注.md

### `BraceBetweenPoints`
```python
def __init__(self, point_1: Point3DLike, point_2: Point3DLike, direction: Vector3DLike = ORIGIN, **kwargs) -> None:
```
- `ret`: `BraceBetweenPoints` (subclass of `Brace`).
- `args`:
  - `point_1: array-like` — endpoint 1.
  - `point_2: array-like` — endpoint 2.
  - `direction: array-like = ORIGIN` — orientation; `ORIGIN` auto-picks the perpendicular.
  - `**kwargs` — forwarded to `Brace`.
- `notes`:
  - Does not need a Mobject; annotates "distance / interval between two points". Supports `get_text`/`get_tex`.
  - With `direction=ORIGIN` on a slanted segment the auto result may be less intuitive — specify `UP`/`DOWN`.
- `see`: ../zh_CN/04-图形与文本/16-花括号标注.md

### `ArcBrace`
```python
def __init__(self, arc: Arc | None = None, direction: Vector3DLike = RIGHT, **kwargs) -> None:
```
- `ret`: `ArcBrace` (subclass of `Brace`).
- `args`:
  - `arc: Arc | None = None` — annotated arc; `None` uses the **unit circle**.
  - `direction: array-like = RIGHT` — orientation (outside/inside of the arc).
  - `**kwargs` — forwarded to `Brace`.
- `notes`:
  - Brace radius follows the arc, so a shorter arc yields a flatter brace. For angle annotation put `direction` outside the arc (default `RIGHT` is outward). Supports `get_text`.
- `see`: ../zh_CN/04-图形与文本/16-花括号标注.md
