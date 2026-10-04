#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探测 js13kGames 38 款是否有作者自建的 GitHub Pages 可直接内嵌。

背景：play.js13kgames.com 设了 CSP frame-ancestors，只放行 js13kgames.com，
所以官方 play 页一律禁嵌。解法有两条：
  A. fork 到 astrnox 名下自托管（需要 fork 权限，等新 PAT）
  B. 作者本人已把游戏部署在自己的 github.io —— 这种能直接内嵌，不用 fork

这个脚本做路线 B 的普查。
"""
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

TOKEN = open('/tmp/tok').read().strip()
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'

IDS = [
    'a-verse-on-leverage', 'ap11', 'asdf', 'bouncing-button', 'chem-fight',
    'clash-of-elements', 'dante', 'dodos-escaping-from-extinction', 'elematter',
    'felicity-and-the-fifth-element-love', 'fill-in-4', 'floor-thirteen',
    'forest-racer', 'hard-vacuum-recon', 'junojs', 'kazukis-escape', 'mawlight',
    'mentat', 'milehigh', 'mission-darkwhite', 'neptune-blue',
    'please-play-again', 'pocketrocket', 'radius-raid', 'rainbow-claw',
    'rainbow-reboot', 'road-the-game', 'senshi', 'shapeblocks', 'sorades-13k',
    'spacepi', 'terraform', 'the-unlucky-king', 'timer-madness',
    'under-the-crypt', 'unifrost', 'vier-wizard-wars', 'wind-rider',
]


def curl(url, head=False, timeout=14):
    cmd = ['curl', '-sL', '--max-time', str(timeout), '-A', UA]
    if head:
        cmd.append('-I')
    cmd.append(url)
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.stdout


def repo_meta(org_repo):
    p = subprocess.run(
        ['curl', '-s', '--max-time', '14', '-H', f'Authorization: Bearer {TOKEN}',
         f'https://api.github.com/repos/{org_repo}'], capture_output=True, text=True)
    try:
        return json.loads(p.stdout)
    except Exception:
        return {}


def candidates(gid):
    """可能的自托管地址：作者 github.io、js13k 组织下的镜像仓库。"""
    out = []
    for repo in (f'js13kGames/{gid}',):
        m = repo_meta(repo)
        if m.get('message'):
            continue
        h = m.get('homepage') or ''
        if h and 'github.io' in h:
            out.append(('homepage', h))
        owner = m.get('owner', {}).get('login')
        if owner:
            out.append(('owner', f'https://{owner.lower()}.github.io/{gid}/'))
    return out


def probe(gid):
    cands = candidates(gid)
    if not cands:
        return gid, None, '无候选'
    for how, url in cands:
        h = curl(url, head=True)
        codes = re.findall(r'HTTP/[\d.]+\s+(\d+)', h)
        code = int(codes[-1]) if codes else 0
        if not (200 <= code < 400):
            continue
        # 确认不是 404 页且真的能内嵌
        full = curl(url)
        if len(full) < 200 or '404' in full[:400].lower():
            continue
        xfo = re.findall(r'x-frame-options:\s*([^\r\n]+)', h, re.I)
        csp = re.findall(r'frame-ancestors\s+([^\r\n;]+)', h, re.I)
        return gid, url, ('禁嵌 ' + (xfo[-1] or csp[-1] if (xfo or csp) else '')) if (xfo or csp) else '可嵌'
    return gid, None, '候选均不可用: ' + ', '.join(u for _, u in cands)


with ThreadPoolExecutor(max_workers=8) as ex:
    res = list(ex.map(probe, IDS))

ok = [r for r in res if r[1]]
print(f'=== 找到自托管可嵌的 {len(ok)}/38 ===')
for gid, url, why in ok:
    print(f'  ✓ {gid:38s} {url:52s} {why}')
print('--- 其余 ---')
for gid, url, why in res:
    if not url:
        print(f'  · {gid:38s} {why}')
json.dump([{'id': g, 'url': u, 'why': w} for g, u, w in ok],
          open('/tmp/js13k_selfhost.json', 'w'), ensure_ascii=False, indent=2)
