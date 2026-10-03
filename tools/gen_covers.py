#!/usr/bin/env python3
"""============================================================
 gen_covers.py · 游戏封面生成器
 15 张 SVG 封面全部由本脚本产出，改配色/构图后重跑即可。

 设计约定
   - 400×300（4:3），与 card__cover 的 aspect-ratio 一致
   - 深色饱和底 + 明亮主体，保证白色标题始终可读
   - 每个封面有明确的「场景」，而不是抽象几何拼贴
   - 统一底部渐隐条 + 珊瑚色圆点 + 小标签 + 大标题
   - 叠一层噪点，避免大面积渐变出现塑料感
============================================================"""

import math
import os

W, H = 400, 300
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "covers")

FONT = ("system-ui,-apple-system,'Segoe UI','Noto Sans CJK SC',"
        "'PingFang SC','Microsoft YaHei',sans-serif")

ACCENT = "#FF6B4A"      # 统一强调色（暖珊瑚）

# 是否在封面里写游戏名。默认 False —— 卡片组件已经在封面下方显示
# 标题和描述，封面里重复一遍既冗余又让画面变脏。
SHOW_TEXT = False


# ------------------------------------------------------------
# 基础工具
# ------------------------------------------------------------
def lin(gid, stops, x1=0, y1=0, x2=0, y2=1):
    s = "".join(
        f'<stop offset="{o}" stop-color="{c}"'
        + (f' stop-opacity="{a}"/>' if a is not None else "/>")
        for o, c, a in stops)
    return (f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
            f"{s}</linearGradient>")


def rad(gid, stops, cx=0.5, cy=0.5, r=0.5):
    s = "".join(
        f'<stop offset="{o}" stop-color="{c}"'
        + (f' stop-opacity="{a}"/>' if a is not None else "/>")
        for o, c, a in stops)
    return (f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}">{s}'
            "</radialGradient>")


def hexpts(cx, cy, r, rot=0):
    return " ".join(
        f"{cx + r * math.cos(math.radians(60 * i + rot)):.1f},"
        f"{cy + r * math.sin(math.radians(60 * i + rot)):.1f}"
        for i in range(6))


def soft_shadow(gid, dy=6, blur=9, op=0.34):
    return (f'<filter id="{gid}" x="-50%" y="-50%" width="200%" height="200%">'
            f'<feDropShadow dx="0" dy="{dy}" stdDeviation="{blur}" '
            f'flood-color="#000" flood-opacity="{op}"/></filter>')


def glow_filter(gid, blur=12, op=0.55):
    return (f'<filter id="{gid}" x="-60%" y="-60%" width="220%" height="220%">'
            f'<feGaussianBlur stdDeviation="{blur}" result="b"/>'
            f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/>'
            f"</feMerge></filter>")


NOISE = ('<filter id="nz" x="0" y="0" width="100%" height="100%">'
         '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3"'
         ' stitchTiles="stitch"/>'
         '<feColorMatrix type="saturate" values="0"/></filter>')

# 噪点纹理：作为纯灰度层低透明度平铺。
# 注意不要用 mix-blend-mode —— SVG 以 <img> 加载时混合模式会失效并盖黑整张图。
GRAIN = (f'<rect width="{W}" height="{H}" filter="url(#nz)" opacity="0.05"'
         ' style="mix-blend-mode:normal"/>')

# 暗角：中心必须完全透明（stop-opacity 缺省值是 1，写成 0 才透明），
# 否则中心半张图会被纯黑盖住。
VIGNETTE = rad("vg", [(0.45, "#000", 0), (0.78, "#000", 0.12), (1, "#000", 0.4)],
               cy=0.42, r=0.8)
SCRIM = lin("sc", [(0, "#000", 0), (0.45, "#000", 0.34), (1, "#000", 0.8)])


def fit_size(text, max_w, base, floor=16):
    """按字宽粗估字号：CJK 记 1em，西文记 0.56em。"""
    w = sum(1.0 if ord(c) > 0x2E80 else 0.56 for c in text)
    return base if w * base <= max_w else max(floor, round(max_w / w, 1))


def text_w(text, size):
    return sum((1.0 if ord(c) > 0x2E80 else 0.56) for c in text) * size


