# 场景 四页样例视频（RTM / ManimCE 对比）

这些视频都由 `assets/RTM code/` 与 `assets/ManimCE code/` 下的源码渲染，页面只引用 **RTM** 那一版；
带 `-manimce` 的是同一份代码用 ManimCE 渲的（仅导入不同），留着自己对比，不进页面。

覆盖页面：`01-Scene基础.md`、`02-内容上屏.md`、`03-播放与等待.md`、`04-分段字幕与声音.md`。

## 对照表

### 01-Scene基础

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `Scene.__init__` | `random_seed=1` | `01-Scene基础-ctor_seed1.mp4`（60 帧 / 1.00s） | `01-Scene基础-ctor_seed1-manimce.mp4`（60 帧） | 对齐 |
| `Scene.__init__` | `random_seed=7` | `01-Scene基础-ctor_seed7.mp4`（60 帧 / 1.00s） | `01-Scene基础-ctor_seed7-manimce.mp4`（60 帧） | 对齐 |
| 生命周期 | `setup`→`construct`→`tear_down`（2026-10-16 起） | `01-Scene基础-life.mp4`（78 帧 / 1.30s） | `01-Scene基础-life-manimce.mp4`（78 帧） | 对齐 |
| `Scene.camera` / `Scene.time` | `self.time` 实时显示 | `01-Scene基础-time.mp4`（72 帧 / 1.20s） | `01-Scene基础-time-manimce.mp4`（72 帧） | 帧对齐（2026-10-17 重渲，`mean\|diff\|` 0.512→0.096） |

`01-Scene基础-ctor.mp4`（120 帧）是 `ctor_seed1` + `ctor_seed7` 两段拼接，也就是页面里嵌的那条。

### 02-内容上屏

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `Scene.add` | 加入顺序 = 绘制顺序 | `02-内容上屏-add.mp4`（90 帧 / 1.50s） | `02-内容上屏-add-manimce.mp4`（90 帧） | 对齐 |
| `Scene.remove` | 圆拿下屏露出方块 | `02-内容上屏-remove.mp4`（60 帧 / 1.00s） | `02-内容上屏-remove-manimce.mp4`（60 帧） | 对齐 |
| `Scene.clear` | 一键清屏换标题 | `02-内容上屏-clear.mp4`（60 帧 / 1.00s） | `02-内容上屏-clear-manimce.mp4`（60 帧） | 对齐 |
| 层次调整 | `bring_to_front`/`bring_to_back`/前景 | `02-内容上屏-zorder.mp4`（198 帧 / 3.30s） | `02-内容上屏-zorder-manimce.mp4`（198 帧） | 对齐 |
| `Scene.replace` | 三角原位换方块 | `02-内容上屏-replace.mp4`（60 帧 / 1.00s） | `02-内容上屏-replace-manimce.mp4`（60 帧） | 对齐 |

### 03-播放与等待

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `win.play` | 并行/run_time/rate_func/`.animate`/Write | `03-播放与等待-play.mp4`（168 帧 / 2.80s） | `03-播放与等待-play-manimce.mp4`（168 帧） | 对齐 |
| 等待 | `win.play(Wait(0.5))` | `03-播放与等待-wait_play.mp4`（48 帧 / 0.80s） | `03-播放与等待-wait_play-manimce.mp4`（48 帧） | 对齐 |
| 等待 | `self.wait(0.5)` | `03-播放与等待-wait_self.mp4`（48 帧 / 0.80s） | `03-播放与等待-wait_self-manimce.mp4`（48 帧） | 对齐 |
| 等待 | `self.pause(0.3)` | `03-播放与等待-wait_pause.mp4`（36 帧 / 0.60s） | `03-播放与等待-wait_pause-manimce.mp4`（36 帧） | 对齐 |
| 等待 | `self.wait_until(λ: True, 0.3)` | `03-播放与等待-wait_until.mp4`（19 帧 / 0.32s） | `03-播放与等待-wait_until-manimce.mp4`（19 帧 / 0.32s） | 对齐 |
| updater | mobject 级与场景级均 | `03-播放与等待-updater.mp4`（60 帧 / 1.00s） | `03-播放与等待-updater-manimce.mp4`（60 帧） | 对齐 |

`03-播放与等待-wait.mp4`（151 帧）是上面四段等待按顺序拼接的，与 `wait-manimce`（151 帧）逐帧一致。

### 04-分段字幕与声音

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `Scene.add_sound` | 两声“哔”@0.5s / 1.0s，gain +6dB / 0dB | `04-分段字幕与声音-sound.mp4`（132 帧 / 2.20s，带音轨） | `04-分段字幕与声音-sound-manimce.mp4`（132 帧，带音轨） | 对齐 |

两版 MP4 都能 ffprobe 到 AAC 音轨；按 50ms 窗口扫音量包络，两声“哔”都落在
**0.5s**（响，+6dB）和 **1.0s**（轻，0dB），RTM 与 ManimCE 完全一致。

