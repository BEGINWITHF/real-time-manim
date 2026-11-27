# runbook — prompt → finished MP4

> scope: the exact sequence used to make a 38.8 s, 2,328-frame RTM short that a person will actually watch — including how to review with that person (stills before renders, §0.5 and §12). Follow it top to bottom; every decision is already made. If a step needs a judgement call, the number to use is written next to it.
> src: this file + `filmcraft.md` (why the numbers are what they are). If you read one agent page, read this one.
> **Rule 0:** do not write `construct()` until §0 is filled in. Code written before the storyboard is the reason agent films look like screensavers.

---

## §0. Fifteen-minute preflight (do not skip)

### 0.1 One sentence

Write, in the file docstring, one sentence of the form:

> “After watching, the viewer understands **\_\_\_\_\_**.”

If the sentence needs “and”, you have two films. Pick one.

### 0.2 Pick a shape

| shape | when to use | acts | total |
| --- | --- | --- | --- |
| **A. one object** | one idea, one visual (a set, a curve, a formula, a number) | title → object appears → caption names it → formula/annotation → takeaway | 10–16 s |
| **B. before → after** | a transform, an algorithm, a comparison | title → before + caption → transform → after + caption → takeaway | 18–28 s |
| **C. build-up** | a 2D idea lifted into 3D/4D (the reference film) | title/hero → 3D reveal → second structure → slice/end card | 30–45 s |

Most requests are **A** or **B**. Shape **C** needs `MeshBatch`; copy the reference film (§4.4), do not invent a mesh pipeline.

### 0.3 Fill the storyboard table

Copy this into the file docstring and fill every cell **before coding**. Empty caption = no shot.

| # | time | what the viewer sees | caption (≤ 72 chars) | camera |
| --- | --- | --- | --- | --- |
| 1 | 0.0–0.8 | title + subtitle | — | static |
| 2 | 0.7–2.5 | hero object appears, opacity fade (no scaling) | names the object | static |
| 3 | 2.5–9.5 | object holds, one annotation grows in | the one sentence that explains it | slow push ≤ 15 %, ease-in-out |
| 4 | 5.5–9.4 | formula or second structure appears, then leaves with the subject | the consequence | static |
| 5 | 9.2–11.8 | object leaves, takeaway | — (takeaway line is the visual) | static |

The reference film's actual sheet (use these numbers as the default if unsure):

| # | time | visual | caption |
| --- | --- | --- | --- |
| 1 | 0.0–2.0 | title (0–0.8), then the escape-time Mandelbrot image fades in (0.8–2.0) | “c ∈ ℂ — keep the orbit of 0 bounded” (4.0–8.7) |
| 2 | 8.0–9.9 | image fades, warm-white outline remains | (quaternion formula, centred) |
| 3 | 14.0–19.6 | camera tilts (14–19), lathe sweeps out the 3D solid | “squaring commutes with rotations of (i, j, k)” (15.2–25.0) |
| 4 | 21–31 | hyperplane `w` slices the solid; slider on the right | “cut the 4D solid: the thin filaments go first” |
| 5 | 31.0–38.2 | object shifts right, end card fades in, fade out | “one Mandelbrot, spun through four dimensions” |

### 0.4 Budget

- 3–6 shots, 4–16 s each, 10–45 s total. Under 8 s is a GIF, over 45 s needs narration.
- Camera moves are 2–8 s and may repeat (3b1b: sustained slow pushes); zoom ≤ 15 % per move, ≤ 40 % over the film.
- ≤ 3 accent colours per frame, all from the 7-colour palette; everything else greyscale.

---

## §0.5 Working with a person (read before your first edit)

The expensive mistake is not a slow render; it is rendering the **wrong direction** for two minutes and then again after every note. Move the review loop onto stills, and only commit to video once a person has approved what they see.

### 0.5.1 Four questions, one message, each with a default

Ask these together, before code. If the person says “whatever”, take the default and say which you took.

| question | default if unanswered |
| --- | --- |
| Length and platform? | 20–40 s, 16:9, 1920×1080 (RTM has no other size) |
| Language of on-screen text? | the language they wrote to you in |
| Captions only, or also narration/music? | captions only (RTM has no TTS; audio must be supplied) |
| The one thing it must explain? | the sentence from their prompt, restated |

