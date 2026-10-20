# -*- coding: utf-8 -*-
"""02b-流线StreamLines.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02b-流线StreamLines.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的两条样例视频（输出到上一级 assets/）。
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

import numpy as np
from real_time_manim import (
    Scene, Text, StreamLines,
    YELLOW, GREY_B, BLUE, UP, DOWN, LEFT,
    Write, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：create 逐条随机顺序画出 =====================================
class StreamLinesCreateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02b-StreamLines-create", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text("sl.create(run_time=..., lag_ratio=...)",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.3)   #签名标签
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        func = lambda pos: np.sin(pos[0] / 2) * UP + np.cos(pos[1] / 2) * LEFT   #场函数
        sl = StreamLines(
            func,                                   #参数 “func”
            x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],   #出生网格
            color=BLUE,                             #参数 “color”：整体蓝色
            stroke_width=3,                         #参数 “stroke_width”
            max_anchors_per_line=15,                #抽稀锚点：创建更快、线更顺
            virtual_time=1,                         #参数 “virtual_time”：轨迹模拟时长
        )
        win.play(sl.create(run_time=1.4), run_time=1.4)   #逐条随机顺序画出
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：start_animation / end_animation 持续流动 ====================
class StreamLinesFlowDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("02b-StreamLines-flow", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text("start_animation(flow_speed=1.5, time_width=0.5) ... end_animation()",
                   font_size=24, color=GREY_B).next_to(title, DOWN, buff=0.3)   #签名标签
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        func = lambda pos: np.sin(pos[0] / 2) * UP + np.cos(pos[1] / 2) * LEFT   #场函数
        sl = StreamLines(
            func,                                   #参数 “func”
            x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],   #出生网格
            color=BLUE,                             #参数 “color”：整体蓝色
            stroke_width=3,                         #参数 “stroke_width”
            max_anchors_per_line=15,                #抽稀锚点
            virtual_time=1,                         #参数 “virtual_time”
        )
        win.play(sl.create(run_time=0.8), run_time=0.8)   #先把流线画出来
        self.add(sl)   #把 “sl” 收进场景：updater 挂在它身上，不 add 就整片黑屏
        sl.start_animation(warm_up=False, flow_speed=1.5, time_width=0.5)   #参数 “flow_speed” / “time_width”
        win.play(Wait(2.0))   #光点沿线持续流动 2 秒
        win.play(sl.end_animation(), run_time=0.6)   #平滑收束持续动画
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("create", StreamLinesCreateDemo),
    ("flow", StreamLinesFlowDemo),
]

PAIRS = [
    ("create", ["create"]),
    ("flow", ["flow"]),
]

PAGE = "02b-流线StreamLines"


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
