# ManimCE CLI Cheat Sheet (not supported by RTM)

RTM **has no command line**: it does not install the `manim` CLI's flags; the frame is determined by `MLWindow(w, h)` and the output by `fast_record_scene` / `record_scene`'s `out_path` / `fps`.

This page is the only place in the whole wiki that contains ManimCE content; it goes through the flags of `manim [options] file.py [scene names ...]` item by item and gives RTM's equivalent — for RTM all flags are uniformly (non-existent).

## Parameters

### Main render parameters (RTM has no CLI)

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `-ql` | tier | — | low quality 854×480 @ 15 FPS. RTM equivalent: none — fixed at 1920×1080@60 |
| `-qm` | tier | — | medium quality 1280×720 @ 30 FPS. RTM equivalent: same as above |
| `-qh` | tier | default | high quality 1920×1080 @ 60 FPS. RTM's fixed output is exactly this tier |
| `-qp` | tier | — | production quality 2560×1440 @ 60 FPS. RTM equivalent: same as above |
| `-qk` | tier | — | 4K 3840×2160 @ 60 FPS. RTM equivalent: same as above |
| `-r, --resolution W,H` | `W,H` | from `manim.cfg` | custom resolution (`W;H`, `W,H`, `W-H` all work). RTM equivalent: `MLWindow(w, h)`, only 1920×1080 |
| `--fps, --frame_rate F` | `float` | `60` | custom frame rate. RTM equivalent: `fast_record_scene(fps=...)`, only 60 |
| `--format [png\|gif\|mp4\|webm\|mov]` | enum | `mp4` | output format (`png` = images only). RTM: mp4 only; for frame-by-frame images use `segment=(...)` |
| `-o, --output_file name` | `str` | auto-named | specify the output file name. RTM equivalent: `out_path="my_video.mp4"` |
| `--media_dir path` | path | `./media` | root directory for all products such as video/LaTeX. RTM equivalent: `out_path` gives the file path directly |
| `-s, --save_last_frame` | flag | off | render and save only the last frame as PNG (no video). RTM equivalent: `segment=(n, n+1)` exports BMP |
| `-n, --from_animation_number start[;end]` | `int` | `0` | start rendering from the `start`-th `play`; the separators `;` `,` `-` all work (in the shell `;` needs quoting, write `3;7` or `3-7`). RTM: comment out / delete the preceding `win.play(...)` yourself |
| `-a, --write_all` | flag | off | render every scene in the script. RTM: call them one by one in the script yourself |
| `--save_sections` | flag | off | save each section as a separate video via `next_section`. RTM: split into several scenes and record them separately |
| `--renderer [cairo\|opengl]` | enum | `cairo` | choose the renderer. RTM: its own Vulkan renderer, no choice |
| `--disable_caching` | flag | off | disable the partial cache. RTM: there is no cache to begin with |
| `--flush_cache` | flag | off | delete all cached partial movies. RTM: same as above |
| `--seed N` | `int` | unset | random seed. RTM equivalent: the `Scene` constructor parameter `random_seed=...` |
| `-t, --transparent` | flag | off | transparent background (output `.mov`/`.webm`). RTM: the output is always opaque |
| `-g, --save_pngs` | flag | off | save PNG frame by frame (**deprecated**, use `--format png`). RTM: `segment=(...)` exports BMP |
| `-i, --save_as_gif` | flag | off | save GIF (**deprecated**, use `--format gif`). RTM: no GIF output |
| `--dry_run` | flag | off | run the pipeline without writing files or opening a window. RTM equivalent: `count_only=True` (count frames only) |

