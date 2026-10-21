# ZoomedScene (picture-in-picture zoom scene)

A picture-in-picture zoom scene: a subclass of `MovingCameraScene` with a built-in "zoom camera" (`self.zoomed_camera`, itself a `MovingCamera`) and a small window that shows the zoomed result (`self.zoomed_display`); `setup()` creates both objects automatically.

Once zooming is on, the small window keeps showing what the zoom camera captures — put the view frame over a small target and that target grows in the window. In RTM testing the whole picture-in-picture chain works (including the `animate=True` entrance animation and manual sequencing).

## Parameters

### class ZoomedScene

```python
def __init__(self, camera_class: type[Camera] = MultiCamera, zoomed_display_height: float = 3, zoomed_display_width: float = 3, zoomed_display_center: Point3DLike | None = None, zoomed_display_corner: Vector3D = UP + RIGHT, zoomed_display_corner_buff: float = DEFAULT_MOBJECT_TO_EDGE_BUFFER, zoomed_camera_config: dict[str, Any] = {"default_frame_stroke_width": 2, "background_opacity": 1}, zoomed_camera_image_mobject_config: dict[str, Any] = {}, zoomed_camera_frame_starting_position: Point3DLike = ORIGIN, zoom_factor: float = 0.15, image_frame_stroke_width: float = 3, zoom_activated: bool = False, **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `camera_class` | `type[Camera]` | `MultiCamera` | main camera class. **Not recommended** to change: registering the small window into the main camera relies on `MultiCamera`'s `add_image_mobject_from_camera` |
| `zoomed_display_height` | `float` | `3` | zoom window height (screen space, no proportional relation to the main frame); **accepts** any positive number |
| `zoomed_display_width` | `float` | `3` | zoom window width; **accepts** any positive number, sample 2 uses `4` |
| `zoomed_display_center` | `Point3DLike \| None` | `None` | centre coordinate of the small window; when `None` (the default) it is positioned by `corner`, normally leave empty |
| `zoomed_display_corner` | `Vector3D` | `UP + RIGHT` | which corner the small window sits in; **accepts** `UP + RIGHT` (top right, default), `DOWN + LEFT` (bottom left) and other direction combinations |
| `zoomed_display_corner_buff` | `float` | `DEFAULT_MOBJECT_TO_EDGE_BUFFER` (`0.4`) | gap between the small window and the corner; **accepts** positive numbers, sample 2 uses `0.3` |
| `zoomed_camera_config` | `dict` | `{"default_frame_stroke_width": 2, "background_opacity": 1}` | configuration of the zoom camera (view frame), normally leave alone |
| `zoomed_camera_image_mobject_config` | `dict` | `{}` | configuration of the small window's image `ImageMobject`, normally leave empty |
| `zoomed_camera_frame_starting_position` | `Point3DLike` | `ORIGIN` | initial position of the zoom view frame (decides what is zoomed right after it is switched on); you can change it, but the samples move it on the spot with `frame.move_to()` |
| `zoom_factor` | `float` | `0.15` | the reciprocal of the zoom factor: view-frame size = small window × `zoom_factor`, so **the smaller, the bigger the zoom**; **accepts** `0.05` ~ `0.5`, the samples contrast `0.15` and `0.08` |
| `image_frame_stroke_width` | `float` | `3` | stroke width of the small window's white border; **accepts** `0` (no border) ~ `6` |
| `zoom_activated` | `bool` | `False` | **not recommended to set by hand**: managed by `activate_zooming()`; setting it to `True` manually only skips the registration step and fails outright |
| `**kwargs` | `Any` | — | forwarded to `MovingCameraScene.__init__` (the view frame and so on, see [MovingCameraScene](01-MovingCameraScene.md)) |

> **Returns**: none (constructs an instance).

#### Sample: changing the constructor parameters

The same scene and the same set of animations, with only four constructor parameters swapped: the default step (`0.15`, `3×3`, top-right) and a harsher one (`0.08`, `4×2.5`, bottom-left).

```python
from real_time_manim import ZoomedScene, Text, VGroup, Dot, \
    UP, DOWN, LEFT, RIGHT, YELLOW, GREEN, RED
