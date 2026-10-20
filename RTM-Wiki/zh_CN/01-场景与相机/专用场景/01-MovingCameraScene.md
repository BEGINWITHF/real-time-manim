# MovingCameraScene（推拉摇移场景）

相机可移动的场景：取景框 `self.camera.frame` 是一个 `ScreenRectangle`，对它做 `animate` 即可平移/缩放镜头；只要 `frame` 在动，全场景都会被当作"运动中"逐帧重绘。

## 参数

### class MovingCameraScene

```python
def __init__(self, camera_class: type[Camera] = MovingCamera, **kwargs: Any) -> None:
```

| 参数             | 类型             | 默认值            | 说明                                                                                                                        |
| -------------- | -------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `camera_class` | `type[Camera]` | `MovingCamera` | 相机类。**能填**：`MovingCamera`（默认）、`MultiCamera`（也有 `frame`，还多一个放大相机）、其它 `Camera` 子类；**不建议**填 `Camera` —— 它没有 `frame`，推拉摇移整段失效 |
| `**kwargs`     | `Any`          | —              | 透传给 `Scene.__init__`，**只能填**下面四个关键字（`camera_class` 已由上一行的同名参数接走），填别的会直接 `TypeError`                                       |

> **返回**：无（构造实例）。

`**kwargs` 能填的四个关键字：

| 关键字                      | 类型 / 默认值                                           | 能填什么           | 是否建议改                                                  |
| ------------------------ | -------------------------------------------------- | -------------- | ------------------------------------------------------ |
| `random_seed` | `int \| None` / `None`（取 `config.seed`） | 任意整数 | 可以改，写死一个数便于复现；画面差异见下面的样例 |
| `always_update_mobjects` | `bool` / `False` | `True`、`False` | **不建议改**：RTM 每帧都驱动更新器，实测两种取值画面完全相同 |
| `skip_animations` | `bool` / `False` | `True`、`False` | **不建议改**：RTM 不走 manim 的跳过路径，`animate` 照常执行，实测画面完全相同 |
| `renderer` | `CairoRenderer \| OpenGLRenderer \| None` / `None` | 一般留空 | **不建议改**：RTM 自己接管窗口与录制，没试过传自定义 renderer，别踩坑 |

#### 样例：`camera_class`改动

取景框 `self.camera.frame` 只在 `camera_class` 是 `MovingCamera`（默认）时存在；换成普通 `Camera`，`frame` 就没有了，推拉摇移整段失效。

```python
from real_time_manim import MovingCameraScene, MovingCamera, Camera, Square, Text, VGroup, \
    BLUE, RED, GREEN, YELLOW, DOWN, LEFT, RIGHT, ORIGIN, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class CameraClassDemo(MovingCameraScene):
    CAM = MovingCamera   #相机类：改成 “Camera” 再跑一次，取景框会消失

    def __init__(self, **kwargs):
        super().__init__(camera_class=self.CAM, **kwargs)   #把 “camera_class” 传给 Scene.__init__

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        left = Square(color=BLUE, side_length=2).shift(LEFT * 4)   #创建一个蓝色方块，放在画面左侧
        right = Square(color=RED, side_length=2).shift(RIGHT * 4)   #创建一个红色方块，放在画面右侧
        head = VGroup(
            Text(type(self.camera).__name__, font_size=28, color=YELLOW),   #第一行：当前相机类名
            Text("frame=%s" % hasattr(self.camera, "frame"), font_size=22, color=GREEN),   #第二行：有没有取景框
        ).arrange(DOWN, buff=0.1)   #两行文字上下排好
        head.move_to(left)   #把两行文字放进左边方块里，镜头推近时它们也跟着放大
        self.add(left, right, head)   #把三个对象放进场景
        win.play(FadeIn(left), run_time=0.4)   #淡入左边的方块
        if hasattr(self.camera, "frame"):   #只有 “MovingCamera” 才有 “frame”，普通 “Camera” 走不进这个分支
            win.play(self.camera.frame.animate.set(width=4.0).move_to(left), run_time=0.8)   #取景框缩到 4 并移到左边 = 推近
            win.play(self.camera.frame.animate.set(width=14.0).move_to(ORIGIN), run_time=0.8)   #取景框放大到 14 并回中 = 拉回全景
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：先开一个 RTM 窗口、把当前场景绑上去，然后在画面左右各放一个方块，并把「现在用的是哪个相机」和「这个相机有没有取景框」两行字放进左边的方块里。播放时先淡入左边的方块，接着判断 `self.camera` 有没有 `frame`：有就把取景框缩到 4 并移到左边方块（推近），再放大到 14 回到正中（拉回全景）；没有就什么都不做，直接等 0.5 秒收工。所以把 `CAM` 改成 `Camera` 再跑一次，推拉会整段不发生，两行字也从 `frame=True` 变成 `frame=False`。

<video src="assets/RTM output/01-MovingCameraScene-camera_class.mp4" controls width="560"></video>

> 提醒：`MLWindow(960, 540)` 会被强制纠正成 1920×1080 并打印一行提示，不是报错，不用改尺寸。两行标签放在方块**里面**（世界坐标），镜头推近时它们会跟着一起放大，这正是“镜头确实在动”的证据。另外换成 `Camera` 后 `self.camera.frame` 不存在，样例靠 `hasattr` 分支兜底——你自己的代码如果直接写 `self.camera.frame`，会直接 `AttributeError`。

#### 样例：`**kwargs`改动

`**kwargs` 原样交给 `Scene.__init__`。其中 `random_seed` 会改变随机序列，能直接看出来；`always_update_mobjects` / `skip_animations` 实测不改变 RTM 的画面（见本节开头的 `**kwargs` 表）。

```python
import random

