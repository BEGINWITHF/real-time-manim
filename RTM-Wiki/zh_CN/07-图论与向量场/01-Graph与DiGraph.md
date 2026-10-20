# 图论：Graph 与 DiGraph

`Graph`（无向图）与 `DiGraph`（有向图）都是"顶点 + 边"的图对象：内部用 networkx 保存拓扑，边自带 updater 跟随顶点移动，所以画完还能继续挪顶点。RTM 没有专门实现图渲染，走通用矢量回退出图——实测 `Create` 逐笔画、标签、箭头、布局动画全部正常（见下方各样例）。

## Graph —— 无向图

### class Graph（RTM 通用矢量回退渲染）

```python
Graph(vertices: Sequence[Hashable], edges: Sequence[tuple[Hashable, Hashable]], labels: bool | dict = False, label_fill_color: str = BLACK, layout: LayoutName | dict[Hashable, Point3DLike] | LayoutFunction = "spring", layout_scale: float | tuple[float, float, float] = 2, layout_config: dict | None = None, vertex_type: type[Mobject] = Dot, vertex_config: dict | None = None, vertex_mobjects: dict | None = None, edge_type: type[Mobject] = Line, partitions: Sequence[Sequence[Hashable]] | None = None, root_vertex: Hashable | None = None, edge_config: dict | None = None)
```

顶点是任意可哈希对象，边用 `(u, v)` 元组（无向图里顺序无关）；每条边都挂着 updater，顶点挪动时边自动跟随。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `vertices` | `Sequence[Hashable]` | 必填 | 顶点名列表；**能填**任意可哈希值（数字、字符串都行），同名顶点会直接 `ValueError` |
| `edges` | `Sequence[tuple]` | 必填 | 边列表，每项 `(u, v)`；顺序无关 |
| `labels` | `bool \| dict` | `False` | `True` 用 `MathTex(顶点名)` 打标签（**要 LaTeX/Typst**）；也可传 `{顶点: 标签mobject}`，**必须覆盖全部顶点**——缺一个就 `LabeledDot` 缺 label 崩（上游行为） |
| `label_fill_color` | `str` | `BLACK` | 仅 `labels=True` 时的标签色；顶点是默认白色 `Dot` 时保持 `BLACK` 最清楚 |
| `layout` | `str \| dict \| LayoutFunction` | `"spring"` | 布局名 / 手写坐标字典 / 自定义布局函数，见下方速查表 |
| `layout_scale` | `float \| tuple` | `2` | 自动布局坐标落在 `[-scale, scale]`；tuple 版 `(sx, sy)` 分轴缩放 |
| `layout_config` | `dict \| None` | `None` | 透传给布局算法的关键字参数；**键必须是该布局函数接受的**（`{"seed": ...}` 只有 `spring`/`random` 这类随机布局吃，传给 `circular`/`kamada_kawai` 会 `TypeError`） |
| `vertex_type` | `type[Mobject]` | `Dot` | 顶点 mobject 类；有标签时自动换成 `LabeledDot` |
| `vertex_config` | `dict \| None` | `None` | 两用：**公共参数** dict（如 `{"radius": 0.16, "color": YELLOW}`），或 `{顶点: 参数dict}` 逐顶点覆盖；两种可混写（键是顶点名的当逐顶点覆盖） |
| `vertex_mobjects` | `dict \| None` | `None` | 直接指定某些顶点用哪个现成 mobject（优先级最高） |
| `edge_type` | `type[Mobject]` | `Line` | 边的类，**必须是 `Line` 子类**（否则 updater 失效）；`DoubleArrow` 实测可用，`CurvedArrow` 不是 `Line` 子类会 `TypeError` |
| `partitions` | `Sequence[Sequence] \| None` | `None` | `layout="partite"` 时的分栏顶点；没列进分栏的顶点单独放最右一栏 |
| `root_vertex` | `Hashable \| None` | `None` | `layout="tree"` 时的根顶点 |
| `edge_config` | `dict \| None` | `None` | 与 `vertex_config` 同款两用：公共边参数 / `{(u,v): 参数dict}` 逐边覆盖（无向图两个方向的键都认） |

**返回**：`Graph` 实例（是 `VMobject`，可直接 `Create`/`add`）。

#### 样例：vertex_config / edge_config 逐项定制

`vertex_config` / `edge_config` 都是"公共参数 + 逐个覆盖"两用 dict：公共键作用于所有顶点/边，键写成顶点名或 `(u, v)` 边元组的项只覆盖那一个。

