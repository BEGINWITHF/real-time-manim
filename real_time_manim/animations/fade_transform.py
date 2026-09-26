# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
from real_time_manim.animations.animation_group import AnimationGroup
import numpy as np


class FadeTransform(Animation):
    def __init__(self, mobject, target_mobject, stretch=True, dim_to_match=1, run_time=1.0, **kwargs):
        self.target_mobject = target_mobject
        self.to_add_on_completion = target_mobject
        self.stretch = stretch
        self.dim_to_match = dim_to_match
        self._source_start_pos = None
        self._target_start_pos = None
        try:
            self._ghost = target_mobject.copy()
            self._ghost._transforming = True
        except Exception:
            self._ghost = None
        super().__init__(mobject, run_time=run_time, **kwargs)

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
            set_anim_opacity(self._ghost, 0.0)
        set_anim_opacity(self.mobject, 1.0)
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
        self.mobject.move_to(cur_pos)
        if self._ghost is not None:
            # VGroup.interpolate() doesn't propagate to submobjects, so
            # interpolate each child individually for proper shape morphing.
            if hasattr(self._ghost, 'submobjects') and self._ghost.submobjects:
                for gs, ss, ts in zip(
                    self._ghost.submobjects,
                    self._source_copy.submobjects,
                    self._target_copy.submobjects,
                ):
                    gs.interpolate(ss, ts, alpha)
            else:
                self._ghost.interpolate(self._source_copy, self._target_copy, alpha)
            self._ghost.move_to(cur_pos)
            if alpha >= 1.0:
                self._ghost._transforming = False
                for sub in self._ghost.submobjects:
                    sub._transforming = False
            set_anim_opacity(self._ghost, alpha)
        set_anim_opacity(self.mobject, max(0.0, 1.0 - alpha))

    def finish(self):
        super().finish()
        self.mobject.move_to(self._target_start_pos)
        set_anim_opacity(self.mobject, 0.0)
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
        pairs = list(zip(mobject.submobjects, target_mobject.submobjects))
        anims = [FadeTransform(sm, tm) for sm, tm in pairs]
        super().__init__(*anims, **kwargs)

    def get_all_mobjects(self):
        mobs = [self.mobject, self.target_mobject]
        for sub in getattr(self, 'animations', []):
            mobs.append(sub.mobject)
            if getattr(sub, 'target_mobject', None) is not None:
                mobs.append(sub.target_mobject)
        return mobs