### 0.5.2 Three gates — never skip one

| gate | artifact | cost here | what the person decides |
| --- | --- | --- | --- |
| **1. Look** | 5–8 stills, or one `contact_sheet` | one scene build (~10 s) + ~10 ms/frame | palette, composition, text, whether the shot list reads |
| **2. Motion** | `FramePreview` (scrub window + progress bar) | scene build only | timing, easing, reveal order |
| **3. Film** | `fast_record_scene(..., jobs=4)` | ~2–3 s per second of film (38.8 s → 118 s) | receives the MP4 |

Rules:

- **A still costs seconds; a render costs minutes.** After any visual change, regenerate stills — do not re-render the MP4 to check a colour.
- **Do not send an MP4 to answer a still question.** If the question is “does this frame look right”, send the frame.
- **If the question is motion, use `FramePreview`, not a video.** The person can scrub to the exact beat; a 40 s MP4 makes them hunt for it.
- **State the cost of the next step.** “Stills are ready; on your OK I record 38.8 s, about 2 minutes.”
- **Review your own stills before sending them.** If you would not ship the frame, do not put it in front of the person.

### 0.5.3 Taste is a choice between two pictures, not an open question

- Never ask “what style do you want?”. Render the same key frame twice (accent A vs accent B, tight vs wide, caption short vs long) and ask **“A or B?”** with both paths.
- One axis per round: colour, composition, pacing, text. Do not change all four at once — the person cannot tell what they are reacting to.
- If the answer is “ugly”, ask **which axis** and show the still that is wrong. Do not re-render blindly.
- If the person is unsure, take the house default (this runbook) and say so; do not stall.

### 0.5.4 Iteration loop (the cheap one)

```
edit → 5 stills (or contact_sheet) → compare with the approved set → one-line note to the person
     → only when the look is approved: FramePreview for motion → only after that: record
```

A colour change, a caption rewrite or a camera nudge costs one still (~10 s). Reserve the MP4 for delivery, not for review.

---

## §1. Copy the scaffold

This is a complete, tested 12 s film (shape **A**). Copy it to `my_film.py`, run §7, then replace the four marked things.

