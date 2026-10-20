# 概率与采样空间 SampleSpace

RTM 走通用矢量回退出图（2026-10-11 实渲染验证，回退能正确画出）。手册第九节实际条目只有 `SampleSpace`（未收录 `Tree`、`Bayes` 等其它概率 mobject）。

## SampleSpace

`SampleSpace(height=3, width=3, fill_color=DARK_GREY, fill_opacity=1, stroke_width=0.5, stroke_color=LIGHT_GREY, default_label_scale_val=1)`

二维矩形"样本空间"图块（概率论视频里的方框），可按概率列表水平/垂直切分成若干子块，并配花括号与文字标注；`Rectangle` 子类，`sample_space[i]` 可索引取第 i 块。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `height` / `width` | `float` | `3` / `3` | 尺寸 |
| `fill_color` | `ParsableManimColor` | `DARK_GREY` | 填充色 |
| `fill_opacity` | `float` | `1` | 不透明度 |
| `stroke_width` | `float` | `0.5` | 描边宽度 |
| `stroke_color` | `ParsableManimColor` | `LIGHT_GREY` | 描边颜色 |
| `default_label_scale_val` | `float` | `1` | 标签缩放系数 |

## 方法一览

| 方法 | 签名 | 频率 | 作用 |
| --- | --- | --- | --- |
| `add_title` | `(title="Sample space", buff=0.25) -> None` | 🟡 | 在上方加 `Tex` 标题（过宽会自动缩到与方框同宽） |
| `divide_horizontally` | `(*args, **kwargs) -> None` | 🟡 | 水平切分，结果存 `horizontal_parts` 并 `add` 进自身 |
| `divide_vertically` | `(*args, **kwargs) -> None` | 🟡 | 垂直切分，结果存 `vertical_parts` |
| `get_horizontal_division` | `(p_list, colors=[GREEN_E, BLUE_E], vect=DOWN) -> VGroup` | ⚪ | 只生成水平切块不加入 |
| `get_vertical_division` | `(p_list, colors=[MAROON_B, YELLOW], vect=RIGHT) -> VGroup` | ⚪ | 只生成垂直切块不加入 |
| `get_division_along_dimension` | `(p_list, dim, colors, vect) -> VGroup` | ⚪ | 通用切分（`dim`: 0=垂直, 1=水平） |
| `complete_p_list` | `(p_list) -> list[float]` | ⚪ | 概率和不足 1 时自动补余量 |
| `add_label` | `(label) -> None` | ⚪ | 记录一个标签字符串到 `self.label`（不生成 mobject） |
| `get_side_braces_and_labels` | `(labels, direction=LEFT, **kwargs) -> VGroup` | 不支持 | 给 `horizontal_parts` 加花括号与标签。**上游 manim 0.21 有 bug，调用即崩**（见下） |
| `get_top_braces_and_labels` | `(labels, **kwargs) -> VGroup` | 不支持 | 同上（`vertical_parts` 顶部加括号） |
| `get_bottom_braces_and_labels` | `(labels, **kwargs) -> VGroup` | 不支持 | 同上（底部） |
| `get_subdivision_braces_and_labels` | `(parts, labels, direction, buff=0.1, min_num_quads=1) -> VGroup` | 不支持 | 三者通用版；崩因就在它身上（见下） |

> **上面四个「花括号 + 标签」helper 在 manim 0.21 里全都用不了**（两引擎一致）：
> `get_subdivision_braces_and_labels` 把 `min_num_quads` 透传给 `Brace(...)`
> （`manim/mobject/graphing/probability.py:159`），而 0.21 的 `Brace` 已没有这个形参，
> 于是抛 `TypeError: Mobject.__init__() got an unexpected keyword argument 'min_num_quads'`。
> 想要花括号标签请**自己 `Brace(part, direction)` + `brace.get_text(...)`**，本页样例就是这么做的。
| `add_braces_and_labels` | `() -> None` | ⚪ | 把已生成的括号与标签并入自身 |

## 参数（切分类）

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `p_list` | `float \| Iterable[float]` | 必填 | 各块占比（和 < 1 时自动补 `1-sum`） |
| `colors` | `Sequence[ParsableManimColor]` | 见方法表 | 配色（会做 `color_gradient` 渐变） |
| `vect` | `Vector3D` | 见方法表 | 切分/标签的朝向 |
| `labels` | `list[str \| VMobject]` | 必填 | 每块的标签 |
| `buff` | `float` | `0.1` | 括号间距 |
| `min_num_quads` | `int` | `1` | 花括号细分段数 |

## 样例 1：`divide_vertically` + 花括号标签

`divide_vertically(p_list, colors, vect)` 按概率列表把方框竖着切成几块，结果存进 `poly.vertical_parts` 并 `add` 进自身；`poly[i]` 也能直接索引第 i 块。样例切出 0.37 / 0.13 / 0.50 三块，再给首尾两块挂 `Brace` + 数值标签。

