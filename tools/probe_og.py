#!/usr/bin/env python3
"""实测路线 B：抓在线入口的 og:image / twitter:image（真实画面通常在这里）。

同时尝试 js13k 仓库的 README（换几种路径写法）。
"""
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'

SITES = [
    'https://mindustrygame.github.io/',
    'https://freecivweb.org/',
    'https://transport-tycoon.k3.demos.sulat.com/',
    'https://play.rosebud.ai/play/unciv-base',
    'https://ancientbeast.com/',
    'https://1255.areso.pro/',
    'https://lo-th.github.io/3d.city/',
    'https://pixel-dungeon.com/',
    'https://crawl.develz.org/play.htm',
    'https://nethack.alt.org/',
    'https://angband.live/',
    'https://adarkroom.doublespeakgames.com/',
    'https://candybox2.github.io/',
    'https://ellisonleao.github.io/clumsy-bird/',
    'https://duckhuntjs.com/',
    'https://basicallydan.github.io/skifree.js/',
    'https://cykod.github.io/AlienInvasion/',
    'https://breakout.lecaro.me/',
    'https://lutzroeder.com/html5/digger/',
    'https://ondras.github.io/custom-tetris/',
    'https://kuberwastaken.github.io/backdooms/',
    'https://enclavegames.com/games/captain-rogers/',
    'https://danbeck.github.io/green-mahjong/',
    'https://kenrick95.github.io/c4/',
    'https://mitallast.github.io/diablo-js/',
    'https://itajaja.github.io/hb/',
    'https://alexnisnevich.github.io/untrusted/',
    'https://wenta.github.io/rapid-dominance/',
    'https://hexgl.bkcore.com/',
    'https://wwwtyro.github.io/Astray/',
    'https://anirudhjoshi.github.io/fluid_table_tennis/',
    'https://jfd.github.io/wpilot/',
    'https://bemuse.ninja/',
    'https://play.bgammon.org/',
]

BAD = re.compile(r'(badge|shields\.io|herokucdn|gravatar|favicon|logo|icon|avatar|emoji)', re.I)


def curl(url, extra=None, timeout=15):
    cmd = ['curl', '-sL', '--max-time', str(timeout), '-A', UA]
    if extra:
        cmd += extra
    cmd.append(url)
    p = subprocess.run(cmd, capture_output=True)
    return p.stdout


def probe(site):
    try:
        html = curl(site).decode('utf-8', 'ignore')
    except Exception:
        return site, None, 'fetch-fail'
    if len(html) < 200:
        return site, None, f'too-small({len(html)})'
    cands = []
    for pat in [r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
                r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)']:
        cands += re.findall(pat, html, re.I)
    for u in cands:
        u = u.strip()
        if u.startswith('//'):
            u = 'https:' + u
        elif u.startswith('/'):
            m = re.match(r'(https?://[^/]+)', site)
            u = m.group(1) + u
        if BAD.search(u):
            continue
        head = curl(u, ['-I']).decode('utf-8', 'ignore')
        mt = re.search(r'content-type:\s*(image/[a-z]+)', head, re.I)
        cl = re.search(r'content-length:\s*(\d+)', head, re.I)
        if mt:
            kb = int(cl.group(1)) // 1024 if cl else 0
            if kb < 40:      # 太小多半是图标
                continue
            return site, u, f'{mt.group(1)} {kb}KB'
    return site, None, f'no-og(len={len(html)})'


with ThreadPoolExecutor(max_workers=10) as ex:
    res = list(ex.map(probe, SITES))

ok = [r for r in res if r[1]]
print(f'=== og:image 命中 {len(ok)}/{len(SITES)} ===')
for s, u, i in ok:
    print(f'  OK  {s:52s} {i:18s} {u[:88]}')
print('--- 未命中 ---')
for s, u, i in res:
    if not u:
        print(f'  --  {s:52s} {i}')
