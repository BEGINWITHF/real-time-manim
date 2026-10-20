# RTM 的录制与窗口参数

RTM 没有 `manim` 命令行、也不读 `manim` 的 `config`：**录制**由 `real_time_manim.record` 的两个函数完成（`fast_record_scene` 离线满速 / `record_scene` 实时可见），**窗口与画幅**由 `MLWindow(w, h, hidden)` 决定，**帧率**只支持 60。这页是 RTM 自己的核心参数，逐个出片。

## 参数

### `fast_record_scene(...)`（离线快速录制）

```python
def fast_record_scene(scene, out_path=None, *, fps=60, hidden=True,
                      count_only=False, segment=None, overwrite=True,
                      cleanup=True, verbose=True) -> dict:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `scene` | `Scene` 类 / 实例 / 无参可调用 | —（必填） | 要跑的场景。**能填**：场景类（最常用）、场景实例、任何不收参数的函数（见样例） |
| `out_path` | `str \| None` | `None` → `~/Downloads/output.mp4` | 输出 `.mp4` 的**文件路径**（不是目录模板）；子目录自动创建；一个场景开多个窗口时后续窗口追加 `_partN` |
| `fps` | `int` | `60` | 输出帧率。**只能填 60**：填别的会打印 `[rtm] forcing 60 fps` 然后照渲 60（见样例） |
| `hidden` | `bool` | `True` | **能填** `True`（窗口从不弹出，离线满速）/ `False`（边渲边弹窗） |
| `count_only` | `bool` | `False` | 探测模式：只数帧数，不采集、不做 GPU 渲染、不写文件 |
| `segment` | `tuple \| None` | `None` | `(start_frame, end_frame)` 按帧区间导出 **BMP 目录**（`out_path` 变成目录），而不是一个 MP4 |
| `overwrite` | `bool` | `True` | `False` 时目标文件已存在就抛 `FileExistsError` |
| `cleanup` | `bool` | `True` | 录完删掉 manim 的 `media/` 临时目录；`False` 保留 |
| `verbose` | `bool` | `True` | 打不打每个窗口的进度行 |

**返回**：`dict` —— `{"out_path": ..., "windows": [...], "files": [...], "with_audio": [...]}`，`files` 是磁盘上真实存在的输出（`count_only` 时为空）。

#### 样例：`scene`（类 / 实例 / 无参可调用）

同一个场景用三种传法各录一段：传类（RTM 自己建实例、跑 `setup()`+`construct()`）、传实例、传一个不收参数的函数。

```python
import sys

from real_time_manim import Scene, Square, Text, BLUE, YELLOW, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene, record_scene

class SceneFormDemo(Scene):
    TAG = "scene = class"   #传法标签：类 / 实例 / 无参可调用

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        label = Text(self.TAG, font_size=40, color=YELLOW).to_edge(UP)   #上屏显示当前的传法
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   #蓝色方块
        self.add(label)   #把标签放进场景
        win.play(Create(sq), run_time=0.8)   #画出方块
        win.play(sq.animate.scale(1.2), run_time=0.6)   #方块放大
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


class SceneFormInstance(SceneFormDemo):
    TAG = "scene = instance"   #同一个场景，改成实例形态


class SceneFormCallable(SceneFormDemo):
    TAG = "scene = callable"   #同一个场景，改成无参可调用形态


def run_callable():
    SceneFormCallable().construct()   #无参可调用形态：一个不收参数的函数，把场景跑完


