# Graph editing and layout transforms

`GenericGraph` offers index access plus a set of `.animate`-ready add/remove/layout methods, all usable with `win.play(g.animate.xxx(...))` for smooth animation. RTM has no dedicated graph renderer; it goes through the generic vector fallback. In testing, indexing vertices and edges, adding vertices/edges, removing vertices/edges and repeatedly changing layout all work (see the samples below).

## g[k] — indexing a vertex/edge

### GenericGraph.__getitem__ (RTM generic vector fallback rendering)

```python
GenericGraph.__getitem__(k: Hashable | tuple[Hashable, Hashable]) -> Mobject
```

`g[vertex name]` fetches the vertex mobject and `g[(u, v)]` fetches the edge mobject; this is the most common way to access them (paired with `.animate` for single-vertex/single-edge animation); an unknown key raises `ValueError`.

| Parameter | Type | Description |
| --- | --- | --- |
| `k` | `Hashable` | vertex name; fetches the vertex mobject |
| `k` | `tuple[Hashable, Hashable]` | `(u, v)` edge tuple; fetches the edge mobject |

#### Sample: getitem fetching a vertex and an edge

Four vertices on a ring: first `g[2].animate.shift(...)` moves vertex 2 (its edges follow automatically), then `g[(1, 2)].animate.set_stroke(...)` thickens the (1,2) edge and turns it orange.

