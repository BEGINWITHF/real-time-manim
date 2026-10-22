# Special entrances: Broadcast

The manual's "7.4 Special entrances" section here covers just one class, `Broadcast`: it emits copies spreading ring by ring from a focal point, producing a radar/sonar ripple effect.

Verified renderable — `Broadcast` is not in RTM's own animation export list; the samples use manim's own `Broadcast` rendered through the RTM timeline, with RTM's `_spec.Broadcast` patch making it work. The two parameter sets each have their own clip.

## Parameters

### Broadcast

```python
Broadcast(mobject, focal_point=ORIGIN, n_mobs=5, initial_opacity=1, final_opacity=0,
          initial_width=0.0, remover=True, lag_ratio=0.2, run_time=3, **kwargs)
```

Inherits `Broadcast(LaggedStart) ← AnimationGroup`, from `animation/specialized.py`. From `focal_point` it **emits `n_mobs` copies of the shape spreading ring by ring**: each copy `Restore`s from the `initial_width` to its original size while its opacity goes from `initial_opacity` to `final_opacity`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the shape being broadcast (internally copied `n_mobs` times, the original is unaffected). **accepts** any vector object such as `Circle`, `Dot` |
| `focal_point` | `Sequence[float]` | `ORIGIN` | the emission centre. **accepts** a coordinate point — both keyword and positional values take strict effect (fixed 2026-10-16: an explicit `focal_point=ORIGIN` gives the manual's semantics, and the positional form `Broadcast(mob, ORIGIN, 3)` no longer raises `TypeError`). When it is not passed, the RTM patch still takes the mobject's centre (a pre-existing difference; the default is left alone so existing renders stay unchanged; both samples pass it explicitly) |
| `n_mobs` | `int` | `5` | number of copies |
| `initial_opacity` | `float` | `1` | starting opacity (0–1) |
| `final_opacity` | `float` | `0` | ending opacity (0–1) |
| `initial_width` | `float` | `0.0` | starting width (`0` starts from a point, `0.2` starts from a small circle) |
| `remover` | `bool` | `True` | remove the copies when done |
| `lag_ratio` | `float` | `0.2` | stagger ratio between rings (the bigger it is, the more "one after another") |
| `run_time` | `float` | `3` | total duration |
| `**kwargs` | `Any` | — | forwarded to `LaggedStart`/`AnimationGroup` (e.g. `rate_func`) |

> **Returns**: `Animation` (hand it to `play` to play it). It relies on `LaggedStart` — RTM likewise renders it with manim's own class (see the measurements in [Composition](../Composition/01-AnimationGroup-and-Lag-Ratios.md)).

#### Sample: a 6-ring radar wave spreading from the focal point into transparency

A teal ring is copied 6 times; the copies scale up in a staggered way from a small circle and fade out, giving ring after ring of wave spreading outwards.

```python
from real_time_manim import Scene, Text, VGroup, Circle, Dot, TEAL_A, GREY_B, YELLOW, UP, \
    DOWN, Broadcast, FadeIn, Write, smooth
from real_time_manim.vulkan_bind import MLWindow, Wait

class BroadcastDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("03-Broadcast", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("Broadcast(ring, focal_point=ORIGIN, n_mobs=6,", font_size=30, color=GREY_B)
        l2 = Text("           initial_opacity=1.0, final_opacity=0.0, initial_width=0.2,", font_size=28, color=GREY_B)
        l3 = Text("           lag_ratio=0.3, run_time=2.4)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        focal = Dot(point=DOWN * 1.4, radius=0.07, color=TEAL_A)   # emission centre
        ring = Circle(radius=2.0, color=TEAL_A).move_to(focal)   # the ring being broadcast
        win.play(FadeIn(sig, shift=DOWN), FadeIn(focal), run_time=0.4)   # fade in the label and the focal point
        win.play(Broadcast(ring, focal_point=focal.get_center(), n_mobs=6,   # parameter "focal_point / n_mobs"
                           initial_opacity=1.0, final_opacity=0.0, initial_width=0.2,   # parameter "opacity / initial_width"
                           lag_ratio=0.3, run_time=2.4))   # parameter "lag_ratio / run_time"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: it puts a big ring on a teal focal point at the bottom of the frame, and `Broadcast` copies it 6 times; each copy scales up from the `initial_width=0.2` small circle back to its full size, staggered by `lag_ratio=0.3`, while its opacity fades from 1 to 0 — ring after ring of radar wave spreading outwards.

`remover=True` clears the copies when done, leaving only the focal point.

<video src="assets/RTM output/03-Special-Entrances-broadcast.mp4" controls width="560"></video>

> Note: when `focal_point` is not passed the default is still the mobject's centre (a pre-existing RTM difference, left alone so existing renders stay unchanged); only an **explicit** value matches the manual's semantics — and now both keyword and positional values take strict effect (both samples pass it explicitly by keyword).

#### Sample: a comparison set with a different focal point, fewer rings, and a semi-transparent finish

The second parameter set: 4 rings, a wider start, finishing at 40% opacity, a wider stagger, and `rate_func=smooth`.

```python
from real_time_manim import Scene, Text, VGroup, Circle, Dot, TEAL_A, GREY_B, YELLOW, LEFT, \
    UP, DOWN, Broadcast, FadeIn, Write, smooth
from real_time_manim.vulkan_bind import MLWindow, Wait

class BroadcastTunedDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("03-BroadcastTuned", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write the title

        l1 = Text("Broadcast(ring, focal_point=SPOT, n_mobs=4,", font_size=30, color=GREY_B)
        l2 = Text("           initial_opacity=0.9, final_opacity=0.4, initial_width=0.5,", font_size=28, color=GREY_B)
        l3 = Text("           lag_ratio=0.5, run_time=2.2, rate_func=smooth)", font_size=30, color=GREY_B)
        sig = VGroup(l1, l2, l3).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # signature label
        spot = Dot(point=LEFT * 2.6 + DOWN * 1.4, radius=0.09, color=GREY_B)   # the new emission centre
        ring = Circle(radius=1.5, color=TEAL_A).move_to(spot)   # a smaller ring
        win.play(FadeIn(sig, shift=DOWN), FadeIn(spot), run_time=0.4)   # fade in the label and the focal point
        win.play(Broadcast(ring, focal_point=spot.get_center(), n_mobs=4,   # parameter "n_mobs=4" (fewer rings)
                           initial_opacity=0.9, final_opacity=0.4, initial_width=0.5,   # parameter "opacity / initial_width" (semi-transparent finish)
                           lag_ratio=0.5, run_time=2.2, rate_func=smooth))   # parameter "lag_ratio / rate_func"
        win.play(Wait(0.6))   # hold to see the result
        win.close()   # close the RTM window
```

What this code does: the focal point moves to the grey dot on the left of the frame, the ring radius becomes 1.5, and the whole parameter set is swapped:

- only 4 rings;
- the start is already half a ring wide (`initial_width=0.5`);
- it stops at 40% opacity at the end;
- the stagger is widened to `lag_ratio=0.5`;
- `rate_func=smooth`.

The ripples are fewer, slower and "fainter". Watched side by side, the two samples show what each parameter in the table above does on its own.

<video src="assets/RTM output/03-Special-Entrances-broadcast_tuned.mp4" controls width="560"></video>

Not demonstrated: `Broadcast`'s `remover` — no video: what gets removed at the end is the internal copies, which are indistinguishable on screen once `final_opacity=0`. The manual's section has no other entries.

> **2026-10-16 update**: `focal_point`'s default is still the mobject's centre (a pre-existing RTM difference; the default is unchanged so existing renders stay the same), but an explicit value now takes strict effect — the keyword `focal_point=ORIGIN` gives the manual's semantics, and the positional form `Broadcast(mob, ORIGIN, 3)` no longer raises `TypeError` outright (it used to crash).

---

See also: [AnimationGroup and Lag Ratios](../Composition/01-AnimationGroup-and-Lag-Ratios.md) · [Rotation animations](01-Rotation.md)
