# -*- coding: utf-8 -*-
"""02b-摆放位置-进阶.md 八个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02b-摆放位置-进阶.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的八条样例视频（输出到上一级 assets/）。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, Square, Rectangle, Text, Line, Dot, VGroup,
    RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, TEAL,
    UP, DOWN, LEFT, RIGHT, UL, DR, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：align_on_border ============================================
class BorderDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        a = Square(color=RED, side_length=0.9)   #贴上边的方块
        b = Square(color=BLUE, side_length=0.9)   #贴右下角的方块
        a.align_on_border(UP, buff=0.4)   #关键点贴向上方边界，留白 0.4
        b.align_on_border(DR, buff=0.4)   #关键点贴向右下角
        self.add(a, b)   #进场景
        win.play(FadeIn(a), FadeIn(b), run_time=0.6)   #两个方块淡入
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：set_coord / set_x / set_y / set_z ==========================
class CoordsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=1.2, fill_opacity=0.6)   #蓝色方块
        self.add(sq)   #进场景
        win.play(sq.animate.set_x(-3.0), run_time=0.5)   #set_x：x 设为 -3，y 不动
        win.play(sq.animate.set_y(1.5), run_time=0.5)   #set_y：y 设为 1.5，x 不动
        win.play(sq.animate.set_coord(2.5, 0), run_time=0.5)   #set_coord：dim=0 即 x 设为 2.5
        sq.set_x(0.0, direction=LEFT)   #direction=LEFT：把左边缘的 x 设为 0（中心停在 0.6）
        sq.set_z(0.5)   #set_z：改 z 坐标，2D 画面看不出变化
        print("get_z =", sq.get_z())   #验证 z 的确改成了 0.5
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：arrange ====================================================
class ArrangeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        row = VGroup(*[Square(color=c, side_length=0.8) for c in (RED, BLUE, GREEN)])   #三个方块
        row.arrange(RIGHT, buff=0.35)   #默认 center=True：整体居中
        self.add(row)   #进场景
        win.play(FadeIn(row), run_time=0.5)   #横排淡入
        win.play(row.animate.arrange(DOWN, buff=0.6), run_time=0.6)   #改成竖排，间距 0.6
        win.play(row.animate.arrange(RIGHT, buff=1.0, center=False), run_time=0.6)   #center=False：不整体回中
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：arrange_in_grid ============================================
class GridDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        colors = (RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE)   #六个颜色 = 填充顺序
        cells = VGroup(*[Square(color=c, side_length=0.7) for c in colors])   #六个方块
        cells.arrange_in_grid(rows=2, cols=3, buff=(0.4, 0.8))   #2 行 3 列，行距 0.4、列距 0.8
        self.add(cells)   #进场景
        win.play(FadeIn(cells), run_time=0.6)   #网格淡入：红橙黄在第一行
        win.play(cells.animate.arrange_in_grid(rows=3, cols=2, flow_order="dr"), run_time=0.7)   #3 行 2 列、按列填充
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：surround / replace =========================================
class SurroundReplaceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        txt = Text("target", font_size=36, color=YELLOW)   #被包住的文字
        self.add(txt)   #进场景
        frame = Rectangle(color=RED)   #空矩形
        frame.surround(txt, buff=0.25)   #surround：按宽度包住文字，留白 0.25
        self.add(frame)   #进场景
        win.play(FadeIn(frame), run_time=0.5)   #外框淡入
        panel = Rectangle(width=1.0, height=1.0, color=BLUE, fill_opacity=0.4)   #小方块
        panel.replace(txt, stretch=True)   #replace：同中心、宽高分别拉伸到与文字一致
        self.add(panel)   #进场景
        win.play(FadeIn(panel), run_time=0.5)   #衬底淡入
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 6：put_start_and_end_on =======================================
class PutEndsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        line = Line(LEFT * 2, RIGHT * 2, color=BLUE)   #初始：长度 4 的水平线
        p1 = Dot(color=RED, radius=0.1).move_to(LEFT * 3 + DOWN * 1.5)   #目标起点
        p2 = Dot(color=RED, radius=0.1).move_to(RIGHT * 1 + UP * 2)   #目标终点
        self.add(line, p1, p2)   #进场景
        win.play(line.animate.put_start_and_end_on(p1.get_center(), p2.get_center()), run_time=0.7)   #缩放+旋转+平移，把两端钉到两点
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 7：shift_onto_screen / is_off_screen ==========================
class OffScreenDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=RED, side_length=1.2)   #红色方块
        sq.shift(LEFT * 12)   #挪到画面外很远
        print("is_off_screen =", sq.is_off_screen())   #True：完全在画面外
        self.add(sq)   #进场景
        win.play(sq.animate.shift_onto_screen(buff=0.5), run_time=0.7)   #拉回画面内，留白 0.5
        print("拉回后 is_off_screen =", sq.is_off_screen())   #False
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 8：space_out_submobjects ======================================
class SpaceOutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        g = VGroup(*[Square(color=BLUE, side_length=0.7) for _ in range(3)])   #三个方块
        g.arrange(RIGHT, buff=0.05)   #几乎贴在一起
        self.add(g)   #进场景
        win.play(g.animate.space_out_submobjects(1.8), run_time=0.6)   #factor>1：只拉间距，方块不变大
        win.play(g.animate.space_out_submobjects(0.5), run_time=0.6)   #factor<1：收紧
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("border", BorderDemo),
    ("coords", CoordsDemo),
    ("arrange", ArrangeDemo),
    ("grid", GridDemo),
    ("surround_replace", SurroundReplaceDemo),
    ("put_ends", PutEndsDemo),
    ("off_screen", OffScreenDemo),
    ("space_out", SpaceOutDemo),
]

PAIRS = [
    ("border", ["border"]),
    ("coords", ["coords"]),
    ("arrange", ["arrange"]),
    ("grid", ["grid"]),
    ("surround_replace", ["surround_replace"]),
    ("put_ends", ["put_ends"]),
    ("off_screen", ["off_screen"]),
    ("space_out", ["space_out"]),
]

PAGE = "02b-摆放位置-进阶"


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
