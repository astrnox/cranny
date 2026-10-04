#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为全部游戏生成封面 SVG。

封面来源优先级（用户指定）：
  1. README 里的现成图  —— 实测 4/29 命中且 2 个误报，此路不通
  2. 在线站实际画面     —— 实测 og:image 3/34 命中且多为 logo，不可用
  3. 字母 / 机制意象    —— 采用此方案

为什么不用大字母：113 张首字母排在一起像密码表。
改用「机制母题」—— 每个游戏挑一个代表玩法的几何构图
（方块阵、六边形塔、细胞、星场、声波、地形、卡牌、管道…），
按 category 定色系，同类型有视觉家族感又互不重复。

两个 SVG-as-image 的坑（踩中会整张图变黑）：
  - 不要用 mix-blend-mode：SVG 以 <img> 加载时混合模式失效
  - <stop> 的 stop-opacity 缺省值是 1，不是 0；必须显式写 0 才是透明
"""
import hashlib
import json
import math
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / 'data' / 'games.json'
OUT = ROOT / 'assets' / 'covers'
W, H = 400, 300

# 按主分类取色相区间：暖向多彩、避开蓝紫（与站点主色系一致）
CAT_HUE = {
    'puzzle': (26, 44),    'casual': (148, 186),
    'action': (6, 30),     'arcade': (330, 358),
    'strategy': (196, 224), 'board': (36, 50),
    'shooter': (348, 14),  'io': (184, 206),
    'sports': (76, 100),   'retro': (16, 40),
    'word': (138, 166),    'geo': (166, 188),
    'survival': (94, 128), 'rpg': (18, 40),
    'tabletop': (40, 56),  'music': (284, 320),
    'racing': (16, 38),    'sim': (170, 196),
    'sandbox': (108, 140), 'tower': (132, 162),
}


def hue_range(cats, accent, gid=''):
    """给每款游戏一个稳定的色相窗口。

    关键：色相不能只由分类决定。母题的随机种子是从 h1 算出来的，
    如果同一分类里 12 款游戏共用一个色相，它们会画出几乎一样的画面
    （曾经 strategy 一片蓝，滚动过去像复制粘贴）。
    所以这里用 id 的稳定哈希在分类色带内散开，
    既保住「同分类颜色相近」的整体感，又保证每张封面都不一样。
    """
    lo, hi = CAT_HUE.get((cats or ['casual'])[0], (200, 230))
    shift = ((accent or 0) % 22) - 11          # ±11° 细微偏移
    h = hashlib.md5(gid.encode('utf-8')).digest()
    # 黄金角步进：相邻 id 也能散得开，不会扎堆
    jitter = (int.from_bytes(h[:4], 'big') / 0xFFFFFFFF - 0.5) * (hi - lo) * 0.92
    base = lo + (hi - lo) / 2 + jitter
    span = max(6.0, (hi - lo) * 0.30)          # 带宽 8°~18°，够画渐变又不会跑出分类色
    return (base - span / 2 + shift) % 360, (base + span / 2 + shift) % 360


# ---------------------------------------------------------------------------
# 颜色
#
# 不要在 SVG 里写 hsl(196 44% 20%) 这种空格分隔的现代语法：
# cairosvg 直接输出黑色，浏览器兼容性也不稳。统一转成 hex。
# ---------------------------------------------------------------------------
import colorsys


def hsl(h, s, l):
    """hsl -> #rrggbb。h 会被取模，s/l 按 0-100 处理。"""
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360.0, l / 100.0, s / 100.0)
    return '#%02x%02x%02x' % (round(r * 255), round(g * 255), round(b * 255))


def _stops(stops):
    """接受 (offset, color) 或 (offset, color, alpha) 两种写法。"""
    out = []
    for st in stops:
        o, c = st[0], st[1]
        a = st[2] if len(st) > 2 else None
        out.append(f'<stop offset="{o}" stop-color="{c}"'
                   + (f' stop-opacity="{a}"' if a is not None else '') + '/>')
    return ''.join(out)


