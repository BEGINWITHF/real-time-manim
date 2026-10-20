# .animate 动画语法

把「对对象调用的任意方法」转换成过渡动画，是实时预览里最常用的写法。

## 参数

### .animate（属性）

```python
def animate(**play_kwargs) -> _AnimationBuilder
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `**play_kwargs` | `Any` | — | 紧跟 `.animate(...)` 的关键字**不是 `Scene.play` 的形参**，而是构建完动画后 `setattr` 到动画对象上（`run_time=`、`rate_func=`、`lag_ratio=`…）；**必须紧跟在 `.animate` 之后、方法调用之前** |

> **返回**：`_AnimationBuilder`，最终由 `Scene.play` 转成动画。`mob.set_fill(RED)` 是瞬间改，`mob.animate.set_fill(RED)` 是播放过渡动画；多个方法可以链起来合成**一个**动画。

**三条常见坑**

1. 同一个对象在一次 `play` 里只能出现一次：写 `m.animate.shift(RIGHT).rotate(PI)`，不要分成两个动画。
2. `.animate` 是**点之间线性插值**，不是路径动画；要沿路径或按角度连续旋转请用 `MoveAlongPath` / `Rotate` / `Rotating`。
3. 要配合 `ValueTracker` 的连续变化，请用 updater 而不是 `.animate`。

#### 样例：平移、链式、play 参数与 `set`

红方块普通平移、链式「放大+旋转」两步合一，再用 `animate(run_time=..., rate_func=there_and_back)` 传 play 参数；橙矩形演示 `set` 配合 `animate`。

```python
from real_time_manim import Scene, Square, Rectangle, \
    RED, ORANGE, DOWN, LEFT, RIGHT, PI, FadeIn
from real_time_manim.vulkan_bind import MLWindow, Wait

class AnimateBasicDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        s = Square(color=RED, side_length=1.2, fill_opacity=0.6).shift(LEFT * 3.5)   #红色方块
        self.add(s)   #进场景
        win.play(s.animate.shift(RIGHT * 1.6), run_time=0.5)   #最普通的 “.animate”：平移
        win.play(s.animate.scale(1.5).rotate(PI / 6), run_time=0.6)   #链式：一个动画两步
        win.play(s.animate(run_time=0.8, rate_func=there_and_back).shift(DOWN), run_time=0.8)   #play 参数紧跟 “.animate”
        rect = Rectangle(width=2.0, height=1.0, color=ORANGE, fill_opacity=0.6).shift(RIGHT * 3.5)   #橙色矩形
        self.add(rect)   #进场景
        win.play(rect.animate.set(width=5.0), run_time=0.5)   #set 配合 animate：按目标尺寸调
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：红方块走三步——`animate.shift` 最普通的用法平移；`animate.scale(1.5).rotate(PI / 6)` 把放大和旋转**链在一起**、由一个动画平滑完成（分成两次 play 会先转再放大，观感完全不同）；第三步 `animate(run_time=0.8, rate_func=there_and_back).shift(DOWN)` 在 `.animate` 后紧跟 play 参数——方块下去又回到原位。右边橙矩形演示 `rect.animate.set(width=5.0)`：按**目标尺寸**调（而不是倍数）的过渡动画。

<video src="assets/RTM output/07-animate语法-animate.mp4" controls width="560"></video>

> 提醒：`.animate(...)` 的括号参数**只认** `setattr` 到动画对象上有效的属性（`run_time` / `rate_func` / `lag_ratio` / `reverse_rate_function`…），写在方法参数的位置就变成了方法参数——`animate.shift(2)` 和 `animate(run_time=2)` 完全两回事。被链起来的方法按顺序执行，`run_time` 是**整条链**的总时长。`lag_ratio=0.3` 传在**没有子对象**的对象上无效，RTM 现在会打 `UserWarning` 显式提示而非静默。

### override_animate（模块级装饰器）

```python
def override_animate(method: types.MethodType) -> Callable[[types.MethodType], types.MethodType]
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `method` | 未绑定方法 | — | 被覆盖的那个方法（定义在 `Mobject` 子类上） |

> **返回**：装饰器。给自定义方法指定「用 `.animate` 调用时应播放哪个动画」：被装饰的方法返回一个 `Animation`，`.animate.method(...)` 就会播放它而不是「直接执行再插值」。**限制**：被覆盖的方法**不能**和其他方法链式出现在同一个 `.animate` 里。

#### 样例：普通调用 vs `.animate` 调用

`PulseSquare` 定义普通方法 `pulse`（直接放大、瞬时），并用 `@override_animate(pulse)` 给它配一个 `Transform` 动画——左块直接调用瞬间变大，右块 `.animate` 调用平滑变大。

```python
from real_time_manim import Scene, Square, \
    PURPLE, LEFT, RIGHT, Transform, override_animate
from real_time_manim.vulkan_bind import MLWindow, Wait

