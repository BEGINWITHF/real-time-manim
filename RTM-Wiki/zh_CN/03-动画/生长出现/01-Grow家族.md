# 生长出现：Grow 家族（从点 / 中心 / 边）

整族在 RTM 自有实现里继承自 `GrowFromPoint(GrowArrow) ← GrowArrow(Animation)`，语义统一：**从 0 尺寸在指定点长大**，可选把初始颜色设为 `point_color`。三个成员只差"从哪儿长"：指定点、自身中心、包围盒的某条边。

## 参数

### `GrowFromPoint`

```python
GrowFromPoint(mobject, point, point_color=None, **kwargs)
```

对象从**指定点**缩放到原尺寸出现（起点把对象 `scale(0)` 并 `move_to(point)`），是该族的通用形式；`point` 可以是坐标、也可以是 mobject。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | —（必填） | 出场对象 |
| `point` | `Point3DLike` | —（必填） | 生长起点。**能填**坐标数组（如 `ORIGIN`）或 mobject（取其中心） |
| `point_color` | `ParsableManimColor \| None` | `None` | 起始颜色；`None` 沿用对象自身颜色（与不传无差别）。**能填**任意颜色 |
| `**kwargs` | `Any` | — | `Animation` 通用参数（`run_time=1.0`、`rate_func`…）。RTM 自有 Grow 族**不是 `Transform` 子类**：`path_arc` / `path_func` 传进去会被 `**kwargs` 吞掉、**完全无效**——要自定义出场路径改用 `Transform` 或 `MoveAlongPath`（见[核心 Transform](../变换/01-Transform核心.md)） |

> **返回**：`GrowFromPoint` 实例。

### `GrowFromCenter`

```python
GrowFromCenter(mobject, point_color=None, **kwargs)
```

从对象**自己的中心**长大，是最常用的出场动画之一（比 `FadeIn` 更有体积感）。`point` 由中心自动给出。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | —（必填） | 出场对象 |
| `point_color` | `ParsableManimColor \| None` | `None` | 起始颜色，`None` 沿用对象自身颜色 |
| `**kwargs` | `Any` | — | 同 `GrowFromPoint`（`point` 由中心自动给出） |

> **返回**：`GrowFromCenter` 实例。

### `GrowFromEdge`

```python
GrowFromEdge(mobject, edge, point_color=None, **kwargs)
```

从对象包围盒的**某条边**（`edge` 方向上的临界点）长出来，适合条形图、标签从边缘展开。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | —（必填） | 出场对象 |
| `edge` | `Vector3DLike` | —（必填） | 生长的边方向。**能填** `DOWN`/`RIGHT`/`UR` 等方向向量 |
| `point_color` | `ParsableManimColor \| None` | `None` | 起始颜色，`None` 沿用对象自身颜色 |
| `**kwargs` | `Any` | — | 同 `GrowFromPoint` |

> **返回**：`GrowFromEdge` 实例。

#### 样例：Point / Center / Edge 三种生长起点

`GrowFromPoint`（`point=ORIGIN` 坐标与 `point=另一 mobject` 两种起点 / `point_color=RED` 与 `BLUE`）、`GrowFromCenter`（`point_color=GREEN`）与 `GrowFromEdge`（`edge=RIGHT` / `point_color=ORANGE`）。

