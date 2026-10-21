# First Scene

Write an ordinary Manim `Scene`: inside `construct()` open a window, bind the scene, play animations and close the window, and you get a live preview plus one-command recording to MP4.

## Parameters

Interfaces involved in the minimal RTM program template (from the Quick start / Core concepts sections of the README):

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `MLWindow(w, h)` | `int, int` | `1920, 1080` | opens a live Vulkan window; here it is `960×540` / `1280×720` |
| `win.scene` | `Scene` | `None` | binds the current Manim scene to the window (`win.scene = self`) |
| `win.play(*animations, **kwargs)` | animation | — | plays any supported animation; at the play level the **only keywords accepted are `run_time`, `rate_func`, and `path_arc` / `path_arc_axis` / `path_arc_centers` / `path_func`** (`path_*` goes through the setattr semantics of manim's `compile_animations`, see `01-Scenes-and-Cameras/Special-Scenes/05-LinearTransformationScene.md`), and any other keyword such as `lag_ratio` prints a `[RTM] play(): unsupported keyword(s) ... ignored` warning and is ignored (`window/play.py::SUPPORTED_PLAY_KWARGS`) |
| `win.close()` | — | — | closes the window and ends rendering |
| `fast_record_scene(Hello)` | `Scene` subclass | — | records the whole scene to `~/Downloads/output.mp4`; the recording automatically wraps the scene's start and end, then cleans up the temporary `media/` |

## Example

```python
from real_time_manim import Scene, Square, BLUE
from real_time_manim.vulkan_bind import MLWindow, Create, Wait
from real_time_manim.record import fast_record_scene

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        sq = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)   # create a "Square" Mobject named "sq"
        win.play(Create(sq), run_time=1.0)   # apply the "Creat" animation to "sq"; the animation completes in 1s
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window

fast_record_scene(Hello)   # save the video rendered by RTM
```

## Sample video (rendered by RTM)
TODO: record a video of a user running this code with RTM, with the window popping up and the video saved normally. To be recorded by Tagin.
See also: [Installation](01-Installation.md) · [Live Window MLWindow](03-Live-Window-MLWindow.md) · [Recording Video](04-Recording-Video.md)
