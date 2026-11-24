# ManimGL 用户指南

如果你以前用 **ManimGL**（3b1b 的 `manimgl` 交互式版本）写过动画，本页把它的各个函数在 real-time-manim 里对应成什么。RTM 和 manimGL 一样是**实时渲染引擎**（manimGL 用 OpenGL，RTM 用 Vulkan，快 1.8–2.8 倍），但互动方式完全不同：RTM **没有 `manimgl` 命令行、没有中途 `embed`、没有改代码自动重载**，交互换成「帧预览窗口」。

## 函数对照表

| ManimGL 写法 | RTM 写法 | 说明 |
| --- | --- | --- |
| `manimgl scene.py`（弹窗口播动画） | 脚本直接跑 `construct`，或 `FramePreview(S).run()` | RTM 的窗口由 `MLWindow` 在 `construct` 里创建 |
| `manimgl scene.py -w`（写视频） | `fast_record_scene(S, out_path="out.mp4")` | 离线快速出片，帧级精确 |
| `manimgl scene.py -w -o`（写完自动打开） | 出片后自己打开 mp4 | 没有自动打开 |
| `-l / -m / -h` 画质档 | 无 | 只有 1920×1080@60 一档 |
| `self.embed()`（中途掉进 Python REPL） | 无 | 想要「停在某一帧」用 `FramePreview` 跳帧 |
| `self.wait()` 弹出输入框 | `FramePreview` 的 `p`（播放）/ `s`（存 PNG）/ `q`（退出） | 没有场景内的输入框 |
| `self.wait(stop_condition=...)` | `win.play(Wait(..., stop_condition=...))` | 保留；但只在正向播放时生效（跳帧时不安全） |
| 改代码自动重载（live edit） | 无 | 改完重跑脚本 |
| `%%manim -w` IPython magic | 无 | 在脚本里跑，不用 magic |
| `config.renderer = "opengl"` | 无 | RTM 固定 Vulkan，没得选 |
| `-s, --skip_animations`（跳到结尾） | `FrameServer.save_frame(fs.duration, path)` | 任意帧 O(1) 直达，含最后一帧 |
| `gui` 面板（pyqt 控件） | 无 | 控制条只有帧预览那一条（输入框 / 滑块） |
| `self.add_sound(...)` | 同名 | 可用；`gain` 单位是 **dB** |
| `from manimlib import *` | `from real_time_manim import *` | RTM 的命名空间是 **ManimCE 0.21.0**，不是 manimGL 的 `manimlib`——类名/动画名大多相同，个别细节以 CE 为准 |

## 最小场景形状

manimGL 里 `construct` 直接写 `self.play(...)`，RTM 里多一个窗口对象：

```python
from real_time_manim import *
from real_time_manim.record import fast_record_scene

class MyScene(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口（尺寸会被强制成 1920×1080）
        win.scene = self   #把场景绑定给窗口（必须）
        circle = Circle(color=YELLOW).set_fill(YELLOW, 0.5)
        win.play(FadeIn(circle), run_time=1.0)   #淡入一个圆，时长1秒
        win.play(circle.animate.shift(RIGHT * 3), run_time=1.0)   #圆向右移
        win.play(Wait(0.5))   #等待0.5秒
        win.close()   #关闭窗口（必须，否则视频不落盘）

fast_record_scene(MyScene, "my_scene.mp4")#导出到项目目录下的 my_scene.mp4
```

和 manimGL 一样，动画是 `alpha`（时间）的纯函数，所以任意帧都能立刻算出来——只是入口从「改代码重载 + `embed`」变成了 [帧预览](03-三种录制方法.md) 的跳帧。

## 错误对照

| 你做了什么 | 会看到 | 修法 |
| --- | --- | --- |
| 先 `import manimlib` 或 `import manim` 再 `import real_time_manim` | `RuntimeWarning`（类身份来自外部拷贝） | 永远先导入 `real_time_manim` |
| 用了 `self.embed()` / `interactive_embed` | 属性不存在 | 用 `FramePreview` 找帧 |
| 忘了 `win.scene = self` | `RuntimeError: win.play() called before the scene was bound...` | 在 `construct` 里绑定 |
| 忘了 `win.close()` | 输出文件为空/不完整 | 结尾调 `win.close()` |
| 传了裸 Mobject 给 `play` | `TypeError: Unexpected argument ... passed to MLWindow.play()` | 用 `FadeIn`/`Create` 包一层，或先 `self.add(...)` |
| 用 manimGL 的 `manimlib` 专用类 | 导入不到或行为不同 | 按 ManimCE 0.21.0 的类名写（RTM 的命名空间就是它） |

---

相关：[快速开始](02-快速开始.md) ｜ [三种录制方法](03-三种录制方法.md) ｜ [ManimCE 用户指南](04-manimCE用户指南.md)
