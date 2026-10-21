# ThreeDCamera（三维相机）

三维相机：视角记在 5 个 `ValueTracker`（`phi` / `theta` / `focal_distance` / `gamma` / `zoom`）里，所以既能整体 `set`/`get`，也能对 tracker 直接做动画；光照、着色、投影方式也归它管。

视角通常经 `ThreeDScene` 的 `set_camera_orientation` / `move_camera` 设置（详见 [ThreeDScene](../专用场景/02-ThreeDScene.md)），本页讲相机**自己**的构造参数与方法。

## 参数

### class ThreeDCamera（构造参数）

```python
def __init__(self, focal_distance: float = 20.0, shading_factor: float = 0.2, default_distance: float = 5.0, light_source_start_point: Point3DLike = 9 * DOWN + 7 * LEFT + 10 * OUT, should_apply_shading: bool = True, exponential_projection: bool = False, phi: float = 0, theta: float = -90 * DEGREES, gamma: float = 0, zoom: float = 1, **kwargs: Any) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `focal_distance` | `float` | `20.0` | 焦距；**能填**任意正数，越大透视越平；运行期用 `set_focal_distance` |
| `shading_factor` | `float` | `0.2` | 明暗着色强度；**别填**：0.21 里只存不用（全库没有读它的代码），填多少画面都不变 |
| `default_distance` | `float` | `5.0` | 默认距离；**别填**：同上，只存不用 |
| `light_source_start_point` | `Point3DLike` | `9*DOWN + 7*LEFT + 10*OUT` | 光源位置；**能填**任意坐标——换到对面，立方体明暗就翻面（样例第 2 段） |
| `should_apply_shading` | `bool` | `True` | 是否对 3D 对象着色；**能填** `True`/`False`，运行期改属性同样生效（样例第 3 段） |
| `exponential_projection` | `bool` | `False` | 用指数投影减少远处畸变；**能填** `True`/`False`（样例见 project 小节） |
| `phi` | `float` | `0` | 初始极角（与 Z 轴夹角，弧度）；**能填**弧度（构造传入即生效，样例第 1 段） |
| `theta` | `float` | `-90 * DEGREES` | 初始方位角（绕 Z 轴，弧度）；同上 |
| `gamma` | `float` | `0` | 初始自转角（弧度）；同上 |
| `zoom` | `float` | `1` | 初始缩放倍数；同上 |
| `**kwargs` | `Any` | — | 透传给 `Camera.__init__`（见 [Camera](01-Camera.md)） |

**返回**：无（构造实例）。

怎么把构造参数送进去：`Scene` 的 `camera_class` 只收**类**，渲染器建相机用的是 `camera_class()` 无参调用——要塞构造参数得用 `functools.partial(ThreeDCamera, ...)` 或子类覆盖默认值（样例用的就是 `partial`）。

另外注意区分：`ThreeDScene` 构造里那个「默认斜视角」参数（`default_angled_camera_orientation_kwargs`）是**只存不用**的（两引擎渲染出来都是正面视角，见 [ThreeDScene](../专用场景/02-ThreeDScene.md) 页），别和 `ThreeDCamera` 自己的 `phi`/`theta` 混为一谈。

#### 样例：class ThreeDCamera（构造参数）

```python
from functools import partial

