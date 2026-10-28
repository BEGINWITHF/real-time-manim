# scene & camera

> scope: Scene lifecycle, add/remove/replace/z-order, play/wait/pause, sections & audio (add_sound, next_section, subcaption/SRT), dedicated scenes (MovingCameraScene, ThreeDScene/SpecialThreeDScene, ZoomedScene, VectorScene, LinearTransformationScene), cameras (Camera, MovingCamera, ThreeDCamera) + viewport/raster fallback, config (background, frame geometry, paths/window, RTM-vs-CE).
> src: `real_time_manim/window/{scene,play,core,paint_order,recording}.py`, `real_time_manim/{record,compat,audio_track}.py`, bundled `real_time_manim/manim/`; human wiki `../zh_CN/01-场景与相机/`.

## 0. RTM deviations from ManimCE (grep first)

| Topic | ManimCE | RTM |
| --- | --- | --- |
| Driving playback | `Scene.play` → `Scene.render()` → file writer | `win.play(...)`; `record.py::scene_lifecycle` calls `setup()` → `construct()` → `tear_down()` itself. **`Scene.render` is never called.** |
| `self.play` | renders via `self.renderer` | `compat.py` shims `Scene.play` to forward to the bound `MLWindow` when one exists (`_shim_scene_play_uses_window`). `self.play = win.play` still works and is what the wiki shows. |
| `self.wait`/`pause`/`wait_until` | render via renderer | work when a window is bound (shim); without a window they fall back to manim's path (draws nowhere RTM shows). |
| `tear_down` | called by `Scene.render` at end | called once in `finally` by `record.scene_lifecycle` (only the user hook; no file-writer teardown). |
| `next_section` | writes per-section video via `--save_sections` | callable, no artifact; no `manim` CLI, no file writer. |
| `add_subcaption` | stamps at `Scene.time`, writes via file writer | stamps at window `_cursor` (recorded-timeline position) + `offset`; exported to `.srt` beside the mp4. |
| `interactive_embed`/`embed`/`set_key_function` | OpenGL interactive debug | unavailable (RTM Vulkan window, no embed link). |
| Camera pixel API (`capture_mobjects`, `capture_mobject`, `get_image`, `set_background_from_func`, `background_image`, pixel keys) | Cairo pixel pipeline | not wired; RTM renders vectors straight to window/encoder. |
| Custom camera | renders via renderer | a camera overriding `capture_mobjects`/`get_frame` (not MovingCamera/ThreeDCamera/…) falls back to **per-frame full-screen rasterisation** (`core.py::_rasterise_custom_camera`) — correct but slow. |
| Output | configurable quality/fps/format | fixed 1920×1080@60 (`MLWindow.SUPPORTED_WIDTH/HEIGHT`, `SUPPORTED_FPS`); anything else forced + prints `[rtm] forcing …`. |
| `config` | many wired keys | only `background_color` wired; `seed` indirect; `renderer` must NOT be set; `tex_dir`/`text_dir`/`assets_dir`/`tex_template(_file)` affect intermediates. |
| Paint order | CE precedence | document order default; `z_index` participates when any root has one and `camera.use_z_index`; ThreeDCamera sorts by camera-space depth; `Camera(use_z_index=False)` disables z sort. |

---

# Scene lifecycle

### `Scene.__init__`

```python
def __init__(self, renderer: CairoRenderer | OpenGLRenderer | None = None, camera_class: type[Camera] = Camera, always_update_mobjects: bool = False, random_seed: int | None = None, skip_animations: bool = False) -> None:
```

| arg | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `renderer` | `CairoRenderer \| OpenGLRenderer \| None` | `None` | do NOT pass: RTM owns window + recording. |
| `camera_class` | `type[Camera]` | `Camera` | any `Camera` subclass; dedicated scenes pre-wire it. |
| `always_update_mobjects` | `bool` | `False` | discouraged; only affects RTM's static-`Wait` decision, no observed picture change. |
| `random_seed` | `int \| None` | `None` (→ `config.seed`) | any int; fixes random sequence (calls `random.seed`/`np.random.seed` in `__init__`). |
| `skip_animations` | `bool` | `False` | discouraged; RTM does not take manim's skip path. |

- `ret`: none (constructs instance).
- `notes`:
  - do not override `__init__` except to forward ctor params; call `super().__init__(...)`; put other prep in `setup()`.
  - `camera_class` takes a **class**; RTM builds the camera with a no-arg call `camera_class()`, so ctor args are unreachable except via `functools.partial(Camera, ...)` or a subclass overriding defaults.
- `see`: ../zh_CN/01-场景与相机/场景/01-Scene基础.md

### `Scene.setup` / `Scene.construct` / `Scene.tear_down`

```python
def setup(self) -> None:
def construct(self) -> None:
def tear_down(self) -> None:
```

- `args`: none for all three; `ret`: none.
- `notes`:
  - order run by `record.py::scene_lifecycle`: `setup()` → `construct()` → `tear_down()`.
  - `tear_down()` runs exactly once, in a `finally` (a raise inside `construct()` still gets the hook, and the exception keeps propagating). Only the user hook is called — no file-writer teardown.
  - dedicated scenes build their state in `setup()`: `MovingCameraScene` → `self.camera.frame`; `ZoomedScene` → `zoomed_camera`/`zoomed_display`; `LinearTransformationScene` → grids + basis vectors + `moving_vectors`.
  - `fast_record_scene`/`record_scene` given a **no-arg callable** do NOT call `setup()` — pass a class/instance if the scene relies on it.
- `see`: ../zh_CN/01-场景与相机/场景/01-Scene基础.md

### `Scene.render`

```python
def render(self, preview: bool = False) -> bool:
```

- `args`: `preview: bool = False` — `True` opens a file viewer after render (irrelevant in RTM).
- `ret`: `bool` (`True` = scene needs re-run).
- `notes`: **RTM does not call `Scene.render`.** No video, no file-writer finish, no "open viewer". Use `fast_record_scene(...)` to produce output.
- `see`: ../zh_CN/01-场景与相机/场景/01-Scene基础.md

### `Scene.camera` / `Scene.time`

```python
@property
def camera(self) -> Camera | OpenGLCamera: ...
@property
def time(self) -> float: ...
```

| prop | type | default | meaning |
| --- | --- | --- | --- |
| `self.camera` | `Camera \| OpenGLCamera` | instance of `camera_class` | the live camera object; pan/zoom = mutate its state (e.g. `self.camera.frame`). |
| `self.time` | `float` | accumulates with frames | adds one frame `dt` per frame actually drawn (manim `add_frame` semantics); not advanced for undrawn frames. |

- `notes`: `self.time` is the renderer's accumulated clock, aligned with manim `add_frame`; read it for "seconds played".
- `see`: ../zh_CN/01-场景与相机/场景/01-Scene基础.md

---

# Content on screen (add / remove / replace / z-order)

RTM draws `scene.mobjects` in list order each frame → **add order = paint order** (earlier = below). `foreground_mobjects` always paint on top.

### `Scene.add`

```python
def add(self, *mobjects: Mobject | OpenGLMobject) -> Self:
```

- `args`: `*mobjects: Mobject` — any mobjects, multiple allowed.
- `ret`: `Self` (chainable).
- `notes`:
  - paints background→foreground in add order; re-`add`ing a mobject already in the scene moves it to the top.
  - animation-introduced mobjects (`win.play(FadeIn(x))` with `x` not in scene) are appended to the end (top); already-present objects are not reordered.
- `see`: ../zh_CN/01-场景与相机/场景/02-内容上屏.md

### `Scene.remove`

```python
def remove(self, *mobjects: Mobject) -> Self:
```

- `args`: `*mobjects: Mobject` — multiple allowed.
- `ret`: `Self`.
- `notes`: immediate (no animation). Removes children too: deleting one member of a `Group` splits the group, remaining members stay top-level. Removing an object not in the scene is a no-op. `Uncreate`/`FadeOut` call this internally at their end.
- `see`: ../zh_CN/01-场景与相机/场景/02-内容上屏.md

### `Scene.clear`

```python
def clear(self) -> Self:
```

- `args`: none. `ret`: `Self`.
- `notes`: clears both `mobjects` and `foreground_mobjects`. Objects are only detached, not destroyed; re-`add` to bring back. Re-register foreground after clearing.
- `see`: ../zh_CN/01-场景与相机/场景/02-内容上屏.md

### z-order: `bring_to_front` / `bring_to_back` / `add_foreground_mobject(s)` / `remove_foreground_mobject(s)`

```python
def bring_to_front(self, *mobjects: Mobject) -> Scene:
def bring_to_back(self, *mobjects: Mobject) -> Scene:
def add_foreground_mobjects(self, *mobjects: Mobject) -> Scene:
def add_foreground_mobject(self, mobject: Mobject) -> Scene:
def remove_foreground_mobjects(self, *to_remove: Mobject) -> Scene:
def remove_foreground_mobject(self, mobject: Mobject) -> Scene:
```

| arg | type | meaning |
| --- | --- | --- |
| `*mobjects` / `mobject` | `Mobject` | `bring_to_front` re-`add`s to top; `bring_to_back` moves to bottom; both return `Scene`. |
| `*to_remove` / `mobject` | `Mobject` | foreground registration/deregistration. Foreground objects always paint on top. |

- `ret`: `Scene`.
- `notes`:
  - `add_foreground_mobject` internally re-`add`s (so it often also moves the object to the top); `remove_foreground_mobject` only leaves the foreground list — the object stays at the list end / still on top; call `bring_to_back` to actually drop it.
  - every `win.play` re-lifts foreground objects to the top (so a foreground title is not covered by later animation objects).
- `see`: ../zh_CN/01-场景与相机/场景/02-内容上屏.md

