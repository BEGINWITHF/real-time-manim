# Frame and Coordinates

The picture's **logical coordinate system**: by default it is 8.0 tall and 14.222... wide (= 8×16/9), with the centre at the origin — coordinates like `to_edge(UP)` and `[7.11, 0, 0]` are all computed within this box.

This batch of keys serves as **layout reference values** in RTM: reading them is fine (layout functions work as usual, and the two engines' pictures match), but **writing them is not controlled** — RTM's imaging is not guaranteed to be the same as ManimCE (the earlier "curves do not scale with straight lines" bug was fixed on 2026-10-16, but the two engines still read them at different times, see the samples below).

If you want to move the camera, use `MovingCameraScene`'s `self.camera.frame` (see [Special Scenes / 01-MovingCameraScene](../Special-Scenes/01-MovingCameraScene.md)).

## Parameters

### `frame_width` / `frame_height` / `frame_x_radius` / `frame_y_radius` (logical frame size)

```python
config.frame_width: float = 14.222222   # logical picture width; frame_x_radius = half of it
config.frame_height: float = 8.0        # logical picture height; frame_y_radius = half of it
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `frame_height` | `float` | `8.0` | logical picture height (manim units). Readable: the margins of `to_edge` / `next_to` are computed from it. **Not recommended to write**: CE reads it when the camera is constructed, RTM reads it only during imaging conversion, so the two engines' pictures are not guaranteed to match (see the sample below; the bug where curves/straight lines scaled inconsistently was fixed on 2026-10-16) |
| `frame_width` | `float` | `14.222...` (= 8×16/9) | logical picture width. Readable; **not recommended to write**, same as above |
| `frame_y_radius` | `float` | `4.0` | `frame_height/2`. Writing it also changes `frame_height`, same pitfall as above |
| `frame_x_radius` | `float` | `7.111...` | `frame_width/2`. Writing it also changes `frame_width`, same pitfall as above |

#### Sample: default frame

Place red dots at the four corners of the picture and put a square and a circle in the middle: the red dots sit exactly against the four corners of the frame, the square is square and the circle is round — the visible area is the 14.222×8.0 16:9 box, and coordinate conversion is uniform and undistorted.

```python
from real_time_manim import (
    config,
    Scene, Square, Circle, Dot, Text, VGroup,
    WHITE, RED, GREEN, YELLOW,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class FrameLayoutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        edge_x = 14.222222 / 2   # x of the picture's right edge: = "frame_width" / 2 = "frame_x_radius"
        edge_y = 8.0 / 2   # y of the picture's top edge: = "frame_height" / 2 = "frame_y_radius"
        label = Text("frame_width=14.222  frame_height=8.0", font_size=34,
                     color=WHITE).to_edge(UP, buff=0.3)   # label the frame size on screen
        corners = VGroup(*[
            Dot(color=RED, radius=0.1).move_to([sx * (edge_x - 0.25), sy * (edge_y - 0.25), 0])
            for sx in (-1, 1) for sy in (-1, 1)])   # a red dot at each corner: the frame's four corners
        sq = Square(side_length=1.6, color=YELLOW).set_stroke(width=4).shift(LEFT * 1.2)   # square: evidence the frame is undistorted
        circ = Circle(radius=0.8, color=GREEN).shift(RIGHT * 1.2)   # circle: same as above
        self.add(label)   # put the label into the scene
        win.play(FadeIn(corners), run_time=0.6)   # fade in the red dots at the four corners
        win.play(Create(sq), Create(circ), run_time=0.8)   # draw the square and the circle
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window
```

What this code does: it first computes the four corners of the visible area from `frame_width/2 ≈ 7.111` and `frame_height/2 = 4.0` and places a red dot at each; then draws a square and a circle in the middle.

If the frame's aspect ratio were wrong, the circle would be stretched into an ellipse and the square into a rectangle; in the video both are standard shapes and the red dots sit exactly in the four corners, showing that the visible area is the 14.222×8.0 16:9 box. The text at the top prints the current frame size.

<video src="assets/RTM output/02-Frame-and-Coordinates-frame_layout.mp4" controls width="560"></video>

> Note: constants like `edge_x = 14.222222 / 2` written straight into the code are the most robust (they match manim's `config` defaults); you can also read `config.frame_x_radius` directly, which gives the same result under the defaults.
>
> The red dots are pulled in by 0.25, so they just reveal the boundary without going off-screen — too close and the screen edge clips half a dot.

#### Sample: rewriting the frame (the two engines behave differently)

The same code halves `config.frame_x_radius` / `frame_y_radius` in `__init__` (frame 7.11×4.0) and then places the same objects.

- **In ManimCE the field of view really halves** (the camera reads config at construction, and the picture is enlarged to fill the whole screen).
- **In RTM straight lines and curves scale by the same factor** (the curve-conversion bug was fixed on 2026-10-16; RTM reads the same `config` key during imaging conversion).

The two sides end up consistent; this sample video was re-rendered on 2026-10-17 (`mean|diff|` 0.417, `frames>4.0: 0`).

```python
from real_time_manim import (
    config,
    Scene, Square, Circle, Dot, Text, VGroup,
    WHITE, RED, GREEN, YELLOW,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class FrameOverrideDemo(Scene):
    def __init__(self, **kwargs):
        self._saved = (config.frame_x_radius, config.frame_y_radius)   # remember the two default radii first
        config.frame_x_radius = 3.555   # rewrite "frame_x_radius": the picture width becomes 7.11
        config.frame_y_radius = 2.0     # rewrite "frame_y_radius": the picture height becomes 4.0
        super().__init__(**kwargs)   # the camera is constructed here, CE reads the changed frame

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        label = Text("frame_x_radius=3.555  frame_y_radius=2.0", font_size=34,
                     color=WHITE).to_edge(UP, buff=0.3)   # label the rewritten radii on screen
        corners = VGroup(*[
            Dot(color=RED, radius=0.1).move_to([sx * (3.555 - 0.25), sy * (2.0 - 0.25), 0])
            for sx in (-1, 1) for sy in (-1, 1)])   # the corner red dots placed for the rewritten frame
        sq = Square(side_length=1.6, color=YELLOW).set_stroke(width=4).shift(LEFT * 1.2)   # square: same as the previous sample
        circ = Circle(radius=0.8, color=GREEN).shift(RIGHT * 1.2)   # circle: same as the previous sample
        self.add(label)   # put the label into the scene
        win.play(FadeIn(corners), run_time=0.6)   # fade in the red dots at the four corners
        win.play(Create(sq), Create(circ), run_time=0.8)   # draw the square and the circle
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window
        config.frame_x_radius, config.frame_y_radius = self._saved   # restore the defaults so later samples are unaffected
```

What this code does: it places exactly the same objects as the previous sample, only it first changes the two frame radii to 3.555 / 2.0 in `__init__` (i.e. frame 7.11×4.0) before constructing the scene, and restores them at the end.

The change is entirely in the imaging: ManimCE reads the new frame, the field of view halves, and the same objects fill the whole screen; RTM reads the same `config.frame_height` during imaging conversion, straight lines and curves scale by the same factor, and the final picture matches ManimCE (curve/straight-line conversion inconsistency fixed on 2026-10-16, clip re-rendered on 2026-10-17).

<video src="assets/RTM output/02-Frame-and-Coordinates-frame_override.mp4" controls width="560"></video>

> Note:
>
> - **Do not adjust the frame by changing `config`'s frame keys** — CE and RTM each have their own understanding (CE reads them when the camera is constructed, RTM during imaging conversion), and the pictures are not guaranteed to match.
> - For the desired field of view use `MovingCameraScene`'s `self.camera.frame.animate.set(width=...)` ([Special Scenes / 01-MovingCameraScene](../Special-Scenes/01-MovingCameraScene.md)); that path is consistent across both engines.
> - `config` is global: remember to restore it after the sample, otherwise every later scene's layout shrinks too.

### `top` / `bottom` / `left_side` / `right_side` (edge midpoints), `aspect_ratio` / `frame_size` (read-only)

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `top` / `bottom` | `Vector3D` | `[0, ±4, 0]` | read-only: the coordinates of the top/bottom edge midpoint; when placing labels just `move_to(config.top)` |
| `left_side` / `right_side` | `Vector3D` | `[±7.111..., 0, 0]` | read-only: the coordinates of the left/right edge midpoint, same as above |
| `aspect_ratio` | `float` | `1.777...` | read-only: pixel aspect ratio = 16/9. Cannot be written: RTM's output is locked to 1920×1080, the frame is always 16:9 |
| `frame_size` | `tuple[int, int]` | `(1920, 1080)` | read-only: `(pixel_width, pixel_height)`, same as above |

#### Sample: edge midpoints

Four red dots are placed at the positions of `top` / `bottom` / `left_side` / `right_side` and labelled with their names, and a white cursor walks around them in a loop — these four coordinates are the most useful anchors when doing layout.

```python
from real_time_manim import (
    config,
    Scene, Square, Circle, Dot, Text, VGroup,
    WHITE, RED, GREEN, YELLOW,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, Create,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class EdgePointsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        edge_x = 14.222222 / 2   # x of the picture's right edge: the x coordinate of "right_side"
        edge_y = 8.0 / 2   # y of the picture's top edge: the y coordinate of "top"
        pts = VGroup(
            Dot(color=RED, radius=0.12).move_to([0, edge_y - 0.3, 0]),   # top: the midpoint of the top edge
            Dot(color=RED, radius=0.12).move_to([edge_x - 0.3, 0, 0]),   # right_side: the midpoint of the right edge
            Dot(color=RED, radius=0.12).move_to([0, -edge_y + 0.3, 0]),   # bottom: the midpoint of the bottom edge
            Dot(color=RED, radius=0.12).move_to([-edge_x + 0.3, 0, 0]),   # left_side: the midpoint of the left edge
        )
        names = VGroup(
            Text("top", font_size=28, color=YELLOW).next_to(pts[0], DOWN, buff=0.15),
            Text("right_side", font_size=28, color=YELLOW).next_to(pts[1], LEFT, buff=0.25),
            Text("bottom", font_size=28, color=YELLOW).next_to(pts[2], UP, buff=0.15),
            Text("left_side", font_size=28, color=YELLOW).next_to(pts[3], RIGHT, buff=0.25),
        )
        walker = Dot(color=WHITE, radius=0.18).move_to(pts[3])   # cursor: starts from "left_side"
        self.add(pts, names, walker)   # put the four edge points, the four name rows and the cursor into the scene
        win.play(FadeIn(pts), FadeIn(names), run_time=0.6)   # fade in the four edge points and names
        win.play(walker.animate.move_to(pts[0]), run_time=0.5)   # the cursor walks to "top"
        win.play(walker.animate.move_to(pts[1]), run_time=0.5)   # the cursor walks to "right_side"
        win.play(walker.animate.move_to(pts[2]), run_time=0.5)   # the cursor walks to "bottom"
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window
```

What this code does: it places the four red dots at the midpoints of the top, right, bottom and left edges respectively (the coordinates are `±frame_x_radius`, `±frame_y_radius`), labels them with their names next to them, then makes a white cursor start from `left_side` and walk to `top`, `right_side`, `bottom` in turn.

In the video you can clearly see these four anchors touching the exact centres of the picture's four edges — when writing layout, use them to hug an edge, or just `move_to(config.top)`.

<video src="assets/RTM output/02-Frame-and-Coordinates-edge_points.mp4" controls width="560"></video>

> Note:
>
> - `top` / `bottom` / `left_side` / `right_side` are computed read-only properties; don't try to assign to them. To put something at the edge, either `move_to(config.top)` or `to_edge(UP, buff=...)` works.
> - `aspect_ratio` / `frame_size` are likewise read-only — "changing the frame" cannot be done; RTM's pixel output is always 1920×1080 (for a demonstration of the forced correction see the `MLWindow` sample in [05-RTM-Record-and-Window-Options](05-RTM-Record-and-Window-Options.md)).

Of the three samples, `frame_layout` and `edge_points` are pixel-for-pixel identical (114 frames / 1.90s, 156 frames / 2.60s); `frame_override` has the same frame count (114 frames), and the two sides end up consistent (the curve/straight-line conversion inconsistency bug was fixed on 2026-10-16, clip re-rendered on 2026-10-17); for the comparison see `assets/README.md`.

---

See also: [01-Quality-and-Output](01-Quality-and-Output.md) | [03-Paths-and-Windows](03-Paths-and-Windows.md) | [05-RTM-Record-and-Window-Options](05-RTM-Record-and-Window-Options.md)
