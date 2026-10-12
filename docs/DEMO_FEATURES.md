# Manim-Vulkan Demo Scenes — Feature Reference

All 77 demo scenes in `scenes/demo_scene.py`, listing every animation, the parameters used in each demo, and which demo uses them.

---

## 1. Create

**Draws a shape by tracing its outline.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `mobject` | Mobject | Shape to draw |
| `run_time` | float | Duration |
| `lag_ratio` | float | Stagger delay between submobjects |

| Demo | Usage |
|------|-------|
| `DemoCreate` | `Create(sq)`, `Create(circ)`, `Create(tri)`, `run_time=2.0` |
| `DemoVGroup` | `Create(squares, run_time=2.0, lag_ratio=0.3)` |
| `DemoAllShapes` | `Create(sq)`, `Create(rect)`, `Create(circ)`, `Create(tri)`, `Create(line)`, `Create(arrow)`, `Create(dash)`, `run_time=2.5` |
| `DemoCreateSquare` | `Create(sq)` (default) |
| `DemoUncreate` | `Create(sq, run_time=1.0)` |
| `DemoDefaultAdd` | `Create(rect, run_time=3.0)` (inside AnimationGroup) |

---

## 2. Uncreate

**Reverse of Create — erases by untracing the outline.**

| Demo | Usage |
|------|-------|
| `DemoUncreate` | `Uncreate(sq, run_time=1.5)` |

---

## 3. Write

**Draws text by simulating handwriting.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `mobject` | Text | Text to write |
| `run_time` | float | Duration |
| `reverse` | bool | If True, erases instead |
| `remover` | bool | If True, removes after animation |

| Demo | Usage |
|------|-------|
| `DemoWriteUnwrite` | `Write(t1, run_time=2.0)`, `Write(t2, run_time=1.5)` |
| `DemoTextFeatures` | `Write(Text("Hello World", font_size=60))`, `Write(Text("Bold Text", font_size=48, weight=BOLD))` |
| `DemoShowWrite` | `Write(text)` (font_size=144) |
| `DemoShowWriteReversed` | `Write(text, reverse=True, remover=False)` |
| `DemoTransformMatchingShapes` | `Write(src, run_time=1.5)` |
| `_title` helper | `Write(Text(text, font_size=32).shift(UP*3.2), run_time=0.8)` |

---

## 4. Unwrite

**Erases text by reversing the Write animation.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `reverse` | bool | If True, erases from start; if False, from end |
| `run_time` | float | Duration |

| Demo | Usage |
|------|-------|
| `DemoWriteUnwrite` | `Unwrite(t1, run_time=1.5)` |
| `DemoUnwriteReverseTrue` | `Unwrite(text, reverse=True)` |
| `DemoUnwriteReverseFalse` | `Unwrite(text, reverse=False)` |

---

## 5. DrawBorderThenFill

**Draws the stroke first, then fills in the interior.**

| Demo | Usage |
|------|-------|
| `DemoDrawBorderThenFill` | `DrawBorderThenFill(sq, run_time=2.0)` |

---

## 6. ShowIncreasingSubsets

**Reveals submobjects one at a time.**

| Demo | Usage |
|------|-------|
| `DemoShowIncreasingSubsets` | `ShowIncreasingSubsets(p, run_time=2.0)` where `p = VGroup(Dot(), Square(), Triangle())` |

---

## 7. SpiralIn

**Spirals shapes into position.**

| Demo | Usage |
|------|-------|
| `DemoSpiralIn` | `SpiralIn(shapes)` where `shapes = VGroup(circle, square)` |

---

## 8. FadeIn

**Fades a mobject into view.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `mobject` | Mobject | What to fade in |
| `shift` | np.array | Direction to slide from |
| `scale` | float | Initial scale factor |
| `target_position` | np.array/str | Where to fade from |
| `fade_scale` | float | Scale at start (custom) |
| `run_time` | float | Duration |

| Demo | Usage |
|------|-------|
| `DemoFadeInFadeOut` | `FadeIn(sq)`, `FadeIn(circ)`, `FadeIn(tri)`, `run_time=1.5` |
| `DemoFadeInShift` | `FadeIn(sq, shift=UP*2)`, `FadeIn(circ, scale=2.0)`, `FadeIn(tri, target_position=sq.get_center())`, `run_time=2.0` |
| `DemoFadeInExample` | `FadeIn(w0)`, `FadeIn(w1, shift=DOWN)`, `FadeIn(w2, target_position=dot)`, `FadeIn(w3, scale=1.5)`, wrapped in `AnimationGroup(*anims, lag_ratio=0.5)` |

