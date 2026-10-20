# -*- coding: utf-8 -*-
"""01-Scene基础.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-Scene基础.py <场景名>...
不带参数就渲染全部片段，并拼出页面里的三条视频（RTM 版）。
"""
import os
import random
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene,
    Square, Text, VGroup,
    BLUE, RED, GREEN, YELLOW, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, Create, linear,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Scene.__init__ 的构造参数 ===================================
class CtorDemo(Scene):
    SEED = 1   #随机种子：改成 7 再跑一次，五个方块的颜色顺序会变

    def __init__(self, **kwargs):
        super().__init__(random_seed=self.SEED, **kwargs)   #把 “random_seed” 传给 Scene.__init__

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        info = VGroup(
            Text("random_seed=%d" % self.SEED, font_size=36, color=YELLOW),
            Text("camera_class=%s" % type(self.camera).__name__, font_size=28, color=WHITE),
            Text("always_update_mobjects=%s  skip_animations=%s" % (
                self.always_update_mobjects, self.skip_animations), font_size=22, color=GREEN),
        ).arrange(DOWN, buff=0.15).to_edge(UP)   #三行标签：把当前构造参数的取值打在屏幕上
        order = [0, 1, 2, 3, 4]   #准备一个 0~4 的下标列表
        random.shuffle(order)   #洗牌；洗牌结果只由 “random_seed” 决定
        colors = [BLUE, RED, GREEN, YELLOW, WHITE]   #五种颜色
        row = VGroup(*[Square(color=colors[i], side_length=0.9) for i in order])   #按洗牌后的下标创建方块
        row.arrange(RIGHT, buff=0.3).to_edge(DOWN)   #从左到右排成一行，颜色顺序 = 洗牌顺序
        self.add(info, row)   #把标签和这一行方块放进场景
        win.play(FadeIn(row), run_time=0.5)   #整行淡入
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


class CtorDemo7(CtorDemo):
    SEED = 7   #同一个场景，只把 “random_seed” 换成 7


# ===== 样例 2：场景生命周期 setup / construct / tear_down ==================
class LifeDemo(Scene):
    def setup(self):
        self.square = Square(color=BLUE)   #setup 在 construct 之前跑，适合准备公共对象

    def tear_down(self):
        print("tear_down ran")   #（2026-10-16 起 RTM 也会调用：record 生命周期 try/finally 里保证跑一次）

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        title = Text("setup -> construct", font_size=40, color=YELLOW).to_edge(UP)   #屏幕标题
        self.add(title)   #把标题放进场景
        win.play(Create(self.square), run_time=0.8)   #画出 setup() 里准备好的方块
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：Scene.camera / Scene.time ==================================
class TimeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=GREEN).shift(DOWN)   #一个会动的方块，证明时间确实在流逝
        label = Text("scene.time = 0.00", font_size=40, color=YELLOW).to_edge(UP)   #显示 self.time 的标签

        def show_time(m):   #每帧把 “self.time” 刷进标签
            m.become(Text("scene.time = %.2f" % self.time, font_size=40, color=YELLOW).to_edge(UP))

        label.add_updater(show_time)   #mobject 级 updater：RTM 每帧都会驱动它
        self.add(sq, label)   #把方块和标签放进场景
        win.play(sq.animate.shift(RIGHT * 4), run_time=0.8, rate_func=linear)   #方块匀速右移
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


PAGE = "01-Scene基础"

SCENES = [
    ("ctor_seed1", CtorDemo),
    ("ctor_seed7", CtorDemo7),
    ("life", LifeDemo),
    ("time", TimeDemo),
]

SAMPLES = [
    ("ctor", ["ctor_seed1", "ctor_seed7"]),
    ("life", ["life"]),
    ("time", ["time"]),
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
