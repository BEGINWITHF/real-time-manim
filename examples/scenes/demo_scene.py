"""Compatibility facade for the demo scene gallery.

The scenes now live in sibling modules (``basics``, ``timing``,
``creation``, ``indication``, ``transform``, ``latex``); this module keeps
the old ``demo_scene`` import path working and doubles as the batch
recorder entry point::

    python examples/scenes/demo_scene.py

which is the same as ``python -m examples.scenes.recorder``.
"""
import os
import sys

if not __package__:  # run as a plain script -> make the package importable
    sys.path.insert(
        0,
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    )
    __package__ = "examples.scenes"

from .basics import *  # noqa: F401,F403
from .timing import *  # noqa: F401,F403
from .creation import *  # noqa: F401,F403
from .indication import *  # noqa: F401,F403
from .transform import *  # noqa: F401,F403
from .latex import *  # noqa: F401,F403
from .recorder import main  # noqa: F401

if __name__ == "__main__":
    main()
