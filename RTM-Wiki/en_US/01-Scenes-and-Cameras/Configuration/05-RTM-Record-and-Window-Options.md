# RTM's Record and Window Options

RTM has no `manim` command line and does not read manim's `config`: **recording** is done by the two functions in `real_time_manim.record` (`fast_record_scene` offline at full speed / `record_scene` live and visible), **window and frame** are determined by `MLWindow(w, h, hidden)`, and **frame rate** only supports 60. This page covers RTM's own core parameters, with a clip for each.

## Parameters

### `fast_record_scene(...)` (offline fast recording)

```python
def fast_record_scene(scene, out_path=None, *, fps=60, hidden=True,
                      count_only=False, segment=None, overwrite=True,
                      cleanup=True, verbose=True) -> dict:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `scene` | `Scene` class / instance / no-arg callable | —(required) | the scene to run. **Can fill in**: a scene class (most common), a scene instance, any function that takes no arguments (see sample) |
| `out_path` | `str \| None` | `None` → `~/Downloads/output.mp4` | the **file path** of the output `.mp4` (not a directory template); subdirectories are created automatically; when one scene opens several windows, later windows get `_partN` appended |
| `fps` | `int` | `60` | output frame rate. **Can only fill in 60**: anything else prints `[rtm] forcing 60 fps` and then renders at 60 anyway (see sample) |
| `hidden` | `bool` | `True` | **Can fill in** `True` (the window never pops up, offline at full speed) / `False` (pop up a window while rendering) |
| `count_only` | `bool` | `False` | probe mode: count frames only, no capture, no GPU rendering, no files written |
| `segment` | `tuple \| None` | `None` | `(start_frame, end_frame)` exports a **BMP directory** by frame range (`out_path` becomes a directory), instead of a single MP4 |
| `overwrite` | `bool` | `True` | when `False`, a target file that already exists raises `FileExistsError` |
| `cleanup` | `bool` | `True` | delete manim's temporary `media/` directory after recording; `False` keeps it |
| `verbose` | `bool` | `True` | whether to print the progress line for each window |

**Returns**: `dict` — `{"out_path": ..., "windows": [...], "files": [...], "with_audio": [...]}`; `files` is the output that really exists on disk (empty when `count_only`).

#### Sample: `scene` (class / instance / no-arg callable)

The same scene recorded three times with three different passing styles: pass the class (RTM builds an instance itself and runs `setup()`+`construct()`), pass an instance, pass a function that takes no arguments.

```python
import sys

from real_time_manim import Scene, Square, Text, BLUE, YELLOW, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene, record_scene

class SceneFormDemo(Scene):
    TAG = "scene = class"   # passing style: class / instance / no-arg callable

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        label = Text(self.TAG, font_size=40, color=YELLOW).to_edge(UP)   # show the current passing style on screen
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   # blue square
        self.add(label)   # put the label into the scene
        win.play(Create(sq), run_time=0.8)   # draw the square
        win.play(sq.animate.scale(1.2), run_time=0.6)   # scale the square up
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


class SceneFormInstance(SceneFormDemo):
    TAG = "scene = instance"   # same scene, changed to the instance form


class SceneFormCallable(SceneFormDemo):
    TAG = "scene = callable"   # same scene, changed to the no-arg callable form


def run_callable():
    SceneFormCallable().construct()   # no-arg callable form: a function that takes no arguments, runs the scene to completion


