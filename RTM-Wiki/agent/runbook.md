# runbook — prompt → finished MP4

> scope: the exact sequence used to make a 38.8 s, 2,328-frame RTM short that a person will actually watch. Follow it top to bottom; every decision is already made. If a step needs a judgement call, the number to use is written next to it.
> src: this file + `filmcraft.md` (why the numbers are what they are) + `real_time_manim/demos/four_d_mandelbrot.py` (a complete film you can run and copy). If you read one agent page, read this one.
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
| 1 | 0.0–1.2 | title + subtitle | — | static |
| 2 | 1.2–3.4 | hero object appears, 0.8–1.2 s ease | names the object | static |
| 3 | 3.4–7.2 | object holds, one annotation grows in | the one sentence that explains it | slow push, ≤ 6 % |
| 4 | 7.2–9.6 | formula or second structure appears | the consequence | static |
| 5 | 9.6–12.0 | object leaves, takeaway | — (takeaway line is the visual) | static |

The reference film's actual sheet (use these numbers as the default if unsure):

| # | time | visual | caption |
| --- | --- | --- | --- |
| 1 | 0.0–2.4 | title, then the escape-time Mandelbrot image fades in | “c ∈ ℂ — keep the orbit of 0 bounded” |
| 2 | 8.1–9.9 | image fades, gold outline remains | (quaternion formula, bottom-left) |
| 3 | 9.4–14.6 | camera tilts, lathe sweeps out the 3D solid | “squaring commutes with rotations of (i, j, k)” |
| 4 | 21–31 | hyperplane `w` slices the solid; slider on the right | “cut the 4D solid: the thin filaments go first” |
| 5 | 32.6–38.2 | object shifts right, end card fades in, fade out | “one Mandelbrot, spun through four dimensions” |

### 0.4 Budget

- 3–5 shots, 6–14 s each, 10–45 s total. Under 8 s is a GIF, over 45 s needs narration.
- One camera move for the whole film (a slow zoom or one tilt). More than one reads as a mistake.
- One accent colour for the subject. A second accent may annotate, nothing else.

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
    DEGREES, DOWN, LEFT, UP, Animation, Circle, MathTex, Text,
    ThreeDScene, VMobject, linear,
)
from real_time_manim.record import fast_record_scene
from real_time_manim.vulkan_bind import MLWindow

# ---- look (house defaults; do not improvise on the first pass) ------------
BG, INK, DIM, GOLD, CYAN = "#070b14", "#efe9dc", "#7b93a6", "#f2c66d", "#6fd6cd"
TITLE, SUB, CAP, EQ, END = 46, 26, 25, 38, 30   # px at 1080p
MARGIN = 0.62                                   # world units = 62 px
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
        self.hud["title"].set_opacity(ramp(t, 0.0, 1.1))
        self.hud["sub"].set_opacity(ramp(t, 0.2, 1.3))
        self.hud["cap"].set_opacity(ramp(t, 2.2, 3.0) * (1.0 - ramp(t, 7.4, 8.0)))
        self.hud["eq"].set_opacity(ramp(t, 6.0, 6.8) * (1.0 - ramp(t, 8.8, 9.4)))
        self.hud["end"].set_opacity(ramp(t, 9.2, 10.2) * (1.0 - ramp(t, 11.5, 11.9)))

        # subject: fade in, breathe, leave before the end card
        a = ramp(t, 1.2, 2.2) * (1.0 - ramp(t, 8.8, 9.4))
        self.subject.set_fill(GOLD, 0.18 * a)
        self.subject.set_stroke(GOLD, 3.0, opacity=a)
        s = 0.90 + 0.10 * ramp(t, 1.2, 2.4) + 0.06 * ramp(t, 5.0, 9.0)
        self.subject.set(width=3.2 * s)          # absolute, never incremental

        self.camera.set_phi(0.0)                 # 2D: head-on
        self.camera.set_theta(-90.0 * DEGREES)
        self.camera.set_zoom(1.0 + 0.06 * ramp(t, 5.0, 9.0))

    def interpolate_mobject(self, alpha):
        self.state(alpha * self.dur)


