# Manim-CE-Vulkan-compatibility Renderer — Bug Hunt Report

**Target:** `real_time_manim/` (RTM), compared against Manim Community `0.21.0`
(`C:\Users\begin\AppData\Local\Programs\Python\Python312\Lib\site-packages\manim`).
**Scope:** timing, easing, mobject-state, resource leaks, reachable Python errors in
the reimplemented animations / `timeline.py` / `record.py` / `frames.py` pipeline.
**Method:** code reading + empirical `python -c` / temp-script probes (Manim 0.21.0,
Python 3.12, Windows). No files were modified; scratch probes were deleted.

Findings are grouped by **severity**, and each is tagged **HIGH / MEDIUM / LOW**
confidence. "Confirmed" = reproduced with a probe or exact CE-source comparison.

---

## Severity: HIGH

### H1. `AnimationGroup(..., run_time=3)` raises `TypeError` — `run_time` passed twice
- **Confidence:** HIGH (confirmed) · **File:** `real_time_manim/animations/animation_group.py:36`

```python
kwargs.setdefault('rate_func', _linear)
super().__init__(run_time=total, **kwargs)      # <-- if caller passed run_time, it is in kwargs too
```

`AnimationGroup` computes `total` from children and forwards `run_time=total` **and**
`**kwargs`. A caller-supplied `run_time=3` is still inside `kwargs`, so
`Animation.__init__(mobject, run_time=total, run_time=3)` →
`TypeError: Animation.__init__() got multiple values for keyword argument 'run_time'`.

**Trigger:** `self.play(AnimationGroup(FadeIn(a), FadeIn(b), run_time=3))`.
CE accepts it (`AnimationGroup` honours an explicit `run_time`).
**Fix:** `kwargs.pop('run_time', None)` before the `super()` call (as `Succession` already
does at `succession.py:20`).

---

### H2. `Succession` finishes the last child at alpha 0 (final state undone) + every child starts ≤1 frame late
- **Confidence:** HIGH (confirmed numerically) · **File:** `real_time_manim/animations/succession.py:45-73`

```python
if active:
    if i not in self._begun:
        ...
        a.begin(t)                 # RTM child: begin with ABSOLUTE t
        self._begun.add(i)
    ...
    a.interpolate(t)               # RTM child: interpolate ABSOLUTE t
    return
...
# fallback when elapsed >= total (end of the whole Succession):
self.animations[last_idx].begin(t)      # begin at t (=end time)
self.animations[last_idx].interpolate(t)# interpolate at same t -> alpha 0
```

Two defects:

1. **End-of-schedule fallback** (`:60-73`): when `elapsed >= run_time`, the last child is
   `begin(t)` then `interpolate(t)`. Because RTM animations derive
   `alpha = (t - start_time)/run_time` and `begin` just pinned `start_time = t`, alpha is **0**.
   Probe: a trailing `FadeIn(sq)` inside a `Succession` has opacity **0.0** at
   `t = run_time` — the mobject it was supposed to reveal is invisible.
   In CE, `Succession` at completion leaves the last sub-animation at its **final** state.
2. **Late `begin`**: a child becomes `active` only once `elapsed >= cumulative`, and is then
   `begin(t)`'d at that same `t`, so its alpha starts at 0 on the first active frame and it
   never reaches 1 within its slot (it is one frame behind CE, which begins each child at the
   slot boundary and immediately renders `alpha≈0→1` across the slot).

