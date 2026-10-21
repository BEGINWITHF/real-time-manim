# graphs & vector fields

> scope: `Graph`/`DiGraph` (networkx-backed topology + updater-driven edges), graph mutation/layout, `VectorField`/`ArrowVectorField`, `StreamLines` in RTM (`real_time_manim`). Data model is bundled ManimCE 0.21.0; RTM only rasterizes it.
> src: `real_time_manim/manim/mobject/graph.py`, `real_time_manim/manim/mobject/vector_field.py`; RTM overlay `real_time_manim/background_color.py`, `real_time_manim/render/text/glyphs.py`; human wiki `../zh_CN/07-图论与向量场/`.
> Render channel (RTM): **none of these has a dedicated RTM renderer** — all fall back to generic vector/bezier rasterization. Observed working: `Create` per-stroke draw, labels, arrow tips, layout animation, RK4 nudge, continuous updaters, submobject drift, stream-line creation/flow (per zh_CN `实测`).

## Graph / DiGraph

### `Graph`
```python
Graph(vertices: Sequence[Hashable], edges: Sequence[tuple[Hashable, Hashable]], labels: bool | dict = False, label_fill_color: str = BLACK, layout: LayoutName | dict[Hashable, Point3DLike] | LayoutFunction = "spring", layout_scale: float | tuple[float, float, float] = 2, layout_config: dict | None = None, vertex_type: type[Mobject] = Dot, vertex_config: dict | None = None, vertex_mobjects: dict | None = None, edge_type: type[Mobject] = Line, partitions: Sequence[Sequence[Hashable]] | None = None, root_vertex: Hashable | None = None, edge_config: dict | None = None)
```
- `ret`: `Graph` instance; subclass of `VMobject` (`Graph` → `GenericGraph` → `VMobject`) → directly `Create`/`add`-able. `repr`: `Undirected graph on {n} vertices and {m} edges`.
- `args`:

| param | type | default | meaning |
| --- | --- | --- | --- |
| `vertices` | `Sequence[Hashable]` | required | vertex names; any hashable (int/str). Duplicate name → `ValueError` at construction. |
| `edges` | `Sequence[tuple]` | required | each item `(u, v)`; order irrelevant for undirected. |
| `labels` | `bool \| dict` | `False` | `True` → `MathTex(v, color=label_fill_color)` per vertex (**needs LaTeX/Typst**). dict `{vertex: label_mobject}` must cover **every** vertex. |
| `label_fill_color` | `str` | `BLACK` | only used when `labels=True`. |
| `layout` | `str \| dict \| LayoutFunction` | `"spring"` | see layouts table. |
| `layout_scale` | `float \| tuple` | `2` | auto-layout coords land in `[-scale, scale]`; tuple `(sx, sy)` scales per axis. |
| `layout_config` | `dict \| None` | `None` | kwargs forwarded to the layout algorithm; **keys must be accepted by that algorithm**. |
| `vertex_type` | `type[Mobject]` | `Dot` | auto-switched to `LabeledDot` when labels are present. |
| `vertex_config` | `dict \| None` | `None` | dual-use: common kwargs, or `{vertex: kwargs}` per-vertex override; mixable (keys that are vertex names = override). |
| `vertex_mobjects` | `dict \| None` | `None` | `{vertex: mobject}`; highest priority. |
| `edge_type` | `type[Mobject]` | `Line` | **must be a `Line` subclass** or the edge updater breaks. |
| `partitions` | `Sequence[Sequence] \| None` | `None` | used by `layout="partite"`; unlisted vertices get their own right-most column. |
| `root_vertex` | `Hashable \| None` | `None` | used by `layout="tree"`. |
| `edge_config` | `dict \| None` | `None` | same dual-use as `vertex_config`, keys `(u, v)` (both directions accepted on undirected); also carries `tip_config`. |
- `notes`:
  - Every edge is registered via `add_updater(self.update_edges)` → edges follow vertices automatically when vertices are moved.
  - Per-vertex / per-edge override entries are **whole replacements, not merges**: writing `{color: RED}` for a vertex drops the common `radius` for it.
  - `labels=True` labels are `MathTex`; keep `label_fill_color=BLACK` on default white `Dot`s.
  - `labels=True` + default `vertex_type=Dot` → the class becomes `LabeledDot`; a missing label in a `labels` dict crashes `LabeledDot` (upstream behavior).
  - `CurvedArrow` is not a `Line` subclass → `TypeError`; `DoubleArrow` works (use it for "undirected graph with double arrows").
  - RTM deviation: rendering is the generic vector fallback, no graph-specific channel.
- `errs`:
  - `ValueError: "Vertex identifier '{vertex}' is already used for a vertex in this graph."` — duplicate vertex name in `vertices`.
  - `TypeError` — `edge_type` not a `Line` subclass; or `layout_config` key not accepted by the chosen layout (e.g. `seed` passed to `circular`/`kamada_kawai`).
