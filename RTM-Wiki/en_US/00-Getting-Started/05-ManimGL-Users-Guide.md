# ManimGL users' guide

If you've written animations with **ManimGL** (3b1b's interactive `manimgl` version) before, this page maps its functions onto their real-time-manim counterparts. RTM is a **real-time rendering engine** like manimGL (manimGL uses OpenGL; RTM uses Vulkan and is 1.8–2.8× faster), but the interaction model is completely different: RTM has **no `manimgl` command line, no mid-animation `embed`, and no live code reload** — interaction is replaced by the "frame preview window".

## Function mapping table

| ManimGL | RTM | Notes |
| --- | --- | --- |
| `manimgl scene.py` (pops a window and plays the animation) | run the script's `construct` directly, or `FramePreview(S).run()` | In RTM the window is created by `MLWindow` inside `construct` |
| `manimgl scene.py -w` (write video) | `fast_record_scene(S, out_path="out.mp4")` | Offline fast render, frame-exact |
| `manimgl scene.py -w -o` (auto-open after writing) | open the mp4 yourself | No auto-open |
| `-l / -m / -h` quality flags | none | The only quality is 1920×1080@60 |
| `self.embed()` (drop into a Python REPL mid-animation) | none | To "stop at a frame", use `FramePreview` scrubbing |
| `self.wait()` popup input box | `FramePreview`'s `p` (play) / `s` (save PNG) / `q` (quit) | No in-scene input box |
| `self.wait(stop_condition=...)` | `win.play(Wait(..., stop_condition=...))` | Kept; but only takes effect during forward playback (unsafe when scrubbing) |
| Live code reload (live edit) | none | Edit, then rerun the script |
| `%%manim -w` IPython magic | none | Run scripts directly, no magic |
| `config.renderer = "opengl"` | none | RTM is always Vulkan; no choice |
| `-s, --skip_animations` (jump to the end) | `FrameServer.save_frame(fs.duration, path)` | Any frame in O(1), including the last one |
| `gui` panel (pyqt widgets) | none | The only control bar is the frame preview one (text box / slider) |
| `self.add_sound(...)` | same name | Works; `gain` is in **dB** |
| `from manimlib import *` | `from real_time_manim import *` | RTM's namespace is **ManimCE 0.21.0**, not manimGL's `manimlib` — class and animation names are mostly the same; where details differ, CE wins |

## Minimal scene shape

In manimGL, `construct` calls `self.play(...)` directly; in RTM there's one extra window object:

```python
from real_time_manim import *
from real_time_manim.record import fast_record_scene

class MyScene(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window (the size is force-corrected to 1920×1080)
        win.scene = self   # bind the scene to the window (required)
        circle = Circle(color=YELLOW).set_fill(YELLOW, 0.5)
        win.play(FadeIn(circle), run_time=1.0)   # fade in a circle over 1 second
        win.play(circle.animate.shift(RIGHT * 3), run_time=1.0)   # move the circle right
        win.play(Wait(0.5))   # wait 0.5 seconds
        win.close()   # close the window (required, otherwise the video never lands on disk)

fast_record_scene(MyScene, "my_scene.mp4")# export to my_scene.mp4 in the project directory
```

As in manimGL, animations are pure functions of `alpha` (time), so any frame can be computed instantly — the entry point has just changed from "code reload + `embed`" to the [frame preview](03-Recording-Methods.md) scrubber.

## Error mapping

| What you did | What you'll see | Fix |
| --- | --- | --- |
| `import manimlib` or `import manim` before `import real_time_manim` | `RuntimeWarning` (class identities come from the external copy) | Always import `real_time_manim` first |
| Used `self.embed()` / `interactive_embed` | Attribute doesn't exist | Use `FramePreview` to find frames |
| Forgot `win.scene = self` | `RuntimeError: win.play() called before the scene was bound...` | Bind it inside `construct` |
| Forgot `win.close()` | Empty/incomplete output file | Call `win.close()` at the end |
| Passed a bare Mobject to `play` | `TypeError: Unexpected argument ... passed to MLWindow.play()` | Wrap it in `FadeIn`/`Create`, or `self.add(...)` first |
| Used manimGL `manimlib`-only classes | Not importable, or behaves differently | Write the class names of ManimCE 0.21.0 (that's what RTM's namespace is) |

---

See also: [Quickstart](02-Quickstart.md) · [Recording methods](03-Recording-Methods.md) · [ManimCE users' guide](04-ManimCE-Users-Guide.md)
