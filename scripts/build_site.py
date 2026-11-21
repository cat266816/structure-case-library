#!/usr/bin/env python3
"""从 Obsidian vault 生成 GitHub Pages 静态站点（docs/）。

用法：
  python3 scripts/build_site.py
  python3 scripts/build_site.py --base /structure-case-library/
  python3 scripts/build_site.py --base /
"""

from __future__ import annotations

import argparse
import html as htmlmod
import json
import re
import shutil
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

import yaml

ROOT = Path(__file__).resolve().parent.parent
VAULT = ROOT / "vault"
DOCS = ROOT / "docs"
TEMPLATES = Path(__file__).resolve().parent / "templates"
ATTACH_DIR = VAULT / "附件"

CATEGORIES = [
    {
        "id": "01",
        "dir": "01-壳体与外观件",
        "full": "01-壳体与外观件",
        "name": "壳体与外观件",
        "blurb": "外壳拆分、外观件固定、壁厚/加强筋、开孔、覆面等「看得见的结构」。",
        "color": "#c4896a",
    },
    {
        "id": "02",
        "dir": "02-连接与紧固",
        "full": "02-连接与紧固",
        "name": "连接与紧固",
        "blurb": "零件之间如何连在一起：卡扣、螺丝与嵌件、卡口、滑轨、磁吸、胶粘、焊接等。",
        "color": "#c6a572",
    },
    {
        "id": "03",
        "dir": "03-转轴与铰链",
        "full": "03-转轴与铰链",
        "name": "转轴与铰链",
        "blurb": "一切转动连接：阻尼转轴、折叠屏铰链、360° 转轴、一体成型活动铰链。",
        "color": "#7f92b3",
    },
    {
        "id": "04",
        "dir": "04-机构与运动",
        "full": "04-机构与运动",
        "name": "机构与运动",
        "blurb": "会动的机构：按压弹跳、锁扣、齿轮/蜗杆、凸轮连杆、弹簧、柔顺机构、力反馈。",
        "color": "#7d9b7a",
    },
    {
        "id": "05",
        "dir": "05-密封与防护",
        "full": "05-密封与防护",
        "name": "密封与防护",
        "blurb": "防水、防尘、防跌：密封圈、O 形圈、点胶、CIPG、透气膜、缓冲结构。",
        "color": "#6a9aa4",
    },
    {
        "id": "06",
        "dir": "06-拆解与可维修",
        "full": "06-拆解与可维修",
        "name": "拆解与可维修",
        "blurb": "整机拆解分析、模块化、可维修设计，以及值得警惕的反面案例。",
        "color": "#8b84b0",
    },
    {
        "id": "07",
        "dir": "07-材料与工艺",
        "full": "07-材料与工艺",
        "name": "材料与工艺",
        "blurb": "注塑、钣金、压铸/CNC、3D 打印、包胶双色、表面处理对结构的约束与案例。",
        "color": "#b4836e",
    },
]
CAT_BY_FULL = {c["full"]: c for c in CATEGORIES}

BASE = ""  # set in main(); empty = relative paths


def enc_seg(s: str) -> str:
    """Encode only unsafe ASCII; keep unicode for readable IRIs."""
    out = []
    safe = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~()（）")
    for ch in s:
        if ch in safe or ord(ch) > 127:
            out.append(ch)
        elif ch == " ":
            out.append("%20")
        else:
            out.append(quote(ch, safe=""))
    return "".join(out)


def anchor_id(s: str) -> str:
    s = re.sub(r"[^\w\u4e00-\u9fff]+", "-", s, flags=re.UNICODE).strip("-")
    return s or "section"


def url(path: str, depth: int) -> str:
    path = path.lstrip("/")
    if BASE:
        return BASE.rstrip("/") + "/" + path
    if depth <= 0:
        return path
    return "../" * depth + path


def case_url(slug: str, depth: int) -> str:
    return url("cases/" + enc_seg(slug) + ".html", depth)


def img_url(filename: str, depth: int) -> str:
    return url("images/" + enc_seg(filename), depth)


def as_list(val) -> list:
    if val is None or val == "":
        return []
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    return [str(val).strip()]


def as_str(val) -> str:
    if val is None:
        return ""
    if isinstance(val, datetime):
        return val.date().isoformat()
    if isinstance(val, date):
        return val.isoformat()
    return str(val).strip().strip('"')


def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    data = yaml.safe_load(text[3:end]) or {}
    body = text[end + 4 :]
    if body.startswith("\n"):
        body = body[1:]
    return data, body


def stars_html(n) -> str:
    try:
        n = int(n)
    except (TypeError, ValueError):
        n = 0
    n = max(0, min(5, n))
    return (
        '<span class="stars">'
        + ("★" * n)
        + '<span class="off">'
        + ("☆" * (5 - n))
        + "</span></span>"
    )


def is_negative(title, subs, tags) -> bool:
    hay = title + " " + " ".join(subs) + " " + " ".join(tags)
    return "反面案例" in hay


WIKILINK_RE = re.compile(r"(!)?\[\[([^\]]+)\]\]")


def split_wikilink(inner: str):
    inner = inner.strip().rstrip("\\").strip()
    parts = re.split(r"(?<!\\)\|", inner)
    target = parts[0].strip().replace("\\|", "|")
    alias = parts[1].strip() if len(parts) > 1 else None
    if target.endswith(".md"):
        target = target[:-3]
    if "/" in target and not target.startswith("附件"):
        target = target.rsplit("/", 1)[-1]
    return target, alias


