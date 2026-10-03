# Temple of Boom

经典 Flash 动作游戏 **Temple of Boom** 的免拦截、可在浏览器中直接游玩的版本。探索一座正在崩塌的神庙，在平台之间精准把握跳跃时机，一路突破陷阱与守卫。

在浏览器中即刻开玩 —— 无需安装，也不需要 Flash。

## 游玩

- **在线演示：** [astrnox.github.io/temple-of-boom](https://astrnox.github.io/temple-of-boom/)
- **源码：** [github.com/astrnox/temple-of-boom](https://github.com/astrnox/temple-of-boom)

## 玩法说明

你被丢入一座古老神庙的深处，出口就在最上方。

- 用键盘**移动**，用跳跃键**起跳**。
- 准确地落在平台上 —— 一次时机不对的跳跃就会让你回到原来的边缘。
- 一路向上，躲开陷阱并击败神庙的守卫。
- 爬得越高，节奏就越快。这里没有存档点：一次失误就意味着损失一条命。

沿途收集金币与强化道具来延长你的旅程。随着高度上升，游戏会逐渐变难，所以每次奔跑终有终点 —— 目标就是刷新自己的最佳成绩。

## 操作按键

| 动作 | 按键 |
| --- | --- |
| 左右移动 | `←` `→` 或 `A` / `D` |
| 跳跃 | `↑` / `W` / `Space` |
| 交互 | `E` / `Enter` |

> 操作方式沿用原版 Flash 发行物的标准键盘布局；如果你不确定，游戏内会显示相应的提示。

## 运行原理

这是一款通过 [Ruffle](https://ruffle.rs) —— 用 Rust 编写的开源 Flash Player 模拟器 —— 运行的 **Adobe Flash（ActionScript）游戏**。页面会启动 Ruffle 运行时，并嵌入编译好的 `TempleBoom` SWF。

```
index.html                              # boots Ruffle, embeds the SWF
TempleBoom_CustomPreloader_ForColin.js   # Ruffle (Lime) player bootstrap
*.swf                                    # the compiled game itself
adSense.js                              # ad script stub
```

原游戏的画布分辨率为 **624×400**，会等比缩放以适配你的浏览器窗口。

## 本地运行

由于页面需要加载 Flash 运行时和资源，请通过 HTTP 提供服务（用 `file://` 直接打开 `index.html` 会被浏览器拦截）：

```bash
git clone https://github.com/astrnox/temple-of-boom.git
cd temple-of-boom
python3 -m http.server 8000
# open http://localhost:8000
```

任何静态文件服务器都可以（`npx serve`、`php -S` 等）。

## 技术栈

- **游戏：** Adobe Flash / ActionScript（`.swf`）
- **运行时：** [Ruffle](https://ruffle.rs) —— 开源的 Flash Player 模拟器
- **引导方式：** 纯 HTML + 单个嵌入脚本
- **托管：** GitHub Pages

## 致谢

- 原版游戏：*Temple of Boom*（Flash） —— 所有权利归原作者所有。
- 本仓库是一个由 Ruffle 驱动、免拦截的网页版本，可在现代浏览器中游玩。
