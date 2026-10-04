#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为收录的第三方游戏生成 README 预览页。

为什么要有这个：详情页原本只有站主自己那 15 款有 README 预览，
收录 98 款之后全靠「去 GitHub 看」兜底，体验断了一截。

做法：抓各仓库 README 原文（Markdown/HTML 都行），
套进与现有 readme/*.html 相同的一套自包含样式，
零外网依赖、零跨域，跟站点主题同步明暗。

不做什么：不装第三方依赖、不执行仓库里的任何脚本、不抓取 README 里的图片
（图片外链会拖慢首屏，且不少是失效的图床）。
"""
import html
import json
import re
import subprocess
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / 'data' / 'games.json'
OUT = ROOT / 'readme'
TOKEN = Path('/tmp/tok').read_text().strip() if Path('/tmp/tok').exists() else ''
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'

STYLE = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · README</title>
<style>
:root{{
  --bg:#ffffff; --fg:#1f2328; --muted:#59636e; --border:#d1d9e0;
  --code-bg:#f6f8fa; --quote-bg:#f6f8fa; --link:#ff5a36; --accent:#ff5a36;
}}
@media (prefers-color-scheme: dark){{
  :root{{
    --bg:#0d1117; --fg:#e6edf3; --muted:#9198a1; --border:#3d444d;
    --code-bg:#161b22; --quote-bg:#161b22; --link:#ff7a58; --accent:#ff7a58;
  }}
}}
html[data-theme="light"]{{
  --bg:#ffffff; --fg:#1f2328; --muted:#59636e; --border:#d1d9e0;
  --code-bg:#f6f8fa; --quote-bg:#f6f8fa; --link:#ff5a36; --accent:#ff5a36;
}}
html[data-theme="dark"]{{
  --bg:#0d1117; --fg:#e6edf3; --muted:#9198a1; --border:#3d444d;
  --code-bg:#161b22; --quote-bg:#161b22; --link:#ff7a58; --accent:#ff7a58;
}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0;background:var(--bg);color:var(--fg)}}
body{{
  padding:18px 20px 22px;
  font:15px/1.68 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",
       "Hiragino Sans GB","Microsoft YaHei",sans-serif;
  -webkit-font-smoothing:antialiased;
  word-wrap:break-word;
}}
h1,h2,h3,h4{{line-height:1.3;margin:1.5em 0 .6em;font-weight:600}}
h1{{font-size:1.5em;margin-top:0;padding-bottom:.4em;border-bottom:1px solid var(--border)}}
h2{{font-size:1.22em;padding-bottom:.3em;border-bottom:1px solid var(--border)}}
h3{{font-size:1.08em}}
p{{margin:0 0 .9em}}
a{{color:var(--link);text-decoration:none}}
a:hover{{text-decoration:underline}}
ul,ol{{margin:0 0 .9em;padding-left:1.5em}}
li{{margin:.25em 0}}
code{{
  background:var(--code-bg);padding:.15em .38em;border-radius:4px;
  font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}}
pre{{
  background:var(--code-bg);border:1px solid var(--border);border-radius:6px;
  padding:12px 14px;overflow-x:auto;margin:0 0 1em;
}}
pre code{{background:none;padding:0}}
blockquote{{
  margin:0 0 1em;padding:.5em 14px;border-left:3px solid var(--border);
  background:var(--quote-bg);color:var(--muted);
}}
blockquote>:last-child{{margin-bottom:0}}
table{{border-collapse:collapse;margin:0 0 1em;font-size:.94em;width:100%}}
th,td{{border:1px solid var(--border);padding:6px 10px;text-align:left}}
th{{background:var(--code-bg);font-weight:600}}
hr{{border:0;border-top:1px solid var(--border);margin:1.6em 0}}
img{{max-width:100%;height:auto;border-radius:6px}}
kbd{{
  background:var(--code-bg);border:1px solid var(--border);border-bottom-width:2px;
  border-radius:4px;padding:.1em .4em;font-size:.85em;
}}
.head{{
  display:flex;flex-wrap:wrap;gap:8px;align-items:center;
  padding-bottom:12px;margin-bottom:16px;border-bottom:1px solid var(--border);
  font-size:13px;color:var(--muted);
}}
.head a{{color:var(--muted)}}
.head .sep{{opacity:.5}}
.prose-raw{{
  margin-top:22px;padding-top:14px;border-top:1px dashed var(--border);
  font-size:12px;color:var(--muted);
}}
{CARD_CSS}
</style>
</head>
<body>
<div class="head">
  <strong style="color:var(--fg)">{title}</strong>
  <span class="sep">·</span>
  <span>{lic}</span>
  <span class="sep">·</span>
  <a href="{repo}" target="_blank" rel="noopener noreferrer">在 GitHub 上看原版 ↗</a>
</div>
{body}
<p class="prose-raw">以上为该项目 README 的原文摘编，版权归原作者所有。</p>
</body>
</html>"""

# 引用行前缀（HTML 转义后的 "> "）
QUOTE_RE = re.compile(r'^&gt;\s?')
# 表格对齐行，如 |:--|:--:|---:|
ALIGN_ROW_RE = re.compile(r'^:?-{2,}:?$')

PLATFORM_LABEL = {'web': '网页', 'pc': 'PC', 'win': 'Windows', 'lin': 'Linux',
                  'mac': 'macOS', 'android': '安卓', 'ios': 'iOS'}


def curl(url, timeout=18):
    p = subprocess.run(['curl', '-sL', '--max-time', str(timeout), '-A', UA, url],
                       capture_output=True, text=True)
    return p.stdout


def usable(txt):
    """判断抓到的是不是真 README，而不是 404 页或 API 的 JSON 错误。"""
    if not txt or len(txt.strip()) < 12:
        return False
    head = txt.lstrip()[:200]
    if '404: Not Found' in txt[:200] or 'Not Found' in head:
        return False
    if head[:1] in '{[':          # API 回了 JSON（多半是 message: Not Found）
        return False
    return True


def default_branch(slug):
    if not TOKEN:
        return 'HEAD'
    meta = subprocess.run(
        ['curl', '-s', '--max-time', '14', '-H', f'Authorization: Bearer {TOKEN}',
         f'https://api.github.com/repos/{slug}'], capture_output=True, text=True).stdout
    try:
        return json.loads(meta).get('default_branch') or 'HEAD'
    except Exception:
        return 'HEAD'


def gitlab_readme(repo):
    """GitLab 的 README 走公开 API，不需要 token。"""
    slug = repo.split('gitlab.com/')[-1].strip('/').removesuffix('.git')
    meta = curl(f'https://gitlab.com/api/v4/projects/{urllib.parse.quote(slug, safe="")}')
    try:
        branch = json.loads(meta).get('default_branch') or 'HEAD'
    except Exception:
        return None
    for name in ('README.md', 'readme.md', 'README', 'README.rst'):
        txt = curl(f'https://gitlab.com/{slug}/-/raw/{branch}/{name}')
        if usable(txt):
            return txt
    return None


def raw_readme(repo):
    """取 README 原文。

    GitHub：API 的 /readme（大小写不敏感，最稳）→ js13k 常见的 .website/README.md
    → raw 猜文件名。js13k 参赛仓库的 README 常常只有一行赛事说明，
    所以下限放得很低，只要不是空的就收。
    GitLab：官方 API 拿默认分支再取 raw。
    取不到不算失败——build() 会退到资料卡。
    """
    if 'gitlab.com/' in repo:
        return gitlab_readme(repo)
    if 'github.com/' not in repo:
        return None
    slug = repo.split('github.com/')[-1].strip('/').removesuffix('.git')

    if TOKEN:
        p = subprocess.run(
            ['curl', '-s', '--max-time', '16', '-H', f'Authorization: Bearer {TOKEN}',
             '-H', 'Accept: application/vnd.github.raw',
             f'https://api.github.com/repos/{slug}/readme'],
            capture_output=True, text=True).stdout
        if usable(p):
            return p

    branch = default_branch(slug)
    names = ('README.md', 'readme.md', 'README.MD', 'README', 'README.html',
             'readme.html', 'README.htm', '.website/README.md')
    for name in names:
        txt = curl(f'https://raw.githubusercontent.com/{slug}/{branch}/{name}')
        if usable(txt):
            return txt
    return None


# --- 极简 Markdown 渲染：只覆盖 README 里真正常用的语法 ---
def render_inline(text):
    """行内元素。输入已做过 HTML 转义。

    用占位符隔离：先把行内代码和 Markdown 链接转成真标签并存起来，
    最后再处理裸链接——否则裸链接的正则会回头去啃刚生成的 href="https://…"，套出一层套壳。
    """
    slots = []

    def hold(fragment):
        slots.append(fragment)
        return f'\x00S{len(slots) - 1}\x00'

    def stash_code(m):
        return hold(f'<code>{m.group(1)}</code>')

    def stash_img(m):
        alt = m.group(1)
        return hold(f'<em>{alt or "图片"}</em>' if alt else '')

    def stash_link(m):
        return hold(f'<a href="{m.group(2)}" target="_blank" '
                    f'rel="noopener noreferrer">{m.group(1)}</a>')

    text = re.sub(r'`([^`\n]+)`', stash_code, text)
    # 图片：降级成斜体文字。外链图会拖慢首屏，且不少图床已失效
    text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', stash_img, text)
    text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', stash_link, text)
    # 剩下的裸链接（前面有 href= 的不会走到这，因为已被占位符换走）
    text = re.sub(r'(?<![\w/@.])(https?://[^\s<>"）】]+)',
                  r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>', text)

    for idx, frag in enumerate(slots):
        text = text.replace(f'\x00S{idx}\x00', frag)
    return text


def split_row(line):
    """按 | 切表格行，但要避开行内代码里的竖线（`a|b` 是一个格子）。"""
    cells, buf, in_code = [], [], False
    for ch in line.strip().strip('|'):
        if ch == '`':
            in_code = not in_code
            buf.append(ch)
        elif ch == '|' and not in_code:
            cells.append(''.join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    cells.append(''.join(buf).strip())
    return cells


def flush_table(out, rows):
    """把攒到的表格行渲染成 thead + tbody。rows[0] 视为表头。"""
    def row(cells, tag):
        return '<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>'

    head, *body = rows
    parts = ['<table><thead>', row(head, 'th'), '</thead><tbody>']
    for r in body:
        # 补齐列数，避免表格歪掉
        cells = r + [''] * (len(head) - len(r))
        parts.append(row(cells, 'td'))
    parts.append('</tbody></table>')
    out.append(''.join(parts))


def md_to_html(md):
    md = html.escape(md.replace('\r\n', '\n'), quote=False)

    # 1. 抽掉围栏代码块，先占位，别让里面的 # 和 - 被当正文
    blocks = []

    def stash(m):
        blocks.append(m.group(1).strip('\n'))
        return f'\x00B{len(blocks) - 1}\x00'

    md = re.sub(r'```[^\n]*\n(.*?)```', stash, md, flags=re.S)
    md = re.sub(r'~~~[^\n]*\n(.*?)~~~', stash, md, flags=re.S)
    # 未闭合的围栏（README 截断时常见）
    md = re.sub(r'```[^\n]*\n(.*)$', stash, md, flags=re.S)

    out, lines = [], md.split('\n')
    i, n = 0, len(lines)
    list_tag = None      # 当前未关闭的列表类型
    table_rows = None    # 当前攒着的表格行

    def close_list():
        nonlocal list_tag
        if list_tag:
            out.append(f'</{list_tag}>')
            list_tag = None

    def close_table():
        nonlocal table_rows
        if table_rows:
            flush_table(out, table_rows)
            table_rows = None

    def close_blocks():
        close_table()
        close_list()

    while i < n:
        stripped = lines[i].strip()

        if not stripped:
            close_blocks()
            i += 1
            continue

        # 标题
        if stripped.startswith('#'):
            close_blocks()
            lv = len(stripped) - len(stripped.lstrip('#'))
            lv = min(lv, 4)
            out.append(f'<h{lv}>{render_inline(stripped[lv:].strip())}</h{lv}>')
            i += 1
            continue

        # 分隔线
        if re.match(r'^(-{3,}|\*{3,}|_{3,})$', stripped):
            close_blocks()
            out.append('<hr>')
            i += 1
            continue

        # 引用（支持连续多行合并成一个块）
        if stripped.startswith('&gt;'):
            close_list()
            close_table()
            buf = []
            while i < n and lines[i].strip().startswith('&gt;'):
                buf.append(QUOTE_RE.sub('', lines[i].strip()))
                i += 1
            inner = '<br>'.join(render_inline(b) for b in buf if b)
            out.append(f'<blockquote>{inner}</blockquote>')
            continue

        # 表格：一行行攒，遇到空行或非表格行才收口
        if stripped.startswith('|') and stripped.endswith('|') and len(stripped) > 1:
            close_list()
            cells = split_row(stripped)
            # 对齐行（|---|:--:|）跳过，不算内容
            if all(ALIGN_ROW_RE.match(c) for c in cells if c):
                i += 1
                continue
            if table_rows is None:
                table_rows = []
            table_rows.append([render_inline(c) for c in cells])
            i += 1
            continue
        close_table()

        # 列表
        m = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.*)$', lines[i])
        if m:
            want = 'ol' if m.group(2)[0].isdigit() else 'ul'
            if list_tag != want:
                close_list()
                out.append(f'<{want}>')
                list_tag = want
            out.append(f'<li>{render_inline(m.group(3).strip())}</li>')
            i += 1
            continue
        close_list()

        out.append(f'<p>{render_inline(stripped)}</p>')
        i += 1

    close_blocks()

    # 放回代码块
    body = '\n'.join(out)
    for idx, code in enumerate(blocks):
        pre = f'<pre><code>{code}</code></pre>'
        body = body.replace(f'<p>\x00B{idx}\x00</p>', pre).replace(f'\x00B{idx}\x00', pre)
    return body


def strip_html(raw):
    """README 若是 HTML 片段，剥标签转成纯文本段落。"""
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', raw, flags=re.S | re.I)
    t = re.sub(r'<br\s*/?>', '\n', t, flags=re.I)
    t = re.sub(r'</(p|div|li|h[1-6]|tr|pre)>', '\n\n', t, flags=re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r' *\n *', '\n', t)
    return re.sub(r'\n{3,}', '\n\n', t).strip()


