"""RTM-Wiki · 03-动画/文字与数字/01b-带光标打字 —— 本页专属样例

演示参数（文档「参数」表逐条）：
    TypeWithCursor(text, cursor, buff=0.12, keep_cursor_y=True, leave_cursor_on=True,
                   time_per_char=0.14, reverse_rate_function=False, introducer=True)   ✓
    UntypeWithCursor(text, cursor, buff=0.12, keep_cursor_y=True, leave_cursor_on=True,
                     time_per_char=0.14, reverse_rate_function=True,
                     introducer=False, remover=True)                                   ✓
    Blink(cursor, time_on=0.3, time_off=0.3, blinks=2)  ← 页面示例里的光标闪烁组合      ✓
不演示：`cursor` 的"颜色参数"不在动画签名里 —— 光标就是个 mobject，颜色在创建
        Rectangle 时给（样例用 RED，页面示例用 GREY_A）；`**kwargs` 其余上游通用参数无可视效果。
运行：python "<本文件>"（脚本会自行把仓库根目录加入 sys.path）
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    GREEN,
    GREY_B,
    PURPLE,
    RED,
    DOWN,
    UP,
    Rectangle,
    Scene,
    Text,
    VGroup,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Blink,
    FadeIn,
    FadeOut,
    TypeWithCursor,
    UntypeWithCursor,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  文件末尾 __main__ 使用


class Page_01b_带光标打字(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w=1280 / h=720 / hidden=True
        win.scene = self                          # 参数 win.scene

        title = Text("TypeWithCursor / UntypeWithCursor",
                     font_size=34, color=GREEN).to_edge(UP)   #标题只用 ASCII：两引擎字体回退才稳
        win.play(Write(title), run_time=0.85)

        # —— 步骤 1：TypeWithCursor(text, cursor, buff, keep_cursor_y,
        #                           leave_cursor_on, time_per_char, ...) ——
        s1a = Text("TypeWithCursor(txt, cursor,", font_size=28, color=GREY_B)
        s1b = Text("    buff=0.12, keep_cursor_y=True, leave_cursor_on=True,",
                   font_size=28, color=GREY_B)
        s1c = Text("    time_per_char=0.14, reverse_rate_function=False,",
                   font_size=28, color=GREY_B)
        s1d = Text("    introducer=True)", font_size=28, color=GREY_B)
        sig1 = VGroup(s1a, s1b, s1c, s1d).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.3)
        txt01 = Text("Inserting", color=PURPLE, font_size=52).next_to(sig1, DOWN, buff=0.6)
        cur01 = Rectangle(color=RED, fill_color=RED, fill_opacity=1,   # 光标颜色：创建 cursor 时给
                          height=1.0, width=0.14).move_to(txt01[0])
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        win.play(
            TypeWithCursor(
                txt01,                                # 参数 text ✓
                cur01,                                # 参数 cursor ✓（细矩形光标，RED）
                buff=0.12,                            # 参数 buff=0.12 ✓（默认 0.1：光标与末字符间距）
                keep_cursor_y=True,                   # 参数 keep_cursor_y=True ✓（y 锁在整段中心）
                leave_cursor_on=True,                 # 参数 leave_cursor_on=True ✓（播完留下光标）
                time_per_char=0.14,                   # 参数 time_per_char=0.14 ✓（默认 0.1）
                reverse_rate_function=False,          # 参数 reverse_rate_function=False ✓
                introducer=True,                      # 参数 introducer=True ✓（播前加入场景）
            ),
            Wait(1.6),                                # 比自动 run_time(=0.14*9=1.26s) 略长，末帧 alpha 才到 1
        )
        win.play(                                     # 页面示例：打完让光标闪两下
            Blink(
                cur01,                                # 参数 mobject ✓
                time_on=0.3,                          # 参数 time_on=0.3 ✓
                time_off=0.3,                         # 参数 time_off=0.3 ✓
                blinks=2,                             # 参数 blinks=2 ✓
            ),
            run_time=1.2,
        )
        win.play(FadeOut(sig1), FadeOut(txt01), FadeOut(cur01), run_time=0.5)

        # —— 步骤 2：UntypeWithCursor(text, cursor, ..., reverse_rate_function=True,
        #                             introducer=False, remover=True) ——
        s2a = Text("UntypeWithCursor(txt, cursor,", font_size=28, color=GREY_B)
        s2b = Text("    buff=0.12, keep_cursor_y=True, leave_cursor_on=True,",
                   font_size=28, color=GREY_B)
        s2c = Text("    time_per_char=0.14, reverse_rate_function=True,",
                   font_size=28, color=GREY_B)
        s2d = Text("    introducer=False, remover=True)", font_size=28, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c, s2d).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.3)
        txt02 = Text("Deleting", color=PURPLE, font_size=52).next_to(sig2, DOWN, buff=0.6)
        cur02 = Rectangle(color=RED, fill_color=RED, fill_opacity=1,
                          height=1.0, width=0.14).move_to(txt02[0])
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        self.add(txt02, cur02)                        # 参数 introducer=False → 先手动放进场景
        win.play(
            UntypeWithCursor(
                txt02,                                # 参数 text ✓
                cur02,                                # 参数 cursor ✓
                buff=0.12,                            # 参数 buff ✓（继承 TypeWithCursor）
                keep_cursor_y=True,                   # 参数 keep_cursor_y ✓
                leave_cursor_on=True,                 # 参数 leave_cursor_on ✓
                time_per_char=0.14,                   # 参数 time_per_char=0.14 ✓
                reverse_rate_function=True,           # 参数 reverse_rate_function=True ✓（与父类 False 不同）
                introducer=False,                     # 参数 introducer=False ✓（与父类 True 不同）
                remover=True,                         # 参数 remover=True ✓（播完移出场景）
            ),
            Wait(1.6),                                # 同上：把时长撑开，末帧 alpha 才到 1
        )
        win.play(FadeOut(sig2), run_time=0.5)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_01b_带光标打字,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "01b-带光标打字.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
