# Graph theory: Graph and DiGraph

`Graph` (undirected) and `DiGraph` (directed) are both "vertex + edge" graph objects: internally networkx stores the topology, and every edge carries its own updater so it follows its vertices — which means you can keep moving vertices after drawing. RTM has no dedicated graph renderer; it goes through the generic vector fallback. In testing, `Create` per-stroke drawing, labels, arrow tips and layout animation all work (see the samples below).

## Graph — undirected

### class Graph (RTM generic vector fallback rendering)

```python
Graph(vertices: Sequence[Hashable], edges: Sequence[tuple[Hashable, Hashable]], labels: bool | dict = False, label_fill_color: str = BLACK, layout: LayoutName | dict[Hashable, Point3DLike] | LayoutFunction = "spring", layout_scale: float | tuple[float, float, float] = 2, layout_config: dict | None = None, vertex_type: type[Mobject] = Dot, vertex_config: dict | None = None, vertex_mobjects: dict | None = None, edge_type: type[Mobject] = Line, partitions: Sequence[Sequence[Hashable]] | None = None, root_vertex: Hashable | None = None, edge_config: dict | None = None)
```

Vertices are any hashable object and edges are `(u, v)` tuples (order does not matter in an undirected graph); every edge carries an updater, so edges follow automatically when vertices move.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `vertices` | `Sequence[Hashable]` | required | vertex name list; **can hold** any hashable value (numbers, strings both fine); a duplicate vertex name raises `ValueError` |
| `edges` | `Sequence[tuple]` | required | edge list, each item `(u, v)`; order irrelevant |
| `labels` | `bool \| dict` | `False` | `True` labels with `MathTex(vertex name)` (**needs LaTeX/Typst**); you can also pass `{vertex: label_mobject}`, which **must cover every vertex** — miss one and `LabeledDot` crashes on the missing label (upstream behavior) |
| `label_fill_color` | `str` | `BLACK` | label color, only when `labels=True`; with the default white `Dot` vertices, `BLACK` stays the clearest |
| `layout` | `str \| dict \| LayoutFunction` | `"spring"` | layout name / hand-written coordinate dict / custom layout function; see the cheat sheet below |
| `layout_scale` | `float \| tuple` | `2` | auto-layout coordinates land in `[-scale, scale]`; the tuple form `(sx, sy)` scales per axis |
| `layout_config` | `dict \| None` | `None` | keyword arguments forwarded to the layout algorithm; **the keys must be accepted by that layout function** (`{"seed": ...}` is only eaten by random layouts like `spring`/`random`; passing it to `circular`/`kamada_kawai` raises `TypeError`) |
| `vertex_type` | `type[Mobject]` | `Dot` | vertex mobject class; auto-switched to `LabeledDot` when labels are present |
| `vertex_config` | `dict \| None` | `None` | dual-use: a **common parameter** dict (e.g. `{"radius": 0.16, "color": YELLOW}`), or `{vertex: kwargs}` per-vertex override; the two can be mixed (keys that are vertex names act as per-vertex overrides) |
| `vertex_mobjects` | `dict \| None` | `None` | directly specify which existing mobject each vertex uses (highest priority) |
| `edge_type` | `type[Mobject]` | `Line` | edge class; **must be a `Line` subclass** (otherwise the updater breaks); `DoubleArrow` works in testing, `CurvedArrow` is not a `Line` subclass and raises `TypeError` |
| `partitions` | `Sequence[Sequence] \| None` | `None` | column vertices for `layout="partite"`; vertices not listed in any column get their own right-most column |
| `root_vertex` | `Hashable \| None` | `None` | root vertex for `layout="tree"` |
| `edge_config` | `dict \| None` | `None` | same dual-use as `vertex_config`: common edge parameters / `{(u,v): kwargs}` per-edge override (both directions of the key are accepted on an undirected graph) |

**Returns**: a `Graph` instance (a `VMobject`, directly `Create`/`add`-able).

#### Sample: customizing vertex_config / edge_config per item

`vertex_config` / `edge_config` are both dual-use dicts of "common parameters + per-item overrides": common keys apply to every vertex/edge, while entries keyed by a vertex name or an `(u, v)` edge tuple override just that one.

