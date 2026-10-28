"""Paint ordering: the deferred paint queue and every depth / z-index rule.

The queue collects what each root would paint during `sync`; the flush
afterwards paints in Manim CE's own precedence (camera-space depth,
z_index, family pre-order, visit order)."""

import ctypes
import math



# native AddPolygon stores at most this many vertices and silently drops any
# polygon that exceeds it (see native/shared_types.h MAX_POLYGON_VERTS and the
# guard in platform.c).  Send larger polygons down the bezier path instead.
NATIVE_MAX_POLYGON_VERTS = 64


def container_subs(mob):
    """The children of a container mobject.

    manim's ``Mobject.__iter__`` yields *self first* when the mobject has points
    (``it.chain([self] if self.has_points() else [], self.submobjects)``), so
    ``enumerate(mob)`` / ``len(list(mob))`` on a point-bearing VGroup hands the
    container back to itself -- a 978-frame recursion in HeatDiagramPlot, and an
    off-by-one in the progress segmentation.  Iterate ``submobjects`` instead.
    """
    return getattr(mob, "submobjects", None) or ()


def depth_key(mob, viewport):
    """One mobject's camera-space depth, exactly as manim scores it.

    ``ThreeDCamera.get_mobjects_to_display`` flattens the whole scene family
    and paints it ``sorted`` by ``np.dot(mob.get_z_index_reference_point(),
    rot.T)[2]`` -- the cell nearest the camera gets the largest key and is
    therefore painted last, on top.  Mobjects that are not ``shade_in_3d``
    score ``inf`` so text and 2D overlays always end up above the 3D content.

    A viewport without a rotation matrix (a 2D scene, or a viewport that is
    not published at all) also scores ``inf``: then every unit ties and the
    caller falls back to document order, which is what manim does when there
    is no 3D camera to sort against.
    """
    if not getattr(mob, "shade_in_3d", False):
        return math.inf
    rot = getattr(viewport, "rotation", None)
    if rot is None:
        return math.inf
    try:
        # CE's ThreeDCamera sorts by get_z_index_reference_point(), not
        # get_center(): z_index_group/z_index_as_group moves the reference
        # point to the group's centre.  Using get_center() here silently
        # ignored that group anchor and reordered those mobjects differently
        # from CE.
        c = mob.get_z_index_reference_point()
    except Exception:
        return math.inf
    return float(rot[2][0] * c[0] + rot[2][1] * c[1] + rot[2][2] * c[2])


