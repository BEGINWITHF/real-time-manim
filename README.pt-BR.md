# Real-Time-Manim (RTM)

<p align="center">
  <img src="banner.jpg" alt="Real-Time-Manim V2 banner" width="880"/>
</p>

<p align="center"><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.es.md">Español</a> · <b>Português</b> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a> · <a href="README.ru.md">Русский</a></p>

Um **backend de renderização em tempo real para o [ManimCE](https://www.manim.community/)
acelerado por Vulkan**. O RTM conduz o próprio modelo `Mobject` / `Animation` do ManimCE por um
pipeline Vulkan nativo, então a mesma cena pode ser assistida **ao vivo**, avançar para qualquer
quadro instantaneamente e ser gravada em MP4 várias vezes mais rápido que o renderizador padrão.

**PyPI:** [pypi.org/project/real-time-manim](https://pypi.org/project/real-time-manim/)

> **Comece por aqui:** o [site do projeto](https://team-axioviva.github.io/real-time-manim_website/)
> para visão geral, demos e o grafo wiki interativo, e a
> [GitHub Wiki](https://github.com/Team-Axioviva/real-time-manim/wiki) para o passo a passo no
> nível do código.
> O manual completo em inglês está em [`RTM-Wiki/en_US/`](RTM-Wiki/en_US/README.md).
>
> **Agentes de IA:** comece por [`RTM-Wiki/agent/README.md`](RTM-Wiki/agent/README.md) — a API
> inteira condensada em uma referência fácil de grep, com [`gotchas.md`](RTM-Wiki/agent/gotchas.md),
> [`patterns.md`](RTM-Wiki/agent/patterns.md) e [`llms.txt`](llms.txt).

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

## Instalação

```bash
pip install real-time-manim
pip install "real-time-manim[typst]"   # opcional: backend Typst em processo
```

A wheel inclui o binário da plataforma (`vulkan_core.dll` no Windows, `vulkan_core.dylib` no
Apple Silicon); não é preciso compilar nada.
Você precisa de uma GPU/driver com Vulkan e `ffmpeg` no `PATH` para gravar. **macOS** também
requer MoltenVK em tempo de execução (`brew install molten-vk`); em Macs Intel você pode compilar
o dylib com `bash native/build_mac.sh`.

---

## Início rápido

```python
from real_time_manim import Scene, Square, Create, Wait, BLUE, MLWindow
from real_time_manim.record import fast_record_scene

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)      # o tamanho é forçado para 1920x1080
        win.scene = self              # obrigatório
        win.play(Create(Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)), run_time=1.0)
        win.play(Wait(0.5))
        win.close()                   # obrigatório: descarrega e finaliza o codificador

fast_record_scene(Hello)              # -> ~/Downloads/output.mp4
```

`MLWindow` também é um gerenciador de contexto: `with MLWindow(...) as win:` fecha a janela ao
sair do bloco.

> **Não é preciso instalar o ManimCE separadamente nem fazer `import manim`.** O RTM inclui o
> ManimCE **0.21.0** e reexporta todo o seu namespace. Importe `real_time_manim`, não `manim`, ou
> a identidade das classes se divide.

---

## Destaques

- **Janela em tempo real** — 1920×1080 @ 60 fps, sem etapa de exportação entre o código e a
  imagem.
- **Gravação rápida** — cerca de **1.9–2.8×** mais rápida que o ManimCE Cairo. As raízes
  estáticas são assadas em uma textura por play e um `Wait` é codificado sem redesenhar a cena.
- **Quadros em paralelo** — `jobs="auto"` divide uma cena longa entre workers;
  `prepare()` / `shared_prepare()` evitam repetir a preparação cara em cada worker.
- **Busca exata de quadros** — qualquer quadro de uma cena preparada em O(1), com `FrameServer` /
  `FramePreview`.
- **3D com teste de profundidade** — `MeshMobject` / `MeshBatch` / `MeshGroup` usam um buffer de
  profundidade da GPU, então superfícies que se cruzam ou se auto-ocultam são resolvidas pixel a
  pixel. Sombreado Manim assado na CPU ou material iluminado nativo.
- **Pós-processamento** — bloom nativo opcional e tonemapping ACES/Reinhard.
- **ManimCE completo** — cenas existentes funcionam sem mudanças, incluindo código com
  `from manim import ...`.
- **Matemática sem LaTeX** — `MathTex` é roteado para um backend **Typst** em processo
  (`RTM_TYPST=0` para desativar).

**Novidades em 2.0.13:** atualização de documentação — página do pacote redesenhada, README em
chinês e histórico de PR recuperado em `PR_HISTORY.md`. Sem mudanças no motor: `native/` é
idêntico ao 2.0.12 e `real_time_manim/` difere apenas no valor de fallback da versão.

---

## 3D e pós-processamento

`MeshMobject` é um mobject real do Manim, então `shift`, `rotate` e `.animate` movem a malha:

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

        mesh = MeshMobject.from_surface(surf, shade=True)   # iluminação estilo Manim
        self.add(mesh)
        win.play(mesh.animate.shift(0.4 * UP), run_time=1.0)
        win.close()
```

- Malha estática: `win.set_mesh(MeshBatch.from_surface(surf))` depois de
  `surf.set_shade_in_3d(False)`. É um snapshot no espaço do mundo; não faça `add` da superfície.
- Material nativo: `MeshMobject.from_surface(surf, lit=True)` mais
  `win.set_mesh_light(ambient=0.25, diffuse=0.9, specular=0.4, shininess=48)`.
  `shade=True` e `lit=True` são mutuamente exclusivos.
- Bloom/tonemap: `win.set_post(bloom=0.8, threshold=0.75, tonemap="aces")`;
  `set_post(False)` desativa e `RTM_POST=1` ativa em tudo.
- `from_surface()` só assa quads opacos; a malha não ordena transparência por pixel.
  `MeshBatch.MAX_QUADS = 131072`, uma malha nativa por quadro.

---

## Três formas de saída

| saída | API | notas |
| --- | --- | --- |
| **Janela ao vivo** | `MLWindow` | renderiza e assiste em tempo real; sem arquivo |
| **MP4** | `fast_record_scene` / `record_scene` | oculto offline (mais rápido) ou visível em tempo real; `jobs=N` divide quadros |
| **Quadros PNG** | `FrameServer` / `FramePreview` | qualquer quadro em qualquer `t` em O(1), ou scrubbing da linha do tempo |

```python
from real_time_manim import MLWindow, Square, Create, FrameServer, FramePreview
from real_time_manim.record import fast_record_scene, record_scene

# 1. Janela ao vivo
win = MLWindow(1920, 1080)
win.scene = MyScene()
win.play(Create(Square()), run_time=1.0)
win.close()

# 2. MP4: oculto/offline (mais rápido), paralelo ou visível/tempo real
fast_record_scene(MyScene)
fast_record_scene(MyScene, "out.mp4", jobs=4)
record_scene(MyScene, "live.mp4")

# 3. Quadros PNG: um, uma lista de tempos ou scrubbing interativo
fs = FrameServer(MyScene)
fs.save_frame(2.5, "frame.png")
fs.export_frames("frames/", [0.0, 1.5, 3.0])
fs.close()
FramePreview(MyScene).run()
```

Os gravadores aceitam uma subclasse / instância de `Scene` ou um callable sem argumentos e
retornam `{out_path, windows, files, with_audio}`. `jobs="auto"` só divide cenas importáveis de
janela única com pelo menos 240 quadros; mova a preparação pura cara para `prepare()` para que
cada worker a compartilhe.

---

## Restrições

- A saída é **fixa em 1920×1080 @ 60 fps**; outros valores são corrigidos com uma linha
  `[rtm] forcing ...`.
- **Uma janela por processo**; `win.scene = self` e `win.close()` são obrigatórios (`atexit` é
  apenas um fallback de melhor esforço e não consegue relatar erros do codificador).
- Não há CLI `manim` — o RTM é uma biblioteca: `MLWindow`, os gravadores, `FrameServer`,
  `FramePreview`, `Timeline`.

---

## Contato

Relatos de bugs e pedidos de recursos: [abra um issue](https://github.com/Team-Axioviva/real-time-manim/issues).
E-mail: **axioviva@gmail.com**.

---

## Licença

[MIT](LICENSE). ManimCE, Vulkan e Typst pertencem aos seus respectivos projetos.
