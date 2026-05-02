import os, time, logging
from dotenv import load_dotenv
from utils import env_bool
from arb_finder import find_arbs
from discord_alert import post_alert

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

WEBHOOK=os.getenv("DISCORD_WEBHOOK_URL")
POLL=int(os.getenv("POLL_SECONDS","60"))
MIN_ARB=float(os.getenv("MIN_ARB_PERCENT","1.0"))
STAKE=float(os.getenv("STAKE_AMOUNT","100"))
COOLDOWN=int(os.getenv("COOLDOWN_MINUTES","10"))*60
SPORTS=[x.strip().upper() for x in os.getenv("SPORTS","MLB,NBA").split(",") if x.strip()]
BOOKS=[x.strip().lower() for x in os.getenv("BOOKS","draftkings,fanduel,betmgm,caesars").split(",") if x.strip()]
USE_DEMO=env_bool("USE_DEMO_DATA", False)
last_alert={}

def fetch_all():
    if USE_DEMO:
        from books.demo import fetch
        return fetch("MLB")
    rows=[]
    for sport in SPORTS:
        for book in BOOKS:
            try:
                mod=__import__(f"books.{book}", fromlist=["fetch"])
                got=mod.fetch(sport)
                logging.info("%s %s rows=%s", book, sport, len(got))
                rows.extend(got)
                time.sleep(2)
            except Exception as e:
                logging.warning("%s %s failed: %s", book, sport, e)
    return rows

def should_send(alert):
    key=f'{alert["sport"]}|{alert["event"]}|{alert["market"]}|'+"|".join(sorted([l["book"]+l["outcome"]+str(l["odds"]) for l in alert["legs"]]))
    now=time.time()
    if now-last_alert.get(key,0) < COOLDOWN: return False
    last_alert[key]=now
    return True

def run_once():
    rows=fetch_all()
    logging.info("active books=%s sports=%s total odds rows=%s", BOOKS, SPORTS, len(rows))
    alerts=find_arbs(rows, MIN_ARB, STAKE)
    logging.info("arbs found=%s", len(alerts))
    for a in alerts[:5]:
        if WEBHOOK and should_send(a):
            post_alert(WEBHOOK, a)
        elif not WEBHOOK:
            logging.info("ARB: %s", a)

if __name__ == "__main__":
    while True:
        run_once()
        time.sleep(POLL)