**Trigger:** `self.play(Succession(FadeIn(a), FadeIn(b), FadeIn(c)))` — at the final frame
`c` is invisible.
**Fix:** clamp the RTM-child fallback to `a.begin(end_of_slot - a.run_time)` and
`a.interpolate(end_of_slot)` (or track per-child start on first activation and always
`interpolate` the child's own slot end once elapsed passes it).

---

### H3. `FadeTransformPieces.mobject` is clobbered to `None` → source absent from `get_all_mobjects()`
- **Confidence:** HIGH (confirmed: `FadeTransformPieces.mobject is None`) · **File:** `real_time_manim/animations/fade_transform.py:124-134`

```python
def __init__(self, mobject, target_mobject, **kwargs):
    self.mobject = mobject
    self.target_mobject = target_mobject
    self.to_add_on_completion = target_mobject
    ...
    super().__init__(*anims, **kwargs)     # AnimationGroup.__init__ -> Animation.__init__
```

`FadeTransformPieces` subclasses RTM `AnimationGroup`, whose `super().__init__(*anims)`
chains to `Animation.__init__(mobject=None, ...)` — which **overwrites** `self.mobject`
with `None`. Verified: `anim.mobject is None`, and the source mobject is therefore missing
from `Animation.get_all_mobjects()`. Only the per-piece children keep their own references;
the group-level source is lost, breaking any consumer that reads `anim.mobject`
(the timeline's opacity/finish bookkeeping, `_ensure_animated_present`, etc.).

**Trigger:** `FadeTransformPieces(src, tgt)` then inspect `anim.mobject`.
**Fix:** restore `self.mobject = mobject` **after** `super().__init__(...)`, or override
`get_all_mobjects` to prepend the stored source (it already appends children at `:136`).

---

### H4. `Rotate.finish()` deletes the pivot but leaves the baked rotation → visible snap after `wait()`
- **Confidence:** HIGH (confirmed: post-finish render uses the ORIGINAL center) · **File:** `real_time_manim/animations/rotate.py:28-31`

```python
def finish(self):
    super().finish()
    if hasattr(self.mobject, '_rotation_about_point'):
        del self.mobject._rotation_about_point   # pivot gone
    # NOTE: self.mobject's accumulated anim rotation (set via set_anim_rotation in
    #       interpolate) is NOT reset here.
```

`interpolate` continuously sets `set_anim_rotation(mobject, start + rot_angle*alpha)`
(`rotate.py:40`) and the renderers (`vulkan_shapes.py:186/256/...`, `vulkan_bind.py:2055`)
rotate every point about `mob._rotation_about_point`. `finish()` removes the pivot but
leaves the **rotation** registered. On the very next frame (e.g. after `play(...); wait()`)
the renderer still has a non-zero anim-rotation but no pivot, so it rotates about the
mobject's **own** center instead of `about_point` → the shape visibly jumps.

Contrast: `Rotating.finish` (`rotating.py:73-85`) **bakes** the rotation into the points
about the pivot and then resets `set_anim_rotation(mobject, 0.0)` **and** deletes the pivot —
the two classes disagree.

**Trigger:** `play(Rotate(sq, PI/2, about_point=LEFT*2)); wait()` → `sq` snaps position.
**Fix:** mirror `Rotating.finish`: apply the final rotation about the pivot to the points,
then `set_anim_rotation(mobject, 0.0)` before deleting `_rotation_about_point`.

---

### H5. `ShowPassingFlash` leaves the path-window open → mobject permanently invisible in the standalone `Timeline`/`FrameServer` path
- **Confidence:** HIGH · **Files:** `animations/show_passing_flash.py:26-27`, `vulkan_bind.py:827` / `:2712`

```python
# show_passing_flash.py
self.mobject._vulkan_progress_lower = lower
self.mobject._vulkan_progress_upper = upper
# finish() only sets _vulkan_progress = 1.0; it never clears the lower/upper window.
```

The flash window is cleaned by `release_flash_window(mob)` (`vulkan_bind.py:827`), which is
called **only** inside `vulkan_bind._run_timeline` (`:2712`) — the `play()`/record path. The
standalone `Timeline` (used by `FrameServer`, `render_at`, `render_mp4`, screenshots) never
calls it. After a flash completes, `_vulkan_progress_lower/upper` stay at `(1.0, 1.0)`, so the
contour-window draws an empty range → the flashed mobject stays **invisible** for the rest of
the timeline.

**Trigger:** Build a `Timeline` with `ShowPassingFlash(mob)` then a later `FadeIn(mob)` /
any animation expecting `mob` visible; `render_at(later_t)` shows `mob` gone.
**Fix:** clear `_vulkan_progress_lower/upper` in `ShowPassingFlash.finish()` (and/or call
`release_flash_window` from `Timeline.evaluate`/`finalize` for completed entries).

---

### H6. `Timeline` never calls `finish()` / `clean_up_from_scene()` → all finish-only restorations skipped
- **Confidence:** HIGH · **File:** `real_time_manim/timeline.py` (`evaluate`/`render_at`), cf. `vulkan_bind.py:2668-2726`

`vulkan_bind._run_timeline` explicitly runs, after the last frame:
`a.finish(); a.clean_up_from_scene(scene); release_split; release_flash_window` (`:2710-2726`).
The standalone `Timeline.evaluate`/`render_at` path (`timeline.py:296-309`) only calls
`interpolate` via `evaluate_animation`; it **never** invokes `finish`/`clean_up_from_scene`.
Consequences in the seek/`FrameServer` path:
- `Transform.clean_up_from_scene` swap (source removed, target added, opacities reset) never runs.
- `Uncreate`/`ShowPassingFlash`/`Create(remover=True)` never remove their mobjects.
- `release_split` / `release_flash_window` never run → H5 above.
- `Rotate`'s finish-side pivot handling (H4) and every `_grow_*`/`_letter_alphas` cleanup is skipped.

**Trigger:** Any `Timeline`-driven render (screenshots / `render_mp4` / FrameServer scrubbing).
**Fix:** In `Timeline.evaluate`, once `t >= entry.start + run_time` for the first time, call
`anim.finish()` and `anim.clean_up_from_scene(scene)` (idempotently, guarded by `finished`).

---

## Severity: MEDIUM

### M1. `AnimationGroup` child starts ignore each child's `run_time` (lag math)
- **Confidence:** HIGH (confirmed: RTM `[0.0, 0.5]` vs CE `[0.0, 1.0]` for run_times (2,1), lag 0.5) · **File:** `animation_group.py:28-29`

```python
for i, a in enumerate(self.animations):
    a._group_start = i * lag_ratio          # index * lag_ratio
total_runs = [a._group_start + a.run_time for a in self.animations]
```

CE (`composition.py`) computes `start_i = lag_ratio * cumsum(run_times[:i])` — the offset
accumulates each **predecessor's run_time**, scaled by lag_ratio. RTM uses the raw **index**,
so with unequal run_times every child after the first starts too early.

**Trigger:** `AnimationGroup(FadeIn(a, run_time=2), FadeIn(b, run_time=1), lag_ratio=0.5)` —
CE starts `b` at 1.0 s, RTM at 0.5 s.
**Fix:** `start = lag_ratio * sum(prev.run_time for prev in animations[:i])`.

---

### M2. `Indicate(..., run_time=3)` is silently ignored
- **Confidence:** HIGH (confirmed: run_time stays 1.0) · **File:** `animations/indicate.py:14`

```python
kwargs.pop('run_time', None)
super().__init__(mobject, run_time=1.0, rate_func=rate_func or _there_and_back, **kwargs)
```

`run_time` is popped and hard-pinned to `1.0`. CE's `Indicate` passes `run_time` through
(default 1.0, but honouring an override).
**Trigger:** `Indicate(sq, run_time=3)` renders in 1.0 s instead of 3.0 s.
**Fix:** `run_time = kwargs.pop('run_time', 1.0)` and forward it.

---

### M3. `AnimationGroup`'s `lag_ratio` is clobbered to `0.0` by the base `__init__`
- **Confidence:** HIGH (confirmed: `get_sub_alpha` uses 0) · **File:** `animation_group.py:26` + `base.py`

```python
self.lag_ratio = lag_ratio      # set correctly at :26
...
super().__init__(run_time=total, **kwargs)   # Animation.__init__ sets self.lag_ratio = 0.0 (CE default)
```

The value set at `:26` is overwritten by the base-class default before `get_sub_alpha`
(`base.py:116-122`) ever reads it, so per-submobject lag inside the group is always 0.
**Fix:** re-assign `self.lag_ratio = lag_ratio` after the `super()` call.

---

### M4. `Indicate` homogenises a multi-coloured mobject (single `_orig_fill`/`_orig_stroke` for the whole family)
- **Confidence:** HIGH (confirmed numerically) · **File:** `animations/indicate.py:24-38, 53-71`

`begin()` captures `_orig_fill`/`_orig_stroke` from the **first** non-empty family member and
breaks. `interpolate()` then lerps **every** family member from that single captured colour:
```python
fr, fg, fb = self._orig_fill[0], ...          # first member's colour
for fm in mob.family_members_with_points():
    cr = fr + (float(ic[0]) - fr) * alpha      # all members start from FIRST member's colour
    fm.fill_rgbas[:, ...] = cr
```
Probe: `VGroup(Square(RED), Square(BLUE))` under `Indicate(g)` — at peak both squares are
identical `[0.968, 0.850, 0.435]` = lerp(RED→YELLOW); the blue square interpolates from **red**.
`finish()` (`:83-94`) also repaints every member to the first member's colour, destroying the
original palette. CE captures/applies colour **per mobject copy** (`family_copy.set_fill(self.color)`),
preserving distinct colours when `color=None`.
**Fix:** store `_orig_fill`/`_orig_stroke` **per family member** (dict keyed by member) and lerp each.

---

### M5. `Unwrite.run_time` hardcoded to 1.0 (CE derives it from text length)
- **Confidence:** HIGH · **File:** `animations/unwrite.py:8`

```python
def __init__(self, mobject, rate_func=_linear, reverse=True, run_time=1.0, **kwargs):
```
CE's `Unwrite` computes `run_time` from `len(mobject.family_members_with_points())`
(≈ 0.1 s/submobject, like `Write`). For a 20-glyph `Text`, CE ≈ 2.0 s, RTM is pinned to 1.0 s.
**Fix:** default `run_time=None` and derive it the way `Write` does.

---

### M6. `Unwrite` / `DrawBorderThenFill` apply `rate_func` twice
- **Confidence:** HIGH (code-certain; wrong for any non-linear `rate_func`) · **Files:** `unwrite.py:26-27`, `draw_border_then_fill.py:89`

```python
# unwrite.py
sub_alpha = self.get_sub_alpha(alpha, idx, num_subs)   # get_sub_alpha already applies rate_func (base.py:122)
letter_alphas[i] = self.rate_func(1.0 - sub_alpha)     # applied AGAIN
# draw_border_then_fill.py
stroke_alpha = self.rate_func(alpha / border_frac)     # alpha is already post-rate_func in interpolate()
```
`base.get_sub_alpha` calls `self.rate_func(...)` (`base.py:122`). Applying it again distorts
the easing. Harmless only for linear `rate_func`; `DrawBorderThenFill`'s default is
`_double_smooth`, and any user-supplied non-linear func is doubly-eased.
**Fix:** compute the reverse with `1 - sub_alpha` **without** re-calling `rate_func`, and in
DBTF feed the pre-rate `alpha` (or use a plain linear map for the border sub-phase).

---

### M7. `Uncreate` easing differs from CE (`lambda t: 1-t` vs `reverse_rate_function=True` on smooth)
- **Confidence:** HIGH (code-certain) · **File:** `animations/uncreate.py:8-9`

```python
if rate_func is None:
    rate_func = lambda t: 1.0 - t          # LINEAR reverse
```
CE's `Uncreate` keeps the default `smooth` `rate_func` and sets `reverse_rate_function=True`
(→ `smooth(1-alpha)`). RTM substitutes a **linear** `1-t`, so the un-create eases differently
(no ease-out) and also differs from RTM's own `Unwrite` semantics.
**Fix:** default to `_smooth` with `reverse_rate_function=True`.

---

### M8. `SpiralIn` omits CE's per-shape counter-rotation
- **Confidence:** HIGH (code-certain vs CE `creation.py:487`) · **File:** `animations/spiral_in.py:34-48`

CE rotates each shape **about its own centre** by `-TAU*alpha` as it spirals in, keeping the
shapes upright. RTM's `interpolate` moves each shape along the spiral (`shape.move_to(...)`)
but never counter-rotates, so the shapes keep spinning as they converge.
**Fix:** after `move_to`, apply the per-shape counter-rotation about `shape.get_center_of_mass()`.

---

### M9. `Transform.interpolate` swallows **all** exceptions → silent no-op morph
- **Confidence:** HIGH · **File:** `animations/transform.py:45-52`

```python
try:
    ...
    for m, s, tgt in zip(mob_fam, start_fam, target_fam):
        m.interpolate(s, tgt, alpha, pf)
except Exception:
    pass
```
The whole interpolate loop is wrapped in a bare `except Exception: pass`; a submobject-shape
mismatch (or a failure caused by the swallowed `align_data` at `:30-34`) makes the Transform
silently draw nothing / freeze. CE does not guard this.
**Fix:** remove the blanket `except`; let genuine errors surface (or catch only the specific
`align_data` mismatch and fall back to whole-mobject `set_points`).

---

### M10. `run.py` never restores the `MLWindow` monkeypatch if `construct()` raises
- **Confidence:** HIGH (code-certain) · **File:** `run.py:190-216`

```python
vb.MLWindow.__init__ = _patched_init
vb.MLWindow.close    = _patched_close
...
scene.construct()                 # if this raises ...
...
vb.MLWindow.__init__ = _orig_init # ... these never run
vb.MLWindow.close    = _orig_close
```
`scene.construct()` (and `_save_tex_cache`/`_clean_media`) sit between the patch and the
restore with **no try/finally**. Any exception leaves `MLWindow.__init__`/`close` permanently
patched process-wide (subsequent scenes auto-record to a stale `out_path`).
**Fix:** wrap the body in `try: ... finally:` restoring both.

---

### M11. Recorder / ffmpeg / temp leaks when a scene raises after the window opens
- **Confidence:** HIGH · **Files:** `record.py`, `vulkan_bind.py:3510, 3546-3559`

Two related leaks:
1. `record.py`: if the scene body raises **after** the recorder window is opened, the
   recorder's `on_close` is skipped → the ffmpeg process and its temp files are never reaped.
2. `vulkan_bind.py:3510` `close()` does **not** call `_finish_fast_record`, so closing the
   window without an explicit `finish` orphans the ffmpeg child and leaks its temp BMPs;
   `_capture_screenshot_to_pipe` (`:3546-3559`) also has no `BrokenPipeError` handler and
   runs ffmpeg with `stderr=DEVNULL`, hiding startup errors.
**Fix:** `try/finally` around the recorded body calling `on_close`/`_finish_fast_record`;
catch `BrokenPipeError` and surface ffmpeg stderr.

---

### M12. `FindWindowW(None, "Real Time Manim")` targets the first such window desktop-wide
- **Confidence:** HIGH (code-certain) · **File:** `vulkan_bind.py:3374, 3449, 3505, 3686`

Recording/screenshot helpers locate the app window by **title only**, via
`FindWindowW(None, "Real Time Manim")`, ignoring the owning process. With two RTM instances
running, every capture binds to whichever window the OS returns first — cross-instance
corruption of recordings/screenshots.
**Fix:** filter by process id (enumerate `GetWindowThreadProcessId` and match `os.getpid()`).

---

### M13. `background_color` caches by `id(image)` → stale colour after id reuse
- **Confidence:** MEDIUM (code-certain hazard; id-reuse is timing-dependent) · **File:** `background_color.py:26, 45`

```python
_cache: dict[int, tuple | None] = {}   # id(image) -> mean colour
```
Keying a module-level dict by `id(image)` without holding a reference to the image means a
**new** image allocated at a freed address inherits the previous image's cached mean colour.
The project's own `state.py` docstring documents this exact hazard class (hence the
`WeakKeyDictionary` registries there), but `background_color` uses a plain `id` dict.
**Fix:** key by the image object in a `WeakKeyDictionary`, or hold a strong ref alongside the id.

---

### M14. `base.get_sub_alpha` omits `reverse_rate_function` and clamps before `rate_func`
- **Confidence:** HIGH (confirmed vs CE source) · **File:** `animations/base.py:116-122`

```python
raw_sub_alpha = max(0.0, min(1.0, value - lower))
return self.rate_func(raw_sub_alpha)
```
CE (`animation.py:get_sub_alpha`) does **not** clamp and handles reverse **inside**:
```python
if self.reverse_rate_function:
    return self.rate_func(1 - (value - lower))
else:
    return self.rate_func(value - lower)
```
RTM's version both clamps the pre-rate value (CE passes values >1 / <0 through to the rate
func) and ignores `reverse_rate_function` entirely. Diverges for any animation with
`lag_ratio > 0` **and** a non-linear or reverse rate func.
**Fix:** mirror CE — no pre-clamp, apply `1 - (...)` when `reverse_rate_function`.

