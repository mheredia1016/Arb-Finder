import os
from models import OddsRow
from utils import get_json

# These are the common FanDuel front-end JSON page endpoints. They can be region-sensitive.
REGION=os.getenv("FANDUEL_REGION","il").lower()
DEFAULTS={
 "MLB": f"https://sbapi.{REGION}.sportsbook.fanduel.com/api/content-managed-page?page=CUSTOM&customPageId=mlb&pbHorizontal=false&_ak=FhMFpcPWXMeyZxOx",
 "NBA": f"https://sbapi.{REGION}.sportsbook.fanduel.com/api/content-managed-page?page=CUSTOM&customPageId=nba&pbHorizontal=false&_ak=FhMFpcPWXMeyZxOx",
 "NHL": f"https://sbapi.{REGION}.sportsbook.fanduel.com/api/content-managed-page?page=CUSTOM&customPageId=nhl&pbHorizontal=false&_ak=FhMFpcPWXMeyZxOx",
 "NFL": f"https://sbapi.{REGION}.sportsbook.fanduel.com/api/content-managed-page?page=CUSTOM&customPageId=nfl&pbHorizontal=false&_ak=FhMFpcPWXMeyZxOx",
}

def _walk(x):
    if isinstance(x, dict):
        yield x
        for v in x.values(): yield from _walk(v)
    elif isinstance(x, list):
        for v in x: yield from _walk(v)

def _odds(obj):
    for k in ("americanOdds","oddsAmerican","price","trueOdds","displayOdds"):
        v=obj.get(k)
        if isinstance(v, dict): v=v.get("americanOdds") or v.get("american")
        if v is not None:
            s=str(v).replace("+","")
            try: return int(float(s))
            except: pass
    return None

def fetch(sport):
    sport=sport.upper()
    url=os.getenv(f"FANDUEL_URL_{sport}") or DEFAULTS.get(sport)
    if not url: return []
    data=get_json(url, referer="https://sportsbook.fanduel.com/")
    rows=[]
    # FanDuel structure moves around, so this parser looks for runner/outcome objects with market labels.
    for obj in _walk(data):
        market=str(obj.get("marketName") or obj.get("marketType") or obj.get("name") or obj.get("title") or "").lower()
        if market not in ("moneyline","money line"):
            continue
        event=obj.get("eventName") or obj.get("event") or obj.get("competitionName") or obj.get("fixtureName") or "Unknown Event"
        runners=obj.get("runners") or obj.get("outcomes") or obj.get("selections") or []
        if not isinstance(runners,list): continue
        for r in runners:
            if not isinstance(r,dict): continue
            odds=_odds(r)
            name=r.get("runnerName") or r.get("selectionName") or r.get("name") or r.get("label")
            if odds and name:
                rows.append(OddsRow("FanDuel",sport,event,"moneyline",name,int(odds),r.get("url") or r.get("link") or ""))
    return rows
