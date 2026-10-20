"""RTM-Wiki · 03-动画/强调与提示 视频样例（RTM 渲染）

一段场景覆盖本文件夹 3 个页面的可演示参数，用注释分隔：

    # ========== 01-强调与闪烁.md ==========
    # ========== 01b-扫光与波纹.md ==========
    # ========== 02-圈注与聚焦.md ==========

只使用 RTM 已导出的动画类（✅ 名单，见 99-功能状态总览）；本组 4 个 ⚠️ 类
（Flash / ShowPassingFlashWithThinningStrokeWidth / FocusOn / Wiggle）来自 manim
原生实现，由 RTM 的 render_hooks 适配渲染，实测可出片。

运行（cwd 必须是 real-time-manim 仓库）：
    $env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"
    python demo_rtm.py      # -> assets\\sample.mp4
"""
import os

from real_time_manim import (
    BLUE,
    DARK_GRAY,
    GREY,
    PURE_YELLOW,
    RED,
    SMALL_BUFF,
    TAU,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Circle,
    Dot,
    RegularPolygon,
    Rectangle,
    Scene,
    Square,
    Text,
    rush_from,
    smooth,
    there_and_back,
    Flash,
    FocusOn,
    ShowPassingFlashWithThinningStrokeWidth,
    Wiggle,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    ApplyWave,
    Blink,
    Circumscribe,
    FadeOut,
    Indicate,
    ShowPassingFlash,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  文件末尾 __main__ 使用


class Demo_Indicate(Scene):
    def construct(self):
        # 参数 MLWindow(w=1280, h=720, hidden=True) ✓ —— 全片共用一个窗口
        win = MLWindow(1280, 720, hidden=True)
        win.scene = self

        # ========== 01-强调与闪烁.md ==========
        # Indicate(mobject, scale_factor=1.2, color=PURE_YELLOW, rate_func=there_and_back, **kwargs)
        # Flash(point, line_length=0.2, num_lines=12, flash_radius=0.1, line_stroke_width=3,
        #       color=PURE_YELLOW, time_width=1, run_time=1.0, **kwargs)
        # Blink(mobject, time_on=0.5, time_off=0.5, blinks=1, hide_at_end=False, **kwargs)
        t01 = Text("强调与闪烁：Indicate / Flash / Blink", font_size=34).to_edge(UP)
        win.play(Write(t01, run_time=0.8), run_time=0.8)

        sq01 = Square(side_length=1.5, color=BLUE).shift(LEFT * 4.6 + DOWN * 1.0)
        self.add(sq01)
        win.play(                                                          # Indicate：放大染色强调
            Indicate(
                sq01,                                                      # 参数 mobject ✓
                scale_factor=1.5,                                          # 参数 scale_factor=1.5 ✓
                color=PURE_YELLOW,                                         # 参数 color=PURE_YELLOW ✓
                rate_func=there_and_back,                                  # 参数 rate_func=there_and_back ✓
            ),
            run_time=1.4,                                                  # 参数 **kwargs(run_time)：RTM 版构造内固定 1.0，用 play 级覆盖 ✓
        )

        dot01 = Dot(color=PURE_YELLOW).shift(LEFT * 1.5 + DOWN * 1.0)
        self.add(dot01)
        win.play(                                                          # Flash：放射闪光
            Flash(
                dot01,                                                     # 参数 point（传 mobject → 取中心）✓
                line_length=0.25,                                          # 参数 line_length=0.25 ✓
                num_lines=30,                                              # 参数 num_lines=30 ✓
                flash_radius=0.15,                                         # 参数 flash_radius=0.15 ✓
                line_stroke_width=3,                                       # 参数 line_stroke_width=3 ✓
                color=RED,                                                 # 参数 color=RED ✓
                time_width=1,                                              # 参数 time_width=1 ✓
                run_time=1.0,                                              # 参数 run_time=1.0 ✓
                rate_func=rush_from,                                       # 参数 **kwargs → 透传给每条线的 ShowPassingFlash ✓
            ),
            run_time=1.0,                                                  # play 级 run_time 与构造值一致 ✓
        )

        txt01 = Text("Blinking", font_size=44).shift(RIGHT * 4.6 + DOWN * 1.0)
        self.add(txt01)
        win.play(                                                          # Blink：明暗闪烁（时间轴 = 显/隐交替）
            Blink(
                txt01,                                                     # 参数 mobject ✓
                time_on=0.4,                                               # 参数 time_on=0.4 ✓
                time_off=0.3,                                              # 参数 time_off=0.3 ✓
                blinks=3,                                                  # 参数 blinks=3 ✓
                hide_at_end=False,                                         # 参数 hide_at_end=False（结束时保持可见）✓
            ),
        )
        win.play(FadeOut(sq01, run_time=0.6), FadeOut(dot01, run_time=0.6),
                  FadeOut(txt01, run_time=0.6), FadeOut(t01, run_time=0.6), run_time=0.6)

        # ========== 01b-扫光与波纹.md ==========
        # ShowPassingFlash(mobject, time_width=0.1, **kwargs)
        # ShowPassingFlashWithThinningStrokeWidth(vmobject, n_segments=10, time_width=0.1, remover=True, **kwargs)
        # ApplyWave(mobject, direction=UP, amplitude=0.2, wave_func=smooth, time_width=1,
        #           ripples=1, run_time=2, **kwargs)
        t01b = Text("扫光与波纹：ShowPassingFlash / ApplyWave", font_size=34).to_edge(UP)
        win.play(Write(t01b, run_time=0.8), run_time=0.8)

        poly = RegularPolygon(5, color=DARK_GRAY).scale(1.7).shift(LEFT * 4.6 + DOWN * 1.0)
        self.add(poly)
        win.play(                                                          # ShowPassingFlash：一束光沿笔画扫过
            ShowPassingFlash(
                poly,                                                      # 参数 mobject ✓
                time_width=0.5,                                            # 参数 time_width=0.5 ✓（光束占整条 50%）
                run_time=1.6,                                              # 参数 **kwargs(run_time) ✓
            ),
            run_time=1.6,
        )
        # RTM 版 ShowPassingFlash 固定 remover=True，播完在 clean_up_from_scene 里把 mobject 移出场景，
        # 因此五边形不再回到场景（CE 是恢复完整笔画），后面不再对它做 FadeOut。

        ring = Circle(radius=1.3, stroke_width=8, color=BLUE).shift(RIGHT * 4.6 + DOWN * 1.0)
        self.add(ring)
        win.play(                                                          # 彗尾渐细扫光
            ShowPassingFlashWithThinningStrokeWidth(
                ring,                                                      # 参数 vmobject ✓
                n_segments=10,                                             # 参数 n_segments=10 ✓
                time_width=0.1,                                            # 参数 time_width=0.1 ✓
                remover=True,                                              # 参数 remover=True ✓
                run_time=2.0,                                              # 参数 **kwargs(run_time) ✓
            ),
            run_time=2.0,
        )

        wtxt = Text("WaveWaveWave", font_size=44).shift(ORIGIN + DOWN * 1.0)
        self.add(wtxt)
        win.play(                                                          # ApplyWave：波纹横穿对象后复原
            ApplyWave(
                wtxt,                                                      # 参数 mobject ✓
                direction=UP,                                              # 参数 direction=UP ✓
                amplitude=0.3,                                             # 参数 amplitude=0.3 ✓
                wave_func=smooth,                                          # 参数 wave_func=smooth ✓
                time_width=1,                                              # 参数 time_width=1 ✓
                ripples=3,                                                 # 参数 ripples=3 ✓
                run_time=2,                                                # 参数 run_time=2 ✓
            ),
        )
        win.play(FadeOut(ring, run_time=0.6), FadeOut(wtxt, run_time=0.6),
                  FadeOut(t01b, run_time=0.6), run_time=0.6)

        # ========== 02-圈注与聚焦.md ==========
        # Circumscribe(mobject, shape=Rectangle, fade_in=False, fade_out=False, time_width=0.3,
        #              buff=SMALL_BUFF, color=PURE_YELLOW, run_time=1, stroke_width=4, **kwargs)
        # FocusOn(focus_point, opacity=0.2, color=GREY, run_time=2, **kwargs)
        # Wiggle(mobject, scale_value=1.1, rotation_angle=0.01*TAU, n_wiggles=6,
        #        scale_about_point=None, rotate_about_point=None, run_time=2, **kwargs)
        t02 = Text("圈注与聚焦：Circumscribe / FocusOn / Wiggle", font_size=34).to_edge(UP)
        win.play(Write(t02, run_time=0.8), run_time=0.8)

        lbl = Text("Circumscribe", font_size=44).shift(LEFT * 4.6 + DOWN * 1.0)
        self.add(lbl)
        cs01 = Circumscribe(
            lbl,                                                           # 参数 mobject ✓
            shape=Rectangle,                                               # 参数 shape=Rectangle（类，不是实例）✓
            fade_in=False,                                                 # 参数 fade_in=False ✓
            fade_out=True,                                                 # 参数 fade_out=True（Create → FadeOut 两段）✓
            time_width=0.3,                                                # 参数 time_width=0.3（RTM 版边框用 Create 画，未接入该参数）
            buff=SMALL_BUFF,                                               # 参数 buff=SMALL_BUFF ✓
            color=PURE_YELLOW,                                             # 参数 color=PURE_YELLOW ✓
            run_time=1.6,                                                  # 参数 run_time=1.6（fade 模式自动平分两段）✓
            stroke_width=4,                                                # 参数 stroke_width=4 ✓
        )
        # RTM 版 Circumscribe 不会把内部边框自动放进场景（play 只收顶层动画的 mobject），
        # 手动加入；播完 clean_up_from_scene 会把它移除。
        self.add(cs01._frame)
        win.play(cs01)

        cs02 = Circumscribe(lbl, shape=Circle, fade_in=True, run_time=1.6)  # 参数 shape=Circle / fade_in=True ✓
        self.add(cs02._frame)
        win.play(cs02)

        dot02 = Dot(color=PURE_YELLOW).shift(RIGHT * 1.5 + DOWN * 1.0)
        self.add(dot02)
        win.play(                                                          # FocusOn：大光斑收缩聚焦到目标点
            FocusOn(
                dot02,                                                     # 参数 focus_point（传 mobject → 取中心）✓
                opacity=0.2,                                               # 参数 opacity=0.2 ✓
                color=GREY,                                                # 参数 color=GREY ✓
                run_time=1.6,                                              # 参数 run_time=1.6 ✓
            ),
        )

        wig = Text("Wiggle", font_size=48).shift(RIGHT * 4.6 + DOWN * 1.0)
        self.add(wig)
        win.play(                                                          # Wiggle：整体抖一下后复原
            Wiggle(
                wig,                                                       # 参数 mobject ✓
                scale_value=1.1,                                           # 参数 scale_value=1.1 ✓
                rotation_angle=0.01 * TAU,                                 # 参数 rotation_angle=0.01*TAU ✓
                n_wiggles=6,                                               # 参数 n_wiggles=6 ✓
                scale_about_point=None,                                    # 参数 scale_about_point=None（用对象中心）✓
                rotate_about_point=None,                                   # 参数 rotate_about_point=None（用对象中心）✓
                run_time=1.6,                                              # 参数 run_time=1.6 ✓
            ),
        )
        win.play(Wait(0.4))                                                # 参数 Wait ✓

        # 参数 win.close() ✓ —— 关闭窗口、结束渲染
        win.close()


if __name__ == "__main__":
    fast_record_scene(Demo_Indicate, out_path=os.path.join(os.path.dirname(__file__), "sample.mp4"), fps=30, overwrite=True, cleanup=True)