---

## 9. FadeOut

**Fades a mobject out of view.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `mobject` | Mobject | What to fade out |
| `shift` | np.array | Direction to slide toward |
| `scale` | float | Final scale factor |
| `target_position` | np.array | Where to fade to |
| `run_time` | float | Duration |

| Demo | Usage |
|------|-------|
| `DemoFadeInFadeOut` | `FadeOut(sq)`, `FadeOut(circ)`, `FadeOut(tri)`, `run_time=1.5` |
| `DemoFadeInShift` | `FadeOut(sq, shift=DOWN*2)`, `FadeOut(circ, scale=0.0)`, `FadeOut(tri, shift=UP*2)`, `run_time=2.0` |
| `DemoVGroup` | `FadeOut(squares, run_time=1.5)` |
| `DemoCombined` | `FadeOut(sq)`, `FadeOut(circ)`, `run_time=1.0` |
| `DemoFadeOutExample` | `FadeOut(t0)`, `FadeOut(t1, shift=DOWN)`, `FadeOut(t2, target_position=dot)`, `FadeOut(t3, scale=0.5)`, in `AnimationGroup(*anims, lag_ratio=0.5)` |

---

## 10. FadeTransform

**Cross-fades source into target.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `mobject` | Mobject | Source (fades out) |
| `target_mobject` | Mobject | Target (fades in) |
| `stretch` | bool | Non-uniform stretch to fit |
| `dim_to_match` | int | Which dimension to match (0 or 1) |
| `run_time` | float | Duration |

| Demo | Usage |
|------|-------|
| `DemoFadeTransform` | `FadeTransform(sq, circ, run_time=2.0)` |
| `DemoDifferentFadeTransforms` | `FadeTransform(starts[0], targets[0], stretch=True)`, `FadeTransform(starts[1], targets[1], stretch=False, dim_to_match=0)`, `FadeTransform(starts[2], targets[2], stretch=False, dim_to_match=1)` |
| `DemoFadeTransformPieces` | `FadeTransform(src, target)` (default params) |

---

## 11. FadeTransformPieces

**Cross-fades each submobject individually.**

| Demo | Usage |
|------|-------|
| `DemoFadeTransformPieces` | `FadeTransformPieces(src_copy, target_copy)` where src/target are VGroups |

---

## 12. FadeToColor

**Fades mobject to a target color.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `color` | Color | Target color |

| Demo | Usage |
|------|-------|
| `DemoFadeToColor` | `FadeToColor(Text("Hello World!"), color=RED)` |

---

## 13. Transform

**Morphs source mobject into target in-place.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `mobject` | Mobject | Source |
| `target_mobject` | Mobject | Target |
| `path_arc` | float | Arc angle for interpolation path |
| `run_time` | float | Duration |

| Demo | Usage |
|------|-------|
| `DemoTransform` | `Transform(sq, circ, run_time=1.5)` |
| `DemoSuccession` | `Transform(sq, circ, run_time=1.0)`, `Transform(sq, tri, run_time=1.0)` |
| `DemoCombined` | `Transform(sq, circ, run_time=1.5)` |
| `DemoReplacementTransformOrTransform` | `Transform(transform[0], transform[1])`, `Transform(transform[1], transform[2])` (no explicit target_mobject — uses `.animate`) |
| `ClockwiseExample` | `Transform(dr, sr)` |
| `DemoTransformPathArc` | `Transform(left_c, right_c, path_arc=angle*DEGREES)` for 6 different arc angles |

---

## 14. ReplacementTransform

**Transforms source into target and replaces source with target in scene.**

| Demo | Usage |
|------|-------|
| `DemoReplacementTransform` | `ReplacementTransform(sq, tri, run_time=1.5)` |
| `DemoReplacementTransformOrTransform` | `ReplacementTransform(r_transform[0], r_transform[1])`, `ReplacementTransform(r_transform[2], texts[0])` |

---

## 15. ClockwiseTransform

**Transforms with a clockwise arc path.**

| Demo | Usage |
|------|-------|
| `ClockwiseExample` | `ClockwiseTransform(dl, sl)` |

---

## 16. CounterclockwiseTransform

**Transforms with a counterclockwise arc path.**

| Demo | Usage |
|------|-------|
| `CounterclockwiseTransform_vs_Transform` | `CounterclockwiseTransform(c_transform[0], c_transform[1])` |

---

## 17. TransformMatchingShapes

