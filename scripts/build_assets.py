#!/usr/bin/env python3
"""Generates the animated SVG assets used by README.md.

Edit the PROJECTS / SECTIONS data below, then run:
    python3 scripts/build_assets.py
"""
import math
import random
from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'SF Pro Display', Inter, Helvetica, Arial, sans-serif"
MONO = "'SF Mono', ui-monospace, 'JetBrains Mono', Menlo, Consolas, monospace"

BG = "#0A0C12"
CARD = "#0F121A"
INK = "#F4F6FB"
MUTED = "#9AA3B5"
DIM = "#5C6476"
CYAN = "#54C5F8"
VIOLET = "#7C5CFF"
MINT = "#2EE6A6"

PROJECTS = [
    {
        "slug": "allah-everywhere", "mono": "AE", "title": "Allah Everywhere", "lang": "Dart",
        "lang_color": "#00B4AB", "accent": "#2EE6A6",
        "desc": "Prayer times, Quran & Hifz, Hadith, Qibla and family challenges with rewards. One app for iOS & Android in 8 languages.",
        "tags": ["Flutter", "Firebase", "8 languages"],
    },
    {
        "slug": "field-sales", "mono": "FS", "title": "Field Sales Management", "lang": "TypeScript",
        "lang_color": "#3178C6", "accent": "#54C5F8",
        "desc": "GPS attendance with geofencing & fraud detection, live rep tracking, sales targets and catalogue sharing. English / Arabic RTL.",
        "tags": ["Flutter", "React", "NestJS", "PostGIS"],
    },
    {
        "slug": "arrowtech-erp", "mono": "AT", "title": "ArrowTech Wristband ERP", "lang": "TypeScript",
        "lang_color": "#3178C6", "accent": "#7C5CFF",
        "desc": "Multi-tenant ERP for badge manufacturing: sales, design proofing, realtime print-floor dispatch, inventory and ZATCA accounting.",
        "tags": ["TypeScript", "Realtime", "Multi-tenant"],
    },
    {
        "slug": "voltstore", "mono": "VS", "title": "VoltStore", "lang": "TypeScript",
        "lang_color": "#3178C6", "accent": "#FF5C7A",
        "desc": "A Redis-compatible in-memory store built from scratch: custom RESP parser, concurrent TCP server, TTL engine and live dashboard.",
        "tags": ["TypeScript", "TCP", "RESP", "Systems"],
    },
    {
        "slug": "nexus-browser", "mono": "NX", "title": "Nexus Browser", "lang": "JavaScript",
        "lang_color": "#F1E05A", "accent": "#FFB547",
        "desc": "A custom desktop browser with a frameless glassmorphic HUD, multi-tab webviews, a live tracker blocker and a new-tab dashboard.",
        "tags": ["Electron", "JavaScript", "Desktop"],
    },
    {
        "slug": "aura-match", "mono": "AM", "title": "Aura Match", "lang": "Dart",
        "lang_color": "#00B4AB", "accent": "#B26BFF",
        "desc": "The AI that finds your next job while you sleep. Matches profiles to openings and does the busywork for you.",
        "tags": ["Flutter", "Node.js", "Groq AI"],
    },
]

SECTIONS = [
    ("services", "01", "What I build for clients"),
    ("work", "02", "Featured work"),
    ("about", "03", "About me"),
    ("stack", "04", "Toolbox"),
    ("activity", "05", "Activity"),
]


def write(name, svg):
    (OUT / name).write_text(svg.strip() + "\n", encoding="utf-8")
    print("wrote", OUT / name)