def lin(gid, stops, x1='0', y1='0', x2='0', y2='1'):
    return (f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
            f'{_stops(stops)}</linearGradient>')


def rad(gid, stops, cx='0.5', cy='0.42', r='0.78'):
    return (f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}">'
            f'{_stops(stops)}</radialGradient>')


NOISE = ('<filter id="nz"><feTurbulence type="fractalNoise" baseFrequency="0.85" '
         'numOctaves="3" stitchTiles="stitch"/>'
         '<feColorMatrix type="saturate" values="0"/></filter>')

# 暗角：中心 stop-opacity 必须显式写 0，否则中心半张图是纯黑
VIGNETTE = rad('vg', [(0.45, '#000', 0), (0.78, '#000', 0.10), (1, '#000', 0.34)],
               cy='0.4', r='0.82')
# 底部压暗，给标题留可读区域
FADE = lin('fd', [(0, '#000', 0), (0.58, '#000', 0.12), (1, '#000', 0.62)])

GRAIN = (f'<rect width="{W}" height="{H}" filter="url(#nz)" opacity="0.045"'
         ' style="mix-blend-mode:normal"/>')


# ---------------------------------------------------------------------------
# 场景母题。统一签名 fn(h1, h2) -> [svg 片段]
# ---------------------------------------------------------------------------
def sc_grid(h1, h2):
    """方块阵：数字合成、消除、俄罗斯方块"""
    # 8 个格子排布有多种，这里按 h1 换一套，避免同色相下每张图一模一样
    layouts = [
        [(0, 0, 0), (1, 1, 0), (0, 2, 1), (2, 0, 3),
         (1, 3, 2), (2, 2, 0), (3, 1, 1), (3, 3, 3)],
        [(0, 1, 0), (1, 0, 1), (2, 1, 2), (3, 0, 3),
         (0, 3, 3), (1, 2, 0), (2, 3, 1), (3, 2, 2)],
        [(0, 0, 1), (1, 0, 0), (0, 1, 2), (1, 1, 3),
         (2, 2, 2), (3, 2, 0), (2, 3, 1), (3, 3, 3)],
        [(1, 0, 0), (0, 1, 1), (1, 1, 2), (2, 0, 3),
         (0, 2, 3), (1, 3, 1), (2, 2, 2), (3, 3, 0)],
    ]
    out, n, cell, gap = [], 4, 40, 8
    ox, oy = (W - (n * cell + (n - 1) * gap)) / 2, H / 2 - 96
    fills = [f'{hsl(h1, 62, 58)}', f'{hsl(h2, 55, 46)}',
             f'{hsl(h1, 42, 32)}', f'{hsl(h2, 40, 70)}']
    pat = layouts[int(h1) % len(layouts)]
    for x, y, c in pat:
        px, py = ox + x * (cell + gap), oy + y * (cell + gap)
        out.append(f'<rect x="{px:.0f}" y="{py:.0f}" width="{cell}" height="{cell}" '
                   f'rx="6" fill="{fills[c]}" opacity="{0.94 if (x + y) % 2 == 0 else 0.78}"/>')
        out.append(f'<rect x="{px:.0f}" y="{py:.0f}" width="{cell}" height="{cell}" '
                   f'rx="6" fill="none" stroke="#fff" stroke-opacity="0.16"/>')
    return out


