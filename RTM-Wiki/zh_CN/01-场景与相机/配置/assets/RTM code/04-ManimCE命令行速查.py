# -*- coding: utf-8 -*-
"""04-ManimCE命令行速查.md 样例的完整源码（与页面里的代码块逐字一致）。

本页是全 wiki 唯一允许出现 ManimCE 内容的页面，样例画的也是命令行速查表。

跑法：python 04-ManimCE命令行速查.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的对比视频。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
ASSETS = os.path.dirname(HERE)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from manim import (
    Scene, Text, VGroup,
    ORANGE, GREY_B, YELLOW, GREEN, UP, DOWN, LEFT,
    Write, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：画质档位 ====================================================
class QualityTiersDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        rows = VGroup(
            Text("-ql    854x480 @ 15", font_size=32, color=GREY_B),
            Text("-qm    1280x720 @ 30", font_size=32, color=GREY_B),
            Text("-qh    1920x1080 @ 60", font_size=32, color=YELLOW),
            Text("-qp    2560x1440 @ 60", font_size=32, color=GREY_B),
            Text("-qk    3840x2160 @ 60", font_size=32, color=GREY_B),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)   #五档画质从上到下排好
        note = Text("RTM = 1920x1080 @ 60 only", font_size=34,
                    color=ORANGE).to_edge(DOWN, buff=0.7)   #RTM 只有这一档
        self.add(rows)   #把五档画质放进场景
        win.play(FadeIn(rows, shift=UP * 0.2), run_time=0.8)   #五档画质淡入
        win.play(Write(note), run_time=0.7)   #写出 RTM 的固定档位
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：命令行 ↔ RTM 调用 ==========================================
class CliEquivDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        cli = Text("manim -qh -o my_video --fps 60 scene.py Hello",
                   font_size=30, color=ORANGE).shift(UP * 1.2)   #ManimCE 的命令行
        same = Text("same output", font_size=26, color=GREY_B)   #两行中间的说明
        call = Text("fast_record_scene(Hello, out_path='my_video.mp4', fps=60)",
                    font_size=30, color=GREEN).shift(DOWN * 1.2)   #RTM 的函数调用
        self.add(cli, same, call)   #把三行文字放进场景
        win.play(FadeIn(cli, shift=UP * 0.2), run_time=0.6)   #先上命令行
        win.play(FadeIn(same), run_time=0.4)   #再上中间的说明
        win.play(FadeIn(call, shift=DOWN * 0.2), run_time=0.6)   #最后上 RTM 调用
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("quality_tiers", QualityTiersDemo),
    ("cli_equiv", CliEquivDemo),
]

OUTPUTS = [
    ("04-ManimCE命令行速查-quality_tiers", ["quality_tiers"]),
    ("04-ManimCE命令行速查-cli_equiv", ["cli_equiv"]),
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
        for out_name, names in OUTPUTS:
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
