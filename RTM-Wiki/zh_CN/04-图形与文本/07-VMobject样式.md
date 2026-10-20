# VMobject 样式（一）：填充、描边与整体样式

> 状态：部分验证 —— `set_fill` / `set_stroke` / `set_color` 核心类已实渲染验证（2026-10-11，引擎原生样式通道）；`set_style`（多 stop 渐变 / sheen 已生效，专项 `tests/test_gradient_fill_stops.py`；仅 `background_image` 纹理填充不生效）

以下方法定义在 `mobject/types/vectorized_mobject.py` 的 `VMobject` 上，**对所有形状/文本/矩阵/表格通用**（`Mobject` 层的 `scale`/`rotate`/`shift` 不在本页范围）。

## VMobject 构造样式参数（fill/stroke 项）
`VMobject(fill_color=None, fill_opacity=0.0, stroke_color=None, stroke_opacity=1.0, stroke_width=4, background_stroke_color=BLACK, background_stroke_opacity=1.0, background_stroke_width=0, sheen_factor=0.0, joint_type=None, sheen_direction=UL, close_new_points=False, cap_style=CapStyleType.AUTO, **kwargs)`：所有矢量类构造时可直接传的样式参数，随 `**kwargs` 一路透传给具体形状。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `fill_color` | `ManimColor` | `None` | 填充色 |
| `fill_opacity` | `float` | `0.0` | 填充不透明度（默认不填充） |
| `stroke_color` | `ManimColor` | `None` | 描边色 |
| `stroke_opacity` | `float` | `1.0` | 描边不透明度 |
| `stroke_width` | `float` | `4` | 描边宽度（全局默认 `DEFAULT_STROKE_WIDTH = 4`） |
| `background_stroke_color` | `ManimColor` | `BLACK` | 背景描边色（叠加在深色背景上的外描边） |
| `background_stroke_opacity` | `float` | `1.0` | 背景描边不透明度 |
| `background_stroke_width` | `float` | `0` | 背景描边宽度 |
| `sheen_factor` | `float` | `0.0` | 光泽/渐变强度 |
| `sheen_direction` | `array-like` | `UL` | 光泽方向 |
| `joint_type` | `str \| None` | `None` | 折角连接方式（`round`/`miter`/`bevel`） |
| `close_new_points` | `bool` | `False` | 新点是否闭合 |
| `cap_style` | `int \| str` | `AUTO` | 端点样式（`round`/`square`/`projecting`） |

## VMobject.set_fill
`set_fill(color=None, opacity=None, family=True)`：设置填充色与不透明度；`opacity=None` 表示不改透明度。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `color` | `ManimColor \| list \| None` | `None` | 填充色（可传颜色列表做多色填充） |
| `opacity` | `float \| None` | `None` | 填充不透明度（0~1） |
| `family` | `bool` | `True` | 是否应用到子对象 |

配对读取：`get_fill_color()`、`get_fill_opacity()`。

## VMobject.set_stroke
`set_stroke(color=None, width=None, opacity=None, background=False, family=True)`：设置描边颜色、宽度与不透明度；`background=True` 时改的是"背景描边"。缩放时若不希望线宽跟着放大，用 `mob.scale(2, scale_stroke=True)`。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `color` | `ManimColor \| None` | `None` | 描边颜色 |
| `width` | `float \| None` | `None` | 描边宽度 |
| `opacity` | `float \| None` | `None` | 描边不透明度 |
| `background` | `bool` | `False` | 是否修改背景描边 |
| `family` | `bool` | `True` | 是否应用到子对象 |

配对读取：`get_stroke_width()`、`get_stroke_color()`、`get_stroke_opacity()`。

## VMobject.set_style（仅 `background_image` 不生效）
`set_style(fill_color=None, fill_opacity=None, stroke_color=None, stroke_width=None, stroke_opacity=None, background_stroke_color=None, background_stroke_width=None, background_stroke_opacity=None, sheen_factor=None, sheen_direction=None, background_image=None, family=True)`：一次性设置全部矢量样式（`set_fill` + `set_stroke` + 光泽的合并版），参数为 `None` 的项保持原值。

> 状态说明：sheen（`sheen_factor`/`sheen_direction`）与**多色/多 stop 渐变填充**在 RTM 的 Vulkan 路径上已生效（多 stop 渐变不再被平均成单色，取首尾 stop 走 native 线性渐变，见 `render/util.py:220-351`，专项 `tests/test_gradient_fill_stops.py`）；只有 `background_image`（纹理填充）在 RTM 下不生效。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `fill_color` | `ManimColor \| None` | `None` | 填充色 |
| `fill_opacity` | `float \| None` | `None` | 填充不透明度 |
| `stroke_color` | `ManimColor \| None` | `None` | 描边色 |
| `stroke_width` | `float \| None` | `None` | 描边宽度 |
| `stroke_opacity` | `float \| None` | `None` | 描边不透明度 |
| `background_stroke_color` | `ManimColor \| None` | `None` | 背景描边色 |
| `background_stroke_width` | `float \| None` | `None` | 背景描边宽度 |
| `background_stroke_opacity` | `float \| None` | `None` | 背景描边不透明度 |
| `sheen_factor` | `float \| None` | `None` | 光泽强度 |
| `sheen_direction` | `array-like \| None` | `None` | 光泽方向 |
| `background_image` | `str \| None` | `None` | 背景纹理图路径——**RTM 的 Vulkan 路径不接线，填了无视觉效果** |
| `family` | `bool` | `True` | 是否应用到子对象 |

配对读取：`get_style(simple=False)`、`match_style(vmobject, family=True)`。

## VMobject.set_color
`set_color(color, family=True)`：统一改颜色（对填充+描边同时生效的便捷入口，对 `Text`/`Dot` 等最直观）。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `color` | `ManimColor` | 必填 | 新颜色 |
| `family` | `bool` | `True` | 是否应用到子对象 |

配对读取：`get_color()`。

## 示例

```python
sq = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)
sq.set_stroke(color=YELLOW, width=8)          # ManimCE 等价：sq.set_stroke(...)
sq.set_color(GREEN)
```

相关：[VMobject 样式（二）](07b-VMobject样式进阶.md) · [基本形状](01-基本形状.md) · [容器与组合](06-容器与组合.md)
