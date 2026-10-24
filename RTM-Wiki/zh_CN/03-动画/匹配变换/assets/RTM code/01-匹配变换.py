# -*- coding: utf-8 -*-
"""01-匹配变换.md 四个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-匹配变换.py <片段名>...
不带参数就渲染全部片段，并拼出页面里的四条样例视频（输出到上一级 assets/）。
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
    GREY_B,
    YELLOW,
    DOWN,
    LEFT,
    UP,
    PI,
    FadeIn,
    FadeOut,
    MathTex,
    Scene,
    Text,
    VGroup,
    Write,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    TransformMatchingShapes,
    TransformMatchingTex,
    Wait,
)
from real_time_manim.record import fast_record_scene


# ===== 样例 1：Shapes 默认同形匹配 ==========================================
class ShapesDefaultDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-ShapesDefault", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l1 = Text("TransformMatchingShapes(src, tar, transform_mismatches=False,",
                  font_size=28, color=GREY_B)
        l2 = Text("    fade_transform_mismatches=False, key_map=None, path_arc=PI/2)",
                  font_size=28, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #两行签名标签
        src = Text("the morse code", font_size=44).next_to(lab1, DOWN, buff=0.8)   #源：待重排的句子
        tar = Text("here come dots", font_size=44).move_to(src)   #目标：重排后的句子
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   #标签从下方淡入
        self.add(src)   #源对象先加进场景（播完会被移除，目标接管）
        win.play(
            TransformMatchingShapes(                #参数 “mobject”（源，播完移除）
                src,
                tar,                                #参数 “target_mobject”（播完接管场景）
                transform_mismatches=False,         #参数 “transform_mismatches”：False，异形走淡出淡入
                fade_transform_mismatches=False,    #参数 “fade_transform_mismatches”：False
                key_map=None,                       #参数 “key_map”：None，不手工配对
                path_arc=PI / 2,                    #参数 “path_arc”（**kwargs）：同形零件走弧线
            ),
            run_time=2.6,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：transform_mismatches=True 强行变形 ===========================
class ShapesMismatchDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-ShapesMismatch", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l3 = Text("TransformMatchingShapes(src, tar, transform_mismatches=True, ...)",
                  font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)   #签名标签
        src2 = Text("the morse code", font_size=44).next_to(l3, DOWN, buff=0.8)   #源：待重排的句子
        tar2 = Text("here come dots", font_size=44).move_to(src2)   #目标：重排后的句子
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)   #标签从下方淡入
        self.add(src2)   #源对象先加进场景（播完会被移除，目标接管）
        win.play(
            TransformMatchingShapes(                #参数 “mobject”（源，播完移除）
                src2,
                tar2,                               #参数 “target_mobject”（播完接管场景）
                transform_mismatches=True,          #参数 “transform_mismatches”：True，异形也强行变形
                fade_transform_mismatches=False,    #参数 “fade_transform_mismatches”：False
                key_map=None,                       #参数 “key_map”：None，不手工配对
                path_arc=PI / 2,                    #参数 “path_arc”（**kwargs）：同形零件走弧线
            ),
            run_time=2.4,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：key_map 手工键配对 ===========================================
class ShapesKeyMapDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-ShapesKeyMap", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l4 = Text("key_map = {shape_key('c'): shape_key('h')}  # 手工键配对",
                  font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)   #签名标签
        l5 = Text("TransformMatchingShapes(cat, hat, key_map=key_map, ...)",
                  font_size=28, color=GREY_B).next_to(l4, DOWN, buff=0.06)   #第二行签名标签
        lab2 = VGroup(l4, l5)
        src3 = Text("cat", font_size=52, color=GREY_B).next_to(lab2, DOWN, buff=0.8).shift(LEFT * 2.0)   #源单词 cat
        tar3 = Text("hat", font_size=52, color=GREY_B).move_to(src3)   #目标单词 hat（只换首字母）
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)   #标签从下方淡入
        self.add(src3)   #源对象先加进场景（播完会被移除，目标接管）
        key_map = {
            TransformMatchingShapes.get_mobject_key(src3[0]):   #源字母 “c” 的形状键
            TransformMatchingShapes.get_mobject_key(tar3[0]),   #目标字母 “h” 的形状键
        }
        win.play(
            TransformMatchingShapes(                #参数 “mobject”（源，播完移除）
                src3,
                tar3,                               #参数 “target_mobject”（播完接管场景）
                transform_mismatches=False,         #参数 “transform_mismatches”：False
                fade_transform_mismatches=False,    #参数 “fade_transform_mismatches”：False
                key_map=key_map,                    #参数 “key_map”（“c” → “h” 强制配对）
                path_arc=PI / 2,                    #参数 “path_arc”（**kwargs）：同形零件走弧线
            ),
            run_time=2.4,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：TransformMatchingTex fade 与默认对照 =========================
class MatchingTexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-MatchingTex", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        l6 = Text("TransformMatchingTex(eq1, eq2, transform_mismatches=False,",
                  font_size=28, color=GREY_B)
        l7 = Text("    fade_transform_mismatches=True, key_map=None)",
                  font_size=28, color=GREY_B)
        lab3 = VGroup(l6, l7).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   #两行签名标签
        eq1 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2").next_to(lab3, DOWN, buff=0.8)   #源公式 x²+y²=z²
        eq2 = MathTex("{{x}}^2", "=", "{{z}}^2", "-", "{{y}}^2").move_to(eq1)   #目标公式 x²=z²−y²
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)   #标签从下方淡入
        self.add(eq1)   #源公式先加进场景（播完会被移除，目标接管）
        win.play(
            TransformMatchingTex(                  #参数 “mobject”（源，播完移除）
                eq1,
                eq2,                                #参数 “target_mobject”（播完接管场景）
                transform_mismatches=False,         #参数 “transform_mismatches”：False
                fade_transform_mismatches=True,     #参数 “fade_transform_mismatches”：True，异形用 FadeTransformPieces
                key_map=None,                       #参数 “key_map”：None，不手工配对
            ),
            run_time=2.4,
        )
        # 同一变换的默认行为对照：异形零件直接淡出/淡入
        eq3 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2").move_to(eq1)   #对照：源公式换回
        eq4 = MathTex("{{x}}^2", "=", "{{z}}^2", "-", "{{y}}^2").move_to(eq1)   #对照：同一目标公式
        l8 = Text("(default) transform_mismatches=False, fade_transform_mismatches=False",
                  font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)   #对照标签
        win.play(FadeOut(VGroup(lab3, eq2)), FadeIn(l8, shift=DOWN), run_time=0.5)   #换标签，结果让位
        self.add(eq3)   #对照的源公式加进场景
        win.play(
            TransformMatchingTex(                  #参数 “mobject”（源，播完移除）
                eq3,
                eq4,                                #参数 “target_mobject”（播完接管场景）
                transform_mismatches=False,         #参数 “transform_mismatches”：False
                fade_transform_mismatches=False,    #参数 “fade_transform_mismatches”：False，异形直接淡出淡入
                key_map=None,                       #参数 “key_map”：None，不手工配对
            ),
            run_time=2.4,
        )
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("shapes_default", ShapesDefaultDemo),
    ("shapes_mismatch", ShapesMismatchDemo),
    ("shapes_keymap", ShapesKeyMapDemo),
    ("tex", MatchingTexDemo),
]

PAIRS = [
    ("shapes_default", ["shapes_default"]),
    ("shapes_mismatch", ["shapes_mismatch"]),
    ("shapes_keymap", ["shapes_keymap"]),
    ("tex", ["tex"]),
]

PAGE = "01-匹配变换"


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
