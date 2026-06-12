# Experiment Protocol

A reproducible protocol for measuring whether machine-readable repository surfaces increase legitimate GitHub and web discovery.

Canonical page: https://yang1bai.github.io/github-machine-beacon/experiment-protocol.html

## Hypothesis

A public GitHub repository with coherent machine-readable surfaces, useful resource pages, structured metadata, and transparent update signals should receive more legitimate machine discovery than a repository with only a basic README.

## Phases

| Phase | Duration | Action | Measurement |
| --- | --- | --- | --- |
| Baseline | 7 days | Publish the repository and do not run paid or automated promotion. | Record GitHub views, unique visitors, clones, referrers, and popular content daily. |
| Metadata expansion | 7 days | Add resource pages, structured data, sitemap, feed, manifest, and llms files. | Compare repository traffic and referrer mix against baseline. |
| Legitimate distribution | 14 days | Share the repository only in relevant communities and owner-controlled profiles. | Record changes in GitHub traffic, search visibility, links, stars, forks, and issues. |
| Maintenance | Ongoing | Publish meaningful updates only when content changes. | Track whether releases, issues, and resource updates correlate with revisit signals. |

## Data caveats

- GitHub traffic data is limited and should be treated as directional.
- GitHub Pages does not expose raw server logs by default.
- A 200 response from a machine endpoint proves availability, not traffic volume.
- Referrer data can be sparse or missing for privacy and platform reasons.
- Do not infer exact bot counts without an explicitly disclosed analytics layer.

## Keywords

- repository traffic experiment
- GitHub Insights traffic
- crawler experiment protocol
- public web observability
- bot traffic research
