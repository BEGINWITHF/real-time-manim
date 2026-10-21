# gotchas & error catalog

> scope: cross-domain pitfalls, RTM-vs-ManimCE deviations, "allowed but discouraged" and "unwired/no-op" items, and an exact error→cause→fix table. Read after the domain file, before writing code.
> src: condensed from `agent/{runtime,scene-camera,mobject,animation-transform,animation-motion,geometry,text,coords-charts,three-d,graph-vector,utils}.md`; site-wide `提醒`/`无法演示`/`不支持` under `../zh_CN/`. Every error string below is verbatim from those files — none invented.

---

## Global / RTM-vs-CE

- **No `manim` CLI.** `real_time_manim` is a pip library + Python API; `manim/cli/`, `__main__.py` and the console script are removed. `manim cfg` / `init` / `plugins -l` / `checkhealth` all unsupported. Entry points are `fast_record_scene` / `record_scene` / `MLWindow` / `FrameServer` / `FramePreview`.
- **Fixed output 1920×1080 @ 60 fps.** Any other size prints `[rtm] forcing 1920x1080: ...`; any other fps prints `[rtm] forcing 60 fps: ...`. Constants: `MLWindow.SUPPORTED_WIDTH=1920`, `SUPPORTED_HEIGHT=1080`, `SUPPORTED_FPS=60`. No config key changes this.
- **`win.scene = self` is required** before `win.play(...)`; without it `play()` raises. RTM runs `Scene.setup()` → `construct()` → `tear_down()` itself and **never calls `Scene.render()`**.
- **`win.close()` is required** at the end of `construct()`; otherwise nothing is flushed and the run may not exit. `close()` alone does **not** finish a record — `fast_record_scene`/`record_scene` wrap it with `_AutoRecord` (calls `_finish_fast_record()`/`stop_record()` first). If you call `enable_fast_record(...)` manually you must call `win._finish_fast_record()` yourself.
- **One window per process** (native DLL limit; Python serialises via `MLWindow._registry`).
- **Import order matters.** `import real_time_manim` installs its bundled ManimCE `0.21.0` as `sys.modules["manim"]` and re-exports the namespace. Importing `manim` **first** makes RTM use that external copy and may emit `RuntimeWarning` (different class identity). Always `import real_time_manim` first; `from manim import ...` then still works.
- **RTM uses its own `play()`, not `Scene.render()`.** `self.play` is shimmed to forward to the bound window when one exists (`compat.py::_shim_scene_play_uses_window`); `self.play = win.play` remains valid and is the wiki idiom. `self.wait`/`pause`/`wait_until` route through `self.play`.
- **Class identity / monkey patches.** RTM-own classes come from `real_time_manim.vulkan_bind` (or `real_time_manim.animations`); everything else resolves to bundled ManimCE 0.21. RTM patches: `MathTex` Typst auto-route (`window/mathtex.py`), `apply_function` pivot forwarding, `ChangeSpeed` wiring (`window/patches.py`, **not** `compat.py`), `ApplyPointwiseFunctionToCenter` ctor fix, `SmoothedVectorizedHomotopy` missing-import fix. Same-name CE and RTM classes are **not** interchangeable in type checks.
- **Custom-camera fallback = raster.** A camera overriding `capture_mobjects`/`get_frame` (and not `MovingCamera`/`ThreeDCamera`/…) falls back to per-frame full-screen rasterisation (`core.py::_rasterise_custom_camera`) — correct but slow. The whole Cairo pixel API (`capture_mobjects`, `capture_mobject`, `get_image`, `set_background_from_func`, `background_image`, pixel keys) is not wired.
- **`config` is mostly unwired.** Only `background_color` (via `camera.background_color`) is wired; `seed` is indirect; `tex_dir`/`text_dir`/`assets_dir`/`tex_template(_file)` affect intermediates; `renderer` must **NOT** be set. Quality/output/path/window keys do nothing (writing them does not error).
- **Paint order**: document order by default; `z_index` participates when any root has one and `camera.use_z_index`; `ThreeDCamera` re-sorts by camera-space depth; `Camera(use_z_index=False)` disables the z sort.
- **Two drivers**: `win.play(...)` (per-frame) and schedule mode (`_schedule_mode=True`, set by `FrameServer`) where `play()` only records onto a `Timeline`; `build_timeline()`/`render_at(t)` then produce any frame in O(1).
- **Param-table semantics**: `能填` = allowed values; `不建议` = allowed but discouraged; `不接线 / 未接线` = RTM ignores it.

---

## Pitfalls by domain

### Runtime / record / window
- **`win.scene` unset** → `play()` raises `RuntimeError: "win.play() called before the scene was bound..."` → `win.scene = self` inside `construct()`.
- **No `win.close()`** → nothing flushed; `fast_record_scene` raises `RuntimeError: "recorded {n} window(s) but MLWindow.close() was only called {m} time(s)..."`; empty output gives `RuntimeError: "recorded file looks empty/incomplete ({n} bytes)..."` → always `win.close()`.
- **Bare `Mobject` passed to `play()`** → `TypeError: "Unexpected argument {Type} passed to MLWindow.play()..."` → wrap in an animation (`Create`/`FadeIn`) or `Scene.add()` first.
- **Unsupported play-level kwarg** (e.g. play-level `lag_ratio=`) → warning `[RTM] win.play(): unsupported keyword(s) {...} ignored -- RTM 不支持该参数...` → pass it to the animation constructor instead. Honoured keys only: `run_time`, `rate_func`, `path_arc`, `path_arc_axis`, `path_arc_centers`, `path_func`.
- **`run_time <= 0`** → `ValueError` (manim `Scene.validate_run_time`); a positive value under one frame clamps up with a warning.
- **Recording needs `ffmpeg` on PATH** → else `[Record] ffmpeg not found. Install ffmpeg and add it to PATH.` / `[Record] ffmpeg failed: {stderr}` / `[Record] No frames captured, aborting.` / `[FastRecord] ffmpeg failed: {e}`.
- **`overwrite=False` with an existing target** → `FileExistsError: "target already exists: {out_path} (pass overwrite=True to replace it)"` → pass `overwrite=True` or delete the file.
- **`fast_record_scene` with a no-arg callable does NOT call `setup()`** → pass a class/instance if the scene relies on `setup()`.
- **`jobs` parallelisation** only works for an importable single-window `Scene` class with ≥ `_AUTO_MIN_FRAMES=240`; instances/lambdas/function-local classes/no `if __name__ == "__main__"` fall back to one pass. Multi-window, `count_only`, `segment`, `hidden=False` never parallelise. Parallel workers skip per-animation `finish()`/`clean_up_from_scene()` hooks.
- **`record_scene` needs a visible window**; wall-clock capture is not frame-exact — use `fast_record_scene` for frame-exact output.
- **`request_readback()` must precede the `tick()` that draws the wanted frame** (a presented swapchain image is owned by the presentation engine).
- **Schedule/`Timeline` misuse** → `RuntimeError: "cannot add to a finalized Timeline"` / `"Timeline already finalized"` / `"call finalize()/prepare() first"`; stateful animations under `strict=True` → `ValueError: "{Type} is stateful and cannot be evaluated as a pure function of time yet"`.
- **`FrameServer`/`FramePreview`**: `construct()` must open a window (`RuntimeError: "scene did not create an MLWindow"`); bad `controls`/`position` → `ValueError: "controls must be 'input' or 'slider', got {value!r}"` / `"position must be two numbers, got {value!r}"` / `"position must look like '100,200', got {value!r}"`.
- **`next_section` is callable but produces nothing** (no CLI/file-writer); `.srt`/segments need manual ffmpeg cuts.
- **`interactive_embed`/`embed`/`set_key_function` unavailable** (RTM Vulkan window, no embed link).
- **Manual `enable_fast_record` + `close()` does not finish** → call `win._finish_fast_record()`.

