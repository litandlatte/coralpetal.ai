#!/usr/bin/env python3
"""Generate academy section pages, course pages, short links and tutorial posters.

  python3 scripts/build_academy_courses.py

Source of truth: academy-data/courses.json. Writes into academy/ (commit the result):
  academy/<section>/index.html                     section page with course boxes
  academy/<section>/<course>/index.html            course page (tutorial focus)
  academy/<section>/<course>/{notes,slides,tutorial}/index.html   fallback redirects
  academy/img/tutorials/<course>.svg               tutorial poster
  academy/.htaccess                                block between the BEGIN/END markers
  academy/login/index.html                         the COURSES name map
Header, footer and each section's intro line are kept from the existing pages.
"""
import json
import math
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "academy"
DATA = json.loads((ROOT / "academy-data" / "courses.json").read_text(encoding="utf-8"))
LOGIN = "/login/?course="

TEMPLATE = (A / "login" / "index.html").read_text(encoding="utf-8")
HEAD = TEMPLATE[: TEMPLATE.index('  <main id="main">')]
FOOT = TEMPLATE[TEMPLATE.index("  <footer"):]
_LOGIN_JS = "  <script>\n    (function"
FOOT = FOOT[: FOOT.index(_LOGIN_JS)] + "</body>\n</html>\n" if _LOGIN_JS in FOOT else FOOT


def head(title, desc, path):
    h = re.sub(r"<title>[^<]*</title>", f"<title>{escape(title)}</title>", HEAD)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{escape(desc)}">', h)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="https://academy.coralpetal.ai{path}">', h)
    return h


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")


def existing_lede(section_slug, fallback):
    p = A / section_slug / "index.html"
    if p.exists():
        m = re.search(r'<p class="lede">(.*?)</p>', p.read_text(encoding="utf-8"), re.S)
        if m:
            return m.group(1)
    return escape(fallback)


# ---------- posters ----------
def motif(kind):
    if kind == "bell":
        pts = " L".join(f"{560 + i * 4} {558 - 336 * math.exp(-(((560 + i * 4) - 880) / 80.0) ** 2 / 2):.1f}" for i in range(161))
        return (f'<path d="M{pts} L1200 560 L560 560 Z" fill="url(#fill)"/>'
                f'<path d="M{pts}" fill="none" stroke="#f2603f" stroke-width="4"/>'
                '<line x1="880" y1="220" x2="880" y2="560" stroke="#ffd2a6" stroke-width="2" stroke-dasharray="6 6"/>')
    if kind == "scatter":
        dots = [(600, 520), (640, 490), (690, 505), (730, 450), (770, 470), (810, 410), (850, 430), (900, 370), (940, 390),
                (980, 330), (1020, 350), (1060, 290), (1100, 300), (1150, 250), (700, 540), (880, 460), (1000, 400), (1120, 330)]
        s = "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="#94a3b8" fill-opacity=".8"/>' for x, y in dots)
        return s + '<line x1="580" y1="545" x2="1180" y2="245" stroke="#f2603f" stroke-width="5" stroke-linecap="round"/>'
    if kind == "tokens":
        rows, out = [[160, 110, 190, 90], [120, 210, 140], [180, 100, 160, 120], [140, 230]], ""
        for r, widths in enumerate(rows):
            x = 600
            for i, w in enumerate(widths):
                hl = (r + i) % 3 == 0
                out += f'<rect x="{x}" y="{250 + r * 80}" width="{w}" height="48" rx="10" fill="{"#f2603f" if hl else "#334155"}" fill-opacity="{".9" if hl else "1"}"/>'
                x += w + 16
        return out
    if kind == "graph":
        nodes = {"a": (880, 260), "b": (700, 400), "c": (1060, 400), "d": (780, 540), "e": (980, 540), "f": (880, 400)}
        edges = [("a", "b"), ("a", "c"), ("a", "f"), ("b", "d"), ("c", "e"), ("f", "d"), ("f", "e"), ("b", "f"), ("c", "f")]
        s = "".join(f'<line x1="{nodes[u][0]}" y1="{nodes[u][1]}" x2="{nodes[v][0]}" y2="{nodes[v][1]}" stroke="#475569" stroke-width="3"/>' for u, v in edges)
        for k, (x, y) in nodes.items():
            s += f'<circle cx="{x}" cy="{y}" r="{30 if k == "a" else 22}" fill="{"#f2603f" if k == "a" else "#1e293b"}" stroke="#f2603f" stroke-width="3"/>'
        return s
    if kind == "badge":
        return ('<path d="M880 210 L1010 260 L1010 380 C1010 470 950 530 880 560 C810 530 750 470 750 380 L750 260 Z" fill="#1e293b" stroke="#f2603f" stroke-width="5"/>'
                '<path d="M820 385 L865 430 L950 335" fill="none" stroke="#ffd2a6" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>')
    if kind == "hex":
        out, r = "", 46
        for row in range(4):
            for col in range(6):
                cx = 640 + col * r * 1.75 + (row % 2) * r * 0.875
                cy = 250 + row * r * 1.5
                pts = " ".join(f"{cx + r * math.cos(math.radians(60 * k + 30)):.1f},{cy + r * math.sin(math.radians(60 * k + 30)):.1f}" for k in range(6))
                hl = (row, col) in {(1, 2), (2, 2), (1, 3), (2, 3)}
                out += f'<polygon points="{pts}" fill="{"#f2603f" if hl else "#1e293b"}" fill-opacity="{".85" if hl else "1"}" stroke="#475569" stroke-width="2"/>'
        return out
    return ""


