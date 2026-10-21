# Style and Color (Mobject level)

The style entry points that `Mobject` itself provides; `set_fill` / `set_stroke` / `set_opacity` are defined on `VMobject`, see [04 Shapes and Text](../04-Shapes-and-Text/07-VMobject-Styles.md). All the methods below return `self`.

## Parameters

### set_color

```python
def set_color(color: ParsableManimColor = PURE_YELLOW, alpha: Any = None,
              family: bool = True) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | color string / `ManimColor` | `PURE_YELLOW` | **you can pass** `"red"`, `"#ff0000"`, `RED`, `ManimColor("#83c167")` |
| `alpha` | any | `None` | only exists in the `Mobject` base-class signature; `VMobject.set_color` **has no such parameter**, so passing it to a vector object raises `TypeError` outright |
| `family` | `bool` | `True` | `False` changes only its own attributes and does **not recurse** into submobjects |

> **Returns**: self. By default it recurses into all submobjects; `color=` also updates `self.color` (which the later `to_original_color` uses to reset).

#### Sample: `set_color`'s `family`

A small yellow square (a submobject) nested inside a big blue square: `set_color(ORANGE)` by default changes the whole group including submobjects; `set_color(GREEN, family=False)` changes only the group's own attributes — the submobject stays orange (the group itself is not drawn, so the picture does not change).

```python
from real_time_manim import Scene, Group, Square, \
    BLUE, YELLOW, ORANGE, GREEN
from real_time_manim.vulkan_bind import MLWindow, Wait

class SetColorDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=2.2, fill_opacity=0.7)   #blue square
        kid = Square(color=YELLOW, side_length=0.8, fill_opacity=0.9)   #small yellow square
        g = Group(sq, kid)   #put the small square into the group as a submobject
        self.add(g)   #add to the scene
        win.play(g.animate.set_color(ORANGE), run_time=0.6)   #default family=True: change the whole group including submobjects
        win.play(g.animate.set_color(GREEN, family=False), run_time=0.6)   #family=False: change only the group's own attributes
        print("sq =", sq.get_color(), "| kid =", kid.get_color())   #the submobject stays orange: family=False does not propagate down
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: with a "big square around a small square", the first `set_color(ORANGE)` uses the default `family=True` and the whole group turns orange from blue (the small square too); the second `set_color(GREEN, family=False)` only turns the `Group`'s own color attribute green — but the container itself is not drawn, so neither square moves on screen, and the console prints `sq = #FF862F | kid = #FF862F`, proving the submobject stayed orange and the `family=False` change did not propagate down.

<video src="assets/RTM output/05-Style-and-Color-set_color.mp4" controls width="560"></video>

> Note: the `alpha` parameter exists only in the `Mobject` base-class signature, `VMobject.set_color` **has none** — passing `set_color(RED, alpha=0.5)` to a square raises `TypeError` outright (tested on 0.21). To change opacity, use `set_fill(opacity=...)` / `fade_to`. Using `family=False` on a container (`Group`) is basically no change at all — what you changed is not part of the drawing.

### set_color_by_gradient / set_submobject_colors_by_gradient / radial gradients

```python
def set_color_by_gradient(*colors: ParsableManimColor) -> Self
def set_submobject_colors_by_gradient(*colors: ParsableManimColor) -> Self
def set_colors_by_radial_gradient(center: Point3DLike | None = None, radius: float = 1,
                                  inner_color: ParsableManimColor = WHITE,
                                  outer_color: ParsableManimColor = BLACK) -> Self
def set_submobject_colors_by_radial_gradient(center=None, radius=1,
                                             inner_color=WHITE, outer_color=BLACK) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*colors` | colors | — | the end colors of the linear gradient, at least 1, usually 2–3 |
| `center` | point or `None` | `None` | the gradient's centre; `None` uses its own centre (radial only) |
| `radius` | `float` | `1` | the distance at which the outer color is reached (radial only) |
| `inner_color` / `outer_color` | colors | `WHITE` / `BLACK` | the inner / outer color of the radial gradient |

