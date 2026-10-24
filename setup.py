"""Build shim: tag the wheel by platform, not by interpreter.

The renderer bundles platform-native Vulkan binaries
(``real_time_manim/vulkan_core.dll`` on Windows,
``real_time_manim/vulkan_core.dylib`` on macOS), so the wheel must be tagged
per-platform (``win_amd64`` / ``macosx_11_0_arm64``) rather than
``py3-none-any``.  Metadata lives in ``pyproject.toml``; this file overrides

* the distribution class, so the wheel stays platform-specific
  (``Root-Is-Purelib: false`` and the native binary lands in ``platlib``),
* ``bdist_wheel``, so the tag is ``py3-none-<plat>`` -- a ``ctypes``-loaded
  dylib is *not* a CPython extension, and tagging the wheel ``cp3XX-cp3XX``
  (which ``Distribution.has_ext_modules()`` would do) locks it to the one
  CPython minor that built it even though ``requires-python >=3.11``,
* the macOS platform tag, which otherwise follows the *build machine's* macOS
  version (a build on macOS 27 produced ``macosx_27_0_arm64``, installable
  nowhere older) instead of the deployment target the dylib is built for.

``MIN_MACOS`` must match ``-mmacosx-version-min`` in ``native/build_mac.sh``.
"""

import os
import platform
import re
import sys
from pathlib import Path

from setuptools import find_namespace_packages, setup
from setuptools.command.build_py import build_py
from setuptools.dist import Distribution
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

# Minimum macOS the bundled dylib is built for (native/build_mac.sh).
MIN_MACOS = "12.0"


class BinaryDistribution(Distribution):
    """Keep the wheel platform-specific (``Root-Is-Purelib: false``)."""

    def has_ext_modules(self):
        # No compiler is involved; this only tells setuptools that the wheel
        # carries a platform binary and must not be tagged ``py3-none-any``.
        return True


def _default_plat_name():
    """The platform tag to pin when the caller did not pass ``--plat-name``."""
    if sys.platform == "darwin":
        arch = platform.machine() or "arm64"
        return "macosx_%s_%s" % (MIN_MACOS.replace(".", "_"), arch)
    return None                      # let setuptools compute win_amd64 / ...


class PlatformWheel(_bdist_wheel):
    """Emit ``py3-none-<plat>`` and pin the macOS deployment target."""

    def finalize_options(self):
        super().finalize_options()
        if not self.plat_name_supplied:
            default = _default_plat_name()
            if default:
                self.plat_name = default
                self.plat_name_supplied = True
        if sys.platform == "darwin" and self.plat_name:
            # setuptools defaults to universal2 on macOS; the bundled dylib is
            # built for one architecture.
            self.plat_name = re.sub(r"universal2$", platform.machine(),
                                    self.plat_name)

    def get_tag(self):
        # Run the platform computation (and setuptools' "is this tag supported
        # here?" assertion) first, then drop the interpreter/ABI lock.
        _, _, plat = super().get_tag()
        return "py3", "none", plat


class PlatformBuildPy(build_py):
    """Put only the current platform's native binary in the wheel.

    Both binaries live in the source tree (and in the sdist, so either platform
    can build from source), but a macOS wheel has no use for the Windows DLL or
    vice versa -- they were 251 KB of dead weight each.
    """

    _FOREIGN = {"darwin": "vulkan_core.dll", "win32": "vulkan_core.dylib"}

    def run(self):
        super().run()
        foreign = self._FOREIGN.get(sys.platform)
        if not foreign:
            return
        stale = os.path.join(self.build_lib, "real_time_manim", foreign)
        if os.path.exists(stale):
            os.remove(stale)


def _stub_packages():
    """Every directory under ``manim-stubs/`` that holds a ``.pyi`` file.

    ``manim-stubs`` is a PEP 561 stub-only package: pyright resolves the
    runtime name ``manim`` (which RTM installs into ``sys.modules``) against
    these files, so the bundled ManimCE copy is fully typed for consumers.
    The hyphenated directory cannot be imported, so it is inert at runtime.
    """
    root = Path(__file__).parent / "manim-stubs"
    if not root.is_dir():
        return []
    packages = []
    for path in root.rglob("*"):
        if path.is_dir() and any(path.glob("*.pyi")):
            packages.append(str(path.relative_to(Path(__file__).parent)).replace(os.sep, "."))
    if any(root.glob("*.pyi")):
        packages.append("manim-stubs")
    return sorted(set(packages))


stub_packages = _stub_packages()

setup(
    distclass=BinaryDistribution,
    cmdclass={"bdist_wheel": PlatformWheel, "build_py": PlatformBuildPy},
    packages=find_namespace_packages(include=["real_time_manim*"]) + stub_packages,
    package_data={package: ["*.pyi", "py.typed"] for package in stub_packages},
)
