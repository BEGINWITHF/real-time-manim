# MovingCamera (the movable camera)

A camera that follows the viewfinder `frame`: wherever the `frame` is and however large it is, the picture shows that piece of space. This page covers the camera's **own** constructor parameters, attributes and `auto_zoom`; animating the viewfinder for pan/zoom/tilt (`frame.animate`, `Restore`) is covered on the [MovingCameraScene](../Special-Scenes/01-MovingCameraScene.md) page.

## Parameters

### class MovingCamera (constructor parameters)

```python
def __init__(self, frame: Mobject | None = None, fixed_dimension: int = 0, default_frame_stroke_color: ManimColor = WHITE, default_frame_stroke_width: int = 0, **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `frame` | `Mobject \| None` | `None` → `ScreenRectangle(height=config.frame_height)` | the viewfinder mobject; **do not pass**: even if you do, `Camera.__init__` resets it to the default — at the end of construction it writes `frame_height`/`frame_width`/`frame_center` in turn, pulling a custom viewfinder back to 8.0×14.222 and moving it back to the origin; measured, passing it is as good as not passing it (byte-identical pictures in both engines) |
| `fixed_dimension` | `int` | `0` | which side is fixed when adjusting the frame (0 = derive height from width); **do not pass**: in 0.21 it is stored but unused (the code that reads it is commented out), so nothing you pass changes the picture |
| `default_frame_stroke_color` | `ManimColor` | `WHITE` | viewfinder stroke color; affects the viewfinder's own stroke: by default the frame is not in the scene and neither is drawn; when you explicitly `self.add(self.camera.frame)` and the stroke is visible, **RTM now draws it too** |
| `default_frame_stroke_width` | `int` | `0` | viewfinder stroke width; as above (default `0` = no pixel output, zero change to existing renders) |
| `**kwargs` | `Any` | — | forwarded to `Camera.__init__` (e.g. `background_color`, see [Camera](01-Camera.md)) |

**Returns**: none (constructs an instance). Common attributes (all readable/writable, see the next section): `frame_height`, `frame_width`, `frame_center`; `frame` itself is the viewfinder mobject (pan/zoom/tilt by changing it, see the MovingCameraScene page).

Why this section has no video: `frame` is pulled back to the default by `Camera.__init__` and `fixed_dimension` is stored but unused (both engines alike); the two stroke parameters only draw the viewfinder if you explicitly `add` `self.camera.frame` to the scene, and a frame with the default stroke width 0 and fill 0 produces no pixel output in either engine, so rendering a segment with the default values shows no difference.

Incidentally, `Scene`'s `camera_class` only takes a **class**, and the renderer builds the camera with a no-argument `camera_class()` call. To really pass constructor parameters you must use `functools.partial(MovingCamera, ...)` or a subclass overriding the defaults — not worth the effort for these parameters.

### MovingCamera.frame_height / frame_width / frame_center (properties)

```python
def frame_height(self) -> float:
def frame_height(self, frame_height: float) -> None:
def frame_width(self) -> float:
def frame_width(self, frame_width: float) -> None:
def frame_center(self) -> Point3D:
def frame_center(self, frame_center: Point3DLike | Mobject) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `frame_height` | `float` | `8.0` | current picture height (manim units); **accepts** any positive number; assigning it **together with** `frame_width` in a 16:9 pair is what gives a proportional zoom |
| `frame_width` | `float` | `14.222` | current picture width; **accepts** any positive number; changing it / `frame_height` on its own distorts the picture (see the note) |
| `frame_center` | `Point3DLike` or `Mobject` | `[0, 0, 0]` (picture center) | viewfinder center; **accepts** any coordinates, or you can pass a mobject directly (the camera pans to it) |

**Returns**: the getter returns `float` / `Point3D`; the setter returns nothing (takes effect immediately).

#### Sample: frame_height / frame_width / frame_center

