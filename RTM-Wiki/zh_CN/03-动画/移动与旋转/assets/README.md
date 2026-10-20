# 移动与旋转 样例视频（RTM / ManimCE 对照）

本目录的成片由 `RTM code/` 与 `ManimCE code/` 下的同源脚本渲染：页面只引用
**RTM** 那一版（`RTM output/`），带 `-manimce` 的是同一份类代码用 ManimCE 渲的
对照件（`ManimCE output/`），仅供比对，不进页面。

## 01-旋转

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `rotate` | rotate | `01-旋转-rotate.mp4`（186 帧 / 3.10s） | 01-旋转-rotate-manimce.mp4（186 帧 / 3.10s） | 对齐 |
| `rotating_axis` | rotating_axis | `01-旋转-rotating_axis.mp4`（174 帧 / 2.90s） | 01-旋转-rotating_axis-manimce.mp4（174 帧 / 2.90s） | 对齐 |
| `rotating_edge` | rotating_edge | `01-旋转-rotating_edge.mp4`（186 帧 / 3.10s） | 01-旋转-rotating_edge-manimce.mp4（186 帧 / 3.10s） | 对齐 |

## 02-沿路径与同态变换

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `homotopy` | homotopy | `02-沿路径与同态变换-homotopy.mp4`（210 帧 / 3.50s） | 02-沿路径与同态变换-homotopy-manimce.mp4（210 帧 / 3.50s） | 对齐 |
| `movealongpath` | movealongpath | `02-沿路径与同态变换-movealongpath.mp4`（258 帧 / 4.30s） | 02-沿路径与同态变换-movealongpath-manimce.mp4（258 帧 / 4.30s） | 对齐 |

## 02b-同态变换其余类

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `complex` | complex | `02b-同态变换其余类-complex.mp4`（198 帧 / 3.30s） | 02b-同态变换其余类-complex-manimce.mp4（198 帧 / 3.30s） | 对齐 |
| `phaseflow` | phaseflow | `02b-同态变换其余类-phaseflow.mp4`（210 帧 / 3.50s） | 02b-同态变换其余类-phaseflow-manimce.mp4（210 帧 / 3.50s） | 对齐 |
| `smoothed` | smoothed | `02b-同态变换其余类-smoothed.mp4`（198 帧 / 3.30s） | 02b-同态变换其余类-smoothed-manimce.mp4（198 帧 / 3.30s） | 对齐 |

## 03-特殊出场

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `broadcast` | broadcast | `03-特殊出场-broadcast.mp4`（234 帧 / 3.90s） | 03-特殊出场-broadcast-manimce.mp4（234 帧 / 3.90s） | 对齐 |
| `broadcast_tuned` | broadcast_tuned | `03-特殊出场-broadcast_tuned.mp4`（222 帧 / 3.70s） | 03-特殊出场-broadcast_tuned-manimce.mp4（222 帧 / 3.70s） | 对齐 |

## 复现

```powershell
# RTM 版（不带参数=渲全部片段并拼接；带参数=只渲指定片段）
python "C:\Users\begin\Desktop\RTM-Wiki\03-动画\移动与旋转\assets\RTM code\01-旋转.py"
python "C:\Users\begin\Desktop\RTM-Wiki\03-动画\移动与旋转\assets\RTM code\02-沿路径与同态变换.py"
python "C:\Users\begin\Desktop\RTM-Wiki\03-动画\移动与旋转\assets\RTM code\02b-同态变换其余类.py"
python "C:\Users\begin\Desktop\RTM-Wiki\03-动画\移动与旋转\assets\RTM code\03-特殊出场.py"

# ManimCE 对照版（同一个 shim 把 win.play 转成 self.play）
python "C:\Users\begin\Desktop\RTM-Wiki\03-动画\移动与旋转\assets\ManimCE code\01-旋转-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\03-动画\移动与旋转\assets\ManimCE code\02-沿路径与同态变换-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\03-动画\移动与旋转\assets\ManimCE code\02b-同态变换其余类-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\03-动画\移动与旋转\assets\ManimCE code\03-特殊出场-manimce.py"
```

RTM 只支持 1920×1080@60，脚本里写 `MLWindow(960, 540)` 会被强制纠正并打印一行提示，属正常。
