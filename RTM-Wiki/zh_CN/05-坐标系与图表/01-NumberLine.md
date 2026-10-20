# 数轴 NumberLine

一根带刻度的直线：`NumberLine` 是 `Axes` / `NumberPlane` / `BarChart` 每根轴的底层实现，也可单独拿来当时间轴、数轴点移动动画；本页讲构造参数，方法（`n2p`、`add_numbers`、`add_labels`…）在[数轴方法进阶](01b-数轴方法进阶.md)。

## 参数

### class NumberLine

```python
def __init__(self, x_range: Sequence[float] | None = None, length: float | None = None,
             unit_size: float = 1, include_ticks: bool = True, tick_size: float = 0.1,
             numbers_with_elongated_ticks: Iterable[float] | None = None,
             longer_tick_multiple: int = 2, exclude_origin_tick: bool = False,
             rotation: float = 0, stroke_width: float = 2.0, include_tip: bool = False,
             tip_width: float = 0.35, tip_height: float = 0.35,
             tip_shape: type[ArrowTip] | None = None, include_numbers: bool = False,
             font_size: float = 36, label_direction: Point3DLike = DOWN,
             label_constructor: type = MathTex, scaling: _ScaleBase = LinearBase(),
             line_to_number_buff: float = 0.25, decimal_number_config: dict | None = None,
             numbers_to_exclude: Iterable[float] | None = None,
             numbers_to_include: Iterable[float] | None = None, **kwargs: Any) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `x_range` | `Sequence[float] \| None` | `None` → `[-7, 7, 1]` | `[x_min, x_max, x_step]`，只给两元组自动补 `step=1`；`step` 决定刻度/数字标签疏密 |
| `length` | `float \| None` | `None` | 数轴总长度（Manim 单位），给定后覆盖 `unit_size` 并反推它 |
| `unit_size` | `float` | `1` | 相邻整数刻度间距，未指定 `length` 时生效 |
| `include_ticks` | `bool` | `True` | 是否画刻度线 |
| `tick_size` | `float` | `0.1` | 刻度线长度 |
| `numbers_with_elongated_ticks` | `Iterable[float] \| None` | `None` | 需要加长刻度的数值，如 `[-2, 4]` |
| `longer_tick_multiple` | `int` | `2` | 加长刻度是普通刻度的倍数 |
| `exclude_origin_tick` | `bool` | `False` | 是否去掉 0 处刻度（`Axes` 线性轴默认置 `True`） |
| `rotation` | `float` | `0` | 整条数轴的旋转角（弧度） |
| `stroke_width` | `float` | `2.0` | 线宽 |
| `include_tip` | `bool` | `False` | 末端是否加箭头 |
| `tip_width` | `float` | `0.35` | 箭头宽度 |
| `tip_height` | `float` | `0.35` | 箭头高度 |
| `tip_shape` | `type[ArrowTip] \| None` | `None` | 箭头类（如 `StealthTip`），`None` 用默认箭头 |
| `include_numbers` | `bool` | `False` | 是否在 `label_direction` 方向显示数字标签 |
| `font_size` | `float` | `36` | 数字/标签字号 |
| `label_direction` | `Point3DLike` | `DOWN` | 标签相对数轴的方向 |
| `label_constructor` | `type` | `MathTex` | 标签文本类（`MathTex`/`Tex`/`Text`…） |
| `scaling` | `_ScaleBase` | `LinearBase()` | 刻度缩放方式，对数轴传 `LogBase()`（见[刻度与缩放](10-刻度与缩放.md)） |
| `line_to_number_buff` | `float` | `0.25` | 标签与数轴的距离 |
| `decimal_number_config` | `dict \| None` | 自动 | 传给 `DecimalNumber`，默认小数位由 `step` 推断 |
| `numbers_to_exclude` | `Iterable[float] \| None` | `None` | 不显示这些数值的标签 |
| `numbers_to_include` | `Iterable[float] \| None` | `None` | 只显示这些数值的标签（传入即触发加数字，无需 `include_numbers=True`） |
| `**kwargs` | — | — | 透传给 `Line`（`color`、`stroke_opacity` 等） |

> **返回**：`NumberLine` 实例（`VMobject`）。构造后常用属性：`numbers`（数字组）、`labels`、`ticks`、`x_range`/`x_min`/`x_max`/`x_step`、`unit_size`、`scaling`。

> `x_range` 同时含正负值时，刻度从 0 起算，`min`/`max` 处**不一定**有刻度（取决于 `step`）。

#### 样例：`x_range`/`length`/`include_tip`/`include_numbers` 基本构造

最常用的四个参数一次到位：数据范围 `[-4,4]`、总长 `8`、带箭头、带数字；红点用 `n2p` 沿轴移动。

```python
from real_time_manim import Scene, NumberLine, Dot, Text, \
    YELLOW, RED, GREY_B, UP, DOWN, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class NumberLineBasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-NumberLine", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        line = NumberLine(x_range=[-4, 4, 1], length=8,   #参数 “x_range”：数据范围与步长；“length”：总长 8
                         include_numbers=True, include_tip=True)   #参数 “include_numbers”/“include_tip”：数字标签 + 末端箭头
        dot = Dot(line.n2p(2), color=RED)   #用 “n2p” 把数值 2 换成场景点（见 01b）
        lab = Text("x_range=[-4,4,1]  length=8  tip+numbers",
                   font_size=26, color=GREY_B).next_to(line, DOWN, buff=0.6)   #参数说明标签
        win.play(Create(line), run_time=0.8)   #画出整条数轴（含刻度、数字、箭头）
        win.play(FadeIn(dot), FadeIn(lab), run_time=0.4)   #红点与标签淡入
        win.play(dot.animate.move_to(line.n2p(-3)), run_time=1.0)   #红点沿轴移到数值 -3
        win.play(dot.animate.move_to(line.n2p(3.5)), run_time=1.0)   #再移到数值 3.5（刻度之间也能停）
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：先画一条从 -4 到 4、总长 8 个 Manim 单位的数轴——`x_range` 定数据范围和刻度步长，`length` 定屏幕长度（两者共同决定比例尺），`include_numbers=True` 在轴下方自动挂数字，`include_tip=True` 在右端补箭头。然后红点用 `n2p(2)` 落在数值 2 上，再依次平移到 -3 和 3.5——`n2p` 就是"数值 → 场景点"的换算器。