class Linker:
    def __init__(self, cases):
        self.by_key = {}
        for c in cases:
            self.by_key[c["slug"]] = c
            self.by_key[c["title"]] = c
        self.special = {
            "首页": ("index.html", "首页"),
            "案例地图.canvas": ("map.html", "案例地图"),
            "案例地图": ("map.html", "案例地图"),
        }
        for cat in CATEGORIES:
            self.special[f"{cat['full']} 索引"] = (f"categories/{cat['id']}.html", cat["name"])
            self.special[f"{cat['dir']} 索引"] = (f"categories/{cat['id']}.html", cat["name"])
            self.special[f"{cat['name']} 索引"] = (f"categories/{cat['id']}.html", cat["name"])

    def resolve(self, target: str, depth: int):
        target = target.strip()
        if target in self.special:
            path, label = self.special[target]
            return url(path, depth), label
        case = self.by_key.get(target)
        if case:
            return case_url(case["slug"], depth), case["title"]
        return None


def extract_summary(body: str) -> str:
    m = re.search(r">\s*\[!summary\][^\n]*\n((?:>[^\n]*(?:\n|$))+)", body)
    if not m:
        return ""
    lines = []
    for line in m.group(1).splitlines():
        line = re.sub(r"^>\s?", "", line)
        lines.append(line)
    text = re.sub(r"\s+", " ", " ".join(lines)).strip()
    def _plain(m):
        if m.group(1):
            return ""
        target, alias = split_wikilink(m.group(2))
        return alias or target
    return WIKILINK_RE.sub(_plain, text)


def inline_md(text: str, linker: Linker, depth: int) -> str:
    tokens = []

    def stash(html: str) -> str:
        key = f"\x00T{len(tokens)}\x00"
        tokens.append((key, html))
        return key

    def repl_code(m):
        return stash(f"<code>{htmlmod.escape(m.group(1))}</code>")

    text = re.sub(r"`([^`]+)`", repl_code, text)

    def repl_html(m):
        return stash(m.group(0))

    text = re.sub(r"<a\s[^>]*>.*?</a>", repl_html, text)
    text = re.sub(r"<span\s[^>]*>.*?</span>", repl_html, text)
    text = re.sub(r"<img\s[^>]*>", repl_html, text)
    text = re.sub(r"<strong>.*?</strong>", repl_html, text)
    text = re.sub(r"<em>.*?</em>", repl_html, text)
    text = re.sub(r"<code>.*?</code>", repl_html, text)

    def repl_img(m):
        alt, href = m.group(1), m.group(2)
        return stash(
            f'<img src="{htmlmod.escape(href, quote=True)}" alt="{htmlmod.escape(alt, quote=True)}">'
        )

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", repl_img, text)

    def repl_link(m):
        label, href = m.group(1), m.group(2)
        ext = href.startswith("http://") or href.startswith("https://")
        attrs = ' target="_blank" rel="noopener noreferrer"' if ext else ""
        return stash(
            f'<a href="{htmlmod.escape(href, quote=True)}"{attrs}>{htmlmod.escape(label)}</a>'
        )

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl_link, text)

    def repl_auto(m):
        href = m.group(1)
        return stash(
            f'<a href="{htmlmod.escape(href, quote=True)}" target="_blank" rel="noopener noreferrer">{htmlmod.escape(href)}</a>'
        )

    text = re.sub(r"<(https?://[^>\s]+)>", repl_auto, text)

    def repl_bold(m):
        inner = m.group(1)
        inner_html = re.sub(
            r"(?<!\*)\*([^*\n]+)\*(?!\*)",
            lambda mm: f"<em>{htmlmod.escape(mm.group(1))}</em>",
            inner,
        )
        if "<em>" in inner_html:
            # escape parts outside em
            inner_html = re.sub(
                r"(?:<em>.*?</em>)|([^<]+)",
                lambda mm: mm.group(0) if mm.group(0).startswith("<em>") else htmlmod.escape(mm.group(0)),
                inner_html,
            )
            return stash(f"<strong>{inner_html}</strong>")
        return stash(f"<strong>{htmlmod.escape(inner)}</strong>")

    text = re.sub(r"\*\*(.+?)\*\*", repl_bold, text)
    text = re.sub(
        r"(?<!\*)\*([^*\n]+)\*(?!\*)",
        lambda m: stash(f"<em>{htmlmod.escape(m.group(1))}</em>"),
        text,
    )

    text = htmlmod.escape(text)
    for key, html in tokens:
        text = text.replace(htmlmod.escape(key), html)
        text = text.replace(key, html)
    return text


def convert_wikilinks_in_text(text: str, linker: Linker, depth: int) -> str:
    def repl(m):
        is_img, inner = m.group(1), m.group(2)
        target, alias = split_wikilink(inner)
        if is_img:
            name = target.replace("附件/", "").split("/")[-1]
            src = img_url(name, depth)
            alt = alias or name
            return f'<img src="{htmlmod.escape(src, quote=True)}" alt="{htmlmod.escape(alt, quote=True)}">'
        resolved = linker.resolve(target, depth)
        label = alias or (resolved[1] if resolved else target)
        if resolved:
            return f'<a href="{htmlmod.escape(resolved[0], quote=True)}">{htmlmod.escape(label)}</a>'
        return htmlmod.escape(label)

    return WIKILINK_RE.sub(repl, text)


