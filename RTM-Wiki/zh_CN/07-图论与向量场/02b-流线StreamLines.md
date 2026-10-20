# 流线 StreamLines

在网格上撒"质点"，用欧拉法沿场积分出轨迹并画成平滑曲线，直观表现流动方向；颜色默认按场强在渐变色上取。**创建时会做完整段轨迹模拟**，所以 `virtual_time` 越大创建越慢。RTM 没有专门实现流线，走通用矢量回退出图——实测逐条创建、持续流动、平滑收束全部正常（见下方各样例）。

## class StreamLines（RTM 通用矢量回退渲染）

```python
StreamLines(func: Callable[[np.ndarray], np.ndarray], color: ParsableManimColor | None = None, color_scheme: Callable[[np.ndarray], float] | None = None, min_color_scheme_value: float = 0, max_color_scheme_value: float = 2, colors: Sequence[ParsableManimColor] = DEFAULT_SCALAR_FIELD_COLORS, x_range: Sequence[float] = None, y_range: Sequence[float] = None, z_range: Sequence[float] = None, three_dimensions: bool = False, noise_factor: float | None = None, n_repeats = 1, dt = 0.05, virtual_time = 3, max_anchors_per_line = 100, padding = 3, stroke_width = 1, opacity = 1, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `func` | `Callable` | 必填 | 场函数 |
| `color` / `color_scheme` / `min_color_scheme_value` / `max_color_scheme_value` / `colors` | 同 `ArrowVectorField` | 同上 | 配色相关 |
| `x_range` / `y_range` / `z_range` | `Sequence[float] \| None` | `None` | 质点**出生区域**（`[min, max, step]`） |
| `three_dimensions` | `bool` | `False` | 三维流线 |
| `noise_factor` | `float \| None` | `None` → `step_y / 2` | 每个出生点的随机抖动幅度（避免完全规整） |
| `n_repeats` | `int` | `1` | 每个出生点撒几个质点 |
| `dt` | `float` | `0.05` | 积分步长，越小轨迹越准 |
| `virtual_time` | `float` | `3` | 每条流线模拟的"时长"，越大线越长、创建越慢 |
| `max_anchors_per_line` | `int` | `100` | 每条线最多锚点数，超出会抽稀（降复杂度不降长度） |
| `padding` | `float` | `3` | 质点跑出出生区多远后终止 |
| `stroke_width` | `float` | `1` | 线宽 |
| `opacity` | `float` | `1` | 不透明度 |
| `**kwargs` | - | - | 透传给 `VectorField` |

**返回** `StreamLines`；所有流线存在 `stream_lines` 属性里。

### 动画方法

| 签名 | 频率 | 作用 |
| --- | --- | --- |
| `create(lag_ratio=None, run_time=None, **kwargs) -> AnimationGroup` | 🔴 | 逐条**随机顺序**画出流线；`run_time` 缺省取 `virtual_time`，`lag_ratio` 缺省取 `run_time/2/条数` |
| `start_animation(warm_up=True, flow_speed=1, time_width=0.3, rate_func=linear, line_animation_class=ShowPassingFlash, **kwargs) -> None` | 🔴 | 开始**持续流动**动画（挂 updater，无返回值）；`warm_up=True` 先逐条亮起，`time_width` 是同时可见的线段比例 |
| `end_animation() -> AnimationGroup` | 🔴 | 平滑收束持续动画（未 `start_animation` 会抛 `ValueError`），返回可 `play` 的动画 |

#### 样例：create 逐条随机顺序画出

`sx*sin + sy*cos` 的场，出生网格 `x∈[-4,4]`、`y∈[-2.5,2.5]` 步长 1，蓝色 3 号线宽、锚点抽到 15、`virtual_time=1` 控制创建成本，`sl.create(run_time=1.4)` 逐条随机顺序画出。

```python
import numpy as np
from real_time_manim import Scene, Text, StreamLines, \
    BLUE, YELLOW, GREY_B, UP, DOWN, LEFT, \
    Write, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class StreamLinesCreateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02b-StreamLines-create", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text("sl.create(run_time=..., lag_ratio=...)",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.3)   #签名标签
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        func = lambda pos: np.sin(pos[0] / 2) * UP + np.cos(pos[1] / 2) * LEFT   #场函数
        sl = StreamLines(
            func,                                   #参数 “func”
            x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],   #出生网格
            color=BLUE,                             #参数 “color”：整体蓝色
            stroke_width=3,                         #参数 “stroke_width”
            max_anchors_per_line=15,                #抽稀锚点：创建更快、线更顺
            virtual_time=1,                         #参数 “virtual_time”：轨迹模拟时长
        )
        win.play(sl.create(run_time=1.4), run_time=1.4)   #逐条随机顺序画出
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：构造时就已经把每条流线的完整轨迹积分出来了（`virtual_time=1` 只模拟 1 个虚拟秒，配合 `max_anchors_per_line=15` 抽稀，创建很快），随后 `sl.create(run_time=1.4)` 把这批曲线**随机顺序**逐条画出来——默认 `lag_ratio` 会按 `run_time/2/条数` 自动摊开，所以整段是错落生长的节奏。

