# runtime

> scope: install/run, minimal scene, `MLWindow`, recording (`fast_record_scene` / `record_scene`), `FrameServer`, `FramePreview`, `Timeline`, subcaption/SRT helpers, hard constraints.
> src: `real_time_manim/{__init__,record,frames,preview,timeline,vulkan_bind}.py`, `real_time_manim/window/{core,play,recording}.py`; wiki `../zh_CN/00-快速开始/`.

## Install

| Item | Value |
| --- | --- |
| Package | `real-time-manim` (import `real_time_manim`), version `2.0.0` (`pyproject.toml`) |
| Python | `>=3.11` |
| Windows 10/11 | wheel ships `vulkan_core.dll` + window icon; no build |
| macOS | build native lib first (below) |
| Vulkan | required at runtime: a Vulkan-capable GPU + driver |
| `ffmpeg` | required only for video recording; must be on `PATH` |

```bash
pip install real-time-manim
pip install "real-time-manim[typst]"   # = pip install "typst>=0.14"; optional Typst backend
```

macOS (build native lib, then install):

```bash
brew install molten-vk           # MoltenVK provides the Vulkan layer on macOS
bash native/build_mac.sh         # -> dist/release/vulkan_core.dylib
pip install real-time-manim
```

Verify (import succeeds = OK):

```python
from real_time_manim.vulkan_bind import MLWindow, Create, Wait
from real_time_manim.record import fast_record_scene
```

- `notes`:
  - Do **not** install ManimCE separately and do **not** `import manim` first. `import real_time_manim` installs its bundled ManimCE `0.21.0` (`MANIM_BUNDLE_VERSION`) as `sys.modules["manim"]` and re-exports the whole namespace. `from manim import ...` still works and gets the same classes.
  - If the process imports `manim` **before** `real_time_manim`, RTM uses that external copy and may emit `RuntimeWarning` (different class identity).
  - There is no `manim` CLI. Library + Python API only.
- `errs`:
  - `FileNotFoundError: "vulkan_core.dll not found. If running from source, build it with native/build.ps1 (requires Vulkan SDK + MinGW-w64)."` — native lib missing → on Windows reinstall the wheel; on macOS run `bash native/build_mac.sh`.
- `see`: ../zh_CN/00-快速开始/01-安装.md

## Minimal scene pattern

```python
from real_time_manim import Scene, Square, BLUE
from real_time_manim.vulkan_bind import MLWindow, Create, Wait
from real_time_manim.record import fast_record_scene

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)        # size forced to 1920x1080 (prints a notice)
        win.scene = self                # REQUIRED: bind the Scene to the window
        sq = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)
        win.play(Create(sq), run_time=1.0)
        win.play(Wait(0.5))
        win.close()                     # REQUIRED: else nothing is flushed / run may not exit

fast_record_scene(Hello)                # -> ~/Downloads/output.mp4
```

- `notes`:
  - Order inside `construct()`: open window → `win.scene = self` → `self.add(...)` mobjects (or animate introducers) → `win.play(...)` → `win.close()`.
  - RTM runs `Scene.setup()` → `construct()` → `tear_down()` itself (`record.scene_lifecycle`); it does **not** drive ManimCE's `Scene.render()`/file-writer.
- `see`: ../zh_CN/00-快速开始/02-第一个场景.md

## `MLWindow`

```python
class MLWindow(ShapeMixin, TextMixin, CoreMixin, PaintMixin, PlayMixin, RecordingMixin)
def __init__(self, w=SUPPORTED_WIDTH, h=SUPPORTED_HEIGHT, hidden=None)   # SUPPORTED_WIDTH=1920, SUPPORTED_HEIGHT=1080
```

- `ret`: one native Vulkan window (single output format: 1920×1080 @ 60 fps).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `w` | `int` | `1920` (forced) | width px; anything else is forced to 1920 |
| `h` | `int` | `1080` (forced) | height px; anything else is forced to 1080 |
| `hidden` | `bool \| None` | `None` → class `_hidden_default` | `True` builds hidden and never shows (offline record) |

- `notes`:
  - Class constants: `SUPPORTED_WIDTH = 1920`, `SUPPORTED_HEIGHT = 1080`, `SUPPORTED_FPS = 60`; class flags `_schedule_mode = False`, `_hidden_default = False`, registry `_registry = []`.
  - **One window per process at a time** (native DLL limit; Python side serialises via `_registry`).
  - Non-1920×1080 prints `[rtm] forcing 1920x1080: RTM supports high quality only (asked for {w}x{h})` and renders 1080p anyway — normal.
  - `win.scene` attribute defaults `None`; must be set to the Scene before `play()` or `play()` raises.
  - There is **no** `MLWindow.add`; put mobjects on screen with `self.add(...)` (manim `Scene.add`) or an introducer animation (`FadeIn`, `Create`).
