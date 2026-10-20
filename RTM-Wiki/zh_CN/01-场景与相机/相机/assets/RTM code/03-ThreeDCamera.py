# -*- coding: utf-8 -*-
"""03-ThreeDCamera.md 四个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 03-ThreeDCamera.py <片段名>...
不带参数就渲染全部 9 个场景，并拼出页面里的四条视频。
"""
import os
import subprocess
import sys
from functools import partial

HERE = os.path.dirname(os.path.abspath(__file__))
FRAG = os.path.join(HERE, "final",
                       os.path.splitext(os.path.basename(__file__))[0])
ASSETS = os.path.dirname(HERE)
os.makedirs(FRAG, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    BLUE, GREEN, WHITE, YELLOW,
    DEGREES, DOWN, LEFT, ORIGIN, OUT, RIGHT, UP,
    Cube, FadeIn, Text, ThreeDAxes, ThreeDCamera, ThreeDScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：class ThreeDCamera 构造参数 ==================================
class CtorAngleDemo(ThreeDScene):
    def __init__(self, **kwargs):
        #“camera_class” 只收类（渲染器内部会无参调用它建相机），
        #构造参数要用 functools.partial 包一层才能送进去
        super().__init__(camera_class=partial(ThreeDCamera, phi=70 * DEGREES, theta=-60 * DEGREES), **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("ctor phi=70 theta=-60 (no set_camera_orientation)", font_size=26, color=YELLOW)   #顶部说明
        self.camera.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上，不随相机转动
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入：视角直接就是斜的
        win.play(Wait(1.2))   #停 1.2s：构造参数里的初始视角直接生效
        win.close()   #关闭 RTM 窗口


class CtorLightDemo(ThreeDScene):
    def __init__(self, **kwargs):
        #把 “light_source_start_point” 也用 partial 送进构造：光源翻到右上前方
        super().__init__(camera_class=partial(
            ThreeDCamera, light_source_start_point=9 * UP + 7 * RIGHT + 10 * OUT), **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("ctor light=9U+7R+10O", font_size=30, color=YELLOW)   #顶部说明
        self.camera.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #视角显式调回前一段的角度，只比光照
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入：明暗和前一段相反
        win.play(Wait(1.0))   #停 1.0s
        win.close()   #关闭 RTM 窗口


class CtorShadingDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("should_apply_shading=True", font_size=30, color=YELLOW)   #顶部说明
        self.camera.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #视角显式设好
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入：各个面深浅不同
        win.play(Wait(0.7))   #停 0.7s
        self.camera.should_apply_shading = False   #关掉着色：所有面变成同一个颜色
        cap.become(Text("should_apply_shading=False", font_size=30, color=YELLOW).to_edge(UP))   #说明文字跟着换
        win.play(Wait(1.0))   #停 1.0s 看清平色
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：get_* / set_* / get_value_trackers ===========================
class ViewZoomDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        cam = self.camera   #ThreeDScene 自带的 ThreeDCamera
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("get_phi / get_theta / get_gamma / get_zoom / get_focal_distance", font_size=22, color=YELLOW)   #顶部说明
        cam.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        info = Text("phi=%.2f theta=%.2f gamma=%.2f zoom=%.2f focal=%.1f" % (
            cam.get_phi(), cam.get_theta(), cam.get_gamma(), cam.get_zoom(), cam.get_focal_distance()),
            font_size=24, color=WHITE).next_to(cap, DOWN)   #五个视角参数的读数
        cam.add_fixed_in_frame_mobjects(info)   #读数也钉在屏幕上
        self.add(axes, cube, cap, info)   #把坐标轴、立方体、标题、读数放进场景
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #视角显式设好
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入
        cam.set_focal_distance(18.0)   #改焦距：立即生效
        cam.set_zoom(1.15)   #改缩放：立即生效
        info.become(Text("phi=%.2f theta=%.2f gamma=%.2f zoom=%.2f focal=%.1f" % (
            cam.get_phi(), cam.get_theta(), cam.get_gamma(), cam.get_zoom(), cam.get_focal_distance()),
            font_size=24, color=WHITE).next_to(cap, DOWN))   #读数刷新
        win.play(Wait(1.2))   #停 1.2s 看清推近后的画面
        win.close()   #关闭 RTM 窗口


class ViewTrackerDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        cam = self.camera   #ThreeDScene 自带的 ThreeDCamera
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("get_value_trackers()[1].animate.set_value(-1.2)", font_size=26, color=YELLOW)   #顶部说明
        cam.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #视角显式设好
        trackers = cam.get_value_trackers()   #5 个 ValueTracker：phi、theta、focal_distance、gamma、zoom
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入
        win.play(trackers[1].animate.set_value(-1.2), run_time=1.0)   #对 theta 的 tracker 做动画：相机环绕
        win.play(Wait(0.6))   #停 0.6s 收工
        win.close()   #关闭 RTM 窗口


class ViewAngleDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        cam = self.camera   #ThreeDScene 自带的 ThreeDCamera
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.5).set_color(BLUE)   #蓝色立方体当参照物
        cap = Text("set_phi(0.6) / set_gamma(0.25)", font_size=28, color=YELLOW)   #顶部说明
        cam.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cube, cap)   #把坐标轴、立方体、标题放进场景
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #视角显式设好
        win.play(FadeIn(cube), run_time=0.5)   #立方体淡入
        cam.set_phi(0.6)   #改极角：立即生效，俯视一些
        cam.set_gamma(0.25)   #改自转角：立即生效，画面绕视轴转动
        win.play(Wait(1.2))   #停 1.2s 看清跳变后的视角
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：add_fixed_in_frame_mobjects / add_fixed_orientation_mobjects ==
class FixedDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #move_camera 内部会调 self.play，先接到窗口上
        cam = self.camera   #ThreeDScene 自带的 ThreeDCamera
        axes = ThreeDAxes()   #默认的三维坐标轴
        cube = Cube(side_length=1.2).set_color(BLUE)   #蓝色立方体当参照物
        title = Text("fixed_in_frame", font_size=34, color=YELLOW)   #演示屏幕钉扎的标题
        tag = Text("fixed_orientation", font_size=26, color=GREEN)   #演示朝向锁定的标签
        tag.next_to(cube, UP)   #标签摆在立方体上方的 3D 空间里
        cam.add_fixed_in_frame_mobjects(title)   #标题：位置和朝向都锁死在屏幕上
        title.to_edge(UP)   #标题挪到画面顶端
        cam.add_fixed_orientation_mobjects(tag)   #标签：只锁朝向，位置仍在 3D 空间
        self.add(axes, cube, tag, title)   #把四个对象放进场景：相机的 add_fixed_* 只登记绘制方式，不替你 add
        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)   #视角显式设好
        win.play(Wait(0.8))   #停 0.8s 看清两个对象的位置
        self.move_camera(theta=-140 * DEGREES, run_time=1.6)   #环绕 90°：标题纹丝不动，标签跟着立方体在画面里移动
        win.play(Wait(0.4))   #停 0.4s
        cam.remove_fixed_in_frame_mobjects(title)   #解除屏幕钉扎
        cam.remove_fixed_orientation_mobjects(tag)   #解除朝向锁定
        self.move_camera(theta=-190 * DEGREES, run_time=1.4)   #再环绕一次：两个对象都变成普通 3D 对象
        win.play(Wait(0.4))   #停 0.4s 收工
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：project_point / project_points、exponential_projection =======
class ProjectDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        cam = self.camera   #ThreeDScene 自带的 ThreeDCamera
        axes = ThreeDAxes()   #默认的三维坐标轴
        cap = Text("project_point(ORIGIN) / project_points([ORIGIN, RIGHT, UP])", font_size=22, color=YELLOW)   #顶部说明
        cam.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, cap)   #把坐标轴和标题放进场景
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #视角显式设好
        p1 = cam.project_point(ORIGIN)   #原点的投影坐标
        pts = cam.project_points([ORIGIN, RIGHT, UP])   #三个点的投影坐标
        info = Text("origin=(%.2f, %.2f)  right=(%.2f, %.2f)  up=(%.2f, %.2f)" % (
            p1[0], p1[1], pts[1][0], pts[1][1], pts[2][0], pts[2][1]),
            font_size=24, color=WHITE).next_to(cap, DOWN)   #投影结果上屏
        cam.add_fixed_in_frame_mobjects(info)   #读数钉在屏幕上
        self.add(info)   #把读数放进场景
        win.play(Wait(1.2))   #停 1.2s 看清投影数值
        win.close()   #关闭 RTM 窗口


class ExponentialDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #场景方法内部会调 self.play，先接到窗口上
        cam = self.camera   #ThreeDScene 自带的 ThreeDCamera
        axes = ThreeDAxes()   #默认的三维坐标轴
        near = Cube(side_length=1.2).set_color(BLUE)   #近处的立方体
        far = Cube(side_length=1.2).set_color(GREEN).shift(DOWN * 2.5 + RIGHT * 2.5)   #远处的立方体
        cap = Text("exponential_projection=False", font_size=28, color=YELLOW)   #顶部说明
        cam.add_fixed_in_frame_mobjects(cap)   #标题钉在屏幕上
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(axes, near, far, cap)   #把坐标轴、两个立方体、标题放进场景
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #视角显式设好
        cam.set_focal_distance(6.0)   #焦距拉近：透视变强，才看得出两种投影的区别
        win.play(FadeIn(near, far), run_time=0.5)   #两个立方体淡入
        win.play(Wait(0.8))   #停 0.8s 看普通投影
        cam.exponential_projection = True   #切到指数投影：远处物体不再被过度放大
        cap.become(Text("exponential_projection=True", font_size=28, color=YELLOW).to_edge(UP))   #说明文字跟着换
        win.play(Wait(1.0))   #停 1.0s 对比
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("03-ThreeDCamera-ctor_angle_1", CtorAngleDemo),
    ("03-ThreeDCamera-ctor_light_2", CtorLightDemo),
    ("03-ThreeDCamera-ctor_shading_3", CtorShadingDemo),
    ("03-ThreeDCamera-view_zoom_1", ViewZoomDemo),
    ("03-ThreeDCamera-view_trackers_2", ViewTrackerDemo),
    ("03-ThreeDCamera-view_angles_3", ViewAngleDemo),
    ("03-ThreeDCamera-fixed_1", FixedDemo),
    ("03-ThreeDCamera-project_coords_1", ProjectDemo),
    ("03-ThreeDCamera-project_exponential_2", ExponentialDemo),
]

