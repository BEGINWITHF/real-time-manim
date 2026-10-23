# This might not cause a bug or issue, check for other place first --TT Noted
"""Point-wise deformation animation: RTM's own ``Homotopy``.

Time semantics are RTM's: ``begin(t)`` / ``interpolate(t)`` with ``t`` in
seconds.  ``apply_function_kwargs`` is the CE parameter of the same name: it
is forwarded to ``Mobject.apply_function`` semantics, i.e. it selects the
point the homotopy function is applied *around* (``about_point`` /
``about_edge``; with neither given manim applies the function about
``ORIGIN``, which is plain absolute-coordinate mapping).

Importing this module also installs a runtime fix for the upstream
``VMobject.apply_function`` pivot drop (see
:func:`_install_apply_function_pivot_fix`), which is what makes
``apply_function_kwargs`` work for the manim-native
``SmoothedVectorizedHomotopy`` / ``ComplexHomotopy`` as well.
"""

from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np

# The only keyword arguments Mobject.apply_function() accepts.
_APPLY_FUNCTION_KWARGS = ("about_point", "about_edge")


def _install_apply_function_pivot_fix():
    """Upstream defect: ``VMobject.apply_function`` drops its pivot kwargs.

    manim CE 0.19-0.21 declares ``about_point``/``about_edge`` on
    ``VMobject.apply_function`` but calls ``super().apply_function(function)``
    without them, so ``Mobject.apply_function`` never sees the pivot and maps
    about ``ORIGIN`` instead.  That silently killed
    ``Homotopy(apply_function_kwargs=...)`` for every vectorized mobject --
    ``SmoothedVectorizedHomotopy`` / ``ComplexHomotopy`` included (their
    ``interpolate_submobject`` forwards the dict straight into
    ``apply_function``).  The defect is identical in the bundled copy and in
    an external ManimCE install, and ``real_time_manim`` keeps an
    already-imported external manim, so the fix has to be applied to
    whichever ``VMobject`` class is active at runtime.  Idempotent: it does
    nothing when the active implementation already forwards.
    """
    try:
        from manim.mobject.types.vectorized_mobject import VMobject
    except Exception:                                   # pragma: no cover
        return False
    original = getattr(VMobject, "apply_function", None)
    if original is None or getattr(original, "_rtm_forwards_pivot", False):
        return False

    def apply_function(self, function, *, about_point=None, about_edge=None):
        factor = self.pre_function_handle_to_anchor_scale_factor
        self.scale_handle_to_anchor_distances(factor)
        # ``super(VMobject, self)`` is Mobject.apply_function -- the method the
        # upstream implementation meant to call with the pivot.
        super(VMobject, self).apply_function(
            function, about_point=about_point, about_edge=about_edge
        )
        self.scale_handle_to_anchor_distances(1.0 / factor)
        if self.make_smooth_after_applying_functions:
            self.make_smooth()
        return self

    apply_function._rtm_forwards_pivot = True
    VMobject.apply_function = apply_function
    return True


_install_apply_function_pivot_fix()


def _handle_scale_factor(fm):
    """``VMobject.pre_function_handle_to_anchor_scale_factor``, else ``None``.

    ``None`` means "this mobject is not a bezier path" (a ``PMobject``, a bare
    ``Mobject``), so the CE handle dance must not run on it.
    """
    if len(getattr(fm, "points", ())) < 4:
        return None
    try:
        from manim.mobject.types.vectorized_mobject import VMobject
        if not isinstance(fm, VMobject):
            return None
    except Exception:                                   # pragma: no cover
        return None
    return float(getattr(fm, "pre_function_handle_to_anchor_scale_factor",
                         0.01))


def _scale_handles(points, n, factor):
    """Vectorised ``VMobject.scale_handle_to_anchor_distances`` on one array.

    ``points`` is modified in place; ``n`` is the usable prefix (a multiple of
    the 4-point cubic stride).  A handle ``H`` next to anchor ``A`` becomes
    ``A + factor * (H - A)`` -- handle 1 relative to the anchor before it,
    handle 2 relative to the anchor after it, exactly as manim does.
    """
    a1 = points[0:n:4].copy()
    h1 = points[1:n:4]
    h1[:] = a1 + factor * (h1 - a1)
    a2 = points[3:n:4].copy()
    h2 = points[2:n:4]
    h2[:] = a2 + factor * (h2 - a2)


