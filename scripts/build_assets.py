#!/usr/bin/env python3
"""Generates the animated SVG assets used by README.md.

GitHub can't load web fonts in a README, so every SVG embeds a subset of the
fonts in scripts/fonts (Instrument Serif, Inter, JetBrains Mono; all SIL OFL).

Edit the content below, then run (needs `pip install fonttools`):
    python3 scripts/build_assets.py
"""
import base64
import io
import math
import random
import re
from html import unescape
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
OUT.mkdir(exist_ok=True)

SERIF = "'Instrument Serif', Georgia, 'Times New Roman', serif"
SANS = "Inter, 'Segoe UI', -apple-system, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, Menlo, Consolas, monospace"

FACES = {  # key: (css family, style, weight, file)
    "serif": ("Instrument Serif", "normal", 400, "InstrumentSerif-Regular"),
    "serif-italic": ("Instrument Serif", "italic", 400, "InstrumentSerif-Italic"),
    "sans": ("Inter", "normal", 400, "Inter-400"),
    "sans-500": ("Inter", "normal", 500, "Inter-500"),
    "sans-600": ("Inter", "normal", 600, "Inter-600"),
    "mono": ("JetBrains Mono", "normal", 400, "JetBrainsMono-400"),
}

BG = "#06070B"
CARD = "#0B0D14"
INK = "#F4F1EA"
MUTED = "#A3A9B8"
DIM = "#5E6577"
CYAN = "#54C5F8"
VIOLET = "#7C5CFF"
LILAC = "#A78BFF"
PINK = "#FF8AD0"
MINT = "#2EE6A6"

GRAD = f'<stop offset="0" stop-color="{CYAN}"/><stop offset=".55" stop-color="{LILAC}"/><stop offset="1" stop-color="{PINK}"/>'

# ------------------------------------------------------------------ content
INTRO = {
    "kicker": "FLUTTER DEVELOPER FOR HIRE",
    "title": ("I turn ideas into ", "apps people love."),
    "lines": [
        "Cross-platform iOS, Android & Windows apps, from the first sketch to the App Store & Google Play.",
        "Bilingual Arabic & English  ·  Based in Jeddah, Saudi Arabia  ·  Working remotely worldwide",
    ],
}

BUTTONS = [  # slug, label, primary
    ("hire", "Hire me  →", True),
    ("fiverr", "Fiverr  ↗", False),
    ("linkedin", "LinkedIn  ↗", False),
    ("portfolio", "Portfolio  ↗", False),
]

METRICS = [("4", "apps live on the stores"), ("17", "engineers led"), ("8", "languages shipped"), ("30+", "projects on GitHub")]

SERVICES = [
    ("flutter", "Flutter App Development", CYAN,
     "Cross-platform iOS & Android apps from one Dart codebase, with smooth 60fps UI, published to the App Store & Google Play."),
    ("rtl", "Arabic & English Apps", MINT,
     "Bilingual apps with true right-to-left layouts and localization in up to 8 languages, built for Saudi Arabia, the GCC & MENA."),
    ("desktop", "Windows Desktop & Kiosks", "#FFB547",
     "Offline-first Flutter desktop systems with RFID, barcode & thermal printer integration for retail, events and hospitals."),
    ("erp", "Custom ERP Systems", LILAC,
     "Multi-tenant ERPs, field sales & GPS attendance, inventory and ZATCA-compliant VAT invoicing, shaped around your team."),
    ("backend", "Firebase & Backend APIs", "#FF5C7A",
     "Firebase, Cloud Functions, Node.js & NestJS APIs, PostgreSQL / PostGIS, realtime sync, auth and push notifications."),
    ("ai", "AI-Powered Apps", PINK,
     "Gemini, Claude & Groq inside your product: smart matching, chat assistants, document automation and recommendations."),
]

