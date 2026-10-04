#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""games.json 数据生成器。

为什么用脚本而不是手写 JSON：
  98 款游戏 × 20 个字段，手写极易出错且无法复跑校验。
  这里把数据写成紧凑元组，由脚本统一展开、补默认值、校验、排序、输出。

数据来源：
  - 用户的开源游戏清单（第一/二/七部分）
  - GitHub API 实测的许可证、Star、最后提交、归档状态
  - 链接内嵌实测（tools/check_links.py）

字段口径见 data/games.schema.json。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'games.json'

TODAY = '2026-10-04'
VERIFIED_AT = '2026-10-03'

# 必须与 data/games.schema.json 的 platform 枚举一致，以及 src/components/card.js
# 的 OS_BADGE、detail.js 的 PLATFORM_NAME 对得上。加新平台要四处同步改。
KNOWN_PLATFORMS = {'web', 'pc', 'win', 'lin', 'mac', 'android', 'ios'}

# ---------------------------------------------------------------------------
# 分类
# ---------------------------------------------------------------------------
CATEGORIES = [
    ('puzzle',   '益智'),
    ('casual',   '休闲'),
    ('action',   '动作'),
    ('arcade',   '街机'),
    ('strategy', '策略'),
    ('board',    '棋牌'),
    ('shooter',  '射击'),
    ('io',       '.io'),
    ('sports',   '体育'),
    ('retro',    '怀旧'),
    ('word',     '文字'),
    ('geo',      '地理'),
    ('survival', '生存'),
    ('rpg',      '角色扮演'),
    ('tabletop', '桌游'),
    ('music',    '音乐'),
    ('racing',   '竞速'),
    ('sim',      '模拟'),
    ('sandbox',  '沙盒'),
    ('tower',    '塔防'),
]

# 许可证条目：commercial=可商用，shareAlike=改后须开源，network=网络服务须开源
LICENSES = [
    ('MIT',          'MIT',          'https://opensource.org/license/mit',          True,  False, False),
    ('Apache-2.0',   'Apache-2.0',   'https://www.apache.org/licenses/LICENSE-2.0',  True,  True,  False),
    ('BSD',          'BSD',          'https://opensource.org/license/bsd-3-clause', True,  False, False),
    ('zlib',         'zlib',         'https://opensource.org/license/zlib-license', True, False, False),
    ('MPL-2.0',      'MPL-2.0',      'https://www.mozilla.org/media/MPL/2.0/',     True,  True,  False),
    ('LGPL-2.1',     'LGPL-2.1',     'https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html', True, True, False),
    ('GPL-2.0',      'GPL-2.0',      'https://www.gnu.org/licenses/old-licenses/gpl-2.0.html', True, True, False),
    ('GPL-3.0',      'GPL-3.0',      'https://www.gnu.org/licenses/gpl-3.0.html', True,  True,  False),
    ('AGPL-3.0',     'AGPL-3.0',     'https://www.gnu.org/licenses/agpl-3.0.html', True,  True,  True),
    ('CC-BY-SA-3.0', 'CC-BY-SA-3.0', 'https://creativecommons.org/licenses/by-sa/3.0/', True, True, True),
    ('CC-BY-SA-4.0', 'CC-BY-SA-4.0', 'https://creativecommons.org/licenses/by-sa/4.0/', True, True, True),
    ('CC0-1.0',      'CC0-1.0',      'https://creativecommons.org/publicdomain/zero/1.0/', True, False, False),
    ('NetHack-PL',   'NetHack 公用许可', 'https://www.nethack.org/common/license.html', True, True, False),
    ('OSL-3.0',      'OSL-3.0',      'https://opensource.org/license/osl-3-0',      True,  True,  True),
]

