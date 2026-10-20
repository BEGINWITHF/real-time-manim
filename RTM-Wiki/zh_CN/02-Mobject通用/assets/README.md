# 02-Mobject通用 样例视频（RTM / ManimCE 对比）

本目录所有页面的样例视频都由 `RTM code/`、`ManimCE code/` 下的源码渲染，各页面 md 只引用 **RTM** 那一版；
带 `-manimce` 的是同一份代码用 ManimCE 渲的，留着自己对比，不进页面。
74 条样例全部渲两个引擎、逐条核对帧数，RTM/CE 帧数一致，可逐帧对照着看。

## 对照表

### 01-构造与容器

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `ctor` | 构造参数 `color` / `name` / `z_index`（含 `dim` / `target` 打印） | `01-构造与容器-ctor.mp4`（66 帧 / 1.10s） | `01-构造与容器-ctor-manimce.mp4`（66 帧 / 1.10s） | 对齐 |
| `group` | `Group` 混装、重复 `add`、`VGroup` 拒收 | `01-构造与容器-group.mp4`（66 帧 / 1.10s） | `01-构造与容器-group-manimce.mp4`（66 帧 / 1.10s） | 对齐 |
| `add_remove` | `add` / `remove` / `add_to_back` / `insert` 四段 | `01-构造与容器-add_remove.mp4`（102 帧 / 1.70s） | `01-构造与容器-add_remove-manimce.mp4`（102 帧 / 1.70s） | 对齐 |
| `indexing` | `mob[i]` / `mob[a:b]` / 迭代 / `len` | `01-构造与容器-indexing.mp4`（90 帧 / 1.50s） | `01-构造与容器-indexing-manimce.mp4`（90 帧 / 1.50s） | 对齐 |

每条样例各为单段输出，无拼接。逐帧 `blend=difference` 平均差（1/255）：`ctor` 0.051（最大 0.104）、
`group` 0.029、`add_remove` 0.041、`indexing` 0.054——差别只在描边抗锯齿，位置/颜色/叠放次序一致。

### 01b-构造与容器-进阶

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `family` | `get_family` / `family_members_with_points` / `split` | `01b-构造与容器-进阶-family.mp4`（36 帧 / 0.60s） | `01b-构造与容器-进阶-family-manimce.mp4`（36 帧 / 0.60s） | 对齐 |
| `points` | `has_points` / `has_no_points` / `get_num_points` | `01b-构造与容器-进阶-points.mp4`（60 帧 / 1.00s） | `01b-构造与容器-进阶-points-manimce.mp4`（60 帧 / 1.00s） | 对齐 |
| `set` | `set(**kwargs)` + 兼容层 `set_width` 警告 | `01b-构造与容器-进阶-set.mp4`（72 帧 / 1.20s） | `01b-构造与容器-进阶-set-manimce.mp4`（72 帧 / 1.20s） | 对齐 |
| `set_default` | 改默认值 → 新对象 → 不带参恢复 | `01b-构造与容器-进阶-set_default.mp4`（66 帧 / 1.10s） | `01b-构造与容器-进阶-set_default-manimce.mp4`（66 帧 / 1.10s） | 对齐 |
| `hooks` | `reset_points` / `generate_points` / `init_colors` | `01b-构造与容器-进阶-hooks.mp4`（90 帧 / 1.50s） | `01b-构造与容器-进阶-hooks-manimce.mp4`（90 帧 / 1.50s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）：`family` 0.020、`points` 0.040、`set` 0.077（最大 0.235，
`animate.set` 的颜色/宽度插值帧）、`set_default` 0.052、`hooks` 0.067（最大 0.107）。

> `hooks` 样例曾暴露一个 **RTM 渲染 bug**（已修，见文末「已修 RTM bug」）：被 `stretch` 拉扁的
> `Circle` 仍走原生圆盘路径，被画成均匀放大的圆（CE 是正确的椭圆）。修复后两边画面一致。

