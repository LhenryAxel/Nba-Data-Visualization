from sqlalchemy import func
from app.models import Session, PlayerStat


def main():
    session = Session()

    print("\nTop 10 scorers")
    top_scorers = (
        session.query(PlayerStat)
        .order_by(PlayerStat.pts.desc())
        .limit(10)
        .all()
    )

    for player in top_scorers:
        print(f"{player.player_name} - {player.pts} pts")

    print("\nAverage points")
    avg_pts = session.query(func.avg(PlayerStat.pts)).scalar()
    print(round(avg_pts, 2))

    print("\nAverage rebounds by team")
    avg_rebounds = (
        session.query(
            PlayerStat.team_abbreviation,
            func.avg(PlayerStat.reb).label("avg_reb")
        )
        .group_by(PlayerStat.team_abbreviation)
        .order_by(func.avg(PlayerStat.reb).desc())
        .limit(10)
        .all()
    )

    for team, avg_reb in avg_rebounds:
        print(f"{team} - {avg_reb:.2f}")

    print("\nNumber of players by age group")
    age_groups = (
        session.query(
            PlayerStat.age_group,
            func.count(PlayerStat.id)
        )
        .group_by(PlayerStat.age_group)
        .all()
    )

    for age_group, count in age_groups:
        print(f"{age_group} - {count}")

    session.close()


if __name__ == "__main__":
    main()