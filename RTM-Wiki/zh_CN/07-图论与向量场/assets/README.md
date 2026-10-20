# 07-图论与向量场 样例视频（RTM / ManimCE 对照）

这些视频都由 `RTM code/`（RTM 版）与 `ManimCE code/`（CE 对照版）下的源码渲染，页面只引用 **RTM** 那一版；
带 `-manimce` 的是同一份代码用 ManimCE 渲的，留着自己对比，不进页面。
图与流线在 RTM 里没有专门实现，走通用矢量回退出图（实测可用，见各页标注）。

## 01-Graph与DiGraph

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `layout` | `"circular"` / `"spring"`（seed=7） / `"partite"` 三段拼接 | `01-Graph与DiGraph-layout.mp4`（468 帧 / 7.80s） | `01-Graph与DiGraph-layout-manimce.mp4`（468 帧 / 7.80s） | 对齐 |
| `config` | 公共 + 逐顶点/逐边覆盖（黄点/红点、蓝线/橙线） | `01-Graph与DiGraph-config.mp4`（144 帧 / 2.40s） | `01-Graph与DiGraph-config-manimce.mp4`（144 帧 / 2.40s） | 对齐 |
| `digraph` | 默认箭头尖 / `tip_config` 放大箭头 两段拼接 | `01-Graph与DiGraph-digraph.mp4`（288 帧 / 4.80s） | `01-Graph与DiGraph-digraph-manimce.mp4`（288 帧 / 4.80s） | 对齐 |
| `from_networkx` | `nx.wheel_graph(7)` → `Graph.from_networkx` | `01-Graph与DiGraph-from_networkx.mp4`（156 帧 / 2.60s） | `01-Graph与DiGraph-from_networkx-manimce.mp4`（156 帧 / 2.60s） | 对齐 |

- 四对全部帧数对齐；PSNR avg 35.9~38.3dB（n=60 采样，差异来自 `MathTex` 标签 Typst/LaTeX 字形与描边抗锯齿）。
- `spring` 布局两引擎都写死 `layout_config={"seed": ...}`，否则坐标随机对不上。
- 顶点标签 `labels=True` 在 RTM 走 Typst、CE 走 LaTeX，字形几乎一致，PSNR 未受明显影响。

## 01b-图的增删与布局

| 样例 | 内容 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `getitem` | `g[2]` 挪点（边跟随）→ `g[(1,2)]` 单独加粗变橙 | `01b-图的增删与布局-getitem.mp4`（210 帧 / 3.50s） | `01b-图的增删与布局-getitem-manimce.mp4`（210 帧 / 3.50s） | 对齐 |
| `add` | `g.animate.add_edges((1,4), positions=…)` 连带新点长出 → `add_vertices(5)` 补孤点 → `add_edges((4,5))` 连线 | `01b-图的增删与布局-add.mp4`（234 帧 / 3.90s） | `01b-图的增删与布局-add-manimce.mp4`（234 帧 / 3.90s） | 对齐 |
| `remove` | `g.animate.remove_edges((1,3))` 只删弦 → `remove_vertices(4)` 级联删关联边 | `01b-图的增删与布局-remove.mp4`（192 帧 / 3.20s） | `01b-图的增删与布局-remove-manimce.mp4`（192 帧 / 3.20s） | 对齐 |
| `change_layout` | `circular → spring(seed=7) → 手写坐标字典` 连续 morph | `01b-图的增删与布局-change_layout.mp4`（240 帧 / 4.00s） | `01b-图的增删与布局-change_layout-manimce.mp4`（240 帧 / 4.00s） | 对齐 |

- 四对全部帧数对齐；PSNR avg 34.8~36.8dB（n=60 采样）。
- **2026-10-17 实测**：`add`/`remove`/`change_layout` 的 `.animate` 版由 `_AnimationBuilder` → `override_animate` 生成动画、`win.play` 直接播，**不**回调 `self.play`；样例首行的 `self.play = win.play` 属保险接线（CE 垫片同理，把它转成 `self.play`）。另实测 `remove` 片里没有橙/蓝像素——`add`/`remove`/`change_layout` 三条都没给点和边改色（默认白）；唯一改色的是 `getitem` 里 `set_stroke(ORANGE, 8)` 那条既有边。
- `change_layout` 样例里的 `spring` 写死 `layout_config={"seed": 7}`，否则两引擎坐标对不上。

