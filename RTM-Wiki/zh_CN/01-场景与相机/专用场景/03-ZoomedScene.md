# ZoomedScene（局部放大场景）

画中画放大场景：`MovingCameraScene` 的子类，内置一台"放大相机"（`self.zoomed_camera`，本身是 `MovingCamera`）和一个显示放大结果的小窗（`self.zoomed_display`），`setup()` 阶段自动创建这两个对象。开启放大后，小窗里持续显示放大相机拍到的画面——把取景框套到哪个小目标上，哪个目标就在小窗里变大。RTM 实测整条画中画链路可用（含 `animate=True` 的入场动画与手动编排）。

## 参数

### class ZoomedScene

```python
def __init__(self, camera_class: type[Camera] = MultiCamera, zoomed_display_height: float = 3, zoomed_display_width: float = 3, zoomed_display_center: Point3DLike | None = None, zoomed_display_corner: Vector3D = UP + RIGHT, zoomed_display_corner_buff: float = DEFAULT_MOBJECT_TO_EDGE_BUFFER, zoomed_camera_config: dict[str, Any] = {"default_frame_stroke_width": 2, "background_opacity": 1}, zoomed_camera_image_mobject_config: dict[str, Any] = {}, zoomed_camera_frame_starting_position: Point3DLike = ORIGIN, zoom_factor: float = 0.15, image_frame_stroke_width: float = 3, zoom_activated: bool = False, **kwargs: Any) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `camera_class` | `type[Camera]` | `MultiCamera` | 主相机类。**不建议**改：把小窗注册进主相机靠的是 `MultiCamera` 的 `add_image_mobject_from_camera` |
| `zoomed_display_height` | `float` | `3` | 放大小窗高（屏幕空间，与主画幅无比例关系）；**能填**任意正数 |
| `zoomed_display_width` | `float` | `3` | 放大小窗宽；**能填**任意正数，样例 2 用了 `4` |
| `zoomed_display_center` | `Point3DLike \| None` | `None` | 小窗中心坐标；`None`（默认）时由 `corner` 定位，一般留空 |
| `zoomed_display_corner` | `Vector3D` | `UP + RIGHT` | 小窗贴在哪个角，**能填** `UP + RIGHT`（右上，默认）、`DOWN + LEFT`（左下）等方向组合 |
| `zoomed_display_corner_buff` | `float` | `DEFAULT_MOBJECT_TO_EDGE_BUFFER`（`0.4`） | 小窗与边角的间距；**能填**正数，样例 2 用了 `0.3` |
| `zoomed_camera_config` | `dict` | `{"default_frame_stroke_width": 2, "background_opacity": 1}` | 放大相机（取景框）配置，一般不改 |
| `zoomed_camera_image_mobject_config` | `dict` | `{}` | 小窗图像 `ImageMobject` 的配置，一般留空 |
| `zoomed_camera_frame_starting_position` | `Point3DLike` | `ORIGIN` | 放大取景框初始位置（决定刚开启时放大哪儿）；可以改，但样例里用 `frame.move_to()` 现场挪 |
| `zoom_factor` | `float` | `0.15` | 放大倍数的倒数：取景框尺寸 = 小窗 × `zoom_factor`，**越小放得越大**；**能填** `0.05` ~ `0.5`，样例对比 `0.15` 与 `0.08` |
| `image_frame_stroke_width` | `float` | `3` | 小窗白色边框线宽；**能填** `0`（无边框）~ `6` |
| `zoom_activated` | `bool` | `False` | **不建议手动填**：由 `activate_zooming()` 管理，手动置 `True` 只会跳过注册步骤直接出错 |
| `**kwargs` | `Any` | — | 透传给 `MovingCameraScene.__init__`（取景框等，见 [MovingCameraScene](01-MovingCameraScene.md)） |

> **返回**：无（构造实例）。

#### 样例：构造参数改动

同一个场景、同一套动画，只换四个构造参数：默认档（`0.15`、`3×3`、右上角）和狠档（`0.08`、`4×2.5`、左下角）。

```python
from real_time_manim import ZoomedScene, Text, VGroup, Dot, \
    UP, DOWN, LEFT, RIGHT, YELLOW, GREEN, RED
