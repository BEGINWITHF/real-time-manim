# RTM-Wiki（中文手册）

Real-Time-Manim（RTM）的中文使用手册快照：**122 页**、9 个章节、**367 条**样例成片。

每个 API 一节，每节配一条样例视频；参数表里写清"能填什么 / 不建议填什么 / 不生效的原因"。

## 目录结构

```
RTM-Wiki/
├─ README.md              ← 本文件（总览）
└─ zh_CN/
   ├─ 00-新手入门/         6 页   下载与安装、快速开始、三种录制方法、ManimCE/ManimGL 用户指南、使用 LLM 与 Agent
   ├─ 01-场景与相机/      17 页   场景生命周期、播放、专用场景、相机、config
   ├─ 02-Mobject通用/     16 页   构造与容器、摆放、测量、变形、样式、复制、更新器
   ├─ 03-动画/             32 页   创建擦除、淡入淡出、变换、强调、生长、移动旋转、编排、文字数字
   ├─ 04-图形与文本/       23 页   几何、线箭头、多边形、标注、布尔、样式、Text/LaTeX/Typst/矩阵/表格/图片
   ├─ 05-坐标系与图表/     14 页   数轴、Axes、换算、网格、曲线、面积、极坐标、BarChart、刻度
   ├─ 06-三维/              5 页   三维基本体、表面、多面体、工具函数
   ├─ 07-图论与向量场/      4 页   Graph/DiGraph、向量场、流线
   └─ 08-工具/              6 页   颜色、速率函数、方向常量、向量与几何工具
```

每章内：

```
<章>/README.md             该章索引（页面列表 + 每页样例视频与源码入口）
<章>/<页>.md               正文（标题 + 导语 + 每函数一节：签名 / 参数表 / 样例代码 / 视频 / 提醒）
<章>/assets/RTM output/    该章样例成片（页面里嵌的就是这些 mp4）
<章>/assets/RTM code/      生成这些成片的 demo 脚本（页面代码块与它逐字一致）
```

## 怎么读

1. 先看对应章的 `README.md`，按需点进具体页面；
2. 页面结构固定：**一个函数（或一组参数）一节**，节内有签名、参数表、完整样例代码、样例视频、可选提醒；
3. 参数表里：`能填` = 可用取值；`不建议` = 能填但别填；`不接线 / 未接线` = RTM 不会读它（替代写法在说明里）；
4. 视频只为演示参数效果，判读以参数表和"这段代码在做什么"的文字为准。

## 怎么跑出样例

样例脚本只依赖 RTM 本身（`fast_record_scene` 离线渲染，无需窗口）：

```powershell
# 单页：渲染该页全部样例并拼成页面里的视频（输出到 assets/RTM output/）
python "...\RTM-Wiki\zh_CN\04-图形与文本\assets\RTM code\12-数字与变量.py"

# 只渲染其中一条
python "...\RTM-Wiki\zh_CN\04-图形与文本\assets\RTM code\12-数字与变量.py" decimal
```

- 输出固定 **1920×1080@60**（脚本里写 `MLWindow(960, 540)` 会被纠正并打印一行提示，属正常）；
- 跑脚本需要 `PYTHONPATH` 指向 real-time-manim 仓库根目录（或直接在该仓库里运行）；
- 每页的 `<video>` 都在 `assets/RTM output/` 下，文件名形如 `<页名>-<样例名>.mp4`。

## 缓存（三层，清理方式各不相同）

| 缓存 | 位置 | 省掉什么 | 怎么清 |
| --- | --- | --- | --- |
| LaTeX / Typst 公式 | `media/Tex`（+ `tex_cache/`） | 重新编译公式 | `clear_tex_cache()`（`dry_run=True` 只预览） |
| 文本 → SVG（Pango） | `media/texts/<hash>.svg` | 重新排版，约 2 ms/条 | `clear_media()`，或录制器默认的 `cleanup=True` |
| 解析后的 SVG → mobject | 进程内存 `SVG_HASH_TO_MOB_MAP` | `svgelements` 解析 + 每个字形建一个 VMobject，4–20 ms/条 | 进程结束自动释放；单个 `Text(use_svg_cache=False)` 可退出 |

```python
from real_time_manim import (
    restore_tex_cache, save_tex_cache, clear_tex_cache, clear_media,
)

restore_tex_cache("tex_cache")   # 渲染前：把保存的公式 SVG 放回 media/Tex
save_tex_cache("tex_cache")      # 渲染后：把新编译的公式存起来
clear_tex_cache()                # 清 media/Tex 与 tex_cache/（dry_run=True 预览）
clear_media()                    # 清整个 media/，包括 media/texts
```

- **`clear_tex_cache()` 不碰 `media/texts`**：文本 SVG 要用 `clear_media()`（或 `cleanup=True`）。
- `fast_record_scene(..., cleanup=True)` 是默认值，每录一次就删掉整个 `media/`，磁盘上的文本缓存只活一次渲染；要跨次复用请传 `cleanup=False`。
- 文本文件的 hash 含内容与样式（字体、字号、颜色、`t2c`、行距、连字），红字和蓝字是两个文件。
- 内存缓存为 FIFO、上限 256 条，且从同一字符串的**第二次**构建才开始写入；重复标签构造约快 2.5 倍，`DecimalNumber` 的每个新值都不会被拖慢。

