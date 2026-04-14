import streamlit as st
from app.visualization import (
    get_avg_height_by_season_figure,
    get_avg_weight_by_season_figure,
    get_rebounds_vs_height_figure,
    get_total_assists_by_season_figure,
    get_center_assists_by_season_figure,
    get_points_by_position_figure,
    get_rebounds_by_position_figure,
    get_assists_by_position_figure,
    get_warriors_vs_league_radar_2016_figure,
    get_warriors_vs_league_metrics_bar_2016_figure,
    get_warriors_vs_league_roster_composition_2016_figure
)


st.set_page_config(page_title="NBA Small Ball Dashboard", layout="wide")

st.title("NBA Small Ball Transformation Dashboard")
st.markdown(
    """
    This dashboard explores the NBA transformation toward small ball,
    especially around and after the Warriors dynasty era (2015-16).
    """
)

st.subheader("Physical Evolution")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(get_avg_height_by_season_figure(), use_container_width=True)
with col2:
    st.plotly_chart(get_avg_weight_by_season_figure(), use_container_width=True)

st.subheader("Height and Rebounding")
st.plotly_chart(get_rebounds_vs_height_figure(), use_container_width=True)

st.subheader("Ball Movement and Playmaking")
col5, col6 = st.columns(2)
with col5:
    st.plotly_chart(get_total_assists_by_season_figure(), use_container_width=True)
with col6:
    st.plotly_chart(get_center_assists_by_season_figure(), use_container_width=True)

st.subheader("Production by Position")
col7, col8 = st.columns(2)
with col7:
    st.plotly_chart(get_points_by_position_figure(), use_container_width=True)
with col8:
    st.plotly_chart(get_assists_by_position_figure(), use_container_width=True)

st.plotly_chart(get_rebounds_by_position_figure(), use_container_width=True)

st.header("6. Warriors 2015-16 vs League Average")

st.plotly_chart(get_warriors_vs_league_radar_2016_figure(), use_container_width=True)

col9, col10 = st.columns(2)

with col9:
    st.plotly_chart(get_warriors_vs_league_metrics_bar_2016_figure(), use_container_width=True)

with col10:
    st.plotly_chart(get_warriors_vs_league_roster_composition_2016_figure(), use_container_width=True)

st.markdown("""
This section directly compares the 2015-16 Warriors to the average NBA team.
It highlights structural differences in height, playmaking, net rating and roster composition,
which helps make the small-ball transition much more explicit.
""")