PROJECTS = [
    {"slug": "allah-everywhere", "mono": "Ae", "title": "ALLAH Everywhere", "lang": "Dart", "lang_color": "#00B4AB", "accent": MINT,
     "desc": "Prayer times, Quran & Hifz, Hadith, Qibla and family challenges with rewards. Live on iOS & Android in 8 languages.",
     "tags": ["Flutter", "Firebase", "8 languages"]},
    {"slug": "field-sales", "mono": "Fs", "title": "Field Sales Management", "lang": "TypeScript", "lang_color": "#3178C6", "accent": CYAN,
     "desc": "GPS attendance with geofencing & fraud detection, live rep tracking, sales targets and catalogue sharing. English / Arabic RTL.",
     "tags": ["Flutter", "React", "NestJS", "PostGIS"]},
    {"slug": "arrowtech-erp", "mono": "At", "title": "ArrowTech Wristband ERP", "lang": "TypeScript", "lang_color": "#3178C6", "accent": LILAC,
     "desc": "Multi-tenant ERP for badge manufacturing: sales, design proofing, realtime print-floor dispatch, inventory and ZATCA accounting.",
     "tags": ["TypeScript", "Realtime", "Multi-tenant"]},
    {"slug": "voltstore", "mono": "Vs", "title": "VoltStore", "lang": "TypeScript", "lang_color": "#3178C6", "accent": "#FF5C7A",
     "desc": "A Redis-compatible in-memory store built from scratch: custom RESP parser, concurrent TCP server, TTL engine and live dashboard.",
     "tags": ["TypeScript", "TCP", "RESP"]},
    {"slug": "nexus-browser", "mono": "Nx", "title": "Nexus Browser", "lang": "JavaScript", "lang_color": "#F1E05A", "accent": "#FFB547",
     "desc": "A custom desktop browser with a frameless glassmorphic HUD, multi-tab webviews, a live tracker blocker and a new-tab dashboard.",
     "tags": ["Electron", "JavaScript", "Desktop"]},
    {"slug": "aura-match", "mono": "Am", "title": "Aura Match", "lang": "Dart", "lang_color": "#00B4AB", "accent": PINK,
     "desc": "The AI that finds your next job while you sleep. Matches profiles to openings and handles the busywork for you.",
     "tags": ["Flutter", "Node.js", "Groq AI"]},
]

SECTIONS = [  # slug, number, plain part, italic part
    ("services", "01", "What I build ", "for clients"),
    ("work", "02", "Featured ", "work"),
    ("about", "03", "A little ", "about me"),
    ("stack", "04", "The ", "toolbox"),
    ("activity", "05", "Recent ", "activity"),
]


# ------------------------------------------------------------------ fonts
_fonts = {}


def font(key):
    if key not in _fonts:
        _fonts[key] = TTFont(ROOT / "fonts" / f"{FACES[key][3]}.ttf")
    return _fonts[key]


def measure(text, key, size, spacing=0):
    f = font(key)
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    adv = sum(hmtx[cmap.get(ord(c), ".notdef")][0] for c in text)
    return adv / upm * size + spacing * len(text)


def wrap(text, key, size, width):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and measure(trial, key, size) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def embed_fonts(svg):
    """Inline only the faces this SVG uses, subset to the characters it draws."""
    chars = set(unescape("".join(re.findall(r">([^<]*)<", svg)))) | {" "}
    used = []
    if "Instrument Serif" in svg:
        used.append("serif")
        if 'font-style="italic"' in svg:
            used.append("serif-italic")
    if 'font-family="Inter' in svg:
        used.append("sans")
        used += [k for k, w in (("sans-500", "500"), ("sans-600", "600")) if f'font-weight="{w}"' in svg]
    if "JetBrains Mono" in svg:
        used.append("mono")
    rules = []
    for key in used:
        family, style, weight, file = FACES[key]
        f = TTFont(ROOT / "fonts" / f"{file}.ttf")
        opts = subset.Options()
        opts.flavor = "woff"
        opts.layout_features = ["kern", "liga"]
        s = subset.Subsetter(opts)
        s.populate(text="".join(chars))
        s.subset(f)
        buf = io.BytesIO()
        f.flavor = "woff"
        f.save(buf)
        data = base64.b64encode(buf.getvalue()).decode()
        rules.append(f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};"
                     f"src:url(data:font/woff;base64,{data}) format('woff')}}")
    return re.sub(r"(<svg[^>]*>)", lambda m: m.group(1) + "\n<style>" + "".join(rules) + "</style>", svg, count=1)


