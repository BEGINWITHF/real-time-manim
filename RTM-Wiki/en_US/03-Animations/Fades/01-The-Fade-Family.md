# The Fade family: FadeIn / FadeOut

The most commonly used entrance and disappearance animations: `FadeIn` fades in from "fully transparent + (optional) offset/scale" to the normal state, `FadeOut` fades out in reverse and automatically removes itself from the scene; `shift` / `target_position` / `scale` combine into a compound effect of displacement, scaling and opacity.

## Parameters

### `FadeIn`

```python
FadeIn(*mobjects, shift=None, target_position=None, scale=1, **kwargs)
```

> In the source, `FadeIn.__init__(self, *mobjects, shift=None, target_position=None, scale=1.0, run_time=1.0, **kwargs)` (RTM's own implementation, `real_time_manim/animations/fade_in.py`). The line above is the **actually usable merged signature**, the same in both versions.

Inherits `FadeIn(Animation)`. The three optional parameters each handle one thing:

- `shift` decides the direction;
- `target_position` decides the start position;
- `scale` decides the start size.

On the RTM side `introducer` is **not fixed** (default `False`; passing `True` explicitly takes effect and is harmless).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | —(required) | one or more (more than 1 is wrapped into a `Group`). Pass at least one: the CE version raises `ValueError("At least one mobject must be passed.")`, while RTM's own version does not error on an empty `mobjects` and simply has no object to animate |
| `shift` | `np.ndarray \| None` | `None` | the displacement vector when fading in (enters from `-shift`). **accepts** `UP`/`DOWN`/`LEFT`/`RIGHT`/any vector; when `None` and no `target_position` is given it is `ORIGIN` (a pure opacity change) |
| `target_position` | `np.ndarray \| Mobject \| None` | `None` | the fade-in start position. **accepts** coordinates or a mobject (takes its **center** and automatically computes `shift = target_position - mobject.get_center()`) |
| `scale` | `float` | `1` | the start scale factor: fades in while scaling from `scale` times back to the original size. **accepts** any positive number. Since 2026-10-16 it also takes effect on **leaf VMobjects** (`Circle`/`Square`/`Dot`) (previously it only worked on containers with submobjects and leaves were silently ignored) |
| `introducer` | `bool` | `False` | **not fixed** on the RTM side and can be passed (default `False`) |
| rest | — | — | `Animation` common parameters (`run_time=1.0`, `rate_func=smooth`, `lag_ratio=0`, `name`, `suspend_mobject_updating`, `reverse_rate_function`, `use_override`). RTM's own `FadeIn` **is not a `Transform` subclass** and has no `path_arc` / `path_func` parameters (passing them gets swallowed by `**kwargs` and has no effect) |

> **Returns**: a `FadeIn` instance.

#### Sample: the three entrance styles shift / scale / target_position

The square `FadeIn(sq, shift=DOWN, scale=0.5, ...)` grows back into place from below at half size, and the circle `FadeIn(ci, target_position=ORIGIN, ...)` drifts in from the center of the picture.

The same row also names the `Animation` common parameters `run_time` / `lag_ratio` / `name` etc. one by one, and puts the two `FadeIn`s into one `win.play` to finish together.

```python
from real_time_manim import Scene, Square, Circle, Text, VGroup, \
    BLUE, GREEN, YELLOW, GREY_B, UP, DOWN, LEFT, RIGHT, ORIGIN, \
    smooth, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class FadeInDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-FadeIn", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l1 = Text("FadeIn(mobject, shift=DOWN, scale=0.5, run_time=1.1,",
                  font_size=30, color=GREY_B)
        l2 = Text("        lag_ratio=0.0, name='FadeIn')   FadeIn(c, target_position=ORIGIN)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line "FadeIn" signature label
        sq = Square(side_length=1.3, color=BLUE).next_to(lab1, DOWN, buff=0.6).shift(LEFT * 2.2)   # demo object "sq"
        ci = Circle(radius=0.6, color=GREEN).next_to(lab1, DOWN, buff=0.6).shift(RIGHT * 2.2)   # demo object "ci"
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(
            FadeIn(sq,                               # one of "*mobjects"
                   shift=DOWN,                       # parameter "shift": enters from below
                   scale=0.5,                        # parameter "scale": grows back to full size from half size
                   run_time=1.1,                     # parameter "run_time"
                   lag_ratio=0.0,                    # parameter "lag_ratio"
                   name="FadeIn(Square)",            # parameter "name"
                   suspend_mobject_updating=True,    # parameter "suspend_mobject_updating"
                   reverse_rate_function=False,      # parameter "reverse_rate_function"
                   use_override=True),               # parameter "use_override"
            FadeIn(ci,                               # the second of "*mobjects" (another instance)
                   target_position=ORIGIN,           # parameter "target_position": drifts in from the center
                   run_time=1.1),                    # parameter "run_time"
            run_time=1.1, rate_func=smooth,          # play-level "rate_func"
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the label first lays out the full call, then the two objects fade in separately.

- The square "grows" back into place from below at half size — `shift` gives the direction, `scale` the start size.
- The circle drifts in from the center of the picture `ORIGIN` — `target_position` gives the start point.

Inside the parentheses, `run_time` / `lag_ratio` / `name` / `suspend_mobject_updating` / `reverse_rate_function` / `use_override` are all `Animation` common parameters; see [Lifecycle and Common Parameters](../Common/01-Lifecycle-and-Common-Parameters.md) for a line-by-line explanation. When the fade-in finishes the objects stay in the scene unchanged.

<video src="assets/RTM output/01-The-Fade-Family-fadein.mp4" controls width="560"></video>

### `FadeOut`

```python
FadeOut(*mobjects, shift=None, target_position=None, scale=1, **kwargs)
```

> Same as `FadeIn`: RTM's own `FadeOut.__init__(self, *mobjects, shift=None, target_position=None, scale=1.0, run_time=1.0, **kwargs)`, with the three optional parameters taken by the parent class `_Fade`. The line above is the **actually usable merged signature**, the same in both versions.

Inherits `FadeOut(Animation)`. The object **fades out** until it disappears, and is automatically removed from the scene when finished.

`remover=True` is a **fixed value** in RTM's own version: it calls `super.__init__` first and then overwrites `self.remover = True`, so passing `remover=False` is overridden.

Something like `shift=UP*2` can make a "drift away" effect, and `target_position=other` can make an object fade toward another object.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | —(required) | one or more (more than 1 is wrapped into a `Group`). Pass at least one: the CE version raises `ValueError`, while RTM's own version does not error but has no object to animate |
| `shift` | `np.ndarray \| None` | `None` | the displacement vector when fading out (drifts out in that direction). **accepts** the same as `FadeIn`; when `None` and no `target_position` is given it is `ORIGIN` (fade out in place) |
| `target_position` | `np.ndarray \| Mobject \| None` | `None` | the fade-out end position. **accepts** coordinates or a mobject (takes the center and computes `shift` automatically) |
| `scale` | `float` | `1` | the end scale factor: shrinks to `scale` times during the fade-out. **accepts** any positive number. Since 2026-10-16 it also takes effect on **leaf VMobjects** (same as `FadeIn`) |
| rest | — | — | same as `FadeIn`: `Animation` common parameters (`introducer` defaults to `False` and can be passed, `remover` is **fixed at `True`**). RTM's own version has an additional internal method `_park_opacity(mob, value)` (it parks the animation opacity on the node the paint walk visits, so only subclasses with detached wrappers need to override it), a non-public parameter |

> **Returns**: a `FadeOut` instance.

#### Sample: shift drift / scale shrink / target_position fade away

The square and circle left behind by the previous segment are first placed statically into the scene, then demonstrated with two `FadeOut`s:

- `FadeOut(sq, shift=UP, ...)` makes the square drift upward;
- `FadeOut(ci, scale=0.3, target_position=ORIGIN, ...)` makes the circle shrink to 30% as it fades toward the center.

The swap label is also changed to a new one with a `FadeOut`.

```python
from real_time_manim import Scene, Square, Circle, Text, VGroup, \
    BLUE, GREEN, YELLOW, GREY_B, UP, DOWN, LEFT, RIGHT, ORIGIN, \
    linear, FadeIn, FadeOut, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class FadeOutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-FadeOut", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l1 = Text("FadeIn(mobject, shift=DOWN, scale=0.5, run_time=1.1,",
                  font_size=30, color=GREY_B)
        l2 = Text("        lag_ratio=0.0, name='FadeIn')   FadeIn(c, target_position=ORIGIN)",
                  font_size=30, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # the signature label left behind by the previous segment
        sq = Square(side_length=1.3, color=BLUE).next_to(lab1, DOWN, buff=0.6).shift(LEFT * 2.2)   # the object "sq" to fade out
        ci = Circle(radius=0.6, color=GREEN).next_to(lab1, DOWN, buff=0.6).shift(RIGHT * 2.2)   # the object "ci" to fade out
        self.add(lab1, sq, ci)   # put the demo objects into the scene statically first (the star of this sample is "FadeOut")
        l3 = Text("FadeOut(sq, shift=UP, run_time=1.0)   FadeOut(ci, scale=0.3, ...)",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # the swap label (in the same slot as lab1)
        win.play(FadeOut(lab1), FadeIn(l3, shift=DOWN), run_time=0.4)   # the old label fades out and the new one swaps in place
        win.play(
            FadeOut(sq,                              # one of "*mobjects"
                    shift=UP,                        # parameter "shift": drifts out upward
                    run_time=1.0,                    # parameter "run_time"
                    lag_ratio=0.0),                  # parameter "lag_ratio"
            FadeOut(ci,                              # the second of "*mobjects"
                    scale=0.3,                       # parameter "scale": shrinks to 0.3 times during the fade-out
                    target_position=ORIGIN,          # parameter "target_position": fades toward the center
                    run_time=1.0,                    # parameter "run_time"
                    name="FadeOut(Circle)"),         # parameter "name"
            run_time=1.0, rate_func=linear,          # play-level "rate_func"
        )
        win.play(FadeOut(l3), run_time=0.4)   # the label fades out too
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the previous segment's "result" is placed directly into the scene with `self.add` (this segment's star is the fade-out, so there is no need to act out the entrance again), and one `FadeOut(lab1)` at the start swaps the old label for a new one.

Then the square `shift=UP` drifts upward and the circle `scale=0.3` shrinks to 30% and `target_position=ORIGIN` fades toward the center.

When `FadeOut` finishes it automatically removes the object from the scene (`remover=True`), so after the label fades out at the end the picture closes cleanly.

<video src="assets/RTM output/01-The-Fade-Family-fadeout.mp4" controls width="560"></video>

### Manual-style "page swap": `AnimationGroup` one-for-one

The manual's classic page-swap idiom: one `AnimationGroup(FadeOut(old, shift=UP), FadeIn(new1, new2, shift=UP), lag_ratio=0.0)` swaps the old object out upward while the new objects swap in from below at the same time (see [AnimationGroup and Lag Ratios](../Composition/01-AnimationGroup-and-Lag-Ratios.md) for `AnimationGroup`'s own parameters and more usage).

`AnimationGroup` imported from the top level of `real_time_manim` works normally under RTM, and the sample uses it. RTM's **own version** previously made this combination "swap out as usual, but the swap in is missing"; it was fixed on 2026-10-16 and both versions now work (see the note below).

#### Sample: one swaps out, one swaps in

A red square is drawn with `Create` first, then one `AnimationGroup(FadeOut(x, shift=UP), FadeIn(ya, yb, shift=UP), lag_ratio=0.0)` swaps it for a "yellow circle + green triangle".

```python
from real_time_manim import Scene, Square, Circle, Triangle, Text, \
    RED, GREEN, YELLOW, GREY_B, UP, DOWN, LEFT, RIGHT, \
    AnimationGroup, Create, FadeIn, FadeOut, Write
from real_time_manim.vulkan_bind import MLWindow, Wait

class SwapGroupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-AnimationGroup swap", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l4 = Text("AnimationGroup(FadeOut(x, shift=UP), FadeIn(y1, y2, shift=UP))",
                  font_size=30, color=GREY_B).next_to(title, DOWN, buff=0.4)   # combination signature label
        x = (Square(side_length=1.2, color=RED).set_fill(RED, 0.6)
             .next_to(l4, DOWN, buff=0.7).shift(LEFT * 2.0))   # the red square "x" to be swapped out
        ya = Circle(radius=0.5, color=YELLOW).move_to(x)   # swap-in object one: stacked at "x"'s original position
        yb = (Triangle(color=GREEN).scale(0.9)
              .next_to(l4, DOWN, buff=0.7).shift(RIGHT * 2.0))   # swap-in object two
        win.play(FadeIn(l4, shift=DOWN), run_time=0.4)   # label fades in from below
        win.play(Create(x), run_time=0.7)   # draw the square to be swapped out first
        win.play(
            AnimationGroup(
                FadeOut(x, shift=UP),                # swap out: drifts out upward
                FadeIn(ya, yb, shift=UP),            # swap in: the new objects fade in from below
                lag_ratio=0.0,                       # parameter "lag_ratio": rise and fall together
            ),
            run_time=1.2,
        )
        win.play(Wait(0.8))   # pause 0.8s
        win.close()   # close the RTM window
```

What this code does: `AnimationGroup` puts the "swap out" and "swap in" into the same `win.play`, and `lag_ratio=0.0` makes the two halves rise and fall together — in the video, as the red square drifts away upward, the yellow circle and green triangle fade in from below at "x"'s original position, visually like an old card being replaced by new cards.

<video src="assets/RTM output/01-The-Fade-Family-swap.mp4" controls width="560"></video>

> Note:
>
> - `FadeIn`/`FadeOut`'s `introducer`/`remover` **in the CE version** are fixed constructor values, so do not pass them explicitly (it is a `TypeError`); RTM's own version accepts `FadeIn(introducer=...)`.
> - `FadeTransform` / `FadeTransformPieces` belong to the "transforms" chapter and are not on this page.

Not demonstrable:

- `introducer`: RTM's own `FadeIn` **does not fix** it and it can be passed (default `False`); only the CE version fixes it at `True` and passing it is a `TypeError`; there is no picture difference between the two versions. `FadeOut`'s `remover` is fixed at `True` on both sides, no difference.
- `path_arc` / `path_arc_axis` / `path_arc_centers` / `path_func` / `replace_mobject_with_target_in_scene`: RTM's own `FadeIn`/`FadeOut` are not `Transform` subclasses and have none of these parameters (passing them is swallowed and not visible in a pure fade in/out).
- empty `*mobjects`: the CE version raises `ValueError`, RTM's own version does not error, and neither has a visible picture.

---

See also: [Lifecycle and Common Parameters](../Common/01-Lifecycle-and-Common-Parameters.md) · [Create and the drawing family](../Creation-and-Removal/01-Create-and-the-Drawing-Family.md) · [Reverse Removal](../Creation-and-Removal/02-Reverse-Removal.md)
