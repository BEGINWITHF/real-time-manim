# -*- coding: utf-8 -*-
"""03-ZoomedScene.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 03-ZoomedScene.py <场景名>...
不带参数就渲染全部 5 个场景，并拼出页面里的两条对比视频（zoom / activate）。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    GREEN, RED, YELLOW, UP, DOWN, LEFT, RIGHT, Dot, Text, VGroup,
    ZoomedScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def make_target():   #一个“小而密”的目标：字小、点也小，不放大看不清
    return VGroup(
        Text("RTM", font_size=22, color=YELLOW),   #很小的标题字
        Dot(radius=0.04, color=GREEN),              #两个小圆点
        Dot(radius=0.04, color=RED).shift(RIGHT * 0.18),
    ).arrange(DOWN, buff=0.1).shift(LEFT * 2 + DOWN * 0.8)   #摆到画面左下偏中的位置


# ===== 样例 1：ZoomedScene 构造参数 =========================================
class ZoomBase(ZoomedScene):
    LABEL = ""   #子类填本段的标题文字
    KW = {}      #子类填要传给 ZoomedScene.__init__ 的构造参数

    def __init__(self, **kwargs):
        super().__init__(**self.KW, **kwargs)   #把 “KW” 里的键传给 ZoomedScene.__init__

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        target = make_target()   #要放大的小目标
        self.add(target)   #放进场景（这时小得看不清）
        cap = Text(self.LABEL, font_size=28, color=YELLOW).to_edge(UP)   #顶部标题显示当前构造参数
        self.add(cap)   #放进场景（2D 场景里文字默认就钉在屏幕上）
        self.activate_zooming(animate=False)   #开启放大：小窗瞬间出现，不播动画
        self.zoomed_camera.frame.move_to(target)   #把放大镜的取景框套到目标上
        win.play(Wait(0.8))   #停 0.8s 看放大结果
        win.play(target.animate.shift(RIGHT * 1.2), run_time=1.2)   #目标右移，滑出取景框
        win.play(self.zoomed_camera.frame.animate.move_to(target), run_time=0.8)   #取景框再追过去
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


class ZoomA(ZoomBase):
    LABEL = "zoom_factor=0.15 display 3x3 corner=UP+RIGHT"   #默认一档：框 15% 大小
    KW = {"zoom_factor": 0.15,
          "zoomed_display_height": 3, "zoomed_display_width": 3,
          "zoomed_display_corner": UP + RIGHT}


class ZoomB(ZoomBase):
    LABEL = "zoom_factor=0.08 display 4x2.5 corner=DOWN+LEFT"   #更狠的一档：框 8% = 放大约 12 倍
    KW = {"zoom_factor": 0.08,
          "zoomed_display_height": 2.5, "zoomed_display_width": 4,
          "zoomed_display_corner": DOWN + LEFT, "zoomed_display_corner_buff": 0.3}


# ===== 样例 2：activate_zooming(animate) ===================================
class ZoomActivateBase(ZoomedScene):
    ANIMATE = False   #子类改 True，看小窗的入场动画
    LABEL = ""        #子类填本段的标题文字

    def __init__(self, **kwargs):
        super().__init__(zoom_factor=0.15, **kwargs)   #两个类共用同一 zoom_factor，只比 animate

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #animate=True 时 activate_zooming 内部会调 self.play，先接到窗口上
        target = make_target()   #要放大的小目标
        self.add(target)   #放进场景
        cap = Text(self.LABEL, font_size=28, color=YELLOW).to_edge(UP)   #顶部标题显示 animate 取值
        self.add(cap)   #放进场景
        self.activate_zooming(animate=self.ANIMATE)   #False=小窗瞬间出现；True=先“推进镜头”再让小窗弹出
        self.zoomed_camera.frame.move_to(target)   #把放大镜的取景框套到目标上
        win.play(Wait(0.8))   #停 0.8s 看放大结果
        win.close()   #关闭 RTM 窗口


class ZoomNoAnim(ZoomActivateBase):
    ANIMATE = False   #小窗直接出现
    LABEL = "activate_zooming(animate=False)"


class ZoomAnim(ZoomActivateBase):
    ANIMATE = True   #播放入场动画
    LABEL = "activate_zooming(animate=True)"


# ===== 样例 3：get_zoom_in_animation / pop_out / get_zoom_factor ===========
class ManualZoomDemo(ZoomedScene):
    def __init__(self, **kwargs):
        super().__init__(zoom_factor=0.15, **kwargs)   #默认 0.15 一档

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #下面手动编排的动画全走 win.play
        target = make_target()   #要放大的小目标
        self.add(target)   #放进场景

        #手动完成 activate_zooming(animate=True) 的三步，节奏自己编排：
        self.renderer.camera.add_image_mobject_from_camera(self.zoomed_display)   #① 把小窗注册进主相机
        win.play(self.get_zoom_in_animation(run_time=1.2))   #② “镜头推进”：取景框从全屏缩回放大尺寸
        win.play(self.get_zoomed_display_pop_out_animation(run_time=0.8))   #③ “小窗弹出”：从小窗位置展开
        self.add_foreground_mobjects(self.zoomed_camera.frame, self.zoomed_display)   #把取景框和小窗盖到最上层

        ratio = self.get_zoom_factor()   #缩放比 = 放大取景框高度 / 小窗高度
        print("get_zoom_factor() =", ratio)   #把缩放比打到控制台
        cap = Text("get_zoom_factor() = %.2f" % ratio,   #顶部也显示一份
                   font_size=28, color=YELLOW).to_edge(UP)
        self.add(cap)   #放进场景
        self.zoomed_camera.frame.move_to(target)   #把放大镜的取景框套到目标上
        win.play(Wait(0.8))   #停 0.8s 看放大结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("zoom_a", ZoomA),
    ("zoom_b", ZoomB),
    ("noanim", ZoomNoAnim),
    ("anim", ZoomAnim),
    ("manual", ManualZoomDemo),
]

PAIRS = [
    ("03-ZoomedScene-zoom", ["zoom_a", "zoom_b"]),
    ("03-ZoomedScene-activate", ["noanim", "anim"]),
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

    for out_name, names in PAIRS:
        dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
        concat(names, dst)
        print("concat ->", dst, os.path.getsize(dst), "bytes")

    import shutil   #单段样例也要发布成页面成片：<页名>-<片段名>.mp4
    PAGE = os.path.splitext(os.path.basename(__file__))[0]
    used = {n for _, names in PAIRS for n in names}
    for name, _ in SCENES:
        if name in used or (only and name not in only):
            continue
        src = os.path.join(OUT, name + ".mp4")
        if os.path.exists(src):
            shutil.copy(src, os.path.join(HERE, "..", PAGE + "-" + name + ".mp4"))
            print("publish ->", PAGE + "-" + name + ".mp4")
