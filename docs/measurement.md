# Measurement

Use this file as the experiment log. Keep the cadence boring and consistent.

## Daily Metrics

Record these from GitHub Insights > Traffic:

| Date | Repo views | Unique visitors | Clones | Unique cloners | Top referrers | Top content | Notes |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| 2026-06-12 | | | | | | | Initial publication |

## Homepage Traffic Counter

The homepage primary traffic panel is backed by the Cloudflare Worker endpoint. `traffic.json` remains the slower GitHub Traffic API snapshot.

- Live source: Cloudflare Worker request counters.
- GitHub source: GitHub Traffic API.
- Scope: Cloudflare counters cover requests through the Worker URL; GitHub counters cover repository traffic, not raw GitHub Pages server logs.
- Window: the API's current traffic window, normally the recent 14-day period.
- Machine/human split: available for requests that pass through the Cloudflare Worker URL; unavailable for direct GitHub repository views because the GitHub Traffic API does not expose user-agent classification.
- Automatic refresh: requires a `TRAFFIC_TOKEN` repository secret with permission to read repository traffic; otherwise the scheduled workflow skips and the site shows the last committed snapshot.

## Cloudflare Edge Split

Cloudflare endpoint:

```text
https://beacon.ybliterature.com/
```

Machine/human split endpoint:

```text
https://beacon.ybliterature.com/cloudflare-traffic.json
```

Geo aggregate endpoint:

```text
https://beacon.ybliterature.com/geo-traffic.json
```

This split is based on a Worker request-header heuristic. It is more direct than GitHub Traffic API for machine/human counting because the Worker sees user-agent headers, but it only counts requests that pass through the Cloudflare Worker URL. Geo data is approximate and represents request exit or cloud edge location, not the physical location of a person or AI company. The Worker stores aggregate counters only; it does not store raw IP addresses or latitude/longitude.

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
