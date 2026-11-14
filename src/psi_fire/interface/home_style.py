"""Lovable's dark glass, ember gradient and motion, scoped to Home."""

import base64
from pathlib import Path

import streamlit as st


@st.cache_data(show_spinner=False)
def hero_image_uri() -> str:
    content = (Path(__file__).parent / "assets/flamsa-hero.jpg").read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(content).decode("ascii")


def apply_home_style(image_uri: str) -> None:
    paused = not st.session_state.get("home_motion", True)
    particles = "".join(
        f'<i style="left:{(i * 37) % 100}%;animation-duration:{8 + (i % 7) * 2}s;'
        f'animation-delay:-{(i % 9) * 1.1}s"></i>' for i in range(24)
    )
    st.html(f'<div class="home-backdrop {"motion-paused" if paused else ""}" aria-hidden="true">'
            f'<img src="{image_uri}" alt=""/><div class="home-grid"></div>'
            f'<div class="home-fade"></div>{particles}</div>')
    st.html("""<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@400;600;800&display=swap');
    .stApp:has(.st-key-home_workspace) { background: #070f1e; color: #e9f0f5; font-family: 'Sora', sans-serif; }
    .stApp:has(.st-key-home_workspace) .stMainBlockContainer { max-width: 1440px; padding: 1rem 2.5rem 3rem; }
    .stApp:has(.st-key-home_workspace) .stMainBlockContainer > div { position: relative; z-index: 1; }
    .home-backdrop { position: fixed; inset: 0; z-index: -1; overflow: hidden; pointer-events: none; background: #070f1e; }
    .home-backdrop img { width: 100%; height: 100%; object-fit: cover; opacity: .6;
      animation: home-kenburns 22s ease-in-out infinite; }
    .home-grid, .home-fade { position: absolute; inset: 0; }
    .home-grid { background-image: linear-gradient(#239bd01c 1px, transparent 1px),
      linear-gradient(90deg, #239bd01c 1px, transparent 1px); background-size: 60px 60px;
      mask-image: linear-gradient(to top, black, transparent 60%); animation: home-gridmove 4s linear infinite; }
    .home-fade { background: radial-gradient(ellipse at 50% 45%, transparent 20%, #070f1ee8 85%),
      linear-gradient(to bottom, #070f1e10 40%, #070f1e 100%); }
    .home-backdrop i { position: absolute; bottom: -10px; width: 4px; height: 4px;
      border-radius: 50%; background: #ff812b; box-shadow: 0 0 0 7px #ff812b14, 0 0 20px #ff812b80;
      animation: home-rise linear infinite; }
    .stApp:has(.st-key-home_workspace) .st-key-topbar { background: #101c2c88;
      border: 1px solid #289dd04d; border-radius: 40px; box-shadow: inset 0 1px #ffffff14, 0 0 40px -12px #239bd060;
      backdrop-filter: blur(18px) saturate(140%); padding: .65rem 1.4rem; margin-bottom: 0; }
    .stApp:has(.st-key-home_workspace) .st-key-topbar button { color: #e9f0f5; }
    .stApp:has(.st-key-home_workspace) .st-key-topbar button[aria-pressed="true"] { background: #ff812b33; }
    .st-key-home_workspace { gap: 1.8rem; color: #e9f0f5; }
    .st-key-home_workspace .st-key-home_hero { max-width: none; padding: 5.5rem 0 1.8rem; }
    .st-key-home_workspace .st-key-home_hero h1 { font-family: 'Sora', sans-serif;
      font-size: clamp(3.2rem, 7.5vw, 7rem) !important; font-weight: 800; line-height: 1.05;
      letter-spacing: -.045em; color: #e9f0f5 !important; max-width: 1240px; padding: 0 0 1.5rem !important; }
    .st-key-home_hero h1 .stMarkdownColoredText { background: linear-gradient(90deg, #ff782b, #eebd2b);
      background-clip: text; -webkit-background-clip: text; color: transparent !important; }
    .stApp:has(.st-key-home_workspace) .st-key-topbar img { filter: brightness(0) invert(1); }
    .stApp:has(.st-key-home_workspace) .st-key-topbar [data-testid="stPopoverButton"] {
      color: #e9f0f5; background: #101c2cbb; border: 1px solid #289dd066; }
    .stApp:has(.st-key-home_workspace) .st-key-home_hero [data-testid="stCaptionContainer"] p {
      color: #24b3ff !important; text-shadow: 0 0 12px #239bd066; font-family: 'JetBrains Mono', monospace;
      font-size: .8rem; text-transform: uppercase; letter-spacing: .3em; }
    .st-key-home_workspace .st-key-home_hero [data-testid="stMarkdownContainer"] p {
      color: #a7bac9; font-size: clamp(1rem, 1.7vw, 1.4rem); line-height: 1.6; max-width: 950px; }
    .st-key-home_workspace h3 { color: #e9f0f5 !important; font-family: 'Sora', sans-serif; font-size: 1.5rem !important; }
    .stApp:has(.st-key-home_workspace) [data-testid="stCaptionContainer"] p,
    .stApp:has(.st-key-home_workspace) [data-testid="stCaptionContainer"] span { color: #a7bac9 !important; }
    .st-key-home_workspace .st-key-home_scene { padding: 5px; border-radius: 28px;
      background: #101c2c70; border: 1px solid #289dd066; box-shadow: 0 0 40px -12px #239bd099; }
    .st-key-home_workspace .st-key-home_context, .st-key-home_metrics,
    .st-key-home_workspace [class*="st-key-home_step_"] { padding: 1.5rem; border-radius: 24px;
      border: 1px solid #289dd04d; background: #101c2ca3; backdrop-filter: blur(18px) saturate(140%);
      box-shadow: inset 0 1px #ffffff14, 0 0 40px -12px #239bd040; }
    .st-key-home_workspace [data-testid="stMetric"] { background: transparent; border: 0; }
    .st-key-home_workspace [data-testid="stMetricValue"] { color: #ff983b; }
    .st-key-home_workspace [data-testid="stMetricLabel"] { color: #a7bac9; }
    .st-key-home_workspace .st-key-home_theme button { color: #e9f0f5; background: #101c2c88;
      border-color: #289dd066; min-height: 44px; }
    .st-key-home_workspace .st-key-home_theme button[aria-pressed="true"] { background: #ff812b33; border-color: #ff812b; }
    .st-key-home_workspace button[kind="primary"] { background: linear-gradient(90deg, #ff782b, #efaf2b);
      border-color: #ff963b; color: #08121f; min-height: 44px; }
    .st-key-home_workspace button[kind="secondary"] { background: #101c2cbb; border-color: #289dd066;
      color: #e9f0f5; min-height: 44px; }
    .st-key-home_workspace [data-testid="stMarkdownContainer"] p { color: #c0ced9; line-height: 1.65; }
    .st-key-home_workspace label { color: #c0ced9; }
    .st-key-home_motion { align-self: flex-end; }
    @keyframes home-kenburns { 0%,100% { transform: scale(1); } 50% { transform: scale(1.12) translate(-1.5%,-1%); } }
    @keyframes home-gridmove { to { background-position: 0 60px; } }
    @keyframes home-rise { 0% { transform: translateY(0); opacity: 0; } 20% { opacity: .7; }
      100% { transform: translateY(-120vh); opacity: 0; } }
    .motion-paused *, .motion-paused { animation-play-state: paused !important; }
    @media (prefers-reduced-motion: reduce) { .home-backdrop, .home-backdrop * { animation: none !important; } }
    @media (max-width: 800px) {
      .stApp:has(.st-key-home_workspace) .stMainBlockContainer { padding: 1rem; }
      .st-key-home_workspace .st-key-home_hero { padding: 2.5rem 0 1rem; }
      .st-key-home_workspace .st-key-home_hero h1 { font-size: clamp(2.6rem, 8vw, 4.5rem) !important; }
      .st-key-home_workspace .st-key-home_hero [data-testid="stCaptionContainer"] p { font-size: .65rem; letter-spacing: .15em; }
      .stApp:has(.st-key-home_workspace) .st-key-topbar { border-radius: 24px; padding: .8rem; }
    }
    </style>""")
