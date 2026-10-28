# 实时窗口 MLWindow

`MLWindow(w, h)` 打开一个实时 Vulkan 渲染窗口；绑定场景后用 `win.play(...)` 驱动整段动画，最后 `win.close()` 收尾。

限制：每个进程同一时刻只支持一个窗口（限制来自原生 DLL；Python 侧靠 `_registry` 顺序开关）

## 参数

### `MLWindow.__init__`

```python
def __init__(self, w=1920, h=1080, hidden=None):
```

| 参数       | 类型             | 默认值                           | 说明                              |
| -------- | -------------- | ----------------------------- | ------------------------------- |
| `w`      | `int`          | `1920`（强制）                    | 窗口宽度（像素）；非 1920×1080 会被强制纠正（见下） |
| `h`      | `int`          | `1080` （强制）                   | 窗口高度（像素）；同上                     |
| `hidden` | `bool \| None` | `None`（取类级 `_hidden_default`） | 为 `True` 时窗口构建后从不显示（离线录制用）      |

> **强制规格**：
>
> - `MLWindow` 目前**只支持 `1920×1080`**（类属性 `SUPPORTED_WIDTH` / `SUPPORTED_HEIGHT`）。
> - 录制帧率只**支持 `60`**（`SUPPORTED_FPS`）。
> - 传别的值不会报错，而是被**强制纠正**并打印一行 `[rtm] forcing 1920x1080: ...`。所以上面写 `MLWindow(960, 540)` 与 `MLWindow()` 实际渲染出的都是 1080p。
>
> **任何非 1920×1080 的尺寸都会被强制成 1080p60 并打印 `[rtm] forcing`，属正常**。*其他尺寸未来可能会提供支持。*

### `win.scene`（属性）

| 参数      | 类型      | 默认值    | 说明                                                     |
| ------- | ------- | ------ | ------------------------------------------------------ |
| `scene` | `Scene` | `None` | 绑定的 Manim 场景；必须先赋值 `win.scene = self`，否则 `play()` 直接返回 |

### `MLWindow.play`