```python
#!/usr/bin/env python3
"""<one sentence: what the viewer understands>."""
from __future__ import annotations

import argparse
import os

import numpy as np

import real_time_manim  # noqa: F401  (must come before any `manim` import)
from real_time_manim import (
    DEGREES, DOWN, UP, Animation, Circle, MathTex, Text,
    ThreeDScene, VMobject, linear,
)
from real_time_manim.record import fast_record_scene
from real_time_manim.vulkan_bind import MLWindow

# ---- look (house defaults; do not improvise on the first pass) ------------
BG, INK, DIM, BLUE1, YELLOW = "#000000", "#FFFAFB", "#828481", "#17B6CF", "#FFF000"
SERIF = "CMU Serif"          # this Mac: "Times New Roman"
TITLE, SUB, CAP, EQ, END = 72, 40, 36, 48, 48   # px at 1080p
DURATION = 12.0


def smoothstep(a):
    a = np.clip(a, 0.0, 1.0)
    return a * a * (3.0 - 2.0 * a)


def ramp(t, t0, t1):
    """0 before t0, 1 after t1, smooth in between."""
    return float(smoothstep((t - t0) / max(t1 - t0, 1e-9)))


class Story(Animation):
    """Every visible value is a function of absolute time t."""

    def __init__(self, camera, hud, subject, run_time=DURATION):
        super().__init__(VMobject(), run_time=run_time, rate_func=linear)
        self.camera, self.hud, self.subject = camera, hud, subject
        self.dur = run_time

    def state(self, t):
        self.hud["title"].set_opacity(ramp(t, 0.0, 0.7))
        self.hud["sub"].set_opacity(ramp(t, 0.2, 0.9))
        self.hud["cap"].set_opacity(ramp(t, 1.7, 2.5) * (1.0 - ramp(t, 7.4, 8.0)))
        self.hud["eq"].set_opacity(ramp(t, 5.5, 6.5) * (1.0 - ramp(t, 8.8, 9.4)))
        self.hud["end"].set_opacity(ramp(t, 9.2, 10.2) * (1.0 - ramp(t, 11.4, 11.8)))

        # subject: fade in (opacity only — no scale-in), leave before the end card
        a = ramp(t, 0.7, 1.7) * (1.0 - ramp(t, 8.8, 9.4))
        self.subject.set_fill(BLUE1, 0.6 * a)
        self.subject.set_stroke(BLUE1, 3.0, opacity=a)
        self.subject.set(width=3.2)              # absolute, never incremental

        self.camera.set_phi(0.0)                 # 2D: head-on
        self.camera.set_theta(-90.0 * DEGREES)
        self.camera.set_zoom(1.0 + 0.08 * ramp(t, 3.5, 9.5))

    def interpolate_mobject(self, alpha):
        self.state(alpha * self.dur)


class TemplateFilm(ThreeDScene):
    def construct(self):
        win = MLWindow(1920, 1080)
        win.scene = self
        self.camera.background_color = BG
        self.set_camera_orientation(phi=0.0, theta=-90.0 * DEGREES, zoom=1.0)

        # TODO 1: the subject (Circle here)
        subject = Circle(radius=1.0, color=BLUE1)
        subject.set_fill(BLUE1, 0.6)
        subject.set_stroke(BLUE1, 3.0)
        subject.move_to(UP * 0.35)

        # TODO 2-4: title / subtitle / caption / formula / takeaway
        title = Text("The one-line title", font=SERIF, font_size=TITLE, color=INK)
        title.move_to([0.0, 1.8, 0.0])
        sub = Text("a subtitle that frames the idea", font=SERIF,
                   font_size=SUB, color=DIM)
        sub.next_to(title, DOWN, buff=0.12)
        cap = Text("one caption line, at most 72 characters", font=SERIF,
                   font_size=CAP, color=DIM)
        cap.move_to([0.0, -2.6, 0.0])
        eq = MathTex(r"e^{i\pi} + 1 = 0", font_size=EQ, color=BLUE1)
        eq.move_to([0.0, -3.0, 0.0])
        end = Text("the takeaway, in one sentence", font=SERIF,
                   font_size=END, color=INK)
        end.move_to(UP * 0.2)

        for m in (title, sub, cap, eq, end):
            m.set_opacity(0.0)

        self.add(subject)
        # text is a scene element (no corner HUD) — added AFTER the subject
        # so it paints above it
        for m in (title, sub, cap, eq, end):
            self.add(m)
        hud = {"title": title, "sub": sub, "cap": cap, "eq": eq, "end": end}
        win.play(Story(self.camera, hud, subject), run_time=DURATION)
        win.close()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/film.mp4")
    ap.add_argument("--jobs", type=int, default=None)
    ap.add_argument("--still", default=None,
                    help="comma separated seconds; write PNGs instead")
    args = ap.parse_args(argv)

    if args.still:
        from real_time_manim import FrameServer
        os.makedirs("frames", exist_ok=True)
        fs = FrameServer(TemplateFilm)
        try:
            for t in [float(x) for x in args.still.split(",") if x.strip()]:
                fs.save_frame(t, "frames/tmpl_%05.2f.png" % t)
        finally:
            fs.close()
        return 0

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    res = fast_record_scene(TemplateFilm, args.out, overwrite=True, jobs=args.jobs)
    print(res["files"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Change exactly four things:** the docstring sentence, `subject`, the five texts, and the caption timings if you add a shot. Keep everything else — the positions, sizes, colours and fades are the look.

---

## §2. The four slots, with rules

### 2.1 Title (centred upper, 72 px)

- 2–5 words, sentence case, no trailing period: “The Mandelbrot set”, “Gaussian curvature”, “Where the wave goes”.
- Subtitle (40 px, `DIM`) is a noun phrase or a question, never a second title: “in four dimensions”, “a 200-year-old argument”.
- Both hold 3–5 s, then fade — they give the frame to the subject, they do not anchor it.

### 2.2 Caption (centred, 36 px)

- One line, ≤ 72 characters, complete sentence, ends with a period if it is a sentence.
- It says the **one thing** the shot shows. It is not a label (“Figure 1”) and not a paragraph.
- It lives from the shot's reveal to the next shot's reveal; never re-write it mid-shot.
- Centred, beside the subject or mid-lower frame — never on the brightest part of the subject.

### 2.3 Formula (follows the subject or centred, ≥ 48 px, `BLUE1`)

- Only if the film is about math. One line; if it needs two, use a `VGroup` of two `MathTex` lines with 0.12 spacing.
- `MathTex` routes to Typst. Verified working: `\mathbb{H}`, `\mathcal{M}`, `\frac`, `\not\to`, `\mapsto`, `\sum`, `\int`, Greek.
- If a symbol fails to compile, replace it with an ASCII equivalent; never ship a red error box.

### 2.4 Takeaway (centre, 48 px, `INK`)

- The sentence the viewer should remember; it can be the film's title restated with the answer.
- Symbolic end cards: `MathTex` 64–80 px centred, with a 28 px sub-line 0.34 below.
- The subject must be gone (or at 20 % opacity) before it appears. Two focal points = no focal point.

---

## §3. Beat sheet, exactly

| beat | in | out | duration | what changes |
| --- | --- | --- | --- | --- |
| title | 0.0 | 0.7 | 0.7 | title fades in (opacity only, no slide) |
| subtitle | 0.2 | 0.9 | 0.7 | subtitle follows by 0.2 s |
| subject in | 0.7 | 1.7 | 1.0 | opacity 0→1 (no scaling) |
| caption 1 | 1.7 | 2.5 | 0.8 | caption fades in |
| hold | 2.5 | 3.5 | 1.0 | nothing moves; let the viewer read |
| camera | 3.5 | 9.5 | 6.0 | one eased zoom ≤ 15 % (1.00→1.08) |
| annotation / formula | 5.5 | 6.5 | 1.0 | second structure fades in |
| caption out | 7.4 | 8.0 | 0.6 | caption leaves |
| subject out | 8.8 | 9.4 | 0.6 | subject + formula leave |
| takeaway | 9.2 | 10.2 | 1.0 | takeaway fades in |
| hold | 10.2 | 11.4 | 1.2 | still |
| end fade | 11.4 | 11.8 | 0.4 | everything to 0 |

Rules: reveal = 1.0–2.0 s; hold ≥ 0.8 s after every reveal; camera moves 2–8 s, several allowed, zoom ≤ 15 % per move and ≤ 40 % over the film; total = last out + 0.1.

---

## §4. The hero visual

Pick one row. Each snippet is complete; drop it in place of TODO 1.

### 4.1 A computed image (fractal, heat map, field)

```python
arr = np.zeros((900, 900, 4), dtype=np.uint8)   # RGBA, row 0 = top
# ... fill arr with colours, alpha = 255 ...
img = ImageMobject(arr)
img.scale_to_fit_width(8.0)      # 8.0 world units ≈ 1080 px at 1080p
img.move_to(ORIGIN)
self.add(img)
```

- Keep the texture ≤ ~1000 px on the long side; more does not show at 1080p.
- Make the *edges* of the array equal to the background colour (not transparent): a hard rectangle is the #1 tell. The reference film does this in `hero_image()` with a 46 px colour falloff.
- Do not fade by editing pixels per frame; `img.set_opacity(a)` is uniform-alpha and cheap.

### 4.2 A vector diagram (the default for math)

```python
obj = VGroup(
    Circle(radius=1.2, color=YELLOW).set_fill(YELLOW, 0.6),
    Line([-2, -1.6], [2, 1.6], color=INK, stroke_width=2),
    Dot([0, 0], radius=0.06, color=BLUE1),
)
obj.move_to(UP * 0.25)
```

- Strokes ≥ 2 px (RTM stroke width is in px at 1080p). At 1 px the line disappears in H.264.
- Filled regions: opacity 0.4–0.9; less disappears, more is a sticker.
- Label parts with `Text(..., font_size=24)` attached via `next_to`, in `DIM`; the main object keeps the accent.

### 4.3 A surface (`Surface`, painter-sorted)

```python
surf = Surface(lambda u, v: [2.4 * np.cos(u) * v, 2.4 * np.sin(u) * v, v],
               u_range=(0, TAU), v_range=(0, 1), resolution=(32, 8))
