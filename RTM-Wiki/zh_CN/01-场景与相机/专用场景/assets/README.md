# 专用场景样例视频（RTM / ManimCE 对照）

这些视频都由 `demos/` 下的源码渲染，页面（`01`~`05`）只引用 **RTM** 那一版；
带 `-manimce` 的是同一份代码用 ManimCE 渲的，留着自己对比，不进页面。

## 01-MovingCameraScene

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `camera_class` | `MovingCamera`（推近+拉回）+ 换成 `Camera`（无镜头运动）两段拼接 | `01-MovingCameraScene-camera_class.mp4`（204 帧 / 3.40s） | `01-MovingCameraScene-camera_class-manimce.mp4`（150 帧 / 2.50s） | 见下（CE 少 54 帧） |
| `**kwargs` | `random_seed` = 1 / 7 | `01-MovingCameraScene-random_seed.mp4`（120 帧 / 2.00s） | `01-MovingCameraScene-random_seed-manimce.mp4`（120 帧 / 2.00s） | 对齐 |
| `self.camera.frame` | 宽度 14.0 / 4.0 / 2.0 三段 | `01-MovingCameraScene-camera_frame.mp4`（522 帧 / 8.70s） | `01-MovingCameraScene-camera_frame-manimce.mp4`（522 帧 / 8.70s） | 对齐 |

- **画面几乎逐像素一致**：逐帧 `blend=difference` 平均差 ≤0.24/255，无一帧超过 1/255。
- **页面里嵌的 `01-MovingCameraScene-camera_class.mp4` 是拼接件**（204 帧 = `MovingCamera` 段 150 + `Camera` 段 54；两段分片在 `RTM code/final/`），CE 侧只有前 150 帧，所以这一对帧数天然对不上，`tools/wiki_sweep.py` 只逐帧比较前 150 帧（`bad_frames=0`）。
- **ManimCE 渲不出 `camera_class=Camera`**：CE 侧没有对照件，`wiki_sweep.py` 只逐帧比较前 150 帧（`bad_frames=0`），原因见 [99-不支持清单](../../../99-不支持清单.md)。

## 02-ThreeDScene

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| 构造参数 | 默认正面 → `set_to_default_angled_camera_orientation`；`ambient_camera_rotation` 存而不用 → `begin_ambient_camera_rotation` 才转 | `02-ThreeDScene-ctor.mp4`（648 帧 / 10.80s） | `02-ThreeDScene-ctor-manimce.mp4`（648 帧 / 10.80s） | 对齐 |
| `set_camera_orientation` / `move_camera` | phi/theta → gamma → zoom → frame_center → 复位 | `02-ThreeDScene-camera.mp4`（384 帧 / 6.40s） | `02-ThreeDScene-camera-manimce.mp4`（384 帧 / 6.40s） | 对齐 |
| 环境旋转 / 3D 错觉 | `about=theta` / `about=phi` / `begin_3dillusion` | `02-ThreeDScene-rotation.mp4`（306 帧 / 5.10s） | `02-ThreeDScene-rotation-manimce.mp4`（306 帧 / 5.10s） | 对齐 |
| fixed 系列 | `fixed_in_frame` vs `fixed_orientation`，解除后变普通 3D 对象 | `02-ThreeDScene-fixed.mp4`（276 帧 / 4.60s） | `02-ThreeDScene-fixed-manimce.mp4`（276 帧 / 4.60s） | 对齐 |
| `SpecialThreeDScene` | 截断坐标轴 + 球体 + 专属默认视角（含三处上游 bug 绕法） | `02-ThreeDScene-special.mp4`（156 帧 / 2.60s） | `02-ThreeDScene-special-manimce.mp4`（156 帧 / 2.60s） | 对齐 |

- 两引擎逐帧一致；`ambient_camera_rotation` 构造参数**存而不用**是上游行为，两边一样（样例 1 用对照实证）。
- **`02-ThreeDScene-camera` 曾因 `zoom` 失效整段对不上**（2026-10-17 修复）：`camera_state` 读死属性 `camera.zoom`，`move_camera(zoom=1.8)` 完全没生效，立方体面宽恒为 316 px 而 CE 是 569 px。改读 `get_zoom()` 后 `mean|diff|` 由 5.4295 降到 **1.3307**（`frames>4.0` 由 131 归零）；配套 `Viewport.unit_height` + `render/shapes/stroke.py::_stroke_width` 让缩放下线宽与 CE 的固定画幅一致，测试 `tests/test_three_d_camera_zoom.py`。剩余 1.33（**全部 <4.0/255，不是 bug**）是两处不可修的光栅化差异：顶部说明文字的字形抗锯齿（RTM 自有光栅化 vs Cairo，行内峰值 30–47/255）与 3D 轴/立方体棱边的亚像素描边 AA（5–18/255），另加 H.264 噪声。
- `SpecialThreeDScene` 在上游 `manim` 0.21 有三处 bug（构造期读 `self.renderer`、
  `three_d_axes_config` 默认值含已删除的 `tick_frequency`、`get_axes` 用已删除的 `axis.tick_marks`），
  两引擎同样崩；demo 内已写好三处绕法（两份脚本逐字一致）。

