# 04-图形与文本 样例视频（RTM / ManimCE 对照）

本目录的成片由 `RTM code/` 与 `ManimCE code/` 下的同源脚本渲染：页面只引用
**RTM** 那一版（`RTM output/`），带 `-manimce` 的是同一份类代码用 ManimCE 渲的
对照件（`ManimCE output/`），仅供比对，不进页面。

## 01-基本形状

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `arc` | arc | `01-基本形状-arc.mp4`（294 帧 / 4.90s） | 01-基本形状-arc-manimce.mp4（294 帧 / 4.90s） | 对齐 |
| `circle_dot` | circle_dot | `01-基本形状-circle_dot.mp4`（270 帧 / 4.50s） | 01-基本形状-circle_dot-manimce.mp4（270 帧 / 4.50s） | 对齐 |
| `curved` | curved | `01-基本形状-curved.mp4`（210 帧 / 3.50s） | 01-基本形状-curved-manimce.mp4（210 帧 / 3.50s） | 对齐 |

## 01b-基本形状进阶

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `dots_ellipse` | dots_ellipse | `01b-基本形状进阶-dots_ellipse.mp4`（282 帧 / 4.70s） | 01b-基本形状进阶-dots_ellipse-manimce.mp4（282 帧 / 4.70s） | 对齐 |
| `sectors` | sectors | `01b-基本形状进阶-sectors.mp4`（312 帧 / 5.20s） | 01b-基本形状进阶-sectors-manimce.mp4（312 帧 / 5.20s） | 对齐 |

## 02-线与箭头

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `arrows` | arrows | `02-线与箭头-arrows.mp4`（294 帧 / 4.90s） | 02-线与箭头-arrows-manimce.mp4（294 帧 / 4.90s） | 对齐 |
| `lines` | lines | `02-线与箭头-lines.mp4`（288 帧 / 4.80s） | 02-线与箭头-lines-manimce.mp4（288 帧 / 4.80s） | 对齐 |

## 02b-箭头尖端

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `tip_shapes` | tip_shapes | `02b-箭头尖端-tip_shapes.mp4`（255 帧 / 4.25s） | —（CE 侧无对照件） | — |
| `tips_base` | tips_base | `02b-箭头尖端-tips_base.mp4`（354 帧 / 5.90s） | —（CE 侧无对照件） | — |

## 03-多边形与星形

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `polygons` | polygons | `03-多边形与星形-polygons.mp4`（267 帧 / 4.45s） | 03-多边形与星形-polygons-manimce.mp4（267 帧 / 4.45s） | 对齐 |
| `stars_round` | stars_round | `03-多边形与星形-stars_round.mp4`（306 帧 / 5.10s） | 03-多边形与星形-stars_round-manimce.mp4（306 帧 / 5.10s） | 对齐 |

## 03b-矩形与特殊多边形

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `rectangle` | rectangle | `03b-矩形与特殊多边形-rectangle.mp4`（162 帧 / 2.70s） | 03b-矩形与特殊多边形-rectangle-manimce.mp4（162 帧 / 2.70s） | 对齐 |
| `square` | square | `03b-矩形与特殊多边形-square.mp4`（168 帧 / 2.80s） | 03b-矩形与特殊多边形-square-manimce.mp4（168 帧 / 2.80s） | 对齐 |
| `rounded` | rounded | `03b-矩形与特殊多边形-rounded.mp4`（126 帧 / 2.10s） | 03b-矩形与特殊多边形-rounded-manimce.mp4（126 帧 / 2.10s） | 对齐 |
| `cutout` | cutout | `03b-矩形与特殊多边形-cutout.mp4`（132 帧 / 2.20s） | 03b-矩形与特殊多边形-cutout-manimce.mp4（132 帧 / 2.20s） | 对齐 |
| `convexhull` | convexhull | `03b-矩形与特殊多边形-convexhull.mp4`（132 帧 / 2.20s） | 03b-矩形与特殊多边形-convexhull-manimce.mp4（132 帧 / 2.20s） | 对齐 |

- **验证**：对应 ManimCE 类 `Rectangle`、`Square`、`RoundedRectangle`、`Cutout`、`ConvexHull`；五条帧数逐条对齐，全库逐帧对拍 `bad_frames=0`（mean 0.11–0.24）。
- `convexhull` 一节刻意用 `FadeIn(hull)` 而不是 `Create(hull)`：`ConvexHull` 的**描边揭示**两引擎有亚帧差异（`Create` 时实测 2 帧越阈 4.0/255，且非整帧延迟），换成淡入即归零——同 `08-图表BarChart` 的处理。
- `cutout` 一节把"孔是否真的镂空"如实写进页面提醒：孔只给描边（`fill_opacity=0`）时主形状填充会盖过孔的内部，两引擎实测一致。

