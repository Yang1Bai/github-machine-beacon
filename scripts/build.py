from __future__ import annotations

import html
import json
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "beacon.json"
CONTENT_PATH = ROOT / "data" / "content-pages.json"
TRAFFIC_PATH = ROOT / "data" / "traffic.json"
SITE = ROOT / "site"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_data() -> tuple[dict, list[dict], dict]:
    return read_json(DATA_PATH), read_json(CONTENT_PATH), read_json(TRAFFIC_PATH)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def page_url(base_url: str, path: str) -> str:
    base = base_url.rstrip("/") + "/"
    return base + path.lstrip("/")


def media_type(path: str) -> str:
    if path == "" or path.endswith(".html"):
        return "text/html"
    if path.endswith(".json"):
        return "application/json"
    if path.endswith(".xml"):
        return "application/xml"
    if path.endswith(".webmanifest"):
        return "application/manifest+json"
    return "text/plain"


def all_pages(data: dict, content_pages: list[dict]) -> list[dict]:
    return data["pages"] + [
        {
            "path": page["path"],
            "title": page["title"],
            "summary": page["summary"],
            "priority": page["priority"],
            "changefreq": page["changefreq"],
            "keywords": page.get("keywords", []),
        }
        for page in content_pages
    ]


def flatten_keywords(data: dict, content_pages: list[dict]) -> list[str]:
    terms: list[str] = []
    for group in data["keyword_groups"]:
        terms.extend(group["terms"])
    for page in content_pages:
        terms.extend(page.get("keywords", []))

    seen: set[str] = set()
    unique_terms: list[str] = []
    for term in terms:
        key = term.lower()
        if key not in seen:
            seen.add(key)
            unique_terms.append(term)
    return unique_terms


