# ValueTracker：可动画的数值

`ValueTracker` 是一个**不可见**的「数值容器」，把数值编码在顶点坐标里，因此能被 `.animate` 动画、被 updater 读取。

它是把参数变化接进动画的枢纽。

## 参数

### ValueTracker 构造

```python
def ValueTracker(value: float = 0, **kwargs: Any) -> None
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `value` | `float` | `0` | 初始值 |
| `**kwargs` | `Any` | — | 透传给 `Mobject.__init__` |

> **返回**：新的 `ValueTracker` 实例。
>
> **用法要点**：用 updater 驱动它时**必须 `self.add(tracker)`**（否则场景不推进它）；播放式改值用 `win.play(tracker.animate.set_value(...))`；也可直接 `tracker += 1.5` 立即改值（无动画）。本身不显示，要画出数值用 `DecimalNumber` + updater 或 `always_redraw`。

### get_value / set_value / increment_value

```python
def get_value() -> float
def set_value(value: float) -> Self
def increment_value(d_value: float) -> Self
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `value` | `float` | — | 目标值（仅 `set_value`） |
| `d_value` | `float` | — | 增量，可为负（仅 `increment_value`） |

> **返回**：`get_value` 返回 `float`，另两个返回自身，可链式调用。读取 / 设置 / 增减当前值。

#### 样例：改值、运算与 `+=` 的坑

顶部读数实时显示 tracker 的值：动画 0→5、动画 -2、`+= 2` 瞬间改值；再打印各种算术运算的结果（全是**新对象**）。

```python
from real_time_manim import Scene, DecimalNumber, ValueTracker, \
    YELLOW, UP
from real_time_manim.vulkan_bind import MLWindow, Wait

class BasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        tracker = ValueTracker(0.0)   #初始值 0
        lbl = DecimalNumber(0, num_decimal_places=2, color=YELLOW).scale(0.8).to_edge(UP, buff=0.5)   #读数标签
        lbl.add_updater(lambda d: d.set_value(round(float(tracker.get_value()), 2)))   #每帧读值显示
        self.add(lbl, tracker)   #tracker 必须进场景才会被驱动
        win.play(tracker.animate.set_value(5.0), run_time=0.8)   #动画式改值：0 → 5
        win.play(tracker.animate.increment_value(-2.0), run_time=0.6)   #动画式增减：-2
        tracker += 2.0   #原地立即改值（+= 原地版本）
        print("after += :", tracker.get_value())   #5.0
        print("(tracker * 3).get_value() =", (tracker * 3).get_value())   #* → 新对象，原对象不变
        print("- / / / // / % / ** =", (tracker - 1).get_value(), (tracker / 2).get_value(), (tracker // 2).get_value(), (tracker % 2).get_value(), (tracker ** 2).get_value())   #各算术运算符 → 新 ValueTracker
        print("bool(tracker) =", bool(tracker))   #bool 等价于 bool(get_value())
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：读数标签每帧 `get_value()` 显示当前值，所以两条动画（0→5、再 -2）在画面上是滚动的数字；随后 `tracker += 2.0` 是**原地**立即改值——数字一帧内从 3.0 跳到 5.0。控制台打印验证算术运算：`tracker * 3`、`tracker - 1`、`/ // % **` 全都返回**新的** `ValueTracker`（原对象还是 5.0），`bool(tracker)` 等价于 `bool(get_value())`。

<video src="assets/RTM output/10-ValueTracker-basic.mp4" controls width="560"></video>

> 提醒：`tracker += 1.5` 与 `tracker = tracker + 1.5` 语义完全不同：前者**原地**修改原对象（挂着的 updater 引用的还是它），后者换成新对象——旧引用继续读旧值，是最常见的「数字不动」事故。
>
> 最常见写法是在时间型 updater 里 `tracker += dt`。

### interpolate

```python
def interpolate(mobject1: Mobject, mobject2: Mobject, alpha: float,
                path_func: PathFuncType = straight_path()) -> Self
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mobject1` / `mobject2` | `Mobject` | — | 起点 / 终点状态（通常是临时的 `ValueTracker`） |
| `alpha` | `float` | — | 0 = 起点，1 = 终点 |
| `path_func` | 可调用 | `straight_path()` | 插值路径 |

> **返回**：自身。覆写了 `Mobject.interpolate`，只对**点数组**做插值（`ValueTracker` 没有颜色概念）。

#### 样例：瞬间取插值态

动画到 4 后，`interpolate(ValueTracker(0), ValueTracker(2), 0.5)` 瞬间把值设为 1.0（0 与 2 的中点）——读数一帧跳变。

