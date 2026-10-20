# Transform 核心：把 A 变成 B

把一个对象插值变形为另一个对象的三种核心写法：整段变形的 `Transform`、换人接管的 `ReplacementTransform`、以及「先改目标再动」的 `MoveToTarget`。不手写 target 的写法见[用方法 / 函数驱动的变换](02-方法与函数驱动.md)。

## 参数

### Transform

```python
Transform(mobject, target_mobject, path_func=None, path_arc=0, path_arc_axis=None,
          path_arc_centers=None, replace_mobject_with_target_in_scene=False, **kwargs)
```

把 `mobject` 的点集**插值变形**成 `target_mobject`（必要时自动补齐点数/子对象），播完后 `mobject` 留在场景里且已经变成 target 的样子，`target_mobject` 默认不会被加入场景。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | —（必填） | 被变形的源对象（会被原地改变） |
| `target_mobject` | `Mobject` | —（**必填，无默认**） | 变形目标。RTM 自有 `Transform` **必须显式传**（没有 `=None` 默认）
| `path_func` | `Callable \| None` | `None` | 自定义路径函数 `(start_pts, end_pts, alpha) -> pts`，见 `manim.utils.paths` |
| `path_arc` | `float` | `0` | 圆弧角度（弧度），`>0` 逆时针 |
| `path_arc_axis` | `np.ndarray \| None` | `None`（→ `OUT`） | 圆弧旋转轴（3D 时用）；`None` 时内部按 `[0,0,1]` 处理 |
| `path_arc_centers` | `Point3DLike \| None` | `None` | 圆弧中心；给了它且没给 `path_func` 就自动生成 `path_along_circles` 路径 |
| `replace_mobject_with_target_in_scene` | `bool` | `False` | `True`：播完把 `mobject` 换成 `target_mobject`（场景里留下 target） |
| `**kwargs` | … | — | `Animation` 通用参数（`run_time`、`rate_func`…） |

> **返回**：`Transform` 实例（继承 `Transform(Animation)`）。

### ReplacementTransform

```python
ReplacementTransform(mobject, target_mobject, **kwargs)
```

与 `Transform` 相同的变形，但固定 `replace_mobject_with_target_in_scene=True`：**播完后源对象消失、目标对象接管场景**，做公式推演/概念替换时首选。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | —（必填） | 变形源对象 |
| `target_mobject` | `Mobject` | —（必填） | 变形目标，播完留在场景里 |
| `**kwargs` | … | — | 全部转发给 `Transform`（`path_arc`、`path_func`、`path_arc_centers`、`replace_mobject_with_target_in_scene`——显式传入会覆盖默认 `True`——及 `Animation` 通用参数） |

> **返回**：`ReplacementTransform` 实例（继承 `ReplacementTransform(Transform)`）。

### MoveToTarget

```python
MoveToTarget(mobject, **kwargs)
```

把 `mobject` 变形为 `mobject.target`，即 `generate_target` 之后你手工修改的那个副本；`.animate` 语法就是它的语法糖。**缺 `target` 时两版都出错，但错法不同**：ManimCE 版构造期抛 `ValueError`；RTM 自有版的判据是 `hasattr(mobject, "target")`，而 `Mobject` **自带一个值为 `None` 的 `.target` 属性**——没调 `generate_target` 时它取到 `None`，构造不报错、但 `begin` 时抛 `AttributeError: 'NoneType' object has no attribute 'copy'`。**先 `generate_target` 再播**，两版都稳。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | —（必填） | 必须先 `generate_target()` 并改好 `mobject.target` |
| `**kwargs` | … | — | 转发 `Transform` / `Animation` 通用参数 |

> **返回**：`MoveToTarget` 实例（继承 `MoveToTarget(Transform)`）。

## 样例

#### 样例：Transform / ReplacementTransform / MoveToTarget

本页专属样例（`assets/RTM code/01-Transform核心.py`）：`Transform` 的 `path_arc` 圆弧路径与自定义 `path_func`、`ReplacementTransform` 的「源消失目标接管」、`MoveToTarget` 的 `generate_target()` 流程各占一段；源与目标在形状 / 位置 / 颜色上都不一样，方便看清每一步变了什么。