def json_script(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def format_count(value: int | None) -> str:
    if value is None:
        return "N/A"
    return f"{int(value):,}"


def build_traffic_card_svg(data: dict, traffic: dict) -> str:
    edge_url = data.get("edge_url", data["base_url"])
    edge_card_url = edge_url.rstrip("/") + "/traffic-card.svg"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 430" role="img" aria-labelledby="title desc">
  <title id="title">Live traffic card for {html.escape(data['name'])}</title>
  <desc id="desc">Pointer to the dynamic Cloudflare traffic card for live machine and human request counts.</desc>
  <rect width="1200" height="430" rx="18" fill="#fbfcf8"/>
  <rect x="24" y="24" width="1152" height="382" rx="14" fill="#ffffff" stroke="#d9e2dc" stroke-width="2"/>
  <text x="64" y="82" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="24" font-weight="800" fill="#0d7f61">LIVE TRAFFIC CARD MOVED TO CLOUDFLARE</text>
  <text x="64" y="206" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="96" font-weight="850" fill="#2357d9">EDGE LIVE</text>
  <text x="72" y="250" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="28" fill="#5c6b63">Use the dynamic Worker SVG for current request totals and machine/human split.</text>
  <g font-family="Inter, Segoe UI, Arial, sans-serif">
    <rect x="640" y="74" width="220" height="112" rx="10" fill="#f8faf7" stroke="#d9e2dc"/>
    <text x="662" y="116" font-size="22" font-weight="700" fill="#5c6b63">Machine visits</text>
    <text x="662" y="166" font-size="42" font-weight="850" fill="#17211c">LIVE</text>
    <rect x="890" y="74" width="220" height="112" rx="10" fill="#f8faf7" stroke="#d9e2dc"/>
    <text x="912" y="116" font-size="22" font-weight="700" fill="#5c6b63">Human visits</text>
    <text x="912" y="166" font-size="42" font-weight="850" fill="#17211c">LIVE</text>
    <rect x="640" y="214" width="220" height="112" rx="10" fill="#f8faf7" stroke="#d9e2dc"/>
    <text x="662" y="256" font-size="22" font-weight="700" fill="#5c6b63">Total requests</text>
    <text x="662" y="306" font-size="42" font-weight="850" fill="#17211c">LIVE</text>
    <rect x="890" y="214" width="220" height="112" rx="10" fill="#f8faf7" stroke="#d9e2dc"/>
    <text x="912" y="256" font-size="22" font-weight="700" fill="#5c6b63">Source</text>
    <text x="912" y="306" font-size="42" font-weight="850" fill="#17211c">WORKER</text>
  </g>
  <text x="64" y="352" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="22" fill="#5c6b63">Dynamic SVG: {html.escape(edge_card_url)}</text>
  <text x="64" y="386" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="22" font-weight="750" fill="#17211c">Open live homepage: {html.escape(edge_url)}</text>
</svg>"""


def render_head(
    data: dict,
    title: str,
    description: str,
    canonical_url: str,
    json_ld: dict,
    keywords: list[str] | None = None,
) -> str:
    base_url = data["base_url"].rstrip("/") + "/"
    keyword_meta = ""
    if keywords:
        keyword_meta = f'\n  <meta name="keywords" content="{html.escape(", ".join(keywords[:40]))}">'
    return f"""<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">{keyword_meta}
  <link rel="canonical" href="{html.escape(canonical_url)}">
  <link rel="alternate" type="application/atom+xml" title="{html.escape(data['name'])} feed" href="{html.escape(page_url(base_url, 'feed.xml'))}">
  <link rel="sitemap" type="application/xml" href="{html.escape(page_url(base_url, 'sitemap.xml'))}">
  <link rel="manifest" href="{html.escape(page_url(base_url, 'manifest.webmanifest'))}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{html.escape(canonical_url)}">
  <meta property="og:image" content="{html.escape(page_url(base_url, 'assets/beacon-map.svg'))}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title)}">
  <meta name="twitter:description" content="{html.escape(description)}">
  <link rel="stylesheet" href="assets/styles.css">
  <script type="application/ld+json">{json_script(json_ld)}</script>
</head>"""


def render_nav(data: dict) -> str:
    return f"""<nav class="topbar" aria-label="Primary">
  <a class="brand" href="./">{html.escape(data['name'])}</a>
  <a href="llms.txt">llms.txt</a>
  <a href="crawler-manifest.json">manifest</a>
  <a href="traffic.json">traffic</a>
  <a href="sitemap.xml">sitemap</a>
  <a href="{html.escape(data['repo_url'])}">GitHub</a>
</nav>"""


def render_table(table: dict) -> str:
    headers = "".join(f"<th>{html.escape(header)}</th>" for header in table["headers"])
    rows = []
    for row in table["rows"]:
        cells = "".join(f"<td>{html.escape(str(cell))}</td>" for cell in row)
        rows.append(f"<tr>{cells}</tr>")
    return f"""<div class="table-wrap">
  <table>
    <thead><tr>{headers}</tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</div>"""


def render_section(section: dict) -> str:
    parts = [f"<section class=\"article-section\"><h2>{html.escape(section['heading'])}</h2>"]
    for paragraph in section.get("body", []):
        parts.append(f"<p>{html.escape(paragraph)}</p>")
    if "items" in section:
        items = "".join(f"<li>{html.escape(item)}</li>" for item in section["items"])
        parts.append(f"<ul class=\"checklist\">{items}</ul>")
    if "table" in section:
        parts.append(render_table(section["table"]))
    parts.append("</section>")
    return "\n".join(parts)


def build_index(data: dict, content_pages: list[dict], traffic: dict) -> str:
    base_url = data["base_url"].rstrip("/") + "/"
    keywords = flatten_keywords(data, content_pages)
    pages = all_pages(data, content_pages)
    views = traffic.get("views", {})
    clones = traffic.get("clones", {})
    edge_traffic_url = data.get("edge_traffic_url", page_url(base_url, "traffic.json"))

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "name": data["name"],
                "url": base_url,
                "description": data["description"],
                "dateModified": data["updated"],
                "inLanguage": data["language"],
            },
            {
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
                    "GitHub repository observability",
                ],
            },
        ],
    }

    machine_cards = "\n".join(
        f"""
        <a class="surface" href="{html.escape(page_url(base_url, page['path']))}">
          <span>{html.escape(page['title'])}</span>
          <small>{html.escape(page['summary'])}</small>
        </a>"""
        for page in data["pages"]
    )
    resource_cards = "\n".join(
        f"""
        <a class="surface" href="{html.escape(page_url(base_url, page['path']))}">
          <span>{html.escape(page['title'])}</span>
          <small>{html.escape(page['summary'])}</small>
        </a>"""
        for page in content_pages
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
{render_head(data, data['name'], data['description'], base_url, json_ld, keywords)}
<body>
  {render_nav(data)}
  <main>
    <section class="intro" aria-labelledby="title">
      <div class="intro-copy">
        <p class="eyebrow">Transparent crawler discovery experiment</p>
        <h1 id="title">{html.escape(data['name'])}</h1>
        <p class="lede">{html.escape(data['description'])}</p>
        <div class="stats" aria-label="Project scope">
          <span><strong>{len(pages)}</strong> indexed resources</span>
          <span><strong>{len(content_pages)}</strong> reusable guides</span>
          <span><strong>{len(keywords)}</strong> mapped terms</span>
        </div>
        <div class="actions" aria-label="Primary machine-readable links">
          <a href="{html.escape(data.get('edge_url', base_url))}">Cloudflare live</a>
          <a href="llms.txt">llms.txt</a>
          <a href="crawler-manifest.json">manifest</a>
          <a href="traffic.json">traffic</a>
          <a href="sitemap.xml">sitemap</a>
          <a href="{html.escape(data['repo_url'])}">GitHub</a>
        </div>
      </div>
      <img class="beacon-map" src="assets/beacon-map.svg" alt="Diagram of repository, metadata, feeds, crawlers, and measurement loops.">
    </section>

    <section class="traffic-panel" aria-labelledby="traffic">
      <div>
        <p class="eyebrow">Live edge traffic</p>
        <h2 id="traffic">...</h2>
        <p class="traffic-caption">Cloudflare requests through the live homepage and machine-readable endpoints.</p>
      </div>
      <div class="traffic-grid" aria-label="Traffic breakdown">
        <div class="traffic-card">
          <span>Machine visits</span>
          <strong id="edge-machine">...</strong>
        </div>
        <div class="traffic-card">
          <span>Human visits</span>
          <strong id="edge-human">...</strong>
        </div>
        <div class="traffic-card">
          <span>Unknown</span>
          <strong id="edge-unknown">...</strong>
        </div>
        <div class="traffic-card">
          <span>GitHub views</span>
          <strong>{format_count(views.get('count', 0))}</strong>
        </div>
      </div>
      <p class="traffic-note">Live split updated <time id="traffic-updated" datetime="">loading</time>. Source: Cloudflare Worker. GitHub official snapshot: {format_count(views.get('count', 0))} views, {format_count(views.get('uniques', 0))} unique visitors, {format_count(clones.get('count', 0))} clones. Raw edge data: <a href="{html.escape(edge_traffic_url)}">cloudflare-traffic.json</a>.</p>
    </section>

    <section class="panel" aria-labelledby="resources">
      <h2 id="resources">Resource Library</h2>
      <p class="section-note">These pages are designed to be useful enough for humans to cite and structured enough for machines to parse.</p>
      <div class="surface-grid">
        {resource_cards}
      </div>
    </section>

    <section class="panel" aria-labelledby="surfaces">
      <h2 id="surfaces">Machine Surfaces</h2>
      <div class="surface-grid">
        {machine_cards}
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
      <p>This page is generated from <code>data/beacon.json</code> and <code>data/content-pages.json</code>. Declared project version: <code>{html.escape(data['version'])}</code>. Last declared update: <time datetime="{html.escape(data['updated'])}">{html.escape(data['updated'])}</time>.</p>
    </section>
  </main>
  <script>
    (() => {{
      const endpoint = {json.dumps(edge_traffic_url)};
      const formatter = new Intl.NumberFormat("en-US");
      const setText = (id, value) => {{
        const element = document.getElementById(id);
        if (element) element.textContent = formatter.format(Number(value || 0));
      }};

      fetch(endpoint, {{ cache: "no-store" }})
        .then((response) => {{
          if (!response.ok) throw new Error(`traffic endpoint returned ${{response.status}}`);
          return response.json();
        }})
        .then((snapshot) => {{
          const totals = snapshot.totals || {{}};
          setText("traffic", totals.requests);
          setText("edge-machine", totals.machine);
          setText("edge-human", totals.human);
          setText("edge-unknown", totals.unknown);
          const updated = document.getElementById("traffic-updated");
          if (updated && snapshot.updated_at) {{
            updated.textContent = snapshot.updated_at;
            updated.setAttribute("datetime", snapshot.updated_at);
          }}
        }})
        .catch(() => {{
          setText("traffic", 0);
          setText("edge-machine", 0);
          setText("edge-human", 0);
          setText("edge-unknown", 0);
          const updated = document.getElementById("traffic-updated");
          if (updated) updated.textContent = "edge endpoint unavailable";
        }});
    }})();
  </script>
</body>
</html>"""


def build_content_page(data: dict, page: dict) -> str:
    base_url = data["base_url"].rstrip("/") + "/"
    canonical = page_url(base_url, page["path"])
    json_ld = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": page["title"],
        "description": page["summary"],
        "url": canonical,
        "dateModified": data["updated"],
        "inLanguage": data["language"],
        "keywords": page.get("keywords", []),
        "isPartOf": {
            "@type": "WebSite",
            "name": data["name"],
            "url": base_url,
        },
        "publisher": {
            "@type": "Organization",
            "name": data["owner"],
            "url": f"https://github.com/{data['owner']}",
        },
    }
    sections = "\n".join(render_section(section) for section in page["sections"])
    keywords = "".join(f"<li>{html.escape(term)}</li>" for term in page.get("keywords", []))

    return f"""<!doctype html>
<html lang="en">
{render_head(data, f"{page['title']} | {data['name']}", page['summary'], canonical, json_ld, page.get('keywords', []))}
<body>
  {render_nav(data)}
  <main class="article-main">
    <article class="article" aria-labelledby="title">
      <p class="eyebrow">GitHub Machine Beacon resource</p>
      <h1 id="title">{html.escape(page['title'])}</h1>
      <p class="lede">{html.escape(page['summary'])}</p>
      {sections}
      <section class="article-section">
        <h2>Page Keywords</h2>
        <ul class="metrics">{keywords}</ul>
      </section>
    </article>
  </main>
</body>
</html>"""


