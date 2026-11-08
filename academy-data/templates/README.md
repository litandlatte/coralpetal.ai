# Academy templates

Every academy section page, course page, tutorial poster and short-link page is generated
from these files plus `../courses.json`. **Change a template once, then run**

    python3 scripts/build_academy_courses.py

**and commit everything under `academy/`.** The change lands on every course.

| # | File | Builds |
|---|---|---|
| 1 | `_head.html` | Page head + site header (`{{page_title}}`, `{{page_description}}`, `{{page_path}}`) |
| 2 | `_foot.html` | Site footer |
| 3 | `course.html` | `/<section>/<course>/` course page |
| 4 | `section.html` | `/<section>/` section page with course boxes |
| 5 | `poster.svg` | `/img/tutorials/<course>.svg` video poster |
| 6 | `shortlink.html` | `/<section>/<course>/{notes,slides,tutorial}/` fallback redirect page |

Placeholders are `{{name}}`; `{{> _head}}` and `{{> _foot}}` include the shared parts.
Lists (modules, prerequisites, course material boxes, course rows) are rendered as HTML by the
script and dropped into one placeholder each. Styling lives in `academy/css/styles.css`
(bump the `?v=` in `_head.html` after changing it, so browsers reload it).

Course material boxes (build script): Tutorial (sign-in), Reference materials (disabled for now: code, datasets and research papers used in the tutorial), Notes, Slides.
