// GitHub Machine Beacon - Cloudflare Worker (optimized)
// -----------------------------------------------------------------------------
// Changes vs. the original worker:
//   1. Classification now uses Cloudflare's authoritative verified-bot signals
//      (request.cf.verifiedBotCategory / botManagement) first, then falls back
//      to the UA + header heuristic. It also records WHICH machine came
//      (Googlebot, GPTBot, ClaudeBot, ...), turning the counter into evidence.
//   2. Owner / self traffic is excluded from the public counter, so your own
//      testing no longer inflates "human". (This was why it looked like "all me".)
//   3. The Worker serves its own enhanced robots.txt that explicitly welcomes
//      AI/LLM crawlers and points at the sitemap.
//   4. The Worker hosts the IndexNow key file and search-engine verification
//      tokens, and exposes an owner-triggered IndexNow ping at /ops/indexnow.
//   KV schema stays backward compatible: only new fields are added.
// -----------------------------------------------------------------------------

const DEFAULT_ORIGIN = "https://yang1bai.github.io/github-machine-beacon";
const DEFAULT_HOST = "beacon.ybliterature.com";
const COUNTER_KEY = "traffic:v1";
const GEO_BUCKET_LIMIT = 250;
const TRAFFIC_CLASS_KEYS = ["ai_reader", "security_scanner", "generic_machine", "human", "unknown"];

const MACHINE_UA_PATTERN = /(bot|crawler|spider|slurp|archive|indexer|preview|facebookexternalhit|twitterbot|linkedinbot|discordbot|slackbot|telegrambot|whatsapp|embedly|quora link preview|pinterest|google-inspectiontool|googleother|bingpreview|duckduckbot|baiduspider|yandex|semrush|ahrefs|mj12bot|dotbot|petalbot|bytespider|gptbot|oai-searchbot|chatgpt-user|openai|anthropic|claude|perplexity|ccbot|cohere|amazonbot|applebot|meta-externalagent|github-camo|curl|wget|python-requests|go-http-client|node-fetch|undici|axios|okhttp|java\/|libwww-perl|ruby|php|headlesschrome|playwright|puppeteer)/i;

const AI_READER_CATEGORY_PATTERN = /(gptbot|oai-searchbot|chatgpt-user|openai|claude|anthropic|perplexity|ccbot|cohere|googlebot|google inspection|googleother|bingbot|duckduckbot|applebot|amazonbot|bytespider|meta|diffbot|youbot)/i;

const STATIC_ASSET_PATTERN = /^\/(?:assets\/|favicon\.ico$)|\.(?:css|js|mjs|svg|png|jpe?g|gif|webp|ico|avif|woff2?|ttf|map)$/i;
const COUNTER_ASSET_PATHS = new Set(["/traffic-card.svg"]);

// Canonical URL set advertised to IndexNow and the enhanced robots/sitemap.
const CANONICAL_PATHS = [
  "/",
  "/llms.txt",
  "/llms-full.txt",
  "/crawler-manifest.json",
  "/keyword-index.json",
  "/resources.json",
  "/traffic.json",
  "/sitemap.xml",
  "/feed.xml",
  "/machine-readable-repository-checklist.html",
  "/crawler-surface-map.html",
  "/ai-agent-entrypoints.html",
  "/experiment-protocol.html",
  "/standards-and-sources.html",
  "/crawlability-audit.html",
  "/results-log.html"
];

// AI / LLM crawlers we explicitly welcome in robots.txt (transparent, opt-in).
const WELCOMED_AI_AGENTS = [
  "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-Web",
  "anthropic-ai", "PerplexityBot", "Perplexity-User", "Google-Extended",
  "Applebot-Extended", "CCBot", "Bytespider", "Amazonbot",
  "meta-externalagent", "cohere-ai", "Diffbot", "Timpibot", "YouBot"
];

// -----------------------------------------------------------------------------
// Classification
// -----------------------------------------------------------------------------

