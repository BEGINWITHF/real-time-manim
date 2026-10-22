# Play and wait: the play / wait family

The core of animation driving. In RTM you always write playback as `win.play(...)`, and waits are best written as `win.play(Wait(...))`. The manim forms `self.wait` / `self.pause` / `self.wait_until` also work, but you must first wire `self.play` to `win.play`.

## Parameters

### `Scene.play` (RTM form: `win.play(...)`)

```python
def play(self, *args: Animation | Mobject | _AnimationBuilder, subcaption: str | None = None, subcaption_duration: float | None = None, subcaption_offset: float = 0, **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*args` | `Animation \| Mobject \| _AnimationBuilder` | — | the animations to play; several are allowed (**played in parallel**, total duration is the largest `run_time`); `.animate...` builders are resolved automatically |
| `subcaption` | `str \| None` | `None` | subcaption text: this play's subcaption is recorded from "play start clock + `subcaption_offset`"; when recording ends a same-named `.srt` is written next to the output mp4 automatically (see [Subcaptions and sound](04-Subcaptions-and-Sound.md)) |
| `subcaption_duration` | `float \| None` | `None` | how long the subcaption shows (seconds); omitted = this play's actual duration |
| `subcaption_offset` | `float` | `0` | start offset (seconds): subcaption clock = play start time + this offset |
| `**kwargs` | `Any` | — | only two are recognized: `run_time=seconds` (overrides the duration of each animation in this play), `rate_func=function` (overrides the rate curve); other keywords print a warning instead of being silently swallowed |

> **Returns**: none. In RTM the window method is `win.play(...)`; if your scene method internally calls `self.play` (e.g. `move_camera`, the internal playback of `Write`), first write `self.play = win.play` to wire it up.

#### Sample: `win.play` parallelism / run_time / rate_func / `.animate`

Putting two animations in one `play` is parallel; `rate_func=linear` is constant speed, and if omitted the default is smooth (slow at both ends, fast in the middle).

```python
from real_time_manim import (
    Scene,
    Square, Circle, Text,
    YELLOW,
    UP, DOWN, LEFT, RIGHT,
    FadeIn, Write, linear,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class PlayDemo(Scene):
    RUN_TIME = 0.6   #animation duration: change it to 1.2 to see a half-speed version

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        a = Circle(color=RED).shift(LEFT * 2.5)   #the circle on the left
        b = Square(color=GREEN).shift(RIGHT * 2.5)   #the square on the right
        self.add(a, b)   #put both objects on screen
        win.play(FadeIn(a), FadeIn(b), run_time=self.RUN_TIME)   #several animations in one play = played in parallel
        win.play(a.animate.shift(RIGHT * 1.2), run_time=self.RUN_TIME, rate_func=linear)   #".animate" builder + linear rate
        win.play(a.animate.shift(LEFT * 1.2), run_time=self.RUN_TIME)   #default smooth rate: slow at both ends, fast in the middle
        win.play(Write(Text("win.play", font_size=42, color=YELLOW).to_edge(DOWN)), run_time=self.RUN_TIME)   #Write writing animation
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: it first `FadeIn`s the circle and the square at the same time (two animations in one `play` = parallel, total duration is `RUN_TIME`); then uses `.animate` to move the circle right at constant speed and back with the default smooth rate — same displacement, different rate curves; finally `Write` writes a line of text and it waits 0.4 seconds to finish.

Increase `RUN_TIME` and all four animation segments slow down together.

<video src="assets/RTM output/03-Play-and-Wait-play.mp4" controls width="560"></video>

> Note: `run_time` / `rate_func` are this play's common parameters and override **each** animation's own setting; to give two animations different durations, split them into two `win.play` calls. For the available `rate_func` curves see [Rate functions](../../08-Utilities/02-Rate-Functions.md).

### Waiting: `Wait` / `Scene.wait` / `Scene.pause` / `Scene.wait_until`

```python
# RTM's Wait (imported from real_time_manim.vulkan_bind), same params as manim's Wait
class Wait(Animation):
    def __init__(self, run_time=1.0, rate_func=None, stop_condition=None, frozen_frame=None, **kwargs):

