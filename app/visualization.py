import pandas as pd
import plotly.express as px
from sqlalchemy import func
from app.models import Session, PlayerStat
import plotly.graph_objects as go


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

    df["position"] = "NA"
    df.loc[df["player_height"] >= 207, "position"] = "Center"
    df.loc[df["player_height"] <= 195, "position"] = "Guard"
    df.loc[(df["player_height"] > 195) & (df["player_height"] < 207), "position"] = "Forward"

    return df


def _get_warriors_vs_league_2016_metrics() -> pd.DataFrame:
    df = load_players_dataframe()
    df_2016 = df[df["season"] == "2015-16"].copy()

    warriors = df_2016[df_2016["team_abbreviation"] == "GSW"].copy()

    warriors_metrics = {
        "average_height": warriors["player_height"].mean(),
        "total_assists": warriors["ast"].sum(),
        "average_net_rating": warriors["net_rating"].mean(),
        "center_share": (warriors["position"] == "Center").mean() * 100
    }

    team_metrics = (
        df_2016.groupby("team_abbreviation")
        .apply(lambda group: pd.Series({
            "average_height": group["player_height"].mean(),
            "total_assists": group["ast"].sum(),
            "average_net_rating": group["net_rating"].mean(),
            "center_share": (group["position"] == "Center").mean() * 100
        }))
        .reset_index()
    )

    league_avg = {
        "average_height": team_metrics["average_height"].mean(),
        "total_assists": team_metrics["total_assists"].mean(),
        "average_net_rating": team_metrics["average_net_rating"].mean(),
        "center_share": team_metrics["center_share"].mean()
    }

    comparison = pd.DataFrame([
        {"group": "Warriors", **warriors_metrics},
        {"group": "League Average", **league_avg}
    ])

    return comparison


def get_warriors_vs_league_radar_2016_figure():
    comparison = _get_warriors_vs_league_2016_metrics().copy()

    metric_labels = {
        "average_height": "Average Height",
        "total_assists": "Total Assists",
        "average_net_rating": "Average Net Rating",
        "center_share": "Center Share"
    }

    # Normalize metrics to compare on same radar scale
    metric_cols = list(metric_labels.keys())
    normalized = comparison.copy()

    for col in metric_cols:
        col_min = comparison[col].min()
        col_max = comparison[col].max()

        if col_max == col_min:
            normalized[col] = 100
        else:
            normalized[col] = (comparison[col] - col_min) / (col_max - col_min) * 100

    categories = [metric_labels[col] for col in metric_cols]
    categories.append(categories[0])

    warriors_values = normalized[normalized["group"] == "Warriors"][metric_cols].iloc[0].tolist()
    league_values = normalized[normalized["group"] == "League Average"][metric_cols].iloc[0].tolist()

    warriors_values.append(warriors_values[0])
    league_values.append(league_values[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=warriors_values,
        theta=categories,
        fill="toself",
        name="Warriors 2015-16"
    ))

    fig.add_trace(go.Scatterpolar(
        r=league_values,
        theta=categories,
        fill="toself",
        name="League Average"
    ))

    fig.update_layout(
        title="Warriors 2015-16 vs League Average (Normalized)",
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True
    )

    return fig


def get_warriors_vs_league_metrics_bar_2016_figure():
    comparison = _get_warriors_vs_league_2016_metrics().copy()

    df_long = comparison.melt(
        id_vars="group",
        value_vars=["average_height", "total_assists", "average_net_rating", "center_share"],
        var_name="metric",
        value_name="value"
    )

    metric_names = {
        "average_height": "Average Height (cm)",
        "total_assists": "Total Assists",
        "average_net_rating": "Average Net Rating",
        "center_share": "Center Share (%)"
    }

    df_long["metric"] = df_long["metric"].map(metric_names)

    fig = px.bar(
        df_long,
        x="metric",
        y="value",
        color="group",
        barmode="group",
        title="Warriors 2015-16 vs League Average - Key Metrics"
    )

    return fig


def get_warriors_vs_league_roster_composition_2016_figure():
    df = load_players_dataframe()
    df_2016 = df[df["season"] == "2015-16"].copy()

    warriors = df_2016[df_2016["team_abbreviation"] == "GSW"].copy()

    league_team_position = (
        df_2016.groupby(["team_abbreviation", "position"])
        .size()
        .reset_index(name="count")
    )

    league_team_position["team_total"] = league_team_position.groupby("team_abbreviation")["count"].transform("sum")
    league_team_position["share_pct"] = league_team_position["count"] / league_team_position["team_total"] * 100

    league_avg = (
        league_team_position.groupby("position", as_index=False)["share_pct"]
        .mean()
    )
    league_avg["group"] = "League Average"

    warriors_comp = (
        warriors.groupby("position")
        .size()
        .reset_index(name="count")
    )
    warriors_comp["share_pct"] = warriors_comp["count"] / warriors_comp["count"].sum() * 100
    warriors_comp["group"] = "Warriors"

    comparison = pd.concat([
        warriors_comp[["position", "share_pct", "group"]],
        league_avg[["position", "share_pct", "group"]]
    ], ignore_index=True)

    fig = px.bar(
        comparison,
        x="position",
        y="share_pct",
        color="group",
        barmode="group",
        title="Warriors 2015-16 vs League Average - Roster Composition",
        labels={"share_pct": "Share of Players (%)", "position": "Position"}
    )

    return fig


if __name__ == "__main__":
    get_avg_height_by_season_figure().show()
    get_avg_weight_by_season_figure().show()
    get_rebounds_vs_height_figure().show()
    get_total_assists_by_season_figure().show()
    get_center_assists_by_season_figure().show()
    get_points_by_position_figure().show()
    get_rebounds_by_position_figure().show()
    get_assists_by_position_figure().show()
    get_warriors_vs_league_radar_2016_figure().show()
    get_warriors_vs_league_metrics_bar_2016_figure().show()
    get_warriors_vs_league_roster_composition_2016_figure().show()