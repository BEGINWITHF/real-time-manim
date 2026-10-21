# Construction, containers, and add/remove (advanced)

Family-tree traversal, bulk attribute setting and construction hooks — APIs you only reach for when writing custom subclasses or utility functions; ordinary animation scripts just need to know they exist.

## Parameters

### get_family / family_members_with_points / split

```python
def get_family(recurse: bool = True) -> list[Mobject]
def family_members_with_points() -> list[Mobject]
def split() -> list[Mobject]
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `recurse` | `bool` | `True` | kept only for signature parity with the OpenGL version; any value behaves the same |
| (the other two take no arguments) | — | — | — |

> **Returns**: `get_family` gives a flat list of **self + all descendants** (depth-first, de-duplicated); `family_members_with_points` keeps only objects that **actually own vertices** (containers themselves and empty groups are dropped); `split` gives "self (if it has points) + **direct** children", the basis of indexing and iteration.

#### Sample: three family-tree traversals

An outer `Group` holds a two-square `VGroup`, an empty `Group` and a standalone square: what each of the three traversals returns is plain to see, and finally each object from `family_members_with_points` is colored — only the three real squares get colored.

```python
from real_time_manim import Scene, Group, VGroup, Square, \
    RED, BLUE, GREEN, ORANGE, YELLOW, PURPLE, RIGHT, UP, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class FamilyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        inner = VGroup(Square(color=RED, side_length=1.0), Square(color=BLUE, side_length=1.0))   # inner layer: two squares
        inner.arrange(RIGHT, buff=0.4)   # line up the inner layer
        empty = Group()   # empty container: not a single vertex
        solo = Square(color=GREEN, side_length=1.0)   # standalone square
        outer = Group(inner, empty, solo)   # outer layer: the inner group, the empty group, one square
        inner.shift(LEFT * 2.2)   # put the inner group on the left (don't use arrange: the empty group is zero wide and they would squeeze together)
        solo.shift(RIGHT * 2.2)   # put the standalone square on the right
        outer.shift(UP * 1.0)   # lift the whole tree a little
        self.add(outer)   # add the whole tree to the scene
        print("get_family =", len(outer.get_family()), [type(m).__name__ for m in outer.get_family()])   # self + all descendants
        print("family_members_with_points =", [type(m).__name__ for m in outer.family_members_with_points()])   # only those owning vertices
        print("split =", [type(m).__name__ for m in outer.split()])   # self (if it has points) + direct children
        for i, m in enumerate(outer.family_members_with_points()):   # the objects shift/scale actually act on
            m.set_color([ORANGE, YELLOW, PURPLE][i])   # color them one by one: only the three squares get colored
        win.play(Wait(0.6))   # pause 0.6s
        win.close()   # close the RTM window
```

What this code does: it builds a three-level object tree (outer `Group` → inner `VGroup` of two squares + empty `Group` + standalone square), then prints the result of the three traversals once it is on screen:

- `get_family` flattens the whole tree (including every container itself).
- `family_members_with_points` leaves only the three squares that own vertices.
- `split` sees only one level.

Finally the three squares are colored orange, yellow and purple in the order of `family_members_with_points` — the ones that change color on screen are exactly the three that "really own geometric data".

<video src="assets/RTM output/01b-Construction-and-Containers-Advanced-family.mp4" controls width="560"></video>

> Note: the set of objects that geometric transforms such as `shift` / `scale` / `rotate` actually act on is `family_members_with_points()`, so empty containers are not stretched, and text moves as a whole while its glyph point set follows. The `recurse` argument of `get_family` is decorative (only the OpenGL version uses it); don't expect passing `False` to give you just one level.

### has_points / has_no_points / get_num_points

```python
def has_points() -> bool
def has_no_points() -> bool
def get_num_points() -> int
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| (all take no arguments) | — | — | an empty container (a freshly built `Group`) has 0 points; geometric objects such as `Square` own vertices; `Text` itself has 0 points — they all live in its glyph children |

> **Returns**: `has_points` / `has_no_points` return `bool`, `get_num_points` returns `int`.

#### Sample: point counts of an empty container / a square / text

Each of three objects has its point count queried: the empty `Group` is all "empty", `Square` owns 16 vertices, and `Text` itself has 0 points with the points spread across its glyph children.

