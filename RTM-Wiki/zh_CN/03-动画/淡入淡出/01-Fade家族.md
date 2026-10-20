# Fade 家族：FadeIn / FadeOut

最常用的进入与消失动画：`FadeIn` 从"完全透明 +（可选）偏移/缩放"淡入到正常状态，`FadeOut` 反向渐隐并自动移出场景；`shift` / `target_position` / `scale` 组合出位移、缩放与透明度的复合效果。

## 参数

### `FadeIn`

```python
FadeIn(*mobjects, shift=None, target_position=None, scale=1, **kwargs)
```

> 源码里 `FadeIn.__init__(self, *mobjects, shift=None, target_position=None, scale=1.0, run_time=1.0, **kwargs)`（RTM 自有实现，`real_time_manim/animations/fade_in.py`）。上一行是**实际可用的合并签名**，两版一致。

继承 `FadeIn(Animation)`。组合时：`shift` 决定方向、`target_position` 决定起点位置、`scale` 决定起始大小。`introducer` 在 RTM 侧**未固定**（默认 `False`、显式传 `True` 生效，无害）。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | —（必填） | 一个或多个（多于 1 个时包成 `Group`）。至少传一个：CE 版抛 `ValueError("At least one mobject must be passed.")`，RTM 自有版 `mobjects` 为空时不报错、也没有可动画对象 |
| `shift` | `np.ndarray \| None` | `None` | 淡入时的位移向量（从 `-shift` 处进入）。**能填** `UP`/`DOWN`/`LEFT`/`RIGHT`/任意向量；`None` 且未给 `target_position` 时为 `ORIGIN`（纯透明度变化） |
| `target_position` | `np.ndarray \| Mobject \| None` | `None` | 淡入的起点位置。**能填**坐标或 mobject（取其**中心**，并自动算出 `shift = target_position - mobject.get_center()`） |
| `scale` | `float` | `1` | 起始缩放倍数：从 `scale` 倍缩放回原大小的同时淡入。**能填**任意正数。2026-10-16 起对**叶子 VMobject**（`Circle`/`Square`/`Dot`）也生效（此前只对有子对象的容器生效、叶子被静默忽略） |
| `introducer` | `bool` | `False` | RTM 侧**未固定**、可传（默认 `False`）
| 其余 | — | — | `Animation` 通用参数（`run_time=1.0`、`rate_func=smooth`、`lag_ratio=0`、`name`、`suspend_mobject_updating`、`reverse_rate_function`、`use_override`）。RTM 自有 `FadeIn` **不是 `Transform` 子类**，没有 `path_arc` / `path_func` 这些形参（传了会被 `**kwargs` 吞掉、无效） |

> **返回**：`FadeIn` 实例。

#### 样例：shift / scale / target_position 三种进入方式

方块 `FadeIn(sq, shift=DOWN, scale=0.5, ...)` 从下方半大处长回原位，圆 `FadeIn(ci, target_position=ORIGIN, ...)` 从画面中心飘来淡入；同一行还把 `run_time` / `lag_ratio` / `name` 等 `Animation` 公共参数逐个点名，两条 `FadeIn` 放进一个 `win.play` 一起播完。

