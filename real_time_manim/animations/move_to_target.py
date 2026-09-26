from real_time_manim.animations.transform import Transform


class MoveToTarget(Transform):
    def __init__(self, mobject, **kwargs):
        target = mobject.target if hasattr(mobject, 'target') else mobject.copy()
        super().__init__(mobject, target, **kwargs)