- `see`: ../zh_CN/07-图论与向量场/01-Graph与DiGraph.md
- `eg`:
```python
g = Graph([1, 2, 3, 4, 5], [(1, 2), (2, 3), (3, 4), (4, 5), (1, 5), (1, 3)],
          layout="circular", layout_scale=2.4, labels=True, label_fill_color=BLACK,
          vertex_config={"radius": 0.16, "color": YELLOW, 3: {"color": RED}},
          edge_config={"stroke_width": 5, "color": BLUE, (1, 3): {"stroke_width": 10}})
```

### `DiGraph`
```python
DiGraph(vertices: Sequence[Hashable], edges: Sequence[tuple[Hashable, Hashable]], labels: bool | dict = False, label_fill_color: str = BLACK, layout: LayoutName | dict[Hashable, Point3DLike] | LayoutFunction = "spring", layout_scale: float | tuple[float, float, float] = 2, layout_config: dict | None = None, vertex_type: type[Mobject] = Dot, vertex_config: dict | None = None, vertex_mobjects: dict | None = None, edge_type: type[Mobject] = Line, partitions: Sequence[Sequence[Hashable]] | None = None, root_vertex: Hashable | None = None, edge_config: dict | None = None)
```
- `ret`: `DiGraph` instance. `repr`: `Directed graph on {n} vertices and {m} edges`.
- `args`: identical to `Graph` (same table above). Only extra: `edge_config["tip_config"]`.
- `notes`:
  - `(u, v)` means arrow `u` → `v`; vertex order is significant.
  - Edges are built with the vertex **mobjects** as ends and get `edge.add_tip(**tip_config)` at construction.
  - `DiGraph.update_edges` does `edge.pop_tips()` → `set_points_by_ends(...)` → `add_tip(tip)` **every frame**, so tips are not deformed when vertices/layout move. This is the extra per-frame cost vs `Graph`.
- `see`: ../zh_CN/07-图论与向量场/01-Graph与DiGraph.md
- `eg`:
```python
d = DiGraph([1, 2, 3, 4], [(1, 2), (2, 3), (1, 3), (3, 4), (4, 1)],
            layout="circular", layout_scale=2.2, labels=True, label_fill_color=BLACK,
            edge_config={"color": BLUE_E, "stroke_width": 5,
                         "tip_config": {"tip_length": 0.3, "tip_width": 0.26}})
```

#### `edge_config["tip_config"]`
| key | type | default | meaning |
| --- | --- | --- | --- |
| `tip_config` | `dict` | `{}` (default tip) | keys include `tip_shape` (tip class), `tip_length`, `tip_width`; settable at the common level and overridable per edge via `{(u, v): {"tip_config": {...}}}`. |

### `GenericGraph.from_networkx`
```python
GenericGraph.from_networkx(nxgraph: nx.Graph | nx.DiGraph, **kwargs)  # classmethod
```
- `ret`: instance of the calling class (`Graph.from_networkx` → `Graph`, `DiGraph.from_networkx` → `DiGraph`).
- `args`:
  - `nxgraph: nx.Graph | nx.DiGraph` — required; existing networkx graph.
  - `**kwargs` — forwarded verbatim to the constructor (`layout`, `labels`, `vertex_config`, …).
- `notes`: pure sugar — body is `cls(list(nxgraph.nodes), list(nxgraph.edges), **kwargs)`; every constructor pitfall applies (layout `seed`, `labels` dict coverage).
- `see`: ../zh_CN/07-图论与向量场/01-Graph与DiGraph.md
- `eg`:
```python
g = Graph.from_networkx(nx.wheel_graph(7), layout="spring",
                        layout_config={"seed": 5}, labels=True, label_fill_color=BLACK)
```

### layouts (`layout` values)
`LayoutName = Literal["circular", "kamada_kawai", "partite", "planar", "random", "shell", "spectral", "spiral", "spring", "tree"]`

| `layout` | form | typical `layout_config` | notes |
| --- | --- | --- | --- |
| `"spring"` (default) | Fruchterman-Reingold force-directed | `{"k": ..., "seed": ...}` (accepts `seed`) | **must pin `seed`** for reproducibility |
| `"circular"` | vertices on a circle | — (does **not** accept `seed`) | deterministic |
| `"partite"` | vertical columns per `partitions` | requires constructor `partitions` | neural-net layers |
| `"kamada_kawai"` | graph-distance preserving | `{"dist": {u: {v: d}}}` | deterministic, no `seed` |
| `"planar"` | planar layout, minimal edge crossings | — | raises on non-planar graphs |
| `"random"` | random scatter | `{"seed": 0}` (accepts `seed`) | pin `seed` |
| `"shell"` | concentric layers | `{"nlist": [[...], [...]]}` | |
| `"spectral"` | graph-Laplacian eigenvector projection | — | |
| `"spiral"` | spiral | — | |
| `"tree"` | layered tree | needs `root_vertex`; optional `{"vertex_spacing", "orientation": "down"}` | |
| `{vertex: [x, y, z]}` | hand-written coordinate dict | — | keys must **cover all vertices** |
| callable | custom `(nx_graph, scale=2, **kwargs) -> dict[node, np.ndarray(3)]` | `layout_config` forwarded | must be pure; must not mutate the passed graph |

