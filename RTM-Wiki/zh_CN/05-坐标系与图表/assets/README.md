# 05-坐标系与图表 样例视频（RTM / ManimCE 对照）

这些视频都由 `assets/RTM code/`（RTM 版脚本）与 `assets/ManimCE code/`（CE 版脚本，同名 + `-manimce`，另有 `manimce_shim.py` 垫片）下的源码渲染，页面只引用 **RTM** 那一版；
带 `-manimce` 的是同一份代码用 ManimCE 渲的，留着自己对比，不进页面。成片分别归档在 `assets/RTM output/` 与 `assets/ManimCE output/`。

> 字形差异说明：下面几处 PSNR 注记写的是"RTM Typst vs CE LaTeX"，对应渲染时已装 `real-time-manim[typst]` extra 且未设 `RTM_TYPST=0`；**未装 extra 的环境 `MathTex` 走真实 LaTeX**，与 CE 的字形差异会随之消失。

## 01-NumberLine

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `basic` | `x_range`/`length`/`include_tip`/`include_numbers` 基本构造，红点沿轴移动 | `01-NumberLine-basic.mp4`（258 帧 / 4.30s） | `01-NumberLine-basic-manimce.mp4`（258 帧 / 4.30s） | 对齐 |
| `unitinterval` | `UnitInterval` 默认外观（0.1 步长、一位小数、端点加长刻度） | `01-NumberLine-unitinterval.mp4`（138 帧 / 2.30s） | `01-NumberLine-unitinterval-manimce.mp4`（138 帧 / 2.30s） | 对齐 |

- 两对帧数全对齐；PSNR avg 33.3 / 37.1dB（数轴数字走 MathTex：RTM Typst vs CE LaTeX，字形抗锯齿差异，无内容分歧，已抽帧目检）。

## 01b-数轴方法进阶

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `n2p_p2n` | `n2p`/`p2n`/`@` 双向换算，红点移动后回读数值 | `01b-数轴方法进阶-n2p_p2n.mp4`（276 帧 / 4.60s） | `01b-数轴方法进阶-n2p_p2n-manimce.mp4`（276 帧 / 4.60s） | 对齐 |
| `addnumbers` | `add_numbers` 指定数值 + `add_labels` 任意标签 | `01b-数轴方法进阶-addnumbers.mp4`（138 帧 / 2.30s） | `01b-数轴方法进阶-addnumbers-manimce.mp4`（138 帧 / 2.30s） | 对齐 |
| `ticks` | `add_ticks`/`get_tick_marks` 补刻度改色，绕数值 0 旋转 | `01b-数轴方法进阶-ticks.mp4`（222 帧 / 3.70s） | `01b-数轴方法进阶-ticks-manimce.mp4`（222 帧 / 3.70s） | 对齐 |

- 三对帧数全对齐；PSNR avg 37.7 / 36.9 / 38.5dB，无内容分歧（`add_labels` 的 `str` 走 MathTex，两引擎数学字体字形略异属预期）。
- `ticks` 的刻度很短（`tick_size=0.1`），缩略图上看不见，高分辨率抽帧确认旋转后黄色刻度随轴一起转，正常。

## 02-Axes

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `ctor` | `x_range`/`y_range`/`x_length`/`y_length`/`tips`/`axis_config` 基本构造 + `plot` 抛物线 | `02-Axes-ctor.mp4`（210 帧 / 3.50s） | `02-Axes-ctor-manimce.mp4`（210 帧 / 3.50s） | 对齐 |
| `addcoordinates` | `add_coordinates` 的 dict（x 轴 Mon/Tue）+ list（y 轴指定数值）写法 | `02-Axes-addcoordinates.mp4`（144 帧 / 2.40s） | `02-Axes-addcoordinates-manimce.mp4`（144 帧 / 2.40s） | 对齐 |

- 两对帧数全对齐；PSNR avg 37.7 / 38.2dB，无内容分歧，已抽帧目检。

## 02b-引导线与折线图

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `lines` | `get_vertical_line`/`get_lines_to_point`/`get_line_from_axis_to_point` 三件套引导线 | `02b-引导线与折线图-lines.mp4`（258 帧 / 4.30s） | `02b-引导线与折线图-lines-manimce.mp4`（258 帧 / 4.30s） | 对齐 |
| `linegraph` | `plot_line_graph` 离散折线（VDict 的 `line_graph`/`vertex_dots` 两键） | `02b-引导线与折线图-linegraph.mp4`（216 帧 / 3.60s） | `02b-引导线与折线图-linegraph-manimce.mp4`（216 帧 / 3.60s） | 对齐 |

- 两对帧数全对齐；PSNR avg 36.3 / 37.2dB，无内容分歧，RTM/CE 双端抽帧目检一致（折线与顶点圆点均正常）。

