# -*- coding: utf-8 -*-
"""03-特殊出场.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 03-特殊出场.py <片段名>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    Scene, Text, VGroup, Circle, Dot,
    TEAL_A, GREY_B, YELLOW, LEFT, UP, DOWN,
    Broadcast, FadeIn, Write, smooth,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Broadcast 6 圈雷达波 =========================================
class BroadcastDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03-Broadcast", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("Broadcast(ring, focal_point=ORIGIN, n_mobs=6,", font_size=30, color=GREY_B)
        l2 = Text("           initial_opacity=1.0, final_opacity=0.0, initial_width=0.2,", font_size=28, color=GREY_B)
        l3 = Text("           lag_ratio=0.3, run_time=2.4)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        focal = Dot(point=DOWN * 1.4, radius=0.07, color=TEAL_A)   #发射中心
        ring = Circle(radius=2.0, color=TEAL_A).move_to(focal)   #被广播的圆环
        win.play(FadeIn(sig, shift=DOWN), FadeIn(focal), run_time=0.4)   #标签与焦点淡入
        win.play(Broadcast(ring, focal_point=focal.get_center(), n_mobs=6,   #参数 “focal_point / n_mobs”
                           initial_opacity=1.0, final_opacity=0.0, initial_width=0.2,   #参数 “opacity / initial_width”
                           lag_ratio=0.3, run_time=2.4))   #参数 “lag_ratio / run_time”
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：Broadcast 调参对比 ===========================================
class BroadcastTunedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("03-BroadcastTuned", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("Broadcast(ring, focal_point=SPOT, n_mobs=4,", font_size=30, color=GREY_B)
        l2 = Text("           initial_opacity=0.9, final_opacity=0.4, initial_width=0.5,", font_size=28, color=GREY_B)
        l3 = Text("           lag_ratio=0.5, run_time=2.2, rate_func=smooth)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #签名标签
        spot = Dot(point=LEFT * 2.6 + DOWN * 1.4, radius=0.09, color=GREY_B)   #新的发射中心
        ring = Circle(radius=1.5, color=TEAL_A).move_to(spot)   #更小的圆环
        win.play(FadeIn(sig, shift=DOWN), FadeIn(spot), run_time=0.4)   #标签与焦点淡入
        win.play(Broadcast(ring, focal_point=spot.get_center(), n_mobs=4,   #参数 “n_mobs=4”（圈数更少）
                           initial_opacity=0.9, final_opacity=0.4, initial_width=0.5,   #参数 “opacity / initial_width”（收尾半透明）
                           lag_ratio=0.5, run_time=2.2, rate_func=smooth))   #参数 “lag_ratio / rate_func”
        win.play(Wait(0.6))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("broadcast", BroadcastDemo),
    ("broadcast_tuned", BroadcastTunedDemo),
]

PAIRS = [
    ("broadcast", ["broadcast"]),
    ("broadcast_tuned", ["broadcast_tuned"]),
]

PAGE = "03-特殊出场"


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