## 04-角度与标注框

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `angle` | angle | `04-角度与标注框-angle.mp4`（276 帧 / 4.60s） | 04-角度与标注框-angle-manimce.mp4（276 帧 / 4.60s） | 对齐 |
| `angle3p` | angle3p | `04-角度与标注框-angle3p.mp4`（126 帧 / 2.10s） | 04-角度与标注框-angle3p-manimce.mp4（126 帧 / 2.10s） | 对齐 |
| `rightangle` | rightangle | `04-角度与标注框-rightangle.mp4`（150 帧 / 2.50s） | 04-角度与标注框-rightangle-manimce.mp4（150 帧 / 2.50s） | 对齐 |
| `surrounding` | surrounding | `04-角度与标注框-surrounding.mp4`（222 帧 / 3.70s） | 04-角度与标注框-surrounding-manimce.mp4（222 帧 / 3.70s） | 对齐 |
| `background` | background | `04-角度与标注框-background.mp4`（204 帧 / 3.40s） | 04-角度与标注框-background-manimce.mp4（204 帧 / 3.40s） | 对齐 |
| `cross` | cross | `04-角度与标注框-cross.mp4`（276 帧 / 4.60s） | 04-角度与标注框-cross-manimce.mp4（276 帧 / 4.60s） | 对齐 |

- **验证**：对应 ManimCE 类 `Angle`（含 `from_three_points`）、`RightAngle`、`SurroundingRectangle`、`BackgroundRectangle`、`Cross`、`Underline`；六条帧数逐条对齐，逐帧对拍 `bad_frames=0`（mean 0.13–0.35）。
- **上游 bug**：`Angle.get_value(degrees=...)` 在 ManimCE 0.21 是坏的——`Angle.__init__` 不写 `self.angle_value`，读它抛 `AttributeError: Angle object has no attribute 'angle_value'`，**两引擎同崩**（外置 ManimCE 0.21.0 实测同错）。样例用两条边 `get_angle` 之差读同一个数值，页面参数表已把该方法标为不支持并写明原因。
- `Cross`/`Underline` 合成一条视频（两者都是"否定"标注、同属 `shape_matchers`），其余每个函数各一条。

## 07b-VMobject样式进阶

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `opacity` | opacity | `07b-VMobject样式进阶-opacity.mp4`（201 帧 / 3.35s） | 07b-VMobject样式进阶-opacity-manimce.mp4（201 帧 / 3.35s） | 对齐 |
| `sheen` | sheen | `07b-VMobject样式进阶-sheen.mp4`（201 帧 / 3.35s） | 07b-VMobject样式进阶-sheen-manimce.mp4（201 帧 / 3.35s） | 对齐 |
| `smooth` | smooth | `07b-VMobject样式进阶-smooth.mp4`（132 帧 / 2.20s） | 07b-VMobject样式进阶-smooth-manimce.mp4（132 帧 / 2.20s） | 对齐 |
| `jagged` | jagged | `07b-VMobject样式进阶-jagged.mp4`（132 帧 / 2.20s） | 07b-VMobject样式进阶-jagged-manimce.mp4（132 帧 / 2.20s） | 对齐 |
| `partial` | partial | `07b-VMobject样式进阶-partial.mp4`（198 帧 / 3.30s） | 07b-VMobject样式进阶-partial-manimce.mp4（198 帧 / 3.30s） | 对齐 |
| `strokewidth` | strokewidth | `07b-VMobject样式进阶-strokewidth.mp4`（156 帧 / 2.60s） | 07b-VMobject样式进阶-strokewidth-manimce.mp4（156 帧 / 2.60s） | 对齐 |
| `capstyle` | capstyle | `07b-VMobject样式进阶-capstyle.mp4`（150 帧 / 2.50s） | 07b-VMobject样式进阶-capstyle-manimce.mp4（150 帧 / 2.50s） | 对齐 |
| `anchor` | anchor | `07b-VMobject样式进阶-anchor.mp4`（132 帧 / 2.20s） | 07b-VMobject样式进阶-anchor-manimce.mp4（132 帧 / 2.20s） | 对齐 |
| `applyfunc` | applyfunc | `07b-VMobject样式进阶-applyfunc.mp4`（180 帧 / 3.00s） | 07b-VMobject样式进阶-applyfunc-manimce.mp4（180 帧 / 3.00s） | 对齐 |