def apply_homotopy_to_points(points, mapping, factor=None):
    """Map every point the way manim CE's ``VMobject.apply_function`` does.

    CE's ``Homotopy`` does not simply run the homotopy over the control
    points.  ``VMobject.apply_function`` first pulls every bezier handle to
    ``pre_function_handle_to_anchor_scale_factor`` (0.01) of its distance from
    its anchor, applies the function to ALL points, then pushes the handles
    back out by ``1 / factor``.  Because the handle lands at the image of a
    point 1 % along the edge and is then extrapolated 100x, the curve that is
    finally stroked follows the homotopy of the *curve*, not of the four
    anchors.

    Measured on wiki ``03-动画/移动与旋转/02-沿路径与同态变换-homotopy``:
    ``wave(x, y, z, t) = (x, y + 0.45 sin(2.2 x + 2 pi t))`` bends a Rectangle
    whose top edge spans x in [-2.2, 2.2] -- 1.5 wavelengths of the wave.  With
    the raw control-point mapping (the old RTM loop) the handles land at the
    wave's value *at the handle*, i.e. the exact opposite side of the anchors
    at the half-wavelength, so the cubic degenerates into a nearly straight
    chord: the centre column of the rectangle never moved (top edge pinned at
    y=148 while CE swings 114..183) and the whole clip scored mean|diff|
    2.303 / 42 bad frames against CE.  With CE's own maths the same frame
    sends handles 0.608 units out where RTM sent -0.45, and the curve snakes.

    ``factor`` is ``None`` for a mobject that is not a bezier path; those keep
    the plain point mapping (which is all ``Mobject.apply_function`` does).
    ``points`` is modified in place and returned.
    """
    pts = np.asarray(points, dtype=float)
    n = (len(pts) // 4) * 4
    use_handles = factor is not None and n >= 4 and factor not in (0.0, 1.0)
    if use_handles:
        _scale_handles(pts, n, factor)
    for i in range(len(pts)):
        px, py, pz = pts[i][0], pts[i][1], pts[i][2]
        nx, ny, nz = mapping(px, py, pz)
        pts[i][0] = nx
        pts[i][1] = ny
        pts[i][2] = nz
    if use_handles:
        _scale_handles(pts, n, 1.0 / factor)
    return pts


class Homotopy(Animation):
    def __init__(self, homotopy, mobject, run_time=3.0, apply_function_kwargs=None, **kwargs):
        self.homotopy = homotopy
        if apply_function_kwargs is None:
            apply_function_kwargs = {}
        unknown = set(apply_function_kwargs) - set(_APPLY_FUNCTION_KWARGS)
        if unknown:
            # CE would raise the same TypeError from
            # ``Mobject.apply_function(**kwargs)`` -- just earlier and clearer.
            raise TypeError(
                "Homotopy: Mobject.apply_function() got unexpected keyword "
                "argument(s) %s (only %s are supported)"
                % (sorted(unknown), ", ".join(_APPLY_FUNCTION_KWARGS))
            )
        self.apply_function_kwargs = dict(apply_function_kwargs)
        self._orig_points = {}
        super().__init__(mobject, run_time=run_time, **kwargs)

    def function_at_time_t(self, t):
        """The point mapping for progress ``t`` (CE parity helper)."""
        def mapping(p):
            return np.array(self.homotopy(p[0], p[1], p[2], t))
        return mapping

    def _pivot_for(self, fm):
        """The point ``fm.apply_function`` would translate around."""
        about_point = self.apply_function_kwargs.get("about_point")
        about_edge = self.apply_function_kwargs.get("about_edge")
        if about_point is None and about_edge is None:
            about_point = np.zeros(3)          # apply_function's ORIGIN default
        elif about_point is None:
            about_point = fm.get_critical_point(about_edge)
        return np.array(about_point, dtype=float)

    def begin(self, t):
        super().begin(t)
        mob = self.mobject
        mob._transforming = True
        if hasattr(mob, 'family_members_with_points'):
            for fm in mob.family_members_with_points():
                try:
                    self._orig_points[id(fm)] = fm.points.copy()
                except Exception:
                    pass

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        mob = self.mobject
        if not hasattr(mob, 'family_members_with_points'):
            return

        for fm in mob.family_members_with_points():
            if id(fm) not in self._orig_points:
                continue
            # `apply_function(func, about_point=P)` maps `p -> func(p - P) + P`.
            pivot = self._pivot_for(fm)
            pts = np.array(self._orig_points[id(fm)], dtype=float, copy=True)
            pts -= pivot
            # CE's VMobject.apply_function collapses the bezier handles around
            # the mapping and expands them afterwards (see
            # apply_homotopy_to_points); without that the drawn curve is the
            # chord between the anchors and a homotopy wave is invisible.
            apply_homotopy_to_points(
                pts,
                lambda x, y, z: self.homotopy(x, y, z, alpha),
                _handle_scale_factor(fm),
            )
            fm.points = pts + pivot
            if getattr(fm, "make_smooth_after_applying_functions", False):
                try:
                    fm.make_smooth()
                except Exception:                       # pragma: no cover
                    pass

    def finish(self):
        super().finish()
        mob = self.mobject
        mob._transforming = False
        # CE leaves the mobject at its FINAL deformed state.  ``Homotopy`` is
        # not a Transform -- there is no target copy to restore to -- and
        # manim's ``Animation.finish`` touches no points.  RTM used to copy the
        # begin-state points back here, so every homotopy visibly snapped back
        # on its last frame: the wiki's
        # ``03-动画/移动与旋转/02-沿路径与同态变换-homotopy`` clip ended on the
        # UNDEFORMED rectangle while CE ends on the wave (measured at t=3.13 s:
        # RTM's top edge back at y=148 where CE snakes 114..183, 3.03 % of the
        # frame visibly different).  ``_orig_points`` has done its job by the
        # last interpolate() -- every frame re-derives the deformation from it,
        # so nothing needs restoring.
        self._orig_points.clear()