### Scene & camera
- **`self.camera.frame` on a plain `Camera`** → `AttributeError` (no `frame`; use `hasattr`). `MovingCameraScene`'s `camera_class` must have a `frame` (not plain `Camera`).
- **Do not write `config.frame_width`/`frame_height`** → CE reads them at camera construction, RTM at imaging time (discouraged). Use `self.camera.frame.animate.set(width=...)`.
- **`MovingCamera.frame_height`/`frame_width` are independent setters** → CE scales per-axis (distortion), RTM scales by height only; assign both in 16:9 or use `frame.animate.set(width=...)`.
- **`Camera` ctor args unreachable**: RTM builds `camera_class()` with no args → use `functools.partial(Camera, ...)` or a subclass overriding defaults.
- **`Camera.frame_center` / pixel args / `frame_rate` discouraged**; `background_opacity` readable/writable but never changes the picture.
- **`ThreeDScene` initial view is head-on** (`phi=0`, `theta=0`); `ambient_camera_rotation` and `default_angled_camera_orientation_kwargs` are stored, not applied (upstream 0.21) → use `begin_ambient_camera_rotation()` / `set_to_default_angled_camera_orientation()`.
- **`SpecialThreeDScene` has 3 upstream bugs** (reads `self.renderer` before `super().__init__()`; default `three_d_axes_config` has removed `tick_frequency`; `get_axes` uses removed `axis.tick_marks`) → see `scene-camera.md` workarounds.
- **`VectorScene.add_plane()` does not set `self.plane`** → assign `self.plane = plane` manually.
- **`lock_in_faded_grid` / `coords_to_vector` / `show_ghost_movement` broken upstream** (also under plain CLI) → for a faded grid: `add_plane(animate=False)` then `plane.set_opacity(0.3)`.
- **`Scene.replace`**: `old_mobject` must be in the scene, `new_mobject` must not → else `ValueError`.
- **`self.wait(...)` (manim `Wait`) leaves an empty `Mobject` in `scene.mobjects`**, inflating `len(self.mobjects)` by 1; `win.play(Wait(...))` does not.
- **`stop_condition` is only honoured during forward play** — not random-access safe; FrameServer/`render_at` renders the full duration.
- **`add_sound` unsupported kwargs** → `[RTM] Scene.add_sound(): unsupported parameter(s) … ignored -- RTM 不支持该参数: the RTM audio mix supports only sound_file, time_offset, gain, gain_to_background.`; `gain` is in **dB**, not a multiplier; the live window plays no audio.
- **`add_subcaption` needs a bound window** → `RuntimeError: "Scene.add_subcaption needs an MLWindow bound to the scene (create one in construct() first, as every RTM scene does)"`.
- **Subcaption clock is the window `_cursor`, not `Scene.time`** (which never advances under RTM).
- **Camera `add_fixed_in_frame_mobjects` does not add to the scene** (the `ThreeDScene` method of the same name does).
- **`ThreeDAxes` `gloss` is an upstream param RTM's Vulkan path does not read** (no visual effect).

### Mobject
- **`VGroup(<non-VMobject>)`** → `TypeError: Only values of type VMobject can be added as submobjects of ...` → use `Group`.
- **`insert` does not de-duplicate** → an already-present object gains a second reference.
- **`set(**kwargs)` has no validation** → a typo is a silent dynamic assignment (no error, no visual change).
- **`generate_points` is a no-op for `Square`/`Triangle`/`Polygon`** (they set points in `__init__`) → `reset_points()` + `generate_points()` will **not** restore their shape.
- **`.animate.rotate(...)` is point-to-point interpolation** (mid frames collapse), not a continuous spin → use `Rotate`/`Rotating`.
- **Extra kwarg to a `VMobject`-based `.rotate`** → `TypeError` (VMobject.rotate has no `**kwargs`).
- **`alpha=` to a vector object's `set_color`** → `TypeError` (VMobject.set_color has no `alpha`).
- **`apply_function` upstream drops `about_point`/`about_edge`** (always origin) — **RTM fixes it** → the two engines render differently; do not rely on it. Coordinates are absolute, so `p * 1.5` pushes the object away from the origin.
- **`interpolate` / `align_points`**: all three mobjects need equal point counts → `align_points` first; `alpha` outside 0–1 is extrapolation (discouraged).
- **`restore()` without a prior `save_state()`** raises; `match_color` overwrites `self.color` (cannot be restored).
- **`lag_ratio=0.3` on a no-submobject object** is ineffective → RTM emits an explicit `UserWarning` (no longer silent).
- **`MultiAnimationOverrideException`** on registering the same animation class twice.
- **`always`/`f_always` `method` must be a bound method** → wrong input raises `AssertionError` from `assert_is_mobject_method`.
- **`ComplexValueTracker` arithmetic unusable on 0.21** (upstream, both engines) → `TypeError: float() argument must be a string or a real number, not 'complex'`; do complex math manually and write back with `set_value`.
- **`get_image`/`show`/`save_image` broken upstream** → `NameError: name 'Camera' is not defined`; get bitmaps from the render pipeline.
- **Base `point_from_proportion`/`proportion_from_point`** → `NotImplementedError`; off-path point → `ValueError: does not lie on this curve`.
- **`arrange_in_grid` overflow** → `ValueError` (not enough cells).
- **Legacy `get_foo()`/`set_foo(v)`** still work but emit `DeprecationWarning`.
- **`VGroup` slice stays `VGroup`; `Group` slice returns `Group`; slices are references, not copies.**