- **验证**：九个方法（`set_opacity` / `set_sheen`+`set_sheen_direction` / `make_smooth` / `make_jagged` / `pointwise_become_partial` / `get_stroke_width` / `set_cap_style` / `change_anchor_mode` / `apply_function`）各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`（mean 0.14–0.40）。
- **上游 bug（`apply_function` 的参考点）**：ManimCE 0.21 的 `apply_function(function, about_point=…, about_edge=…)` **不读** `about_point` / `about_edge`——实测四种写法（不传 / `about_point=ORIGIN` / `about_point=自身中心` / `about_edge=UP`）最终几何完全一样（中心都是 `p*1.5` 的绝对结果）；RTM 会按参考点变换，所以这两条**两引擎画面不同**，样例不演示，页面参数表已标为不支持并写明。想按参考点变换就自己写进函数里（如 `center + (p - center) * 1.5`）。
- `set_cap_style` / `set_sheen` 是 RTM 已完整接线的（`CapStyleType.ROUND/BUTT/SQUARE` 三种端点、方向渐变逐帧一致），样例用粗线 40px 才看得出端点差异。


## 09b-片段方法与列表

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `bulletedlist` | bulletedlist | `09b-片段方法与列表-bulletedlist.mp4`（228 帧 / 3.80s） | 09b-片段方法与列表-bulletedlist-manimce.mp4（228 帧 / 3.80s） | ✅ |
| `colorbytex` | colorbytex | `09b-片段方法与列表-colorbytex.mp4`（204 帧 / 3.40s） | 09b-片段方法与列表-colorbytex-manimce.mp4（204 帧 / 3.40s） | ✅ |
| `colormap` | colormap | `09b-片段方法与列表-colormap.mp4`（132 帧 / 2.20s） | 09b-片段方法与列表-colormap-manimce.mp4（132 帧 / 2.20s） | ✅ |
| `getpart` | getpart | `09b-片段方法与列表-getpart.mp4`（198 帧 / 3.30s） | 09b-片段方法与列表-getpart-manimce.mp4（198 帧 / 3.30s） | ✅ |
| `opacitybytex` | opacitybytex | `09b-片段方法与列表-opacitybytex.mp4`（168 帧 / 2.80s） | 09b-片段方法与列表-opacitybytex-manimce.mp4（168 帧 / 2.80s） | ✅ |
| `parts` | parts | `09b-片段方法与列表-parts.mp4`（144 帧 / 2.40s） | 09b-片段方法与列表-parts-manimce.mp4（144 帧 / 2.40s） | ✅ |
| `title` | title | `09b-片段方法与列表-title.mp4`（240 帧 / 4.00s） | 09b-片段方法与列表-title-manimce.mp4（240 帧 / 4.00s） | ✅ |

- **验证**：7 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **片段拆分前提**：`{{ }}` 只对同一个字符串参数内部生效——`MathTex("{{x}}^2+{{y}}^2={{z}}^2")` 实测只拆成 `x` 与 `^2+{{y}}^2={{z}}^2` 两片（两引擎一致），页面已改成每片一个参数的写法；`get_part_by_tex` 找不到时返回 `None`（不是抛错）。
- **`BulletedList.fade_all_but` 只吃下标**：传字符串一律抛 `Could not locate part by provided tex string`（条目 `tex_string` 带结尾 `\\`，纯文本/`\item x` 都匹配不上），**两引擎一致**；样例只演示下标形式。
- **`Title` 那条样例不再有黄色页眉标签**：`Title` 本身就是"贴画面顶部的页眉"，样例里再叠一行黄色标题会打架，已去掉（2026-10-21）。

## 13-矩阵

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `decimal` | decimal | `13-矩阵-decimal.mp4`（213 帧 / 3.55s） | 13-矩阵-decimal-manimce.mp4（213 帧 / 3.55s） | ✅ |
| `dettext` | dettext | `13-矩阵-dettext.mp4`（168 帧 / 2.80s） | 13-矩阵-dettext-manimce.mp4（168 帧 / 2.80s） | ✅ |
| `integer` | integer | `13-矩阵-integer.mp4`（162 帧 / 2.70s） | 13-矩阵-integer-manimce.mp4（162 帧 / 2.70s） | ✅ |
| `matrix` | matrix | `13-矩阵-matrix.mp4`（888 帧 / 14.80s） | 13-矩阵-matrix-manimce.mp4（888 帧 / 14.80s） | ✅ |
| `mobject` | mobject | `13-矩阵-mobject.mp4`（168 帧 / 2.80s） | 13-矩阵-mobject-manimce.mp4（168 帧 / 2.80s） | ✅ |
| `texmob` | texmob | `13-矩阵-texmob.mp4`（144 帧 / 2.40s） | 13-矩阵-texmob-manimce.mp4（144 帧 / 2.40s） | ✅ |
| `texstr` | texstr | `13-矩阵-texstr.mp4`（120 帧 / 2.00s） | 13-矩阵-texstr-manimce.mp4（120 帧 / 2.00s） | ✅ |

- **验证**：7 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **`font_size` 不是矩阵参数**：`Matrix(..., font_size=40)` 抛 `TypeError: Mobject.__init__() got an unexpected keyword argument 'font_size'`（`**kwargs` 落到 `Mobject`）；元素字号要走 `element_to_mobject_config={"font_size": …}`，页面顶部已写明。
- **数字元素不能换 `Text`/`MathTex`**：`DecimalMatrix(..., element_to_mobject=Text)` 渲染时执行 `Text(1.2)`，抛 `AttributeError: 'int' object has no attribute 'find'`（数字元素要用 `DecimalNumber`/`Integer`）；样例里小数/整数矩阵分别用 `Integer`、`DecimalNumber` 演示这一条。
- **逐段演示不叠图**：`Matrix` 那条的 12 个参数段共用同一个 `show()`，每段先淡出上一段的矩阵与字幕，画面上始终只有一个矩阵——这也是本次重叠修复后的版式。

## 04b-带标签标注

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `label` | label | `04b-带标签标注-label.mp4`（204 帧 / 3.40s） | 04b-带标签标注-label-manimce.mp4（204 帧 / 3.40s） | 对齐 |
| `labeledarrow` | labeledarrow | `04b-带标签标注-labeledarrow.mp4`（162 帧 / 2.70s） | 04b-带标签标注-labeledarrow-manimce.mp4（162 帧 / 2.70s） | 对齐 |
| `labeledline` | labeledline | `04b-带标签标注-labeledline.mp4`（216 帧 / 3.60s） | 04b-带标签标注-labeledline-manimce.mp4（216 帧 / 3.60s） | 对齐 |
| `labeledpoly` | labeledpoly | `04b-带标签标注-labeledpoly.mp4`（204 帧 / 3.40s） | 04b-带标签标注-labeledpoly-manimce.mp4（204 帧 / 3.40s） | 对齐 |

- **验证**：4 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **顶点组要按"整圈"给**：`LabeledPolygram(v1, v2, v3, label=…)` 抛 `IndexError: too many indices for array: array is 1-dimensional, but 2 were indexed`（每个位置参数被当成一圈），正确写法是 `LabeledPolygram([v1, v2, v3], label=…)`；开口环会自动闭合，多个环一起传时只有一个标签（落在面积最大的那块）。
- **配置字典只对字符串标签生效**：`label` 传现成 `Text`/`MathTex` 时 `label_config`/`box_config`/`frame_config` 被忽略，样式以对象自身为准（样例第一条最后一块演示）。

## 16-花括号标注

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `arcbrace` | arcbrace | `16-花括号标注-arcbrace.mp4`（216 帧 / 3.60s） | 16-花括号标注-arcbrace-manimce.mp4（216 帧 / 3.60s） | ✅ |
| `brace` | brace | `16-花括号标注-brace.mp4`（375 帧 / 6.25s） | 16-花括号标注-brace-manimce.mp4（375 帧 / 6.25s） | ✅ |
| `bracebetween` | bracebetween | `16-花括号标注-bracebetween.mp4`（204 帧 / 3.40s） | 16-花括号标注-bracebetween-manimce.mp4（204 帧 / 3.40s） | ✅ |
| `bracelabel` | bracelabel | `16-花括号标注-bracelabel.mp4`（192 帧 / 3.20s） | 16-花括号标注-bracelabel-manimce.mp4（192 帧 / 3.20s） | ✅ |
| `bracetext` | bracetext | `16-花括号标注-bracetext.mp4`（216 帧 / 3.60s） | 16-花括号标注-bracetext-manimce.mp4（216 帧 / 3.60s） | ✅ |

- **验证**：5 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **`get_text` / `get_tex` 的 kwargs 只喂给 `put_at_tip`**：`Brace.get_text("x", font_size=20)` 抛 `TypeError: Mobject.next_to() got an unexpected keyword argument 'font_size'`（**实测 RTM 与 ManimCE 0.21 一致**）；字号/颜色要取回对象后再设（`lbl = br.get_text("x"); lbl.scale(0.6).set_color(GREY)`），只有 `buff` 这类 `next_to` 的参数能直接传，样例已按此写法。
- **`Brace` 的 `sharpness` 太小会变钝**：样例用 `sharpness=6` 与默认 2 对比；`stroke_width` 与 `background_stroke_width/Color` 分别是内圈与外圈两层描边，可以叠出双色效果。

## 15-图片与SVG

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `abstractimage` | abstractimage | `15-图片与SVG-abstractimage.mp4`（138 帧 / 2.30s） | 15-图片与SVG-abstractimage-manimce.mp4（138 帧 / 2.30s） | 对齐 |
| `image` | image | `15-图片与SVG-image.mp4`（198 帧 / 3.30s） | 15-图片与SVG-image-manimce.mp4（198 帧 / 3.30s） | 对齐 |
| `imagefromcamera` | imagefromcamera | `15-图片与SVG-imagefromcamera.mp4`（162 帧 / 2.70s） | 15-图片与SVG-imagefromcamera-manimce.mp4（162 帧 / 2.70s） | 对齐 |
| `svg` | svg | `15-图片与SVG-svg.mp4`（276 帧 / 4.60s） | 15-图片与SVG-svg-manimce.mp4（276 帧 / 4.60s） | 对齐 |
| `svgpath` | svgpath | `15-图片与SVG-svgpath.mp4`（228 帧 / 3.80s） | 15-图片与SVG-svgpath-manimce.mp4（228 帧 / 3.80s） | 对齐 |

- **验证**：5 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **类名是 `ImageMobject`（小写 m）**：`ImageMObject` 这个名字在两引擎里都不存在（ManimCE 0.21 同样是 `ImageMobject`）；`real_time_manim` 顶层导出 `ImageMobject` / `ImageMobjectFromCamera` / `SVGMobject` / `VMobjectFromSVGPath` / `Camera`，但 `AbstractImageMobject` 不在顶层，要从 `manim.mobject.types.image_mobject` 导入。
- **`svg_default` 是整份样式表**：`SVGMobject(..., svg_default={"fill": RED})` 抛 `KeyError: 'color'`（键要齐全：`color`/`fill_color`/`fill_opacity`/`stroke_color`/`stroke_opacity`/`stroke_width`/`opacity`）；样例里给了完整字典，日常更推荐用 `fill_color`/`stroke_color` 这些参数。
- **`VMobjectFromSVGPath` 不吃字符串**：`VMobjectFromSVGPath("M 0 0 L 2 0 L 2 2 Z")` 抛 `AttributeError: 'str' object has no attribute 'approximate_arcs_with_quads'`（两引擎一致），要先用 `svgelements` 解析成 `se.Path`；页面表格已改成 `svgelements.Path`。
- **`ImageMobjectFromCamera` 要先拍照**：`self.camera.capture_mobject(...)` 把画面写进 `camera.pixel_array` 后再构造，否则是一张空图；样例同一张快照做了"构造时给外框"与"事后 `add_display_frame`"两种。

## 05-布尔运算

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `difference` | difference | `05-布尔运算-difference.mp4`（216 帧 / 3.60s） | 05-布尔运算-difference-manimce.mp4（216 帧 / 3.60s） | 对齐 |
| `exclusion` | exclusion | `05-布尔运算-exclusion.mp4`（174 帧 / 2.90s） | 05-布尔运算-exclusion-manimce.mp4（174 帧 / 2.90s） | 对齐 |
| `intersection` | intersection | `05-布尔运算-intersection.mp4`（234 帧 / 3.90s） | 05-布尔运算-intersection-manimce.mp4（234 帧 / 3.90s） | 对齐 |
| `union` | union | `05-布尔运算-union.mp4`（246 帧 / 4.10s） | 05-布尔运算-union-manimce.mp4（246 帧 / 4.10s） | 对齐 |

- **验证**：4 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **四个函数都返回新对象**：`Union`/`Difference`/`Intersection`/`Exclusion` 的结果都是全新 `VMobject`，输入形状不受影响（样例里每次都把原 `a`/`b` 摆出来对照）；样式 `**kwargs` 直接作用在返回值上。
- **`Difference` 的减法有方向**：`Difference(圆, 方块)` 与 `Difference(方块, 圆)` 结果不同；把 `clip` 完全放进 `subject` 内部就得到圆环（内部挖空）。
- **不相交的 `Intersection` 是空结果**：完全分开的两块图形求交得到空对象，屏幕上没有新形状属正常（样例右下专门演示）。

## 06-容器与组合

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `curves` | curves | `06-容器与组合-curves.mp4`（210 帧 / 3.50s） | 06-容器与组合-curves-manimce.mp4（210 帧 / 3.50s） | ✅ |
| `dashed` | dashed | `06-容器与组合-dashed.mp4`（288 帧 / 4.80s） | 06-容器与组合-dashed-manimce.mp4（288 帧 / 4.80s） | ✅ |
| `vdict` | vdict | `06-容器与组合-vdict.mp4`（246 帧 / 4.10s） | 06-容器与组合-vdict-manimce.mp4（246 帧 / 4.10s） | ✅ |
| `vgroup` | vgroup | `06-容器与组合-vgroup.mp4`（270 帧 / 4.50s） | 06-容器与组合-vgroup-manimce.mp4（270 帧 / 4.50s） | ✅ |
| `vpoint` | vpoint | `06-容器与组合-vpoint.mp4`（234 帧 / 3.90s） | 06-容器与组合-vpoint-manimce.mp4（234 帧 / 3.90s） | ✅ |

- **验证**：5 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **`VGroup` 只装矢量对象**：`VGroup(Circle(), ImageMobject(...))` 与 `VGroup(...).add(ImageMobject(...))` 都抛 `TypeError: Only values of type VMobject can be added as submobjects of ...`（**两引擎一致**），要混装图片用 `Group`（`Group(Circle(), ImageMobject())` 正常，`len=2`）。
- **`VDict` 按键取，不按下标**：`vd["c"]` 可用，`vd[2]` 抛 `KeyError: 2`；`show_keys=True` 时键名文字也是子对象，会一起参与 `arrange`/`get_all_submobjects()`。
- **`VectorizedPoint` 的 `artificial_width/height` 只改"报告尺寸"**：默认 0.01×0.01 且不可见（样例用灰框标出报告尺寸），给 `fill_opacity=1` 才会画出来。

## 12-数字与变量

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `decimal` | decimal | `12-数字与变量-decimal.mp4`（534 帧 / 8.90s） | 12-数字与变量-decimal-manimce.mp4（534 帧 / 8.90s） | ✅ |
| `integer` | integer | `12-数字与变量-integer.mp4`（354 帧 / 5.90s） | 12-数字与变量-integer-manimce.mp4（354 帧 / 5.90s） | ✅ |
| `textdecimal` | textdecimal | `12-数字与变量-textdecimal.mp4`（336 帧 / 5.60s） | —（RTM 单边，无 CE 孪生片） | — |
| `variable` | variable | `12-数字与变量-variable.mp4`（330 帧 / 5.50s） | 12-数字与变量-variable-manimce.mp4（330 帧 / 5.50s） | ✅ |

- **验证**：4 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **`Integer` 就是 `num_decimal_places=0` 的 `DecimalNumber`**：其余参数完全通用；`show_ellipsis=True` 只在数值被四舍五入截断时补 `...`（`3.14159` + 2 位小数 → `3.14...`）。
- **`edge_to_fix` 只在数值长度变化时可见**：样例把 `LEFT` / `RIGHT` 两个数同时从 `9.99` 改成 `100.0`，左对齐的左边不动、右对齐的右边不动；`set_value`/`increment_value` 是立即改，要动画就用 `ValueTracker` + updater。
- **`Variable` 更新要走 `tracker`**：`v.tracker.animate.set_value(x)` 才有过渡，直接 `v.value.set_value(x)` 是瞬变。
- **`textdecimal` 是 RTM 单边样例（无 CE 对照）**：`TextDecimalNumber` 只存在于 `real_time_manim/animations/text.py`，ManimCE 0.21 没有这个类，所以 `12-数字与变量-textdecimal.mp4` 没有 CE 孪生片（`wiki_sweep.py` 会自动跳过无孪生片的成片）；它是 `Text` 子类，`set_value` 走内部 `_value_cache` 复用字形，改值不重新排版，但只吃 `number`/`font_size`/`font`/`num_decimal_places`。

## 14-表格

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `decimaltable` | decimaltable | `14-表格-decimaltable.mp4`（192 帧 / 3.20s） | 14-表格-decimaltable-manimce.mp4（192 帧 / 3.20s） | ✅ |
| `integertable` | integertable | `14-表格-integertable.mp4`（192 帧 / 3.20s） | 14-表格-integertable-manimce.mp4（192 帧 / 3.20s） | ✅ |
| `mathtable` | mathtable | `14-表格-mathtable.mp4`（186 帧 / 3.10s） | 14-表格-mathtable-manimce.mp4（186 帧 / 3.10s） | ✅ |
| `mobjecttable` | mobjecttable | `14-表格-mobjecttable.mp4`（210 帧 / 3.50s） | 14-表格-mobjecttable-manimce.mp4（210 帧 / 3.50s） | ✅ |
| `table` | table | `14-表格-table.mp4`（510 帧 / 8.50s） | 14-表格-table-manimce.mp4（510 帧 / 8.50s） | ✅ |

- **验证**：5 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **单元格渲染类决定"能放什么"**：`Table` 默认 `Paragraph`、`MathTable` 默认 `MathTex`、`MobjectTable` 默认恒等函数、`IntegerTable`/`DecimalTable` 默认 `Integer`/`DecimalNumber`；把数字元素交给 `Text`/`MathTex` 会抛 `AttributeError`（与 13-矩阵 同一个坑），样例里换类时都用了能接数字的类。
- **`top_left_entry` 需要行列标签都给**：只给其一时左上角不会显示；`element_to_mobject_config` 是整体替换而非合并（换位数时把 `font_size` 一起写进去）。
- **`Table` 继承 `VGroup`**：`arrange`/`scale`/整体上色/下标索引都能用，`get_cell`/`add_highlighted_cell`/`create` 见 14b-表格方法页；样例里有 `get_rows/get_columns/get_entries` 与 `get_horizontal_lines/get_vertical_lines` 的读数、`set_row_colors`/`set_column_colors`/`add_background_to_entries` 三个方法的连续演示。

## 14b-表格方法

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `create` | create | `14b-表格方法-create.mp4`（198 帧 / 3.30s） | 14b-表格方法-create-manimce.mp4（198 帧 / 3.30s） | ✅ |
| `getcell` | getcell | `14b-表格方法-getcell.mp4`（204 帧 / 3.40s） | 14b-表格方法-getcell-manimce.mp4（204 帧 / 3.40s） | ✅ |
| `highlight` | highlight | `14b-表格方法-highlight.mp4`（198 帧 / 3.30s） | 14b-表格方法-highlight-manimce.mp4（198 帧 / 3.30s） | ✅ |

- **验证**：3 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **位置 `pos` 是 `(行, 列)`、1 起算**：`(1,1)` 是左上角，与 Python 0 起算下标不同；四个方法统一用这套坐标。
- **`add_highlighted_cell` 返回表格自身**（可链式），高亮块是表格子对象、会跟着表格变换；对同一格重复调用会叠出新的背景块。
- **`get_cell` 给多边形、`get_highlighted_cell` 给背景矩形**：前者是格子本体（描边可见），后者是自带 `BackgroundRectangle` 的底块；后者不会自动 `add` 进表格，需要跟随变换时自己 `t.add(hl)`。
- **`create()` 返回 `AnimationGroup`**：表格对象仍要先构造，`win.play(t.create())` 播放编排；`lag_ratio` 控制线/标签/单元格三组的错峰，`line_animation` 等可替换。

## 11-代码块

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `code` | code | `11-代码块-code.mp4`（222 帧 / 3.70s） | 11-代码块-code-manimce.mp4（222 帧 / 3.70s） | ✅ |
| `styles` | styles | `11-代码块-styles.mp4`（204 帧 / 3.40s） | 11-代码块-styles-manimce.mp4（204 帧 / 3.40s） | ✅ |

- **验证**：2 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **`code_file` / `code_string` 二选一**：文件构造按扩展名推断语言，字符串构造建议显式写 `language`；`\n` 换行、`\t` 缩进。
- **`background` 有 `rectangle` 与 `window` 两种**：`window` 会多一层标题栏、整体更高，排版留位要大一点；`background_config` / `paragraph_config` 分别透传给背景矩形与内部 `Paragraph`。
- **`get_styles_list()` 是 classmethod**：直接 `Code.get_styles_list()` 查 `formatter_style` 的可选值（当前 50 种），名单随 Pygments 版本变化，别写死。

## 10-Typst

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `autoroute` | autoroute | `10-Typst-autoroute.mp4`（198 帧 / 3.30s） | —（RTM 单边，无 CE 孪生片） | — |
| `typst` | typst | `10-Typst-typst.mp4`（216 帧 / 3.60s） | —（RTM 单边，无 CE 孪生片） | — |
| `typstmath` | typstmath | `10-Typst-typstmath.mp4`（234 帧 / 3.90s） | —（RTM 单边，无 CE 孪生片） | — |

- **验证**：3 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **RTM 特有**：`Typst` / `TypstMath` 是 RTM 的排版类，ManimCE 0.21 没有 `TypstMath`，因此三条样例都是 RTM 单边成片（`# RTM-only` 标记，CE 孪生脚本不生成这三条）。
- **Typst 数学写 `$...$`，TypstMath 里不要再写 `$`**：`TypstMath` 会自动包一层；分式 `a/b`、根号 `sqrt(x)`、矩阵 `mat(1, 2; 3, 4)` 都是 Typst 语法，不是 LaTeX。
- **`typst_preamble` 是前置定义**：`#set` / `#let` 这类要先于正文生效的语句写在这里；`height` 与 `font_size` 同时给时以 `height` 为准。
- **`MathTex` 自动路由**：照常写 LaTeX，RTM 内部转 Typst 排版（本机不需要装 LaTeX），片段接口（`set_color_by_tex` / `get_part_by_tex`）仍然可用；极少数自定义宏没有对应实现时改用 `TypstMath`。

