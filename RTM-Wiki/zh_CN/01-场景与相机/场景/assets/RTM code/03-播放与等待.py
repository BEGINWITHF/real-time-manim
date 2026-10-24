# -*- coding: utf-8 -*-
"""03-播放与等待.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 03-播放与等待.py <场景名>...
不带参数就渲染全部片段，并拼出页面里的三条视频（RTM 版）。
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    Scene,
    Square, Circle, Text,
    BLUE, RED, GREEN, YELLOW,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, Write, linear,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：win.play 的 *args / run_time / rate_func / .animate ========
class PlayDemo(Scene):
    RUN_TIME = 0.6   #动画时长：改成 1.2 看慢一倍的版本

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        a = Circle(color=RED).shift(LEFT * 2.5)   #左边的圆
        b = Square(color=GREEN).shift(RIGHT * 2.5)   #右边的方块
        self.add(a, b)   #两个对象上屏
        win.play(FadeIn(a), FadeIn(b), run_time=self.RUN_TIME)   #一条 play 塞多个动画 = 并行播放
        win.play(a.animate.shift(RIGHT * 1.2), run_time=self.RUN_TIME, rate_func=linear)   #“.animate” 构造器 + 线性速率
        win.play(a.animate.shift(LEFT * 1.2), run_time=self.RUN_TIME)   #默认 smooth 速率：两头慢中间快
        win.play(Write(Text("win.play", font_size=42, color=YELLOW).to_edge(DOWN)), run_time=self.RUN_TIME)   #Write 书写动画
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：等待的四种写法 =============================================
class WaitDemo(Scene):
    FLAVOR = "play_wait"   #等待写法：四种口味，见下面的子类

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #self.wait / self.pause / self.wait_until 内部都调 self.play，必须先接上
        tag = Text(self.FLAVOR, font_size=40, color=YELLOW).to_edge(UP)   #屏幕顶端显示当前写法
        sq = Square(color=BLUE).shift(DOWN)   #一个静态方块，方便看清等待时画面确实不动
        self.add(tag, sq)   #把标签和方块放进场景
        win.play(FadeIn(sq), run_time=0.3)   #先淡入 0.3s
        if self.FLAVOR == "play_wait":
            win.play(Wait(0.5))   #RTM 写法：win.play(Wait(秒))
        elif self.FLAVOR == "self_wait":
            self.wait(0.5)   #manim 写法：经 self.play 转发，等 0.5s
        elif self.FLAVOR == "self_pause":
            self.pause(0.3)   #冻结画面的暂停，等 0.3s
        else:
            self.wait_until(lambda: True, max_time=0.3)   #条件等待；条件第一帧后就为真，等待立即结束
        win.close()   #关闭 RTM 窗口


class WaitSelf(WaitDemo):
    FLAVOR = "self_wait"   #换成 self.wait


class WaitPause(WaitDemo):
    FLAVOR = "self_pause"   #换成 self.pause


class WaitUntil(WaitDemo):
    FLAVOR = "wait_until"   #换成 self.wait_until


# ===== 样例 3：Scene.add_updater / Scene.remove_updater ===================
class UpdaterDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接上
        mob = Square(color=BLUE).shift(LEFT * 3 + DOWN * 2)   #mobject 级 updater 驱动的方块
        via_scene = Square(color=RED).shift(RIGHT * 3 + DOWN * 2)   #场景级 updater 驱动的方块
        self.add(mob, via_scene)   #两个方块上屏
        self.add(Text("mobject.add_updater", font_size=24, color=BLUE).next_to(mob, UP))   #左边的说明
        self.add(Text("scene.add_updater", font_size=24, color=RED).next_to(via_scene, UP))   #右边的说明
        mob.add_updater(lambda m, dt: m.shift(UP * 0.03))   #mobject 级：RTM 每帧驱动，方块持续上移

        def scene_updater(dt):   #场景级：RTM 每帧驱动
            via_scene.shift(UP * 0.03)

        self.add_updater(scene_updater)   #把函数登记到场景上
        win.play(Wait(0.5))   #等 0.5s：蓝方块上移，红方块也上移
        self.remove_updater(scene_updater)   #摘掉场景级 updater
        mob.clear_updaters()   #摘掉 mobject 级 updater，蓝方块停住
        win.play(Wait(0.5))   #再等 0.5s：两个方块都不动
        win.close()   #关闭 RTM 窗口


PAGE = "03-播放与等待"

SCENES = [
    ("play", PlayDemo),
    ("wait_play", WaitDemo),
    ("wait_self", WaitSelf),
    ("wait_pause", WaitPause),
    ("wait_until", WaitUntil),
    ("updater", UpdaterDemo),
]

SAMPLES = [
    ("play", ["play"]),
    ("wait", ["wait_play", "wait_self", "wait_pause", "wait_until"]),
    ("updater", ["updater"]),
]


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
        for out_name, names in SAMPLES:
            dst = os.path.join(ASSETS, "RTM output", "%s-%s.mp4" % (PAGE, out_name))
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
            if len(names) > 1:
                #多片段样例：每个片段也拷进 assets/，方便逐段对照
                for n in names:
                    shutil.copyfile(os.path.join(OUT, n + ".mp4"),
                                    os.path.join(ASSETS, "%s-%s.mp4" % (PAGE, n)))