class _PaintQueue:
    """One frame's deferred paint list, ordered the way Manim CE paints.

    CE never paints mobject by mobject: ``Camera.get_mobjects_to_display``
    flattens the *whole* scene family (``extract_mobject_family_members``) and
    ``ThreeDCamera`` then stable-sorts every member by its own camera-space
    depth, so the cells of neighbouring roots interleave.  A ``Dot3D`` sitting
    on a saddle ``Surface`` is painted between the saddle's own cells and ends
    up half hidden behind them.

    Sorting RTM's roots cannot express that: ``Surface``, ``Dot3D``,
    ``Line3D`` and ``Arrow3D`` are ``VGroup``-derived containers whose own
    ``shade_in_3d`` is False (the VGroup default), so they all score ``inf``
    and are painted as one block in insertion order -- the sphere came out in
    front of the surface and the ribbon behind it, the exact reverse of CE.

    ``sync`` therefore walks the roots *first* and collects what each one
    would paint; the queue is flushed afterwards.  The sort key is CE's own,
    in CE's own precedence:

        (camera-space depth, z_index, family pre-order, visit order)

    ``Camera.get_mobjects_to_display`` stable-sorts the flattened family by
    ``z_index`` first, and ``ThreeDCamera.get_mobjects_to_display`` then
    stable-sorts *that* list by depth -- so depth wins over ``z_index`` in a
    3D scene (a ``z_index=-1`` overlay still lands on top of every shaded
    face, because it scores ``inf``), and ``z_index`` wins over position
    everywhere.  The family pre-order is CE's tie-break of last resort; it is
    looked up from ``index``, which ``sync`` builds exactly the way
    ``extract_mobject_family_members`` does (first occurrence of a shared
    member wins).  The visit counter only ranks units the map does not know.
    """

    __slots__ = ("viewport", "units", "_seq", "index", "z_mode", "cleanup")

    def __init__(self, viewport=None, index=None, z_mode=False):
        self.viewport = viewport
        # (depth key, z_index, family pre-order, visit order, paint callback)
        self.units = []
        self._seq = 0
        self.index = index if index is not None else {}
        self.z_mode = bool(z_mode)
        # (mobject, drop _grow_scale, drop _grow_point) undone after the paint
        self.cleanup = []

    def add(self, key, paint, mob=None):
        seq = self._seq
        self._seq = seq + 1
        if mob is None:
            z = 0.0
        elif self.z_mode:
            z = unit_z_index(mob)
        else:
            z = 0.0
        fam = self.index.get(id(mob)) if mob is not None else None
        if fam is None:
            # Outside the map: rank after everything the map does know, in the
            # order the walk met it.
            fam = len(self.index) + seq
        self.units.append((float(key), z, int(fam), seq, paint))

    def flush(self):
        units = sorted(self.units, key=lambda unit: unit[:4])
        del self.units[:]
        try:
            for *_keys, paint in units:
                paint()
        finally:
            cleanup, self.cleanup = self.cleanup, []
            for sub, drop_gs, drop_gp in cleanup:
                # The submobject was only *queued* while its parent still held
                # the inherited grow state; the sender read it during paint().
                if drop_gs:
                    sub.__dict__.pop('_grow_scale', None)
                if drop_gp:
                    sub.__dict__.pop('_grow_point', None)


def lend_grow(parent, sub):
    """Copy ``parent``'s grow state onto ``sub`` for the paint ahead.

    ``GrowFromCenter`` / ``GrowArrow`` / ``Indicate`` stamp
    ``_grow_scale``/``_grow_point`` on the ANIMATED mobject only, and every
    leaf sender reads the channels off the mobject it is drawing.  So a parent
    that only *dispatches* (a ``VGroup``) has to hand the state down its
    children, or the container grows while its contents stay at full size.

    The ``VGroup``/3D branches always did that; the branches where a mobject
    carries points AND children of its own -- a ``Rectangle`` and its
    ``grid_lines``, a ``RoundedRectangle``/``NumberLine``/labelled ``Dot``
    walked by the generic family walk -- never did, so a channel-only grow
    (an RTM animation, ``Flash``, ``Circumscribe``) on such a shape scaled the
    parent and left its contents at full size.

    manim's own ``GrowFrom*`` need no loan: they are Transforms and scale the
    points, so no channel is written at all (see ``_write_grow``).

    Returns the pair :func:`release_grow` needs to take the loan back.
    """
    pg_gs = getattr(parent, "_grow_scale", None)
    pg_gp = getattr(parent, "_grow_point", None)
    need_gs = pg_gs is not None and not hasattr(sub, "_grow_scale")
    need_gp = pg_gp is not None and not hasattr(sub, "_grow_point")
    if need_gs:
        sub._grow_scale = pg_gs
    if need_gp:
        sub._grow_point = pg_gp
    return need_gs, need_gp


def release_grow(queue, sub, drop_gs, drop_gp):
    """Drop the grow attributes a parent lent ``sub``, at the right time.

    ``Indicate``/``GrowArrow`` set ``_grow_scale``/``_grow_point`` on the
    animated mobject and ``_send_impl`` lends them to each submobject for the
    duration of one ``_send`` call.  With a paint queue open that call only
    *records* what the subtree will paint -- the sender runs later, in
    ``_PaintQueue.flush`` -- so dropping them immediately made the queued paint
    miss the grow entirely: every 3D frame (the queue is always open there)
    and every 2D frame whose scene uses a ``z_index`` drew the mobject at full
    size, in the middle of its own animation.

    With no queue the paint already happened, so drop right away.
    """
    if not (drop_gs or drop_gp):
        return
    if queue is None:
        if drop_gs:
            sub.__dict__.pop('_grow_scale', None)
        if drop_gp:
            sub.__dict__.pop('_grow_point', None)
        return
    queue.cleanup.append((sub, drop_gs, drop_gp))


