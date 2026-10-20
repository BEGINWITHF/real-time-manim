# Scene.play / wait / pause / wait_until 参数

驱动一切动画的入口。RTM 的场景不走 manim 的渲染器，播放统一写 `win.play(...)`，等待推荐写 `win.play(Wait(...))`。

## 参数

### `Scene.play`（RTM 写法：`win.play(...)`）

```python
Scene.play(*anims, subcaption=None, subcaption_duration=None, subcaption_offset=0, **kwargs)
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `*anims` | `Animation` / `.animate` 构建器 | — | 可以是**多个动画对象**（并行播放，总时长取最大 `run_time`），也可以是 `.animate` 构建器。**不接受**裸方法（`win.play(sq.shift, RIGHT)` 报 `TypeError`），也不接受裸 mobject |
| `subcaption` | `str \| None` | `None` | play 级字幕：RTM 的 `win.play` 内存收集字幕文本，与 `subcaption_duration` 配对；录制结束经 `export_srt()` 在 mp4 旁自动落盘 `.srt`（演示见[分段字幕与声音](../../01-场景与相机/场景/04-分段字幕与声音.md)）。`Scene.add_subcaption` 直调写入同一个 store、同样会落进 `.srt`（2026-10-19 复核，`tests/test_wiki_marked_gaps.py`） |
| `subcaption_duration` | `float \| None` | `None` | 每条字幕停留的秒数（配合 `subcaption`；本页无视频） |
| `subcaption_offset` | `float` | `0` | 字幕相对动画开始的偏移秒数（同上） |
| `**kwargs` | `Any` | — | 生效的关键字：`run_time=` 覆盖这条 play 里**每个**动画的时长、`rate_func=` 覆盖速率曲线（逐个 `setattr` 到动画实例），以及 `path_arc=` / `path_arc_axis=` / `path_arc_centers=` / `path_func=`（2026-10-17 起；manim 的 `apply_*` 会把弧转角经 `play(...)` 传播）。其余关键字（如 play 级 `lag_ratio=`）**不支持**：现在会打印明确警告（列出未识别项 + "RTM 不支持该参数"），不再静默吞掉；错峰要写在动画构造器或 `AnimationGroup` 上 |

> **返回**：无。要点：一次 `play` 的总时长 = `max(anim.run_time)`；可以一次播一个列表/生成器：`win.play(*[FadeIn(m) for m in mobs])`。

### `Wait` / `Scene.wait`

```python
# RTM 的等待动画（从 real_time_manim.vulkan_bind 导入），与 manim 的 Wait 同参
Wait(run_time=1.0, rate_func=None, stop_condition=None, frozen_frame=None, **kwargs)

def wait(self, duration=DEFAULT_WAIT_TIME, stop_condition=None, frozen_frame=None) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `duration` / `run_time` | `float` | `DEFAULT_WAIT_TIME`（=1.0） | 等待秒数。**能填**任意正数；推荐写 `win.play(Wait(1.2))`，`Scene.wait(1.2)` 等价（内部就是播一个 `Wait`） |
| `stop_condition` | `Callable[[], bool] \| None` | `None` | 每帧求值：每帧绘制完成后调用一次，为真就提前结束等待；与 `frozen_frame=True` 互斥，同时给会 `ValueError`。见[播放与等待（场景篇）](../../01-场景与相机/场景/03-播放与等待.md) |
| `frozen_frame` | `bool \| None` | `None` | `True` = 等待期间 updaters 一律不驱动、画面定格；`False` = 照常逐帧步进；`None`（默认）自动判定——没有任何 updater 时冻结，否则步进 |

> **返回**：无。

### `Scene.pause` / `Scene.wait_until`

