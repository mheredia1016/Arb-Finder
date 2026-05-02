import os
from books.json_adapter import fetch_from_url

# BetMGM does not publish a self-serve official odds API. Use only URLs you can access publicly
# without login/captcha from the browser Network tab. This adapter parses common JSON shapes.

def fetch(sport):
    sport = sport.upper()
    url = os.getenv(f"BETMGM_URL_{sport}") or os.getenv("BETMGM_URL")
    if not url:
        return []
    return fetch_from_url("BetMGM", sport, url, referer="https://sports.betmgm.com/")