## 09-LaTeX公式

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `mathtex` | mathtex | `09-LaTeX公式-mathtex.mp4`（198 帧 / 3.30s） | 09-LaTeX公式-mathtex-manimce.mp4（198 帧 / 3.30s） | ✅ |
| `singlestring` | singlestring | `09-LaTeX公式-singlestring.mp4`（198 帧 / 3.30s） | 09-LaTeX公式-singlestring-manimce.mp4（198 帧 / 3.30s） | ✅ |
| `tex` | tex | `09-LaTeX公式-tex.mp4`（180 帧 / 3.00s） | 09-LaTeX公式-tex-manimce.mp4（180 帧 / 3.00s） | ✅ |

- **验证**：3 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **三个类的分工**：`Tex` 混排正文与公式（公式写 `$...$`）、`MathTex` 纯公式且可拆片段、`SingleStringMathTex` 最轻量的单串公式（不拆片段，`Text`/`MathTex` 的字形叶子就是它）。
- **`tex_environment="document"` 下不要用 `\\` 手动换行**：实测直接编译失败（`latex error converting to dvi`，两引擎一致）；换行请拆多个 `Tex` 或改用 `align*`/`gather*`。
- **`MathTex` 的 `$` 不用再写**（它本身就是数学模式）；单个字符串里的 `{{ }}` 只会拆出第一段，要按项上色就每个片段一个位置参数。
- **LaTeX 依赖**：`Tex`/`MathTex` 需要本机 LaTeX；不想装就用 [Typst](10-Typst.md)（`TypstMath`，或让 `MathTex` 走 RTM 的自动路由）。