```python
from real_time_manim import Scene, Graph, Text, VGroup, \
    BLACK, YELLOW, GREY_B, RED, BLUE, ORANGE, UP, DOWN, \
    Write, FadeIn, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class GraphConfigDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Graph-config", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = VGroup(
            Text("vertex_config={radius:0.16, color:YELLOW, 3:{color:RED}}",
                 font_size=26, color=GREY_B),
            Text("edge_config={stroke_width:5, color:BLUE, (1,3):{...:10}}",
                 font_size=26, color=GREY_B),
        ).arrange(DOWN, buff=0.06).next_to(title, DOWN, buff=0.3)   #两行参数摘要
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        g = Graph(
            [1, 2, 3, 4, 5],                                   #五个顶点
            [(1, 2), (2, 3), (3, 4), (4, 5), (1, 5), (1, 3)],  #六条边
            layout="circular", layout_scale=2.4,               #环形布局并放大一点
            labels=True,                                       #参数 “labels”
            label_fill_color=BLACK,                            #参数 “label_fill_color”
            vertex_config={"radius": 0.16, "color": YELLOW,    #公共顶点样式
                           3: {"color": RED, "radius": 0.26}}, #顶点 3 单独覆盖
            edge_config={"stroke_width": 5, "color": BLUE,     #公共边样式
                         (1, 3): {"stroke_width": 10,          #该边单独覆盖
                                  "color": ORANGE}},
        )
        win.play(Create(g), run_time=1.0)   #逐笔画出整张图
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：造一个五顶点六边的环形图，所有顶点是半径 0.16 的黄色圆点（顶点 3 单独覆盖成更大的红点），所有边是 5 号粗的蓝线（`(1, 3)` 这条单独覆盖成 10 号粗的橙线），`labels=True` 给每个顶点打上黑色数字标签。`Create` 逐笔画出整张图。

<video src="assets/RTM output/01-Graph与DiGraph-config.mp4" controls width="560"></video>

> 提醒：`vertex_config`/`edge_config` 的"逐个覆盖"项是**整体替换**而非合并——给某顶点写了 `{color: RED}`，公共的 `radius` 就不再作用于它。另外 `labels=True` 的标签走 `MathTex`，黑字白点才看得清，别把 `label_fill_color` 改成和顶点同色。

### layout —— 布局（12 种取值速查）

`layout` 决定顶点怎么摆；大部分取值就是 networkx 的同名布局算法，`layout_config` 透传该算法的关键字参数。

| layout 值 | 形态 | 常用 `layout_config` | 实测 |
| --- | --- | --- | --- |
| `"spring"`（默认） | Fruchterman-Reingold 力导向，均衡散开 | `{"k":..., "seed":...}`（支持 `seed`） | 样例实测 |
| `"circular"` | 顶点均匀排在一个圆上 | -（不接受 `seed`） | 样例实测 |
| `"partite"` | 按 `partitions` 分成若干竖栏（画神经网络层常用） | 需配合构造参数 `partitions` | 样例实测 |
| `"kamada_kawai"` | 尽量保持给定图距离 | `{"dist": {u:{v:d}}}` | 构造实测 OK，未单独出片 |
| `"planar"` | 平面图布局，边尽量不交叉（非平面图会报错） | - | 同上 |
| `"random"` | 随机撒点 | `{"seed": 0}`（支持 `seed`） | 同上 |
| `"shell"` | 同心圆分层 | `{"nlist": [[...], [...]]}` | 同上 |
| `"spectral"` | 图拉普拉斯特征向量投影 | - | 同上 |
| `"spiral"` | 螺旋线 | - | 同上 |
| `"tree"` | 树形分层 | 需 `root_vertex`，可选 `{"vertex_spacing", "orientation": "down"}` | 同上 |
| `{顶点: [x,y,z]}` | 手写坐标字典 | - | 同上 |
| `callable` | 自定义布局函数，签名 `(nx_graph, scale=2, **kwargs) -> dict` | 用 `layout_config` 传自定义参数 | 同上 |

#### 样例：layout 三种布局对比

同一张图只换 `layout`：`"circular"` 环形、`"spring"` 力导向（配 `layout_config={"seed": 7}` 固定随机结果，两引擎才能逐帧对上）、`"partite"` 按 `partitions` 分成两栏。

```python
from real_time_manim import Scene, Graph, Text, \
    BLACK, YELLOW, GREY_B, UP, DOWN, \
    Write, FadeIn, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class GraphLayoutDemo(Scene):
    LAYOUT = "circular"   #布局名：换成 “spring” 力导向散开，“partite” 见下方变体
    PARTITIONS = None     #“partite” 布局的分栏；其他布局留 None
    CONFIG = {}           #“layout_config”：布局算法参数（如 spring 的随机种子）

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Graph-layout", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text('layout="%s"' % self.LAYOUT, font_size=30, color=GREY_B)   #当前布局名
        lab.next_to(title, DOWN, buff=0.35)   #标签放到标题正下方
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        g = Graph(
            [1, 2, 3, 4, 5, 6],                                        #顶点：任意可哈希值
            [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1), (1, 4)],  #边：(u, v) 元组
            layout=self.LAYOUT,                                        #参数 “layout”
            layout_config=self.CONFIG,                                 #参数 “layout_config”
            partitions=self.PARTITIONS,                                #参数 “partitions”
            labels=True,                                               #参数 “labels”
            label_fill_color=BLACK,                                    #参数 “label_fill_color”
        )
        win.play(Create(g), run_time=1.2)   #逐笔画出整张图
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：六个顶点七条边的同一张图，只换 `layout` 参数画三遍——`"circular"` 顶点均匀站成一个圈（1→4 的弦跨过圆心）、`"spring"` 力导向随机散开（种子 7 写死保证可复现）、`"partite"` 把 `[[1,2,3],[4,5,6]]` 排成左右两栏、栏间连线。三条片段拼在一条视频里。

