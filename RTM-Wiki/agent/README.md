# RTM agent wiki

> Reference for AI agents / bots. **Not optimized for human reading**: dense, structured, greppable.
> Human-facing version: [`../zh_CN/`](../zh_CN/README.md) (Chinese). This folder is its compressed reformat.
> Source of truth: the `real_time_manim/` source tree + `../zh_CN/`. On conflict, the source wins.

## 0. TL;DR — minimal runnable

```python
from real_time_manim import Scene, Square, Create, Wait, BLUE, YELLOW, Text, UP
from real_time_manim.vulkan_bind import MLWindow

class MyScene(Scene):
    def construct(self):
        win = MLWindow(960, 540)      # size is forced to 1920x1080 and prints a notice
        win.scene = self              # required: bind the manim Scene to the window
        win.play(Text("hi", color=YELLOW).to_edge(UP), run_time=0.5)
        win.play(Create(Square(color=BLUE)), run_time=1.0)
        win.play(Wait(0.5))
        win.close()                   # required: otherwise nothing is flushed / the run may not exit

# Offline render (no window, fastest, best for scripts/CI)
from real_time_manim.record import fast_record_scene
fast_record_scene(MyScene, "out.mp4")
```

## 1. What RTM is (facts)

- Package `real-time-manim`; import name `real_time_manim`; version `2.0.0` (`pyproject.toml`).
- A **Vulkan real-time rendering backend** for ManimCE. Not a Manim fork: it **drives** ManimCE's `Mobject`/`VMobject`/`Animation` data model.
- **Bundles ManimCE 0.21.0** (`real_time_manim/manim/`, `MANIM_BUNDLE_VERSION`). `import real_time_manim` re-exports the whole ManimCE namespace.
- **No `manim` CLI**. pip library + Python API only.
- Python `>=3.11`. Windows 10/11 out of the box; macOS needs a native lib build first (see `runtime.md`).

## 2. Hard constraints (read before writing code)

| Constraint | Value | Notes |
| --- | --- | --- |
| Output resolution | **fixed 1920×1080** | Any other size is corrected and prints `[rtm] forcing 1920x1080: ...` (`MLWindow.SUPPORTED_WIDTH/HEIGHT`) |
| Frame rate | **fixed 60 fps** | `SUPPORTED_FPS = 60` |
| Window | each Scene creates its own `MLWindow` | No global window; `win.scene = self` is a required binding |
| Teardown | must call `win.close()` | Without it nothing is flushed and the run may not exit |
| `import manim` | works, but **do not import it first** | If the process imports `manim` first, RTM uses that external copy and may warn (`RuntimeWarning`); import `real_time_manim` first to keep class identity |
| Runtime deps | see `pyproject.toml` | Needs a Vulkan GPU+driver; recording also needs `ffmpeg` on PATH |

## 3. Entry points / import paths

| Symbol | import | Notes |
| --- | --- | --- |
| All ManimCE classes (`Scene`/`Square`/`Create`/colors/rate funcs/…) | `from real_time_manim import ...` | Full namespace at top level |
| `MLWindow` | `from real_time_manim import MLWindow` or `from real_time_manim.vulkan_bind import MLWindow` | Lazy export; `vulkan_bind` is the legacy entry |
| Animations/shapes/utils (`Create`/`Wait`/`Square`/`ORIGIN`…) | `from real_time_manim.vulkan_bind import ...` | `vulkan_bind` re-exports common symbols |
| `fast_record_scene` / `record_scene` | `from real_time_manim.record import ...` | Also lazily available at top level |
| `FrameServer` | `from real_time_manim.frames import FrameServer` | Arbitrary-frame export |
| `FramePreview` | `from real_time_manim.preview import FramePreview` | Frame-scrub preview |
| `Timeline` | `from real_time_manim.timeline import Timeline` | Schedule mode (record first, render later) |
| `Typst` / `TypstMath` / `MathTypst` | `from real_time_manim import Typst, TypstMath` | Typst typesetting |
| RTM rate functions | `from real_time_manim import rate_functions` (module) | Shadows the ManimCE export of the same name |

## 4. Execution modes

| Use case | API | Traits |
| --- | --- | --- |
| Offline render (batch/CI/scripts) | `fast_record_scene(SceneCls, out, fps=60, hidden=True)` | Vulkan framebuffer readback → ffmpeg; fastest; no window |
| Real-time render (interactive) | `record_scene(SceneCls, out, fps=60)` | Visible window + background capture thread |
| Live preview | run `MLWindow(...)` directly | Watch the animation on screen |
| Arbitrary-frame export | `FrameServer` | Per-frame PNGs |
| Frame-scrub preview | `FramePreview` | Scrub the timeline |

