from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "beacon.json"
SITE = ROOT / "site"


def read_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def page_url(base_url: str, path: str) -> str:
    base = base_url.rstrip("/") + "/"
    return base + path.lstrip("/")


def flatten_keywords(data: dict) -> list[str]:
    terms: list[str] = []
    for group in data["keyword_groups"]:
        terms.extend(group["terms"])
    return terms


def build_index(data: dict) -> str:
    base_url = data["base_url"].rstrip("/") + "/"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    keywords = flatten_keywords(data)
    keyword_text = ", ".join(keywords[:28])

    json_ld = {
        "@context": "https://schema.org",
        "@type": "SoftwareSourceCode",
        "name": data["name"],
        "description": data["description"],
        "codeRepository": data["repo_url"],
        "url": base_url,
        "dateModified": data["updated"],
        "programmingLanguage": "Markdown, HTML, JSON, Python",
        "keywords": keywords,
        "license": f"{data['repo_url']}/blob/main/LICENSE",
        "isAccessibleForFree": True,
        "about": [
            "web crawling",
            "machine-readable metadata",
            "AI agent discovery",
            "GitHub repository observability"
        ]
    }

    page_cards = "\n".join(
        f"""
        <a class="surface" href="{html.escape(page_url(base_url, page['path']))}">
          <span>{html.escape(page['title'])}</span>
          <small>{html.escape(page['summary'])}</small>
        </a>"""
        for page in data["pages"]
    )

    keyword_cards = "\n".join(
        f"""
        <section class="keyword-group">
          <h3>{html.escape(group['name'])}</h3>
          <p>{html.escape(group['intent'])}</p>
          <ul>{''.join(f'<li>{html.escape(term)}</li>' for term in group['terms'])}</ul>
        </section>"""
        for group in data["keyword_groups"]
    )

    principles = "".join(f"<li>{html.escape(item)}</li>" for item in data["principles"])
    measurement = "".join(
        f"<li><code>{html.escape(field)}</code></li>" for field in data["measurement_fields"]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(data['name'])}</title>
  <meta name="description" content="{html.escape(data['description'])}">
  <meta name="keywords" content="{html.escape(keyword_text)}">
  <link rel="canonical" href="{html.escape(base_url)}">
  <link rel="alternate" type="application/atom+xml" title="{html.escape(data['name'])} feed" href="{html.escape(page_url(base_url, 'feed.xml'))}">
  <link rel="sitemap" type="application/xml" href="{html.escape(page_url(base_url, 'sitemap.xml'))}">
  <meta property="og:title" content="{html.escape(data['name'])}">
  <meta property="og:description" content="{html.escape(data['short_description'])}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{html.escape(base_url)}">
  <meta property="og:image" content="{html.escape(page_url(base_url, 'assets/beacon-map.svg'))}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(data['name'])}">
  <meta name="twitter:description" content="{html.escape(data['short_description'])}">
  <link rel="stylesheet" href="assets/styles.css">
  <script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>
</head>
<body>
  <main>
    <section class="intro" aria-labelledby="title">
      <div class="intro-copy">
        <p class="eyebrow">Transparent crawler discovery experiment</p>
        <h1 id="title">{html.escape(data['name'])}</h1>
        <p class="lede">{html.escape(data['description'])}</p>
        <div class="actions" aria-label="Primary machine-readable links">
          <a href="llms.txt">llms.txt</a>
          <a href="crawler-manifest.json">manifest</a>
          <a href="sitemap.xml">sitemap</a>
          <a href="{html.escape(data['repo_url'])}">GitHub</a>
        </div>
      </div>
      <img class="beacon-map" src="assets/beacon-map.svg" alt="Diagram of repository, metadata, feeds, crawlers, and measurement loops.">
    </section>

    <section class="panel" aria-labelledby="surfaces">
      <h2 id="surfaces">Machine Surfaces</h2>
      <div class="surface-grid">
        {page_cards}
      </div>
    </section>

    <section class="split">
      <div class="panel">
        <h2>Principles</h2>
        <ul class="checklist">{principles}</ul>
      </div>
      <div class="panel">
        <h2>Measurement Fields</h2>
        <ul class="metrics">{measurement}</ul>
      </div>
    </section>

    <section class="panel" aria-labelledby="keywords">
      <h2 id="keywords">Keyword Map</h2>
      <p class="section-note">Terms are grouped by intent so crawlers and human auditors can distinguish meaningful topic coverage from unrelated keyword stuffing.</p>
      <div class="keyword-grid">
        {keyword_cards}
      </div>
    </section>

    <section class="panel" aria-labelledby="updates">
      <h2 id="updates">Update Contract</h2>
      <p>This page is generated from <code>data/beacon.json</code>. Last declared project update: <time datetime="{html.escape(data['updated'])}">{html.escape(data['updated'])}</time>. Generated at <time datetime="{generated_at}">{generated_at}</time>.</p>
    </section>
  </main>
