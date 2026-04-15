import pandas as pd
import streamlit as st

from app.models import Session, User, PlayerStat
from app.auth import verify_password
from app.visualization import (
    get_avg_height_by_season_figure,
    get_avg_weight_by_season_figure,
    get_rebounds_vs_height_figure,
    get_total_assists_by_season_figure,
    get_center_assists_by_season_figure,
    get_points_by_position_figure,
    get_rebounds_by_position_figure,
    get_assists_by_position_figure,
)


st.set_page_config(page_title="NBA Small Ball Dashboard", layout="wide")


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load player stats from SQLite using SQLAlchemy."""
    session = Session()

    try:
        players = session.query(PlayerStat).all()

        data = [
            {
                "id": player.id,
                "player_name": player.player_name,
                "team_abbreviation": player.team_abbreviation,
                "season": player.season,
                "age": player.age,
                "player_height": player.player_height,
                "player_weight": player.player_weight,
                "pts": player.pts,
                "reb": player.reb,
                "ast": player.ast,
                "net_rating": player.net_rating,
                "usg_pct": player.usg_pct,
                "ts_pct": player.ts_pct,
            }
            for player in players
        ]

        return pd.DataFrame(data)

    finally:
        session.close()


def show_login():
    """Display Streamlit login form."""
    st.title("NBA Small Ball Dashboard")
    st.subheader("Connexion")

    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")

        if submitted:
            if not username or not password:
                st.error("Veuillez remplir tous les champs.")
                return

            session = Session()

            try:
                user = session.query(User).filter(User.username == username).first()
            finally:
                session.close()

            if user and verify_password(user.password_hash, password):
                st.session_state.authenticated = True
                st.session_state.username = user.username
                st.session_state.role = user.role
                st.rerun()
            else:
                st.error("Identifiants incorrects.")


def show_dashboard():
    """Display protected dashboard."""
    df = load_data()

    if df.empty:
        st.warning("Aucune donnée disponible.")
        return

    col1, col2 = st.columns([6, 1])

    with col1:
        st.title("NBA Small Ball Transformation Dashboard")
        st.caption(
            f"Connecté en tant que : {st.session_state.username} "
            f"({st.session_state.role})"
        )

    with col2:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.role = None
            st.rerun()

    st.markdown(
        """
        This dashboard explores the NBA transformation toward small ball,
        especially around and after the Warriors dynasty era (2015-16).
        """
    )

    st.subheader("Physical Evolution")
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(get_avg_height_by_season_figure(df), use_container_width=True)
    with col4:
        st.plotly_chart(get_avg_weight_by_season_figure(df), use_container_width=True)

    st.subheader("Height and Rebounding")
    st.plotly_chart(get_rebounds_vs_height_figure(df), use_container_width=True)

    st.subheader("Ball Movement and Playmaking")
    col5, col6 = st.columns(2)
    with col5:
        st.plotly_chart(get_total_assists_by_season_figure(df), use_container_width=True)
    with col6:
        st.plotly_chart(get_center_assists_by_season_figure(df), use_container_width=True)

    st.subheader("Production by Position")
    col7, col8 = st.columns(2)
    with col7:
        st.plotly_chart(get_points_by_position_figure(df), use_container_width=True)
    with col8:
        st.plotly_chart(get_assists_by_position_figure(df), use_container_width=True)

    st.plotly_chart(get_rebounds_by_position_figure(df), use_container_width=True)


if not st.session_state.authenticated:
    show_login()
else:
    show_dashboard()