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

    if (url.pathname === "/health") {
      return jsonResponse({ ok: true, service: "github-machine-beacon-worker", origin: env.ORIGIN || DEFAULT_ORIGIN });
    }

    if (request.method === "GET" || request.method === "HEAD") {
      await recordVisit(env, request, url);
    }

    return proxyToOrigin(request, url, env.ORIGIN || DEFAULT_ORIGIN);
  }
};
