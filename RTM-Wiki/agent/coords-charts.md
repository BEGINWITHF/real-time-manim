# coordinates & charts

> scope: NumberLine + methods, Axes + methods, coordinate conversion (c2p/p2c/@), NumberPlane/ComplexPlane, function curves (plot/parametric/implicit/FunctionGraph), curve labels & helper lines, derivative/antiderivative/tangent, area & Riemann rectangles, PolarPlane/ThreeDAxes/plot_surface, BarChart, SampleSpace, ticks/scales (LinearBase/LogBase). Data model = bundled ManimCE 0.21.0; RTM only rasterizes it.
> src: `real_time_manim/manim/mobject/graphing/{coordinate_systems,functions,number_line,probability,scale}.py`; human wiki `../zh_CN/05-坐标系与图表/`.
> RTM render notes: `BarChart`/`SampleSpace`/`scaling` go through the generic vector fallback path (verified rendered 2026-10-11). MathTex/Tex labels are compiled by the Typst backend when the `real-time-manim[typst]` extra is installed and `RTM_TYPST` is not `0`, otherwise by real LaTeX.

## NumberLine

### `NumberLine`
```python
def __init__(self, x_range: Sequence[float] | None = None, length: float | None = None,
             unit_size: float = 1, include_ticks: bool = True, tick_size: float = 0.1,
             numbers_with_elongated_ticks: Iterable[float] | None = None,
             longer_tick_multiple: int = 2, exclude_origin_tick: bool = False,
             rotation: float = 0, stroke_width: float = 2.0, include_tip: bool = False,
             tip_width: float = DEFAULT_ARROW_TIP_LENGTH,          # 0.35
             tip_height: float = DEFAULT_ARROW_TIP_LENGTH,         # 0.35
             tip_shape: type[ArrowTip] | None = None, include_numbers: bool = False,
             font_size: float = 36, label_direction: Point3DLike = DOWN,
             label_constructor: type[ManimTextLabel] = MathTex, scaling: _ScaleBase = LinearBase(),
             line_to_number_buff: float = MED_SMALL_BUFF,          # 0.25
             decimal_number_config: dict | None = None,
             numbers_to_exclude: Iterable[float] | None = None,
             numbers_to_include: Iterable[float] | None = None, **kwargs: Any) -> None
```
- `ret`: `NumberLine` (subclass of `Line` → `VMobject`). Key attrs after ctor: `numbers`, `labels`, `ticks`, `x_range`/`x_min`/`x_max`/`x_step`, `unit_size`, `scaling`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `x_range` | `Sequence[float] \| None` | `None` → `[-7, 7, 1]` | `[x_min, x_max, x_step]`; a 2-tuple auto-appends `step=1`; `step` sets tick/label density |
| `length` | `float \| None` | `None` | total axis length (Manim units); if given it overrides and back-solves `unit_size` |
| `unit_size` | `float` | `1` | spacing of adjacent integer ticks (used when `length` is not given) |
| `include_ticks` | `bool` | `True` | draw tick marks |
| `tick_size` | `float` | `0.1` | tick length |
| `numbers_with_elongated_ticks` | `Iterable[float] \| None` | `None` | values whose ticks are elongated, e.g. `[-2, 4]` |
| `longer_tick_multiple` | `int` | `2` | elongation factor |
| `exclude_origin_tick` | `bool` | `False` | drop the tick at 0 (`Axes` linear axes set `True`) |
| `rotation` | `float` | `0` | whole-axis rotation (radians) |
| `stroke_width` | `float` | `2.0` | line width |
| `include_tip` | `bool` | `False` | arrow at the end |
| `tip_width` / `tip_height` | `float` | `DEFAULT_ARROW_TIP_LENGTH` (0.35) | arrow dimensions |
| `tip_shape` | `type[ArrowTip] \| None` | `None` | arrow class (e.g. `StealthTip`); `None` = default |
| `include_numbers` | `bool` | `False` | show numeric labels along `label_direction` |
| `font_size` | `float` | `36` | label font size |
| `label_direction` | `Point3DLike` | `DOWN` | label side relative to the axis |
| `label_constructor` | `type` | `MathTex` | label class (`MathTex`/`Tex`/`Text`/…) |
| `scaling` | `_ScaleBase` | `LinearBase()` | tick scaling; pass `LogBase()` for a log axis |
| `line_to_number_buff` | `float` | `MED_SMALL_BUFF` (0.25) | gap between label and axis |
| `decimal_number_config` | `dict \| None` | auto | forwarded to `DecimalNumber`; default decimals inferred from `step` |
| `numbers_to_exclude` | `Iterable[float] \| None` | `None` | values whose labels are hidden |
| `numbers_to_include` | `Iterable[float] \| None` | `None` | only these labels (passing it triggers number creation without `include_numbers=True`) |
| `**kwargs` | — | — | forwarded to `Line` (`color`, `stroke_opacity`, …) |

- `notes`:
  - When `x_range` spans negative and positive, ticks are counted from 0; `min`/`max` may have **no** tick (depends on `step`).
  - Given `length`, do not also tune `unit_size` — it is overridden.
  - The tip is drawn beyond `x_max`; do not place dots/labels exactly at `x_max`.
- `see`: ../zh_CN/05-坐标系与图表/01-NumberLine.md
- `eg`:
```python
line = NumberLine(x_range=[-4, 4, 1], length=8, include_numbers=True, include_tip=True)
dot = Dot(line.n2p(2), color=RED)
```

### `UnitInterval`
```python
def __init__(self, unit_size: float = 10, numbers_with_elongated_ticks: list[float] | None = None,
             decimal_number_config: dict | None = None, **kwargs: Any) -> None
```
- `ret`: `UnitInterval` (`NumberLine` subclass, all methods available).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `unit_size` | `float` | `10` | unit length (spans the frame) |
| `numbers_with_elongated_ticks` | `list[float] \| None` | `[0, 1]` | elongated tick positions |
| `decimal_number_config` | `dict \| None` | `{"num_decimal_places": 1}` | number format |
| `**kwargs` | — | — | forwarded to `NumberLine` (a passed `x_range` overrides) |

- `notes`: fixed `x_range=(0, 1, 0.1)`. Overriding `x_range` via `**kwargs` makes it no longer a unit interval — use `NumberLine` instead.
- `see`: ../zh_CN/05-坐标系与图表/01-NumberLine.md

## NumberLine methods

### `n2p` / `p2n` (`number_to_point` / `point_to_number`)
```python
def number_to_point(self, number: float | np.ndarray) -> np.ndarray   # alias n2p
def point_to_number(self, point: Sequence[float]) -> float            # alias p2n
```
- `ret`: `n2p` → scene point `np.ndarray` (arrays in → array out); `p2n` → `float`.
- `args`:
  - `number: float | np.ndarray` — required; an array converts many at once.
  - `point: Sequence[float]` — required scene point `[x, y, z]`; point arrays allowed.
- `notes`:
  - The only correct way to place anything on a number line. A scaling axis (`LogBase`) applies `scaling.inverse_function` first.
  - `axis @ number` is equivalent to `n2p(number)` but only accepts a scalar. The reverse `point @ axis` accepts only a plain `list`/`tuple` — an `np.ndarray` is claimed by numpy as matmul and errors; use `p2n`/`p2c`.
- `see`: ../zh_CN/05-坐标系与图表/01b-数轴方法进阶.md

### `add_numbers` / `add_labels`
```python
def add_numbers(self, x_values: Iterable[float] | None = None, excluding: Iterable[float] | None = None,
                font_size: float | None = None, label_constructor: type | None = None,
                **kwargs: Any) -> Self
def add_labels(self, dict_values: dict[float, str | float | VMobject], direction: Point3DLike | None = None,
               buff: float | None = None, font_size: float | None = None,
               label_constructor: type[ManimTextLabel] | None = None) -> Self
```
- `ret`: `Self` (chainable). `add_numbers` results in `self.numbers`; `add_labels` results in `self.labels`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `x_values` | `Iterable[float] \| None` | `None` | values to label; default = all of `get_tick_range()` |
| `excluding` | `Iterable[float] \| None` | `numbers_to_exclude` | values to skip |
| `dict_values` | `dict[float, str \| float \| VMobject]` | required | e.g. `{1: "Monday"}`; a `str` is built by `label_constructor` |
| `direction` | `Point3DLike \| None` | `label_direction` | label side |
| `buff` | `float \| None` | `line_to_number_buff` | gap to the axis |
| `font_size` | `float \| None` | `font_size` | label must expose a `font_size` attr or `AttributeError` is raised |
| `label_constructor` | `type \| None` | axis setting | class for `str` labels |
| `**kwargs` | — | — | `add_numbers` forwards to `get_number_mobject` (e.g. `num_decimal_places`) |

