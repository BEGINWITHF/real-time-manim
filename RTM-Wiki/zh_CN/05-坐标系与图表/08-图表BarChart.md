# 图表 BarChart

RTM 走通用矢量回退出图（2026-10-11 实渲染验证，回退能正确画出）。柱状图继承 `Axes`，所以 `c2p`、`plot`、`get_area`、`x_axis_config` / `y_axis_config` 全部可用。

## BarChart

`BarChart(values, bar_names=None, y_range=None, x_length=None, y_length=None, bar_colors=["#003f5c", "#58508d", "#bc5090", "#ff6361", "#ffa600"], bar_width=0.6, bar_fill_opacity=0.7, bar_stroke_width=3, **kwargs)`

构造时自动铺柱子、给 y 轴加数字、给 x 轴加 `bar_names` 标签。内部固定 `x_range=[0, len(values), 1]`、`tips=False`；x 轴默认 `font_size=24`、`label_constructor=Tex`。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `values` | `MutableSequence[float]` | 必填 | 每根柱子的值，**可为负** |
| `bar_names` | `Sequence[str] \| None` | `None` | x 轴标签；比 `values` 短没问题，比 `values` **长会索引越界**；负值柱标签自动放到轴上方 |
| `y_range` | `Sequence[float] \| None` | 自动 `[min(0,min(v)), max(0,max(v)), round(max(v)/y_length, 2)]` | y 轴范围与步长；给两元组会自动补步长 |
| `x_length` | `float \| None` | `min(len(values), frame_width-2)` | x 轴长度 |
| `y_length` | `float \| None` | `frame_height - 4`（=4） | y 轴长度 |
| `bar_colors` | `Iterable[str]` | 5 色调色板（见签名） | 柱色；长度与 `values` 不同时自动插值渐变；**必须传列表**（传 `str` 会在 v0.17 后移除并告警） |
| `bar_width` | `float` | `0.6` | 柱宽（0~1，占格子的比例） |
| `bar_fill_opacity` | `float` | `0.7` | 填充不透明度 |
| `bar_stroke_width` | `float` | `3` | 柱子描边宽度 |
| `**kwargs` | — | — | 透传 `Axes`：`x_axis_config`、`y_axis_config`、`y_range` 等 |

关键属性：`bars`（`VGroup[Rectangle]`）、`values`、`bar_names`、`bar_colors`、`x_labels`、`bar_labels`。

## BarChart.get_bar_labels

`BarChart.get_bar_labels(color=None, font_size=24, buff=0.25, label_constructor=Tex) -> VGroup`

给每根柱子顶端加数值标签（正柱在上、负柱在下）。**只返回不自动加入**，必须自己 `self.add(...)`；也不会写回 `chart.bar_labels`（该属性构造时为 `None`），请把返回值存到变量。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `color` | `ParsableManimColor \| None` | `None`（跟随柱子填充色） | 标签颜色 |
| `font_size` | `float` | `24` | 字号 |
| `buff` | `float` | `0.25` | 与柱子的距离 |
| `label_constructor` | `type[MathTex]` | `Tex` | 文本类（想要数学字体传 `MathTex`） |

## BarChart.change_bar_values

`BarChart.change_bar_values(values, update_colors=True) -> None`

**就地**更新柱高（不重新建图），是做"数值增长"动画（`Transform` / `always_redraw`）的核心方法。新 `values` 长度不必与原值相同（超出部分忽略），原柱高为 0 时会重建该柱。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `values` | `Iterable[float]` | 必填 | 新的柱值 |
| `update_colors` | `bool` | `True` | 是否按 `bar_colors` 重新渐变上色 |

## 样例 1：构造 + `get_bar_labels`

构造时自动铺柱子、给 y 轴加数字、给 x 轴加 `bar_names` 标签；`get_bar_labels` 另外**返回**柱顶数值标签。样例用带负值的 `values` 让负柱自动朝下，`y_range` 只给两元组，步长自动补。