# ---------------------------------------------------------------- hero
def stars(n, seed=7):
    """Deterministic twinkling starfield."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(20, 1180), rnd.uniform(20, 420)
        r = rnd.choice([.6, .8, 1, 1.2, 1.6])
        out.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" class="tw" '
            f'style="animation-duration:{rnd.uniform(2.5, 6):.1f}s;animation-delay:-{rnd.uniform(0, 6):.1f}s"/>'
        )
    return "\n  ".join(out)



def silk(n, seed_phase, amp, spread, center, xs, opacity):
    """A twisting ribbon of n hairlines whose shape morphs between three keyframes."""
    def d(t, k):
        ph = seed_phase + k * 2 * math.pi / 3
        ys = [center + amp * math.sin(ph + j * 1.15) + (t - .5) * spread * math.sin(ph * 1.3 + j * 1.6)
              for j in range(4)]
        return f"M{xs[0]} {ys[0]:.1f}C{xs[1]} {ys[1]:.1f} {xs[2]} {ys[2]:.1f} {xs[3]} {ys[3]:.1f}"

    out = []
    for i in range(n):
        t = i / (n - 1)
        frames = [d(t, k) for k in range(3)]
        o = opacity * (.25 + .75 * math.sin(math.pi * t))
        out.append(
            f'<path d="{frames[0]}" fill="none" stroke="url(#silk)" stroke-width="{.7 + .5 * math.sin(math.pi * t):.2f}" opacity="{o:.2f}">'
            f'<animate attributeName="d" dur="16s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.33;.66;1" '
            f'keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1" values="{";".join(frames + frames[:1])}"/></path>'
        )
    return "\n  ".join(out)


def hero():
    words = ["apps your users love", "ERPs that scale", "Arabic & English RTL apps", "offline-first desktop systems"]
    cycle = len(words) * 3
    show = 3 / cycle * 100
    word_nodes = "\n  ".join(
        f'<text class="word w{i}" x="80" y="346" font-family="{MONO}" font-size="17" fill="url(#ink)">'
        f'<tspan fill="{DIM}">building </tspan>{escape(w)}<tspan class="caret" fill="{CYAN}"> ▍</tspan></text>'
        for i, w in enumerate(words)
    )
    word_css = " ".join(f".w{i}{{animation:word {cycle}s {i * 3 - 1}s infinite both}}" for i in range(len(words)))
    xs = [-80, 420, 820, 1280]
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="440" viewBox="0 0 1200 440" role="img" aria-label="Muhammad Abdullah Waseem, Flutter Developer for iOS, Android and Windows apps">
<defs>
  <linearGradient id="ink" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".55" stop-color="#A78BFF"/><stop offset="1" stop-color="#FF8AD0"/></linearGradient>
  <linearGradient id="silk" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="1200" y2="0">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".45" stop-color="#A78BFF"/><stop offset=".8" stop-color="#FF8AD0"/><stop offset="1" stop-color="{CYAN}"/>
  </linearGradient>
  <linearGradient id="shimmer" gradientUnits="userSpaceOnUse" x1="-400" y1="0" x2="400" y2="0" spreadMethod="reflect">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".35" stop-color="#A78BFF"/><stop offset=".5" stop-color="#ffffff"/><stop offset=".65" stop-color="#A78BFF"/><stop offset="1" stop-color="#FF8AD0"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="800 0" dur="7s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="edge" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".5"/><stop offset=".5" stop-color="#ffffff" stop-opacity=".05"/><stop offset="1" stop-color="{VIOLET}" stop-opacity=".5"/></linearGradient>
  <linearGradient id="hair" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity=".25"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="reveal" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity=".12"/><stop offset=".42" stop-color="#fff" stop-opacity=".3"/><stop offset=".7" stop-color="#fff"/></linearGradient>
  <mask id="fadeLeft"><rect width="1200" height="440" fill="url(#reveal)"/></mask>
  <filter id="blur" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="80"/></filter>
  <filter id="glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="soft" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="4"/></filter>
  <clipPath id="frame"><rect width="1200" height="440" rx="28"/></clipPath>
</defs>
<style>
  @keyframes drift1{{0%,100%{{transform:translate(0,0) scale(1)}}50%{{transform:translate(140px,50px) scale(1.15)}}}}
  @keyframes drift2{{0%,100%{{transform:translate(0,0) scale(1.1)}}50%{{transform:translate(-160px,-40px) scale(.9)}}}}
  @keyframes twinkle{{0%,100%{{opacity:.08}}50%{{opacity:.85}}}}
  @keyframes pulse{{0%{{transform:scale(1);opacity:.7}}100%{{transform:scale(3.2);opacity:0}}}}
  @keyframes word{{0%{{opacity:0;transform:translateY(8px)}}{show * .15:.2f}%,{show * .85:.2f}%{{opacity:1;transform:none}}{show:.2f}%,100%{{opacity:0;transform:translateY(-8px)}}}}
  @keyframes blink{{50%{{opacity:0}}}}
  @keyframes travel{{0%{{transform:translateX(0);opacity:0}}10%,80%{{opacity:1}}100%{{transform:translateX(420px);opacity:0}}}}
  .b1{{animation:drift1 16s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
  .b2{{animation:drift2 21s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
  .tw{{animation:twinkle 4s ease-in-out infinite}}
  .ring{{transform-box:fill-box;transform-origin:center;animation:pulse 2.4s ease-out infinite}}
  .word{{opacity:0}} {word_css}
  .caret{{animation:blink 1.1s steps(1) infinite}}
  .spark{{animation:travel 5s cubic-bezier(.4,0,.2,1) infinite}}
</style>

<g clip-path="url(#frame)">
  <rect width="1200" height="440" fill="#06070B"/>
  <ellipse class="b1" cx="240" cy="80" rx="260" ry="170" fill="{CYAN}" opacity=".13" filter="url(#blur)"/>
  <ellipse class="b2" cx="900" cy="240" rx="320" ry="190" fill="{VIOLET}" opacity=".26" filter="url(#blur)"/>
  <ellipse class="b1" cx="620" cy="470" rx="240" ry="120" fill="#FF5CA8" opacity=".12" filter="url(#blur)"/>
  {stars(60)}
  <g mask="url(#fadeLeft)" filter="url(#glow)">
  {silk(34, 0.0, 70, 150, 230, xs, .9)}
  {silk(22, 2.1, 90, 90, 250, xs, .45)}
  </g>
</g>
<rect x=".75" y=".75" width="1198.5" height="438.5" rx="27.5" fill="none" stroke="url(#edge)" stroke-width="1.2"/>

<rect x="80" y="72" width="150" height="32" rx="16" fill="#06070B" fill-opacity=".6" stroke="#ffffff" stroke-opacity=".14"/>
<circle class="ring" cx="101" cy="88" r="4" fill="{MINT}"/>
<circle cx="101" cy="88" r="4" fill="{MINT}"/>
<text x="115" y="92.5" font-family="{MONO}" font-size="11.5" letter-spacing="2.5" fill="{INK}" opacity=".9">OPEN TO WORK</text>

<text x="76" y="176" font-family="{SANS}" font-size="62" font-weight="300" letter-spacing="-1.5" fill="{INK}">Muhammad Abdullah</text>
<text x="76" y="248" font-family="{SANS}" font-size="62" font-weight="700" letter-spacing="-1.5" fill="url(#shimmer)">Waseem</text>
<rect x="80" y="274" width="420" height="1" fill="url(#hair)"/>
<circle class="spark" cx="80" cy="274.5" r="2" fill="#fff"/>
<circle class="spark" cx="80" cy="274.5" r="7" fill="{CYAN}" opacity=".35" filter="url(#soft)"/>
<text x="80" y="308" font-family="{SANS}" font-size="19" fill="{MUTED}">Flutter Developer · iOS, Android &amp; Windows apps</text>
{word_nodes}
<text x="1120" y="400" text-anchor="end" font-family="{MONO}" font-size="11" letter-spacing="3" fill="{INK}" opacity=".45">JEDDAH, SAUDI ARABIA · REMOTE WORLDWIDE</text>
</svg>"""


