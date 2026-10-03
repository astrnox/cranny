# Arkadium's Bubble Shooter

经典 **bubble shooter**（泡泡射手），已解除限制，可在任意现代浏览器中游玩。瞄准、发射，匹配**三个或更多**同色泡泡即可将其消除。在泡泡被压到底部底线之前清空棋盘上的所有泡泡——否则你就输了。

- **在线试玩：** [astrnox.github.io/arkadiumx27s-bubble-shooter](https://astrnox.github.io/arkadiumx27s-bubble-shooter/)
- **源码：** [github.com/astrnox/arkadiumx27s-bubble-shooter](https://github.com/astrnox/arkadiumx27s-bubble-shooter)

## 玩法说明

泡泡从顶部以紧密的六边形排列向下漂移。你控制位于底部的发射器。

- 用鼠标**瞄准**——瞄准线会显示下一颗泡泡的飞行轨迹（它会从墙壁上反弹）。
- **点击 / 轻触**以从炮口发射泡泡。
- 泡泡接触后会**粘附**在泡泡群上。匹配**3 个以上同色**泡泡即可消除，其上方的一切都会落下。
- 每一发没有命中的射击都会让整堆泡泡**下移一排**。任何一颗泡泡越过底线，游戏就结束。
- 清空整个棋盘即可进入下一关——后续关卡会加入更多颜色和更紧凑的布局，因此失误的代价更高。

张力在于落点选择：看起来显而易见的那一枪未必安全，一次糟糕的反弹可能引发你并不想要的连锁反应。

## 操作按键

| 动作 | 操作方式 |
| --- | --- |
| 瞄准 | 移动鼠标 / 拖动手指 |
| 射击 | 点击 / 轻触 |

## 运行原理

这是 Arkadium's Bubble Shooter 的 **HTML5/JavaScript** 构建版本（即发布在 CrazyGames 上的那一版），以单个编译后的 bundle 加载。

```
index.html      # 页面外壳，加载游戏 bundle
build/main.js   # 游戏引擎 + 游戏代码（带内容哈希）
adSense.js      # 广告脚本桩
```

canvas 铺满整个页面并可缩放到任意窗口尺寸；同时支持鼠标和触屏操作。

## 本地运行

通过 HTTP 伺服（打包后的脚本无法从 `file://` 加载）：

```bash
git clone https://github.com/astrnox/arkadiumx27s-bubble-shooter.git
cd arkadiumx27s-bubble-shooter
python3 -m http.server 8000
# open http://localhost:8000
```

## 技术栈

- **语言：** JavaScript（HTML5 构建）
- **渲染器：** HTML5 `<canvas>`
- **托管：** GitHub Pages

## 版权声明

- 原作：*Arkadium's Bubble Shooter*，发布于 [CrazyGames](https://www.crazygames.com/)。Arkadium / CrazyGames 保留所有权利。
- 本仓库是一个已解除限制的网页构建版本，可在现代浏览器中游玩。