### 02-摆放位置

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `shift` | 单向量 / 多向量 / 瞬间平移 | `02-摆放位置-shift.mp4`（96 帧 / 1.60s） | `02-摆放位置-shift-manimce.mp4`（96 帧 / 1.60s） | 对齐 |
| `move_to` | 对象对点 / `aligned_edge=UR` / `coor_mask` | `02-摆放位置-move_to.mp4`（138 帧 / 2.30s） | `02-摆放位置-move_to-manimce.mp4`（138 帧 / 2.30s） | 对齐 |
| `next_to` | `direction`/`buff`/`aligned_edge`/子对象对齐/下标对齐 | `02-摆放位置-next_to.mp4`（120 帧 / 2.00s） | `02-摆放位置-next_to-manimce.mp4`（120 帧 / 2.00s） | 对齐 |
| `edge_corner` | `to_edge` 三边 + `to_corner(UR)` | `02-摆放位置-edge_corner.mp4`（66 帧 / 1.10s） | `02-摆放位置-edge_corner-manimce.mp4`（66 帧 / 1.10s） | 对齐 |
| `center_align` | `center()` / `align_to(big, UP)` | `02-摆放位置-center_align.mp4`（102 帧 / 1.70s） | `02-摆放位置-center_align-manimce.mp4`（102 帧 / 1.70s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）：`shift` 0.014、`move_to` 0.014、`next_to` 0.048、
`edge_corner` 0.093（灰色示意框的直线抗锯齿）、`center_align` 0.028，最大不过 0.12。

### 02b-摆放位置-进阶

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `border` | `align_on_border` 贴边 + 贴角 | `02b-摆放位置-进阶-border.mp4`（60 帧 / 1.00s） | `02b-摆放位置-进阶-border-manimce.mp4`（60 帧 / 1.00s） | 对齐 |
| `coords` | `set_x` / `set_y` / `set_coord` / `set_z` | `02b-摆放位置-进阶-coords.mp4`（120 帧 / 2.00s） | `02b-摆放位置-进阶-coords-manimce.mp4`（120 帧 / 2.00s） | 对齐 |
| `arrange` | 横排 / 竖排 / `center=False` | `02b-摆放位置-进阶-arrange.mp4`（126 帧 / 2.10s） | `02b-摆放位置-进阶-arrange-manimce.mp4`（126 帧 / 2.10s） | 对齐 |
| `grid` | `arrange_in_grid` 2×3 → 3×2 `flow_order="dr"` | `02b-摆放位置-进阶-grid.mp4`（102 帧 / 1.70s） | `02b-摆放位置-进阶-grid-manimce.mp4`（102 帧 / 1.70s） | 对齐 |
| `surround_replace` | `surround` 外框 + `replace(stretch=True)` 垫底 | `02b-摆放位置-进阶-surround_replace.mp4`（84 帧 / 1.40s） | `02b-摆放位置-进阶-surround_replace-manimce.mp4`（84 帧 / 1.40s） | 对齐 |
| `put_ends` | `put_start_and_end_on` 两端钉点 | `02b-摆放位置-进阶-put_ends.mp4`（66 帧 / 1.10s） | `02b-摆放位置-进阶-put_ends-manimce.mp4`（66 帧 / 1.10s） | 对齐 |
| `off_screen` | `is_off_screen` 判断 + `shift_onto_screen` 拉回 | `02b-摆放位置-进阶-off_screen.mp4`（66 帧 / 1.10s） | `02b-摆放位置-进阶-off_screen-manimce.mp4`（66 帧 / 1.10s） | 对齐 |
| `space_out` | `space_out_submobjects` 1.8 / 0.5 | `02b-摆放位置-进阶-space_out.mp4`（96 帧 / 1.60s） | `02b-摆放位置-进阶-space_out-manimce.mp4`（96 帧 / 1.60s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）都在 0.06 以下（最大单帧 0.074）：`border` 0.015、`coords` 0.011、
`arrange` 0.025、`grid` 0.048、`surround_replace` 0.053、`put_ends` 0.020、`off_screen` 0.006、`space_out` 0.026。

