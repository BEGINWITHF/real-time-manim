# Recording Video

RTM provides two recorders: `fast_record_scene` records offline at full speed (no window by default), and `record_scene` records against a visible live window. Both wrap the start and end of the scene, and both clean up the temporary `media/` automatically once recording finishes.

Prerequisite: `ffmpeg` must be on `PATH`.

Subtitles and sections: after `win.play(subcaption=...)` records, a `.srt` is **produced automatically** next to the mp4 (collected in memory and then written to disk; the export function is `real_time_manim.window.play.export_srt`). The other half of command-line artifacts such as `.srt` and sections — the `next_section` section videos — genuinely requires cutting with ffmpeg by hand; see [Subcaptions and Sound](../01-Scenes-and-Cameras/Scenes/04-Subcaptions-and-Sound.md).

## Parameters

### `record_scene` (live, visible window)

```python
def record_scene(scene, out_path=None, *, fps=60, overwrite=True, cleanup=True, verbose=True) -> Dict[str, Any]:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `scene` | `type \| instance \| Callable[[], None]` | — | a `Scene` subclass, a `Scene` instance, or a zero-argument callable |
| `out_path` | `str \| None` | `None` → `~/Downloads/output.mp4` | target `.mp4`; when a scene opens several windows, `_partN` is appended automatically |
| `fps` | `int` | `60` (forced) | frame rate of the live capture; every frame the play loop draws is captured exactly once |
| `overwrite` | `bool` | `True` | when `False`, an existing `out_path` is not overwritten |
| `cleanup` | `bool` | `True` (recommended) | delete the temporary manim `media/` directory after recording; `False` keeps it |
| `verbose` | `bool` | `True` | print a progress line for each window |

> Note: the recording frame rate **only supports `60`** (`SUPPORTED_FPS`)

`record_scene` is frame-exact: a `win.play(..., run_time=1.0)` at 60 fps contributes exactly 60 frames, so the MP4 is the same length as the scene schedule (the offline recorder produces the same frames). The capture runs on the render thread, one readback per drawn frame; the encoder write runs on a small writer thread so the visible animation stays real-time. On macOS the recording window's drawable is pinned to 1920×1080 while recording (a screen-clamped Retina window would otherwise capture 3420×1924 and need a per-frame downscale), then restored to the display's backing scale when `stop_record` runs.

### `fast_record_scene` (offline, no window by default)

```python
def fast_record_scene(scene, out_path=None, *, fps=60, hidden=True, count_only=False, segment=None, overwrite=True, cleanup=True, verbose=True, jobs=None) -> Dict[str, Any]:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `scene` | `type \| instance \| Callable[[], None]` | — | a `Scene` subclass, a `Scene` instance, or a zero-argument callable |
| `out_path` | `str \| None` | `None` → `~/Downloads/output.mp4` | target `.mp4` (pipe mode); in `segment` mode it is a directory |
| `fps` | `int` | `60` | output frame rate; **must be 60** (`enable_fast_record` force-corrects it and prints `[rtm] forcing 60 fps`, `window/recording.py:142-145`) |
| `hidden` | `bool` | `True` | the window is hidden and never pops up, so offline capture does not disturb the desktop; `False` lets you watch while recording |
| `count_only` | `bool` | `False` | probe mode: only counts frames, neither captures nor does GPU rendering |
| `segment` | `tuple \| None` | `None` | `(start_frame, end_frame)`; export the frame range as a BMP directory instead of an MP4 |
| `overwrite` | `bool` | `True` | when `False`, an existing target is not overwritten (not applicable with `count_only`) |
| `cleanup` | `bool` | `True` | delete the temporary manim `media/` directory after recording |
| `verbose` | `bool` | `True` | print a progress line for each window |
| `jobs` | `int \| "auto" \| None` | `None` (single process) | how many worker processes to use for parallel frame rendering; `"auto"` probes first and then decides, `1` forces a single process |

#### `jobs`: multi-process parallel frame rendering (speeds up long scenes)

In a time-addressable scene **every frame is independent of the others**, so a frame range can be split across several processes and rendered at the same time:
worker i renders its own contiguous block of frames into its own mp4 (the encoding parameters are **exactly the same** as single-process),
and finally `ffmpeg -f concat -c copy` joins them losslessly. The per-frame cost falls as the number of workers grows.

