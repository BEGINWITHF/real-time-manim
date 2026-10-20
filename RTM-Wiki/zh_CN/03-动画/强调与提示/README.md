# 强调与提示

把观众视线临时拉到目标上的提示动画：`Indicate` 放大染色强调、`Flash` 放射闪光、`Blink` 明暗闪烁、`ShowPassingFlash`/`ShowPassingFlashWithThinningStrokeWidth` 沿笔画扫光、`ApplyWave` 波纹横穿、`Circumscribe` 圈注、`FocusOn` 光斑聚焦、`Wiggle` 抖动。

[03-动画](../README.md) ｜ [首页](../../README.md) ｜ [功能状态总览](../../99-功能状态总览.md)

- [01-强调与闪烁](01-强调与闪烁.md) —— Indicate / Flash / Blink
- [01b-扫光与波纹](01b-扫光与波纹.md) —— ShowPassingFlash / ApplyWave
- [02-圈注与聚焦](02-圈注与聚焦.md) —— Circumscribe / FocusOn / Wiggle

## 每页视频与 demo

| 页 | RTM 成片 | ManimCE 对照 | demo（RTM） | demo（CE） | 帧数（RTM / CE） |
| --- | --- | --- | --- | --- | --- |
| 01-强调与闪烁 | [assets/RTM output/01-强调与闪烁.mp4](assets/RTM output/01-强调与闪烁.mp4) | [assets/ManimCE output/01-强调与闪烁-manimce.mp4](assets/ManimCE output/01-强调与闪烁-manimce.mp4) | [assets/RTM code/01-强调与闪烁.py](assets/RTM code/01-强调与闪烁.py) | [assets/ManimCE code/01-强调与闪烁-manimce.py](assets/ManimCE code/01-强调与闪烁-manimce.py) | 504 / 504 |
| 01b-扫光与波纹 | [assets/RTM output/01b-扫光与波纹.mp4](assets/RTM output/01b-扫光与波纹.mp4) | [assets/ManimCE output/01b-扫光与波纹-manimce.mp4](assets/ManimCE output/01b-扫光与波纹-manimce.mp4) | [assets/RTM code/01b-扫光与波纹.py](assets/RTM code/01b-扫光与波纹.py) | [assets/ManimCE code/01b-扫光与波纹-manimce.py](assets/ManimCE code/01b-扫光与波纹-manimce.py) | 585 / 585 |
| 02-圈注与聚焦 | [assets/RTM output/02-圈注与聚焦.mp4](assets/RTM output/02-圈注与聚焦.mp4) | [assets/ManimCE output/02-圈注与聚焦-manimce.mp4](assets/ManimCE output/02-圈注与聚焦-manimce.mp4) | [assets/RTM code/02-圈注与聚焦.py](assets/RTM code/02-圈注与聚焦.py) | [assets/ManimCE code/02-圈注与聚焦-manimce.py](assets/ManimCE code/02-圈注与聚焦-manimce.py) | 666 / 666 |

## 对照结论

- 三页的全部演示项在 RTM 下逐帧对齐、逐帧目检一致：`Indicate`/`Flash`/`Blink`、`ShowPassingFlash`/`ShowPassingFlashWithThinningStrokeWidth`/`ApplyWave`、`Circumscribe`（矩形/圆形两种边框）/`FocusOn`/`Wiggle`。
- **Blink 必须先 `self.add(...)`**：`Blink` 不负责引入对象，样例曾漏掉这一行导致 RTM 全程不显示（对照版反而因上游 play 自动引入而能闪），补上后两引擎闪烁相位完全一致。本组页面提醒里已写明。
- **Blink 相位（play 级压缩时）**：`win.play(Blink(...), run_time=1.2)` 这种覆盖内部总时长的写法，两引擎对"各段怎么缩"处理不同（CE 按比例缩、RTM 保持原 on/off 节奏），相位会错开（见文字与数字/01b 的对照）；不压时长则完全同步。
- （2026-10-16 更新）`ShowPassingFlash` 的 `remover` 已接收（默认仍 `True`，播完移出场景；`remover=False` 时对象留在场景并恢复全笔画 `_restore_full_stroke`）；`Circumscribe` 的 `time_width` 已接入——显式传时非 fade 分支走 `ShowPassingFlash` 光束语义（每帧只点亮宽 `time_width` 的一小段），不传时保持旧的 `Create` 渐进绘制（既有渲染逐帧不变），`fade_in/fade_out` 分支与 CE 一致忽略该参数。两条均测试于 `tests/test_gap_indication_fade.py`，页面对应小节已同步。
- `FocusOn`/`Wiggle`/`ShowPassingFlash`/`ApplyWave` 等原「部分验证」项已全部渲染验证。

说明：成片由 `assets\RTM code\<页名>.py` 用 `fast_record_scene(..., fps=60)` 渲染（RTM 强制 1920×1080@60）；对照版 `assets\ManimCE code\<页名>-manimce.py` 是同一份类代码（`self.play` 替代 `win.play`、去窗口），用 `python -m manim render -qh` 渲染后归档到 `assets\ManimCE output\`。

## 视频样例（旧格式合集，保留）

<video src="assets/RTM output/sample.mp4" controls width="560"></video>

- [assets/RTM code/demo_rtm.py](assets/RTM code/demo_rtm.py) —— 旧格式 RTM 版演示场景（本文件夹 3 个页面各一段）
- [assets/ManimCE code/demo_manimce.py](assets/ManimCE code/demo_manimce.py) —— 旧格式 ManimCE 等价写法（仅作对照）

说明：`assets/RTM output/sample.mp4` 是早期"目录级合集"格式的产物，页面已不再引用；三个文件按约定保留不动，页面成片以上表为准。
