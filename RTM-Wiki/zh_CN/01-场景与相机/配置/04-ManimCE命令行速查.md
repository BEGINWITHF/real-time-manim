# ManimCE 命令行速查（RTM 不支持）

RTM **没有命令行**：不装 `manim` CLI 那套旗标，画幅由 `MLWindow(w, h)` 决定、输出由 `fast_record_scene` / `record_scene` 的 `out_path` / `fps` 决定。

本页是全 wiki 唯一放 ManimCE 内容的地方，把 `manim [选项] 文件名.py [场景名 ...]` 的旗标逐条速查，并给 RTM 的等价做法——所有旗标对 RTM 一律（不存在）。

## 参数

### 渲染主参数（RTM 无 CLI）

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `-ql` | 档位 | — | 低画质 854×480 @ 15 FPS。RTM 等价：没有——固定 1920×1080@60 |
| `-qm` | 档位 | — | 中画质 1280×720 @ 30 FPS。RTM 等价：同上 |
| `-qh` | 档位 | 默认 | 高画质 1920×1080 @ 60 FPS。RTM 的固定输出就是这一档 |
| `-qp` | 档位 | — | 生产画质 2560×1440 @ 60 FPS。RTM 等价：同上 |
| `-qk` | 档位 | — | 4K 3840×2160 @ 60 FPS。RTM 等价：同上 |
| `-r, --resolution W,H` | `W,H` | 取自 `manim.cfg` | 自定义分辨率（`W;H`、`W,H`、`W-H` 均可）。RTM 等价：`MLWindow(w, h)`，只能 1920×1080 |
| `--fps, --frame_rate F` | `float` | `60` | 自定义帧率。RTM 等价：`fast_record_scene(fps=...)`，只能 60 |
| `--format [png\|gif\|mp4\|webm\|mov]` | 枚举 | `mp4` | 输出格式（`png`=只出图）。RTM：只出 mp4；逐帧出图用 `segment=(...)` |
| `-o, --output_file 名称` | `str` | 自动命名 | 指定输出文件名。RTM 等价：`out_path="my_video.mp4"` |
| `--media_dir 路径` | 路径 | `./media` | 视频/LaTeX 等所有产物的根目录。RTM 等价：`out_path` 直接给文件路径 |
| `-s, --save_last_frame` | 标志 | 关 | 只渲染并保存最后一帧 PNG（不产视频）。RTM 等价：`segment=(n, n+1)` 导 BMP |
| `-n, --from_animation_number start[;end]` | `int` | `0` | 从第 `start` 个 `play` 开始渲染；分隔符 `;` `,` `-` 都行（shell 里 `;` 要加引号，写 `3;7` 或 `3-7`）。RTM：自己注释/删掉前面的 `win.play(...)` |
| `-a, --write_all` | 标志 | 关 | 渲染脚本里的全部场景。RTM：自己在脚本里逐个调用 |
| `--save_sections` | 标志 | 关 | 按 `next_section` 另存每段视频。RTM：拆成多个场景分别录 |
| `--renderer [cairo\|opengl]` | 枚举 | `cairo` | 选择渲染器。RTM：自己的 Vulkan 渲染器，没得选 |
| `--disable_caching` | 标志 | 关 | 关闭片段缓存。RTM：本来就没有缓存 |
| `--flush_cache` | 标志 | 关 | 删除所有已缓存的片段。RTM：同上 |
| `--seed N` | `int` | 未设 | 随机种子。RTM 等价：`Scene` 构造参数 `random_seed=...` |
| `-t, --transparent` | 标志 | 关 | 透明背景（输出 `.mov`/`.webm`）。RTM：输出永远不透明 |
| `-g, --save_pngs` | 标志 | 关 | 逐帧存 PNG（**已弃用**，用 `--format png`）。RTM：`segment=(...)` 导 BMP |
| `-i, --save_as_gif` | 标志 | 关 | 存 GIF（**已弃用**，用 `--format gif`）。RTM：不出 GIF |
| `--dry_run` | 标志 | 关 | 只跑流程不写文件、不开窗口。RTM 等价：`count_only=True`（只数帧） |

