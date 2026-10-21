# Sweeps and Waves (ShowPassingFlash, ApplyWave)

Three "running-light / disturbance" animations: a beam that sweeps along a stroke, and a ripple that crosses an object.

## Parameters

### `ShowPassingFlash` 

```python
ShowPassingFlash(mobject, time_width=0.1, run_time=1.0, remover=True, **kwargs)
```

Each frame shows only a small "sliding beam" sweeping along the stroke (rather than drawing it in gradually); when it finishes the object is handled according to `remover`. Good for giving an outline or curve an "energy flowing through" effect. **Inherits** `ShowPassingFlash(Animation)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `VMobject` | — (required) | the vector object being swept |
| `time_width` | `float` | `0.1` | the beam length as a fraction of the whole stroke (`1` = one whole stroke, `2` = twice as long) |
| `run_time` | `float` | `1.0` | the duration |
| `remover` | `bool` | `True` | whether to remove the object from the scene when it finishes. Since 2026-10-16 **you can pass `False` explicitly** (previously always `True`): with `False` the object stays in the scene and its full stroke is restored |
| `**kwargs` | … | — | `Animation` common parameters (`rate_func`, `lag_ratio`, …) |

> **Returns**: a `ShowPassingFlash` instance.

One-liner:

```python
win.play(ShowPassingFlash(RegularPolygon(5, color=DARK_GRAY).scale(2), time_width=0.5))
```

### `ShowPassingFlashWithThinningStrokeWidth` 

```python
ShowPassingFlashWithThinningStrokeWidth(vmobject, n_segments=10, time_width=0.1, remover=True, **kwargs)
```

Plays `n_segments` `ShowPassingFlash`es with decreasing stroke width and decreasing beam width stacked together, giving a sweep whose "comet tail gradually thins" (this class has **no docstring**; this is put together from the source). **Inherits** `ShowPassingFlashWithThinningStrokeWidth(AnimationGroup)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vmobject` | `VMobject` | — (required) | the vector object being swept |
| `n_segments` | `int` | `10` | the number of segments |
| `time_width` | `float` | `0.1` | the starting beam width |
| `remover` | `bool` | `True` | whether to remove it when it finishes |
| `**kwargs` | … | — | passed through to each segment's `ShowPassingFlash` (its `time_width` is popped first) |

> **Returns**: a `ShowPassingFlashWithThinningStrokeWidth` instance.

One-liner:

```python
win.play(ShowPassingFlashWithThinningStrokeWidth(Circle(stroke_width=8), run_time=2))
```

### `ApplyWave` 

```python
ApplyWave(mobject, direction=UP, amplitude=0.2, wave_func=smooth, time_width=1,
          ripples=1, run_time=2, **kwargs)
```

Sends a **ripple across the object**, periodically displacing its point set along a direction and then restoring it (the shape ends up fully recovered); `ripples` controls the number of crests, and `time_width` controls the wave's length relative to the object's width. **Inherits** `ApplyWave(Animation)`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | the object being disturbed |
| `direction` | `Vector3DLike` | `UP` | the direction in which the wave pushes the points (it is normalised) |
| `amplitude` | `float` | `0.2` | the maximum displacement |
| `wave_func` | `RateFunction` | `smooth` | the shape function of a single crest |
| `time_width` | `float` | `1` | the wave length as a fraction of the object's width |
| `ripples` | `int` | `1` | the number of ripples |
| `run_time` | `float` | `2` | the duration |
| `**kwargs` | … | — | `Animation` common parameters. RTM's own `ApplyWave` **has no `apply_function_kwargs`** (it is not a `Homotopy` subclass, so that kwarg is swallowed by `**kwargs` and has no effect) |

> **Returns**: an `ApplyWave` instance.

One-liner:

```python
win.play(ApplyWave(Tex("WaveWaveWave").scale(2), ripples=3, amplitude=0.3))
```

#### Sample: ShowPassingFlash / thinning comet tail / ApplyWave demonstrated item by item

The page clip demonstrates ShowPassingFlash → ShowPassingFlashWithThinningStrokeWidth → ApplyWave in that order, one segment each, with every parameter labelled on screen.

```python
from real_time_manim import (
    BLUE,
    DARK_GRAY,
    GREEN,
    GREY_B,
    YELLOW,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Circle,
    RegularPolygon,
    Scene,
    ShowPassingFlashWithThinningStrokeWidth,
    Text,
    VGroup,
    smooth,
)
from real_time_manim.vulkan_bind import (
    MLWindow,
    ApplyWave,
    FadeIn,
    FadeOut,
    ShowPassingFlash,
    Wait,
    Write,
)
from real_time_manim.record import fast_record_scene  # noqa: F401  used by __main__ at the end of the file


