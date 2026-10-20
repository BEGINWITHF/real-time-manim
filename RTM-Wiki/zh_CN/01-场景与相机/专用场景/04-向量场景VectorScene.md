# 向量场景（VectorScene）

在数轴平面上画向量、写坐标、标注基向量的线性代数教学场景，网格变换玩法见 [线性变换场景](05-线性变换场景.md)。RTM 实测全部可播动画的方法都能用。

先记一个通用前提：`add_plane()` 返回的平面**不会**自动挂到 `self.plane` 上，而 `get_vector` / `add_vector` 又要读 `self.plane` —— 所以样例里每次 `add_plane` 之后都紧跟一句 `self.plane = plane` 手动挂上，你自己的代码也要这么写。

## 参数

### class VectorScene

```python
def __init__(self, basis_vector_stroke_width: float = 6.0, **kwargs: Any) -> None:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `basis_vector_stroke_width` | `float` | `6.0` | 基向量（`get_basis_vectors` 生成的 `i_hat` / `j_hat`）线宽；**能填**正数，样例对比 `6.0` 与 `2.0`，改小变细 |
| `**kwargs` | `Any` | — | 透传给 `Scene.__init__`（`random_seed` 等，见 [Scene 基础](../场景/01-Scene基础.md)） |

> **返回**：无（构造实例）。

### add_plane / add_axes

```python
def add_plane(self, animate: bool = False, **kwargs: Any) -> NumberPlane:
def add_axes(self, animate: bool = False, color: ParsableManimColor | Iterable[ParsableManimColor] = WHITE) -> Axes:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `animate` | `bool` | `False` | `True` 时用 `Create` 播画网格 / 画坐标轴的入场（内部 `self.play`，RTM 里先 `self.play = win.play`） |
| `color` | `ParsableManimColor \| Iterable[...]` | `WHITE` | 仅 `add_axes`：坐标轴颜色，**能填**任意颜色 |
| `**kwargs` | `Any` | — | 仅 `add_plane`：透传给 `NumberPlane`（如 `x_range`、`y_range`） |

> **返回**：`add_plane` 返回 `NumberPlane`（记得手动 `self.plane = ...`），`add_axes` 返回 `Axes`。

#### 样例：构造参数与 `add_plane`改动

同一个场景跑两遍，只换构造参数 `basis_vector_stroke_width`：先 `Create` 画网格，再换成画坐标轴，最后放上基向量看线宽差别。

```python
from real_time_manim import VectorScene, Text, \
    UP, YELLOW
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   #瞬间换掉顶部说明文字，不占动画时间
    cap.become(Text(text, font_size=28, color=YELLOW).to_edge(UP))

class PlaneAxesBase(VectorScene):
    STROKE = 6.0   #子类改小，看基向量变细
    TAG = ""       #子类填标题里的线宽数字

    def __init__(self, **kwargs):
        super().__init__(basis_vector_stroke_width=self.STROKE, **kwargs)   #把 “basis_vector_stroke_width” 传给 VectorScene.__init__

    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #add_plane / add_axes 内部会调 self.play，先接到窗口上
        cap = Text("", font_size=28, color=YELLOW)   #顶部说明文字（内容后面换）
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(cap)   #放进场景

        say(cap, "add_plane(animate=True)")
        plane = self.add_plane(animate=True)   #用 Create 画出网格平面
        self.plane = plane   #get_vector / add_vector 都要读 self.plane，手动挂上
        win.play(Wait(0.6))   #停 0.6s

        say(cap, "add_axes(animate=True, color=WHITE)")
        self.remove(plane)   #把网格收走
        self.add_axes(animate=True, color=WHITE)   #用 Create 画出坐标轴
        win.play(Wait(0.4))   #停 0.4s

        say(cap, "get_basis_vectors() stroke=%.1f" % self.STROKE)
        self.add(self.get_basis_vectors())   #放上 i_hat / j_hat，线宽就是构造参数
        win.play(Wait(0.8))   #停 0.8s 收工
        win.close()   #关闭 RTM 窗口


class PlaneAxesWide(PlaneAxesBase):
    STROKE = 6.0   #默认线宽
    TAG = "6.0"


class PlaneAxesThin(PlaneAxesBase):
    STROKE = 2.0   #细一档
    TAG = "2.0"
```