- `notes`: `str` values in `add_labels` default to `MathTex` (math italic); pass a `Text` object or `label_constructor=Text` for upright text. `Axes.add_coordinates(dict)` calls `add_labels` internally.
- `errs`:
  - `AttributeError` — `font_size` given to a bare `VMobject` label that has no `font_size` attribute → use `Text`/`MathTex`/`DecimalNumber`.
- `see`: ../zh_CN/05-坐标系与图表/01b-数轴方法进阶.md

### `get_tick_range` / `add_ticks` / `get_tick` / `get_tick_marks` / `rotate_about_number` / `get_unit_size` / `get_unit_vector`
```python
def get_tick_range(self) -> np.ndarray
def add_ticks(self) -> Self
def get_tick(self, x: float, size: float | None = None) -> Line
def get_tick_marks(self) -> VGroup
def rotate_about_number(self, number: float, angle: float, axis: Vector3D = OUT, **kwargs: Any) -> Self
def get_unit_size(self) -> float
def get_unit_vector(self) -> Vector3D
```
- `ret`: see signatures; `rotate_about_number` returns `Self`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `x` / `number` | `float` | required | tick value / rotation-center value |
| `size` | `float \| None` | `tick_size` | scale factor of one tick (`get_tick` only) |
| `angle` | `float` | required | rotation angle (radians) |
| `axis` | `Vector3D` | `OUT` | rotation axis |

- `notes`:
  - `get_tick_range()` accounts for `exclude_origin_tick` and `scaling`; it is the engine behind `include_numbers`/`add_ticks`.
  - `get_unit_size()` = 1 data unit in Manim length. `rotate_about_number(0, 0.5)` == `rotate(0.5, about_point=line.n2p(0))`.
- `see`: ../zh_CN/05-坐标系与图表/01b-数轴方法进阶.md

### `get_number_mobject` / `get_number_mobjects` / `get_labels`
```python
def get_number_mobject(self, x: float, direction: Vector3D | None = None, buff: float | None = None,
                       font_size: float | None = None, label_constructor: type | None = None,
                       **number_config: Any) -> VMobject
def get_number_mobjects(self, *numbers: float, **kwargs: Any) -> VGroup
def get_labels(self) -> VGroup
```
- `ret`: a positioned number mobject (`VMobject`) / `VGroup`; `get_labels()` == no-arg `get_number_mobjects()`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `x` | `float` | required | value to label |
| `direction` | `Vector3D \| None` | `label_direction` | placement direction |
| `buff` | `float \| None` | `line_to_number_buff` | gap to axis |
| `font_size` | `float \| None` | `font_size` | font size |
| `label_constructor` | `type \| None` | axis setting | text class |
| `**number_config` | — | — | merged into `decimal_number_config`, e.g. `num_decimal_places=2` |

- `notes`: generates the mobject but does **not** add it to the line — use it to animate a single number separately.
- `see`: ../zh_CN/05-坐标系与图表/01b-数轴方法进阶.md

## Axes

### `Axes`
```python
def __init__(self, x_range: Sequence[float] | None = None, y_range: Sequence[float] | None = None,
             x_length: float | None = round(config.frame_width) - 2,      # ≈12
             y_length: float | None = round(config.frame_height) - 2,     # ≈6
             axis_config: dict | None = None, x_axis_config: dict | None = None,
             y_axis_config: dict | None = None, tips: bool = True, **kwargs: Any) -> None
```
- `ret`: `Axes` (`VGroup` + `CoordinateSystem`). Key attrs: `x_axis`, `y_axis`, `axes`, `x_range`, `y_range`, `dimension=2`, `coordinate_labels`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `x_range` | `Sequence[float] \| None` | `None` → `[-7, 7, 1]` | `[x_min, x_max, x_step]`; 2-tuple auto-appends `step=1`; `step` only affects tick/label density, not scale |
| `y_range` | `Sequence[float] \| None` | `None` → `[-4, 4, 1]` | same |
| `x_length` | `float \| None` | `round(config.frame_width) - 2` (≈12) | x-axis screen length |
| `y_length` | `float \| None` | `round(config.frame_height) - 2` (≈6) | y-axis screen length |
| `axis_config` | `dict \| None` | `{"include_tip": tips, "numbers_to_exclude": [0]}` | common params for both `NumberLine`s |
| `x_axis_config` | `dict \| None` | `{}` | x-axis only; merged over `axis_config` |
| `y_axis_config` | `dict \| None` | `{"rotation": 90*DEGREES, "label_direction": LEFT}` | y-axis only |
| `tips` | `bool` | `True` | arrow tips on both axes |
| `**kwargs` | — | — | forwarded to `VGroup`/`CoordinateSystem` |

- `notes`:
  - Scale = `x_length / (x_max - x_min)`. If 0 is outside `[min, max]` the whole system auto-shifts so 0 (or the nearest end) sits at the screen center; `c2p` still resolves data coords.
  - 0 is excluded from tick numbers by the default `axis_config` `numbers_to_exclude=[0]`; pass `axis_config={"numbers_to_exclude": []}` to show it.
  - `get_axis_labels(...)` results are **not** auto-added to the scene.
- `see`: ../zh_CN/05-坐标系与图表/02-Axes.md
- `eg`:
```python
ax = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1], x_length=8, y_length=5,
          tips=False, axis_config={"font_size": 24}).add_coordinates()
curve = ax.plot(lambda x: 0.5 * x**2, color=BLUE)
```

### `add_coordinates`
```python
def add_coordinates(self, *axes_numbers: Iterable[float] | None | dict[float, str | float | Mobject],
                    **kwargs: Any) -> Self
```
- `ret`: `Self`. Labels are collected into `ax.coordinate_labels` (`VGroup`).
- `args`:
  - `*axes_numbers` — one value per axis in order (x, y, [z]): no arg = all axes default; `None` = that axis default; `list` = show only those values; `dict` = value→label.
  - `**kwargs` — forwarded to `NumberLine.add_numbers`/`add_labels` (e.g. `font_size`).
- `notes`: a `dict` `str` value renders via `MathTex`; pass `Tex`/`Text` objects for upright. Re-calling **overwrites** the same axis' labels — remove the old `ax.coordinate_labels` first or they stack. A scaling axis with `custom_labels=True` and a `None` arg uses `scaling.get_custom_labels`.
- `see`: ../zh_CN/05-坐标系与图表/02-Axes.md · ../zh_CN/05-坐标系与图表/03-坐标换算.md
- `eg`:
```python
ax.add_coordinates({1: "Mon", 2: "Tue"}, [-2, 0, 2])   # x: dict, y: list
ax.add_coordinates(None, [0, 0.5, 1])                  # x default, y explicit
```

### `get_axis` / `get_axes` / `get_x_axis` / `get_y_axis` / `get_z_axis` / `get_origin` / `get_x_unit_size` / `get_y_unit_size`
```python
def get_axis(self, index: int) -> NumberLine
def get_axes(self) -> VGroup
def get_x_axis(self) -> NumberLine
def get_y_axis(self) -> NumberLine
def get_z_axis(self) -> NumberLine          # ThreeDAxes
def get_origin(self) -> Point3D
def get_x_unit_size(self) -> float
def get_y_unit_size(self) -> float
```
- `ret`: axis `NumberLine` / `VGroup` / scene point / scale factor.
- `args`:
  - `index: int` — `0`=x, `1`=y, `2`=z.
- `notes`: `get_origin()` = scene point of `(0, 0)`; `get_*_unit_size()` = 1 data unit in screen length. `CoordinateSystem.get_axes` raises `NotImplementedError`; `Axes` returns `self.axes`.
- `see`: ../zh_CN/05-坐标系与图表/02-Axes.md