```python
from real_time_manim import (
    BLUE, RED, WHITE, YELLOW,
    DOWN, LEFT, RIGHT, UP,
    Circle, Dot, FadeIn, MovingCameraScene, Square, Text, VGroup,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class FrameScaleDemo(MovingCameraScene):
    HEIGHT = 4.0   #the picture height you want to see: change it to 2.0 and run again to zoom in 4×

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        cam = self.camera   #MovingCameraScene's built-in movable camera
        a = Square(color=BLUE).set_stroke(width=4).shift(LEFT * 2.5)   #the target on the left
        b = Square(color=RED).set_stroke(width=4).shift(RIGHT * 2.5)   #the target on the right
        info = Text("frame: %.2f x %.2f" % (cam.frame_height, cam.frame_width),
                    font_size=28, color=WHITE).move_to(UP * 1.6)   #the viewfinder's height and width (placed inside the picture: after zooming in, an edge-hugging label goes off screen)
        self.add(a, b, info)   #add the two squares and the reading to the scene
        win.play(FadeIn(a, b), run_time=0.5)   #the two squares fade in: at this point still the default frame
        win.play(Wait(0.4))   #hold 0.4s
        cam.frame_height = self.HEIGHT   #change the height
        cam.frame_width = self.HEIGHT * 16 / 9   #change the width to match at 16:9: only a paired assignment gives a proportional zoom
        info.become(Text("frame: %.2f x %.2f" % (cam.frame_height, cam.frame_width),
                    font_size=28, color=WHITE).move_to(UP * 1.6))   #refresh the reading
        win.play(Wait(1.0))   #hold 1.0s to see the zoomed-in picture
        win.close()   #close the RTM window


class FrameCenterDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        cam = self.camera   #MovingCameraScene's built-in movable camera
        a = Square(color=BLUE).set_stroke(width=4).shift(LEFT * 4)   #the target on the left
        b = Square(color=RED).set_stroke(width=4).shift(RIGHT * 4)   #the target on the right
        info = Text("frame_center = ORIGIN", font_size=28, color=WHITE).to_edge(UP)   #viewfinder center
        self.add(a, b, info)   #add the two squares and the reading to the scene
        win.play(FadeIn(a, b), run_time=0.5)   #the two squares fade in
        win.play(Wait(0.4))   #hold 0.4s
        cam.frame_center = b   #move the viewfinder center onto the red square (a coordinate array is accepted too)
        info.become(Text("frame_center = red square", font_size=28, color=WHITE).to_edge(UP))   #refresh the reading
        win.play(Wait(1.0))   #hold 1.0s: the camera pans to the right
        win.close()   #close the RTM window
```

What this code does: the first segment first shows two squares 5 units apart at the default frame (`8.00 × 14.22`), then sets `frame_height` to 4.0 and `frame_width` to 7.11 at 16:9 — assigning both is what gives one clean proportional zoom, the picture instantly becomes a 2× close-up, and the reading refreshes in step.

The second segment demonstrates panning: `cam.frame_center = b` moves the whole viewfinder center onto the red square (this line also accepts a coordinate array, e.g. `cam.frame_center = [4, 0, 0]`), the picture pans right, the red square is centered and the blue square leaves the view.

<video src="assets/RTM output/02-MovingCamera-frame_props.mp4" controls width="560"></video>

> Note:
>
> - `frame_height`/`frame_width` are two **independent** setters — changing **one** on its own stretches the viewfinder away from 16:9: CE scales each of the two axes separately (distorting the picture), while RTM scales proportionally by height and ignores width entirely, so the two engines differ.
> - for a safe proportional zoom: assign the pair at 16:9 (as in the sample), or use `frame.animate.set(width=...)` (it locks to 16:9 automatically, see the MovingCameraScene page).
> - placing the reading text inside the picture (`move_to(UP * 1.6)`) is a small gotcha too: after zooming in, an edge-hugging `to_edge(UP)` text goes straight off screen.

### MovingCamera.auto_zoom(mobjects, margin, only_mobjects_in_frame, animate)

```python
def auto_zoom(self, mobjects: Iterable[Mobject], margin: float = 0, only_mobjects_in_frame: bool = False, animate: bool = True) -> _AnimationBuilder | Mobject:
```

