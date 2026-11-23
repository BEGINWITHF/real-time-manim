# Frame Preview (Frame Skipping)

> Note: interactive preview is an RTM-only capability; the window and control bar are described below. Regression tests: `tests/test_preview_spec.py` (20 items) and `tests/test_preview_mac_bar.py` (19 items); frame-skip timings are in the measurement table below.

A window pops up and **plays nothing by default**, with a control bar (a text box or a slider) attached to it. Fill in **any frame** and press Enter, and that frame **immediately** appears in the window: you neither pre-render the whole video nor replay from the start up to that frame.
On Windows and macOS the bar is a native window of its own, docked directly below the video window; on macOS it is also kept clear of an auto-hiding Dock.

```bash
python -m real_time_manim.preview 1                    # demo 1 in run.py
python -m real_time_manim.preview examples.scenes:DemoCreate --at 120
```

## Why frames can appear "immediately"

RTM 2.0's rendering layer is **time-addressable**: animations are defined as pure functions of `alpha` (and hence of time `t`), so `Timeline.render_at(t)` evaluates once and draws a single frame, at a cost independent of `t` (O(1)), rather than "playing from the start up to frame t". Preview mode wires this up to interaction:

| Stage | What it does | Measured cost |
| --- | --- | --- |
| Preparation (one-off) | run `construct()` once, **scheduling only, no drawing** (`play` becomes recording animation semantics, `FrameServer`) | 2.5s scene: 0.26s (warm) / 1.4–1.9s (cold); 6.3s scene: 0.30–0.43s |
| Each seek | `Timeline.render_at(t)` → `sync` → one `tick` frame | **1.3–7.5 ms**, independent of where you land |

That is to say: **there is no pre-rendering at all** — the frame 0 you see is drawn when the window appears, and every later frame is drawn only when you type it in.

> A seek replays **animation** state; objects driven only by a custom updater / `TracedPath` **step forward exactly but jump backwards only approximately** (making this kind of state "replayable from `t`" is P3 on the RTM 2.0 plan).

## Control bar: text box or slider

The control bar has two appearances, chosen by `controls=` (the `--controls` command-line flag):

| `controls` | Control bar | How to skip frames |
| --- | --- | --- |
| `"input"` (default) | `[ text box ] [Jump] [Save PNG] [Quit]` | fill the text box with a frame number / seconds / step, then press Enter or click `Jump` |
| `"slider"` | `[═════╪═════] [Save PNG] [Quit]` | drag the slider (**dragging itself samples frames live**, and rapid-fire seeks are coalesced automatically so only the newest frame is drawn) |

Both modes show `frame 123/347   t=2.050s` live in the control bar's title bar (on macOS the video window keeps its own `Real Time Manim` title, because the bar is a separate window). The video keeps its exact aspect ratio when the window is resized; the bar follows its width and stays docked underneath.

```bash
python -m real_time_manim.preview 3 --controls slider
python -m real_time_manim.preview 3 --controls input
```

> Multiple previews at once: the video windows are native windows placed by the system by default, so they may **overlap**; separate them with `--pos X,Y` (or `position=(x, y)`).
>
> The control bar **always stays with its video window**: it is glued to the bottom edge on both platforms (drag the video window and the bar follows).

## Input syntax (typed into the text box in `input` mode)

| Input | Meaning |
| --- | --- |
| `120` / `120f` | **frame 120** (the default unit is frames) |
| `1.5` / `1.5s` | 1.5 seconds |
| `+10` / `-1` | jump N frames forward / backward from the current frame |
| `s` | save the current frame as a PNG (default `frames/`, change it with `--out`) |
| `p` | play from the current frame (any input interrupts it) |
| `?` | print help |
| `q` | quit |

Out-of-range values are clamped into the valid range (`-999` → frame 0); input it cannot parse prints a hint instead of crashing (for example `cannot read '#' -- try 120, 2.5s, +1, s, q`).

## Parameters

```python
FramePreview(scene_cls, fps=60, out_dir="frames", use_bar=True,
             width=None, height=None, verbose=True,
             controls="input", position=None)
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `scene_cls` | `type \| instance \| Callable` | — | the scene to preview (same forms as `fast_record_scene`) |
| `fps` | `int` | `60` | **frame rate for frame-number conversion**: `120` means frame 120, i.e. `t = 120 / fps` |
| `out_dir` | `str` | `"frames"` | directory where `s` / `Save PNG` stores images |
| `use_bar` | `bool` | `True` | when `False`, falls back to **terminal input** (the same syntax and queue protocol); also automatic on platforms without a native bar |
| `width` / `height` | `int \| None` | `None` | window size (RTM only supports 1920×1080 and will force-correct it) |
| `verbose` | `bool` | `True` | print the preparation time and status lines |
| `controls` | `str` | `"input"` | `"input"` (text box) / `"slider"` (slider); the aliases `box`/`text`/`edit` and `bar`/`progress`/`scrub` are all accepted, anything else raises `ValueError` |
| `position` | `tuple \| None` | `None` | top-left corner `(x, y)` of the video window, used to separate multiple previews; the string form `"100,80"` is also accepted |

Equivalent command-line flags:

| Flag | Description |
| --- | --- |
| `scene` (positional) | demo number (`SCENES` in `run.py`) or `module:Class` |
| `--at N` | show frame N first when opening (default 0) |
| `--fps N` | frame rate for frame-number conversion (default 60) |
| `--out DIR` | image directory (default `frames/`) |
| `--controls {input,slider}` | control bar appearance |
| `--pos X,Y` | video window position |
| `--no-bar` | input only in the terminal (no control bar) |
| `--quiet` | print less |

## Example

```python
from real_time_manim import FramePreview          # top-level lazy export
from examples.scenes import DemoCreate

FramePreview(DemoCreate).run()                     # text box mode
FramePreview(DemoCreate, controls="slider").run()  # slider mode
FramePreview(DemoCreate, use_bar=False).run()      # terminal input
```

You can also use it purely as a "prepare once, grab any frame" library (the `FrameServer` behind the preview):

```python
from real_time_manim import FrameServer
fs = FrameServer(DemoCreate)      # run construct() once, drawing nothing
fs.show_frame(2.05)               # show t=2.05s (about 10 ms)
fs.save_frame(2.05, "f205.png")   # save it as a PNG while you are at it
fs.close()
```

## Video tutorial

TODO: Tagin records the tutorial video himself

See also: [Recording Video](04-Recording-Video.md) · [Live Window MLWindow](03-Live-Window-MLWindow.md) · [Play and Wait (Scene chapter)](../01-Scenes-and-Cameras/Scenes/03-Play-and-Wait.md)
