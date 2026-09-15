"""Pull real GitHub activity and rewrite the live_signal block in README.md.

Runs in CI (see .github/workflows/live-signal.yml) on a schedule. Uses only
the stdlib so the workflow needs no dependency install step.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import urllib.request

START_MARKER = "<!-- LIVE_SIGNAL:START -->"
END_MARKER = "<!-- LIVE_SIGNAL:END -->"

GRAPHQL_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def api_request(url: str, token: str, data: dict | None = None) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "live-signal-script",
    }
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_contribution_days(login: str, token: str) -> list[dict]:
    result = api_request(
        "https://api.github.com/graphql",
        token,
        {"query": GRAPHQL_QUERY, "variables": {"login": login}},
    )
    if "errors" in result:
        raise RuntimeError(result["errors"])
    weeks = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [d for week in weeks for d in week["contributionDays"]]
    days.sort(key=lambda d: d["date"])
    return days


def current_streak(days: list[dict]) -> int:
    streak = 0
    for day in reversed(days):
        if day["contributionCount"] > 0:
            streak += 1
        else:
            break
    return streak


def contributions_this_week(days: list[dict]) -> int:
    today = dt.date.today()
    week_ago = today - dt.timedelta(days=6)
    return sum(
        d["contributionCount"]
        for d in days
        if week_ago <= dt.date.fromisoformat(d["date"]) <= today
    )


def last_active_at(days: list[dict]) -> str:
    for day in reversed(days):
        if day["contributionCount"] > 0:
            return day["date"]
    return "unknown"


def repos_touched_7d(login: str, token: str) -> int:
    result = api_request(
        f"https://api.github.com/users/{login}/repos?sort=pushed&direction=desc&per_page=100",
        token,
    )
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)
    count = 0
    for repo in result:
        pushed_at = repo.get("pushed_at")
        if not pushed_at:
            continue
        pushed = dt.datetime.strptime(pushed_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
        if pushed >= cutoff:
            count += 1
    return count


def render_block(streak: int, week_total: int, repos_7d: int, last_active: str) -> str:
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
    rows = [
        ("current_streak_days", str(streak), now),
        ("contributions_this_week", str(week_total), ""),
        ("repos_touched_7d", str(repos_7d), ""),
        ("last_active_at", last_active, ""),
    ]
    lines = [
        "```console",
        "$ python -m notworle.stats --source github --live",
        "",
        "  metric                        value       updated (UTC)",
        "  ─────────────────────────────  ──────────  ────────────────────",
    ]
    for name, value, ts in rows:
        lines.append(f"  {name:<30}  {value:<10}  {ts}".rstrip())
    lines += [
        "",
        "  source: github graphql api · auto-regenerated every 12h",
        "```",
    ]
    return "\n".join(lines)


def main() -> None:
    login = os.environ["GH_USERNAME"]
    token = os.environ["GITHUB_TOKEN"]
    readme_path = os.environ.get("README_PATH", "README.md")

    days = fetch_contribution_days(login, token)
    block = render_block(
        streak=current_streak(days),
        week_total=contributions_this_week(days),
        repos_7d=repos_touched_7d(login, token),
        last_active=last_active_at(days),
    )

    with open(readme_path, encoding="utf-8") as f:
        readme = f.read()

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL
    )
    if not pattern.search(readme):
        print("live_signal markers not found in README.md", file=sys.stderr)
        sys.exit(1)

    updated = pattern.sub(f"{START_MARKER}\n{block}\n{END_MARKER}", readme)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(updated)


if __name__ == "__main__":
    main()
