"""Verdict test for wiki page ``02-play与wait参数`` (issues.txt lines 35-36).

The page carried the highest residual mean|diff| in the whole wiki table
(**2.380**, bad=0/480, the runner-up was 0.853).  The original report was
"shift down 被展示成了 up"; that direction bug is fixed (bad frames 44 -> 0)
and this test pins the verdict on what the remaining 2.380 *is*:

**It is not an RTM text-metrics bug.**

Evidence (all numbers measured, reproducible via ``tools/_probe_play02*.py``):

1. The two demo sources intentionally differ in four strings -- RTM shows
   ``win.play(...)``, the ManimCE twin shows ``self.play(...)`` (title, l1,
   l3, l4).  Every one of those lines is *centred*, so a width delta ``d``
   (ce minus rtm) between the two spellings rigidly shifts the shared prefix
   by ``-d/2`` and the shared suffix by ``+d/2``.  Layout of both renderers
   is the same code (RTM vendors ManimCE 0.21.0 and reuses its Pango-based
   ``Text``), so the shift is exactly half the string width delta: +-3.71 px
   at 1920x1080.
   Measured on the checked-in videos by column-profile cross-correlation:
   title prefix 3.80 px (CE right), title suffix 3.88 px, l1 3.82 px,
   l3 3.81 px, l4 3.83 px (CE left) -- and the single rigid shift explains
   73-89% of the per-band residual.
2. Where the two sources ARE identical -- the ``run_time=1.6, rate_func=linear)``
   control line l2 -- RTM and CE place the text at the same position to
   **-0.001 px**.  There is no systematic or per-glyph metric drift in RTM.
3. Controlled A/B render: re-rendering the page with the CE strings swapped
   in (all other code identical) drops the mean|diff| over the time-aligned
   frames 0..215 from **2.2286** to **0.3757**.  So ~83% of the residual is
   the intentional content difference; the remaining ~0.38 is the
   Cairo-vs-Vulkan rasteriser floor (identical geometry, different AA).

The tests below pin each link of that chain so a *future* text-placement
regression in RTM (pixel snapping, per-glyph rounding, a forked layout)
fails loudly instead of hiding behind "font metric noise".

Pure Python + numpy + ffmpeg; no GPU, no window, no image inspection.
"""
import functools
import os
import shutil
import subprocess
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import numpy as np  # noqa: E402

from manim import Text  # noqa: E402  (bundled; conftest pins the import order)

from real_time_manim.render.util import manim_to_screen  # noqa: E402

# The four string pairs the two demo sources disagree on, plus the two
# identical control lines.  (label, rtm string, ce string, font_size)
PAGE_PAIRS = [
    ("title",
     "02-Scene.play / wait 参数（win.play 等价）",
     "02-Scene.play / wait 参数（self.play 等价）", 42),
    ("l1",
     "win.play(Create(sq), FadeIn(ci, scale=0.5),",
     "self.play(Create(sq), FadeIn(ci, scale=0.5),", 30),
    ("l2 (control, identical)",
     "         run_time=1.6, rate_func=linear)   # 逐个 setattr",
     "         run_time=1.6, rate_func=linear)   # 逐个 setattr", 30),
    ("l3",
     "win.play(*[FadeIn(m, shift=DOWN) for m in dots])",
     "self.play(*[FadeIn(m, shift=DOWN) for m in dots])", 30),
    ("l4",
     "win.play(Wait(1.2))   #  ≡  self.wait(1.2)",
     "self.play(Wait(1.2))   #  ≡  self.wait(1.2)", 30),
    ("txt (control, identical)",
     "静止 1.2 秒",
     "静止 1.2 秒", 30),
]
DIFFERING = [p for p in PAGE_PAIRS if p[1] != p[2]]
CONTROLS = [p for p in PAGE_PAIRS if p[1] == p[2]]

#: 1920x1080: 1 manim unit = 1080/8 = 135 px, frame centre at x = 960.
PX_PER_UNIT = 1080 / 8.0
CENTRE_X = 1920 / 2.0

# Glyph geometry is float32 (SVG -> manim points) and the sender packs
# vertices into ctypes c_float.  At x ~ 1000 px one float32 ULP is 6.1e-05
# px, so "identical" here means equal to within an ULP -- never bit-equal.
# Calibrated on this page's strings: the largest observed per-glyph spread
# or send-path mismatch is 8.4e-06 px.
FLOAT32_PX_TOL = 5e-5

