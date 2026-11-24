# Using LLMs and Agents

real-time-manim is a young project: general-purpose LLMs (ChatGPT, Claude, etc.) have almost nothing about it in their training data — but RTM itself is **ManimCE's data model + a Vulkan window**, so a model that can write ManimCE already knows 90% of the job. The missing piece is just the RTM shell. This page teaches you how to feed that shell to the model: with the right context, the RTM code it writes usually runs first try.

## 1. What your model knows and doesn't

| It already knows | It doesn't (RTM-specific) |
| --- | --- |
| All ManimCE classes, animations, colors (RTM bundles ManimCE 0.21.0 — the namespace is identical) | The window layer: `MLWindow`, `win.play`, `win.scene`, `win.close` |
| Writing Python, reading tracebacks | RTM has **no manim CLI** — you render via `fast_record_scene` |
| Everything in generic Manim tutorials | RTM rules: fixed 1920×1080@60, Vulkan, typst routing |

Bottom line: **don't make it relearn ManimCE — only fill in the RTM layer**. Here it is.

## 2. Paste this context block to it

For any model (web chat, Claude Code, Codex — all work), paste this block before the first request. English is recommended — the agent-facing reference docs are in English:

```text
You are writing real-time-manim (RTM) code. RTM is a Vulkan real-time rendering
backend for ManimCE: it bundles ManimCE 0.21.0 and re-exports the whole namespace,
so every ManimCE class/animation works — but the driving layer is different.

Hard facts (do not contradict these):
- Import name: real_time_manim (underscores). Never write real-time-manim (the
  pip package name, hyphens) in an import. Always import real_time_manim first.
- There is NO manim CLI. Render from Python:
    fast_record_scene(SceneClass, "out.mp4")   # offline, no window, frame-exact
    record_scene(SceneClass, "out.mp4")        # visible window, wall-clock
- Every scene must create an MLWindow inside construct():
    win = MLWindow(960, 540)   # size is force-corrected to 1920x1080
    win.scene = self           # REQUIRED binding
    win.play(...)              # playback goes through the window, not self.play
    win.close()                # REQUIRED, or nothing is flushed
- Output is fixed at 1920x1080 @ 60 fps: no -ql/-qm quality flags, no --fps,
  no transparent output, manim.cfg is mostly not read.
- MathTex compiles via Typst when the typst extra is installed (no LaTeX needed);
  Tex always needs LaTeX.
- Reference (read before coding, in this order): RTM-Wiki/agent/README.md first,
  then the domain file (runtime, scene-camera, mobject, animation-transform,
  animation-motion, geometry, text, coords-charts, three-d, graph-vector, utils),
  then gotchas.md for errors, patterns.md for recipes.
```

### Explanation

- The first line establishes the RTM–ManimCE relationship: the model treats RTM not as an unknown library but as "the stack it already knows + a window layer";
- The "Hard facts" are all hard constraints (see [Recording methods](03-Recording-Methods.md) and the parameter tables in each chapter) — with them, the model won't invent a nonexistent `manim -qh`;
- The last paragraph is a reading list: reading the reference before coding beats trial-and-error.

## 3. Point it at the agent wiki

The repo contains a whole **agent-facing condensed reference**: `RTM-Wiki/agent/`, 14 files covering all of chapters 00–08 plus an error catalog and recipes:

| File | Covers |
| --- | --- |
| `README.md` | Overview: facts, hard constraints, entry points, execution modes, read order (**read it first**) |
| `runtime.md` | Install, run, MLWindow, recording, arbitrary frames, Timeline |
| `scene-camera.md` | Scene lifecycle, play/wait, adding to screen, special scenes, cameras, config |
| `mobject.md` / `animation-transform.md` / `animation-motion.md` / `geometry.md` / `text.md` / `coords-charts.md` / `three-d.md` / `graph-vector.md` / `utils.md` | Domain references (matching chapters 01–08 of this manual) |
| `gotchas.md` | Error catalog: error → cause → fix (read before debugging) |
| `patterns.md` | Copy-pasteable recipes: scene skeletons, updaters, cameras, 3D, charts… |

Two ways to feed it:

1. **The agent runs inside the repo** (Claude Code / Codex / Hermes): do nothing — the repo-root `AGENTS.md` routes them to `RTM-Wiki/agent/README.md` automatically;
2. **Web chat**: it can't read the repo; the block from section 2 is enough. For more, paste the whole `agent/README.md` after it.

## 4. The minimal scene skeleton

Have the agent start from this skeleton instead of writing from scratch:

```python
from real_time_manim import *

class MyScene(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window (size is force-corrected to 1920x1080)
        win.scene = self   # bind the scene to the window (required)
        sq = Square(color=BLUE).set_fill(BLUE, 0.5)
        win.play(Create(sq), run_time=1.0)   # draw the square over 1 second
        win.play(Wait(0.5))   # wait 0.5 seconds
        win.close()   # close the window (required, otherwise nothing is flushed)

fast_record_scene(MyScene, "out.mp4")# export to out.mp4 in the project directory
```

### Explanation

- The skeleton is four things: **create the window, bind the scene, play, close** — without `win.scene = self`, `play` errors immediately; without `win.close()`, the file may be empty;
- `fast_record_scene` renders offline: no window, frame-exact, a few seconds per run (see [Recording methods](03-Recording-Methods.md)).

## 5. Mistakes agents commonly make

| It wrote | What you'll see | Say this back |
| --- | --- | --- |
| `manim -qh scene.py Hello` | `command not found` | RTM has no CLI; use `fast_record_scene(Hello, "out.mp4")` |
| `from manim import *` / `import manimlib` | `RuntimeWarning` (class identities from the external copy) | Always `import real_time_manim` first |
| `import real-time-manim` | `SyntaxError` | The import name is `real_time_manim` (underscores) |
| Forgot `win.scene = self` | `RuntimeError: win.play() called before the scene was bound...` | Bind it inside `construct` |
| Forgot `win.close()` | Empty/incomplete output file | Call `win.close()` at the end |
| Bare Mobject passed to `win.play` | `TypeError: Unexpected argument ... passed to MLWindow.play()` | Wrap it in `FadeIn`/`Create`/`Write` |
| `-ql` / `--fps 30` / `-t` flags | They don't exist | Output is fixed at 1920×1080@60, one quality only |
| Invented an RTM API that doesn't exist | `AttributeError` | Have it read the matching `RTM-Wiki/agent/` file first, or grep the source |

## 6. Workflow: let it run the code itself

`fast_record_scene` pops no window and renders in seconds, so the "write → run → read the error → fix" loop is very fast:

1. Paste the section 2 block + your request (an agent that can read the repo should read `AGENTS.md` first);
2. Let it run `python xxx.py` itself (Claude Code / Codex can execute commands);
3. If it fails, paste the traceback back verbatim — it can read it, and the entries in `gotchas.md` will match;
4. A web chat can't run code: you run it and paste the traceback back — same effect.

---

See also: [Installation](01-Installation.md) · [Quickstart](02-Quickstart.md) · [Recording methods](03-Recording-Methods.md) · [ManimCE users' guide](04-ManimCE-Users-Guide.md)
