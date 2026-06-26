# Cloudflare Worker Traffic Classifier

This Worker proxies the GitHub Pages mirror origin and records canonical content requests into Cloudflare KV.

It exposes:

- `/` - proxied GitHub Machine Beacon homepage
- `/cloudflare-traffic.json` - edge request totals with machine/human heuristic split
- `/traffic-edge.json` - alias for the same traffic payload
- `/geo-traffic.json` - aggregate country, region, city, Cloudflare colo, and ASN organization counters
- `/traffic-geo.json` - alias for the same geo payload
- `/traffic-classes.json` - split machine traffic into AI readers, security scanners, and generic machine requests
- `/traffic-classification.json` - alias for the same class payload
- `/ai-readers.json` - structured AI reader entry index; requests are counted before the JSON response is served
- `/ai-reader-context.txt` - plain-text AI reader context bundle; requests are counted before the text response is served
- `/traffic-card.svg` - dynamic SVG card for the GitHub README traffic display
- `/health` - health check

The machine/human split is heuristic. It uses user-agent and request headers, which is more informative than GitHub Traffic API for this purpose but still not identity-level analytics. Static assets, favicon requests, and the README traffic-card SVG are excluded from future visit increments so the counter focuses on page and machine-readable endpoint reads. Cloudflare verified categories such as `AI Crawler`, `AI Search`, and `AI Assistant` are counted as `ai_reader`; sensitive-file and exploit-probe paths are classified as `security_scanner` before AI/generic machine classes. Geo data is aggregated from Cloudflare request metadata; the Worker does not store raw IP addresses or latitude/longitude.