def write(name, svg):
    (OUT / name).write_text(embed_fonts(svg.strip()) + "\n", encoding="utf-8")
    print("wrote", OUT / name)


# ------------------------------------------------------------------ hero
def stars(n, seed=7, w=1200, h=460):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(20, w - 20), rnd.uniform(20, h - 20)
        r = rnd.choice([.5, .7, .9, 1.1, 1.4])
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" class="tw" '
                   f'style="animation-duration:{rnd.uniform(2.5, 6):.1f}s;animation-delay:-{rnd.uniform(0, 6):.1f}s"/>')
    return "\n  ".join(out)


def silk(n, seed_phase, amp, spread, center, xs, opacity):
    """A twisting ribbon of n hairlines whose shape morphs between three keyframes."""
    def d(t, k):
        ph = seed_phase + k * 2 * math.pi / 3
        ys = [center + amp * math.sin(ph + j * 1.15) + (t - .5) * spread * math.sin(ph * 1.3 + j * 1.6) for j in range(4)]
        return f"M{xs[0]} {ys[0]:.1f}C{xs[1]} {ys[1]:.1f} {xs[2]} {ys[2]:.1f} {xs[3]} {ys[3]:.1f}"

    out = []
    for i in range(n):
        t = i / (n - 1)
        frames = [d(t, k) for k in range(3)]
        o = opacity * (.25 + .75 * math.sin(math.pi * t))
        out.append(
            f'<path d="{frames[0]}" fill="none" stroke="url(#silk)" stroke-width="{.7 + .5 * math.sin(math.pi * t):.2f}" opacity="{o:.2f}">'
            f'<animate attributeName="d" dur="16s" repeatCount="indefinite" calcMode="spline" keyTimes="0;.33;.66;1" '
            f'keySplines=".45 0 .55 1;.45 0 .55 1;.45 0 .55 1" values="{";".join(frames + frames[:1])}"/></path>')
    return "\n  ".join(out)


def hero():
    w, h = 1200, 460
    words = ["apps your users love", "ERPs that scale", "Arabic & English RTL apps", "offline-first desktop systems"]
    cycle = len(words) * 3
    show = 3 / cycle * 100
    word_nodes = "\n".join(
        f'<text class="word w{i}" x="82" y="398" font-family="{MONO}" font-size="15" letter-spacing=".3" fill="url(#ink)">'
        f'<tspan fill="{DIM}">building </tspan>{escape(wd)}<tspan class="caret" fill="{CYAN}"> ▍</tspan></text>'
        for i, wd in enumerate(words))
    word_css = " ".join(f".w{i}{{animation:word {cycle}s {i * 3 - 1}s infinite both}}" for i in range(len(words)))
    badge_w = measure("OPEN TO WORK", "mono", 11, 2.6) + 52
    loc = "JEDDAH, SAUDI ARABIA  ·  REMOTE WORLDWIDE"
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Muhammad Abdullah Waseem, Flutter Developer for iOS, Android and Windows apps">
<defs>
  <linearGradient id="ink" x1="0" x2="1">{GRAD}</linearGradient>
  <linearGradient id="silk" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="0">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".45" stop-color="{LILAC}"/><stop offset=".8" stop-color="{PINK}"/><stop offset="1" stop-color="{CYAN}"/>
  </linearGradient>
  <linearGradient id="shimmer" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="300" y2="0" spreadMethod="reflect">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".35" stop-color="{LILAC}"/><stop offset=".5" stop-color="#ffffff"/><stop offset=".65" stop-color="{LILAC}"/><stop offset="1" stop-color="{PINK}"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="600 0" dur="7s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="edge" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".45"/><stop offset=".5" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="{VIOLET}" stop-opacity=".45"/></linearGradient>
  <linearGradient id="hair" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="reveal" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity=".1"/><stop offset=".45" stop-color="#fff" stop-opacity=".3"/><stop offset=".72" stop-color="#fff"/></linearGradient>
  <mask id="fadeLeft"><rect width="{w}" height="{h}" fill="url(#reveal)"/></mask>
  <filter id="blur" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="80"/></filter>
  <filter id="glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="soft" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="4"/></filter>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="28"/></clipPath>