# ---------------------------------------------------------------------------
# 第一部分 · 可直接在线玩
# 元组字段：id, title, alias, desc, url, repo, license, cats, tags,
#           accent, embeddable, stars, pushed, extra(可覆盖任意字段)
# ---------------------------------------------------------------------------
WEB = [
    # --- 策略 / 模拟 / 建造 ---
    ('mindustry', 'Mindustry 工厂战争', ['mindustry', '塔防', '流水线'],
     '塔防加流水线自动化，一人Factories 的开源答案。',
     'https://mindustrygame.github.io/', 'Anuken/Mindustry', 'GPL-3.0',
     ['strategy', 'tower', 'action'], ['塔防', '自动化', 'RTS', '可联机'],
     205, True, 0, '', {}),

    ('freeciv-web', 'Freeciv-web 自由文明', ['freeciv', '文明', '4x'],
     '浏览器里的 4X 文明网页版，开源世纪老将。',
     'https://freecivweb.org/', 'freeciv/freeciv-web', 'GPL-2.0',
     ['strategy', 'board'], ['4X', '回合', '文明', '多人'],
     30, True, 0, '', {}),

    ('openttd-wasm', 'OpenTTD 交通大亨', ['openttd', 'td', '交通'],
     '开源运输模拟，WASM 移植后浏览器直接跑。',
     'https://transport-tycoon.k3.demos.sulat.com/', 'OpenTTD/OpenTTD', 'GPL-2.0',
     ['sim', 'strategy'], ['模拟', '交通', '经营', '像素'],
     200, True, 0, '', {}),

    ('unciv', 'Unciv 完整文明', ['unciv', '文明'],
     '手机端 3  civilisation 的开源复刻，Web 版可直接玩。',
     'https://play.rosebud.ai/play/unciv-base', 'yairm210/Unciv', 'MPL-2.0',
     ['strategy'], ['4X', '回合', '文明'],
     215, True, 0, '', {}),

    ('cc-web', 'Command & Conquer 网页复刻', ['cc', '红色警戒', 'rts'],
     '红色警戒网页复刻，非官方但完整可玩。',
     'https://adityaravishankar.github.io/command-and-conquer/',
     'adityaravishankar/command-and-conquer', None,
     ['strategy'], ['RTS', '即时战略', '复刻'],
     12, True, 808, '2020-10-03',
     {'licenseNote': '仓库无 LICENSE 文件，仅源码公开，法律上默认保留所有权利'}),
    ('ancient-beast', 'Ancient Beast 远古巨兽', ['ancientbeast', '回合计'],
     '阿凡提式回合策略，画面精致的老牌开源。',
     'https://ancientbeast.com/', 'FreezingMoon/AncientBeast', 'AGPL-3.0',
     ['strategy'], ['回合', '策略', '多人'],
     270, True, 0, '', {}),
    ('burgomaster-1255', '1255 Burgomaster 城建', ['1255', '城建'],
     '中世纪城市建设与战役管理，界面朴素但系统扎实。',
     'https://1255.areso.pro/', 'Areso/1255-burgomaster', 'GPL-3.0',
     ['strategy', 'sim'], ['城建', '中世纪', '建造'],
     25, True, 0, '', {}),
    ('3d-city', '3d.city 城市模拟', ['3dcity', '城市'],
     '像搭积木一样长城市的网页沙盒。',
     'https://lo-th.github.io/3d.city/', 'lo-th/3d.city', 'GPL-3.0',
     ['sim', 'sandbox'], ['城市', '建造', '沙盒'],
     165, True, 0, '', {}),

    # --- Roguelike / 生存 ---
    ('cataclysm-dda', 'Cataclysm: DDA', ['dda', '末日', 'cataclysm'],
     '回合制生存 Roguelike，浏览器 WASM 版能玩但很长。',
     'https://browsercraft.com/play/cataclysm-dark-days-ahead',
     'CleverRaven/Cataclysm-DDA', 'CC-BY-SA-3.0',
     ['survival', 'rpg'], ['Roguelike', '生存', '回合', '末日'],
     45, False, 0, '', {'players': 1}),
    ('shattered-pixel-dungeon', 'Shattered Pixel Dungeon', ['像素地牢', 'spd'],
     '像素风 Roguelike 地牢爬行，手机也能玩。',
     'https://pixel-dungeon.com/', '00-Evan/shattered-pixel-dungeon', 'GPL-3.0',
     ['rpg', 'survival'], ['Roguelike', '地牢', '像素', '回合'],
     350, True, 0, '', {}),
    ('dcss', 'Dungeon Crawl Stone Soup', ['dcss', '石头汤', 'crawl'],
     '文字 roguelike 的社区分支，WebTiles 直连公共服务器。',
     'https://crawl.develz.org/play.htm', 'crawl/crawl', 'GPL-2.0',
     ['rpg', 'survival'], ['Roguelike', '文字', '地牢', '多人'],
     60, True, 0, '', {}),
    ('nethack', 'NetHack', ['nethack', '地下城'],
     '三十年不倒的地牢绞肉机，正版授权老游戏。',
     'https://nethack.alt.org/', 'NetHack/NetHack', 'NetHack-PL',
     ['rpg', 'survival'], ['Roguelike', '文字', '地牢', '硬核'],
     95, False, 0, '',
     {'note': '实测响应头带 CSP frame-ancestors self，禁止内嵌'}),
    ('angband', 'Angband', ['angband'],
     'classic roguelike，设定深且自由度高。',
     'https://angband.live/', 'angband/angband', 'GPL-2.0',
     ['rpg'], ['Roguelike', '文字', '地牢'],
     30, True, 0, '', {}),
    ('a-dark-room', 'A Dark Room', ['暗室', 'adr'],
     '一开始只有生火按钮的文字生存，克制到极致的经典。',
     'https://adarkroom.doublespeakgames.com/', 'doublespeakgames/adarkroom', 'MPL-2.0',
     ['word', 'survival'], ['文字', '生存', '放置', '极简'],
     0, True, 0, '', {}),

    # --- 街机 / 休闲 / 益智 ---
    ('2048-original', '2048 原版', ['2048', '二四八', '数字合并'],
     '那个把手机屏幕玩秃的数字合并游戏原版。',
     'https://play2048.co/', 'gabrielecirulli/2048', 'MIT',
     ['puzzle', 'casual'], ['益智', '数字', '合成', '经典'],
     45, False, 0, '',
     {'note': '官方站设了 frame-ancestors，无法内嵌；站内 fork 版见「2048 合集」'}),
    ('candy-box-2', 'Candy Box 2', ['糖果盒', '放置'],
     '网页里藏了二十年的放置 RPG，后劲很大。',
     'https://candybox2.github.io/', 'candybox2/candybox2.github.io', 'GPL-3.0',
     ['rpg', 'casual'], ['放置', '文字', '隐藏要素', '彩蛋'],
     330, True, 0, '', {}),
    ('clumsy-bird', 'Clumsy Bird 笨笨鸟', ['笨鸟', 'clumsy'],
     'Flappy Bird 的开源复刻，物理弹得莫名其妙地好玩。',
     'https://ellisonleao.github.io/clumsy-bird/', 'ellisonleao/clumsy-bird', 'MIT',
     ['arcade', 'casual'], ['飞行', '物理', '单指', '高分'],
     55, True, 0, '', {}),
    ('duck-hunt-js', 'Duck Hunt JS 猎鸭', ['猎鸭', 'ducks'],
     '红白机上那两管猎鸭枪的网页复刻。',
     'https://duckhuntjs.com/', 'MattSurabian/DuckHunt-JS', 'MIT',
     ['shooter', 'retro'], ['射击', '怀旧', '复刻', '鼠标'],
     20, True, 0, '', {}),
    ('skifree-js', 'SkiFree.js 滑雪', ['滑雪', 'skifree'],
     '无尽下坡滑雪，越滑越快，看你能撑多久。',
     'https://basicallydan.github.io/skifree.js/', 'basicallydan/skifree.js', 'MIT',
     ['arcade', 'sports'], ['滑雪', '无尽', '反应', '单指'],
     195, True, 0, '', {}),
    ('alien-invasion', 'Alien Invasion 星际侵略', ['外星', '入侵'],
     '打飞机类射击，敌人分波次涌来。',
     'https://cykod.github.io/AlienInvasion/', 'cykod/AlienInvasion', 'GPL-2.0',
     ['shooter'], ['射击', '飞机', '复古'],
     140, True, 183, '2019-10-07', {}),
    ('breakout-71', 'Breakout 71', ['打砖块', 'breakout'],
     '70 年代太空打砖块的现代重制，画面很讲究。',
     'https://breakout.lecaro.me/', 'https://gitlab.com/lecarore/breakout71', 'AGPL-3.0',
     ['arcade', 'puzzle'], ['打砖块', '街机', '矢量'],
     250, True, 0, '', {}),
    ('digger', 'Digger 挖地', ['挖地', 'digger'],
     '钻地采矿石的 HTML5 小游戏，上游仓库已归档。',
     'https://lutzroeder.com/html5/digger/', 'lutzroeder/digger', None,
     ['arcade', 'action'], ['挖矿', '街机', 'HTML5'],
     85, True, 95, '2024-02-12',
     {'licenseNote': '上游仓库已归档且无许可证文件', 'archived': True}),
    ('custom-tetris', 'Custom Tetris 俄罗斯方块', ['俄罗斯方块', 'tetris'],
     '带自定关卡编辑器的俄罗斯方块。',
     'https://ondras.github.io/custom-tetris/', 'ondras/custom-tetris', 'MIT',
     ['puzzle', 'arcade'], ['俄罗斯方块', '消除', '编辑器'],
     280, True, 0, '', {}),
    ('backdooms', 'Backdooms', ['dooms', '快克'],
     '老 Doom 引擎做的手机版，扫码即玩。',
     'https://kuberwastaken.github.io/backdooms/', 'Kuberwastaken/backdooms', 'MIT',
     ['shooter', 'retro'], ['FPS', '复古', '手机', '扫码'],
     0, True, 641, '2026-09-17', {}),
    ('captain-rogers', 'Captain Rogers 罗杰船长', ['罗杰船长', 'platformer'],
     '单屏平台跳跃，致敬红白机时代。',
     'https://enclavegames.com/games/captain-rogers/',
     'EnclaveGames/Captain-Rogers', None,
     ['action', 'arcade'], ['平台', '跳跃', '像素'],
     165, True, 51, '2020-05-24',
     {'licenseNote': '仓库无 LICENSE 文件',
      'status': 'broken',
      'note': '在线站已 404（项目下线），仓库与 README 仍可访问'}),
    ('green-mahjong', 'Green Mahjong 绿麻将', ['麻将', 'mahjong'],
     '麻将连连看，三消规则清爽不费脑。',
     'https://danbeck.github.io/green-mahjong/', 'danbeck/green-mahjong', 'MIT',
     ['puzzle', 'casual'], ['麻将', '三消', '消除'],
     130, True, 0, '', {}),
    ('c4', 'c4 四子棋', ['四子棋', 'connect4'],
     '经典四子棋，网页上跟人对弈或跟电脑练。',
     'https://kenrick95.github.io/c4/', 'kenrick95/c4', 'MIT',
     ['tabletop', 'board'], ['棋类', '桌游', '策略', '双人对弈'],
     210, True, 0, '', {'players': 2}),

    # --- 角色扮演 / 冒险 ---
    ('diablo-js', 'Diablo JS 暗黑', ['暗黑', 'diablo'],
     '动作 RPG，地牢刷装备的手感很有那年味。',
     'https://mitallast.github.io/diablo-js/', 'mitallast/diablo-js', 'MIT',
     ['rpg', 'action'], ['刷装备', '地牢', '动作'],
     5, True, 0, '', {}),
    ('hexa-battle', 'Hexa Battle 六角战', ['六角战', 'hb'],
     '六边形格子上的爬行对战。',
     'https://itajaja.github.io/hb/', 'itajaja/hb', 'MIT',
     ['rpg', 'action'], ['六边形', '地牢', '爬行'],
     185, True, 87, '2017-06-21', {}),
    ('untrusted', 'Untrusted 不可信', ['不可信'],
     '画风很怪的解谜 RPG，第一人称里摸索出路。',
     'https://alexnisnevich.github.io/untrusted/', 'AlexNisnevich/untrusted', 'MIT',
     ['rpg', 'puzzle'], ['解谜', '第一人称', '复古'],
     25, True, 0, '', {}),
    ('rapid-dominance', 'Rapid Dominance 快节奏', ['rapid'],
     'RTS 与卡牌混合的快节奏对战。',
     'https://wenta.github.io/rapid-dominance/', 'wenta/rapid-dominance', 'Apache-2.0',
     ['strategy', 'board'], ['RTS', '卡牌', '快节奏'],
     15, True, 18, '2023-11-01', {}),

    # --- 射击 / 动作 / 竞速 / 音乐 ---
    ('hexgl', 'HexGL 未来竞速', ['hexgl', '极速'],
     '反重力赛车，实时光影做得像 2012 年的科幻片。',
     'https://hexgl.bkcore.com/', 'BKcore/HexGL', 'MIT',
     ['racing'], ['竞速', '科幻', '反重力', '光影'],
     200, True, 0, '', {}),
    ('astray', 'Astray 迷宫', ['astray', '3d迷宫'],
     '第一人称 3D 迷宫生成器，每一局都不一样。',
     'https://wwwtyro.github.io/Astray/', 'wwwtyro/Astray', 'MIT',
     ['action', 'puzzle'], ['3D', '迷宫', '第一人称'],
     285, True, 0, '', {}),
    ('fluid-table-tennis', 'Fluid Table Tennis 流体乒乓', ['乒乓球', 'fluid'],
     '流体物理驱动的乒乓球，来球角度全靠算。',
     'https://anirudhjoshi.github.io/fluid_table_tennis/',
     'anirudhjoshi/fluid_table_tennis', 'MIT',
     ['sports', 'arcade'], ['乒乓球', '物理', '流体', '对战'],
     160, True, 0, '', {'players': 2}),
    ('wpilot', 'WPilot 太空飞行员', ['wpilot', '太空'],
     '太空飞行射击，操作简单但容易上瘾。',
     'https://jfd.github.io/wpilot/', 'jfd/wpilot', 'MIT',
     ['shooter', 'action'], ['太空', '射击', '飞行', '复古'],
     230, True, 0, '', {}),
    ('nazi-zombies-portable', 'Nazi Zombies Portable', ['nzp', '丧尸'],
     '开放世界丧尸射击，老派但很杀时间。',
     'https://nzp.gay/', 'nzp-team/nzportable', None,
     ['shooter'], ['FPS', '丧尸', '开放世界', '联机'],
     10, True, 827, '2026-09-24',
     {'licenseNote': '仓库无 LICENSE 文件', 'stars': 827, 'players': 4}),
    ('bemuse', 'Bemuse 音乐游戏', ['bemuse', '节奏'],
     '节奏游戏里少见的一档，界面干净、上手快。',
     'https://bemuse.ninja/', 'bemusic/bemuse', 'AGPL-3.0',
     ['music'], ['节奏', '音乐', '谱面', '现代'],
     275, True, 0, '', {}),

    # --- 棋类 / 桌游 / 多人服务器 ---
    ('lichess', 'Lichess 国际象棋', ['lichess', '国际象棋', 'chess'],
     '免费开源的在线国际象棋，强弱 AI 都有。',
     'https://lichess.org/', 'lichess-org/lila', 'AGPL-3.0',
     ['board', 'strategy'], ['棋类', '国际象棋', '联机', '开源之最'],
     40, False, 0, '',
     {'players': 2, 'note': '官方站设 X-Frame-Options: DENY，只能外链'}),
    ('boxcars', 'Boxcars 双陆棋', ['boxcars', '双陆'],
     '在线双陆棋，对手来自全世界。',
     'https://play.bgammon.org/', 'tslocum/boxcars', 'AGPL-3.0',
     ['tabletop', 'board'], ['双陆棋', '棋类', '联机'],
     120, True, 0, '', {'players': 2, 'repo': 'https://codeberg.org/tslocum/boxcars'}),
    ('stendhal', 'Stendhal 斯坦达尔', ['stendhal', 'mmo'],
     '文字 MMORPG，玩了二十年的老开源世界。',
     'https://stendhalgame.org/', 'arianne/stendhal', 'GPL-2.0',
     ['rpg', 'word'], ['MMO', '文字', '冒险', '多人'],
     300, False, 0, '',
     {'note': '官方站设 X-Frame-Options: SAMEORIGIN；游戏本身需 Java 客户端'}),
]

