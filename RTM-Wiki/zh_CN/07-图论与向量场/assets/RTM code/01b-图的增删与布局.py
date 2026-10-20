# -*- coding: utf-8 -*-
"""01b-图的增删与布局.md 四个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01b-图的增删与布局.py <片段名>...
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
    Scene, Graph, Text, VGroup,
    BLACK, YELLOW, GREY_B, ORANGE, UP, DOWN, LEFT,
    Write, FadeIn, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：g[k] 索引取顶点/边 ===========================================
class GetItemDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01b-Graph-getitem", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text("g[2].animate.shift(...)   g[(1,2)].animate.set_stroke(...)",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.3)   #签名标签
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        g = Graph(
            [1, 2, 3, 4], [(1, 2), (2, 3), (3, 4), (4, 1)],   #四个顶点围成一圈
            layout="circular", layout_scale=2.2,             #环形布局
            labels=True, label_fill_color=BLACK,             #顶点数字标签
        )
        win.play(Create(g), run_time=0.8)   #逐笔画出整张图
        win.play(g[2].animate.shift(UP + LEFT), run_time=0.8)   #参数 “k”：挪 2 号顶点，相连的边自动跟随
        win.play(g[(1, 2)].animate.set_stroke(ORANGE, width=8), run_time=0.5)   #参数 “k”：把 (1,2) 这条边加粗变色
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：add_vertices / add_edges ====================================
class GraphAddDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #图的动态方法内部会回放动画：先把 “self.play” 接给 win.play
        title = Text("01b-Graph-add", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text("g.animate.add_edges((1,4), positions=..., labels=True)",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.3)   #签名标签
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        g = Graph(
            [1, 2, 3], [(1, 2), (2, 3)],   #先画三个顶点两条边
            layout="circular", layout_scale=2.0,   #环形布局
            labels=True, label_fill_color=BLACK,   #顶点数字标签
        )
        win.play(Create(g), run_time=0.6)   #逐笔画出初始图
        win.play(g.animate.add_edges((1, 4), positions={4: [3.2, 1.2, 0]},   #参数 “*edges” / “positions”
                                     labels=True), run_time=0.8)   #新边连带新顶点 4 一起长出来
        win.play(g.animate.add_vertices(5, positions={5: [3.2, -1.4, 0]},   #参数 “*vertices”
                                         labels=True), run_time=0.6)   #只加一个孤点 5
        win.play(g.animate.add_edges((4, 5)), run_time=0.5)   #再把 4、5 两个新顶点连起来
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：remove_vertices / remove_edges ==============================
class GraphRemoveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #图的动态方法内部会回放动画：先把 “self.play” 接给 win.play
        title = Text("01b-Graph-remove", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text("g.animate.remove_edges((1,3))  then  g.animate.remove_vertices(4)",
                   font_size=24, color=GREY_B).next_to(title, DOWN, buff=0.3)   #签名标签
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        g = Graph(
            [1, 2, 3, 4], [(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)],   #四点成圈外加一条弦
            layout="circular", layout_scale=2.2,   #环形布局
            labels=True, label_fill_color=BLACK,   #顶点数字标签
        )
        win.play(Create(g), run_time=0.8)   #逐笔画出整张图
        win.play(g.animate.remove_edges((1, 3)), run_time=0.5)   #参数 “*edges”：只删边，顶点保留
        win.play(g.animate.remove_vertices(4), run_time=0.5)   #参数 “*vertices”：删顶点，连带它的边一起删
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：change_layout 重新布局 ======================================
class GraphChangeLayoutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #图的动态方法内部会回放动画：先把 “self.play” 接给 win.play
        title = Text("01b-Graph-change_layout", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = VGroup(
            Text('g.animate.change_layout("spring", layout_config={"seed":7})',
                 font_size=26, color=GREY_B),
            Text("g.animate.change_layout({1:[-3.2,0,0], ...})  # manual",
                 font_size=26, color=GREY_B),
        ).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.3)   #两行签名标签
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        g = Graph(
            [1, 2, 3, 4, 5], [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)],   #五点成圈
            layout="circular", layout_scale=2.2,   #初始环形布局
            labels=True, label_fill_color=BLACK,   #顶点数字标签
        )
        win.play(Create(g), run_time=0.6)   #逐笔画出整张图
        win.play(g.animate.change_layout("spring", layout_config={"seed": 7}),   #参数 “layout”
                 run_time=1.0)   #所有顶点平移到新布局，边跟着走
        win.play(g.animate.change_layout(
            {1: [-3.2, 0, 0], 2: [-1.6, 0, 0], 3: [0, 0, 0],   #手写坐标字典也是合法布局
             4: [1.6, 0, 0], 5: [3.2, 0, 0]}), run_time=1.0)   #这次把五个顶点排成一条水平线
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("getitem", GetItemDemo),
    ("add", GraphAddDemo),
    ("remove", GraphRemoveDemo),
    ("change_layout", GraphChangeLayoutDemo),
]

PAIRS = [
    ("getitem", ["getitem"]),
    ("add", ["add"]),
    ("remove", ["remove"]),
    ("change_layout", ["change_layout"]),
]

PAGE = "01b-图的增删与布局"


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
