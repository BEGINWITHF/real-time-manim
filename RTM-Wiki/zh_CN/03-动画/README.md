# 03-动画

ManimCE 动画类逐个说明：公共参数、创建擦除、淡入淡出、变换、强调、生长、移动旋转、编排、文字数字。

[首页](../README.md) ｜ [功能状态总览](../99-功能状态总览.md)

> **2026-10-17 更新 · 导入口径**：RTM **自有 39 个动画类**在 `real_time_manim.animations` / `real_time_manim.vulkan_bind`；
> 顶层 `from real_time_manim import Create/FadeIn/Wait/...` 拿到的是**内置 ManimCE 0.21 版**（顶层 = `from manim import *`）。
> 两版同名同参、绝大多数场景行为一致，各页参数表按 **RTM 自有版**写并在页内注明差异；`Wait` 务必从
> `real_time_manim.vulkan_bind` 导入。各页 demo 的具体导入方式见各子目录 README。
>
> **成片时效（总注）**：本章成片原渲于 **10-15 及 10-16 上午**，早于引擎 10-16 下午的一批改动
> （`timeline.py` 13:32、`base.py` 13:16、`play.py` 14:19、`patches.py` 14:30、`animation_group.py` 15:22、
> `rotate.py`/`rotating.py` 19:33/19:39）。这些改动以**语义对齐 / 补形参 / 修崩溃**为主，样例用法未变；
> **2026-10-17 已把本章比 `RTM output/` 更新的 `final/` 片段统一重发布**（含 10-16/10-17 的引擎修复），
> 本章现无"修复前渲染"的成片——`tools/wiki_sweep.py` 全章 `frames>4.0` 均为 0。个别页面仍保留时效标注（
> [移动与旋转](移动与旋转/README.md)、[组合编排](组合编排/README.md)、[变换/05](变换/05-淡出淡入式变换.md)），
> 其余页面不再逐条标注。

## 通用

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01-生命周期与公共参数](通用/01-生命周期与公共参数.md) | 动画的生命周期与公共构造参数 | 已支持 |
| [02-play与wait参数](通用/02-play与wait参数.md) | Scene.play / wait / pause / wait_until 参数 | 已支持 |
| [03-animate语法](通用/03-animate语法.md) | .animate 语法与 generate_target() / MoveToTarget | 已支持 |

## 创建与擦除

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01-Create与画线族](创建与擦除/01-Create与画线族.md) | Create 与画线族：Create / Write / DrawBorderThenFill / ShowPartial | 已支持 |
| [02-反向擦除](创建与擦除/02-反向擦除.md) | 反向擦除：Uncreate / Unwrite / Add | 已支持 |
| [03-逐个显示与集合](创建与擦除/03-逐个显示与集合.md) | 逐个显示子对象：ShowIncreasingSubsets / ShowSubmobjectsOneByOne / SpiralIn | 已支持 |

## 淡入淡出

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01-Fade家族](淡入淡出/01-Fade家族.md) | Fade 家族：FadeIn / FadeOut | 已支持 |