# ---------------------------------------------------------------------------
# 第二部分 · 需下载安装
# ---------------------------------------------------------------------------
DOWNLOAD = [
    ('openra', 'OpenRA 红色警戒', ['openra', '红色警戒'],
     '用开源引擎重做的红色警戒，原版素材需自备。',
     'OpenRA/OpenRA', 'GPL-3.0', ['strategy'], ['RTS', '即时战略', '经典复刻'],
     20, 17478, '2026-10-03', 'win,lin,mac',
     {'assetNote': '代码 GPL-3.0；原版 C&C 素材需自备'}),
    ('warzone-2100', 'Warzone 2100 战区2100', ['warzone', '战区'],
     '开源 RTS 老兵，剧情和难度比同类扎实。',
     'warzone2100/warzone2100', 'GPL-2.0', ['strategy'], ['RTS', '剧情', '科幻'],
     190, 3982, '2026-10-02', 'win,lin,mac',
     {'assetNote': '代码与素材均 GPL-2.0-or-later，含 CC0 内容'}),
    ('0ad', '0 A.D. 零纪元', ['0ad', '零纪元'],
     '古代文明 RTS，免费但配置要求偏高；仓库已归档。',
     '0ad/0ad', 'GPL-2.0', ['strategy'], ['RTS', '古代', '高画质'],
     35, 2824, '2024-08-17', 'win,lin,mac',
     {'archived': True,
      'licenseNote': '此为已废弃的 SVN 镜像，代码 GPL-2.0，美术 CC-BY-SA-3.0',
      'note': '上游仓库已标注 DEPRECATED，官方已迁移到自建 SVN'}),
    ('widelands', 'Widelands 旷野', ['widelands', '旷野'],
     '《盖亚战纪》思路的开源经济模拟 RTS。',
     'widelands/widelands', 'GPL-2.0', ['strategy', 'sim'], ['RTS', '经济', '建造'],
     45, 3072, '2026-10-01', 'win,lin,mac', {}),
    ('wesnoth', 'Battle for Wesnoth 韦诺之战', ['wesnoth', '韦诺'],
     '战棋经典，几百关战役全靠手写剧情。',
     'wesnoth/wesnoth', 'GPL-2.0', ['strategy'], ['战棋', '回合', '剧情', '海量关卡'],
     265, 6900, '2026-10-03', 'win,lin,mac',
     {'assetNote': '代码 GPL-2.0，新素材多为 CC-BY-SA'}),
    ('hedgewars', 'Hedgewars 刺猬大战', ['hedgewars', '刺猬'],
     '炮战版坦克大战，画面卡通但战术真不简单。',
     'hedgewars/hw', 'GPL-2.0', ['action', 'strategy'], ['炮战', '回合', '卡通', '联机'],
     75, 563, '2026-09-26', 'win,lin,mac,android', {}),
    ('freeciv', 'Freeciv 自由文明（客户端）', ['freeciv客户端'],
     '经典自由文明桌面版，与网页版可互通存档。',
     'freeciv/freeciv', 'GPL-2.0', ['strategy', 'board'], ['4X', '回合', '文明', '联机'],
     25, 1601, '2026-10-04', 'win,lin,mac',
     {'assetNote': '代码 GPL-2.0，部分素材为 CC'}),
    ('luanti', 'Luanti 体素沙盒', ['luanti', 'minetest', '体素'],
     '原 Minetest，开源体素沙盒，模组生态极活跃。',
     'luanti-org/luanti', 'LGPL-2.1', ['sandbox'], ['体素', '沙盒', '模组', '建造'],
     110, 13676, '2026-10-03', 'win,lin,mac,android',
     {'assetNote': '引擎 LGPL-2.1，素材 CC-BY-SA-3.0'}),
    ('veloren', 'Veloren 沃洛伦', ['veloren', '沃洛伦'],
     '体素风 RPG，Rust 团队写的，生态全自由。',
     'veloren/veloren', 'GPL-3.0', ['rpg', 'sandbox'], ['体素', 'RPG', '开放世界', '联机'],
     150, 7598, '2026-10-03', 'win,lin',
     {'assetNote': '代码 GPL-3.0，素材 CC-BY-SA-4.0'}),
    ('endless-sky', 'Endless Sky 无尽天空', ['endlesssky', '太空贸易'],
     '太空贸易与战斗，像在写自己的科幻小说。',
     'endless-sky/endless-sky', 'GPL-3.0', ['rpg', 'sim'],
     ['太空', '贸易', 'RPG', '剧情'],
     250, 7609, '2026-10-03', 'win,lin,mac,android',
     {'assetNote': '代码 GPL-3.0，素材 CC-BY-SA 与公共领域'}),
    ('flare-rpg', 'Flare RPG 火焰', ['flare', '火焰'],
     '单人动作 RPG，剧情改编自开源奇幻小说。',
     'flareteam/flare-game', 'GPL-3.0', ['rpg', 'action'], ['动作', 'RPG', '奇幻', '剧情'],
     15, 1320, '2026-08-08', 'win,lin,mac',
     {'licenseNote': '仓库许可证识别为 NOASSERTION；上游声明 GPL-3.0，素材 CC-BY-SA-3.0'}),
    ('supertuxkart', 'SuperTuxKart 超级卡丁车', ['supertuxkart', '卡丁车'],
     '卡通引擎的竞速游戏，关卡编辑器能自己造图。',
     'supertuxkart/stk-code', 'GPL-3.0', ['racing'], ['竞速', '卡通', '编辑器', '联机'],
     205, 5394, '2026-10-02', 'win,lin,mac,android', {}),
    ('xonotic', 'Xonotic 超级武器竞赛', ['xonotic', '武器竞赛'],
     'Arena 射击的复活之作，上下左右都爽。',
     'xonotic/xonotic', 'GPL-2.0', ['shooter'], ['FPS', '竞技', '快节奏', '联机'],
     300, 0, '', 'win,lin,mac',
     {'repo': 'https://gitlab.com/xonotic/xonotic', 'assetNote': '代码 GPL-2.0，素材 GPL/CC-BY-SA'}),
    ('red-eclipse', 'Red Eclipse 红日', ['redeclipse', '红日'],
     '免费开源的三维竞技射击，自带编辑器。',
     'redeclipse/base', 'zlib', ['shooter'], ['FPS', '竞技', '编辑器'],
     5, 534, '2026-09-27', 'win,lin,mac',
     {'licenseNote': '引擎代码 zlib；随附社区数据模块多为 CC-BY-SA',
      'stars': 534,
      'note': '官方组织是 redeclipse，游戏主体代码在 redeclipse/base（SVG/CC 资源在 redeclipse/community）'}),
    ('freedoom', 'Freedoom 自由的地狱', ['freedoom', 'doom'],
     '完全自由 doom 引擎的素材包，自己配就能玩。',
     'freedoom/freedoom', 'BSD', ['shooter'], ['FPS', '素材包', '自由'],
     0, 1354, '2026-10-02', 'win,lin,mac,android',
     {'licenseNote': '仓库许可证识别为 NOASSERTION，项目声明 BSD 系列', 'stars': 1354}),
    ('quake3-arena', 'Quake III Arena 引擎', ['q3', 'quake3'],
     'id 开源了 Quake III 引擎，但原版素材不自由。',
     'id-Software/Quake-III-Arena', 'GPL-2.0', ['shooter'], ['FPS', '引擎', '竞技'],
     0, 8249, '2024-08-02', 'win,lin',
     {'assetNote': '引擎代码 GPL-2.0；原版对局素材不自由，需搭配自由素材包'}),
    ('openmw', 'OpenMW 晨风', ['openmw', '晨风'],
     '重建上古卷轴 3 的开源引擎，素材需自备。',
     'OpenMW/openmw', 'GPL-3.0', ['rpg', 'sandbox'], ['RPG', '开放世界', '引擎'],
     120, 6595, '2026-10-03', 'win,lin,mac',
     {'assetNote': '引擎 GPL-3.0；需自备《晨风》游戏数据'}),
    ('openrct2', 'OpenRCT2 侏罗纪公园', ['openrct2', '过山车'],
     '《过山车大亨 2》的开源重制版，功能比原版还多。',
     'OpenRCT2/OpenRCT2', 'GPL-3.0', ['sim'], ['模拟经营', '过山车', '建造'],
     340, 16274, '2026-10-04', 'win,lin,mac',
     {'assetNote': '代码 GPL-3.0；需自备《过山车大亨 2》原始数据'}),
    ('stepmania', 'StepMania 跳舞机', ['stepmania', '跳舞机'],
     '开源音乐游戏引擎，自制谱面与键盘练习两用。',
     'stepmania/stepmania', None, ['music'], ['音乐', '节奏', '引擎', '自制谱面'],
     285, 2107, '2026-08-22', 'win,lin,mac',
     {'licenseNote': '仓库未附 LICENSE 文件；项目官网声明 MIT，需以官网为准'}),
    ('bananabread', 'BananaBread 引擎', ['bananabread', '香蕉面包'],
     'C++ 3D 引擎的 WebAssembly 移植，网页里能跑。',
     'kripken/BananaBread', None, ['shooter'], ['引擎', '3D', 'WebAssembly'],
     130, 1451, '2022-05-31', 'win,lin,mac',
     {'licenseNote': '仓库未附 LICENSE 文件；项目声明 zlib'}),
]

