#!/usr/bin/env python3
"""Validate academy/courses.json (standard library only).

  python3 scripts/check_courses.py academy/courses.json

Fails on: bad JSON, missing fields, duplicate or malformed slugs, unknown level,
tags not listed in tagGroups, a course without exactly one Format tag.
"""
import json, re, sys

LEVELS = {"Beginner", "Intermediate", "Advanced"}

def main(path):
    data = json.load(open(path, encoding="utf-8"))
    groups = data["tagGroups"]
    known = {t for g in groups.values() for t in g}
    formats = set(groups.get("Format", []))
    errs, seen = [], set()
    for i, c in enumerate(data["courses"]):
        name = c.get("slug", f"#{i}")
        for f in ("slug", "title", "summary", "level", "tags"):
            if not c.get(f):
                errs.append(f"{name}: missing {f}")
        s = c.get("slug", "")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", s):
            errs.append(f"{name}: slug must be lowercase-with-hyphens")
        if s in seen:
            errs.append(f"{name}: duplicate slug")
        seen.add(s)
        if c.get("level") not in LEVELS:
            errs.append(f"{name}: level must be one of {sorted(LEVELS)}")
        for t in c.get("tags", []):
            if t not in known:
                errs.append(f"{name}: tag '{t}' is not in tagGroups")
        if len([t for t in c.get("tags", []) if t in formats]) != 1:
            errs.append(f"{name}: needs exactly one Format tag {sorted(formats)}")
    for e in errs:
        print("FAIL", e)
    print(f"checked {len(data['courses'])} course(s), {len(errs)} problem(s)")
    return 1 if errs else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "academy/courses.json"))