def wrap(title, kicker, bg_stops, extra_defs, scene):
    """把背景 / 场景 / 遮罩 / 文字组装成一张完整封面。

    SHOW_TEXT = False 时只输出纯画面：游戏名和类型都由卡片组件在封面
    下方显示，封面里再写一遍是重复信息，也会让画面变脏。
    """
    size = fit_size(title, 356, 29)
    cx = 22 + text_w(title, size) / 2      # 标题视觉中线
    label = ""
    if SHOW_TEXT:
        label = (
            f'<rect y="176" width="{W}" height="124" fill="url(#sc)"/>'
            f'<circle cx="25" cy="245" r="3.6" fill="{ACCENT}"/>'
            f'<text x="35" y="249" font-family="{FONT}" font-size="12.5" '
            f'font-weight="600" fill="#fff" fill-opacity="0.72" '
            f'letter-spacing="0.7">{kicker}</text>'
            f'<text x="{cx:.0f}" y="282" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="800" fill="#fff" '
            f'letter-spacing="-0.4">{title}</text>')
    else:
        # 纯画面：只在底部留一点压暗，托住卡片 hover 时浮现的渐隐条
        label = f'<rect y="216" width="{W}" height="84" fill="url(#sc)"/>'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{title} 封面"><defs>{lin("bg", bg_stops)}{rad("gl", [(0, "#fff", 0.2), (1, "#fff", 0)], cy=0.36, r=0.62)}{VIGNETTE}{SCRIM}{NOISE}{extra_defs}</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#gl)"/>
{scene}
<rect width="{W}" height="{H}" fill="url(#vg)"/>
{GRAIN}
{label}
<rect x="10.5" y="10.5" width="379" height="279" rx="14" fill="none" stroke="#fff" stroke-opacity="0.13" stroke-width="1.5"/></svg>"""


def tile(x, y, w, h, r, fill, label=None, fs=26, tc="#fff", op=None, sh="sh"):
    o = f' opacity="{op}"' if op else ""
    t = ""
    if label:
        t = (f'<text x="{x + w / 2}" y="{y + h / 2 + fs * 0.35:.0f}" '
             f'text-anchor="middle" font-family="{FONT}" font-size="{fs}" '
             f'font-weight="800" fill="{tc}" letter-spacing="-1">{label}</text>')
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            f'fill="{fill}"{o} filter="url(#{sh})"/>{t}')


# ------------------------------------------------------------
# 各游戏的场景
# ------------------------------------------------------------
def c_2048():
    d = (lin("t2", [(0, "#F6E7D2", None), (1, "#E3CBA6", None)]) +
         lin("t8", [(0, "#F7B267", None), (1, "#EE8A3C", None)]) +
         lin("t16", [(0, "#F0834E", None), (1, "#D95D2B", None)]) +
         lin("t64", [(0, "#EB5F3C", None), (1, "#C13F22", None)]) +
         soft_shadow("sh", dy=5, blur=8, op=0.4))
    s = f"""<g>
{tile(150, 44, 88, 88, 12, "url(#t2)", "2", 34, "#7A5B3A", sh="sh")}
{tile(246, 44, 88, 88, 12, "url(#t8)", "8", 34, "#fff")}
{tile(150, 140, 88, 88, 12, "url(#t16)", "16", 30, "#fff")}
{tile(246, 140, 88, 88, 12, "url(#t64)", "64", 30, "#fff", op=0.55)}
<rect x="62" y="60" width="70" height="70" rx="12" fill="#fff" opacity="0.07"/>
<rect x="58" y="152" width="78" height="78" rx="12" fill="#fff" opacity="0.05"/>
<path d="M300 96 l14 -14 M312 116 l20 -6" stroke="#FFD9A8" stroke-width="4" stroke-linecap="round" opacity="0.5"/>
<circle cx="88" cy="120" r="4" fill="#FFD9A8" opacity="0.65"/>
<circle cx="330" cy="150" r="5.5" fill="#FFE7C4" opacity="0.5"/>
</g>"""
    return d, s


def c_hextris():
    cells = ""
    rows = [(86, "#7FE8CE", 0.9), (86, "#3FC0A4", 0.75)]
    # 上方堆叠的三层六边形
    for i, (cx, r) in enumerate([(200, 34), (166, 34), (234, 34)]):
        cells += (f'<polygon points="{hexpts(cx, 96, r)}" fill="none" '
                  f'stroke="#A9F2E2" stroke-width="4" opacity="{0.9 - i * 0.18:.2f}"/>')
    cells += f'<polygon points="{hexpts(166, 158, 34)}" fill="#3FC7AA" opacity="0.95"/>'
    cells += f'<polygon points="{hexpts(234, 158, 34)}" fill="#3FC7AA" opacity="0.75"/>'
    cells += (f'<polygon points="{hexpts(200, 214, 36)}" fill="#FFCE4F" '
              f'filter="url(#gl2)"/>')
    d = glow_filter("gl2", 14, 0.5)
    s = f"""<g opacity="0.5">{''.join(
        f'<polygon points="{hexpts(x, y, 30)}" fill="none" stroke="#8FE0CE" stroke-width="1.6" opacity="0.28"/>'
        for x, y in [(100, 60), (166, 60), (232, 60), (298, 60),
                     (66, 126), (132, 126), (200, 126), (266, 126), (332, 126)])}
