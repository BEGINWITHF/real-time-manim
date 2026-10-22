# Matching transforms: TransformMatchingShapes / Tex

This transform family splits both the source and the target into "parts" and then pairs them by key: each part first gets a **key**, parts with the same key `Transform` into one another, and parts with different keys fade out / fade in (or are transformed forcibly, depending on the parameters).

Scenes like deriving a formula or rearranging letters, where "only the changing terms move", are its home turf.

## Parameters

### `TransformMatchingShapes`

```python
TransformMatchingShapes(mobject, target_mobject, transform_mismatches=False,
                        fade_transform_mismatches=False, key_map=None, **kwargs)
```

Matches by **shape**. It takes all point-bearing submobjects on both sides, normalizes them (moves them to the origin, sets the height to 1, keeps coordinates to 3 decimals) and hashes them: equal hashes count as "the same shape" and transform into one another; unmatched source parts fade out and target parts fade in.

A typical use is rearranging letters such as `Text("the morse code")` → `Text("here come dots")`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the source (removed when finished; `target_mobject` takes over) |
| `target_mobject` | `Mobject` | — | the target (added to the scene when finished) |
| `transform_mismatches` | `bool` | `False` | `True`: unmatched parts are forcibly deformed with `Transform` too |
| `fade_transform_mismatches` | `bool` | `False` | `True`: unmatched parts transition with `FadeTransformPieces` |
| `key_map` | `dict \| None` | `None` | manually specify "different keys that should still be paired": `{source key: target key}` |
| `**kwargs` | … | — | passed through to each internal sub-transform (commonly `path_arc=PI/2`), plus the `Animation` common parameters |

> **Returns**: a `TransformMatchingShapes` instance.

#### Sample: default same-shape matching (path_arc along an arc)

`the morse code` is rearranged into `here come dots`. With the default parameters, same-shape letters swap along an arc while differently-shaped parts fade out and the new letters fade in.

```python
from real_time_manim import GREY_B, YELLOW, DOWN, UP, PI, Scene, Text, VGroup, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, TransformMatchingShapes, Wait

class ShapesDefaultDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-ShapesDefault", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l1 = Text("TransformMatchingShapes(src, tar, transform_mismatches=False,",
                  font_size=28, color=GREY_B)
        l2 = Text("    fade_transform_mismatches=False, key_map=None, path_arc=PI/2)",
                  font_size=28, color=GREY_B)
        lab1 = VGroup(l1, l2).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line signature label
        src = Text("the morse code", font_size=44).next_to(lab1, DOWN, buff=0.8)   # source: the sentence to rearrange
        tar = Text("here come dots", font_size=44).move_to(src)   # target: the rearranged sentence
        win.play(FadeIn(lab1, shift=DOWN), run_time=0.4)   # label fades in from below
        self.add(src)   # add the source to the scene first (it is removed when finished and the target takes over)
        win.play(
            TransformMatchingShapes(                # parameter "mobject" (source, removed when finished)
                src,
                tar,                                # parameter "target_mobject" (takes over the scene when finished)
                transform_mismatches=False,         # parameter "transform_mismatches": False, differently-shaped parts fade out and in
                fade_transform_mismatches=False,    # parameter "fade_transform_mismatches": False
                key_map=None,                       # parameter "key_map": None, no manual pairing
                path_arc=PI / 2,                    # parameter "path_arc" (**kwargs): same-shape parts travel along an arc
            ),
            run_time=2.6,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: the source sentence `src` is first `self.add`ed into the scene. `TransformMatchingShapes` normalizes every letter on both sides and then pairs them by shape hash: the same-shape letters `h`/`e`/`o`… travel along the `path_arc=PI/2` arc to their positions in the new words, and the letters that do not match fade out in place while the target letters fade in. When it finishes the source sentence is removed and `tar` takes over the scene.

<video src="assets/RTM output/01-Matching-Transforms-shapes_default.mp4" controls width="560"></video>

#### Sample: transform_mismatches=True forces a deformation

The same sentence is run again with only one difference: `transform_mismatches=True`, so parts that do not match no longer fade out and in but are forcibly deformed across with `Transform`.

```python
from real_time_manim import GREY_B, YELLOW, DOWN, UP, PI, Scene, Text, VGroup, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, TransformMatchingShapes, Wait

class ShapesMismatchDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-ShapesMismatch", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l3 = Text("TransformMatchingShapes(src, tar, transform_mismatches=True, ...)",
                  font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        src2 = Text("the morse code", font_size=44).next_to(l3, DOWN, buff=0.8)   # source: the sentence to rearrange
        tar2 = Text("here come dots", font_size=44).move_to(src2)   # target: the rearranged sentence
        win.play(FadeIn(l3, shift=DOWN), run_time=0.4)   # label fades in from below
        self.add(src2)   # add the source to the scene first (it is removed when finished and the target takes over)
        win.play(
            TransformMatchingShapes(                # parameter "mobject" (source, removed when finished)
                src2,
                tar2,                               # parameter "target_mobject" (takes over the scene when finished)
                transform_mismatches=True,          # parameter "transform_mismatches": True, differently-shaped parts are forcibly deformed too
                fade_transform_mismatches=False,    # parameter "fade_transform_mismatches": False
                key_map=None,                       # parameter "key_map": None, no manual pairing
                path_arc=PI / 2,                    # parameter "path_arc" (**kwargs): same-shape parts travel along an arc
            ),
            run_time=2.4,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: same source and target as the previous one, only `transform_mismatches=True`, so parts whose hashes do not match are also forcibly deformed across with `Transform` (a hard morph across shapes) instead of each fading on its own. Put the two side by side to tell the two ways of finishing apart: "fade out and in" vs "hard deformation".

<video src="assets/RTM output/01-Matching-Transforms-shapes_mismatch.mp4" controls width="560"></video>

#### Sample: manual key pairing with key_map

`cat` → `hat`: `key_map` manually pairs the differently-shaped source `"c"` with the target `"h"`, so only the first letter swaps and transforms.

```python
from real_time_manim import GREY_B, YELLOW, DOWN, LEFT, UP, PI, Scene, Text, VGroup, FadeIn, Write
from real_time_manim.vulkan_bind import MLWindow, TransformMatchingShapes, Wait

class ShapesKeyMapDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-ShapesKeyMap", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l4 = Text("key_map = {shape_key('c'): shape_key('h')}  # manual key pairing",
                  font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)   # signature label
        l5 = Text("TransformMatchingShapes(cat, hat, key_map=key_map, ...)",
                  font_size=28, color=GREY_B).next_to(l4, DOWN, buff=0.06)   # second signature line
        lab2 = VGroup(l4, l5)
        src3 = Text("cat", font_size=52, color=GREY_B).next_to(lab2, DOWN, buff=0.8).shift(LEFT * 2.0)   # source word cat
        tar3 = Text("hat", font_size=52, color=GREY_B).move_to(src3)   # target word hat (only the first letter changes)
        win.play(FadeIn(lab2, shift=DOWN), run_time=0.4)   # label fades in from below
        self.add(src3)   # add the source to the scene first (it is removed when finished and the target takes over)
        key_map = {
            TransformMatchingShapes.get_mobject_key(src3[0]):   # the shape key of the source letter "c"
            TransformMatchingShapes.get_mobject_key(tar3[0]),   # the shape key of the target letter "h"
        }
        win.play(
            TransformMatchingShapes(                # parameter "mobject" (source, removed when finished)
                src3,
                tar3,                               # parameter "target_mobject" (takes over the scene when finished)
                transform_mismatches=False,         # parameter "transform_mismatches": False
                fade_transform_mismatches=False,    # parameter "fade_transform_mismatches": False
                key_map=key_map,                    # parameter "key_map" ("c" -> "h" forced pairing)
                path_arc=PI / 2,                    # parameter "path_arc" (**kwargs): same-shape parts travel along an arc
            ),
            run_time=2.4,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: `get_mobject_key(src3[0])` / `get_mobject_key(tar3[0])` computes on the spot the shape keys of the source's first letter `c` and the target's first letter `h` (different shapes, so naturally different hashes). Once the two keys are put in `key_map`, that pair of letters is forcibly paired: only the first letter swaps and transforms, while `a`/`t` stay put.

<video src="assets/RTM output/01-Matching-Transforms-shapes_keymap.mp4" controls width="560"></video>

### `TransformMatchingTex`

```python
TransformMatchingTex(mobject, target_mobject, transform_mismatches=False,
                     fade_transform_mismatches=False, key_map=None, **kwargs)
```

Matches by the **LaTeX fragment's `tex_string`**: as long as some sub-part's TeX source string is the same on both sides, they transform into one another — a great tool for "while deriving a formula, only the changing terms move and the rest stay put". For `Group`/`VGroup` it drills down recursively to the parts that actually carry a `tex_string`. (The MathTex sample has been measured in RTM: MathTex goes through the Typst conversion channel and the formula renders character by character correctly)

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | source |
| `target_mobject` | `Mobject` | — | target |
| `transform_mismatches` | `bool` | `False` | whether unmatched parts are forcibly `Transform`ed |
| `fade_transform_mismatches` | `bool` | `False` | whether unmatched parts use `FadeTransformPieces` |
| `key_map` | `dict \| None` | `None` | manual key pairing `{source key: target key}` |
| `**kwargs` | … | — | internal sub-transform parameters and the `Animation` common parameters |

> **Returns**: a `TransformMatchingTex` instance.

#### Sample: fade_transform_mismatches contrasted with the default

MathTex matches by `tex_string`; the same formula is run twice, `x²+y²=z²` → `x²=z²−y²`, first with `fade_transform_mismatches=True`, then back to the default behaviour for comparison.

```python
from real_time_manim import GREY_B, YELLOW, DOWN, UP, MathTex, Scene, Text, VGroup, \
    FadeIn, FadeOut, Write
from real_time_manim.vulkan_bind import MLWindow, TransformMatchingTex, Wait

class MatchingTexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-MatchingTex", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title

        l6 = Text("TransformMatchingTex(eq1, eq2, transform_mismatches=False,",
                  font_size=28, color=GREY_B)
        l7 = Text("    fade_transform_mismatches=True, key_map=None)",
                  font_size=28, color=GREY_B)
        lab3 = VGroup(l6, l7).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.4)   # two-line signature label
        eq1 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2").next_to(lab3, DOWN, buff=0.8)   # source formula x²+y²=z²
        eq2 = MathTex("{{x}}^2", "=", "{{z}}^2", "-", "{{y}}^2").move_to(eq1)   # target formula x²=z²−y²
        win.play(FadeIn(lab3, shift=DOWN), run_time=0.4)   # label fades in from below
        self.add(eq1)   # add the source formula to the scene first (it is removed when finished and the target takes over)
        win.play(
            TransformMatchingTex(                  # parameter "mobject" (source, removed when finished)
                eq1,
                eq2,                                # parameter "target_mobject" (takes over the scene when finished)
                transform_mismatches=False,         # parameter "transform_mismatches": False
                fade_transform_mismatches=True,     # parameter "fade_transform_mismatches": True, differently-shaped parts use FadeTransformPieces
                key_map=None,                       # parameter "key_map": None, no manual pairing
            ),
            run_time=2.4,
        )
        # comparison against the same transform's default behaviour: differently-shaped parts fade out / in directly
        eq3 = MathTex("{{x}}^2", "+", "{{y}}^2", "=", "{{z}}^2").move_to(eq1)   # comparison: the source formula is swapped back
        eq4 = MathTex("{{x}}^2", "=", "{{z}}^2", "-", "{{y}}^2").move_to(eq1)   # comparison: the same target formula
        l8 = Text("(default) transform_mismatches=False, fade_transform_mismatches=False",
                  font_size=28, color=GREY_B).next_to(title, DOWN, buff=0.4)   # comparison label
        win.play(FadeOut(VGroup(lab3, eq2)), FadeIn(l8, shift=DOWN), run_time=0.5)   # swap the label and let the result give way
        self.add(eq3)   # add the comparison's source formula to the scene
        win.play(
            TransformMatchingTex(                  # parameter "mobject" (source, removed when finished)
                eq3,
                eq4,                                # parameter "target_mobject" (takes over the scene when finished)
                transform_mismatches=False,         # parameter "transform_mismatches": False
                fade_transform_mismatches=False,    # parameter "fade_transform_mismatches": False, differently-shaped parts fade out and in directly
                key_map=None,                       # parameter "key_map": None, no manual pairing
            ),
            run_time=2.4,
        )
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: `x²+y²=z²` is transformed into `x²=z²−y²`. The TeX source strings of `x²`/`=`/`z²` are the same on both sides, so they stay put; only `+`/`y²` and `−`/`y²` move.

