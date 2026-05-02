import os
from books.json_adapter import fetch_from_url

# Caesars does not publish a self-serve official odds API. Use only URLs you can access publicly
# without login/captcha from the browser Network tab. This adapter parses common JSON shapes.

def fetch(sport):
    sport = sport.upper()
    url = os.getenv(f"CAESARS_URL_{sport}") or os.getenv("CAESARS_URL")
    if not url:
        return []
    return fetch_from_url("Caesars", sport, url, referer="https://www.caesars.com/sportsbook-and-casino/")
