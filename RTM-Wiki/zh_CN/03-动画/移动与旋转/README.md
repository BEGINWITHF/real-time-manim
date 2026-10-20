# 移动与旋转

路径移动与同态变换的四个主力类加特殊出场 `Broadcast`——让对象沿轨迹走、用函数逐点重塑形状、从一点扩散波纹。

[03-动画](../README.md) ｜ [首页](../../README.md) ｜ [功能状态总览](../../99-功能状态总览.md)

- [01-旋转](01-旋转.md)
- [02-沿路径与同态变换](02-沿路径与同态变换.md)
- [02b-同态变换其余类](02b-同态变换其余类.md)
- [03-特殊出场](03-特殊出场.md)

## 每页样例视频与源码

### [01-旋转](01-旋转.md)

<video src="assets/RTM output/01-旋转.mp4" controls width="560"></video>

> **2026-10-17 更新 · 成片时效**：上面这条合集 `01-旋转.mp4` 原是 10-15 的旧构建件（540 帧），早于 `animations/rotate.py` / `rotating.py` 的 **10-16 19:33 / 19:39** 改动（显式 `about_point`/`about_edge` 逐帧烘焙真实旋转）。现已用页面三条分片**成对重建**（RTM 与 CE 同时从各自分片重拼，保持逐帧对齐）→ **546 帧 / 9.1s**。重建工具：仓库 `tools/wiki_concat.py --pages --fix`。

- RTM 成片：[assets/RTM output/01-旋转.mp4](assets/RTM output/01-旋转.mp4)（546 帧 / 9.1s，由 10-16 20:09 的三条分片拼成）
- 页面内嵌分片：`assets/RTM output/01-旋转-rotate.mp4` / `-rotating_axis.mp4` / `-rotating_edge.mp4`
- 专属 demo：[assets/RTM code/01-旋转.py](assets/RTM code/01-旋转.py)（页面里的代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/01-旋转-manimce.py](assets/ManimCE code/01-旋转-manimce.py) → [assets/ManimCE output/01-旋转-manimce.mp4](assets/ManimCE output/01-旋转-manimce.mp4)（546 帧 / 9.1s，帧数对齐）

### [02-沿路径与同态变换](02-沿路径与同态变换.md)

<video src="assets/RTM output/02-沿路径与同态变换.mp4" controls width="560"></video>

- RTM 成片：[assets/RTM output/02-沿路径与同态变换.mp4](assets/RTM output/02-沿路径与同态变换.mp4)（468 帧 / 7.8s，由两条分片拼成）
- 专属 demo：[assets/RTM code/02-沿路径与同态变换.py](assets/RTM code/02-沿路径与同态变换.py)
- CE 对照：[assets/ManimCE code/02-沿路径与同态变换-manimce.py](assets/ManimCE code/02-沿路径与同态变换-manimce.py) → [assets/ManimCE output/02-沿路径与同态变换-manimce.mp4](assets/ManimCE output/02-沿路径与同态变换-manimce.mp4)（468 帧 / 7.8s，帧数对齐）

### [02b-同态变换其余类](02b-同态变换其余类.md)

<video src="assets/RTM output/02b-同态变换其余类.mp4" controls width="560"></video>

- RTM 成片：[assets/RTM output/02b-同态变换其余类.mp4](assets/RTM output/02b-同态变换其余类.mp4)（606 帧 / 10.1s，由三条分片拼成）
- 专属 demo：[assets/RTM code/02b-同态变换其余类.py](assets/RTM code/02b-同态变换其余类.py)
- CE 对照：[assets/ManimCE code/02b-同态变换其余类-manimce.py](assets/ManimCE code/02b-同态变换其余类-manimce.py) → [assets/ManimCE output/02b-同态变换其余类-manimce.mp4](assets/ManimCE output/02b-同态变换其余类-manimce.mp4)（606 帧 / 10.1s，帧数对齐）

### [03-特殊出场](03-特殊出场.md)

