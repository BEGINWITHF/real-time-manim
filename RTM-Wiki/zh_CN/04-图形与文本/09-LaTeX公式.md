# LaTeX 公式

`Tex` / `MathTex` / `SingleStringMathTex` 三个排版类：混排正文与公式、纯公式（可拆片段）、以及最轻量的单串公式。三个类各一条样例。

> **RTM 与 ManimCE 都走 LaTeX**：`Tex` / `MathTex` 需要本机有可用的 LaTeX 发行版；不想装 LaTeX 就用 [Typst](10-Typst.md)（`Typst` / `TypstMath`，或直接写 `MathTex` 由 RTM 自动路由）。

## 参数

### `Tex` 

```python
def __init__(self, *tex_strings: str, font_size: float = 48, color: ParsableManimColor | None = None, tex_environment: str = "document", **kwargs) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `*tex_strings` | `str...` | 必填 | 正文与公式混排；公式写在 `$...$` 里，样例 `r"The area is $A = \pi r^2$."` |
| `font_size` | `float` | `48` | 字号；样例 40 / 48 / 36 |
| `color` | `ManimColor \| None` | `None` | 整体颜色（正文与公式一起变）；样例 `TEAL` |
| `tex_environment` | `str` | `"document"` | 外层 LaTeX 环境；样例换成 `"align*"`（数学环境） |

#### 样例：字号 / 颜色 / 换环境

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Tex, MathTex, SingleStringMathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class TexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09-Tex", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认：正文里用 $...$ 写公式，font_size 控制整体字号 ——
        t1 = Tex(r"The area is $A = \pi r^2$.", font_size=40).move_to([0, 1.5, 0])   #参数 “*tex_strings / font_size”
        win.play(Write(t1), FadeIn(cap("Tex(...font_size=40)", t1)), run_time=0.7)

        # —— color：整体颜色（正文与公式一起变）——
        t2 = Tex(r"$E = mc^2$", font_size=48, color=TEAL).move_to([0, 0.2, 0])   #参数 “color”
        win.play(Write(t2), FadeIn(cap("color=TEAL", t2)), run_time=0.7)

        # —— tex_environment：换一个数学环境（默认是 document）——
        t3 = Tex(r"a + b = c", font_size=36,
                 tex_environment="align*").move_to([0, -1.4, 0])   #参数 “tex_environment”
        win.play(Write(t3), FadeIn(cap('tex_environment="align*"', t3)), run_time=0.7)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：MathTex —— 纯公式、可拆片段 =================================
```

这段代码在做什么：第一段是正文混排（`$A = \pi r^2$` 是行内公式、字号 40）；第二段只放一个公式并整体染 `TEAL`；第三段把 `tex_environment` 换成 `"align*"`，看同一段内容在数学环境下的排版差异。

<video src="assets/RTM output/09-LaTeX公式-tex.mp4" controls width="560"></video>

> 提醒：`tex_environment="document"` 下**不要**用 `\\` 手动换行（会编译失败，实测两引擎一致）；要换行就拆成多个 `Tex` 或改用 `align*`/`gather*` 这类环境。

### `MathTex` 