from real_time_manim import MovingCameraScene, Square, Text, VGroup, \
    BLUE, RED, GREEN, YELLOW, WHITE, UP, DOWN, LEFT, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class RandomSeedDemo(MovingCameraScene):
    SEED = 1   #随机种子：改成 7 再跑一次，一排方块的颜色顺序会变

    def __init__(self, **kwargs):
        super().__init__(random_seed=self.SEED, **kwargs)   #把 “random_seed” 透传给 Scene.__init__

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        tag = Text("random_seed=%d" % self.SEED, font_size=40, color=YELLOW).to_edge(UP)   #在屏幕顶端显示当前种子
        order = [0, 1, 2, 3, 4]   #准备一个 0~4 的下标列表
        random.shuffle(order)   #洗牌；洗牌结果由构造参数 “random_seed” 决定
        colors = [BLUE, RED, GREEN, YELLOW, WHITE]   #五种颜色
        g = VGroup(*[Square(color=colors[i], side_length=0.9) for i in order])   #按洗牌后的下标创建方块
        g.arrange(RIGHT, buff=0.3).to_edge(DOWN)   #从左到右排成一行，颜色顺序 = 洗牌顺序
        self.add(tag, g)   #把标签和这一行方块放进场景
        print("random_seed=%d 洗牌顺序 =" % self.SEED, order)   #把顺序打到控制台，方便对照
        win.play(FadeIn(g), run_time=0.5)   #整行淡入
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：用 `random_seed` 决定的随机序列把 `[0, 1, 2, 3, 4]` 洗一次牌，再按洗好的顺序把五个颜色的方块从左到右排成一行淡入，屏幕顶端同时显示当前的种子值，控制台也打印洗牌结果。整个场景没有别的随机来源，所以这一排方块的颜色顺序完全由 `random_seed` 这一个数字决定。

<video src="assets/RTM output/01-MovingCameraScene-random_seed.mp4" controls width="560"></video>

> 提醒：`random_seed` 只影响随机数，不影响动画本身；想每次跑出来都一样就把 `SEED` 写死，换成别的整数会得到另一种排列。另外 `Square` 默认只有描边、没有填充，想要实心得自己加 `.set_fill(颜色, 0.6)`。

同一个场景只改这一个数字，两段视频的像素级内容不同——只改别的参数（如 `always_update_mobjects`、`skip_animations`）时，RTM 输出的两帧字节完全相同：

| `**kwargs` | RTM 实测 |
| --- | --- |
| `random_seed` | 画面随种子改变（上表） |
| `always_update_mobjects` | 无差异：RTM 每帧都驱动更新器，与 manim 的"静止 Wait 冻结"不同 |
| `skip_animations` | 无差异：RTM 不走 manim 的跳过路径，`animate` 照常执行 |

### self.camera.frame（取景框）

**作用**：相机的取景框 mobject（`ScreenRectangle`）。对它 `save_state()` / `animate.set(width=...)` / `Restore(...)` 即可实现镜头推拉；它由 `MovingCamera` 提供，没有独立构造参数。

可以直接读写的属性如下（用 `.animate` 改就会产生镜头运动）：