<video src="assets/RTM output/02b-流线StreamLines-create.mp4" controls width="560"></video>

> 提醒：`create()` 的 `run_time` **缺省取 `virtual_time`**——不显式给就会出现"等 3 秒才画完"的错觉；`virtual_time` 越大构造越慢（创建时整段轨迹都积完了），大图请先调小它或 `max_anchors_per_line`。

#### 样例：start_animation / end_animation 持续流动

同一张流线先 `create` 画出来，再 `start_animation(warm_up=False, flow_speed=1.5, time_width=0.5)` 挂上持续流动，2 秒后 `win.play(sl.end_animation(), ...)` 平滑收束。

```python
import numpy as np
from real_time_manim import Scene, Text, StreamLines, \
    BLUE, YELLOW, GREY_B, UP, DOWN, LEFT, \
    Write, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class StreamLinesFlowDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02b-StreamLines-flow", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text("start_animation(flow_speed=1.5, time_width=0.5) ... end_animation()",
                   font_size=24, color=GREY_B).next_to(title, DOWN, buff=0.3)   #签名标签
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        func = lambda pos: np.sin(pos[0] / 2) * UP + np.cos(pos[1] / 2) * LEFT   #场函数
        sl = StreamLines(
            func,                                   #参数 “func”
            x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],   #出生网格
            color=BLUE,                             #参数 “color”：整体蓝色
            stroke_width=3,                         #参数 “stroke_width”
            max_anchors_per_line=15,                #抽稀锚点
            virtual_time=1,                         #参数 “virtual_time”
        )
        win.play(sl.create(run_time=0.8), run_time=0.8)   #先把流线画出来
        self.add(sl)   #把 “sl” 收进场景：updater 挂在它身上，不 add 就整片黑屏
        sl.start_animation(warm_up=False, flow_speed=1.5, time_width=0.5)   #参数 “flow_speed” / “time_width”
        win.play(Wait(2.0))   #光点沿线持续流动 2 秒
        win.play(sl.end_animation(), run_time=0.6)   #平滑收束持续动画
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：`start_animation` 是**直接挂 updater**（没有返回值，不能单独 `play`），所以放在 `win.play(Wait(2.0))` 前面调用即可——`flow_speed=1.5` 决定光点跑多快，`time_width=0.5` 决定同时亮着的线段占整条的多少，`warm_up=False` 跳过"逐条预热亮起"直接流动。最后 `end_animation()` 返回一个可 `play` 的动画，把持续效果平滑收掉。中间那行 `self.add(sl)` 不能省：`create` 只是把**每条线**放进场景，`sl` 这个组本身没入场景，而 updater 挂在 `sl` 上——不 add 它，`begin()` 已经把线裁成空的，updater 又永远不跑，画面就是一片黑（实测两引擎同黑）。

<video src="assets/RTM output/02b-流线StreamLines-flow.mp4" controls width="560"></video>

> 提醒：`end_animation()` 在**没调用过** `start_animation` 时会抛 `ValueError`；反过来，只 `start_animation` 不收束也能渲（画面停在流动状态），但两条必须成对出现才讲得清这对 API。持续动画期间 `Wait` 里光点一直在走，帧与帧内容不同，两引擎的光点相位可能有细微差别属正常。**最要命的坑是忘 `self.add(sl)`**——症状是开始流动后整片流线消失且不报错。

---

相关：[向量场与流线](02-向量场与流线.md) · [Graph 与 DiGraph](01-Graph与DiGraph.md) · [图的增删与布局](01b-图的增删与布局.md)
