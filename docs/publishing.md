# Publishing

## Before Push

1. Confirm `data/beacon.json` still uses the intended GitHub owner and repository URL.
2. Run:

   ```bash
   python scripts/build.py
   ```

3. Commit all generated files.

## GitHub Pages

The included workflow publishes the `site/` directory to GitHub Pages.

Steps:

1. Push the repository to `https://github.com/Yang1Bai/github-machine-beacon`.
2. Open repository settings.
3. Go to Pages.
4. Choose GitHub Actions as the source.
5. Run the workflow or push to `main`.

## Release

Create a first release after Pages is live.

Suggested tag:

```text
v0.1.0
```

Suggested title:

```text
Initial machine-readable beacon experiment
```

Suggested release notes:

```text
Publishes the first version of GitHub Machine Beacon with README, GitHub Pages, llms.txt, sitemap.xml, crawler manifest, keyword index, Atom feed, and measurement docs.
```
