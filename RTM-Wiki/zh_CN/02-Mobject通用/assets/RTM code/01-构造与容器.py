# -*- coding: utf-8 -*-
"""01-构造与容器.md 四个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-构造与容器.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的四条样例视频（输出到上一级 assets/）。
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
    Scene, Mobject, Group, VGroup,
    Square, Circle, Text, Dot,
    BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE,
    RIGHT, UP, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Mobject 构造参数 ============================================
class CtorDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        front = Square(color=RED, side_length=2.4, fill_opacity=0.8, name="hero", z_index=2)   #名字 “hero”、叠放层级 2
        back = Square(color=BLUE, side_length=2.4, fill_opacity=0.8)   #其余全走默认：name 取类名、z_index=0
        back.shift(RIGHT * 1.2)   #向右错开一点，让两个方块有重叠
        self.add(front, back)   #先加 “front” 后加 “back”，但层级大的仍然显示在上
        print("color =", back.color, "| name =", back.name, "| dim =", back.dim)   #颜色、名字、点坐标维度
        print("target =", front.target, "| z_index =", front.z_index, back.z_index)   #target 缓存默认为空
        win.play(FadeIn(front), FadeIn(back), run_time=0.6)   #两个方块一起淡入
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Group 容器 ==================================================
class GroupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=1.2)   #方块
        label = Text("G", font_size=48, color=YELLOW)   #文字：和方块不同类
        dot = Dot(color=GREEN, radius=0.35)   #圆点：又一种类型
        g = Group(sq, label, dot, z_index=1)   #“Group” 什么类型都能装，“z_index” 透传给 Mobject
        g.arrange(RIGHT, buff=0.6)   #三个子对象排成一行
        self.add(g)   #整组进场景
        print("len(g) =", len(g), "| 类型 =", [type(m).__name__ for m in g])   #三个子对象都在
        g.add(sq)   #重复添加同一个对象：被忽略，只留一份
        print("重复 add 后 len(g) =", len(g))   #仍然是 3
        try:
            VGroup(Mobject())   #“VGroup” 只收矢量对象
        except TypeError as exc:   #裸 “Mobject” 没有矢量数据
            print("VGroup 拒收非矢量对象 ->", exc)
        win.play(FadeIn(g), run_time=0.6)   #整组淡入
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：add / remove / add_to_back / insert =========================
class AddRemoveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        box = Square(color=RED, side_length=2.6, fill_opacity=0.8)   #红色方块（带填充）
        disc = Circle(color=BLUE, radius=1.25, fill_opacity=0.8)   #蓝色圆盘（带填充）
        g = Group(box)   #先把方块放进 “Group”
        g.add(disc)   #add：圆盘加到列表尾部，显示在方块上面
        self.add(g)   #整组进场景
        win.play(FadeIn(g), run_time=0.5)   #淡入：圆盘盖住方块中心
        g.remove(disc)   #remove：圆盘退出组，画面里只剩方块
        win.play(Wait(0.4))   #停 0.4s 看结果
        g.add_to_back(disc)   #add_to_back：圆盘插到列表头部，显示在方块下面
        win.play(Wait(0.4))   #停 0.4s 看结果
        g.remove(disc)   #先拿走：insert 不去重，已存在时会多出一份引用
        g.insert(1, disc)   #insert：按索引插入到尾部，圆盘又盖住方块
        win.play(Wait(0.4))   #停 0.4s 看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：索引、切片与迭代 ===========================================
class IndexingDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        colors = (RED, BLUE, GREEN, YELLOW, PURPLE)   #五个颜色
        g = VGroup(*[Square(color=c, side_length=0.9) for c in colors])   #五个方块装进 “VGroup”
        g.arrange(RIGHT, buff=0.35)   #排成一行
        self.add(g)   #整组进场景
        print("len(g) =", len(g))   #子对象个数
        print("g[0] =", type(g[0]).__name__, "| g[1:3] =", type(g[1:3]).__name__)   #切片返回同类型新组
        win.play(g[2].animate.shift(UP * 1.2), run_time=0.5)   #索引取出的子对象可以直接动画
        part = g[1:3]   #切片出中间两个方块
        win.play(part.animate.set_color(ORANGE), run_time=0.5)   #只改这两个的颜色
        print("迭代 =", [type(m).__name__ for m in g])   #for 循环依次取出子对象
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("ctor", CtorDemo),
    ("group", GroupDemo),
    ("add_remove", AddRemoveDemo),
    ("indexing", IndexingDemo),
]

PAIRS = [
    ("ctor", ["ctor"]),
    ("group", ["group"]),
    ("add_remove", ["add_remove"]),
    ("indexing", ["indexing"]),
]

PAGE = "01-构造与容器"


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
