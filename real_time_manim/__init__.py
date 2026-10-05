"""real-time-manim — a Vulkan-accelerated real-time backend for ManimCE.

The package used to ship an empty ``__init__.py``, so ``real_time_manim.__version__``
did not exist even though the distribution metadata carried the version.  It is
read from the installed metadata, with a literal fallback for source checkouts
(keep that literal in sync with ``pyproject.toml``).
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("real-time-manim")
except PackageNotFoundError:          # running from a source tree
    __version__ = "2.0.0"

# RTM drives Manim's own classes, so a few upstream defects that plain Manim also
# hits are worked around here (see real_time_manim/compat.py and wiki/Known-Issues).
from real_time_manim.compat import apply_manim_shims as _apply_manim_shims

_apply_manim_shims()

__all__ = ["__version__"]
