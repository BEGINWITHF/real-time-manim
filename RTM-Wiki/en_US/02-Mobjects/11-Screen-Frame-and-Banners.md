# Screen frames and the branded banner

Layout mock-up rectangles and the official Manim logo banner — the low-frequency visual objects in `frame.py` / `logo.py`.

## Parameters

### ScreenRectangle

```python
def ScreenRectangle(aspect_ratio: float = 16.0 / 9.0, height: float = 4,
                    **kwargs: Any) -> None
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `aspect_ratio` | `float` | `16/9` | aspect ratio |
| `height` | `float` | `4` | height |
| `**kwargs` | `Any` | — | passed through to `Rectangle` (`color=`, `fill_opacity=`, …) |

> **Returns**: a new `ScreenRectangle` (inherits all of `Rectangle`'s methods). A rectangle built to a "screen ratio", usually standing for "a screen / a layout area", and arranged with `arrange`, `to_edge`. **Extra read/write property `aspect_ratio`**: assigning to it automatically calls `stretch_to_fit_width`, changing the ratio without changing the height.

#### Sample: a 16:9 mock screen and `aspect_ratio`

Two 16:9 screen rectangles side by side; setting the right one's `aspect_ratio` to 1.0 keeps the height and shrinks the width to equal the height.

```python
from real_time_manim import Scene, ScreenRectangle, \
    BLUE, GREEN, LEFT, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class ScreenRectDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        s1 = ScreenRectangle(height=2.6, color=BLUE)   # a mock screen generated at 16:9
        s1.shift(LEFT * 3.4)   # put it on the left
        s2 = ScreenRectangle(height=2.6, color=GREEN).next_to(s1, RIGHT, buff=0.5)   # a comparison on the right
        self.add(s1, s2)   # add to the scene
        print("s1 width, height =", round(s1.width, 2), round(s1.height, 2))   #16:9
        win.play(FadeIn(s1), FadeIn(s2), run_time=0.5)   # fade in
        s2.aspect_ratio = 1.0   # extra read/write property: becomes a square, height unchanged (takes effect instantly)
        print("s2 after =", round(s2.aspect_ratio, 2), round(s2.width, 2), round(s2.height, 2))   #1.0 2.6 2.6
        win.play(Wait(0.5))   # pause to see the result
        win.close()   # close the RTM window
```

What this code does: two screen rectangles 2.6 high fade in side by side — `s1`'s width-to-height is 4.62 : 2.6 = 16 : 9 (verifiable in the console).

Then assigning `s2.aspect_ratio = 1.0` directly makes the setter `stretch_to_fit_width` shrink the width to 2.6 while the **height stays the same**, so the green screen becomes a square on screen. This is the basic building block for "laying out by screen ratio".

<video src="assets/RTM output/11-Screen-Frame-and-Banners-screen_rect.mp4" controls width="560"></video>

> Note: assigning `aspect_ratio` is **instant** (for a transition write `animate.set(aspect_ratio=...)`); it only changes the width and never touches `height`.
>
> The mock-up rectangle is an area in **world coordinates**; don't expect it to follow camera zooming automatically (see the edge-snapping note in [02 Positioning](02-Positioning.md)).

### FullScreenRectangle

```python
def FullScreenRectangle(**kwargs: Any) -> None
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `**kwargs` | `Any` | — | passed through to `ScreenRectangle` (e.g. `fill_opacity=`, `color=`) |

> **Returns**: a new `FullScreenRectangle`. A rectangle covering the whole screen (its height comes from `config.frame_height`), commonly used as a mask or dimmed background: `FullScreenRectangle(fill_opacity=0.7, color=BLACK)`.

#### Sample: a full-screen dimming mask

A semi-transparent black mask is laid over a scene of white text and a square, dimming everything; `remove` takes the mask off and restores it.

```python
from real_time_manim import Scene, Square, Text, FullScreenRectangle, \
    BLUE, WHITE, BLACK, DOWN, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class FullScreenDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        txt = Text("SCENE", font_size=48, color=WHITE)   # white text
        sq = Square(color=BLUE, side_length=1.5).shift(DOWN * 1.5)   # blue square
        self.add(txt, sq)   # add to the scene
        win.play(FadeIn(txt), FadeIn(sq), run_time=0.4)   # fade the content in
        mask = FullScreenRectangle(fill_opacity=0.7, color=BLACK)   # a dimming mask covering the whole screen
        self.add(mask)   # add to the scene
        win.play(FadeIn(mask), run_time=0.5)   # the mask fades in: the whole screen dims
        win.play(Wait(0.4))   # pause to see the mask effect
        self.remove(mask)   # take the mask off
        win.play(Wait(0.3))   # pause 0.3s
        win.close()   # close the RTM window
```

