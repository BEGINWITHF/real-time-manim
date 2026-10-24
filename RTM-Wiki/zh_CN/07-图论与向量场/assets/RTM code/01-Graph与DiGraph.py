# -*- coding: utf-8 -*-
"""01-Graph与DiGraph.md 四个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-Graph与DiGraph.py <片段名>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

import networkx as nx
from real_time_manim import (
    Scene, Graph, DiGraph, Text, VGroup,
    BLACK, YELLOW, GREY_B, RED, BLUE, BLUE_E, GREEN, ORANGE,
    UP, DOWN, Write, FadeIn, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：layout 三种布局 =============================================
class GraphLayoutDemo(Scene):
    LAYOUT = "circular"   #布局名：换成 “spring” 力导向散开，“partite” 见下方变体
    PARTITIONS = None     #“partite” 布局的分栏；其他布局留 None
    CONFIG = {}           #“layout_config”：布局算法参数（如 spring 的随机种子）

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Graph-layout", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text('layout="%s"' % self.LAYOUT, font_size=30, color=GREY_B)   #当前布局名
        lab.next_to(title, DOWN, buff=0.35)   #标签放到标题正下方
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        g = Graph(
            [1, 2, 3, 4, 5, 6],                                        #顶点：任意可哈希值
            [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1), (1, 4)],  #边：(u, v) 元组
            layout=self.LAYOUT,                                        #参数 “layout”
            layout_config=self.CONFIG,                                 #参数 “layout_config”
            partitions=self.PARTITIONS,                                #参数 “partitions”
            labels=True,                                               #参数 “labels”
            label_fill_color=BLACK,                                    #参数 “label_fill_color”
        )
        win.play(Create(g), run_time=1.2)   #逐笔画出整张图
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


class GraphLayoutSpringDemo(GraphLayoutDemo):
    LAYOUT = "spring"                      #换成力导向布局
    CONFIG = {"seed": 7}                   #固定随机种子，两引擎结果才能对上


class GraphLayoutPartiteDemo(GraphLayoutDemo):
    LAYOUT = "partite"                          #换成分栏布局
    PARTITIONS = [[1, 2, 3], [4, 5, 6]]         #两栏各三个顶点


# ===== 样例 2：vertex_config / edge_config =================================
class GraphConfigDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Graph-config", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = VGroup(
            Text("vertex_config={radius:0.16, color:YELLOW, 3:{color:RED}}",
                 font_size=26, color=GREY_B),
            Text("edge_config={stroke_width:5, color:BLUE, (1,3):{...:10}}",
                 font_size=26, color=GREY_B),
        ).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.3)   #两行参数摘要
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        g = Graph(
            [1, 2, 3, 4, 5],                                   #五个顶点
            [(1, 2), (2, 3), (3, 4), (4, 5), (1, 5), (1, 3)],  #六条边
            layout="circular", layout_scale=2.4,               #环形布局并放大一点
            labels=True,                                       #参数 “labels”
            label_fill_color=BLACK,                            #参数 “label_fill_color”
            vertex_config={"radius": 0.16, "color": YELLOW,    #公共顶点样式
                           3: {"color": RED, "radius": 0.26}}, #顶点 3 单独覆盖
            edge_config={"stroke_width": 5, "color": BLUE,     #公共边样式
                         (1, 3): {"stroke_width": 10,          #该边单独覆盖
                                  "color": ORANGE}},
        )
        win.play(Create(g), run_time=1.0)   #逐笔画出整张图
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：DiGraph 的 tip_config =======================================
class DiGraphTipDemo(Scene):
    TIP = None   #箭头尖配置：None 用默认大小，{...} 把箭头放大一号

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-DiGraph-tip", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text(
            "tip_config=%s" % ("{tip_length:0.3, tip_width:0.26}"
                               if self.TIP else "{}"),
            font_size=28, color=GREY_B,
        ).next_to(title, DOWN, buff=0.35)   #显示当前箭头尖配置
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        d = DiGraph(
            [1, 2, 3, 4],                               #顶点
            [(1, 2), (2, 3), (1, 3), (3, 4), (4, 1)],   #有向边：u 指向 v
            layout="circular", layout_scale=2.2,        #环形布局
            labels=True,                                #参数 “labels”
            label_fill_color=BLACK,                     #参数 “label_fill_color”
            edge_config={"color": BLUE_E, "stroke_width": 5,   #公共边样式
                         "tip_config": self.TIP or {}},        #参数 “tip_config”
        )
        win.play(Create(d), run_time=1.0)   #逐笔画出整张图（箭头随 updater 重定位）
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


class DiGraphTipBig(DiGraphTipDemo):
    TIP = {"tip_length": 0.3, "tip_width": 0.26}   #把箭头尖放大一号


# ===== 样例 4：from_networkx ===============================================
class FromNetworkxDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Graph-from_networkx", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text('Graph.from_networkx(nx.wheel_graph(7), layout="spring")',
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.35)   #参数摘要
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        nxg = nx.wheel_graph(7)   #networkx 的轮状图：中心 0 号 + 外圈 1~6 号
        g = Graph.from_networkx(
            nxg,                                                 #现成的 networkx 图
            layout="spring", layout_config={"seed": 5},          #布局名与随机种子
            labels=True, label_fill_color=BLACK,                #参数 “labels”
            vertex_config={"color": GREEN, "radius": 0.15},      #公共顶点样式
        )
        win.play(Create(g), run_time=1.2)   #逐笔画出整张图
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("graph_layout_circular", GraphLayoutDemo),
    ("graph_layout_spring", GraphLayoutSpringDemo),
    ("graph_layout_partite", GraphLayoutPartiteDemo),
    ("graph_config", GraphConfigDemo),
    ("digraph_tip_default", DiGraphTipDemo),
    ("digraph_tip_big", DiGraphTipBig),
    ("graph_from_networkx", FromNetworkxDemo),
]

PAIRS = [
    ("layout", ["graph_layout_circular", "graph_layout_spring",
                "graph_layout_partite"]),
    ("config", ["graph_config"]),
    ("digraph", ["digraph_tip_default", "digraph_tip_big"]),
    ("from_networkx", ["graph_from_networkx"]),
]

PAGE = "01-Graph与DiGraph"


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
