# 配置 章节样例视频（RTM / ManimCE 对比）

这些视频都由 `assets/RTM code/` 与 `assets/ManimCE code/` 下的源码渲染，5 个页面只引用 **RTM** 那一版；带 `-manimce` 的是同一份代码用 ManimCE 渲的，留着自己对比，不进页面。ManimCE 0.21.0，垫片 `ManimCE code/manimce_shim.py` 与 `专用场景/assets/ManimCE code/manimce_shim.py` 一致（SHA256 相同，直接复制）。

## 对照表

### 01-画质与输出

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `background_color` | 深蓝 `#12233a` / 米白 `#e8e4d8` 两段 | `01-画质与输出-background_color.mp4`（228 帧 / 3.80s） | `01-画质与输出-background_color-manimce.mp4`（228 帧 / 3.80s） | 对齐 |

### 02-画幅坐标

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `frame_layout` | 默认画幅：四角红点 + 正方形 + 圆 | `02-画幅坐标-frame_layout.mp4`（114 帧 / 1.90s） | `02-画幅坐标-frame_layout-manimce.mp4`（114 帧 / 1.90s） | 对齐 |
| `frame_override` | 改写 `frame_x_radius`/`frame_y_radius` | `02-画幅坐标-frame_override.mp4`（114 帧 / 1.90s） | `02-画幅坐标-frame_override-manimce.mp4`（114 帧 / 1.90s） | （画面**有意不同**，见结论） |
| `edge_points` | 四边中点 `top`/`bottom`/`left_side`/`right_side` | `02-画幅坐标-edge_points.mp4`（156 帧 / 2.60s） | `02-画幅坐标-edge_points-manimce.mp4`（156 帧 / 2.60s） | 对齐 |

### 03-路径与窗口

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `config_to_rtm` | config 键 → RTM 入口对照动画（4 行） | `03-路径与窗口-config_to_rtm.mp4`（168 帧 / 2.80s） | `03-路径与窗口-config_to_rtm-manimce.mp4`（168 帧 / 2.80s） | 对齐 |

### 04-ManimCE命令行速查

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `quality_tiers` | `-ql`~`-qk` 五档 + RTM 固定档 | `04-ManimCE命令行速查-quality_tiers.mp4`（120 帧 / 2.00s） | `04-ManimCE命令行速查-quality_tiers-manimce.mp4`（120 帧 / 2.00s） | 对齐 |
| `cli_equiv` | `manim` 命令 ↔ `fast_record_scene` 调用 | `04-ManimCE命令行速查-cli_equiv.mp4`（126 帧 / 2.10s） | `04-ManimCE命令行速查-cli_equiv-manimce.mp4`（126 帧 / 2.10s） | 对齐 |

### 05-RTM的录制与窗口参数

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `scene_forms` | 类 / 实例 / 无参可调用 三段 | `05-RTM的录制与窗口参数-scene_forms.mp4`（342 帧 / 5.70s） | `05-RTM的录制与窗口参数-scene_forms-manimce.mp4`（342 帧 / 5.70s） | 对齐 |
| `out_path` | `out_path="clips/demo.mp4"`（子目录自动建） | `05-RTM的录制与窗口参数-out_path.mp4`（114 帧 / 1.90s） | `05-RTM的录制与窗口参数-out_path-manimce.mp4`（114 帧 / 1.90s） | 对齐 |
| `fps` | 请求 `fps=30` / `fps=60` 两段 | `05-RTM的录制与窗口参数-fps.mp4`（228 帧 / 3.80s） | `05-RTM的录制与窗口参数-fps-manimce.mp4`（228 帧 / 3.80s） | 对齐 |
| `mlwindow` | `MLWindow(960,540,hidden=True)` / `(3840,2160,hidden=False)` | `05-RTM的录制与窗口参数-mlwindow.mp4`（228 帧 / 3.80s） | `05-RTM的录制与窗口参数-mlwindow-manimce.mp4`（228 帧 / 3.80s） | 对齐 |
| `record_scene` | 实时可见窗口录制 | `05-RTM的录制与窗口参数-record_scene.mp4`（130 帧 / 2.17s） | `05-RTM的录制与窗口参数-record_scene-manimce.mp4`（114 帧 / 1.90s） | 见下 |

## 对比结论

