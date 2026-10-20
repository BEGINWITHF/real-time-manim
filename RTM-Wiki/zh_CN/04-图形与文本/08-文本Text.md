# 文本 Text

`Text` / `MarkupText` / `Paragraph` 三个文本类，加上 `register_font`（临时注册字体文件）。四者各一条样例。

> **`remove_invisible_chars` 不可用**：当前版本没有从 `real_time_manim` 导出这个函数（`from real_time_manim import remove_invisible_chars` 直接 `ImportError`），需要清理不可见字符时自己按字形过滤。

## 参数

### `Text` 

```python
def __init__(self, text: str, fill_opacity: float = 1, stroke_width: float = 0, color: ParsableManimColor | None = None, font_size: float = 48, line_spacing: float = -1, font: str = "", slant: str = "NORMAL", weight: str = "NORMAL", t2c: dict | None = None, t2f: dict | None = None, t2w: dict | None = None, t2s: dict | None = None, disable_ligatures: bool = False, **kwargs) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `text` | `str` | 必填 | 文本内容，`\n` 换行 |
| `font` | `str` | `""`（默认字体） | 字体族名；样例 `"Arial"` |
| `font_size` | `float` | `48` | 字号；样例 40 / 34 |
| `weight` | `str` | `"NORMAL"` | 字重；样例 `"BOLD"` |
| `slant` | `str` | `"NORMAL"` | 斜体；样例 `"ITALIC"` |
| `color` | `ManimColor \| None` | `None` | 整体颜色；样例 `TEAL` |
| `line_spacing` | `float` | `-1`（自动） | 行距；样例 `1.2` |
| `t2c` | `dict \| None` | `None` | 子串→颜色（`{"red": RED}`） |
| `t2f` / `t2w` / `t2s` | `dict \| None` | `None` | 子串→字体 / 字重 / 斜体 |
| `fill_opacity` / `stroke_width` | `float` | `1` / `0` | 填充与描边 |

#### 样例：字体 / 字号 / 粗细 / 斜体 / 行距 / 子串分色

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Text, MarkupText, Paragraph, register_font,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class TextDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("08-Text", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认：单行文本 ——
        t1 = Text("Hello RTM").move_to([0, 1.6, 0])   #参数 “text”
        win.play(Write(t1), FadeIn(cap('Text("Hello RTM")', t1)), run_time=0.6)

        # —— font / font_size / weight / slant ——
        t2 = Text("Arial 40 bold italic", font="Arial", font_size=40,
                  weight="BOLD", slant="ITALIC").move_to([0, 0.5, 0])   #参数 “font / font_size / weight / slant”
        win.play(Write(t2), FadeIn(cap('font="Arial" weight=BOLD slant=ITALIC', t2)), run_time=0.7)

        # —— color / line_spacing：两行文本的整体颜色与行距 ——
        t3 = Text("first line\nsecond line", font_size=34, color=TEAL,
                  line_spacing=1.2).move_to([0, -1.0, 0])   #参数 “color / line_spacing”
        win.play(Write(t3), FadeIn(cap("color=TEAL, line_spacing=1.2", t3)), run_time=0.7)

        # —— t2c：把指定子串单独上色 ——
        t4 = Text("red green blue", font_size=34,
                  t2c={"red": RED, "green": GREEN, "blue": BLUE}).move_to([0, -2.3, 0])   #参数 “t2c”
        win.play(Write(t4), FadeIn(cap('t2c={"red": RED, …}', t4)), run_time=0.7)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：MarkupText —— Pango 标记文本 ===============================
```

这段代码在做什么：第一行默认文本；第二行把 `font="Arial"`、`font_size=40`、`weight="BOLD"`、`slant="ITALIC"` 一起给上；第三行是两行文本，用 `color=TEAL` 与 `line_spacing=1.2` 看行距；第四行用 `t2c` 把 `red`/`green`/`blue` 三个词分别染红绿蓝。

<video src="assets/RTM output/08-文本Text-text.mp4" controls width="560"></video>