- `errs`: `ValueError: "The layout '{layout}' is neither a recognized layout, a layout function,nor a vertex placement dictionary."` — unknown name and the callable branch raised `TypeError`.
- `see`: ../zh_CN/07-图论与向量场/01-Graph与DiGraph.md

### `GenericGraph.__getitem__`
```python
GenericGraph.__getitem__(k: Hashable | tuple[Hashable, Hashable]) -> Mobject
```
- `ret`: the vertex `Mobject` (`g[vertex]`) or edge `Mobject` (`g[(u, v)]`). Same object, **not a copy**.
- `args`:
  - `k: Hashable` — vertex name → vertex mobject.
  - `k: tuple[Hashable, Hashable]` — `(u, v)` → edge mobject.
- `notes`: the standard way to animate one vertex/edge: `g[2].animate.shift(...)`, `g[(1, 2)].animate.set_stroke(...)`. Mutations hit the graph itself; restore manually.
- `errs`:
  - `ValueError: "Could not find {k} in vertices or edges"` — unknown key (the docstring claims `KeyError`, the code raises `ValueError`).
- `see`: ../zh_CN/07-图论与向量场/01b-图的增删与布局.md

### `GenericGraph.add_vertices`
```python
GenericGraph.add_vertices(*vertices: Hashable, positions: dict | None = None, labels: bool = False, label_fill_color: str = BLACK, vertex_type: type[Mobject] = Dot, vertex_config: dict | None = None, vertex_mobjects: dict | None = None)
```
- `ret`: list of the newly created vertex mobjects (`_add_created_vertex` per vertex). Under `.animate` → `AnimationGroup` of `Create` (default `animation`, overridable via `anim_args["animation"]`).
- `args`:

| param | type | default | meaning |
| --- | --- | --- | --- |
| `*vertices` | `Hashable` | required | new vertex names |
| `positions` | `dict \| None` | `None` | `{vertex: [x, y, z]}`; `None` → placed at graph center (**give `positions` in practice**) |
| `labels` | `bool \| dict` | `False` | `bool` applies to all passed vertices; a `dict` is merged over `dict.fromkeys(vertices, False)` |
| `label_fill_color` | `str` | `BLACK` | label color |
| `vertex_type` | `type[Mobject]` | `Dot` | vertex class |
| `vertex_config` | `dict \| None` | `None` | merged over the graph's `default_vertex_config` |
| `vertex_mobjects` | `dict \| None` | `None` | direct mobjects |
- `notes`: the source signature annotates `labels: bool` but a `dict` is accepted (`assert isinstance(labels, dict)` branch).
- `see`: ../zh_CN/07-图论与向量场/01b-图的增删与布局.md
- `eg`:
```python
win.play(g.animate.add_vertices(5, positions={5: [3.2, -1.4, 0]}, labels=True), run_time=0.6)
```

### `GenericGraph.add_edges`
```python
GenericGraph.add_edges(*edges: tuple[Hashable, Hashable], edge_type: type[Mobject] = Line, edge_config: dict | None = None, **kwargs)
```
- `ret`: list of new edge mobjects. Under `.animate` → `AnimationGroup` of `Create` (default `animation`).
- `args`:
  - `*edges: tuple[Hashable, Hashable]` — edges to add; endpoints that do not exist yet are auto-created as vertices.
  - `edge_type: type[Mobject] = Line` — edge class.
  - `edge_config: dict | None = None` — common kwargs, or `{(u, v): kwargs}`.
  - `**kwargs` — **all forwarded to `add_vertices`** (`positions`, `labels`, `label_fill_color`, `vertex_config`, …).
- `notes`: new vertices created here get default settings; create them yourself first to customize.
- `see`: ../zh_CN/07-图论与向量场/01b-图的增删与布局.md
- `eg`:
```python
win.play(g.animate.add_edges((1, 4), positions={4: [3.2, 1.2, 0]}, labels=True), run_time=0.8)
```

### `GenericGraph.remove_vertices`
```python
GenericGraph.remove_vertices(*vertices: Hashable)
```
- `ret`: `VGroup` of all removed mobjects (the vertices **and** their incident edges).
- `args`: `*vertices: Hashable` — vertices to remove; all incident edges are removed too.
- `notes`: `.animate` version is `AnimationGroup` of `Uncreate` (default `animation`, `anim_args["animation"]` overridable). Layout is **not** recomputed after removal — remaining vertices stay in place; call `change_layout` to re-space.
- `see`: ../zh_CN/07-图论与向量场/01b-图的增删与布局.md

### `GenericGraph.remove_edges`
```python
GenericGraph.remove_edges(*edges: tuple[Hashable]) -> VGroup
```
- `ret`: `VGroup` of the removed edge mobjects.
- `args`: `*edges: tuple[Hashable, Hashable]` — edges to remove; their vertices are kept.
- `notes`: `.animate` version is `AnimationGroup` of `Uncreate`.
- `see`: ../zh_CN/07-图论与向量场/01b-图的增删与布局.md
- `eg`:
```python
win.play(g.animate.remove_edges((1, 3)), run_time=0.5)   # edge only
win.play(g.animate.remove_vertices(4), run_time=0.5)     # vertex + its edges
```

