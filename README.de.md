# Real-Time-Manim (RTM)

<p align="center">
  <img src="banner.jpg" alt="Real-Time-Manim V2 banner" width="880"/>
</p>

<p align="center"><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.hi.md">हिन्दी</a> · <a href="README.es.md">Español</a> · <a href="README.pt-BR.md">Português</a> · <a href="README.fr.md">Français</a> · <b>Deutsch</b> · <a href="README.ru.md">Русский</a></p>

Ein **Vulkan-beschleunigtes Echtzeit-Rendering-Backend für
[ManimCE](https://www.manim.community/)**. RTM treibt ManimCEs eigenes `Mobject` /
`Animation`-Modell über eine native Vulkan-Pipeline an, sodass dieselbe Szene **live** angesehen,
sofort auf jeden Frame gesprungen und mehrere Male schneller als der Standard-Renderer als MP4
aufgezeichnet werden kann.

**PyPI:** [pypi.org/project/real-time-manim](https://pypi.org/project/real-time-manim/)

> **Hier starten:** die [Projektwebsite](https://team-axioviva.github.io/real-time-manim_website/)
> für Überblick, Demos und den interaktiven Wiki-Graphen, und das
> [GitHub Wiki](https://github.com/Team-Axioviva/real-time-manim/wiki) für den Durchgang auf
> Quellcode-Ebene.
> Das vollständige englische Handbuch liegt in [`RTM-Wiki/en_US/`](RTM-Wiki/en_US/README.md).
>
> **KI-Agenten:** beginnt mit [`RTM-Wiki/agent/README.md`](RTM-Wiki/agent/README.md) — die
> gesamte API in einer grep-freundlichen Referenz, dazu
> [`gotchas.md`](RTM-Wiki/agent/gotchas.md), [`patterns.md`](RTM-Wiki/agent/patterns.md) und
> [`llms.txt`](llms.txt).

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
[![PyPI](https://img.shields.io/pypi/v/real-time-manim.svg)](https://pypi.org/project/real-time-manim/)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2B%20%7C%20macOS-lightgrey.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-brightgreen.svg)
[![PyPI downloads](https://img.shields.io/pypi/dm/real-time-manim.svg)](https://pypi.org/project/real-time-manim/)
![GitHub stars](https://img.shields.io/github/stars/Team-Axioviva/real-time-manim.svg)
![Last commit](https://img.shields.io/github/last-commit/Team-Axioviva/real-time-manim.svg)
![Backend: Vulkan](https://img.shields.io/badge/Backend-Vulkan-red.svg)
![ManimCE](https://img.shields.io/badge/ManimCE-0.21.0-yellow.svg)
![AI agents](https://img.shields.io/badge/AI%20agents-llms.txt-blueviolet.svg)
![Website](https://img.shields.io/badge/Website-live-brightgreen.svg)
![Wiki](https://img.shields.io/badge/Wiki-GitHub-blue.svg)

---

## Installation

```bash
pip install real-time-manim
pip install "real-time-manim[typst]"   # optional: prozessinternes Typst-Backend
```

Das Wheel enthält das Plattform-Binary (`vulkan_core.dll` unter Windows,
`vulkan_core.dylib` auf Apple Silicon); ein nativer Build ist nicht nötig.
Du brauchst eine Vulkan-fähige GPU/treiber und `ffmpeg` im `PATH` zum Aufzeichnen.
**macOS** benötigt zur Laufzeit zusätzlich MoltenVK (`brew install molten-vk`); auf Intel-Macs
kannst du die dylib mit `bash native/build_mac.sh` selbst bauen.

---

## Schnellstart

```python
from real_time_manim import Scene, Square, Create, Wait, BLUE, MLWindow
from real_time_manim.record import fast_record_scene

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)      # Größe wird auf 1920x1080 erzwungen
        win.scene = self              # erforderlich
        win.play(Create(Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)), run_time=1.0)
        win.play(Wait(0.5))
        win.close()                   # erforderlich: leert und beendet den Encoder

fast_record_scene(Hello)              # -> ~/Downloads/output.mp4
```

`MLWindow` ist auch ein Context Manager: `with MLWindow(...) as win:` schließt es beim Verlassen
des Blocks.

> **Keine separate ManimCE-Installation und kein `import manim`.** RTM bündelt ManimCE
> **0.21.0** und re-exportiert den gesamten Namespace. Importiere `real_time_manim`, nicht
> `manim`, sonst spaltet sich die Klassenidentität.

---

## Highlights

- **Echtzeitfenster** — 1920×1080 @ 60 fps, kein Export-Schritt zwischen Code und Bild.
- **Schnelle Aufzeichnung** — rund **1,9–2,8×** schneller als ManimCE Cairo. Statische Wurzeln
  werden pro Play in eine Textur gebacken und ein `Wait` wird ohne Neuzeichnen der Szene kodiert.
- **Parallele Frames** — `jobs="auto"` teilt eine lange Szene auf Worker auf; `prepare()` /
  `shared_prepare()` verhindern, dass teure Vorbereitung in jedem Worker wiederholt wird.
- **Framegenaues Seek** — jeder Frame einer vorbereiteten Szene in O(1), über `FrameServer` /
  `FramePreview`.
- **Tiefengetestetes 3D** — `MeshMobject` / `MeshBatch` / `MeshGroup` nutzen einen
  GPU-Tiefenpuffer, sodass sich schneidende und selbst verdeckende Flächen pixelgenau aufgelöst
  werden. CPU-gebackenes Manim-Shading oder natives Lit-Material.
- **Post-Processing** — optionales natives Bloom und ACES/Reinhard-Tonemapping.
- **Vollständiges ManimCE** — bestehende Szenen laufen unverändert, auch Code mit
  `from manim import ...`.
- **Mathe ohne LaTeX** — `MathTex` wird an ein prozessinternes **Typst**-Backend geleitet
  (`RTM_TYPST=0` deaktiviert es).

**Neu in 2.0.13:** Dokumentations-Update — neu gestaltete Paketseite, chinesisches README und
wiederhergestellte PR-Historie in `PR_HISTORY.md`. Keine Engine-Änderungen: `native/` ist
identisch zu 2.0.12, `real_time_manim/` unterscheidet sich nur im Versions-Fallback.

---

## 3D und Post-Processing

`MeshMobject` ist ein echtes Manim-Mobject: `shift`, `rotate` und `.animate` bewegen das Mesh:

```python
import numpy as np
from real_time_manim import (
    ThreeDScene, Surface, MeshMobject, BLUE, UP, DEGREES, MLWindow,
)

class Terrain(ThreeDScene):
    def construct(self):
        win = MLWindow(1920, 1080)
        win.scene = self
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)

        surf = Surface(
            lambda u, v: np.array([u, v, 0.35 * np.sin(2 * u) * np.cos(2 * v)]),
            u_range=(-2, 2), v_range=(-2, 2), resolution=(48, 48), fill_color=BLUE,
        ).set_stroke(width=0)

        mesh = MeshMobject.from_surface(surf, shade=True)   # Manim-artige Beleuchtung
        self.add(mesh)
        win.play(mesh.animate.shift(0.4 * UP), run_time=1.0)
        win.close()
```

- Statisches Mesh: `win.set_mesh(MeshBatch.from_surface(surf))` nach
  `surf.set_shade_in_3d(False)`. Es ist ein Snapshot im Weltraum; die Surface nicht zusätzlich
  `add`en.
- Natives Material: `MeshMobject.from_surface(surf, lit=True)` plus
  `win.set_mesh_light(ambient=0.25, diffuse=0.9, specular=0.4, shininess=48)`.
  `shade=True` und `lit=True` schließen sich gegenseitig aus.
- Bloom/tonemap: `win.set_post(bloom=0.8, threshold=0.75, tonemap="aces")`;
  `set_post(False)` deaktiviert, `RTM_POST=1` aktiviert überall.
- `from_surface()` backt nur opake Quads; das Mesh hat keine pixelgenaue Transparenzsortierung.
  `MeshBatch.MAX_QUADS = 131072`, ein natives Mesh pro Frame.

---

## Drei Ausgabeformen

| Ausgabe | API | Hinweise |
| --- | --- | --- |
| **Live-Fenster** | `MLWindow` | in Echtzeit rendern und ansehen; keine Datei |
| **MP4** | `fast_record_scene` / `record_scene` | versteckt offline (am schnellsten) oder sichtbar in Echtzeit; `jobs=N` teilt Frames |
| **PNG-Frames** | `FrameServer` / `FramePreview` | jeder Frame zu jedem `t` in O(1), oder Timeline-Scrubbing |

```python
from real_time_manim import MLWindow, Square, Create, FrameServer, FramePreview
from real_time_manim.record import fast_record_scene, record_scene

# 1. Live-Fenster
win = MLWindow(1920, 1080)
win.scene = MyScene()
win.play(Create(Square()), run_time=1.0)
win.close()

# 2. MP4: versteckt/offline (am schnellsten), parallel oder sichtbar/Echtzeit
fast_record_scene(MyScene)
fast_record_scene(MyScene, "out.mp4", jobs=4)
record_scene(MyScene, "live.mp4")

# 3. PNG-Frames: einer, eine Zeitliste oder interaktives Scrubben
fs = FrameServer(MyScene)
fs.save_frame(2.5, "frame.png")
fs.export_frames("frames/", [0.0, 1.5, 3.0])
fs.close()
FramePreview(MyScene).run()
```

Die Recorder akzeptieren eine `Scene`-Unterklasse / -Instanz oder ein Callable ohne Argumente und
liefern `{out_path, windows, files, with_audio}`. `jobs="auto"` teilt nur importierbare
Einzelfenster-Szenen mit mindestens 240 Frames; verschiebe teure reine Vorbereitung in
`prepare()`, damit jeder Worker sie teilt.

---

## Einschränkungen

- Die Ausgabe ist **fest auf 1920×1080 @ 60 fps**; andere Werte werden mit einer
  `[rtm] forcing ...`-Zeile korrigiert.
- **Ein Fenster pro Prozess**; `win.scene = self` und `win.close()` sind erforderlich (`atexit`
  ist nur ein Best-Effort-Fallback und kann Encoder-Fehler nicht melden).
- Es gibt keine `manim`-CLI — RTM ist eine Bibliothek: `MLWindow`, die Recorder, `FrameServer`,
  `FramePreview`, `Timeline`.

---

## Kontakt

Bug-Reports und Feature-Wünsche: [Issue öffnen](https://github.com/Team-Axioviva/real-time-manim/issues).
E-Mail: **axioviva@gmail.com**.

---

## Lizenz

[MIT](LICENSE). ManimCE, Vulkan und Typst gehören ihren jeweiligen Projekten.
