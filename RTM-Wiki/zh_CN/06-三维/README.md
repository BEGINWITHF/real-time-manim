# 06-三维

三维基本体、旋转体进阶、参数曲面、多面体与 three_d_utils 辅助函数——`ThreeDScene` 里 `set_camera_orientation` 摆视角、`move_camera` 环绕，全部双引擎出片。

[首页](../README.md) ｜ [功能状态总览](../99-功能状态总览.md)

- [01-三维基本体](01-三维基本体.md)
- [01b-三维基本体进阶](01b-三维基本体进阶.md)
- [02-三维表面](02-三维表面.md)
- [03-多面体](03-多面体.md)
- [04-三维工具函数](04-三维工具函数.md)

## 每页样例视频与源码

### [01-三维基本体](01-三维基本体.md)

小节 = 样例 = 视频（页面里嵌的就是这几条）：

| 样例 | 内容 | 视频 | 帧数 |
| --- | --- | --- | --- |
| `cube` | 默认蓝立方体 vs 实心绿描边立方体，环绕 90° | [assets/RTM output/01-三维基本体-cube.mp4](assets/RTM output/01-三维基本体-cube.mp4) | 156 |
| `prism` | `[3,2,1]` vs `[1,1,3]` 两棱柱，环绕 90° | [assets/RTM output/01-三维基本体-prism.mp4](assets/RTM output/01-三维基本体-prism.mp4) | 156 |
| `dot3d` | 半径/颜色/分辨率 `(4,2)` vs `(8,8)` 对比 | [assets/RTM output/01-三维基本体-dot3d.mp4](assets/RTM output/01-三维基本体-dot3d.mp4) | 156 |

- 专属 demo：[assets/RTM code/01-三维基本体.py](assets/RTM code/01-三维基本体.py)（页面里的代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/01-三维基本体-manimce.py](assets/ManimCE code/01-三维基本体-manimce.py) → 同名 `-manimce.mp4` 三条，帧数全对齐

### [01b-三维基本体进阶](01b-三维基本体进阶.md)

| 样例 | 内容 | 视频 | 帧数 |
| --- | --- | --- | --- |
| `line3d` | `parallel_to` / `perpendicular_to` 派生线，旋转 90° | [assets/RTM output/01b-三维基本体进阶-line3d.mp4](assets/RTM output/01b-三维基本体进阶-line3d.mp4) | 174 |
| `arrow3d` | 红箭头参数 + `get_end()` 标注，旋转 90° | [assets/RTM output/01b-三维基本体进阶-arrow3d.mp4](assets/RTM output/01b-三维基本体进阶-arrow3d.mp4) | 144 |
| `cone` | `show_base=True` vs `u_min=0.5, v_range=(0,PI)`，旋转 90° | [assets/RTM output/01b-三维基本体进阶-cone.mp4](assets/RTM output/01b-三维基本体进阶-cone.mp4) | 144 |
| `cylinder` | `show_ends=False + v_range + direction=RIGHT` vs 默认，旋转 90° | [assets/RTM output/01b-三维基本体进阶-cylinder.mp4](assets/RTM output/01b-三维基本体进阶-cylinder.mp4) | 144 |

- 专属 demo：[assets/RTM code/01b-三维基本体进阶.py](assets/RTM code/01b-三维基本体进阶.py)（页面代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/01b-三维基本体进阶-manimce.py](assets/ManimCE code/01b-三维基本体进阶-manimce.py) → 四条 `-manimce.mp4`，帧数全对齐

### [02-三维表面](02-三维表面.md)

| 样例 | 内容 | 视频 | 帧数 |
| --- | --- | --- | --- |
| `surface` | `ParametricSurface` 参数曲面（u/v 网格），环绕 90° | [assets/RTM output/02-三维表面-surface.mp4](assets/RTM output/02-三维表面-surface.mp4) | 180 |
| `sphere` | `v_range=(0,PI)` 全球 vs `(0,PI/2)` 半球（红），环绕 90° | [assets/RTM output/02-三维表面-sphere.mp4](assets/RTM output/02-三维表面-sphere.mp4) | 144 |
| `torus` | 完整圆环 vs `v_range=(0,PI)` 半环（绿），环绕 90° | [assets/RTM output/02-三维表面-torus.mp4](assets/RTM output/02-三维表面-torus.mp4) | 144 |