> **Returns**: self. Both `set_*` versions distribute solid colors among the **descendants that have vertices**, by order or by distance — the color is **per-object**, not a true gradient inside a single shape. `set_color_by_gradient` internally calls `set_submobject_colors_by_gradient`; likewise for the two radial methods.

#### Sample: linear and radial gradients

Four rows of small shapes, one method each: linear gradient (blue→red, green→purple) and radial gradient (white inside / blue outside, yellow inside / red outside) — each row takes its colors from the submobjects' order or distance from the centre.

```python
from real_time_manim import Scene, VGroup, Square, Circle, \
    BLUE, RED, GREEN, PURPLE, WHITE, YELLOW, UP, DOWN, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class GradientDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        r1 = VGroup(*[Square(side_length=0.8) for _ in range(4)])   #a row of four squares
        r1.arrange(RIGHT, buff=0.25).shift(UP * 2.2)
        self.add(r1)   #add to the scene
        win.play(r1.animate.set_color_by_gradient(BLUE, RED), run_time=0.5)   #gradient across the group: the four squares take the in-between colors in turn
        r2 = VGroup(*[Square(side_length=0.8) for _ in range(4)])   #second row
        r2.arrange(RIGHT, buff=0.25).shift(UP * 0.7)
        self.add(r2)   #add to the scene
        win.play(r2.animate.set_submobject_colors_by_gradient(GREEN, PURPLE), run_time=0.5)   #color the submobjects one by one directly (an equivalent implementation)
        r3 = VGroup(*[Circle(radius=0.2 + 0.15 * i) for i in range(3)])   #third row: circles of different sizes
        r3.arrange(RIGHT, buff=0.35).shift(DOWN * 1.0)
        self.add(r3)   #add to the scene
        win.play(r3.animate.set_colors_by_radial_gradient(radius=1.6, inner_color=WHITE, outer_color=BLUE), run_time=0.5)   #radial: colors taken by distance from the centre
        r4 = VGroup(*[Circle(radius=0.2 + 0.15 * i) for i in range(3)])   #fourth row
        r4.arrange(RIGHT, buff=0.35).shift(DOWN * 2.4)
        self.add(r4)   #add to the scene
        win.play(r4.animate.set_submobject_colors_by_radial_gradient(radius=1.6, inner_color=YELLOW, outer_color=RED), run_time=0.5)   #same as above
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: four rows of small shapes demonstrate the gradient quartet. The first row of four squares `set_color_by_gradient(BLUE, RED)` takes the in-between colors from blue to red left to right (measured `#58C4DD → #8EA3AF → #C58282 → #FC6255`); the second row uses `set_submobject_colors_by_gradient` for exactly the same result — the former internally calls the latter. The third row of three differently sized circles uses `set_colors_by_radial_gradient`, taking colors between white inside and blue outside by each submobject's **distance from the centre** (the middle circle is the whitest); the fourth row is the matching `set_submobject_colors_by_radial_gradient` version, yellow inside and red outside.

<video src="assets/RTM output/05-Style-and-Color-gradient.mp4" controls width="560"></video>

