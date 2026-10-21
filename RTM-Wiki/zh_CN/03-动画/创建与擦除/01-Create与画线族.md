# Create 与画线族：Create / Write / DrawBorderThenFill / ShowPartial

这一节讲"一笔一笔画出来"收录的类：它们都沿矢量笔画，把对象从无到有画出来。

- `Create`：最标准的画图动画。
- `Write`：最常用的出场动画。
- `DrawBorderThenFill`：适合带填充的图形。
- `ShowPartial`：它们共同的抽象基类。

## 参数

### `Create` 

```python
Create(mobject, run_time=1.0, lag_ratio=1.0, **kwargs)
```

继承 `Create(Animation)`（RTM 自有实现，`real_time_manim/animations/create.py`；**不是** `ShowPartial` 子类）。它沿矢量笔画**从头到尾逐渐画出**，是最标准的"画图"动画。RTM 版**不做类型校验**；默认 `lag_ratio=1.0`，让多个子笔画**依次**画完。

> **2026-10-17 更新 · 导入**：本页签名描述的是 **RTM 自有** `Create`，须 `from real_time_manim.vulkan_bind import Create`（或 `real_time_manim.animations`）。
>
> 样例代码从 `real_time_manim` **顶层**导入，拿到的是**内置 ManimCE 0.21 版**：
>
> - `Create(ShowPartial)`
> - `introducer` 固定 `True`
> - 非矢量对象抛 `TypeError`
>
> 两版同名同参、用法一致，样例不依赖这处差别。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobject` | `VMobject` | —（必填） | 要画出来的对象。**能填** `Square`/`Circle`/`Text`/`MathTex`/`Arrow`…任意 `VMobject`；RTM 自有版不校验类型，传普通 `Mobject` 也能构造（但画面仍是按笔画推进） |
| `run_time` | `float` | `1.0` | 画完所需秒数；**能填**任意正数 |
| `lag_ratio` | `float` | `1.0` | 子笔画错峰比例；**能填** `0`~`1`，`1.0` = 一个接一个画，`0` = 所有笔画同时长 |
| `introducer` | `bool` | `False` | 播放前把对象加入场景。RTM 自有 `Create` **未固定**该形参（走 `Animation` 默认 `False`、显式传 `True` 生效）。样例显式传 `True` 两边等价 |
| 其余 | — | — | 继承 `Animation` 的 `rate_func`/`remover`/`name`/`suspend_mobject_updating`/`reverse_rate_function`/`use_override`（见[公共参数](../通用/01-生命周期与公共参数.md)） |

> **返回**：`Create` 实例。

#### 样例：公共参数传满，字母按 lag_ratio 依次画出

一个 Text 吃满 `Animation` 全套公共参数：`lag_ratio=0.3` 让字母错峰依次画出，其余逐个点名。

```python
from real_time_manim import Scene, Text, VGroup, BLUE, YELLOW, GREY_B, UP, DOWN, \
    smooth, Create, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class CreateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Create", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("Create(mobject, lag_ratio=0.3, introducer=True,",
                  font_size=30, color=GREY_B)
        l2 = Text("         run_time=1.3, rate_func=smooth, remover=False, ...)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #两行 “Create” 签名标签
        obj1 = Text("Create", font_size=52, color=BLUE).next_to(lab1, DOWN, buff=0.7)   #被逐笔画出的字
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(
            Create(obj1,                               #参数 “mobject”
                   lag_ratio=0.3,                      #参数 “lag_ratio”：字母依次画
                   introducer=True,                    #参数 “introducer”
                   run_time=1.3,                       #参数 “run_time”
                   rate_func=smooth,                   #参数 “rate_func”
                   remover=False,                      #参数 “remover”：画完保留
                   name="Create(Text)",                #参数 “name”
                   suspend_mobject_updating=True,      #参数 “suspend_mobject_updating”
                   reverse_rate_function=False,        #参数 “reverse_rate_function”
                   use_override=True),                 #参数 “use_override”
            run_time=1.3,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：把 `Animation` 公共参数整套传给 `Create` 走一遍，重点看 `lag_ratio=0.3`。

- `lag_ratio=0.3`：Text 的每个字母错峰 30% 依次画出（默认 `1.0` 是一个接一个，`0` 则所有笔画同时长）。
- `rate_func=smooth`：收尾带缓动。
- `remover=False`：画完字留在画面上。
- `introducer=True`：对象播放前不用手动进场景。

<video src="assets/RTM output/01-Create与画线族-create.mp4" controls width="560"></video>

### `Write` 

```python
Write(mobject, rate_func=linear, reverse=False, run_time=None, lag_ratio=None, **kwargs)
```

继承 `Write(DrawBorderThenFill) ← DrawBorderThenFill(Animation)`。它模拟"手写/手画"：先描边、再填充，逐笔出现，是最常用的出场动画，`Text`、`Tex`、`MathTex`、任意 `VMobject` 都能用。

默认速率是 `linear`。`run_time` 与 `lag_ratio` 默认都是 `None`，按对象复杂度自动取值（`length < 15` 时 `run_time=1`，否则 `2`；`lag_ratio = min(4/length, 0.2)`），显式传入则以你传的为准。`reverse=True` 则变成"倒着写"，并自动 `remover=True`、`introducer=False`。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `vmobject` | `VMobject` | —（必填） | 要写出来的对象 |
| `rate_func` | `Callable` | `linear` | **不建议改**：写字用匀速才符合手写直觉 |
| `reverse` | `bool` | `False` | `True` 倒序书写，且默认 `remover=True`（写完即移除） |
| `run_time` | `float \| None` | `None` | **能填**任意正数；不传则按长度自动取 `1` 或 `2` |
| `lag_ratio` | `float \| None` | `None` | **能填** `0`~`1`；不传则自动取 `min(4/max(1,length), 0.2)` |
| 其余 | — | — | `Animation` 通用参数 + `DrawBorderThenFill` 的 `stroke_width=2`/`stroke_color=None` |

> **返回**：`Write` 实例。

#### 样例：linear 匀速手写，显式覆盖自动 run_time / lag_ratio

"Hello Manim" 用 `Write` 写出，`run_time=1.5` / `lag_ratio=0.2` 压过按长度自动取的默认值。

```python
from real_time_manim import Scene, Text, VGroup, GREEN, YELLOW, GREY_B, UP, DOWN, \
    linear, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class WriteDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Write", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l3 = Text("Write(vmobject, rate_func=linear, reverse=False,",
                  font_size=30, color=GREY_B)
        l4 = Text("        run_time=1.5, lag_ratio=0.2, stroke_width=2, ...)",
                  font_size=30, color=GREY_B)
        lab2 = VGroup(l3, l4).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #两行 “Write” 签名标签
        obj2 = Text("Hello Manim", font_size=48, color=GREEN).next_to(lab2, DOWN, buff=0.7)   #被写出的字
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(
            Write(obj2,                                #参数 “vmobject”
                  rate_func=linear,                    #参数 “rate_func”：匀速手写
                  reverse=False,                       #参数 “reverse”：正序书写
                  run_time=1.5,                        #参数 “run_time”：覆盖自动值
                  lag_ratio=0.2,                       #参数 “lag_ratio”：覆盖自动值
                  stroke_width=2,                      #参数 “stroke_width”
                  stroke_color=None),                  #参数 “stroke_color”
            run_time=1.5,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：`Write(obj2, rate_func=linear, run_time=1.5, lag_ratio=0.2, ...)` 先描边再填充，逐笔写出 "Hello Manim"。`linear` 匀速才像手写；`run_time` / `lag_ratio` 显式传入，就压过了按长度自动取值的默认逻辑（见提醒）。

<video src="assets/RTM output/01-Create与画线族-write.mp4" controls width="560"></video>

> 提醒：`run_time` / `lag_ratio` 不传时 `Write` 会按字数自动取值（`length<15` → `run_time=1`，否则 `2`；`lag_ratio=min(4/max(1,length), 0.2)`）——想精确控制就显式传，样例里就是显式覆盖。

### `DrawBorderThenFill` 

```python
DrawBorderThenFill(mobject, run_time=2.0, stroke_width=2, stroke_color=None,
                   rate_func=double_smooth, introducer=True, **kwargs)
```

继承 `DrawBorderThenFill(Animation)`（RTM 自有实现）。它是**先画轮廓、再显示填充**的两段式动画，也是 `Write` 的直接父类，但自己没有 `lag_ratio` 自动逻辑，也不逐笔细分，适合让"带填充的图形"整体出现。RTM 自有版**不做类型校验**。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobject` | `VMobject` | —（必填） | 被动画的矢量对象；RTM 自有版不校验类型 |
| `run_time` | `float` | `2` | 总时长（两阶段共用）。**能填**任意正数 |
| `rate_func` | `Callable` | `double_smooth` | 两段各用一次平滑，形成"顿一下再填充"的手感；**不建议改** |
| `stroke_width` | `float` | `2` | 第一阶段轮廓线宽。**能填**任意正数 |
| `stroke_color` | `str \| None` | `None` | 轮廓颜色；`None` 时取对象自身描边色（无描边则取填充色） |
| `introducer` | `bool` | `True` | 播放前加入场景（RTM 自有版把它写成显式形参，默认 `True`，可传 `False`） |
| 其余 | — | — | `Animation` 通用参数 |

> **返回**：`DrawBorderThenFill` 实例。

#### 样例：stroke_width=6 蓝轮廓 + double_smooth 顿挫填充

橙色实心方块走一遍两段式：先用 `stroke_width=6` 的 `stroke_color=BLUE` 描出粗轮廓，顿一下再填橙色。

```python
from real_time_manim import Scene, Text, Square, VGroup, BLUE, ORANGE, YELLOW, GREY_B, \
    UP, DOWN, double_smooth, DrawBorderThenFill, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class BorderFillDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-DrawBorderThenFill", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l5 = Text("DrawBorderThenFill(vmobject, run_time=1.8,",
                  font_size=30, color=GREY_B)
        l6 = Text("    rate_func=double_smooth, stroke_width=6,",
                  font_size=30, color=GREY_B)
        l7 = Text("    stroke_color=BLUE, introducer=True)",
                  font_size=30, color=GREY_B)
        lab3 = VGroup(l5, l6, l7).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #三行签名标签
        obj3 = (Square(side_length=1.8, color=ORANGE)
                .set_fill(ORANGE, 1.0).next_to(lab3, DOWN, buff=0.6))   #带填充的橙色方块
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(
            DrawBorderThenFill(                        #参数 “vmobject”
                obj3,
                run_time=1.8,                          #参数 “run_time”
                rate_func=double_smooth,               #参数 “rate_func”：两段各一次平滑
                stroke_width=6,                        #参数 “stroke_width”：轮廓更粗
                stroke_color=BLUE,                     #参数 “stroke_color”：蓝色轮廓
                introducer=True),                      #参数 “introducer”
            run_time=1.8,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：两段式——`DrawBorderThenFill` 先用 `stroke_width=6` 的蓝线把方块轮廓描一圈（`stroke_color=BLUE`），`double_smooth` 在两段之间顿一下，再把橙色填满。和 `Write` 不同，它不逐笔细分，整块轮廓一次性出。

<video src="assets/RTM output/01-Create与画线族-border_fill.mp4" controls width="560"></video>

### `ShowPartial`（抽象基类，不建议直接使用）

```python
ShowPartial(mobject, **kwargs)
```

继承 `ShowPartial(Animation)`（**这是 ManimCE 的类**：`ShowPartial` 不在 RTM 自有 39 个动画的导出清单里，随内置 ManimCE 从 `real_time_manim` 顶层导入）。

它是**抽象基类**，在 CE 里是"每帧只显示一部分笔画"的动画（`Create`、`ShowPassingFlash`）的父类。构造时会检查对象有没有 `pointwise_become_partial` 方法，没有就抛 `TypeError`。

直接实例化会在播放时报 `NotImplementedError("Please use Create or ShowPassingFlash")`，所以**用户不应直接使用**；这里列出它，只是为了说明 CE 侧的继承链。

RTM **自有**的 `Create` / `ShowPassingFlash` 都**不是**它的子类（各自直接继承 `Animation`）。RTM 下直传实测可播：`real_time_manim/compat.py` 给 `_get_bounds` 打了补丁，按 Create 式 bounds 渲染。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobject` | `VMobject \| OpenGLVMobject \| OpenGLSurface` | —（必填） | 被动画的对象 |
| 其余 | — | — | `Animation` 通用参数（本类无额外形参） |

> **返回**：`ShowPartial` 实例（**别直接播**，用 `Create` / `ShowPassingFlash`）。

#### 样例：抽象基类直传一播，圆沿笔画画出

`ShowPartial(obj4, run_time=1.3, introducer=True)` 直接构造播一发，看它和 `Create` 同族的"画一部分"效果（RTM 下靠 compat 补丁可播）。

```python
from real_time_manim import Scene, Text, Circle, YELLOW, GREY_B, UP, DOWN, \
    FadeIn, ShowPartial, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class ShowPartialDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-ShowPartial", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l8 = Text("ShowPartial(mobject, run_time=1.3, introducer=True)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   #签名标签
        obj4 = Circle(radius=0.7, color=GREEN).next_to(l8, DOWN, buff=0.7)   #被逐帧画出的圆
        win.play(FadeIn(l8, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(
            ShowPartial(obj4,                          #参数 “mobject”
                        run_time=1.3,                  #参数 “run_time”
                        introducer=True),              #参数 “introducer”
            run_time=1.3,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：抽象基类 `ShowPartial(obj4, run_time=1.3)` 直接播——绿色圆沿笔画从起点画到终点，效果和 `Create` 同族；它的存在价值是当 `Create` / `ShowPassingFlash` 的父类，正常代码别直接用它。

<video src="assets/RTM output/01-Create与画线族-showpartial.mp4" controls width="560"></video>

---

相关：[生命周期与公共参数](../通用/01-生命周期与公共参数.md) · [反向擦除](02-反向擦除.md) · [逐个显示与集合](03-逐个显示与集合.md)
