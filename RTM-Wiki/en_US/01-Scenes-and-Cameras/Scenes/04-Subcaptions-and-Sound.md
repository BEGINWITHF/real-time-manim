# Sections, subcaptions and sound

Of the three-piece render-output control set, RTM supports **sound** and **subcaptions**: `Scene.add_sound` is captured during recording and mixed into the MP4 audio track; the subcaption of `win.play(..., subcaption=...)` is written to a `.srt` when recording ends.

Sections (`next_section`) and calling `Scene.add_subcaption` directly still depend on manim's file writer; RTM doesn't take that path, so the call raises no error but **produces nothing**. The end of the page lists the OpenGL interactive-debug API that is unavailable under RTM.

## Parameters

### `Scene.add_sound`

```python
def add_sound(self, sound_file: str, time_offset: float = 0, gain: float | None = None, **kwargs: Any) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `sound_file` | `str` | — | audio file path (`.wav` / `.mp3`). A relative path is resolved against the **working directory**; an absolute path is recommended |
| `time_offset` | `float` | `0` | how many seconds after the **current moment** playback starts; may be negative |
| `gain` | `float \| None` | `None` | volume gain in **dB** (not a multiplier): `6.0` is about twice as loud, `-6` half as loud, `None`/`0` the original volume |
| `**kwargs` | `Any` | — | forwarded: supported ones (e.g. `gain_to_background` → pydub's `gain_during_overlay`) are applied; unsupported keywords **print an explicit warning** instead of being silently dropped |

Inserts an audio segment at the current moment (with optional offset). During recording RTM captures every `add_sound` through an `audio_track` hook, then after rendering mixes all sounds into one track and muxes it into the produced MP4 with ffmpeg (the video stream is not re-encoded).

The live window itself makes no sound; sound exists only in the recording output.

#### Sample: `Scene.add_sound`

Two "beeps": the first 0.5 seconds in, with +6 dB gain; the second at the instant the circle finishes, at the original volume as a control. Listen for where the sounds land, then watch the `Indicate` on the circle keep time.

```python
import os

from real_time_manim import Scene, Circle, ORANGE, Create, Indicate
from real_time_manim.vulkan_bind import MLWindow, Wait

class AddSoundDemo(Scene):
    GAIN = 6.0   #volume gain (dB): change it to 0 for the original volume, or -6 for something quieter

    def construct(self):
        win = MLWindow(960, 540)   #create an RTM window
        win.scene = self   #bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   #a scene method calls self.play internally, so wire it up first
        beep = os.path.join(os.path.dirname(os.path.abspath(__file__)), "beep.wav")   #the demo "beep"
        self.add_sound(beep, time_offset=0.5, gain=self.GAIN)   #beep once 0.5s in (louder)
        dot = Circle(radius=0.9, color=ORANGE)   #a circle
        self.add(dot)   #put the circle on screen
        win.play(Create(dot), run_time=1.0)   #draw this circle over 1.0s
        self.add_sound(beep, time_offset=0, gain=0)   #beep once more right now (at 1.0s), with no gain, as a control
        win.play(Indicate(dot), run_time=0.6)   #Indicate the circle to emphasize it, keeping time with the second sound
        win.play(Wait(0.6))   #wait 0.6s, leaving room for the sound's tail
        win.close()   #close the RTM window
```

What this code does: right at the start it registers the first "beep" (`time_offset=0.5` means it sounds 0.5 seconds from now, `gain=6.0` is noticeably louder), then draws a circle over 1 second. At the instant the circle finishes it registers the second "beep" (no gain), immediately followed by `Indicate` growing and shrinking the circle to keep time with that sound, and finally it waits 0.6 seconds to wrap up.

The recorded MP4 carries its own audio track, and the two "beeps" land at 0.5 s and 1.0 s.

<video src="assets/RTM output/04-Subcaptions-and-Sound-sound.mp4" controls width="560"></video>

> Note: `gain` is in **dB**; `1.5` is only slightly louder, write around `6.0` for a noticeable difference.
>
> RTM's timestamp is "the current position of the recorded timeline" (advanced after each `win.play`), so where you put `add_sound` is where the sound lands; the live preview window plays no sound — listen with a player after export.
>
> The demo audio `beep.wav` sits at `assets/RTM code/beep.wav`; `add_sound`'s relative path is resolved against the **working directory**, so both versions run from their own code directory.

### `Scene.next_section`

```python
def next_section(self, name: str = "unnamed", section_type: str = DefaultSectionType.NORMAL, skip_animations: bool = False) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | `str` | `"unnamed"` | section name (not unique), originally used for output file names/indexes |
| `section_type` | `str` | `DefaultSectionType.NORMAL` (`"default.normal"`) | a type tag for third parties (e.g. presentation tools) to recognize |
| `skip_animations` | `bool` | `False` | skip rendering all animations in this section |

**The call is harmless but produces nothing**: section output depends on the command-line `--save_sections` and `sections_dir` (manim's file writer renders each section into its own clip), and RTM has no `manim` command line and runs no file writer, so `next_section` just records a section marker in memory and nothing is written at the end.

To split a long video, write one scene per section, render each with `fast_record_scene`, and join/cut them with ffmpeg. No video.

### `Scene.add_subcaption` / `play(..., subcaption=...)`

```python
def add_subcaption(self, content: str, duration: float = 1, offset: float = 0) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `content` | `str` | — | subcaption text |
| `duration` | `float` | `1` | how long the subcaption shows (seconds) |
| `offset` | `float` | `0` | start-time offset (seconds) |

Both paths land in the same in-memory subcaption table and export a `.srt` automatically:

* `win.play(..., subcaption=..., subcaption_duration=..., subcaption_offset=...)`: timed from "this play's start time + `subcaption_offset`"; if `subcaption_duration` is omitted it takes this play's actual duration.
* `self.add_subcaption(...)` (since 2026-10-18): timed from **the current position of the recorded timeline** + `offset`; if `duration` is omitted it defaults to 1 second — matching manim's semantics.

When recording ends (hooked onto `audio_track.apply_sounds`) a same-named `.srt` is written next to the output mp4 automatically (the file is written only when there really are subcaptions; verified end to end: the timestamps of both cue paths, direct call + play, land correctly at 0.5 s instead of the old t=0). No video.

### Interactive debug: `interactive_embed` / `embed` / `set_key_function`

```python
def interactive_embed(self) -> None:
def embed(self) -> None:
def set_key_function(self, char: str, func: Callable[[], Any]) -> None:
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `char` | `str` | — | the key character |
| `func` | `Callable[[], Any]` | — | the function run when that key is pressed |

All return nothing. This group is the OpenGL renderer's interactive-debug feature:

- `interactive_embed` opens an IPython shell + live preview
- `embed` embeds IPython inside the preview window
- `set_key_function` binds a single key

RTM emits frames with its own Vulkan window and Timeline, has no such interactive link, and none of the three are available. To tinker while watching, write a small scene and use `fast_record_scene` to render it in seconds. No video.

---

See also: [Play and wait](03-Play-and-Wait.md) · [Scene basics](01-Scene-Basics.md) · [Recording video](../../00-Getting-Started/04-Recording-Video.md) · [Live window MLWindow](../../00-Getting-Started/03-Live-Window-MLWindow.md)
