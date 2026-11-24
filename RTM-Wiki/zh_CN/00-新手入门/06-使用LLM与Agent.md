# 使用 LLM 与 Agent

real-time-manim 是个年轻的项目，通用大模型（ChatGPT、Claude、通义……）的训练数据里几乎没有它——但 RTM 本身是 **ManimCE 的数据模型 + Vulkan 窗口**，所以一个会写 ManimCE 的模型已经会了九成，缺的只是 RTM 这层壳。这一页教你把这层壳喂给模型：给对上下文，它写出的 RTM 代码大概率一次能跑。

## 1. 你的模型会什么、不会什么

| 它本来就会 | 它不会（RTM 特有） |
| --- | --- |
| ManimCE 全部类、动画、颜色（RTM 内置 ManimCE 0.21.0，命名空间完全相同） | `MLWindow`、`win.play`、`win.scene`、`win.close` 这套窗口层 |
| 写 Python、读 traceback | RTM **没有 manim 命令行**，出片靠 `fast_record_scene` |
| 通用 Manim 教程里的一切 | 固定 1920×1080@60、Vulkan、typst 路由等 RTM 规则 |

结论：**别让它重学 ManimCE，只补 RTM 这层**。下面就是这层。

## 2. 把这段上下文粘给它

任何模型（网页聊天、Claude Code、Codex 都行），开工前先把这段粘进去。建议用英文粘——写给 agent 的参考文档也是英文：

```text
You are writing real-time-manim (RTM) code. RTM is a Vulkan real-time rendering
backend for ManimCE: it bundles ManimCE 0.21.0 and re-exports the whole namespace,
so every ManimCE class/animation works — but the driving layer is different.

Hard facts (do not contradict these):
- Import name: real_time_manim (underscores). Never write real-time-manim (the
  pip package name, hyphens) in an import. Always import real_time_manim first.
- There is NO manim CLI. Render from Python:
    fast_record_scene(SceneClass, "out.mp4")   # offline, no window, frame-exact
    record_scene(SceneClass, "out.mp4")        # visible window, wall-clock
- Every scene must create an MLWindow inside construct():
    win = MLWindow(960, 540)   # size is force-corrected to 1920x1080
    win.scene = self           # REQUIRED binding
    win.play(...)              # playback goes through the window, not self.play
    win.close()                # REQUIRED, or nothing is flushed
- Output is fixed at 1920x1080 @ 60 fps: no -ql/-qm quality flags, no --fps,
  no transparent output, manim.cfg is mostly not read.
- MathTex compiles via Typst when the typst extra is installed (no LaTeX needed);
  Tex always needs LaTeX.
- Reference (read before coding, in this order): RTM-Wiki/agent/README.md first,
  then the domain file (runtime, scene-camera, mobject, animation-transform,
  animation-motion, geometry, text, coords-charts, three-d, graph-vector, utils),
  then gotchas.md for errors, patterns.md for recipes.
```

### 解释

- 第一段先立 RTM 和 ManimCE 的关系：模型不会把 RTM 当陌生库，而是当「会写的那套 + 一层窗口」；
- 「Hard facts」都是硬约束（详见 [三种录制方法](03-三种录制方法.md) 和各章参数表），模型拿到后就不会去写不存在的 `manim -qh`；
- 最后一段是阅读清单：让它先读参考再写代码，比让它现场试错快得多。

## 3. 让它读 agent wiki

仓库里有一整套**写给 agent 的压缩参考**：`RTM-Wiki/agent/`，14 个文件，覆盖 00–08 全部章节 + 报错目录 + 配方：

