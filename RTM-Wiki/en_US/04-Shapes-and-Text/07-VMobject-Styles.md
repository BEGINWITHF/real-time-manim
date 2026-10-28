# VMobject styles (1): fill, stroke and whole-object style

The following methods are defined on `VMobject` in `mobject/types/vectorized_mobject.py`, and they are **common to all shapes / text / matrices / tables** (`scale`/`rotate`/`shift` at the `Mobject` layer are out of scope for this page). These style channels are verified by real rendering: the core `set_fill` / `set_stroke` / `set_color` classes work, `set_style`'s multi-stop gradient and sheen take effect, and only the `background_image` texture fill does not.

## VMobject constructor style parameters (the fill/stroke items)
`VMobject(fill_color=None, fill_opacity=0.0, stroke_color=None, stroke_opacity=1.0, stroke_width=4, background_stroke_color=BLACK, background_stroke_opacity=1.0, background_stroke_width=0, sheen_factor=0.0, joint_type=None, sheen_direction=UL, close_new_points=False, cap_style=CapStyleType.AUTO, **kwargs)`: the style parameters you can pass directly when constructing any vector class; they pass all the way through `**kwargs` to the concrete shape.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `fill_color` | `ManimColor` | `None` | fill colour |
| `fill_opacity` | `float` | `0.0` | fill opacity (no fill by default) |
| `stroke_color` | `ManimColor` | `None` | stroke colour |
| `stroke_opacity` | `float` | `1.0` | stroke opacity |
| `stroke_width` | `float` | `4` | stroke width (the global default is `DEFAULT_STROKE_WIDTH = 4`) |
| `background_stroke_color` | `ManimColor` | `BLACK` | background stroke colour (the outer stroke overlaid on a dark background) |
| `background_stroke_opacity` | `float` | `1.0` | background stroke opacity |
| `background_stroke_width` | `float` | `0` | background stroke width |
| `sheen_factor` | `float` | `0.0` | sheen / gradient strength |
| `sheen_direction` | `array-like` | `UL` | sheen direction |
| `joint_type` | `str \| None` | `None` | corner join style (`round`/`miter`/`bevel`) |
| `close_new_points` | `bool` | `False` | whether new points close |
| `cap_style` | `int \| str` | `AUTO` | end-cap style (`round`/`square`/`projecting`) |

## VMobject.set_fill
`set_fill(color=None, opacity=None, family=True)`: set the fill colour and opacity; `opacity=None` means do not change the opacity.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `ManimColor \| list \| None` | `None` | fill colour (a list of colours gives a multi-colour fill) |
| `opacity` | `float \| None` | `None` | fill opacity (0 to 1) |
| `family` | `bool` | `True` | whether to apply it to submobjects |

Paired reads: `get_fill_color()`, `get_fill_opacity()`.

## VMobject.set_stroke
`set_stroke(color=None, width=None, opacity=None, background=False, family=True)`: set the stroke colour, width and opacity; with `background=True` it changes the "background stroke". If you do not want the stroke width to scale along when scaling, use `mob.scale(2, scale_stroke=True)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `ManimColor \| None` | `None` | stroke colour |
| `width` | `float \| None` | `None` | stroke width |
| `opacity` | `float \| None` | `None` | stroke opacity |
| `background` | `bool` | `False` | whether to change the background stroke |
| `family` | `bool` | `True` | whether to apply it to submobjects |

Paired reads: `get_stroke_width()`, `get_stroke_color()`, `get_stroke_opacity()`.

## VMobject.set_style (only `background_image` does not take effect)
`set_style(fill_color=None, fill_opacity=None, stroke_color=None, stroke_width=None, stroke_opacity=None, background_stroke_color=None, background_stroke_width=None, background_stroke_opacity=None, sheen_factor=None, sheen_direction=None, background_image=None, family=True)`: set the whole vector style in one go (a merged version of `set_fill` + `set_stroke` + sheen); items whose parameter is `None` keep their original values.

> Note: sheen (`sheen_factor`/`sheen_direction`) and the **multi-colour / multi-stop gradient fill** are in effect on RTM's Vulkan path — a multi-stop gradient is no longer averaged into a single colour, but takes the first and last stops and runs a native linear gradient (see `render/util.py:220-351`, dedicated test `tests/test_gradient_fill_stops.py`). Only `background_image` (texture fill) does not take effect under RTM.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `fill_color` | `ManimColor \| None` | `None` | fill colour |
| `fill_opacity` | `float \| None` | `None` | fill opacity |
| `stroke_color` | `ManimColor \| None` | `None` | stroke colour |
| `stroke_width` | `float \| None` | `None` | stroke width |
| `stroke_opacity` | `float \| None` | `None` | stroke opacity |
| `background_stroke_color` | `ManimColor \| None` | `None` | background stroke colour |
| `background_stroke_width` | `float \| None` | `None` | background stroke width |
| `background_stroke_opacity` | `float \| None` | `None` | background stroke opacity |
| `sheen_factor` | `float \| None` | `None` | sheen strength |
| `sheen_direction` | `array-like \| None` | `None` | sheen direction |
| `background_image` | `str \| None` | `None` | background texture image path — **RTM's Vulkan path is not wired up for it, so filling it in has no visual effect** |
| `family` | `bool` | `True` | whether to apply it to submobjects |

Paired reads: `get_style(simple=False)`, `match_style(vmobject, family=True)`.

## VMobject.set_color
`set_color(color, family=True)`: change the colour uniformly (a convenient entry point that affects fill and stroke at once, most obvious on `Text`/`Dot` and the like).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | `ManimColor` | required | the new colour |
| `family` | `bool` | `True` | whether to apply it to submobjects |

Paired reads: `get_color()`.

## Example

```python
sq = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)
sq.set_stroke(color=YELLOW, width=8)          # ManimCE equivalent: sq.set_stroke(...)
sq.set_color(GREEN)
```

See also: [VMobject styles (2)](07b-VMobject-Styles-Advanced.md) · [Basic shapes](01-Basic-Shapes.md) · [Containers and grouping](06-Containers-and-Grouping.md)
