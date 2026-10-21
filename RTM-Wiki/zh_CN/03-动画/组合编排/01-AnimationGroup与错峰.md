# AnimationGroup 与错峰：LaggedStart / LaggedStartMap

手册「八、组合动画」前半，讲的是把多个动画当成一个播放的基础编排工具，以及它的两个流水式错峰变体。

`AnimationGroup` 走 RTM 自有实现。`LaggedStart` / `LaggedStartMap` 不在 RTM 自有导出清单里，用 manim 本体类经 RTM 时间轴渲染；流水错峰与批量套动画的效果都实测一致。

## 参数

### AnimationGroup

```python
AnimationGroup(*animations, group=None, run_time=None, rate_func=linear, lag_ratio=0, **kwargs)
```

继承 `AnimationGroup(Animation)`，来源 `animation/composition.py`。它把多个动画**当成一个动画**播放：`run_time=None` 时，总时长自动取"按 `lag_ratio` 排完的时间轴的最大结束时间"；给了 `run_time` 就整体拉伸/压缩到该时长。`lag_ratio` 决定**下一个动画在上一个播到多少比例时启动**（`start[i+1] = start[i] + run_time[i] * lag_ratio`）。

子元素可以是任意动画或 `.animate` 构建器，还能**嵌套** `AnimationGroup`。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `*animations` | `Animation \| Iterable[Animation]` | — | 子动画（列表/生成器会被自动展平；每个都会经 `prepare_animation` 转换）。**能填** 任意动画与 `.animate` 构建器 |
| `group` | `Group \| None` | `None` | 手动指定整组的容器；默认把所有非 introducer 子动画的 mobject 收进一个 `Group`。按 CE 语义接收（容器 mobjects 收进组、`get_all_mobjects()` 返回之） |
| `run_time` | `float \| None` | `None` | 总时长；`None` = 按子动画时间轴自动计算。现已支持构造器传入：非 `None` 时按 CE 语义整体拉伸/压缩子动画时间轴；属性赋值 `ag.run_time = 1.8` 继续有效（样例用的就是它） |
| `rate_func` | `Callable` | `linear` | **组级**速率函数（作用于整条时间轴；子动画各自还有自己的 `rate_func`）。**能填** `linear`、`smooth`… |
| `lag_ratio` | `float` | `0` | `0` 全部同时开始；`0.5` 下一个在上一个过半时开始；`1` 完全接续 |
| `**kwargs` | `Any` | — | `Animation` 通用参数（`name`、`remover`、`introducer`、`suspend_mobject_updating`…）；`synchronize_with_wall_clock` 不支持且**显式拒绝**：`True` 抛 `ValueError` |

> **返回**：`Animation`（交给 `play` 播放）。

组合技巧（手册同节）：

- `run_time=1.5` 传在 `play` 级别，可统一压平多个动画；
- `lag_ratio=0.3` 做"依次启动"；
- 嵌套组合时，外层管大节奏、内层管小动作；
- 外层 `lag_ratio=1`，即"前一组完全播完再播后一个"。

#### 样例：三个 .animate 依次启动，整轴拉伸到 1.8 秒

红方块、蓝圆、绿三角各配一个 `.animate.shift` 塞进 `AnimationGroup`，`lag_ratio=0.5` 让三个动作依次启动；`ag.run_time = 1.8` 属性赋值把整条时间轴拉伸到 1.8 秒。

