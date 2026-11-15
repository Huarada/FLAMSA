"""Student-facing explanations of the existing experimental evidence views."""

import streamlit as st


def behavior_introduction() -> None:
    with st.container(border=True, key="behavior_introduction"):
        st.caption("THE SCIENCE BEHIND THE CHARTS")
        st.subheader("From physical laws to traceable evidence")
        st.write("Fire-safety research asks how quickly fuel is consumed, how a fire changes the surrounding atmosphere, "
                 "and whether a flame keeps spreading. These experiments let us examine those questions using "
                 "reported measurements, explicit calculations and the original source records.")
        st.write("Microgravity changes the role of buoyancy—the tendency of hot gases to rise. "
                 "Studying combustion in that environment helps researchers separate physical effects and examine "
                 "how ground-based observations relate to conditions in space.")
        fuel, gases, gravity = st.columns(3)
        with fuel, st.container(border=True, key="behavior_learning_flex"):
            st.markdown("**01 · How quickly is fuel consumed?**")
            st.caption("FLEX / PHYSICAL MODEL")
            st.latex(r"d(t)^2 = d_0^2 - Kt")
            st.write("In the approximate d-squared model, a burning droplet's squared diameter decreases with time. "
                     "K describes that decrease: a larger K means faster loss of squared diameter under the tested conditions.")
            st.caption("d and d₀: droplet diameter and initial diameter in mm; t: time in s; K: mm²/s.")
            st.write("The FLEX charts estimate how K changes with oxygen within comparable fuel/blend groups, "
                     "adjusting for reported pressure and initial droplet diameter.")
        with gases, st.container(border=True, key="behavior_learning_bass"):
            st.markdown("**02 · How does the atmosphere change?**")
            st.caption("BASS-II / MEASURED DIFFERENCES")
            st.latex(r"\begin{aligned}\Delta O_2 &= O_{2,i}-O_{2,f}\\"
                     r"\Delta CO_2 &= CO_{2,f}-CO_{2,i}\end{aligned}")
            st.write("Compare the gas readings before and after the same burn. A positive oxygen decrease and CO₂ "
                     "increase describe changes in the measured atmosphere, which are relevant to fire-detection research.")
            st.caption("i: initial reading; f: final reading. Differences are percentage points.")
            st.write("The plot retains negative differences so measurement variation stays visible. "
                     "It reports concentration changes rather than a calculated CO₂ mass or exposure limit.")
        with gravity, st.container(border=True, key="behavior_learning_saffire"):
            st.markdown("**03 · Does the ground result carry over?**")
            st.caption("SAFFIRE-II / PAIRED OBSERVATIONS")
            st.latex(r"L_{\mu g}\;\longleftrightarrow\;L_{1g}")
            st.write("Read each sample's microgravity and ground outcomes side by side. This comparison asks whether "
                     "the reported screening result agrees with the flight result for that sample.")
            st.caption("L: reported burned length; μg: microgravity; 1 g: Earth's gravity. The arrow denotes a comparison.")
            st.write("Material, thickness, oxygen and flow provide context. Labels such as Complete and Acceleratory "
                     "stay in their original form so the comparison preserves what the source actually reports.")
        st.markdown("**What makes the evidence checkable?**")
        st.write("Follow the chain: physical relationship → measured quantities → reproducible calculation → "
                 "source row and interpretation. The section exposes units, tested ranges, exclusions, uncertainty "
                 "and downloadable analysis records so a reader can audit each step.")
        st.caption("Agreement with an expected relationship is a physical-consistency check. An oxygen/K association "
                   "is conditional on the fitted model; it does not prove a universal law. Habitat safety also requires "
                   "independent evidence for the relevant environment. This archive does not establish direct lunar-gravity behavior.")
        with st.expander("Read the model, the uncertainty and the source trail"):
            st.markdown("**Physical model and statistical estimate play different roles.**")
            st.write("The d-squared model relates diameter, burning time and K. The fitted oxygen coefficient answers "
                     "a narrower question: how K changes per oxygen percentage point within one fuel/blend stratum, "
                     "after accounting for reported pressure and initial diameter.")
            st.latex(r"K = \beta_0 + \beta_{O_2}\,O_2 + \beta_P\,P + \beta_d\,d_0 + \varepsilon")
            st.write("β₀ is the intercept, the other β terms are fitted coefficients, P is pressure, and ε represents "
                     "variation left unexplained by the model. A covariate term is omitted when it is constant in the group. "
                     "βO₂ has units of mm²/s per oxygen percentage point.")
            st.write("The 95% intervals describe model-based uncertainty under the stated error assumptions. "
                     "Read the tested ranges before using a coefficient: a fit near 1 atm is not validated at a lower "
                     "pressure or a different gravity level.")
            st.write("Use the study tabs for measurements and paired outcomes, the slope details for group conditions, "
                     "and Methods, source columns and excluded records for locators and checksums. All coefficients "
                     "and intervals are calculated deterministically in the application. The analysis JSON records "
                     "the data revision, settings and numerical-library versions.")
            st.markdown("Background: [NASA — combustion and fire safety]"
                        "(https://www.nasa.gov/missions/station/iss-research/studying-combustion-and-fire-safety/), "
                        "[NASA — FLEX experiment requirements]"
                        "(https://www1.grc.nasa.gov/wp-content/uploads/FLEX_EIRD_v4.pdf). "
                        "Study-specific evidence remains available in the records below.")
