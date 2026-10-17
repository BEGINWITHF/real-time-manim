"""RTM must work with no ManimCE installed at all.

The ManimCE RTM drives is bundled in ``real_time_manim/manim/`` and installed
under its canonical ``manim`` name by ``real_time_manim/__init__``.  These tests
run in a *subprocess* with the top-level ``manim`` import blocked -- exactly
what a machine without the ``manim`` distribution sees.
"""
import os
import subprocess
import sys
import textwrap

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_HEAD = textwrap.dedent(
    """
    import sys

    class _NoManimInstalled:
        def find_spec(self, fullname, path=None, target=None):
            if fullname == "manim":
                raise ModuleNotFoundError("No module named 'manim'", name=fullname)
            return None

    sys.meta_path.insert(0, _NoManimInstalled())
    sys.path.insert(0, {repo!r})
    """
)


def run(body):
    """Run ``body`` in a clean interpreter where ``import manim`` fails."""
    code = _HEAD.format(repo=REPO) + textwrap.dedent(body)
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO,
        timeout=300,
    )
    assert proc.returncode == 0, (
        "subprocess failed\n--- stdout ---\n%s\n--- stderr ---\n%s"
        % (proc.stdout, proc.stderr)
    )
    return proc.stdout


def test_bundled_manim_answers_to_the_manim_name():
    out = run(
        """
        import real_time_manim
        import manim
        assert "real-time-manim" in manim.__file__.replace("\\\\", "/"), manim.__file__
        assert manim.__name__ == "manim"
        print("ok")
        """
    )
    assert "ok" in out


def test_scene_construction_without_manim_install():
    out = run(
        """
        from real_time_manim import (
            Scene, Square, Circle, Text, BLUE, Create, FadeIn, Write,
            linear, smooth, config,
        )

        sq = Square(side_length=1.5, color=BLUE).set_fill(BLUE, 0.6)
        anim = Create(sq)
        anim.begin()
        for alpha in (0.0, 0.5, 1.0):
            anim.interpolate(alpha)
        assert len(sq.points) > 0
        assert callable(smooth) and callable(linear)
        assert Scene.__module__.startswith("manim")
        print("ok")
        """
    )
    assert "ok" in out


def test_legacy_manim_imports_share_one_identity():
    """Old ``from manim import ...`` code keeps working -- same classes."""
    out = run(
        """
        import real_time_manim
        from real_time_manim import Square as RtmSquare, FadeIn as RtmFadeIn
        from manim import Square as LegacySquare
        from manim.animation.fading import FadeIn as LegacyFadeIn

        assert RtmSquare is LegacySquare
        assert RtmFadeIn is LegacyFadeIn
        print("ok")
        """
    )
    assert "ok" in out


def test_deep_manim_paths_resolve_to_the_same_modules():
    """``real_time_manim.manim.<sub>`` is an alias, never a second copy."""
    out = run(
        """
        import sys
        import real_time_manim
        import manim.utils.paths as upstream_paths
        from real_time_manim.manim.utils.paths import spiral_path

        assert spiral_path is upstream_paths.spiral_path
        # every alias key must be *the same module object* as the canonical one
        for key, mod in list(sys.modules.items()):
            if not key.startswith("real_time_manim.manim"):
                continue
            canonical = "manim" + key[len("real_time_manim.manim"):]
            assert sys.modules.get(canonical) is mod, (key, canonical)
            assert mod is sys.modules[canonical]
        print("ok")
        """
    )
    assert "ok" in out


def test_rtm_entry_points_are_exported_too():
    """The renderer entry points ride along with the ManimCE namespace."""
    out = run(
        """
        import real_time_manim
        for name in ("MLWindow", "Timeline", "fast_record_scene",
                     "record_scene", "restore_tex_cache"):
            assert name in real_time_manim.__all__, name
            assert getattr(real_time_manim, name) is not None, name
        print("ok")
        """
    )
    assert "ok" in out


def test_bundle_version_is_reported():
    out = run(
        """
        import real_time_manim, manim
        assert real_time_manim.MANIM_BUNDLE_VERSION == manim.__version__, (
            real_time_manim.MANIM_BUNDLE_VERSION, manim.__version__)
        print("ok")
        """
    )
    assert "ok" in out