def sc_hex(h1, h2):
    """六边形塔：六边形消除、落塔"""
    out, r = [], 26
    # 三种铺法轮换，否则同色相的六边形图会一模一样
    style = int(h1) % 3
    for row in range(4):
        for col in range(5):
            cx = W / 2 + (col - 2) * r * 1.74 + (r * 0.87 if row % 2 else 0)
            cy = 74 + row * r * 1.5
            if style == 0:
                f = h1 if (row + col) % 3 == 0 else (h2 if (row + col) % 3 == 1 else h1 + 18)
            elif style == 1:
                f = h2 if (row * col) % 3 == 0 else (h1 if (row + col) % 2 else h2 + 22)
            else:
                f = h1 if (row + 2 * col) % 4 < 2 else h2
            pts = ' '.join(f'{cx + r * math.cos(math.radians(a)):.1f},'
                           f'{cy + r * math.sin(math.radians(a)):.1f}'
                           for a in range(-90, 270, 60))
            out.append(f'<polygon points="{pts}" fill="{hsl(f, 55, 52 - row * 5)}" '
                       f'fill-opacity="0.9" stroke="#fff" '
                       f'stroke-opacity="0.18" stroke-width="1.5"/>')
    return out


def sc_tower(h1, h2):
    """塔防：底座 + 炮塔 + 弹道"""
    rnd = random.Random(int(h1) * 7717 + int(h2))
    out = [f'<rect x="46" y="196" width="308" height="10" rx="3" '
           f'fill="{hsl(h2, 30, 26)}"/>']
    # 炮塔数量与位置随机，2~4 座
    spots = [110 + i * 62 for i in range(4) if rnd.random() > 0.28][:4] or [200]
    for i, x in enumerate(spots):
        hh = 46 + rnd.uniform(0, 44)
        out += [
            f'<rect x="{x - 22}" y="{196 - hh:.0f}" width="44" height="{hh:.0f}" rx="4" '
            f'fill="{hsl(h1, 48, 34 + i * 4)}" stroke="#fff" stroke-opacity="0.15"/>',
            f'<circle cx="{x}" cy="{196 - hh - 10:.0f}" r="9" fill="{hsl(h2, 68, 58)}"/>',
            f'<path d="M{x - 8} {196 - hh - 14:.0f} L{x + 26} {196 - hh - 34:.0f} '
            f'L{x + 27} {196 - hh - 24:.0f} L{x - 6} {196 - hh - 4:.0f} Z" '
            f'fill="{hsl(h2, 70, 62)}" opacity="0.85"/>']
    for i in range(5):
        out.append(f'<circle cx="{58 + i * 14}" cy="{112 + (i % 3) * 12}" r="5" '
                   f'fill="{hsl(h1, 72, 62)}" opacity="{0.75 - i * 0.09:.2f}"/>')
    return out


def sc_cell(h1, h2):
    """细胞：roguelike、地牢、有机质感"""
    rnd = random.Random(int(h1) * 7919 + int(h2))
    out = []
    for _ in range(13):
        cx, cy = rnd.uniform(50, W - 50), rnd.uniform(56, H - 74)
        r = rnd.uniform(16, 46)
        col = h1 if rnd.random() > 0.4 else h2
        out.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" '
                   f'fill="{hsl(col, 58, rnd.randint(28, 56))}" '
                   f'opacity="{rnd.uniform(0.34, 0.7):.2f}" stroke="#fff" '
                   f'stroke-opacity="0.13"/>')
    return out


def sc_star(h1, h2):
    """星场：太空、弹幕、射击"""
    rnd = random.Random(int(h2) * 6271 + int(h1))
    out = []
    for _ in range(64):
        out.append(f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(0, H - 60):.0f}" '
                   f'r="{rnd.uniform(0.8, 2.6):.1f}" fill="#fff" '
                   f'opacity="{rnd.uniform(0.18, 0.78):.2f}"/>')
    out += [
        f'<circle cx="200" cy="150" r="62" fill="none" stroke="{hsl(h1, 70, 60)}" '
        f'stroke-opacity="0.2"/>',
        f'<polygon points="200,150 178,198 200,187 222,198" fill="{hsl(h1, 78, 62)}" '
        f'stroke="#fff" stroke-opacity="0.4"/>']
    for i, (dx, dy) in enumerate(((-84, -34), (86, -30), (-70, 22), (74, 24))):
        out.append(f'<rect x="{200 + dx - 8}" y="{150 + dy - 8}" width="16" height="16" '
                   f'fill="{hsl((h2 + i * 20) % 360, 66, 54)}" opacity="0.9" '
                   f'transform="rotate(45 {200 + dx} {150 + dy})"/>')
    return out