### Animations
- **RTM-own vs CE animation classes differ**: RTM-own `Create`/`Uncreate`/`FadeIn`/`FadeOut`/`Indicate`/`Grow*`/`Rotate`/`Rotating`/`ApplyWave`/`ShowPassingFlash` are **not** `Transform`/`ShowPartial` subclasses → `path_arc`/`path_func` are swallowed. Import RTM-own from `vulkan_bind`.
- **`ShowPartial` is an abstract base — do not play directly** → `NotImplementedError: "Please use Create or ShowPassingFlash"`; missing `pointwise_become_partial` → `TypeError`.
- **`TransformMatchingAbstractBase` not directly playable** → `NotImplementedError` in `get_mobject_key`.
- **`TransformMatchingStrings` does not exist** → `ImportError: cannot import name 'TransformMatchingStrings' from 'manim' ... Did you mean: 'TransformMatchingShapes'?` → use `TransformMatchingTex`.
- **`MoveToTarget` without `generate_target()`** → CE `ValueError` at construction; RTM-own `AttributeError: 'NoneType' object has no attribute 'copy'` in `begin()` → always `generate_target()` first.
- **`ApplyMethod` given an already-called result** (`sq.shift(RIGHT)` instead of `sq.shift`) → `ValueError`.
- **`ApplyFunction` returning a non-`Mobject`** → `TypeError`.
- **`ApplyMatrix` non-2×2/3×3** → `ValueError: "Matrix has bad dimensions"`.
- **`ApplyPointwiseFunctionToCenter` upstream ctor bug** (`super().__init__` omits `mobject` → `TypeError`) → RTM fixes it when `real_time_manim.compat` is imported.
- **`Homotopy`/`ComplexHomotopy` invalid `apply_function_kwargs` key** → `TypeError` (only keys `Mobject.apply_function` accepts).
- **`SmoothedVectorizedHomotopy` non-`VMobject`** → `AssertionError`; pure manim 0.21 → `NameError` (upstream missing import; fixed in RTM `compat.py`).
- **`ChangeSpeed`**: >1 `affects_speed_updaters=True` playing at once → `AssertionError`; `speedinfo` keys are progress fractions (0–1), not seconds.
- **`Wait`/`Scene.wait` with both `stop_condition` and `frozen_frame=True`** → `ValueError`.
- **`AnimationGroup(synchronize_with_wall_clock=True)`** → `ValueError` (explicitly rejected).
- **`AddTextLetterByLetter` empty text** → `ValueError`; only supports `Text`, not `MathTex`.
- **`RemoveTextLetterByLetter` / `UntypeWithCursor`** default `introducer=False` and `clean_up_from_scene` is a no-op → `self.add(...)` first, and they do **not** actually remove from the scene.
- **`AddTextWordByWord` broken upstream** (word splitting empty → static frame) → use `Text` line slicing + `LaggedStart(FadeIn)`.
- **`Blink` does not introduce the object** → `self.add(txt)` first or nothing blinks.
- **`SpiralIn` moves submobjects in the ctor** → do **not** `self.add(shapes)` beforehand. `ShowIncreasingSubsets`/`ShowSubmobjectsOneByOne` `set_opacity(0)` in the ctor → `self.add` first or enter only on `play`.
- **`Indicate(run_time=...)` is dropped in the ctor** → set duration at play level (`win.play(Indicate(...), run_time=1.4)`).
- **`Blink` ctor pops & discards `run_time`** → duration is always `blinks × (time_on + time_off)`.
- **`Unwrite` `remover=True` still leaves the object in the scene** (no own `clean_up_from_scene`); `Unwrite` default `reverse_rate_function=False` (CE default `True`, opposite).
- **`ShrinkToCenter` is not a remover** → `self.remove(m)` or use `FadeOut`/`Uncreate`.
- **`Circumscribe` `shape` validation differs**: CE `ValueError("shape should be either Rectangle or Circle.")`; RTM-own draws anything non-`Rectangle` as `Circle` (no error). `Circumscribe.mobject` is `None` → `self.add(lbl)` yourself.
- **`FadeIn()` with no mobjects** → CE `ValueError("At least one mobject must be passed.")`; RTM-own does not error.
- **`.animate` kwargs after a chained method or twice** → `ValueError`; pass once right after `.animate(...)`.
- **`.animate` `lag_ratio=` on a no-submobject object** → no-op + explicit `UserWarning`.
- **`UpdateFromFunc`/`UpdateFromAlphaFunc` need explicit `run_time`** (else callbacks stop after 1 s); wrong callback arity raises on the first frame.
- **`ChangingDecimal`/`ChangeDecimalToValue` non-`DecimalNumber`** → `TypeError`; both are one-shot.
- **Auto-changing objects (updaters/`always_redraw`/`TracedPath`) only move while scene time advances** → `win.play(Wait(...))`; a bare `self.add(...)` does not animate. `clear_updaters()` before switching sections.
- **`TracedPath`/custom-updater objects are only exact forward** under random access (approximate backwards).
- **RTM `Wait` vs manim `Wait`**: use RTM's from `vulkan_bind`; manim's leaves an empty `Mobject` per wait.
- **Rate-func factories** (`squish_rate_func`, `not_quite_there`) must be **called** → passing the factory itself blows up at runtime. Overshooting rate funcs (`_back`/`_elastic`/`_bounce`, `wiggle`, `there_and_back`) output outside 0–1 → do not drive strict-0–1 properties (`set_opacity`).
- **`Animation.set_default` is class-global** → restore after use; `Indicate`'s RTM default color is manim `YELLOW` (CE `PURE_YELLOW`).

