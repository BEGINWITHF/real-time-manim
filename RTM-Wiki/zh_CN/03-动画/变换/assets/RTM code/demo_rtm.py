"""RTM-Wiki · 03-动画/变换 视频样例（RTM 渲染）

一段场景覆盖本文件夹 7 个页面的可演示参数，每页一段，用注释分隔：

    # ========== 01-Transform核心.md ==========
    # ========== 02-方法与函数驱动.md ==========
    # ========== 02b-更多函数驱动.md ==========
    # ========== 03-状态保存与样式变换.md ==========
    # ========== 03b-收缩与变色.md ==========
    # ========== 04-位置互换与复制式变换.md ==========
    # ========== 05-淡出淡入式变换.md ==========

Transform / ReplacementTransform / MoveToTarget / FadeTransform / FadeTransformPieces
来自 RTM 导出清单（✅）；ApplyMethod / ApplyFunction / ApplyPointwiseFunction(ToCenter) /
ApplyComplexFunction / ApplyMatrix / Restore / ScaleInPlace / ShrinkToCenter / FadeToColor /
TransformFromCopy / Clockwise(Counterclockwise)Transform / CyclicReplace / Swap /
TransformAnimations 不在导出清单（⚠️），随自带 ManimCE 从 real_time_manim 导入，实测可跑。

运行（脚本会自行把仓库根目录加入 sys.path）：
    python demo_rtm.py      # -> assets\\sample.mp4
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

import numpy as np
from real_time_manim import (
    BLUE,
    GREEN,
    ORANGE,
    PURPLE,
    RED,
    WHITE,
    YELLOW,
    DEGREES,
    DOWN,
    LEFT,
    ORIGIN,
    OUT,
    RIGHT,
    UP,
    PI,
    Circle,
    Dot,
    MathTex,
    Rectangle,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
    linear,
    smooth,
    squish_rate_func,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeTransform,
    FadeTransformPieces,
    FadeOut,
    MoveToTarget,
    ReplacementTransform,
    Transform,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  文件末尾 __main__ 使用

# 以下动画类不在 RTM 导出清单（⚠️），实测 win.play 可正常播放
from real_time_manim import (
    ApplyComplexFunction,
    ApplyFunction,
    ApplyMatrix,
    ApplyMethod,
    ApplyPointwiseFunction,
    ApplyPointwiseFunctionToCenter,
    ClockwiseTransform,
    CounterclockwiseTransform,
    Create as MCreate,          # TransformAnimations 需要 manim 原生动画（要 set_run_time / starting_mobject）
    CyclicReplace,
    FadeOut as MFadeOut,
    FadeToColor,
    Restore,
    ScaleInPlace,
    ShrinkToCenter,
    Swap,
    TransformAnimations,
    TransformFromCopy,
)


class Demo_Transform(Scene):
    def construct(self):
        # 参数 MLWindow(w=1280, h=720, hidden=True) ✓ —— 全片共用一个窗口
        win = MLWindow(1280, 720, hidden=True)
        win.scene = self

        # ========== 01-Transform核心.md ==========
        # Transform(mobject, target_mobject, path_func, path_arc, path_arc_axis,
        #           path_arc_centers, replace_mobject_with_target_in_scene, **kwargs)
        # ReplacementTransform(mobject, target_mobject, **kwargs)
        # MoveToTarget(mobject, **kwargs)
        t01 = Text("Transform 核心", font_size=40).to_edge(UP)
        sq01 = Square(side_length=1.5, color=BLUE).shift(LEFT * 4 + DOWN * 0.6)
        ci01 = Circle(radius=0.75, color=GREEN).shift(RIGHT * 1.5 + DOWN * 0.6)
        lt01 = Text("left", font_size=36).shift(LEFT * 3.5 + DOWN * 2.6)
        rt01 = Text("right", font_size=36).shift(RIGHT * 3.5 + DOWN * 2.6)
        mt01 = Square(side_length=1.2, color=YELLOW).set_fill(YELLOW, 0.5).shift(DOWN * 2.6)
        win.play(Write(t01, rate_func=linear, run_time=0.8), run_time=0.8)
        win.play(Create(sq01), run_time=0.7)
        win.play(                                                          # 点集插值变形 + 圆弧路径
            Transform(
                sq01, ci01,
                path_func=None,                                            # 参数 path_func=None ✓
                path_arc=PI / 2,                                           # 参数 path_arc=PI/2 ✓
                path_arc_axis=OUT,                                         # 参数 path_arc_axis=OUT ✓
                path_arc_centers=None,                                     # 参数 path_arc_centers=None ✓
                replace_mobject_with_target_in_scene=False,                # 参数 replace_mobject_with_target_in_scene=False ✓
                run_time=1.5,                                              # 参数 run_time ✓
                rate_func=smooth,                                          # 参数 rate_func ✓
            ),
            run_time=1.5,
        )
        self.add(lt01)                                                     # 源对象先放进场景
        win.play(                                                          # 播完源对象消失、目标接管场景
            ReplacementTransform(
                lt01, rt01,
                path_arc=0.0,                                              # 参数 path_arc ✓（显式传入覆盖默认 True 的开关见下）
                path_arc_axis=OUT,
                path_arc_centers=None,
                path_func=None,
                replace_mobject_with_target_in_scene=True,                 # 参数 replace_mobject_with_target_in_scene=True ✓
                run_time=1.2,
            ),
            run_time=1.2,
        )
        win.play(Create(mt01), run_time=0.7)
        mt01.generate_target()                                             # 参数 generate_target() ✓
        mt01.target.shift(RIGHT * 1.6).set_fill(GREEN, 0.5).scale(0.8)
        win.play(MoveToTarget(mt01, run_time=1.2, path_arc=0.0), run_time=1.2)   # 参数 MoveToTarget(mobject) ✓
        win.play(FadeOut(t01), FadeOut(sq01), FadeOut(rt01), FadeOut(mt01), run_time=0.7)

        # ========== 02-方法与函数驱动.md ==========
        # ApplyMethod(method, *args, **kwargs)
        # ApplyFunction(function, mobject, **kwargs)
        # ApplyPointwiseFunction(function, mobject, run_time=3.0, **kwargs)
        t02 = Text("方法 / 函数驱动", font_size=40).to_edge(UP)
        m02 = Square(side_length=1.6, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 4.5 + DOWN * 0.8)
        win.play(Write(t02, rate_func=linear, run_time=0.8), run_time=0.8)
        win.play(Create(m02), run_time=0.7)
        win.play(                                                          # 「调用方法」变成动画
            ApplyMethod(m02.shift, RIGHT * 2.0,                            # 参数 method + *args ✓（绑定方法 + 位置参数）
                        run_time=1.0,                                      # 参数 run_time ✓
                        path_arc=0.0,                                      # 参数 path_arc ✓
                        rate_func=smooth),                                 # 参数 rate_func ✓
            run_time=1.0,
        )
        win.play(                                                          # 纯函数：副本 -> 新对象
            ApplyFunction(lambda m: m.scale(1.4).set_color(RED), m02,
                          run_time=1.2,                                    # 参数 run_time ✓
                          rate_func=smooth),
            run_time=1.2,
        )
        win.play(                                                          # 每个点各走各的（扭曲）
            ApplyPointwiseFunction(lambda p: p + 0.35 * np.sin(p[1] * 3) * RIGHT, m02,
                                   run_time=1.5,                           # 参数 run_time ✓（默认 3.0）
                                   rate_func=smooth),
            run_time=1.5,
        )
        win.play(FadeOut(t02), FadeOut(m02), run_time=0.7)

        # ========== 02b-更多函数驱动.md ==========
        # ApplyPointwiseFunctionToCenter(function, mobject, **kwargs)
        # ApplyComplexFunction(function, mobject, **kwargs)
        # ApplyMatrix(matrix, mobject, about_point=ORIGIN, **kwargs)
        t02b = Text("中心 / 复变 / 矩阵", font_size=40).to_edge(UP)
        d02b = Dot(radius=0.14, color=YELLOW).shift(LEFT * 4.5 + DOWN * 0.8)
        c02b = Square(side_length=2.0, color=GREEN).set_fill(GREEN, 0.4)   # 共形变换以 ORIGIN 为基准
        r02b = Rectangle(width=3.2, height=1.4, color=ORANGE).shift(DOWN * 2.8)
        mtxt = Text("Hello", font_size=44, color=BLUE).move_to(r02b)
        win.play(Write(t02b, rate_func=linear, run_time=0.8), run_time=0.8)
        win.play(Create(d02b), run_time=0.5)
        win.play(                                                          # 只改中心点再整体 move_to
            ApplyPointwiseFunctionToCenter(lambda c: c + UP * 1.4, d02b,
                                           run_time=1.2,                   # 参数 run_time ✓（默认 3.0）
                                           rate_func=smooth),
            run_time=1.2,
        )
        win.play(Create(c02b), run_time=0.7)
        win.play(ApplyComplexFunction(lambda z: np.exp(z), c02b,           # 参数 function + mobject ✓
                                      run_time=1.4, rate_func=smooth),
                 run_time=1.4)
        self.add(mtxt)
        win.play(                                                          # 2x2 线性变换（剪切 + 纵向拉伸）
            ApplyMatrix([[1, 1], [0, 2 / 3]], mtxt,                        # 参数 matrix ✓（2×2 自动补成 3×3）
                        about_point=ORIGIN,                                # 参数 about_point=ORIGIN ✓
                        run_time=1.6,                                      # 参数 run_time ✓（默认 3.0）
                        rate_func=smooth),
            run_time=1.6,
        )
        win.play(FadeOut(t02b), FadeOut(d02b), FadeOut(c02b), FadeOut(mtxt), FadeOut(r02b), run_time=0.7)

        # ========== 03-状态保存与样式变换.md ==========
        # Restore(mobject, **kwargs)
        # ScaleInPlace(mobject, scale_factor, **kwargs)
        t03 = Text("Restore / ScaleInPlace", font_size=38).to_edge(UP)
        sq03 = Square(side_length=1.6, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 3.5 + DOWN * 0.8)
        tx03 = Text("ScaleInPlace", font_size=36, color=GREEN).shift(RIGHT * 3.5 + DOWN * 0.6)
        win.play(Write(t03, rate_func=linear, run_time=0.8), run_time=0.8)
        win.play(Create(sq03), run_time=0.7)
        sq03.save_state()                                                  # 参数 save_state() ✓（Restore 的前提）
        win.play(sq03.animate.set_color(PURPLE).scale(1.8), run_time=1.0)  # 参数 .animate ✓（折腾一下）
        win.play(Restore(sq03, run_time=1.0, rate_func=smooth), run_time=1.0)   # 参数 Restore(mobject) ✓
        win.play(Write(tx03, rate_func=linear, run_time=0.9), run_time=0.9)
        win.play(ScaleInPlace(tx03, 1.6, run_time=0.9, rate_func=smooth), run_time=0.9)   # 参数 scale_factor=1.6 ✓
        win.play(ScaleInPlace(tx03, 0.7, run_time=0.9, rate_func=smooth), run_time=0.9)   # 参数 scale_factor=0.7 ✓
        win.play(FadeOut(t03), FadeOut(sq03), FadeOut(tx03), run_time=0.7)

        # ========== 03b-收缩与变色.md ==========
        # ShrinkToCenter(mobject, **kwargs)      —— 内部固定 scale_factor=0，且不是 remover
        # FadeToColor(mobject, color, **kwargs)
        t03b = Text("ShrinkToCenter / FadeToColor", font_size=36).to_edge(UP)
        sb03b = Text("Bye", font_size=44, color=BLUE).shift(LEFT * 3.5 + DOWN * 1.0)
        fc03b = Text("Hello World!", font_size=40, color=WHITE).shift(RIGHT * 3.5 + DOWN * 1.0)
        win.play(Write(t03b, rate_func=linear, run_time=0.8), run_time=0.8)
        win.play(Write(sb03b, rate_func=linear, run_time=0.9), run_time=0.9)
        win.play(ShrinkToCenter(sb03b, run_time=1.0, rate_func=smooth), run_time=1.0)    # 参数 ShrinkToCenter ✓
        win.play(Write(fc03b, rate_func=linear, run_time=0.9), run_time=0.9)
        win.play(FadeToColor(fc03b, RED, run_time=1.2, rate_func=smooth), run_time=1.2)  # 参数 color=RED ✓
        win.play(FadeOut(t03b), FadeOut(fc03b), run_time=0.7)

        # ========== 04-位置互换与复制式变换.md ==========
        # TransformFromCopy(mobject, target_mobject, **kwargs)
        # ClockwiseTransform(mobject, target_mobject, path_arc=-np.pi, **kwargs)
        # CounterclockwiseTransform(mobject, target_mobject, path_arc=np.pi, **kwargs)
        # CyclicReplace(*mobjects, path_arc=90 * DEGREES, **kwargs)
        # Swap(*mobjects, path_arc=90 * DEGREES, **kwargs)
        t04 = Text("位置互换 / 复制式变换", font_size=36).to_edge(UP)
        aa04 = Text("A", font_size=44, color=BLUE).shift(LEFT * 4 + UP * 1.9)
        bb04 = Text("B", font_size=44, color=GREEN).shift(RIGHT * 4 + UP * 1.9)
        x04 = MathTex("x = 1").shift(LEFT * 4 + DOWN * 0.2)
        y04 = MathTex("x^2 = 1").shift(RIGHT * 4 + DOWN * 0.2)
        p04 = Dot(radius=0.16, color=YELLOW).shift(LEFT * 4 + DOWN * 1.8)
        q04 = Dot(radius=0.16, color=ORANGE).shift(RIGHT * 4 + DOWN * 1.8)
        u04 = Dot(radius=0.16, color=RED).shift(LEFT * 4 + DOWN * 3.0)
        v04 = Dot(radius=0.16, color=PURPLE).shift(RIGHT * 4 + DOWN * 3.0)
        c104 = Text("1", font_size=40, color=BLUE).shift(LEFT * 4.5 + DOWN * 0.9)
        c204 = Text("2", font_size=40, color=GREEN).shift(DOWN * 0.9)
        c304 = Text("3", font_size=40, color=ORANGE).shift(RIGHT * 4.5 + DOWN * 0.9)
        win.play(Write(t04, rate_func=linear, run_time=0.8), run_time=0.8)
        self.add(aa04, bb04)
        win.play(Swap(aa04, bb04, path_arc=90 * DEGREES, run_time=1.2), run_time=1.2)    # 参数 Swap(*mobjects, path_arc) ✓
        win.play(Write(x04, rate_func=linear, run_time=1.0), run_time=1.0)
        win.play(TransformFromCopy(x04, y04, run_time=1.2, rate_func=smooth), run_time=1.2)   # 参数 TransformFromCopy ✓（原件保留）
        self.add(p04, q04)
        win.play(ClockwiseTransform(p04, q04.copy(), path_arc=-np.pi, run_time=1.2), run_time=1.2)   # 参数 path_arc=-π ✓
        self.add(u04, v04)
        win.play(CounterclockwiseTransform(u04, v04.copy(), path_arc=np.pi, run_time=1.2), run_time=1.2)  # 参数 path_arc=+π ✓
        self.add(c104, c204, c304)
        win.play(CyclicReplace(c104, c204, c304, path_arc=90 * DEGREES, run_time=1.4), run_time=1.4)  # 参数 CyclicReplace ✓
        win.play(FadeOut(t04), FadeOut(aa04), FadeOut(bb04), FadeOut(x04), FadeOut(y04),
                 FadeOut(p04), FadeOut(q04), FadeOut(u04), FadeOut(v04),
                 FadeOut(c104), FadeOut(c204), FadeOut(c304), run_time=0.7)

        # ========== 05-淡出淡入式变换.md ==========
        # FadeTransform(mobject, target_mobject, stretch=True, dim_to_match=1, **kwargs)
        # FadeTransformPieces(mobject, target_mobject, stretch=True, dim_to_match=1, **kwargs)
        # TransformAnimations(start_anim, end_anim, rate_func=squish_rate_func(smooth), **kwargs)
        t05 = Text("淡出—淡入式变换", font_size=40).to_edge(UP)
        rc05 = Rectangle(width=4.0, height=1.0, color=BLUE).shift(LEFT * 3.5 + DOWN * 0.6)
        cc05 = Circle(radius=0.5, color=GREEN).shift(RIGHT * 0.5 + DOWN * 0.6)
        src05 = VGroup(Square(side_length=1.1, color=ORANGE), Circle(radius=0.5, color=BLUE).shift(LEFT + UP))
        src05.shift(RIGHT * 3.5 + DOWN * 0.6)
        dst05 = VGroup(Circle(radius=0.5, color=RED), Triangle(color=YELLOW).scale(0.7).shift(RIGHT + DOWN))
        dst05.shift(RIGHT * 3.5 + DOWN * 0.6)
        an05 = Square(side_length=1.6, color=GREEN).set_fill(GREEN, 0.5).shift(LEFT * 3.5 + DOWN * 2.6)
        win.play(Write(t05, rate_func=linear, run_time=0.8), run_time=0.8)
        win.play(                                                          # 源淡出、目标淡入（并拉伸到源尺寸）
            FadeTransform(rc05, cc05, stretch=True, dim_to_match=1,        # 参数 stretch / dim_to_match ✓
                          run_time=1.3, rate_func=smooth),
            run_time=1.3,
        )
        win.play(                                                          # 按子对象逐个配对淡入淡出
            # 注：RTM 的 FadeTransformPieces 是 AnimationGroup，run_time 由内部子动画求和，
            #     构造器不接受 run_time（会与内部 total 冲突），时长放在 play 级别传。
            FadeTransformPieces(src05, dst05, stretch=True, dim_to_match=1),
            run_time=1.5,                                                  # 参数 run_time ✓（play 级别）
            rate_func=smooth,                                              # 参数 rate_func ✓
        )
        win.play(Create(an05), run_time=0.7)
        win.play(                                                          # 两个动画本身互相插值
            TransformAnimations(MCreate(an05), MFadeOut(an05),             # 参数 start_anim / end_anim ✓（需 manim 原生动画）
                                rate_func=squish_rate_func(smooth),        # 参数 rate_func=squish_rate_func(smooth) ✓
                                run_time=1.6),                             # 参数 run_time ✓
            run_time=1.6,
        )
        win.play(Wait(0.4))
        win.play(FadeOut(t05), FadeOut(cc05), FadeOut(dst05), run_time=0.7)

        # 参数 win.close() ✓ —— 关闭窗口、结束渲染
        win.close()


if __name__ == "__main__":
    fast_record_scene(Demo_Transform, out_path=os.path.join(os.path.dirname(__file__), "sample.mp4"), fps=30, overwrite=True, cleanup=True)