<video src="assets/RTM output/01-Graph与DiGraph-layout.mp4" controls width="560"></video>

> 提醒：`"spring"` / `"random"` 这类随机布局**一定要在 `layout_config` 里写死 `seed`**，否则每次跑坐标都不一样；而 `"circular"` / `"kamada_kawai"` 这类确定性布局不吃 `seed`，传了反而 `TypeError`。

## DiGraph —— 有向图

### class DiGraph（RTM 通用矢量回退渲染，箭头 updater 正常）

```python
DiGraph(vertices: Sequence[Hashable], edges: Sequence[tuple[Hashable, Hashable]], labels: bool | dict = False, label_fill_color: str = BLACK, layout: LayoutName | dict[Hashable, Point3DLike] | LayoutFunction = "spring", layout_scale: float | tuple[float, float, float] = 2, layout_config: dict | None = None, vertex_type: type[Mobject] = Dot, vertex_config: dict | None = None, vertex_mobjects: dict | None = None, edge_type: type[Mobject] = Line, partitions: Sequence[Sequence[Hashable]] | None = None, root_vertex: Hashable | None = None, edge_config: dict | None = None)
```

有向图：`(u, v)` 表示从 `u` 指向 `v` 的箭头，边在构造时自动 `add_tip()`。构造参数与 `Graph` 完全一致，差异只有两点：边自带箭头（顶点顺序有意义）、边的 updater 每帧会重摆箭头尖防止变形。

**返回**：`DiGraph` 实例。

DiGraph 独有的只有 `edge_config` 里的 `tip_config`：

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `edge_config["tip_config"]` | `dict` | `{}`（默认箭头尖） | 箭头尖配置，键如 `tip_shape`（箭头形状类）、`tip_length`（长）、`tip_width`（宽）；可写在公共层，也可写在某条边的 dict 里逐边覆盖 |

#### 样例：tip_config 箭头尖大小

同一张有向图渲两遍：默认箭头尖 vs `tip_config={"tip_length": 0.3, "tip_width": 0.26}` 放大一号的箭头尖。

