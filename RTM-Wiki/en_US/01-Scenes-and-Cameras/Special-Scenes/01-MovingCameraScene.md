# MovingCameraScene (camera pan and zoom)

A scene whose camera can move: the view frame `self.camera.frame` is a `ScreenRectangle`, and animating it pans and zooms the shot. As long as `frame` moves, the whole scene counts as "in motion" and is redrawn frame by frame.

## Parameters

### class MovingCameraScene

```python
def __init__(self, camera_class: type[Camera] = MovingCamera, **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `camera_class` | `type[Camera]` | `MovingCamera` | camera class. **You can pass**: `MovingCamera` (default), `MultiCamera` (it also has a `frame`, plus one extra zoom camera), any other `Camera` subclass; **not recommended**: `Camera` — it has no `frame`, and the whole pan and zoom stops working |
| `**kwargs` | `Any` | — | forwarded to `Scene.__init__`; **only the four keywords below** may be passed (`camera_class` is already taken by the same-named parameter on the line above), anything else raises `TypeError` |

> **Returns**: none (constructs an instance).

The four keywords `**kwargs` accepts:

| Keyword | Type / Default | Accepted values | Worth changing? |
| --- | --- | --- | --- |
| `random_seed` | `int \| None` / `None` (takes `config.seed`) | any integer | you can change it; hard-code one number for reproducibility; frame differences are in the sample below |
| `always_update_mobjects` | `bool` / `False` | `True`, `False` | **not worth changing**: RTM drives updaters every frame, and both values render identically in testing |
| `skip_animations` | `bool` / `False` | `True`, `False` | **not worth changing**: RTM does not take manim's skip path, `animate` runs as usual, and the frames are identical in testing |
| `renderer` | `CairoRenderer \| OpenGLRenderer \| None` / `None` | normally leave empty | **not worth changing**: RTM handles the window and recording itself; a custom renderer has not been tried, so don't step on that rake |

#### Sample: changing `camera_class`

The view frame `self.camera.frame` only exists when `camera_class` is `MovingCamera` (the default); switch to a plain `Camera` and `frame` is gone, so the whole pan and zoom stops working.

```python
from real_time_manim import MovingCameraScene, MovingCamera, Camera, Square, Text, VGroup, \
    BLUE, RED, GREEN, YELLOW, DOWN, LEFT, RIGHT, ORIGIN, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class CameraClassDemo(MovingCameraScene):
    CAM = MovingCamera   # camera class: change it to "Camera" and rerun, the view frame disappears

    def __init__(self, **kwargs):
        super().__init__(camera_class=self.CAM, **kwargs)   # pass "camera_class" to Scene.__init__

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        left = Square(color=BLUE, side_length=2).shift(LEFT * 4)   # blue square on the left of the frame
        right = Square(color=RED, side_length=2).shift(RIGHT * 4)   # red square on the right of the frame
        head = VGroup(
            Text(type(self.camera).__name__, font_size=28, color=YELLOW),   # line 1: the current camera class name
            Text("frame=%s" % hasattr(self.camera, "frame"), font_size=22, color=GREEN),   # line 2: is there a view frame
        ).arrange(DOWN, buff=0.1)   # stack the two lines vertically
        head.move_to(left)   # put the two lines inside the left square; they scale up too when the camera zooms in
        self.add(left, right, head)   # add the three objects to the scene
        win.play(FadeIn(left), run_time=0.4)   # fade in the left square
        if hasattr(self.camera, "frame"):   # only "MovingCamera" has "frame"; a plain "Camera" never enters this branch
            win.play(self.camera.frame.animate.set(width=4.0).move_to(left), run_time=0.8)   # shrink the frame to 4 and move it left = zoom in
            win.play(self.camera.frame.animate.set(width=14.0).move_to(ORIGIN), run_time=0.8)   # grow the frame to 14 and recentre = zoom back out
        win.play(Wait(0.5))   # wait 0.5s
        win.close()   # close the RTM window
