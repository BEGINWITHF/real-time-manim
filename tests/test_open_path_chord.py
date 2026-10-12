"""An OPEN point path must not be closed by the renderer.

Regression for the AnimatedBoundary diagonal.  manim's ``pointwise_become_partial``
run *outside* a tracked ShowPartial -- ``AnimatedBoundary``'s per-frame updater --
cuts the anchors so they no longer return to the first.  ``_send_polygon`` closes
the vertex ring it is handed, drawing a spurious chord from the pen's last point
back to the first: the diagonal that slashed across AnimatedBoundary's framebox.
``_send_polygon`` already rebuilds a *tagged* cut open via
``_vulkan_points_partial``, but a cut made outside a tracked ShowPartial never
carries the tag.

Render the open L (a stroke-only Square cut to its first two edges) and assert
the closing chord -- the anti-diagonal through the square's centre -- stays empty.
The dispatch-level pin lives in ``test_quad_dispatch.py``; this one checks the
rendered outcome rather than the branch taken.

Run with::

    python -X utf8 -m pytest tests/test_open_path_chord.py -q
"""
import os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
import pytest
from tools.rtm_verify import window_available, render_frames

if not window_available():                              # pragma: no cover
    pytest.skip("Vulkan window unavailable", allow_module_level=True)

from manim import Scene, Square, RED, Wait


def _open_l_scene():
    """A stroke-only Square cut to its first two edges (an open L)."""
    class S(Scene):
        def construct(self):
            from real_time_manim.vulkan_bind import MLWindow
            win = MLWindow(1920, 1080); win.scene = self
            sq = Square(side_length=2).set_fill(opacity=0).set_stroke(RED, width=3)
            sq.pointwise_become_partial(Square(side_length=2), 0.0, 0.5)
            sq.set_stroke(RED, width=3)
            self.add(sq)
            win.play(Wait(0.2))
            win.close()
    return S


def test_open_partial_square_draws_no_closing_chord():
    frames = render_frames(_open_l_scene(), "open_path_chord",
                           fps=30, duration=0.3)

    # Screen mapping for a centred side-2 square on 1920x1080 (scale h/8=135):
    #   x = 960 + 135*X, y = 540 - 135*Y.
    # The L (top edge Y=1, left edge X=-1) sits at y=405 / x=825; the spurious
    # chord joins the L's free ends (-1,-1)->(1,1), i.e. screen (825,675) ->
    # (1095,405), every point of which lies on the line x+y=1500.
    x0, y0 = 825, 675
    x1, y1 = 1095, 405
    # Sample the middle 60% of the chord, well clear of the L's own corners
    # (whose endpoints do sit on the top/left edges and would read as ink).
    ts = np.linspace(0.2, 0.8, 40)
    ink = 0
    total = 0
    for f in (frames[0], frames[len(frames) // 2], frames[-1]):
        for t in ts:
            cx = int(round(x0 + (x1 - x0) * t))
            cy = int(round(y0 + (y1 - y0) * t))
            patch = f[cy - 4:cy + 5, cx - 4:cx + 5]
            total += 1
            if patch.size and int(patch.max()) > 40:
                ink += 1

    assert ink == 0, (
        "ink on the closing chord (%d/%d samples): the open partial path was "
        "closed with a spurious diagonal -- the AnimatedBoundary bug"
        % (ink, total))