</g>
<g>{cells}</g>"""
    return d, s


def c_tower():
    blocks = ""
    # 塔身居中：所有块宽一致（w），左边缘围绕中线 200 对称错位
    w = 128
    for y, off, c in ((88, -10, "#DE7526"), (116, 8, "#F5AC5C"), (144, -6, "#E88B33"),
                      (172, 6, "#F09A45"), (200, -8, "#E07A2C")):
        x = 200 - w / 2 + off
        blocks += (f'<rect x="{x:.0f}" y="{y}" width="{w}" height="27" rx="8" fill="{c}"/>'
                   f'<rect x="{x:.0f}" y="{y}" width="{w}" height="8" rx="4" fill="#fff" opacity="0.28"/>'
                   f'<rect x="{x + w - 9:.0f}" y="{y}" width="9" height="27" rx="4" fill="#000" opacity="0.14"/>')
    d = soft_shadow("sh", dy=8, blur=12, op=0.3) + rad("sun", [(0, "#FFE9A8", 0.95), (1, "#FFC24A", 0)])
    s = f"""<circle cx="330" cy="58" r="52" fill="url(#sun)"/>
<g filter="url(#sh)">{blocks}</g>
<circle cx="330" cy="106" r="15" fill="#F44336" filter="url(#sh)"/>
<circle cx="325" cy="101" r="5" fill="#fff" opacity="0.45"/>
<path d="M330 130 l0 26 M330 90 l0 -16" stroke="#FFD9A8" stroke-width="3" stroke-linecap="round" opacity="0.45" stroke-dasharray="5 7"/>
<path d="M40 206 q26 -12 52 0" stroke="#FFD9A8" stroke-width="3" fill="none" opacity="0.28" stroke-linecap="round"/>"""
    return d, s


def c_pvz():
    d = (lin("lawn", [(0, "#5EA33C", None), (1, "#2F6B26", None)]) +
         soft_shadow("sh", dy=5, blur=7, op=0.35) + rad("sun2", [(0, "#FFF3B0", 0.9), (1, "#FFD24A", 0)]))
    s = f"""<circle cx="66" cy="58" r="34" fill="url(#sun2)"/>
<g opacity="0.35" fill="#FFF6C9">
<path d="M300 46 l0 16 M310 54 l-14 0 M307 50 l10 10 M307 58 l10 -10" stroke="#FFF6C9" stroke-width="3" stroke-linecap="round" fill="none"/>
</g>
<path d="M0 214 h400 v86 h-400 z" fill="url(#lawn)"/>
<g opacity="0.16" fill="#fff">
<rect x="0" y="214" width="400" height="14"/><rect x="0" y="242" width="400" height="14"/>
<rect x="0" y="270" width="400" height="14"/></g>
<path d="M0 214 h400" stroke="#1E4A18" stroke-width="3" opacity="0.5"/>
<g filter="url(#sh)">
<path d="M118 214 v-38" stroke="#3E8C2E" stroke-width="9" stroke-linecap="round"/>
<path d="M112 200 q-30 -4 -38 -24 q28 -2 38 24" fill="#57A83C"/>
<path d="M124 202 q28 -6 36 -26 q-28 0 -36 26" fill="#4C9635"/>
<circle cx="118" cy="150" r="27" fill="#63B845"/>
<circle cx="109" cy="144" r="5" fill="#1E4A18"/><circle cx="127" cy="144" r="5" fill="#1E4A18"/>
<path d="M103 162 q15 9 30 0" stroke="#1E4A18" stroke-width="3.4" fill="none" stroke-linecap="round"/>
<path d="M132 142 q18 -10 18 -26" stroke="#3E8C2E" stroke-width="6" fill="none" stroke-linecap="round"/>
<ellipse cx="151" cy="112" rx="8" ry="13" fill="#4C9635" transform="rotate(28 151 112)"/>
</g>
<g opacity="0.85" filter="url(#sh)">
<path d="M290 214 v-56" stroke="#4A5A6E" stroke-width="22" stroke-linecap="round"/>
<circle cx="290" cy="146" r="22" fill="#8FA3B8"/>
<circle cx="281" cy="141" r="4.2" fill="#2B3646"/><circle cx="299" cy="141" r="4.2" fill="#2B3646"/>
<path d="M280 158 q10 -6 20 0" stroke="#2B3646" stroke-width="3" fill="none" stroke-linecap="round"/>
<path d="M268 176 h-18" stroke="#4A5A6E" stroke-width="9" stroke-linecap="round"/>
<path d="M312 176 h18" stroke="#4A5A6E" stroke-width="9" stroke-linecap="round"/>
</g>"""
    return d, s


def c_trust():
    d = (rad("lens", [(0, "#FFD9A8", 0.95), (1, "#FF9A5A", 0.8)]) +
         soft_shadow("sh", dy=4, blur=10, op=0.3))
    s = f"""<g filter="url(#sh)">
