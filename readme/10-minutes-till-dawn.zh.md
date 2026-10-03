# 10 Minutes Till Dawn

一款俯视角生存射击游戏。怪物从四面八方涌来，而你的角色会**自动攻击**——你唯一的任务就是不断移动、躲开工蚁般的敌群，存活**十分钟**。升级会在波次之间陆续到来；你如何分配它们，决定了你能走多远。

- **在线试玩：** [astrnox.github.io/10-minutes-till-dawn](https://astrnox.github.io/10-minutes-till-dawn/)
- **源码：** [github.com/astrnox/10-minutes-till-dawn](https://github.com/astrnox/10-minutes-till-dawn)

## 玩法说明

你手提灯笼，从一片黑暗战场的底部出发。时钟永远在走——**坚持到十分钟整。**

- 你的武器会**自行开火**，始终瞄准最近的敌人。你不需要瞄准；你要做的是*站位*。
- 用移动按键**移动**，与怪群放风筝、穿过缝隙，避免被包围。
- 你存活得越久，敌人的刷新越快、阵型也越凶险。
- 击杀敌人可获得 XP。升级时你要**挑选一项升级**——额外伤害、更快的射速、更高移速、更多 HP 等等。
- 一旦死亡，本局就结束。撑满十分钟，你就算获胜。

没有瞄准，也没有弹药——纯粹的走位与流派选择。张力来自对怪群密度的掌控：一旦让敌人包围你，哪怕自动攻击也救不了你。

## 操作按键

| 动作 | 按键 |
| --- | --- |
| 移动 | `W` `A` `S` `D` 或方向键 |
| 攻击 | 自动（瞄准最近的敌人） |
| 暂停 | `Esc` / `P` |

## 运行原理

游戏使用 **Unity** 构建并导出为 **WebGL**，因此浏览器会下载 `.wasm` 构建产物并在 `<canvas>` 中运行。

```
index.html                          # Unity 引导 + 缩放逻辑
Build/10MinutesTillDawnWebGL.json    # Unity 构建清单
Build/*.wasm, *.data                # Unity WebGL 负载
js/main.js                          # 页面脚本
icon.png                            # favicon
```

游戏以固定的 **675×1200** 竖屏分辨率渲染，并通过信箱式裁切/缩放适配你的窗口（`onResize` 处理函数保持 9:16 宽高比）。加上 `?pixelated` 可获得清晰的像素艺术效果。

## 本地运行

Unity WebGL 构建必须通过 HTTP 伺服，并带上正确的 MIME 类型（尤其是 `.wasm` 和 `.data`）：

```bash
git clone https://github.com/astrnox/10-minutes-till-dawn.git
cd 10-minutes-till-dawn
python3 -m http.server 8000
# open http://localhost:8000
```

本地游玩只需一个普通的 `python3 -m http.server`；若想要更接近生产环境的配置，可使用 `npx serve` 或 Nginx。

## 技术栈

- **引擎：** Unity（C#）
- **导出：** Unity WebGL（WebAssembly）
- **托管：** GitHub Pages

## 版权声明

- 原作：*10 Minutes Till Dawn*——一款 Unity WebGL 生存射击游戏。原作创作者保留所有权利。
- 本仓库是一个已解除限制的网页构建版本，可在现代浏览器中游玩。