这段代码在做什么：第一段（线宽 6.0）先用 `add_plane(animate=True)` 把网格 `Create` 出来并手动挂上 `self.plane`，收走网格后用 `add_axes(animate=True, color=WHITE)` 画坐标轴，最后放上默认的 `i_hat`/`j_hat` —— 基向量的粗细就是构造参数。第二段除了把线宽改成 `2.0` 之外一字不差，两段拼在同一条视频里对比。

<video src="assets/RTM output/04-向量场景VectorScene-plane.mp4" controls width="560"></video>

> 提醒：`self.plane = plane` 别忘了（`get_vector` / `add_vector` / `label_vector` 都读它）。`add_axes` 画完坐标轴后，样例刻意 `self.remove(plane)` 再画轴，是为了让两步在画面上不叠在一起。`basis_vector_stroke_width` 只影响 `get_basis_vectors()`（也影响场景启动时自动放上的基向量），不影响坐标轴线宽。

### add_vector / get_vector

```python
def add_vector(self, vector: Arrow | Vector3DLike, color: ParsableManimColor | Iterable[ParsableManimColor] = PURE_YELLOW, animate: bool = True, **kwargs: Any) -> Arrow:
def get_vector(self, numerical_vector: Vector3DLike, **kwargs: Any) -> Arrow:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `vector` | `Arrow \| Vector3DLike` | — | 向量：坐标列表 `[2, 1]` 或现成的 `Arrow` 对象 |
| `color` | `ParsableManimColor \| Iterable[...]` | `PURE_YELLOW` | 向量颜色，**能填**任意颜色 |
| `animate` | `bool` | `True` | 是否 `GrowArrow` 出场（内部 `self.play`，RTM 里先 `self.play = win.play`） |
| `numerical_vector` | `Vector3DLike` | — | 仅 `get_vector`：按坐标生成 `Arrow` |
| `**kwargs` | `Any` | — | 透传给 `Arrow` / 动画 |

> **返回**：两者都返回 `Arrow`；`add_vector` 会把它加进场景并登记进 `moving_vectors`，`get_vector` **只生成不加**，什么时候 `self.add` 由你自己决定。

#### 样例：`add_vector` / `get_vector`改动

同一张网格上：`add_vector` 加一个自动出场的黄色向量，`get_vector` 生成另一个后手动 `self.add`。

```python
from real_time_manim import VectorScene, Text, \
    UP, YELLOW
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   #瞬间换掉顶部说明文字，不占动画时间
    cap.become(Text(text, font_size=28, color=YELLOW).to_edge(UP))

class VectorAddDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #add_vector 内部会调 self.play，先接到窗口上
        cap = Text("", font_size=28, color=YELLOW)   #顶部说明文字（内容后面换）
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(cap)   #放进场景
        plane = self.add_plane(animate=False)   #直接放上网格
        self.plane = plane   #get_vector / add_vector 都要读 self.plane，手动挂上

        say(cap, "add_vector([2, 1], color=YELLOW, animate=True)")
        self.add_vector([2, 1], color=YELLOW, animate=True)   #坐标生成向量，GrowArrow 出场
        win.play(Wait(0.8))   #停 0.8s

        say(cap, "get_vector([-2, 1]) -> self.add(arrow)")
        arrow = self.get_vector([-2, 1])   #只生成 Arrow：不加入场景、不登记
        self.add(arrow)   #自己决定什么时候加进去
        win.play(Wait(0.8))   #停 0.8s 收工
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：放好网格并挂上 `self.plane` 后，先 `add_vector([2, 1], animate=True)` —— 按坐标生成黄色箭头并 `GrowArrow` 长出来；再用 `get_vector([-2, 1])` 只生成一个白色箭头对象，场景里看不到任何变化，直到手动 `self.add(arrow)` 它才出现。一屏里最终并排两个向量，直观展示两个方法"加不加、播不播"的区别。

<video src="assets/RTM output/04-向量场景VectorScene-addvec.mp4" controls width="560"></video>

> 提醒：`add_vector` 的 `animate` 默认是 `True`（`get_vector` 则完全不播动画）；想要"先生成、稍后再上屏"就用 `get_vector` + 自己 `self.add`。`color` 只在你传坐标（而不是现成 `Arrow`）时生效。这两个方法都要读 `self.plane`，别忘了手动挂。

### write_vector_coordinates、label_vector、get_vector_label

