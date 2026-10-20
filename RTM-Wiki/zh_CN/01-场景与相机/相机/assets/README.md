# 相机 三页样例视频（RTM / ManimCE 对比）

这些视频都由 `demos/` 下的源码渲染；三个页面（`01-Camera.md`、`02-MovingCamera.md`、`03-ThreeDCamera.md`）只引用 **RTM** 那一版；带 `-manimce` 的是同一份类代码用 ManimCE 渲的，留着自己对比，不进页面。

- 成品视频：本目录（`assets/`），命名 `<页名>-<样例名>.mp4`（RTM）/ `<页名>-<样例名>-manimce.mp4`（CE）。
- 渲染片段：`demos/final/`（RTM）与 `demos/out_manimce/`（CE），多段样例用 ffmpeg concat demuxer `-c copy` 拼成成品。

## 对照表

| 页 | 样例 | 片段（RTM 帧数 = CE 帧数） | RTM 成品（页面里嵌的） | ManimCE 成品 | 帧数对齐 |
| --- | --- | --- | --- | --- | --- |
| `01-Camera` | `background` | `background_1` 150 | `01-Camera-background.mp4`（150 帧 / 2.50s） | `01-Camera-background-manimce.mp4`（150 帧） | 对齐 |
| `01-Camera` | `is_in_frame` | `is_in_frame_1` 156 | `01-Camera-is_in_frame.mp4`（156 帧 / 2.60s） | `01-Camera-is_in_frame-manimce.mp4`（156 帧） | 对齐 |
| `01-Camera` | `use_z_index` | `use_z_index_1` 120 | `01-Camera-use_z_index.mp4`（120 帧 / 2.00s） | `01-Camera-use_z_index-manimce.mp4`（120 帧） | 对齐 |
| `02-MovingCamera` | `frame_props` | `frame_scale_1` 114、`frame_center_1` 114 | `02-MovingCamera-frame_props.mp4`（228 帧 / 3.80s） | `02-MovingCamera-frame_props-manimce.mp4`（228 帧） | 对齐 |
| `02-MovingCamera` | `auto_zoom` | `auto_zoom_anim_1` 96、`auto_zoom_noanim_1` 60、`auto_zoom_only_1` 204 | `02-MovingCamera-auto_zoom.mp4`（360 帧 / 6.00s） | `02-MovingCamera-auto_zoom-manimce.mp4`（360 帧） | 对齐 |
| `03-ThreeDCamera` | `ctor` | `ctor_angle_1` 102、`ctor_light_2` 90、`ctor_shading_3` 132 | `03-ThreeDCamera-ctor.mp4`（324 帧 / 5.40s） | `03-ThreeDCamera-ctor-manimce.mp4`（324 帧） | 对齐 |
| `03-ThreeDCamera` | `view` | `view_zoom_1` 102、`view_trackers_2` 126、`view_angles_3` 102 | `03-ThreeDCamera-view.mp4`（330 帧 / 5.50s） | `03-ThreeDCamera-view-manimce.mp4`（330 帧） | 对齐 |
| `03-ThreeDCamera` | `fixed` | `fixed_1` 276 | `03-ThreeDCamera-fixed.mp4`（276 帧 / 4.60s） | `03-ThreeDCamera-fixed-manimce.mp4`（276 帧） | 对齐 |
| `03-ThreeDCamera` | `project` | `project_coords_1` 72、`project_exponential_2` 138 | `03-ThreeDCamera-project.mp4`（210 帧 / 3.50s） | `03-ThreeDCamera-project-manimce.mp4`（210 帧） | 对齐 |

17 个片段、9 条成品，帧数与时长逐条一致；抽帧目检（每条 3 帧、RTM/CE 并排）均一致。

## 对比结论

