"""Curated values obey the physical rules stated in the PSI reports (docs/DATA_QUALITY_REVIEW.md, ADR-0067).

A failure here means a curation change broke a relation the source data satisfies, e.g. a column swap or a
wrong unit conversion. Known source anomalies are listed in the review, not silently filtered here.
"""

from pathlib import Path
from statistics import median

import pandas as pd
import pytest

from psi_fire.domain.model import Investigation
from psi_fire.infrastructure.curated_store import CuratedRepository

CURATED = Path(__file__).resolve().parents[2] / "data" / "curated"
N2_MOLAR_MASS = 28.01
O2_MOLAR_MASS = 32.0
# (molar mass g/mol, mol O2 per mol fuel) for complete combustion
ALKANES = {"ethane": (30.07, 3.5), "propane": (44.10, 5.0), "butane": (58.12, 6.5)}
CDM_CO2_RESOLUTION_PERCENT = 0.1  # BASS-II Summary Report p. 14


@pytest.fixture(scope="module")
def repository() -> CuratedRepository:
    return CuratedRepository(CURATED)


def _num(investigation: Investigation, key: str) -> list[float | None]:
    return [v if isinstance(v := tp.value(key), (int, float)) else None for tp in investigation.test_points]


def test_flex_burn_time_follows_the_d_squared_law(repository: CuratedRepository) -> None:
    flex = repository.get("FLEX")
    ratios = []
    for tp in flex.test_points:
        d0, k, t = tp.value("droplet_initial_diameter_mm"), tp.value("burning_rate_constant_mm2_s"), tp.value("burn_time_s")
        de = tp.value("flame_extinction_diameter_mm") or 0.0
        if isinstance(d0, float) and isinstance(k, float) and isinstance(t, float) and isinstance(de, float) and d0 > 1.1 * de:
            ratios.append(t / ((d0**2 - de**2) / k))
    assert len(ratios) > 200
    assert 0.95 < median(ratios) < 1.10


@pytest.mark.parametrize("fuel", ["heptane", "methanol"])
def test_flex_burning_rate_rises_with_oxygen_in_nitrogen(repository: CuratedRepository, fuel: str) -> None:
    flex = repository.get("FLEX")
    rows = [(tp.o2_percent_min, tp.value("burning_rate_constant_mm2_s")) for tp in flex.test_points
            if tp.fuel_name == fuel and tp.diluent == "N2" and tp.value("burning_rate_constant_mm2_s") is not None]
    frame = pd.DataFrame(rows, columns=["o2", "k"])
    assert frame.o2.corr(frame.k, method="spearman") > 0.5


def _mass_fraction(mole_fraction: float, molar_mass: float) -> float:
    return mole_fraction * molar_mass / (mole_fraction * molar_mass + (1 - mole_fraction) * N2_MOLAR_MASS)


def test_acme_cfi_g_stoichiometric_mixture_fraction_matches_reported_composition(repository: CuratedRepository) -> None:
    checked = 0
    for tp in repository.get("ACME-CFI-G").test_points:
        zst, o2 = tp.value("stoichiometric_mixture_fraction"), tp.o2_percent_min
        column = "burner_fuel_fraction_percent" if tp.value("flame_configuration") == "normal" else "ambient_fuel_fraction_percent"
        fuel_percent = tp.value(column)
        if not isinstance(zst, float) or not isinstance(fuel_percent, float) or o2 is None:
            continue
        molar_mass, o2_moles = ALKANES[str(tp.fuel_name)]
        s = o2_moles * O2_MOLAR_MASS / molar_mass
        expected = 1 / (1 + s * _mass_fraction(fuel_percent / 100, molar_mass) / _mass_fraction(o2 / 100, O2_MOLAR_MASS))
        assert expected == pytest.approx(zst, abs=1e-3), tp.test_point_id
        checked += 1
    assert checked > 300


def test_acme_cfi_g_flames_never_add_oxygen_to_the_sealed_chamber(repository: CuratedRepository) -> None:
    acme = repository.get("ACME-CFI-G")
    pairs = [(tp.o2_percent_min, tp.value("o2_after_test_percent")) for tp in acme.test_points]
    pairs = [(before, after) for before, after in pairs if before is not None and isinstance(after, float)]
    assert len(pairs) > 150 and all(after <= before for before, after in pairs)


def test_bass_ii_burns_never_remove_carbon_dioxide(repository: CuratedRepository) -> None:
    bass = repository.get("BASS-II")
    pairs = zip(_num(bass, "co2_initial_percent"), _num(bass, "co2_final_percent"), strict=True)
    assert all(final >= initial - CDM_CO2_RESOLUTION_PERCENT for initial, final in pairs
               if initial is not None and final is not None)


def test_saffire_ii_spread_rate_equals_burn_length_over_burn_time(repository: CuratedRepository) -> None:
    checked = 0
    for tp in repository.get("SAFFIRE-II").test_points:
        rate, length, time = (tp.value(k) for k in ("microgravity_spread_rate_cm_s", "microgravity_burn_length_mm", "burn_time_s"))
        if isinstance(rate, float) and isinstance(length, float) and isinstance(time, float):
            assert length / 10 / time == pytest.approx(rate, rel=0.1), tp.test_point_id
            checked += 1
    assert checked == 2


def test_spice_mass_flow_is_consistent_with_the_labelled_gas_density(repository: CuratedRepository) -> None:
    densities = {}
    for tp in repository.get("SPICE").test_points:
        mass, volume = tp.value("fuel_mass_flow_rate_mg_s"), tp.value("fuel_volume_flow_rate_sccm")
        if isinstance(mass, float) and isinstance(volume, float) and volume > 0:
            densities.setdefault((tp.fuel_name, tp.value("fuel_label_fraction_percent")), []).append(mass * 60 / volume)
    for group, values in densities.items():
        assert max(values) / min(values) < 1.01, group  # one density per gas: no methane-density rows left


def test_bass_ii_final_o2_never_rises_or_collapses(repository: CuratedRepository) -> None:
    bass = repository.get("BASS-II")
    for tp in bass.test_points:
        final = tp.value("o2_final_percent")
        if isinstance(final, float) and tp.o2_percent_min is not None:
            assert -0.5 <= tp.o2_percent_min - final <= 10, tp.test_point_id
    flagged = {tp.test_point_id for tp in bass.test_points if "o2_final_percent_raw" in tp.extras}
    assert flagged == {"B2", "P22a", "P22b", "T28a", "T28b"}
    assert all((v or 0) >= 0 for v in _num(bass, "co_initial_percent") + _num(bass, "co_initial_ppm"))


def test_flagged_conflicts_keep_the_reported_value(repository: CuratedRepository) -> None:
    flex = {tp.test_point_id: tp for tp in repository.get("FLEX").test_points}
    assert all(flex[i].value("flame_extinction_diameter_mm") is None for i in ("39", "43", "52", "93"))
    assert all(tp.value("flame_extinction_diameter_mm") != 0 for tp in flex.values() if tp.value("test_outcome") == "disruption")
    cfi = {tp.test_point_id: tp for tp in repository.get("CFI").test_points}
    assert cfi["r13"].value("n2_percent") == 76 and "not 1" in str(cfi["r13"].provenance_note)
    acme = {tp.test_point_id: tp for tp in repository.get("ACME-CFI-G").test_points}
    f4 = acme["21106 F4"]
    assert f4.value("burn_time_s") == 22 and f4.provenance_status == "verified" and "conflicts" in str(f4.provenance_note)