```python
def write_vector_coordinates(self, vector: Vector, **kwargs: Any) -> Matrix:
def label_vector(self, vector: Vector, label: ManimTextLabel | str, animate: bool = True, **kwargs: Any) -> ManimTextLabel:
def get_vector_label(self, vector: Vector, label: ManimTextLabel | str, at_tip: bool = False, direction: str = "left", rotate: bool = False, color: ParsableManimColor | None = None, label_scale_factor: float = LARGE_BUFF - 0.2) -> ManimTextLabel:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `vector` | `Vector` | — | 被标注 / 写坐标的向量（场景里已有的 `Arrow`） |
| `label` | `ManimTextLabel \| str` | — | 标签内容；**传单个字符时排成带箭头的字母形式**（样例里的 `v`），多字符正常横排 |
| `animate` | `bool` | `True` | 仅 `label_vector`：是否 `Write` 出场（内部 `self.play`，RTM 里先 `self.play = win.play`） |
| `at_tip` | `bool` | `False` | 仅 `get_vector_label`：标签放到箭头尖端 |
| `direction` | `str` | `"left"` | 仅 `get_vector_label`：放向量哪一侧，`"left"` / `"right"` |
| `rotate` | `bool` | `False` | 仅 `get_vector_label`：是否随向量方向倾斜 |
| `color` | `ParsableManimColor \| None` | `None`（跟随向量） | 仅 `get_vector_label`：标签颜色 |
| `label_scale_factor` | `float` | `LARGE_BUFF - 0.2` | 仅 `get_vector_label`：标签缩放，样例用 `1.0` |
| `**kwargs` | `Any` | — | 透传给 `Matrix` / 标签创建 / 动画 |

> **返回**：`write_vector_coordinates` 返回 `Matrix`（列矩阵，并进前景层）；`label_vector` / `get_vector_label` 返回标签 mobject —— 前者播动画并登记，后者**只生成**，自己 `self.add`。

#### 样例：`write_vector_coordinates` / `label_vector`改动

一个向量依次做三件事：写出列矩阵 `[2, 1]`、`label_vector` 写上标签（单字符排成箭头字母）、`get_vector_label` 在尖端生成另一个标签手动加上。

```python
from real_time_manim import VectorScene, Text, \
    UP, YELLOW, GREEN
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   #瞬间换掉顶部说明文字，不占动画时间
    cap.become(Text(text, font_size=28, color=YELLOW).to_edge(UP))

class VectorLabelDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #下面几个方法内部都会调 self.play，先接到窗口上
        cap = Text("", font_size=28, color=YELLOW)   #顶部说明文字（内容后面换）
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(cap)   #放进场景
        plane = self.add_plane(animate=False)   #直接放上网格
        self.plane = plane   #add_vector 要读 self.plane，手动挂上
        v = self.add_vector([2, 1], color=YELLOW, animate=True)   #先要有一个向量对象

        say(cap, "write_vector_coordinates(v)")
        self.write_vector_coordinates(v)   #写出列矩阵 [2, 1]，并登记进前景层
        win.play(Wait(0.8))   #停 0.8s

        say(cap, "label_vector(v, 'v')")
        self.label_vector(v, "v")   #在向量旁 Write 一个标签；单字符会排成箭头字母 v
        win.play(Wait(0.8))   #停 0.8s

        say(cap, "get_vector_label(v, 'w', at_tip=True, ...)")
        lab = self.get_vector_label(   #只生成标签、不播动画，参数都在这里
            v, "w", at_tip=True, direction="right",
            rotate=False, color=GREEN, label_scale_factor=1.0)
        self.add(lab)   #自己加进场景
        win.play(Wait(0.8))   #停 0.8s 收工
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：先加一个 `[2, 1]` 黄色向量，然后三步标注依次登场 —— ① `write_vector_coordinates(v)` 在向量旁写出列矩阵 `★[2, 1]`；② `label_vector(v, "v")` 用 `Write` 在向量旁写标签，单字符 `v` 被排成带箭头的字母形式；③ `get_vector_label(v, "w", at_tip=True, ...)` 只生成一个绿色 `w` 放到箭头尖端，手动 `self.add` 才出现。三个标注最终同屏共存。

<video src="assets/RTM output/04-向量场景VectorScene-labels.mp4" controls width="560"></video>

> 提醒：`label_vector` 会播动画（`animate=True` 默认），RTM 里要先 `self.play = win.play`；`get_vector_label` 不播动画，属于"生成器"，别忘了 `self.add`。单字符 `label` 的箭头字母排版是上游排版规则，不是渲染问题。`at_tip=True` 会把标签放到箭头尖端 —— 如果旁边还有矩阵，两者会挨得比较近，想错开就用默认的 `at_tip=False` + `direction="left"`。

