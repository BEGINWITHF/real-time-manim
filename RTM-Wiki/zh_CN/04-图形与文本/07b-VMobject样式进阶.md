# VMobject 样式（二）：透明度、光泽与路径处理

承接[VMobject 样式（一）](07-VMobject样式.md)：透明度、光泽渐变、路径平滑/截取、端点样式等其余 `VMobject` 样式方法。每个方法各一条样例，样例里把该方法**全部可填参数**各改一次。

## 参数

### `VMobject.set_opacity`

```python
def set_opacity(self, opacity: float, family: bool = True) -> Self:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `opacity` | `float` | 必填 | 0~1。**能填**任意 0~1 的数；它同时改填充与描边（样例 0.25 / 0.6 / 1.0 三档） |
| `family` | `bool` | `True` | 是否连子对象一起改。`True` 时容器与子对象一起降；`False` 只改容器自己，子对象保持各自的不透明度（样例两组并排对比） |

#### 样例：三档不透明度 + `family` 两种取值

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class OpacityDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-set_opacity", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— opacity 三档：0.25 / 0.6 / 1.0（不调用就是 1.0）——
        for i, op in enumerate([0.25, 0.6, 1.0]):
            sq = Square(side_length=1.3, color=BLUE).set_fill(BLUE, 0.9)
            sq.move_to([-4.0 + i * 1.8, 1.3, 0])
            sq.set_opacity(op)   #参数 “opacity”：填充与描边一起变
            cap = Text("opacity=%.2f" % op, font_size=18, color=GREY_B).next_to(sq, DOWN, buff=0.2)
            win.play(Create(sq), FadeIn(cap), run_time=0.45)   #逐个画 + 字幕

        # —— family：同一个 VGroup，True 连子对象一起改，False 只改容器自己 ——
        g1 = VGroup(Square(side_length=0.9, color=GREEN).set_fill(GREEN, 0.9),
                    Circle(radius=0.5, color=GREEN).set_fill(GREEN, 0.9))
        g1.arrange(RIGHT, buff=0.3).move_to([-2.6, -1.4, 0])
        g1.set_opacity(0.3, family=True)   #参数 “family=True”：容器与子对象一起降
        cap1 = Text("family=True", font_size=18, color=GREY_B).next_to(g1, DOWN, buff=0.2)
        win.play(FadeIn(g1), FadeIn(cap1), run_time=0.5)   #两个子对象都变淡

        g2 = VGroup(Square(side_length=0.9, color=ORANGE).set_fill(ORANGE, 0.9),
                    Circle(radius=0.5, color=ORANGE).set_fill(ORANGE, 0.9))
        g2.arrange(RIGHT, buff=0.3).move_to([2.6, -1.4, 0])
        g2.set_opacity(0.3, family=False)   #参数 “family=False”：只改容器
        cap2 = Text("family=False", font_size=18, color=GREY_B).next_to(g2, DOWN, buff=0.2)
        win.play(FadeIn(g2), FadeIn(cap2), run_time=0.5)   #子对象保持自己的 0.9
        win.play(Wait(0.5))   #停留对比两组
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：set_sheen / set_sheen_direction —— 光泽渐变 ==================
```

这段代码在做什么：第一行三个方块分给 `opacity` 0.25 / 0.6 / 1.0，越右越实。

下面两组 `VGroup`（方块 + 圆）都用 0.3，唯一区别是 `family`：左边 `True` 连子对象一起变淡；右边 `False` 只改容器本身，两个子对象保持各自的 0.9，所以看起来还是实心。

<video src="assets/RTM output/07b-VMobject样式进阶-opacity.mp4" controls width="560"></video>

> 提醒：`set_opacity` 会**同时**改填充和描边，这才是它和 `set_fill(BLUE, 0.3)` 的区别。叶子对象上 `family` 没有可见差别，只有容器（`VGroup`/`Text`）上两种取值才看得出。

### `VMobject.set_sheen`