CALLOUT_RE = re.compile(r"^> \[!(\w+)\][^\n]*\n((?:^>.*\n?)*)", re.M)


def parse_callout_title(first_line: str):
    m = re.match(r"> \[!(\w+)\]\s*(.*)$", first_line)
    if not m:
        return "note", ""
    return m.group(1).lower(), m.group(2).strip()


def md_to_html(body: str, linker: Linker, depth: int, attach_used: set) -> str:
    placeholders = {}
    counter = [0]

    def put(html: str) -> str:
        counter[0] += 1
        key = f"%%PLACE_{counter[0]}%%"
        placeholders[key] = html
        return key

    text = body.replace("\r\n", "\n")

    def repl_mermaid(m):
        src = m.group(1).strip("\n")
        escaped = htmlmod.escape(src)
        return put(f'<pre class="mermaid">\n{escaped}\n</pre>') + "\n"

    text = re.sub(r"```mermaid[^\n]*\n(.*?)```", repl_mermaid, text, flags=re.S)

    def repl_code(m):
        lang = m.group(1) or ""
        src = htmlmod.escape(m.group(2).strip("\n"))
        cls = f' class="language-{htmlmod.escape(lang, quote=True)}"' if lang else ""
        return put(f"<pre><code{cls}>{src}</code></pre>") + "\n"

    text = re.sub(r"```(\w+)?[^\n]*\n(.*?)```", repl_code, text, flags=re.S)
    text = re.sub(r"```dataview[^\n]*\n.*?```", "", text, flags=re.S)

    def repl_figure(m):
        inner = m.group(1)
        caption = m.group(2) or ""
        target, alias = split_wikilink(inner)
        name = target.replace("附件/", "").split("/")[-1]
        attach_used.add(name)
        src = img_url(name, depth)
        cap_html = ""
        if caption:
            cap_inner = convert_wikilinks_in_text(caption, linker, depth)
            cap_html = f"<figcaption>{inline_md(cap_inner, linker, depth)}</figcaption>"
        alt = alias or (re.sub(r"<[^>]+>", "", caption)[:80] if caption else name)
        return (
            put(
                "<figure>"
                f'<img src="{htmlmod.escape(src, quote=True)}" alt="{htmlmod.escape(alt, quote=True)}">'
                f"{cap_html}</figure>"
            )
            + "\n"
        )

    text = re.sub(
        r"!\[\[([^\]]+)\]\]\s*(?:\n\s*\*(.+?)\*\s*)?",
        repl_figure,
        text,
    )

    def repl_callout(m):
        raw_block = m.group(0)
        first, _, rest = raw_block.partition("\n")
        typ, title = parse_callout_title(first)
        body_lines = []
        for line in rest.splitlines():
            if line.startswith(">"):
                line = line[1:]
                if line.startswith(" "):
                    line = line[1:]
            body_lines.append(line)
        inner = "\n".join(body_lines).strip()
        if typ == "summary":
            return "\n"
        inner = convert_wikilinks_in_text(inner, linker, depth)
        inner_html = blocks_to_html(inner, linker, depth, placeholders)
        defaults = {"summary": "一句话概述", "note": "说明"}
        title_html = htmlmod.escape(title) if title else defaults.get(typ, typ)
        return (
            put(
                f'<aside class="callout callout-{htmlmod.escape(typ, quote=True)}">'
                f'<div class="callout-title">{title_html}</div>{inner_html}</aside>'
            )
            + "\n"
        )

    text = CALLOUT_RE.sub(repl_callout, text)
    text = convert_wikilinks_in_text(text, linker, depth)
    return blocks_to_html(text, linker, depth, placeholders)


def is_placeholder_line(line: str) -> bool:
    s = line.strip()
    return s.startswith("%%PLACE_") and s.endswith("%%")


def is_hr(line: str) -> bool:
    s = line.strip()
    return bool(re.match(r"^(-{3,}|\*{3,}|_{3,})$", s))


def is_table_start(lines, i: int) -> bool:
    if i + 1 >= len(lines):
        return False
    if "|" not in lines[i]:
        return False
    return bool(re.match(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$", lines[i + 1]))


def split_row(line: str):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)]


