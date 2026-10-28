# Scene basics

An RTM script = a class that subclasses `Scene` + an overridden `construct()`. `setup()` runs first, to prepare shared objects; `construct()` runs next, and all your animation goes here.

RTM drives this process directly from the record module — it does not go through the `manim` command line, nor through `Scene.render`.

## Parameters

### class Scene (`__init__`)

```python
def __init__(self, renderer: CairoRenderer | OpenGLRenderer | None = None, camera_class: type[Camera] = Camera, always_update_mobjects: bool = False, random_seed: int | None = None, skip_animations: bool = False) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `renderer` | `CairoRenderer \| OpenGLRenderer \| None` | `None` | **do not pass**: RTM takes over the window and recording itself, so a custom renderer is meaningless |
| `camera_class` | `type[Camera]` | `Camera` | the camera class this scene uses. **accepts** any `Camera` subclass; special scenes swap it in automatically (e.g. [MovingCameraScene](../Special-Scenes/01-MovingCameraScene.md) uses `MovingCamera`); you normally don't pass it by hand |
| `always_update_mobjects` | `bool` | `False` | **not advisable to change**: it only affects RTM's decision about a "static Wait" (freeze or step frame counting); measured output shows no difference |
| `random_seed` | `int \| None` | `None` (takes `config.seed`) | random seed; hard-code a number for reproducibility. **accepts** any integer; the picture changes with the seed (see the sample) |
| `skip_animations` | `bool` | `False` | **not advisable to change**: RTM does not take manim's skip path, `animate` runs as usual; measured output shows no difference |

> **Returns**: none (constructs an instance). **Do not** recklessly override `__init__` in your own scene: only override it when you need to pass constructor parameters (such as `random_seed`), and forward `super().__init__(...)`; put any other setup in `setup()`.

#### Sample: the `Scene.__init__` constructor parameters

Of the five parameters only `random_seed` is directly visible: change just that one number in the same scene and the color arrangement of the five squares changes. The current values of `camera_class` / `always_update_mobjects` / `skip_animations` are also printed on screen.

```python
import random

