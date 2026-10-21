# animation — transform & appearance

> scope: create/erase (`Create`/`Uncreate`/`Write`/`Unwrite`/`DrawBorderThenFill`/`ShowPartial`/`Add`/`ShowIncreasingSubsets`/`ShowSubmobjectsOneByOne`/`SpiralIn`), matching transforms, core transforms, method/function-driven transforms, state/style transforms, positional/copy transforms, fade transforms, emphasis, grow, fade.
> src: `../zh_CN/03-动画/` (`创建与擦除`, `匹配变换`, `变换`, `强调与提示`, `生长出现`, `淡入淡出`) + `real_time_manim/animations/`.
> Import rule (all entries): RTM-own classes come from `real_time_manim.vulkan_bind` (or `real_time_manim.animations`); classes **not** in RTM's own export list resolve from top-level `real_time_manim` = bundled ManimCE 0.21. See `README.md` §2/§3.

## create / erase

### `Create`
```python
Create(mobject, run_time=1.0, lag_ratio=1.0, **kwargs)
```
- `ret`: `Create` instance (RTM-own `Create(Animation)`; **not** a `ShowPartial` subclass).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `mobject` | `VMobject` | — (required) | drawn object. RTM-own does **no** type check; a plain `Mobject` also constructs (still advances by stroke) |
| `run_time` | `float` | `1.0` | seconds |
| `lag_ratio` | `float` | `1.0` | `0`~`1`; `1.0` = sub-strokes drawn one after another, `0` = all at once |
| `introducer` | `bool` | `False` | RTM-own **does not pin** it (explicit `True` works) |
| rest | — | — | `Animation`: `rate_func`/`remover`/`name`/`suspend_mobject_updating`/`reverse_rate_function`/`use_override` |

- `notes`:
  - Draws along vector strokes start→end.
  - Import: RTM-own via `from real_time_manim.vulkan_bind import Create`. Top-level `real_time_manim` resolves to bundled ManimCE 0.21 `Create(ShowPartial)` with `introducer` fixed `True` and `TypeError` on non-VMobject. Same name/params; samples do not depend on the difference.
- `see`: ../zh_CN/03-动画/创建与擦除/01-Create与画线族.md