## 03-坐标换算

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `c2p_p2c` | `c2p` 数据坐标 -> 屏幕点、`p2c` 反向回读、`@` 简写 | `03-坐标换算-c2p_p2c.mp4`（234 帧 / 3.90s） | `03-坐标换算-c2p_p2c-manimce.mp4`（234 帧 / 3.90s） | 对齐 |

- 帧数对齐；PSNR avg 35.7dB（标签走 MathTex：RTM Typst vs CE LaTeX，字形抗锯齿差异，无内容分歧），RTM/CE 抽帧目检一致。

## 04-网格与复平面

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `numberplane` | `background_line_style`/`faded_line_ratio` 网格画布 | `04-网格与复平面-numberplane.mp4`（156 帧 / 2.60s） | `04-网格与复平面-numberplane-manimce.mp4`（156 帧 / 2.60s） | 对齐 |
| `complexplane` | `n2p` 复数落点 + `get_vector` 向量 + `i` 标签 | `04-网格与复平面-complexplane.mp4`（216 帧 / 3.60s） | `04-网格与复平面-complexplane-manimce.mp4`（216 帧 / 3.60s） | 对齐 |

- 两对帧数全对齐；PSNR avg 39.5 / 34.9dB（`2+i` 标签走 MathTex：RTM Typst vs CE LaTeX，字形差异属预期），RTM/CE 抽帧目检一致。

## 05-函数曲线

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `plot` | `discontinuities`/`dt` 声明间断点（错误画法 vs 正确画法） | `05-函数曲线-plot.mp4`（282 帧 / 4.70s） | `05-函数曲线-plot-manimce.mp4`（282 帧 / 4.70s） | 对齐 |
| `functiongraph` | `FunctionGraph` 余弦 vs 正弦对比 | `05-函数曲线-functiongraph.mp4`（198 帧 / 3.30s） | `05-函数曲线-functiongraph-manimce.mp4`（198 帧 / 3.30s） | 对齐 |
| `parametric` | `plot_parametric_curve` 画李萨如（`t_range` 走 `**kwargs`） | `05-函数曲线-parametric.mp4`（210 帧 / 3.50s） | `05-函数曲线-parametric-manimce.mp4`（210 帧 / 3.50s） | 对齐 |

- 三对帧数全对齐；PSNR avg 38.9 / 37.6 / 38.1dB，无内容分歧，已抽帧目检。
- **demo 侧修复记录**：`plot` 样例的 `f` 原为不加限制的 `(x²-2)/(x²-4)`——极点附近浮点算出 `±1e14` 巨值，CE 把整条路径丢掉（红曲线完全不画）、RTM 把巨值坐标画成乱码竖线墙，两端都不可用。已按 99 §四.1 把 `f` 改成 `max(-60, min(60, ...))` 钳制版（RTM/CE/md 三处同步），钳到 ±60 后错误画法的竖直连线正常可见、两端一致。RTM 对巨值坐标画成乱码墙的问题另行记录（未动渲染器）。

## 05b-曲线标注与辅助线

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `implicit` | `plot_implicit_curve` 画隐式圆 | `05b-曲线标注与辅助线-implicit.mp4`（174 帧 / 2.90s） | `05b-曲线标注与辅助线-implicit-manimce.mp4`（174 帧 / 2.90s） | 对齐 |
| `labels` | `get_graph_label` + `get_T_label` 曲线标注 | `05b-曲线标注与辅助线-labels.mp4`（210 帧 / 3.50s） | `05b-曲线标注与辅助线-labels-manimce.mp4`（210 帧 / 3.50s） | 对齐 |
| `secant` | `get_vertical_lines_to_graph` + 割线组 | `05b-曲线标注与辅助线-secant.mp4`（252 帧 / 4.20s） | `05b-曲线标注与辅助线-secant-manimce.mp4`（252 帧 / 4.20s） | 对齐 |

- 三对帧数逐条一致（ffprobe 实测 2026-10-17）；本组**未附 PSNR 数据**，本次仅用 ffprobe 核对帧数，抽帧目检另需补做。

## 05c-导数原函数与切线

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `takepoint` | `i2gp` / `i2gc` 曲线上取点 | `05c-导数原函数与切线-takepoint.mp4`（198 帧 / 3.30s） | `05c-导数原函数与切线-takepoint-manimce.mp4`（198 帧 / 3.30s） | 对齐 |
| `deriv` | `plot_derivative_graph` / `plot_antiderivative_graph` 导函数与原函数曲线 | `05c-导数原函数与切线-deriv.mp4`（240 帧 / 4.00s） | `05c-导数原函数与切线-deriv-manimce.mp4`（240 帧 / 4.00s） | 对齐 |
| `tangent` | `slope_of_tangent` + `angle_of_tangent` 动态切线 | `05c-导数原函数与切线-tangent.mp4`（240 帧 / 4.00s） | `05c-导数原函数与切线-tangent-manimce.mp4`（240 帧 / 4.00s） | 对齐 |

