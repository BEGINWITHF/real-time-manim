# 二维坐标系 Axes

`Axes` 是由两根 `NumberLine` 组合而成的直角坐标系：`x_range`/`y_range` 定数据范围，`x_length`/`y_length` 定屏幕长度。`c2p`/`p2c` 负责换算，`plot` 画曲线，`get_area` 求面积（换算见[坐标换算](03-坐标换算.md)，曲线见[05-函数曲线](05-函数曲线.md)）。

## 参数

### class Axes

```python
def __init__(self, x_range: Sequence[float] | None = None, y_range: Sequence[float] | None = None,
             x_length: float | None = None, y_length: float | None = None,
             axis_config: dict | None = None, x_axis_config: dict | None = None,
             y_axis_config: dict | None = None, tips: bool = True, **kwargs: Any) -> None:
```

`x_range`/`y_range` 决定**数据范围与刻度步长**，`x_length`/`y_length` 决定**屏幕物理长度**，二者共同决定比例尺（= `x_length / (x_max - x_min)`）。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `x_range` | `Sequence[float] \| None` | `None` → `[-7, 7, 1]` | `[x_min, x_max, x_step]`；两元组自动补 `step=1`；`step` 只影响刻度/标签密度，不影响比例尺 |
| `y_range` | `Sequence[float] \| None` | `None` → `[-4, 4, 1]` | 同上 |
| `x_length` | `float \| None` | `None` → 按帧宽推算（约 12） | x 轴屏幕长度（Manim 单位） |
| `y_length` | `float \| None` | `None` → 按帧高推算（约 6） | y 轴屏幕长度 |
| `axis_config` | `dict \| None` | `{"include_tip": tips, "numbers_to_exclude": [0]}` | 传给**两根** `NumberLine` 的公共参数（`font_size`、`include_numbers`、`scaling`…） |
| `x_axis_config` | `dict \| None` | `{}` | 只作用于 x 轴，与 `axis_config` 合并（后者优先级低） |
| `y_axis_config` | `dict \| None` | `{"rotation": 90*DEGREES, "label_direction": LEFT}` | 只作用于 y 轴（默认转 90°） |
| `tips` | `bool` | `True` | 两轴是否带箭头 |
| `**kwargs` | — | — | 透传 `VGroup`/`CoordinateSystem`（`color`、`stroke_width`…） |

> **返回**：`Axes` 实例。关键语义：0 不在 `[min, max]` 内时坐标系自动平移，使 0 点（或最近端点）落在屏幕中心，`c2p` 依旧正确。常用属性：`x_axis`、`y_axis`、`axes`、`x_range`、`y_range`、`dimension=2`。

#### 样例：`x_range`/`length`/`tips`/`axis_config` 基本构造

范围 `[-4,4]×[-3,3]`、屏幕 `8×5`、去掉轴端箭头、缩小轴上字号，再挂刻度数字、轴名称并画一条抛物线。

