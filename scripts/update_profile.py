# Tu dong cap nhat profile: doc repo + ngon ngu tu GitHub API,
# ve lai assets/tech-galaxy.svg va cap nhat danh sach repo trong README.md
import json, os, random, re, urllib.request

USER = os.environ.get("GH_USER", "TPhPlyFking")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

COLORS = {
    "JavaScript": "#f7df1e", "TypeScript": "#3178c6", "HTML": "#e34f26", "CSS": "#2965f1",
    "Java": "#ed8b00", "C++": "#00599c", "C": "#a8b9cc", "Python": "#3776ab", "C#": "#a179dc",
    "PHP": "#777bb4", "Jupyter Notebook": "#f37626", "ShaderLab": "#e5e7eb", "HLSL": "#aace60",
    "Shell": "#89e051", "Dockerfile": "#2496ed", "SCSS": "#c6538c", "Vue": "#41b883",
}


def api(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", "Bearer " + TOKEN)
    with urllib.request.urlopen(req) as r:
        return json.load(r)


# 1. Lay danh sach repo (bo repo fork va repo profile)
repos = api(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed")
repos = [r for r in repos if not r["fork"] and r["name"] != USER]

# 2. Cong don so byte cua tung ngon ngu
langs = {}
for r in repos:
    for name, size in api(r["languages_url"]).items():
        langs[name] = langs.get(name, 0) + size
total = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda x: -x[1])[:15]

# 3. Ve Tech Galaxy: ngon ngu dung nhieu nhat nam o quy dao trong cung
W, H, cx, cy = 900, 560, 450, 280
orbits = [(110, 22, top[0:4]), (200, 34, top[4:9]), (290, 50, top[9:15])]
random.seed(3)
parts = []
for i in range(120):
    parts.append(f'<circle cx="{random.uniform(0, W):.0f}" cy="{random.uniform(0, H):.0f}" '
                 f'r="{random.choice([0.6, 0.9, 1.3])}" fill="#fff"><animate attributeName="opacity" '
                 f'values="0.2;1;0.2" dur="{random.uniform(2, 5):.1f}s" begin="{random.uniform(0, 3):.1f}s" '
                 f'repeatCount="indefinite"/></circle>')
for rx, dur, items in orbits:
    if not items:
        continue
    ry = round(rx * 0.42)
    parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#a78bfa" '
                 f'stroke-opacity="0.3" stroke-dasharray="4 6"/>')
    path = f"M {cx + rx} {cy} A {rx} {ry} 0 1 1 {cx - rx} {cy} A {rx} {ry} 0 1 1 {cx + rx} {cy}"
    for j, (name, size) in enumerate(items):
        col = COLORS.get(name, "#c4b5fd")
        label = f"{name} {size * 100 / total:.1f}%"
        w = len(label) * 7.5 + 24
        begin = -dur * j / len(items)
        parts.append(
            f'<g><circle r="9" fill="{col}" filter="url(#pg)"/>'
            f'<rect x="12" y="-11" width="{w:.0f}" height="22" rx="11" fill="#0f0b2a" fill-opacity="0.85" '
            f'stroke="{col}" stroke-opacity="0.8"/><text x="{12 + w / 2:.0f}" y="5" text-anchor="middle" '
            f'font-family="Segoe UI,Arial,sans-serif" font-size="12.5" font-weight="700" fill="#fff">{label}</text>'
            f'<animateMotion dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite" path="{path}"/></g>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
 <radialGradient id="bg2" cx="50%" cy="50%" r="70%"><stop offset="0" stop-color="#1e1250"/><stop offset="1" stop-color="#05040f"/></radialGradient>
 <radialGradient id="sun" cx="40%" cy="40%"><stop offset="0" stop-color="#fef9c3"/><stop offset="0.45" stop-color="#c084fc"/><stop offset="1" stop-color="#4c1d95"/></radialGradient>
 <radialGradient id="corona"><stop offset="0.4" stop-color="#a78bfa" stop-opacity="0.6"/><stop offset="1" stop-color="#a78bfa" stop-opacity="0"/></radialGradient>
 <filter id="pg"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="100%" height="100%" rx="18" fill="url(#bg2)"/>
{"".join(parts)}
<text x="{cx}" y="40" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="22" font-weight="800" fill="#e0e7ff" letter-spacing="5">✦ MY LANGUAGE GALAXY ✦</text>
<circle cx="{cx}" cy="{cy}" r="70" fill="url(#corona)"><animate attributeName="r" values="62;78;62" dur="4s" repeatCount="indefinite"/></circle>
<circle cx="{cx}" cy="{cy}" r="40" fill="url(#sun)"/>
<text x="{cx}" y="{cy + 7}" text-anchor="middle" font-family="Consolas,monospace" font-size="22" font-weight="700" fill="#1e1b4b">&lt;/&gt;</text>
<text x="{cx}" y="{H - 22}" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" font-size="13" fill="#a5b4fc">auto-generated from {len(repos)} repositories  •  closer orbit = used more</text>
</svg>'''
os.makedirs("assets", exist_ok=True)
with open("assets/tech-galaxy.svg", "w", encoding="utf-8") as f:
    f.write(svg)

# 4. Cap nhat bang "Latest repos" giua 2 dong danh dau trong README
rows = ["| 🪐 Repository | 📝 Description | 💻 Language | ⭐ |", "|---|---|---|---|"]
for r in repos[:6]:
    desc = (r["description"] or "—").replace("|", "/")
    rows.append(f"| [{r['name']}]({r['html_url']}) | {desc} | {r['language'] or '—'} | {r['stargazers_count']} |")
table = "\n".join(rows)

with open("README.md", encoding="utf-8") as f:
    readme = f.read()
readme = re.sub(r"(<!--REPOS:START-->).*?(<!--REPOS:END-->)",
                lambda m: m.group(1) + "\n" + table + "\n" + m.group(2), readme, flags=re.S)
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)


# ================= 5. Du lieu chung cho Terminal / HUD / Chom sao =================
from datetime import datetime, timezone, timedelta

user = api(f"https://api.github.com/users/{USER}")
now = datetime.now(timezone(timedelta(hours=7)))
created = datetime.strptime(user["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
days_on_github = (now - created).days
total_stars = sum(r["stargazers_count"] for r in repos)
last_push = repos[0]["pushed_at"][:10] if repos else "—"
top_lang = top[0][0] if top else "—"
top_pct = top[0][1] * 100 / total if top else 0
FONT_MONO = "Consolas,'Courier New',monospace"
FONT_SANS = "Segoe UI,Arial,sans-serif"


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ================= 6. Terminal sci-fi =================
lines = []  # (thoi diem hien ra, loai, noi dung, mau)
t = 0.5
def cmd(text):
    global t
    lines.append((t, "cmd", text, "#e0e7ff"))
    t += 0.06 * len(text) + 0.4


def out(text, color="#a5b4fc"):
    global t
    lines.append((t, "out", text, color))
    t += 0.15


cmd("whoami")
out("Trần Phát — Frontend Developer @ HCMUTE 🚀", "#67e8f9")
cmd("ls ~/projects --sort=recent")
for r in repos[:5]:
    out(f"  ▸ {r['name']:<38} {r['language'] or ''}", "#c4b5fd")
cmd("cat skills.json --top 4")
for name, size in top[:4]:
    pct = size * 100 / total
    bar = "█" * round(pct / 4) + "░" * (25 - round(pct / 4))
    out(f"  {name:<12} {bar} {pct:5.1f}%", COLORS.get(name, "#c4b5fd"))
cmd("uptime")
out(f"  exploring GitHub for {days_on_github} days · {len(repos)} repos · last push {last_push}", "#fbbf24")

TW, LH = 900, 22
TH = 70 + LH * (len(lines) + 1)
body = []
for i, (start, kind, text, color) in enumerate(lines):
    y = 62 + i * LH
    if kind == "cmd":
        w = (len(text) + 17) * 9.8 + 20  # 17 = do dai "phat@universe:~$ "
        body.append(f'<clipPath id="c{i}"><rect x="20" y="{y - 16}" height="22" width="0">'
                    f'<animate attributeName="width" from="0" to="{w:.0f}" begin="{start:.2f}s" '
                    f'dur="{0.06 * len(text):.2f}s" fill="freeze"/></rect></clipPath>')
        body.append(f'<text x="24" y="{y}" clip-path="url(#c{i})" font-family="{FONT_MONO}" font-size="16" fill="{color}">'
                    f'<tspan fill="#4ade80">phat@universe</tspan><tspan fill="#64748b">:</tspan>'
                    f'<tspan fill="#60a5fa">~</tspan><tspan fill="#64748b">$ </tspan>{esc(text)}</text>')
    else:
        body.append(f'<text x="24" y="{y}" font-family="{FONT_MONO}" font-size="15" fill="{color}" '
                    f'xml:space="preserve" opacity="0">{esc(text)}<set attributeName="opacity" to="1" '
                    f'begin="{start:.2f}s" fill="freeze"/></text>')
cy_end = 62 + len(lines) * LH
body.append(f'<text x="24" y="{cy_end}" font-family="{FONT_MONO}" font-size="16" opacity="0">'
            f'<tspan fill="#4ade80">phat@universe</tspan><tspan fill="#64748b">:~$ </tspan>'
            f'<tspan fill="#e0e7ff">█<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan>'
            f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/></text>')
terminal = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{TW}" height="{TH}" viewBox="0 0 {TW} {TH}">
<defs><linearGradient id="tb" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b0820"/><stop offset="1" stop-color="#140c33"/></linearGradient>
<filter id="tg"><feGaussianBlur stdDeviation="8"/></filter></defs>
<rect x="4" y="4" width="{TW - 8}" height="{TH - 8}" rx="14" fill="#7c3aed" opacity="0.35" filter="url(#tg)"/>
<rect x="2" y="2" width="{TW - 4}" height="{TH - 4}" rx="14" fill="url(#tb)" stroke="#7c3aed" stroke-opacity="0.6"/>
<rect x="2" y="2" width="{TW - 4}" height="32" rx="14" fill="#1e1546"/><rect x="2" y="20" width="{TW - 4}" height="14" fill="#1e1546"/>
<circle cx="24" cy="18" r="6" fill="#ff5f57"/><circle cx="44" cy="18" r="6" fill="#febc2e"/><circle cx="64" cy="18" r="6" fill="#28c840"/>
<text x="{TW / 2}" y="23" text-anchor="middle" font-family="{FONT_MONO}" font-size="13" fill="#a5b4fc">phat@universe: ~ — zsh — {TW}×{TH}</text>
{"".join(body)}
<rect x="2" y="34" width="{TW - 4}" height="3" fill="#67e8f9" opacity="0.08"><animate attributeName="y" values="34;{TH - 6};34" dur="6s" repeatCount="indefinite"/></rect>
</svg>'''
with open("assets/terminal.svg", "w", encoding="utf-8") as f:
    f.write(terminal)


# ================= 7. HUD bang dieu khien phi thuyen =================
random.seed(len(repos))
blips = "".join(
    f'<circle cx="{150 + random.uniform(-80, 80):.0f}" cy="{160 + random.uniform(-80, 80):.0f}" r="3" fill="#4ade80">'
    f'<animate attributeName="opacity" values="0;1;0" dur="4s" begin="{random.uniform(0, 4):.1f}s" repeatCount="indefinite"/></circle>'
    for _ in range(min(len(repos), 14)))


def gauge(x, label, value, color):
    return (f'<g transform="translate({x} 110)"><rect x="-70" y="-50" width="140" height="100" rx="10" fill="#0f0b2a" '
            f'stroke="{color}" stroke-opacity="0.6"/><text y="10" text-anchor="middle" font-family="{FONT_MONO}" '
            f'font-size="34" font-weight="700" fill="{color}">{value}</text><text y="36" text-anchor="middle" '
            f'font-family="{FONT_SANS}" font-size="11" letter-spacing="2" fill="#a5b4fc">{label}</text></g>')


ring_len = 2 * 3.1416 * 60
hud = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="320" viewBox="0 0 900 320">
<defs><radialGradient id="rad"><stop offset="0" stop-color="#14532d" stop-opacity="0.6"/><stop offset="1" stop-color="#052e16" stop-opacity="0.1"/></radialGradient>
<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#4ade80" stop-opacity="0"/><stop offset="1" stop-color="#4ade80" stop-opacity="0.6"/></linearGradient></defs>
<rect x="2" y="2" width="896" height="316" rx="16" fill="#07051a" stroke="#7c3aed" stroke-opacity="0.5"/>
<path d="M 20 20 h 40 M 20 20 v 40 M 880 20 h -40 M 880 20 v 40 M 20 300 h 40 M 20 300 v -40 M 880 300 h -40 M 880 300 v -40" stroke="#67e8f9" stroke-width="2"/>
<text x="450" y="34" text-anchor="middle" font-family="{FONT_MONO}" font-size="15" letter-spacing="6" fill="#67e8f9">◤ MISSION CONTROL ◢</text>
<g><circle cx="150" cy="160" r="100" fill="url(#rad)" stroke="#4ade80" stroke-opacity="0.6"/>
<circle cx="150" cy="160" r="66" fill="none" stroke="#4ade80" stroke-opacity="0.3"/><circle cx="150" cy="160" r="33" fill="none" stroke="#4ade80" stroke-opacity="0.3"/>
<path d="M 50 160 H 250 M 150 60 V 260" stroke="#4ade80" stroke-opacity="0.25"/>
<path d="M 150 160 L 250 160 A 100 100 0 0 0 220.7 89.3 Z" fill="url(#sweep)"><animateTransform attributeName="transform" type="rotate" from="0 150 160" to="360 150 160" dur="4s" repeatCount="indefinite"/></path>
{blips}<text x="150" y="285" text-anchor="middle" font-family="{FONT_MONO}" font-size="11" fill="#4ade80">SCANNING {len(repos)} REPOS</text></g>
{gauge(340, "REPOSITORIES", len(repos), "#c4b5fd")}{gauge(500, "STARS", total_stars, "#fbbf24")}
{gauge(340, "LANGUAGES", len(langs), "#67e8f9").replace("translate(340 110)", "translate(340 225)")}
{gauge(500, "DAYS IN ORBIT", days_on_github, "#f472b6").replace("translate(500 110)", "translate(500 225)")}
<g transform="translate(730 160)"><circle r="60" fill="none" stroke="#1e1546" stroke-width="14"/>
<circle r="60" fill="none" stroke="{COLORS.get(top_lang, "#c4b5fd")}" stroke-width="14" stroke-linecap="round" transform="rotate(-90)" stroke-dasharray="0 {ring_len:.0f}">
<animate attributeName="stroke-dasharray" from="0 {ring_len:.0f}" to="{ring_len * top_pct / 100:.0f} {ring_len:.0f}" dur="2s" fill="freeze"/></circle>
<text y="2" text-anchor="middle" font-family="{FONT_MONO}" font-size="24" font-weight="700" fill="#fff">{top_pct:.0f}%</text>
<text y="24" text-anchor="middle" font-family="{FONT_SANS}" font-size="12" fill="#a5b4fc">{esc(top_lang)}</text>
<text y="-80" text-anchor="middle" font-family="{FONT_SANS}" font-size="11" letter-spacing="2" fill="#a5b4fc">PRIMARY FUEL</text>
<text y="100" text-anchor="middle" font-family="{FONT_MONO}" font-size="11" fill="#64748b">LAST PUSH {last_push}</text></g>
<text x="450" y="306" text-anchor="middle" font-family="{FONT_MONO}" font-size="10" fill="#475569">LAST SYNC {now:%Y-%m-%d %H:%M} (UTC+7) · AUTO-UPDATED BY GITHUB ACTIONS</text>
</svg>'''
with open("assets/hud.svg", "w", encoding="utf-8") as f:
    f.write(hud)


# ================= 8. Chom sao du an =================
CW, CH = 900, 400
pts = []
for i, r in enumerate(repos[:8]):
    rnd = random.Random(r["name"])  # vi tri co dinh theo ten repo
    col_x = 90 + i * (CW - 180) / max(len(repos[:8]) - 1, 1)
    # sao chan nam tren cao, sao le nam duoi thap -> chu khong de len nhau
    y = rnd.uniform(130, 190) if i % 2 == 0 else rnd.uniform(240, 300)
    pts.append((col_x, y, r))
star_parts, link_parts = [], []
for i in range(len(pts) - 1):
    (x1, y1, _), (x2, y2, _) = pts[i], pts[i + 1]
    link_parts.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#a78bfa" stroke-opacity="0.5" '
                      f'stroke-width="1.2" stroke-dasharray="300" stroke-dashoffset="300"><animate attributeName="stroke-dashoffset" '
                      f'from="300" to="0" begin="{0.3 * i:.1f}s" dur="0.8s" fill="freeze"/></line>')
for i, (x, y, r) in enumerate(pts):
    size = 4 + min(r["size"], 20000) ** 0.25
    col = COLORS.get(r["language"], "#e0e7ff")
    label_y = y - size * 1.6 - 10 if i % 2 == 0 else y + size * 1.6 + 20
    star_parts.append(
        f'<g opacity="0"><set attributeName="opacity" to="1" begin="{0.3 * i:.1f}s" fill="freeze"/>'
        f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{size * 2.5:.1f}" fill="{col}" opacity="0.15"><animate attributeName="r" '
        f'values="{size * 2:.1f};{size * 3:.1f};{size * 2:.1f}" dur="{2 + i % 3}s" repeatCount="indefinite"/></circle>'
        f'<path d="M {x:.0f} {y - size * 1.6:.0f} L {x + size * 0.35:.1f} {y:.0f} L {x:.0f} {y + size * 1.6:.0f} L {x - size * 0.35:.1f} {y:.0f} Z '
        f'M {x - size * 1.6:.0f} {y:.0f} L {x:.0f} {y + size * 0.35:.1f} L {x + size * 1.6:.0f} {y:.0f} L {x:.0f} {y - size * 0.35:.1f} Z" fill="#fff"/>'
        f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{size * 0.6:.1f}" fill="{col}"/>'
        f'<text x="{x:.0f}" y="{label_y:.0f}" text-anchor="middle" font-family="{FONT_SANS}" font-size="11.5" '
        f'font-weight="600" fill="#e0e7ff">{esc(r["name"].strip("-")[:20])}</text></g>')
random.seed(5)
bg_stars = "".join(f'<circle cx="{random.uniform(0, CW):.0f}" cy="{random.uniform(0, CH):.0f}" r="{random.choice([0.5, 0.8, 1.1])}" '
                   f'fill="#fff" opacity="{random.uniform(0.2, 0.8):.2f}"/>' for _ in range(150))
constellation = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}">
<defs><radialGradient id="cbg" cx="50%" cy="40%" r="75%"><stop offset="0" stop-color="#160d3a"/><stop offset="1" stop-color="#03020a"/></radialGradient></defs>
<rect width="100%" height="100%" rx="18" fill="url(#cbg)"/>{bg_stars}
<text x="{CW / 2}" y="44" text-anchor="middle" font-family="{FONT_SANS}" font-size="20" font-weight="800" letter-spacing="6" fill="#e0e7ff">✧ CONSTELLATION PHÁT MAJOR ✧</text>
<text x="{CW / 2}" y="66" text-anchor="middle" font-family="{FONT_MONO}" font-size="12" fill="#a5b4fc">each star is a repository · bigger star = bigger project · auto-updated</text>
{"".join(link_parts)}{"".join(star_parts)}
</svg>'''
with open("assets/constellation.svg", "w", encoding="utf-8") as f:
    f.write(constellation)

print("Updated:", len(repos), "repos,", len(langs), "languages")