def sc_wave(h1, h2):
    """声波：音乐节奏"""
    rnd = random.Random(int(h1) * 4409 + int(h2) * 17)
    out, n, gap = [], 24, 6
    bw = (W - 100 - (n - 1) * gap) / n
    for i in range(n):
        amp = 12 + abs(math.sin(i * 0.55)) * 78 * rnd.uniform(0.55, 1.0)
        out.append(f'<rect x="{50 + i * (bw + gap):.1f}" y="{(H - 62 - amp) / 2:.1f}" '
                   f'width="{bw:.1f}" height="{amp:.1f}" rx="3" '
                   f'fill="{hsl(h1 + i * 3, 66, 58 - (i % 3) * 8)}" '
                   f'opacity="{0.6 + (i % 3) * 0.15:.2f}"/>')
    return out


def sc_terrain(h1, h2):
    """地形：竞速、地理、运动"""
    rnd = random.Random(int(h2) * 3571 + int(h1) * 13)
    out = []
    for layer in range(4):
        base = 128 + layer * 30
        pts, step = [], 26
        for x in range(-10, W + 20, step):
            y = (base - abs(math.sin(x * 0.013 + layer * 1.6)) * (56 - layer * 8)
                 - rnd.uniform(0, 16))
            pts.append(f'{x},{y:.0f}')
        pts += [f'{W + 20},{H}', f'-10,{H}']
        col = h1 if layer % 2 == 0 else h2
        out.append(f'<polygon points="{" ".join(pts)}" '
                   f'fill="{hsl(col, 42, 30 + layer * 8)}" '
                   f'opacity="{0.55 + layer * 0.13:.2f}"/>')
    out.append(f'<circle cx="308" cy="72" r="26" fill="{hsl((h2 + 30) % 360, 74, 64)}" '
               f'opacity="0.85"/>')
    return out


def sc_cards(h1, h2):
    """扇形卡牌：棋牌、桌游"""
    rnd = random.Random(int(h1) * 6421 + int(h2))
    out = []
    # 张数 3~6、展开角、卡背花纹都随机
    n = rnd.randint(3, 6)
    span = rnd.uniform(9, 17)
    for i in range(n):
        a = -span + (2 * span * i / (n - 1) if n > 1 else 0)
        cx, cy = W / 2, 218
        col = h1 if i % 2 == 0 else h2
        # 中间几张更高，形成扇形的层次
        lift = int(abs(i - (n - 1) / 2) * -7)
        out.append(f'<g transform="rotate({a:.1f} {cx} {cy})">'
                   f'<rect x="{cx - 30}" y="{cy - 92 + lift}" width="60" height="88" rx="6" '
                   f'fill="{hsl(col, 46, 88 - i * 3)}" stroke="#fff" '
                   f'stroke-opacity="0.22"/>'
                   f'<circle cx="{cx}" cy="{cy - 48 + lift}" r="9" '
                   f'fill="{hsl((col + 40) % 360, 60, 62)}" opacity="0.7"/></g>')
    return out


def sc_pipes(h1, h2):
    """管道：工厂、流水线、自动化"""
    rnd = random.Random(int(h1) * 4231 + int(h2))
    out = []
    rows = rnd.randint(3, 5)
    bend = rnd.choice((150, 176, 200))          # 拐弯位置
    for i in range(rows):
        y = 70 + i * (140 / max(1, rows - 1)) if rows > 1 else 120
        col = h1 if i % 2 == 0 else h2
        out += [
            f'<path d="M40 {y:.0f} H{bend} Q{bend + 16} {y:.0f} {bend + 16} '
            f'{y + 16:.0f} V{H - 96} '
            f'Q{bend + 16} {H - 80} {bend + 32} {H - 80} H360" fill="none" '
            f'stroke="{hsl(col % 360, 50, 50)}" stroke-width="9" '
            f'stroke-linecap="round" opacity="0.82"/>',
            f'<circle cx="{bend}" cy="{y:.0f}" r="7" fill="{hsl(col % 360, 70, 64)}"/>',
            f'<circle cx="{bend + 16}" cy="{y + 30:.0f}" r="11" fill="none" stroke="#fff" '
            f'stroke-opacity="0.24" stroke-width="2"/>']
    return out


