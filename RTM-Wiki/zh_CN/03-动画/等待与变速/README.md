	# 等待与变速

`Wait` 纯等待、`ChangeSpeed` 给任意动画按时间百分比配速度倍率、`Animation` 基类占位——外加 8 种 `rate_func` 的速率函数全家桶对比。

[03-动画](../README.md) ｜ [首页](../../README.md) ｜ [功能状态总览](../../99-功能状态总览.md)

- [01-等待速率与变速](01-等待速率与变速.md)

## 每页样例视频与源码

### [01-等待速率与变速](01-等待速率与变速.md)

小节 = 样例 = 视频（页面里嵌的就是这几条）：

| 样例 | 内容 | 视频 | 帧数 |
| --- | --- | --- | --- |
| `wait` | `Wait(1.0)` 纯停 1 秒，前后 `FadeIn`/`FadeOut` 进出 | [assets/RTM output/01-等待速率与变速-wait.mp4](assets/RTM output/01-等待速率与变速-wait.mp4) | 174 |
| `changespeed` | `AnimationGroup` 对撞双点，`speedinfo` 前常速 / 中 0.25 倍 / 末 2 倍 | [assets/RTM output/01-等待速率与变速-changespeed.mp4](assets/RTM output/01-等待速率与变速-changespeed.mp4) | 154 |
| `changespeed_updater` | `ChangeSpeed.add_updater` 挂的位移随 `ChangeSpeed(Wait(1.6), ...)` 变速 | [assets/RTM output/01-等待速率与变速-changespeed_updater.mp4](assets/RTM output/01-等待速率与变速-changespeed_updater.mp4) | 236 |
| `animation` | 裸 `Animation` 占位 1.2 秒，绿方块纹丝不动 | [assets/RTM output/01-等待速率与变速-animation.mp4](assets/RTM output/01-等待速率与变速-animation.mp4) | 162 |
| `ratefunc` | 同一条平移动画配 8 种 `rate_func`（4 平滑/冲激族 + 4 往返/超调族） | [assets/RTM output/01-等待速率与变速-ratefunc.mp4](assets/RTM output/01-等待速率与变速-ratefunc.mp4) | 390 |

- 专属 demo：[assets/RTM code/01-等待速率与变速.py](assets/RTM code/01-等待速率与变速.py)（页面里的代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/01-等待速率与变速-manimce.py](assets/ManimCE code/01-等待速率与变速-manimce.py) → 同名 `-manimce.mp4` 五条，帧数 174/154/236/162/390 全对齐

## CE 对照说明

出片（在 `assets\ManimCE code` 下，内部走 manim CLI `-qh`，自动出片）：

```powershell
cd "assets\ManimCE code"
python 01-等待速率与变速-manimce.py            # 全部
python 01-等待速率与变速-manimce.py ratefunc   # 只跑指定片段
```

对照结论：

- 五对视频帧数全对齐、内容同貌（PSNR 平均 35.6~41.1dB，差异为描边抗锯齿量级），详见 [assets/README.md](assets/README.md)。
- 本目录 CE 首版是"无垫片仿写"（`self.play` 直写、与页面代码不同源），现已按统一样板换成 `manimce_shim.py` 垫片版——五个 class 与 RTM / 页面代码逐字一致，唯一差异是 import。
- `ChangeSpeed` 的 RTM 接线归属：**`window/patches.py`**（`manim.animation.speedmodifier.prepare_animation` 被替成 `_patched_prepare_animation` + `_RtmAnimationAdapter` 桥接 RTM 自有子动画），**不在 `compat.py`**（2026-10-17 更正）。
- `Wait` 的 `stop_condition` / `frozen_frame` 已支持：RTM 自有 `Wait` 现在与 manim 同参构造，两个形参均接线（见 [02-play与wait参数](../通用/02-play与wait参数.md)）；本页样例未涉及。`Wait` 必须从 `real_time_manim.vulkan_bind` 导入——顶层 `from real_time_manim import Wait` 拿到的是 ManimCE 的 `Wait`。
