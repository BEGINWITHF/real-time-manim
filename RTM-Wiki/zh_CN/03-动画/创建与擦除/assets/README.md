# 创建与擦除样例视频（RTM / ManimCE 对照）

这些视频都由 `RTM code/`、`ManimCE code/` 下的源码渲染，页面只引用 **RTM** 那一版；
带 `-manimce` 的是同一份代码用 ManimCE 渲的，留着自己对比，不进页面。

## 01-Create与画线族

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `create` | `lag_ratio=0.3` 字母依次画出 | `01-Create与画线族-create.mp4`（168 帧 / 2.80s） | `01-Create与画线族-create-manimce.mp4`（168 帧 / 2.80s） | 对齐 |
| `write` | `linear` 匀速手写 + `run_time`/`lag_ratio` 显式覆盖 | `01-Create与画线族-write.mp4`（180 帧 / 3.00s） | `01-Create与画线族-write-manimce.mp4`（180 帧 / 3.00s） | 对齐 |
| `border_fill` | `stroke_width=6` 蓝轮廓 + `double_smooth` 顿挫填充 | `01-Create与画线族-border_fill.mp4`（198 帧 / 3.30s） | `01-Create与画线族-border_fill-manimce.mp4`（198 帧 / 3.30s） | 对齐 |
| `showpartial` | 抽象基类直播（RTM compat 补丁） | `01-Create与画线族-showpartial.mp4`（168 帧 / 2.80s） | `01-Create与画线族-showpartial-manimce.mp4`（168 帧 / 2.80s） | 对齐 |

- 四对 PSNR 平均 33.3~36.1dB，差异集中在描边抗锯齿与下述中段进度。
- **`showpartial` 的 CE 版是等长占位**：`ShowPartial` 在 CE 里播不了 → CE 版用等长 `Wait(1.3)` 顶替该段（by design，帧数对齐、占位段内容为空白）。
- **`border_fill` 中段进度映射不同**：两引擎都沿周长逐段描边（非 alpha 渐显），但同一帧 RTM 约画到 40%（顶+左两边）、CE 已近整圈；首尾状态一致，PSNR 30~36dB 属正常。

## 02-反向擦除

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `uncreate` | 先画后擦，五参数逐点名倒放擦除 | `02-反向擦除-uncreate.mp4`（222 帧 / 3.70s） | `02-反向擦除-uncreate-manimce.mp4`（222 帧 / 3.70s） | 对齐 |
| `unwrite` | `reverse=False` 从头手擦（"Goodbye" 先消失） | `02-反向擦除-unwrite.mp4`（234 帧 / 3.90s） | `02-反向擦除-unwrite-manimce.mp4`（234 帧 / 3.90s） | 对齐 |
| `add` | `Succession` 时间轴：绿点瞬入 → 隔 0.4s 红蓝 `Group` 停留半秒 | `02-反向擦除-add.mp4`（192 帧 / 3.20s） | `02-反向擦除-add-manimce.mp4`（192 帧 / 3.20s） | 对齐 |

- 三对逐帧同貌：PSNR 平均 34.9~38.7dB、最低帧 32.4~37.7dB。
- `add` 入场时序两引擎一致（抽帧逐帧核对：f101 无点 → f103/f110/f125 仅绿点 → f130 三色齐全）。
- import 口径差异（类体逐字一致）：RTM 侧 `Add`/`Succession` 从 `real_time_manim.vulkan_bind` 导入，CE 侧全部从 `manim` 导入。原"manim `Succession` 装 RTM `Wait` 报 `TypeError`、manim `Add` 不登记进场景"已修复（`window/patches.py`：`prepare_animation` 在 composition/scene 模块重绑定 + `_RtmAnimationAdapter` 语义桥接 + manim `Add` 识别；测试 `tests/test_gap_interop.py`），现从 `manim` 导入两者同样可用。

## 03-逐个显示与集合

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `increasing_subsets` | `np.floor` 按节拍逐个蹦出（先前的都留下） | `03-逐个显示与集合-increasing_subsets.mp4`（210 帧 / 3.50s） | `03-逐个显示与集合-increasing_subsets-manimce.mp4`（210 帧 / 3.50s） | 对齐 |
| `one_by_one` | `np.ceil` 同一时刻只亮一个，轮流闪现 | `03-逐个显示与集合-one_by_one.mp4`（210 帧 / 3.50s） | `03-逐个显示与集合-one_by_one-manimce.mp4`（210 帧 / 3.50s） | 对齐 |
| `spiral_in` | `scale_factor=6` 沿螺旋轨迹飞入 | `03-逐个显示与集合-spiral_in.mp4`（198 帧 / 3.30s） | `03-逐个显示与集合-spiral_in-manimce.mp4`（198 帧 / 3.30s） | 对齐 |

- 三对逐帧同貌：PSNR 平均 34.6~37.3dB、最低帧 34.0~36.5dB。
- `ShowSubmobjectsOneByOne` 不在 RTM 导出清单里：demo 从 `real_time_manim` **顶层**导入（= 内置 ManimCE 0.21 版），CE 侧从 `manim` 导入；`ShowIncreasingSubsets` / `SpiralIn` RTM **自有版**在 `real_time_manim.animations` / `vulkan_bind`，但 demo 也按顶层导入（= 内置 ManimCE 版），实测与 CE 逐帧一致。
- `increasing_subsets` 的取整节奏受默认 `smooth` 缓动影响（前 1/4 段无形状、50% 处 2 个、末段 3→4），两引擎一致。

## 复现

`manimce_shim.py` 为 CE 垫片，与 04-图形与文本 同源，勿改：

```powershell
# RTM：在 assets\RTM code 下（不带参数=全量渲染 + concat 出片）
cd "assets\RTM code"
python 01-Create与画线族.py

# CE：在 assets\ManimCE code 下（不带参数=全量；后跟片段名只渲一条）
cd "..\ManimCE code"
python 01-Create与画线族-manimce.py
python 01-Create与画线族-manimce.py write
python 02-反向擦除-manimce.py
python 03-逐个显示与集合-manimce.py
```

> **2026-10-17 更新**：脚本自带的 `concat` 目标仍是旧布局的 `assets\` 根目录（历史遗留）；页面引用的成片在 `assets\RTM output\` / `assets\ManimCE output\`。RTM 侧可用仓库工具一键渲染+归位：
> `python C:\Users\begin\Desktop\real-time-manim\tools\wiki_render.py "<本目录>\RTM code\01-Create与画线族.py"`

- RTM 只支持 1920×1080@60；demo 里的 `MLWindow(960, 540)` 会被自动纠正并打印提示（良性）。
- PSNR 由 `ffmpeg -lavfi psnr` 逐对测得；30~39dB 区间为描边抗锯齿量级差异，除上列两处注明的内容差异外无分歧。
