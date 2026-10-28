# Scene 基础

一个 RTM 脚本 = 一个继承 `Scene` 的类 + 覆写 `construct()`。`setup()` 先跑，用来准备公共对象；`construct()` 再跑，你的动画全写在这里。

RTM 由 record 模块直接驱动这个过程，不走 `manim` 命令行，也不经过 `Scene.render`。

## 参数

### class Scene（`__init__`）

```python
def __init__(self, renderer: CairoRenderer | OpenGLRenderer | None = None, camera_class: type[Camera] = Camera, always_update_mobjects: bool = False, random_seed: int | None = None, skip_animations: bool = False) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `renderer` | `CairoRenderer \| OpenGLRenderer \| None` | `None` | **不要传**：RTM 自己接管窗口与录制，自定义渲染器没有意义 |
| `camera_class` | `type[Camera]` | `Camera` | 该场景用的相机类。**能填**任何 `Camera` 子类；专用场景会自动换好（如 [MovingCameraScene](../专用场景/01-MovingCameraScene.md) 用 `MovingCamera`），一般不用手传 |
| `always_update_mobjects` | `bool` | `False` | **不建议改**：只影响 RTM 对"静态 Wait"的判定（冻结还是步进计帧），实测画面无差异 |
| `random_seed` | `int \| None` | `None`（取 `config.seed`） | 随机种子，写死一个数便于复现。**能填**任意整数；画面会随种子改变（见样例） |
| `skip_animations` | `bool` | `False` | **不建议改**：RTM 不走 manim 的跳过路径，`animate` 照常执行，实测画面无差异 |

> **返回**：无（构造实例）。**不要**在自己的场景里乱覆写 `__init__`：只有要传构造参数（如 `random_seed`）时才覆写，并转发 `super().__init__(...)`；其它预处理写在 `setup()` 里。

#### 样例：`Scene.__init__` 构造参数

五个参数里只有 `random_seed` 能直接看出来：同一个场景只换这一个数字，五个方块的颜色排列就换一种。`camera_class` / `always_update_mobjects` / `skip_animations` 的当前取值一并打在屏幕上。

```python
import random

