# Recording methods

real-time-manim has **no command line** — you render from Python function calls. The three methods correspond to three different answers to "what will you see":

| Method | What you see | Output | Frame-exact? | Use for |
| --- | --- | --- | --- | --- |
| `fast_record_scene` | Nothing pops up; progress prints in the console | mp4 | Yes | Batch rendering, the daily default |
| `record_scene` | A window pops up and plays the animation for real | mp4 | No (wall-clock) | Rendering while people watch |
| `FramePreview` | A static window + a control bar; scrub frame by frame | None (can save PNGs) | Yes | Tuning animations, finding a frame |

Details below.

## 1. `fast_record_scene` — offline fast recording (no window)

The window **never pops up**; RTM reads the Vulkan framebuffer frame by frame in the background and feeds it straight to ffmpeg. This is the fastest path and it is frame-exact. Use it for batch rendering and scripted output.

```python
from real_time_manim import *

class Demo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the scene to the window
        circle = Circle(color=YELLOW).set_fill(YELLOW, 0.5)
        win.play(FadeIn(circle), run_time=1.0)   # fade in a circle over 1 second
        win.play(circle.animate.shift(RIGHT * 3), run_time=1.0)   # move the circle right
        win.play(Wait(0.5))   # wait 0.5 seconds
        win.close()   # close the window

fast_record_scene(Demo, "demo.mp4")# export to demo.mp4 in the project directory
```

**What you'll see**: nothing on screen; the console prints, in order:

```
[rtm] forcing 1920x1080: RTM supports high quality only (asked for 960x540)
[FastRecord] Pipe: 1920x1080 @ 60 fps (bgra) -> .../demo.mp4
[record] window #1 -> .../demo.mp4
[FastRecord] Saved: .../demo.mp4 (150 frames, ... KB)
```

The first line is the normal "size force-corrected to 1920×1080" notice. `150 frames` = a 2.5-second animation × 60 fps — **every frame lands on disk exactly**, matching the durations in the `win.play` calls.

Common parameters: `out_path` (defaults to `~/Downloads/output.mp4` if omitted), `hidden=False` (**pops the window up while rendering and still stays frame-exact** — use it when you want to watch and still need an exact video), `fps` (60 only). All parameters: [RTM record and window options](../01-Scenes-and-Cameras/Configuration/05-RTM-Record-and-Window-Options.md).

## 2. `record_scene` — live, visible recording (you see the window)

The window **really pops up** and the animation plays in real time, while a background thread grabs frames by the wall clock and composites an mp4. Use it when you want to render and show people at the same time.

```python
from real_time_manim import *
from real_time_manim.record import record_scene

class Demo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the scene to the window
        circle = Circle(color=YELLOW).set_fill(YELLOW, 0.5)
        win.play(FadeIn(circle), run_time=1.0)   # fade in a circle over 1 second
        win.play(circle.animate.shift(RIGHT * 3), run_time=1.0)   # move the circle right
        win.play(Wait(0.5))   # wait 0.5 seconds
        win.close()   # close the window

record_scene(Demo, "demo_live.mp4")# pop the window and play live, recording to demo_live.mp4
```

**What you'll see**: a real window pops up and plays the animation to the end (`[Record] Recording to ... at 60 fps` to start, `[Record] Captured N frames in X.Xs ... encoding ...` to finish). The recorded mp4's duration matches the real playback.

> Reminder: this path's frame count **is not guaranteed to line up with offline rendering** — it runs on the wall clock (including window startup/teardown time), and the capture speed is limited by the machine (measured capture is ~6.5 frames/second, and the result is re-timed to 60 fps by its actual duration: the same animation is 114 frames / 1.90s offline but 130 frames / 2.17s live). For frame-exact reproducible output, use `fast_record_scene`.

## 3. `FramePreview` — frame preview (scrub, no video)

Pops up a **static window + a control bar** that plays nothing by default. Type any frame number or time into the control bar and that frame **immediately** appears in the window — no replaying from frame 0, no pre-rendering the whole video.

Take the file from section 1, replace the last line `fast_record_scene(Demo, "demo.mp4")` with the snippet below (leave the `Demo` scene as is), and add an import at the top of the file:

```python
from real_time_manim import FramePreview   # add at the top of the file

FramePreview(Demo).run()   # open the frame preview window (default: text box mode)
```

**What you'll see**: a video window with a control bar tucked right beneath it (a text box plus three buttons: Jump / Save PNG / Quit), and the title bar shows `frame 0/150   t=0.000s` live. In the text box you can type:

| Input | Meaning |
| --- | --- |
| `120` / `120f` | jump to frame 120 |
| `1.5` / `1.5s` | jump to 1.5 seconds |
| `+10` / `-1` | advance/rewind N frames from the current frame |
| `s` | save the current frame as a PNG (default `frames/` directory) |
| `p` | play from the current frame (any input interrupts) |
| `q` | quit |

For slider mode, drag the slider to sample frames directly: `FramePreview(Demo, controls="slider").run()`.

To grab and save a specific frame directly from a script (no control bar), hook the `FrameServer` behind it onto the `Demo` scene from section 1 (again, add the import at the top of the file):

```python
from real_time_manim import FrameServer   # add at the top of the file

fs = FrameServer(Demo)            # run construct() once, drawing nothing
fs.save_frame(1.5, "frame_1.5.png")# save the frame at 1.5 seconds as a PNG (~10 ms, any frame is just as fast)
fs.close()
```

---

**Summary**: for daily output, `fast_record_scene`; to show people the rendering as it happens, `record_scene` (or `fast_record_scene(hidden=False)` — a window pops up but the result is still frame-exact); to tune animations and find a frame, `FramePreview` / `FrameServer`.

See also: [Installation](01-Installation.md) · [RTM record and window options](../01-Scenes-and-Cameras/Configuration/05-RTM-Record-and-Window-Options.md)