def release_split(mob):
    """Undo the per-child progress stamps a container's split left behind.

    While a container's own ``_vulkan_progress`` is below 1.0 its sender
    stamps a slice of that progress onto each child -- a lagged ``Create``
    draws child *i* over ``[i, i + 1)`` -- so the leaf sender windowing the
    child's stroke draws the right slice.  Nothing ever cleared those stamps,
    so once the container finished, the split stopped updating them and every
    later frame re-painted the *last* child at its leftover fraction: the
    final square of ``Create(VGroup(n))`` stayed ``n * 0.27%`` short of its
    outline (8% at n = 30) and a ``Write`` never closed its last letter.

    Called where CE calls ``Animation.finish()`` -- after the terminal state
    has been applied -- so the next frame paints the container fully.  A stamp
    is dropped only while it still holds the value the split wrote; anything
    an animation wrote in between (an ``Uncreate`` of one child in the same
    ``play()``, say) is left alone.
    """
    if mob is None:
        return
    try:
        family = mob.get_family()
    except Exception:
        return
    # The lag ratio ``Create``/``Uncreate`` stamped for this split is only
    # meaningful while that animation runs; clear it or a later animation on
    # the same container would inherit the stale split.
    d0 = getattr(mob, '__dict__', None)
    if d0 is not None:
        d0.pop('_vulkan_lag_ratio', None)
    for sub in family:
        d = getattr(sub, '__dict__', None)
        if d is None or '_vsplit_progress' not in d:
            continue
        stamp = d.pop('_vsplit_progress')
        if d.get('_vulkan_progress', None) == stamp:
            d.pop('_vulkan_progress', None)


def release_flash_window(mob):
    """Clear the path-window a finished ``ShowPassingFlash`` parked behind.

    The flash writers (RTM's own ``ShowPassingFlash.interpolate`` and the
    manim bridge ``render_hooks._write_passing_flash``) tag the mobject with a
    ``_vulkan_progress_lower/upper`` sweep window so the leaf sender shows only
    the passing segment.  ``finish()`` leaves that window at its terminal
    ``(1.0, 1.0)`` -- an EMPTY window -- and nothing ever cleared it, so any
    later frame that re-painted the same mobject drew it invisible (a flashed
    arc or word that re-entered a scene vanished; ``point_path_bounds`` kept
    answering ``(1.0, 1.0)`` forever).  CE's flash restores the full path on
    finish, so a flashed mobject re-added later is drawn whole.

    Called where CE calls ``Animation.finish()``/``clean_up_from_scene()`` --
    next to ``release_split`` -- so the frames of the *next* play see the full
    geometry.  Only the flash's two window attrs are dropped; a live
    ``Create``/``Uncreate`` sweep (a single ``_vulkan_progress``) is untouched.
    """
    if mob is None:
        return
    try:
        family = mob.get_family()
    except Exception:
        return
    for sub in family:
        d = getattr(sub, '__dict__', None)
        if d is None:
            continue
        d.pop('_vulkan_progress_lower', None)
        d.pop('_vulkan_progress_upper', None)


def scan_z_index(roots):
    """Does any family member carry a non-zero ``z_index``?

    CE stable-sorts the flattened family by ``z_index`` on every frame
    (``Camera.get_mobjects_to_display``), so any non-zero value reorders the
    scene -- including across roots, and ``manim/mobject/graph.py`` hard-codes
    ``z_index=-1`` on every Graph edge.  Scenes that use none of it keep the
    document-order paint path untouched.
    """
    for root in roots:
        stack = [root]
        while stack:
            mob = stack.pop()
            if getattr(mob, "z_index", 0):
                return True
            subs = getattr(mob, "submobjects", None)
            if subs:
                stack.extend(reversed(subs))
    return False


