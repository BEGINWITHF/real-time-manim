# animation — motion, timing & text

> scope: Rotate/Rotating; MoveAlongPath/Homotopy (+SmoothedVectorizedHomotopy/ComplexHomotopy/PhaseFlow); Broadcast; Wait/ChangeSpeed/Animation + rate_func overview; AnimationGroup/LaggedStart/LaggedStartMap/Succession; Animation base (common params, set_default, set_rate_func); Scene.play/wait/pause/wait_until; `.animate` + generate_target/MoveToTarget; updater animations + update utils + TracedPath/AnimatedBoundary; text/number animations.
> src: `../zh_CN/03-动画/{移动与旋转,等待与变速,组合编排,通用,更新器动画,文字与数字}/`
> NOTE: `import` all animation classes from `real_time_manim` (top level) or `real_time_manim.vulkan_bind` (legacy). Use RTM's `Wait` from `vulkan_bind`, not `manim`'s. `win.play(...)` is the driver (see README §5).

---

## Rotate / Rotating

### `Rotate`
```python
Rotate(mobject, angle=PI, axis=OUT, about_point=None, about_edge=None, **kwargs)
```
- `ret`: `Animation` → pass to `win.play(...)`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | object to rotate |
| `angle` | `float` | `PI` | rotation angle in radians (`PI`, `2*PI/3`, `90 * DEGREES`) |
| `axis` | `Vector3DLike` | `OUT` | rotation axis (2D = z). axis ∥ ±z → scalar draw channel, angle sign flipped (`axis=IN` reverses). other axes → per-frame 3D Rodrigues (2D shows perspective squash) |
| `about_point` | `Point3DLike \| None` | `None` | pivot; `None` → `mobject.get_center()` |
| `about_edge` | `Vector3DLike \| None` | `None` | used when `about_point is None`; bbox edge as pivot (e.g. `UP`) → `get_critical_point(about_edge)` |
| `**kwargs` | `Any` | — | `Animation` common params (`run_time`, `rate_func`, …) |

- `notes`:
  - RTM-owned implementation `real_time_manim/animations/rotate.py`; **NOT** a `Transform` subclass.
  - one-shot rotate by `angle`; RTM bakes real per-frame rotation when an explicit `about_point`/`about_edge` (or non-z axis) is given — final state pointwise-identical to CE. Only "about self center + axis ∥ z" uses the cheap scalar render channel.
  - pivot precedence: `about_point` > `about_edge` > self center.
  - `path_arc` / `path_func` kwargs are swallowed (not a `Transform` subclass); use `Transform` for arc paths.
  - **RTM vs CE**: `axis` / `about_edge` wired 2026-10-16 (`tests/test_gap_transform_motion.py`); previously `axis=IN` was a no-op.
- `see`: ../zh_CN/03-动画/移动与旋转/01-旋转.md
- `eg`:
```python
win.play(Rotate(sq, angle=2 * PI / 3, about_point=pivot.get_center(),
                run_time=1.6, rate_func=smooth))
```

### `Rotating`
```python
Rotating(mobject, angle=TAU, axis=None, about_point=None, about_edge=None,
         run_time=5, rate_func=linear, **kwargs)
```
- `ret`: `Animation` → pass to `win.play(...)`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | object to rotate |
| `angle` | `float` | `TAU` | total angle (radians): `TAU`, `180 * DEGREES`, `PI`… |
| `axis` | `Vector3DLike \| None` | `None` | **RTM default is `None`** (semantically `OUT`; `_is_3d_axis()` treats `None` as non-3D, `interpolate` handles as `OUT`). **ManimCE signature writes `OUT`** — same behavior, different default spelling. `OUT` = forward, `IN` = reversed on a 2D picture |
| `about_point` | `Point3DLike \| None` | `None` | pivot; `None` → object center. explicit value → real per-frame orbit baking |
| `about_edge` | `Vector3DLike \| None` | `None` | used when `about_point is None`; bbox edge as hinge (e.g. `UP`) |
| `run_time` | `float` | `5` | total duration (s) |
| `rate_func` | `Callable` | `linear` | progress func (`linear`, `rush_into`, `smooth`…) |
| `**kwargs` | `Any` | — | `Animation` common params; `path_arc`/`path_func` swallowed (not `Transform`) |

- `notes`:
  - RTM-owned `real_time_manim/animations/rotating.py`; **not** a `Rotate` or `Transform` subclass.
  - continuous rotation: each frame resets the object to its start state, then rotates by `rate_func(alpha) * angle` → "really turns", never distorted by interpolation. Good for gears/needles/3D objects.
  - explicit `about_point`/`about_edge` (or non-z axis) → per-frame baked 3D/around-pivot rotation.
- `see`: ../zh_CN/03-动画/移动与旋转/01-旋转.md
- `eg`:
```python
win.play(Rotating(arrow, angle=180 * DEGREES, axis=IN,
                  run_time=1.4, rate_func=linear))
```

---

## MoveAlongPath / Homotopy family

### `MoveAlongPath`
```python
MoveAlongPath(mobject, path, suspend_mobject_updating=False, **kwargs)
```
- `ret`: `Animation` → pass to `win.play(...)`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | moving object |
| `path` | `VMobject` | — | path; **only** vector objects (`Line`, `Arc`, `Circle`, custom `VMobject`…) |
| `suspend_mobject_updating` | `bool` | `False` | suspend updaters (keep `False` if the path needs updaters) |
| `**kwargs` | `Any` | — | `Animation` common params (`run_time`, `rate_func`, `lag_ratio`…) |

- `notes`:
  - source `animation/movement.py`. Each frame: `path.point_from_proportion(rate_func(alpha))` then `move_to`. **Moves position only, not orientation.**
  - `rate_func` directly sets speed along the path (`linear` = constant; `smooth` = slow-fast-slow).
- `see`: ../zh_CN/03-动画/移动与旋转/02-沿路径与同态变换.md
- `eg`:
```python
win.play(MoveAlongPath(dot, path, run_time=2.0, rate_func=linear))
```

### `Homotopy`
```python
Homotopy(homotopy, mobject, run_time=3, apply_function_kwargs=None, **kwargs)
```
- `ret`: `Animation` → pass to `win.play(...)`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `homotopy` | `Callable[[float,float,float,float], tuple]` | — | `(x, y, z, t) -> (x', y', z')`, `t` from 0 to 1 |
| `mobject` | `Mobject` | — | deformed object (recomputed each frame from a start copy) |
| `run_time` | `float` | `3` | duration (s) |
| `apply_function_kwargs` | `dict \| None` | `None` | passed through to `Mobject.apply_function` (e.g. `about_point`/`about_edge`); invalid key → `TypeError` at construction (2026-10-16) |
| `**kwargs` | `Any` | — | `Animation` common params (`rate_func`…) |

