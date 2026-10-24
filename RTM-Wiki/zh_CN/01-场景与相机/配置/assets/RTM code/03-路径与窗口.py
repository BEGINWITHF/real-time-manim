# -*- coding: utf-8 -*-
"""03-路径与窗口.md 样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 03-路径与窗口.py <片段名>...
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import Scene, Text, VGroup, ORANGE, GREY_B, UP, DOWN, LEFT, Write, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例：config_to_rtm =================================================
class ConfigToRtmDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("config  ->  RTM", font_size=42, color=ORANGE).to_edge(UP, buff=0.7)   #标题行
        rows = VGroup(
            Text("media_dir / video_dir  ->  out_path = my.mp4", font_size=30, color=GREY_B),
            Text("window_size / window_position  ->  MLWindow(w, h)", font_size=30, color=GREY_B),
            Text("fullscreen / force_window  ->  hidden", font_size=30, color=GREY_B),
            Text("preview  ->  hidden=False", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).next_to(title, DOWN, buff=0.7)   #四行对照排好
        self.add(title)   #把标题放进场景
        win.play(Write(title), run_time=0.7)   #写出标题
        for row in rows:   #对照行一行一行上屏
            win.play(FadeIn(row, shift=UP * 0.15), run_time=0.4)   #淡入一行对照
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("config_to_rtm", ConfigToRtmDemo),
]

OUTPUTS = [
    ("03-路径与窗口-config_to_rtm", ["config_to_rtm"]),
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