- 三对帧数逐条一致（ffprobe 实测 2026-10-17）；本组**未附 PSNR 数据**，本次仅用 ffprobe 核对帧数，抽帧目检另需补做。

## 06-面积与黎曼矩形

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `area` | `get_area` 曲线下方面积 | `06-面积与黎曼矩形-area.mp4`（258 帧 / 4.30s） | `06-面积与黎曼矩形-area-manimce.mp4`（258 帧 / 4.30s） | 对齐 |
| `riemann` | `get_riemann_rectangles` 黎曼和逼近 | `06-面积与黎曼矩形-riemann.mp4`（234 帧 / 3.90s） | `06-面积与黎曼矩形-riemann-manimce.mp4`（234 帧 / 3.90s） | 对齐 |

- 两对帧数逐条一致（ffprobe 实测 2026-10-17）；本组**未附 PSNR 数据**，本次仅用 ffprobe 核对帧数，抽帧目检另需补做。
- 中间产物 `RTM code/final/06-面积与黎曼矩形-*.mp4` 是拼接前的片段，成片以 `RTM output/` 为准。

## 07-极坐标与三维坐标系

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `polar` | polar | `07-极坐标与三维坐标系-polar.mp4`（198 帧 / 3.30s） | 07-极坐标与三维坐标系-polar-manimce.mp4（198 帧 / 3.30s） | ✅ |
| `surface` | surface | `07-极坐标与三维坐标系-surface.mp4`（198 帧 / 3.30s） | 07-极坐标与三维坐标系-surface-manimce.mp4（198 帧 / 3.30s） | ✅ |
| `threed` | threed | `07-极坐标与三维坐标系-threed.mp4`（198 帧 / 3.30s） | 07-极坐标与三维坐标系-threed-manimce.mp4（198 帧 / 3.30s） | ✅ |

- **验证**：3 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **`plot_surface` 的样例源已按 CE 逐参数复原**：早期 RTM 存档件与 CE 不是同源，且 RTM 渲染器扫描线填充曾逐点发射 6 顶点、整屏填充撞穿 `MAX_VERTICES` 后截断（已在 `native/draw/draw_bezier.c` 修好），复原后 `bad_frames=0`。
- **`polar` 的版式**：`PolarPlane(size=6)` 的角度标签会顶到标题/底部说明，样例改成 `size=5`、说明文字缩到 18 号并贴底——最外环与全部分数标签现在都完整可见（本轮修）。
- **`ThreeDScene` 的 `surface` 要先 `self.play = win.play`**：`move_camera` 内部会调 `self.play`，不接上镜头不动。

## 08-图表BarChart

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `basic` | 带负值的 `BarChart` + `get_bar_labels` | `08-图表BarChart-basic.mp4`（150 帧 / 2.50s） | `08-图表BarChart-basic-manimce.mp4`（150 帧 / 2.50s） | 对齐 |
| `changevalues` | `chart.animate.change_bar_values(...)` 两次就地改柱高 | `08-图表BarChart-changevalues.mp4`（234 帧 / 3.90s） | `08-图表BarChart-changevalues-manimce.mp4`（234 帧 / 3.90s） | 对齐 |

- 两对帧数一致（ffprobe 实测 2026-10-17）；`wiki_diff` 实测 `basic` `mean|diff|=0.175`、`changevalues` `0.251`，`frames>4.0` 均为 0。
- 本页 2026-10-17 补齐：此前 `RTM code/08-BarChart.py` 还是 RTM v1 旧 API（`MLVector` / `MLWindow(self,(w,h))` / `win.render()`），`import` 即 `ImportError`；已按现行 API 重写为 `08-图表BarChart.py`，并补上 CE 对照 `08-图表BarChart-manimce.py`。
- 样例刻意**不用** `Create(chart)` 出场：整套 `BarChart`（多轴 + 多柱）的 `Create` 描边揭示两引擎有亚帧差异（实测 1 帧 4.11/255 越阈，且非整帧延迟），改用 `FadeIn(chart)`；与 `07-surface` 的「填充截断」无关。
- **验证**：（核心类已实渲染验证，2026-10-11；专项 `tests/test_phase2_graphics.py:249` `test_bar_chart`；样例视频与 ManimCE 对照已补，2026-10-17）；对应 ManimCE：`BarChart`
## 09-概率与SampleSpace

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `basic` | `divide_vertically(p_list=[0.37,0.13,0.5])` + `Brace` 标签 | `09-概率与SampleSpace-basic.mp4`（192 帧 / 3.20s） | `09-概率与SampleSpace-basic-manimce.mp4`（192 帧 / 3.20s） | 对齐 |
| `horizontal` | `divide_horizontally(p_list=[0.4,0.25])`（余量自动补成 0.35） | `09-概率与SampleSpace-horizontal.mp4`（192 帧 / 3.20s） | `09-概率与SampleSpace-horizontal-manimce.mp4`（192 帧 / 3.20s） | 对齐 |