### 全局 / 输出 / 易用性旗标与子命令（RTM 无 CLI）

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `-c, --config_file 路径` | 路径 | 无 | 指定配置文件（**注意**：背景色没有 `-c` 旗标）。RTM：不读配置文件 |
| `-v, --verbosity` | 枚举 | `INFO` | 日志级别 `DEBUG/INFO/WARNING/ERROR/CRITICAL`。RTM 等价：`verbose=...` |
| `--progress_bar` | 枚举 | `display` | 进度条 `display` / `leave`（渲染后保留）/ `none`（不显示）。RTM：只打一行 `[FastRecord] Saved: ...` |
| `-p, --preview` | 标志 | 关 | 渲染完用播放器打开（OpenGL 为实时预览窗口）。RTM 等价：`hidden=False` 或 `record_scene` |
| `-f, --show_in_file_browser` | 标志 | 关 | 在文件管理器里显示输出文件 |
| `--custom_folders` | 标志 | 关 | 使用配置文件 `[custom_folders]` 的目录结构 |
| `--log_dir 路径` | 路径 | — | 日志目录。RTM：不写日志文件 |
| `--log_to_file` | 标志 | 关 | 把日志写文件。RTM：同上 |
| `--tex_template 路径` | 路径 | 默认模板 | 自定义 LaTeX 模板。RTM 侧入口是 `config.tex_template` / `config.tex_template_file`（**实际生效**，2026-10-17 实测，见 [03-路径与窗口](03-路径与窗口.md)），只是没有命令行旗标 |
| `--notify_outdated_version / --silent` | 标志 | 开 | 是否提示新版本 |
| `--no_latex_cleanup` | 标志 | 关 | 保留 LaTeX 中间文件。RTM 等价：`cleanup=False`（保留整个 `media/`） |
| `--enable_gui` | 标志 | 关 | OpenGL GUI 面板 |
| `--gui_location x,y` | `x,y` | `0,0` | GUI 面板位置 |
| `--fullscreen` | 标志 | 关 | 窗口全屏 |
| `--force_window` | 标志 | 关 | 强制开窗口。RTM 等价：`hidden=False` |
| `--enable_wireframe` | 标志 | 关 | OpenGL 线框调试 |
| `--jupyter` | 标志 | 关 | Jupyter magic 用（不立即渲染） |
| `--preview_command 命令` | `str` | 无 | 自定义预览命令 |

其它子命令（全部不支持）：**`manim cfg`** 管理 `manim.cfg`（`write`/`show`/`export -d 目录`）；**`manim init`** 脚手架（`project`/`scene`）；**`manim plugins -l`** 列出插件；**`manim checkhealth`** 安装体检。

> 提醒：这张表在 RTM 里不是「填了不生效」，而是**根本没有这些入口**——`manim` 命令**只有另外安装了 ManimCE 的环境**才有（RTM 本身不提供：`real_time_manim/manim/` 删掉了 `cli/` 与 `__main__.py`，`pyproject.toml` 也没有 console script）。
>
> 只装 RTM 时装不出 `manim` 命令；另装 ManimCE 后它照样能跑，只是渲出来的是 CE 画面。想用 RTM 渲，就写 Python 脚本调 `fast_record_scene` / `record_scene`。两边的画面对比可以看 `assets/README.md`。

### manim 命令 ↔ RTM 调用

下面两条样例把最常用的对照画了出来。命令行照抄可用：

```bash
# ManimCE：命令行渲染
manim -qh -o my_video --fps 60 scene.py Hello
```

```python
# RTM：函数调用（同样的效果）
from real_time_manim.record import fast_record_scene
fast_record_scene(Hello, out_path="my_video.mp4", fps=60)
```

#### 样例：画质档位 `-q`

五个档位和 RTM 的固定档位上屏对照：ManimCE 可以在 854×480@15 到 4K@60 之间挑，RTM 只有 1920×1080@60 一档。