### `get_axis_labels` / `get_x_axis_label` / `get_y_axis_label`
```python
def get_axis_labels(self, x_label: float | str | Mobject = "x",
                    y_label: float | str | Mobject = "y") -> VGroup
def get_x_axis_label(self, label: float | str | VMobject, edge: Vector3D = UR,
                     direction: Vector3D = UR, buff: float = SMALL_BUFF, **kwargs: Any) -> Mobject
def get_y_axis_label(self, label: float | str | VMobject, edge: Vector3D = UR,
                     direction: Vector3D = UP * 0.5 + RIGHT, buff: float = SMALL_BUFF,
                     **kwargs: Any) -> Mobject
```
- `ret`: `VGroup` (both labels) or a positioned `Mobject`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `x_label` / `y_label` / `label` | `float \| str \| Mobject` | `"x"` / `"y"` | `str`/`float` built with `MathTex`; a `Tex`/`Text` object may be passed |
| `edge` | `Vector3D` | `UR` | axis edge the label hugs |
| `direction` | `Vector3D` | `UR` (x) / `UP*0.5+RIGHT` (y) | further offset from `edge` |
| `buff` | `float` | `SMALL_BUFF` (0.1) | distance from the axis |
| `**kwargs` | — | — | forwarded (`ThreeDAxes` also supports `rotation`, `rotation_axis`) |

- `notes`: the returned labels must be added to the scene yourself (`self.add`/`FadeIn`). `get_axis_labels` stores into `ax.axis_labels`.
- `see`: ../zh_CN/05-坐标系与图表/02-Axes.md

## Coordinate conversion

### `coords_to_point` / `c2p`
```python
def coords_to_point(self, *coords: float | Sequence[float] | Sequence[Sequence[float]] | np.ndarray) -> np.ndarray
```
- `ret`: `np.ndarray` scene coords (single point → shape `(3,)`).
- `args`: `*coords` — required. Single `ax.c2p(1, 2)` or `ax.c2p([1, 2])`; batch `ax.c2p([x0, x1, ...], [y0, y1, ...])`; 3D adds a third arg.
- `notes`: alias `c2p`, also `ax @ (x, y)`. The only correct way to place elements on the system; do not hand-compute the scale.
- `see`: ../zh_CN/05-坐标系与图表/03-坐标换算.md
- `eg`:
```python
p = ax.c2p(2, 1.5)
dots = [Dot(pt) for pt in ax.c2p([-3, 0, 3], [-2, 0, 2])]
```

### `point_to_coords` / `p2c`
```python
def point_to_coords(self, point: Sequence[float]) -> np.ndarray
```
- `ret`: `np.ndarray` data coords (e.g. `[4.0, 7.0]`); a list of points returns a 2D array.
- `args`: `point: Sequence[float]` — required scene point, e.g. `RIGHT` or `[0, 1, 0]`; a list `[RIGHT, [0, 1, 0]]` is accepted.
- `notes`: inverse of `c2p`. The reverse `@` (`point @ ax`) only accepts a plain `list`/`tuple` — an `np.ndarray` is interpreted by numpy as matmul and errors; use `p2c`.
- `see`: ../zh_CN/05-坐标系与图表/03-坐标换算.md

### `polar_to_point` / `pr2pt` · `point_to_polar` / `pt2pr`
```python
def polar_to_point(self, radius: float, azimuth: float) -> Point2D          # alias pr2pt
def point_to_polar(self, point: Point2DLike) -> Point2D                     # alias pt2pr
```
- `ret`: `Point2D` (`polar_to_point`) / `(radius, azimuth)` tuple (`point_to_polar`).
- `args`:
  - `radius: float` — coordinate radius `r`.
  - `azimuth: float` — coordinate azimuth `θ`.
  - `point: Point2DLike` — scene point.
- `notes`: internally `c2p`/`p2c` with trig; `polar_to_point` == `coords_to_point(radius*cos(azimuth), radius*sin(azimuth))`.
- `see`: ../zh_CN/05-坐标系与图表/07-极坐标与三维坐标系.md

## Grid & complex plane

### `NumberPlane`
```python
def __init__(self, x_range: Sequence[float] | None = (-config["frame_x_radius"], config["frame_x_radius"], 1),
             y_range: Sequence[float] | None = (-config["frame_y_radius"], config["frame_y_radius"], 1),
             x_length: float | None = None, y_length: float | None = None,
             background_line_style: dict | None = None, faded_line_style: dict | None = None,
             faded_line_ratio: int = 1, make_smooth_after_applying_functions: bool = True,
             **kwargs: Any) -> None
```
- `ret`: `NumberPlane` (`Axes` subclass). Attrs: `background_lines`, `faded_lines` (`VGroup`).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `x_range` / `y_range` | `Sequence[float] \| None` | `±frame_*_radius`, step 1 | as `Axes`; default uses **unrounded** frame radii |
| `x_length` / `y_length` | `float \| None` | `None` | `None` ⇒ 1 data unit = 1 Manim unit (grid fills the frame) |
| `background_line_style` | `dict \| None` | `{"stroke_color": BLUE_D, "stroke_width": 2, "stroke_opacity": 1}` | main grid line style |
| `faded_line_style` | `dict \| None` | half of the main style | faded subdivision line style |
| `faded_line_ratio` | `int` | `1` | subdivision density: `2`→4 sub-cells, `3`→9, `0`→off |
| `make_smooth_after_applying_functions` | `bool` | `True` | no effect currently |
| `**kwargs` | — | — | forwarded to `Axes` (`axis_config`, `y_axis_config`, `tips`, …) |

- `notes`: no tick numbers, no tips by default; axis labels point down-right. Since `x_length=None`, changing `x_range` changes grid density — pass `x_length`/`y_length` to fix screen scale. `c2p`/`plot`/`add_coordinates` inherited.
- `see`: ../zh_CN/05-坐标系与图表/04-网格与复平面.md

### `ComplexPlane`
```python
def __init__(self, **kwargs: Any) -> None
```
- `ret`: `ComplexPlane` (`NumberPlane` subclass); y-axis labels auto-carry `i` (`1i, 2i, -1i…`).
- `args`: all inherited from `NumberPlane` (`x_range`, `y_range`, `background_line_style`, …).
- `notes`:
  - `number_to_point` / `n2p`: `(number: float | complex) -> np.ndarray` — `n2p(2 + 1j)` positions directly.
  - `point_to_number` / `p2n`: `(point: Point3DLike) -> complex` — inverse of `n2p`.
  - `get_coordinate_labels(*numbers, **kwargs) -> VGroup` — default x real, y `1i, 2i…`.
  - `add_coordinates(*numbers, **kwargs) -> Self` — e.g. `add_coordinates([2, 1j, -3, -2j])`.
- `see`: ../zh_CN/05-坐标系与图表/04-网格与复平面.md

### `NumberPlane.get_vector`
```python
def get_vector(self, coords: Sequence[float], **kwargs: Any) -> Arrow
```
- `ret`: `Arrow` from the **origin** to the point (`buff=0`).
- `args`:
  - `coords: Sequence[float]` — required, data coords in x/y order.
  - `**kwargs` — forwarded to `Arrow` (`color`, `stroke_width`, …).
- `notes`: takes an x/y numeric sequence, **not** a complex number; for a complex value call `n2p` first, then draw the arrow manually.
- `see`: ../zh_CN/05-坐标系与图表/04-网格与复平面.md

### `NumberPlane.prepare_for_nonlinear_transform`
```python
def prepare_for_nonlinear_transform(self, num_inserted_curves: int = 50) -> Self
```
- `ret`: `Self`.
- `args`: `num_inserted_curves: int = 50` — minimum bezier segments inserted per path so later `ApplyFunction`-style morphs stay smooth; call once before such an animation.
- `see`: ../zh_CN/05-坐标系与图表/04-网格与复平面.md

## Guide lines & line graph

### `get_vertical_line` / `get_horizontal_line` / `get_lines_to_point`
```python
def get_vertical_line(self, point: Point3DLike, **kwargs: Any) -> Line
def get_horizontal_line(self, point: Point3DLike, **kwargs: Any) -> Line
def get_lines_to_point(self, point: Point3DLike, **kwargs: Any) -> VGroup
```
- `ret`: `Line` / `VGroup` (play or add to the scene).
- `args`:
  - `point: Point3DLike` — required target (usually from `ax.c2p(...)`).
  - `**kwargs` — forwarded to `get_line_from_axis_to_point`: `line_func`, `line_config` (e.g. `{"dashed_ratio": 0.85}`), `color`, `stroke_width`.
- `notes`: default line type `DashedLine`. Anchors are **scene points**, not data coords — call `ax.c2p(...)` first. `get_vertical_line` always starts from the x-axis; for the y-axis use `get_line_from_axis_to_point(1, ...)`.
- `see`: ../zh_CN/05-坐标系与图表/02b-引导线与折线图.md