---

### M15. `timeline` coerces `run_time == 0` to `1.0` → phantom extra second
- **Confidence:** HIGH (code-certain) · **File:** `timeline.py:78, 202`

```python
run_time = float(getattr(anim, "run_time", 1.0) or 1.0)   # 0.0 -> 1.0
"run_time": float(getattr(anim, "run_time", 1.0) or 1.0),  # :202
```
`x or 1.0` maps a legitimate `run_time = 0.0` to `1.0`, adding a phantom second of duration
and frames for `Wait(0)` or any zero-run animation. CE treats a 0-run animation as empty.
**Fix:** use `run_time = getattr(anim, "run_time", 1.0); if run_time is None: run_time = 1.0`
(or `max(0.0, ...)`), not truthiness.

---

### M16. `Timeline.render_at` skips mobject updaters on the first frame and on every seek
- **Confidence:** HIGH (contradicts its own docstring) · **File:** `timeline.py:301-304`

```python
dt = 0.0 if (self._last_t is None or t <= self._last_t) else t - self._last_t
if dt > 0.0:
    _drive_mobject_updaters(self.scene, dt)
```
The docstring (`:297-300`) says a seek "re-anchors with dt=0" — but `dt` is 0 on the **first**
frame (`_last_t is None`) and on **every** backward/equal seek, so `_drive_mobject_updaters`
is skipped entirely. `always_redraw` / time-based updaters / camera trackers therefore produce
**stale** state on the first rendered frame and after any scrub backwards.
**Fix:** drive updaters with `dt=0` (re-anchor) even on the first frame / seeks, per the
docstring's intent.