```python
from manim import (
    Scene, Text, VGroup,
    ORANGE, GREY_B, YELLOW, GREEN, UP, DOWN, LEFT,
    Write, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class QualityTiersDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        rows = VGroup(
            Text("-ql    854x480 @ 15", font_size=32, color=GREY_B),
            Text("-qm    1280x720 @ 30", font_size=32, color=GREY_B),
            Text("-qh    1920x1080 @ 60", font_size=32, color=YELLOW),
            Text("-qp    2560x1440 @ 60", font_size=32, color=GREY_B),
            Text("-qk    3840x2160 @ 60", font_size=32, color=GREY_B),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)   #五档画质从上到下排好
        note = Text("RTM = 1920x1080 @ 60 only", font_size=34,
                    color=ORANGE).to_edge(DOWN, buff=0.7)   #RTM 只有这一档
        self.add(rows)   #把五档画质放进场景
        win.play(FadeIn(rows, shift=UP * 0.2), run_time=0.8)   #五档画质淡入
        win.play(Write(note), run_time=0.7)   #写出 RTM 的固定档位
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：把 `-ql` 到 `-qk` 五个画质档位（分辨率 @ 帧率）排成一列淡入上屏，`-qh` 高亮标黄——它就是 RTM 的固定输出档；最后在画面底部写出「RTM = 1920x1080 @ 60 only」。

看这条视频记住一件事就够了：**RTM 不分档**，传什么尺寸/帧率都会被强制纠正成 1080p60（强制提示的实拍见 [05-RTM的录制与窗口参数](05-RTM的录制与窗口参数.md) 的 `MLWindow` 样例）。

<video src="assets/RTM output/04-ManimCE命令行速查-quality_tiers.mp4" controls width="560"></video>

> 提醒：`-q` 档位和 `--fps` 在 RTM 里没有任何入口；你在 `MLWindow(w, h)` 或 `fast_record_scene(fps=...)` 里填的值只起到「触发一行强制提示」的作用。想要低清预览快点出片，只能渲完用 ffmpeg 缩。

#### 样例：命令行 ↔ RTM 调用

一条 ManimCE 命令和它的 RTM 等价调用上下对照：出的片子一样，入口一个是命令行、一个是函数。

```python
from manim import (
    Scene, Text, VGroup,
    ORANGE, GREY_B, YELLOW, GREEN, UP, DOWN, LEFT,
    Write, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class CliEquivDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        cli = Text("manim -qh -o my_video --fps 60 scene.py Hello",
                   font_size=30, color=ORANGE).shift(UP * 1.2)   #ManimCE 的命令行
        same = Text("same output", font_size=26, color=GREY_B)   #两行中间的说明
        call = Text("fast_record_scene(Hello, out_path='my_video.mp4', fps=60)",
                    font_size=30, color=GREEN).shift(DOWN * 1.2)   #RTM 的函数调用
        self.add(cli, same, call)   #把三行文字放进场景
        win.play(FadeIn(cli, shift=UP * 0.2), run_time=0.6)   #先上命令行
        win.play(FadeIn(same), run_time=0.4)   #再上中间的说明
        win.play(FadeIn(call, shift=DOWN * 0.2), run_time=0.6)   #最后上 RTM 调用
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：三行文字依次淡入——上面是 ManimCE 的完整命令 `manim -qh -o my_video --fps 60 scene.py Hello`，中间一行 "same output" 说明两者出片相同，下面是 RTM 的等价调用 `fast_record_scene(Hello, out_path='my_video.mp4', fps=60)`。

记忆点：命令行里的 `-o 名称` 对应 `out_path`、`--fps` 对应 `fps`、文件名/场景名的位置参数对应函数的第一个参数。

<video src="assets/RTM output/04-ManimCE命令行速查-cli_equiv.mp4" controls width="560"></video>

> 提醒：`fast_record_scene` 的第二参数直接就是**文件路径**（带 `.mp4`），不是命令行那种「不带扩展名的名字」；场景参数可以是类、实例或无参可调用（见 [05-RTM的录制与窗口参数](05-RTM的录制与窗口参数.md) 的 `scene` 样例）。

**总结**：ManimCE 的命令行旗标在 RTM 里全部不存在；画质固定 1080p60、输出由 `out_path`/`fps` 两个参数给、想看效果用 `hidden=False` 或 `record_scene`。

真要跑 ManimCE 的命令行（比如只为出低清草稿），先另装 ManimCE（`pip install "real-time-manim[test]"` 或 `pip install manim`），之后 `manim` 命令照常用——只是那不是 RTM 的画面。

两条样例两引擎逐像素一致（120 帧 / 2.00s、126 帧 / 2.10s）。

---

相关：[01-画质与输出](01-画质与输出.md) ｜ [03-路径与窗口](03-路径与窗口.md) ｜ [05-RTM 的录制与窗口参数](05-RTM的录制与窗口参数.md)
