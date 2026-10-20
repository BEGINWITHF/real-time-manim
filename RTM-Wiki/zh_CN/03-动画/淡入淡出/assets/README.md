# 淡入淡出样例视频（RTM / ManimCE 对照）

这些视频都由 `RTM code/`、`ManimCE code/` 下的源码渲染，页面（`01-Fade家族.md`）只引用 **RTM** 那一版；
带 `-manimce` 的是同一份代码用 ManimCE 渲的，留着自己对比，不进页面。

## 01-Fade家族

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `fadein` | `shift` 从下进 / `scale=0.5` 半大长回 / `target_position=ORIGIN` 从心飘来 | `01-Fade家族-fadein.mp4`（156 帧 / 2.60s） | `01-Fade家族-fadein-manimce.mp4`（156 帧 / 2.60s） | 对齐 |
| `fadeout` | `shift=UP` 飘走 / `scale=0.3 + target_position` 缩淡向心 / 标签就地换行 | `01-Fade家族-fadeout.mp4`（174 帧 / 2.90s） | `01-Fade家族-fadeout-manimce.mp4`（174 帧 / 2.90s） | 对齐 |
| `swap` | `AnimationGroup(FadeOut, FadeIn)` 手册换页组合 | `01-Fade家族-swap.mp4`（216 帧 / 3.60s） | `01-Fade家族-swap-manimce.mp4`（216 帧 / 3.60s） | 对齐 |

- 三对画面逐帧同貌：PSNR 平均 36~39dB、最低帧 34.6dB，差异全在描边抗锯齿量级，无内容分歧。
- **换页组合的两个 `AnimationGroup` 版本对照**（各渲 216 帧；"必须从 manim 导入"的旧结论已于 2026-10-16 随修复过时）：
  - `from manim import AnimationGroup` —— **正常**：组合期间 `FadeOut` 换下与 `FadeIn` 新对象换上同时发生，两引擎表现一致；页面样例用的就是它。
 - `from real_time_manim.vulkan_bind import AnimationGroup`（RTM 自有版）—— **已修复**：此前"新对象全程缺席"（`FadeIn(ya, yb)` 组合播放中不出现、连后面的 `Wait` 也不冒出来）的问题已随本轮补全解决——`AnimationGroup` 新增递归 `mobjects` 属性 + `_setup_scene` 钩子，真实窗口端到端复测 opacity 0→1 正常（测试 `tests/test_gap_composition.py`），两版现均可用。
  - 复现（记录的是修复前状态）：`RTM code/_test_swap_vtk.py` 只改 `AnimationGroup` 来源渲 swap，抽 f140（组合中段）与 f215（结尾）即可看出旧版缺陷画面。

## 复现

```powershell
# RTM 版：在 assets\RTM code 下，不带参数渲全部片段，并拼出页面里的三条样例视频
cd "assets\RTM code"
python 01-Fade家族.py
python 01-Fade家族.py fadeout    # 只渲指定片段

# ManimCE 对照版：在 assets\ManimCE code 下（同一个 manimce_shim 垫片把 win.play 转成 self.play）
cd "..\ManimCE code"
python 01-Fade家族-manimce.py
python 01-Fade家族-manimce.py swap    # 只渲指定片段
```

> **2026-10-17 更新**：脚本自带的 `concat` 目标仍是旧布局的 `assets\` 根目录（历史遗留）；页面引用的成片在 `assets\RTM output\` / `assets\ManimCE output\`。RTM 侧可用仓库工具一键渲染+归位：
> `python C:\Users\begin\Desktop\real-time-manim\tools\wiki_render.py "<本目录>\RTM code\01-Fade家族.py"`

RTM 只支持 1920×1080@60，`MLWindow(960, 540)` 会被强制纠正并打印一行提示，属正常。