## 08-文本Text

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `markup` | markup | `08-文本Text-markup.mp4`（198 帧 / 3.30s） | 08-文本Text-markup-manimce.mp4（198 帧 / 3.30s） | ✅ |
| `paragraph` | paragraph | `08-文本Text-paragraph.mp4`（198 帧 / 3.30s） | 08-文本Text-paragraph-manimce.mp4（198 帧 / 3.30s） | ✅ |
| `registerfont` | registerfont | `08-文本Text-registerfont.mp4`（198 帧 / 3.30s） | 08-文本Text-registerfont-manimce.mp4（198 帧 / 3.30s） | ✅ |
| `text` | text | `08-文本Text-text.mp4`（216 帧 / 3.60s） | 08-文本Text-text-manimce.mp4（216 帧 / 3.60s） | ✅ |

- **验证**：4 个样例各一条，帧数逐条对齐，逐帧对拍 `bad_frames=0`。
- **`MarkupText` 只认 `<b>`/`<i>` 这类基础标记**：`<span foreground=…>` 会让 Pango→SVG 解析失败（`ElementTree.ParseError: no element found`，实测 RTM 报错），要单独上色请给整串 `color` 或用 `Text` 的 `t2c`。
- **`Paragraph` 的 `alignment` 是整块对齐**：段与段之间用 `line_spacing` 控制，`\n` 只是同一段内的换行；`**kwargs`（`color`/`font`/`font_size`）透传给整段文本。
- **`register_font` 是上下文管理器**：`with register_font(路径):` 块内注册、按**字体文件里的族名**使用（不是文件名）；同进程内退出 `with` 后仍可用（缓存），换进程要重新注册。
- **`remove_invisible_chars` 不可用**：当前版本没有从 `real_time_manim` 导出（`ImportError`），需要清理不可见字符时自己按字形过滤。

