# 等待与变速样例视频（RTM / ManimCE 对照）

这些视频都由 `RTM code/`、`ManimCE code/` 下的源码渲染，页面只引用 **RTM** 那一版；
带 `-manimce` 的是同一份代码用 ManimCE 渲的，留着自己对比，不进页面。

## 01-等待速率与变速

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `wait` | `run_time` 纯等待 1 秒 | `01-等待速率与变速-wait.mp4`（174 帧 / 2.90s） | `01-等待速率与变速-wait-manimce.mp4`（174 帧 / 2.90s） | 对齐 |
| `changespeed` | `speedinfo` 按百分比配速，对撞双点 | `01-等待速率与变速-changespeed.mp4`（154 帧 / 2.57s） | `01-等待速率与变速-changespeed-manimce.mp4`（154 帧 / 2.57s） | 对齐 |
| `changespeed_updater` | `add_updater` 挂的 updater 跟着变速 | `01-等待速率与变速-changespeed_updater.mp4`（236 帧 / 3.93s） | `01-等待速率与变速-changespeed_updater-manimce.mp4`（236 帧 / 3.93s） | 对齐 |
| `animation` | 基类占位 1.2 秒 | `01-等待速率与变速-animation.mp4`（162 帧 / 2.70s） | `01-等待速率与变速-animation-manimce.mp4`（162 帧 / 2.70s） | 对齐 |
| `ratefunc` | 同一条平移动画 × 8 种速率函数 | `01-等待速率与变速-ratefunc.mp4`（390 帧 / 6.50s） | `01-等待速率与变速-ratefunc-manimce.mp4`（390 帧 / 6.50s） | 对齐 |

- 五对逐帧同貌：PSNR 平均 35.6~41.1dB、最低帧 35.0~37.8dB；`changespeed_updater` / `ratefunc` 另做过双引擎抽帧逐条对比。
- 本目录的 `ChangeSpeed`、`Animation` 与 8 种 `rate_func` 两侧都跑 manim 本体的同名实现（RTM 侧由 **`window/patches.py`** 的 `prepare_animation` 补丁 + `_RtmAnimationAdapter` 接管、再走时间轴渲染——**不在 `compat.py`**），没有内容差异——`speedinfo` 重排出的动画帧数（154 帧里的 64、236 帧里的 146）两侧一致。
- `Wait(stop_condition / frozen_frame)` 已支持：RTM 自有 `Wait` 现在与 manim 同参构造，两个形参均接线（条件等待逐帧求值、冻结帧期间不驱动 updaters）；演示见 01-场景与相机/场景/03-播放与等待，本页样例未涉及。`Wait` 须从 `real_time_manim.vulkan_bind` 导入（顶层 `from real_time_manim import Wait` 是 ManimCE 版）。
- `ratefunc` 首轮 `FadeOut` 换标签那行曾被误写进注释（两批标签叠字），已修：三处（RTM/CE/md）同步，重渲后 390 帧两侧一致。

## 复现

`manimce_shim.py` 为 CE 垫片，与 04-图形与文本 同源，勿改：

```powershell
# RTM：在 assets\RTM code 下
cd "assets\RTM code"
python 01-等待速率与变速.py            # 全量渲染 + 拼接
python 01-等待速率与变速.py ratefunc    # 只渲一条，产物落 final\（全量跑才拼接）

# CE：在 assets\ManimCE code 下
cd "..\ManimCE code"
python 01-等待速率与变速-manimce.py     # 全量 + concat；后跟片段名只渲一条（产物落 out_manimce\）
```

> **2026-10-17 更新**：脚本自带的 `concat` 目标仍是旧布局的 `assets\` 根目录（历史遗留）；页面引用的成片在 `assets\RTM output\` / `assets\ManimCE output\`。RTM 侧可用仓库工具一键渲染+归位：
> `python C:\Users\begin\Desktop\real-time-manim\tools\wiki_render.py "<本目录>\RTM code\01-等待速率与变速.py"`

- RTM 只支持 1920×1080@60；demo 里的 `MLWindow(960, 540)` 会被自动纠正并打印提示（良性）。
- PSNR 由 `ffmpeg -lavfi psnr` 逐对测得；差异为描边抗锯齿量级，无内容分歧。
