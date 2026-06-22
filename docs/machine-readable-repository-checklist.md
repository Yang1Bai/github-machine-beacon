# Machine-Readable Repository Checklist

A practical checklist for making a GitHub repository easier for crawlers, code indexes, LLM readers, and AI agents to parse.

Canonical page: https://beacon.ybliterature.com/machine-readable-repository-checklist.html

## Repository identity

A machine-readable repository should answer who it is, what it does, where the canonical URLs are, and how it should be cited before a crawler has to infer context from file names.

- Put the project purpose in the first README paragraph.
- Use a stable repository name, description, homepage URL, and license.
- Add focused GitHub topics that describe the project purpose and subject area.
- Publish CITATION.cff when the project is intended to be cited.
- Keep the README summary consistent with the website, manifest, and llms.txt.

## Machine entry points

Use multiple entry points because different machines begin in different places. GitHub code search, web crawlers, LLM readers, link preview bots, feed readers, and archive systems do not all share one discovery path.

- Expose a canonical live Worker URL and keep GitHub Pages as a mirror.
- Publish /llms.txt and a richer /llms-full.txt.
- Publish /sitemap.xml and /robots.txt.
- Publish a JSON crawler manifest with canonical URLs and summaries.
- Publish a keyword index grouped by intent, not a flat keyword dump.
- Publish an Atom feed for legitimate update and recrawl signals.

## Content quality

Discovery improves when machines find useful, stable, internally linked pages that can be summarized and cited. The clean path is to create real resources, not hidden text or unrelated trend terms.

- Create reusable pages such as checklists, protocols, glossaries, matrices, and measurement templates.
- Give each page a descriptive title, summary, canonical URL, and JSON-LD block.
- Keep page copy short enough to parse but complete enough to quote or summarize.
- Use plain tables for structured comparisons.
- Make update dates explicit and avoid meaningless timestamp churn.

## Keywords

- machine-readable repository checklist
- GitHub README structure
- crawler-friendly documentation
- AI agent documentation
- repository metadata