if __name__ == "__main__" and ("scene_forms" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(SceneFormDemo, out_path="scene_class.mp4", verbose=True)   #类：最常用的形态
    fast_record_scene(SceneFormInstance(), out_path="scene_instance.mp4", verbose=True)   #实例：自己先建好再传
    fast_record_scene(run_callable, out_path="scene_callable.mp4", verbose=True)   #无参可调用：流程完全自己写
```

这段代码在做什么：三个子类只是把标签换成了 `scene = class` / `scene = instance` / `scene = callable`，场景内容一模一样；然后用三条 `fast_record_scene` 调用分别以**类、实例、无参可调用**三种形态录制，出来的三段画面对应视频里的三格。传类时 RTM 会替你建实例并跑 `setup()`+`construct()`；传实例就跑你给的那个；传函数则只调用它，跑什么全由函数自己写（样例里就是 `SceneFormCallable().construct()`）。

<video src="assets/RTM output/05-RTM的录制与窗口参数-scene_forms.mp4" controls width="560"></video>

> 提醒：传无参可调用时 RTM **不会**替你调 `setup()`——如果你的场景依赖 `setup()`（比如 `MovingCameraScene` 的取景框是在 `setup()` 里建的），要么传类/实例，要么在函数里自己调。日常一律传类就好。

#### 样例：`out_path`（输出路径）

`out_path` 就是「文件落在哪」：直接给文件路径，不存在的子目录自动创建，不走 `media_dir` 那套目录模板。

```python
import sys

from real_time_manim import Scene, Square, Text, BLUE, YELLOW, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene, record_scene

class OutPathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        label = Text("out_path = clips/demo.mp4", font_size=38,
                     color=YELLOW).to_edge(UP)   #上屏显示输出路径
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   #蓝色方块
        self.add(label)   #把标签放进场景
        win.play(Create(sq), run_time=0.8)   #画出方块
        win.play(sq.animate.scale(1.2), run_time=0.6)   #方块放大
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


if __name__ == "__main__" and ("out_path" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(OutPathDemo, out_path="clips/demo.mp4", verbose=True)   #out_path 直接给文件路径，子目录自动创建
```

这段代码在做什么：场景内容和上一个样例一样，只是调用里 `out_path="clips/demo.mp4"` ——输出直接落到 `clips/` 子目录下的 `demo.mp4`，`clips/` 不存在会自动建。页面里嵌的这条视频就是这个文件本身（最终按命名规范发布为 `assets/RTM output/05-RTM的录制与窗口参数-out_path.mp4`）。

<video src="assets/RTM output/05-RTM的录制与窗口参数-out_path.mp4" controls width="560"></video>

> 提醒：不传 `out_path` 时默认写到 `~/Downloads/output.mp4`，一不小心就把桌面下载目录塞满了——建议每次都显式给路径。多窗口场景第二个窗口会写 `xxx_part2.mp4`，别和自己给的文件名打架。

#### 样例：`fps`（帧率，只能 60）

同一个场景分别请求 `fps=30` 和 `fps=60` 各录一段：请求 30 会被强制纠正成 60 并打印提示，两段的帧数、时长完全一样。

```python
import sys

from real_time_manim import Scene, Square, Text, BLUE, YELLOW, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene, record_scene

class FpsDemo(Scene):
    FPS = 30   #请求的帧率：改成 60 就不触发强制纠正

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        label = Text("fps = %d" % self.FPS, font_size=40, color=YELLOW).to_edge(UP)   #上屏显示请求的帧率
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   #蓝色方块
        self.add(label)   #把标签放进场景
        win.play(Create(sq), run_time=0.8)   #画出方块
        win.play(sq.animate.scale(1.2), run_time=0.6)   #方块放大
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


class FpsDemo60(FpsDemo):
    FPS = 60   #同一个场景，请求 60 fps


if __name__ == "__main__" and ("fps" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(FpsDemo, out_path="fps_30.mp4", fps=30, verbose=True)   #fps=30：打印 “[rtm] forcing 60 fps” 后照渲
    fast_record_scene(FpsDemo60, out_path="fps_60.mp4", fps=60, verbose=True)   #fps=60：不触发提示
```

这段代码在做什么：两段的唯一区别是调用里的 `fps=30` / `fps=60`（场景里只是把数字打到标签上）。`fps=30` 那次控制台会打印 `[rtm] forcing 60 fps: RTM supports high quality only (asked for 30)`，然后照样按 60fps 出片——所以视频里两段各 114 帧、1.90s，逐帧对齐，只有标签文字不同。

<video src="assets/RTM output/05-RTM的录制与窗口参数-fps.mp4" controls width="560"></video>

> 提醒：想要 30fps 的成片，先按 60fps 渲，再 `ffmpeg -i in.mp4 -r 30 out.mp4` 转——直接填 `fps=30` 只会得到一行提示。`MLWindow` 的 `w`/`h` 同理：任何非 1920×1080 的请求都被强制纠正（下一小节有实拍）。

#### 样例：`count_only` / `segment` / `overwrite` / `cleanup` / `verbose`（不出片）

这五个参数改的是「录不录、录到哪、覆盖不覆盖、留不留临时目录、说不说话」，画面内容一模一样（甚至不产视频），所以只给代码和实测输出，不贴视频。下面这段探针在 demo 脚本里，跑 `python 05-RTM的录制与窗口参数.py probes` 可复现：

```python
if __name__ == "__main__" and "probes" in sys.argv[1:]:
    result = fast_record_scene(FpsDemo, out_path="probe_count.mp4", count_only=True, verbose=True)   #count_only：只数帧，不采集也不写文件
    print("count_only 的返回值：", result)   #out_path 照常返回，但磁盘上没有这个文件
    fast_record_scene(FpsDemo, out_path="probe_bmp", segment=(0, 30), verbose=True)   #segment：按帧区间导出 BMP 目录，不是 MP4
    fast_record_scene(FpsDemo, out_path="probe_clean.mp4", cleanup=False, verbose=True)   #cleanup=False：保留 manim 的 media/ 目录
    try:
        fast_record_scene(FpsDemo, out_path="probe_clean.mp4", overwrite=False, verbose=True)   #overwrite=False：目标已存在就报错
    except FileExistsError as exc:
        print("overwrite=False 的报错：", exc)   #FileExistsError：target already exists
    fast_record_scene(FpsDemo, out_path="probe_quiet.mp4", verbose=False)   #verbose=False：不打进度行
```

实测输出（依次）：

| 参数 | 实测行为 |
| --- | --- |
| `count_only=True` | 打印 `[FastRecord] Count: 114 frames`，不写任何文件；返回值的 `files` 是空列表 |
| `segment=(0, 30)` | 打印 `[FastRecord] BMP mode (0, 30)` 和 `[FastRecord] BMP: 30 frames in ...`，目录里是 `frame_000000.bmp` ~ `frame_000029.bmp` |
| `cleanup=False` | 那次运行后 manim 的 `media/` 目录保留在原地（默认会被整目录删掉） |
| `overwrite=False` | 目标已存在时抛 `FileExistsError: target already exists: ... (pass overwrite=True to replace it)` |
| `verbose=False` | 不打 `[record] window #1 -> ...` / `[FastRecord] ...` 这些进度行 |

> 提醒：`segment` 导出的是**BMP 序列**（未压缩，很占盘），拿它对接逐帧工具链；只想知道「这段动画有多少帧」就用 `count_only=True`，最快。`overwrite=False` 的保护只看文件存不存在，不比内容——批量脚本里很适合用来防覆盖。

### `record_scene(...)`（实时可见窗口录制）

```python
def record_scene(scene, out_path=None, *, fps=60, overwrite=True,
                 cleanup=True, verbose=True) -> dict:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `scene` | `Scene` 类 / 实例 / 无参可调用 | —（必填） | 要跑的场景，三种形态同 `fast_record_scene` |
| `out_path` | `str \| None` | `None` → `~/Downloads/output.mp4` | 输出 `.mp4` 文件路径，同上 |
| `fps` | `int` | `60` | 采集帧率（后台线程按它抓窗口）；同样只支持 60 |
| `overwrite` | `bool` | `True` | 同 `fast_record_scene` |
| `cleanup` | `bool` | `True` | 同 `fast_record_scene` |
| `verbose` | `bool` | `True` | 同 `fast_record_scene` |

和 `fast_record_scene` 的区别只有一条：**窗口必须可见**，动画按真实时间播放，后台线程边看边抓屏（底层是 `win.start_record(...)` … `win.stop_record()`）。适合「渲染的同时给人看」的场合；批量出片用 `fast_record_scene` 快得多。

#### 样例：`record_scene`

同一个动画走实时录制：弹出可见窗口、按墙钟播完、后台抓屏合成 mp4。

```python
import sys

from real_time_manim import Scene, Square, Text, BLUE, YELLOW, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene, record_scene

class RecordSceneDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        label = Text("record_scene = live window", font_size=38,
                     color=YELLOW).to_edge(UP)   #实时录制：窗口可见
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   #蓝色方块
        self.add(label)   #把标签放进场景
        win.play(Create(sq), run_time=0.8)   #画出方块
        win.play(sq.animate.scale(1.2), run_time=0.6)   #方块放大
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


if __name__ == "__main__" and ("record_scene" in sys.argv[1:] or not sys.argv[1:]):
    record_scene(RecordSceneDemo, out_path="record_scene.mp4", fps=60, verbose=True)   #实时可见窗口录制：弹窗、按真实时间跑
```

这段代码在做什么：场景内容和前面一样（标签换成 `record_scene = live window`），但录制走的是 `record_scene`——你会看到窗口真的弹出来把动画播完，控制台打印 `[Record] Recording to ... at 60 fps`，收尾时报告 `Captured N frames in X.Xs (... fps), encoding ...`。输出视频的时间和真实播放一致。

<video src="assets/RTM output/05-RTM的录制与窗口参数-record_scene.mp4" controls width="560"></video>

> 提醒：实时录制的**帧数不保证和离线渲染对齐**——它按墙钟走（含窗口启动/收尾时间），抓屏速度还受机器性能限制（本机实测约 6.5 帧/秒抓屏，成片按实际时长重排到 60fps，画面略卡但节奏正确：130 帧 / 2.17s，对比离线的 114 帧 / 1.90s）。要帧级可复现的输出，用 `fast_record_scene`。

### `MLWindow(w, h, hidden)`（窗口与画幅）

```python
def __init__(self, w=1920, h=1080, hidden=None):
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `w` | `int` | `1920` | 窗口/帧缓冲宽度 = RTM 的「分辨率」。**只能填 1920**：传别的打印 `[rtm] forcing 1920x1080` 后强制纠正 |
| `h` | `int` | `1080` | 窗口/帧缓冲高度，同上 |
| `hidden` | `bool \| None` | `None` → 跟随类属性 `_hidden_default` | **能填** `True`（构建为隐藏窗口）/ `False` / `None`（跟随默认）。一般不直接传：`fast_record_scene(hidden=...)` 已经替你设好 |

**强制规格**：画幅只支持 `1920×1080`（`MLWindow.SUPPORTED_WIDTH/HEIGHT`），帧率只支持 `60`（`SUPPORTED_FPS`）。传别的值不报错，而是强制纠正并打印提示——所以 `MLWindow(960, 540)` 打印 `[rtm] forcing 1920x1080` 是**正常现象**，不用改。窗口建好后 `win.scene = self` 把 manim 场景绑上去，`win.play(...)` 驱动播放，`win.close()` 收尾（**经录制助手包装**时顺带结束编码：`record._AutoRecord` 会在真正的 `MLWindow.close()` 之前先跑 `_finish_fast_record()` / `stop_record()`，见本页 `enable_fast_record` 小节）。

#### 样例：`w` / `h` / `hidden`（一组强相关参数）

两段各请求一组不同的窗口参数（960×540 隐藏 / 3840×2160 可见），输出画面逐帧相同——尺寸请求被强制纠正、显隐只影响桌面弹不弹窗。

```python
import sys

from real_time_manim import Scene, Square, Text, BLUE, YELLOW, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene, record_scene

class MLWindowDemo(Scene):
    SIZE = "MLWindow(960, 540)  hidden=True"   #窗口参数：尺寸 + 是否隐藏
    W, H = 960, 540   #窗口尺寸：改别的值会被强制纠正成 1920x1080

    def construct(self):
        win = MLWindow(self.W, self.H)   #创建一个 RTM 窗口：“w” / “h” 就是这两个参数
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        label = Text(self.SIZE, font_size=38, color=YELLOW).to_edge(UP)   #上屏显示这组窗口参数
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   #蓝色方块
        self.add(label)   #把标签放进场景
        win.play(Create(sq), run_time=0.8)   #画出方块
        win.play(sq.animate.scale(1.2), run_time=0.6)   #方块放大
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


class MLWindowBig(MLWindowDemo):
    SIZE = "MLWindow(3840, 2160)  hidden=False"   #请求 4K + 可见窗口：照样被纠正成 1920x1080
    W, H = 3840, 2160   #4K 尺寸：只用来触发强制纠正提示


if __name__ == "__main__" and ("mlwindow" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(MLWindowDemo, out_path="mlwin_small.mp4", hidden=True, verbose=True)   #hidden=True：窗口从不弹出
    fast_record_scene(MLWindowBig, out_path="mlwin_big.mp4", hidden=False, verbose=True)   #hidden=False：边渲边弹窗
```

这段代码在做什么：`MLWindowDemo` 把 `MLWindow(960, 540)` 的请求打在标签上、`MLWindowBig` 请求 `MLWindow(3840, 2160)`，两次录制一次 `hidden=True`（不弹窗）一次 `hidden=False`（会弹窗）。控制台各打一行强制纠正提示，视频里两段除了标签文字完全一样：请求 540p 得到的是 1080p，请求 4K 得到的还是 1080p，弹不弹窗不影响画面。

<video src="assets/RTM output/05-RTM的录制与窗口参数-mlwindow.mp4" controls width="560"></video>

> 提醒：别再琢磨调分辨率了——RTM 只有 1920×1080@60 这一种输出（源码里写死 `SUPPORTED_WIDTH/HEIGHT/FPS`，理由是小窗口会把分辨率相关 bug 藏起来）。想要低清就渲完用 ffmpeg 缩。`hidden=False` 时窗口会抢焦点，录完自动关。

### `MLWindow.enable_fast_record(...)`（录制的底层入口）

```python
def enable_fast_record(self, path, fps=60, segment=None, hidden=True, count_only=False):
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `path` | `str` | —（必填） | MP4 输出路径（管道模式），或 `segment` 模式下的 BMP 帧目录 |
| `fps` | `int` | `60` | 帧率；非 60 被强制成 `SUPPORTED_FPS` 并打印提示 |
| `segment` | `tuple \| None` | `None` | `(start_frame, end_frame)` → BMP 目录模式 |
| `hidden` | `bool` | `True` | 隐藏窗口（win32 下 `ShowWindow(SW_HIDE)`） |
| `count_only` | `bool` | `False` | 只数帧：不采集、不做 GPU 渲染 |

`fast_record_scene` 内部就是创建 `MLWindow` 后调它；**编码收尾由 `fast_record_scene` / `record_scene` 安装的 `record._AutoRecord` 包装的 `close` 先调 `_finish_fast_record()`（或 `stop_record()`），再执行真正的 `MLWindow.close()`**（`record.py:181-186`、`window/recording.py:217-221`）。日常用 `fast_record_scene` 即可，需要直接控制窗口时才用这一层。实时录像对应的底层是 `win.start_record(path, fps=60)` … `win.stop_record()`（`record_scene` 用的就是这对）。

本小节不出片：它的每个参数都和 `fast_record_scene` 同名同义，画面效果见上面的对应样例。

> 提醒：直接用这一层要自己负责收尾——`MLWindow.close()` 本身**不做录制编码收尾**，**直接手调 `enable_fast_record(...)` + `win.close()` 不会收尾**，必须自己调 `win._finish_fast_record()`；忘调它（走 `fast_record_scene` 时即忘调 `win.close()`）ffmpeg 管道就不关，视频不完整/不存在。另外 `segment` 模式写出的 BMP 文件名是 `frame_000000.bmp` 起步，自己按需排序。

**总结**：出片三件事——场景传给 `fast_record_scene`（或要可见窗口就 `record_scene`），文件给 `out_path`，画幅认 `MLWindow` 的 1920×1080；帧率只有 60，其余 `config`/命令行的习惯一律改掉。背景色是唯一接线的 config 键，见 [01-画质与输出](01-画质与输出.md)。

出片情况：`scene_forms` 342 帧 / 5.70s、`out_path` 114 帧 / 1.90s、`fps` 228 帧 / 3.80s、`mlwindow` 228 帧 / 3.80s 逐帧对齐；`record_scene` 130 帧 / 2.17s。

---

相关：[01-画质与输出](01-画质与输出.md) ｜ [03-路径与窗口](03-路径与窗口.md) ｜ [04-ManimCE 命令行速查](04-ManimCE命令行速查.md)