# ---------------------------------------------------------------------------
# 第七部分 · js13kGames（13KB 大赛作品，需自托管）
# 字段：id, title, alias, desc, license, cats, tags, accent, stars, desc_src
# ---------------------------------------------------------------------------
JS13K = [
    ('a-verse-on-leverage', 'A Verse on Leverage', ['杠杆'],
     '押韵串烧动作游戏，靠谐音过关。', 'AGPL-3.0', ['action'], ['文字', '押韵'], 320, ''),
    ('ap11', 'ap11', ['ap'],
     '2014 年参赛作品，剧情简短的老派动作。', 'GPL-3.0', ['action'], ['参赛作品', '复古'], 8, ''),
    ('asdf', 'asdf · 西蒙复刻', ['西蒙', 'simon'],
     '1978 年西蒙电子游戏复刻，四个按钮。', 'MIT', ['casual'], ['记忆', '经典复刻', '四键'], 35, ''),
    ('bouncing-button', 'Bouncing Button', ['弹跳按钮'],
     '按钮在屏幕上乱弹，点击得分。', 'MIT', ['arcade'], ['点击', '极简'], 200, ''),
    ('chem-fight', 'Chem Fight 化学大战', ['化学', 'chem'],
     '买原子配 compounds，反应对赢整场战斗。', 'MIT', ['strategy'], ['化学', '对战', '教育'], 165, ''),
    ('clash-of-elements', 'Clash of Elements', ['元素冲突'],
     '左上角架枪轰对角敌人，拆掉对方建筑。', 'GPL-2.0', ['shooter', 'strategy'], ['对战', '射击', '建筑'], 5, ''),
    ('dante', 'Dante 但丁', ['但丁'],
     '2022 年参赛作品，取材但丁《神曲》。', 'MIT', ['action'], ['参赛作品', '动作'], 275, ''),
    ('dodos-escaping-from-extinction', 'Dodos Escaping', ['恐鸟'],
     '恐鸟逃离灭绝，可自造关卡。', 'GPL-3.0', ['action', 'puzzle'], ['平台', '关卡编辑'], 100, ''),
    ('elematter', 'Elematter 元素塔防', ['元素塔防'],
     '简笔画风的塔防，2014 年参赛作。', 'MIT', ['tower', 'strategy'], ['塔防', '极简'], 145, ''),
    ('felicity-and-the-fifth-element-love', 'Felicity and the Fifth Element', ['第五元素'],
     '单屏 NES 风格平台跳跃，手感很难。', 'GPL-2.0', ['action'], ['平台', '高难度', 'NES'], 15, ''),
    ('fill-in-4', 'Fill in 4', ['填四'],
     '四行填数的数字消除玩法。', 'Apache-2.0', ['puzzle'], ['数字', '消除'], 45, ''),
    ('floor-thirteen', 'Floor Thirteen', ['十三层'],
     '像素战争塔防，作者昵称就叫 Pixel Wars。', 'MIT', ['tower', 'strategy'], ['塔防', '像素'], 180, ''),
    ('forest-racer', 'Forest Racer 森林竞速', ['森林竞速'],
     '高速纯 HTML5 竞速，跑得比音乐还快。', None, ['racing'], ['竞速', '高速'], 95, ''),
    ('hard-vacuum-recon', 'Hard Vacuum Recon', ['真空侦察'],
     '冰星球侦察，靠记忆和半坏的设备活着回来。', 'MIT', ['action', 'survival'], ['科幻', '记忆', '文字'], 220, ''),
    ('junojs', 'JunoJS', ['朱诺'],
     '又一款太空管状射击，Juno 探测器的梗。', 'MIT', ['shooter'], ['太空', '射击', '复古'], 250, ''),
    ('kazukis-escape', "Kazuki's Escape", ['和树的escape'],
     '越狱五年的和树在夜里逃出去。', 'MIT', ['action'], ['逃脱', '潜行'], 300, ''),
    ('mawlight', 'MawLight 噬光', ['噬光'],
     '种田、升级、推线，越往前越难。', 'Apache-2.0', ['rpg', 'strategy'], ['经营', '生存', '推进'], 155, ''),
    ('mentat', 'Mentat 门萨', ['门萨', '数独'],
     '拖数字棋子，行列和为偶数就得分。', 'MIT', ['puzzle'], ['数独', '变体', '益智'], 25, ''),
    ('milehigh', 'Mile High 空中事故', ['空中', '劫机'],
     '在客机上求好运，飞机一直在出事。', 'MIT', ['casual'], ['随机', '黑色幽默'], 210, ''),
    ('mission-darkwhite', 'Mission Darkwhite', ['暗白行动'],
     '只支持鼠标键盘的太空射击，越快越准。', 'Apache-2.0', ['shooter'], ['太空', '瞄准', '射击'], 240, ''),
    ('neptune-blue', 'Neptune Blue 海王蓝', ['海王'],
     '海王星上的操作演练，左右移动躲攻击。', 'MIT', ['action'], ['躲避', '太空'], 195, ''),
    ('please-play-again', 'Please Play Again', ['再来一次'],
     '2013 年参赛作品，「再玩一次」的执念。', 'GPL-2.0', ['arcade'], ['参赛作品', '街机'], 60, ''),
    ('pocketrocket', 'PocketRocket 口袋火箭', ['口袋火箭'],
     '四发火箭选一发，别越过自己的射线。', 'MIT', ['puzzle'], ['躲闪', '极简'], 320, ''),
    ('radius-raid', 'Radius Raid 半径突袭', ['半径'],
     '13 种敌机 5 种强化，卷轴打到底。', 'MIT', ['shooter'], ['太空', '弹幕', '复古'], 230, ''),
    ('rainbow-claw', 'Rainbow Claw 彩虹抓娃娃', ['彩虹', 'unicorn'],
     '独角兽主题的抓娃娃机 roguelite。', 'MIT', ['arcade'], ['抓娃娃', '肉鸽', '彩虹'], 330, ''),
    ('rainbow-reboot', 'Rainbow Reboot', ['彩虹重启'],
     '2026 年参赛作，WebXR 迷你游戏。', 'MIT', ['casual'], ['WebXR', 'VR', '极简'], 20, ''),
    ('road-the-game', 'Road The Game 鸡过马路', ['鸡', '过马路'],
     '鸡为什么过马路？顺便把所有车撞一遍。', 'MIT', ['action'], ['黑色幽默', '得分'], 40, ''),
    ('senshi', 'Senshi 战士', ['战士'],
     '大逃杀风格的像素 MMO 混战。', 'MIT', ['action'], ['大逃杀', '像素', '多人'], 350, ''),
    ('shapeblocks', 'ShapeBlocks 形状块', ['形状'],
     '形状堆叠消除，作者自己说 UI 没时间做。', 'MIT', ['puzzle'], ['消除', '形状'], 170, ''),
    ('sorades-13k', 'Sorades 13K', ['sorades'],
     '《警戒：永恒》风格卷轴射击，活过 13 波。', 'Apache-2.0', ['shooter'], ['卷轴', '射击', '弹幕'], 265, ''),
    ('spacepi', 'SpacePi 太空派', ['太空pi'],
     '鼠标准确度游戏，守住 13 个基地。', 'MIT', ['puzzle', 'strategy'], ['防守', '画线', '鼠标'], 290, ''),
    ('terraform', 'Terraform 改造星球', ['terraform', '改造'],
     '音乐解谜，把一颗死星改造成能住人的地方。', 'MIT', ['puzzle', 'music'], ['音乐', '解谜', '建造'], 185, ''),
    ('the-unlucky-king', 'The Unlucky King 倒霉国王', ['倒霉国王'],
     '13KB 的平台跳跃，运气决定你能走多远。', 'MIT', ['action'], ['平台', '运气'], 5, ''),
    ('timer-madness', 'Timer Madness 计时狂乱', ['计时'],
     '手速训练：点破圆点，别让计时器跑完。', 'MIT', ['arcade'], ['反应', '计时', '点击'], 215, ''),
    ('under-the-crypt', 'Under the Crypt 墓下', ['墓下'],
     '地牢爬行塔防，超难模式死了就重来。', 'GPL-3.0', ['tower', 'rpg'], ['塔防', '爬行', '高难度'], 275, ''),
    ('unifrost', 'Unifrost 独霜', ['独霜'],
     '2016 年 3D 平台跳跃，小得刚好。', 'MIT', ['action'], ['3D', '平台'], 205, ''),
    ('vier-wizard-wars', 'Vier Wizard Wars', ['巫师战争'],
     '像素世界打元素敌人，像老 Atari。', 'MIT', ['action', 'strategy'], ['像素', '元素', '复古'], 310, ''),
    ('wind-rider', 'Wind Rider 御风者', ['御风'],
     '2014 年参赛作品，标题党式酷炫。', 'MIT', ['action'], ['飞行', '参赛作品'], 130, ''),
]