PAIRS = [
    ("03-ThreeDCamera-ctor", ["03-ThreeDCamera-ctor_angle_1", "03-ThreeDCamera-ctor_light_2",
                              "03-ThreeDCamera-ctor_shading_3"]),
    ("03-ThreeDCamera-view", ["03-ThreeDCamera-view_zoom_1", "03-ThreeDCamera-view_trackers_2",
                              "03-ThreeDCamera-view_angles_3"]),
    ("03-ThreeDCamera-fixed", ["03-ThreeDCamera-fixed_1"]),
    ("03-ThreeDCamera-project", ["03-ThreeDCamera-project_coords_1", "03-ThreeDCamera-project_exponential_2"]),
]


def concat(names, dst):
    lst = os.path.join(HERE, "concat-03-ThreeDCamera.txt")
    with open(lst, "w", encoding="utf-8") as fh:
        for n in names:
            fh.write("file '%s'\n" % os.path.join(FRAG, n + ".mp4"))
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
            fast_record_scene(cls, out_path=os.path.join(FRAG, name + ".mp4"),
                              verbose=True)
        except Exception:
            import traceback
            traceback.print_exc()

    if not only:
        for out_name, names in PAIRS:
            dst = os.path.join(ASSETS, "RTM output", out_name + ".mp4")
            concat(names, dst)
            print("concat ->", dst, os.path.getsize(dst), "bytes")