- `errs`:
  - `FileNotFoundError: "vulkan_core.dll not found. ..."` — native lib missing.
  - `RuntimeError: "Vulkan_Init failed"` / `"Vulkan_InitEx failed"` — device/init failure.
- `see`: ../zh_CN/00-快速开始/03-实时窗口-MLWindow.md

### `MLWindow.scene`
- `args`: `scene: Scene = None` — the bound manim Scene (`win.scene = self`). Required; without it `play()` raises.

### `MLWindow.play`

```python
def play(self, *animations, subcaption=None, subcaption_duration=None, subcaption_offset=0, **kwargs)
```

- `ret`: none.
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `*animations` | `Animation \| _AnimationBuilder` | — | animations to play together; `.animate...` builders auto-resolved. A bare `Mobject` raises `TypeError` |
| `subcaption` | `str \| None` | `None` | SRT cue content (see subcaption helpers) |
| `subcaption_duration` | `float \| None` | `None` → the play's actual media run time | cue duration (s) |
| `subcaption_offset` | `float` | `0` | cue start offset from the play start (s) |
| `**kwargs` | — | — | honoured: `run_time`, `rate_func`, plus `path_arc` / `path_arc_axis` / `path_arc_centers` / `path_func`; all other keywords warn and are ignored |

- `notes`:
  - Play-level `run_time` / `rate_func` override **every** animation in that play (`SUPPORTED_PLAY_KWARGS = ("run_time", "rate_func") + ("path_arc", "path_arc_axis", "path_arc_centers", "path_func")`).
  - `run_time` ≤ 0 raises manim's `ValueError` (via `Scene.validate_run_time`); shorter than one frame clamps up with a warning.
  - Timeline-driven since 2.0.0: schedules a `Timeline` and renders each frame via O(1) `render_at`.
  - `self.wait` / `self.pause` / `self.wait_until` call `self.play` internally — set `self.play = win.play` to route them through RTM.
- `errs`:
  - `RuntimeError: "win.play() called before the scene was bound: run `win.scene = self` inside construct(), or pass the scene explicitly; without it RTM has nothing to draw or record."` — `win.scene` unset.
  - `TypeError: "Unexpected argument {Type} passed to MLWindow.play(): pass an Animation or a .animate(...) builder (or Scene.add() the mobject first)."` — passed a bare Mobject.
  - Warning (not an error): `[RTM] win.play(): unsupported keyword(s) {...} ignored -- RTM 不支持该参数: only run_time, rate_func, path_arc, path_arc_axis, path_arc_centers, path_func are honoured at play level; pass the rest to the animation constructor instead (e.g. Create(sq, lag_ratio=...)).`
- `see`: ../zh_CN/01-场景与相机/场景/03-播放与等待.md

### `MLWindow.close`

```python
def close(self)
```

- `ret`: none. Calls `_unregister()` + `Vulkan_Shutdown()`.
- `notes`:
  - **Required** at the end of `construct()`; without it nothing is flushed and the run may not exit.
  - Does **not** finish a record by itself. `fast_record_scene` / `record_scene` install `record._AutoRecord`, which runs `_finish_fast_record()` / `stop_record()` *before* the real `close()`. If you call `enable_fast_record(...)` manually you must call `win._finish_fast_record()` yourself.
  - If `_defer_close` is True (schedule mode) `close()` returns without shutting down.

### `MLWindow.screenshot`

```python
def screenshot(self, path)
```

- `ret`: native result (`self.dll.SaveScreenshot(path_bytes)`; nonzero = written).
- `args`: `path: str | bytes` — target image path; on Windows a `str` is encoded `mbcs` (UTF-8 fallback) because native opens via the ANSI C runtime.
- `notes`: works on a hidden window (reads the Vulkan framebuffer, not the composited screen).

### `MLWindow.request_readback`

```python
def request_readback(self)
```

- `ret`: none. Arms the next drawn frame to copy itself for readback; stores ring slot in `_readback_slot`.
- `notes`: must be called **before** the `tick()` that draws the frame you want (a presented swapchain image is owned by the presentation engine).

### `MLWindow.start_record` / `stop_record`

```python
def start_record(self, path="output.mp4", fps=60)
def stop_record(self)
```

