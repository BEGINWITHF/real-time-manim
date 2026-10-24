# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
from real_time_manim.animations.animation_group import AnimationGroup
from real_time_manim.rate_functions import _linear, _smooth
import numpy as np


def _is_scene_root(scene, mob):
    """Is ``mob`` one of the scene's TOP-LEVEL roots?

    ``Scene.mobjects`` holds roots only; a mobject that is merely a submobject
    of a root is reached through its parent.  Clean-up code has to tell the two
    apart (only a root may be removed/absorbed here).
    """
    if mob is None:
        return False
    try:
        return mob in scene.mobjects
    except Exception:
        return False


class FadeTransform(Animation):
    def __init__(self, mobject, target_mobject, stretch=True, dim_to_match=1, run_time=1.0, **kwargs):
        self.target_mobject = target_mobject
        self.to_add_on_completion = target_mobject
        self.stretch = stretch
        self.dim_to_match = dim_to_match
        self._source_start_pos = None
        self._target_start_pos = None
        self._source_start = None
        try:
            self._ghost = target_mobject.copy()
            self._ghost._transforming = True
        except Exception:
            self._ghost = None
        super().__init__(mobject, run_time=run_time, **kwargs)

    def _park_opacity(self, mob, value):
        """Park ``value`` as ``mob``'s animated opacity.

        Hook mirroring ``FadeOut._park_opacity``: the paint pipeline walks
        the SCENE tree, so a subclass whose mobject is a detached wrapper
        must also reach the nodes the tree actually visits.
        """
        set_anim_opacity(mob, value)

    def begin(self, t):
        super().begin(t)
        self.mobject.save_state()
        self.target_mobject.save_state()
        self._source_start_pos = self.mobject.get_center().copy()
        self._target_start_pos = self.target_mobject.get_center().copy()
        if self._ghost is not None:
            self._ghost.move_to(self._source_start_pos)
            if self.stretch:
                sx = self.mobject.width / self._ghost.width if self._ghost.width > 0 else 1.0
                sy = self.mobject.height / self._ghost.height if self._ghost.height > 0 else 1.0
                self._ghost.stretch(sx, 0)
                self._ghost.stretch(sy, 1)
            else:
                self._ghost.rescale_to_fit(
                    self.mobject.length_over_dim(self.dim_to_match),
                    self.dim_to_match,
                    stretch=False,
                )
            self._ghost.move_to(self._source_start_pos)
            self._source_copy = self._ghost.copy()
            self._target_copy = self.target_mobject.copy()
            self._source_copy.align_data(self._target_copy)
            # CE's FadeTransform IS a Transform, so the OUTGOING piece morphs
            # into the target while it fades: at every instant the fading source
            # and the fading-in ghost are the SAME shape, which is why CE's
            # crossfade reads as one letter.  RTM morphed only the ghost and
            # faded the source in place, so the two shapes differed and the
            # outgoing letter ghosted over the incoming one -- the wiki's
            # key_map demo read "ħat" instead of a clean crossfade into "hat".
            # Snapshot the source's own start (aligned like the ghost's) so
            # `interpolate` can morph it too.
            try:
                self._source_start = self.mobject.copy()
                self._source_start.align_data(self._target_copy)
                self.mobject.align_data(self._target_copy)
            except Exception:
                self._source_start = None
            set_anim_opacity(self._ghost, 0.0)
        self._park_opacity(self.mobject, 1.0)
        set_anim_opacity(self.target_mobject, 0.0)

    def interpolate(self, t):
        if getattr(self, '_use_alpha', False):
            # Driven by an AnimationGroup which already applied its rate_func to
            # the overall progress. Using linear alpha here avoids double-easing
            # (group smooth + this FadeTransform's own smooth).
            alpha = max(0.0, min(1.0, t))
        else:
            alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
            alpha = max(0.0, min(1.0, alpha))
            if self.reverse_rate_function:
                alpha = 1.0 - alpha
            alpha = self.rate_func(alpha)
        cur_pos = (
            self._source_start_pos * (1.0 - alpha)
            + self._target_start_pos * alpha
        )
        if self._source_start is not None:
            # Morph the source toward the target the way CE's Transform does, so
            # the outgoing and the incoming shape coincide at every alpha (see
            # begin()).  `_source_start` is aligned to `_target_copy`, and so is
            # `self.mobject`, so the three families zip member for member.
            try:
                for m, s, tgt in zip(
                    self.mobject.family_members_with_points(),
                    self._source_start.family_members_with_points(),
                    self._target_copy.family_members_with_points(),
                ):
                    m.interpolate(s, tgt, alpha)
            except Exception:
                self.mobject.move_to(cur_pos)
        else:
            self.mobject.move_to(cur_pos)
        if self._ghost is not None:
            # Morph the POINTED members of the whole family level by level,
            # the way Transform.interpolate_mobject does.  Interpolating only
            # the direct children morphed nothing whenever the points live
            # one level deeper (a MathTexPart carries no points of its own;
            # they sit on its glyph child): VMobject.interpolate is not
            # recursive, so the ghost kept the source's stretched bounding
            # box -- a bright square -- for the entire crossfade.  The three
            # families are structurally identical (ghost -> source_copy are
            # copies of each other, and begin() aligned source_copy with
            # target_copy), so the zip pairs the same member in each.
            for gs, ss, ts in zip(
                self._ghost.family_members_with_points(),
                self._source_copy.family_members_with_points(),
                self._target_copy.family_members_with_points(),
            ):
                gs.interpolate(ss, ts, alpha)
            self._ghost.move_to(cur_pos)
            if alpha >= 1.0:
                self._ghost._transforming = False
                for sub in self._ghost.get_family():
                    sub._transforming = False
            set_anim_opacity(self._ghost, alpha)
        self._park_opacity(self.mobject, max(0.0, 1.0 - alpha))

    def finish(self):
        super().finish()
        self.mobject.move_to(self._target_start_pos)
        self._park_opacity(self.mobject, 0.0)
        set_anim_opacity(self.target_mobject, 1.0)
        if self._ghost is not None:
            set_anim_opacity(self._ghost, 0.0)
        try:
            self.mobject.restore()
            self.target_mobject.restore()
        except Exception:
            pass

    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        if self.mobject in scene.mobjects:
            scene.remove(self.mobject)
        if self._ghost is not None and self._ghost in scene.mobjects:
            scene.remove(self._ghost)
        if self.target_mobject not in scene.mobjects:
            scene.add(self.target_mobject)
        set_anim_opacity(self.target_mobject, 1.0)

    def get_all_mobjects(self):
        mobs = [self.mobject, self.target_mobject]
        if self._ghost is not None:
            mobs.append(self._ghost)
        return mobs