from real_time_manim.vulkan_bind import MLWindow, Wait

def make_target():   #一个“小而密”的目标：字小、点也小，不放大看不清
    return VGroup(
        Text("RTM", font_size=22, color=YELLOW),   #很小的标题字
        Dot(radius=0.04, color=GREEN),              #两个小圆点
        Dot(radius=0.04, color=RED).shift(RIGHT * 0.18),
    ).arrange(DOWN, buff=0.1).shift(LEFT * 2 + DOWN * 0.8)   #摆到画面左下偏中的位置

class ZoomBase(ZoomedScene):
    LABEL = ""   #子类填本段的标题文字
    KW = {}      #子类填要传给 ZoomedScene.__init__ 的构造参数

    def __init__(self, **kwargs):
        super().__init__(**self.KW, **kwargs)   #把 “KW” 里的键传给 ZoomedScene.__init__

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        target = make_target()   #要放大的小目标
        self.add(target)   #放进场景（这时小得看不清）
        cap = Text(self.LABEL, font_size=28, color=YELLOW).to_edge(UP)   #顶部标题显示当前构造参数
        self.add(cap)   #放进场景（2D 场景里文字默认就钉在屏幕上）
        self.activate_zooming(animate=False)   #开启放大：小窗瞬间出现，不播动画
        self.zoomed_camera.frame.move_to(target)   #把放大镜的取景框套到目标上
        win.play(Wait(0.8))   #停 0.8s 看放大结果
        win.play(target.animate.shift(RIGHT * 1.2), run_time=1.2)   #目标右移，滑出取景框
        win.play(self.zoomed_camera.frame.animate.move_to(target), run_time=0.8)   #取景框再追过去
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


class ZoomA(ZoomBase):
    LABEL = "zoom_factor=0.15 display 3x3 corner=UP+RIGHT"   #默认一档：框 15% 大小
    KW = {"zoom_factor": 0.15,
          "zoomed_display_height": 3, "zoomed_display_width": 3,
          "zoomed_display_corner": UP + RIGHT}


class ZoomB(ZoomBase):
    LABEL = "zoom_factor=0.08 display 4x2.5 corner=DOWN+LEFT"   #更狠的一档：框 8% = 放大约 12 倍
    KW = {"zoom_factor": 0.08,
          "zoomed_display_height": 2.5, "zoomed_display_width": 4,
          "zoomed_display_corner": DOWN + LEFT, "zoomed_display_corner_buff": 0.3}
```

这段代码在做什么：两段各放一个小到看不清的目标（小字 + 两个小圆点），`activate_zooming(animate=False)` 让小窗瞬间出现，再把放大取景框 `move_to` 套到目标上——小窗里立刻显示放大的画面。接着目标右移滑出取景框（小窗里变空白），取景框再 `animate.move_to` 追过去重新对准。两段唯一区别是构造参数：第一段默认档 `0.15` / `3×3` / 右上角，第二段 `0.08` / `4×2.5` / 左下角贴边 `0.3`，放大约 12 倍。

<video src="assets/RTM output/03-ZoomedScene-zoom.mp4" controls width="560"></video>

> 提醒：`zoom_factor` 是"取景框相对小窗"的比例，**越小放得越大**（`0.15` ≈ 6.7 倍、`0.08` ≈ 12.5 倍），不是"放大 0.15 倍"。取景框 `self.zoomed_camera.frame` 就是 `MovingCamera` 的取景框，对它 `.animate.move_to(...)` 就能让放大镜跟着目标走（先让目标滑出、再让框追上，就是取景框在动的证据）。小窗宽高跟主画幅没有任何比例关系，随便填；换角只改 `zoomed_display_corner`。

### ZoomedScene.activate_zooming

```python
def activate_zooming(self, animate: bool = False) -> None:
```

启用放大：把小窗注册进主相机、置为前景层、`zoom_activated` 置 `True`。之后 `self.zoomed_camera.frame` 才是"放大镜的取景框"，对它 `animate` 即可选择放大哪里。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `animate` | `bool` | `False` | `False`：小窗一帧出现；`True`：先播"镜头推进"再播"小窗弹出"两个入场动画（内部 `self.play`，RTM 里先 `self.play = win.play`） |

> **返回**：无。

#### 样例：`activate_zooming(animate)`改动

同一场景只换 `animate` 一个参数，各跑一段：瞬间出现 vs 带入场动画。

```python
from real_time_manim import ZoomedScene, Text, VGroup, Dot, \
    UP, DOWN, LEFT, RIGHT, YELLOW, GREEN, RED