- `ret`: none. Background capture thread (`_record_worker`) snapshots the live window via `SaveScreenshot` at `fps`.
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `path` | `str` | `"output.mp4"` | destination mp4 |
| `fps` | `int` | `60` (forced) | capture rate; non-60 prints `[rtm] forcing 60 fps: RTM supports high quality only (asked for {fps})` |

- `notes`:
  - `start_record` prints `[Record] Recording to {path} at {fps} fps`; `stop_record` encodes with ffmpeg (`libx264`, `yuv420p`, `-crf 18 -preset fast`), prints `[Record] Captured {n} frames in {d}s ({fps} fps), encoding to {output} ...` then `[Record] Saved: {output}`, and removes the temp frame dir.
  - Window must be visible (used by `record_scene`).
- `errs`:
  - `[Record] ffmpeg not found. Install ffmpeg and add it to PATH.` (also prints `[Record] Frames are in: {dir}`).
  - `[Record] ffmpeg failed: {stderr}`.
  - `[Record] No frames captured, aborting.`

### `MLWindow.enable_fast_record` / `_finish_fast_record`

```python
def enable_fast_record(self, path, fps=60, segment=None, hidden=True, count_only=False)
def _finish_fast_record(self)
```

- `ret`: none. Offline capture: frames read from the Vulkan framebuffer straight into ffmpeg.
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `path` | `str` | — | mp4 path (pipe mode) or directory (BMP `segment` mode) |
| `fps` | `int` | `60` (forced) | non-60 prints `[rtm] forcing 60 fps: RTM supports high quality only (asked for {fps})` |
| `segment` | `tuple \| None` | `None` | `(start_frame, end_frame)` → BMP directory instead of mp4 |
| `hidden` | `bool` | `True` | hide the window during capture |
| `count_only` | `bool` | `False` | only count frames; no capture / no GPU render |

- `notes`:
  - Pipe mode prints `[FastRecord] Pipe: {w}x{h} @ {fps} fps ({pix_fmt}) → {path}`; BMP mode prints `[FastRecord] BMP mode {segment} → {path}/`.
  - `_finish_fast_record` closes the ffmpeg pipe; prints `[FastRecord] Saved: {path} ({n} frames, {kb:.0f} KB)`, or `[FastRecord] BMP: {n} frames in {path}`, or `[FastRecord] Count: {n} frames`.
  - On ffmpeg failure: `[FastRecord] ffmpeg failed: {e}`.
  - Manual `enable_fast_record` + `close()` does **not** finish; call `_finish_fast_record()` yourself.

### `MLWindow.set_visible`

```python
def set_visible(self, visible=True)
```

- `ret`: none. Shows/hides the window after creation (`Vulkan_SetWindowVisible`, Win32 fallback by title). Sets `self.hidden = not visible` and toggles vsync pacing.

### `MLWindow.tick`

```python
def tick(self)
```

- `ret`: `bool` — `False` when the window is gone (`Vulkan_Tick` returned 0 / WM_QUIT), else `True`. Advances `frame_count`; updates `win_w`/`win_h` from the return value.
- `notes`: the per-frame present call; a `False` result means the frame was not drawn — stop walking.

### `MLWindow.sync`

```python
def sync(self, scene, angle=0.0)
```

- `ret`: none. Publishes the frame's camera viewport and walks `scene.mobjects` (+ foreground mobjects) into native draw calls (`ClearShapes` first).
- `notes`: `render_at` calls `evaluate` → `sync` → `tick` in that order. A custom camera overriding `capture_mobjects`/`get_frame` falls back to per-frame full-screen rasterization (`_rasterise_custom_camera`).

### `MLWindow.hwnd` (property)

```python
@property
def hwnd(self)
```

- `ret`: `int \| None` — this window's Win32 handle (looked up by class+title, cached); `None` off Windows or before init.
- `notes`: used by `recording.py` and `FramePreview`.

### `MLWindow.build_timeline`

```python
def build_timeline(self)
```

- `ret`: a `Timeline` built from the recorded `_sched` schedule (`Timeline(self, self.scene)` → `add` each entry → `finalize()`).
- `notes`: schedule mode only (`MLWindow._schedule_mode = True`, e.g. set by `FrameServer`). `play()` records instead of drawing; `build_timeline()` then makes any frame producible on demand.

## `fast_record_scene`

```python
def fast_record_scene(scene, out_path=None, *, fps=60, hidden=True, count_only=False, segment=None, overwrite=True, cleanup=True, verbose=True, jobs=None) -> Dict[str, Any]
```