<circle cx="166" cy="118" r="58" fill="#F5E3D0" opacity="0.16"/>
<circle cx="166" cy="118" r="58" fill="none" stroke="#F7DFC7" stroke-width="13"/>
<circle cx="234" cy="118" r="58" fill="#5A1410" opacity="0.3"/>
<circle cx="234" cy="118" r="58" fill="none" stroke="#FFD2A8" stroke-width="13" opacity="0.8"/>
</g>
<path d="M200 74 a58 58 0 0 1 0 88 a58 58 0 0 1 0 -88" fill="url(#lens)"/>
<circle cx="200" cy="118" r="9" fill="#FFF3DC"/>
<g opacity="0.4" stroke="#FFD2A8" stroke-width="2" fill="none">
<path d="M300 76 l0 84 M282 84 l36 68 M282 152 l36 -68"/></g>"""
    return d, s


def c_temple():
    d = (rad("s2", [(0, "#FFF0C2", 0.95), (1, "#FFC martian", 0)]) if False else
         rad("s2", [(0, "#FFF0C2", 0.95), (1, "#FFC24A", 0)]) +
         lin("st", [(0, "#5C3A1E", None), (1, "#38220F", None)]))
    cols = ""
    for x in (120, 160, 200, 240):
        cols += (f'<rect x="{x}" y="118" width="22" height="86" fill="url(#st)"/>'
                 f'<rect x="{x - 4}" y="112" width="30" height="10" rx="3" fill="#6B4526"/>'
                 f'<rect x="{x - 4}" y="200" width="30" height="10" rx="3" fill="#6B4526"/>')
    s = f"""<circle cx="200" cy="96" r="58" fill="url(#s2)"/>
<g opacity="0.45" fill="#7A4A22">
<polygon points="200,26 246,66 154,66"/>
<rect x="140" y="66" width="120" height="12" rx="4"/>
<rect x="152" y="78" width="96" height="9" rx="4"/></g>
<rect x="108" y="100" width="184" height="16" rx="5" fill="#6B4526"/>
{cols}
<rect x="96" y="204" width="208" height="18" rx="6" fill="#54341C"/>
<rect x="82" y="220" width="236" height="16" rx="6" fill="#43290F" opacity="0.85"/>
<g opacity="0.35" fill="#FFE6A8">
<polygon points="200,84 220,100 180,100"/></g>
<g stroke="#FFB347" stroke-width="4" stroke-linecap="round" opacity="0.5" fill="none">
<path d="M60 150 l-14 -10 M60 186 l-16 4 M340 150 l14 -10 M340 186 l16 4"/></g>"""
    return d, s


def c_wordle():
    d = (lin("wg", [(0, "#6AAA64", None), (1, "#4C7F48", None)]) +
         lin("wy", [(0, "#C9B458", None), (1, "#A8913C", None)]) +
         lin("wd", [(0, "#3E5A46", None), (1, "#2C4232", None)]) +
         lin("wn", [(0, "#22392C", None), (1, "#1A2C21", None)]) +
         soft_shadow("sh", dy=3, blur=6, op=0.4))
    cells = ""
    letters = ["C", "R", "A", "N", "N", "Y", "E", "O", "U", "P", "E"]
    kinds = ["g", "g", "d", "y", "d", "g", "d", "y", "d", "d", "d"]
    fills = {"g": "url(#wg)", "y": "url(#wy)", "d": "url(#wd)", "n": "url(#wn)"}
    for i, (ch, k) in enumerate(zip(letters, kinds)):
        r, c = divmod(i, 5)
        x, y = 74 + c * 52, 52 + r * 52
        tc = "#fff" if k in ("g", "y") else "#8FA898"
        cells += (f'<rect x="{x}" y="{y}" width="46" height="46" rx="7" fill="{fills[k]}" '
                  f'filter="url(#sh)"/>'
                  f'<text x="{x + 23}" y="{y + 32}" text-anchor="middle" font-family="{FONT}" '
                  f'font-size="26" font-weight="800" fill="{tc}" letter-spacing="0.5">{ch}</text>')
    s = f"""<g>{cells}</g>
<rect x="286" y="156" width="46" height="46" rx="7" fill="none" stroke="#6E8F7C" stroke-width="2.5" stroke-dasharray="5 5"/>
<rect x="290.5" y="176" width="3" height="16" rx="1.5" fill="#8FA898" opacity="0.8">
<animate attributeName="opacity" values="0.2;1;0.2" dur="1.1s" repeatCount="indefinite"/></rect>"""
    return d, s


def c_oddbot():
    d = (lin("hd", [(0, "#EDE6F7", None), (1, "#B9AEDA", None)]) +
         lin("hd2", [(0, "#FFD9A8", None), (1, "#F5A65B", None)]) +
         soft_shadow("sh", dy=4, blur=7, op=0.32))
    out = ""
    for i in range(9):
        r, c = divmod(i, 3)
        x, y = 108 + c * 64, 40 + r * 60
        odd = (i == 4)
        body = "url(#hd2)" if odd else "url(#hd)"
        eye = "#B4531F" if odd else "#4B3A6B"
        ant = "#FF8A4A" if odd else "#9C8CC4"
        out += f"""<g filter="url(#sh)">
