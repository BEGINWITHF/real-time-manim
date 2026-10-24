"""RTM-Wiki · 03-动画/强调与提示/01b-扫光与波纹 —— 本页专属样例

演示参数（文档「参数」表逐条）：
    ShowPassingFlash(mobject, time_width=0.5, **kwargs(run_time=1.6))                            ✓
    ShowPassingFlashWithThinningStrokeWidth(vmobject, n_segments=12, time_width=0.15,
                                            remover=True, **kwargs(run_time=1.8))                 ✓
    ApplyWave(mobject, direction=UP, amplitude=0.35, wave_func=smooth, time_width=1,
              ripples=3, run_time=2)                                                              ✓
不演示：`ShowPassingFlash` 播完"恢复完整笔画"（`remover=False`）的行为 —— ✅ 已接线
        （2026-10-16 补全 `remover` 形参、默认 `True` 保持向后兼容：`True` 时 `clean_up_from_scene`
        把对象移出场景；显式传 `False` 时对象留在场景并恢复全笔画），样例用默认值；
        `**kwargs` 其余通用参数无可视效果。
运行：python "<本文件>"（脚本会自行把仓库根目录加入 sys.path）
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    BLUE,
    DARK_GRAY,
    GREEN,
    GREY_B,
    YELLOW,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Circle,
    RegularPolygon,
    Scene,
    ShowPassingFlashWithThinningStrokeWidth,
    Text,
    VGroup,
    smooth,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    ApplyWave,
    FadeIn,
    FadeOut,
    ShowPassingFlash,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  文件末尾 __main__ 使用


class Page_01b_扫光与波纹(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w=1280 / h=720 / hidden=True
        win.scene = self                          # 参数 win.scene

        title = Text("ShowPassingFlash / ApplyWave",
                     font_size=36, color=GREEN).to_edge(UP)   #标题只用 ASCII：两引擎字体回退才稳
        win.play(Write(title), run_time=0.8)

        # —— 步骤 1：ShowPassingFlash(mobject, time_width, **kwargs) ——
        sig1 = Text("ShowPassingFlash(poly, time_width=0.5, run_time=1.6)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        poly = RegularPolygon(5, color=DARK_GRAY).scale(1.6).next_to(sig1, DOWN, buff=0.7)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        win.play(
            ShowPassingFlash(
                poly,                                    # 参数 mobject ✓
                time_width=0.5,                          # 参数 time_width=0.5 ✓（默认 0.1：光束占整条 50%）
                run_time=1.6,                            # 参数 **kwargs(run_time) ✓
            ),
            run_time=1.6,
        )
        # RTM 版 remover 默认 True，播完把 mobject 移出场景，因此不再对五边形 FadeOut
        #（2026-10-16 起 remover 可显式传 False，让对象留在场景）。
        win.play(FadeOut(sig1), run_time=0.45)

        # —— 步骤 2：ShowPassingFlashWithThinningStrokeWidth(
        #                vmobject, n_segments, time_width, remover, **kwargs) ——
        s2a = Text("ShowPassingFlashWithThinningStrokeWidth(", font_size=28, color=GREY_B)
        s2b = Text("    ring, n_segments=12, time_width=0.15,", font_size=28, color=GREY_B)
        s2c = Text("    remover=True, run_time=1.8)", font_size=28, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        ring = Circle(radius=1.2, stroke_width=10, color=BLUE).next_to(sig2, DOWN, buff=0.6)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        win.play(
            ShowPassingFlashWithThinningStrokeWidth(
                ring,                                    # 参数 vmobject ✓
                n_segments=12,                           # 参数 n_segments=12 ✓（默认 10）
                time_width=0.15,                         # 参数 time_width=0.15 ✓（默认 0.1）
                remover=True,                            # 参数 remover=True ✓（默认值，显式传）
                run_time=1.8,                            # 参数 **kwargs(run_time) ✓
            ),
            run_time=1.8,
        )
        win.play(FadeOut(sig2), FadeOut(ring), run_time=0.45)

        # —— 步骤 3：ApplyWave(mobject, direction, amplitude, wave_func,
        #                      time_width, ripples, run_time) ——
        s3a = Text("ApplyWave(txt, direction=UP, amplitude=0.35,", font_size=30, color=GREY_B)
        s3b = Text("           wave_func=smooth, time_width=1,", font_size=30, color=GREY_B)
        s3c = Text("           ripples=3, run_time=2)", font_size=30, color=GREY_B)
        sig3 = VGroup(s3a, s3b, s3c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        wtxt = Text("WaveWaveWave", font_size=46, color=YELLOW).next_to(sig3, DOWN, buff=0.9)
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.45)
        win.play(
            ApplyWave(
                wtxt,                                    # 参数 mobject ✓
                direction=UP,                            # 参数 direction=UP ✓（显式：波推动方向）
                amplitude=0.35,                          # 参数 amplitude=0.35 ✓（默认 0.2）
                wave_func=smooth,                        # 参数 wave_func=smooth ✓（单个波峰形状）
                time_width=1,                            # 参数 time_width=1 ✓（波长占比）
                ripples=3,                               # 参数 ripples=3 ✓（默认 1）
                run_time=2,                              # 参数 run_time=2 ✓
            ),
        )
        win.play(FadeOut(sig3), FadeOut(wtxt), run_time=0.5)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_01b_扫光与波纹,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "01b-扫光与波纹.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
