# Quickstart

This page gets you into real-time-manim fast: your first scene, transformations, and an animation that turns `Hello, world!` into `Hello, real-time-manim!`. We strongly recommend finishing the installation guide and getting real-time-manim working before reading this page, so you can follow along as you read.

## Rendering a circle

1. In a project with real-time-manim installed, create a new file (call it `main.py`)
2. Copy the code below into your file

```python
from real_time_manim import *

class CreateCircle(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the scene to the window
        circle = Circle()# create a circle
        circle.set_fill(PINK, opacity=0.5)  # set the circle's fill and opacity
        win.play(FadeIn(circle), run_time=1.0)   # fade in the circle over 1 second
        win.close()   # close the window

fast_record_scene(CreateCircle)# export the video to ~/Downloads/output.mp4
```

3. Open a terminal, activate the virtual environment (in VS Code we recommend running `source .venv/bin/activate`), then run:

```bash
python main.py
```

4. Open `~/Downloads/output.mp4` and you'll see the rendered video.

### Explanation

Let's look at what each part does.

```py
from real_time_manim import *
```

```py
class CreateCircle(Scene):
    def construct(self):
        ...
```

In this snippet the main code goes into `construct(self)` — that is, we override the `construct` method of the `Scene` class. Inside `construct` you can add objects, animations and visual effects: it's where the main animation program of the `real-time-manim` library is written.

```python
win = MLWindow(960, 540)
win.scene = self
```

These two lines create the RTM window and bind the current scene to it (RTM always renders at 1920×1080, so the 960×540 in the parentheses is automatically corrected to 1920×1080). In `real-time-manim`, windows are rendered by the Vulkan-powered `MLWindow` — the Python `cairo renderer` has been entirely replaced by the Vulkan engine, which speeds up rendering.

```python
circle = Circle()# create a circle
circle.set_fill(PINK, opacity=0.5)  # set the circle's fill and opacity
```

Here we bind the circle to the variable name `circle`, so we can control the animation through that name. Each object can also be given properties (like the `.set_fill` call here) that change its appearance.

```py
win.play(FadeIn(circle), run_time=1.0)   # fade in the circle over 1 second
```

This is the main animation-rendering call: a `FadeIn`, which fades the circle into the frame. The animation can be swapped for another, and its duration is set by the trailing parameter (here `run_time=1.0`).

## Rendering the `Hello, world! → Hello, real-time-manim` animation

1. Append the code below to the end of the file

```python
class HelloWorld(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the scene to the window
        text = Text("Hello, world!")# create a text
        win.play(FadeIn(text), run_time=1.0)   # fade in the text over 1 second
        text2 = Text("Hello, real-time-manim!")# create a second text
        win.play(Transform(text, text2), run_time=2.0)   # transform into the second text over 2 seconds
        win.play(Wait(0.5))   # wait 0.5 seconds
        win.close()   # close the window

fast_record_scene(HelloWorld, "hello.mp4")# export the video to hello.mp4 in the project directory
```

2. Run it again in the virtual environment

```bash
python main.py
```

3. Open `hello.mp4` in the project directory and you'll see the text morph from `Hello, world!` to `Hello, real-time-manim!`.

### Explanation

```python
text = Text("Hello, world!")# create a text
```

Here we bind the text to the variable name `text`; `Text` turns a string into a text object (a mobject). Like `circle` in the previous section, we can control the text object through this variable name and give it properties such as `.set_fill`.

```python
win.play(Transform(text, text2), run_time=2.0)   # transform into the second text over 2 seconds
```

This is the heart of this section: `Transform` morphs the first object into the second. Here `text` smoothly deforms from `Hello, world!` into `Hello, real-time-manim!`; the duration of the morph is set by the trailing `run_time=2.0`, just like in the previous section.