```python
import os
from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    RED,
    YELLOW,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Circle,
    Dot,
    Rectangle,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    GrowFromEdge,
    GrowFromPoint,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401

class Page_01_Grow家族(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w=1280 / h=720 / hidden=True
        win.scene = self

        title = Text("Grow 家族：Point / Center / Edge", font_size=44, color=YELLOW).to_edge(UP)
        win.play(Write(title, run_time=0.8), run_time=0.8)

        # —— 一、GrowFromPoint：从指定点长出来（point 可以是坐标，也可以是 mobject）——
        l1 = Text("GrowFromPoint(mobject, point, point_color, run_time=1.3)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        sq = Square(side_length=1.4, color=BLUE).next_to(l1, DOWN, buff=0.7).shift(LEFT * 2.6)
        anchor = Dot(radius=0.1, color=GREY_B).next_to(l1, DOWN, buff=0.7).shift(RIGHT * 1.4)
        tri = Triangle(color=RED).scale(0.8).next_to(l1, DOWN, buff=0.7).shift(RIGHT * 3.4)
        win.play(FadeIn(VGroup(l1, anchor), shift=DOWN), run_time=0.4)
        win.play(
            GrowFromPoint(                          # 参数 mobject=sq
                sq,
                ORIGIN,                              # 参数 point=ORIGIN（坐标当起点）
                point_color=RED,                     # 参数 point_color=RED（起点是红色）
                run_time=1.3,                        # 参数 **kwargs(run_time)
            ),
            run_time=1.3,
        )
        win.play(
            GrowFromPoint(                          # 参数 mobject=tri
                tri,
                anchor,                              # 参数 point=另一个 mobject（取其中心）
                point_color=BLUE,                    # 参数 point_color=BLUE
                run_time=1.3,                        # 参数 **kwargs(run_time)
            ),
            run_time=1.3,
        )
        win.play(FadeOut(VGroup(l1, sq, anchor, tri)), run_time=0.5)

        # —— 二、GrowFromCenter：从自身中心长大 ——
        l2 = Text("GrowFromCenter(mobject, point_color=GREEN, run_time=1.3)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        ci = Circle(radius=0.85, color=GREEN).next_to(l2, DOWN, buff=0.7)
        win.play(FadeIn(l2, shift=DOWN), run_time=0.4)
        win.play(
            GrowFromCenter(                         # 参数 mobject
                ci,                                 # （point 由自身中心自动给出）
                point_color=GREEN,                  # 参数 point_color=GREEN
                run_time=1.3,                       # 参数 **kwargs(run_time)
            ),
            run_time=1.3,
        )
        win.play(FadeOut(VGroup(l2, ci)), run_time=0.5)

        # —— 三、GrowFromEdge：从包围盒的某条边长出来 ——
        l3 = Text("GrowFromEdge(mobject, edge=RIGHT, point_color=ORANGE)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        rect = (Rectangle(width=3.4, height=1.1, color=ORANGE)
                .next_to(l3, DOWN, buff=0.8))
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)
        win.play(
            GrowFromEdge(                           # 参数 mobject
                rect,
                RIGHT,                              # 参数 edge=RIGHT（从右边长出来）
                point_color=ORANGE,                 # 参数 point_color=ORANGE
                run_time=1.3,                       # 参数 **kwargs(run_time)
            ),
            run_time=1.3,
        )

        win.play(Wait(0.5))
        win.play(FadeOut(VGroup(l3, rect)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_01_Grow家族,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "01-Grow家族.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
```

这段代码在做什么：三段依次演示。

- ① `GrowFromPoint(sq, ORIGIN, point_color=RED, run_time=1.3)` 让蓝方块从画面中心（坐标当起点）带红色渐变长出来；接着 `GrowFromPoint(tri, anchor, point_color=BLUE, run_time=1.3)` 让红三角从灰点 `anchor`（mobject 当起点、取其中心）长出来。
- ② `GrowFromCenter(ci, point_color=GREEN, run_time=1.3)` 让绿圆从自身中心长大。
- ③ `GrowFromEdge(rect, RIGHT, point_color=ORANGE, run_time=1.3)` 让橙色长条从包围盒右边长出来。

每段之间把标签和对象一起淡出，画面保持干净。

<video src="assets/RTM output/01-Grow家族.mp4" controls width="560"></video>

> 提醒：
>
> - `point_color=None`（默认）与不传完全一样，都是沿用对象自身颜色；想看"起点变色"效果就显式给一个颜色。
> - `point` 传 mobject 时取的是它的**中心**，别传还没定位好的对象。

---

相关：[箭头与旋入式生长](01b-箭头与旋入.md)、[强调与闪烁](../强调与提示/01-强调与闪烁.md)、[核心 Transform](../变换/01-Transform核心.md)