```

What this code does: it first opens an RTM window and binds the current scene to it, then puts one square on each side of the frame and places two lines of text — "which camera is in use" and "does this camera have a view frame" — inside the left square.

During playback it fades in the left square, then checks whether `self.camera` has a `frame`: if so, it shrinks the frame to 4 and moves it to the left square (zoom in), then grows it to 14 and recentres (zoom back out); if not, it does nothing and just waits 0.5s. So change `CAM` to `Camera`, rerun, and the pan and zoom never happens, while the two lines go from `frame=True` to `frame=False`.

<video src="assets/RTM output/01-MovingCameraScene-camera_class.mp4" controls width="560"></video>

> Note: `MLWindow(960, 540)` is forcibly corrected to 1920×1080 and prints one line; it is not an error, so don't change the size.
>
> The two labels sit **inside** the square (world coordinates), so they scale up along with it when the camera zooms in — which is exactly the proof that "the camera really is moving".
>
> Also, after switching to `Camera` the `self.camera.frame` does not exist, and the sample falls back on the `hasattr` branch — if your own code writes `self.camera.frame` directly, it raises `AttributeError`.

#### Sample: changing `**kwargs`

`**kwargs` is handed to `Scene.__init__` as-is. `random_seed` changes the random sequence, which is directly visible; in testing `always_update_mobjects` / `skip_animations` do not change RTM's frames (see the `**kwargs` table at the start of this section).

```python
import random

from real_time_manim import MovingCameraScene, Square, Text, VGroup, \
    BLUE, RED, GREEN, YELLOW, WHITE, UP, DOWN, LEFT, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class RandomSeedDemo(MovingCameraScene):
    SEED = 1   # random seed: change it to 7 and rerun, the color order of the row of squares changes

    def __init__(self, **kwargs):
        super().__init__(random_seed=self.SEED, **kwargs)   # forward "random_seed" to Scene.__init__

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        tag = Text("random_seed=%d" % self.SEED, font_size=40, color=YELLOW).to_edge(UP)   # show the current seed at the top of the screen
        order = [0, 1, 2, 3, 4]   # prepare an index list 0~4
        random.shuffle(order)   # shuffle; the result is decided by the constructor parameter "random_seed"
        colors = [BLUE, RED, GREEN, YELLOW, WHITE]   # five colors
        g = VGroup(*[Square(color=colors[i], side_length=0.9) for i in order])   # build squares from the shuffled indices
        g.arrange(RIGHT, buff=0.3).to_edge(DOWN)   # one row from left to right; color order = shuffle order
        self.add(tag, g)   # add the label and the row of squares to the scene
        print("random_seed=%d shuffled order =" % self.SEED, order)   # print the order to the console for comparison
        win.play(FadeIn(g), run_time=0.5)   # fade in the whole row
        win.play(Wait(0.5))   # wait 0.5s
        win.close()   # close the RTM window
```

What this code does: it shuffles `[0, 1, 2, 3, 4]` with the random sequence decided by `random_seed`, then fades in five colored squares arranged left to right in the shuffled order, while the current seed shows at the top of the screen and the shuffle result is also printed to the console.

The scene has no other source of randomness, so the color order of the row is decided entirely by the single number `random_seed`.

<video src="assets/RTM output/01-MovingCameraScene-random_seed.mp4" controls width="560"></video>

> Note: `random_seed` only affects the random numbers, not the animation itself; hard-code `SEED` if you want every run to come out identical, and another integer gives another arrangement. Also, `Square` is stroke-only by default with no fill; for a solid one add `.set_fill(color, 0.6)` yourself.

With only this one number changed in the same scene, the two videos differ pixel for pixel — while changing only the other parameters (such as `always_update_mobjects`, `skip_animations`) makes RTM output two frames that are byte-identical:

| `**kwargs` | RTM measurement |
| --- | --- |
| `random_seed` | the frames change with the seed (table above) |
| `always_update_mobjects` | no difference: RTM drives updaters every frame, unlike manim's "a still Wait freezes everything" |
| `skip_animations` | no difference: RTM does not take manim's skip path, `animate` runs as usual |

### self.camera.frame (the view frame)

**What it does**: the camera's view-frame mobject (`ScreenRectangle`). Calling `save_state()` / `animate.set(width=...)` / `Restore(...)` on it pans and zooms the shot; it is provided by `MovingCamera` and has no constructor parameter of its own.

The properties you can read and write directly are below (changing them with `.animate` produces camera motion):

| Parameter | Type | Default | Accepted values | Worth changing? |
| --- | --- | --- | --- | --- |
| `width` | `float` | `14.222` | any positive number, commonly `2` ~ `14` | you can change it (zooming is exactly this); don't make it so small that not a single object fits, or the whole screen goes black |
| `height` | `float` | `8.0` | any positive number | **not worth setting directly**: `width` / `height` are locked to 16:9, change one and the other follows automatically (`width=4` → `height=2.25`) |
| position (`move_to()` / `shift()`) | `Point3DLike` | `[0, 0, 0]` (frame centre) | any coordinates | you can change it (panning is exactly this); note that `center()` is a method and cannot be assigned to |

**Returns**: the property itself is a `ScreenRectangle`; you can read and write its position and size (default `height=8.0`, `width=14.222`).

#### Sample: `self.camera.frame`

`set(width=...)` only changes the zoom and `move_to(...)` only changes the centre — the two jobs are clearly separated; `save_state()` + `Restore(...)` pulls the camera back to the initial full view.

```python
from real_time_manim import MovingCameraScene, Square, Text, \
    BLUE, RED, WHITE, UP, DOWN, LEFT, RIGHT, Restore
