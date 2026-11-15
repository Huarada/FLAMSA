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
    .st-key-header_navigation button { min-height: 44px; border-radius: 9px; }
    @media (min-width: 1024px) {
      .st-key-header_navigation button { min-height: 56px; padding: .85rem 1.15rem; }
      .st-key-header_navigation button p { font-size: 1rem; font-weight: 600; white-space: nowrap; }
      .st-key-topbar [data-testid="stPopoverButton"] { min-height: 56px; }
    }
    @media (min-width: 1024px) and (max-width: 1199px) {
      .st-key-header_navigation { column-gap: 1rem; }
      .st-key-header_navigation button { min-height: 52px; padding: .7rem .65rem; }
      .st-key-header_navigation button p { font-size: .95rem; }
    }
    .st-key-nav_dashboard button { background: #3563b9; border: 1px solid #2c54a0; color: #fff;
      box-shadow: 0 3px 10px #3563b91c; font-weight: 600;
      animation: dashboard-nav-pulse 3.6s ease-in-out infinite; }
    .st-key-nav_dashboard button p { color: #fff !important; }
    .st-key-nav_dashboard button:hover { background: #294f96; border-color: #1e417f; }
    .st-key-nav_dashboard button:hover, .st-key-nav_dashboard button:focus-visible { animation-play-state: paused; }
    .st-key-nav_investigations button { background: #117443; border: 1px solid #0d5b35; color: #fff;
      box-shadow: 0 4px 13px #11744324; font-weight: 650; }
    .st-key-nav_investigations button p, .st-key-nav_investigations button span { color: #fff !important; }
    .st-key-nav_investigations button:hover { background: #0c5e36; border-color: #08482a; }
    @keyframes dashboard-nav-pulse {
      0%,100% { box-shadow: 0 0 0 0 #3563b92b, 0 3px 10px #3563b91c; }
      50% { box-shadow: 0 0 0 5px #3563b914, 0 4px 18px #3563b938; }
    }
    .st-key-research_guide_controls { justify-content: space-between; margin-bottom: .6rem; }
    [class*="st-key-guide_step_"] { position: relative; overflow: visible;
      --guide-background: #dce9ff; --guide-accent: #2458bb; --guide-glow: 48, 102, 211;
      background: var(--guide-background); color: #203747;
      border: 2px solid var(--guide-accent); border-left-width: 6px;
      border-radius: 14px 14px 14px 4px;
      padding: 1rem; margin-bottom: .8rem; gap: .35rem;
      box-shadow: 0 4px 16px rgba(var(--guide-glow), .16); }
    [class*="st-key-guide_step_"]::after { content: ''; position: absolute; left: 20px; bottom: -9px;
      width: 17px; height: 10px; background: var(--guide-background);
      clip-path: polygon(0 0, 100% 0, 20% 100%); pointer-events: none; }
    .st-key-guide_step_2 { --guide-background: #eadcfc; --guide-accent: #7436ae; --guide-glow: 133, 62, 196; }
    .st-key-guide_step_3 { --guide-background: #daf2e5; --guide-accent: #177447; --guide-glow: 23, 116, 71; }
    [class*="st-key-guide_step_"] [data-testid="stMarkdownContainer"] p {
      font-size: .86rem; line-height: 1.5; color: #203747; }
    [class*="st-key-guide_step_"] p > strong:only-child {
      color: var(--guide-accent); font-size: 1rem; font-weight: 750; }
    .st-key-nav_fire_behavior button { background: linear-gradient(115deg, #ffd17d, #f4b34b);
      border: 1px solid #bd7d20; color: #25374a; box-shadow: 0 4px 13px #c4872e26; font-weight: 650; }
    .st-key-nav_fire_behavior button p, .st-key-nav_fire_behavior button span { color: #25374a !important; }
    .st-key-nav_fire_behavior button:hover { background: #ffcd72; border-color: #905d12; }
    .st-key-behavior_introduction { background: #ffffffcf; border-radius: 16px; padding: 1.4rem;
      border-top: 3px solid #c58b36; box-shadow: 0 7px 24px #20374708; }
    .st-key-behavior_introduction h3 { font-size: 1.3rem !important; }
    .st-key-behavior_introduction [data-testid="stMarkdownContainer"] p { font-size: .9rem; line-height: 1.65; }
    [class*="st-key-behavior_learning_"] { background: #f5f8fc; border-radius: 12px; padding: .9rem; }
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
    .st-key-filter_panel [data-testid="stForm"] { border: 0; padding: 0; }
    .st-key-copilot_mascot { padding: .5rem .6rem; border-radius: 12px;
      border-left: 3px solid #F4BD61; background: #F5F8FC; }
    .st-key-copilot_panel button[kind="primary"] { min-height: 44px; }
    .st-key-copilot_question_bubble { position: relative; overflow: visible; padding: .85rem;
      background: linear-gradient(135deg, #532a8b, #342649); border: 2px solid #b986ef;
      border-radius: 18px 18px 18px 6px;
      margin-bottom: .45rem; box-shadow: 0 6px 22px #5f2da040; }
    .st-key-copilot_question_bubble:focus-within {
      box-shadow: 0 0 0 3px #b986ef66, 0 6px 22px #5f2da040 !important; }
    .st-key-copilot_question_bubble::after { content: ''; position: absolute; left: 24px; bottom: -11px;
      width: 20px; height: 12px; background: #342649; clip-path: polygon(0 0, 100% 0, 25% 100%);
      pointer-events: none; }
    .st-key-copilot_question_bubble label p,
    .st-key-copilot_question_bubble [data-testid="stTooltipIcon"] { color: #FCF7FF !important; }
    .st-key-copilot_question_bubble [data-testid="stTooltipHoverTarget"] span { color: #D9C3F0 !important; }
    .st-key-copilot_question_bubble [data-testid="stTextAreaRootElement"] { background: #241B34;
      border: 1px solid #A58CBF; border-radius: 12px; overflow: hidden; }
    .st-key-copilot_question_bubble textarea { background: #241B34 !important; color: #FCF7FF !important;
      border: 0 !important; border-radius: 11px; -webkit-text-fill-color: #FCF7FF; caret-color: #F4BD61; }
    .st-key-copilot_question_bubble textarea::placeholder { color: #C8BADA; -webkit-text-fill-color: #C8BADA; opacity: 1; }
    .st-key-copilot_question_bubble [data-testid="stTextAreaRootElement"]:focus-within {
      border-color: #D9C3F0; box-shadow: 0 0 0 2px #D9C3F066; }
    @supports not (backdrop-filter: blur(1px)) {
      .st-key-topbar, .st-key-filter_panel, .st-key-profiles_card, .st-key-volume_card,
      .st-key-composition_card, .st-key-coverage_card, .st-key-investigation_preview,
      .st-key-copilot_panel, .st-key-home_scene, .st-key-home_context,
      .st-key-behavior_flex, .st-key-behavior_bass, .st-key-behavior_saffire,
      [class*="st-key-kpi_"] { background: #f9fbfd; }
    }
    .stApp:has(.home-backdrop.motion-paused) .st-key-nav_dashboard button { animation: none !important; }
    @media (prefers-reduced-motion: reduce) {
      button, input, textarea { transition: none; }
      .st-key-nav_dashboard button { animation: none !important; }
      [class*="st-key-guide_step_"], .st-key-copilot_question_bubble { animation: none !important; }
    }
    @media (max-width: 800px) { .stMainBlockContainer { padding: 1rem; } .st-key-hero { padding: 1rem; } }
    </style>""")
