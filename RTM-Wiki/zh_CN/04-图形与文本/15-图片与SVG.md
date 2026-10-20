# 图片与 SVG

把位图照片与 SVG 矢量文件放进场景的入口类。每个类各一条样例，样例里把该类**全部可填参数**各改一次（`ImageMobjectFromCamera` 与 `VMobjectFromSVGPath` 原本"未单独出片"，现在补上了）。

> **三个容易踩的点（都在样例里验证过，两引擎一致）**
> 1. 类名是 **`ImageMobject`**（小写 `m`），不是旧文档里的 `ImageMObject`；`real_time_manim` 顶层直接导出 `ImageMobject`、`ImageMobjectFromCamera`、`SVGMobject`、`VMobjectFromSVGPath`、`Camera`；`AbstractImageMobject` **不在**顶层，要从 `manim.mobject.types.image_mobject` 导入（一般不直接构造它）。
> 2. `SVGMobject(..., svg_default={...})` 是**整份**默认样式表：键必须齐全（`color` / `fill_color` / `fill_opacity` / `stroke_color` / `stroke_opacity` / `stroke_width` / `opacity`），少一个就 `KeyError: 'color'`。
> 3. `VMobjectFromSVGPath(path_obj, ...)` 要的是**已解析的 `svgelements.Path`**（`se.Path("M 0 0 L 2 0 L 2 2 Z")`），直接传 `d` 字符串会抛 `AttributeError: 'str' object has no attribute 'approximate_arcs_with_quads'`——页面旧表格里写的 `str` 是不对的。

## 参数

### `ImageMobject`