### 03-测量

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `size` | `width`/`height`/`depth` 读取与赋值 | `03-测量-size.mp4`（96 帧 / 1.60s） | `03-测量-size-manimce.mp4`（96 帧 / 1.60s） | 对齐 |
| `edges` | `get_center`/`get_top`/`get_bottom`/`get_left`/`get_right` 打点 | `03-测量-edges.mp4`（60 帧 / 1.00s） | `03-测量-edges-manimce.mp4`（60 帧 / 1.00s） | 对齐 |
| `coords` | `get_x`/`get_y`/`get_z`/`get_coord`/`get_corner`/`get_edge_center`/`get_critical_point` | `03-测量-coords.mp4`（54 帧 / 0.90s） | `03-测量-coords-manimce.mp4`（54 帧 / 0.90s） | 对齐 |
| `points` | `length_over_dim` / `get_all_points` 顶点云 | `03-测量-points.mp4`（60 帧 / 1.00s） | `03-测量-points-manimce.mp4`（60 帧 / 1.00s） | 对齐 |
| `stats` | 重心/边界点族 + `get_extremum_along_dim` 等底层统计 | `03-测量-stats.mp4`（54 帧 / 0.90s） | `03-测量-stats-manimce.mp4`（54 帧 / 0.90s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）：`size` 0.035、`edges` 0.020、`coords` 0.017、`points` 0.061、
`stats` 0.061（小圆点标记的抗锯齿），最大单帧 0.070。控制台打印的测量值两引擎逐字一致。

### 04-缩放旋转与变形

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `scale` | 中心 / `about_point` / `about_edge` 三种基准 | `04-缩放旋转与变形-scale.mp4`（132 帧 / 2.20s） | `04-缩放旋转与变形-scale-manimce.mp4`（132 帧 / 2.20s） | 对齐 |
| `rotate` | `animate.rotate` / `about_point` / `Rotate` 动画 / `rotate_about_origin` | `04-缩放旋转与变形-rotate.mp4`（180 帧 / 3.00s） | `04-缩放旋转与变形-rotate-manimce.mp4`（180 帧 / 3.00s） | 对齐 |
| `flip` | `axis=UP`（左右）/ `axis=RIGHT`（上下） | `04-缩放旋转与变形-flip.mp4`（96 帧 / 1.60s） | `04-缩放旋转与变形-flip-manimce.mp4`（96 帧 / 1.60s） | 对齐 |
| `stretch` | `dim=0/1` / `about_point` / `stretch_about_point` | `04-缩放旋转与变形-stretch.mp4`（132 帧 / 2.20s） | `04-缩放旋转与变形-stretch-manimce.mp4`（132 帧 / 2.20s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）：`scale` 0.026、`rotate` 0.040、`flip` 0.021、`stretch` 0.020，
最大单帧 0.059。**注意**：`.animate.rotate` 的中间帧是「点对点插值」（会缩塌），RTM 与 CE 在这些帧上
逐帧一致——说明这确实是 manim 语义而非 RTM 特性，页面里已按此写明并推荐用 `Rotate` 动画类。

### 04b-缩放旋转与变形-进阶

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `rescale` | `rescale_to_fit` 等比 / 拉伸 | `04b-缩放旋转与变形-进阶-rescale.mp4`（96 帧 / 1.60s） | `04b-缩放旋转与变形-进阶-rescale-manimce.mp4`（96 帧 / 1.60s） | 对齐 |
| `fit` | `scale_to_fit_*` vs `stretch_to_fit_*` | `04b-缩放旋转与变形-进阶-fit.mp4`（96 帧 / 1.60s） | `04b-缩放旋转与变形-进阶-fit-manimce.mp4`（96 帧 / 1.60s） | 对齐 |
| `pose` | `pose_at_angle` 斜向投影（3D 轴） | `04b-缩放旋转与变形-进阶-pose.mp4`（66 帧 / 1.10s） | `04b-缩放旋转与变形-进阶-pose-manimce.mp4`（66 帧 / 1.10s） | 对齐 |
| `apply` | `apply_function` / `apply_matrix` / `apply_complex_function` / 两个位置版 | `04b-缩放旋转与变形-进阶-apply.mp4`（264 帧 / 4.40s） | `04b-缩放旋转与变形-进阶-apply-manimce.mp4`（264 帧 / 4.40s） | 对齐 |
| `points_func` | `apply_points_function_about_point` | `04b-缩放旋转与变形-进阶-points_func.mp4`（96 帧 / 1.60s） | `04b-缩放旋转与变形-进阶-points_func-manimce.mp4`（96 帧 / 1.60s） | 对齐 |
| `repeat_rev` | `reverse_points` 换向 + `repeat` 翻点数 | `04b-缩放旋转与变形-进阶-repeat_rev.mp4`（60 帧 / 1.00s） | `04b-缩放旋转与变形-进阶-repeat_rev-manimce.mp4`（60 帧 / 1.00s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）：`rescale` 0.032、`fit` 0.024、`pose` 0.042（3D 轴旋转的投影
两引擎完全一致）、`apply` 0.077、`points_func` 0.013、`repeat_rev` 0.124（小红点标记的抗锯齿）。

