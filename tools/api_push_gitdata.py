#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沙箱里 git push 连不上 github.com:443，但 api.github.com 通。

Contents API 逐文件 PUT 会产生 N 个 commit（这里 239 个文件 = 239 个 commit，
PR 里全是噪声）。所以走 Git Data API 一次性合成一个 commit：
    blob（每个改动文件）→ tree → commit → update ref
和普通 git push 的结果等价，但只占一个 commit。

用法：python3 tools/api_push_gitdata.py [PAT] [消息]
不带 PAT 时读 /tmp/tok。
"""

import base64
import hashlib
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = 'astrnox/gamespace'
API = f'https://api.github.com/repos/{REPO}'
TOKEN = (sys.argv[1] if len(sys.argv) > 1 else
         (Path('/tmp/tok').read_text().strip() if Path('/tmp/tok').exists() else ''))
MESSAGE = sys.argv[2] if len(sys.argv) > 2 else '更新游戏收录数据与界面'

if not TOKEN:
    sys.exit('没有 PAT：把 token 存到 /tmp/tok 或作为第一个参数传入')


def req(method, url, body=None, raw=False, timeout=60):
    data = None if body is None else json.dumps(body).encode()
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header('Authorization', f'Bearer {TOKEN}')
    r.add_header('Accept', 'application/vnd.github+json')
    r.add_header('X-GitHub-Api-Version', '2022-11-28')
    if data:
        r.add_header('Content-Type', 'application/json')
    for attempt in range(4):
        try:
            resp = urllib.request.urlopen(r, timeout=timeout)
            payload = resp.read()
            return payload if raw else (json.loads(payload) if payload else {})
        except urllib.error.HTTPError as e:
            # 仓库改名后 api.github.com/repos/旧名 会 307 到 repositories/<id>，
            # 307/308 对 POST 是安全的（method 和 body 都保持），直接跟着走。
            if e.code in (307, 308):
                new_url = e.headers.get('Location')
                if new_url:
                    return req(method, new_url, body, raw, timeout)
            body_txt = e.read()[:300].decode('utf-8', 'replace')
            # 5xx 和速率限制都重试；4xx 直接失败
            if e.code >= 500 or e.code == 429:
                wait = 2 ** attempt
                print(f'  ! {e.code}，{wait}s 后重试')
                time.sleep(wait)
                continue
            sys.exit(f'✗ {method} {url}\n  HTTP {e.code}: {body_txt}')
        except urllib.error.URLError as e:
            wait = 2 ** attempt
            print(f'  ! 网络错误（{e.reason}），{wait}s 后重试')
            time.sleep(wait)
    sys.exit(f'✗ {method} {url} 重试 4 次仍失败')


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()


# blob 上传很慢（238 个文件要好几分钟），失败重试时别重复劳动：
# 用「内容 sha1 → blob sha」做缓存，Git 的 blob sha 就是内容的 git hash。
BLOB_CACHE_PATH = ROOT / '.git' / 'blob-cache.json'


def load_blob_cache():
    if BLOB_CACHE_PATH.exists():
        try:
            return json.loads(BLOB_CACHE_PATH.read_text())
        except Exception:
            return {}
    return {}


def save_blob_cache(cache):
    BLOB_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BLOB_CACHE_PATH.write_text(json.dumps(cache))


def git_blob_sha(data: bytes) -> str:
    """git hash-object 的算法：sha1('blob <len>\\0' + data)。"""
    header = f'blob {len(data)}\0'.encode()
    return hashlib.sha1(header + data).hexdigest()


def main():
    base = req('GET', f'{API}/git/ref/heads/main')['object']['sha']
    print(f'远端 main: {base[:10]}')

    # 1. 本地相对远端改了哪些文件（含删除）
    changed = git('diff', '--name-status', 'origin/main', 'HEAD').splitlines()
    if not changed:
        print('没有改动，跳过')
        return
    ops, adds, dels = [], 0, 0
    cache = load_blob_cache()
    new_cache = 0
    for line in changed:
        parts = line.split('\t')
        status, path = parts[0], parts[-1]
        if status.startswith('D'):
            ops.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': None})
            dels += 1
            continue
        content = (ROOT / path).read_bytes()
        key = git_blob_sha(content)
        if key in cache:
            blob_sha = cache[key]
        else:
            blob = req('POST', f'{API}/git/blobs',
                       {'content': base64.b64encode(content).decode(),
                        'encoding': 'base64'})
            blob_sha = blob['sha']
            cache[key] = blob_sha
            new_cache += 1
        ops.append({'path': path, 'mode': '100644', 'type': 'blob', 'sha': blob_sha})
        adds += 1
    if new_cache:
        save_blob_cache(cache)
    print(f'待提交：新增/修改 {adds}，删除 {dels}'
          + (f'（{new_cache} 个 blob 新上传，{adds - new_cache} 个命中缓存）'
             if new_cache else '（全部命中缓存）'))

    # 2. 基于远端 tree 叠加，得到新 tree
    base_commit = req('GET', f'{API}/git/commits/{base}')
    tree = req('POST', f'{API}/git/trees',
               {'base_tree': base_commit['tree']['sha'], 'tree': ops})
    if tree.get('truncated'):
        sys.exit('✗ tree 被截断，文件过多')

    # 3. 合成一个 commit
    msg = (git('log', '-1', '--pretty=%B', 'HEAD').strip() or MESSAGE)
    commit = req('POST', f'{API}/git/commits', {
        'message': msg, 'tree': tree['sha'], 'parents': [base],
    })

    # 4. 推 ref（force=false，挡住并发写）
    req('PATCH', f'{API}/git/refs/heads/main',
        {'sha': commit['sha'], 'force': False})
    print(f'✓ 已推送 {commit["sha"][:10]}（{adds + dels} 个文件，1 个 commit）')

    # 5. 本地跟上远端，避免下次 push 又从旧 base 起算
    subprocess.run(['git', 'update-ref', 'refs/remotes/origin/main', commit['sha']],
                   cwd=ROOT, check=False)


if __name__ == '__main__':
    main()