### `get_line_from_axis_to_point`
```python
def get_line_from_axis_to_point(self, index: int, point: Point3DLike, line_func: type[Line] = DashedLine,
                                line_config: dict | None = None, color: ParsableManimColor | None = None,
                                stroke_width: float = 2) -> Line
```
- `ret`: `Line`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `index` | `int` | required | `0`=x-axis, `1`=y-axis |
| `point` | `Point3DLike` | required | target point |
| `line_func` | `type[Line]` | `DashedLine` | line class (`Line`, `Arrow`, …) |
| `line_config` | `dict \| None` | `None` | params for `line_func` |
| `color` | `ParsableManimColor \| None` | mobject default | line color |
| `stroke_width` | `float` | `2` | line width |

- `see`: ../zh_CN/05-坐标系与图表/02b-引导线与折线图.md

### `plot_line_graph`
```python
def plot_line_graph(self, x_values: Iterable[float], y_values: Iterable[float],
                    z_values: Iterable[float] | None = None, line_color: ParsableManimColor = PURE_YELLOW,
                    add_vertex_dots: bool = True, vertex_dot_radius: float = DEFAULT_DOT_RADIUS,   # 0.08
                    vertex_dot_style: dict | None = None, **kwargs: Any) -> VDict
```
- `ret`: `VDict` — polyline at `["line_graph"]`, dots at `["vertex_dots"]`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `x_values` | `Iterable[float]` | required | x data |
| `y_values` | `Iterable[float]` | required | y data (length must match x) |
| `z_values` | `Iterable[float] \| None` | `None` (all 0) | 3D data |
| `line_color` | `ParsableManimColor` | `PURE_YELLOW` | polyline color |
| `add_vertex_dots` | `bool` | `True` | draw vertex dots |
| `vertex_dot_radius` | `float` | `DEFAULT_DOT_RADIUS` (0.08) | dot radius |
| `vertex_dot_style` | `dict \| None` | `None` | style passed to `Dot` |
| `**kwargs` | — | — | passed to the polyline `VGroup` (e.g. `stroke_width=4`) |

- `notes`: discrete polyline (per-point `c2p`, no interpolation); the vertices are the data points. For a smooth curve use `ax.plot`.
- `errs`:
  - `ValueError` — `x_values`/`y_values` length mismatch (internal `zip(strict=True)`).
- `see`: ../zh_CN/05-坐标系与图表/02b-引导线与折线图.md

## Function curves

### `Axes.plot`
```python
def plot(self, function: Callable[[float], float], x_range: Sequence[float] | None = None,
         use_vectorized: bool = False, colorscale=None, colorscale_axis: int = 1,
         **kwargs: Any) -> ParametricFunction
```
- `ret`: `ParametricFunction`. Attrs: `underlying_function`, `t_min`, `t_max`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `function` | `Callable[[float], float]` | required | e.g. `lambda x: np.sin(x)` |
| `x_range` | `Sequence[float] \| None` | `None` = full x-axis | `[x_min, x_max]` or `[x_min, x_max, x_step]`; `x_step` is the **sampling** step (not ticks) |
| `use_vectorized` | `bool` | `False` | set `True` if the function accepts arrays — big speedup |
| `colorscale` | color seq / `(color, pivot)` seq \| `None` | `None` | color by value; **must be passed together with `x_range`** or `TypeError` |
| `colorscale_axis` | `int` | `1` | gradient axis: `0`=x, `1`=y |
| `color` | `ParsableManimColor` | `PURE_YELLOW` | curve color (via `**kwargs`) |
| `discontinuities` | `Iterable[float] \| None` | `None` | x values of discontinuities, e.g. `[-2, 2]`; omitting them draws a connecting vertical line |
| `dt` | `float` | `1e-8` | tolerance around discontinuities; use `0.1` in practice |
| `use_smoothing` | `bool` | `True` | smoothing (turn off for sparse/steep functions) |
| `stroke_width` | `float` | inherited | line width |

- `notes`:
  - There is **no** `ax.get_graph(...)` / `plot_area` alias; `ax.plot(...)` is the only entry point.
  - Functions with vertical asymptotes must clamp y (e.g. `max(-60, min(60, ...))`) — the poles produce `1e14`-scale values that break rendering.
  - `dt` default `1e-8` is too small; use `0.1`.
- `errs`:
  - `TypeError` — `colorscale` passed without `x_range`.
- `see`: ../zh_CN/05-坐标系与图表/05-函数曲线.md
- `eg`:
```python
ax = NumberPlane(x_range=[-3, 3, 1], y_range=[-4, 4, 1])
good = ax.plot(lambda x: (x**2 - 2) / (x**2 - 4), discontinuities=[-2, 2], dt=0.1,
               color=GREEN, use_smoothing=False)
```

### `FunctionGraph`
```python
def __init__(self, function: Callable[[float], Any], x_range: tuple | None = None,
             color: ParsableManimColor = PURE_YELLOW, **kwargs: Any) -> None
```
- `ret`: `FunctionGraph` (`ParametricFunction` subclass). `get_function()` returns the raw function.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `function` | `Callable[[float], Any]` | required | e.g. `lambda t: np.cos(t)` |
| `x_range` | `tuple \| None` | `None` → `(-frame_x_radius, frame_x_radius)` | sampling range (third element = step) |
| `color` | `ParsableManimColor` | `PURE_YELLOW` | curve color |
| `**kwargs` | — | — | forwarded to `ParametricFunction` (`discontinuities`, `use_smoothing`, …) |

- `notes`: draws `y = f(x)` with **no** coordinate system (defaults to full frame width). `x_range` is a sampling range, not data coords — for ticks/grid use `ax.plot`.
- `see`: ../zh_CN/05-坐标系与图表/05-函数曲线.md
- `eg`:
```python
g1 = FunctionGraph(lambda t: np.cos(3 * t), x_range=[-4, 4], color=BLUE)
g2 = FunctionGraph(lambda t: np.sin(3 * t), x_range=[-4, 4], color=GREEN)
```

### `ParametricFunction`
```python
def __init__(self, function: Callable[[float], Point3DLike], t_range: tuple = (0, 1),
             scaling: _ScaleBase = LinearBase(), dt: float = 1e-8,
             discontinuities: Iterable[float] | None = None, use_smoothing: bool = True,
             use_vectorized: bool = False, **kwargs: Any) -> None
```
- `ret`: `ParametricFunction` (`VMobject`); the base class of `Axes.plot` results.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `function` | `Callable[[float], Point3DLike]` | required | `lambda t: (x(t), y(t), z(t))` |
| `t_range` | `tuple` | `(0, 1)` | `(t_min, t_max)` or `(t_min, t_max, step)`; a 2-tuple appends `0.01` |
| `scaling` | `_ScaleBase` | `LinearBase()` | parameter scaling (a log axis inherits its own scaling) |
| `dt` | `float` | `1e-8` | discontinuity tolerance |
| `discontinuities` | `Iterable[float] \| None` | `None` | discontinuities on `t` |
| `use_smoothing` | `bool` | `True` | smoothing |
| `use_vectorized` | `bool` | `False` | pass the whole `t` array (output shape `[[x…],[y…],[z…]]`) |
| `**kwargs` | — | — | forwarded to `VMobject` |

- `notes`: `function` returns **scene** points; contrast with `plot_parametric_curve` (returns data coords).
- `see`: ../zh_CN/05-坐标系与图表/05-函数曲线.md

### `CoordinateSystem.plot_parametric_curve`
```python
def plot_parametric_curve(self, function: Callable[[float], np.ndarray],
                          use_vectorized: bool = False, **kwargs: Any) -> ParametricFunction
```
- `ret`: `ParametricFunction`.
- `args`:
  - `function: Callable[[float], np.ndarray]` — required, returns **data** coords, e.g. `lambda t: np.array([x(t), y(t), 0])`; auto `c2p`.
  - `use_vectorized: bool = False` — function supports vectorized input.
  - `**kwargs` — forwarded to `ParametricFunction`; **`t_range` also goes here** (e.g. `t_range=[0, 2*PI]`).
- `notes`: to keep a parametric figure (e.g. a Lissajous curve) undistorted, set equal x/y scales (`x_length == y_length` over equal ranges). Do not put `t_range` in the function's own args.
- `see`: ../zh_CN/05-坐标系与图表/05-函数曲线.md

## Curve labels & helper lines

