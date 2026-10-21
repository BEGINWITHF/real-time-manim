# Quality and Output

The batch of keys in manim's `config` that govern "quality and output" — resolution, frame rate, format, output file name, ... — are **mostly not wired up** in RTM: RTM does not go through the manim renderer, quality is fixed at 1920×1080@60, and the frame rate and output file name are given by the recording function's `fps` / `out_path`.

Only one key on this whole page is actually wired up: `background_color` (background colour); change it and the effect is immediate — there is a clip below. There are two other exceptions: `seed` takes effect indirectly, and `renderer` is instead something you should not fill in.

## Parameters

### `config` quality-and-output keys (most are not wired up; `seed` / `renderer` see the table)

**What it does**: in ManimCE this batch of keys controls resolution, frame rate, output format, file name, etc.; RTM does not read the quality-and-output path at all (writing them in a script has no on-screen effect). There are only two exceptions: `seed` indirectly fixes the random numbers via `Scene.__init__`, and `renderer` is read by the bundled ManimCE (so don't fill it in).

The table below marks, item by item, RTM's wiring status and "who is in charge of this".

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `pixel_width` | `int` | `1920` | not wired up: the output width is always 1920, determined by the size of `MLWindow(w, h)` (and you can only pass 1920×1080) |
| `pixel_height` | `int` | `1080` | not wired up: the output height is always 1080, same as above |
| `quality` | `str \| None` | `high_quality` | not wired up: you **can fill in** `low_quality` / `medium_quality` / `high_quality` / `production_quality` / `fourk_quality`, but RTM only has the single 1920×1080@60 tier, so whatever you fill in the picture does not change |
| `frame_rate` | `float` | `60` | not wired up: the frame rate is given by `fast_record_scene(fps=...)`, and only 60 is supported; anything else is force-corrected |
| `format` | `str \| None` | `mp4` | not wired up: you **can fill in** `png` / `gif` / `mp4` / `webm` / `mov`, but RTM only outputs `mp4`; to get one image per frame use `segment=(...)` to export BMP |
| `output_file` | `str` | `""` | not wired up: the output file name is given by `fast_record_scene(out_path=...)` |
| `background_color` | `ManimColor` | `BLACK` | **wired up**: the only key that works, see the section below |
| `background_opacity` | `float` | `1` | not wired up: you **can fill in** 0–1, but the clear colour RTM sends down has only RGB, so the output is always opaque |
| `transparent` | `bool` | `False` | not wired up: RTM does not output a transparent background (filling the row above with 0 does not help either) |
| `save_last_frame` | `bool` | `False` | not wired up: if you only want one frame, use `segment=(n, n+1)` to export BMP |
| `write_to_movie` | `bool` | `True` | not wired up: if you don't want to write a file, use `count_only=True` (count frames only, write nothing) |
| `write_all` | `bool` | `False` | not wired up: RTM has no concept of "render every scene in the file"; to render a given scene just call it one by one in your own script |
| `save_sections` | `bool` | `False` | not wired up: if you want sectioned output, split it into several scenes and record them separately |
| `zero_pad` | `int` | `4` | not wired up (number of zero-padding digits for the PNG index; RTM does not output a PNG sequence) |
| `movie_file_extension` | `str` | `.mp4` | not wired up: always `.mp4` |
| `from_animation_number` | `int` | `0` | not wired up: to start rendering from the Nth animation, comment out the `win.play(...)` calls before it |
| `upto_animation_number` | `int` | `-1` | not wired up: same as above — to render up to a point, delete the `win.play(...)` calls after it |
| `preview` | `bool` | `False` | not wired up: to watch while rendering, use `fast_record_scene(hidden=False)` or `record_scene` |
| `show_in_file_browser` | `bool` | `False` | not wired up |
| `verbosity` | `str` | `INFO` | not wired up: you **can fill in** `DEBUG`/`INFO`/`WARNING`/`ERROR`/`CRITICAL`, but how much RTM logs is governed by `fast_record_scene(verbose=...)` |
| `progress_bar` | `str` | `display` | not wired up: you **can fill in** `display`/`leave`/`none`, but RTM only prints one line, `[FastRecord] Saved: ...` |
| `disable_caching` | `bool` | `False` | not wired up: RTM has no partial-movie cache, every run is a full render |
| `flush_cache` | `bool` | `False` | not wired up (there is no cache to clear) |
| `max_files_cached` | `int` | `100` | not wired up (same as above) |
| `disable_caching_warning` | `bool` | `False` | not wired up |
| `seed` | `int \| None` | `None` | **takes effect indirectly**: the default value of `Scene.__init__`'s `random_seed` is `config.seed` (taken from it when not passed explicitly, then `random.seed(...)` / `np.random.seed(...)`, `manim/scene/scene.py:180,223-224`) — `config.seed = 42` likewise fixes the random numbers. To fix the random numbers, passing `random_seed=...` explicitly is still recommended (see [Special Scenes / 01-MovingCameraScene](../Special-Scenes/01-MovingCameraScene.md)) |
| `renderer` | `RendererType` | `cairo` | **do not fill in**: RTM's renderer really is Vulkan and will not switch to OpenGL because of this, **but a lot of the bundled ManimCE code reads it** (`Scene.__init__` choosing renderer/`mouse_point`, `VMobject` class selection, etc.); filling in `opengl` changes or even breaks behaviour, so it is by no means "no effect at all" |
| `dry_run` | `bool` | `False` | not wired up: run the pipeline without writing files = `count_only=True` |
| `save_pngs` | `bool` | `False` | not wired up (**deprecated**): for frame-by-frame images use `segment=(...)` |
| `save_as_gif` | `bool` | `False` | not wired up (**deprecated**): RTM does not output GIF, convert the mp4 yourself |

To change quality/output, the corresponding entry points in RTM are these (for the detailed parameters see [05-RTM-Record-and-Window-Options](05-RTM-Record-and-Window-Options.md)):

| What you want to change | Use in RTM | Description |
| --- | --- | --- |
| Resolution | `MLWindow(w, h)` | only 1920×1080; passing anything else is force-corrected and a hint is printed |
| Frame rate | `fast_record_scene(fps=...)` | only 60, same as above |
| Output file name | `fast_record_scene(out_path=...)` | give the file path directly; it does not go through the `media_dir` directory template |
| Background colour | `self.camera.background_color` | the sample lower on this page |
| Log amount | `fast_record_scene(verbose=...)` | `True` prints a progress line per window, `False` is silent mode |

These keys have nothing to show on screen (apart from `background_color`, changing them produces no picture), so this section has no clip; the only one you can actually see is the background colour, see the next section.

> Note: writing this batch of keys in a script **does not raise an error**, and the vast majority **also has no effect** (two exceptions: `seed` indirectly fixes the random numbers via the default value of `Scene.__init__`'s `random_seed`; `renderer` is instead something you **should not fill in**, the bundled ManimCE reads it).
>
> The easiest pitfall is thinking that `config.frame_rate = 30` will produce a 30fps video — in fact RTM always outputs at 60fps. If you want a non-60fps video, your only option is to convert it yourself with ffmpeg after rendering.
>
> For the command-line flags corresponding to these keys in ManimCE, see [04-ManimCE-CLI-Cheat-Sheet](04-ManimCE-CLI-Cheat-Sheet.md).

### `background_color` / `background_opacity`

```python
self.camera.background_color: ManimColor = BLACK   # clear colour: RTM reads it every frame, falling back to config.background_color
self.camera.background_opacity: float = 1.0        # only recorded on the camera; an opaque MP4 will not fade (consistent with ManimCE)
```

| Parameter                   | Type           | Default     | Description                                                                                                                                        |
| -------------------- | ------------ | ------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `background_color`   | `ManimColor` | `BLACK` | wired up: you **can fill in** any manim colour — `"#12233a"`, `BLUE`, `"#e8e4d8"`, ...; RTM reads the clear colour from `scene.camera.background_color` every frame (falling back to `config.background_color` if unset) and sends it down to the native layer |
| `background_opacity` | `float`      | `1`     | not wired up: 0–1 can be read and written, but it does not change the picture — CE only puts it into the frame's alpha channel, and the alpha is dropped when the opaque video is written out, so both engines' final clips are full colour (since 2026-10-19 RTM and CE match frame by frame, see [01-Camera](../Cameras/01-Camera.md)) |

#### Sample: changing `background_color`

The same scene with only `background_color` changed to one value (plus a label colour so the text is legible), and the whole screen's base colour swaps; the two clips are stitched together, one deep blue and one off-white.

```python
from real_time_manim import Scene, Square, Text, WHITE, UP, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class BackgroundColorDemo(Scene):
    BG = "#12233a"    # background colour: change it to "#e8e4d8" and run again, the whole clear colour follows
    TXT = "#e8e4d8"   # label colour: a light background needs a dark colour to stay legible

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        self.camera.background_color = self.BG   # hand "background_color" to the camera: that is the clear colour
        label = Text("background_color = %s" % self.BG, font_size=38,
                     color=self.TXT).to_edge(UP)   # show the current background colour on screen
        sq = Square(side_length=2.0, color=WHITE).set_fill(WHITE, 0.8).set_stroke(width=4)   # white square: contrast against the background
        self.add(label)   # put the label into the scene
        win.play(Create(sq), run_time=0.8)   # draw the white square
        win.play(sq.animate.scale(1.25), run_time=0.6)   # scale the square up a little
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window


class BackgroundColorLight(BackgroundColorDemo):
    BG = "#e8e4d8"    # same scene, just swap "background_color" to off-white
    TXT = "#12233a"   # swap the label back to deep blue
```

What this code does: it opens an RTM window and binds the scene to it, then sets `self.camera.background_color` to deep blue — from that frame on the whole screen's clear colour is that.

Then it puts a line of text showing the current colour on screen, draws a white square and scales it up a little, waits 0.5s and stops; the `BackgroundColorLight` subclass only swaps `BG` to off-white (and the label colour back to deep blue), producing the video's second clip.

So in the video you can see the base colour swap from deep blue to off-white across the whole screen, while the square, text and animation are completely the same — the only thing that changes is the single parameter, the clear colour.

<video src="assets/RTM output/01-Quality-and-Output-background_color.mp4" controls width="560"></video>

> Note:
>
> - `background_color` is re-read every frame, so changing it mid-way takes effect immediately too (the sample sets it once at the start).
> - For colour strings the hex `"#rrggbb"` is the most robust; remember to keep text/shape colours in contrast with the background — in the sample the light background swaps the label to deep blue.
> - Don't count on `background_opacity` / `transparent` — RTM's output is always an opaque mp4.

---

See also: [02-Frame-and-Coordinates](02-Frame-and-Coordinates.md) | [03-Paths-and-Windows](03-Paths-and-Windows.md) | [05-RTM-Record-and-Window-Options](05-RTM-Record-and-Window-Options.md)