### get_basis_vectors / get_basis_vector_labels

```python
def get_basis_vectors(self, i_hat_color: ParsableManimColor | Iterable[ParsableManimColor] = X_COLOR, j_hat_color: ParsableManimColor | Iterable[ParsableManimColor] = Y_COLOR) -> VGroup:
def get_basis_vector_labels(self, **kwargs: Any) -> VGroup:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `i_hat_color` | `ParsableManimColor \| Iterable[...]` | `X_COLOR`（即 `GREEN_C`） | `î` 的颜色；**能填**任意颜色，样例换成标准 `GREEN`（只深一档，画面差别微妙） |
| `j_hat_color` | `ParsableManimColor \| Iterable[...]` | `Y_COLOR`（即 `RED_C`） | `ĵ` 的颜色；样例换成 `RED` |
| `**kwargs` | `Any` | — | 仅 `get_basis_vector_labels`：透传给标签创建 |

> **返回**：两者都返回 `VGroup`（只生成不加场景，`self.add` 自己来）；线宽由构造参数 `basis_vector_stroke_width` 决定。

#### 样例：`get_basis_vectors`改动

同屏先放默认配色（`X_COLOR` / `Y_COLOR`）的基向量 + 标签，再换成 `GREEN` / `RED` 对比。

```python
from real_time_manim import VectorScene, Text, \
    UP, YELLOW, GREEN, RED
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   #瞬间换掉顶部说明文字，不占动画时间
    cap.become(Text(text, font_size=28, color=YELLOW).to_edge(UP))

class BasisDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        cap = Text("", font_size=28, color=YELLOW)   #顶部说明文字（内容后面换）
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(cap)   #放进场景
        plane = self.add_plane(animate=False)   #直接放上网格
        self.plane = plane   #与向量无关，只是摆个背景

        say(cap, "get_basis_vectors() 默认 X_COLOR / Y_COLOR")
        basis = self.get_basis_vectors()   #默认：i_hat 绿（X_COLOR）、j_hat 红（Y_COLOR）
        labels = self.get_basis_vector_labels()   #i_hat / j_hat 的 MathTex 标签
        self.add(basis, labels)   #一起放进场景
        win.play(Wait(0.9))   #停 0.9s

        self.remove(basis, labels)   #收走默认色的基向量
        say(cap, "get_basis_vectors(i_hat_color=GREEN, j_hat_color=RED)")
        basis2 = self.get_basis_vectors(   #换成 manim 标准 GREEN / RED（和默认色不同）
            i_hat_color=GREEN, j_hat_color=RED)
        self.add(basis2, labels)   #标签复用，颜色换了
        win.play(Wait(0.9))   #停 0.9s 收工
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：先 `get_basis_vectors()` 拿默认配色的 `î`/`ĵ`（分别是 `GREEN_C`/`RED_C`）配上 `get_basis_vector_labels()` 的 `MathTex` 标签一起上屏；0.9 秒后收走，换成显式传 `GREEN`/`RED` 的版本（标签复用），再看 0.9 秒。两档颜色只差一档深浅，肉眼对比微妙 —— 想要明显区分就直接传自己的颜色（如 `BLUE`/`ORANGE`）。

<video src="assets/RTM output/04-向量场景VectorScene-basis.mp4" controls width="560"></video>

> 提醒：默认值 `X_COLOR = GREEN_C`、`Y_COLOR = RED_C`，和 `GREEN`/`RED` 只差一档深浅，所以样例前后两段看起来几乎一样 —— 换成对比强的颜色差别才明显。两个方法都只生成不加场景。标签是 `MathTex`（走 RTM 的 Typst 转换通道渲染），线宽只归 `basis_vector_stroke_width` 管。

### vector_to_coords