### `Axes.plot_implicit_curve`
```python
def plot_implicit_curve(self, func: Callable[[float, float], float],
                        min_depth: int = 5, max_quads: int = 1500,
                        **kwargs: Any) -> ImplicitFunction
```
- `ret`: `ImplicitFunction`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `func` | `Callable[[float, float], float]` | required | e.g. `lambda x, y: x**2 + y**2 - 4`, zero contour |
| `min_depth` | `int` | `5` | quadtree min depth (smaller = faster, coarser) |
| `max_quads` | `int` | `1500` | max subdivision blocks |
| `**kwargs` | — | — | forwarded to the curve (`color`, `stroke_width`, …) |

- `notes`:
  - Evaluated only inside the system's framing; parts outside are not drawn — make `x_range`/`y_range` enclose the whole curve.
  - The returned `ImplicitFunction` **cannot** be fed to methods that need an analytic function (`get_area`, `plot_derivative_graph`, …).
- `see`: ../zh_CN/05-坐标系与图表/05b-曲线标注与辅助线.md

### `Axes.get_graph_label`
```python
def get_graph_label(self, graph: ParametricFunction, label: float | str | VMobject = "f(x)",
                    x_val: float | None = None, direction: Sequence[float] = RIGHT,
                    buff: float = MED_SMALL_BUFF, color: ParsableManimColor | None = None,
                    dot: bool = False, dot_config: dict | None = None) -> Mobject
```
- `ret`: `Mobject` label (and dot if requested).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `graph` | `ParametricFunction` | required | the `ax.plot` return value |
| `label` | `float \| str \| VMobject` | `"f(x)"` | label content (`str` → `MathTex`) |
| `x_val` | `float \| None` | `None` → curve midpoint | x where the label sits |
| `direction` | `Sequence[float]` | `RIGHT` | side relative to the dot, e.g. `DL` |
| `buff` | `float` | `MED_SMALL_BUFF` (0.25) | gap to the dot |
| `color` | `ParsableManimColor \| None` | `None` → curve color | label color |
| `dot` | `bool` | `False` | also add a dot on the curve |
| `dot_config` | `dict \| None` | `None` | dot config (`radius`, `color`, …) |

- `notes`: `label` renders via `MathTex` — write `x^2`, not `x²`.
- `see`: ../zh_CN/05-坐标系与图表/05b-曲线标注与辅助线.md
- `eg`:
```python
label = ax.get_graph_label(curve, "x^2", x_val=-2, direction=DL, dot=True)
```

### `Axes.get_T_label`
```python
def get_T_label(self, x_val: float, graph: ParametricFunction, label: float | str | Mobject | None = None,
                label_color: ParsableManimColor | None = None, triangle_size: float = MED_SMALL_BUFF,
                triangle_color: ParsableManimColor | None = WHITE, line_func: type[Line] = Line,
                line_color: ParsableManimColor = PURE_YELLOW) -> VGroup
```
- `ret`: `VGroup` = triangle on the x-axis + vertical line to the curve + optional text.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `x_val` | `float` | required | marker x |
| `graph` | `ParametricFunction` | required | curve the line reaches |
| `label` | `float \| str \| Mobject \| None` | `None` → no text | text label (`str` → `MathTex`) |
| `label_color` | `ParsableManimColor \| None` | `None` | text color |
| `triangle_size` | `float` | `MED_SMALL_BUFF` (0.25) | triangle size |
| `triangle_color` | `ParsableManimColor \| None` | `WHITE` | triangle color |
| `line_func` | `type[Line]` | `Line` | vertical line class (e.g. `DashedLine`) |
| `line_color` | `ParsableManimColor` | `PURE_YELLOW` | vertical line color |

- `notes`: triangle color and text color are set separately via `triangle_color` / `label_color`.
- `see`: ../zh_CN/05-坐标系与图表/05b-曲线标注与辅助线.md

### `Axes.get_vertical_lines_to_graph`
```python
def get_vertical_lines_to_graph(self, graph: ParametricFunction, x_range: Sequence[float] | None = None,
                                num_lines: int = 20, **kwargs: Any) -> VGroup
```
- `ret`: `VGroup` of vertical dashed lines from the x-axis to the curve.
- `args`:
  - `graph: ParametricFunction` — required target curve.
  - `x_range: Sequence[float] | None` — `None` → full curve range; `[x_min, x_max]` distribution interval.
  - `num_lines: int = 20` — number of lines.
  - `**kwargs` — forwarded to each `DashedLine` (`color`, `stroke_width`, …).
- `see`: ../zh_CN/05-坐标系与图表/05b-曲线标注与辅助线.md

### `Axes.get_secant_slope_group`
```python
def get_secant_slope_group(self, x: float, graph: ParametricFunction, dx: float | None = None,
                           dx_line_color: ParsableManimColor = PURE_YELLOW,
                           dy_line_color: ParsableManimColor | None = None,
                           dx_label: float | str | None = None, dy_label: float | str | None = None,
                           include_secant_line: bool = True,
                           secant_line_color: ParsableManimColor = GREEN,
                           secant_line_length: float = 10) -> VGroup
```
- `ret`: `VGroup` = Δx horizontal segment + Δy vertical segment + optional labels + secant line.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `x` | `float` | required | secant start x |
| `graph` | `ParametricFunction` | required | target curve |
| `dx` | `float \| None` | `None` → 10% of x-axis length | horizontal increment |
| `dx_line_color` | `ParsableManimColor` | `PURE_YELLOW` | Δx segment color |
| `dy_line_color` | `ParsableManimColor \| None` | `None` → same as dx | Δy segment color |
| `dx_label` / `dy_label` | `float \| str \| None` | `None` | segment text labels |
| `include_secant_line` | `bool` | `True` | include the secant itself |
| `secant_line_color` | `ParsableManimColor` | `GREEN` | secant color |
| `secant_line_length` | `float` | `10` | secant length (**scene** units) |

- `notes`: `secant_line_length` is in scene units, not data units — use a small value (e.g. `4`) to keep it on-screen. `dx_label`/`dy_label` render via `MathTex`.
- `see`: ../zh_CN/05-坐标系与图表/05b-曲线标注与辅助线.md

## Derivative / antiderivative / tangent

### `Axes.input_to_graph_point` / `i2gp`
```python
def input_to_graph_point(self, x: float, graph: ParametricFunction | VMobject) -> Point3D
```
- `ret`: **scene** point on the curve at `x` (feed to `Dot`, distance math).
- `args`: `x: float` — required; `graph: ParametricFunction | VMobject` — required (`ax.plot` return value).
- `notes`: all graph methods here are **numeric**; `graph` must be the `ax.plot` result (it reads its sampler). `i2gp` → scene coords; `i2gc` → data coords — do not swap them.
- `see`: ../zh_CN/05-坐标系与图表/05c-导数原函数与切线.md

### `Axes.input_to_graph_coords` / `i2gc`
```python
def input_to_graph_coords(self, x: float, graph: ParametricFunction) -> tuple[float, float]
```
- `ret`: **data** coords `(x, y)` on the curve.
- `args`: `x: float` — required; `graph: ParametricFunction` — required.
- `see`: ../zh_CN/05-坐标系与图表/05c-导数原函数与切线.md

### `Axes.plot_derivative_graph`
```python
def plot_derivative_graph(self, graph: ParametricFunction, color: ParsableManimColor = GREEN,
                          **kwargs: Any) -> ParametricFunction
```
- `ret`: derivative curve (`ParametricFunction`), same framing as the source curve.
- `args`:
  - `graph: ParametricFunction` — required curve to differentiate.
  - `color: ParsableManimColor = GREEN` — derivative curve color.
  - `**kwargs` — forwarded to `ParametricFunction`.
- `notes`: **numeric** central difference `(f(x+h)-f(x-h))/2h`; errors near steep parts or discontinuities.
- `see`: ../zh_CN/05-坐标系与图表/05c-导数原函数与切线.md

### `Axes.plot_antiderivative_graph`
```python
def plot_antiderivative_graph(self, graph: ParametricFunction, y_intercept: float = 0,
                              samples: int = 50, use_vectorized: bool = False,
                              **kwargs: Any) -> ParametricFunction
```
- `ret`: antiderivative curve (`ParametricFunction`).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `graph` | `ParametricFunction` | required | curve to integrate |
| `y_intercept` | `float` | `0` | integration constant (y-intercept) |
| `samples` | `int` | `50` | integration sample count (larger = more accurate, slower) |
| `use_vectorized` | `bool` | `False` | set `True` if the function accepts arrays |
| `**kwargs` | — | — | forwarded to `ParametricFunction` |

