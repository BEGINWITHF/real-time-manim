# -*- coding: utf-8 -*-
"""02-内容上屏.md 五个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02-内容上屏.py <场景名>...
不带参数就渲染全部片段，并拼出页面里的五条视频（RTM 版）。
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
    Square, Circle, Triangle, Dot, Text,
    BLUE, RED, GREEN, YELLOW, ORANGE, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Scene.add ==================================================
class AddDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        back = Square(color=BLUE, side_length=2.5)   #第一个加入的方块
        mid = Circle(color=RED, radius=1.6)   #第二个加入的圆
        top = Triangle(color=YELLOW).scale(1.3).shift(RIGHT * 2.2)   #第三个加入的三角
        self.add(back)   #先加的画在最下面
        self.add(mid, top)   #后加的盖在上面；一次可传多个
        self.add(Text("add order = paint order", font_size=36, color=WHITE).to_edge(UP))   #最后加的文字在最上层
        win.play(Wait(0.5))   #保持 0.5s，看清谁盖住谁
        win.play(FadeIn(Square(color=GREEN, side_length=1.2)), run_time=0.5)   #动画新加的对象直接盖在最上层
        win.play(Wait(0.5))   #再等 0.5s
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Scene.remove ===============================================
class RemoveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        back = Square(color=BLUE, side_length=2.5)   #被盖住的方块
        front = Circle(color=RED, radius=1.6)   #压在上面的圆
        self.add(back, front)   #圆盖着方块上屏
        win.play(Wait(0.5))   #先看清“圆盖住方块”
        self.remove(front)   #把圆拿下屏，露出下面的方块
        win.play(Wait(0.5))   #再等 0.5s 看效果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：Scene.clear =================================================
class ClearDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        self.add(Square(color=BLUE, side_length=2).shift(LEFT * 2))   #放一个方块
        self.add(Circle(color=RED, radius=1.2).shift(RIGHT * 2))   #再放一个圆
        self.add(Text("before clear", font_size=40, color=YELLOW).to_edge(UP))   #加个标题
        win.play(Wait(0.5))   #先看清屏幕上的内容
        self.clear()   #一键清空：mobjects 和 foreground_mobjects 全部下屏
        self.add(Text("after clear", font_size=40, color=GREEN).to_edge(UP))   #再放一个新标题
        win.play(Wait(0.5))   #画面里只剩新标题
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：bring_to_front / bring_to_back / foreground ================
class ZorderDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #置顶规则会在 win.play 内部重排对象，先接上
        blue = Square(color=BLUE, side_length=2.2).shift(LEFT * 0.6)   #先加的蓝方块
        red = Square(color=RED, side_length=2.2).shift(RIGHT * 0.6)   #后加的红方块，压在蓝上
        title = Text("z-order", font_size=40, color=YELLOW).to_edge(UP)   #要置顶的标题
        self.add(blue, red)   #红上蓝下
        win.play(Wait(0.5))
        self.bring_to_front(blue)   #蓝方块提到最上层
        win.play(Wait(0.5))
        self.bring_to_back(blue)   #蓝方块压回最底层
        win.play(Wait(0.5))
        self.add(title)   #标题先按普通对象上屏
        sweep = Circle(color=GREEN, radius=2.8, fill_opacity=1).shift(LEFT * 9 + UP * 3.5)   #一个实心大圆，会横扫过标题
        self.add(sweep)   #大圆后加，压在标题上面
        win.play(sweep.animate.shift(RIGHT * 8), run_time=0.8)   #大圆横扫过标题，把标题盖住
        self.add_foreground_mobject(title)   #标题登记为前景：立刻浮到最上层
        win.play(Wait(0.5))   #停 0.5s：标题压在圆上
        self.remove_foreground_mobject(title)   #取消前景；但标题已被 add 挪到列表末尾，仍在最上层
        self.bring_to_back(title)   #想回到下层还得自己压回去
        win.play(Wait(0.5))   #停 0.5s：标题又被圆盖住了
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：Scene.replace + 查询工具 ===================================
class ReplaceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        tri = Triangle(color=GREEN).scale(1.3).shift(LEFT * 2.5)   #将被顶替的三角
        dot = Dot(color=RED, radius=0.35).shift(RIGHT * 2.5)   #旁边的红点，作对照
        self.add(tri, dot)   #两个对象上屏
        print("replace之前：top-level = %d" % len(self.get_top_level_mobjects()))   #查询工具 get_top_level_mobjects
        win.play(Wait(0.5))
        self.replace(tri, Square(color=ORANGE, side_length=1.8).shift(LEFT * 2.5))   #三角原位换成方块
        print("replace 之后：top-level = %d" % len(self.get_top_level_mobjects()))   #数量不变，只是原位顶替
        win.play(Wait(0.5))
        win.close()   #关闭 RTM 窗口


PAGE = "02-内容上屏"

SCENES = [
    ("add", AddDemo),
    ("remove", RemoveDemo),
    ("clear", ClearDemo),
    ("zorder", ZorderDemo),
    ("replace", ReplaceDemo),
]

SAMPLES = [
    ("add", ["add"]),
    ("remove", ["remove"]),
    ("clear", ["clear"]),
    ("zorder", ["zorder"]),
    ("replace", ["replace"]),
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