```python
from real_time_manim import Scene, Group, Square, Text, \
    BLUE, YELLOW, LEFT, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class PointsDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        g = Group()   # empty container
        sq = Square(color=BLUE, side_length=1.6)   # a square with vertices
        txt = Text("points", font_size=36, color=YELLOW)   # text: the points live in its glyph children
        sq.shift(LEFT * 3.2)   # put the square on the left
        txt.shift(RIGHT * 2.4)   # put the text on the right
        self.add(sq, txt)   # add both objects to the scene
        print("empty Group: has_points =", g.has_points(), "has_no_points =", g.has_no_points(), "get_num_points =", g.get_num_points())   # all "empty"
        print("Square: has_points =", sq.has_points(), "get_num_points =", sq.get_num_points())   # the square owns vertices
        print("Text itself get_num_points =", txt.get_num_points(), "| glyphs =", [m.get_num_points() for m in txt.submobjects])   # the points are in the glyphs
        win.play(FadeIn(sq), FadeIn(txt), run_time=0.5)   # fade in both objects
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: it queries the point counts of the empty `Group`, the `Square` and `Text("points")` and prints them to the console — the empty group is `has_points=False` / `has_no_points=True` / count 0; the square's count is 16 (shape sample points); the text **itself** has 0 points, and only each letter's glyph child owns vertices. The square and text fade in on screen so you can line the console numbers up with the objects.

<video src="assets/RTM output/01b-Construction-and-Containers-Advanced-points.mp4" controls width="560"></video>

> Note: to count the total vertices of a complex object, use `get_all_points().shape[0]` (see [03-Measurement](03-Measurement.md)) rather than calling `get_num_points` directly on `Text` — the latter only tells you 0. These three methods are pure queries and change no state.

### set

```python
def set(**kwargs: Any) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `**kwargs` | any | — | "attribute name=value" pairs, equivalent to writing `mob.foo = v` one by one; **accepts** attributes that really exist on the object, such as `width=`, `color=`, `fill_opacity=` |

> **Returns**: `self`, chainable. Mainly used with `.animate` (see [07-animate-Syntax](07-animate-Syntax.md)): `win.play(rect.animate.set(width=7))`. The legacy `mob.get_foo()` / `mob.set_foo(v)` still work but emit a `DeprecationWarning`; prefer attribute access or `set`.

#### Sample: `set` with `.animate`

`rect.animate.set(width=..., color=...)` changes several attributes at once and plays a transition; a `set` without `animate` changes instantly; then the legacy `set_width` shows the `DeprecationWarning`.

```python
import warnings

from real_time_manim import Scene, Rectangle, \
    BLUE, ORANGE
from real_time_manim.vulkan_bind import MLWindow, Wait

class SetDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        rect = Rectangle(width=3.0, height=1.4, color=BLUE, fill_opacity=0.6)   # a rectangle
        self.add(rect)   # add it to the scene
        win.play(rect.animate.set(width=5.0, color=ORANGE), run_time=0.7)   # "set" with animate: change several attributes at once
        rect.set(fill_opacity=1.0)   # without "animate" the change is instant
        print("rect.width =", rect.width, "| rect.color =", rect.color)   # verify by reading the attributes back
        with warnings.catch_warnings(record=True) as w:   # the legacy get_foo / set_foo emits a warning
            warnings.simplefilter("always")
            rect.set_width(4.0)   # legacy style: works but emits a DeprecationWarning
            print("legacy warning =", [str(x.message)[:24] for x in w])   # peek at the warning text
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: a translucent blue rectangle goes on screen. `rect.animate.set(width=5.0, color=ORANGE)` combines "get wider" and "turn orange" into **one** transition animation; then `rect.set(fill_opacity=1.0)` without `animate` is a direct assignment that takes effect instantly. The console prints the read-back `width` / `color` to verify the change. Finally the legacy `rect.set_width(4.0)` changes the width once, and the `DeprecationWarning` text it emits is captured and printed.

<video src="assets/RTM output/01b-Construction-and-Containers-Advanced-set.mp4" controls width="560"></video>

> Note: the attributes in `.animate.set(...)` must be interpolable between the start and end state (numbers and colors are fine); a string attribute can only jump instantly. `set` does no validity checking, so a misspelled attribute name is just an ordinary dynamic assignment — no reaction on screen and no error to trace. If you are unsure whether an attribute exists, run `dir(mob)` for a look.

### set_default (classmethod)

```python
def set_default(**kwargs: Any) -> None
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `**kwargs` | any | — | `__init__` keyword arguments to override, e.g. `side_length=1.0` |

> **Returns**: `None`. Changes the default for subsequent constructions of **that class**; affects only objects created afterwards, never existing ones. Calling with no arguments **restores the original defaults**.

#### Sample: `set_default` changing the default side length

Build a square → change `Square`'s default side length to 1 and color to yellow → build another (using the new defaults) → call with no arguments to restore → build one more; the three squares line up in a row for comparison.