<rect x="{x}" y="{y}" width="52" height="46" rx="12" fill="{body}"/>
<rect x="{x}" y="{y}" width="52" height="14" rx="7" fill="#fff" opacity="0.28"/>
<circle cx="{x + 17}" cy="{y + 25}" r="5.4" fill="{eye}"/>
<circle cx="{x + 35}" cy="{y + 25}" r="5.4" fill="{eye}"/>
<path d="M{x + 20} {y - 4} v-8" stroke="{ant}" stroke-width="3" stroke-linecap="round"/>
<circle cx="{x + 20}" cy="{y - 15}" r="4.6" fill="{ant}"/>
</g>"""
    ring = f'<rect x="168" y="96" width="76" height="80" rx="16" fill="none" stroke="#FF8A4A" stroke-width="3" stroke-dasharray="7 6" opacity="0.9"/>'
    return d, out + ring


def c_bubble():
    cols = ["#FF7EA8", "#FFD166", "#6ED6C0", "#7FB2FF", "#C79BFF"]
    import itertools
    bubbles = ""
    idx = itertools.count()
    for row in range(4):
        for col in range(6 - (row % 2)):
            i = next(idx)
            cx = 74 + col * 46 + (23 if row % 2 else 0)
            cy = 46 + row * 38
            c = cols[i % len(cols)]
            bubbles += (f'<circle cx="{cx}" cy="{cy}" r="20" fill="{c}" opacity="0.92"/>'
                        f'<circle cx="{cx - 6}" cy="{cy - 7}" r="6.5" fill="#fff" opacity="0.45"/>')
    d = soft_shadow("sh", dy=3, blur=6, op=0.3)
    s = f"""<g filter="url(#sh)">{bubbles}</g>
<g filter="url(#sh)">
<rect x="168" y="176" width="64" height="52" rx="14" fill="#F4F7FA"/>
<rect x="168" y="176" width="64" height="16" rx="8" fill="#fff" opacity="0.6"/>
<rect x="186" y="152" width="28" height="30" rx="8" fill="#E3EAF2"/>
<circle cx="200" cy="252" r="20" fill="#FF7EA8"/>
<circle cx="193" cy="245" r="6" fill="#fff" opacity="0.45"/>
</g>
<path d="M214 148 L266 96" stroke="#fff" stroke-width="3" stroke-dasharray="8 7" opacity="0.65" stroke-linecap="round"/>
<circle cx="274" cy="88" r="9" fill="#FFD166"/>"""
    return d, s


def c_dawn():
    d = (lin("sky", [(0, "#0B0B2A", None), (0.42, "#3A2160", None),
                     (0.72, "#A8425C", None), (1, "#F2913D", None)]) +
         rad("dawn", [(0, "#FFE0A0", 0.9), (1, "#FF9A3C", 0)]) +
         lin("hill", [(0, "#2A1A3E", None), (1, "#150C22", None)]))
    import random
    random.seed(7)
    stars = ""
    for _ in range(34):
        x, y = random.randint(12, 388), random.randint(10, 150)
        o = 0.3 + (1 - y / 150) * 0.6
        stars += f'<circle cx="{x}" cy="{y}" r="{random.choice([0.9, 1.2, 1.6])}" fill="#FFF6D8" opacity="{o:.2f}"/>'
    s = f"""{stars}
<circle cx="200" cy="204" r="72" fill="url(#dawn)"/>
<path d="M0 214 q60 -30 118 -14 q66 18 128 -6 q70 -26 154 6 v100 h-400 z" fill="url(#hill)"/>
<path d="M0 236 q76 -20 150 0 q80 22 160 -4 q54 -18 90 -2 v70 h-400 z" fill="#0D0718" opacity="0.9"/>
<g filter="url(#sh)">
<rect x="286" y="176" width="46" height="30" rx="7" fill="#2B2340"/>
<rect x="276" y="200" width="14" height="26" rx="4" fill="#3A2F55"/>
<rect x="330" y="200" width="14" height="26" rx="4" fill="#3A2F55"/>
<rect x="298" y="164" width="22" height="14" rx="5" fill="#4A3C6B"/>
<circle cx="309" cy="190" r="4.5" fill="#FF8A5C"/>
</g>
<g fill="#FFD98A">
<circle cx="176" cy="120" r="3.4" opacity="0.9"/><circle cx="150" cy="96" r="2.4" opacity="0.7"/>
<circle cx="196" cy="86" r="2" opacity="0.55"/></g>"""
    return d, s


def c_fc():
    d = (lin("crt", [(0, "#3B4460", None), (1, "#161A28", None)], 0, 0, 0, 1) +
         lin("pad", [(0, "#E8ECF5", None), (1, "#B6BECD", None)]) +
         rad("glw", [(0, "#7FD8FF", 0.55), (1, "#7FD8FF", 0)]) +
         soft_shadow("sh", dy=8, blur=12, op=0.45))
    scan = "".join(f'<rect y="{y}" width="400" height="1.4" fill="#000" opacity="0.24"/>'
                   for y in range(28, 190, 4))
    s = f"""<rect x="18" y="24" width="364" height="196" rx="18" fill="#2A3049" filter="url(#sh)"/>
