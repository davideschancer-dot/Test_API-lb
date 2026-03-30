# Affiliate Leaderboard Portal

Internal web portal for viewing affiliate leaderboard data from the So Nux platform through the affiliate leaderboard API.

## Overview

This application is intended for internal use only. When a valid API key is entered in the web portal at `lb.cgboa.info`, the app retrieves and displays the highest-wagered players for the relevant affiliate.

The portal supports:

- API key entry through the web interface
- Adjustable date ranges
- Currency selection
- Export of leaderboard table data for admin use

The web server is hosted on Fly.io.

## Intended Use

This tool is provided for internal operational and admin purposes only. It is not intended for public distribution or external customer use.

Support and uptime are provided on a best-effort SLA basis.

## Ownership And Distribution

This application remains the property of Chancer Group LTD.

Public distribution, reuse, or disclosure of this application is forbidden unless explicit consent has been approved by Chancer Group management.

## Technical Summary

- Backend: Flask
- Hosting: Fly.io
- Portal URL: `lb.cgboa.info`
- Primary function: retrieve and display highest-wagered affiliate players from the affiliate leaderboard API

## Local Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python app.py
```

By default, the app runs locally and can be opened in a browser for testing.