# ---------------------------------------------------------------- metrics strip
METRICS = [("4", "apps live on the stores"), ("17", "engineers led"), ("8", "languages shipped"), ("30+", "projects on GitHub")]


def metrics():
    w, h, col = 1200, 170, 1200 / len(METRICS)
    cells = []
    for i, (num, label) in enumerate(METRICS):
        cx = col * i + col / 2
        cells.append(
            f'<text x="{cx:.0f}" y="92" text-anchor="middle" font-family="{SANS}" font-size="58" font-weight="200" letter-spacing="-1" fill="url(#ink)">{num}</text>'
            f'<text x="{cx:.0f}" y="126" text-anchor="middle" font-family="{MONO}" font-size="12" letter-spacing="2.5" fill="{MUTED}">{escape(label.upper())}</text>'
        )
        if i:
            cells.append(f'<rect x="{col * i:.0f}" y="42" width="1" height="96" fill="url(#vline)"/>')
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(', '.join(f'{n} {l}' for n, l in METRICS))}">
<defs>
  <linearGradient id="ink" x1="80" x2="1120" gradientUnits="userSpaceOnUse" y1="0" y2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="#A78BFF"/><stop offset="1" stop-color="#FF8AD0"/></linearGradient>
  <linearGradient id="vline" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".18"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".45"/><stop offset=".5" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#FF8AD0" stop-opacity=".45"/></linearGradient>
  <clipPath id="c"><rect width="{w}" height="{h}" rx="24"/></clipPath>
</defs>
<style>
  @keyframes sweep{{from{{transform:translateX(-300px)}}to{{transform:translateX({w + 300}px)}}}}
  .sweep{{animation:sweep 9s ease-in-out infinite}}
