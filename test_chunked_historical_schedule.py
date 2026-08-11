from mlb_bulk_schedule_runtime import month_chunks, completed_games_chunked

def fake_payload(game_pk, date_str, away_score=3, home_score=4):
    return {
        "dates":[{
            "date":date_str,
            "games":[{
                "gamePk":game_pk,
                "gameDate":date_str+"T18:00:00Z",
                "status":{"abstractGameState":"Final","detailedState":"Final"},
                "teams":{
                    "away":{"team":{"id":1},"score":away_score},
                    "home":{"team":{"id":2},"score":home_score},
                },
                "venue":{"id":31},
            }],
        }]
    }

def test_month_chunks_cross_year_boundary():
    assert list(month_chunks("2024-12-30","2025-02-02")) == [
        ("2024-12-30","2024-12-31"),
        ("2025-01-01","2025-01-31"),
        ("2025-02-01","2025-02-02"),
    ]

def test_chunked_fetch_merges_and_dedupes():
    calls=[]
    def fetcher(url):
        calls.append(url)
        if "startDate=2025-01-01" in url:
            return fake_payload(100,"2025-01-10")
        return fake_payload(100,"2025-01-10")

    games,stats=completed_games_chunked(
        "2025-01-01","2025-02-02",fetcher=fetcher
    )

    assert len(calls)==2
    assert len(stats)==2
    assert len(games)==1
    assert games[0]["game_pk"]=="100"

def test_chunked_fetch_retains_distinct_games():
    counter={"n":0}
    def fetcher(url):
        counter["n"]+=1
        return fake_payload(
            100+counter["n"],
            "2025-01-10" if counter["n"]==1 else "2025-02-01",
        )

    games,stats=completed_games_chunked(
        "2025-01-01","2025-02-02",fetcher=fetcher
    )
    assert len(games)==2
    assert [g["game_pk"] for g in games]==["101","102"]

def test_final_status_without_score_is_not_completed_observation():
    def fetcher(url):
        return fake_payload(999,"2025-01-10",away_score=None,home_score=4)

    games,stats=completed_games_chunked(
        "2025-01-01","2025-01-31",fetcher=fetcher
    )

    assert games == []
    assert stats[0]["completed_games"] == 0