## 对比结论

- **绝大多数样例逐帧对齐、画面几乎逐像素一致**。差别只在字重和抗锯齿
  （Cairo vs RTM 自己的光栅化），动画时序、位置、颜色、层叠顺序完全一样
  （2026-10-17 已把本页唯一一条修复前渲染的 `01-Scene基础-time.mp4` 重渲，`mean|diff|` 由 0.512 降到 0.096）。
  随机种子的排列两引擎也一致（seed=1 → 绿黄白蓝红，seed=7 → 白蓝黄红绿）。
- **四处差异已修复**（页面已同步；`03-播放与等待` 页与视频已重渲，`01-Scene基础` 两处的视频情况见各条注记）：
  1. `Scene.add_updater`：RTM 现在与 ManimCE 一样每帧驱动场景级 updater（`03-播放与等待-updater.mp4` 红方块跟着蓝方块一起上移）。
  2. `wait_until` 的 `stop_condition`：RTM 现在逐帧求值、条件为真立即结束（19 帧，与 ManimCE 相同；`wait_until` 与拼接后的 `wait.mp4` 均已重渲）。
  3. `self.time`（2026-10-16 修）：RTM 现在随出帧累加（每画出一帧 `renderer.time += dt`），与 ManimCE 同步递增；`01-Scene基础-time.mp4` 已于 2026-10-17 重渲（`mean|diff|` 0.512→0.096，标签逐帧与 ManimCE 同步）。
  4. `tear_down()`（2026-10-16 修）：record 生命周期（`record.py::scene_lifecycle`）改为 try/finally，正常与异常路径都保证调用一次（只跑用户钩子），RTM 现在同样在控制台打印 `tear_down ran`（`tests/test_gap_wait_timeline.py` 验证）。`life.mp4` 画面无变化（该样例的证据在控制台），视频沿用原片。
- **上游 manim 0.21 的两个小坑**（两引擎行为一致，只是计数时容易误会）：
  - `Wait` 自带一个空 `Mobject`（`Wait.mobject`），每次 `play` 一个 manim 的
    `Wait`（含 `self.wait`/`pause`/`wait_until`）就会往 `scene.mobjects` 塞一个
    空对象，`len(scene.mobjects)` / `get_top_level_mobjects()` 会多算；
    `win.play(Wait(...))`（RTM 的 `Wait`）没有这个问题。`02-内容上屏-replace`
    样例的第二条计数打印在 ManimCE 下是 3、RTM 下是 2，就是这个原因。
  - `add_foreground_mobject` 内部会再 `add` 一遍对象（`Scene.add` 的前景规则
    把它挪到列表末尾），所以 `remove_foreground_mobject` 只是退出前景名单，
    对象仍在列表末尾、依然画在最上层；想让它回到下层要自己 `bring_to_back`。
    `02-内容上屏-zorder` 样例把这一幕直接演了出来。
- **RTM 侧修复一处后才对齐的 bug**：`Scene.add_sound` 的落点原本取
  `win._cursor`，而时间轴播放路径从不推进它，导致中途加的声音全部堆在
  `time_offset` 处。已在 `real_time_manim/window/play.py` 的 `play()` 末尾
  补上 `self._cursor += tl.duration`，修复后两引擎的音轨落点一致（见上表）。

## 复现

```powershell
# RTM 版（逐片段 + 拼接；片段落 assets\RTM code\final\，成片复制到 assets\ 根，仓库里已归档进 assets\RTM output\）
cd assets\RTM code
python -X utf8 01-Scene基础.py
python -X utf8 02-内容上屏.py
python -X utf8 03-播放与等待.py
python -X utf8 04-分段字幕与声音.py

# ManimCE 对照版（片段落 assets\ManimCE code\out_manimce\，成片同样复制到 assets\ 根，仓库里归档进 assets\ManimCE output\）
# 前置：要另外安装 ManimCE（如 pip install "real-time-manim[test]" 或 pip install manim）——
#       脚本里 python -m manim render 依赖 ManimCE 自带的 CLI，RTM 本身不提供 manim 命令
cd ..\ManimCE code
python -X utf8 01-Scene基础-manimce.py
python -X utf8 02-内容上屏-manimce.py
python -X utf8 03-播放与等待-manimce.py
python -X utf8 04-分段字幕与声音-manimce.py

# 帧数核对
ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of csv=p=0 <文件>
```

RTM 只支持 1920×1080@60，`MLWindow(960, 540)` 会被强制纠正并打印一行提示，属正常。
`04` 的 `beep.wav` 是 code 目录里现成的 0.25s 演示音（`RTM code\beep.wav`、`ManimCE code\beep.wav` 各一份），`add_sound` 的相对路径
按**运行目录**解析，所以 RTM 版都从 `assets\RTM code` 下跑、对照版从 `assets\ManimCE code` 下跑。
