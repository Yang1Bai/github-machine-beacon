# Cloudflare Worker Traffic Classifier

This Worker proxies the GitHub Pages mirror origin and records canonical content requests into Cloudflare KV.

It exposes:

- `/` - proxied GitHub Machine Beacon homepage
- `/cloudflare-traffic.json` - edge request totals with machine/human heuristic split
- `/traffic-edge.json` - alias for the same traffic payload
- `/traffic-card.svg` - dynamic SVG card for the GitHub README traffic display
- `/health` - health check

The machine/human split is heuristic. It uses user-agent and request headers, which is more informative than GitHub Traffic API for this purpose but still not identity-level analytics. Static assets, favicon requests, and the README traffic-card SVG are excluded from future visit increments so the counter focuses on page and machine-readable endpoint reads.
