"""RTM-Wiki · 03-动画/文字与数字 视频样例（RTM 渲染）

一段场景覆盖本文件夹 3 个页面的可演示参数，每页一段，用注释分隔：

    # ========== 01-逐字出现与消失.md ==========
    # ========== 01b-带光标打字.md ==========
    # ========== 02-数字动画.md ==========

只使用 RTM 已导出/已接线的动画：`TypeWithCursor` / `UntypeWithCursor` / `Blink`
（✅ 名单），`ChangingDecimal` / `ChangeDecimalToValue`（compat 接线）；
`AddTextLetterByLetter` / `RemoveTextLetterByLetter` / `AddTextWordByWord` 是手册 ⚠️ 类，
不在 RTM 导出清单里，但 real_time_manim 的 render_hooks 已给前两个装好逐字通道，实测可渲。

两个渲染时的小处理（RTM 时间轴只跑到 alpha<1 的最后一帧）：
  * RTM 自有的 `TypeWithCursor` / `UntypeWithCursor` 用 floor(alpha*n) 取字形下标，
    同一个 play 里配一个略长的 `Wait` 把时长撑开，末帧 alpha 才会到 1；
  * `AddTextWordByWord` 是 manim 的 Succession，RTM 会把它内部的 `Group` 也作为
    根对象塞进场景，淡出后要把这个 Group 一并 `self.remove` 掉，否则会残留一份全亮副本。

运行（cwd 必须是 real-time-manim 仓库）：
    $env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"
    python demo_rtm.py      # -> assets\\sample.mp4
"""
import os

import numpy as np
from real_time_manim import (
    BLUE,
    GREY_A,
    PURPLE,
    RED,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    ChangeDecimalToValue,
    ChangingDecimal,
    DecimalNumber,
    Rectangle,
    Scene,
    Text,
    linear,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Blink,
    FadeOut,
    TypeWithCursor,
    UntypeWithCursor,
    Wait,
    Write,
)
# ⚠️ 手册类，不在 RTM 导出清单里；import manim 后由 real_time_manim 的 render_hooks
#    装好逐字显示通道，实测 win.play 可正常出片。
from real_time_manim import AddTextLetterByLetter, AddTextWordByWord, RemoveTextLetterByLetter
from real_time_manim.record import fast_record_scene  # noqa: F401  文件末尾 __main__ 使用