class FadeTransformPieces(AnimationGroup):
    """FadeTransformPieces — per-piece, index-wise crossfade.

    Each source submobject cross-fades into its matching target submobject
    (src[i]→tgt[i]) INDEPENDENTLY, which differs from the whole-group FadeTransform
    (that pairs submobjects crosswise). Each piece gets its own FadeTransform.
    """

    def __init__(self, mobject, target_mobject, **kwargs):
        self.mobject = mobject
        self.target_mobject = target_mobject
        self.to_add_on_completion = target_mobject
        try:
            mobject.align_submobjects(target_mobject)
        except Exception:
            pass
        # manim's own ``FadeTransformPieces`` is a SINGLE ``FadeTransform``, so
        # ``rate_func`` is applied exactly once.  Ours is an ``AnimationGroup``
        # of per-piece ``FadeTransform``s and every child eases itself, which
        # makes the group the only place a play-level ``rate_func=`` can land
        # without being applied twice: leaving the group at AnimationGroup's
        # ``linear`` default meant ``win.play(..., rate_func=smooth)`` put a
        # SECOND smooth on top of each child's -- measured on the wiki
        # ``03-动画/变换/05-淡出淡入式变换`` source-opacity curve at the halfway
        # frame, RTM 0.976 vs CE 0.846 and at 2/3 RTM 0.024 vs CE 0.154: the
        # crossfade visibly lagged and then rushed ("速率错误").  ``_smooth`` is
        # literally manim's ``smooth`` (same sigmoid), so the default matches a
        # lone ``FadeTransform``'s own default.
        #
        # ``stretch`` / ``dim_to_match`` belong to the PIECES: they used to
        # ride along in ``**kwargs`` to ``AnimationGroup.__init__``, which
        # swallows them into ``Animation.__init__(**kwargs)``, so a
        # ``FadeTransformPieces(a, b, stretch=False, dim_to_match=0)`` built
        # children at their defaults and the documented parameters did nothing.
        stretch = kwargs.get("stretch", True)
        dim_to_match = kwargs.get("dim_to_match", 1)
        self.stretch = stretch
        self.dim_to_match = dim_to_match
        kwargs.setdefault("rate_func", _smooth)
        pairs = list(zip(mobject.submobjects, target_mobject.submobjects))
        # children pass the group's progress through un-eased (see above)
        anims = [FadeTransform(sm, tm, stretch=stretch, dim_to_match=dim_to_match,
                               rate_func=_linear)
                 for sm, tm in pairs]
        super().__init__(*anims, **kwargs)
        # ``AnimationGroup`` chains to ``Animation.__init__(mobject=None)``,
        # which clobbers the source reference stored ABOVE (docs/BUG_REPORT.md
        # H3: ``FadeTransformPieces.mobject is None``, so the source group was
        # missing from ``get_all_mobjects()`` and presentation could not find
        # it).  Restore it after super() so it survives.
        self.mobject = mobject

    def clean_up_from_scene(self, scene):
        """Never leave the crossfade's copies behind.

        Report: wiki ``03-动画/变换/05-淡出淡入式变换`` -- after a
        ``FadeTransformPieces`` finished a copy of the target stayed on screen
        and a later ``FadeOut`` could not remove it (the red circle + yellow
        triangle at the clip's end).  Two copies are produced per piece:

        * ``_ghost`` -- ``target.copy()``, presented as an extra scene ROOT by
          ``PlayMixin._present_detached_animated`` (RTM paints only the scene
          tree).  Its final frame parks it at opacity 1, so a ghost that is not
          removed reads as "a copy of the target" that ``FadeOut(target)``
          cannot touch;
        * the piece's ``target_mobject`` -- the child clean-up parks those as
          separate roots, so the target GROUP itself never enters the scene and
          its pieces cannot be dimmed together.

        Everything is done here as well as through ``super()`` so this class
        does not depend on ``AnimationGroup.clean_up_from_scene`` recursing
        into its children (that lives in another module).
        """
        animations = list(getattr(self, "animations", []) or [])
        for sub in animations:
            ghost = getattr(sub, "_ghost", None)
            if _is_scene_root(scene, ghost):
                scene.remove(ghost)

        # Per-piece clean-up: source/ghost removal + target presentation.
        super().clean_up_from_scene(scene)

        target = getattr(self, "target_mobject", None)
        source = getattr(self, "mobject", None)

        # Regroup the piece targets under the ONE target group: they ARE its
        # own submobjects, and as separate roots paint multiplies their alpha
        # from themselves, so a later FadeOut(target) never dimmed them.
        for sub in animations:
            tm = getattr(sub, "target_mobject", None)
            if tm is None:
                continue
            set_anim_opacity(tm, 1.0)
            if (tm is not target
                    and any(tm is sm for sm in getattr(target, "submobjects", ()))
                    and _is_scene_root(scene, tm)):
                scene.remove(tm)

        # The transformed source is done and CE removes it from the scene.
        # RTM used to keep it as a transparent ROOT ("only the group's own
        # alpha paints it"), which leaked one dead root per FadeTransformPieces
        # -- `scene.mobjects` ended up as `[source, target]` where CE has just
        # `[target]` (audit state_probes: fadetransformpieces_cleanup).
        if _is_scene_root(scene, source):
            set_anim_opacity(source, 0.0)
            try:
                scene.remove(source)
            except Exception:
                pass

        # The whole target enters as ONE root, exactly like CE's
        # ``scene.add(to_add_on_completion)`` -- Scene.add absorbs any of its
        # family members that are still roots.
        if target is not None:
            if not _is_scene_root(scene, target):
                scene.add(target)
            set_anim_opacity(target, 1.0)

    def get_all_mobjects(self):
        mobs = [self.mobject, self.target_mobject]
        for sub in getattr(self, 'animations', []):
            mobs.append(sub.mobject)
            if getattr(sub, 'target_mobject', None) is not None:
                mobs.append(sub.target_mobject)
        return mobs
