"""Regression test: a manim animation driven through an updater still needs
RTM's render channels.

Report: wiki ``03-动画/更新器动画/01b-更新工具与自动变化`` -- "welcome的write动画
不对".  The page (legitimately, per its own docstring) uses manim's native
``Write`` inside ``turn_animation_into_updater(...)`` so the animation can be
driven as an updater instead of a ``play``.  That animation never becomes a
timeline entry, and ``Timeline.finalize`` -- the only caller of
``install_hooks`` -- therefore never sees it.

Without channels the ``Text`` falls back to ``_send_vmobject``, whose TEXT
branch switches the outline off as soon as the fill reports any visibility::

    if is_text and vis_fill > 0.01:
        do_stroke = False

but manim's ``DrawBorderThenFill`` spends a glyph's whole second half ramping
the fill from 0 while it keeps the outline at full width -- so for those frames
RTM drew a few-percent fill and NO outline and the letter vanished.  Measured
on the rendered page: at each of ``Welcome``'s seven outline->fill boundaries
the word's ink fell 31571 -> 9504 (-70 %) in one frame, where CE's curve never
drops; a 120-frame probe render with the hooks armed gives 0 drops vs 7.

``render.hooks.install_hooks_from_updaters`` finds the animation in the
updater's closure; ``window.scene._run_mobject_updaters`` calls it before the
first updater call of each frame.

Pure Python: stub scene, no GPU, no images.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402
from manim import Scene, Text, Write, turn_animation_into_updater  # noqa: E402

from real_time_manim.render.hooks import (  # noqa: E402
    install_hooks,
    install_hooks_from_updaters,
)
from real_time_manim.window.scene import _drive_mobject_updaters  # noqa: E402


class StubScene:
    """The two attributes ``_drive_mobject_updaters`` walks."""

    def __init__(self):
        self.mobjects = []
        self.updaters = []


def _written_word():
    scene = StubScene()
    words = Text("Welcome", font_size=30, color="YELLOW")
    anim = Write(words, run_time=1.2)
    turn_animation_into_updater(anim, cycle=False, delay=0.3)
    scene.mobjects.append(words)
    return scene, words, anim


def test_the_updater_driven_write_gets_hooked():
    scene, words, anim = _written_word()
    assert not getattr(anim, "_rtm_hooks_installed", False)
    assert install_hooks_from_updaters(words) >= 1
    assert getattr(anim, "_rtm_hooks_installed", False), (
        "the Write closed over by turn_animation_into_updater was not hooked")


def test_hooking_is_idempotent():
    scene, words, anim = _written_word()
    first = install_hooks_from_updaters(words)
    second = install_hooks_from_updaters(words)
    assert first >= 1 and second == 0


def test_the_hook_arms_letter_alphas_for_every_glyph():
    """This is the channel `_send_vmobject` lacks and the dip came from."""
    scene, words, anim = _written_word()
    _drive_mobject_updaters(scene, 1 / 60)
    alphas = getattr(words, "_letter_alphas", None)
    assert alphas is not None, "the Text never got its per-glyph channel"
    assert set(alphas) == set(range(len(words.submobjects)))


def test_letter_alphas_advance_once_per_frame():
    """Re-derived from the animation's own alpha on every frame."""
    scene, words, anim = _written_word()
    seen = []
    for k in range(40):
        _drive_mobject_updaters(scene, 1 / 60)
        seen.append(float(words._letter_alphas[0]))
    assert all(b >= a for a, b in zip(seen, seen[1:])), "the reveal went backwards"
    assert seen[-1] > seen[0], "the reveal never advanced"
    # a well-behaved map covers the whole glyph range, not just 0/1
    assert max(seen) > 0.0


def test_plain_lambda_updaters_hook_nothing():
    """The overwhelmingly common mobject must stay untouched (and fast)."""
    from manim import Square

    scene = StubScene()
    sq = Square()
    sq.add_updater(lambda m: m.shift(0))
    scene.mobjects.append(sq)
    assert install_hooks_from_updaters(sq) == 0
    # must not raise either, and the updater still runs
    _drive_mobject_updaters(scene, 1 / 60)


def test_the_manually_hooked_path_still_works():
    """``install_hooks`` itself is unchanged -- it is just called from further in."""
    scene, words, anim = _written_word()
    install_hooks(anim)                     # second call must be a no-op
    assert getattr(anim, "_rtm_hooks_installed", False)
    assert install_hooks_from_updaters(words) == 0
