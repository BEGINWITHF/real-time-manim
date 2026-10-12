"""Real-time demo scenes for Real Time Manim.

The scenes used to live in a single 2200-line ``demo_scene.py``; they are
now grouped by topic in the modules listed below and re-exported here, so
``from examples.scenes import DemoCreate`` keeps working either way::

    run.py                              menu-driven single scene -> MP4
    run_all.py                          render every scene -> MP4
    python -m examples.scenes.recorder  batch-record via screen capture

Modules:
    basics      demos 1-12   -- the core animation vocabulary
    timing      demos 13-24  -- text styles and animation timing
    creation    demos 25-42  -- create / write / grow / fade
    indication  demos 43-61  -- attention effects and speed modifiers
    transform   demos 62-78  -- advanced transform variants
    latex       demos 79-82  -- LaTeX, Fourier and Lorenz showcases
"""
from .basics import *  # noqa: F401,F403
from .timing import *  # noqa: F401,F403
from .creation import *  # noqa: F401,F403
from .indication import *  # noqa: F401,F403
from .transform import *  # noqa: F401,F403
from .latex import *  # noqa: F401,F403