What this code does: the white text and blue square fade in first, then a `FullScreenRectangle(fill_opacity=0.7, color=BLACK)` fades in — it covers the whole screen automatically (no size calculation needed), dimming everything to 30% brightness.

After pausing 0.4 seconds to see the effect, `self.remove(mask)` takes the mask off and restores the original. This is the standard way to do a "dim for a transition".

<video src="assets/RTM output/11-Screen-Frame-and-Banners-fullscreen.mp4" controls width="560"></video>

> Note: the mask is built to the **frame size** (`frame_height`/`frame_width`), unlike `ScreenRectangle`; `remove` takes it off instantly, so to fade it out animate its `fill_opacity`.
>
> If you `add` several masks on top of each other, the last one added draws on top.

### ManimBanner

```python
def ManimBanner(dark_theme: bool = True)
def create(run_time: float = 2) -> AnimationGroup
def expand(run_time: float = 1.5, direction: str = "center") -> Succession
def scale(scale_factor: float, **kwargs: Any) -> Self
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `dark_theme` | `bool` | `True` | `True` dark theme (light text), `False` light theme (dark text) |
| `run_time` | `float` | `2` / `1.5` | animation duration of `create` / `expand` |
| `direction` | `str` | `"center"` | the direction the `expand` icon yields to. **Only** `"left"` / `"right"` / `"center"` are accepted; any other value raises `ValueError` |
| `scale_factor` | `float` | — | scale multiplier |

> **Returns**: `create` returns an `AnimationGroup` (the logo shape spinning in plus the letter `M` fading in; it is an override of `Create`, so both `banner.create()` and `Create(banner)` work); `expand` returns a `Succession` (it expands the icon-only logo into the full "manim" banner, and only after expanding is the `anim` letter group `add`ed); `scale` is an overridden version: it additionally records `self.scale_factor` and scales the not-yet-mounted `anim` letter group in step, keeping the spacing correct when `expand()` runs — **you must use this version, don't go around it**. Common attributes: `M`, `circle`, `square`, `triangle`, `shapes`, `anim` (appears only after expanding), `font_color`, `scale_factor`.

#### Sample: create → expand → an illegal direction

A dark-theme banner scaled 0.8 at the bottom: `create` plays the logo entrance and `expand` expands it into the full wordmark; then a `try` demonstrates an illegal `direction` raising `ValueError`, and finally the `anim` attribute is printed to confirm it is mounted after expanding.

```python
from real_time_manim import Scene, ManimBanner, \
    DOWN, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class BannerDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        banner = ManimBanner(dark_theme=True)   # dark-theme banner
        banner.scale(0.8)   # must use the overridden scale: it scales the not-yet-mounted letter group in step
        banner.to_edge(DOWN, buff=0.8)   # put it at the bottom
        print("font_color =", banner.font_color, "| scale_factor =", banner.scale_factor)   # common attributes
        self.add(banner)   # add to the scene
        win.play(banner.create(run_time=1.2))   # logo shape spins in + letter M fades in
        win.play(banner.expand(run_time=1.0, direction="center"))   # expand into the full "manim" banner
        try:
            banner.expand(direction="up")   # an illegal direction raises ValueError
        except ValueError as exc:
            print("expand illegal direction ->", str(exc)[:50])
        print("anim attribute =", getattr(banner, "anim", None) is not None)   # anim is mounted only after expanding
        win.play(Wait(0.4))   # pause 0.4s
        win.close()   # close the RTM window
```

What this code does: the dark-theme `ManimBanner` is first `scale(0.8)`d (the overridden version is required, otherwise `expand`'s spacing is wrong) and placed at the bottom; `banner.create(run_time=1.2)` plays the entrance — the logo shape spins in and the letter `M` fades in; then `expand(run_time=1.0, direction="center")` makes the icon yield and expands it into the full "manim" wordmark.

Finally a `try` runs an illegal `expand(direction="up")` and the console prints the `ValueError` message (only `left/right/center` are accepted); the `anim` attribute prints `True` — the letter group is mounted only after expanding.

<video src="assets/RTM output/11-Screen-Frame-and-Banners-banner.mp4" controls width="560"></video>

> Note: `create` then `expand` is the officially recommended order (`expand` assumes the logo is already on screen); doing expand first shows the icon yielding before it has even entered.
>
> `banner.scale(...)` must use the banner's own overridden version (it scales the not-yet-mounted `anim` group in step); calling `Mobject.scale(banner, ...)` directly will misalign the letter spacing during expansion.

---

See also: [Misc APIs](11b-Misc-APIs.md) | [animate Syntax](07-animate-Syntax.md)
