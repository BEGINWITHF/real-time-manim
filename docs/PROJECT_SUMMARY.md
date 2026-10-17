# real-time-manim — Project Architecture Summary

> A Vulkan-accelerated rendering backend for [ManimCE](https://www.manim.community/) that replaces Manim's default OpenGL/Cairo rendering pipeline with a custom native Vulkan renderer, providing real-time preview and fast offline video recording.

---

## 1. Project Purpose

real-time-manim intercepts standard Manim scene code and renders all mobjects through a **native Vulkan DLL** instead of Manim's built-in shaders. The goal is:

- **Faster rendering** — hardware-accelerated Vulkan instead of OpenGL/Cairo
- **Live preview** — a real-time window shows the animation as it plays
- **Fast offline recording** — pipe frames directly to ffmpeg without screenshot overhead
- **Zero API changes** — users write standard Manim `Scene` code; the Vulkan backend is injected transparently

---

## 2. Directory Structure

```
real-time-manim/
├── run.py                      # Entry point — monkey-patches manim, runs a Scene
├── pyproject.toml              # ManimCE 0.21 is bundled; deps are its third-party requirements
├── README.md                   # Project overview (roadmap)
│
├── real_time_manim/
│   ├── window/                 # MLWindow — the bridge between Python and the DLL, assembled from mixins
│   │   ├── core.py             # window creation, DLL binding, per-frame sync (CoreMixin)
│   │   ├── paint.py            # turning mobjects into native draw calls (PaintMixin)
│   │   ├── play.py             # the play loop and timeline renderer (PlayMixin)
│   │   ├── recording.py        # screenshots and video capture (RecordingMixin)
│   │   └── mathtex.py / scene.py / paint_order.py / patches.py
│   ├── vulkan_bind.py          # Facade re-exporting window/ — the old import path still works
│   ├── render/                 # mobject → DLL senders (formerly vulkan_shapes/text/util/image)
│   │   ├── shapes/             # ShapeMixin — rect, circle, ellipse, polygon, arrow, line, paths
│   │   ├── text/               # TextMixin — Text/MathTex glyphs and bezier paths
│   │   ├── hooks.py            # render hooks for manim's own animations
│   │   ├── image.py            # textured quads (image → Vulkan texture)
│   │   └── util.py             # Coordinate conversion (manim → screen), color helpers
│   ├── vulkan_shapes.py / vulkan_text.py / vulkan_util.py /
│   ├── vulkan_image.py / render_hooks.py   # shims re-exporting render/ (old import paths)
│   ├── rate_functions.py       # Easing functions (smooth, linear, there_and_back, etc.)
│   ├── utils/
│   │   └── paths.py            # Path helpers (straight_path, path_along_arc) for Transform
│   └── animations/
│       ├── __init__.py         # Exports all animation classes
│       ├── base.py             # Animation base class — timing, interpolation, opacity/rotation tracking
│       ├── transform.py        # Transform / ReplacementTransform
│       ├── fade_transform.py   # FadeTransform (crossfade with ghost shape-morph)
│       ├── create.py           # Create (stroke draw-on)
│       ├── write.py            # Write (text stroke + fill reveal)
│       ├── fade_in.py / fade_out.py
│       ├── grow_from_*.py      # GrowFromCenter, GrowFromEdge, GrowFromPoint, GrowArrow
│       ├── indicate.py         # Indicate (pulse effect)
│       ├── rotating.py / rotate.py
│       ├── succession.py / animation_group.py
│       ├── transform_matching_shapes.py / transform_matching_tex.py
│       ├── type_with_cursor.py / untype_with_cursor.py
│       ├── circumscribe.py, blink.py, show_passing_flash.py
│       ├── homotopy.py, move_along_path.py, apply_wave.py
│       └── text.py             # TextDecimalNumber
│
├── native/
│   ├── shared_types.h          # C structs: Rect, Circle, LineObj, EllipseObj, PolygonObj, etc.
│   ├── vulkan_render.h         # DLL API: Render_Init, Render_DrawScene, Render_Cleanup
│   ├── vulkan_core.h           # Vulkan instance/device/swapchain globals
│   ├── vulkan_core.c           # Vulkan initialization, swapchain, pipeline setup
│   ├── vulkan_renderer.c       # Render_DrawScene — builds vertex buffer, issues draw commands
│   ├── platform.c              # DLL entry point, shape arrays, AddRect/AddCircle/etc. API
│   ├── platform.h              # DLL function declarations
│   ├── screenshot.c            # SaveScreenshot (BMP capture via VkImage readback)
│   ├── draw/
│   │   ├── draw_common.h       # Shared vertex types for all draw modules
│   │   ├── draw_rect.c         # Rectangle vertex generation (fill + stroke)
│   │   ├── draw_circle.c       # Circle vertex generation
│   │   ├── draw_ellipse.c      # Ellipse vertex generation
│   │   ├── draw_line.c         # Line vertex generation
│   │   ├── draw_polygon.c      # Polygon vertex generation
│   │   ├── draw_dashed.c       # Dashed line vertex generation
│   │   ├── draw_arc.c          # Arc vertex generation
│   │   └── draw_text.c         # Text rendering (DirectWrite → Vulkan texture)
│   ├── shaders/
│   │   ├── vertex.vert         # Vertex shader (position + color pass-through)
│   │   └── fragment.frag       # Fragment shader (solid color with alpha)
│   └── build.bat               # Compilation script
│
├── examples/
│   ├── scenes/                 # 82 demo scenes showcasing all animation types, one module per topic
│   │   └── demo_scene.py       # facade re-exporting them all (+ the batch MP4 recorder)
│   └── timeline_seek.py        # timeline seeking demo
└── tests/                      # pytest suite
```

---

## 3. Rendering Pipeline (End-to-End Flow)

```
User Code (Scene)
       │
       ▼
   run.py ── monkey-patches manim, loads vulkan_render.dll via ctypes
       │
       ▼
   Scene.construct()
       │
       ▼
   MLWindow.play(Animation, ...)
       │
       ├─ begin(): set up animation state (opacity, transforms, ghost copies)
       │
       ├─ Main Loop (per frame):
       │   │
       │   ├─ Compute dt, advance simulated or real time
       │   │
       │   ├─ For each active animation:
       │   │   ├─ Compute alpha = elapsed / run_time
       │   │   ├─ Apply rate_func (smooth, linear, etc.)
       │   │   └─ anim.interpolate(alpha) → modifies mobject points/opacity
       │   │
       │   ├─ Apply VGroup rotation deltas
       │   ├─ Run mobject updaters
       │   │
       │   ├─ DLL tick() ── present the Vulkan frame
       │   │
       │   └─ sync(scene) ── walk scene.mobjects, dispatch each to DLL:
       │       │
       │       ├─ Detect mobject type (Square, Circle, Text, etc.)
       │       │
       │       ├─ Extract: position, size, rotation, fill/stroke color, opacity, progress
       │       │
       │       ├─ Convert manim coords → screen coords (manim_to_screen)
       │       │
       │       └─ Call DLL Add*() function:
       │           ├─ AddRect()      — rectangles, squares
       │           ├─ AddCircle()    — circles, dots
       │           ├─ AddEllipse()   — ellipses
       │           ├─ AddLine()      — lines, strokes, borders
       │           ├─ AddPolygon()   — triangles, polygons, arrow heads
       │           ├─ AddBezierPath()— complex curves, text glyphs, VMObjects
       │           ├─ AddDashedLine()— dashed lines
       │           ├─ AddArc()       — arcs
       │           └─ AddText()      — bitmap text fallback
       │
       ├─ finish(): restore mobject state, clean up scene
       │
       └─ (if recording) save frames → ffmpeg
```

---

## 4. Key Components in Detail

### 4.1. `run.py` — Entry Point

- Loads `vulkan_render.dll` via `ctypes.CDLL`
- **Monkey-patches** Manim's built-in classes (`Scene`, `Square`, `Circle`, `Text`, all animation classes, etc.) so they are replaced by custom versions from `core/`
- Sets up MiKTeX PATH for LaTeX rendering
- Parses CLI args: `run.py <scene_index> [--record <output.mp4>] [--record-fps <fps>]`
- Runs the selected `Scene` class, which internally creates a `MLWindow` instance

### 4.2. `MLWindow` (real_time_manim/vulkan_bind.py)

The central orchestrator. Key methods:

| Method | Purpose |
|--------|---------|
| `__init__(w, h)` | Opens a Vulkan window via DLL, initializes shape buffers |
| `play(*animations, **kwargs)` | Main animation loop — advances time, calls `interpolate()`, syncs scene to GPU |
| `sync(scene)` | Walks `scene.mobjects`, detects types, calls `_send_*()` dispatchers |
| `tick()` | Presents the current frame (calls `dll.Render_Present()`) |
| `screenshot(path)` | Captures the current frame as BMP via `dll.SaveScreenshot()` |
| `enable_fast_record(path, fps)` | Starts offline recording — pipes raw BMP frames to ffmpeg |
| `start_record(path, fps)` | Starts GDI-based recording (PrintWindow capture, fallback) |
| `stop_record()` | Stops recording, encodes frames to MP4 via ffmpeg |
| `close()` | Shuts down Vulkan via `dll.Vulkan_Shutdown()` |

**Mobject Dispatch** (`sync()` method):
- Checks `_transforming` flag — if set, routes through `_send_vmobject()` (bezier-based) instead of shape-specific dispatchers
- Falls through a type hierarchy: `Square` → `_send_square()`, `Circle` → `_send_circle()`, `Text` → `_send_text_bitmap()`, etc.
- Handles VGroups, Groups, TracedPath, and nested mobject trees

### 4.3. Shape Rendering (ShapeMixin + TextMixin)

Each shape type has a dedicated `_send_*()` method that:

1. Extracts mobject properties (position, size, rotation, color, opacity, stroke width)
2. Handles animation modifiers (`_vulkan_progress`, `_grow_scale`, `_grow_point`, `_rotation_about_point`)
3. Converts manim coordinates → screen pixel coordinates via `manim_to_screen()`
4. Calls the appropriate DLL function (`AddRect`, `AddCircle`, `AddLine`, etc.)

**Coordinate System** (`vulkan_util.py`):
```
manim_to_screen(x, y, w, h):
  frame_width = w * 8.0 / h     # manim's default frame height = 8 units
  sx = w / frame_width            # scale factor
  sy = h / 8.0
  cx, cy = w/2, h/2              # screen center
  return (cx + x*sx, cy - y*sy)  # manim Y-up → screen Y-down
```

### 4.4. Animation System (core/animations/)

A custom reimplementation of Manim's animation classes that works with the Vulkan renderer:

**Base `Animation` class** (`base.py`):
- Stores `mobject`, `run_time`, `rate_func`, `lag_ratio`
- `begin(t)`: records start time
- `interpolate(t)`: computes `alpha = (t - start_time) / run_time`, applies rate_func, calls `interpolate_mobject(alpha)`
- Uses global dictionaries (`_anim_opacity`, `_anim_rotation`, `_anim_rotation_delta`) keyed weakly BY THE MOBJECT ITSELF (not by `id(mob)`: an id-keyed entry outlives its owner and CPython reuses ids, so a freed mobject's verdict -- a faded-out 0.0 -- lands on the next mobject allocated at that address) to track per-mobject animation state without modifying mobject attributes

**Key Animation Types**:

| Animation | Behavior |
|-----------|----------|
| `Create` | Stroke draw-on: `_vulkan_progress` goes 0→1 |
| `Write` | Stroke draw-on + fill reveal per letter |
| `FadeIn/FadeOut` | Opacity 0→1 / 1→0: manim writes the eased value into the mobject's own `*_rgbas`, which every sender already folds into the primitive — so the opacity registry is **cleared to 1.0** for anything that has arrays (`_refresh_opacity`), otherwise the fade applied twice (measured: 0.084 vs CE's 0.084²). Only a `DashedLine`'s primitive ignores its arrays and still takes the animation's value |
| `Transform` | Shape morph: copies source→target, interpolates points each frame |
| `FadeTransform` | Crossfade: source fades out, ghost (stretched target copy) fades in with shape morph |
| `GrowFromCenter` | manim's own grows are Transforms: `interpolate` already scales the points, so no channel is written (`_write_grow` only stamps `_grow_scale`/`_grow_point` for the animations that do NOT move points -- `Flash`, `Circumscribe`) |
| `Indicate` | Temporary scale pulse |
| `Succession` | Sequential sub-animations |
| `AnimationGroup` | Parallel sub-animations |

### 4.5. Native Vulkan Layer (native/)

A Windows DLL (`vulkan_render.dll`) that:

1. **Initializes Vulkan**: instance, physical device, logical device, swapchain, render pass, pipeline, command buffers, semaphores
2. **Receives draw calls** from Python via exported C functions (`AddRect`, `AddCircle`, `AddLine`, `AddPolygon`, `AddBezierPath`, `AddText`, etc.)
3. **Stores shapes** in static arrays (`g_rects`, `g_circles`, etc.) with a command list (`g_draw_cmds`) tracking draw order
4. **Renders each frame**: converts shape data → triangle/line vertices → vertex buffer → Vulkan draw calls
5. **Captures screenshots**: reads back swapchain image to CPU memory, writes BMP header + pixel data

**DLL Exported Functions** (called via ctypes from Python):
```
Render_Init, Render_IsReady, Render_DrawScene, Render_Cleanup
Tick, Render_Present, SaveScreenshot
AddRect, AddCircle, AddLine, AddEllipse, AddPolygon, AddDashedLine, AddArc, AddText, AddBezierPath, AddLineStrip
```

### 4.6. Recording Modes

**Fast Record (pipe mode)** — default:
```
enable_fast_record(path="output.mp4", fps=60)
→ Saves each frame as BMP via SaveScreenshot()
→ Parses BMP pixel data (skip 54-byte header)
→ Pipes raw BGR24 frames to ffmpeg stdin
→ ffmpeg encodes to H.264 MP4
```

**Fast Record (BMP mode)** — multi-segment:
```
enable_fast_record(path="output_dir/", segment=(start, end))
→ Saves each frame as frame_NNNNNN.bmp in the directory
→ Batch-processing friendly for parallel rendering
```

**GDI Record** — fallback:
```
start_record(path="output.mp4", fps=60)
→ Background thread captures via PrintWindow/GDI BitBlt
→ Saves BMP frames, then encodes with ffmpeg at actual capture FPS
```

**Batch Rendering**:
```bash
for i in $(seq 1 79); do python run.py $i; done
```

---

## 5. Data Flow Summary

```
Manim Scene (Python)
    │
    ▼  monkey-patched classes
Custom Animation subclasses (core/animations/)
    │
    ▼  interpolate() modifies mobject points/opacity
MLWindow.sync() — type detection + coordinate conversion
    │
    ▼  ctypes calls
Native DLL (platform.c) — shape storage + command list
    │
    ▼  BuildVerticesFrom*() — shape → triangle vertices
Vulkan Pipeline (vulkan_core.c) — vertex buffer → GPU draw
    │
    ▼
Screen (Vulkan window) / BMP capture → ffmpeg → MP4
```

---

## 6. Supported Mobject Types

| Manim Class | Render Method | Notes |
|-------------|---------------|-------|
| `Square`, `Rectangle` | `_send_square` / `_send_rectangle` | Fill + stroke with progress |
| `Circle` | `_send_circle` | 48-segment tessellation |
| `Ellipse` | `_send_ellipse` | 48-segment tessellation |
| `Line`, `Arrow` | `_send_line` / `_send_arrow` | Arrow heads via AddPolygon |
| `Dot` | `_send_dot` | Rendered as filled circle |
| `DashedLine` | `_send_dashed_line` | Dash/gap pattern |
| `Arc` | `_send_arc` | Start angle + sweep |
| `Polygon`, `Triangle` | `_send_polygon` | Arbitrary vertices |
| `VGroup`, `Group` | Recursive `_send_vmobject` | Propagates rotation/grow to children |
| `Text`, `MathTex` | `_send_text_bitmap` / `_send_transformed_text` | Bezier paths + AddBezierPath |
| `TracedPath` | `_send_vmobject` (polyline mode) | Line strip with opacity gradient |
| `VMobject` (generic) | `_send_vmobject` | Bezier path rendering |

#### Stroke rasterisation: `_stroke_layers(px, alpha)`

Native widths are integers and a quad of native width `w` paints `w + 1` px, so a
sub-pixel stroke is drawn as an integer core laid over a `core + 1`-wide band at
`alpha * frac`. **Both cover the core pixels**, so at `alpha < 1` the two must be
solved together or they stack: an inner pixel came out `1-(1-a)(1-a*frac)`.

Opaque strokes saturate and hide it (which is why every width calibration was done
opaque), but a translucent one did not: a Square and a Circle posed statically at
`stroke_opacity = 0.345` peaked at 117/255 and 118/255 against CE's 93/255 and
91/255 (x1.26, x1.29), and a fading `DashedLine` came out 1.37x CE's dash. The
inner layer is now `1 - (1-alpha)/(1-alpha*frac)`, which is **exactly the old value
at `alpha == 1`** and lands the composite on `alpha` below it. Probes:
`_stroke_check.py` (static), `_fade_check.py` (fading), test
`test_closed_stroke_strip.py::test_stroke_layers_composite_onto_the_requested_alpha`.

---

## 7. Animation State Tracking

The system tracks per-mobject state via global dictionaries keyed by `id(mob)`:

| Dictionary | Purpose | Set By |
|------------|---------|--------|
| `_anim_opacity` | Current opacity (0.0–1.0) | FadeIn, FadeOut, Transform, Add |
| `_anim_rotation` | Current accumulated rotation (radians) | Rotate, Rotating, VGroup patch |
| `_anim_rotation_delta` | Per-frame rotation increment | Rotating, Rotate |

Special mobject attributes (set dynamically during animations):

| Attribute | Purpose |
|-----------|---------|
| `_vulkan_progress` | Stroke draw-on progress (0→1 for Create/Write) |
| `_vulkan_progress_lower` / `_upper` | Partial stroke range |
| `_transforming` | Flag: render via bezier path instead of shape dispatcher |
| `_grow_scale` / `_grow_point` | Scale animation origin |
| `_rotation_about_point` | Rotation pivot override |
| `_focus_on_dot` | Tag for FocusOn rendering |
| `_dot_max_opacity` | Cap opacity for subtle effects |

---

## 8. Dependencies

- **Python**: ManimCE 0.21 is **bundled** (`real_time_manim/manim/`, see its
  `UPSTREAM.md`) -- no `manim` install -- plus ManimCE's third-party
  requirements (`numpy`, `manimpango`, `svgelements`, `skia-pathops`, `pycairo`,
  `moderngl`, `scipy`, `networkx`, ... listed in `pyproject.toml`)
- **System**: Windows 10, Vulkan SDK, MiKTeX (for LaTeX/MathTex)
- **Build**: MSVC compiler (for native DLL), `build.bat`
- **Runtime**: `ffmpeg` on PATH (for video encoding)

---

## 9. How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run a demo scene (index into the gallery under examples/scenes)
python run.py 0          # DemoCreate
python run.py 1          # DemoWriteUnwrite
python run.py 5          # DemoTransformMatchingShapes

# Record to MP4
python run.py 0 --record output.mp4

# Batch render all demos
for i in $(seq 0 79); do python run.py $i; done
```

---

*Generated from source analysis — 2026-08-07*
