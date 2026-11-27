# filmcraft — from API to a finished short

> scope: the layer the API files do not cover: what a **watchable** RTM short looks like and how to get there. Palette, typography, HUD zones, beat timing, 3D presentation, the stills-based QA loop, and the failure modes that make a technically-correct scene read as slop. This page is craft, not API; every symbol used here is documented in the domain files (`scene-camera.md`, `three-d.md`, `text.md`, `runtime.md`).
> src: measured on a 38.8 s, 2,328-frame 4D Mandelbrot short (2D hero image → 3D lathe reveal → 4D hyperplane slicing) plus the same review applied to half a dozen agent-written scenes. Where it conflicts with the source tree, the tree wins.
> **This page is opinionated on purpose.** Treat the numbers as defaults to copy, not laws.

A scene can be pixel-exact and still fail: 33 seconds of morphing geometry with no text, a default-blue square on black, a camera that never eases, five saturated hues fighting. The API docs teach *how* to call `win.play`; this page is about *what to put in front of the play*.

**If you just need the process, use [`runbook.md`](runbook.md).** Same rules, laid out as numbered steps with a copy-paste scaffold, exact beat timings, QA thresholds and a symptom→fix table. This page is the *why* behind its numbers.

---

## 1. The contract

- **One idea per beat.** A beat is one caption plus one visual change. If a shot needs two captions to be understood, it is two shots.
- **Text carries the idea.** A 30 s film with no text is a screensaver. Even a pure-visual piece needs a title card, one running caption line, and an end card.
- **Shots are 4–16 s.** A 10–45 s short has 3–6 shots. `33 s of continuous morph` is not a shot list.
- **Every shot must be legible as a still.** If a random frame does not say what is happening, the motion is not doing the work.
- **Hold after every reveal.** Minimum 0.8 s of stillness before the next move; reveals run 1.0–2.0 s.

## 2. Look

Start from one background and a four-colour system. The defaults below are what the reference film uses at 1080p:

| role | value | use |
| --- | --- | --- |
| background | `#000000` | flat pure black, no grid, no vignette unless you author one |
| ink | `#FFFAFB` | title, the one line that must be read first |
| dim | `#828481` | subtitle, captions, secondary labels |
| accent | `#17B6CF` (cyan-blue, BLUE1) | the subject, the formula, the highlighted curve |
| second accent | `#FFF000` (yellow) | a second structure only |

Rules that survive every review:

- **≤3 semantic colours per frame**, all from the 7-colour palette (`#17B6CF`, `#217AC8`, `#FFF000`, `#329F35`, `#C26D1C`, `#EF532C`, `#FF4CDB`); everything else greyscale.
- **Gradients are rare.** Intensity is expressed with opacity/glow; when a value must be encoded (escape time, radius, `w`), sample a palette with 4–6 stops along that parameter — never across the screen.
- **Dark subjects need light edges.** A dark shape on a dark background disappears the moment the viewer's screen gamma differs. Give it a rim: a warm-white outline (`#FFFAFB`), a cyan-blue edge term (`0.09, 0.71, 0.81`), or a baked halo.
- **1 px is not a line at 1080p.** Strokes below 2 px disappear in video compression; body text below ~24 px is unreadable on a phone.
- **No raw file paths, no debug numbers, no `t=…` overlays** unless the time is the subject.

## 3. Typography and HUD zones

- **Prose**: `Text(..., font="CMU Serif", ...)` — a serif reads as "explainer", not "UI" (this Mac: Times New Roman). **Math**: `MathTex` (routed to Typst; `\mathbb`, `\mathcal`, `\not\to` all work). One mixed line of prose+math is fine if the sizes match.
- **Sizes at 1080p**: title 72, subtitle 40, caption 36–48, formula ≥ 48, minimum 24.
- **Zones** — no corner HUD (3b1b measured: text is a scene element, `self.add`, not fixed-in-frame):
  - title + subtitle: horizontally centred, upper (title block centre ≈ 1.8 world units up), 40 px margin;
  - the running caption: centred, beside the subject or mid-lower frame — never on the subject's brightest part;
  - the formula: follows the subject or centred in frame;
  - right edge (optional): sliders/legends — these stay `add_fixed_in_frame_mobjects`.