def family_index(roots):
    """``id(mobject) -> position in CE's flattened family``, first wins.

    Mirrors ``extract_mobject_family_members``: walk each root in scene order,
    pre-order through its family, and keep the first occurrence of a member
    that two roots share.  The index is what turns RTM's visit order into CE's
    order for a member whose scene root is not its family root (a child listed
    on its own *before* the group that contains it: CE paints it where the
    group's family reaches it, RTM used to paint it where it listed it).
    """
    index = {}
    for root in roots:
        stack = [root]
        while stack:
            mob = stack.pop()
            index.setdefault(id(mob), len(index))
            subs = getattr(mob, "submobjects", None)
            if subs:
                stack.extend(reversed(subs))
    return index


def foreground_mobjects_of(scene):
    """The trailing CE render list entries: ``list_update(mobjects, foreground)``.

    ``CairoRenderer.update_frame`` captures ``scene.mobjects`` followed by any
    ``foreground_mobjects`` that are not in it already, so an explicitly
    foreground mobject paints last -- on top -- even if nothing ever put it in
    ``scene.mobjects``.  RTM reads the scene list only, which drops those.
    """
    fg = getattr(scene, "foreground_mobjects", None) or ()
    if not fg:
        return ()
    known = {id(root) for root in scene.mobjects}
    return tuple(m for m in fg if id(m) not in known)


def foreground_to_front(scene):
    """Re-apply CE's ``Scene.add`` rule: ``foreground_mobjects`` end up last.

    ``Scene.add`` rebuilds the list as ``[*new, *self.foreground_mobjects]``
    every time it runs, so a foreground mobject is dragged back in front of
    whatever was just added.  ``play`` appends the animated mobjects itself
    (it does not go through ``Scene.add``), which used to leave a foreground
    overlay behind the mobject it was supposed to cover.
    """
    fg = getattr(scene, "foreground_mobjects", None) or ()
    if not fg:
        return
    fg_ids = {id(m) for m in fg}
    scene.mobjects = ([m for m in scene.mobjects if id(m) not in fg_ids]
                      + list(fg))


def unit_z_index(mob):
    """The ``z_index`` CE paints ``mob``'s subtree at.

    A container that paints none of its own pixels has no position in CE's
    sort -- only its point-bearing members do -- so it takes the first of
    those, which is also where its own paint starts.
    """
    z = getattr(mob, "z_index", None)
    if z:
        return float(z)
    try:
        members = mob.family_members_with_points()
    except Exception:
        members = ()
    for sub in members:
        sz = getattr(sub, "z_index", 0)
        if sz:
            return float(sz)
    return float(z or 0.0)


def split_mixed_z(mob):
    """Does CE sort this ``_paint_as_unit`` subtree's members apart by z?

    A non-``VGroup`` parent that carries points of its own and paints its
    children in the SAME unit (a ``DiGraph`` edge: ``Line z=-1`` with an
    ``ArrowTriangleFilledTip`` child at ``z=0``) is only CE-correct while the
    whole subtree agrees on ``z_index``.  CE flattens the family and
    stable-sorts every member by its OWN ``z_index``, so a tip that disagrees
    lands in the ``z=0`` block -- but one unit paints it early, with the
    ``z=-1`` edge, and any ``z=0`` vertex it overlaps then covers it (the
    arrowhead sinks under the dot it points at).  True when any point-bearing
    member's ``z_index`` differs from the unit's, so the caller walks the
    subtree and each member reaches the paint queue at its own z.
    """
    unit_z = unit_z_index(mob)
    try:
        members = mob.family_members_with_points()
    except Exception:
        return False
    for sub in members:
        if float(getattr(sub, "z_index", 0) or 0) != unit_z:
            return True
    return False