</defs>
<style>
  @keyframes drift1{{0%,100%{{transform:translate(0,0) scale(1)}}50%{{transform:translate(140px,50px) scale(1.15)}}}}
  @keyframes drift2{{0%,100%{{transform:translate(0,0) scale(1.1)}}50%{{transform:translate(-160px,-40px) scale(.9)}}}}
  @keyframes twinkle{{0%,100%{{opacity:.08}}50%{{opacity:.85}}}}
  @keyframes pulse{{0%{{transform:scale(1);opacity:.7}}100%{{transform:scale(3.2);opacity:0}}}}
  @keyframes word{{0%{{opacity:0;transform:translateY(8px)}}{show * .15:.2f}%,{show * .85:.2f}%{{opacity:1;transform:none}}{show:.2f}%,100%{{opacity:0;transform:translateY(-8px)}}}}
  @keyframes blink{{50%{{opacity:0}}}}
  @keyframes travel{{0%{{transform:translateX(0);opacity:0}}10%,80%{{opacity:1}}100%{{transform:translateX(440px);opacity:0}}}}
  .b1{{animation:drift1 16s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
  .b2{{animation:drift2 21s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
  .tw{{animation:twinkle 4s ease-in-out infinite}}
  .ring{{transform-box:fill-box;transform-origin:center;animation:pulse 2.4s ease-out infinite}}
  .word{{opacity:0}} {word_css}
  .caret{{animation:blink 1.1s steps(1) infinite}}
  .spark{{animation:travel 5s cubic-bezier(.4,0,.2,1) infinite}}
</style>
<g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="{BG}"/>
  <ellipse class="b1" cx="240" cy="80" rx="260" ry="170" fill="{CYAN}" opacity=".13" filter="url(#blur)"/>
  <ellipse class="b2" cx="900" cy="250" rx="320" ry="190" fill="{VIOLET}" opacity=".26" filter="url(#blur)"/>
  <ellipse class="b1" cx="620" cy="490" rx="240" ry="120" fill="#FF5CA8" opacity=".12" filter="url(#blur)"/>
  {stars(60)}
  <g mask="url(#fadeLeft)" filter="url(#glow)">
  {silk(34, 0.0, 70, 150, 240, [-80, 420, 820, 1280], .9)}
  {silk(22, 2.1, 90, 90, 260, [-80, 420, 820, 1280], .45)}
  </g>
</g>
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="27.25" fill="none" stroke="url(#edge)" stroke-width="1.2"/>

<rect x="82" y="68" width="{badge_w:.0f}" height="30" rx="15" fill="{BG}" fill-opacity=".6" stroke="#fff" stroke-opacity=".14"/>
<circle class="ring" cx="102" cy="83" r="3.5" fill="{MINT}"/>
<circle cx="102" cy="83" r="3.5" fill="{MINT}"/>
<text x="116" y="87" font-family="{MONO}" font-size="11" letter-spacing="2.6" fill="{INK}" opacity=".85">OPEN TO WORK</text>

<text x="78" y="196" font-family="{SERIF}" font-size="88" letter-spacing="-1" fill="{INK}">Muhammad Abdullah</text>
<text x="78" y="282" font-family="{SERIF}" font-size="88" font-style="italic" letter-spacing="-.5" fill="url(#shimmer)">Waseem</text>
<rect x="82" y="314" width="440" height="1" fill="url(#hair)"/>
<circle class="spark" cx="82" cy="314.5" r="2" fill="#fff"/>
<circle class="spark" cx="82" cy="314.5" r="7" fill="{CYAN}" opacity=".35" filter="url(#soft)"/>
<text x="82" y="354" font-family="{SANS}" font-size="18" fill="{MUTED}">Flutter Developer  ·  iOS, Android &amp; Windows apps</text>
{word_nodes}
<text x="{w - 70}" y="{h - 44}" text-anchor="end" font-family="{MONO}" font-size="10.5" letter-spacing="2.6" fill="{INK}" opacity=".4">{escape(loc)}</text>
</svg>"""


# ------------------------------------------------------------------ intro (transparent, light + dark)
def intro(light=False):
    w, h = 1200, 250
    ink, muted = ("#14161D", "#4A5162") if light else (INK, MUTED)
    plain, ital = INTRO["title"]
    tw = measure(plain, "serif", 52) + measure(ital, "serif-italic", 52)
    lines = "".join(
        f'<text x="600" y="{178 + i * 30}" text-anchor="middle" font-family="{SANS}" font-size="17" fill="{muted}">{escape(l)}</text>'
        for i, l in enumerate(INTRO["lines"]))
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Flutter developer for hire. {escape(plain + ital)} {escape(' '.join(INTRO['lines']))}">
<defs>
  <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="{600 - tw / 2:.0f}" x2="{600 + tw / 2:.0f}" y1="0" y2="0">{GRAD}</linearGradient>
  <linearGradient id="hair" x1="0" x2="1"><stop offset="0" stop-color="{LILAC}" stop-opacity="0"/><stop offset=".5" stop-color="{LILAC}"/><stop offset="1" stop-color="{LILAC}" stop-opacity="0"/></linearGradient>
</defs>
<rect x="520" y="22" width="160" height="1" fill="url(#hair)"/>
<text x="600" y="52" text-anchor="middle" font-family="{MONO}" font-size="12" letter-spacing="4" fill="url(#ink)">{INTRO['kicker']}</text>
<text x="600" y="122" text-anchor="middle" font-family="{SERIF}" font-size="52" letter-spacing="-.5" fill="{ink}">{escape(plain)}<tspan font-style="italic" fill="url(#ink)">{escape(ital)}</tspan></text>
{lines}
</svg>"""


# ------------------------------------------------------------------ link buttons
def button(label, primary):
    h = 56
    w = measure(label, "sans-500", 16) + 64
    if primary:
        body = (f'<rect x="1" y="1" width="{w - 2:.0f}" height="{h - 2}" rx="{(h - 2) / 2}" fill="url(#ink)"/>'
                f'<text x="{w / 2:.0f}" y="34" text-anchor="middle" font-family="{SANS}" font-size="16" font-weight="500" fill="{BG}">{escape(label)}</text>')
    else:
        body = (f'<rect x="1" y="1" width="{w - 2:.0f}" height="{h - 2}" rx="{(h - 2) / 2}" fill="{CARD}" stroke="url(#ink)" stroke-opacity=".6"/>'
                f'<text x="{w / 2:.0f}" y="34" text-anchor="middle" font-family="{SANS}" font-size="16" font-weight="500" fill="{INK}">{escape(label)}</text>')
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h}" viewBox="0 0 {w:.0f} {h}" role="img" aria-label="{escape(label.strip(' →↗'))}">
<defs><linearGradient id="ink" x1="0" x2="1">{GRAD}</linearGradient></defs>
{body}
</svg>"""


# ------------------------------------------------------------------ metrics strip
def metrics():
    w, h, col = 1200, 180, 1200 / len(METRICS)
    cells = []
    for i, (num, label) in enumerate(METRICS):
        cx = col * i + col / 2
        cells.append(
            f'<text x="{cx:.0f}" y="100" text-anchor="middle" font-family="{SERIF}" font-size="76" fill="url(#ink)">{num}</text>'
            f'<text x="{cx:.0f}" y="136" text-anchor="middle" font-family="{MONO}" font-size="11" letter-spacing="2.6" fill="{MUTED}">{escape(label.upper())}</text>')
        if i:
            cells.append(f'<rect x="{col * i:.0f}" y="44" width="1" height="100" fill="url(#vline)"/>')
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(', '.join(f'{n} {l}' for n, l in METRICS))}">
<defs>
  <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="80" x2="1120" y1="0" y2="0">{GRAD}</linearGradient>
  <linearGradient id="vline" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".4"/><stop offset=".5" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="{PINK}" stop-opacity=".4"/></linearGradient>
  <clipPath id="c"><rect width="{w}" height="{h}" rx="24"/></clipPath>
</defs>
<style>
  @keyframes sweep{{from{{transform:translateX(-300px)}}to{{transform:translateX({w + 300}px)}}}}
  .sweep{{animation:sweep 9s ease-in-out infinite}}
</style>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="{CARD}"/>
  <rect class="sweep" x="0" y="-60" width="120" height="{h + 120}" fill="#fff" opacity=".035" transform="skewX(-20)"/>
</g>
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="23.25" fill="none" stroke="url(#edge)" stroke-width="1.2"/>
{''.join(cells)}
</svg>"""


# ------------------------------------------------------------------ section headers
def section(num, plain, ital, light=False):
    ink = "#14161D" if light else INK
    w, h = 900, 96
    tw = measure(plain, "serif", 48) + measure(ital, "serif-italic", 48)
    lx = tw + 28
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(plain + ital)}">
<defs>
  <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="0" x2="{max(tw, 200):.0f}" y1="0" y2="0">{GRAD}</linearGradient>
  <linearGradient id="line" x1="0" x2="1"><stop offset="0" stop-color="{LILAC}" stop-opacity=".7"/><stop offset="1" stop-color="{LILAC}" stop-opacity="0"/></linearGradient>
  <filter id="soft" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="3"/></filter>
</defs>
<style>
  @keyframes travel{{0%{{transform:translateX(0);opacity:0}}10%,70%{{opacity:1}}100%{{transform:translateX({w - lx - 60:.0f}px);opacity:0}}}}
  .spark{{animation:travel 6s cubic-bezier(.4,0,.2,1) infinite both}}
</style>
<text x="2" y="24" font-family="{MONO}" font-size="12" letter-spacing="3" fill="url(#ink)">{num} / {len(SECTIONS):02d}</text>
<text x="0" y="78" font-family="{SERIF}" font-size="48" letter-spacing="-.4" fill="{ink}">{escape(plain)}<tspan font-style="italic" fill="url(#ink)">{escape(ital)}</tspan></text>
<rect x="{lx:.0f}" y="66" width="{w - lx:.0f}" height="1" fill="url(#line)"/>
<g class="spark"><circle cx="{lx:.0f}" cy="66.5" r="6" fill="{CYAN}" opacity=".4" filter="url(#soft)"/><circle cx="{lx:.0f}" cy="66.5" r="1.8" fill="#fff"/></g>
</svg>"""


# ------------------------------------------------------------------ cards (services + projects)
def card_shell(w, h, accent, label, inner, sweep=True):
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">
<defs>
  <linearGradient id="sheen" x1="0" x2="1" y1="0" y2="1">
    <stop offset="0" stop-color="{accent}" stop-opacity=".85"/><stop offset=".35" stop-color="#fff" stop-opacity=".06"/>
    <stop offset=".7" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="{accent}" stop-opacity=".45"/>
  </linearGradient>
  <radialGradient id="glow" cx="0" cy="0" r="1"><stop offset="0" stop-color="{accent}" stop-opacity=".2"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
  <linearGradient id="tile" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="{accent}" stop-opacity=".45"/></linearGradient>
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
  <rect class="glow" width="{w * 1.1:.0f}" height="{h * 1.1:.0f}" fill="url(#glow)"/>
  {f'<rect class="sweep" x="0" y="-40" width="60" height="{h + 80}" fill="#fff" opacity=".035" transform="skewX(-20)"/>' if sweep else ''}
</g>
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="21.25" fill="none" stroke="url(#sheen)" stroke-width="1.3"/>
{inner}
</svg>"""


def desc_lines(text, y0, step=23, size=14.5, width=456, limit=3):
    return "".join(
        f'<text x="32" y="{y0 + i * step}" font-family="{SANS}" font-size="{size}" fill="{MUTED}">{escape(l)}</text>'
        for i, l in enumerate(wrap(text, "sans", size, width)[:limit]))


def service(i, title, accent, desc):
    w, h = 520, 230
    inner = (
        f'<text x="32" y="48" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{accent}">{i:02d}</text>'
        f'<rect x="62" y="43" width="28" height="1" fill="{accent}" opacity=".5"/>'
        f'<circle cx="{w - 44}" cy="44" r="12" fill="none" stroke="{accent}" stroke-opacity=".5"/>'
        f'<circle cx="{w - 44}" cy="44" r="3.5" fill="{accent}"/>'
        f'<text x="30" y="104" font-family="{SERIF}" font-size="36" letter-spacing="-.3" fill="{INK}">{escape(title)}</text>'
        + desc_lines(desc, 142))
    return card_shell(w, h, accent, f"{title}: {desc}", inner, sweep=False)


def project(p):
    w, h, a = 520, 300, p["accent"]
    x, pills = 32, []
    for t in p["tags"]:
        pw = measure(t, "mono", 12) + 26
        pills.append(
            f'<rect x="{x:.0f}" y="240" width="{pw:.0f}" height="28" rx="14" fill="{a}" fill-opacity=".08" stroke="{a}" stroke-opacity=".35"/>'
            f'<text x="{x + pw / 2:.0f}" y="258.5" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{a}">{escape(t)}</text>')
        x += pw + 8
    lang_w = measure(p["lang"], "mono", 12)
    inner = (
        f'<rect x="32" y="30" width="54" height="54" rx="16" fill="url(#tile)"/>'
        f'<text x="59" y="67" text-anchor="middle" font-family="{SERIF}" font-size="28" font-style="italic" fill="{BG}">{p["mono"]}</text>'
        f'<circle cx="{w - 74 - lang_w:.0f}" cy="53" r="4.5" fill="{p["lang_color"]}"/>'
        f'<text x="{w - 64 - lang_w:.0f}" y="57" font-family="{MONO}" font-size="12" fill="{MUTED}">{p["lang"]}</text>'
        f'<text x="{w - 36}" y="59" text-anchor="end" font-family="{SANS}" font-size="18" fill="{INK}" opacity=".7">↗</text>'
        f'<text x="30" y="134" font-family="{SERIF}" font-size="36" letter-spacing="-.3" fill="{INK}">{escape(p["title"])}</text>'
        + desc_lines(p["desc"], 168) + "".join(pills))
    return card_shell(w, h, a, f"{p['title']}: {p['desc']}", inner)


# ------------------------------------------------------------------ call to action
def cta():
    w, h = 1200, 260
    plain, ital = "Have an app idea? ", "Let's build it."
    tw = measure(plain, "serif", 60) + measure(ital, "serif-italic", 60)
    bl = "Start a project  →"
    bw = measure(bl, "sans-500", 17) + 72
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Have an app idea? Let's build it. Start a project.">
<defs>
  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".3" stop-color="#fff" stop-opacity=".05"/><stop offset=".6" stop-color="{LILAC}"/><stop offset=".85" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="{PINK}"/>
    <animateTransform attributeName="gradientTransform" type="rotate" values="0 .5 .5;360 .5 .5" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="{600 - tw / 2:.0f}" x2="{600 + tw / 2:.0f}" y1="0" y2="0">{GRAD}</linearGradient>
  <linearGradient id="btn" x1="0" x2="1">{GRAD}</linearGradient>
  <radialGradient id="glow" cx=".5" cy="1" r=".8"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".35"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
  <filter id="soft" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="14"/></filter>
  <clipPath id="c"><rect width="{w}" height="{h}" rx="28"/></clipPath>
</defs>
<style>
  @keyframes breathe{{0%,100%{{opacity:.35}}50%{{opacity:.8}}}}
  @keyframes twinkle{{0%,100%{{opacity:.08}}50%{{opacity:.7}}}}
  .halo{{animation:breathe 4s ease-in-out infinite}}
  .tw{{animation:twinkle 4s ease-in-out infinite}}
</style>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="{CARD}"/>
  <rect width="{w}" height="{h}" fill="url(#glow)"/>
  {stars(28, seed=3, w=w, h=h)}
</g>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="27" fill="none" stroke="url(#ring)" stroke-width="2"/>
<text x="600" y="98" text-anchor="middle" font-family="{SERIF}" font-size="60" letter-spacing="-.6" fill="{INK}">{escape(plain)}<tspan font-style="italic" fill="url(#ink)">{escape(ital)}</tspan></text>
<text x="600" y="136" text-anchor="middle" font-family="{SANS}" font-size="16" fill="{MUTED}">Freelance &amp; contract Flutter development  ·  Remote worldwide</text>
<rect class="halo" x="{600 - bw / 2:.0f}" y="164" width="{bw:.0f}" height="56" rx="28" fill="url(#btn)" filter="url(#soft)"/>
<rect x="{600 - bw / 2:.0f}" y="164" width="{bw:.0f}" height="56" rx="28" fill="url(#btn)"/>
<text x="600" y="198" text-anchor="middle" font-family="{SANS}" font-size="17" font-weight="500" fill="{BG}">{escape(bl)}</text>
</svg>"""


# ------------------------------------------------------------------ footer
def footer():
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="160" viewBox="0 0 1200 160" role="img" aria-label="Thanks for stopping by">
<defs>
  <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="380" x2="820" y1="0" y2="0">{GRAD}</linearGradient>
  <linearGradient id="wave" x1="0" x2="1">{GRAD}</linearGradient>
</defs>
<style>
  @keyframes wave{{from{{transform:translateX(0)}}to{{transform:translateX(-600px)}}}}
  .w1{{animation:wave 12s linear infinite}} .w2{{animation:wave 18s linear infinite reverse}}
</style>
<g opacity=".5" class="w1"><path d="M0 122 Q150 92 300 122 T600 122 T900 122 T1200 122 T1500 122 T1800 122" fill="none" stroke="url(#wave)" stroke-width="1.5"/></g>
<g opacity=".28" class="w2"><path d="M-600 132 Q-450 108 -300 132 T0 132 T300 132 T600 132 T900 132 T1200 132 T1500 132 T1800 132" fill="none" stroke="url(#wave)" stroke-width="1.2"/></g>
<text x="600" y="66" text-anchor="middle" font-family="{SERIF}" font-size="40" font-style="italic" fill="url(#ink)">Thanks for stopping by.</text>
</svg>"""


if __name__ == "__main__":
    for old in OUT.glob("*.svg"):
        old.unlink()
    write("hero.svg", hero())
    write("intro.svg", intro())
    write("intro-light.svg", intro(light=True))
    for slug, label, primary in BUTTONS:
        write(f"btn-{slug}.svg", button(label, primary))
    write("metrics.svg", metrics())
    for slug, num, plain, ital in SECTIONS:
        write(f"section-{slug}.svg", section(num, plain, ital))
        write(f"section-{slug}-light.svg", section(num, plain, ital, light=True))
    for i, (slug, title, accent, desc) in enumerate(SERVICES, 1):
        write(f"service-{slug}.svg", service(i, title, accent, desc))
    for p in PROJECTS:
        write(f"card-{p['slug']}.svg", project(p))
    write("cta.svg", cta())
    write("footer.svg", footer())
