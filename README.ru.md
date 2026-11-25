# Real-Time-Manim (RTM)

<p align="center">
  <img src="banner.jpg" alt="Real-Time-Manim V2 banner" width="880"/>
</p>

<p align="center"><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.hi.md">हिन्दी</a> · <a href="README.es.md">Español</a> · <a href="README.pt-BR.md">Português</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a> · <b>Русский</b></p>

**Бэкенд рендеринга в реальном времени для [ManimCE](https://www.manim.community/),
ускоренный Vulkan.** RTM управляет собственной моделью `Mobject` / `Animation` из ManimCE через
нативный конвейер Vulkan, поэтому одну и ту же сцену можно смотреть **вживую**, мгновенно
переходить к любому кадру и записывать в MP4 в несколько раз быстрее стандартного рендерера.

**PyPI:** [pypi.org/project/real-time-manim](https://pypi.org/project/real-time-manim/)

> **Начните здесь:** [сайт проекта](https://team-axioviva.github.io/real-time-manim_website/) —
> обзор, демо и интерактивный граф wiki; [GitHub Wiki](https://github.com/Team-Axioviva/real-time-manim/wiki)
> — разбор на уровне исходного кода.
> Полное руководство на английском: [`RTM-Wiki/en_US/`](RTM-Wiki/en_US/README.md).
>
> **ИИ-агентам:** начните с [`RTM-Wiki/agent/README.md`](RTM-Wiki/agent/README.md) — весь API
> сжат в один справочник, удобный для grep, плюс [`gotchas.md`](RTM-Wiki/agent/gotchas.md),
> [`patterns.md`](RTM-Wiki/agent/patterns.md) и [`llms.txt`](llms.txt).

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

## Установка

```bash
pip install real-time-manim
pip install "real-time-manim[typst]"   # опционально: Typst-бэкенд в процессе
```

Пакет wheel содержит бинарник платформы (`vulkan_core.dll` в Windows, `vulkan_core.dylib` на Apple
Silicon); нативная сборка не нужна.
Нужны GPU/драйвер с Vulkan и `ffmpeg` в `PATH` для записи. **macOS** также требует MoltenVK во
время выполнения (`brew install molten-vk`); на Intel Mac dylib можно собрать командой
`bash native/build_mac.sh`.

---

## Быстрый старт

```python
from real_time_manim import Scene, Square, Create, Wait, BLUE, MLWindow
from real_time_manim.record import fast_record_scene

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)      # размер принудительно 1920x1080
        win.scene = self              # обязательно
        win.play(Create(Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)), run_time=1.0)
        win.play(Wait(0.5))
        win.close()                   # обязательно: сбрасывает и завершает кодировщик

fast_record_scene(Hello)              # -> ~/Downloads/output.mp4
```

`MLWindow` также является контекстным менеджером: `with MLWindow(...) as win:` закрывает окно
при выходе из блока.

> **Отдельно устанавливать ManimCE и делать `import manim` не нужно.** RTM включает ManimCE
> **0.21.0** и реэкспортирует всё пространство имён. Импортируйте `real_time_manim`, а не
> `manim`, иначе идентичность классов разделится.

---

## Возможности

- **Окно в реальном времени** — 1920×1080 @ 60 fps, без шага экспорта между кодом и картинкой.
- **Быстрая запись** — примерно **1,9–2,8×** быстрее ManimCE Cairo. Статические корни
  запекаются в одну текстуру на play, а `Wait` кодируется без перерисовки сцены.
- **Параллельные кадры** — `jobs="auto"` делит длинную сцену между воркерами; `prepare()` /
  `shared_prepare()` не дают повторять дорогую подготовку в каждом воркере.
- **Точный переход по кадрам** — любой кадр подготовленной сцены за O(1), через `FrameServer` /
  `FramePreview`.
- **3D с тестом глубины** — `MeshMobject` / `MeshBatch` / `MeshGroup` используют буфер глубины
  GPU, поэтому пересекающиеся и самозакрывающиеся поверхности решаются попиксельно. Затенение
  Manim, запечённое на CPU, или нативный материал с освещением.
- **Постобработка** — опциональные нативные bloom и тонмаппинг ACES/Reinhard.
- **Полный ManimCE** — существующие сцены работают без изменений, включая код с
  `from manim import ...`.
- **Математика без LaTeX** — `MathTex` направляется во встроенный **Typst**-бэкенд
  (`RTM_TYPST=0` отключает).

**Новое в 2.0.13:** обновление документации — переработанная страница пакета, README на
китайском и восстановленная история PR в `PR_HISTORY.md`. Движок не менялся: `native/`
идентичен 2.0.12, а `real_time_manim/` отличается только значением версии по умолчанию.

---

## 3D и постобработка

`MeshMobject` — настоящий mobject Manim, поэтому `shift`, `rotate` и `.animate` двигают сетку:

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

        mesh = MeshMobject.from_surface(surf, shade=True)   # освещение в стиле Manim
        self.add(mesh)
        win.play(mesh.animate.shift(0.4 * UP), run_time=1.0)
        win.close()
```

- Статическая сетка: `win.set_mesh(MeshBatch.from_surface(surf))` после
  `surf.set_shade_in_3d(False)`. Это снимок в мировом пространстве; не добавляйте Surface через
  `add`.
- Нативный материал: `MeshMobject.from_surface(surf, lit=True)` плюс
  `win.set_mesh_light(ambient=0.25, diffuse=0.9, specular=0.4, shininess=48)`.
  `shade=True` и `lit=True` взаимоисключающие.
- Bloom/tonemap: `win.set_post(bloom=0.8, threshold=0.75, tonemap="aces")`;
  `set_post(False)` выключает, `RTM_POST=1` включает везде.
- `from_surface()` запекает только непрозрачные квады; у сетки нет попиксельной сортировки
  прозрачности. `MeshBatch.MAX_QUADS = 131072`, одна нативная сетка на кадр.

---

## Три способа вывода

| вывод | API | примечания |
| --- | --- | --- |
| **Живое окно** | `MLWindow` | рендер и просмотр в реальном времени; без файла |
| **MP4** | `fast_record_scene` / `record_scene` | скрыто офлайн (быстрее всего) или видимо в реальном времени; `jobs=N` делит кадры |
| **PNG-кадры** | `FrameServer` / `FramePreview` | любой кадр в любой `t` за O(1), или скраббинг таймлайна |

```python
from real_time_manim import MLWindow, Square, Create, FrameServer, FramePreview
from real_time_manim.record import fast_record_scene, record_scene

# 1. Живое окно
win = MLWindow(1920, 1080)
win.scene = MyScene()
win.play(Create(Square()), run_time=1.0)
win.close()

# 2. MP4: скрыто/офлайн (быстрее всего), параллельно или видимо/в реальном времени
fast_record_scene(MyScene)
fast_record_scene(MyScene, "out.mp4", jobs=4)
record_scene(MyScene, "live.mp4")

# 3. PNG-кадры: один, список времён или интерактивный скраббинг
fs = FrameServer(MyScene)
fs.save_frame(2.5, "frame.png")
fs.export_frames("frames/", [0.0, 1.5, 3.0])
fs.close()
FramePreview(MyScene).run()
```

Рекордеры принимают подкласс / экземпляр `Scene` или callable без аргументов и возвращают
`{out_path, windows, files, with_audio}`. `jobs="auto"` делит только импортируемые сцены с одним
окном и не менее 240 кадрами; переносите дорогую чистую подготовку в `prepare()`, чтобы её
разделяли все воркеры.

---

## Ограничения

- Вывод **фиксирован на 1920×1080 @ 60 fps**; другие значения исправляются строкой
  `[rtm] forcing ...`.
- **Одно окно на процесс**; `win.scene = self` и `win.close()` обязательны (`atexit` — лишь
  резервный вариант, он не может сообщить об ошибках кодировщика).
- CLI `manim` нет — RTM это библиотека: `MLWindow`, рекордеры, `FrameServer`, `FramePreview`,
  `Timeline`.

---

## Контакты

Сообщения об ошибках и запросы функций: [открыть issue](https://github.com/Team-Axioviva/real-time-manim/issues).
Email: **axioviva@gmail.com**.

---

## Лицензия

[MIT](LICENSE). ManimCE, Vulkan и Typst принадлежат своим проектам.