---

## Severity: LOW

### L1. `TextDecimalNumber` contains dead / erroneous duplicate methods → `AttributeError`
- **Confidence:** HIGH (code-certain) · **File:** `animations/text.py:45-113`

The second `update_submobject_list` (`:55-113`) shadows the first (`:45-46`) and references
non-existent attributes `self.all_submobs`, `self.cursor`, `self._orig_fo`, `self.buff`,
`self.keep_cursor_y`, `self.initial_cursor_y`. `_build_cache` references a non-existent
`cls._digit_cache`. `set_value` also grows a class-level `_value_cache` without bound and
swaps `self.submobjects` directly. Any invocation of the shadowed method raises
`AttributeError`.
**Fix:** delete the dead duplicate; use the attributes that exist; bound or instance-scope the cache.

### L2. `frames.py`: `--out` given without a value raises `IndexError`
- **Confidence:** HIGH · **File:** `frames.py` (argparse block)
An optional flag parsed by positional index (not `argparse`) crashes when supplied with no
value. **Fix:** use `argparse` or validate presence.

### L3. `record.py`: `_produced_files` prefix matching can over-match
- **Confidence:** MEDIUM · **File:** `record.py`
Cleanup selects produced files by path-prefix; a shared-directory prefix can capture
unrelated files. **Fix:** match on the exact generated basename set.