### `Scene.replace` + query utils

```python
def replace(self, old_mobject: Mobject, new_mobject: Mobject) -> None:
def get_attrs(self, *keys: str) -> list[Any]:
def get_top_level_mobjects(self) -> list[Mobject]:
def get_mobject_family_members(self) -> list[Mobject]:
```

| arg | type | meaning |
| --- | --- | --- |
| `old_mobject` | `Mobject` | must be in the scene; else `ValueError`. If a `Group` child, replaced in place. |
| `new_mobject` | `Mobject` | must NOT already be in the scene. Paint order preserved (single slot swapped). |
| `*keys` | `str` | `get_attrs` only: attribute names. |

- `ret`: `replace` none; `get_attrs` → list of values; `get_top_level_mobjects` → top-level list; `get_mobject_family_members` → flattened list of all objects + children.
- `notes`: after `replace`, do not reference the old object. `self.wait(...)` (manim `Wait`) leaves an empty `Mobject` in `scene.mobjects` (upstream), inflating `len(self.mobjects)` by 1; `win.play(Wait(...))` does not.
- `see`: ../zh_CN/01-场景与相机/场景/02-内容上屏.md

---

# Play / wait / pause

### `MLWindow.play` (RTM form of `Scene.play`)

```python
def play(self, *animations, subcaption=None, subcaption_duration=None,
         subcaption_offset=0, **kwargs):
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `*animations` | `Animation \| _AnimationBuilder` | — | animations, multiple = **parallel** (total = max `run_time`); `.animate...` builders resolved via `.build()`. |
| `subcaption` | `str \| None` | `None` | cue text; stamped at play-start cursor + `subcaption_offset`; `.srt` written at record end. |
| `subcaption_duration` | `float \| None` | `None` | display seconds; `None` = this play's actual run_time. |
| `subcaption_offset` | `float` | `0` | start offset (s) added to play-start cursor. |
| `**kwargs` | `Any` | — | only `run_time` and `rate_func` (plus `path_arc`/`path_arc_axis`/`path_arc_centers`/`path_func`) are honoured; anything else prints a warning and is ignored. |

- `ret`: none.
- `notes`:
  - `run_time`/`rate_func` override **every** animation in the call (play-level). Different durations → separate `play` calls.
  - `SUPPORTED_PLAY_KWARGS = ("run_time", "rate_func", "path_arc", "path_arc_axis", "path_arc_centers", "path_func")`. Others warn: `[RTM] win.play(): unsupported keyword(s) … ignored …`.
  - passing a bare `Mobject` raises `TypeError` ("Unexpected argument …").
  - `win.play` validates aggregate run_time (max) via `Scene.validate_run_time`.
  - a `Wait` alone decides frozen-vs-stepping before the timeline is built (`resolve_static_wait`).
  - `self.play` is shimmed to `win.play` when a window is bound; the wiki idiom `self.play = win.play` remains valid.
- `errs`:
  - `RuntimeError: "win.play() called before the scene was bound: run \`win.scene = self\` inside construct(), or pass the scene explicitly; without it RTM has nothing to draw or record."` — set `win.scene = self`.
  - `TypeError: "Unexpected argument <X> passed to MLWindow.play(): pass an Animation or a .animate(...) builder (or Scene.add() the mobject first)."` — wrap in an animation.
  - `ValueError` — non-positive aggregate `run_time`.
- `see`: ../zh_CN/01-场景与相机/场景/03-播放与等待.md
- `eg`:
  ```python
  win.play(FadeIn(a), FadeIn(b), run_time=0.6)      # parallel
  win.play(a.animate.shift(RIGHT), run_time=0.6, rate_func=linear)
  win.play(Wait(0.4))
  ```

### `Wait` / `Scene.wait` / `Scene.pause` / `Scene.wait_until`

```python
# RTM Wait (import from real_time_manim.vulkan_bind), same params as manim's
class Wait(Animation):
    def __init__(self, run_time=1.0, rate_func=None, stop_condition=None, frozen_frame=None, **kwargs):

def wait(self, duration: float = DEFAULT_WAIT_TIME, stop_condition: Callable[[], bool] | None = None, frozen_frame: bool | None = None) -> None:
def pause(self, duration: float = DEFAULT_WAIT_TIME) -> None:
def wait_until(self, stop_condition: Callable[[], bool], max_time: float = 60) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `duration` / `run_time` | `float` | `DEFAULT_WAIT_TIME` (=`1.0`) | seconds, must be `> 0` (0/negative → `ValueError` like manim). |
| `stop_condition` | `Callable[[], bool] \| None` | `None` | evaluated once per drawn frame; truthy ends the wait early. Only during forward play/wait; FrameServer/`render_at` still renders the full duration. An exception inside it ends the wait gracefully. Mutually exclusive with `frozen_frame=True` (else `ValueError`). |
| `frozen_frame` | `bool \| None` | `None` | `True` freezes the whole wait (updaters off; this is what `self.pause` is); `False` steps updaters every frame; `None` auto-decides (freeze when no updaters/scene updaters/stop_condition, else step). |
| `max_time` | `float` | `60` | `wait_until` only: cap; ends earlier when `stop_condition` is true. |