### `GenericGraph.change_layout`
```python
GenericGraph.change_layout(layout: LayoutName | dict[Hashable, Point3DLike] | LayoutFunction = "spring", layout_scale: float | tuple[float, float, float] = 2, layout_config: dict[str, Any] | None = None, partitions: list[list[Hashable]] | None = None, root_vertex: Hashable | None = None) -> Graph
```
- `ret`: `self` (chainable).
- `args`:

| param | type | default | meaning |
| --- | --- | --- | --- |
| `layout` | same as constructor | `"spring"` | new layout (name / coord dict / callable) |
| `layout_scale` | `float \| tuple` | `2` | new scale |
| `layout_config` | `dict \| None` | `None` | layout algorithm kwargs |
| `partitions` | `list[list] \| None` | `None` | written into `layout_config["partitions"]` if not already present |
| `root_vertex` | `Hashable \| None` | `None` | written into `layout_config["root_vertex"]` if not already present |
- `notes`: `move_to`s every vertex to the new positions; edges follow via their updater. Called internally by `__init__` too. Same layout rules/pitfalls as the constructor.
- `see`: ../zh_CN/07-图论与向量场/01b-图的增删与布局.md
- `eg`:
```python
win.play(g.animate.change_layout("spring", layout_config={"seed": 7}), run_time=1.0)
win.play(g.animate.change_layout({1: [-3.2, 0, 0], 2: [-1.6, 0, 0], 3: [0, 0, 0],
                                  4: [1.6, 0, 0], 5: [3.2, 0, 0]}), run_time=1.0)
```

### `Graph.update_edges` / `DiGraph.update_edges`
```python
Graph.update_edges(self, graph) -> Self
DiGraph.update_edges(self, graph) -> Self
```
- `notes`: the updater body, auto-attached by `add_updater` in `__init__` — **do not call manually**. `Graph` version: `edge.set_points_by_ends(...)` with `buff=self._edge_config.get("buff", 0)` and `path_arc=self._edge_config.get("path_arc", 0)`.
- `see`: ../zh_CN/07-图论与向量场/01b-图的增删与布局.md

### `GenericGraph` attributes / RTM specifics
| item | meaning |
| --- | --- |
| `.vertices` | `dict[Hashable, Mobject]` |
| `.edges` | `dict[(u, v), Mobject]` |
| `._layout` | current layout coordinates |
| `g[v].move_to(...)` | manual reposition; edges follow, but `_layout` does **not** stay in sync (only `change_layout` recomputes it) |
| `LayoutFunction` (Protocol) | custom layout must be a pure `(graph, scale=2, **kwargs) -> dict[node, np.ndarray(3)]`; must not mutate the passed graph |
| `.animate` graph methods + RTM | measured 2026-10-17: `.animate` versions of `add_vertices`/`add_edges`/`remove_vertices`/`remove_edges`/`change_layout` are built by `override_animate` into `AnimationGroup`/`Uncreate`/`_MethodAnimation` and played **directly by `win.play`** — they do **not** call back into `self.play`. The `self.play = win.play` line in zh_CN samples is belt-and-braces wiring; only `Scene`-level methods such as `move_camera` truly need it. |

## Vector fields

### `DEFAULT_SCALAR_FIELD_COLORS`
```python
DEFAULT_SCALAR_FIELD_COLORS: list = [BLUE_E, GREEN, YELLOW, RED]
```
- `notes`: module-level constant in `manim/mobject/vector_field.py`. **Not** in that module's `__all__` (`__all__ = ["VectorField", "ArrowVectorField", "StreamLines"]`) → **not** exported at `real_time_manim` top level. Import via `from manim.mobject.vector_field import DEFAULT_SCALAR_FIELD_COLORS` (the bundled copy answers to `manim` once `real_time_manim` is imported). It is the default "gradient by magnitude" palette.
- `see`: ../zh_CN/07-图论与向量场/02-向量场与流线.md

### `VectorField`
```python
VectorField(func: Callable[[Point3D], Vector3D], color: ParsableManimColor | None = None, color_scheme: Callable[[Vector3D], float] | None = None, min_color_scheme_value: float = 0, max_color_scheme_value: float = 2, colors: Sequence[ParsableManimColor] = DEFAULT_SCALAR_FIELD_COLORS, **kwargs)
```
- `ret`: `VectorField` instance (`VGroup` subclass). Produces **no visible elements** itself.
- `args`:

