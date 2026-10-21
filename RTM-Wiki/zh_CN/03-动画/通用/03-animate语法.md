# .animate 语法与 generate_target() / MoveToTarget

`Mobject.animate` 是"改属性即动画"的语法糖；RTM 的 `win.play` / `AnimationGroup` / `Succession` 都显式识别 `.animate` 构建器并自动转换，`MoveToTarget` 也已支持。

## 参数

### `Mobject.animate`（`_AnimationBuilder`）

```python
@property
def animate(self) -> _AnimationBuilder: ...

win.play(sq.animate.shift(RIGHT))                    # 平移
win.play(sq.animate.set_fill(RED).set_opacity(0.5))  # 链式：多个方法合成一个动画
win.play(sq.animate(run_time=2).rotate(PI / 2))      # 动画参数紧跟 .animate(...)，只能传一次
win.play(sq.animate(rate_func=there_and_back).shift(RIGHT))
```

`Mobject.animate` 是一个 property，返回 `_AnimationBuilder`：它内部先 `generate_target()`，链上的每个方法都记到列表里，`win.play` 时合成**一个**动画。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `**kwargs`（紧跟 `.animate(...)`） | `Any` | — | **能填**可以 `setattr` 到动画对象上的属性：`run_time`、`rate_func`、`reverse_rate_function`…。**只能在访问任何方法之前传一次**，写在链式方法之后或传两次都抛 `ValueError`。`lag_ratio=...` 并未被丢弃：构建时会 `setattr` 到动画对象上——含 submobject 时按 family 错峰、RTM 正常渲染；单个动画无子对象时该参数无效，但现在会打 `UserWarning` 显式提示，不再静默 |
| 链式方法调用 | — | — | 如 `.shift(RIGHT)`、`.set_fill(RED)`、`.rotate(PI/2)`：本身不是参数，全部记入列表，`win.play` 时合成一个动画 |

> **返回**：`_AnimationBuilder`，交给 `win.play(...)` 时自动转成动画。

### `generate_target` / `MoveToTarget`

```python
def generate_target(self) -> None: ...
MoveToTarget(mobject, **kwargs)
```

`.animate` 是 `generate_target()` + `MoveToTarget` 的语法糖；当**目标状态需要复杂计算**（先对 `target` 排版、对齐，再播放）时，用显式写法：`c.generate_target()` 复制一份到 `c.target`，随便改 `c.target`，最后 `win.play(MoveToTarget(c))`。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | —（必填） | 要奔向自己 `target` 的对象；先调过 `generate_target()` 才有 `target`。没调就播：ManimCE 版构造期抛 `ValueError`，RTM 自有版会在 `begin()` 抛 `AttributeError: 'NoneType' object has no attribute 'copy'`（`Mobject` 自带的 `.target` 是 `None`） |
| `**kwargs` | `Any` | — | `Animation` 通用参数（`run_time`、`rate_func`、`lag_ratio`…），无额外形参 |

> **返回**：`generate_target()` 无返回（把复制体挂到 `mobject.target`）；`MoveToTarget(...)` 返回动画实例，交给 `win.play(...)`。

#### 样例：.animate 三种写法 + generate_target / MoveToTarget

样例演示三种 `.animate` 写法，外加显式的 `generate_target()` + `MoveToTarget`：

- 链式 `.animate.shift(...)`；
- `.animate(run_time=1.3).set_color(RED).rotate(PI/5)`（kwargs 紧跟 `.animate(...)`、多个方法合成一个动画）；
- `.animate(rate_func=there_and_back).scale(0.55)`；
- 显式 `ci.generate_target()` + `MoveToTarget(ci, run_time=1.2)`。

