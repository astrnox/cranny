# Odd Bot Out

一款浏览器上的观察解谜游戏。屏幕上是一整片一模一样的机器人 —— **其中只有一个与众不同。** 找出它，点中它，然后进入下一轮。随着进程推进，网格会变大，差异也会越来越隐蔽。

- **在线演示：** [astrnox.github.io/odd-bot-out](https://astrnox.github.io/odd-bot-out/)
- **源码：** [github.com/astrnox/odd-bot-out](https://github.com/astrnox/odd-bot-out)
- **官方网站：** [oddbotout.com](https://www.oddbotout.com/)

## 玩法说明

每一轮都会显示一片看起来完全相同的机器人网格，只有一个例外。你的任务就是找出那个不属于这里的。

1. **扫视**网格 —— 那个异类通常只在一处细节上有差别：一个颜色、一根天线、一只眼睛、一道标记。
2. **点击**你认为与众不同的那个机器人。
3. 选对即可进入下一轮；选错则损失一条命（或一次重试机会，取决于难度）。
4. 随着关卡推进，网格会变得更大，差异也会变得更难被察觉。

这是一款纯粹锻炼眼神 / 识别规律的游戏 —— 没有计时，没有阅读，只需要仔细观察。

## 运行原理

游戏是**使用 Emscripten 编译为 WebAssembly 的原生代码**，渲染到 HTML5 的 `<canvas>` 中。

```
index.html            # canvas host + loading splash
webapp/index.js       # Emscripten runtime loader
webapp/source_min.js  # compiled game module
webapp/obo.css        # canvas / layout styles
webapp/splash.png     # loading splash
```

首次加载时，一个 `<progress>` 进度条会显示下载／编译进度，之后游戏逐渐淡入。

## 本地运行

请通过 HTTP 提供服务（Emscripten 模块无法从 `file://` 加载）：

```bash
git clone https://github.com/astrnox/odd-bot-out.git
cd odd-bot-out
python3 -m http.server 8000
# open http://localhost:8000
```

## 技术栈

- **游戏：** 原生代码（C/C++），使用 **Emscripten** 编译为 WebAssembly
- **渲染器：** HTML5 `<canvas>`
- **托管：** GitHub Pages

## 致谢

- 原版游戏：*Odd Bot Out* —— [oddbotout.com](https://www.oddbotout.com/)
- 本仓库是一个免拦截的网页版本，可在现代浏览器中游玩。