```python
def set_sheen(self, factor: float, direction: Vector3DLike | None = None, family: bool = True) -> Self:
def set_sheen_direction(self, direction: Vector3DLike, family: bool = True) -> Self:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `factor` | `float` | 必填 | 光泽强度。0 关闭（回到纯色），常用 0.2~1.5；样例 0.0 / 0.6 / 1.5 |
| `direction` | `array-like \| None` | `None` | 渐变方向；不填沿用对象已有的 `sheen_direction`；样例 `UP` / `RIGHT` 各一次 |
| `family` | `bool` | `True` | 是否应用到子对象 |
| `set_sheen_direction(direction, family=True)` | 方法 | — | 单独改方向、强度沿用上一次的 `factor`（样例先 `set_sheen(1.0, UP)` 再改成 `DOWN`） |

#### 样例：三档强度 + 两个方向 + 单独改方向

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class SheenDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-set_sheen", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— factor 三档 ——
        for i, f in enumerate([0.0, 0.6, 1.5]):
            sq = Square(side_length=1.2, color=BLUE).set_fill(BLUE, 1.0)
            sq.move_to([-4.0 + i * 1.7, 1.3, 0])
            sq.set_sheen(f, direction=UP)   #参数 “factor / direction=UP”
            cap = Text("factor=%.1f" % f, font_size=18, color=GREY_B).next_to(sq, DOWN, buff=0.2)
            win.play(Create(sq), FadeIn(cap), run_time=0.45)   #0 关闭 / 0.6 / 1.5

        # —— direction 换成 RIGHT，光泽改成从左到右 ——
        sq2 = Square(side_length=1.2, color=TEAL).set_fill(TEAL, 1.0).move_to([1.4, -1.2, 0])
        sq2.set_sheen(1.0, direction=RIGHT)   #参数 “direction=RIGHT”
        cap2 = Text("direction=RIGHT", font_size=18, color=GREY_B).next_to(sq2, DOWN, buff=0.2)
        win.play(Create(sq2), FadeIn(cap2), run_time=0.5)

        # —— set_sheen_direction：单独改方向，强度沿用上一次的 factor ——
        sq3 = Square(side_length=1.2, color=PURPLE).set_fill(PURPLE, 1.0).move_to([4.4, -1.2, 0])
        sq3.set_sheen(1.0, direction=UP)   #先按 UP
        sq3.set_sheen_direction(DOWN)   #再单独改方向（family 默认 True）
        cap3 = Text("set_sheen_direction(DOWN)", font_size=18, color=GREY_B).next_to(sq3, DOWN, buff=0.2)
        win.play(Create(sq3), FadeIn(cap3), run_time=0.5)
        win.play(Wait(0.5))   #停留看渐变方向
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：make_smooth —— 折线变平滑曲线 ==============================
```

这段代码在做什么：上面三个蓝方块只差 `factor`——0 是纯色、0.6 有淡淡的高光、1.5 几乎变成白到蓝的渐变。

下面两个单独演示方向：青方块 `direction=RIGHT` 变成左右渐变；紫方块先 `set_sheen(1.0, UP)`，再用 `set_sheen_direction(DOWN)` 把方向翻过来，强度不用再传。

<video src="assets/RTM output/07b-VMobject样式进阶-sheen.mp4" controls width="560"></video>

> 提醒：光泽是**填充**的渐变，描边不参与。`direction` 给的是渐变指向（高光在**反方向**那一端），所以 `UP` 看起来是"顶上亮、往下暗"。多 stop 的自定义渐变色也能画（引擎取首尾两站走原生线性渐变）。

### `VMobject.make_smooth`

```python
def make_smooth(self) -> Self:
```

无参数，直接对对象调用。把当前路径的角点改成平滑锚点（等价于 `change_anchor_mode("smooth")`），用来"折线变曲线"。

