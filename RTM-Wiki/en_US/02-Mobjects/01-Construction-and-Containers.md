# Construction, containers, and add/remove

`Mobject` is the base class of every visible object. This page covers its constructor parameters, the `Group` container, and adding, removing and index-accessing children — four entry points no animation script can avoid.

## Parameters

### class Mobject

```python
def __init__(self, color: ParsableManimColor | list[ParsableManimColor] = WHITE,
             name: str | None = None, dim: int = 3,
             target: Mobject | None = None, z_index: float = 0) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `color` | color string / `ManimColor` / color list | `WHITE` | object color. **Accepts**: `"red"`, `"#ff0000"`, `RED`, `ManimColor("#83c167")`; also takes a list of colors (some subclasses color each child from the list). Subclasses consume it in `init_colors()` to set up stroke and fill |
| `name` | `str \| None` | `None` | object name. **Accepts** any string; defaults to the class name (e.g. `Square`); affects only debug output such as `repr`, so change it freely |
| `dim` | `int` | `3` | dimension of the vertex coordinates. **Do not change**: in practice only `3` works; any other value makes the point-array dimension mismatch. A purely internal parameter of custom subclasses |
| `target` | `Mobject \| None` | `None` | the `.target` cache slot. **Do not set manually**: it is filled by `generate_target()` (see [06-Copying-Deriving-and-State](06-Copying-Deriving-and-State.md)); forcing a value easily fights `MoveToTarget` |
| `z_index` | `float` | `0` | render paint order. **Accepts** any number, larger sits higher; unrelated to `add` order (only equal `z_index` falls back to add order) |

> **Returns**: none (constructs an instance). These 5 parameters are passed through `**kwargs` unchanged by every subclass (`Square`, `Text`, `Circle`, …), so you can write them in the constructor of **any** subclass.

#### Sample: changing `color` / `name` / `z_index`

Two same-sized squares offset to overlap: the one added to the scene later is blue, but red has the larger `z_index=2`, so at the overlap red always sits on top of blue — that is what `z_index` does. `name` does not change the frame, only the object name in console output. `dim` / `target` are internal parameters; the sample just prints their current values for a look.

```python
from real_time_manim import Scene, Square, \
    BLUE, RED, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class CtorDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        front = Square(color=RED, side_length=2.4, fill_opacity=0.8, name="hero", z_index=2)   # name "hero", layer 2
        back = Square(color=BLUE, side_length=2.4, fill_opacity=0.8)   # everything else default: name taken from the class, z_index=0
        back.shift(RIGHT * 1.2)   # offset it right a little so the two squares overlap
        self.add(front, back)   # "front" added before "back", but the higher layer still shows on top
        print("color =", back.color, "| name =", back.name, "| dim =", back.dim)   # color, name, vertex-coordinate dimension
        print("target =", front.target, "| z_index =", front.z_index, back.z_index)   # the target cache is empty by default
        win.play(FadeIn(front), FadeIn(back), run_time=0.6)   # fade in both squares together
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: it first opens an RTM window and binds the scene to it, then makes two identical squares — the red one is called `hero` with layer 2, the blue one passes nothing and takes all defaults. The blue one is offset 1.2 to the right so they overlap, then both are added to the scene "red first, blue second".

The console prints the actual values of the constructor parameters `color` / `name` / `dim` / `target` / `z_index`. On the frame you can see that although blue was added to the scene later, it does **not** cover red at the overlap — because the larger `z_index` renders on top.

<video src="assets/RTM output/01-Construction-and-Containers-ctor.mp4" controls width="560"></video>

> Note:
>
> - `Square` has only a stroke and no fill by default; the sample explicitly passes `fill_opacity=0.8`, otherwise both squares would be hollow and you could not tell which covers which at the overlap.
> - `z_index` only falls back to add order when equal, so "the later `add` is on top" is just a coincidence of the default `z_index` all being 0.
> - Do not assign `target` by hand; it is `generate_target()`'s territory.

### class Group

