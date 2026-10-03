# WorldGuessr

一款受 GeoGuessr 启发的热门地理游戏的免费游玩、源码开放版本。这个基于 React 的项目旨在提供一种有趣且有教育意义的方式，让你通过 Google Street View 影像探索世界。

### 立即[开始游玩](https://worldguessr.com)！
#### [加入 Discord 社区](https://discord.gg/yenVspFmkB)

## 功能特性

- **随机街景：** 每一局都会带你体验世界上某个全新的地点。
- **多人模式：** 挑战你的朋友，或与随机对手实时对战。
- **国家连胜：** 检验你的知识储备，看看你能连续猜对多少个国家。
- **免费运行：** 源代码公开，可免费自行托管用于非商业用途（见[许可证](#license)）。本项目使用 [Google Maps Streetview Embed API](https://developers.google.com/streetview/web)，相较于 GeoGuessr 所使用的昂贵 SDK，它完全免费。

## 致谢

- [Leaflet](https://leafletjs.com/) 用于小地图显示。
- [Leaflet.SmoothWheelZoom](https://github.com/mutsuyuki/Leaflet.SmoothWheelZoom)，作者 mutsuyuki；我们的流畅滚轮缩放（`lib/leafletFluidZoom.js`）改编自此。
- [Google Maps API](https://developers.google.com/maps)，感谢其对街景影像提供的慷慨免费额度。
- [Vali](https://github.com/slashP/Vali)，作者 @SlashP，用于为所有国家生成均衡的地点分布。
- [Next.js](https://nextjs.org/) 用于构建这个 Web 应用。
- 每一位帮助这个项目落地的贡献者！

## 本地运行

### 前置条件

开始之前，请确保你已安装以下内容：
- [Node.js](https://nodejs.org/en/)（v18.18 或更高版本）
- [npm](https://www.npmjs.com/)（v6.x 或更高版本）
- [pnpm](https://pnpm.io/)（v9.x 或更高版本）

### 安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/codergautam/worldguessr.git
   cd worldguessr
   ```

2. 安装依赖：
   ```bash
   pnpm install
   ```

3. 启动开发服务器：
   ```bash
   pnpm run dev
   ```

   用浏览器打开 [http://localhost:3000](http://localhost:3000) 查看结果。

## 部署到 VPS／外部服务器

如果你要把 WorldGuessr 部署到 VPS 或任何拥有外部 IP 的服务器上（而非 localhost），就**必须**在 `.env` 文件中配置以下环境变量：

```bash
# Replace YOUR_IP with your server's IP address or domain
NEXT_PUBLIC_API_URL=YOUR_IP:3001
NEXT_PUBLIC_WS_HOST=YOUR_IP:3002
```

**以 IP 为例：**
```bash
NEXT_PUBLIC_API_URL=123.45.67.89:3001
NEXT_PUBLIC_WS_HOST=123.45.67.89:3002
```

**以域名为例（配置好 nginx 之后）：**
```bash
NEXT_PUBLIC_API_URL=api.yourdomain.com
NEXT_PUBLIC_WS_HOST=ws.yourdomain.com
```

### 快速配置清单

1. **MongoDB** —— 在 [MongoDB Atlas](https://www.mongodb.com/atlas) 上创建一个集群（有免费额度），并添加连接字符串：
   ```bash
   MONGODB=mongodb+srv://username:password@cluster.mongodb.net/worldguessr
   ```

2. **Google OAuth** —— 在 [Google Cloud Console](https://console.cloud.google.com/) 中创建凭据：
   ```bash
   NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_client_secret
   ```

3. **API/WS URL** —— 指向你的外部 IP 或域名（见上文）

有关环境变量的详细说明，请参阅 [docs/environment-variables.md](docs/environment-variables.md)。

## 参与贡献

贡献让这个社区成为一个学习、启发与创作的非凡之地。你的任何贡献都**万分受用**。

如果你有能让它变得更好的建议，请 fork 这个仓库并创建 pull request。你也可以直接以 "enhancement" 为标签创建一个 issue。
别忘了给这个项目点个 star！再次感谢！

1. Fork 这个项目
2. 创建你的功能分支（`git checkout -b feature/AmazingFeature`）
3. 提交你的更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到该分支（`git push origin feature/AmazingFeature`）
5. 创建一个 Pull Request

## 许可证

本项目依据 PolyForm Noncommercial License 1.0.0 发布。你可以自由地出于非商业目的使用、修改和分发本项目。更多信息请见 [LICENSE.md](LICENSE.md)。

## 社区

[点击这里](https://discord.gg/yenVspFmkB)加入 Discord 社区，讨论新功能、报告 bug、与开发者交流，并结识其他玩家。

你也可以私下给我发邮件：gautam@worldguessr.com
