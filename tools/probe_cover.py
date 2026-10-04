#!/usr/bin/env python3
"""实测：从各开源项目的 README / 仓库元数据里抓真实截图 URL。

策略（按可靠性排序）：
  1. 仓库里的 og:image / social preview（GitHub 自动生成，尺寸稳定 1280x640）
  2. README 正文里的 <img>（排除 badge / 徽章 / 头像 / 动画）
  3. 站点首页的 og:image

只要抓到就说明这条路可行。
"""
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

TOKEN = open('/tmp/tok').read().strip()
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'

# 只测一部分，验证可行性
REPOS = [
    'Anuken/Mindustry', 'freeciv/freeciv-web', 'OpenTTD/OpenTTD', 'yairm210/Unciv',
    'FreezingMoon/AncientBeast', 'Areso/1255-burgomaster', 'lo-th/3d.city',
    '00-Evan/shattered-pixel-dungeon', 'crawl/crawl', 'NetHack/NetHack',
    'angband/angband', 'doublespeakgames/adarkroom',
    'gabrielecirulli/2048', 'candybox2/candybox2.github.io', 'ellisonleao/clumsy-bird',
    'MattSurabian/DuckHunt-JS', 'basicallydan/skifree.js', 'cykod/AlienInvasion',
    'ondras/custom-tetris', 'wwwtyro/Astray', 'BKcore/HexGL',
    'mitallast/diablo-js', 'AlexNisnevich/untrusted', 'itajaja/hb',
    'js13kGames/asdf', 'js13kGames/bouncing-button', 'js13kGames/chem-fight',
    'js13kGames/spacepi', 'js13kGames/terraform',
]

BAD_IMG = re.compile(
    r'(badge|shields\.io|img\.shields|travis|circleci|coveralls|'
    r'github\.com/user|githubusercontent\.com/[^/]+/\d+\?|'
    r'opencollective|patreon|paypal|ko-fi|discord\.gg|'
    r'\.gif|\.svg|emoji|logo|avatar|sponsor|contrib|wishlist)', re.I)


def api_get(path):
    p = subprocess.run(['curl', '-s', '--max-time', '18', '-H', f'Authorization: Bearer {TOKEN}',
                        '-H', 'Accept: application/vnd.github+json',
                        f'https://api.github.com{path}'], capture_output=True, text=True)
    try:
        return json.loads(p.stdout)
    except Exception:
        return {}


def probe(repo):
    full = 'https://raw.githubusercontent.com/' + repo + '/HEAD/README.md'
    p = subprocess.run(['curl', '-sL', '--max-time', '18', '-A', UA, full],
                       capture_output=True, text=True)
    if p.returncode != 0 or len(p.stdout) < 100:
        return repo, None, 'no-readme'
    md = p.stdout
    # markdown 图片 ![alt](url)
    urls = re.findall(r'!\[[^\]]*\]\(\s*<?([^)>\s]+)', md)
    # html <img src="...">
    urls += re.findall(r'<img[^>]+src=["\']([^"\']+)', md, re.I)
    urls += re.findall(r'src=["\']?(https?://[^\s"\'>]+)', md, re.I)
    for u in urls:
        if BAD_IMG.search(u):
            continue
        u = u.strip('<>')
        if not u.lower().split('?')[0].endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
            continue
        if u.startswith('./') or not u.startswith('http'):
            u = 'https://raw.githubusercontent.com/' + repo + '/HEAD/' + u.lstrip('./')
        head = subprocess.run(
            ['curl', '-sI', '--max-time', '12', '-A', UA, u], capture_output=True, text=True).stdout
        mt = re.search(r'content-type:\s*(\S+)', head, re.I)
        cl = re.search(r'content-length:\s*(\d+)', head, re.I)
        if mt and mt.group(1).startswith('image'):
            return repo, u, f'{mt.group(1)} {int(cl.group(1))//1024 if cl else "?"}KB'
    return repo, None, 'no-img'


with ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(probe, REPOS))

ok = [r for r in results if r[1]]
print(f'=== README 抓图命中 {len(ok)}/{len(REPOS)} ===')
for repo, u, info in ok:
    print(f'  ✓ {repo:45s} {info:20s} {u[:95]}')
print('--- 未命中 ---')
for repo, u, info in results:
    if not u:
        print(f'  ✗ {repo:45s} {info}')
