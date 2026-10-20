# MovingCamera（可移动相机）

跟随着取景框 `frame` 走的相机：`frame` 在哪、多大，画面就显示哪块空间。本页讲相机**自己**的构造参数、属性和 `auto_zoom`；对取景框做动画的推拉摇移玩法（`frame.animate`、`Restore`）在 [MovingCameraScene](../专用场景/01-MovingCameraScene.md) 那页。

## 参数

### class MovingCamera（构造参数）

```python
def __init__(self, frame: Mobject | None = None, fixed_dimension: int = 0, default_frame_stroke_color: ManimColor = WHITE, default_frame_stroke_width: int = 0, **kwargs: Any) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `frame` | `Mobject \| None` | `None` → `ScreenRectangle(height=config.frame_height)` | 取景框 mobject； **别填**：传进去也会被 `Camera.__init__` 改回默认——构造尾部会把 `frame_height`/`frame_width`/`frame_center` 依次写一遍，自定义取景框被拉回 8.0×14.222、挪回原点，实测传了等于没传（两个引擎逐字节相同的画面） |
| `fixed_dimension` | `int` | `0` | 调整画幅时固定哪一边（0=按宽算高）；**别填**：0.21 里只存不用（读它的代码被注释掉了），填什么都不改变画面 |
| `default_frame_stroke_color` | `ManimColor` | `WHITE` | 取景框描边色；影响取景框自身描边：默认 frame 不在场景里、都不画；显式 `self.add(self.camera.frame)` 且描边可见时 **RTM 现在也画** |
| `default_frame_stroke_width` | `int` | `0` | 取景框描边宽；同上（默认 `0` = 无像素输出，既有渲染零变化） |
| `**kwargs` | `Any` | — | 透传给 `Camera.__init__`（如 `background_color`，见 [Camera](01-Camera.md)） |

**返回**：无（构造实例）。常用属性（均读写，见下节）：`frame_height`、`frame_width`、`frame_center`；`frame` 本身是取景框 mobject（推拉摇移改它，详见 MovingCameraScene 页）。

为什么这节不出视频：`frame` 会被 `Camera.__init__` 拉回默认、`fixed_dimension` 存而不用（两个引擎都一样）；描边两个参数要显式把 `self.camera.frame` add 进场景才画得出取景框，而默认描边宽 `0`、填充 `0` 的 frame 在两个引擎里都没有像素输出，按默认值渲一段看不出差别。顺带一提 `Scene` 的 `camera_class` 只收**类**，渲染器建相机用的是 `camera_class()` 无参调用，真要塞构造参数得用 `functools.partial(MovingCamera, ...)` 或子类覆盖默认值——在上面这些参数身上不值得费这个劲。
### MovingCamera.frame_height / frame_width / frame_center（property）

```python
def frame_height(self) -> float:
def frame_height(self, frame_height: float) -> None:
def frame_width(self) -> float:
def frame_width(self, frame_width: float) -> None:
def frame_center(self) -> Point3D:
def frame_center(self, frame_center: Point3DLike | Mobject) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `frame_height` | `float` | `8.0` | 当前画面高（manim 单位）；**能填**任意正数；和 `frame_width` **成对**按 16:9 赋值才是等比缩放 |
| `frame_width` | `float` | `14.222` | 当前画面宽；**能填**任意正数；单独改它/`frame_height` 会变形（见提醒） |
| `frame_center` | `Point3DLike` 或 `Mobject` | `[0, 0, 0]`（画面正中） | 取景框中心；**能填**任意坐标，也可以直接塞一个 mobject（镜头摇移到它身上） |

**返回**：getter 返回 `float` / `Point3D`；setter 无返回（立即生效）。

#### 样例：frame_height / frame_width / frame_center

