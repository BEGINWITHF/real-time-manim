# 低频但公开的其余 API

§收尾的杂项：位图导出、子对象重排、家族批量操作与沿路径取点。可出片的三组都有样例视频；两组**无法出片**的在小节里写清原因，不留空视频位。

## 参数

### get_image / show / save_image —— 无法出片

```python
def get_image(camera: Camera | None = None) -> Image.Image
def show(camera: Camera | None = None) -> None
def save_image(name: str | None = None) -> None
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `camera` | `Camera` 或 `None` | `None` | 自定义相机 |
| `name` | `str` 或 `None` | `None` | 文件名（不含扩展名），缺省用对象名 |

> **返回**：`get_image` 返回 PIL `Image`；`show` 弹出图片查看器；`save_image(name)` 保存到当前 `video_dir` 下的 `name.png`。按文档设计适合调试「这东西到底长什么样」。

**为什么没有视频**：manim 0.21 的实现里这三个方法内部引用了**没有导入**的 `Camera`（上游 bug），调用直接抛 `NameError: name 'Camera' is not defined`——RTM 与原版引擎实测**一致地崩**，无画面可渲，因此本小节不贴视频。

绕法：想要位图请直接用渲染管线的输出（RTM 录屏帧 / `manim` 的 `-s` 存帧），或自己拿点数组画。

```python
from real_time_manim import Square
Square().get_image()   #NameError: name 'Camera' is not defined（两引擎一致）
```

### sort / shuffle / invert

```python
def sort(point_to_num_func: Callable[[Point3DLike], float] = lambda p: p[0],
         submob_func: Callable[[Mobject], Any] | None = None) -> Self
def shuffle(recursive: bool = False) -> Self
def invert(recursive: bool = False) -> Self
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `point_to_num_func` | 可调用 | `lambda p: p[0]` | 由点算排序键（`sort`） |
| `submob_func` | 可调用或 `None` | `None` | 直接由子对象算排序键，**优先级更高** |
| `recursive` | `bool` | `False` | 是否递归到子对象 |

> **返回**：自身。重排 `submobjects` 列表顺序，直接影响叠放次序与 `arrange` 的次序：`sort` 默认按中心 x 排序，`shuffle` 随机打乱，`invert` 反转顺序。

#### 样例：顺序四连变

五个散乱的彩色方块：`sort`（按位置排序）→ `invert`（反转）→ 固定种子 `shuffle`（随机）→ `sort(submob_func=...)`（按颜色名排序），每步后 `arrange` 展示新顺序。

```python
import random

from real_time_manim import Scene, VGroup, Square, \
    RED, BLUE, GREEN, YELLOW, PURPLE, UP, RIGHT
from real_time_manim.vulkan_bind import MLWindow, Wait

class SortShuffleInvertDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        colors = (RED, BLUE, GREEN, YELLOW, PURPLE)   #五个颜色
        spots = (LEFT * 3.5 + UP * 1.4, RIGHT * 2.0 + UP * 0.6, LEFT * 1.0 + DOWN * 1.2, RIGHT * 3.2 + DOWN * 1.6, LEFT * 2.4)   #五个互不相同的散乱位置
        v = VGroup(*[Square(color=c, side_length=0.8).shift(p) for c, p in zip(colors, spots)])   #先散乱摆放
        self.add(v)   #进场景
        win.play(Wait(0.4))   #看清初始散乱位置
        v.sort()   #sort：按当前中心 x 从左到右改列表顺序
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   #按列表顺序排成一行：颜色按位置排好
        v.invert(recursive=False)   #invert：反转列表顺序
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   #顺序整个反过来
        random.seed(7)   #固定随机种子，便于复现
        v.shuffle(recursive=False)   #shuffle：随机打乱
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   #随机顺序
        v.sort(submob_func=lambda m: str(m.color))   #submob_func 优先级更高：按颜色名排序
        win.play(v.animate.arrange(RIGHT, buff=0.3), run_time=0.5)   #颜色名从 A 到 Z
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：五个彩色方块先散乱摆在九宫格里，随后列表顺序连变四次。

- `sort()` 按当前**中心 x** 改列表顺序，`arrange` 后颜色从左到右=位置从左到右。
- `invert()` 把列表整个倒过来，重排后顺序镜像。
- `shuffle()` 随机打乱（样例先 `random.seed(7)` 固定随机序列，两引擎/两次运行才一致）。
- 最后 `sort(submob_func=lambda m: str(m.color))` 用**优先级更高**的子对象键——按颜色名的字母序排成 BLUE→GREEN→PURPLE→RED→YELLOW。

<video src="assets/RTM output/11b-低频其余API-sort_shuffle_invert.mp4" controls width="560"></video>

> 提醒：三个方法改的是**列表顺序**（同时影响叠放和 `arrange`），不动坐标；`shuffle` 不设种子每次结果都不同。
>
> `recursive=True` 会递归处理子对象内部的列表。

### apply_to_family

```python
def apply_to_family(func: Callable[[Mobject], None]) -> Self
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `func` | `Callable[[Mobject], None]` | — | 对每个**有顶点**的后代调用一次 |

