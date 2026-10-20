# 变换

点集插值的 `Transform` 家族：核心 `Transform` / `ReplacementTransform` / `MoveToTarget`、方法与函数驱动（`ApplyMethod` / `ApplyFunction` / `ApplyPointwiseFunction` / `ApplyPointwiseFunctionToCenter` / `ApplyComplexFunction` / `ApplyMatrix`）、状态保存与样式变换、位置互换与复制式变换、淡出—淡入式变换。

[03-动画](../README.md) ｜ [首页](../../README.md) ｜ [功能状态总览](../../99-功能状态总览.md)

- [01-Transform核心](01-Transform核心.md) — 视频 `assets/RTM output/01-Transform核心.mp4` ｜ demo `assets/RTM code/01-Transform核心.py`
- [02-方法与函数驱动](02-方法与函数驱动.md) — 视频 `assets/RTM output/02-方法与函数驱动.mp4` ｜ demo `assets/RTM code/02-方法与函数驱动.py`
- [02b-更多函数驱动](02b-更多函数驱动.md) — 视频 `assets/RTM output/02b-更多函数驱动.mp4` ｜ demo `assets/RTM code/02b-更多函数驱动.py`
- [03-状态保存与样式变换](03-状态保存与样式变换.md) — 视频 `assets/RTM output/03-状态保存与样式变换.mp4` ｜ demo `assets/RTM code/03-状态保存与样式变换.py`
- [03b-收缩与变色](03b-收缩与变色.md) — 视频 `assets/RTM output/03b-收缩与变色.mp4` ｜ demo `assets/RTM code/03b-收缩与变色.py`
- [04-位置互换与复制式变换](04-位置互换与复制式变换.md) — 视频 `assets/RTM output/04-位置互换与复制式变换.mp4` ｜ demo `assets/RTM code/04-位置互换与复制式变换.py`
- [05-淡出淡入式变换](05-淡出淡入式变换.md) — 视频 `assets/RTM output/05-淡出淡入式变换.mp4` ｜ demo `assets/RTM code/05-淡出淡入式变换.py`

每页一条样例视频（RTM 渲染，页面里嵌的就是它）；同名 `-manimce.mp4` 是同一份类代码的 ManimCE 对照成片，只放 `assets/` 供对比，不进页面。

## ManimCE 对照

- 对照脚本：`assets/ManimCE code/<页名>-manimce.py` —— 与 RTM 版同一份类代码，只把 `win.play` 换成 `self.play`、去掉 `MLWindow` 窗口三件套，动画类改从 `manim` 本体导入（生成自 RTM 版并逐行比对过类体）。
- 渲染命令（每页一条，成片归档到 `assets/ManimCE output/<页名>-manimce.mp4`）：

```powershell
cd "assets\ManimCE code"
python -m manim render -qh --media_dir ..\media_manimce -o <页名>-manimce <页名>-manimce.py <类名>
# 产物在 ..\media_manimce\videos\<页名>-manimce\1080p60\<页名>-manimce.mp4，归档到 ..\ManimCE output\<页名>-manimce.mp4
```

- **帧数对齐**：8 页（含匹配变换目录那页）RTM / CE 逐条一致——`01` 678、`02` 573、`02b` 552、`03` 567、`03b` 507、`04` 732、`05` 654（单位：帧 @60fps）。
- **两个 ManimCE 0.21 上游 bug 的绕法**（RTM 由 `real_time_manim.compat` 在导入时打同款补丁，CE 对照脚本里照抄了最小补丁，注释已写明）：
  1. `ApplyPointwiseFunctionToCenter.__init__` 漏传 `mobject`（02b 页），直接构造抛 `TypeError: missing 1 required positional argument: 'mobject'`；
  2. `TransformAnimations` 的非-Transform 子动画缺 `target_copy` / `starting_mobject`（05 页），插值时抛 `AttributeError: 'FadeOut' object has no attribute 'target_copy'`；补上后还有第二层 `zip() argument 2 is shorter than argument 1`（`Transform.get_all_families_zipped` 的 strict zip），同样按 compat 的方式截到最短配对。
- **逐帧目检结论**：7 页两引擎画面逐帧一致（差别仅在字形抗锯齿与个别帧的亚帧相位）；`05` 的 FadeTransform 系在 RTM 开发中版本上重渲后与 CE 一致（其 `FadeTransformPieces` 残留问题已于 2026-10-16 修复，见下）。
- **RTM 侧实测记录**（只记录、不改源码）：
 - `05`：`FadeTransformPieces` 播完残留目标副本的问题已修复（2026-10-16，测试 `tests/test_gap_indication_fade.py`）——`clean_up_from_scene` 先显式摘掉幽灵副本、piece 目标收尾统一为单根入场景，`FadeOut(target)` 从此可淡掉，不再依赖组递归清理；`FadeTransform` 整段形态复查无同类残留。**已知边界**：`FrameServer` / `render_mp4` 这类纯 `render_at` 路径不跑收尾钩子，那里幽灵会保持可见；wiki 样例走 `fast_record_scene → play` 会跑收尾，已覆盖。
  - `02b`：RTM 的 `Create(Dot)` 没有渐进描边过程，首帧即完整（CE 按弧长渐进）；`Create(Square)` 等常规形状两引擎逐帧一致。

## 旧产物（保留）

- [assets/RTM output/sample.mp4](assets/RTM output/sample.mp4)、[assets/RTM code/demo_rtm.py](assets/RTM code/demo_rtm.py)、[assets/ManimCE code/demo_manimce.py](assets/ManimCE code/demo_manimce.py) —— 旧格式顶层演示（每页一段的历史产物），保留不动；新格式内容见上表各页专属 demo 与成片。

## 复现

```powershell
# RTM 版（每页渲本页一条成片；MLWindow 会被强制 1080p60，属正常）
cd "assets\RTM code"
$env:PYTHONPATH="C:\Users\begin\Desktop\real-time-manim"
python 01-Transform核心.py
python 02-方法与函数驱动.py
python 02b-更多函数驱动.py
python 03-状态保存与样式变换.py
python 03b-收缩与变色.py
python 04-位置互换与复制式变换.py
python 05-淡出淡入式变换.py
```

> **2026-10-17 更新**：脚本的出片目标仍是旧布局的 `assets\` 根目录（历史遗留）；页面引用的成片在 `assets\RTM output\`。RTM 侧可用仓库工具一键渲染+归位：
> `python C:\Users\begin\Desktop\real-time-manim\tools\wiki_render.py "<本目录>\RTM code\01-Transform核心.py"`