#### 样例：同一条折线的原样与平滑版并排

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class MakeSmoothDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-make_smooth", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        verts = [[-3.2, 1.0, 0], [-1.6, -0.6, 0], [-0.2, 1.2, 0], [1.4, -0.4, 0]]   #折线顶点
        raw = Polygon(*verts, color=GREY_B, stroke_width=5)   #原样（折角）
        smoothed = Polygon(*verts, color=GREEN, stroke_width=5)   #待平滑的那份
        smoothed.make_smooth()   #把角点改成平滑锚点：折线变曲线
        raw.shift(DOWN * 1.4)   #上：原样
        smoothed.shift(DOWN * 1.4)
        cap1 = Text("jagged (raw)", font_size=20, color=GREY_B).next_to(raw, UP, buff=0.25)
        cap2 = Text("make_smooth()", font_size=20, color=GREEN).next_to(smoothed, UP, buff=0.25)
        win.play(Create(raw), FadeIn(cap1), run_time=0.6)   #先看折线
        win.play(Create(smoothed), FadeIn(cap2), run_time=0.6)   #再看平滑后的同一条路径
        win.play(Wait(0.5))   #停留对比
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：make_jagged —— 平滑曲线改回折线 ============================
```

这段代码在做什么：同一组顶点画两份——灰色那份保持折角，绿色那份调用 `make_smooth()`。两条路径先后画出来，绿色那条在原来每个拐角处都鼓成了弧，这就是"折线变曲线"；顶点个数与位置都没变，变的只是锚点模式。

<video src="assets/RTM output/07b-VMobject样式进阶-smooth.mp4" controls width="560"></video>

> 提醒：`make_smooth()` 是**就地**改这个对象（返回 `self`，可以链式），想保留原始折线就 `poly.copy().make_smooth()`。

### `VMobject.make_jagged`

```python
def make_jagged(self) -> Self:
```

无参数。`make_smooth()` 的反操作：把平滑锚点改回折角（等价于 `change_anchor_mode("jagged")`）。

#### 样例：同一个圆的原样与"折线版"

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class MakeJaggedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-make_jagged", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        circle = Circle(radius=1.2, color=BLUE).set_fill(BLUE, 0.3)   #圆本身就是平滑的
        circle.move_to(LEFT * 2.2 + DOWN * 0.6)
        jagged = Circle(radius=1.2, color=ORANGE).set_fill(ORANGE, 0.3)
        jagged.make_jagged()   #把平滑锚点改回折角：圆变成多边形
        jagged.move_to(RIGHT * 2.2 + DOWN * 0.6)
        cap1 = Text("Circle (smooth)", font_size=20, color=BLUE).next_to(circle, UP, buff=0.25)
        cap2 = Text("make_jagged()", font_size=20, color=ORANGE).next_to(jagged, UP, buff=0.25)
        win.play(Create(circle), FadeIn(cap1), run_time=0.6)   #先看圆
        win.play(Create(jagged), FadeIn(cap2), run_time=0.6)   #再看同半径的"折线圆"
        win.play(Wait(0.5))   #停留对比
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：pointwise_become_partial —— 沿路径截取一段 ==================
```

这段代码在做什么：两个半径相同的圆，右边那个调用 `make_jagged()` 后轮廓变成多边形（点数不变，每段之间不再平滑过渡），一眼看出它是在同一批点上切换锚点模式，而不是真的重建了一个多边形。

<video src="assets/RTM output/07b-VMobject样式进阶-jagged.mp4" controls width="560"></video>

> 提醒：`make_jagged` 之后对象仍然是 VMobject、仍然可填充，只是轮廓不再是曲线；要恢复曲线再调用 `make_smooth()`。

### `VMobject.pointwise_become_partial`

```python
def pointwise_become_partial(self, vmobject: VMobject, a: float, b: float) -> Self:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `vmobject` | `VMobject` | 必填 | 源对象（读它的路径） |
| `a` | `float` | 必填 | 起始比例 0~1（沿路径） |
| `b` | `float` | 必填 | 结束比例 0~1；`[0, 1]` 就是整条路径 |

#### 样例：四段四分之一 + 整条路径

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class PartialDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-pointwise_become_partial", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 同一条圆，四段 [a, b] 各截一次 ——
        spans = [(0.0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0)]   #参数 “a / b”
        for i, (a, b) in enumerate(spans):
            src = Circle(radius=0.9, color=TEAL, stroke_width=6)   #源对象
            part = Circle(radius=0.9)   #接收截取结果的对象
            part.pointwise_become_partial(src, a, b)   #参数 “vmobject / a / b”
            part.set_stroke(TEAL, 6)
            part.move_to([-4.0 + i * 2.2, 1.2, 0])
            cap = Text("[%.2f, %.2f]" % (a, b), font_size=18, color=GREY_B).next_to(part, DOWN, buff=0.25)
            win.play(Create(part), FadeIn(cap), run_time=0.45)   #四段四分之一弧

        # —— [0, 1] 就是整条路径（与源对象等长）——
        src = Circle(radius=0.9, color=GOLD, stroke_width=6)
        whole = Circle(radius=0.9)
        whole.pointwise_become_partial(src, 0, 1)   #a=0, b=1：整条
        whole.set_stroke(GOLD, 6).move_to([-1.0, -1.4, 0])
        cap = Text("[0, 1] = whole path", font_size=18, color=GREY_B).next_to(whole, DOWN, buff=0.25)
        win.play(Create(whole), FadeIn(cap), run_time=0.5)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 6：get_stroke_width —— 读出当前线宽 ============================
```