> 提醒：`t2c`/`t2f`/`t2w`/`t2s` 的键是**子串**、按出现顺序匹配；`line_spacing=-1` 是"自动"，显式给正数才按倍数走。

### `MarkupText` 

```python
def __init__(self, text: str, fill_opacity: float = 1, stroke_width: float = 0, color: ParsableManimColor | None = None, font_size: float = 48, line_spacing: float = -1, font: str = "", slant: str = "NORMAL", weight: str = "NORMAL", justify: str = "left", indent: float = 0, **kwargs) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `text` | `str` | 必填 | Pango 标记文本；样例只用了 `<b>` / `<i>` |
| `font_size` | `float` | `48` | 字号；样例 36 / 32 / 30 |
| `color` | `ManimColor \| None` | `None` | 整体颜色；样例 `TEAL` |
| `line_spacing` | `float` | `-1` | 行距；样例 `1.4` |
| `font` / `weight` / `slant` | `str` | 默认 / `NORMAL` | 同 `Text` |
| `justify` | `str` | `"left"` | 多行对齐方式（`left`/`center`/`right`） |
| `indent` | `float` | `0` | 首行缩进 |

#### 样例：`<b>`/`<i>` / 整体颜色 / 行距

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Text, MarkupText, Paragraph, register_font,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class MarkupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("08-MarkupText", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 标记语法：<b> / <i> / <span foreground=…> ——
        m1 = MarkupText('<b>bold</b> and <i>italic</i>',
                        font_size=36).move_to([0, 1.3, 0])   #参数 “text（Pango 标记）”
        win.play(Write(m1), FadeIn(cap('MarkupText("<b>…</b> <i>…</i>")', m1)), run_time=0.8)

        # —— color / font_size：整体颜色与字号（标记里的颜色优先）——
        m2 = MarkupText('colored markup text',
                        font_size=32, color=TEAL).move_to([0, 0.0, 0])   #参数 “color / font_size”
        win.play(Write(m2), FadeIn(cap("color=TEAL", m2)), run_time=0.8)

        # —— line_spacing / justify：多行与对齐 ——
        m3 = MarkupText("line one\nline two is longer", font_size=30,
                        line_spacing=1.4).move_to([0, -1.5, 0])   #参数 “line_spacing”
        win.play(Write(m3), FadeIn(cap("line_spacing=1.4", m3)), run_time=0.8)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：Paragraph —— 多段文本，逐行对齐 ============================
```

这段代码在做什么：第一行用 `<b>` 与 `<i>` 标记出粗体、斜体；第二行整串染成 `TEAL`；第三行是两行文本，`line_spacing=1.4` 拉开行距。

<video src="assets/RTM output/08-文本Text-markup.mp4" controls width="560"></video>

> 提醒：RTM 的标记解析走 Pango→SVG 通道，**`<span foreground=…>` 这类属性会解析失败**（`ElementTree.ParseError: no element found`，样例因此只用 `<b>`/`<i>`）；要单独上色请给整串一个 `color`，或用 `Text` 的 `t2c`。

### `Paragraph` 

```python
def __init__(self, *text: str, line_spacing: float = -1, alignment: str | None = None, **kwargs) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `*text` | `str...` | 必填 | 每个位置参数是一段；样例 3 段 / 2 段 |
| `line_spacing` | `float` | `-1` | 段间距；样例 `0.6` |
| `alignment` | `str \| None` | `None` | 整块对齐（`left`/`center`/`right`）；样例 `"left"` / `"center"` |
| `**kwargs` | `Any` | — | 传给文本（`font_size` / `color` / `font`）；样例 `color=ORANGE, font="Arial"` |

#### 样例：三段左对齐 / 段距 0.6 / 颜色与字体透传

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Text, MarkupText, Paragraph, register_font,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class ParagraphDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("08-Paragraph", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 每个位置参数是一段；alignment 控制整块对齐 ——
        p1 = Paragraph("first paragraph", "second paragraph", "third",
                       alignment="left", font_size=32).move_to([-0.6, 0.9, 0])   #参数 “*text / alignment”
        win.play(Write(p1), FadeIn(cap('alignment="left"', p1)), run_time=0.8)

        # —— line_spacing：段间距 ——
        p2 = Paragraph("tight", "spacing", line_spacing=0.6,
                       alignment="center", font_size=32).move_to([-0.6, -1.4, 0])   #参数 “line_spacing”
        win.play(Write(p2), FadeIn(cap("line_spacing=0.6", p2)), run_time=0.8)

        # —— **kwargs 透传：颜色 / 字体 ——
        p3 = Paragraph("colored", "paragraph", font_size=32, color=ORANGE,
                       font="Arial").move_to([2.6, -1.4, 0])   #参数 “**kwargs（color / font）”
        win.play(Write(p3), FadeIn(cap("color=ORANGE, font=Arial", p3)), run_time=0.8)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：register_font —— 临时注册字体文件 ==========================
```

