# 匹配变换

把源与目标拆成「零件」、按键配对的变换家族：按形状匹配的 `TransformMatchingShapes`、按 LaTeX 片段匹配的 `TransformMatchingTex`，以及它们的抽象基类 `TransformMatchingAbstractBase`。

[03-动画](../README.md) ｜ [首页](../../README.md) ｜ [功能状态总览](../../99-功能状态总览.md)

- [01-匹配变换](01-匹配变换.md)

## 每页样例视频与源码

### [01-匹配变换](01-匹配变换.md)

小节 = 样例 = 视频（页面里嵌的就是这几条）：

| 样例 | 内容 | 视频 | 帧数 |
| --- | --- | --- | --- |
| `shapes_default` | 默认同形匹配：`the morse code` → `here come dots`，异形淡出淡入 | [assets/RTM output/01-匹配变换-shapes_default.mp4](assets/RTM output/01-匹配变换-shapes_default.mp4) | 246 |
| `shapes_mismatch` | `transform_mismatches=True`：对不上的零件强行变形 | [assets/RTM output/01-匹配变换-shapes_mismatch.mp4](assets/RTM output/01-匹配变换-shapes_mismatch.mp4) | 234 |
| `shapes_keymap` | `key_map` 手工把 `"c"` 配给 `"h"`（`cat` → `hat`，首字母互换） | [assets/RTM output/01-匹配变换-shapes_keymap.mp4](assets/RTM output/01-匹配变换-shapes_keymap.mp4) | 234 |
| `tex` | `TransformMatchingTex` 公式变形，`fade_transform_mismatches=True` 与默认行为两连跑对照 | [assets/RTM output/01-匹配变换-tex.mp4](assets/RTM output/01-匹配变换-tex.mp4) | 408 |

- 专属 demo：[assets/RTM code/01-匹配变换.py](assets/RTM code/01-匹配变换.py)（页面里的代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/01-匹配变换-manimce.py](assets/ManimCE code/01-匹配变换-manimce.py) → 同名 `-manimce.mp4` 四条，帧数 246/234/234/408 全对齐

## CE 对照说明

出片（在 `assets\ManimCE code` 下，内部走 manim CLI `-qh`，自动出片）：

```powershell
cd "assets\ManimCE code"
python 01-匹配变换-manimce.py            # 全部
python 01-匹配变换-manimce.py tex         # 只跑指定片段
```

对照结论：

- 四对视频帧数全对齐、内容同貌（PSNR 平均 30.9~35.9dB），详见 [assets/README.md](assets/README.md)。
- `tex` 对的 PSNR 略低（30.9 / 最低 29.7）属正常：MathTex 在 RTM 走 Typst、CE 走 LaTeX，公式布局与动画进度逐帧一致，差别仅在字形抗锯齿。
- **成片时效**：四条 RTM 成片渲于 **10-16 03:44**，早于 `animations/fade_transform.py` 的 **10-16 13:38**（`FadeTransformPieces` 播完残留目标副本的清理修复）与 `animation_group.py` 的 **15:22**。`tex` 样例用了 `fade_transform_mismatches=True`（走 `FadeTransformPieces`），重渲即带上收尾清理；其余三条不受影响。
- import 口径（类体逐字一致）：RTM 侧 `TransformMatchingShapes` / `TransformMatchingTex` 从 `real_time_manim.vulkan_bind` 导入（RTM 自带实现，含页面顶部记录的四类引擎修复），CE 侧从 `manim` 导入，配 `manimce_shim.py` 垫片——本目录 CE 首版是"无垫片仿写"，现已按统一样板换成垫片版。
- `TransformMatchingStrings` 两引擎均不存在（页面小节有导入报错原文）。
