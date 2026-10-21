# ThreeDScene (3D scene)

A 3D view-control scene: it swaps `Scene` onto a `ThreeDCamera`, and lets you change the view (`phi` / `theta` / `gamma`), zoom (`zoom`) and frame centre at any time, plus ambient rotation, 3D-illusion wobble, the fixed family that pins objects to the screen, and the enhanced subclass `SpecialThreeDScene`. Angles are always in **radians** (`70 * DEGREES` is 70°).

Under RTM all of this renders and is verified to work; note that both "view" constructor parameters are merely stored and do not take effect on their own (see sample 1).

## Parameters

### class ThreeDScene

```python
def __init__(self, camera_class: type[ThreeDCamera] = ThreeDCamera, ambient_camera_rotation: dict | None = None, default_angled_camera_orientation_kwargs: dict | None = None, **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `camera_class` | `type[ThreeDCamera]` | `ThreeDCamera` | camera class. **You can pass**: `ThreeDCamera` (default); **not recommended** to swap it out — every `phi`/`theta`/`gamma`/`zoom` below works off `ThreeDCamera`'s properties |
| `ambient_camera_rotation` | `dict \| None` | `None` | **stored but unused**: shaped like `{"theta": 0.15}`; upstream only hangs it on `self.ambient_camera_rotation`, nothing in the whole library reads it, and in testing the frame does not budge; to rotate, call `begin_ambient_camera_rotation()` in `construct` (sample 3) |
| `default_angled_camera_orientation_kwargs` | `dict \| None` | `{"phi": 70*DEGREES, "theta": -135*DEGREES}` | **stored, only used later**: it is likewise stored first, and only read and applied when `set_to_default_angled_camera_orientation()` is called (sample 1); to set an angle directly, use `set_camera_orientation` |
| `**kwargs` | `Any` | — | forwarded to `Scene.__init__` (`random_seed` and so on, see [Scene Basics](../Scenes/01-Scene-Basics.md)) |

> **Returns**: none (constructs an instance).

The companion method (the only place that reads `default_angled_camera_orientation_kwargs`):

```python
def set_to_default_angled_camera_orientation(self, **kwargs: Any) -> None:
```

It hands the stored angled-view dict (`kwargs` can override on the spot, e.g. `set_to_default_angled_camera_orientation(phi=60 * DEGREES)`) to `set_camera_orientation`; **returns**: none.

#### Sample: changing the constructor parameters

With nothing passed, the starting view is actually **straight on** (`phi=0°`, `theta=0°`; the classic oblique angle does not appear by itself). Both view constructor parameters are stored but unused — `default_angled_camera_orientation_kwargs` waits for `set_to_default_angled_camera_orientation()` before it applies, and upstream simply nobody reads `ambient_camera_rotation`.

```python
from real_time_manim import ThreeDScene, ThreeDAxes, Cube, Text, FadeIn, \
    BLUE, YELLOW, UP, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   # instantly swap the top caption text without spending animation time
    cap.become(Text(text, font_size=30, color=YELLOW).to_edge(UP))