def wrap_title(title, width=17):
    words, lines, cur = title.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    return lines[:4]


def poster(course, kind):
    lines = wrap_title(course["title"])
    size, step = (56, 66) if len(lines) <= 3 else (46, 56)
    t = "".join(f'<text x="80" y="{200 + i * step}" fill="#ffffff" font-size="{size}" font-weight="700">{escape(l)}</text>' for i, l in enumerate(lines))
    sub_y = 200 + len(lines) * step - 4
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" role="img" aria-label="{escape(course["title"])} tutorial">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f172a"/><stop offset="1" stop-color="#1e293b"/></linearGradient>
    <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f2603f" stop-opacity=".55"/><stop offset="1" stop-color="#f2603f" stop-opacity="0"/></linearGradient>
  </defs>
  <rect width="1280" height="720" fill="url(#bg)"/>
  {motif(kind)}
  <g font-family="Inter, Arial, sans-serif">
    <text x="80" y="110" fill="#f2603f" font-size="22" font-weight="700" letter-spacing="4">CORAL PETAL AI ACADEMY</text>
    {t}
    <text x="80" y="{sub_y}" fill="#cbd5e1" font-size="26">Module 1 · {escape(course["modules"][0][0])}</text>
  </g>
  <rect x="0" y="704" width="1280" height="16" fill="#1e293b"/>
  <rect x="0" y="704" width="140" height="16" fill="#f2603f"/>
</svg>
'''


# ---------- pages ----------
def section_page(sec, all_secs):
    others = "\n".join(f'          <li><a href="/{s["slug"]}/">{escape(s["name"])}</a></li>' for s in all_secs if s["slug"] != sec["slug"])
    if sec["courses"]:
        rows = "\n".join(f'''            <li>
              <a class="course-row" href="/{sec["slug"]}/{c["slug"]}/">
                <span class="course-row-main">
                  <span class="course-row-title">{escape(c["title"])}</span>
                  <span class="course-row-meta">{escape(c["level"])} · {len(c["modules"])} modules</span>
                </span>
                <span class="course-row-go" aria-hidden="true">→</span>
              </a>
            </li>''' for c in sec["courses"])
        body = f'''        <div class="course-list">
          <p class="eyebrow">Courses</p>
          <ul>
{rows}
          </ul>
        </div>
'''
    else:
        body = '''        <div class="soon-box">
          <h2>Courses are being prepared</h2>
          <p>Courses for this section are being written. Write to academy@coralpetal.ai if there is a topic you want covered first.</p>
        </div>
'''
    lede = existing_lede(sec["slug"], sec["name"])
    return head(f'{sec["name"]} | Coral Petal AI Academy', f'{sec["name"]} courses at Coral Petal AI Academy.', f'/{sec["slug"]}/') + f'''  <main id="main">
    <section class="section-page">
      <div class="wrap">
        <p class="crumbs"><a href="/">Academy</a> / {escape(sec["name"])}</p>
        <h1>{escape(sec["name"])}</h1>
        <p class="lede">{lede}</p>

{body}
        <div class="related">
          <p class="eyebrow">Other sections</p>
          <ul>
{others}
          </ul>
        </div>
      </div>
    </section>
  </main>