### Geometry
- **`Polygram(p1, p2, ...)`** (single points as separate args) → `IndexError`; each positional arg must be one vertex group → use `Polygon`.
- **`LabeledPolygram` individual points** → `IndexError: too many indices for array: array is 1-dimensional, but 2 were indexed` → pass one full ring per group.
- **`TangentialArc` without `radius`** → `TypeError` (no default).
- **`VDict` indexed by integer** → `KeyError: 2` → it is a dict, use `vd["c"]`.
- **`change_anchor_mode` other than `"smooth"`/`"jagged"`** → `ValueError` (the old `"corners"` is gone).
- **`Angle.get_value()` broken upstream** (no `angle_value`; both engines crash) → read the difference of the two edges' `get_angle()`.
- **`Dot` has no positional location arg** in `AnnotationDot` (first positional is `radius`) → `.move_to(...)`/`.shift(...)`.
- **`Rectangle.grid_xstep`/`grid_ystep` change `submobjects`** (affects `set_color`/`MoveToTarget`/`Create`) → prefer `VGroup(rect, lines)`.
- **`Cutout` holes need the hole's `fill_opacity`** (stroke-only hole is covered by the main fill) → or use `Difference`.
- **`Intersection` of disjoint inputs → empty object** (not a render failure).
- **`Arrow` `buff` default is `0.25`, `Line`'s is `0`**; use `buff=0` for flush tips.
- **`tip=` takes an instance, `tip_shape=` takes a class** (no parens); `get_tip(0)` is wrong (no params).
- **`VMobject` multi-stop gradient fill uses first→last stop** (native linear gradient, not averaged); `background_image` texture fill not wired.

### Text / math / tabular
- **Cold tex cache = a visible pause before the first frame** (not a hang): `MathTex`/`Tex`/`Typst`/`MathTypst` compile synchronously in `__init__` (~1–2 s LaTeX / ~0.4 s Typst). With a **visible** window RTM shows a "compiling formula" popup (`runtime.md` → *Compile-wait popup*); `RTM_WAIT_POPUP=0` disables it, `RTM_LANG` forces its language, and a warm cache (`restore_tex_cache`) removes the wait. Output is unaffected.
- **`from real_time_manim import remove_invisible_chars`** → `ImportError` (not exported) → filter invisible chars yourself.
- **`MarkupText` with `<span foreground=…>`** → `ElementTree.ParseError: no element found` → give the whole string a `color` or use `Text` + `t2c`.
- **`get_part_by_tex` no match returns `None`** → chaining `part.width` gives `AttributeError` → test for `None`.
- **`BulletedList.fade_all_but("string")`** → `Exception: Could not locate part by provided tex string '…'` → use an integer index; dimmed items are not restored automatically.
- **`Typst.select`** unknown label → `KeyError`; bad index → `IndexError`.
- **`TypstMath`/`MathTypst`: do not add your own `$`** (nests twice). `TypstMath` is an alias of `MathTypst`.
- **`Tex` never auto-routes to Typst** (excluded by `isinstance(self, _OrigTex)`); a real LaTeX distribution is required. Do not use `\\` line breaks under `tex_environment="document"`.
- **`MathTex` Typst auto-route** can silently fall back to LaTeX; disable with `RTM_TYPST=0`, debug with `RTM_TYPST_DEBUG=1`. `_USE_NATIVE_MATHTEX` is off by default (renders many commands literally).
- **`MathTex` `set_color_by_tex`/`tex_to_color_map` keys must exactly equal the part's `tex_string`**; absent keys are silently ignored.
- **`Code` with neither `code_file` nor `code_string`** → `ValueError: Either a code file or a code string must be specified.`
- **`Matrix(font_size=...)`** → `TypeError: Mobject.__init__() got an unexpected keyword argument 'font_size'` → use `element_to_mobject_config={"font_size": …}`.
- **`Matrix`/`DecimalMatrix`/`IntegerMatrix`/`Table` numeric elements with `element_to_mobject=Text`/`MathTex`** → `AttributeError: 'int' object has no attribute 'find'` (or generic `AttributeError`) → use `DecimalNumber`/`Integer` for numbers.
- **`element_to_mobject_config` replaces (does not merge) the default** → include `font_size` when changing places.
- **`SVGMobject(svg_default=...)` missing a key** → `KeyError: 'color'` → required keys: `color`/`fill_color`/`fill_opacity`/`stroke_color`/`stroke_opacity`/`stroke_width`/`opacity` (whole table replaced, no merge).
- **`VMobjectFromSVGPath` given a `d` string** → `AttributeError: 'str' object has no attribute 'approximate_arcs_with_quads'` → wrap with `se.Path("…")`.
- **`Brace.get_text`/`get_tex(..., font_size=…)`** → `TypeError: Mobject.next_to got an unexpected keyword argument 'font_size'` → kwargs only reach `put_at_tip`; set style on the returned object.
- **`Table`/`Matrix` highlights are `(row, col)` 1-based**; `add_highlighted_cell` stacks blocks (no replacement); `Table.create` returns an `AnimationGroup` (do not pre-`add` the table).
- **`Label`/`LabeledLine` `*_config` dicts only apply to `str` labels** (an existing `Text`/`MathTex` wins). `LabeledLine`/`LabeledArrow`: `start`/`end` must be keyword args.
- **`ImageMobject` (lowercase `m`)**, not `ImageMObject`. `ImageMobjectFromCamera` captures a static snapshot (call `capture_mobject` first). `Text`/`MathTex` own 0 points (vertices live in glyph submobjects) — use `get_all_points()`.

