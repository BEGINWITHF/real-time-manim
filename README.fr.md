# Real-Time-Manim (RTM)

<p align="center">
  <img src="banner.jpg" alt="Real-Time-Manim V2 banner" width="880"/>
</p>

<p align="center"><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <a href="README.es.md">Español</a> · <a href="README.pt-BR.md">Português</a> · <b>Français</b> · <a href="README.de.md">Deutsch</a> · <a href="README.ru.md">Русский</a></p>

Un **backend de rendu temps réel pour [ManimCE](https://www.manim.community/) accéléré par
Vulkan**. RTM pilote le modèle `Mobject` / `Animation` de ManimCE à travers un pipeline Vulkan
natif : une même scène peut donc être vue **en direct**, positionnée instantanément sur n'importe
quelle image et enregistrée en MP4 plusieurs fois plus vite que le moteur par défaut.

**PyPI :** [pypi.org/project/real-time-manim](https://pypi.org/project/real-time-manim/)

> **Commencez ici :** le [site du projet](https://team-axioviva.github.io/real-time-manim_website/)
> pour la présentation, les démos et le graphe wiki interactif, et le
> [GitHub Wiki](https://github.com/Team-Axioviva/real-time-manim/wiki) pour le parcours au niveau
> du code.
>
> **Agents IA :** commencez par [`RTM-Wiki/agent/README.md`](RTM-Wiki/agent/README.md) — toute
> l'API condensée en une référence facile à grep, avec [`gotchas.md`](RTM-Wiki/agent/gotchas.md),
> [`patterns.md`](RTM-Wiki/agent/patterns.md) et [`llms.txt`](llms.txt).

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
pip install "real-time-manim[typst]"   # facultatif : backend Typst en processus
```

La wheel contient le binaire de la plateforme (`vulkan_core.dll` sous Windows,
`vulkan_core.dylib` sur Apple Silicon) ; aucune compilation native n'est nécessaire.
Il faut un GPU/driver Vulkan, et `ffmpeg` dans le `PATH` pour enregistrer. **macOS** requiert
aussi MoltenVK à l'exécution (`brew install molten-vk`) ; sur Mac Intel, vous pouvez compiler le
dylib avec `bash native/build_mac.sh`.

---

## Démarrage rapide

```python
from real_time_manim import Scene, Square, Create, Wait, BLUE, MLWindow
from real_time_manim.record import fast_record_scene

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)      # la taille est forcée à 1920x1080
        win.scene = self              # obligatoire
        win.play(Create(Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)), run_time=1.0)
        win.play(Wait(0.5))
        win.close()                   # obligatoire : vide et termine l'encodeur

fast_record_scene(Hello)              # -> ~/Downloads/output.mp4
```

`MLWindow` est aussi un gestionnaire de contexte : `with MLWindow(...) as win:` le ferme en
sortant du bloc.

> **Pas besoin d'installer ManimCE séparément, ni de faire `import manim`.** RTM embarque
> ManimCE **0.21.0** et réexporte tout son namespace. Importez `real_time_manim`, pas `manim`,
> sinon l'identité des classes se scinde.

---

## Points forts

- **Fenêtre temps réel** — 1920×1080 @ 60 fps, sans étape d'export entre le code et l'image.
- **Enregistrement rapide** — environ **1.9–2.8×** plus rapide que ManimCE Cairo. Les racines
  statiques sont cuites dans une texture par play et un `Wait` est encodé sans redessiner la
  scène.
- **Images en parallèle** — `jobs="auto"` répartit une longue scène entre plusieurs workers ;
  `prepare()` / `shared_prepare()` évitent de répéter la préparation coûteuse dans chaque worker.
- **Navigation exacte** — n'importe quelle image d'une scène préparée en O(1), via `FrameServer` /
  `FramePreview`.
- **3D avec test de profondeur** — `MeshMobject` / `MeshBatch` / `MeshGroup` utilisent un buffer
  de profondeur GPU : les surfaces qui se croisent ou s'auto-occultent sont résolues pixel par
  pixel. Ombrage Manim cuit en CPU ou matériau éclairé natif.
- **Post-traitement** — bloom natif optionnel et tonemapping ACES/Reinhard.
- **ManimCE complet** — les scènes existantes fonctionnent sans modification, y compris le code
  avec `from manim import ...`.
- **Maths sans LaTeX** — `MathTex` est routé vers un backend **Typst** en processus
  (`RTM_TYPST=0` pour le désactiver).

**Nouveautés 2.0.13 :** mise à jour de la documentation — page du paquet repensée, README en
chinois et historique des PR récupéré dans `PR_HISTORY.md`. Aucun changement moteur : `native/`
est identique à 2.0.12 et `real_time_manim/` ne diffère que par la valeur de repli de version.

---

## 3D et post-traitement

`MeshMobject` est un vrai mobject Manim : `shift`, `rotate` et `.animate` déplacent le maillage :

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

        mesh = MeshMobject.from_surface(surf, shade=True)   # éclairage style Manim
        self.add(mesh)
        win.play(mesh.animate.shift(0.4 * UP), run_time=1.0)
        win.close()
```

- Maillage statique : `win.set_mesh(MeshBatch.from_surface(surf))` après
  `surf.set_shade_in_3d(False)`. C'est un instantané dans l'espace monde ; ne faites pas `add` de
  la surface.
- Matériau natif : `MeshMobject.from_surface(surf, lit=True)` plus
  `win.set_mesh_light(ambient=0.25, diffuse=0.9, specular=0.4, shininess=48)`.
  `shade=True` et `lit=True` sont mutuellement exclusifs.
- Bloom/tonemap : `win.set_post(bloom=0.8, threshold=0.75, tonemap="aces")` ;
  `set_post(False)` désactive, `RTM_POST=1` active partout.
- `from_surface()` ne cuit que des quads opaques ; le maillage n'a pas de tri de transparence par
  pixel. `MeshBatch.MAX_QUADS = 131072`, un maillage natif par image.

---

## Trois sorties possibles

| sortie | API | notes |
| --- | --- | --- |
| **Fenêtre live** | `MLWindow` | rendu et visionnage en temps réel ; aucun fichier |
| **MP4** | `fast_record_scene` / `record_scene` | caché hors ligne (le plus rapide) ou visible temps réel ; `jobs=N` découpe les images |
| **Images PNG** | `FrameServer` / `FramePreview` | n'importe quelle image à n'importe quel `t` en O(1), ou scrub de la timeline |

```python
from real_time_manim import MLWindow, Square, Create, FrameServer, FramePreview
from real_time_manim.record import fast_record_scene, record_scene

# 1. Fenêtre live
win = MLWindow(1920, 1080)
win.scene = MyScene()
win.play(Create(Square()), run_time=1.0)
win.close()

# 2. MP4 : caché/hors ligne (le plus rapide), parallèle ou visible/temps réel
fast_record_scene(MyScene)
fast_record_scene(MyScene, "out.mp4", jobs=4)
record_scene(MyScene, "live.mp4")

# 3. Images PNG : une seule, une liste de temps ou scrub interactif
fs = FrameServer(MyScene)
fs.save_frame(2.5, "frame.png")
fs.export_frames("frames/", [0.0, 1.5, 3.0])
fs.close()
FramePreview(MyScene).run()
```

Les enregistreurs acceptent une sous-classe / instance de `Scene` ou un callable sans argument et
renvoient `{out_path, windows, files, with_audio}`. `jobs="auto"` ne découpe que les scènes
importables à fenêtre unique d'au moins 240 images ; déplacez la préparation pure coûteuse dans
`prepare()` pour que chaque worker la partage.

---

## Contraintes

- La sortie est **fixée à 1920×1080 @ 60 fps** ; les autres valeurs sont corrigées avec une ligne
  `[rtm] forcing ...`.
- **Une fenêtre par processus** ; `win.scene = self` et `win.close()` sont obligatoires (`atexit`
  n'est qu'un repli au mieux et ne peut pas signaler les erreurs d'encodeur).
- Il n'y a pas de CLI `manim` — RTM est une bibliothèque : `MLWindow`, les enregistreurs,
  `FrameServer`, `FramePreview`, `Timeline`.

---

## Contact

Rapports de bugs et demandes : [ouvrez un issue](https://github.com/Team-Axioviva/real-time-manim/issues).
E-mail : **axioviva@gmail.com**.

---

## Licence

[MIT](LICENSE). ManimCE, Vulkan et Typst appartiennent à leurs projets respectifs.
