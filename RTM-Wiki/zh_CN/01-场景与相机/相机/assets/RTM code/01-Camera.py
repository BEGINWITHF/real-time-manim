# -*- coding: utf-8 -*-
"""01-Camera.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-Camera.py <片段名>...
不带参数就渲染全部 3 个场景，并拼出页面里的三条视频。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FRAG = os.path.join(HERE, "final",
                       os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(FRAG, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    BLUE, RED, WHITE, YELLOW,
    DOWN, LEFT, RIGHT, UP,
    Circle, FadeIn, Scene, Square, Text,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：background_color / background_opacity ========================
class BackgroundDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        sq = Square(color=BLUE).set_fill(BLUE, 0.8)   #一个蓝色方块当参照物
        cap = Text("default background", font_size=32, color=YELLOW).to_edge(UP)   #顶部说明
        self.add(sq, cap)   #把方块和说明放进场景
        win.play(FadeIn(sq), run_time=0.5)   #方块淡入：此刻还是默认的黑背景
        win.play(Wait(0.4))   #停 0.4s
        self.camera.background_color = "#1E3A5F"   #改背景色：赋值立即生效
        cap.become(Text("background_color = '#1E3A5F'", font_size=32, color=YELLOW).to_edge(UP))   #说明文字换成背景色
        win.play(Wait(0.8))   #停 0.8s 看清深蓝背景
        self.camera.background_opacity = 0.6   #改背景不透明度：可读可写
        info = Text("background_opacity = 0.6 (video unchanged)", font_size=26, color=WHITE).next_to(cap, DOWN)   #读回透明度：出片是不透明的 MP4
        self.add(info)   #把读数放进场景
        win.play(Wait(0.8))   #停 0.8s：画面不会变淡
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：is_in_frame ==================================================
class IsInFrameDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        near = Square(color=BLUE).set_fill(BLUE, 0.8)   #画面正中的方块：在取景框内
        far = Circle(radius=0.8, color=RED).shift(RIGHT * 10)   #远处的圆：在取景框外
        cap = Text("camera.is_in_frame(mobject) -> bool", font_size=30, color=YELLOW).to_edge(UP)   #顶部说明
        info = Text("square=%s  circle=%s" % (self.camera.is_in_frame(near), self.camera.is_in_frame(far)),
                    font_size=28, color=WHITE).next_to(cap, DOWN)   #第一组读数：方块 True、圆 False
        self.add(near, far, cap, info)   #把四个对象放进场景
        win.play(FadeIn(near), run_time=0.5)   #方块淡入
        win.play(Wait(0.5))   #停 0.5s
        win.play(near.animate.shift(RIGHT * 8.5), run_time=0.8)   #把方块推出取景框
        info.become(Text("after move: square=%s" % self.camera.is_in_frame(near),
                    font_size=28, color=WHITE).next_to(cap, DOWN))   #第二组读数：方块变 False
        win.play(Wait(0.8))   #停 0.8s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：use_z_index ==================================================
class UseZIndexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        a = Square(color=BLUE).set_fill(BLUE, 0.9).shift(LEFT * 0.4)   #蓝色方块：先加进场景
        a.z_index = 1   #z 序高：use_z_index=True 时画在上面
        b = Square(color=RED).set_fill(RED, 0.9).shift(RIGHT * 0.4)   #红色方块：后加进场景
        b.z_index = 0   #z 序低：只按添加顺序绘制时反而在上面
        cap = Text("use_z_index=True", font_size=32, color=YELLOW).to_edge(UP)   #顶部说明
        self.add(a, b, cap)   #先 a 后 b 放进场景
        win.play(Wait(1.0))   #停 1.0s：蓝色在上（按 z_index 排序绘制）
        self.camera.use_z_index = False   #关掉 z 序：改成按添加顺序绘制
        cap.become(Text("use_z_index=False", font_size=32, color=YELLOW).to_edge(UP))   #说明文字跟着换
        win.play(Wait(1.0))   #停 1.0s：红色在上（后加的画在上面）
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("01-Camera-background_1", BackgroundDemo),
    ("01-Camera-is_in_frame_1", IsInFrameDemo),
    ("01-Camera-use_z_index_1", UseZIndexDemo),
]

PAIRS = [
    ("01-Camera-background", ["01-Camera-background_1"]),
    ("01-Camera-is_in_frame", ["01-Camera-is_in_frame_1"]),
    ("01-Camera-use_z_index", ["01-Camera-use_z_index_1"]),
]


def concat(names, dst):
    lst = os.path.join(HERE, "concat-01-Camera.txt")
    with open(lst, "w", encoding="utf-8") as fh:
        for n in names:
            fh.write("file '%s'\n" % os.path.join(FRAG, n + ".mp4"))
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
            fast_record_scene(cls, out_path=os.path.join(FRAG, name + ".mp4"),
                              verbose=True)
        except Exception:
            import traceback
            traceback.print_exc()

    if not only:
        for out_name, names in PAIRS:
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