```python
def play(self, *animations, **kwargs):
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `*animations` | `Animation \| Mobject \| _AnimationBuilder` | — | 要播放的动画（可多个），`.animate...` 构造器会被自动解析 |
| `**kwargs` | `Any` | — | **生效的是 `run_time` / `rate_func`**（分别覆盖每个动画的时长/速率曲线）**加上 `path_arc` / `path_arc_axis` / `path_arc_centers` / `path_func`**（2026-10-17 起转发到动画实例，`Transform.path_arc` 的 setter 会重建 `path_func`）；`subcaption` / `subcaption_duration` / `subcaption_offset` 另有专门形参；**其余关键字打印具名警告**（`[RTM] play(): unsupported keyword(s) ... ignored`），不再静默（`window/play.py`、`window/play.py::SUPPORTED_PLAY_KWARGS`） |

### `MLWindow.close`

```python
def close(self):
```

无参数。关闭窗口、结束渲染（`_unregister()` + `Vulkan_Shutdown()`）。

**录制的编码收尾不在 `MLWindow.close` 里**：它由 `fast_record_scene` / `record_scene` 安装的 `record._AutoRecord` 在调用 `close()` 前先执行 `_finish_fast_record()` / `stop_record()`（`record.py:181-186`、`window/recording.py:217-221`）。直接手调 `enable_fast_record(...)` + `win.close()` 不会收尾，必须自己调 `win.finish_record()`。

### `MLWindow.set_mesh` / `MLWindow.clear_mesh`

```python
def set_mesh(self, mesh): ...
def clear_mesh(self): ...
```

`set_mesh(mesh)` 把一个 `MeshBatch` 交给窗口，每帧在 painter 图元之前提交，用 GPU 深度缓冲解决 3D 自遮挡。`set_mesh(None)` 或 `clear_mesh()` 摘掉。

```python
mesh = MeshBatch()
mesh.append(quads, colors)     # (Q, 4, 3) 世界坐标 + (Q, 4, 4) RGBA
win.set_mesh(mesh)
```

面片格式、限制和完整示例见[三维表面 · 深度网格](../06-三维/02-三维表面.md)。

### 首次编译公式的等待提示

首次渲染 LaTeX / Typst 公式要调用编译器，可能卡住一两秒。这时若已有**可见**窗口，RTM 会弹出一个置顶小窗，明确告诉你在等编译、不是卡住：

- **只在有可见窗口时出现**：`fast_record_scene` / `FrameServer` 用隐藏窗口，不会弹；
- **只在编译慢时出现**：有缓存时约 30ms 就编译完，弹窗来不及出现就被取消；
- 带实时「已等待 N.Ns」计数与跑马灯进度条，一眼看出没死；
- 文案跟随 **Windows 显示语言（用户 UI 语言）**：中文 / English / 日本語 / 한국어，其它语言回退英文。

| 环境变量 | 默认 | 作用 |
| --- | --- | --- |
| `RTM_WAIT_POPUP` | `1` | 设 `0` 完全关闭弹窗 |
| `RTM_WAIT_POPUP_DELAY` | `0.35` | 编译超过多少秒才弹 |
| `RTM_LANG` | 自动 | 强制弹窗语言：`zh` / `en` / `ja` / `ko` |
| `RTM_WAIT_ICON` | 内置沙漏图标 | 换弹窗图标（给 `.ico` 路径） |

> 提醒：弹窗只是「告知」，**不影响编译结果**（`fast_record_scene` 的成片与有没有弹窗逐字节相同）。想彻底不等待就先预热缓存（`save_tex_cache` / `restore_tex_cache`，仓库 `run.py` 就是这么做的），或先空跑一次；要反过来强制重编 / 清空间，用 `clear_tex_cache()`——它同时清 `<media>/Tex` 和持久缓存 `tex_cache/`，返回删除的文件数（`dry_run=True` 只预览，`only_ext=(".svg",)` 只清 SVG）。

## 示例

RTM 最小程序模板：

```python
from real_time_manim import Scene, Square, BLUE
from real_time_manim.vulkan_bind import MLWindow, Create, Wait

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)   #创建一个 “Square” Mobject，名为 “sq”
        win.play(Create(sq), run_time=1.0)   #对 “sq” 使用 “Creat” 动画，动画用 1s 完成
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口
```

## 视频样例（RTM 渲染结果）
TODO：第一个场景的产物直接拿过来

## 低层方法（高级）

这些方法面向录制、预览和自定义帧循环。普通场景用 `win.play(...)` + `win.close()` 就够，不需要直接调。

| 方法 | 说明 |
| --- | --- |
| `win.screenshot(path)` | 把当前帧存成图片；`path` 为 `str` 或 `bytes`；隐藏窗口也可用；返回原生结果（非 0 表示写入成功） |
| `win.request_readback()` | 安排下一帧回读；必须在绘制该帧的 `tick()` 之前调用 |
| `win.tick()` | 推进一帧；窗口关闭返回 `False`；同时更新 `win_w` / `win_h` |
| `win.set_visible(visible=True)` | 显示或隐藏窗口 |
| `win.hwnd` | 只读属性；Win32 窗口句柄，非 Windows 或未初始化时为 `None` |
| `win.start_record(path="output.mp4", fps=60)` | 开始实时录制（后台线程编码） |
| `win.stop_record()` | 结束实时录制并收尾 |
| `win.finish_record()` | 结束手动 `enable_fast_record()` 的快速录制；`fast_record_scene` 会自动调用，手调时在 `close()` 前调用 |
| `win.build_timeline()` | 把 schedule 模式记录的动画列表构建成 `Timeline` |
| `win.sync(scene, angle=0.0)` | 每帧把 `scene` 同步到窗口；播放/录制循环内部使用，一般不用手调 |

> 提醒：`start_record` / `stop_record` 是实时录制；`enable_fast_record` + `finish_record` 是离线快速录制。两者不要和 `fast_record_scene` 的自动收尾混用。

相关：[第一个场景](02-第一个场景.md) · [录制视频](04-录制视频.md) · [Scene 基础](../01-场景与相机/场景/01-Scene基础.md)