class TemplateFilm(ThreeDScene):
    def construct(self):
        win = MLWindow(1920, 1080)
        win.scene = self
        self.camera.background_color = BG
        self.set_camera_orientation(phi=0.0, theta=-90.0 * DEGREES, zoom=1.0)

        # TODO 1: the subject (Circle here)
        subject = Circle(radius=1.0, color=GOLD)
        subject.set_fill(GOLD, 0.18)
        subject.set_stroke(GOLD, 3.0)
        subject.move_to(UP * 0.35)

        # TODO 2-4: title / subtitle / caption / formula / takeaway
        title = Text("The one-line title", font="Cambria", font_size=TITLE, color=INK)
        title.to_corner([-1, 1, 0], buff=MARGIN)
        sub = Text("a subtitle that frames the idea", font="Cambria",
                   font_size=SUB, color=DIM)
        sub.next_to(title, DOWN, buff=0.12, aligned_edge=LEFT)
        cap = Text("one caption line, at most 72 characters", font="Cambria",
                   font_size=CAP, color=DIM)
        cap.to_corner([-1, -1, 0], buff=MARGIN)
        eq = MathTex(r"e^{i\pi} + 1 = 0", font_size=EQ, color=GOLD)
        eq.to_corner([1, -1, 0], buff=MARGIN)
        end = Text("the takeaway, in one sentence", font="Cambria",
                   font_size=END, color=INK)
        end.move_to(UP * 0.2)

        for m in (title, sub, cap, eq, end):
            m.set_opacity(0.0)
            self.add_fixed_in_frame_mobjects(m)

        self.add(subject)
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

### 2.1 Title (top-left, 46 px)

- 2–5 words, sentence case, no trailing period: “The Mandelbrot set”, “Gaussian curvature”, “Where the wave goes”.
- Subtitle (26 px, `DIM`) is a noun phrase or a question, never a second title: “in four dimensions”, “a 200-year-old argument”.
- Both stay on screen for the whole film. They are the viewer's anchor.

### 2.2 Caption (bottom-left, 25 px)

- One line, ≤ 72 characters, complete sentence, ends with a period if it is a sentence.
- It says the **one thing** the shot shows. It is not a label (“Figure 1”) and not a paragraph.
- It lives from the shot's reveal to the next shot's reveal; never re-write it mid-shot.
- Never centre it under the subject, never put it on the brightest part of the subject. Bottom-left is empty by construction.

### 2.3 Formula (bottom-right, 38–40 px, `GOLD`)

- Only if the film is about math. One line; if it needs two, use a `VGroup` of two `MathTex` lines with 0.12 spacing.
- `MathTex` routes to Typst. Verified working: `\mathbb{H}`, `\mathcal{M}`, `\frac`, `\not\to`, `\mapsto`, `\sum`, `\int`, Greek.
- If a symbol fails to compile, replace it with an ASCII equivalent; never ship a red error box.

### 2.4 Takeaway (centre, 30 px, `INK`)

- The sentence the viewer should remember; it can be the film's title restated with the answer.
- The subject must be gone (or at 20 % opacity) before it appears. Two focal points = no focal point.

---

## §3. Beat sheet, exactly

| beat | in | out | duration | what changes |
| --- | --- | --- | --- | --- |
| title | 0.0 | 1.1 | 1.1 | title fades in (opacity only, no slide) |
| subtitle | 0.2 | 1.3 | 1.1 | subtitle follows by 0.2 s |
| subject in | 1.2 | 2.2 | 1.0 | opacity 0→1, scale 0.90→1.00 |
| caption 1 | 2.2 | 3.0 | 0.8 | caption fades in |
| hold | 3.0 | 5.0 | 2.0 | nothing moves; let the viewer read |
| camera | 5.0 | 9.0 | 4.0 | one eased zoom ≤ 6 % |
| annotation / formula | 6.0 | 6.8 | 0.8 | second structure fades in |
| subject out | 8.8 | 9.4 | 0.6 | subject + formula leave |
| takeaway | 9.2 | 10.2 | 1.0 | takeaway fades in |
| hold | 10.2 | 11.5 | 1.3 | still |
| end fade | 11.5 | 11.9 | 0.4 | everything to 0 |