```python
from real_time_manim import Scene, DiGraph, Text, \
    BLACK, YELLOW, GREY_B, BLUE_E, UP, DOWN, \
    Write, FadeIn, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class DiGraphTipDemo(Scene):
    TIP = None   #箭头尖配置：None 用默认大小，{...} 把箭头放大一号

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-DiGraph-tip", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text(
            "tip_config=%s" % ("{tip_length:0.3, tip_width:0.26}"
                               if self.TIP else "{}"),
            font_size=28, color=GREY_B,
        ).next_to(title, DOWN, buff=0.35)   #显示当前箭头尖配置
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        d = DiGraph(
            [1, 2, 3, 4],                               #顶点
            [(1, 2), (2, 3), (1, 3), (3, 4), (4, 1)],   #有向边：u 指向 v
            layout="circular", layout_scale=2.2,        #环形布局
            labels=True,                                #参数 “labels”
            label_fill_color=BLACK,                     #参数 “label_fill_color”
            edge_config={"color": BLUE_E, "stroke_width": 5,   #公共边样式
                         "tip_config": self.TIP or {}},        #参数 “tip_config”
        )
        win.play(Create(d), run_time=1.0)   #逐笔画出整张图（箭头随 updater 重定位）
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：四个顶点的环形有向图，五条有向边（含 `3→4→1` 和横穿的 `1→3`）都是深蓝 5 号粗线，箭头尖由 `tip_config` 控制。两段对比：第一段用默认箭头尖，第二段把 `tip_length`/`tip_width` 放大到 0.3/0.26，箭头明显更粗大。

<video src="assets/RTM output/01-Graph与DiGraph-digraph.mp4" controls width="560"></video>

> 提醒：DiGraph 的边 updater 每帧会 `pop_tips()` 再 `add_tip()` 重摆箭头尖——所以挪动顶点/改布局时箭头不会被拉变形，这也是它比 Graph 多一层开销的原因。想画"无向图但用双向箭头"，用 `Graph(..., edge_type=DoubleArrow)` 即可（`CurvedArrow` 不是 `Line` 子类，会 `TypeError`）。

## from_networkx —— 从 networkx 图构建

### GenericGraph.from_networkx

```python
GenericGraph.from_networkx(nxgraph: nx.Graph | nx.DiGraph, **kwargs)  # classmethod
```

把现成的 networkx 图直接转成 `Graph`/`DiGraph`（`Graph.from_networkx` 出无向图、`DiGraph.from_networkx` 出有向图），`**kwargs`（`layout`、`labels`、`vertex_config`……）与构造函数完全相同。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `nxgraph` | `nx.Graph \| nx.DiGraph` | 必填 | 现成的 networkx 图对象 |
| `**kwargs` | — | — | 透传给 `Graph`/`DiGraph` 构造函数，能填的与构造参数表一致 |

**返回**：由调用的类决定（`Graph.from_networkx` → `Graph`）。

#### 样例：from_networkx 导入轮状图

`nx.wheel_graph(7)` 是 networkx 自带的轮状图（中心 0 号连外圈 1~6 号），直接转成 manim 图并用带种子的 spring 布局摆开。

```python
import networkx as nx

from real_time_manim import Scene, Graph, Text, \
    BLACK, YELLOW, GREY_B, GREEN, UP, DOWN, \
    Write, FadeIn, Create
from real_time_manim.vulkan_bind import MLWindow, Wait

class FromNetworkxDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        title = Text("01-Graph-from_networkx", font_size=34, color=YELLOW).to_edge(UP)   #页面标题
        win.play(Write(title), run_time=0.5)   #写出标题
        lab = Text('Graph.from_networkx(nx.wheel_graph(7), layout="spring")',
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.35)   #参数摘要
        win.play(FadeIn(lab, shift=DOWN), run_time=0.3)   #标签从下方淡入
        nxg = nx.wheel_graph(7)   #networkx 的轮状图：中心 0 号 + 外圈 1~6 号
        g = Graph.from_networkx(
            nxg,                                                 #现成的 networkx 图
            layout="spring", layout_config={"seed": 5},          #布局名与随机种子
            labels=True, label_fill_color=BLACK,                #参数 “labels”
            vertex_config={"color": GREEN, "radius": 0.15},      #公共顶点样式
        )
        win.play(Create(g), run_time=1.2)   #逐笔画出整张图
        win.play(Wait(0.6))   #进行 0.6s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：先用 networkx 造一个 7 顶点 12 边的轮状图（中心一个点、外圈六个点成环），然后 `Graph.from_networkx(...)` 一步转成 manim 图：spring 布局（种子 5 固定结果）、绿色小顶点、黑色数字标签。`Create` 逐笔画出。

<video src="assets/RTM output/01-Graph与DiGraph-from_networkx.mp4" controls width="560"></video>

> 提醒：`from_networkx` 就是个语法糖，最终还是走 `Graph(...)`/`DiGraph(...)` 构造——构造参数表里所有坑（布局 seed、labels dict 要全覆盖等）对它同样适用。

---

相关：[图的增删与布局](01b-图的增删与布局.md) · [向量场与流线](02-向量场与流线.md) · [流线 StreamLines](02b-流线StreamLines.md)
