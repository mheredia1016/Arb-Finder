from dataclasses import dataclass

@dataclass(frozen=True)
class OddsRow:
    book: str
    sport: str
    event: str
    market: str
    outcome: str
    american_odds: int
    link: str = ""
