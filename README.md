# GitHub Machine Beacon

Transparent experiment: make a GitHub project unusually easy for crawlers, code search, AI agents, LLM readers, link preview bots, and search indexes to discover, parse, cite, revisit, and measure.

[![Deploy GitHub Pages](https://github.com/Yang1Bai/github-machine-beacon/actions/workflows/pages.yml/badge.svg)](https://github.com/Yang1Bai/github-machine-beacon/actions/workflows/pages.yml)
[![Validate Machine Surfaces](https://github.com/Yang1Bai/github-machine-beacon/actions/workflows/validate.yml/badge.svg)](https://github.com/Yang1Bai/github-machine-beacon/actions/workflows/validate.yml)

Chinese guide: [`README.zh-CN.md`](README.zh-CN.md)

中文摘要：这是一个“机器可读 GitHub 项目”实验。目标不是刷量，而是把公开项目做成对机器读者极其友好的形态：清晰 README、GitHub Pages、`llms.txt`、`sitemap.xml`、Atom feed、JSON manifest、结构化关键词地图、可复现实验记录。

## What This Project Tests

Most repositories are designed for humans first. This one treats machine readers as first-class visitors:

- repository readers: GitHub search, code indexers, dependency scanners, citation tools
- web crawlers: search engines, link unfurlers, archive bots, feed readers
- AI readers: LLM crawlers, retrieval systems, agent browsers, coding assistants
- research readers: people auditing whether machine-friendly metadata changes discovery

The hypothesis is simple: a repo with coherent machine-readable surfaces, stable URLs, explicit metadata, and useful content should be discovered and revisited more often than a repo with only a normal README.

## Traffic Display

The project homepage shows a large current traffic panel backed by [`traffic.json`](traffic.json).

- `views` and `unique visitors` come from the GitHub Traffic API.
- the window is the GitHub Traffic API's current repository traffic window, normally the recent 14-day period.
- `machine visits` and `human visits` are shown as unavailable unless a request-log backend is added, because GitHub's public traffic data does not expose user-agent classification.
- `.github/workflows/update-traffic.yml` refreshes the snapshot on a schedule and republishes the site when values change.

## Resource Library

These pages are intended to be useful resources, not just discovery bait:

- [Machine-Readable Repository Checklist](https://yang1bai.github.io/github-machine-beacon/machine-readable-repository-checklist.html)
- [Crawler Surface Map](https://yang1bai.github.io/github-machine-beacon/crawler-surface-map.html)
- [AI Agent Entrypoints](https://yang1bai.github.io/github-machine-beacon/ai-agent-entrypoints.html)
- [Experiment Protocol](https://yang1bai.github.io/github-machine-beacon/experiment-protocol.html)
- [Standards and Sources](https://yang1bai.github.io/github-machine-beacon/standards-and-sources.html)
- [Crawlability Audit](https://yang1bai.github.io/github-machine-beacon/crawlability-audit.html)
- [Results Log](https://yang1bai.github.io/github-machine-beacon/results-log.html)

## Machine Entry Points

After publishing with GitHub Pages, these endpoints become the main crawler surfaces:

- `/` - semantic landing page with JSON-LD, Open Graph, and canonical metadata
- `/llms.txt` - compact guide for LLM and agent readers
- `/llms-full.txt` - extended context bundle for retrieval systems
- `/crawler-manifest.json` - canonical machine-readable project manifest
- `/keyword-index.json` - topic map for discovery experiments
- `/resources.json` - structured index of all human-readable and machine-readable resources
- `/traffic.json` - latest public traffic snapshot used by the homepage counter
- `/sitemap.xml` - URL inventory for crawlers
- `/feed.xml` - Atom feed for recrawl triggers
- `/robots.txt` - transparent crawl permission and sitemap pointer

The repository itself also exposes:

- [`llms.txt`](llms.txt)
- [`llms-full.txt`](llms-full.txt)
- [`crawler-manifest.json`](crawler-manifest.json)
- [`resources.json`](resources.json)
- [`traffic.json`](traffic.json)
- [`keyword-index.json`](keyword-index.json)
- [`data/beacon.json`](data/beacon.json)
- [`data/content-pages.json`](data/content-pages.json)
- [`docs/strategy.md`](docs/strategy.md)
- [`docs/measurement.md`](docs/measurement.md)
- [`docs/ethics.md`](docs/ethics.md)

## Ethical Boundary

This project intentionally avoids:

- fake content, cloaking, hidden text, doorway pages, or misleading metadata
- automated traffic generation, botnets, proxy traffic, or refresh loops
- copying popular project names or impersonating brands
- collecting personal data from visitors

It does use:

- clear project identity
- honest keywords that describe the experiment
- public metadata formats
- stable, crawlable, human-readable pages
- reproducible release and measurement notes

## Quick Start

1. Confirm [`data/beacon.json`](data/beacon.json) points to the intended owner, repository URL, and Pages URL.
2. Run:

   ```bash
   python scripts/build.py
   python scripts/validate.py
   ```

3. Commit the generated files.
4. Push to GitHub.
5. Enable GitHub Pages with the included workflow.
6. Add GitHub topics from [`docs/github-topics.txt`](docs/github-topics.txt).
7. Track results using GitHub Insights > Traffic and the template in [`docs/measurement.md`](docs/measurement.md).

## Recommended GitHub Topics

Use a focused set. Do not add unrelated popular topics.

`llms-txt`, `crawler`, `web-crawling`, `github-pages`, `metadata`, `json-ld`, `sitemap`, `ai-agents`, `search-indexing`, `machine-readable`, `retrieval-augmented-generation`, `observability`

## Repository Map

```text
.
+-- README.md
+-- data/
|   +-- beacon.json
|   +-- content-pages.json
+-- docs/
|   +-- ethics.md
|   +-- github-topics.txt
|   +-- measurement.md
|   +-- publishing.md
|   +-- strategy.md
|   +-- machine-readable-repository-checklist.md
|   +-- crawler-surface-map.md
|   +-- ai-agent-entrypoints.md
|   +-- experiment-protocol.md
|   +-- standards-and-sources.md
|   +-- crawlability-audit.md
|   +-- results-log.md
+-- scripts/
|   +-- build.py
|   +-- validate.py
+-- site/
|   +-- assets/
|   |   +-- beacon-map.svg
|   |   +-- styles.css
|   +-- index.html
|   +-- llms.txt
|   +-- llms-full.txt
|   +-- crawler-manifest.json
|   +-- keyword-index.json
|   +-- resources.json
|   +-- traffic.json
|   +-- manifest.webmanifest
|   +-- sitemap.xml
|   +-- feed.xml
|   +-- robots.txt
+-- .github/
    +-- workflows/
        +-- pages.yml
        +-- validate.yml
```

## Success Metrics

Primary:

- GitHub repository views
- unique visitors
- referring sites
- clones and unique cloners
- GitHub Pages visits if a privacy-preserving analytics layer is added later

Secondary:

- search result appearance
- external citations
- inbound links
- stars and forks
- issue/discussion mentions from people or agents

## License

MIT. See [`LICENSE`](LICENSE).