def build_sitemap(data: dict, content_pages: list[dict]) -> str:
    urls = []
    for page in all_pages(data, content_pages):
        loc = page_url(data["base_url"], page["path"])
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


def build_feed(data: dict, content_pages: list[dict]) -> str:
    base_url = data["base_url"].rstrip("/") + "/"
    updated = f"{data['updated']}T00:00:00Z"
    entries = []
    for page in all_pages(data, content_pages):
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


def build_llms(data: dict, content_pages: list[dict], full: bool = False) -> str:
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
        f"- Resource index: {page_url(base_url, 'resources.json')}",
        f"- Traffic snapshot: {page_url(base_url, 'traffic.json')}",
        f"- Keyword index: {page_url(base_url, 'keyword-index.json')}",
        f"- Sitemap: {page_url(base_url, 'sitemap.xml')}",
        f"- Atom feed: {page_url(base_url, 'feed.xml')}",
        "",
        "## Preferred Summary",
        f"{data['name']} studies whether structured metadata, stable URLs, llms.txt, sitemap.xml, Atom feeds, JSON manifests, resource pages, and semantic README design increase legitimate machine discovery of a GitHub project.",
        "",
        "## Preferred Crawl Order",
        "1. Read crawler-manifest.json for canonical metadata.",
        "2. Read this llms.txt file for the compact agent summary.",
        "3. Read resources.json to choose deeper pages.",
        "4. Read traffic.json for the latest public GitHub Traffic API snapshot.",
        "5. Read the sitemap for the complete URL set.",
        "6. Read feed.xml for meaningful updates.",
        "",
        "## Resource Library",
    ]
    lines.extend(f"- [{page['title']}]({page_url(base_url, page['path'])}): {page['summary']}" for page in content_pages)

    lines.extend(["", "## Boundaries"])
    lines.extend(f"- {item}" for item in data["principles"])

    if full:
        lines.extend(["", "## Keyword Groups"])
        for group in data["keyword_groups"]:
            lines.extend(["", f"### {group['name']}", group["intent"]])
            lines.extend(f"- {term}" for term in group["terms"])

        lines.extend(["", "## Measurement Fields"])
        lines.extend(f"- {field}" for field in data["measurement_fields"])

        lines.extend(["", "## Page Summaries"])
        for page in content_pages:
            lines.extend(["", f"### {page['title']}", page["summary"]])
            for section in page["sections"]:
                lines.append(f"- {section['heading']}")

        lines.extend([
            "",
            "## Reuse Guidance",
            "If citing or summarizing this project, describe it as an ethical machine-readable discovery experiment, not as a traffic generation tool.",
        ])

    return "\n".join(lines)