```python
import os
from real_time_manim import (
    BLUE,
    DOWN,
    GREEN,
    GREY_B,
    LEFT,
    RED,
    RIGHT,
    UP,
    YELLOW,
    PI,
    Circle,
    Scene,
    Square,
    Text,
    VGroup,
    there_and_back,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    MoveToTarget,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401

class Page_03_animate语法(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w / h / hidden
        win.scene = self                          # 参数 win.scene

        title = Text("03-.animate 语法与 MoveToTarget", font_size=44, color=YELLOW).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        sq = Square(side_length=1.4, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 3.2 + DOWN * 1.9)
        ci = Circle(radius=0.7, color=GREEN).set_fill(GREEN, 0.5).shift(RIGHT * 3.2 + DOWN * 1.9)

        # —— 步骤 1：sq.animate.shift(...) ——
        l1 = Text("win.play(sq.animate.shift(RIGHT * 1.6))", font_size=30, color=GREY_B)
        l1.to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(l1, shift=DOWN), FadeIn(sq), FadeIn(ci), run_time=0.4)
        win.play(sq.animate.shift(RIGHT * 1.6))                  # 参数 .animate + 链式方法 shift
        win.play(Wait(0.2))

        # —— 步骤 2：kwargs 紧跟 .animate(...)，链式多个方法 ——
        win.play(FadeOut(l1), run_time=0.3)
        l2 = Text("win.play(sq.animate(run_time=1.3)", font_size=30, color=GREY_B)
        l3 = Text("              .set_color(RED).rotate(PI/5))", font_size=30, color=GREY_B)
        sig2 = VGroup(l2, l3).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.4)
        win.play(sq.animate(run_time=1.3)                         # 参数 .animate(run_time=…)（只能传一次）
                 .set_color(RED)                                  # 链式方法 1
                 .rotate(PI / 5))                                 # 链式方法 2（合成一个动画）
        win.play(Wait(0.2))

        # —— 步骤 3：rate_func 写进 .animate(...) ——
        win.play(FadeOut(sig2), run_time=0.3)
        l4 = Text("win.play(sq.animate(rate_func=there_and_back).scale(0.55))",
                  font_size=30, color=GREY_B).to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(l4, shift=DOWN), run_time=0.4)
        win.play(sq.animate(rate_func=there_and_back).scale(0.55))   # 参数 rate_func（出去又回来）
        win.play(Wait(0.2))

        # —— 步骤 4：显式 generate_target() + MoveToTarget ——
        win.play(FadeOut(l4), run_time=0.3)
        l5 = Text("ci.generate_target();  ci.target.set_fill(RED, 0.4)", font_size=28, color=GREY_B)
        l6 = Text("                 .shift(2 * RIGHT + UP).scale(0.5)", font_size=28, color=GREY_B)
        l7 = Text("win.play(MoveToTarget(ci, run_time=1.2))", font_size=28, color=GREY_B)
        sig4 = VGroup(l5, l6, l7).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.05)
        win.play(FadeIn(sig4, shift=DOWN), run_time=0.4)
        ci.generate_target()                                      # 参数 generate_target()
        ci.target.set_fill(RED, 0.4).shift(2 * RIGHT + UP).scale(0.5)
        win.play(MoveToTarget(ci, run_time=1.2))                  # 参数 MoveToTarget(mobject, run_time)
        win.play(Wait(0.3))

        win.play(FadeOut(VGroup(title, sq, ci, sig4)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_03_animate语法,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "03-animate语法.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
```

这段代码在做什么：四步演示——

- ① `sq.animate.shift(RIGHT * 1.6)`，最朴素的"改属性即动画"；
- ② `sq.animate(run_time=1.3).set_color(RED).rotate(PI / 5)`，把动画参数紧跟在 `.animate(...)` 后面、再链两个方法，合成一个 1.3 秒的变色+旋转动画；
- ③ `sq.animate(rate_func=there_and_back).scale(0.55)`，把速率函数写进 `.animate(...)`，缩放"出去又回来"；
- ④ 给圆 `ci.generate_target()` 生成目标副本，改好 `ci.target` 的颜色/位置/大小后，用 `MoveToTarget(ci, run_time=1.2)` 一次变过去。

<video src="assets/RTM output/03-animate语法.mp4" controls width="560"></video>

> 提醒：同一个 mobject 在一次 `play` 里只能有一个 `.animate`，要多步就链式写。`.animate` 是在"变更前的点集 ↔ 变更后的点集"之间插值，沿复杂路径、绕远的旋转会走直线而非弧线——这类需求用 `Rotate`、`MoveAlongPath` 或 `ValueTracker + updater`。目标状态要先算再播的场景，用 `generate_target()` + `MoveToTarget` 更直观。

无法演示：.animate(lag_ratio=...) —— 无视频：调查结论——该参数并未被丢弃（构建时 `setattr` 到动画对象上），含 submobject 时按 family 错峰且 RTM 正常渲染；单个动画无子对象时无效，但现在会打 `UserWarning` 显式提示，不再静默；`@override_animate` / `@override_animation` —— 已接线（`Animation.__new__` 查重写注册表 + `animation_override_for` 跨命名空间同名回退，`use_override=False` 保原类，`.animate` 走 `@override_animate` 回归锁），仍不演示：需要自定义 Mobject 子类。

---

相关：[生命周期与公共参数](01-生命周期与公共参数.md) · [play 与 wait 参数](02-play与wait参数.md) · [Create 与画线族](../创建与擦除/01-Create与画线族.md)
