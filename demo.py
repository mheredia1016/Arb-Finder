from models import OddsRow

def fetch(_sport):
    return [
        OddsRow("DraftKings","MLB","Cubs vs Cardinals","moneyline","Cubs",125),
        OddsRow("DraftKings","MLB","Cubs vs Cardinals","moneyline","Cardinals",-130),
        OddsRow("FanDuel","MLB","Cardinals vs Cubs","moneyline","Cubs",110),
        OddsRow("FanDuel","MLB","Cardinals vs Cubs","moneyline","Cardinals",-105),
    ]
