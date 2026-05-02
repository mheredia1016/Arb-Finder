# Sportsbook Arbitrage Bot - Live JSON Test

Railway/Discord bot that tries public sportsbook JSON endpoints and alerts on 2-way moneyline arbitrage.

## Important
These sportsbook endpoints are unofficial front-end JSON endpoints. They may break, be region-sensitive, or return no data. This bot does not log in, bypass captchas, or automate betting.

BetMGM and Caesars do not provide a stable self-serve public odds API. Their adapters are included, but you must paste the public JSON URL you see in your own browser Network tab. If the URL is blank or fails, that book is skipped and the bot keeps running.

## Railway variables
```env
DISCORD_WEBHOOK_URL=your_private_channel_webhook
USE_DEMO_DATA=false
POLL_SECONDS=60
MIN_ARB_PERCENT=1.0
STAKE_AMOUNT=100
COOLDOWN_MINUTES=10
SPORTS=MLB,NBA
BOOKS=draftkings,fanduel,betmgm,caesars
FANDUEL_REGION=il
```

## Test first
Set:
```env
USE_DEMO_DATA=true
```
You should get a test arb alert. Then set it to false.

## DraftKings
DraftKings defaults are already included through event group IDs:
```env
DRAFTKINGS_EVENTGROUPS_MLB=84240
DRAFTKINGS_EVENTGROUPS_NBA=42648
DRAFTKINGS_EVENTGROUPS_NHL=42133
DRAFTKINGS_EVENTGROUPS_NFL=88808
```

## FanDuel override
If FanDuel returns 0 rows, open FanDuel in Chrome > Network > Fetch/XHR and look for `content-managed-page`. Copy the full URL into:
```env
FANDUEL_URL_MLB=...
FANDUEL_URL_NBA=...
```

## BetMGM + Caesars setup
1. Open the sportsbook league page in Chrome.
2. Open DevTools > Network > Fetch/XHR.
3. Refresh the page.
4. Click requests that return JSON and contain words like `event`, `market`, `fixture`, `coupon`, `competition`, `offer`, or `odds`.
5. Copy the full request URL.
6. Paste it into Railway:

```env
BETMGM_URL_MLB=...
CAESARS_URL_MLB=...
```

The included generic parser looks for moneyline markets and common runner/outcome fields.

## Run locally
```bash
pip install -r requirements.txt
python main.py
```
