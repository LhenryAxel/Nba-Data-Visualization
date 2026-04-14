from flask import Flask, jsonify
from sqlalchemy import func
from app.models import Session, PlayerStat
from app.visualization import (
    get_avg_height_by_season_figure,
    get_avg_weight_by_season_figure,
    get_rebounds_vs_height_figure,
    get_total_assists_by_season_figure,
    get_center_assists_by_season_figure,
    get_points_by_position_figure,
    get_rebounds_by_position_figure,
    get_assists_by_position_figure
)

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>NBA Small Ball API</h1>
    <ul>
        <li><a href="/data/top-scorers">/data/top-scorers</a></li>
        <li><a href="/data/avg-height-by-season">/data/avg-height-by-season</a></li>
        <li><a href="/chart/avg-height-by-season">/chart/avg-height-by-season</a></li>
        <li><a href="/chart/avg-weight-by-season">/chart/avg-weight-by-season</a></li>
        <li><a href="/chart/rebounds-vs-height">/chart/rebounds-vs-height</a></li>
        <li><a href="/chart/total-assists-by-season">/chart/total-assists-by-season</a></li>
        <li><a href="/chart/center-assists-by-season">/chart/center-assists-by-season</a></li>
        <li><a href="/chart/points-by-position">/chart/points-by-position</a></li>
        <li><a href="/chart/rebounds-by-position">/chart/rebounds-by-position</a></li>
        <li><a href="/chart/assists-by-position">/chart/assists-by-position</a></li>
    </ul>
    """


@app.route("/data/top-scorers")
def top_scorers():
    session = Session()
    players = (
        session.query(PlayerStat)
        .order_by(PlayerStat.pts.desc())
        .limit(10)
        .all()
    )

    data = [{
        "player_name": p.player_name,
        "team_abbreviation": p.team_abbreviation,
        "season": p.season,
        "pts": p.pts
    } for p in players]

    session.close()
    return jsonify(data)


@app.route("/data/avg-height-by-season")
def avg_height_by_season_data():
    session = Session()

    results = (
        session.query(
            PlayerStat.season,
            func.avg(PlayerStat.player_height).label("avg_height")
        )
        .group_by(PlayerStat.season)
        .order_by(PlayerStat.season)
        .all()
    )

    data = [{"season": season, "avg_height": round(avg_height, 2)} for season, avg_height in results]

    session.close()
    return jsonify(data)


@app.route("/chart/avg-height-by-season")
def chart_avg_height_by_season():
    return get_avg_height_by_season_figure().to_html(full_html=True)


@app.route("/chart/avg-weight-by-season")
def chart_avg_weight_by_season():
    return get_avg_weight_by_season_figure().to_html(full_html=True)


@app.route("/chart/rebounds-vs-height")
def chart_rebounds_vs_height():
    return get_rebounds_vs_height_figure().to_html(full_html=True)


@app.route("/chart/total-assists-by-season")
def chart_total_assists_by_season():
    return get_total_assists_by_season_figure().to_html(full_html=True)


@app.route("/chart/center-assists-by-season")
def chart_center_assists_by_season():
    return get_center_assists_by_season_figure().to_html(full_html=True)


@app.route("/chart/points-by-position")
def chart_points_by_position():
    return get_points_by_position_figure().to_html(full_html=True)


@app.route("/chart/rebounds-by-position")
def chart_rebounds_by_position():
    return get_rebounds_by_position_figure().to_html(full_html=True)


@app.route("/chart/assists-by-position")
def chart_assists_by_position():
    return get_assists_by_position_figure().to_html(full_html=True)


if __name__ == "__main__":
    app.run(debug=True)