function machineLabelFromUA(ua) {
  const u = ua.toLowerCase();
  const table = [
    ["googlebot", "Googlebot"], ["google-inspectiontool", "Google Inspection"],
    ["googleother", "GoogleOther"], ["bingbot", "Bingbot"], ["bingpreview", "Bingbot"],
    ["duckduckbot", "DuckDuckBot"], ["baiduspider", "Baiduspider"], ["yandex", "YandexBot"],
    ["gptbot", "GPTBot"], ["oai-searchbot", "OAI-SearchBot"], ["chatgpt-user", "ChatGPT-User"],
    ["openai", "OpenAI"], ["claudebot", "ClaudeBot"], ["claude-web", "Claude-Web"],
    ["anthropic", "Anthropic"], ["perplexity", "PerplexityBot"], ["ccbot", "CCBot"],
    ["cohere", "Cohere"], ["amazonbot", "Amazonbot"], ["applebot", "Applebot"],
    ["bytespider", "Bytespider"], ["meta-externalagent", "Meta"], ["facebookexternalhit", "Facebook"],
    ["twitterbot", "Twitterbot"], ["linkedinbot", "LinkedInBot"], ["slackbot", "Slackbot"],
    ["discordbot", "Discordbot"], ["telegrambot", "TelegramBot"], ["whatsapp", "WhatsApp"],
    ["github-camo", "GitHub-Camo"], ["semrush", "SemrushBot"], ["ahrefs", "AhrefsBot"],
    ["curl", "curl"], ["wget", "wget"], ["python-requests", "python-requests"],
    ["go-http-client", "Go-http-client"], ["node-fetch", "node-fetch"], ["axios", "axios"],
    ["undici", "undici"], ["okhttp", "OkHttp"], ["headlesschrome", "HeadlessChrome"],
    ["playwright", "Playwright"], ["puppeteer", "Puppeteer"]
  ];
  for (const [needle, label] of table) {
    if (u.includes(needle)) return label;
  }
  if (/(bot|crawler|spider|indexer|archive|preview)/.test(u)) return "Other Bot";
  return "Other Machine";
}

// Returns { type: "machine"|"human", category: string, verified: boolean }
function classifyVisitor(request) {
  const cf = request.cf || {};
  const ua = request.headers.get("user-agent") || "";

  // 1. Cloudflare's verified-bot list is authoritative when present (all plans
  //    expose verifiedBotCategory for known good bots; guarded for safety).
  const verifiedCategory = cf.verifiedBotCategory || "";
  const bm = cf.botManagement || {};
  if (bm.verifiedBot === true || (verifiedCategory && verifiedCategory.toLowerCase() !== "" && verifiedCategory.toLowerCase() !== "unknown")) {
    const uaLabel = machineLabelFromUA(ua);
    const verifiedLabel = verifiedCategory && verifiedCategory.toLowerCase() !== "unknown"
      ? verifiedCategory
      : "";
    const label = verifiedLabel && uaLabel && uaLabel !== "Other Machine" && uaLabel.toLowerCase() !== verifiedLabel.toLowerCase()
      ? `${verifiedLabel}: ${uaLabel}`
      : verifiedLabel || uaLabel;
    return { type: "machine", category: label || "Verified Bot", verified: true };
  }

  // 2. Bot Management score (only on plans that provide it). Low score = bot.
  if (typeof bm.score === "number" && bm.score > 0 && bm.score <= 30) {
    return { type: "machine", category: machineLabelFromUA(ua), verified: false };
  }

  // 3. User-agent regex.
  if (MACHINE_UA_PATTERN.test(ua)) {
    return { type: "machine", category: machineLabelFromUA(ua), verified: false };
  }

  // 4. Missing UA is machine-ish.
  if (!ua.trim()) {
    return { type: "machine", category: "No User-Agent", verified: false };
  }

  // 5. Real browsers send client hints / navigate fetch mode.
  const accept = request.headers.get("accept") || "";
  const secFetchMode = request.headers.get("sec-fetch-mode") || "";
  const hasBrowserHints =
    request.headers.has("sec-ch-ua") ||
    request.headers.has("sec-ch-ua-platform") ||
    request.headers.has("sec-fetch-site");
  if (accept.includes("text/html") && (hasBrowserHints || secFetchMode === "navigate")) {
    return { type: "human", category: "Browser", verified: false };
  }

  // 6. Data-format Accept headers without browser hints => machine.
  if (accept.includes("application/json") || accept.includes("application/xml") || accept.includes("text/plain")) {
    return { type: "machine", category: "Data Fetch", verified: false };
  }

  // 7. A bare request to a machine-only endpoint with no browser hints is
  //    almost certainly a tool, not a person in a browser.
  if (!hasBrowserHints && !accept.includes("text/html")) {
    return { type: "machine", category: "Headless Fetch", verified: false };
  }

  return { type: "human", category: "Unclassified", verified: false };
}

