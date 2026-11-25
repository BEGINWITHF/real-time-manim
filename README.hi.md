# Real-Time-Manim (RTM)

<p align="center">
  <img src="banner.jpg" alt="Real-Time-Manim V2 banner" width="880"/>
</p>

<p align="center"><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.zh-TW.md">繁體中文</a> · <a href="README.ja.md">日本語</a> · <a href="README.ko.md">한국어</a> · <b>हिन्दी</b> · <a href="README.es.md">Español</a> · <a href="README.pt-BR.md">Português</a> · <a href="README.fr.md">Français</a> · <a href="README.de.md">Deutsch</a> · <a href="README.ru.md">Русский</a></p>

**[ManimCE](https://www.manim.community/) के लिए Vulkan-accelerated, रियल-टाइम रेंडरिंग
बैकएंड**। RTM ManimCE के अपने `Mobject` / `Animation` मॉडल को नेटिव Vulkan पाइपलाइन से चलाता है,
इसलिए वही सीन **लाइव** देखा जा सकता है, किसी भी फ़्रेम पर तुरंत जाया जा सकता है, और डिफ़ॉल्ट
रेंडरर से कई गुना तेज़ी से MP4 में रिकॉर्ड किया जा सकता है।

**PyPI:** [pypi.org/project/real-time-manim](https://pypi.org/project/real-time-manim/)

> **यहाँ से शुरू करें:** [प्रोजेक्ट वेबसाइट](https://team-axioviva.github.io/real-time-manim_website/)
> पर अवलोकन, डेमो और इंटरैक्टिव wiki ग्राफ़ देखें, और
> [GitHub Wiki](https://github.com/Team-Axioviva/real-time-manim/wiki) पर सोर्स-लेवल
> walkthrough।
> पूरा अंग्रेज़ी मैनुअल [`RTM-Wiki/en_US/`](RTM-Wiki/en_US/README.md) में है।
>
> **AI एजेंट:** पहले [`RTM-Wiki/agent/README.md`](RTM-Wiki/agent/README.md) पढ़ें — पूरा API
> एक grep-friendly संदर्भ में, साथ में [`gotchas.md`](RTM-Wiki/agent/gotchas.md),
> [`patterns.md`](RTM-Wiki/agent/patterns.md) और [`llms.txt`](llms.txt)।

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

## इंस्टॉलेशन

```bash
pip install real-time-manim
pip install "real-time-manim[typst]"   # वैकल्पिक: इन-प्रोसेस Typst गणित बैकएंड
```

wheel में प्लेटफ़ॉर्म की नेटिव बाइनरी शामिल है (Windows पर `vulkan_core.dll`, Apple Silicon पर
`vulkan_core.dylib`); नेटिव बिल्ड की ज़रूरत नहीं।
Vulkan सपोर्ट वाला GPU/ड्राइवर चाहिए, और रिकॉर्डिंग के लिए `ffmpeg` `PATH` में होना चाहिए।
**macOS** पर रनटाइम में MoltenVK भी चाहिए (`brew install molten-vk`); Intel Mac पर
`bash native/build_mac.sh` से dylib बना सकते हैं।

---

## त्वरित शुरुआत

```python
from real_time_manim import Scene, Square, Create, Wait, BLUE, MLWindow
from real_time_manim.record import fast_record_scene

class Hello(Scene):
    def construct(self):
        win = MLWindow(960, 540)      # साइज़ 1920x1080 पर फ़ोर्स होता है
        win.scene = self              # ज़रूरी
        win.play(Create(Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)), run_time=1.0)
        win.play(Wait(0.5))
        win.close()                   # ज़रूरी: फ़्लश करता है और एनकोडर समाप्त करता है

fast_record_scene(Hello)              # -> ~/Downloads/output.mp4
```

`MLWindow` एक context manager भी है: `with MLWindow(...) as win:` ब्लॉक से बाहर निकलते समय
इसे बंद कर देता है।

> **ManimCE अलग से इंस्टॉल करने की ज़रूरत नहीं, और `import manim` न करें।** RTM में ManimCE
> **0.21.0** शामिल है और पूरा namespace फिर से export करता है। `manim` नहीं,
> `real_time_manim` import करें, वरना class identity बँट जाती है।

---

## मुख्य बातें

- **रियल-टाइम विंडो** — 1920×1080 @ 60 fps, कोड और तस्वीर के बीच कोई export स्टेप नहीं।
- **तेज़ रिकॉर्डिंग** — ManimCE Cairo से लगभग **1.9–2.8×** तेज़। हर play की स्थिर जड़ें एक
  texture में bake होती हैं, और `Wait` सीन दोबारा बनाए बिना encode होता है।
- **समानांतर फ़्रेम** — `jobs="auto"` लंबे सीन को workers में बाँटता है; `prepare()` /
  `shared_prepare()` हर worker में महँगी तैयारी दोहराने से बचाते हैं।
- **सटीक फ़्रेम सीक** — तैयार सीन का कोई भी फ़्रेम O(1) में, `FrameServer` / `FramePreview` से।
- **डेप्थ-टेस्टेड 3D** — `MeshMobject` / `MeshBatch` / `MeshGroup` GPU depth buffer का उपयोग
  करते हैं, इसलिए एक-दूसरे को काटती और खुद को ढकती सतहें पिक्सेल-दर-पिक्सेल हल होती हैं।
  CPU-baked Manim shading या नेटिव lit material।
- **पोस्ट-प्रोसेसिंग** — वैकल्पिक नेटिव bloom और ACES/Reinhard tonemapping।
- **पूरा ManimCE** — मौजूदा सीन बिना बदलाव चलते हैं, `from manim import ...` कोड भी।
- **LaTeX के बिना गणित** — `MathTex` इन-प्रोसेस **Typst** बैकएंड पर जाता है
  (`RTM_TYPST=0` से बंद)।

**2.0.13 में नया:** दस्तावेज़ अपडेट — नया पैकेज पेज, चीनी README, और `PR_HISTORY.md` में बहाल
PR इतिहास। इंजन में कोई बदलाव नहीं: `native/` 2.0.12 जैसा है, और `real_time_manim/` में सिर्फ़
version fallback बदला है।

---

## 3D और पोस्ट-प्रोसेसिंग

`MeshMobject` असली Manim mobject है, इसलिए `shift`, `rotate` और `.animate` mesh को हिलाते हैं:

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

        mesh = MeshMobject.from_surface(surf, shade=True)   # Manim-शैली लाइटिंग
        self.add(mesh)
        win.play(mesh.animate.shift(0.4 * UP), run_time=1.0)
        win.close()
```

- स्थिर mesh: `surf.set_shade_in_3d(False)` के बाद
  `win.set_mesh(MeshBatch.from_surface(surf))`। यह world-space snapshot है; Surface को
  `add` न करें।
- नेटिव material: `MeshMobject.from_surface(surf, lit=True)` और
  `win.set_mesh_light(ambient=0.25, diffuse=0.9, specular=0.4, shininess=48)`।
  `shade=True` और `lit=True` साथ नहीं चलते।
- Bloom/tonemap: `win.set_post(bloom=0.8, threshold=0.75, tonemap="aces")`;
  `set_post(False)` से बंद, `RTM_POST=1` से हर जगह चालू।
- `from_surface()` सिर्फ़ अपारदर्शी quads bake करता है; mesh में per-pixel transparency sort
  नहीं है। `MeshBatch.MAX_QUADS = 131072`, प्रति फ़्रेम एक native mesh।

---

## आउटपुट के तीन तरीके

| आउटपुट | API | नोट्स |
| --- | --- | --- |
| **लाइव विंडो** | `MLWindow` | रियल-टाइम में रेंडर करके देखें; कोई फ़ाइल नहीं |
| **MP4** | `fast_record_scene` / `record_scene` | छिपा ऑफ़लाइन (सबसे तेज़) या दिखाई देने वाला रियल-टाइम; `jobs=N` फ़्रेम बाँटता है |
| **PNG फ़्रेम** | `FrameServer` / `FramePreview` | किसी भी `t` का फ़्रेम O(1) में, या timeline scrub |

```python
from real_time_manim import MLWindow, Square, Create, FrameServer, FramePreview
from real_time_manim.record import fast_record_scene, record_scene

# 1. लाइव विंडो
win = MLWindow(1920, 1080)
win.scene = MyScene()
win.play(Create(Square()), run_time=1.0)
win.close()

# 2. MP4: छिपा/ऑफ़लाइन (सबसे तेज़), समानांतर, या दिखाई देने वाला/रियल-टाइम
fast_record_scene(MyScene)
fast_record_scene(MyScene, "out.mp4", jobs=4)
record_scene(MyScene, "live.mp4")

# 3. PNG फ़्रेम: एक, समयों की सूची, या इंटरैक्टिव scrub
fs = FrameServer(MyScene)
fs.save_frame(2.5, "frame.png")
fs.export_frames("frames/", [0.0, 1.5, 3.0])
fs.close()
FramePreview(MyScene).run()
```

रिकॉर्डर `Scene` सबक्लास / इंस्टेंस / बिना आर्ग्युमेंट वाला callable लेते हैं और
`{out_path, windows, files, with_audio}` लौटाते हैं। `jobs="auto"` सिर्फ़ import हो सकने वाले,
एक विंडो वाले, कम से कम 240 फ़्रेम के सीन को बाँटता है; महँगी शुद्ध तैयारी `prepare()` में
डालें ताकि हर worker उसे साझा करे।

---

## सीमाएँ

- आउटपुट **1920×1080 @ 60 fps पर फ़िक्स्ड** है; दूसरी वैल्यू `[rtm] forcing ...` लाइन के साथ
  ठीक कर दी जाती हैं।
- **प्रति प्रोसेस एक विंडो**; `win.scene = self` और `win.close()` ज़रूरी हैं (`atexit` सिर्फ़
  best-effort fallback है और encoder errors नहीं बता सकता)।
- `manim` CLI नहीं है — RTM एक लाइब्रेरी है: `MLWindow`, recorders, `FrameServer`,
  `FramePreview`, `Timeline`।

---

## संपर्क

बग रिपोर्ट और फ़ीचर अनुरोध: [issue खोलें](https://github.com/Team-Axioviva/real-time-manim/issues)।
ईमेल: **axioviva@gmail.com**।

---

## लाइसेंस

[MIT](LICENSE)। ManimCE, Vulkan और Typst अपने-अपने प्रोजेक्ट्स के हैं।