```python
def vector_to_coords(self, vector: Vector3DLike, integer_labels: bool = True, clean_up: bool = True) -> tuple[Matrix, Line, Line]:
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `vector` | `Vector3DLike` | — | 要分解的坐标，如 `[-1, 2]`、`[1.5, -1]` |
| `integer_labels` | `bool` | `True` | 标签取整显示（`-1` 而不是 `-1.0`）；**能填** `False` 看小数标签 |
| `clean_up` | `bool` | `True` | 动画结束后恢复场景原状（分解线、矩阵自动退场） |

> **返回**：`(矩阵, x 线, y 线)` 三元组（方法内部自己播动画，RTM 里要先 `self.play = win.play`；这段方法没有 `run_time` 可传，节奏固定，单次约 6 秒）。

#### 样例：`vector_to_coords`改动

同一场景连做两次分解：整数向量 `[-1, 2]`（`integer_labels=True`）和小数向量 `[1.5, -1]`（`integer_labels=False`）。

```python
from real_time_manim import VectorScene, Text, \
    UP, YELLOW
from real_time_manim.vulkan_bind import MLWindow, Wait

def say(cap, text):   #瞬间换掉顶部说明文字，不占动画时间
    cap.become(Text(text, font_size=28, color=YELLOW).to_edge(UP))

class CoordsDemo(VectorScene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        self.play = win.play   #vector_to_coords 内部会调 self.play，先接到窗口上
        cap = Text("", font_size=28, color=YELLOW)   #顶部说明文字（内容后面换）
        cap.to_edge(UP)   #标题挪到画面顶端
        self.add(cap)   #放进场景
        plane = self.add_plane(animate=False)   #直接放上网格
        self.plane = plane   #与向量无关，只是摆个背景

        say(cap, "vector_to_coords([-1, 2], integer_labels=True)")
        self.vector_to_coords([-1, 2], integer_labels=True, clean_up=True)   #向量->坐标的分解动画，结束恢复原状
        win.play(Wait(0.5))   #停 0.5s

        say(cap, "vector_to_coords([1.5, -1], integer_labels=False)")
        self.vector_to_coords([1.5, -1], integer_labels=False, clean_up=True)   #小数就显示小数标签
        win.play(Wait(0.5))   #停 0.5s 收工
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：第一次把 `[-1, 2]` 分解 —— 白色向量长出来，接着画出绿色的 x 分量线（标 `-1`）和红色的 y 分量线（标 `2`），再写出列矩阵 `[-1, 2]`，`clean_up=True` 让这一切自动退场；第二次换成小数向量 `[1.5, -1]` 并把 `integer_labels` 关掉，标签就显示 `1.5`、`-1.0`（而不是四舍五入的 `2`、`-1`）。两次演示的就是同一套分解动画在两种标签规则下的样子。

<video src="assets/RTM output/04-向量场景VectorScene-coords.mp4" controls width="560"></video>

> 提醒：`vector_to_coords` 内部连播两个动画、**没有 `run_time` 参数**（签名固定），单次约 6 秒，整条视频 13 秒就是这么来的。`clean_up=True` 会在结束时把分解线和矩阵收掉，想留住过程就传 `False`。反方向的 `coords_to_vector`（坐标矩阵 → 向量）在上游 `manim` 0.21 里有 bug，见下一节。

### lock_in_faded_grid / coords_to_vector / show_ghost_movement

```python
def lock_in_faded_grid(self, dimness: float = 0.7, axes_dimness: float = 0.5) -> None:
def coords_to_vector(self, vector: Vector2DLike, coords_start: Point3DLike = 2 * RIGHT + 2 * UP, clean_up: bool = True) -> None:
def show_ghost_movement(self, vector: Arrow | Vector2DLike | Vector3DLike) -> None:
```

三个方法在上游 `manim` 0.21 里自身带 bug，**纯命令行渲染同样崩溃**，不是 RTM 的问题，所以不配视频：

| 方法 | 上游问题 | 状态 |
| --- | --- | --- |
| `lock_in_faded_grid` | 内部调 `renderer.update_frame()` 缺 `scene` 参数，源码里就挂着 TODO 注释 | 不可用 |
| `coords_to_vector` | `Matrix(vector)` 报 `TypeError: 'numpy.float64' object is not iterable` | 不可用 |
| `show_ghost_movement` | 构造 `VMobject(*Dots)` 报 `ValueError`（0.20.1 里则是 `Dot object has no attribute 'hex'`） | 不可用 |

如果只是想要"淡网格"效果，用 `add_plane(animate=False)` 后手动 `plane.set_opacity(0.3)` 之类的方式代替；"平移幽灵"效果可参考 `apply_*` 动画的路径弧线思路（见 [线性变换场景](05-线性变换场景.md)）。

---

相关：[线性变换场景](05-线性变换场景.md)、[ThreeDScene](02-ThreeDScene.md)、[Scene 基础](../场景/01-Scene基础.md)