**Matches submobjects by point similarity.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path_arc` | float | Arc path for matched pieces |

| Demo | Usage |
|------|-------|
| `DemoTransformMatchingShapes` | `TransformMatchingShapes(src, tar, run_time=2.0)` |
| `DemoAnagram` | `TransformMatchingShapes(src, tar, path_arc=PI/2)` — "the morse code" to "here come dots" |

---

## 18. TransformMatchingTex

**Matches LaTeX submobjects by label.**

| Demo | Usage |
|------|-------|
| `DemoMatchingEquationParts` | `TransformMatchingTex(Group(eq1, variables), eq2)`, `TransformMatchingTex(eq2, eq3)` |

---

## 19. CyclicReplace

**Cyclically swaps positions of group members.**

| Demo | Usage |
|------|-------|
| `DemoCyclicReplace` | `CyclicReplace(*group)` where group = VGroup(Square, Circle, Triangle, Star) |

---

## 20. Rotating

**Continuously rotates a mobject.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `mobject` | Mobject | What to rotate |
| `angle` | float | Total rotation (radians) |
| `axis` | np.array | Rotation axis |
| `about_point` | np.array | Center of rotation |
| `about_edge` | np.array | Edge to rotate about |
| `run_time` | float | Duration |

| Demo | Usage |
|------|-------|
| `DemoRotating` | `Rotating(sq, run_time=3.0)` |
| `DemoRotatingAbout` | `Rotating(arrow, 180*DEGREES, about_point=arrow.get_start(), run_time=1)`, `Rotating(arrow, PI, **anim_kw)`, `Rotating(vg, PI, about_point=RIGHT)`, `Rotating(vg, PI, axis=UP, about_point=ORIGIN)`, `Rotating(vg, PI, axis=RIGHT, about_edge=UP)` |

---

## 21. Rotate

**Rotates by a fixed angle.**

| Demo | Usage |
|------|-------|
| `DemoRotating` | `Rotate(tri, angle=PI, run_time=1.5)`, `Rotate(circ, angle=PI/2, run_time=1.0)` |
| `DemoUsingRotate` | `Rotate(VGroup(top_sq, bot_sq), angle=2*PI, about_point=ORIGIN, rate_func=linear)` |
| `DemoChangeDefaultAnimation` | `Rotate(S, PI)` with defaults `run_time=2, rate_func=linear` |

---

## 22. GrowFromCenter

**Grows a shape from its center.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `point_color` | Color | Color of the center point |

| Demo | Usage |
|------|-------|
| `DemoGrowFromCenter` | `GrowFromCenter(squares[0])`, `GrowFromCenter(squares[1], point_color=RED)` |

---

## 23. GrowArrow

**Grows an Arrow from tail to tip.**

| Demo | Usage |
|------|-------|
| `DemoGrowArrow` | `GrowArrow(arrows[0])`, `GrowArrow(arrows[1], point_color=RED)` |

---

## 24. GrowFromEdge

**Grows from a specified edge.**

| Demo | Usage |
|------|-------|
| `DemoGrowFromEdge` | `GrowFromEdge(squares[0], DOWN)`, `GrowFromEdge(squares[1], RIGHT)`, `GrowFromEdge(squares[2], UR)`, `GrowFromEdge(squares[3], UP, point_color=RED)` |

---

## 25. GrowFromPoint

**Grows from an arbitrary point.**

| Demo | Usage |
|------|-------|
| `DemoGrowFromPoint` | `GrowFromPoint(squares[0], ORIGIN)`, `GrowFromPoint(squares[1], [-2, 2, 0])`, `GrowFromPoint(squares[2], [3, -2, 0], RED)`, `GrowFromPoint(squares[3], dot, dot.get_color())` |

---

## 26. SpinInFromNothing

**Spins and scales in from zero size.**

| Demo | Usage |
|------|-------|
| `DemoSpinInFromNothing` | `SpinInFromNothing(squares[0])`, `SpinInFromNothing(squares[1], angle=2*PI)`, `SpinInFromNothing(squares[2], point_color=RED)` |

---

## 27. TypeWithCursor

**Types text one character at a time with a cursor.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `time_per_char` | float | Delay between chars |

| Demo | Usage |
|------|-------|
| `DemoTypeWithCursor` | `TypeWithCursor(text, cursor, time_per_char=0.15, run_time=2.5)` |

---

## 28. UntypeWithCursor

**Deletes text one character at a time with a cursor.**

| Demo | Usage |
|------|-------|
| `DemoUntypeWithCursor` | `UntypeWithCursor(text, cursor)` (defaults) |

---

## 29. Blink

**Blinks a mobject on/off.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `blinks` | int | Number of blinks |
| `time_on` | float | Duration visible |
| `time_off` | float | Duration invisible |

| Demo | Usage |
|------|-------|
| `DemoTypeWithCursor` | `Blink(cursor, blinks=2, time_on=0.4, time_off=0.4, run_time=2.0)` |
| `DemoUntypeWithCursor` | `Blink(cursor, blinks=2)` |
| `DemoBlinking` | `Blink(text, blinks=3)` |

---

## 30. Indicate

**Highlights a mobject with a color/scale pulse.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `color` | Color | Pulse color (None = use mobject color) |

| Demo | Usage |
|------|-------|
| `DemoUsingIndicate` | `Indicate(tex)` |
| `DemoChangeDefaultAnimation` | `Indicate(S)` with default `color=None` |

---

## 31. Flash

**Rays flash outward from a point.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `line_length` | float | Length of flash lines |
| `num_lines` | int | Number of lines |
| `color` | Color | Line color |
| `flash_radius` | float | Radius of flash |
| `time_width` | float | How long flash persists |
| `rate_func` | callable | Timing function |

| Demo | Usage |
|------|-------|
| `DemoUsingFlash` | `Flash(dot)` (all defaults) |
| `DemoFlashOnCircle` | `Flash(circle, line_length=1, num_lines=30, color=RED, flash_radius=radius+SMALL_BUFF, time_width=0.3, run_time=2, rate_func=rush_from)` |

---

## 32. FocusOn

**Spotlight effect on a point.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `opacity` | float | Max opacity (0..3) |

| Demo | Usage |
|------|-------|
| `DemoFocusOn` | `FocusOn(dot, run_time=1, opacity=3.0)` |

---

## 33. ShowPassingFlash

**A glowing edge that passes along a shape.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `time_width` | float | Fraction of run_time the flash is visible (0..1+) |

| Demo | Usage |
|------|-------|
| `DemoTimeWidthValues` | `ShowPassingFlash(p.copy().set_color(BLUE), run_time=2, time_width=0.2)`, `time_width=0.5`, `time_width=1`, `time_width=2` |

---

## 34. Circumscribe

**Draws a shape that highlights around a mobject.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `shape` | class | Shape class to draw (default: Rectangle) |
| `fade_out` | bool | Fades the circumscription out |
| `time_width` | float | Duration fraction of highlight |

| Demo | Usage |
|------|-------|
| `DemoCircumscribe` | `Circumscribe(lbl)` (default), `Circumscribe(lbl, Circle)`, `Circumscribe(lbl, fade_out=True)`, `Circumscribe(lbl, time_width=2)`, `Circumscribe(lbl, Circle, True)` |

---

## 35. ApplyWave

**Applies a wave distortion to a mobject.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `direction` | np.array | Wave direction |
| `time_width` | float | Width of the wave pulse |
| `amplitude` | float | Height of the wave |
| `ripples` | int | Number of wave crests |
| `rate_func` | callable | Timing function |

| Demo | Usage |
|------|-------|
| `DemoApplyingWaves` | `ApplyWave(tex)` (defaults), `ApplyWave(tex, direction=RIGHT, time_width=0.5, amplitude=0.3)`, `ApplyWave(tex, rate_func=linear, ripples=4)` |

---

## 36. Wiggle

**Wiggles/shakes a mobject.**

| Demo | Usage |
|------|-------|
| `DemoWiggle` | `Wiggle(tex)` |

---

## 37. Homotopy

**Applies a custom point-wise deformation function `f(x,y,z,t) -> (x,y,z)`.**

| Demo | Usage |
|------|-------|
| `DemoHomotopy` | `Homotopy(homotopy, square, rate_func=linear, run_time=2)` with custom sin-wave function |

---

## 38. MoveAlongPath

**Moves a mobject along a path.**

| Demo | Usage |
|------|-------|
| `DemoMoveAlongPath` | `MoveAlongPath(d1, l1), rate_func=linear` |

---

## 39. Broadcast

**Expanding ring effect.**

| Demo | Usage |
|------|-------|
| `BroadcastExample` | `Broadcast(mob)` where mob = Circle(radius=4, color=TEAL_A) |

---

## 40. Succession

**Chains animations to play one after another.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `rate_func` | callable | Timing function for transitions |

| Demo | Usage |
|------|-------|
| `DemoSuccession` | `Succession(Transform(sq, circ), Transform(sq, tri))` |
| `DemoDefaultAdd` | `Succession(Wait(1.0), Add(text_1), Wait(1.0), Add(text_2, text_3))` |
| `DemoAddWithRunTime` | `Succession(*[Add(circle, run_time=0.2) for circle in circles], rate_func=smooth)` |
| `DemoSuccessionDots` | `Succession(dot1.animate.move_to(dot2), dot2.animate.move_to(dot3), ...)` |

---

## 41. AnimationGroup

**Plays multiple animations in parallel.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `lag_ratio` | float | Stagger between sub-animations |

| Demo | Usage |
|------|-------|
| `DemoLagRatios` | `AnimationGroup(*[grp.animate(lag_ratio=ratio, run_time=1.5).shift(DOWN*2) for grp, ratio in zip(groups, ratios)])` |
| `DemoFadeInExample` | `AnimationGroup(*anims, lag_ratio=0.5)` |
| `DemoFadeOutExample` | `AnimationGroup(*anims, lag_ratio=0.5)` |
| `SpeedModifierExample` | `AnimationGroup(a.animate(...).shift(...), b.animate(...).shift(...))` |

---

## 42. LaggedStart

**Staggered-start version of AnimationGroup.**

| Demo | Usage |
|------|-------|
| `DemoLaggedStart` | `LaggedStart(dot1.animate.shift(RIGHT*4), dot2.animate.shift(RIGHT*4), dot3.animate.shift(RIGHT*4), lag_ratio=0.25, run_time=4)` |

---

## 43. LaggedStartMap

**Maps an animation factory over submobjects with lag.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `anim_class` | class | Animation class to apply |
| `mob` | Mobject | Target mobject |
| `lambda_fn` | callable | Returns (method, args) for each sub |
| `lag_ratio` | float | Stagger delay |
| `rate_func` | callable | Timing function |

| Demo | Usage |
|------|-------|
| `DemoLaggedStartMap` | `LaggedStartMap(ApplyMethod, mob, lambda m: (m.set_color, YELLOW), lag_ratio=0.1, rate_func=there_and_back, run_time=2)` |

---

## 44. Add

**Instantly adds mobject(s) to the scene (no animation).**

| Demo | Usage |
|------|-------|
| `DemoTransform` | `Add(sq), Add(circ), run_time=0.5` |
| `DemoFadeTransform` | `Add(sq), Add(circ), run_time=0.5` |
| `DemoReplacementTransform` | `Add(sq), run_time=0.5` |
| `DemoDefaultAdd` | `Add(text_1)`, `Add(text_2, text_3)` inside Succession |
| `DemoAddWithRunTime` | `Add(circle, run_time=0.2)` inside Succession |
| `DemoTransformMatchingShapes` | `Add(tar), run_time=0.5` |
| `DemoCombined` | `Add(sq), Add(circ)` |
| `DemoRotating` | `Add(sq), Add(tri), Add(circ), run_time=0.5` |

---

## 45. ChangeSpeed

**Modifies the speed profile of an animation.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `speedinfo` | dict | `{progress: speed_multiplier}` |
| `rate_func` | callable | Base timing function |
| `affects_speed_updaters` | bool | Also affects updater-driven motions |

| Demo | Usage |
|------|-------|
| `SpeedModifierExample` | `ChangeSpeed(AnimationGroup(...), speedinfo={0.3:1, 0.4:0.1, 0.6:0.1, 1:1}, rate_func=linear)` |
| `SpeedModifierUpdaterExample` | `ChangeSpeed(Wait(2), speedinfo={0.4:1, 0.5:0.2, 0.8:0.2, 1:1}, affects_speed_updaters=True)` |
| `SpeedModifierUpdaterExample2` | `ChangeSpeed(Wait(), speedinfo={1:0}, affects_speed_updaters=True)` |

---

## 46. ApplyMatrix

**Applies a 2x2 matrix transformation to points.**

| Demo | Usage |
|------|-------|
| `ApplyMatrixExample` | `ApplyMatrix([[1,1],[0,2/3]], Text("Hello World!"))`, `ApplyMatrix(matrix, NumberPlane())` |

---

## 47. ApplyPointwiseFunction

**Applies a custom point-wise function `f(point) -> point`.**

| Demo | Usage |
|------|-------|
| `WarpSquare` | `ApplyPointwiseFunction(lambda point: complex_to_R3(np.exp(R3_to_complex(point))), square)` |

---

## 48. ChangeDecimalToValue

**Animates a number to a target value.**

| Demo | Usage |
|------|-------|
| `DemoChangeDecimalToValue` | `ChangeDecimalToValue(number, 10, run_time=3)` where number = TextDecimalNumber(0, font_size=48) |

---

## 49. ChangingDecimal

**Animates a number via a lambda function `f(alpha) -> value`.**

| Demo | Usage |
|------|-------|
| `DemoChangingDecimal` | `ChangingDecimal(number, lambda a: 5*a, run_time=3)` |

---

## 50. Restore

**Restores a mobject to its last saved state.**

| Demo | Usage |
|------|-------|
| `DemoRestore` | `s.save_state()`, then `Restore(s), run_time=2` after modify with `.set_color(PURPLE).set_opacity(0.5).shift(2*LEFT).scale(3)` |

---

## 51. ScaleInPlace

**Scales a mobject by a factor in place.**

| Demo | Usage |
|------|-------|
| `DemoScaleInPlace` | `ScaleInPlace(t, 2)` |

---

## 52. ShrinkToCenter

**Shrinks a mobject to its center.**

| Demo | Usage |
|------|-------|
| `DemoShrinkToCenter` | `ShrinkToCenter(t)` |

---

## 53. TracedPath

**Draws the path traced by a point.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dissipating_time` | float | Time for trace to fade |
| `stroke_opacity` | list | Opacity range [start, end] |

