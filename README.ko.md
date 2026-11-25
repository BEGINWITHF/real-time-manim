# Real-Time-Manim (RTM)

<p align="center">
  <img src="banner.jpg" alt="Real-Time-Manim V2 banner" width="880"/>
</p>

<p align="center"><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.ja.md">日本語</a> · <b>한국어</b> · <a href="README.hi.md">हिन्दी</a> · <a href="README.es.md">Español</a> · <a href="README.pt-BR.md">Português</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a> · <a href="README.ru.md">Русский</a></p>

**Vulkan으로 가속되는 [ManimCE](https://www.manim.community/) 실시간 렌더링 백엔드**입니다.
RTM은 ManimCE 자체의 `Mobject` / `Animation` 모델을 네이티브 Vulkan 파이프라인으로 구동하므로,
같은 장면을 **실시간으로 보여 주고**, 임의의 프레임으로 즉시 이동하며, 기본 렌더러보다 몇 배
빠르게 MP4로 녹화할 수 있습니다.

**PyPI:** [pypi.org/project/real-time-manim](https://pypi.org/project/real-time-manim/)

> **여기서 시작하세요:** 개요, 데모, 인터랙티브 wiki 그래프는
> [프로젝트 웹사이트](https://team-axioviva.github.io/real-time-manim_website/)에서,
> 소스 수준 설명은
> [GitHub Wiki](https://github.com/Team-Axioviva/real-time-manim/wiki)에서 볼 수 있습니다.
> 전체 영어 매뉴얼은 [`RTM-Wiki/en_US/`](RTM-Wiki/en_US/README.md)에 있습니다.
>
> **AI 에이전트:** 먼저 [`RTM-Wiki/agent/README.md`](RTM-Wiki/agent/README.md)를 읽으세요.
> 전체 API를 grep하기 쉬운 하나의 레퍼런스로 정리했으며,
> [`gotchas.md`](RTM-Wiki/agent/gotchas.md), [`patterns.md`](RTM-Wiki/agent/patterns.md),
> [`llms.txt`](llms.txt)도 함께 제공합니다.

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

## 설치

```bash
pip install real-time-manim
pip install "real-time-manim[typst]"   # 선택: 프로세스 내 Typst 수식 백엔드
```

wheel에는 플랫폼용 네이티브 바이너리(Windows는 `vulkan_core.dll`, Apple Silicon은
`vulkan_core.dylib`)가 포함되어 있어 네이티브 빌드가 필요 없습니다.
Vulkan을 지원하는 GPU/드라이버가 필요하고, 녹화에는 `ffmpeg`가 `PATH`에 있어야 합니다.
**macOS**는 런타임에 MoltenVK도 필요합니다(`brew install molten-vk`). Intel Mac에서는
`bash native/build_mac.sh`로 dylib을 직접 빌드할 수 있습니다.

---

## 빠른 시작

```python
from real_time_manim import Scene, Square, Create, Wait, BLUE, MLWindow
from real_time_manim.record import fast_record_scene

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)      # 크기는 1920x1080으로 강제됩니다
        win.scene = self              # 필수
        win.play(Create(Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)), run_time=1.0)
        win.play(Wait(0.5))
        win.close()                   # 필수: 플러시하고 인코더를 종료

fast_record_scene(Hello)              # -> ~/Downloads/output.mp4
```

`MLWindow`는 컨텍스트 관리자로도 쓸 수 있습니다. `with MLWindow(...) as win:`은 블록을
벗어날 때 자동으로 닫습니다.

> **ManimCE를 따로 설치할 필요가 없고, `import manim`도 하지 마세요.** RTM은 ManimCE
> **0.21.0**을 내장하고 전체 네임스페이스를 다시 내보냅니다. `manim`이 아니라
> `real_time_manim`을 임포트하세요. 그렇지 않으면 클래스 identity가 갈라집니다.

---

## 하이라이트

- **실시간 창** — 1920×1080 @ 60 fps. 코드와 화면 사이에 내보내기 단계가 없습니다.
- **빠른 녹화** — ManimCE Cairo보다 약 **1.9–2.8배** 빠릅니다. play마다 정적인 루트를 하나의
  텍스처로 베이크하고, `Wait`는 장면을 다시 그리지 않고 인코딩합니다.
- **프레임 병렬화** — `jobs="auto"`가 긴 장면을 여러 워커로 나눕니다. `prepare()` /
  `shared_prepare()`로 비싼 준비 작업을 워커마다 반복하지 않습니다.
- **프레임 단위 탐색** — 준비된 장면의 임의 프레임을 O(1)로 가져옵니다.
  `FrameServer` / `FramePreview`.
- **깊이 테스트 3D** — `MeshMobject` / `MeshBatch` / `MeshGroup`이 GPU 깊이 버퍼를 사용해
  교차하거나 자기 자신을 가리는 표면을 픽셀 단위로 해결합니다. CPU 베이크 Manim 셰이딩 또는
  네이티브 조명 머티리얼을 선택할 수 있습니다.
- **후처리** — 선택적인 네이티브 bloom과 ACES/Reinhard 톤매핑.
- **완전한 ManimCE** — 기존 장면이 그대로 동작하며, `from manim import ...` 코드도 포함합니다.
- **LaTeX 없는 수식** — `MathTex`는 프로세스 내 **Typst** 백엔드로 라우팅됩니다
  (`RTM_TYPST=0`으로 비활성화).

**2.0.13의 새로운 점:** 문서 업데이트 — 패키지 페이지 재설계, 중국어 README 추가,
`PR_HISTORY.md`의 PR 기록 복원. 엔진 변경은 없습니다. `native/`는 2.0.12와 동일하고,
`real_time_manim/`은 버전 폴백 값만 다릅니다.

---

## 3D와 후처리

`MeshMobject`는 실제 Manim mobject이므로 `shift`, `rotate`, `.animate`가 메시를 움직입니다:

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

        mesh = MeshMobject.from_surface(surf, shade=True)   # Manim 스타일 조명
        self.add(mesh)
        win.play(mesh.animate.shift(0.4 * UP), run_time=1.0)
        win.close()
```

- 정적 메시: `surf.set_shade_in_3d(False)` 후
  `win.set_mesh(MeshBatch.from_surface(surf))`. 월드 공간 스냅샷이므로 Surface를
  `add`하지 마세요.
- 네이티브 머티리얼: `MeshMobject.from_surface(surf, lit=True)`와
  `win.set_mesh_light(ambient=0.25, diffuse=0.9, specular=0.4, shininess=48)`.
  `shade=True`와 `lit=True`는 함께 쓸 수 없습니다.
- Bloom/tonemap: `win.set_post(bloom=0.8, threshold=0.75, tonemap="aces")`.
  `set_post(False)`로 끄고, `RTM_POST=1`로 전역 활성화합니다.
- `from_surface()`는 불투명 사각형만 베이크합니다. mesh에는 픽셀 단위 투명 정렬이 없습니다.
  `MeshBatch.MAX_QUADS = 131072`, 프레임당 하나의 네이티브 메시입니다.

---

## 세 가지 출력 방법

| 출력 | API | 설명 |
| --- | --- | --- |
| **실시간 창** | `MLWindow` | 실시간으로 렌더링해 보기. 파일 없음 |
| **MP4** | `fast_record_scene` / `record_scene` | 숨김 오프라인(가장 빠름) 또는 표시 실시간. `jobs=N`으로 프레임 분할 |
| **PNG 프레임** | `FrameServer` / `FramePreview` | 임의 `t`의 프레임을 O(1)로 내보내거나 타임라인 스크럽 |

```python
from real_time_manim import MLWindow, Square, Create, FrameServer, FramePreview
from real_time_manim.record import fast_record_scene, record_scene

# 1. 실시간 창
win = MLWindow(1920, 1080)
win.scene = MyScene()
win.play(Create(Square()), run_time=1.0)
win.close()

# 2. MP4: 숨김 오프라인(가장 빠름), 병렬, 또는 표시 실시간
fast_record_scene(MyScene)
fast_record_scene(MyScene, "out.mp4", jobs=4)
record_scene(MyScene, "live.mp4")

# 3. PNG 프레임: 한 장, 시간 목록, 또는 인터랙티브 스크럽
fs = FrameServer(MyScene)
fs.save_frame(2.5, "frame.png")
fs.export_frames("frames/", [0.0, 1.5, 3.0])
fs.close()
FramePreview(MyScene).run()
```

레코더는 `Scene` 서브클래스 / 인스턴스 / 인자 없는 callable을 받고
`{out_path, windows, files, with_audio}`를 반환합니다. `jobs="auto"`는 임포트 가능하고
단일 창이며 240프레임 이상인 장면만 분할합니다. 비싼 순수 데이터 준비는 `prepare()`로 옮겨
모든 워커가 공유하게 하세요.

---

## 제약

- 출력은 **1920×1080 @ 60 fps로 고정**됩니다. 다른 값은 `[rtm] forcing ...`을 출력하고
  보정됩니다.
- **프로세스당 하나의 창**만 허용됩니다. `win.scene = self`와 `win.close()`가 필수입니다
  (`atexit`은 최선 노력 폴백일 뿐이며 인코더 오류를 보고할 수 없습니다).
- `manim` CLI는 없습니다. RTM은 라이브러리입니다: `MLWindow`, 레코더, `FrameServer`,
  `FramePreview`, `Timeline`.

---

## 문의

버그 보고 및 기능 요청: [issue 열기](https://github.com/Team-Axioviva/real-time-manim/issues).
이메일: **axioviva@gmail.com**.

---

## 라이선스

[MIT](LICENSE). ManimCE, Vulkan, Typst는 각 프로젝트에 귀속됩니다.