* Default `jobs=None`: **single-process recording with no probing at all** (probing must first open a window + Vulkan device
  before it can count the total number of frames, about 1.4 seconds, which is not worth it for short clips).
* `jobs="auto"`: probe once and only split frames when it pays off — the scene is ≥ **240 frames** (4 seconds at 60fps),
  can be imported by a child process, and opens only one window, then split into `min(4, CPU cores-1)` parts.
* `jobs=4`: ask for 4 workers directly (it still probes once for the total frame count and window count, and falls back to single-process if the conditions are not met).
* It needs a **`Scene` class** that another process can import: instances, lambdas and classes defined inside a function all fall back to single-process.
  A script run directly as `python my_script.py` must have an `if __name__ == "__main__":` guard,
  otherwise a worker re-executes it on import (that case also falls back to single-process automatically).
* Multi-window scenes, `count_only`, `segment` mode and `hidden=False` are never parallelised.
* Each worker uses its own `media/` directory (manim's `Text`/`Tex` SVG cache is not concurrency-safe).
* `print()` inside the `scene` appears only once (the parent process's own), and workers' stdout is swallowed.
* Parallel frame recording goes through the timeline (`Timeline.render_at`) path and **does not run each animation's finish hooks**
  (`finish()` / `clean_up_from_scene()`, which is for example where `FadeTransform`'s ghost copy gets cleaned up) —
  use the default `jobs=None` for scenes that depend on finish-up logic.

> Measured (1920×1080@60, 16 cores): a 15-second scene takes **4.6–6.6 s (5.1–7.3 ms/frame)** in a single process (alternating within the same session for comparison, ManimCE Cairo takes 12.8–13.9 s / 14.2–15.4 ms/frame, i.e. 1.9–2.8× faster).
>
> The four most important cuts:
>
> - during recording, the window switched to `IMMEDIATE` presentation (previously every frame spent 6.9 ms waiting for vblank);
> - per-point coordinate conversion (2000+ per frame) became one projector built per object;
> - the affine case is computed in a single numpy pass over the whole stretch;
> - bounding boxes / centres are computed straight from point sets (no longer through manim's per-point linked-list `get_center/get_bottom`).
>
> Text-heavy scenes' sync dropped all the way from 11.2 ms to 2.5 ms (−78%). `jobs=4` reaches 1.4–2× when the machine has headroom, but loses to a single process when the same iGPU is shared (measured), so it is off by default and `auto` only turns it on at ≥240 frames. Parallel frame recording goes through the timeline path and does not run the finish hooks.

> **Returns**: both return a dict `{out_path, windows, files, with_audio}` — `out_path` is the output path, `windows` the paths handed to each recorder, `files` the files actually written to disk, and `with_audio` whether there is an audio track (`record.py:225-230`).

## Example

```python
from real_time_manim import Scene, Square, BLUE
from real_time_manim.vulkan_bind import MLWindow, Create, Wait
from real_time_manim.record import fast_record_scene, record_scene

class MyScene(Scene):
    def construct(self):
        win = MLWindow(1280, 720)
        win.scene = self
        sq = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)
        win.play(Create(sq), run_time=1.0)   # equivalent to self.play(Create(sq), run_time=1.0) in ManimCE
        win.play(Wait(0.5))
        win.close()

fast_record_scene(MyScene)                       # ~/Downloads/output.mp4
fast_record_scene(MyScene, "preview.mp4")        # current directory (a full path also works)
fast_record_scene(MyScene, fps=60, hidden=False) # also show the window while recording
fast_record_scene(MyScene, jobs=4)               # 4 processes rendering frames in parallel (faster for long scenes)
record_scene(MyScene, "live.mp4", fps=60)         # record against the visible live window (fps only supports 60: passing 30 prints "[rtm] forcing 60 fps" and still renders at 60)
```

## Video tutorial
TODO: Tagin records the tutorial video himself

See also: [Live Window MLWindow](03-Live-Window-MLWindow.md) · [First Scene](02-First-Scene.md)
