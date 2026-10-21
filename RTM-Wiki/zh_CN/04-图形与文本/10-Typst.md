# Typst

RTM 内置 **Typst** 渲染通道：不用装 LaTeX 也能排公式与文本。三个样例分别是 `Typst`（排整段内容）、`TypstMath`（只写数学表达式）、以及 `MathTex` 的**自动路由**（照常写 LaTeX，内部转 Typst 排版）。

> **RTM 特有**：`Typst` / `TypstMath` 是 RTM 的排版类，ManimCE 0.21 **没有** `TypstMath`，所以本节三条样例都是 **RTM 单边成片**（没有 ManimCE 对照件）。

## 参数

### `Typst` 

```python
def __init__(self, typst_code: str, *, font_size: float = 48, typst_preamble: str = "", color: ParsableManimColor | None = None, stroke_width: float | None = None, font_paths: list[str | Path] | None = None, track_baselines: bool = False, should_center: bool = True, height: float | None = None) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `typst_code` | `str` | 必填 | Typst 源码；数学写进 `$...$`（如 `"The area is $pi r^2$"`） |
| `font_size` | `float` | `48` | 字号；样例 40 / 36 |
| `typst_preamble` | `str` | `""` | 拼在源码前的**前置定义**（`#set`、`#let` 等）；样例里用它设置文字大小 |
| `color` | `ManimColor \| None` | `None` | 整体颜色；样例 `TEAL` |
| `stroke_width` | `float \| None` | `None` | 描边宽度；样例 `1` |
| `font_paths` | `list \| None` | `None` | 额外字体目录（自定义字体时用） |
| `track_baselines` | `bool` | `False` | 是否按基线排列（多行混排时有用） |
| `should_center` | `bool` | `True` | 是否把结果移到原点居中；样例 `False` 保留原始位置 |
| `height` | `float \| None` | `None` | 按给定高度缩放（与 `font_size` 二选一） |

