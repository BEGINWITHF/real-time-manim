# 匹配变换样例视频（RTM / ManimCE 对照）

这些视频都由 `RTM code/`、`ManimCE code/` 下的源码渲染，页面只引用 **RTM** 那一版；
带 `-manimce` 的是同一份代码用 ManimCE 渲的，留着自己对比，不进页面。

## 01-匹配变换

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `shapes_default` | 默认同形匹配（`path_arc=PI/2` 弧线，异形淡出淡入） | `01-匹配变换-shapes_default.mp4`（246 帧 / 4.10s） | `01-匹配变换-shapes_default-manimce.mp4`（246 帧 / 4.10s） | 对齐 |
| `shapes_mismatch` | `transform_mismatches=True` 强行变形 | `01-匹配变换-shapes_mismatch.mp4`（234 帧 / 3.90s） | `01-匹配变换-shapes_mismatch-manimce.mp4`（234 帧 / 3.90s） | 对齐 |
| `shapes_keymap` | `key_map` 手工键配对（`cat` → `hat`） | `01-匹配变换-shapes_keymap.mp4`（234 帧 / 3.90s） | `01-匹配变换-shapes_keymap-manimce.mp4`（234 帧 / 3.90s） | 对齐 |
| `tex` | `TransformMatchingTex` fade 与默认两连跑对照 | `01-匹配变换-tex.mp4`（408 帧 / 6.80s） | `01-匹配变换-tex-manimce.mp4`（408 帧 / 6.80s） | 对齐 |

- 四对逐帧同貌：PSNR 平均 30.9~35.9dB、最低帧 29.7~35.2dB。`shapes_*` 三对 34~36dB；`tex` 对 30.9/29.7 偏低属正常——MathTex 在 RTM 走 Typst 编译、CE 走 LaTeX，公式布局与动画进度逐帧一致（换标边界 f196/f205/f230 双引擎抽帧对比过），差别仅在字形抗锯齿。
- `TransformMatchingShapes` / `TransformMatchingTex`：RTM 侧从 `real_time_manim.vulkan_bind` 导入（RTM 自带实现，含页面顶部记录的四类引擎修复——未匹配零件淡出淡入、收尾残留叠印、FadeTransform 幽灵、目标零件淡入），CE 侧从 `manim` 本体导入——同语义实现，抽帧逐帧同貌。
- `TransformMatchingStrings` 在两引擎均不存在（导入报错原文见页面）。

## 复现

复现（`manimce_shim.py` 为 CE 垫片，与 04-图形与文本 同源，勿改）：

```powershell
# RTM：在 assets\RTM code 下
cd "assets\RTM code"
python 01-匹配变换.py            # 全量渲染 + 拼接
python 01-匹配变换.py tex         # 只渲一条，产物落 final\（全量跑才拼接）

# CE：在 assets\ManimCE code 下
cd "..\ManimCE code"
python 01-匹配变换-manimce.py     # 全量 + concat；后跟片段名只渲一条（产物落 out_manimce\）
```

> **2026-10-17 更新**：脚本自带的 `concat` 目标仍是旧布局的 `assets\` 根目录（历史遗留）；页面引用的成片在 `assets\RTM output\` / `assets\ManimCE output\`。RTM 侧可用仓库工具一键渲染+归位：
> `python C:\Users\begin\Desktop\real-time-manim\tools\wiki_render.py "<本目录>\RTM code\01-匹配变换.py"`

- RTM 只支持 1920×1080@60；demo 里的 `MLWindow(960, 540)` 会被自动纠正并打印提示（良性）。
- `tex` 样例里 RTM 日志出现 `Compiling Typst source`（MathTex 走 Typst 通道），CE 走 LaTeX，均正常出片。
- PSNR 由 `ffmpeg -lavfi psnr` 逐对测得；除上列字形抗锯齿差异外无内容分歧。
