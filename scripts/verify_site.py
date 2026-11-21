#!/usr/bin/env python3
"""核对 docs/ 静态站点：案例页数量、站内死链、图片路径。"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
VAULT = ROOT / "vault"

SKIP_PREFIXES = ("http://", "https://", "mailto:", "data:", "javascript:")


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.srcs = []
        self.ids = set()
        self.title = ""
        self.in_title = False
        self.imgs_missing_src = 0

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        if tag == "title":
            self.in_title = True
        if "id" in ad and ad["id"]:
            self.ids.add(ad["id"])
        if tag == "a" and "href" in ad:
            self.hrefs.append(ad["href"])
        if tag in {"img", "script", "source"} and "src" in ad:
            self.srcs.append((tag, ad["src"]))
        if tag == "link" and ad.get("href"):
            self.hrefs.append(ad["href"])
        if tag == "img" and not ad.get("src"):
            self.imgs_missing_src += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def is_external(href: str) -> bool:
    if href is None:
        return True
    href = href.strip()
    if href.startswith("#"):
        return False
    return href.startswith(SKIP_PREFIXES)


def resolve(src: Path, href: str) -> Path | None:
    href = href.strip()
    if not href or is_external(href):
        return None
    # strip query/hash
    parsed = urlparse(href)
    path = unquote(parsed.path)
    if not path:
        return src  # hash-only, same file
    if path.startswith("/"):
        # absolute from site root: try docs-relative
        # if it starts with a known prefix we don't have the repo root;
        # treat as docs-relative by stripping a possible repo base
        for base in ("/structure-case-library/", "/"):
            if path.startswith(base) and base != "/":
                path = path[len(base) :]
                break
        else:
            # leading slash without known base — not a local relative link
            return Path("/__abs__") / path.lstrip("/")
    return (src.parent / path).resolve()


def main() -> int:
    if not DOCS.exists():
        print("docs/ 不存在，请先运行 python3 scripts/build_site.py")
        return 1

    html_files = sorted(DOCS.rglob("*.html"))
    case_pages = sorted((DOCS / "cases").glob("*.html")) if (DOCS / "cases").exists() else []

    vault_cases = []
    for p in VAULT.glob("0[1-7]-*/*.md"):
        if "索引" not in p.name:
            vault_cases.append(p.stem)

    print(f"HTML pages: {len(html_files)}")
    print(f"Case pages: {len(case_pages)}")
    print(f"Vault cases: {len(vault_cases)}")

    missing_pages = []
    for stem in vault_cases:
        if not (DOCS / "cases" / f"{stem}.html").exists():
            missing_pages.append(stem)

    extra_pages = []
    case_stems = {p.stem for p in case_pages}
    for stem in sorted(case_stems):
        if stem not in set(vault_cases):
            extra_pages.append(stem)

    dead = []
    missing_imgs = []
    missing_assets = []
    hash_miss = []
    empty_title = []
    no_article = []
    broken_abs = []

    for fp in html_files:
        raw = fp.read_text(encoding="utf-8", errors="replace")
        parser = LinkParser()
        try:
            parser.feed(raw)
        except Exception as e:
            dead.append((fp, f"(parse error: {e})", None))
            continue
        if not parser.title.strip():
            empty_title.append(fp)
        if fp.parent.name == "cases":
            if 'class="article-body"' not in raw or "<h1>" not in raw:
                no_article.append(fp)

        for href in parser.hrefs:
            if is_external(href) or href.startswith("mailto:"):
                continue
            parsed = urlparse(href)
            path_part = parsed.path
            if not path_part and parsed.fragment:
                if parsed.fragment not in parser.ids:
                    # might be generated / url-encoded
                    frag = unquote(parsed.fragment)
                    if frag not in parser.ids:
                        hash_miss.append((fp, href))
                continue
            dest = resolve(fp, href)
            if dest is None:
                continue
            if str(dest).startswith("/__abs__"):
                broken_abs.append((fp, href))
                continue
            # file may be a directory index
            if dest.is_dir():
                if not (dest / "index.html").exists():
                    dead.append((fp, href, dest))
                continue
            if not dest.exists():
                dead.append((fp, href, dest))
            elif parsed.fragment:
                # check id in dest
                try:
                    t = dest.read_text(encoding="utf-8", errors="replace")
                    if f'id="{parsed.fragment}"' not in t and f"id='{parsed.fragment}'" not in t:
                        frag = unquote(parsed.fragment)
                        if f'id="{frag}"' not in t:
                            hash_miss.append((fp, href))
                except Exception:
                    pass

        for tag, src in parser.srcs:
            if is_external(src):
                continue
            dest = resolve(fp, src)
            if dest is None:
                continue
            if str(dest).startswith("/__abs__") or not dest.exists():
                if tag == "img":
                    missing_imgs.append((fp, src))
                else:
                    missing_assets.append((fp, src))

    print("\n--- Results ---")
    print(f"Case page count == vault count: {len(case_pages) == len(vault_cases)} ({len(case_pages)}/{len(vault_cases)})")
    print(f"Missing case pages: {len(missing_pages)}")
    for s in missing_pages:
        print(f"  MISSING {s}")
    print(f"Extra case pages: {len(extra_pages)}")
    print(f"Internal dead links: {len(dead)}")
    for fp, href, dest in dead[:40]:
        print(f"  DEAD  {fp.relative_to(DOCS)}  ->  {href}")
    if len(dead) > 40:
        print(f"  ... {len(dead) - 40} more")
    print(f"Missing images: {len(missing_imgs)}")
    for fp, src in missing_imgs[:30]:
        print(f"  IMG   {fp.relative_to(DOCS)}  ->  {src}")
    print(f"Missing other assets: {len(missing_assets)}")
    for fp, src in missing_assets[:20]:
        print(f"  ASSET {fp.relative_to(DOCS)}  ->  {src}")
    print(f"Broken absolute-root links: {len(broken_abs)}")
    for fp, href in broken_abs[:20]:
        print(f"  ABS   {fp.relative_to(DOCS)}  ->  {href}")
    print(f"Hash targets missing (may be ignorable): {len(hash_miss)}")
    print(f"Empty titles: {len(empty_title)}")
    print(f"Case pages missing article/h1: {len(no_article)}")

    # size
    def du(path: Path) -> int:
        return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())

    total = du(DOCS)
    imgs = du(DOCS / "images") if (DOCS / "images").exists() else 0
    n_imgs = len(list((DOCS / "images").glob("*"))) if (DOCS / "images").exists() else 0
    print(f"\nImages: {n_imgs}")
    print(f"docs/images size: {imgs / (1024*1024):.1f} MB")
    print(f"docs/ total size: {total / (1024*1024):.1f} MB")

    ok = (
        len(case_pages) == len(vault_cases)
        and bool(vault_cases)
        and not extra_pages
        and not missing_pages
        and not dead
        and not missing_imgs
        and not missing_assets
        and not no_article
        and not empty_title
        and not broken_abs
    )
    print("\nPASS" if ok else "\nFAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