class CtorDefault(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # scene methods call self.play internally, so wire it to the window first
        axes = ThreeDAxes()   # default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   # a blue cube as a reference
        cap = Text("", font_size=30, color=YELLOW)   # top caption text (content swapped later)
        self.add_fixed_in_frame_mobjects(cap)   # pin the title to the screen so it faces the viewer however the view turns
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(axes, cube, cap)   # add the axes, the cube and the title to the scene
        say(cap, "default phi=0° theta=0°")   # nothing passed: the start is the straight-on view
        win.play(FadeIn(cube), run_time=0.5)   # fade in the cube
        win.play(Wait(1.4))   # pause 1.4s to see the default view
        self.set_to_default_angled_camera_orientation()   # apply the stored default angled view {phi:70°, theta:-135°}
        say(cap, "set_to_default_angled_camera_orientation()")
        win.play(Wait(1.6))   # jump to manim's classic oblique view
        win.close()   # close the RTM window


class CtorAngled(ThreeDScene):
    def __init__(self, **kwargs):
        # the constructor parameter is only stored into self.default_angled_camera_orientation_kwargs; nobody uses it on their own
        super().__init__(
            default_angled_camera_orientation_kwargs=
            {"phi": 60 * DEGREES, "theta": -45 * DEGREES}, **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # scene methods call self.play internally, so wire it to the window first
        axes = ThreeDAxes()   # default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   # a blue cube as a reference
        cap = Text("", font_size=30, color=YELLOW)   # top caption text (content swapped later)
        self.add_fixed_in_frame_mobjects(cap)   # pin the title to the screen
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(axes, cube, cap)   # add the axes, the cube and the title to the scene
        say(cap, "ctor kwarg stored ... view unchanged")   # a constructor parameter was passed, but nobody reads it
        win.play(FadeIn(cube), run_time=0.5)   # fade in the cube
        win.play(Wait(1.4))   # still the straight-on view: passing the parameter alone has no effect
        self.set_to_default_angled_camera_orientation()   # only calling this method reads and applies it
        say(cap, "set_to_default_angled_camera_orientation()")
        win.play(Wait(1.6))   # this time it jumps to the custom phi=60° theta=-45°
        win.close()   # close the RTM window


class CtorAmbient(ThreeDScene):
    def __init__(self, **kwargs):
        # this constructor parameter is likewise only stored into self.ambient_camera_rotation; nobody in the library reads it (upstream is like this)
        super().__init__(ambient_camera_rotation={"theta": 0.15}, **kwargs)

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # scene methods call self.play internally, so wire it to the window first
        axes = ThreeDAxes()   # default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   # a blue cube as a reference
        cap = Text("", font_size=30, color=YELLOW)   # top caption text (content swapped later)
        self.add_fixed_in_frame_mobjects(cap)   # pin the title to the screen
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(axes, cube, cap)   # add the axes, the cube and the title to the scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=-90 * DEGREES)   # set an oblique view first so you can tell whether it rotates
        say(cap, "ambient_camera_rotation ... no effect")
        win.play(FadeIn(cube), run_time=0.5)   # fade in the cube
        win.play(Wait(1.5))   # the frame does not budge: nobody reads this parameter
        self.begin_ambient_camera_rotation(rate=0.15)   # ambient rotation only works through the method
        say(cap, "begin_ambient_camera_rotation(rate=0.15)")
        win.play(Wait(1.5))   # now it starts turning
        self.stop_ambient_camera_rotation()   # stop
        win.play(Wait(0.3))   # pause 0.3s and finish
        win.close()   # close the RTM window
```

What this code does: three clips in a row, all about constructor parameters.

- The first passes nothing, starts straight on, then calls `set_to_default_angled_camera_orientation()` to jump to the stored classic oblique view (70° / -135°).
- The second passes a custom `{phi: 60°, theta: -45°}` at construction time, and the frame **still does not move** (the parameter alone is unused) until the same method is called, which jumps to the custom angle.
- The third passes `ambient_camera_rotation={"theta": 0.15}` and the frame does not budge, then switches to calling `begin_ambient_camera_rotation()` and it starts turning — a control that proves both parameters are "stored but unused".

<video src="assets/RTM output/02-ThreeDScene-ctor.mp4" controls width="560"></video>

> Note: constructor parameters not taking effect is existing behavior of upstream `manim` 0.21; command-line rendering and RTM are exactly the same, so it is not an RTM problem.
>
> In daily use, the most direct way to set an oblique view is `set_camera_orientation(phi=70 * DEGREES, theta=-135 * DEGREES)` in `construct`; the point of `default_angled_camera_orientation_kwargs` is to "preset one step and jump back to it at any time".
>
> The `ambient_camera_rotation` parameter can be ignored outright; the proper route for ambient rotation is `begin_ambient_camera_rotation()` from sample 3.

### set_camera_orientation / move_camera

`set_camera_orientation` sets the view **instantly** (no animation, a one-frame jump); `move_camera` moves **with animation** (it calls `self.play(...)` internally, so under RTM you must set `self.play = win.play` first). The parameters mean the same in both, and any parameter passed as `None` stays unchanged.

```python
def set_camera_orientation(self, phi: float | None = None, theta: float | None = None, gamma: float | None = None, zoom: float | None = None, focal_distance: float | None = None, frame_center: Mobject | Sequence[float] | None = None, **kwargs: Any) -> None:
def move_camera(self, phi: float | None = None, theta: float | None = None, gamma: float | None = None, zoom: float | None = None, focal_distance: float | None = None, frame_center: Mobject | Sequence[float] | None = None, added_anims: Iterable[Animation] = [], **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `phi` | `float \| None` | `None` (unchanged) | polar angle (radians): `0` = straight down from the front, `70 * DEGREES` ≈ the classic oblique view; **accepts** any radian value |
| `theta` | `float \| None` | `None` (unchanged) | azimuth (radians): how far to rotate about the vertical axis, the classic value is `-135 * DEGREES` |
| `gamma` | `float \| None` | `None` (unchanged) | roll angle (radians): the frame "tilts its head" about the view axis; **not recommended** to make it large, or the text turns upside down |
| `zoom` | `float \| None` | `None` (unchanged, i.e. `1.0`) | zoom factor: `>1` zooms in, `<1` zooms out; **accepts** commonly `0.5` ~ `3`, too large and only black remains |
| `focal_distance` | `float \| None` | `None` (unchanged) | focal length (perspective strength), normally leave empty, only tune it together with `zoom` |
| `frame_center` | `Mobject \| Sequence[float] \| None` | `None` (frame centre) | move the frame centre to some object or coordinate; **accepts** a mobject or `[x, y, z]` |
| `added_anims` | `Iterable[Animation]` | `[]` | `move_camera` only: other animations played **at the same time** as the camera motion |
| `**kwargs` | `Any` | — | `move_camera` only: forwarded to `self.play` (e.g. `run_time=1.2`); `set_camera_orientation` has no animation, so passing it does nothing |

> **Returns**: none.

#### Sample: changing `set_camera_orientation` / `move_camera`

`set_camera_orientation` gets there in one step and `move_camera` glides over; one sample walks through five entry points — `phi`/`theta` → `gamma` → `zoom` → `frame_center` — and resets everything at the end.

```python
from real_time_manim import ThreeDScene, ThreeDAxes, Cube, Text, \
    BLUE, YELLOW, UP, ORIGIN, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   # instantly swap the top caption text without spending animation time
    cap.become(Text(text, font_size=30, color=YELLOW).to_edge(UP))

class OrientationDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        axes = ThreeDAxes()   # default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   # a blue cube as a reference
        cap = Text("", font_size=30, color=YELLOW)   # top caption text (content swapped later)
        self.add_fixed_in_frame_mobjects(cap)   # pin the title to the screen
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(axes, cube, cap)   # add the three objects to the scene

        say(cap, "set_camera_orientation phi=30° theta=-60°")
        self.set_camera_orientation(phi=30 * DEGREES, theta=-60 * DEGREES)   # jump to a new view instantly, no animation
        win.play(Wait(0.8))   # pause 0.8s to see the result

        say(cap, "move_camera phi=70° theta=-45°")
        self.move_camera(phi=70 * DEGREES, theta=-45 * DEGREES, run_time=1.2)   # animate the orbit to the new phi/theta
        win.play(Wait(0.3))   # pause 0.3s

        say(cap, "move_camera gamma=25°")
        self.move_camera(gamma=25 * DEGREES, run_time=0.8)   # roll the frame 25° about the view axis
        win.play(Wait(0.3))   # pause 0.3s

        say(cap, "move_camera zoom=1.8")
        self.move_camera(zoom=1.8, run_time=0.8)   # zoom in to 1.8x
        win.play(Wait(0.3))   # pause 0.3s

        say(cap, "move_camera frame_center=cube")
        self.move_camera(frame_center=cube, run_time=0.8)   # move the frame centre onto the cube
        win.play(Wait(0.6))   # pause 0.6s

        say(cap, "set_camera_orientation reset all")
        self.set_camera_orientation(phi=70 * DEGREES, theta=-135 * DEGREES,   # reset phi/theta/gamma/zoom in one step
                                    gamma=0, zoom=1, frame_center=ORIGIN)
        win.play(Wait(0.5))   # pause 0.5s and finish
        win.close()   # close the RTM window
```

What this code does: it first uses `set_camera_orientation` to jump to a `phi=30°` top-down view in one frame, then uses `move_camera` to glide over to `70°/-45°`, and then the same `move_camera` demonstrates three "local" parameters in turn: `gamma` rolls the frame 25°, `zoom=1.8` zooms in, and `frame_center=cube` moves the frame centre onto the cube (the first two do not move the centre, this one does not change the zoom).

Finally one `set_camera_orientation` resets `phi`/`theta`/`gamma`/`zoom`/`frame_center` all at once, and the camera returns to the classic oblique full view.

<video src="assets/RTM output/02-ThreeDScene-camera.mp4" controls width="560"></video>

> Note: `set_camera_orientation` has no animation (a one-frame jump); for a smooth transition use `move_camera`. `move_camera` calls `self.play` internally, so under RTM you must first write `self.play = win.play`, or the camera will not move. Angles are all in radians, so `25 * DEGREES` is 25°.
>
> When resetting, don't forget `frame_center=ORIGIN` — with `phi/theta` alone, the frame centre you moved earlier stays where it was.
>
> Also: the `zoom` **constructor parameter** has always worked, but runtime `move_camera(zoom=…)` / `set_zoom` only really took effect in RTM on 2026-10-17 (before that `camera_state` read `camera.zoom`, a write-once dead attribute of `ThreeDCamera`, while the animation drove `zoom_tracker` / `get_zoom`), so this clip's `zoom=1.8` zoom-in had no effect at the time; this entry stands after the fix.

### begin/stop_ambient_camera_rotation, begin/stop_3dillusion_camera_rotation

Ambient rotation turns steadily about an axis (a negative value reverses it), and the turn only advances "during playback", so pairing it with `Wait` gives the familiar orbiting transition; the 3D-illusion rotation wobbles slightly around the current view to create a sense of depth.

```python
def begin_ambient_camera_rotation(self, rate: float = 0.02, about: str = "theta") -> None:
def stop_ambient_camera_rotation(self, about: str = "theta") -> None:
def begin_3dillusion_camera_rotation(self, rate: float = 1, origin_phi: float | None = None, origin_theta: float | None = None) -> None:
def stop_3dillusion_camera_rotation(self) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `rate` | `float` | `0.02` (illusion rotation `1`) | radians turned per second / wobble speed; **accepts** any real number, the sample uses `0.15`, `0.2`; a negative value reverses it |
| `about` | `str` | `"theta"` | which axis to turn about: one of `"theta"` (orbit about the vertical axis), `"phi"` (pitch), `"gamma"` (roll) |
| `origin_phi` | `float \| None` | `None` (takes the current value) | the polar angle the illusion wobbles around, normally leave empty |
| `origin_theta` | `float \| None` | `None` (takes the current value) | the azimuth the illusion wobbles around, normally leave empty |

> **Returns**: none (the `about` of `stop_*` and `begin_*` must come in pairs).

#### Sample: changing the ambient rotation / 3D illusion

Ambient rotation turns steadily about an axis, and while it turns the frame must be "in playback" (under RTM that means during `win.play(Wait(...))`); the 3D illusion wobbles slightly around the current view.

```python
from real_time_manim import ThreeDScene, ThreeDAxes, Cube, Text, \
    BLUE, YELLOW, UP, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   # instantly swap the top caption text without spending animation time
    cap.become(Text(text, font_size=30, color=YELLOW).to_edge(UP))

class RotationDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # scene methods call self.play internally, so wire it to the window first
        axes = ThreeDAxes()   # default 3D axes
        cube = Cube(side_length=1.5).set_color(BLUE)   # a blue cube as a reference
        cap = Text("", font_size=30, color=YELLOW)   # top caption text (content swapped later)
        self.add_fixed_in_frame_mobjects(cap)   # pin the title to the screen
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(axes, cube, cap)   # add the three objects to the scene
        self.set_camera_orientation(phi=60 * DEGREES, theta=-90 * DEGREES)   # set an oblique view first

        say(cap, "ambient rate=0.15 about=theta")
        self.begin_ambient_camera_rotation(rate=0.15, about="theta")   # orbit steadily about the vertical axis, 0.15 radians per second
        win.play(Wait(1.6))   # keep waiting while it turns, so the frame keeps rotating
        self.stop_ambient_camera_rotation()   # stop (about must match the one passed to begin)

        say(cap, "ambient rate=0.2 about=phi")
        self.begin_ambient_camera_rotation(rate=0.2, about="phi")   # switch to turning about the polar-angle direction
        win.play(Wait(1.6))   # keep waiting while it turns
        self.stop_ambient_camera_rotation(about="phi")   # stop

        say(cap, "3dillusion rate=1")
        self.begin_3dillusion_camera_rotation(rate=1)   # wobble slightly around the current view for a sense of depth
        win.play(Wait(1.6))   # keep waiting while it wobbles
        self.stop_3dillusion_camera_rotation()   # stop
        win.play(Wait(0.3))   # pause 0.3s and finish
        win.close()   # close the RTM window
```

What this code does: it first sets the camera to an oblique view, then starts three rotation segments: the first orbits steadily about the vertical axis (`about="theta"`) for 1.6 seconds and stops; the second switches to `about="phi"` and turns in the pitch direction for another 1.6 seconds, and `stop` gets the same `about` passed back; the third starts the 3D-illusion rotation (`rate=1`), the frame wobbles slightly around the current view to give a sense of depth, and finally it stops and finishes.

Throughout, the top title stays facing the viewer because it is pinned to the screen.

<video src="assets/RTM output/02-ThreeDScene-rotation.mp4" controls width="560"></video>

> Note: the `about` of `stop_*` must match the one passed to `begin_*` (`theta` and `phi` each stop their own; pass the wrong one and it will not stop).
>
> Rotation only advances "during playback", which under RTM means it turns during waits such as `win.play(Wait(1.6))` — don't switch to a form that does not enter the playback loop. The constructor parameter `ambient_camera_rotation` does not have this effect (see sample 1); to rotate you must call the method.

### add/remove_fixed_in_frame_mobjects, add/remove_fixed_orientation_mobjects

`add_fixed_in_frame_mobjects` "pins" an object to the screen (both position and orientation are locked, so it does not move however the camera turns — good for titles and formulas in a 3D scene); `add_fixed_orientation_mobjects` locks only the **orientation** (the text always faces the camera, but its position is still in 3D space and it pans with the camera's perspective); `remove_*` releases the corresponding lock.

```python
def add_fixed_in_frame_mobjects(self, *mobjects: Mobject) -> None:
def remove_fixed_in_frame_mobjects(self, *mobjects: Mobject) -> None:
def add_fixed_orientation_mobjects(self, *mobjects: Mobject, **kwargs: Any) -> None:
def remove_fixed_orientation_mobjects(self, *mobjects: Mobject) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | — | the objects to pin (or release); several can be passed at once |
| `**kwargs` | `Any` | — | `add_fixed_orientation_mobjects` only: `use_static_center_func: bool`, `center_func: Callable`, which control the centre-point algorithm of the orientation lock, normally leave empty |

> **Returns**: none.

#### Sample: changing `add_fixed_in_frame_mobjects`

Two objects in the same scene: the title uses `fixed_in_frame` (position and orientation both locked) and the label uses `fixed_orientation` (orientation only); after orbiting once they are released and both immediately turn back into ordinary 3D objects.

```python
from real_time_manim import ThreeDScene, ThreeDAxes, Cube, Text, \
    BLUE, GREEN, YELLOW, UP, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

class FixedDemo(ThreeDScene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        axes = ThreeDAxes()   # default 3D axes
        cube = Cube(side_length=1.2).set_color(BLUE)   # a blue cube as a reference
        title = Text("fixed_in_frame", font_size=34, color=YELLOW)   # title demonstrating screen pinning
        tag = Text("fixed_orientation", font_size=26, color=GREEN)   # label demonstrating the orientation lock
        tag.next_to(cube, UP)   # put the label above the cube in 3D space
        self.add_fixed_in_frame_mobjects(title)   # title: position and orientation both locked to the screen
        title.to_edge(UP)   # move the title to the top of the frame
        self.add_fixed_orientation_mobjects(tag)   # label: orientation locked only, position still in 3D space
        self.add(axes, cube, tag)   # add the axes, the cube and the label to the scene (the title is already pinned)
        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES)   # set an oblique view
        win.play(Wait(0.8))   # pause 0.8s to see the position of the two objects

        self.move_camera(theta=-140 * DEGREES, run_time=1.6)   # orbit 90°: the title does not budge, the label moves with the cube in the frame
        win.play(Wait(0.4))   # pause 0.4s

        self.remove_fixed_in_frame_mobjects(title)   # release the screen pin
        self.remove_fixed_orientation_mobjects(tag)   # release the orientation lock
        self.move_camera(theta=-190 * DEGREES, run_time=1.4)   # orbit once more: both objects become ordinary 3D objects and tilt with the view
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: it first sets an oblique view to see the initial state of the two objects — the yellow title stuck to the top of the screen, the green label hanging above the cube in 3D space.

The first `move_camera` orbits 90°: the title does not budge (it is pinned), while the label shifts position in the frame with the cube (because its position is still in 3D space). Then both locks are released, and on the second orbit both become ordinary 3D objects and tilt with the view, turning round to the back together.

<video src="assets/RTM output/02-ThreeDScene-fixed.mp4" controls width="560"></video>

> Note: `add_fixed_in_frame_mobjects` adds the object **straight to the scene**, so there is no need for `self.add(...)` again (that is why the title does not appear among the arguments of `self.add` in the sample); `remove_*` only releases the lock, and the object stays in the scene.
>
> For text that should "always face the camera but still be pushed along by perspective" (such as a label stuck to an object) use `fixed_orientation`; for something completely still (titles, captions) use `fixed_in_frame`.

### class SpecialThreeDScene

An enhanced `ThreeDScene`: shading and exponential projection are on by default, and it brings its own default parameters for a set of 3D axes and a sphere.

Companion methods: `get_axes()` builds 3D axes, `get_sphere(**kwargs)` builds a sphere, `get_default_camera_position()` returns the default view dict, and `set_camera_to_default_position()` sets the camera back to the default oblique view.

> Upstream `manim` 0.21 has **three bugs** in this subclass (it reads `self.renderer` during construction, the default `three_d_axes_config` contains the removed `tick_frequency`, and `get_axes` uses the removed `axis.tick_marks`); inheriting it as-is crashes under command-line rendering too.
>
> The sample gives three workarounds; copy them and rendering works.

```python
def __init__(self, cut_axes_at_radius: bool = True, camera_config: dict = {"should_apply_shading": True, "exponential_projection": True}, three_d_axes_config: dict = {...}, sphere_config: dict = {"radius": 2, "resolution": (24, 48)}, default_angled_camera_position: dict = {"phi": 70 * DEGREES, "theta": -110 * DEGREES}, low_quality_config: dict = {...}, **kwargs: Any) -> None:
def get_axes(self) -> ThreeDAxes:
def get_sphere(self, **kwargs: Any) -> Surface:
def get_default_camera_position(self) -> dict:
def set_camera_to_default_position(self) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `cut_axes_at_radius` | `bool` | `True` | cut the axes off at the sphere's radius (instead of extending forever); **accepts** `False` to let the axes run through the sphere |
| `camera_config` | `dict` | `{"should_apply_shading": True, "exponential_projection": True}` | shading + exponential projection; normally leave alone |
| `three_d_axes_config` | `dict` | see the source | the parameters of `get_axes()`; the upstream default contains the defunct `tick_frequency`, so the sample swaps in its own `AXIS_CFG` |
| `sphere_config` | `dict` | `{"radius": 2, "resolution": (24, 48)}` | the default parameters of `get_sphere()`, which `get_sphere(**kwargs)` can override on the spot |
| `default_angled_camera_position` | `dict` | `{"phi": 70*DEGREES, "theta": -110*DEGREES}` | the subclass's own default oblique view (note it is `-110°`, not the `-135°` stored by `ThreeDScene`) |
| `low_quality_config` | `dict` | see the source | **not worth bothering with**: RTM is always 1080p60, so this low-quality override never triggers |
| `**kwargs` | `Any` | — | forwarded to `ThreeDScene.__init__` |

> **Returns**: none (constructs an instance).

#### Sample: changing `SpecialThreeDScene`

`SpecialThreeDScene` brings cut-off axes, a translucent sphere and its own default view; the three workarounds map to the three upstream bugs and are written in the comments.

```python
from types import SimpleNamespace

from real_time_manim import SpecialThreeDScene, ThreeDAxes, VGroup, Line, \
    VectorizedPoint, Text, config, BLUE, YELLOW, UP, DEGREES
from real_time_manim.vulkan_bind import MLWindow, Wait

# upstream manim 0.21 bug 2: the tick_frequency in the default three_d_axes_config
# no longer exists in 0.21's NumberLine, so passing it as-is raises TypeError; drop that entry
AXIS_CFG = {
    "num_axis_pieces": 1,
    "axis_config": {
        "unit_size": 2,
        "numbers_with_elongated_ticks": [0, 1, 2],
        "stroke_width": 2,
    },
}


class SpecialDemo(SpecialThreeDScene):
    def __init__(self, **kwargs):
        # upstream manim 0.21 bug 1: SpecialThreeDScene reads self.renderer
        # before super().__init__(), so stuff in a stand-in that only carries camera_config
        self.renderer = SimpleNamespace(
            camera_config={"pixel_width": config.pixel_width})
        super().__init__(three_d_axes_config=AXIS_CFG, **kwargs)   # swap out the default axes config that carries tick_frequency

    def get_axes(self):
        # upstream manim 0.21 bug 3: NumberLine no longer has a tick_marks attribute,
        # so use get_tick_marks() instead; the rest is word for word from the manim source
        axes = ThreeDAxes(**self.three_d_axes_config)
        for axis in axes:
            if self.cut_axes_at_radius:
                p0 = axis.get_start()
                p1 = axis.number_to_point(-1)
                p2 = axis.number_to_point(1)
                p3 = axis.get_end()
                new_pieces = VGroup(Line(p0, p1), Line(p1, p2), Line(p2, p3))
                for piece in new_pieces:
                    piece.shade_in_3d = True
                new_pieces.match_style(axis.pieces)
                axis.pieces.submobjects = new_pieces.submobjects
            for tick in axis.get_tick_marks():
                tick.add(VectorizedPoint(1.5 * tick.get_center()))
        return axes

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # move_camera calls self.play internally, so wire it to the window first
        axes = self.get_axes()   # built from three_d_axes_config; the axes are cut off at the sphere's radius
        sphere = self.get_sphere(color=BLUE, fill_opacity=0.55)   # sphere_config defaults radius=2, resolution=(24, 48)
        cap = Text("SpecialThreeDScene", font_size=32, color=YELLOW)   # top title
        self.add_fixed_in_frame_mobjects(cap)   # pin the title to the screen
        cap.to_edge(UP)   # move the title to the top of the frame
        self.add(axes, sphere, cap)   # add the axes, the sphere and the title to the scene
        self.set_camera_to_default_position()   # back to default_angled_camera_position (phi=70° theta=-110°)
        print("default view:", self.get_default_camera_position())   # print the default view to the console
        win.play(Wait(0.8))   # pause 0.8s to see the default oblique view
        self.move_camera(phi=50 * DEGREES, theta=-150 * DEGREES, run_time=1.4)   # orbit to show the sense of depth
        win.play(Wait(0.4))   # pause 0.4s and finish
        win.close()   # close the RTM window
```

What this code does: it first pads over the upstream bugs with three workarounds (a `renderer` stand-in, dropping `tick_frequency`, overriding `get_axes`), then builds the "cut off at the sphere's radius" axes and the translucent sphere from the config, and pins the title.

`set_camera_to_default_position()` returns to this subclass's own default oblique view (the console also prints the contents of `get_default_camera_position()`), and after a 0.8-second pause `move_camera` orbits once to show the sense of depth.

<video src="assets/RTM output/02-ThreeDScene-special.mp4" controls width="560"></video>

> Note: all three workarounds are required (the `self.renderer` stand-in, dropping `tick_frequency`, `get_tick_marks()`); missing any one of them crashes, so just copy them — they are not RTM-specific patches, and plain command-line rendering needs them too.
>
> The default view of `SpecialThreeDScene` is `phi=70° theta=-110°`, which is not the same as the `-135°` stored in `ThreeDScene`'s constructor, so don't mix them.
>
> `low_quality_config` is meant for `-ql` low-quality rendering; RTM is always 1080p60, so it is never reached.

---

See also: [ThreeDCamera](../Cameras/03-ThreeDCamera.md), [MovingCameraScene](01-MovingCameraScene.md), [Scene Basics](../Scenes/01-Scene-Basics.md)
