# Scene.play / wait / pause / wait_until parameters

The entry point that drives every animation. RTM's scene does not use manim's renderer; playback is uniformly written `win.play(...)`, and for waiting the recommended form is `win.play(Wait(...))`.

## Parameters

### `Scene.play` (RTM form: `win.play(...)`)

```python
Scene.play(*anims, subcaption=None, subcaption_duration=None, subcaption_offset=0, **kwargs)
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*anims` | `Animation` / `.animate` builder | — | can be **several animation objects** (played in parallel, total duration = the largest `run_time`), or an `.animate` builder. **Does not accept** a bare method (`win.play(sq.shift, RIGHT)` raises `TypeError`), nor a bare mobject |
| `subcaption` | `str \| None` | `None` | play-level subcaption: RTM's `win.play` collects subcaption text in memory, paired with `subcaption_duration`; when recording ends `export_srt()` writes a `.srt` automatically next to the mp4 (demonstration in [Subcaptions and sound](../../01-Scenes-and-Cameras/Scenes/04-Subcaptions-and-Sound.md)). Calling `Scene.add_subcaption` directly writes to the same store and also lands in the `.srt` (reviewed 2026-10-19, `tests/test_wiki_marked_gaps.py`) |
| `subcaption_duration` | `float \| None` | `None` | how many seconds each subcaption stays (used with `subcaption`; no video on this page) |
| `subcaption_offset` | `float` | `0` | subcaption offset in seconds relative to the animation start (same as above) |
| `**kwargs` | `Any` | — | the keywords that take effect: `run_time=` overrides the duration of **every** animation in this play, `rate_func=` overrides the rate curve (setattr on each animation instance), and `path_arc=` / `path_arc_axis=` / `path_arc_centers=` / `path_func=` (since 2026-10-17; manim's `apply_*` propagates the arc angle through `play(...)`). Other keywords (e.g. play-level `lag_ratio=`) are **not supported**: they now print an explicit warning (listing the unrecognised item + "RTM does not support this parameter") instead of being silently swallowed; write staggering on the animation constructor or `AnimationGroup` |

> **Returns**: none. Key point: one `play`'s total duration = `max(anim.run_time)`; you can play a list/generator at once: `win.play(*[FadeIn(m) for m in mobs])`.

### `Wait` / `Scene.wait`

```python
# RTM's wait animation (imported from real_time_manim.vulkan_bind); the same parameters as manim's Wait
Wait(run_time=1.0, rate_func=None, stop_condition=None, frozen_frame=None, **kwargs)

def wait(self, duration=DEFAULT_WAIT_TIME, stop_condition=None, frozen_frame=None) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `duration` / `run_time` | `float` | `DEFAULT_WAIT_TIME` (=1.0) | wait duration in seconds. **What can be passed**: any positive number; the recommended form is `win.play(Wait(1.2))`, and `Scene.wait(1.2)` is equivalent (internally it plays a `Wait`) |
| `stop_condition` | `Callable[[], bool] \| None` | `None` | evaluated every frame: called once after each frame is drawn; when true the wait ends early. Mutually exclusive with `frozen_frame=True`; giving both raises `ValueError`. See [Play and wait (Scene chapter)](../../01-Scenes-and-Cameras/Scenes/03-Play-and-Wait.md) |
| `frozen_frame` | `bool \| None` | `None` | `True` = updaters are not driven at all during the wait and the image is frozen; `False` = it steps frame by frame as usual; `None` (default) decides automatically — freezes when there are no updaters, otherwise steps |

> **Returns**: none.

### `Scene.pause` / `Scene.wait_until`

```python
def pause(self, duration=DEFAULT_WAIT_TIME) -> None:
def wait_until(stop_condition, max_time=60) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `duration` (pause) | `float` | `1.0` | `pause` = `wait(..., frozen_frame=True)`: a forced still-frame pause during which updaters are not driven and the image is frozen |
| `stop_condition` (wait_until) | `Callable[[], bool]` | — | evaluated every frame; when the condition is true the wait ends immediately (without reaching `max_time`). It only takes effect during forward playback; random-access frame extraction still renders the full duration |
| `max_time` | `float` | `60` | the upper bound on the wait; if `stop_condition` becomes true early it does not reach this duration |

> **Returns**: none.

#### Sample: win.play's parallel/override parameters and Wait

One `play` plays several animations; the play-level `run_time=1.6` / `rate_func=linear` are setattr'd onto each animation in turn; then a list is unpacked with `win.play(*[FadeIn(m) for m in dots])`. Finally `win.play(Wait(1.2))` holds still for 1.2 seconds.

```python
import os
from real_time_manim import (
    BLUE,
    DOWN,
    GREEN,
    GREY_B,
    LEFT,
    ORANGE,
    PURPLE,
    RED,
    RIGHT,
    UP,
    YELLOW,
    Circle,
    Dot,
    Scene,
    Square,
    Text,
    Triangle,
    VGroup,
    linear,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    Create,
    FadeIn,
    FadeOut,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401

class Page_02_play_and_wait_Parameters(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # params w / h / hidden
        win.scene = self                          # param win.scene

        title = Text("02-Scene.play / wait parameters (win.play equivalent)", font_size=42, color=YELLOW).to_edge(UP)
        win.play(Write(title), run_time=0.8)

        # —— Step 1: one play with several animations + play-level run_time / rate_func ——
        l1 = Text("win.play(Create(sq), FadeIn(ci, scale=0.5),", font_size=30, color=GREY_B)
        l2 = Text("         run_time=1.6, rate_func=linear)   # setattr on each", font_size=30, color=GREY_B)
        sig1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).to_edge(UP).shift(DOWN * 1.05)
        sq = Square(side_length=1.3, color=BLUE).set_fill(BLUE, 0.5).shift(LEFT * 2.4 + DOWN * 2.0)
        ci = Circle(radius=0.68, color=GREEN).set_fill(GREEN, 0.5).shift(RIGHT * 2.4 + DOWN * 2.0)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.4)
        win.play(
            Create(sq),                          # param *anims: Create
            FadeIn(ci, scale=0.5),               # param *anims: FadeIn(scale)
            run_time=1.6,                        # param **kwargs: run_time (both animations stretched to 1.6s)
            rate_func=linear,                    # param **kwargs: rate_func
        )
        win.play(FadeOut(VGroup(sig1, sq, ci)), run_time=0.4)

        # —— Step 2: unpacking a list: win.play(*[FadeIn(m) for m in dots]) ——
        l3 = Text("win.play(*[FadeIn(m, shift=DOWN) for m in dots])",
                  font_size=30, color=GREY_B).to_edge(UP).shift(DOWN * 1.05)
        cols = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        dots = VGroup(*[Dot(radius=0.16, color=c).shift(LEFT * 5 + RIGHT * 2 * i + DOWN * 1.9)
                        for i, c in enumerate(cols)])
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)
        win.play(*[FadeIn(m, shift=DOWN) for m in dots])          # param *anims (list/generator unpacked)
        win.play(Wait(0.4))
        win.play(FadeOut(VGroup(l3, dots)), run_time=0.4)

        # —— Step 3: Wait(duration): ≈ Scene.wait(duration) ——
        l4 = Text("win.play(Wait(1.2))   #  ≡  self.wait(1.2)", font_size=30, color=GREY_B)
        l4.to_edge(UP).shift(DOWN * 1.05)
        tr = Triangle(color=ORANGE).scale(0.8).set_fill(ORANGE, 0.5).shift(DOWN * 1.9)
        txt = Text("still for 1.2 seconds", font_size=30, color=GREY_B).next_to(tr, DOWN, buff=0.45)
        win.play(FadeIn(l4, shift=DOWN), FadeIn(tr), FadeIn(txt), run_time=0.4)
        win.play(Wait(1.2))                                        # param duration=1.2
        win.play(Wait(0.4))

        win.play(FadeOut(VGroup(title, l4, tr, txt)), run_time=0.6)
        win.close()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    fast_record_scene(Page_02_play_and_wait_Parameters,
                      out_path=os.path.join(os.path.dirname(here), "RTM output", "02-play-and-wait-Parameters.mp4"),
                      fps=60, hidden=True, overwrite=True, cleanup=True, verbose=True)
```

What this code does: three steps —

- ① one `win.play` does `Create(sq)` and `FadeIn(ci, scale=0.5)` at the same time, and the play-level `run_time=1.6, rate_func=linear` stretches both animations to 1.6 seconds at constant speed (the effect of setattr on each);
- ② a list unpacking fades in six coloured dots at once (`*anims` accepts a generator/list);
- ③ a triangle and a "still for 1.2 seconds" label are placed, and `win.play(Wait(1.2))` waits the full 1.2 seconds without the image moving at all.

<video src="assets/RTM output/02-play-and-wait-Parameters.mp4" controls width="560"></video>

> Note: among `win.play(...)`'s keywords, `run_time` / `rate_func` take effect, and so do `path_arc` / `path_arc_axis` / `path_arc_centers` / `path_func` (since 2026-10-17; manim's `apply_*` uses these to pass the arc angle in). Other keywords print an explicit "RTM does not support this parameter" warning (no longer silently swallowed) — if you see the warning, check whether you wrote it at the play level by mistake.
>
> Use the `Wait` from `real_time_manim.vulkan_bind`, not manim's `Wait`.

