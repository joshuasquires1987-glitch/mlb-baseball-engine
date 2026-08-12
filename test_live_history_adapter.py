from live_history_adapter import history_window


def test_history_window_excludes_target_day():
    start, end = history_window("2026-08-12")
    assert start == "2025-03-15"
    assert end == "2026-08-11"


def test_history_window_accepts_explicit_warmup_start():
    start, end = history_window("2026-08-12", "2026-03-15")
    assert start == "2026-03-15"
    assert end == "2026-08-11"