> `apply` 样例涉及一个 **ManimCE 0.21 上游 bug**（纯 CE 会中招；**RTM 侧已修**，见文末「上游 bug 清单」）：
> `VMobject.apply_function` 丢弃 `about_point` / `about_edge`，导致 `apply_function` /
> `apply_complex_function` 在矢量对象上永远以原点为基准——RTM 进程里该形参**生效**
> （内嵌副本已转发 + `homotopy.py` 运行时补丁）。样例仍改用「在原点变形 → `move_to` 摆位」
> 的绕法，只为与未修的 CE 逐帧可比、两边画面一致。

### 05-样式与颜色

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `set_color` | `color` / `family`（`alpha` 不适用于 `VMobject`） | `05-样式与颜色-set_color.mp4`（96 帧 / 1.60s） | `05-样式与颜色-set_color-manimce.mp4`（96 帧 / 1.60s） | 对齐 |
| `gradient` | 线性/径向渐变四件套 | `05-样式与颜色-gradient.mp4`（144 帧 / 2.40s） | `05-样式与颜色-gradient-manimce.mp4`（144 帧 / 2.40s） | 对齐 |
| `fade` | `fade_to` 混色 / `fade` 变淡 | `05-样式与颜色-fade.mp4`（96 帧 / 1.60s） | `05-样式与颜色-fade-manimce.mp4`（96 帧 / 1.60s） | 对齐 |
| `get_match` | `get_color` / `match_color` / `to_original_color` | `05-样式与颜色-get_match.mp4`（120 帧 / 2.00s） | `05-样式与颜色-get_match-manimce.mp4`（120 帧 / 2.00s） | 对齐 |
| `z_index` | `set_z_index` / `set_z_index_by_z_Point3D` | `05-样式与颜色-z_index.mp4`（90 帧 / 1.50s） | `05-样式与颜色-z_index-manimce.mp4`（90 帧 / 1.50s） | 对齐 |
| `background` | `add_background_rectangle` 三个变体 | `05-样式与颜色-background.mp4`（90 帧 / 1.50s） | `05-样式与颜色-background-manimce.mp4`（90 帧 / 1.50s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）：`set_color` 0.051、`gradient` 0.089、`fade` 0.028、
`get_match` 0.093、`z_index` 0.021、`background` 1.568（全目录最大，来源是字形抗锯齿叠在黑衬底上的
局部高对比，逐帧对比两画面内容一致）。

### 06-复制派生与状态

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `copy` | 深拷贝后互不影响 | `06-复制派生与状态-copy.mp4`（84 帧 / 1.40s） | `06-复制派生与状态-copy-manimce.mp4`（84 帧 / 1.40s） | 对齐 |
| `become` | 直接变成 + `stretch`/`match_center` | `06-复制派生与状态-become.mp4`（90 帧 / 1.50s） | `06-复制派生与状态-become-manimce.mp4`（90 帧 / 1.50s） | 对齐 |
| `save_restore` | `save_state` → 改动 → `restore` | `06-复制派生与状态-save_restore.mp4`（102 帧 / 1.70s） | `06-复制派生与状态-save_restore-manimce.mp4`（102 帧 / 1.70s） | 对齐 |
| `target` | `generate_target` + `MoveToTarget` | `06-复制派生与状态-target.mp4`（66 帧 / 1.10s） | `06-复制派生与状态-target-manimce.mp4`（66 帧 / 1.10s） | 对齐 |
| `interpolate` | 手动取 `alpha=0.5` 插值态 | `06-复制派生与状态-interpolate.mp4`（96 帧 / 1.60s） | `06-复制派生与状态-interpolate-manimce.mp4`（96 帧 / 1.60s） | 对齐 |
| `match_size` | `match_width` 等比 / `match_dim_size` 拉伸 / `match_depth` | `06-复制派生与状态-match_size.mp4`（84 帧 / 1.40s） | `06-复制派生与状态-match_size-manimce.mp4`（84 帧 / 1.40s） | 对齐 |
| `match_pos` | `match_x` / `match_coord` / `match_points` / `align_points` | `06-复制派生与状态-match_pos.mp4`（114 帧 / 1.90s） | `06-复制派生与状态-match_pos-manimce.mp4`（114 帧 / 1.90s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）都在 0.06 以下（最大单帧 0.094）：`copy` 0.026、`become` 0.057、
`save_restore` 0.023、`target` 0.023、`interpolate` 0.023、`match_size` 0.044、`match_pos` 0.041。
`become` 的 `stretch` 椭圆（Circle 分支点路径）两引擎一致。

