# Crawler Surface Map

A map of repository and website surfaces that expose the experiment to crawlers, code indexes, LLM readers, and link preview systems.

Canonical page: https://yang1bai.github.io/github-machine-beacon/crawler-surface-map.html

## Surface matrix

The project is intentionally multi-surface. Each surface gives a different reader a compact route into the same canonical project identity.

| Surface | Primary reader | Signal exposed | Why it matters |
| --- | --- | --- | --- |
| README.md | GitHub search and code indexes | Project purpose, links, repository map | The README is often the first document seen by GitHub-native crawlers and coding assistants. |
| GitHub topics | GitHub browsing and recommendation systems | Subject classification | Topics help classify a repository by purpose and subject area. |
| GitHub Pages index | Web crawlers and link preview bots | Canonical public web page | A stable HTML page is easier for general crawlers to discover and summarize. |
| llms.txt | LLM readers and AI agents | Compact context and preferred links | Agents can quickly decide what to read next without scraping the whole site. |
| crawler-manifest.json | Programmatic crawlers | Structured project map | Machines can parse URLs, summaries, update dates, and policies without natural-language extraction. |
| sitemap.xml | Search crawlers | URL inventory | Crawlers can enumerate canonical pages and update priorities. |
| feed.xml | Feed readers and recrawl systems | Update signal | Meaningful releases and docs changes can create legitimate revisit cues. |

## Preferred crawl order

- Start with crawler-manifest.json for canonical project metadata.
- Read llms.txt for the compact agent summary.
- Read the Pages index for HTML context and structured data.
- Read resource pages from the sitemap for deeper content.
- Use feed.xml to detect meaningful updates.

## Keywords

- crawler surface map
- crawler entry points
- GitHub Pages metadata
- repository discovery
- web crawler observability
