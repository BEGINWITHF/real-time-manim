# real-time-manim — Feature Reference

> Every animation and capability of the Vulkan rendering backend, verified
> against the actual package and organized by category. All animations below are
> importable from `real_time_manim.vulkan_bind` and render through the engine's
> custom animation pipeline.

## Basic usage pattern

A `Scene` is just an object that holds the window and mobjects; it is not
rendered by Manim's own renderer. Open an `MLWindow`, bind the scene, play, close:

```python
from manim import Scene, Square, BLUE
from real_time_manim.vulkan_bind import MLWindow, Create, Wait

class Example(Scene):
    def construct(self):
        win = MLWindow(1280, 720)          # opens a live Vulkan window
        win.scene = self
        sq = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)
        win.play(Create(sq), run_time=1.0)
        win.play(Wait(0.5))
        win.close()
```

Code snippets below are fragments meant to live inside such a `construct()`.
`win.play(...)` accepts the same animation keyword arguments as Manim
(`run_time`, `lag_ratio`, `rate_func`, …). To render to an MP4 instead of a
window, pass the scene to `real_time_manim.record.fast_record_scene`
(or `record_scene`).

---

## Supported shapes

Mobjects are Manim objects routed to native per-type Vulkan "sender" methods.
These common shapes have dedicated senders; anything else falls back to generic
bezier/tessellation rendering.

| Manim mobject | Engine dispatch | Notes |
|---------------|-----------------|-------|
| `Square` | dedicated square sender | `side_length` |
| `Rectangle` | dedicated rectangle sender | `width`, `height` |
| `Circle` | dedicated circle sender | `radius` |
| `Ellipse` | dedicated ellipse sender | `width`, `height` |
| `Line` | dedicated line sender | two points, no fill |
| `DashedLine` | dedicated dashed-line sender | `dash_length`, `dashed_ratio` |
| `Arrow` | dedicated arrow sender | shaft + triangular tip |
| `Polygon` / `Polygram` | polygon sender | arbitrary vertex lists |
| `Triangle` | polygon sender | `Triangle` is a `Polygon` |
| `Arc` | dedicated arc sender | `start_angle`, `angle` |
| `Dot` | dedicated dot sender | small filled circle |
| `Point` | dedicated point sender | single pixel |
| `Text` | text/glyph senders | TrueType, per-character reveal |
| `MathTex` | text/glyph senders | LaTeX or Unicode |
| `VGroup` / `Group` | routed to children | container for grouped mobjects |

Fill/stroke color and opacity are set with the usual Manim API
(`set_fill`, `set_stroke`); the engine picks the right sender automatically.

---

## Drawing animations

### Create

Traces a mobject's outline to reveal it progressively. The workhorse for
building shapes into a scene.

```python
win.play(Create(sq))                      # default speed
win.play(Create(circle, run_time=2.0))    # slower
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `run_time` | `1.0` | duration in seconds |
| `lag_ratio` | `1.0` | stagger between submobjects |

### Uncreate

Reverse of `Create`: untraces the outline, removing the mobject.

```python
win.play(Uncreate(sq, run_time=1.5))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `run_time` | `1.0` | duration |
| `lag_ratio` | `1.0` | stagger |
| `remover` | `True` | remove mobject at end |

### DrawBorderThenFill

Draws the stroke first, then fills the interior.

```python
win.play(DrawBorderThenFill(sq, run_time=2.0))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `run_time` | `2.0` | duration |
| `stroke_width` | `2` | stroke width while drawing |
| `stroke_color` | `None` | stroke color override |

### ShowIncreasingSubsets

Reveals a group's submobjects one at a time, keeping earlier ones visible.

```python
group = VGroup(Dot(), Square(), Triangle())
win.play(ShowIncreasingSubsets(group, run_time=2.0))
```

### SpiralIn

Spirals shapes into position from outside the frame while fading them in.

```python
win.play(SpiralIn(VGroup(sq, circle)))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `scale_factor` | `8` | how far from center they start |
| `fade_in_fraction` | `0.3` | portion of time spent fading in |
| `run_time` | `1.0` | duration |

### Add

Adds mobjects instantly (default `run_time=0`), no drawn-in transition.

```python
win.play(Add(sq, circle))
```

### Wait

Holds the current frame.

```python
win.play(Wait(0.5))
```

---

## Fading animations

### FadeIn / FadeOut

