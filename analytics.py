"""Validated Kaggle loading and reusable cricket aggregations."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent

KAGGLE_URL = (
    "https://www.kaggle.com/datasets/"
    "patrickb1912/ipl-complete-dataset-20082020"
)

BOWLER_WICKETS = {
    "caught",
    "bowled",
    "lbw",
    "caught and bowled",
    "stumped",
    "hit wicket",
}

ALIASES = {
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
}


def prepare(matches, deliveries):
    m, d = matches.copy(), deliveries.copy()

    required_m = {
        "id", "date", "team1", "team2", "winner",
        "match_type", "venue", "result",
    }
    required_d = {
        "match_id", "inning", "over", "batter", "bowler",
        "batsman_runs", "total_runs", "extra_runs", "extras_type",
        "dismissal_kind", "is_wicket", "batting_team", "bowling_team",
    }

    for frame, required, label in [
        (m, required_m, "matches.csv"),
        (d, required_d, "deliveries.csv.gz"),
    ]:
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(
                f'{label} is missing columns: {", ".join(sorted(missing))}. '
                "Use the linked Kaggle dataset."
            )
        if frame.empty:
            raise ValueError(f"{label} is empty.")

    if m.id.isna().any() or m.id.duplicated().any():
        raise ValueError("Match IDs must be present and unique.")

    m["date"] = pd.to_datetime(m.date, errors="raise")
    if m.date.isna().any():
        raise ValueError("Match dates cannot be missing.")

    # Map season labels to the match date's calendar year.
    m["season"] = m.date.dt.year

    for col in [
        "inning", "over", "batsman_runs",
        "total_runs", "extra_runs", "is_wicket",
    ]:
        d[col] = pd.to_numeric(d[col], errors="raise")
        if (
            d[col].isna().any()
            or (d[col] < 0).any()
            or (d[col] % 1 != 0).any()
        ):
            raise ValueError(
                f"Delivery column {col} must contain nonnegative integers."
            )

    name_columns = ["batter", "bowler", "batting_team", "bowling_team"]
    if d[name_columns].isna().any().any():
        raise ValueError("Delivery player and team names cannot be missing.")

    if not d.match_id.isin(m.id).all():
        raise ValueError(
            "Some deliveries have no matching match ID. "
            "Upload a matching CSV pair."
        )

    if not d.total_runs.eq(d.batsman_runs + d.extra_runs).all():
        raise ValueError(
            "Total runs do not reconcile with batter runs plus extras."
        )

    for frame, columns in [
        (m, ["team1", "team2", "winner", "toss_winner"]),
        (d, ["batting_team", "bowling_team"]),
    ]:
        for col in columns:
            if col in frame:
                frame[col] = frame[col].replace(ALIASES)

    d = d.merge(
        m[["id", "season"]],
        left_on="match_id",
        right_on="id",
        validate="many_to_one",
    ).drop(columns="id")

    d["extras_type"] = d.extras_type.fillna("").str.lower().str.strip()
    d["dismissal_kind"] = (
        d.dismissal_kind.fillna("").str.lower().str.strip()
    )

    # Preserve the project's ball-counting definitions.
    d["ball_faced"] = d.extras_type.ne("wides").astype(int)
    d["legal_ball"] = (
        ~d.extras_type.isin(["wides", "noballs"])
    ).astype(int)
    d["bowler_wicket"] = d.dismissal_kind.isin(BOWLER_WICKETS).astype(int)

    d["conceded"] = d.batsman_runs + d.extra_runs.where(
        d.extras_type.isin(["wides", "noballs"]), 0
    )
    d["four"] = d.batsman_runs.eq(4).astype(int)
    d["six"] = d.batsman_runs.eq(6).astype(int)

    return m, d


def load_data():
    matches = pd.read_csv(ROOT / "data" / "matches.csv")
    deliveries = pd.read_csv(ROOT / "data" / "deliveries.csv.gz")
    return prepare(matches, deliveries)


def batting(d, keys=None):
    keys = keys or ["batter"]

    result = d.groupby(keys).agg(
        Runs=("batsman_runs", "sum"),
        Balls=("ball_faced", "sum"),
        Innings=("match_id", "nunique"),
        Fours=("four", "sum"),
        Sixes=("six", "sum"),
    ).reset_index()

    result["Strike rate"] = (
        100 * result.Runs / result.Balls.replace(0, float("nan"))
    ).round(2)

    return result.sort_values("Runs", ascending=False)


def bowling(d):
    result = d.groupby("bowler").agg(
        Wickets=("bowler_wicket", "sum"),
        Balls=("legal_ball", "sum"),
        Conceded=("conceded", "sum"),
        Matches=("match_id", "nunique"),
    ).reset_index()

    result["Economy"] = (
        6 * result.Conceded / result.Balls.replace(0, float("nan"))
    ).round(2)

    return result.sort_values(
        ["Wickets", "Economy"],
        ascending=[False, True],
    )


def filter_data(m, d, seasons, team="All teams"):
    selected = m[m.season.isin(seasons)]

    if team != "All teams":
        selected = selected[
            selected.team1.eq(team) | selected.team2.eq(team)
        ]

    # Exclude super overs from player and league statistics.
    balls = d[
        d.match_id.isin(selected.id)
        & d.inning.le(2)
    ]

    return selected, balls
