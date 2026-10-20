# Succession：顺序播放

手册「八、组合动画」后半：一个播完再播下一个的串行编排，同一时刻只有一个子动画在跑。走 RTM 自有实现实测可渲，`Wait` 可直接当子动画留白。

## 参数

### Succession

```python
Succession(*animations, lag_ratio=1, **kwargs)
```

继承 `Succession(AnimationGroup)`，来源 `animation/composition.py`。**一个播完再播下一个**（`lag_ratio` 固定默认 `1`，即 100% 接续），用于编排叙事顺序：等待 → 加入 → 等待 → 变形……把若干段动作收进一次 `play`。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `*animations` | `Animation \| Iterable[Animation]` | — | 子动画（列表/生成器会被自动展平；每个都会经 `prepare_animation` 转换）。**能填** 任意动画、`.animate` 构建器与 `Wait` |
| `lag_ratio` | `float` | `1` | 固定默认 100% 接续；改成小于 1 可让相邻动画重叠。RTM 自有 `Succession` 现继承 RTM `AnimationGroup`，该形参生效 |
| `**kwargs` | `Any` | — | 同 `AnimationGroup`：`group`、`run_time=None`、`rate_func=linear` 与 `Animation` 通用参数；`run_time` 现被接收：非 `None` 时等比拉伸整条串行轴（`None` = 各子动画 `run_time` 之和） |

> **返回**：`Animation`（交给 `play` 播放）。

> `Wait`（已支持）可以作为子动画直接放进 `Succession` 时间轴，用来在两段动作之间留白；`Animation` 基类也可直接实例化占位（见[等待、速率与变速](../等待与变速/01-等待速率与变速.md)）。`AnimationGroup` 与 `LaggedStart`/`LaggedStartMap` 的实测结论见 [01-AnimationGroup与错峰](01-AnimationGroup与错峰.md)。

#### 样例：动→动→留白→变色，四段一次 play 排完

三个方块排开，一次 `play` 把"移动→移动→`Wait` 留白→变色"四段动作全部排进串行时间轴。

```python
from real_time_manim import Scene, Text, VGroup, Square, BLUE, GREEN, GREY_B, RED, YELLOW, \
    UP, DOWN, LEFT, RIGHT, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Succession, Wait

class SuccessionDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-Succession", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("Succession(sq1.animate.move_to(sq2),", font_size=30, color=GREY_B)
        l2 = Text("           sq2.animate.move_to(sq3), Wait(0.6),", font_size=30, color=GREY_B)
        l3 = Text("           sq3.animate(run_time=0.8).set_color(RED))", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        sq1 = Square(side_length=1.1, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 3.6 + DOWN * 2.1)   #蓝色方块
        sq2 = Square(side_length=1.1, color=GREEN).set_fill(GREEN, 0.5).shift(DOWN * 2.1)   #绿色方块
        sq3 = Square(side_length=1.1, color=GREY_B).shift(RIGHT * 3.6 + DOWN * 2.1)   #灰色方块
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(sq1, sq2, sq3)), run_time=0.4)   #标签与方块淡入
        win.play(Succession(                                      #参数 “*animations”（4 个子动画）
            sq1.animate(run_time=1.0).move_to(sq2.get_center()),
            sq2.animate(run_time=1.0).move_to(sq3.get_center()),
            Wait(0.6),                                            #参数 “*animations”（Wait 直接当空段）
            sq3.animate(run_time=0.8).set_color(RED),
        ))
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：蓝块先移到绿块位置（1 秒），绿块再移到灰块位置（1 秒），接着 `Wait(0.6)` 原地留白 0.6 秒，最后灰块在 0.8 秒内变成红色。四段收进一次 `play`，同一时刻只有一个小段在动，顺序绝对可靠（对比 `AnimationGroup` 的并行/错峰）；未传组级 `run_time` 时总时长就是各子动画 `run_time` 之和。

<video src="assets/RTM output/02-Succession顺序播放-succession.mp4" controls width="560"></video>

> 提醒：`Succession` 未传组级 `run_time` 时总时长 = 各子动画 `run_time` **之和**；传 `run_time` 会等比拉伸整条串行轴。`Wait` 直接当子动画传即可。想要子动画**重叠**可把 `lag_ratio` 改成小于 1，或改用 `AnimationGroup(lag_ratio=0.5)` / `LaggedStart`。

#### 样例：rate_func=smooth 作用于整条串行时间轴

两个圆依次上移，组级 `rate_func=smooth` 作用于整条串行时间轴。

```python
from real_time_manim import Scene, Text, VGroup, Circle, RED, BLUE, GREY_B, YELLOW, UP, \
    DOWN, LEFT, RIGHT, FadeIn, Write, smooth
from real_time_manim.vulkan_bind import MLWindow, Succession, Wait

class SuccessionRateFuncDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02-SuccessionRateFunc", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("Succession(a.animate.shift(UP), b.animate.shift(UP),", font_size=30, color=GREY_B)
        l2 = Text("           rate_func=smooth)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        a = Circle(radius=0.55, color=RED).set_fill(RED, 0.5).shift(LEFT * 2.2 + DOWN * 2.3)   #红色圆
        b = Circle(radius=0.55, color=BLUE).set_fill(BLUE, 0.5).shift(RIGHT * 2.2 + DOWN * 2.3)   #蓝色圆
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(a, b)), run_time=0.4)   #标签与圆淡入
        win.play(Succession(                                      #参数 “rate_func”（作用于整条串行时间轴）
            a.animate(run_time=1.0).shift(UP * 1.6),
            b.animate(run_time=1.0).shift(UP * 1.6),
            rate_func=smooth,
        ))
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：两个圆一前一后上移，`smooth` 作为**组级** `rate_func` 作用于整条串行时间轴——整段的起步与收尾是缓动的，中间接续处也平滑，而不是每个子动画各自缓动一次。

<video src="assets/RTM output/02-Succession顺序播放-ratefunc.mp4" controls width="560"></video>

> 提醒：组级 `rate_func` 作用的是**整条串行时间轴**（起步/收尾缓动、接缝平滑）；想单独调某个子动画的节奏，把 `rate_func` 写进那个子动画自己的构造里。

### 与错峰的区别

| | `Succession` | `AnimationGroup(lag_ratio=...)` | `LaggedStart` |
| --- | --- | --- | --- |
| 默认节奏 | `lag_ratio=1` 完全串行 | `lag_ratio=0` 完全并行 | `lag_ratio=0.05` 微错峰 |
| 同一时刻 | 只有一个子动画 | 全部/按比例重叠 | 大部分重叠 |
| 典型用途 | 叙事顺序、分步讲解 | 并列动作、整体编排 | 流水式逐个出现 |

无法演示：`lag_ratio` —— 已支持，本页不演示；`run_time` —— 已支持（非 `None` 时等比拉伸整条串行轴），本页不演示（样例未传，默认即各子动画 `run_time` 之和）。

---

相关：[AnimationGroup 与错峰](01-AnimationGroup与错峰.md) · [等待、速率与变速](../等待与变速/01-等待速率与变速.md) · [更新器动画与自动变化](../更新器动画/01-更新器动画与自动变化.md)
