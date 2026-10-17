# Bundled ManimCE

The `.py` files in this directory (and its data files: `_config/default.cfg`,
`renderer/shaders/**`, `templates/*.mtp`) are a **verbatim copy of the ManimCE
package**, taken from `manim==0.21.0` with only these parts removed:

| removed | why |
| --- | --- |
| `cli/`, `__main__.py` | the `manim` command line tool — RTM has no CLI |
| `utils/ipython_magic.py` | pulls in `manim.cli`, only used from an IPython session |
| `utils/docbuild/` | Sphinx documentation builders |
| `utils/testing/` | ManimCE's own graphical test helpers |
| `__pycache__/` | bytecode |

Nothing else was edited: the files still import each other through the
canonical `manim.*` names, and `real_time_manim/__init__.py` installs this copy
under that name when ManimCE is not already imported.  That keeps one set of
`Mobject` / `VMobject` / `Animation` classes for RTM, the scenes, and any
legacy `from manim import ...` code, and it means RTM needs no ManimCE install.

* Project: <https://www.manim.community/>
* Source: <https://github.com/ManimCommunity/manim>
* Version: 0.21.0
* License: MIT — Copyright (c) 2017-2020 3b1b and Manim Community developers

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

To update: copy a fresh `manim/` tree here, delete the five entries in the
table above, and bump `MANIM_BUNDLE_VERSION` in `real_time_manim/__init__.py`.
