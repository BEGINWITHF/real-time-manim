# -*- coding: utf-8 -*-
"""02-ThreeDScene.md 五个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 02-ThreeDScene.py <场景名>...
不带参数就渲染全部 7 个场景，并拼出页面里的第一条对比视频（ctor）。
"""
import os
import subprocess
import sys
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    BLUE, GREEN, YELLOW, UP, DOWN, DEGREES, ORIGIN, FadeIn,
    Line, Text, ThreeDAxes, Cube, VGroup, VectorizedPoint, config,
    ThreeDScene, SpecialThreeDScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


def say(cap, text):   #瞬间换掉顶部说明文字，不占动画时间
    cap.become(Text(text, font_size=30, color=YELLOW).to_edge(UP))


# ===== 样例 1：ThreeDScene 构造参数、set_to_default_angled_camera_orientation =
class CtorDefault(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #一个蓝色立方体当参照物
        cap = Text("", font_size=30, color=YELLOW)   #顶部说明文字（内容后面换）
        self.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上，视角怎么转都正对观众
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        say(cap, "default phi=0° theta=0°")   #什么都不传：起始就是正面视角
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入
        win.play(Wait(1.4))   #停 1.4s 看清默认视角
        self.set_to_default_angled_camera_orientation()   #应用存着的默认斜视角 {phi:70°, theta:-135°}
        say(cap, "set_to_default_angled_camera_orientation()")
        win.play(Wait(1.6))   #跳到 manim 经典斜视角
        win.close()   #关闭 RTM 窗口


class CtorAngled(ThreeDScene):
    def __init__(self, **kwargs):
        #构造参数只被存进 self.default_angled_camera_orientation_kwargs，没人主动用它
        super().__init__(
            default_angled_camera_orientation_kwargs=
            {"phi": 60 * DEGREES, "theta": -45 * DEGREES}, **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #一个蓝色立方体当参照物
        cap = Text("", font_size=30, color=YELLOW)   #顶部说明文字（内容后面换）
        self.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        say(cap, "ctor kwarg stored ... view unchanged")   #传了构造参数，但没人读它
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入
        win.play(Wait(1.4))   #仍是正面视角：光传参不生效
        self.set_to_default_angled_camera_orientation()   #调这个方法才读取并应用
        say(cap, "set_to_default_angled_camera_orientation()")
        win.play(Wait(1.6))   #这次跳到自定义的 phi=60° theta=-45°
        win.close()   #关闭 RTM 窗口


class CtorAmbient(ThreeDScene):
    def __init__(self, **kwargs):
        #构造参数同样只被存进 self.ambient_camera_rotation，全库没人读它（上游如此）
        super().__init__(ambient_camera_rotation={"theta": 0.15}, **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #一个蓝色立方体当参照物
        cap = Text("", font_size=30, color=YELLOW)   #顶部说明文字（内容后面换）
        self.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        self.set_camera_orientation(phi=65 * DEGREES, theta=-90 * DEGREES)   #先摆个斜视角，才看得出转不转
        say(cap, "ambient_camera_rotation ... no effect")
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入
        win.play(Wait(1.5))   #画面纹丝不动：这个参数没人读
        self.begin_ambient_camera_rotation(rate=0.15)   #要用环境旋转只能调方法
        say(cap, "begin_ambient_camera_rotation(rate=0.15)")
        win.play(Wait(1.5))   #现在开始转
        self.stop_ambient_camera_rotation()   #停住
        win.play(Wait(0.3))   #停 0.3s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：set_camera_orientation / move_camera ========================
class OrientationDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("", font_size=30, color=YELLOW)   #顶部说明文字（内容后面换）
        self.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把三个对象放进场景

        say(cap, "set_camera_orientation phi=30° theta=-60°")
        self.set_camera_orientation(phi=30 * DEGREES, theta=-60 * DEGREES)   #瞬间跳到新视角，没有动画
        win.play(Wait(0.8))   #停 0.8s 看清结果

        say(cap, "move_camera phi=70° theta=-45°")
        self.move_camera(phi=70 * DEGREES, theta=-45 * DEGREES, run_time=1.2)   #带动画地绕到新 phi/theta
        win.play(Wait(0.3))   #停 0.3s

        say(cap, "move_camera gamma=25°")
        self.move_camera(gamma=25 * DEGREES, run_time=0.8)   #画面绕视轴自转 25°
        win.play(Wait(0.3))   #停 0.3s

        say(cap, "move_camera zoom=1.8")
        self.move_camera(zoom=1.8, run_time=0.8)   #推近到 1.8 倍
        win.play(Wait(0.3))   #停 0.3s

        say(cap, "move_camera frame_center=cube")
        self.move_camera(frame_center=cube, run_time=0.8)   #把画面中心挪到立方体上
        win.play(Wait(0.6))   #停 0.6s

        say(cap, "set_camera_orientation 全部复位")
        self.set_camera_orientation(phi=70 * DEGREES, theta=-135 * DEGREES,   #一步复位 phi/theta/gamma/zoom
                                    gamma=0, zoom=1, frame_center=ORIGIN)
        win.play(Wait(0.5))   #停 0.5s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：begin/stop_ambient_camera_rotation、3dillusion ==============
class RotationDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("", font_size=30, color=YELLOW)   #顶部说明文字（内容后面换）
        self.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把三个对象放进场景
        self.set_camera_orientation(phi=60 * DEGREES, theta=-90 * DEGREES)   #先摆好一个斜视角

        say(cap, "ambient rate=0.15 about=theta")
        self.begin_ambient_camera_rotation(rate=0.15, about="theta")   #绕竖直轴匀速环绕，每秒 0.15 弧度
        win.play(Wait(1.6))   #旋转期间一直 wait，画面持续转动
        self.stop_ambient_camera_rotation()   #停住（about 要和 begin 时一致）

        say(cap, "ambient rate=0.2 about=phi")
        self.begin_ambient_camera_rotation(rate=0.2, about="phi")   #改绕极角方向转
        win.play(Wait(1.6))   #旋转期间一直 wait
        self.stop_ambient_camera_rotation(about="phi")   #停住

        say(cap, "3dillusion rate=1")
        self.begin_3dillusion_camera_rotation(rate=1)   #在当前视角附近小幅晃动，造立体感
        win.play(Wait(1.6))   #晃动期间一直 wait
        self.stop_3dillusion_camera_rotation()   #停住
        win.play(Wait(0.3))   #停 0.3s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：fixed_in_frame / fixed_orientation ==========================
class FixedDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.2).set_color(BLUE)   #蓝色立方体当参照物
        title = Text("fixed_in_frame", font_size=34, color=YELLOW)   #演示屏幕钉扎的标题
        tag = Text("fixed_orientation", font_size=26, color=GREEN)   #演示朝向锁定的标签
        tag.next_to(cube, UP)   #标签摆在立方体上方的 3D 空间里
        self.add_fixed_in_frame_mobjects(title)   #标题：位置和朝向都锁死在屏幕上
        title.to_edge(UP)   #标题挪到画面顶端
        self.add_fixed_orientation_mobjects(tag)   #标签：只锁朝向，位置仍在 3D 空间
        self.add(axes, cube, tag)   #把坐标轴、立方体、标签放进场景（标题已被钉扎）
        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)   #摆好斜视角
        win.play(Wait(0.8))   #停 0.8s 看清两个对象的位置

        self.move_camera(theta=-140 * DEGREES, run_time=1.6)   #环绕 90°：标题纹丝不动，标签跟着立方体在画面里移动
        win.play(Wait(0.4))   #停 0.4s

        self.remove_fixed_in_frame_mobjects(title)   #解除屏幕钉扎
        self.remove_fixed_orientation_mobjects(tag)   #解除朝向锁定
        self.move_camera(theta=-190 * DEGREES, run_time=1.4)   #再环绕一次：两个对象都变成普通 3D 对象，跟着视角一起歪
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：SpecialThreeDScene ==========================================
#上游 manim 0.21 bug 2：默认 three_d_axes_config 里的 tick_frequency
#在 0.21 的 NumberLine 里已不存在，原样传进去 TypeError，删掉这一项
AXIS_CFG = {
    "num_axis_pieces": 1,
    "axis_config": {
        "unit_size": 2,
        "numbers_with_elongated_ticks": [0, 1, 2],
        "stroke_width": 2,
    },
}


class SpecialDemo(SpecialThreeDScene):
    def __init__(self, **kwargs):
        #上游 manim 0.21 bug 1：SpecialThreeDScene 在 super().__init__() 之前
        #就读 self.renderer，先塞一个只带 camera_config 的替身绕过去
        self.renderer = SimpleNamespace(
            camera_config={"pixel_width": config.pixel_width})
        super().__init__(three_d_axes_config=AXIS_CFG, **kwargs)   #换掉带 tick_frequency 的默认坐标轴配置

    def get_axes(self):
        #上游 manim 0.21 bug 3：NumberLine 没有 tick_marks 属性了，
        #改用 get_tick_marks()，其余与 manim 源码逐字一致
        axes = ThreeDAxes(**self.three_d_axes_config)
        for axis in axes:
            if self.cut_axes_at_radius:
                p0 = axis.get_start()
                p1 = axis.number_to_point(-1)
                p2 = axis.number_to_point(1)
                p3 = axis.get_end()
                new_pieces = VGroup(Line(p0, p1), Line(p1, p2), Line(p2, p3))
                for piece in new_pieces:
                    piece.shade_in_3d = True
                new_pieces.match_style(axis.pieces)
                axis.pieces.submobjects = new_pieces.submobjects
            for tick in axis.get_tick_marks():
                tick.add(VectorizedPoint(1.5 * tick.get_center()))
        return axes

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        axes = self.get_axes()   #按 three_d_axes_config 生成，坐标轴在球面半径处截断
        sphere = self.get_sphere(color=BLUE, fill_opacity=0.55)   #sphere_config 默认 radius=2、resolution=(24, 48)
        cap = Text("SpecialThreeDScene", font_size=32, color=YELLOW)   #顶部标题
        self.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, sphere, cap)   #把坐标轴、球体、标题放进场景
        self.set_camera_to_default_position()   #回到 default_angled_camera_position（phi=70° theta=-110°）
        print("默认视角：", self.get_default_camera_position())   #把默认视角打到控制台
        win.play(Wait(0.8))   #停 0.8s 看清默认斜视角
        self.move_camera(phi=50 * DEGREES, theta=-150 * DEGREES, run_time=1.4)   #环绕展示立体感
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("ctor_default", CtorDefault),
    ("ctor_angled", CtorAngled),
    ("ctor_ambient", CtorAmbient),
    ("camera", OrientationDemo),
    ("rotation", RotationDemo),
    ("fixed", FixedDemo),
    ("special", SpecialDemo),
]

PAIRS = [
    ("02-ThreeDScene-ctor", ["ctor_default", "ctor_angled", "ctor_ambient"]),
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

    for out_name, names in PAIRS:
        dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
        concat(names, dst)
        print("concat ->", dst, os.path.getsize(dst), "bytes")

    import shutil   #单段样例也要发布成页面成片：<页名>-<片段名>.mp4
    PAGE = os.path.splitext(os.path.basename(__file__))[0]
    used = {n for _, names in PAIRS for n in names}
    for name, _ in SCENES:
        if name in used or (only and name not in only):
            continue
        src = os.path.join(OUT, name + ".mp4")
        if os.path.exists(src):
            shutil.copy(src, os.path.join(HERE, "..", PAGE + "-" + name + ".mp4"))
            print("publish ->", PAGE + "-" + name + ".mp4")