class Demo_TextAnim(Scene):
    def construct(self):
        # 参数 MLWindow(w=1280, h=720, hidden=True) ✓ —— 全片共用一个窗口
        win = MLWindow(1280, 720, hidden=True)
        win.scene = self

        # ========== 01-逐字出现与消失.md ==========
        # AddTextLetterByLetter(text, suspend_mobject_updating=False, int_func=np.ceil,
        #                       rate_func=linear, time_per_char=0.1, run_time=None,
        #                       reverse_rate_function=False, introducer=True, **kwargs)
        # RemoveTextLetterByLetter(text, suspend_mobject_updating=False, int_func=np.ceil,
        #                          rate_func=linear, time_per_char=0.1, run_time=None,
        #                          reverse_rate_function=True, introducer=False, remover=True, **kwargs)
        # AddTextWordByWord(text_mobject, run_time=None, time_per_char=0.06, **kwargs)
        t01 = Text("逐字出现与消失", font_size=40).to_edge(UP)
        a01 = Text("Typing...", font_size=44).shift(LEFT * 3.4 + UP * 1.4)
        b01 = Text("Vanishing", font_size=44).shift(RIGHT * 3.4 + UP * 1.4)
        c01 = Text("Word by word", font_size=40).shift(DOWN * 1.6)
        win.play(Write(t01, rate_func=linear, run_time=0.9), run_time=0.9)
        win.play(                                                         # 一个字母一个字母蹦出来
            AddTextLetterByLetter(
                a01,
                suspend_mobject_updating=False,                           # 参数 suspend_mobject_updating=False ✓
                int_func=np.ceil,                                         # 参数 int_func=np.ceil ✓（到达即显示）
                rate_func=linear,                                         # 参数 rate_func=linear ✓（匀速打字）
                time_per_char=0.15,                                       # 参数 time_per_char=0.15 ✓（默认 0.1）
                run_time=1.5,                                             # 参数 run_time ✓（不传则按 max(1/帧率, time_per_char)*len 自动算）
                reverse_rate_function=False,                              # 参数 reverse_rate_function=False ✓
                introducer=True,                                          # 参数 introducer=True ✓（播前加入场景）
            ),
        )
        win.play(Wait(0.3))                                                # 参数 Wait ✓
        self.add(b01)                                                     # introducer=False → 先手动放进场景
        win.play(                                                         # 父类的倒放：一个字母一个字母消失
            RemoveTextLetterByLetter(
                b01,
                suspend_mobject_updating=False,                           # 参数 suspend_mobject_updating=False ✓
                int_func=np.ceil,                                         # 参数 int_func=np.ceil ✓
                rate_func=linear,                                         # 参数 rate_func=linear ✓
                time_per_char=0.12,                                       # 参数 time_per_char=0.12 ✓
                run_time=1.3,                                             # 参数 run_time ✓
                reverse_rate_function=True,                               # 参数 reverse_rate_function=True ✓（与父类 False 不同）
                introducer=False,                                         # 参数 introducer=False ✓（与父类 True 不同）
                remover=True,                                             # 参数 remover=True ✓（播完移出场景）
            ),
        )
        self.add(c01)
        aw01 = AddTextWordByWord(                                         # 逐词出现（手册标注 currently broken，实测可渲）
            c01,
            run_time=1.4,                                                 # 参数 run_time ✓
            time_per_char=0.06,                                           # 参数 time_per_char=0.06 ✓（默认值）
        )
        win.play(aw01, run_time=1.4)
        win.play(Wait(0.4))
        win.play(FadeOut(t01), FadeOut(a01), FadeOut(c01), run_time=0.6)
        # 淡出后从场景移除：aw01.group 是 manim Succession 内部的 Group，RTM 把它当根
        # 对象画了一份全亮副本，必须一起移除，否则会一直留在后面几节里。
        self.remove(t01, a01, b01, c01, aw01.group)

        # ========== 01b-带光标打字.md ==========
        # TypeWithCursor(text, cursor, buff=0.1, keep_cursor_y=True, leave_cursor_on=True,
        #                time_per_char=0.1, reverse_rate_function=False, introducer=True, **kwargs)
        # UntypeWithCursor(text, cursor=None, time_per_char=0.1, reverse_rate_function=True,
        #                  introducer=False, remover=True, **kwargs)
        # Blink(mobject, time_on=0.5, time_off=0.5, blinks=1, hide_at_end=False)
        t01b = Text("带光标打字 TypeWithCursor / UntypeWithCursor", font_size=34).to_edge(UP)
        txt01 = Text("Inserting", color=PURPLE, font_size=52).shift(LEFT * 3.6)
        cur01 = Rectangle(color=GREY_A, fill_color=GREY_A, fill_opacity=1,
                          height=1.0, width=0.14).move_to(txt01[0])
        txt02 = Text("Deleting", color=PURPLE, font_size=52).shift(RIGHT * 3.0 + DOWN * 1.6)
        cur02 = Rectangle(color=GREY_A, fill_color=GREY_A, fill_opacity=1,
                          height=1.0, width=0.14).move_to(txt02[0])
        win.play(Write(t01b, rate_func=linear, run_time=0.9), run_time=0.9)
        win.play(                                                         # 逐字打字 + 末尾光标
            TypeWithCursor(
                txt01,
                cur01,
                buff=0.1,                                                 # 参数 buff=0.1 ✓（光标与末字符间距）
                keep_cursor_y=True,                                       # 参数 keep_cursor_y=True ✓（光标 y 锁在整段中心）
                leave_cursor_on=True,                                     # 参数 leave_cursor_on=True ✓（播完留下光标）
                time_per_char=0.14,                                       # 参数 time_per_char=0.14 ✓
                reverse_rate_function=False,                              # 参数 reverse_rate_function=False ✓
                introducer=True,                                          # 参数 introducer=True ✓
            ),
            Wait(1.6),                                                    # 比自动 run_time(=0.14*9=1.26s) 略长，末帧 alpha 才到 1
        )
        win.play(Blink(cur01, blinks=2), run_time=2.5)                     # 参数 Blink(blinks=2) ✓（光标闪两下）
        self.add(txt02, cur02)
        win.play(                                                         # 带光标的倒打字
            UntypeWithCursor(
                txt02,
                cur02,
                buff=0.1,                                                 # 参数 buff ✓（继承 TypeWithCursor）
                keep_cursor_y=True,                                       # 参数 keep_cursor_y ✓
                leave_cursor_on=True,                                     # 参数 leave_cursor_on ✓
                time_per_char=0.14,                                       # 参数 time_per_char=0.14 ✓
                reverse_rate_function=True,                               # 参数 reverse_rate_function=True ✓（与父类 False 不同）
                introducer=False,                                         # 参数 introducer=False ✓（与父类 True 不同）
                remover=True,                                             # 参数 remover=True ✓（与父类不同）
            ),
            Wait(1.4),                                                    # 比自动 run_time(=0.14*8=1.12s) 略长，同上
        )
        win.play(FadeOut(t01b), FadeOut(txt01), FadeOut(cur01),
                 FadeOut(txt02), FadeOut(cur02), run_time=0.6)
        self.remove(t01b, txt01, cur01, txt02, cur02)

        # ========== 02-数字动画.md ==========
        # ChangingDecimal(decimal_mob, number_update_func, suspend_mobject_updating=False, **kwargs)
        # ChangeDecimalToValue(decimal_mob, target_number, **kwargs)
        t02 = Text("数字动画 ChangingDecimal / ChangeDecimalToValue", font_size=32).to_edge(UP)
        n01 = DecimalNumber(0, num_decimal_places=2, color=BLUE).shift(LEFT * 3.6 + UP * 1.2)
        n02 = DecimalNumber(0, num_decimal_places=2, color=RED).shift(RIGHT * 3.6 + UP * 1.2)
        cap01 = Text("f(alpha) = 5 * alpha", font_size=28, color=BLUE).next_to(n01, DOWN, buff=0.5)
        cap02 = Text("target = 10", font_size=28, color=RED).next_to(n02, DOWN, buff=0.5)
        win.play(Write(t02, rate_func=linear, run_time=0.9), run_time=0.9)
        win.play(Write(cap01, run_time=0.5), Write(cap02, run_time=0.5), run_time=0.6)
        self.add(n01, n02)
        win.play(                                                         # 任意 f(alpha) -> 数值
            ChangingDecimal(
                n01,
                lambda a: 5 * a,                                          # 参数 number_update_func ✓
                suspend_mobject_updating=False,                           # 参数 suspend_mobject_updating=False ✓（可与 ValueTracker 共存）
                run_time=3,                                               # 参数 **kwargs：run_time ✓
                rate_func=linear,                                         # 参数 **kwargs：rate_func ✓
            ),
        )
        win.play(Wait(1))                                                 # 参数 Wait(1) ✓（页面示例的停顿）
        win.play(                                                         # 从当前值线性跳到目标值
            ChangeDecimalToValue(
                n02,
                10,                                                       # 参数 target_number=10 ✓（源码标 int，浮点同样可用）
                run_time=3,                                               # 参数 **kwargs：run_time=3 ✓
                rate_func=linear,                                         # 参数 **kwargs：rate_func ✓
                suspend_mobject_updating=False,                           # 参数 suspend_mobject_updating=False ✓（继承 ChangingDecimal）
            ),
        )
        win.play(Wait(0.6))
        win.play(FadeOut(t02), FadeOut(cap01), FadeOut(cap02),
                 FadeOut(n01), FadeOut(n02), run_time=0.6)
        self.remove(t02, cap01, cap02, n01, n02)

        # 参数 win.close() ✓ —— 关闭窗口、结束渲染
        win.close()


if __name__ == "__main__":
    fast_record_scene(Demo_TextAnim, out_path=os.path.join(os.path.dirname(__file__), "sample.mp4"), fps=30, overwrite=True, cleanup=True)
