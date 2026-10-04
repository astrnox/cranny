#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 games.json 里全部游戏的在线入口与仓库地址。

三项检查：
  1. 在线入口 HTTP 状态
  2. 是否允许 iframe 内嵌（X-Frame-Options / CSP frame-ancestors）
  3. 仓库地址是否存在（GitHub API）

结果写回 data/link-check.json，同时按需修正 games.json 的
embeddable / embedCheck / status 字段。
"""
import base64
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / 'data' / 'games.json'
OUT = ROOT / 'data' / 'link-check.json'

TOKEN = Path('/tmp/tok').read_text().strip() if Path('/tmp/tok').exists() else ''
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# 已知禁嵌站点（站点策略明确禁止），实测过就不再重复请求
KNOWN_BLOCKED = {
    'play2048.co': "'self'",
    'lichess.org': 'DENY',
    'browsercraft.com': 'SAMEORIGIN',
    'stendhalgame.org': 'SAMEORIGIN',
    'play.js13kgames.com': "frame-ancestors 'self' js13kgames.com",
}


def code_of(r):
    """status 可能是 'skip' 字符串，统一成整数（0 = 未测/无响应）。"""
    v = r.get('status')
    return v if isinstance(v, int) else 0


def headers(url):
    """只取响应头，跟重定向但不发请求体。"""
    p = subprocess.run(
        ['curl', '-sIL', '--max-time', '18', '-A', UA,
         '-o', '-', '-w', '\n[final:%{http_code} url:%{url_effective}]', url],
        capture_output=True, text=True)
    return p.stdout


def check_embed(h):
    xfo = re.findall(r'x-frame-options:\s*([^\r\n]+)', h, re.I)
    csp = re.findall(r'frame-ancestors\s+([^\r\n;]+)', h, re.I)
    return (xfo[-1].strip() if xfo else None), (csp[-1].strip() if csp else None)


def probe(g):
    gid = g['id']
    rec = {'id': gid, 'title': g['title']}

    # 仓库存在性
    if g.get('repo') and 'github.com/' in g['repo']:
        slug = g['repo'].split('github.com/')[1].strip('/')
        if TOKEN:
            p = subprocess.run(
                ['curl', '-s', '--max-time', '15', '-H', f'Authorization: Bearer {TOKEN}',
                 f'https://api.github.com/repos/{slug}'], capture_output=True, text=True)
            try:
                j = json.loads(p.stdout)
                rec['repoOk'] = 'message' not in j
                if 'message' in j:
                    rec['repoErr'] = j['message']
                elif g.get('license') is None and j.get('license'):
                    rec['apiLicense'] = j['license']['spdx_id']
            except Exception:
                rec['repoOk'] = None

    # 在线入口
    if g['kind'] == 'download' or not g.get('url'):
        rec['status'] = 'skip'
        return rec

    host = re.sub(r'^https?://([^/]+).*', r'\1', g['url'])
    if host in KNOWN_BLOCKED:
        rec.update(status=200, xfo=None,
                   csp=KNOWN_BLOCKED[host], embeddable=False, known='blocked')
        return rec

    h = headers(g['url'])
    code = re.search(r'\[final:(\d+)', h)
    fin = re.search(r'url:([^\]]+)\]', h)
    code = int(code.group(1)) if code else 0   # 0 = 没抓到状态码
    xfo, csp = check_embed(h)
    embed = not (xfo or csp)
    rec.update(status=code, finalUrl=fin.group(1) if fin else None,
               xfo=xfo, csp=csp, embeddable=embed)
    return rec


def main():
    doc = json.loads(GAMES.read_text(encoding='utf-8'))
    games = doc['games']
    print(f'开始校验 {len(games)} 款…\n')

    with ThreadPoolExecutor(max_workers=10) as ex:
        results = list(ex.map(probe, games))
    by_id = {r['id']: r for r in results}

    dead, blocked, changed, no_lic = [], [], [], []
    for g in games:
        r = by_id[g['id']]
        if r.get('repoOk') is False:
            dead.append((g['id'], '仓库不存在: ' + r.get('repoErr', '')))
        if r.get('repoOk') is None and r.get('repoErr'):
            dead.append((g['id'], '仓库查询失败: ' + r['repoErr']))
        if r.get('apiLicense') and g.get('license') != r['apiLicense']:
            no_lic.append((g['id'], g.get('license'), r['apiLicense']))
        if r.get('status') == 'skip':
            continue
        code = code_of(r)
        if code == 0:
            dead.append((g['id'], '无响应/超时'))
            continue
        if code >= 400:
            dead.append((g['id'], f'HTTP {code}'))
            continue
        if r.get('embeddable') is False:
            blocked.append((g['id'], r.get('xfo') or r.get('csp')))
        # 修正数据里的 embeddable
        want = r.get('embeddable')
        if want is not None and g.get('embeddable') != want:
            changed.append((g['id'], g.get('embeddable'), want))

    alive = sum(1 for r in results if 0 < code_of(r) < 400)
    print(f'✅ 在线可访问   {alive}')
    print(f'⛔ 禁止内嵌     {len(blocked)}')
    print(f'❌ 失效/异常    {len(dead)}')
    print(f'🔄 需改内嵌标记 {len(changed)}')

    if blocked:
        print('\n--- 禁嵌（只能外链）---')
        for i, why in sorted(blocked):
            print(f'  {i:32s} {why}')
    if dead:
        print('\n--- 失效 ---')
        for i, why in sorted(dead):
            print(f'  {i:32s} {why}')
    if no_lic:
        print('\n--- 许可证与 API 不一致（数据缺 license，建议补）---')
        for i, cur, api in sorted(no_lic):
            print(f'  {i:32s} 当前={cur}  API={api}')
    if changed:
        print('\n--- 内嵌标记需修正 ---')
        for i, a, b in changed:
            print(f'  {i:32s} {a} → {b}')

    OUT.write_text(json.dumps(
        {'checkedAt': '2026-10-04', 'results': results},
        ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\n→ {OUT.relative_to(ROOT)}')

    if '--apply' in sys.argv:
        for g in games:
            r = by_id[g['id']]
            if r.get('status') == 'skip':
                continue
            if r.get('embeddable') is not None:
                g['embeddable'] = r['embeddable']
                g['embedCheck'] = {
                    'checkedAt': '2026-10-04',
                    'result': 'ok' if r['embeddable'] else 'blocked',
                }
                # 禁嵌的不能再走 iframe，改为外链
                if not r['embeddable'] and g['mode'] == 'embed':
                    g['mode'] = 'redirect'
                    g.setdefault('note', '官方站禁止内嵌，已改为新窗口打开')
        GAMES.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n',
                         encoding='utf-8')
        print('已写回 games.json')

    return 1 if dead else 0


if __name__ == '__main__':
    sys.exit(main())
