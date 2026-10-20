# 组合编排

把多个动画编排成一个：`AnimationGroup` 并行/错峰、`LaggedStart`/`LaggedStartMap` 流水式逐个启动、`Succession` 一个播完再播下一个。

[03-动画](../README.md) ｜ [首页](../../README.md) ｜ [功能状态总览](../../99-功能状态总览.md)

- [01-AnimationGroup与错峰](01-AnimationGroup与错峰.md)
- [02-Succession顺序播放](02-Succession顺序播放.md)

## 每页样例视频与源码

### [01-AnimationGroup与错峰](01-AnimationGroup与错峰.md)

小节 = 样例 = 视频（页面里嵌的就是这几条）：

| 样例 | 内容 | 视频 | 帧数 |
| --- | --- | --- | --- |
| `animationgroup` | `AnimationGroup(lag_ratio=0.5)` 三个 `.animate` 依次启动，`ag.run_time` 属性赋值拉伸到 1.8s | [assets/RTM output/01-AnimationGroup与错峰-animationgroup.mp4](assets/RTM output/01-AnimationGroup与错峰-animationgroup.mp4) | 198 |
| `laggedstart` | `LaggedStart(lag_ratio=0.3, run_time=1.6)` 5 个彩点流水式淡入 | [assets/RTM output/01-AnimationGroup与错峰-laggedstart.mp4](assets/RTM output/01-AnimationGroup与错峰-laggedstart.mp4) | 186 |
| `laggedstartmap` | `LaggedStartMap(ApplyMethod, ...)` 逐字母染黄、`there_and_back` 回色 | [assets/RTM output/01-AnimationGroup与错峰-laggedstartmap.mp4](assets/RTM output/01-AnimationGroup与错峰-laggedstartmap.mp4) | 210 |

- 专属 demo：[assets/RTM code/01-AnimationGroup与错峰.py](assets/RTM code/01-AnimationGroup与错峰.py)（页面里的代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/01-AnimationGroup与错峰-manimce.py](assets/ManimCE code/01-AnimationGroup与错峰-manimce.py) → 同名 `-manimce.mp4` 三条，帧数 198/186/210 全对齐

### [02-Succession顺序播放](02-Succession顺序播放.md)

| 样例 | 内容 | 视频 | 帧数 |
| --- | --- | --- | --- |
| `succession` | 动→动→`Wait(0.6)`→变色四段串行，一次 `play` 排完 | [assets/RTM output/02-Succession顺序播放-succession.mp4](assets/RTM output/02-Succession顺序播放-succession.mp4) | 294 |
| `ratefunc` | `rate_func=smooth` 作用于整条串行时间轴，两圆依次上移 | [assets/RTM output/02-Succession顺序播放-ratefunc.mp4](assets/RTM output/02-Succession顺序播放-ratefunc.mp4) | 210 |

- 专属 demo：[assets/RTM code/02-Succession顺序播放.py](assets/RTM code/02-Succession顺序播放.py)（页面里的代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/02-Succession顺序播放-manimce.py](assets/ManimCE code/02-Succession顺序播放-manimce.py) → `succession` CE 295 帧、`ratefunc` 210 帧；RTM 侧的 1 帧口径差已在引擎修复（改朴素累加后重渲 demo 实测 295 帧 = CE；本页嵌的成片已于 2026-10-17 重渲为 295 帧 = CE）

## CE 对照说明

出片（在 `assets\ManimCE code` 下，内部走 manim CLI `-qh`，自动出片）：

```powershell
cd "assets\ManimCE code"
python 01-AnimationGroup与错峰-manimce.py             # 全部
python 01-AnimationGroup与错峰-manimce.py laggedstart # 只跑指定片段
python 02-Succession顺序播放-manimce.py
```

> **2026-10-17 更新 · 成片时效**：`01` 的三条成片原渲于 10-15 14:45、`02` 的两条原渲于 10-15 14:43，均早于 `animations/animation_group.py`（10-16 15:22）与 `succession.py`（10-16 13:45）的改动；样例用法未变，**成片已于 2026-10-17 重渲/重发布，与 ManimCE 逐帧对齐**。

对照结论：

- 五对视频内容同貌；`succession` 的 1 帧口径差已在引擎侧修复（重渲即 295 帧对齐，详见下条）；PSNR 平均 31.1~36.4dB，差异为文字字形抗锯齿量级，详见 [assets/README.md](assets/README.md)。
- 本目录 CE 版为 `manimce_shim.py` 垫片版：五个 class 与 RTM / 页面代码逐字一致，唯一差异是 import（`AnimationGroup`/`Succession`/`Wait` 从 manim 本体导入，`LaggedStart`/`LaggedStartMap` 两侧都从 manim 本体导入）。
- `succession` 的 1 帧差已修复：根因是 RTM 用 `sum` 补偿求和与 CE `np.add.accumulate` 的 1 ulp 差跨在 arange 帧边界；引擎改为朴素累加后 RTM 重渲 demo 实测 **295 帧 = CE**（测试锁定），详见 [assets/README.md](assets/README.md)。
