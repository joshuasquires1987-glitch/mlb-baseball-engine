import re

def parse_wind(wind_text):
    if wind_text is None:
        return None,None
    s=str(wind_text).strip().lower()
    m=re.search(r"(\d+(?:\.\d+)?)\s*mph",s)
    if not m:
        return None,None
    mph=float(m.group(1))
    if "out" in s:
        return mph,0.0
    if "in" in s:
        return 0.0,mph
    return 0.0,0.0

def parse_pregame_weather(game_data):
    w=(game_data or {}).get("weather") or {}
    temp=w.get("temp")
    out_mph,in_mph=parse_wind(w.get("wind"))
    if temp is None or out_mph is None or in_mph is None:
        return None
    return {
        "temp_f":float(temp),
        "wind_out_mph":out_mph,
        "wind_in_mph":in_mph,
        "condition":w.get("condition"),
    }