```python
from real_time_manim import Scene, VGroup, Square, \
    YELLOW, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class SetDefaultDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        before = Square()   # default square: side length 2, white
        Square.set_default(side_length=1.0, color=YELLOW)   # change "Square"'s default side length to 1 and default color to yellow
        after = Square()   # the new object uses the new defaults
        Square.set_default()   # called with no arguments: restore the original defaults
        back = Square()   # build one more: back to the defaults
        trio = VGroup(before, after, back)   # the three squares as one group
        trio.arrange(RIGHT, buff=0.8)   # line them up so the size difference is plain
        self.add(trio)   # add them to the scene
        print("side length:", before.width, after.width, back.width)   # 2.0 1.0 2.0
        win.play(FadeIn(trio), run_time=0.6)   # fade in the whole group
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: a white square is built from the defaults first (`Square`'s default side length is **2**), then `Square.set_default(side_length=1.0, color=YELLOW)` changes `Square`'s construction defaults, and the square built right after is a small yellow one. Calling `Square.set_default()` with no arguments restores the original defaults in one go, and the third square is back to a big white one. The three squares line up in a row and fade in, and the console prints side lengths `2.0 1.0 2.0` — already-built objects are unaffected, only those built afterwards use the new defaults.

<video src="assets/RTM output/01b-Construction-and-Containers-Advanced-set_default.mp4" controls width="560"></video>

> Note:
>
> - `set_default` is a **class-level global change** and keeps affecting all later code; remember to restore it with `set_default()` or pass the old values back manually.
> - It has no effect on existing objects; to change existing objects in bulk use an instance method such as `set` or `set_color`.
> - `Square`'s default side length is 2, not 1; don't lay out with an assumed size.

### reset_points / generate_points / init_colors

```python
def reset_points() -> Self
def generate_points() -> Self
def init_colors(propagate_colors: bool = True) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `propagate_colors` | `bool` | `True` | `init_colors` only: whether to push the color down the family |

> **Returns**: all return `self`. These are the three hooks called in order inside the constructor: clear `points` → generate the shape → initialize the style from `color`. **You only need to override them when writing a custom `Mobject` subclass**; ordinary scripts never call them.

#### Sample: a custom subclass and the three hooks

A custom `WideCircle` overrides `generate_points` to stretch a circle into a wide ellipse; a plain circle for comparison is manually taken through "clear → regenerate → recolor", watching it disappear and reappear at the origin.

```python
from real_time_manim import Scene, VGroup, Circle, \
    GREEN, BLUE, DOWN, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class WideCircle(Circle):   # custom subclass: change the shape in a construction hook
    def generate_points(self):   # the constructor calls this to generate the shape
        super().generate_points()   # first generate "Circle"'s default shape
        self.stretch(1.6, 0)   # then stretch it horizontally into a "wide ellipse"


class HooksDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        wc = WideCircle(radius=0.9, color=GREEN)   # custom subclass: stretched after generation
        c = Circle(radius=0.9, color=BLUE)   # a plain circle for comparison
        duo = VGroup(wc, c)   # the two circles as one group
        duo.arrange(DOWN, buff=0.6)   # stack them vertically
        self.add(duo)   # add them to the scene
        win.play(FadeIn(duo), run_time=0.5)   # fade in: the wide ellipse is on top
        c.reset_points()   # clear all vertices: the circle disappears
        win.play(Wait(0.5))   # pause 0.5s to see it disappear
        c.generate_points()   # regenerate the shape: the default circle reappears at the origin
        c.init_colors()   # re-initialize the style from "color"
        win.play(Wait(0.5))   # pause 0.5s to see the result
        win.close()   # close the RTM window
```

What this code does: the custom `WideCircle` overrides `generate_points`, generating the default circle first and then stretching it 1.6× horizontally, so the upper one on screen is a wide ellipse and the lower plain circle is the comparison. The three hooks are then called on the plain circle in order:

- `reset_points()` clears the vertices (the circle vanishes on the spot).
- `generate_points()` regenerates the shape.
- `init_colors()` recolors it from `color`.

The circle reappears at the **origin** (`generate_points` generates a shape around the origin and does not remember the old position).

<video src="assets/RTM output/01b-Construction-and-Containers-Advanced-hooks.mp4" controls width="560"></video>

> Note: `generate_points` only works where a subclass **really overrides** it: `Circle` / `Arc` generate their shape in a hook, so both overriding and re-calling work; `Square` / `Triangle` / `Polygon` set their points directly in `__init__`, and the base class's `generate_points` is a no-op, so calling `reset_points()` and then `generate_points()` on them will **not** bring the shape back (measured on 0.21). Also, a regenerated shape sits at the origin and its vertex layout may change; to keep position and style, add `move_to` / `init_colors` yourself.

---

See also: [Construction and Containers](01-Construction-and-Containers.md) · [Style and Color](05-Style-and-Color.md)
