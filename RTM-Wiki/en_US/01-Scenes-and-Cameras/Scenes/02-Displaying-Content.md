# Displaying content: add / remove and z-order

Put objects on screen, take them off, and adjust their occlusion order. RTM draws every frame following the order of `scene.mobjects`, so add order is draw order: earlier additions are below, later ones cover them. The foreground list (`foreground_mobjects`) is always drawn on top.

## Parameters

### `Scene.add`

```python
def add(self, *mobjects: Mobject | OpenGLMobject) -> Self:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | — | the objects to put on screen; you can pass several at once. **accepts** any `Mobject`; drawn from background to foreground in add order (earlier below), and returns the `Scene` itself for chaining. An object already in the scene that is `add`ed again is moved to the top |

#### Sample: `Scene.add`

Three shapes added one by one, so who covers whom is obvious at a glance; an object newly added by an animation (the small green square) goes straight to the top.

```python
from real_time_manim import (
    Scene,
    Square, Circle, Triangle, Text,
    BLUE, RED, GREEN, YELLOW, WHITE,
    UP, RIGHT,
    FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class AddDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        back = Square(color=BLUE, side_length=2.5)   #the first square added
        mid = Circle(color=RED, radius=1.6)   #the second circle added
        top = Triangle(color=YELLOW).scale(1.3).shift(RIGHT * 2.2)   #the third triangle added
        self.add(back)   #earlier additions are drawn at the bottom
        self.add(mid, top)   #later additions cover them; you can pass several at once
        self.add(Text("add order = paint order", font_size=36, color=WHITE).to_edge(UP))   #the text added last is on top
        win.play(Wait(0.5))   #hold 0.5s to see who covers whom
        win.play(FadeIn(Square(color=GREEN, side_length=1.2)), run_time=0.5)   #an object newly added by an animation goes straight to the top
        win.play(Wait(0.5))   #wait another 0.5s
        win.close()   #close the RTM window
```

What this code does: it adds a blue square first, then a red circle, then a yellow triangle, and finally a title line. Because drawing goes bottom-up in add order, the circle covers the square, the triangle covers the circle, and the title covers all the shapes.

Then `FadeIn` plays a small green square in; it counts as "an object newly added by an animation" and likewise goes straight to the top. The whole process has no z-order call at all — it all relies on the `add` order.

<video src="assets/RTM output/02-Displaying-Content-add.mp4" controls width="560"></video>

> Note: adding an object through an animation also follows this rule: if the `x` in `win.play(FadeIn(x))` isn't in the scene it is registered and appended to the end of the list (the top); an object already in the scene (even a child of some `Group`) is not re-sorted, it stays in place.

### `Scene.remove`

```python
def remove(self, *mobjects: Mobject) -> Self:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | — | the objects to take off screen; you can pass several at once; returns the `Scene` itself. It handles child objects too: removing one child from a `Group` "dissolves" the group and keeps the remaining members as top-level objects |

#### Sample: `Scene.remove`

The circle covers the square; `remove` the circle and the square underneath shows through.

```python
from real_time_manim import Scene, Square, Circle, BLUE, RED
from real_time_manim.vulkan_bind import MLWindow, Wait

class RemoveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        back = Square(color=BLUE, side_length=2.5)   #the covered square
        front = Circle(color=RED, radius=1.6)   #the circle on top
        self.add(back, front)   #put the circle covering the square on screen
        win.play(Wait(0.5))   #first see clearly that "the circle covers the square"
        self.remove(front)   #take the circle off screen, revealing the square underneath
        win.play(Wait(0.5))   #wait another 0.5s to see the effect
        win.close()   #close the RTM window
```

What this code does: it first puts the square and the circle into the scene (circle added later, covering the square) and waits 0.5 seconds so you can see the occlusion; then `remove` takes the circle off screen — the covered blue square is immediately fully revealed — and it waits another 0.5 seconds to finish.

`remove` takes effect immediately and needs no animation.

<video src="assets/RTM output/02-Displaying-Content-remove.mp4" controls width="560"></video>

> Note: the object passed to `remove` must be in the scene (if not, nothing happens). RTM goes through the same entry internally: "disappearance" animations such as `Uncreate`, `FadeOut` call `scene.remove` at wrap-up to take the object off.

### `Scene.clear`

```python
def clear(self) -> Self:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| (no parameters) | — | — | one-key off-screen: empties both the `mobjects` and `foreground_mobjects` lists. Returns the `Scene` itself. Often used for "page-turn" style scene switches |

#### Sample: `Scene.clear`

After clearing the screen, a new title is put up, just like turning a page.

```python
from real_time_manim import Scene, Square, Circle, Text, BLUE, RED, YELLOW, GREEN, LEFT, RIGHT, UP
from real_time_manim.vulkan_bind import MLWindow, Wait

class ClearDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        self.add(Square(color=BLUE, side_length=2).shift(LEFT * 2))   #put up a square
        self.add(Circle(color=RED, radius=1.2).shift(RIGHT * 2))   #put up a circle
        self.add(Text("before clear", font_size=40, color=YELLOW).to_edge(UP))   #add a title
        win.play(Wait(0.5))   #first see what's on screen
        self.clear()   #one-key clear: both mobjects and foreground_mobjects go off screen
        self.add(Text("after clear", font_size=40, color=GREEN).to_edge(UP))   #put up a new title
        win.play(Wait(0.5))   #only the new title remains on screen
        win.close()   #close the RTM window
```

What this code does: it first puts up a square, a circle and a yellow title and waits 0.5 seconds to see the content; then `clear()` takes everything off screen at once (clearing the foreground list too), puts up a new green title and waits 0.5 seconds — the screen goes from "three objects" to "one title", which is one page turn.

<video src="assets/RTM output/02-Displaying-Content-clear.mp4" controls width="560"></video>

> Note: `clear()` only takes the objects off the scene, it doesn't destroy the objects themselves; to use them again, just `add` them once more. It clears `foreground_mobjects` too, so after clearing you must re-register the foreground.

### Z-order adjustment: `bring_to_front` / `bring_to_back` / `add_foreground_mobject(s)` / `remove_foreground_mobject(s)`

```python
def bring_to_front(self, *mobjects: Mobject) -> Scene:
def bring_to_back(self, *mobjects: Mobject) -> Scene:
def add_foreground_mobjects(self, *mobjects: Mobject) -> Scene:
def add_foreground_mobject(self, mobject: Mobject) -> Scene:
def remove_foreground_mobjects(self, *to_remove: Mobject) -> Scene:
def remove_foreground_mobject(self, mobject: Mobject) -> Scene:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*mobjects` / `mobject` | `Mobject` | — | the objects whose z-order to adjust. `bring_to_front` re-`add`s them to the top; `bring_to_back` moves them to the bottom; both return the `Scene` itself |
| `*to_remove` / `mobject` | `Mobject` | — | the objects to register/unregister as foreground. Foreground objects are always drawn on top (even when other objects are added later or animation objects come and go); good for titles, legends, magnifier-frame borders |

#### Sample: z-order adjustment

A square changes layer and a big circle sweeps across the title: first see "who is on top" change with `bring_to_front` / `bring_to_back`, then see how the title, once registered as foreground, covers the big circle and, once unregistered, is covered by it again.

```python
from real_time_manim import Scene, Square, Circle, Text, BLUE, RED, GREEN, YELLOW, UP, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class ZorderDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   #the on-top rule re-sorts objects inside win.play, so wire it up first
        blue = Square(color=BLUE, side_length=2.2).shift(LEFT * 0.6)   #the blue square added first
        red = Square(color=RED, side_length=2.2).shift(RIGHT * 0.6)   #the red square added later, covering the blue
        title = Text("z-order", font_size=40, color=YELLOW).to_edge(UP)   #the title to put on top
        self.add(blue, red)   #red above, blue below
        win.play(Wait(0.5))
        self.bring_to_front(blue)   #move the blue square to the top
        win.play(Wait(0.5))
        self.bring_to_back(blue)   #push the blue square back to the bottom
        win.play(Wait(0.5))
        self.add(title)   #put the title on screen as an ordinary object first
        sweep = Circle(color=GREEN, radius=2.8, fill_opacity=1).shift(LEFT * 9 + UP * 3.5)   #a solid big circle that will sweep across the title
        self.add(sweep)   #the circle added later, covering the title
        win.play(sweep.animate.shift(RIGHT * 8), run_time=0.8)   #the big circle sweeps across and covers the title
        self.add_foreground_mobject(title)   #register the title as foreground: it floats straight to the top
        win.play(Wait(0.5))   #hold 0.5s: the title covers the circle
        self.remove_foreground_mobject(title)   #unregister the foreground; but the title was already moved to the end of the list by add, so it is still on top
        self.bring_to_back(title)   #to get back down you still have to push it back yourself
        win.play(Wait(0.5))   #hold 0.5s: the title is covered by the circle again
        win.close()   #close the RTM window
```

What this code does: two overlapping squares; `bring_to_front(blue)` makes the blue square cover the red one, and `bring_to_back(blue)` pushes it back under the red one — the ownership of the overlap flips accordingly.

Next a solid green circle sweeps left to right across the title and covers it; at that point `add_foreground_mobject(title)` registers the title as foreground and it immediately floats above the green circle. Finally `remove_foreground_mobject(title)` unregisters the foreground and `bring_to_back(title)` pushes it back to the bottom, so the title is covered by the green circle again.

<video src="assets/RTM output/02-Displaying-Content-zorder.mp4" controls width="560"></video>

> Note: two gotchas.
>
> ① `add_foreground_mobject` internally `add`s the object again (`Scene.add`'s foreground rule moves it to the end of the list along the way), so it often "incidentally" moves to the top; `remove_foreground_mobject` **only leaves the foreground list**, the object stays at the end of the list and is still drawn on top — to really get it back down you have to `bring_to_back` yourself (the last part of the sample demonstrates exactly this step).
>
> ② Every `win.play` pulls foreground objects back to the top according to the foreground list, so a foreground title will not be covered by animation objects added later.

### `Scene.replace` / scene query utilities

```python
def replace(self, old_mobject: Mobject, new_mobject: Mobject) -> None:
def get_attrs(self, *keys: str) -> list[Any]:
def get_top_level_mobjects(self) -> list[Mobject]:
def get_mobject_family_members(self) -> list[Mobject]:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `old_mobject` | `Mobject` | — | the object being replaced; it must already be in the scene, otherwise a `ValueError` is raised. If it is a child of some `Group`, it is replaced in place within the group |
| `new_mobject` | `Mobject` | — | the new object that takes its place; it must not already be in the scene. No return value; the draw order stays the same and only this one slot is swapped |

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `*keys` | `str` | — | attribute names (`get_attrs` only). The three query functions return, respectively, a list of attribute values, a list of top-level objects, and a flattened list of all objects and their children |

#### Sample: `Scene.replace`

The triangle is swapped for a square in place while the red dot next to it stays put — same draw order, one slot swapped.

```python
from real_time_manim import Scene, Square, Triangle, Dot, GREEN, ORANGE, RED, LEFT, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class ReplaceDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        tri = Triangle(color=GREEN).scale(1.3).shift(LEFT * 2.5)   #the triangle to be replaced
        dot = Dot(color=RED, radius=0.35).shift(RIGHT * 2.5)   #the red dot beside it, as a control
        self.add(tri, dot)   #put both objects on screen
        print("before replace: top-level = %d" % len(self.get_top_level_mobjects()))   #query utility get_top_level_mobjects
        win.play(Wait(0.5))
        self.replace(tri, Square(color=ORANGE, side_length=1.8).shift(LEFT * 2.5))   #swap the triangle for a square in place
        print("after replace: top-level = %d" % len(self.get_top_level_mobjects()))   #the count is unchanged; it is just replaced in place
        win.play(Wait(0.5))
        win.close()   #close the RTM window
```

What this code does: it puts a green triangle on the left and a red dot on the right as a control, and first counts the top-level objects with `get_top_level_mobjects()` (2). After waiting 0.5 seconds it swaps the triangle for an orange square in place with `replace` and counts again — still 2, showing it is only a replacement with no add/remove, and the red dot beside it is completely unaffected.

<video src="assets/RTM output/02-Displaying-Content-replace.mp4" controls width="560"></video>

> Note: after `replace`, remember not to reference the old object again (it is no longer in the scene).
>
> When counting, note: waits that go through manim's `Wait` such as `self.wait(...)` leave an empty `Mobject` in `scene.mobjects` (upstream behaviour), making `len(self.mobjects)` 1 more; `win.play(Wait(...))` does not (see [Play and wait](03-Play-and-Wait.md) for details).

---

See also: [Scene basics](01-Scene-Basics.md) · [Play and wait](03-Play-and-Wait.md) · [Live window MLWindow](../../00-Getting-Started/03-Live-Window-MLWindow.md) · [animate syntax](../../02-Mobjects/07-animate-Syntax.md)