#### 样例：字号 / 颜色描边 / 前置定义 / 不居中 + 高度

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Typst, TypstMath, MathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class TypstDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("10-Typst", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认：font_size=48、居中；Typst 语法（$...$ 里是数学）——
        t1 = Typst("The area is $pi r^2$", font_size=40).move_to([0, 1.4, 0])   #参数 “typst_code / font_size”
        win.play(Write(t1), FadeIn(cap("Typst(...font_size=40)", t1)), run_time=0.7)

        # —— color / stroke_width：整体颜色与描边 ——
        t2 = Typst("bold text #text(fill: red)[red]", font_size=40,
                   color=TEAL, stroke_width=1).move_to([0, -0.2, 0])   #参数 “color / stroke_width”
        win.play(Write(t2), FadeIn(cap("color=TEAL, stroke_width=1", t2)), run_time=0.7)

        # —— typst_preamble：给整块代码加前置定义（这里定义颜色）——
        t3 = Typst("#let hot = rgb(\"#ff6600\")\nA #text(fill: hot)[hot] word",
                   font_size=36, typst_preamble='#set text(size: 12pt)')   #参数 “typst_preamble”
        t3.move_to([0, -1.8, 0])
        win.play(Write(t3), FadeIn(cap("typst_preamble 前置定义", t3)), run_time=0.7)

        # —— should_center / height：不居中、按高度缩放 ——
        t4 = Typst("H", font_size=72, should_center=False, height=1.2)   #参数 “should_center / height”
        t4.move_to([4.6, 1.4, 0])
        win.play(Write(t4), FadeIn(cap("height=1.2", t4)), run_time=0.6)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：TypstMath —— 只写数学表达式 =================================
```

这段代码在做什么：四个 `Typst` 对象各演示一组参数。

- 第一段最普通的 Typst 文本（`$pi r^2$` 是数学）。
- 第二段加 `color=TEAL` 与 `stroke_width=1`。
- 第三段用 `typst_preamble` 先写 `#set text(size: 12pt)`，再让正文里的 `#text(fill: hot)[hot]` 生效。
- 右上把 `should_center=False` 且 `height=1.2`，只看缩放结果、不回到原点。

<video src="assets/RTM output/10-Typst-typst.mp4" controls width="560"></video>

> 提醒：Typst 的数学是 `$...$` 包起来的（不像 LaTeX 的 `$` 需要成对写在字符串里），`#let` 定义的颜色之类必须放在 `typst_preamble` 或正文前面；`height` 与 `font_size` 同时给时以 `height` 为准。

### `TypstMath` 

```python
def __init__(self, math_expression: str, **kwargs) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `math_expression` | `str` | 必填 | 只写数学表达式（内部自动包 `$ ... $`）；样例 `sum_(i=1)^n i = (n(n+1))/2`、`mat(1, 2; 3, 4)` |
| `**kwargs` | `Any` | — | 透传给 `Typst`（`font_size` / `color` / `stroke_width` …）；样例给了 `color=ORANGE` |

#### 样例：求和 / 积分 / 矩阵 / 根号

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Typst, TypstMath, MathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class TypstMathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("10-TypstMath", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认：直接写表达式（会自动包进 $ ... $）——
        m1 = TypstMath("sum_(i=1)^n i = (n(n+1))/2", font_size=44).move_to([0, 1.4, 0])   #参数 “math_expression”
        win.play(Write(m1), FadeIn(cap("TypstMath(求和公式)", m1)), run_time=0.8)

        # —— 其余参数透传给 Typst：color / font_size ——
        m2 = TypstMath("integral_0^1 x^2 dif x = 1/3", font_size=44,
                       color=ORANGE).move_to([0, -0.4, 0])   #参数 “**kwargs（color）”
        win.play(Write(m2), FadeIn(cap("color=ORANGE", m2)), run_time=0.8)

        # —— 分式/根号/矩阵 ——
        m3 = TypstMath("mat(1, 2; 3, 4)", font_size=40).move_to([-3.4, -2.2, 0])
        m4 = TypstMath("sqrt(2) approx 1.414", font_size=40).move_to([2.6, -2.2, 0])
        win.play(Write(m3), FadeIn(cap("mat(1, 2; 3, 4)", m3)), run_time=0.7)
        win.play(Write(m4), FadeIn(cap("sqrt(2)", m4)), run_time=0.7)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：自动路由 —— MathTex 在 RTM 下走 Typst ======================
```

这段代码在做什么：

- 上面是求和公式（默认字号 44）。
- 中间是定积分并给 `color=ORANGE`（参数透传）。
- 下面一行左边 `mat(1, 2; 3, 4)` 排矩阵、右边 `sqrt(2) approx 1.414`，说明 Typst 的数学函数写法（`mat` / `sqrt` / `integral` / `approx`）。

<video src="assets/RTM output/10-Typst-typstmath.mp4" controls width="560"></video>

> 提醒：Typst 数学的写法与 LaTeX 不同（`sqrt(x)` 不是 `\sqrt{x}`、分式用 `a/b`、矩阵用 `mat(...)`）；`TypstMath` 里**不要**再自己写 `$`，否则会套两层。

### 自动路由：`MathTex` 照常写 LaTeX 

```python
MathTex(r"\frac{a}{b} + \sqrt{x}")   # RTM 下内部转 Typst 排版
```

| 项目 | 说明 |
| --- | --- |
| `MathTex` | 写法与 LaTeX 一致（`\frac`、`\sqrt`…），RTM 内部**转成 Typst** 排版，所以本机不需要装 LaTeX |
| 片段接口 | `MathTex` 的片段上色/取件（`set_color_by_tex`、`get_part_by_tex` 等）照常可用，见 [片段方法](09b-片段方法与列表.md) |
| `TypstMath` 对照 | 同一个公式用 Typst 语法写（`a/b + sqrt(x)`），形状与位置一致 |

#### 样例：`MathTex` / `TypstMath` 同式对照 / 片段上色

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Typst, TypstMath, MathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class AutoRouteDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("10-Typst 自动路由", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— MathTex 照常写 LaTeX，RTM 内部转成 Typst 排版（无需本机 LaTeX）——
        mt = MathTex(r"\frac{a}{b} + \sqrt{x}").move_to([0, 1.0, 0])   #参数 “MathTex（自动路由）”
        win.play(Write(mt), FadeIn(cap("MathTex(\\frac{a}{b}+\\sqrt{x})", mt)), run_time=0.8)

        # —— 同一公式用 TypstMath 写，形状与位置一致 ——
        tm = TypstMath("a/b + sqrt(x)", font_size=48).move_to([0, -0.6, 0])
        win.play(Write(tm), FadeIn(cap("TypstMath(a/b + sqrt(x))", tm)), run_time=0.8)

        # —— MathTex 的片段上色等接口照常可用 ——
        mt2 = MathTex(r"E = mc^2").move_to([0, -2.2, 0])
        mt2[0].set_color(YELLOW)
        win.play(Write(mt2), FadeIn(cap("MathTex 片段上色照常", mt2)), run_time=0.8)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：上面用 `MathTex(r"\frac{a}{b} + \sqrt{x}")` 写 LaTeX；下面用 `TypstMath("a/b + sqrt(x)")` 写同一个式子，两者排出来几乎一样——说明 LaTeX 写法在 RTM 下会被转成 Typst；最后 `MathTex(r"E = mc^2")` 并用 `mt2[0].set_color(YELLOW)` 给片段上色，证明片段接口仍然可用。

<video src="assets/RTM output/10-Typst-autoroute.mp4" controls width="560"></video>

> 提醒：自动路由对**常规 LaTeX 命令**有效，但极少数宏（自定义 `\newcommand`、复杂 `tikz` 类）没有对应实现；遇到排不出来时改用 `TypstMath` 直接写 Typst 语法。

---

相关：[LaTeX 公式](09-LaTeX公式.md) · [文本 Text](08-文本Text.md) · [片段方法](09b-片段方法与列表.md)