```python
from real_time_manim import Scene, Text, VGroup, Square, Circle, Triangle, RED, BLUE, GREEN, \
    GREY_B, YELLOW, UP, DOWN, LEFT, RIGHT, FadeIn, Write, linear
from real_time_manim.vulkan_bind import MLWindow, AnimationGroup, Wait

class AnimationGroupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-AnimationGroup", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("AnimationGroup(sq.animate.shift(UP),", font_size=30, color=GREY_B)
        l2 = Text("              ci.animate.shift(DOWN), tr.animate.shift(UP),", font_size=28, color=GREY_B)
        l3 = Text("              lag_ratio=0.5, rate_func=linear);  ag.run_time = 1.8", font_size=28, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        sq = Square(side_length=1.2, color=RED).set_fill(RED, 0.5).shift(LEFT * 3.4 + DOWN * 2.1)   #红色方块
        ci = Circle(radius=0.65, color=BLUE).set_fill(BLUE, 0.5).shift(DOWN * 2.1)   #蓝色圆
        tr = Triangle(color=GREEN).scale(0.8).set_fill(GREEN, 0.5).shift(RIGHT * 3.4 + DOWN * 2.1)   #绿色三角
        win.play(FadeIn(sig, shift=DOWN), FadeIn(VGroup(sq, ci, tr)), run_time=0.4)   #标签与图形淡入
        ag = AnimationGroup(                                      #参数 “*animations”（3 个 .animate 构建器）
            sq.animate.shift(UP * 1.4),
            ci.animate.shift(DOWN * 1.4),
            tr.animate.shift(UP * 1.4),
            lag_ratio=0.5,                                        #参数 “lag_ratio”（红→蓝→绿依次启动）
            rate_func=linear,                                     #参数 “rate_func”（组级）
        )
        ag.run_time = 1.8                                         #参数 “run_time”（属性赋值整体拉伸到 1.8s）
        win.play(ag)   #三个动作依次启动
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：红方块先动，蓝圆要等红方块播过一半才起步，绿三角再等一轮——`lag_ratio=0.5` 就是"下一个在上一个播到 50% 时启动"。

三个动作收进一次 `play` 后，`ag.run_time = 1.8` 属性赋值把整条时间轴拉伸到 1.8 秒。

<video src="assets/RTM output/01-AnimationGroup与错峰-animationgroup.mp4" controls width="560"></video>

> 提醒：`lag_ratio` 是"**上一个播到多少比例**时启动下一个"，不是间隔几秒。
>
> - `0.5` = 过半
> - `1` = 完全接续
> - `0` = 全部同时
>
> `run_time` 构造器传入与属性赋值 `ag.run_time = 1.8` 均可。

### LaggedStart

```python
LaggedStart(*animations, lag_ratio=0.05, **kwargs)
```

继承 `LaggedStart(AnimationGroup)`，来源 `animation/composition.py`。它是 `AnimationGroup` 的便捷版：`lag_ratio` 默认 **0.05**，即"上一个播了 5% 就启动下一个"，用来制造**流水式错峰**效果。语义与 `AnimationGroup` 完全一致，只是默认错峰而不是同时。

样例用 manim 本体的 `LaggedStart` 经 RTM 时间轴渲染，实测错峰效果正常。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `*animations` | `Animation \| Iterable[Animation]` | — | 子动画，同 `AnimationGroup`。**能填** 如 `*[FadeIn(d, shift=DOWN) for d in dots]` |
| `lag_ratio` | `float` | `0.05` | 错峰比例（与 `AnimationGroup` 的 `0` 不同）。**能填** 0~1 |
| `**kwargs` | `Any` | — | 同 `AnimationGroup`：`group`、`run_time=None`、`rate_func=linear` 与 `Animation` 通用参数 |

> **返回**：`Animation`（交给 `play` 播放）。

#### 样例：5 个彩点流水式错峰淡入

5 个不同颜色的 `FadeIn` 交给 `LaggedStart`，错峰比例放大到 0.3，彩点像流水一样逐个淡入。

```python
from real_time_manim import Scene, Text, VGroup, Dot, RED, YELLOW, GREEN, BLUE, PURPLE, \
    GREY_B, UP, DOWN, LEFT, RIGHT, FadeIn, LaggedStart, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class LaggedStartDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-LaggedStart", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("LaggedStart(*[FadeIn(d, shift=DOWN) for d in dots],", font_size=30, color=GREY_B)
        l2 = Text("            lag_ratio=0.3, run_time=1.6)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        cols = [RED, YELLOW, GREEN, BLUE, PURPLE]   #5 个轨道的颜色
        dots = VGroup(*[Dot(radius=0.18, color=c).shift(LEFT * 4.4 + RIGHT * 2.2 * i + DOWN * 1.8)   #5 个彩色点
                        for i, c in enumerate(cols)])
        win.play(FadeIn(sig, shift=DOWN), run_time=0.4)   #标签淡入
        win.play(LaggedStart(                                    #参数 “*animations”（5 个不同颜色的 FadeIn）
            *[FadeIn(d, shift=DOWN) for d in dots],
            lag_ratio=0.3,                                       #参数 “lag_ratio”（流水式错峰）
            run_time=1.6,                                        #参数 “run_time”
        ))
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：与 `AnimationGroup` 的区别只在默认值——`LaggedStart` 把 `lag_ratio` 默认设成 0.05，这里放大到 0.3。5 个彩点像流水一样一个接一个淡入，`run_time=1.6` 控住整组总时长。

<video src="assets/RTM output/01-AnimationGroup与错峰-laggedstart.mp4" controls width="560"></video>

> 提醒：`LaggedStart` / `LaggedStartMap` 不在 RTM 自有 39 类的导出清单里。样例（见代码块）直接 `from real_time_manim import LaggedStart` 就行，拿到的是**内置 ManimCE 版**（顶层 = `from manim import *`，所以 `from manim import LaggedStart` 是同一个类）。时间轴照常驱动，效果与 CE 逐帧一致。

### LaggedStartMap

```python
LaggedStartMap(animation_class, mobject, arg_creator=None, run_time=2, lag_ratio=0.05, **kwargs)
```

继承 `LaggedStartMap(LaggedStart)`，来源 `animation/composition.py`。对 `mobject` 的**每个子对象**生成一个 `animation_class` 并错峰播放——"按类批量套动画"的最短写法。`arg_creator(submob)` 把子对象转成该动画的参数列表；不给时默认传子对象本身。

样例同样走 manim 本体类实测出片。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `animation_class` | `type[Animation]` | — | 要批量实例化的动画类。**能填** `FadeIn`、`ApplyMethod`… |
| `mobject` | `Mobject` | — | 被遍历的容器，逐个**子对象**处理 |
| `arg_creator` | `Callable \| None` | `None` | `submob -> (动画参数元组)`；`None` 时直接把 `submob` 作为唯一参数。**能填** 如 `lambda m: (m.set_color, YELLOW)` |
| `run_time` | `float` | `2` | 组总时长 |
| `lag_ratio` | `float` | `0.05` | 错峰比例（若在 `**kwargs` 里再传会被剔除，以本参数为准） |
| `**kwargs` | `Any` | — | 传给**每个** `animation_class` 实例的参数（如 `rate_func=there_and_back`） |

> **返回**：`Animation`（交给 `play` 播放）。

#### 样例：arg_creator 让每个字母逐个染黄再回色

`arg_creator` 把 "manim" 的每个字母转成 `ApplyMethod(set_color)`，逐字染黄、再由 `there_and_back` 各自回色。

```python
from real_time_manim import Scene, Text, GREY_B, YELLOW, UP, DOWN, FadeIn, LaggedStartMap, \
    ApplyMethod, Write, there_and_back
from real_time_manim.vulkan_bind import MLWindow, Wait

class LaggedStartMapDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-LaggedStartMap", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("LaggedStartMap(ApplyMethod, words,", font_size=30, color=GREY_B)
        l2 = Text("   lambda m: (m.set_color, YELLOW),", font_size=30, color=GREY_B)
        l3 = Text("   lag_ratio=0.15, run_time=2.0, rate_func=there_and_back)", font_size=28, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        words = Text("manim", font_size=64, color=GREY_B).shift(DOWN * 1.9)   #被逐字染色的词
        win.play(FadeIn(sig, shift=DOWN), FadeIn(words), run_time=0.4)   #标签与词淡入
        win.play(LaggedStartMap(                                 #参数 “animation_class / mobject / arg_creator”
            ApplyMethod, words,
            lambda m: (m.set_color, YELLOW),                     #参数 “arg_creator”（submob -> 参数元组）
            lag_ratio=0.15,                                      #参数 “lag_ratio”
            run_time=2.0,                                        #参数 “run_time”
            rate_func=there_and_back,                            #参数 “**kwargs”（透传给每个子动画）
        ))
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：不用手写 5 个 `ApplyMethod`——`LaggedStartMap` 遍历 "manim" 的每个字母，`arg_creator` 负责把子对象转成动画参数（这里就是染黄）。`there_and_back` 通过 `**kwargs` 传给每个子动画，字母染黄后又各自弹回原色。

<video src="assets/RTM output/01-AnimationGroup与错峰-laggedstartmap.mp4" controls width="560"></video>

> 提醒：`LaggedStartMap` 的 `**kwargs` 是传给**每个子动画**的（如这里的 `rate_func=there_and_back`），不是组级参数；`arg_creator` 不给时默认把子对象本身当唯一参数。

---

相关：[Succession 顺序播放](02-Succession顺序播放.md) · [特殊出场](../移动与旋转/03-特殊出场.md) · [play 与 wait 参数](../通用/02-play与wait参数.md)
