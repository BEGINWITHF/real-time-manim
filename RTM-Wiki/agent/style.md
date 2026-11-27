# Style parameters (3b1b, measured)

> Canonical editable spec: `rtm_风格参数表.md` (**repo root**, Chinese) — the user edits the
> right column there and says "generate a new style from the table". This file mirrors it in
> English for agents; **on conflict, the repo-root table wins**. Values measured from
> 10 Grant Sanderson videos, 2026-11-26 (report: `~/Desktop/rtm_3b1b_style/3b1b_测量报告.md`).
> When a value changes in the table, propagate it into the scene files that instantiate it
> (`~/gallary/code/<project>/` colour/lighting blocks + inline layout) — the table is the spec,
> the scene constants are its instances.

## 1. Canvas

| Parameter | Value |
| --- | --- |
| Resolution / fps | 1920×1080 @ 60 fps (RTM hard limit) |
| Background | `#000000` pure black (`BG`; measured 7/10 videos) |
| Background RGB (grid fade) | `(0.0, 0.0, 0.0)` (`BG_RGB`) |
| Safe margin | 0.4 world units = 40 px (`MARGIN`; 3b1b text ≥0.4 from edges) |
| Aspect | 16:9, no letterbox, no frame, no vignette |
| Subject max width | 8.00 world units (3b1b subjects often 0.8–1.0 frame width; full width allowed) |
| Grid / ground | None; if unavoidable: grey `#828481`, low opacity, thin lines |

## 2. Colour

| Parameter | Value |
| --- | --- |
| Ink (main text) | `#FFFAFB` (`INK`, measured) |
| Secondary text / captions | `#828481` (`DIM`, measured) |
| Faint elements (slider track) | `#414240` (`FAINT`) |
| Accent 1 (subject/formula) | `#17B6CF` cyan-blue (`BLUE1`, measured) |
| Accent 2 (second structure) | `#FFF000` yellow (`YELLOW`, measured) |
| Highlight white (end card) | `#FFFFFF` (`WHITE`) |
| Accent budget | ≤3 semantic colours per frame, all from the 7-colour palette: cyan-blue `#17B6CF`, deep blue `#217AC8`, yellow `#FFF000`, green `#329F35`, orange `#C26D1C`, red `#EF532C`, magenta `#FF4CDB` (all measured) |
| Fill opacity | 0.4–0.9 (3b1b: high-opacity solids) |
| Gradients | Avoid; express intensity with opacity/glow |

**2D image palette (escape time, 6 stops):** `#000000 → #123A52 → #17B6CF → #217AC8 → #EF532C → #FFF000`
(`PALETTE` normalised `[.000,.000,.000] [.071,.227,.322] [.090,.714,.812] [.129,.478,.784] [.937,.325,.173] [1.000,.941,.000]`)

**3D surface palette (6 stops):** black `(0.000,0.000,0.000)` → `(0.071,0.227,0.322)` → cyan-blue
`(0.090,0.714,0.812)` → blue `(0.129,0.478,0.784)` → red `(0.937,0.325,0.173)` → yellow `(1.000,0.941,0.000)`
(`SURFACE_PALETTE`, sampled along profile position `0.06 + 0.88·frac^0.95`)

## 3. Fonts & text