> **2026-10-16 update**:
>
> - the three play-level `subcaption` parameters are wired up (in-memory collection + `export_srt()`, which writes a `.srt` next to the mp4 when recording ends; calling `Scene.add_subcaption` directly writes to the same store, reviewed 2026-10-19);
> - unrecognised play-level keywords now print an explicit warning instead of being silently ignored;
> - `Scene.pause` (= `wait(..., frozen_frame=True)`, a true still frame) and `Scene.wait_until` (the condition is evaluated every frame and truncates when true) are both implemented.

Not demonstrated:

- `subcaption` / `subcaption_duration` / `subcaption_offset` — the three play-level parameters are supported (in-memory collection + `export_srt`, which writes a `.srt` next to the mp4 when recording ends), not demonstrated here; see [Subcaptions and sound](../../01-Scenes-and-Cameras/Scenes/04-Subcaptions-and-Sound.md); calling `Scene.add_subcaption` directly writes the same store (reviewed 2026-10-19);
- `Scene.pause` / `Scene.wait_until` and `Wait`'s `stop_condition` / `frozen_frame` — supported, not demonstrated here; see [Play and wait (Scene chapter)](../../01-Scenes-and-Cameras/Scenes/03-Play-and-Wait.md);
- play-level `lag_ratio` — no video: RTM's `win.play` overrides the keywords `run_time` / `rate_func` (and since 2026-10-17 `path_arc` / `path_arc_axis` / `path_arc_centers` / `path_func`); a mistaken pass prints the "RTM does not support this parameter" warning (no longer silent), and staggering must be written on the animation constructor or `AnimationGroup`.

---

See also: [Lifecycle and common parameters](01-Lifecycle-and-Common-Parameters.md) · [.animate syntax](03-animate-Syntax.md) · [Play and wait (Scene chapter)](../../01-Scenes-and-Cameras/Scenes/03-Play-and-Wait.md)
