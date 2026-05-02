import requests

def post_alert(webhook_url, alert):
    lines=[]
    for leg in alert["legs"]:
        odds = f'+{leg["odds"]}' if leg["odds"]>0 else str(leg["odds"])
        link = f' — {leg["link"]}' if leg.get("link") else ''
        lines.append(f'**{leg["outcome"]}** {odds} at **{leg["book"]}**\nStake: `${leg["stake"]:.2f}`{link}')
    embed={
        "title":"🔥 Arbitrage Found",
        "description":f'**{alert["sport"]} — {alert["event"]}**\nMarket: `{alert["market"]}`\nArb: **{alert["arb_pct"]:.2f}%**\nTotal stake: `${alert["stake_amount"]:.2f}`\nGuaranteed profit: `${alert["profit"]:.2f}`\n\n'+'\n\n'.join(lines),
        "color":16753920
    }
    r=requests.post(webhook_url, json={"embeds":[embed]}, timeout=15)
    r.raise_for_status()
