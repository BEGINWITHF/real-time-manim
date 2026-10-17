"""Count gradient fills that lose their ramp (item a) and their stops (item b).

Two fill senders are instrumented while one wiki fragment records:

* ``PathMixin._send_polygon`` -- native ``AddPolygon`` carries ONE colour and no
  gradient channel (``native/platform.h``), so every multi-stop fill that lands
  here is painted as one flat colour where CE paints a
  ``cairo.LinearGradient``.  That is item (a).
* ``VMobjectMixin._send_vmobject`` -- ``shaded_fill_gradient`` can hand native
  only TWO stops (``AddBezierPath`` takes ``fr2/fg2/fb2`` + one axis), so a fill
  with THREE OR MORE distinct rows drops its middle stops.  That is item (b).

Each mobject is counted once per fragment (id-keyed) so a 250-frame clip still
prints a readable table.  Numbers only -- never opens an image.

    python tools/_probe_gradient_poly.py "<.../assets/RTM code/<page>.py>" <fragment>
"""
import argparse
import importlib.util
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402

POLY_LOG = []        # (type, n_verts, n_distinct_stops)
BEZ_LOG = []         # (type, n_distinct_stops)
_seen_poly = set()
_seen_bez = set()


def _distinct_stops(mob):
    """Distinct fill colours of ``mob``, or 0 when it has none/a flat fill."""
    try:
        rgbas = np.asarray(mob.get_fill_rgbas(), dtype=float)
    except Exception:
        return 0
    if rgbas.ndim != 2 or len(rgbas) == 0:
        return 0
    rows = np.unique(np.round(rgbas[:, :4], 4), axis=0)
    return int(len(rows))


def install():
    from real_time_manim.render.shapes.paths import PathMixin
    from real_time_manim.render.text.vmobject import VMobjectMixin

    orig_poly = PathMixin._send_polygon
    orig_bez = VMobjectMixin._send_vmobject

    def poly(self, mob, verts, alpha=1.0, rot_override=None, parent_offset=None):
        n = _distinct_stops(mob)
        if n > 1:
            nv = len(verts) if verts is not None else -1
            POLY_LOG.append((type(mob).__name__, nv, n))
            _seen_poly.add(id(mob))
        return orig_poly(self, mob, verts, alpha, rot_override, parent_offset)

    def bez(self, mob, a, w, h, parent_offset=None, rot=0.0, is_text=False,
            exact_width=False):
        n = _distinct_stops(mob)
        if n > 2:
            BEZ_LOG.append((type(mob).__name__, n))
            _seen_bez.add(id(mob))
        return orig_bez(self, mob, a, w, h, parent_offset, rot, is_text,
                        exact_width)

    PathMixin._send_polygon = poly
    VMobjectMixin._send_vmobject = bez


def _load(path):
    spec = importlib.util.spec_from_file_location(
        "_wiki_probe_" + str(abs(hash(path))), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page_py")
    ap.add_argument("fragments", nargs="*")
    args = ap.parse_args()
    page_py = os.path.abspath(args.page_py)

    from real_time_manim.record import fast_record_scene
    install()
    mod = _load(page_py)
    scenes = dict(getattr(mod, "SCENES", []))
    wanted = args.fragments or list(scenes)
    for name in wanted:
        cls = scenes[name]
        POLY_LOG.clear()
        BEZ_LOG.clear()
        _seen_poly.clear()
        _seen_bez.clear()
        print("=" * 20, name)
        fast_record_scene(cls, out_path=os.path.join(
            os.path.dirname(page_py), "final", name + ".mp4"),
            count_only=False, verbose=False)
        print("  (a) flat-painted gradient polygons (AddPolygon, no gradient):")
        print("      %d distinct mobjects, %d shape-calls" % (
            len(_seen_poly), len(POLY_LOG)))
        for e in sorted(set(POLY_LOG)):
            print("      %-24s verts=%-5d stops=%d" % e)
        print("  (b) bezier-path fills carrying >2 distinct stops (middle "
              "stops dropped):")
        print("      %d distinct mobjects, %d shape-calls" % (
            len(_seen_bez), len(BEZ_LOG)))
        for e in sorted(set(BEZ_LOG)):
            print("      %-24s stops=%d" % e)


if __name__ == "__main__":
    main()
