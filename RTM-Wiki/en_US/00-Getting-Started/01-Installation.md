# Installing real-time-manim

RTM installs as a pip library; it has no `manim` command line. Once it is installed, use `MLWindow` directly inside a Python script to render live or record video.

> **You do not need to install ManimCE separately, and you do not need to `import manim`**: RTM ships the copy of ManimCE it drives (`real_time_manim/manim/`). `import real_time_manim` exports the whole ManimCE namespace (`Scene`, every mobject, every animation, colours, rate functions, ...), so `from real_time_manim import ...` just works. `from manim import ...` in older code still works too, and gets the same set of classes.
>
> **Exception**: if the process does `import manim` **first**, then `manim` keeps using that external copy and prints a `RuntimeWarning` when the version does not match; class identity then differs from the copy bundled with RTM — just `import real_time_manim` first.
>
> Version reference: the bundled ManimCE is **0.21.0** (`real_time_manim.MANIM_BUNDLE_VERSION`, MIT, see `UPSTREAM.md` in the repo); the project version is **2.0.0** (`pyproject.toml`).

## Parameters

Installation methods and runtime dependencies (from the Install section of the README):

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| Python | version | 3.11+ | minimum Python version for running RTM |
| Platform | system | Windows 10/11 | the wheel ships `vulkan_core.dll` and the window icon; no separate build |
| macOS prerequisites | shell commands | — | `brew install molten-vk` + `bash native/build_mac.sh`, producing `vulkan_core.dylib` |
| Vulkan driver | GPU/driver | — | required at runtime: needs a Vulkan-capable GPU and driver |
| `ffmpeg` | command on `PATH` | — | required only if you want to record video |

## Example

One-line install on Windows:

```bash
pip install real-time-manim
```

Optional: the Typst typesetting backend (required for `MathTex` to route Typst compilation automatically, see [10 Typst](../04-Shapes-and-Text/10-Typst.md)):

```bash
pip install "real-time-manim[typst]"   # = pip install "typst>=0.14"
```

On macOS, build the native library first and then install:

```bash
brew install molten-vk          # MoltenVK provides the Vulkan layer on macOS
bash native/build_mac.sh        # -> dist/release/vulkan_core.dylib
pip install real-time-manim
```

Verify the install (a successful import is enough):

```python
from real_time_manim.vulkan_bind import MLWindow, Create, Wait
from real_time_manim.record import fast_record_scene
```

## RTM in Action
TODO: add a video of a real machine run here (from setting up the environment all the way to successfully running the first piece of code), to be recorded by Tagin
See also: [First Scene](02-First-Scene.md)
