# 通用

动画的生命周期与公共构造参数、`Scene.play` / `wait` 参数、`.animate` 语法 —— 每个动画场景都要用到的通用机制。

[03-动画](../README.md) ｜ [首页](../../README.md) ｜ [功能状态总览](../../99-功能状态总览.md)

- [01-生命周期与公共参数](01-生命周期与公共参数.md)
- [02-play与wait参数](02-play与wait参数.md)
- [03-animate语法](03-animate语法.md)

## 每页样例视频与源码

### [01-生命周期与公共参数](01-生命周期与公共参数.md)

<video src="assets/RTM output/01-生命周期与公共参数.mp4" controls width="560"></video>

- RTM 成片：[assets/RTM output/01-生命周期与公共参数.mp4](assets/RTM output/01-生命周期与公共参数.mp4)（804 帧 / 13.4s）
- 专属 demo：[assets/RTM code/01-生命周期与公共参数.py](assets/RTM code/01-生命周期与公共参数.py)（页面里的代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/01-生命周期与公共参数-manimce.py](assets/ManimCE code/01-生命周期与公共参数-manimce.py) → [assets/ManimCE output/01-生命周期与公共参数-manimce.mp4](assets/ManimCE output/01-生命周期与公共参数-manimce.mp4)（804 帧 / 13.4s，帧数对齐）

### [02-play与wait参数](02-play与wait参数.md)

<video src="assets/RTM output/02-play与wait参数.mp4" controls width="560"></video>

- RTM 成片：[assets/RTM output/02-play与wait参数.mp4](assets/RTM output/02-play与wait参数.mp4)（480 帧 / 8.0s）
- 专属 demo：[assets/RTM code/02-play与wait参数.py](assets/RTM code/02-play与wait参数.py)
- CE 对照：[assets/ManimCE code/02-play与wait参数-manimce.py](assets/ManimCE code/02-play与wait参数-manimce.py) → [assets/ManimCE output/02-play与wait参数-manimce.mp4](assets/ManimCE output/02-play与wait参数-manimce.mp4)（480 帧 / 8.0s，帧数对齐）

### [03-animate语法](03-animate语法.md)

<video src="assets/RTM output/03-animate语法.mp4" controls width="560"></video>

- RTM 成片：[assets/RTM output/03-animate语法.mp4](assets/RTM output/03-animate语法.mp4)（558 帧 / 9.3s）
- 专属 demo：[assets/RTM code/03-animate语法.py](assets/RTM code/03-animate语法.py)
- CE 对照：[assets/ManimCE code/03-animate语法-manimce.py](assets/ManimCE code/03-animate语法-manimce.py) → [assets/ManimCE output/03-animate语法-manimce.mp4](assets/ManimCE output/03-animate语法-manimce.mp4)（558 帧 / 9.3s，帧数对齐）

## CE 对照说明

每页的 `<页名>-manimce.py` 与 RTM demo 同一份场景逻辑：`self.play` 替代 `win.play`、去掉 `MLWindow`
窗口三件套、动画类改从 manim 本体导入；画面里的说明文字同步换成 `self.play` 写法。出片：

```powershell
cd "assets\ManimCE code"
python -m manim render -qh --media_dir ..\media_manimce -o <页名>-manimce <页名>-manimce.py <类名>
# 产物在 ..\media_manimce\videos\<页名>-manimce\1080p60\<页名>-manimce.mp4，归档到 ..\ManimCE output\<页名>-manimce.mp4
```

对照结论：

- 三页 RTM / CE **帧数逐条对齐**（804 / 480 / 558），抽帧目检画面几乎逐像素一致，差别只在字重和抗锯齿。
- `01` 的对照脚本比 RTM 版少了两处显式实参：`FadeIn(..., introducer=True)` / `FadeOut(..., remover=True)`
  在 manim 的构造器里是固定值、再传会 `TypeError`（值本来就一样，画面不受影响）；**RTM 侧 `FadeIn` 的 `introducer`
  未固定（默认 `False`、显式传 `True` 生效），`FadeOut` 的 `remover` 固定 `True`——两处显式再传均无害**。
- `02`/`03` 的画面文字 `win.play(...)` 在 CE 版里显示为 `self.play(...)`，其余逐帧一致。

## 旧版合集样例

- [assets/RTM output/sample.mp4](assets/RTM output/sample.mp4)（旧版合集，`fast_record_scene(..., fps=30, ...)` 渲染）与
  [assets/RTM code/demo_rtm.py](assets/RTM code/demo_rtm.py) / [assets/ManimCE code/demo_manimce.py](assets/ManimCE code/demo_manimce.py) 保留不动；
  页面已改用上面每页专属的样例视频。
