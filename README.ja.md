# Real-Time-Manim (RTM)

<p align="center">
  <img src="banner.jpg" alt="Real-Time-Manim V2 banner" width="880"/>
</p>

<p align="center"><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <b>日本語</b> · <a href="README.ko.md">한국어</a> · <a href="README.es.md">Español</a> · <a href="README.pt-BR.md">Português</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a> · <a href="README.ru.md">Русский</a></p>

**Vulkan で高速化された [ManimCE](https://www.manim.community/) のリアルタイムレンダリング
バックエンド**です。RTM は ManimCE 自身の `Mobject` / `Animation` モデルをネイティブ Vulkan
パイプラインで駆動するため、同じシーンを**ライブ表示**し、任意のフレームへ瞬時にシークし、
既定のレンダラーより数倍速く MP4 に録画できます。

**PyPI:** [pypi.org/project/real-time-manim](https://pypi.org/project/real-time-manim/)

> **まずはこちら：** 概要・デモ・インタラクティブな wiki グラフは
> [プロジェクトサイト](https://team-axioviva.github.io/real-time-manim_website/)、
> ソースレベルの解説は
> [GitHub Wiki](https://github.com/Team-Axioviva/real-time-manim/wiki) をご覧ください。
> 完全な英語マニュアルは [`RTM-Wiki/en_US/`](RTM-Wiki/en_US/README.md) にあります。
>
> **AI エージェント：** まず [`RTM-Wiki/agent/README.md`](RTM-Wiki/agent/README.md) を読んで
> ください——API 全体を grep しやすい 1 つのリファレンスにまとめてあり、
> [`gotchas.md`](RTM-Wiki/agent/gotchas.md)、[`patterns.md`](RTM-Wiki/agent/patterns.md)、
> [`llms.txt`](llms.txt) も用意しています。

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

## インストール

```bash
pip install real-time-manim
pip install "real-time-manim[typst]"   # 任意：プロセス内 Typst 数式バックエンド
```

wheel にはプラットフォーム用のネイティブバイナリ（Windows は `vulkan_core.dll`、
Apple Silicon は `vulkan_core.dylib`）が含まれており、ネイティブビルドは不要です。
Vulkan 対応の GPU / ドライバーが必要で、録画には `ffmpeg` が `PATH` に必要です。
**macOS** では実行時に MoltenVK も必要です（`brew install molten-vk`）。Intel Mac では
`bash native/build_mac.sh` で dylib をビルドできます。

---

## クイックスタート

```python
from real_time_manim import Scene, Square, Create, Wait, BLUE, MLWindow
from real_time_manim.record import fast_record_scene

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)      # サイズは 1920x1080 に固定されます
        win.scene = self              # 必須
        win.play(Create(Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)), run_time=1.0)
        win.play(Wait(0.5))
        win.close()                   # 必須：フラッシュしてエンコーダーを終了

fast_record_scene(Hello)              # -> ~/Downloads/output.mp4
```

`MLWindow` はコンテキストマネージャーとしても使えます：`with MLWindow(...) as win:` は
ブロックを抜けるときに自動で閉じます。

> **ManimCE を別途インストールする必要はなく、`import manim` も不要です。** RTM は
> ManimCE **0.21.0** を同梱し、名前空間全体を再エクスポートします。`manim` ではなく
> `real_time_manim` をインポートしてください。クラス identity が分裂します。

---

## ハイライト

- **リアルタイムウィンドウ** —— 1920×1080 @ 60 fps。コードと映像の間に書き出し工程がありません。
- **高速録画** —— ManimCE Cairo より約 **1.9–2.8 倍**高速。play ごとの静的ルートは 1 枚の
  テクスチャにベイクされ、`Wait` はシーンを再描画せずにエンコードされます。
- **フレーム並列** —— `jobs="auto"` が長いシーンをワーカーに分割します。`prepare()` /
  `shared_prepare()` により、高コストな準備を各ワーカーで繰り返しません。
- **フレーム単位のシーク** —— 準備済みシーンの任意のフレームを O(1) で取得。
  `FrameServer` / `FramePreview`。
- **深度テスト付き 3D** —— `MeshMobject` / `MeshBatch` / `MeshGroup` は GPU 深度バッファーを
  使い、交差・自己遮蔽する面をピクセル単位で解決します。CPU ベイクの Manim シェーディングか、
  ネイティブのライティング素材を選べます。
- **ポストプロセス** —— 任意のネイティブ bloom と ACES/Reinhard トーンマッピング。
- **ManimCE 完全対応** —— 既存のシーンはそのまま動作し、`from manim import ...` のコードも
  含みます。
- **LaTeX なしの数式** —— `MathTex` はプロセス内 **Typst** バックエンドにルーティングされます
  （`RTM_TYPST=0` で無効化）。

**2.0.13 の新着：** ドキュメント更新——パッケージページの刷新、中国語版 README の追加、
`PR_HISTORY.md` の PR 履歴復元。エンジンの変更はありません。`native/` は 2.0.12 と同一で、
`real_time_manim/` はバージョンのフォールバック値のみ異なります。

---

## 3D とポストプロセス

`MeshMobject` は本物の Manim mobject なので、`shift`、`rotate`、`.animate` でメッシュが
移動します：

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

        mesh = MeshMobject.from_surface(surf, shade=True)   # Manim 風のライティング
        self.add(mesh)
        win.play(mesh.animate.shift(0.4 * UP), run_time=1.0)
        win.close()
```

- 静的メッシュ：`surf.set_shade_in_3d(False)` の後に
  `win.set_mesh(MeshBatch.from_surface(surf))`。ワールド空間のスナップショットなので、
  Surface を `add` しないでください。
- ネイティブ素材：`MeshMobject.from_surface(surf, lit=True)` と
  `win.set_mesh_light(ambient=0.25, diffuse=0.9, specular=0.4, shininess=48)`。
  `shade=True` と `lit=True` は同時に使えません。
- Bloom/tonemap：`win.set_post(bloom=0.8, threshold=0.75, tonemap="aces")`。
  `set_post(False)` で無効、`RTM_POST=1` で全体に有効。
- `from_surface()` は不透明な四角形のみをベイクします。mesh にはピクセル単位の透明ソートが
  ありません。`MeshBatch.MAX_QUADS = 131072`、1 フレームにつき 1 つのネイティブメッシュです。

---

## 3 つの出力方法

| 出力 | API | 説明 |
| --- | --- | --- |
| **ライブウィンドウ** | `MLWindow` | リアルタイムに描画して見る。ファイルは作らない |
| **MP4** | `fast_record_scene` / `record_scene` | 非表示オフライン（最速）または表示リアルタイム。`jobs=N` でフレーム分割 |
| **PNG フレーム** | `FrameServer` / `FramePreview` | 任意の `t` のフレームを O(1) で書き出し、またはタイムラインをスクラブ |

```python
from real_time_manim import MLWindow, Square, Create, FrameServer, FramePreview
from real_time_manim.record import fast_record_scene, record_scene

# 1. ライブウィンドウ
win = MLWindow(1920, 1080)
win.scene = MyScene()
win.play(Create(Square()), run_time=1.0)
win.close()

# 2. MP4：非表示オフライン（最速）、並列、または表示リアルタイム
fast_record_scene(MyScene)
fast_record_scene(MyScene, "out.mp4", jobs=4)
record_scene(MyScene, "live.mp4")

# 3. PNG フレーム：1 枚、時刻のリスト、またはインタラクティブなスクラブ
fs = FrameServer(MyScene)
fs.save_frame(2.5, "frame.png")
fs.export_frames("frames/", [0.0, 1.5, 3.0])
fs.close()
FramePreview(MyScene).run()
```

レコーダーは `Scene` サブクラス / インスタンス / 引数なし callable を受け取り、
`{out_path, windows, files, with_audio}` を返します。`jobs="auto"` はインポート可能で
単一ウィンドウ、240 フレーム以上のシーンだけを分割します。高コストな純粋データの準備は
`prepare()` に移し、各ワーカーで共有してください。

---

## 制約

- 出力は**1920×1080 @ 60 fps に固定**です。他の値は `[rtm] forcing ...` を出して補正されます。
- **1 プロセスにつき 1 ウィンドウ**。`win.scene = self` と `win.close()` が必須です
  （`atexit` はベストエフォートのフォールバックで、エンコーダーのエラーを報告できません）。
- `manim` CLI はありません——RTM はライブラリです：`MLWindow`、レコーダー、`FrameServer`、
  `FramePreview`、`Timeline`。

---

## 連絡先

バグ報告・機能要望：[issue を作成](https://github.com/Team-Axioviva/real-time-manim/issues)。
メール：**axioviva@gmail.com**。

---

## ライセンス

[MIT](LICENSE)。ManimCE、Vulkan、Typst はそれぞれのプロジェクトに帰属します。