- **画面几乎逐像素一致**。逐帧算 `blend=difference` 的平均差（/255）：`background_color` 0.19、`frame_layout` 0.26、`edge_points` 0.12、`config_to_rtm` 0.36、`quality_tiers` 0.47、`cli_equiv` 0.34、`scene_forms` 0.11、`out_path` 0.16、`fps` 0.06、`mlwindow` 0.21 —— 全部低于 0.5/255。差异集中在**文字笔画边缘**（Cairo 与 RTM 各有一套文字光栅化，字重/抗锯齿略有差别），背景、图形、动画时序完全一致。
- **`frame_override` 两引擎最终一致**：同一份代码把 `config.frame_x_radius`/`frame_y_radius` 改小一半后，ManimCE 的相机在构造时读走 config，视野缩小一倍、对象铺满全屏；RTM 在成像换算时读同一个 `config.frame_height`，直线与曲线**同倍率缩放**——原先"圆和点没跟着放大（实测圆只有方块一半大）"的曲线/直线缩放不一致 bug 已于 **2026-10-16 修复**（`render/shapes/stroke.py::_visible_frame_height` 无 viewport 时回退读 `config.frame_height`，默认 8.0 画幅下渲染逐字节不变）。对照视频 `02-画幅坐标-frame_override.mp4` 2026-10-17 已重渲：`mean|diff|` 0.417、`frames>4.0: 0`，两引擎的方形/圆形同尺寸。页面里「别用 config 调画幅」的建议仍成立（CE 与 RTM 读 config 的时机不同，别的键未必对齐，用 `MovingCameraScene` 更稳）。
- **`record_scene` 帧数不对齐（预期行为）**：实时录制按墙钟走，从窗口建立起录到 `close()`，还包含启动/收尾时间；抓屏速度受机器限制（本机实测 ~6.5 帧/秒），成片按实际时长重排到 60fps —— 130 帧 / 2.17s，对比离线渲染的 114 帧 / 1.90s。要帧级可复现就用 `fast_record_scene`。
- **`fps=30` 请求不改变输出**：控制台打印 `[rtm] forcing 60 fps` 后照渲 60，两段逐帧一致（ManimCE 对照侧固定 `-qh` 1080p60）。
- **`MLWindow` 尺寸请求不改变输出**：960×540、3840×2160 都被强制纠正成 1920×1080（打印 `[rtm] forcing 1920x1080`），`hidden` 只决定桌面弹不弹窗，画面逐帧一致。

## 不出片的参数（原因都在页面里写清了）

| 页 | 参数 | 原因 |
| --- | --- | --- |
| 01 | `pixel_width`/`pixel_height`/`quality`/`frame_rate`/`format`/`output_file`/`background_opacity`/`transparent`/`save_last_frame`/`write_to_movie`/`write_all`/`save_sections`/`zero_pad`/`movie_file_extension`/`from_animation_number`/`upto_animation_number`/`preview`/`show_in_file_browser`/`verbosity`/`progress_bar`/`disable_caching`/`flush_cache`/`max_files_cached`/`disable_caching_warning`/`dry_run`/`save_pngs`/`save_as_gif` | RTM 不读 manim `config`，改了无画面效果（`seed` 间接固定随机数、`renderer` 被内嵌 ManimCE 读取（别填），均不出片故不在本列） |
| 02 | `aspect_ratio`/`frame_size` | 只读（输出锁死 1920×1080），改不动 |
| 03 | `media_dir` 等成片路径键、`window_size` 等 12 个窗口键 | 同上（例外：`tex_dir`/`text_dir`/`assets_dir` 对**中间产物**生效，`tex_template`/`tex_template_file` **实际生效**，2026-10-17 实测——都不出片，故不进对照表） |
| 04 | `manim` 全部旗标与 `cfg`/`init`/`plugins`/`checkhealth` 子命令 | RTM 没有命令行入口 |
| 05 | `count_only` | 只数帧、不产文件（有控制台输出实测表） |
| 05 | `segment` | 产 BMP 目录而非 MP4 |
| 05 | `overwrite` | 只影响报不报 `FileExistsError` |
| 05 | `cleanup` | 只影响删不删 `media/` 临时目录 |
| 05 | `verbose` | 只影响控制台输出 |
| 05 | `MLWindow.enable_fast_record` 各参数 | 与 `fast_record_scene` 同名同义，画面见其样例 |

## 复现

```powershell
# RTM 版（每页不带参数 = 渲全部片段并拼出页面里的视频；片段落 assets\RTM code\final\，成片复制到 assets\ 根，仓库归档在 assets\RTM output\）
cd "RTM code"
python -X utf8 "01-画质与输出.py"
python -X utf8 "02-画幅坐标.py"
python -X utf8 "03-路径与窗口.py"
python -X utf8 "04-ManimCE命令行速查.py"
python -X utf8 "05-RTM的录制与窗口参数.py"
python -X utf8 "05-RTM的录制与窗口参数.py probes"   # 不产视频的参数探针

# ManimCE 对照版（同一个 MLWindow 垫片把 win.play 转成 self.play）
# 前置：需另行安装 ManimCE（pip install "real-time-manim[test]" 或 pip install manim）——
#       脚本内 python -m manim render 依赖 ManimCE 自带 CLI，RTM 不提供 manim 命令
cd "..\ManimCE code"
python -X utf8 "01-画质与输出-manimce.py"
python -X utf8 "02-画幅坐标-manimce.py"
python -X utf8 "03-路径与窗口-manimce.py"
python -X utf8 "04-ManimCE命令行速查-manimce.py"
python -X utf8 "05-RTM的录制与窗口参数-manimce.py"
```

RTM 只支持 1920×1080@60，`MLWindow(960, 540)` 会被强制纠正并打印一行提示，属正常。录制完打印 `[clean] removed ...media` 是正常清理。