```python
import numpy as np
from real_time_manim import (
    BLACK, BLUE_E, Brace, Create, DOWN, FadeIn, GRAY, GREEN_E, GREY_B, LEFT,
    RIGHT, SampleSpace, Scene, Text, UP, WHITE, YELLOW, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class VerticalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09-SampleSpace", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        poly = SampleSpace(width=2, height=2, stroke_width=5, fill_opacity=0.1)   #样本空间方框
        poly.divide_vertically(   #“divide_vertically”：按概率列表垂直切块
            p_list=np.array([0.37, 0.13, 0.5]),   #参数 “p_list”：各块占比（和不足 1 自动补余量）
            colors=[BLACK, WHITE, GRAY],   #参数 “colors”：配色（自动做渐变）
            vect=RIGHT)   #参数 “vect”：切分方向
        poly.add_title("Sample space")   #“add_title”：方框上方的标题
        win.play(Create(poly), run_time=0.8)   #画出方框与切块
        win.play(Wait(0.5))   #进行 0.5s 的等待

        b0 = Brace(poly.vertical_parts[0], LEFT)   #给第 0 块在左侧挂花括号
        t0 = b0.get_text("0.37")   #“get_text”：花括号旁的标签
        b2 = Brace(poly.vertical_parts[2], RIGHT)   #最右一块在右侧挂
        t2 = b2.get_text("0.50")
        win.play(FadeIn(b0), FadeIn(t0), run_time=0.4)   #左右两个标签依次淡入
        win.play(FadeIn(b2), FadeIn(t2), run_time=0.4)
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：`divide_vertically` 按 `p_list` 的比例把宽度分掉，`colors` 只有 3 个 → 每块一色（多于 3 块时用 `color_gradient` 插值）；`add_title` 用 `Tex` 在方框上方写标题（过宽会自动缩到与方框同宽）。花括号是标准 `Brace`：贴在 `vertical_parts[i]` 的左侧/右侧，`get_text` 给出旁边那行标签。

<video src="assets/RTM output/09-概率与SampleSpace-basic.mp4" controls width="560"></video>

> 提醒：`add_title` 内部是 `Tex(title)`，**标题里别写 `_`**（数学模式下标，会 `Missing $ inserted`)；要下划线得转义或改用 `Text`。`p_list` 的和只要 ≤1，不足部分由 `complete_p_list` 自动补成最后一块。

## 样例 2：`divide_horizontally` + 占比不足自动补余量

`divide_horizontally` 是同一套逻辑的横向版本，结果存 `grid.horizontal_parts`。样例只给 `[0.4, 0.25]`，剩下的 0.35 自动补成第三块。

```python
import numpy as np
from real_time_manim import (
    BLACK, BLUE_E, Brace, Create, DOWN, FadeIn, GRAY, GREEN_E, GREY_B, LEFT,
    RIGHT, SampleSpace, Scene, Text, UP, WHITE, YELLOW, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class HorizontalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09-divide_horizontally", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        grid = SampleSpace(height=2.5, width=3, fill_opacity=0.6)   #更扁的样本空间
        grid.divide_horizontally(   #“divide_horizontally”：按概率列表水平切块
            p_list=[0.4, 0.25],   #只给两块 = 0.65，剩余 0.35 由 complete_p_list 自动补成第三块
            colors=[GREEN_E, BLUE_E],
            vect=DOWN)   #参数 “vect”：切分方向
        grid.add_title("horizontal division")   #标题写明切分方式（Tex 里别写 `_`）
        win.play(Create(grid), run_time=0.8)   #画出三块
        win.play(Wait(0.5))   #进行 0.5s 的等待

        labels = ["0.40", "0.25", "0.35"]
        braces = [Brace(grid.horizontal_parts[i], LEFT) for i in range(3)]   #每行左侧一个花括号
        texts = [braces[i].get_text(labels[i]) for i in range(3)]
        win.play(*[FadeIn(b) for b in braces], run_time=0.4)   #三个花括号一起淡入
        win.play(*[FadeIn(t) for t in texts], run_time=0.4)   #三个标签一起淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：横向切分后 `horizontal_parts` 从上到下排列；`colors=[GREEN_E, BLUE_E]` 只给两色 → 三块做渐变上色。`complete_p_list` 把不足 1 的部分补到末尾，所以第三块的标签是自动算出的 `0.35`。

<video src="assets/RTM output/09-概率与SampleSpace-horizontal.mp4" controls width="560"></video>

> 提醒：`horizontal_parts[i]` 是**子块 mobject**，可以直接 `Brace` / 上色 / 做动画；`parts.braces`、`parts.labels` 只有走那四个（在 0.21 里坏掉的）helper 才会被写上。

相关：[图表 BarChart](08-图表BarChart.md) · [容器与组合](../04-图形与文本/06-容器与组合.md) · [布尔运算](../04-图形与文本/05-布尔运算.md)