- `ret`: `dict` `{out_path, windows, files, with_audio}` — `out_path` destination; `windows` path handed to each recorder; `files` files present on disk; `with_audio` whether an audio track was muxed.
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `scene` | `type \| Scene \| Callable[[], None]` | — | Scene subclass, instance, or no-arg callable |
| `out_path` | `str \| None` | `None` → `~/Downloads/output.mp4` | mp4 (pipe mode) or directory (`segment` mode); multi-window scenes get `_partN` |
| `fps` | `int` | `60` | output rate; only `60` (forced, prints `[rtm] forcing 60 fps`) |
| `hidden` | `bool` | `True` | window hidden, never shown (offline); `False` watches while recording |
| `count_only` | `bool` | `False` | probe: count frames only, no capture/GPU render |
| `segment` | `tuple \| None` | `None` | `(start_frame, end_frame)` → BMP directory instead of mp4 |
| `overwrite` | `bool` | `True` | `False` refuses to overwrite an existing target (n/a for `count_only`) |
| `cleanup` | `bool` | `True` | delete transient manim `media/` after recording |
| `verbose` | `bool` | `True` | print per-window progress lines |
| `jobs` | `int \| "auto" \| None` | `None` | worker processes for frame-parallel recording |

- `notes`:
  - Offline, fastest route: Vulkan framebuffer readback → ffmpeg; maps to `enable_fast_record` / `_finish_fast_record`.
  - `jobs=None` — single pass, no probe (default).
  - `jobs="auto"` — probe once, split only if a win: importable single-window Scene with ≥ `_AUTO_MIN_FRAMES = 240` frames (4 s @60fps), split across `min(4, cpus-1)`.
  - `jobs=N` — that many workers; still probes frame count / window count and falls back to single pass otherwise.
  - Splitting requires a `Scene` **class** importable in another process; instances, lambdas, function-local classes, or a script without `if __name__ == "__main__":` fall back to one pass. Multi-window, `count_only`, `segment`, `hidden=False` never parallelise.
  - Parallel workers use the `Timeline.render_at` path and do **not** run per-animation finish hooks (`finish()` / `clean_up_from_scene()`); scenes relying on those need `jobs=None`.
- `errs`:
  - `FileExistsError: "target already exists: {out_path} (pass overwrite=True to replace it)"` — `overwrite=False` and target exists.
  - `RuntimeError: "recorded {n} window(s) but MLWindow.close() was only called {m} time(s): the encoder was never finished, so the output is incomplete. Call win.close() at the end of construct()."`
  - `RuntimeError: "recorded file looks empty/incomplete ({n} bytes): {f} -- did the scene forget `win.scene = self`, or forget win.close()?"` — file < 1024 bytes.
  - `TypeError: "scene looks like a class but has no construct(); ..."` / `"scene must be a Scene subclass, a Scene instance, or a no-arg callable."`
- `eg`:
  ```python
  fast_record_scene(MyScene)                        # ~/Downloads/output.mp4
  fast_record_scene(MyScene, "preview.mp4", fps=60, hidden=False)
  fast_record_scene(MyScene, jobs=4)
  ```
- `see`: ../zh_CN/00-快速开始/04-录制视频.md

## `record_scene`

```python
def record_scene(scene, out_path=None, *, fps=60, overwrite=True, cleanup=True, verbose=True) -> Dict[str, Any]
```

