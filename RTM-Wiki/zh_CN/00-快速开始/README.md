# 00-快速开始

安装 RTM、打开第一个实时窗口、把场景录成 MP4、任意帧预览，以及常见问题。

[首页](../README.md) ｜ [功能状态总览](../99-功能状态总览.md)

| 页面                                      | 内容                 |
| --------------------------------------- | ------------------ |
| [01-安装](01-安装.md)                       | 安装 real-time-manim |
| [02-第一个场景](02-第一个场景.md)                 | 第一个场景              |
| [03-实时窗口-MLWindow](03-实时窗口-MLWindow.md) | 实时窗口 MLWindow      |
| [04-录制视频](04-录制视频.md)                   | 录制视频               |
| [05-任意帧预览](05-任意帧预览.md)                 | 任意帧预览（跳帧，O(1) seek） |

## 导入规则（2.0 起）

RTM 自带它驱动的那份 ManimCE（`real_time_manim/manim/`），所以**一切从 `real_time_manim` 导入**：

```python
from real_time_manim import Scene, Square, Create, BLUE, linear   # mobject / 动画 / 颜色 / 速率函数
from real_time_manim.vulkan_bind import MLWindow, Wait            # 窗口与 RTM 专属实现
from real_time_manim.record import fast_record_scene              # 录制
```

- 不需要 `pip install manim`，也不需要 `import manim`；
- 旧写法 `from manim import ...` 仍然可用——它指向 RTM 自带的同一份实现，拿到的是**同一批类**（本手册的 ManimCE 对照样例就是这么跑的）；
  **例外**：若进程里**先** `import manim`（例如环境另装了 ManimCE），则 `manim` 沿用那份外部副本并在版本不符时打印 `RuntimeWarning`，此时它的类身份与 RTM 内置的那份并不相同——先 `import real_time_manim`（或干脆只用 `from real_time_manim import ...`）即可；
- 没被顶层导出的深层模块走 `real_time_manim.manim.<子模块>`，如 `real_time_manim.manim.utils.paths.spiral_path`。

## 视频样例
TODO：这里添加一个欢迎类的视频。做成类似M动画的效果。