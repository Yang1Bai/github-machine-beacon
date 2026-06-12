from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
TRAFFIC_PATH = ROOT / "data" / "traffic.json"
REPO = "Yang1Bai/github-machine-beacon"
API_BASE = f"https://api.github.com/repos/{REPO}"


def token_from_env_or_gh() -> str | None:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        return token
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or None
    except Exception:
        return None


def gh_get(path: str, token: str) -> object:
    request = Request(
        f"{API_BASE}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "github-machine-beacon-traffic-updater",
        },
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def existing_payload() -> dict:
    if TRAFFIC_PATH.exists():
        return json.loads(TRAFFIC_PATH.read_text(encoding="utf-8"))
    return {}


def daily_rows(payload: dict, key: str) -> list[dict]:
    return [
        {
            "timestamp": row.get("timestamp"),
            "count": int(row.get("count", 0)),
            "uniques": int(row.get("uniques", 0)),
        }
        for row in payload.get(key, [])
    ]


def normalize_referrers(rows: list[dict]) -> list[dict]:
    return [
        {
            "referrer": row.get("referrer", ""),
            "count": int(row.get("count", 0)),
            "uniques": int(row.get("uniques", 0)),
        }
        for row in rows
    ]


def normalize_paths(rows: list[dict]) -> list[dict]:
    return [
        {
            "path": row.get("path", ""),
            "title": row.get("title", ""),
            "count": int(row.get("count", 0)),
            "uniques": int(row.get("uniques", 0)),
        }
        for row in rows
    ]


def build_payload(token: str) -> dict:
    views = gh_get("/traffic/views", token)
    clones = gh_get("/traffic/clones", token)
    referrers = gh_get("/traffic/popular/referrers", token)
    paths = gh_get("/traffic/popular/paths", token)
    return {
        "schema_version": "github-machine-beacon/traffic/v1",
        "repo": REPO,
        "source": "GitHub Traffic API",
        "source_scope": "repository traffic, not raw GitHub Pages server logs",
        "coverage": "last_14_days",
        "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "views": {
            "count": int(views.get("count", 0)),
            "uniques": int(views.get("uniques", 0)),
            "daily": daily_rows(views, "views"),
        },
        "clones": {
            "count": int(clones.get("count", 0)),
            "uniques": int(clones.get("uniques", 0)),
            "daily": daily_rows(clones, "clones"),
        },
        "referrers": normalize_referrers(referrers),
        "popular_paths": normalize_paths(paths),
        "visitor_classification": {
            "machine_visits": None,
            "human_visits": None,
            "status": "not_available_without_request_logs",
            "reason": "GitHub Traffic API does not expose user-agent level data, and GitHub Pages does not provide raw request logs to this static site.",
        },
    }


def main() -> None:
    token = token_from_env_or_gh()
    if not token:
        raise SystemExit("No GitHub token available for traffic update.")
    else:
        try:
            payload = build_payload(token)
            payload["last_update_status"] = "success"
        except (HTTPError, URLError, TimeoutError) as exc:
            if os.getenv("GITHUB_ACTIONS") == "true":
                raise
            payload = existing_payload()
            payload["last_update_status"] = f"failed_{type(exc).__name__}"

    TRAFFIC_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {TRAFFIC_PATH}")


if __name__ == "__main__":
    main()