<video src="assets/RTM output/03-特殊出场.mp4" controls width="560"></video>

- RTM 成片：[assets/RTM output/03-特殊出场.mp4](assets/RTM output/03-特殊出场.mp4)（456 帧 / 7.6s，由两条分片拼成）
- 专属 demo：[assets/RTM code/03-特殊出场.py](assets/RTM code/03-特殊出场.py)
- CE 对照：[assets/ManimCE code/03-特殊出场-manimce.py](assets/ManimCE code/03-特殊出场-manimce.py) → [assets/ManimCE output/03-特殊出场-manimce.mp4](assets/ManimCE output/03-特殊出场-manimce.mp4)（456 帧 / 7.6s，帧数对齐）

## CE 对照说明

每页的 `<页名>-manimce.py` 与 RTM demo 同一份场景逻辑：`self.play` 替代 `win.play`、去掉 `MLWindow`
窗口三件套、动画类改从 manim 本体导入；画面里的说明文字只在含 `win.play(...)` 时换成 `self.play(...)` 写法
（本目录四页的签名文字都是类调用，无需替换）。出片：

```powershell
cd "assets\ManimCE code"
python 01-旋转-manimce.py            # 全部片段；后跟片段名只渲一条
# 片段落 out_manimce\，脚本把拼接成片写到上一级 assets\（旧布局遗留），
# 再移进页面引用的 ..\ManimCE output\<页名>-manimce.mp4
```

对照结论：

- 四页 RTM / CE **帧数逐条对齐**（546 / 468 / 606 / 456），抽帧目检画面内容一致；
  逐帧 `blend=difference` 平均差 0.79~1.83/255（最大 5.7/255），差异集中在中文字形的光栅化
  （Cairo vs RTM 自绘）与字重，位置、动画时序、形状完全一致。
- 2026-10-17：四条整页合集（`01-旋转` / `02-沿路径与同态变换` / `02b-同态变换其余类` / `03-特殊出场`）
  原是 10-15 的构建件，帧数与当前分片之和对不上（540/480/600/498 vs 546/468/606/456），已由
  `tools/wiki_concat.py --pages --fix` **成对重建**（RTM 与 CE 同时重拼，保持逐帧对齐）。
- 同日修复 `Homotopy` 的形变语义：RTM 原先把形变函数直接施加在原始控制点上，CE 是先按
  `pre_function_handle_to_anchor_scale_factor` 把手柄收缩到锚点的 1%、逐点映射、再外推 100 倍——
  描出来的曲线才真正跟随形变。修复后 `02-沿路径与同态变换-homotopy` 与 CE 的逐帧平均差
  从 2.303 降到 0.287（480x270 解码、阈值 4.0：坏帧 42 → 0）。
- `02b` 的 CE 脚本顶部带两行**上游 bug 绕法**：manim 0.21 的
  `SmoothedVectorizedHomotopy.interpolate_submobject` 引用了没导入的 `VMobject`，纯命令行渲染
  第一次插值就 `NameError`；RTM 侧由 `real_time_manim/compat.py` 同源修复，所以 RTM demo 无需改动。
  绕法即 `movement.VMobject = VMobject`（脚本顶部有注释，照抄即可）。
- `03-特殊出场` 的 `Broadcast`、`01-AnimationGroup与错峰` 的 `LaggedStart`/`LaggedStartMap`
  都不在 RTM 自有动画导出清单里，但用 manim 本体类经 RTM 时间轴渲染完全正常（两引擎均出片、逐帧对齐）。

## 旧版合集样例

- [assets/RTM output/sample.mp4](assets/RTM output/sample.mp4)（旧版合集，`fast_record_scene(..., fps=30, ...)` 渲染）与
  [assets/RTM code/demo_rtm.py](assets/RTM code/demo_rtm.py) / [assets/ManimCE code/demo_manimce.py](assets/ManimCE code/demo_manimce.py)
  保留不动；页面已改用上面每页专属的样例视频。