def blocks_to_html(text: str, linker: Linker, depth: int, placeholders: dict) -> str:
    lines = text.split("\n")
    i = 0
    out = []

    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        if is_placeholder_line(line):
            out.append(placeholders.get(line.strip(), ""))
            i += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            level = len(heading.group(1))
            raw = heading.group(2).strip()
            out.append(f"<h{level}>{inline_md(raw, linker, depth)}</h{level}>")
            i += 1
            continue
        if is_hr(line):
            out.append("<hr>")
            i += 1
            continue
        if is_table_start(lines, i):
            rows = [split_row(lines[i])]
            i += 2
            while i < len(lines) and "|" in lines[i] and not is_hr(lines[i]):
                if is_placeholder_line(lines[i]):
                    break
                if re.match(r"^#{1,6}\s", lines[i]):
                    break
                rows.append(split_row(lines[i]))
                i += 1
            html = ['<div class="table-wrap"><table><thead><tr>']
            for cell in rows[0]:
                html.append(f"<th>{inline_md(cell, linker, depth)}</th>")
            html.append("</tr></thead><tbody>")
            for row in rows[1:]:
                html.append("<tr>")
                for cell in row:
                    html.append(f"<td>{inline_md(cell, linker, depth)}</td>")
                html.append("</tr>")
            html.append("</tbody></table></div>")
            out.append("".join(html))
            continue
        list_m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.+)$", line)
        if list_m:
            html, i = parse_list(lines, i, linker, depth)
            out.append(html)
            continue
        if line.startswith(">"):
            buf = []
            while i < len(lines) and (lines[i].startswith(">") or lines[i].strip() == ">"):
                l = lines[i][1:] if lines[i].startswith(">") else lines[i]
                if l.startswith(" "):
                    l = l[1:]
                buf.append(l)
                i += 1
            inner = blocks_to_html("\n".join(buf), linker, depth, placeholders)
            out.append(f"<blockquote>{inner}</blockquote>")
            continue
        buf = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if nxt.strip() == "":
                break
            if is_placeholder_line(nxt) or is_hr(nxt) or is_table_start(lines, i):
                break
            if re.match(r"^#{1,6}\s", nxt):
                break
            if re.match(r"^(\s*)([-*+]|\d+\.)\s+", nxt):
                break
            if nxt.startswith(">"):
                break
            buf.append(nxt)
            i += 1
        para = " ".join(x.strip() for x in buf)
        out.append(f"<p>{inline_md(para, linker, depth)}</p>")
    return "\n".join(out)


def parse_list(lines, i, linker, depth):
    items = []
    while i < len(lines):
        m = re.match(r"^(\s*)([-*+]|\d+\.)\s+(.*)$", lines[i])
        if not m:
            break
        indent = len(m.group(1).replace("\t", "    "))
        typ = "ol" if re.match(r"\d+\.", m.group(2)) else "ul"
        text = m.group(3)
        i += 1
        extra = []
        while i < len(lines):
            nxt = lines[i]
            if nxt.strip() == "":
                j = i + 1
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                if j < len(lines) and re.match(r"^(\s*)([-*+]|\d+\.)\s+", lines[j]):
                    break
                if j < len(lines) and len(lines[j]) - len(lines[j].lstrip()) > indent:
                    extra.append("")
                    i += 1
                    continue
                break
            if re.match(r"^(\s*)([-*+]|\d+\.)\s+", nxt):
                break
            extra.append(nxt)
            i += 1
        items.append((indent, typ, text, extra))
    return render_list(items, linker, depth), i


def render_list(items, linker, depth) -> str:
    if not items:
        return ""
    base = items[0][0]
    typ = items[0][1]
    parts = [f"<{typ}>"]
    k = 0
    while k < len(items):
        indent, _, text, extra = items[k]
        if indent < base:
            break
        if indent > base:
            k += 1
            continue
        k += 1
        children = []
        while k < len(items) and items[k][0] > base:
            children.append(items[k])
            k += 1
        inner = inline_md(text, linker, depth)
        if extra:
            extra_txt = " ".join(x.strip() for x in extra if x.strip())
            if extra_txt:
                inner += " " + inline_md(extra_txt, linker, depth)
        if children:
            inner += render_list(children, linker, depth)
        parts.append(f"<li>{inner}</li>")
    parts.append(f"</{typ}>")
    return "".join(parts)


def load_cases():
    cases = []
    for cat in CATEGORIES:
        folder = VAULT / cat["dir"]
        for path in sorted(folder.glob("*.md")):
            if "索引" in path.name:
                continue
            text = path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            title = as_str(fm.get("标题")) or path.stem
            slug = path.stem
            cover = as_str(fm.get("封面图"))
            cover_name = ""
            if cover:
                cover_name = cover.replace("附件/", "").replace("\\", "/").split("/")[-1]
            summary = extract_summary(body)
            cases.append(
                {
                    "slug": slug,
                    "path": path,
                    "title": title,
                    "body": body,
                    "cat": cat,
                    "subs": as_list(fm.get("二级分类")),
                    "products": as_list(fm.get("应用产品")),
                    "materials": as_list(fm.get("材料")),
                    "process": as_list(fm.get("工艺")),
                    "tags": as_list(fm.get("标签")),
                    "difficulty": as_str(fm.get("难度")) or "进阶",
                    "platform": as_str(fm.get("来源平台")),
                    "source": as_str(fm.get("来源链接")),
                    "extra_sources": as_list(fm.get("补充来源")),
                    "date": as_str(fm.get("收录日期")),
                    "score": int(fm.get("评分") or 0),
                    "verified": as_str(fm.get("核实状态")),
                    "cover": cover_name,
                    "summary": summary,
                    "negative": is_negative(
                        title, as_list(fm.get("二级分类")), as_list(fm.get("标签"))
                    ),
                    "fm": fm,
                }
            )
    cases.sort(key=lambda c: (c["cat"]["id"], c["title"]))
    return cases


FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#c6a572" stroke-width="1.6">
  <rect x="2.5" y="4.5" width="14" height="11" rx="1.6"/>
  <rect x="7.5" y="8.5" width="14" height="11" rx="1.6"/>
</svg>"""

BRAND_MARK = """<svg class="brand-mark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
  <rect x="2.5" y="4.5" width="14" height="11" rx="1.6"/>
  <rect x="7.5" y="8.5" width="14" height="11" rx="1.6"/>
