"""RTM-Wiki · 03-动画/强调与提示/02-圈注与聚焦 —— 本页专属样例

演示参数（文档「参数」表逐条）：
    Circumscribe(mobject, shape=Rectangle, fade_in=False, fade_out=True, time_width=0.3,
                 buff=SMALL_BUFF, color=PURE_YELLOW, run_time=1.6, stroke_width=6)      ✓
    Circumscribe(mobject, shape=Circle, fade_in=True, buff=0.18, color=TEAL,
                 stroke_width=6, run_time=1.6)                                           ✓
    FocusOn(focus_point, opacity=0.4, color=PURPLE, run_time=1.4)                        ✓
    Wiggle(mobject, scale_value=1.35, rotation_angle=0.03*TAU, n_wiggles=4,
           scale_about_point=None, rotate_about_point=None, run_time=1.6)                ✓
不演示：`Circumscribe` 的 `time_width` 光束分支 —— ✅ 已接入（2026-10-16 补全）：**显式传**时
        非 fade 分支改用 `ShowPassingFlash` 光束语义，**不传时**保持旧的 `Create` 渐进绘制；
        `fade_in` / `fade_out=True` 分支与 CE 一致**忽略**该参数（本页两条样例走的正是 fade 分支），
        故本页无光束分支视频；`FocusOn` 的 `**kwargs` 其余 Transform 通用参数无可视效果。
运行：$env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<本文件>"
"""
import os