- **画面几乎逐像素一致**。9 条成品各采样 4 帧算 `blend=difference` 的逐通道均值：`background` 0.94、`is_in_frame` 0.32、`use_z_index` 0.18、`frame_props` 0.19、`auto_zoom` 0.22、`ctor` 0.32、`view` 0.28、`fixed` 0.36、`project` 0.43（单位 1/255）。差别集中在字形抗锯齿与个别动画帧的亚帧相位，位置、颜色、时序完全一致。
- **`ThreeDCamera.zoom` 动起来时 RTM 曾完全忽略**（2026-10-17 修复）：`camera_state.viewport_from_scene` 读的是 `camera.zoom` 这个只在 `ThreeDCamera.__init__` 写过一次的死属性，而 `move_camera(zoom=…)` / `set_camera_orientation(zoom=…)` / `set_zoom()` 动画的是 `zoom_tracker`（读值走 `get_zoom()`）。所以构造参数里的初始 `zoom` 生效（上一条），但运行时缩放无效——`view_zoom_1` 段立方体面宽恒为 316 px，CE 是 569 px（=569/1.8）。改读 `get_zoom()` 后 `03-ThreeDCamera-view.mp4` 由 0.8253 降到 **0.2753**（`frames>4.0: 0`），测试 `tests/test_three_d_camera_zoom.py`。
- **`should_apply_shading`：RTM 曾不认这个开关**（CE 关着色后画面变平色、RTM 照旧带明暗，立方体格子实测差 41864 px）。本次给 `real_time_manim/camera_state.py` 的 `viewport_from_scene` 加了一个 no-light 门闩（`should_apply_shading=False` 时不发布光源，走渲染器已有的「无光源=原色」分支），修复后两引擎一致（`ctor_shading` 段）。
- **上游「存而不用」的死参数**（两引擎同表现，页面已标）：`ThreeDCamera.shading_factor`、`ThreeDCamera.default_distance`、`MovingCamera.fixed_dimension`——0.21 全库只有赋值没有读取。
- **`camera.background_opacity` 曾让 RTM 与 CE 不一致**（2026-10-19 修复）：RTM 把清屏色按 opacity 缩放，而 CE 只把 alpha 放进帧的 alpha 通道（不透明视频写出时丢掉了），所以深蓝背景 `#1E3A5F` 在 `background_opacity = 0.6` 之后 RTM 渲染成 `(16,34,55)`、CE 仍是 `(29,57,93)`，`01-Camera-background` 有 48 帧对不上（均值 7.99）。现在 RTM 不再缩放清屏色（`real_time_manim/window/core.py::_publish_background_color`），该条成片逐帧对拍 `bad_frames = 0`（全片均值 0.75），页面里「出片无变化」的说明对两引擎都成立；测试改为 `tests/test_wiki_marked_gaps.py::test_background_opacity_does_not_change_the_clear_colour`。
- **`MovingCamera` 构造参数 `frame` 实际无效**：传进去的取景框会被 `Camera.__init__` 收尾时写一遍 `frame_height`/`frame_width`/`frame_center` 拉回 8.0×14.222、挪回原点（实测两引擎输出与默认构造逐字节相同）。
- **已知两引擎不一致**（本批样例已避开或在页面提醒里写明）：
  - 普通 `Camera` 的 `frame_center`：CE 按它挪画面，RTM 画面固定居中（只影响 `is_in_frame` 判定）。
  - `frame_height` / `frame_width` **单独**赋值：CE 横竖各自缩放（画面变形），RTM 只按高度等比缩放；成对按 16:9 赋值则完全一致。
  - `default_frame_stroke_*`：把 `self.camera.frame` add 进场景后，CE 会画出取景框描边，RTM 曾把取景框当辅助对象跳过不画——**2026-10-16 已修复**（`MLWindow.sync` 不再无条件跳过，显式 add 且描边可见时 RTM 也画；默认描边 0/填充 0 无像素输出，既有 MovingCameraScene 渲染零变化，测试 `tests/test_gap_camera_frame.py`）。
  - 3D 里固定字幕与坐标轴箭头重叠时的绘制次序：CE 把箭头画在 `fixed_in_frame` 字幕上层，RTM 把字幕画在上层（字幕避开箭头即可）。
- **构造参数里的初始视角没问题**：`ThreeDCamera` 的 `phi`/`theta`/`gamma`/`zoom` 构造参数两引擎都生效（`ctor_angle` 段，抽帧对比显式 `set_camera_orientation` 的结果一致）；「传了没人用」的是 `ThreeDScene` 侧的 `default_angled_camera_orientation_kwargs`/`ambient_camera_rotation`（见 `专用场景/02-ThreeDScene.md`）。

## 复现

```powershell
# RTM 版（03 页 9 个片段 + 各页拼接视频；MLWindow 会被强制 1080p60，属正常）
cd demos
python 01-Camera.py
python 02-MovingCamera.py
python 03-ThreeDCamera.py

# ManimCE 版（同一份类代码，只有导入不同；先从 专用场景/assets/demos 复制 manimce_shim.py）
python 01-Camera-manimce.py
python 02-MovingCamera-manimce.py
python 03-ThreeDCamera-manimce.py
```

带参数（如 `python 01-Camera.py 01-Camera-background_1`）只渲指定片段；CE 版带组名参数（如 `python 01-Camera-manimce.py background`）只渲该组、不拼接。