- `notes`: trapezoidal integration, numeric. Integration starts fixed at the minimum x; `y_intercept` only shifts vertically.
- `see`: ../zh_CN/05-坐标系与图表/05c-导数原函数与切线.md

### `Axes.slope_of_tangent`
```python
def slope_of_tangent(self, x: float, graph: ParametricFunction, **kwargs: Any) -> float
```
- `ret`: tangent slope at `x` (**data** slope dy/dx).
- `args`:
  - `x: float` — required tangent point x.
  - `graph: ParametricFunction` — required curve.
  - `**kwargs` — forwarded to the underlying difference (e.g. `dx`).
- `notes`: the value is a data slope — use it to extrapolate in data coords, **not** as a screen slope (they differ when x/y scales differ).
- `see`: ../zh_CN/05-坐标系与图表/05c-导数原函数与切线.md

### `Axes.angle_of_tangent`
```python
def angle_of_tangent(self, x: float, graph: ParametricFunction, dx: float = 1e-8) -> float
```
- `ret`: tangent angle to the x-axis in **radians** (`atan(slope_of_tangent(x))`).
- `args`: `x: float` — required; `graph: ParametricFunction` — required; `dx: float = 1e-8` — difference step.
- `see`: ../zh_CN/05-坐标系与图表/05c-导数原函数与切线.md

## Area & Riemann rectangles

### `Axes.get_area`
```python
def get_area(self, graph: ParametricFunction, x_range: tuple[float, float] | None = None,
             color: ParsableManimColor | Iterable[ParsableManimColor] = (BLUE, GREEN),
             opacity: float = 0.3, bounded_graph: ParametricFunction | None = None,
             **kwargs: Any) -> Polygon
```
- `ret`: `Polygon` = area under the curve over `x_range` (or between two curves).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `graph` | `ParametricFunction` | required | target curve |
| `x_range` | `tuple[float, float] \| None` | `None` → full curve range | x interval of the area |
| `color` | single / sequence | `(BLUE, GREEN)` | a list creates an x-gradient |
| `opacity` | `float` | `0.3` | fill opacity |
| `bounded_graph` | `ParametricFunction \| None` | `None` | upper boundary; with it the area is **between** the two curves |
| `**kwargs` | — | — | forwarded to `Polygon` |

- `notes`: `bounded_graph` must be **above** `graph`, else the area is negative and direction flips. The returned `Polygon` accepts `FadeIn`/`Transform`.
- `see`: ../zh_CN/05-坐标系与图表/06-面积与黎曼矩形.md
- `eg`:
```python
area = ax.get_area(quad, x_range=(0, 2), color=(GREEN_B, GREEN_D), opacity=1)
area2 = ax.get_area(quad, x_range=(-1.5, 1.5), bounded_graph=bound, opacity=0.6)
```

### `Axes.get_riemann_rectangles`
```python
def get_riemann_rectangles(self, graph: ParametricFunction, x_range: Sequence[float] | None = None,
                           dx: float = 0.1, input_sample_type: str = "left", stroke_width: float = 1,
                           stroke_color: ParsableManimColor = BLACK, fill_opacity: float = 1,
                           color: Iterable[ParsableManimColor] | ParsableManimColor = (BLUE, GREEN),
                           show_signed_area: bool = True, bounded_graph: ParametricFunction | None = None,
                           blend: bool = False, width_scale_factor: float = 1.001) -> VGroup
```
- `ret`: `VGroup` of Riemann rectangles.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `graph` | `ParametricFunction` | required | curve being approximated |
| `x_range` | `Sequence[float] \| None` | `None` → full curve range | rectangle distribution interval |
| `dx` | `float` | `0.1` | rectangle width (data units) |
| `input_sample_type` | `str` | `"left"` | sample point: `"left"`/`"right"`/`"center"` |
| `stroke_width` | `float` | `1` | rectangle stroke width |
| `stroke_color` | `ParsableManimColor` | `BLACK` | stroke color |
| `fill_opacity` | `float` | `1` | fill opacity |
| `color` | color / color seq | `(BLUE, GREEN)` | single color or gradient (interpolated by position) |
| `show_signed_area` | `bool` | `True` | invert color for negative area below the x-axis |
| `bounded_graph` | `ParametricFunction \| None` | `None` | rectangles between two curves |
| `blend` | `bool` | `False` | blend adjacent rectangle colors |
| `width_scale_factor` | `float` | `1.001` | width tweak to remove stroke gaps |

- `notes`: smaller `dx` = better approximation but slower. `input_sample_type` must be the full word — abbreviations are not accepted. Negative-area inversion is controlled by `show_signed_area`.
- `see`: ../zh_CN/05-坐标系与图表/06-面积与黎曼矩形.md

## Polar & 3D

### `PolarPlane`
```python
def __init__(self, radius_max: float = config["frame_y_radius"], size: float | None = None,
             radius_step: float = 1, azimuth_step: float | None = None,
             azimuth_units: str = "PI radians", azimuth_compact_fraction: bool = True,
             azimuth_offset: float = 0, azimuth_direction: str = "CCW",
             azimuth_label_buff: float = SMALL_BUFF, azimuth_label_font_size: float = 24,
             radius_config: dict | None = None, background_line_style: dict | None = None,
             faded_line_style: dict | None = None, faded_line_ratio: int = 1,
             make_smooth_after_applying_functions: bool = True, **kwargs: Any)
```
- `ret`: `PolarPlane` (`Axes` subclass). Concentric circles = radius ticks, radial lines = angle ticks; `add_coordinates()` adds radius numbers + angle labels.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `radius_max` | `float` | `config["frame_y_radius"]` (4.0) | max radius |
| `size` | `float \| None` | `None` | plane diameter (overrides radius auto-scaling) |
| `radius_step` | `float` | `1` | concentric circle spacing |
| `azimuth_step` | `float \| None` | `None` | radial line spacing (fractions of π) |
| `azimuth_units` | `str` | `"PI radians"` | `"PI radians"`/`"TAU radians"`/`"radians"`/`"degrees"`/`"gradians"`/`None` |
| `azimuth_compact_fraction` | `bool` | `True` | compact fraction labels |
| `azimuth_offset` | `float` | `0` | angle offset |
| `azimuth_direction` | `str` | `"CCW"` | `"CCW"`/`"CW"` |
| `azimuth_label_buff` | `float` | `SMALL_BUFF` (0.1) | angle label gap |
| `azimuth_label_font_size` | `float` | `24` | angle label font size |
| `radius_config` | `dict \| None` | `None` | radius label/line config |
| `background_line_style` | `dict \| None` | `None` | circle + radial line style (`stroke_color`/`stroke_width`…) |
| `faded_line_style` | `dict \| None` | `None` | faded subdivision line style |
| `faded_line_ratio` | `int` | `1` | subdivision density (`0` = off) |
| `make_smooth_after_applying_functions` | `bool` | `True` | no effect currently |

- `notes`: RTM vs CE — `Create(PolarPlane)` intermediate frames differ slightly in draw order; the final frame is identical (verify by the last frame). `plot_polar_graph` takes `r(θ)` returning a **radius** scalar, not coords.
- `errs`:
  - `ValueError: "Invalid azimuth units. Expected one of: PI radians, TAU radians, degrees, gradians or None."` — bad `azimuth_units` → use one of the listed values.
- `see`: ../zh_CN/05-坐标系与图表/07-极坐标与三维坐标系.md

### `plot_polar_graph`
```python
def plot_polar_graph(self, r_func: Callable[[float], float], theta_range: Sequence[float] | None = None,
                     **kwargs: Any) -> ParametricFunction
```
- `ret`: `ParametricFunction`.
- `args`:
  - `r_func: Callable[[float], float]` — required, `r(θ)` returning a scalar radius.
  - `theta_range: Sequence[float] | None` — `[theta_min, theta_max, theta_step]`.
  - `**kwargs` — forwarded to `ParametricFunction`.
- `notes`: `r_func` returns a **radius** (scalar), not coords.
- `see`: ../zh_CN/05-坐标系与图表/07-极坐标与三维坐标系.md
- `eg`:
```python
plane = PolarPlane(size=5, azimuth_units="PI radians").add_coordinates()
rose = plane.plot_polar_graph(lambda th: 2 * np.sin(th * 5), theta_range=[0, TAU], color=ORANGE)
```

