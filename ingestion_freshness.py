from datetime import datetime,timezone
def parse_utc(ts):
    if isinstance(ts,datetime): return ts
    dt=datetime.fromisoformat(str(ts).replace("Z","+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
def age_minutes(fetched_at_utc,now_utc):
    return (parse_utc(now_utc)-parse_utc(fetched_at_utc)).total_seconds()/60
def is_fresh(fetched_at_utc,now_utc,max_age_minutes):
    return age_minutes(fetched_at_utc,now_utc) <= float(max_age_minutes)
