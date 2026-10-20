# 08-工具 样例视频（RTM / ManimCE 对照）

这些视频都由 `RTM code/`（RTM 版）与 `ManimCE code/`（CE 对照版）下的源码渲染，页面只引用 **RTM** 那一版；
带 `-manimce` 的是同一份代码用 ManimCE 渲的，留着自己对比，不进页面。

本目录是**速查类目录**：每页只挑最有可视性的一组做 2~4 条样例，其余纯函数 / 常量保留在参数表里，并在页尾"无法演示"行归总说明。

## 01-颜色

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `parse` | 五种 `value` 形式 + `to_hex` + `alpha` | `01-颜色-parse.mp4`（138 帧 / 2.30s） | `01-颜色-parse-manimce.mp4`（138 帧 / 2.30s） | 对齐 |
| `depth` | `darker` / `lighter` 同色系深浅五档 | `01-颜色-depth.mp4`（138 帧 / 2.30s） | `01-颜色-depth-manimce.mp4`（138 帧 / 2.30s） | 对齐 |
| `gradient` | `color_gradient` 同组参考色 × 两种 `length_of_output` | `01-颜色-gradient.mp4`（138 帧 / 2.30s） | `01-颜色-gradient-manimce.mp4`（138 帧 / 2.30s） | 对齐 |

- 三对逐帧同貌：PSNR 平均 36.5~38.3dB、最低帧 35.6~36.6dB（差异为文字抗锯齿量级）。

## 01b-颜色进阶

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `interpolate` | `RED → BLUE` 九档插值带 + `interpolate_color` 等价 | `01b-颜色进阶-interpolate.mp4`（168 帧 / 2.80s） | `01b-颜色进阶-interpolate-manimce.mp4`（168 帧 / 2.80s） | 对齐 |
| `helpers` | 平均 / 随机 / 亮随机取色 + `invert` / `opacity` / `contrasting` | `01b-颜色进阶-helpers.mp4`（174 帧 / 2.90s） | `01b-颜色进阶-helpers-manimce.mp4`（174 帧 / 2.90s） | 对齐 |

- 两对帧数全对齐；PSNR 平均 34.2~34.5dB、最低帧 30.4~33.3dB——差异来自 `Write` 逐字进度与小字抗锯齿（RTM/CE 各自排版同一 Pango 文本），抽帧逐画面比对**内容完全同貌**（六格 `to_hex` 标签、两引擎逐位一致）。
- `helpers` 里两处 `random_color()` / `random_bright_color()` 先 `random.seed(7)` 固定，否则两引擎各抽各的色、无法对比。

## 02-速率函数

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `curves_common` | `linear` / `smooth` / `rush_into` / `rush_from` 四条曲线 | `02-速率函数-curves_common.mp4`（282 帧 / 4.70s） | `02-速率函数-curves_common-manimce.mp4`（282 帧 / 4.70s） | 对齐 |
| `curves_factory` | `squish` / `wiggle` / `lingering` / `ease_out_bounce` 四条曲线 | `02-速率函数-curves_factory.mp4`（282 帧 / 4.70s） | `02-速率函数-curves_factory-manimce.mp4`（282 帧 / 4.70s） | 对齐 |
| `motion` | 同一条位移 × 四种 `rate_func` 四泳道齐跑 | `02-速率函数-motion.mp4`（192 帧 / 3.20s） | `02-速率函数-motion-manimce.mp4`（192 帧 / 3.20s） | 对齐 |

- 三对帧数全对齐；PSNR 平均 40.7~42.2dB、最低帧 34.8~35.5dB。曲线均为 `FunctionGraph` 逐点采样（标量 mapper 定义在 `construct` 内，与页面代码块逐字一致），两引擎同一套 manim 速率函数实现，抽帧比对曲线形态、图例、泳道点位逐帧同貌（`motion` 末帧 `there_and_back` 的点已折返回起点）。

## 03-方向与常量

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `directions` | 八方向箭头 + 对角构造 + `ORIGIN` 标注 | `03-方向与常量-directions.mp4`（306 帧 / 5.10s） | `03-方向与常量-directions-manimce.mp4`（306 帧 / 5.10s） | 对齐 |
| `compass_math` | `compass_directions(8)` 圆周等分 + `TAU` / `PI` / `45 * DEGREES` 三弧 | `03-方向与常量-compass_math.mp4`（240 帧 / 4.00s） | `03-方向与常量-compass_math-manimce.mp4`（240 帧 / 4.00s） | 对齐 |

- 两对帧数全对齐；PSNR 平均 40.9~42.4dB、最低帧 34.8~35.6dB。方向常量与 `compass_directions` 都是同一份 manim 常量模块逐位复用，抽帧比对圆周 8 点分布、四色弧段、图例文字逐帧同貌。

## 04-向量与几何工具

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `rotate` | 同一向量转 45° 与 90°（`rotate_vector` 两角弧） | `04-向量与几何工具-rotate.mp4`（213 帧 / 3.55s） | `04-向量与几何工具-rotate-manimce.mp4`（213 帧 / 3.55s） | 对齐 |
| `angle_centroid` | 两向量夹角（`angle_of_vector` 摆角弧）+ 四边形质心/中点 | `04-向量与几何工具-angle_centroid.mp4`（267 帧 / 4.45s） | `04-向量与几何工具-angle_centroid-manimce.mp4`（267 帧 / 4.45s） | 对齐 |
| `polygon` | `regular_vertices` 正五边形 + 顺时针正方形的 `shoelace` 面积 | `04-向量与几何工具-polygon.mp4`（243 帧 / 4.05s） | `04-向量与几何工具-polygon-manimce.mp4`（243 帧 / 4.05s） | 对齐 |

- 三对帧数全对齐；PSNR（480×270、n=60 采样）avg 42.5~45.9dB、最低帧 38.1~39.8dB——差异为文字与角弧的抗锯齿量级，两引擎共用同一份 `space_ops` 实现。
- 抽帧拼图（QA 留档，不进页面）：`tile-08-04-向量与几何工具-rotate.png`、`-angle_centroid.png`、`-polygon.png`、`-polygon-ce.png`。

## 04b-路径与序列工具

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `paths` | 同一条弦的三条变换轨迹：`path_along_arc(±TAU/2)` vs 默认直线 | `04b-路径与序列工具-paths.mp4`（273 帧 / 4.55s） | `04b-路径与序列工具-paths-manimce.mp4`（273 帧 / 4.55s） | 对齐 |
| `iterables` | `adjacent_pairs` 闭合连四边 + `choose` / `clip` / `sigmoid` 取值 | `04b-路径与序列工具-iterables.mp4`（237 帧 / 3.95s） | `04b-路径与序列工具-iterables-manimce.mp4`（237 帧 / 3.95s） | 对齐 |

- 两对帧数全对齐；PSNR（480×270、n=60 采样）avg 45.1~46.0dB、最低帧 38.9~39.8dB——轨迹曲线与文字的抗锯齿量级差异。
- 抽帧拼图（QA 留档，不进页面）：`tile-08-04b-路径与序列工具-paths.png`、`-paths-ce.png`、`-iterables.png`。
