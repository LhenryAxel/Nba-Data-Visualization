from app.data_processing import load_csv, clean_data, enrich_data
from app.models import engine, init_db, Session, PlayerStat


def main():
    # 1. Initialize database
    init_db()

    # 2. Load and process data
    df = load_csv("data/all_seasons.csv")
    df = clean_data(df)
    df = enrich_data(df)

    # 3. Insert into SQLite
    df.to_sql("player_stats", engine, if_exists="append", index=False)
    
    # 4. Verify insertion
    session = Session()
    count = session.query(PlayerStat).count()
    print(f"{count} records inserted into database")

    print("\nFirst 5 players:")
    players = session.query(PlayerStat).limit(5).all()
    for player in players:
        print(
            f"{player.player_name} | {player.team_abbreviation} | "
            f"{player.pts} pts | {player.reb} reb | {player.ast} ast"
        )

    session.close()


if __name__ == "__main__":
    main()