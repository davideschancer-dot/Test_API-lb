"""
Nux Affiliate Leaderboard API – Test Suite
==========================================
Usage:
    export AFFILIATE_SECRET="your_secret_here"
    python test_leaderboard.py

Or set API_SECRET directly in the script below.
"""

import os
import json
from datetime import date, timedelta

import requests

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL    = "https://admin.chancer.bet/external/activities/leaderboard"
API_SECRET  = os.getenv("AFFILIATE_SECRET", "")   # set via env or replace here
# ─────────────────────────────────────────────────────────────────────────────

TODAY      = date.today()
PASS       = "\033[32mPASS\033[0m"
FAIL       = "\033[31mFAIL\033[0m"
WARN       = "\033[33mWARN\033[0m"
results    = []


def run(label, *, headers, body, expect_status, extra_checks=None):
    """Fire the request and evaluate the response."""
    print(f"\n{'─'*60}")
    print(f"TEST : {label}")
    print(f"BODY : {json.dumps(body, indent=2)}")
    print(f"HDR  : {headers}")

    try:
        resp = requests.get(BASE_URL, headers=headers, json=body, timeout=15)
    except requests.RequestException as exc:
        print(f"ERROR: {exc}")
        results.append((label, False, str(exc)))
        return None

    status_ok = resp.status_code == expect_status
    verdict   = PASS if status_ok else FAIL

    print(f"STATUS : {resp.status_code}  (expected {expect_status})  [{verdict}]")
    print(f"BODY   : {resp.text[:400]}")

    passed = status_ok
    notes  = []

    if extra_checks and resp.status_code == expect_status:
        for desc, fn in extra_checks:
            try:
                ok = fn(resp)
            except Exception as exc:
                ok = False
                desc = f"{desc} [exception: {exc}]"
            icon = PASS if ok else WARN
            print(f"CHECK  : {desc}  [{icon}]")
            if not ok:
                notes.append(desc)
                passed = False

    results.append((label, passed, "; ".join(notes)))
    return resp


def auth_headers():
    return {"X-Affiliate-Secret": API_SECRET, "Content-Type": "application/json"}

def no_auth_headers():
    return {"Content-Type": "application/json"}

def fmt(d: date) -> str:
    return d.isoformat()


# ── Test cases ────────────────────────────────────────────────────────────────

# 1. Happy path – 30-day window, explicit USD
date_to   = TODAY
date_from = TODAY - timedelta(days=29)   # inclusive 30-day window

run(
    "Happy path – 30-day window with explicit currency=USD",
    headers=auth_headers(),
    body={
        "date_from": fmt(date_from),
        "date_to":   fmt(date_to),
        "currency":  "USD",
    },
    expect_status=200,
    extra_checks=[
        ("Response is valid JSON",      lambda r: r.json() is not None),
        ("Response is a non-empty list", lambda r: isinstance(r.json(), list) and len(r.json()) > 0),
        ("First item has rank/player fields", lambda r: all(
            k in r.json()[0].get("items", [{}])[0] for k in ("rank", "player_id", "total_wager")
        ) if r.json() and r.json()[0].get("items") else True),
    ],
)

# 2. Large range – 90-day window
run(
    "Large range – 90-day window (expect 200)",
    headers=auth_headers(),
    body={
        "date_from": fmt(TODAY - timedelta(days=89)),
        "date_to":   fmt(date_to),
        "currency":  "USD",
    },
    expect_status=200,
    extra_checks=[
        ("Response is valid JSON", lambda r: r.json() is not None),
    ],
)

# 3. Missing auth header → 401
run(
    "Missing X-Affiliate-Secret header triggers 401",
    headers=no_auth_headers(),
    body={
        "date_from": fmt(date_from),
        "date_to":   fmt(date_to),
        "currency":  "USD",
    },
    expect_status=401,
    extra_checks=[
        ("Auth error message present", lambda r: bool(
            r.json().get("error") or r.json().get("message") or r.json().get("detail")
        )),
    ],
)

# 5. Omit currency – confirm USD default
resp_with    = requests.get(BASE_URL, headers=auth_headers(),
                            json={"date_from": fmt(date_from), "date_to": fmt(date_to), "currency": "USD"},
                            timeout=15)
resp_without = run(
    "Omit currency field – confirm USD default",
    headers=auth_headers(),
    body={
        "date_from": fmt(date_from),
        "date_to":   fmt(date_to),
        # currency intentionally omitted
    },
    expect_status=200,
    extra_checks=[
        ("Response is valid JSON", lambda r: r.json() is not None),
        # If both responses are 200 compare payloads as a signal of USD default
        ("Response currency is USD", lambda r: all(
            entry.get("currency") == "USD" for entry in r.json()
        ) if isinstance(r.json(), list) else r.json().get("currency") == "USD"),
    ],
)


# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'═'*60}")
print("SUMMARY")
print(f"{'═'*60}")
total  = len(results)
passed = sum(1 for _, ok, _ in results if ok)

for label, ok, notes in results:
    icon = PASS if ok else FAIL
    note = f"  ({notes})" if notes else ""
    print(f"  [{icon}]  {label}{note}")

print(f"\n{passed}/{total} tests passed")
print('═'*60)