### 07-animate语法

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `animate` | 平移 / 链式 / `play_kwargs` / `set` | `07-animate语法-animate.mp4`（168 帧 / 2.80s） | `07-animate语法-animate-manimce.mp4`（168 帧 / 2.80s） | 对齐 |
| `override` | `@override_animate`：直接调用 vs `.animate` 调用 | `07-animate语法-override.mp4`（90 帧 / 1.50s） | `07-animate语法-override-manimce.mp4`（90 帧 / 1.50s） | 对齐 |
| `add_override` | `add_animation_override` 注册 FadeIn→FadeOut | `07-animate语法-add_override.mp4`（60 帧 / 1.00s） | `07-animate语法-add_override-manimce.mp4`（60 帧 / 1.00s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）：`animate` 0.054（there_and_back 插值帧最大 0.173）、
`override` 0.031、`add_override` 0.011。`override_animate` / `add_animation_override` 在 RTM 下
照常生效（RTM 正确执行了返回的 `Transform` / 替换后的 `FadeOut`），与 CE 逐帧一致。

### 08-更新器

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `add_updater` | 时间型 + 非时间型 + `index`/`call_updater` | `08-更新器-add_updater.mp4`（114 帧 / 1.90s） | `08-更新器-add_updater-manimce.mp4`（114 帧 / 1.90s） | 对齐 |
| `remove_clear` | `remove_updater` / `clear_updaters` | `08-更新器-remove_clear.mp4`（90 帧 / 1.50s） | `08-更新器-remove_clear-manimce.mp4`（90 帧 / 1.50s） | 对齐 |
| `suspend` | `suspend_updating` / `resume_updating` / `update` | `08-更新器-suspend.mp4`（96 帧 / 1.60s） | `08-更新器-suspend-manimce.mp4`（96 帧 / 1.60s） | 对齐 |
| `always` | `mob.always.method` 跟随标签 | `08-更新器-always.mp4`（72 帧 / 1.20s） | `08-更新器-always-manimce.mp4`（72 帧 / 1.20s） | 对齐 |
| `query_match` | `get_updaters` 三查询 + `match_updaters` | `08-更新器-query_match.mp4`（48 帧 / 0.80s） | `08-更新器-query_match-manimce.mp4`（48 帧 / 0.80s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）：`add_updater` 0.251（每帧变化的数字字形是主要差异源）、
`remove_clear` 0.013、`suspend` 0.013、`always` 0.029、`query_match` 0.017，最大单帧 0.594。
**updater 在 RTM 与 CE 下的执行时机/次数完全一致**——旋转角度、数字读数、跟随位置逐帧对得上。

### 08b-更新器工具函数

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `always_redraw` | `ValueTracker` 驱动逐帧重画 | `08b-更新器工具函数-always_redraw.mp4`（84 帧 / 1.40s） | `08b-更新器工具函数-always_redraw-manimce.mp4`（84 帧 / 1.40s） | 对齐 |
| `always_fn` | 模块级 `always` / `f_always` 跟随标签 | `08b-更新器工具函数-always_fn.mp4`（72 帧 / 1.20s） | `08b-更新器工具函数-always_fn-manimce.mp4`（72 帧 / 1.20s） | 对齐 |
| `always_shift_rotate` | `always_shift` + `always_rotate` + `assert_is_mobject_method` | `08b-更新器工具函数-always_shift_rotate.mp4`（96 帧 / 1.60s） | `08b-更新器工具函数-always_shift_rotate-manimce.mp4`（96 帧 / 1.60s） | 对齐 |
| `anim_updater` | `turn_animation_into_updater` / `cycle_animation` | `08b-更新器工具函数-anim_updater.mp4`（132 帧 / 2.20s） | `08b-更新器工具函数-anim_updater-manimce.mp4`（132 帧 / 2.20s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）：`always_redraw` 0.011、`always_fn` 0.067（文字标签）、
`always_shift_rotate` 0.010、`anim_updater` 0.023。动画 updater（`turn_animation_into_updater`）
随场景时间推进的效果在两引擎逐帧一致。