def sc_city(h1, h2):
    """等高方块：城市、经营、建造"""
    # 种子同时吃 h1 和 h2：strategy 有 12 款挤这个母题，只用 h1 会撞图
    rnd = random.Random(int(h1) * 5171 + int(h2) * 131)
    out, n, gap = [], 8, 5
    cw = (W - 100 - (n - 1) * gap) / n
    # 每栋楼的相位错开，高度差更自然
    phase = rnd.uniform(0, 6.28)
    for x in range(n):
        hh = 20 + abs(math.sin(x * 0.8 + phase)) * 92 + rnd.uniform(0, 26)
        px = 50 + x * (cw + gap)
        col = h1 if x % 3 else h2
        out += [
            f'<rect x="{px:.1f}" y="{196 - hh:.0f}" width="{cw:.1f}" height="{hh:.0f}" '
            f'rx="3" fill="{hsl(col, 46, 32 + (x % 4) * 9)}" stroke="#fff" '
            f'stroke-opacity="0.13"/>',
            f'<rect x="{px + cw * 0.28:.1f}" y="{196 - hh + 9:.0f}" '
            f'width="{cw * 0.44:.0f}" height="5" rx="2" fill="#fff" opacity="0.26"/>']
    return out


def sc_maze(h1, h2):
    """网格推理：谜题、文字、数独"""
    rnd = random.Random(int(h1) * 9133 + int(h2) * 7)
    # 墙体密度和断点规则随机，否则同色相下每张迷宫图完全一致
    wall_h, wall_v = rnd.choice((3, 4, 5)), rnd.choice((3, 4, 5))
    ox, oy = 52, 58
    out, cell = [], 24
    for row in range(7):
        for col in range(12):
            x, y = ox + col * cell, oy + row * cell
            horiz = (row * 12 + col) % wall_h != 0
            out += [
                f'<rect x="{x}" y="{y + cell / 2 - 1.5:.0f}" width="{cell}" height="3" '
                f'fill="{hsl(h1 if horiz else h2, 52, 44 + ((row + col) % 4) * 10)}" '
                f'opacity="0.8"/>']
            if (row * 12 + col) % wall_v != 0:
                out.append(
                    f'<rect x="{x + cell / 2 - 1.5:.0f}" y="{y}" width="3" '
                    f'height="{cell}" fill="{hsl(h2, 46, 38 + ((row * col) % 3) * 12)}" '
                    f'opacity="0.6"/>')
    out += [f'<circle cx="56" cy="62" r="7" fill="{hsl(h1, 78, 62)}"/>',
            f'<circle cx="336" cy="218" r="7" fill="{hsl(h2, 78, 58)}"/>']
    return out


