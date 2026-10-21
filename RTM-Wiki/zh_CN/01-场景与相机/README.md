# 01-场景与相机

> 功能目录 · 17 页。

## 专用场景

| 页面 | 功能 |
| --- | --- |
| [01-MovingCameraScene](专用场景/01-MovingCameraScene.md) | MovingCameraScene · self.camera.frame |
| [02-ThreeDScene](专用场景/02-ThreeDScene.md) | ThreeDScene · set_camera_orientation / move_camera · begin/stop_ambient_camera_rotation、begin/stop_3dillusion_camera_rotation · add/remove_fixed_in_frame_mobjects、add/remove_fixed_orientation_mobjects · SpecialThreeDScene |
| [03-ZoomedScene](专用场景/03-ZoomedScene.md) | ZoomedScene · ZoomedScene.activate_zooming · get_zoom_in_animation / get_zoomed_display_pop_out_animation / get_zoom_factor |
| [04-向量场景VectorScene](专用场景/04-向量场景VectorScene.md) | VectorScene · add_plane / add_axes · add_vector / get_vector · write_vector_coordinates、label_vector、get_vector_label · get_basis_vectors / get_basis_vector_labels · vector_to_coords · lock_in_faded_grid / coords_to_vector / show_ghost_movement |
| [05-线性变换场景](专用场景/05-线性变换场景.md) | LinearTransformationScene · apply_matrix / apply_inverse / apply_transposed_matrix / apply_inverse_transpose · apply_nonlinear_transformation / apply_function · add_title / get_unit_square / add_unit_square · add_vector / write_vector_coordinates / add_transformable_label |

## 场景

| 页面 | 功能 |
| --- | --- |
| [01-Scene基础](场景/01-Scene基础.md) | Scene · Scene.setup · Scene.render · Scene.camera |
| [02-内容上屏](场景/02-内容上屏.md) | Scene.add · Scene.remove · Scene.clear · bring_to_front · Scene.replace |
| [03-播放与等待](场景/03-播放与等待.md) | Scene.play · Wait · Scene.add_updater · Scene.validate_run_time |
| [04-分段字幕与声音](场景/04-分段字幕与声音.md) | Scene.add_sound · Scene.next_section · Scene.add_subcaption · interactive_embed |

## 相机

| 页面 | 功能 |
| --- | --- |
| [01-Camera](相机/01-Camera.md) | Camera · Camera.background_color / Camera.background_opacity · Camera.is_in_frame · Camera.use_z_index · 像素读取与手动捕获 |
| [02-MovingCamera](相机/02-MovingCamera.md) | MovingCamera · MovingCamera.frame_height / frame_width / frame_center · MovingCamera.auto_zoom |
| [03-ThreeDCamera](相机/03-ThreeDCamera.md) | ThreeDCamera · ThreeDCamera 视角参数 · ThreeDCamera.add_fixed_in_frame_mobjects / add_fixed_orientation_mobjects · ThreeDCamera.project_point / project_points · ThreeDCamera.capture_mobjects |

## 配置

| 页面 | 功能 |
| --- | --- |
| [01-画质与输出](配置/01-画质与输出.md) | config · background_color |
| [02-画幅坐标](配置/02-画幅坐标.md) | frame_width · top |
| [03-路径与窗口](配置/03-路径与窗口.md) | config · out_path |
| [04-ManimCE命令行速查](配置/04-ManimCE命令行速查.md) | 渲染主参数 · 全局 / 输出 / 易用性旗标与子命令 · manim 命令 ↔ RTM 调用 |
| [05-RTM的录制与窗口参数](配置/05-RTM的录制与窗口参数.md) | fast_record_scene(...) · record_scene(...) · MLWindow(w, h, hidden) · MLWindow.enable_fast_record(...) |
