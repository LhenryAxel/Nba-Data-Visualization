from flask import Flask, jsonify, request
from sqlalchemy import func

from app.models import Session, PlayerStat
from app.auth import login_user, register_user, token_required

app = Flask(__name__)

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()
    role = str(data.get("role", "user")).strip()

    if not username or not password:
        return jsonify({
            "error": "username and password are required"
        }), 400

    user = register_user(username, password, role)

    if not user:
        return jsonify({
            "error": "User already exists"
        }), 409

    return jsonify({
        "message": "User created successfully",
        "username": user.username,
        "role": user.role
    }), 201

@app.route("/")
def home():
    return jsonify({
        "message": "NBA Secure API",
        "endpoints": {
            "login": {
                "method": "POST",
                "url": "/api/login"
            },
            "data": {
                "method": "GET",
                "url": "/api/data",
                "auth": "Bearer token required"
            },
            "stats": {
                "method": "GET",
                "url": "/api/stats",
                "auth": "Bearer token required"
            }
        }
    })


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    if not username or not password:
        return jsonify({
            "error": "username and password are required"
        }), 400

    token = login_user(username, password)

    if not token:
        return jsonify({
            "error": "Invalid credentials"
        }), 401

    return jsonify({
        "token": token
    }), 200


@app.route("/api/data", methods=["GET"])
@token_required
def api_data(payload):
    session = Session()

    try:
        season = request.args.get("season")
        team = request.args.get("team")
        limit = request.args.get("limit", default=20, type=int)

        if limit is None or limit <= 0:
            limit = 20
        if limit > 100:
            limit = 100

        query = session.query(PlayerStat)

        if season:
            query = query.filter(PlayerStat.season == season)

        if team:
            query = query.filter(PlayerStat.team_abbreviation == team.upper())

        players = query.limit(limit).all()

        data = [
            {
                "id": player.id,
                "player_name": player.player_name,
                "team_abbreviation": player.team_abbreviation,
                "season": player.season,
                "age": player.age,
                "pts": player.pts,
                "reb": player.reb,
                "ast": player.ast,
                "net_rating": player.net_rating,
                "usg_pct": player.usg_pct,
                "ts_pct": player.ts_pct
            }
            for player in players
        ]

        return jsonify({
            "message": "Protected data access granted",
            "user": {
                "user_id": payload.get("user_id"),
                "role": payload.get("role")
            },
            "filters": {
                "season": season,
                "team": team.upper() if team else None,
                "limit": limit
            },
            "count": len(data),
            "data": data
        }), 200

    finally:
        session.close()


@app.route("/api/stats", methods=["GET"])
@token_required
def api_stats(payload):
    session = Session()

    try:
        season = request.args.get("season")
        team = request.args.get("team")

        query = session.query(PlayerStat)

        if season:
            query = query.filter(PlayerStat.season == season)

        if team:
            query = query.filter(PlayerStat.team_abbreviation == team.upper())

        stats = query.with_entities(
            func.count(PlayerStat.id).label("total_rows"),
            func.avg(PlayerStat.pts).label("avg_pts"),
            func.avg(PlayerStat.reb).label("avg_reb"),
            func.avg(PlayerStat.ast).label("avg_ast"),
            func.avg(PlayerStat.net_rating).label("avg_net_rating"),
            func.avg(PlayerStat.player_height).label("avg_height"),
            func.avg(PlayerStat.player_weight).label("avg_weight")
        ).one()

        return jsonify({
            "message": "Protected stats access granted",
            "user": {
                "user_id": payload.get("user_id"),
                "role": payload.get("role")
            },
            "filters": {
                "season": season,
                "team": team.upper() if team else None
            },
            "stats": {
                "total_rows": int(stats.total_rows or 0),
                "avg_pts": round(stats.avg_pts or 0, 2),
                "avg_reb": round(stats.avg_reb or 0, 2),
                "avg_ast": round(stats.avg_ast or 0, 2),
                "avg_net_rating": round(stats.avg_net_rating or 0, 2),
                "avg_height": round(stats.avg_height or 0, 2),
                "avg_weight": round(stats.avg_weight or 0, 2)
            }
        }), 200

    finally:
        session.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000) 