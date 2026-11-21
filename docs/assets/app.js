(function () {
  "use strict";

  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  /* Mobile nav */
  const toggle = $(".nav-toggle");
  const nav = $(".nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* Lightbox */
  function openLightbox(src, caption) {
    let box = $(".lightbox");
    if (!box) {
      box = document.createElement("div");
      box.className = "lightbox";
      box.id = "lightbox";
      box.innerHTML = '<img alt=""><div class="lightbox-cap"></div>';
      box.addEventListener("click", (e) => {
        if (e.target === box) closeLightbox();
      });
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeLightbox();
      });
      document.body.appendChild(box);
    }
    box.querySelector("img").src = src;
    box.querySelector("img").alt = caption || "";
    box.querySelector(".lightbox-cap").textContent = caption || "";
    box.classList.add("is-open");
  }
  function closeLightbox() {
    const box = $(".lightbox");
    if (box) box.classList.remove("is-open");
  }
  document.addEventListener("click", (e) => {
    const img = e.target.closest(".article-body figure img, .hero-figure img");
    if (!img) return;
    e.preventDefault();
    const cap = img.closest("figure") && img.closest("figure").querySelector("figcaption");
    openLightbox(img.getAttribute("src"), cap ? cap.textContent.trim() : img.alt);
  });

  /* Mermaid */
  if (window.mermaid && $$(".mermaid").length) {
    try {
      window.mermaid.initialize({
        startOnLoad: true,
        theme: "dark",
        securityLevel: "loose",
        fontFamily: "inherit",
        themeVariables: {
          darkMode: true,
          background: "#16171f",
          primaryColor: "#2a241c",
          primaryTextColor: "#eceae4",
          primaryBorderColor: "#c6a572",
          lineColor: "#9c9a93",
          secondaryColor: "#1d1f2a",
          tertiaryColor: "#12131a",
          nodeTextColor: "#eceae4"
        },
        flowchart: { htmlLabels: true, curve: "basis" }
      });
    } catch (err) {
      console.warn("mermaid init failed", err);
    }
  }

  /* Browse filters */
  const grid = $("#case-grid");
  if (!grid || !window.CASES) return;

  const cases = window.CASES;
  const qInput = $("#q");
  const subSelect = $("#sub");
  const countEl = $("#result-count");
  const emptyEl = $("#empty-state");

  const params = new URLSearchParams(location.search);
  if (qInput && params.get("q")) qInput.value = params.get("q");

  const initialCat = params.get("cat") || "";
  const initialDiff = params.get("diff") || "";
  const initialSub = params.get("sub") || "";

  function activeChip(group, value) {
    $$('[data-filter="' + group + '"]').forEach((el) => {
      el.classList.toggle("is-on", (el.getAttribute("data-value") || "") === value);
    });
  }

  let cat = initialCat;
  let diff = initialDiff;
  let sub = initialSub;
  activeChip("cat", cat);
  activeChip("diff", diff);

  function fillSubs() {
    if (!subSelect) return;
    const set = new Map();
    cases.forEach((c) => {
      if (cat && c.catId !== cat) return;
      (c.subs || []).forEach((s) => set.set(s, true));
    });
    const cur = sub;
    subSelect.innerHTML = '<option value="">全部二级分类</option>';
    Array.from(set.keys())
      .sort()
      .forEach((s) => {
        const opt = document.createElement("option");
        opt.value = s;
        opt.textContent = s;
        subSelect.appendChild(opt);
      });
    if (cur && set.has(cur)) {
      subSelect.value = cur;
      sub = cur;
    } else {
      subSelect.value = "";
      sub = "";
    }
  }

  function stars(n) {
    const on = "★".repeat(n);
    const off = "☆".repeat(Math.max(0, 5 - n));
    return '<span class="stars">' + on + '<span class="off">' + off + "</span></span>";
  }

  function cardHTML(c) {
    const cover = c.cover
      ? '<img src="' + c.cover + '" alt="">'
      : '<div class="placeholder">无配图</div>';
    const neg = c.negative ? '<span class="chip badge-neg">反面案例</span>' : "";
    return (
      '<a class="card" href="' +
      c.href +
      '">' +
      '<div class="card-cover">' +
      cover +
      "</div>" +
      '<div class="card-body">' +
      "<h2 class=\"card-title\">" +
      escapeHtml(c.title) +
      "</h2>" +
      '<p class="card-summary">' +
      escapeHtml(c.summary || "") +
      "</p>" +
      '<div class="card-meta">' +
      '<span class="chip chip-' +
      c.catId +
      '">' +
      escapeHtml(c.catShort) +
      "</span>" +
      '<span class="chip chip-diff-' +
      escapeHtml(c.difficulty) +
      '">' +
      escapeHtml(c.difficulty) +
      "</span>" +
      stars(c.score) +
      neg +
      "</div></div></a>"
    );
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function apply() {
    const q = (qInput ? qInput.value : "").trim().toLowerCase();
    const shown = cases.filter((c) => {
      if (cat && c.catId !== cat) return false;
      if (diff && c.difficulty !== diff) return false;
      if (sub && !(c.subs || []).includes(sub)) return false;
      if (q) {
        const hay = (
          c.title +
          " " +
          (c.summary || "") +
          " " +
          (c.tags || []).join(" ") +
          " " +
          (c.products || []).join(" ") +
          " " +
          (c.materials || []).join(" ") +
          " " +
          (c.process || []).join(" ") +
          " " +
          (c.subs || []).join(" ")
        ).toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
    grid.innerHTML = shown.map(cardHTML).join("");
    if (countEl) {
      countEl.textContent = "显示 " + shown.length + " / " + cases.length + " 篇";
    }
    if (emptyEl) emptyEl.classList.toggle("hidden", shown.length > 0);
  }

  function syncURL() {
    const p = new URLSearchParams();
    const q = qInput ? qInput.value.trim() : "";
    if (q) p.set("q", q);
    if (cat) p.set("cat", cat);
    if (diff) p.set("diff", diff);
    if (sub) p.set("sub", sub);
    const qs = p.toString();
    const next = location.pathname + (qs ? "?" + qs : "") + location.hash;
    history.replaceState(null, "", next);
  }

  $$('[data-filter="cat"]').forEach((el) => {
    el.addEventListener("click", () => {
      const v = el.getAttribute("data-value") || "";
      cat = cat === v ? "" : v;
      activeChip("cat", cat);
      fillSubs();
      apply();
      syncURL();
    });
  });
  $$('[data-filter="diff"]').forEach((el) => {
    el.addEventListener("click", () => {
      const v = el.getAttribute("data-value") || "";
      diff = diff === v ? "" : v;
      activeChip("diff", diff);
      apply();
      syncURL();
    });
  });
  if (subSelect) {
    subSelect.addEventListener("change", () => {
      sub = subSelect.value;
      apply();
      syncURL();
    });
  }
  if (qInput) {
    let t;
    qInput.addEventListener("input", () => {
      clearTimeout(t);
      t = setTimeout(() => {
        apply();
        syncURL();
      }, 120);
    });
  }

  fillSubs();
  apply();
})();