class PulseSquare(Square):   #自定义子类：给普通方法配专用动画
    def pulse(self, scale_factor):   #普通调用：直接放大（瞬时）
        self.scale(scale_factor)

    @override_animate(pulse)   #给 “pulse” 指定 “.animate” 调用时该播的动画
    def _pulse_animation(self, scale_factor, anim_args=None):   #参数与原方法一致，外加 anim_args
        if anim_args is None:
            anim_args = {}
        target = self.copy().scale(scale_factor)   #目标形态
        return Transform(self, target, **anim_args)   #返回动画：平滑变形过去


class OverrideDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        ds = PulseSquare(color=PURPLE, side_length=1.2, fill_opacity=0.6).shift(LEFT * 3.5)   #左边：直接调用
        ds2 = PulseSquare(color=PURPLE, side_length=1.2, fill_opacity=0.6).shift(RIGHT * 3.5)   #右边：animate 调用
        self.add(ds, ds2)   #进场景
        ds.pulse(1.4)   #直接调用 → 走普通方法（瞬间变大）
        win.play(Wait(0.5))   #看清瞬间变化
        win.play(ds2.animate.pulse(1.4), run_time=0.6)   #“.animate” 调用 → 被替换成返回的动画（平滑）
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：`PulseSquare.pulse(1.4)` 平时就是「直接 `scale` 一下」——左块直接调用，一帧之内变大；同一个类上 `@override_animate(pulse)` 装饰的方法定义了「`.animate` 调用时该播什么」：右块 `ds2.animate.pulse(1.4)` 触发它，它返回一个 `Transform`（放大后快照），于是右块**平滑地**变大。同一个方法、两种调用方式、两种行为——这就是 override 的意义。

<video src="assets/RTM output/07-animate语法-override.mp4" controls width="560"></video>

> 提醒：装饰器方法（下划线开头的 `_xxx_animation`）的签名 = 原方法参数 + `anim_args`（`.animate(...)` 括号里的 play 参数）；返回值必须是 `Animation`。被覆盖的方法**不能**与其它方法混在同一条 `.animate` 链上（会报错/绕过覆盖）。直接调用永远走原始实现，想两种行为都留着就靠这个装饰器区分。

### add_animation_override / animation_override_for（类方法）

```python
def add_animation_override(animation_class: type[Animation],
                           override_func: FunctionOverride) -> None
def animation_override_for(animation_class: type[Animation]) -> FunctionOverride | None
```

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `animation_class` | `type[Animation]` | — | 被替换的动画类，如 `FadeIn` |
| `override_func` | 可调用 | — | 返回新动画的函数，接收构造参数 |

> **返回**：前者 `None`，后者注册的函数或 `None`。以编程方式注册/查询「某动画类对该子类的替换实现」，等价于 `@override_animate` 的底层。**只作用于当前类**（不应用到子类）；同一动画类重复注册抛 `MultiAnimationOverrideException`。

#### 样例：注册 FadeIn → FadeOut

给 `FlashSquare` 注册「`FadeIn` 换成 `FadeOut`」：查表打印注册结果，播放 `FadeIn(sq)` 实际执行的是淡出——可见的方块当场消失。

```python
from real_time_manim import Scene, Square, \
    TEAL, FadeIn, FadeOut, Transform
from real_time_manim.vulkan_bind import MLWindow, Wait

class FlashSquare(Square):   #只是挂注册表的载体类
    pass


class AddOverrideDemo(Scene):
    def construct(self):
        win = MLWindow(960, 540)   #创建一个 RTM 窗口
        win.scene = self   #将名为 “self” 的 manim 窗口，绑定给名为 “win” 的 RTM 窗口
        FlashSquare.add_animation_override(FadeIn, lambda mobject, **kwargs: FadeOut(mobject))   #注册：FadeIn 换成 FadeOut
        print("override_for(FadeIn) =", FlashSquare.animation_override_for(FadeIn))   #查表：拿到注册的函数
        print("override_for(Transform) =", FlashSquare.animation_override_for(Transform))   #没注册过：None
        sq = FlashSquare(color=TEAL, side_length=1.4, fill_opacity=0.7)   #青色方块
        self.add(sq)   #进场景
        win.play(FadeIn(sq), run_time=0.6)   #写的是 FadeIn，注册表把它换成了 FadeOut（可见对象当场淡出）
        win.play(Wait(0.4))   #进行 0.4s 的等待
        win.close()   #关闭 RTM 窗口
```

这段代码在做什么：先给 `FlashSquare` 类注册一条规则——「这个类遇到 `FadeIn` 就换成返回 `FadeOut` 的函数」；`animation_override_for(FadeIn)` 查表拿回刚注册的函数、`animation_override_for(Transform)` 查不到返回 `None`；然后把一个**已经在画面里**的青色方块用 `win.play(FadeIn(sq))` 播放——注册表生效，实际执行的是 `FadeOut`，方块当场淡出消失。

<video src="assets/RTM output/07-animate语法-add_override.mp4" controls width="560"></video>

> 提醒：注册是**类级别**且**不继承到子类**；重复注册同一个动画类会抛 `MultiAnimationOverrideException`（要改先删旧的）。这个 API 比 `@override_animate` 更底层——它是「按动画类」替换，`@override_animate` 是「按方法」替换，日常自定义动画优先用后者。

---

相关：[复制派生与状态](06-复制派生与状态.md)｜[更新器动画](09-更新器动画.md)