### Coords & charts
- **`add_labels(font_size=...)` on a bare `VMobject` label** → `AttributeError` → use `Text`/`MathTex`/`DecimalNumber`.
- **`CoordinateSystem.get_axes`** → `NotImplementedError` (only `Axes` returns `self.axes`).
- **`plot_line_graph` with mismatched `x_values`/`y_values`** → `ValueError` (`zip(strict=True)`).
- **`Axes.plot(colorscale=...)` without `x_range`** → `TypeError` (pass both).
- **`PolarPlane` bad `azimuth_units`** → `ValueError: "Invalid azimuth units. Expected one of: PI radians, TAU radians, degrees, gradians or None."`
- **`BarChart` `bar_names` longer than `values`** → `IndexError`.
- **`SampleSpace` brace helpers** (`get_side/top/bottom/subdivision_braces_and_labels`) broken upstream → `TypeError: Mobject.__init__() got an unexpected keyword argument 'min_num_quads'` → build braces manually.
- **`LogBase.inverse_function(value <= 0)`** → `ValueError: "log(0) is undefined"` → keep axis/plot lower bounds `> 0`.
- **`Axes.plot` with vertical asymptotes** must clamp y; `dt=1e-8` is too small (use `0.1`); `discontinuities` omitting values draws a connecting vertical line.
- **`NumberLine` `axis @ number` only accepts a scalar; `point @ axis` only a plain `list`/`tuple`** (an `np.ndarray` is claimed by numpy as matmul) → use `n2p`/`p2c`.
- **`get_graph_label`/`plot_implicit_curve`** label via `MathTex` (write `x^2`); `ImplicitFunction` cannot be fed to analytic methods (`get_area`, `plot_derivative_graph`).
- **`get_area` `bounded_graph` must be above `graph`** else the area flips.
- **`get_riemann_rectangles` `input_sample_type` must be the full word** (`"left"`/`"right"`/`"center"`).
- **`FunctionGraph` has no coordinate system**; `ParametricFunction` returns **scene** points, `plot_parametric_curve` returns **data** coords.
- **`Axes` `get_axis_labels` results are not auto-added**; `add_coordinates` re-calls overwrite same-axis labels.

### 3D
- **3D looks flat without a 3D camera** → use `ThreeDScene` + `set_camera_orientation(phi=…, theta=…)`.
- **`self.move_camera(...)` needs `self.play = win.play`** (it calls `self.play` internally); `set_camera_orientation` does not. `Create(...)`/`.animate` via `win.play` do not need the wiring.
- **Surface subclasses swallow `color=`** (`Cone`/`Cylinder`/`Sphere`/`Torus`/`Surface`) → `.set_color(...)` after construction, or `checkerboard_colors=False, fill_color=...`. `Dot3D` colors itself internally (works).
- **`Surface.set_fill_by_value`** extra kwargs alongside `colors` → `ValueError: "Unsupported keyword argument(s): <keys>"`; `colorscale=None` → warning `"The value passed to the colorscale keyword argument was None, the surface fill color has not been changed"`.
- **`Line3D.perpendicular_to` when the point lies on the line** → `ValueError: "Could not find the perpendicular."` → pick a point off the line.
- **`three_d_utils` functions need a single 3D face**, not a `VGroup` shell → take `cube[i]` first (else corners fall back to `ORIGIN`, normals to `UP`).
- **`Surface`/`Sphere`/`Torus` cost = `u_res × v_res` faces** → keep resolution low; `color=` caveat applies.
- **`ConvexHull3D` takes positional points** (`ConvexHull3D(*pts)`), degenerates with <4 points or coplanar input.
- **`Polyhedron` `fill_color` goes through `faces_config`** (a `Polygon` param), not the `set_color` path; edge strokes off by default (`stroke_opacity: 0`).
- **`Arrow3D` `end` is the tip**; `Cylinder.height` is along `direction` (not necessarily vertical).
- **`ThreeDCamera.shading_factor`/`default_distance` stored, never read** (dead); `MovingCamera.fixed_dimension` stored, never read.

### Graph & vector fields
- **Duplicate vertex name** → `ValueError: "Vertex identifier '{vertex}' is already used for a vertex in this graph."`
- **`edge_type` not a `Line` subclass** (`CurvedArrow`) → `TypeError` → use `Line`/`DoubleArrow`.
- **Unknown layout name** → `ValueError: "The layout '{layout}' is neither a recognized layout, a layout function,nor a vertex placement dictionary."`; a `layout_config` key not accepted by the chosen algorithm (e.g. `seed` on `circular`/`kamada_kawai`) → `TypeError`.
- **`Graph.__getitem__` unknown key** → `ValueError: "Could not find {k} in vertices or edges"` (docstring claims `KeyError`).
- **`Graph` per-vertex/per-edge overrides are whole replacements, not merges.**
- **`labels=True` labels are `MathTex`** (need LaTeX/Typst); a `labels` dict must cover every vertex; `vertex_type` becomes `LabeledDot`.
- **`Graph.layout="spring"`/`"random"` must pin `seed`** for reproducibility; `move_to` on a vertex does not keep `_layout` in sync (only `change_layout` does).
- **`VectorField.get_colored_background_image` with `single_color`** → `ValueError: "There is no point in generating an image if the vector field uses a single color."`
- **`StreamLines.start_animation` renders blank with no error if `self.add(sl)` is missing** (the updater lives on `sl`; `create()` only adds the individual lines) → always `self.add(sl)`.
- **`StreamLines.end_animation()` without a prior `start_animation()`** → `ValueError: "You have to start the animation before fading it out."`
- **`StreamLines.create` `run_time` defaults to `virtual_time`** → forgetting it makes the draw look like a 3-second wait; `virtual_time` dominates construction cost.
- **`StreamLines` per-position gradient is flattened to one averaged color in RTM** (cannot tint per pixel) → pass `color=` explicitly for deterministic output.
- **`VectorField.nudge` produces no animation** (instant jump); `start_submobject_movement` can only be stopped by `stop_submobject_movement()` (`clear_updaters()` has no effect).
- **`DEFAULT_SCALAR_FIELD_COLORS` not exported at top level** → import from `manim.mobject.vector_field`.

