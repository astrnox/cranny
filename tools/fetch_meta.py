#!/usr/bin/env python3
"""用 GitHub API 补齐许可证与健康度数据（清单里标「见仓库」的必须查实）。"""
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor

TOKEN = open('/tmp/tok').read().strip()

# 清单里许可证写「见仓库」的 9 款 + 现有 15 款自己的仓库
REPOS = [
    'adityaravishankar/command-and-conquer', 'cykod/AlienInvasion',
    'lutzroeder/digger', 'Kuberwastaken/backdooms',
    'EnclaveGames/Captain-Rogers', 'itajaja/hb', 'wenta/rapid-dominance',
    'nzp-team/nzportable', 'freedoom/freedoom',
    'astrnox/2048', 'astrnox/hextris', 'astrnox/tower_game',
    'astrnox/h5-game-plantsVSzombies', 'astrnox/trust',
    'astrnox/temple-of-boom', 'astrnox/wordle-plus', 'astrnox/odd-bot-out',
    'astrnox/arkadiumx27s-bubble-shooter', 'astrnox/10-minutes-till-dawn',
    'astrnox/fcgame', 'astrnox/worldguessr', 'astrnox/remake',
    'astrnox/fluid-weiqi-web', 'astrnox/fight-the-landlord',
    # 第二部分客户端（顺带确认 release 有 Windows 包）
    'OpenRA/OpenRA', '0ad/0ad', 'widelands/widelands', 'wesnoth/wesnoth',
    'hedgewars/hw', 'luanti-org/luanti', 'veloren/veloren',
    'endless-sky/endless-sky', 'flareteam/flare-game', 'supertuxkart/stk-code',
    'red-eclipse/base', 'OpenMW/openmw', 'OpenRCT2/OpenRCT2',
    'stepmania/stepmania', 'warzone2100/warzone2100', 'freeciv/freeciv',
    'id-Software/Quake-III-Arena', 'kripken/BananaBread',
]


def get(path):
    p = subprocess.run(['curl', '-s', '--max-time', '18',
                        '-H', f'Authorization: Bearer {TOKEN}',
                        '-H', 'Accept: application/vnd.github+json',
                        f'https://api.github.com{path}'], capture_output=True, text=True)
    try:
        return json.loads(p.stdout)
    except Exception:
        return {}


def probe(repo):
    r = get(f'/repos/{repo}')
    if r.get('message'):
        return repo, {'error': r['message']}
    return repo, {
        'license': ((r.get('license') or {}).get('spdx_id') or 'none'),
        'stars': r.get('stargazers_count'),
        'pushed': (r.get('pushed_at') or '')[:10],
        'archived': r.get('archived'),
        'fork': r.get('fork'),
    }


with ThreadPoolExecutor(max_workers=6) as ex:
    res = dict(ex.map(probe, REPOS))

out = []
for repo, info in res.items():
    out.append((repo, info))

print(f'{"仓库":45s} {"许可证":18s} {"Star":>7s} {"最后push":11s} 归档')
print('-' * 100)
for repo, i in sorted(out):
    if 'error' in i:
        print(f'{repo:45s} ERR {i["error"][:40]}')
    else:
        print(f'{repo:45s} {str(i["license"]):18s} {str(i["stars"]):>7s} {i["pushed"]:11s} '
              f'{"是" if i["archived"] else ""}{" fork" if i["fork"] else ""}')

json.dump(res, open('/tmp/repo_meta.json', 'w'), ensure_ascii=False, indent=2)
print('\n→ /tmp/repo_meta.json')