```python
def __init__(self, *tex_strings: str, font_size: float = 48, color: ParsableManimColor | None = None, **kwargs) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `*tex_strings` | `str...` | 必填 | 每个位置参数是一个片段；`{{ }}` 再把一片拆成多片（见 [片段方法](09b-片段方法与列表.md)） |
| `font_size` | `float` | `48` | 字号；样例 48 / 44 |
| `color` | `ManimColor \| None` | `None` | 整体颜色；样例 `ORANGE` |

#### 样例：整串公式 / 显式分片上色 / 整体样式

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Tex, MathTex, SingleStringMathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class MathTexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09-MathTex", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认：每个位置参数是一个片段，单个字符串可含多个 $...$ ——
        m1 = MathTex(r"x^2 + y^2 = z^2", font_size=48).move_to([0, 1.4, 0])   #参数 “*tex_strings”
        win.play(Write(m1), FadeIn(cap("MathTex(r\"x^2 + y^2 = z^2\")", m1)), run_time=0.8)

        # —— 显式分片：每片独立单位，便于后面单片上色 ——
        m2 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=48).move_to([0, 0.0, 0])   #参数 “{{ }} 分片”
        m2[0].set_color(RED)
        m2[2].set_color(GREEN)
        m2[4].set_color(BLUE)
        win.play(Write(m2), FadeIn(cap("每片独立上色", m2)), run_time=0.8)

        # —— color / font_size：整体样式 ——
        m3 = MathTex(r"\int_0^1 x^2\,dx = \frac{1}{3}", font_size=44,
                     color=ORANGE).move_to([0, -1.6, 0])   #参数 “color / font_size”
        win.play(Write(m3), FadeIn(cap("color=ORANGE, font_size=44", m3)), run_time=0.8)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：SingleStringMathTex —— 单个公式串 ===========================
```

这段代码在做什么：第一段直接写一整串公式；第二段用 `{{ }}` 把 `x^2+y^2=z^2` 拆成五片并给 `x`/`y`/`z` 三片分别上红绿蓝；第三段是定积分，给 `color=ORANGE` 与 44 号字号。

<video src="assets/RTM output/09-LaTeX公式-mathtex.mp4" controls width="560"></video>

> 提醒：`MathTex` 里的 `$` 不用再写（它本身就是数学模式）；要按片段取件就显式分片，单个字符串里的 `{{ }}` 只会拆出第一段（实测两引擎一致）。

### `SingleStringMathTex` 

```python
def __init__(self, tex_string: str, font_size: float = 48, color: ParsableManimColor | None = None, **kwargs) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `tex_string` | `str` | 必填 | 只接**一个**字符串、不拆片段；`Text` / `MathTex` 的字形叶子就是它 |
| `font_size` | `float` | `48` | 字号；样例 44 / 64 |
| `color` | `ManimColor \| None` | `None` | 整体颜色；样例 `TEAL` |

#### 样例：求和 / 整串上色 / 放大字号

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Tex, MathTex, SingleStringMathTex, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class SingleStringDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09-SingleStringMathTex", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 只接一个字符串：不拆片段，最轻量的公式对象 ——
        s1 = SingleStringMathTex(r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}",
                                 font_size=44).move_to([0, 1.2, 0])   #参数 “tex_string”
        win.play(Write(s1), FadeIn(cap("SingleStringMathTex(求和)", s1)), run_time=0.8)

        # —— 与 MathTex 的差别：它只有一片，不能按片段取 ——
        s2 = SingleStringMathTex(r"[a, b] = [c, d]", font_size=44,
                                 color=TEAL).move_to([0, -0.4, 0])
        win.play(Write(s2), FadeIn(cap("整串一个对象（color=TEAL）", s2)), run_time=0.8)

        # —— font_size 再变一次，看缩放 ——
        s3 = SingleStringMathTex(r"f(x) = e^{-x^2}", font_size=64).move_to([0, -2.2, 0])
        win.play(Write(s3), FadeIn(cap("font_size=64", s3)), run_time=0.8)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：第一段是求和公式（44 号）；第二段给整串文字染 `TEAL`；第三段把 `font_size` 提到 64，看等比放大——三个都是"一整片"，没有可拆的子片段。

<video src="assets/RTM output/09-LaTeX公式-singlestring.mp4" controls width="560"></video>

> 提醒：`SingleStringMathTex` 是三个类里最轻量的（只有一层字形叶子），适合"公式不需要拆片段、只要显示"的场景；要按项上色就用 `MathTex` 并显式分片。

---

相关：[片段方法与列表](09b-片段方法与列表.md) · [Typst](10-Typst.md) · [文本 Text](08-文本Text.md)
