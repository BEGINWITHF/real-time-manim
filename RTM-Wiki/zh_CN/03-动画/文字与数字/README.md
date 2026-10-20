# 文字与数字

逐字打字/删除、带光标的打字机效果、驱动 `DecimalNumber` 数字变化的动画类。

[03-动画](../README.md) ｜ [首页](../../README.md) ｜ [功能状态总览](../../99-功能状态总览.md)

- [01-逐字出现与消失](01-逐字出现与消失.md) —— AddTextLetterByLetter / RemoveTextLetterByLetter（AddTextWordByWord 上游坏实现）
- [01b-带光标打字](01b-带光标打字.md) —— TypeWithCursor / UntypeWithCursor
- [02-数字动画](02-数字动画.md) —— ChangingDecimal / ChangeDecimalToValue

## 每页视频与 demo

| 页 | RTM 成片 | ManimCE 对照 | demo（RTM） | demo（CE） | 帧数（RTM / CE） |
| --- | --- | --- | --- | --- | --- |
| 01-逐字出现与消失 | [assets/RTM output/01-逐字出现与消失.mp4](assets/RTM output/01-逐字出现与消失.mp4) | [assets/ManimCE output/01-逐字出现与消失-manimce.mp4](assets/ManimCE output/01-逐字出现与消失-manimce.mp4) | [assets/RTM code/01-逐字出现与消失.py](assets/RTM code/01-逐字出现与消失.py) | [assets/ManimCE code/01-逐字出现与消失-manimce.py](assets/ManimCE code/01-逐字出现与消失-manimce.py) | 489 / 489 |
| 01b-带光标打字 | [assets/RTM output/01b-带光标打字.mp4](assets/RTM output/01b-带光标打字.mp4) | [assets/ManimCE output/01b-带光标打字-manimce.mp4](assets/ManimCE output/01b-带光标打字-manimce.mp4) | [assets/RTM code/01b-带光标打字.py](assets/RTM code/01b-带光标打字.py) | [assets/ManimCE code/01b-带光标打字-manimce.py](assets/ManimCE code/01b-带光标打字-manimce.py) | 477 / 477 |
| 02-数字动画 | [assets/RTM output/02-数字动画.mp4](assets/RTM output/02-数字动画.mp4) | [assets/ManimCE output/02-数字动画-manimce.mp4](assets/ManimCE output/02-数字动画-manimce.mp4) | [assets/RTM code/02-数字动画.py](assets/RTM code/02-数字动画.py) | [assets/ManimCE code/02-数字动画-manimce.py](assets/ManimCE code/02-数字动画-manimce.py) | 714 / 714 |

## 对照结论

- `AddTextLetterByLetter` / `RemoveTextLetterByLetter` 原「未验证」已实测落地：逐字显示/消失两引擎逐帧一致（489 帧对齐）；只支持 `Text`。
- `TypeWithCursor` / `UntypeWithCursor` 逐字打字、光标跟随两引擎一致；`ChangingDecimal` / `ChangeDecimalToValue` / `ValueTracker` 跟随的数字逐帧相同（1.01 → 3.96 → 5.6 各采样点一致）。
- **Blink 相位注意**：01b 里 `win.play(Blink(...), run_time=1.2)` 的 play 级 `run_time` 覆盖了 `Blink` 内部 1.5s 总时长，两引擎对"压缩后各段怎么缩"处理不同（CE 按比例缩放、RTM 保持原 on/off 节奏），闪烁明暗相位错开、总帧数一致。想节奏确定就别在 play 级压 `Blink` 的时长。
- `AddTextWordByWord` 上游（ManimCE 0.21）坏实现（源码标 `# TODO, this is broken...`），两引擎同样渲成静止画面，不建议使用。

说明：成片由 `assets\RTM code\<页名>.py` 用 `fast_record_scene(..., fps=60)` 渲染（RTM 强制 1920×1080@60）；对照版 `assets\ManimCE code\<页名>-manimce.py` 是同一份类代码（`self.play` 替代 `win.play`、去窗口），用 `python -m manim render -qh` 渲染后归档到 `assets\ManimCE output\`。逐字类动画的逐帧行为以页面内嵌视频为准。

## 旧产物（保留未删）

`assets/RTM output/sample.mp4`、`assets/RTM code/demo_rtm.py`、`assets/ManimCE code/demo_manimce.py` 是早期"目录级合集"格式的产物，页面已不再引用，按约定保留不动。