| param | type | default | meaning |
| --- | --- | --- | --- |
| `func` | `Callable[[Point3D], Vector3D]` | required | position → vector |
| `color` | `ParsableManimColor \| None` | `None` | if set, single color and position-based coloring is disabled (`self.single_color = True`) |
| `color_scheme` | `Callable[[Vector3D], float] \| None` | `None` | vector → scalar; default is `np.linalg.norm` (magnitude) |
| `min_color_scheme_value` | `float` | `0` | scalar mapped to first color of `colors` |
| `max_color_scheme_value` | `float` | `2` | scalar mapped to last color of `colors` |
| `colors` | `Sequence[ParsableManimColor]` | `[BLUE_E, GREEN, YELLOW, RED]` | gradient |
| `**kwargs` | — | — | forwarded to `VGroup` |
- `notes`:
  - `color` and `colors`/`color_scheme` are mutually exclusive in effect: setting `color` flattens the field; leave `None` for gradient-by-position.
  - With `color=None`, `self.pos_to_rgb` / `self.pos_to_color` are installed; `color_scheme` values are clipped into `[min_color_scheme_value, max_color_scheme_value]` before the gradient lookup.
  - RTM deviation: per-position/per-pixel coloring is not reproducible in the vector path — see the RTM note under `StreamLines`.
- `see`: ../zh_CN/07-图论与向量场/02-向量场与流线.md

### `VectorField.nudge`
```python
VectorField.nudge(self, mob: Mobject, dt: float = 1, substeps: int = 1, pointwise: bool = False) -> Self
```
- `ret`: the vector field (`self`).
- `args`:
  - `mob: Mobject` — mobject to move.
  - `dt: float = 1` — scalar amount moved along the field; actual distance depends on field magnitude.
  - `substeps: int = 1` — RK4 step subdivision; higher = more accurate. `substeps=1` degenerates to a single RK4 sample.
  - `pointwise: bool = False` — `False`: field acts on `mob.get_center()` (rigid `shift`); `True`: applied per point via `apply_function` → **distorts** the mobject.
- `notes`: implementation is RK4 with `step_size = dt / substeps`, looped `substeps` times. **Produces no animation** — the mobject jumps instantly; add your own `Line` to visualize the step, or use `get_nudge_updater`.
- `see`: ../zh_CN/07-图论与向量场/02-向量场与流线.md
- `eg`:
```python
vf.nudge(dot, dt=1, substeps=20)          # one big RK4 step, instant
step = Line(start, dot.get_center(), stroke_width=4, color=ORANGE)
```

### `VectorField.get_nudge_updater`
```python
VectorField.get_nudge_updater(self, speed: float = 1, pointwise: bool = False) -> Callable[[Mobject, float], Mobject]
```
- `ret`: an updater `lambda mob, dt: self.nudge(mob, dt * speed, pointwise=pointwise)` — hand it to `mob.add_updater(...)`.
- `args`:
  - `speed: float = 1` — at `speed=1` the per-second distance equals the field magnitude along the path.
  - `pointwise: bool = False` — see `nudge`.
- `notes`: while attached, the mobject keeps moving for **as long as the frame keeps rendering** — remember `mob.clear_updaters()` to stop it.
- `see`: ../zh_CN/07-图论与向量场/02-向量场与流线.md
- `eg`:
```python
dot.add_updater(vf.get_nudge_updater(speed=1))
win.play(Wait(2.0))
dot.clear_updaters()
```

### `VectorField.nudge_submobjects`
```python
VectorField.nudge_submobjects(self, dt: float = 1, substeps: int = 1, pointwise: bool = False) -> Self
```
- `ret`: `self`.
- `args`: same meaning as `nudge`; applied to **every** submobject of the field.
- `notes`: loops `for mob in self.submobjects: self.nudge(mob, dt, substeps, pointwise)`. One-shot (no animation), like `nudge`.
- `see`: ../zh_CN/07-图论与向量场/02-向量场与流线.md

### `VectorField.start_submobject_movement`
```python
VectorField.start_submobject_movement(self, speed: float = 1, pointwise: bool = False) -> Self
```
- `ret`: `self`.
- `args`:
  - `speed: float = 1` — see `get_nudge_updater`.
  - `pointwise: bool = False` — see `nudge`.
- `notes`:
  - Moves the field's **own** submobjects (each `Vector` / stream line), not arbitrary mobjects — use `nudge` / `get_nudge_updater` for those.
  - Calling it again **replaces** the previous updater (it calls `stop_submobject_movement()` first). Stop only via `stop_submobject_movement()`; `clear_updaters()` has no effect on it.
- `see`: ../zh_CN/07-图论与向量场/02-向量场与流线.md
- `eg`:
```python
vf.start_submobject_movement(speed=1.5)
win.play(Wait(2.0))
vf.stop_submobject_movement()
```

### `VectorField.stop_submobject_movement`
```python
VectorField.stop_submobject_movement(self) -> Self
```
- `ret`: `self`.
- `notes`: `remove_updater(self.submob_movement_updater)` then resets it to `None`; the submobjects stay where they are.
- `see`: ../zh_CN/07-图论与向量场/02-向量场与流线.md