| 参数 | 类型 | 默认值 | 能填什么 | 是否建议改 |
| --- | --- | --- | --- | --- |
| `width` | `float` | `14.222` | 任意正数，常用 `2` ~ `14` | 可以改（推拉就是改它）；别小到画面里一个对象都装不下，否则整屏全黑 |
| `height` | `float` | `8.0` | 任意正数 | **不建议直接填**：`width` / `height` 锁死 16:9，改一个另一个自动跟着变（`width=4` → `height=2.25`） |
| 位置（`move_to()` / `shift()`） | `Point3DLike` | `[0, 0, 0]`（画面正中） | 任意坐标 | 可以改（摇移就是改它）；注意 `center()` 是个方法，不能拿来赋值 |

**返回**：属性本身是 `ScreenRectangle`，可读写其位置与尺寸（默认 `height=8.0`、`width=14.222`）。

#### 样例：`self.camera.frame`

`set(width=...)` 只改缩放、`move_to(...)` 只改中心，两者分工明确；`save_state()` + `Restore(...)` 把镜头拉回初始全景。

```python
from real_time_manim import MovingCameraScene, Square, Text, \
    BLUE, RED, WHITE, UP, DOWN, LEFT, RIGHT, Restore
from real_time_manim.vulkan_bind import MLWindow, Wait

class FrameDemo(MovingCameraScene):
    WIDTH = 4.0   #取景框宽度：改成 2.0 看更近的一档，改成 14.0 就是全景

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        a = Square(color=BLUE, side_length=1.5).shift(LEFT * 1.5)   #左边的目标
        b = Square(color=RED, side_length=1.5).shift(RIGHT * 1.5)   #右边的目标
        t = Text("width=%.1f" % self.WIDTH, font_size=32, color=WHITE)   #显示当前取景框宽度

        def pin(m):   #让标签跟着取景框底部走，并按取景框宽度缩放，屏幕上大小始终不变
            m.width = self.camera.frame.width * 0.28
            m.move_to(self.camera.frame.get_bottom() + UP * (
                m.height * 0.5 + self.camera.frame.height * 0.08))

        t.add_updater(pin)   #把宽度标签钉在取景框底部
        self.add(a, b, t)   #把三个对象放进场景
        print("初始 frame：height=%.3f width=%.3f" % (
            self.camera.frame.height, self.camera.frame.width))   #默认高度 8.0、宽度 14.222
        self.camera.frame.save_state()   #记住当前（全景）状态，供后面 Restore 复原
        win.play(self.camera.frame.animate.set(width=self.WIDTH), run_time=0.8)   #只改宽度 = 只推拉，画面中心不动
        win.play(self.camera.frame.animate.move_to(a), run_time=0.8)   #只改中心 = 只摇移，缩放比例不动
        print("之后 frame：height=%.3f width=%.3f" % (
            self.camera.frame.height, self.camera.frame.width))   #宽度仍是上面设的值，中心已移到 a
        win.play(Restore(self.camera.frame), run_time=0.8)   #回到 save_state 时的全景
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：先在左右各放一个方块、底部放一个跟着镜头走的宽度标签，打印取景框的初始尺寸（`height=8.0`、`width=14.222`），然后 `save_state()` 记住全景。之后依次走三步——只改 `width`（画面中心不动，只推拉）、只改 `move_to`（缩放比例不变，只摇移）、`Restore` 一次性回到最初的全景，最后等 0.5 秒收工。控制台会打印推拉前后的尺寸，能看到宽度变成了 `WIDTH`，高度按 16:9 自动跟着变。

<video src="assets/RTM output/01-MovingCameraScene-camera_frame.mp4" controls width="560"></video>

> 提醒：取景框是 16:9，`set(width=...)` 会自动算好 `height`（`width=4` → `height=2.25`），所以**不要**自己去改 `height`，否则画幅比例会乱。推近也别太狠——`width` 小到一个对象都装不下时，整屏就是黑的；样例把两个方块放在 `±1.5`，就是为了让 `width=2.0` 时画面里还有东西。宽度标签钉在取景框底部、并按取景框宽度缩放，所以无论怎么推拉，它在屏幕上看起来一样大。

三种取景框宽度渲染出的画面内容各不相同；每段里 `move_to(a)` 只移动中心，`Restore` 再把缩放和中心一起复位。

---

相关：[MovingCamera](../相机/02-MovingCamera.md)、[ZoomedScene](03-ZoomedScene.md)、[Scene 基础](../场景/01-Scene基础.md)