```python
from real_time_manim import Scene, Graph, Text, \
    BLACK, YELLOW, GREY_B, ORANGE, UP, DOWN, LEFT, \
    Write, FadeIn, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class GetItemDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        title = Text("01b-Graph-getitem", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text("g[2].animate.shift(...)   g[(1,2)].animate.set_stroke(...)",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.3)   # signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        g = Graph(
            [1, 2, 3, 4], [(1, 2), (2, 3), (3, 4), (4, 1)],   # four vertices on a ring
            layout="circular", layout_scale=2.2,             # circular layout
            labels=True, label_fill_color=BLACK,             # numeric vertex labels
        )
        win.play(Create(g), run_time=0.8)   # draw the whole graph stroke by stroke
        win.play(g[2].animate.shift(UP + LEFT), run_time=0.8)   # parameter "k": move vertex 2; its edges follow automatically
        win.play(g[(1, 2)].animate.set_stroke(ORANGE, width=8), run_time=0.5)   # parameter "k": thicken and recolor the (1,2) edge
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: it first draws the four-vertex ring graph stroke by stroke, then moves vertex 2 one step up-left — the four edges, each carrying an updater, follow their endpoints automatically.

Then it thickens the `(1, 2)` edge to width 8 and turns it orange, showing that edges can be indexed precisely and animated individually.

<video src="assets/RTM output/01b-Graph-Editing-and-Layout-getitem.mp4" controls width="560"></video>

> Note: indexing returns **the same mobject itself** (not a copy), so any `.animate` you apply to it acts directly on the graph; to restore it after a change, `set_stroke` it back yourself.

## add_vertices / add_edges — adding vertices and edges

### GenericGraph.add_vertices / add_edges

```python
GenericGraph.add_vertices(*vertices: Hashable, positions: dict | None = None, labels: bool | dict = False, label_fill_color: str = BLACK, vertex_type: type[Mobject] = Dot, vertex_config: dict | None = None, vertex_mobjects: dict | None = None)
GenericGraph.add_edges(*edges: tuple[Hashable, Hashable], edge_type: type[Mobject] = Line, edge_config: dict | None = None, **kwargs)
```

`g.animate.add_vertices(...)` smoothly "grows" new vertices (`positions=None` places them at the graph center, and **in practice you nearly always want to give `positions`**); any new vertices appearing in `add_edges` are created automatically. Both **return** a `Group` of the added vertices and edges.

### Add/remove parameters

| Method | Parameter | Type | Default | Description |
| --- | --- | --- | --- | --- |
| add_vertices | *vertices | `Hashable` | required | new vertex names |
| add_vertices | positions | `dict \| None` | `None` | `{vertex: [x,y,z]}`; defaults to the graph center |
| add_vertices | labels | `bool \| dict` | `False` | same as the constructor parameter |
| add_vertices | label_fill_color | `str` | `BLACK` | label color |
| add_vertices | vertex_type | `type[Mobject]` | `Dot` | vertex class |
| add_vertices | vertex_config | `dict \| None` | `None` | vertex parameters (merged with the graph's defaults) |
| add_vertices | vertex_mobjects | `dict \| None` | `None` | direct mobjects for the vertices |
| add_edges | *edges | `tuple` | required | edges `(u, v)` |
| add_edges | edge_type | `type[Mobject]` | `Line` | edge class |
| add_edges | edge_config | `dict \| None` | `None` | common edge parameters, or `{(u,v): kwargs}` |
| add_edges | **kwargs | - | - | forwarded to `add_vertices` (`positions`, `labels`, `vertex_config`, …) |

#### Sample: add — adding vertices and edges

The three-vertex, two-edge ring graph first grows an edge connected to the new vertex 4, then adds an isolated vertex 5, and finally connects 4 and 5.

```python
from real_time_manim import Scene, Graph, Text, \
    BLACK, YELLOW, GREY_B, UP, DOWN, LEFT, \
    Write, FadeIn, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class GraphAddDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # the graph's dynamic methods replay animations internally: wire "self.play" to win.play first
        title = Text("01b-Graph-add", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text("g.animate.add_edges((1,4), positions=..., labels=True)",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.3)   # signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        g = Graph(
            [1, 2, 3], [(1, 2), (2, 3)],   # start with three vertices and two edges
            layout="circular", layout_scale=2.0,   # circular layout
            labels=True, label_fill_color=BLACK,   # numeric vertex labels
        )
        win.play(Create(g), run_time=0.6)   # draw the initial graph stroke by stroke
        win.play(g.animate.add_edges((1, 4), positions={4: [3.2, 1.2, 0]},   # parameters "*edges" / "positions"
                                     labels=True), run_time=0.8)   # the new edge grows out together with the new vertex 4
        win.play(g.animate.add_vertices(5, positions={5: [3.2, -1.4, 0]},   # parameter "*vertices"
                                         labels=True), run_time=0.6)   # add a single isolated vertex 5 only
        win.play(g.animate.add_edges((4, 5)), run_time=0.5)   # then connect the two new vertices 4 and 5
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does:

- `add_edges((1, 4), positions=..., labels=True)` contains vertex 4, which is not yet in the graph; upstream creates it according to `positions`, so the edge and the vertex grow in smoothly together.
- `add_vertices(5, ...)` adds just one labeled isolated vertex.
- Finally `add_edges((4, 5))` connects the two new vertices (without `positions` a new vertex would land at the graph center, but here both vertices already exist, so it just draws the line).

<video src="assets/RTM output/01b-Graph-Editing-and-Layout-add.mp4" controls width="560"></video>

> Note:
>
> - All of `add_edges`'s `**kwargs` are forwarded to `add_vertices` — so writing `positions`, `labels`, `label_fill_color` inside `add_edges(...)` works just as well.
> - **Measured 2026-10-17**: the graph's dynamic methods (add/remove/change_layout) under `.animate` go through `override_animate`, which returns an `AnimationGroup`/`Uncreate`/`_MethodAnimation`, played **directly by `win.play`**, and do **not** call `self.play` — the `self.play = win.play` on the first line of the sample is belt-and-braces wiring (what really must be wired is a scene method like `move_camera`).

## remove_vertices / remove_edges — removing vertices and edges

### GenericGraph.remove_vertices / remove_edges

```python
GenericGraph.remove_vertices(*vertices: Hashable)
GenericGraph.remove_edges(*edges: tuple[Hashable, Hashable])
```

