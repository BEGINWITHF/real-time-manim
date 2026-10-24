# -*- coding: utf-8 -*-
"""04-分段字幕与声音.md 唯一能出片的样例（Scene.add_sound）完整源码。

跑法：python 04-分段字幕与声音.py
出片后 MP4 自带混流音轨（RTM 录制时由 audio_track hook 捕获 add_sound）。
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import Scene, Circle, ORANGE, Create, Indicate
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Scene.add_sound ===========================================
class AddSoundDemo(Scene):
    GAIN = 6.0   #音量增益（dB）：改成 0 听原音量，改成 -6 听更轻

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 场景，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接上
        beep = os.path.join(os.path.dirname(os.path.abspath(__file__)), "beep.wav")   #演示用的“哔”声
        self.add_sound(beep, time_offset=0.5, gain=self.GAIN)   #开场 0.5s 后“哔”一声（加大音量）
        dot = Circle(radius=0.9, color=ORANGE)   #一个圆
        self.add(dot)   #圆上屏
        win.play(Create(dot), run_time=1.0)   #用 1.0s 画出这个圆
        self.add_sound(beep, time_offset=0, gain=0)   #此刻（第 1.0s）再“哔”一声，不加增益作对照
        win.play(Indicate(dot), run_time=0.6)   #圆圈放大强调一下，给第二个声音打节拍
        win.play(Wait(0.6))   #进行 0.6s 的等待，留出声音的尾巴
        win.close()   #关闭 RTM 窗口


PAGE = "04-分段字幕与声音"

SCENES = [
    ("sound", AddSoundDemo),
]

SAMPLES = [
    ("sound", ["sound"]),
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
        for out_name, names in SAMPLES:
            dst = os.path.join(ASSETS, "RTM output", "%s-%s.mp4" % (PAGE, out_name))
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
            if len(names) > 1:
                #多片段样例：每个片段也拷进 assets/，方便逐段对照
                for n in names:
                    shutil.copyfile(os.path.join(OUT, n + ".mp4"),
                                    os.path.join(ASSETS, "%s-%s.mp4" % (PAGE, n)))
