#!/usr/bin/env python3
# Guard runner — prevents regressions by restoring last good items.json

import json, re, shutil
from pathlib import Path
from datetime import datetime

ALLOWED_SOURCES = {
    "ESPN","Yahoo Sports","Sports Illustrated","CBS Sports","SB Nation",
    "Bleacher Report","The Athletic","NFL.com","PFF","Pro-Football-Reference",
    "NBC Sports","USA Today",
    "Philadelphia Eagles","Philadelphia Inquirer","PhillyVoice",
    "NBC Sports Philadelphia","94WIP","Crossing Broad","Bleeding Green Nation",
    "Reddit — r/eagles",
}

REQUIRED_BUTTONS = {
  "Schedule","Roster","Depth Chart","Injury Report","Team Shop","Tickets",
  "Reddit","Bleacher Report","ESPN Team","Yahoo Team","PFF Team Page",
  "Pro-Football-Reference","NFL Power Rankings","Stats","Standings"
}

ROOT = Path(__file__).resolve().parent
ITEMS = ROOT/"items.json"
BACKUP = ROOT/"items.last-good.json"
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

def now(): return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def read_json(p):
    with open(p,"r",encoding="utf-8") as f: return json.load(f)

def write_json(p, obj):
    tmp = p.with_suffix(".tmp")
    with open(tmp,"w",encoding="utf-8") as f: json.dump(obj,f,ensure_ascii=False,indent=2)
    tmp.replace(p)

def validate(payload):
    errs=[]
    if not payload.get("updated") or not ISO.match(str(payload["updated"])): errs.append("bad updated")
    labels = { (x.get("label") or "").strip() for x in (payload.get("links") or []) if isinstance(x,dict) }
    miss = [b for b in REQUIRED_BUTTONS if b not in labels]
    if miss: errs.append("missing buttons: "+", ".join(miss))
    items = payload.get("items") or []
    if not items: errs.append("no items")
    for i,it in enumerate(items[:100],1):
        if (it.get("source") or "") not in ALLOWED_SOURCES: errs.append(f"bad source @{i}:{it.get('source')}")
        if not it.get("published") or not ISO.match(str(it["published"])): errs.append(f"bad published @{i}")
    return errs

def run_collect():
    import importlib.util
    spec = importlib.util.spec_from_file_location("collect", str(ROOT/"collect.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod,"main"): mod.main()

def main():
    if ITEMS.exists() and not BACKUP.exists(): shutil.copyfile(ITEMS,BACKUP)
    run_collect()
    try:
        payload = read_json(ITEMS)
    except Exception as e:
        if BACKUP.exists(): shutil.copyfile(BACKUP,ITEMS)
        write_json(ROOT/"health.json",{"time":now(),"status":"read_error","detail":str(e)})
        return
    errs = validate(payload)
    if errs:
        if BACKUP.exists(): shutil.copyfile(BACKUP,ITEMS)
        write_json(ROOT/"health.json",{"time":now(),"status":"invalid","errors":errs})
    else:
        shutil.copyfile(ITEMS,BACKUP)
        write_json(ROOT/"health.json",{"time":now(),"status":"ok","items":len(payload.get("items",[]))})

if __name__=="__main__":
    main()