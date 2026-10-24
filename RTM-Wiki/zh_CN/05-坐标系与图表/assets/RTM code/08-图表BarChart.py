# -*- coding: utf-8 -*-
"""08-图表BarChart.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 08-图表BarChart.py <场景名>...
不带参数就渲染全部场景，并拼出页面里的两条视频。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (  # noqa: E402
    BarChart, DOWN, FadeIn, GREY_B, Scene, Text, UP, WHITE, YELLOW,
    Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait  # noqa: E402
from real_time_manim.record import fast_record_scene  # noqa: E402


# ===== 样例 1：BarChart 构造 + get_bar_labels ==============================
class BasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("08-BarChart", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        chart = BarChart(values=[-4, 6, -2, 3],   #参数 “values”：可为负，负值柱自动朝下
                         bar_names=["one", "two", "three", "four"],   #参数 “bar_names”：x 轴标签
                         y_range=[-7, 9, 2],   #参数 “y_range”：给两元组自动补步长
                         y_length=5.5, x_length=10,   #两轴屏幕长度
                         x_axis_config={"font_size": 24})   #透传 Axes：x 轴刻度字号
        labels = chart.get_bar_labels(color=WHITE, font_size=24)   #“get_bar_labels”：柱顶数值标签（只返回，要自己 add）
        win.play(FadeIn(chart), run_time=0.8)   #整套坐标系与柱体淡入
        win.play(FadeIn(labels), run_time=0.4)   #数值标签淡入
        win.play(Wait(0.8))   #进行 0.8s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：change_bar_values 就地改柱高 ================================
class ChangeValuesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("08-change_bar_values", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        chart = BarChart(values=[3, 4, 2],   #起始柱高
                         bar_names=["A", "B", "C"],
                         y_range=[0, 10, 2],
                         y_length=5, x_length=9,
                         x_axis_config={"font_size": 24})
        lab = Text("chart.animate.change_bar_values(...)", font_size=24,
                   color=GREY_B).to_edge(UP).shift(DOWN * 0.9)   #参数说明放到标题下方
        win.play(FadeIn(chart), FadeIn(lab), run_time=0.8)   #坐标系与说明一起出场
        win.play(chart.animate.change_bar_values([7, 5, 3]),   #“change_bar_values”：就地换柱高
                 run_time=1.0)   #沿 .animate 平滑过渡
        win.play(chart.animate.change_bar_values([1, 2, 9]),
                 run_time=1.0)   #再换一次
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("08-图表BarChart-basic", BasicDemo),
    ("08-图表BarChart-changevalues", ChangeValuesDemo),
]

PAIRS = [
    ("08-图表BarChart-basic", ["08-图表BarChart-basic"]),
    ("08-图表BarChart-changevalues", ["08-图表BarChart-changevalues"]),
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
        for out_name, names in PAIRS:
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