</svg>"""


def layout(title, body, depth, active="", description="", extra_head="", extra_js="", mermaid=False):
    site = "结构设计案例库"
    full_title = site if title == site else f"{title} · {site}"
    desc = description or "产品与机械结构设计案例库：壳体、连接与紧固、转轴铰链、机构与运动、密封防护、拆解与可维修、材料与工艺。"

    def nav_item(key, path, label):
        href = url(path, depth)
        cls = ' class="is-active"' if active == key else ""
        return f'<a href="{href}"{cls}>{label}</a>'

    mermaid_tag = ""
    if mermaid:
        mermaid_tag = f'<script src="{url("assets/mermaid.min.js", depth)}"></script>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{htmlmod.escape(full_title)}</title>
  <meta name="description" content="{htmlmod.escape(desc, quote=True)}">
  <link rel="icon" href="{url("assets/favicon.svg", depth)}" type="image/svg+xml">
  <link rel="stylesheet" href="{url("assets/style.css", depth)}">
  {extra_head}
</head>
<body>
  <a class="skip-link" href="#main">跳到正文</a>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="{url("index.html", depth)}">{BRAND_MARK}<span>{site}</span></a>
      <button class="nav-toggle" type="button" aria-label="打开菜单" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
      <nav class="nav" id="nav">
        {nav_item("home", "index.html", "首页")}
        {nav_item("browse", "browse.html", "浏览案例")}
        {nav_item("map", "map.html", "案例地图")}
      </nav>
    </div>
  </header>
  <main id="main">
    {body}
  </main>
  <footer class="site-footer">
    <div class="footer-inner">
      <div>仅供个人学习，配图版权归原作者。</div>
      <div>结构设计案例库 · 静态站点，可部署到 GitHub Pages</div>
    </div>
  </footer>
  <script src="{url("assets/config.js", depth)}"></script>
  {mermaid_tag}
  <script src="{url("assets/app.js", depth)}"></script>
  {extra_js}
</body>
</html>
"""


def chips_for_case(c):
    cat = c["cat"]
    bits = [
        f'<span class="chip chip-{cat["id"]}">{htmlmod.escape(cat["name"])}</span>',
        f'<span class="chip chip-diff-{htmlmod.escape(c["difficulty"])}">{htmlmod.escape(c["difficulty"])}</span>',
        stars_html(c["score"]),
    ]
    if c["negative"]:
        bits.append('<span class="chip badge-neg">反面案例</span>')
    if c["date"]:
        bits.append(f'<span class="chip">{htmlmod.escape(c["date"])}</span>')
    return "\n".join(bits)


def card_html(c, depth):
    href = case_url(c["slug"], depth)
    if c["cover"]:
        cover = f'<img src="{img_url(c["cover"], depth)}" alt="">'
    else:
        cover = '<div class="placeholder">无配图</div>'
    neg = '<span class="chip badge-neg">反面案例</span>' if c["negative"] else ""
    return f"""<a class="card" href="{href}">
  <div class="card-cover">{cover}</div>
  <div class="card-body">
    <h3 class="card-title">{htmlmod.escape(c["title"])}</h3>
    <p class="card-summary">{htmlmod.escape(c["summary"])}</p>
    <div class="card-meta">
      <span class="chip chip-{c["cat"]["id"]}">{htmlmod.escape(c["cat"]["name"])}</span>
      <span class="chip chip-diff-{htmlmod.escape(c["difficulty"])}">{htmlmod.escape(c["difficulty"])}</span>
      {stars_html(c["score"])}
      {neg}
    </div>
  </div>
</a>"""


def list_or_dash(items):
    items = [x for x in items if x]
    if not items:
        return "—"
    if len(items) == 1:
        return htmlmod.escape(items[0])
    return "<ul>" + "".join(f"<li>{htmlmod.escape(x)}</li>" for x in items) + "</ul>"


def ext_link(href, label=None):
    if not href:
        return "—"
    label = label or href
    return (
        f'<a class="source-link" href="{htmlmod.escape(href, quote=True)}" '
        f'target="_blank" rel="noopener noreferrer">{htmlmod.escape(label)}</a>'
    )