// -----------------------------------------------------------------------------
// Owner / self detection (so your own visits don't pollute the counter)
// -----------------------------------------------------------------------------

function isOwnerRequest(request, url, env) {
  const token = env.OWNER_TOKEN;
  if (!token) return false;
  if (url.searchParams.get("beacon_owner") === token) return true;
  if (request.headers.get("x-beacon-owner") === token) return true;
  const cookie = request.headers.get("cookie") || "";
  return cookie.split(/;\s*/).includes(`beacon_owner=${token}`);
}

// -----------------------------------------------------------------------------
// Snapshot / KV
// -----------------------------------------------------------------------------

function classifierMeta() {
  return {
    method: "cloudflare verified-bot signals + user-agent/header heuristic + security-probe path classifier",
    caveat: "Classification is approximate. Cloudflare verified bots are authoritative when available; the rest is heuristic. Sensitive-file and exploit-probe paths are classified as security_scanner before AI/generic machine classes. Static assets and the README traffic-card SVG are excluded, and owner/self traffic is excluded from totals."
  };
}

function emptySnapshot(now) {
  return {
    schema_version: "github-machine-beacon/cloudflare-traffic/v2",
    source: "Cloudflare Worker edge request classification",
    source_scope: "requests that pass through this Worker URL",
    updated_at: now,
    totals: { requests: 0, machine: 0, human: 0, unknown: 0 },
    verified_machine: 0,
    excluded_self: 0,
    traffic_classes: emptyTrafficClasses(),
    machine_categories: {},
    paths: {},
    geo: emptyGeo(),
    classifier: classifierMeta(),
    privacy: privacyInfo()
  };
}

function emptyGeo() {
  return {
    countries: {},
    regions: {},
    cities: {},
    continents: {},
    colos: {},
    asOrganizations: {}
  };
}

function privacyInfo() {
  return {
    raw_ip_storage: false,
    latitude_longitude_storage: false,
    geo_precision: "aggregated country, region, city, Cloudflare colo, and ASN organization counters only"
  };
}

function normalizeSnapshot(snapshot, now) {
  const normalized = snapshot || emptySnapshot(now);
  normalized.schema_version = "github-machine-beacon/cloudflare-traffic/v2";
  normalized.totals ||= { requests: 0, machine: 0, human: 0, unknown: 0 };
  normalized.verified_machine ||= 0;
  normalized.excluded_self ||= 0;
  normalized.traffic_classes = normalized.traffic_classes
    ? normalizeTrafficClasses(normalized.traffic_classes)
    : legacyTrafficClasses(normalized);
  normalized.machine_categories ||= {};
  normalized.paths ||= {};
  normalized.geo ||= emptyGeo();
  for (const key of Object.keys(emptyGeo())) {
    normalized.geo[key] ||= {};
  }
  normalized.classifier = classifierMeta();
  normalized.privacy = privacyInfo();
  return normalized;
}

async function readSnapshot(env, now) {
  const stored = await env.TRAFFIC_KV.get(COUNTER_KEY, "json");
  return normalizeSnapshot(stored, now);
}

function shouldRecordVisit(url) {
  return !COUNTER_ASSET_PATHS.has(url.pathname) && !STATIC_ASSET_PATTERN.test(url.pathname);
}