```python
def __init__(self, filename_or_array: StrPath | np.ndarray, scale_to_resolution: int = 1080, invert: bool = False, image_mode: str = "RGBA", **kwargs) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `filename_or_array` | `str \| Path \| np.ndarray` | 必填 | 图片路径（png/jpg…）或像素数组；样例用 `assets/demo_photo.png` |
| `scale_to_resolution` | `int` | `1080` | 把图片缩放到的目标分辨率高度；调成 `120` 再配 `NEAREST` 会明显像素化 |
| `invert` | `bool` | `False` | 颜色反转（扫描件/暗底图常用） |
| `image_mode` | `str` | `'RGBA'` | 像素模式（`'RGBA'` 带透明通道，`'RGB'` 不带） |

方法：`set_opacity(alpha)`、`get_pixel_array()`（返回 `(H, W, 4)` 的 `uint8` 数组）、`set_resampling_algorithm(算法)`。

#### 样例：默认 / 低分辨率+NEAREST / `invert` / `set_opacity`+`image_mode` / 读像素数组

```python
import os
import sys
import svgelements as se
from PIL import Image
from real_time_manim import (
    Scene, ImageMobject, ImageMobjectFromCamera, SVGMobject, VMobjectFromSVGPath,
    Square, Circle, Triangle, Dot, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class ImageDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("15-ImageMobject", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题
        photo = os.path.join(ASSETS, "demo_photo.png")   #参数 “filename_or_array”：图片路径

        # —— 默认：scale_to_resolution=1080 ——
        a = ImageMobject(photo).scale(1.1).move_to([-4.4, 0.9, 0])
        cap = Text("default", font_size=18, color=GREY_B).next_to(a, DOWN, buff=0.3)
        win.play(FadeIn(a), FadeIn(cap), run_time=0.5)

        # —— scale_to_resolution 调小 + NEAREST 重采样：像素化 ——
        b = ImageMobject(photo, scale_to_resolution=120)   #参数 “scale_to_resolution”
        b.set_resampling_algorithm(Image.Resampling.NEAREST)   #方法 “set_resampling_algorithm”
        b.scale(1.1).move_to([0, 0.9, 0])
        cap2 = Text("scale_to_resolution=120 + NEAREST", font_size=18, color=GREY_B).next_to(b, DOWN, buff=0.3)
        win.play(FadeIn(b), FadeIn(cap2), run_time=0.5)

        # —— invert=True：颜色反转 ——
        c = ImageMobject(photo, invert=True).scale(1.1).move_to([4.4, 0.9, 0])   #参数 “invert”
        cap3 = Text("invert=True", font_size=18, color=GREY_B).next_to(c, DOWN, buff=0.3)
        win.play(FadeIn(c), FadeIn(cap3), run_time=0.5)

        # —— set_opacity + image_mode：半透明叠在另一张上 ——
        d = ImageMobject(photo, image_mode="RGB").scale(1.1).move_to([-1.4, -1.9, 0])   #参数 “image_mode”
        e = ImageMobject(photo).scale(1.1).move_to([-0.2, -1.9, 0])   #垫在下面的一张
        d.set_opacity(0.5)   #方法 “set_opacity(alpha)”
        cap4 = Text("set_opacity(0.5)  image_mode='RGB'", font_size=18, color=GREY_B).next_to(d, DOWN, buff=0.3)
        win.play(FadeIn(e), FadeIn(d), FadeIn(cap4), run_time=0.6)

        # —— get_pixel_array：把像素数组的形状打成读数 ——
        arr = d.get_pixel_array()   #方法 “get_pixel_array()”
        cap5 = Text("pixel_array %s %s" % (arr.shape, arr.dtype),
                    font_size=18, color=GREY_B).next_to(e, DOWN, buff=1.0)
        win.play(FadeIn(cap5), run_time=0.4)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：ImageMobjectFromCamera —— 把相机画面当图片 ==================
```

这段代码在做什么：同一个文件渲染五遍——第一张默认（`scale_to_resolution=1080`）；第二张把分辨率压到 120 并把重采样算法换成 `NEAREST`，放大看就是马赛克；第三张 `invert=True`，颜色整体反转；第四张 `image_mode='RGB'` 并 `set_opacity(0.5)`，半透明地叠在另一张同图上（能看到下面那张透出来）；最后把 `get_pixel_array()` 的形状与 dtype 打成读数。

<video src="assets/RTM output/15-图片与SVG-image.mp4" controls width="560"></video>

> 提醒：`scale_to_resolution` 决定"加载时把像素降到多少"，图像在屏幕上显示多大由 `.scale()`/`.set(height=…)` 决定；两者都小的时候才看得出马赛克，所以样例特意把两个方向都调小。

### `ImageMobjectFromCamera`

```python
def __init__(self, camera: MovingCamera, default_display_frame_config: dict | None = None, **kwargs) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `camera` | `Camera` | 必填 | 来源相机；场景里就是 `self.camera`，要先 `capture_mobject(...)` 把画面拍进 `pixel_array` 才有内容 |
| `default_display_frame_config` | `dict \| None` | `{"stroke_width": 3, "stroke_color": WHITE, "buff": 0}` | 外框默认样式；样例给了粗黄框 `{"stroke_width": 6, "stroke_color": YELLOW, "buff": 0}` |

方法：`add_display_frame(**kwargs)`（事后加/换外框，kwargs 覆盖 `default_display_frame_config`）、`get_pixel_array()`。

#### 样例：`capture_mobject` + 构造参数外框 + `add_display_frame`

```python
import os
import sys
import svgelements as se
from PIL import Image
from real_time_manim import (
    Scene, ImageMobject, ImageMobjectFromCamera, SVGMobject, VMobjectFromSVGPath,
    Square, Circle, Triangle, Dot, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class ImageFromCameraDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("15-ImageMobjectFromCamera", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 先在场景里摆几个对象，再用相机把它们“拍”下来 ——
        sq = Square(side_length=1.5, color=BLUE).move_to([-2.4, 1.4, 0])
        tri = Triangle(color=GREEN).scale(0.9).move_to([0.4, 1.4, 0])
        dot = Dot([2.6, 1.4, 0], color=ORANGE, radius=0.35)
        win.play(Create(sq), Create(tri), FadeIn(dot), run_time=0.5)
        self.camera.capture_mobject(VGroup(sq, tri, dot))   #把这三个对象画进相机的像素数组

        # —— default_display_frame_config：构造时就指定外框样式 ——
        img = ImageMobjectFromCamera(self.camera,
                                     default_display_frame_config={"stroke_width": 6, "stroke_color": YELLOW, "buff": 0})   #参数 “camera / default_display_frame_config”
        img.set(height=2.4).move_to([-3.6, -1.3, 0])
        win.play(FadeIn(img), run_time=0.7)   #外框是粗黄框

        # —— add_display_frame：事后加外框（可覆盖样式）——
        img2 = ImageMobjectFromCamera(self.camera)   #参数 “camera”
        img2.set(height=2.4).move_to([0.8, -1.3, 0])
        img2.add_display_frame(stroke_color=TEAL, buff=0.1)   #方法 “add_display_frame(**kwargs)”
        win.play(FadeIn(img2), run_time=0.7)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：AbstractImageMobject —— 像素数组三个方法 ====================
```

这段代码在做什么：先在场景里摆三个对象（方、三角、点）并用 `self.camera.capture_mobject(...)` 把它们"拍"进相机；然后用同一张相机画面做两个图片对象——左边那个在构造时就给了粗黄外框（`default_display_frame_config`），右边那个用默认外框并在事后 `add_display_frame(stroke_color=TEAL, buff=0.1)` 换成青色框。

<video src="assets/RTM output/15-图片与SVG-imagefromcamera.mp4" controls width="560"></video>

> 提醒：它拿的是相机**当下**的 `pixel_array`，所以顺序是"先摆对象 → `capture_mobject` → 再构造图片对象"；之后再改场景不会回写这张图（它是静态快照）。

### `AbstractImageMobject`

```python
def __init__(self, scale_to_resolution: int, pixel_array_dtype: str = "uint8", resampling_algorithm: Resampling = Resampling.BICUBIC, **kwargs) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `scale_to_resolution` | `int` | 必填 | 目标分辨率高度（具体类 `ImageMobject` 已代填 `1080`） |
| `pixel_array_dtype` | `str` | `'uint8'` | 像素数组类型；样例写 `"uint8"` 并把它打成读数 |
| `resampling_algorithm` | `Resampling` | `BICUBIC` | 缩放时的重采样算法；样例 `Image.Resampling.BICUBIC` 与 `NEAREST` 对比 |

**不直接构造**（抽象基类，顶层也不导出）：关心像素数组与重采样时用它的方法——`get_pixel_array()`、`set_resampling_algorithm(...)`、`set_color(...)`。

#### 样例：`NEAREST` + `set_color` + `BICUBIC` 对比

```python
import os
import sys
import svgelements as se
from PIL import Image
from real_time_manim import (
    Scene, ImageMobject, ImageMobjectFromCamera, SVGMobject, VMobjectFromSVGPath,
    Square, Circle, Triangle, Dot, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class AbstractImageDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("15-AbstractImageMobject", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题
        photo = os.path.join(ASSETS, "demo_photo.png")

        # —— 抽象基类不直接构造：拿一个具体实例来用它的方法 ——
        img = ImageMobject(photo, scale_to_resolution=200, pixel_array_dtype="uint8")   #参数 “scale_to_resolution / pixel_array_dtype”
        img.set_resampling_algorithm(Image.Resampling.NEAREST)   #方法 “set_resampling_algorithm”
        img.scale(1.3).move_to([-3.4, 0.4, 0])
        arr = img.get_pixel_array()   #方法 “get_pixel_array()”
        cap = Text("dtype=%s shape=%s" % (arr.dtype, arr.shape),
                   font_size=18, color=GREY_B).next_to(img, DOWN, buff=0.35)
        win.play(FadeIn(img), FadeIn(cap), run_time=0.6)

        # —— set_color：整体染色 ——
        img.set_color(RED)   #方法 “set_color(color)”
        cap2 = Text("set_color(RED)", font_size=18, color=GREY_B).next_to(cap, DOWN, buff=0.2)
        win.play(FadeIn(cap2), run_time=0.4)

        # —— 同一张图换个重采样算法（BICUBIC）：边缘更平滑 ——
        img2 = ImageMobject(photo, scale_to_resolution=200, resampling_algorithm=Image.Resampling.BICUBIC)   #参数 “resampling_algorithm”
        img2.set(height=img.height).move_to([2.6, 0.4, 0])
        cap3 = Text("resampling=BICUBIC", font_size=18, color=GREY_B).next_to(img2, DOWN, buff=0.35)
        win.play(FadeIn(img2), FadeIn(cap3), run_time=0.5)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：SVGMobject —— 矢量文件 ======================================
```

这段代码在做什么：拿一个 `ImageMobject` 实例来演示基类接口——先给 `scale_to_resolution=200`、`pixel_array_dtype="uint8"` 并用 `NEAREST` 重采样，读一次 `get_pixel_array()` 的 dtype/形状打在下面；再调用 `set_color(RED)` 把整张图染色；右侧放同一张图但用 `resampling_algorithm=BICUBIC`，边缘比左侧平滑。

<video src="assets/RTM output/15-图片与SVG-abstractimage.mp4" controls width="560"></video>

> 提醒：`set_color()` 是把整张图"染一层色"（乘算），不是调色板替换；要淡入淡出用 `set_opacity()` 更自然。

### `SVGMobject`

```python
def __init__(self, file_name: str | Path | None = None, should_center: bool = True, height: float | None = 2, width: float | None = None, color: ManimColor | None = None, opacity: float | None = None, fill_color: ManimColor | None = None, fill_opacity: float | None = None, stroke_color: ManimColor | None = None, stroke_opacity: float | None = None, stroke_width: float | None = None, svg_default: dict | None = None, path_string_config: dict | None = None, use_svg_cache: bool = True, **kwargs) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `file_name` | `str \| Path \| None` | `None` | SVG 文件路径（样例 `assets/demo_icon.svg`） |
| `should_center` | `bool` | `True` | 是否把图形移到原点居中；`False` 保留文件里的坐标原点 |
| `height` | `float \| None` | `2` | 加载后的高度（样例 `1.1`、`1.5`） |
| `width` | `float \| None` | `None` | 按宽度缩放（与 `height` 二选一；样例 `2.2`） |
| `color` | `ManimColor \| None` | `None` | 统一颜色（填充与描边都变）；样例 `WHITE` |
| `opacity` | `float \| None` | `None` | 整体不透明度；样例 `0.6` |
| `fill_color` | `ManimColor \| None` | `None` | 填充色；样例 `TEAL` |
| `fill_opacity` | `float \| None` | `None` | 填充不透明度；样例 `0.8` |
| `stroke_color` | `ManimColor \| None` | `None` | 描边色；样例 `ORANGE` |
| `stroke_opacity` | `float \| None` | `None` | 描边不透明度；样例 `1.0` |
| `stroke_width` | `float \| None` | `None` | 描边宽度；样例 `8` |
| `svg_default` | `dict \| None` | `None` | **整份**默认样式表（键要齐全，否则 `KeyError: 'color'`）；一般用上面那些 `fill_*`/`stroke_*` 参数更省事 |
| `path_string_config` | `dict \| None` | `None` | 传给每条路径解析的配置（如 `{"long_lines": True}`） |
| `use_svg_cache` | `bool` | `True` | 复用同文件的解析缓存；作图对比时可关掉 |

返回 `SVGMobject`（子对象是各条路径，可逐个变色/动画）；`Text` 本身就是它的子类。

#### 样例：默认 / `height`+`color` / `width` / `should_center` / 填充描边六件套 / `svg_default` / 逐路径变色

```python
import os
import sys
import svgelements as se
from PIL import Image
from real_time_manim import (
    Scene, ImageMobject, ImageMobjectFromCamera, SVGMobject, VMobjectFromSVGPath,
    Square, Circle, Triangle, Dot, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class SVGDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("15-SVGMobject", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题
        icon_path = os.path.join(ASSETS, "demo_icon.svg")   #参数 “file_name”

        # —— 默认：height=2、should_center=True ——
        i1 = SVGMobject(icon_path).move_to([-5.4, 0.9, 0])
        win.play(FadeIn(i1), FadeIn(Text("default", font_size=18, color=GREY_B).next_to(i1, DOWN, buff=0.2)), run_time=0.5)

        # —— height / color：只想变高和统一颜色 ——
        i2 = SVGMobject(icon_path, height=1.1, color=WHITE).move_to([-2.8, 0.9, 0])   #参数 “height / color”
        win.play(FadeIn(i2), FadeIn(Text("height=1.1 color=WHITE", font_size=18, color=GREY_B).next_to(i2, DOWN, buff=0.2)), run_time=0.5)

        # —— width：按宽度缩放（与 height 二选一）——
        i3 = SVGMobject(icon_path, width=2.2).move_to([0.2, 0.9, 0])   #参数 “width”
        win.play(FadeIn(i3), FadeIn(Text("width=2.2", font_size=18, color=GREY_B).next_to(i3, DOWN, buff=0.2)), run_time=0.5)

        # —— should_center=False：不再居中（原点保持在文件原点）——
        i4 = SVGMobject(icon_path, height=1.1, should_center=False).move_to([2.6, 0.9, 0])   #参数 “should_center”
        win.play(FadeIn(i4), FadeIn(Text("should_center=False", font_size=18, color=GREY_B).next_to(i4, DOWN, buff=0.2)), run_time=0.5)

        # —— 填充/描边六件套 + opacity ——
        i5 = SVGMobject(icon_path, height=1.5, opacity=0.6, fill_color=TEAL, fill_opacity=0.8,
                        stroke_color=ORANGE, stroke_opacity=1.0, stroke_width=8,
                        use_svg_cache=False).move_to([-4.6, -2.0, 0])   #参数 “opacity / fill_* / stroke_* / use_svg_cache”
        win.play(FadeIn(i5), FadeIn(Text("fill/stroke 六件套", font_size=18, color=GREY_B).next_to(i5, DOWN, buff=0.2)), run_time=0.6)

        # —— svg_default / path_string_config：覆盖文件内部默认样式 ——
        # svg_default 是**整份**默认样式表（键必须齐全，缺一个就 KeyError）
        i6 = SVGMobject(icon_path, height=1.5,
                        svg_default={"color": None, "fill_color": RED, "fill_opacity": 1.0,
                                     "stroke_color": YELLOW, "stroke_opacity": 1.0,
                                     "stroke_width": 6, "opacity": None},
                        path_string_config={"long_lines": True}).move_to([-1.4, -2.0, 0])   #参数 “svg_default / path_string_config”
        win.play(FadeIn(i6), FadeIn(Text("svg_default={整份样式表}", font_size=18, color=GREY_B).next_to(i6, DOWN, buff=0.2)), run_time=0.6)

        # —— 子对象是各条路径：可以逐个变色 ——
        i7 = SVGMobject(icon_path, height=1.5).move_to([2.2, -2.0, 0])
        i7[0].set_color(PURPLE)   #第一条路径（星形）
        i7[1].set_color(GREEN)   #第二条路径（圆）
        win.play(FadeIn(i7), FadeIn(Text("i7[0] / i7[1] 分别变色", font_size=18, color=GREY_B).next_to(i7, DOWN, buff=0.2)), run_time=0.6)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：VMobjectFromSVGPath —— 手头的 path 数据 =====================
```

这段代码在做什么：同一个图标七连拍——默认（高 2、居中）；`height=1.1` 加 `color=WHITE`；`width=2.2`；`should_center=False`（能看到它没被搬回原点）；`opacity` + `fill_color/fill_opacity` + `stroke_color/stroke_opacity/stroke_width` 一起给，并 `use_svg_cache=False`；`svg_default` 给一整份样式表（红填充黄描边）并配 `path_string_config`；最后把 `i7[0]`（星形）和 `i7[1]`（圆）分别染成紫色和绿色，证明子对象就是一条条路径。

<video src="assets/RTM output/15-图片与SVG-svg.mp4" controls width="560"></video>

> 提醒：`color` 会同时盖掉填充与描边，想让填充和描边不同色就别用 `color`，改用 `fill_color` + `stroke_color`；`svg_default` 一旦给了就会**替换**整套默认样式（不是合并），所以样例里七个键全写上了。

### `VMobjectFromSVGPath`

```python
def __init__(self, path_obj: svgelements.Path, long_lines: bool = False, should_subdivide_sharp_curves: bool = False, should_remove_null_curves: bool = False, **kwargs) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path_obj` | `svgelements.Path` | 必填 | **已解析**的路径对象：`se.Path("M 0 0 L 2 0 L 2 2 Z")`； 传 `str` 抛 `AttributeError: 'str' object has no attribute 'approximate_arcs_with_quads'` |
| `long_lines` | `bool` | `False` | 长直线段的拆分方式（样例 `True` 对比） |
| `should_subdivide_sharp_curves` | `bool` | `False` | 尖角处细分（样例 `True`） |
| `should_remove_null_curves` | `bool` | `False` | 移除零长度线段（样例 `True`，路径里特意塞了两个重复点） |

`Text` / `MathTex` 的每个字形叶子就是这类对象（所以它其实一直在被常态渲染）；只有"手头只有 `d` 数据、没有 SVG 文件"时才需要自己构造。

#### 样例：三角形 / `long_lines` / 三个开关 / 从 SVG 文件抄来的 `d`

```python
import os
import sys
import svgelements as se
from PIL import Image
from real_time_manim import (
    Scene, ImageMobject, ImageMobjectFromCamera, SVGMobject, VMobjectFromSVGPath,
    Square, Circle, Triangle, Dot, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene

class SVGPathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("15-VMobjectFromSVGPath", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— path_obj 必须是已解析的 svgelements.Path（直接传字符串会抛错）——
        tri = VMobjectFromSVGPath(se.Path("M 0 0 L 2 0 L 2 2 Z"), color=TEAL).move_to([-4.4, 1.0, 0])   #参数 “path_obj”
        win.play(Create(tri), FadeIn(Text("se.Path(\"M 0 0 L 2 0 L 2 2 Z\")", font_size=18, color=GREY_B).next_to(tri, DOWN, buff=0.25)), run_time=0.6)

        # —— long_lines：长直线段的拆分方式 ——
        curve = VMobjectFromSVGPath(se.Path("M 0 0 C 1 0 2 1 2 2 L 5 2 Z"),
                                    long_lines=True, color=GOLD).move_to([-0.9, 1.0, 0])   #参数 “long_lines”
        win.play(Create(curve), FadeIn(Text("long_lines=True", font_size=18, color=GREY_B).next_to(curve, DOWN, buff=0.25)), run_time=0.6)

        # —— should_subdivide_sharp_curves：尖角处细分 ——
        sharp = VMobjectFromSVGPath(se.Path("M 0 0 L 2 0 L 2 2 L 0 2 Z"),
                                    should_subdivide_sharp_curves=True, color=ORANGE).move_to([2.8, 1.0, 0])   #参数 “should_subdivide_sharp_curves”
        win.play(Create(sharp), FadeIn(Text("should_subdivide_sharp_curves=True", font_size=18, color=GREY_B).next_to(sharp, DOWN, buff=0.25)), run_time=0.6)

        # —— should_remove_null_curves：丢掉零长度线段 ——
        nulls = VMobjectFromSVGPath(se.Path("M 0 0 L 0 0 L 2 0 L 2 0 L 2 2 Z"),
                                    should_remove_null_curves=True, color=PURPLE).move_to([-3.0, -2.0, 0])   #参数 “should_remove_null_curves”
        win.play(Create(nulls), FadeIn(Text("should_remove_null_curves=True", font_size=18, color=GREY_B).next_to(nulls, DOWN, buff=0.25)), run_time=0.6)

        # —— 从 SVG 文件里抄一条 d 也能这样用 ——
        star = VMobjectFromSVGPath(se.Path("M 60 8 L 74 45 L 114 45 L 82 68 L 94 106 L 60 82 L 26 106 L 38 68 L 6 45 L 46 45 Z"),
                                   color=YELLOW).scale(0.02).move_to([1.2, -2.0, 0])
        win.play(Create(star), FadeIn(Text("从 demo_icon.svg 抄来的 d", font_size=18, color=GREY_B).next_to(star, DOWN, buff=0.25)), run_time=0.6)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：把四个 `d` 字符串交给 `se.Path(...)` 解析后再喂给 `VMobjectFromSVGPath`——三角形（最基本用法）、带曲线的路径配 `long_lines=True`、正方形配 `should_subdivide_sharp_curves=True`、带重复点的路径配 `should_remove_null_curves=True`；最后从 `demo_icon.svg` 里抄出星形的 `d`，用同样的方式画出来。

<video src="assets/RTM output/15-图片与SVG-svgpath.mp4" controls width="560"></video>

> 提醒：`long_lines` / `should_subdivide_sharp_curves` / `should_remove_null_curves` 这三个开关的注释里写着"只在 OpenGL 渲染器下生效"——非 OpenGL 路径下传了也**不会报错**，只是形状不变，样例把它们都画出来便于对照。

---

相关：[文本 Text](08-文本Text.md) · [花括号标注](16-花括号标注.md) · [容器与组合](06-容器与组合.md)
