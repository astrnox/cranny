# Wordle+

一个猜单词游戏。在 **6 次尝试**内找出隐藏的 **6 字母**单词。每次猜测都会得到带颜色标记的反馈——而且与经典 Wordle 不同，你可以选择**每日、每小时或无限**模式游玩。

- **在线演示：** [astrnox.github.io/wordle-plus](https://astrnox.github.io/wordle-plus/)
- **源码：** [github.com/astrnox/wordle-plus](https://github.com/astrnox/wordle-plus)

## 如何游玩

在六次尝试中猜出这个六字母单词。每次猜测之后，方块会告诉你猜得有多接近：

| 方块 | 含义 |
| --- | --- |
| 🟩 绿色 | 字母正确，位置也正确 |
| 🟨 黄色 | 字母正确，位置错误 |
| ⬜ 灰色 | 该字母不在单词中 |

利用这些反馈逐步缩小范围，**绿色方块会被锁定**并保留到下一次猜测中。六次机会，一个单词。

### 模式

- **每日（Daily）**——每天一道谜题，所有人题目相同；明天回来再挑战新的。
- **每小时（Hourly）**——每小时刷新一道新谜题。
- **无限（Infinite）**——无尽谜题，想玩多久都可以。

它完全**支持离线使用**：可以安装为 PWA，首次加载之后即可正常工作。

## 运行方式

一个自带 service worker 的自包含 JavaScript 包，可安装为**渐进式 Web 应用（Progressive Web App）**。

```
index.html        # 应用外壳，注册 service worker
build/bundle.js   # 游戏本体（已编译的打包文件）
build/bundle.css  # 样式
global.css        # 基础样式
manifest.json     # PWA manifest
sw.js             # service worker（离线缓存）
img/              # 图标 + 社交分享图
```

键盘操作：输入字母，`Enter` 提交，`Backspace` 删除。

## 本地运行

```bash
git clone https://github.com/astrnox/wordle-plus.git
cd wordle-plus
python3 -m http.server 8000
# 打开 http://localhost:8000
```

（service worker 需要 HTTP 或 HTTPS 协议——`file://` 无法注册。）

## 技术栈

- **语言：** JavaScript（打包形式）
- **类型：** 渐进式 Web 应用（可离线、可安装）
- **托管：** GitHub Pages

## 致谢

- 灵感来自 Josh Wardle 的 **Wordle**（[wordle.xyz](https://www.wordle.xyz/)）；`+` 变体在其基础上增加了每小时与无限模式。
- 本仓库是一个无拦截的网页构建版本。