### L4. `Write` counts `len(submobjects)` vs CE's `len(family_members_with_points())`
- **Confidence:** MEDIUM · **File:** `animations/write.py`
For nested `Tex`/`MathTex`, CE's run_time/lag derive from `family_members_with_points()`;
RTM uses direct `submobjects`, giving a different run_time for nested groups.
**Fix:** use `family_members_with_points()` for the count.

### L5. `Resolve`-style `sys.path` growth in `frames.py:_resolve_scene`
- **Confidence:** LOW · **File:** `frames.py`
`_resolve_scene` appends to `sys.path` per call without dedup → unbounded growth across many
resolutions in one process. **Fix:** check membership before appending.

### L6. Lone RTM `Wait` is never treated as a frozen frame
- **Confidence:** HIGH (confirmed: 5 frames vs manim's 4 for `Wait(0.3)` @15fps) · **Files:** `timeline.py:113-130, 160`, `animations/wait.py`
`ce_frame_count`/`resolve_static_wait` test `isinstance(anim, manim.Wait)`, but RTM exports its
**own** `Wait` (subclassing RTM `Animation`, `animations/wait.py:6`), which is not a
`manim.Wait`. A lone RTM `Wait` therefore falls through to the stepped `arange` count (5)
instead of the frozen `int()` count (4). Note `scene.wait()` builds a `manim.Wait` (correctly
frozen), so this only bites code that explicitly imports RTM's `Wait`.
**Fix:** also accept RTM's `Wait` in the `isinstance` checks (and give it an `is_static_wait`).

---

## Not bugs (verified intentional / correct)

- **`Transform.clean_up_from_scene` leaving `_transforming=True`** for a plain
  `Transform` (`transform.py:99`) is **intentional** — the play path deliberately keeps the
  flag for permanent morphs (`vulkan_bind.py:3218-3231`, `keep = True` for
  `_ManimTransform` without replacement) so the renderer draws the morphed points. Not a bug.
- **Rate functions** (`_smooth`, `_linear`, `_rush_into`, `_rush_from`, `_there_and_back`,
  `_slow_into`, `_double_smooth`, `_wiggle`, `_lingering`, `_exponential_decay`) all match
  CE 0.21 numerically. No mismatches.