> **返回**：自身。对自身及所有有顶点的后代依次调用 `func`，比手写循环方便。

#### 样例：批量改样式

三个方块和两个圆各用一行 `apply_to_family` 批量改描边——比 `for m in ...` 循环少写三行。

```python
from real_time_manim import Scene, VGroup, Group, Square, Circle, \
    BLUE, RED, UP, DOWN, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class ApplyFamilyDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        v = VGroup(*[Square(color=BLUE, side_length=0.9) for _ in range(3)])   #三个方块
        v.arrange(RIGHT, buff=0.3).shift(UP * 1.5)
        self.add(v)   #进场景
        v.apply_to_family(lambda m: m.set_stroke(width=6))   #对每个有顶点的成员调用一次
        win.play(FadeIn(v), run_time=0.4)   #粗描边的方块淡入
        g = Group(Circle(radius=0.45), Circle(radius=0.45)).arrange(RIGHT, buff=0.4).shift(DOWN * 1.5)   #两个圆
        self.add(g)   #进场景
        g.apply_to_family(lambda m: m.set_stroke(color=RED, width=6))   #对圆同样生效
        win.play(FadeIn(g), run_time=0.4)   #红粗描边的圆淡入
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：一排三个方块用 `apply_to_family(lambda m: m.set_stroke(width=6))` 一次性全部加粗描边；下面两个圆同样一行搞定红粗描边。回调**只会发给有顶点的成员**（容器本身不收），等价于 `for m in v.family_members_with_points(): f(m)` 的手写循环。

<video src="assets/RTM output/11b-低频其余API-apply_family.mp4" controls width="560"></video>

> 提醒：回调收到的是家族里**每个有顶点的成员**——包含自身（有顶点时）。它不返回新对象，改的是原地状态。
>
> 想要「每帧批量改」请改用 updater。

### get_start / get_end / get_start_and_end / get_pieces / point_from_proportion / proportion_from_point

```python
def get_start() -> Point3D    def get_end() -> Point3D    def get_start_and_end() -> tuple
def get_pieces(n_pieces: float) -> Group
def point_from_proportion(alpha: float) -> Point3D
def proportion_from_point(point: Point3DLike) -> float
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `n_pieces` | `float` | — | 切成的段数（仅 `get_pieces`） |
| `alpha` | `float` | — | 路径比例 0~1（仅 `point_from_proportion`） |
| `point` | 点 | — | 反算比例的目标点（仅 `proportion_from_point`） |

