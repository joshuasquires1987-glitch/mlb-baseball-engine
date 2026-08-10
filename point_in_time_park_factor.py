from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

MIN_VENUE_GAMES = 20
LOOKBACK_DAYS = 730
SHRINK_GAMES = 40

def _dt(x):
    if isinstance(x, datetime):
        v=x
    else:
        v=datetime.fromisoformat(str(x).replace("Z","+00:00"))
    if v.tzinfo is None:
        v=v.replace(tzinfo=timezone.utc)
    return v.astimezone(timezone.utc)

def _total_runs(game):
    h=game.get("home_runs")
    a=game.get("away_runs")
    if h is None or a is None:
        return None
    return float(h)+float(a)

def _mean(values):
    return sum(values)/len(values) if values else None

def shrink_to_neutral(raw_factor, venue_games, shrink_games=SHRINK_GAMES):
    n=float(venue_games)
    w=n/(n+float(shrink_games))
    return 1.0 + w*(float(raw_factor)-1.0)

def build_point_in_time_records(
    games,
    target_start_date,
    target_end_date,
    min_venue_games=MIN_VENUE_GAMES,
    lookback_days=LOOKBACK_DAYS,
    shrink_games=SHRINK_GAMES,
):
    ordered=sorted(
        [g for g in games if g.get("game_time_utc")],
        key=lambda g:(_dt(g["game_time_utc"]),str(g["game_pk"]))
    )

    league=deque()
    venue=defaultdict(deque)
    records=[]
    skipped=[]

    start=datetime.fromisoformat(target_start_date).date()
    end=datetime.fromisoformat(target_end_date).date()

    for g in ordered:
        now=_dt(g["game_time_utc"])
        cutoff=now-timedelta(days=lookback_days)

        while league and league[0][0] < cutoff:
            league.popleft()
        for vid in list(venue):
            q=venue[vid]
            while q and q[0][0] < cutoff:
                q.popleft()

        game_date=now.date()
        vid=str(g.get("venue_id")) if g.get("venue_id") is not None else None

        # IMPORTANT: calculate target record before adding the current game's runs.
        if start <= game_date <= end:
            if vid is None:
                skipped.append({"game_pk":str(g["game_pk"]),"reason":"missing-venue"})
            else:
                vvals=[x[1] for x in venue[vid]]
                lvals=[x[1] for x in league]

                if len(vvals) < int(min_venue_games):
                    skipped.append({
                        "game_pk":str(g["game_pk"]),
                        "reason":"insufficient-prior-venue-games",
                        "prior_venue_games":len(vvals),
                    })
                elif not lvals:
                    skipped.append({"game_pk":str(g["game_pk"]),"reason":"missing-league-history"})
                else:
                    venue_mean=_mean(vvals)
                    league_mean=_mean(lvals)
                    if league_mean <= 0:
                        skipped.append({"game_pk":str(g["game_pk"]),"reason":"invalid-league-mean"})
                    else:
                        raw=venue_mean/league_mean
                        factor=shrink_to_neutral(raw,len(vvals),shrink_games)
                        records.append({
                            "game_pk":str(g["game_pk"]),
                            "venue_id":vid,
                            "game_time_utc":g["game_time_utc"],
                            "park_factor":factor,
                            "raw_run_environment_factor":raw,
                            "prior_venue_games":len(vvals),
                            "prior_league_games":len(lvals),
                            "venue_mean_total_runs":venue_mean,
                            "league_mean_total_runs":league_mean,
                            "frozen_through_utc":(
                                max([x[0] for x in league]).isoformat()
                                if league else None
                            ),
                            "lookback_days":int(lookback_days),
                            "shrink_games":int(shrink_games),
                            "source":"prior-completed-MLB-game-runs",
                            "research_only":True,
                        })

        total=_total_runs(g)
        # Only completed, non-null results enter FUTURE history.
        if total is not None and vid is not None:
            league.append((now,total))
            venue[vid].append((now,total))

    return {"records":records,"skipped":skipped}
