"""RTM-Wiki · 03-Animations/Growth/01-The-Grow-Family -- sample dedicated to this page

Demonstrated parameters (one by one from the page's Parameters table):
    GrowFromPoint(mobject, point=ORIGIN, point_color=RED, run_time=1.3)  ✓
    GrowFromPoint(mobject, point=Dot (a mobject can be a point too), point_color=BLUE, ...)  ✓
    GrowFromCenter(mobject, point_color=GREEN, run_time=1.3)  ✓
    GrowFromEdge(mobject, edge=RIGHT, point_color=ORANGE, run_time=1.3)  ✓
Not demonstrated: point_color=None (the default = keeps the object's own colour, no different from not passing it);
    path_arc / path_func in **kwargs (Transform path parameters, invisible in Grow).
Run: $env:PYTHONPATH="C:\\Users\\begin\\Desktop\\real-time-manim"; python "<this file>"
"""
import os

from real_time_manim import (
    BLUE,
    GREEN,
    GREY_B,
    ORANGE,
    RED,
    YELLOW,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Circle,
    Dot,
    Rectangle,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    GrowFromEdge,
    GrowFromPoint,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401


class Page_01_The_Grow_Family(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameter w=1280 / h=720 / hidden=True
        win.scene = self

        title = Text("Grow family: Point / Center / Edge", font_size=44, color=YELLOW).to_edge(UP)
        win.play(Write(title, run_time=0.8), run_time=0.8)

        # --- 1. GrowFromPoint: grow from a given point (point can be a coordinate or a mobject) ---
        l1 = Text("GrowFromPoint(mobject, point, point_color, run_time=1.3)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        sq = Square(side_length=1.4, color=BLUE).next_to(l1, DOWN, buff=0.7).shift(LEFT * 2.6)
        anchor = Dot(radius=0.1, color=GREY_B).next_to(l1, DOWN, buff=0.7).shift(RIGHT * 1.4)
        tri = Triangle(color=RED).scale(0.8).next_to(l1, DOWN, buff=0.7).shift(RIGHT * 3.4)
        win.play(FadeIn(VGroup(l1, anchor), shift=DOWN), run_time=0.4)
        win.play(
            GrowFromPoint(                          # parameter mobject=sq
                sq,
                ORIGIN,                              # parameter point=ORIGIN (a coordinate as the origin)
                point_color=RED,                     # parameter point_color=RED (the origin is red)
                run_time=1.3,                        # parameter **kwargs(run_time)
            ),
            run_time=1.3,
        )
        win.play(
            GrowFromPoint(                          # parameter mobject=tri
                tri,
                anchor,                              # parameter point=another mobject (its centre is taken)
                point_color=BLUE,                    # parameter point_color=BLUE
                run_time=1.3,                        # parameter **kwargs(run_time)
            ),
            run_time=1.3,
        )
        win.play(FadeOut(VGroup(l1, sq, anchor, tri)), run_time=0.5)

        # --- 2. GrowFromCenter: grow from the object's own centre ---
        l2 = Text("GrowFromCenter(mobject, point_color=GREEN, run_time=1.3)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        ci = Circle(radius=0.85, color=GREEN).next_to(l2, DOWN, buff=0.7)
        win.play(FadeIn(l2, shift=DOWN), run_time=0.4)
        win.play(
            GrowFromCenter(                         # parameter mobject
                ci,                                 # (point is supplied automatically from its own centre)
                point_color=GREEN,                  # parameter point_color=GREEN
                run_time=1.3,                       # parameter **kwargs(run_time)
            ),
            run_time=1.3,
        )
        win.play(FadeOut(VGroup(l2, ci)), run_time=0.5)

        # --- 3. GrowFromEdge: grow out of one edge of the bounding box ---
        l3 = Text("GrowFromEdge(mobject, edge=RIGHT, point_color=ORANGE)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        rect = (Rectangle(width=3.4, height=1.1, color=ORANGE)
                .next_to(l3, DOWN, buff=0.8))
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)
        win.play(
            GrowFromEdge(                           # parameter mobject
                rect,
                RIGHT,                              # parameter edge=RIGHT (grows out of the right edge)
                point_color=ORANGE,                 # parameter point_color=ORANGE
                run_time=1.3,                       # parameter **kwargs(run_time)
            ),
            run_time=1.3,
        )

        win.play(Wait(0.5))
        win.play(FadeOut(VGroup(l3, rect)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(
        Page_01_The_Grow_Family,
        out_path=os.path.join(os.path.dirname(here), "RTM output", "01-The-Grow-Family.mp4"),
        fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