```python
from real_time_manim import Scene, DecimalNumber, ValueTracker, \
    YELLOW, UP, straight_path
from real_time_manim.vulkan_bind import MLWindow, Wait

class InterpolateDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        tracker = ValueTracker(0.0)   #数值追踪器
        lbl = DecimalNumber(0, num_decimal_places=2, color=YELLOW).scale(0.8).to_edge(UP, buff=0.5)   #读数标签
        lbl.add_updater(lambda d: d.set_value(round(float(tracker.get_value()), 2)))   #每帧读值显示
        self.add(lbl, tracker)   #进场景
        win.play(tracker.animate.set_value(4.0), run_time=0.6)   #先动画到 4.0
        tracker.interpolate(ValueTracker(0.0), ValueTracker(2.0), 0.5, path_func=straight_path())   #直接取 0 与 2 在 0.5 处的插值（瞬间）
        print("after interpolate =", tracker.get_value())   #1.0
        win.play(Wait(0.5))   #进行 0.5s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：读数先随动画从 0 滚到 4.0。

然后 `interpolate` 用两个临时 `ValueTracker`（0 和 2）在 `alpha=0.5` 处算出中点，**瞬间**把本体的值设为 1.0——数字一帧内从 4.0 跳到 1.0。

这正是 `Transform` 两个 `ValueTracker` 时内部做的事；手动调用适合「直接摆一个中间值」的场合。

<video src="assets/RTM output/10-ValueTracker-interpolate.mp4" controls width="560"></video>

> 提醒：`interpolate` 是瞬间函数，想要连续过渡把 `animate` 交给 `Transform`。
>
> 两个临时对象 `ValueTracker(0)` / `ValueTracker(2)` 造完就扔，只取它们的点数组。

### ComplexValueTracker

```python
def ComplexValueTracker(value: float = 0, **kwargs: Any) -> None
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `value` | `complex` / `float` | `0` | 初始复数值 |

> **返回**：新的 `ComplexValueTracker`。跟踪**复数**参数，值内部存成 `[实部, 虚部, 0]`，可 `dot.move_to(ct.points)` 当几何位置用。覆写 `get_value -> complex`、`set_value(value) -> Self`。
>
> 继承的算术运算符在 0.21 上**实测不可用**（`tracker * 1j` / `tracker + 1` 都抛 `TypeError: float argument must be a string or a real number, not 'complex'`），两引擎一致的上游行为。

#### 样例：复数即坐标

`ComplexValueTracker(-2 + 1j)` 起步，一个蓝点用 updater 直接跟着 `ct.points`；`animate.set_value(3 + 2j)` 让点从 (-2, 1) 平滑走到 (3, 2)。

```python
from real_time_manim import Scene, Dot, ComplexValueTracker, \
    BLUE
from real_time_manim.vulkan_bind import MLWindow, Wait

class ComplexDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        ct = ComplexValueTracker(-2 + 1j)   #复数追踪器：值内部存成 [实部, 虚部, 0]
        cdot = Dot(color=BLUE, radius=0.12)   #蓝点
        cdot.add_updater(lambda x: x.move_to(ct.points))   #点直接跟着内部坐标走
        self.add(cdot, ct)   #进场景
        win.play(ct.animate.set_value(3 + 2j), run_time=1.0)   #动画式改值：点从 (-2, 1) 走到 (3, 2)
        cdot.clear_updaters()   #停掉跟随
        print("ct.get_value() =", ct.get_value())   #3+2j
        #无法演示：ct * 1j / ct + 1 等算术运算
        #    TypeError: float() argument must be a string or a real number, not 'complex'
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：`ComplexValueTracker(-2 + 1j)` 的值以 `[实部, 虚部, 0]` 存在点坐标里，蓝点的 updater 直接 `move_to(ct.points)`——复数就是画面坐标。

`ct.animate.set_value(3 + 2j)` 在 1 秒里把实部从 -2 拖到 3、虚部从 1 拖到 2，蓝点沿直线平滑飞到右上；改值完成后停掉跟随、打印 `ct.get_value()`（`3+2j`）。

<video src="assets/RTM output/10-ValueTracker-complex.mp4" controls width="560"></video>

> 无法演示：`ComplexValueTracker` 的算术运算 `ct * 1j` / `ct + 1` / `ct * 2`——**上游行为**：`TypeError: float argument must be a string or a real number, not 'complex'`（复数标量存进实数点坐标后按 float 取值）。
>
> `set_value` / `get_value` / `.animate` 均正常，本页其余参数均已渲染；需要复数运算请自己拿 `get_value` 算完再 `set_value` 回去。

---

相关：[更新器](08-更新器.md)｜[更新器工具函数](08b-更新器工具函数.md)
