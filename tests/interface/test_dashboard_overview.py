"""Dashboard overview: explained KPIs, O2 x pressure coverage map and the filtered-records download."""

from io import StringIO
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[2] / "src/psi_fire/interface/app.py"


def test_dashboard_shows_scenario_coverage_and_downloads_records() -> None:
    app = AppTest.from_file(str(APP), default_timeout=45).run()
    app.button(key="nav_dashboard").click().run()
    assert not app.exception
    labels = [metric.label for metric in app.metric]
    assert labels[:4] == ["Investigations", "Reported records", "Tests with O₂ and pressure", "Lunar-scenario tests"]
    assert all(metric.proto.help for metric in app.metric[:4])
    assert app.metric[3].value == "20"
    assert any("+28 with O₂ in the burner stream" in item.value for item in app.caption)
    assert any("Experimental coverage" in item.value for item in app.markdown)
    assert not any("Dataset composition" in item.value or "Records by investigation" in item.value
                   for item in app.markdown)
    assert not any(box.label == "Open investigation" for box in app.selectbox)


def test_filtered_records_csv_keeps_raw_values_and_provenance() -> None:
    from psi_fire.application.explore import ExplorationQuery, ExploreInvestigations, LoadExplorer
    from psi_fire.infrastructure.explorer import FileSnapshotProvider
    from psi_fire.interface.reference_dashboard import filtered_records_csv

    snapshot = LoadExplorer(FileSnapshotProvider(APP.parents[3]))()
    matches = ExploreInvestigations(snapshot)(ExplorationQuery(ids=("FLEX",)))
    frame = pd.read_csv(StringIO(filtered_records_csv(matches)), dtype={"test_point_id": str, "pressure_psi_raw": str})
    assert len(frame) == 274 and set(frame["investigation_id"]) == {"FLEX"}
    assert {"provenance_status", "source_row", "burning_rate_constant_mm2_s", "pressure_psi_raw"} <= set(frame.columns)
    assert frame.loc[frame["test_point_id"] == "114", "pressure_psi_raw"].item() == "0"
