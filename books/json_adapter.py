from __future__ import annotations
from typing import Any, Iterable
from models import OddsRow
from utils import get_json

MONEYLINE_NAMES = {
    "moneyline", "money line", "money_line", "ml", "match winner", "winner", "game lines - money line"
}


def walk(x: Any) -> Iterable[dict]:
    if isinstance(x, dict):
        yield x
        for v in x.values():
            yield from walk(v)
    elif isinstance(x, list):
        for v in x:
            yield from walk(v)


def pick_odds(obj: dict) -> int | None:
    keys = (
        "americanOdds", "oddsAmerican", "american", "priceAmerican", "odds",
        "price", "displayOdds", "trueOdds", "line", "numerator"
    )
    for k in keys:
        v = obj.get(k)
        if isinstance(v, dict):
            v = v.get("american") or v.get("americanOdds") or v.get("oddsAmerican") or v.get("value")
        if v is None:
            continue
        # Skip spread/total points like 7.5 by requiring sportsbook-style values.
        try:
            s = str(v).strip().replace("+", "")
            n = int(float(s))
            if abs(n) >= 100:
                return n
        except Exception:
            pass
    return None


def pick_name(obj: dict) -> str | None:
    for k in ("name", "label", "title", "runnerName", "selectionName", "participantName", "teamName", "outcomeName"):
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    participant = obj.get("participant")
    if isinstance(participant, dict):
        return pick_name(participant)
    return None


def pick_event(obj: dict, default: str = "Unknown Event") -> str:
    for k in ("eventName", "event", "fixtureName", "competitionName", "name", "title"):
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    competitors = obj.get("competitors") or obj.get("participants") or obj.get("teams")
    if isinstance(competitors, list):
        names = []
        for c in competitors:
            if isinstance(c, dict):
                n = pick_name(c)
                if n:
                    names.append(n)
        if len(names) >= 2:
            return f"{names[0]} vs {names[1]}"
    return default


def is_moneyline_market(obj: dict) -> bool:
    candidates = []
    for k in ("marketName", "marketType", "marketTypeName", "bettingType", "wagerType", "name", "title", "label", "type"):
        v = obj.get(k)
        if isinstance(v, str):
            candidates.append(v.lower().strip())
    return any(c in MONEYLINE_NAMES or "moneyline" in c or c == "ml" for c in candidates)


def rows_from_json(book: str, sport: str, data: Any) -> list[OddsRow]:
    rows: list[OddsRow] = []

    # Pattern 1: market objects containing selections/runners/outcomes.
    for obj in walk(data):
        if not is_moneyline_market(obj):
            continue
        runners = obj.get("runners") or obj.get("outcomes") or obj.get("selections") or obj.get("participants") or []
        if not isinstance(runners, list):
            continue
        event_name = pick_event(obj)
        for r in runners:
            if not isinstance(r, dict):
                continue
            odds = pick_odds(r)
            name = pick_name(r)
            if odds and name:
                rows.append(OddsRow(book, sport.upper(), event_name, "moneyline", name, odds, r.get("url") or r.get("link") or ""))

    # Pattern 2: flattened selection objects with an attached market name.
    for obj in walk(data):
        if not any(k in obj for k in ("americanOdds", "oddsAmerican", "priceAmerican", "american")):
            continue
        market_text = " ".join(str(obj.get(k, "")) for k in ("marketName", "marketType", "bettingType", "wagerType", "type")).lower()
        if "moneyline" not in market_text and "money line" not in market_text and market_text.strip() != "ml":
            continue
        odds = pick_odds(obj)
        name = pick_name(obj)
        if odds and name:
            rows.append(OddsRow(book, sport.upper(), pick_event(obj), "moneyline", name, odds, obj.get("url") or obj.get("link") or ""))

    # De-dupe exact rows.
    seen = set()
    out = []
    for r in rows:
        key = (r.book, r.sport, r.event, r.market, r.outcome, r.american_odds)
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def fetch_from_url(book: str, sport: str, url: str, referer: str = "") -> list[OddsRow]:
    data = get_json(url, referer=referer or None)
    return rows_from_json(book, sport, data)