- 专属 demo：[assets/RTM code/02-三维表面.py](assets/RTM code/02-三维表面.py)（页面代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/02-三维表面-manimce.py](assets/ManimCE code/02-三维表面-manimce.py) → 三条 `-manimce.mp4`，帧数全对齐

### [03-多面体](03-多面体.md)

| 样例 | 内容 | 视频 | 帧数 |
| --- | --- | --- | --- |
| `platonic` | 四种柏拉图立体一行排开 + `graph`/`faces` 上色，环绕 90° | [assets/RTM output/03-多面体-platonic.mp4](assets/RTM output/03-多面体-platonic.mp4) | 156 |
| `polyhedron` | 自定义顶点/面表四棱锥，`graph[4].animate` 拖锥顶形变 | [assets/RTM output/03-多面体-polyhedron.mp4](assets/RTM output/03-多面体-polyhedron.mp4) | 132 |
| `hull` | 6 散点 `ConvexHull3D` 自动求凸包，环绕 90° | [assets/RTM output/03-多面体-hull.mp4](assets/RTM output/03-多面体-hull.mp4) | 156 |

- 专属 demo：[assets/RTM code/03-多面体.py](assets/RTM code/03-多面体.py)（页面代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/03-多面体-manimce.py](assets/ManimCE code/03-多面体-manimce.py) → 三条 `-manimce.mp4`，帧数全对齐

### [04-三维工具函数](04-三维工具函数.md)

| 样例 | 内容 | 视频 | 帧数 |
| --- | --- | --- | --- |
| `corners` | 首/尾角点（红/黄球）+ 首/尾法向（绿箭头）标在面片上，环绕 90° | [assets/RTM output/04-三维工具函数-corners.mp4](assets/RTM output/04-三维工具函数-corners.mp4) | 144 |
| `face_normals` | 首/中/尾三锚点 `get_3d_vmob_unit_normal` 法向箭头，环绕 90° | [assets/RTM output/04-三维工具函数-face_normals.mp4](assets/RTM output/04-三维工具函数-face_normals.mp4) | 144 |

- 专属 demo：[assets/RTM code/04-三维工具函数.py](assets/RTM code/04-三维工具函数.py)（页面代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/04-三维工具函数-manimce.py](assets/ManimCE code/04-三维工具函数-manimce.py) → 两条 `-manimce.mp4`，帧数全对齐

## CE 对照说明

出片（CE 对照侧在 `assets\ManimCE code` 下，内部走 `python -m manim render -qh`，自动 concat 到 assets/ —— 这一步**依赖外置 ManimCE 安装**：内置副本无 `cli/`、`__main__.py`，零依赖环境下 `-m manim` 不可用；RTM 侧在 `assets\RTM code`，走 `fast_record_scene`，**不依赖 manim CLI**）：

```powershell
cd assets\ManimCE code
python 01-三维基本体-manimce.py            # 全部
python 03-多面体-manimce.py hull           # 只跑指定片段
python 04-三维工具函数-manimce.py --concat-only   # 只拼接
```

对照结论：

- 15 对视频帧数全对齐、内容同貌（PSNR 平均 30.9~43.2dB，差异为描边抗锯齿与光栅化量级），详见 [assets/README.md](assets/README.md)。
- 五个 RTM demo 与 CE demo 唯一差异是 import（CE 走 `manimce_shim.py` 垫片把 `win.play` 转回 `self.play`），class 主体逐字一致。
- Surface 子类（`Cone`/`Cylinder`/`Sphere`/`Torus`）构造参数里的 `color=` 会被吞（上游行为，两引擎一致），须构造成 `.set_color(...)`——页面与 demo 已按此写，各页提醒里标了。
- `three_d_utils` 八函数里 `get_3d_vmob_start_corner_index` 恒返回 0，加上对 `VGroup` 外壳调用会退化（角点→`ORIGIN`、法向→`UP`），页面尾"无法演示"里就地标明。
