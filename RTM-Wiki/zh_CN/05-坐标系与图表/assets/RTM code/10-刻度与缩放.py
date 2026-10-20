# -*- coding: utf-8 -*-
"""10-刻度与缩放.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 10-刻度与缩放.py <场景名>...
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
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (  # noqa: E402
    Axes, BLUE, Create, DOWN, FadeIn, GREY_B, LEFT, LinearBase, LogBase,
    NumberLine, Scene, Text, UP, YELLOW,
    Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait  # noqa: E402
from real_time_manim.record import fast_record_scene  # noqa: E402


# ===== 样例 1：Axes 的 y 轴用 LogBase（对数刻度 + 10^k 标签）==============
class LogBaseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("10-LogBase", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        ax = Axes(x_range=[0, 10, 1], y_range=[-2, 6, 1], tips=False,   #两轴数据范围
                  axis_config={"include_numbers": True},   #两轴都带刻度数字
                  y_axis_config={"scaling": LogBase(custom_labels=True)})   #参数 “scaling”：y 轴改对数刻度
        graph = ax.plot(lambda x: x**2,   #画 y=x^2：在对数 y 轴上会被“压扁”成一条上升曲线
                        x_range=[0.001, 10],   #x_min 必须 > 0（LogBase 的 inverse_function 对 ≤0 抛 ValueError）
                        use_smoothing=False)
        lab = Text("y_axis_config={'scaling': LogBase()}",
                   font_size=24, color=GREY_B).to_edge(UP).shift(DOWN * 0.9)   #参数说明放标题下
        win.play(Create(ax), FadeIn(lab), run_time=0.8)   #坐标系与说明一起出场
        win.play(Create(graph), run_time=0.8)   #画出曲线
        win.play(Wait(0.8))   #进行 0.8s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：LinearBase 给刻度整体乘一个系数 ============================
class LinearBaseDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("10-LinearBase", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        base = NumberLine(x_range=[0, 6, 1], length=9,   #默认刻度：LinearBase(scale_factor=1.0)
                          include_numbers=True).shift(UP * 0.9 + LEFT * 0.6)
        wide = NumberLine(x_range=[0, 6, 1], length=9,   #参数 “scale_factor”：刻度整体乘 1.5
                          scaling=LinearBase(scale_factor=1.5),
                          include_numbers=True).shift(DOWN * 0.9)
        la = Text("LinearBase(scale_factor=1.0)  # 默认", font_size=22,
                  color=GREY_B).next_to(base, UP, buff=0.25)
        lb = Text("LinearBase(scale_factor=1.5)", font_size=22,
                  color=GREY_B).next_to(wide, DOWN, buff=0.25)
        win.play(Create(base), Create(wide), FadeIn(la), FadeIn(lb), run_time=0.8)   #两条数轴一起出场
        win.play(Wait(0.8))   #进行 0.8s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("10-刻度与缩放-logbase", LogBaseDemo),
    ("10-刻度与缩放-linearbase", LinearBaseDemo),
]

PAIRS = [
    ("10-刻度与缩放-logbase", ["10-刻度与缩放-logbase"]),
    ("10-刻度与缩放-linearbase", ["10-刻度与缩放-linearbase"]),
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