> Note: this distributes solid colors **per submobject**, not a true gradient inside a single shape — with only one submobject in the group you see a single solid color. To make a gradient **inside one shape**, use something beyond `set_fill(color1, opacity).set_style(...)` (a `VMobject`'s per-vertex colors) or switch to a texture/pattern fill; the `Mobject` layer provides none of this. `radius` / `center` only matter for the radial versions.

### fade_to / fade

```python
def fade_to(color: ParsableManimColor, alpha: float, family: bool = True) -> Self
def fade(darkness: float = 0.5, family: bool = True) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | color | — | target color (`fade_to` only) |
| `alpha` | `float` | — | blend ratio 0–1 (`fade_to` only) |
| `darkness` | `float` | `0.5` | how much darker / fainter (`fade` only) |
| `family` | `bool` | `True` | whether to recurse into submobjects |

> **Returns**: self. `fade_to` blends the color toward the target by the ratio `alpha` (`alpha=0.7` = seven tenths the new color); `fade`'s real logic lives in `VMobject.fade` — **it changes opacity, not color** — and works on vector objects but not on a bare `Mobject`.

#### Sample: `fade_to` blending and `fade` fading

Two blue squares: the left one's `fade_to(RED, 0.7)` blends it toward red; the right one's `fade(darkness=0.6)` fades it (`get_color` is still blue).

```python
from real_time_manim import Scene, Square, \
    BLUE, RED, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class FadeDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        f1 = Square(color=BLUE, side_length=1.4, fill_opacity=0.8).shift(LEFT * 2.5)   #left: blend colors
        f2 = Square(color=BLUE, side_length=1.4, fill_opacity=0.8).shift(RIGHT * 2.5)   #right: fade
        self.add(f1, f2)   #add to the scene
        win.play(f1.animate.fade_to(RED, 0.7), run_time=0.6)   #blend 70% toward red
        win.play(f2.animate.fade(darkness=0.6), run_time=0.6)   #fade the vector object by 60%
        print("f1 =", f1.get_color(), "| f2 =", f2.get_color())   #verify by reading the colors
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: two identical blue squares, one method each. The left one's `fade_to(RED, 0.7)` blends the color 70% toward red, printing `#CA7F7D` (about seven parts red, three parts blue); the right one's `fade(darkness=0.6)` visibly fades the square, but `get_color` still reads **blue** `#58C4DD` — because `VMobject.fade` adjusts the opacity channel and leaves the color attribute alone.

<video src="assets/RTM output/05-Style-and-Color-fade.mp4" controls width="560"></video>

> Note: `fade_to` changes color while `fade` changes opacity — they are not symmetric, so don't mix them up; for a fade-out animation use `FadeOut` directly. The larger `darkness` is, the fainter (`1.0` = gone completely); for a bare `Mobject` with no notion of fill/stroke color, `fade` is a no-op.

### get_color / match_color / to_original_color

```python
def get_color() -> ManimColor
def match_color(mobject: Mobject) -> Self
def to_original_color() -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | the reference object (`match_color` only) |

> **Returns**: `get_color` returns a `ManimColor`, the other two return self. `match_color` sets both `self.color` and the color to the reference object's (**the old `self.color` is overwritten too**); `to_original_color` pushes `self.color` back down over the whole family — its real use is clearing the **per-submobject** colors of objects like `Text`.

#### Sample: reading, copying and clearing submobject colors

A red square `match_color`s the green square's color; a white text has only its first two letters colored red, and `to_original_color()` clears the glyphs' individual colors in one go.

```python
from real_time_manim import Scene, Square, Text, \
    RED, GREEN, WHITE, UP, DOWN, LEFT, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class GetMatchDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        a = Square(color=RED, side_length=1.4).shift(LEFT * 3.0 + UP * 1.2)   #red square
        b = Square(color=GREEN, side_length=1.4).shift(RIGHT * 3.0 + UP * 1.2)   #green square
        self.add(a, b)   #add to the scene
        print("a =", a.get_color())   #read the current color
        win.play(a.animate.match_color(b), run_time=0.6)   #set a's color to b's
        print("after match: a =", a.get_color(), "b =", b.get_color())
        w = Text("color", font_size=38, color=WHITE).shift(DOWN * 1.6)   #white text: the glyphs can be colored individually
        w[0:2].set_color(RED)   #color only the first two letters red
        self.add(w)   #add to the scene
        win.play(FadeIn(w), run_time=0.4)   #fade the text in
        win.play(Wait(0.5))   #see that the first two letters are red
        w.to_original_color()   #reset to self.color across the board: the glyphs' individual colors are cleared
        print("after reset w =", w.get_color())   #the attribute prints black (Text's color defaults to black)
        win.play(Wait(0.5))   #see that all the glyphs are restored
        win.close()   #close the RTM window
```

What this code does: in the top row the red square first reads its own color as red (`#FC6255`) with `get_color()`, and after `match_color(b)` it matches the green square (`#83C167`). Note that this step overwrites `a`'s `self.color` too, so a later `to_original_color()` will not turn it red again.

The bottom row shows `to_original_color`'s real use: a white text has only its first two letters colored red (the glyphs are submobjects with their own colors), and `to_original_color()` resets all glyphs to the overall color in one go — the red "co" on screen turns back to white and the whole word becomes consistent again. The `self.color` printed to the console is `#000000` (the `Text`'s `color` attribute defaults to black, which is a different thing from the glyphs being drawn white; the glyphs' actual color is managed by the `Text`'s own `font_color`).