- `notes`:
  - source `animation/movement.py`. Pointwise remap of the whole shape.
  - recomputed each frame from the **start copy** — it will not "rest in an intermediate state" after finishing. For a per-frame `make_smooth()` variant use `SmoothedVectorizedHomotopy`.
- `errs`:
  - `TypeError` — invalid key in `apply_function_kwargs` → only pass keys accepted by `Mobject.apply_function`.
- `see`: ../zh_CN/03-动画/移动与旋转/02-沿路径与同态变换.md
- `eg`:
```python
def wave(x, y, z, t):
    return (x, y + 0.45 * np.sin(2.2 * x + 2.0 * np.pi * t), z)
win.play(Homotopy(wave, rect, run_time=2.0, rate_func=linear))
```

### `SmoothedVectorizedHomotopy`
```python
SmoothedVectorizedHomotopy(homotopy, mobject, run_time=3, apply_function_kwargs=None, **kwargs)
```
- `ret`: `Animation` → pass to `win.play(...)`.
- `args`: identical to `Homotopy` (subclass with **no own `__init__`**); `mobject` **must be a `VMobject`**.
- `notes`:
  - source `animation/movement.py` (no docstring). Calls `make_smooth()` on the result each frame → smooth curves, no kinks. Non-`VMobject` → `assert` fails.
  - upstream manim 0.21 `interpolate_submobject` uses `VMobject` without importing it → `NameError` on first interpolation in pure manim; fix is `movement.VMobject = VMobject`. RTM's `compat.py` already ships this fix.
  - `apply_function_kwargs` fixed 2026-10-16: upstream `VMobject.apply_function` declares `about_point`/`about_edge` but does not forward them (0.19–0.21); RTM patches it (also applies to an already-imported external manim).
- `errs`:
  - `AssertionError` — `mobject` not a `VMobject`.
  - `NameError` (pure manim only) — upstream missing import; not in RTM.
- `see`: ../zh_CN/03-动画/移动与旋转/02b-同态变换其余类.md

### `ComplexHomotopy`
```python
ComplexHomotopy(complex_homotopy, mobject, **kwargs)
```
- `ret`: `Animation` → pass to `win.play(...)`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `complex_homotopy` | `Callable[[complex,float], complex]` | — | input complex + time, output complex (e.g. `lambda z, t: z * np.exp(1j * t * PI / 2)`) |
| `mobject` | `Mobject` | — | deformed object |
| `**kwargs` | `Any` | — | `Homotopy`'s `run_time=3`, `apply_function_kwargs` + `Animation` common params |

- `notes`: source `animation/movement.py`. Treats `(x, y)` as complex `z`, computes `complex_homotopy(complex(x, y), t)`, then takes real/imag; `z` coordinate unchanged.
- `see`: ../zh_CN/03-动画/移动与旋转/02b-同态变换其余类.md

### `PhaseFlow`
```python
PhaseFlow(function, mobject, virtual_time=1, suspend_mobject_updating=False,
          rate_func=linear, **kwargs)
```
- `ret`: `Animation` → pass to `win.play(...)`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `function` | `Callable[[np.ndarray], np.ndarray]` | — | vector field: point → velocity (e.g. `lambda p: np.array([-p[1], p[0], 0])`) |
| `mobject` | `Mobject` | — | pushed object |
| `virtual_time` | `float` | `1` | displacement multiplier |
| `suspend_mobject_updating` | `bool` | `False` | suspend updaters |
| `rate_func` | `Callable` | `linear` | progress func |
| `**kwargs` | `Any` | — | `Animation` common params |

- `notes`: source `animation/movement.py` (no docstring). Per-frame accumulated displacement `Δ = virtual_time * (rate_func(a2) - rate_func(a1)) * function(p)`. **No `apply_function_kwargs` param** (unlike `Homotopy`).
- `see`: ../zh_CN/03-动画/移动与旋转/02b-同态变换其余类.md
- `eg`:
```python
win.play(PhaseFlow(lambda p: np.array([-p[1] - 1.3, p[0], 0.0]), dot,
                   virtual_time=1.2, run_time=2.0, rate_func=linear))
```

---

## Broadcast

### `Broadcast`
```python
Broadcast(mobject, focal_point=ORIGIN, n_mobs=5, initial_opacity=1, final_opacity=0,
          initial_width=0.0, remover=True, lag_ratio=0.2, run_time=3, **kwargs)
```
- `ret`: `Animation` → pass to `win.play(...)`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | broadcast shape (copied `n_mobs` times; original untouched) |
| `focal_point` | `Sequence[float]` | `ORIGIN` | emission center. **RTM default is the mobject center** unless explicitly passed (see notes) |
| `n_mobs` | `int` | `5` | number of copies |
| `initial_opacity` | `float` | `1` | start opacity (0–1) |
| `final_opacity` | `float` | `0` | end opacity (0–1) |
| `initial_width` | `float` | `0.0` | start width (`0` = from a point; `0.2` = starts as a small ring) |
| `remover` | `bool` | `True` | remove copies after playing |
| `lag_ratio` | `float` | `0.2` | ring-to-ring stagger (larger = more sequential) |
| `run_time` | `float` | `3` | total duration |
| `**kwargs` | `Any` | — | passed to `LaggedStart`/`AnimationGroup` (e.g. `rate_func`) |

- `notes`:
  - inherits `Broadcast(LaggedStart) ← AnimationGroup`, source `animation/specialized.py`. Each copy `Restore`s from `initial_width` to full size while opacity goes `initial_opacity` → `final_opacity`.
  - **not in RTM's owned-animation export list**: samples use manim's own `Broadcast` rendered through the RTM timeline, together with RTM's `_spec.Broadcast` patch.
  - **RTM vs CE**: `focal_point` default remains the **mobject center** (existing RTM deviation, kept to preserve existing renders) — explicit passing gives manual semantics. As of 2026-10-16 both keyword and positional passing work (`Broadcast(mob, ORIGIN, 3)` no longer raises `TypeError`).
- `see`: ../zh_CN/03-动画/移动与旋转/03-特殊出场.md

---

## Wait / ChangeSpeed / Animation (base)

