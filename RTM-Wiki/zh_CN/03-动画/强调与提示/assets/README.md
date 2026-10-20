# 强调与提示 样例视频（RTM / ManimCE 对照）

本目录的成片由 `RTM code/` 与 `ManimCE code/` 下的同源脚本渲染：页面只引用
**RTM** 那一版（`RTM output/`），带 `-manimce` 的是同一份类代码用 ManimCE 渲的
对照件（`ManimCE output/`），仅供比对，不进页面。

## 复现

```powershell
# RTM 版（不带参数=渲全部片段并拼接；带参数=只渲指定片段）
python "C:\Users\begin\Desktop\RTM-Wiki\03-动画\强调与提示\assets\RTM code\01-强调与闪烁.py"
python "C:\Users\begin\Desktop\RTM-Wiki\03-动画\强调与提示\assets\RTM code\01b-扫光与波纹.py"
python "C:\Users\begin\Desktop\RTM-Wiki\03-动画\强调与提示\assets\RTM code\02-圈注与聚焦.py"

# ManimCE 对照版（同一个 shim 把 win.play 转成 self.play）
python "C:\Users\begin\Desktop\RTM-Wiki\03-动画\强调与提示\assets\ManimCE code\01-强调与闪烁-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\03-动画\强调与提示\assets\ManimCE code\01b-扫光与波纹-manimce.py"
python "C:\Users\begin\Desktop\RTM-Wiki\03-动画\强调与提示\assets\ManimCE code\02-圈注与聚焦-manimce.py"
```

RTM 只支持 1920×1080@60，脚本里写 `MLWindow(960, 540)` 会被强制纠正并打印一行提示，属正常。
