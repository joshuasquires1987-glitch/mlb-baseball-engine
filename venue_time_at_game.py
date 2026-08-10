from datetime import datetime
from zoneinfo import ZoneInfo

def _dt(value):
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))

def utc_offset_hours_at_game(timezone_id, game_time_utc):
    dt = _dt(game_time_utc)
    if dt.tzinfo is None:
        raise ValueError("game_time_utc must be timezone-aware")
    local = dt.astimezone(ZoneInfo(timezone_id))
    offset = local.utcoffset()
    if offset is None:
        raise ValueError(f"unable to resolve offset for {timezone_id}")
    return offset.total_seconds() / 3600.0

def venue_offset_record(registry_row, game_time_utc):
    return {
        **registry_row,
        "utc_offset_hours": utc_offset_hours_at_game(
            registry_row["timezone_id"],
            game_time_utc,
        ),
    }
