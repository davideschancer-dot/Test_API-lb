# Affiliate Leaderboard

A lightweight Flask web app that fetches and displays affiliate leaderboard data from the Nux/Chancer API. Deployable to Fly.io with a custom domain.

---

## What it does

- Calls the Chancer affiliate leaderboard API and displays ranked player data in a table
- Supports filtering by date range and currency
- Accepts an affiliate secret key via the UI, allowing different affiliates to query their own data
- Displays affiliate metadata (ID, platform, currency, generated time)
- Top 3 players highlighted with gold, silver, and bronze rankings

---

## Project structure

```
api_lb_test/
├── app.py                  # Flask app and API logic
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container definition for deployment
├── fly.toml                # Fly.io configuration
├── test_leaderboard.py     # API test suite
├── templates/
│   └── index.html          # Frontend template
└── static/
    └── style.css           # Styles
```

---

## Running locally

**Prerequisites:** Python 3.12+, pip

**1. Install dependencies:**
```bash
pip install flask requests
```

**2. Set your affiliate secret:**
```bash
# Linux/macOS
export AFFILIATE_SECRET="your_secret_here"

# Windows PowerShell
$env:AFFILIATE_SECRET="your_secret_here"
```

**3. Start the app:**
```bash
python app.py
```

**4. Open in browser:**
```
http://localhost:5000
```

The secret can also be entered directly in the UI on the page, which will override the environment variable.

---

## Running the API test suite

```bash
export AFFILIATE_SECRET="your_secret_here"
python test_leaderboard.py
```

Tests covered:
| Test | Expected |
|---|---|
| Happy path – 30-day window, USD | 200 |
| Large range – 90-day window | 200 |
| Missing auth header | 401 |
| Omit currency – confirms USD default | 200 |

---

## Deploying to Fly.io

**Prerequisites:** [Fly CLI installed](https://fly.io/docs/hands-on/install-flyctl/), Fly.io account

**1. Log in:**
```bash
flyctl auth login
```

**2. Set the API secret:**
```bash
flyctl secrets set AFFILIATE_SECRET="your_secret_here"
```

**3. Deploy:**
```bash
flyctl deploy
```

**4. Add a custom domain:**
```bash
flyctl certs add yourdomain.com
```
Then add the CNAME record provided to your DNS. The SSL certificate provisions automatically.

---

## API reference

**Endpoint:** `GET https://admin.chancer.bet/external/activities/leaderboard`

**Auth:** `X-Affiliate-Secret` header

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `date_from` | string (YYYY-MM-DD) | Yes | Start of date range |
| `date_to` | string (YYYY-MM-DD) | Yes | End of date range |
| `currency` | string | No | Defaults to USD |

**Response fields:**

| Field | Description |
|---|---|
| `affiliate_id` | Affiliate identifier |
| `platform_type` | Platform (e.g. TRADITIONAL) |
| `currency` | Currency of wager amounts |
| `generated_at` | Timestamp the data was generated |
| `items` | Array of ranked players |
| `items[].rank` | Player rank |
| `items[].player_id` | Internal player ID |
| `items[].nickname` | Player display name |
| `items[].total_wager` | Total wager amount |
