# -*- coding: utf-8 -*-
"""`tools/wiki_render.py` publish guards (no GPU / no window / no images).

Layout matters: a page script lives at `<assets>/RTM code/<page>.py`, its
fragments in `<assets>/RTM code/final/`, and the published clips in
`<assets>/RTM output/`.

Pinned rules:

* `02-Mobject通用/assets/RTM code/` holds 16 page scripts sharing one `final/`,
  so fragment names collide (`interpolate`, `coords`, `points`).  Publishing a
  fragment whose bytes may belong to a sibling page corrupts the clip -- measured
  live: page 10's 66-frame ValueTracker render landed in page 06's 96-frame
  `interpolate`.
* a scene that only feeds a *concatenated* output must not be published on its
  own (`01-MovingCameraScene`'s `camera_class_moving` / `_plain` are the halves
  of the embedded `...-camera_class.mp4`).
* a page without a `PAGE` constant whose `PAIRS` names are bare must still
  refresh the file the markdown points at (`01-MovingCameraScene-camera_class.mp4`,
  which had gone unrefreshed since 10-14).
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from tools import wiki_render  # noqa: E402

PAGE_A = '''
PAGE = "A"
SCENES = [("shared", object), ("only_a", object)]
PAIRS = [("shared", ["shared"]), ("only_a", ["only_a"])]
'''

PAGE_B = '''
PAGE = "B"
SCENES = [("shared", object), ("only_b", object)]
PAIRS = [("shared", ["shared"]), ("only_b", ["only_b"])]
'''

NO_PAGE_BARE = '''
SCENES = [("out_name", object)]
PAIRS = [("out_name", ["out_name"])]
'''

CONCAT_PAGE = '''
SCENES = [("part_a", object), ("part_b", object)]
PAIRS = [("combo", ["part_a"])]
'''


def _page(tmp_path, name, body):
    code = tmp_path / "assets" / "RTM code"
    code.mkdir(parents=True, exist_ok=True)
    p = code / name
    p.write_text(body, encoding="utf-8")
    return p


def _final(tmp_path):
    d = tmp_path / "assets" / "RTM code" / "final"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _out(tmp_path):
    d = tmp_path / "assets" / "RTM output"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# cross-page fragments
# ---------------------------------------------------------------------------

def test_shared_fragments_are_detected(tmp_path):
    a = _page(tmp_path, "A.py", PAGE_A)
    _page(tmp_path, "B.py", PAGE_B)
    mod = wiki_render._load(str(a))
    here = os.path.dirname(str(a))
    assert wiki_render._shared_fragments(here, str(a), mod) == {"shared"}


def test_refresh_only_skips_the_shared_fragment(tmp_path):
    a = _page(tmp_path, "A.py", PAGE_A)
    _page(tmp_path, "B.py", PAGE_B)
    final, out = _final(tmp_path), _out(tmp_path)
    (final / "shared.mp4").write_bytes(b"shared")
    (final / "only_a.mp4").write_bytes(b"only_a")
    (out / "A-shared.mp4").write_bytes(b"old")
    (out / "A-only_a.mp4").write_bytes(b"old")

    wiki_render.render(str(a), [], refresh_only=True)

    assert (out / "A-only_a.mp4").read_bytes() == b"only_a", "not published"
    assert (out / "A-shared.mp4").read_bytes() == b"old", "clobbered by a sibling"


def test_scene_clip_prefix_guard_does_not_cross_pages(tmp_path):
    """`B-shared.mp4` must never be refreshed while publishing page A."""
    a = _page(tmp_path, "A.py", PAGE_A)
    _page(tmp_path, "B.py", PAGE_B)
    final, out = _final(tmp_path), _out(tmp_path)
    (final / "shared.mp4").write_bytes(b"shared")
    (final / "only_a.mp4").write_bytes(b"only_a")
    (out / "B-shared.mp4").write_bytes(b"b-old")

    wiki_render.render(str(a), [], refresh_only=True)

    assert (out / "B-shared.mp4").read_bytes() == b"b-old"


# ---------------------------------------------------------------------------
# publish-name rules
# ---------------------------------------------------------------------------

def test_bare_pairs_name_follows_the_published_file(tmp_path):
    """No PAGE + bare PAIRS name: refresh the file the markdown points at."""
    p = _page(tmp_path, "Demo.py", NO_PAGE_BARE)
    final, out = _final(tmp_path), _out(tmp_path)
    (final / "out_name.mp4").write_bytes(b"frag")
    (out / "Demo-out_name.mp4").write_bytes(b"old")

    wiki_render.render(str(p), [], refresh_only=True)

    assert (out / "Demo-out_name.mp4").read_bytes() == b"frag"
    assert not (out / "out_name.mp4").exists(), "must not create an unlinked name"


def test_concat_subscene_is_not_published_on_its_own(tmp_path):
    p = _page(tmp_path, "Page.py", CONCAT_PAGE)
    final, out = _final(tmp_path), _out(tmp_path)
    (final / "part_a.mp4").write_bytes(b"a")
    (final / "part_b.mp4").write_bytes(b"b")
    (out / "Page-combo.mp4").write_bytes(b"old-combo")
    (out / "Page-part_a.mp4").write_bytes(b"stale-part")

    wiki_render.render(str(p), [], refresh_only=True)

    assert (out / "Page-combo.mp4").read_bytes() == b"a"       # output refreshed
    assert (out / "Page-part_a.mp4").read_bytes() == b"stale-part", (
        "the sub-scene must not be republished on its own")
