const DEFAULT_ORIGIN = "https://yang1bai.github.io/github-machine-beacon";
const COUNTER_KEY = "traffic:v1";
const BOT_PATTERN = /(bot|crawler|spider|slurp|archive|indexer|preview|facebookexternalhit|twitterbot|linkedinbot|discordbot|slackbot|telegrambot|whatsapp|embedly|quora link preview|pinterest|google-inspectiontool|googleother|bingpreview|duckduckbot|baiduspider|yandex|semrush|ahrefs|mj12bot|dotbot|petalbot|bytespider|gptbot|chatgpt-user|openai|anthropic|claude|perplexity|ccbot|cohere|amazonbot|applebot|meta-externalagent)/i;

function classifyVisitor(request) {
  const userAgent = request.headers.get("user-agent") || "";
  const accept = request.headers.get("accept") || "";
  const secFetchMode = request.headers.get("sec-fetch-mode") || "";
  const hasBrowserHints =
    request.headers.has("sec-ch-ua") ||
    request.headers.has("sec-ch-ua-platform") ||
    request.headers.has("sec-fetch-site");

  if (BOT_PATTERN.test(userAgent)) {
    return "machine";
  }

  if (!userAgent.trim()) {
    return "machine";
  }

  if (accept.includes("text/html") && (hasBrowserHints || secFetchMode === "navigate")) {
    return "human";
  }

  if (accept.includes("application/json") || accept.includes("application/xml") || accept.includes("text/plain")) {
    return "machine";
  }

  return "human";
}

function emptySnapshot(now) {
  return {
    schema_version: "github-machine-beacon/cloudflare-traffic/v1",
    source: "Cloudflare Worker edge request classification",
    source_scope: "requests that pass through this Worker URL",
    updated_at: now,
    totals: {
      requests: 0,
      machine: 0,
      human: 0,
      unknown: 0
    },
    paths: {},
    classifier: {
      method: "user-agent and request-header heuristic",
      caveat: "Classification is approximate. It is more useful for directional machine/human split than identity-level analytics."
    }
  };
}

async function readSnapshot(env, now) {
  const stored = await env.TRAFFIC_KV.get(COUNTER_KEY, "json");
  return stored || emptySnapshot(now);
}

async function recordVisit(env, request, url) {
  const now = new Date().toISOString();
  const visitorType = classifyVisitor(request);
  const path = url.pathname;
  const snapshot = await readSnapshot(env, now);

  snapshot.updated_at = now;
  snapshot.totals.requests += 1;
  snapshot.totals[visitorType] = (snapshot.totals[visitorType] || 0) + 1;

  snapshot.paths[path] ||= { requests: 0, machine: 0, human: 0, unknown: 0 };
  snapshot.paths[path].requests += 1;
  snapshot.paths[path][visitorType] = (snapshot.paths[path][visitorType] || 0) + 1;

  await env.TRAFFIC_KV.put(COUNTER_KEY, JSON.stringify(snapshot));
  return snapshot;
}

function jsonResponse(payload, init = {}) {
  return new Response(JSON.stringify(payload, null, 2), {
    ...init,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "access-control-allow-origin": "*",
      ...(init.headers || {})
    }
  });
}

function formatCount(value) {
  return Number(value || 0).toLocaleString("en-US");
}

