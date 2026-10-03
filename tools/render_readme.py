#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_readme.py · 把 readme/{id}.{lang}.md 渲染为自包含的 {id}.{lang}.html

- 内联 GitHub 风格样式，零外网依赖（不引 CDN）
- 浅色为默认，prefers-color-scheme 深色自动适配
- 同时支持 html[data-theme="dark"/"light"]，由 detail.js 同步站点主题
用法：python3 tools/render_readme.py
"""
import glob
import re
import os
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "readme")

CSS = """
:root{
  --bg:#ffffff; --fg:#1f2328; --muted:#59636e; --border:#d1d9e0;
  --code-bg:#f6f8fa; --quote-bg:#f6f8fa; --link:#ff5a36; --accent:#ff5a36;
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#0d1117; --fg:#e6edf3; --muted:#9198a1; --border:#3d444d;
    --code-bg:#161b22; --quote-bg:#161b22; --link:#ff7a58; --accent:#ff7a58;
  }
}
html[data-theme="light"]{
  --bg:#ffffff; --fg:#1f2328; --muted:#59636e; --border:#d1d9e0;
  --code-bg:#f6f8fa; --quote-bg:#f6f8fa; --link:#ff5a36; --accent:#ff5a36;
}
html[data-theme="dark"]{
  --bg:#0d1117; --fg:#e6edf3; --muted:#9198a1; --border:#3d444d;
  --code-bg:#161b22; --quote-bg:#161b22; --link:#ff7a58; --accent:#ff7a58;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--bg);color:var(--fg)}
body{
  padding:18px 20px 22px;
  font:15px/1.68 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",
       "Hiragino Sans GB","Microsoft YaHei",system-ui,sans-serif;
  overflow-wrap:break-word;
}
a{color:var(--link);text-decoration:none}
a:hover{text-decoration:underline}
h1,h2,h3,h4,h5{line-height:1.3;margin:1.4em 0 .6em;font-weight:800;letter-spacing:-.01em}
h1{font-size:1.9em;margin-top:.2em;padding-bottom:.3em;border-bottom:1px solid var(--border)}
h2{font-size:1.4em;padding-bottom:.3em;border-bottom:1px solid var(--border)}
h3{font-size:1.15em}
p{margin:.7em 0}
ul,ol{padding-left:1.5em;margin:.7em 0}
li{margin:.3em 0}
img{max-width:100%;height:auto;border-radius:8px}
code{
  background:var(--code-bg);padding:.15em .4em;border-radius:6px;
  font:0.88em/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
pre{
  background:var(--code-bg);padding:14px 16px;border-radius:10px;overflow:auto;
  border:1px solid var(--border);
}
pre code{background:none;padding:0;font-size:13px}
blockquote{
  margin:.8em 0;padding:.5em 1em;border-left:4px solid var(--accent);
  background:var(--quote-bg);color:var(--muted);border-radius:0 8px 8px 0;
}
blockquote>:first-child{margin-top:0}
blockquote>:last-child{margin-bottom:0}
table{border-collapse:collapse;margin:1em 0;display:block;overflow:auto;max-width:100%}
th,td{border:1px solid var(--border);padding:8px 12px;text-align:left}
th{background:var(--code-bg);font-weight:700}
tr:nth-child(2n){background:color-mix(in srgb,var(--code-bg) 40%,transparent)}
hr{border:0;border-top:1px solid var(--border);margin:1.6em 0}
strong{font-weight:800}
"""

TPL = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body class="markdown-body">
{body}
</body>
</html>
"""


def render(md_path: str):
    name = os.path.basename(md_path)[:-3]          # {id}.{lang}
    gid, _, lang = name.rpartition(".")
    text = open(md_path, encoding="utf-8").read()
    # README 会以 srcdoc 注入 iframe，基准是站点根目录，
    # 去掉 ../ 前缀并剥掉 md 里多余的换行尖括号，避免 404
    text = re.sub(r'src="\.\./+', 'src="', text)
    text = text.replace('"><br>', '">')
    html = markdown.markdown(
        text, extensions=["tables", "fenced_code", "nl2br", "sane_lists"]
    )
    # 图片加载失败时隐藏破图
    html = html.replace(
        "<img ", '<img onerror="this.remove()" loading="lazy" '
    )
    title = gid
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    out = os.path.join(SRC, name + ".html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(TPL.format(lang="zh-CN" if lang == "zh" else "en",
                           title=title, css=CSS, body=html))
    return out, os.path.getsize(out)


if __name__ == "__main__":
    total = 0
    for md in sorted(glob.glob(os.path.join(SRC, "*.md"))):
        out, size = render(md)
        total += size
        print(f"{os.path.basename(out):34s} {size:>7d} B")
    print(f"---\n{len(glob.glob(os.path.join(SRC,'*.md')))} 个文件，共 {total} B")