# ---------------------------------------------------------------------------
# 站主自己的 15 款（原有内容，保持 id 与上线地址不变）
#
# 许可证说明：这些仓库是 fork，GitHub 常检测不到 LICENSE 文件，
# 因此许可证以上游项目的官方声明为准，licenseNote 里写明这一点。
# ---------------------------------------------------------------------------
OWN = [
    # id, title, alias, desc, url, mode, embed, license, cats, tags, accent,
    # readmeLangs, featured, source, addedAt, extra
    # extra.repo 用于 id 与实际仓库名不一致的情况（连字符 vs 下划线）
    ('2048', '2048 合集', ['二四八', '数字合并'],
     '多种玩法，一种经典。数字合并游戏的合集版。',
     'https://2048.xns.asia/', 'redirect', False, 'MIT',
     ['puzzle', 'casual', 'arcade'], ['益智', '数字', '合成', '单指'],
     210, ['zh'], True, 'own', '2026-08-21', {}),
    ('hextris', 'Hextris 六边形俄罗斯方块', ['Hextris', '六边形', 'hex'],
     '六边形旋转方块，节奏明快的高分挑战。',
     'https://hextris.io/', 'embed', None, None,
     ['arcade', 'puzzle', 'casual'], ['街机', '反应', '高分', '六边形'],
     280, ['en', 'zh'], True, 'fork', '2026-10-01',
     {'licenseNote': '上游未附标准许可证文件，仅源码公开',
      'note': '仓库含 CNAME 指向 hextris.io，该域名为上游所有',
      'upstream': 'https://github.com/Hextris/Hextris'}),
    ('tower-game', 'Tower Game 叠塔', ['tower', '叠塔', '建塔'],
     '时机精准地叠放方块，塔越高越刺激。',
     'https://astrnox.github.io/tower_game/', 'embed', True, 'MIT',
     ['casual', 'arcade'], ['休闲', '单指', '时机', '叠塔'],
     195, ['en', 'zh'], True, 'fork', '2026-10-01',
     {'repo': 'https://github.com/astrnox/tower_game'}),
    ('plants-vs-zombies', '植物大战僵尸 H5', ['pvz', '植物大战僵尸', 'plants'],
     '经典塔防玩法的网页复刻版。',
     'https://astrnox.github.io/h5-game-plantsVSzombies/', 'embed', True, 'MIT',
     ['tower', 'strategy', 'casual'], ['塔防', '经典', '策略'],
     120, ['zh'], True, 'fork', '2026-10-01',
     {'repo': 'https://github.com/astrnox/h5-game-plantsVSzombies'}),
    ('trust', 'Trust', ['信任'],
     '独立的网页小游戏作品，自己写着玩的。',
     'https://astrnox.github.io/trust/', 'embed', True, 'CC0-1.0',
     ['casual'], ['休闲', '独立'],
     45, ['en', 'zh'], False, 'own', '2026-10-01', {}),
    ('temple-of-boom', 'Temple of Boom', ['temple', '神庙', 'boom'],
     '动作闯关类网页游戏。',
     'https://astrnox.github.io/temple-of-boom/', 'embed', True, None,
     ['action', 'arcade'], ['动作', '闯关'],
     20, ['en', 'zh'], True, 'fork', '2026-10-01',
     {'licenseNote': '上游未附标准许可证文件，仅源码公开'}),
    ('wordle-plus', 'Wordle Plus', ['wordle', '猜词', '单词'],
     '猜单词游戏，每行一词逐步逼近答案。',
     'https://astrnox.github.io/wordle-plus/', 'embed', True, None,
     ['word', 'puzzle'], ['文字', '猜词', '益智'],
     155, ['en', 'zh'], False, 'fork', '2026-10-01',
     {'licenseNote': '上游未附标准许可证文件，仅源码公开'}),
    ('odd-bot-out', 'Odd Bot Out', ['odd bot', '找出不同'],
     '从机器人堆里找出与众不同的那一个。',
     'https://astrnox.github.io/odd-bot-out/', 'embed', True, None,
     ['puzzle', 'casual'], ['观察', '益智', '找不同'],
     330, ['en', 'zh'], False, 'fork', '2026-10-01',
     {'licenseNote': '上游未附标准许可证文件，仅源码公开'}),
    ('bubble-shooter', 'Bubble Shooter 泡泡龙', ['bubble', '泡泡龙', '消泡泡'],
     '经典泡泡龙玩法，三消击破整片泡泡。',
     'https://astrnox.github.io/arkadiumx27s-bubble-shooter/', 'embed', True, None,
     ['arcade', 'puzzle'], ['街机', '消除', '经典'],
     265, ['en', 'zh'], False, 'fork', '2026-10-01',
     {'licenseNote': '上游未附标准许可证文件，仅源码公开',
      'repo': 'https://github.com/astrnox/arkadiumx27s-bubble-shooter'}),
    ('10-minutes-till-dawn', '10 Minutes Till Dawn', ['10 minutes', '黎明前十分钟'],
     '生存射击，在怪物潮中撑过十分钟。',
     'https://astrnox.github.io/10-minutes-till-dawn/', 'embed', True, None,
     ['shooter', 'action', 'survival'], ['射击', '生存', 'Roguelike'],
     250, ['en', 'zh'], True, 'fork', '2026-10-01',
     {'licenseNote': '上游未附标准许可证文件，仅源码公开'}),
    ('fcgame', 'FCGame · FC/NES 模拟器', ['fc', 'nes', '红白机', '模拟器'],
     '基于 JSNES 的网页模拟器，支持导入本地 ROM。',
     'https://github.com/astrnox/fcgame', 'redirect', False, 'GPL-3.0',
     ['retro', 'arcade'], ['模拟器', '红白机', '怀旧', 'ROM'],
     0, ['zh'], True, 'fork', '2026-10-01',
     {'note': '需先部署到 Pages/Docker；仅内置合规 Homebrew ROM，不内置商业 ROM'}),
    ('worldguessr', 'WorldGuessr 猜地理', ['worldguessr', '猜地图', 'geo'],
     '街景猜地点的地理问答游戏（需服务端）。',
     'https://github.com/astrnox/worldguessr', 'redirect', False, None,
     ['geo', 'casual'], ['地理', '猜谜', '街景'],
     205, ['en', 'zh'], False, 'fork', '2026-10-01',
     {'upstream': 'https://github.com/codergautam/worldguessr',
      'licenseNote': '上游许可证识别为 NOASSERTION',
      'note': 'Next.js + Node 服务端项目，GitHub Pages 无法直接运行'}),
    ('remake', 'Remake', ['重制'],
     'pnpm monorepo 前端项目，需构建后部署。',
     'https://github.com/astrnox/remake', 'redirect', False, 'MIT',
     ['casual'], ['待构建', 'monorepo'],
     175, ['en', 'zh'], False, 'own', '2026-10-01',
     {'note': '需 pnpm build 产出 dist 后才能部署'}),
    ('fluid-weiqi-web', 'Fluid 围棋', ['围棋', 'weiqi', 'go', 'fluid'],
     '围棋对战前端，含构建流程与服务端配置。',
     'https://github.com/astrnox/fluid-weiqi-web', 'redirect', False, None,
     ['board', 'strategy', 'tabletop'], ['围棋', '棋类', '对弈'],
     35, ['en', 'zh'], False, 'own', '2026-10-01',
     {'licenseNote': '仓库许可证识别为 NOASSERTION，需补充许可声明',
      'note': 'pnpm monorepo + vercel.json，需构建后部署到 Vercel'}),
    ('fight-the-landlord', '斗地主 AI 对战', ['斗地主', 'landlord', 'douzero'],
     'Go 后端驱动的斗地主，集成 DouZero AI。',
     'https://github.com/astrnox/fight-the-landlord', 'redirect', False, 'GPL-3.0',
     ['board', 'tabletop'], ['斗地主', 'AI', '棋牌'],
     355, ['zh'], False, 'fork', '2026-10-01',
     {'note': 'Go 后端项目（含 Dockerfile），需服务器运行，非纯前端'}),
]