<video src="assets/RTM output/01-NumberLine-basic.mp4" controls width="560"></video>

> 提醒：给了 `length` 就别再纠结 `unit_size`——它会被反推覆盖。箭头会画在 `x_max` 之外，所以别把红点/标签正好放在 `x_max` 上，会和箭头叠住。数轴数字默认走 `MathTex`：**已安装 `real-time-manim[typst]` extra（且未设 `RTM_TYPST=0`）时由 Typst 后端编译，否则为真实 LaTeX**；要纯文本观感可以传 `label_constructor=Text`。

### UnitInterval

```python
def __init__(self, unit_size: float = 10, numbers_with_elongated_ticks: list[float] | None = None,
             decimal_number_config: dict | None = None, **kwargs: Any) -> None:
```

`[0, 1]` 区间专用数轴（`NumberLine` 子类，拥有其全部方法）：步长 0.1、一位小数、0 和 1 处刻度加长，画概率区间、贝叶斯图的基础件。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `unit_size` | `float` | `10` | 单位长度（比普通数轴长，铺满画面） |
| `numbers_with_elongated_ticks` | `list[float] \| None` | `[0, 1]` | 加长刻度的位置 |
| `decimal_number_config` | `dict \| None` | `{"num_decimal_places": 1}` | 数字格式 |
| `**kwargs` | — | — | 透传 `NumberLine`（`x_range` 等也会被透传覆盖） |

> **返回**：`UnitInterval` 实例。

#### 样例：`UnitInterval` 默认外观

默认参数直接可用：0~1 铺满 10 个单位、0.1 步长刻度、一位小数标签、两端刻度加长。

```python
from real_time_manim import Scene, UnitInterval, Text, \
    YELLOW, GREY_B, UP, DOWN, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class UnitIntervalDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-UnitInterval", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        line = UnitInterval(unit_size=10)   #参数 “unit_size”：0~1 铺满 10 个 Manim 单位
        line.add_numbers()   #步长 0.1 自动出一位小数标签，0/1 处刻度加长
        lab = Text("UnitInterval(unit_size=10)", font_size=28,
                   color=GREY_B).next_to(line, DOWN, buff=0.6)   #参数说明标签
        win.play(Create(line), run_time=0.8)   #画出 [0,1] 专用数轴
        win.play(FadeIn(lab), run_time=0.4)   #标签淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：`UnitInterval(unit_size=10)` 画出 [0,1] 专用数轴，`add_numbers()` 在每个 0.1 刻度下挂一位小数的数字，0 和 1 处的刻度默认加长一倍。和手写 `NumberLine(x_range=[0,1,0.1], ...)` 相比，它把"加长端点刻度 + 小数标签"这两件事默认配好了。

<video src="assets/RTM output/01-NumberLine-unitinterval.mp4" controls width="560"></video>

> 提醒：`UnitInterval` 的 `x_range` 依然可以被 `**kwargs` 覆盖，但覆盖后它就不是"单位区间"了，不如直接用 `NumberLine`。轴上数字走 `MathTex`（**装了 `real-time-manim[typst]` extra 且未设 `RTM_TYPST=0` 时由 Typst 后端编译，否则为真实 LaTeX**），与 CE 的 LaTeX 字形略有差异属正常。

---

相关：[数轴方法进阶](01b-数轴方法进阶.md) · [二维坐标系](02-Axes.md) · [刻度与缩放](10-刻度与缩放.md)