### `ThreeDAxes`
```python
def __init__(self, x_range: Sequence[float] | None = (-6, 6, 1), y_range: Sequence[float] | None = (-5, 5, 1),
             z_range: Sequence[float] | None = (-4, 4, 1),
             x_length: float | None = config.frame_height + 2.5,     # 10.5
             y_length: float | None = config.frame_height + 2.5,     # 10.5
             z_length: float | None = config.frame_height - 1.5,     # 6.5
             z_axis_config: dict | None = None, z_normal: Vector3DLike = DOWN,
             num_axis_pieces: int = 20, light_source: Point3DLike = 9 * DOWN + 7 * LEFT + 10 * OUT,
             depth: Any = None, gloss: float = 0.5, **kwargs: Any)
```
- `ret`: `ThreeDAxes` (`Axes` subclass); 3 axes + `c2p(x, y, z)`; `add_coordinates(x, y, z)` per-axis.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `x_range` / `y_range` / `z_range` | `Sequence[float] \| None` | `(-6,6,1)`/`(-5,5,1)`/`(-4,4,1)` | per-axis data range + tick step |
| `x_length` / `y_length` / `z_length` | `float \| None` | `10.5`/`10.5`/`6.5` | per-axis screen length |
| `z_axis_config` | `dict \| None` | `None` | z-axis style |
| `z_normal` | `Vector3DLike` | `DOWN` (`[0,-1,0]`) | z-axis direction |
| `num_axis_pieces` | `int` | `20` | axis tessellation pieces |
| `light_source` | `Point3DLike` | `9*DOWN + 7*LEFT + 10*OUT` (`[-7,-9,10]`) | light position |
| `depth` | `Any` | `None` | depth param |
| `gloss` | `float` | `0.5` | **upstream param; RTM's Vulkan path does not read it (no visual effect)** — it only exists in manim's OpenGL shader (`manim/renderer/shaders/**/*.glsl`) |

- `notes`: use `ThreeDScene` for 3D; the order is `win.scene = self`, then `self.play = win.play`, before `move_camera` (which calls `self.play` internally). `add_coordinates(x_labels, None, z_labels)` maps to x/y/z (`None` = default ticks).
- `see`: ../zh_CN/05-坐标系与图表/07-极坐标与三维坐标系.md
- `eg`:
```python
ax = ThreeDAxes(x_range=(-3, 3, 1), y_range=(-3, 3, 1), z_range=(-4, 4, 1),
                x_length=7, y_length=7, z_length=5)
ax.add_coordinates(range(-2, 3), None, range(-4, 5, 2))
d1 = Dot(ax.c2p(1, 1, 2), color=RED)
```

### `Axes.plot_surface`
```python
def plot_surface(self, function: Callable[[float], float], u_range: Sequence[float] | None = None,
                 v_range: Sequence[float] | None = None, colorscale=None, colorscale_axis: int = 2,
                 **kwargs: Any) -> Surface | OpenGLSurface
```
- `ret`: `Surface`; behaves like a normal mobject (`FadeIn`/`Create`/transform).
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `function` | `Callable[[float, float], float]` | required | height function `f(u, v)` |
| `u_range` / `v_range` | `Sequence[float] \| None` | `None` | the two parameter intervals |
| `colorscale` | color seq / `(color, pivot)` seq \| `None` | `None` | color by z-value |
| `colorscale_axis` | `int` | `2` | gradient axis (`0`=x, `1`=y, `2`=z) |
| `resolution` | `Sequence[int]` | `(32, 32)` | **passed via `**kwargs`** to `Surface`; segments per u/v direction (not point count) |

- `notes`: a **parametric** surface `(u,v) → f(u,v)`, distinct from `plot` (`x → f(x)`). `resolution` is a segment count — `(12, 12)` gives 144 patches; too few makes it polygonal. RTM aligned frame-by-frame with ManimCE (198 frames / 3.30 s, `tests/test_plot_surface.py`).
- `see`: ../zh_CN/05-坐标系与图表/07-极坐标与三维坐标系.md
- `eg`:
```python
surf = ax.plot_surface(lambda u, v: np.sin(u) * np.cos(v),
                       u_range=(-3, 3), v_range=(-3, 3), resolution=(12, 12))
```

## BarChart

### `BarChart`
```python
def __init__(self, values: MutableSequence[float], bar_names: Sequence[str] | None = None,
             y_range: Sequence[float] | None = None, x_length: float | None = None,
             y_length: float | None = None,
             bar_colors: Iterable[str] = ["#003f5c", "#58508d", "#bc5090", "#ff6361", "#ffa600"],
             bar_width: float = 0.6, bar_fill_opacity: float = 0.7, bar_stroke_width: float = 3,
             **kwargs: Any)
```
- `ret`: `BarChart` (`Axes` subclass) — so `c2p`/`plot`/`get_area`/`x_axis_config`/`y_axis_config` all work. Attrs: `bars` (`VGroup[Rectangle]`), `values`, `bar_names`, `bar_colors`, `x_labels`, `bar_labels`.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `values` | `MutableSequence[float]` | required | bar values, **may be negative** |
| `bar_names` | `Sequence[str] \| None` | `None` | x-axis labels; shorter than `values` is fine, **longer raises IndexError**; negative-bar labels auto-place above the axis |
| `y_range` | `Sequence[float] \| None` | auto `[min(0, min(v)), max(0, max(v)), round(max(v)/y_length, 2)]` | y range + step; a 2-tuple auto-appends the step |
| `x_length` | `float \| None` | `min(len(values), frame_width - 2)` | x-axis length |
| `y_length` | `float \| None` | `config.frame_height - 4` (=4) | y-axis length |
| `bar_colors` | `Iterable[str]` | 5-color palette (see signature) | bar colors; a length ≠ `values` auto-gradients; **must be a list** (a `str` is deprecated since v0.15.2 and removed after v0.17.0 with a warning) |
| `bar_width` | `float` | `0.6` | bar width (0–1, fraction of the cell) |
| `bar_fill_opacity` | `float` | `0.7` | fill opacity |
| `bar_stroke_width` | `float` | `3` | bar stroke width |
| `**kwargs` | — | — | forwarded to `Axes`: `x_axis_config`, `y_axis_config`, `y_range`, … |

- `notes`: fixes `x_range=[0, len(values), 1]` and `tips=False`; x-axis defaults `font_size=24`, `label_constructor=Tex`. RTM renders via the generic vector fallback path (verified 2026-10-11).
- `errs`:
  - `IndexError` — `bar_names` longer than `values`.
- `see`: ../zh_CN/05-坐标系与图表/08-图表BarChart.md
- `eg`:
```python
chart = BarChart(values=[-4, 6, -2, 3], bar_names=["one", "two", "three", "four"],
                 y_range=[-7, 9, 2], y_length=5.5, x_length=10,
                 x_axis_config={"font_size": 24})
labels = chart.get_bar_labels(color=WHITE, font_size=24)
```

### `BarChart.get_bar_labels`
```python
def get_bar_labels(self, color: ParsableManimColor | None = None, font_size: float = 24,
                   buff: float = MED_SMALL_BUFF, label_constructor: type[MathTex] = Tex) -> VGroup
```
- `ret`: `VGroup` of value labels (positive bars above, negative below). **Returns only** — add it yourself; it does **not** write back to `chart.bar_labels` (which is `None` at construction), so store the return value.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `color` | `ParsableManimColor \| None` | `None` (follows bar fill) | label color |
| `font_size` | `float` | `24` | font size |
| `buff` | `float` | `MED_SMALL_BUFF` (0.25) | gap to the bar |
| `label_constructor` | `type[MathTex]` | `Tex` | text class (`MathTex` for math font) |

- `see`: ../zh_CN/05-坐标系与图表/08-图表BarChart.md

### `BarChart.change_bar_values`
```python
def change_bar_values(self, values: Iterable[float], update_colors: bool = True) -> Self
```
- `ret`: `Self`.
- `args`:
  - `values: Iterable[float]` — required new bar values.
  - `update_colors: bool = True` — re-apply the `bar_colors` gradient.
- `notes`: updates bar heights **in place** (does not rebuild the chart); the core method for value-growth animations (`Transform`/`always_redraw`). The new `values` length need not match the old (extra entries ignored; a bar whose old height was 0 is rebuilt). Calling it directly jumps on the next frame — wrap it as `chart.animate.change_bar_values(...)` for a smooth transition.
- `see`: ../zh_CN/05-坐标系与图表/08-图表BarChart.md

