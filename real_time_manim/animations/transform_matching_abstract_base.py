from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np
from manim import VGroup
from real_time_manim.animations.transform import Transform
from real_time_manim.animations.fade_out import FadeOut
from real_time_manim.animations.fade_in import FadeIn
from real_time_manim.animations.fade_transform import FadeTransform


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
                key_mapped_source.add(source_map[key1])
                key_mapped_target.add(target_map[key2])
                source_map.pop(key1, None)
                target_map.pop(key2, None)
        if len(key_mapped_source.submobjects) > 0:
            self._anims.append(
                FadeTransform(key_mapped_source, key_mapped_target, run_time=self.run_time)
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
            fade_source = VGroup(*fade_source_parts)
            fade_target = VGroup(*fade_target_parts)
            self._anims.append(
                FadeTransform(fade_source, fade_target, run_time=self.run_time)
            )
        else:
            # Fade out mismatched source parts, fade in mismatched target parts.
            # Use VGroup wrappers (like original manim) so the scene.add at line
            # 1011-1012 picks up the entire Group, not just the first part.
            fade_source = VGroup(*fade_source_parts)
            fade_target_copy = VGroup(*fade_target_parts).copy()
            self._anims.append(
                FadeOut(fade_source, shift=None,
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
