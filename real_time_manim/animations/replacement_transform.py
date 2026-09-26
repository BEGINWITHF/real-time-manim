from real_time_manim.animations.transform import Transform


class ReplacementTransform(Transform):
    def __init__(self, mobject, target_mobject, **kwargs):
        kwargs['replace_mobject_with_target_in_scene'] = True
        super().__init__(mobject, target_mobject, **kwargs)