### `VectorField.shift_func` / `VectorField.scale_func`
```python
VectorField.shift_func(func: Callable[[np.ndarray], np.ndarray], shift_vector: np.ndarray) -> Callable[[np.ndarray], np.ndarray]   # staticmethod
VectorField.scale_func(func: Callable[[np.ndarray], np.ndarray], scalar: float) -> Callable[[np.ndarray], np.ndarray]           # staticmethod
```
- `ret`: `lambda p: func(p - shift_vector)` / `lambda p: func(p * scalar)`.
- `notes`: static helpers that translate / scale the **domain** of a field function. Usable to build a `become`-style comparison: `vector_field.animate.become(ArrowVectorField(VectorField.scale_func(func, 0.5)))`.
- `see`: ../zh_CN/07-图论与向量场/02-向量场与流线.md

### `VectorField.fit_to_coordinate_system`
```python
VectorField.fit_to_coordinate_system(self, coordinate_system: CoordinateSystem) -> Self
```
- `ret`: `self` (zh_CN table lists `-> None`; source returns `self`).
- `args`: `coordinate_system: CoordinateSystem` — target coordinate system.
- `notes`: body is `self.apply_function(lambda pos: coordinate_system.coords_to_point(*pos))` — **in-place transform, callable only once** (it moves each vector's origin).
- `see`: ../zh_CN/07-图论与向量场/02-向量场与流线.md

### `VectorField.get_colored_background_image`
```python
VectorField.get_colored_background_image(self, sampling_rate: int = 5) -> Image.Image
```
- `ret`: PIL `Image` colored by `pos_to_rgb` over the frame; used internally by `StreamLines` for coloring.
- `args`: `sampling_rate: int = 5` — pixel step; lower = more accurate, slower.
- `errs`:
  - `ValueError: "There is no point in generating an image if the vector field uses a single color."` — `self.single_color` is `True` (i.e. `color=` was passed).
- `notes`: RTM cannot tint per stroke pixel from this image; it substitutes the image's mean color (see `StreamLines` RTM note).
- `see`: ../zh_CN/07-图论与向量场/02-向量场与流线.md

### `VectorField.get_vectorized_rgba_gradient_function`
```python
VectorField.get_vectorized_rgba_gradient_function(self, start: float, end: float, colors: Iterable[ParsableManimColor]) -> Callable[[Sequence[float], float], FloatRGBA_Array]
```
- `ret`: `func(values, opacity=1.0) -> FloatRGBA_Array` — vectorized "scalar array → RGBA array" gradient.
- `args`:
  - `start: float` — start value for `inverse_interpolate`.
  - `end: float` — end value for `inverse_interpolate`.
  - `colors: Iterable[ParsableManimColor]` — gradient colors.
- `notes`: OpenGL-renderer path (`StreamLines` uses it only when `config["renderer"] == RendererType.OPENGL`). Under the default Cairo path RTM uses `pos_to_color` / background images instead.
- `see`: ../zh_CN/07-图论与向量场/02-向量场与流线.md

### `ArrowVectorField`
```python
ArrowVectorField(func: Callable[[np.ndarray], np.ndarray], color: ParsableManimColor | None = None, color_scheme: Callable[[np.ndarray], float] | None = None, min_color_scheme_value: float = 0, max_color_scheme_value: float = 2, colors: Sequence[ParsableManimColor] = DEFAULT_SCALAR_FIELD_COLORS, x_range: Sequence[float] = None, y_range: Sequence[float] = None, z_range: Sequence[float] = None, three_dimensions: bool = False, length_func: Callable[[float], float] = lambda norm: 0.45 * sigmoid(norm), opacity: float = 1.0, vector_config: dict | None = None, **kwargs)
```
- `ret`: `ArrowVectorField` instance (a `VectorField`, i.e. `VGroup`) — `Create`/`FadeIn`/`add`-able.
- `args`:

| param | type | default | meaning |
| --- | --- | --- | --- |
| `func` | `Callable[[ndarray], ndarray]` | required | position → vector |
| `color` | `ParsableManimColor \| None` | `None` | set → whole field single-colored, position coloring off |
| `color_scheme` | `Callable[[ndarray], float] \| None` | `None` | vector → scalar; default `np.linalg.norm` |
| `min_color_scheme_value` / `max_color_scheme_value` | `float` | `0` / `2` | scalar range mapped to gradient ends |
| `colors` | `Sequence[ParsableManimColor]` | `[BLUE_E, GREEN, YELLOW, RED]` | gradient |
| `x_range` / `y_range` / `z_range` | `Sequence[float] \| None` | `None` | `[min, max, step]` sampling grid; default `x/y` = frame span (`floor(-frame_width/2) .. ceil(frame_width/2)`), `step` defaults to `0.5` when a range has only 2 entries |
| `three_dimensions` | `bool` | `False` | 3D sampling; **automatically `True` if `z_range` is given** |
| `length_func` | `Callable[[float], float]` | `lambda norm: 0.45 * sigmoid(norm)` | displayed length from the **actual norm** (default saturating cap to reduce clutter) |
| `opacity` | `float` | `1.0` | arrow opacity (applied via `set_opacity`) |
| `vector_config` | `dict \| None` | `None` | kwargs to the `Vector` constructor (`stroke_width`, `tip_shape`, …) |
| `**kwargs` | — | — | forwarded to `VGroup` |
- `notes`:
  - Grid is `np.arange(*range)` over `x_range × y_range × z_range`; each cell builds one `Vector` via `get_vector`.
  - `length_func` receives the **normalized/actual magnitude**; its return value is used directly as the arrow length (constant function → equal-length arrows).
  - `vector_config` does **not** set the color: color is applied afterwards (`set_color(self.color)` or `set_color(self.pos_to_color(point))`).
  - `func` returning a zero vector → length is left at 0 (no division by zero).
- `see`: ../zh_CN/07-图论与向量场/02-向量场与流线.md
- `eg`:
```python
func = lambda pos: np.sin(pos[1] / 2) * RIGHT + np.cos(pos[0] / 2) * UP
vf = ArrowVectorField(func, x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],
                      color=RED, length_func=lambda x: x / 3,
                      vector_config={"stroke_width": 2})
```

### `ArrowVectorField.get_vector`
```python
ArrowVectorField.get_vector(self, point: np.ndarray)
```
- `ret`: a single `Vector` rooted at `point`, colored and length-scaled per this field's config.
- `args`: `point: np.ndarray` — root point.
- `notes`: normally called automatically during construction; rarely invoked directly.
- `see`: ../zh_CN/07-图论与向量场/02-向量场与流线.md

## StreamLines

### `StreamLines`
```python
StreamLines(func: Callable[[np.ndarray], np.ndarray], color: ParsableManimColor | None = None, color_scheme: Callable[[np.ndarray], float] | None = None, min_color_scheme_value: float = 0, max_color_scheme_value: float = 2, colors: Sequence[ParsableManimColor] = DEFAULT_SCALAR_FIELD_COLORS, x_range: Sequence[float] = None, y_range: Sequence[float] = None, z_range: Sequence[float] = None, three_dimensions: bool = False, noise_factor: float | None = None, n_repeats = 1, dt = 0.05, virtual_time = 3, max_anchors_per_line = 100, padding = 3, stroke_width = 1, opacity = 1, **kwargs)
```
- `ret`: `StreamLines` instance (`VectorField` subclass). All lines are also stored in the `.stream_lines` attribute.
- `args`:

| param | type | default | meaning |
| --- | --- | --- | --- |
| `func` | `Callable` | required | field function |
| `color` / `color_scheme` / `min_color_scheme_value` / `max_color_scheme_value` / `colors` | as `ArrowVectorField` | same | coloring |
| `x_range` / `y_range` / `z_range` | `Sequence[float] \| None` | `None` | **spawn area** `[min, max, step]` (not a display grid) |
| `three_dimensions` | `bool` | `False` | 3D stream lines; auto-`True` if `z_range` given |
| `noise_factor` | `float \| None` | `None` → `y_range[2] / 2` | random jitter per spawn point along each axis |
| `n_repeats` | `int` | `1` | agents spawned per spawn point |
| `dt` | `float` | `0.05` | integration step; smaller = more accurate trajectories |
| `virtual_time` | `float` | `3` | simulated duration per line; higher = longer lines **and slower construction** (the whole trace is integrated at construction) |
| `max_anchors_per_line` | `int` | `100` | max anchors per line; excess is decimated (lower complexity, **not** shorter) |
| `padding` | `float` | `3` | how far an agent may leave the spawn box before termination |
| `stroke_width` | `float` | `1` | line width |
| `opacity` | `float` | `1` | line opacity |
| `**kwargs` | — | — | forwarded to `VectorField`/`VGroup` |
- `notes`:
  - Simulation is Euler (`new_point = last_point + dt * func(last_point)`), not RK4; `max_steps = ceil(virtual_time / dt) + 1`.
  - Spawn points use `np.random.default_rng(0)` → the jitter is reproducible across runs.
  - Each line stores `line.duration = step * dt` and is decimated by `set_points_smoothly(points[::step])` with `step = max(1, int(len(points) / max_anchors_per_line))`.
  - **`virtual_time` dominates construction cost** — for dense/large fields reduce it or reduce `max_anchors_per_line` first.
  - **RTM deviation (coloring)**: with `color=None`, CE leaves each line's stroke rgba **WHITE** and lets the Cairo renderer tint per pixel from `background_img` (`VMobject.color_using_background_image`). RTM cannot tint per pixel, so it takes the **mean color of the background image** and uses it as the line's stroke color (`real_time_manim/background_color.py::background_image_rgb`, applied in `render/text/glyphs.py::GlyphMixin._stroke_rgb_with_background`). Effect: per-position gradient on stream lines is flattened to one averaged color; a field rendered red in CE came out white before this fix. Pass `color=` explicitly for deterministic output.
  - **RTM deviation (render channel)**: generic vector fallback, no stream-line-specific channel.
- `errs`:
  - (none raised at construction; `get_colored_background_image` raises only if `single_color`)
- `see`: ../zh_CN/07-图论与向量场/02b-流线StreamLines.md
- `eg`:
```python
sl = StreamLines(func, x_range=[-4, 4, 1], y_range=[-2.5, 2.5, 1],
                 color=BLUE, stroke_width=3, max_anchors_per_line=15, virtual_time=1)
```

### `StreamLines.create`
```python
StreamLines.create(self, lag_ratio: float | None = None, run_time: Callable[[float], float] | None = None, **kwargs) -> AnimationGroup
```
- `ret`: `AnimationGroup` of one `Create(line, run_time=run_time, **kwargs)` per stream line, `animations` **shuffled with `random.shuffle`** (random order).
- `args`:
  - `lag_ratio: float | None = None` — if `None`: `run_time / 2 / len(self.submobjects)`.
  - `run_time: Callable[[float], float] | None = None` — run time of **each single line** creation; if `None`: **`self.virtual_time`** is used.
  - `**kwargs` — forwarded to each `Create`.
- `notes`: because `run_time` defaults to `virtual_time` (default `3`), forgetting to pass it makes the draw look like a 3-second wait. Whole animation is longer than `run_time` due to `lag_ratio`.
- `see`: ../zh_CN/07-图论与向量场/02b-流线StreamLines.md
- `eg`:
```python
win.play(sl.create(run_time=1.4), run_time=1.4)
```

### `StreamLines.start_animation`
```python
StreamLines.start_animation(self, warm_up: bool = True, flow_speed: float = 1, time_width: float = 0.3, rate_func: Callable[[float], float] = linear, line_animation_class: type[ShowPassingFlash] = ShowPassingFlash, **kwargs) -> Self
```
- `ret`: `self` (source returns `self`; zh_CN describes it as "attaches an updater, no return value"). It is **not** playable on its own — call it before a `Wait`.
- `args`:

| param | type | default | meaning |
| --- | --- | --- | --- |
| `warm_up` | `bool` | `True` | `True` initializes line by line (staggered light-up); `False` starts with all lines already shown |
| `flow_speed` | `float` | `1` | at `1` the flow advances per second by the field magnitude along the path; scales the flow speed |
| `time_width` | `float` | `0.3` | proportion of each line that is lit/visible at once |
| `rate_func` | `Callable[[float], float]` | `linear` | rate function of each line flash |
| `line_animation_class` | `type[ShowPassingFlash]` | `ShowPassingFlash` | animation class used per line |
| `**kwargs` | — | — | forwarded to `line_animation_class` |
- `notes`:
  - Per line: `run_time = line.duration / flow_speed`, `line.anim.begin()`, then `line.time = random.random() * self.virtual_time` (`warm_up=True` negates it). **Phase** of each light point is therefore random per line at start and advances by `dt * flow_speed` modulo `virtual_time` in the updater; during `Wait` the frame content keeps changing, so CE/RTM light-point phase may differ slightly (expected, not a bug).
  - Wraps at `virtual_time`: `if line.time >= self.virtual_time: line.time -= self.virtual_time`.
  - Sets `self.flow_animation`, `self.flow_speed`, `self.time_width`.
  - **RTM/critical pitfall**: the updater lives on `sl` itself. `create()` only puts the **individual lines** into the scene, so `sl` is not in the scene unless you `self.add(sl)` — without it the updater never runs and the whole field renders black, **with no error**. zh_CN measured the same on both engines.
- `errs`:
  - (none) — but the missing `self.add(sl)` failure is silent.
- `see`: ../zh_CN/07-图论与向量场/02b-流线StreamLines.md
- `eg`:
```python
win.play(sl.create(run_time=0.8), run_time=0.8)
self.add(sl)                                          # REQUIRED, else blank
sl.start_animation(warm_up=False, flow_speed=1.5, time_width=0.5)
win.play(Wait(2.0))
```

### `StreamLines.end_animation`
```python
StreamLines.end_animation(self) -> AnimationGroup
```
- `ret`: `AnimationGroup` — a playable animation that eases the running flow into fully displayed lines with no visible cut.
- `args`: none.
- `notes`: removes the flow updater (`self.flow_animation = None`), then per line either a `Create` with `ease_out_sine` or a `Succession(UpdateFromAlphaFunc(...), Create(...))` when `line.time <= 0`; `max_run_time = self.virtual_time / self.flow_speed`, `dt = 1 / config["frame_rate"]`. Only `start_animation` may be left un-ended (renders fine, just stays flowing), but the pair is meant to be used together.
- `errs`:
  - `ValueError: "You have to start the animation before fading it out."` — `end_animation()` called without a prior `start_animation()`.
- `see`: ../zh_CN/07-图论与向量场/02b-流线StreamLines.md
- `eg`:
```python
win.play(sl.end_animation(), run_time=0.6)
```

## see also
- ../zh_CN/07-图论与向量场/01-Graph与DiGraph.md · 01b-图的增删与布局.md · 02-向量场与流线.md · 02b-流线StreamLines.md
- agent: `mobject.md` (`.animate`, updaters), `geometry.md` (`Line`/`Vector`/tips), `gotchas.md`