# Measured on the checked-in videos (tools/_probe_play02_shift.py); the
# layout predicts +-3.71 px, the videos read 3.80-3.88 (the CE twin was
# rendered by a Pango build that quantises "win." - "self" ~0.1 px wider).
# The tolerance band below is deliberately wider than both.
SHIFT_BAND_PX = (3.0, 4.5)


# --------------------------------------------------------------------------
# layout: what the shared Pango pipeline produces for the page's strings
# --------------------------------------------------------------------------
def _glyph_xs(text, font_size):
    """(left, right, [x centre of each glyph]) in manim units."""
    t = Text(text, font_size=font_size)
    xs = [float(sub.get_center()[0]) for sub in t.submobjects]
    return float(t.get_left()[0]), float(t.get_right()[0]), xs


def _common_affix(a, b):
    """(common prefix chars, common suffix chars) of two strings."""
    k = 0
    while k < len(a) and k < len(b) and a[k] == b[k]:
        k += 1
    m = 0
    while m < len(a) - k and m < len(b) - k and a[-1 - m] == b[-1 - m]:
        m += 1
    return k, m


def _glyph_index_for_char(text, char_idx):
    """Glyph index of character ``char_idx`` (``Text`` drops whitespace)."""
    return sum(1 for ch in text[:char_idx] if not ch.isspace())


def _affix_drift(a_text, b_text, font_size):
    """Screen-px drift (ce - rtm) of the shared prefix and suffix glyphs."""
    _, _, xa = _glyph_xs(a_text, font_size)
    _, _, xb = _glyph_xs(b_text, font_size)
    k, m = _common_affix(a_text, b_text)
    out = {}
    ia, ib = _glyph_index_for_char(a_text, k), _glyph_index_for_char(b_text, k)
    n = min(ia, ib)
    if n:
        out["head"] = [(xb[i] - xa[i]) * PX_PER_UNIT for i in range(n)]
    ja = _glyph_index_for_char(a_text, len(a_text) - m) if m else len(xa)
    jb = _glyph_index_for_char(b_text, len(b_text) - m) if m else len(xb)
    n = min(len(xa) - ja, len(xb) - jb)
    if n:
        out["tail"] = [(xb[len(xb) - n + i] - xa[len(xa) - n + i]) * PX_PER_UNIT
                       for i in range(n)]
    return out


@pytest.mark.parametrize("label", [p[0] for p in CONTROLS])
def test_identical_strings_layout_bit_exact(label):
    """Control lines: same string in both sources -> bit-exact same layout.

    RTM consumes the very ``Text`` geometry CE lays out (one vendored
    implementation), so identical input must give *identical* floats -- any
    drift here would be an RTM-side fork of the layout.
    """
    _, a, b, size = next(p for p in CONTROLS if p[0] == label)
    la, ra, xa = _glyph_xs(a, size)
    lb, rb, xb = _glyph_xs(b, size)
    assert abs(ra - rb) < FLOAT32_PX_TOL
    assert abs(la - lb) < FLOAT32_PX_TOL
    assert np.allclose(xa, xb, atol=FLOAT32_PX_TOL, rtol=0)


@pytest.mark.parametrize("label", [p[0] for p in DIFFERING])
def test_string_difference_shifts_shared_text_rigidly(label):
    """The page's four differing lines: the shared text moves as ONE RIGID
    block -- no per-glyph drift -- by half the width delta, i.e. the exact
    consequence of centring a line whose spelling changed.

    Sign rule for a centred line ``P + A + S`` whose middle ``A`` changes by
    ``d = width_ce(A) - width_rtm(A)``: the shared prefix ``P`` sits at
    ``-d/2``, the shared suffix ``S`` at ``+d/2`` (both in ce-minus-rtm).
    """
    _, a, b, size = next(p for p in DIFFERING if p[0] == label)
    la, ra, _ = _glyph_xs(a, size)
    lb, rb, _ = _glyph_xs(b, size)
    half_delta = (rb - lb - (ra - la)) / 2.0 * PX_PER_UNIT   # (ce - rtm)/2

    drift = _affix_drift(a, b, size)
    for which, values in drift.items():
        values = np.asarray(values)
        spread = float(values.max() - values.min())
        mean = float(values.mean())
        # rigid: every glyph of the affix moves by the same amount
        assert spread < FLOAT32_PX_TOL, f"{label} {which}: drift {spread}px"
        # magnitude: centred line -> exactly half the width delta
        target = -half_delta if which == "head" else +half_delta
        assert mean == pytest.approx(target, abs=FLOAT32_PX_TOL), label
        assert SHIFT_BAND_PX[0] <= abs(mean) <= SHIFT_BAND_PX[1], label