from real_time_manim import (
    Scene,
    Square, Text, VGroup,
    BLUE, RED, GREEN, YELLOW, WHITE,
    UP, DOWN, LEFT, RIGHT,
    FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class CtorDemo(Scene):
    SEED = 1   #random seed: change it to 7 and run again; the color order of the five squares changes

    def __init__(self, **kwargs):
        super().__init__(random_seed=self.SEED, **kwargs)   #pass "random_seed" to Scene.__init__

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        info = VGroup(
            Text("random_seed=%d" % self.SEED, font_size=36, color=YELLOW),
            Text("camera_class=%s" % type(self.camera).__name__, font_size=28, color=WHITE),
            Text("always_update_mobjects=%s  skip_animations=%s" % (
                self.always_update_mobjects, self.skip_animations), font_size=22, color=GREEN),
        ).arrange(DOWN, buff=0.15).to_edge(UP)   #three label lines: print the current constructor parameter values on screen
        order = [0, 1, 2, 3, 4]   #prepare an index list 0..4
        random.shuffle(order)   #shuffle; the result is determined only by "random_seed"
        colors = [BLUE, RED, GREEN, YELLOW, WHITE]   #five colors
        row = VGroup(*[Square(color=colors[i], side_length=0.9) for i in order])   #create squares in the shuffled index order
        row.arrange(RIGHT, buff=0.3).to_edge(DOWN)   #arrange left to right in a row; color order = shuffle order
        self.add(info, row)   #add the labels and this row of squares to the scene
        win.play(FadeIn(row), run_time=0.5)   #fade in the whole row
        win.play(Wait(0.5))   #wait 0.5s
        win.close()   #close the RTM window
```

What this code does: it overrides `__init__` to pass `SEED` to `Scene.__init__`'s `random_seed`; then in `construct` it uses the random sequence determined by that seed to shuffle `[0, 1, 2, 3, 4]` and fade in a row of five colored squares in the shuffled order. The top of the screen shows the current `random_seed`, `camera_class` and the other two boolean parameters.

The whole scene has no other source of randomness, so the color order of this row is decided entirely by the single number `random_seed` — the first half of the video is `SEED = 1` (green, yellow, white, blue, red) and the second half is `SEED = 7` (white, blue, yellow, red, green).

<video src="assets/RTM output/01-Scene-Basics-ctor.mp4" controls width="560"></video>

> Note: `random.seed` / `np.random.seed` are already seeded inside `Scene.__init__`, and any random call in your code afterwards consumes that seed; to get the exact same result every run, hard-code `SEED`.
>
> The default is `camera_class=Camera`, which is the `Camera` shown on screen; for a special camera such as `MovingCamera` see [MovingCamera](../Cameras/02-MovingCamera.md).

### Scene lifecycle: `Scene.setup` / `Scene.construct` / `Scene.tear_down`

```python
def setup(self) -> None:
def construct(self) -> None:
def tear_down(self) -> None:
```

| Method | When it runs | RTM calls it? | Description |
| --- | --- | --- | --- |
| `setup()` | before `construct()` | yes | no parameters, no return value. Put shared-object preparation here (squares, plots, camera setup); it is also what initializes subclasses such as `MovingCameraScene` and `ZoomedScene` |
| `construct()` | after `setup()` | yes | no parameters, no return value. All your animation code goes here: put things on screen with `add(...)`, play animations with `win.play(...)`, take them off with `remove(...)` |
| `tear_down()` | when the scene wraps up | yes | no parameters, no return value. manim calls it at the end of `Scene.render()`; RTM calls it from the record lifecycle (`scene_lifecycle` in `real_time_manim/record.py`) inside try/finally, guaranteeing it runs **once** on both the normal and the exception path, and it only runs your hook without triggering the file writer's second cleanup (verified by pytest `tests/test_gap_wait_timeline.py`). You can also put wrap-up cleanup at the end of `construct()` (even after `win.close()`) |

#### Sample: script skeleton (setup → construct)

The square prepared in `setup` is drawn in `construct`, which proves `setup` really runs first; the print in `tear_down` shows up when the scene wraps up.

```python
from real_time_manim import Scene, Square, Text, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class LifeDemo(Scene):
    def setup(self):
        self.square = Square(color=BLUE)   #setup runs before construct; use it to prepare shared objects

    def tear_down(self):
        print("tear_down ran")   #(RTM calls this too since 2026-10-16: the record lifecycle's try/finally guarantees one run)

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        title = Text("setup -> construct", font_size=40, color=YELLOW).to_edge(UP)   #on-screen title
        self.add(title)   #add the title to the scene
        win.play(Create(self.square), run_time=0.8)   #draw the square prepared in setup()
        win.play(Wait(0.5))   #wait 0.5s
        win.close()   #close the RTM window
```

What this code does: `setup()` creates a blue square and keeps it on `self.square`; `construct()` opens an RTM window, puts a title line up, then draws that square with `Create` and finally waits 0.5 seconds to finish.

That the square can be drawn proves `setup()` runs before `construct()`. `tear_down()` runs when the scene wraps up and prints `tear_down ran` to the console — run it once to verify.

<video src="assets/RTM output/01-Scene-Basics-life.mp4" controls width="560"></video>

> Note: `MLWindow(960, 540)` is forcibly corrected to 1920×1080 and prints a hint line; this is not an error, and you don't need to change the size.
>
> Put any preparation shared by several scenes in `setup()` — RTM added a dedicated lifecycle call for it, and `MovingCameraScene`'s viewfinder `self.camera.frame` is created in `setup()`.

### `Scene.render`

```python
def render(self, preview: bool = False) -> bool:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `preview` | `bool` | `False` | when `True`, opens the file viewer after rendering |

Returns `bool` (`True` means the scene needs to be re-run).

**RTM does not go through `Scene.render`**: the record module (`fast_record_scene` / `record_scene`) drives the scene directly as `setup` → `construct` and takes over recording, so the wrap-up in `render` (the file writer's `finish`, "open file viewer") never happens — `tear_down` is now called by the record lifecycle at wrap-up instead (see the previous section). No video is produced; to get output use `fast_record_scene(...)` from [Recording video](../../00-Getting-Started/04-Recording-Video.md).

### `Scene.camera` / `Scene.time`

```python
@property
def camera(self) -> Camera | OpenGLCamera: ...
@property
def time(self) -> float: ...
```

| Attribute | Type | Default | Description |
| --- | --- | --- | --- |
| `self.camera` | `Camera \| OpenGLCamera` | an instance of `camera_class` | a directly readable attribute: the current scene's camera object. Pan/zoom/tilt is just changing its state (e.g. `self.camera.frame`); see [Camera](../Cameras/01-Camera.md) |
| `self.time` | `float` | accumulates with emitted frames | **usable**: every frame drawn adds that frame's `dt` (matching manim's `add_frame` semantics; a frame not drawn adds nothing). To know "how many seconds have played" read it directly, or accumulate `run_time` yourself |

#### Sample: reading `Scene.time` frame by frame

The square moves and time passes while the label refreshes every frame — direct evidence that `self.time` accumulates with emitted frames.

```python
from real_time_manim import Scene, Square, Text, UP, DOWN, RIGHT, linear
from real_time_manim.vulkan_bind import MLWindow, Wait

class TimeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=GREEN).shift(DOWN)   #a square that moves, proving time really passes
        label = Text("scene.time = 0.00", font_size=40, color=YELLOW).to_edge(UP)   #label showing self.time

        def show_time(m):   #refresh "self.time" into the label every frame
            m.become(Text("scene.time = %.2f" % self.time, font_size=40, color=YELLOW).to_edge(UP))

        label.add_updater(show_time)   #mobject-level updater: RTM drives it every frame
        self.add(sq, label)   #add the square and the label to the scene
        win.play(sq.animate.shift(RIGHT * 4), run_time=0.8, rate_func=linear)   #the square moves right at constant speed
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: it attaches a mobject-level updater to the label that refreshes `self.time` into text every frame; meanwhile the square moves right at constant speed for 0.8 seconds, so time runs and the label climbs along with it.

`self.time` reads the renderer's accumulating clock: each frame the Timeline draws adds one frame's `dt` to `renderer.time` (frames not drawn don't count), the same semantics as manim's `add_frame`.

<video src="assets/RTM output/01-Scene-Basics-time.mp4" controls width="560"></video>

> Note: when you need "which second are we at now", read `self.time` directly (it accumulates once per drawn frame, and doesn't advance when a frame isn't drawn); to show it on screen, refresh a `Text` with an updater as in the sample, or use a `ValueTracker` to turn time into a visible value.
>
> `self.camera` is fully usable: it is an ordinary camera object, and operations like changing `frame` or `set(width=...)` are all recognized by RTM.
---

See also: [Displaying content](02-Displaying-Content.md) · [Play and wait](03-Play-and-Wait.md) · [First scene](../../00-Getting-Started/02-First-Scene.md) · [Recording video](../../00-Getting-Started/04-Recording-Video.md)