def build_home(cases):
    n = len(cases)
    avg = round(sum(c["score"] for c in cases) / n, 1) if n else 0
    last = max((c["date"] for c in cases if c["date"]), default="")
    cats_n = len(CATEGORIES)
    latest = sorted(cases, key=lambda c: (c["date"], c["score"]), reverse=True)[:12]
    featured = sorted(
        [c for c in cases if c["score"] >= 5],
        key=lambda c: (c["date"], c["score"]),
        reverse=True,
    )[:12]

    cat_cards = []
    for cat in CATEGORIES:
        group = [c for c in cases if c["cat"]["id"] == cat["id"]]
        cover_case = next(
            (c for c in sorted(group, key=lambda x: (-x["score"], x["date"])) if c["cover"]),
            None,
        )
        cover = (
            f'<img src="{img_url(cover_case["cover"], 0)}" alt="">'
            if cover_case
            else '<div class="placeholder"></div>'
        )
        cat_cards.append(
            f"""<a class="cat-card" href="{url('categories/' + cat['id'] + '.html', 0)}" style="--cat-color:{cat['color']}">
  <div class="cat-card-cover">{cover}</div>
  <div class="cat-card-body">
    <div class="cat-card-kicker">{cat["id"]}</div>
    <h3>{htmlmod.escape(cat["name"])}</h3>
    <p>{htmlmod.escape(cat["blurb"])}</p>
    <div class="cat-count">{len(group)} 篇</div>
  </div>
</a>"""
        )

    body = f"""
<section class="hero">
  <div class="wrap">
    <p class="hero-kicker">Product structure cases</p>
    <h1>结构设计案例库</h1>
    <p class="hero-lede">按结构原理归档的产品与机械设计案例，覆盖壳体与外观件、连接与紧固、转轴与铰链、机构与运动、密封与防护、拆解与可维修、材料与工艺。参数只写来源里已有的，不估算、不编造。</p>
    <div class="stats">
      <div class="stat"><div class="stat-value">{n}</div><div class="stat-label">篇案例</div></div>
      <div class="stat"><div class="stat-value">{cats_n}</div><div class="stat-label">个一级分类</div></div>
      <div class="stat"><div class="stat-value">{avg}</div><div class="stat-label">平均评分</div></div>
      <div class="stat"><div class="stat-value">{htmlmod.escape(last)}</div><div class="stat-label">最近更新</div></div>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head">
      <h2>分类入口</h2>
      <a class="section-more" href="{url("browse.html", 0)}">浏览全部</a>
    </div>
    <div class="cat-grid">
      {"".join(cat_cards)}
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="section-head">
      <h2>最新收录</h2>
      <a class="section-more" href="{url("browse.html", 0)}">全部案例</a>
    </div>
    <div class="card-grid">
      {"".join(card_html(c, 0) for c in latest)}
    </div>
  </div>
</section>
<section class="section" style="padding-bottom:64px">
  <div class="wrap">
    <div class="section-head">
      <h2>精选案例</h2>
      <span class="section-more">评分 5 分</span>
    </div>
    <div class="card-grid">
      {"".join(card_html(c, 0) for c in featured)}
    </div>
  </div>
</section>
"""
    return layout("结构设计案例库", body, 0, active="home")


def build_browse(cases):
    cat_btns = ['<button type="button" class="filter-chip" data-filter="cat" data-value="">全部</button>']
    for cat in CATEGORIES:
        cat_btns.append(
            f'<button type="button" class="filter-chip" data-filter="cat" data-value="{cat["id"]}">{htmlmod.escape(cat["name"])}</button>'
        )
    diff_btns = ['<button type="button" class="filter-chip" data-filter="diff" data-value="">全部</button>']
    for d in ("入门", "进阶", "高级"):
        diff_btns.append(
            f'<button type="button" class="filter-chip" data-filter="diff" data-value="{htmlmod.escape(d)}">{d}</button>'
        )
    body = f"""
<div class="wrap">
  <div class="page-head">
    <h1>浏览案例</h1>
    <p>按关键词、一级/二级分类和难度筛选。共 {len(cases)} 篇。</p>
  </div>
  <div class="filters">
    <div class="filter-row">
      <span class="filter-label">搜索</span>
      <input class="search-input" id="q" type="search" placeholder="标题、概述、标签、材料、工艺…" autocomplete="off">
    </div>
    <div class="filter-row">
      <span class="filter-label">一级分类</span>
      {"".join(cat_btns)}
    </div>
    <div class="filter-row">
      <span class="filter-label">难度</span>
      {"".join(diff_btns)}
    </div>
    <div class="filter-row">
      <span class="filter-label">二级分类</span>
      <select class="select-input" id="sub"></select>
    </div>
  </div>
  <p class="result-count" id="result-count"></p>
  <div class="card-grid" id="case-grid"></div>
  <div class="empty-state hidden" id="empty-state">没有符合条件的案例。试试减少筛选条件。</div>
  <p style="height:48px"></p>
</div>
"""
    extra_js = f'<script src="{url("assets/data.js", 0)}"></script>'
    return layout("浏览案例", body, 0, active="browse", extra_js=extra_js)


def build_category(cat, cases):
    group = [c for c in cases if c["cat"]["id"] == cat["id"]]
    order = []
    for c in group:
        for s in c["subs"]:
            if s not in order:
                order.append(s)
    by_sub = defaultdict(list)
    placed = set()
    for s in order:
        for c in group:
            if s in c["subs"]:
                by_sub[s].append(c)
                placed.add(c["slug"])
    ungrouped = [c for c in group if c["slug"] not in placed]

    jump = []
    for s in order:
        jump.append(f'<a href="#{anchor_id(s)}">{htmlmod.escape(s)} ({len(by_sub[s])})</a>')
    if ungrouped:
        jump.append(f'<a href="#ungrouped">未分组 ({len(ungrouped)})</a>')

    blocks = []
    for s in order:
        cards = "".join(card_html(c, 1) for c in by_sub[s])
        blocks.append(
            f'<section class="sub-block" id="{anchor_id(s)}">'
            f'<h2>{htmlmod.escape(s)} <span class="count">{len(by_sub[s])} 篇</span></h2>'
            f'<div class="card-grid">{cards}</div>'
            f"</section>"
        )
    if ungrouped:
        cards = "".join(card_html(c, 1) for c in ungrouped)
        blocks.append(
            f'<section class="sub-block" id="ungrouped">'
            f'<h2>未分组 <span class="count">{len(ungrouped)} 篇</span></h2>'
            f'<div class="card-grid">{cards}</div>'
            f"</section>"
        )

    body = f"""
<div class="wrap">
  <div class="cat-hero" style="--cat-color:{cat["color"]}">
    <p class="kicker">{cat["id"]}</p>
    <h1>{htmlmod.escape(cat["name"])}</h1>
    <p>{htmlmod.escape(cat["blurb"])} 本类共 {len(group)} 篇。</p>
    <div class="cat-jump">{"".join(jump)}</div>
  </div>
  {"".join(blocks)}
</div>
"""
    return layout(cat["name"], body, 1, active="", description=cat["blurb"])


