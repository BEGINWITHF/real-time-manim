# -*- coding: utf-8 -*-
"""01-画质与输出.md 样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-画质与输出.py <片段名>...
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

from real_time_manim import Scene, Square, Text, WHITE, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例：background_color ==============================================
class BackgroundColorDemo(Scene):
    BG = "#12233a"    #背景色：改成 “#e8e4d8” 再跑一次，整屏清屏色跟着换
    TXT = "#e8e4d8"   #标签颜色：浅色背景要换成深色才看得清

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.camera.background_color = self.BG   #把 “background_color” 交给相机：清屏色就是它
        label = Text("background_color = %s" % self.BG, font_size=38,
                     color=self.TXT).to_edge(UP)   #上屏显示当前背景色
        sq = Square(side_length=2.0, color=WHITE).set_fill(WHITE, 0.8).set_stroke(width=4)   #白色方块：和背景拉开反差
        self.add(label)   #把标签放进场景
        win.play(Create(sq), run_time=0.8)   #画出白色方块
        win.play(sq.animate.scale(1.25), run_time=0.6)   #方块再放大一点
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


class BackgroundColorLight(BackgroundColorDemo):
    BG = "#e8e4d8"    #同一个场景，只把 “background_color” 换成米白
    TXT = "#12233a"   #标签换回深蓝


SCENES = [
    ("bg_dark", BackgroundColorDemo),
    ("bg_light", BackgroundColorLight),
]

OUTPUTS = [
    ("01-画质与输出-background_color", ["bg_dark", "bg_light"]),
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
