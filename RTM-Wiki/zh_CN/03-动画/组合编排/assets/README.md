# 组合编排样例视频（RTM / ManimCE 对照）

这些视频都由 `RTM code/`、`ManimCE code/` 下的源码渲染，页面只引用 **RTM** 那一版；
带 `-manimce` 的是同一份代码用 ManimCE 渲的，留着自己对比，不进页面。

> **2026-10-17 更新 · 成片时效**：下表五条 RTM 成片原渲于 **10-15 14:43~14:45**，早于
> `animations/animation_group.py`（**10-16 15:22**：`run_time=` / `group=` 接线、
> `synchronize_with_wall_clock=True` 显式抛 `ValueError`、默认 `rate_func=_linear`）
> 与 `succession.py`（**10-16 13:45**）的改动。样例只用 `lag_ratio` / 属性赋值 `run_time`，
> 画面语义未变；**成片已于 2026-10-17 全部重渲/重发布，与 ManimCE 逐帧对齐**（`succession` 现为 295 帧 = CE）。

## 01-AnimationGroup与错峰

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `animationgroup` | `AnimationGroup(lag_ratio=0.5)` 三个 `.animate` 依次启动，`ag.run_time=1.8` 属性赋值拉伸整轴 | `01-AnimationGroup与错峰-animationgroup.mp4`（198 帧 / 3.30s） | `01-AnimationGroup与错峰-animationgroup-manimce.mp4`（198 帧 / 3.30s） | 对齐 |
| `laggedstart` | `LaggedStart(lag_ratio=0.3, run_time=1.6)` 5 个彩点流水式淡入 | `01-AnimationGroup与错峰-laggedstart.mp4`（186 帧 / 3.10s） | `01-AnimationGroup与错峰-laggedstart-manimce.mp4`（186 帧 / 3.10s） | 对齐 |
| `laggedstartmap` | `LaggedStartMap(ApplyMethod, arg_creator)` 逐字母染黄、`there_and_back` 回色 | `01-AnimationGroup与错峰-laggedstartmap.mp4`（210 帧 / 3.50s） | `01-AnimationGroup与错峰-laggedstartmap-manimce.mp4`（210 帧 / 3.50s） | 对齐 |

## 02-Succession顺序播放

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `succession` | 动→动→`Wait(0.6)`→变色四段串行，一次 `play` 排完 | `02-Succession顺序播放-succession.mp4`（295 帧 / 4.917s） | `02-Succession顺序播放-succession-manimce.mp4`（295 帧 / 4.917s） | 对齐 |
| `ratefunc` | `rate_func=smooth` 作用于整条串行时间轴，两圆依次上移 | `02-Succession顺序播放-ratefunc.mp4`（210 帧 / 3.50s） | `02-Succession顺序播放-ratefunc-manimce.mp4`（210 帧 / 3.50s） | 对齐 |

- 五对逐帧同貌：PSNR 平均 31.1~36.4dB；`animationgroup` 的 31.1（最低帧 27.9）是标题/签名文字的字形抗锯齿差异，RTM/CE 双侧抽帧对比画面内容一致（错峰位移序列逐帧吻合）。
- `LaggedStart` / `LaggedStartMap` 不在 RTM 自有 39 类的导出清单里——demo 直接 `from real_time_manim import LaggedStart`（顶层 = `from manim import *`，拿到的就是内置 ManimCE 版，与 `from manim import ...` 同一个类），经 RTM 时间轴渲染，三条视频全部逐帧对齐。
- `succession` 的 1 帧差（原：CE 295 vs RTM 294）已修复：根因是 `Succession` 内含 `Wait` 时，RTM 用 `sum` 补偿求和与 CE `np.add.accumulate` 存在 1 ulp 差、恰好跨在 arange 帧边界上（该段 205 vs 204 帧）；引擎改为朴素累加后 RTM 重渲 demo 实测 **295 帧 = CE**（已加测试锁定）。本页嵌的成片已于 2026-10-17 重渲为 **295 帧**，与 CE 对齐。
- `AnimationGroup` 构造器里传 `run_time` 现已支持（非 `None` 时按 CE 语义整体拉伸子动画时间轴，不再 `TypeError`）；`group=` 显式容器形参同样已接线；`synchronize_with_wall_clock=True` **显式抛 `ValueError`**（RTM 时间轴按帧驱动，无墙钟路径）；组级默认 `rate_func` 已改为 `_linear` 对齐 CE。样例仍用属性赋值 `ag.run_time = 1.8`（与构造器传入等价；CE 侧 manim 本体对该写法同样生效，108 帧 = 1.8s 两侧一致）。

## 复现

`manimce_shim.py` 为 CE 垫片，与 04-图形与文本 同源，勿改：

```powershell
# RTM：在 assets\RTM code 下
cd "assets\RTM code"
python 01-AnimationGroup与错峰.py             # 全量渲染 + 拼接
python 01-AnimationGroup与错峰.py laggedstart # 只渲一条，产物落 final\（全量跑才拼接）

# CE：在 assets\ManimCE code 下
cd "..\ManimCE code"
python 01-AnimationGroup与错峰-manimce.py     # 全量 + concat；后跟片段名只渲一条（产物落 out_manimce\）
python 02-Succession顺序播放.py
python 02-Succession顺序播放-manimce.py
```

> **2026-10-17 更新**：脚本自带的 `concat` 目标仍是旧布局的 `assets\` 根目录（历史遗留）；页面引用的成片在 `assets\RTM output\` / `assets\ManimCE output\`。RTM 侧可用仓库工具一键渲染+归位：
> `python C:\Users\begin\Desktop\real-time-manim\tools\wiki_render.py "<本目录>\RTM code\01-AnimationGroup与错峰.py"`

- RTM 只支持 1920×1080@60；demo 里的 `MLWindow(960, 540)` 会被自动纠正并打印提示（良性）。
- PSNR 由 `ffmpeg -lavfi psnr` 逐对测得；差异为文字字形抗锯齿量级，无内容分歧。
