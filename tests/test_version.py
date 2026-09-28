"""Regression test: the package exposes its version.

`real_time_manim/__init__.py` shipped empty, so `real_time_manim.__version__`
raised AttributeError even though pip knew the version.  It is now read from the
distribution metadata (with a source-tree fallback).

Pure Python: no window, no GPU.
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import real_time_manim


def test_version_is_exposed():
    assert isinstance(real_time_manim.__version__, str)
    assert real_time_manim.__version__.strip()


def test_version_looks_like_a_version():
    assert re.match(r"^\d+\.\d+", real_time_manim.__version__), real_time_manim.__version__


def test_version_matches_installed_metadata_when_installed():
    """For an installed build the metadata is the source of truth."""
    from importlib.metadata import PackageNotFoundError, version

    try:
        installed = version("real-time-manim")
    except PackageNotFoundError:
        installed = None                      # source tree: fallback literal applies
    if installed is not None:
        assert real_time_manim.__version__ == installed


def test_source_fallback_matches_pyproject():
    """The literal fallback must not drift from pyproject.toml."""
    from importlib.metadata import PackageNotFoundError, version

    try:
        version("real-time-manim")
        return                                 # installed: nothing to compare here
    except PackageNotFoundError:
        pass
    pyproject = os.path.join(REPO, "pyproject.toml")
    if not os.path.exists(pyproject):
        return
    with open(pyproject, encoding="utf-8") as f:
        m = re.search(r'^version\s*=\s*"([^"]+)"', f.read(), re.M)
    assert m, "no version in pyproject.toml"
    assert real_time_manim.__version__ == m.group(1), (real_time_manim.__version__, m.group(1))
