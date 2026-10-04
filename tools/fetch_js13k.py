#!/usr/bin/env python3
"""抓取 js13kGames 38 款仓库的 README 摘要（修正版）。

坑位记录：
  1. 默认分支是 master 不是 main，用 HEAD 别名请求最稳。
  2. contents API 对 HEAD 别名返回 404，要用真实分支名或直接走 raw。
  3. 这些仓库的 README 大量是 HTML 片段，不是 Markdown —— 必须按 HTML 剥标签。
"""
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

REPOS = [
    ('a-verse-on-leverage', 'AGPL-3.0'), ('ap11', 'GPL'), ('asdf', 'MIT'),
    ('bouncing-button', 'MIT'), ('chem-fight', 'MIT'), ('clash-of-elements', 'GPL'),
    ('dante', 'MIT'), ('dodos-escaping-from-extinction', 'GPL'), ('elematter', 'MIT'),
    ('felicity-and-the-fifth-element-love', 'GPL'), ('fill-in-4', 'Apache-2.0'),
    ('floor-thirteen', 'MIT'), ('forest-racer', 'GPL'), ('hard-vacuum-recon', 'MIT'),
    ('junojs', 'MIT'), ('kazukis-escape', 'MIT'), ('mawlight', 'Apache-2.0'),
    ('mentat', 'MIT'), ('milehigh', 'MIT'), ('mission-darkwhite', 'Apache-2.0'),
    ('neptune-blue', 'MIT'), ('please-play-again', 'GPL'), ('pocketrocket', 'MIT'),
    ('radius-raid', 'MIT'), ('rainbow-claw', 'MIT'), ('rainbow-reboot', 'MIT'),
    ('road-the-game', 'MIT'), ('senshi', 'MIT'), ('shapeblocks', 'MIT'),
    ('sorades-13k', 'Apache-2.0'), ('spacepi', 'MIT'), ('terraform', 'MIT'),
    ('the-unlucky-king', 'MIT'), ('timer-madness', 'MIT'), ('under-the-crypt', 'GPL'),
    ('unifrost', 'MIT'), ('vier-wizard-wars', 'MIT'), ('wind-rider', 'MIT'),
]

SKIP = re.compile(
    r'^(js13kgames|js13k|why\?|how to|how do|install|build|run |usage|control|'
    r'contribut|license|licence|deploy|submit|source code|coding competition|'
    r'download|credits|author|you can play|play it|play online|open index|index\.html)', re.I)

GENRE_HINTS = [
    (r'shooter|shmup|invader|bullet ?hell|gun|turret|cannon', 'shooter'),
    (r'platformer|platform game|mario|jump on', 'action'),
    (r'\brac(e|ing)|\bcar\b|drift|track|circuit', 'racing'),
    (r'sokoban|rotate the|physics|puzzle|match ?[34]|lines|tetris', 'puzzle'),
    (r'\brpg\b|role.?play|dungeon|quest|adventure|crawl', 'rpg'),
    (r'tower ?defen|defen[cs]e the|waves of|enemies|turret', 'strategy'),
    (r'\brts\b|strategy|build|base|castle|tower', 'strategy'),
    (r'music|rhythm|beat|sound|audio|note', 'music'),
    (r'clicker|idle|incremental|tycoon|cookie', 'casual'),
    (r'top.?down|arena|duel|fight|combat|battle', 'action'),
    (r'simulat|farm|city|builder|tycoon', 'strategy'),
]


def fetch(url):
    p = subprocess.run(['curl', '-sL', '--max-time', '20', url],
                       capture_output=True, text=True)
    return p.stdout


def readme_of(repo):
    """先查默认分支，拿到真实分支名再取 README（HEAD 别名在 contents API 上会 404）。"""
    api = f'https://api.github.com/repos/js13kGames/{repo}'
    meta = subprocess.run(
        ['curl', '-s', '--max-time', '15', '-H', f'Authorization: Bearer {open("/tmp/tok").read().strip()}',
         api], capture_output=True, text=True).stdout
    branch = 'master'
    try:
        branch = (json.loads(meta).get('default_branch') or 'master')
    except Exception:
        pass
    for name in (f'{branch}/README.md', f'{branch}/readme.md', f'{branch}/README.html',
                 f'{branch}/index.html', f'{branch}/README'):
        txt = fetch(f'https://raw.githubusercontent.com/js13kGames/{repo}/{name}')
        if len(txt) > 60 and 'Not Found' not in txt[:200]:
            return txt
    return ''


def strip(raw):
    """README 多为 HTML；Markdown 图片与 HTML 标签都要清掉。"""
    t = raw
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', t, flags=re.S | re.I)
    t = re.sub(r'<img[^>]*>', ' ', t, flags=re.I)
    t = re.sub(r'<hr\s*/?>', ' ', t, flags=re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', t)
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)
    t = re.sub(r'https?://\S+', ' ', t)
    t = re.sub(r'[*_`>#|]', ' ', t)

    out, seen = [], set()
    for ln in t.split('\n'):
        s = re.sub(r'\s+', ' ', ln).strip()
        if len(s) < 24 or not re.search(r'[A-Za-z]{3}', s):
            continue
        if SKIP.match(s):
            continue
        key = s.lower()[:40]
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
        if sum(len(x) for x in out) > 300:
            break
    return ' '.join(out)


def probe(item):
    repo, lic = item
    raw = readme_of(repo)
    text = strip(raw) if raw else ''
    low = (text + ' ' + repo.replace('-', ' ') + ' ' + repo).lower()
    genres = []
    for pat, g in GENRE_HINTS:
        if re.search(pat, low) and g not in genres:
            genres.append(g)
    # 站点 URL：从 README 里捞作者部署版链接，捞不到就用官方 play 页
    home = ''
    m = re.search(r'https?://([\w.-]+\.(?:github\.io|github\.com|netlify\.app|vercel\.app)/?' + repo + r'/?)', raw or '', re.I)
    if m:
        home = 'https://' + m.group(1)
    return repo, lic, text, genres[:3], home


with ThreadPoolExecutor(max_workers=8) as ex:
    res = list(ex.map(probe, REPOS))

for repo, lic, desc, genres, home in res:
    flag = ' ' if desc else '⚠️'
    print(f'{flag}{repo:40s} [{lic:11s}] {genres}')
    print(f'    {desc[:200]}')
    if home:
        print(f'    home: {home}')

json.dump([{'id': r, 'license': l, 'desc': d, 'genres': g, 'home': h}
           for r, l, d, g, h in res],
          open('/tmp/js13k_meta.json', 'w'), ensure_ascii=False, indent=2)
print(f'\n命中 README: {sum(1 for r in res if r[2])}/38 → /tmp/js13k_meta.json')