<video src="assets/RTM output/05-Style-and-Color-get_match.mp4" controls width="560"></video>

> Note: after `match_color`, don't count on `to_original_color` restoring the old color — the original was overwritten; to restore it, `save_state()` first (see [Copying, Deriving and State](06-Copying-Deriving-and-State.md)). `to_original_color` is for cases like "I colored some of a `Text` / `MathTex` glyphs and want to revert them in one click".

### set_z_index / set_z_index_by_z_Point3D

```python
def set_z_index(z_index_value: float, family: bool = True) -> Self
def set_z_index_by_z_Point3D() -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `z_index_value` | `float` | — | any number; larger is higher up |
| `family` | `bool` | `True` | whether to set all submobjects at the same time |

> **Returns**: self. **The render order is decided by `z_index`, regardless of the order of `add`** (only equal `z_index` values fall back to insertion order); the latter sets `z_index` to the **centre's z coordinate**, for far/near occlusion in 3D scenes.

#### Sample: `set_z_index` reverses the stacking

Two overlapping red and blue squares: by default the blue one added later is on top; after `zA.set_z_index(2)` the red one overtakes it; then `set_z(3.0)` on the blue one followed by `set_z_index_by_z_Point3D()` sets its level to 3 from its z coordinate, and it covers the red one again.

```python
from real_time_manim import Scene, Square, \
    RED, BLUE, LEFT
from real_time_manim.vulkan_bind import MLWindow, Wait

class ZIndexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        zA = Square(color=RED, side_length=2.2, fill_opacity=0.85).shift(LEFT * 2.2)   #red square
        zB = Square(color=BLUE, side_length=2.2, fill_opacity=0.85).shift(LEFT * 1.3)   #blue square
        self.add(zA, zB)   #the blue one added later is on top (equal levels fall back to insertion order)
        win.play(Wait(0.5))   #look at the default stacking first
        zA.set_z_index(2)   #set the red level to 2: it overtakes to the upper layer instantly
        win.play(Wait(0.5))   #pause to see the red cover the blue
        zB.set_z(3.0)   #give the blue one a z coordinate (no visible position change on a 2D canvas)
        zB.set_z_index_by_z_Point3D()   #blue level = centre z coordinate = 3: it covers again
        print("z_index:", zA.z_index, zB.z_index)   #2 3
        win.play(Wait(0.5))   #pause to see the blue cover the red
        win.close()   #close the RTM window
```

What this code does: two semi-transparent squares overlap with an offset; the first `Wait` shows the default rule — both `z_index` are 0, and **the blue one added later is on top**; then `zA.set_z_index(2)` instantly raises the red one's level to 2, and in the next stretch of the picture the red one overtakes and covers the blue; finally the blue one gets `set_z(3.0)` for a z coordinate (no visible position change on a 2D canvas), and `set_z_index_by_z_Point3D()` sets its `z_index` to the centre z=3, so the blue covers it again. The console prints `z_index: 2 3.0`.

<video src="assets/RTM output/05-Style-and-Color-z_index.mp4" controls width="560"></video>

> Note:
>
> - `set_z_index` changes the level **instantly**, with no transition; for a gradual level change write your own updater.
> - Only when two objects share the same `z_index` does the `add` order matter, so "the later one is on top" is just a coincidence of equal defaults.
> - `set_z_index_by_z_Point3D` is only meaningful in a 3D scene (in 2D every z is 0).

### add_background_rectangle (and the two recursive variants)

```python
def add_background_rectangle(color: ParsableManimColor | None = None,
                             opacity: float = 0.75, **kwargs: Any) -> Self
