from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PLACEHOLDERS = ("YOUR_" "GITHUB_USERNAME", "example.org/" "schemas")


class RefParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value for key, value in attrs if value}
        for attr in ("href", "src"):
            if attr in attr_map:
                self.refs.append((tag, attr, attr_map[attr]))


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def check_json(path: Path) -> None:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path} is not valid JSON: {exc}")


def check_xml(path: Path) -> None:
    try:
        ET.parse(path)
    except Exception as exc:
        fail(f"{path} is not valid XML: {exc}")


def check_placeholders() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for placeholder in PLACEHOLDERS:
            if placeholder in text:
                fail(f"{path} contains placeholder {placeholder}")


def check_html_refs() -> None:
    for html_path in SITE.glob("*.html"):
        parser = RefParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        for _tag, _attr, ref in parser.refs:
            parsed = urlparse(ref)
            if parsed.scheme or ref.startswith("#") or ref.startswith("mailto:"):
                continue
            target = (html_path.parent / parsed.path).resolve()
            if not target.exists():
                fail(f"{html_path} references missing local file {ref}")


def check_sitemap_urls() -> None:
    data = json.loads((ROOT / "data" / "beacon.json").read_text(encoding="utf-8"))
    sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
    required = [
        data["base_url"],
        data["base_url"].rstrip("/") + "/llms.txt",
        data["base_url"].rstrip("/") + "/crawler-manifest.json",
        data["base_url"].rstrip("/") + "/resources.json",
        data["base_url"].rstrip("/") + "/traffic.json",
        data["base_url"].rstrip("/") + "/machine-readable-repository-checklist.html",
    ]
    for url in required:
        if url not in sitemap:
            fail(f"sitemap.xml is missing {url}")


def check_llms_links() -> None:
    text = (SITE / "llms.txt").read_text(encoding="utf-8")
    for required in ("crawler-manifest.json", "resources.json", "traffic.json", "sitemap.xml", "feed.xml"):
        if required not in text:
            fail(f"llms.txt is missing {required}")
    if not (SITE / ".nojekyll").exists():
        fail("site/.nojekyll is missing; GitHub Pages may omit .well-known files")
    if not (SITE / "assets" / "traffic-card.svg").exists():
        fail("site/assets/traffic-card.svg is missing")


def check_schema_json_ld() -> None:
    for html_path in SITE.glob("*.html"):
        if html_path.name == "404.html":
            continue
        text = html_path.read_text(encoding="utf-8")
        matches = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            text,
            flags=re.DOTALL,
        )
        if not matches:
            fail(f"{html_path} has no JSON-LD block")
        for match in matches:
            json.loads(match)


def main() -> None:
    for path in [
        ROOT / "data" / "beacon.json",
        ROOT / "data" / "content-pages.json",
        ROOT / "crawler-manifest.json",
        ROOT / "keyword-index.json",
        ROOT / "resources.json",
        ROOT / "traffic.json",
        SITE / "crawler-manifest.json",
        SITE / "keyword-index.json",
        SITE / "resources.json",
        SITE / "traffic.json",
        SITE / "manifest.webmanifest",
    ]:
        check_json(path)
    for path in [SITE / "sitemap.xml", SITE / "feed.xml"]:
        check_xml(path)
    check_placeholders()
    check_html_refs()
    check_sitemap_urls()
    check_llms_links()
    check_schema_json_ld()
    print("validation_ok")


if __name__ == "__main__":
    main()