### Global / output / usability flags and subcommands (RTM has no CLI)

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `-c, --config_file path` | path | none | specify a config file (**note**: there is no `-c` flag for the background colour). RTM: does not read config files |
| `-v, --verbosity` | enum | `INFO` | log level `DEBUG/INFO/WARNING/ERROR/CRITICAL`. RTM equivalent: `verbose=...` |
| `--progress_bar` | enum | `display` | progress bar `display` / `leave` (keep after rendering) / `none` (don't show). RTM: only prints one line, `[FastRecord] Saved: ...` |
| `-p, --preview` | flag | off | open with a player after rendering (OpenGL is a live preview window). RTM equivalent: `hidden=False` or `record_scene` |
| `-f, --show_in_file_browser` | flag | off | show the output file in the file manager |
| `--custom_folders` | flag | off | use the directory structure from the config file's `[custom_folders]` |
| `--log_dir path` | path | — | log directory. RTM: does not write log files |
| `--log_to_file` | flag | off | write logs to a file. RTM: same as above |
| `--tex_template path` | path | default template | custom LaTeX template. The RTM-side entry point is `config.tex_template` / `config.tex_template_file` (**really takes effect**, measured 2026-10-17, see [03-Paths-and-Windows](03-Paths-and-Windows.md)), only there is no command-line flag |
| `--notify_outdated_version / --silent` | flag | on | whether to notify about a new version |
| `--no_latex_cleanup` | flag | off | keep LaTeX intermediate files. RTM equivalent: `cleanup=False` (keeps the whole `media/`) |
| `--enable_gui` | flag | off | OpenGL GUI panel |
| `--gui_location x,y` | `x,y` | `0,0` | GUI panel position |
| `--fullscreen` | flag | off | window fullscreen |
| `--force_window` | flag | off | force-open a window. RTM equivalent: `hidden=False` |
| `--enable_wireframe` | flag | off | OpenGL wireframe debug |
| `--jupyter` | flag | off | for the Jupyter magic (does not render immediately) |
| `--preview_command command` | `str` | none | custom preview command |

Other subcommands (all unsupported): **`manim cfg`** manages `manim.cfg` (`write`/`show`/`export -d directory`); **`manim init`** scaffolding (`project`/`scene`); **`manim plugins -l`** lists plugins; **`manim checkhealth`** installation health check.

> Note: in RTM this table is not "filled in but ineffective" — rather, **these entry points simply do not exist** — the `manim` command **is available only in an environment where ManimCE is separately installed** (RTM itself does not provide it: `real_time_manim/manim/` has `cli/` and `__main__.py` removed, and `pyproject.toml` has no console script either).
>
> With only RTM installed you cannot produce the `manim` command; after installing ManimCE separately it will still run, except that what is rendered is the CE picture. To render with RTM, write a Python script that calls `fast_record_scene` / `record_scene`. For a picture comparison of the two sides see `assets/README.md`.

### manim command <-> RTM call

The two samples below draw the most frequently used correspondences. The command lines are copy-pasteable:

```bash
# ManimCE: command-line rendering
manim -qh -o my_video --fps 60 scene.py Hello
```

```python
# RTM: function call (same effect)
from real_time_manim.record import fast_record_scene
fast_record_scene(Hello, out_path="my_video.mp4", fps=60)
```

#### Sample: quality tiers `-q`

Five tiers and RTM's fixed tier side by side on screen: ManimCE can pick from 854×480@15 up to 4K@60, while RTM has only the single 1920×1080@60 tier.

```python
from manim import (
    Scene, Text, VGroup,
    ORANGE, GREY_B, YELLOW, GREEN, UP, DOWN, LEFT,
    Write, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class QualityTiersDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        rows = VGroup(
            Text("-ql    854x480 @ 15", font_size=32, color=GREY_B),
            Text("-qm    1280x720 @ 30", font_size=32, color=GREY_B),
            Text("-qh    1920x1080 @ 60", font_size=32, color=YELLOW),
            Text("-qp    2560x1440 @ 60", font_size=32, color=GREY_B),
            Text("-qk    3840x2160 @ 60", font_size=32, color=GREY_B),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)   # lay out the five quality tiers top to bottom
        note = Text("RTM = 1920x1080 @ 60 only", font_size=34,
                    color=ORANGE).to_edge(DOWN, buff=0.7)   # RTM has only this one tier
        self.add(rows)   # put the five quality tiers into the scene
        win.play(FadeIn(rows, shift=UP * 0.2), run_time=0.8)   # fade in the five quality tiers
        win.play(Write(note), run_time=0.7)   # write out RTM's fixed tier
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window
```

What this code does: it lays the five quality tiers `-ql` through `-qk` (resolution @ frame rate) in a column and fades them onto the screen, with `-qh` highlighted in yellow — it is RTM's fixed output tier; finally it writes "RTM = 1920x1080 @ 60 only" at the bottom of the picture.

One thing is enough to remember from this video: **RTM has no tiers**; whatever size/frame rate you pass is force-corrected to 1080p60 (for real footage of the forced hint see the `MLWindow` sample in [05-RTM-Record-and-Window-Options](05-RTM-Record-and-Window-Options.md)).

<video src="assets/RTM output/04-ManimCE-CLI-Cheat-Sheet-quality_tiers.mp4" controls width="560"></video>

> Note: the `-q` tiers and `--fps` have no entry point at all in RTM; the values you fill into `MLWindow(w, h)` or `fast_record_scene(fps=...)` only serve to "trigger one line of forced hint". If you want a low-resolution preview that renders faster, your only option is to downscale with ffmpeg after rendering.

#### Sample: command line <-> RTM call

A ManimCE command and its RTM equivalent call side by side top and bottom: the clip produced is the same, only one entry point is the command line and the other is a function.

```python
from manim import (
    Scene, Text, VGroup,
    ORANGE, GREY_B, YELLOW, GREEN, UP, DOWN, LEFT,
    Write, FadeIn,
)
from real_time_manim.vulkan_bind import MLWindow, Wait

class CliEquivDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim window named "self" to the RTM window named "win"
        cli = Text("manim -qh -o my_video --fps 60 scene.py Hello",
                   font_size=30, color=ORANGE).shift(UP * 1.2)   # the ManimCE command line
        same = Text("same output", font_size=26, color=GREY_B)   # the note between the two lines
        call = Text("fast_record_scene(Hello, out_path='my_video.mp4', fps=60)",
                    font_size=30, color=GREEN).shift(DOWN * 1.2)   # the RTM function call
        self.add(cli, same, call)   # put the three lines of text into the scene
        win.play(FadeIn(cli, shift=UP * 0.2), run_time=0.6)   # first the command line
        win.play(FadeIn(same), run_time=0.4)   # then the note in the middle
        win.play(FadeIn(call, shift=DOWN * 0.2), run_time=0.6)   # finally the RTM call
        win.play(Wait(0.5))   # wait for 0.5s
        win.close()   # close the RTM window
```

What this code does: three lines of text fade in in turn — at the top is ManimCE's full command `manim -qh -o my_video --fps 60 scene.py Hello`, the middle line "same output" says the two produce the same clip, and at the bottom is RTM's equivalent call `fast_record_scene(Hello, out_path='my_video.mp4', fps=60)`.

Memory aid: `-o name` on the command line corresponds to `out_path`, `--fps` corresponds to `fps`, and the positional file-name/scene-name arguments correspond to the function's first argument.

<video src="assets/RTM output/04-ManimCE-CLI-Cheat-Sheet-cli_equiv.mp4" controls width="560"></video>

> Note: `fast_record_scene`'s second argument is directly a **file path** (with `.mp4`), not the command line's "name without extension"; the scene argument can be a class, an instance, or a no-arg callable (see the `scene` sample in [05-RTM-Record-and-Window-Options](05-RTM-Record-and-Window-Options.md)).

**Summary**: ManimCE's command-line flags do not exist at all in RTM; quality is fixed at 1080p60, the output is given by the two arguments `out_path`/`fps`, and to see the effect use `hidden=False` or `record_scene`.

If you really want to run ManimCE's command line (say, just to get a low-resolution draft), install ManimCE separately first (`pip install "real-time-manim[test]"` or `pip install manim`); after that the `manim` command works as usual — except that is not RTM's picture.

The two samples are pixel-for-pixel identical across both engines (120 frames / 2.00s, 126 frames / 2.10s).

---

See also: [01-Quality-and-Output](01-Quality-and-Output.md) | [03-Paths-and-Windows](03-Paths-and-Windows.md) | [05-RTM-Record-and-Window-Options](05-RTM-Record-and-Window-Options.md)