Rules: reveal = 0.8–1.6 s; hold ≥ 0.6 s after every reveal; camera move 3–5 s and never in the first 2 s; total = last out + 0.1.

---

## §4. The hero visual

Pick one row. Each snippet is complete; drop it in place of TODO 1.

### 4.1 A computed image (fractal, heat map, field)

```python
arr = np.zeros((900, 900, 4), dtype=np.uint8)   # RGBA, row 0 = top
# ... fill arr with colours, alpha = 255 ...
img = ImageMobject(arr)
img.scale_to_fit_width(7.6)      # 7.6 world units ≈ 820 px at 1080p
img.move_to(ORIGIN)
self.add(img)
```

- Keep the texture ≤ ~1000 px on the long side; more does not show at 1080p.
- Make the *edges* of the array equal to the background colour (not transparent): a hard rectangle is the #1 tell. The reference film does this in `hero_image()` with a 46 px colour falloff.
- Do not fade by editing pixels per frame; `img.set_opacity(a)` is uniform-alpha and cheap.

### 4.2 A vector diagram (the default for math)

```python
obj = VGroup(
    Circle(radius=1.2, color=CYAN).set_fill(CYAN, 0.10),
    Line([-2, -1.6], [2, 1.6], color=INK, stroke_width=2),
    Dot([0, 0], radius=0.06, color=GOLD),
)
obj.move_to(UP * 0.25)
```

- Strokes ≥ 2 px (RTM stroke width is in px at 1080p). At 1 px the line disappears in H.264.
- Filled regions: opacity 0.08–0.20; more looks like a highlighter.
- Label parts with `Text(..., font_size=22)` attached via `next_to`, in `DIM`; the main object keeps the accent.

### 4.3 A surface (`Surface`, painter-sorted)

```python
surf = Surface(lambda u, v: [2.4 * np.cos(u) * v, 2.4 * np.sin(u) * v, v],
               u_range=(0, TAU), v_range=(0, 1), resolution=(32, 8))
surf.set_fill_by_checkerboard(CYAN, "#1d6a8c")
```

- `resolution=(u, v)` is the face count; 32×8 = 256 faces is plenty for one object.
- `color=` is swallowed by `Surface` — colour it after construction.
- No self-occlusion: if the shape folds through itself, use §4.4 instead.

### 4.4 A depth-tested mesh (only when the shape needs real occlusion)

Copy the reference film's `Vase` class and `Story.state()` (see §9 map): it builds `(K, n_az)` quad strips from a profile, shades per vertex, and writes `mesh.quads` / `mesh.colors` each frame. Sizing rule:

```
quads = N_PROFILE * N_AZ   must be <= MeshBatch.MAX_QUADS (131072)
```

The reference film uses `680 × 56 = 38,080`; ~10.5 ms/frame to rebuild and shade. Go bigger only if the object fills the frame.

---

## §5. 3D numbers

- Camera: `phi=0, theta=-90°` is head-on (world x right, y up). Start there, then tilt `phi` to 35–45° for a 3/4 view. `theta` orbits; keep the subject's long axis horizontal.
- Light: `L = normalize([-0.72, -0.28, 0.63])` (upper-left, off the view axis). On-axis light = flat = “why does my 3D look like a sticker”.
- Shading per vertex: `base * (0.20 + 0.95 * max(n·L, 0)) + rim * 0.30` with `rim = (1 - n·V)^4`; optional specular `max(n·H, 0)^38 * 0.30`.
- `MeshBatch` has no transparency and no post FX: bake glow into an image texture or use the rim term.
- Smooth any profile extracted from a mask with 4–8 passes of a 5-tap kernel, or the lathe reads as a screw thread.
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
| every caption ≤ 2 lines, ≥ 22 px | smaller / longer |
| subject inside the frame at every sample | any edge clipping |
| no empty frame > 0.5 s that is not a deliberate hold | black or near-black shot |
| one accent hue on the subject | two accents competing |
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

