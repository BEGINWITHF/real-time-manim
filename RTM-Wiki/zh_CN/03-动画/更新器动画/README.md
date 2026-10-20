# 更新器动画

播放期间每帧回调驱动对象的动画（`UpdateFromFunc` 等）、12.1 更新工具函数（`always_redraw` 等）与随时间自动变化的对象（`TracedPath`、`AnimatedBoundary`）——都是"每帧/随时间自动更新状态"这一类。

[03-动画](../README.md) ｜ [首页](../../README.md) ｜ [功能状态总览](../../99-功能状态总览.md)

- [01-更新器动画与自动变化](01-更新器动画与自动变化.md) —— UpdateFromFunc / UpdateFromAlphaFunc / MaintainPositionRelativeTo
- [01b-更新工具与自动变化](01b-更新工具与自动变化.md) —— 12.1 工具函数 / TracedPath / AnimatedBoundary

## 每页视频与 demo

| 页 | RTM 成片 | ManimCE 对照 | demo（RTM） | demo（CE） | 帧数（RTM / CE） |
| --- | --- | --- | --- | --- | --- |
| 01-更新器动画与自动变化 | [assets/RTM output/01-更新器动画与自动变化.mp4](assets/RTM output/01-更新器动画与自动变化.mp4) | [assets/ManimCE output/01-更新器动画与自动变化-manimce.mp4](assets/ManimCE output/01-更新器动画与自动变化-manimce.mp4) | [assets/RTM code/01-更新器动画与自动变化.py](assets/RTM code/01-更新器动画与自动变化.py) | [assets/ManimCE code/01-更新器动画与自动变化-manimce.py](assets/ManimCE code/01-更新器动画与自动变化-manimce.py) | 642 / 642 |
| 01b-更新工具与自动变化 | [assets/RTM output/01b-更新工具与自动变化.mp4](assets/RTM output/01b-更新工具与自动变化.mp4) | [assets/ManimCE output/01b-更新工具与自动变化-manimce.mp4](assets/ManimCE output/01b-更新工具与自动变化-manimce.mp4) | [assets/RTM code/01b-更新工具与自动变化.py](assets/RTM code/01b-更新工具与自动变化.py) | [assets/ManimCE code/01b-更新工具与自动变化-manimce.py](assets/ManimCE code/01b-更新工具与自动变化-manimce.py) | 993 / 993 |

## 对照结论

- 两页的全部演示项在 RTM 下逐帧对齐、逐帧目检一致：`UpdateFromFunc`（标签跟点）、`UpdateFromAlphaFunc`（按进度渐显填充）、`MaintainPositionRelativeTo`（保持相对位移）、`always_redraw`（按 ValueTracker 重绘）、`always`/`f_always`（贴着移动对象）、`always_shift`/`always_rotate`（不 play 自动动）、`turn_animation_into_updater`/`cycle_animation`（动画变 updater）、`TracedPath`（黄色拖尾 + `dissipating_time` 消散）、`AnimatedBoundary`（红绿蓝循环描边）。
- 「未验证」清单已全部落地为；唯一不演示的是 `override_animation`（装饰器，无可视差异，见页面「无法演示」）。
- `turn_animation_into_updater` / `cycle_animation` 按 alpha 语义调用 `animation.interpolate(alpha)`，与 RTM 自有时间语义动画（`begin(t)`/`interpolate(t)`）原不兼容；**2026-10-16 已桥接**（`t = origin + alpha*run_time` 归一化驱动，到点收尾并摘除 updater，`cycle=True` 走 `ratio % 1`；manim 原生动画仍走原函数，行为不变，测试 `tests/test_gap_interop.py`），两种来源现在都能喂。样例第 4 步仍用 manim 原生 `Write`/`ApplyWave`（demo 未重渲，两引擎一致）。

说明：成片由 `assets\RTM code\<页名>.py` 用 `fast_record_scene(..., fps=60)` 渲染（RTM 强制 1920×1080@60）；对照版 `assets\ManimCE code\<页名>-manimce.py` 是同一份类代码（`self.play` 替代 `win.play`、去窗口），用 `python -m manim render -qh` 渲染后归档到 `assets\ManimCE output\`。updater 类动画的逐帧行为以页面内嵌视频为准。