<rect x="34" y="38" width="332" height="156" rx="10" fill="url(#crt)"/>
<rect x="34" y="38" width="332" height="156" rx="10" fill="url(#glw)"/>
<rect x="34" y="38" width="332" height="156" rx="10" fill="none" stroke="#8FE0FF" stroke-opacity="0.3" stroke-width="2"/>
<g clip-path="inset(38px 34px 106px 34px round 10px)">
<rect x="34" y="38" width="332" height="156" fill="none"/>
{scan}
</g>
<g>
<rect x="78" y="82" width="26" height="26" fill="#FF5C5C"/><rect x="104" y="82" width="26" height="26" fill="#FFD166"/>
<rect x="78" y="108" width="26" height="26" fill="#6ED6C0"/><rect x="104" y="108" width="26" height="26" fill="#7FB2FF"/>
<rect x="216" y="76" width="80" height="12" rx="3" fill="#7FE8CE" opacity="0.85"/>
<rect x="216" y="98" width="56" height="12" rx="3" fill="#FF8A5C" opacity="0.8"/>
<rect x="216" y="120" width="68" height="12" rx="3" fill="#FFD166" opacity="0.7"/>
<rect x="216" y="142" width="44" height="12" rx="3" fill="#C79BFF" opacity="0.7"/>
</g>
<g filter="url(#sh)">
<rect x="118" y="212" width="164" height="72" rx="26" fill="url(#pad)"/>
<rect x="118" y="212" width="164" height="26" rx="13" fill="#fff" opacity="0.5"/>
<path d="M156 232 h34 M173 215 v34" stroke="#39415C" stroke-width="11" stroke-linecap="round"/>
<circle cx="252" cy="230" r="9" fill="#E03A4E"/><circle cx="238" cy="250" r="9" fill="#E03A4E" opacity="0.7"/>
<circle cx="266" cy="250" r="9" fill="#2E7DE0" opacity="0.85"/>
<rect x="196" y="240" width="28" height="9" rx="4.5" fill="#8E97AC"/>
<rect x="192" y="258" width="36" height="9" rx="4.5" fill="#8E97AC"/>
</g>"""
    return d, s


def c_geo():
    d = (rad("globe", [(0, "#8FE3D2", 0.5), (1, "#1E6F7A", 0.15)]) +
         soft_shadow("sh", dy=6, blur=10, op=0.4))
    ell = []
    for i, rx in enumerate((78, 52, 26)):
        ell.append(f'<ellipse cx="176" cy="116" rx="{rx}" ry="82" fill="none" stroke="#9FF0DE" stroke-width="2.2" opacity="{0.55 - i * 0.12:.2f}"/>')
    lat = []
    for dy, rx in ((0, 82), (-40, 70), (40, 70), (-66, 50), (66, 50)):
        lat.append(f'<ellipse cx="176" cy="{116 + dy}" rx="{rx}" ry="{abs(dy) * 0.2 + 6}" fill="none" stroke="#9FF0DE" stroke-width="1.8" opacity="0.35"/>')
    s = f"""<g filter="url(#sh)">
<circle cx="176" cy="116" r="82" fill="#16697A"/>
<circle cx="176" cy="116" r="82" fill="url(#globe)"/>
<g>{''.join(lat)}{''.join(ell)}</g>
<path d="M132 78 q30 -10 44 12 q-18 16 -40 6 z" fill="#5FD6A8" opacity="0.75"/>
<path d="M198 132 q34 -8 30 26 q-16 22 -34 6 z" fill="#5FD6A8" opacity="0.6"/>
</g>
<g filter="url(#sh)">
<path d="M296 74 a26 26 0 0 1 26 26 c0 18 -26 40 -26 40 s-26 -22 -26 -40 a26 26 0 0 1 26 -26 z" fill="#FF6B4A"/>
<circle cx="296" cy="100" r="9.5" fill="#fff" fill-opacity="0.9"/>
</g>
<path d="M258 128 q-24 12 -34 4" stroke="#FFB199" stroke-width="2.6" fill="none" stroke-dasharray="5 6" stroke-linecap="round"/>
<g opacity="0.45" stroke="#9FF0DE" stroke-width="2" fill="none" stroke-linecap="round">
<path d="M60 60 q22 -18 48 -14"/><path d="M52 200 q26 20 56 14"/></g>"""
    return d, s


def c_remake():
    d = soft_shadow("sh", dy=5, blur=9, op=0.35)
    blocks = ""
    # 被打散、正在飞回原位的像素块
    flying = [(74, 62, "#FF7EA8", -18), (300, 70, "#FFD166", 14), (86, 168, "#6ED6C0", 10)]
    for x, y, c, rot in flying:
        blocks += (f'<rect x="{x}" y="{y}" width="30" height="30" rx="6" fill="{c}" '
                   f'opacity="0.9" transform="rotate({rot} {x + 15} {y + 15})" filter="url(#sh)"/>')
    grid = ""
    for r in range(3):
        for c in range(3):
            x, y = 152 + c * 34, 76 + r * 34
            filled = (r * 3 + c) in (0, 1, 3, 4, 7)
            if filled:
                grid += (f'<rect x="{x}" y="{y}" width="28" height="28" rx="6" '
                         f'fill="#C77DFF" filter="url(#sh)"/>'
                         f'<rect x="{x}" y="{y}" width="28" height="9" rx="4" fill="#fff" opacity="0.25"/>')
            else:
                grid += (f'<rect x="{x}" y="{y}" width="28" height="28" rx="6" fill="none" '
                         f'stroke="#E3C6FF" stroke-width="2" stroke-opacity="0.4" stroke-dasharray="5 5"/>')
    s = f"""<g opacity="0.28" stroke="#E3C6FF" stroke-width="2" fill="none" stroke-dasharray="6 7">
