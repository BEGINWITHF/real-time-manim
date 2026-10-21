"""Clear the LaTeX / Typst cache.

Removes the persistent ``tex_cache/`` folder next to this script and the
compiled SVGs in ``media/Tex/``, so the next run recompiles from scratch.
This is a thin wrapper over ``real_time_manim.util.clear_tex_cache``.
"""
import os

from real_time_manim.util import clear_tex_cache

REPO = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    clear_tex_cache(cache_dir=os.path.join(REPO, "tex_cache"),
                    media_dir=os.path.join(REPO, "media"))