## Probability — SampleSpace

### `SampleSpace`
```python
def __init__(self, height: float = 3, width: float = 3, fill_color: ParsableManimColor = DARK_GREY,
             fill_opacity: float = 1, stroke_width: float = 0.5,
             stroke_color: ParsableManimColor = LIGHT_GREY, default_label_scale_val: float = 1)
```
- `ret`: `SampleSpace` (`Rectangle` subclass); `sample_space[i]` indexes the i-th part.
- `args`:

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `height` / `width` | `float` | `3` / `3` | size |
| `fill_color` | `ParsableManimColor` | `DARK_GREY` | fill color |
| `fill_opacity` | `float` | `1` | opacity |
| `stroke_width` | `float` | `0.5` | stroke width |
| `stroke_color` | `ParsableManimColor` | `LIGHT_GREY` | stroke color |
| `default_label_scale_val` | `float` | `1` | label scale factor |

- `notes`: RTM renders via the generic vector fallback path (verified 2026-10-11). The manual only documents `SampleSpace` (no `Tree`/`Bayes` etc.).
- `see`: ../zh_CN/05-坐标系与图表/09-概率与SampleSpace.md

### `SampleSpace` methods
```python
def add_title(self, title: str = "Sample space", buff: float = MED_SMALL_BUFF) -> Self
def divide_horizontally(self, *args: Any, **kwargs: Any) -> Self
def divide_vertically(self, *args: Any, **kwargs: Any) -> Self
def get_horizontal_division(self, p_list, colors=[GREEN_E, BLUE_E], vect=DOWN) -> VGroup
def get_vertical_division(self, p_list, colors=[MAROON_B, YELLOW], vect=RIGHT) -> VGroup
def get_division_along_dimension(self, p_list, dim, colors, vect) -> VGroup
def complete_p_list(self, p_list: float | Iterable[float]) -> list[float]
def add_label(self, label: str) -> Self
def add_braces_and_labels(self) -> Self
def get_subdivision_braces_and_labels(self, parts, labels, direction, buff=0.1, min_num_quads=1) -> VGroup
def get_side_braces_and_labels(self, labels, direction=LEFT, **kwargs) -> VGroup
def get_top_braces_and_labels(self, labels, **kwargs) -> VGroup
def get_bottom_braces_and_labels(self, labels, **kwargs) -> VGroup
```
- `ret`: `Self` for `add_title`/`divide_*`/`add_label`/`add_braces_and_labels`; `VGroup` for the `get_*` division/brace helpers.
- `args` (division helpers):

| arg | type | default | meaning |
| --- | --- | --- | --- |
| `p_list` | `float \| Iterable[float]` | required | part proportions (sum < 1 auto-fills the remainder) |
| `colors` | `Sequence[ParsableManimColor]` | see method table | palette (gradient-interpolated) |
| `vect` | `Vector3D` | see method table | split/label direction |
| `labels` | `list[str \| VMobject]` | required | per-part labels |
| `buff` | `float` | `0.1` | brace gap |
| `min_num_quads` | `int` | `1` | brace subdivision count |
| `dim` | `int` | required | `0`=vertical, `1`=horizontal |

- `notes`:
  - `divide_horizontally` stores into `horizontal_parts` and adds them to self; `divide_vertically` stores into `vertical_parts`.
  - `get_horizontal_division`/`get_vertical_division`/`get_division_along_dimension` generate blocks **without** adding them.
  - `complete_p_list` appends `1 - sum` when the total is below 1 (within `EPSILON`).
  - `add_title` internally builds `Tex(title)` — do not put `_` in the title (math subscript → `Missing $ inserted`); escape it or use `Text`.
  - The four brace helpers (`get_side_braces_and_labels`, `get_top_braces_and_labels`, `get_bottom_braces_and_labels`, `get_subdivision_braces_and_labels`) are **unusable in manim 0.21** (both engines): `get_subdivision_braces_and_labels` forwards `min_num_quads` to `Brace(...)` (`manim/mobject/graphing/probability.py:159`) which no longer accepts it. For braces use `Brace(part, direction)` + `brace.get_text(...)`. `parts.braces`/`parts.labels` are only populated by those broken helpers.
- `errs`:
  - `TypeError: Mobject.__init__() got an unexpected keyword argument 'min_num_quads'` — any of the four brace helpers → build braces manually.
- `see`: ../zh_CN/05-坐标系与图表/09-概率与SampleSpace.md
- `eg`:
```python
poly = SampleSpace(width=2, height=2, stroke_width=5, fill_opacity=0.1)
poly.divide_vertically(p_list=np.array([0.37, 0.13, 0.5]), colors=[BLACK, WHITE, GRAY], vect=RIGHT)
poly.add_title("Sample space")
b0 = Brace(poly.vertical_parts[0], LEFT); t0 = b0.get_text("0.37")
```

## Ticks & scales

### `_ScaleBase`
```python
class _ScaleBase:
    def __init__(self, custom_labels: bool = False)
    def function(self, value) -> float            # must override
    def inverse_function(self, value) -> float    # must override
    def get_custom_labels(self, val_range, **kw_args) -> Iterable[VMobject]   # optional override
```
- `ret`: base class for `scaling=` values (public extension point despite the leading underscore).
- `args`:
  - `custom_labels: bool = False` — route `get_custom_labels` when `True`.
- `notes`:
  - `function`: value → axis logical position (`NumberLine` runs all of `x_range` through it).
  - `inverse_function`: inverse of `function`; `n2p`/`p2c` use it to recover real values.
  - `get_custom_labels(val_range)`: returns labels one-to-one with `val_range`; only used when `custom_labels=True`.
  - The manual does not include `SqrtBase`; for a sqrt/square axis, subclass `_ScaleBase` and override `function`/`inverse_function`.
- `see`: ../zh_CN/05-坐标系与图表/10-刻度与缩放.md

### `LinearBase`
```python
def __init__(self, scale_factor: float = 1.0)
```
- `ret`: linear scale, `function(v) = scale_factor * v`; the default `scaling` of all axes (`custom_labels=False`).
- `args`: `scale_factor: float = 1.0` — slope.
- `notes`: tick position = `scaling.function(value)` mapped onto the axis, so `scale_factor=1.5` pushes each tick out 1.5× (0 fixed) while label values are unchanged. When `scale_factor ≠ 1` ticks no longer fill the line — manim does not re-normalize (upstream behavior, both engines).
- `see`: ../zh_CN/05-坐标系与图表/10-刻度与缩放.md
- `eg`:
```python
wide = NumberLine(x_range=[0, 6, 1], length=9,
                  scaling=LinearBase(scale_factor=1.5), include_numbers=True)
```

### `LogBase`
```python
def __init__(self, base: float = 10, custom_labels: bool = True)
```
- `ret`: log scale; pass to `NumberLine(scaling=...)` or `Axes(y_axis_config={"scaling": LogBase(...)})`. Turns the linear step into `base**k` decade ticks and generates `10^2`-style LaTeX labels.
- `args`: `base: float = 10` — log base; `custom_labels: bool = True` — use `10^k` custom labels (`False` → plain numbers).
- `notes`:
  - Methods (auto-called, callable manually): `function(value) -> float` = `base ** value`; `inverse_function(value) -> float` (real value → exponent; **raises on `value <= 0`**); `get_custom_labels(val_range, unit_decimal_places=0, **base_config) -> list[Integer]`.
  - `LogBase` on `NumberLine`: `NumberLine(x_range=[0, 6, 1], scaling=LogBase(base=10), include_numbers=True)` crashes (log of 0). Even with `x_range=[1, 6, 1]` manim places ticks off the line (measured: with `length=9` ticks land at x≈-6.3…-4.9 and `include_numbers` produces 0 labels). To demo a log axis use `Axes(y_axis_config={"scaling": LogBase(...)})` — the working path.
  - `plot`'s `x_range` lower bound must be `> 0`.
- `errs`:
  - `ValueError: "log(0) is undefined"` — `inverse_function(value <= 0)` → keep axis/plot lower bounds `> 0`.
- `see`: ../zh_CN/05-坐标系与图表/10-刻度与缩放.md
- `eg`:
```python
ax = Axes(x_range=[0, 10, 1], y_range=[-2, 6, 1], tips=False,
          axis_config={"include_numbers": True},
          y_axis_config={"scaling": LogBase(custom_labels=True)})
graph = ax.plot(lambda x: x**2, x_range=[0.001, 10], use_smoothing=False)
```