class Page_01b_Sweeps_and_Waves(Scene):
    def construct(self):
        win = MLWindow(1280, 720, hidden=True)   # parameters w=1280 / h=720 / hidden=True
        win.scene = self                          # parameter win.scene

        title = Text("ShowPassingFlash / ApplyWave",
                     font_size=36, color=GREEN).to_edge(UP)   #title uses ASCII only: font fallback stays reliable in both engines
        win.play(Write(title), run_time=0.8)

        # —— step 1: ShowPassingFlash(mobject, time_width, **kwargs) ——
        sig1 = Text("ShowPassingFlash(poly, time_width=0.5, run_time=1.6)",
                    font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)
        poly = RegularPolygon(5, color=DARK_GRAY).scale(1.6).next_to(sig1, DOWN, buff=0.7)
        win.play(FadeIn(sig1, shift=DOWN), run_time=0.45)
        win.play(
            ShowPassingFlash(
                poly,                                    # parameter mobject ✓
                time_width=0.5,                          # parameter time_width=0.5 ✓ (default 0.1: the beam covers 50% of the whole stroke)
                run_time=1.6,                            # parameter **kwargs(run_time) ✓
            ),
            run_time=1.6,
        )
        # RTM's version defaults remover to True, removing the mobject from the scene when it finishes, so the pentagon is not FadeOut-ed again
        #(since 2026-10-16 remover can be passed False explicitly, leaving the object in the scene).
        win.play(FadeOut(sig1), run_time=0.45)

        # —— step 2: ShowPassingFlashWithThinningStrokeWidth(
        #                vmobject, n_segments, time_width, remover, **kwargs) ——
        s2a = Text("ShowPassingFlashWithThinningStrokeWidth(", font_size=28, color=GREY_B)
        s2b = Text("    ring, n_segments=12, time_width=0.15,", font_size=28, color=GREY_B)
        s2c = Text("    remover=True, run_time=1.8)", font_size=28, color=GREY_B)
        sig2 = VGroup(s2a, s2b, s2c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        ring = Circle(radius=1.2, stroke_width=10, color=BLUE).next_to(sig2, DOWN, buff=0.6)
        win.play(FadeIn(sig2, shift=DOWN), run_time=0.45)
        win.play(
            ShowPassingFlashWithThinningStrokeWidth(
                ring,                                    # parameter vmobject ✓
                n_segments=12,                           # parameter n_segments=12 ✓ (default 10)
                time_width=0.15,                         # parameter time_width=0.15 ✓ (default 0.1)
                remover=True,                            # parameter remover=True ✓ (the default, passed explicitly)
                run_time=1.8,                            # parameter **kwargs(run_time) ✓
            ),
            run_time=1.8,
        )
        win.play(FadeOut(sig2), FadeOut(ring), run_time=0.45)

        # —— step 3: ApplyWave(mobject, direction, amplitude, wave_func,
        #                      time_width, ripples, run_time) ——
        s3a = Text("ApplyWave(txt, direction=UP, amplitude=0.35,", font_size=30, color=GREY_B)
        s3b = Text("           wave_func=smooth, time_width=1,", font_size=30, color=GREY_B)
        s3c = Text("           ripples=3, run_time=2)", font_size=30, color=GREY_B)
        sig3 = VGroup(s3a, s3b, s3c).arrange(DOWN, buff=0.08).next_to(title, DOWN, buff=0.4)
        wtxt = Text("WaveWaveWave", font_size=46, color=YELLOW).next_to(sig3, DOWN, buff=0.9)
        win.play(FadeIn(sig3, shift=DOWN), run_time=0.45)
        win.play(
            ApplyWave(
                wtxt,                                    # parameter mobject ✓
                direction=UP,                            # parameter direction=UP ✓ (explicit: the direction the wave pushes)
                amplitude=0.35,                          # parameter amplitude=0.35 ✓ (default 0.2)
                wave_func=smooth,                        # parameter wave_func=smooth ✓ (the shape of a single crest)
                time_width=1,                            # parameter time_width=1 ✓ (the wave-length fraction)
                ripples=3,                               # parameter ripples=3 ✓ (default 1)
                run_time=2,                              # parameter run_time=2 ✓
            ),
        )
        win.play(FadeOut(sig3), FadeOut(wtxt), run_time=0.5)
        win.play(Wait(0.3))

        win.play(FadeOut(title), run_time=0.5)
        win.close()
```

What this code does: it writes the title first, then demonstrates three segments.

- Segment 1: a dark-grey pentagon; `ShowPassingFlash` sweeps a beam covering 50% of the whole stroke once around its edges (1.6 s).
- Segment 2: a blue ring; `ShowPassingFlashWithThinningStrokeWidth` stacks 12 sweeps with decreasing stroke width to give a "thinning comet tail".
- Segment 3: the yellow text "WaveWaveWave"; `ApplyWave` sends 3 crests across it from bottom to top, and the shape is fully restored once it finishes.

Each segment clears the stage when it finishes; the window closes at the end.

<video src="assets/RTM output/01b-Sweeps-and-Waves.mp4" controls width="560"></video>

> Note:
>
> - `ShowPassingFlash`'s `remover` defaults to `True` (for backward compatibility): when it finishes the object **is removed from the scene** (the sample uses the default, so the pentagon is not `FadeOut`-ed again); with an explicit `remover=False` the object stays in the scene and its full stroke is restored (`_restore_full_stroke`).
> - `ApplyWave`'s `time_width`/`ripples` are both relative to the object's **width**; use the same parameters on a wider object and the wave is flatter.

Not demonstrated: `ShowPassingFlash`'s "restore the full stroke" (`remover=False`) behaviour after it finishes — it is wired up (the `remover` parameter was completed on 2026-10-16, test `tests/test_gap_indication_fade.py`): with `remover=True` (the default) `clean_up_from_scene` removes the pentagon from the scene; the sample only demonstrates the sweep itself, so this page has no `remover=False` video yet.
See also: [Indicate and Flash](01-Indicate-and-Flash.md), [Circumscribe and Focus](02-Circumscribe-and-Focus.md), [Transform Core](../Transforms/01-Transform-Core.md)
