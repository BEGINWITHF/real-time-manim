# -*- coding: utf-8 -*-
"""06-容器与组合.md 五个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 06-容器与组合.py <样例名>...
不带参数就渲染全部样例，并拼出页面里的五条样例视频（输出到 assets/RTM output/）。
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
    Scene, VGroup, VDict, DashedVMobject, VectorizedPoint, CurvesAsSubmobjects,
    Circle, Square, Triangle, Dot, Line, Rectangle, Text, Arc, Star,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN, DR,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：VGroup —— 矢量对象打包 ======================================
class VGroupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("06-VGroup", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 构造：把三个形状打包 ——
        vg = VGroup(Circle(radius=0.5, color=BLUE),
                    Square(side_length=0.9, color=GREEN),
                    Triangle(color=ORANGE).scale(0.5))   #参数 “*vmobjects”
        vg.arrange(RIGHT, buff=0.4).move_to([-3.4, 1.2, 0])   #方法 “arrange(direction, buff)”
        cap = Text("VGroup(圆, 方, 三角)", font_size=18, color=GREY_B).next_to(vg, DOWN, buff=0.35)
        win.play(Create(vg), FadeIn(cap), run_time=0.6)

        # —— 整体变换：一组对象一起动 ——
        win.play(vg.animate.shift(RIGHT * 1.2).scale(1.15), run_time=0.7)   #整体右移并放大

        # —— add / remove：随时增删子对象（标题就地更新，不叠字）——
        vg.add(Dot([1.6, 0, 0], color=RED, radius=0.14))   #方法 “add(*vmobjects)”
        cap.become(Text("add(Dot)", font_size=18, color=GREY_B).next_to(vg, DOWN, buff=0.35))
        win.play(FadeIn(vg[-1]), run_time=0.5)
        vg.remove(vg[1])   #方法 “remove(*vmobjects)”：拿掉方块
        cap.become(Text("remove(方块)", font_size=18, color=GREY_B).next_to(vg, DOWN, buff=0.35))
        win.play(FadeOut(vg[1].copy().move_to(vg[1])), run_time=0.5)

        # —— 索引与逐个上色：vg[i] 就是个子对象 ——
        vg2 = VGroup(*[Dot(point=[-4.0 + i * 0.9, -1.4, 0], radius=0.16) for i in range(7)])
        vg2[0].set_color(RED)   #下标索引
        vg2[3].set_color(TEAL)
        vg2[-1].set_color(GOLD)
        cap2 = Text("vg2[0] / vg2[3] / vg2[-1] 单独上色", font_size=18, color=GREY_B).next_to(vg2, DOWN, buff=0.4)
        win.play(FadeIn(vg2), FadeIn(cap2), run_time=0.6)

        # —— 整体样式：一次性作用于所有子对象 ——
        win.play(vg2.animate.set_color_by_gradient(BLUE, PURPLE), run_time=0.7)
        cap2.become(Text("set_color_by_gradient 整体生效", font_size=18, color=GREY_B).next_to(vg2, DOWN, buff=0.4))
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：VDict —— 带名字的容器 =======================================
class VDictDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("06-VDict", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 字典形式 + show_keys=True：键会显示在子对象旁边 ——
        vd = VDict({"c": Circle(radius=0.55, color=BLUE),
                    "s": Square(side_length=0.9, color=GREEN)},
                   show_keys=True)   #参数 “mapping_or_iterable / show_keys”
        vd.arrange(RIGHT, buff=1.1).move_to([-3.2, 1.2, 0])
        cap = Text('VDict({"c":…, "s":…}, show_keys=True)', font_size=18, color=GREY_B).next_to(vd, DOWN, buff=0.4)
        win.play(FadeIn(vd), FadeIn(cap), run_time=0.6)

        # —— 键值对列表形式 + show_keys=False ——
        vd2 = VDict([("tri", Triangle(color=ORANGE).scale(0.55)),
                     ("dot", Dot([0.5, 0, 0], color=RED, radius=0.16))],
                    show_keys=False)   #参数 “mapping_or_iterable” 给 iterable
        vd2.arrange(RIGHT, buff=1.0).move_to([1.6, 1.2, 0])
        win.play(FadeIn(vd2), FadeIn(Text('[("tri",…), ("dot",…)] show_keys=False', font_size=18, color=GREY_B).next_to(vd2, DOWN, buff=0.4)), run_time=0.6)

        # —— 按键取值：vd["c"] 拿到的是那个子对象 ——
        vd["c"].set_color(YELLOW)   #按下标/键取子对象
        cap.become(Text('vd["c"].set_color(YELLOW)', font_size=18, color=GREY_B).next_to(vd, DOWN, buff=0.4))
        win.play(Wait(0.4), run_time=0.4)

        # —— add / add_key_value_pair / remove：容器随时增删（注意是按键，不是下标）——
        vd3 = VDict({"t": Triangle(color=TEAL).scale(0.5),
                     "d": Dot([0.6, 0, 0], color=PURPLE, radius=0.14)})
        vd3.arrange(RIGHT, buff=0.9).move_to([-3.2, -1.6, 0])
        win.play(FadeIn(vd3), run_time=0.5)
        vd3.add({"s2": Square(side_length=0.6, color=GREEN)})   #方法 “add(mapping)”
        vd3.add_key_value_pair("c2", Circle(radius=0.32, color=BLUE))   #方法 “add_key_value_pair(key, value)”
        vd3.arrange(RIGHT, buff=0.7).move_to([-3.2, -1.6, 0])
        cap3 = Text('add + add_key_value_pair + remove("t")', font_size=18, color=GREY_B).next_to(vd3, DOWN, buff=0.4)
        win.play(FadeIn(vd3["s2"]), FadeIn(vd3["c2"]), FadeIn(cap3), run_time=0.5)   #按键取值：vd3["s2"]
        vd3.remove("t")   #方法 “remove(key)”
        vd3.arrange(RIGHT, buff=0.7).move_to([-3.2, -1.6, 0])

        # —— get_all_submobjects：把子对象列出来一起动 ——
        subs = vd3.get_all_submobjects()   #方法 “get_all_submobjects()”
        win.play(vd3.animate.shift(RIGHT * 0.8), run_time=0.6)
        cap3.become(Text("get_all_submobjects() -> %d 个" % len(subs), font_size=18, color=GREY_B).next_to(vd3, DOWN, buff=0.4))
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：DashedVMobject —— 虚线化 ====================================
class DashedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("06-DashedVMobject", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— num_dashes：虚线段数（10 与 40 对比）——
        base = Circle(radius=0.85, color=BLUE)
        d10 = DashedVMobject(base, num_dashes=10, color=BLUE).move_to([-4.6, 1.3, 0])   #参数 “vmobject / num_dashes”
        d40 = DashedVMobject(base, num_dashes=40, color=TEAL).move_to([-1.8, 1.3, 0])
        win.play(FadeIn(d10), FadeIn(Text("num_dashes=10", font_size=18, color=GREY_B).next_to(d10, DOWN, buff=0.25)), run_time=0.5)
        win.play(FadeIn(d40), FadeIn(Text("num_dashes=40", font_size=18, color=GREY_B).next_to(d40, DOWN, buff=0.25)), run_time=0.5)

        # —— dashed_ratio：实段占比（0.5 与 0.1 对比）——
        d50 = DashedVMobject(base, num_dashes=20, dashed_ratio=0.5, color=ORANGE).move_to([1.2, 1.3, 0])   #参数 “dashed_ratio”
        ddot = DashedVMobject(base, num_dashes=20, dashed_ratio=0.1, color=YELLOW).move_to([4.0, 1.3, 0])
        win.play(FadeIn(d50), FadeIn(Text("dashed_ratio=0.5", font_size=18, color=GREY_B).next_to(d50, DOWN, buff=0.25)), run_time=0.5)
        win.play(FadeIn(ddot), FadeIn(Text("dashed_ratio=0.1（点线）", font_size=18, color=GREY_B).next_to(ddot, DOWN, buff=0.25)), run_time=0.5)

        # —— dash_offset：起点偏移（虚线在路径上的起始位置）——
        off0 = DashedVMobject(base, num_dashes=12, color=GREEN).move_to([-4.6, -1.6, 0])   #参数 “dash_offset” 默认 0
        off5 = DashedVMobject(base, num_dashes=12, dash_offset=0.5, color=PURPLE).move_to([-1.8, -1.6, 0])
        win.play(FadeIn(off0), FadeIn(Text("dash_offset=0", font_size=18, color=GREY_B).next_to(off0, DOWN, buff=0.25)), run_time=0.5)
        win.play(FadeIn(off5), FadeIn(Text("dash_offset=0.5", font_size=18, color=GREY_B).next_to(off5, DOWN, buff=0.25)), run_time=0.5)

        # —— equal_lengths=False：各段不等长（长段仍按弧长比例）——
        circle = Circle(radius=0.85, color=BLUE).move_to([1.2, -1.6, 0])
        eq = DashedVMobject(circle, num_dashes=12, equal_lengths=False, color=GOLD).move_to([1.2, -1.6, 0])   #参数 “equal_lengths”
        win.play(FadeIn(eq), FadeIn(Text("equal_lengths=False", font_size=18, color=GREY_B).next_to(eq, DOWN, buff=0.25)), run_time=0.5)

        # —— 不限于圆：任意矢量对象都能虚线化 ——
        rr = DashedVMobject(Rectangle(width=2.4, height=1.2, color=RED), num_dashes=24,
                            dashed_ratio=0.6, color=RED).move_to([4.0, -1.6, 0])
        win.play(FadeIn(rr), FadeIn(Text("矩形也能虚线化", font_size=18, color=GREY_B).next_to(rr, DOWN, buff=0.25)), run_time=0.5)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：VectorizedPoint —— 隐形锚点 =================================
class VectorizedPointDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("06-VectorizedPoint", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 默认：完全不可见，但占据一个很小的“报告尺寸” ——
        p = VectorizedPoint(location=[-4.6, 1.5, 0])   #参数 “location”
        box = Rectangle(width=p.width + 0.4, height=p.height + 0.4,
                        color=GREY_B).move_to(p.get_location())
        cap = Text("默认 0.01 x 0.01", font_size=16, color=GREY_B).next_to(box, DOWN, buff=0.3)
        win.play(Create(box), FadeIn(cap), run_time=0.6)

        # —— artificial_width / artificial_height：把“报告尺寸”撑大 ——
        p2 = VectorizedPoint(location=[-1.6, 1.5, 0], artificial_width=0.8,
                             artificial_height=0.5)   #参数 “artificial_width / artificial_height”
        box2 = Rectangle(width=p2.width + 0.2, height=p2.height + 0.2,
                         color=GREY_B).move_to(p2.get_location())
        cap2 = Text("artificial 0.8 x 0.5", font_size=16, color=GREY_B).next_to(box2, DOWN, buff=0.3)
        win.play(Create(box2), FadeIn(cap2), run_time=0.6)

        # —— color / fill_opacity / stroke_width：也能画成一个可见小点 ——
        p3 = VectorizedPoint(location=[1.6, 1.5, 0], color=RED, fill_opacity=1.0,
                             stroke_width=0, artificial_width=0.06,
                             artificial_height=0.06)   #参数 “color / fill_opacity / stroke_width”
        dot = Dot(p3.get_location(), color=YELLOW, radius=0.05)
        cap3 = Text("可见（fill_opacity=1）", font_size=16, color=GREY_B).next_to(p3.get_location(), DOWN, buff=0.35)
        win.play(FadeIn(dot), FadeIn(cap3), run_time=0.6)

        # —— get_location / set_location：把它当锚点搬来搬去 ——
        target = Dot([-3.0, -1.9, 0], color=TEAL, radius=0.1)
        p.set_location([-3.0, -1.9, 0])   #方法 “set_location(new_loc)”
        win.play(FadeIn(target), run_time=0.4)

        # —— 用锚点定位别的对象：把方框搬到它现在的位置 ——
        win.play(box.animate.move_to(p.get_location()), run_time=0.8)   #方法 “get_location()”
        cap.become(Text("set_location + get_location：方框跟着锚点走", font_size=16, color=GREY_B).next_to(target, DOWN, buff=0.4))
        win.play(Wait(0.5))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：CurvesAsSubmobjects —— 拆成一段段 ============================
class CurvesDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("06-CurvesAsSubmobjects", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 圆由若干段贝塞尔曲线组成：拆开后能一段段数出来 ——
        cs = CurvesAsSubmobjects(Circle(radius=1.1, color=BLUE))   #参数 “vmobject”
        cs.move_to([-3.4, 0.4, 0])
        cap = Text("圆 -> %d 段" % len(cs), font_size=18, color=GREY_B).next_to(cs, DOWN, buff=0.8)
        win.play(Create(cs), FadeIn(cap), run_time=0.7)

        # —— 逐段上色：每段是独立子对象 ——
        colors = [RED, ORANGE, YELLOW, GREEN, TEAL, BLUE, PURPLE, GOLD]
        for i, part in enumerate(cs):
            part.set_color(colors[i % len(colors)])
        cap.become(Text("逐段 set_color", font_size=18, color=GREY_B).next_to(cs, DOWN, buff=0.8))
        win.play(Wait(0.4), run_time=0.4)

        # —— 逐段动画：把每段搬开一点，证明它们彼此独立 ——
        for i, part in enumerate(cs):
            part.shift(DR * 0.22 * (i % 3))

        # —— 拆更复杂的对象：`Star` 的多段直线同样能逐段取色 ——
        star = Star(outer_radius=1.2, color=TEAL)
        cs2 = CurvesAsSubmobjects(star)   #参数 “vmobject”
        cs2.scale(0.85).move_to([2.6, 0.4, 0])
        cap2 = Text("Star -> %d 段" % len(cs2), font_size=18, color=GREY_B).next_to(cs2, DOWN, buff=0.4)
        win.play(Create(cs2), FadeIn(cap2), run_time=0.8)

        # —— 对拆出来的段做渐变：逐段取色更方便 ——
        win.play(cs2.animate.set_color_by_gradient(ORANGE, PURPLE), run_time=0.8)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("vgroup", VGroupDemo),
    ("vdict", VDictDemo),
    ("dashed", DashedDemo),
    ("vpoint", VectorizedPointDemo),
    ("curves", CurvesDemo),
]

PAIRS = [
    ("vgroup", ["vgroup"]),
    ("vdict", ["vdict"]),
    ("dashed", ["dashed"]),
    ("vpoint", ["vpoint"]),
    ("curves", ["curves"]),
]

PAGE = "06-容器与组合"


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