def test_control_lines_never_move():
    """Both control lines: width delta exactly zero -> zero shift."""
    for _, a, b, size in CONTROLS:
        la, ra, _ = _glyph_xs(a, size)
        lb, rb, _ = _glyph_xs(b, size)
        assert abs((ra - la) - (rb - lb)) < FLOAT32_PX_TOL
        for values in _affix_drift(a, b, size).values():
            assert max(abs(v) for v in values) < FLOAT32_PX_TOL


# --------------------------------------------------------------------------
# send path: RTM must place CE's glyphs exactly where CE's layout put them
# --------------------------------------------------------------------------
class _RecordingDll:
    """Stands in for ``vulkan_core.dll``; records ``AddBezierPath`` calls."""

    def __init__(self):
        self.calls = []

    def AddBezierPath(self, arr, n, *args):
        self.calls.append((list(arr), int(n)))


@pytest.fixture(autouse=True)
def _no_viewport():
    """Keep ``manim_to_screen`` on its plain linear map (no camera viewport)."""
    from real_time_manim import camera_state
    camera_state.set_viewport(None)
    yield
    camera_state.set_viewport(None)


def test_text_send_path_applies_no_rounding():
    """Every glyph vertex RTM hands to native is *exactly*
    ``960 + x * 135`` -- no pixel snapping, no per-glyph rounding, no metric
    adjustment on top of CE's layout.  (This is the invariant whose
    violation would make RTM drift away from CE by fractions of a pixel per
    glyph, the class of bug this page was suspected of.)"""
    from real_time_manim.vulkan_bind import MLWindow

    win = MLWindow.__new__(MLWindow)          # no __init__: no DLL, no window
    win.dll = _RecordingDll()

    mob = Text("run_time=1.6, rate_func=linear", font_size=30)
    letter_alphas = {i: 1.0 for i in range(len(mob.submobjects))}
    win._send_text_write(mob, letter_alphas, 1920, 1080)

    xs, ys = [], []
    for call, n in win.dll.calls:
        flat = np.asarray(call, dtype=np.float64).reshape(-1, 3)
        assert 0 < n <= len(flat), "sender sent an empty or overlong path"
        xs.append(flat[:n, 0])
        ys.append(flat[:n, 1])
    xs = np.concatenate(xs)
    ys = np.concatenate(ys)
    assert xs.size > 0

    expected_x, expected_y = [], []
    for sub in mob.submobjects:
        pts = sub.get_points()
        n = (len(pts) // 4) * 4                 # sender truncates to beziers
        for p in pts[:n]:
            sx, sy = manim_to_screen(float(p[0]), float(p[1]), 1920, 1080, p[2])
            expected_x.append(sx)
            expected_y.append(sy)
    expected_x = np.asarray(expected_x, dtype=np.float32).astype(np.float64)
    expected_y = np.asarray(expected_y, dtype=np.float32).astype(np.float64)
    assert np.allclose(xs, expected_x, atol=FLOAT32_PX_TOL, rtol=0), \
        "glyph x drifted from CE's layout"
    assert np.allclose(ys, expected_y, atol=FLOAT32_PX_TOL, rtol=0), \
        "glyph y drifted from CE's layout"
    # ... and the projection is the plain linear map, no snapping / offset
    all_x = np.asarray([float(p[0]) for sub in mob.submobjects
                        for p in sub.get_points()[:len(sub.get_points()) // 4 * 4]])
    linear = np.asarray(CENTRE_X + all_x * PX_PER_UNIT,
                        dtype=np.float32).astype(np.float64)
    assert np.allclose(xs, linear, atol=FLOAT32_PX_TOL, rtol=0)


# --------------------------------------------------------------------------
# checked-in artifacts: the measured shift pattern of the actual videos
# --------------------------------------------------------------------------
WIKI = "C:/Users/begin/Desktop/RTM-Wiki"
RTM_MP4 = os.path.join(WIKI, "03-动画/通用/assets/RTM output/02-play与wait参数.mp4")
CE_MP4 = os.path.join(WIKI, "03-动画/通用/assets/ManimCE output/02-play与wait参数-manimce.mp4")

_VIDEO_OK = bool(shutil.which("ffmpeg")) and \
    os.path.exists(RTM_MP4) and os.path.exists(CE_MP4)


VIDEO_CENTRES = (130, 190, 225, 310)
VIDEO_FRAMES = tuple(sorted({i + d for i in VIDEO_CENTRES for d in (-2, 0, 2)}))


@functools.lru_cache(maxsize=None)
def _video_frames(path):
    """Decode the frames of interest at native 1920x1080, cached per file."""
    sel = "+".join(f"eq(n\\,{i})" for i in VIDEO_FRAMES)
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"select={sel}",
           "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    size = 1080 * 1920 * 3
    frames = np.frombuffer(raw[:len(raw) // size * size], dtype=np.uint8)
    frames = frames.reshape(-1, 1080, 1920, 3)
    assert frames.shape[0] == len(VIDEO_FRAMES), path
    return {idx: frames[i] for i, idx in enumerate(VIDEO_FRAMES)}


def _is_frozen(frames, idx, span=2, tol=1.5):
    """True when the video is static around ``idx`` (the measurement only
    makes sense on a frozen frame).

    Calibrated on this page: a still Wait(1.2) frame reads d~0.69 (pure h264
    noise), while an actively animating one reads far above tol.
    """
    d = np.abs(frames[idx + span].astype(np.int16)
                - frames[idx - span].astype(np.int16)).mean()
    return float(d) < tol


def _profile(img, y0, y1):
    return img[y0:y1].astype(np.float64).mean(axis=2).sum(axis=0)


def _best_shift(pa, pb, x0, x1, max_lag=14):
    """Sub-pixel px that ``pb`` must move RIGHT to sit on ``pa``.

    Positive == profile ``b`` (CE) is LEFT of ``a`` (RTM) by that amount.
    Returns (shift, residual at zero shift, residual at best shift).
    """
    win_a = pa[x0:x1]
    lags = np.arange(-max_lag, max_lag + 1)
    res = np.array([np.abs(win_a - pb[x0 - l:x1 - l]).mean() for l in lags])
    k = int(res.argmin())
    s = float(lags[k])
    if 0 < k < len(lags) - 1:
        y0_, y1_, y2_ = res[k - 1], res[k], res[k + 1]
        den = y0_ - 2 * y1_ + y2_
        if den > 0:
            s += 0.5 * (y0_ - y2_) / den
    r0 = float(np.abs(win_a - pb[x0:x1]).mean())
    return s, r0, float(res[k])


@pytest.mark.skipif(not _VIDEO_OK,
                    reason="ffmpeg or the wiki videos are not available")
@pytest.mark.parametrize("frame_idx,y0,y1,x0,x1,label,expected", [
    # f130 (t=2.17s): title + l1 + l2 on screen, all frozen
    (130, 284, 322, 250, 1750, "l2 identical control", 0.0),
    (130, 210, 262, 400, 1700, "l1 shared tail", +1.0),
    (130, 60, 150, 150, 1150, "title shared prefix", -1.0),
    # f190 (t=3.17s): title still up; suffix after the win/self difference
    (190, 60, 150, 1250, 1700, "title shared suffix", +1.0),
    # f225 (t=3.75s): l3 frozen between FadeIn and FadeOut
    (225, 210, 262, 400, 1700, "l3 shared tail", +1.0),
    # f310 (t=5.17s): l4 frozen during Wait(1.2)
    (310, 210, 280, 350, 1700, "l4 shared tail", +1.0),
])
def test_checked_in_videos_show_only_the_content_shift(
        frame_idx, y0, y1, x0, x1, label, expected):
    """On the actual wiki artifacts: identical text lands at the same x
    (control), and the four intentionally-different lines are rigidly
    displaced by ~3.8 px -- half the `win.`/`self` width delta."""
    rtm = _video_frames(RTM_MP4)
    ce = _video_frames(CE_MP4)
    if not (_is_frozen(rtm, frame_idx) and _is_frozen(ce, frame_idx)):
        pytest.skip(f"frame {frame_idx} is no longer frozen (page timing changed)")
    shift, r0, rb = _best_shift(_profile(rtm[frame_idx], y0, y1),
                                _profile(ce[frame_idx], y0, y1), x0, x1)
    print(f"    [{label}] shift={shift:+.3f}px  residual {r0:.1f} -> {rb:.1f}"
          f"  ({100 * (1 - rb / r0):.0f}% explained)")
    if expected == 0.0:
        assert abs(shift) < 0.25, \
            f"{label}: RTM/CE disagree by {shift:.3f} px on IDENTICAL text"
    else:
        assert expected * shift > 0, f"{label}: wrong direction ({shift:+.3f})"
        assert SHIFT_BAND_PX[0] <= abs(shift) <= SHIFT_BAND_PX[1], \
            f"{label}: {shift:+.3f} px outside the content-shift band"
        # the single rigid shift must explain most of the band residual
        assert rb < 0.4 * r0, \
            f"{label}: shift explains too little ({r0:.1f} -> {rb:.1f})"