### Utils
- **Unknown color name** (e.g. `"REDD"`) → `ValueError`.
- **`ManimColor.gradient(...)`** → `NotImplementedError` → use module-level `color_gradient`.
- **`ManimColor.parse` treats a tuple as a sequence** → parses element-by-element; use `ManimColor(...)`/`from_rgb`.
- **`from_hsv`/`from_hsl` pass a tuple, not a list** (a list is misparsed as an int RGB array).
- **`average_color` ignores alpha**; `random_color`/`random_bright_color` use the global random state.
- **Rate-func factory passed uncalled** → runtime `TypeError`/`ValueError`.
- **`rotate_vector` with >3 components** → `ValueError: "Vector must have the correct dimensions."`
- **`shoelace` given a plain `list`** → `TypeError` (needs `np.array`); it does not auto-close the polygon.
- **`line_intersection` parallel or z≠0 lines** raises.
- **`angle_of_vector` ignores z**; `center_of_mass` is an equal-weight vertex mean (differs from `get_midpoint` path midpoint).
- **`compass_directions` has no `clockwise` param** (zh_CN 03 says otherwise; source wins) → pass a different `start_vect`/negate the angle.
- **`DR` value is `[1, -1, 0]`** (source wins over the zh_CN 03 table's `[1, 1, 0]`).
- **Naming traps that do not exist (0.21.0)**: `rotation_between_vectors` → `rotation_matrix(angle_between_vectors(...), cross(...))`; `angle_between` → `angle_between_vectors`; `get_unit_vector` → `normalize`; `complex_to_vec3` → `complex_to_R3`; `path_along_line` → `straight_path()`.
- **`adjacent_pairs` returns a zip iterator** (not a list); `remove_list_redundancies` keeps the **last** occurrence.
- **`rate_functions` top level has only 17 names**; `ease_*` (30), decorators (`unit_interval`/`zero`) and `RateFunction` need the `rate_functions.` prefix. `from real_time_manim import rate_functions` gives RTM's superset module.

---

## Error → cause → fix

| Error (verbatim) | Cause | Fix | See |
| --- | --- | --- | --- |
| `[rtm] forcing 1920x1080: RTM supports high quality only (asked for {w}x{h})` | window size ≠ 1920×1080 | none (info notice); use 1920×1080 | `runtime.md` |
| `[rtm] forcing 60 fps: RTM supports high quality only (asked for {fps})` | fps ≠ 60 | none (info notice) | `runtime.md` |
| `RuntimeWarning` (different class identity) | `manim` imported before `real_time_manim` | `import real_time_manim` first | `runtime.md` |
| `FileNotFoundError: "vulkan_core.dll not found. If running from source, build it with native/build.ps1 (requires Vulkan SDK + MinGW-w64)."` | native lib missing | Windows: reinstall the wheel; macOS: `bash native/build_mac.sh` | `runtime.md` |
| `RuntimeError: "Vulkan_Init failed"` / `"Vulkan_InitEx failed"` | device/init failure | check Vulkan GPU+driver | `runtime.md` |
| `RuntimeError: "win.play() called before the scene was bound: run \`win.scene = self\` inside construct(), or pass the scene explicitly; without it RTM has nothing to draw or record."` | `win.scene` unset | `win.scene = self` before `win.play` | `runtime.md` |
| `TypeError: "Unexpected argument {Type} passed to MLWindow.play(): pass an Animation or a .animate(...) builder (or Scene.add() the mobject first)."` | bare `Mobject` passed to `play()` | wrap in an animation or `Scene.add()` first | `runtime.md` |
| `[RTM] win.play(): unsupported keyword(s) {...} ignored -- RTM 不支持该参数: only run_time, rate_func, path_arc, path_arc_axis, path_arc_centers, path_func are honoured at play level; pass the rest to the animation constructor instead (e.g. Create(sq, lag_ratio=...)).` | unsupported play-level kwarg | pass it to the animation constructor | `runtime.md` |
| `[RTM] Scene.add_sound(): unsupported parameter(s) … ignored -- RTM 不支持该参数: the RTM audio mix supports only sound_file, time_offset, gain, gain_to_background.` | unsupported `add_sound` kwarg | drop the keyword | `scene-camera.md` |
| `RuntimeError: "Scene.add_subcaption needs an MLWindow bound to the scene (create one in construct() first, as every RTM scene does)"` | no window bound | create `MLWindow` + `win.scene = self` | `scene-camera.md` |
| `RuntimeError: "recorded {n} window(s) but MLWindow.close() was only called {m} time(s): the encoder was never finished, so the output is incomplete. Call win.close() at the end of construct()."` | `win.close()` not called | call `win.close()` | `runtime.md` |
| `RuntimeError: "recorded file looks empty/incomplete ({n} bytes): {f} -- did the scene forget \`win.scene = self\`, or forget win.close()?"` | output < 1024 bytes | bind `win.scene`, call `win.close()` | `runtime.md` |
| `TypeError: "scene looks like a class but has no construct(); ..."` / `"scene must be a Scene subclass, a Scene instance, or a no-arg callable."` | wrong `scene` argument | pass a `Scene` subclass/instance/no-arg callable | `runtime.md` |
| `FileExistsError: "target already exists: {out_path} (pass overwrite=True to replace it)"` | `overwrite=False`, target exists | `overwrite=True` or remove the file | `runtime.md` |
| `RuntimeError: "scene did not create an MLWindow"` | `FrameServer` scene opened no window | create an `MLWindow` in `construct()` | `runtime.md` |
| `ValueError: "controls must be 'input' or 'slider', got {value!r}"` | bad `FramePreview(controls=…)` | use `"input"`/`"slider"` (aliases listed) | `runtime.md` |
| `ValueError: "position must be two numbers, got {value!r}"` / `"position must look like '100,200', got {value!r}"` | bad `FramePreview(position=…)` | pass `(x, y)` or `"x,y"` | `runtime.md` |
| `RuntimeError: "cannot add to a finalized Timeline"` | `Timeline.add` after `finalize` | add before `finalize()` | `runtime.md` |
| `RuntimeError: "Timeline already finalized"` | `finalize()` twice | call once | `runtime.md` |
| `ValueError: "{Type} is stateful and cannot be evaluated as a pure function of time yet"` | stateful animation under `strict=True` | drop `strict` or avoid stateful anims | `runtime.md` |
| `RuntimeError: "call finalize()/prepare() first"` | `evaluate` before `finalize` | `finalize()`/`prepare()` first | `runtime.md` |
| `[Record] ffmpeg not found. Install ffmpeg and add it to PATH.` | no ffmpeg | install ffmpeg, add to PATH | `runtime.md` |
| `[Record] ffmpeg failed: {stderr}` | ffmpeg encode error | inspect stderr | `runtime.md` |
| `[Record] No frames captured, aborting.` | nothing captured | window must be visible; check playback | `runtime.md` |
| `[FastRecord] ffmpeg failed: {e}` | offline encode error | inspect `{e}` | `runtime.md` |
| `[rtm] cannot read '{x}' -- try 120, 2.5s, +1, s, q` | bad `FramePreview` input | use listed syntax | `runtime.md` |
| `NotImplementedError: "Please use Create or ShowPassingFlash"` | played abstract `ShowPartial` directly | use `Create`/`ShowPassingFlash` | `animation-transform.md` |
| `TypeError` (object lacks `pointwise_become_partial`) | non-VMobject passed to `ShowPartial` | pass a `VMobject` | `animation-transform.md` |
| `NotImplementedError` (`get_mobject_key`) | instantiating `TransformMatchingAbstractBase` | subclass + implement hooks | `animation-transform.md` |
| `ImportError: cannot import name 'TransformMatchingStrings' from 'manim' (…). Did you mean: 'TransformMatchingShapes'?` | class does not exist | use `TransformMatchingTex` | `animation-transform.md` |
| `ValueError` (`MoveToTarget`, ManimCE) | no prior `generate_target()` | call `generate_target()` first | `animation-motion.md` |
| `AttributeError: 'NoneType' object has no attribute 'copy'` (RTM `MoveToTarget`) | no prior `generate_target()` | call `generate_target()` first | `animation-motion.md` |
| `ValueError` (`ApplyMethod`) | passed an already-called result instead of a bound method | pass `sq.shift`, not `sq.shift(RIGHT)` | `animation-transform.md` |
| `TypeError` (`ApplyFunction`) | function returned a non-`Mobject` | return a `Mobject` | `animation-transform.md` |
| `ValueError: "Matrix has bad dimensions"` | `ApplyMatrix` matrix not 2×2/3×3 | pass 2×2 or 3×3 | `animation-transform.md` |
| `ValueError("shape should be either Rectangle or Circle.")` | CE `Circumscribe` bad `shape` | use `Rectangle`/`Circle` (RTM-own does not error) | `animation-transform.md` |
| `ValueError("At least one mobject must be passed.")` | CE `FadeIn()` empty | pass ≥1 mobject | `animation-transform.md` |
| `TypeError` (`Homotopy`/`ComplexHomotopy`) | invalid `apply_function_kwargs` key | only pass `Mobject.apply_function` keys | `animation-motion.md` |
| `AssertionError` (`SmoothedVectorizedHomotopy`) | `mobject` not a `VMobject` | pass a `VMobject` | `animation-motion.md` |
| `NameError` (`SmoothedVectorizedHomotopy`, pure manim 0.21) | upstream missing import | fixed in RTM `compat.py` | `animation-motion.md` |
| `ValueError` (`Wait`, `Scene.wait`) | `stop_condition` + `frozen_frame=True` together | use only one | `animation-motion.md` |
| `AssertionError` (`ChangeSpeed`) | >1 `affects_speed_updaters=True` playing | serialize them | `animation-motion.md` |
| `ValueError("The run_time of Animation cannot be negative...")` | ManimCE negative `run_time` | pass ≥ 0 | `animation-motion.md` |
| `ValueError` (`Animation`, RTM `win.play`) | whole-play `run_time <= 0` | pass a positive `run_time` | `animation-motion.md` |
| `ValueError` (`AnimationGroup`) | `synchronize_with_wall_clock=True` | drop it (unsupported) | `animation-motion.md` |
| `ValueError` (`AddTextLetterByLetter`) | empty text | pass non-empty `Text` | `animation-motion.md` |
| `ValueError` (`Mobject.animate`) | animation kwargs after a chained method or twice | pass once, right after `.animate(...)` | `animation-motion.md` |
| `TypeError` (`ChangingDecimal`/`ChangeDecimalToValue`) | non-`DecimalNumber` input | pass a `DecimalNumber` | `animation-motion.md` |
| `TypeError` (`Scene.play`) | bare method/mobject as an anim | wrap in an animation | `animation-motion.md` |
| `UserWarning` (`lag_ratio` on no-submobject object) | `lag_ratio` ineffective | ignore, or apply to a group | `mobject.md` |
| `MultiAnimationOverrideException` | same animation class registered twice | delete the old override first | `mobject.md` |
| `AssertionError` (`assert_is_mobject_method`) | non-bound/non-`Mobject` method passed to `always`/`f_always` | pass a bound method | `mobject.md` |
| `TypeError: float() argument must be a string or a real number, not 'complex'` | `ComplexValueTracker` arithmetic on 0.21 | do complex math manually + `set_value` | `mobject.md` |
| `ValueError` (`expand(direction=…)`) | direction not `left`/`right`/`center` | use one of the three | `mobject.md` |
| `NameError: name 'Camera' is not defined` | `get_image`/`show`/`save_image` (upstream) | unusable; read the render pipeline | `mobject.md` |
| `NotImplementedError` (base `point_from_proportion`/`proportion_from_point`) | called on the base class | use `Line`/`Arc`/`VMobject` | `mobject.md` |
| `ValueError: does not lie on this curve` | `proportion_from_point` off-path | pass a point on the curve | `mobject.md` |
| `ValueError` (`arrange_in_grid`) | not enough cells | increase `rows`/`cols` | `mobject.md` |
| `TypeError` (extra kwarg to `.rotate`) | `VMobject.rotate` has no `**kwargs` | drop the extra kwarg | `mobject.md` |
| `TypeError` (`alpha=` to `set_color`) | `VMobject.set_color` has no `alpha` | use `set_fill(opacity=…)`/`fade_to` | `mobject.md` |
| `TypeError: Only values of type VMobject can be added as submobjects of ...` | non-`VMobject` in a `VGroup` | use `Group` | `geometry.md` |
| `IndexError` (`Polygram(p1, p2, …)`) | single points as separate args | pass one vertex group, or use `Polygon` | `geometry.md` |
| `IndexError: too many indices for array: array is 1-dimensional, but 2 were indexed` | `LabeledPolygram` individual points | pass one full ring per group | `geometry.md` |
| `KeyError: 2` | integer index into a `VDict` | index by key: `vd["c"]` | `geometry.md` |
| `ValueError` (`change_anchor_mode`) | mode other than `"smooth"`/`"jagged"` | use those two | `geometry.md` |
| `TypeError` (`TangentialArc`) | `radius` omitted (no default) | pass `radius=` | `geometry.md` |
| `ImportError` (`remove_invisible_chars`) | not exported by RTM | filter invisible chars yourself | `text.md` |
| `ElementTree.ParseError: no element found` | `MarkupText` `<span foreground=…>` | whole-string `color`, or `Text` + `t2c` | `text.md` |
| `AttributeError` (chaining on `get_part_by_tex` result) | part not found → `None` | test for `None` first | `text.md` |
| `Exception: Could not locate part by provided tex string '…'` | `BulletedList.fade_all_but("string")` | use an integer index | `text.md` |
| `KeyError` / `IndexError` (`Typst.select`) | unknown label / index out of range | use a valid label/index | `text.md` |
| `ValueError: Either a code file or a code string must be specified.` | `Code` with neither source | pass `code_file` or `code_string` | `text.md` |
| `TypeError: Mobject.__init__() got an unexpected keyword argument 'font_size'` | `Matrix(font_size=…)` | use `element_to_mobject_config` | `text.md` |
| `AttributeError: 'int' object has no attribute 'find'` | numeric elements with `element_to_mobject=Text`/`MathTex` | use `DecimalNumber`/`Integer` | `text.md` |
| `AttributeError` (`DecimalMatrix`/`Table` numeric + `Text`/`MathTex`) | element renderer cannot take numbers | use a number class | `text.md` |
| `KeyError: 'color'` (`SVGMobject`) | `svg_default` missing a key | supply all required keys | `text.md` |
| `AttributeError: 'str' object has no attribute 'approximate_arcs_with_quads'` | `VMobjectFromSVGPath` given a `d` string | wrap with `se.Path("…")` | `text.md` |
| `TypeError: Mobject.next_to got an unexpected keyword argument 'font_size'` | `Brace.get_text`/`get_tex(..., font_size=…)` | set style on the returned object | `text.md` |
| `AttributeError` (`add_labels(font_size=…)` on a bare `VMobject`) | label has no `font_size` | use `Text`/`MathTex`/`DecimalNumber` | `coords-charts.md` |
| `NotImplementedError` (`CoordinateSystem.get_axes`) | base `CoordinateSystem` | use `Axes` | `coords-charts.md` |
| `ValueError` (`plot_line_graph`) | `x_values`/`y_values` length mismatch | match lengths | `coords-charts.md` |
| `TypeError` (`Axes.plot`) | `colorscale` without `x_range` | pass `x_range` too | `coords-charts.md` |
| `ValueError: "Invalid azimuth units. Expected one of: PI radians, TAU radians, degrees, gradians or None."` | bad `azimuth_units` | use a listed value | `coords-charts.md` |
| `IndexError` (`BarChart`) | `bar_names` longer than `values` | shorten `bar_names` | `coords-charts.md` |
| `TypeError: Mobject.__init__() got an unexpected keyword argument 'min_num_quads'` | `SampleSpace` brace helpers (upstream) | build braces manually | `coords-charts.md` |
| `ValueError: "log(0) is undefined"` | `LogBase.inverse_function(value <= 0)` | keep lower bounds `> 0` | `coords-charts.md` |
| `ValueError: "Could not find the perpendicular."` | `Line3D.perpendicular_to` point on the line | pick a point off the line | `three-d.md` |
| `ValueError: "Unsupported keyword argument(s): <keys>"` | `Surface.set_fill_by_value` extra kwargs alongside `colors` | pass only one of `colorscale`/`colors` | `three-d.md` |
| `"The value passed to the colorscale keyword argument was None, the surface fill color has not been changed"` (warning) | `set_fill_by_value(colorscale=None)` | provide a colorscale | `three-d.md` |
| `ValueError: "Vertex identifier '{vertex}' is already used for a vertex in this graph."` | duplicate vertex name | rename the vertex | `graph-vector.md` |
| `TypeError` (`Graph` `edge_type`) | `edge_type` not a `Line` subclass | use `Line`/`DoubleArrow` | `graph-vector.md` |
| `TypeError` (`layout_config` key) | key not accepted by the chosen layout (e.g. `seed` on `circular`) | use only accepted keys | `graph-vector.md` |
| `ValueError: "The layout '{layout}' is neither a recognized layout, a layout function,nor a vertex placement dictionary."` | unknown layout name + callable branch raised | use a valid layout name/dict/callable | `graph-vector.md` |
| `ValueError: "Could not find {k} in vertices or edges"` | unknown `Graph.__getitem__` key | use an existing vertex/edge | `graph-vector.md` |
| `ValueError: "There is no point in generating an image if the vector field uses a single color."` | `get_colored_background_image` with `color=` set | do not pass `color=` | `graph-vector.md` |
| `ValueError: "You have to start the animation before fading it out."` | `StreamLines.end_animation()` without `start_animation()` | call `start_animation()` first | `graph-vector.md` |
| (no error) `StreamLines` renders blank | `start_animation` updater lives on `sl`, which was not added | `self.add(sl)` | `graph-vector.md` |
| `ValueError` (unknown color name) | bad color string (e.g. `"REDD"`) | use a valid name/hex | `utils.md` |
| `NotImplementedError` (`ManimColor.gradient`) | called the method | use module-level `color_gradient` | `utils.md` |
| `TypeError`/`ValueError` (rate-func factory) | factory passed uncalled as `rate_func` | call it: `squish_rate_func(smooth, 0.2, 0.8)` | `utils.md` |
| `ValueError: "Vector must have the correct dimensions."` | `rotate_vector` vector > 3 components | pass ≤ 3 components | `utils.md` |
| `TypeError` (`shoelace`) | plain Python `list` instead of `np.array` | pass `np.array` | `utils.md` |
| `TypeError: 'numpy.float64' object is not iterable` | `coords_to_vector` (upstream `Matrix(vector)`) | build the matrix manually | `scene-camera.md` |
| `ValueError` (`show_ghost_movement`, 0.20.1 `Dot object has no attribute 'hex'`) | upstream `VMobject(*Dots)` | avoid; use a manual ghost | `scene-camera.md` |
| `AttributeError` (`self.camera.frame` on plain `Camera`) | `Camera` has no `frame` | use `MovingCameraScene`/`hasattr` | `scene-camera.md` |
| `LinAlgError` (`apply_inverse`) | singular matrix | pass an invertible 2×2 | `scene-camera.md` |
| `ValueError` (`Scene.replace`) | `old_mobject` not in scene / `new_mobject` already in scene | fix the operands | `scene-camera.md` |
| `DeprecationWarning` (`get_foo`/`set_foo`) | legacy accessors | use the property/attribute | `mobject.md` |