Automatically aims the camera at a group of objects and zooms to exactly frame them. Only valid for 2D content in the XY plane (it is inaccurate if the camera has been rotated).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobjects` | `Iterable[Mobject]` | — | the objects to focus on; a single mobject or a list both work |
| `margin` | `float` | `0` | extra viewfinder padding (manim units); any non-negative number; **only added on the "tighter" side** (the size is decided by whichever of width/height has the larger ratio) |
| `only_mobjects_in_frame` | `bool` | `False` | `True`: only consider objects **currently on screen**, and ignore off-screen ones |
| `animate` | `bool` | `True` | `True` returns a playable animation builder (to hand to `win.play`); `False` takes effect at once, the picture jumps straight there |

**Returns**: when `animate=True`, a playable animation builder; otherwise the updated viewfinder.

#### Sample: auto_zoom

```python
from real_time_manim import (
    BLUE, RED, WHITE, YELLOW,
    DOWN, LEFT, RIGHT, UP,
    Circle, Dot, FadeIn, MovingCameraScene, Square, Text, VGroup,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class AutoZoomAnimDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        cam = self.camera   #MovingCameraScene's built-in movable camera
        group = VGroup(
            Square(color=BLUE).set_stroke(width=4).shift(LEFT * 2.5),   #the square on the left
            Circle(color=RED).set_stroke(width=4).shift(RIGHT * 2.5),   #the circle on the right
            Dot(color=YELLOW).shift(DOWN * 2),   #the small dot below
        )   #the three objects as one group
        self.add(group)   #add the three objects to the scene
        win.play(cam.auto_zoom(group, margin=0.5), run_time=1.0)   #zoom in with an animation to exactly frame the three objects
        win.play(Wait(0.6))   #hold 0.6s
        win.close()   #close the RTM window


class AutoZoomNoAnimDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        cam = self.camera   #MovingCameraScene's built-in movable camera
        group = VGroup(
            Square(color=BLUE).set_stroke(width=4).shift(LEFT * 2.5),   #the square on the left
            Circle(color=RED).set_stroke(width=4).shift(RIGHT * 2.5),   #the circle on the right
            Dot(color=YELLOW).shift(DOWN * 2),   #the small dot below
        )   #the three objects as one group
        self.add(group)   #add the three objects to the scene
        cam.auto_zoom(group, margin=0.5, animate=False)   #animate=False: takes effect at once, the picture jumps straight there
        win.play(Wait(1.0))   #hold 1.0s
        win.close()   #close the RTM window


class AutoZoomOnlyDemo(MovingCameraScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        cam = self.camera   #MovingCameraScene's built-in movable camera
        sq = Square(color=BLUE).set_stroke(width=4).shift(LEFT * 5)   #a square far to the left
        circ = Circle(color=RED).set_stroke(width=4).shift(RIGHT * 2.5)   #the circle on the right
        self.add(sq, circ)   #add the square and the circle to the scene
        win.play(cam.auto_zoom(circ, margin=0.4), run_time=0.8)   #zoom in on the circle first: the square leaves the frame
        win.play(cam.auto_zoom([circ, sq], margin=0.4, only_mobjects_in_frame=True), run_time=0.8)   #the square is off screen and ignored: the camera does not move
        win.play(Wait(0.5))   #hold 0.5s
        win.play(cam.auto_zoom([circ, sq], margin=0.4), run_time=0.8)   #with no restriction: the square counts too, so the camera zooms out
        win.play(Wait(0.5))   #hold 0.5s and wrap up
        win.close()   #close the RTM window
```

What this code does: the video has three segments in turn.

- the first packs three objects (square, circle, small dot) into one group; `cam.auto_zoom(group, margin=0.5)` returns an animation that "fits the viewfinder around them", and playing it with `win.play` is a smooth zoom-in plus half a unit of padding.
- the second uses the same group and the same margin but `animate=False` — no animation is returned, and the picture jumps straight to the target view the moment it is called.
- the third covers `only_mobjects_in_frame`: it first zooms in on the circle on the right (pushing the square on the left out of the frame), then calls `[circle, square]` with `only_mobjects_in_frame=True` — the square is off screen and ignored, so the camera does not budge; finally the same call with the restriction removed counts the square too, so the camera zooms out to fit both.

<video src="assets/RTM output/02-MovingCamera-auto_zoom.mp4" controls width="560"></video>

> Note:
>
> - `auto_zoom` returns a `frame.animate` animation builder, and it **must** be handed to `win.play` to move (with `animate=False` it simply fixes up the viewfinder and returns, so don't wrap it in `play`).
> - `margin` is not half added to each of the four sides — it is added entirely to the size of whichever side is proportionally tighter.
> - the typical use of `only_mobjects_in_frame=True` is "focus on what is already in the current shot, don't yank the camera around to reach off-screen objects".

---

See also: [Camera](01-Camera.md), [MovingCameraScene](../Special-Scenes/01-MovingCameraScene.md), [ZoomedScene](../Special-Scenes/03-ZoomedScene.md), [Scene basics](../Scenes/01-Scene-Basics.md)