from real_time_manim.vulkan_bind import MLWindow, Wait

def make_target():   # a "small and dense" target: small text and dots, unreadable without zooming
    return VGroup(
        Text("RTM", font_size=22, color=YELLOW),   # very small title text
        Dot(radius=0.04, color=GREEN),              # two small dots
        Dot(radius=0.04, color=RED).shift(RIGHT * 0.18),
    ).arrange(DOWN, buff=0.1).shift(LEFT * 2 + DOWN * 0.8)   # place it lower-left of centre in the frame

class ZoomBase(ZoomedScene):
    LABEL = ""   # subclasses fill in this clip's title text
    KW = {}      # subclasses fill in the constructor parameters to pass to ZoomedScene.__init__

    def __init__(self, **kwargs):
        super().__init__(**self.KW, **kwargs)   # pass the keys in "KW" to ZoomedScene.__init__

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        target = make_target()   # the small target to zoom in on
        self.add(target)   # add it to the scene (it is too small to read here)
        cap = Text(self.LABEL, font_size=28, color=YELLOW).to_edge(UP)   # top title shows the current constructor parameters
        self.add(cap)   # add it to the scene (in a 2D scene text is pinned to the screen by default)
        self.activate_zooming(animate=False)   # switch zooming on: the small window appears instantly, no animation
        self.zoomed_camera.frame.move_to(target)   # put the magnifier's view frame over the target
        win.play(Wait(0.8))   # pause 0.8s to see the zoomed result
        win.play(target.animate.shift(RIGHT * 1.2), run_time=1.2)   # move the target right, out of the view frame
        win.play(self.zoomed_camera.frame.animate.move_to(target), run_time=0.8)   # the view frame follows it
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window


class ZoomA(ZoomBase):
    LABEL = "zoom_factor=0.15 display 3x3 corner=UP+RIGHT"   # the default step: frame at 15%
    KW = {"zoom_factor": 0.15,
          "zoomed_display_height": 3, "zoomed_display_width": 3,
          "zoomed_display_corner": UP + RIGHT}


class ZoomB(ZoomBase):
    LABEL = "zoom_factor=0.08 display 4x2.5 corner=DOWN+LEFT"   # the harsher step: frame at 8% = about 12x zoom
    KW = {"zoom_factor": 0.08,
          "zoomed_display_height": 2.5, "zoomed_display_width": 4,
          "zoomed_display_corner": DOWN + LEFT, "zoomed_display_corner_buff": 0.3}
```

What this code does: each clip places a target too small to read (small text + two small dots), `activate_zooming(animate=False)` makes the small window appear instantly, and then the zoom view frame `move_to`s over the target — the small window immediately shows the zoomed picture. Next the target moves right out of the view frame (the window goes blank), and the view frame `animate.move_to`s after it to line up again.

The only difference between the two clips is the constructor parameters: the first is the default step `0.15` / `3×3` / top-right, the second is `0.08` / `4×2.5` / bottom-left flush at `0.3`, about 12x zoom.

<video src="assets/RTM output/03-ZoomedScene-zoom.mp4" controls width="560"></video>

> Note: `zoom_factor` is "the view frame relative to the small window", so **the smaller, the bigger the zoom** (`0.15` ≈ 6.7x, `0.08` ≈ 12.5x), not "zoom 0.15x".
>
> The view frame `self.zoomed_camera.frame` is just `MovingCamera`'s view frame; `.animate.move_to(...)` on it makes the magnifier follow the target (letting the target slide out first and then having the frame catch up is the proof that the view frame is moving).
>
> The width and height of the small window have no proportional relation to the main frame at all, so put in whatever; changing the corner only changes `zoomed_display_corner`.

### ZoomedScene.activate_zooming

```python
def activate_zooming(self, animate: bool = False) -> None:
```

Enables zooming: it registers the small window into the main camera, puts it on the foreground layer, and sets `zoom_activated` to `True`. Only after that is `self.zoomed_camera.frame` "the magnifier's view frame", and `animate`-ing it chooses where to zoom.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `animate` | `bool` | `False` | `False`: the small window appears in one frame; `True`: it first plays "camera pushes in" and then "small window pops out" as two entrance animations (internally `self.play`, so under RTM set `self.play = win.play` first) |

> **Returns**: none.

#### Sample: changing `activate_zooming(animate)`

The same scene with only the `animate` parameter swapped, run as two clips: instant appearance vs. with entrance animations.

```python
from real_time_manim import ZoomedScene, Text, VGroup, Dot, \
    UP, DOWN, LEFT, RIGHT, YELLOW, GREEN, RED