```python
from real_time_manim import (
    BarChart, DOWN, FadeIn, GREY_B, Scene, Text, UP, WHITE, YELLOW,
    Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class BasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("08-BarChart", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        chart = BarChart(values=[-4, 6, -2, 3],   #参数 “values”：可为负，负值柱自动朝下
                         bar_names=["one", "two", "three", "four"],   #参数 “bar_names”：x 轴标签
                         y_range=[-7, 9, 2],   #参数 “y_range”：给两元组自动补步长
                         y_length=5.5, x_length=10,   #两轴屏幕长度
                         x_axis_config={"font_size": 24})   #透传 Axes：x 轴刻度字号
        labels = chart.get_bar_labels(color=WHITE, font_size=24)   #“get_bar_labels”：柱顶数值标签（只返回，要自己 add）
        win.play(FadeIn(chart), run_time=0.8)   #整套坐标系与柱体淡入
        win.play(FadeIn(labels), run_time=0.4)   #数值标签淡入
        win.play(Wait(0.8))   #进行 0.8s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：

- `BarChart` 继承 `Axes`，构造时把 `values` 变成一排 `Rectangle`（`chart.bars`），负值柱向下画；y 轴刻度数字与 x 轴 `bar_names` 标签一起生成（`label_constructor` 默认 `Tex`）。
- `get_bar_labels()` 再按每根柱的顶端（负柱则在底端）生成一个数值标签 `VGroup`——**只返回不自动上屏**，样例里显式 `FadeIn(labels)`。

<video src="assets/RTM output/08-图表BarChart-basic.mp4" controls width="560"></video>

> 提醒：
>
> - `bar_names` 比 `values` **长会索引越界**（短没关系）。
> - `get_bar_labels` 的返回值不会写回 `chart.bar_labels`（该属性构造时为 `None`），要自己存变量再上屏。

## 样例 2：`change_bar_values` 就地改柱高

`change_bar_values(values)` **就地**换柱高、不重建图表；沿 `.animate` 播就是平滑长高 / 缩矮。样例从 `[3, 4, 2]` 依次变到 `[7, 5, 3]`、`[1, 2, 9]`。

```python
from real_time_manim import (
    BarChart, DOWN, FadeIn, GREY_B, Scene, Text, UP, WHITE, YELLOW,
    Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class ChangeValuesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("08-change_bar_values", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        chart = BarChart(values=[3, 4, 2],   #起始柱高
                         bar_names=["A", "B", "C"],
                         y_range=[0, 10, 2],
                         y_length=5, x_length=9,
                         x_axis_config={"font_size": 24})
        lab = Text("chart.animate.change_bar_values(...)", font_size=24,
                   color=GREY_B).to_edge(UP).shift(DOWN * 0.9)   #参数说明放到标题下方
        win.play(FadeIn(chart), FadeIn(lab), run_time=0.8)   #坐标系与说明一起出场
        win.play(chart.animate.change_bar_values([7, 5, 3]),   #“change_bar_values”：就地换柱高
                 run_time=1.0)   #沿 .animate 平滑过渡
        win.play(chart.animate.change_bar_values([1, 2, 9]),
                 run_time=1.0)   #再换一次
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：`change_bar_values` 本身是同步方法，直接调只会在下一帧瞬变。样例用 `chart.animate.change_bar_values(...)` 把它包成动画，柱子的高度与颜色在 1 秒里连续插值。

这是做「数值增长」类动画的核心手法，配合 `always_redraw` / `ValueTracker` 可以逐帧跟随。

<video src="assets/RTM output/08-图表BarChart-changevalues.mp4" controls width="560"></video>

> 提醒：
>
> - 新 `values` 长度**不必**与原值相同（超出部分忽略，原高为 0 的柱子会重建）。
> - `update_colors=True`（默认）会按 `bar_colors` 重新渐变上色。

相关：[二维坐标系](02-Axes.md) · [坐标换算](03-坐标换算.md) · [面积与黎曼矩形](06-面积与黎曼矩形.md)