function emptyTrafficClasses() {
  return Object.fromEntries(TRAFFIC_CLASS_KEYS.map((key) => [key, 0]));
}

function normalizeTrafficClasses(classes = {}) {
  const normalized = emptyTrafficClasses();
  for (const key of TRAFFIC_CLASS_KEYS) {
    normalized[key] = Number(classes?.[key] || 0);
  }
  return normalized;
}

function isSecurityProbePath(pathname) {
  const path = String(pathname || "/").toLowerCase();
  return (
    path.includes("/.env") ||
    path.startsWith("/.git") ||
    path.includes("wp-login.php") ||
    path.includes("wp-admin") ||
    path.includes("wp-json") ||
    path.includes("xmlrpc.php") ||
    /\/(?:phpinfo|test|shell|adminer)\.php(?:$|[/?#])/.test(path) ||
    /\/(?:config|settings|credentials|secrets|database|dump|backup|db)(?:[.\-/]|$)/.test(path) ||
    /\/(?:docker-compose\.ya?ml|dockerfile|jenkinsfile|\.gitlab-ci\.yml|\.npmrc|\.pypirc|\.git-credentials|web\.config|appsettings(?:\.[a-z]+)?\.json|application\.(?:ya?ml|properties))(?:$|[?#])/.test(path) ||
    /\/(?:logs?|storage\/logs|var\/log)\//.test(path)
  );
}

function trafficClassFor(pathname, verdict) {
  if (verdict.type === "human") return "human";
  if (verdict.type === "unknown") return "unknown";
  if (isSecurityProbePath(pathname)) return "security_scanner";
  if (AI_READER_CATEGORY_PATTERN.test(verdict.category || "")) return "ai_reader";
  return "generic_machine";
}

function legacyTrafficClasses(snapshot) {
  const classes = emptyTrafficClasses();
  classes.human = Number(snapshot?.totals?.human || 0);
  classes.unknown = Number(snapshot?.totals?.unknown || 0);

  let securityScanner = 0;
  for (const [path, counts] of Object.entries(snapshot?.paths || {})) {
    if (isSecurityProbePath(path)) {
      securityScanner += Number(counts?.machine || 0);
    }
  }

  let aiReader = 0;
  for (const [category, count] of Object.entries(snapshot?.machine_categories || {})) {
    if (AI_READER_CATEGORY_PATTERN.test(category)) {
      aiReader += Number(count || 0);
    }
  }

  const totalMachine = Number(snapshot?.totals?.machine || 0);
  classes.security_scanner = securityScanner;
  classes.ai_reader = Math.min(aiReader, Math.max(totalMachine - securityScanner, 0));
  classes.generic_machine = Math.max(totalMachine - classes.security_scanner - classes.ai_reader, 0);
  return classes;
}

function cleanGeoValue(value, fallback = "unknown") {
  const text = String(value || "").trim();
  return text || fallback;
}

function geoKey(parts) {
  return parts.map((part) => cleanGeoValue(part)).join("|");
}

function extractGeo(request) {
  const cf = request.cf || {};
  const country = cleanGeoValue(cf.country || request.headers.get("cf-ipcountry"), "XX").toUpperCase();
  const region = cleanGeoValue(cf.region);
  const regionCode = cleanGeoValue(cf.regionCode).toUpperCase();
  const city = cleanGeoValue(cf.city);
  const continent = cleanGeoValue(cf.continent).toUpperCase();
  const timezone = cleanGeoValue(cf.timezone);
  const colo = cleanGeoValue(cf.colo).toUpperCase();
  const asn = cleanGeoValue(cf.asn);
  const asOrganization = cleanGeoValue(cf.asOrganization);

  return { country, region, regionCode, city, continent, timezone, colo, asn, asOrganization };
}

function incrementBucket(bucket, key, visitorType, trafficClass, metadata = {}) {
  bucket[key] ||= { ...metadata, requests: 0, machine: 0, human: 0, unknown: 0, traffic_classes: emptyTrafficClasses() };
  bucket[key].traffic_classes = normalizeTrafficClasses(bucket[key].traffic_classes);
  bucket[key].requests += 1;
  bucket[key][visitorType] = (bucket[key][visitorType] || 0) + 1;
  bucket[key].traffic_classes[trafficClass] = (bucket[key].traffic_classes[trafficClass] || 0) + 1;
}

function pruneBucket(bucket) {
  const entries = Object.entries(bucket);
  if (entries.length <= GEO_BUCKET_LIMIT) {
    return bucket;
  }
  return Object.fromEntries(
    entries
      .sort(([, left], [, right]) => (right.requests || 0) - (left.requests || 0))
      .slice(0, GEO_BUCKET_LIMIT)
  );
}

function recordGeo(snapshot, request, visitorType, trafficClass) {
  const geo = extractGeo(request);

  incrementBucket(snapshot.geo.countries, geo.country, visitorType, trafficClass, {
    country: geo.country,
    continent: geo.continent
  });
  incrementBucket(snapshot.geo.regions, geoKey([geo.country, geo.regionCode]), visitorType, trafficClass, {
    country: geo.country,
    region: geo.region,
    regionCode: geo.regionCode,
    continent: geo.continent
  });
  incrementBucket(snapshot.geo.cities, geoKey([geo.country, geo.regionCode, geo.city]), visitorType, trafficClass, {
    country: geo.country,
    region: geo.region,
    regionCode: geo.regionCode,
    city: geo.city,
    timezone: geo.timezone,
    continent: geo.continent
  });
  incrementBucket(snapshot.geo.continents, geo.continent, visitorType, trafficClass, {
    continent: geo.continent
  });
  incrementBucket(snapshot.geo.colos, geo.colo, visitorType, trafficClass, {
    colo: geo.colo
  });
  incrementBucket(snapshot.geo.asOrganizations, geoKey([geo.asn, geo.asOrganization]), visitorType, trafficClass, {
    asn: geo.asn,
    organization: geo.asOrganization
  });

  for (const key of Object.keys(snapshot.geo)) {
    snapshot.geo[key] = pruneBucket(snapshot.geo[key]);
  }
}

function geoSnapshot(snapshot) {
  return {
    schema_version: "github-machine-beacon/geo-traffic/v1",
    source: snapshot.source,
    source_scope: snapshot.source_scope,
    updated_at: snapshot.updated_at,
    totals: snapshot.totals,
    geo: snapshot.geo || emptyGeo(),
    classifier: snapshot.classifier,
    privacy: snapshot.privacy
  };
}

function classSnapshot(snapshot) {
  const securityPaths = Object.entries(snapshot.paths || {})
    .filter(([path, counts]) => isSecurityProbePath(path) && Number(counts?.machine || 0) > 0)
    .map(([path, counts]) => ({
      path,
      requests: Number(counts.requests || 0),
      machine: Number(counts.machine || 0),
      security_scanner: Number(counts.traffic_classes?.security_scanner || counts.machine || 0)
    }))
    .sort((left, right) => right.security_scanner - left.security_scanner || right.requests - left.requests)
    .slice(0, 40);

  return {
    schema_version: "github-machine-beacon/traffic-classes/v1",
    source: snapshot.source,
    source_scope: snapshot.source_scope,
    updated_at: snapshot.updated_at,
    totals: snapshot.totals,
    traffic_classes: normalizeTrafficClasses(snapshot.traffic_classes),
    verified_machine: snapshot.verified_machine || 0,
    excluded_self: snapshot.excluded_self || 0,
    machine_categories: snapshot.machine_categories || {},
    top_security_paths: securityPaths,
    classifier: snapshot.classifier,
    privacy: snapshot.privacy
  };
}

async function recordVisit(env, request, url) {
  const now = new Date().toISOString();
  const snapshot = await readSnapshot(env, now);
  snapshot.updated_at = now;
  snapshot.classifier = classifierMeta();

  // Owner / self traffic is tracked separately and kept out of the public totals.
  if (isOwnerRequest(request, url, env)) {
    snapshot.excluded_self += 1;
    await env.TRAFFIC_KV.put(COUNTER_KEY, JSON.stringify(snapshot));
    return snapshot;
  }

  const verdict = classifyVisitor(request);
  const visitorType = verdict.type;
  const path = url.pathname;
  const trafficClass = trafficClassFor(path, verdict);

  snapshot.totals.requests += 1;
  snapshot.totals[visitorType] = (snapshot.totals[visitorType] || 0) + 1;
  snapshot.traffic_classes = normalizeTrafficClasses(snapshot.traffic_classes);
  snapshot.traffic_classes[trafficClass] = (snapshot.traffic_classes[trafficClass] || 0) + 1;
  if (verdict.verified) snapshot.verified_machine += 1;

  if (visitorType === "machine") {
    const cat = verdict.category || "Other Machine";
    snapshot.machine_categories[cat] = (snapshot.machine_categories[cat] || 0) + 1;
  }

  snapshot.paths[path] ||= { requests: 0, machine: 0, human: 0, unknown: 0 };
  snapshot.paths[path].traffic_classes = normalizeTrafficClasses(snapshot.paths[path].traffic_classes);
  snapshot.paths[path].requests += 1;
  snapshot.paths[path][visitorType] = (snapshot.paths[path][visitorType] || 0) + 1;
  snapshot.paths[path].traffic_classes[trafficClass] = (snapshot.paths[path].traffic_classes[trafficClass] || 0) + 1;
  recordGeo(snapshot, request, visitorType, trafficClass);

  await env.TRAFFIC_KV.put(COUNTER_KEY, JSON.stringify(snapshot));
  return snapshot;
}

// -----------------------------------------------------------------------------
// Responses
// -----------------------------------------------------------------------------

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

function textResponse(text, init = {}) {
  return new Response(text, {
    ...init,
    headers: {
      "content-type": "text/plain; charset=utf-8",
      "cache-control": "no-store",
      ...(init.headers || {})
    }
  });
}

function canonicalHost(request, env) {
  return env.CANONICAL_HOST || new URL(request.url).host || DEFAULT_HOST;
}

function buildRobotsTxt(host) {
  const lines = [
    "# GitHub Machine Beacon - machine readers are welcome.",
    "# Transparent discovery experiment. No cloaking, no hidden text.",
    "",
    "User-agent: *",
    "Allow: /",
    ""
  ];
  for (const agent of WELCOMED_AI_AGENTS) {
    lines.push(`User-agent: ${agent}`, "Allow: /", "");
  }
  lines.push(`Sitemap: https://${host}/sitemap.xml`, "");
  return lines.join("\n");
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
    <text x="662" y="256" font-size="22" font-weight="700" fill="#5c6b63">Verified bots</text>
    <text x="662" y="306" font-size="50" font-weight="850" fill="#17211c">${formatCount(snapshot.verified_machine)}</text>
    <rect x="890" y="214" width="220" height="112" rx="10" fill="#f8faf7" stroke="#d9e2dc"/>
    <text x="912" y="256" font-size="22" font-weight="700" fill="#5c6b63">Paths tracked</text>
    <text x="912" y="306" font-size="50" font-weight="850" fill="#17211c">${formatCount(pathCount)}</text>
  </g>
  <text x="64" y="352" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="22" fill="#5c6b63">Updated ${escapeSvg(updated)} - source: Cloudflare Worker request classifier</text>
  <text x="64" y="386" font-family="Inter, Segoe UI, Arial, sans-serif" font-size="22" font-weight="750" fill="#17211c">Live homepage: https://beacon.ybliterature.com/</text>
</svg>`;
}

// -----------------------------------------------------------------------------
// IndexNow
// -----------------------------------------------------------------------------

async function pingIndexNow(host, key, urls) {
  const body = {
    host,
    key,
    keyLocation: `https://${host}/${key}.txt`,
    urlList: urls
  };
  const res = await fetch("https://api.indexnow.org/indexnow", {
    method: "POST",
    headers: { "content-type": "application/json; charset=utf-8" },
    body: JSON.stringify(body)
  });
  return { status: res.status, ok: res.ok, submitted: urls.length };
}

// -----------------------------------------------------------------------------
// Origin proxy
// -----------------------------------------------------------------------------

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

// -----------------------------------------------------------------------------
// Worker entry
// -----------------------------------------------------------------------------

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const now = new Date().toISOString();
    const host = canonicalHost(request, env);

    // --- Live traffic JSON ---
    if (url.pathname === "/cloudflare-traffic.json" || url.pathname === "/traffic-edge.json") {
      return jsonResponse(await readSnapshot(env, now));
    }

    // --- Live traffic card ---
    if (url.pathname === "/geo-traffic.json" || url.pathname === "/traffic-geo.json") {
      return jsonResponse(geoSnapshot(await readSnapshot(env, now)));
    }

    if (url.pathname === "/traffic-classes.json" || url.pathname === "/traffic-classification.json") {
      return jsonResponse(classSnapshot(await readSnapshot(env, now)));
    }

    if (url.pathname === "/traffic-card.svg") {
      const snapshot = await readSnapshot(env, now);
      const svg = buildTrafficCardSvg(snapshot);
      return svgResponse(request.method === "HEAD" ? null : svg);
    }

    // --- Health ---
    if (url.pathname === "/health") {
      return jsonResponse({ ok: true, service: "github-machine-beacon-worker", origin: env.ORIGIN || DEFAULT_ORIGIN });
    }

    // --- IndexNow key file (hosted on the canonical host) ---
    if (env.INDEXNOW_KEY && url.pathname === `/${env.INDEXNOW_KEY}.txt`) {
      return textResponse(env.INDEXNOW_KEY);
    }

    // --- Search-engine verification tokens (served from config) ---
    if (env.GOOGLE_SITE_VERIFICATION && url.pathname === `/${env.GOOGLE_SITE_VERIFICATION}`) {
      return textResponse(`google-site-verification: ${env.GOOGLE_SITE_VERIFICATION}`);
    }
    if (env.BING_SITE_AUTH && url.pathname === "/BingSiteAuth.xml") {
      return new Response(
        `<?xml version="1.0"?>\n<users>\n  <user>${env.BING_SITE_AUTH}</user>\n</users>\n`,
        { headers: { "content-type": "application/xml; charset=utf-8", "cache-control": "no-store" } }
      );
    }

    // --- Enhanced robots.txt (overrides the origin copy) ---
    if (url.pathname === "/robots.txt") {
      if (request.method === "GET" || request.method === "HEAD") {
        await recordVisit(env, request, url);
      }
      return textResponse(request.method === "HEAD" ? null : buildRobotsTxt(host), {
        headers: { "cache-control": "public, max-age=300" }
      });
    }

    // --- Owner-triggered IndexNow ping: /ops/indexnow?token=OWNER_TOKEN ---
    if (url.pathname === "/ops/indexnow") {
      if (!env.OWNER_TOKEN || url.searchParams.get("token") !== env.OWNER_TOKEN) {
        return jsonResponse({ ok: false, error: "unauthorized" }, { status: 401 });
      }
      if (!env.INDEXNOW_KEY) {
        return jsonResponse({ ok: false, error: "INDEXNOW_KEY not configured" }, { status: 400 });
      }
      const urls = CANONICAL_PATHS.map((p) => `https://${host}${p}`);
      const result = await pingIndexNow(host, env.INDEXNOW_KEY, urls);
      return jsonResponse({ ok: result.ok, ...result, host });
    }

    // --- Count the visit, then proxy to the static origin ---
    if ((request.method === "GET" || request.method === "HEAD") && shouldRecordVisit(url)) {
      await recordVisit(env, request, url);
    }

    return proxyToOrigin(request, url, env.ORIGIN || DEFAULT_ORIGIN);
  }
};
