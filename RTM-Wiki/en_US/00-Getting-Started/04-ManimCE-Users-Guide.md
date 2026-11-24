# ManimCE users' guide

If you've written animations with **ManimCE** (the `manim` command line) before, this page maps every function onto its real-time-manim counterpart. **RTM has no `manim` command, no command-line flags, and it doesn't read `manim.cfg`.**

## Fastest migration (three steps)

1. Change the import from `from manim import ...` to `from real_time_manim import ...` (RTM ships a full ManimCE 0.21.0 — shapes, colors and animations are used **exactly the same way**);
2. Add two lines at the start of every `construct`: `win = MLWindow(960, 540)` and `win.scene = self`, plus `win.close()` at the end;
3. Replace the command-line render with `fast_record_scene(SceneName, out_path="xxx.mp4")`.

## Function mapping table

| ManimCE | RTM | Notes |
| --- | --- | --- |
| `manim -qh scene.py Hello` | `fast_record_scene(Hello, out_path="out.mp4")` | The command line doesn't exist at all; you render through functions |
| `from manim import *` | `from real_time_manim import *` | The same namespace (RTM ships ManimCE) |
| `self.play(...)` | `win.play(...)` | In RTM, playback goes through the window; `self.play` also works after the window is bound, but scene methods that call `self.play` internally (like `move_camera`) need `self.play = win.play` first |
| `self.wait(1)` | `win.play(Wait(1))` | `Wait` is imported from `real_time_manim.vulkan_bind` (also in the top-level `from real_time_manim import *`) |
| `-ql / -qm / -qh / -qp / -qk` | none | The only quality is 1920×1080@60; anything else is force-corrected and prints `[rtm] forcing ...` |
| `--fps 30` | none | Frame rate is 60 only |
| `-o name` | `out_path="xxx.mp4"` | Pass a file path ending in `.mp4` directly |
| `--format png` / `-s` (save last frame) | `FrameServer.save_frame(t, path)` / `segment=(a, b)` | Save any frame as PNG in O(1); export a segment as a directory of BMPs |
| `--save_sections` / `next_section` | none (produces no files) | Split into multiple scenes and record each, or cut with ffmpeg |
| `--renderer cairo/opengl` | none | RTM is always Vulkan; no choice |
| `-a, --write_all` | call each yourself | `fast_record_scene(A); fast_record_scene(B)` |
| `--dry_run` | `count_only=True` | Only counts frames; captures nothing, writes no files |
| `-t, --transparent` | none | Output is never transparent (black background) |
| `manim.cfg` | mostly not read | Only a few keys matter: `background_color` (the background color, changeable — see [Quality and output](../01-Scenes-and-Cameras/Configuration/01-Quality-and-Output.md)), `seed`, tex paths |
| `Scene.render()` / file_writer | doesn't exist | RTM runs `setup() → construct() → tear_down()` itself |
| `MathTex(...)` | same name | With typst installed it compiles via Typst — **no LaTeX needed**; without typst it falls back to LaTeX |
| `Tex(...)` | same name | Always needs LaTeX |
| `--enable_gui` / `-p --preview` | `FramePreview(S).run()` / `hidden=False` | Interactive preview is replaced by the frame preview window |
| `self.add_sound(...)` | same name | Works; `gain` is in **dB**, not a multiplier |
| `%%manim` Jupyter magic | none | Run scripts directly, no magic |

For a line-by-line quick reference of every flag, see [ManimCE CLI cheat sheet](../01-Scenes-and-Cameras/Configuration/04-ManimCE-CLI-Cheat-Sheet.md).

## Minimal scene shape

```python
from real_time_manim import *
from real_time_manim.record import fast_record_scene

class MyScene(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window (the size is force-corrected to 1920×1080)
        win.scene = self   # bind the scene to the window (required)
        sq = Square(color=BLUE).set_fill(BLUE, 0.5)
        win.play(Create(sq), run_time=1.0)   # draw the square over 1 second
        win.play(sq.animate.scale(1.5), run_time=1.0)   # enlarge the square
        win.play(Wait(0.5))   # wait 0.5 seconds
        win.close()   # close the window (required, otherwise the video never lands on disk)

fast_record_scene(MyScene, "my_scene.mp4")# export to my_scene.mp4 in the project directory
```

Note the two hard rules: without `win.scene = self`, `play` errors out immediately; without `win.close()`, the video encoding never finishes and the file may be empty.

## Error mapping

| What you did | What you'll see | Fix |
| --- | --- | --- |
| `import manim` before `import real_time_manim` | `RuntimeWarning` (class identities come from the external manim) | Always import `real_time_manim` first |
| Passed a bare Mobject to `play` | `TypeError: Unexpected argument ... passed to MLWindow.play()` | Wrap it in `FadeIn`/`Create`/`Write`, or `self.add(...)` first |
| Forgot `win.scene = self` | `RuntimeError: win.play() called before the scene was bound...` | Bind it inside `construct` |
| Forgot `win.close()` | Empty/incomplete output file | Call `win.close()` at the end |
| Put an unknown parameter in `play` | Warning printed: `unsupported keyword(s) ... ignored` | Only pass `run_time`/`rate_func`; give everything else to the animation constructors |
| Used `next_section` to split into sections | Nothing comes out | Split into scenes or cut with ffmpeg |
| Called `Scene.render()` | Nobody calls it; no output | Use `fast_record_scene` / `record_scene` |
| `MathTex` reports `latex error converting to dvi` | No LaTeX and the typst route failed | Install `real-time-manim[typst]`, or check the formula escaping (write it as a raw string) |

---

See also: [Quickstart](02-Quickstart.md) · [ManimCE CLI cheat sheet](../01-Scenes-and-Cameras/Configuration/04-ManimCE-CLI-Cheat-Sheet.md) · [RTM record and window options](../01-Scenes-and-Cameras/Configuration/05-RTM-Record-and-Window-Options.md)