- **Captions ≤ ~72 characters.** One line, two at most. If it wraps to three, the sentence is wrong.
- **Fade, do not slide.** HUD text that slides competes with the subject; an opacity ramp reads as a change of thought. Slide is for the subject, not the labels.

## 4. Timing and motion

- Fades use `smoothstep` (or `smooth`); camera moves use `ease-in-out`; steady rotations/translations run `linear`. A move that starts and stops instantly is a cut, not a move.
- Typical durations: title 0.7–0.8 s, hero fade 1.2 s, caption 0.6–0.8 s, camera 2–8 s, subject reveal 1.0–2.0 s, end card 1.8–2.0 s. Transitions are hard cuts; a chapter end fades to black 0.5–0.8 s.
- **Camera moves are 2–8 s and may repeat** (3b1b: sustained slow pushes); zoom ≤ 15 % per move and ≤ 40 % over the film. Zoom + pan + roll simultaneously reads as a mistake unless it is a deliberate fly-through.
- **Let the geometry finish.** If a sweep takes 5 s, do not start the caption at 2 s and the camera at 2.5 s; stagger them by the reveal.
- **Everything is a function of absolute time.** See §6 — a shot script that accumulates state breaks seeking and parallel rendering.

## 5. Presenting 3D geometry

- **Choose the axis so the silhouette reads.** A surface of revolution is only recognisable from the side; the "top" view collapses it to a disc. Check the silhouette first, the shading second.
- **Camera**: in a `ThreeDScene`, `phi=0, theta=-90°` is head-on with world `x` right and `y` up. `phi` tilts the view out of the screen; `theta` orbits. A good default 3/4 view is `phi≈35–45°`, `theta` chosen so the object's long axis stays horizontal.
- **Light off the view axis.** A light parallel to the camera flattens everything. `(-0.72, -0.28, 0.63)` normalized reads as a studio key from the upper left.
- **`MeshBatch` has no material system.** With `lit=False` you shade per vertex yourself — house values: `base * (0.30 + 0.90 * max(n·L, 0)^0.80) + max(n·H, 0)^32 * 0.12 (white) + (1 − n·V)^4 * 0.15 (cyan-blue 0.09, 0.71, 0.81)`. With `lit=True` you supply normals and use `win.set_mesh_light`. Do not mix the two on the same batch.
- **Smooth the profile.** A boundary extracted at pixel resolution has pixel-scale radius wiggles; lathed, they become rings that read as a machining artifact. 6 passes of a 5-tap kernel along the profile is the difference between "turned wood" and "screw thread".
- **Respect the budget.** `MeshBatch.MAX_QUADS = 131072` (indexed). Size `N_PROFILE × N_AZ` against it before rendering; `append` raises when crossed.
- **No post FX.** No bloom, no DOF, no tone mapping. Fake glow by baking it into an `ImageMobject` texture, or with a rim term in the vertex colours.

## 6. One pure timeline

Frame-parallel recording and `FrameServer` seek by replaying the timeline at an arbitrary `t`. Anything that mutates state incrementally is only correct forward. The robust shape is **one custom `Animation` whose `interpolate_mobject(alpha)` computes every visible value from absolute time**:

```python
class Story(Animation):
    def __init__(self, camera, hud, image, run_time):
        super().__init__(VMobject(), run_time=run_time, rate_func=linear)
        self.camera, self.hud, self.image, self.run_time = camera, hud, image, run_time

    def state(self, t):
        self.image.set_opacity(ramp(t, 0.8, 2.0) * (1.0 - ramp(t, 9.0, 9.9)))
        self.camera.set_phi(np.radians(38) * ramp(t, 14.0, 19.0))
        self.hud["title"].set_opacity(ramp(t, 0.0, 0.8))

    def interpolate_mobject(self, alpha):
        self.state(alpha * self.run_time)


win.play(Story(self.camera, hud, image, run_time=38.8), run_time=38.8)
```