这段代码在做什么：同一半径的圆当源，四个"接收对象"分别 `pointwise_become_partial(src, a, b)`，于是每个只拿到四分之一段弧，字幕标着各自的 `[a, b]`。最后一条 `[0, 1]` 拿到整条路径，弧长与源对象一致——这就是 `ShowPassingFlash` 一类"只显现一段"效果的底层方法。

<video src="assets/RTM output/07b-VMobject样式进阶-partial.mp4" controls width="560"></video>

> 提醒：`a > b` 不报错但拿到的是反向（空/逆向）路径；`a == b` 会退化成一点。实际做扫光效果时一般让 `b - a` 固定、整体平移这个窗口。

### `VMobject.get_stroke_width`

```python
def get_stroke_width(self, background: bool = False) -> float:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `background` | `bool` | `False` | `False` 读当前描边宽度；`True` 读背景描边宽度（没设置过就是 0） |

返回 `float`。

#### 样例：读线宽 → 改线宽 → 再读

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class GetWidthDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-get_stroke_width", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ln = Line([-4.4, 1.0, 0], [-0.4, 1.0, 0], color=BLUE, stroke_width=4)   #初始线宽 4
        info = Text("get_stroke_width() = %.1f" % ln.get_stroke_width(), font_size=24, color=WHITE)
        info.next_to(ln, DOWN, buff=0.4)
        win.play(Create(ln), FadeIn(info), run_time=0.5)   #读出来是 4.0

        ln.set_stroke(width=14)   #改线宽
        info.become(Text("after set_stroke(width=14) = %.1f" % ln.get_stroke_width(),
                         font_size=24, color=WHITE).next_to(ln, DOWN, buff=0.4))
        win.play(Create(ln), run_time=0.4)   #线变粗
        win.play(FadeIn(info), run_time=0.3)   #读出来变 14.0

        # —— background=True：读的是"背景描边宽度"（默认 0，未设置过就是 0）——
        info2 = Text("get_stroke_width(background=True) = %.1f" % ln.get_stroke_width(background=True),
                     font_size=24, color=ORANGE).next_to(info, DOWN, buff=0.25)
        win.play(FadeIn(info2), run_time=0.4)   #参数 “background=True”
        win.play(Wait(0.5))   #停留看读数
        win.close()   #关闭 RTM 窗口


# ===== 样例 7：set_cap_style —— 三种线端点样式 ============================
```

这段代码在做什么：先用 `stroke_width=4` 画一条线，把 `get_stroke_width()` 的读数打在字幕上（4.0）；接着 `set_stroke(width=14)` 把线加粗，同一个读数变成 14.0；最后一行显示 `background=True` 的读数——它是"背景描边"通道，这个对象从没设置过，所以是 0.0。

<video src="assets/RTM output/07b-VMobject样式进阶-strokewidth.mp4" controls width="560"></video>

> 提醒：读数就是构造/`set_stroke` 时给的值（不随 `scale()` 变），拿它做线宽补偿时要自己乘缩放系数。

### `VMobject.set_cap_style`

