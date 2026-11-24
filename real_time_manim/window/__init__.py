"""The render window: RTM's bridge between manim and the native Vulkan DLL.

`MLWindow` is assembled from four mixins so that no single file has to carry
the whole renderer:

    core      -- construction, DLL binding, camera publish, ``sync``
    paint     -- turning mobjects into native draw calls
    play      -- the play loop, the timeline renderer, the legacy play path
    recording -- screenshots and video capture

Importing the package also applies the monkey patches RTM installs on manim
(``patches``) and the MathTex patches (``mathtex``), which is what importing
``real_time_manim.vulkan_bind`` used to do.
"""

from real_time_manim.render.shapes import ShapeMixin
from real_time_manim.render.text import TextMixin

# Upstream monkey patches first: they must be in place before any animation or
# MathTex is built, and nothing below builds one at import time.
from real_time_manim.window import patches as _patches  # noqa: F401  (patches manim)
from real_time_manim.window import mathtex as _mathtex  # noqa: F401  (patches MathTex)

from real_time_manim.window.core import CoreMixin
from real_time_manim.window.paint import PaintMixin
from real_time_manim.window.play import PlayMixin
from real_time_manim.window.recording import RecordingMixin


class MLWindow(ShapeMixin, TextMixin, CoreMixin, PaintMixin, PlayMixin, RecordingMixin):
    """One native render window, 1920x1080 at 60 fps.

    The mixins above hold the implementation; this class only fixes their
    order -- ``ShapeMixin``/``TextMixin`` first, exactly as before the split,
    so any method they both define keeps winning.

    Use it as a context manager (``with MLWindow(...) as win:``) or call
    ``close()`` explicitly.  A process that exits with a live window is closed
    by the ``atexit`` hook below, so a forgotten ``close()`` no longer means
    "no output" -- but explicit is still better: ``close()`` finishes a manual
    fast record and reports encoder errors.
    """


def _close_remaining_windows():
    """Best-effort close of windows still alive at interpreter exit."""
    for win in list(MLWindow._registry):
        try:
            win.close()
        except Exception:                 # shutdown must not raise
            pass


import atexit  # noqa: E402  (kept local to the registration below)

atexit.register(_close_remaining_windows)


__all__ = ["MLWindow"]