```python
from real_time_manim import (
    BLUE, RED, WHITE, YELLOW,
    DOWN, LEFT, RIGHT, UP,
    Circle, Dot, FadeIn, MovingCameraScene, Square, Text, VGroup,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class FrameScaleDemo(MovingCameraScene):
    HEIGHT = 4.0   #想看到的画面高度：改成 2.0 再跑一次，画面放大到 4 倍

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        cam = self.camera   #MovingCameraScene 自带的可移动相机
        a = Square(color=BLUE).set_stroke(width=4).shift(LEFT * 2.5)   #左边的目标
        b = Square(color=RED).set_stroke(width=4).shift(RIGHT * 2.5)   #右边的目标
        info = Text("frame: %.2f x %.2f" % (cam.frame_height, cam.frame_width),
                    font_size=28, color=WHITE).move_to(UP * 1.6)   #取景框的高和宽（放在画面里侧：推近后贴边会出画）
        self.add(a, b, info)   #把两个方块和读数放进场景
        win.play(FadeIn(a, b), run_time=0.5)   #两个方块淡入：此刻还是默认画幅
        win.play(Wait(0.4))   #停 0.4s
        cam.frame_height = self.HEIGHT   #改高度
        cam.frame_width = self.HEIGHT * 16 / 9   #宽度按 16:9 跟着改：成对赋值才是等比缩放
        info.become(Text("frame: %.2f x %.2f" % (cam.frame_height, cam.frame_width),
                    font_size=28, color=WHITE).move_to(UP * 1.6))   #读数刷新
        win.play(Wait(1.0))   #停 1.0s 看清放大后的画面
        win.close()   #关闭 RTM 窗口


class FrameCenterDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        cam = self.camera   #MovingCameraScene 自带的可移动相机
        a = Square(color=BLUE).set_stroke(width=4).shift(LEFT * 4)   #左边的目标
        b = Square(color=RED).set_stroke(width=4).shift(RIGHT * 4)   #右边的目标
        info = Text("frame_center = ORIGIN", font_size=28, color=WHITE).to_edge(UP)   #取景框中心
        self.add(a, b, info)   #把两个方块和读数放进场景
        win.play(FadeIn(a, b), run_time=0.5)   #两个方块淡入
        win.play(Wait(0.4))   #停 0.4s
        cam.frame_center = b   #把取景框中心挪到红方块上（也接受坐标数组）
        info.become(Text("frame_center = red square", font_size=28, color=WHITE).to_edge(UP))   #读数刷新
        win.play(Wait(1.0))   #停 1.0s：镜头摇到右边
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：第一段先按默认画幅（`8.00 × 14.22`）显示两个相距 5 单位的方块，然后把 `frame_height` 设成 4.0、`frame_width` 按 16:9 配成 7.11——两个都赋值才是一次干净的等比放大，画面瞬间变成 2 倍近景，读数同步刷新。第二段演示摇移：`cam.frame_center = b` 把取景框中心整个挪到红方块上（这一行也接受坐标数组，如 `cam.frame_center = [4, 0, 0]`），画面平移到右边，红方块居中、蓝方块退出视野。

<video src="assets/RTM output/02-MovingCamera-frame_props.mp4" controls width="560"></video>

> 提醒：`frame_height`/`frame_width` 是两个**独立**的 setter——**单独**改一个会把取景框拉成非 16:9：CE 按横竖两个方向各自缩放（画面变形），RTM 只按高度做等比缩放、根本不看宽度，两引擎画面不一致。想要安全的等比推拉：成对按 16:9 赋值（如样例），或用 `frame.animate.set(width=...)`（自动锁 16:9，见 MovingCameraScene 页）。读数文本放在画面里侧（`move_to(UP * 1.6)`）也是个小坑：推近后贴边的 `to_edge(UP)` 文本会直接出画。

### MovingCamera.auto_zoom(mobjects, margin, only_mobjects_in_frame, animate)

```python
def auto_zoom(self, mobjects: Iterable[Mobject], margin: float = 0, only_mobjects_in_frame: bool = False, animate: bool = True) -> _AnimationBuilder | Mobject:
```

自动把镜头对准一组对象并缩放到恰好框住它们。只对 XY 平面内的 2D 内容有效（相机被旋转过就不准）。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobjects` | `Iterable[Mobject]` | — | 要聚焦的对象；单个 mobject 或列表都行 |
| `margin` | `float` | `0` | 取景框额外留白（manim 单位）；任意非负数；**只加在「更挤」的那条边上**（按宽/高里比例更大的一侧定尺寸） |
| `only_mobjects_in_frame` | `bool` | `False` | `True`：只考虑**此刻已在画面内**的对象，画面外的直接忽略 |
| `animate` | `bool` | `True` | `True` 返回可播放的动画构造器（要交给 `win.play`）；`False` 立即生效、画面直接跳过去 |