''' + FOOT


def course_page(sec, c):
    base = f'/{sec["slug"]}/{c["slug"]}/'
    mods = "\n".join(
        f'            <li><span class="mod-n">{i + 1:02d}</span><div><h3>{escape(m[0])}</h3>' + (f'<p>{escape(m[1])}</p>' if len(m) > 1 and m[1] else "") + "</div></li>"
        for i, m in enumerate(c["modules"]))
    prereq = "\n".join(f"                <li>{escape(p)}</li>" for p in c["prerequisites"])
    refs = f'              <a class="ref-box ref-main" href="{LOGIN}{c["slug"]}"><span class="ref-title">Tutorial</span><span class="ref-sub">Sign in to watch the video course</span></a>\n'
    if c.get("notes"):
        refs += f'              <a class="ref-box" href="{base}notes"><span class="ref-title">Notes</span><span class="ref-sub">Read the course notes</span></a>\n'
    if c.get("slides"):
        refs += f'              <a class="ref-box" href="{base}slides"><span class="ref-title">Slides</span><span class="ref-sub">View the slide deck</span></a>\n'
    return head(f'{c["title"]} | Coral Petal AI Academy', f'{c["title"]} at Coral Petal AI Academy. {c["summary"]}', base) + f'''  <main id="main">
    <section class="section-page course-page">
      <div class="wrap">
        <p class="crumbs"><a href="/">Academy</a> / <a href="/{sec["slug"]}/">{escape(sec["name"])}</a> / {escape(c["title"])}</p>
        <h1>{escape(c["title"])}</h1>
        <p class="lede">{escape(c["summary"])}</p>
        <ul class="course-facts">
          <li><span>Level</span>{escape(c["level"])}</li>
          <li><span>Modules</span>{len(c["modules"])}</li>
          <li><span>Tools</span>{escape(c["tools"])}</li>
        </ul>

        <div class="course-layout">
          <div class="course-main">
            <section class="tutorial-box" id="tutorial" aria-labelledby="tutorial-h">
              <a class="tutorial-frame tutorial-poster" href="{LOGIN}{c["slug"]}" aria-label="Play the {escape(c["title"])} tutorial (sign-in required)">
                <img src="/img/tutorials/{c["slug"]}.svg" alt="" width="1280" height="720">
                <span class="play" aria-hidden="true"></span>
                <span class="lock-note">Sign in to watch</span>
              </a>
              <div class="tutorial-caption">
                <h2 id="tutorial-h">Tutorial</h2>
                <p>Work through the course module by module. Use the notes and slides alongside the video.</p>
              </div>
            </section>

            <section class="course-block">
              <h2>What you'll learn</h2>
              <ol class="modules">
{mods}
              </ol>
            </section>
          </div>

          <aside class="course-side">
            <div class="side-box">
              <h2>Prerequisites</h2>
              <ul>
{prereq}
              </ul>
            </div>
            <div class="side-box">
              <h2>Who it's for</h2>
              <p>{escape(c["audience"])}</p>
            </div>
            <div class="side-box side-refs">
              <h2>Course material</h2>
{refs}            </div>
            <div class="side-box side-cta">
              <p>Questions about this course or training for your team?</p>
              <a class="btn btn-small" href="mailto:academy@coralpetal.ai">Talk to us</a>
            </div>
          </aside>
        </div>
      </div>
    </section>
  </main>

''' + FOOT


def stub(title, label, url):
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(title)} {label} | Coral Petal AI Academy</title>
  <meta name="description" content="{escape(title)} {label.lower()}.">
  <meta name="robots" content="noindex">
  <meta http-equiv="refresh" content="0; url={escape(url)}">
</head>
<body>
  <p>Opening the {label.lower()}: <a href="{escape(url)}">continue</a>.</p>
</body>
</html>
'''


def main():
    secs = DATA["sections"]
    redirects, names = [], {}
    for sec in secs:
        write(A / sec["slug"] / "index.html", section_page(sec, secs))
        for c in sec["courses"]:
            d = A / sec["slug"] / c["slug"]
            write(d / "index.html", course_page(sec, c))
            write(A / "img" / "tutorials" / f'{c["slug"]}.svg', poster(c, sec["motif"]))
            targets = {"tutorial": LOGIN + c["slug"]}
            if c.get("notes"):
                targets["notes"] = c["notes"]
            if c.get("slides"):
                targets["slides"] = c["slides"]
            for kind, url in targets.items():
                write(d / kind / "index.html", stub(c["title"], kind.capitalize(), url))
                redirects.append(f'  RedirectMatch 302 ^/{sec["slug"]}/{c["slug"]}/{kind}/?$ {url}')
            names[c["slug"]] = c["title"]

    block = ("# BEGIN course short links (generated by scripts/build_academy_courses.py, do not edit by hand)\n"
             "<IfModule mod_alias.c>\n" + "\n".join(redirects) + "\n</IfModule>\n# END course short links\n")
    h = (A / ".htaccess").read_text(encoding="utf-8")
    if "# BEGIN course short links" in h:
        h = re.sub(r"# BEGIN course short links.*?# END course short links\n", block, h, flags=re.S)
    else:
        h = re.sub(r"# Course short links:.*?</IfModule>\n", block, h, flags=re.S)
    write(A / ".htaccess", h)

    login = (A / "login" / "index.html").read_text(encoding="utf-8")
    login = re.sub(r"var COURSES = \{.*?\};", "var COURSES = " + json.dumps(names, ensure_ascii=False) + ";", login, flags=re.S)
    write(A / "login" / "index.html", login)
    print(f"built {sum(len(s['courses']) for s in secs)} course(s) in {len(secs)} section(s), {len(redirects)} short link(s)")


if __name__ == "__main__":
    main()
