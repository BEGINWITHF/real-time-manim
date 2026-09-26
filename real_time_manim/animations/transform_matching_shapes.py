# This might not cause a bug or issue, check for other place first --TT Noted
import numpy as np
from real_time_manim.animations.transform_matching_abstract_base import TransformMatchingAbstractBase


class TransformMatchingShapes(TransformMatchingAbstractBase):
    @staticmethod
    def get_mobject_parts(mobject):
        if hasattr(mobject, 'family_members_with_points'):
            return mobject.family_members_with_points()
        if hasattr(mobject, 'submobjects') and mobject.submobjects:
            return list(mobject.submobjects)
        return [mobject]

    @staticmethod
    def get_mobject_key(mobject):
        mobject.save_state()
        mobject.center()
        mobject.set(height=1)
        rounded_points = np.round(mobject.points, 3) + 0.0
        result = hash(rounded_points.tobytes())
        mobject.restore()
        return result