from real_time_manim.vulkan_bind import MLWindow, Wait

def make_target():   #一个“小而密”的目标：字小、点也小，不放大看不清
    return VGroup(
        Text("RTM", font_size=22, color=YELLOW),   #很小的标题字
        Dot(radius=0.04, color=GREEN),              #两个小圆点
        Dot(radius=0.04, color=RED).shift(RIGHT * 0.18),
    ).arrange(DOWN, buff=0.1).shift(LEFT * 2 + DOWN * 0.8)   #摆到画面左下偏中的位置

class ZoomActivateBase(ZoomedScene):
    ANIMATE = False   #子类改 True，看小窗的入场动画
    LABEL = ""        #子类填本段的标题文字

    def __init__(self, **kwargs):
        super().__init__(zoom_factor=0.15, **kwargs)   #两个类共用同一 zoom_factor，只比 animate

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #animate=True 时 activate_zooming 内部会调 self.play，先接到窗口上
        target = make_target()   #要放大的小目标
        self.add(target)   #放进场景
        cap = Text(self.LABEL, font_size=28, color=YELLOW).to_edge(UP)   #顶部标题显示 animate 取值
        self.add(cap)   #放进场景
        self.activate_zooming(animate=self.ANIMATE)   #False=小窗瞬间出现；True=先“推进镜头”再让小窗弹出
        self.zoomed_camera.frame.move_to(target)   #把放大镜的取景框套到目标上
        win.play(Wait(0.8))   #停 0.8s 看放大结果
        win.close()   #关闭 RTM 窗口


class ZoomNoAnim(ZoomActivateBase):
    ANIMATE = False   #小窗直接出现
    LABEL = "activate_zooming(animate=False)"


class ZoomAnim(ZoomActivateBase):
    ANIMATE = True   #播放入场动画
    LABEL = "activate_zooming(animate=True)"
```

这段代码在做什么：基类把 `zoom_factor` 固定在 `0.15`，只让子类切换 `ANIMATE`。第一段 `animate=False`：小窗一帧出现，直接把取景框套到目标上就开始放大；第二段 `animate=True`：先播"镜头推进"（取景框从全屏缩回放大尺寸），再播"小窗弹出"（小窗从角上展开出来），动画放完才对准目标。两段最终画面一致，差别只在小窗怎么登场。

<video src="assets/RTM output/03-ZoomedScene-activate.mp4" controls width="560"></video>

> 提醒：`animate=True` 时 `activate_zooming` 内部会连播两个动画，RTM 里必须先写 `self.play = win.play`，否则动画不播。`activate_zooming` 之前小窗还没注册进主相机，画面里根本看不到它，所以 `frame.move_to(target)` 一定要放在它**之后**。两个子类只差一个布尔值，可以对照着改 `ANIMATE` 重跑。

### get_zoom_in_animation / get_zoomed_display_pop_out_animation / get_zoom_factor

分别返回"镜头推进"动画、"小窗弹出"动画，以及当前缩放比；想自行编排入场节奏时用这三件套替代 `activate_zooming(animate=True)`。

```python
def get_zoom_in_animation(self, run_time: float = 2, **kwargs: Any) -> ApplyMethod:
def get_zoomed_display_pop_out_animation(self, **kwargs: Any) -> ApplyMethod:
def get_zoom_factor(self) -> float:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `run_time` | `float` | `2` | 推进动画时长（仅 `get_zoom_in_animation`，样例用 `1.2`） |
| `**kwargs` | `Any` | — | 透传给 `ApplyMethod`（两个动画方法都可加，如 `run_time=0.8`） |

