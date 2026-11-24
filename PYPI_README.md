# Real-Time-Manim (RTM)

![Real-Time-Manim V2 banner](https://raw.githubusercontent.com/Team-Axioviva/real-time-manim/main/banner.jpg)

[![PyPI](https://img.shields.io/pypi/v/real-time-manim.svg)](https://pypi.org/project/real-time-manim/)
[![Python](https://img.shields.io/pypi/pyversions/real-time-manim.svg)](https://pypi.org/project/real-time-manim/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2B%20%7C%20macOS-lightgrey.svg)](https://github.com/Team-Axioviva/real-time-manim)
[![Downloads](https://img.shields.io/pypi/dm/real-time-manim.svg)](https://pypi.org/project/real-time-manim/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/Team-Axioviva/real-time-manim/blob/main/LICENSE)
[![AI agents](https://img.shields.io/badge/AI%20agents-llms.txt-blueviolet.svg)](https://github.com/Team-Axioviva/real-time-manim/blob/main/llms.txt)

A **Vulkan-accelerated, real-time rendering backend for
[ManimCE](https://www.manim.community/)**. RTM drives ManimCE's own `Mobject` /
`Animation` model through a native Vulkan pipeline, so the same scene can be
watched **live**, seeked to any frame instantly, and recorded to MP4 several
times faster than the default renderer.

> **Start here:** the [project website](https://team-axioviva.github.io/real-time-manim_website/)
> for demos and the interactive wiki graph, and the
> [GitHub Wiki](https://github.com/Team-Axioviva/real-time-manim/wiki) for the
> source-level walkthrough. 中文说明：
> [README.zh-CN.md](https://github.com/Team-Axioviva/real-time-manim/blob/main/README.zh-CN.md).
>
> **AI agents:** start with
> [`RTM-Wiki/agent/README.md`](https://github.com/Team-Axioviva/real-time-manim/blob/main/RTM-Wiki/agent/README.md)
> — the whole API condensed into one greppable reference, with `gotchas.md`,
> `patterns.md` and `llms.txt`.

---

## Install

```bash
pip install real-time-manim
pip install "real-time-manim[typst]"   # optional: in-process Typst math backend
```

The wheel bundles the platform binary (`vulkan_core.dll` on Windows,
`vulkan_core.dylib` on Apple Silicon); no native build step. You need a Vulkan
GPU/driver, and `ffmpeg` on `PATH` to record. **macOS** also needs MoltenVK at
runtime (`brew install molten-vk`); Intel Macs can build the dylib with
`bash native/build_mac.sh`.

---

## Quick start

```python
from real_time_manim import Scene, Square, Create, Wait, BLUE, MLWindow
from real_time_manim.record import fast_record_scene

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)      # size is forced to 1920x1080
        win.scene = self              # required
        win.play(Create(Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)), run_time=1.0)
        win.play(Wait(0.5))
        win.close()                   # required: flushes and finishes the encoder

fast_record_scene(Hello)              # -> ~/Downloads/output.mp4
```

`MLWindow` is also a context manager: `with MLWindow(...) as win:` closes it on
the way out.

> **No separate ManimCE install, and no `import manim`.** RTM bundles ManimCE
> **0.21.0** and re-exports its whole namespace. Import `real_time_manim` — not
> `manim` — or class identity splits.

---

## Three ways to output

| output | API | notes |
| --- | --- | --- |
| **Live window** | `MLWindow` | render and watch in real time; no file |
| **MP4** | `fast_record_scene` / `record_scene` | hidden offline (fastest) or visible real-time; `jobs=N` splits frames |
| **PNG frames** | `FrameServer` / `FramePreview` | any frame at any `t` in O(1), or scrub the timeline |

```python
from real_time_manim import MLWindow, Square, Create, FrameServer, FramePreview
from real_time_manim.record import fast_record_scene, record_scene

# 1. Live window
win = MLWindow(1920, 1080)
win.scene = MyScene()
win.play(Create(Square()), run_time=1.0)
win.close()

# 2. MP4: hidden/offline (fastest), parallel, or visible/real-time
fast_record_scene(MyScene)
fast_record_scene(MyScene, "out.mp4", jobs=4)
record_scene(MyScene, "live.mp4")

# 3. PNG frames: one frame, a list of times, or interactive scrubbing
fs = FrameServer(MyScene)
fs.save_frame(2.5, "frame.png")
fs.export_frames("frames/", [0.0, 1.5, 3.0])
fs.close()
FramePreview(MyScene).run()
```

The recorders accept a `Scene` subclass / instance / no-arg callable and return
`{out_path, windows, files, with_audio}`. `jobs="auto"` splits only for an
importable single-window scene of at least 240 frames; move expensive pure setup
into `prepare()` so every worker shares it.

---

## Highlights

- **Real-time window** — 1920x1080 @ 60 fps, no export step.
- **Fast recording** — around **1.9-2.8x** faster than ManimCE Cairo. Static
  roots are baked into one texture per play; a `Wait` is encoded without
  redrawing the scene.
- **Parallel frames** — `jobs="auto"` splits a long scene across workers;
  `prepare()` / `shared_prepare()` keep expensive setup from being repeated.
- **Frame-accurate seeking** — any frame of a prepared scene in O(1), via
  `FrameServer` / `FramePreview`.
- **Depth-tested 3D** — `MeshMobject` / `MeshBatch` / `MeshGroup` use a GPU depth
  buffer, so intersecting and self-occluding surfaces resolve per pixel.
- **Lighting** — CPU-baked Manim shading (`shade=True`) or a native material
  (`lit=True` + `win.set_mesh_light(...)`).
- **Post-processing** — optional native bloom and ACES/Reinhard tonemapping.
- **Full ManimCE** — existing scenes run unchanged, including
  `from manim import ...` code.
- **Math without LaTeX** — `MathTex` routes to an in-process **Typst** backend
  (`RTM_TYPST=0` disables it).

**New in 2.0.13:** documentation refresh — a redesigned package page, a Chinese
README, and the recovered pull-request history in `PR_HISTORY.md`. No engine
changes: `native/` is identical to 2.0.12, and `real_time_manim/` differs only
in the version fallback.

---

## 3D and post-processing

`MeshMobject` is a real Manim mobject, so `shift`, `rotate` and `.animate` move
the mesh:

```python
import numpy as np
from real_time_manim import (
    ThreeDScene, Surface, MeshMobject, BLUE, UP, DEGREES, MLWindow,
)

class Terrain(ThreeDScene):
    def construct(self):
        win = MLWindow(1920, 1080)
        win.scene = self
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)
        surf = Surface(
            lambda u, v: np.array([u, v, 0.35 * np.sin(2 * u) * np.cos(2 * v)]),
            u_range=(-2, 2), v_range=(-2, 2), resolution=(48, 48), fill_color=BLUE,
        ).set_stroke(width=0)
        mesh = MeshMobject.from_surface(surf, shade=True)
        self.add(mesh)
        win.play(mesh.animate.shift(0.4 * UP), run_time=1.0)
        win.close()
```

- Static mesh: `win.set_mesh(MeshBatch.from_surface(surf))` after
  `surf.set_shade_in_3d(False)`. It is a world-space snapshot; do not `add` the
  surface too.
- Native material: `MeshMobject.from_surface(surf, lit=True)` plus
  `win.set_mesh_light(ambient=0.25, diffuse=0.9, specular=0.4, shininess=48)`.
  `shade=True` and `lit=True` are mutually exclusive.
- Bloom/tonemap: `win.set_post(bloom=0.8, threshold=0.75, tonemap="aces")`;
  `set_post(False)` disables it, `RTM_POST=1` enables it everywhere.
- `from_surface()` bakes opaque quads only; the mesh has no per-pixel
  transparency sort. `MeshBatch.MAX_QUADS = 131072`, one native mesh per frame.

---

## Constraints

- Output is **fixed at 1920x1080 @ 60 fps**; other values are corrected with a
  `[rtm] forcing ...` line.
- **One window per process**; `win.scene = self` and `win.close()` are required
  (`atexit` is only a best-effort fallback and cannot report encoder errors).
- There is no `manim` CLI — RTM is a library: `MLWindow`, the recorders,
  `FrameServer`, `FramePreview`, `Timeline`.

---

## License

MIT. ManimCE, Vulkan and Typst belong to their respective projects.
