"""RTM-Wiki · 03-动画/文字与数字/01-逐字出现与消失 —— 本页专属样例

演示参数（文档「参数」表逐条）：
    AddTextLetterByLetter(text, suspend_mobject_updating=False, int_func=np.ceil,
                          rate_func=linear, time_per_char=0.25, run_time=2.4,
                          reverse_rate_function=False, introducer=True)                 ✓
    RemoveTextLetterByLetter(text, suspend_mobject_updating=False, int_func=np.ceil,
                             rate_func=linear, time_per_char=0.2, run_time=2.0,
                             reverse_rate_function=True, introducer=False, remover=True) ✓
不演示：`AddTextWordByWord`（`text_mobject` / `run_time` / `time_per_char`）——
        上游源码标注 `# TODO, this is broken...`：对普通 `Text` 切词为空，ManimCE 自身
        渲染同样是静止画面（忠实复现，不是 RTM 缺口），页面也标注"不建议在新脚本中使用"。
运行：python "<本文件>"（脚本会自行把仓库根目录加入 sys.path）
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

import numpy as np
from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    RED,
    DOWN,
    UP,
    AddTextLetterByLetter,
    RemoveTextLetterByLetter,
    Scene,
    Text,
    VGroup,
    linear,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  文件末尾 __main__ 使用


class Page_01_逐字出现与消失(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w=1280 / h=720 / hidden=True
        win.scene = self                          # 参数 win.scene

        title = Text("AddTextLetterByLetter / RemoveTextLetterByLetter",
                     font_size=34, color=GREEN).to_edge(UP)   #标题只用 ASCII：两引擎字体回退才稳
        win.play(Write(title), run_time=0.85)

        # —— 步骤 1：AddTextLetterByLetter(...) ——
        s1a = Text("AddTextLetterByLetter(txt, suspend_mobject_updating=False,",
                   font_size=28, color=GREY_B)
        s1b = Text("    int_func=np.ceil, rate_func=linear, time_per_char=0.25,",
                   font_size=28, color=GREY_B)
        s1c = Text("    run_time=2.4, reverse_rate_function=False, introducer=True)",
                   font_size=28, color=GREY_B)
        sig1 = VGroup(s1a, s1b, s1c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        a01 = Text("Typing...", font_size=50, color=BLUE).next_to(sig1, DOWN, buff=0.9)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        win.play(
            AddTextLetterByLetter(
                a01,                                   # 参数 text ✓（只支持 Text）
                suspend_mobject_updating=False,        # 参数 suspend_mobject_updating=False ✓
                int_func=np.ceil,                      # 参数 int_func=np.ceil ✓（到达即显示）
                rate_func=linear,                      # 参数 rate_func=linear ✓（匀速打字）
                time_per_char=0.25,                    # 参数 time_per_char=0.25 ✓（默认 0.1）
                run_time=2.4,                          # 参数 run_time=2.4 ✓（不传则按字符数自动算）
                reverse_rate_function=False,           # 参数 reverse_rate_function=False ✓
                introducer=True,                       # 参数 introducer=True ✓（播前加入场景）
            ),
        )
        win.play(Wait(0.3))
        win.play(FadeOut(sig1), FadeOut(a01), run_time=0.45)

        # —— 步骤 2：RemoveTextLetterByLetter(...) ——
        s2a = Text("RemoveTextLetterByLetter(txt, suspend_mobject_updating=False,",
                   font_size=28, color=GREY_B)
        s2b = Text("    int_func=np.ceil, rate_func=linear, time_per_char=0.2,",
                   font_size=28, color=GREY_B)
        s2c = Text("    run_time=2.0, reverse_rate_function=True, introducer=False,",
                   font_size=28, color=GREY_B)
        s2d = Text("    remover=True)", font_size=28, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c, s2d).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        b01 = Text("Vanishing", font_size=50, color=RED).next_to(sig2, DOWN, buff=0.7)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        self.add(b01)                                  # 参数 introducer=False → 先手动放进场景
        win.play(
            RemoveTextLetterByLetter(
                b01,                                   # 参数 text ✓
                suspend_mobject_updating=False,        # 参数 suspend_mobject_updating=False ✓
                int_func=np.ceil,                      # 参数 int_func=np.ceil ✓
                rate_func=linear,                      # 参数 rate_func=linear ✓
                time_per_char=0.2,                     # 参数 time_per_char=0.2 ✓
                run_time=2.0,                          # 参数 run_time=2.0 ✓
                reverse_rate_function=True,            # 参数 reverse_rate_function=True ✓（与父类 False 不同）
                introducer=False,                      # 参数 introducer=False ✓（与父类 True 不同）
                remover=True,                          # 参数 remover=True ✓（播完移出场景）
            ),
        )
        win.play(FadeOut(sig2), run_time=0.45)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_01_逐字出现与消失,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "01-逐字出现与消失.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