from real_time_manim import (
    Scene,
    Square, Text, VGroup,
    BLUE, RED, GREEN, YELLOW, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class CtorDemo(Scene):
    SEED = 1   #随机种子：改成 7 再跑一次，五个方块的颜色顺序会变

    def __init__(self, **kwargs):
        super().__init__(random_seed=self.SEED, **kwargs)   #把 “random_seed” 传给 Scene.__init__

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        info = VGroup(
            Text("random_seed=%d" % self.SEED, font_size=36, color=YELLOW),
            Text("camera_class=%s" % type(self.camera).__name__, font_size=28, color=WHITE),
            Text("always_update_mobjects=%s  skip_animations=%s" % (
                self.always_update_mobjects, self.skip_animations), font_size=22, color=GREEN),
        ).arrange(DOWN, buff=0.15).to_edge(UP)   #三行标签：把当前构造参数的取值打在屏幕上
        order = [0, 1, 2, 3, 4]   #准备一个 0~4 的下标列表
        random.shuffle(order)   #洗牌；洗牌结果只由 “random_seed” 决定
        colors = [BLUE, RED, GREEN, YELLOW, WHITE]   #五种颜色
        row = VGroup(*[Square(color=colors[i], side_length=0.9) for i in order])   #按洗牌后的下标创建方块
        row.arrange(RIGHT, buff=0.3).to_edge(DOWN)   #从左到右排成一行，颜色顺序 = 洗牌顺序
        self.add(info, row)   #把标签和这一行方块放进场景
        win.play(FadeIn(row), run_time=0.5)   #整行淡入
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：覆写 `__init__`，把 `SEED` 传给 `Scene.__init__` 的 `random_seed`；然后在 `construct` 里用这个种子决定的随机序列给 `[0, 1, 2, 3, 4]` 洗牌，按洗好的顺序把五种颜色的方块排成一行淡入。屏幕顶端同时显示当前的 `random_seed`、`camera_class` 和另外两个布尔参数的取值。

整个场景没有别的随机来源，所以这一行的颜色顺序完全由 `random_seed` 一个数字决定——视频前半段是 `SEED = 1`（绿黄白蓝红），后半段是 `SEED = 7`（白蓝黄红绿）。

<video src="assets/RTM output/01-Scene基础-ctor.mp4" controls width="560"></video>

> 提醒：`random.seed` / `np.random.seed` 在 `Scene.__init__` 里就播好了，之后你代码里的任何随机调用都吃这个种子；想每次跑出来一模一样，就把 `SEED` 写死。
>
> 默认 `camera_class=Camera`，就是屏幕上显示的 `Camera`；换成 `MovingCamera` 之类的专用相机见 [MovingCamera](../相机/02-MovingCamera.md)。

### 场景生命周期：`Scene.setup` / `Scene.construct` / `Scene.tear_down`

```python
def setup(self) -> None:
def construct(self) -> None:
def tear_down(self) -> None:
```

| 方法 | 何时跑 | RTM 是否调用 | 说明 |
| --- | --- | --- | --- |
| `setup()` | `construct()` 之前 | 调用 | 无参数无返回。准备公共对象（各方块、图表、相机设置）写在这里；`MovingCameraScene`、`ZoomedScene` 这些子类的初始化也靠它 |
| `construct()` | `setup()` 之后 | 调用 | 无参数无返回。你的动画代码全写在这里：上屏用 `add(...)`，播动画用 `win.play(...)`，下屏用 `remove(...)` |
| `tear_down()` | 场景收尾时 | 调用 | 无参数无返回。manim 在 `Scene.render()` 末尾调它；RTM 由 record 生命周期（`real_time_manim/record.py` 的 `scene_lifecycle`）在 try/finally 里调，正常与异常路径都保证跑**一次**，且只跑你的钩子、不触发文件写入器的二次清理（pytest `tests/test_gap_wait_timeline.py` 验证）。收尾清理也可以写在 `construct()` 末尾（`win.close()` 之后也行） |

#### 样例：脚本骨架（setup → construct）

`setup` 里准备的方块在 `construct` 里被画出来，就证明 `setup` 确实先跑；`tear_down` 里的打印会在场景收尾时出现。

```python
from real_time_manim import Scene, Square, Text, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class LifeDemo(Scene):
    def setup(self):
        self.square = Square(color=BLUE)   #setup 在 construct 之前跑，适合准备公共对象

    def tear_down(self):
        print("tear_down ran")   #（2026-10-16 起 RTM 也会调用：record 生命周期 try/finally 里保证跑一次）

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        title = Text("setup -> construct", font_size=40, color=YELLOW).to_edge(UP)   #屏幕标题
        self.add(title)   #把标题放进场景
        win.play(Create(self.square), run_time=0.8)   #画出 setup() 里准备好的方块
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：`setup()` 里创建一个蓝色方块，挂在 `self.square` 上；`construct()` 里开一个 RTM 窗口、放一行标题，然后用 `Create` 把那个方块画出来，最后等 0.5 秒收工。

方块能被画出来，就说明 `setup()` 先于 `construct()` 执行。`tear_down()` 在场景收尾时跑，控制台会打出 `tear_down ran`——想验证，跑一次看控制台。

<video src="assets/RTM output/01-Scene基础-life.mp4" controls width="560"></video>

> 提醒：`MLWindow(960, 540)` 会被强制纠正成 1920×1080 并打印一行提示，不是报错，不用改尺寸。
>
> 多个场景共用的准备工作一律放 `setup()`——RTM 专门为它补了生命周期调用，`MovingCameraScene` 的取景框 `self.camera.frame` 就是在 `setup()` 里创建的。

### `Scene.render`

```python
def render(self, preview: bool = False) -> bool:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `preview` | `bool` | `False` | 为 `True` 时渲染完打开文件查看器 |

返回 `bool`（`True` 表示场景需要重跑）。

**RTM 不走 `Scene.render`**：record 模块（`fast_record_scene` / `record_scene`）直接按 `setup` → `construct` 驱动场景并接管录制，`render` 里的收尾（文件写入器 `finish`、"打开文件查看器"）都不会发生——`tear_down` 现在改由 record 生命周期在收尾时调用（见上一节）。不出视频；要出片请用 [录制视频](../../00-快速开始/04-录制视频.md) 里的 `fast_record_scene(...)`。

### `Scene.camera` / `Scene.time`

```python
@property
def camera(self) -> Camera | OpenGLCamera: ...
@property
def time(self) -> float: ...
```

| 属性 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `self.camera` | `Camera \| OpenGLCamera` | `camera_class` 的实例 | 直接读的属性：当前场景的相机对象。推拉摇移就是改它的状态（如 `self.camera.frame`），见 [Camera](../相机/01-Camera.md) |
| `self.time` | `float` | 随出帧累加 | **可用**：每画出一帧就累加一帧的 `dt`（对齐 manim `add_frame` 的语义；帧没画出就不累加）。想记录"已经播了多少秒"直接读它，或自己累计 `run_time` |

#### 样例：`Scene.time` 逐帧读数

方块在动、时间在流逝，标签跟着每帧刷新——这就是 `self.time` 随出帧累加的直接证据。

```python
from real_time_manim import Scene, Square, Text, UP, DOWN, RIGHT, linear
from real_time_manim.vulkan_bind import MLWindow, Wait

class TimeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=GREEN).shift(DOWN)   #一个会动的方块，证明时间确实在流逝
        label = Text("scene.time = 0.00", font_size=40, color=YELLOW).to_edge(UP)   #显示 self.time 的标签

        def show_time(m):   #每帧把 “self.time” 刷进标签
            m.become(Text("scene.time = %.2f" % self.time, font_size=40, color=YELLOW).to_edge(UP))

        label.add_updater(show_time)   #mobject 级 updater：RTM 每帧都会驱动它
        self.add(sq, label)   #把方块和标签放进场景
        win.play(sq.animate.shift(RIGHT * 4), run_time=0.8, rate_func=linear)   #方块匀速右移
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：给标签挂一个 mobject 级 updater，每帧把 `self.time` 的值刷成文字；方块同时匀速右移 0.8 秒，画面里时间在走、标签也跟着往上跳。

`self.time` 读的是渲染器的累加时钟：Timeline 每画出一帧就把 `renderer.time` 加一帧的 `dt`（没画出的帧不计），与 manim 的 `add_frame` 同一套语义。

<video src="assets/RTM output/01-Scene基础-time.mp4" controls width="560"></video>

> 提醒：需要"当前播到第几秒"时直接读 `self.time`（每画出一帧累加一次，帧没画出就不走）；想把它显示在画面里，照样例用一个 updater 刷 `Text`，或用 `ValueTracker` 把时间也变成一个可见的值。
>
> `self.camera` 则完全可用：它就是普通的相机对象，改 `frame`、`set(width=...)` 这些操作 RTM 都认。
---

相关：[内容上屏](02-内容上屏.md) · [播放与等待](03-播放与等待.md) · [第一个场景](../../00-快速开始/02-第一个场景.md) · [录制视频](../../00-快速开始/04-录制视频.md)
