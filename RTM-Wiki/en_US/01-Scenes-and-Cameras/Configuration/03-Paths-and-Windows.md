# Paths and Windows

In `config`, the keys that govern the **output path** (the batch of directory templates around `media_dir`) and the **window** (the OpenGL preview window's position/size/fullscreen) are **not wired up at all for the final clip path** in RTM: RTM's output is exactly the one file path you give (`out_path`), and the window is governed by `MLWindow(w, h, hidden)`.

**Exception**: `tex_dir` / `text_dir` / `assets_dir` still take effect for **intermediate products** (the LaTeX/Typst compile directory, `Text`'s svg, the image/audio lookup directory), and `tex_template` / `tex_template_file` really do take effect (measured 2026-10-17, see the table below).

Everything you want can be done, only the entry point has changed — for the correspondence see the sample at the end of this page, and for the parameter details see [05-RTM-Record-and-Window-Options](05-RTM-Record-and-Window-Options.md).

## Parameters

### `config` output-path keys (cheat-sheet C; the final clip is not wired up, intermediate products see `tex_dir` / `text_dir` / `assets_dir`)

**What it does**: in ManimCE this batch of keys assembles directory templates like `media/videos/...` and `media/Tex`; RTM's **final clip** does not go through this template — the product is a single file, `out_path` (plus a temporary manim `media/` directory that is cleaned up automatically after recording).

But manim's own LaTeX / Text / image pipeline is still running, and the directory keys they read still take effect.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `media_dir` | `str` | `./media` | final clip not wired up: the output root directory template is useless, RTM is given the file path `out_path` directly. But `tex_dir` / `text_dir` default to its subdirectories, so changing it also moves the LaTeX / Text intermediate products; also note the cleanup helper `util.clear_media()` only deletes `<cwd>/media` (`real_time_manim/util.py:144-166`) and **does not follow** `config.media_dir` |
| `video_dir` | `str` | `{media_dir}/videos/{module_name}/{quality}` | not wired up: same as above |
| `sections_dir` | `str` | `{video_dir}/sections` | not wired up: for sectioned output, split into scenes and record them separately |
| `images_dir` | `str` | `{media_dir}/images/{module_name}` | not wired up |
| `partial_movie_dir` | `str` | `{video_dir}/partial_movie_files/{scene_name}` | not wired up: RTM has no partial cache and will not generate partial movies |
| `tex_dir` | `str` | `{media_dir}/Tex` | **takes effect for intermediate products**: the LaTeX/Typst compile directory is exactly `config.get_dir("tex_dir")` (`manim/utils/tex_file_writing.py:105,202,277`, `manim/utils/typst_file_writing.py:84`); changing it moves the `.tex`/`.svg` intermediate files (measured 2026-10-17: after setting it to a temporary directory, `Tex('a + b')`'s `.tex`/`.svg` really landed there); **what is not wired up is only the final clip output path** (RTM only uses `out_path`). By default it is under `media/` and is cleaned up along with `cleanup=True` |
| `text_dir` | `str` | `{media_dir}/texts` | **takes effect for intermediate products**: `Text`'s svg cache directory is exactly `config.get_dir("text_dir")` (`manim/mobject/text/text_mobject.py:841,1388`; measured 2026-10-17, `Text('hello rtm')` landed in the changed directory), same as above |
| `log_dir` | `str` | `{media_dir}/logs` | not wired up: RTM does not write log files, output goes to the terminal |
| `assets_dir` | `str` | `./` | **takes effect for the lookup directory**: `get_full_raster_image_path` / `get_full_svg_image_path` (`manim/utils/images.py:27-38`, audio `manim/utils/sounds.py:24` likewise) treat `config.get_dir("assets_dir")` as one of the default search directories — it first tries the relative path you give as-is, then tries a same-named file under `assets_dir` (measured 2026-10-17: after changing it, a same-named png in the new directory could be found by `ImageMobject`). **What is not wired up is only the final clip output path** |
| `input_file` | `str \| Path` | — | not wired up: RTM has no concept of "the script being rendered" |
| `scene_names` | `list[str]` | `[]` | not wired up: which scene to render = which `fast_record_scene` you call in your own script |
| `custom_folders` | `str` | `False` | not wired up (the custom directory structure fails together with `media_dir`) |
| `tex_template` | `TexTemplate` | default template | **really takes effect**: `config.tex_template` is a real `TexTemplate` object (measured 2026-10-17, `type(...) == TexTemplate`, `hasattr(..., "add_to_preamble") == True`), and RTM goes through manim's own LaTeX pipeline (`manim/utils/tex_file_writing.py:56-57,98-99` reads `config["tex_template"]` directly) — measured: after adding a custom comment line to the template, the written `.tex` carries that line |
| `tex_template_file` | `Path` | `""` | **really takes effect**: `tex_template`'s getter does `TexTemplate.from_file(...)` when this key is non-empty (`manim/_config/utils.py:1811-1820`); setting it is equivalent to replacing the whole template |
| `plugins` | `list[str]` | `[]` | not wired up: plugins are loaded by the manim command line, and RTM does not go through the command line |
| `log_to_file` | `bool` | `False` | not wired up |
| `ffmpeg_loglevel` | `str` | `ERROR` | not wired up: RTM starts ffmpeg itself (stderr is discarded directly), this key cannot reach it |
| `notify_outdated_version` | `bool` | `True` | not wired up |
| `no_latex_cleanup` | `bool` | `False` | not wired up: note that RTM's `cleanup` is reversed — by default it **deletes the entire** manim `media/`, and only `cleanup=False` keeps it |
| `preview_command` | `str` | `""` | not wired up: after rendering, open your own player to watch |

> Note:
>
> - The most common pitfall: "arranging" the output file in the `media_dir` template and then looking for `media/videos/xxx/1080p60/` — RTM simply will not generate that path; the file is exactly where your `out_path` says (non-existent subdirectories are created automatically).
> - Conversely, manim's own temporary `media/` directory **will be deleted by RTM** (with `cleanup=True`, the default); if you want to keep it for study, pass `cleanup=False`.

### `config` window keys (cheat-sheet D, all not wired up)

**What it does**: in ManimCE this batch of keys configures the OpenGL preview window (position, size, fullscreen, debug switches); RTM's window is created by `MLWindow(w, h, hidden)`, and the size can only be 1920×1080.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `enable_gui` | `bool` | `False` | not wired up (the DearPyGUI control panel; RTM does not have it) |
| `gui_location` | `tuple[int,...]` | `(0,0)` | not wired up |
| `fullscreen` | `bool` | `False` | not wired up: the recorded output is always a 1920×1080 frame, regardless of whether the window is fullscreen |
| `window_position` | `str` | `UR` | not wired up: RTM does not manage the window position (the popup position follows the system) |
| `window_size` | `str \| tuple` | `default` | not wired up: the window size = the two parameters of `MLWindow(w, h)`, and only 1920×1080 |
| `window_monitor` | `int` | `0` | not wired up (which monitor to render on) |
| `force_window` | `bool` | `False` | not wired up: to open a window use `fast_record_scene(hidden=False)` or `record_scene` |
| `enable_wireframe` | `bool` | `False` | not wired up (wireframe debug) |
| `use_projection_fill_shaders` | `bool` | `False` | not wired up (OpenGL shader compatibility switch; RTM uses its own render pipeline) |
| `use_projection_stroke_shaders` | `bool` | `False` | not wired up (same as above) |
| `media_embed` | `bool \| None` | `False` | not wired up (Jupyter embedded video) |
| `media_width` | `str` | `60%` | not wired up (same as above) |

> Note: `hidden` is the only visibility switch for an RTM window (a constructor parameter or `fast_record_scene(hidden=...)`); it only affects whether a window pops up on **your desktop** — the recorded video content is exactly the same — this has a clip comparison, see the `MLWindow` sample in [05-RTM-Record-and-Window-Options](05-RTM-Record-and-Window-Options.md).

### RTM-side correspondence: paths go to `out_path`, windows go to `MLWindow`

| What you want to do | Use in RTM | See |
| --- | --- | --- |
| Specify the output file | `fast_record_scene(..., out_path="my.mp4")` | the `out_path` sample in [05](05-RTM-Record-and-Window-Options.md) |
| Output to a subdirectory | `out_path="clips/my.mp4"` (directory created automatically) | same as above |
| Window size | `MLWindow(w, h)` (only 1920×1080) | the `MLWindow` sample in [05](05-RTM-Record-and-Window-Options.md) |
| Window visibility | `fast_record_scene(..., hidden=...)` | same as above |
| Watch while rendering / live recording | `record_scene(...)` | the `record_scene` sample in [05](05-RTM-Record-and-Window-Options.md) |
| Keep the manim temporary directory | `fast_record_scene(..., cleanup=False)` | [05](05-RTM-Record-and-Window-Options.md) |

#### Sample: config -> RTM correspondence

This sample does not demonstrate a single parameter; instead it animates the "who is in charge" relation of the two tables above on screen: one line for the `config` key, one line for RTM's real entry point.

```python
from real_time_manim import Scene, Text, VGroup, ORANGE, GREY_B, UP, DOWN, LEFT, Write, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class ConfigToRtmDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        title = Text("config  ->  RTM", font_size=42, color=ORANGE).to_edge(UP, buff=0.7)   # title line
        rows = VGroup(
            Text("media_dir / video_dir  ->  out_path = my.mp4", font_size=30, color=GREY_B),
            Text("window_size / window_position  ->  MLWindow(w, h)", font_size=30, color=GREY_B),
            Text("fullscreen / force_window  ->  hidden", font_size=30, color=GREY_B),
            Text("preview  ->  hidden=False", font_size=30, color=GREY_B),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).next_to(title, DOWN, buff=0.7)   # lay out the four rows
        self.add(title)   # put the title into the scene
        win.play(Write(title), run_time=0.7)   # write the title
        for row in rows:   # bring the correspondence rows onto the screen one by one
            win.play(FadeIn(row, shift=UP * 0.15), run_time=0.4)   # fade in one row
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window
```

What this code does: it first writes the "config -> RTM" title, then fades in the four correspondence rows one by one:

- directory templates become `out_path`;
- window size/position become `MLWindow(w, h)`;
- fullscreen/force-open-window become `hidden`;
- post-render preview becomes `hidden=False`.

Finally it waits 0.5s and stops. The video is a condensed version of this page: the `config` keys on the left are all not wired up, and the right side is RTM's real entry point.

<video src="assets/RTM output/03-Paths-and-Windows-config_to_rtm.mp4" controls width="560"></video>

> Note: when you can't remember the correspondence, one sentence is enough — "path = `out_path`, window = `MLWindow`, treat the rest of the config keys as non-existent".
>
> Also note that after rendering RTM **actively deletes** manim's temporary `media/` directory (`cleanup=True`, the default); don't put anything important in there.

The two engines are pixel-for-pixel identical (168 frames / 2.80s); every `config` key on this page has no on-screen effect, and the only thing that produces a clip is this correspondence animation.

---

See also: [01-Quality-and-Output](01-Quality-and-Output.md) | [02-Frame-and-Coordinates](02-Frame-and-Coordinates.md) | [04-ManimCE-CLI-Cheat-Sheet](04-ManimCE-CLI-Cheat-Sheet.md) | [05-RTM-Record-and-Window-Options](05-RTM-Record-and-Window-Options.md)
