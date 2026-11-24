# ManimCE 用户指南

如果你以前用 **ManimCE**（`manim` 命令行）写过动画，本页把每个函数在 real-time-manim 里对应成什么。**RTM 没有 `manim` 命令、没有命令行旗标、也不读 `manim.cfg`。**
## 最快迁移（三步）

1. 导入从 `from manim import ...` 改成 `from real_time_manim import ...`（RTM 自带整套 ManimCE 0.21.0，形状、颜色、动画的用法**完全一样**）；
2. 每个 `construct` 开头加两行：`win = MLWindow(960, 540)` 和 `win.scene = self`，结尾加 `win.close()`；
3. 命令行出片换成 `fast_record_scene(Scene名, out_path="xxx.mp4")`。

## 函数对照表

| ManimCE 写法 | RTM 写法 | 说明 |
| --- | --- | --- |
| `manim -qh scene.py Hello` | `fast_record_scene(Hello, out_path="out.mp4")` | 命令行整个不存在；出片靠函数 |
| `from manim import *` | `from real_time_manim import *` | 同一个命名空间（RTM 自带 ManimCE） |
| `self.play(...)` | `win.play(...)` | RTM 的播放统一走窗口；`self.play` 在窗口绑定后也能用，场景内部会调 `self.play` 的方法（如 `move_camera`）要先写 `self.play = win.play` |
| `self.wait(1)` | `win.play(Wait(1))` | `Wait` 从 `real_time_manim.vulkan_bind` 导入（顶级 `from real_time_manim import *` 也有） |
| `-ql / -qm / -qh / -qp / -qk` | 无 | 画质只有 1920×1080@60 一档，其它请求强制纠正并打印 `[rtm] forcing ...` |
| `--fps 30` | 无 | 帧率只有 60 |
| `-o 名称` | `out_path="xxx.mp4"` | 直接给带 `.mp4` 的文件路径 |
| `--format png` / `-s`（存最后一帧） | `FrameServer.save_frame(t, path)` / `segment=(a, b)` | 任意帧 O(1) 存 PNG；区间导出 BMP 目录 |
| `--save_sections` / `next_section` | 无（不产任何文件） | 拆成多个场景分别录，或用 ffmpeg 切 |
| `--renderer cairo/opengl` | 无 | RTM 固定 Vulkan，没得选 |
| `-a, --write_all` | 自己逐个调用 | `fast_record_scene(A); fast_record_scene(B)` |
| `--dry_run` | `count_only=True` | 只数帧数，不采集不写文件 |
| `-t, --transparent` | 无 | 输出永远不透明（黑底） |
| `manim.cfg` | 基本不读 | 只有 `background_color`（背景色，能改，见 [画质与输出](../01-场景与相机/配置/01-画质与输出.md)）、`seed`、tex 路径等少数键有意义 |
| `Scene.render()` / file_writer | 不存在 | RTM 自己跑 `setup() → construct() → tear_down()` |
| `MathTex(...)` | 同名 | 装了 typst 就走 Typst 编译，**不用装 LaTeX**；没装则回落到 LaTeX |
| `Tex(...)` | 同名 | 恒需要 LaTeX |
| `--enable_gui` / `-p --preview` | `FramePreview(S).run()` / `hidden=False` | 交互预览换成了帧预览窗口 |
| `self.add_sound(...)` | 同名 | 可用；`gain` 单位是 **dB** 不是倍数 |
| `%%manim` Jupyter magic | 无 | 在脚本里跑，不用 magic |

全部旗标的逐条速查见 [ManimCE命令行速查](../01-场景与相机/配置/04-ManimCE命令行速查.md)。

## 最小场景形状

```python
from real_time_manim import *
from real_time_manim.record import fast_record_scene

class MyScene(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口（尺寸会被强制成 1920×1080）
        win.scene = self   #把场景绑定给窗口（必须）
        sq = Square(color=BLUE).set_fill(BLUE, 0.5)
        win.play(Create(sq), run_time=1.0)   #画出方块，时长1秒
        win.play(sq.animate.scale(1.5), run_time=1.0)   #方块放大
        win.play(Wait(0.5))   #等待0.5秒
        win.close()   #关闭窗口（必须，否则视频不落盘）

fast_record_scene(MyScene, "my_scene.mp4")#导出到项目目录下的 my_scene.mp4
```

注意两条硬规矩：`win.scene = self` 不写，`play` 直接报错；`win.close()` 不写，视频编码不结束、文件可能为空。

## 错误对照

| 你做了什么 | 会看到 | 修法 |
| --- | --- | --- |
| 先 `import manim` 再 `import real_time_manim` | `RuntimeWarning`（类身份来自外部 manim） | 永远先导入 `real_time_manim` |
| 传了裸 Mobject 给 `play` | `TypeError: Unexpected argument ... passed to MLWindow.play()` | 用 `FadeIn`/`Create`/`Write` 包一层，或先 `self.add(...)` |
| 忘了 `win.scene = self` | `RuntimeError: win.play() called before the scene was bound...` | 在 `construct` 里绑定 |
| 忘了 `win.close()` | 输出文件为空/不完整 | 结尾调 `win.close()` |
| `play` 里塞了不认识的参数 | 打印警告 `unsupported keyword(s) ... ignored` | 只传 `run_time`/`rate_func`，其余交给动画构造函数 |
| 用 `next_section` 想分段 | 什么都不出 | 拆场景或 ffmpeg 切 |
| 调 `Scene.render()` | 无人调用，无产物 | 用 `fast_record_scene` / `record_scene` |
| `MathTex` 报 `latex error converting to dvi` | 没装 LaTeX 且 typst 路由失败 | 装 `real-time-manim[typst]`，或检查公式转义（写成 raw string） |

---

相关：[快速开始](02-快速开始.md) ｜ [ManimCE命令行速查](../01-场景与相机/配置/04-ManimCE命令行速查.md) ｜ [RTM的录制与窗口参数](../01-场景与相机/配置/05-RTM的录制与窗口参数.md)