### `Wait`
```python
Wait(run_time=1, stop_condition=None, frozen_frame=None, rate_func=linear, **kwargs)      # ../zh_CN/03-动画/等待与变速
Wait(run_time=1.0, rate_func=None, stop_condition=None, frozen_frame=None, **kwargs)      # ../zh_CN/03-动画/通用/02-play与wait参数
```
- `ret`: `Animation` → pass to `win.play(...)`, or place inside `Succession`/`AnimationGroup`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `run_time` | `float` | `1` | wait seconds |
| `stop_condition` | `Callable[[], bool] \| None` | `None` | evaluated each frame; truthy ends early. **With `frozen_frame=True` → `ValueError`** (same as manim) |
| `frozen_frame` | `bool \| None` | `None` | `True` = freeze frame, updaters not driven; `False` = step frames; `None` = auto (freeze if the scene has no updater, else step) |
| `rate_func` | `Callable` | `linear` | progress func (usually irrelevant — nothing to interpolate) |
| `**kwargs` | `Any` | — | `Animation` common params |

- `notes`:
  - RTM-owned implementation; import from `real_time_manim.vulkan_bind` (do **not** use manim's `Wait`).
  - the two zh_CN pages disagree on the exact signature/defaults (see the two lines above); both are verbatim from their sources. Semantics identical.
  - only needed explicitly when placing a wait inside a `Succession`/`AnimationGroup` timeline; otherwise `win.play(Wait(1.2))` or `self.wait(1.2)`.
- `errs`:
  - `ValueError` — `stop_condition` given together with `frozen_frame=True`.
- `see`: ../zh_CN/03-动画/等待与变速/01-等待速率与变速.md
- `eg`:
```python
win.play(Wait(1.0))
```

### `ChangeSpeed`
```python
ChangeSpeed(anim, speedinfo, rate_func=None, affects_speed_updaters=True, **kwargs)
```
- `ret`: `Animation` → pass to `win.play(...)`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `anim` | `Animation \| _AnimationBuilder` | — | wrapped animation (`AnimationGroup` gets each sub-animation processed then rebuilt) |
| `speedinfo` | `dict[float, float]` | — | `{progress_fraction: speed_multiplier}` e.g. `{0.3:1, 0.6:0.1, 1:1}`. Missing `0` → `1`; missing `1` → last multiplier |
| `rate_func` | `Callable \| None` | `None` | override the wrapped animation's rate func (`None` = keep its own) |
| `affects_speed_updaters` | `bool` | `True` | also slow/speed updaters added via `ChangeSpeed.add_updater` |
| `**kwargs` | `Any` | — | `Animation` common params (`run_time` recomputed internally on the new timeline) |

- `notes`:
  - source `animation/speedmodifier.py`; RTM wiring lives in **`window/patches.py`** (`_sm.prepare_animation = _patched_prepare_animation` + `_RtmAnimationAdapter` bridges RTM-owned sub-animations into manim's `ChangeSpeed`) — **NOT in `compat.py`**.
  - rewrites the wrapped animation's `rate_func` and recomputes total duration on the new timeline. Speed `1` = normal, `0.1` = slow-mo, `0` = frozen; smooth transitions between nodes.
  - `speedinfo` keys are **progress fractions (0–1), not seconds**.
  - only one `affects_speed_updaters=True` `ChangeSpeed` may play at a time.
  - staticmethod `ChangeSpeed.add_updater(mobject, update_function, index=None, call_updater=False)`: only updaters added this way respond to speed changes (a `dt`-taking function gets the speed-scaled `dt`). Plain `add_updater` `dt` is unaffected.
- `errs`:
  - `AssertionError` — more than one `affects_speed_updaters=True` playing simultaneously.
- `see`: ../zh_CN/03-动画/等待与变速/01-等待速率与变速.md
- `eg`:
```python
win.play(ChangeSpeed(AnimationGroup(a.animate(run_time=1).shift(RIGHT * 6.4)),
                     speedinfo={0.3: 1, 0.5: 0.25, 1: 2}, rate_func=linear))
```

### `Animation` (base class, used directly)
```python
Animation(mobject, lag_ratio=0.0, run_time=1.0, rate_func=smooth, reverse_rate_function=False,
          name=None, remover=False, suspend_mobject_updating=True, introducer=False, use_override=True)
```
- `ret`: `Animation`. A bare `Animation` changes nothing but occupies `run_time` (placeholder in `Succession`/`LaggedStartMap`); it is also the base for custom animations (override `interpolate_mobject()`).
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `mobject` | `Mobject \| None` | `None` | target object; `None` → empty `Mobject` |
| `lag_ratio` | `float` | `0.0` | submobject stagger; sub-i progress = `rate_func(alpha*full_length - i*lag_ratio)`, `full_length = (n-1)*lag_ratio + 1`; does not change total duration |
| `run_time` | `float` | `1.0` | duration (s). RTM-owned classes do **not** validate at construction (negative/0 accepted); ManimCE raises `ValueError("The run_time of Animation cannot be negative...")` (0 OK) |
| `rate_func` | `Callable` | `smooth` | progress↔time mapping (`linear`, `smooth`, `there_and_back`, `rush_into`, `rush_from`, `double_smooth`, `exponential_decay`…) |
| `reverse_rate_function` | `bool` | `False` | `True` reverses the rate func ("play backwards" feel); does not flip `remover`/`introducer` |
| `name` | `str \| None` | `None` | name in render logs; default `<ClassName>(<MobjectName>)`; no visual effect |
| `remover` | `bool` | `False` | `True` removes mobject from scene after playing |
| `suspend_mobject_updating` | `bool` | `True` | suspend the mobject's own updaters during the animation |
| `introducer` | `bool` | `False` | `True` adds the mobject to the scene before playing |
| `use_override` | `bool` | `True` | use `override_animation` override if the mobject type redefines this class (`Animation.__new__` checks the override registry; `animation_override_for` supports cross-namespace same-name fallback; `False` keeps the original class) |

- `notes`:
  - lifecycle: `begin()` (save `starting_mobject = mobject.copy()`, build target, suspend updaters) → `interpolate(alpha)` (per frame, `alpha` 0→1; `rate_func` and `lag_ratio` apply via `get_sub_alpha()`) → `finish()` (force `interpolate(1)`, restore updaters) → `_setup_scene()` / `clean_up_from_scene(scene)` (add introducers / remove removers).
  - **RTM vs CE** run_time validation: RTM-owned classes skip it; RTM's fallback is in `win.play` — `ValueError` if the whole play's total `run_time <= 0` (`window/play.py:_validate_play_run_time`, aligned with CE's `Scene.validate_run_time`); a positive value under one frame is bumped to one frame with a warning.
  - `FadeOut` is fixed to `remover=True`; `FadeIn`'s `introducer` is **not** fixed in RTM (default `False`, explicit `True` accepted).
- `errs`:
  - `ValueError` — whole-play `run_time <= 0` (RTM `win.play`).
- `see`: ../zh_CN/03-动画/通用/01-生命周期与公共参数.md

### `Animation.set_default`
```python
@classmethod
def set_default(cls, **kwargs) -> None:
```
- `ret`: none (mutates the class's construction defaults in place).
- `args`: `**kwargs: Any` — defaults to override (e.g. `run_time=2, rate_func=linear`); any construction param. Class-global; `set_default()` with no args restores the original defaults.
- `notes`: class-level global switch — restore after use; discouraged inside library code.
- `see`: ../zh_CN/03-动画/通用/01-生命周期与公共参数.md

### `Animation.set_rate_func`
```python
def set_rate_func(self, func: Callable[[float], float]) -> "Animation":
```
- `ret`: `self` (mutates `rate_func` in place, chainable).
- `args`: `func: Callable[[float], float]` — new rate function (e.g. `linear`).
- `notes`: chainable methods implemented on RTM's own `Animation`: `set_run_time`, `get_run_time`, `get_rate_func`, `set_name`, `is_introducer`, `is_remover`, `copy` (`tests/test_gap_wait_timeline.py`).
- `see`: ../zh_CN/03-动画/通用/01-生命周期与公共参数.md
- `eg`:
```python
rot = Rotate(ci, -PI / 2, run_time=0.8).set_rate_func(linear)
```

### rate functions (overview)
- `rate_func` is a common param on every animation; default `smooth` (see `Animation` above). Full catalog: `../08-工具/02-速率函数.md`.
- commonly compared set: `linear` (constant), `smooth` (slow-fast-slow), `rush_into` (slow-in, fast-out), `rush_from` (fast-in, slow-out), `there_and_back` (returns to start), `exponential_decay` (one-shot to end), `wiggle` (oscillating overshoot), `squish_rate_func(linear, 0.35, 0.65)` (fast middle).
- `squish_rate_func` is a **factory**: call it first to get the wrapped function, then pass the result.
- `rate_func` only matters for animations with motion; on `Wait` it has no visible effect.
- `see`: ../zh_CN/03-动画/等待与变速/01-等待速率与变速.md

---

## Composition

### `AnimationGroup`
```python
AnimationGroup(*animations, group=None, run_time=None, rate_func=linear, lag_ratio=0, **kwargs)
```
- `ret`: `Animation` → pass to `win.play(...)`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `*animations` | `Animation \| Iterable[Animation]` | — | sub-animations (lists/generators auto-flattened; each goes through `prepare_animation`); any animation or `.animate` builder |
| `group` | `Group \| None` | `None` | explicit group container; default collects all non-introducer sub-mobject into a `Group` |
| `run_time` | `float \| None` | `None` | total duration; `None` = auto from sub-timeline. Non-`None` stretches/compresses the sub-timeline (CE semantics). Attribute assignment `ag.run_time = 1.8` also works |
| `rate_func` | `Callable` | `linear` | **group-level** rate func (whole timeline; sub-animations keep their own) |
| `lag_ratio` | `float` | `0` | `0` all start together; `0.5` next starts at half of previous; `1` fully sequential. `start[i+1] = start[i] + run_time[i] * lag_ratio` |
| `**kwargs` | `Any` | — | `Animation` common params (`name`, `remover`, `introducer`, `suspend_mobject_updating`…). `synchronize_with_wall_clock` is unsupported and **explicitly rejected**: `True` → `ValueError` |

- `notes`:
  - RTM-owned implementation, source `animation/composition.py`.
  - `lag_ratio` = "how far the previous has played when the next starts", not a seconds gap.
  - `run_time` works via constructor **and** attribute assignment; `play`-level `run_time` can flatten several animations at once.
  - nestable; outer `lag_ratio=1` = fully sequential groups.
- `errs`:
  - `ValueError` — `synchronize_with_wall_clock=True`.
- `see`: ../zh_CN/03-动画/组合编排/01-AnimationGroup与错峰.md
- `eg`:
```python
ag = AnimationGroup(sq.animate.shift(UP * 1.4), ci.animate.shift(DOWN * 1.4),
                    tr.animate.shift(UP * 1.4), lag_ratio=0.5, rate_func=linear)
ag.run_time = 1.8
win.play(ag)
```

### `LaggedStart`
```python
LaggedStart(*animations, lag_ratio=0.05, **kwargs)
```
- `ret`: `Animation` → pass to `win.play(...)`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `*animations` | `Animation \| Iterable[Animation]` | — | as `AnimationGroup`, e.g. `*[FadeIn(d, shift=DOWN) for d in dots]` |
| `lag_ratio` | `float` | `0.05` | stagger ratio (**unlike** `AnimationGroup`'s `0`); 0–1 |
| `**kwargs` | `Any` | — | same as `AnimationGroup`: `group`, `run_time=None`, `rate_func=linear` + `Animation` common params |

- `notes`:
  - inherits `LaggedStart(AnimationGroup)`, source `animation/composition.py`; semantics identical to `AnimationGroup` except the default stagger (pipelined appearance).
  - **not in RTM's owned 39-class export list**: `from real_time_manim import LaggedStart` yields the bundled ManimCE class (top level = `from manim import *`); timeline-driven, frame-identical to CE.
- `see`: ../zh_CN/03-动画/组合编排/01-AnimationGroup与错峰.md

### `LaggedStartMap`
```python
LaggedStartMap(animation_class, mobject, arg_creator=None, run_time=2, lag_ratio=0.05, **kwargs)
```
- `ret`: `Animation` → pass to `win.play(...)`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `animation_class` | `type[Animation]` | — | class to instantiate per submobject (`FadeIn`, `ApplyMethod`…) |
| `mobject` | `Mobject` | — | container iterated **per submobject** |
| `arg_creator` | `Callable \| None` | `None` | `submob -> (animation args tuple)`; `None` → pass `submob` as the sole arg (e.g. `lambda m: (m.set_color, YELLOW)`) |
| `run_time` | `float` | `2` | group total duration |
| `lag_ratio` | `float` | `0.05` | stagger ratio (a duplicate in `**kwargs` is stripped; this param wins) |
| `**kwargs` | `Any` | — | passed to **each** `animation_class` instance (e.g. `rate_func=there_and_back`) |

- `notes`:
  - inherits `LaggedStartMap(LaggedStart)`, source `animation/composition.py`; shortest "apply an animation class to every submobject" form.
  - `**kwargs` go to **each sub-animation**, not the group.
  - not in RTM's owned export list — uses the bundled ManimCE class.
- `see`: ../zh_CN/03-动画/组合编排/01-AnimationGroup与错峰.md

### `Succession`
```python
Succession(*animations, lag_ratio=1, **kwargs)
```
- `ret`: `Animation` → pass to `win.play(...)`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `*animations` | `Animation \| Iterable[Animation]` | — | sub-animations (auto-flattened, `prepare_animation`); any animation, `.animate` builder, or `Wait` |
| `lag_ratio` | `float` | `1` | fixed 100% continuation; `<1` lets adjacent animations overlap. RTM's `Succession` now inherits RTM's `AnimationGroup`, so this param takes effect |
| `**kwargs` | `Any` | — | as `AnimationGroup`: `group`, `run_time=None`, `rate_func=linear` + `Animation` common params. `run_time` non-`None` proportionally stretches the whole serial timeline (`None` = sum of sub `run_time`) |

- `notes`:
  - RTM-owned implementation, source `animation/composition.py`. One plays after another; only one sub-animation runs at a time. `Wait` can be a direct sub-animation (blank gap); bare `Animation` also works as a placeholder.
  - group-level `rate_func` applies to the **whole serial timeline** (eased start/end, smooth seams) rather than each sub-animation easing separately.
  - `Succession` vs staggers: default `lag_ratio=1` (fully serial) vs `AnimationGroup(lag_ratio=0)` (fully parallel) vs `LaggedStart` (`0.05`, light stagger).
- `see`: ../zh_CN/03-动画/组合编排/02-Succession顺序播放.md
- `eg`:
```python
win.play(Succession(sq1.animate(run_time=1.0).move_to(sq2.get_center()),
                    sq2.animate(run_time=1.0).move_to(sq3.get_center()),
                    Wait(0.6),
                    sq3.animate(run_time=0.8).set_color(RED)))
```

---

## Scene driving: play / wait / pause / wait_until

### `Scene.play` (RTM: `win.play(...)`)
```python
Scene.play(*anims, subcaption=None, subcaption_duration=None, subcaption_offset=0, **kwargs)
```
- `ret`: none. Total duration of one play = `max(anim.run_time)`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `*anims` | `Animation` / `.animate` builder | — | multiple animations (parallel; duration = max `run_time`), or `.animate` builders. **Not** bare methods (`win.play(sq.shift, RIGHT)` → `TypeError`) and not bare mobjects |
| `subcaption` | `str \| None` | `None` | play-level subtitle; RTM collects text in memory, paired with `subcaption_duration`; `export_srt()` writes a `.srt` next to the mp4 at recording end. `Scene.add_subcaption` writes the same store |
| `subcaption_duration` | `float \| None` | `None` | seconds each subtitle stays (with `subcaption`) |
| `subcaption_offset` | `float` | `0` | subtitle offset in seconds relative to animation start |
| `**kwargs` | `Any` | — | effective keys: `run_time=` (overrides every animation in this play), `rate_func=` (setattr per animation), plus `path_arc=` / `path_arc_axis=` / `path_arc_centers=` / `path_func=` (since 2026-10-17). Any other key (e.g. play-level `lag_ratio=`) prints an explicit warning naming the unrecognized items + "RTM 不支持该参数" (no longer silently swallowed) |

- `notes`:
  - `win.play(*[FadeIn(m) for m in mobs])` accepts lists/generators.
  - play-level `run_time`/`rate_func` are applied by `setattr` onto each animation instance.
  - stagger must be written on the animation constructor or an `AnimationGroup`.
- `errs`:
  - `TypeError` — a bare method (or bare mobject) passed as an anim.
- `see`: ../zh_CN/03-动画/通用/02-play与wait参数.md

### `Scene.wait` / `Scene.pause` / `Scene.wait_until`
```python
def wait(self, duration=DEFAULT_WAIT_TIME, stop_condition=None, frozen_frame=None) -> None:
def pause(self, duration=DEFAULT_WAIT_TIME) -> None:
def wait_until(stop_condition, max_time=60) -> None:
```
- `ret`: none.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `duration` | `float` | `DEFAULT_WAIT_TIME` (= `1.0`) | wait seconds; `self.wait(1.2)` ≡ `win.play(Wait(1.2))` |
| `stop_condition` (wait) | `Callable[[], bool] \| None` | `None` | evaluated once per frame after drawing; truthy ends early; mutually exclusive with `frozen_frame=True` (→ `ValueError`) |
| `frozen_frame` (wait) | `bool \| None` | `None` | `True` = freeze frame (updaters not driven); `False` = step frames; `None` = auto |
| `duration` (pause) | `float` | `1.0` | `pause` = `wait(..., frozen_frame=True)`: forced still frame, updaters not driven |
| `stop_condition` (wait_until) | `Callable[[], bool]` | — | evaluated each frame; truthy ends immediately (even before `max_time`). Only during forward playback; random-access frame export still renders the full duration |
| `max_time` | `float` | `60` | max wait duration |

- `errs`:
  - `ValueError` — `stop_condition` together with `frozen_frame=True`.
- `see`: ../zh_CN/03-动画/通用/02-play与wait参数.md, ../zh_CN/01-场景与相机/场景/03-播放与等待.md

---

## `.animate` syntax & target transforms

### `Mobject.animate` (`_AnimationBuilder`)
```python
@property
def animate(self) -> _AnimationBuilder: ...

win.play(sq.animate.shift(RIGHT))                     # translate
win.play(sq.animate.set_fill(RED).set_opacity(0.5))   # chain: multiple methods -> one animation
win.play(sq.animate(run_time=2).rotate(PI / 2))       # anim kwargs right after .animate(...), only once
win.play(sq.animate(rate_func=there_and_back).shift(RIGHT))
```
- `ret`: `_AnimationBuilder`; auto-converted to an animation when passed to `win.play(...)` (also recognized by `AnimationGroup`/`Succession`).
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `**kwargs` (right after `.animate(...)`) | `Any` | — | attributes settable on the animation object: `run_time`, `rate_func`, `reverse_rate_function`… **Only once, before any chained method**; after a chained method or twice → `ValueError`. `lag_ratio=...` is **not** dropped: setattr onto the animation (staggers by family when submobjects exist; no-op for a single object with no children, now with an explicit `UserWarning`) |
| chained method calls | — | — | e.g. `.shift(RIGHT)`, `.set_fill(RED)`, `.rotate(PI/2)`: recorded into a list, combined into one animation at `win.play` |

- `notes`:
  - internally `generate_target()` first; `.animate` interpolates between the pre-change and post-change point sets → straight-line motion (a "long way around" rotation goes straight, not along an arc). For arc paths use `Rotate`, `MoveAlongPath`, or `ValueTracker` + updater.
  - one `.animate` per mobject per `play`; chain for multiple steps.
  - `@override_animate` / `@override_animation` wired (`Animation.__new__` checks the override registry; cross-namespace same-name fallback; `use_override=False` keeps the original).
- `errs`:
  - `ValueError` — animation kwargs passed after a chained method or passed twice.
- `see`: ../zh_CN/03-动画/通用/03-animate语法.md

### `generate_target` / `MoveToTarget`
```python
def generate_target(self) -> None: ...
MoveToTarget(mobject, **kwargs)
```
- `ret`: `generate_target()` → none (attaches a copy to `mobject.target`); `MoveToTarget(...)` → `Animation` → pass to `win.play(...)`.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | object that moves to its own `target`; `generate_target()` must have been called first |
| `**kwargs` | `Any` | — | `Animation` common params (`run_time`, `rate_func`, `lag_ratio`…); no extra params |

- `notes`: `.animate` is sugar for `generate_target()` + `MoveToTarget`. Use the explicit form when the target needs computation first (layout/align `target`, then play). Without a prior `generate_target()`: ManimCE raises `ValueError` at construction; RTM's own version raises `AttributeError: 'NoneType' object has no attribute 'copy'` in `begin()` (`Mobject.target` is `None`).
- `errs`:
  - `ValueError` — ManimCE version, no `target`.
  - `AttributeError: 'NoneType' object has no attribute 'copy'` — RTM version, no `target`.
- `see`: ../zh_CN/03-动画/通用/03-animate语法.md
- `eg`:
```python
ci.generate_target()
ci.target.set_fill(RED, 0.4).shift(2 * RIGHT + UP).scale(0.5)
win.play(MoveToTarget(ci, run_time=1.2))
```

---

## Updater animations & update utils

### `UpdateFromFunc`
```python
UpdateFromFunc(mobject, update_function, suspend_mobject_updating=False, **kwargs)
```
- `ret`: `UpdateFromFunc` instance.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | driven object |
| `update_function` | `Callable[[Mobject], Any]` | — | called each frame with the mobject |
| `suspend_mobject_updating` | `bool` | `False` | suspend the mobject's own updaters; **keep `False`** to coexist |
| `**kwargs` | `Any` | — | `Animation` common params (**`run_time` must be given explicitly**, else callbacks stop after 1 s) |

- `notes`:
  - source manim `animation/updaters/update.py` — not in RTM's `vulkan_bind` export list, but RTM's render hooks take over; frame-aligned across both engines.
  - `rate_func` is not passed to the function; behavior is up to the function.
- `see`: ../zh_CN/03-动画/更新器动画/01-更新器动画与自动变化.md
- `eg`:
```python
win.play(dot.animate.shift(RIGHT * 3),
         UpdateFromFunc(label, lambda l: l.next_to(dot, UP), run_time=3),
         rate_func=linear)
```

### `UpdateFromAlphaFunc`
```python
UpdateFromAlphaFunc(mobject, update_function, suspend_mobject_updating=False, **kwargs)
```
- `ret`: `UpdateFromAlphaFunc` instance.
- `args`: same as `UpdateFromFunc`, but `update_function: Callable[[Mobject, float], Any]` — second arg is the `rate_func`-processed progress.
- `notes`: inherits `UpdateFromAlphaFunc(UpdateFromFunc)` with **no own `__init__`**; only the interpolation is overridden. `alpha` advances monotonically 0→1. A wrong callback signature raises on the first frame.
- `errs`: callback arity mismatch → exception on first frame.
- `see`: ../zh_CN/03-动画/更新器动画/01-更新器动画与自动变化.md

### `MaintainPositionRelativeTo`
```python
MaintainPositionRelativeTo(mobject, tracked_mobject, **kwargs)
```
- `ret`: `MaintainPositionRelativeTo` instance.
- `args`: `mobject: Mobject` (follower); `tracked_mobject: Mobject` (tracked); `**kwargs` = `Animation` common params.
- `notes`: keeps the initial relative offset between `mobject` and `tracked_mobject` during playback (tracked moves → follower follows). No docstring; source-derived.
- `see`: ../zh_CN/03-动画/更新器动画/01-更新器动画与自动变化.md

### update utils (module-level functions; not animation classes)
- `ret`: the mobject with the updater attached (just `self.add(...)`).
- table:

| function (source `mobject_update_utils.py`) | signature | effect |
| --- | --- | --- |
| `always_redraw` | `always_redraw(func) -> Mobject` | regenerate the object each frame via `func()` (`mob.become(func())`) |
| `always` | `always(method, *args, **kwargs) -> Mobject` | call `method(*args, **kwargs)` each frame (`method` must be a bound mobject method), e.g. `always(sq.set_color, RED)` |
| `f_always` | `f_always(method, *arg_generators, **kwargs) -> Mobject` | like `always`, but args are **generator functions** re-evaluated each frame, e.g. `f_always(label.next_to, mob.get_center, UP)` |
| `always_shift` | `always_shift(mobject, direction=RIGHT, rate=0.1) -> Mobject` | shift `rate` units along `direction` per second |
| `always_rotate` | `always_rotate(mobject, rate=20*DEGREES, **kwargs) -> Mobject` | rotate `rate` radians per second (`**kwargs` → `rotate`, e.g. `about_point`) |
| `turn_animation_into_updater` | `turn_animation_into_updater(animation, cycle=False, delay=0, **kwargs) -> Mobject` | turn any animation into an updater: not `play`ed, advances with scene time; `delay` = delay seconds |
| `cycle_animation` | `cycle_animation(animation, **kwargs) -> Mobject` | `turn_animation_into_updater(animation, cycle=True)`, infinite loop |
| `override_animation` | `override_animation(animation_class) -> decorator` | decorate a `Mobject` subclass method to override an animation class (source `animation/animation.py`); wired in RTM (`Animation.__new__` registry, cross-namespace fallback, `use_override=False` keeps original, bidirectional) |

- `notes`:
  - these auto-changing objects only move when **scene time advances**: in RTM you must `win.play(Wait(...))` (or another play); a bare `self.add(...)` will not animate.
  - `turn_animation_into_updater` / `cycle_animation` bridge RTM-owned animation classes (`t = origin + alpha*run_time` normalized; auto-removed at end; manim animations still use the original function).
  - `always`/`f_always` `method` must be a **bound** mobject method.
  - call `clear_updaters()` before switching sections, else stale updaters keep dragging the object.
- `see`: ../zh_CN/03-动画/更新器动画/01b-更新工具与自动变化.md, ../zh_CN/02-Mobject通用/08b-更新器工具函数.md

### `TracedPath`
```python
TracedPath(traced_point_func, stroke_width=2, stroke_color=WHITE, dissipating_time=None, **kwargs)
```
- `ret`: `TracedPath` instance (a `VMobject`; `self.add(...)` directly).
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `traced_point_func` | `Callable[[], point]` | — | no-arg function returning the tracked point (e.g. `circ.get_start`, `dot.get_center`) |
| `stroke_width` | `float` | `2` | trail line width |
| `stroke_color` | `ParsableManimColor \| None` | `WHITE` | trail color |
| `dissipating_time` | `float \| None` | `None` | dissipate after that many seconds; `None` = keep forever |
| `**kwargs` | `Any` | — | other `VMobject` params (`stroke_opacity=[0,1]` for a fading trail, `fill_opacity`…) |

- `notes`: records the path walked by a point function, appending each frame. Inherits `TracedPath(VMobject)` (`metaclass=ConvertToOpenGL`). With `dissipating_time`, the trail fades segment-by-segment.
- `see`: ../zh_CN/03-动画/更新器动画/01b-更新工具与自动变化.md
- `eg`:
```python
trace = TracedPath(circ.get_start, dissipating_time=0.5, stroke_opacity=[0, 1])
group.add_updater(lambda m: m.rotate(-0.3))
self.add(trace, group)
win.play(group.animate.shift(8 * RIGHT), run_time=4, rate_func=linear)
```

### `AnimatedBoundary`
```python
AnimatedBoundary(vmobject, colors=[BLUE_D, BLUE_B, BLUE_E, GREY_BROWN], max_stroke_width=3,
                 cycle_rate=0.5, back_and_forth=True, draw_rate_func=smooth,
                 fade_rate_func=smooth, **kwargs)
```
- `ret`: `AnimatedBoundary` instance (a `VGroup`; `self.add(...)` directly).
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `vmobject` | `VMobject` | — | object to outline |
| `colors` | `Sequence` | `[BLUE_D, BLUE_B, BLUE_E, GREY_BROWN]` | cycling color sequence |
| `max_stroke_width` | `float` | `3` | max line width |
| `cycle_rate` | `float` | `0.5` | cycle speed multiplier |
| `back_and_forth` | `bool` | `True` | `True` = draw back and forth, `False` = one-way loop |
| `draw_rate_func` / `fade_rate_func` | `RateFunction` | `smooth` | draw / fade rate funcs |
| `**kwargs` | `Any` | — | `VGroup` params |

- `notes`: wraps an object in a continuously recoloring, back-and-forth drawing outline (two outline copies: one drawing, one fading). Inherits `AnimatedBoundary(VGroup)`. Auto-loops.
- `see`: ../zh_CN/03-动画/更新器动画/01b-更新工具与自动变化.md

---

## Text & number animations

### `AddTextLetterByLetter`
```python
AddTextLetterByLetter(text, suspend_mobject_updating=False, int_func=np.ceil,
                      rate_func=linear, time_per_char=0.1, run_time=None,
                      reverse_rate_function=False, introducer=True, **kwargs)
```
- `ret`: `AddTextLetterByLetter` instance.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `text` | `Text` | — | text to reveal letter by letter (must be non-empty) |
| `suspend_mobject_updating` | `bool` | `False` | suspend updaters |
| `int_func` | `Callable` | `np.ceil` | progress rounding (`ceil` = show on arrival) |
| `rate_func` | `Callable` | `linear` | constant typing |
| `time_per_char` | `float` | `0.1` | min per-character interval (s) |
| `run_time` | `float \| None` | `None` | auto = `max(1/frame_rate, time_per_char) * len(text)` |
| `reverse_rate_function` | `bool` | `False` | `True` removes in reverse |
| `introducer` | `bool` | `True` | add to scene before playing |
| `**kwargs` | `Any` | — | `ShowIncreasingSubsets`/`Animation` common params |

- `notes`: inherits `AddTextLetterByLetter(ShowIncreasingSubsets) ← Animation`. **Only supports `Text`, not `MathTex`.**
- `errs`:
  - `ValueError` — empty text.
- `see`: ../zh_CN/03-动画/文字与数字/01-逐字出现与消失.md

### `RemoveTextLetterByLetter`
```python
RemoveTextLetterByLetter(text, suspend_mobject_updating=False, int_func=np.ceil,
                         rate_func=linear, time_per_char=0.1, run_time=None,
                         reverse_rate_function=True, introducer=False, remover=True, **kwargs)
```
- `ret`: `RemoveTextLetterByLetter` instance.
- `args`: same as `AddTextLetterByLetter` except defaults `reverse_rate_function=True`, `introducer=False`, plus `remover=True` (removed from scene after playing).
- `notes`: inherits `RemoveTextLetterByLetter(AddTextLetterByLetter)`; reverse playback of the parent. Default `introducer=False` — **you must `self.add(...)` first**, otherwise the object is not in the scene and the animation spins idle. Only supports `Text`.
- `see`: ../zh_CN/03-动画/文字与数字/01-逐字出现与消失.md
- `eg`:
```python
self.add(t)
win.play(RemoveTextLetterByLetter(t))
```

### `AddTextWordByWord` (upstream broken; not recommended)
```python
AddTextWordByWord(text_mobject, run_time=None, time_per_char=0.06, **kwargs)
```
- `ret`: `AddTextWordByWord` instance (**not recommended to construct**).
- `args`: `text_mobject: Text`; `run_time: float | None = None`; `time_per_char: float = 0.06` (per-word interval); `**kwargs` = `Succession`/`AnimationGroup` common params.
- `notes`:
  - inherits `AddTextWordByWord(Succession)`.
  - upstream source marks `# TODO, this is broken...` and the docstring says *currently broken*: word splitting on a normal `Text` is empty → static frame. This is an **upstream bug, not an RTM gap**.
  - for per-word effects use `Text` line-level slicing + `LaggedStart(FadeIn)`.
- `see`: ../zh_CN/03-动画/文字与数字/01-逐字出现与消失.md

### `TypeWithCursor`
```python
TypeWithCursor(text, cursor, buff=0.1, keep_cursor_y=True, leave_cursor_on=True,
               time_per_char=0.1, run_time=None, **kwargs)
```
- `ret`: `TypeWithCursor` instance.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `text` | `Text` | — | text to type |
| `cursor` | `Mobject` | — (required, no default) | cursor (e.g. a thin rectangle / underline); repositioned during the animation |
| `buff` | `float` | `0.1` | gap between cursor and last character |
| `keep_cursor_y` | `bool` | `True` | `True` locks cursor y to the whole text center; `False` follows the current character center |
| `leave_cursor_on` | `bool` | `True` | keep the cursor after the animation (`False` hides it) |
| `time_per_char` | `float` | `0.1` | per-character interval (also drives the auto `run_time`) |
| `run_time` | `float \| None` | `None` (→ `time_per_char × chars`) | explicit value overrides the auto value |
| `rate_func` | `Callable` | `smooth` (`Animation` default) | RTM's own version has **no** CE `linear` default |
| `reverse_rate_function` | `bool` | `False` | via `**kwargs` to `Animation`, **not an explicit param** |
| `introducer` | `bool` | `False` (`Animation` default) | RTM's own version is **not fixed** (can pass `True`) |
| `**kwargs` | `Any` | — | `Animation` common params (`suspend_mobject_updating`…); RTM has no CE `int_func`/`suspend_mobject_updating=False` defaults |

- `notes`: inherits `TypeWithCursor(ShowIncreasingSubsets) ← Animation`. Often combined with `Blink` for a full input effect. Cursor color/width are set when creating the mobject — **not** in the animation signature.
- `see`: ../zh_CN/03-动画/文字与数字/01b-带光标打字.md
- `eg`:
```python
text = Text("Inserting", color=PURPLE).scale(1.5).to_edge(LEFT)
cursor = Rectangle(color=GREY_A, fill_color=GREY_A, fill_opacity=1,
                   height=1.1, width=0.5).move_to(text[0])
win.play(TypeWithCursor(text, cursor))
win.play(Blink(cursor, blinks=2))
```

### `UntypeWithCursor`
```python
UntypeWithCursor(text, cursor, buff=0.1, keep_cursor_y=True, leave_cursor_on=True,
                 time_per_char=0.1, run_time=None, **kwargs)
```
- `ret`: `UntypeWithCursor` instance.
- `args`: `text: Text`; `cursor: VMobject` (**required, second positional, no `None` default**); `buff=0.1`; `keep_cursor_y=True`; `leave_cursor_on=True`; `time_per_char=0.1`; `run_time=None` (→ `time_per_char × chars`); `**kwargs` = `Animation` common params (`rate_func`…).
- `notes`:
  - inherits `UntypeWithCursor(Animation)`; reverse typing (characters vanish from the end, cursor follows).
  - **RTM vs CE**: RTM's own version has **no `reverse_rate_function` / `remover` / `introducer` params** — the reverse direction is hard-coded (`index = n - floor(alpha*n)`); `remover`/`introducer` can only reach `Animation` via `**kwargs`, and `clean_up_from_scene` is the base-class `pass`, so it does **not** actually remove from the scene after playing. ManimCE's version has both explicit params.
  - `introducer` is not an explicit param (default `False` via `Animation`) — `self.add(text, cursor)` first, else the objects are not in the scene and the animation spins idle.
- `see`: ../zh_CN/03-动画/文字与数字/01b-带光标打字.md

### `ChangingDecimal`
```python
ChangingDecimal(decimal_mob, number_update_func, suspend_mobject_updating=False, **kwargs)
```
- `ret`: `ChangingDecimal` instance.
- `args`:

| name | type | default | meaning / constraint |
| --- | --- | --- | --- |
| `decimal_mob` | `DecimalNumber` | — | animated number (must be a `DecimalNumber`) |
| `number_update_func` | `Callable[[float], float]` | — | input progress `alpha`, returns the displayed value |
| `suspend_mobject_updating` | `bool` | `False` | suspend updaters (default `False` to coexist with `ValueTracker`) |
| `**kwargs` | `Any` | — | `Animation` common params (`run_time`, `rate_func`…) |

- `notes`: inherits `ChangingDecimal(Animation)`. Each frame `set_value(f(rate_func(alpha)))`. **One-shot**: stops at the final value.
- `errs`:
  - `TypeError` — input is not a `DecimalNumber`.
- `see`: ../zh_CN/03-动画/文字与数字/02-数字动画.md
- `eg`:
```python
win.play(ChangingDecimal(number, lambda a: 5 * a, run_time=3))
```

### `ChangeDecimalToValue`
```python
ChangeDecimalToValue(decimal_mob, target_number, **kwargs)
```
- `ret`: `ChangeDecimalToValue` instance.
- `args`: `decimal_mob: DecimalNumber`; `target_number: int` (source annotates `int`; goes through `interpolate`, so floats work too); `**kwargs` = `ChangingDecimal`'s `suspend_mobject_updating=False` + `Animation` common params (e.g. `run_time=3`).
- `notes`: inherits `ChangeDecimalToValue(ChangingDecimal)`; linearly interpolates from the current value to the target (`lambda a: interpolate(start, target, a)`). Most common "counter jumps to X" form. **One-shot** — for long-term following use `number.add_updater(lambda n: n.set_value(tracker.get_value()))` and `clear_updaters()` when done.
- `errs`:
  - `TypeError` — input is not a `DecimalNumber`.
- `see`: ../zh_CN/03-动画/文字与数字/02-数字动画.md
- `eg`:
```python
win.play(ChangeDecimalToValue(number, 10, run_time=3))
```

---

## errs index (this file)

| error | symbol | cause → fix |
| --- | --- | --- |
| `ValueError` | `Wait`, `Scene.wait` | `stop_condition` + `frozen_frame=True` together → use one |
| `ValueError` | `AnimationGroup` | `synchronize_with_wall_clock=True` → unsupported, drop it |
| `ValueError` | `Animation` (RTM `win.play`) | whole-play `run_time <= 0` → pass a positive `run_time` |
| `ValueError` | `AddTextLetterByLetter` | empty text → non-empty `Text` |
| `ValueError` | `Mobject.animate` | animation kwargs after a chained method or twice → pass once, right after `.animate(...)` |
| `ValueError` | `MoveToTarget` (ManimCE) | no prior `generate_target()` |
| `AttributeError: 'NoneType' object has no attribute 'copy'` | `MoveToTarget` (RTM) | no prior `generate_target()` → call it first |
| `AssertionError` | `ChangeSpeed` | >1 `affects_speed_updaters=True` playing → serialize |
| `AssertionError` | `SmoothedVectorizedHomotopy` | `mobject` not a `VMobject` |
| `TypeError` | `Homotopy` / `ComplexHomotopy` | invalid key in `apply_function_kwargs` |
| `TypeError` | `ChangingDecimal` / `ChangeDecimalToValue` | non-`DecimalNumber` input |
| `TypeError` | `Scene.play` | bare method/mobject passed as an anim → wrap in an animation |
| `NameError` | `SmoothedVectorizedHomotopy` (pure manim 0.21) | upstream missing import; fixed in RTM `compat.py` |
