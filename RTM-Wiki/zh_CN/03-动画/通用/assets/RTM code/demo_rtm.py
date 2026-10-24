"""RTM-Wiki · 03-动画/通用 视频样例（RTM 渲染）

一段场景覆盖本文件夹 3 个页面的可演示参数，每页一段，用注释分隔：

    # ========== 01-生命周期与公共参数.md ==========
    # ========== 02-play与wait参数.md ==========
    # ========== 03-animate语法.md ==========

只使用 RTM 已导出的动画类（✅ 名单，见 99-功能状态总览）。
02 页里 RTM 未接线/无法在录制里体现的参数（subcaption 字幕、Scene.pause、
wait_until(stop_condition=...)、frozen_frame）不进脚本，页面上逐项标「无视频」。

运行（脚本会自行把仓库根目录加入 sys.path）：
    python demo_rtm.py      # -> assets\\sample.mp4
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    BLUE,
    GREEN,
    ORANGE,
    RED,
    YELLOW,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    PI,
    Circle,
    Rectangle,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
    linear,
    smooth,
    there_and_back,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    MoveToTarget,
    Rotate,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  文件末尾 __main__ 使用


class Demo_Basics(Scene):
    def construct(self):
        # 参数 MLWindow(w=1280, h=720, hidden=True) ✓ —— 全片共用一个窗口
        win = MLWindow(1280, 720, hidden=True)
        # 参数 win.scene = self ✓ —— 先绑定场景，否则 play() 直接返回
        win.scene = self

        # ========== 01-生命周期与公共参数.md ==========
        # Animation(mobject, lag_ratio=0.0, run_time=1.0, rate_func=smooth,
        #           reverse_rate_function=False, name=None, remover=False,
        #           suspend_mobject_updating=True, introducer=False, use_override=True)
        #   begin() -> interpolate(alpha) -> finish() -> _setup_scene/clean_up_from_scene
        #   参数 mobject ✓（每个动画的第一个位置参数）
        #   参数 lag_ratio=1.0 ✓  参数 run_time=1.0 ✓   参数 rate_func=linear ✓
        #   参数 reverse_rate_function=False ✓          参数 name="..." ✓
        #   参数 remover=True ✓（FadeOut 播完移出场景）  参数 introducer=True ✓（FadeIn 播前加入场景）
        #   参数 suspend_mobject_updating=True ✓        参数 use_override=True ✓
        #   方法 set_rate_func(fn) ✓                   类方法 Animation.set_default(**kwargs) ✓
        t01 = Text("Animation 公共构造参数", font_size=40).to_edge(UP)
        sq01 = Square(side_length=1.4, color=BLUE).set_fill(BLUE, 0.6).shift(LEFT * 2.6)
        ci01 = Circle(radius=0.7, color=GREEN).shift(RIGHT * 2.6)
        win.play(Write(t01), run_time=1.0)                       # 参数 run_time=1.0 ✓
        # introducer=True：播放前的 _setup_scene 阶段才把 sq01 加进场景
        win.play(FadeIn(sq01, introducer=True), run_time=0.9)     # 参数 introducer ✓
        win.play(
            Create(
                ci01,
                lag_ratio=1.0,                                    # 参数 lag_ratio=1.0 ✓（子笔画依次画完）
                run_time=1.0,                                     # 参数 run_time ✓
                name="Create(Circle)",                            # 参数 name ✓（渲染日志里的名字）
                suspend_mobject_updating=True,                    # 参数 suspend_mobject_updating ✓
                use_override=True,                                # 参数 use_override ✓
            ),
            run_time=1.0,
        )
        rot01 = Rotate(                                            # 参数 mobject + angle ✓
            ci01, PI / 2,
            run_time=1.0,                                          # 参数 run_time ✓
            rate_func=linear,                                      # 参数 rate_func=linear ✓
            reverse_rate_function=False,                           # 参数 reverse_rate_function ✓
            name="Rotate(Circle)",                                 # 参数 name ✓
        )
        rot01.set_rate_func(linear)                                # 方法 set_rate_func ✓
        win.play(rot01)
        win.play(FadeOut(sq01, remover=True), run_time=0.9)        # 参数 remover ✓
        Rotate.set_default(run_time=1.5, rate_func=linear)         # Animation.set_default(**kwargs) ✓
        win.play(Rotate(ci01, PI))                                 # 参数 run_time=1.5 ✓（由 set_default 提供）
        Rotate.set_default()                                       # 传空参恢复原始默认值 ✓
        win.play(Wait(0.4))
        win.play(FadeOut(VGroup(t01, ci01)), run_time=0.6)

        # ========== 02-play与wait参数.md ==========
        # Scene.play(*anims, subcaption=None, subcaption_duration=None, subcaption_offset=0, **kwargs)
        # Scene.wait(duration=1.0, stop_condition=None, frozen_frame=None)
        #   参数 *anims ✓（一次 play 传多个动画对象）
        #   参数 **kwargs：run_time ✓ / rate_func ✓（逐个 setattr 到每个动画实例上）
        #   参数 lag_ratio ✓（写在动画构造器上）
        #   参数 duration ✓（win.play(Wait(1.5)) ≡ self.wait(1.5)）
        #   ❌ subcaption / subcaption_duration / subcaption_offset —— RTM 的 win.play 未提供字幕参数
        #   ❌ Scene.pause / wait_until(stop_condition=, max_time=) / frozen_frame —— RTM 未接线，见页面「无视频」
        t02 = Text("Scene.play / wait 参数", font_size=40).to_edge(UP)
        a02 = Square(color=BLUE).scale(0.7).shift(LEFT * 3)
        b02 = Circle(color=GREEN).scale(0.7)
        c02 = Triangle(color=ORANGE).scale(0.7).shift(RIGHT * 3)
        r02 = Rectangle(width=2.6, height=1.1, color=YELLOW).shift(DOWN * 2)
        win.play(Write(t02), run_time=0.9)                         # 参数 *anims + run_time ✓
        win.play(                                                  # 三个动画一次播完
            Create(a02, lag_ratio=1.0),                            # 参数 lag_ratio=1.0 ✓（构造器上）
            FadeIn(b02, scale=0.5),                                # 参数 FadeIn(scale=...) ✓
            FadeIn(c02, shift=UP),                                 # 参数 FadeIn(shift=...) ✓
            run_time=1.6,                                          # 参数 run_time=1.6 ✓（setattr 到每个动画）
            rate_func=smooth,                                      # 参数 rate_func=smooth ✓（同上）
        )
        win.play(                                                  # play 级别覆盖两个动画的默认值
            Create(r02),
            FadeOut(c02),
            run_time=1.4,                                          # 参数 run_time=1.4 ✓
            rate_func=linear,                                      # 参数 rate_func=linear ✓
        )
        win.play(Wait(1.5))                                        # 参数 duration=1.5 ✓ ≡ self.wait(1.5)
        win.play(Wait(0.6))                                        # 参数 duration=0.6 ✓（默认 1.0）
        win.play(FadeOut(VGroup(t02, a02, b02, r02)), run_time=0.6)

        # ========== 03-animate语法.md ==========
        # Mobject.animate -> _AnimationBuilder(**kwargs 只能紧跟 .animate(...) 传一次)
        #   参数 .animate.shift(RIGHT) ✓      参数 链式 set_fill(RED).set_opacity(0.5) ✓
        #   参数 .animate(run_time=1.2).rotate(PI/2) ✓
        #   参数 .animate(rate_func=there_and_back).shift(RIGHT) ✓
        # 1.5 generate_target() + MoveToTarget(mobject, **kwargs) ✓
        t03 = Text(".animate 语法与 MoveToTarget", font_size=38).to_edge(UP)
        sq03 = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6).shift(LEFT * 2 + DOWN)
        ci03 = Circle(radius=0.75, color=GREEN).shift(RIGHT * 2)
        win.play(Write(t03), run_time=0.8)                          # 参数 win.play ✓
        win.play(Create(sq03), run_time=0.9)                        # 参数 Create ✓
        win.play(sq03.animate.shift(RIGHT * 1.2), run_time=0.7)     # 参数 .animate.shift(RIGHT) ✓
        win.play(                                                   # 链式方法合成一个动画
            sq03.animate.set_fill(RED).set_opacity(0.5),
            run_time=0.8,                                           # 参数 run_time ✓
        )
        win.play(sq03.animate(run_time=1.2).rotate(PI / 2))         # 参数 .animate(run_time=1.2) ✓
        win.play(                                                   # 动画参数也能放 rate_func
            sq03.animate(rate_func=there_and_back).shift(RIGHT),
            run_time=0.9,                                           # 参数 rate_func=there_and_back ✓
        )
        win.play(Create(ci03), run_time=0.8)
        ci03.generate_target()                                      # 参数 generate_target() ✓
        ci03.target.set_fill(GREEN, opacity=0.5).shift(2 * RIGHT + UP).scale(0.5)
        win.play(MoveToTarget(ci03), run_time=1.0)                  # 参数 MoveToTarget(mobject) ✓
        win.play(Wait(0.4))                                         # 参数 Wait ✓
        win.play(FadeOut(VGroup(t03, sq03, ci03)), run_time=0.6)

        # 参数 win.close() ✓ —— 关闭窗口、结束渲染（录制时在此触发编码收尾）
        win.close()


if __name__ == "__main__":
    fast_record_scene(Demo_Basics, out_path=os.path.join(os.path.dirname(__file__), "sample.mp4"), fps=30, overwrite=True, cleanup=True)