CARD_CSS = """.card{
  border:1px solid var(--border);border-radius:8px;padding:14px 16px;margin:0 0 1em;
  background:var(--code-bg);
}
.card h2{margin:0 0 .7em;font-size:1.05em;border:0;padding:0}
.card dl{display:grid;grid-template-columns:auto 1fr;gap:.45em 1em;margin:0}
.card dt{color:var(--muted);font-size:.9em;white-space:nowrap}
.card dd{margin:0;font-size:.94em}
.card .actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:1.1em}
.card .actions a{
  border:1px solid var(--border);border-radius:6px;padding:.34em .8em;
  font-size:.88em;background:var(--bg);
}
.card .actions a:hover{border-color:var(--accent);text-decoration:none}
.thin-note{
  margin:0 0 1em;padding:.6em 12px;border-left:3px solid var(--accent);
  background:var(--quote-bg);color:var(--muted);font-size:.9em;
}"""


def info_card(g):
    """README 太空（js13k 常见：一行赛事说明）时，用元数据补一张像样的资料卡。

    比给用户看一个光秃秃的标题强——至少说清玩法、怎么玩、什么许可证。
    """
    def row(label, value):
        if not value:
            return ''
        v = html.escape(str(value))
        return f'<dt>{html.escape(label)}</dt><dd>{v}</dd>'

    def links():
        out = []
        if g.get('url'):
            out.append(f'<a href="{html.escape(g["url"], quote=True)}" target="_blank" '
                       f'rel="noopener noreferrer">直接开玩 ↗</a>')
        if g.get('repo'):
            out.append(f'<a href="{html.escape(g["repo"], quote=True)}" target="_blank" '
                       f'rel="noopener noreferrer">源码仓库 ↗</a>')
        return ''.join(out)

    plat = ' / '.join(PLATFORM_LABEL.get(p, p) for p in g.get('platform', []))
    rows = ''.join([
        row('玩法', g.get('desc')),
        row('类型', '、'.join(g.get('tags', []))),
        row('操作', '鼠标' if g.get('kind') == 'web' else '键鼠'),
        row('平台', plat),
        row('人数', f"{g['players']} 人" if g.get('players') else ''),
        row('许可证', g.get('license') or '未声明'),
    ])
    acts = links()
    return (f'<div class="card"><h2>游戏资料</h2><dl>{rows}</dl>'
            + (f'<div class="actions">{acts}</div>' if acts else '')
            + '</div>')


