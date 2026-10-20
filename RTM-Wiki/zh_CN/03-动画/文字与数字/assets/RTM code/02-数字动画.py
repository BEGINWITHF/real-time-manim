"""RTM-Wiki · 03-动画/文字与数字/02-数字动画 —— 本页专属样例

演示参数（文档「参数」表逐条）：
    ChangingDecimal(decimal_mob, number_update_func=lambda a: 5*a,
                    suspend_mobject_updating=False, **kwargs(run_time, rate_func))  ✓
    ChangeDecimalToValue(decimal_mob, target_number=10,
                         **kwargs(run_time, rate_func, suspend_mobject_updating))    ✓
    ValueTracker + add_updater 长期跟随（页面「经验」条目）                            ✓
不演示：`TextDecimalNumber` —— RTM 另导出的类，手册未收录其签名，页面明确"本页不展开"。
运行：$env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<本文件>"
"""
import os

from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    RED,
    DOWN,
    UP,
    ChangeDecimalToValue,
    ChangingDecimal,
    DecimalNumber,
    Scene,
    Text,
    ValueTracker,
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


class Page_02_数字动画(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # 参数 w=1280 / h=720 / hidden=True
        win.scene = self                          # 参数 win.scene

        title = Text("ChangingDecimal / ChangeDecimalToValue",
                     font_size=34, color=GREEN).to_edge(UP)   #标题只用 ASCII：两引擎字体回退才稳
        win.play(Write(title), run_time=0.85)

        # —— 步骤 1：ChangingDecimal(decimal_mob, number_update_func, ...) ——
        s1a = Text("ChangingDecimal(num, lambda a: 5 * a,", font_size=30, color=GREY_B)
        s1b = Text("    suspend_mobject_updating=False, run_time=2.4,", font_size=30, color=GREY_B)
        s1c = Text("    rate_func=linear)", font_size=30, color=GREY_B)
        sig1 = VGroup(s1a, s1b, s1c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        n01 = DecimalNumber(0, num_decimal_places=2, color=BLUE).next_to(sig1, DOWN, buff=0.9)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        self.add(n01)
        win.play(
            ChangingDecimal(
                n01,                                  # 参数 decimal_mob ✓（必须是 DecimalNumber）
                lambda a: 5 * a,                      # 参数 number_update_func ✓：f(alpha) -> 数值
                suspend_mobject_updating=False,       # 参数 suspend_mobject_updating=False ✓（可与 ValueTracker 共存）
                run_time=2.4,                         # 参数 **kwargs：run_time=2.4 ✓
                rate_func=linear,                     # 参数 **kwargs：rate_func=linear ✓
            ),
        )
        win.play(Wait(0.4))
        win.play(FadeOut(sig1), FadeOut(n01), run_time=0.45)

        # —— 步骤 2：ChangeDecimalToValue(decimal_mob, target_number, ...) ——
        s2a = Text("ChangeDecimalToValue(num, target_number=10,",
                   font_size=30, color=GREY_B)
        s2b = Text("    run_time=2.4, rate_func=linear,", font_size=30, color=GREY_B)
        s2c = Text("    suspend_mobject_updating=False)", font_size=30, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        n02 = DecimalNumber(0, num_decimal_places=2, color=RED).next_to(sig2, DOWN, buff=0.9)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        self.add(n02)
        win.play(
            ChangeDecimalToValue(
                n02,                                  # 参数 decimal_mob ✓
                10,                                   # 参数 target_number=10 ✓（源码标 int，浮点同样可用）
                run_time=2.4,                         # 参数 **kwargs：run_time=2.4 ✓
                rate_func=linear,                     # 参数 **kwargs：rate_func=linear ✓
                suspend_mobject_updating=False,       # 参数 **kwargs：继承 ChangingDecimal ✓
            ),
        )
        win.play(Wait(0.3))
        win.play(FadeOut(sig2), FadeOut(n02), run_time=0.45)

        # —— 步骤 3：页面「经验」——长期跟随用 ValueTracker + updater ——
        s3a = Text("tracker = ValueTracker(0)", font_size=30, color=GREY_B)
        s3b = Text("num.add_updater(lambda n: n.set_value(tracker.get_value()))",
                   font_size=30, color=GREY_B)
        s3c = Text("win.play(tracker.animate.set_value(7.5), run_time=2)",
                   font_size=30, color=GREY_B)
        sig3 = VGroup(s3a, s3b, s3c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        tracker = ValueTracker(0)
        n03 = DecimalNumber(0, num_decimal_places=1, color=GREEN).next_to(sig3, DOWN, buff=0.9)
        n03.add_updater(lambda n: n.set_value(tracker.get_value()))
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.45)
        self.add(n03)
        win.play(tracker.animate.set_value(7.5), run_time=2, rate_func=linear)
        n03.clear_updaters()
        win.play(FadeOut(sig3), FadeOut(n03), run_time=0.5)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_02_数字动画,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "02-数字动画.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