- `ret`: none.
- `notes`:
  - prefer `win.play(Wait(0.5))` (RTM's `Wait`); `self.wait(0.5)` is equivalent.
  - `self.wait`/`self.pause`/`self.wait_until` delegate to `self.play` — ensure it reaches `win.play` (shim does this when a window is bound; otherwise set `self.play = win.play`).
  - manim's `Wait` (used by `self.wait` etc.) leaves an empty `Mobject` in `scene.mobjects` each wait; RTM's `Wait` does not.
  - `stop_condition` is only honoured during forward play — not random-access safe.
- `see`: ../zh_CN/01-场景与相机/场景/03-播放与等待.md

### `Scene.add_updater` / `Scene.remove_updater`

```python
def add_updater(self, func: Callable[[float], None]) -> None:
def remove_updater(self, func: Callable[[float], None]) -> None:
```

- `args`: `func: Callable[[float], None]` — per-frame scene-level updater receiving `dt`.
- `ret`: none.
- `notes`: scene updaters run **after** all mobject-level updaters (manim order). `remove_updater` stops it immediately. Mobject-level updaters (`mobject.add_updater`) are driven too and accept `func()` / `func(m)` / `func(m, dt)` by arity; nested `VGroup` children are driven recursively.
- `see`: ../zh_CN/01-场景与相机/场景/03-播放与等待.md

### `Scene.validate_run_time`

```python
@classmethod
def validate_run_time(cls, run_time: float, method: Callable[[Any], Any], parameter_name: str = "run_time") -> float:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `run_time` | `float` | — | must be positive, else `ValueError`. |
| `method` | `Callable` | — | method shown in the error (e.g. `self.play`). |
| `parameter_name` | `str` | `"run_time"` | param name shown in the error. |

- `ret`: validated `float`; sub-frame values warn and clamp to one frame.
- `notes`: `win.play` calls this (aggregate run_time); `wait`/`wait_until` go through `play` and are protected too.
- `see`: ../zh_CN/01-场景与相机/场景/03-播放与等待.md

---

# Sections, subcaptions & audio

### `Scene.add_sound`

```python
def add_sound(self, sound_file: str, time_offset: float = 0, gain: float | None = None, **kwargs: Any) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `sound_file` | `str` | — | `.wav`/`.mp3` path; relative paths resolve against the **run cwd** (prefer absolute). |
| `time_offset` | `float` | `0` | seconds after the current playhead (may be negative). |
| `gain` | `float \| None` | `None` | gain in **dB** (not a multiplier): `6.0` ≈ +2×, `-6` ≈ half, `None`/`0` = original. |
| `**kwargs` | `Any` | — | `gain_to_background` is forwarded; unsupported keys print an explicit warning. |

- `ret`: none.
- `notes`: RTM captures every `add_sound` via `audio_track.install_add_sound_hook`; after render all sounds are mixed into one track and muxed into the MP4 by ffmpeg (video stream not re-encoded). Timestamps use the recorded-timeline playhead (`win._cursor`, advanced after each `win.play`). The live window plays no audio.
- `errs`: `[RTM] Scene.add_sound(): unsupported parameter(s) … ignored -- RTM 不支持该参数: the RTM audio mix supports only sound_file, time_offset, gain, gain_to_background.` — drop the keyword.
- `see`: ../zh_CN/01-场景与相机/场景/04-分段字幕与声音.md
- `eg`:
  ```python
  self.add_sound("beep.wav", time_offset=0.5, gain=6.0)
  ```

### `Scene.next_section`

```python
def next_section(self, name: str = "unnamed", section_type: str = DefaultSectionType.NORMAL, skip_animations: bool = False) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `name` | `str` | `"unnamed"` | section name (non-unique). |
| `section_type` | `str` | `DefaultSectionType.NORMAL` (`"default.normal"`) | type tag for third-party consumers. |
| `skip_animations` | `bool` | `False` | skip rendering the section's animations. |

- `ret`: none.
- `notes`: **callable but produces nothing.** Sectioned output needs `--save_sections` + `sections_dir` (manim file writer); RTM has no CLI and runs no file writer, so it only records an in-memory mark. To split a long video, write one scene per section and `fast_record_scene` each, then join/split with ffmpeg.
- `see`: ../zh_CN/01-场景与相机/场景/04-分段字幕与声音.md

### `Scene.add_subcaption` / `play(..., subcaption=...)`

```python
def add_subcaption(self, content: str, duration: float = 1, offset: float = 0) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `content` | `str` | — | subtitle text. |
| `duration` | `float` | `1` | display seconds. |
| `offset` | `float` | `0` | start offset (s). |

- `ret`: none.
- `notes`: both paths land in one in-memory cue store and auto-export `.srt` beside the output mp4 (via `audio_track.apply_sounds` at record end; only written when cues exist).
  - `win.play(..., subcaption=..., subcaption_duration=..., subcaption_offset=...)`: stamped at play start + `subcaption_offset`; duration defaults to the play's actual run_time.
  - `self.add_subcaption(...)`: stamped at the current recorded-timeline position + `offset`; duration defaults to 1 s (manim semantics). `compat.py` shims this onto the window's store — a window must be bound.
- `errs`: `RuntimeError: "Scene.add_subcaption needs an MLWindow bound to the scene (create one in construct() first, as every RTM scene does)"` — bind a window.
- `see`: ../zh_CN/01-场景与相机/场景/04-分段字幕与声音.md

### `interactive_embed` / `embed` / `set_key_function` (unavailable)

```python
def interactive_embed(self) -> None:
def embed(self) -> None:
def set_key_function(self, char: str, func: Callable[[], Any]) -> None:
```

- `args`: `set_key_function` takes `char: str`, `func: Callable[[], Any]`. `ret`: none.
- `notes`: OpenGL interactive-debug API. RTM uses its own Vulkan window + Timeline, so none of the three work. For quick iteration, write small scenes and `fast_record_scene` them.
- `see`: ../zh_CN/01-场景与相机/场景/04-分段字幕与声音.md

---

# Dedicated scenes

## MovingCameraScene

### `MovingCameraScene`

```python
def __init__(self, camera_class: type[Camera] = MovingCamera, **kwargs: Any) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `camera_class` | `type[Camera]` | `MovingCamera` | `MovingCamera` (default), `MultiCamera` (also has `frame`, plus a zoom camera), or other `Camera` subclasses; **not** plain `Camera` (no `frame` → all pan/zoom inert). |
| `**kwargs` | `Any` | — | forwarded to `Scene.__init__`; only `random_seed`, `always_update_mobjects`, `skip_animations`, `renderer` accepted (else `TypeError`). |

- `ret`: none.
- `notes`: `self.camera.frame` (a `ScreenRectangle`) is created in `setup()`. Animate it (`frame.animate.set(width=...)`, `.move_to(...)`, `Restore(frame)`) for pan/zoom. While `frame` moves the whole scene is redrawn per frame.
- `errs`: `AttributeError` if you write `self.camera.frame` with a plain `Camera` (use `hasattr`).
- `see`: ../zh_CN/01-场景与相机/专用场景/01-MovingCameraScene.md

### `self.camera.frame` (viewport rect)

| prop | type | default | meaning |
| --- | --- | --- | --- |
| `width` | `float` | `14.222` | any positive; typical `2`–`14`; too small → all-black. |
| `height` | `float` | `8.0` | do not set directly: width/height locked 16:9 (setting width auto-updates height, e.g. `width=4` → `height=2.25`). |
| position (`move_to()`/`shift()`) | `Point3DLike` | `[0,0,0]` | center; `center()` is a method, not assignable. |

- `notes`: `set(width=...)` changes only zoom; `move_to(...)` changes only center; `save_state()` + `Restore(frame)` restores both. `frame.width`/`frame.height` are also writable inside updaters (see wiki sample pinning a label to the frame bottom).
- `see`: ../zh_CN/01-场景与相机/专用场景/01-MovingCameraScene.md

## ThreeDScene

### `ThreeDScene`

```python
def __init__(self, camera_class: type[ThreeDCamera] = ThreeDCamera, ambient_camera_rotation: dict | None = None, default_angled_camera_orientation_kwargs: dict | None = None, **kwargs: Any) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `camera_class` | `type[ThreeDCamera]` | `ThreeDCamera` | keep it; all `phi`/`theta`/`gamma`/`zoom` depend on `ThreeDCamera`. |
| `ambient_camera_rotation` | `dict \| None` | `None` | **stored, never read** (upstream 0.21); use `begin_ambient_camera_rotation()` instead. |
| `default_angled_camera_orientation_kwargs` | `dict \| None` | `{"phi": 70*DEGREES, "theta": -135*DEGREES}` | **stored, not applied** until `set_to_default_angled_camera_orientation()`. |
| `**kwargs` | `Any` | — | forwarded to `Scene.__init__`. |

- `ret`: none.
- `notes`: with nothing passed the initial view is **head-on** (`phi=0`, `theta=0`); the classic oblique view is not automatic. Angles are always radians (`70 * DEGREES`).
- `see`: ../zh_CN/01-场景与相机/专用场景/02-ThreeDScene.md

### `ThreeDScene.set_to_default_angled_camera_orientation`

```python
def set_to_default_angled_camera_orientation(self, **kwargs: Any) -> None:
```

- `args`: `**kwargs` override the stored dict (e.g. `phi=60 * DEGREES`).
- `ret`: none.
- `notes`: the only reader of `default_angled_camera_orientation_kwargs`; applies it via `set_camera_orientation`.
- `see`: ../zh_CN/01-场景与相机/专用场景/02-ThreeDScene.md

### `set_camera_orientation` / `move_camera`

```python
def set_camera_orientation(self, phi: float | None = None, theta: float | None = None, gamma: float | None = None, zoom: float | None = None, focal_distance: float | None = None, frame_center: Mobject | Sequence[float] | None = None, **kwargs: Any) -> None:
def move_camera(self, phi: float | None = None, theta: float | None = None, gamma: float | None = None, zoom: float | None = None, focal_distance: float | None = None, frame_center: Mobject | Sequence[float] | None = None, added_anims: Iterable[Animation] = [], **kwargs: Any) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `phi` | `float \| None` | `None` (unchanged) | polar angle (rad): `0` = head-on, `70 * DEGREES` ≈ classic oblique. |
| `theta` | `float \| None` | `None` | azimuth (rad): classic `-135 * DEGREES`. |
| `gamma` | `float \| None` | `None` | roll (rad); large values tip text over. |
| `zoom` | `float \| None` | `None` (=1.0) | `>1` closer, `<1` farther; typical `0.5`–`3`. |
| `focal_distance` | `float \| None` | `None` | focal length (perspective strength); usually left empty. |
| `frame_center` | `Mobject \| Sequence[float] \| None` | `None` (center) | mobject or `[x,y,z]`. |
| `added_anims` | `Iterable[Animation]` | `[]` | `move_camera` only: animations played simultaneously. |
| `**kwargs` | `Any` | — | `move_camera` only: forwarded to `self.play` (e.g. `run_time`). |

- `ret`: none.
- `notes`: `set_camera_orientation` is instant (one-frame jump, no animation); `move_camera` animates (calls `self.play`). Both keep `None` args unchanged. Reset with all of `phi`/`theta`/`gamma`/`zoom`/`frame_center` (e.g. `frame_center=ORIGIN`) — omitting `frame_center` leaves a previously moved center.
  - runtime `zoom` via `move_camera(zoom=…)`/`set_zoom` only took effect in RTM from 2026-10-17 (previously `camera_state` read a write-once `camera.zoom`).
- `see`: ../zh_CN/01-场景与相机/专用场景/02-ThreeDScene.md

### ambient / 3D-illusion rotation

```python
def begin_ambient_camera_rotation(self, rate: float = 0.02, about: str = "theta") -> None:
def stop_ambient_camera_rotation(self, about: str = "theta") -> None:
def begin_3dillusion_camera_rotation(self, rate: float = 1, origin_phi: float | None = None, origin_theta: float | None = None) -> None:
def stop_3dillusion_camera_rotation(self) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `rate` | `float` | `0.02` (illusion `1`) | rad/s (illusion: wobble rate); negative reverses. |
| `about` | `str` | `"theta"` | `"theta"` / `"phi"` / `"gamma"`. |
| `origin_phi` | `float \| None` | `None` (current) | illusion wobble center polar angle. |
| `origin_theta` | `float \| None` | `None` (current) | illusion wobble center azimuth. |

- `ret`: none.
- `notes`: rotation only advances **while playing** (use `win.play(Wait(...))`). `stop_*`'s `about` must match `begin_*`'s (each axis stops separately). The ctor `ambient_camera_rotation` has no such effect.
- `see`: ../zh_CN/01-场景与相机/专用场景/02-ThreeDScene.md

### fixed-in-frame / fixed-orientation

```python
def add_fixed_in_frame_mobjects(self, *mobjects: Mobject) -> None:
def remove_fixed_in_frame_mobjects(self, *mobjects: Mobject) -> None:
def add_fixed_orientation_mobjects(self, *mobjects: Mobject, **kwargs: Any) -> None:
def remove_fixed_orientation_mobjects(self, *mobjects: Mobject) -> None:
```

| arg | type | meaning |
| --- | --- | --- |
| `*mobjects` | `Mobject` | objects to pin (or release). |
| `**kwargs` | `Any` | `add_fixed_orientation_mobjects` only: `use_static_center_func: bool`, `center_func: Callable`. |

- `ret`: none.
- `notes`: `add_fixed_in_frame_mobjects` pins position **and** orientation (3D titles/formulas) and **also adds the objects to the scene** (no separate `self.add`). `add_fixed_orientation_mobjects` locks orientation only (still positioned in 3D, follows perspective). `remove_*` releases but leaves objects in the scene.
- `see`: ../zh_CN/01-场景与相机/专用场景/02-ThreeDScene.md

### `SpecialThreeDScene`

```python
def __init__(self, cut_axes_at_radius: bool = True, camera_config: dict = {"should_apply_shading": True, "exponential_projection": True}, three_d_axes_config: dict = {...}, sphere_config: dict = {"radius": 2, "resolution": (24, 48)}, default_angled_camera_position: dict = {"phi": 70 * DEGREES, "theta": -110 * DEGREES}, low_quality_config: dict = {...}, **kwargs: Any) -> None:
def get_axes(self) -> ThreeDAxes:
def get_sphere(self, **kwargs: Any) -> Surface:
def get_default_camera_position(self) -> dict:
def set_camera_to_default_position(self) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `cut_axes_at_radius` | `bool` | `True` | truncate axes at sphere radius (`False` = axes through sphere). |
| `camera_config` | `dict` | `{"should_apply_shading": True, "exponential_projection": True}` | shading + exponential projection. |
| `three_d_axes_config` | `dict` | see source | params for `get_axes()`. |
| `sphere_config` | `dict` | `{"radius": 2, "resolution": (24, 48)}` | defaults for `get_sphere(**kwargs)`. |
| `default_angled_camera_position` | `dict` | `{"phi": 70*DEGREES, "theta": -110*DEGREES}` | subclass default view (**`-110°`**, not `ThreeDScene`'s stored `-135°`). |
| `low_quality_config` | `dict` | see source | never triggers (RTM always 1080p60). |
| `**kwargs` | `Any` | — | forwarded to `ThreeDScene.__init__`. |

- `ret`: none (ctor); `get_axes` → `ThreeDAxes`; `get_sphere` → `Surface`; `get_default_camera_position` → `dict`; `set_camera_to_default_position` none.
- `notes`: upstream manim 0.21 has **three bugs** on this subclass (also crash under plain CLI): (1) reads `self.renderer` before `super().__init__()`, (2) default `three_d_axes_config` contains removed `tick_frequency`, (3) `get_axes` uses removed `axis.tick_marks`. Workarounds in the wiki sample: stub `self.renderer = SimpleNamespace(camera_config={"pixel_width": config.pixel_width})`; supply your own `three_d_axes_config` without `tick_frequency`; override `get_axes` to use `axis.get_tick_marks()`.
- `see`: ../zh_CN/01-场景与相机/专用场景/02-ThreeDScene.md

## ZoomedScene

### `ZoomedScene`

```python
def __init__(self, camera_class: type[Camera] = MultiCamera, zoomed_display_height: float = 3, zoomed_display_width: float = 3, zoomed_display_center: Point3DLike | None = None, zoomed_display_corner: Vector3D = UP + RIGHT, zoomed_display_corner_buff: float = DEFAULT_MOBJECT_TO_EDGE_BUFFER, zoomed_camera_config: dict[str, Any] = {"default_frame_stroke_width": 2, "background_opacity": 1}, zoomed_camera_image_mobject_config: dict[str, Any] = {}, zoomed_camera_frame_starting_position: Point3DLike = ORIGIN, zoom_factor: float = 0.15, image_frame_stroke_width: float = 3, zoom_activated: bool = False, **kwargs: Any) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `camera_class` | `type[Camera]` | `MultiCamera` | keep: registering the display relies on `MultiCamera.add_image_mobject_from_camera`. |
| `zoomed_display_height` | `float` | `3` | display height (screen space, independent of main frame). |
| `zoomed_display_width` | `float` | `3` | display width. |
| `zoomed_display_center` | `Point3DLike \| None` | `None` | display center; `None` positions via `corner`. |
| `zoomed_display_corner` | `Vector3D` | `UP + RIGHT` | corner (`UP+RIGHT`, `DOWN+LEFT`, …). |
| `zoomed_display_corner_buff` | `float` | `DEFAULT_MOBJECT_TO_EDGE_BUFFER` (`0.4`) | gap to corner. |
| `zoomed_camera_config` | `dict` | `{"default_frame_stroke_width": 2, "background_opacity": 1}` | zoom-camera config. |
| `zoomed_camera_image_mobject_config` | `dict` | `{}` | display `ImageMobject` config. |
| `zoomed_camera_frame_starting_position` | `Point3DLike` | `ORIGIN` | initial zoom-frame position. |
| `zoom_factor` | `float` | `0.15` | **inverse** magnification: frame size = display × `zoom_factor`; smaller = bigger zoom; typical `0.05`–`0.5`. |
| `image_frame_stroke_width` | `float` | `3` | display border width (`0`–`6`). |
| `zoom_activated` | `bool` | `False` | managed by `activate_zooming()`; do not set manually. |
| `**kwargs` | `Any` | — | forwarded to `MovingCameraScene.__init__`. |

- `ret`: none.
- `notes`: subclass of `MovingCameraScene`; `setup()` creates `self.zoomed_camera` (`MovingCamera`) and `self.zoomed_display`. `zoom_factor=0.15` ≈ 6.7×, `0.08` ≈ 12.5×.
- `see`: ../zh_CN/01-场景与相机/专用场景/03-ZoomedScene.md

### `ZoomedScene.activate_zooming`

```python
def activate_zooming(self, animate: bool = False) -> None:
```

- `args`: `animate: bool = False` — `False` shows the display in one frame; `True` plays "zoom in" then "display pop out" (calls `self.play`).
- `ret`: none.
- `notes`: registers the display into the main camera, sets it foreground, sets `zoom_activated=True`. `self.zoomed_camera.frame.move_to(target)` must come **after** this. With `animate=True`, ensure `self.play` reaches `win.play`.
- `see`: ../zh_CN/01-场景与相机/专用场景/03-ZoomedScene.md

### `get_zoom_in_animation` / `get_zoomed_display_pop_out_animation` / `get_zoom_factor`

```python
def get_zoom_in_animation(self, run_time: float = 2, **kwargs: Any) -> ApplyMethod:
def get_zoomed_display_pop_out_animation(self, **kwargs: Any) -> ApplyMethod:
def get_zoom_factor(self) -> float:
```

- `args`: `run_time: float = 2` (zoom-in only); `**kwargs` forwarded to `ApplyMethod`.
- `ret`: both animation methods → `ApplyMethod` (pass to `win.play`); `get_zoom_factor` → `float` (= frame height ÷ display height, equals ctor `zoom_factor`).
- `notes`: manual replacement for `activate_zooming(animate=True)`; order matters: (1) `self.renderer.camera.add_image_mobject_from_camera(self.zoomed_display)`, (2) `win.play(self.get_zoom_in_animation(...))`, (3) `win.play(self.get_zoomed_display_pop_out_animation(...))`, then `self.add_foreground_mobjects(self.zoomed_camera.frame, self.zoomed_display)`.
- `see`: ../zh_CN/01-场景与相机/专用场景/03-ZoomedScene.md

## VectorScene

### `VectorScene`

```python
def __init__(self, basis_vector_stroke_width: float = 6.0, **kwargs: Any) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `basis_vector_stroke_width` | `float` | `6.0` | stroke width of `get_basis_vectors()` `i_hat`/`j_hat`. |
| `**kwargs` | `Any` | — | forwarded to `Scene.__init__`. |

- `ret`: none.
- `notes`: **`add_plane()` does not set `self.plane`** — assign `self.plane = plane` manually (`get_vector`/`add_vector`/`label_vector` read it).
- `see`: ../zh_CN/01-场景与相机/专用场景/04-向量场景VectorScene.md

### `add_plane` / `add_axes`

```python
def add_plane(self, animate: bool = False, **kwargs: Any) -> NumberPlane:
def add_axes(self, animate: bool = False, color: ParsableManimColor | Iterable[ParsableManimColor] = WHITE) -> Axes:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `animate` | `bool` | `False` | `True` plays `Create` entrance (calls `self.play`). |
| `color` | color(s) | `WHITE` | `add_axes` only. |
| `**kwargs` | `Any` | — | `add_plane` only: forwarded to `NumberPlane`. |

- `ret`: `add_plane` → `NumberPlane` (assign to `self.plane`); `add_axes` → `Axes`.
- `see`: ../zh_CN/01-场景与相机/专用场景/04-向量场景VectorScene.md

### `add_vector` / `get_vector`

```python
def add_vector(self, vector: Arrow | Vector3DLike, color: ParsableManimColor | Iterable[ParsableManimColor] = PURE_YELLOW, animate: bool = True, **kwargs: Any) -> Arrow:
def get_vector(self, numerical_vector: Vector3DLike, **kwargs: Any) -> Arrow:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `vector` | `Arrow \| Vector3DLike` | — | coords like `[2, 1]` or an existing `Arrow`. |
| `color` | color(s) | `PURE_YELLOW` | used only when coords (not a prebuilt `Arrow`) are passed. |
| `animate` | `bool` | `True` | `GrowArrow` entrance (calls `self.play`). |
| `numerical_vector` | `Vector3DLike` | — | `get_vector` only. |
| `**kwargs` | `Any` | — | forwarded to `Arrow`/animation. |

- `ret`: both `Arrow`. `add_vector` adds to the scene and registers in `moving_vectors`; `get_vector` only builds (you `self.add`).
- `see`: ../zh_CN/01-场景与相机/专用场景/04-向量场景VectorScene.md

### `write_vector_coordinates` / `label_vector` / `get_vector_label`

```python
def write_vector_coordinates(self, vector: Vector, **kwargs: Any) -> Matrix:
def label_vector(self, vector: Vector, label: ManimTextLabel | str, animate: bool = True, **kwargs: Any) -> ManimTextLabel:
def get_vector_label(self, vector: Vector, label: ManimTextLabel | str, at_tip: bool = False, direction: str = "left", rotate: bool = False, color: ParsableManimColor | None = None, label_scale_factor: float = LARGE_BUFF - 0.2) -> ManimTextLabel:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `vector` | `Vector` | — | existing arrow. |
| `label` | `ManimTextLabel \| str` | — | single-char labels are typeset as a vector letter; multi-char stays horizontal. |
| `animate` | `bool` | `True` | `label_vector` only: `Write` entrance (calls `self.play`). |
| `at_tip` | `bool` | `False` | `get_vector_label`: place at arrow tip. |
| `direction` | `str` | `"left"` | `get_vector_label`: `"left"`/`"right"`. |
| `rotate` | `bool` | `False` | `get_vector_label`: tilt with vector. |
| `color` | color `\| None` | `None` (follows vector) | `get_vector_label`. |
| `label_scale_factor` | `float` | `LARGE_BUFF - 0.2` | `get_vector_label`. |
| `**kwargs` | `Any` | — | forwarded to `Matrix`/label/animation. |

- `ret`: `write_vector_coordinates` → `Matrix` (column matrix, goes foreground); `label_vector`/`get_vector_label` → label mobject (`label_vector` plays + registers; `get_vector_label` only builds).
- `see`: ../zh_CN/01-场景与相机/专用场景/04-向量场景VectorScene.md

### `get_basis_vectors` / `get_basis_vector_labels`

```python
def get_basis_vectors(self, i_hat_color: ParsableManimColor | Iterable[ParsableManimColor] = X_COLOR, j_hat_color: ParsableManimColor | Iterable[ParsableManimColor] = Y_COLOR) -> VGroup:
def get_basis_vector_labels(self, **kwargs: Any) -> VGroup:
```

- `args`: `i_hat_color` default `X_COLOR` (= `GREEN_C`); `j_hat_color` default `Y_COLOR` (= `RED_C`); `**kwargs` forwarded to label creation.
- `ret`: both `VGroup`, **not added** (call `self.add`). Stroke width = ctor `basis_vector_stroke_width`. Labels are `MathTex` (RTM Typst channel).
- `see`: ../zh_CN/01-场景与相机/专用场景/04-向量场景VectorScene.md

### `vector_to_coords`

```python
def vector_to_coords(self, vector: Vector3DLike, integer_labels: bool = True, clean_up: bool = True) -> tuple[Matrix, Line, Line]:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `vector` | `Vector3DLike` | — | e.g. `[-1, 2]`, `[1.5, -1]`. |
| `integer_labels` | `bool` | `True` | integer labels (`-1` not `-1.0`); `False` = decimals. |
| `clean_up` | `bool` | `True` | restore scene after (decomposition lines + matrix exit). |

- `ret`: `(matrix, x_line, y_line)`.
- `notes`: plays animations internally (calls `self.play`); **no `run_time` param** — fixed pacing, ~6 s per call.
- `see`: ../zh_CN/01-场景与相机/专用场景/04-向量场景VectorScene.md

### `lock_in_faded_grid` / `coords_to_vector` / `show_ghost_movement` (broken upstream)

```python
def lock_in_faded_grid(self, dimness: float = 0.7, axes_dimness: float = 0.5) -> None:
def coords_to_vector(self, vector: Vector2DLike, coords_start: Point3DLike = 2 * RIGHT + 2 * UP, clean_up: bool = True) -> None:
def show_ghost_movement(self, vector: Arrow | Vector2DLike | Vector3DLike) -> None:
```

- `ret`: none.
- `notes`: all three are broken in upstream manim 0.21 (crash under plain CLI too, not RTM-specific):
  - `lock_in_faded_grid` — calls `renderer.update_frame()` missing the `scene` arg (upstream TODO).
  - `coords_to_vector` — `Matrix(vector)` → `TypeError: 'numpy.float64' object is not iterable`.
  - `show_ghost_movement` — `VMobject(*Dots)` → `ValueError` (0.20.1: `Dot object has no attribute 'hex'`).
  - Workaround for a faded grid: `add_plane(animate=False)` then `plane.set_opacity(0.3)`.
- `see`: ../zh_CN/01-场景与相机/专用场景/04-向量场景VectorScene.md

## LinearTransformationScene

### `LinearTransformationScene`

```python
def __init__(self, include_background_plane: bool = True, include_foreground_plane: bool = True, background_plane_kwargs: dict[str, Any] | None = None, foreground_plane_kwargs: dict[str, Any] | None = None, show_coordinates: bool = False, show_basis_vectors: bool = True, basis_vector_stroke_width: float = 6, i_hat_color: ParsableManimColor = X_COLOR, j_hat_color: ParsableManimColor = Y_COLOR, leave_ghost_vectors: bool = False, **kwargs: Any) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `include_background_plane` | `bool` | `True` | grey background grid; turning it off alone still leaves grid (foreground plane has its own). |
| `include_foreground_plane` | `bool` | `True` | transformable cyan grid; off → `self.plane` is `None`, `apply_*` transforms only basis vectors. |
| `background_plane_kwargs` | `dict \| None` | `None` | override background `NumberPlane`. |
| `foreground_plane_kwargs` | `dict \| None` | `None` | override foreground `NumberPlane`. |
| `show_coordinates` | `bool` | `False` | tick numbers on the background grid. |
| `show_basis_vectors` | `bool` | `True` | show `î`/`ĵ`. |
| `basis_vector_stroke_width` | `float` | `6` | basis-vector width. |
| `i_hat_color` | color | `X_COLOR` (`GREEN_C`) | `î` color. |
| `j_hat_color` | color | `Y_COLOR` (`RED_C`) | `ĵ` color. |
| `leave_ghost_vectors` | `bool` | `False` | keep old-position ghosts after transform (basis vectors only). |
| `**kwargs` | `Any` | — | forwarded to `VectorScene.__init__` → `Scene.__init__`. |

- `ret`: none.
- `notes`: grids + basis vectors added by `setup()`; ready in `construct`. To fully clear the grid, disable both planes.
- `see`: ../zh_CN/01-场景与相机/专用场景/05-线性变换场景.md

### `apply_matrix` / `apply_inverse` / `apply_transposed_matrix` / `apply_inverse_transpose`

```python
def apply_matrix(self, matrix: np.ndarray | list | tuple, **kwargs: Any) -> None:
def apply_inverse(self, matrix: np.ndarray | list | tuple, **kwargs: Any) -> None:
def apply_transposed_matrix(self, transposed_matrix: np.ndarray | list | tuple, **kwargs: Any) -> None:
def apply_inverse_transpose(self, t_matrix: np.ndarray | list | tuple, **kwargs: Any) -> None:
```

| arg | type | meaning |
| --- | --- | --- |
| `matrix` | `np.ndarray \| list \| tuple` | 2×2; `apply_inverse` needs invertible (singular → `LinAlgError`). |
| `transposed_matrix` / `t_matrix` | same | pass the **original** matrix; the method transposes internally. |
| `**kwargs` | `Any` | forwarded to `self.play`: `run_time`, `path_arc`, … |

- `ret`: none (plays via `self.play`).
- `notes`: affect foreground grid, basis vectors, and `moving_vectors` (incl. unit square). `path_arc` is play-level and reaches `Transform.path_arc` (RTM supports it since 2026-10-17).
- `see`: ../zh_CN/01-场景与相机/专用场景/05-线性变换场景.md

### `apply_nonlinear_transformation` / `apply_function`

```python
def apply_nonlinear_transformation(self, function: Callable[[np.ndarray], np.ndarray], **kwargs: Any) -> None:
def apply_function(self, function: MappingFunction, added_anims: list[Animation] = [], **kwargs: Any) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `function` | `Callable[[np.ndarray], np.ndarray]` | — | point transform: input `[x,y,z]`, **must return a 3-tuple** `np.array([x',y',z'])`. |
| `added_anims` | `list[Animation]` | `[]` | `apply_function` only: simultaneous animations. |
| `**kwargs` | `Any` | — | forwarded to `self.play` (`run_time`, …). |

- `ret`: none.
- `notes`: `apply_nonlinear_transformation` first subdivides the grid (`prepare_for_nonlinear_transform`, smoother bends, heavier frames); `apply_function` applies per point (good for gentle stretches). Both affect grid + basis vectors + unit square + `moving_vectors`.
- `errs`: shape error if the function returns a 2-tuple — return all three components.
- `see`: ../zh_CN/01-场景与相机/专用场景/05-线性变换场景.md

### `add_title` / `get_unit_square` / `add_unit_square`

```python
def add_title(self, title: str | MathTex | Tex, scale_factor: float = 1.5, animate: bool = False) -> Self:
def get_unit_square(self, color: ParsableManimColor | Iterable[ParsableManimColor] = PURE_YELLOW, opacity: float = 0.3, stroke_width: float = 3) -> Rectangle:
def add_unit_square(self, animate: bool = False, **kwargs: Any) -> Self:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `title` | `str \| MathTex \| Tex` | — | `str` typeset via `Tex` + background bar, goes foreground; pinned `to_edge(UP)`. |
| `scale_factor` | `float` | `1.5` | `str` titles only. |
| `animate` | `bool` | `False` | `True` plays `Write` (calls `self.play`). |
| `color` | color(s) | `PURE_YELLOW` | `get_unit_square` only. |
| `opacity` | `float` | `0.3` | `get_unit_square` only. |
| `stroke_width` | `float` | `3` | `get_unit_square` only. |
| `**kwargs` | `Any` | — | `add_unit_square` only: forwarded to animation (`run_time`). |

- `ret`: `add_title`/`add_unit_square` → `Self` (in scene, registered transformable); `get_unit_square` → `Rectangle` (only built).
- `notes`: `add_title` is fixed to the top edge and covers top content — put captions at the bottom.
- `see`: ../zh_CN/01-场景与相机/专用场景/05-线性变换场景.md

### `add_vector` / `write_vector_coordinates` / `add_transformable_label`

```python
def add_vector(self, vector: Arrow | Vector3DLike, color: ParsableManimColor | Iterable[ParsableManimColor] = PURE_YELLOW, animate: bool = False, **kwargs: Any) -> Arrow:
def write_vector_coordinates(self, vector: Vector, **kwargs: Any) -> Matrix:
def add_transformable_label(self, vector: Vector, label: MathTex | str, transformation_name: str | MathTex = "L", new_label: str | MathTex | None = None, **kwargs: Any) -> MathTex:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `vector` | `Arrow \| Vector3DLike` | — | coords or existing `Arrow`; registered in `moving_vectors`. |
| `color` | color(s) | `PURE_YELLOW` | `add_vector` only. |
| `animate` | `bool` | `False` | `add_vector` only: **default off** (opposite of `VectorScene`); `True` = `GrowArrow`. |
| `label` | `MathTex \| str` | — | `add_transformable_label`: label rewritten on transform. |
| `transformation_name` | `str \| MathTex` | `"L"` | prefix after rewrite: `w` → `L(w)`. |
| `new_label` | `str \| MathTex \| None` | `None` | full custom rewritten label. |
| `label_scale_factor` | `float` | `0.8` | label scale. |
| `**kwargs` | `Any` | — | forwarded to `Arrow`/animation/label. |

- `ret`: `add_vector` → `Arrow`; `write_vector_coordinates` → `Matrix` (foreground); `add_transformable_label` → `MathTex`.
- `notes`: labels rewrite during `apply_*` playback (`w` → `L(w)`); the column matrix is in the foreground and does **not** move with the transform (intentional — coordinates of the pre-transform quantity).
- `see`: ../zh_CN/01-场景与相机/专用场景/05-线性变换场景.md

---

# Cameras

### `Camera`

```python
def __init__(self, background_image: str | None = None, frame_center: Point3D = ORIGIN, image_mode: str = "RGBA", n_channels: int = 4, pixel_array_dtype: str = "uint8", cairo_line_width_multiple: float = 0.01, use_z_index: bool = True, background: PixelArray | None = None, pixel_height: int | None = None, pixel_width: int | None = None, frame_height: float | None = None, frame_width: float | None = None, frame_rate: float | None = None, background_color: ParsableManimColor | None = None, background_opacity: float | None = None, **kwargs: Any) -> None:
```

| arg | type | default | meaning / RTM wiring |
| --- | --- | --- | --- |
| `background_image` | `str \| None` | `None` | not wired (Cairo pixel compositing). |
| `frame_center` | `Point3D` | `ORIGIN` | discouraged: CE shifts the frame; RTM stays centered (only affects `is_in_frame` center) — engines differ. |
| `image_mode` | `str` | `"RGBA"` | not wired. |
| `n_channels` | `int` | `4` | not wired. |
| `pixel_array_dtype` | `str` | `"uint8"` | not wired. |
| `cairo_line_width_multiple` | `float` | `0.01` | not wired. |
| `use_z_index` | `bool` | `True` | **wired**; runtime assignment works too. |
| `background` | `PixelArray \| None` | `None` | not wired. |
| `pixel_height` / `pixel_width` | `int \| None` | `None` → `config` | discouraged; RTM only outputs 1920×1080. |
| `frame_height` / `frame_width` | `float \| None` | `None` → `config` | discouraged; coordinate mapping fixed to `config`. |
| `frame_rate` | `float \| None` | `None` → `config` | discouraged; RTM fixed 60 fps. |
| `background_color` | color `\| None` | `None` → `config.background_color` | wired via property (see below); ctor arg cannot reach it. |
| `background_opacity` | `float \| None` | `None` → `config.background_opacity` | readable/writable but output unchanged (mp4 has no alpha). |

- `ret`: none; any `None` arg takes `config`'s same-named value.
- `notes`: `Scene` stores only the `camera_class` **class** and RTM builds the camera with `camera_class()`; ctor args are unreachable except via `functools.partial(Camera, ...)` or a subclass.
- `see`: ../zh_CN/01-场景与相机/相机/01-Camera.md

### `Camera.background_color` / `Camera.background_opacity`

```python
def background_color(self) -> ManimColor:
def background_color(self, color: ManimColor) -> None:
def background_opacity(self) -> float:
def background_opacity(self, alpha: float) -> None:
```

- `args`: `color: ManimColor` (any color string/constant, e.g. `"#1E3A5F"`, `BLUE`); `alpha: float` (0–1).
- `ret`: getters `ManimColor` / `float`; setters none. `background_color` assignment rebuilds the clear color immediately (no animation needed, re-read every frame, falls back to `config.background_color`).
- `notes`: `background_opacity` is readable/writable but does not change the picture (video stores RGB only; matches CE for opaque output).
- `see`: ../zh_CN/01-场景与相机/相机/01-Camera.md

### `Camera.is_in_frame`

```python
def is_in_frame(self, mobject: Mobject) -> bool:
```

- `args`: `mobject: Mobject` — any mobject (does not count children individually).
- `ret`: `bool` — `False` only when the object is entirely outside; any overlap → `True`. Pure math (no rendering). RTM frame is the default 14.222×8 centered at `ORIGIN`; under `MovingCamera` it follows `frame`.
- `see`: ../zh_CN/01-场景与相机/相机/01-Camera.md

### `Camera.use_z_index`

- `args`/type: `use_z_index: bool = True` — `True` sorts by `z_index` (higher paints on top); `False` paints in add order.
- `ret`: none (plain attribute; change takes effect next frame).
- `notes`: `core.py` gates the z sort with `bool(cam.use_z_index) and scan_z_index(roots)` — with equal `z_index` both modes look identical, so set differing `z_index` to see the difference.
- `see`: ../zh_CN/01-场景与相机/相机/01-Camera.md

### pixel read / manual capture (unavailable)

```python
def capture_mobjects(self, mobjects: Iterable[Mobject], **kwargs: Any) -> None:
def capture_mobject(self, mobject: Mobject, **kwargs: Any) -> None:
def get_image(self, pixel_array: PixelArray | list | tuple | None = None) -> Image.Image:
def set_background_from_func(self, coords_to_colors_func: Callable[[np.ndarray], np.ndarray]) -> None:
```

- `args`: `mobjects`/`mobject` to capture; `**kwargs` → `get_mobjects_to_display` (e.g. `excluded_mobjects=[...]`); `pixel_array` (`None` = current frame); `coords_to_colors_func: (x,y) -> RGBA float[4]`.
- `ret`: `get_image` → `PIL.Image.Image`; the rest none.
- `notes`: Cairo pixel-array pipeline; RTM has no readable pixel array — these return no current frame. To grab a frame, render with `fast_record_scene` then extract with ffmpeg. Distinguish from `Mobject.color_using_background_image`, which RTM only samples for an average stroke color.
- `see`: ../zh_CN/01-场景与相机/相机/01-Camera.md

### `MovingCamera`

```python
def __init__(self, frame: Mobject | None = None, fixed_dimension: int = 0, default_frame_stroke_color: ManimColor = WHITE, default_frame_stroke_width: int = 0, **kwargs: Any) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `frame` | `Mobject \| None` | `None` → `ScreenRectangle(height=config.frame_height)` | do not pass: `Camera.__init__` rewrites `frame_height`/`frame_width`/`frame_center`, pulling a custom frame back to 8.0×14.222 at the origin. |
| `fixed_dimension` | `int` | `0` | do not pass: stored, never read in 0.21. |
| `default_frame_stroke_color` | `ManimColor` | `WHITE` | frame stroke color; drawn only if the frame is explicitly added and stroke visible. |
| `default_frame_stroke_width` | `int` | `0` | frame stroke width (`0` = no pixels). |
| `**kwargs` | `Any` | — | forwarded to `Camera.__init__`. |

- `ret`: none.
- `notes`: readable/writable properties `frame_height`, `frame_width`, `frame_center`; `frame` is the viewport mobject.
- `see`: ../zh_CN/01-场景与相机/相机/02-MovingCamera.md

### `MovingCamera.frame_height` / `frame_width` / `frame_center`

```python
def frame_height(self) -> float:
def frame_height(self, frame_height: float) -> None:
def frame_width(self) -> float:
def frame_width(self, frame_width: float) -> None:
def frame_center(self) -> Point3D:
def frame_center(self, frame_center: Point3DLike | Mobject) -> None:
```

| prop | type | default | meaning |
| --- | --- | --- | --- |
| `frame_height` | `float` | `8.0` | current frame height. |
| `frame_width` | `float` | `14.222` | current frame width. |
| `frame_center` | `Point3DLike` or `Mobject` | `[0,0,0]` | center; a mobject pans the camera to it. |

- `ret`: getters `float`/`Point3D`; setters none (immediate).
- `notes`: **deviation** — `frame_height`/`frame_width` are independent setters: CE scales each axis separately (distortion), RTM scales by height only and ignores width → engines differ. For a safe proportional zoom assign both in 16:9 (e.g. `h` then `w = h*16/9`) or use `frame.animate.set(width=...)`.
- `see`: ../zh_CN/01-场景与相机/相机/02-MovingCamera.md

### `MovingCamera.auto_zoom`

```python
def auto_zoom(self, mobjects: Iterable[Mobject], margin: float = 0, only_mobjects_in_frame: bool = False, animate: bool = True) -> _AnimationBuilder | Mobject:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `mobjects` | `Iterable[Mobject]` | — | target(s); single or list. |
| `margin` | `float` | `0` | extra padding (manim units), added only on the tighter edge. |
| `only_mobjects_in_frame` | `bool` | `False` | `True` ignores objects currently off-screen. |
| `animate` | `bool` | `True` | `True` returns a playable builder (give to `win.play`); `False` applies instantly. |

- `ret`: `animate=True` → animation builder; else the updated frame.
- `notes`: only valid for 2D XY content (inaccurate if the camera is rotated).
- `see`: ../zh_CN/01-场景与相机/相机/02-MovingCamera.md

### `ThreeDCamera`

```python
def __init__(self, focal_distance: float = 20.0, shading_factor: float = 0.2, default_distance: float = 5.0, light_source_start_point: Point3DLike = 9 * DOWN + 7 * LEFT + 10 * OUT, should_apply_shading: bool = True, exponential_projection: bool = False, phi: float = 0, theta: float = -90 * DEGREES, gamma: float = 0, zoom: float = 1, **kwargs: Any) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `focal_distance` | `float` | `20.0` | focal length; larger = flatter; runtime `set_focal_distance`. |
| `shading_factor` | `float` | `0.2` | stored, never read in 0.21 (dead). |
| `default_distance` | `float` | `5.0` | stored, never read (dead). |
| `light_source_start_point` | `Point3DLike` | `9*DOWN + 7*LEFT + 10*OUT` | light position; flipping it flips cube shading. |
| `should_apply_shading` | `bool` | `True` | 3D shading; runtime assignment works. |
| `exponential_projection` | `bool` | `False` | reduce far-field distortion; runtime assignment works. |
| `phi` | `float` | `0` | initial polar angle (rad); **effective** (unlike `ThreeDScene`'s stored default). |
| `theta` | `float` | `-90 * DEGREES` | initial azimuth (rad); effective. |
| `gamma` | `float` | `0` | initial roll (rad); effective. |
| `zoom` | `float` | `1` | initial zoom; effective. |
| `**kwargs` | `Any` | — | forwarded to `Camera.__init__`. |

- `ret`: none.
- `notes`: pass ctor args via `functools.partial(ThreeDCamera, ...)` or a subclass. Angles stored in 5 `ValueTracker`s (`phi`/`theta`/`focal_distance`/`gamma`/`zoom`). `phi`/`theta`/`gamma`/`zoom` ctor args **do** work in RTM and CE; only `ThreeDScene`'s `default_angled_camera_orientation_kwargs`/`ambient_camera_rotation` are stored-not-used.
- `see`: ../zh_CN/01-场景与相机/相机/03-ThreeDCamera.md

### `ThreeDCamera` view params (get/set/trackers)

```python
def get_phi(self) -> float:
def get_theta(self) -> float:
def get_gamma(self) -> float:
def get_zoom(self) -> float:
def get_focal_distance(self) -> float:
def set_phi(self, value: float) -> None:
def set_theta(self, value: float) -> None:
def set_gamma(self, value: float) -> None:
def set_zoom(self, value: float) -> None:
def set_focal_distance(self, value: float) -> None:
def get_value_trackers(self) -> list[ValueTracker]:
```

- `args`: `value: float` — `set_phi`/`set_theta`/`set_gamma` radians (with `DEGREES`), `set_zoom` multiplier, `set_focal_distance` length; all immediate (no animation).
- `ret`: five `get_*` → `float`; `get_value_trackers()` → `[phi, theta, focal_distance, gamma, zoom]` (animate a tracker for a smooth view change).
- `notes`: `set_*` are instant jumps; for smooth transitions animate the trackers or use `ThreeDScene.move_camera`.
- `see`: ../zh_CN/01-场景与相机/相机/03-ThreeDCamera.md

### `ThreeDCamera.add_fixed_in_frame_mobjects` / `add_fixed_orientation_mobjects`

```python
def add_fixed_in_frame_mobjects(self, *mobjects: Mobject) -> None:
def remove_fixed_in_frame_mobjects(self, *mobjects: Mobject) -> None:
def add_fixed_orientation_mobjects(self, *mobjects: Mobject, use_static_center_func: bool = False, center_func: Callable[[], Point3D] | None = None) -> None:
def remove_fixed_orientation_mobjects(self, *mobjects: Mobject) -> None:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | — | objects to pin/release. |
| `use_static_center_func` | `bool` | `False` | pin the rotation center at call time. |
| `center_func` | `Callable[[], Point3D] \| None` | `None` | custom orientation-lock center. |

- `ret`: none.
- `notes`: the **camera** `add_fixed_*` only registers how objects are drawn — it does **not** add them to the scene; `self.add(...)` them yourself (the `ThreeDScene` methods of the same name do add them). `remove_*` releases the lock, objects stay in the scene.
- `see`: ../zh_CN/01-场景与相机/相机/03-ThreeDCamera.md

### `ThreeDCamera.project_point` / `project_points`

```python
def project_point(self, point: Point3D) -> Point3D:
def project_points(self, points: Point3D_Array) -> Point3D_Array:
```

- `args`: `point` / `points` — 3D point(s).
- `ret`: screen coords `[x,y,z]` under the current view (per-row array for `project_points`). Values change when the view changes.
- `see`: ../zh_CN/01-场景与相机/相机/03-ThreeDCamera.md

### `ThreeDCamera.capture_mobjects` (unavailable)

```python
def capture_mobjects(self, mobjects: Iterable[Mobject], **kwargs: Any) -> None:
```

- `ret`: none. Cairo pixel-capture entry; no RTM pixel array (same as `Camera.capture_*`).
- `notes`: `get_rotation_matrix` (current 3×3 rotation) and `project_*` are pure computation and always available.
- `see`: ../zh_CN/01-场景与相机/相机/03-ThreeDCamera.md

---

# Config

## `config` quality/output keys (mostly not wired)

Only `background_color` is wired. `seed` is indirect; `renderer` must NOT be set (bundled ManimCE reads it). Everything else has no effect on RTM output.

| key | type | default | RTM |
| --- | --- | --- | --- |
| `pixel_width` | `int` | `1920` | not wired; output fixed 1920 (from `MLWindow`). |
| `pixel_height` | `int` | `1080` | not wired. |
| `quality` | `str \| None` | `high_quality` | not wired; only 1920×1080@60. |
| `frame_rate` | `float` | `60` | not wired; use `fast_record_scene(fps=...)`, only 60. |
| `format` | `str \| None` | `mp4` | not wired; mp4 only (per-frame via `segment=(...)` BMP). |
| `output_file` | `str` | `""` | not wired; use `fast_record_scene(out_path=...)`. |
| `background_color` | `ManimColor` | `BLACK` | **wired** (see below). |
| `background_opacity` | `float` | `1` | not wired; output always opaque. |
| `transparent` | `bool` | `False` | not wired. |
| `save_last_frame` | `bool` | `False` | not wired; use `segment=(n, n+1)`. |
| `write_to_movie` | `bool` | `True` | not wired; use `count_only=True`. |
| `write_all` | `bool` | `False` | not wired. |
| `save_sections` | `bool` | `False` | not wired; split into scenes. |
| `zero_pad` | `int` | `4` | not wired. |
| `movie_file_extension` | `str` | `.mp4` | not wired; always `.mp4`. |
| `from_animation_number` | `int` | `0` | not wired; comment out `win.play(...)`. |
| `upto_animation_number` | `int` | `-1` | not wired. |
| `preview` | `bool` | `False` | not wired; use `fast_record_scene(hidden=False)` / `record_scene`. |
| `show_in_file_browser` | `bool` | `False` | not wired. |
| `verbosity` | `str` | `INFO` | not wired; use `fast_record_scene(verbose=...)`. |
| `progress_bar` | `str` | `display` | not wired; prints one `[FastRecord] Saved: ...`. |
| `disable_caching` / `flush_cache` / `max_files_cached` / `disable_caching_warning` | — | — | not wired (no fragment cache). |
| `seed` | `int \| None` | `None` | **indirect**: `Scene.__init__` `random_seed` default is `config.seed`. Prefer explicit `random_seed=...`. |
| `renderer` | `RendererType` | `cairo` | **do NOT set**: bundled ManimCE reads it broadly; `opengl` breaks behavior. |
| `dry_run` | `bool` | `False` | not wired; use `count_only=True`. |
| `save_pngs` / `save_as_gif` | `bool` | `False` | not wired (deprecated). |

- `notes`: writing these does not error but mostly does nothing. `config.frame_rate = 30` does not give 30 fps (always 60); convert with ffmpeg afterwards.
- `see`: ../zh_CN/01-场景与相机/配置/01-画质与输出.md

### `background_color` / `background_opacity`

```python
self.camera.background_color: ManimColor = BLACK   # clear color; RTM reads it every frame, falls back to config.background_color
self.camera.background_opacity: float = 1.0        # stored on the camera only; opaque mp4 unchanged (same as ManimCE)
```

- `args`: any manim color (`"#12233a"`, `BLUE`, `"#e8e4d8"`, …).
- `notes`: `background_color` is the only wired config key; assign at any time (re-read each frame). `background_opacity` (0–1) is readable/writable but never changes the picture. Keep text/figure colors contrasting with the background.
- `see`: ../zh_CN/01-场景与相机/配置/01-画质与输出.md

## Frame geometry (`config` layout keys)

```python
config.frame_width: float = 14.222222   # logical width; frame_x_radius = half
config.frame_height: float = 8.0        # logical height; frame_y_radius = half
```

| key | type | default | RTM |
| --- | --- | --- | --- |
| `frame_height` | `float` | `8.0` | readable (edge/next_to margins use it); **discouraged to write** — CE reads it at camera construction, RTM at imaging time. |
| `frame_width` | `float` | `14.222…` (= 8×16/9) | readable; discouraged to write. |
| `frame_y_radius` | `float` | `4.0` | `frame_height/2`; writing cascades. |
| `frame_x_radius` | `float` | `7.111…` | `frame_width/2`; writing cascades. |
| `top` / `bottom` | `Vector3D` | `[0, ±4, 0]` | read-only edge midpoints (`move_to(config.top)`). |
| `left_side` / `right_side` | `Vector3D` | `[±7.111…, 0, 0]` | read-only. |
| `aspect_ratio` | `float` | `1.777…` | read-only (16/9). |
| `frame_size` | `tuple[int, int]` | `(1920, 1080)` | read-only. |

- `notes`: do not change the frame by writing these keys (CE and RTM read them at different times). Use `MovingCameraScene`'s `self.camera.frame.animate.set(width=...)`. The curve/line scaling mismatch was fixed 2026-10-16; `config` is global, so restore values you change.
- `see`: ../zh_CN/01-场景与相机/配置/02-画幅坐标.md

## Paths & window (`config` keys)

Final video path is never taken from `config`; only intermediate dirs matter.

| key | type | default | RTM |
| --- | --- | --- | --- |
| `media_dir` | `str` | `./media` | final output not wired; but `tex_dir`/`text_dir` default under it. `util.clear_media()` only deletes `<cwd>/media` (does not follow `config.media_dir`). |
| `video_dir` / `sections_dir` / `images_dir` / `partial_movie_dir` | `str` | templates | not wired. |
| `tex_dir` | `str` | `{media_dir}/Tex` | **wired** for intermediates (LaTeX/Typst compile dir). |
| `text_dir` | `str` | `{media_dir}/texts` | **wired** for intermediates (`Text` svg cache). |
| `log_dir` | `str` | `{media_dir}/logs` | not wired (no log file). |
| `assets_dir` | `str` | `./` | **wired** for lookup (`get_full_raster_image_path`/svg/audio). |
| `input_file` / `scene_names` / `custom_folders` | — | — | not wired. |
| `tex_template` | `TexTemplate` | default | **effective** (real object; RTM uses manim's LaTeX pipeline). |
| `tex_template_file` | `Path` | `""` | **effective** (loads a template when non-empty). |
| `plugins` / `log_to_file` / `ffmpeg_loglevel` / `notify_outdated_version` | — | — | not wired. |
| `no_latex_cleanup` | `bool` | `False` | not wired; RTM's `cleanup` is inverted (default deletes manim `media/`, `cleanup=False` keeps it). |
| `preview_command` | `str` | `""` | not wired. |

Window keys (all not wired): `enable_gui`, `gui_location`, `fullscreen`, `window_position`, `window_size`, `window_monitor`, `force_window`, `enable_wireframe`, `use_projection_fill_shaders`, `use_projection_stroke_shaders`, `media_embed`, `media_width`. The RTM window comes from `MLWindow(w, h, hidden)`; `hidden` only affects whether a window pops on your desktop, not the recorded video.

- `see`: ../zh_CN/01-场景与相机/配置/03-路径与窗口.md

## ManimCE CLI (RTM has no CLI)

No `manim` command is shipped (`manim/cli/` and `__main__.py` removed; no console script). RTM entry points:

| want | CLI flag | RTM |
| --- | --- | --- |
| resolution | `-r W,H` | `MLWindow(w, h)` (only 1920×1080) |
| fps | `--fps F` | `fast_record_scene(fps=...)` (only 60) |
| format | `--format` | mp4 only; per-frame `segment=(...)` BMP |
| output name | `-o` | `out_path="my.mp4"` |
| media dir | `--media_dir` | `out_path` is a direct file path |
| last frame | `-s` | `segment=(n, n+1)` |
| from/to animation | `-n` | comment out `win.play(...)` |
| write all | `-a` | call per scene in your script |
| sections | `--save_sections` | split into scenes |
| renderer | `--renderer` | Vulkan, no choice |
| cache flags | `--disable_caching` etc. | no cache |
| seed | `--seed` | `random_seed=...` |
| transparent | `-t` | always opaque |
| pngs/gif | `-g` / `-i` | `segment=(...)` BMP / no GIF |
| dry run | `--dry_run` | `count_only=True` |
| verbosity | `-v` | `verbose=...` |
| preview | `-p` | `hidden=False` or `record_scene` |
| force window | `--force_window` | `hidden=False` |
| LaTeX template | `--tex_template` | `config.tex_template` / `config.tex_template_file` |
| keep LaTeX | `--no_latex_cleanup` | `cleanup=False` |

- `notes`: `manim cfg` / `manim init` / `manim plugins -l` / `manim checkhealth` are all unsupported. Installing ManimCE separately gives a working `manim` command, but that renders CE output, not RTM.
- `see`: ../zh_CN/01-场景与相机/配置/04-ManimCE命令行速查.md

## RTM record & window params

### `fast_record_scene(...)`

```python
def fast_record_scene(scene, out_path=None, *, fps=60, hidden=True,
                      count_only=False, segment=None, overwrite=True,
                      cleanup=True, verbose=True, jobs=None) -> dict:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `scene` | Scene class / instance / no-arg callable | — (required) | class (runs `setup()`+`construct()`), instance, or any no-arg callable (RTM does **not** call `setup()` for a callable). |
| `out_path` | `str \| None` | `None` → `~/Downloads/output.mp4` | output file path (not a dir template); subdirs auto-created; extra windows append `_partN`. |
| `fps` | `int` | `60` | only 60; else prints `[rtm] forcing 60 fps` and still renders 60. |
| `hidden` | `bool` | `True` | `True` never shows a window (offline full speed); `False` shows while rendering. |
| `count_only` | `bool` | `False` | probe: count frames, no capture/GPU/write. |
| `segment` | `tuple \| None` | `None` | `(start_frame, end_frame)` → BMP dir (then `out_path` is a directory). |
| `overwrite` | `bool` | `True` | `False` → `FileExistsError` if target exists. |
| `cleanup` | `bool` | `True` | delete manim's `media/` after recording; `False` keeps it. |
| `verbose` | `bool` | `True` | print per-window progress lines. |
| `jobs` | `int \| str \| None` | `None` | worker processes for pipe mode (source-only; not in wiki). `None` = single pass; `"auto"` probes then splits if worthwhile; int = that many workers. Splitting needs an importable Scene class; ignored for `count_only`/`segment`/`hidden=False`. |

- `ret`: `dict` — `{"out_path": ..., "windows": [...], "files": [...], "with_audio": [...]}`; `files` = real on-disk outputs (`count_only` → empty).
- `errs`: `FileExistsError: "target already exists: ... (pass overwrite=True to replace it)"` — pass `overwrite=True` or remove the file.
- `notes`: the `.srt`/audio mux happens here; the audio track is applied via `audio_track.apply_sounds` at record end.
- `see`: ../zh_CN/01-场景与相机/配置/05-RTM的录制与窗口参数.md
- `eg`:
  ```python
  from real_time_manim.record import fast_record_scene
  fast_record_scene(MyScene, out_path="clips/demo.mp4", fps=60, hidden=True)
  ```

### `record_scene(...)`

```python
def record_scene(scene, out_path=None, *, fps=60, overwrite=True,
                 cleanup=True, verbose=True) -> dict:
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `scene` | class / instance / no-arg callable | — (required) | same three forms. |
| `out_path` | `str \| None` | `None` → `~/Downloads/output.mp4` | output `.mp4`. |
| `fps` | `int` | `60` | capture rate (background thread); only 60. |
| `overwrite` | `bool` | `True` | as `fast_record_scene`. |
| `cleanup` | `bool` | `True` | as `fast_record_scene`. |
| `verbose` | `bool` | `True` | as `fast_record_scene`. |

- `ret`: `dict` (same shape; `with_audio` from the mux step).
- `notes`: window must be visible; plays in real time while a background thread grabs frames (`win.start_record(...)` … `win.stop_record()`). Frame counts are not aligned with offline rendering (wall-clock). For frame-exact output use `fast_record_scene`.
- `see`: ../zh_CN/01-场景与相机/配置/05-RTM的录制与窗口参数.md

### `MLWindow(w, h, hidden)`

```python
def __init__(self, w=1920, h=1080, hidden=None):
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `w` | `int` | `1920` | framebuffer width; only 1920 (else `[rtm] forcing 1920x1080`). |
| `h` | `int` | `1080` | framebuffer height; only 1080. |
| `hidden` | `bool \| None` | `None` → class attr `_hidden_default` | `True` build hidden / `False` visible / `None` follow default. Usually set via `fast_record_scene(hidden=...)`. |

- `notes`: forced spec — 1920×1080 (`MLWindow.SUPPORTED_WIDTH/HEIGHT`) and 60 fps (`SUPPORTED_FPS`). Bind with `win.scene = self`, drive with `win.play(...)`, finish with `win.close()` (required, or nothing is flushed and the run may not exit). `close()` itself does no record finish — `_AutoRecord` wraps it to call `_finish_fast_record()` / `stop_record()` first.
- `see`: ../zh_CN/01-场景与相机/配置/05-RTM的录制与窗口参数.md
- `eg`:
  ```python
  win = MLWindow(960, 540)   # -> prints [rtm] forcing 1920x1080
  win.scene = self
  win.play(Create(Square()))
  win.close()
  ```

### `MLWindow.enable_fast_record(...)`

```python
def enable_fast_record(self, path, fps=60, segment=None, hidden=True, count_only=False):
```

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `path` | `str` | — (required) | mp4 output path (pipe mode) or BMP frame dir (`segment` mode). |
| `fps` | `int` | `60` | non-60 forced to `SUPPORTED_FPS` with a notice. |
| `segment` | `tuple \| None` | `None` | `(start, end)` → BMP dir mode. |
| `hidden` | `bool` | `True` | hidden window (win32 `ShowWindow(SW_HIDE)`). |
| `count_only` | `bool` | `False` | count frames only. |

- `notes`: low-level entry used by `fast_record_scene`. If you use this layer directly you own the finish: `MLWindow.close()` alone does not close the encoder — you must call the internal `win._finish_fast_record()`, or the ffmpeg pipe stays open and the video is incomplete/absent. Live counterpart: `win.start_record(path, fps=60)` … `win.stop_record()`. `segment` BMP files start at `frame_000000.bmp`.
- `see`: ../zh_CN/01-场景与相机/配置/05-RTM的录制与窗口参数.md
