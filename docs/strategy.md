# Strategy

Goal: maximize legitimate machine discovery of a GitHub project by making the project easy to classify, crawl, summarize, cite, and revisit.

## Discovery Surfaces

1. GitHub repository page
   - clear project name
   - direct summary in the first paragraph
   - focused GitHub topics
   - meaningful docs with stable names
   - `CITATION.cff`, `SECURITY.md`, `CONTRIBUTING.md`, and license

2. GitHub Pages site
   - canonical URL
   - semantic HTML
   - JSON-LD structured data
   - Open Graph and Twitter card metadata
   - `sitemap.xml`
   - `robots.txt`
   - Atom feed

3. AI/agent entry points
   - `llms.txt`
   - `llms-full.txt`
   - `crawler-manifest.json`
   - `keyword-index.json`
   - `resources.json`
   - `.well-known/llms.txt`

4. Recrawl triggers
   - real release notes
   - meaningful documentation updates
   - Atom feed changes
   - GitHub discussions or issues with experiment logs

5. Reusable resource pages
   - machine-readable repository checklist
   - crawler surface map
   - AI agent entrypoints
   - experiment protocol
   - standards and sources
   - crawlability audit
   - results log

## Content Rules

Every keyword should be connected to real project content. The experiment should attract machine readers because the repo is useful and easy to parse, not because it hides keywords or imitates unrelated projects. Resource pages should be useful enough for a human to bookmark and structured enough for a machine to summarize.

## Initial Experiment Design

Baseline:

- publish the repo
- enable GitHub Pages
- do not promote it for 7 days
- record GitHub traffic metrics daily

Intervention:

- add GitHub topics
- publish a release
- submit the Pages URL to search tools that accept manual submission
- share the repo in a small number of relevant communities
- record traffic metrics daily for another 14 days

Comparison:

- repository views before/after Pages
- referring sites before/after sitemap and feed visibility
- code search appearances
- inbound links and citations

## Avoid

- keyword stuffing
- generated fake commits
- automated refreshes
- fake stars
- fake forks
- unrelated trending keywords
- names that confuse this project with an existing project