> **返回**：`get_start` / `get_end` 返回**第一个/最后一个顶点**；`point_from_proportion` / `proportion_from_point` 是「沿曲线取点」的通用入口，**基类抛 `NotImplementedError`**，由 `Line` / `Arc` / `VMobject` 等子类实现；`get_pieces(n)` 把对象切成 n 段的组。前几个无参数方法返回 `np.ndarray` / `tuple`。

#### 样例：沿线取点与切段

直线的首尾顶点、25% 处打红点、`get_pieces(4)` 切四段渐变色；圆上取 25% 点并 `proportion_from_point` 反算回比例（`0.25`）。

```python
from real_time_manim import Scene, Line, Circle, Dot, \
    BLUE, RED, YELLOW, ORANGE, UP, DOWN, LEFT, RIGHT, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class PathDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        line = Line(LEFT * 3.5, RIGHT * 0.5, color=YELLOW).shift(UP * 1.5)   #一段线
        self.add(line)   #进场景
        print("get_start =", line.get_start().round(2))   #第一个顶点
        print("get_end =", line.get_end().round(2))   #最后一个顶点
        p = line.point_from_proportion(0.25)   #沿路径 25% 处
        self.add(Dot(color=RED, radius=0.09).move_to(p))   #打点标出来
        print("point_from_proportion(0.25) =", p.round(2))
        pieces = line.get_pieces(4)   #切成 4 段
        pieces.set_color_by_gradient(RED, BLUE)
        self.add(pieces)   #进场景
        win.play(FadeIn(pieces), run_time=0.5)   #四段渐变色显示
        c = Circle(radius=0.9, color=ORANGE).shift(RIGHT * 3.0 + DOWN * 1.2)   #圆：曲线上的取点更直观
        self.add(c)   #进场景
        q = c.point_from_proportion(0.25)
        print("circle 25% =", q.round(2))
        print("proportion_from_point =", round(c.proportion_from_point(q), 4))   #反算比例
        win.play(FadeIn(c), run_time=0.4)   #圆淡入
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：黄色直线的 `get_start` / `get_end` 打印出首尾顶点坐标；`point_from_proportion(0.25)` 取路径 25% 处并打红点（在线上偏左 1/4 处）；`get_pieces(4)` 把线切成四段、用渐变色染色后淡入——四段颜色各不相同。

右下的圆演示曲线上的取点与**反算**：`point_from_proportion(0.25)` 取一个点，`proportion_from_point(q)` 把比例 `0.25` 精确算回来。

<video src="assets/RTM output/11b-低频其余API-path.mp4" controls width="560"></video>

> 提醒：`get_start` / `get_end` 对无顶点对象（空 `Group`）会抛异常，先 `has_points()` 判一下。
>
> `point_from_proportion` 的实现按**累计弧长**取点，对 `Line` / `Arc` / `Circle` 这类均匀路径直觉正确；`proportion_from_point` 要求点**确实在路径上**（`Circle` 上实测返回0.25，偏一点就 `ValueError: does not lie on this curve`）。

### mobject/utils.py 渲染器基类工厂 —— 无画面

```python
def get_mobject_class() -> type           # 当前渲染器的 Mobject 基类
def get_vectorized_mobject_class() -> type  # VMobject
def get_point_mobject_class() -> type     # PMobject
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| （均无参数） | — | — | 按当前渲染器返回对应基类 |

**为什么没有视频**：这三个函数返回的是**类对象**（`Mobject` / `VMobject` / `PMobject`），本身不产生任何画面，只适合 print。给 Manim 自身代码和插件作者用的，**普通动画脚本不需要也不应该调用**：

```python
from real_time_manim import get_mobject_class, get_vectorized_mobject_class, get_point_mobject_class
print(get_mobject_class(), get_vectorized_mobject_class(), get_point_mobject_class())
#<class 'manim.mobject.mobject.Mobject'> <class '...VMobject'> <class '...PMobject'>
```

---

相关：[测量](03-测量.md)｜[屏幕框架与横幅](11-屏幕框架与横幅.md)
