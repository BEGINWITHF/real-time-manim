# -*- coding: utf-8 -*-
"""07-animate语法.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 07-animate语法.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的三条样例视频（输出到上一级 assets/）。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Square, Rectangle,
    PURPLE, TEAL, RED, ORANGE,
    UP, DOWN, LEFT, RIGHT, PI, FadeIn, FadeOut, Transform,
    there_and_back, override_animate,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：.animate 基础 ==============================================
class AnimateBasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        s = Square(color=RED, side_length=1.2, fill_opacity=0.6).shift(LEFT * 3.5)   #红色方块
        self.add(s)   #进场景
        win.play(s.animate.shift(RIGHT * 1.6), run_time=0.5)   #最普通的 “.animate”：平移
        win.play(s.animate.scale(1.5).rotate(PI / 6), run_time=0.6)   #链式：一个动画两步
        win.play(s.animate(run_time=0.8, rate_func=there_and_back).shift(DOWN), run_time=0.8)   #play 参数紧跟 “.animate”
        rect = Rectangle(width=2.0, height=1.0, color=ORANGE, fill_opacity=0.6).shift(RIGHT * 3.5)   #橙色矩形
        self.add(rect)   #进场景
        win.play(rect.animate.set(width=5.0), run_time=0.5)   #set 配合 animate：按目标尺寸调
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：override_animate ==========================================
class PulseSquare(Square):   #自定义子类：给普通方法配专用动画
    def pulse(self, scale_factor):   #普通调用：直接放大（瞬时）
        self.scale(scale_factor)

    @override_animate(pulse)   #给 “pulse” 指定 “.animate” 调用时该播的动画
    def _pulse_animation(self, scale_factor, anim_args=None):   #参数与原方法一致，外加 anim_args
        if anim_args is None:
            anim_args = {}
        target = self.copy().scale(scale_factor)   #目标形态
        return Transform(self, target, **anim_args)   #返回动画：平滑变形过去


class OverrideDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        ds = PulseSquare(color=PURPLE, side_length=1.2, fill_opacity=0.6).shift(LEFT * 3.5)   #左边：直接调用
        ds2 = PulseSquare(color=PURPLE, side_length=1.2, fill_opacity=0.6).shift(RIGHT * 3.5)   #右边：animate 调用
        self.add(ds, ds2)   #进场景
        ds.pulse(1.4)   #直接调用 → 走普通方法（瞬间变大）
        win.play(Wait(0.5))   #看清瞬间变化
        win.play(ds2.animate.pulse(1.4), run_time=0.6)   #“.animate” 调用 → 被替换成返回的动画（平滑）
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：add_animation_override / animation_override_for ===========
class FlashSquare(Square):   #只是挂注册表的载体类
    pass


class AddOverrideDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        FlashSquare.add_animation_override(FadeIn, lambda mobject, **kwargs: FadeOut(mobject))   #注册：FadeIn 换成 FadeOut
        print("override_for(FadeIn) =", FlashSquare.animation_override_for(FadeIn))   #查表：拿到注册的函数
        print("override_for(Transform) =", FlashSquare.animation_override_for(Transform))   #没注册过：None
        sq = FlashSquare(color=TEAL, side_length=1.4, fill_opacity=0.7)   #青色方块
        self.add(sq)   #进场景
        win.play(FadeIn(sq), run_time=0.6)   #写的是 FadeIn，注册表把它换成了 FadeOut（可见对象当场淡出）
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("animate", AnimateBasicDemo),
    ("override", OverrideDemo),
    ("add_override", AddOverrideDemo),
]

PAIRS = [
    ("animate", ["animate"]),
    ("override", ["override"]),
    ("add_override", ["add_override"]),
]

PAGE = "07-animate语法"


def concat(names, dst):
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    lst = os.path.join(HERE, "concat.txt")
    with open(lst, "w", encoding="utf-8") as fh:
        for n in names:
            fh.write("file '%s'\n" % os.path.join(OUT, n + ".mp4"))
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", lst, "-c", "copy", dst],
        check=True)
    return dst


if __name__ == "__main__":
    only = set(sys.argv[1:])
    for name, cls in SCENES:
        if only and name not in only:
            continue
        print("=" * 30, name)
        try:
            fast_record_scene(cls, out_path=os.path.join(OUT, name + ".mp4"),
                              verbose=True)
        except Exception:
            import traceback
            traceback.print_exc()

    if not only:
        for out_name, names in PAIRS:
            dst = os.path.join(ASSETS, "RTM output", "%s-%s.mp4" % (PAGE, out_name))
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
