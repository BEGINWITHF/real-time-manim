# ThreeDCamera (the 3D camera)

The 3D camera: the view is stored in five `ValueTracker`s (`phi` / `theta` / `focal_distance` / `gamma` / `zoom`), so you can both `set`/`get` the whole thing and animate the trackers directly; lighting, shading and the projection mode are also its responsibility.

The view is normally set through `ThreeDScene`'s `set_camera_orientation` / `move_camera` (see [ThreeDScene](../Special-Scenes/02-ThreeDScene.md)), and this page covers the camera's **own** constructor parameters and methods.

## Parameters

### class ThreeDCamera (constructor parameters)

```python
def __init__(self, focal_distance: float = 20.0, shading_factor: float = 0.2, default_distance: float = 5.0, light_source_start_point: Point3DLike = 9 * DOWN + 7 * LEFT + 10 * OUT, should_apply_shading: bool = True, exponential_projection: bool = False, phi: float = 0, theta: float = -90 * DEGREES, gamma: float = 0, zoom: float = 1, **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `focal_distance` | `float` | `20.0` | focal length; **accepts** any positive number, larger is flatter perspective; use `set_focal_distance` at runtime |
| `shading_factor` | `float` | `0.2` | light/dark shading strength; **do not pass**: in 0.21 it is stored but unused (nothing in the codebase reads it), so no value changes the picture |
| `default_distance` | `float` | `5.0` | default distance; **do not pass**: as above, stored but unused |
| `light_source_start_point` | `Point3DLike` | `9*DOWN + 7*LEFT + 10*OUT` | light source position; **accepts** any coordinates — move it to the opposite side and the cube's light/dark faces flip (sample segment 2) |
| `should_apply_shading` | `bool` | `True` | whether to shade 3D objects; **accepts** `True`/`False`, and changing the attribute at runtime works too (sample segment 3) |
| `exponential_projection` | `bool` | `False` | use exponential projection to reduce distortion at distance; **accepts** `True`/`False` (see the project section for the sample) |
| `phi` | `float` | `0` | initial polar angle (angle with the Z axis, radians); **accepts** radians (effective as passed in the constructor, sample segment 1) |
| `theta` | `float` | `-90 * DEGREES` | initial azimuth (around the Z axis, radians); as above |
| `gamma` | `float` | `0` | initial roll angle (radians); as above |
| `zoom` | `float` | `1` | initial zoom factor; as above |
| `**kwargs` | `Any` | — | forwarded to `Camera.__init__` (see [Camera](01-Camera.md)) |

**Returns**: none (constructs an instance).

How to get constructor parameters through: `Scene`'s `camera_class` only takes a **class**, and the renderer builds the camera with a no-argument `camera_class()` call — to get constructor parameters in you must use `functools.partial(ThreeDCamera, ...)` or a subclass overriding the defaults (the samples use `partial`).

Also note the distinction: the "default angled camera orientation" parameter in `ThreeDScene`'s constructor (`default_angled_camera_orientation_kwargs`) is **stored but unused** (both engines render a front view, see the [ThreeDScene](../Special-Scenes/02-ThreeDScene.md) page), so don't confuse it with `ThreeDCamera`'s own `phi`/`theta`.

#### Sample: class ThreeDCamera (constructor parameters)

```python
from functools import partial

