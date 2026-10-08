from datetime import date

import pandas as pd

from app.analytics.core import analyze, data_sufficiency


def test_deep_work_hand_computed():
    sessions = pd.DataFrame(
        [
            {
                "local_date": date(2026, 10, 1),
                "weekday": 3,
                "hour": 9,
                "minutes": 60,
                "deep_work": True,
                "focus": 4,
            },
            {
                "local_date": date(2026, 10, 1),
                "weekday": 3,
                "hour": 11,
                "minutes": 20,
                "deep_work": False,
                "focus": 3,
            },
            {
                "local_date": date(2026, 10, 2),
                "weekday": 4,
                "hour": 9,
                "minutes": 30,
                "deep_work": True,
                "focus": 5,
            },
        ]
    )
    empty = pd.DataFrame()
    result = analyze("deep-work", sessions, empty, empty, empty, empty)["result"]
    assert result["total_minutes"] == 90
    assert result["session_count"] == 2
    assert result["median_daily_minutes"] == 45


def test_time_leaks_and_empty_data():
    distractions = pd.DataFrame(
        [
            {
                "local_date": date(2026, 10, 1),
                "weekday": 3,
                "minutes": 10,
                "category": "YOUTUBE",
            },
            {
                "local_date": date(2026, 10, 1),
                "weekday": 3,
                "minutes": 5,
                "category": "YOUTUBE",
            },
            {
                "local_date": date(2026, 10, 2),
                "weekday": 4,
                "minutes": 20,
                "category": "PHONE",
            },
        ]
    )
    empty = pd.DataFrame()
    result = analyze("time-leaks", empty, distractions, empty, empty, empty)["result"]
    assert result["total_minutes"] == 35
    assert result["top_category"] == "PHONE"
    assert (
        analyze("prayers", empty, empty, empty, empty, empty)["result"]["completed"]
        == 0
    )


def test_sufficiency_thresholds():
    assert data_sufficiency(6)["level"] == "insufficient"
    assert data_sufficiency(14)["level"] == "preliminary"
    assert data_sufficiency(90)["level"] == "strong"
