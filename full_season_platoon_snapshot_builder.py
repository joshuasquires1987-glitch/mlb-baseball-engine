import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from historical_platoon_probe import enrich_snapshot

def load_jsonl(path):
    rows=[]
    with open(path,"r",encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def write_jsonl(rows,path):
    with open(path,"w",encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row,separators=(",",":"))+"\n")

def build_all(raw_rows,max_workers=16,fetcher=None):
    enriched=[]
    failures=[]

    def task(row):
        try:
            kwargs={}
            if fetcher is not None:
                kwargs["fetcher"]=fetcher
            return enrich_snapshot(row,**kwargs)
        except Exception as e:
            return None,{
                "game_pk":str(row["game_pk"]),
                "reason":f"request-error:{type(e).__name__}",
                "detail":str(e)[:300],
            }

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures=[pool.submit(task,row) for row in raw_rows]
        for i,fut in enumerate(as_completed(futures),1):
            row,err=fut.result()
            if row is not None:
                if row.get("captured_before_first_pitch") is not True:
                    err={"game_pk":str(row.get("game_pk")),"reason":"certification-lost"}
                elif row.get("platoon_lineup_delta") is None:
                    err={"game_pk":str(row.get("game_pk")),"reason":"delta-missing-after-enrichment"}
                else:
                    enriched.append(row)
            if err is not None:
                failures.append(err)
            if i % 100 == 0 or i == len(futures):
                print(
                    f"processed={i}/{len(futures)} "
                    f"enriched={len(enriched)} failures={len(failures)}",
                    flush=True,
                )

    enriched.sort(key=lambda r:(r.get("scheduled_game_time_utc") or "",str(r["game_pk"])))
    failures.sort(key=lambda r:str(r.get("game_pk") or ""))
    return enriched,failures