def add_background_rectangle_to_submobjects(**kwargs: Any) -> Self
def add_background_rectangle_to_family_members_with_points(**kwargs: Any) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | color or `None` | `None` | background color |
| `opacity` | `float` | `0.75` | background opacity |
| `**kwargs` | `Any` | — | passed through to `BackgroundRectangle` (the two latter variants take this set directly) |

> **Returns**: self. The backing rectangle is added to the submobject list (drawn underneath), making text/shapes easier to read on a busy background. The three versions are: back yourself with one / back each direct submobject with its own / back every member of the family that has vertices with its own.

#### Sample: backdrops for text and shapes

White text on a striped background: one block behind the whole word via `add_background_rectangle`; the letters `A B` each get their own via variant two; the two circles each get their own via variant three — everything on the busy background is readable.

```python
from real_time_manim import Scene, VGroup, Square, Circle, Text, Rectangle, \
    RED, BLUE, GREEN, WHITE, BLACK, UP, DOWN, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class BgRectDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim window named "self" to the RTM window named "win"
        bg = VGroup(*[Rectangle(width=2.0, height=6.0, color=c, fill_opacity=1.0) for c in (RED, BLUE, GREEN)])   #three colored vertical bars
        bg.arrange(RIGHT, buff=0)
        self.add(bg)   #busy background
        txt = Text("READABLE", font_size=44, color=WHITE).shift(UP * 1.6)   #white text
        txt.add_background_rectangle(color=BLACK, opacity=0.75)   #put a semi-transparent black block behind it
        self.add(txt)
        win.play(FadeIn(bg), FadeIn(txt), run_time=0.6)   #fade in the background and the text together
        duo = VGroup(Text("A", font_size=36), Text("B", font_size=36)).arrange(RIGHT, buff=0.9)
        duo.shift(UP * 0.1)
        duo.add_background_rectangle_to_submobjects(color=BLACK, opacity=0.7)   #give each letter its own block
        self.add(duo)
        rings = VGroup(Circle(radius=0.35), Circle(radius=0.35)).arrange(RIGHT, buff=0.4).shift(DOWN * 1.8)
        rings.add_background_rectangle_to_family_members_with_points(color=BLACK, opacity=0.7)   #give each member with vertices its own block
        self.add(rings)
        win.play(FadeIn(duo), FadeIn(rings), run_time=0.5)   #fade in the two groups
        win.play(Wait(0.4))   #wait 0.4s
        win.close()   #close the RTM window
```

What this code does: three red, blue and green vertical bars are laid down as a "busy background", then the white text `READABLE` goes on top — it has a semi-transparent black block behind it (`add_background_rectangle`), so the parts crossing the bright stripes are still clearly readable; the `A B` in the middle uses variant two, with a block behind **each letter**; the two circles at the bottom use variant three, backing every member of the family that has vertices. All three ways are shown at once, and each has the effect of "a dark backdrop making the foreground pop out".

<video src="assets/RTM output/05-Style-and-Color-background.mp4" controls width="560"></video>

> Note: the backing rectangle is **a submobject of the object** and moves/scales with it; backing a whole `Text` makes the rectangle wrap **all the glyphs**, so to back only some colored letters, slice the glyphs and use variant two. `opacity` defaults to 0.75, which may look too dark on a solid background — lower it as needed.

---

See also: [Construction and Containers](01-Construction-and-Containers.md) | [animate Syntax](07-animate-Syntax.md)
