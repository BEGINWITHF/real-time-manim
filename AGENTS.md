# AGENTS.md

> Guidance for AI agents (Copilot, coding assistants, bots) working in this repository.
> Dense and structured, like `RTM-Wiki/agent/` — not marketing prose.
> Canonical agent reference: [`RTM-Wiki/agent/README.md`](RTM-Wiki/agent/README.md) (read it first).
> If a fact conflicts between docs: **the source tree (`real_time_manim/`) wins**, then `RTM-Wiki/zh_CN/`, then this file.

## 1. What this project is

- **real-time-manim (RTM)**: a Vulkan-accelerated, real-time rendering backend for [ManimCE](https://www.manim.community/).
- It is **not a Manim fork** — it drives ManimCE's own `Mobject` / `Animation` model through a native Vulkan pipeline.
- Package name: `real-time-manim` (hyphens). Import name: `real_time_manim` (underscores).
- It **bundles ManimCE 0.21.0** and re-exports the whole namespace — one import gives the renderer *and* every shape/animation/colour.
- **There is no `manim` CLI.** It is a Python library: `MLWindow`, `fast_record_scene` / `record_scene`, `FrameServer`, `FramePreview`, `Timeline`.
- Key capabilities: live 1920×1080@60 window, 1.9–2.8× faster MP4 recording, O(1) frame seeking, `MathTex` routed to an in-process Typst backend (no LaTeX install needed).
- Version: read `pyproject.toml` (`project.version`); at runtime use `import real_time_manim; real_time_manim.__version__` (note: a repo-tree run can print the version of the last pip-installed copy — check `git log -1` when it matters).
- Python >= 3.11. Windows 10+ out of the box; macOS needs MoltenVK at runtime. Recording requires `ffmpeg` on `PATH`.

## 2. How to read this repository

Layered documentation. Work top-down and stop at the layer that answers your question.

| Order | Doc | What it is |
| --- | --- | --- |
| 1 | [`RTM-Wiki/agent/README.md`](RTM-Wiki/agent/README.md) | Agent-facing condensed reference: facts, hard constraints, entry points, execution modes, file map, suggested read order. **Start here.** |
| 2 | [`README.md`](README.md) | Human quick start + install + recording + caches + constraints. |
| 3 | `RTM-Wiki/agent/<domain>.md` | One dense file per domain (`runtime`, `scene-camera`, `mobject`, `animation-transform`, `animation-motion`, `geometry`, `text`, `coords-charts`, `three-d`, `graph-vector`, `utils`). Pick the file for your task via the file map in the agent README. |
| 4 | `RTM-Wiki/agent/gotchas.md` | Cross-domain pitfalls + error → cause → fix catalogue. Read before debugging anything. |
| 5 | `RTM-Wiki/agent/patterns.md` | Copy-pasteable, runnable `construct()` recipes (scene skeletons, updaters, camera moves, 3D, graphs, tables...). |
| 6 | `RTM-Wiki/zh_CN/` | Full human manual, 144 pages, one section per API with rendered sample clips. **zh_CN is the source of truth**; every agent entry carries a `see` path back to it. |
| 7 | `RTM-Wiki/en_US/` | English translation of the same manual (sample clips re-rendered in English). |
| 8 | [`real_time_manim/`](real_time_manim/) | The source. Read it for ground truth: `__init__.py` (namespace re-export), `window/` (live window + play), `record.py` (recorders), `frames.py`, `preview.py`, `timeline.py`, `vulkan_*.py` (native binding). |
| 9 | [GitHub wiki](https://github.com/Team-Axioviva/real-time-manim/wiki) | Source-level walkthrough in 9 chapters, 01 Overview → 09 Performance by Scene Type. |

Core mental model (from the agent README §5): **the data model is ManimCE** — RTM only rasterizes it. `Scene.setup()` → `construct()` → `tear_down()` are called for you; `Scene.render()` is never driven. One window per process; `win.scene = self` and `win.close()` are required.

## 3. How to use it to build videos

RTM is a library, not a CLI. A video is a `Scene` subclass whose `construct()` drives an `MLWindow`, plus a recorder call.

**Setup** (only if not installed): `pip install real-time-manim`; macOS additionally `brew install molten-vk`; any recording additionally needs `ffmpeg` on `PATH`. Math without LaTeX: `pip install "real-time-manim[typst]"`.

**The canonical scene shape** — follow it exactly:

```python
from real_time_manim import Scene, Text, Square, BLUE, YELLOW, UP
from real_time_manim.vulkan_bind import MLWindow, Create, Wait
from real_time_manim.record import fast_record_scene

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)            # size is forced to 1920x1080, prints a notice
        win.scene = self                    # REQUIRED
        win.play(Text("hi", color=YELLOW).to_edge(UP), run_time=0.5)
        win.play(Create(Square(color=BLUE).set_fill(BLUE, 0.6)), run_time=1.0)
        win.play(Wait(0.5))
        win.close()                         # REQUIRED: flushes + finishes the encoder

if __name__ == "__main__":
    r = fast_record_scene(Hello, "out.mp4", overwrite=True)
    print(r["files"])
```

Grammar: `MLWindow(...) ; win.scene = self ; (add | play)* ; win.close()`.

**Picking the entry point:**

| Goal | Call | Notes |
| --- | --- | --- |
| Offline MP4 (fastest) | `fast_record_scene(S, path)` | Hidden window, frame-exact readback |
| Visible MP4 | `fast_record_scene(S, path, hidden=False)` or `record_scene(S, path)` | `record_scene` samples wall-clock frames |
| Still frame → PNG | `FrameServer(S).save_frame(t, path)` | O(1), frame-exact |
| Seek / scrub | `FramePreview(S).run()` | Frame-exact scrub GUI |

**Rules that bite (full list: agent `README.md` §2 and `gotchas.md`):**

1. Import `real_time_manim` first — never `import manim` first (class identity splits).
2. One `play` = one parallel timeline; sequence with `Succession` / `LaggedStart`.
3. A bare `Mobject` cannot be played — wrap in `Create` / `FadeIn` / `Write` or `self.add(...)`.
4. Updaters only advance during a `play`; `Wait` is a play.
5. Output is always 1920×1080 @ 60 fps; do not fight it.
6. The module is `real_time_manim` (underscores) — fix hyphenated imports on sight.
7. After recording, verify: the returned `files` list must exist; grep the log for `[FastRecord] Saved:`.

Full scene grammar, recording options, math (`MathTex`→Typst routing, raw-string escaping), and text: `RTM-Wiki/agent/` domain files. Ready-made recipes: `RTM-Wiki/agent/patterns.md`.

## 4. How to report issues

Follow the template system in [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/): `bug_report.yml` (bugs), `feature_request.yml` (features), `documentation.yml` (docs), `suggestion.yml` (ideas), `help.yml` (usage questions). Answer the preflight checklist honestly.

**A bug report must contain a minimal, runnable reproduction** — one `Scene` (the canonical shape above) that triggers the bug, plus:

- environment: OS, Python version, package version (`pip show real-time-manim` or the pyproject version), GPU/driver, MoltenVK presence on macOS;
- the full traceback / error text, verbatim;
- expected vs actual behaviour.

For agents using `gh`: `gh issue create --template bug_report --repo Team-Axioviva/real-time-manim`. Fill `What happened?` and `Minimal reproduction` with the above; do not paste an entire project — reduce it first.

Wiki/content errors found in `RTM-Wiki/` (including `agent/`) are **not** issues — open a PR fixing the page, since the wiki lives in this repo. The maintainer accepts AI-drafted issue content with an AI disclosure.

## 5. Style and non-negotiables

- Docs and agent-facing text in **English**; keep code, identifiers, and error strings byte-identical to the source.
- Do not invent API details. If a fact is unknown, omit it or mark `TODO`.
- Repo wiki facts derive from `RTM-Wiki/zh_CN/` and the source tree; on conflict, the source tree wins.