`FadeIn` fades a mobject in; `FadeOut` fades it out. Both accept `shift`,
`target_position` and `scale` to slide and/or rescale while fading.

```python
win.play(FadeIn(sq))
win.play(FadeIn(sq, shift=UP * 2, scale=2.0))
win.play(FadeOut(sq, shift=DOWN * 2, target_position=dot))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `shift` | `None` | direction to slide from/to |
| `target_position` | `None` | position to fade from/to |
| `scale` | `1.0` | initial/final scale factor |
| `run_time` | `1.0` | duration |

### FadeTransform

Cross-fades one mobject into another, optionally stretching to fit and choosing
which dimension to match.

```python
win.play(FadeTransform(square, circle, run_time=2.0))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `stretch` | `True` | non-uniform stretch to fit target |
| `dim_to_match` | `1` | dimension to match (0 = x, 1 = y) |
| `run_time` | `1.0` | duration |

### FadeTransformPieces

Like `FadeTransform`, but cross-fades each pair of submobjects individually.

```python
win.play(FadeTransformPieces(VGroup(sq, tri), VGroup(circle, star)))
```

---

## Transform animations

### Transform

Morphs a source mobject into a target in place (the source stays in the scene and
visually becomes the target).

```python
sq = Square(); circle = Circle()
win.play(Transform(sq, circle, run_time=1.5))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `run_time` | `1.0` | duration |
| `path_arc` | `0.0` | arc angle for the interpolation path |
| `path_arc_axis` | `None` | axis for the arc |
| `replace_mobject_with_target_in_scene` | `False` | swap the mobject out at the end |

### ReplacementTransform

Transforms a source into a target and removes the source, leaving the target in
the scene.

```python
sq = Square(); triangle = Triangle()
win.play(ReplacementTransform(sq, triangle, run_time=1.5))
```

### TransformMatchingShapes

Matches submobjects by point similarity and transforms the matched pieces, giving
smooth per-letter morphs between two pieces of text or shape groups.

```python
win.play(TransformMatchingShapes(Text("the morse code"), Text("here come dots")))
```

### TransformMatchingTex

Matches `MathTex` submobjects by their LaTeX so equation terms slide into new
positions during a rewrite.

```python
win.play(TransformMatchingTex(MathTex(r"x^2 + y^2 = r^2"),
                              MathTex(r"r^2 = x^2 + y^2")))
```

---

## Movement & deformation

### MoveToTarget

Moves a mobject to its saved `.target` attribute.

```python
sq.target = Circle().shift(RIGHT * 3)
win.play(MoveToTarget(sq))
```

### MoveAlongPath

Moves a mobject along the path of another mobject (commonly a `Dot` around a
`Circle`).

```python
win.play(MoveAlongPath(dot, circle))
```

### Homotopy

Deforms a mobject with a continuous function `homotopy(x, y, z, t)` evaluated
every frame, where `t` runs 0 → 1 over the animation.

```python
def warp(x, y, z, t):
    return np.array([x + np.sin(t * PI) * y, y, z])

win.play(Homotopy(warp, sq))             # default run_time = 3.0
```

---

## Rotation animations

### Rotating

Continuously rotates a mobject over the whole animation (default: one full turn).

```python
win.play(Rotating(sq, run_time=3.0))
win.play(Rotating(arrow, PI, about_point=arrow.get_start()))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `angle` | `TAU` | total rotation in radians |
| `axis` | `None` | 3D rotation axis |
| `about_point` | `None` | center of rotation |
| `about_edge` | `None` | edge to rotate about |
| `run_time` | `5.0` | duration |

### Rotate

Rotates a mobject by a fixed angle, interpolated smoothly over `run_time`.

```python
win.play(Rotate(sq, PI / 4))
win.play(Rotate(sq, 90 * DEGREES, about_point=ORIGIN))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `angle` | `PI` | rotation in radians |
| `about_point` | `None` | rotation pivot |
| `run_time` | `1.0` | duration |

---

## Grow & scale-in animations

### GrowFromCenter

Scales a mobject up from its center.

```python
win.play(GrowFromCenter(sq))
```

### GrowFromEdge / GrowFromPoint

`GrowFromEdge` grows from a given edge; `GrowFromPoint` grows from an arbitrary
point.

```python
win.play(GrowFromEdge(sq, DOWN))
win.play(GrowFromPoint(sq, LEFT * 3))
```

### GrowArrow

Grows an arrow from its tail toward its tip.

```python
win.play(GrowArrow(Arrow(LEFT, RIGHT)))
```

### SpinInFromNothing

Spins a mobject while growing it in from its center.

```python
win.play(SpinInFromNothing(sq))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `angle` | `PI/2` | spin angle |
| `run_time` | `1.0` | duration |