Removing a vertex also removes every edge connected to it; removing an edge keeps the vertices. `g.animate.remove_vertices(...)` / `g.animate.remove_edges(...)` produce `Uncreate` animations and **return** a `Group` of the removed mobjects.

| Method | Parameter | Type | Description |
| --- | --- | --- | --- |
| remove_vertices | *vertices | `Hashable` | vertices to remove; incident edges are removed too |
| remove_edges | *edges | `tuple[Hashable, Hashable]` | edges to remove; both endpoint vertices are kept |

#### Sample: remove — removing edges and vertices

Four vertices on a ring plus one chord `(1, 3)`: first `remove_edges((1, 3))` removes just the chord (it fades out whole), then `remove_vertices(4)` removes vertex 4 (its two edges vanish along with it).

```python
from real_time_manim import Scene, Graph, Text, \
    BLACK, YELLOW, GREY_B, UP, DOWN, LEFT, \
    Write, FadeIn, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class GraphRemoveDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # the graph's dynamic methods replay animations internally: wire "self.play" to win.play first
        title = Text("01b-Graph-remove", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = Text("g.animate.remove_edges((1,3))  then  g.animate.remove_vertices(4)",
                   font_size=24, color=GREY_B).next_to(title, DOWN, buff=0.3)   # signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        g = Graph(
            [1, 2, 3, 4], [(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)],   # four vertices on a ring plus one chord
            layout="circular", layout_scale=2.2,   # circular layout
            labels=True, label_fill_color=BLACK,   # numeric vertex labels
        )
        win.play(Create(g), run_time=0.8)   # draw the whole graph stroke by stroke
        win.play(g.animate.remove_edges((1, 3)), run_time=0.5)   # parameter "*edges": remove edges only, keep the vertices
        win.play(g.animate.remove_vertices(4), run_time=0.5)   # parameter "*vertices": remove the vertex and its incident edges
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: the five-edge graph first loses the crossing chord `(1, 3)`, leaving all four vertices intact; then it removes vertex 4, and the `(3, 4)` and `(4, 1)` edges connected to it fade out too — demonstrating the difference between "removing a vertex cascades to its edges" and "removing an edge leaves the vertices alone".

<video src="assets/RTM output/01b-Graph-Editing-and-Layout-remove.mp4" controls width="560"></video>

> Note: after removal the **layout is not recomputed automatically** — the remaining vertices stay where they are; call `change_layout` again to re-space them.

## change_layout — re-layout

### GenericGraph.change_layout

```python
GenericGraph.change_layout(layout: LayoutName | dict[Hashable, Point3DLike] | LayoutFunction = "spring", layout_scale: float | tuple[float, float, float] = 2, layout_config: dict[str, Any] | None = None, partitions: list[list[Hashable]] | None = None, root_vertex: Hashable | None = None) -> Graph
```

`move_to`s every vertex to its new position under the new layout; most often paired with `.animate` as a "layout transform" transition; **returns** `self` (chainable).

### Parameters

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| layout | same as constructor | `"spring"` | new layout |
| layout_scale | `float \| tuple` | `2` | new scale |
| layout_config | `dict \| None` | `None` | layout algorithm parameters |
| partitions | `list[list] \| None` | `None` | merged into `layout_config["partitions"]` |
| root_vertex | `Hashable \| None` | `None` | merged into `layout_config["root_vertex"]` |

#### Sample: change_layout transforming layout repeatedly

A five-vertex ring graph goes through two layout transforms in a row: `"spring"` force-directed spread (seed 7 pinned), then a hand-written coordinate dict `{1: [-3.2, 0, 0], ...}` lining them up horizontally.

```python
from real_time_manim import Scene, Graph, Text, VGroup, \
    BLACK, YELLOW, GREY_B, UP, DOWN, LEFT, \
    Write, FadeIn, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class GraphChangeLayoutDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   # create an RTM window
        win.scene = self   # bind the manim scene named "self" to the RTM window named "win"
        self.play = win.play   # the graph's dynamic methods replay animations internally: wire "self.play" to win.play first
        title = Text("01b-Graph-change_layout", font_size=34, color=YELLOW).to_edge(UP)   # page title
        win.play(Write(title), run_time=0.5)   # write out the title
        lab = VGroup(
            Text('g.animate.change_layout("spring", layout_config={"seed":7})',
                 font_size=26, color=GREY_B),
            Text("g.animate.change_layout({1:[-3.2,0,0], ...})  # manual",
                 font_size=26, color=GREY_B),
        ).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.3)   # two-line signature label
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   # label fades in from below
        g = Graph(
            [1, 2, 3, 4, 5], [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)],   # five vertices on a ring
            layout="circular", layout_scale=2.2,   # initial circular layout
            labels=True, label_fill_color=BLACK,   # numeric vertex labels
        )
        win.play(Create(g), run_time=0.6)   # draw the whole graph stroke by stroke
        win.play(g.animate.change_layout("spring", layout_config={"seed": 7}),   # parameter "layout"
                 run_time=1.0)   # every vertex moves to the new layout, edges follow
        win.play(g.animate.change_layout(
            {1: [-3.2, 0, 0], 2: [-1.6, 0, 0], 3: [0, 0, 0],   # a hand-written coordinate dict is a valid layout too
             4: [1.6, 0, 0], 5: [3.2, 0, 0]}), run_time=1.0)   # this time line up the five vertices horizontally
        win.play(Wait(0.6))   # wait for 0.6 s
        win.close()   # close the RTM window