from real_time_manim.vulkan_bind import MLWindow, Wait

def make_target():   # a "small and dense" target: small text and dots, unreadable without zooming
    return VGroup(
        Text("RTM", font_size=22, color=YELLOW),   # very small title text
        Dot(radius=0.04, color=GREEN),              # two small dots
        Dot(radius=0.04, color=RED).shift(RIGHT * 0.18),
    ).arrange(DOWN, buff=0.1).shift(LEFT * 2 + DOWN * 0.8)   # place it lower-left of centre in the frame

class ZoomActivateBase(ZoomedScene):
    ANIMATE = False   # subclasses change it to True to see the small window's entrance animation
    LABEL = ""        # subclasses fill in this clip's title text

    def __init__(self, **kwargs):
        super().__init__(zoom_factor=0.15, **kwargs)   # both classes share the same zoom_factor and compare only animate

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # with animate=True, activate_zooming calls self.play internally, so wire it to the window first
        target = make_target()   # the small target to zoom in on
        self.add(target)   # add it to the scene
        cap = Text(self.LABEL, font_size=28, color=YELLOW).to_edge(UP)   # top title shows the value of animate
        self.add(cap)   # add it to the scene
        self.activate_zooming(animate=self.ANIMATE)   # False = the small window appears instantly; True = push the camera in first, then pop the window out
        self.zoomed_camera.frame.move_to(target)   # put the magnifier's view frame over the target
        win.play(Wait(0.8))   # pause 0.8s to see the zoomed result
        win.close()   # close the RTM window


class ZoomNoAnim(ZoomActivateBase):
    ANIMATE = False   # the small window appears directly
    LABEL = "activate_zooming(animate=False)"


class ZoomAnim(ZoomActivateBase):
    ANIMATE = True   # play the entrance animations
    LABEL = "activate_zooming(animate=True)"
```

What this code does: the base class fixes `zoom_factor` at `0.15` and lets only the subclasses switch `ANIMATE`. In the first clip `animate=False`: the small window appears in one frame and the view frame goes straight onto the target and starts zooming; in the second `animate=True`: it first plays "camera pushes in" (the view frame shrinks from full screen to the zoom size), then "small window pops out" (the window unfolds from the corner), and only after the animations finish does it line up on the target.

The two clips end with the same frame; the only difference is how the small window makes its entrance.

<video src="assets/RTM output/03-ZoomedScene-activate.mp4" controls width="560"></video>

> Note: with `animate=True`, `activate_zooming` plays two animations in a row, so under RTM you must first write `self.play = win.play`, or the animations will not play.
>
> Before `activate_zooming` the small window is not yet registered into the main camera and cannot be seen in the frame at all, so `frame.move_to(target)` must come **after** it. The two subclasses differ by a single boolean, so you can switch `ANIMATE` and rerun them side by side.

### get_zoom_in_animation / get_zoomed_display_pop_out_animation / get_zoom_factor

They return the "camera pushes in" animation, the "small window pops out" animation, and the current zoom ratio respectively; when you want to sequence the entrance yourself, use this trio instead of `activate_zooming(animate=True)`.

```python
def get_zoom_in_animation(self, run_time: float = 2, **kwargs: Any) -> ApplyMethod:
def get_zoomed_display_pop_out_animation(self, **kwargs: Any) -> ApplyMethod:
def get_zoom_factor(self) -> float:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `run_time` | `float` | `2` | duration of the push-in animation (`get_zoom_in_animation` only, the sample uses `1.2`) |
| `**kwargs` | `Any` | — | forwarded to `ApplyMethod` (both animation methods accept it, e.g. `run_time=0.8`) |

