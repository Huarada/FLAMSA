"""Light glass presentation with the existing analytic palette; no scientific logic."""

import streamlit as st


def apply_style() -> None:
    st.html("""<style>
    .stApp {
      background-color: #edf3f8;
      background-image: radial-gradient(ellipse at 95% 0%, rgba(103,136,212,.22), transparent 45%),
        radial-gradient(ellipse at 0% 55%, rgba(141,191,186,.16), transparent 42%),
        linear-gradient(155deg, #f7fafc 0%, #eaf1f7 48%, #f5f8fa 100%);
      background-attachment: fixed;
    }
    .stMainBlockContainer { max-width: 1500px; padding: 1.4rem 2.2rem 2rem; }
    [data-testid="stHeader"] { display: none; }
    h1 { font-size: 1.8rem !important; letter-spacing: -.035rem; padding-bottom: .15rem !important; }
    h3 { font-size: 1.05rem !important; letter-spacing: -.015rem; }
    h4 { font-size: .95rem !important; }
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p,
    [data-testid="stCaptionContainer"] span { color: #526a7e !important; font-size: .78rem; opacity: 1; }
    [data-testid="stVerticalBlockBorderWrapper"] > div { border-color: rgba(157,181,199,.38) !important; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 600; }
    [data-testid="stMetricLabel"] { color: #60798d; font-size: .8rem; }
    .st-key-topbar { background: rgba(255,255,255,.76); border: 1px solid rgba(255,255,255,.8);
      border-bottom: 2px solid rgba(103,136,212,.5); border-radius: 14px;
      box-shadow: 0 6px 24px rgba(32,55,71,.045);
      backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
      padding: .8rem 1rem; margin-bottom: 1rem; }
    .st-key-hero { position: relative; overflow: hidden; isolation: isolate;
      padding: 1.5rem 1.5rem 1.2rem; margin-bottom: 1rem;
      border-radius: 16px; border: 1px solid rgba(255,255,255,.85);
      background: linear-gradient(105deg, rgba(255,255,255,.94), rgba(230,239,249,.68));
      box-shadow: inset 0 1px 0 rgba(255,255,255,.95), 0 10px 35px rgba(32,55,71,.04); }
    .st-key-hero::after { content: ""; position: absolute; pointer-events: none; z-index: -1;
      width: 560px; height: 560px; right: -90px; top: 45px; border-radius: 50%;
      border: 1px solid rgba(103,136,212,.3);
      background: radial-gradient(circle at 35% 15%, rgba(255,255,255,.7), rgba(103,136,212,.13) 45%, rgba(32,55,71,.08) 70%);
      box-shadow: 0 -8px 35px rgba(103,136,212,.14), inset 0 8px 25px rgba(255,255,255,.9); }
    .st-key-hero h1 { font-size: 2.35rem !important; letter-spacing: .08rem; }
    .st-key-home_hero { padding: 2.8rem .4rem 1.8rem; max-width: 960px; }
    .st-key-home_hero h1 { font-size: clamp(2.4rem, 4.5vw, 4rem) !important;
      line-height: 1.08; letter-spacing: -.07rem; white-space: pre-line; }
    .st-key-home_hero [data-testid="stMarkdownContainer"] p { max-width: 760px; }
    .st-key-filter_panel, .st-key-investigation_preview,
    .st-key-profiles_card, .st-key-volume_card, .st-key-composition_card,
    .st-key-coverage_card, .st-key-copilot_panel, .st-key-home_scene, .st-key-home_context,
    .st-key-behavior_flex, .st-key-behavior_bass, .st-key-behavior_saffire {
      background: rgba(255,255,255,.76); border-radius: 14px;
      backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
      box-shadow: inset 0 1px 0 rgba(255,255,255,.9), 0 8px 30px rgba(32,55,71,.045);
    }
    [data-testid="stMetric"] { background: #fff; border: 1px solid #e0e8ee;
      border-radius: 8px; padding: .9rem 1rem; }
    [class*="st-key-kpi_"] { background: rgba(255,255,255,.72); border-radius: 12px;
      backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
      box-shadow: inset 0 1px 0 rgba(255,255,255,.9), 0 5px 20px rgba(32,55,71,.04); }
    [class*="st-key-kpi_"] [data-testid="stMetric"] { border: 0; padding: 0; }
    [class*="st-key-kpi_"] [data-testid="stMetric"] { background: transparent; }
    button, input, textarea, [data-baseweb="select"] > div { transition: border-color .15s, box-shadow .15s; }
    button:focus-visible, input:focus-visible { outline: 2px solid #6788d4 !important; outline-offset: 2px; }
    .st-key-workspace_navigation button { background: transparent; border: 0; box-shadow: none; }
    .st-key-filter_panel [data-testid="stForm"] { border: 0; padding: 0; }
    @supports not (backdrop-filter: blur(1px)) {
      .st-key-topbar, .st-key-filter_panel, .st-key-profiles_card, .st-key-volume_card,
      .st-key-composition_card, .st-key-coverage_card, .st-key-investigation_preview,
      .st-key-copilot_panel, .st-key-home_scene, .st-key-home_context,
      .st-key-behavior_flex, .st-key-behavior_bass, .st-key-behavior_saffire,
      [class*="st-key-kpi_"] { background: #f9fbfd; }
    }
    @media (prefers-reduced-motion: reduce) { button, input, textarea { transition: none; } }
    @media (max-width: 800px) { .stMainBlockContainer { padding: 1rem; } .st-key-hero { padding: 1rem; } }
    </style>""")