from real_time_manim import (
    BLUE, GREEN, WHITE, YELLOW,
    DEGREES, DOWN, LEFT, ORIGIN, OUT, RIGHT, UP,
    Cube, FadeIn, Text, ThreeDAxes, ThreeDCamera, ThreeDScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class CtorAngleDemo(ThreeDScene):
    def __init__(self, **kwargs):
        #"camera_class" only takes a class (the renderer calls it with no arguments to build the camera),
        #constructor parameters must be wrapped in functools.partial to get through
        super().__init__(camera_class=partial(ThreeDCamera, phi=70 * DEGREES, theta=-60 * DEGREES), **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        axes = ThreeDAxes()   #the default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   #a blue cube as a reference
        cap = Text("ctor phi=70 theta=-60 (no set_camera_orientation)", font_size=26, color=YELLOW)   #caption at the top
        self.camera.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen so it does not turn with the camera
        cap.to_edge(UP)   #move the title to the top of the picture
        self.add(axes, cube, cap)   #add the axes, the cube and the title to the scene
        win.play(FadeIn(cube), run_time=0.5)   #the cube fades in: the view is already angled
        win.play(Wait(1.2))   #hold 1.2s: the initial view from the constructor parameters takes effect directly
        win.close()   #close the RTM window


class CtorLightDemo(ThreeDScene):
    def __init__(self, **kwargs):
        #also pass "light_source_start_point" into the constructor with partial: the light flips to the upper-right-front
        super().__init__(camera_class=partial(
            ThreeDCamera, light_source_start_point=9 * UP + 7 * RIGHT + 10 * OUT), **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        axes = ThreeDAxes()   #the default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   #a blue cube as a reference
        cap = Text("ctor light=9U+7R+10O", font_size=30, color=YELLOW)   #caption at the top
        self.camera.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen
        cap.to_edge(UP)   #move the title to the top of the picture
        self.add(axes, cube, cap)   #add the axes, the cube and the title to the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #explicitly set the view back to the previous segment's angle, to compare only the lighting
        win.play(FadeIn(cube), run_time=0.5)   #the cube fades in: its light/dark faces are opposite to the previous segment
        win.play(Wait(1.0))   #hold 1.0s
        win.close()   #close the RTM window


class CtorShadingDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        axes = ThreeDAxes()   #the default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   #a blue cube as a reference
        cap = Text("should_apply_shading=True", font_size=30, color=YELLOW)   #caption at the top
        self.camera.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen
        cap.to_edge(UP)   #move the title to the top of the picture
        self.add(axes, cube, cap)   #add the axes, the cube and the title to the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #set the view explicitly
        win.play(FadeIn(cube), run_time=0.5)   #the cube fades in: the faces have different brightness
        win.play(Wait(0.7))   #hold 0.7s
        self.camera.should_apply_shading = False   #turn shading off: all faces become the same color
        cap.become(Text("should_apply_shading=False", font_size=30, color=YELLOW).to_edge(UP))   #swap the caption text accordingly
        win.play(Wait(1.0))   #hold 1.0s to see the flat color
        win.close()   #close the RTM window
```

What this code does: three contrasted segments.

- segment 1 uses only the constructor parameter `partial(ThreeDCamera, phi=70°, theta=-60°)` to set an angled view — with **no** `set_camera_orientation` call at all, the picture is angled from the start, proving that `ThreeDCamera`'s view constructor parameters really work.
- segment 2 flips the light source from the default "lower-left-back" to "upper-right-front" (`9*UP + 7*RIGHT + 10*OUT`), sets the view back to the same angle with an explicit call, and compares only the lighting: the cube's light/dark faces flip entirely.
- segment 3 demonstrates `should_apply_shading`: the first half has faces of different brightness (shading on), and after turning it off midway all faces become the same blue (flat color).

<video src="assets/RTM output/03-ThreeDCamera-ctor.mp4" controls width="560"></video>

> Note:
>
> - a frame-extraction-verified conclusion: `ThreeDCamera`'s own `phi`/`theta`/`gamma`/`zoom` constructor parameters **both take effect** under RTM and ManimCE (segment 1); what is really "stored but unused" is `default_angled_camera_orientation_kwargs`/`ambient_camera_rotation` on the `ThreeDScene` side.
> - even so, in everyday use it is still best to explicitly call `self.set_camera_orientation(...)` in `construct` — it does not depend on the constructor chain and is the most direct and easiest to change.
> - `shading_factor`/`default_distance` are dead parameters in 0.21, so don't bother tuning them.
> - `MLWindow(960, 540)` being forcibly corrected to 1920×1080 is a normal hint.

### ThreeDCamera view parameters (get_* / set_* / get_value_trackers)

```python
def get_phi(self) -> float:
def get_theta(self) -> float:
def get_gamma(self) -> float:
def get_zoom(self) -> float:
def get_focal_distance(self) -> float:
def set_phi(self, value: float) -> None:
def set_theta(self, value: float) -> None:
def set_gamma(self, value: float) -> None:
def set_zoom(self, value: float) -> None:
def set_focal_distance(self, value: float) -> None:
def get_value_trackers(self) -> list[ValueTracker]:
```

| Parameter / Return | Type | Description |
| --- | --- | --- |
| `value` (the five `set_*`) | `float` | **accepts** any number: `set_phi`/`set_theta`/`set_gamma` in radians (often with `DEGREES`), `set_zoom` a multiplier, `set_focal_distance` a length unit; all take effect **immediately** (no animation) |
| five `get_*` | `float` | read back the current view, returns a `float` |
| `get_value_trackers()` | `list[ValueTracker]` | returns the 5 trackers `[phi, theta, focal_distance, gamma, zoom]`; `animate`ing a tracker is an animated view change |

#### Sample: get_* / set_* / get_value_trackers

```python
from functools import partial

from real_time_manim import (
    BLUE, GREEN, WHITE, YELLOW,
    DEGREES, DOWN, LEFT, ORIGIN, OUT, RIGHT, UP,
    Cube, FadeIn, Text, ThreeDAxes, ThreeDCamera, ThreeDScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class ViewZoomDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        cam = self.camera   #ThreeDScene's built-in ThreeDCamera
        axes = ThreeDAxes()   #the default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   #a blue cube as a reference
        cap = Text("get_phi / get_theta / get_gamma / get_zoom / get_focal_distance", font_size=22, color=YELLOW)   #caption at the top
        cam.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen
        cap.to_edge(UP)   #move the title to the top of the picture
        info = Text("phi=%.2f theta=%.2f gamma=%.2f zoom=%.2f focal=%.1f" % (
            cam.get_phi(), cam.get_theta(), cam.get_gamma(), cam.get_zoom(), cam.get_focal_distance()),
            font_size=24, color=WHITE).next_to(cap, DOWN)   #readings of the five view parameters
        cam.add_fixed_in_frame_mobjects(info)   #pin the readings to the screen too
        self.add(axes, cube, cap, info)   #add the axes, the cube, the title and the readings to the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #set the view explicitly
        win.play(FadeIn(cube), run_time=0.5)   #the cube fades in
        cam.set_focal_distance(18.0)   #change the focal length: takes effect immediately
        cam.set_zoom(1.15)   #change the zoom: takes effect immediately
        info.become(Text("phi=%.2f theta=%.2f gamma=%.2f zoom=%.2f focal=%.1f" % (
            cam.get_phi(), cam.get_theta(), cam.get_gamma(), cam.get_zoom(), cam.get_focal_distance()),
            font_size=24, color=WHITE).next_to(cap, DOWN))   #refresh the readings
        win.play(Wait(1.2))   #hold 1.2s to see the zoomed-in picture
        win.close()   #close the RTM window


class ViewTrackerDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        cam = self.camera   #ThreeDScene's built-in ThreeDCamera
        axes = ThreeDAxes()   #the default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   #a blue cube as a reference
        cap = Text("get_value_trackers()[1].animate.set_value(-1.2)", font_size=26, color=YELLOW)   #caption at the top
        cam.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen
        cap.to_edge(UP)   #move the title to the top of the picture
        self.add(axes, cube, cap)   #add the axes, the cube and the title to the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #set the view explicitly
        trackers = cam.get_value_trackers()   #5 ValueTrackers: phi, theta, focal_distance, gamma, zoom
        win.play(FadeIn(cube), run_time=0.5)   #the cube fades in
        win.play(trackers[1].animate.set_value(-1.2), run_time=1.0)   #animate the theta tracker: the camera orbits
        win.play(Wait(0.6))   #hold 0.6s and wrap up
        win.close()   #close the RTM window


class ViewAngleDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        cam = self.camera   #ThreeDScene's built-in ThreeDCamera
        axes = ThreeDAxes()   #the default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   #a blue cube as a reference
        cap = Text("set_phi(0.6) / set_gamma(0.25)", font_size=28, color=YELLOW)   #caption at the top
        cam.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen
        cap.to_edge(UP)   #move the title to the top of the picture
        self.add(axes, cube, cap)   #add the axes, the cube and the title to the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #set the view explicitly
        win.play(FadeIn(cube), run_time=0.5)   #the cube fades in
        cam.set_phi(0.6)   #change the polar angle: takes effect immediately, a shallower top-down look
        cam.set_gamma(0.25)   #change the roll angle: takes effect immediately, the picture rolls about the view axis
        win.play(Wait(1.2))   #hold 1.2s to see the view after the jump
        win.close()   #close the RTM window
```

What this code does: each segment demonstrates a kind of usage.

- segment 1 reads the five view parameters onto the screen; the two lines `set_focal_distance(18.0)` + `set_zoom(1.15)` **immediately** push the picture closer — the readings refresh in step to `zoom=1.15 focal=18.0`.
- segment 2 plays with the trackers: `get_value_trackers()` returns the 5 `ValueTracker`s in the order `[phi, theta, focal_distance, gamma, zoom]`; animating index 1, the theta tracker, makes the camera orbit the scene smoothly.
- segment 3 demonstrates an instant view jump: `set_phi(0.6)` makes the camera look down more shallowly and `set_gamma(0.25)` rolls the picture about the view axis; both lines take effect in one step with no transition animation.

<video src="assets/RTM output/03-ThreeDCamera-view.mp4" controls width="560"></video>

> Note:
>
> - all `set_*` are instant jumps; for a smooth transition either `animate` a tracker (segment 2) or use `ThreeDScene`'s `move_camera` (see the [ThreeDScene](../Special-Scenes/02-ThreeDScene.md) page).
> - a tracker is an ordinary `ValueTracker` and can also go into an `AnimationGroup` and be played alongside other animations.
> - angles are always radians — whether you write `0.6` by hand or `70 * DEGREES`, both are radian values.

### ThreeDCamera.add_fixed_in_frame_mobjects / add_fixed_orientation_mobjects

```python
def add_fixed_in_frame_mobjects(self, *mobjects: Mobject) -> None:
def remove_fixed_in_frame_mobjects(self, *mobjects: Mobject) -> None:
def add_fixed_orientation_mobjects(self, *mobjects: Mobject, use_static_center_func: bool = False, center_func: Callable[[], Point3D] | None = None) -> None:
def remove_fixed_orientation_mobjects(self, *mobjects: Mobject) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | — | the objects to fix (or unfix) |
| `use_static_center_func` | `bool` | `False` | `add_fixed_orientation_mobjects` only: pin the rotation center to the center at call time (saving one `get_center` computation per frame) |
| `center_func` | `Callable[[], Point3D] \| None` | `None` | `add_fixed_orientation_mobjects` only: a custom rotation center for the orientation lock |

**Returns**: none of them return anything. `add_fixed_in_frame_mobjects` **pins the object to the screen** (both position and orientation are locked, and it does not move however the camera turns; good for titles and formulas in a 3D scene); `add_fixed_orientation_mobjects` locks only the **orientation** (the object still sits in 3D space and follows perspective, but it does not flip over entirely like an ordinary 3D object); `remove_*` undoes it.

#### Sample: add_fixed_in_frame_mobjects / add_fixed_orientation_mobjects

```python
from functools import partial

from real_time_manim import (
    BLUE, GREEN, WHITE, YELLOW,
    DEGREES, DOWN, LEFT, ORIGIN, OUT, RIGHT, UP,
    Cube, FadeIn, Text, ThreeDAxes, ThreeDCamera, ThreeDScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class FixedDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #move_camera calls self.play internally, so wire it to the window first
        cam = self.camera   #ThreeDScene's built-in ThreeDCamera
        axes = ThreeDAxes()   #the default 3D axes
        cube = Cube(side_length=1.2).set_color(BLUE)   #a blue cube as a reference
        title = Text("fixed_in_frame", font_size=34, color=YELLOW)   #a title demonstrating screen pinning
        tag = Text("fixed_orientation", font_size=26, color=GREEN)   #a label demonstrating the orientation lock
        tag.next_to(cube, UP)   #place the label in 3D space above the cube
        cam.add_fixed_in_frame_mobjects(title)   #title: both position and orientation locked to the screen
        title.to_edge(UP)   #move the title to the top of the picture
        cam.add_fixed_orientation_mobjects(tag)   #label: only the orientation is locked, the position stays in 3D space
        self.add(axes, cube, tag, title)   #add the four objects to the scene: the camera's add_fixed_* only registers the draw mode, it does not add for you
        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)   #set the view explicitly
        win.play(Wait(0.8))   #hold 0.8s to see the two objects' positions
        self.move_camera(theta=-140 * DEGREES, run_time=1.6)   #orbit 90°: the title does not budge, the label moves with the cube across the picture
        win.play(Wait(0.4))   #hold 0.4s
        cam.remove_fixed_in_frame_mobjects(title)   #undo the screen pinning
        cam.remove_fixed_orientation_mobjects(tag)   #undo the orientation lock
        self.move_camera(theta=-190 * DEGREES, run_time=1.4)   #orbit once more: both objects become ordinary 3D objects
        win.play(Wait(0.4))   #hold 0.4s and wrap up
        win.close()   #close the RTM window
```

What this code does: it puts a green label in 3D space above the cube and pins a yellow title to the top of the screen, then `move_camera` orbits 90°: the title does not budge, and the label moves with the cube across the picture while keeping its orientation without tipping over.

Then `remove_fixed_*` releases both locks and it orbits once more — this time both texts become ordinary 3D objects and tilt along with the view. The difference between locked and not is obvious.

<video src="assets/RTM output/03-ThreeDCamera-fixed.mp4" controls width="560"></video>

> Note:
>
> - **the camera's `add_fixed_*` only registers the draw mode; it does not add the object to the scene for you** — forget `self.add` and it won't appear at all (that is why the sample deliberately puts the title in `self.add` too); `ThreeDScene` also has same-named scene methods, and that version adds for you along the way, so pick one of the two entries.
> - an orientation-locked object's position is still in 3D space, and perspective skew makes it look a little tilted; this is normal.

### ThreeDCamera.project_point / project_points

```python
def project_point(self, point: Point3D) -> Point3D:
def project_points(self, points: Point3D_Array) -> Point3D_Array:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `point` / `points` | `Point3D` / `Point3D_Array` | — | the 3D point(s) to project (a single coordinate or an array of coordinates) |

**Returns**: screen coordinates projected according to the **current view** (an `[x, y, z]` array; `project_points` returns one row per point). Often used to convert a 3D position into screen coordinates for annotations.

#### Sample: project_point / project_points, exponential_projection

```python
from functools import partial

from real_time_manim import (
    BLUE, GREEN, WHITE, YELLOW,
    DEGREES, DOWN, LEFT, ORIGIN, OUT, RIGHT, UP,
    Cube, FadeIn, Text, ThreeDAxes, ThreeDCamera, ThreeDScene,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class ProjectDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        cam = self.camera   #ThreeDScene's built-in ThreeDCamera
        axes = ThreeDAxes()   #the default 3D axes
        cap = Text("project_point(ORIGIN) / project_points([ORIGIN, RIGHT, UP])", font_size=22, color=YELLOW)   #caption at the top
        cam.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen
        cap.to_edge(UP)   #move the title to the top of the picture
        self.add(axes, cap)   #add the axes and the title to the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #set the view explicitly
        p1 = cam.project_point(ORIGIN)   #the projected coordinate of the origin
        pts = cam.project_points([ORIGIN, RIGHT, UP])   #the projected coordinates of the three points
        info = Text("origin=(%.2f, %.2f)  right=(%.2f, %.2f)  up=(%.2f, %.2f)" % (
            p1[0], p1[1], pts[1][0], pts[1][1], pts[2][0], pts[2][1]),
            font_size=24, color=WHITE).next_to(cap, DOWN)   #put the projection result on screen
        cam.add_fixed_in_frame_mobjects(info)   #pin the readings to the screen
        self.add(info)   #add the readings to the scene
        win.play(Wait(1.2))   #hold 1.2s to see the projection values
        win.close()   #close the RTM window


class ExponentialDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it to the window first
        cam = self.camera   #ThreeDScene's built-in ThreeDCamera
        axes = ThreeDAxes()   #the default 3D axes
        near = Cube(side_length=1.2).set_color(BLUE)   #the near cube
        far = Cube(side_length=1.2).set_color(GREEN).shift(DOWN * 2.5 + RIGHT * 2.5)   #the far cube
        cap = Text("exponential_projection=False", font_size=28, color=YELLOW)   #caption at the top
        cam.add_fixed_in_frame_mobjects(cap)   #pin the title to the screen
        cap.to_edge(UP)   #move the title to the top of the picture
        self.add(axes, near, far, cap)   #add the axes, the two cubes and the title to the scene
        self.set_camera_orientation(phi=70 * DEGREES, theta=-60 * DEGREES)   #set the view explicitly
        cam.set_focal_distance(6.0)   #pull the focal length closer: stronger perspective, so the difference between the two projections shows
        win.play(FadeIn(near, far), run_time=0.5)   #the two cubes fade in
        win.play(Wait(0.8))   #hold 0.8s to see the ordinary projection
        cam.exponential_projection = True   #switch to exponential projection: distant objects are no longer over-magnified
        cap.become(Text("exponential_projection=True", font_size=28, color=YELLOW).to_edge(UP))   #swap the caption text accordingly
        win.play(Wait(1.0))   #hold 1.0s to compare
        win.close()   #close the RTM window
```

What this code does: segment 1 projects the origin and the two unit vectors `RIGHT` and `UP` into screen coordinates and prints them — note the projection is computed for the **current view**, so it is only meaningful to ask after the angled view is set up.

Segment 2 pulls the focal length to 6.0 to strengthen perspective; the first half is ordinary projection (linear perspective, where the distant green cube is exaggeratedly enlarged), and midway `exponential_projection` is switched to `True` and the distant object immediately shrinks back to a normal size — that is the difference between the two projection formulas.

<video src="assets/RTM output/03-ThreeDCamera-project.mp4" controls width="560"></video>

> Note:
>
> - `project_*` returns coordinates under the current projection matrix, and the values change as soon as the view turns — the readings and the picture always line up.
> - `exponential_projection` takes effect as soon as it is assigned at runtime, and the smaller the focal length (the stronger the perspective) the more obvious the difference between the two projections; the default linear projection is good enough, and exponential projection is worth considering only for ultra-wide deep scenes.

### ThreeDCamera.capture_mobjects

```python
def capture_mobjects(self, mobjects: Iterable[Mobject], **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobjects` | `Iterable[Mobject]` | — | the objects to capture |
| `**kwargs` | `Any` | — | forwarded to `get_mobjects_to_display` |

**Returns**: none. Upstream semantics: first refresh the rotation matrix for the current view, then "shoot" the objects into the camera's pixel array.

**No video**: this is the entry point of the Cairo pixel-capture pipeline; RTM uses Vulkan vector rendering and has no pixel array to shoot into, same as the `capture_*` family on the [Camera](01-Camera.md) page.

Among the other low-frequency methods, `get_rotation_matrix` (the current 3×3 rotation matrix) and `project_*` above are pure computations and always available; see the corresponding sections for `add_fixed_*`.

---

See also: [ThreeDScene](../Special-Scenes/02-ThreeDScene.md), [Camera](01-Camera.md), [MovingCamera](02-MovingCamera.md), [Scene basics](../Scenes/01-Scene-Basics.md)
