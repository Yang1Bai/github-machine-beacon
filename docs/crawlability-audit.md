# Crawlability Audit

A self-audit of the repository discovery surfaces and machine-readable files currently published by GitHub Machine Beacon.

Canonical page: https://yang1bai.github.io/github-machine-beacon/crawlability-audit.html

## Current status

| Check | Status | Evidence |
| --- | --- | --- |
| Public repository | Pass | Repository is public at https://github.com/Yang1Bai/github-machine-beacon. |
| Canonical Pages URL | Pass | GitHub Pages is published at https://yang1bai.github.io/github-machine-beacon/. |
| llms.txt | Pass | Root site and repository both expose llms.txt. |
| Sitemap | Pass | sitemap.xml lists canonical HTML and machine-readable resources. |
| Crawler manifest | Pass | crawler-manifest.json lists entry points, policies, resources, and measurement fields. |
| Structured data | Pass | HTML pages include JSON-LD metadata. |
| Ethical boundary | Pass | README and ethics docs reject fake traffic, cloaking, hidden text, and unrelated keyword stuffing. |
| Measurement template | Pass | docs/measurement.md and experiment-protocol.html define the measurement cadence. |

## Next audit targets

- Record GitHub traffic baseline after 24 hours.
- Check search result appearance for exact project name after indexing delay.
- Add observations to results-log.html only when there is real data.
- Keep topics focused and remove any term that stops matching project content.

## Keywords

- crawlability audit
- machine-readable audit
- GitHub Pages audit
- metadata validation
- crawler readiness
