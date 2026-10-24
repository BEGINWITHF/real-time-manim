"""Build shim: mark the distribution as platform-specific.

The renderer bundles platform-native Vulkan binaries (real_time_manim/vulkan_core.dll on
Windows, real_time_manim/vulkan_core.dylib on macOS), so the wheel must be tagged
per-platform (``win_amd64`` / ``macosx_*_arm64``) rather than ``py3-none-any``. Metadata
lives in ``pyproject.toml``; this file overrides the distribution class and, on macOS,
replaces setuptools' ``universal2`` default (the bundled dylib is built for one arch)
with the build machine's real architecture.
"""

import platform
import re
import sys

from setuptools import setup
from setuptools.dist import Distribution
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel


class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True


class ArchCorrectBdistWheel(_bdist_wheel):
    def get_tag(self):
        python, abi, plat = super().get_tag()
        if sys.platform == "darwin":
            plat = re.sub(r"universal2$", platform.machine(), plat)
        return python, abi, plat


setup(distclass=BinaryDistribution, cmdclass={"bdist_wheel": ArchCorrectBdistWheel})