### 09-更新器动画

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `update_func` | `UpdateFromFunc` 跟随读数 | `09-更新器动画-update_func.mp4`（162 帧 / 2.70s） | `09-更新器动画-update_func-manimce.mp4`（162 帧 / 2.70s） | 对齐 |
| `update_alpha` | `UpdateFromAlphaFunc` 按进度插值 | `09-更新器动画-update_alpha.mp4`（78 帧 / 1.30s） | `09-更新器动画-update_alpha-manimce.mp4`（78 帧 / 1.30s） | 对齐 |
| `maintain` | `MaintainPositionRelativeTo` 卫星跟随 | `09-更新器动画-maintain.mp4`（90 帧 / 1.50s） | `09-更新器动画-maintain-manimce.mp4`（90 帧 / 1.50s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）：`update_func` 0.036、`update_alpha` 0.016、`maintain` 0.023。

### 10-ValueTracker

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `basic` | `set_value` / `increment_value` / `+=` / 算术运算 | `10-ValueTracker-basic.mp4`（114 帧 / 1.90s） | `10-ValueTracker-basic-manimce.mp4`（114 帧 / 1.90s） | 对齐 |
| `interpolate` | `interpolate` 瞬间取插值态 | `10-ValueTracker-interpolate.mp4`（66 帧 / 1.10s） | `10-ValueTracker-interpolate-manimce.mp4`（66 帧 / 1.10s） | 对齐 |
| `complex` | `ComplexValueTracker` 复数即坐标 | `10-ValueTracker-complex.mp4`（84 帧 / 1.40s） | `10-ValueTracker-complex-manimce.mp4`（84 帧 / 1.40s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）：`basic` 0.032、`interpolate` 0.086（读数跳变帧）、
`complex` 0.002。`ValueTracker` 的动画/`+=` 语义与算术运算结果两引擎逐字一致。
`ComplexValueTracker` 的算术运算两引擎一致地抛 `TypeError`（上游行为，页面已注明）。

### 11-屏幕框架与横幅

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `screen_rect` | `ScreenRectangle` + `aspect_ratio` 属性 | `11-屏幕框架与横幅-screen_rect.mp4`（60 帧 / 1.00s） | `11-屏幕框架与横幅-screen_rect-manimce.mp4`（60 帧 / 1.00s） | 对齐 |
| `fullscreen` | `FullScreenRectangle` 变暗遮罩 | `11-屏幕框架与横幅-fullscreen.mp4`（96 帧 / 1.60s） | `11-屏幕框架与横幅-fullscreen-manimce.mp4`（96 帧 / 1.60s） | 对齐 |
| `banner` | `ManimBanner.create` / `expand` / 非法 direction | `11-屏幕框架与横幅-banner.mp4`（156 帧 / 2.60s） | `11-屏幕框架与横幅-banner-manimce.mp4`（156 帧 / 2.60s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）：`screen_rect` 0.061、`fullscreen` 0.065、
`banner` 0.185（logo 与字母全是文字光栅化，是本页差异大头），最大单帧 0.316。
`AnimationGroup` / `Succession` 组合动画在 RTM 下正常播放、`expand` 的 `ValueError` 两引擎一致。

### 11b-低频其余API

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `sort_shuffle_invert` | `sort` / `shuffle`（固定种子）/ `invert` | `11b-低频其余API-sort_shuffle_invert.mp4`（168 帧 / 2.80s） | `11b-低频其余API-sort_shuffle_invert-manimce.mp4`（168 帧 / 2.80s） | 对齐 |
| `apply_family` | `apply_to_family` 批量改样式 | `11b-低频其余API-apply_family.mp4`（72 帧 / 1.20s） | `11b-低频其余API-apply_family-manimce.mp4`（72 帧 / 1.20s） | 对齐 |
| `path` | `get_start`/`get_end`/`point_from_proportion`/`proportion_from_point`/`get_pieces` | `11b-低频其余API-path.mp4`（78 帧 / 1.30s） | `11b-低频其余API-path-manimce.mp4`（78 帧 / 1.30s） | 对齐 |

