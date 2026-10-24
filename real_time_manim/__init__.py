"""real-time-manim — a Vulkan-accelerated real-time backend for ManimCE.

``import real_time_manim`` gives you **everything**: RTM's own renderer plus the
complete ManimCE namespace, so a scene never has to ``import manim``::

    from real_time_manim import Scene, Square, Create, BLUE, MLWindow

How that works
--------------
RTM drives Manim's own ``Mobject`` / ``VMobject`` / ``Animation`` classes — they
are the data model the Vulkan pipeline reads points, fills and strokes from.
Those classes now live **inside this package**, in :mod:`real_time_manim.manim`
(``real_time_manim/manim/``: ManimCE 0.21.0, MIT, see ``UPSTREAM.md`` there).

Python resolves every ``import manim`` in one process through a single entry —
``sys.modules["manim"]`` — so the bundled copy is installed there at import
time and takes over that name:

* no ManimCE install needed: RTM is self-contained;
* legacy code that still writes ``from manim import Square`` keeps working, and
  gets the *same* classes RTM uses (one class identity, no split brain);
* if ManimCE has already been imported in this process, it is left alone and
  used as-is (RTM then runs on it, exactly like before 2.0.0).  A warning is
  emitted when that upstream copy is not the version RTM bundles.

The physical path ``real_time_manim.manim`` is *not* a second copy: a meta-path
finder maps it onto the canonical ``manim`` modules, and the few ManimCE names
that are not at Manim's top level can be reached through it, e.g.
``real_time_manim.manim.utils.rate_functions``.

Version
-------
The distribution version is read from the installed metadata, with a literal
fallback for source checkouts (keep that literal in sync with
``pyproject.toml``).
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
import warnings
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import TYPE_CHECKING

try:
    __version__ = version("real-time-manim")
except PackageNotFoundError:          # running from a source tree
    __version__ = "2.0.1"

#: The ManimCE release bundled in ``real_time_manim/manim/``.
MANIM_BUNDLE_VERSION = "0.21.0"

# ---------------------------------------------------------------------------
# 1. Install the bundled ManimCE under its canonical name.
# ---------------------------------------------------------------------------

_MANIM_PREFIX = "real_time_manim.manim"


class _RtmManimLoader:
    """Hands out the canonical ``manim`` module for ``real_time_manim.manim.*``.

    ``create_module`` returns the already-imported canonical module, so both
    spellings share one module object (and therefore one set of classes).
    """

    __slots__ = ("canonical",)

    def __init__(self, canonical: str) -> None:
        self.canonical = canonical

    def create_module(self, spec):
        return importlib.import_module(self.canonical)

    def exec_module(self, module):        # already executed under its real name
        return None


class _RtmManimAliasFinder:
    """``import real_time_manim.manim[.x]`` -> the canonical ``manim[.x]``.

    Registered on ``sys.meta_path`` so the physical package directory can never
    be imported a second time (which would duplicate every class).
    """

    def find_spec(self, fullname, path=None, target=None):
        if fullname == _MANIM_PREFIX or fullname.startswith(_MANIM_PREFIX + "."):
            canonical = "manim" + fullname[len(_MANIM_PREFIX):]
            return importlib.util.spec_from_loader(
                fullname, _RtmManimLoader(canonical)
            )
        return None


def _install_bundled_manim():
    """Make the bundled ManimCE available as ``manim`` (once per process).

    Returns the module that now answers to ``import manim``.
    """
    existing = sys.modules.get("manim")
    if existing is not None:
        # Something already imported ManimCE (an install, or a previous import
        # in this process).  Use it: same code, and swapping the name out now
        # would split class identity in two.
        found = getattr(existing, "__version__", "") or ""
        if not str(found).startswith(MANIM_BUNDLE_VERSION.rsplit(".", 1)[0]):
            warnings.warn(
                f"real-time-manim bundles ManimCE {MANIM_BUNDLE_VERSION}, but "
                f"manim {found or 'unknown'} was imported first and is being "
                "used instead. Uninstall/upgrade manim, or import "
                "real_time_manim before manim, for the bundled behaviour.",
                RuntimeWarning,
                stacklevel=3,
            )
        return existing

    pkg_dir = Path(__file__).resolve().parent / "manim"
    spec = importlib.util.spec_from_file_location(
        "manim",
        pkg_dir / "__init__.py",
        submodule_search_locations=[str(pkg_dir)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["manim"] = module          # claim the name before exec: manim's
    try:                                   # own modules import "manim.x" by name
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop("manim", None)     # leave the name free for a retry
        raise

    if not str(getattr(module, "__version__", "")).startswith(MANIM_BUNDLE_VERSION.rsplit(".", 1)[0]):
        # No ManimCE distribution metadata -> manim's own fallback version.
        module.__version__ = MANIM_BUNDLE_VERSION
    return module


_manim = _install_bundled_manim()

if not any(finder.__class__ is _RtmManimAliasFinder for finder in sys.meta_path):
    sys.meta_path.insert(0, _RtmManimAliasFinder())

# ---------------------------------------------------------------------------
# 2. Re-export the whole ManimCE namespace, so scenes only import RTM.
# ---------------------------------------------------------------------------

# RTM's public API *is* the ManimCE namespace: scenes import one module and get
# Scene, Square, Create, BLUE, ... Listing several hundred names here would be
# unmaintainable and would drift from the bundled release, so the wildcard is
# deliberate.  pyright flags wildcard imports from third-party packages; this
# is the facade that makes that rule a false positive.
from manim import *  # noqa: F403  # pyright: ignore[reportWildcardImportFromLibrary]

# The import above only resolves at runtime: ``manim`` is installed into
# ``sys.modules`` by ``_install_bundled_manim()``, which a static analyzer
# never executes.  Type checkers therefore see no names coming through it.
# Re-import the same objects by their real path (``real_time_manim.manim`` is
# the bundle on disk) so ``from real_time_manim import *`` is typed.
if TYPE_CHECKING:                                                      # pragma: no cover
    from real_time_manim.manim import *                                # noqa: F403
    from real_time_manim.frames import FrameServer
    from real_time_manim.preview import FramePreview
    from real_time_manim.record import fast_record_scene, record_scene
    from real_time_manim.timeline import Timeline
    from real_time_manim.util import (
        clear_media,
        clear_tex_cache,
        restore_tex_cache,
        save_tex_cache,
    )
    from real_time_manim.vulkan_bind import MLWindow

# ---------------------------------------------------------------------------
# 3. Upstream defects RTM works around (see real_time_manim/compat.py).
# ---------------------------------------------------------------------------

from real_time_manim.compat import apply_manim_shims as _apply_manim_shims

_apply_manim_shims()

# ---------------------------------------------------------------------------
# 4. Typst layer: the Typst/TypstMath mobjects (re-exported from ManimCE) plus
#    the LaTeX->Typst auto-routing that window.mathtex installs on MathTex.
# ---------------------------------------------------------------------------

from real_time_manim.typst_support import MathTypst, Typst, TypstMath

# ---------------------------------------------------------------------------
# 5. Names that must stay RTM's own even though ManimCE exports them too.
# ---------------------------------------------------------------------------

from real_time_manim import rate_functions as _rtm_rate_functions

rate_functions = _rtm_rate_functions          # real_time_manim.rate_functions

# ---------------------------------------------------------------------------
# 6. RTM's renderer entry points, imported lazily so ``import real_time_manim``
#    stays cheap (the window/record modules pull in the native renderer).
# ---------------------------------------------------------------------------

_LAZY_EXPORTS = {
    "MLWindow": ("real_time_manim.vulkan_bind", "MLWindow"),
    "Timeline": ("real_time_manim.timeline", "Timeline"),
    "FrameServer": ("real_time_manim.frames", "FrameServer"),
    "FramePreview": ("real_time_manim.preview", "FramePreview"),
    "fast_record_scene": ("real_time_manim.record", "fast_record_scene"),
    "record_scene": ("real_time_manim.record", "record_scene"),
    "restore_tex_cache": ("real_time_manim.util", "restore_tex_cache"),
    "save_tex_cache": ("real_time_manim.util", "save_tex_cache"),
    "clear_tex_cache": ("real_time_manim.util", "clear_tex_cache"),
    "clear_media": ("real_time_manim.util", "clear_media"),
}


def __getattr__(name):
    """Resolve RTM's renderer entry points on first use (PEP 562)."""
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r}"
        ) from None
    module_name, attr = target
    return getattr(importlib.import_module(module_name), attr)


__all__ = sorted(
    {name for name in dir(_manim) if not name.startswith("_")}
    | {"__version__", "MANIM_BUNDLE_VERSION", "Typst", "MathTypst", "TypstMath"}
    | set(_LAZY_EXPORTS)
)
