# -*- coding: utf-8 -*-
"""09b-片段方法与列表.md 七个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 09b-片段方法与列表.py <样例名>...
不带参数就渲染全部样例，并拼出页面里的七条样例视频（输出到 assets/RTM output/）。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5)))

from real_time_manim import (
    Scene, MathTex, BulletedList, Title, Text, Rectangle, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write, MED_LARGE_BUFF,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：set_color_by_tex —— 给某一片段上色 ==========================
class ColorByTexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09b-set_color_by_tex", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 同一个公式，三段各染一次（每次只给一个 “tex / color” 组合）——
        pairs = [("x", RED), ("y", GREEN), ("z", BLUE)]   #参数 “tex / color”
        for i, (tex, col) in enumerate(pairs):
            eq = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=52)
            eq.set_color_by_tex(tex, col)   #参数 “tex=片段文本 / color=目标颜色”
            eq.move_to([-4.2 + i * 4.2, 0.9, 0])
            cap = Text('set_color_by_tex("%s")' % tex, font_size=18, color=GREY_B).next_to(eq, DOWN, buff=0.4)
            win.play(Write(eq), FadeIn(cap), run_time=0.6)   #依次染红 x、绿 y、蓝 z

        # —— 一个片段在不同公式里可以染不同颜色 ——
        eq2 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=52)
        eq2.set_color_by_tex("x", ORANGE)   #同一个 “x”，这次染橙色
        eq2.set_color_by_tex("z", PURPLE)   #再来一次，染紫色
        eq2.move_to([-1.6, -1.7, 0])
        cap2 = Text('x->ORANGE  z->PURPLE', font_size=18, color=GREY_B).next_to(eq2, DOWN, buff=0.35)
        win.play(Write(eq2), FadeIn(cap2), run_time=0.6)   #链式调用两次
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：set_color_by_tex_to_color_map —— 一次染多片 =================
class ColorMapDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09b-set_color_by_tex_to_color_map", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 方法形式：一次传一个字典 ——
        eq = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=72)
        eq.set_color_by_tex_to_color_map({"x": RED, "y": GREEN, "z": BLUE})   #参数 “texs_to_color_map”
        eq.move_to([0, 0.9, 0])
        cap = Text("set_color_by_tex_to_color_map({...})", font_size=18, color=GREY_B).next_to(eq, DOWN, buff=0.4)
        win.play(Write(eq), FadeIn(cap), run_time=0.6)   #一次染三片

        # —— 构造参数形式：完全等价，写进 MathTex(...) 即可 ——
        eq2 = MathTex("{{a}}^2", "+", "{{b}}^2", "=", "{{c}}^2", font_size=72,
                      tex_to_color_map={"a": ORANGE, "b": TEAL, "c": PURPLE})   #参数 “tex_to_color_map”
        eq2.move_to([0, -1.7, 0])
        cap2 = Text("MathTex(..., tex_to_color_map={...})", font_size=18, color=GREY_B).next_to(eq2, DOWN, buff=0.35)
        win.play(Write(eq2), FadeIn(cap2), run_time=0.6)   #构造时就上好色
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：get_part_by_tex —— 取出某一片段 =============================
class GetPartDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09b-get_part_by_tex", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 取出的子对象可以单独加动画（这里套一个框）——
        eq = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=72).move_to([0, 0.9, 0])
        part = eq.get_part_by_tex("y")   #参数 “tex=片段文本”
        box = Rectangle(width=part.width + 0.3, height=part.height + 0.3,
                        color=YELLOW).move_to(part.get_center())   #只框住 “y”
        win.play(Write(eq), run_time=0.6)   #先写公式
        win.play(Create(box), run_time=0.5)   #框住取出来的那一片

        # —— 取出的片段也能单独移动 ——
        eq2 = MathTex("{{a}}", "+", "{{b}}", "=", "{{c}}", font_size=72).move_to([0, -1.7, 0])
        part2 = eq2.get_part_by_tex("b")
        win.play(Write(eq2), run_time=0.6)
        win.play(part2.animate.shift(UP * 1.2), run_time=0.6)   #把 “b” 单独抬起来
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：set_opacity_by_tex —— 高亮主角、压暗其他 ====================
class OpacityByTexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09b-set_opacity_by_tex", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— opacity 默认 0.5；不传 remaining_opacity 时其余部分不动 ——
        eq = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=72)
        eq.set_opacity_by_tex("y")   #参数只给 “tex”：默认 opacity=0.5
        eq.move_to([-2.2, 0.9, 0])
        cap = Text("set_opacity_by_tex('y')", font_size=18, color=GREY_B).next_to(eq, DOWN, buff=0.4)
        win.play(Write(eq), FadeIn(cap), run_time=0.6)

        # —— opacity 显式 + remaining_opacity：主角亮、其余更暗 ——
        eq2 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=72)
        eq2.set_opacity_by_tex("y", opacity=1.0, remaining_opacity=0.25)   #参数 “opacity / remaining_opacity”
        eq2.move_to([2.2, 0.9, 0])
        cap2 = Text("opacity=1.0 remaining=0.25", font_size=18, color=GREY_B).next_to(eq2, DOWN, buff=0.4)
        win.play(Write(eq2), FadeIn(cap2), run_time=0.6)

        # —— 同一个公式上两次调用：可以依次高亮不同片段 ——
        eq3 = MathTex("{{a}}", "+", "{{b}}", "=", "{{c}}", font_size=72)
        eq3.set_opacity_by_tex("b", opacity=1.0, remaining_opacity=0.3)
        eq3.move_to([0, -1.7, 0])
        cap3 = Text("highlight 'b'", font_size=18, color=GREY_B).next_to(eq3, DOWN, buff=0.35)
        win.play(Write(eq3), FadeIn(cap3), run_time=0.6)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：MathTexPart —— 遍历片段读 tex_string ========================
class PartsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09b-MathTexPart", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— 遍历子对象：每个 MathTexPart 都带着自己的 .tex_string ——
        eq = MathTex(r"{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2", font_size=64)
        eq.move_to([0, 1.4, 0])
        win.play(Write(eq), run_time=0.8)   #先写公式

        labels = VGroup()   #把每片的 tex_string 依次打在下方
        for i, part in enumerate(eq.submobjects):
            txt = getattr(part, "tex_string", "(no tex_string)")   #属性 “tex_string”
            labels.add(Text("%d: %s" % (i, txt), font_size=18, color=GREY_B))
        labels.arrange(DOWN, buff=0.08).next_to(eq, DOWN, buff=0.35)
        win.play(FadeIn(labels), run_time=0.6)   #逐片列出片段文本
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 6：BulletedList —— 项目符号列表 ================================
class BulletedListDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("09b-BulletedList", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题

        # —— buff 用默认值，dot_scale_factor 用默认 2 ——
        bl = BulletedList("first item", "second item", "third item",
                          font_size=40)   #参数 “*items”
        bl.move_to([-3.2, 0.9, 0])
        win.play(Write(bl), run_time=0.7)   #默认间距与点号大小

        # —— buff 收紧 + dot_scale_factor 放大 ——
        bl2 = BulletedList("tight", "spacing", "list", font_size=40,
                           buff=MED_LARGE_BUFF * 0.3,   #参数 “buff”：条目间距
                           dot_scale_factor=4)   #参数 “dot_scale_factor”：点号放大
        bl2.move_to([2.6, 0.9, 0])
        cap2 = Text("buff=0.3x  dot_scale_factor=4", font_size=18, color=GREY_B).next_to(bl2, DOWN, buff=0.4)
        win.play(Write(bl2), FadeIn(cap2), run_time=0.7)

        # —— fade_all_but：按“下标”压暗除某条以外的所有条目 ——
        bl3 = BulletedList("alpha", "beta", "gamma", font_size=40).move_to([-1.6, -1.6, 0])
        win.play(Write(bl3), run_time=0.6)
        bl3.fade_all_but(1, opacity=0.25)   #参数 “index_or_string=1”：只有第 1 条保持原样
        win.play(FadeIn(Text("fade_all_but(1, opacity=0.25)",
                             font_size=18, color=GREY_B).next_to(bl3, DOWN, buff=0.3)),
                 run_time=0.4)
        bl3.fade_all_but(2, opacity=0.25)   #参数换成 2：改成压暗第 0、1 条
        win.play(FadeIn(Text("fade_all_but(2, opacity=0.25)",
                             font_size=18, color=GREY_B).next_to(bl3, DOWN, buff=0.05)),
                 run_time=0.4)
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 7：Title —— 页眉标题与下划线 ===================================
class TitleDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口

        # —— 默认：自带一条与屏幕等宽的下划线 ——
        t1 = Title("Chapter 1")   #参数 “*text_parts”
        win.play(Write(t1), run_time=0.6)   #默认下划线铺满屏幕宽
        win.play(FadeOut(t1), run_time=0.3)

        # —— match_underline_width_to_text：下划线只跟文字一样宽 ——
        t2 = Title("Chapter 2", match_underline_width_to_text=True)   #参数 “match_underline_width_to_text=True”
        win.play(Write(t2), run_time=0.6)
        win.play(FadeOut(t2), run_time=0.3)

        # —— include_underline=False：完全不要下划线 ——
        t3 = Title("Chapter 3", include_underline=False)   #参数 “include_underline=False”
        win.play(Write(t3), run_time=0.6)
        win.play(FadeOut(t3), run_time=0.3)

        # —— underline_buff：下划线与文字的间距 ——
        t4 = Title("Chapter 4", match_underline_width_to_text=True,
                   underline_buff=0.55)   #参数 “underline_buff=0.55”（默认 MED_SMALL_BUFF）
        win.play(Write(t4), run_time=0.8)   #下划线明显离文字更远
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("colorbytex", ColorByTexDemo),
    ("colormap", ColorMapDemo),
    ("getpart", GetPartDemo),
    ("opacitybytex", OpacityByTexDemo),
    ("parts", PartsDemo),
    ("bulletedlist", BulletedListDemo),
    ("title", TitleDemo),
]

PAIRS = [
    ("colorbytex", ["colorbytex"]),
    ("colormap", ["colormap"]),
    ("getpart", ["getpart"]),
    ("opacitybytex", ["opacitybytex"]),
    ("parts", ["parts"]),
    ("bulletedlist", ["bulletedlist"]),
    ("title", ["title"]),
]

PAGE = "09b-片段方法与列表"


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