```python
from real_time_manim import Scene, Axes, Text, \
    YELLOW, BLUE, GREY_B, UP, DOWN, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class AxesCtorDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-Axes", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1],   #参数 “x_range”/“y_range”：数据范围与刻度步长
                  x_length=8, y_length=5,                   #参数 “x_length”/“y_length”：屏幕物理长度
                  tips=False, axis_config={"font_size": 24})   #参数 “tips”：轴端箭头；“axis_config”：两轴公共参数
        ax.add_coordinates()   #两轴挂刻度数字
        labels = ax.get_axis_labels("x", "y")   #x/y 两个轴名称（需自己加入场景）
        curve = ax.plot(lambda x: 0.5 * x**2, color=BLUE)   #顺手画一条抛物线（参数见 05 页）
        lab = Text("x_range=[-4,4,1]  y_range=[-3,3,1]  tips=False",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #参数说明标签
        win.play(Create(ax), run_time=1.0)   #画出坐标系（含刻度数字）
        win.play(FadeIn(labels), FadeIn(lab), run_time=0.4)   #轴名称与说明标签淡入
        win.play(Create(curve), run_time=1.0)   #画出抛物线
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：先按"数据范围 [-4,4]×[-3,3]、屏幕 8×5"建坐标系，比例尺由此确定（x 方向每数据单位 1 个 Manim 单位，y 方向约 0.83）。`tips=False` 去掉轴端箭头，`axis_config={"font_size": 24}` 把两轴数字统一缩小。

`add_coordinates()` 挂刻度数字（0 处默认排除），`get_axis_labels("x", "y")` 生成两个轴名（返回值要自己加进场景），最后 `plot` 画一条抛物线演示"坐标系上直接画函数"。

<video src="assets/RTM output/02-Axes-ctor.mp4" controls width="560"></video>

> 提醒：
>
> - `get_axis_labels(...)` 的返回值**不会自动进场景**，忘了 `self.add`/`FadeIn` 就是空的。
> - 0 被排除在刻度数字外是 `axis_config` 默认值 `numbers_to_exclude=[0]` 干的，想显示 0 就显式传 `axis_config={"numbers_to_exclude": []}`。

### add_coordinates

```python
def add_coordinates(self, *axes_numbers: Iterable[float] | None | dict, **kwargs) -> Self
```

给坐标轴加刻度数字或自定义标签，按轴顺序逐个接收参数：

- 不传参数：全部轴用默认数字
- `None`：该轴保持默认
- `list`：只显示这些数值
- `dict`：数值映射成任意标签

标签用 `ax.coordinate_labels`（`VGroup`）取回。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `*axes_numbers` | `Iterable[float] \| None \| dict` | 全部 `None` | 按轴顺序（x, y, [z]）逐个给出，`None`=默认数字，`list`=指定数值，`dict`=数值→标签 |
| `**kwargs` | — | — | 透传 `NumberLine.add_numbers`/`add_labels`（如 `font_size`） |

> **返回**：`Self`（链式调用）。

#### 样例：`add_coordinates` 的 list / dict 写法

x 轴用 dict 把数值 1/2 映射成 "Mon"/"Tue"，y 轴用 list 只显示 -2/0/2 三个数；不传参数的轴保持默认数字。

```python
from real_time_manim import Scene, Axes, Text, \
    YELLOW, GREY_B, UP, DOWN, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class AxesAddCoordDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-add_coordinates", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 2, 1], x_length=9, y_length=5)   #默认 tips=True（轴端带箭头）
        ax.add_coordinates({1: "Mon", 2: "Tue"}, [-2, 0, 2])   #“add_coordinates”：x 轴 dict 数值->标签，y 轴 list 只显指定数值
        labels = ax.get_axis_labels("x", "y")   #轴名称
        lab = Text("add_coordinates({1:Mon,2:Tue}, [-2,0,2])",
                   font_size=24, color=GREY_B).to_edge(DOWN)   #参数说明标签
        win.play(Create(ax), run_time=0.9)   #画出坐标系（含箭头与自定义标签）
        win.play(FadeIn(labels), FadeIn(lab), run_time=0.4)   #轴名称与说明标签淡入
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：`add_coordinates` 按轴顺序逐个接收参数——x 轴收到 dict，数值 1/2 处显示 "Mon"/"Tue"（其余刻度不再挂数字）；y 轴收到 list `[-2, 0, 2]`，只在这三个刻度下挂数字。想全默认就整段不传参数，想某轴不动就传 `None`。

<video src="assets/RTM output/02-Axes-addcoordinates.mp4" controls width="560"></video>

> 提醒：
>
> - dict 的 `str` 值走 `MathTex`（数学斜体），要正体可以传 `Tex`/`Text` 对象。
> - `add_coordinates` 会**覆盖**同轴已有的数字，重复调用前先把 `ax.coordinate_labels` 移除，否则新旧标签叠在一起。

### 取轴：get_axis / get_axes / get_x_axis / get_y_axis / get_origin / get_*_unit_size（只留表格）

```python
def get_axis(self, index: int) -> NumberLine
def get_axes(self) -> VGroup
def get_x_axis(self) -> NumberLine
def get_y_axis(self) -> NumberLine
def get_origin(self) -> Point3D
def get_x_unit_size(self) -> float
def get_y_unit_size(self) -> float
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `index` | `int` | 必填 | `0`=x，`1`=y；`get_origin()` 返回 `(0,0)` 的场景点，`get_*_unit_size()` 返回 1 个数据单位的屏幕长度（比例尺） |

### 轴标签：get_axis_labels / get_x_axis_label / get_y_axis_label（只留表格）

```python
def get_axis_labels(self, x_label: float | str | Mobject = "x", y_label: float | str | Mobject = "y") -> VGroup
def get_x_axis_label(self, label, edge=UR, direction=UR, buff=0.1, **kwargs) -> Mobject
def get_y_axis_label(self, label, edge=UR, direction=UP * 0.5 + RIGHT, buff=0.1, **kwargs) -> Mobject
```

一次生成 x/y 两个标签（存 `ax.axis_labels`），或用单个方法精确控制位置；**返回的标签需要自己 `self.add(...)`**（见上面样例里的 `FadeIn(labels)`）。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `x_label` / `y_label` / `label` | `float \| str \| Mobject` | `"x"` / `"y"` | `str`/`float` 用 `MathTex` 生成，也可直接传 `Tex`/`Text` |
| `edge` | `Vector3D` | `UR` | 标签贴靠的轴边缘 |
| `direction` | `Vector3D` | 见签名 | 相对 `edge` 的进一步摆放方向 |
| `buff` | `float` | `0.1` | 与轴的距离 |
| `**kwargs` | — | — | 透传（`ThreeDAxes` 版还支持 `rotation`、`rotation_axis`） |

---

相关：[坐标换算](03-坐标换算.md) · [引导线与折线图](02b-引导线与折线图.md) · [绘制函数曲线](05-函数曲线.md) · [数轴 NumberLine](01-NumberLine.md)
