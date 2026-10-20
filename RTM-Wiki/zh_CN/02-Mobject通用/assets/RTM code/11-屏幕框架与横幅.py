# -*- coding: utf-8 -*-
"""11-屏幕框架与横幅.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 11-屏幕框架与横幅.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的三条样例视频（输出到上一级 assets/）。
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

from real_time_manim import (
    Scene, Square, Text, ScreenRectangle, FullScreenRectangle, ManimBanner,
    BLUE, GREEN, WHITE, BLACK, UP, DOWN, LEFT, RIGHT, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：ScreenRectangle ===========================================
class ScreenRectDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        s1 = ScreenRectangle(height=2.6, color=BLUE)   #按 16:9 生成的示意屏幕
        s1.shift(LEFT * 3.4)   #放左边
        s2 = ScreenRectangle(height=2.6, color=GREEN).next_to(s1, RIGHT, buff=0.5)   #右边一个对照
        self.add(s1, s2)   #进场景
        print("s1 宽高 =", round(s1.width, 2), round(s1.height, 2))   #16:9
        win.play(FadeIn(s1), FadeIn(s2), run_time=0.5)   #淡入
        s2.aspect_ratio = 1.0   #特有可读写属性：变正方形，高度不变（瞬间生效）
        print("改后 s2 =", round(s2.aspect_ratio, 2), round(s2.width, 2), round(s2.height, 2))   #1.0 2.6 2.6
        win.play(Wait(0.5))   #停一下看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：FullScreenRectangle =======================================
class FullScreenDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        txt = Text("SCENE", font_size=48, color=WHITE)   #白字
        sq = Square(color=BLUE, side_length=1.5).shift(DOWN * 1.5)   #蓝方块
        self.add(txt, sq)   #进场景
        win.play(FadeIn(txt), FadeIn(sq), run_time=0.4)   #内容淡入
        mask = FullScreenRectangle(fill_opacity=0.7, color=BLACK)   #铺满整个画面的变暗遮罩
        self.add(mask)   #进场景
        win.play(FadeIn(mask), run_time=0.5)   #遮罩淡入：画面整体变暗
        win.play(Wait(0.4))   #停一下看遮罩效果
        self.remove(mask)   #摘掉遮罩
        win.play(Wait(0.3))   #进行 0.3s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：ManimBanner ===============================================
class BannerDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        banner = ManimBanner(dark_theme=True)   #深色主题横幅
        banner.scale(0.8)   #必须用覆写的 scale：会同步缩放尚未挂载的字母组
        banner.to_edge(DOWN, buff=0.8)   #放到下方
        print("font_color =", banner.font_color, "| scale_factor =", banner.scale_factor)   #常用属性
        self.add(banner)   #进场景
        win.play(banner.create(run_time=1.2))   #logo 图形旋转飞入 + 字母 M 淡入
        win.play(banner.expand(run_time=1.0, direction="center"))   #展开成完整 “manim” 横幅
        try:
            banner.expand(direction="up")   #非法 direction 抛 ValueError
        except ValueError as exc:
            print("expand 非法 direction ->", str(exc)[:50])
        print("anim 属性 =", getattr(banner, "anim", None) is not None)   #展开后才挂上 anim
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("screen_rect", ScreenRectDemo),
    ("fullscreen", FullScreenDemo),
    ("banner", BannerDemo),
]

PAIRS = [
    ("screen_rect", ["screen_rect"]),
    ("fullscreen", ["fullscreen"]),
    ("banner", ["banner"]),
]

PAGE = "11-屏幕框架与横幅"


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
