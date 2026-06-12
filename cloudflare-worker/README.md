# Cloudflare Worker Traffic Classifier

This Worker proxies the GitHub Pages site and records edge requests into Cloudflare KV.

It exposes:

- `/` - proxied GitHub Machine Beacon homepage
- `/cloudflare-traffic.json` - edge request totals with machine/human heuristic split
- `/traffic-edge.json` - alias for the same traffic payload
- `/health` - health check

The machine/human split is heuristic. It uses user-agent and request headers, which is more informative than GitHub Traffic API for this purpose but still not identity-level analytics.