# the manim wait forms (all become one playback internally, so wire self.play = win.play first)
def wait(self, duration: float = DEFAULT_WAIT_TIME, stop_condition: Callable[[], bool] | None = None, frozen_frame: bool | None = None) -> None:
def pause(self, duration: float = DEFAULT_WAIT_TIME) -> None:
def wait_until(self, stop_condition: Callable[[], bool], max_time: float = 60) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `duration` / `run_time` | `float` | `DEFAULT_WAIT_TIME` (=1.0) | wait duration (seconds); must be > 0, writing 0 or a negative raises `ValueError` directly like manim (see `validate_run_time`). Prefer `win.play(Wait(0.5))` (RTM's `Wait`); `self.wait(0.5)` is equivalent |
| `stop_condition` | `Callable[[], bool] \| None` | `None` | evaluated every frame: the condition function is called once after each frame is drawn, and if true the wait ends early (same check timing as manim). Note: it only takes effect during forward playback (`play` / `wait`); random-access frame extraction (`FrameServer`) still renders the full duration. When the condition function raises, the wait ends gracefully instead of crashing the whole play. It is mutually exclusive with `frozen_frame=True`; passing both raises `ValueError` (the same error as manim) |
| `frozen_frame` | `bool \| None` | `None` | controls whether the picture is "frozen" or "stepped" during the wait: `True` = no updaters are driven for the whole wait and the picture is frozen (`self.pause` is exactly this); `False` = updaters in the scene are still driven frame by frame; `None` (default) decides automatically — frozen when there is no updater, scene-level update function or `stop_condition`, otherwise stepped. The same rules as manim |
| `max_time` | `float` | `60` | `wait_until` only: upper bound on the wait duration; if `stop_condition` becomes true early, it stops short of this |

#### Sample: four ways to wait

`win.play(Wait(...))`, `self.wait` and `self.pause` behave identically (frozen picture, honest duration). `self.wait_until`'s condition is evaluated every frame and ends early as soon as it is true — `lambda: True` is true after the first frame, so the wait renders only one extra frame.

```python
from real_time_manim import (
    Scene,
    Square, Text,
    BLUE, YELLOW,
    UP, DOWN,
    FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class WaitDemo(Scene):
    FLAVOR = "play_wait"   #wait form: four flavors, see the subclasses below

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   #self.wait / self.pause / self.wait_until all call self.play internally, so wire it up first
        tag = Text(self.FLAVOR, font_size=40, color=YELLOW).to_edge(UP)   #show the current form at the top of the screen
        sq = Square(color=BLUE).shift(DOWN)   #a static square, to make it clear the picture really doesn't move during the wait
        self.add(tag, sq)   #add the label and the square to the scene
        win.play(FadeIn(sq), run_time=0.3)   #fade in for 0.3s first
        if self.FLAVOR == "play_wait":
            win.play(Wait(0.5))   #RTM form: win.play(Wait(seconds))
        elif self.FLAVOR == "self_wait":
            self.wait(0.5)   #manim form: forwarded through self.play, waits 0.5s
        elif self.FLAVOR == "self_pause":
            self.pause(0.3)   #a pause that freezes the picture, waits 0.3s
        else:
            self.wait_until(lambda: True, max_time=0.3)   #conditional wait; the condition is true after the first frame, so the wait ends immediately
        win.close()   #close the RTM window


class WaitSelf(WaitDemo):
    FLAVOR = "self_wait"   #switch to self.wait


class WaitPause(WaitDemo):
    FLAVOR = "self_pause"   #switch to self.pause


class WaitUntil(WaitDemo):
    FLAVOR = "wait_until"   #switch to self.wait_until
```

What this code does: the top of the screen shows which wait form is in use, the square fades in for 0.3 seconds, then one of the four waits is chosen by `FLAVOR`, during which the picture is completely frozen.

The four video segments are, in order:

- `win.play(Wait(0.5))` (48 frames = 18 frames fade-in + 30 frames wait)
- `self.wait(0.5)` (48 frames)
- `self.pause(0.3)` (36 frames)
- `self.wait_until(lambda: True, max_time=0.3)` (19 frames = 18 frames fade-in + 1 frame wait)

The last segment's condition is evaluated every frame and is true after the first frame, so the wait ends while much of `max_time` is left — that is exactly the "wait until some condition" usage.

<video src="assets/RTM output/03-Play-and-Wait-wait.mp4" controls width="560"></video>

> Note: three gotchas.
>
> - ① `self.wait` / `self.pause` / `self.wait_until` all call `self.play` internally; forget `self.play = win.play` and they take manim's own render path, so the picture will not appear in the RTM window.
> - ② In the wait family only `win.play(Wait(...))` uses RTM's `Wait`; `self.wait` and friends use manim's `Wait`, which carries an empty `Mobject` and pushes one empty object into `scene.mobjects` on every wait (no effect on the picture, but `len(self.mobjects)` counts more).
> - ③ `stop_condition` is only evaluated frame by frame during forward playback: random-access frame extraction (`FrameServer` / `render_at`) still renders the full duration, so don't use it as random-access-safe event synchronization.

### `Scene.add_updater` / `Scene.remove_updater`

```python
def add_updater(self, func: Callable[[float], None]) -> None:
def remove_updater(self, func: Callable[[float], None]) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `func` | `Callable[[float], None]` | — | a scene-level update function called every frame with the frame interval `dt`; it runs after all mobject-level updaters have run (same order as manim). `remove_updater` takes it off the list, and it stops running immediately after |

Mobject-level updaters (`mobject.add_updater`) are driven every frame too, see [Updaters](../../02-Mobjects/08-Updaters.md); the two forms can be mixed.

#### Sample: scene-level vs mobject-level updater

In the same `wait`, the blue square (mobject-level updater) and the red square (scene-level updater) move up together; after both updaters are removed, both stop in the second `wait`.

```python
from real_time_manim import (
    Scene,
    Square, Text,
    BLUE, RED,
    UP, DOWN, LEFT, RIGHT,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class UpdaterDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it up first
        mob = Square(color=BLUE).shift(LEFT * 3 + DOWN * 2)   #a square driven by a mobject-level updater
        via_scene = Square(color=RED).shift(RIGHT * 3 + DOWN * 2)   #a square driven by a scene-level updater
        self.add(mob, via_scene)   #put both squares on screen
        self.add(Text("mobject.add_updater", font_size=24, color=BLUE).next_to(mob, UP))   #label on the left
        self.add(Text("scene.add_updater", font_size=24, color=RED).next_to(via_scene, UP))   #label on the right
        mob.add_updater(lambda m, dt: m.shift(UP * 0.03))   #mobject level: RTM drives it every frame, the square keeps moving up

        def scene_updater(dt):   #scene level: RTM drives it every frame
            via_scene.shift(UP * 0.03)

        self.add_updater(scene_updater)   #register the function on the scene
        win.play(Wait(0.5))   #wait 0.5s: the blue square moves up and the red square too
        self.remove_updater(scene_updater)   #remove the scene-level updater
        mob.clear_updaters()   #remove the mobject-level updater, the blue square stops
        win.play(Wait(0.5))   #wait another 0.5s: neither square moves
        win.close()   #close the RTM window
```

What this code does: it puts one square on each side; the left one has a mobject-level updater (shifts up 0.03 each frame), and the right one registers the same logic on the scene with `self.add_updater`.

During the first 0.5-second wait the two squares move up in sync — both updater kinds are now driven by RTM every frame, and the scene-level one runs after the mobject-level one (matching manim). After removing both updaters, both squares are still during the second wait.

<video src="assets/RTM output/03-Play-and-Wait-updater.mp4" controls width="560"></video>

> Note: a mobject-level updater's function signature is up to you: `func()`, `func(m)`, `func(m, dt)` all work (dispatched by the number of parameters); children nested in a `VGroup` are also driven one by one.
>
> A scene-level updater always takes one `dt` parameter, and changing other objects inside the updater works fine too.

### `Scene.validate_run_time`

```python
@classmethod
def validate_run_time(cls, run_time: float, method: Callable[[Any], Any], parameter_name: str = "run_time") -> float:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `run_time` | `float` | — | the duration to validate (seconds); must be positive, otherwise a `ValueError` is raised |
| `method` | `Callable` | — | the method shown in the error message (e.g. `self.play`) |
| `parameter_name` | `str` | `"run_time"` | the parameter name shown in the error message |

Returns the validated `float` (one shorter than a frame is warned about and clamped to one frame).

`win.play` **does** call it for you now: writing `run_time` as 0 or a negative raises `ValueError` directly (manim's friendly error), one shorter than a frame is warned about and clamped to one frame; `wait` / `wait_until` also go through `play` and are protected the same way. You can also call it manually when writing your own animation class that needs to validate duration; no video.

---

See also: [Scene basics](01-Scene-Basics.md) · [Subcaptions and sound](04-Subcaptions-and-Sound.md) · [play and wait parameters](../../03-Animations/Common/02-play-and-wait-Parameters.md) · [Updaters](../../02-Mobjects/08-Updaters.md) · [Recording video](../../00-Getting-Started/04-Recording-Video.md)
