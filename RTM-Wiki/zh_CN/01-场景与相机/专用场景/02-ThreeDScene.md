# ThreeDScene（三维场景）

三维视角控制场景：给 `Scene` 换上 `ThreeDCamera`，可以随时改视角（`phi` / `theta` / `gamma`）、缩放（`zoom`）、换画面中心，还有环境旋转、3D 错觉晃动、把对象钉在屏幕上的 fixed 系列，以及加强版子场景 `SpecialThreeDScene`。角度一律是**弧度**（`70 * DEGREES` 才是 70°）。

RTM 下这些能力全部渲染实测可用；注意两个"视角类"构造参数都只是存起来、不会自己生效（详见样例 1）。

## 参数

### class ThreeDScene

```python
def __init__(self, camera_class: type[ThreeDCamera] = ThreeDCamera, ambient_camera_rotation: dict | None = None, default_angled_camera_orientation_kwargs: dict | None = None, **kwargs: Any) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `camera_class` | `type[ThreeDCamera]` | `ThreeDCamera` | 相机类。**能填**：`ThreeDCamera`（默认）；**不建议**换成别的 —— 下面所有 `phi`/`theta`/`gamma`/`zoom` 都靠 `ThreeDCamera` 的属性工作 |
| `ambient_camera_rotation` | `dict \| None` | `None` | **存而不用**：形如 `{"theta": 0.15}`，上游只把它挂到 `self.ambient_camera_rotation`，全库没有任何地方读它，实测画面纹丝不动；要转请在 `construct` 里调 `begin_ambient_camera_rotation()`（样例 3） |
| `default_angled_camera_orientation_kwargs` | `dict \| None` | `{"phi": 70*DEGREES, "theta": -135*DEGREES}` | **只存不用**：同样先存起来，只有调 `set_to_default_angled_camera_orientation()` 才会被读取并应用（样例 1）；想直接摆角度用 `set_camera_orientation` |
| `**kwargs` | `Any` | — | 透传给 `Scene.__init__`（`random_seed` 等，含义见 [Scene 基础](../场景/01-Scene基础.md)） |

> **返回**：无（构造实例）。

配套方法（唯一会读 `default_angled_camera_orientation_kwargs` 的地方）：

```python
def set_to_default_angled_camera_orientation(self, **kwargs: Any) -> None:
```

把存着的斜视角字典（`kwargs` 可现场覆盖，如 `set_to_default_angled_camera_orientation(phi=60 * DEGREES)`）交给 `set_camera_orientation` 应用；**返回**：无。

#### 样例：构造参数改动

什么都不传时的起始视角其实是**正面**（`phi=0°`、`theta=0°`，经典斜角并不会自动出现）。两个视角类构造参数都只存不用 —— `default_angled_camera_orientation_kwargs` 要等 `set_to_default_angled_camera_orientation()` 才应用，`ambient_camera_rotation` 上游根本没人读。

```python
from real_time_manim import ThreeDScene, ThreeDAxes, Cube, Text, FadeIn, \
    BLUE, YELLOW, UP, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   #瞬间换掉顶部说明文字，不占动画时间
    cap.become(Text(text, font_size=30, color=YELLOW).to_edge(UP))