# ---------------------------------------------------------------------------
# 构建
# ---------------------------------------------------------------------------

def build_own():
    """站主自己的游戏：id、上线地址、featured 全部沿用原样。"""
    out = []
    for (gid, title, alias, desc, url, mode, embed, lic, cats, tags,
         accent, langs, feat, source, added, extra) in OWN:
        g = {
            'id': gid,
            'title': title,
            'alias': alias,
            'desc': desc,
            'cover': f'assets/covers/{gid}.svg',
            'coverFrom': 'scene',
            'readmeLangs': {'default': langs[0], 'available': langs},
            'accent': accent,
            'category': cats,
            'tags': tags,
            'kind': 'web',
            'mode': mode,
            'embeddable': embed,
            'url': url,
            'repo': extra.get('repo', f'https://github.com/astrnox/{gid}'),
            'license': lic,
            'platform': ['web'],
            'players': extra.get('players', 2 if gid == 'fight-the-landlord' else 1),
            'featured': feat,
            'addedAt': added,
            'source': source,
            'status': 'active',
            'embedCheck': {'checkedAt': '2026-10-01', 'result': 'unknown'},
        }
        for k in ('licenseNote', 'note', 'upstream'):
            if k in extra:
                g[k] = extra[k]
        out.append({k: v for k, v in g.items() if v is not None})
    return out


