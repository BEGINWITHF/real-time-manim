# Camera（Cairo 基类相机）

所有场景背后默默干活的基类相机：RTM 会按窗口把它建好，你几乎不用手动构造。日常真正能用上的只有三样：背景色、`is_in_frame` 判定、`use_z_index` 绘制顺序。

其余构造参数，以及「读像素 / 手动抓帧」那半边 API，都属 Cairo 像素管线——RTM 走 Vulkan 渲染，没有接线（下文标）。

## 参数

### class Camera（构造参数）

```python
def __init__(self, background_image: str | None = None, frame_center: Point3D = ORIGIN, image_mode: str = "RGBA", n_channels: int = 4, pixel_array_dtype: str = "uint8", cairo_line_width_multiple: float = 0.01, use_z_index: bool = True, background: PixelArray | None = None, pixel_height: int | None = None, pixel_width: int | None = None, frame_height: float | None = None, frame_width: float | None = None, frame_rate: float | None = None, background_color: ParsableManimColor | None = None, background_opacity: float | None = None, **kwargs: Any) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `background_image` | `str \| None` | `None` | 背景图路径； **未接线**：背景图属 Cairo 像素合成，RTM 的向量渲染不认它 |
| `frame_center` | `Point3D` | `ORIGIN` | 画面中心；**不建议改**：CE 会按它挪画面，RTM 画面固定居中不动（只改变 `is_in_frame` 的判定中心），两引擎不一致 |
| `image_mode` | `str` | `"RGBA"` | 像素模式； **未接线**（像素数组专用，RTM 没有 `pixel_array`） |
| `n_channels` | `int` | `4` | 像素通道数； **未接线**，同上 |
| `pixel_array_dtype` | `str` | `"uint8"` | 像素数组 dtype； **未接线**，同上 |
| `cairo_line_width_multiple` | `float` | `0.01` | Cairo 线宽倍数； **未接线**：RTM 自己光栅化描边，不用这个系数 |
| `use_z_index` | `bool` | `True` | 是否按 `z_index` 排序绘制；**能填** `True`/`False`，两引擎都生效（运行期改属性同样生效，见样例 3） |
| `background` | `PixelArray \| None` | `None` | 初始背景像素数组； **未接线**，像素数组专用 |
| `pixel_height` | `int \| None` | `None` → 取 `config` | 输出像素高度；**不建议改**：RTM 只输出 1920×1080，填什么都不改变画面 |
| `pixel_width` | `int \| None` | `None` → 取 `config` | 输出像素宽度；同上 |
| `frame_height` | `float \| None` | `None` → 取 `config` | 逻辑画幅高（默认 8.0）；**不建议改**：坐标换算固定按 `config` 画幅走，改了不生效 |
| `frame_width` | `float \| None` | `None` → 取 `config` | 逻辑画幅宽（默认 14.222）；同上 |
| `frame_rate` | `float \| None` | `None` → 取 `config` | 帧率；**不建议改**：RTM 固定 60fps |
| `background_color` | `ParsableManimColor \| None` | `None` → `config.background_color` | 背景色；能填任意颜色，但构造参数传不进来（见下），用 property 更直接（样例 1） |
| `background_opacity` | `float \| None` | `None` → `config.background_opacity` | 背景不透明度 0~1；能读能写但出片无变化（样例 1） |
| `**kwargs` | `Any` | — | 额外关键字参数（签名中列出） |

**返回**：无（构造实例）。所有为 `None` 的参数会自动取 `config` 的同名值。

为什么这节不出视频：`Scene` 只保存 `camera_class` 这个**类**，渲染器建相机用的是 `camera_class()` 无参调用——构造参数根本递不进去（想递只能用 `functools.partial(Camera, ...)` 或子类覆盖默认值）。

而这批参数又没有一个值得费这个劲：

- 像素管线参数，RTM 压根不走；
- 背景相关的两个，直接改 property（样例 1）；
- `use_z_index`，运行期改属性一样生效（样例 3）。

### Camera.background_color / Camera.background_opacity（property）

```python
def background_color(self) -> ManimColor:
def background_color(self, color: ManimColor) -> None:
def background_opacity(self) -> float:
def background_opacity(self, alpha: float) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `color` | `ManimColor` | — | 赋值立即重建背景；**能填**任意颜色字符串或常量（`"#1E3A5F"`、`BLUE`…） |
| `alpha` | `float` | — | 0~1；**能读能写，但出片画面不变**——视频只存 RGB，没有透明通道 |

**返回**：getter 返回 `ManimColor` / `float`；setter 无返回，赋值立即生效（不用等下一帧动画）。

#### 样例：background_color / background_opacity

