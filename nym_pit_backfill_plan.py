NYM_TEAM_ID="121"
PIT_TEAM_ID="134"
TARGET_DATE="2026-08-09"
AWAY_TEAM="NYM"
HOME_TEAM="PIT"
AWAY_STARTER_ID="640455"  # Sean Manaea
HOME_STARTER_ID="683003"  # Jared Jones

# Deliberately broad enough to exceed the minimum team/bullpen coverage.
BACKFILL_START_DATE="2026-06-20"
BACKFILL_END_DATE="2026-08-08"

def dedupe_game_refs(*lists):
    seen={}
    for rows in lists:
        for g in rows:
            seen[str(g["game_pk"])]=g
    return sorted(seen.values(),key=lambda x:x["game_date"])