```python
def Group(*mobjects: Mobject, **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*mobjects` | any `Mobject` | — | objects to put into the group; **accepts any type** (including non-purely-geometric ones such as `Text`, `ImageMobject`) |
| `**kwargs` | `Any` | — | forwarded to `Mobject.__init__`, so the 5 parameters of [the previous section](#class-mobject) (such as `color=`, `z_index=`) work here too |

> **Returns**: a new `Group`, with no methods of its own (it still uses the `Mobject` set). Difference from `VGroup`: `VGroup` accepts only vector objects (`VMobject` subclasses) and raises `TypeError` for anything else, while `Group` accepts everything. Adding the same object twice to a group is ignored (for two copies, call `.copy()` first).

#### Sample: `Group` mixing different types

A square, a text and a dot — three objects of different types — are put into one `Group`, then placed and faded in as a single object; the sample also shows that a duplicate add is ignored and that `VGroup` rejects non-vector objects.

```python
from real_time_manim import Scene, Mobject, Group, VGroup, Square, Circle, Text, Dot, \
    BLUE, YELLOW, GREEN, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class GroupDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        sq = Square(color=BLUE, side_length=1.2)   # square
        label = Text("G", font_size=48, color=YELLOW)   # text: a different class from the square
        dot = Dot(color=GREEN, radius=0.35)   # dot: yet another type
        g = Group(sq, label, dot, z_index=1)   # "Group" accepts any type; "z_index" forwards to Mobject
        g.arrange(RIGHT, buff=0.6)   # line the three children up in a row
        self.add(g)   # add the whole group to the scene
        print("len(g) =", len(g), "| type =", [type(m).__name__ for m in g])   # all three children are there
        g.add(sq)   # add the same object again: ignored, only one copy kept
        print("len(g) after duplicate add =", len(g))   # still 3
        try:
            VGroup(Mobject())   # "VGroup" accepts only vector objects
        except TypeError as exc:   # a bare "Mobject" has no vector data
            print("VGroup rejects non-vector objects ->", exc)
        win.play(FadeIn(g), run_time=0.6)   # fade in the whole group
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: it puts a square, the text `G` and a dot — three objects of different types — into one `Group`, lines them up in a row with `arrange`, then adds the whole group to the scene and fades it in as one. The console prints that the group holds 3 children and each one's type. Then the square is `add`ed once more — the group still holds only 3, the duplicate is ignored. Finally a bare `Mobject` is used to construct a `VGroup`, which raises `TypeError`, proving `VGroup` accepts only vector objects.

<video src="assets/RTM output/01-Construction-and-Containers-group.mp4" controls width="560"></video>

> Note: placement methods such as `Group.arrange` use each child's bounding box, so mixing text and geometric objects is fine; but slicing a `Group` (`g[1:3]`) also returns a `Group`, never a `VGroup`. To do vector-style operations such as `set_fill` on a whole group, a `VGroup` is handier.

### add / remove / add_to_back / insert

```python
def add(*mobjects: Mobject) -> Self
def remove(*mobjects: Mobject) -> Self
def add_to_back(*mobjects: Mobject) -> Self
def insert(index: int, mobject: Mobject) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | — | objects to add/remove (`add` / `remove` / `add_to_back`); `add` ignores duplicates and prints a warning, `remove` silently ignores missing objects |
| `index` | `int` | — | `insert` position; negatives follow Python list rules |
| `mobject` | `Mobject` | — | object for `insert` to insert |

> **Returns**: all return `self` for chaining. **Render order = `submobjects` list order**: the head of the list is drawn first (bottom), the tail last (covers).
>
> - `add` appends to the tail (on top).
> - `add_to_back` prepends to the head (at the bottom).
> - `insert` sets the position exactly.
>
> When the parent is already on the scene, newly added children appear automatically.

#### Sample: `add` / `remove` / `add_to_back` / `insert`

A red square and a blue disc repeatedly adjust their layering: appended to the tail it covers the square, `remove` takes it off leaving only the square, `add_to_back` prepends it to the head and it goes under the square, and `insert(1, ...)` puts it back at the tail.

```python
from real_time_manim import Scene, Group, Square, Circle, \
    RED, BLUE, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class AddRemoveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        box = Square(color=RED, side_length=2.6, fill_opacity=0.8)   # red square (with fill)
        disc = Circle(color=BLUE, radius=1.25, fill_opacity=0.8)   # blue disc (with fill)
        g = Group(box)   # put the square into a "Group" first
        g.add(disc)   # add: the disc appends to the tail, showing above the square
        self.add(g)   # add the whole group to the scene
        win.play(FadeIn(g), run_time=0.5)   # fade in: the disc covers the square's center
        g.remove(disc)   # remove: the disc leaves the group, only the square is left on screen
        win.play(Wait(0.4))   # pause 0.4s to see the result
        g.add_to_back(disc)   # add_to_back: the disc prepends to the head, showing below the square
        win.play(Wait(0.4))   # pause 0.4s to see the result
        g.remove(disc)   # take it off first: insert does not de-duplicate, an existing object gains a second reference
        g.insert(1, disc)   # insert: insert by index at the tail, the disc covers the square again
        win.play(Wait(0.4))   # pause 0.4s to see the result
        win.close()   # close the RTM window
```

What this code does: a red square and a blue disc go into a `Group`, and a few changes to the list order show how the layering changes.

- `add` appends the disc to the tail, it covers the square.
- `remove` takes it away, only the square is left on screen.
- `add_to_back` prepends it to the head, so it goes under the square (its center covered by the red square).
- Finally `remove` first and then `insert(1, disc)` inserts it by index at the tail, and the disc is back on top of the square.

The three `Wait`s each pause 0.4 seconds, just to let you see the result of each step.

<video src="assets/RTM output/01-Construction-and-Containers-add_remove.mp4" controls width="560"></video>

> Note:
>
> - These methods take effect **instantly**, with no transition animation; to give "adding in" a process, use an animation class such as `FadeIn` / `Write`.
> - `remove` only breaks the parent-child relation; the object itself still exists and can be `add`ed elsewhere at any time.
> - `add`ing the same object twice is ignored, but `insert` does **not** de-duplicate — an object already in the list gains a second reference, so to move it, `remove` first and then `insert`.

### Indexing, slicing, and iteration

```python
def __getitem__(value: int | slice) -> Mobject | Group
def __iter__() -> Iterator[Mobject]
def __len__() -> int
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `value` | `int` / `slice` | — | child index or slice; negative indices follow Python list rules |

> **Returns**: an `int` index returns a child `Mobject`, a `slice` returns a new group of the **same type** (slicing a `VGroup` still gives a `VGroup`), `len()` returns the child count, and a `for` loop yields the direct children in order. It is backed by `split()` ("self + direct children") and does not expand deeper levels automatically.

#### Sample: `mob[i]` / `mob[a:b]` / iteration

Five squares line up in a row: an index pulls out the 3rd and moves it up, a slice takes the two middle ones and recolors them, and finally the whole group is iterated to print the types.

```python
from real_time_manim import Scene, VGroup, Square, \
    RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE, RIGHT, UP
from real_time_manim.vulkan_bind import MLWindow, Wait

class IndexingDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        colors = (RED, BLUE, GREEN, YELLOW, PURPLE)   # five colors
        g = VGroup(*[Square(color=c, side_length=0.9) for c in colors])   # put five squares into a "VGroup"
        g.arrange(RIGHT, buff=0.35)   # line them up in a row
        self.add(g)   # add the whole group to the scene
        print("len(g) =", len(g))   # child count
        print("g[0] =", type(g[0]).__name__, "| g[1:3] =", type(g[1:3]).__name__)   # a slice returns a new group of the same type
        win.play(g[2].animate.shift(UP * 1.2), run_time=0.5)   # a child pulled out by index can be animated directly
        part = g[1:3]   # slice out the two middle squares
        win.play(part.animate.set_color(ORANGE), run_time=0.5)   # recolor only these two
        print("iteration =", [type(m).__name__ for m in g])   # a for loop yields the children in order
        win.play(Wait(0.5))   # pause 0.5s
        win.close()   # close the RTM window
```

What this code does: five differently colored squares line up in a row and go on screen. It first prints `len(g)` for the child count and `type(g[1:3])` to see whether a slice returns a new group of the same type. Then `g[2]` pulls out the 3rd square by index and plays its `animate` moving it up; next `g[1:3]` slices out the two middle ones (they are references to the original group's children, not copies) and recolors both orange. Finally a `for` loop iterates the whole group and prints the types.

<video src="assets/RTM output/01-Construction-and-Containers-indexing.mp4" controls width="560"></video>

> Note: a slice gives **child references**, not copies, so `part.animate.set_color(...)` changes exactly those two squares in the original group; for independent copies use `.copy()`. Also, slicing/iteration only sees the "direct children" level — a `VGroup` nested inside a `VGroup` is not expanded automatically, and its index is still a single whole.

---

See also: [Positioning](02-Positioning.md) · [Copying, Deriving and State](06-Copying-Deriving-and-State.md)
