# -*- coding: utf-8 -*-
"""04b-带标签标注.md 四个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 04b-带标签标注.py <样例名>...
不带参数就渲染全部样例，并拼出页面里的四条样例视频（输出到 assets/RTM output/）。
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
    Scene, Label, LabeledLine, LabeledArrow, LabeledPolygram,
    Line, Arrow, Polygon, Triangle, Square, Text,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Label —— 文本 + 背景框 + 边框 ===============================
class LabelDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04b-Label", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 默认：白字 + 默认背景框 ——
        l1 = Label("x")   #参数 “label”：字符串用 MathTex 渲染
        l1.move_to([-4.2, 1.2, 0])
        cap1 = Text('Label("x")', font_size=18, color=GREY_B).next_to(l1, DOWN, buff=0.3)
        win.play(FadeIn(l1), FadeIn(cap1), run_time=0.5)

        # —— label_config：只对字符串标签生效（颜色 / 字号）——
        l2 = Label("y", label_config={"color": RED, "font_size": 72})   #参数 “label_config”
        l2.move_to([-0.6, 1.2, 0])
        cap2 = Text('label_config={"color": RED, "font_size": 72}', font_size=18, color=GREY_B).next_to(l2, DOWN, buff=0.3)
        win.play(FadeIn(l2), FadeIn(cap2), run_time=0.5)

        # —— box_config：背景框的颜色与不透明度 ——
        l3 = Label("z", box_config={"color": TEAL, "fill_opacity": 0.8})   #参数 “box_config”
        l3.move_to([3.0, 1.2, 0])
        cap3 = Text('box_config={"color": TEAL, "fill_opacity": 0.8}', font_size=18, color=GREY_B).next_to(l3, DOWN, buff=0.3)
        win.play(FadeIn(l3), FadeIn(cap3), run_time=0.5)

        # —— frame_config：外框的颜色与线宽 ——
        l4 = Label("w", frame_config={"color": ORANGE, "stroke_width": 6})   #参数 “frame_config”
        l4.move_to([-4.2, -1.0, 0])
        cap4 = Text('frame_config={"color": ORANGE, "stroke_width": 6}', font_size=18, color=GREY_B).next_to(l4, DOWN, buff=0.3)
        win.play(FadeIn(l4), FadeIn(cap4), run_time=0.5)

        # —— label 不是字符串时不读 *_config：直接拿现成 mobject 当标签 ——
        l5 = Label(Text("hi", color=YELLOW, font_size=40),
                   label_config={"color": RED})   #参数 “label” 给 Mobject：config 被忽略
        l5.move_to([-0.6, -1.0, 0])
        cap5 = Text("Label(Text(...))  config 被忽略", font_size=18, color=GREY_B).next_to(l5, DOWN, buff=0.3)
        win.play(FadeIn(l5), FadeIn(cap5), run_time=0.5)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：LabeledLine —— 线上带标签 ===================================
class LabeledLineDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04b-LabeledLine", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— label_position：标签在线上的位置比例（0 起点 ~ 1 终点）——
        for i, pos in enumerate([0.2, 0.5, 0.8]):   #参数 “label_position”
            ln = LabeledLine("3cm", start=[-4.4, 1.5 - i * 1.5, 0], end=[-0.4, 1.5 - i * 1.5, 0],
                             label_position=pos)   #参数 “start / end 必须用关键字”
            cap = Text("label_position=%.1f" % pos, font_size=18, color=GREY_B).next_to(ln, RIGHT, buff=0.4)
            win.play(Create(ln), FadeIn(cap), run_time=0.5)   #标签沿线滑动

        # —— label_config / box_config / frame_config 三件套 ——
        ln2 = LabeledLine("L", start=[1.6, 0.4, 0], end=[5.4, 0.4, 0],
                          label_config={"color": RED, "font_size": 64},
                          box_config={"color": TEAL, "fill_opacity": 0.8},
                          frame_config={"color": ORANGE, "stroke_width": 5})
        cap2 = Text("label/box/frame_config", font_size=18, color=GREY_B).next_to(ln2, DOWN, buff=0.4)
        win.play(Create(ln2), FadeIn(cap2), run_time=0.6)

        # —— 同一根线也能给现成 mobject 当标签 ——
        ln3 = LabeledLine(Text("Tetra", color=YELLOW, font_size=32),
                          start=[1.6, -1.4, 0], end=[5.4, -1.4, 0], label_position=0.35)
        cap3 = Text("label=Text(...)  label_position=0.35", font_size=18, color=GREY_B).next_to(ln3, DOWN, buff=0.4)
        win.play(Create(ln3), FadeIn(cap3), run_time=0.6)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：LabeledArrow —— 箭头版 ======================================
class LabeledArrowDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04b-LabeledArrow", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 与 LabeledLine 同一套参数，只是形状是箭头 ——
        for i, pos in enumerate([0.2, 0.6]):   #参数 “label_position”
            arr = LabeledArrow("5m", start=[-4.4, 1.2 - i * 1.9, 0], end=[0.4, 1.2 - i * 1.9, 0],
                               label_position=pos, color=GOLD)   #颜色等继续传给 Arrow
            cap = Text("label_position=%.1f" % pos, font_size=18, color=GREY_B).next_to(arr, DOWN, buff=0.35)
            win.play(Create(arr), FadeIn(cap), run_time=0.6)

        # —— 三件套配置同样可用 ——
        arr2 = LabeledArrow("A", start=[2.0, 0.2, 0], end=[5.6, 0.2, 0],
                            label_config={"color": RED, "font_size": 60},
                            box_config={"color": PURPLE, "fill_opacity": 0.8},
                            frame_config={"color": YELLOW, "stroke_width": 5})
        cap2 = Text("label/box/frame_config", font_size=18, color=GREY_B).next_to(arr2, DOWN, buff=0.4)
        win.play(Create(arr2), FadeIn(cap2), run_time=0.6)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：LabeledPolygram —— 多边形内部自动找位置 =====================
class LabeledPolygramDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("04b-LabeledPolygram", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 一个顶点组（一组闭合环）：标签自动落在多边形内部最“宽敞”的位置 ——
        ring = [[-5.4, -0.4, 0], [-3.4, -0.4, 0], [-4.4, 1.6, 0]]   #参数 “*vertex_groups”：每组是一圈顶点
        tri = LabeledPolygram(ring, label="A", color=TEAL)   #参数 “label”
        win.play(Create(tri), FadeIn(Text("one ring, label=\"A\"", font_size=18, color=GREY_B).next_to(tri, DOWN, buff=0.35)),
                 run_time=0.6)

        # —— precision：PolyLabel 算法的搜索精度，要与图形尺度匹配 ——
        square = [[-1.8, -0.6, 0], [1.4, -0.6, 0], [1.4, 1.6, 0], [-1.8, 1.6, 0]]
        big = LabeledPolygram(square, label="B", precision=0.5, color=GREEN)   #参数 “precision=0.5”
        win.play(Create(big), FadeIn(Text("precision=0.5", font_size=18, color=GREY_B).next_to(big, DOWN, buff=0.35)),
                 run_time=0.6)

        # —— 多个顶点组：每个环各自闭合，标签落在最大的那块里 ——
        two = LabeledPolygram([[3.2, 0.2, 0], [5.6, 0.2, 0], [4.4, 1.8, 0]],   #第一圈：大三角
                              [[6.0, 0.2, 0], [6.8, 0.2, 0], [6.4, 0.8, 0]],   #第二圈：小三角
                              label="2x", color=ORANGE)   #参数 “*vertex_groups”：两组环
        win.play(Create(two), FadeIn(Text("two rings, label=\"2x\"", font_size=18, color=GREY_B).next_to(two, DOWN, buff=0.35)),
                 run_time=0.6)

        # —— 标签配置三件套：label_config / box_config / frame_config ——
        poly = LabeledPolygram([[-5.4, -2.6, 0], [-3.4, -2.6, 0], [-4.4, -1.0, 0]],
                               label="C",
                               label_config={"color": RED, "font_size": 60},
                               box_config={"color": TEAL, "fill_opacity": 0.8},
                               frame_config={"color": ORANGE, "stroke_width": 5})
        win.play(Create(poly), FadeIn(Text("label/box/frame_config", font_size=18, color=GREY_B).next_to(poly, DOWN, buff=0.35)),
                 run_time=0.6)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("label", LabelDemo),
    ("labeledline", LabeledLineDemo),
    ("labeledarrow", LabeledArrowDemo),
    ("labeledpoly", LabeledPolygramDemo),
]

PAIRS = [
    ("label", ["label"]),
    ("labeledline", ["labeledline"]),
    ("labeledarrow", ["labeledarrow"]),
    ("labeledpoly", ["labeledpoly"]),
]

PAGE = "04b-带标签标注"


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
