#!/usr/bin/env python3
"""git 协议不通时的兜底：走 GitHub API 逐个提交文件。

git push 连的是 github.com:443，沙箱里常常被墙；
api.github.com 通常能通，所以用 Contents API 逐文件 PUT。

用法：python3 tools/api_push.py <PAT> [base_sha]
"""

import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

REPO = "astrnox/gamespace"
API = f"https://api.github.com/repos/{REPO}"


def req(method, url, pat, body=None, timeout=30):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Authorization", f"Bearer {pat}")
    r.add_header("Accept", "application/vnd.github+json")
    r.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")
    except Exception as e:                                  # 网络抖动
        return 0, {"message": str(e)}


def get_sha(pat, path, ref):
    st, d = req("GET", f"{API}/contents/{path}?ref={ref}", pat)
    return d.get("sha") if st == 200 else None


def put(pat, path, content, msg, ref, base_sha):
    body = {
        "message": msg,
        "content": base64.b64encode(content).decode(),
        "branch": ref,
    }
    if base_sha:
        body["sha"] = base_sha
    st, d = req("PUT", f"{API}/contents/{path}", pat, body)
    return st, d


def main():
    pat = sys.argv[1]
    ref = "main"
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    # 远端 sha 只用来兜底；Contents API 逐文件提交会在远端留下一串
    # 本地没有的 commit，git diff 对不上，所以直接比对文件内容。
    st, d = req("GET", f"{API}/commits/{ref}", pat)
    if st != 200:
        print(f"读远端 {ref} 失败：{d.get('message')}")
        return 1
    print(f"远端 {ref} = {d['sha'][:10]}\n")

    # 以 HEAD 为准取文件清单：工作区改动 + 未跟踪文件
    out = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True, text=True)
    tracked = [f for f in out.stdout.split("\n") if f.strip()]
    out2 = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True, text=True)
    untracked = [f for f in out2.stdout.split("\n") if f.strip()]

    # 本地 HEAD 相对远端没有可用的 diff（远端有本地说没有的 commit），
    # 所以把「远端存在的全部文件」也纳入比对，靠内容差异找出该传什么。
    out3 = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "HEAD"],
        capture_output=True, text=True)
    in_head = [f for f in out3.stdout.split("\n") if f.strip()]
    files = sorted({f for f in tracked + untracked + in_head
                    if os.path.isfile(f)})
    if not files:
        print("没有需要上传的变更")
        return 0

    msg = subprocess.run(["git", "log", "-1", "--pretty=%B"],
                         capture_output=True, text=True).stdout.strip()

    changed, skipped = [], []
    for f in files:
        with open(f, "rb") as fh:
            data = fh.read()
        st, cur = req("GET", f"{API}/contents/{f}?ref={ref}", pat, timeout=40)
        if st == 200 and cur.get("sha"):
            import base64 as _b64
            try:
                remote_bytes = _b64.b64decode(cur.get("content", ""))
            except Exception:
                remote_bytes = b""
            if remote_bytes == data:
                skipped.append(f)
                continue
        changed.append(f)

    if not changed:
        print(f"远端已是最新（{len(skipped)} 个文件一致）")
        return 0

    print(f"待传 {len(changed)} 个文件，跳过 {len(skipped)} 个已一致\n")

    for i, f in enumerate(changed, 1):
        with open(f, "rb") as fh:
            data = fh.read()
        cur = get_sha(pat, f, ref)
        for attempt in range(3):
            st, d = put(pat, f, data, msg, ref, cur)
            if st in (200, 201):
                print(f"  [{i}/{len(changed)}] ✓ {f}")
                break
            # 并发改动导致的 sha 冲突：重新取一次再试
            if st in (409, 422) and attempt < 2:
                cur = get_sha(pat, f, ref)
                continue
            print(f"  [{i}/{len(changed)}] ✗ {f}  {st} {d.get('message')}")
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
