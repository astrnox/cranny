# Fluid Weiqi (Web Edition) · 液态围棋网页版

[Fluid Weiqi（液态围棋）](https://github.com/WangNianyi2001/Fluid-Weiqi) 的网页移植版——这是一种在连续势力场（而非离散棋子）上对弈的围棋变体。

> 原版游戏由 **王念一（Nianyi Wang）** 创作——[@WangNianyi2001](https://github.com/WangNianyi2001)。
> 这是经原作者许可完成的社区网页移植版。所有游戏规则、命名与视觉概念均归原作者所有。

## 本仓库包含什么

一个包含三个包的 pnpm monorepo：

```
fluid-weiqi-web/
├── packages/
│   └── core/          Pure-TS game logic (board, influence field, capture, match flow, WS protocol)
├── apps/
│   ├── server/        Node + ws relay server (rooms, action validation, broadcast)
│   └── web/           Vite + React + Canvas2D front-end
└── scripts/
    └── smoke-test.mjs  End-to-end WS protocol test
```

同一份游戏规则代码（`@fluid/core`）同时运行在服务端（权威校验）与客户端（预览渲染）上。

## 本地运行

需要 Node 22+ 与 pnpm 10+。

```bash
pnpm install
pnpm dev
```

`pnpm dev` 会并行启动服务端（`http://localhost:8787`）与网页开发服务器（`http://localhost:5173` 或任意空闲端口）。在浏览器中打开该网页地址即可。若要在本地进行双人对战，再打开一个标签页并使用相同的房间码即可。

若要分别启动：

```bash
pnpm --filter @fluid/server dev   # backend
pnpm --filter @fluid/web    dev   # frontend
```

若要运行协议冒烟测试（需服务端已在运行）：

```bash
node scripts/smoke-test.mjs
```

## 已实现（MVP）

- ✅ 方形棋盘（默认 19×19）、落子位置连续
- ✅ 势力场算法移植自原版的 [`BoardDistribution.compute`](https://github.com/WangNianyi2001/Fluid-Weiqi/blob/master/Assets/Resources/Shaders/BoardDistribution.compute)（CPU 采样 + Canvas 2D 放大）
- ✅ 提子检测：在地盘图上做连通分量分析、气与自杀判定
- ✅ 双人回合制对局，支持 **place**（落子）与 **pass**（弃权）操作
- ✅ 连续两次弃权即对局结束；存活棋子多者获胜
- ✅ WebSocket 协议，含房间码、加入/离开、操作转发
- ✅ 落子自动吸附到网格；按住 **Shift** 可自由连续落子（与原版一致）

## 尚未实现（为 MVP 有意裁剪）

- ❌ 基于 GPU shader 的势力场渲染（回合制下 96² 的 CPU 采样已足够；后续可换成 WebGL2）
- ❌ 球形棋盘 / 收缩模式（上游 v0.3.0 已加入）
- ❌ 大厅浏览界面（目前房间为私有，仅凭房间码进入）
- ❌ AI 对手
- ❌ 音效、动画
- ❌ 生产环境部署（步骤见下文）

## 架构说明

- `@fluid/core` 以 TypeScript 源码形式被 `apps/web`（经由 Vite）与 `apps/server`（经由 tsx）同时使用，开发期间无需构建步骤。
- 服务端是**权威方**——每一手棋都要在服务端经过 `Match.apply()`。客户端绝不直接调用游戏逻辑修改状态；它只渲染服务端广播的快照。
- 同一个 `Match.apply()` 也通过 `@fluid/core` 暴露在客户端，以便日后实现乐观 UI。
- 状态按服务端进程保存在内存中。重启服务端会销毁所有房间（这是 MVP 阶段有意为之的简化）。

## 部署（后续）

此 MVP 面向本地对战，尚未接入任何托管平台。准备就绪时：

- **前端**：Vercel / Netlify / GitHub Pages 可托管 `apps/web/dist`。执行 `pnpm --filter @fluid/web build`。
- **后端**：任何运行 Node 22+ 且支持持久 WebSocket 连接的服务均可——Render、Fly.io、Railway，或一台小型 VPS。执行 `tsx src/index.ts`（或打包为 ESM bundle）。
- 在后端设置 `PORT` 环境变量，并将前端指向它（目前 WS 地址为 `${proto}://${location.host}/ws` 并使用 Vite 的开发代理——生产环境请在 `wsClient.ts` 中替换为真实的后端地址）。

## 致谢

- **原版游戏**：[王念一的 Fluid Weiqi](https://github.com/WangNianyi2001/Fluid-Weiqi)。所有规则、术语与游戏设计思路均源自原版，经许可使用。
- **macOS 原生版本**：参见 [Keith9922/Fluid-Weiqi releases](https://github.com/Keith9922/Fluid-Weiqi/releases)。
- **本网页移植版**：Keith9922（[github.com/ Keith9922](https://github.com/Keith9922)）。

## 许可证

本仓库中的网页移植代码以 MIT 许可证发布。游戏设计、规则与视觉概念依据[上游 LICENSE](https://github.com/WangNianyi2001/Fluid-Weiqi/blob/master/LICENSE)仍归原作者所有。

如果你 fork 或扩展本移植版，请保留对原作者的致谢。
