# -*- coding: utf-8 -*-
"""01-MovingCameraScene.md 三个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 01-MovingCameraScene.py <场景名>...
不带参数就渲染全部 7 个场景，并拼出页面里的三条对比视频。
"""
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6)))

from real_time_manim import (
    MovingCameraScene, MovingCamera, Camera,
    Square, Text, VGroup,
    BLUE, RED, GREEN, YELLOW, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    FadeIn, Restore,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：camera_class ===============================================
class CameraClassDemo(MovingCameraScene):
    CAM = MovingCamera   #相机类：改成 “Camera” 再跑一次，取景框会消失

    def __init__(self, **kwargs):
        super().__init__(camera_class=self.CAM, **kwargs)   #把 “camera_class” 传给 Scene.__init__

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        left = Square(color=BLUE, side_length=2).shift(LEFT * 4)   #创建一个蓝色方块，放在画面左侧
        right = Square(color=RED, side_length=2).shift(RIGHT * 4)   #创建一个红色方块，放在画面右侧
        head = VGroup(
            Text(type(self.camera).__name__, font_size=28, color=YELLOW),   #第一行：当前相机类名
            Text("frame=%s" % hasattr(self.camera, "frame"), font_size=22, color=GREEN),   #第二行：有没有取景框
        ).arrange(DOWN, buff=0.1)   #两行文字上下排好
        head.move_to(left)   #把两行文字放进左边方块里，镜头推近时它们也跟着放大
        self.add(left, right, head)   #把三个对象放进场景
        win.play(FadeIn(left), run_time=0.4)   #淡入左边的方块
        if hasattr(self.camera, "frame"):   #只有 “MovingCamera” 才有 “frame”，普通 “Camera” 走不进这个分支
            win.play(self.camera.frame.animate.set(width=4.0).move_to(left), run_time=0.8)   #取景框缩到 4 并移到左边 = 推近
            win.play(self.camera.frame.animate.set(width=14.0).move_to(ORIGIN), run_time=0.8)   #取景框放大到 14 并回中 = 拉回全景
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


class CameraClassPlain(CameraClassDemo):
    CAM = Camera   #只把 “MovingCamera” 换成 “Camera”


# ===== 样例 2：**kwargs -> random_seed ====================================
class RandomSeedDemo(MovingCameraScene):
    SEED = 1   #随机种子：改成 7 再跑一次，一排方块的颜色顺序会变

    def __init__(self, **kwargs):
        super().__init__(random_seed=self.SEED, **kwargs)   #把 “random_seed” 透传给 Scene.__init__

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        tag = Text("random_seed=%d" % self.SEED, font_size=40, color=YELLOW).to_edge(UP)   #在屏幕顶端显示当前种子
        order = [0, 1, 2, 3, 4]   #准备一个 0~4 的下标列表
        random.shuffle(order)   #洗牌；洗牌结果由构造参数 “random_seed” 决定
        colors = [BLUE, RED, GREEN, YELLOW, WHITE]   #五种颜色
        g = VGroup(*[Square(color=colors[i], side_length=0.9) for i in order])   #按洗牌后的下标创建方块
        g.arrange(RIGHT, buff=0.3).to_edge(DOWN)   #从左到右排成一行，颜色顺序 = 洗牌顺序
        self.add(tag, g)   #把标签和这一行方块放进场景
        print("random_seed=%d 洗牌顺序 =" % self.SEED, order)   #把顺序打到控制台，方便对照
        win.play(FadeIn(g), run_time=0.5)   #整行淡入
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


class RandomSeedDemo7(RandomSeedDemo):
    SEED = 7   #同一个场景，只把 “random_seed” 换成 7


# ===== 样例 3：self.camera.frame ==========================================
class FrameDemo(MovingCameraScene):
    WIDTH = 4.0   #取景框宽度：改成 2.0 看更近的一档，改成 14.0 就是全景

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        a = Square(color=BLUE, side_length=1.5).shift(LEFT * 1.5)   #左边的目标
        b = Square(color=RED, side_length=1.5).shift(RIGHT * 1.5)   #右边的目标
        t = Text("width=%.1f" % self.WIDTH, font_size=32, color=WHITE)   #显示当前取景框宽度

        def pin(m):   #让标签跟着取景框底部走，并按取景框宽度缩放，屏幕上大小始终不变
            m.width = self.camera.frame.width * 0.28
            m.move_to(self.camera.frame.get_bottom() + UP * (
                m.height * 0.5 + self.camera.frame.height * 0.08))

        t.add_updater(pin)   #把宽度标签钉在取景框底部
        self.add(a, b, t)   #把三个对象放进场景
        print("初始 frame：height=%.3f width=%.3f" % (
            self.camera.frame.height, self.camera.frame.width))   #默认高度 8.0、宽度 14.222
        self.camera.frame.save_state()   #记住当前（全景）状态，供后面 Restore 复原
        win.play(self.camera.frame.animate.set(width=self.WIDTH), run_time=0.8)   #只改宽度 = 只推拉，画面中心不动
        win.play(self.camera.frame.animate.move_to(a), run_time=0.8)   #只改中心 = 只摇移，缩放比例不动
        print("之后 frame：height=%.3f width=%.3f" % (
            self.camera.frame.height, self.camera.frame.width))   #宽度仍是上面设的值，中心已移到 a
        win.play(Restore(self.camera.frame), run_time=0.8)   #回到 save_state 时的全景
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口


class FrameDemo2(FrameDemo):
    WIDTH = 2.0   #更近的一档


class FrameDemo14(FrameDemo):
    WIDTH = 14.0   #全景


SCENES = [
    ("camera_class_moving", CameraClassDemo),
    ("camera_class_plain", CameraClassPlain),
    ("random_seed_1", RandomSeedDemo),
    ("random_seed_7", RandomSeedDemo7),
    ("frame_width_4", FrameDemo),
    ("frame_width_2", FrameDemo2),
    ("frame_width_14", FrameDemo14),
]

PAIRS = [
    ("camera_class", ["camera_class_moving", "camera_class_plain"]),
    ("random_seed", ["random_seed_1", "random_seed_7"]),
    ("camera_frame", ["frame_width_14", "frame_width_4", "frame_width_2"]),
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

    if not only:
        for out_name, names in PAIRS:
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