if __name__ == "__main__" and ("scene_forms" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(SceneFormDemo, out_path="scene_class.mp4", verbose=True)   # class: the most common form
    fast_record_scene(SceneFormInstance(), out_path="scene_instance.mp4", verbose=True)   # instance: build it yourself and pass it
    fast_record_scene(run_callable, out_path="scene_callable.mp4", verbose=True)   # no-arg callable: the whole flow is written by you
```

What this code does: the three subclasses only swap the label to `scene = class` / `scene = instance` / `scene = callable`, and the scene content is exactly the same; then three `fast_record_scene` calls record it in the three forms **class, instance, no-arg callable**, and the three clips produced correspond to the three panels in the video.

When you pass a class RTM builds an instance for you and runs `setup()`+`construct()`; when you pass an instance it runs the one you give; when you pass a function it just calls it, and whatever it runs is entirely up to the function (in the sample it is `SceneFormCallable().construct()`).

<video src="assets/RTM output/05-RTM-Record-and-Window-Options-scene_forms.mp4" controls width="560"></video>

> Note: when you pass a no-arg callable RTM does **not** call `setup()` for you — if your scene depends on `setup()` (for example `MovingCameraScene`'s framing box is built in `setup()`), either pass a class/instance or call it yourself in the function. For everyday use just pass the class.

#### Sample: `out_path` (output path)

`out_path` is simply "where the file lands": give the file path directly, non-existent subdirectories are created automatically, and it does not go through the `media_dir` directory-template set.

```python
import sys

from real_time_manim import Scene, Square, Text, BLUE, YELLOW, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene, record_scene

class OutPathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        label = Text("out_path = clips/demo.mp4", font_size=38,
                     color=YELLOW).to_edge(UP)   # show the output path on screen
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   # blue square
        self.add(label)   # put the label into the scene
        win.play(Create(sq), run_time=0.8)   # draw the square
        win.play(sq.animate.scale(1.2), run_time=0.6)   # scale the square up
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


if __name__ == "__main__" and ("out_path" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(OutPathDemo, out_path="clips/demo.mp4", verbose=True)   # out_path gives the file path directly, subdirectories are created automatically
```

What this code does: the scene content is the same as the previous sample, except the call has `out_path="clips/demo.mp4"` — the output lands directly in `demo.mp4` under the `clips/` subdirectory, and `clips/` is created automatically if it does not exist.

The video embedded in the page is this file itself (finally published per the naming convention as `assets/RTM output/05-RTM-Record-and-Window-Options-out_path.mp4`).

<video src="assets/RTM output/05-RTM-Record-and-Window-Options-out_path.mp4" controls width="560"></video>

> Note:
>
> - When `out_path` is not passed it writes to `~/Downloads/output.mp4` by default, and it is easy to fill up your desktop downloads directory by accident — it is better to give a path explicitly every time.
> - In a multi-window scene the second window writes `xxx_part2.mp4`; don't let it clash with a file name you gave yourself.

#### Sample: `fps` (frame rate, only 60)

The same scene requests `fps=30` and `fps=60` and records one clip each: a request of 30 is force-corrected to 60 and a hint is printed, and the two clips' frame counts and durations are exactly the same.

```python
import sys

from real_time_manim import Scene, Square, Text, BLUE, YELLOW, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene, record_scene

class FpsDemo(Scene):
    FPS = 30   # requested frame rate: change it to 60 and the forced correction is not triggered

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        label = Text("fps = %d" % self.FPS, font_size=40, color=YELLOW).to_edge(UP)   # show the requested frame rate on screen
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   # blue square
        self.add(label)   # put the label into the scene
        win.play(Create(sq), run_time=0.8)   # draw the square
        win.play(sq.animate.scale(1.2), run_time=0.6)   # scale the square up
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


class FpsDemo60(FpsDemo):
    FPS = 60   # same scene, requests 60 fps


if __name__ == "__main__" and ("fps" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(FpsDemo, out_path="fps_30.mp4", fps=30, verbose=True)   # fps=30: prints "[rtm] forcing 60 fps" and then renders anyway
    fast_record_scene(FpsDemo60, out_path="fps_60.mp4", fps=60, verbose=True)   # fps=60: does not trigger the hint
```

What this code does: the only difference between the two clips is `fps=30` / `fps=60` in the call (the scene only prints the number on the label).

The `fps=30` run prints `[rtm] forcing 60 fps: RTM supports high quality only (asked for 30)` to the console, then still produces the clip at 60fps — so in the video the two clips are 114 frames / 1.90s each, aligned frame by frame, with only the label text differing.

<video src="assets/RTM output/05-RTM-Record-and-Window-Options-fps.mp4" controls width="560"></video>

> Note: if you want a 30fps clip, render at 60fps first, then convert with `ffmpeg -i in.mp4 -r 30 out.mp4` — filling in `fps=30` directly only gets you one line of hint. The same applies to `MLWindow`'s `w`/`h`: any request other than 1920×1080 is force-corrected (the next section has real footage).

#### Sample: `count_only` / `segment` / `overwrite` / `cleanup` / `verbose` (no clip)

These five parameters change "whether to record, where to record, whether to overwrite, whether to keep the temporary directory, whether to talk"; the picture content is exactly the same (it may not even produce a video), so only the code and the measured output are given, no video. The probe below is in the demo script; run `python 05-RTM-Record-and-Window-Options.py probes` to reproduce it:

```python
if __name__ == "__main__" and "probes" in sys.argv[1:]:
    result = fast_record_scene(FpsDemo, out_path="probe_count.mp4", count_only=True, verbose=True)   # count_only: count frames only, no capture and no file
    print("count_only return value: ", result)   # out_path is returned as usual, but the file is not on disk
    fast_record_scene(FpsDemo, out_path="probe_bmp", segment=(0, 30), verbose=True)   # segment: export a BMP directory by frame range, not an MP4
    fast_record_scene(FpsDemo, out_path="probe_clean.mp4", cleanup=False, verbose=True)   # cleanup=False: keep manim's media/ directory
    try:
        fast_record_scene(FpsDemo, out_path="probe_clean.mp4", overwrite=False, verbose=True)   # overwrite=False: error if the target already exists
    except FileExistsError as exc:
        print("overwrite=False error: ", exc)   # FileExistsError: target already exists
    fast_record_scene(FpsDemo, out_path="probe_quiet.mp4", verbose=False)   # verbose=False: don't print progress lines
```

Measured output (in order):

| Parameter | Measured behaviour |
| --- | --- |
| `count_only=True` | prints `[FastRecord] Count: 114 frames`, writes no files; the return value's `files` is an empty list |
| `segment=(0, 30)` | prints `[FastRecord] BMP mode (0, 30)` and `[FastRecord] BMP: 30 frames in ...`; the directory contains `frame_000000.bmp` ~ `frame_000029.bmp` |
| `cleanup=False` | after that run manim's `media/` directory stays in place (by default the whole directory is deleted) |
| `overwrite=False` | when the target already exists it raises `FileExistsError: target already exists: ... (pass overwrite=True to replace it)` |
| `verbose=False` | does not print progress lines like `[record] window #1 -> ...` / `[FastRecord] ...` |

> Note:
>
> - `segment` exports a **BMP sequence** (uncompressed, takes a lot of disk space); use it to connect to a frame-by-frame toolchain; if you only want to know "how many frames this animation has", use `count_only=True`, which is the fastest.
> - `overwrite=False`'s protection only looks at whether the file exists, it does not compare content — it is well suited to preventing overwrites in batch scripts.

### `record_scene(...)` (live visible-window recording)

```python
def record_scene(scene, out_path=None, *, fps=60, overwrite=True,
                 cleanup=True, verbose=True) -> dict:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `scene` | `Scene` class / instance / no-arg callable | —(required) | the scene to run, the three forms are the same as `fast_record_scene` |
| `out_path` | `str \| None` | `None` → `~/Downloads/output.mp4` | the output `.mp4` file path, same as above |
| `fps` | `int` | `60` | capture frame rate (a background thread grabs the window at this rate); likewise only 60 is supported |
| `overwrite` | `bool` | `True` | same as `fast_record_scene` |
| `cleanup` | `bool` | `True` | same as `fast_record_scene` |
| `verbose` | `bool` | `True` | same as `fast_record_scene` |

The only difference from `fast_record_scene` is one thing: **the window must be visible**; the animation plays in real time and a background thread grabs the screen while watching (under the hood it is `win.start_record(...)` ... `win.stop_record()`). It suits situations where you render while showing someone; for batch clip production `fast_record_scene` is much faster.

#### Sample: `record_scene`

The same animation goes through live recording: a visible window pops up, it plays to completion by wall clock, and a background thread captures the screen and composites an mp4.

```python
import sys

from real_time_manim import Scene, Square, Text, BLUE, YELLOW, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene, record_scene

class RecordSceneDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        label = Text("record_scene = live window", font_size=38,
                     color=YELLOW).to_edge(UP)   # live recording: the window is visible
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   # blue square
        self.add(label)   # put the label into the scene
        win.play(Create(sq), run_time=0.8)   # draw the square
        win.play(sq.animate.scale(1.2), run_time=0.6)   # scale the square up
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


if __name__ == "__main__" and ("record_scene" in sys.argv[1:] or not sys.argv[1:]):
    record_scene(RecordSceneDemo, out_path="record_scene.mp4", fps=60, verbose=True)   # live visible-window recording: pop up a window, run by real time
```

What this code does: the scene content is the same as before (the label is swapped to `record_scene = live window`), but the recording goes through `record_scene` — you will see the window really pop up and play the animation to the end, the console prints `[Record] Recording to ... at 60 fps`, and at the end it reports `Captured N frames in X.Xs (... fps), encoding ...`.

The output video's timing matches real playback.

<video src="assets/RTM output/05-RTM-Record-and-Window-Options-record_scene.mp4" controls width="560"></video>

> Note: live recording's **frame count is not guaranteed to align with offline rendering** — it goes by wall clock (including window startup/finish-up time), and the capture speed is also limited by machine performance (on this machine, measured at about 6.5 frames/second capture; the clip is rearranged to 60fps by actual duration, so the picture is a bit choppy but the rhythm is correct: 130 frames / 2.17s, compared with the offline 114 frames / 1.90s).
>
> For frame-level reproducible output, use `fast_record_scene`.

### `MLWindow(w, h, hidden)` (window and frame)

```python
def __init__(self, w=1920, h=1080, hidden=None):
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `w` | `int` | `1920` | window/framebuffer width = RTM's "resolution". **Can only fill in 1920**: passing anything else prints `[rtm] forcing 1920x1080` and then force-corrects |
| `h` | `int` | `1080` | window/framebuffer height, same as above |
| `hidden` | `bool \| None` | `None` → follows the class attribute `_hidden_default` | **Can fill in** `True` (build as a hidden window) / `False` / `None` (follow the default). Usually not passed directly: `fast_record_scene(hidden=...)` has already set it for you |

**Enforced specs**: the frame only supports `1920×1080` (`MLWindow.SUPPORTED_WIDTH/HEIGHT`), and the frame rate only supports `60` (`SUPPORTED_FPS`). Passing other values does not raise an error; instead they are force-corrected and a hint is printed — so `MLWindow(960, 540)` printing `[rtm] forcing 1920x1080` is **normal** and needs no change.

After the window is created, `win.scene = self` binds the manim scene to it, `win.play(...)` drives playback, and `win.close()` finishes up (when **wrapped by the recording helper** it also ends the encoding along the way: `record._AutoRecord` runs `_finish_fast_record()` / `stop_record()` before the real `MLWindow.close()`, see the `enable_fast_record` section on this page).

#### Sample: `w` / `h` / `hidden` (a group of strongly related parameters)

The two clips each request a different set of window parameters (960×540 hidden / 3840×2160 visible), and the output picture is identical frame by frame — the size request is force-corrected, and visibility only affects whether a window pops up on the desktop.

```python
import sys

from real_time_manim import Scene, Square, Text, BLUE, YELLOW, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait
from real_time_manim.record import fast_record_scene, record_scene

class MLWindowDemo(Scene):
    SIZE = "MLWindow(960, 540)  hidden=True"   # window parameters: size + whether hidden
    W, H = 960, 540   # window size: any other value is force-corrected to 1920x1080

    def construct(self):
        win = MLWindow(self.W, self.H)   # create an RTM window: "w" / "h" are exactly these two parameters
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        label = Text(self.SIZE, font_size=38, color=YELLOW).to_edge(UP)   # show this set of window parameters on screen
        sq = Square(side_length=1.8, color=BLUE).set_fill(BLUE, 0.5).set_stroke(width=4)   # blue square
        self.add(label)   # put the label into the scene
        win.play(Create(sq), run_time=0.8)   # draw the square
        win.play(sq.animate.scale(1.2), run_time=0.6)   # scale the square up
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


class MLWindowBig(MLWindowDemo):
    SIZE = "MLWindow(3840, 2160)  hidden=False"   # request 4K + visible window: still force-corrected to 1920x1080
    W, H = 3840, 2160   # 4K size: only used to trigger the forced-correction hint


if __name__ == "__main__" and ("mlwindow" in sys.argv[1:] or not sys.argv[1:]):
    fast_record_scene(MLWindowDemo, out_path="mlwin_small.mp4", hidden=True, verbose=True)   # hidden=True: the window never pops up
    fast_record_scene(MLWindowBig, out_path="mlwin_big.mp4", hidden=False, verbose=True)   # hidden=False: pop up a window while rendering
```

What this code does: `MLWindowDemo` prints the `MLWindow(960, 540)` request on the label, and `MLWindowBig` requests `MLWindow(3840, 2160)`; the two recordings use `hidden=True` (no popup) once and `hidden=False` (pops up) once.

The console prints one forced-correction hint each; in the video the two clips are completely the same except for the label text: a request for 540p gets 1080p, a request for 4K still gets 1080p, and whether a window pops up does not affect the picture.

<video src="assets/RTM output/05-RTM-Record-and-Window-Options-mlwindow.mp4" controls width="560"></video>

> Note:
>
> - Stop trying to tune the resolution — RTM has only the single 1920×1080@60 output (hard-coded in the source as `SUPPORTED_WIDTH/HEIGHT/FPS`, the reason being that small windows hide resolution-related bugs). If you want low resolution, downscale with ffmpeg after rendering.
> - With `hidden=False` the window steals focus, and it closes automatically after recording.

### `MLWindow.enable_fast_record(...)` (the low-level recording entry point)

```python
def enable_fast_record(self, path, fps=60, segment=None, hidden=True, count_only=False):
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `path` | `str` | —(required) | the MP4 output path (pipe mode), or the BMP frame directory in `segment` mode |
| `fps` | `int` | `60` | frame rate; anything other than 60 is forced to `SUPPORTED_FPS` and a hint is printed |
| `segment` | `tuple \| None` | `None` | `(start_frame, end_frame)` → BMP directory mode |
| `hidden` | `bool` | `True` | hide the window (on win32 `ShowWindow(SW_HIDE)`) |
| `count_only` | `bool` | `False` | count frames only: no capture, no GPU rendering |

Inside `fast_record_scene` this is exactly what is called after creating an `MLWindow`; **the encoding finish-up is done by the `close` wrapped by the `record._AutoRecord` installed by `fast_record_scene` / `record_scene`, which first calls `_finish_fast_record()` (or `stop_record()`), and then executes the real `MLWindow.close()`** (`record.py:181-186`, `window/recording.py:217-221`).

For everyday use `fast_record_scene` is enough; use this layer only when you need to control the window directly. The low-level counterpart of live recording is `win.start_record(path, fps=60)` ... `win.stop_record()` (this pair is what `record_scene` uses).

This section has no clip: each of its parameters shares the name and meaning of `fast_record_scene`, and the on-screen effect is in the corresponding samples above.

> Note: using this layer directly means you are responsible for the finish-up — `MLWindow.close()` itself **does no recording-encoding finish-up**, and **calling `enable_fast_record(...)` + `win.close()` by hand does not finish up**; you must call the internal `win._finish_fast_record()` (internal API, not needed in normal scenes). If you forget it (going through `fast_record_scene`, that means forgetting `win.close()`) the ffmpeg pipe is not closed, and the video is incomplete / does not exist.
>
> Also, the BMP file names written in `segment` mode start from `frame_000000.bmp`; sort them as needed.

**Summary**: three things produce a clip — pass the scene to `fast_record_scene` (or `record_scene` if you want a visible window), give the file to `out_path`, and recognise the frame as `MLWindow`'s 1920×1080; the frame rate is only 60, and every other `config`/command-line habit must be dropped.

The background colour is the only wired-up config key, see [01-Quality-and-Output](01-Quality-and-Output.md).

Clip status: `scene_forms` 342 frames / 5.70s, `out_path` 114 frames / 1.90s, `fps` 228 frames / 3.80s, `mlwindow` 228 frames / 3.80s aligned frame by frame; `record_scene` 130 frames / 2.17s.

---

See also: [01-Quality-and-Output](01-Quality-and-Output.md) | [03-Paths-and-Windows](03-Paths-and-Windows.md) | [04-ManimCE-CLI-Cheat-Sheet](04-ManimCE-CLI-Cheat-Sheet.md)
