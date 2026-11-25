# Installation

This page walks you through installing every dependency of real-time-manim. real-time-manim supports **Windows 10/11** and **macOS** (there is no Linux build) and requires Python 3.11 or later.

Once everything here is installed, read [Quickstart](02-Quickstart.md) to render your first animation.

## The install list

| Dependency | What it is for | Required? |
| --- | --- | --- |
| Python 3.11+ | The interpreter that runs real-time-manim | Required |
| real-time-manim | RTM itself (ships its own ManimCE 0.21.0 — **do not install manim separately**) | Required |
| Vulkan (MoltenVK on macOS) | RTM's rendering engine | Required |
| ffmpeg | Composites the frames into an mp4 when recording | Required for video recording |
| typst | Compilation backend for `MathTex` formulas (with it you don't need LaTeX for formulas) | Optional |
| LaTeX (TeX Live / MacTeX / MiKTeX) | Always needed for `Tex` text formulas; also needed for `MathTex` without typst | Optional |

## 1. Install Python

Download and install **Python 3.11 or later** from [python.org](https://www.python.org/downloads/), ticking "Add Python to PATH" during the install (Windows).

Verify in a terminal:

```bash
python3 --version
```

If it prints a version (3.11 or later), carry on.

## 2. Create a virtual environment (recommended)

We recommend giving every real-time-manim project its own virtual environment so its packages don't clash with other projects:

```bash
python3 -m venv .venv   # create the virtual environment in the project directory
```

Activate it before every use (VS Code's terminal will offer to activate it for you):

```bash
# Windows
.venv\Scripts\activate
```

```bash
# macOS
source .venv/bin/activate
```

## 3. Install real-time-manim

```bash
pip install real-time-manim            # just the package
pip install "real-time-manim[typst]"   # package + typst (recommended: MathTex formulas without LaTeX)
```

The `[typst]` extra also installs `typst>=0.14`, after which `MathTex` works out of the box. You only need LaTeX if you use `Tex` (whole-line text formulas).

### Vulkan on Windows

The Windows wheel bundles `vulkan_core.dll` — **you don't need a separate Vulkan SDK**. Vulkan drivers come from your GPU driver: just update the NVIDIA / AMD / Intel graphics driver to the latest. You only need the Vulkan SDK if you want to compile RTM's native parts yourself (`native/build.ps1`).

### Vulkan on macOS (MoltenVK)

macOS has no native Vulkan; RTM runs through **MoltenVK** (a Vulkan → Metal translation layer):

```bash
brew install molten-vk   # install MoltenVK with Homebrew
```

PyPI publishes a prebuilt macOS arm64 wheel, which `pip install` uses directly. If pip falls back to the sdist (Intel Mac, or an unmatched platform tag), the sdist ships the native sources plus a prebuilt `vulkan_core.dylib` and builds the wheel locally. On Apple Silicon, if that build fails, retry with this environment variable:

```bash
MACOSX_DEPLOYMENT_TARGET=12 python3 -m pip install real-time-manim
```

Building the native library from source is `bash native/build_mac.sh` (only needed for repo development).

## 4. Install ffmpeg (needed for video recording)

When recording, RTM relies on ffmpeg to composite the frames into an mp4, so ffmpeg must be on your `PATH`:

```bash
# macOS
brew install ffmpeg
```

```bash
# Windows: winget, or download from the official site and add it to PATH
winget install ffmpeg
```

Verify:

```bash
ffmpeg -version
```

## 5. (Optional) Install LaTeX

With typst installed, `MathTex` (inline formulas) doesn't need LaTeX; but `Tex` (whole-line formula text) **always** needs LaTeX:

| Platform | How to install | Size |
| --- | --- | --- |
| macOS | `brew install --cask mactex-no-gui` (or the lightweight BasicTeX) | Large (several GB) |
| Windows | Install [TeX Live](https://tug.org/texlive/) or MiKTeX | Large |

If you don't write `Tex` and only use `MathTex` + typst, skip this section.

## 6. Verify the installation

Save the code below as `main.py` and run it; if it produces an mp4, the whole chain works:

```python
from real_time_manim import *

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the scene to the window
        text = Text("Hello, real-time-manim!")
        win.play(FadeIn(text), run_time=1.0)   # fade in the text over 1 second
        win.close()   # close the window

fast_record_scene(Hello, "hello.mp4")# export to hello.mp4 in the project directory
```

```bash
python main.py
```

If it works, `hello.mp4` appears in the project directory and the console prints `[FastRecord] Saved: ...`.

## Common errors

| Error | Cause | Fix |
| --- | --- | --- |
| `FileNotFoundError: vulkan_core.dll not found...` | Missing native library | Windows: reinstall the wheel; macOS: run `bash native/build_mac.sh`, then reinstall |
| `RuntimeError: Vulkan_Init failed` | Vulkan device/driver initialization failed | Update the GPU driver (macOS: confirm `brew install molten-vk` succeeded) |
| `[Record] ffmpeg not found` | ffmpeg is not on the PATH | Install ffmpeg as in section 4 |
| `latex error converting to dvi` | Used `Tex`/`MathTex` without LaTeX | Install LaTeX, or install typst for `MathTex` (section 3) |

> Reminder: real-time-manim **ships** ManimCE 0.21.0 — don't `pip install manim` separately, and don't `import manim` before `import real_time_manim` (that makes RTM use the external manim copy). Always import from `real_time_manim`.

---

See also: [Quickstart](02-Quickstart.md) · [Recording methods](03-Recording-Methods.md)