def build_manifest(data: dict, content_pages: list[dict], traffic: dict) -> dict:
    base_url = data["base_url"].rstrip("/") + "/"
    return {
        "schema_version": "github-machine-beacon/v2",
        "name": data["name"],
        "slug": data["slug"],
        "version": data["version"],
        "description": data["description"],
        "updated": data["updated"],
        "base_url": base_url,
        "repo_url": data["repo_url"],
        "owner": data["owner"],
        "ethical_boundaries": data["principles"],
        "machine_entry_points": [
            {
                "title": page["title"],
                "url": page_url(base_url, page["path"]),
                "summary": page["summary"],
                "type": media_type(page["path"]),
                "changefreq": page["changefreq"],
                "priority": page["priority"],
            }
            for page in all_pages(data, content_pages)
        ],
        "content_resources": [
            {
                "title": page["title"],
                "url": page_url(base_url, page["path"]),
                "summary": page["summary"],
                "keywords": page.get("keywords", []),
            }
            for page in content_pages
        ],
        "keyword_groups": data["keyword_groups"],
        "measurement_fields": data["measurement_fields"],
        "traffic_snapshot": {
            "url": page_url(base_url, "traffic.json"),
            "updated_at": traffic.get("updated_at"),
            "source": traffic.get("source"),
            "views": traffic.get("views", {}),
            "visitor_classification": traffic.get("visitor_classification", {}),
        },
        "cloudflare_edge": {
            "url": data.get("edge_url"),
            "traffic_url": data.get("edge_traffic_url"),
            "classification": "machine/human split via Worker request-header heuristic",
        },
        "recommended_citation": f"{data['name']}: transparent machine-readable GitHub discovery experiment.",
        "traffic_policy": "Do not generate fake visits. Observe legitimate discovery only.",
        "validation": {
            "json_parseable": True,
            "xml_parseable": True,
            "local_links_checked": True,
            "placeholder_usernames_removed": True,
        },
    }


