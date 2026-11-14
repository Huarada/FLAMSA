"""An isolated image-hotspot control; research queries remain outside the component."""

from collections.abc import Callable

import streamlit as st
from streamlit.components.v2.types import ComponentRenderer

_SCENE_ASSETS = {
    "html": """
    <figure class="research-scene">
      <div class="scene" role="group" aria-label="Research themes in a conceptual combustion scene">
        <div class="scene-world">
        <img alt="Concept illustration of a blue flame in a chamber, with Earth and a lunar habitat beyond the windows."
             width="1600" height="912" draggable="false" />
        <span class="flame-energy" aria-hidden="true"></span>
        <button type="button" data-topic="flame" style="left:51.5%;top:46%"
                aria-label="1: Flame behavior" title="Flame behavior">1</button>
        <button type="button" data-topic="earth" style="left:13%;top:30%"
                aria-label="2: Earth applications" title="Earth applications">2</button>
        <button type="button" data-topic="habitats" style="left:85%;top:38%"
                aria-label="3: Exploration habitats" title="Exploration habitats">3</button>
        <button type="button" data-topic="detection" style="left:12%;top:72%"
                aria-label="4: Detection and diagnostics" title="Detection and diagnostics">4</button>
        </div>
      </div>
    </figure>
    """,
    "css": """
    .research-scene { margin: 0; width: 100%; }
    .scene { position: relative; aspect-ratio: 1600 / 912; overflow: hidden;
      border-radius: 22px; background: #0a1727; }
    .scene-world { position: absolute; inset: 0; animation: drift 22s ease-in-out infinite; }
    img { width: 100%; height: 100%; display: block; object-fit: cover; }
    .flame-energy { position: absolute; left: 51.5%; top: 48.7%; width: 10%; aspect-ratio: 1;
      transform: translate(-50%, -50%); pointer-events: none; border-radius: 50%;
      background: radial-gradient(circle, #16b5ff12 35%, #23aaff44 70%, transparent 74%);
      mix-blend-mode: screen; box-shadow: 0 0 24px #007bff55; animation: flame-breathe 3.5s ease-in-out infinite; }
    .flame-energy::after { content: ''; position: absolute; inset: 0; border-radius: 50%;
      background: conic-gradient(from 0deg, transparent, #1bbaff30, transparent 32%, #55dfff30, transparent 70%);
      filter: blur(3px); animation: flame-turn 7s linear infinite; }
    button { position: absolute; transform: translate(-50%, -50%); width: 44px; height: 44px;
      border: 2px solid #e5efff; border-radius: 50%; background: #ff812b; color: #08121f;
      font: 600 14px / 1 var(--st-font, sans-serif); cursor: pointer;
      box-shadow: 0 0 0 10px #ff812b44, 0 4px 16px #0006;
      transition: background .15s, box-shadow .15s; }
    button::before { content: ''; position: absolute; inset: -2px; border-radius: 50%;
      background: #ff812b; z-index: -1; animation: ping-soft 1.8s ease-out infinite; }
    button:hover { background: #ffab4c; box-shadow: 0 0 0 10px #ff812b66; }
    button[aria-pressed="true"] { background: #ff963b; border-color: #fff;
      box-shadow: 0 0 0 12px #ff812b55, 0 0 30px #ff812b99; }
    button:focus-visible { outline: 3px solid #ffe2a4; outline-offset: 6px; }
    @keyframes drift { 0%,100% { transform: scale(1); } 50% { transform: scale(1.06) translate(-.5%,-.5%); } }
    @keyframes flame-breathe { 0%,100% { opacity: .45; } 50% { opacity: 1; } }
    @keyframes flame-turn { to { transform: rotate(360deg); } }
    @keyframes ping-soft { 0% { transform: scale(1); opacity: .6; } 100% { transform: scale(2.4); opacity: 0; } }
    .paused *, .paused *::after, .paused *::before { animation-play-state: paused !important; }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }
    """,
    "js": """
    export default function({data, parentElement, setTriggerValue}) {
      const image = parentElement.querySelector('img');
      if (image.getAttribute('src') !== data.image) image.src = data.image;
      parentElement.querySelector('.scene').classList.toggle('paused', !data.motion);
      const buttons = parentElement.querySelectorAll('button[data-topic]');
      let hoverTimer;
      buttons.forEach(button => {
        button.setAttribute('aria-pressed', String(button.dataset.topic === data.active));
        button.onclick = () => {
          if (button.dataset.topic !== data.active) setTriggerValue('selected', button.dataset.topic);
        };
        button.onmouseenter = () => { hoverTimer = setTimeout(() => button.click(), 200); };
        button.onmouseleave = () => clearTimeout(hoverTimer);
      });
      return () => {
        clearTimeout(hoverTimer);
        buttons.forEach(button => { button.onclick = null; button.onmouseenter = null; button.onmouseleave = null; });
      };
    }
    """,
}


def scene_renderer() -> ComponentRenderer:
    # Registration belongs to the active runtime; identical definitions are idempotent.
    return st.components.v2.component("psi_fire.research_scene", **_SCENE_ASSETS)


def research_scene(image: str, active: str, on_select: Callable[[], None]) -> None:
    scene_renderer()(data={"image": image, "active": active, "motion": st.session_state.get("home_motion", True)},
                     key="home_scene_control", on_selected_change=on_select,
                     width="stretch", height="content")
