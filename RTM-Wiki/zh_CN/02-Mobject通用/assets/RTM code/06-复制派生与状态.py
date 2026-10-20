# -*- coding: utf-8 -*-
"""06-复制派生与状态.md 七个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 06-复制派生与状态.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的七条样例视频（输出到上一级 assets/）。
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
    Scene, VGroup, Square, Rectangle, Circle, Text,
    BLUE, RED, GREEN, YELLOW, ORANGE, PURPLE, TEAL, GREY,
    UP, DOWN, LEFT, RIGHT, ORIGIN, PI, FadeIn, MoveToTarget, straight_path,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：copy =======================================================
class CopyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=1.4, fill_opacity=0.6).shift(LEFT * 3.5)   #原件
        self.add(sq)   #进场景
        twin = sq.copy()   #深拷贝：独立副本，不会自动进场景
        twin.set_color(RED).shift(RIGHT * 2.0)   #副本改色、挪走：与原件互不影响
        self.add(twin)   #副本进场景
        win.play(FadeIn(twin), run_time=0.5)   #副本淡入
        win.play(sq.animate.set_color(GREEN), run_time=0.5)   #改原件颜色：副本纹丝不动
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：become =====================================================
class BecomeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        circ = Circle(radius=0.9, color=ORANGE, fill_opacity=0.7)   #圆形
        self.add(circ)   #进场景
        rect = Rectangle(width=3.0, height=1.4, color=PURPLE, fill_opacity=0.7).shift(RIGHT * 3.2)   #目标矩形在右边
        win.play(circ.animate.become(rect), run_time=0.6)   #形态与位置一起变成目标的样子
        print("become 后：width =", round(circ.width, 2), "位置 =", circ.get_center().round(2))   #3.0，跑到右边
        dot = Circle(radius=0.3, color=TEAL).shift(LEFT * 3.2)   #目标小圆在左边
        win.play(circ.animate.become(dot, match_center=True, stretch=True),
                 run_time=0.5)   #stretch 把目标拉成自己的 3.0×1.4（小圆→椭圆），match_center 位置不动
        print("stretch+center 后：", round(circ.width, 2), round(circ.height, 2), circ.get_center().round(2))   #3.0 1.4 位置不变
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：save_state / restore ======================================
class SaveRestoreDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE, side_length=1.4, fill_opacity=0.7).shift(LEFT * 3.0)   #蓝色方块
        self.add(sq)   #进场景
        sq.save_state()   #把位置/大小/颜色/结构存进 saved_state
        win.play(sq.animate.scale(1.8).set_color(GREEN).shift(RIGHT * 3.0), run_time=0.7)   #放大、改绿、右移
        win.play(sq.animate.restore(), run_time=0.6)   #还原到存档时的状态
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：generate_target + MoveToTarget =============================
class TargetDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=YELLOW, side_length=1.2).shift(LEFT * 3.5)   #黄色方块
        self.add(sq)   #进场景
        sq.generate_target(use_deepcopy=False)   #生成 self.target 快照（本体不消失）
        sq.target.shift(RIGHT * 3.0).scale(1.6).set_color(TEAL)   #在快照上摆出目标形态
        win.play(MoveToTarget(sq), run_time=0.7)   #本体动画到目标形态
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：interpolate ===============================================
class InterpolateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=GREEN, side_length=1.2)   #绿色方块
        self.add(sq)   #进场景
        win.play(Wait(0.4))   #看清起点状态
        s1 = sq.copy()   #起点状态
        s2 = sq.copy().shift(RIGHT * 2.5).scale(1.5).rotate(PI / 4)   #终点状态
        sq.interpolate(s1, s2, 0.5, path_func=straight_path())   #直接取 alpha=0.5 的插值态（瞬间）
        win.play(Wait(0.5))   #看清中间状态
        win.play(sq.animate.become(s2), run_time=0.4)   #再动到终点状态对照
        win.play(Wait(0.3))   #进行 0.3s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 6：match_dim_size / match_width / match_height / match_depth =
class MatchSizeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        ref = Rectangle(width=2.6, height=1.0, color=GREY, fill_opacity=0.5).shift(UP * 1.6)   #参照矩形
        m1 = Square(color=BLUE, side_length=1.0).shift(LEFT * 3.0)   #等比对照
        m2 = Square(color=RED, side_length=1.8).shift(LEFT * 1.0)   #拉伸对照
        self.add(ref, m1, m2)   #进场景
        win.play(m1.animate.match_width(ref), run_time=0.5)   #等比缩到与参照同宽
        print("match_width 后：", round(m1.width, 2), round(m1.height, 2))   #2.6 2.6
        win.play(m2.animate.match_dim_size(ref, 1, stretch=True), run_time=0.5)   #match_dim_size：dim=1，只压这一维
        print("match_dim_size 后：", round(m2.width, 2), round(m2.height, 2))   #1.8 1.0
        m2.match_depth(ref)   #match_depth：平面对象安全 no-op（维度长度都是 0）
        print("match_depth 后：", round(m2.width, 2), round(m2.height, 2))   #不变
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 7：match_coord / match_points / align_points =================
class MatchPosDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        ref = Circle(radius=0.8, color=GREY, fill_opacity=0.5).shift(UP * 1.5 + RIGHT * 2.0)   #参照圆
        m1 = Square(color=BLUE, side_length=1.0).shift(LEFT * 3.5 + DOWN * 1.5)   #x 对齐对照
        m2 = Square(color=RED, side_length=1.0).shift(LEFT * 1.5 + DOWN * 1.5)   #y 边缘对齐对照
        self.add(ref, m1, m2)   #进场景
        win.play(m1.animate.match_x(ref), run_time=0.5)   #match_x：x 对齐到参照中心
        win.play(m2.animate.match_coord(ref, 1, direction=DOWN), run_time=0.5)   #match_coord：dim=1，按下边缘对齐
        print("ref 中心 =", ref.get_center().round(2), "| m1 中心 =", m1.get_center().round(2))   #x 相同
        mp = Circle(color=TEAL, radius=0.4).shift(LEFT * 3.5 + UP * 1.5)   #待变形的圆
        self.add(mp)   #进场景
        win.play(mp.animate.match_points(ref), run_time=0.5)   #match_points：顶点照抄参照（形状大小一起变）
        print("match_points 后 width =", round(mp.width, 2))   #1.6 与参照一致
        mp.align_points(ref)   #align_points：把顶点数对齐（插值的前提）
        print("align_points 后点数 =", mp.get_num_points(), ref.get_num_points())   #两边一致
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("copy", CopyDemo),
    ("become", BecomeDemo),
    ("save_restore", SaveRestoreDemo),
    ("target", TargetDemo),
    ("interpolate", InterpolateDemo),
    ("match_size", MatchSizeDemo),
    ("match_pos", MatchPosDemo),
]

PAIRS = [
    ("copy", ["copy"]),
    ("become", ["become"]),
    ("save_restore", ["save_restore"]),
    ("target", ["target"]),
    ("interpolate", ["interpolate"]),
    ("match_size", ["match_size"]),
    ("match_pos", ["match_pos"]),
]

PAGE = "06-复制派生与状态"


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