def build_map(cases):
    sections = []
    for cat in CATEGORIES:
        group = [c for c in cases if c["cat"]["id"] == cat["id"]]
        tiles = []
        for c in group:
            if c["cover"]:
                cover = f'<img src="{img_url(c["cover"], 0)}" alt="">'
            else:
                cover = '<div class="placeholder" style="width:100%;height:100%"></div>'
            tiles.append(
                f'<a class="map-tile" href="{case_url(c["slug"], 0)}" style="--cat-color:{cat["color"]}">'
                f'<div class="map-tile-cover">{cover}</div>'
                f'<div class="map-tile-title">{htmlmod.escape(c["title"])}</div>'
                f"</a>"
            )
        href = url("categories/" + cat["id"] + ".html", 0)
        sections.append(
            f'<section class="map-section" id="cat-{cat["id"]}" style="--cat-color:{cat["color"]}">'
            f'<div class="map-section-head">'
            f"<h2>{htmlmod.escape(cat['full'])}</h2>"
            f'<a class="section-more" href="{href}">{len(group)} 篇</a>'
            f"</div>"
            f'<div class="map-tiles">{"".join(tiles)}</div>'
            f"</section>"
        )
    jump = "".join(
        f'<a href="#cat-{c["id"]}">{htmlmod.escape(c["name"])}</a>' for c in CATEGORIES
    )
    body = f"""
<div class="wrap">
  <div class="map-intro">
    <h1>案例地图</h1>
    <p>按一级分类浏览全部 {len(cases)} 篇案例。点击封面或标题进入详情。</p>
    <div class="cat-jump">{jump}</div>
  </div>
  {"".join(sections)}
  <p style="height:40px"></p>
</div>
"""
    return layout("案例地图", body, 0, active="map")


def related_from_body(body, linker):
    found = []
    seen = set()
    m = re.search(r"^##\s+相关案例\s*$", body, re.M)
    chunk = body[m.start() :] if m else body
    nxt = re.search(r"^##\s+", chunk[3:], re.M)
    if nxt:
        chunk = chunk[: nxt.start() + 3]
    for wm in WIKILINK_RE.finditer(chunk):
        if wm.group(1):
            continue
        target, _ = split_wikilink(wm.group(2))
        case = linker.by_key.get(target)
        if case and case["slug"] not in seen:
            seen.add(case["slug"])
            found.append(case)
    return found


def build_case(c, linker, attach_used):
    depth = 1
    body_md = c["body"].lstrip()
    body_md = re.sub(r"^#\s+.+?(?:\n+|$)", "", body_md, count=1)
    html_body = md_to_html(body_md, linker, depth, attach_used)
    if c["cover"]:
        attach_used.add(c["cover"])
    hero = ""

    cat = c["cat"]
    crumbs = (
        f'<nav class="breadcrumb" aria-label="面包屑">'
        f'<a href="{url("index.html", depth)}">首页</a>'
        f'<span class="sep">/</span>'
        f'<a href="{url("categories/" + cat["id"] + ".html", depth)}">{htmlmod.escape(cat["name"])}</a>'
        f'<span class="sep">/</span>'
        f'<span>{htmlmod.escape(c["title"])}</span>'
        f"</nav>"
    )

    related = related_from_body(c["body"], linker)
    related_html = ""
    if related:
        items = "".join(
            f'<li><a href="{case_url(r["slug"], depth)}">{htmlmod.escape(r["title"])}</a></li>'
            for r in related
        )
        related_html = (
            f'<div class="panel"><h2>相关案例</h2><ul class="related-list">{items}</ul></div>'
        )

    if c["extra_sources"]:
        extras = "<ul>" + "".join(f"<li>{ext_link(x)}</li>" for x in c["extra_sources"]) + "</ul>"
    else:
        extras = "—"

    tags = c["tags"]
    if tags:
        tag_html = (
            '<div class="tag-list">'
            + "".join(f'<span class="chip">{htmlmod.escape(t)}</span>' for t in tags)
            + "</div>"
        )
    else:
        tag_html = "—"

    aside = f"""
<aside class="case-aside">
  <div class="panel">
    <h2>属性</h2>
    <dl class="prop-list">
      <div class="prop-item"><dt>一级分类</dt><dd><a href="{url("categories/" + cat["id"] + ".html", depth)}">{htmlmod.escape(cat["full"])}</a></dd></div>
      <div class="prop-item"><dt>二级分类</dt><dd>{list_or_dash(c["subs"])}</dd></div>
      <div class="prop-item"><dt>应用产品</dt><dd>{list_or_dash(c["products"])}</dd></div>
      <div class="prop-item"><dt>材料</dt><dd>{list_or_dash(c["materials"])}</dd></div>
      <div class="prop-item"><dt>工艺</dt><dd>{list_or_dash(c["process"])}</dd></div>
      <div class="prop-item"><dt>难度</dt><dd>{htmlmod.escape(c["difficulty"])}</dd></div>
      <div class="prop-item"><dt>评分</dt><dd>{stars_html(c["score"])} {c["score"]}/5</dd></div>
      <div class="prop-item"><dt>收录日期</dt><dd>{htmlmod.escape(c["date"] or "—")}</dd></div>
      <div class="prop-item"><dt>来源平台</dt><dd>{htmlmod.escape(c["platform"] or "—")}</dd></div>
      <div class="prop-item"><dt>来源链接</dt><dd>{ext_link(c["source"])}</dd></div>
      <div class="prop-item"><dt>补充来源</dt><dd>{extras}</dd></div>
      <div class="prop-item"><dt>核实状态</dt><dd>{htmlmod.escape(c["verified"] or "—")}</dd></div>
      <div class="prop-item"><dt>标签</dt><dd>{tag_html}</dd></div>
    </dl>
  </div>
  {related_html}
</aside>
"""

    main = f"""
{crumbs}
<div class="case-layout">
  <article>
    <header class="case-header">
      <h1>{htmlmod.escape(c["title"])}</h1>
      <p class="lede">{htmlmod.escape(c["summary"])}</p>
      <div class="meta-row">{chips_for_case(c)}</div>
    </header>
    <div class="article-body">
      {html_body}
    </div>
  </article>
  {aside}
</div>
"""
    has_mermaid = "```mermaid" in c["body"]
    return layout(
        c["title"],
        main,
        depth,
        description=c["summary"] or c["title"],
        mermaid=has_mermaid,
    )