def build_resources_json(data: dict, content_pages: list[dict]) -> dict:
    base_url = data["base_url"].rstrip("/") + "/"
    return {
        "name": data["name"],
        "updated": data["updated"],
        "version": data["version"],
        "resources": [
            {
                "title": page["title"],
                "url": page_url(base_url, page["path"]),
                "summary": page["summary"],
                "media_type": media_type(page["path"]),
                "keywords": page.get("keywords", []),
            }
            for page in all_pages(data, content_pages)
        ],
    }


def build_keyword_index(data: dict, content_pages: list[dict]) -> dict:
    base_url = data["base_url"].rstrip("/") + "/"
    return {
        "name": data["name"],
        "updated": data["updated"],
        "keyword_groups": data["keyword_groups"],
        "page_keywords": [
            {
                "title": page["title"],
                "url": page_url(base_url, page["path"]),
                "keywords": page.get("keywords", []),
            }
            for page in content_pages
        ],
    }


def build_webmanifest(data: dict) -> dict:
    return {
        "name": data["name"],
        "short_name": "Machine Beacon",
        "description": data["description"],
        "start_url": data["base_url"],
        "scope": data["base_url"],
        "display": "minimal-ui",
        "background_color": "#fbfcf8",
        "theme_color": "#17211c",
    }