<path d="M110 76 q18 -6 34 0"/><path d="M114 168 q20 8 30 0"/><path d="M292 84 q-16 4 -22 14"/></g>
{blocks}
<g filter="url(#sh)"><rect x="146" y="70" width="110" height="110" rx="12" fill="#fff" opacity="0.05"/></g>
{grid}
<g transform="translate(318 196)" opacity="0.9">
<path d="M0 -26 a28 28 0 1 0 16 46 a23 23 0 1 1 -16 -46" fill="none" stroke="#7FE8CE" stroke-width="8" stroke-linecap="round"/>
<path d="M2 -40 l18 7 l-18 7 z" fill="#7FE8CE"/></g>"""
    return d, s


def c_weiqi():
    d = (lin("wood", [(0, "#C08A4E", None), (1, "#7A4E22", None)]) +
         lin("board", [(0, "#EFD5A6", None), (1, "#D9B87E", None)]) +
         rad("st1", [(0, "#6E6E78", 0.5), (0.5, "#15151B", None), (1, "#000", 0.55)]) +
         soft_shadow("sh", dy=3, blur=5, op=0.4))
    n, x0, y0, step = 9, 92, 40, 26
    gl = ""
    for i in range(n):
        gl += (f'<path d="M{x0} {y0 + i * step} H{x0 + (n - 1) * step}" stroke="#4A3418" '
               f'stroke-width="1.3" opacity="0.62"/>'
               f'<path d="M{x0 + i * step} {y0} V{y0 + (n - 1) * step}" stroke="#4A3418" '
               f'stroke-width="1.3" opacity="0.62"/>')
    gl += (f'<circle cx="{x0 + step * 2}" cy="{y0 + step * 2}" r="3.4" fill="#4A3418" opacity="0.62"/>'
           f'<circle cx="{x0 + step * 6}" cy="{y0 + step * 6}" r="3.4" fill="#4A3418" opacity="0.62"/>'
           f'<circle cx="{x0 + step * 4}" cy="{y0 + step * 4}" r="3.4" fill="#4A3418" opacity="0.62"/>')
    s = f"""<rect width="{W}" height="{H}" fill="url(#wood)"/>
<g opacity="0.14" stroke="#3E2712" stroke-width="3" fill="none">
<path d="M0 60 q100 14 200 0 t200 6"/><path d="M0 150 q100 -12 200 2 t200 -8"/></g>
<rect x="80" y="28" width="240" height="240" rx="10" fill="url(#board)" filter="url(#sh)"/>
<rect x="80" y="28" width="240" height="14" rx="7" fill="#fff" opacity="0.28"/>
{gl}
<g filter="url(#sh)">
<circle cx="{x0 + step * 2}" cy="{y0 + step * 2}" r="11.5" fill="url(#st1)"/>
<circle cx="{x0 + step * 5}" cy="{y0 + step * 3}" r="11.5" fill="url(#st1)"/>
<circle cx="{x0 + step * 4}" cy="{y0 + step * 6}" r="11.5" fill="url(#st1)"/>
</g>
<g filter="url(#sh)">
<circle cx="{x0 + step * 6}" cy="{y0 + step * 1}" r="11.5" fill="#FCFAF4"/>
<circle cx="{x0 + step * 6}" cy="{y0 + step * 1}" r="11.5" fill="none" stroke="#C9B896" stroke-width="1"/>
<circle cx="{x0 + step * 1}" cy="{y0 + step * 5}" r="11.5" fill="#FCFAF4"/>
<circle cx="{x0 + step * 1}" cy="{y0 + step * 5}" r="11.5" fill="none" stroke="#C9B896" stroke-width="1"/>
<circle cx="{x0 + step * 4}" cy="{y0 + step * 4}" r="11.5" fill="#FCFAF4" opacity="0.9"/>
</g>"""
    return d, s


def c_doudizhu():
    def card(x, y, rot, sym, col, rank):
        return f"""<g transform="rotate({rot} {x + 44} {y + 62})" filter="url(#sh)">