| Demo | Usage |
|------|-------|
| `DemoTracedPath` | `TracedPath(circ.get_start)` with updater `rolling_circle.add_updater(lambda m: m.rotate(-0.3))` |
| `DemoDissipatingPath` | `TracedPath(a.get_center, dissipating_time=0.5, stroke_opacity=[0, 1])` |

---

## 54. AnimatedBoundary

**Cycling colored border around a mobject.**

| Parameter | Type | Description |
|-----------|------|-------------|
| `colors` | list | List of colors to cycle through |
| `cycle_rate` | float | Speed of color cycling |

| Demo | Usage |
|------|-------|
| `DemoAnimatedBoundary` | `AnimatedBoundary(text, colors=[RED, GREEN, BLUE], cycle_rate=3)` |

---

## 55. Rotate.set_default / Indicate.set_default

**Sets class-wide default parameters for animations.**

| Demo | Usage |
|------|-------|
| `DemoChangeDefaultAnimation` | `Rotate.set_default(run_time=2, rate_func=rate_functions.linear)`, `Indicate.set_default(color=None)`, then resets with `set_default()` |

---

## Mobject Types Used

| Mobject | Parameters Used | Demos |
|---------|-----------------|-------|
| `Square` | `side_length`, `color`, `fill_color`, `fill_opacity` | DemoCreate, DemoTransform, DemoAllShapes, DemoCombined, DemoUsingRotate, etc. |
| `Circle` | `radius`, `color`, `fill_opacity` | DemoCreate, DemoTransform, DemoFadeTransform, DemoAllShapes, etc. |
| `Triangle` | `color`, `fill_opacity` | DemoCreate, DemoFadeInFadeOut, DemoAllShapes, etc. |
| `Rectangle` | `width`, `height`, `color`, `fill_opacity` | DemoAllShapes, DemoTimeWidthValues, DemoDifferentFadeTransforms |
| `Line` | `start`, `end`, `color` | DemoAllShapes, DemoRotatingAbout, DemoMoveAlongPath |
| `DashedLine` | `start`, `end`, `color` | DemoAllShapes, DemoLaggedStart |
| `Arrow` | `start`, `end`, `buff`, `color` | DemoAllShapes, DemoGrowArrow, DemoRotatingAbout |
| `Dot` | `point`, `radius`, `color` | DemoLagRatios, DemoTracedPath, SpeedModifierExample, etc. |
| `Text` | `text`, `font_size`, `weight` (BOLD), `color` | DemoWriteUnwrite, DemoTextFeatures, DemoShowWrite, etc. |
| `RegularPolygon` | `n`, `color`, `stroke_width` | DemoTimeWidthValues |
| `Star` | (defaults) | DemoCyclicReplace |
| `VGroup` | `.add()`, `.arrange()`, `.arrange_in_grid()` | DemoVGroup, DemoLaggedStartMap, DemoSuccessionDots, etc. |
| `VMobject` | `.set_points_smoothly()` | DemoTransformPathArc |
| `NumberPlane` | (defaults) | ApplyMatrixExample |
| `MathTex` | LaTeX strings | DemoMatchingEquationParts |
| `SurroundingRectangle` | `buff` | DemoDefaultAdd |
| `TextDecimalNumber` | `number`, `font_size`, `num_decimal_places` | DemoChangeDecimalToValue, DemoChangingDecimal, CounterclockwiseTransform |
| `AnimatedBoundary` | `colors`, `cycle_rate` | DemoAnimatedBoundary |