def accent_from_id(gid):
    """稳定散列出色相，避免 id 顺序决定配色。"""
    h = 0
    for ch in gid:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return h % 360


def build_web():
    out = []
    for (gid, title, alias, desc, url, repo, lic, cats, tags,
         accent, embed, stars, pushed, extra) in WEB:
        g = {
            'id': gid,
            'title': title,
            'alias': alias,
            'desc': desc,
            'cover': f'assets/covers/{gid}.svg',
            'coverFrom': 'scene',
            'accent': accent,
            'category': cats,
            'tags': tags,
            'kind': 'web',
            'mode': 'embed' if embed else 'redirect',
            'embeddable': embed,
            'url': url,
            'repo': f'https://github.com/{repo}' if '/' in repo and not repo.startswith('http') else repo,
            'license': lic,
            'platform': ['web'],
            'players': extra.get('players', 1),
            'featured': extra.get('featured', False),
            'addedAt': TODAY,
            'source': 'upstream',
            'status': extra.get('status', 'active'),
            'stars': extra.get('stars', stars) or None,
            'pushedAt': pushed or None,
            'archived': extra.get('archived', False),
            'embedCheck': {'checkedAt': VERIFIED_AT,
                           'result': 'ok' if embed else 'blocked'},
        }
        for k in ('licenseNote', 'note', 'featured', 'players'):
            if k in extra:
                g[k] = extra[k]
        g = {k: v for k, v in g.items() if v is not None}
        out.append(g)
    return out


