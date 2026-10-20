# 生长出现

Grow 家族的入场动画：`GrowFromPoint` 从指定点长出、`GrowFromCenter` 从自身中心长出、`GrowFromEdge`
从包围盒的边长出、`GrowArrow` 箭头从起点长向箭尖、`SpinInFromNothing` 边旋转边长大。

[03-动画](../README.md) ｜ [首页](../../README.md) ｜ [功能状态总览](../../99-功能状态总览.md)

- [01-Grow家族](01-Grow家族.md)
- [01b-箭头与旋入](01b-箭头与旋入.md)

## 每页样例视频与源码

### [01-Grow家族](01-Grow家族.md)

<video src="assets/RTM output/01-Grow家族.mp4" controls width="560"></video>

- RTM 成片：[assets/RTM output/01-Grow家族.mp4](assets/RTM output/01-Grow家族.mp4)（558 帧 / 9.3s）
- 专属 demo：[assets/RTM code/01-Grow家族.py](assets/RTM code/01-Grow家族.py)（页面里的代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/01-Grow家族-manimce.py](assets/ManimCE code/01-Grow家族-manimce.py) → [assets/ManimCE output/01-Grow家族-manimce.mp4](assets/ManimCE output/01-Grow家族-manimce.mp4)（558 帧 / 9.3s，帧数对齐）

### [01b-箭头与旋入](01b-箭头与旋入.md)

<video src="assets/RTM output/01b-箭头与旋入.mp4" controls width="560"></video>

- RTM 成片：[assets/RTM output/01b-箭头与旋入.mp4](assets/RTM output/01b-箭头与旋入.mp4)（522 帧 / 8.7s）
- 专属 demo：[assets/RTM code/01b-箭头与旋入.py](assets/RTM code/01b-箭头与旋入.py)
- CE 对照：[assets/ManimCE code/01b-箭头与旋入-manimce.py](assets/ManimCE code/01b-箭头与旋入-manimce.py) → [assets/ManimCE output/01b-箭头与旋入-manimce.mp4](assets/ManimCE output/01b-箭头与旋入-manimce.mp4)（522 帧 / 8.7s，帧数对齐）

## CE 对照说明

每页的 `<页名>-manimce.py` 与 RTM demo 同一份场景逻辑：`self.play` 替代 `win.play`、去掉 `MLWindow`
窗口三件套、动画类改从 manim 本体导入。出片：

```powershell
cd "assets\ManimCE code"
python -m manim render -qh --media_dir ..\media_manimce -o <页名>-manimce <页名>-manimce.py <类名>
# 产物在 ..\media_manimce\videos\<页名>-manimce\1080p60\<页名>-manimce.mp4，归档到 ..\ManimCE output\<页名>-manimce.mp4
```

对照结论：

- 两页 RTM / CE **帧数逐条对齐**（558 / 522），抽帧目检几乎逐像素一致：`GrowFromPoint` 的
  坐标/mobject 两种起点、`point_color` 渐变起点色、`GrowFromEdge(edge=RIGHT)`、
  `GrowArrow` 从起点长向箭尖、`SpinInFromNothing` 的 `angle=2*PI` 与默认 `PI/2` 对照，两边一致。
- `01-Grow家族.mp4` 的 RTM 成片是**当前引擎重渲**的：旧片里标签淡出后有文字残影（三个标签
  叠在一起），系旧版引擎的淡出残影问题（现已修复，同代码复现不出）；demo 代码未改动，
  仅用当前引擎重新渲染替换。重渲后与 CE 版逐帧一致。

## 旧版合集样例

- [assets/RTM output/sample.mp4](assets/RTM output/sample.mp4)（旧版合集，`fast_record_scene(..., fps=30, ...)` 渲染）与
  [assets/RTM code/demo_rtm.py](assets/RTM code/demo_rtm.py) / [assets/ManimCE code/demo_manimce.py](assets/ManimCE code/demo_manimce.py) 保留不动；
  页面已改用上面每页专属的样例视频。
