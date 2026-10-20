# 淡入淡出

`FadeIn` / `FadeOut` —— 最常用的进入与消失动画（`shift` / `target_position` / `scale` 组合位移、缩放与透明度）。

[03-动画](../README.md) ｜ [首页](../../README.md) ｜ [功能状态总览](../../99-功能状态总览.md)

- [01-Fade家族](01-Fade家族.md)

## 每页样例视频与源码

### [01-Fade家族](01-Fade家族.md)

小节 = 样例 = 视频（页面里嵌的就是这三条）：

| 样例 | 内容 | 视频 | 帧数 |
| --- | --- | --- | --- |
| `fadein` | `shift` 从下进 / `scale=0.5` 半大长回 / `target_position=ORIGIN` 从心飘来 | [assets/RTM output/01-Fade家族-fadein.mp4](assets/RTM output/01-Fade家族-fadein.mp4) | 156 |
| `fadeout` | `shift=UP` 飘走 / `scale=0.3 + target_position` 缩淡向心 / 标签就地换行 | [assets/RTM output/01-Fade家族-fadeout.mp4](assets/RTM output/01-Fade家族-fadeout.mp4) | 174 |
| `swap` | `AnimationGroup(FadeOut, FadeIn)` 手册换页组合 | [assets/RTM output/01-Fade家族-swap.mp4](assets/RTM output/01-Fade家族-swap.mp4) | 216 |

- 专属 demo：[assets/RTM code/01-Fade家族.py](assets/RTM code/01-Fade家族.py)（页面里的代码块与它逐字一致）
- CE 对照：[assets/ManimCE code/01-Fade家族-manimce.py](assets/ManimCE code/01-Fade家族-manimce.py) → 同名 `-manimce.mp4` 三条，帧数 156 / 174 / 216 全对齐，抽帧目检逐帧同貌

## CE 对照说明

出片（在 `assets\ManimCE code` 下，内部走 manim CLI `-qh`，自动 concat 出片）：

```powershell
cd "assets\ManimCE code"
python 01-Fade家族-manimce.py            # 全部
python 01-Fade家族-manimce.py swap       # 只跑指定片段
```

对照结论：

- 三对视频帧数全对齐、内容同貌（PSNR 平均 36~39dB，差异仅描边抗锯齿量级），详见 [assets/README.md](assets/README.md)。
- **换页组合的 `AnimationGroup` 两个版本**（页面提醒的实测依据）：
  - 从 `real_time_manim` 顶层导入（= 自带 ManimCE 原生版）：两引擎一致，换下换上同时发生——页面样例用的是这版；
  - 从 `real_time_manim.vulkan_bind` 导入（RTM 自带版）：修复前 `FadeIn` 新对象会整段缺席到录像结束，只剩 `FadeOut` 半边；**2026-10-16 已修复**（`AnimationGroup` 新增递归 `mobjects` 属性 + `_setup_scene` 钩子，真实窗口端到端复测 opacity 0→1 正常，测试 `tests/test_gap_composition.py`），现两版均可；复现脚本 [assets/RTM code/_test_swap_vtk.py](assets/RTM code/_test_swap_vtk.py) 记录的是修复前状态。