```python
import os

import numpy as np
from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    RED,
    YELLOW,
    DOWN,
    LEFT,
    OUT,
    RIGHT,
    UP,
    PI,
    Circle,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
    smooth,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    MoveToTarget,
    ReplacementTransform,
    Transform,
    Wait,  # noqa: F401
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


def arc_up(start_pts, end_pts, alpha):
    """自定义 path_func：(start_pts, end_pts, alpha) -> pts，插值时向上拱一段。"""
    pts = start_pts + (end_pts - start_pts) * alpha
    return pts + np.array([0.0, 1.1 * np.sin(np.pi * alpha), 0.0])


class Page_01_Transform核心(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w / h / hidden
        win.scene = self                          # 参数 win.scene

        title = Text("Transform 核心 · 把 A 变成 B", font_size=44, color=ORANGE).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # —— ① Transform：全部文档参数显式传；源与目标形状 / 位置 / 颜色都不同 ——
        lab1 = VGroup(
            Text("Transform(sq, circ, path_arc=PI / 2,", font_size=30, color=GREY_B),
            Text("  path_func=None, path_arc_axis=OUT,", font_size=30, color=GREY_B),
            Text("  replace_mobject_with_target_in_scene=False)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.3)
        sq = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6).move_to(LEFT * 3.6 + DOWN * 1.2)
        circ = Circle(radius=0.8, color=GREEN).set_fill(GREEN, 0.6).move_to(RIGHT * 2.8 + DOWN * 0.4)
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)
        win.play(Create(sq), run_time=0.5)
        win.play(                                                    # 点集插值变形 + 圆弧路径
            Transform(sq, circ,                                     # 参数 mobject / target_mobject ✓
                      path_func=None,                               # 参数 path_func=None ✓（下一步换自定义函数）
                      path_arc=PI / 2,                              # 参数 path_arc ✓（非默认 0：走 90° 圆弧）
                      path_arc_axis=OUT,                            # 参数 path_arc_axis ✓（2D 下恒为 z 轴）
                      path_arc_centers=None,                        # 参数 path_arc_centers ✓（见「无法演示」）
                      replace_mobject_with_target_in_scene=False,   # 参数 ✓（默认；播完源留在场景）
                      run_time=1.5),                                # 参数 run_time / **kwargs ✓
            run_time=1.5,
        )
        win.play(FadeOut(VGroup(lab1, sq)), run_time=0.5)

        # —— ② Transform 的 path_func：自定义插值路径 ——
        lab2 = VGroup(
            Text("Transform(sq2, tri, path_func=arc_up,", font_size=30, color=GREY_B),
            Text("                      run_time=1.3)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        sq2 = Square(side_length=1.2, color=YELLOW).set_fill(YELLOW, 0.6).move_to(LEFT * 3.6 + DOWN * 1.2)
        tri = Triangle(color=RED).scale(0.8).set_fill(RED, 0.6).move_to(RIGHT * 3.2 + DOWN * 1.2)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)
        win.play(Create(sq2), run_time=0.5)
        win.play(                                     # 插值点沿自定义路径向上拱起再落下
            Transform(sq2, tri, path_func=arc_up, run_time=1.3),
            run_time=1.3,
        )
        win.play(FadeOut(VGroup(lab2, sq2)), run_time=0.5)

        # —— ③ ReplacementTransform：播完源消失、目标接管场景 ——
        lab3 = VGroup(
            Text("ReplacementTransform(left, right,", font_size=30, color=GREY_B),
            Text("                     run_time=1.2)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.35)
        left = Text("left", font_size=44, color=BLUE).move_to(LEFT * 3.2 + DOWN * 1.2)
        right = Text("right", font_size=44, color=GREEN).move_to(RIGHT * 3.2 + DOWN * 1.2)
        self.add(left)                              # 源对象先放进场景
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)
        win.play(ReplacementTransform(left, right, run_time=1.2), run_time=1.2)
        win.play(FadeOut(VGroup(lab3, right)), run_time=0.5)

        # —— ④ MoveToTarget：先 generate_target() 改好 .target 再播 ——
        lab4 = VGroup(
            Text("sq3.generate_target(); sq3.target.shift(", font_size=30, color=GREY_B),
            Text("  RIGHT * 3).scale(1.6).set_fill(GREEN, 0.6)", font_size=30, color=GREY_B),
            Text("MoveToTarget(sq3, run_time=1.3)", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.12).next_to(title, DOWN, buff=0.3)
        sq3 = Square(side_length=0.9, color=YELLOW).set_fill(YELLOW, 0.6).move_to(LEFT * 3.4 + DOWN * 1.4)
        win.play(FadeIn(lab4, shift=DOWN), run_time=0.4)
        win.play(Create(sq3), run_time=0.5)
        sq3.generate_target()                       # 参数 mobject.target ✓（先改好目标状态）
        sq3.target.shift(RIGHT * 3).scale(1.6).set_fill(GREEN, 0.6)
        win.play(MoveToTarget(sq3, run_time=1.3), run_time=1.3)

        win.play(FadeOut(VGroup(title, lab4, sq3)), run_time=0.6)
        win.close()                                 # 参数 win.close()
```

这段代码在做什么：四段演示。第一段把蓝色方块沿 90° 圆弧变形成绿色圆（`path_arc=PI/2`，形状/位置/颜色全变，播完方块以圆的形态留在原位）；第二段换成自定义 `path_func=arc_up`，方块变三角时每个插值点先向上拱起再落下；第三段 `ReplacementTransform` 把左边的 `left` 文字变成右边的 `right`——源直接消失、目标接管；第四段先 `generate_target()` 把目标状态（右移三格、放大 1.6 倍、填绿）改好，再 `MoveToTarget` 一次播到位。

<video src="assets/RTM output/01-Transform核心.mp4" controls width="560"></video>

> 提醒：样例里的 `Transform` / `ReplacementTransform` / `MoveToTarget` / `Write` 从 `real_time_manim.vulkan_bind` 导入——RTM 对这组核心变换有自己的实现；`FadeIn` / `FadeOut` / `Create` 以及 `Wait`（RTM 版）同样从 `vulkan_bind` 导入，普通动画类从 `real_time_manim` 导入即可。`Transform` 播完源对象还在场景里（只是变成了目标的样子），想要「换掉」的效果要么显式 `replace_mobject_with_target_in_scene=True`，要么直接用 `ReplacementTransform`。

相关：[用方法/函数驱动的变换](02-方法与函数驱动.md)、[位置互换 / 复制式变换](04-位置互换与复制式变换.md)、[淡出—淡入式变换](05-淡出淡入式变换.md)