from real_time_manim.vulkan_bind import MLWindow, Wait

class FrameDemo(MovingCameraScene):
    WIDTH = 4.0   # view-frame width: set it to 2.0 for a closer step, 14.0 for the full view

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        a = Square(color=BLUE, side_length=1.5).shift(LEFT * 1.5)   # the left target
        b = Square(color=RED, side_length=1.5).shift(RIGHT * 1.5)   # the right target
        t = Text("width=%.1f" % self.WIDTH, font_size=32, color=WHITE)   # show the current view-frame width

        def pin(m):   # keep the label at the bottom of the view frame and scale it with the frame width, so its on-screen size never changes
            m.width = self.camera.frame.width * 0.28
            m.move_to(self.camera.frame.get_bottom() + UP * (
                m.height * 0.5 + self.camera.frame.height * 0.08))

        t.add_updater(pin)   # pin the width label to the bottom of the view frame
        self.add(a, b, t)   # add the three objects to the scene
        print("initial frame: height=%.3f width=%.3f" % (
            self.camera.frame.height, self.camera.frame.width))   # default height 8.0, width 14.222
        self.camera.frame.save_state()   # remember the current (full-view) state so Restore can bring it back later
        win.play(self.camera.frame.animate.set(width=self.WIDTH), run_time=0.8)   # change only the width = zoom only, the frame centre does not move
        win.play(self.camera.frame.animate.move_to(a), run_time=0.8)   # change only the centre = pan only, the zoom does not change
        print("after frame: height=%.3f width=%.3f" % (
            self.camera.frame.height, self.camera.frame.width))   # the width is still the value set above, the centre has moved to a
        win.play(Restore(self.camera.frame), run_time=0.8)   # back to the full view from save_state
        win.play(Wait(0.5))   # wait 0.5s
        win.close()   # close the RTM window
```

What this code does: it first puts one square on each side and a width label that follows the camera at the bottom, and prints the view frame's initial size (`height=8.0`, `width=14.222`), then `save_state()` remembers the full view.

After that it takes three steps in order — change only `width` (the frame centre does not move, only the zoom), change only `move_to` (the zoom does not change, only the pan), and `Restore` to return to the original full view in one go, then wait 0.5s and finish. The console prints the size before and after the zoom, where you can see the width becomes `WIDTH` and the height follows automatically at 16:9.

<video src="assets/RTM output/01-MovingCameraScene-camera_frame.mp4" controls width="560"></video>

> Note: the view frame is 16:9, so `set(width=...)` computes `height` for you (`width=4` → `height=2.25`); therefore do **not** change `height` yourself, or the aspect ratio breaks.
>
> Don't zoom in too hard either — when `width` is so small that not a single object fits, the whole screen is black; the sample puts the two squares at `±1.5` precisely so that something is still in the frame at `width=2.0`.
>
> The width label is pinned to the bottom of the view frame and scaled with the frame width, so it always looks the same size on screen however you zoom.

The three view-frame widths render three visibly different frames; in each clip `move_to(a)` moves only the centre and `Restore` resets both the zoom and the centre.

---

See also: [MovingCamera](../Cameras/02-MovingCamera.md), [ZoomedScene](03-ZoomedScene.md), [Scene Basics](../Scenes/01-Scene-Basics.md)