- 两对帧数一致（ffprobe 实测 2026-10-17）；`wiki_diff` 实测 `basic` `mean|diff|=0.137`、`horizontal` `0.201`，`frames>4.0` 均为 0。
- 本页 2026-10-17 补齐：旧探针 `RTM code/_probe_09.py` 还是 v1 API（`MLWindow(self,(w,h))` / `win.render()` / `sample_space.divide("horizontal","all")`），已删；新增 `09-概率与SampleSpace.py` + CE 对照 `09-概率与SampleSpace-manimce.py`。
- **顺带查实一处上游 bug**：四个「花括号 + 标签」helper（`get_side/top/bottom_braces_and_labels`、`get_subdivision_braces_and_labels`）在 manim 0.21 里**调用即崩** —— `probability.py:159` 把 `min_num_quads` 透传给 `Brace(...)`，而 0.21 的 `Brace` 已无此形参（`TypeError: Mobject.__init__ got an unexpected keyword argument 'min_num_quads'`）。样例改用 `Brace` + `get_text`，页面表格已把这四个方法标成。
- **验证**：（核心类已实渲染验证，2026-10-11；专项 `tests/test_phase2_graphics.py:256` `test_sample_space`；样例视频与 ManimCE 对照已补，2026-10-17）；对应 ManimCE：`SampleSpace`
## 10-刻度与缩放

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `logbase` | `Axes(y_axis_config={"scaling": LogBase()})` + `plot(x**2)` | `10-刻度与缩放-logbase.mp4`（174 帧 / 2.90s） | `10-刻度与缩放-logbase-manimce.mp4`（174 帧 / 2.90s） | 对齐 |
| `linearbase` | 两条 `NumberLine`：默认 vs `LinearBase(scale_factor=1.5)` | `10-刻度与缩放-linearbase.mp4`（126 帧 / 2.10s） | `10-刻度与缩放-linearbase-manimce.mp4`（126 帧 / 2.10s） | 对齐 |

- 两对帧数一致（ffprobe 实测 2026-10-17）；`wiki_diff` 实测 `logbase` `mean|diff|=0.265`、`linearbase` `0.187`，`frames>4.0` 均为 0。
- 本页 2026-10-17 补齐：`_probe_scaling.py` 是只算不渲的语义探针（保留）；新增 `10-刻度与缩放.py` + CE 对照。
- **页面 `示例` 里那行 `NumberLine(x_range=[0, 6, 1], scaling=LogBase(base=10))` 是坏的**：`x_range` 含 0 → `LogBase.inverse_function(0)` 抛 `ValueError: log(0) is undefined`；改成 `x_range=[1, 6, 1]` 虽不崩，但 manim 把刻度摆到线外（实测 `length=9` 时刻度在 x≈-6.3…-4.9、`include_numbers` 生成 0 个标签）。已把页面 `示例` 换成可用的 `Axes(y_axis_config=…)` 版本并写明这个坑。
- **验证**：（核心类已实渲染验证，2026-10-11；专项 `tests/test_phase7_remaining.py:250/258` `test_log_base_scaling` / `test_linear_base_scaling`；样例视频与 ManimCE 对照已补，2026-10-17）；对应 ManimCE：`LogBase`、`LinearBase`
## 复现

在 `assets\RTM code`（RTM 版）/ `assets\ManimCE code`（CE 版，`manimce_shim.py` 为垫片，与 04-图形与文本 同源，勿改）下：

```powershell
python 01-NumberLine.py            # RTM：全量渲染 + 拼接，成片归档到 ..\RTM output\
python 01-NumberLine.py basic      # 只渲一条，产物落 final\（全量跑才拼接）
python 01-NumberLine-manimce.py    # CE：全量 + 拼接；后跟片段名只渲一条（垫片先落 out_manimce\，交付件归档到 ..\ManimCE output\）```

- RTM 只支持 1920×1080@60；demo 里的 `MLWindow(960, 540)` 会被自动纠正并打印提示（良性）。
- PSNR 由 `ffmpeg -lavfi psnr` 逐对测得；含公式字形页面 avg ≥28~30 属正常。