```python
def pause(self, duration=DEFAULT_WAIT_TIME) -> None:
def wait_until(stop_condition, max_time=60) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `duration`（pause） | `float` | `1.0` | `pause` = `wait(..., frozen_frame=True)`：强制静帧暂停，期间 updaters 不驱动、画面定格 |
| `stop_condition`（wait_until） | `Callable[[], bool]` | — | 每帧求值，条件为真立即结束等待（不到 `max_time` 也行）；只在正向播放时生效，随机访问抽帧仍按完整时长渲染 |
| `max_time` | `float` | `60` | 等待的时长上限；`stop_condition` 提前为真就不到这个时长 |

> **返回**：无。

#### 样例：win.play 的并行/覆盖参数与 Wait 等待

一次 `play` 播多个动画、play 级 `run_time=1.6` / `rate_func=linear` 逐个 setattr 到每个动画、列表展开 `win.play(*[FadeIn(m) for m in dots])`，最后 `win.play(Wait(1.2))` 静止 1.2 秒。

```python
import os
from real_time_manim import (
    BLUE,
    DOWN,
    GREEN,
    GREY_B,
    LEFT,
    ORANGE,
    PURPLE,
    RED,
    RIGHT,
    UP,
    YELLOW,
    Circle,
    Dot,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
    linear,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401

class Page_02_play与wait参数(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w / h / hidden
        win.scene = self                          # 参数 win.scene

        title = Text("02-Scene.play / wait 参数（win.play 等价）", font_size=42, color=YELLOW).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # —— 步骤 1：一次 play 多个动画 + play 级 run_time / rate_func ——
        l1 = Text("win.play(Create(sq), FadeIn(ci, scale=0.5),", font_size=30, color=GREY_B)
        l2 = Text("         run_time=1.6, rate_func=linear)   # 逐个 setattr", font_size=30, color=GREY_B)
        sig1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.05)
        sq = Square(side_length=1.3, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 2.4 + DOWN * 2.0)
        ci = Circle(radius=0.68, color=GREEN).set_fill(GREEN, 0.5).shift(RIGHT * 2.4 + DOWN * 2.0)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.4)
        win.play(
            Create(sq),                          # 参数 *anims 之 Create
            FadeIn(ci, scale=0.5),               # 参数 *anims 之 FadeIn(scale)
            run_time=1.6,                        # 参数 **kwargs: run_time（两个动画都被拉到 1.6s）
            rate_func=linear,                    # 参数 **kwargs: rate_func
        )
        win.play(FadeOut(VGroup(sig1, sq, ci)), run_time=0.4)

        # —— 步骤 2：列表展开：win.play(*[FadeIn(m) for m in dots]) ——
        l3 = Text("win.play(*[FadeIn(m, shift=DOWN) for m in dots])",
                  font_size=30, color=GREY_B).to_edge(UP).shift(DOWN * 1.05)
        cols = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        dots = VGroup(*[Dot(radius=0.16, color=c).shift(LEFT * 5 + RIGHT * 2 * i + DOWN * 1.9)
                        for i, c in enumerate(cols)])
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)
        win.play(*[FadeIn(m, shift=DOWN) for m in dots])          # 参数 *anims（列表/生成器展开）
        win.play(Wait(0.4))
        win.play(FadeOut(VGroup(l3, dots)), run_time=0.4)

        # —— 步骤 3：Wait(duration)：≈ Scene.wait(duration) ——
        l4 = Text("win.play(Wait(1.2))   #  ≡  self.wait(1.2)", font_size=30, color=GREY_B)
        l4.to_edge(UP).shift(DOWN * 1.05)
        tr = Triangle(color=ORANGE).scale(0.8).set_fill(ORANGE, 0.5).shift(DOWN * 1.9)
        txt = Text("静止 1.2 秒", font_size=30, color=GREY_B).next_to(tr, DOWN, buff=0.45)
        win.play(FadeIn(l4, shift=DOWN), FadeIn(tr), FadeIn(txt), run_time=0.4)
        win.play(Wait(1.2))                                        # 参数 duration=1.2
        win.play(Wait(0.4))

        win.play(FadeOut(VGroup(title, l4, tr, txt)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_02_play与wait参数,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "02-play与wait参数.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
```

这段代码在做什么：三步走——① 一条 `win.play` 同时 `Create(sq)` 和 `FadeIn(ci, scale=0.5)`，并用 play 级 `run_time=1.6, rate_func=linear` 把两个动画都拉成 1.6 秒匀速（逐个 setattr 的效果）；② 用列表展开一次性 `FadeIn` 六个彩色圆点（`*anims` 接受生成器/列表）；③ 放一个三角和"静止 1.2 秒"的说明，用 `win.play(Wait(1.2))` 完整等 1.2 秒，画面纹丝不动。

<video src="assets/RTM output/02-play与wait参数.mp4" controls width="560"></video>

> 提醒：`win.play(...)` 的关键字里 `run_time` / `rate_func` 生效，`path_arc` / `path_arc_axis` / `path_arc_centers` / `path_func` 也生效（2026-10-17 起，manim 的 `apply_*` 靠这条把弧转角传进来），其余会打印"RTM 不支持该参数"的明确警告（不再静默吞掉）——看到警告就检查是不是误写在了 play 级。`Wait` 用 `real_time_manim.vulkan_bind` 里的那一个，别导 manim 的 `Wait`。

> **2026-10-16 更新**：play 级 `subcaption` 三形参已接线（内存收集 + `export_srt()`，录制结束在 mp4 旁自动落盘 `.srt`；`Scene.add_subcaption` 直调写入同一个 store，2026-10-19 复核）；play 级未识别关键字现在打印明确警告而非静默忽略；`Scene.pause`（= `wait(..., frozen_frame=True)`，真静帧）与 `Scene.wait_until`（条件每帧求值、为真即截断）均已实装。

无法演示：`subcaption` / `subcaption_duration` / `subcaption_offset` —— play 级三形参已支持（内存收集 + `export_srt`，录制结束在 mp4 旁自动落盘 `.srt`），本页不演示，见[分段字幕与声音](../../01-场景与相机/场景/04-分段字幕与声音.md)；`Scene.add_subcaption` 直调也写同一个 store（2026-10-19 复核）；`Scene.pause` / `Scene.wait_until` 与 `Wait` 的 `stop_condition` / `frozen_frame` —— 已支持，本页不演示，见[播放与等待（场景篇）](../../01-场景与相机/场景/03-播放与等待.md)；play 级 `lag_ratio` —— 无视频：RTM 的 `win.play` 覆盖 `run_time` / `rate_func`（以及 2026-10-17 起的 `path_arc` / `path_arc_axis` / `path_arc_centers` / `path_func`）这几个关键字，误传会打印"RTM 不支持该参数"警告（不再静默），错峰要写在动画构造器或 `AnimationGroup` 上。

---

相关：[生命周期与公共参数](01-生命周期与公共参数.md) · [.animate 语法](03-animate语法.md) · [播放与等待（场景篇）](../../01-场景与相机/场景/03-播放与等待.md)
