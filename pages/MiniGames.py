import streamlit as st
from games.MiniGames import run_games_hub

st.set_page_config(page_title="Mini Games", page_icon="🎮", layout="wide")

run_games_hub()