> **Returns**: the two animation methods return `ApplyMethod` (hand it to `win.play` to play); `get_zoom_factor` returns the `float` zoom ratio (no parameters), measured as `= view-frame height ÷ small-window height`, matching the constructor parameter `zoom_factor`.

#### Sample: hand-rolling `get_zoom_in_animation`

Do the three steps inside `activate_zooming(animate=True)` by hand, fully controlling the pacing, and print `get_zoom_factor()` at the end.

```python
from real_time_manim import ZoomedScene, Text, VGroup, Dot, \
    UP, DOWN, LEFT, RIGHT, YELLOW, GREEN, RED
from real_time_manim.vulkan_bind import MLWindow, Wait

def make_target():   # a "small and dense" target: small text and dots, unreadable without zooming
    return VGroup(
        Text("RTM", font_size=22, color=YELLOW),   # very small title text
        Dot(radius=0.04, color=GREEN),              # two small dots
        Dot(radius=0.04, color=RED).shift(RIGHT * 0.18),
    ).arrange(DOWN, buff=0.1).shift(LEFT * 2 + DOWN * 0.8)   # place it lower-left of centre in the frame

class ManualZoomDemo(ZoomedScene):
    def __init__(self, **kwargs):
        super().__init__(zoom_factor=0.15, **kwargs)   # the default 0.15 step

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # all the animations sequenced by hand below go through win.play
        target = make_target()   # the small target to zoom in on
        self.add(target)   # add it to the scene

        # do the three steps of activate_zooming(animate=True) by hand, pacing them yourself:
        self.renderer.camera.add_image_mobject_from_camera(self.zoomed_display)   # (1) register the small window into the main camera
        win.play(self.get_zoom_in_animation(run_time=1.2))   # (2) "camera pushes in": the view frame shrinks from full screen to the zoom size
        win.play(self.get_zoomed_display_pop_out_animation(run_time=0.8))   # (3) "small window pops out": it unfolds from the window's position
        self.add_foreground_mobjects(self.zoomed_camera.frame, self.zoomed_display)   # put the view frame and the small window on top

        ratio = self.get_zoom_factor()   # zoom ratio = zoom view-frame height / small-window height
        print("get_zoom_factor() =", ratio)   # print the zoom ratio to the console
        cap = Text("get_zoom_factor() = %.2f" % ratio,   # show a copy at the top as well
                   font_size=28, color=YELLOW).to_edge(UP)
        self.add(cap)   # add it to the scene
        self.zoomed_camera.frame.move_to(target)   # put the magnifier's view frame over the target
        win.play(Wait(0.8))   # pause 0.8s to see the zoomed result
        win.close()   # close the RTM window
```

What this code does: it takes `activate_zooming(animate=True)` apart and builds it itself — (1) `self.renderer.camera.add_image_mobject_from_camera(self.zoomed_display)` registers the small window into the main camera (this is the first thing `activate_zooming` does inside), (2) it plays `get_zoom_in_animation(run_time=1.2)` so the view frame shrinks from full screen to the zoom size, (3) it plays `get_zoomed_display_pop_out_animation(run_time=0.8)` so the small window pops out from the corner, and then `add_foreground_mobjects` puts the view frame and the small window on the top layer.

Then `get_zoom_factor()` prints the zoom ratio both to the console and at the top of the screen, and finally it lines up on the target to show the zoomed result.

<video src="assets/RTM output/03-ZoomedScene-manual.mp4" controls width="560"></video>

> Note: the order of the three steps cannot be shuffled — the small window must be registered before the two animations play, and finally `add_foreground_mobjects(...)` puts the view frame and the small window on the top layer, or the scene content presses on top of the small window.
>
> `get_zoom_in_animation` defaults to `run_time=2`; when sequencing by hand, pass your own value to match the pacing.
>
> `get_zoom_factor()` is measured to return `0.15`, exactly the value of the constructor parameter `zoom_factor` (view-frame height ÷ small-window height).

---

See also: [MovingCameraScene](01-MovingCameraScene.md), [MovingCamera](../Cameras/02-MovingCamera.md), [Scene Basics](../Scenes/01-Scene-Basics.md)