def sc_bullet(h1, h2):
    """横向弹幕：射击专用。比 sc_star 更有方向感"""
    rnd = random.Random(int(h1) * 3301 + int(h2) * 29)
    out = []
    for i in range(22):
        x = 40 + (i * 37) % (W - 80)
        y = 60 + (i * 53) % (H - 120)
        r = 3 + (i % 3)
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{hsl(h2, 70, 62)}" '
                   f'opacity="{0.9 - i * 0.03:.2f}"/>')
    # 玩家战机 + 一排弹幕
    out += [
        f'<polygon points="62,150 30,138 30,162" fill="{hsl(h1, 74, 60)}" '
        f'stroke="#fff" stroke-opacity="0.35"/>',
        f'<rect x="86" y="142" width="230" height="3" fill="{hsl(h2, 60, 50)}" '
        f'opacity="0.3"/>',
        f'<circle cx="200" cy="150" r="54" fill="none" stroke="{hsl(h1, 68, 58)}" '
        f'stroke-opacity="0.18"/>']
    for i in range(4):
        out.append(f'<rect x="{110 + i * 62}" y="{136 + (i % 2) * 20}" width="14" '
                   f'height="14" rx="2" fill="{hsl(h1, 72, 58)}" '
                   f'transform="rotate(45 {117 + i * 62} {143 + (i % 2) * 20})" '
                   f'opacity="0.9"/>')
    return out


def sc_platform(h1, h2):
    """平台跳跃：台阶 + 跳跃弧线"""
    rnd = random.Random(int(h1) * 5501 + int(h2) * 3)
    out = [
        f'<rect x="0" y="212" width="{W}" height="8" fill="{hsl(h2, 32, 22)}"/>']
    # 台阶数量与高度随机
    n = rnd.randint(4, 6)
    step = 300 / n
    for i in range(n):
        px = 24 + i * step
        ph = 20 + rnd.uniform(0, 42)
        out.append(f'<rect x="{px:.0f}" y="{212 - ph:.0f}" width="{step * 0.68:.0f}" '
                   f'height="{ph:.0f}" rx="3" '
                   f'fill="{hsl(h1, 42, 30 + i * 6)}" stroke="#fff" stroke-opacity="0.14"/>')
    # 跳跃轨迹：从第一阶跨到最后一阶
    x0, x1 = 24 + step * 0.3, 24 + (n - 1) * step * 0.3
    out.append(f'<path d="M{x0:.0f} 150 Q{(x0 + x1) / 2:.0f} {rnd.uniform(60, 96):.0f} '
               f'{x1:.0f} 140" fill="none" stroke="{hsl(h2, 72, 62)}" '
               f'stroke-width="3" stroke-dasharray="7 6" opacity="0.7"/>')
    out += [
        f'<circle cx="{x0:.0f}" cy="150" r="10" fill="{hsl(h1, 76, 60)}"/>',
        f'<circle cx="{x1:.0f}" cy="140" r="12" fill="{hsl(h2, 78, 62)}" stroke="#fff" '
        f'stroke-opacity="0.35"/>',
        f'<rect x="{x1 - 14:.0f}" y="54" width="30" height="30" rx="4" '
        f'fill="{hsl(h1, 50, 40)}" stroke="#fff" stroke-opacity="0.2"/>',
        f'<path d="M{x1 - 8:.0f} 70h18M{x1 + 1:.0f} 61v18" stroke="{hsl(h1, 80, 66)}" '
        f'stroke-width="3" stroke-linecap="round"/>']
    return out


# 母题选择：关键词优先（比分类更准），否则按分类
MOTIF_BY_KEY = [
    # 这些要先判，否则会被下面更宽泛的规则抢走
    (r'平台|跳跃|爬行', sc_platform),
    (r'弹幕|卷轴|射击|FPS|shoot|gun', sc_bullet),
    (r'塔防|炮战|守卫|tower ?defen|守塔', sc_tower),
    (r'工厂|流水线|automation|mindustry|自动化', sc_pipes),
    (r'音乐|节奏|音|谱|music|rhythm', sc_wave),
    (r'棋|麻将|卡牌|card|骰|board', sc_cards),
    (r'太空|星际|space|行星', sc_star),
    (r'赛车|竞速|race|racing|漂移|滑雪', sc_terrain),
    (r'迷宫|maze|数独|sudoku|猜词|wordle', sc_maze),
    (r'地牢|爬行|roguelike|生存|survival', sc_cell),
    (r'城市|city|建造|经营|模拟|sim|策略', sc_city),
    (r'消除|合成|2048|俄罗斯|tetris|方块|叠塔', sc_grid),
    (r'六边|hex', sc_hex),
    (r'益智|puzzle|推理', sc_maze),
]
MOTIF_BY_CAT = {
    'puzzle': sc_maze, 'casual': sc_grid, 'action': sc_bullet,
    'arcade': sc_hex, 'strategy': sc_city, 'board': sc_cards,
    'shooter': sc_bullet, 'io': sc_hex, 'sports': sc_terrain,
    'retro': sc_grid, 'word': sc_maze, 'geo': sc_terrain,
    'survival': sc_cell, 'rpg': sc_cell, 'tabletop': sc_cards,
    'music': sc_wave, 'racing': sc_terrain, 'sim': sc_city,
    'sandbox': sc_hex, 'tower': sc_tower,
}


