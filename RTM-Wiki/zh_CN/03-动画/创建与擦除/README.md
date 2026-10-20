# 创建与擦除

`Create` / `Write` / `DrawBorderThenFill` 画线族、`Uncreate` / `Unwrite` / `Add` 反向擦除，以及
`ShowIncreasingSubsets` / `ShowSubmobjectsOneByOne` / `SpiralIn` 逐个显示与集合。

[03-动画](../README.md) ｜ [首页](../../README.md) ｜ [功能状态总览](../../99-功能状态总览.md)

- [01-Create与画线族](01-Create与画线族.md)
- [02-反向擦除](02-反向擦除.md)
- [03-逐个显示与集合](03-逐个显示与集合.md)

## 每页样例视频与源码

### [01-Create与画线族](01-Create与画线族.md)

小节 = 样例 = 视频（页面里嵌的就是这几条）：

| 样例 | 内容 | 视频 | 帧数 |
| --- | --- | --- | --- |
| `create` | `lag_ratio=0.3` 字母依次画出 | [assets/RTM output/01-Create与画线族-create.mp4](assets/RTM output/01-Create与画线族-create.mp4) | 168 |
| `write` | `linear` 匀速手写 + `run_time`/`lag_ratio` 显式覆盖 | [assets/RTM output/01-Create与画线族-write.mp4](assets/RTM output/01-Create与画线族-write.mp4) | 180 |
| `border_fill` | `stroke_width=6` 蓝轮廓 + `double_smooth` 顿挫填充 | [assets/RTM output/01-Create与画线族-border_fill.mp4](assets/RTM output/01-Create与画线族-border_fill.mp4) | 198 |
| `showpartial` | 抽象基类直播（RTM compat 补丁） | [assets/RTM output/01-Create与画线族-showpartial.mp4](assets/RTM output/01-Create与画线族-showpartial.mp4) | 168 |

- 专属 demo：[assets/RTM code/01-Create与画线族.py](assets/RTM code/01-Create与画线族.py)（页面里的代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/01-Create与画线族-manimce.py](assets/ManimCE code/01-Create与画线族-manimce.py) → 同名 `-manimce.mp4` 四条，帧数 168/180/198/168 全对齐

### [02-反向擦除](02-反向擦除.md)

小节 = 样例 = 视频（页面里嵌的就是这几条）：

| 样例 | 内容 | 视频 | 帧数 |
| --- | --- | --- | --- |
| `uncreate` | 先画后擦，五参数逐点名倒放擦除 | [assets/RTM output/02-反向擦除-uncreate.mp4](assets/RTM output/02-反向擦除-uncreate.mp4) | 222 |
| `unwrite` | `reverse=False` 从头手擦（"Goodbye" 先消失） | [assets/RTM output/02-反向擦除-unwrite.mp4](assets/RTM output/02-反向擦除-unwrite.mp4) | 234 |
| `add` | `Succession` 时间轴：绿点瞬入 → 隔 0.4s 红蓝 `Group` 停留半秒 | [assets/RTM output/02-反向擦除-add.mp4](assets/RTM output/02-反向擦除-add.mp4) | 192 |

- 专属 demo：[assets/RTM code/02-反向擦除.py](assets/RTM code/02-反向擦除.py)（页面里的代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/02-反向擦除-manimce.py](assets/ManimCE code/02-反向擦除-manimce.py) → 同名 `-manimce.mp4` 三条，帧数 222/234/192 全对齐，入场时序逐帧同貌

### [03-逐个显示与集合](03-逐个显示与集合.md)

小节 = 样例 = 视频（页面里嵌的就是这几条）：

| 样例 | 内容 | 视频 | 帧数 |
| --- | --- | --- | --- |
| `increasing_subsets` | `np.floor` 按节拍逐个蹦出（先前的都留下） | [assets/RTM output/03-逐个显示与集合-increasing_subsets.mp4](assets/RTM output/03-逐个显示与集合-increasing_subsets.mp4) | 210 |
| `one_by_one` | `np.ceil` 同一时刻只亮一个，轮流闪现 | [assets/RTM output/03-逐个显示与集合-one_by_one.mp4](assets/RTM output/03-逐个显示与集合-one_by_one.mp4) | 210 |
| `spiral_in` | `scale_factor=6` 沿螺旋轨迹飞入 | [assets/RTM output/03-逐个显示与集合-spiral_in.mp4](assets/RTM output/03-逐个显示与集合-spiral_in.mp4) | 198 |

- 专属 demo：[assets/RTM code/03-逐个显示与集合.py](assets/RTM code/03-逐个显示与集合.py)（页面里的代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/03-逐个显示与集合-manimce.py](assets/ManimCE code/03-逐个显示与集合-manimce.py) → 同名 `-manimce.mp4` 三条，帧数 210/210/198 全对齐

## CE 对照说明

出片（在 `assets\ManimCE code` 下，内部走 manim CLI `-qh`，自动 concat 到 `assets\ManimCE output\`）：

```powershell
cd "assets\ManimCE code"
python 01-Create与画线族-manimce.py            # 全部
python 01-Create与画线族-manimce.py write      # 只跑指定片段
python 02-反向擦除-manimce.py
python 03-逐个显示与集合-manimce.py
```

对照结论：

- 十对视频帧数全对齐、内容同貌（PSNR 平均 33~39dB，差异为描边抗锯齿量级），详见 [assets/README.md](assets/README.md)。
- 两处已注明的内容差异：`showpartial` 的 CE 版用等长 `Wait(1.3)` 占位（`ShowPartial` CE 播不了）；`border_fill` 描边中段进度映射 RTM 慢、CE 快，起止一致。
- **导入口径（2026-10-17 更正）**：本章 RTM demo 的动画类多从 `real_time_manim` **顶层**导入 = **内置 ManimCE 0.21 版**（如 `Create` 是 `Create(ShowPartial)`、`introducer` 固定 `True`、非矢量对象抛 `TypeError`）；**RTM 自有版**（`Create(Animation)`、不做类型校验、`introducer` 默认 `False` 可传）须 `from real_time_manim.vulkan_bind import Create`（或 `real_time_manim.animations`）。两版同名同参、样例用法一致，页面参数表按 **RTM 自有版**写并在页内注明差别。
- `add` 样例的 `Add`/`Succession`：demo 为旧口径——RTM 侧从 `real_time_manim.vulkan_bind` 导入、CE 侧全 `manim`，类体逐字一致。原"manim `Succession` 装 RTM `Wait` 报 `TypeError`、manim `Add` 不登记"的互操作问题已修复（`window/patches.py`，测试 `tests/test_gap_interop.py`），两侧导入现均可用。