def build(g):
    raw = raw_readme(g.get('repo', ''))
    body = ''
    if raw:
        # README 若是 HTML（含 badge、居中排版这类），剥标签按纯文本处理
        if re.search(r'<(html|body|div|center|table|h[1-6])\b', raw[:3000], re.I):
            text = strip_html(raw)
            paras = [p.strip() for p in text.split('\n\n') if p.strip()]
            body = ''.join(f'<p>{html.escape(p).replace(chr(10), "<br>")}</p>'
                           for p in paras)
        else:
            body = md_to_html(raw)
        # 超长 README 截断，别把整个 iframe 撑爆
        body = body[:24000]

    # 剥掉标签后正文太短 → README 基本没写东西，补一张资料卡
    plain = re.sub(r'<[^>]+>', '', body)
    if len(plain.strip()) < 120:
        note = ('<p class="thin-note">这个项目的 README 只写了寥寥几句，'
                '下面是我们从仓库和页面里整理的资料。</p>' if plain.strip() else '')
        body = note + info_card(g)

    lic = g.get('license') or '未声明许可证'
    return STYLE.format(lang='zh-CN', title=html.escape(g['title']),
                        lic=html.escape(lic), repo=html.escape(g.get('repo', ''), quote=True),
                        body=body, CARD_CSS=CARD_CSS)


def main():
    doc = json.loads(GAMES.read_text(encoding='utf-8'))
    OUT.mkdir(exist_ok=True)

    # 只处理收录的（source=upstream），站主自己那 15 款已有手写版
    targets = [g for g in doc['games'] if g.get('source') == 'upstream']

    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(build, targets))

    ok, card = 0, []
    for g, page in zip(targets, results):
        # build() 永不返回 None：取不到 README 也会退到资料卡
        (OUT / f'{g["id"]}.en.html').write_text(page, encoding='utf-8')
        langs = g.setdefault('readmeLangs', {})
        langs['default'] = 'en'
        langs['available'] = ['en']
        ok += 1
        if 'class="card"' in page:
            card.append(g['id'])

    GAMES.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'生成 {ok}/{len(targets)} 份 README 预览'
          f'（其中 {len(card)} 份上游 README 过简，用资料卡补全）')
    if card:
        print('  资料卡:', ', '.join(card))


if __name__ == '__main__':
    main()