```python
from real_time_manim import (
    BLUE, RED, WHITE, YELLOW,
    DOWN, LEFT, RIGHT, UP,
    Circle, FadeIn, Scene, Square, Text,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class BackgroundDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE).set_fill(BLUE, 0.8)   #一个蓝色方块当参照物
        cap = Text("default background", font_size=32, color=YELLOW).to_edge(UP)   #顶部说明
        self.add(sq, cap)   #把方块和说明放进场景
        win.play(FadeIn(sq), run_time=0.5)   #方块淡入：此刻还是默认的黑背景
        win.play(Wait(0.4))   #停 0.4s
        self.camera.background_color = "#1E3A5F"   #改背景色：赋值立即生效
        cap.become(Text("background_color = '#1E3A5F'", font_size=32, color=YELLOW).to_edge(UP))   #说明文字换成背景色
        win.play(Wait(0.8))   #停 0.8s 看清深蓝背景
        self.camera.background_opacity = 0.6   #改背景不透明度：可读可写
        info = Text("background_opacity = 0.6 (video unchanged)", font_size=26, color=WHITE).next_to(cap, DOWN)   #读回透明度：出片是不透明的 MP4
        self.add(info)   #把读数放进场景
        win.play(Wait(0.8))   #停 0.8s：画面不会变淡
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：先放一个蓝色方块，此刻背景还是 manim 默认的黑。

接着一行 `self.camera.background_color = "#1E3A5F"` 把背景换成深蓝——不用播放任何动画，赋值那一瞬间画面就变了，视频里能清楚看到背景跳色。

然后写入 `background_opacity = 0.6` 并把当前值打到屏幕上：这个值读得出来也写得进去，但出片是不透明的 MP4（只有 RGB），所以后半段画面纹丝不动。

<video src="assets/RTM output/01-Camera-background.mp4" controls width="560"></video>

> 提醒：
>
> - 背景色随时可改、随时生效，做「换色转场」不用额外动画。
> - `background_opacity` 只是记录在相机上的一个数，导出视频时会被丢掉——想做半透明效果，请给 mobject 本身设 `fill_opacity`，别指望背景变淡。
> - `MLWindow(960, 540)` 会被强制纠正成 1920×1080 并打印一行提示，这不是报错。

### Camera.is_in_frame(mobject)

```python
def is_in_frame(self, mobject: Mobject) -> bool:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | 待判断对象；**能填**任意 mobject（不算子对象的单独成员） |

**返回**：`bool`。按取景框边界做纯数学判定：整个对象都在画面外返回 `False`，**露出一点就算 `True`**（RTM 下取景框固定为默认画幅 14.222×8、中心 ORIGIN；`MovingCamera` 下按它的 `frame` 算）。

#### 样例：is_in_frame