```python
def set_cap_style(self, cap_style: CapStyleType) -> Self:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `cap_style` | `CapStyleType` | 必填 | 线端点样式。可填 `CapStyleType.ROUND`（圆头）/ `BUTT`（平头，正好在端点停住）/ `SQUARE`（方头，会往两端各伸出半个线宽）/ `AUTO`（跟随描边默认） |

#### 样例：三种端点样式，粗线才看得清

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class CapStyleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-set_cap_style", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        from manim import CapStyleType   #三种端点样式的枚举
        styles = [("ROUND", CapStyleType.ROUND), ("BUTT", CapStyleType.BUTT),
                  ("SQUARE", CapStyleType.SQUARE)]   #参数 “cap_style”
        for i, (name, style) in enumerate(styles):
            ln = Line([-4.4, 1.4 - i * 1.5, 0], [-1.2, 1.4 - i * 1.5, 0],
                      color=TEAL, stroke_width=40)   #粗线才看得清端点
            ln.set_cap_style(style)   #参数 “cap_style=CapStyleType.%s” % name
            cap = Text("CapStyleType.%s" % name, font_size=20, color=GREY_B).next_to(ln, RIGHT, buff=0.4)
            win.play(Create(ln), FadeIn(cap), run_time=0.5)   #三种端点依次出现
        win.play(Wait(0.5))   #停留对比
        win.close()   #关闭 RTM 窗口


# ===== 样例 8：change_anchor_mode —— smooth / jagged 两档 =================
```

这段代码在做什么：三条一样长、一样粗（`stroke_width=40`）的线，从上到下依次设成 `ROUND` / `BUTT` / `SQUARE`：圆头两端鼓成半圆，平头正好停在端点，方头往两侧各伸出半个线宽（所以看起来最长）。线细的时候这三种几乎看不出差别，必须用粗线演示。

<video src="assets/RTM output/07b-VMobject样式进阶-capstyle.mp4" controls width="560"></video>

> 提醒：它是**描边**属性，只影响开放路径的两端；闭合路径（圆、矩形）没有端点，设了也看不出区别。

### `VMobject.change_anchor_mode`

```python
def change_anchor_mode(self, mode: Literal["jagged", "smooth"]) -> Self:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mode` | `str` | 必填 | 只接受 `"smooth"`（平滑）与 `"jagged"`（折角）两档，正是 `make_smooth`/`make_jagged` 的底层开关 |

#### 样例：同一组顶点的平滑档与折角档

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class AnchorModeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-change_anchor_mode", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        verts = [[-3.0, 0.8, 0], [-1.4, -0.8, 0], [0.2, 1.0, 0], [1.8, -0.6, 0]]
        smooth = Polygon(*verts, color=GREEN, stroke_width=5)
        smooth.change_anchor_mode("smooth")   #参数 “mode="smooth"”
        smooth.shift(UP * 0.9 + LEFT * 1.4)
        jagged = Polygon(*verts, color=ORANGE, stroke_width=5)
        jagged.change_anchor_mode("jagged")   #参数 “mode="jagged"”
        jagged.shift(DOWN * 1.2 + LEFT * 1.4)
        cap1 = Text('mode="smooth"', font_size=20, color=GREEN).next_to(smooth, RIGHT, buff=0.4)
        cap2 = Text('mode="jagged"', font_size=20, color=ORANGE).next_to(jagged, RIGHT, buff=0.4)
        win.play(Create(smooth), FadeIn(cap1), run_time=0.6)   #平滑档
        win.play(Create(jagged), FadeIn(cap2), run_time=0.6)   #折角档
        win.play(Wait(0.5))   #停留对比
        win.close()   #关闭 RTM 窗口


# ===== 样例 9：apply_function —— 自定义形变与参考点 ========================
```

这段代码在做什么：同一组顶点画两份，一份 `change_anchor_mode("smooth")`、一份 `"jagged"`，两档上下并排——绿色那条在拐角处是弧，橙色那条是硬折角；`make_smooth()` / `make_jagged()` 就是这两个取值的封装。

<video src="assets/RTM output/07b-VMobject样式进阶-anchor.mp4" controls width="560"></video>

> 提醒：`mode` 只认 `"smooth"`/`"jagged"` 两个字符串（早期文档里写的 `"corners"` 是不对的，会抛 `ValueError`）。

### `VMobject.apply_function`（`about_point` / `about_edge` 上游无效）

```python
def apply_function(self, function: MappingFunction, *, about_point: Point3DLike | None = None, about_edge: Vector3DLike | None = None) -> Self:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `function` | `callable` | 必填 | 接收一个点、返回新点的函数；**能填**任意逐点映射（样例给了波浪、缩放、缩放+平移、只压 y 四种） |
| `about_point` | `array-like \| None` | `None` | **别指望**：ManimCE 0.21 的 `apply_function` 不读这个参数——传与不传结果完全一样（实测四种写法最终中心都是同一个），RTM 会按参考点变换，**两引擎画面会不同**，所以样例不演示它 |
| `about_edge` | `array-like \| None` | `None` | 同上（上游同样忽略） |