这段代码在做什么：左边上面是三段文本、`alignment="left"`；下面两段把 `line_spacing` 收到 0.6、改成居中；右边第二块用 `**kwargs` 把 `color=ORANGE` 与 `font="Arial"` 透传给整段文本。

<video src="assets/RTM output/08-文本Text-paragraph.mp4" controls width="560"></video>

> 提醒：`alignment` 是**整块**的对齐，不是每段独立对齐；段与段之间用 `line_spacing` 控制，不是 `\n`（`\n` 会变成同一段里的换行）。

### `register_font` ✅

```python
@contextmanager
def register_font(font_file: str | Path) -> Iterator[None]:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `font_file` | `str \| Path` | 必填 | 字体文件路径；样例 `C:\Windows\Fonts\arial.ttf` |

**上下文管理器**：`with register_font(路径):` 块内注册，块内构造的 `Text` 就能按字体族名使用它。

#### 样例：`with` 块内注册 + 块外沿用 + 未注册回退

```python
import os
import subprocess
import sys
from real_time_manim import (
    Scene, Text, MarkupText, Paragraph, register_font,
    BLUE, GREEN, RED, ORANGE, YELLOW, TEAL, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class RegisterFontDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("08-register_font", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 用法：with 块内注册字体文件，块内构造的 Text 就能用这个族名 ——
        font_file = r"C:\Windows\Fonts\arial.ttf"   #参数 “font_file”：字体文件路径
        with register_font(font_file):   #参数 “font_file”
            t1 = Text("Registered: Arial", font="Arial", font_size=44).move_to([0, 0.9, 0])
            win.play(Write(t1), FadeIn(cap("with register_font(arial.ttf): Text(..., font=\"Arial\")", t1)), run_time=0.8)

        # —— 块外用同一族名：字体缓存里已有，照常能排 ——
        t2 = Text("outside the with-block", font="Arial", font_size=36,
                  color=TEAL).move_to([0, -0.8, 0])
        win.play(Write(t2), FadeIn(cap("块外沿用同一族名", t2)), run_time=0.8)

        # —— 不注册时的对照：用系统里没有的族名会打警告并回退 ——
        t3 = Text("fallback family", font_size=36, color=GREY_B).move_to([0, -2.2, 0])
        win.play(Write(t3), FadeIn(cap("未注册的族名会回退到默认字体", t3)), run_time=0.8)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：`with register_font(r"C:\Windows\Fonts\arial.ttf"):` 里用 `font="Arial"` 排一行字；退出 `with` 后再用同一族名仍能排（字体缓存已登记）；最后一行不给 `font`，用默认字体做对照——说明注册的是"族名到文件"的映射。

<video src="assets/RTM output/08-文本Text-registerfont.mp4" controls width="560"></video>

> 提醒：注册是按**字体文件里的族名**生效的（不是文件名）；`with` 块只影响注册时机、不影响之后使用（同一进程内缓存），换进程要重新注册。

---

相关：[LaTeX 公式](09-LaTeX公式.md) · [Typst](10-Typst.md) · [容器与组合](06-容器与组合.md)