- `ret`: `dict` `{out_path, windows, files, with_audio}` (same shape as `fast_record_scene`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `scene` | `type \| Scene \| Callable[[], None]` | — | Scene subclass, instance, or no-arg callable |
| `out_path` | `str \| None` | `None` → `~/Downloads/output.mp4` | target mp4; multi-window appends `_partN` |
| `fps` | `int` | `60` (forced) | background-thread capture rate; only `60` (prints `[rtm] forcing 60 fps`) |
| `overwrite` | `bool` | `True` | `False` refuses to overwrite existing `out_path` |
| `cleanup` | `bool` | `True` | delete transient manim `media/` after recording |
| `verbose` | `bool` | `True` | print per-window progress lines |

- `notes`: real-time capture against a **visible** window; maps to `start_record` / `stop_record`. The user sees the animation as it is captured.
- `errs`: same as `fast_record_scene` (overwrite / unfinished-window / empty-file / scene-type).
- `see`: ../zh_CN/00-快速开始/04-录制视频.md

## `FrameServer`

```python
class FrameServer
def __init__(self, scene_cls, width=1920, height=1080, max_workers=4, max_pending=32, hidden=True)
```

- `ret`: a prepared scene whose every frame can be produced on demand (one `construct()` pass, then O(1) per frame).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `scene_cls` | `type` | — | Scene class to prepare (schedule mode, no draw) |
| `width` | `int` | `1920` | window width (forced to 1920) |
| `height` | `int` | `1080` | window height (forced to 1080) |
| `max_workers` | `int` | `4` | PNG-encode / write thread-pool size |
| `max_pending` | `int` | `32` | max queued async writes (backpressure) |
| `hidden` | `bool` | `True` | build the window hidden; only `show_frame` reveals it |

- attributes: `scene`, `window`, `timeline`, `duration` (seconds).
- `notes`: builds the scene with `MLWindow._schedule_mode = True` (play records, never draws) and `_hidden_default = hidden`; after building calls `build_timeline()` and sets `timeline.finish_hooks = True`.
- `errs`:
  - `RuntimeError: "scene did not create an MLWindow"` — `construct()` opened no window.

### `FrameServer` methods

| Signature | `ret` / behavior |
| --- | --- |
| `render_frame(self, t, readback=False)` | none; draw frame at `t` (~10 ms, O(1)). `readback=True` copies before present |
| `show_frame(self, t)` | none; `set_visible(True)` then `render_frame(t)` |
| `grab(self, t)` | `(bytes, w, h, row_bytes)`; render with readback + read pixels |
| `save_frame(self, t, path, quality=6)` | `path`; render → read → PNG (synchronous) |
| `save_frame_async(self, t, path, quality=6)` | `Future`; render on main thread, encode/write on pool |
| `export_frames(self, out_dir, times, async_=True)` | `list[str]`; writes `f_{i:05d}_t{t:.3f}.png` |
| `frame_times(self, fps=60)` | `list[float]`; evaluation time of every frame (from `Timeline.frame_times`) |
| `flush(self)` | none; join pending writes |
| `close(self)` | none; flush, shut pool, close window |

- properties: `readback_format` → `"bgra"` or `"bgr24"`; `frame_size` → `(w, h)`.
- `eg`:
  ```python
  from real_time_manim import FrameServer
  fs = FrameServer(DemoCreate)      # runs construct() once, no draw
  fs.show_frame(2.05)               # ~10 ms
  fs.save_frame(2.05, "f205.png")
  fs.close()
  ```
- CLI: `python -m real_time_manim.frames 1 0 1.5 3.0 --out frames/` (`--out DIR`, `--sync`).
- `see`: ../zh_CN/00-快速开始/05-任意帧预览.md

## `FramePreview`

```python
class FramePreview
def __init__(self, scene_cls, fps=60, out_dir="frames", use_bar=True, width=None, height=None, verbose=True, controls="input", position=None)
```

- `ret`: a still window + input bar; nothing plays on open; each seek is one O(1) draw.
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `scene_cls` | `type \| Scene \| Callable` | — | scene to preview (same forms as `fast_record_scene`) |
| `fps` | `int` | `60` | frame-number rate (`120` = frame 120 = `t = 120/fps`) |
| `out_dir` | `str` | `"frames"` | directory `s` / `Save PNG` writes into |
| `use_bar` | `bool` | `True` | `False` → terminal input (no GUI toolkit); auto-`False` where no native bar exists (Windows/macOS have one) |
| `width` / `height` | `int \| None` | `None` | window size (forced to 1920×1080) |
| `verbose` | `bool` | `True` | print prepare time and status lines |
| `controls` | `str` | `"input"` | `"input"` (text field) or `"slider"` (scrubber); aliases `box`/`text`/`edit`, `bar`/`progress`/`progressbar`/`scrub` |
| `position` | `tuple \| None` | `None` | video-window top-left `(x, y)`; `"100,80"` accepted |

- methods: `run(self, start_frame=0)` → `0`; `close(self)`; `time_of(self, frame)`; `frame_of(self, t)`; property `last_frame`.
- attributes: `server` (`FrameServer`), `window`, `duration`, `n_frames`, `current`, `saved`, `prepare_seconds`, `fps`, `out_dir`, `controls`, `position`.
- `notes`:
  - Input syntax: `120`/`120f` frame, `1.5`/`1.5s` seconds, `+10`/`-1` step N frames, `s` save PNG, `p` play from here, `?` help, `q` quit. Out-of-range clamps; bad input prints e.g. `[rtm] cannot read '{x}' -- try 120, 2.5s, +1, s, q`.
  - Title bar shows `frame {i}/{last}   t={t:.3f}s`.
  - Bar: `Win32Bar` (Windows) and `MacBar` (macOS) are native bar windows docked under the video. Both use the same widgets (`input`: text + Jump/Save PNG/Quit; `slider`: scrubber + Save PNG/Quit).
  - macOS AppKit runs only on the main thread, so the native bar queues events and `FramePreview._pump_bar()` drains them into `_queue`; `_dispatch` remains the sole timeline owner. `FramePreview.run()` tells the platform layer to reserve room before revealing the hidden window (`Vulkan_SetPreviewBarReserve`), so the docked bar stays clear of an auto-hiding Dock. `MacBar` falls back to terminal input if the dylib lacks the preview-bar exports.
  - A seek replays **animation** state; custom-updater / `TracedPath`-only objects are exact forward, approximate backwards.
- `errs`:
  - `ValueError: "controls must be 'input' or 'slider', got {value!r}"`.
  - `ValueError: "position must be two numbers, got {value!r}"` / `"position must look like '100,200', got {value!r}"`.
- CLI: `python -m real_time_manim.preview {demo|module:Class} [--at N] [--fps N] [--out DIR] [--controls {input,slider}] [--pos X,Y] [--no-bar] [--quiet]`.
- `eg`:
  ```python
  from real_time_manim import FramePreview
  FramePreview(DemoCreate).run()
  FramePreview(DemoCreate, controls="slider").run()
  FramePreview(DemoCreate, use_bar=False).run()
  ```
- `see`: ../zh_CN/00-快速开始/05-任意帧预览.md

## `Timeline`

```python
class Timeline
def __init__(self, window, scene, strict=False)
```

- `ret`: a schedule of animations on one time axis that can render any frame instantly.
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `window` | `MLWindow` | — | window used to `sync`/`tick` each frame |
| `scene` | `Scene` | — | the scene owning the mobjects |
| `strict` | `bool` | `False` | if `True`, scheduling a stateful animation raises `ValueError` |

- attributes: `duration` (set in `finalize()`), `finish_hooks` (bool; forward walks set `True` to run `finish()` hooks), `strict`.

### `Timeline` methods

| Signature | `ret` / behavior |
| --- | --- |
| `add(self, anim, start=0.0)` | `self`; schedule `anim` at global time `start` (s) |
| `finalize(self)` | `self`; captures each animation's start state (`begin()` once); sets `duration`, frozen windows |
| `prepare(self, *animations)` | `self`; `add` all at `t=0` then `finalize()` |
| `evaluate(self, t, dt=0.0, drive=True)` | none; set mobjects to their state at `t` (no draw) |
| `render_at(self, t, readback=False, frame_dt=None)` | `bool`; evaluate + draw + present. `False` if the window is gone |
| `screenshot_at(self, t, path)` | `render_at(t, readback=True)` then `window.screenshot(path)` |
| `render_mp4(self, path, fps=60, duration=None, realtime=False)` | `path`; walk the schedule forward and encode with ffmpeg |
| `frame_times(self, fps=60)` | `list[float]`; per-play local grids (matches what `play()` writes) |
| `stateful_names(self)` | `list[str]`; class names of scheduled stateful animations |
| `finish_all(self)` | none; apply every entry's `finish()` once |
| `stop_conditions(self, t=None)` | `list`; scheduled `Wait.stop_condition` callables |
| `poll_stop_conditions(self, t)` | `bool`; `True` = end the wait now |

- `notes`:
  - Pure function of `t`; `render_at` is O(1) in `t`. Entries sharing a `start` are one play.
  - `STATEFUL_ANIMATIONS` (not time-pure): `Rotate`, `Rotating`, `Rotation`, `AnimationGroup`, `Succession`, `LaggedStart`, `LaggedStartMap`, `SpiralIn`, `Blink`, `FadeTransform`, `FadeTransformPieces`, `TransformMatchingAbstractBase`, `TransformMatchingShapes`, `TransformMatchingTex`, `SpeedModifier`, `ChangeSpeed`, plus any animation with `updaters`.
  - `render_at` order: `evaluate` → `sync` → `tick`; a frozen wait holds the picture (no updater pass). `render_mp4` polls stop conditions once per drawn frame.
- `errs`:
  - `RuntimeError: "cannot add to a finalized Timeline"` — `add` after `finalize`.
  - `RuntimeError: "Timeline already finalized"` — `finalize` twice.
  - `ValueError: "{Type} is stateful and cannot be evaluated as a pure function of time yet"` — stateful animation with `strict=True`.
  - `RuntimeError: "call finalize()/prepare() first"` — `evaluate` before `finalize`.
- `eg`:
  ```python
  tl = Timeline(window, scene)
  tl.add(FadeIn(sq), start=0.0)
  tl.add(Transform(sq, circle), start=1.0)
  tl.finalize()
  tl.render_at(1.5)          # instant — no replay
  ```
- `see`: ../zh_CN/00-快速开始/05-任意帧预览.md

## Subcaption / SRT helpers

Module `real_time_manim.window.play`.

```python
def record_subcaption(window, content, start, duration)
def collect_subcaptions(windows=None)
def clear_subcaptions(windows=None)
def compose_srt(entries)
def export_srt(path, entries=None, windows=None, verbose=False)
```

| Symbol | `ret` / behavior |
| --- | --- |
| `record_subcaption` | stored `{"content", "start", "duration"}` dict; `duration` clamped ≥ 0; mirrored onto `window` |
| `collect_subcaptions` | `list[dict]` sorted by `(start, duration)`; `windows=None` → the run's flat store |
| `clear_subcaptions` | none; `windows=None` clears the flat store + every registered window's mirror |
| `compose_srt` | `str` SRT text (uses manim's `srt` lib when importable, else a hand-rolled formatter) |
| `export_srt` | `str` path written, or `None` when there is nothing to write (no file created) |

- `notes`:
  - `win.play(..., subcaption=...)` records cues in memory; a recording run writes a `.srt` next to the mp4 automatically (`record._run` → `audio_track.apply_sounds(files)` → `export_srt`). `export_srt(verbose=True)` prints `[srt] wrote {n} subcaption(s) -> {path}`.
  - The cue clock is the window's recorded-timeline `_cursor`, not manim's `Scene.time` (which never advances under RTM).
  - `next_section` per-section video splitting is not automatic: `.srt`/segments need manual ffmpeg cuts.
- `see`: ../zh_CN/00-快速开始/04-录制视频.md · ../zh_CN/01-场景与相机/场景/04-分段字幕与声音.md

## Compile-wait popup (first formula render)

`MathTex` / `Tex` / `Typst` / `MathTypst` compile **synchronously in `__init__`** (LaTeX ~1–2 s cold, Typst ~0.4 s). On a live scene the `MLWindow` already exists, so the pause happens with an empty window on screen. RTM shows a small always-on-top popup so it does not look like a freeze.

- `shows`: only when a **visible** `MLWindow` is registered (`MLWindow._registry`, `hidden` False) **and** the compile exceeds `RTM_WAIT_POPUP_DELAY` (default `0.35` s). A cache hit (~30 ms) never triggers it.
- `silent`: hidden/offline runs — `fast_record_scene` and `FrameServer` build hidden windows.
- `content`: live `已等待 N.Ns` counter + marquee progress bar. Language follows the **Windows display language (user UI language)** — `zh`/`en`/`ja`/`ko`, else English.
- `effect on output`: **none** — it only observes elapsed time; the compile and the recorded video are unchanged. No-op off Windows.
- `avoid / clear the wait`: warm the cache with `restore_tex_cache` (see *LaTeX / Typst cache* below), or force a recompile with `clear_tex_cache`.

| env | default | effect |
| --- | --- | --- |
| `RTM_WAIT_POPUP` | `1` | `0` disables the popup |
| `RTM_WAIT_POPUP_DELAY` | `0.35` | seconds before it appears |
| `RTM_LANG` | auto | force `zh` / `en` / `ja` / `ko` |
| `RTM_WAIT_ICON` | bundled `wait.ico` | override the popup icon (`.ico` path) |

- `see`: ../zh_CN/00-快速开始/03-实时窗口-MLWindow.md

## LaTeX / Typst cache

> src: `real_time_manim/util.py`. RTM compiles every `MathTex`/`Tex`/`Typst` to an SVG under `<media>/Tex`; a cold compile is what makes the first formula render pause. These four helpers warm, stash, or clear that folder, and all are exported top-level.

### `restore_tex_cache`
```python
def restore_tex_cache(cache_dir, media_dir=None, *, tex_subdir="Tex",
                      only_ext=(".svg",), overwrite=False,
                      dry_run=False, verbose=True) -> int
```
- `ret`: number of files copied into `<media>/<tex_subdir>`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `cache_dir` | `str` | required | folder of previously saved SVGs (eg `tex_cache`) |
| `media_dir` | `str \| None` | `None` | media root; `None` → `<cwd>/media` |
| `tex_subdir` | `str` | `"Tex"` | sub-folder manim compiles into |
| `only_ext` | `Iterable[str]` | `(".svg",)` | extensions to copy; `()` copies every file |
| `overwrite` | `bool` | `False` | also replace files already present |
| `dry_run` | `bool` | `False` | report only, copy nothing |
| `verbose` | `bool` | `True` | print a line per file |

- `notes`: call **before** a run to skip recompiling unchanged math; the demo runner does this.
- `see`: ../zh_CN/00-快速开始/03-实时窗口-MLWindow.md

### `save_tex_cache`
```python
def save_tex_cache(cache_dir, media_dir=None, *, tex_subdir="Tex",
                   only_ext=(".svg",), overwrite=False,
                   dry_run=False, verbose=True) -> int
```
- `ret`: number of files copied into `cache_dir`.
- `args`: mirror `restore_tex_cache` (source and destination swapped).
- `notes`: call **after** a run to stash newly compiled SVGs for the next one.
- `see`: ../zh_CN/00-快速开始/03-实时窗口-MLWindow.md

### `clear_tex_cache`
```python
def clear_tex_cache(cache_dir="tex_cache", media_dir=None, *,
                    tex_subdir="Tex", only_ext=(),
                    dry_run=False, verbose=True) -> int
```
- `ret`: number of files removed (or that `dry_run` would remove).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `cache_dir` | `str \| None` | `"tex_cache"` | persistent cache to empty; `None` clears only `<media>/Tex` |
| `media_dir` | `str \| None` | `None` | media root; `None` → `<cwd>/media` |
| `tex_subdir` | `str` | `"Tex"` | sub-folder manim compiles into |
| `only_ext` | `Iterable[str]` | `()` | extensions to remove; `()` removes every file |
| `dry_run` | `bool` | `False` | report only, delete nothing |
| `verbose` | `bool` | `True` | print a line per folder plus the total |

- `notes`:
  - Clears **both** `<media>/<tex_subdir>` and `cache_dir` (each is a dedicated cache, hence `only_ext=()` by default). `only_ext=(".svg",)` keeps the `.tex`/`.dvi`/`.log` intermediates.
  - Empties a folder and then removes it; idempotent — returns `0` when nothing exists.
  - Inverse of `restore_tex_cache` / `save_tex_cache`; the repo's `clear_cache.py` is a thin wrapper over it.
- `see`: ../zh_CN/00-快速开始/03-实时窗口-MLWindow.md
- `eg`:
```python
clear_tex_cache()                    # <media>/Tex + tex_cache/
clear_tex_cache(dry_run=True)        # preview only
clear_tex_cache(only_ext=(".svg",))  # keep .tex/.dvi intermediates
clear_tex_cache(cache_dir=None)      # only <media>/Tex
```

### `clear_media`
```python
def clear_media(media_dir=None, *, verbose=True) -> bool
```
- `ret`: `True` if the folder existed and was removed, else `False`.
- `notes`:
  - Removes the **whole** `media/` folder, not just `Tex`; unconditional (never skipped).
  - Does **not** follow `config.media_dir` — it always targets `<cwd>/media` unless `media_dir` is given.
  - `record.py` calls it after a run when `cleanup=True`.
- `see`: ../zh_CN/00-快速开始/04-录制视频.md

## Hard constraints

| Constraint | Value | Notes |
| --- | --- | --- |
| Output resolution | **fixed 1920×1080** | other sizes forced; prints `[rtm] forcing 1920x1080: ...` (`SUPPORTED_WIDTH`/`SUPPORTED_HEIGHT`) |
| Frame rate | **fixed 60 fps** | `SUPPORTED_FPS = 60`; other values print `[rtm] forcing 60 fps: ...` |
| Window | each Scene creates its own `MLWindow` | no global window; `win.scene = self` is a required binding |
| Teardown | must call `win.close()` | without it nothing is flushed and the run may not exit |
| One window per process | native DLL limit | Python side serialises via `_registry` |
| `import manim` | works, but do not import it first | import `real_time_manim` first to keep class identity (else `RuntimeWarning`) |
| Runtime deps | Vulkan GPU+driver | recording also needs `ffmpeg` on `PATH` |

## Entry points

| Symbol | import |
| --- | --- |
| `MLWindow` | `from real_time_manim import MLWindow` or `from real_time_manim.vulkan_bind import MLWindow` |
| `fast_record_scene` / `record_scene` | `from real_time_manim.record import ...` (also lazily top-level) |
| `FrameServer` | `from real_time_manim.frames import FrameServer` (also lazily top-level) |
| `FramePreview` | `from real_time_manim.preview import FramePreview` (also lazily top-level) |
| `Timeline` | `from real_time_manim.timeline import Timeline` (also lazily top-level) |
| Common shapes/anims/utils | `from real_time_manim.vulkan_bind import ...` |
| Everything else (ManimCE namespace) | `from real_time_manim import ...` |
