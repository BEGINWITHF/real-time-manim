# -*- coding: utf-8 -*-
"""05-样式与颜色.md 六个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 05-样式与颜色.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的六条样例视频（输出到上一级 assets/）。
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
    Scene, Group, VGroup, Square, Circle, Text, Rectangle,
    BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, WHITE, BLACK, TEAL,
    UP, DOWN, LEFT, RIGHT, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：set_color ==================================================
class SetColorDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=2.2, fill_opacity=0.7)   #蓝色方块
        kid = Square(color=YELLOW, side_length=0.8, fill_opacity=0.9)   #黄色小方块
        g = Group(sq, kid)   #小方块作为子对象放进组
        self.add(g)   #进场景
        win.play(g.animate.set_color(ORANGE), run_time=0.6)   #默认 family=True：整组连子对象全改
        win.play(g.animate.set_color(GREEN, family=False), run_time=0.6)   #family=False：只改组自身属性
        print("sq =", sq.get_color(), "| kid =", kid.get_color())   #子对象停在橙色：family=False 不下放
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：渐变四件套 ================================================
class GradientDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        r1 = VGroup(*[Square(side_length=0.8) for _ in range(4)])   #一排四个方块
        r1.arrange(RIGHT, buff=0.25).shift(UP * 2.2)
        self.add(r1)   #进场景
        win.play(r1.animate.set_color_by_gradient(BLUE, RED), run_time=0.5)   #整组渐变：四个方块依次取中间色
        r2 = VGroup(*[Square(side_length=0.8) for _ in range(4)])   #第二排
        r2.arrange(RIGHT, buff=0.25).shift(UP * 0.7)
        self.add(r2)   #进场景
        win.play(r2.animate.set_submobject_colors_by_gradient(GREEN, PURPLE), run_time=0.5)   #直接对子对象逐个上色（等价实现）
        r3 = VGroup(*[Circle(radius=0.2 + 0.15 * i) for i in range(3)])   #第三排：大小不一的圆
        r3.arrange(RIGHT, buff=0.35).shift(DOWN * 1.0)
        self.add(r3)   #进场景
        win.play(r3.animate.set_colors_by_radial_gradient(radius=1.6, inner_color=WHITE, outer_color=BLUE), run_time=0.5)   #径向：按离中心的距离取色
        r4 = VGroup(*[Circle(radius=0.2 + 0.15 * i) for i in range(3)])   #第四排
        r4.arrange(RIGHT, buff=0.35).shift(DOWN * 2.4)
        self.add(r4)   #进场景
        win.play(r4.animate.set_submobject_colors_by_radial_gradient(radius=1.6, inner_color=YELLOW, outer_color=RED), run_time=0.5)   #同上
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：fade_to / fade ============================================
class FadeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        f1 = Square(color=BLUE, side_length=1.4, fill_opacity=0.8).shift(LEFT * 2.5)   #左侧：混色
        f2 = Square(color=BLUE, side_length=1.4, fill_opacity=0.8).shift(RIGHT * 2.5)   #右侧：变淡
        self.add(f1, f2)   #进场景
        win.play(f1.animate.fade_to(RED, 0.7), run_time=0.6)   #向红色混合 70%
        win.play(f2.animate.fade(darkness=0.6), run_time=0.6)   #矢量对象变淡 60%
        print("f1 =", f1.get_color(), "| f2 =", f2.get_color())   #颜色读数验证
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：get_color / match_color / to_original_color ===============
class GetMatchDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        a = Square(color=RED, side_length=1.4).shift(LEFT * 3.0 + UP * 1.2)   #红方块
        b = Square(color=GREEN, side_length=1.4).shift(RIGHT * 3.0 + UP * 1.2)   #绿方块
        self.add(a, b)   #进场景
        print("a =", a.get_color())   #读取当前颜色
        win.play(a.animate.match_color(b), run_time=0.6)   #把 a 的颜色设成 b 的
        print("match 后：a =", a.get_color(), "b =", b.get_color())
        w = Text("color", font_size=38, color=WHITE).shift(DOWN * 1.6)   #白色文字：字形各自能染色
        w[0:2].set_color(RED)   #只把前两个字母染红
        self.add(w)   #进场景
        win.play(FadeIn(w), run_time=0.4)   #文字淡入
        win.play(Wait(0.5))   #看清前两个字母是红的
        w.to_original_color()   #整体按 self.color 重置：字形的单独颜色被清掉
        print("reset 后 w =", w.get_color())   #属性打印是黑色（Text 的 color 默认黑）
        win.play(Wait(0.5))   #看清字形全部恢复
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：set_z_index / set_z_index_by_z_Point3D ====================
class ZIndexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        zA = Square(color=RED, side_length=2.2, fill_opacity=0.85).shift(LEFT * 2.2)   #红方块
        zB = Square(color=BLUE, side_length=2.2, fill_opacity=0.85).shift(LEFT * 1.3)   #蓝方块
        self.add(zA, zB)   #后加的蓝色在上（同层级时按加入顺序）
        win.play(Wait(0.5))   #先看默认叠放
        zA.set_z_index(2)   #红色层级设为 2：瞬间反超到上层
        win.play(Wait(0.5))   #停一下看红色盖住蓝色
        zB.set_z(3.0)   #给蓝色一个 z 坐标（2D 画面看不出位置变化）
        zB.set_z_index_by_z_Point3D()   #蓝色层级 = 中心 z 坐标 = 3：又盖回去
        print("z_index:", zA.z_index, zB.z_index)   #2 3
        win.play(Wait(0.5))   #停一下看蓝色盖住红色
        win.close()   #关闭 RTM 窗口


# ===== 样例 6：add_background_rectangle 三个变体 =========================
class BgRectDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        bg = VGroup(*[Rectangle(width=2.0, height=6.0, color=c, fill_opacity=1.0) for c in (RED, BLUE, GREEN)])   #三条彩色竖条
        bg.arrange(RIGHT, buff=0)
        self.add(bg)   #花哨背景
        txt = Text("READABLE", font_size=44, color=WHITE).shift(UP * 1.6)   #白字
        txt.add_background_rectangle(color=BLACK, opacity=0.75)   #背后垫一块半透明黑
        self.add(txt)
        win.play(FadeIn(bg), FadeIn(txt), run_time=0.6)   #背景与文字一起淡入
        duo = VGroup(Text("A", font_size=36), Text("B", font_size=36)).arrange(RIGHT, buff=0.9)
        duo.shift(UP * 0.1)
        duo.add_background_rectangle_to_submobjects(color=BLACK, opacity=0.7)   #给每个字母各垫一块
        self.add(duo)
        rings = VGroup(Circle(radius=0.35), Circle(radius=0.35)).arrange(RIGHT, buff=0.4).shift(DOWN * 1.8)
        rings.add_background_rectangle_to_family_members_with_points(color=BLACK, opacity=0.7)   #给每个有顶点的成员垫一块
        self.add(rings)
        win.play(FadeIn(duo), FadeIn(rings), run_time=0.5)   #两组元素淡入
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("set_color", SetColorDemo),
    ("gradient", GradientDemo),
    ("fade", FadeDemo),
    ("get_match", GetMatchDemo),
    ("z_index", ZIndexDemo),
    ("background", BgRectDemo),
]

PAIRS = [
    ("set_color", ["set_color"]),
    ("gradient", ["gradient"]),
    ("fade", ["fade"]),
    ("get_match", ["get_match"]),
    ("z_index", ["z_index"]),
    ("background", ["background"]),
]

PAGE = "05-样式与颜色"


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