```python
from real_time_manim import Scene, Graph, Text, VGroup, \
    BLACK, YELLOW, GREY_B, RED, BLUE, ORANGE, UP, DOWN, \
    Write, FadeIn, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class GraphConfigDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Graph-config", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = VGroup(
            Text("vertex_config={radius:0.16, color:YELLOW, 3:{color:RED}}",
                 font_size=26, color=GREY_B),
            Text("edge_config={stroke_width:5, color:BLUE, (1,3):{...:10}}",
                 font_size=26, color=GREY_B),
        ).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.3)   # two-line parameter summary
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        g = Graph(
            [1, 2, 3, 4, 5],                                   # five vertices
            [(1, 2), (2, 3), (3, 4), (4, 5), (1, 5), (1, 3)],  # six edges
            layout="circular", layout_scale=2.4,               # circular layout, scaled up a bit
            labels=True,                                       # parameter "labels"
            label_fill_color=BLACK,                            # parameter "label_fill_color"
            vertex_config={"radius": 0.16, "color": YELLOW,    # common vertex style
                           3: {"color": RED, "radius": 0.26}}, # vertex 3 overridden individually
            edge_config={"stroke_width": 5, "color": BLUE,     # common edge style
                         (1, 3): {"stroke_width": 10,          # this edge overridden individually
                                  "color": ORANGE}},
        )
        win.play(Create(g), run_time=1.0)   # draw the whole graph stroke by stroke
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: it builds a five-vertex, six-edge ring graph — every vertex is a yellow dot of radius 0.16 (vertex 3 is overridden into a larger red dot), every edge is a blue line of width 5 (the `(1, 3)` edge is overridden into an orange line of width 10), and `labels=True` stamps a black numeric label on each vertex. `Create` draws the whole graph stroke by stroke.

<video src="assets/RTM output/01-Graph-and-DiGraph-config.mp4" controls width="560"></video>

> Note:
>
> - The "per-item override" entries of `vertex_config`/`edge_config` are **whole replacements, not merges** — writing `{color: RED}` for a vertex means the common `radius` no longer applies to it.
> - `labels=True` labels go through `MathTex`; black text on white dots is what stays legible, so do not set `label_fill_color` to the same color as the vertices.

### layout — layouts (cheat sheet of the 12 values)

`layout` decides how the vertices are placed; most values are networkx's same-named layout algorithm, and `layout_config` forwards that algorithm's keyword arguments.

| layout value | form | typical `layout_config` | tested |
| --- | --- | --- | --- |
| `"spring"` (default) | Fruchterman-Reingold force-directed, balanced spread | `{"k":..., "seed":...}` (accepts `seed`) | tested in a sample |
| `"circular"` | vertices placed evenly on a circle | - (does not accept `seed`) | tested in a sample |
| `"partite"` | split into vertical columns per `partitions` (common for neural-net layers) | requires the constructor's `partitions` | tested in a sample |
| `"kamada_kawai"` | preserves the given graph distances as much as possible | `{"dist": {u:{v:d}}}` | construction tested OK, no separate clip |
| `"planar"` | planar layout, minimal edge crossings (raises on non-planar graphs) | - | same as above |
| `"random"` | random scatter | `{"seed": 0}` (accepts `seed`) | same as above |
| `"shell"` | concentric layers | `{"nlist": [[...], [...]]}` | same as above |
| `"spectral"` | graph-Laplacian eigenvector projection | - | same as above |
| `"spiral"` | spiral | - | same as above |
| `"tree"` | layered tree | needs `root_vertex`, optional `{"vertex_spacing", "orientation": "down"}` | same as above |
| `{vertex: [x,y,z]}` | hand-written coordinate dict | - | same as above |
| `callable` | custom layout function, signature `(nx_graph, scale=2, **kwargs) -> dict` | pass custom parameters via `layout_config` | same as above |

#### Sample: comparing three layouts

The same graph with only `layout` changed: `"circular"` a ring, `"spring"` force-directed (with `layout_config={"seed": 7}` pinning the random result so both engines match frame by frame), `"partite"` split into two columns per `partitions`.

```python
from real_time_manim import Scene, Graph, Text, \
    BLACK, YELLOW, GREY_B, UP, DOWN, \
    Write, FadeIn, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class GraphLayoutDemo(Scene):
    LAYOUT = "circular"   # layout name: switch to "spring" for the force-directed spread, "partite" is shown in the variant below
    PARTITIONS = None     # columns for the "partite" layout; leave None for other layouts
    CONFIG = {}           # "layout_config": layout algorithm kwargs (e.g. spring's random seed)

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Graph-layout", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text('layout="%s"' % self.LAYOUT, font_size=30, color=GREY_B)   # current layout name
        lab.next_to(title, DOWN, buff=0.35)   # place the label right below the title
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        g = Graph(
            [1, 2, 3, 4, 5, 6],                                        # vertices: any hashable value
            [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1), (1, 4)],  # edges: (u, v) tuples
            layout=self.LAYOUT,                                        # parameter "layout"
            layout_config=self.CONFIG,                                 # parameter "layout_config"
            partitions=self.PARTITIONS,                                # parameter "partitions"
            labels=True,                                               # parameter "labels"
            label_fill_color=BLACK,                                    # parameter "label_fill_color"
        )
        win.play(Create(g), run_time=1.2)   # draw the whole graph stroke by stroke
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: the same six-vertex, seven-edge graph, drawn three times with only the `layout` parameter changed:

