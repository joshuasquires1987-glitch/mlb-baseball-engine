def chronological_split(rows, holdout_games=150):
    ordered=sorted(rows,key=lambda r:(r["game_date"],r["game_id"]))
    if len(ordered)<=holdout_games:
        raise ValueError("not enough rows for requested holdout")
    return ordered[:-holdout_games],ordered[-holdout_games:]

def assert_no_date_overlap(train,holdout):
    if not train or not holdout:
        raise ValueError("empty split")
    max_train=max(r["game_date"] for r in train)
    min_holdout=min(r["game_date"] for r in holdout)
    if max_train>min_holdout:
        raise RuntimeError("chronological leakage detected")
    return True