def split_mixed_depth(mob, viewport):
    """Does CE sort this ``_paint_as_unit`` subtree's members apart by *depth*?

    ``ThreeDCamera.get_mobjects_to_display`` flattens the family and
    stable-sorts every member by ITS OWN camera-space depth, so a container
    and its children only paint as one block while they all score the same
    key.  When they do not, CE interleaves the other roots between them.

    Measured on ThreeDPrimitives: ``ThreeDAxes``' ``x_axis`` is a ``NumberLine``
    (a non-``VGroup`` container that carries points, so ``_paint_as_unit`` kept
    it whole).  Its own key is its centre -- the origin, 0.0 -- while its 33
    cells run from -2.6035 to +2.4820, spread across CE indices 10..742 of 906.
    Pinning all 33 to key 0.0 put the axis on top of the sphere and cylinder
    (both entirely *behind* key 0, so RTM painted it after them) and under the
    prism and torus (both entirely *in front*, so the x-axis arrow tip at
    2.4820 came out behind the torus where CE leaves it on top).  The tick
    spans measure it: over the sphere CE shows 33 white line pixels, RTM 185;
    over the torus CE 36, RTM 0.

    Only meaningful under a rotated 3D viewport: outside one every key is
    ``inf`` and no two members can disagree, so 2D scenes keep their existing
    whole-unit painting untouched.  True when any point-bearing member's depth
    key differs from the unit's, so the caller walks the subtree and each cell
    reaches the paint queue at its own depth.
    """
    if viewport is None or getattr(viewport, "rotation", None) is None:
        return False
    unit_key = depth_key(mob, viewport)
    try:
        members = mob.family_members_with_points()
    except Exception:
        return False
    for sub in members:
        if sub is mob:
            continue
        if depth_key(sub, viewport) != unit_key:
            return True
    return False


def depth_order(items):
    """``(original_index, mobject)`` pairs in manim's ThreeDCamera paint order.

    Returns the input untouched (original order) outside a rotated 3D viewport,
    so 2D scenes keep painting exactly as before.  The original index travels
    with each mobject because callers still need it: camera-rasterised images
    index into the scene's mobject list, and the VGroup progress split keys the
    partial reveal off the family position, not the paint position.

    Under a 3D camera the siblings are ordered the way CE orders them *within*
    one queued unit -- depth first, ``z_index`` second, position third -- which
    is CE's own precedence: ``ThreeDCamera`` stable-sorts the list that
    ``Camera`` already sorted by ``z_index``.

    Measured on ThreeDLightSourcePosition: a ``Sphere`` builds its cells
    back-hemisphere-first, so RTM painted the unlit back cells over the lit
    front ones -- top-half luma 161 (CE) against 88 (RTM), a hard seam where
    the painter's order flips, while the shading maths itself was identical.
    """
    try:
        from real_time_manim.camera_state import get_viewport
        viewport = get_viewport()
    except Exception:
        viewport = None
    if viewport is None or getattr(viewport, "rotation", None) is None:
        return list(enumerate(items))
    return sorted(enumerate(items),
                  key=lambda pair: (depth_key(pair[1], viewport),
                                   float(getattr(pair[1], "z_index", 0) or 0),
                                   pair[0]))


def native_dll_is_live(dll):
    """True when ``dll`` is the real native loader, not a stand-in.

    ``Vulkan_Tick`` answers 0 for "the window is gone (WM_QUIT)", but a stub
    DLL -- the ``Recorder`` the tests hand to ``window.dll`` -- answers 0 for
    *every* call it does not know.  A play that stopped on a bare
    ``if not tick()`` therefore returned before its very first frame and
    submitted no geometry at all (``AnimationGroup(Create)`` drew nothing).
    ``ctypes.CDLL`` is exactly what ``MLWindow.__init__`` loads, and a Python
    stand-in is never an instance of it.
    """
    return isinstance(dll, ctypes.CDLL)
