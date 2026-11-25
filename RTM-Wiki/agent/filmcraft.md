# filmcraft — from API to a finished short

> scope: the layer the API files do not cover: what a **watchable** RTM short looks like and how to get there. Palette, typography, HUD zones, beat timing, 3D presentation, the stills-based QA loop, and the failure modes that make a technically-correct scene read as slop. This page is craft, not API; every symbol used here is documented in the domain files (`scene-camera.md`, `three-d.md`, `text.md`, `runtime.md`).
> src: measured on `examples/four_d_mandelbrot.py` (a 38.8 s, 2,328-frame reference film) plus the same review applied to half a dozen agent-written scenes. Where it conflicts with the source tree, the tree wins.
> **This page is opinionated on purpose.** Treat the numbers as defaults to copy, not laws.

A scene can be pixel-exact and still fail: 33 seconds of morphing geometry with no text, a default-blue square on black, a camera that never eases, five saturated hues fighting. The API docs teach *how* to call `win.play`; this page is about *what to put in front of the play*.

---

## 1. The contract

- **One idea per beat.** A beat is one caption plus one visual change. If a shot needs two captions to be understood, it is two shots.
- **Text carries the idea.** A 30 s film with no text is a screensaver. Even a pure-visual piece needs a title card, one running caption line, and an end card.
- **Shots are 6–14 s.** A 25–45 s short has 3–5 shots. `33 s of continuous morph` is not a shot list.
- **Every shot must be legible as a still.** If a random frame does not say what is happening, the motion is not doing the work.
- **Hold after every reveal.** Minimum 0.6 s of stillness before the next move; 1.0–1.5 s is better.

## 2. Look

Start from one background and a four-colour system. The defaults below are what the reference film uses at 1080p:

| role | value | use |
| --- | --- | --- |
| background | `#070b14` | flat, no grid, no vignette unless you author one |
| ink | `#efe9dc` | title, the one line that must be read first |
| dim | `#7b93a6` | subtitle, captions, secondary labels |
| accent | `#f2c66d` (gold) | the subject, the formula, the highlighted curve |
| second accent | `#6fd6cd` (cyan) | a second structure only — never a third saturated hue |

Rules that survive every review:

- **Two accents maximum.** A third saturated hue turns a diagram into a toy.
- **Gradients run along a parameter**, not across the screen: escape time, arc length, `w`, radius. `palette(t)` with 4–6 stops, sampled per vertex/point.
- **Dark subjects need light edges.** A dark shape on a dark background disappears the moment the viewer's screen gamma differs. Give it a rim: a gold outline, a cyan edge term, or a baked halo.
- **1 px is not a line at 1080p.** Strokes below 2 px disappear in video compression; body text below ~22 px is unreadable on a phone.
- **No raw file paths, no debug numbers, no `t=…` overlays** unless the time is the subject.

## 3. Typography and HUD zones

- **Prose**: `Text(..., font="Cambria", ...)` — a serif reads as "explainer", not "UI". **Math**: `MathTex` (routed to Typst; `\mathbb`, `\mathcal`, `\not\to` all work). One mixed line of prose+math is fine if the sizes match.
- **Sizes at 1080p**: title 46, subtitle 26, caption 24–25, formula 36–40, HUD micro-label 20–22.
- **Zones** (fixed in frame, `add_fixed_in_frame_mobjects`):
  - top-left: title + subtitle, 62 px margin;
  - bottom-left: the running caption, 62 px margin, left-aligned with the title — *not* bottom-centre over the subject;
  - bottom-right: the formula or a read-only value;
  - right edge (optional): sliders/legends.
- **Captions ≤ ~72 characters.** One line, two at most. If it wraps to three, the sentence is wrong.
- **Fade, do not slide.** HUD text that slides competes with the subject; an opacity ramp reads as a change of thought. Slide is for the subject, not the labels.

## 4. Timing and motion

- Ease everything with `smoothstep` (or `smooth`); linear camera moves look mechanical. A move that starts and stops instantly is a cut, not a move.
- Typical durations: title 1.0–1.2 s, hero fade 1.2–1.5 s, caption 0.8 s, camera 3–5 s, subject reveal 1.0–1.6 s, crossfade between shots 0.8–1.2 s, end card 1.2–1.6 s.
- **One camera move at a time.** Zoom + pan + roll simultaneously reads as a mistake unless it is a deliberate fly-through.
- **Let the geometry finish.** If a sweep takes 5 s, do not start the caption at 2 s and the camera at 2.5 s; stagger them by the reveal.
- **Everything is a function of absolute time.** See §6 — a shot script that accumulates state breaks seeking and parallel rendering.

## 5. Presenting 3D geometry

- **Choose the axis so the silhouette reads.** A surface of revolution is only recognisable from the side; the "top" view collapses it to a disc. Check the silhouette first, the shading second.
- **Camera**: in a `ThreeDScene`, `phi=0, theta=-90°` is head-on with world `x` right and `y` up. `phi` tilts the view out of the screen; `theta` orbits. A good default 3/4 view is `phi≈35–45°`, `theta` chosen so the object's long axis stays horizontal.
- **Light off the view axis.** A light parallel to the camera flattens everything. `(-0.7, -0.3, 0.6)` normalized reads as a studio key from the left.
- **`MeshBatch` has no material system.** With `lit=False` you shade per vertex yourself: `base * (ambient + diffuse * max(n·L, 0)) + specular + rim`. With `lit=True` you supply normals and use `win.set_mesh_light`. Do not mix the two on the same batch.
- **Smooth the profile.** A boundary extracted at pixel resolution has pixel-scale radius wiggles; lathed, they become rings that read as a machining artifact. 4–8 passes of a 5-tap kernel along the profile is the difference between "turned wood" and "screw thread".
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
        self.image.set_opacity(ramp(t, 1.0, 2.4) * (1.0 - ramp(t, 9.0, 9.9)))
        self.camera.set_phi(np.radians(38) * ramp(t, 9.4, 12.2))
        self.hud["title"].set_opacity(ramp(t, 0.0, 1.1))

    def interpolate_mobject(self, alpha):
        self.state(alpha * self.run_time)


win.play(Story(self.camera, hud, image, run_time=38.8), run_time=38.8)
```

Two traps this avoids:

- **A custom animation's `alpha=0` is evaluated once while a timeline is prepared**, before any frame is rendered. If `interpolate_mobject` writes state that differs from the scene's initial state, that state leaks into every earlier frame. Keeping a single animation that starts at `t=0`, or making `state(t)` self-consistent for all `t`, sidesteps it.
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
| five hues, none dominant | more than two accents; collapse to one accent + warm highlight |

## 9. Ship checklist

- [ ] 3–5 shots, each with a caption; total 25–45 s.
- [ ] Title, one running caption line, end card.
- [ ] Two accents max; text ≥ 22 px; strokes ≥ 2 px.
- [ ] Every camera move eased; no move starts before the previous reveal settles.
- [ ] Contact sheet reviewed at full size (title safe, subject framed, captions legible).
- [ ] `--jobs 1` and `--jobs 4` render identical first/middle/last frames.
- [ ] Mesh under `MAX_QUADS`; no `set_opacity`-filled outlines; no leaked `alpha=0` state.
- [ ] Encoded MP4 checked at 0.5 s / midpoint / last second.

## See also

`../zh_CN/` for the full manual; `patterns.md` for runnable recipes; `gotchas.md` for error → cause → fix; `three-d.md` for the `MeshBatch`/`MeshGroup`/`lit` API; `runtime.md` for `FrameServer`, `FramePreview`, `prepared()` and `shared_prepare()`.