</style>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="#0B0D14"/>
  <rect class="sweep" x="0" y="-60" width="120" height="{h + 120}" fill="#fff" opacity=".035" transform="skewX(-20)"/>
</g>
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="23.25" fill="none" stroke="url(#edge)" stroke-width="1.2"/>
{''.join(cells)}
</svg>"""


# ---------------------------------------------------------------- call to action
def cta():
    w, h = 1200, 230
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Have an app idea? Let's build it together. Start a project.">
<defs>
  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".3" stop-color="#ffffff" stop-opacity=".05"/><stop offset=".6" stop-color="#A78BFF"/><stop offset=".85" stop-color="#ffffff" stop-opacity=".05"/><stop offset="1" stop-color="#FF8AD0"/>
    <animateTransform attributeName="gradientTransform" type="rotate" values="0 .5 .5;360 .5 .5" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="btn" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".55" stop-color="#A78BFF"/><stop offset="1" stop-color="#FF8AD0"/></linearGradient>
  <radialGradient id="glow" cx=".5" cy="1" r=".8"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".35"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
  <filter id="soft" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="14"/></filter>
  <clipPath id="c"><rect width="{w}" height="{h}" rx="28"/></clipPath>
</defs>
<style>
  @keyframes breathe{{0%,100%{{opacity:.35}}50%{{opacity:.8}}}}
  .halo{{animation:breathe 4s ease-in-out infinite}}
</style>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="#0B0D14"/>
  <rect width="{w}" height="{h}" fill="url(#glow)"/>
</g>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="27" fill="none" stroke="url(#ring)" stroke-width="2"/>
<text x="600" y="84" text-anchor="middle" font-family="{SANS}" font-size="40" font-weight="300" letter-spacing="-.8" fill="{INK}">Have an app idea? <tspan font-weight="700" fill="url(#btn)">Let's build it.</tspan></text>
<text x="600" y="118" text-anchor="middle" font-family="{SANS}" font-size="17" fill="{MUTED}">Freelance &amp; contract Flutter development · Remote worldwide</text>
<rect class="halo" x="490" y="140" width="220" height="52" rx="26" fill="url(#btn)" filter="url(#soft)"/>
<rect x="490" y="140" width="220" height="52" rx="26" fill="url(#btn)"/>
<text x="600" y="172" text-anchor="middle" font-family="{SANS}" font-size="17" font-weight="700" fill="#07080D">Start a project  →</text>
</svg>"""


# ---------------------------------------------------------------- section headers
def section(num, title, light=False):
    ink = "#1F2330" if light else INK
    tw = len(title) * 14
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="72" viewBox="0 0 900 72" role="img" aria-label="{escape(title)}">
<defs>
  <linearGradient id="ink" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="#A78BFF"/></linearGradient>
  <linearGradient id="line" x1="0" x2="1"><stop offset="0" stop-color="#A78BFF" stop-opacity=".7"/><stop offset="1" stop-color="#A78BFF" stop-opacity="0"/></linearGradient>
  <filter id="soft" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="3"/></filter>
</defs>
<style>
  @keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
  @keyframes travel{{0%{{transform:translateX(0);opacity:0}}10%,70%{{opacity:1}}100%{{transform:translateX({760 - tw:.0f}px);opacity:0}}}}
  .spark{{animation:travel 6s 1.6s cubic-bezier(.4,0,.2,1) infinite both}}