function escapeSvg(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function svgResponse(svg, init = {}) {
  return new Response(svg, {
    ...init,
    headers: {
      "content-type": "image/svg+xml; charset=utf-8",
      "cache-control": "no-store, no-cache, max-age=0, must-revalidate",
      "access-control-allow-origin": "*",
      "x-content-type-options": "nosniff",
      ...(init.headers || {})
    }
  });
}

function buildTrafficCardSvg(snapshot) {
  const totals = snapshot.totals || {};
  const paths = snapshot.paths || {};
  const pathCount = Object.keys(paths).length;
  const updated = snapshot.updated_at || new Date().toISOString();

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 430" role="img" aria-labelledby="title desc">
  <title id="title">Live Cloudflare edge traffic for GitHub Machine Beacon</title>
  <desc id="desc">Live request counter with machine and human split from the Cloudflare Worker edge endpoint.</desc>
  <rect width="1200" height="430" rx="18" fill="#fbfcf8"/>
  <rect x="24" y="24" width="1152" height="382" rx="14" fill="#ffffff" stroke="#d9e2dc" stroke-width="2"/>
  <text x="64" y="82" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="24" font-weight="800" fill="#0d7f61">LIVE CLOUDFLARE EDGE TRAFFIC</text>
  <text x="64" y="206" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="142" font-weight="850" fill="#2357d9">${formatCount(totals.requests)}</text>
  <text x="72" y="250" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="28" fill="#5c6b63">requests through the live homepage and machine-readable endpoints</text>
  <g font-family="Inter, Segoe UI, Arial, sans-serif">
    <rect x="640" y="74" width="220" height="112" rx="10" fill="#f8faf7" stroke="#d9e2dc"/>
    <text x="662" y="116" font-size="22" font-weight="700" fill="#5c6b63">Machine visits</text>
    <text x="662" y="166" font-size="50" font-weight="850" fill="#17211c">${formatCount(totals.machine)}</text>
    <rect x="890" y="74" width="220" height="112" rx="10" fill="#f8faf7" stroke="#d9e2dc"/>
    <text x="912" y="116" font-size="22" font-weight="700" fill="#5c6b63">Human visits</text>
    <text x="912" y="166" font-size="50" font-weight="850" fill="#17211c">${formatCount(totals.human)}</text>
    <rect x="640" y="214" width="220" height="112" rx="10" fill="#f8faf7" stroke="#d9e2dc"/>
    <text x="662" y="256" font-size="22" font-weight="700" fill="#5c6b63">Unknown</text>
    <text x="662" y="306" font-size="50" font-weight="850" fill="#17211c">${formatCount(totals.unknown)}</text>
    <rect x="890" y="214" width="220" height="112" rx="10" fill="#f8faf7" stroke="#d9e2dc"/>
    <text x="912" y="256" font-size="22" font-weight="700" fill="#5c6b63">Paths tracked</text>
    <text x="912" y="306" font-size="50" font-weight="850" fill="#17211c">${formatCount(pathCount)}</text>
  </g>
  <text x="64" y="352" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="22" fill="#5c6b63">Updated ${escapeSvg(updated)} - source: Cloudflare Worker request classifier</text>
  <text x="64" y="386" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="22" font-weight="750" fill="#17211c">Live homepage: https://github-machine-beacon.yangbai0110.workers.dev/</text>
</svg>`;
}

async function proxyToOrigin(request, url, origin) {
  const originBase = new URL(origin.endsWith("/") ? origin : `${origin}/`);
  const originPath = url.pathname === "/" ? "" : url.pathname.replace(/^\/+/, "");
  const originUrl = new URL(originPath, originBase);
  originUrl.search = url.search;
  const originRequest = new Request(originUrl, request);
  const response = await fetch(originRequest);
  const headers = new Headers(response.headers);
  headers.set("x-github-machine-beacon-proxy", "cloudflare-worker");
  headers.set("cache-control", response.headers.get("cache-control") || "public, max-age=60");
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const now = new Date().toISOString();

    if (url.pathname === "/cloudflare-traffic.json" || url.pathname === "/traffic-edge.json") {
      return jsonResponse(await readSnapshot(env, now));
    }

    if (url.pathname === "/traffic-card.svg") {
      const snapshot =
        request.method === "GET" || request.method === "HEAD"
          ? await recordVisit(env, request, url)
          : await readSnapshot(env, now);
      const svg = buildTrafficCardSvg(snapshot);
      return svgResponse(request.method === "HEAD" ? null : svg);
    }

    if (url.pathname === "/health") {
      return jsonResponse({ ok: true, service: "github-machine-beacon-worker", origin: env.ORIGIN || DEFAULT_ORIGIN });
    }

    if (request.method === "GET" || request.method === "HEAD") {
      await recordVisit(env, request, url);
    }

    return proxyToOrigin(request, url, env.ORIGIN || DEFAULT_ORIGIN);
  }
};