def write_data_js(dest, cases):
    payload = []
    for c in cases:
        payload.append(
            {
                "slug": c["slug"],
                "title": c["title"],
                "summary": c["summary"],
                "catId": c["cat"]["id"],
                "catShort": c["cat"]["name"],
                "subs": c["subs"],
                "difficulty": c["difficulty"],
                "score": c["score"],
                "date": c["date"],
                "cover": img_url(c["cover"], 0) if c["cover"] else "",
                "href": case_url(c["slug"], 0),
                "tags": c["tags"],
                "products": c["products"],
                "materials": c["materials"],
                "process": c["process"],
                "negative": c["negative"],
            }
        )
    dest.write_text(
        "window.CASES = " + json.dumps(payload, ensure_ascii=False, indent=0) + ";\n",
        encoding="utf-8",
    )


def write_config(dest):
    tmpl = (TEMPLATES / "config.js").read_text(encoding="utf-8")
    dest.write_text(tmpl.replace("__SITE_BASE__", BASE), encoding="utf-8")


def copy_assets(attach_used):
    assets = DOCS / "assets"
    images = DOCS / "images"
    assets.mkdir(parents=True, exist_ok=True)
    images.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATES / "style.css", assets / "style.css")
    shutil.copy2(TEMPLATES / "app.js", assets / "app.js")
    write_config(assets / "config.js")
    (assets / "favicon.svg").write_text(FAVICON_SVG, encoding="utf-8")

    mermaid_src = TEMPLATES / "mermaid.min.js"
    alt = Path("/tmp/site-vendor/mermaid.min.js")
    if mermaid_src.exists():
        shutil.copy2(mermaid_src, assets / "mermaid.min.js")
    elif alt.exists():
        shutil.copy2(alt, assets / "mermaid.min.js")
    else:
        print("WARNING: mermaid.min.js not found; diagrams will not render offline")

    copied = 0
    if ATTACH_DIR.exists():
        for p in ATTACH_DIR.iterdir():
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}:
                shutil.copy2(p, images / p.name)
                copied += 1
    return copied


def reset_docs():
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")


def main():
    global BASE, DOCS
    parser = argparse.ArgumentParser(description="Build static site into docs/")
    parser.add_argument(
        "--base",
        default="",
        help="Absolute base path, e.g. /structure-case-library/ . Default empty = relative paths.",
    )
    parser.add_argument("--out", default=str(DOCS), help="Output directory")
    args = parser.parse_args()
    BASE = args.base or ""
    if BASE and not BASE.startswith("/"):
        BASE = "/" + BASE
    if BASE and not BASE.endswith("/"):
        BASE += "/"
    if Path(args.out).resolve() != DOCS:
        DOCS = Path(args.out).resolve()

    cases = load_cases()
    if not cases:
        raise SystemExit("No case notes found in vault/; refusing to build an empty site.")

    linker = Linker(cases)
    attach_used = set()

    reset_docs()
    n_img = copy_assets(attach_used)
    write_data_js(DOCS / "assets" / "data.js", cases)

    (DOCS / "index.html").write_text(build_home(cases), encoding="utf-8")
    (DOCS / "browse.html").write_text(build_browse(cases), encoding="utf-8")
    (DOCS / "map.html").write_text(build_map(cases), encoding="utf-8")

    cat_dir = DOCS / "categories"
    cat_dir.mkdir(exist_ok=True)
    for cat in CATEGORIES:
        (cat_dir / f"{cat['id']}.html").write_text(build_category(cat, cases), encoding="utf-8")

    case_dir = DOCS / "cases"
    case_dir.mkdir(exist_ok=True)
    for c in cases:
        html = build_case(c, linker, attach_used)
        (case_dir / f"{c['slug']}.html").write_text(html, encoding="utf-8")

    print(f"Built {len(cases)} case pages, 7 category pages, home/browse/map.")
    print(f"Copied {n_img} images into docs/images/.")
    print(f"Output: {DOCS}")
    print(f"BASE: {BASE!r} (empty means relative paths)")


if __name__ == "__main__":
    main()