**返回**：`animate=True` 时返回可播放的动画构造器，否则返回更新后的取景框。

#### 样例：auto_zoom

```python
from real_time_manim import (
    BLUE, RED, WHITE, YELLOW,
    DOWN, LEFT, RIGHT, UP,
    Circle, Dot, FadeIn, MovingCameraScene, Square, Text, VGroup,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class AutoZoomAnimDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        cam = self.camera   #MovingCameraScene 自带的可移动相机
        group = VGroup(
            Square(color=BLUE).set_stroke(width=4).shift(LEFT * 2.5),   #左边的方块
            Circle(color=RED).set_stroke(width=4).shift(RIGHT * 2.5),   #右边的圆
            Dot(color=YELLOW).shift(DOWN * 2),   #下方的小点
        )   #三个对象一组
        self.add(group)   #把三个对象放进场景
        win.play(cam.auto_zoom(group, margin=0.5), run_time=1.0)   #带动画地推近，恰好框住三个对象
        win.play(Wait(0.6))   #停 0.6s
        win.close()   #关闭 RTM 窗口


class AutoZoomNoAnimDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        cam = self.camera   #MovingCameraScene 自带的可移动相机
        group = VGroup(
            Square(color=BLUE).set_stroke(width=4).shift(LEFT * 2.5),   #左边的方块
            Circle(color=RED).set_stroke(width=4).shift(RIGHT * 2.5),   #右边的圆
            Dot(color=YELLOW).shift(DOWN * 2),   #下方的小点
        )   #三个对象一组
        self.add(group)   #把三个对象放进场景
        cam.auto_zoom(group, margin=0.5, animate=False)   #animate=False：立即生效，画面直接跳过去
        win.play(Wait(1.0))   #停 1.0s
        win.close()   #关闭 RTM 窗口


class AutoZoomOnlyDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        cam = self.camera   #MovingCameraScene 自带的可移动相机
        sq = Square(color=BLUE).set_stroke(width=4).shift(LEFT * 5)   #很靠左的方块
        circ = Circle(color=RED).set_stroke(width=4).shift(RIGHT * 2.5)   #右边的圆
        self.add(sq, circ)   #把方块和圆放进场景
        win.play(cam.auto_zoom(circ, margin=0.4), run_time=0.8)   #先推近圆圈：方块出画
        win.play(cam.auto_zoom([circ, sq], margin=0.4, only_mobjects_in_frame=True), run_time=0.8)   #方块在画面外，被忽略：镜头不动
        win.play(Wait(0.5))   #停 0.5s
        win.play(cam.auto_zoom([circ, sq], margin=0.4), run_time=0.8)   #不加限制：方块也算上，镜头拉远
        win.play(Wait(0.5))   #停 0.5s 收工
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：视频依次是三段。第一段把三个对象（方块、圆、小点）打包成一组，`cam.auto_zoom(group, margin=0.5)` 返回一个「把取景框套上去」的动画，`win.play` 播出来就是平滑推近、外加半单位留白。第二段同一组对象、同一 margin，但 `animate=False`——不返回动画，调用瞬间画面直接跳到目标取景。第三段讲 `only_mobjects_in_frame`：先推近右边的圆（左边的方块被挤出画面），再对 `[圆, 方块]` 调 `only_mobjects_in_frame=True`——方块在画面外被忽略，镜头纹丝不动；最后同样的调用去掉这个限制，方块也算上，镜头拉远到两者都装下。

<video src="assets/RTM output/02-MovingCamera-auto_zoom.mp4" controls width="560"></video>

> 提醒：`auto_zoom` 返回的是 `frame.animate` 动画构造器，**必须**交给 `win.play` 播放才会动（`animate=False` 时它直接改好取景框就返回，别再套 play）。`margin` 不是四边各加一半——它整体加在按比例更挤的那条边的尺寸上。`only_mobjects_in_frame=True` 的典型用法是「聚焦当前镜头里已有的东西，别为了够到画面外的对象乱拉镜头」。

---

相关：[Camera](01-Camera.md)、[MovingCameraScene](../专用场景/01-MovingCameraScene.md)、[ZoomedScene](../专用场景/03-ZoomedScene.md)、[Scene 基础](../场景/01-Scene基础.md)