- `"circular"`: vertices sit evenly on a circle (the 1→4 chord crosses the center).
- `"spring"`: force-directed random spread (seed 7 pinned for reproducibility).
- `"partite"`: lays `[[1,2,3],[4,5,6]]` out as left and right columns with edges between them.

The three clips are concatenated into one video.

<video src="assets/RTM output/01-Graph-and-DiGraph-layout.mp4" controls width="560"></video>

> Note: random layouts like `"spring"` / `"random"` **must have `seed` pinned in `layout_config`**, otherwise the coordinates differ on every run; deterministic layouts like `"circular"` / `"kamada_kawai"` do not accept `seed`, and passing it raises `TypeError`.

## DiGraph — directed

### class DiGraph (RTM generic vector fallback rendering, arrow-tip updater works)

```python
DiGraph(vertices: Sequence[Hashable], edges: Sequence[tuple[Hashable, Hashable]], labels: bool | dict = False, label_fill_color: str = BLACK, layout: LayoutName | dict[Hashable, Point3DLike] | LayoutFunction = "spring", layout_scale: float | tuple[float, float, float] = 2, layout_config: dict | None = None, vertex_type: type[Mobject] = Dot, vertex_config: dict | None = None, vertex_mobjects: dict | None = None, edge_type: type[Mobject] = Line, partitions: Sequence[Sequence[Hashable]] | None = None, root_vertex: Hashable | None = None, edge_config: dict | None = None)
```

Directed graph: `(u, v)` means an arrow from `u` to `v`, and edges get `add_tip()` automatically at construction. The constructor parameters are identical to `Graph`, with only two differences: edges carry their own tips (vertex order is significant) and the edge updater repositions the tip every frame to prevent deformation.

**Returns**: a `DiGraph` instance.

The only thing unique to `DiGraph` is `tip_config` inside `edge_config`:

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `edge_config["tip_config"]` | `dict` | `{}` (default tip) | tip configuration; keys include `tip_shape` (tip shape class), `tip_length` (length), `tip_width` (width); settable at the common level, or written in a specific edge's dict to override per edge |

#### Sample: tip_config tip size

The same directed graph rendered twice: the default tip versus a tip enlarged one notch with `tip_config={"tip_length": 0.3, "tip_width": 0.26}`.