```python
from real_time_manim import (
    BLUE, RED, WHITE, YELLOW,
    DOWN, LEFT, RIGHT, UP,
    Circle, FadeIn, Scene, Square, Text,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class IsInFrameDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        near = Square(color=BLUE).set_fill(BLUE, 0.8)   #画面正中的方块：在取景框内
        far = Circle(radius=0.8, color=RED).shift(RIGHT * 10)   #远处的圆：在取景框外
        cap = Text("camera.is_in_frame(mobject) -> bool", font_size=30, color=YELLOW).to_edge(UP)   #顶部说明
        info = Text("square=%s  circle=%s" % (self.camera.is_in_frame(near), self.camera.is_in_frame(far)),
                    font_size=28, color=WHITE).next_to(cap, DOWN)   #第一组读数：方块 True、圆 False
        self.add(near, far, cap, info)   #把四个对象放进场景
        win.play(FadeIn(near), run_time=0.5)   #方块淡入
        win.play(Wait(0.5))   #停 0.5s
        win.play(near.animate.shift(RIGHT * 8.5), run_time=0.8)   #把方块推出取景框
        info.become(Text("after move: square=%s" % self.camera.is_in_frame(near),
                    font_size=28, color=WHITE).next_to(cap, DOWN))   #第二组读数：方块变 False
        win.play(Wait(0.8))   #停 0.8s 收工
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：画面正中放一个方块、右边很远处放一个圆（远到根本看不见），先读一组 `is_in_frame` 结果打到屏幕上——方块 `True`、圆 `False`；然后把方块平移出画面，动画结束后再判一次，读数翻成 `False`。

整个判定是纯几何计算、不碰渲染，所以任何时刻调用都是瞬间出结果，常用来做「对象出画就换镜头」这类逻辑。

<video src="assets/RTM output/01-Camera-is_in_frame.mp4" controls width="560"></video>

> 提醒：
>
> - 判定标准是「和取景框有没有交集」，对象一半在画面外照样返回 `True`；圆放在 `RIGHT * 10` 加进场景后完全看不见，这正是 `False` 的效果——出不出画不用肉眼猜，问它就行。
> - 普通 `Camera` 的取景框永远是默认画幅，`frame_center` 改了它也跟着变（但画面不动，见上表），拿不准就别动 `frame_center`。

### Camera.use_z_index

**作用**：是否按 `z_index` 排序绘制。属性可读写（`True`/`False`），改完下一帧就生效。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `use_z_index` | `bool` | `True` | **能填** `True`（按 `z_index` 排序，`z_index` 大的画在上面）/ `False`（按添加顺序绘制，后加的画在上面） |

**返回**：无（普通属性赋值）。

#### 样例：use_z_index

```python
from real_time_manim import (
    BLUE, RED, WHITE, YELLOW,
    DOWN, LEFT, RIGHT, UP,
    Circle, FadeIn, Scene, Square, Text,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class UseZIndexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        a = Square(color=BLUE).set_fill(BLUE, 0.9).shift(LEFT * 0.4)   #蓝色方块：先加进场景
        a.z_index = 1   #z 序高：use_z_index=True 时画在上面
        b = Square(color=RED).set_fill(RED, 0.9).shift(RIGHT * 0.4)   #红色方块：后加进场景
        b.z_index = 0   #z 序低：只按添加顺序绘制时反而在上面
        cap = Text("use_z_index=True", font_size=32, color=YELLOW).to_edge(UP)   #顶部说明
        self.add(a, b, cap)   #先 a 后 b 放进场景
        win.play(Wait(1.0))   #停 1.0s：蓝色在上（按 z_index 排序绘制）
        self.camera.use_z_index = False   #关掉 z 序：改成按添加顺序绘制
        cap.become(Text("use_z_index=False", font_size=32, color=YELLOW).to_edge(UP))   #说明文字跟着换
        win.play(Wait(1.0))   #停 1.0s：红色在上（后加的画在上面）
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：两个半透明方块错开叠放，蓝色先加但 `z_index=1`、红色后加但 `z_index=0`。

前半段 `use_z_index=True`（默认），按 `z_index` 排序绘制，重叠区是蓝色压着红色；中途一行 `self.camera.use_z_index = False` 关掉 z 序，立刻改成按添加顺序绘制，重叠区翻成红色压着蓝色。

同一对对象、同一位置，只改这一个布尔值，上下关系整个反过来。

<video src="assets/RTM output/01-Camera-use_z_index.mp4" controls width="560"></video>

> 提醒：这是运行期属性，不需要重新建相机——构造参数传不进 `Camera`（见本页开头），直接 `self.camera.use_z_index = False` 就行。
>
> 另外，两个对象 `z_index` 相同时，两种模式的画面完全一样（都按添加顺序），所以想看出差异，得像样例这样给对象设不同的 `z_index`。

### 像素读取与手动捕获（capture_mobjects / capture_mobject / get_image / set_background_from_func）

```python
def capture_mobjects(self, mobjects: Iterable[Mobject], **kwargs: Any) -> None:
def capture_mobject(self, mobject: Mobject, **kwargs: Any) -> None:
def get_image(self, pixel_array: PixelArray | list | tuple | None = None) -> Image.Image:
def set_background_from_func(self, coords_to_colors_func: Callable[[np.ndarray], np.ndarray]) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobjects` | `Iterable[Mobject]` | — | `capture_mobjects`：要捕获的对象 |
| `mobject` | `Mobject` | — | `capture_mobject`：要捕获的对象 |
| `**kwargs` | `Any` | — | 透传给 `get_mobjects_to_display`，如 `excluded_mobjects=[...]` |
| `pixel_array` | `PixelArray \| list \| tuple \| None` | `None` | `get_image`：为 `None` 时取当前帧 |
| `coords_to_colors_func` | `Callable[[np.ndarray], np.ndarray]` | — | `set_background_from_func`：输入 (x,y) 坐标对，输出 4 元素 RGBA 浮点数组 |

**返回**：`capture_mobjects` / `capture_mobject` / `set_background_from_func` 无返回；`get_image` 返回 `PIL.Image.Image`。

**无视频**：这四个是 Cairo 像素数组管线的 API——把画面画进 `camera.pixel_array` 再读回来。RTM 走 Vulkan 向量渲染，画完直接进窗口/编码器，根本没有可读的像素数组，这些调用拿不到当帧图像。

想要「截一帧」，请用 `fast_record_scene` 出片后用 ffmpeg 抽帧。

**补充区分**：**相机**的 `background_image`（构造参数）在 RTM 下未接线（见本页开头参数表）；这里说的是**给 mobject** 用的 `Mobject.color_using_background_image`——RTM 只取那张图片的平均色当作该对象的描边色（`real_time_manim/background_color.py:1-40`），与「截一帧当背景」无关，也不构成截帧手段。

---

相关：[MovingCamera](02-MovingCamera.md)、[ThreeDCamera](03-ThreeDCamera.md)、[MovingCameraScene](../专用场景/01-MovingCameraScene.md)、[Scene 基础](../场景/01-Scene基础.md)