The first pass has `fade_transform_mismatches=True`, so differently-shaped parts transition with `FadeTransformPieces`; after the label is swapped, the second pass uses the default behaviour, where differently-shaped parts fade out and the new parts fade in directly. Put the two side by side to see the parameter difference.

<video src="assets/RTM output/01-Matching-Transforms-tex.mp4" controls width="560"></video>

> Note:
>
> - `TransformMatchingShapes` / `TransformMatchingTex` are imported from `real_time_manim.vulkan_bind` (RTM's own implementation, see the fix record at the top).
> - The keys in `key_map` must be computed on the spot with `Class.get_mobject_key(part)`, e.g. `TransformMatchingShapes.get_mobject_key(src3[0])`; remember to pair source key with target key and do not write the direction backwards.
> - Remember to `self.add` the source object into the scene first: the source is removed when finished and the target takes over.

### `TransformMatchingAbstractBase` (abstract base class)

```python
TransformMatchingAbstractBase(mobject, target_mobject, transform_mismatches=False,
                              fade_transform_mismatches=False, key_map=None, **kwargs)
```

The **abstract base class** of the two classes above; it defines two static hooks: `get_mobject_parts` (split parts) and `get_mobject_key` (compute keys). Instantiating it directly makes the hook calls `raise NotImplementedError`; you only need to subclass it to customize "match by text content / by a custom attribute".

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | source |
| `target_mobject` | `Mobject` | — | target |
| `transform_mismatches` | `bool` | `False` | whether unmatched parts are forcibly `Transform`ed |
| `fade_transform_mismatches` | `bool` | `False` | whether unmatched parts use `FadeTransformPieces` |
| `key_map` | `dict \| None` | `None` | manual key pairing `{source key: target key}` |
| `**kwargs` | … | — | internal sub-transform parameters and the `Animation` common parameters |

> **Returns**: a base-class instance (**cannot be played directly**).
>
> **Rules for handling unmatched parts** (shared by the three classes):
>
> - `transform_mismatches=True` → use `Transform`;
> - `fade_transform_mismatches=True` → use `FadeTransformPieces`;
> - both `False` (default) → source parts `FadeOut` toward the target and target parts `FadeIn` toward the source.
>
> To customize matching, subclass it and implement the two hooks (the manual's example `MatchByColor` uses `submobjects` + `str(get_color())` as the key).

### `TransformMatchingStrings` (the "match by string" mentioned in the manual)

The ability to match by string content is already covered by `TransformMatchingTex` (by `tex_string`). Importing it directly has been measured to raise:

```text
ImportError: cannot import name 'TransformMatchingStrings' from 'manim'
(C:\...\Lib\site-packages\manim\__init__.py). Did you mean: 'TransformMatchingShapes'?
```

Not demonstrable: `TransformMatchingAbstractBase` is an abstract base class (`get_mobject_key` directly `raise NotImplementedError`) and cannot be played directly; custom matching (such as by color) requires subclassing it and implementing the two hooks. `TransformMatchingStrings` does not exist in either current engine (see the subsection above and the raw error).

---

See also: [Create and the drawing family](../Creation-and-Removal/01-Create-and-the-Drawing-Family.md) · [Writing and Unwriting](../Text-and-Numbers/01-Writing-and-Unwriting.md)
