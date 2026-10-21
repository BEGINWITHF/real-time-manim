# 02-Mobject通用

> 功能目录 · 16 页。

| 页面 | 功能 |
| --- | --- |
| [01-构造与容器](01-构造与容器.md) | Mobject · Group · add / remove / add_to_back / insert · 索引、切片与迭代 |
| [01b-构造与容器-进阶](01b-构造与容器-进阶.md) | get_family / family_members_with_points / split · has_points / has_no_points / get_num_points · set · set_default · reset_points / generate_points / init_colors |
| [02-摆放位置](02-摆放位置.md) | shift · move_to · next_to · to_edge / to_corner · center / align_to |
| [02b-摆放位置-进阶](02b-摆放位置-进阶.md) | align_on_border · set_coord / set_x / set_y / set_z · arrange · arrange_in_grid · surround / replace · put_start_and_end_on · shift_onto_screen / is_off_screen · space_out_submobjects |
| [03-测量](03-测量.md) | width / height / depth · get_center / get_top / get_bottom / get_left / get_right · get_x / get_y / get_z / get_coord / get_corner / get_edge_center / get_critical_point · length_over_dim / get_all_points · 重心与边界点族 + 底层统计 |
| [04-缩放旋转与变形](04-缩放旋转与变形.md) | scale · rotate / rotate_about_origin · flip · stretch / stretch_about_point |
| [04b-缩放旋转与变形-进阶](04b-缩放旋转与变形-进阶.md) | rescale_to_fit · scale_to_fit_* / stretch_to_fit_* · pose_at_angle · apply_function / apply_matrix / apply_complex_function · apply_points_function_about_point · repeat / reverse_points |
| [05-样式与颜色](05-样式与颜色.md) | set_color · set_color_by_gradient / set_submobject_colors_by_gradient / 径向渐变 · fade_to / fade · get_color / match_color / to_original_color · set_z_index / set_z_index_by_z_Point3D · add_background_rectangle |
| [06-复制派生与状态](06-复制派生与状态.md) | copy · become · save_state / restore · generate_target · interpolate · match_dim_size / match_width / match_height / match_depth · match_coord / match_x / match_y / match_z / match_points / align_points |
| [07-animate语法](07-animate语法.md) | .animate · override_animate · add_animation_override / animation_override_for |
| [08-更新器](08-更新器.md) | add_updater · remove_updater / clear_updaters · suspend_updating / resume_updating / update · always · get_updaters / get_time_based_updaters / has_time_based_updater / match_updaters |
| [08b-更新器工具函数](08b-更新器工具函数.md) | always_redraw · always / f_always · always_shift / always_rotate · turn_animation_into_updater / cycle_animation |
| [09-更新器动画](09-更新器动画.md) | UpdateFromFunc · UpdateFromAlphaFunc · MaintainPositionRelativeTo |
| [10-ValueTracker](10-ValueTracker.md) | ValueTracker 构造 · get_value / set_value / increment_value · interpolate · ComplexValueTracker |
| [11-屏幕框架与横幅](11-屏幕框架与横幅.md) | ScreenRectangle · FullScreenRectangle · ManimBanner |
| [11b-低频其余API](11b-低频其余API.md) | get_image / show / save_image · sort / shuffle / invert · apply_to_family · get_start / get_end / get_start_and_end / get_pieces / point_from_proportion / proportion_from_point · mobject/utils.py 渲染器基类工厂 |
