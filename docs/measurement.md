# Measurement

Use this file as the experiment log. Keep the cadence boring and consistent.

## Daily Metrics

Record these from GitHub Insights > Traffic:

| Date | Repo views | Unique visitors | Clones | Unique cloners | Top referrers | Top content | Notes |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| 2026-06-12 | | | | | | | Initial publication |

## Homepage Traffic Counter

The homepage traffic panel is backed by `traffic.json`.

- Source: GitHub Traffic API.
- Scope: repository traffic, not raw GitHub Pages server logs.
- Window: the API's current traffic window, normally the recent 14-day period.
- Machine/human split: unavailable unless a request-log backend is added, because GitHub Traffic API does not expose user-agent classification.

## Weekly Review

Questions:

- Which pages or files are being visited?
- Are visits coming from GitHub search, external search, direct links, or unknown referrers?
- Did a docs update, release, issue, or backlink correlate with a traffic change?
- Are machine-readable endpoints receiving attention indirectly through referrers?
- Are keywords still accurate and non-misleading?

## Optional External Signals

Use privacy-preserving tools only:

- search result checks for the project name
- GitHub code search queries
- inbound link search
- archive snapshots
- package or citation references if the project later becomes a package or dataset

## Interpretation Notes

GitHub traffic data is sampled and limited. Treat it as directional evidence, not a complete traffic log. GitHub Pages does not expose raw server logs by default, so do not claim exact bot counts unless an explicit logging layer is added and disclosed.