逐帧 `blend=difference` 平均差（1/255）：`sort_shuffle_invert` 0.040、`apply_family` 0.038、
`path` 0.027。`shuffle` 在固定 `random.seed(7)` 后两引擎顺序一致。

**无法出片的两组（页面已写清原因，不留空视频位）**：
- `get_image` / `show` / `save_image`：ManimCE 0.21 上游 `NameError: name 'Camera' is not defined`，
  RTM 与纯 CE 实测一致地崩。
- `mobject/utils.py` 的三个渲染器基类工厂（`get_mobject_class` 等）：返回类对象、本身无画面。

## 复现

```powershell
# RTM 版（每页一个脚本，放在 assets\RTM code\：渲全部片段到 final\ 并拼出成片）
cd "assets\RTM code"
python 01-构造与容器.py
python 01b-构造与容器-进阶.py

# ManimCE 对照版（assets\ManimCE code\，同一个 manimce_shim 垫片把 win.play 转成 self.play）
cd "..\ManimCE code"
python 01-构造与容器-manimce.py
python 01b-构造与容器-进阶-manimce.py
```

> **2026-10-17 更新**：两份脚本自带的 `concat` 目标仍是旧布局的 `assets\` 根目录（历史遗留），
> 渲完把成片移进页面实际引用的 `assets\RTM output\` / `assets\ManimCE output\` 即可。
> RTM 侧可用仓库工具一键渲染+归位：
> `python C:\Users\begin\Desktop\real-time-manim\tools\wiki_render.py "<本目录>\RTM code\01-构造与容器.py"`（不带片段名=整页；带片段名=只渲该片段）。

RTM 只支持 1920×1080@60，`MLWindow(960, 540)` 会被强制纠正并打印一行提示，属正常。

## 已修 RTM bug

- **被 `stretch` / `apply_matrix` 弄变形的 `Circle` 被画成均匀圆盘**（01b `hooks` 样例发现）：
  `window/paint.py` 的 `Circle` 分支走原生 `_send_circle`，半径取「起点到中心的距离」，
  拉扁后的圆被画成半径=半宽的正圆，与 CE 不符。
  修复：`render/shapes/primitives.py` 新增 `PrimitiveMixin._circle_round_radius`（检查贝塞尔锚点
  是否仍在同一个圆上），`window/paint.py` 的 `Circle` 分支在锚点不共圆时改走 `_send_vmobject`
  点路径。未变形的圆仍走原生路径，行为不变。

## ManimCE 0.21 上游 bug 清单（RTM 侧已修的会注明；页面已注明绕法）

- **`VMobject.apply_function` 丢弃 `about_point` / `about_edge`**（04b `apply` 样例发现）：
  `VMobject.apply_function` 内部只调 `super().apply_function(function)`，把基准点吞掉，
  于是**纯 ManimCE 0.21** 的 `apply_function` / `apply_complex_function` 在所有矢量对象
  （`Circle` / `Square` / `Text`……）上永远以原点为基准，传了 `about_point` 也不生效。
  `apply_matrix` 与 `apply_points_function_about_point` 不受影响。
  **RTM 侧已修（2026-10-17 起在 wiki 中注明）**：`real_time_manim/manim/mobject/types/vectorized_mobject.py`
  的内嵌副本已把 `about_point` / `about_edge` 转发给 `super()`，且 `animations/homotopy.py` 导入时会
  装一个幂等运行时补丁（对先 import 外置 manim 的场景同样生效），所以 **RTM 进程里该形参生效**。
  样例仍用「先 `move_to(ORIGIN)` 在原点变形、变完再挪走」的绕法，只为与未修的 CE 逐帧画面可比。
- **`VMobject.set_color` 没有 `alpha` 参数**：`Mobject.set_color(color, alpha, family)` 的签名里
  有 `alpha`，但 `VMobject` 覆写成 `set_color(color, family=True)`——矢量对象传 `alpha=` 直接
  `TypeError`。要调不透明度用 `set_fill(opacity=...)`。