## §7. Record and verify

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
| colours muddy | more than two accents, or an accent mixed with `DIM` on a filled area |
| formula shows a red error box | unsupported Typst symbol; replace with ASCII (never ship it) |
| render takes minutes per second | Python loop per frame; vectorise (one numpy expression per frame) |
| preview/seek shows a different pose | custom animation reads current state instead of `t` |
| text is cut after H.264 | stroke/text under 2 px / 22 px; bump the size |

---

## §9. Where the answers are

| question | file |
| --- | --- |
| how did you make the 2D image, the profile, the lathe, the slice? | `real_time_manim/demos/four_d_mandelbrot.py` — map below |
| how do I run/record/seek? | `runtime.md`, this file §7 |
| camera angles, fixed-in-frame text, scenes | `scene-camera.md` |
| `MeshBatch`, `MeshGroup`, `lit`, limits | `three-d.md` |
| text, MathTex/Typst, sizes | `text.md` |
| why these look/timing rules | `filmcraft.md` |
| error → cause → fix catalog | `gotchas.md` |
| copy-paste recipes | `patterns.md` |

Reference film map (the numbers are line numbers in that file):

| what you want | where |
| --- | --- |
| look constants, palette, light | top of the file, `PALETTE` / `SURFACE_PALETTE` / `LIGHT` |
| easing helpers | `smoothstep()`, `ramp()` (l.124–131) |
| escape-time image + edge falloff | `mandel_field()` l.143, `hero_image()` l.164 |
| contour extraction | `boundary_loops()` l.252, `upper_arc()` l.304 |
| profile smoothing | `smooth_profile()` l.343 |
| lathe + per-vertex shading + slicing | `Vase.geometry()` l.382 |
| the whole film as one pure function | `Story.state()` l.460 |
| HUD construction and zones | `FourDMandelbrot.construct()` l.553 |
| stills / preview / render CLI | `stills()` l.699, `preview()` l.715, `render()` l.689 |

Run it: `python -m real_time_manim.demos.four_d_mandelbrot --preview`.

---

## §10. Do not ship these

Observed in real agent submissions, in order of frequency:

1. **A long film with no text.** 30 s of geometry with no title/caption/end card. If the API cannot say what it shows, the film cannot either.
2. **Default Manim blue on black.** It reads as “unfinished”. Use the house palette.
3. **Five colours.** Two accents maximum.
4. **Linear camera moves**, or three moves in the same shot.
5. **Captions over the subject's brightest area.** Bottom-left, always.
6. **A single 30 s shot.** No cuts, no beats, no holds.
7. **An empty end.** Fade to black with nothing said.
8. **A hard-coded absolute path** (`~/…/real-time-manim`) in a file meant to be shared. Import the package; do not point at your checkout.
9. **A `Surface` used for a self-occluding shape** (painter order gives wrong occlusion). Use `MeshBatch`.
10. **Shipping the first render.** The stills loop is 2 minutes; the review is the product.

---

## §11. Final checklist (copy into the PR/description)

- [ ] docstring sentence filled; storyboard table complete.
- [ ] 3–5 shots, 6–14 s each, total 10–45 s.
- [ ] title/subtitle/subject/caption/formula/takeaway in the house palette and zones.
- [ ] one accent + one secondary; strokes ≥ 2 px; text ≥ 22 px.
- [ ] every reveal ≥ 0.8 s; hold ≥ 0.6 s after each; one camera move, eased.
- [ ] stills at 5+ times reviewed; contact sheet if available.
- [ ] `--jobs 1` and `--jobs 4` agree on a middle frame.
- [ ] `MeshBatch` under `MAX_QUADS` if used; no `set_opacity`-filled outlines.
- [ ] encoded MP4: 1920×1080, 60 fps, planned duration; first/middle/last frames checked.
