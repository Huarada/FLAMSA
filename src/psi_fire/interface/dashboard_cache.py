"""Bounded caches for deterministic chart projections, keyed by data revision and retained row identities."""

import streamlit as st

from psi_fire.application.chart_data import BuildChartData, ChartData, InvestigationPlotCoverage, PlotVariable
from psi_fire.application.explore import Match
from psi_fire.domain.model import O2Basis

RecordScope = tuple[tuple[str, tuple[str, ...]], ...]


def record_scope(matches: tuple[Match, ...]) -> RecordScope:
    return tuple((match.investigation.id, tuple(point.test_point_id for point in match.points)) for match in matches)


@st.cache_data(max_entries=32, show_spinner=False)
def chart_variables(revision: str, scope: RecordScope, _matches: tuple[Match, ...]) -> tuple[PlotVariable, ...]:
    return BuildChartData().variables(_matches)


@st.cache_data(max_entries=32, show_spinner=False)
def partner_counts(revision: str, scope: RecordScope, x: str, ids: tuple[str, ...], basis: O2Basis,
                   _matches: tuple[Match, ...]) -> dict[str, int]:
    return BuildChartData().partners(_matches, x, ids, basis)


@st.cache_data(max_entries=32, show_spinner=False)
def comparison_projection(revision: str, scope: RecordScope, x: str, y: str, ids: tuple[str, ...], basis: O2Basis,
                          _matches: tuple[Match, ...]) -> tuple[ChartData, tuple[InvestigationPlotCoverage, ...]]:
    # _matches avoids hashing the whole Pydantic graph; revision and row identities cover its scientific content.
    builder = BuildChartData()
    return builder(_matches, x, y, ids, basis), builder.coverage(_matches, x, y, ids, basis)