def build_download():
    out = []
    for (gid, title, alias, desc, repo, lic, cats, tags,
         accent, stars, pushed, plats, extra) in DOWNLOAD:
        files = []
        for p in plats.split(','):
            if not p:
                continue
            label = {'win': 'Windows', 'lin': 'Linux', 'mac': 'macOS',
                     'android': 'Android'}[p]
            files.append({'label': f'{label} 官方下载', 'platform': [p],
                          'url': f'https://github.com/{repo}/releases'})
        g = {
            'id': gid,
            'title': title,
            'alias': alias,
            'desc': desc,
            'cover': f'assets/covers/{gid}.svg',
            'coverFrom': 'scene',
            'accent': accent,
            'category': cats,
            'tags': tags,
            'kind': 'download',
            'mode': 'download',
            'embeddable': False,
            'repo': f'https://github.com/{repo}',
            'license': lic,
            'platform': sorted({f['platform'][0] for f in files},
                               key=lambda x: ['web', 'pc', 'mac', 'android', 'ios'].index(x)
                               if x in ['web', 'pc', 'mac', 'android', 'ios'] else 9),
            'downloads': files,
            'requirements': '需从源码或发行包安装，配置要求见项目主页',
            'players': 1,
            'featured': extra.get('featured', False),
            'addedAt': TODAY,
            'source': 'upstream',
            'status': extra.get('status', 'active'),
            'stars': stars or None,
            'pushedAt': pushed or None,
            'archived': extra.get('archived', False),
            'embedCheck': {'checkedAt': VERIFIED_AT, 'result': 'unknown'},
        }
        for k in ('licenseNote', 'note', 'assetNote'):
            if k in extra:
                g[k] = extra[k]
        g = {k: v for k, v in g.items() if v is not None}
        out.append(g)
    return out


# 实测可内嵌的自托管地址（其余 36 款官方 play 页禁嵌，需 fork 后自托管）
JS13K_HOSTED = {
    'neptune-blue': 'https://js13kgames.github.io/neptune-blue/',
    'wind-rider':   'https://js13kgames.github.io/wind-rider/',
}


def build_js13k():
    out = []
    for (gid, title, alias, desc, lic, cats, tags, accent, _x) in JS13K:
        hosted = JS13K_HOSTED.get(gid)
        out.append({
            'id': f'js13k-{gid}',
            'title': title,
            'alias': alias + ['js13k'],
            'desc': desc,
            'cover': f'assets/covers/js13k-{gid}.svg',
            'coverFrom': 'scene',
            'accent': accent,
            'category': cats,
            'tags': tags + ['js13k', '13KB'],
            'kind': 'web',
            'mode': 'embed' if hosted else 'redirect',
            'embeddable': bool(hosted),
            'url': hosted or f'https://play.js13kgames.com/{gid}/',
            'repo': f'https://github.com/js13kGames/{gid}',
            'upstream': f'https://github.com/js13kGames/{gid}',
            'license': lic,
            'platform': ['web'],
            'players': 1,
            'featured': False,
            'addedAt': TODAY,
            'source': 'upstream',
            'status': 'active',
            'embedCheck': {'checkedAt': VERIFIED_AT,
                           'result': 'ok' if hosted else 'blocked'},
            **({'note': '官方 play 页禁止内嵌（frame-ancestors 只放行 js13kgames.com），'
                        '需 fork 自托管后才能站内直接玩'} if not hosted else {}),
        })
    return out


def validate(games):
    errs = []
    ids = set()
    known_cats = {c[0] for c in CATEGORIES}
    # 只认 LICENSES 里真登记过的 id。裸 'GPL' 不是 SPDX 标识，不放行——
    # 要么写 GPL-2.0/GPL-3.0，要么写 None 表示仓库里没找到许可证文件。
    known_lic = {l[0] for l in LICENSES} | {'NetHack-PL'}
    for g in games:
        if g['id'] in ids:
            errs.append(f"重复 id: {g['id']}")
        ids.add(g['id'])
        if not re.match(r'^[a-z0-9][a-z0-9-]*$', g['id']):
            errs.append(f"id 不合规: {g['id']}")
        if len(g.get('desc', '')) > 80:
            errs.append(f"desc 超 80 字: {g['id']} ({len(g['desc'])})")
        for c in g.get('category', []):
            if c not in known_cats:
                errs.append(f"未知分类 {c}: {g['id']}")
        if g.get('license') and g['license'] not in known_lic:
            errs.append(f"未知许可证 {g['license']}: {g['id']}")
        if g['kind'] == 'download' and not g.get('downloads'):
            errs.append(f"download 类缺 downloads: {g['id']}")
        if g['kind'] == 'web' and not g.get('url'):
            errs.append(f"web 类缺 url: {g['id']}")
        if g['mode'] == 'embed' and g.get('embeddable') is False:
            errs.append(f"标 embed 但 embeddable=false: {g['id']}")
        for p in g.get('platform', []):
            if p not in KNOWN_PLATFORMS:
                errs.append(f"未知平台 {p}: {g['id']}")
        if not (ROOT / g['cover']).exists():
            errs.append(f"封面文件不存在: {g['id']} -> {g['cover']}")
    return errs


def main():
    games = build_own() + build_web() + build_download() + build_js13k()
    errs = validate(games)
    if errs:
        print('校验未通过:')
        for e in errs:
            print('  ✗', e)
        raise SystemExit(1)

    doc = {
        '$schema': './games.schema.json',
        'version': 3,
        'owner': 'astrnox',
        'updatedAt': TODAY,
        'categories': [{'id': i, 'name': n} for i, n in CATEGORIES],
        'licenses': [
            {'id': i, 'name': n, 'url': u, 'commercial': c,
             'shareAlike': s, 'network': n}
            for i, n, u, c, s, n in LICENSES
        ],
        'games': games,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    web = sum(1 for g in games if g['kind'] == 'web')
    dl = len(games) - web
    no_lic = sum(1 for g in games if not g.get('license'))
    arch = sum(1 for g in games if g.get('archived'))
    print(f'✓ {OUT.relative_to(ROOT)}  {len(games)} 款'
          f'（网页 {web} / 需下载 {dl}）')
    print(f'  分类 {len(CATEGORIES)} 个 · 无许可证 {no_lic} 款 · 已归档 {arch} 款 · '
          f'文件 {OUT.stat().st_size // 1024}KB')


if __name__ == '__main__':
    main()