def build_markdown_page(data: dict, page: dict) -> str:
    lines = [
        f"# {page['title']}",
        "",
        page["summary"],
        "",
        f"Canonical page: {page_url(data['base_url'], page['path'])}",
        "",
    ]
    for section in page["sections"]:
        lines.extend([f"## {section['heading']}", ""])
        for paragraph in section.get("body", []):
            lines.extend([paragraph, ""])
        if "items" in section:
            lines.extend(f"- {item}" for item in section["items"])
            lines.append("")
        if "table" in section:
            headers = section["table"]["headers"]
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join("---" for _ in headers) + " |")
            for row in section["table"]["rows"]:
                lines.append("| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |")
            lines.append("")
    lines.extend(["## Keywords", ""])
    lines.extend(f"- {term}" for term in page.get("keywords", []))
    return "\n".join(lines)


def main() -> None:
    data, content_pages, traffic = read_data()
    manifest = build_manifest(data, content_pages, traffic)

    write(SITE / "index.html", build_index(data, content_pages, traffic))
    for page in content_pages:
        write(SITE / page["path"], build_content_page(data, page))
        write(ROOT / "docs" / f"{page['slug']}.md", build_markdown_page(data, page))

    write(SITE / "sitemap.xml", build_sitemap(data, content_pages))
    write(SITE / "feed.xml", build_feed(data, content_pages))
    write(SITE / "llms.txt", build_llms(data, content_pages, full=False))
    write(SITE / ".well-known" / "llms.txt", build_llms(data, content_pages, full=False))
    write(SITE / "llms-full.txt", build_llms(data, content_pages, full=True))
    write(SITE / "crawler-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    write(SITE / "keyword-index.json", json.dumps(build_keyword_index(data, content_pages), ensure_ascii=False, indent=2))
    write(SITE / "resources.json", json.dumps(build_resources_json(data, content_pages), ensure_ascii=False, indent=2))
    write(SITE / "traffic.json", json.dumps(traffic, ensure_ascii=False, indent=2))
    write(SITE / "manifest.webmanifest", json.dumps(build_webmanifest(data), ensure_ascii=False, indent=2))
    write(SITE / "assets" / "traffic-card.svg", build_traffic_card_svg(data, traffic))
    write(SITE / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {page_url(data['base_url'], 'sitemap.xml')}\n")
    write(SITE / ".nojekyll", "")
    write(SITE / ".well-known" / "security.txt", f"Contact: {data['repo_url']}/issues\nPreferred-Languages: en, zh\n")
    write(SITE / "404.html", '<!doctype html><meta charset="utf-8"><title>Not found</title><p>Not found. Try <a href="./">GitHub Machine Beacon</a>.</p>')

    write(ROOT / "llms.txt", build_llms(data, content_pages, full=False))
    write(ROOT / "llms-full.txt", build_llms(data, content_pages, full=True))
    write(ROOT / "crawler-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    write(ROOT / "keyword-index.json", json.dumps(build_keyword_index(data, content_pages), ensure_ascii=False, indent=2))
    write(ROOT / "resources.json", json.dumps(build_resources_json(data, content_pages), ensure_ascii=False, indent=2))
    write(ROOT / "traffic.json", json.dumps(traffic, ensure_ascii=False, indent=2))

    print(f"Generated machine-readable site in {SITE}")


if __name__ == "__main__":
    main()