<rect x="{x}" y="{y}" width="88" height="124" rx="10" fill="#FDFAF3"/>
<rect x="{x}" y="{y}" width="88" height="124" rx="10" fill="none" stroke="#D9CDB4" stroke-width="1.5"/>
<text x="{x + 15}" y="{y + 30}" font-family="{FONT}" font-size="21" font-weight="800" fill="{col}">{rank}</text>
<text x="{x + 44}" y="{y + 92}" text-anchor="middle" font-family="{FONT}" font-size="50" fill="{col}">{sym}</text>
</g>"""

    d = (soft_shadow("sh", dy=8, blur=12, op=0.42) +
         lin("crown", [(0, "#FFE08A", None), (1, "#E0A32E", None)]))
    s = f"""<g opacity="0.22" stroke="#FFD98A" stroke-width="2.4" fill="none">
<path d="M40 60 l0 140 M360 60 l0 140 M28 78 h300 M28 182 h300"/></g>
<g transform="translate(200 24)">
<path d="M-34 34 l-8 -30 l20 14 l14 -22 l14 22 l20 -14 l-8 30 z" fill="url(#crown)"/>
<rect x="-36" y="33" width="72" height="9" rx="4.5" fill="#C98A1E"/>
<circle cx="0" cy="6" r="4" fill="#FFF3C4"/></g>
{card(74, 96, -13, "♠", "#1E2430", "A")}
{card(156, 90, 0, "♥", "#C62B3C", "K")}
{card(238, 96, 13, "♦", "#C62B3C", "Q")}"""
    return d, s


# ------------------------------------------------------------
# 登记表：id -> (标题, 标签, 底色渐变, 场景函数)
# ------------------------------------------------------------
COVERS = [
    ("2048",                 "2048",      "益智 · 数字",
     [(0, "#3A2010", None), (1, "#A65C1E", None)], c_2048),
    ("hextris",              "HEXTRIS",   "街机 · 反应",
     [(0, "#04211E", None), (1, "#0E7A66", None)], c_hextris),
    ("tower-game",           "叠塔",       "休闲 · 叠塔",
     [(0, "#3A1230", None), (1, "#C9452E", None)], c_tower),
    ("plants-vs-zombies",    "植物大战僵尸", "塔防 · 策略",
     [(0, "#10240F", None), (1, "#4E8A2E", None)], c_pvz),
    ("trust",                "TRUST",     "休闲 · 独立",
     [(0, "#2A0A0C", None), (1, "#A62B22", None)], c_trust),
    ("temple-of-boom",       "TEMPLE OF BOOM", "动作 · 闯关",
     [(0, "#26140A", None), (1, "#C98A2E", None)], c_temple),
    ("wordle-plus",          "WORDLE+",   "文字 · 猜词",
     [(0, "#0C2A24", None), (1, "#1E6F52", None)], c_wordle),
    ("odd-bot-out",          "ODD BOT OUT", "观察 · 找不同",
     [(0, "#1A1030", None), (1, "#5B3A9E", None)], c_oddbot),
    ("bubble-shooter",       "泡泡龙",     "街机 · 消除",
     [(0, "#0A1B33", None), (1, "#1E5B8A", None)], c_bubble),
    ("10-minutes-till-dawn", "黎明倒计时", "射击 · 生存",
     [(0, "#0B0B2A", None), (0.45, "#6B2C5A", None),
      (0.78, "#C4523F", None), (1, "#F2913D", None)], c_dawn),
    ("fcgame",               "FCGAME",    "模拟器 · 怀旧",
     [(0, "#14161F", None), (1, "#3A3F55", None)], c_fc),
    ("worldguessr",          "WORLDGUESSR", "地理 · 街景",
     [(0, "#06202E", None), (1, "#1C6E7A", None)], c_geo),
    ("remake",               "REMAKE",    "实验 · 待构建",
     [(0, "#24103A", None), (1, "#8E3FA8", None)], c_remake),
    ("fluid-weiqi-web",      "FLUID 围棋", "围棋 · 对弈",
     [(0, "#3A2416", None), (1, "#A9743C", None)], c_weiqi),
    ("fight-the-landlord",   "斗地主",     "斗地主 · AI",
     [(0, "#2A0810", None), (1, "#B02233", None)], c_doudizhu),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    for gid, title, kicker, bg, fn in COVERS:
        extra, scene = fn()
        svg = wrap(title, kicker, bg, extra, scene)
        path = os.path.join(OUT, f"{gid}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"  {gid:22s} {os.path.getsize(path):6d} B")


if __name__ == "__main__":
    print("生成封面 →", OUT)
    main()
