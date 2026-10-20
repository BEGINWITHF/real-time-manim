"""RTM-Wiki · 03-动画/移动与旋转 视频样例（RTM 渲染）

一段场景覆盖本文件夹 4 个页面的可演示参数，用注释分隔：

    # ========== 01-旋转.md ==========
    # ========== 02-沿路径与同态变换.md ==========
    # ========== 02b-同态变换其余类.md ==========
    # ========== 03-特殊出场.md ==========

Rotate / Rotating / MoveAlongPath / Homotopy 为 RTM 自有实现（✅ 名单）；
02b、03 三个 ⚠️ 类（SmoothedVectorizedHomotopy / ComplexHomotopy / PhaseFlow /
Broadcast）来自 manim 原生实现，由 RTM 的 render_hooks 适配渲染，实测可出片。

运行（cwd 必须是 real-time-manim 仓库）：
    $env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"
    python demo_rtm.py      # -> assets\\sample.mp4
"""
import os

import numpy as np
from real_time_manim import (
    BLUE,
    ORANGE,
    RED,
    TEAL_A,
    DEGREES,
    PI,
    TAU,
    DOWN,
    LEFT,
    ORIGIN,
    OUT,
    RIGHT,
    UP,
    Arc,
    Arrow,
    Circle,
    Dot,
    Scene,
    Square,
    Text,
    Triangle,
    linear,
    Broadcast,
    ComplexHomotopy,
    PhaseFlow,
    SmoothedVectorizedHomotopy,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeOut,
    Homotopy,
    MoveAlongPath,
    Rotating,
    Rotate,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  文件末尾 __main__ 使用


class Demo_Move(Scene):
    def construct(self):
        # 参数 MLWindow(w=1280, h=720, hidden=True) ✓ —— 全片共用一个窗口
        win = MLWindow(1280, 720, hidden=True)
        win.scene = self

        # ========== 01-旋转.md ==========
        # Rotate(mobject, angle=PI, axis=OUT, about_point=None, about_edge=None, **kwargs)
        # Rotating(mobject, angle=TAU, axis=OUT, about_point=None, about_edge=None,
        #          run_time=5, rate_func=linear, **kwargs)
        # 手册本页示例用 Arrow 作演示对象；RTM 的 _send_arrow_tip 在 rot != 0 时
        # `centre(3,) + np.array([..., ...])(2,)` 形状不匹配抛 ValueError，
        # 故本段改用 Triangle 演示（见页面末尾「无法演示」）。
        t01 = Text("旋转动画：Rotate / Rotating", font_size=34).to_edge(UP)
        win.play(Write(t01, run_time=0.8), run_time=0.8)

        sq = Square(side_length=1.6, color=BLUE).shift(LEFT * 4.6 + DOWN * 1.0)
        self.add(sq)
        win.play(                                                          # Rotate：一次性弧线转过去
            Rotate(
                sq,                                                        # 参数 mobject ✓
                angle=PI,                                                  # 参数 angle=PI ✓
                about_point=None,                                          # 参数 about_point=None（用对象中心）✓
                rate_func=linear,                                          # 参数 **kwargs(rate_func) ✓
            ),
            run_time=1.2,                                                  # play 级 run_time ✓
        )
        win.play(                                                          # 绕画面中心公转一整圈
            Rotate(
                sq,
                angle=TAU,                                                 # 参数 angle=TAU ✓
                about_point=ORIGIN,                                        # 参数 about_point=ORIGIN ✓
                rate_func=linear,
            ),
            run_time=1.6,
        )

        tri = Triangle(color=ORANGE).scale(1.0).shift(RIGHT * 3.6 + DOWN * 1.0)
        self.add(tri)
        win.play(                                                          # Rotating：每帧真的转过去（绕对象中心/指定点）
            Rotating(
                tri,                                                       # 参数 mobject ✓
                angle=180 * DEGREES,                                       # 参数 angle=180*DEGREES ✓
                axis=OUT,                                                  # 参数 axis=OUT（2D 即 z 轴）✓
                about_point=ORIGIN,                                        # 参数 about_point=ORIGIN ✓
                about_edge=None,                                           # 参数 about_edge=None（先用 about_point）✓
                run_time=1.6,                                              # 参数 run_time=1.6 ✓
                rate_func=linear,                                          # 参数 rate_func=linear ✓
            ),
            run_time=1.6,
        )
        win.play(                                                          # 用包围盒的边当旋转中心
            Rotating(
                tri,
                angle=90 * DEGREES,
                axis=OUT,
                about_point=None,                                          # 参数 about_point=None ✓
                about_edge=UP,                                             # 参数 about_edge=UP ✓（绕包围盒上边转）
                run_time=1.4,
                rate_func=linear,
            ),
            run_time=1.4,
        )
        win.play(FadeOut(sq, run_time=0.6), FadeOut(tri, run_time=0.6),
                  FadeOut(t01, run_time=0.6), run_time=0.6)

        # ========== 02-沿路径与同态变换.md ==========
        # MoveAlongPath(mobject, path, suspend_mobject_updating=False, **kwargs)
        # Homotopy(homotopy, mobject, run_time=3, apply_function_kwargs=None, **kwargs)
        t02 = Text("沿路径移动与同态变换", font_size=34).to_edge(UP)
        win.play(Write(t02, run_time=0.8), run_time=0.8)

        p = Arc(start_angle=0, angle=PI).shift(LEFT * 4.0 + DOWN * 1.0)
        d = Dot(color=ORANGE).move_to(p.get_start())
        self.add(d, p)
        win.play(                                                          # MoveAlongPath：点沿弧线按比例前进
            MoveAlongPath(
                d,                                                         # 参数 mobject ✓
                p,                                                         # 参数 path ✓（矢量路径 Arc）
                suspend_mobject_updating=False,                            # 参数 suspend_mobject_updating=False ✓
            ),
            rate_func=linear,                                              # play 级 rate_func ✓
            run_time=2,                                                    # play 级 run_time ✓
        )

        sqh = Square(side_length=2.2, color=BLUE).shift(RIGHT * 3.6 + DOWN * 1.0)
        self.add(sqh)

        def homotopy(x, y, z, t):
            return (x, y + 0.3 * np.sin(x + 2 * PI * t), z)

        win.play(                                                          # Homotopy：逐点函数驱动整体变形
            Homotopy(
                homotopy,                                                  # 参数 homotopy ✓
                sqh,                                                       # 参数 mobject ✓
                run_time=2,                                                # 参数 run_time=2 ✓
            ),
            run_time=2,
        )
        win.play(FadeOut(d, run_time=0.6), FadeOut(p, run_time=0.6),
                  FadeOut(sqh, run_time=0.6), FadeOut(t02, run_time=0.6), run_time=0.6)

        # ========== 02b-同态变换其余类.md ==========
        # SmoothedVectorizedHomotopy(homotopy, mobject, run_time=3, apply_function_kwargs=None, **kwargs)
        # ComplexHomotopy(complex_homotopy, mobject, **kwargs)
        # PhaseFlow(function, mobject, virtual_time=1, suspend_mobject_updating=False,
        #           rate_func=linear, **kwargs)
        t02b = Text("同态变换其余类：Smoothed / Complex / PhaseFlow", font_size=34).to_edge(UP)
        win.play(Write(t02b, run_time=0.8), run_time=0.8)

        c = Circle(radius=1.2, color=TEAL_A).shift(LEFT * 4.6 + DOWN * 1.0)
        self.add(c)
        win.play(                                                          # 每帧 make_smooth() 的同态变换
            SmoothedVectorizedHomotopy(
                lambda x, y, z, t: (x * (1 + 0.2 * t), y, z),             # 参数 homotopy ✓
                c,                                                         # 参数 mobject（VMobject）✓
                run_time=1.8,                                              # 参数 run_time=1.8 ✓
                apply_function_kwargs=None,                                # 参数 apply_function_kwargs=None（RTM 版无该形参，仅存于 **kwargs）
            ),
            run_time=1.8,
        )

        sqc = Square(side_length=2.2, color=BLUE).shift(DOWN * 1.0)
        self.add(sqc)
        win.play(                                                          # 复变函数驱动变形
            ComplexHomotopy(
                lambda z, t: z * np.exp(1j * t * PI / 2),                 # 参数 complex_homotopy ✓
                sqc,                                                       # 参数 mobject ✓
                run_time=2.0,                                              # 参数 **kwargs(run_time) ✓
            ),
            run_time=2.0,
        )

        d2 = Dot(color=RED).shift(LEFT * 3.2 + DOWN * 2.6)
        self.add(d2)
        win.play(                                                          # 向量场逐帧累积位移
            PhaseFlow(
                lambda pt: np.array([-pt[1], pt[0], 0.0]),                 # 参数 function ✓（绕原点的旋转场）
                d2,                                                        # 参数 mobject ✓
                virtual_time=1,                                            # 参数 virtual_time=1 ✓
                suspend_mobject_updating=False,                            # 参数 suspend_mobject_updating=False ✓
                rate_func=linear,                                          # 参数 rate_func=linear ✓
                run_time=2.0,                                              # 参数 **kwargs(run_time) ✓
            ),
            run_time=2.0,
        )
        win.play(FadeOut(c, run_time=0.6), FadeOut(sqc, run_time=0.6),
                  FadeOut(d2, run_time=0.6), FadeOut(t02b, run_time=0.6), run_time=0.6)

        # ========== 03-特殊出场.md ==========
        # Broadcast(mobject, focal_point=ORIGIN, n_mobs=5, initial_opacity=1, final_opacity=0,
        #           initial_width=0.0, remover=True, lag_ratio=0.2, run_time=3, **kwargs)
        t03 = Text("特殊出场：Broadcast", font_size=34).to_edge(UP)
        win.play(Write(t03, run_time=0.8), run_time=0.8)

        mob = Circle(radius=3, color=TEAL_A)
        self.add(mob)
        win.play(                                                          # 手册示例：默认参数雷达波纹
            Broadcast(
                mob,                                                       # 参数 mobject ✓
                focal_point=ORIGIN,                                        # 参数 focal_point=ORIGIN ✓
                n_mobs=5,                                                  # 参数 n_mobs=5 ✓
                initial_opacity=1,                                         # 参数 initial_opacity=1 ✓
                final_opacity=0,                                           # 参数 final_opacity=0 ✓
                initial_width=0.0,                                         # 参数 initial_width=0.0 ✓
                remover=True,                                              # 参数 remover=True ✓
                lag_ratio=0.2,                                             # 参数 lag_ratio=0.2 ✓
                run_time=3,                                                # 参数 run_time=3 ✓
            ),
            run_time=3,
        )
        win.play(                                                          # 手册调参示例：更多圈、更快、慢速淡出
            Broadcast(
                mob,
                focal_point=ORIGIN,                                        # 参数 focal_point ✓
                n_mobs=8,                                                  # 参数 n_mobs=8 ✓
                final_opacity=0.4,                                         # 参数 final_opacity=0.4 ✓
                initial_width=0.2,                                         # 参数 initial_width=0.2 ✓（从 0.2 宽开始）
                lag_ratio=0.35,                                            # 参数 lag_ratio=0.35 ✓
                run_time=2,                                                # 参数 run_time=2 ✓
            ),
            run_time=2,
        )
        win.play(Wait(0.4))                                                # 参数 Wait ✓

        # 参数 win.close() ✓ —— 关闭窗口、结束渲染
        win.close()


if __name__ == "__main__":
    fast_record_scene(Demo_Move, out_path=os.path.join(os.path.dirname(__file__), "sample.mp4"), fps=30, overwrite=True, cleanup=True)