#### 样例：四种逐点映射

```python
import os
import subprocess
import sys
import numpy as np
from real_time_manim import (
    Scene, Square, Circle, Polygon, Line, Dot, Triangle, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI,
    Create, FadeIn, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class ApplyFunctionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("07b-apply_function", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 逐点扭曲：正弦波改 x ——
        wave = lambda p: p + 0.35 * np.sin(p[1] * PI) * RIGHT   #参数 “function”：逐点改 x
        a = Square(side_length=1.6, color=BLUE).set_fill(BLUE, 0.6).move_to([-3.6, 1.2, 0])
        a.apply_function(wave)   #参数 “function”
        cap1 = Text("apply_function(wave)", font_size=18, color=GREY_B).next_to(a, DOWN, buff=0.25)
        win.play(Create(a), FadeIn(cap1), run_time=0.5)   #方块被扭成波浪边

        # —— 整体放大：p * 1.5 ——
        b = Square(side_length=1.2, color=GREEN).set_fill(GREEN, 0.6).move_to([1.2, 1.2, 0])
        b.apply_function(lambda p: p * 1.5)   #参数 “function”：整体缩放
        cap2 = Text("function = p * 1.5", font_size=18, color=GREY_B).next_to(b, DOWN, buff=0.25)
        win.play(Create(b), FadeIn(cap2), run_time=0.5)   #方块整体变大

        # —— 缩放 + 平移：p * 0.8 + UP * 0.4 ——
        c = Square(side_length=1.2, color=RED).set_fill(RED, 0.6).move_to([1.2, -1.4, 0])
        c.apply_function(lambda p: p * 0.8 + UP * 0.4)   #参数 “function”：缩放后再整体上移
        cap3 = Text("function = p * 0.8 + UP * 0.4", font_size=18, color=GREY_B).next_to(c, DOWN, buff=0.25)
        win.play(Create(c), FadeIn(cap3), run_time=0.5)   #缩小并上移

        # —— 只改一个坐标：把 y 压扁 ——
        d = Square(side_length=1.2, color=PURPLE).set_fill(PURPLE, 0.6).move_to([4.2, -1.4, 0])
        d.apply_function(lambda p: p * [1.0, 0.5, 1.0])   #参数 “function”：只压 y
        cap4 = Text("function = p * [1, 0.5, 1]", font_size=18, color=GREY_B).next_to(d, DOWN, buff=0.25)
        win.play(Create(d), FadeIn(cap4), run_time=0.5)   #方块被压扁
        win.play(Wait(0.5))   #停留对比
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：四个方块各给一个 `function`。

- 正弦波把竖边扭成波浪；
- `p * 1.5` 整体放大；
- `p * 0.8 + UP * 0.4` 缩小并上移；
- `p * [1, 0.5, 1]` 只把 y 压到一半。

四种都是"逐点写真坐标"的写法，所以方块会真的变形（不是整体位移），`function` 返回的必须是 `[x, y, z]` 三个数。

<video src="assets/RTM output/07b-VMobject样式进阶-applyfunc.mp4" controls width="560"></video>

> 提醒：`function` 拿到的是**绝对坐标**（不是相对对象中心），所以 `p * 1.5` 会把对象推离原点——想让它在原地缩放，得自己写成 `center + (p - center) * 1.5`（把 `center` 先算出来存成变量）。

---

相关：[VMobject 样式（一）](07-VMobject样式.md) · [基本形状](01-基本形状.md) · [线与箭头](02-线与箭头.md)
