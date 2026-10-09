#!/usr/bin/env python3
"""Pre-deploy checks for the static site. Standard library only.

  python3 scripts/check_site.py site

Fails (exit 1) on: unparseable HTML, unbalanced tags, missing <title> or
meta description, images without alt, internal links/assets that do not exist,
and in-page anchors that point at a missing id.
"""
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr", "path", "circle", "use", "stop"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors = [], []
        self.ids, self.refs, self.anchors = set(), [], []
        self.title = self.desc = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in VOID:
            self.stack.append(tag)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "title":
            self.title = True
        if tag == "meta" and a.get("name") == "description" and a.get("content"):
            self.desc = True
        if tag == "img" and "alt" not in a:
            self.errors.append(f"<img src={a.get('src')}> has no alt")
        for key in ("href", "src"):
            v = a.get(key)
            if v:
                (self.anchors if v.startswith("#") else self.refs).append(v)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unexpected </{tag}> (open: {self.stack[-3:]})")
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()


def main(root):
    root = Path(root)
    failures = 0
    pages = sorted(root.rglob("*.html"))
    for page in pages:
        p = Page()
        p.feed(page.read_text(encoding="utf-8"))
        errs = list(p.errors)
        if p.stack:
            errs.append(f"unclosed tags: {p.stack}")
        if not p.title:
            errs.append("missing <title>")
        if not p.desc and page.name != "404.html":
            errs.append("missing meta description")
        for a in p.anchors:
            if a != "#" and a[1:] not in p.ids:
                errs.append(f"anchor {a} has no matching id")
        for ref in p.refs:
            u = urlparse(ref)
            if u.scheme or ref.startswith("//"):
                continue
            target = (root / u.path.lstrip("/")) if u.path.startswith("/") else (page.parent / u.path)
            if u.path and not target.exists():
                errs.append(f"broken link: {ref}")
        for e in errs:
            print(f"FAIL {page.relative_to(root)}: {e}")
        failures += len(errs)
    print(f"checked {len(pages)} page(s), {failures} problem(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "site"))
