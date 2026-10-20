# 04-图形与文本

几何图形、线与箭头、多边形、标注、布尔运算、VMobject 样式，以及 Text / LaTeX / 数字 / 矩阵 / 表格 / 图片。

[首页](../README.md) ｜ [功能状态总览](../99-功能状态总览.md)

> 状态列与 [98-功能清单](../98-功能清单.md) 第 5 节一致：= 核心类已实渲染验证（2026-10-11 实渲染，2026-10-16 复跑全绿）；部分验证 = 核心类已验证、次要类未单独出片。

> **2026-10-17 更新**：修正了 01/01b/02/03/03b/06/07/07b/10/12 各页的**路由与出片证据**——`ArcBetweenPoints`/`TangentialArc`/`CurvedArrow`/`CurvedDoubleArrow`（`Arc` 子类）、`TangentLine`/`Vector`/`DoubleArrow`、`AnnotationDot`/`LabeledDot`、`Star` 均走**原生**发送器（`_send_arc`/`_send_line`/`_send_arrow`/`_send_dot`/`_send_polygon`），不再是"通用 bezier 回退"；并补齐各页对应的专项测试编号。

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01b-基本形状进阶](01b-基本形状进阶.md) | 基本形状（二）：标注点、扇环与自由曲线 | （已渲染：`Ellipse`；`AnnotationDot` / `LabeledDot` 是 `Dot` 子类走原生 `_send_dot`（`paint.py:914`），随 dots_ellipse 样例出片；扇环家族是 `Arc` 子类走原生 `_send_arc`，随 sectors 样例出片；专项 `tests/test_dot_with_label.py`、`tests/test_arc_fill.py`、`tests/test_passing_flash_and_fill.py`） |
| [01-基本形状](01-基本形状.md) | 基本形状（一）：圆弧、圆与点 | （已渲染：`Arc` / `Circle` / `Dot`；`ArcBetweenPoints` / `TangentialArc` / `CurvedArrow` / `CurvedDoubleArrow` 都是 `Arc` 子类（`arc.py:446/505/597/608`），走原生 `_send_arc`（`paint.py:998`），随 `01-基本形状-arc.mp4` / `-curved.mp4` 出片） |
| [02b-箭头尖端](02b-箭头尖端.md) | 线与箭头（二）：尖端基类与箭头形状 | （已渲染：尖端基类与七种箭头形状；CE 侧无对照件） |
| [02-线与箭头](02-线与箭头.md) | 线与箭头（一）：线段、虚线与箭头 | （已渲染：`Line` / `DashedLine` / `Arrow`；`TangentLine(Line)` 走原生 `_send_line`（`paint.py:996`）、`Vector` / `DoubleArrow(Arrow)` 走原生 `_send_arrow`（`paint.py:967`），随 `-lines.mp4` / `-arrows.mp4` 出片，`DoubleArrow` 另有专项 `tests/test_double_arrow.py`；仅 `Elbow(VMobject)` 落通用回退，同样随 lines 样例出片） |
| [03b-矩形与特殊多边形](03b-矩形与特殊多边形.md) | 多边形与星形（二）：矩形与特殊多边形 | 部分验证：`Rectangle` / `Square` 已渲染；`RoundedRectangle` 有专项 `tests/test_quad_dispatch.py:173`（刻意走通用镶嵌，是设计不是未验证）；`Cutout` / `ConvexHull` 未单独出片 |
| [03-多边形与星形](03-多边形与星形.md) | 多边形与星形（一）：Polygram 家族 | 部分验证：`Polygram` / `Polygon` / `Triangle` / `Star` 渲染已验证；`Star(Polygon)`（`polygram.py:465`）走原生 `_send_polygon`（`paint.py:1036`），专项断言 `tests/test_polygram_groups.py:195`；`RegularPolygon` / `RegularPolygram` / `round_corners` 随本页样例出图。**两条样例（`polygons` 267 帧 / `stars_round` 306 帧）已于 2026-10-17 出图 + 补上 ManimCE 对照**（`mean\|diff\|` 0.489 / 0.844，`frames>4.0` 均 0） |
| [04b-带标签标注](04b-带标签标注.md) | 角度与标注框（二）：带标签的标注 | （已渲染） |
| [04-角度与标注框](04-角度与标注框.md) | 角度与标注框（一）：角度与高亮框 | （已渲染） |
| [05-布尔运算](05-布尔运算.md) | 布尔运算 | （已渲染：`Union`，其余三运算同一条链路） |
| [06-容器与组合](06-容器与组合.md) | 容器 VGroup 与组合 | 部分验证：`VGroup` 已渲染（按子对象路由）；`VDict` 有专项 `tests/test_dot_with_label.py`、`tests/test_point_bearing_container.py`，并已随 05 章 `02b-引导线与折线图-linegraph.mp4` 出片；`DashedVMobject` / `VectorizedPoint` / `CurvesAsSubmobjects` 未单独出片 |
| [07b-VMobject样式进阶](07b-VMobject样式进阶.md) | VMobject 样式（二）：透明度、光泽与路径处理 | 部分验证：`set_opacity` 已渲染；`set_sheen` / 多 stop 渐变填充有专项 `tests/test_gradient_fill_stops.py`，`pointwise_become_partial` 有 3 项专项（`tests/test_open_path_chord.py:43`、`tests/test_quad_dispatch.py:211`、`tests/test_render_hooks.py:299`），`apply_function` 有专项 `tests/test_gap_transform_motion.py:318`；`make_smooth` / `make_jagged` / `get_stroke_width` / `set_cap_style` / `change_anchor_mode` 未单独出片 |
| [07-VMobject样式](07-VMobject样式.md) | VMobject 样式（一）：填充、描边与整体样式 | 部分验证：`set_fill` / `set_stroke` / `set_color` 已渲染（引擎原生样式通道）；`set_style` （仅 `background_image` 纹理填充 RTM 不生效，sheen / 多色填充已支持） |
| [08-文本Text](08-文本Text.md) | 文本 Text | 部分验证：`Text`（TrueType 逐字符）/ `MarkupText` / `Paragraph` 已渲染；`register_font`、`remove_invisible_chars` 未单独出片 |
| [09b-片段方法与列表](09b-片段方法与列表.md) | MathTex 片段方法与列表、标题 | （已渲染） |
| [09-LaTeX公式](09-LaTeX公式.md) | LaTeX 公式：MathTex / Tex | 部分验证：`MathTex` / `Tex` 已渲染（RTM 默认真 LaTeX 且有 LaTeX 缓存，另有 Unicode 原生模式）；基类与片段方法未单独出片 |
| [10-Typst](10-Typst.md) | Typst 排版 | 已支持（`Typst`/`TypstMath` 直用 + `MathTex` 自动路由，条件：装了 `real-time-manim[typst]` extra 且未设 `RTM_TYPST=0`，否则 `MathTex` 仍是真实 LaTeX；失败回退 LaTeX） |
| [11-代码块](11-代码块.md) | 代码块 | （已渲染：`Code`；RTM 无语法高亮专属路径，走文本渲染） |
| [12-数字与变量](12-数字与变量.md) | 数字与变量 | （已渲染：`DecimalNumber` / `Integer` / `Variable`，专项 `tests/test_phase2_graphics.py:121,128,135`；另提供 RTM 新增的 `TextDecimalNumber`（`animations/text.py:9`，基于 Text 渲染、无需 LaTeX）供选择） |
| [13-矩阵](13-矩阵.md) | 矩阵 | （已渲染：`Matrix`，括号走 LaTeX、元素默认 MathTex） |
| [14b-表格方法](14b-表格方法.md) | 表格方法：取格、高亮与逐步生成 | （已渲染） |
| [14-表格](14-表格.md) | 表格 | （已渲染） |
| [15-图片与SVG](15-图片与SVG.md) | 图片与 SVG | （已渲染：`ImageMObject` 原生贴图路径、`SVGMobject`） |
| [16-花括号标注](16-花括号标注.md) | 花括号标注 | （已渲染：`Brace` / `BraceLabel`） |

