import os
from models import OddsRow
from utils import get_json

GROUPS={"MLB":os.getenv("DRAFTKINGS_EVENTGROUPS_MLB","84240"),"NBA":os.getenv("DRAFTKINGS_EVENTGROUPS_NBA","42648"),"NHL":os.getenv("DRAFTKINGS_EVENTGROUPS_NHL","42133"),"NFL":os.getenv("DRAFTKINGS_EVENTGROUPS_NFL","88808")}
URL="https://sportsbook-nash.draftkings.com/sites/US-SB/api/v5/eventgroups/{group_id}?format=json"

def _teams(ev):
    name=ev.get("name") or ev.get("eventName") or ""
    participants=ev.get("participants") or []
    names=[p.get("name") or p.get("fullName") for p in participants if p.get("name") or p.get("fullName")]
    return " vs ".join(names[:2]) if len(names)>=2 else name

def _price(out):
    for k in ("oddsAmerican","americanOdds","displayOdds","odds"):
        v=out.get(k)
        if isinstance(v, dict): v=v.get("american") or v.get("americanOdds")
        if v is not None:
            s=str(v).replace("+","")
            try: return int(float(s))
            except: pass
    return None

def fetch(sport):
    group_id=GROUPS.get(sport.upper())
    if not group_id: return []
    data=get_json(URL.format(group_id=group_id), referer="https://sportsbook.draftkings.com/")
    rows=[]
    events={str(e.get("id") or e.get("eventId")):e for e in data.get("events",[])}
    cats=data.get("eventGroup",{}).get("offerCategories",[]) or data.get("offerCategories",[])
    for cat in cats:
        for sub in cat.get("offerSubcategoryDescriptors",[]) or cat.get("offerSubcategories",[]):
            for offer_group in sub.get("offerSubcategory",{}).get("offers",[]) or sub.get("offers",[]):
                for offer in offer_group if isinstance(offer_group, list) else [offer_group]:
                    label=(offer.get("label") or offer.get("name") or "").lower()
                    if label not in ("moneyline","money line"): continue
                    ev=events.get(str(offer.get("eventId"))) or {}
                    event_name=_teams(ev) or offer.get("eventName") or "Unknown Event"
                    for out in offer.get("outcomes",[]):
                        odds=_price(out)
                        name=out.get("label") or out.get("name") or out.get("participant")
                        if odds and name:
                            rows.append(OddsRow("DraftKings",sport.upper(),event_name,"moneyline",name,int(odds),out.get("link") or ""))
    return rows