| Parameter | Value |
| --- | --- |
| Body/title font | CMU Serif (serif; this Mac: Times New Roman as the stand-in) |
| Math font | Typst (`MathTex`, no LaTeX; New Computer Modern Math ≈ 3b1b's Computer Modern) |
| Numbers/readouts (slider label) | math font `w`, 30 px |
| Title size | 72 px (measured block height 60–90) |
| Subtitle size | 40 px |
| Caption size | 36–48 px (explanatory text, centred; 3b1b has no corner captions) |
| Formula size | ≥ 48 px (scales with subject) |
| End-card main line | 64–80 px (centred, `MathTex` symbolic) |
| End-card sub line | 28 px, line spacing 0.85 |
| Caption length limit | ≤ 72 chars, ≤ 2 lines |
| Minimum text size | 24 px (unreadable below after compression) |
| Minimum stroke width | 2 px (lines/outlines) |
| Weight / letter spacing | defaults |

## 4. Layout (HUD zones)

| Parameter | Value |
| --- | --- |
| Title position | horizontally centred, upper (measured y-centre 0.24–0.72 of frame height, mostly upper); 2–3 lines allowed, up to full width |
| Subtitle position | directly under title, 0.12 gap, centred |
| Caption position | no corner HUD (3b1b measured); explanatory text beside the subject or mid-lower frame, centred |
| Caption alignment | centred |
| Formula position | follows subject or centred in frame |
| End-card position | frame centre; sub line 0.34 below |
| Slider position | right `x=5.9`, vertical bar 0.07×2.4 (3b1b has no HUD; keep only when RTM needs it) |
| Slider marker | 0.52×0.055, left of the bar, gap 0.10 |
| Slider label | 0.18 above the bar |
| HUD pinning | no corner HUD — **text is a scene element** (3b1b measured); the slider stays `add_fixed_in_frame_mobjects` |
| HUD entrance | opacity fade only, no slide/move-in |
| Title/subtitle persistence | no — hold 3–5 s, then fade to give the subject the frame |

## 5. Timeline: reference film (38.8 s)

| Event | Time (s) |
| --- | --- |
| Title + subtitle fade in | 0.0 → 0.8 (centred) |
| 2D main image fade in | 0.8 → 2.0 |
| Formula fade in | 5.0 → 6.0 |
| Caption 1 fade in | 4.0 → 4.8 |
| Slow push-in (zoom 1.00 → 1.10) | 4.8 → 14.0 (ease-in-out) |
| Gold contour fade in | 8.0 → 9.2 |
| Caption 1 fade out | 8.1 → 8.7 |
| 2D image fade out | 9.0 → 9.9 |
| Camera tilt up (phi 0° → 38°) | 14.0 → 19.0 |
| Camera azimuth (theta −90° → −74°) | 14.0 → 19.0 |
| Camera zoom (1.10 → 0.88 → 0.92) | 14.0 → 18.0 → 19.0 |
| Lathe sweep reveal 0 → 1 | 14.6 → 19.6 |
| Quaternion caption fade in / out | 15.0→16.0 / 17.0→18.0 |
| "Rotation" caption fade in / out | 15.2→16.2 / 24.0→25.0 |
| Gold meridian fade out | 19.8 → 21.2 |
| 4D slice w: 0 → 0.52·Rmax → 0 | 21.0 → 31.0 (sine + 1.35 power) |
| Slice caption fade in / out | 21.4→22.2 / 30.4→31.2 |
| Slider fade in / out | 21.2→22.0 / 30.6→31.4 |
| Subject shift right 1.55 units | 31.0 → 33.4 |
| End-card main line fade in | 32.6 → 34.6 |
| End-card sub line fade in | 33.4 → 34.8 |
| Full fade-out | 36.6 → 38.2 |
| Total | 38.8 s / 2328 frames |
| Curves | fades `smoothstep`; camera `ease-in-out` |

## 6. Timeline: 12 s template (type A, one-page)

| Event | Time (s) |
| --- | --- |
| Title fade in | 0.0 → 0.7 |
| Subtitle fade in | 0.2 → 0.9 |
| Subject fade in | 0.7 → 1.7 (opacity fade only, no scaling) |
| Caption fade in | 1.7 → 2.5 |
| Hold | 2.5 → 3.5 |
| Slow push-in (zoom 1.00 → 1.08) | 3.5 → 9.5 (ease-in-out) |
| Formula fade in | 5.5 → 6.5 |
| Caption fade out | 7.4 → 8.0 |
| Subject + formula fade out | 8.8 → 9.4 |
| End card fade in | 9.2 → 10.2 (centred) |
| Hold | 10.2 → 11.4 |
| Full fade-out | 11.4 → 11.8 |
| Total | 12.0 s |

## 7. Motion & camera

| Parameter | Value |
| --- | --- |
| Easing | fades `smoothstep`; camera `ease-in-out`; steady rotation/translation `linear` |
| Reveal duration | 1.0 – 2.0 s |
| Post-reveal hold | ≥ 0.8 s |
| Camera move duration | 2 – 8 s, multiple moves allowed (3b1b: sustained slow pushes) |
| Camera zoom budget | ≤ 15 % per move; ≤ 40 % cumulative |
| Reference-film camera | `phi 0°→38°`, `theta -90°→-74°` |
| 2D main-shot camera | `phi=0, theta=-90°` (face-on; world x right, y up) |
| Transitions | hard cuts between shots; chapter ends fade to black 0.5 – 0.8 s; **no** slide/push transitions |
| Subject entrance | opacity fade only, no scale/rotate fly-in |
| Loop/breathing | optional, amplitude ≤ 8 % |

## 8. 3D material (MeshBatch)

| Parameter | Value |
| --- | --- |
| Light direction (world, normalised) | `(-0.72, -0.28, 0.63)` |
| Ambient | `0.30` (3b1b: flatter faces) |
| Diffuse | `0.90 × max(n·L, 0)^0.80` |
| Specular | `max(n·H, 0)^32 × 0.12`, colour `(1.0, 1.0, 1.0)` (matte) |
| Rim | `(1 - n·V)^4 × 0.15`, colour `(0.09, 0.71, 0.81)` (cyan-blue) |
| Surface base colour | `SURFACE_PALETTE` sampled along the profile |
| Contour line | warm white `#FFFAFB`, 2.0 px |
| Sweep meridian | cyan-blue `#17B6CF`, 2.0 px |
| Profile smoothing | 6 passes, 5-tap `[1,4,6,4,1]/16` |
| Mesh density | `N_PROFILE=680 × N_AZ=56 = 38,024 quads` (~228k vertices) |
| Mesh cap | `MeshBatch.MAX_QUADS = 131,072` (indexed path) |
| Per-frame geometry cost | ≈ 10.5 ms (38k quads rebuild + shading) |
| Transparency | none (opaque + depth test only) |
| Post (bloom/DOF) | none; glow via baked texture or fake rim |

## 9. 2D image texture

| Parameter | Value |
| --- | --- |
| Texture size | 1000 × 911 px |
| Complex-plane window | Re `[-2.06, 0.53]`, Im `±1.18` |
| Max iterations | 300 |
| Colour mapping | `t = (μ/(μ+6.5))^2.1` |
| Set interior colour | `(0.0, 0.0, 0.0)` pure black |
| Edge glow | `exp(-(300-μ)/16)`, Gaussian blur 9 px |
| Glow overlay | warm yellow ×0.30 + cyan-blue ×0.25 (warm `(1.00,0.94,0.00)`, cool `(0.09,0.71,0.81)`) |
| Far-field darkening | `smoothstep((μ-2)/12)` |
| Edge fade to background | 46 px (fade to pure black) |
| Image world size | 8.00 / 7.29 world units |

## 10. Ship thresholds (before delivery)

| Parameter | Value |
| --- | --- |
| Shots | 3 – 6 |
| Shot duration | 4 – 16 s |
| Total duration | 10 – 45 s |
| Captions | ≤ 72 chars, ≤ 2 lines, ≥ 24 px, centred |
| Accents | ≤ 3 per frame (within the 7-colour palette) |
| Dead air | no > 0.5 s unintentional still frames |
| Subject safety | never leaves the frame (≤ 7.4–8.0 world units wide) |
| Voice/music | none (add `add_sound` separately) |
| Reference stills | first / middle / last frame + 5 more time points |

## 11. Open / user-designed

| Parameter | Current answer |
| --- | --- |
| Composition rules (subject ratio, position, whitespace) | subject centred, generous whitespace (black IS whitespace), very little screen text |
| Visual metaphor (what to draw for an abstract concept) | concept → geometric intuition, the animation IS the explanation; keep A/B/C story shapes |
| Light / paper / neon presets | dark set only; a bright-field variant exists (image-processing videos): white `#FFFFFF` + ink `#101010`, same palette |
| Font fallback | CMU Serif (serif) primary + Typst; this Mac: Times New Roman |
| Multi-line titles | allowed, centred, 1–3 lines, up to full width |
| Sound / music / subtitle bars | unused (3b1b narrates; RTM has no audio track) |
| Branding (corner logo, watermark, intro) | none (3b1b videos carry no watermark) |
