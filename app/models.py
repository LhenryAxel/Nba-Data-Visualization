from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///sportstats.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(20), default="user")


class PlayerStat(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_name = Column(String(100), nullable=False)
    team_abbreviation = Column(String(10))
    age = Column(Float)
    player_height = Column(Float)
    player_weight = Column(Float)
    college = Column(String(100))
    country = Column(String(100))
    draft_year = Column(String(20))
    draft_round = Column(Float)
    draft_number = Column(Float)
    gp = Column(Integer)
    pts = Column(Float)
    reb = Column(Float)
    ast = Column(Float)
    net_rating = Column(Float)
    oreb_pct = Column(Float)
    dreb_pct = Column(Float)
    usg_pct = Column(Float)
    ts_pct = Column(Float)
    ast_pct = Column(Float)
    season = Column(String(20))
    pts_per_game_level = Column(String(30))
    age_group = Column(String(30))
    reb_per_cm = Column(Float)
    ast_to_pts_ratio = Column(Float)


def init_db():
    Base.metadata.create_all(engine)