## 02-向量场与流线

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `field` | 默认渐变配色 / `color=RED`+`length_func=x/3`+`stroke_width:2` 两段拼接 | `02-向量场与流线-field.mp4`（264 帧 / 4.40s） | `02-向量场与流线-field-manimce.mp4`（264 帧 / 4.40s） | 对齐 |
| `nudge` | RK4 单步（橙色位移线）+ `get_nudge_updater` 持续流动 2s | `02-向量场与流线-nudge.mp4`（276 帧 / 4.60s） | `02-向量场与流线-nudge-manimce.mp4`（276 帧 / 4.60s） | 对齐 |
| `submobject` | `start_submobject_movement(1.5)` 漂移 2s + `stop` | `02-向量场与流线-submobject.mp4`（234 帧 / 3.90s） | `02-向量场与流线-submobject-manimce.mp4`（234 帧 / 3.90s） | 对齐 |

- 三对全部帧数对齐；PSNR avg 35.4~37.0dB（n=60 采样）。
- 持续 updater（红点流动、箭头群体漂移）在 RTM 的 `Wait` 里逐帧推进正常，两引擎同貌。
- `ArrowVectorFieldTuned` 是 `ArrowVectorFieldDemo` 的子类（`TUNED = True`），页面里只贴基类一份代码。

## 02b-流线StreamLines

| 样例 | 片段 | RTM | ManimCE | 帧数对齐 |
| --- | --- | --- | --- | --- |
| `create` | `sl.create(run_time=…, lag_ratio=…)` 随机顺序逐条画出 | `02b-流线StreamLines-create.mp4`（168 帧 / 2.80s） | `02b-流线StreamLines-create-manimce.mp4`（168 帧 / 2.80s） | 对齐 |
| `flow` | `start_animation(flow_speed=1.5, time_width=0.5)` 流动 2s → `end_animation()` 收束 | `02b-流线StreamLines-flow.mp4`（252 帧 / 4.20s） | `02b-流线StreamLines-flow-manimce.mp4`（252 帧 / 4.20s） | 对齐 |

- 两对全部帧数对齐；PSNR（480×270、n=60 采样）avg 33.2~37.1dB、最低帧 25.7~26.2dB——差异集中在细流线与光点的抗锯齿（两引擎同一套积分轨迹）。
- 抽帧目检（两片各取第 20/60/120 帧）：标题、签名标签、蓝色流线均正常出画，`flow` 段光点沿线推进，无黑屏/缺字。

## 复现

```powershell
# RTM 版：每页一个脚本，不带参数渲全部并拼出 assets/ 下的样例视频
cd assets\RTM code
python -X utf8 01-Graph与DiGraph.py            # 01b/02/02b 同款：换对应文件名即可
python -X utf8 01b-图的增删与布局.py
python -X utf8 02-向量场与流线.py
python -X utf8 02b-流线StreamLines.py

# 单片段重渲：只渲该片段到 RTM code\final\，不拼接（参数是片段名，见脚本里的 SCENES）
python -X utf8 01-Graph与DiGraph.py graph_config
#   ※ 脚本只在“不带参数”时才 concat —— 想刷新 assets/ 下的样例视频，跑一遍上面的无参数命令即可

# ManimCE 对照版（同一个 manimce_shim 垫片把 win.play 转成 self.play；内部走 "python -m manim render -qh"，
#                  这一步依赖外置 ManimCE 安装——内置副本无 cli/、__main__.py，零依赖下 -m manim 不可用）
cd ..\ManimCE code
python -X utf8 01-Graph与DiGraph-manimce.py          # 全部 + concat 到 assets/
python -X utf8 01-Graph与DiGraph-manimce.py digraph  # 只跑指定样例
python -X utf8 02-向量场与流线-manimce.py
python -X utf8 02b-流线StreamLines-manimce.py
```

RTM 渲染开真窗口占 GPU：多个会话并行时**错峰渲染**（一个会话在渲，其他会话先写代码/写页面）。仓库与脚本里**没有**任何渲染锁实现（`rtm_render.lock` / acquire-release 全仓库无命中），别按有锁去写流程；CE 渲染走 manim 自己的命令行，不占 RTM 的 GPU 路径。

RTM 只支持 1920×1080@60，`MLWindow(960, 540)` 会被强制纠正并打印一行提示，属正常。