## 5. Mental model (agent must-know)

- **Data model = ManimCE**: `Mobject`/`VMobject`/`Animation` are the single source of truth; RTM only rasterizes them to Vulkan. ManimCE geometry/color/animation semantics apply directly.
- **Two drivers**:
  - `win.play(*anims, run_time=..., subcaption=...)` — per-frame real-time render (`window/play.py`).
  - Schedule mode (`_schedule_mode=True`) — `play()` only **records** onto a timeline; later `build_timeline()` evaluates any frame on demand (`timeline.py`).
- **Paint order**: document order by default; `z_index` participates; under `ThreeDCamera` it is re-sorted by camera-space depth; `Camera(use_z_index=False)` disables the z sort (`window/paint_order.py`).
- **Custom-camera fallback**: a camera that overrides `capture_mobjects`/`get_frame` (and is not one of the handled ones: `MovingCamera`/`ThreeDCamera`/…) falls back to **per-frame full-screen rasterization** — correct but slow (`core.py::_rasterise_custom_camera`).
- **RTM vs CE**: RTM uses its own `play()` and does **not** drive ManimCE's `Scene.render()`/file-writer. It calls `Scene.setup()` → `construct()` → `tear_down()` itself, in order.
- **First formula render blocks**: `MathTex`/`Tex`/`Typst` compile synchronously at construction (~1–2 s cold). On a cold cache a **visible** window shows a small "compiling formula" popup (hidden/offline runs stay silent); the output is unaffected. See `runtime.md` → *Compile-wait popup*.
- **Param-table semantics** (from zh_CN): `能填` = allowed values; `不建议` = allowed but discouraged; `不接线 / 未接线` = RTM ignores it.

## 6. File map

| File | Covers | zh_CN source |
| --- | --- | --- |
| `runtime.md` | Install, run, `MLWindow`, recording, arbitrary frames, Timeline | `00-快速开始/` |
| `scene-camera.md` | Scene lifecycle, play/wait, add-to-screen, sections/audio, dedicated scenes, cameras, config | `01-场景与相机/` |
| `mobject.md` | Construct/containers, placement, measure, transform, style, copy, updaters, animate syntax, ValueTracker | `02-Mobject通用/` |
| `animation-transform.md` | Create/erase, transforms, matching transforms, emphasis, grow, fade | `03-动画/` (first half) |
| `animation-motion.md` | Move/rotate, wait/rate, grouping, common params, updater animations, text/number | `03-动画/` (second half) |
| `geometry.md` | Basic shapes, lines/arrows, arrow tips, polygons, rectangles, angle/box annotations, labels, boolean ops, containers, VMobject style | `04-图形与文本/` (geometry) |
| `text.md` | Text, LaTeX, fragments, Typst, code block, numbers, matrix, table, image/SVG, braces | `04-图形与文本/` (text) |
| `coords-charts.md` | NumberLine, Axes, coordinate conversion, grid/complex plane, curves, area, polar/3D, BarChart, probability, ticks | `05-坐标系与图表/` |
| `three-d.md` | 3D primitives, surfaces, polyhedra, 3D utils | `06-三维/` |
| `graph-vector.md` | Graph/DiGraph, vector field, streamlines | `07-图论与向量场/` |
| `utils.md` | Colors, rate functions, direction constants, vector/geometry utils, path/sequence utils | `08-工具/` |
| `gotchas.md` | Cross-domain pitfalls + error→cause→fix catalog | site-wide `提醒`/`无法演示` |
| `patterns.md` | Idiomatic recipes (scene skeleton, common tasks) | site-wide samples |

## 7. Entry schema (uniform across this folder)

```text
### `Name`
```python
<exact signature, verbatim from source / zh_CN>
```
- `ret`: return value (type + key methods)
- `args`:
  - `name: type = default` — meaning / constraint (range, required?, RTM deviation)
- `notes`:
  - pitfalls, RTM-specific behavior, differences from CE
- `errs`:
  - `ErrorType: "raw message"` — cause → fix
- `see`: ../zh_CN/<path>.md
- `eg`: (optional) ≤6-line minimal snippet
```

Conventions: **write everything in English**; keep identifiers/code/error strings verbatim; no marketing prose; if a detail is unknown, omit it or mark `TODO` — **do not invent**.

## 8. Suggested read order (bot)

1. Read this README for the global picture and constraints.
2. Read the domain file for the task (see file map).
3. For errors/edge behavior, read `gotchas.md`.
4. For "how do I combine these", read `patterns.md`.
5. For fuller prose / complete sample code, fall back to the matching `../zh_CN/` page (each entry gives a `see` path).