## 变换

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01-Transform核心](变换/01-Transform核心.md) | Transform 核心：把 A 变成 B | 全部已支持（`Transform`、`ReplacementTr… |
| [02b-更多函数驱动](变换/02b-更多函数驱动.md) | 更多函数驱动的变换（中心 / 复变 / 矩阵） | 已支持（`ApplyPointwiseFunctionToCe… |
| [02-方法与函数驱动](变换/02-方法与函数驱动.md) | 用方法 / 函数驱动的变换 | 已支持（`ApplyMethod`、`ApplyFunctio… |
| [03b-收缩与变色](变换/03b-收缩与变色.md) | 就地改样式：ShrinkToCenter / FadeToColor | 已支持（`ShrinkToCenter`、`FadeToCol… |
| [03-状态保存与样式变换](变换/03-状态保存与样式变换.md) | 状态保存 / 就地改样式（Restore、ScaleInPlace） | 已支持（`Restore`、`ScaleInPlace`） |
| [04-位置互换与复制式变换](变换/04-位置互换与复制式变换.md) | 位置互换 / 复制式变换 | 已支持（`TransformFromCopy`、`Clockw… |
| [05-淡出淡入式变换](变换/05-淡出淡入式变换.md) | 淡出—淡入式变换 | 已支持（`FadeTransform`、`FadeTransformPieces` 构造器 `run_time=` 自 10-16 起已接线、`TransformAnimations` 走原生版） |

## 强调与提示

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01b-扫光与波纹](强调与提示/01b-扫光与波纹.md) | 扫光与波纹（ShowPassingFlash、ApplyWave） | 已渲染验证（`ShowPassingFlash` 非 `ShowPartial` 子类、`remover` 可显式传；`ApplyWave` 非 `Homotopy` 子类、无 `apply_function_kwargs`） |
| [01-强调与闪烁](强调与提示/01-强调与闪烁.md) | 强调与闪烁（Indicate、Flash、Blink） | 已渲染验证（`Indicate(Animation)` 构造器 `run_time` 被丢弃；`Blink(Succession)` 的 `run_time` 由 `time_on×blinks` 算出） |
| [02-圈注与聚焦](强调与提示/02-圈注与聚焦.md) | 圈注与聚焦（Circumscribe、FocusOn、Wiggle） | 已渲染验证（`Circumscribe` 的 `time_width` 已接入、非 Rectangle 一律按 Circle 处理不报错；`FocusOn`、`Wiggle` 全参数渲染） |

## 生长出现

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01b-箭头与旋入](生长出现/01b-箭头与旋入.md) | 生长出现：GrowArrow / SpinInFromNothing | 全部已支持（`GrowArrow`、`SpinInFromNot… |
| [01-Grow家族](生长出现/01-Grow家族.md) | 生长出现：Grow 家族（从点 / 中心 / 边） | 全部已支持（`GrowFromPoint`、`GrowFromC… |

## 移动与旋转

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01-旋转](移动与旋转/01-旋转.md) | 旋转动画：Rotate 与 Rotating | 已支持（RTM 自有 `Rotate(Animation)` / `Rotating(Animation)`，非 `Transform` 子类；显式轴心/非 z 轴逐帧烘焙真实旋转） |
| [02b-同态变换其余类](移动与旋转/02b-同态变换其余类.md) | 同态变换其余类：Smoothed / Complex / PhaseFlow | 已支持（`SmoothedVectorizedHomotopy… |
| [02-沿路径与同态变换](移动与旋转/02-沿路径与同态变换.md) | 沿路径移动与同态变换（MoveAlongPath / Homotopy） | 已支持（`MoveAlongPath`、`Homotopy`） |
| [03-特殊出场](移动与旋转/03-特殊出场.md) | 特殊出场：Broadcast | 已支持（`Broadcast` 经 RTM 时间轴渲… |

## 组合编排

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01-AnimationGroup与错峰](组合编排/01-AnimationGroup与错峰.md) | AnimationGroup 与错峰：LaggedStart / LaggedStartMap | 已支持（`AnimationGroup`、`LaggedStart` / `LaggedStartMap`） |
| [02-Succession顺序播放](组合编排/02-Succession顺序播放.md) | Succession：顺序播放 | 已支持（`Succession`） |

## 匹配变换

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01-匹配变换](匹配变换/01-匹配变换.md) | 匹配变换：TransformMatchingShapes / Tex | 已支持（`TransformMatchingShapes`、`T… |

## 文字与数字

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01b-带光标打字](文字与数字/01b-带光标打字.md) | 带光标打字：TypeWithCursor / UntypeWithCursor | 已支持（RTM 自有 `TypeWithCursor(ShowIncreasingSubsets)`；`UntypeWithCursor` 为独立 `Animation` 实现、`cursor` 必填） |
| [01-逐字出现与消失](文字与数字/01-逐字出现与消失.md) | 逐字出现与消失：AddTextLetterByLetter 等 | 已支持（`AddTextLetterByLetter` / `RemoveTextLetterByLetter`；`AddTextWordByWord` 为上游坏实现、不建议用，见页内说明） |
| [02-数字动画](文字与数字/02-数字动画.md) | 数字动画：ChangingDecimal / ChangeDecimalToValue | 已支持（`ChangingDecimal`、`ChangeDec… |

## 等待与变速

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01-等待速率与变速](等待与变速/01-等待速率与变速.md) | 等待、速率与变速：Wait / ChangeSpeed / Animation | 已支持（`Wait` 自有实现、`ChangeSpeed` 经 `window/patches.py` 桥接、裸 `Animation` 占位；`stop_condition`/`frozen_frame` 已接线） |

## 更新器动画

| 页面 | 内容 | 状态 |
| --- | --- | --- |
| [01b-更新工具与自动变化](更新器动画/01b-更新工具与自动变化.md) | 更新工具与自动变化对象：12.1 + changing.py | 已支持（12.1 工具函数、`TracedPath`、`AnimatedBoundary`；`override_animation` 已接线） |
| [01-更新器动画与自动变化](更新器动画/01-更新器动画与自动变化.md) | 更新器动画与更新工具：UpdateFromFunc 等 | 已支持（`UpdateFromFunc` 等更新器动画） |

