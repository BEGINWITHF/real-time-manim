# Real-Time-Manim (RTM)

A **Vulkan-accelerated, real-time rendering backend for
[ManimCE](https://www.manim.community/)**. RTM drives ManimCE's own `Mobject` /
`Animation` model through a native Vulkan pipeline, so the same scene can be
watched **live in a window**, seeked to any frame instantly, and recorded to MP4
several times faster than the default renderer.

> **About this page.** This is the package overview, kept plain-text on purpose
> (PyPI renders neither images nor diagrams). The illustrated README, the manual
> and a source-level walkthrough live in the
> [repository](https://github.com/BEGINWITHF/real-time-manim) and its
> [wiki](https://github.com/BEGINWITHF/real-time-manim/wiki).

---

## Install

```bash
pip install real-time-manim
```

The Windows wheel bundles `vulkan_core.dll`, so there is no build step. You need
a Vulkan-capable GPU/driver, and `ffmpeg` on `PATH` to record video.

**macOS is supported as well** — build the dylib once, then install and run as
usual:

```bash
brew install molten-vk          # MoltenVK provides the Vulkan layer on macOS
bash native/build_mac.sh        # -> dist/release/vulkan_core.dylib
```

---

## Quick start

```python
from real_time_manim import Scene, Square, BLUE
from real_time_manim.vulkan_bind import MLWindow, Create, Wait
from real_time_manim.record import fast_record_scene

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)      # a real-time window
        win.scene = self              # required
        sq = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)
        win.play(Create(sq), run_time=1.0)
        win.play(Wait(0.5))
        win.close()                   # required

fast_record_scene(Hello)              # -> ~/Downloads/output.mp4
```

`MLWindow` opens the live window; `fast_record_scene` / `record_scene` record to
MP4. Recording starts and stops around the scene automatically, and the
transient `media/` folder is cleaned up afterwards.

> **No separate ManimCE install, and no `import manim`.** RTM bundles ManimCE
> **0.21.0** and re-exports its whole namespace (`Scene`, every mobject and
> animation, the colours, the rate functions). Import `real_time_manim` — not
> `manim` — or class identity splits.

---

## Highlights

- **Real-time window.** `MLWindow` renders at 1920×1080 @ 60 fps with no export
  step between code and picture.
- **Fast recording.** `fast_record_scene(...)` reads back frames straight into
  `ffmpeg` — around **1.9–2.8×** faster than ManimCE Cairo (a 15-second scene:
  4.6–6.6 s versus 12.8–13.9 s), windowless and at full speed by default.
- **Parallel frames.** `jobs="auto"` splits a long scene across worker processes
  and concatenates their segments losslessly.
- **Frame-accurate seeking.** Any frame of a prepared scene is produced in O(1),
  which is what makes both the frame preview and the parallel recorder possible.
- **Full ManimCE.** Existing scenes run unchanged, including code that still
  writes `from manim import ...`.
- **Math without LaTeX.** `MathTex` strings inside a convertible subset are
  compiled by an in-process **Typst** backend (`RTM_TYPST=0` disables it); both
  Typst and LaTeX results are content-hashed and cached.
- **Animations.** Every animation family is available: transforms, drawing,
  fading, movement/scaling, text, rotation, effects and grouping/timing — see
  the manual for the full list.

---

## Recording

```python
fast_record_scene(MyScene)                    # offline readback -> ~/Downloads/output.mp4
fast_record_scene(MyScene, "out.mp4", jobs=4) # 4 worker processes
record_scene(MyScene, "live.mp4")             # capture a visible window in real time
```

Both accept a `Scene` subclass, a `Scene` instance or a no-arg callable, and
return a dict `{out_path, windows, files, with_audio}`. With `out_path` omitted
the output lands at `~/Downloads/output.mp4`; a scene that opens several windows
gets `_part2`, `_part3`, … suffixes.

---

## Constraints

- Output is **fixed at 1920×1080 @ 60 fps**; any other value is corrected and
  reported with a `[rtm] forcing ...` line.
- **One window per process**, and `win.scene = self` plus `win.close()` are
  required.
- There is no `manim` CLI — RTM is a library: `MLWindow`, the recorders,
  `FrameServer`, `FramePreview`.

---

## How it works

```
Manim Scene
   |  MLWindow.play(...)
   v
type dispatch  (_send per mobject)
   |  ctypes FFI
   v
vulkan_core.dll  ->  Vulkan pipeline  ->  GPU
   |  optional framebuffer readback
   v
ffmpeg  ->  MP4
```

A `Scene` builds mobjects and calls `MLWindow.play(...)`; the Python layer walks
the mobject tree and dispatches each shape to a type-specific sender; those cross
a `ctypes` boundary into `vulkan_core.dll`, which emits vertices and submits them
to a Vulkan pipeline. Every frame is presented to the window, and can optionally
be read back and piped to `ffmpeg` as an MP4.

---

## LaTeX / Typst cache

Compiled formulas are content-hashed, so unchanged math is never recompiled:

```python
from real_time_manim import restore_tex_cache, save_tex_cache, clear_tex_cache

restore_tex_cache("tex_cache")   # before: warm manim's SVG folder from a saved cache
# ... run your Tex / MathTex scenes ...
save_tex_cache("tex_cache")      # after: stash newly compiled SVGs

clear_tex_cache()                # wipe <media>/Tex and tex_cache/ (dry_run=True to preview)
```

---

## Documentation

- **Repository** — <https://github.com/BEGINWITHF/real-time-manim>
- **Wiki (English)** — a source-level walkthrough in eight chapters, from
  [01 Overview](https://github.com/BEGINWITHF/real-time-manim/wiki/01-Overview)
  to
  [08 Native Layer](https://github.com/BEGINWITHF/real-time-manim/wiki/08-Native-Layer)
- **Chinese manual** — 144 pages, one section per API, each with a rendered
  sample clip:
  [RTM-Wiki/zh_CN](https://github.com/BEGINWITHF/real-time-manim/blob/C-version-clean/RTM-Wiki/zh_CN/README.md)
- **Agent manual** — the same material condensed for AI agents:
  [RTM-Wiki/agent](https://github.com/BEGINWITHF/real-time-manim/blob/C-version-clean/RTM-Wiki/agent/README.md)

---

## License

[MIT](https://github.com/BEGINWITHF/real-time-manim/blob/C-version-clean/LICENSE)

## Acknowledgments

- [ManimCE](https://www.manim.community/) — the mathematical animation engine
- [stb_truetype](https://github.com/nothings/stb) — TrueType font rasterizer
- [Vulkan](https://www.vulkan.org/) — the graphics API
- [Typst](https://typst.app/) — the in-process math typesetting backend