## 复现

```powershell
# RTM 版（不带参数=渲全部片段并拼接；带参数=只渲指定片段）
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\RTM code\01-基本形状.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\RTM code\01b-基本形状进阶.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\RTM code\02-线与箭头.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\RTM code\02b-箭头尖端.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\RTM code\03-多边形与星形.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\RTM code\03b-矩形与特殊多边形.py"

python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\RTM code\04-角度与标注框.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\RTM code\07b-VMobject样式进阶.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\RTM code\09b-片段方法与列表.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\RTM code\13-矩阵.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\RTM code\04b-带标签标注.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\RTM code\16-花括号标注.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\RTM code\15-图片与SVG.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\RTM code\05-布尔运算.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\RTM code\06-容器与组合.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\RTM code\12-数字与变量.py"
python "C:\Users\begin\Desktop\RTM-Wiki\%s\RTM code\14-表格.py"
python "C:\Users\begin\Desktop\RTM-Wiki\%s\RTM code\14b-表格方法.py"
python "C:\Users\begin\Desktop\RTM-Wiki\%s\RTM code\11-代码块.py"
python "C:\Users\begin\Desktop\RTM-Wiki\%s\RTM code\10-Typst.py"
python "C:\Users\begin\Desktop\RTM-Wiki\%s\RTM code\09-LaTeX公式.py"
python "C:\Users\begin\Desktop\RTM-Wiki\%s\RTM code\08-文本Text.py"
# ManimCE 对照版（同一个 shim 把 win.play 转成 self.play）
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\ManimCE code\01-基本形状-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\ManimCE code\01b-基本形状进阶-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\ManimCE code\02-线与箭头-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\ManimCE code\02b-箭头尖端-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\ManimCE code\03-多边形与星形-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\ManimCE code\03b-矩形与特殊多边形-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\ManimCE code\04-角度与标注框-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\ManimCE code\07b-VMobject样式进阶-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\ManimCE code\09b-片段方法与列表-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\assets\ManimCE code\13-矩阵-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\ManimCE code\04b-带标签标注-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\ManimCE code\16-花括号标注-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\ManimCE code\15-图片与SVG-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\ManimCE code\05-布尔运算-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\ManimCE code\06-容器与组合-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\04-图形与文本\ManimCE code\12-数字与变量-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\%s\ManimCE code\14-表格-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\%s\ManimCE code\14b-表格方法-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\%s\ManimCE code\11-代码块-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\%s\ManimCE code\10-Typst-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\%s\ManimCE code\09-LaTeX公式-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\%s\ManimCE code\08-文本Text-manimce.py"```

RTM 只支持 1920×1080@60，脚本里写 `MLWindow(960, 540)` 会被强制纠正并打印一行提示，属正常。
