import csv
import io
import os
from datetime import date, timedelta

import requests
from flask import Flask, render_template, request, Response

app = Flask(__name__)

API_URL    = "https://admin.chancer.bet/external/activities/leaderboard"
API_SECRET = os.getenv("AFFILIATE_SECRET", "")
CURRENCIES = ["USD", "EUR", "GBP", "AUD", "CAD"]


def fetch_leaderboard(date_from, date_to, currency, secret):
    payload = {"date_from": date_from, "date_to": date_to}
    if currency:
        payload["currency"] = currency

    resp = requests.get(
        API_URL,
        headers={
            "X-Affiliate-Secret": secret,
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


@app.route("/", methods=["GET"])
def index():
    # Default: last 30 days
    date_to   = date.today().isoformat()
    date_from = (date.today() - timedelta(days=29)).isoformat()
    currency  = "USD"

    # Override with query params if provided
    if request.args.get("date_from"):
        date_from = request.args["date_from"]
    if request.args.get("date_to"):
        date_to = request.args["date_to"]
    if request.args.get("currency"):
        currency = request.args["currency"]
    secret = request.args.get("secret") or API_SECRET

    error     = None
    entries   = []
    meta      = {}

    try:
        data = fetch_leaderboard(date_from, date_to, currency, secret)
        if data:
            meta    = {k: v for k, v in data[0].items() if k != "items"}
            entries = data[0].get("items", [])
    except requests.HTTPError as e:
        error = f"API error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        error = str(e)

    return render_template(
        "index.html",
        entries=entries,
        meta=meta,
        error=error,
        date_from=date_from,
        date_to=date_to,
        currency=currency,
        currencies=CURRENCIES,
        secret=secret,
    )


@app.route("/export-csv", methods=["GET"])
def export_csv():
    date_to   = date.today().isoformat()
    date_from = (date.today() - timedelta(days=29)).isoformat()
    currency  = "USD"

    if request.args.get("date_from"):
        date_from = request.args["date_from"]
    if request.args.get("date_to"):
        date_to = request.args["date_to"]
    if request.args.get("currency"):
        currency = request.args["currency"]
    secret = request.args.get("secret") or API_SECRET

    data = fetch_leaderboard(date_from, date_to, currency, secret)
    entries = data[0].get("items", []) if data else []
    meta    = {k: v for k, v in data[0].items() if k != "items"} if data else {}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Rank", "Player ID", "Nickname", f"Total Wager ({meta.get('currency', currency)})"])
    for item in entries:
        writer.writerow([item["rank"], item["player_id"], item["nickname"], item["total_wager"]])

    filename = f"leaderboard_{date_from}_to_{date_to}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