class CtorDefault(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #一个蓝色立方体当参照物
        cap = Text("", font_size=30, color=YELLOW)   #顶部说明文字（内容后面换）
        self.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上，视角怎么转都正对观众
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        say(cap, "default phi=0° theta=0°")   #什么都不传：起始就是正面视角
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入
        win.play(Wait(1.4))   #停 1.4s 看清默认视角
        self.set_to_default_angled_camera_orientation()   #应用存着的默认斜视角 {phi:70°, theta:-135°}
        say(cap, "set_to_default_angled_camera_orientation()")
        win.play(Wait(1.6))   #跳到 manim 经典斜视角
        win.close()   #关闭 RTM 窗口


class CtorAngled(ThreeDScene):
    def __init__(self, **kwargs):
        #构造参数只被存进 self.default_angled_camera_orientation_kwargs，没人主动用它
        super().__init__(
            default_angled_camera_orientation_kwargs=
            {"phi": 60 * DEGREES, "theta": -45 * DEGREES}, **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #一个蓝色立方体当参照物
        cap = Text("", font_size=30, color=YELLOW)   #顶部说明文字（内容后面换）
        self.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        say(cap, "ctor kwarg stored ... view unchanged")   #传了构造参数，但没人读它
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入
        win.play(Wait(1.4))   #仍是正面视角：光传参不生效
        self.set_to_default_angled_camera_orientation()   #调这个方法才读取并应用
        say(cap, "set_to_default_angled_camera_orientation()")
        win.play(Wait(1.6))   #这次跳到自定义的 phi=60° theta=-45°
        win.close()   #关闭 RTM 窗口


class CtorAmbient(ThreeDScene):
    def __init__(self, **kwargs):
        #构造参数同样只被存进 self.ambient_camera_rotation，全库没人读它（上游如此）
        super().__init__(ambient_camera_rotation={"theta": 0.15}, **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #一个蓝色立方体当参照物
        cap = Text("", font_size=30, color=YELLOW)   #顶部说明文字（内容后面换）
        self.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        self.set_camera_orientation(phi=65 * DEGREES, theta=-90 * DEGREES)   #先摆个斜视角，才看得出转不转
        say(cap, "ambient_camera_rotation ... no effect")
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入
        win.play(Wait(1.5))   #画面纹丝不动：这个参数没人读
        self.begin_ambient_camera_rotation(rate=0.15)   #要用环境旋转只能调方法
        say(cap, "begin_ambient_camera_rotation(rate=0.15)")
        win.play(Wait(1.5))   #现在开始转
        self.stop_ambient_camera_rotation()   #停住
        win.play(Wait(0.3))   #停 0.3s 收工
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：三段连着讲构造参数。

- 第一段什么都不传，起始就是正面视角，再调 `set_to_default_angled_camera_orientation()` 跳到存着的经典斜视角（70° / -135°）。
- 第二段构造时传自定义的 `{phi: 60°, theta: -45°}`，画面**依旧不动**（光传参没人用），直到同一个方法被调用才跳到自定义角度。
- 第三段传 `ambient_camera_rotation={"theta": 0.15}` 后画面纹丝不动，改调 `begin_ambient_camera_rotation()` 才开始转 —— 用对照证明两个参数都是"存而不用"。

<video src="assets/RTM output/02-ThreeDScene-ctor.mp4" controls width="560"></video>

> 提醒：构造参数传了不生效是上游 `manim` 0.21 的既有行为，命令行渲染和 RTM 完全一致，不是 RTM 的问题。
>
> 日常想摆斜视角，最直接是在 `construct` 里 `set_camera_orientation(phi=70 * DEGREES, theta=-135 * DEGREES)`；`default_angled_camera_orientation_kwargs` 的用途是"预设一档，后面随时一键调回"。
>
> `ambient_camera_rotation` 这个参数可以直接忽略，环境旋转的正路是样例 3 的 `begin_ambient_camera_rotation()`。

### set_camera_orientation / move_camera

`set_camera_orientation` **瞬间**设定视角（不带动画、一帧跳变）；`move_camera` **带动画地**移动（内部会 `self.play(...)`，RTM 里必须先 `self.play = win.play`）。两者参数含义相同，都传 `None` 的参数保持不变。

```python
def set_camera_orientation(self, phi: float | None = None, theta: float | None = None, gamma: float | None = None, zoom: float | None = None, focal_distance: float | None = None, frame_center: Mobject | Sequence[float] | None = None, **kwargs: Any) -> None:
def move_camera(self, phi: float | None = None, theta: float | None = None, gamma: float | None = None, zoom: float | None = None, focal_distance: float | None = None, frame_center: Mobject | Sequence[float] | None = None, added_anims: Iterable[Animation] = [], **kwargs: Any) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `phi` | `float \| None` | `None`（不改） | 极角（弧度）：`0` = 正面俯视，`70 * DEGREES` ≈ 经典斜视角；**能填**任意弧度 |
| `theta` | `float \| None` | `None`（不改） | 方位角（弧度）：绕竖直轴转多少，经典值 `-135 * DEGREES` |
| `gamma` | `float \| None` | `None`（不改） | 自转角（弧度）：画面绕视轴"歪头"；**不建议**给太大，文字会倒过来 |
| `zoom` | `float \| None` | `None`（不改，即 `1.0`） | 缩放倍数：`>1` 推近、`<1` 拉远；**能填**常用 `0.5` ~ `3`，太大会只剩黑屏 |
| `focal_distance` | `float \| None` | `None`（不改） | 焦距（透视强度），一般留空，和 `zoom` 配合时才调 |
| `frame_center` | `Mobject \| Sequence[float] \| None` | `None`（画面正中） | 画面中心挪到某个对象或坐标，**能填** mobject 或 `[x, y, z]` |
| `added_anims` | `Iterable[Animation]` | `[]` | 仅 `move_camera`：与镜头运动**同时**播放的其它动画 |
| `**kwargs` | `Any` | — | 仅 `move_camera`：透传给 `self.play`（如 `run_time=1.2`）；`set_camera_orientation` 没有动画，传了也没用 |

> **返回**：无。

#### 样例：`set_camera_orientation` / `move_camera`改动

`set_camera_orientation` 一步到位、`move_camera` 平滑绕过去；一个样例连着演示 `phi`/`theta` → `gamma` → `zoom` → `frame_center` 五个入口，最后一步全部复位。

```python
from real_time_manim import ThreeDScene, ThreeDAxes, Cube, Text, \
    BLUE, YELLOW, UP, ORIGIN, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   #瞬间换掉顶部说明文字，不占动画时间
    cap.become(Text(text, font_size=30, color=YELLOW).to_edge(UP))

class OrientationDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("", font_size=30, color=YELLOW)   #顶部说明文字（内容后面换）
        self.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把三个对象放进场景

        say(cap, "set_camera_orientation phi=30° theta=-60°")
        self.set_camera_orientation(phi=30 * DEGREES, theta=-60 * DEGREES)   #瞬间跳到新视角，没有动画
        win.play(Wait(0.8))   #停 0.8s 看清结果

        say(cap, "move_camera phi=70° theta=-45°")
        self.move_camera(phi=70 * DEGREES, theta=-45 * DEGREES, run_time=1.2)   #带动画地绕到新 phi/theta
        win.play(Wait(0.3))   #停 0.3s

        say(cap, "move_camera gamma=25°")
        self.move_camera(gamma=25 * DEGREES, run_time=0.8)   #画面绕视轴自转 25°
        win.play(Wait(0.3))   #停 0.3s

        say(cap, "move_camera zoom=1.8")
        self.move_camera(zoom=1.8, run_time=0.8)   #推近到 1.8 倍
        win.play(Wait(0.3))   #停 0.3s

        say(cap, "move_camera frame_center=cube")
        self.move_camera(frame_center=cube, run_time=0.8)   #把画面中心挪到立方体上
        win.play(Wait(0.6))   #停 0.6s

        say(cap, "set_camera_orientation 全部复位")
        self.set_camera_orientation(phi=70 * DEGREES, theta=-135 * DEGREES,   #一步复位 phi/theta/gamma/zoom
                                    gamma=0, zoom=1, frame_center=ORIGIN)
        win.play(Wait(0.5))   #停 0.5s 收工
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：先用 `set_camera_orientation` 一帧跳到 `phi=30°` 的俯视角，再用 `move_camera` 平滑绕到 `70°/-45°`，接着同一条 `move_camera` 依次演示三个"局部"参数：`gamma` 让画面歪 25°、`zoom=1.8` 推近、`frame_center=cube` 把画面中心挪到立方体上（前两步不动中心、这一步不动缩放）。

最后用一个 `set_camera_orientation` 把 `phi`/`theta`/`gamma`/`zoom`/`frame_center` 五项一次性复位，镜头回到经典斜视角全景。

<video src="assets/RTM output/02-ThreeDScene-camera.mp4" controls width="560"></video>

> 提醒：`set_camera_orientation` 没有动画（一帧跳变），要平滑过渡就用 `move_camera`。`move_camera` 内部会调 `self.play`，在 RTM 里必须先写 `self.play = win.play`，否则镜头不动。角度都按弧度算，写 `25 * DEGREES` 才是 25°。
>
> 复位时 `frame_center=ORIGIN` 别忘了 —— 只写 `phi/theta` 的话，之前挪走的画面中心还在。
>
> 另外：`zoom` **构造参数**一直生效，但运行时的 `move_camera(zoom=…)` / `set_zoom` 到 2026-10-17 才在 RTM 里真正起作用（此前 `camera_state` 读的是 `ThreeDCamera` 只写一次的死属性 `camera.zoom`，而动画驱动的是 `zoom_tracker`／`get_zoom`），因此本段的 `zoom=1.8` 推近当时是无效的；修复后本条。

### begin/stop_ambient_camera_rotation、begin/stop_3dillusion_camera_rotation

环境旋转绕轴匀速转动（负值反向），转动只在"播放中"前进，配合 `Wait` 就是常见的环绕转场；3D 错觉旋转在当前视角附近小幅晃动，制造立体感。

```python
def begin_ambient_camera_rotation(self, rate: float = 0.02, about: str = "theta") -> None:
def stop_ambient_camera_rotation(self, about: str = "theta") -> None:
def begin_3dillusion_camera_rotation(self, rate: float = 1, origin_phi: float | None = None, origin_theta: float | None = None) -> None:
def stop_3dillusion_camera_rotation(self) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `rate` | `float` | `0.02`（错觉旋转 `1`） | 每秒转的弧度 / 晃动速率；**能填**任意实数，样例用 `0.15`、`0.2`；负值反向 |
| `about` | `str` | `"theta"` | 转哪根轴：`"theta"`（绕竖直轴环绕）、`"phi"`（俯仰）、`"gamma"`（自转）三选一 |
| `origin_phi` | `float \| None` | `None`（取当前值） | 错觉晃动围绕的极角，一般留空 |
| `origin_theta` | `float \| None` | `None`（取当前值） | 错觉晃动围绕的方位角，一般留空 |

> **返回**：无（`stop_*` 与 `begin_*` 的 `about` 必须成对）。

#### 样例：环境旋转 / 3D 错觉改动

环境旋转匀速绕轴，转的时候画面必须在"播放中"（RTM 里就是 `win.play(Wait(...))` 期间）；3D 错觉在当前视角附近小幅晃动。

```python
from real_time_manim import ThreeDScene, ThreeDAxes, Cube, Text, \
    BLUE, YELLOW, UP, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   #瞬间换掉顶部说明文字，不占动画时间
    cap.become(Text(text, font_size=30, color=YELLOW).to_edge(UP))

class RotationDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("", font_size=30, color=YELLOW)   #顶部说明文字（内容后面换）
        self.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把三个对象放进场景
        self.set_camera_orientation(phi=60 * DEGREES, theta=-90 * DEGREES)   #先摆好一个斜视角

        say(cap, "ambient rate=0.15 about=theta")
        self.begin_ambient_camera_rotation(rate=0.15, about="theta")   #绕竖直轴匀速环绕，每秒 0.15 弧度
        win.play(Wait(1.6))   #旋转期间一直 wait，画面持续转动
        self.stop_ambient_camera_rotation()   #停住（about 要和 begin 时一致）

        say(cap, "ambient rate=0.2 about=phi")
        self.begin_ambient_camera_rotation(rate=0.2, about="phi")   #改绕极角方向转
        win.play(Wait(1.6))   #旋转期间一直 wait
        self.stop_ambient_camera_rotation(about="phi")   #停住

        say(cap, "3dillusion rate=1")
        self.begin_3dillusion_camera_rotation(rate=1)   #在当前视角附近小幅晃动，造立体感
        win.play(Wait(1.6))   #晃动期间一直 wait
        self.stop_3dillusion_camera_rotation()   #停住
        win.play(Wait(0.3))   #停 0.3s 收工
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：先把镜头摆到斜视角，然后开三段旋转：第一段绕竖直轴（`about="theta"`）匀速环绕 1.6 秒后停；第二段换 `about="phi"` 俯仰方向再转 1.6 秒，`stop` 时把同样的 `about` 传回去；第三段开 3D 错觉旋转（`rate=1`），画面在当前视角附近小幅晃动出立体感，最后停住收工。

整个过程中顶部标题因为被钉在屏幕上，始终正对观众不动。

<video src="assets/RTM output/02-ThreeDScene-rotation.mp4" controls width="560"></video>

> 提醒：`stop_*` 的 `about` 要和 `begin_*` 时一致（`theta` 和 `phi` 各停各的，写错会停不掉）。
>
> 旋转只在"播放中"前进，RTM 里就是 `win.play(Wait(1.6))` 这类等待期间在转 —— 别换成不进播放循环的写法。构造参数 `ambient_camera_rotation` 没有这个效果（见样例 1），要转必须调方法。

### add/remove_fixed_in_frame_mobjects、add/remove_fixed_orientation_mobjects

`add_fixed_in_frame_mobjects` 把对象"钉"在屏幕上（位置和朝向都锁死，相机怎么转它都不动，适合 3D 场景里的标题、公式）；`add_fixed_orientation_mobjects` 只锁**朝向**（文字始终正对镜头，但位置仍在 3D 空间里、会跟着相机透视平移）；`remove_*` 解除对应锁定。

```python
def add_fixed_in_frame_mobjects(self, *mobjects: Mobject) -> None:
def remove_fixed_in_frame_mobjects(self, *mobjects: Mobject) -> None:
def add_fixed_orientation_mobjects(self, *mobjects: Mobject, **kwargs: Any) -> None:
def remove_fixed_orientation_mobjects(self, *mobjects: Mobject) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | — | 要钉住（或解除）的对象，可一次传多个 |
| `**kwargs` | `Any` | — | 仅 `add_fixed_orientation_mobjects`：`use_static_center_func: bool`、`center_func: Callable`，控制朝向锁定的中心点算法，一般留空 |

> **返回**：无。

#### 样例：`add_fixed_in_frame_mobjects`改动

同一个场景里放两个对象：标题用 `fixed_in_frame`（位置+朝向全锁），标签用 `fixed_orientation`（只锁朝向）；环绕一周后解除，两者立刻变回普通 3D 对象。

```python
from real_time_manim import ThreeDScene, ThreeDAxes, Cube, Text, \
    BLUE, GREEN, YELLOW, UP, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class FixedDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.2).set_color(BLUE)   #蓝色立方体当参照物
        title = Text("fixed_in_frame", font_size=34, color=YELLOW)   #演示屏幕钉扎的标题
        tag = Text("fixed_orientation", font_size=26, color=GREEN)   #演示朝向锁定的标签
        tag.next_to(cube, UP)   #标签摆在立方体上方的 3D 空间里
        self.add_fixed_in_frame_mobjects(title)   #标题：位置和朝向都锁死在屏幕上
        title.to_edge(UP)   #标题挪到画面顶端
        self.add_fixed_orientation_mobjects(tag)   #标签：只锁朝向，位置仍在 3D 空间
        self.add(axes, cube, tag)   #把坐标轴、立方体、标签放进场景（标题已被钉扎）
        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清两个对象的位置

        self.move_camera(theta=-140 * DEGREES, run_time=1.6)   #环绕 90°：标题纹丝不动，标签跟着立方体在画面里移动
        win.play(Wait(0.4))   #停 0.4s

        self.remove_fixed_in_frame_mobjects(title)   #解除屏幕钉扎
        self.remove_fixed_orientation_mobjects(tag)   #解除朝向锁定
        self.move_camera(theta=-190 * DEGREES, run_time=1.4)   #再环绕一次：两个对象都变成普通 3D 对象，跟着视角一起歪
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：先摆好斜视角看两个对象的初始状态 —— 黄色标题贴在屏幕顶端，绿色标签悬在立方体上方的 3D 空间里。

第一次 `move_camera` 环绕 90°：标题纹丝不动（钉死了），标签却跟着立方体在画面里挪了位置（因为它的位置还在 3D 空间）。然后把两种锁定都解除，第二次环绕时两者都变成普通 3D 对象，跟着视角一起歪、一起转到背面去。

<video src="assets/RTM output/02-ThreeDScene-fixed.mp4" controls width="560"></video>

> 提醒：`add_fixed_in_frame_mobjects` 会把对象**直接加进场景**，不用再 `self.add(...)`（样例里标题没出现在 `self.add` 的参数里，就是这个原因）；`remove_*` 只解除锁定，对象仍留在场景中。
>
> 想让文字"始终正对镜头但还能被透视推着走"（如贴着对象的标注）用 `fixed_orientation`，想完全静止（标题、字幕）用 `fixed_in_frame`。

### class SpecialThreeDScene

`ThreeDScene` 的加强版：默认开着色与指数投影，并带一套 3D 坐标轴、球体的默认参数。

配套方法：`get_axes()` 生成 3D 坐标轴、`get_sphere(**kwargs)` 生成球体、`get_default_camera_position()` 返回默认视角 dict、`set_camera_to_default_position()` 把相机设回默认斜视角。

> 上游 `manim` 0.21 在这个子类上有**三处 bug**（构造期读 `self.renderer`、默认 `three_d_axes_config` 含已删除的 `tick_frequency`、`get_axes` 用已删除的 `axis.tick_marks`），原样继承在命令行渲染下同样崩溃。
>
> 样例里给出三处绕法，照抄即可正常出片。

```python
def __init__(self, cut_axes_at_radius: bool = True, camera_config: dict = {"should_apply_shading": True, "exponential_projection": True}, three_d_axes_config: dict = {...}, sphere_config: dict = {"radius": 2, "resolution": (24, 48)}, default_angled_camera_position: dict = {"phi": 70 * DEGREES, "theta": -110 * DEGREES}, low_quality_config: dict = {...}, **kwargs: Any) -> None:
def get_axes(self) -> ThreeDAxes:
def get_sphere(self, **kwargs: Any) -> Surface:
def get_default_camera_position(self) -> dict:
def set_camera_to_default_position(self) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `cut_axes_at_radius` | `bool` | `True` | 坐标轴在球面半径处截断（不无限延伸）；**能填** `False` 让轴贯穿球体 |
| `camera_config` | `dict` | `{"should_apply_shading": True, "exponential_projection": True}` | 开着色 + 指数投影；一般不改 |
| `three_d_axes_config` | `dict` | 见源码 | `get_axes()` 的参数；上游默认值里有已失效的 `tick_frequency`，样例换成自己的 `AXIS_CFG` |
| `sphere_config` | `dict` | `{"radius": 2, "resolution": (24, 48)}` | `get_sphere()` 的默认参数，`get_sphere(**kwargs)` 可现场覆盖 |
| `default_angled_camera_position` | `dict` | `{"phi": 70*DEGREES, "theta": -110*DEGREES}` | 专属默认斜视角（注意是 `-110°`，不是 `ThreeDScene` 存的 `-135°`） |
| `low_quality_config` | `dict` | 见源码 | **不建议管**：RTM 恒为 1080p60，这个低画质覆盖永远不会触发 |
| `**kwargs` | `Any` | — | 透传给 `ThreeDScene.__init__` |

> **返回**：无（构造实例）。

#### 样例：`SpecialThreeDScene`改动

`SpecialThreeDScene` 自带截断坐标轴、半透明球体与专属默认视角；三处绕法分别对应上游三处 bug，写在注释里。

```python
from types import SimpleNamespace

from real_time_manim import SpecialThreeDScene, ThreeDAxes, VGroup, Line, \
    VectorizedPoint, Text, config, BLUE, YELLOW, UP, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

#上游 manim 0.21 bug 2：默认 three_d_axes_config 里的 tick_frequency
#在 0.21 的 NumberLine 里已不存在，原样传进去 TypeError，删掉这一项
AXIS_CFG = {
    "num_axis_pieces": 1,
    "axis_config": {
        "unit_size": 2,
        "numbers_with_elongated_ticks": [0, 1, 2],
        "stroke_width": 2,
    },
}


class SpecialDemo(SpecialThreeDScene):
    def __init__(self, **kwargs):
        #上游 manim 0.21 bug 1：SpecialThreeDScene 在 super().__init__() 之前
        #就读 self.renderer，先塞一个只带 camera_config 的替身绕过去
        self.renderer = SimpleNamespace(
            camera_config={"pixel_width": config.pixel_width})
        super().__init__(three_d_axes_config=AXIS_CFG, **kwargs)   #换掉带 tick_frequency 的默认坐标轴配置

    def get_axes(self):
        #上游 manim 0.21 bug 3：NumberLine 没有 tick_marks 属性了，
        #改用 get_tick_marks()，其余与 manim 源码逐字一致
        axes = ThreeDAxes(**self.three_d_axes_config)
        for axis in axes:
            if self.cut_axes_at_radius:
                p0 = axis.get_start()
                p1 = axis.number_to_point(-1)
                p2 = axis.number_to_point(1)
                p3 = axis.get_end()
                new_pieces = VGroup(Line(p0, p1), Line(p1, p2), Line(p2, p3))
                for piece in new_pieces:
                    piece.shade_in_3d = True
                new_pieces.match_style(axis.pieces)
                axis.pieces.submobjects = new_pieces.submobjects
            for tick in axis.get_tick_marks():
                tick.add(VectorizedPoint(1.5 * tick.get_center()))
        return axes

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        axes = self.get_axes()   #按 three_d_axes_config 生成，坐标轴在球面半径处截断
        sphere = self.get_sphere(color=BLUE, fill_opacity=0.55)   #sphere_config 默认 radius=2、resolution=(24, 48)
        cap = Text("SpecialThreeDScene", font_size=32, color=YELLOW)   #顶部标题
        self.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, sphere, cap)   #把坐标轴、球体、标题放进场景
        self.set_camera_to_default_position()   #回到 default_angled_camera_position（phi=70° theta=-110°）
        print("默认视角：", self.get_default_camera_position())   #把默认视角打到控制台
        win.play(Wait(0.8))   #停 0.8s 看清默认斜视角
        self.move_camera(phi=50 * DEGREES, theta=-150 * DEGREES, run_time=1.4)   #环绕展示立体感
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：先用三处绕法把上游 bug 垫掉（替身 `renderer`、删 `tick_frequency`、覆写 `get_axes`），然后按配置生成"在球面半径处截断"的坐标轴和半透明球体，钉上标题。

`set_camera_to_default_position()` 回到这个子类专属的默认斜视角（控制台同时打印 `get_default_camera_position()` 的内容），停 0.8 秒后再 `move_camera` 环绕一圈展示立体感。

<video src="assets/RTM output/02-ThreeDScene-special.mp4" controls width="560"></video>

> 提醒：三处绕法（`self.renderer` 替身、删 `tick_frequency`、`get_tick_marks()`）缺一个都会崩，照抄即可；它们不是 RTM 特有的补丁，纯命令行渲染同样需要。
>
> `SpecialThreeDScene` 的默认视角是 `phi=70° theta=-110°`，和 `ThreeDScene` 构造里存的 `-135°` 不是同一个，别混用。
>
> `low_quality_config` 是给 `-ql` 低画质渲染准备的，RTM 恒为 1080p60，永远走不到。

---

相关：[ThreeDCamera](../相机/03-ThreeDCamera.md)、[MovingCameraScene](01-MovingCameraScene.md)、[Scene 基础](../场景/01-Scene基础.md)