```python
from real_time_manim import Scene, Square, Circle, Text, VGroup, \
    BLUE, GREEN, YELLOW, GREY_B, UP, DOWN, LEFT, RIGHT, ORIGIN, \
    smooth, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class FadeInDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-FadeIn", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("FadeIn(mobject, shift=DOWN, scale=0.5, run_time=1.1,",
                  font_size=30, color=GREY_B)
        l2 = Text("        lag_ratio=0.0, name='FadeIn')   FadeIn(c, target_position=ORIGIN)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #两行 “FadeIn” 签名标签
        sq = Square(side_length=1.3, color=BLUE).next_to(lab1, DOWN, buff=0.6).shift(LEFT * 2.2)   #演示对象 “sq”
        ci = Circle(radius=0.6, color=GREEN).next_to(lab1, DOWN, buff=0.6).shift(RIGHT * 2.2)   #演示对象 “ci”
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(
            FadeIn(sq,                               #“*mobjects” 之一
                   shift=DOWN,                       #参数 “shift”：从下方进入
                   scale=0.5,                        #参数 “scale”：从半大长回原大
                   run_time=1.1,                     #参数 “run_time”
                   lag_ratio=0.0,                    #参数 “lag_ratio”
                   name="FadeIn(Square)",            #参数 “name”
                   suspend_mobject_updating=True,    #参数 “suspend_mobject_updating”
                   reverse_rate_function=False,      #参数 “reverse_rate_function”
                   use_override=True),               #参数 “use_override”
            FadeIn(ci,                               #“*mobjects” 之二（另一实例）
                   target_position=ORIGIN,           #参数 “target_position”：从中心飘来
                   run_time=1.1),                    #参数 “run_time”
            run_time=1.1, rate_func=smooth,          #play 级 “rate_func”
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：标签先把完整调用摆出来，然后方块从下方半大处"长"回原位——`shift` 给方向、`scale` 给起始大小；圆从画面中心 `ORIGIN` 飘过来淡入——`target_position` 给起点。括号里那些 `run_time` / `lag_ratio` / `name` / `suspend_mobject_updating` / `reverse_rate_function` / `use_override` 都是 `Animation` 公共参数，逐条解释见[生命周期与公共参数](../通用/01-生命周期与公共参数.md)；淡入完成后对象原样留在场景里。

<video src="assets/RTM output/01-Fade家族-fadein.mp4" controls width="560"></video>

### `FadeOut`

```python
FadeOut(*mobjects, shift=None, target_position=None, scale=1, **kwargs)
```

> 同 `FadeIn`：RTM 自有 `FadeOut.__init__(self, *mobjects, shift=None, target_position=None, scale=1.0, run_time=1.0, **kwargs)`，三个可选参数由父类 `_Fade` 收下。上一行是**实际可用的合并签名**，两版一致。

继承 `FadeOut(Animation)`。对象**淡出**直至消失，`remover=True`（**RTM 自有版固定**：先 `super.__init__` 再覆写 `self.remover = True`，传 `remover=False` 也会被盖掉）播完自动从场景移除。`shift=UP*2` 之类可以做"飘走"效果，`target_position=other` 可以让对象淡向另一个对象。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | —（必填） | 一个或多个（多于 1 个时包成 `Group`）。至少传一个：CE 版抛 `ValueError`，RTM 自有版不报错但也无对象可动画 |
| `shift` | `np.ndarray \| None` | `None` | 淡出时的位移向量（朝该方向飘出）。**能填**同 `FadeIn`；`None` 且未给 `target_position` 时为 `ORIGIN`（原地渐隐） |
| `target_position` | `np.ndarray \| Mobject \| None` | `None` | 淡出的终点位置。**能填**坐标或 mobject（取中心、自动算 `shift`） |
| `scale` | `float` | `1` | 结束缩放倍数：淡出过程中缩到 `scale` 倍。**能填**任意正数。2026-10-16 起对**叶子 VMobject** 也生效（同 `FadeIn`） |
| 其余 | — | — | 同 `FadeIn`：`Animation` 通用参数（`introducer` 默认 `False` 可传、`remover` **固定 `True`**）。RTM 自有版另有内部方法 `_park_opacity(mob, value)`（把动画透明度挂到 paint walk 会访问的节点上，脱挂包装的子类才要重写），非公开参数 |

> **返回**：`FadeOut` 实例。

#### 样例：shift 飘出 / scale 缩出 / target_position 淡走

上一段留下的方块、圆先静态摆进场景，再用两条 `FadeOut` 分别演示：`FadeOut(sq, shift=UP, ...)` 让方块朝上飘走，`FadeOut(ci, scale=0.3, target_position=ORIGIN, ...)` 让圆一边缩到三成大一边淡向中心；换行标签也顺手用一条 `FadeOut` 换成新标签。

```python
from real_time_manim import Scene, Square, Circle, Text, VGroup, \
    BLUE, GREEN, YELLOW, GREY_B, UP, DOWN, LEFT, RIGHT, ORIGIN, \
    linear, FadeIn, FadeOut, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class FadeOutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-FadeOut", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("FadeIn(mobject, shift=DOWN, scale=0.5, run_time=1.1,",
                  font_size=30, color=GREY_B)
        l2 = Text("        lag_ratio=0.0, name='FadeIn')   FadeIn(c, target_position=ORIGIN)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #上一段演示留下的签名标签
        sq = Square(side_length=1.3, color=BLUE).next_to(lab1, DOWN, buff=0.6).shift(LEFT * 2.2)   #待淡出的对象 “sq”
        ci = Circle(radius=0.6, color=GREEN).next_to(lab1, DOWN, buff=0.6).shift(RIGHT * 2.2)   #待淡出的对象 “ci”
        self.add(lab1, sq, ci)   #演示对象先静态进场景（本样例的主角是 “FadeOut”）
        l3 = Text("FadeOut(sq, shift=UP, run_time=1.0)   FadeOut(ci, scale=0.3, ...)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   #换行标签（与 lab1 同槽位）
        win.play(FadeOut(lab1), FadeIn(l3, shift=DOWN), run_time=0.4)   #旧标签淡出、新标签就地换上
        win.play(
            FadeOut(sq,                              #“*mobjects” 之一
                    shift=UP,                        #参数 “shift”：朝上飘出
                    run_time=1.0,                    #参数 “run_time”
                    lag_ratio=0.0),                  #参数 “lag_ratio”
            FadeOut(ci,                              #“*mobjects” 之二
                    scale=0.3,                       #参数 “scale”：淡出时缩到 0.3 倍
                    target_position=ORIGIN,          #参数 “target_position”：朝中心淡走
                    run_time=1.0,                    #参数 “run_time”
                    name="FadeOut(Circle)"),         #参数 “name”
            run_time=1.0, rate_func=linear,          #play 级 “rate_func”
        )
        win.play(FadeOut(l3), run_time=0.4)   #标签也淡出
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：上一段的"结果"用 `self.add` 直接摆进场景（这段的主角是淡出，不用再演一遍进入），开场一条 `FadeOut(lab1)` 把旧标签换成新标签；接着方块 `shift=UP` 朝上飘走，圆 `scale=0.3` 缩到三成大并 `target_position=ORIGIN` 淡向中心。`FadeOut` 播完会把对象从场景里自动移走（`remover=True`），所以最后连标签也淡出后，画面干干净净收尾。

<video src="assets/RTM output/01-Fade家族-fadeout.mp4" controls width="560"></video>

### 手册「换页组合」：`AnimationGroup` 一换一

手册里的经典换页写法：一条 `AnimationGroup(FadeOut(旧, shift=UP), FadeIn(新1, 新2, shift=UP), lag_ratio=0.0)` 让旧对象朝上换下、新对象同时从下方换上（`AnimationGroup` 自身的参数与更多用法见[AnimationGroup 与错峰](../组合编排/01-AnimationGroup与错峰.md)）。从 `real_time_manim` 顶层导入的 `AnimationGroup`在 RTM 下正常工作，样例用的就是它；RTM **自带版**此前这条组合会"换下照常、换上缺席"，2026-10-16 已修复、两版均可（见下面提醒）。

#### 样例：一个换下、一个换上

红方块先 `Create` 画出来，然后 `AnimationGroup(FadeOut(x, shift=UP), FadeIn(ya, yb, shift=UP), lag_ratio=0.0)` 一条把它换成"黄圆 + 绿三角"。

```python
from real_time_manim import Scene, Square, Circle, Triangle, Text, \
    RED, GREEN, YELLOW, GREY_B, UP, DOWN, LEFT, RIGHT, \
    AnimationGroup, Create, FadeIn, FadeOut, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class SwapGroupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-AnimationGroup swap", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l4 = Text("AnimationGroup(FadeOut(x, shift=UP), FadeIn(y1, y2, shift=UP))",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   #组合签名标签
        x = (Square(side_length=1.2, color=RED).set_fill(RED, 0.6)
             .next_to(l4, DOWN, buff=0.7).shift(LEFT * 2.0))   #要被换下的红方块 “x”
        ya = Circle(radius=0.5, color=YELLOW).move_to(x)   #换上对象一：叠在 “x” 原位
        yb = (Triangle(color=GREEN).scale(0.9)
              .next_to(l4, DOWN, buff=0.7).shift(RIGHT * 2.0))   #换上对象二
        win.play(FadeIn(l4, shift=DOWN), run_time=0.4)   #标签从下方淡入
        win.play(Create(x), run_time=0.7)   #先画出要被换下的方块
        win.play(
            AnimationGroup(
                FadeOut(x, shift=UP),                #换下：朝上飘出
                FadeIn(ya, yb, shift=UP),            #换上：新对象从下方淡入
                lag_ratio=0.0,                       #参数 “lag_ratio”：同起同落
            ),
            run_time=1.2,
        )
        win.play(Wait(0.8))   #进行 0.8s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：`AnimationGroup` 把"换下"和"换上"塞进同一条 `win.play`，`lag_ratio=0.0` 让两半同起同落——视频里红方块朝上飘走的同时，黄圆绿三角从下方淡入 "x" 的原位，视觉上像旧卡片被新卡片顶替。

<video src="assets/RTM output/01-Fade家族-swap.mp4" controls width="560"></video>

> 提醒：`FadeIn`/`FadeOut` 的 `introducer`/`remover` **在 CE 版里**是构造器固定值、别显式再传（直接 `TypeError`）；RTM 自有版 `FadeIn(introducer=...)` 可传。`FadeTransform` / `FadeTransformPieces` 属于「变换」章节，不在本页。

无法演示：`introducer` —— RTM 自有 `FadeIn` **未固定**、可传（默认 `False`），CE 版才固定 `True` 传了就 `TypeError`，两版画面无差异；`FadeOut` 的 `remover` 两边都固定 `True`，无差异。RTM 自有 `FadeIn`/`FadeOut` 不是 `Transform` 子类，没有 `path_arc` / `path_arc_axis` / `path_arc_centers` / `path_func` / `replace_mobject_with_target_in_scene` 这些形参（传了被吞、纯淡入淡出中也不可视）；`*mobjects` 为空 —— CE 版抛 `ValueError`，RTM 自有版不报错，均无可视画面。

---

相关：[生命周期与公共参数](../通用/01-生命周期与公共参数.md) · [Create 与画线族](../创建与擦除/01-Create与画线族.md) · [反向擦除](../创建与擦除/02-反向擦除.md)
