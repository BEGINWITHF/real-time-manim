# 01-场景与相机

Scene 的生命周期与播放接口、四类专用场景、相机对象，以及 config / 命令行 / RTM 录制参数。

[首页](../README.md) ｜ [功能状态总览](../99-功能状态总览.md)

## 场景

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01-Scene基础](场景/01-Scene基础.md) | Scene 基础：脚本骨架 | 已支持 |
| [02-内容上屏](场景/02-内容上屏.md) | 内容上屏：add / remove 与层次 | 已支持 |
| [03-播放与等待](场景/03-播放与等待.md) | 播放与等待：play / wait 家族 | 已支持 |
| [04-分段字幕与声音](场景/04-分段字幕与声音.md) | 分段、字幕与声音 | 已支持（`add_sound`、`win.play` 字幕；`next_section`、交互调试 ） |

## 专用场景

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01-MovingCameraScene](专用场景/01-MovingCameraScene.md) | MovingCameraScene（推拉摇移场景） | 已支持 |
| [02-ThreeDScene](专用场景/02-ThreeDScene.md) | ThreeDScene（三维场景） | 已支持 |
| [03-ZoomedScene](专用场景/03-ZoomedScene.md) | ZoomedScene（局部放大场景） | 已支持 |
| [04-向量场景VectorScene](专用场景/04-向量场景VectorScene.md) | 向量场景（VectorScene） | 已支持 |
| [05-线性变换场景](专用场景/05-线性变换场景.md) | 线性变换场景（LinearTransformationScene） | 已支持 |

## 相机

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01-Camera](相机/01-Camera.md) | Camera（Cairo 基类相机） | 部分支持：像素管线 （刻意不做）、少数属性（`background_color` / `is_in_frame` / `use_z_index`） |
| [02-MovingCamera](相机/02-MovingCamera.md) | MovingCamera（可移动相机） | 已支持 |
| [03-ThreeDCamera](相机/03-ThreeDCamera.md) | ThreeDCamera（三维相机） | 已支持 |

## 配置

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01-画质与输出](配置/01-画质与输出.md) | 画质与输出（ManimCE `config` 速查表 A） | 成片画质未接线（刻意）；`background_color`、`seed` 间接生效、`renderer` 别填 |
| [02-画幅坐标](配置/02-画幅坐标.md) | 画幅坐标（ManimCE `config` 速查表 B） | 未接线（刻意；RTM 不走 manim 渲染器） |
| [03-路径与窗口](配置/03-路径与窗口.md) | 路径与窗口（ManimCE `config` 速查表 C、D） | 成片路径/窗口未接线（刻意）；`tex_dir`/`text_dir`/`assets_dir`/`tex_template*` 只对中间产物生效 |
| [04-ManimCE命令行速查](配置/04-ManimCE命令行速查.md) | ManimCE 命令行速查（RTM 不支持） | 不支持（RTM 不用 `manim` CLI，改用 `fast_… |
| [05-RTM的录制与窗口参数](配置/05-RTM的录制与窗口参数.md) | RTM 的录制与窗口参数 | （见 `real-time-manim/docs/ALL_FEATURES.… |

## 视频样例

各子文件夹的 `assets/` 下按统一布局存放素材（旧版 `demo_rtm.py` / `demo_manimce.py` / `sample.mp4` 布局已废弃、文件已不存在）：

- `assets/RTM code/0<页>.py` —— 每页一个 RTM 版脚本，片段先落 `RTM code\final\`，成片归档进 `assets\RTM output\`；
- `assets/ManimCE code/0<页>-manimce.py` —— 同一份类代码的 ManimCE 对照版（配 `manimce_shim.py` 把 `win.play` 转回 `self.play`），**需另行安装 ManimCE**；
- `assets/RTM output/` 与 `assets/ManimCE output/` —— 成对成片，逐条对照见各子文件夹的 `assets/README.md`：[场景](场景/assets/README.md)、[专用场景](专用场景/assets/README.md)、[相机](相机/assets/README.md)、[配置](配置/assets/README.md)。

| 子文件夹 | 视频样例（RTM 渲染） | RTM 源码 | ManimCE 对照 |
| --- | --- | --- | --- |
| 场景 | <video src="场景/assets/RTM output/04-分段字幕与声音-sound.mp4" controls width="480"></video> | [场景/assets/RTM code/04-分段字幕与声音.py](场景/assets/RTM code/04-分段字幕与声音.py) | [场景/assets/ManimCE code/04-分段字幕与声音-manimce.py](场景/assets/ManimCE code/04-分段字幕与声音-manimce.py) |
| 专用场景 | <video src="专用场景/assets/RTM output/01-MovingCameraScene-camera_frame.mp4" controls width="480"></video> | [专用场景/assets/RTM code/01-MovingCameraScene.py](专用场景/assets/RTM code/01-MovingCameraScene.py) | [专用场景/assets/ManimCE code/01-MovingCameraScene-manimce.py](专用场景/assets/ManimCE code/01-MovingCameraScene-manimce.py) |
| 相机 | <video src="相机/assets/RTM output/01-Camera-background.mp4" controls width="480"></video> | [相机/assets/RTM code/01-Camera.py](相机/assets/RTM code/01-Camera.py) | [相机/assets/ManimCE code/01-Camera-manimce.py](相机/assets/ManimCE code/01-Camera-manimce.py) |
| 配置 | <video src="配置/assets/RTM output/01-画质与输出-background_color.mp4" controls width="480"></video> | [配置/assets/RTM code/01-画质与输出.py](配置/assets/RTM code/01-画质与输出.py) | [配置/assets/ManimCE code/01-画质与输出-manimce.py](配置/assets/ManimCE code/01-画质与输出-manimce.py) |

以上四条只是各子目录的**示例片段**（完整清单与帧数对齐情况见各 `assets/README.md`）；全部片段都由 `fast_record_scene` 真实渲染（RTM 强制 1920×1080@60），逐条经 `ffprobe -count_frames` 与两引擎帧数比对。

