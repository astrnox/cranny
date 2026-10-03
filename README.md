# 游戏中心

> 15 款自建游戏的小集合 —— 网页游戏点开即玩，PC 与安卓游戏提供下载。

**在线地址：<https://astrnox.github.io/gamespace/>**

## 收录的游戏

| 游戏 | 类型 | 接入方式 | 仓库 |
| --- | --- | --- | --- |
| 2048 合集 | 益智 | 跳转 | [astrnox/2048](https://github.com/astrnox/2048) |
| Hextris 六边形俄罗斯方块 | 益智 | 站内直接玩 | [astrnox/hextris](https://github.com/astrnox/hextris) |
| Tower Game 叠塔 | 休闲 | 站内直接玩 | [astrnox/tower_game](https://github.com/astrnox/tower_game) |
| 植物大战僵尸 H5 | 策略 | 站内直接玩 | [astrnox/h5-game-plantsVSzombies](https://github.com/astrnox/h5-game-plantsVSzombies) |
| Temple of Boom | 动作 | 站内直接玩 | [astrnox/temple-of-boom](https://github.com/astrnox/temple-of-boom) |
| 10 Minutes Till Dawn | 射击 | 站内直接玩 | [astrnox/10-minutes-till-dawn](https://github.com/astrnox/10-minutes-till-dawn) |
| FCGame · FC/NES 模拟器 | 怀旧 | 跳转 | [astrnox/fcgame](https://github.com/astrnox/fcgame) |
| 斗地主 AI 对战 | 怀旧 | 跳转 | [astrnox/fight-the-landlord](https://github.com/astrnox/fight-the-landlord) |
| Trust | 策略 | 站内直接玩 | [astrnox/trust](https://github.com/astrnox/trust) |
| Wordle Plus | 文字 | 站内直接玩 | [astrnox/wordle-plus](https://github.com/astrnox/wordle-plus) |
| Odd Bot Out | 动作 | 站内直接玩 | [astrnox/odd-bot-out](https://github.com/astrnox/odd-bot-out) |
| Bubble Shooter 泡泡龙 | 休闲 | 站内直接玩 | [astrnox/arkadiumx27s-bubble-shooter](https://github.com/astrnox/arkadiumx27s-bubble-shooter) |
| WorldGuessr 猜地理 | 地理 | 跳转 | [astrnox/worldguessr](https://github.com/astrnox/worldguessr) |
| Remake | 怀旧 | 跳转 | [astrnox/remake](https://github.com/astrnox/remake) |
| Fluid 围棋 | 策略 | 跳转 | [astrnox/fluid-weiqi-web](https://github.com/astrnox/fluid-weiqi-web) |

## 特色

- **双语 README** —— 每款游戏的中英文文档都在站内直接看，默认英文，可一键切简体中文
- **零外部依赖** —— 纯静态站点，无构建步骤，README 在部署前渲染成自包含 HTML
- **专属封面** —— 每款游戏一张 SVG 封面，不用占位图，也没有 emoji

## 技术栈

原生 HTML / CSS / ES Modules，无框架、无打包器。README 用 Python 的 `markdown` 库在部署前渲染（`tools/render_readme.py`），构建期会剔除站点上不存在的图片，站内 iframe 直接注入。

```
assets/covers/     15 张专属 SVG 封面
assets/styles/     base / layout / components 分层的 CSS
data/games.json    游戏清单
readme/            26 份 README（{id}.{lang}.md + 渲染产物 .html）
images/            社交分享图与 README 内嵌截图
src/               ES Module 源码
tools/             README 渲染脚本
```

改完 `readme/*.md` 后跑一次 `python3 tools/render_readme.py` 重新生成 HTML。

## 部署

`.github/workflows/deploy.yml` 在每次 push 到 `main` 时把仓库根目录原样发布到 GitHub Pages —— 仓库根即产物目录，没有构建步骤。

## 许可

各游戏版权归原作者所有，详见对应仓库。
