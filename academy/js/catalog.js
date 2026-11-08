/* Coral Petal AI Academy: catalog and course pages, rendered from /courses.json.
   To add or change a course, edit courses.json only. */
(function () {
  "use strict";

  var LEVELS = ["Beginner", "Intermediate", "Advanced"];

  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === "text") n.textContent = attrs[k];
      else if (k === "class") n.className = attrs[k];
      else n.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { if (c) n.appendChild(c); });
    return n;
  }

  function formatOf(course, groups) {
    var f = groups.Format || [];
    for (var i = 0; i < course.tags.length; i++) if (f.indexOf(course.tags[i]) >= 0) return course.tags[i];
    return "";
  }

  function tagLink(tag) {
    return el("a", { class: "tag", href: "/?tag=" + encodeURIComponent(tag), text: tag });
  }

  function card(course, groups) {
    var fmt = formatOf(course, groups);
    var tags = el("ul", { class: "tag-list", "aria-label": "Tags" },
      course.tags.filter(function (t) { return t !== fmt; }).map(function (t) { return el("li", null, [el("span", { class: "tag", text: t })]); }));
    return el("li", null, [
      el("a", { class: "course-card", href: "/course/?id=" + encodeURIComponent(course.slug) }, [
        el("div", { class: "course-meta" }, [
          el("span", { class: "format", text: fmt }),
          el("span", { class: "level", text: course.level })
        ]),
        el("h3", { text: course.title }),
        el("p", { text: course.summary }),
        tags,
        el("span", { class: "track-go", text: "View course →" })
      ])
    ]);
  }

  /* ---------- catalog ---------- */
  function catalog(data, root) {
    var groups = data.tagGroups, courses = data.courses;
    var params = new URLSearchParams(location.search);
    var state = { q: params.get("q") || "", tags: params.getAll("tag"), levels: params.getAll("level") };

    // Old section links (/?topic=…) map onto tags.
    params.getAll("topic").forEach(function (t) { if (state.tags.indexOf(t) < 0) state.tags.push(t); });

    var search = root.querySelector("#q");
    var filters = root.querySelector("#filters");
    var grid = root.querySelector("#results");
    var count = root.querySelector("#count");
    var active = root.querySelector("#active");
    search.value = state.q;

    function countFor(pred) { return courses.filter(pred).length; }

    function checkbox(name, value, n, checked) {
      var id = "f-" + name + "-" + value.toLowerCase().replace(/[^a-z0-9]+/g, "-");
      var input = el("input", { type: "checkbox", id: id, value: value });
      input.checked = checked;
      input.addEventListener("change", function () {
        var list = name === "level" ? state.levels : state.tags;
        var i = list.indexOf(value);
        if (input.checked && i < 0) list.push(value);
        if (!input.checked && i >= 0) list.splice(i, 1);
        render();
      });
      return el("li", null, [input, el("label", { for: id }, [document.createTextNode(value + " "), el("span", { class: "n", text: "(" + n + ")" })])]);
    }

    function buildFilters() {
      filters.textContent = "";
      Object.keys(groups).forEach(function (g) {
        var items = groups[g].filter(function (t) { return countFor(function (c) { return c.tags.indexOf(t) >= 0; }) > 0; });
        if (!items.length) return;
        filters.appendChild(el("fieldset", null, [
          el("legend", { text: g }),
          el("ul", null, items.map(function (t) {
            return checkbox("tag", t, countFor(function (c) { return c.tags.indexOf(t) >= 0; }), state.tags.indexOf(t) >= 0);
          }))
        ]));
      });
      filters.appendChild(el("fieldset", null, [
        el("legend", { text: "Level" }),
        el("ul", null, LEVELS.filter(function (l) { return countFor(function (c) { return c.level === l; }) > 0; }).map(function (l) {
          return checkbox("level", l, countFor(function (c) { return c.level === l; }), state.levels.indexOf(l) >= 0);
        }))
      ]));
    }

    function groupOf(tag) {
      return Object.keys(groups).filter(function (g) { return groups[g].indexOf(tag) >= 0; })[0];
    }

    function matches(c) {
      // Within a group: any selected tag matches (OR). Across groups: all groups must match (AND).
      var byGroup = {};
      state.tags.forEach(function (t) { var g = groupOf(t) || "Other"; (byGroup[g] = byGroup[g] || []).push(t); });
      for (var g in byGroup) if (!byGroup[g].some(function (t) { return c.tags.indexOf(t) >= 0; })) return false;
      if (state.levels.length && state.levels.indexOf(c.level) < 0) return false;
      if (state.q) {
        var hay = (c.title + " " + c.summary + " " + c.tags.join(" ") + " " + c.level).toLowerCase();
        var words = state.q.toLowerCase().split(/\s+/).filter(Boolean);
        if (!words.every(function (w) { return hay.indexOf(w) >= 0; })) return false;
      }
      return true;
    }

    function syncUrl() {
      var p = new URLSearchParams();
      if (state.q) p.set("q", state.q);
      state.tags.forEach(function (t) { p.append("tag", t); });
      state.levels.forEach(function (l) { p.append("level", l); });
      var s = p.toString();
      try { history.replaceState(null, "", s ? "?" + s : location.pathname); } catch (e) { /* ignore */ }
    }

    function render() {
      var list = courses.filter(matches);
      grid.textContent = "";
      list.forEach(function (c) { grid.appendChild(card(c, groups)); });
      count.textContent = list.length + (list.length === 1 ? " course" : " courses");
      active.textContent = "";
      state.tags.concat(state.levels).forEach(function (t) {
        var b = el("button", { type: "button", class: "chip-active", "aria-label": "Remove filter " + t }, [document.createTextNode(t + " ×")]);
        b.addEventListener("click", function () {
          [state.tags, state.levels].forEach(function (l) { var i = l.indexOf(t); if (i >= 0) l.splice(i, 1); });
          buildFilters(); render();
        });
        active.appendChild(b);
      });
      if (state.tags.length || state.levels.length || state.q) {
        var clear = el("button", { type: "button", class: "chip-clear", text: "Clear all" });
        clear.addEventListener("click", function () { state.tags = []; state.levels = []; state.q = ""; search.value = ""; buildFilters(); render(); });
        active.appendChild(clear);
      }
      if (!list.length) grid.appendChild(el("li", { class: "empty" }, [el("p", { text: "No courses match these filters. Remove a filter or try another search." })]));
      syncUrl();
    }

    search.addEventListener("input", function () { state.q = search.value.trim(); render(); });
    // On phones the filter panel starts collapsed so courses are visible first.
    var det = root.querySelector(".filters details");
    if (det && window.matchMedia && window.matchMedia("(max-width: 860px)").matches && !state.tags.length && !state.levels.length) det.open = false;
    root.querySelectorAll("[data-tag]").forEach(function (a) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        state.tags = [a.getAttribute("data-tag")]; state.levels = []; state.q = ""; search.value = "";
        buildFilters(); render();
        document.getElementById("catalog").scrollIntoView({ behavior: "smooth" });
      });
    });
    buildFilters();
    render();
  }

  /* ---------- course page ---------- */
  function coursePage(data, root) {
    var id = new URLSearchParams(location.search).get("id");
    var c = data.courses.filter(function (x) { return x.slug === id; })[0];
    if (!c) {
      root.textContent = "";
      root.appendChild(el("h1", { text: "Course not found" }));
      root.appendChild(el("p", null, [document.createTextNode("This course isn't in the catalog. "), el("a", { href: "/", text: "Browse all courses" })]));
      root.hidden = false;
      return;
    }
    document.title = c.title + " | Coral Petal AI Academy";
    var fmt = formatOf(c, data.tagGroups);
    root.querySelector("#c-crumb").textContent = c.title;
    root.querySelector("#c-format").textContent = fmt;
    root.querySelector("#c-level").textContent = c.level;
    root.querySelector("#c-title").textContent = c.title;
    root.querySelector("#c-summary").textContent = c.summary;
    var tags = root.querySelector("#c-tags");
    c.tags.forEach(function (t) { tags.appendChild(el("li", null, [tagLink(t)])); });
    var out = root.querySelector("#c-outline");
    (c.outline || []).forEach(function (o) { out.appendChild(el("li", { text: o })); });
    root.querySelector("#c-outline-wrap").hidden = !(c.outline || []).length;

    // Related: courses sharing the most non-format tags.
    var fmts = data.tagGroups.Format || [];
    var mine = c.tags.filter(function (t) { return fmts.indexOf(t) < 0; });
    var rel = data.courses.filter(function (x) { return x.slug !== c.slug; })
      .map(function (x) { return { c: x, s: x.tags.filter(function (t) { return mine.indexOf(t) >= 0; }).length }; })
      .filter(function (r) { return r.s > 0; })
      .sort(function (a, b) { return b.s - a.s; }).slice(0, 3);
    var relGrid = root.querySelector("#c-related");
    rel.forEach(function (r) { relGrid.appendChild(card(r.c, data.tagGroups)); });
    root.querySelector("#c-related-wrap").hidden = !rel.length;
    root.hidden = false;
  }

  function boot() {
    var cat = document.getElementById("catalog");
    var page = document.getElementById("course");
    if (!cat && !page) return;
    fetch("/courses.json", { cache: "no-cache" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) { if (cat) catalog(data, cat); if (page) coursePage(data, page); })
      .catch(function () {
        var box = cat || page;
        box.hidden = false;
        box.insertBefore(el("p", { class: "load-error", text: "The course list couldn't load. Refresh the page to try again." }), box.firstChild);
      });
  }

  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();
  boot();
})();
