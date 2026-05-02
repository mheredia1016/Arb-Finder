from collections import defaultdict
from utils import implied_prob, american_to_decimal, similar

def find_arbs(rows, min_arb_percent=1.0, stake_amount=100):
    grouped=defaultdict(list)
    for r in rows:
        grouped[(r.sport, r.market)].append(r)
    alerts=[]
    for (sport, market), market_rows in grouped.items():
        # pair events by fuzzy name to handle Cubs @ Cardinals vs Cardinals v Cubs
        used=[]
        for r in market_rows:
            key=None
            for k in used:
                if similar(r.event, k)>82:
                    key=k; break
            if key is None:
                used.append(r.event); key=r.event
        event_groups=defaultdict(list)
        for r in market_rows:
            best=max(used, key=lambda k: similar(r.event,k)) if used else r.event
            if similar(r.event,best)>82:
                event_groups[best].append(r)
        for event, erows in event_groups.items():
            outcomes=defaultdict(list)
            for r in erows: outcomes[r.outcome].append(r)
            if len(outcomes) != 2: continue  # v1: 2-way markets only
            best=[]
            for outcome, ors in outcomes.items():
                best.append(max(ors, key=lambda x: american_to_decimal(x.american_odds)))
            total_prob=sum(implied_prob(x.american_odds) for x in best)
            arb_pct=(1-total_prob)*100
            if arb_pct >= min_arb_percent:
                decs=[american_to_decimal(x.american_odds) for x in best]
                stakes=[stake_amount/(d*total_prob) for d in decs]
                payout=stakes[0]*decs[0]
                profit=payout-stake_amount
                alerts.append({"sport":sport,"event":event,"market":market,"arb_pct":arb_pct,"stake_amount":stake_amount,"profit":profit,"legs":[{"book":b.book,"outcome":b.outcome,"odds":b.american_odds,"stake":stakes[i],"link":b.link} for i,b in enumerate(best)]})
    return sorted(alerts, key=lambda x:x["arb_pct"], reverse=True)
