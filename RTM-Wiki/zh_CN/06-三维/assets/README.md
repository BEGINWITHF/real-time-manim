# 三维样例视频（RTM / ManimCE 对照）

这些视频都由 `RTM code/`（RTM 版）与 `ManimCE code/`（CE 对照版）下的源码渲染，页面（`01`~`04`）只引用 **RTM** 那一版；
带 `-manimce` 的是同一份代码用 ManimCE 渲的，留着自己对比，不进页面。

## 01-三维基本体

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `cube` | 默认蓝立方体 vs 实心绿描边立方体，环绕 90° | `01-三维基本体-cube.mp4`（156 帧 / 2.60s） | `01-三维基本体-cube-manimce.mp4`（156 帧 / 2.60s） | 对齐 |
| `prism` | `[3,2,1]` vs `[1,1,3]` 两棱柱，环绕 90° | `01-三维基本体-prism.mp4`（156 帧 / 2.60s） | `01-三维基本体-prism-manimce.mp4`（156 帧 / 2.60s） | 对齐 |
| `dot3d` | 半径/颜色/分辨率 `(4,2)` vs `(8,8)` 对比 | `01-三维基本体-dot3d.mp4`（156 帧 / 2.60s） | `01-三维基本体-dot3d-manimce.mp4`（156 帧 / 2.60s） | 对齐 |

- 三条全部对齐；PSNR avg：cube 41.0、prism 43.2、dot3d 33.8 dB（低分辨率球面锯齿对光栅化差异敏感，画面内容逐帧目检一致）。
- 三维光照着色两引擎一致：不同朝向的面亮度不同，半透明立方体可透出背面。

## 01b-三维基本体进阶

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `line3d` | `parallel_to` / `perpendicular_to` 派生线，旋转 90° | `01b-三维基本体进阶-line3d.mp4`（174 帧） | `01b-三维基本体进阶-line3d-manimce.mp4`（174 帧） | 对齐 |
| `arrow3d` | 红箭头参数 + `get_end()` 标注，旋转 90° | `01b-三维基本体进阶-arrow3d.mp4`（144 帧） | `01b-三维基本体进阶-arrow3d-manimce.mp4`（144 帧） | 对齐 |
| `cone` | `show_base=True` vs `u_min=0.5, v_range=(0,PI)`，旋转 90° | `01b-三维基本体进阶-cone.mp4`（144 帧） | `01b-三维基本体进阶-cone-manimce.mp4`（144 帧） | 对齐 |
| `cylinder` | `show_ends=False + v_range + direction=RIGHT` vs 默认，旋转 90° | `01b-三维基本体进阶-cylinder.mp4`（144 帧） | `01b-三维基本体进阶-cylinder-manimce.mp4`（144 帧） | 对齐 |

- 四条全部对齐；PSNR avg：line3d 39.9、arrow3d 33.1、cone 38.9、cylinder 38.5 dB，画面内容逐帧目检一致。
- Surface 子类（Cone/Cylinder 等）构造参数里的 `color=` 会被吞掉（着色发生在部件生成之前），必须构造成 `.set_color(...)`——两引擎行为一致，已按此修正示例。

## 02-三维表面

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `surface` | `ParametricSurface` 参数曲面（u/v 网格），环绕 90° | `02-三维表面-surface.mp4`（180 帧） | `02-三维表面-surface-manimce.mp4`（180 帧） | 对齐 |
| `sphere` | `v_range=(0,PI)` 全球 vs `(0,PI/2)` 半球（红），环绕 90° | `02-三维表面-sphere.mp4`（144 帧） | `02-三维表面-sphere-manimce.mp4`（144 帧） | 对齐 |
| `torus` | 完整圆环 vs `v_range=(0,PI)` 半环（绿），环绕 90° | `02-三维表面-torus.mp4`（144 帧） | `02-三维表面-torus-manimce.mp4`（144 帧） | 对齐 |

- 三条全部对齐；PSNR avg：surface 42.0、sphere 34.0、torus 32.7 dB，画面内容逐帧目检一致。
- 同 01b：`Sphere`/`Torus` 的 `color=` 参数会被吞，样例用构造成 `.set_color(...)` 染色（红半球 / 绿半环），两引擎一致。

## 03-多面体

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `platonic` | 四种柏拉图立体一行排开 + `graph`/`faces` 上色，环绕 90° | `03-多面体-platonic.mp4`（156 帧） | `03-多面体-platonic-manimce.mp4`（156 帧） | 对齐 |
| `polyhedron` | 自定义顶点/面表四棱锥，`graph[4].animate` 拖锥顶形变 | `03-多面体-polyhedron.mp4`（132 帧） | `03-多面体-polyhedron-manimce.mp4`（132 帧） | 对齐 |
| `hull` | 6 散点 `ConvexHull3D` 自动求凸包，环绕 90° | `03-多面体-hull.mp4`（156 帧） | `03-多面体-hull-manimce.mp4`（156 帧） | 对齐 |

- 三条全部对齐；PSNR avg：platonic 36.0、polyhedron 40.0、hull 30.9 dB（凸包细描边的抗锯齿差异，画面内容逐帧目检一致）。
- `graph[4].animate.shift` 拖顶点形变在 RTM 正常（updater 驱动面片跟随），与 CE 同貌。

## 04-三维工具函数

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `corners` | 面片首/尾角点（红/黄球）+ 首/尾法向（绿箭头），环绕 90° | `04-三维工具函数-corners.mp4`（144 帧） | `04-三维工具函数-corners-manimce.mp4`（144 帧） | 对齐 |
| `face_normals` | 首/中/尾三锚点 `get_3d_vmob_unit_normal` 法向箭头，环绕 90° | `04-三维工具函数-face_normals.mp4`（144 帧） | `04-三维工具函数-face_normals-manimce.mp4`（144 帧） | 对齐 |

- 两条全部对齐；PSNR avg：corners 38.1、face_normals 39.8 dB，画面内容逐帧目检一致。
- `three_d_utils` 八函数七个进样例（`get_3d_vmob_start_corner_index` 恒返回 0，页面尾"无法演示"标明）；对 `VGroup` 外壳调用会退化（角点→`ORIGIN`、法向→`UP`），样例一律先取 `cube[i]` 单面片。

## 复现

```powershell
# RTM 版：每页一个脚本，不带参数渲全部，带片段名只渲指定片段
cd assets\RTM code
python 01-三维基本体.py cube        # 只渲一个片段（RTM 渲染开真窗口占 GPU：多会话并行请错峰渲染，仓库里没有"GPU 锁"）
python 01-三维基本体.py --concat-only

# ManimCE 对照版（同一个 MLWindow 垫片把 win.play 转成 self.play；内部走 "python -m manim render -qh"，
#                  这一步依赖外置 ManimCE 安装——内置副本无 cli/、__main__.py，零依赖下 -m manim 不可用）
cd ..\ManimCE code
python 01-三维基本体-manimce.py             # 全部
python 01-三维基本体-manimce.py prism       # 只跑指定片段
```

RTM 只支持 1920×1080@60，`MLWindow(960, 540)` 会被强制纠正并打印一行提示，属正常。
