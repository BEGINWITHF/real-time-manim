"""Build shim: mark the distribution as platform-specific.

The renderer bundles a Windows-only Vulkan DLL (real_time_manim/vulkan_core.dll), so the
wheel must be tagged ``win_amd64`` rather than ``py3-none-any``. Metadata lives
in ``pyproject.toml``; this file only overrides the distribution class.
"""

from setuptools import setup
from setuptools.dist import Distribution


class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True


setup(distclass=BinaryDistribution)