## 03-ZoomedScene

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| 构造参数 | `zoom_factor` 0.15 / 0.08、窗 `3×3`/`4×2.5`、右上/左下 | `03-ZoomedScene-zoom.mp4`（384 帧 / 6.40s） | `03-ZoomedScene-zoom-manimce.mp4`（384 帧 / 6.40s） | 对齐 |
| `activate_zooming(animate)` | `False` 瞬现 vs `True` 推进+弹出 | `03-ZoomedScene-activate.mp4`（276 帧 / 4.60s） | `03-ZoomedScene-activate-manimce.mp4`（276 帧 / 4.60s） | 对齐 |
| 手动编排三步 | 注册 → `get_zoom_in_animation` → `pop_out` → 盖前景 | `03-ZoomedScene-manual.mp4`（180 帧 / 3.00s） | `03-ZoomedScene-manual-manimce.mp4`（180 帧 / 3.00s） | 对齐 |

- 画中画整条链路两引擎一致，无差异。

## 04-向量场景VectorScene

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| 构造参数 + `add_plane` | 线宽 6.0 / 2.0 两段拼接 | `04-向量场景VectorScene-plane.mp4`（456 帧 / 7.60s） | `04-向量场景VectorScene-plane-manimce.mp4`（456 帧 / 7.60s） | 对齐 |
| `add_vector` / `get_vector` | 自动出场 vs 生成后手动加 | `04-向量场景VectorScene-addvec.mp4`（156 帧 / 2.60s） | `04-向量场景VectorScene-addvec-manimce.mp4`（156 帧 / 2.60s） | 对齐 |
| 坐标 / 标签三件套 | 列矩阵、`label_vector`、`get_vector_label` | `04-向量场景VectorScene-labels.mp4`（324 帧 / 5.40s） | `04-向量场景VectorScene-labels-manimce.mp4`（324 帧 / 5.40s） | 对齐 |
| `get_basis_vectors` | 默认 `X_COLOR`/`Y_COLOR` vs `GREEN`/`RED` | `04-向量场景VectorScene-basis.mp4`（108 帧 / 1.80s） | `04-向量场景VectorScene-basis-manimce.mp4`（108 帧 / 1.80s） | 对齐 |
| `vector_to_coords` | 整数 / 小数两种标签 + `clean_up` | `04-向量场景VectorScene-coords.mp4`（780 帧 / 13.00s） | `04-向量场景VectorScene-coords-manimce.mp4`（780 帧 / 13.00s） | 对齐 |

- 五条全部对齐；`vector_to_coords` 单次约 6s 是方法内部节奏（签名无 `run_time`）。
- `lock_in_faded_grid` / `coords_to_vector` / `show_ghost_movement` 三方法在上游 `manim` 0.21
 自身带 bug（详见页面对照表），两引擎一致崩溃，不产视频。

## 05-线性变换场景

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| 构造参数 | 默认 / `show_coordinates` / 两平面全关 / `leave_ghost_vectors` 四段拼接 | `05-线性变换场景-ctor.mp4`（420 帧 / 7.00s） | `05-线性变换场景-ctor-manimce.mp4`（420 帧 / 7.00s） | 对齐 |
| apply 系列 | 剪切 → 求逆还原 → 转置 → 转置之逆 | `05-线性变换场景-apply.mp4`（414 帧 / 6.90s） | `05-线性变换场景-apply-manimce.mp4`（414 帧 / 6.90s） | 对齐 |
| 非线性 | `swirl`（按半径旋转）+ `squash`（tanh 压扁） | `05-线性变换场景-nonlinear.mp4`（264 帧 / 4.40s） | `05-线性变换场景-nonlinear-manimce.mp4`（264 帧 / 4.40s） | 对齐 |
| 组合编排 | 标题/方块/向量/坐标/标签 → 旋转 90° 全联动 | `05-线性变换场景-compose.mp4`（726 帧 / 12.10s） | — 渲不出来（见下） | 不支持 |

- **ManimCE 渲不出 `compose`**：CE 侧无对照件（原因见 [99-不支持清单](../../../99-不支持清单.md)）。RTM 同代码正常出片，旋转、标签改写 `L(w)`、方块变竖均已目检。
- **`ctor` / `apply` 曾整段对不上**（2026-10-17 修复）：`apply_transposed_matrix` 按 manim 的写法把矩阵的净转角**经 `play(...)` 传播**（从不经过动画构造器），而 `win.play()` 只转发了 `run_time`/`rate_func`，`path_arc` 被吞——于是整张 `NumberPlane` 线性插值，网格线该绕弧却没绕。`play` 侧补上 `path_*` 转发后（沿用 manim `compile_animations` 的 `setattr` 语义，`Transform.path_arc` 的 setter 会重建 `path_func`）：`apply` 由 4.0756 降到 **0.6180**（`frames>4.0` 172→0），`ctor` 由 1.1876 降到 **0.4475**（40→0）；测试 `tests/test_play_path_kwargs.py`。

## 复现

```powershell
# RTM 版：每页一个脚本，不带参数渲全部，带场景名只渲指定片段
python demos\01-MovingCameraScene.py
python demos\02-ThreeDScene.py
python demos\03-ZoomedScene.py
python demos\04-向量场景VectorScene.py
python demos\05-线性变换场景.py

# ManimCE 对照版（同一个 MLWindow 垫片把 win.play 转成 self.play）
python demos\01-MovingCameraScene-manimce.py
python demos\02-ThreeDScene-manimce.py
python demos\03-ZoomedScene-manimce.py
python demos\04-向量场景VectorScene-manimce.py
python demos\05-线性变换场景-manimce.py ctor apply nonlinear   # compose 会崩，跳过
```

RTM 只支持 1920×1080@60，`MLWindow(960, 540)` 会被强制纠正并打印一行提示，属正常。