```

What this code does: the five-vertex ring graph first morphs into the seeded spring force-directed layout — vertices translate to their new positions and the edge updaters keep every segment attached to its endpoints.

Then it morphs into the hand-written coordinate dict, stretching the five points into a horizontal line, showing that `layout` accepts both algorithm names and ready-made coordinates.

<video src="assets/RTM output/01b-Graph-Editing-and-Layout-change_layout.mp4" controls width="560"></video>

> Note:
>
> - `change_layout` accepts exactly the same `layout`/`layout_config` rules as the constructor — `"spring"`/`"random"` need `seed` pinned, deterministic layouts like `"circular"` raise `TypeError` if you pass `seed`; and a hand-written coordinate dict's keys must **cover every vertex in the graph**.
> - For both engines' coordinates to match frame by frame, not a single random-layout seed may be omitted.

## Other graph theory details

| Item | Description |
| --- | --- |
| `Graph.update_edges(graph)` | the updater body: resets each edge's ends to the current positions of its two vertices; auto-attached by `add_updater`, **do not call manually** |
| `Graph.vertices` / `.edges` / `._layout` | public attributes: vertex dict, edge dict `{(u,v): mobject}`, current layout coordinates |
| manual vertex repositioning | `g[v].move_to(...)` moves it directly and edges follow; but `_layout` does not stay in sync (only `change_layout` recomputes it wholesale) |
| `LayoutFunction` (Protocol) | a custom layout function must be pure `(graph, scale=2, **kwargs) -> dict[node, np.ndarray(3)]` and must not mutate the passed graph |
| graph dynamic methods and RTM | the `.animate` versions of `add_vertices`/`remove_vertices`/`change_layout` are built by `_AnimationBuilder` and played **directly by `win.play`**; measured to **not** call back into `self.play`; the `self.play = win.play` on the first line of the sample is belt-and-braces wiring (only scene methods like `move_camera` truly need it — see the first line of the add/remove samples) |

---

See also: [Graph and DiGraph](01-Graph-and-DiGraph.md) · [Vector Fields and Streamlines](02-Vector-Fields-and-Streamlines.md) · [StreamLines](02b-StreamLines.md)