All grow animations accept `point_color` and `run_time`.

---

## Text & typing animations

### Write / Unwrite

`Write` reveals text (or any mobject) character by character, simulating
handwriting. `Unwrite` erases it again; `reverse=True` flips the direction.

```python
win.play(Write(Text("Hello World"), run_time=2.0))
win.play(Unwrite(Text("Hello World")))
```

### TypeWithCursor / UntypeWithCursor

`TypeWithCursor` types text one character at a time while a cursor mobject sits at
the insertion point; `UntypeWithCursor` deletes it character by character.

```python
text = Text("Hello")
cursor = Dot(color=WHITE).scale(0.3)
win.play(TypeWithCursor(text, cursor))
win.play(UntypeWithCursor(text, cursor))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `buff` | `0.1` | gap between text and cursor |
| `time_per_char` | `0.1` | seconds per typed character |
| `keep_cursor_y` | `True` | keep cursor on the text line |
| `leave_cursor_on` | `True` | leave cursor visible at end |

### TextDecimalNumber

A `Text` mobject rendering a formatted decimal number, commonly used for animated
counters.

```python
count = TextDecimalNumber(0, num_decimal_places=2, color=GREEN)
win.play(Create(count))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `number` | `0` | initial value |
| `font_size` | `48` | font size |
| `num_decimal_places` | `2` | decimal digits shown |

---

## Visual effects

### Indicate

Briefly scales a mobject up and back to draw attention, optionally tinting it.

```python
win.play(Indicate(sq))
win.play(Indicate(circle, color=RED))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `scale_factor` | `1.2` | how much it pops |
| `color` | yellow `#F7D96F` | attention tint |

### ShowPassingFlash

Sweeps a bright band along a mobject's path for a moment, emphasizing a curve or
outline without changing it.

```python
win.play(ShowPassingFlash(circle))
```

### Circumscribe

Draws a shape (a `Rectangle` by default) around a mobject to enclose it.

```python
win.play(Circumscribe(sq))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `shape` | `Rectangle` | enclosing shape |
| `color` | `None` | outline color |
| `stroke_width` | `4` | outline width |
| `buff` | `0.1` | gap around the mobject |

### Blink

Makes a mobject blink by fading it off and back on.

```python
win.play(Blink(Dot()))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `time_on` / `time_off` | `0.5` | seconds on/off per blink |
| `blinks` | `1` | number of blinks |

### ApplyWave

Passes a sinusoidal wave distortion through a mobject, making it ripple.

```python
win.play(ApplyWave(sq))
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `direction` | `UP` | wave travel direction |
| `amplitude` | `0.2` | wave strength |
| `ripples` | `1` | number of waves |
| `run_time` | `2.0` | duration |

---

## Composition

### AnimationGroup

Plays several animations simultaneously, optionally staggering their starts.

```python
win.play(AnimationGroup(Create(sq), FadeIn(circle), lag_ratio=0.5))
```

### Succession

Plays a sequence of animations one after another as a single `play`.

```python
win.play(Succession(Create(sq), Transform(sq, circle), FadeOut(circle)))
```

---

## MathTex & Text rendering

- `MathTex` defaults to **real LaTeX** rendering (`_USE_NATIVE_MATHTEX = False` in
  `real_time_manim.vulkan_bind`). Set that flag to `True` for the fast **native
  Unicode mode**, which needs no TeX installation. See the wiki's Math Rendering
  page for both modes and the Unicode mapping.
- `Text` renders TrueType fonts with per-character submobjects, so it works with
  `Write`, `TypeWithCursor`, and the text senders. Color, size, weight and slant
  are set through the standard Manim API.

---

## Recording & cleanup

Recording and automatic cleanup of transient `media/` output are handled by the
`real_time_manim.record` module:

- `fast_record_scene(scene, out_path=None, ...)` — offline, hidden-window
  rendering straight to an MP4 (default output `~/Downloads/output.mp4`).
- `record_scene(scene, out_path=None, ...)` — records a visible live window.

Both accept a Scene subclass/instance/callable, and clean up transient media by
default. See the wiki's Recording page for the full option set.
