import os, re, time, requests
from rapidfuzz import fuzz

def env_bool(name, default=False):
    return os.getenv(name, str(default)).lower() in ("1","true","yes","y","on")

def american_to_decimal(odds:int)->float:
    odds=int(odds)
    return 1 + (odds/100 if odds>0 else 100/abs(odds))

def implied_prob(odds:int)->float:
    return 1 / american_to_decimal(odds)

def norm(s:str)->str:
    s=(s or "").lower()
    s=re.sub(r"[^a-z0-9 ]+"," ",s)
    s=re.sub(r"\b(the|fc|sc|club)\b"," ",s)
    return re.sub(r"\s+"," ",s).strip()

def similar(a,b):
    return fuzz.token_sort_ratio(norm(a), norm(b))

SESSION=requests.Session()
SESSION.headers.update({
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Accept":"application/json,text/plain,*/*",
    "Accept-Language":"en-US,en;q=0.9",
})

def get_json(url, timeout=20, referer=None):
    headers={}
    if referer: headers["Referer"]=referer
    r=SESSION.get(url, timeout=timeout, headers=headers)
    r.raise_for_status()
    return r.json()