def pick_scene(game):
    text = ' '.join([game.get('title', ''), ' '.join(game.get('tags') or [])])
    for pat, fn in MOTIF_BY_KEY:
        if re.search(pat, text, re.I):
            return fn
    return MOTIF_BY_CAT.get((game.get('category') or ['casual'])[0], sc_grid)


def build(game):
    gid = game['id']
    safe = gid.replace('-', '')
    h1, h2 = hue_range(game.get('category'), game.get('accent'), gid)
    bg = lin(f'b{safe}', [(0, hsl(h1, 44, 20)), (1, hsl(h2, 48, 12))])
    glow = rad(f'g{safe}',
               [(0, hsl(h1, 78, 56), 0.32), (1, hsl(0, 0, 0), 0)],
               cx='0.62', cy='0.3', r='0.7')
    body = pick_scene(game)(h1, h2)

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}" aria-hidden="true">'
            f'<defs>{bg}{glow}{VIGNETTE}{FADE}{NOISE}</defs>'
            f'<rect width="{W}" height="{H}" fill="url(#b{safe})"/>'
            f'<rect width="{W}" height="{H}" fill="url(#g{safe})"/>'
            f'{"".join(body)}'
            f'<rect width="{W}" height="{H}" fill="url(#vg)"/>'
            f'<rect y="{H * 0.6:.0f}" width="{W}" height="{H * 0.4:.0f}" fill="url(#fd)"/>'
            f'{GRAIN}'
            f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" '
            f'fill="none" stroke="#000" stroke-opacity="0.16"/>'
            f'</svg>')


def main():
    doc = json.loads(GAMES.read_text(encoding='utf-8'))
    games = doc['games']
    OUT.mkdir(parents=True, exist_ok=True)
    for stale in OUT.glob('*.svg'):
        stale.unlink()            # 清掉上一轮 15 张，避免孤儿文件残留

    for g in games:
        (OUT / f'{g["id"]}.svg').write_text(build(g), encoding='utf-8')

    report_dupes(games)
    print(f'✓ 生成 {len(games)} 张封面 → {OUT.relative_to(ROOT)}')


def report_dupes(games):
    """相邻封面长得一样是这站最难看的失败模式，这里主动量一下。

    判重不比对像素（渐变和噪点会让任何两张都略有差异，没意义），
    而是看「母题 + 主色相」这个组合：撞了就说明随机化没生效。
    """
    buckets = {}
    for g in games:
        fn = pick_scene(g)
        h1, _ = hue_range(g.get('category'), g.get('accent'), g['id'])
        buckets.setdefault((fn.__name__, round(h1 / 12)), []).append(g['id'])
    worst = sorted(buckets.values(), key=len, reverse=True)[:3]
    for ids in worst:
        if len(ids) > 2:
            print(f'  ! 母题+色相撞车 {len(ids)} 款: {", ".join(ids[:6])}'
                  f'{"…" if len(ids) > 6 else ""}')
    uniq = len({build(g) for g in games})
    print(f'  唯一画面 {uniq}/{len(games)}'
          + (' ✓' if uniq == len(games) else ' ✗ 有重复'))


if __name__ == '__main__':
    main()