| 文件 | 内容 |
| --- | --- |
| `README.md` | 总览：事实、硬约束、入口、执行模式、阅读顺序（**先读它**） |
| `runtime.md` | 安装、运行、MLWindow、录制、任意帧、Timeline |
| `scene-camera.md` | 场景生命周期、play/wait、上屏、专用场景、相机、config |
| `mobject.md` / `animation-transform.md` / `animation-motion.md` / `geometry.md` / `text.md` / `coords-charts.md` / `three-d.md` / `graph-vector.md` / `utils.md` | 各领域速查（和本手册 01–08 章一一对应） |
| `gotchas.md` | 报错目录：错误 → 原因 → 修法（调试前必读） |
| `patterns.md` | 可复制的配方：场景骨架、更新器、相机、3D、图表…… |

两种喂法：

1. **agent 在仓库里跑**（Claude Code / Codex / Hermes）：什么都不用做——仓库根目录的 `AGENTS.md` 会把它们自动导向 `RTM-Wiki/agent/README.md`；
2. **网页聊天**：读不了仓库，把第 2 节的块粘过去就够用；想要更全，再把 `agent/README.md` 的内容整个贴一遍。

## 4. 最小场景骨架

让 agent 从这段骨架开始改，而不是从零写：

```python
from real_time_manim import *

class MyScene(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口（尺寸会被强制成 1920×1080）
        win.scene = self   #把场景绑定给窗口（必须）
        sq = Square(color=BLUE).set_fill(BLUE, 0.5)
        win.play(Create(sq), run_time=1.0)   #画出方块，时长1秒
        win.play(Wait(0.5))   #等待0.5秒
        win.close()   #关闭窗口（必须，否则不落盘）

fast_record_scene(MyScene, "out.mp4")#导出到项目目录下的 out.mp4
```

### 解释

- 骨架就四件事：**建窗、绑定、播放、关闭**——`win.scene = self` 不写，`play` 直接报错；`win.close()` 不写，文件可能为空；
- `fast_record_scene` 离线出片：不弹窗、帧级精确，改一处跑一次只要几秒（见 [三种录制方法](03-三种录制方法.md)）。

## 5. agent 常犯的错

| 它写了 | 会看到 | 回它这句 |
| --- | --- | --- |
| `manim -qh scene.py Hello` | `command not found` | RTM 没有命令行，改用 `fast_record_scene(Hello, "out.mp4")` |
| `from manim import *` / `import manimlib` | `RuntimeWarning`（类身份来自外部拷贝） | 永远先 `import real_time_manim` |
| `import real-time-manim` | `SyntaxError` | 导入名是 `real_time_manim`（下划线） |
| 忘了 `win.scene = self` | `RuntimeError: win.play() called before the scene was bound...` | 在 `construct` 里绑定 |
| 忘了 `win.close()` | 输出文件为空/不完整 | 结尾调 `win.close()` |
| 裸 Mobject 传给 `win.play` | `TypeError: Unexpected argument ... passed to MLWindow.play()` | 用 `FadeIn`/`Create`/`Write` 包一层 |
| `-ql` / `--fps 30` / `-t` 等旗标 | 不存在 | 输出固定 1920×1080@60，只有一档 |
| 编造了一个不存在的 RTM API | `AttributeError` | 让它先读 `RTM-Wiki/agent/` 对应文件，或 grep 源码 |

## 6. 工作流：让它自己跑

`fast_record_scene` 不弹窗、几秒出片，所以「写 → 跑 → 读报错 → 改」这个循环非常快：

1. 粘第 2 节的块 + 你的需求（能读仓库的 agent 让它先读 `AGENTS.md`）；
2. 让它自己 `python xxx.py` 跑一遍（Claude Code / Codex 都能执行命令）；
3. 报错就把 traceback 原样粘回去——它读得懂，`gotchas.md` 里的条目它也能对上；
4. 网页聊天不能跑代码：你跑，把 traceback 粘回去，效果一样。

---

相关：[下载与安装](01-下载与安装.md) ｜ [快速开始](02-快速开始.md) ｜ [三种录制方法](03-三种录制方法.md) ｜ [ManimCE 用户指南](04-manimCE用户指南.md)
