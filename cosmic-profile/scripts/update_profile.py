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

print("Updated:", len(repos), "repos,", len(langs), "languages")