</style>
<text x="2" y="24" font-family="{MONO}" font-size="12" letter-spacing="3" fill="url(#ink)">{num} ——</text>
<text x="0" y="60" font-family="{SANS}" font-size="30" font-weight="300" letter-spacing="-.4" fill="{ink}">{escape(title)}</text>
<rect class="line" x="{tw + 24:.0f}" y="50" width="{876 - tw - 24:.0f}" height="1" fill="url(#line)"/>
<g class="spark"><circle cx="{tw + 24:.0f}" cy="50.5" r="6" fill="{CYAN}" opacity=".4" filter="url(#soft)"/><circle cx="{tw + 24:.0f}" cy="50.5" r="1.8" fill="#fff"/></g>
</svg>"""


# ---------------------------------------------------------------- project cards
def card(p):
    w, h = 520, 290
    lines = wrap(p["desc"], 54)[:3]
    desc = "".join(
        f'<text x="32" y="{150 + i * 24}" font-family="{SANS}" font-size="15.5" fill="{MUTED}">{escape(l)}</text>'
        for i, l in enumerate(lines)
    )
    x, pills = 32, []
    for t in p["tags"]:
        pw = len(t) * 7.6 + 26
        pills.append(
            f'<rect x="{x}" y="232" width="{pw:.0f}" height="28" rx="14" fill="{p["accent"]}" fill-opacity=".1" stroke="{p["accent"]}" stroke-opacity=".35"/>'
            f'<text x="{x + pw / 2:.0f}" y="250.5" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="{p["accent"]}">{escape(t)}</text>'
        )
        x += pw + 8
    a = p["accent"]
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(p['title'])}: {escape(p['desc'])}">
<defs>
  <linearGradient id="sheen" x1="0" x2="1" y1="0" y2="1">
    <stop offset="0" stop-color="{a}" stop-opacity=".9"/><stop offset=".35" stop-color="#ffffff" stop-opacity=".06"/>
    <stop offset=".7" stop-color="#ffffff" stop-opacity=".06"/><stop offset="1" stop-color="{a}" stop-opacity=".5"/>
  </linearGradient>
  <radialGradient id="glow" cx="0" cy="0" r="1"><stop offset="0" stop-color="{a}" stop-opacity=".22"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>
  <linearGradient id="tile" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{a}" stop-opacity=".45"/></linearGradient>
  <clipPath id="c"><rect width="{w}" height="{h}" rx="22"/></clipPath>
</defs>
<style>
  @keyframes breathe{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
  @keyframes sweep{{from{{transform:translateX(-200px)}}to{{transform:translateX({w + 200}px)}}}}
  .glow{{animation:breathe 5s ease-in-out infinite}}
  .sweep{{animation:sweep 7s ease-in-out infinite}}
</style>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="{CARD}"/>
  <rect class="glow" width="{w * 1.1}" height="{h * 1.1}" fill="url(#glow)"/>
  <rect class="sweep" x="0" y="-40" width="60" height="{h + 80}" fill="#ffffff" opacity=".035" transform="skewX(-20)"/>
</g>
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="21.25" fill="none" stroke="url(#sheen)" stroke-width="1.5"/>
<rect x="32" y="30" width="52" height="52" rx="15" fill="url(#tile)"/>
<text x="58" y="63" text-anchor="middle" font-family="{SANS}" font-size="18" font-weight="600" fill="{BG}">{p['mono']}</text>
<circle cx="{w - 140}" cy="49" r="5" fill="{p['lang_color']}"/>
<text x="{w - 128}" y="54" font-family="{MONO}" font-size="13" fill="{MUTED}">{p['lang']}</text>
<text x="{w - 40}" y="56" font-family="{SANS}" font-size="20" fill="{INK}" opacity=".7">↗</text>
<text x="32" y="122" font-family="{SANS}" font-size="25" font-weight="600" letter-spacing="-.4" fill="{INK}">{escape(p['title'])}</text>
{desc}
{''.join(pills)}
</svg>"""


# ---------------------------------------------------------------- footer
def footer():
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="150" viewBox="0 0 1200 150" role="img" aria-label="Thanks for visiting">
<defs>
  <linearGradient id="ink" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset=".55" stop-color="{VIOLET}"/><stop offset="1" stop-color="#FF5CA8"/></linearGradient>
</defs>
<style>
  @keyframes wave{{from{{transform:translateX(0)}}to{{transform:translateX(-600px)}}}}
  .w1{{animation:wave 12s linear infinite}} .w2{{animation:wave 18s linear infinite reverse}}
</style>
<g opacity=".55" class="w1"><path d="M0 110 Q150 70 300 110 T600 110 T900 110 T1200 110 T1500 110 T1800 110" fill="none" stroke="url(#ink)" stroke-width="2"/></g>
<g opacity=".3" class="w2"><path d="M-600 120 Q-450 90 -300 120 T0 120 T300 120 T600 120 T900 120 T1200 120 T1500 120 T1800 120" fill="none" stroke="url(#ink)" stroke-width="1.5"/></g>
<text x="600" y="58" text-anchor="middle" font-family="{SANS}" font-size="24" font-weight="800" fill="url(#ink)">Thanks for stopping by. Let's build something great.</text>
</svg>"""


if __name__ == "__main__":
    write("hero.svg", hero())
    for slug, num, title in SECTIONS:
        write(f"section-{slug}.svg", section(num, title))
        write(f"section-{slug}-light.svg", section(num, title, light=True))
    for p in PROJECTS:
        write(f"card-{p['slug']}.svg", card(p))
    write("metrics.svg", metrics())
    write("cta.svg", cta())
    write("footer.svg", footer())
