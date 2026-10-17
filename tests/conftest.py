"""Pin the import order for the whole suite.

RTM installs its bundled ManimCE under ``sys.modules["manim"]`` **only if that
name is still free** (see ``real_time_manim/__init__.py``).  A site-packages
ManimCE is present in many environments, so any test module that happens to
import ``manim`` before ``real_time_manim`` silently makes RTM drive the
*external* copy instead of the bundled, patched one -- and the suite then fails
depending on collection order (historically: ``test_bundled_manim``,
``test_gap_transform_motion``, ``test_phase5_tools`` flaked at random).

Importing ``real_time_manim`` here, before any test module is collected, makes
the bundled copy win deterministically for every test.
"""

import real_time_manim  # noqa: F401  -- must run before test collection