---

## Scene Index (1-77)

| # | Scene Class | Primary Features |
|---|-------------|-----------------|
| 1 | `DemoCreate` | Create, set_fill, set_stroke |
| 2 | `DemoWriteUnwrite` | Write, Unwrite |
| 3 | `DemoTransform` | Add, Transform |
| 4 | `DemoReplacementTransform` | Add, ReplacementTransform |
| 5 | `DemoFadeInFadeOut` | FadeIn, FadeOut |
| 6 | `DemoFadeTransform` | Add, FadeTransform |
| 7 | `DemoRotating` | Add, Rotating, Rotate |
| 8 | `DemoTransformMatchingShapes` | Write, Add, TransformMatchingShapes |
| 9 | `DemoVGroup` | VGroup, Create (lag_ratio), FadeOut |
| 10 | `DemoAllShapes` | Create (7 shape types) |
| 11 | `DemoSuccession` | Add, Succession, Transform |
| 12 | `DemoFadeInShift` | FadeIn (shift/scale/target_position), FadeOut |
| 13 | `DemoTextFeatures` | Write, Text (font_size, weight) |
| 14 | `DemoCombined` | Add, Write, Transform, FadeOut |
| 15 | `DemoDefaultAdd` | Add, Create, Succession, SurroundingRectangle |
| 16 | `DemoAddWithRunTime` | Add (run_time), Succession, rate_func=smooth |
| 17 | `DemoLagRatios` | AnimationGroup, lag_ratio, .animate |
| 18 | `DemoChangeDefaultAnimation` | set_default, Rotate, Indicate |
| 19 | `DemoAnimatedBoundary` | AnimatedBoundary |
| 20 | `DemoTracedPath` | TracedPath, VGroup, add_updater |
| 21 | `DemoDissipatingPath` | TracedPath (dissipating_time, stroke_opacity) |
| 22 | `DemoLaggedStartMap` | LaggedStartMap, ApplyMethod, there_and_back |
| 23 | `DemoLaggedStart` | LaggedStart, lag_ratio |
| 24 | `DemoSuccessionDots` | Succession, .animate.move_to |
| 25 | `DemoCreateSquare` | Create |
| 26 | `DemoDrawBorderThenFill` | DrawBorderThenFill |
| 27 | `DemoShowIncreasingSubsets` | ShowIncreasingSubsets |
| 28 | `DemoSpiralIn` | SpiralIn |
| 29 | `DemoTypeWithCursor` | TypeWithCursor, Blink |
| 30 | `DemoUntypeWithCursor` | UntypeWithCursor, Blink |
| 31 | `DemoUnwriteReverseTrue` | Write, Unwrite (reverse=True) |
| 32 | `DemoUnwriteReverseFalse` | Write, Unwrite (reverse=False) |
| 33 | `DemoUncreate` | Create, Uncreate |
| 34 | `DemoShowWrite` | Write (font_size=144) |
| 35 | `DemoShowWriteReversed` | Write (reverse=True, remover=False) |
| 36 | `DemoFadeInExample` | FadeIn (shift, target_position, scale), AnimationGroup |
| 37 | `DemoFadeOutExample` | FadeOut (shift, target_position, scale), AnimationGroup |
| 38 | `DemoGrowFromCenter` | GrowFromCenter, point_color |
| 39 | `DemoGrowArrow` | GrowArrow, point_color |
| 40 | `DemoGrowFromEdge` | GrowFromEdge (DOWN, RIGHT, UR, UP) |
| 41 | `DemoGrowFromPoint` | GrowFromPoint (ORIGIN, array, dot) |
| 42 | `DemoSpinInFromNothing` | SpinInFromNothing (angle, point_color) |
| 43 | `DemoApplyingWaves` | ApplyWave (direction, time_width, amplitude, ripples) |
| 44 | `DemoBlinking` | Blink (blinks) |
| 45 | `DemoCircumscribe` | Circumscribe (Circle, fade_out, time_width) |
| 46 | `DemoUsingIndicate` | Indicate |
| 47 | `DemoUsingFlash` | Flash (defaults) |
| 48 | `DemoFlashOnCircle` | Flash (line_length, num_lines, color, flash_radius, time_width, rate_func) |
| 49 | `DemoFocusOn` | FocusOn (opacity) |
| 50 | `DemoTimeWidthValues` | ShowPassingFlash (time_width: 0.2, 0.5, 1, 2) |
| 51 | `DemoHomotopy` | Homotopy (custom function, rate_func=linear) |
| 52 | `DemoMoveAlongPath` | MoveAlongPath, add_updater |
| 53 | `DemoWiggle` | Wiggle |
| 54 | `DemoChangeDecimalToValue` | ChangeDecimalToValue, TextDecimalNumber |
| 55 | `DemoUsingRotate` | Rotate (angle, about_point, rate_func=linear) |
| 56 | `DemoRotatingAbout` | Rotating (about_point, axis, about_edge) |
| 57 | `DemoChangingDecimal` | ChangingDecimal (lambda) |
| 58 | `BroadcastExample` | Broadcast |
| 59 | `SpeedModifierExample` | ChangeSpeed (speedinfo, rate_func=linear) |
| 60 | `SpeedModifierUpdaterExample` | ChangeSpeed (affects_speed_updaters=True), add_updater |
| 61 | `SpeedModifierUpdaterExample2` | ChangeSpeed (pause updater with speedinfo={1:0}) |
| 62 | `ApplyMatrixExample` | ApplyMatrix (2x2 matrix) |
| 63 | `WarpSquare` | ApplyPointwiseFunction (complex exp warp) |
| 64 | `ClockwiseExample` | ClockwiseTransform, Transform |
| 65 | `CounterclockwiseTransform_vs_Transform` | CounterclockwiseTransform, _ManimTransform |
| 66 | `DemoCyclicReplace` | CyclicReplace |
| 67 | `DemoFadeToColor` | FadeToColor (color) |
| 68 | `DemoDifferentFadeTransforms` | FadeTransform (stretch, dim_to_match) |
| 69 | `DemoFadeTransformPieces` | FadeTransformPieces, FadeTransform |
| 70 | `DemoMoveToTarget` | generate_target, MoveToTarget |
| 71 | `DemoReplacementTransformOrTransform` | ReplacementTransform, Transform |
| 72 | `DemoRestore` | save_state, Restore, .animate |
| 73 | `DemoScaleInPlace` | ScaleInPlace |
| 74 | `DemoShrinkToCenter` | ShrinkToCenter |
| 75 | `DemoTransformPathArc` | Transform (path_arc), path_along_arc |
| 76 | `DemoAnagram` | TransformMatchingShapes (path_arc=PI/2) |
| 77 | `DemoMatchingEquationParts` | TransformMatchingTex, MathTex |

