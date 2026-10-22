from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np
from manim import VGroup
from real_time_manim.animations.transform import Transform
from real_time_manim.animations.fade_out import FadeOut
from real_time_manim.animations.fade_in import FadeIn
from real_time_manim.animations.fade_transform import FadeTransform, FadeTransformPieces


class _WrappedFadeOut(FadeOut):
    """FadeOut of a DETACHED wrapper group (see TransformMatchingAbstractBase).

    The paint pipeline walks the SCENE tree, which reaches the wrapped parts
    through their real parents (eq1, ...), never through this wrapper -- so
    opacity parked only on the wrapper never applied and the unmatched source
    parts stayed fully opaque for the whole fade.  Park on the wrapper AND
    its direct children: the children are the nodes the tree visits, and
    paint multiplies parent x child alpha, so parking at exactly one visited
    level gives the right result.  (Parking on the whole family would square
    it: part alpha x glyph alpha.)
    """

    def _park_opacity(self, mob, value):
        super()._park_opacity(mob, value)
        for sm in getattr(mob, "submobjects", ()):
            set_anim_opacity(sm, value)


class TransformMatchingAbstractBase(Animation):
    def __init__(
        self,
        mobject,
        target_mobject,
        transform_mismatches=False,
        fade_transform_mismatches=False,
        key_map=None,
        run_time=1.0,
        **kwargs,
    ):
        self.target_mobject = target_mobject
        self.transform_mismatches = transform_mismatches
        self.fade_transform_mismatches = fade_transform_mismatches
        self.key_map = key_map or {}
        self._transform_kwargs = kwargs
        self._anims = []
        self._scene = None
        super().__init__(mobject, run_time=run_time, **kwargs)

    def get_shape_map(self, mobject):
        shape_map = {}
        for sm in self.get_mobject_parts(mobject):
            key = self.get_mobject_key(sm)
            if key not in shape_map:
                shape_map[key] = VGroup()
            shape_map[key].add(sm)
        return shape_map

    def begin(self, t):
        super().begin(t)
        if hasattr(self.mobject, '_letter_alphas'):
            self.mobject._letter_alphas = None
        if hasattr(self.target_mobject, '_letter_alphas'):
            self.target_mobject._letter_alphas = None

        source_map = self.get_shape_map(self.mobject)
        target_map = self.get_shape_map(self.target_mobject)

        transform_source = VGroup()
        transform_target = VGroup()
        for key in set(source_map).intersection(target_map):
            transform_source.add(source_map[key])
            transform_target.add(target_map[key])
        self._anims.append(
            Transform(transform_source, transform_target, run_time=self.run_time,
                      **self._transform_kwargs)
        )

        key_mapped_source = VGroup()
        key_mapped_target = VGroup()
        for key1, key2 in self.key_map.items():
            if key1 in source_map and key2 in target_map:
                # Flatten to wrapper -> parts (same as the fade_source branch
                # below): the parts are the nodes the paint walk visits, and
                # _WrappedFadeOut parks opacity on the wrapper's direct
                # children.  Adding the shape-map GROUP instead would nest one
                # level deeper, park on that detached group, and leave the
                # real part -- reached through its real parent -- untouched.
                key_mapped_source.add(*source_map[key1].submobjects)
                key_mapped_target.add(*target_map[key2].submobjects)
                source_map.pop(key1, None)
                target_map.pop(key2, None)
        if len(key_mapped_source.submobjects) > 0:
            # CE pairs these with FadeTransformPieces: each part fades out where
            # it stands while a COPY of its partner fades in at the partner's
            # place, AND the source part is stretched toward the partner's box
            # on the way (FadeTransform is a Transform with a fade).  RTM's
            # hand-rolled version below used _WrappedFadeOut + FadeIn, which
            # moves the part to the partner's centre but never rescales it, so
            # the outgoing "c" stayed its own size on top of the incoming "h"
            # and read as "not fading out" (measured on the wiki's key_map demo:
            # 16 % more ink in the first-letter box through the whole crossfade
            # than CE; the code comment claimed the per-piece crossfade matched
            # CE, but it only matched the fade, not the stretch).
            self._anims.append(
                FadeTransformPieces(key_mapped_source, key_mapped_target,
                                    run_time=self.run_time)
            )

        fade_source_parts = []
        fade_target_parts = []
        for key in set(source_map).difference(target_map):
            fade_source_parts.extend(source_map[key].submobjects)
        for key in set(target_map).difference(source_map):
            fade_target_parts.extend(target_map[key].submobjects)

        if self.transform_mismatches:
            fade_source = VGroup(*fade_source_parts)
            fade_target = VGroup(*fade_target_parts)
            self._anims.append(
                Transform(fade_source, fade_target, run_time=self.run_time,
                          replace_mobject_with_target_in_scene=True,
                          **self._transform_kwargs)
            )
        elif self.fade_transform_mismatches:
            # CE pairs the mismatched parts with ``FadeTransformPieces`` -- one
            # per-piece FadeTransform (source part fades/slides into its
            # partner while a copy of the partner fades/slides in).  RTM used a
            # single whole-group ``_WrappedFadeTransform``, whose one ghost is
            # stretched to the SOURCE GROUP's bounding box, so mismatched parts
            # of different sizes were crossfaded through a wrongly sized ghost
            # -- the same disease the key_map branch above had (wiki
            # 03-动画/匹配变换/01-匹配变换, "异形用 FadeTransformPieces").
            fade_source = VGroup(*fade_source_parts)
            fade_target = VGroup(*fade_target_parts)
            self._anims.append(
                FadeTransformPieces(fade_source, fade_target,
                                    run_time=self.run_time)
            )
        else:
            # Fade out mismatched source parts, fade in mismatched target parts.
            # Use VGroup wrappers (like original manim) so the scene.add at line
            # 1011-1012 picks up the entire Group, not just the first part.
            fade_source = VGroup(*fade_source_parts)
            fade_target_copy = VGroup(*fade_target_parts).copy()
            self._anims.append(
                _WrappedFadeOut(fade_source, shift=None,
                                target_position=fade_target_copy,
                                run_time=self.run_time)
            )
            self._anims.append(
                FadeIn(fade_target_copy, shift=None,
                       target_position=fade_target_copy,
                       run_time=self.run_time)
            )
            self._fade_target_copy = fade_target_copy

        for anim in self._anims:
            anim.begin(t)

    def interpolate(self, t):
        for anim in self._anims:
            anim.interpolate(t)

    def finish(self):
        super().finish()
        for anim in self._anims:
            anim.finish()

    def get_all_mobjects(self):
        mobs = [self.mobject]
        ftc = getattr(self, '_fade_target_copy', None)
        if ftc is not None:
            mobs.append(ftc)
        return mobs

    def clean_up_from_scene(self, scene):
        # CE resets every sub-animation before the source leaves the scene
        # ("Interpolate all animations back to 0 to ensure source mobjects
        # remain unchanged"): Transform.interpolate(0) puts the moved parts
        # back and the fades restore their opacity, so a source the caller
        # still holds a reference to is pristine once it is removed.
        # Best-effort per anim -- a failed reset must not stop the removal.
        for anim in getattr(self, "_anims", []):
            try:
                anim.interpolate(0.0)
            except Exception:
                pass
        if self.mobject in scene.mobjects:
            scene.remove(self.mobject)
        ftc = getattr(self, '_fade_target_copy', None)
        if ftc is not None and ftc in scene.mobjects:
            scene.remove(ftc)
        # Remove sub-anims' transform_source/transform_target VGroups
        for sub_anim in getattr(self, '_anims', []):
            if hasattr(sub_anim, 'mobject') and sub_anim.mobject in scene.mobjects:
                scene.remove(sub_anim.mobject)
            if hasattr(sub_anim, 'target_mobject') and sub_anim.target_mobject in scene.mobjects:
                scene.remove(sub_anim.target_mobject)
            # FadeTransform's morph ghost was presented as an extra scene root
            # (see play._present_detached_animated); TMA drives its sub-anims
            # itself and never calls their clean_up_from_scene, so remove the
            # ghost here or it lingers in the tree at parked opacity 0.  Walk
            # NESTED children too: `fade_transform_mismatches=True` builds one
            # FadeTransform per pair inside a FadeTransformPieces group, so the
            # ghosts live one level down and used to survive the whole scene.
            def _remove_ghosts(node):
                ghost = getattr(node, '_ghost', None)
                if ghost is not None and ghost in scene.mobjects:
                    scene.remove(ghost)
                for child in (getattr(node, '_anims', None)
                              or getattr(node, 'animations', None) or ()):
                    _remove_ghosts(child)

            _remove_ghosts(sub_anim)
        if self.target_mobject not in scene.mobjects:
            scene.add(self.target_mobject)
        set_anim_opacity(self.target_mobject, 1.0)
        if hasattr(self.mobject, '_transforming'):
            self.mobject._transforming = False
        if hasattr(self.target_mobject, '_transforming'):
            self.target_mobject._transforming = False

    @staticmethod
    def get_mobject_parts(mobject):
        if hasattr(mobject, 'family_members_with_points'):
            return mobject.family_members_with_points()
        if hasattr(mobject, 'submobjects') and mobject.submobjects:
            return list(mobject.submobjects)
        return [mobject]

    @staticmethod
    def get_mobject_key(mobject):
        raise NotImplementedError