> **返回**：两个动画方法返回 `ApplyMethod`（交给 `win.play` 播）；`get_zoom_factor` 返回 `float` 缩放比（无参数），实测 `= 取景框高度 ÷ 小窗高度`，与构造参数 `zoom_factor` 一致。

#### 样例：`get_zoom_in_animation`手动编排

手动完成 `activate_zooming(animate=True)` 内部的三步，节奏完全自己控制，最后打印 `get_zoom_factor()`。

```python
from real_time_manim import ZoomedScene, Text, VGroup, Dot, \
    UP, DOWN, LEFT, RIGHT, YELLOW, GREEN, RED
from real_time_manim.vulkan_bind import MLWindow, Wait

def make_target():   #一个“小而密”的目标：字小、点也小，不放大看不清
    return VGroup(
        Text("RTM", font_size=22, color=YELLOW),   #很小的标题字
        Dot(radius=0.04, color=GREEN),              #两个小圆点
        Dot(radius=0.04, color=RED).shift(RIGHT * 0.18),
    ).arrange(DOWN, buff=0.1).shift(LEFT * 2 + DOWN * 0.8)   #摆到画面左下偏中的位置

class ManualZoomDemo(ZoomedScene):
    def __init__(self, **kwargs):
        super().__init__(zoom_factor=0.15, **kwargs)   #默认 0.15 一档

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #下面手动编排的动画全走 win.play
        target = make_target()   #要放大的小目标
        self.add(target)   #放进场景

        #手动完成 activate_zooming(animate=True) 的三步，节奏自己编排：
        self.renderer.camera.add_image_mobject_from_camera(self.zoomed_display)   #① 把小窗注册进主相机
        win.play(self.get_zoom_in_animation(run_time=1.2))   #② “镜头推进”：取景框从全屏缩回放大尺寸
        win.play(self.get_zoomed_display_pop_out_animation(run_time=0.8))   #③ “小窗弹出”：从小窗位置展开
        self.add_foreground_mobjects(self.zoomed_camera.frame, self.zoomed_display)   #把取景框和小窗盖到最上层

        ratio = self.get_zoom_factor()   #缩放比 = 放大取景框高度 / 小窗高度
        print("get_zoom_factor() =", ratio)   #把缩放比打到控制台
        cap = Text("get_zoom_factor() = %.2f" % ratio,   #顶部也显示一份
                   font_size=28, color=YELLOW).to_edge(UP)
        self.add(cap)   #放进场景
        self.zoomed_camera.frame.move_to(target)   #把放大镜的取景框套到目标上
        win.play(Wait(0.8))   #停 0.8s 看放大结果
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：把 `activate_zooming(animate=True)` 拆开自己搭 —— ① `self.renderer.camera.add_image_mobject_from_camera(self.zoomed_display)` 把小窗注册进主相机（这就是 `activate_zooming` 内部的第一件事），② 播 `get_zoom_in_animation(run_time=1.2)` 让取景框从全屏缩回放大尺寸，③ 播 `get_zoomed_display_pop_out_animation(run_time=0.8)` 让小窗从角上弹出，再把取景框和小窗 `add_foreground_mobjects` 盖到最上层。然后 `get_zoom_factor()` 把缩放比同时打到控制台和屏幕顶部，最后对准目标看放大结果。

<video src="assets/RTM output/03-ZoomedScene-manual.mp4" controls width="560"></video>

> 提醒：三步顺序不能乱 —— 必须先注册小窗再播两个动画，且最后 `add_foreground_mobjects(...)` 把取景框与小窗盖到最上层，否则场景内容会压在小窗上面。`get_zoom_in_animation` 默认 `run_time=2`，手动编排时按节奏传自己的值。`get_zoom_factor()` 实测返回 `0.15`，正是构造参数 `zoom_factor` 的值（取景框高度 ÷ 小窗高度）。

---

相关：[MovingCameraScene](01-MovingCameraScene.md)、[MovingCamera](../相机/02-MovingCamera.md)、[Scene 基础](../场景/01-Scene基础.md)
