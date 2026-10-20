# -*- coding: utf-8 -*-
"""01b-构造与容器-进阶.md 五个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01b-构造与容器-进阶.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的五条样例视频（输出到上一级 assets/）。
"""
import os
import subprocess
import sys
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, Group, VGroup,
    Square, Rectangle, Circle, Text,
    WHITE, RED, BLUE, YELLOW, GREEN, ORANGE, PURPLE,
    RIGHT, DOWN, UP, LEFT, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：get_family / family_members_with_points / split ============
class FamilyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        inner = VGroup(Square(color=RED, side_length=1.0), Square(color=BLUE, side_length=1.0))   #里层：两个方块
        inner.arrange(RIGHT, buff=0.4)   #里层排成一行
        empty = Group()   #空容器：一个顶点都没有
        solo = Square(color=GREEN, side_length=1.0)   #独立方块
        outer = Group(inner, empty, solo)   #外层：里层组、空组、一个方块
        inner.shift(LEFT * 2.2)   #里层组放左边（别用 arrange：空组宽度为 0，会挤到一起）
        solo.shift(RIGHT * 2.2)   #独立方块放右边
        outer.shift(UP * 1.0)   #整棵树抬高一点
        self.add(outer)   #整棵树进场景
        print("get_family =", len(outer.get_family()), [type(m).__name__ for m in outer.get_family()])   #自身+全部后代
        print("family_members_with_points =", [type(m).__name__ for m in outer.family_members_with_points()])   #只留有顶点的
        print("split =", [type(m).__name__ for m in outer.split()])   #自身(有点时)+直接子对象
        for i, m in enumerate(outer.family_members_with_points()):   #真正会被 shift/scale 作用的对象
            m.set_color([ORANGE, YELLOW, PURPLE][i])   #逐个染色：只有三个方块被染到
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：has_points / has_no_points / get_num_points ================
class PointsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        g = Group()   #空容器
        sq = Square(color=BLUE, side_length=1.6)   #有顶点的方块
        txt = Text("points", font_size=36, color=YELLOW)   #文字：点在字形子对象里
        sq.shift(LEFT * 3.2)   #方块放左边
        txt.shift(RIGHT * 2.4)   #文字放右边
        self.add(sq, txt)   #两个对象进场景
        print("空 Group：has_points =", g.has_points(), "has_no_points =", g.has_no_points(), "get_num_points =", g.get_num_points())   #全是“空”
        print("Square：has_points =", sq.has_points(), "get_num_points =", sq.get_num_points())   #方块自带顶点
        print("Text 本身 get_num_points =", txt.get_num_points(), "| 字形 =", [m.get_num_points() for m in txt.submobjects])   #点在字形里
        win.play(FadeIn(sq), FadeIn(txt), run_time=0.5)   #淡入两个对象
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：set ========================================================
class SetDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        rect = Rectangle(width=3.0, height=1.4, color=BLUE, fill_opacity=0.6)   #一个矩形
        self.add(rect)   #进场景
        win.play(rect.animate.set(width=5.0, color=ORANGE), run_time=0.7)   #“set” 配合 animate：一次改多个属性
        rect.set(fill_opacity=1.0)   #不加 “animate” 就是瞬间改
        print("rect.width =", rect.width, "| rect.color =", rect.color)   #属性读取验证
        with warnings.catch_warnings(record=True) as w:   #兼容层的 get_foo / set_foo 会发警告
            warnings.simplefilter("always")
            rect.set_width(4.0)   #兼容层写法：能用但会发 DeprecationWarning
            print("兼容层警告 =", [str(x.message)[:24] for x in w])   #看一眼警告内容
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：set_default（类方法）======================================
class SetDefaultDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        before = Square()   #默认方块：边长 2、白色
        Square.set_default(side_length=1.0, color=YELLOW)   #把 “Square” 的默认边长改成 1、默认颜色改成黄
        after = Square()   #新建对象用新默认值
        Square.set_default()   #不带参数调用：恢复原始默认值
        back = Square()   #再建一个：又回到默认
        trio = VGroup(before, after, back)   #三个方块一组
        trio.arrange(RIGHT, buff=0.8)   #排成一行，大小差别一眼看出
        self.add(trio)   #进场景
        print("边长：", before.width, after.width, back.width)   #2.0 1.0 2.0
        win.play(FadeIn(trio), run_time=0.6)   #整组淡入
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：reset_points / generate_points / init_colors ===============
class WideCircle(Circle):   #自定义子类：在构造钩子里改形状
    def generate_points(self):   #构造函数调它生成形状
        super().generate_points()   #先按 “Circle” 的默认形状生成
        self.stretch(1.6, 0)   #再横向拉宽，得到“宽椭圆”


class HooksDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        wc = WideCircle(radius=0.9, color=GREEN)   #自定义子类：生成后被拉宽
        c = Circle(radius=0.9, color=BLUE)   #普通圆对照
        duo = VGroup(wc, c)   #两个圆一组
        duo.arrange(DOWN, buff=0.6)   #上下排好
        self.add(duo)   #进场景
        win.play(FadeIn(duo), run_time=0.5)   #淡入：上面是宽椭圆
        c.reset_points()   #清空所有顶点：圆消失
        win.play(Wait(0.5))   #停 0.5s 看消失
        c.generate_points()   #重新生成形状：默认圆在原点又出现
        c.init_colors()   #按 “color” 重新初始化样式
        win.play(Wait(0.5))   #停 0.5s 看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("family", FamilyDemo),
    ("points", PointsDemo),
    ("set", SetDemo),
    ("set_default", SetDefaultDemo),
    ("hooks", HooksDemo),
]

PAIRS = [
    ("family", ["family"]),
    ("points", ["points"]),
    ("set", ["set"]),
    ("set_default", ["set_default"]),
    ("hooks", ["hooks"]),
]

PAGE = "01b-构造与容器-进阶"


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