---

## Rate Functions Used

| Rate Function | Where Used |
|---------------|------------|
| `smooth` | DemoAddWithRunTime |
| `linear` | DemoUsingRotate, DemoHomotopy, DemoMoveAlongPath, SpeedModifierExample |
| `there_and_back` | DemoLaggedStartMap |
| `rush_from` | DemoFlashOnCircle |
| `rate_functions.linear` | DemoChangeDefaultAnimation |

---

## Mobject Methods Used

| Method | Purpose | Demos |
|--------|---------|-------|
| `.set_fill(color, opacity)` | Set fill color/opacity | Most shape demos |
| `.set_stroke(width)` | Set stroke width | Most shape demos |
| `.shift(direction)` | Move by vector | All demos |
| `.scale(factor)` | Resize | DemoCreate, DemoRotating, etc. |
| `.rotate(angle)` | Rotate | DemoRotating |
| `.get_center()` | Get center point | DemoFadeInShift, DemoFocusOn, etc. |
| `.get_start()` | Get start point | DemoTracedPath |
| `.copy()` | Clone | DemoTimeWidthValues, DemoFadeTransformPieces |
| `.next_to()` | Position relative to | DemoLaggedStart |
| `.to_edge()` / `.to_corner()` | Edge positioning | DemoLaggedStartMap, DemoTypeWithCursor |
| `.arrange()` / `.arrange_submobjects()` | Layout | DemoVGroup, DemoLagRatios, etc. |
| `.arrange_in_grid()` | Grid layout | DemoLaggedStartMap, DemoAddWithRunTime |
| `.add()` | Add submobjects | DemoVGroup, DemoLaggedStartMap |
| `.save_state()` | Snapshot for Restore | DemoRestore |
| `.generate_target()` | Create target for MoveToTarget | DemoMoveToTarget |
| `.add_updater()` | Per-frame callback | DemoTracedPath, DemoMoveAlongPath, SpeedModifier |
| `.animate.method()` | Animated method call | DemoLagRatios, DemoSuccessionDots, DemoRestore |
| `.set_color()` | Change color | DemoLaggedStartMap, DemoTimeWidthValues |
| `.put_start_and_end_on()` | Update line endpoints | DemoMoveAlongPath |
