# 01-Scenes-and-Cameras

> Feature index · 17 pages.

## Special Scenes

| Page | Features |
| --- | --- |
| [01-MovingCameraScene](Special-Scenes/01-MovingCameraScene.md) | MovingCameraScene · self.camera.frame |
| [02-ThreeDScene](Special-Scenes/02-ThreeDScene.md) | ThreeDScene · set_camera_orientation / move_camera · begin/stop_ambient_camera_rotation, begin/stop_3dillusion_camera_rotation · add/remove_fixed_in_frame_mobjects, add/remove_fixed_orientation_mobjects · SpecialThreeDScene |
| [03-ZoomedScene](Special-Scenes/03-ZoomedScene.md) | ZoomedScene · ZoomedScene.activate_zooming · get_zoom_in_animation / get_zoomed_display_pop_out_animation / get_zoom_factor |
| [04-VectorScene](Special-Scenes/04-VectorScene.md) | VectorScene · add_plane / add_axes · add_vector / get_vector · write_vector_coordinates, label_vector, get_vector_label · get_basis_vectors / get_basis_vector_labels · vector_to_coords · lock_in_faded_grid / coords_to_vector / show_ghost_movement |
| [05-LinearTransformationScene](Special-Scenes/05-LinearTransformationScene.md) | LinearTransformationScene · apply_matrix / apply_inverse / apply_transposed_matrix / apply_inverse_transpose · apply_nonlinear_transformation / apply_function · add_title / get_unit_square / add_unit_square · add_vector / write_vector_coordinates / add_transformable_label |

## Scenes

| Page | Features |
| --- | --- |
| [01-Scene-Basics](Scenes/01-Scene-Basics.md) | Scene · Scene.setup · Scene.render · Scene.camera |
| [02-Displaying-Content](Scenes/02-Displaying-Content.md) | Scene.add · Scene.remove · Scene.clear · bring_to_front · Scene.replace |
| [03-Play-and-Wait](Scenes/03-Play-and-Wait.md) | Scene.play · Wait · Scene.add_updater · Scene.validate_run_time |
| [04-Subcaptions-and-Sound](Scenes/04-Subcaptions-and-Sound.md) | Scene.add_sound · Scene.next_section · Scene.add_subcaption · interactive_embed |

## Cameras

| Page | Features |
| --- | --- |
| [01-Camera](Cameras/01-Camera.md) | Camera · Camera.background_color / Camera.background_opacity · Camera.is_in_frame · Camera.use_z_index · pixel reading and manual capture |
| [02-MovingCamera](Cameras/02-MovingCamera.md) | MovingCamera · MovingCamera.frame_height / frame_width / frame_center · MovingCamera.auto_zoom |
| [03-ThreeDCamera](Cameras/03-ThreeDCamera.md) | ThreeDCamera · ThreeDCamera view parameters · ThreeDCamera.add_fixed_in_frame_mobjects / add_fixed_orientation_mobjects · ThreeDCamera.project_point / project_points · ThreeDCamera.capture_mobjects |

## Configuration

| Page | Features |
| --- | --- |
| [01-Quality-and-Output](Configuration/01-Quality-and-Output.md) | config · background_color |
| [02-Frame-and-Coordinates](Configuration/02-Frame-and-Coordinates.md) | frame_width · top |
| [03-Paths-and-Windows](Configuration/03-Paths-and-Windows.md) | config · out_path |
| [04-ManimCE-CLI-Cheat-Sheet](Configuration/04-ManimCE-CLI-Cheat-Sheet.md) | main render parameters · global / output / usability flags and subcommands · manim commands ↔ RTM calls |
| [05-RTM-Record-and-Window-Options](Configuration/05-RTM-Record-and-Window-Options.md) | fast_record_scene(...) · record_scene(...) · MLWindow(w, h, hidden) · MLWindow.enable_fast_record(...) |