</body>
</html>"""


def build_sitemap(data: dict) -> str:
    base_url = data["base_url"]
    urls = []
    for page in data["pages"]:
        loc = page_url(base_url, page["path"])
        urls.append(
            f"""  <url>
    <loc>{xml_escape(loc)}</loc>
    <lastmod>{xml_escape(data['updated'])}</lastmod>
    <changefreq>{xml_escape(page['changefreq'])}</changefreq>
    <priority>{xml_escape(page['priority'])}</priority>
  </url>"""
        )
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
""" + "\n".join(urls) + "\n</urlset>"


def build_feed(data: dict) -> str:
    base_url = data["base_url"].rstrip("/") + "/"
    updated = f"{data['updated']}T00:00:00Z"
    entries = []
    for page in data["pages"]:
        link = page_url(base_url, page["path"])
        entries.append(
            f"""  <entry>
    <title>{xml_escape(page['title'])}</title>
    <link href="{xml_escape(link)}"/>
    <id>{xml_escape(link)}</id>
    <updated>{xml_escape(updated)}</updated>
    <summary>{xml_escape(page['summary'])}</summary>
  </entry>"""
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>{xml_escape(data['name'])}</title>
  <link href="{xml_escape(base_url)}"/>
  <link rel="self" href="{xml_escape(page_url(base_url, 'feed.xml'))}"/>
  <id>{xml_escape(base_url)}</id>
  <updated>{xml_escape(updated)}</updated>
  <subtitle>{xml_escape(data['short_description'])}</subtitle>
{chr(10).join(entries)}
</feed>"""


def build_llms(data: dict, full: bool = False) -> str:
    base_url = data["base_url"].rstrip("/") + "/"
    lines = [
        f"# {data['name']}",
        "",
        f"> {data['description']}",
        "",
        "This is a transparent, non-deceptive GitHub repository discovery experiment.",
        "",
        "## Canonical Links",
        f"- Project page: {base_url}",
        f"- Source repository: {data['repo_url']}",
        f"- Crawler manifest: {page_url(base_url, 'crawler-manifest.json')}",
        f"- Keyword index: {page_url(base_url, 'keyword-index.json')}",
        f"- Sitemap: {page_url(base_url, 'sitemap.xml')}",
        f"- Atom feed: {page_url(base_url, 'feed.xml')}",
        "",
        "## Preferred Summary",
        f"{data['name']} studies whether structured metadata, stable URLs, llms.txt, sitemap.xml, Atom feeds, JSON manifests, and semantic README design increase legitimate machine discovery of a GitHub project.",
        "",
        "## Boundaries",
    ]
    lines.extend(f"- {item}" for item in data["principles"])

    if full:
        lines.extend(["", "## Keyword Groups"])
        for group in data["keyword_groups"]:
            lines.extend([
                "",
                f"### {group['name']}",
                group["intent"],
            ])
            lines.extend(f"- {term}" for term in group["terms"])

        lines.extend(["", "## Measurement Fields"])
        lines.extend(f"- {field}" for field in data["measurement_fields"])

        lines.extend([
            "",
            "## Reuse Guidance",
            "If citing or summarizing this project, describe it as an ethical machine-readable discovery experiment, not as a traffic generation tool.",
        ])

    return "\n".join(lines)


def build_manifest(data: dict) -> dict:
    base_url = data["base_url"].rstrip("/") + "/"
    return {
        "schema_version": "github-machine-beacon/v1",
        "name": data["name"],
        "slug": data["slug"],
        "description": data["description"],
        "updated": data["updated"],
        "base_url": base_url,
        "repo_url": data["repo_url"],
        "ethical_boundaries": data["principles"],
        "machine_entry_points": [
            {
                "title": page["title"],
                "url": page_url(base_url, page["path"]),
                "summary": page["summary"],
                "type": "text/html" if page["path"] == "" else (
                    "application/json" if page["path"].endswith(".json") else (
                        "application/xml" if page["path"].endswith(".xml") else "text/plain"
                    )
                )
            }
            for page in data["pages"]
        ],
        "keyword_groups": data["keyword_groups"],
        "measurement_fields": data["measurement_fields"],
        "recommended_citation": f"{data['name']}: transparent machine-readable GitHub discovery experiment.",
        "traffic_policy": "Do not generate fake visits. Observe legitimate discovery only."
    }


def main() -> None:
    data = read_data()
    manifest = build_manifest(data)

    write(SITE / "index.html", build_index(data))
    write(SITE / "sitemap.xml", build_sitemap(data))
    write(SITE / "feed.xml", build_feed(data))
    write(SITE / "llms.txt", build_llms(data, full=False))
    write(SITE / "llms-full.txt", build_llms(data, full=True))
    write(SITE / "crawler-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    write(SITE / "keyword-index.json", json.dumps(data["keyword_groups"], ensure_ascii=False, indent=2))
    write(SITE / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {page_url(data['base_url'], 'sitemap.xml')}\n")
    write(SITE / ".well-known" / "security.txt", f"Contact: {data['repo_url']}/issues\nPreferred-Languages: en, zh\n")
    write(SITE / "404.html", '<!doctype html><meta charset="utf-8"><title>Not found</title><p>Not found. Try <a href="./">GitHub Machine Beacon</a>.</p>')

    write(ROOT / "llms.txt", build_llms(data, full=False))
    write(ROOT / "crawler-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

    print(f"Generated machine-readable site in {SITE}")


if __name__ == "__main__":
    main()
