import pandas as pd
import plotly.express as px
from sqlalchemy import func
from app.models import Session, PlayerStat


def load_players_dataframe() -> pd.DataFrame:
    session = Session()
    players = session.query(PlayerStat).all()

    df = pd.DataFrame([{
        "player_name": p.player_name,
        "team_abbreviation": p.team_abbreviation,
        "season": str(p.season),
        "age": p.age,
        "player_height": p.player_height,
        "player_weight": p.player_weight,
        "pts": p.pts,
        "reb": p.reb,
        "ast": p.ast,
        "net_rating": p.net_rating,
        "usg_pct": p.usg_pct,
        "ts_pct": p.ts_pct,
    } for p in players])

    session.close()

    df["start_year"] = df["season"].str[:4].astype(int)

    # Add positions from height
    df["position"] = "NA"
    df.loc[df["player_height"] >= 207, "position"] = "Center"
    df.loc[df["player_height"] <= 195, "position"] = "Guard"
    df.loc[(df["player_height"] > 195) & (df["player_height"] < 207), "position"] = "Forward"

    # Small-ball proxy
    df["position_type"] = "Big"
    df.loc[df["position"].isin(["Guard", "Forward"]), "position_type"] = "Guard/Wing"

    return df


def add_small_ball_marker(fig, y=None):
    fig.add_vline(
        x="2015-16",
        line_width=2,
        line_dash="dash",
        line_color="red"
    )

    annotation_kwargs = {
        "x": "2015-16",
        "text": "Warriors dynasty / small-ball shift",
        "showarrow": True,
        "arrowhead": 2,
        "ax": 40,
        "ay": -40
    }

    if y is not None:
        annotation_kwargs["y"] = y

    fig.add_annotation(**annotation_kwargs)
    return fig


def get_avg_height_by_season_figure():
    df = load_players_dataframe()

    grouped = (
        df.groupby("season", as_index=False)["player_height"]
        .mean()
        .rename(columns={"player_height": "avg_height"})
    )

    grouped["start_year"] = grouped["season"].str[:4].astype(int)
    grouped = grouped.sort_values("start_year")

    fig = px.line(
        grouped,
        x="season",
        y="avg_height",
        title="Average Player Height by Season",
        markers=True,
        labels={"season": "Season", "avg_height": "Average Height (cm)"}
    )

    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=grouped["season"].tolist()
    )

    return add_small_ball_marker(fig, grouped["avg_height"].max())


def get_avg_weight_by_season_figure():
    df = load_players_dataframe()

    grouped = (
        df.groupby("season", as_index=False)["player_weight"]
        .mean()
        .rename(columns={"player_weight": "avg_weight"})
    )

    grouped["start_year"] = grouped["season"].str[:4].astype(int)
    grouped = grouped.sort_values("start_year")

    fig = px.line(
        grouped,
        x="season",
        y="avg_weight",
        title="Average Player Weight by Season",
        markers=True,
        labels={"season": "Season", "avg_weight": "Average Weight (kg)"}
    )

    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=grouped["season"].tolist()
    )

    return add_small_ball_marker(fig, grouped["avg_weight"].max())


def get_rebounds_vs_height_figure():
    df = load_players_dataframe()

    fig = px.scatter(
        df,
        x="player_height",
        y="reb",
        color="season",
        title="Rebounds vs Height",
        labels={
            "player_height": "Height (cm)",
            "reb": "Rebounds per Game"
        },
        opacity=0.55
    )

    return fig

def get_total_assists_by_season_figure():
    df = load_players_dataframe()

    grouped = (
        df.groupby("season", as_index=False)["ast"]
        .sum()
        .rename(columns={"ast": "total_ast"})
    )

    grouped["start_year"] = grouped["season"].str[:4].astype(int)
    grouped = grouped.sort_values("start_year")

    fig = px.line(
        grouped,
        x="season",
        y="total_ast",
        title="Total Assists by Season",
        markers=True,
        labels={"season": "Season", "total_ast": "Total Assists"}
    )

    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=grouped["season"].tolist()
    )

    return add_small_ball_marker(fig, grouped["total_ast"].max())


def get_center_assists_by_season_figure():
    df = load_players_dataframe()
    df = df[df["position"] == "Center"].copy()

    grouped = (
        df.groupby("season", as_index=False)["ast"]
        .sum()
        .rename(columns={"ast": "center_ast"})
    )

    grouped["start_year"] = grouped["season"].str[:4].astype(int)
    grouped = grouped.sort_values("start_year")

    fig = px.line(
        grouped,
        x="season",
        y="center_ast",
        title="Total Assists by Centers per Season",
        markers=True,
        labels={"season": "Season", "center_ast": "Center Assists"}
    )

    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=grouped["season"].tolist()
    )

    return add_small_ball_marker(fig, grouped["center_ast"].max())


def get_points_by_position_figure():
    df = load_players_dataframe()

    grouped = (
        df.groupby(["season", "position"], as_index=False)["pts"]
        .sum()
        .rename(columns={"pts": "total_pts"})
    )

    grouped["start_year"] = grouped["season"].str[:4].astype(int)
    grouped = grouped.sort_values(["start_year", "position"])

    fig = px.line(
        grouped,
        x="season",
        y="total_pts",
        color="position",
        title="Total Points by Position and Season",
        markers=True,
        labels={
            "season": "Season",
            "total_pts": "Total Points",
            "position": "Position"
        }
    )

    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=grouped.drop_duplicates("season")["season"].tolist()
    )

    return add_small_ball_marker(fig, grouped["total_pts"].max())


def get_rebounds_by_position_figure():
    df = load_players_dataframe()

    grouped = (
        df.groupby(["season", "position"], as_index=False)["reb"]
        .sum()
        .rename(columns={"reb": "total_reb"})
    )

    grouped["start_year"] = grouped["season"].str[:4].astype(int)
    grouped = grouped.sort_values(["start_year", "position"])

    fig = px.line(
        grouped,
        x="season",
        y="total_reb",
        color="position",
        title="Total Rebounds by Position and Season",
        markers=True,
        labels={
            "season": "Season",
            "total_reb": "Total Rebounds",
            "position": "Position"
        }
    )

    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=grouped.drop_duplicates("season")["season"].tolist()
    )

    return add_small_ball_marker(fig, grouped["total_reb"].max())


def get_assists_by_position_figure():
    df = load_players_dataframe()

    grouped = (
        df.groupby(["season", "position"], as_index=False)["ast"]
        .sum()
        .rename(columns={"ast": "total_ast"})
    )

    grouped["start_year"] = grouped["season"].str[:4].astype(int)
    grouped = grouped.sort_values(["start_year", "position"])

    fig = px.line(
        grouped,
        x="season",
        y="total_ast",
        color="position",
        title="Total Assists by Position and Season",
        markers=True,
        labels={
            "season": "Season",
            "total_ast": "Total Assists",
            "position": "Position"
        }
    )

    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=grouped.drop_duplicates("season")["season"].tolist()
    )

    return add_small_ball_marker(fig, grouped["total_ast"].max())


if __name__ == "__main__":
    get_avg_height_by_season_figure().show()
    get_avg_weight_by_season_figure().show()
    get_rebounds_vs_height_figure().show()
    get_total_assists_by_season_figure().show()
    get_center_assists_by_season_figure().show()
    get_points_by_position_figure().show()
    get_rebounds_by_position_figure().show()
    get_assists_by_position_figure().show()