Two traps this avoids:

- **Seek correctness is a property of the animation, not the renderer.** A timeline is prepared by calling `begin()` — which evaluates `interpolate(0)` — for every entry, and frames at an earlier `t` replay the started entries from their own start. If `interpolate_mobject` reads or writes state that is not a pure function of `alpha`, forward playback still looks right while seeking and `jobs=N` diverge. Keep every visible value as `state(t)`.
- **`FadeIn` is a `Transform` to the mobject's current state.** Pre-fading a mobject to 0 with `set_opacity(0)` and then playing `FadeIn` fades it *to 0*. Either add it at opacity 1 and use `FadeIn`, or drive opacity yourself.
- `VMobject.set_opacity` sets **fill and stroke** opacity. For an outline that must stay unfilled, use `set_stroke(opacity=...)`, not `set_opacity`.

## 7. The QA loop (do this before recording)

1. Pick 8–12 timestamps that cover the shot list: the first frame, every boundary, the last frame.
2. Render them at full size (do not eyeball a downscaled video):
   ```python
   from real_time_manim import FrameServer
   fs = FrameServer(MyScene)
   for t in times:
       fs.save_frame(t, "frames/t%05.2f.png" % t)
   fs.close()
   ```
   `FrameServer` prepares once (~10 s for a scene with a computed image) and then each frame is ~10 ms.
3. Lay them out as one 4×3 contact sheet and read it like a comic page. Judge the **sequence**, not the frames:
   - Is the title readable against the background *and* over the image?
   - Does every shot say one thing without the next one?
   - Is the subject inside the safe area at every point (nothing clipped by the frame edge)?
   - Are there empty frames (black or near-empty) longer than 0.5 s that are not deliberate holds?
   - Does the caption ever sit on top of the brightest part of the subject?
4. Only then record the film; re-check the first/last 2 s in the encoded MP4 (text can alias differently after compression).

## 8. Failure modes (all observed in real submissions)

| symptom | cause |
| --- | --- |
| 30 s of geometry with no text | no shot list; "the math speaks for itself" |
| subject invisible for the first 8 s | scene builds before the first reveal; add a title or start earlier |
| camera glides in a straight line | linear rate on a camera move |
| surface looks like a screw thread | unsmoothed extracted profile; see §5 |
| outlines glow white from behind | `set_opacity` filled the closed path; use `set_stroke` |
| a shape vanishes at the start | `FadeIn` on a pre-zeroed mobject; see §6 |
| parallel render differs from `--jobs 1` | incremental state in a custom animation; see §6 |
| mesh disappears in the last shot | batch over `MAX_QUADS`; check the profile × azimuth product |
| five hues, none dominant | more than three accents; collapse to one accent + warm highlight |

## 9. Ship checklist

- [ ] 3–6 shots, each with a caption; total 10–45 s.
- [ ] Title, one running caption line, end card.
- [ ] ≤ 3 accents per frame (7-colour palette); text ≥ 24 px; strokes ≥ 2 px.
- [ ] Every camera move eased; no move starts before the previous reveal settles.
- [ ] Contact sheet reviewed at full size (title safe, subject framed, captions legible).
- [ ] `--jobs 1` and `--jobs 4` render identical first/middle/last frames.
- [ ] Mesh under `MAX_QUADS`; no `set_opacity`-filled outlines; custom animation state is `f(t)`.
- [ ] Encoded MP4 checked at 0.5 s / midpoint / last second.

## See also

`../zh_CN/` for the full manual; `patterns.md` for runnable recipes; `gotchas.md` for error → cause → fix; `three-d.md` for the `MeshBatch`/`MeshGroup`/`lit` API; `runtime.md` for `FrameServer`, `FramePreview`, `prepared()` and `shared_prepare()`.