surf.set_fill_by_checkerboard(YELLOW, "#217AC8")
```

- `resolution=(u, v)` is the face count; 32×8 = 256 faces is plenty for one object.
- `color=` is swallowed by `Surface` — colour it after construction.
- No self-occlusion: if the shape folds through itself, use §4.4 instead.

### 4.4 A depth-tested mesh (only when the shape needs real occlusion)

Copy the house reference film's approach — a `Vase`-style lathe and one pure `Story.state()`: it builds `(K, n_az)` quad strips from a profile, shades per vertex, and writes `mesh.quads` / `mesh.colors` each frame. Sizing rule:

```
quads = N_PROFILE * N_AZ   must be <= MeshBatch.MAX_QUADS (131072)
```

The reference film uses `680 × 56 = 38,024` quads; ~10.5 ms/frame to rebuild and shade. Go bigger only if the object fills the frame.

---

## §5. 3D numbers

- Camera: `phi=0, theta=-90°` is head-on (world x right, y up). Start there, then tilt `phi` to 35–45° for a 3/4 view. `theta` orbits; keep the subject's long axis horizontal.
- Light: `L = normalize([-0.72, -0.28, 0.63])` (upper-left, off the view axis). On-axis light = flat = “why does my 3D look like a sticker”.
- Shading per vertex: `base * (0.30 + 0.90 * max(n·L, 0)^0.80) + rim * 0.15` with `rim = (1 - n·V)^4` (cyan-blue `0.09, 0.71, 0.81`); optional specular `max(n·H, 0)^32 * 0.12` (white).
- `MeshBatch` has no transparency and no post FX: bake glow into an image texture or use the rim term.
- Smooth any profile extracted from a mask with 6 passes of a 5-tap kernel, or the lathe reads as a screw thread.
- Budget check before the first render, not after: print `len(mesh.quads)`.

---

## §6. Look at it (mandatory, 2 minutes)

### 6.1 Stills

```bash
python my_film.py --still 0.5,3,6,9,11.8
```

Read all of them, in order, like a comic page. If one of these is true, fix it before recording:

| check | fail |
| --- | --- |
| title readable over the background and over the subject | any overlap where contrast drops |
| every caption ≤ 72 chars, ≤ 2 lines, ≥ 24 px, centred | smaller / longer / corner-pinned |
| subject inside the frame at every sample | any edge clipping |
| no empty frame > 0.5 s that is not a deliberate hold | black or near-black shot |
| ≤ 3 accent hues per frame, all from the 7-colour palette | more accents, or off-palette colours |
| the end card has no other focal point | subject still visible behind it |

### 6.2 Storyboard sheet (optional, one call)

If `contact_sheet` is available in your build (`from real_time_manim import contact_sheet`), one call does this:

```python
contact_sheet(MyScene, [0.5, 3, 6, 9, 11.8], "frames/sheet.png")
```

Twelve cells maximum; it prepares the scene once and each frame is ~10 ms.

### 6.3 The three-frame rule

Pick the first frame, a middle frame and the last. If they do not tell a story in order, the film does not either.

---

## §7. Record and verify (gate 3 — after gates 1 and 2)

Only run this after a person has approved the stills (§0.5.2). Recording is the one step that cannot be undone in ten seconds.

```bash
python my_film.py --jobs 4
```

- Expected wall time: roughly `2 × duration` seconds with 4 workers on a laptop (measured: 38.8 s film → 118 s, 2,328 frames). If it is 10× that, you have a per-frame Python hot loop; move the geometry into one numpy expression.
- Verify:

```bash
ffprobe -v error -show_entries format=duration -show_entries stream=width,height,r_frame_rate -of default=noprint_wrappers=1 out/film.mp4
ffmpeg -v error -ss 0.5  -i out/film.mp4 -frames:v 1 -y f_a.png
ffmpeg -v error -ss 20   -i out/film.mp4 -frames:v 1 -y f_b.png
ffmpeg -v error -sseof -1 -i out/film.mp4 -frames:v 1 -y f_c.png
```

Check `f_a/f_b/f_c` against the stills: 1920×1080, 60/1, duration within 0.1 s of the plan.

- **`--jobs 4` must match `--jobs 1`.** Render one middle frame both ways and compare. A difference means state is not a function of `t` (see §6 of `filmcraft.md`).

---

## §8. Symptom → fix (no thinking required)

| symptom | fix |
| --- | --- |
| 3D object looks flat / like a sticker | move the light off the view axis (§5); add the rim term |
| lathe surface has rings like a screw thread | smooth the profile, 4–8 passes of a 5-tap kernel |
| text invisible | it was faded with `FadeIn` while already at opacity 0 — add at 1 and use `set_opacity` yourself |
| outline/closed shape filled white | `set_opacity` sets fill too; use `set_stroke(opacity=...)` |
| first frames differ from the last / `jobs=4` differs from `jobs=1` | state is incremental; make every value `state(t)` |
| `MeshBatch` raises “MAX_QUADS” | reduce `N_PROFILE * N_AZ`; indexed limit 131,072 |
| mesh renders garbage | the batch is over the limit or the quads array shape is wrong (`(Q,4,3)`) |
| image shows a hard rectangle | fade the array's edge colour into the background (46 px) |
| image looks soft | texture under 1000 px or `scale_to_fit_width` too large; rebuild at ~1 px per output px |
| subject clipped by the frame edge | scale to ≤ 7.4 world units wide, or zoom out 5 % |
| camera move feels mechanical | linear rate; use `smoothstep`/`ramp` |
| colours muddy | more than three accents, or an accent mixed with `DIM` on a filled area |
| formula shows a red error box | unsupported Typst symbol; replace with ASCII (never ship it) |
| render takes minutes per second | Python loop per frame; vectorise (one numpy expression per frame) |
| preview/seek shows a different pose | custom animation reads current state instead of `t` |
| text is cut after H.264 | stroke/text under 2 px / 24 px; bump the size |

---

## §9. Where the answers are

| question | file |
| --- | --- |
| how did you make the 2D image, the profile, the lathe, the slice? | the house reference film — RTM ships no demos inside the package; the recipes are in `patterns.md`, the craft rules in `filmcraft.md` |
| how do I run/record/seek? | `runtime.md`, this file §7 |
| camera angles, fixed-in-frame text, scenes | `scene-camera.md` |
| `MeshBatch`, `MeshGroup`, `lit`, limits | `three-d.md` |
| text, MathTex/Typst, sizes | `text.md` |
| why these look/timing rules | `filmcraft.md` |
| error → cause → fix catalog | `gotchas.md` |
| copy-paste recipes | `patterns.md` |

The reference film is **not shipped inside the package** — RTM is a library, not a demo host. Its structure (hero image → lathe → 4D slice → end card) and craft rules are documented in `filmcraft.md`; the mesh recipes it uses are in `three-d.md` and `patterns.md`.

---

## §10. Do not ship these

Observed in real agent submissions, in order of frequency:

1. **A long film with no text.** 30 s of geometry with no title/caption/end card. If the API cannot say what it shows, the film cannot either.
2. **Default Manim blue on black.** It reads as “unfinished”. Use the house palette.
3. **Five colours.** ≤ 3 semantic colours per frame, all from the 7-colour palette.
4. **Linear camera moves.** Camera must ease (ease-in-out); several slow pushes are fine.
5. **Captions over the subject's brightest area.** Centred mid-lower, clear of the subject.
6. **A single 30 s shot.** No cuts, no beats, no holds.
7. **An empty end.** Fade to black with nothing said.
8. **A hard-coded absolute path** (`~/…/real-time-manim`) in a file meant to be shared. Import the package; do not point at your checkout.
9. **A `Surface` used for a self-occluding shape** (painter order gives wrong occlusion). Use `MeshBatch`.
10. **Shipping the first render.** The stills loop is 2 minutes; the review is the product.

---

## §11. Final checklist (copy into the PR/description)

- [ ] docstring sentence filled; storyboard table complete.
- [ ] 3–6 shots, 4–16 s each, total 10–45 s.
- [ ] title/subtitle/subject/caption/formula/takeaway in the house palette and zones.
- [ ] ≤ 3 accents per frame (7-colour palette); strokes ≥ 2 px; text ≥ 24 px.
- [ ] reveals 1.0–2.0 s; hold ≥ 0.8 s after each; camera eased, zoom ≤ 15 % per move, ≤ 40 % total.
- [ ] stills at 5+ times reviewed; contact sheet if available.
- [ ] look (gate 1) and motion (gate 2) approved by the person **before** recording.
- [ ] `--jobs 1` and `--jobs 4` agree on a middle frame.
- [ ] `MeshBatch` under `MAX_QUADS` if used; no `set_opacity`-filled outlines.
- [ ] commits authored **and** committed by the person's git identity (§12.5).
- [ ] encoded MP4: 1920×1080, 60 fps, planned duration; first/middle/last frames checked.

---

## §12. Talking to the person (delivery, feedback, honesty)

### 12.1 One message per decision

A review message has five parts, in this order. Nothing else.

```
What changed: <one line>
Look at:      <absolute path to sheet.png or preview>
Cost:         <duration / resolution / file size, or "still, ~10 s to regenerate">
Check:        <the one thing you are unsure about>
Next:         <the decision you need: A/B, or "OK to record (~2 min)">
```

- Paths, not code. The person reviews pictures, not `construct()`.
- One decision per message. If you have two questions, ask the one that blocks the next step; the other can wait.
- If the environment can reveal a file (Explorer / Finder), reveal the main artifact; otherwise give the absolute path.
- Never write “looks great” — write what you checked: “title clears the subject at 3.0 s and 9.8 s”.

### 12.2 Delivering a film

State, in this order: path, duration, resolution/fps, size, how to re-render.

```
out/film.mp4 — 38.8 s, 1920×1080 @ 60, 7.6 MB
Re-render: python my_film.py --jobs 4
```

- Keep the source script next to the output; the person will ask for a one-word change later.
- Version approved outputs (`film_v2.mp4`) instead of overwriting the file they signed off on.
- If `--jobs > 1`, say you verified a middle frame against `--jobs 1`.
- If something is still wrong, say it before they find it (“the last caption is tight on a phone; I can shorten it to 60 characters”).

### 12.3 Receiving feedback

| they say | you do |
| --- | --- |
| “ugly” | ask which axis (colour / composition / pacing / text); show the still that is wrong |
| “too slow” | shorten holds first, then the reveal; do not speed up the camera |
| “boring” | add one beat (a second structure or a caption change), not more colours |
| “make it like <film>” | copy its *structure* (shot lengths, palette count, text density) — not its content |
| “just finish it” | take the house defaults, state them, ship; do not keep asking |

### 12.4 The one rule behind all of these

**Show, don't promise.** A path to a still the person can open beats a paragraph describing what the film will look like. This is why §0.5 exists: stills are cheap, renders are not, and a person's taste is only readable from pixels.

### 12.5 Git identity — always the person's, never a bot

Every commit must be **authored and committed by the person who asked for the work**. A commit by `opencode`, `agent`, `AI`, `Claude`, or any noreply address you do not control is a bug: it breaks `git blame`, the PR's attribution, and their contribution graph.

Before the first commit:

```bash
git config --get user.name
git config --get user.email          # repo-local wins; then --global
gh auth status                       # for pushes / PRs
```

- Use exactly that identity. **Do not override it** with `git -c user.name=...` or a made-up fallback.
- If the name/e-mail is missing, empty, or ambiguous, or `gh auth status` fails or shows the wrong account: **stop and ask the person**. Do not guess, do not invent a bot identity, do not fall back to “the agent”.
- Do not change `git config` (local or global) without permission. A one-off override is still a change of attribution — treat it the same way.
- If the person explicitly asks for a bot/agent identity, use exactly the one they name and say so in the PR body.
- Only if you already committed under the wrong identity: rewrite **only branches you created for this task** (never `main`, never someone else's branch), preserving the message and author date, setting both author and committer, then force-push with `--force-with-lease`:

  ```bash
  git log --format="%h  %an <%ae>  |  %cn <%ce>  %s" -3   # verify first
  git push --force-with-lease origin <branch>
  ```

  Tell the person which old → new SHAs changed.

Verify before opening a PR:

```bash
git log --format="%h  %an <%ae>  |  %cn <%ce>  %s" origin/main..HEAD
```


