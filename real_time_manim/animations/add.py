# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, set_anim_opacity


class Add(Animation):
    def __init__(self, *mobjects, run_time=0.0, **kwargs):
        self.mobjects = list(mobjects)
        super().__init__(mobjects[0] if mobjects else None, run_time=run_time, **kwargs)

    def interpolate(self, t):
        elapsed = t - self.start_time
        if elapsed >= 0:
            for mob in self.mobjects:
                set_anim_opacity(mob, 1.0)

    def get_all_mobjects(self):
        return list(self.mobjects)