```python
from real_time_manim import Scene, DiGraph, Text, \
    BLACK, YELLOW, GREY_B, BLUE_E, UP, DOWN, \
    Write, FadeIn, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class DiGraphTipDemo(Scene):
    TIP = None   # tip config: None uses the default size, {...} enlarges the tip one notch

    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-DiGraph-tip", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text(
            "tip_config=%s" % ("{tip_length:0.3, tip_width:0.26}"
                               if self.TIP else "{}"),
            font_size=28, color=GREY_B,
        ).next_to(title, DOWN, buff=0.35)   # show the current tip config
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        d = DiGraph(
            [1, 2, 3, 4],                               # vertices
            [(1, 2), (2, 3), (1, 3), (3, 4), (4, 1)],   # directed edges: u points to v
            layout="circular", layout_scale=2.2,        # circular layout
            labels=True,                                # parameter "labels"
            label_fill_color=BLACK,                     # parameter "label_fill_color"
            edge_config={"color": BLUE_E, "stroke_width": 5,   # common edge style
                         "tip_config": self.TIP or {}},        # parameter "tip_config"
        )
        win.play(Create(d), run_time=1.0)   # draw the whole graph stroke by stroke (tips are repositioned by their updater)
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: a four-vertex ring directed graph; its five directed edges (including `3→4→1` and the crossing `1→3`) are all dark-blue lines of width 5, with the tips controlled by `tip_config`. Two segments for comparison: the first uses the default tip, the second enlarges `tip_length`/`tip_width` to 0.3/0.26 so the tips are clearly chunkier.

<video src="assets/RTM output/01-Graph-and-DiGraph-digraph.mp4" controls width="560"></video>

> Note:
>
> - DiGraph's edge updater does `pop_tips()` then `add_tip()` every frame to reposition the tips — so tips are not stretched out of shape when you move vertices or change layout, which is also why it costs one layer more than Graph.
> - To draw an "undirected graph with double arrows", just use `Graph(..., edge_type=DoubleArrow)` (`CurvedArrow` is not a `Line` subclass and raises `TypeError`).

## from_networkx — building from a networkx graph

### GenericGraph.from_networkx

```python
GenericGraph.from_networkx(nxgraph: nx.Graph | nx.DiGraph, **kwargs)  # classmethod
```

Turns an existing networkx graph directly into a `Graph`/`DiGraph` (`Graph.from_networkx` gives an undirected graph, `DiGraph.from_networkx` gives a directed one); the `**kwargs` (`layout`, `labels`, `vertex_config`, …) are exactly the same as the constructor's.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `nxgraph` | `nx.Graph \| nx.DiGraph` | required | an existing networkx graph object |
| `**kwargs` | — | — | forwarded to the `Graph`/`DiGraph` constructor; accepted keys match the constructor parameter table |

**Returns**: determined by the class it is called on (`Graph.from_networkx` → `Graph`).

#### Sample: importing a wheel graph with from_networkx

`nx.wheel_graph(7)` is networkx's built-in wheel graph (center 0 connected to the outer ring 1–6); it is converted straight into a manim graph and spread out with a seeded spring layout.

```python
import networkx as nx

from real_time_manim import Scene, Graph, Text, \
    BLACK, YELLOW, GREY_B, GREEN, UP, DOWN, \
    Write, FadeIn, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class FromNetworkxDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01-Graph-from_networkx", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text('Graph.from_networkx(nx.wheel_graph(7), layout="spring")',
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.35)   # parameter summary
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        nxg = nx.wheel_graph(7)   # networkx wheel graph: center 0 plus outer ring 1..6
        g = Graph.from_networkx(
            nxg,                                                 # the existing networkx graph
            layout="spring", layout_config={"seed": 5},          # layout name and random seed
            labels=True, label_fill_color=BLACK,                # parameter "labels"
            vertex_config={"color": GREEN, "radius": 0.15},      # common vertex style
        )
        win.play(Create(g), run_time=1.2)   # draw the whole graph stroke by stroke
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: it first builds a 7-vertex, 12-edge wheel graph with networkx (one center point plus an outer ring of six points), then converts it into a manim graph in one step with `Graph.from_networkx(...)`: spring layout (seed 5 pinning the result), small green vertices, black numeric labels. `Create` draws it stroke by stroke.

<video src="assets/RTM output/01-Graph-and-DiGraph-from_networkx.mp4" controls width="560"></video>

> Note: `from_networkx` is just syntax sugar; it ultimately goes through the `Graph(...)`/`DiGraph(...)` constructor — every pitfall in the constructor parameter table (layout seed, the labels dict needing full coverage, etc.) applies to it just the same.

---

See also: [Graph Editing and Layout](01b-Graph-Editing-and-Layout.md) · [Vector Fields and Streamlines](02-Vector-Fields-and-Streamlines.md) · [StreamLines](02b-StreamLines.md)