from real_time_manim import (
    BLUE, GREEN, WHITE, YELLOW,
    DEGREES, DOWN, LEFT, ORIGIN, OUT, RIGHT, UP,
    Cube, FadeIn, Text, ThreeDAxes, ThreeDCamera, ThreeDScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class CtorAngleDemo(ThreeDScene):
    def __init__(self, **kwargs):
        #“camera_class” 只收类（渲染器内部会无参调用它建相机），
        #构造参数要用 functools.partial 包一层才能送进去
        super().__init__(camera_class=partial(ThreeDCamera, phi=70 * DEGREES, theta=-60 * DEGREES), **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("ctor phi=70 theta=-60 (no set_camera_orientation)", font_size=26, color=YELLOW)   #顶部说明
        self.camera.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上，不随相机转动
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入：视角直接就是斜的
        win.play(Wait(1.2))   #停 1.2s：构造参数里的初始视角直接生效
        win.close()   #关闭 RTM 窗口


class CtorLightDemo(ThreeDScene):
    def __init__(self, **kwargs):
        #把 “light_source_start_point” 也用 partial 送进构造：光源翻到右上前方
        super().__init__(camera_class=partial(
            ThreeDCamera, light_source_start_point=9 * UP + 7 * RIGHT + 10 * OUT), **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("ctor light=9U+7R+10O", font_size=30, color=YELLOW)   #顶部说明
        self.camera.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #视角显式调回前一段的角度，只比光照
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入：明暗和前一段相反
        win.play(Wait(1.0))   #停 1.0s
        win.close()   #关闭 RTM 窗口


class CtorShadingDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("should_apply_shading=True", font_size=30, color=YELLOW)   #顶部说明
        self.camera.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #视角显式设好
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入：各个面深浅不同
        win.play(Wait(0.7))   #停 0.7s
        self.camera.should_apply_shading = False   #关掉着色：所有面变成同一个颜色
        cap.become(Text("should_apply_shading=False", font_size=30, color=YELLOW).to_edge(UP))   #说明文字跟着换
        win.play(Wait(1.0))   #停 1.0s 看清平色
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：三段对比。

- 第 1 段只靠构造参数 `partial(ThreeDCamera, phi=70°, theta=-60°)` 摆出斜视角——**没有任何** `set_camera_orientation` 调用，画面直接就是斜的，证明 `ThreeDCamera` 的视角构造参数真生效。
- 第 2 段把光源从默认的「左下后」翻到「右上前」（`9*UP + 7*RIGHT + 10*OUT`），视角用显式调用摆回同一角度，只比光照：立方体的明暗面整个翻转。
- 第 3 段演示 `should_apply_shading`：前半段各个面深浅不同（着色开），中途关掉后所有面变成同一个蓝色（平色）。

<video src="assets/RTM output/03-ThreeDCamera-ctor.mp4" controls width="560"></video>

> 提醒：
>
> - 抽帧验证过的结论：`ThreeDCamera` 自己的 `phi`/`theta`/`gamma`/`zoom` 构造参数在 RTM 与 ManimCE 两个引擎下**都生效**（第 1 段）；真正「只存不用」的是 `ThreeDScene` 那边的 `default_angled_camera_orientation_kwargs`/`ambient_camera_rotation`。
> - 即便如此，日常还是建议在 `construct` 里显式 `self.set_camera_orientation(...)`——不依赖构造链路，最直观也最好改。
> - `shading_factor`/`default_distance` 两个参数在 0.21 里是死参数，别费劲调。
> - `MLWindow(960, 540)` 被强制纠正成 1920×1080 属正常提示。

### ThreeDCamera 视角参数（get_* / set_* / get_value_trackers）

```python
def get_phi(self) -> float:
def get_theta(self) -> float:
def get_gamma(self) -> float:
def get_zoom(self) -> float:
def get_focal_distance(self) -> float:
def set_phi(self, value: float) -> None:
def set_theta(self, value: float) -> None:
def set_gamma(self, value: float) -> None:
def set_zoom(self, value: float) -> None:
def set_focal_distance(self, value: float) -> None:
def get_value_trackers(self) -> list[ValueTracker]:
```

| 参数 / 返回 | 类型 | 说明 |
| --- | --- | --- |
| `value`（五个 `set_*`） | `float` | **能填**任意数：`set_phi`/`set_theta`/`set_gamma` 弧度（配 `DEGREES` 常用），`set_zoom` 倍数，`set_focal_distance` 长度单位；都**立即生效**（无动画） |
| 五个 `get_*` | `float` | 读回当前视角，返回 `float` |
| `get_value_trackers()` | `list[ValueTracker]` | 返回 `[phi, theta, focal_distance, gamma, zoom]` 5 个 tracker；对 tracker 做 `animate` 就是带动画的视角变化 |

#### 样例：get_* / set_* / get_value_trackers

```python
from functools import partial

from real_time_manim import (
    BLUE, GREEN, WHITE, YELLOW,
    DEGREES, DOWN, LEFT, ORIGIN, OUT, RIGHT, UP,
    Cube, FadeIn, Text, ThreeDAxes, ThreeDCamera, ThreeDScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class ViewZoomDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        cam = self.camera   #ThreeDScene 自带的 ThreeDCamera
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("get_phi / get_theta / get_gamma / get_zoom / get_focal_distance", font_size=22, color=YELLOW)   #顶部说明
        cam.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        info = Text("phi=%.2f theta=%.2f gamma=%.2f zoom=%.2f focal=%.1f" % (
            cam.get_phi(), cam.get_theta(), cam.get_gamma(), cam.get_zoom(), cam.get_focal_distance()),
            font_size=24, color=WHITE).next_to(cap, DOWN)   #五个视角参数的读数
        cam.add_fixed_in_frame_mobjects(info)   #读数也钉在屏幕上
        self.add(axes, cube, cap, info)   #把坐标轴、立方体、标题、读数放进场景
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #视角显式设好
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入
        cam.set_focal_distance(18.0)   #改焦距：立即生效
        cam.set_zoom(1.15)   #改缩放：立即生效
        info.become(Text("phi=%.2f theta=%.2f gamma=%.2f zoom=%.2f focal=%.1f" % (
            cam.get_phi(), cam.get_theta(), cam.get_gamma(), cam.get_zoom(), cam.get_focal_distance()),
            font_size=24, color=WHITE).next_to(cap, DOWN))   #读数刷新
        win.play(Wait(1.2))   #停 1.2s 看清推近后的画面
        win.close()   #关闭 RTM 窗口


class ViewTrackerDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        cam = self.camera   #ThreeDScene 自带的 ThreeDCamera
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("get_value_trackers()[1].animate.set_value(-1.2)", font_size=26, color=YELLOW)   #顶部说明
        cam.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #视角显式设好
        trackers = cam.get_value_trackers()   #5 个 ValueTracker：phi、theta、focal_distance、gamma、zoom
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入
        win.play(trackers[1].animate.set_value(-1.2), run_time=1.0)   #对 theta 的 tracker 做动画：相机环绕
        win.play(Wait(0.6))   #停 0.6s 收工
        win.close()   #关闭 RTM 窗口


class ViewAngleDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        cam = self.camera   #ThreeDScene 自带的 ThreeDCamera
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("set_phi(0.6) / set_gamma(0.25)", font_size=28, color=YELLOW)   #顶部说明
        cam.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #视角显式设好
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入
        cam.set_phi(0.6)   #改极角：立即生效，俯视一些
        cam.set_gamma(0.25)   #改自转角：立即生效，画面绕视轴转动
        win.play(Wait(1.2))   #停 1.2s 看清跳变后的视角
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：三段各演示一类玩法。

- 第 1 段把五个视角参数读出来打在屏幕上，`set_focal_distance(18.0)` + `set_zoom(1.15)` 两行**立即**把画面推近——读数同步刷新成 `zoom=1.15 focal=18.0`。
- 第 2 段玩 tracker：`get_value_trackers()` 返回 `[phi, theta, focal_distance, gamma, zoom]` 顺序的 5 个 `ValueTracker`，对下标 1 的 theta tracker 做动画，相机就平滑地绕场景环绕。
- 第 3 段演示瞬时视角跳变：`set_phi(0.6)` 让镜头俯得浅一些、`set_gamma(0.25)` 让画面绕视轴滚转，两行都是一步到位、没有过渡动画。

<video src="assets/RTM output/03-ThreeDCamera-view.mp4" controls width="560"></video>

> 提醒：
>
> - `set_*` 全是瞬间跳变，想要平滑过渡要么对 tracker 做 `animate`（第 2 段），要么用 `ThreeDScene` 的 `move_camera`（见 [ThreeDScene](../专用场景/02-ThreeDScene.md) 页）。
> - tracker 就是普通 `ValueTracker`，也可以塞进 `AnimationGroup` 和别的动画并排播。
> - 角度一律是弧度——手写 `0.6` 也好，`70 * DEGREES` 也好，都是弧度值。

### ThreeDCamera.add_fixed_in_frame_mobjects / add_fixed_orientation_mobjects

```python
def add_fixed_in_frame_mobjects(self, *mobjects: Mobject) -> None:
def remove_fixed_in_frame_mobjects(self, *mobjects: Mobject) -> None:
def add_fixed_orientation_mobjects(self, *mobjects: Mobject, use_static_center_func: bool = False, center_func: Callable[[], Point3D] | None = None) -> None:
def remove_fixed_orientation_mobjects(self, *mobjects: Mobject) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | — | 要固定（或解除固定）的对象 |
| `use_static_center_func` | `bool` | `False` | 仅 `add_fixed_orientation_mobjects`：把旋转中心定死为调用时刻的中心（省每帧一次 `get_center` 计算） |
| `center_func` | `Callable[[], Point3D] \| None` | `None` | 仅 `add_fixed_orientation_mobjects`：自定义朝向锁定的旋转中心 |

**返回**：均无返回。`add_fixed_in_frame_mobjects` 把对象**钉在屏幕上**（位置和朝向都锁死，相机怎么转它都不动，适合 3D 场景里的标题、公式）；`add_fixed_orientation_mobjects` 只锁**朝向**（对象仍待在 3D 空间里跟着透视走，但不会像普通 3D 对象那样整个翻过去）；`remove_*` 解除。

#### 样例：add_fixed_in_frame_mobjects / add_fixed_orientation_mobjects

```python
from functools import partial

from real_time_manim import (
    BLUE, GREEN, WHITE, YELLOW,
    DEGREES, DOWN, LEFT, ORIGIN, OUT, RIGHT, UP,
    Cube, FadeIn, Text, ThreeDAxes, ThreeDCamera, ThreeDScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class FixedDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        cam = self.camera   #ThreeDScene 自带的 ThreeDCamera
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.2).set_color(BLUE)   #蓝色立方体当参照物
        title = Text("fixed_in_frame", font_size=34, color=YELLOW)   #演示屏幕钉扎的标题
        tag = Text("fixed_orientation", font_size=26, color=GREEN)   #演示朝向锁定的标签
        tag.next_to(cube, UP)   #标签摆在立方体上方的 3D 空间里
        cam.add_fixed_in_frame_mobjects(title)   #标题：位置和朝向都锁死在屏幕上
        title.to_edge(UP)   #标题挪到画面顶端
        cam.add_fixed_orientation_mobjects(tag)   #标签：只锁朝向，位置仍在 3D 空间
        self.add(axes, cube, tag, title)   #把四个对象放进场景：相机的 add_fixed_* 只登记绘制方式，不替你 add
        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)   #视角显式设好
        win.play(Wait(0.8))   #停 0.8s 看清两个对象的位置
        self.move_camera(theta=-140 * DEGREES, run_time=1.6)   #环绕 90°：标题纹丝不动，标签跟着立方体在画面里移动
        win.play(Wait(0.4))   #停 0.4s
        cam.remove_fixed_in_frame_mobjects(title)   #解除屏幕钉扎
        cam.remove_fixed_orientation_mobjects(tag)   #解除朝向锁定
        self.move_camera(theta=-190 * DEGREES, run_time=1.4)   #再环绕一次：两个对象都变成普通 3D 对象
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：立方体上方 3D 空间里放一个绿色标签、屏幕顶端钉一个黄色标题，然后 `move_camera` 环绕 90°：标题纹丝不动、标签跟着立方体在画面里移动但保持朝向不翻倒。

接着 `remove_fixed_*` 解除两者的锁定，再环绕一次——这回两个文字都变成普通 3D 对象，跟着视角一起歪过去。锁定与否的差别一目了然。

<video src="assets/RTM output/03-ThreeDCamera-fixed.mp4" controls width="560"></video>

> 提醒：
>
> - **相机的 `add_fixed_*` 只登记绘制方式，不会替你把对象加进场景**——忘了 `self.add` 它就整个不出现（样例特意把标题也放进 `self.add` 就是这个原因）；`ThreeDScene` 也有同名的场景方法，那版会顺手替你 `add`，两个入口二选一。
> - 朝向锁定的对象位置仍在 3D 空间，透视斜切会让它看着有点歪，这是正常现象。

### ThreeDCamera.project_point / project_points

```python
def project_point(self, point: Point3D) -> Point3D:
def project_points(self, points: Point3D_Array) -> Point3D_Array:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `point` / `points` | `Point3D` / `Point3D_Array` | — | 要投影的 3D 点（单个坐标或坐标数组） |

**返回**：按**当前视角**投影后的屏幕坐标（`[x, y, z]` 数组；`project_points` 返回逐行一组）。常用于把 3D 位置换算成屏幕坐标做标注。

#### 样例：project_point / project_points、exponential_projection

```python
from functools import partial

from real_time_manim import (
    BLUE, GREEN, WHITE, YELLOW,
    DEGREES, DOWN, LEFT, ORIGIN, OUT, RIGHT, UP,
    Cube, FadeIn, Text, ThreeDAxes, ThreeDCamera, ThreeDScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class ProjectDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        cam = self.camera   #ThreeDScene 自带的 ThreeDCamera
        axes = ThreeDAxes()   #默认的三维坐标轴
        cap = Text("project_point(ORIGIN) / project_points([ORIGIN, RIGHT, UP])", font_size=22, color=YELLOW)   #顶部说明
        cam.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cap)   #把坐标轴和标题放进场景
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #视角显式设好
        p1 = cam.project_point(ORIGIN)   #原点的投影坐标
        pts = cam.project_points([ORIGIN, RIGHT, UP])   #三个点的投影坐标
        info = Text("origin=(%.2f, %.2f)  right=(%.2f, %.2f)  up=(%.2f, %.2f)" % (
            p1[0], p1[1], pts[1][0], pts[1][1], pts[2][0], pts[2][1]),
            font_size=24, color=WHITE).next_to(cap, DOWN)   #投影结果上屏
        cam.add_fixed_in_frame_mobjects(info)   #读数钉在屏幕上
        self.add(info)   #把读数放进场景
        win.play(Wait(1.2))   #停 1.2s 看清投影数值
        win.close()   #关闭 RTM 窗口


class ExponentialDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        cam = self.camera   #ThreeDScene 自带的 ThreeDCamera
        axes = ThreeDAxes()   #默认的三维坐标轴
        near = Cube(side_length=1.2).set_color(BLUE)   #近处的立方体
        far = Cube(side_length=1.2).set_color(GREEN).shift(DOWN * 2.5 + RIGHT * 2.5)   #远处的立方体
        cap = Text("exponential_projection=False", font_size=28, color=YELLOW)   #顶部说明
        cam.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, near, far, cap)   #把坐标轴、两个立方体、标题放进场景
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #视角显式设好
        cam.set_focal_distance(6.0)   #焦距拉近：透视变强，才看得出两种投影的区别
        win.play(FadeIn(near, far), run_time=0.5)   #两个立方体淡入
        win.play(Wait(0.8))   #停 0.8s 看普通投影
        cam.exponential_projection = True   #切到指数投影：远处物体不再被过度放大
        cap.become(Text("exponential_projection=True", font_size=28, color=YELLOW).to_edge(UP))   #说明文字跟着换
        win.play(Wait(1.0))   #停 1.0s 对比
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：第 1 段把原点和 `RIGHT`、`UP` 两个单位向量投影成屏幕坐标打到屏幕上——注意投影是按**当前视角**算的，所以在摆好斜视角之后再问才有意义。

第 2 段把焦距拉到 6.0 强化透视，前半段是普通投影（线性透视，远处的绿方块被放大得很夸张），中途把 `exponential_projection` 切成 `True`，远处物体立刻缩回正常大小——这就是两种投影公式的差别。

<video src="assets/RTM output/03-ThreeDCamera-project.mp4" controls width="560"></video>

> 提醒：
>
> - `project_*` 返回的是当前投影矩阵下的坐标，视角一转数值就变——读数和画面永远对得上。
> - `exponential_projection` 运行期赋值即生效，焦距越小（透视越强）两种投影的差别越明显；默认线性投影就够用，超广角深景再考虑指数投影。

### ThreeDCamera.capture_mobjects

```python
def capture_mobjects(self, mobjects: Iterable[Mobject], **kwargs: Any) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobjects` | `Iterable[Mobject]` | — | 要捕获的对象 |
| `**kwargs` | `Any` | — | 透传给 `get_mobjects_to_display` |

**返回**：无。上游语义：先按当前视角刷新旋转矩阵，再把对象「拍」进相机的像素数组。

**无视频**：这是 Cairo 像素捕获管线的入口，RTM 走 Vulkan 向量渲染、没有可拍的像素数组，同 [Camera](01-Camera.md) 页的 `capture_*` 一族。

其余低频方法里，`get_rotation_matrix`（当前 3×3 旋转矩阵）和上面的 `project_*` 都是纯计算、随时可用；`add_fixed_*` 见对应小节。

---

相关：[ThreeDScene](../专用场景/02-ThreeDScene.md)、[Camera](01-Camera.md)、[MovingCamera](02-MovingCamera.md)、[Scene 基础](../场景/01-Scene基础.md)
