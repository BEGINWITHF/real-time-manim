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

__all__ = ["__version__"]
