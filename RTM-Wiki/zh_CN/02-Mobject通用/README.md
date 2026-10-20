# 02-Mobject通用

所有 mobject 共用的能力：构造与容器、摆放、测量、变形、样式、`.animate`、更新器 + `ValueTracker`。

[首页](../README.md) ⬅ → [功能状态总览](../99-功能状态总览.md)

本目录的每页都按统一格式重写：**参数表 → 样例代码 → 白话讲解 → RTM 视频 → 温馨提醒**；
视频全部由 RTM 实渲，逐条与原版 manim 引擎对照、逐条核对帧数（74 条样例全部逐帧对齐）。
对照视频、渲染源码与帧数/差异对照表在 [`assets/README.md`](assets/README.md)。

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01-构造与容器](01-构造与容器.md) | `Mobject` 构造参数、`Group`、`add`/`remove`/`insert`、索引切片 | 4 条样例，RTM/CE 逐帧对齐 |
| [01b-构造与容器-进阶](01b-构造与容器-进阶.md) | `get_family`、点数查询、`set`、`set_default`、构造钩子 | 5 条样例 |
| [02-摆放位置](02-摆放位置.md) | `shift`、`move_to`、`next_to`、`to_edge`/`to_corner`、`center`/`align_to` | 5 条样例 |
| [02b-摆放位置-进阶](02b-摆放位置-进阶.md) | `align_on_border`、`set_coord` 族、`arrange`、网格、`surround`、`put_start_and_end_on` 等 | 8 条样例 |
| [03-测量](03-测量.md) | `width/height/depth`、边中点与关键点读取、顶点云、底层统计 | 5 条样例 |
| [04-缩放旋转与变形](04-缩放旋转与变形.md) | `scale`、`rotate`（含 `Rotate` 对照）、`flip`、`stretch` | 4 条样例 |
| [04b-缩放旋转与变形-进阶](04b-缩放旋转与变形-进阶.md) | `rescale_to_fit`、六个 fit 方法、`pose_at_angle`、`apply_*` 变换族、`repeat`/`reverse_points` | 6 条样例 |
| [05-样式与颜色](05-样式与颜色.md) | `set_color`、渐变四件套、`fade_to`/`fade`、`z_index`、背景衬底 | 6 条样例 |
| [06-复制派生与状态](06-复制派生与状态.md) | `copy`、`become`、`save_state`/`restore`、`generate_target`、`interpolate`、`match_*` | 7 条样例 |
| [07-animate语法](07-animate语法.md) | `.animate` 语法与 play 参数、`@override_animate`、`add_animation_override` | 3 条样例 |
| [08-更新器](08-更新器.md) | `add_updater`/`remove_updater`/`clear_updaters`、`suspend`、`always`、查询与 `match_updaters` | 5 条样例 |
| [08b-更新器工具函数](08b-更新器工具函数.md) | `always_redraw`、`always`/`f_always`、`always_shift`/`always_rotate`、动画变 updater | 4 条样例 |
| [09-更新器动画](09-更新器动画.md) | `UpdateFromFunc`、`UpdateFromAlphaFunc`、`MaintainPositionRelativeTo` | 3 条样例 |
| [10-ValueTracker](10-ValueTracker.md) | 可动画的数值：改值/运算/插值、`ComplexValueTracker` | 3 条样例 |
| [11-屏幕框架与横幅](11-屏幕框架与横幅.md) | `ScreenRectangle`、`FullScreenRectangle`、`ManimBanner` | 3 条样例 |
| [11b-低频其余API](11b-低频其余API.md) | `sort`/`shuffle`/`invert`、`apply_to_family`、路径取点族；位图导出与基类工厂标注无法出片 | 3 条样例 + 2 组说明 |

## 视频与样例

- 每页样例视频在页面内直接嵌 **RTM** 版本：`assets/RTM output/<页名>-<样例名>.mp4`。
- `assets/ManimCE output/` 下保留同名 `-manimce` 的 CE 对照版；帧数与 RTM 逐条一致，可逐帧对比。
- 渲染源码在页面同级 `assets\RTM code\`（RTM 版 `<页名>.py`）与 `assets\ManimCE code\`（CE 版
  `<页名>-manimce.py`、CE 垫片 `manimce_shim.py`），两目录各有子目录 `final/`（RTM 输出）与
  `out_manimce/`（CE 输出）；复现细节见 [`assets/README.md`](assets/README.md)。

复现时 `MLWindow(960, 540)` 会被 RTM 强制纠正成 1920×1080 并打印一行提示，属正常（RTM 只支持 1080p60）。
