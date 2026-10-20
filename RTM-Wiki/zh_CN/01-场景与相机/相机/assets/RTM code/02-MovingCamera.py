# -*- coding: utf-8 -*-
"""02-MovingCamera.md 两个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02-MovingCamera.py <片段名>...
不带参数就渲染全部 5 个场景，并拼出页面里的两条视频。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FRAG = os.path.join(HERE, "final",
                       os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(FRAG, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    BLUE, RED, WHITE, YELLOW,
    DOWN, LEFT, RIGHT, UP,
    Circle, Dot, FadeIn, MovingCameraScene, Square, Text, VGroup,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：frame_height / frame_width / frame_center ====================
class FrameScaleDemo(MovingCameraScene):
    HEIGHT = 4.0   #想看到的画面高度：改成 2.0 再跑一次，画面放大到 4 倍

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        cam = self.camera   #MovingCameraScene 自带的可移动相机
        a = Square(color=BLUE).set_stroke(width=4).shift(LEFT * 2.5)   #左边的目标
        b = Square(color=RED).set_stroke(width=4).shift(RIGHT * 2.5)   #右边的目标
        info = Text("frame: %.2f x %.2f" % (cam.frame_height, cam.frame_width),
                    font_size=28, color=WHITE).move_to(UP * 1.6)   #取景框的高和宽（放在画面里侧：推近后贴边会出画）
        self.add(a, b, info)   #把两个方块和读数放进场景
        win.play(FadeIn(a, b), run_time=0.5)   #两个方块淡入：此刻还是默认画幅
        win.play(Wait(0.4))   #停 0.4s
        cam.frame_height = self.HEIGHT   #改高度
        cam.frame_width = self.HEIGHT * 16 / 9   #宽度按 16:9 跟着改：成对赋值才是等比缩放
        info.become(Text("frame: %.2f x %.2f" % (cam.frame_height, cam.frame_width),
                    font_size=28, color=WHITE).move_to(UP * 1.6))   #读数刷新
        win.play(Wait(1.0))   #停 1.0s 看清放大后的画面
        win.close()   #关闭 RTM 窗口


class FrameCenterDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        cam = self.camera   #MovingCameraScene 自带的可移动相机
        a = Square(color=BLUE).set_stroke(width=4).shift(LEFT * 4)   #左边的目标
        b = Square(color=RED).set_stroke(width=4).shift(RIGHT * 4)   #右边的目标
        info = Text("frame_center = ORIGIN", font_size=28, color=WHITE).to_edge(UP)   #取景框中心
        self.add(a, b, info)   #把两个方块和读数放进场景
        win.play(FadeIn(a, b), run_time=0.5)   #两个方块淡入
        win.play(Wait(0.4))   #停 0.4s
        cam.frame_center = b   #把取景框中心挪到红方块上（也接受坐标数组）
        info.become(Text("frame_center = red square", font_size=28, color=WHITE).to_edge(UP))   #读数刷新
        win.play(Wait(1.0))   #停 1.0s：镜头摇到右边
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：auto_zoom ====================================================
class AutoZoomAnimDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        cam = self.camera   #MovingCameraScene 自带的可移动相机
        group = VGroup(
            Square(color=BLUE).set_stroke(width=4).shift(LEFT * 2.5),   #左边的方块
            Circle(color=RED).set_stroke(width=4).shift(RIGHT * 2.5),   #右边的圆
            Dot(color=YELLOW).shift(DOWN * 2),   #下方的小点
        )   #三个对象一组
        self.add(group)   #把三个对象放进场景
        win.play(cam.auto_zoom(group, margin=0.5), run_time=1.0)   #带动画地推近，恰好框住三个对象
        win.play(Wait(0.6))   #停 0.6s
        win.close()   #关闭 RTM 窗口


class AutoZoomNoAnimDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        cam = self.camera   #MovingCameraScene 自带的可移动相机
        group = VGroup(
            Square(color=BLUE).set_stroke(width=4).shift(LEFT * 2.5),   #左边的方块
            Circle(color=RED).set_stroke(width=4).shift(RIGHT * 2.5),   #右边的圆
            Dot(color=YELLOW).shift(DOWN * 2),   #下方的小点
        )   #三个对象一组
        self.add(group)   #把三个对象放进场景
        cam.auto_zoom(group, margin=0.5, animate=False)   #animate=False：立即生效，画面直接跳过去
        win.play(Wait(1.0))   #停 1.0s
        win.close()   #关闭 RTM 窗口


class AutoZoomOnlyDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        cam = self.camera   #MovingCameraScene 自带的可移动相机
        sq = Square(color=BLUE).set_stroke(width=4).shift(LEFT * 5)   #很靠左的方块
        circ = Circle(color=RED).set_stroke(width=4).shift(RIGHT * 2.5)   #右边的圆
        self.add(sq, circ)   #把方块和圆放进场景
        win.play(cam.auto_zoom(circ, margin=0.4), run_time=0.8)   #先推近圆圈：方块出画
        win.play(cam.auto_zoom([circ, sq], margin=0.4, only_mobjects_in_frame=True), run_time=0.8)   #方块在画面外，被忽略：镜头不动
        win.play(Wait(0.5))   #停 0.5s
        win.play(cam.auto_zoom([circ, sq], margin=0.4), run_time=0.8)   #不加限制：方块也算上，镜头拉远
        win.play(Wait(0.5))   #停 0.5s 收工
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("02-MovingCamera-frame_scale_1", FrameScaleDemo),
    ("02-MovingCamera-frame_center_1", FrameCenterDemo),
    ("02-MovingCamera-auto_zoom_anim_1", AutoZoomAnimDemo),
    ("02-MovingCamera-auto_zoom_noanim_1", AutoZoomNoAnimDemo),
    ("02-MovingCamera-auto_zoom_only_1", AutoZoomOnlyDemo),
]

PAIRS = [
    ("02-MovingCamera-frame_props", ["02-MovingCamera-frame_scale_1", "02-MovingCamera-frame_center_1"]),
    ("02-MovingCamera-auto_zoom", ["02-MovingCamera-auto_zoom_anim_1", "02-MovingCamera-auto_zoom_noanim_1",
                                   "02-MovingCamera-auto_zoom_only_1"]),
]


def concat(names, dst):
    lst = os.path.join(HERE, "concat-02-MovingCamera.txt")
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