from real_time_manim import (
    GREEN,
    GREY_B,
    PURE_YELLOW,
    PURPLE,
    SMALL_BUFF,
    TEAL,
    TAU,
    DOWN,
    UP,
    Circle,
    Dot,
    FocusOn,
    Rectangle,
    Scene,
    Text,
    VGroup,
    Wiggle,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Circumscribe,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  文件末尾 __main__ 使用


class Page_02_圈注与聚焦(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w=1280 / h=720 / hidden=True
        win.scene = self                          # 参数 win.scene

        title = Text("Circumscribe / FocusOn / Wiggle",
                     font_size=36, color=GREEN).to_edge(UP)   #标题只用 ASCII：两引擎字体回退才稳
        win.play(Write(title), run_time=0.8)

        lbl = Text("Circumscribe", font_size=46, color=GREEN).shift(DOWN * 1.6)

        # —— 步骤 1：Circumscribe(shape=Rectangle, fade_out=True) ——
        s1a = Text("Circumscribe(lbl, shape=Rectangle, fade_in=False,", font_size=28, color=GREY_B)
        s1b = Text("    fade_out=True, time_width=0.3, buff=SMALL_BUFF,", font_size=28, color=GREY_B)
        s1c = Text("    color=PURE_YELLOW, run_time=1.6, stroke_width=6)", font_size=28, color=GREY_B)
        sig1 = VGroup(s1a, s1b, s1c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        cs1 = Circumscribe(
            lbl,                                     # 参数 mobject ✓
            shape=Rectangle,                         # 参数 shape=Rectangle（类，不是实例）✓
            fade_in=False,                           # 参数 fade_in=False ✓
            fade_out=True,                           # 参数 fade_out=True ✓（默认 False：边框渐隐）
            time_width=0.3,                          # 参数 time_width=0.3（本例 fade_out=True：fade 分支忽略该参数）
            buff=SMALL_BUFF,                         # 参数 buff=SMALL_BUFF ✓
            color=PURE_YELLOW,                       # 参数 color=PURE_YELLOW ✓
            run_time=1.6,                            # 参数 run_time=1.6 ✓（fade 模式自动平分两段）
            stroke_width=6,                          # 参数 stroke_width=6 ✓（默认 4）
        )
        # 手动把标签 lbl 放进场景（Circumscribe 的 .mobject 是 None、不携带文本）；
        # 边框 _frame 自 2026-10-16 起也会被 play 层"组子动画呈现"自动带进场景，
        # 这里的 self.add 变成幂等兜底，播完 clean_up_from_scene 仍会移除 _frame。
        self.add(lbl, cs1._frame)
        win.play(cs1)
        win.play(FadeOut(sig1), run_time=0.4)

        # —— 步骤 2：Circumscribe(shape=Circle, fade_in=True) ——
        s2a = Text("Circumscribe(lbl, shape=Circle, fade_in=True,", font_size=30, color=GREY_B)
        s2b = Text("    buff=0.18, color=TEAL, stroke_width=6, run_time=1.6)", font_size=30, color=GREY_B)
        sig2 = VGroup(s2a, s2b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.4)
        cs2 = Circumscribe(
            lbl,                                     # 参数 mobject ✓
            shape=Circle,                            # 参数 shape=Circle ✓（默认 Rectangle）
            fade_in=True,                            # 参数 fade_in=True ✓（默认 False：边框渐显）
            buff=0.18,                               # 参数 buff=0.18 ✓（默认 SMALL_BUFF）
            color=TEAL,                              # 参数 color=TEAL ✓（默认 PURE_YELLOW）
            stroke_width=6,                          # 参数 stroke_width=6 ✓
            run_time=1.6,                            # 参数 run_time=1.6 ✓
        )
        self.add(cs2._frame)
        win.play(cs2)
        win.play(FadeOut(sig2), FadeOut(lbl), run_time=0.4)

        # —— 步骤 3：FocusOn(focus_point, opacity, color, run_time) ——
        s3a = Text("FocusOn(dot, opacity=0.4,", font_size=32, color=GREY_B)
        s3b = Text("         color=PURPLE, run_time=1.4)", font_size=32, color=GREY_B)
        sig3 = VGroup(s3a, s3b).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        dot = Dot(radius=0.1, color=PURPLE).next_to(sig3, DOWN, buff=1.2)
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.4)
        self.add(dot)
        win.play(
            FocusOn(
                dot,                                   # 参数 focus_point（传 mobject → 取中心）✓
                opacity=0.4,                           # 参数 opacity=0.4 ✓（默认 0.2）
                color=PURPLE,                          # 参数 color=PURPLE ✓（默认 GREY）
                run_time=1.4,                          # 参数 run_time=1.4 ✓（默认 2）
            ),
        )
        win.play(FadeOut(sig3), FadeOut(dot), run_time=0.4)

        # —— 步骤 4：Wiggle(mobject, scale_value, rotation_angle, n_wiggles,
        #                   scale_about_point, rotate_about_point, run_time) ——
        s4a = Text("Wiggle(wig, scale_value=1.35, rotation_angle=0.03*TAU,", font_size=28, color=GREY_B)
        s4b = Text("        n_wiggles=4, scale_about_point=None,", font_size=28, color=GREY_B)
        s4c = Text("        rotate_about_point=None, run_time=1.6)", font_size=28, color=GREY_B)
        sig4 = VGroup(s4a, s4b, s4c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.35)
        wig = Text("Wiggle", font_size=52, color=GREEN).next_to(sig4, DOWN, buff=0.9)
        win.play(FadeIn(sig4, shift=DOWN), run_time=0.4)
        self.add(wig)
        win.play(
            Wiggle(
                wig,                                   # 参数 mobject ✓
                scale_value=1.35,                      # 参数 scale_value=1.35 ✓（默认 1.1）
                rotation_angle=0.03 * TAU,             # 参数 rotation_angle=0.03*TAU ✓（默认 0.01*TAU）
                n_wiggles=4,                           # 参数 n_wiggles=4 ✓（默认 6）
                scale_about_point=None,                # 参数 scale_about_point=None ✓（用对象中心）
                rotate_about_point=None,               # 参数 rotate_about_point=None ✓（用对象中心）
                run_time=1.6,                          # 参数 run_time=1.6 ✓（默认 2）
            ),
        )
        win.play(FadeOut(sig4), FadeOut(wig), run_time=0.45)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_02_圈注与聚焦,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "02-圈注与聚焦.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
