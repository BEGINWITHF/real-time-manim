# -*- coding: utf-8 -*-
"""05-RTM的录制与窗口参数.md 样例的完整源码（与页面里的代码块逐字一致）。

本页样例演示的是录制函数 / 窗口的参数，页面里连调用行一起原样摘录。

跑法：python 05-RTM的录制与窗口参数.py               # 渲全部 + 拼接
      python 05-RTM的录制与窗口参数.py fps mlwindow  # 只渲指定样例
      python 05-RTM的录制与窗口参数.py probes        # 跑不产视频的参数探针
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
ASSETS = os.path.dirname(HERE)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import Scene, Square, Text, BLUE, YELLOW, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene, record_scene

if __name__ == "__main__":
    os.chdir(OUT)   #下面所有 out_path 都写成相对文件名，统一落到 final/ 目录


# ===== 样例：scene 的三种形态 ==============================================
class SceneFormDemo(Scene):
    TAG = "scene = class"   #传法标签：类 / 实例 / 无参可调用

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        label = Text(self.TAG, font_size=40, color=YELLOW).to_edge(UP)   #上屏显示当前的传法
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   #蓝色方块
        self.add(label)   #把标签放进场景
        win.play(Create(sq), run_time=0.8)   #画出方块
        win.play(sq.animate.scale(1.2), run_time=0.6)   #方块放大
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


class SceneFormInstance(SceneFormDemo):
    TAG = "scene = instance"   #同一个场景，改成实例形态


class SceneFormCallable(SceneFormDemo):
    TAG = "scene = callable"   #同一个场景，改成无参可调用形态


def run_callable():
    SceneFormCallable().construct()   #无参可调用形态：一个不收参数的函数，把场景跑完


if __name__ == "__main__" and ("scene_forms" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(SceneFormDemo, out_path="scene_class.mp4", verbose=True)   #类：最常用的形态
    fast_record_scene(SceneFormInstance(), out_path="scene_instance.mp4", verbose=True)   #实例：自己先建好再传
    fast_record_scene(run_callable, out_path="scene_callable.mp4", verbose=True)   #无参可调用：流程完全自己写


# ===== 样例：out_path ======================================================
class OutPathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        label = Text("out_path = clips/demo.mp4", font_size=38,
                     color=YELLOW).to_edge(UP)   #上屏显示输出路径
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   #蓝色方块
        self.add(label)   #把标签放进场景
        win.play(Create(sq), run_time=0.8)   #画出方块
        win.play(sq.animate.scale(1.2), run_time=0.6)   #方块放大
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


if __name__ == "__main__" and ("out_path" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(OutPathDemo, out_path="clips/demo.mp4", verbose=True)   #out_path 直接给文件路径，子目录自动创建


# ===== 样例：fps ===========================================================
class FpsDemo(Scene):
    FPS = 30   #请求的帧率：改成 60 就不触发强制纠正

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        label = Text("fps = %d" % self.FPS, font_size=40, color=YELLOW).to_edge(UP)   #上屏显示请求的帧率
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   #蓝色方块
        self.add(label)   #把标签放进场景
        win.play(Create(sq), run_time=0.8)   #画出方块
        win.play(sq.animate.scale(1.2), run_time=0.6)   #方块放大
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


class FpsDemo60(FpsDemo):
    FPS = 60   #同一个场景，请求 60 fps


if __name__ == "__main__" and ("fps" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(FpsDemo, out_path="fps_30.mp4", fps=30, verbose=True)   #fps=30：打印 “[rtm] forcing 60 fps” 后照渲
    fast_record_scene(FpsDemo60, out_path="fps_60.mp4", fps=60, verbose=True)   #fps=60：不触发提示


# ===== 样例：MLWindow 的 w / h / hidden ===================================
class MLWindowDemo(Scene):
    SIZE = "MLWindow(960, 540)  hidden=True"   #窗口参数：尺寸 + 是否隐藏
    W, H = 960, 540   #窗口尺寸：改别的值会被强制纠正成 1920x1080

    def construct(self):
        win = MLWindow(self.W, self.H)   #创建一个 RTM 窗口：“w” / “h” 就是这两个参数
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        label = Text(self.SIZE, font_size=38, color=YELLOW).to_edge(UP)   #上屏显示这组窗口参数
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   #蓝色方块
        self.add(label)   #把标签放进场景
        win.play(Create(sq), run_time=0.8)   #画出方块
        win.play(sq.animate.scale(1.2), run_time=0.6)   #方块放大
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


class MLWindowBig(MLWindowDemo):
    SIZE = "MLWindow(3840, 2160)  hidden=False"   #请求 4K + 可见窗口：照样被纠正成 1920x1080
    W, H = 3840, 2160   #4K 尺寸：只用来触发强制纠正提示


if __name__ == "__main__" and ("mlwindow" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(MLWindowDemo, out_path="mlwin_small.mp4", hidden=True, verbose=True)   #hidden=True：窗口从不弹出
    fast_record_scene(MLWindowBig, out_path="mlwin_big.mp4", hidden=False, verbose=True)   #hidden=False：边渲边弹窗


# ===== 样例：record_scene ==================================================
class RecordSceneDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        label = Text("record_scene = live window", font_size=38,
                     color=YELLOW).to_edge(UP)   #实时录制：窗口可见
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   #蓝色方块
        self.add(label)   #把标签放进场景
        win.play(Create(sq), run_time=0.8)   #画出方块
        win.play(sq.animate.scale(1.2), run_time=0.6)   #方块放大
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


if __name__ == "__main__" and ("record_scene" in sys.argv[1:] or not sys.argv[1:]):
    record_scene(RecordSceneDemo, out_path="record_scene.mp4", fps=60, verbose=True)   #实时可见窗口录制：弹窗、按真实时间跑


# ===== 不产视频的参数：count_only / segment / overwrite / cleanup / verbose ==
if __name__ == "__main__" and "probes" in sys.argv[1:]:
    result = fast_record_scene(FpsDemo, out_path="probe_count.mp4", count_only=True, verbose=True)   #count_only：只数帧，不采集也不写文件
    print("count_only 的返回值：", result)   #out_path 照常返回，但磁盘上没有这个文件
    fast_record_scene(FpsDemo, out_path="probe_bmp", segment=(0, 30), verbose=True)   #segment：按帧区间导出 BMP 目录，不是 MP4
    fast_record_scene(FpsDemo, out_path="probe_clean.mp4", cleanup=False, verbose=True)   #cleanup=False：保留 manim 的 media/ 目录
    try:
        fast_record_scene(FpsDemo, out_path="probe_clean.mp4", overwrite=False, verbose=True)   #overwrite=False：目标已存在就报错
    except FileExistsError as exc:
        print("overwrite=False 的报错：", exc)   #FileExistsError：target already exists
    fast_record_scene(FpsDemo, out_path="probe_quiet.mp4", verbose=False)   #verbose=False：不打进度行


OUTPUTS = [
    ("05-RTM的录制与窗口参数-scene_forms", ["scene_class", "scene_instance", "scene_callable"]),
    ("05-RTM的录制与窗口参数-out_path", ["clips/demo"]),
    ("05-RTM的录制与窗口参数-fps", ["fps_30", "fps_60"]),
    ("05-RTM的录制与窗口参数-mlwindow", ["mlwin_small", "mlwin_big"]),
    ("05-RTM的录制与窗口参数-record_scene", ["record_scene"]),
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


if __name__ == "__main__" and not sys.argv[1:]:
    for out_name, names in OUTPUTS:
        dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
        concat(names, dst)
        print("concat ->", dst, os.path.getsize(dst), "bytes")
