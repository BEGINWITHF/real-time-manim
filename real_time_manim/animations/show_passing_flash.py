# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation


class ShowPassingFlash(Animation):
    def __init__(self, mobject, time_width=0.1, run_time=1.0, remover=True, **kwargs):
        # ``remover`` used to be hard-wired to True: the sweep always took the
        # mobject out of the scene when it ended, while CE lets it be configured
        # (``ShowPassingFlash(..., remover=False)`` leaves the full stroke in
        # place -- the behaviour the wiki could not demo, 01b-扫光与波纹).
        # Default stays True, so existing renders are unchanged.
        self.time_width = time_width
        super().__init__(mobject, run_time=run_time, remover=remover, **kwargs)

    def begin(self, t):
        super().begin(t)
        self.mobject._vulkan_progress = 0.0

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        tw = self.time_width
        upper = (1 + tw) * alpha
        lower = upper - tw
        upper = min(upper, 1.0)
        lower = max(lower, 0.0)
        self.mobject._vulkan_progress_lower = lower
        self.mobject._vulkan_progress_upper = upper

    def _restore_full_stroke(self):
        """CE puts the WHOLE path back once the sweep is over.

        ``interpolate`` parks the sliding window on the mobject and ``begin``
        left ``_vulkan_progress`` at ``0.0``; with the window still open the
        senders answer ``point_path_bounds == (1.0, 1.0)`` (an empty range) and
        the mobject paints nothing -- so a ``remover=False`` flash would end
        with the object invisible instead of "scanned and whole" (CE calls
        ``pointwise_become_partial(start, 0, 1)`` in its clean-up).
        Drop the two window attrs and mark the stroke complete; the play path's
        ``release_flash_window`` does the same and is idempotent about it.
        """
        mob = getattr(self, "mobject", None)
        if mob is None:
            return
        try:
            family = mob.get_family()
        except Exception:
            family = [mob]
        for sub in family:
            d = getattr(sub, "__dict__", None)
            if d is None:
                continue
            d.pop("_vulkan_progress_lower", None)
            d.pop("_vulkan_progress_upper", None)
        mob._vulkan_progress = 1.0

    def finish(self):
        super().finish()
        self._restore_full_stroke()

    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        self._restore_full_stroke()
        if self.remover and self.mobject in scene.mobjects:
            scene.remove(self.mobject)
