# Live Window MLWindow

`MLWindow(w, h)` opens a live Vulkan rendering window; after binding a scene, drive the whole animation with `win.play(...)`, and finish with `win.close()`.

Limit: only one window is supported per process at a time (the limit comes from the native DLL; on the Python side `_registry` opens and closes them in order)

## Parameters

### `MLWindow.__init__`

```python
def __init__(self, w=1920, h=1080, hidden=None):
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `w` | `int` | `1920` (forced) | window width in pixels; anything other than 1920×1080 is force-corrected (see below) |
| `h` | `int` | `1080` (forced) | window height in pixels; same as above |
| `hidden` | `bool \| None` | `None` (from the class-level `_hidden_default`) | when `True`, the window is never shown after being created (for offline recording) |

> **Enforced specs**:
>
> - `MLWindow` currently **only supports `1920×1080`** (the class attributes `SUPPORTED_WIDTH` / `SUPPORTED_HEIGHT`).
> - The recording frame rate **only supports `60`** (`SUPPORTED_FPS`).
> - Passing other values does not raise an error; instead they are **force-corrected** and a `[rtm] forcing 1920x1080: ...` line is printed. So `MLWindow(960, 540)` above and `MLWindow()` both actually render at 1080p.
>
> **Any size other than 1920×1080 is forced to 1080p60 and prints `[rtm] forcing`; this is normal**. *Other sizes may be supported in the future.*

### `win.scene` (property)

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `scene` | `Scene` | `None` | the bound Manim scene; `win.scene = self` must be assigned first, otherwise `play()` returns immediately |

### `MLWindow.play`

```python
def play(self, *animations, **kwargs):
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*animations` | `Animation \| Mobject \| _AnimationBuilder` | — | the animation(s) to play (can be several); `.animate...` builders are resolved automatically |
| `**kwargs` | `Any` | — | **what takes effect is `run_time` / `rate_func`** (each overriding one animation's duration / rate curve) **plus `path_arc` / `path_arc_axis` / `path_arc_centers` / `path_func`** (since 2026-10-17 these are forwarded to the animation instance, and the `Transform.path_arc` setter rebuilds `path_func`); `subcaption` / `subcaption_duration` / `subcaption_offset` have dedicated formal parameters; **any other keyword prints a named warning** (`[RTM] play(): unsupported keyword(s) ... ignored`) instead of staying silent (`window/play.py`, `window/play.py::SUPPORTED_PLAY_KWARGS`) |

### `MLWindow.close`

```python
def close(self):
```

No parameters. Closes the window and ends rendering (`_unregister()` + `Vulkan_Shutdown()`).

**The encoding finish-up for recording is not inside `MLWindow.close`**: it is done by the `record._AutoRecord` installed by `fast_record_scene` / `record_scene`, which runs `_finish_fast_record()` / `stop_record()` before calling `close()` (`record.py:181-186`, `window/recording.py:217-221`). Calling `enable_fast_record(...)` + `win.close()` by hand does not finish up; you must call the internal `win._finish_fast_record()` (internal API, not needed in normal scenes).

### `MLWindow.set_mesh` / `MLWindow.clear_mesh`

```python
def set_mesh(self, mesh): ...
def clear_mesh(self): ...
```

`set_mesh(mesh)` hands a `MeshBatch` to the window. It is submitted before the painter primitives every frame, so the GPU depth buffer resolves 3D self-occlusion. `set_mesh(None)` or `clear_mesh()` detaches it.

```python
mesh = MeshBatch()
mesh.append(quads, colors)     # (Q, 4, 3) world coords + (Q, 4, 4) RGBA
win.set_mesh(mesh)
```

See [Surfaces · depth mesh](../06-Three-Dimensional/02-Surfaces.md) for the quad format, limits and a full example.

### Waiting hint for the first formula compile

Rendering a LaTeX / Typst formula for the first time invokes the compiler and may stall for a second or two. If a **visible** window already exists at that point, RTM pops up a small always-on-top window that clearly tells you it is waiting for the compile and not stuck:

- **Only appears when there is a visible window**: `fast_record_scene` / `FrameServer` use hidden windows, so it does not pop up;
- **Only appears when the compile is slow**: with a cache the compile finishes in about 30ms, so the popup is cancelled before it can appear;
- it carries a live "waited N.Ns" counter and a marquee progress bar, so you can tell at a glance that it is not dead;
- the text follows the **Windows display language (user UI language)**: Chinese / English / Japanese / Korean, with other languages falling back to English.

| Environment variable | Default | Effect |
| --- | --- | --- |
| `RTM_WAIT_POPUP` | `1` | set to `0` to turn the popup off entirely |
| `RTM_WAIT_POPUP_DELAY` | `0.35` | how many seconds the compile must exceed before it pops up |
| `RTM_LANG` | auto | force the popup language: `zh` / `en` / `ja` / `ko` |
| `RTM_WAIT_ICON` | built-in hourglass icon | replace the popup icon (pass a path to a `.ico`) |

> Reminder: the popup is only informational and **does not affect the compile result** (`fast_record_scene`'s output is byte-for-byte identical whether or not the popup appears). To avoid the wait entirely, warm the cache first (`save_tex_cache` / `restore_tex_cache`, which is exactly what the repo's `run.py` does), or do one throwaway run first; to go the other way and force a recompile / free space, use `clear_tex_cache()` — it clears both `<media>/Tex` and the persistent `tex_cache/` cache and returns the number of files deleted (`dry_run=True` only previews, `only_ext=(".svg",)` only clears SVGs).

## Example

The minimal RTM program template:

```python
from real_time_manim import Scene, Square, BLUE
from real_time_manim.vulkan_bind import MLWindow, Create, Wait

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        sq = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)   # create a "Square" Mobject named "sq"
        win.play(Create(sq), run_time=1.0)   # apply the "Creat" animation to "sq"; the animation completes in 1s
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window
```

## Sample video (RTM render result)
TODO: just reuse the output of the first scene

## Low-level methods (advanced)

These methods are for recording, preview and custom frame loops. A normal scene only needs `win.play(...)` + `win.close()`.

| Method | Meaning |
| --- | --- |
| `win.screenshot(path)` | save the current frame to an image; `path` is `str` or `bytes`; works on a hidden window; returns the native result (non-zero = written) |
| `win.request_readback()` | arm the next frame for readback; must be called before the `tick()` that draws it |
| `win.tick()` | advance one frame; returns `False` when the window is closed; updates `win_w` / `win_h` |
| `win.set_visible(visible=True)` | show or hide the window |
| `win.hwnd` | read-only property; Win32 window handle, `None` off Windows or before init |
| `win.start_record(path="output.mp4", fps=60)` | start live recording (background encoding thread) |
| `win.stop_record()` | finish live recording |
| `win.build_timeline()` | build a `Timeline` from the animations recorded in schedule mode |
| `win.sync(scene, angle=0.0)` | sync `scene` into the window each frame; used by the play/record loops, rarely called by hand |

> Note: `start_record` / `stop_record` are live recording; `enable_fast_record` + the internal `_finish_fast_record` are the offline fast path. Do not mix either with `fast_record_scene`'s automatic finish-up.

See also: [First Scene](02-First-Scene.md) · [Recording Video](04-Recording-Video.md) · [Scene Basics](../01-Scenes-and-Cameras/Scenes/01-Scene-Basics.md)
