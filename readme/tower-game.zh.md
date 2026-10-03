[![许可证](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[English](./README.en.md) | **简体中文**

<h1 align="center">塔楼建造游戏</h1>
<p align="center"><img src="https://o2qq673j2.qnssl.com/tower-loading.gif"/></p>

> 一款基于 ES6 和 Canvas 的塔楼建造游戏（Tower Bloxx Deluxe Skyscraper）

## 演示
<p align="center"><img src="https://user-images.githubusercontent.com/17680888/47480922-93a20c00-d864-11e8-8f7c-6d1d60184730.gif"/></p>
<h2 align="center"><a href="https://iamkun.github.io/tower_game">在线 Demo 链接（Demo Link）</a></h2>
<h4 align="center">移动设备可以扫描下面的二维码：</h4>
<p align="center">
  <img src="https://user-images.githubusercontent.com/17680888/47480646-abc55b80-d863-11e8-9337-4ea768ebe55d.png" />
</p>

## 游戏规则

以下是游戏的默认规则：

- 玩家初始拥有 3 点生命值（hp），由屏幕右上角的心形图标表示。每掉落一个 Tower 方块，玩家就失去 1 点生命值；生命值耗尽时游戏结束。

- 玩家每成功堆叠（Success）一个方块可获得 25 分。如果一个方块完美（Perfect）地堆叠在前一个方块上，那么玩家将获得 50 分作为奖励。连续达成 Perfect 会额外获得 25 分。

**注意：每一个 Success 或 Perfect 都算作一层楼**

  例如，第一个 Perfect 奖励 50 分。第二个连续 Perfect 奖励 75 分。
 第三个连续 Perfect 奖励 100 分，以此类推。

<p align="center">
  <img width="550" src="https://user-images.githubusercontent.com/17680888/47473105-d9021180-d843-11e8-8c19-b6b78d86cbdf.png" />
</p>

## 自定义游戏规则

```
git clone https://github.com/iamkun/tower_game.git
cd tower_game
npm install
npm start
```
在浏览器中打开 `http://localhost:8082`。

- 如需自定义图片和声音资源文件，直接替换 `assets` 目录下的对应文件即可。
- 如需自定义游戏规则，修改 `index.html` 中的 `option` 对象即可。

## 配置项（Option）

使用下面的 `option` 常量表来完成游戏规则的自定义。

**注意：所有常量都是可选的**

| 配置项 | 类型 | 说明 |
|---------|--------|-------------|
| width          | number | 游戏界面的宽度 |
| height         | number | 游戏界面的高度 |
| canvasId       | string | Canvas 中的 DOM ID |
| soundOn        | boolean | 是否开启声音 |
| successScore   | number | success 时奖励的分数 |
| perfectScore   | number | perfect 时额外奖励的分数 |
| <a href="#hookspeed">hookSpeed</a> | function | 钩子移动的速度 |
| <a href="#hookangle">hookAngle</a> | function | 钩子的角度 |
| <a href="#landblockspeed">landBlockSpeed</a> | function | 方块摆动的速度 |
| <a href="#setgamescore">setGameScore</a> | function | 用于当前分数的钩子（hook） |
| <a href="#setgamesuccess">setGameSuccess</a> | function | 用于当前成功次数的钩子（hook） |
| <a href="#setgamefailed">setGameFailed</a> | function | 用于当前失败次数的钩子（hook） |

#### hookSpeed

该函数接收两个参数 currentFloor 和 currentScore，并返回一个速度值。
```
function(currentFloor, currentScore) {
  return number
}
```

#### hookAngle

该函数接收两个参数 currentFloor 和 currentScore，并返回一个角度值。
```
function(currentFloor, currentScore) {
  return number
}
```

#### landBlockSpeed

该函数接收两个参数 currentFloor 和 currentScore，并返回一个速度值。
```
function(currentFloor, currentScore) {
  return number
}
```

#### setGameScore

该函数接收一个参数 score，并把 currentScore 设置为 score。
```
function(score) {
  // your logic
}
```

#### setGameSuccess

该函数接收一个参数 score，并把 GameSuccess 设置为 successCount。
```
function(successCount) {
  // your logic
}
```

#### setGameFailed

该函数接收一个参数 score，并把 GameFailed 设置为 failedCount。
```
function(failedCount) {
  // your logic
}
```

## 许可证

MIT license。
