#!/usr/bin/env python3
"""Generate academy section pages, course pages, short links and tutorial posters.

  python3 scripts/build_academy_courses.py

Inputs (the course TEMPLATE lives here, change it once for every course):
  academy-data/courses.json            sections and courses (content)
  academy-data/templates/*.html|.svg   page templates (layout), see templates/README.md
Writes into academy/ (commit the result):
  <section>/index.html, <section>/<course>/index.html,
  <section>/<course>/{notes,slides,tutorial}/index.html, img/tutorials/<course>.svg,
  the short-link block in .htaccess and the course names in login/index.html.
"""
import json
import math
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "academy"
D = ROOT / "academy-data"
T = D / "templates"
DATA = json.loads((D / "courses.json").read_text(encoding="utf-8"))
LOGIN = "/login/?course="


def tpl(name):
    return (T / name).read_text(encoding="utf-8")


PARTIALS = {"_head": tpl("_head.html"), "_foot": tpl("_foot.html")}


def render(name, **values):
    """Fill {{> partial}} includes, then {{key}} placeholders. Values are inserted as given."""
    text = tpl(name)
    text = re.sub(r"\{\{> *(\w+) *\}\}", lambda m: PARTIALS[m.group(1)], text)
    def sub(m):
        key = m.group(1)
        if key not in values:
            raise KeyError(f"{name}: no value for {{{{{key}}}}}")
        return str(values[key])
    return re.sub(r"\{\{(\w+)\}\}", sub, text).rstrip("\n") + "\n"


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
    title_lines = "".join(f'<text x="80" y="{200 + i * step}" fill="#ffffff" font-size="{size}" font-weight="700">{escape(l)}</text>' for i, l in enumerate(lines))
    return render("poster.svg", title=escape(course["title"]), motif=motif(kind), title_lines=title_lines,
                  subtitle_y=200 + len(lines) * step - 4, first_module=escape(course["modules"][0][0]))


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
        courses = f'''        <div class="course-list">
          <p class="eyebrow">Courses</p>
          <ul>
{rows}
          </ul>
        </div>
'''
    else:
        courses = '''        <div class="soon-box">
          <h2>Courses are being prepared</h2>
          <p>Courses for this section are being written. Write to academy@coralpetal.ai if there is a topic you want covered first.</p>
        </div>
'''
    return render("section.html", page_title=escape(f'{sec["name"]} | Coral Petal AI Academy'),
                  page_description=escape(f'{sec["name"]} courses at Coral Petal AI Academy.'), page_path=f'/{sec["slug"]}/',
                  section_name=escape(sec["name"]), lede=existing_lede(sec["slug"], sec["name"]),
                  courses=courses, other_sections=others)


def course_page(sec, c):
    base = f'/{sec["slug"]}/{c["slug"]}/'
    modules = "\n".join(
        f'            <li><span class="mod-n">{i + 1:02d}</span><div><h3>{escape(m[0])}</h3>' + (f'<p>{escape(m[1])}</p>' if len(m) > 1 and m[1] else "") + "</div></li>"
        for i, m in enumerate(c["modules"]))
    prereq = "\n".join(f"                <li>{escape(p)}</li>" for p in c["prerequisites"])
    material = f'              <a class="ref-box ref-main" href="{LOGIN}{c["slug"]}"><span class="ref-title">Tutorial</span><span class="ref-sub">Sign in to watch the video course</span></a>\n'
    material += '              <span class="ref-box ref-disabled" aria-disabled="true" title="Coming soon"><span class="ref-title">Reference materials</span><span class="ref-sub">Coming soon</span></span>\n'
    if c.get("notes"):
        material += f'              <a class="ref-box" href="{base}notes" target="_blank" rel="noopener"><span class="ref-title">Notes</span><span class="ref-sub">Read the course notes</span></a>\n'
    if c.get("slides"):
        material += f'              <a class="ref-box" href="{base}slides" target="_blank" rel="noopener"><span class="ref-title">Slides</span><span class="ref-sub">View the slide deck</span></a>\n'
    return render("course.html", page_title=escape(f'{c["title"]} | Coral Petal AI Academy'),
                  page_description=escape(f'{c["title"]} at Coral Petal AI Academy. {c["summary"]}'), page_path=base,
                  section_slug=sec["slug"], section_name=escape(sec["name"]), slug=c["slug"], title=escape(c["title"]),
                  summary=escape(c["summary"]), level=escape(c["level"]), module_count=len(c["modules"]),
                  tools=escape(c["tools"]), tutorial_url=LOGIN + c["slug"], modules=modules, prerequisites=prereq,
                  audience=escape(c["audience"]), material=material)


def stub(title, label, url):
    return render("shortlink.html", title=escape(title), label=label, label_lower=label.lower(), url=escape(url))


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
