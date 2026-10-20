# -*- coding: utf-8 -*-
"""15-图片与SVG.md 五个样例的完整源码（与页面里的代码块逐字一致）。

跑法：python 15-图片与SVG.py <样例名>...
不带参数就渲染全部样例，并拼出页面里的五条样例视频（输出到 assets/RTM output/）。
样例用到两个素材文件（就放在 assets/ 下）：demo_photo.png、demo_icon.svg。
"""
import os
import sys

import svgelements as se
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "final",
                        os.path.splitext(os.path.basename(__file__))[0])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, r"C:\Users\begin\Desktop\real-time-manim")

from real_time_manim import (
    Scene, ImageMobject, ImageMobjectFromCamera, SVGMobject, VMobjectFromSVGPath,
    Square, Circle, Triangle, Dot, Text, VGroup,
    BLUE, GREEN, RED, ORANGE, YELLOW, PURPLE, TEAL, GOLD, GREY_B, WHITE,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    Create, FadeIn, FadeOut, Write,
)
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene


# ===== 样例 1：ImageMobject —— 位图图片 ====================================
class ImageDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("15-ImageMobject", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题
        photo = os.path.join(ASSETS, "demo_photo.png")   #参数 “filename_or_array”：图片路径

        # —— 默认：scale_to_resolution=1080 ——
        a = ImageMobject(photo).scale(1.1).move_to([-4.4, 0.9, 0])
        cap = Text("default", font_size=18, color=GREY_B).next_to(a, DOWN, buff=0.3)
        win.play(FadeIn(a), FadeIn(cap), run_time=0.5)

        # —— scale_to_resolution 调小 + NEAREST 重采样：像素化 ——
        b = ImageMobject(photo, scale_to_resolution=120)   #参数 “scale_to_resolution”
        b.set_resampling_algorithm(Image.Resampling.NEAREST)   #方法 “set_resampling_algorithm”
        b.scale(1.1).move_to([0, 0.9, 0])
        cap2 = Text("scale_to_resolution=120 + NEAREST", font_size=18, color=GREY_B).next_to(b, DOWN, buff=0.3)
        win.play(FadeIn(b), FadeIn(cap2), run_time=0.5)

        # —— invert=True：颜色反转 ——
        c = ImageMobject(photo, invert=True).scale(1.1).move_to([4.4, 0.9, 0])   #参数 “invert”
        cap3 = Text("invert=True", font_size=18, color=GREY_B).next_to(c, DOWN, buff=0.3)
        win.play(FadeIn(c), FadeIn(cap3), run_time=0.5)

        # —— set_opacity + image_mode：半透明叠在另一张上 ——
        d = ImageMobject(photo, image_mode="RGB").scale(1.1).move_to([-1.4, -1.9, 0])   #参数 “image_mode”
        e = ImageMobject(photo).scale(1.1).move_to([-0.2, -1.9, 0])   #垫在下面的一张
        d.set_opacity(0.5)   #方法 “set_opacity(alpha)”
        cap4 = Text("set_opacity(0.5)  image_mode='RGB'", font_size=18, color=GREY_B).next_to(d, DOWN, buff=0.3)
        win.play(FadeIn(e), FadeIn(d), FadeIn(cap4), run_time=0.6)

        # —— get_pixel_array：把像素数组的形状打成读数 ——
        arr = d.get_pixel_array()   #方法 “get_pixel_array()”
        cap5 = Text("pixel_array %s %s" % (arr.shape, arr.dtype),
                    font_size=18, color=GREY_B).next_to(e, DOWN, buff=1.0)
        win.play(FadeIn(cap5), run_time=0.4)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 2：ImageMobjectFromCamera —— 把相机画面当图片 ==================
class ImageFromCameraDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("15-ImageMobjectFromCamera", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— 先在场景里摆几个对象，再用相机把它们“拍”下来 ——
        sq = Square(side_length=1.5, color=BLUE).move_to([-2.4, 1.4, 0])
        tri = Triangle(color=GREEN).scale(0.9).move_to([0.4, 1.4, 0])
        dot = Dot([2.6, 1.4, 0], color=ORANGE, radius=0.35)
        win.play(Create(sq), Create(tri), FadeIn(dot), run_time=0.5)
        self.camera.capture_mobject(VGroup(sq, tri, dot))   #把这三个对象画进相机的像素数组

        # —— default_display_frame_config：构造时就指定外框样式 ——
        img = ImageMobjectFromCamera(self.camera,
                                     default_display_frame_config={"stroke_width": 6, "stroke_color": YELLOW, "buff": 0})   #参数 “camera / default_display_frame_config”
        img.set(height=2.4).move_to([-3.6, -1.3, 0])
        win.play(FadeIn(img), run_time=0.7)   #外框是粗黄框

        # —— add_display_frame：事后加外框（可覆盖样式）——
        img2 = ImageMobjectFromCamera(self.camera)   #参数 “camera”
        img2.set(height=2.4).move_to([0.8, -1.3, 0])
        img2.add_display_frame(stroke_color=TEAL, buff=0.1)   #方法 “add_display_frame(**kwargs)”
        win.play(FadeIn(img2), run_time=0.7)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 3：AbstractImageMobject —— 像素数组三个方法 ====================
class AbstractImageDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("15-AbstractImageMobject", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题
        photo = os.path.join(ASSETS, "demo_photo.png")

        # —— 抽象基类不直接构造：拿一个具体实例来用它的方法 ——
        img = ImageMobject(photo, scale_to_resolution=200, pixel_array_dtype="uint8")   #参数 “scale_to_resolution / pixel_array_dtype”
        img.set_resampling_algorithm(Image.Resampling.NEAREST)   #方法 “set_resampling_algorithm”
        img.scale(1.3).move_to([-3.4, 0.4, 0])
        arr = img.get_pixel_array()   #方法 “get_pixel_array()”
        cap = Text("dtype=%s shape=%s" % (arr.dtype, arr.shape),
                   font_size=18, color=GREY_B).next_to(img, DOWN, buff=0.35)
        win.play(FadeIn(img), FadeIn(cap), run_time=0.6)

        # —— set_color：整体染色 ——
        img.set_color(RED)   #方法 “set_color(color)”
        cap2 = Text("set_color(RED)", font_size=18, color=GREY_B).next_to(cap, DOWN, buff=0.2)
        win.play(FadeIn(cap2), run_time=0.4)

        # —— 同一张图换个重采样算法（BICUBIC）：边缘更平滑 ——
        img2 = ImageMobject(photo, scale_to_resolution=200, resampling_algorithm=Image.Resampling.BICUBIC)   #参数 “resampling_algorithm”
        img2.set(height=img.height).move_to([2.6, 0.4, 0])
        cap3 = Text("resampling=BICUBIC", font_size=18, color=GREY_B).next_to(img2, DOWN, buff=0.35)
        win.play(FadeIn(img2), FadeIn(cap3), run_time=0.5)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 4：SVGMobject —— 矢量文件 ======================================
class SVGDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("15-SVGMobject", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题
        icon_path = os.path.join(ASSETS, "demo_icon.svg")   #参数 “file_name”

        # —— 默认：height=2、should_center=True ——
        i1 = SVGMobject(icon_path).move_to([-5.4, 0.9, 0])
        win.play(FadeIn(i1), FadeIn(Text("default", font_size=18, color=GREY_B).next_to(i1, DOWN, buff=0.2)), run_time=0.5)

        # —— height / color：只想变高和统一颜色 ——
        i2 = SVGMobject(icon_path, height=1.1, color=WHITE).move_to([-2.8, 0.9, 0])   #参数 “height / color”
        win.play(FadeIn(i2), FadeIn(Text("height=1.1 color=WHITE", font_size=18, color=GREY_B).next_to(i2, DOWN, buff=0.2)), run_time=0.5)

        # —— width：按宽度缩放（与 height 二选一）——
        i3 = SVGMobject(icon_path, width=2.2).move_to([0.2, 0.9, 0])   #参数 “width”
        win.play(FadeIn(i3), FadeIn(Text("width=2.2", font_size=18, color=GREY_B).next_to(i3, DOWN, buff=0.2)), run_time=0.5)

        # —— should_center=False：不再居中（原点保持在文件原点）——
        i4 = SVGMobject(icon_path, height=1.1, should_center=False).move_to([2.6, 0.9, 0])   #参数 “should_center”
        win.play(FadeIn(i4), FadeIn(Text("should_center=False", font_size=18, color=GREY_B).next_to(i4, DOWN, buff=0.2)), run_time=0.5)

        # —— 填充/描边六件套 + opacity ——
        i5 = SVGMobject(icon_path, height=1.5, opacity=0.6, fill_color=TEAL, fill_opacity=0.8,
                        stroke_color=ORANGE, stroke_opacity=1.0, stroke_width=8,
                        use_svg_cache=False).move_to([-4.6, -2.0, 0])   #参数 “opacity / fill_* / stroke_* / use_svg_cache”
        win.play(FadeIn(i5), FadeIn(Text("fill/stroke 六件套", font_size=18, color=GREY_B).next_to(i5, DOWN, buff=0.2)), run_time=0.6)

        # —— svg_default / path_string_config：覆盖文件内部默认样式 ——
        # svg_default 是**整份**默认样式表（键必须齐全，缺一个就 KeyError）
        i6 = SVGMobject(icon_path, height=1.5,
                        svg_default={"color": None, "fill_color": RED, "fill_opacity": 1.0,
                                     "stroke_color": YELLOW, "stroke_opacity": 1.0,
                                     "stroke_width": 6, "opacity": None},
                        path_string_config={"long_lines": True}).move_to([-1.4, -2.0, 0])   #参数 “svg_default / path_string_config”
        win.play(FadeIn(i6), FadeIn(Text("svg_default={整份样式表}", font_size=18, color=GREY_B).next_to(i6, DOWN, buff=0.2)), run_time=0.6)

        # —— 子对象是各条路径：可以逐个变色 ——
        i7 = SVGMobject(icon_path, height=1.5).move_to([2.2, -2.0, 0])
        i7[0].set_color(PURPLE)   #第一条路径（星形）
        i7[1].set_color(GREEN)   #第二条路径（圆）
        win.play(FadeIn(i7), FadeIn(Text("i7[0] / i7[1] 分别变色", font_size=18, color=GREY_B).next_to(i7, DOWN, buff=0.2)), run_time=0.6)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


# ===== 样例 5：VMobjectFromSVGPath —— 手头的 path 数据 =====================
class SVGPathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("15-VMobjectFromSVGPath", font_size=30, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.4)   #写出标题

        # —— path_obj 必须是已解析的 svgelements.Path（直接传字符串会抛错）——
        tri = VMobjectFromSVGPath(se.Path("M 0 0 L 2 0 L 2 2 Z"), color=TEAL).move_to([-4.4, 1.0, 0])   #参数 “path_obj”
        win.play(Create(tri), FadeIn(Text("se.Path(\"M 0 0 L 2 0 L 2 2 Z\")", font_size=18, color=GREY_B).next_to(tri, DOWN, buff=0.25)), run_time=0.6)

        # —— long_lines：长直线段的拆分方式 ——
        curve = VMobjectFromSVGPath(se.Path("M 0 0 C 1 0 2 1 2 2 L 5 2 Z"),
                                    long_lines=True, color=GOLD).move_to([-0.9, 1.0, 0])   #参数 “long_lines”
        win.play(Create(curve), FadeIn(Text("long_lines=True", font_size=18, color=GREY_B).next_to(curve, DOWN, buff=0.25)), run_time=0.6)

        # —— should_subdivide_sharp_curves：尖角处细分 ——
        sharp = VMobjectFromSVGPath(se.Path("M 0 0 L 2 0 L 2 2 L 0 2 Z"),
                                    should_subdivide_sharp_curves=True, color=ORANGE).move_to([2.8, 1.0, 0])   #参数 “should_subdivide_sharp_curves”
        win.play(Create(sharp), FadeIn(Text("should_subdivide_sharp_curves=True", font_size=18, color=GREY_B).next_to(sharp, DOWN, buff=0.25)), run_time=0.6)

        # —— should_remove_null_curves：丢掉零长度线段 ——
        nulls = VMobjectFromSVGPath(se.Path("M 0 0 L 0 0 L 2 0 L 2 0 L 2 2 Z"),
                                    should_remove_null_curves=True, color=PURPLE).move_to([-3.0, -2.0, 0])   #参数 “should_remove_null_curves”
        win.play(Create(nulls), FadeIn(Text("should_remove_null_curves=True", font_size=18, color=GREY_B).next_to(nulls, DOWN, buff=0.25)), run_time=0.6)

        # —— 从 SVG 文件里抄一条 d 也能这样用 ——
        star = VMobjectFromSVGPath(se.Path("M 60 8 L 74 45 L 114 45 L 82 68 L 94 106 L 60 82 L 26 106 L 38 68 L 6 45 L 46 45 Z"),
                                   color=YELLOW).scale(0.02).move_to([1.2, -2.0, 0])
        win.play(Create(star), FadeIn(Text("从 demo_icon.svg 抄来的 d", font_size=18, color=GREY_B).next_to(star, DOWN, buff=0.25)), run_time=0.6)
        win.play(Wait(0.4))   #停留看结果
        win.close()   #关闭 RTM 窗口


SCENES = [
    ("image", ImageDemo),
    ("imagefromcamera", ImageFromCameraDemo),
    ("abstractimage", AbstractImageDemo),
    ("svg", SVGDemo),
    ("svgpath", SVGPathDemo),
]

PAIRS = [
    ("image", ["image"]),
    ("imagefromcamera", ["imagefromcamera"]),
    ("abstractimage", ["abstractimage"]),
    ("svg", ["svg"]),
    ("svgpath", ["svgpath"]),
]

PAGE = "15-图片与SVG"


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
    import subprocess
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