### `Uncreate`
```python
Uncreate(mobject, run_time=1.0, lag_ratio=1.0, remover=True,
         rate_func=None, reverse_rate_function=True, **kwargs)
```
- `ret`: `Uncreate` instance (`Uncreate(Create)`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `mobject` | `VMobject` | — (required) | erased object |
| `reverse_rate_function` | `bool` | `True` | reverse playback. Since 2026-10-16 the default curve is CE `smooth(1-t)` (was linear) |
| `remover` | `bool` | `True` | remove from scene on finish; not advised `False` |
| `introducer` | `bool` | `False` | RTM-own passable (explicit `True` works) |
| `run_time` / `lag_ratio` | `float` | `1.0` / `1.0` | same as `Create` |

- `notes`: `Create` played backwards along the same strokes; reveals the stroke path (unlike `FadeOut`'s whole-object fade).
- `see`: ../zh_CN/03-动画/创建与擦除/02-反向擦除.md

### `Write`
```python
Write(mobject, rate_func=linear, reverse=False, run_time=None, lag_ratio=None, **kwargs)
```
- `ret`: `Write` instance (`Write(DrawBorderThenFill) ← DrawBorderThenFill(Animation)`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `vmobject` | `VMobject` | — (required) | written object |
| `rate_func` | `Callable` | `linear` | not advised to change (uniform = handwriting feel) |
| `reverse` | `bool` | `False` | `True` = reverse write, and defaults `remover=True`, `introducer=False` |
| `run_time` | `float \| None` | `None` | `None` → auto `1` if `length < 15` else `2` |
| `lag_ratio` | `float \| None` | `None` | `None` → auto `min(4/max(1,length), 0.2)` |
| rest | — | — | `Animation` + `DrawBorderThenFill` `stroke_width=2`/`stroke_color=None` |

- `notes`: stroke-then-fill, sub-stroke by sub-stroke; the usual reveal for `Text`/`Tex`/`MathTex`/any `VMobject`.
- `see`: ../zh_CN/03-动画/创建与擦除/01-Create与画线族.md

### `Unwrite`
```python
Unwrite(mobject, rate_func=linear, reverse=True, run_time=1.0, **kwargs)
```
- `ret`: `Unwrite` instance (`Unwrite(Write) ← DrawBorderThenFill(Animation)`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `mobject` | `VMobject` | — (required) | erased object |
| `rate_func` | `Callable` | `linear` | not advised to change |
| `reverse` | `bool` | `True` | `True` erase from last submobject; `False` from first. RTM no longer ties `reverse` to `remover` |
| `run_time` | `float` | `1.0` | RTM-own hard-codes `1.0` (no length auto) |
| `lag_ratio` | `float \| None` | `None` | `None` → auto `min(4/max(1,length), 0.2)` |
| `remover` | `bool` | `False` | RTM-own default fixed `False`, not linked to `reverse`; RTM parks stroke/sub progress to 0 but `Unwrite` has no own `clean_up_from_scene` → object stays in scene even if `remover=True` is passed |
| `reverse_rate_function` | `bool` | `False` | inherited `DrawBorderThenFill.interpolate` reads it: `False` = full→gone; `True` = reverses again (gone→full). RTM-own default `False`; ManimCE default `True` (opposite defaults) |

- `notes`: two-phase; the unwind is computed in-class as `rate_func(1 - sub_alpha)`.
- `see`: ../zh_CN/03-动画/创建与擦除/02-反向擦除.md

### `DrawBorderThenFill`
```python
DrawBorderThenFill(mobject, run_time=2.0, stroke_width=2, stroke_color=None,
                   rate_func=double_smooth, introducer=True, **kwargs)
```
- `ret`: `DrawBorderThenFill` instance (RTM-own `Animation`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `mobject` | `VMobject` | — (required) | RTM-own does no type check |
| `run_time` | `float` | `2` | total (shared by both phases) |
| `rate_func` | `Callable` | `double_smooth` | one smooth per phase ("pause then fill") |
| `stroke_width` | `float` | `2` | phase-1 outline width |
| `stroke_color` | `str \| None` | `None` | `None` → object's own stroke (else fill) color |
| `introducer` | `bool` | `True` | RTM-own makes it an explicit param (passable `False`) |

- `notes`: outline-then-fill, no per-stroke subdivision, no `lag_ratio` auto; direct parent of `Write`.
- `see`: ../zh_CN/03-动画/创建与擦除/01-Create与画线族.md

### `ShowPartial`
```python
ShowPartial(mobject, **kwargs)
```
- `ret`: `ShowPartial` instance — **do not play directly**; use `Create`/`ShowPassingFlash`.
- `args`:
  - `mobject: VMobject | OpenGLVMobject | OpenGLSurface` — required.
- `notes`:
  - **ManimCE class** (not in RTM's own export list; from top-level `real_time_manim`). Abstract base of CE `Create`/`ShowPassingFlash`; ctor checks `pointwise_become_partial`, else `TypeError`.
  - RTM-own `Create`/`ShowPassingFlash` are **not** its subclasses. RTM `compat.py` patches `_get_bounds`, so a direct pass is playable (Create-style bounds).
- `errs`:
  - `TypeError: ...` — object lacks `pointwise_become_partial`.
  - `NotImplementedError: "Please use Create or ShowPassingFlash"` — direct play of the abstract base.
- `see`: ../zh_CN/03-动画/创建与擦除/01-Create与画线族.md

### `Add`
```python
Add(*mobjects, run_time=0.0, **kwargs)
```
- `ret`: `Add` instance (`Add(Animation)`).
- `args`:
  - `*mobjects: Mobject` — required; >1 wrapped into a `Group`.
  - `run_time: float = 0.0` — dwell after the (instant) insert.
  - `introducer: bool = False` — RTM-own does not pin it.
- `notes`: animation form of `Scene.add`; composable in `Succession`/`AnimationGroup` and schedulable. `win.play(Add(x))` == `self.add(x)` but honors `run_time`.
- `see`: ../zh_CN/03-动画/创建与擦除/02-反向擦除.md

### `ShowIncreasingSubsets`
```python
ShowIncreasingSubsets(group, suspend_mobject_updating=False, int_func=np.floor,
                      reverse_rate_function=False, **kwargs)
```
- `ret`: `ShowIncreasingSubsets` instance (`Animation`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `group` | `Mobject` | — (required) | container (`VGroup`…) revealed item by item |
| `suspend_mobject_updating` | `bool` | `False` | not advised to change |
| `int_func` | `Callable` | `np.floor` | maps continuous progress → count shown; `np.floor`/`np.ceil`/custom |
| `reverse_rate_function` | `bool` | `False` | `True` = reverse collapse |

- `notes`: **ctor immediately `set_opacity(0)`s every submobject** → either `self.add(group)` before constructing, or ensure it enters the scene only on `play`. Shows items one after another, all previous stay (opacity snaps 0→1, not a fade). `int_func` replaces `lag_ratio` here.
- `see`: ../zh_CN/03-动画/创建与擦除/03-逐个显示与集合.md

### `ShowSubmobjectsOneByOne`
```python
ShowSubmobjectsOneByOne(group, int_func=np.ceil, **kwargs)
```
- `ret`: `ShowSubmobjectsOneByOne` instance (`ShowSubmobjectsOneByOne(ShowIncreasingSubsets)`).
- `args`:
  - `group: Iterable[Mobject]` — required; wrapped into `Group`.
  - `int_func: Callable = np.ceil`.
- `notes`: **not in RTM's export list**; import from top-level `real_time_manim` (bundled CE), verified playable. Opposite of `ShowIncreasingSubsets`: only one submobject visible at a time, previous auto-hidden. Ctor also sets submobjects to 0 → `self.add` first.
- `see`: ../zh_CN/03-动画/创建与擦除/03-逐个显示与集合.md

### `SpiralIn`
```python
SpiralIn(shapes, scale_factor=8, fade_in_fraction=0.3, **kwargs)
```
- `ret`: `SpiralIn` instance (`Animation`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `shapes` | `Mobject` | — (required) | container; **each submobject flies in individually** |
| `scale_factor` | `float` | `8` | start-radius multiplier around the whole center |
| `fade_in_fraction` | `float` | `0.3` | leading progress fraction used to fade in |
| `introducer` | `bool` | `False` | RTM-own passable |

- `notes`: **ctor immediately moves submobjects to the spiral start** → do **not** `self.add(shapes)` beforehand.
- `see`: ../zh_CN/03-动画/创建与擦除/03-逐个显示与集合.md

## matching transforms

Shared mismatch rule (`TransformMatchingShapes`/`Tex`/`AbstractBase`): `transform_mismatches=True` → `Transform`; `fade_transform_mismatches=True` → `FadeTransformPieces`; both `False` (default) → source part `FadeOut` toward target, target part `FadeIn` toward source.

### `TransformMatchingShapes`
```python
TransformMatchingShapes(mobject, target_mobject, transform_mismatches=False,
                        fade_transform_mismatches=False, key_map=None, **kwargs)
```
- `ret`: `TransformMatchingShapes` instance.
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — | source (removed on finish, target takes over) |
| `target_mobject` | `Mobject` | — | target (added on finish) |
| `transform_mismatches` | `bool` | `False` | force `Transform` for mismatched parts |
| `fade_transform_mismatches` | `bool` | `False` | use `FadeTransformPieces` for mismatched parts |
| `key_map` | `dict \| None` | `None` | manual pairing `{src_key: target_key}` |
| `**kwargs` | … | — | forwarded to each sub-transform (e.g. `path_arc=PI/2`) + `Animation` params |

- `notes`: matches by **shape**. Normalizes point-bearing submobjects (center to origin, height 1, 3-decimal coords) then hashes. Keys computed with `TransformMatchingShapes.get_mobject_key(part)` (src key → target key, don't reverse). `self.add(src)` first.
- `see`: ../zh_CN/03-动画/匹配变换/01-匹配变换.md

### `TransformMatchingTex`
```python
TransformMatchingTex(mobject, target_mobject, transform_mismatches=False,
                     fade_transform_mismatches=False, key_map=None, **kwargs)
```
- `ret`: `TransformMatchingTex` instance.
- `args`: same table as `TransformMatchingShapes`.
- `notes`: matches by LaTeX fragment `tex_string`; recurses into `Group`/`VGroup` to the parts that carry `tex_string`. Key = `get_mobject_key` → the part's `tex_string`.
- `see`: ../zh_CN/03-动画/匹配变换/01-匹配变换.md

### `TransformMatchingAbstractBase`
```python
TransformMatchingAbstractBase(mobject, target_mobject, transform_mismatches=False,
                              fade_transform_mismatches=False, key_map=None, **kwargs)
```
- `ret`: base instance (**not directly playable**).
- `args`: same table as `TransformMatchingShapes`.
- `notes`: abstract base of the two classes above; defines static hooks `get_mobject_parts` (split) and `get_mobject_key` (key). Direct instantiation raises at hook call. Subclass it only for custom matching (e.g. by text content / custom attribute).
- `errs`: `NotImplementedError` — `get_mobject_key` on the abstract base.
- `see`: ../zh_CN/03-动画/匹配变换/01-匹配变换.md

### `TransformMatchingStrings` — does not exist
- `notes`: the "match by string" capability is covered by `TransformMatchingTex` (`tex_string`). Direct import fails:
```text
ImportError: cannot import name 'TransformMatchingStrings' from 'manim'
(C:\...\Lib\site-packages\manim\__init__.py). Did you mean: 'TransformMatchingShapes'?
```
- `see`: ../zh_CN/03-动画/匹配变换/01-匹配变换.md

## core transforms

### `Transform`
```python
Transform(mobject, target_mobject, path_func=None, path_arc=0, path_arc_axis=None,
          path_arc_centers=None, replace_mobject_with_target_in_scene=False, **kwargs)
```
- `ret`: `Transform` instance (`Transform(Animation)`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | source (mutated in place) |
| `target_mobject` | `Mobject` | — (**required, no default**) | RTM-own must be passed explicitly |
| `path_func` | `Callable \| None` | `None` | `(start_pts, end_pts, alpha) -> pts` |
| `path_arc` | `float` | `0` | arc angle (rad); `>0` counterclockwise |
| `path_arc_axis` | `np.ndarray \| None` | `None` (→`OUT`) | arc axis (3D); `None` handled as `[0,0,1]` |
| `path_arc_centers` | `Point3DLike \| None` | `None` | arc centers; with no `path_func` auto-generates `path_along_circles` |
| `replace_mobject_with_target_in_scene` | `bool` | `False` | `True` = leave target in scene on finish |
| `**kwargs` | … | — | `Animation` (`run_time`, `rate_func`…) |

- `notes`: point-set interpolation; on finish `mobject` stays in scene already looking like target; `target_mobject` is not added by default.
- `see`: ../zh_CN/03-动画/变换/01-Transform核心.md

### `ReplacementTransform`
```python
ReplacementTransform(mobject, target_mobject, **kwargs)
```
- `ret`: `ReplacementTransform` instance (`ReplacementTransform(Transform)`).
- `args`:
  - `mobject: Mobject` — required.
  - `target_mobject: Mobject` — required.
  - `**kwargs` — forwarded to `Transform`; explicit `replace_mobject_with_target_in_scene` overrides the fixed `True`.
- `notes`: same transform, but pins `replace_mobject_with_target_in_scene=True`: source disappears, target takes over the scene.
- `see`: ../zh_CN/03-动画/变换/01-Transform核心.md

### `MoveToTarget`
```python
MoveToTarget(mobject, **kwargs)
```
- `ret`: `MoveToTarget` instance (`MoveToTarget(Transform)`).
- `args`: `mobject: Mobject` — required; must `generate_target()` and edit `mobject.target` first.
- `notes`: transforms `mobject` into `mobject.target` (sugar of `.animate`). Missing `target`: CE raises `ValueError` at construction; RTM-own checks `hasattr(mobject, "target")` and `Mobject` has a `None`-valued `.target`, so construction passes but `begin` raises. Always `generate_target()` first.
- `errs`:
  - `ValueError: ...` — ManimCE, no `target`.
  - `AttributeError: 'NoneType' object has no attribute 'copy'` — RTM-own, `begin` with no `generate_target()`.
- `see`: ../zh_CN/03-动画/变换/01-Transform核心.md

## method / function driven transforms

### `ApplyMethod`
```python
ApplyMethod(method, *args, **kwargs)
```
- `ret`: `ApplyMethod` instance (`ApplyMethod(Transform)`).
- `args`:
  - `method: Callable` (bound method) — required, e.g. `sq.shift`, `sq.set_color`, `sq.rotate`.
  - `*args` — positional args; **a trailing `dict`** is treated as the method's keyword args.
  - `**kwargs` — forwarded to `Transform`/`Animation`.
- `notes`: **not in RTM's export list**; import from top-level `real_time_manim` (bundled CE), verified playable. Must pass a bound method that returns a mobject.
- `errs`: `ValueError: ...` — passed an already-called result (`sq.shift(RIGHT)`) instead of the bound method (`sq.shift`).
- `see`: ../zh_CN/03-动画/变换/02-方法与函数驱动.md

### `ApplyFunction`
```python
ApplyFunction(function, mobject, **kwargs)
```
- `ret`: `ApplyFunction` instance (`ApplyFunction(Transform)`).
- `args`:
  - `function: Callable[[Mobject], Mobject]` — required; receives a copy, returns a new mobject.
  - `mobject: Mobject` — required.
- `notes`: not in RTM's export list (top-level import).
- `errs`: `TypeError: ...` — `function` returns a non-`Mobject`.
- `see`: ../zh_CN/03-动画/变换/02-方法与函数驱动.md

### `ApplyPointwiseFunction`
```python
ApplyPointwiseFunction(function, mobject, run_time=3.0, **kwargs)
```
- `ret`: `ApplyPointwiseFunction` instance (`ApplyPointwiseFunction(ApplyMethod) ← Transform`).
- `args`:
  - `function: Callable[[np.ndarray], np.ndarray]` — required; coord → coord.
  - `mobject: Mobject` — required.
  - `run_time: float = 3.0` — constant `DEFAULT_POINTWISE_FUNCTION_RUN_TIME`; much longer than others.
- `notes`: applies the function to every point (internal `mobject.apply_function`).
- `see`: ../zh_CN/03-动画/变换/02-方法与函数驱动.md

### `ApplyPointwiseFunctionToCenter`
```python
ApplyPointwiseFunctionToCenter(function, mobject, **kwargs)
```
- `ret`: `ApplyPointwiseFunctionToCenter` instance (`ApplyPointwiseFunctionToCenter(ApplyPointwiseFunction)`).
- `args`:
  - `function: Callable[[np.ndarray], np.ndarray]` — required; center → new center.
  - `mobject: Mobject` — required.
  - `**kwargs` — includes `run_time=3.0`.
- `notes`: applies the function to the **center only**, then `move_to`s the whole object. Not in RTM's export list (top-level import). ManimCE 0.21 ctor has an upstream bug (`super().__init__` omits `mobject` → `TypeError`); RTM fixes it when `real_time_manim.compat` is imported.
- `see`: ../zh_CN/03-动画/变换/02b-更多函数驱动.md

### `ApplyComplexFunction`
```python
ApplyComplexFunction(function, mobject, **kwargs)
```
- `ret`: `ApplyComplexFunction` instance (`ApplyComplexFunction(ApplyMethod) ← Transform`).
- `args`:
  - `function: Callable[[complex], complex]` — required.
  - `mobject: Mobject` — required.
- `notes`: applies `z -> f(z)` to every point (internal `mobject.apply_complex_function`); auto-sets the rotation path arc from `log(f(1)).imag`. Not in RTM's export list (top-level import).
- `see`: ../zh_CN/03-动画/变换/02b-更多函数驱动.md

### `ApplyMatrix`
```python
ApplyMatrix(matrix, mobject, about_point=ORIGIN, **kwargs)
```
- `ret`: `ApplyMatrix` instance (`ApplyMatrix(ApplyPointwiseFunction)`).
- `args`:
  - `matrix: np.ndarray \| list` — required; `2×2` or `3×3`.
  - `mobject: Mobject` — required.
  - `about_point: np.ndarray = ORIGIN` — transform origin.
  - `**kwargs` — includes `run_time=3.0`.
- `notes`: `p' = (p - about_point) @ matrix.T + about_point`. `2×2` auto-padded to `3×3`. Not in RTM's export list (top-level import).
- `errs`: `ValueError: "Matrix has bad dimensions"` — matrix not 2×2 / 3×3.
- `see`: ../zh_CN/03-动画/变换/02b-更多函数驱动.md

## state / style transforms

### `Restore`
```python
Restore(mobject, **kwargs)
```
- `ret`: `Restore` instance (`Restore(ApplyMethod) ← Transform`).
- `args`: `mobject: Mobject` — required; must have called `save_state()` beforehand (else restores the default state).
- `notes`: restores position/size/color/opacity of the **most recent** `save_state()` snapshot. Not in RTM's export list (top-level import), verified playable.
- `see`: ../zh_CN/03-动画/变换/03-状态保存与样式变换.md

### `ScaleInPlace`
```python
ScaleInPlace(mobject, scale_factor, **kwargs)
```
- `ret`: `ScaleInPlace` instance (`ScaleInPlace(ApplyMethod) ← Transform`).
- `args`:
  - `mobject: Mobject` — required.
  - `scale_factor: float` — required; scale multiplier.
- `notes`: equivalent to `ApplyMethod(m.scale, factor)`. Not in RTM's export list (top-level import).
- `see`: ../zh_CN/03-动画/变换/03-状态保存与样式变换.md

### `ShrinkToCenter`
```python
ShrinkToCenter(mobject, **kwargs)
```
- `ret`: `ShrinkToCenter` instance (`ShrinkToCenter(ScaleInPlace) ← ApplyMethod ← Transform`).
- `args`: `mobject: Mobject` — required.
- `notes`: shrinks to 0 (points → 0, invisible). **Not a remover** — stays in the scene; `self.remove(m)` or use `FadeOut`/`Uncreate` to actually remove. Not in RTM's export list (top-level import).
- `see`: ../zh_CN/03-动画/变换/03b-收缩与变色.md

### `FadeToColor`
```python
FadeToColor(mobject, color, **kwargs)
```
- `ret`: `FadeToColor` instance (`FadeToColor(ApplyMethod) ← Transform`).
- `args`:
  - `mobject: Mobject` — required.
  - `color: str \| ManimColor` — required; target color.
- `notes`: gradient (not instant) color change; equivalent to `ApplyMethod(m.set_color, color)`. Not in RTM's export list (top-level import).
- `see`: ../zh_CN/03-动画/变换/03b-收缩与变色.md

## positional / copy transforms

### `TransformFromCopy`
```python
TransformFromCopy(mobject, target_mobject, **kwargs)
```
- `ret`: `TransformFromCopy` instance (`TransformFromCopy(Transform)`).
- `args`:
  - `mobject: Mobject` — required; source, **stays unchanged**.
  - `target_mobject: Mobject` — required; added and transformed.
- `notes`: keeps the source fixed, aligns `target_mobject` to it first, then interpolates back to its own shape/position. Target is auto-added to the scene. Not in RTM's export list (top-level import).
- `see`: ../zh_CN/03-动画/变换/04-位置互换与复制式变换.md

### `ClockwiseTransform`
```python
ClockwiseTransform(mobject, target_mobject, path_arc=-np.pi, **kwargs)
```
- `ret`: `ClockwiseTransform` instance (`Transform` subclass).
- `args`:
  - `mobject: Mobject` — required.
  - `target_mobject: Mobject` — required.
  - `path_arc: float = -np.pi` — change to alter the arc.
  - `**kwargs` — `Transform`/`Animation` params.
- `notes`: forces points along a clockwise semicircle. Not in RTM's export list (top-level import).
- `see`: ../zh_CN/03-动画/变换/04-位置互换与复制式变换.md

### `CounterclockwiseTransform`
```python
CounterclockwiseTransform(mobject, target_mobject, path_arc=np.pi, **kwargs)
```
- `ret`: `CounterclockwiseTransform` instance (`Transform` subclass).
- `args`: same as `ClockwiseTransform`, but `path_arc: float = np.pi`.
- `notes`: counterclockwise semicircle; same params as `ClockwiseTransform`, only the `path_arc` default differs. Not in RTM's export list (top-level import).
- `see`: ../zh_CN/03-动画/变换/04-位置互换与复制式变换.md

### `CyclicReplace`
```python
CyclicReplace(*mobjects, path_arc=90 * DEGREES, **kwargs)
```
- `ret`: `CyclicReplace` instance (`CyclicReplace(Transform)`).
- `args`:
  - `*mobjects: Group \| VGroup \| Mobject…` — required; a single `Group` is used as-is, else `Group(*mobjects)`.
  - `path_arc: float = 90 * DEGREES` — rotation arc angle.
- `notes`: rotates objects into each other's slots (1st→2nd, …, last→1st). Not in RTM's export list (top-level import).
- `see`: ../zh_CN/03-动画/变换/04-位置互换与复制式变换.md

### `Swap`
```python
Swap(*mobjects, path_arc=90 * DEGREES, **kwargs)
```
- `ret`: `Swap` instance (`Swap(CyclicReplace)`).
- `args`: same as `CyclicReplace`.
- `notes`: no own ctor — just a clearer name for `CyclicReplace` (2 objects = a positional swap). Not in RTM's export list (top-level import).
- `see`: ../zh_CN/03-动画/变换/04-位置互换与复制式变换.md

## fade transforms

### `FadeTransform`
```python
FadeTransform(mobject, target_mobject, stretch=True, dim_to_match=1, **kwargs)
```
- `ret`: `FadeTransform` instance (`FadeTransform(Transform)`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | source (restored + removed on finish) |
| `target_mobject` | `Mobject` | — (required) | target (added on finish) |
| `stretch` | `bool` | `True` | stretch target to source size |
| `dim_to_match` | `int` | `1` | when `stretch=False`: `0/1/2` = match x/y/z length |

- `notes`: source fades out while target fades in; target is stretched/scaled to the source size then restored. RTM-own implementation (import from `real_time_manim.vulkan_bind`).
- `see`: ../zh_CN/03-动画/变换/05-淡出淡入式变换.md

### `FadeTransformPieces`
```python
FadeTransformPieces(mobject, target_mobject, stretch=True, dim_to_match=1, **kwargs)
```
- `ret`: `FadeTransformPieces` instance (RTM-own `AnimationGroup`).
- `args`: same table as `FadeTransform`.
- `notes`: like `FadeTransform` but pairs **subobject by subobject** (ctor first `align_submobjects`s the two). Since 2026-10-16 the ctor accepts `run_time=` (`AnimationGroup` gained `run_time=`/`group=`), so `run_time`/`rate_func` may be passed at the constructor or at play level. RTM-own implementation.
- `see`: ../zh_CN/03-动画/变换/05-淡出淡入式变换.md

### `TransformAnimations`
```python
TransformAnimations(start_anim, end_anim, rate_func=squish_rate_func(smooth), **kwargs)
```
- `ret`: `TransformAnimations` instance (`TransformAnimations(Transform)`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `start_anim` | `Animation` | — (required) | start animation |
| `end_anim` | `Animation` | — (required) | end animation |
| `rate_func` | `Callable` | `squish_rate_func(smooth)` | squeezes progress into the middle |
| `run_time` | `float` | `max(start.run_time, end.run_time)` | auto when not passed |

- `notes`: interpolates **two animations themselves** (runs both, cross-transforms their mobject points). Source marks `TODO, this may be deprecated`; prefer `AnimationGroup` + `lag_ratio` or `Succession`. **ManimCE-native** (RTM does not rewrite it; exported with `real_time_manim`); its sub-animations must be native (need `set_run_time`/`starting_mobject`) — import those as aliases.
- `see`: ../zh_CN/03-动画/变换/05-淡出淡入式变换.md

## emphasis

### `Indicate`
```python
Indicate(mobject, scale_factor=1.2, color=PURE_YELLOW, rate_func=there_and_back, **kwargs)
```
- `ret`: `Indicate` instance (RTM-own `Indicate(Animation)`; **not** a `Transform` subclass).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | highlighted object |
| `scale_factor` | `float` | `1.2` | temporary scale-up |
| `color` | `ParsableManimColor` | `PURE_YELLOW` | highlight color (original restored on finish). RTM-own default is manim `YELLOW` (`#F7D96F`); CE is `PURE_YELLOW` — pass a value to be identical |
| `rate_func` | `RateFunction` | `there_and_back` | go-and-return curve; keep a round-trip curve or the object stops scaled/tinted |
| `run_time` | `float` | `1.0` | RTM-own `run_time` is dropped in the ctor (`Indicate(sq, run_time=3)` is ineffective); set duration at **play level** (`win.play(Indicate(...), run_time=1.4)`) |
| `**kwargs` | … | — | `Animation` params; `path_arc` etc. are swallowed (not a `Transform`) |

- `eg`:
```python
win.play(Indicate(Tex("Indicate").scale(3)))
```
- `see`: ../zh_CN/03-动画/强调与提示/01-强调与闪烁.md

### `Flash`
```python
Flash(point, line_length=0.2, num_lines=12, flash_radius=0.1, line_stroke_width=3,
      color=PURE_YELLOW, time_width=1, run_time=1.0, **kwargs)
```
- `ret`: `Flash` instance (`Flash(AnimationGroup)`); each line is a `ShowPassingFlash`.
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `point` | `Point3DLike \| Mobject` | — (required) | flash center (mobject → its center) |
| `line_length` | `float` | `0.2` | per-line length |
| `num_lines` | `int` | `12` | number of lines |
| `flash_radius` | `float` | `0.1` | start distance from center |
| `line_stroke_width` | `int` | `3` | line width |
| `color` | `ParsableManimColor` | `PURE_YELLOW` | line color |
| `time_width` | `float` | `1` | beam width passed to `ShowPassingFlash` |
| `run_time` | `float` | `1.0` | duration |
| `**kwargs` | … | — | stored as `animation_config`, forwarded to each line's `ShowPassingFlash` (e.g. `rate_func=rush_from`) |

- `notes`: ManimCE class (top-level import).
- `eg`:
```python
win.play(Flash(Dot(color=PURE_YELLOW).shift(DOWN), num_lines=30, color=RED))
```
- `see`: ../zh_CN/03-动画/强调与提示/01-强调与闪烁.md

### `Blink`
```python
Blink(mobject, time_on=0.5, time_off=0.5, blinks=1, hide_at_end=False, **kwargs)
```
- `ret`: `Blink` instance (`Blink(Succession) ← AnimationGroup ← Animation`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | blinking object |
| `time_on` | `float` | `0.5` | visible time per blink |
| `time_off` | `float` | `0.5` | hidden time per blink |
| `blinks` | `int` | `1` | number of blinks |
| `hide_at_end` | `bool` | `False` | `True` = stay hidden at end |
| `run_time` | `float` | computed | ctor pops & discards `run_time`: actual duration is always `blinks × (time_on + time_off)` (`+ time_on` when `hide_at_end=False`) |
| `**kwargs` | … | — | forwarded to internal `Succession` |

- `notes`: does **not** introduce the object — `self.add(txt)` first or nothing blinks.
- `eg`:
```python
win.play(Blink(Text("Blinking").scale(1.5), blinks=3))
```
- `see`: ../zh_CN/03-动画/强调与提示/01-强调与闪烁.md

### `ShowPassingFlash`
```python
ShowPassingFlash(mobject, time_width=0.1, run_time=1.0, remover=True, **kwargs)
```
- `ret`: `ShowPassingFlash` instance (RTM-own `Animation`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `mobject` | `VMobject` | — (required) | swept vector object |
| `time_width` | `float` | `0.1` | beam length as fraction of the stroke (`1` = full, `2` = double) |
| `run_time` | `float` | `1.0` | duration |
| `remover` | `bool` | `True` | remove on finish. Since 2026-10-16 explicitly passable `False` → stays in scene and restores the full stroke (`_restore_full_stroke`) |

- `notes`: each frame shows only a sliding beam segment, not a growing reveal.
- `eg`:
```python
win.play(ShowPassingFlash(RegularPolygon(5, color=DARK_GRAY).scale(2), time_width=0.5))
```
- `see`: ../zh_CN/03-动画/强调与提示/01b-扫光与波纹.md

### `ShowPassingFlashWithThinningStrokeWidth`
```python
ShowPassingFlashWithThinningStrokeWidth(vmobject, n_segments=10, time_width=0.1, remover=True, **kwargs)
```
- `ret`: instance (`ShowPassingFlashWithThinningStrokeWidth(AnimationGroup)`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `vmobject` | `VMobject` | — (required) | swept vector object |
| `n_segments` | `int` | `10` | segment count |
| `time_width` | `float` | `0.1` | starting beam width |
| `remover` | `bool` | `True` | remove on finish |
| `**kwargs` | … | — | forwarded to each `ShowPassingFlash` (`time_width` popped first) |

- `notes`: overlays `n_segments` decreasing-width `ShowPassingFlash`es for a "thinning comet tail". **No docstring** (derived from source). Not in RTM's export list (top-level import).
- `eg`:
```python
win.play(ShowPassingFlashWithThinningStrokeWidth(Circle(stroke_width=8), run_time=2))
```
- `see`: ../zh_CN/03-动画/强调与提示/01b-扫光与波纹.md

### `ApplyWave`
```python
ApplyWave(mobject, direction=UP, amplitude=0.2, wave_func=smooth, time_width=1,
          ripples=1, run_time=2, **kwargs)
```
- `ret`: `ApplyWave` instance (RTM-own `Animation`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | disturbed object |
| `direction` | `Vector3DLike` | `UP` | push direction (normalized) |
| `amplitude` | `float` | `0.2` | max displacement |
| `wave_func` | `RateFunction` | `smooth` | single-peak shape |
| `time_width` | `float` | `1` | wavelength as fraction of object width |
| `ripples` | `int` | `1` | number of wave crests |
| `run_time` | `float` | `2` | duration |

- `notes`: a ripple crosses the object; the shape fully restores at the end. RTM-own `ApplyWave` has **no `apply_function_kwargs`** (not a `Homotopy` subclass; swallowed by `**kwargs`). `time_width`/`ripples` are relative to object **width**.
- `eg`:
```python
win.play(ApplyWave(Tex("WaveWaveWave").scale(2), ripples=3, amplitude=0.3))
```
- `see`: ../zh_CN/03-动画/强调与提示/01b-扫光与波纹.md

### `Circumscribe`
```python
Circumscribe(mobject, shape=Rectangle, fade_in=False, fade_out=False, time_width=0.3,
             buff=SMALL_BUFF, color=PURE_YELLOW, run_time=1, stroke_width=DEFAULT_STROKE_WIDTH, **kwargs)
```
- `ret`: `Circumscribe` instance (`Circumscribe(Succession) ← AnimationGroup ← Animation`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | circled object |
| `shape` | `type[Rectangle] \| type[Circle]` | `Rectangle` | frame **class** (not instance) |
| `fade_in` | `bool` | `False` | frame fades in (also reverses draw direction) |
| `fade_out` | `bool` | `False` | frame fades out |
| `time_width` | `float` | `0.3` (sentinel) | explicit value → non-fade branch uses `ShowPassingFlash` beam semantics; unset → legacy `Create` draw; `fade_in`/`fade_out` branches **ignore** it |
| `buff` | `float` | `SMALL_BUFF` | gap between frame and object |
| `color` | `ParsableManimColor` | `PURE_YELLOW` | frame color. RTM-own default is written `None`, falls back to manim `YELLOW` |
| `run_time` | `float` | `1` | total (fade mode splits it in two) |
| `stroke_width` | `float` | `DEFAULT_STROKE_WIDTH (=4)` | frame line width |

- `notes`:
  - `shape` validation differs: **CE** accepts only `Rectangle`/`Circle`, else `ValueError("shape should be either Rectangle or Circle.")`; **RTM-own does not error** — `Rectangle` → `SurroundingRectangle`, everything else silently drawn as `Circle`.
  - `Circumscribe.mobject` is `None` (does not carry the circled text) → `self.add(lbl)` the label yourself; the internal `_frame` is auto-presented by the play layer since 2026-10-16, so `self.add(cs._frame)` is idempotent; `clean_up_from_scene` removes `_frame`.
- `eg`:
```python
lbl = Tex("Circumscribe").scale(2)
win.play(Circumscribe(lbl, Circle, fade_out=True))
```
- `see`: ../zh_CN/03-动画/强调与提示/02-圈注与聚焦.md

### `FocusOn`
```python
FocusOn(focus_point, opacity=0.2, color=GREY, run_time=2, **kwargs)
```
- `ret`: `FocusOn` instance (`FocusOn(Transform)`).
- `args`:
  - `focus_point: Point3DLike \| Mobject` — required; mobject → its center.
  - `opacity: float = 0.2` — final spot opacity.
  - `color: ParsableManimColor = GREY`.
  - `run_time: float = 2`.
- `notes`: a big spotlight (radius = frame radius) shrinks onto the point; `remover=True`, so no extra `FadeOut`. Not in RTM's export list (top-level import).
- `eg`:
```python
win.play(FocusOn(Dot(color=PURE_YELLOW).shift(DOWN)))
```
- `see`: ../zh_CN/03-动画/强调与提示/02-圈注与聚焦.md

### `Wiggle`
```python
Wiggle(mobject, scale_value=1.1, rotation_angle=0.01 * TAU, n_wiggles=6,
       scale_about_point=None, rotate_about_point=None, run_time=2, **kwargs)
```
- `ret`: `Wiggle` instance (`Wiggle(Animation)`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `mobject` | `Mobject` | — (required) | wiggled object |
| `scale_value` | `float` | `1.1` | temporary scale-up |
| `rotation_angle` | `float` | `0.01*TAU (=3.6°)` | per-wiggle angle |
| `n_wiggles` | `int` | `6` | number of wiggles |
| `scale_about_point` | `Point3DLike \| None` | `None` | scale origin (`None` = object center) |
| `rotate_about_point` | `Point3DLike \| None` | `None` | rotate origin (`None` = object center) |
| `run_time` | `float` | `2` | duration |

- `notes`: small in-place scale + left-right swing `n_wiggles` times, then restores (uses the `wiggle` rate func). Differs from `ApplyWave`: `Wiggle` swings the whole object, `ApplyWave` propagates a wave inside it. Not in RTM's export list (top-level import).
- `eg`:
```python
win.play(Wiggle(Tex("Wiggle").scale(3)))
```
- `see`: ../zh_CN/03-动画/强调与提示/02-圈注与聚焦.md

## grow

Family semantics (RTM-own): grows from 0 size at a given point, optionally setting the start color to `point_color`. Chain `GrowFromPoint(GrowArrow) ← GrowArrow(Animation)`. RTM-own Grow family is **not** a `Transform` subclass: `path_arc`/`path_func` are swallowed by `**kwargs` and have no effect — use `Transform`/`MoveAlongPath` for a custom path.

### `GrowFromPoint`
```python
GrowFromPoint(mobject, point, point_color=None, **kwargs)
```
- `ret`: `GrowFromPoint` instance.
- `args`:
  - `mobject: Mobject` — required.
  - `point: Point3DLike` — required; growth origin (coord array like `ORIGIN`, or a mobject → its center).
  - `point_color: ParsableManimColor \| None = None` — start color; `None` = object's own color.
- `notes`: generic form (scales 0 and `move_to(point)` at start).
- `see`: ../zh_CN/03-动画/生长出现/01-Grow家族.md

### `GrowFromCenter`
```python
GrowFromCenter(mobject, point_color=None, **kwargs)
```
- `ret`: `GrowFromCenter` instance.
- `args`:
  - `mobject: Mobject` — required.
  - `point_color: ParsableManimColor \| None = None`.
- `notes`: grows from the object's own center (most common reveal).
- `see`: ../zh_CN/03-动画/生长出现/01-Grow家族.md

### `GrowFromEdge`
```python
GrowFromEdge(mobject, edge, point_color=None, **kwargs)
```
- `ret`: `GrowFromEdge` instance.
- `args`:
  - `mobject: Mobject` — required.
  - `edge: Vector3DLike` — required; e.g. `DOWN`/`RIGHT`/`UR`.
  - `point_color: ParsableManimColor \| None = None`.
- `notes`: grows from a critical point of the bounding box in the `edge` direction.
- `see`: ../zh_CN/03-动画/生长出现/01-Grow家族.md

### `GrowArrow`
```python
GrowArrow(arrow, point_color=None, **kwargs)
```
- `ret`: `GrowArrow` instance (`GrowArrow(Animation)`).
- `args`:
  - `arrow: Arrow` — required.
  - `point_color: ParsableManimColor \| None = None`.
- `notes`: grows from `arrow.get_start()` toward the tip (render-channel `_grow_scale`/`_grow_point`), so the tip always grows toward the target. Non-`Transform`, no `path_func`.
- `see`: ../zh_CN/03-动画/生长出现/01b-箭头与旋入.md

### `SpinInFromNothing`
```python
SpinInFromNothing(mobject, angle=PI / 2, point_color=None, **kwargs)
```
- `ret`: `SpinInFromNothing` instance (`SpinInFromNothing(GrowFromCenter) ← GrowArrow(Animation)`).
- `args`:
  - `mobject: Mobject` — required.
  - `angle: float = PI / 2` — extra total rotation while growing (`2*PI` = full turn).
  - `point_color: ParsableManimColor \| None = None`.
- `notes`: RTM writes `_grow_rot = angle * alpha` to the renderer (not a path function). RTM-own has **no `path_func` param at all** (CE uses `spiral_path(angle)`); `angle` only affects the growth spin, not the final pose.
- `see`: ../zh_CN/03-动画/生长出现/01b-箭头与旋入.md

## fade

### `FadeIn`
```python
FadeIn(*mobjects, shift=None, target_position=None, scale=1, **kwargs)
```
- `ret`: `FadeIn` instance (RTM-own `FadeIn(Animation)`; source `FadeIn.__init__(self, *mobjects, shift=None, target_position=None, scale=1.0, run_time=1.0, **kwargs)`).
- `args`:

| name | type | default | meaning |
| --- | --- | --- | --- |
| `*mobjects` | `Mobject` | — (required) | ≥1; >1 wrapped in `Group`. CE raises `ValueError("At least one mobject must be passed.")` on empty; RTM-own does not error (nothing to animate) |
| `shift` | `np.ndarray \| None` | `None` | fade-in displacement (enters from `-shift`); `None` + no `target_position` → `ORIGIN` (opacity only) |
| `target_position` | `np.ndarray \| Mobject \| None` | `None` | start position; mobject → its center, auto-computes `shift = target_position - mobject.get_center()` |
| `scale` | `float` | `1` | start scale (grows back to full while fading). Since 2026-10-16 also effective on **leaf VMobjects** (`Circle`/`Square`/`Dot`) |
| `introducer` | `bool` | `False` | RTM-own not pinned, passable |

- `notes`: `Animation` params (`run_time=1.0`, `rate_func=smooth`, `lag_ratio=0`, `name`, `suspend_mobject_updating`, `reverse_rate_function`, `use_override`). RTM-own `FadeIn` is **not** a `Transform` subclass → no `path_arc`/`path_func` (swallowed). CE pins `introducer=True` in the ctor → passing it there raises `TypeError`; RTM-own allows it.
- `see`: ../zh_CN/03-动画/淡入淡出/01-Fade家族.md

### `FadeOut`
```python
FadeOut(*mobjects, shift=None, target_position=None, scale=1, **kwargs)
```
- `ret`: `FadeOut` instance (RTM-own `FadeOut(Animation)`; source `FadeOut.__init__(self, *mobjects, shift=None, target_position=None, scale=1.0, run_time=1.0, **kwargs)`).
- `args`: same as `FadeIn` (`shift`/`target_position`/`scale`), with `remover` **fixed `True`**.
- `notes`:
  - Fades to invisible and auto-removes from the scene. RTM-own pins `self.remover = True` after `super().__init__`, so `remover=False` is overwritten.
  - `shift=UP*2` gives a "drift away"; `target_position=other` fades toward another object.
  - RTM-own has a private `_park_opacity(mob, value)` (parks animated opacity on the paint-walk node) — only subclasses that detach-wrap need to override it.
- `see`: ../zh_CN/03-动画/淡入淡出/01-Fade家族.md
